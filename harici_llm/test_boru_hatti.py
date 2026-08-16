"""
Uctan uca boru hatti testi.

Onemli: bu dosya bulmacanin kaidesini COZMEZ ve kaide kodu icermez — kural
kesfi daima gercek modelin (RWKV/Mamba/Falcon-Mamba, Kaggle'da) isidir.
Burada sadece MEKANIZMANIN dogru calistigi kanitlanir: arac-cagirma
ayiklama+yurutme, submit_answer'in satir/sutun tutarsizligini KENDIMIZ
DUZELTMEDEN reddetmesi, gercek gradyan adimlariyla TTT, ve turbo_dfs MCTS
dallanmasinin gercekten birden fazla aday uretmesi. Model olarak "bizim
vasifsiz model de olabilir" talimati geregince kucuk, gercek (mock degil,
gercekten forward/backward calisan) bir torch modeli kullanilir; bu model
bulmacayi COZEMEYECEK kadar kucuktur ve bu beklenen bir durumdur.
"""
import sys
from typing import Any, Dict, List, Optional

import numpy as np
import torch
import torch.nn as nn

from arc import Example, Task
from araclar import CevapDefteri, arac_cagrilarini_ayikla, arac_cagrisini_yurut, submit_answer_arac
from mcts_dallanma import arac_kelime_dagarcigi_olustur, inference_turbo_dfs
from ttt_lora import _tamamlama_sadece_etiketleri_olustur, gorev_ozelinde_ince_ayar

BASARISIZLIK_SAYACI = {"n": 0}


def _dogrula(kosul: bool, mesaj: str) -> None:
    if not kosul:
        BASARISIZLIK_SAYACI["n"] += 1
        print(f"  [BAŞARISIZ] {mesaj}")
    else:
        print(f"  [OK] {mesaj}")


class VasifsizKucukDil(nn.Module):
    """Gercekten forward/backward calisan, kucuk (vasifsiz) bir dil modeli
    kaligi. Herhangi bir ARC kuralini bilmez / bilemez; sadece boru hattinin
    mekanizmasini (TTT gradyan akisi, MCTS onbellek arayuzu) test etmek
    icindir."""

    def __init__(self, vocab_boyutu: int = 32, d: int = 16):
        super().__init__()
        self.gomulu = nn.Embedding(vocab_boyutu, d)
        self.govde = nn.GRUCell(d, d)
        self.baslik = nn.Linear(d, vocab_boyutu)
        self.d = d

    @property
    def device(self):
        return next(self.parameters()).device

    def forward(self, input_ids: torch.Tensor, position_ids=None,
                past_key_values=None, use_cache=True, return_dict=True, labels=None):
        B, T = input_ids.shape
        h = past_key_values if past_key_values is not None else torch.zeros(B, self.d, device=input_ids.device)
        tum_logitler = []
        for t in range(T):
            x = self.gomulu(input_ids[:, t])
            h = self.govde(x, h)
            tum_logitler.append(self.baslik(h))
        logits = torch.stack(tum_logitler, dim=1)

        class _Cikti:
            pass
        cikti = _Cikti()
        cikti.logits = logits
        cikti.past_key_values = h
        cikti.loss = None
        if labels is not None:
            kaydirilmis_logits = logits[:, :-1, :].reshape(-1, logits.shape[-1])
            kaydirilmis_hedefler = labels[:, 1:].reshape(-1)
            if kaydirilmis_hedefler.numel() > 0:
                cikti.loss = torch.nn.functional.cross_entropy(kaydirilmis_logits, kaydirilmis_hedefler)
            else:
                cikti.loss = logits.sum() * 0.0
        return cikti


class _CihazaTasinabilirSozluk(dict):
    def to(self, cihaz):
        return _CihazaTasinabilirSozluk({k: v.to(cihaz) for k, v in self.items()})


class BasitTokenizer:
    """Karakter tabanli, gercek bir tokenizer'in minimal arayuzunu (encode,
    __call__ (HF BatchEncoding gibi .to() destekler), pad_token_id,
    eos_token_id) taklit eder."""

    def __init__(self, vocab_boyutu: int = 32):
        self.vocab_boyutu = vocab_boyutu
        self.pad_token_id = 0
        self.eos_token_id = 1

    def encode(self, metin: str, add_special_tokens: bool = True) -> List[int]:
        return [(ord(c) % (self.vocab_boyutu - 2)) + 2 for c in metin]

    def __call__(self, metin: str, return_tensors: str = "pt", truncation: bool = True, max_length: int = 4096):
        idler = self.encode(metin)[:max_length]
        if not idler:
            idler = [self.pad_token_id]
        return _CihazaTasinabilirSozluk({"input_ids": torch.tensor([idler], dtype=torch.long)})

    def decode(self, idler, skip_special_tokens: bool = True) -> str:
        return "".join(chr(max(32, int(t))) for t in idler)


def test_1_arac_cagrisi_ayiklama() -> None:
    print("[test 1] Araç çağrısı ayıklama (iki RWKV şablon biçimi)...")

    metin_a = '```json\n{"name": "submit_answer", "arguments": {"grid": [[1, 2], [3, 4]]}}\n```'
    cagrilar_a = arac_cagrilarini_ayikla(metin_a)
    _dogrula(len(cagrilar_a) == 1 and cagrilar_a[0]["name"] == "submit_answer", "```json fence biçimi ayıklandı")

    metin_b = '<think></think\n<tool_call>\n{"name": "execute_python", "arguments": {"code": "sonuc = 1+1"}}\n</tool_call>'
    cagrilar_b = arac_cagrilarini_ayikla(metin_b)
    _dogrula(len(cagrilar_b) == 1 and cagrilar_b[0]["name"] == "execute_python", "<tool_call> etiket biçimi ayıklandı")


def test_2_cevap_verme_araci_boyut_tutarliligi() -> None:
    print("[test 2] submit_answer: tutarsız satır/sütun sayısı REDDEDİLMELİ, kendimiz düzeltmemeliyiz...")

    defter = CevapDefteri()
    tutarsiz_grid = [[1, 2, 3], [4, 5], [6, 7, 8]]
    sonuc = submit_answer_arac(tutarsiz_grid, defter)

    _dogrula(sonuc["basarili"] is False, "tutarsız ızgara reddedildi")
    _dogrula(defter.kaydedilen_cevap is None, "reddedilen ızgara SESSİZCE düzeltilip kaydedilmedi")
    _dogrula("satır 0: 3 sütun" in sonuc["hata"] and "satır 1: 2 sütun" in sonuc["hata"],
              "hata mesajı hangi satırların kaç sütun olduğunu açıkça söylüyor")
    print(f"    -> döndürülen hata: {sonuc['hata']}")

    defter2 = CevapDefteri()
    tutarli_grid_farkli_boyut = [[9, 9, 9, 9, 9], [8, 8, 8, 8, 8]]
    sonuc2 = submit_answer_arac(tutarli_grid_farkli_boyut, defter2)
    _dogrula(sonuc2["basarili"] is True, "kendi içinde tutarlı fakat train örneklerinden FARKLI boyutlu ızgara kabul edildi (boyut değişebilir)")
    _dogrula(defter2.kaydedilen_cevap == tutarli_grid_farkli_boyut, "kaydedilen cevap AYNEN (yeniden boyutlandırılmadan) saklandı")


def test_3_arac_cagrisini_yurutme_ve_hata_donen_akis() -> None:
    print("[test 3] Ajan döngüsü: önce hatalı boyut dener, hatayı görür, sonra düzeltir...")

    defter = CevapDefteri()

    cagri_1 = {"name": "submit_answer", "arguments": {"grid": [[1, 1], [2]]}}
    sonuc_1 = arac_cagrisini_yurut(cagri_1, defter)
    _dogrula(not sonuc_1["basarili"], "1. deneme (tutarsız) reddedildi")
    _dogrula(defter.kaydedilen_cevap is None, "1. denemeden sonra kayıtlı cevap hâlâ yok")

    cagri_2 = {"name": "execute_python", "arguments": {"code": "sonuc = [x*2 for x in range(3)]"}}
    sonuc_2 = arac_cagrisini_yurut(cagri_2, defter)
    _dogrula(sonuc_2["basarili"] and sonuc_2["sonuc"] == [0, 2, 4], "execute_python aracı gerçekten çalıştı ve doğru sonucu döndü")

    cagri_3 = {"name": "submit_answer", "arguments": {"grid": [[1, 1], [2, 2]]}}
    sonuc_3 = arac_cagrisini_yurut(cagri_3, defter)
    _dogrula(sonuc_3["basarili"], "2. deneme (tutarlı) kabul edildi")
    _dogrula(defter.kaydedilen_cevap == [[1, 1], [2, 2]], "nihai cevap doğru kaydedildi")


def test_4_gercek_ttt_gradyan_adimlari() -> None:
    print("[test 4] Gerçek TTT gradyan adımları (vasıfsız küçük model üzerinde)...")

    model = VasifsizKucukDil()
    tokenizer = BasitTokenizer()

    baslangic_agirlik = model.baslik.weight.detach().clone()

    egitim_metinleri = [
        "Task ID: test\n\nInput:\n12\n34\n\nOutput:\n21\n43",
        "Task ID: test\n\nInput:\n56\n78\n\nOutput:\n65\n87",
    ]
    kayip_gecmisi = gorev_ozelinde_ince_ayar(model, tokenizer, egitim_metinleri, adim_sayisi=8, azami_token=64)

    _dogrula(len(kayip_gecmisi) == 8, "8 gerçek eğitim adımı çalıştı")
    _dogrula(not torch.allclose(baslangic_agirlik, model.baslik.weight), "ağırlıklar gerçekten güncellendi (gradyan aktı)")
    print(f"    -> kayıp geçmişi: {[round(k, 4) for k in kayip_gecmisi]}")


def test_5_mcts_turbo_dfs_dallanma() -> None:
    print("[test 5] MCTS/turbo_dfs dallanma: verilen algoritma gerçekten çoklu aday üretiyor mu?...")

    model = VasifsizKucukDil(vocab_boyutu=16, d=8)
    tokenizer = BasitTokenizer(vocab_boyutu=16)
    arac_vocab = arac_kelime_dagarcigi_olustur(tokenizer)

    onek = tokenizer.encode("12")
    sonuclar = inference_turbo_dfs(
        model, "standart", arac_vocab,
        prefix_tokens=[onek],
        max_new_tokens=3,
        max_score=8.0,
        end_time=__import__("time").time() + 10,
    )

    _dogrula(len(sonuclar) >= 1, "turbo_dfs en az bir dal döndürdü")
    toplam_dal = sum(len(beams) for _bid, beams in sonuclar)
    _dogrula(toplam_dal >= 2, f"MCTS dallanması BİRDEN FAZLA aday ürettiği (gerçek dallanma): {toplam_dal} dal")
    print(f"    -> {toplam_dal} dal üretildi (skorlu aday diziler).")


def test_6_kaide_kodu_yok_denetimi() -> None:
    print("[test 6] Kendi yazdığım kural/kaide kodu deposundan tamamen silindi mi?...")

    import os
    for dosya in os.listdir("."):
        if not dosya.endswith(".py") or dosya == "test_boru_hatti.py":
            continue
        with open(dosya, "r", encoding="utf-8") as f:
            icerik = f.read()
        _dogrula(
            "def transform(grid" not in icerik,
            f"{dosya} içinde sabit-kodlanmış bir 'def transform(grid...' kural fonksiyonu YOK",
        )


def test_7_uctan_uca_gorevi_coz() -> None:
    print("[test 7] coz_yurutucu.gorevi_coz(): gerçek Task + gerçek TTT + çok-turlu araç döngüsü birlikte...")

    import coz_yurutucu

    task = Task(
        test_example=Example(input=np.array([[0, 0], [0, 0]]), output=np.array([[0, 0], [0, 0]])),
        train_examples=[
            Example(input=np.array([[1, 2], [3, 4]]), output=np.array([[4, 3], [2, 1]])),
            Example(input=np.array([[5, 6], [7, 8]]), output=np.array([[8, 7], [6, 5]])),
        ],
        name="testgorev-0",
    )

    model = VasifsizKucukDil()
    tokenizer = BasitTokenizer()

    senaryo = [
        '```json\n{"name": "execute_python", "arguments": {"code": "sonuc = 1"}}\n```',
        '```json\n{"name": "submit_answer", "arguments": {"grid": [[1, 2, 3], [4]]}}\n```',
        '```json\n{"name": "submit_answer", "arguments": {"grid": [[9, 9], [9, 9]]}}\n```',
    ]
    sayac = {"i": 0}

    def sahte_uret_sohbet(lora_model, tok, model_ailesi, mesajlar, azami_yeni_token=900):
        yanit = senaryo[min(sayac["i"], len(senaryo) - 1)]
        sayac["i"] += 1
        return yanit

    coz_yurutucu.uret_sohbet = sahte_uret_sohbet

    sonuc = coz_yurutucu.gorevi_coz(
        model, tokenizer, "rwkv", task,
        varsayilan_lora_agirliklari=None, cogaltma_n=2, ttt_adim_sayisi=2,
        azami_token=256, azami_tur=4,
    )

    _dogrula("attempt_1" in sonuc and "attempt_2" in sonuc, "gorevi_coz submission şemasını (attempt_1/attempt_2) döndürdü")
    _dogrula(sonuc["attempt_1"] == [[9, 9], [9, 9]], "tutarsız ilk deneme atlandı, tutarlı ikinci deneme kaydedildi")
    print(f"    -> gorevi_coz sonucu: {sonuc}")


class _OfsetliSahteTokenizer:
    """offset_mapping destekleyen bir hızlı tokenizer'ı taklit eder;
    tamamlama-sadece (completion-only) maskeleme testinde kullanılır."""

    def __call__(self, metin, return_tensors=None, truncation=True, max_length=4096, return_offsets_mapping=False):
        idler = [(ord(c) % 30) + 2 for c in metin]
        if return_offsets_mapping:
            offsetler = [(i, i + 1) for i in range(len(metin))]
            return {"input_ids": idler, "offset_mapping": offsetler}
        return {"input_ids": idler}


def test_8_tamamlama_sadece_maskeleme() -> None:
    print("[test 8] arc_solver.py'nin QwenDataCollatorForCompletionOnlyLM'inin genel karşılığı: yalnız asistan/çıktı kısmından gradyan...")

    tok = _OfsetliSahteTokenizer()
    metin = "User: 12\n\nAssistant: 21\n\nUser: 34\n\nAssistant: 43\n\n"
    kodlama = tok(metin, return_offsets_mapping=True)

    etiketler = _tamamlama_sadece_etiketleri_olustur(tok, metin, "rwkv", kodlama["input_ids"], kodlama["offset_mapping"])

    _dogrula(etiketler is not None, "tamamlama maskesi üretildi (None dönmedi)")

    ilk_assistant_baslangic = metin.index("Assistant:") + len("Assistant:")
    ilk_assistant_bitis = metin.index("\n\n", ilk_assistant_baslangic)
    _dogrula(
        all(e == -100 for e in etiketler[:ilk_assistant_baslangic]),
        "ilk 'User:' bölümündeki TÜM tokenlar -100 ile maskelendi (bu kısımdan gradyan alınmıyor)",
    )
    _dogrula(
        all(e != -100 for e in etiketler[ilk_assistant_baslangic:ilk_assistant_bitis]),
        "ilk 'Assistant:' çıktı bölümündeki tokenlar MASKELENMEDİ (yalnızca buradan gradyan alınıyor)",
    )

    ikinci_assistant_baslangic = metin.index("Assistant:", ilk_assistant_bitis) + len("Assistant:")
    _dogrula(
        etiketler[ikinci_assistant_baslangic] != -100,
        "İKİNCİ 'Assistant:' turu da (çok-turlu metin) doğru şekilde maskesiz bırakıldı",
    )
    print(f"    -> {sum(1 for e in etiketler if e == -100)}/{len(etiketler)} token maskelendi (yalnız kullanıcı/girdi kısmı).")


def test_9_ne_olursa_olsun_kayit_garantisi() -> None:
    print("[test 9] gonderim_uret._SonuCuKaydedici: hata/kesme/süre bitmesi FARK ETMEKSİZİN o ana kadarki sonuçlar kaydediliyor mu?...")

    import json
    import os
    import tempfile

    from gonderim_uret import _SonuCuKaydedici

    sahte_gorevler = [
        Task(test_example=Example(input=np.zeros((1, 1)), output=np.zeros((1, 1))), train_examples=[], name=f"gorev{i}-0")
        for i in range(5)
    ]

    with tempfile.TemporaryDirectory() as gecici_dizin:
        cikti_yolu = os.path.join(gecici_dizin, "submission.json")
        kaydedici = _SonuCuKaydedici(sahte_gorevler, cikti_yolu)

        kaydedici.ekle([[[1, 1]], [[1, 1]]])
        kaydedici.ekle([[[2, 2]], [[2, 2]]])

        try:
            raise RuntimeError("simüle edilmiş çökme (3. görev sırasında)")
        except RuntimeError:
            pass
        finally:
            kaydedici._son_kayit()

        _dogrula(os.path.isfile(cikti_yolu), "hata sonrası submission.json dosyası GERÇEKTEN diskte var")

        with open(cikti_yolu, "r", encoding="utf-8") as f:
            diskteki = json.load(f)

        _dogrula(len(diskteki) == 5, f"tüm {len(sahte_gorevler)} görev submission şemasında yer alıyor (eksik kalanlar boş dolduruldu)")
        _dogrula(diskteki["gorev0"][0]["attempt_1"] == [[1, 1]], "1. görevin GERÇEK sonucu (çökmeden önce üretilen) kayıtlı")
        _dogrula(diskteki["gorev1"][0]["attempt_1"] == [[2, 2]], "2. görevin GERÇEK sonucu (çökmeden önce üretilen) kayıtlı")
        _dogrula(diskteki["gorev2"][0]["attempt_1"] == [[0, 0], [0, 0]], "hiç işlenmemiş 3. görev BOŞ yer tutucuyla dolduruldu, uydurma bir sonuç yazılmadı")
        print(f"    -> diskteki submission.json: {list(diskteki.keys())}")


class _SahteNativeRWKV:
    """rwkv.model.RWKV'nin minimal, TÜREVLENEBİLİR bir taklidi: gerçek
    forward(idx, state, full_output=False) arayüzünü (tek token İSE
    forward_one, BİRDEN FAZLA token listesi İSE forward_seq'e denk
    düşen tek-çağrılık toplu işleme) ve self.w ağırlık sözlüğünü taşır.
    Bu ayrım kritik: gerçek pakette forward([t1,t2,...], state) TEK bir
    çağrıda tüm diziyi işler (rwkv_native.py'nin performans düzeltmesi
    tam olarak bunu kullanıyor) -- token-başına ayrı çağrı YAPMAZ."""

    def __init__(self, vocab: int = 60, d: int = 4):
        self.vocab = vocab
        self.d = d
        self.emb = torch.nn.Parameter(torch.randn(vocab, d))
        self.head = torch.nn.Parameter(torch.randn(d, vocab))
        self.w = {"emb.weight": self.emb, "head.weight": self.head}
        self.coklu_token_cagri_sayaci = 0
        self.tekli_token_cagri_sayaci = 0

    def forward(self, tokens, state, full_output=False):
        if len(tokens) > 1:
            self.coklu_token_cagri_sayaci += 1
        else:
            self.tekli_token_cagri_sayaci += 1
        durum = state if state is not None else [torch.zeros(self.d)]
        tum_logitler = []
        for tok in tokens:
            x = self.emb[tok]
            durum = [0.5 * durum[0] + 0.5 * x]
            tum_logitler.append(durum[0] @ self.head)
        if len(tokens) > 1 and full_output:
            return torch.stack(tum_logitler, dim=0), durum
        return tum_logitler[-1], durum


class _SahteNativeRWKV_x070(_SahteNativeRWKV):
    """Gerçek `rwkv==0.8.32` kaynağında (RWKV_V7_ON=1 iken kullanılan
    RWKV_x070 sınıfı) doğrulandığı gibi ağırlıklar `self.w` DEĞİL
    `self.z` sözlüğünde tutulur. Bu sınıf o gerçek adlandırmayı taklit
    eder; RWKVUyumluModel._agirlik_sozlugu() 'z'yi bulup kullanabilmeli."""

    def __init__(self, vocab: int = 60, d: int = 4):
        super().__init__(vocab, d)
        self.z = self.w
        del self.w


class _SahteNativeRWKVNoGrad(_SahteNativeRWKV):
    """Gerçek `rwkv` pip paketinin forward_one/forward_seq'inin (rwkv==0.8.32
    kaynağında doğrudan tespit edilen) `torch.no_grad()` sarmalını taklit
    eder: state-tuning için gradyan akışı YAPISAL olarak imkansızdır."""

    def forward(self, tokens, state, full_output=False):
        with torch.no_grad():
            return super().forward(tokens, state, full_output=full_output)


class _RWKVStateTuningTokenizer:
    def __call__(self, metin, return_tensors=None, truncation=True, max_length=64, return_offsets_mapping=False):
        idler = [(ord(c) % 58) + 1 for c in metin][:max_length]
        if return_tensors == "pt":
            class _D(dict):
                def to(self, cihaz):
                    return self
            return _D({"input_ids": torch.tensor([idler])})
        return {"input_ids": idler}

    def encode(self, metin, add_special_tokens=True):
        return [(ord(c) % 58) + 1 for c in metin]


def test_10_rwkv_state_tuning() -> None:
    print("[test 10] RWKV state-tuning: LoRA'nın çalışmadığı native (.pth) yolda ağırlıklara dokunmadan öğrenilebilir başlangıç durumu...")

    from rwkv_native import RWKVUyumluModel
    from rwkv_state_tuning import RWKVDurumAyarlayici, state_egitimi_calisir_mi_dogrula
    from ttt_lora import adaptoru_sifirla

    native = _SahteNativeRWKV()
    sarmali = RWKVUyumluModel(native, "cpu fp32")
    durum_ayarlayici = RWKVDurumAyarlayici(sarmali)

    state_egitimi_calisir_mi_dogrula(durum_ayarlayici)
    print("    -> autograd doğrulaması geçti (state parametrelerinden gerçek gradyan akıyor).")

    _dogrula(not native.emb.requires_grad and not native.head.requires_grad,
              "taban (native) ağırlıklar requires_grad=False ile donduruldu")

    egitilebilir = [p for p in durum_ayarlayici.parameters() if p.requires_grad]
    _dogrula(len(egitilebilir) == len(list(durum_ayarlayici.durum_parametreleri)),
              "optimizer'a giden eğitilebilir parametreler YALNIZCA state parametreleri (taban ağırlıklar değil)")

    tok = _RWKVStateTuningTokenizer()
    oncesi = durum_ayarlayici.durum_anlik_goruntusu_al()
    gorev_ozelinde_ince_ayar(durum_ayarlayici, tok, ["abcabc", "xyzxyz"], adim_sayisi=5, azami_token=32)
    sonrasi = durum_ayarlayici.durum_anlik_goruntusu_al()
    _dogrula(any(not torch.allclose(a, b) for a, b in zip(oncesi, sonrasi)),
              "state parametreleri gerçek gradyan adımlarıyla güncellendi")

    adaptoru_sifirla(durum_ayarlayici)
    sifirlanmis = durum_ayarlayici.durum_anlik_goruntusu_al()
    _dogrula(all(torch.allclose(a, torch.zeros_like(a)) for a in sifirlanmis),
              "adaptoru_sifirla() ile state başlangıç değerine (sıfır) geri döndü")


def test_11_rwkv_no_grad_backend_zarifce_devre_disi_birakir() -> None:
    print("[test 11] Gerçek `rwkv` paketindeki gibi torch.no_grad()-sarmalı bir backend ile lora_adaptoru_kur() ÇÖKMEDEN TTT'yi devre dışı bırakıyor mu?...")

    from rwkv_native import RWKVUyumluModel
    from ttt_lora import lora_adaptoru_kur

    native = _SahteNativeRWKVNoGrad()
    sarmali = RWKVUyumluModel(native, "cpu fp32")

    sonuc = lora_adaptoru_kur(sarmali, "rwkv")

    _dogrula(sonuc is sarmali,
              "no_grad backend'de lora_adaptoru_kur() çökmeden çıplak base_model'i döndürdü (TTT devre dışı)")
    _dogrula(not hasattr(sonuc, "durum_parametreleri"),
              "dönen model bir RWKVDurumAyarlayici DEĞİL (state-tuning sarmalanmadı)")


def test_12_rwkv_x070_z_sozlugu_gercek_kaggle_cokmesi() -> None:
    print("[test 12] Gerçek Kaggle çökmesi (AttributeError: 'RecursiveScriptModule' object has no attribute 'w'): RWKV_x070'in GERÇEK 'z' sözlüğü ile parameters()/named_parameters() çalışıyor mu?...")

    from rwkv_native import RWKVUyumluModel
    from rwkv_state_tuning import RWKVDurumAyarlayici, state_egitimi_calisir_mi_dogrula

    native = _SahteNativeRWKV_x070()
    _dogrula(not hasattr(native, "w"), "sahte model gerçek RWKV_x070 gibi 'w' TAŞIMIYOR (yalnızca 'z')")

    sarmali = RWKVUyumluModel(native, "cpu fp32")
    parametreler = list(sarmali.parameters())
    _dogrula(len(parametreler) == 2, "parameters() 'z' sözlüğünden gerçek tensörleri okuyabildi (eski 'w' varsayımıyla çökmedi)")

    durum_ayarlayici = RWKVDurumAyarlayici(sarmali)
    state_egitimi_calisir_mi_dogrula(durum_ayarlayici)
    _dogrula(not native.emb.requires_grad and not native.head.requires_grad,
              "'z' sözlüğü üzerinden de taban ağırlıklar requires_grad=False ile donduruldu")


def test_13_rwkv_prompt_isleme_token_basina_degil_tek_cagriyla() -> None:
    print("[test 13] Performans: forward()/generate() promptu TOKEN-BAŞINA AYRI çağrı yerine TEK forward_seq çağrısıyla mı işliyor?...")

    from rwkv_native import RWKVUyumluModel

    native = _SahteNativeRWKV()
    sarmali = RWKVUyumluModel(native, "cpu fp32")

    uzun_prompt = torch.tensor([[(i % native.vocab) for i in range(37)]], dtype=torch.long)
    sarmali.forward(uzun_prompt)
    _dogrula(native.coklu_token_cagri_sayaci == 1 and native.tekli_token_cagri_sayaci == 0,
              "forward(): 37 token'lık tek satır TEK çoklu-token çağrısıyla işlendi (37 ayrı tekli-token çağrısı DEĞİL)")

    native2 = _SahteNativeRWKV()
    sarmali2 = RWKVUyumluModel(native2, "cpu fp32")
    sarmali2.generate(uzun_prompt, max_new_tokens=5, do_sample=False)
    _dogrula(native2.coklu_token_cagri_sayaci == 1,
              "generate(): 37 token'lık prompt TEK çoklu-token çağrısıyla (prefill) işlendi")
    _dogrula(native2.tekli_token_cagri_sayaci == 5,
              "generate(): prefill sonrası yalnızca gerçekten üretilen 5 token için (kaçınılmaz biçimde) tekli-token çağrısı yapıldı")


class _KarakterTabanliRWKVTokenizer:
    """RWKVUyumluTokenizer'ın minimal, karakter-tabanlı bir taklidi
    (gerçek dünya rwkv_vocab_v20230424 yerine, deterministik test için)."""

    def __init__(self) -> None:
        self.pad_token_id = 0
        self.eos_token_id = 0

    def encode(self, metin: str, add_special_tokens: bool = True) -> List[int]:
        return [(ord(c) % 58) + 1 for c in metin]

    def decode(self, token_idler: Any, skip_special_tokens: bool = True) -> str:
        if hasattr(token_idler, "tolist"):
            token_idler = token_idler.tolist()
        return "".join(chr(32 + (int(t) % 90)) for t in token_idler)


def test_14_rwkv_oturum_turler_arasi_durum_tasir_yeniden_islemez() -> None:
    print("[test 14] rwkv_oturum.RWKVSohbetOturumu: çok-turlu döngüde önceki turların tokenleri İKİNCİ kez işleniyor mu (performans)?...")

    from rwkv_native import RWKVUyumluModel
    from rwkv_oturum import RWKVSohbetOturumu

    native = _SahteNativeRWKV()
    sarmali = RWKVUyumluModel(native, "cpu fp32")
    tok = _KarakterTabanliRWKVTokenizer()

    oturum = RWKVSohbetOturumu(sarmali, tok)
    oturum.metin_isle("AAAA")  # 4 token, tek çoklu-token çağrısı
    _dogrula(native.coklu_token_cagri_sayaci == 1 and native.tekli_token_cagri_sayaci == 0,
              "ilk metin_isle(): 4 token TEK çoklu-token çağrısıyla işlendi")

    oturum.uret(azami_yeni_token=3, do_sample=False)
    _dogrula(native.tekli_token_cagri_sayaci == 3,
              "1. uret(): yalnızca gerçekten üretilen 3 token için tekli-token çağrısı yapıldı (prefill tekrarlanmadı)")

    oturum.metin_isle("BB")  # 2 YENİ token -- önceki 4+3=7 token TEKRAR işlenmemeli
    _dogrula(native.coklu_token_cagri_sayaci == 2,
              "2. metin_isle(): yalnızca 2 YENİ token için (önceki 7 token'ı YENİDEN işlemeden) ikinci bir çoklu-token çağrısı yapıldı")

    onceki_tekli = native.tekli_token_cagri_sayaci
    oturum.uret(azami_yeni_token=2, do_sample=False)
    _dogrula(native.tekli_token_cagri_sayaci - onceki_tekli == 2,
              "2. uret(): yalnızca 2 YENİ üretilen token için tekli-token çağrısı yapıldı")

    toplam_forward_cagrisi = native.coklu_token_cagri_sayaci + native.tekli_token_cagri_sayaci
    _dogrula(toplam_forward_cagrisi == 2 + 3 + 2,
              f"TOPLAM forward çağrısı tam olarak işlenen benzersiz token sayısına eşit ({toplam_forward_cagrisi} == 7); "
              f"eski 'her turde tüm geçmişi yeniden işle' yaklaşımında bu sayı çok daha yüksek olurdu (ör. 4+7+9=20)")


def test_15_coz_yurutucu_artimli_yol_uctan_uca() -> None:
    print("[test 15] coz_yurutucu._tek_deneme_uret_artimli(): native RWKV modelle uçtan uca (araç çağrısı ayıklama + submit_answer akışı) doğru çalışıyor mu?...")

    import coz_yurutucu
    from rwkv_native import RWKVUyumluModel

    task = Task(
        test_example=Example(input=np.array([[0, 0], [0, 0]]), output=np.array([[0, 0], [0, 0]])),
        train_examples=[Example(input=np.array([[1, 2], [3, 4]]), output=np.array([[4, 3], [2, 1]]))],
        name="testgorev-artimli",
    )

    native = _SahteNativeRWKV()
    model = RWKVUyumluModel(native, "cpu fp32")
    tok = _KarakterTabanliRWKVTokenizer()

    senaryo = [
        '```json\n{"name": "submit_answer", "arguments": {"grid": [[1, 2, 3], [4]]}}\n```',
        '```json\n{"name": "submit_answer", "arguments": {"grid": [[7, 7], [7, 7]]}}\n```',
    ]
    sayac = {"i": 0}

    class _SahteOturum:
        def __init__(self, model, tokenizer):
            pass

        def metin_isle(self, metin: str) -> None:
            pass

        def uret(self, azami_yeni_token, **kwargs) -> str:
            yanit = senaryo[min(sayac["i"], len(senaryo) - 1)]
            sayac["i"] += 1
            return yanit

    import rwkv_oturum
    gercek_sinif = rwkv_oturum.RWKVSohbetOturumu
    rwkv_oturum.RWKVSohbetOturumu = _SahteOturum
    try:
        sonuc = coz_yurutucu._tek_deneme_uret_artimli(model, tok, "rwkv", task, azami_tur=4, azami_yeni_token=50)
    finally:
        rwkv_oturum.RWKVSohbetOturumu = gercek_sinif

    _dogrula(sonuc == [[7, 7], [7, 7]],
              "tutarsız ilk deneme (satır uzunlukları farklı) reddedildi, tutarlı ikinci deneme kaydedildi")


def test_16_execute_python_gercekten_numpy_calistirabiliyor_mu() -> None:
    print("[test 16] execute_python: gerçek Kaggle transkriptlerinde görülen 'import numpy as np' GERÇEKTEN çalışıyor mu (önceden hiçbir import çalışmıyordu)?...")

    from araclar import kodu_guvenle_calistir_serbest

    basarili, sonuc = kodu_guvenle_calistir_serbest(
        "import numpy as np\n"
        "a = np.array([[1, 2], [3, 4]])\n"
        "sonuc = (a * 2).tolist()\n"
    )
    _dogrula(basarili, "'import numpy as np' içeren gerçek kod BAŞARIYLA çalıştı (eskiden AST aşamasında reddedilirdi)")
    _dogrula(sonuc == [[2, 4], [6, 8]], "numpy ile hesaplanan sonuç doğru")

    basarili2, sonuc2 = kodu_guvenle_calistir_serbest("import math\nsonuc = math.sqrt(16)\n")
    _dogrula(basarili2 and sonuc2 == 4.0,
              "önceden izinli sanılan 'math' importu da GERÇEKTE hiç çalışmıyordu (__import__ builtin'i sandbox'ta yoktu) -- şimdi çalışıyor")

    basarili3, sonuc3 = kodu_guvenle_calistir_serbest("import os\nsonuc = sorted(os.listdir('.'))[:1] if os.listdir('.') else []\n")
    _dogrula(basarili3, "import kısıtlaması kaldırıldı (kullanıcı talebiyle): daha önce reddedilen 'os' gibi modüller de artık serbestçe import edilebiliyor")

    basarisiz, hata = kodu_guvenle_calistir_serbest("sonuc = eval('1+1')\n")
    _dogrula(not basarisiz, "eval/exec/open çağrıları hâlâ reddediliyor (import serbestisi başka bir korumayı gevşetmedi)")


def test_17_yarisma_false_dogruluk_kontrolu() -> None:
    print("[test 17] YARISMA=False (deneme) modu: gonderim_uret._dogrulugu_kontrol_et gerçek cevapla doğru/yanlış ve gerçek-submit durumunu doğru tespit ediyor mu?...")

    import gonderim_uret

    task = Task(
        test_example=Example(input=np.array([[0, 0], [0, 0]]), output=np.array([[9, 9], [9, 9]])),
        train_examples=[],
        name="testgorev-degerlendirme",
    )

    dogru_sonuc = {
        "attempt_1": [[9, 9], [9, 9]], "attempt_1_gonderildi_mi": True,
        "attempt_2": [[0, 0], [0, 0]], "attempt_2_gonderildi_mi": False,
    }

    yakalanan = {}
    gercek_yaz = gonderim_uret.transkript_satiri_yaz
    gonderim_uret.transkript_satiri_yaz = lambda kayit: yakalanan.update(kayit)
    try:
        gonderim_uret._dogrulugu_kontrol_et(task, dogru_sonuc)
    finally:
        gonderim_uret.transkript_satiri_yaz = gercek_yaz

    _dogrula(yakalanan["icerik"]["attempt_1"]["dogru_mu"] is True, "attempt_1 (gerçek cevapla birebir aynı) DOĞRU olarak tespit edildi")
    _dogrula(yakalanan["icerik"]["attempt_1"]["gercekten_submit_edildi_mi"] is True, "attempt_1'in gerçekten submit_answer ile geldiği doğru tespit edildi")
    _dogrula(yakalanan["icerik"]["attempt_2"]["dogru_mu"] is False, "attempt_2 (yanlış/boş yer tutucu) YANLIŞ olarak tespit edildi")
    _dogrula(yakalanan["icerik"]["attempt_2"]["gercekten_submit_edildi_mi"] is False,
              "attempt_2'nin GERÇEKTEN submit edilmediği (boş yer tutucuya düştüğü) doğru tespit edildi -- tesadüfen doğru çıksa bile bu ayrım kaybolmaz")


def test_18_coklu_gpu_padisah_vezir_gercekten_paralel_mi() -> None:
    print("[test 18] coklu_gpu.padisah_vezir_havuzuyla_coz: padişah bir veziri BEKLEMEDEN diğerini başlatıyor mu, GERÇEK duvar-saati hızlanması var mı?...")

    import threading
    import time as _time

    from coklu_gpu import padisah_vezir_havuzuyla_coz

    ADIM_SURESI = 0.05
    baslama_zamanlari: List[float] = []
    kilit = threading.Lock()

    def _yavas_gorevi_coz(gpu_index: int, task: Task) -> Dict[str, Any]:
        with kilit:
            baslama_zamanlari.append(_time.time())
        _time.sleep(ADIM_SURESI)  # gerçek bir GPU işinin süresini taklit eder
        return {"attempt_1": [[gpu_index, gpu_index]], "attempt_1_gonderildi_mi": True}

    tasks = [
        Task(
            test_example=Example(input=np.array([[0, 0]]), output=np.array([[0, 0]])),
            train_examples=[], name=f"gorev{i}",
        )
        for i in range(8)
    ]

    baslangic = _time.time()
    sonuclar = padisah_vezir_havuzuyla_coz(4, tasks, _yavas_gorevi_coz)
    gecen = _time.time() - baslangic

    _dogrula(len(sonuclar) == 8, "8 görevin hepsi sonuçlandı")
    _dogrula(all(sonuclar[t.name]["attempt_1_gonderildi_mi"] for t in tasks), "hepsi gerçekten çözüldü (boş yer tutucuya düşen olmadı)")

    # 4 vezir, 8 gorev -> her vezir 2 gorev cozer (kuyruktan dinamik alarak).
    # SIRALI calisirsa 8*0.05=0.40 sn surer; GERCEKTEN paralel calisirsa
    # ~2*0.05=0.10 sn civari surer. Aradaki net fark, padisahin vezirleri
    # BIRBIRINI BEKLETMEDEN baslattigini VE isin kuyruktan dinamik
    # dagitildigini kanitlar.
    _dogrula(
        gecen < 0.30,
        f"8 görev GERÇEKTEN paralel çözüldü (duvar-saati: {gecen:.3f} sn, sıralı olsaydı ~{len(tasks) * ADIM_SURESI:.2f} sn sürerdi)",
    )

    # Padişahın vezir 2/3/4'ü, vezir 1'in İLK görevini bitirmesini
    # BEKLEMEDEN başlattığını kanıtla: ilk 4 dispatch (thread.start()
    # çağrıları) tek bir ADIM_SURESI içinde, art arda gerçekleşmiş olmalı.
    _dogrula(len(baslama_zamanlari) >= 4, "en az 4 görev işbaşı yaptı")
    ilk_dort = sorted(baslama_zamanlari)[:4]
    _dogrula(
        (ilk_dort[-1] - ilk_dort[0]) < ADIM_SURESI,
        "4 vezir de BİRBİRİNİN bitmesini beklemeden, hemen art arda işbaşı yaptı (padişah sıraya sokmadı)",
    )


class _SecenekliSahteOturum:
    """coz_yurutucu._esikli_uret()'i, gerçek RWKV/tokenizer'a hiç
    dokunmadan, oturum.uret() çağrı SAYISINI ve ARGÜMANLARINI doğrudan
    doğrulamak için taklit eder."""

    def __init__(self, senaryo: List[str]):
        self._senaryo = senaryo
        self.uret_cagrilari: List[int] = []
        self.metin_isle_cagrilari: List[str] = []

    def metin_isle(self, metin: str) -> None:
        self.metin_isle_cagrilari.append(metin)

    def uret(self, azami_yeni_token: int, **kwargs) -> str:
        self.uret_cagrilari.append(azami_yeni_token)
        return self._senaryo[len(self.uret_cagrilari) - 1]


def test_19_ikaz_esigi_yazma_hakki_tukenmek_uzere() -> None:
    print("[test 19] coz_yurutucu._esikli_uret: token bütçesi eşiğine ulaşılınca modele İKAZ enjekte ediliyor mu (ve gereksiz yere DEĞİL)?...")

    from coz_yurutucu import IKAZ_METNI, _esikli_uret

    # Durum A: butce esigi asilmiyor -> tek cagri, ikaz YOK.
    oturum_a = _SecenekliSahteOturum(["kisa cevap"])
    metin_a, ikaz_a = _esikli_uret(oturum_a, azami_yeni_token=100, uretim_ayarlari={}, ikaz_esigi=55000)
    _dogrula(oturum_a.uret_cagrilari == [100], "bütçe eşiğin altındaysa TEK çağrı yapıldı (bölünmedi)")
    _dogrula(not ikaz_a and not oturum_a.metin_isle_cagrilari, "bütçe eşiğin altındaysa İKAZ enjekte edilmedi")

    # Durum B: esik asiliyor, model ilk parcada HENUZ arac cagrisi
    # uretmemis (hala dusunuyor) -> ikaz enjekte edilmeli, ikinci parca
    # kalan token butcesiyle uretilmeli.
    oturum_b = _SecenekliSahteOturum(["hâlâ düşünüyorum, araç çağrısı yok", " ve sonunda submit_answer çağırdım"])
    metin_b, ikaz_b = _esikli_uret(oturum_b, azami_yeni_token=100, uretim_ayarlari={}, ikaz_esigi=60)
    _dogrula(oturum_b.uret_cagrilari == [60, 40], "eşik aşılınca üretim İKİYE bölündü (60 + kalan 40)")
    _dogrula(ikaz_b, "eşik aşılıp hâlâ araç çağrısı yokken İKAZ enjekte edildi")
    _dogrula(oturum_b.metin_isle_cagrilari and IKAZ_METNI in oturum_b.metin_isle_cagrilari[0],
              "modele GERÇEKTEN 'yazma hakkın tükenmek üzere' ikaz metni beslendi")
    _dogrula(metin_b == "hâlâ düşünüyorum, araç çağrısı yok ve sonunda submit_answer çağırdım",
              "iki parçanın metni doğru birleştirildi")

    # Durum C: esik asiliyor AMA model ilk parcada ZATEN gecerli bir
    # arac cagrisi uretmis -- ikinci parca (ve ikaz) GEREKSIZ yere
    # UretilMEMELI (token israfi olmamali).
    oturum_c = _SecenekliSahteOturum([
        '```json\n{"name": "submit_answer", "arguments": {"grid": [[1, 1], [1, 1]]}}\n```',
        "BU HİÇ ÇAĞRILMAMALI",
    ])
    metin_c, ikaz_c = _esikli_uret(oturum_c, azami_yeni_token=100, uretim_ayarlari={}, ikaz_esigi=60)
    _dogrula(oturum_c.uret_cagrilari == [60], "ilk parçada zaten geçerli bir araç çağrısı varsa İKİNCİ parça HİÇ üretilmedi (israf yok)")
    _dogrula(not ikaz_c, "cevap zaten bulunduysa İKAZ enjekte edilmedi")


def _sentetik_rwkv_x070_pth_olustur(yol: str, vocab: int = 16, n_layer: int = 2,
                                     n_head: int = 2, head_size: int = 4) -> None:
    """GERÇEK rwkv paketinin RWKV_x070.__init__'inin (site-packages/rwkv/model.py
    satır 245-281) beklediği TAM anahtar adları/şekilleriyle sentetik (rastgele
    ama biçim olarak gerçek) bir .pth ağırlık sözlüğü üretir -- ffn_dim ve
    LoRA ara boyutları (D_DECAY/D_AAA/D_MV/D_GATE) rastgele küçük değerler,
    sonuçların doğruluğu şekle bağlı değildir."""
    n_embd = n_head * head_size
    ffn_dim = 10
    d_decay, d_aaa, d_mv, d_gate = 6, 5, 5, 7
    g = torch.Generator().manual_seed(1234)

    def r(*shape):
        return torch.randn(*shape, generator=g) * 0.1

    z: Dict[str, torch.Tensor] = {
        "emb.weight": r(vocab, n_embd),
        "head.weight": r(vocab, n_embd),  # nn.Linear(out=vocab,in=n_embd) ham hali
        "ln_out.weight": torch.ones(n_embd),
        "ln_out.bias": torch.zeros(n_embd),
    }
    for i in range(n_layer):
        bbb, att, ffn = f"blocks.{i}.", f"blocks.{i}.att.", f"blocks.{i}.ffn."
        if i == 0:
            z[bbb + "ln0.weight"] = torch.ones(n_embd)
            z[bbb + "ln0.bias"] = torch.zeros(n_embd)
        z[bbb + "ln1.weight"] = torch.ones(n_embd)
        z[bbb + "ln1.bias"] = torch.zeros(n_embd)
        z[bbb + "ln2.weight"] = torch.ones(n_embd)
        z[bbb + "ln2.bias"] = torch.zeros(n_embd)

        z[att + "x_r"] = r(n_embd)
        z[att + "x_w"] = r(n_embd)
        z[att + "x_k"] = r(n_embd)
        z[att + "x_v"] = r(n_embd)
        z[att + "x_a"] = r(n_embd)
        z[att + "x_g"] = r(n_embd)
        z[att + "w0"] = r(n_embd)
        z[att + "w1"] = r(n_embd, d_decay)
        z[att + "w2"] = r(d_decay, n_embd)
        z[att + "a0"] = r(n_embd)
        z[att + "a1"] = r(n_embd, d_aaa)
        z[att + "a2"] = r(d_aaa, n_embd)
        z[att + "v0"] = r(n_embd)
        z[att + "v1"] = r(n_embd, d_mv)
        z[att + "v2"] = r(d_mv, n_embd)
        z[att + "g1"] = r(n_embd, d_gate)
        z[att + "g2"] = r(d_gate, n_embd)
        z[att + "k_k"] = r(n_embd)
        z[att + "k_a"] = r(n_embd)
        z[att + "r_k"] = r(n_head, head_size)
        z[att + "receptance.weight"] = r(n_embd, n_embd)  # nn.Linear ham hali (out,in)
        z[att + "key.weight"] = r(n_embd, n_embd)
        z[att + "value.weight"] = r(n_embd, n_embd)
        z[att + "output.weight"] = r(n_embd, n_embd)
        z[att + "ln_x.weight"] = torch.ones(n_embd)
        z[att + "ln_x.bias"] = torch.zeros(n_embd)

        z[ffn + "x_k"] = r(n_embd)
        z[ffn + "key.weight"] = r(ffn_dim, n_embd)    # nn.Linear(in=n_embd,out=ffn_dim) ham hali
        z[ffn + "value.weight"] = r(n_embd, ffn_dim)  # nn.Linear(in=ffn_dim,out=n_embd) ham hali

    torch.save(z, yol)


def test_20_rwkv_batch_gercek_rwkv_paketiyle_sayisal_dogrulama() -> None:
    print("[test 20] rwkv_batch.adim_toplu: GERÇEK kurulu `rwkv` paketinin RWKV_x070 sınıfıyla (forward_one, B=1 döngüsü referans alınarak) sayısal olarak eşleşiyor mu?...")

    import os
    import tempfile

    os.environ["RWKV_V7_ON"] = "1"
    os.environ.setdefault("RWKV_JIT_ON", "0")
    os.environ.setdefault("RWKV_CUDA_ON", "0")
    from rwkv.model import RWKV as GercekRWKV

    import rwkv_batch

    B, adim_sayisi, vocab = 3, 5, 16
    with tempfile.TemporaryDirectory() as tmp:
        model_kok = os.path.join(tmp, "sentetik_model")
        _sentetik_rwkv_x070_pth_olustur(model_kok + ".pth", vocab=vocab)

        gercek_model = GercekRWKV(model=model_kok, strategy="cpu fp32")

        rastgele = torch.Generator().manual_seed(99)
        token_dizileri = [
            [int(t) for t in torch.randint(0, vocab, (adim_sayisi,), generator=rastgele)]
            for _ in range(B)
        ]

        # Referans: GERÇEK pakedin kendi forward_one()'ı ile HER diziyi AYRI
        # AYRI, kendi bağımsız state'iyle, adım adım işleyip son adımın
        # logit'ini topluyoruz.
        referans_logitler = []
        for dizi in token_dizileri:
            durum = None
            logit = None
            for tok in dizi:
                logit, durum = gercek_model.forward([tok], durum)
            referans_logitler.append(logit)
        referans = torch.stack(referans_logitler, dim=0)

        # Toplu (batched): AYNI gerçek modelin .z sözlüğünü PAYLAŞARAK, B
        # diziyi TEK bir adim_toplu() çağrı zincirinde birlikte işliyoruz.
        durum_toplu = rwkv_batch.sifir_durum_toplu(
            gercek_model.z, gercek_model.n_layer, gercek_model.n_embd,
            gercek_model.n_head, gercek_model.head_size, B,
        )
        toplu_logit = None
        for adim in range(adim_sayisi):
            token_idler = [token_dizileri[b][adim] for b in range(B)]
            toplu_logit, durum_toplu = rwkv_batch.adim_toplu(
                gercek_model.z, gercek_model.n_layer, gercek_model.n_embd,
                gercek_model.n_head, gercek_model.head_size, token_idler, durum_toplu,
            )

        _dogrula(toplu_logit.shape == referans.shape,
                  f"toplu çıktı şekli referansla eşleşti: {tuple(toplu_logit.shape)}")
        fark = (toplu_logit - referans).abs().max().item()
        _dogrula(fark < 1e-4,
                  f"adim_toplu() B={B} bağımsız diziyi, GERÇEK rwkv paketinin forward_one() B kere ayrı çağrılmasıyla AYNI sonucu üretti (azami fark={fark:.2e})")

        # RWKVTopluDurumYoneticisi sarmalayıcısı da aynı sonucu vermeli ve
        # ağırlıkları KOPYALAMAMALI (aynı .z referansını paylaşmalı).
        yonetici = rwkv_batch.RWKVTopluDurumYoneticisi(gercek_model, B)
        # NOT: gercek_model bir torch.jit.ScriptModule (RWKV_JIT_ON=1 varsayılan
        # olsaydı) olduğunda .z özelliğine her erişim JIT tarafından yeni bir
        # sarmalayıcı nesne döndürebilir (kimlik/`is` karşılaştırması bu yüzden
        # güvenilir değildir); burada test RWKV_JIT_ON=0 ile çalıştığından `z`
        # düz bir dict'tir -- asıl garanti, aynı TENSÖR nesnelerinin (VRAM'in)
        # paylaşıldığıdır, bunu tek bir tensörün `is` kimliğiyle doğruluyoruz.
        ornek_anahtar = next(iter(gercek_model.z))
        _dogrula(yonetici.z[ornek_anahtar] is gercek_model.z[ornek_anahtar],
                  "RWKVTopluDurumYoneticisi ağırlık tensörlerini KOPYALAMADI, gerçek modelin tensörlerini doğrudan paylaştı")
        son_logit = None
        for adim in range(adim_sayisi):
            token_idler = [token_dizileri[b][adim] for b in range(B)]
            son_logit = yonetici.adim(token_idler)
        fark2 = (son_logit - referans).abs().max().item()
        _dogrula(fark2 < 1e-4,
                  f"RWKVTopluDurumYoneticisi sarmalayıcısı da referansla eşleşti (azami fark={fark2:.2e})")


def calistir() -> None:
    test_1_arac_cagrisi_ayiklama()
    test_2_cevap_verme_araci_boyut_tutarliligi()
    test_3_arac_cagrisini_yurutme_ve_hata_donen_akis()
    test_4_gercek_ttt_gradyan_adimlari()
    test_5_mcts_turbo_dfs_dallanma()
    test_6_kaide_kodu_yok_denetimi()
    test_7_uctan_uca_gorevi_coz()
    test_8_tamamlama_sadece_maskeleme()
    test_9_ne_olursa_olsun_kayit_garantisi()
    test_10_rwkv_state_tuning()
    test_11_rwkv_no_grad_backend_zarifce_devre_disi_birakir()
    test_12_rwkv_x070_z_sozlugu_gercek_kaggle_cokmesi()
    test_13_rwkv_prompt_isleme_token_basina_degil_tek_cagriyla()
    test_14_rwkv_oturum_turler_arasi_durum_tasir_yeniden_islemez()
    test_15_coz_yurutucu_artimli_yol_uctan_uca()
    test_16_execute_python_gercekten_numpy_calistirabiliyor_mu()
    test_17_yarisma_false_dogruluk_kontrolu()
    test_18_coklu_gpu_padisah_vezir_gercekten_paralel_mi()
    test_19_ikaz_esigi_yazma_hakki_tukenmek_uzere()
    test_20_rwkv_batch_gercek_rwkv_paketiyle_sayisal_dogrulama()

    if BASARISIZLIK_SAYACI["n"] == 0:
        print("\n[test] TÜMÜ BAŞARILI.")
    else:
        print(f"\n[test] {BASARISIZLIK_SAYACI['n']} DOĞRULAMA BAŞARISIZ.")
        sys.exit(1)


if __name__ == "__main__":
    calistir()
