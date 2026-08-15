"""
BlinkDL/rwkv7-g1 deposundan indirilen HAM .pth kontrol noktasi (transformers
config.json TASIMIYOR) icin native yukleme yolu.

`rwkv` pip paketinin kendi RWKV sinifi, HF'nin batched
forward(input_ids=...)/generate() arayuzunden FARKLI bir arayuz sunar:
tek bir token dizisini, kendi tasidigi (state) ile TEK TEK isler. Bu dosya,
geri kalan tum boru hattinin (mcts_dallanma.py'deki turbo_dfs BATCHED
cagrisi dahil) HICBIR SATIRI degismeden calismaya devam etmesi icin, native
RWKV'yi HF-uyumlu bir sarmalayiciya (adapter) gizler: batch'teki her satiri
kendi bagimsiz state'iyle TEK TEK isleyip sonuclari yigin (tensor) halinde
geri dondurur.

ONEMLI KISIT: `rwkv` pip paketinin agirliklari (`self.w`) standart
nn.Linear alt-moduller olarak DEGIL, duz bir tensor sozlugu olarak
saklanir. Bu yuzden `peft.get_peft_model()` bu modele dogrudan LoRA
uygulayamaz -- target_modules eslesmesi nn.Module agac gezintisine
dayanir. lora_adaptoru_kur() bu durumu tespit edip LoRA'yi ATLAR ve
acik bir uyari basar; test-time-training bu native yolda su an icin
devre disi kalir (inference/degerlendirme calisir, TTT calismaz). Bu,
kaide/hile ile ortulmez -- kullaniciya acikca bildirilir.
"""
import os
from typing import Any, List, Optional

import torch

_HAM_PTH_UYARISI_BASILDI = False


def rwkv_ham_pth_mi(yol: str) -> bool:
    """Yol bir .pth DOSYASI ise (transformers dizini degil), native
    yukleme gerektigini soyler."""
    if os.path.isfile(yol):
        return True
    if os.path.isdir(yol) and not os.path.isfile(os.path.join(yol, "config.json")):
        return any(f.endswith(".pth") for f in os.listdir(yol))
    return False


class _RWKVCiktisi:
    __slots__ = ("logits", "past_key_values", "loss", "state")


class RWKVUyumluModel(torch.nn.Module):
    """rwkv pip paketindeki modeli, geri kalan boru hattinin (uret_sohbet,
    turbo_dfs, gorev_ozelinde_ince_ayar) beklediği HF-benzeri arayuze
    (forward(input_ids, past_key_values, use_cache, return_dict),
    .generate(), .device, .parameters()) sarmalar."""

    def __init__(self, rwkv_model: Any, strateji: str):
        super().__init__()
        self._rwkv = rwkv_model
        self._strateji = strateji
        self._cihaz = torch.device("cuda" if "cuda" in strateji else "cpu")

    @property
    def device(self) -> torch.device:
        return self._cihaz

    def parameters(self, recurse: bool = True):
        for tensor in self._rwkv.w.values():
            if isinstance(tensor, torch.Tensor):
                yield tensor

    def named_parameters(self, prefix: str = "", recurse: bool = True):
        for isim, tensor in self._rwkv.w.items():
            if isinstance(tensor, torch.Tensor):
                yield isim, tensor

    def forward(self, input_ids: torch.Tensor, position_ids: Any = None,
                past_key_values: Optional[List[Any]] = None, use_cache: bool = True,
                return_dict: bool = True, labels: Optional[torch.Tensor] = None) -> _RWKVCiktisi:
        """Batch'teki HER satiri kendi bagimsiz (state) ile tek tek isler
        (native RWKV RNN state'i satirlar arasinda paylasilamaz), sonuclari
        yigin haline getirir. past_key_values burada aslinda per-satir
        RWKV state listesidir (isim, geri kalan koddaki genel 'onbellek'
        kavramiyla uyumlu kalsin diye korunuyor).

        HER T konumundaki logit toplanir (yalnizca sonuncusu degil) --
        state-tuning'in ogrenilebilir baslangic durumu ile HEDEF cikti
        dizisinin TUM pozisyonlarindan ogrenmesi icin sart; mcts_dallanma.
        py'nin `outputs.logits[:, -1]` kullanimi da bu bicimle (B,T,V)
        sorunsuz calisir."""
        B, T = input_ids.shape
        durumlar = list(past_key_values) if past_key_values is not None else [None] * B

        tum_logitler = []
        yeni_durumlar = []
        for b in range(B):
            durum = durumlar[b]
            satir_logitleri = []
            for t in range(T):
                token = int(input_ids[b, t].item())
                logit, durum = self._rwkv.forward([token], durum)
                satir_logitleri.append(torch.as_tensor(logit, device=self._cihaz))
            tum_logitler.append(torch.stack(satir_logitleri, dim=0))
            yeni_durumlar.append(durum)

        cikti = _RWKVCiktisi()
        cikti.logits = torch.stack(tum_logitler, dim=0)
        cikti.past_key_values = yeni_durumlar
        cikti.state = yeni_durumlar
        cikti.loss = None
        if labels is not None:
            kaydirilmis_logits = cikti.logits[:, :-1, :].reshape(-1, cikti.logits.shape[-1])
            kaydirilmis_hedefler = labels[:, 1:].reshape(-1)
            cikti.loss = torch.nn.functional.cross_entropy(
                kaydirilmis_logits, kaydirilmis_hedefler, ignore_index=-100,
            )
        return cikti

    @torch.no_grad()
    def generate(self, input_ids: torch.Tensor, max_new_tokens: int = 768,
                 do_sample: bool = True, temperature: Optional[float] = None,
                 top_p: Optional[float] = None, pad_token_id: Optional[int] = None,
                 baslangic_durumu: Optional[List[torch.Tensor]] = None,
                 **_yoksayilan: Any) -> torch.Tensor:
        B, T = input_ids.shape
        assert B == 1, "native RWKV generate() şu an tek örnek (B=1) destekliyor"

        durum = [t.clone() for t in baslangic_durumu] if baslangic_durumu is not None else None
        son_logits = None
        for t in range(T):
            token = int(input_ids[0, t].item())
            son_logits, durum = self._rwkv.forward([token], durum)

        uretilenler: List[int] = []
        for _ in range(max_new_tokens):
            olasiliklar = torch.softmax(
                torch.as_tensor(son_logits) / max(temperature or 1.0, 1e-4), dim=-1
            )
            if do_sample:
                sonraki_token = int(torch.multinomial(olasiliklar, 1).item())
            else:
                sonraki_token = int(torch.argmax(olasiliklar).item())

            uretilenler.append(sonraki_token)
            if pad_token_id is not None and sonraki_token == pad_token_id:
                break

            son_logits, durum = self._rwkv.forward([sonraki_token], durum)

        tam_dizi = input_ids[0].tolist() + uretilenler
        return torch.tensor([tam_dizi], device=self._cihaz, dtype=torch.long)


class RWKVUyumluTokenizer:
    """rwkv.utils.PIPELINE'i, geri kalan kodun bekledigi tokenizer
    arayuzune (encode/decode/__call__/pad_token_id/eos_token_id) sarmalar.
    "rwkv_vocab_v20230424" pip paketiyle birlikte gelir; internet gerekmez."""

    def __init__(self, pipeline: Any):
        self._pipeline = pipeline
        self.pad_token_id = 0
        self.eos_token_id = 0

    def encode(self, metin: str, add_special_tokens: bool = True) -> List[int]:
        return self._pipeline.encode(metin)

    def decode(self, token_idler: Any, skip_special_tokens: bool = True) -> str:
        if hasattr(token_idler, "tolist"):
            token_idler = token_idler.tolist()
        return self._pipeline.decode(list(token_idler))

    def __call__(self, metin: str, return_tensors: Optional[str] = None, truncation: bool = True,
                 max_length: int = 4096, return_offsets_mapping: bool = False) -> Any:
        idler = self.encode(metin)[:max_length]
        if not idler:
            idler = [self.pad_token_id]
        if return_tensors == "pt":
            sozluk = {"input_ids": torch.tensor([idler], dtype=torch.long)}

            class _Tasinabilir(dict):
                def to(self, cihaz):
                    return _Tasinabilir({k: v.to(cihaz) for k, v in self.items()})

            return _Tasinabilir(sozluk)
        cikti = {"input_ids": idler}
        if return_offsets_mapping:
            cikti["offset_mapping"] = None  # native RWKV world tokenizer icin karakter-hizali degil
        return cikti


def native_rwkv_yukle(pth_yolu: str, veri_tipi: torch.dtype = torch.bfloat16) -> RWKVUyumluModel:
    from rwkv.model import RWKV

    strateji = "cuda fp16" if torch.cuda.is_available() else "cpu fp32"
    if pth_yolu.endswith(".pth"):
        model_yolu = pth_yolu[: -len(".pth")]
    else:
        model_yolu = pth_yolu

    print(f"[rwkv_native] `rwkv` pip paketiyle native yükleniyor: {model_yolu} | strateji={strateji}")
    ham_model = RWKV(model=model_yolu, strategy=strateji)
    return RWKVUyumluModel(ham_model, strateji)


def native_rwkv_tokenizer_yukle() -> RWKVUyumluTokenizer:
    from rwkv.utils import PIPELINE

    pipeline = PIPELINE(None, "rwkv_vocab_v20230424")
    return RWKVUyumluTokenizer(pipeline)
