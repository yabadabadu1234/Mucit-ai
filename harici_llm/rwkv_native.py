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
import time
from typing import Any, List, Optional, Tuple

import torch

_HAM_PTH_UYARISI_BASILDI = False
_ILERLEME_ADIMI = 20  # her N tokende bir ilerleme satırı bas (sessiz kalıp "donmuş gibi" görünmesin diye)


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

    def baslangic_durumu_kopyala(self) -> None:
        """rwkv_oturum.py için: TTT devre dışıysa (bkz. ttt_lora.lora_adaptoru_kur)
        öğrenilmiş bir durum yok -- `rwkv` paketi zaten `durum=None`'ı sıfır
        durum olarak yorumluyor, o yüzden burada da None döndürülür."""
        return None

    def _agirlik_sozlugu(self) -> Any:
        """RWKV-7 (RWKV_x070) ağırlıklarını `self.z` sözlüğünde tutar;
        eski (v4/5/6) `RWKV` sınıfı `self.w` kullanır. RWKV_V7_ON=1 ile
        artık daima RWKV_x070 kullanıldığından `z` önce denenir, ama
        eski sınıfla da (örn. test/gelecek uyumluluk) çalışmaya devam
        etsin diye `w`'ye geri düşülür. Gerçek kurulu `rwkv==0.8.32`
        kaynağı doğrudan okunarak doğrulandı (RWKV_x070.__init__ içinde
        `self.z = {}`, `self.w` YOK)."""
        sozluk = getattr(self._rwkv, "z", None)
        if sozluk is None:
            sozluk = getattr(self._rwkv, "w", None)
        if sozluk is None:
            raise AttributeError(
                "native rwkv modelinde ne 'z' (RWKV-7) ne de 'w' (eski sürüm) "
                "ağırlık sözlüğü bulundu; `rwkv` paketinin sürümü/mimarisi değişmiş olabilir."
            )
        return sozluk

    def parameters(self, recurse: bool = True):
        for tensor in self._agirlik_sozlugu().values():
            if isinstance(tensor, torch.Tensor):
                yield tensor

    def named_parameters(self, prefix: str = "", recurse: bool = True):
        for isim, tensor in self._agirlik_sozlugu().items():
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
        sorunsuz calisir.

        ONEMLI PERFORMANS NOTU: `rwkv` paketinin KENDI forward() metodu,
        TEK bir cagriya BIRDEN FAZLA token listesi verilince (`len(idx)>1`)
        otomatik olarak `forward_seq`'e yonlenir -- bu, katman basina TEK
        Python/JIT cagrisiyla tum diziyi isler. Onceden burada her token
        icin AYRI bir `forward([token], state)` cagrisi yapiliyordu; bu,
        7.2B/32-katmanlik modelde katman-basi kurulum/JIT dispatch
        maliyetini T KERE tekrarlatip devasa bir yavaslamaya yol aciyordu.
        Simdi satir basina TEK cagri (`forward(tum_token_listesi, state,
        full_output=True)`) yapiliyor."""
        B, T = input_ids.shape
        durumlar = list(past_key_values) if past_key_values is not None else [None] * B

        baslangic = time.time()
        if B > _ILERLEME_ADIMI:
            print(f"[rwkv_native] forward(): {B} satır x {T} token, her satır TEK forward_seq çağrısıyla işleniyor...")
        tum_logitler = []
        yeni_durumlar = []
        for b in range(B):
            durum = durumlar[b]
            token_listesi = input_ids[b].tolist()
            if len(token_listesi) > 1:
                logitler, durum = self._rwkv.forward(token_listesi, durum, full_output=True)
                satir_logitleri = torch.as_tensor(logitler, device=self._cihaz)
            else:
                logit, durum = self._rwkv.forward(token_listesi, durum)
                satir_logitleri = torch.as_tensor(logit, device=self._cihaz).unsqueeze(0)
            tum_logitler.append(satir_logitleri)
            yeni_durumlar.append(durum)
            if (b + 1) % _ILERLEME_ADIMI == 0 or (b + 1) == B:
                gecen = time.time() - baslangic
                print(f"[rwkv_native]   forward(): {b + 1}/{B} satır işlendi ({gecen:.1f} sn)")

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

    def ileri_besle_tokenler(self, token_ids: List[int], durum: Optional[List[torch.Tensor]]) -> Tuple[Any, List[torch.Tensor]]:
        """Verilen token dizisini TEK bir forward çağrısıyla besler, (son_logit,
        güncellenmiş_durum) döndürür. ÇAĞIRAN TARAF durumu SAKLAYIP bir sonraki
        adımda buradan devam edebilir -- coz_yurutucu.py'nin çok-turlu araç
        döngüsünde (bkz. rwkv_oturum.py) AYNI tokenlerin İKİNCİ kez asla
        işlenmemesi tam olarak bu metotla sağlanır."""
        if not token_ids:
            raise ValueError("ileri_besle_tokenler: boş token listesi verildi")
        baslangic = time.time()
        if len(token_ids) > 1:
            son_logits, durum = self._rwkv.forward(token_ids, durum, full_output=False)
        else:
            son_logits, durum = self._rwkv.forward(token_ids, durum)
        if len(token_ids) > 1:
            gecen = time.time() - baslangic
            print(f"[rwkv_native] {len(token_ids)} token TEK çağrıyla işlendi ({gecen:.1f} sn, {len(token_ids) / max(gecen, 1e-6):.2f} token/sn).")
        return son_logits, durum

    def uret_devam(self, son_logits: Any, durum: Optional[List[torch.Tensor]], max_new_tokens: int,
                    do_sample: bool = True, temperature: Optional[float] = None,
                    top_p: Optional[float] = None, pad_token_id: Optional[int] = None
                    ) -> Tuple[List[int], Any, List[torch.Tensor]]:
        """generate()'in oto-regresif kısmı: HAZIR bir (son_logits, durum)
        çiftinden devam eder, prefill'i TEKRARLAMAZ. Dönen `durum`, üretilen
        TÜM tokenleri de kapsar (RNN'in doğası gereği state zaten bu tokenleri
        "görmüş" haldedir) -- bir sonraki turde bu tokenleri TEKRAR beslemeye
        gerek yoktur."""
        uretim_baslangici = time.time()
        uretilenler: List[int] = []
        for _adim in range(max_new_tokens):
            olasiliklar = torch.softmax(
                torch.as_tensor(son_logits) / max(temperature or 1.0, 1e-4), dim=-1
            )
            if do_sample:
                sonraki_token = int(torch.multinomial(olasiliklar, 1).item())
            else:
                sonraki_token = int(torch.argmax(olasiliklar).item())

            uretilenler.append(sonraki_token)
            if (_adim + 1) % _ILERLEME_ADIMI == 0:
                gecen = time.time() - uretim_baslangici
                print(f"[rwkv_native]   üretim: {_adim + 1}/{max_new_tokens} token üretildi ({gecen:.1f} sn, {(_adim + 1) / max(gecen, 1e-6):.2f} token/sn)")
            if pad_token_id is not None and sonraki_token == pad_token_id:
                break

            son_logits, durum = self._rwkv.forward([sonraki_token], durum)

        gecen_toplam = time.time() - uretim_baslangici
        print(f"[rwkv_native] üretim tamamlandı: {len(uretilenler)} token, {gecen_toplam:.1f} sn.")
        return uretilenler, son_logits, durum

    @torch.no_grad()
    def generate(self, input_ids: torch.Tensor, max_new_tokens: int = 768,
                 do_sample: bool = True, temperature: Optional[float] = None,
                 top_p: Optional[float] = None, pad_token_id: Optional[int] = None,
                 baslangic_durumu: Optional[List[torch.Tensor]] = None,
                 **_yoksayilan: Any) -> torch.Tensor:
        B, T = input_ids.shape
        assert B == 1, "native RWKV generate() şu an tek örnek (B=1) destekliyor"

        durum = [t.clone() for t in baslangic_durumu] if baslangic_durumu is not None else None
        prompt_token_listesi = input_ids[0].tolist()
        # PERFORMANS: onceden burada T ayrı forward([token], state) cagrisi
        # yapiliyordu (bkz. forward()'daki not) -- tum prompt'u TEK
        # forward_seq cagrisiyla isleyip yalnizca son pozisyonun logitini
        # istiyoruz (full_output=False, kutuphanenin varsayilani).
        son_logits, durum = self.ileri_besle_tokenler(prompt_token_listesi, durum)

        uretilenler, _son_logits, _durum = self.uret_devam(
            son_logits, durum, max_new_tokens,
            do_sample=do_sample, temperature=temperature, top_p=top_p, pad_token_id=pad_token_id,
        )
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


_RWKV_CUDA_ON_DENENDI = False


def _rwkv_cuda_kernelini_dene_etkinlestir() -> None:
    """`rwkv` paketi, RWKV_CUDA_ON=1 ile (rwkv.model.py satır 200-220
    civarı, WKV_7 sınıfı) token-başına üretimi ELLE YAZILMIŞ, derlenmiş bir
    CUDA kernel'iyle (rwkv7.cu) çalıştırabiliyor -- bu, bizim şu an
    kullandığımız genel PyTorch yolundan (ölçülen: ~16 token/sn, 7.2B
    modelde beklenenden yavaş) kayda değer ölçüde hızlı olabilir.

    RİSK: bu, `torch.utils.cpp_extension.load` ile bir CUDA uzantısını
    JIT DERLER; derleme ortamda nvcc/ninja yoksa ya da mimari uyuşmazsa
    İSTİSNA fırlatır -- ve bu istisna `rwkv.model` İLK import edildiğinde
    modül-seviyesinde gerçekleştiği için, ana süreçte doğrudan denersek
    BAŞARISIZLIK TÜM ÇALIŞTIRMAYI ÇÖKERTİR (geri dönüşü yok, çünkü RWKV
    tek model adayımız). Bu yüzden önce AYRI bir alt süreçte (asıl model
    yüklemesini hiç etkilemeden) "derlenebiliyor mu" diye TEK SEFERLİK
    sınanır; yalnızca o sınama BAŞARILI olursa RWKV_CUDA_ON=1 ana sürece
    de yansıtılır. Başarısız olursa (ya da zaten env var elle verilmişse,
    ya da CUDA yoksa) sessizce şimdiki (her zaman çalışan, ama yavaş)
    PyTorch yoluna devam edilir."""
    global _RWKV_CUDA_ON_DENENDI
    if _RWKV_CUDA_ON_DENENDI:
        return
    _RWKV_CUDA_ON_DENENDI = True

    if os.environ.get("RWKV_CUDA_ON") is not None:
        return  # kullanıcı zaten elle ayarlamış, dokunma
    if not torch.cuda.is_available():
        return  # özel CUDA kernel'i yalnızca GPU'da anlamlı

    import subprocess
    import sys as _sys

    prob_kodu = (
        "import os; os.environ['RWKV_V7_ON']='1'; os.environ['RWKV_CUDA_ON']='1'; "
        "import rwkv.model; print('RWKV_CUDA_PROB_OK')"
    )
    sonuc = None
    try:
        sonuc = subprocess.run(
            [_sys.executable, "-c", prob_kodu],
            capture_output=True, text=True, timeout=300,
        )
        basarili = sonuc.returncode == 0 and "RWKV_CUDA_PROB_OK" in sonuc.stdout
    except Exception as prob_hatasi:
        basarili = False
        print(f"[rwkv_native] RWKV_CUDA_ON sınaması çalıştırılamadı: {prob_hatasi}")

    if basarili:
        os.environ["RWKV_CUDA_ON"] = "1"
        print(
            "[rwkv_native] RWKV_CUDA_ON=1: özel CUDA kernel derlemesi BAŞARILI "
            "(ayrı bir alt süreçte sınandı) -- hızlandırılmış üretim yolu etkinleştiriliyor."
        )
    elif sonuc is not None:
        hata_ozeti = (sonuc.stderr or "")[-1000:]
        print(
            "[rwkv_native] RWKV_CUDA_ON=1 sınaması BAŞARISIZ -- genel (daha yavaş ama "
            f"HER ZAMAN çalışan) PyTorch yoluna devam ediliyor. Alt süreç hatası:\n{hata_ozeti}"
        )


def native_rwkv_yukle(pth_yolu: str, veri_tipi: torch.dtype = torch.bfloat16) -> RWKVUyumluModel:
    # RWKV_V7_ON=1 (model_yapilandirmalari.py'de import-oncesi ayarlanir)
    # `rwkv.model.RWKV`'yi DAIMA `RWKV_x070` sinifina cozer -- gercek
    # kurulu rwkv==0.8.32 kaynagi dogrudan okunarak dogrulandi (model.py
    # satir 1679-1680: `if RWKV_V7_ON == '1': RWKV = RWKV_x070`). Eski
    # (v4/5/6) `RWKV` sinifina ozgu `args.n_head`/`args.n_att` yamasi
    # bu yuzden hicbir zaman calismiyordu/gerekmiyordu -- RWKV_x070
    # kendi `self.n_head`/`self.head_size` degerlerini checkpoint'ten
    # dogrudan turetiyor (bkz. RWKVUyumluModel._agirlik_sozlugu).
    _rwkv_cuda_kernelini_dene_etkinlestir()
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
