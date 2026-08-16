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
from typing import Any, Dict, List, Optional, Tuple

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

    # GERÇEK Kaggle transkriptinde (kullanıcının paylaştığı) modelin ÇIPLAK
    # (```json fence'siz, <tool_call> etiketsiz) ürettiği TAM biçim -- eski
    # _CIPLAK_JSON_DESENI regex'i "\{[^{}]*...[^{}]*\}" idi ve İÇ İÇE süslü
    # parantez İÇEREMEZDİ; ama GERÇEK her araç çağrısının "arguments" alanı
    # da bir nesnedir, yani HER çıplak çağrı en az bir iç içe {} taşır --
    # eski regex bu yüzden ÇIPLAK hiçbir gerçek çağrıyı asla bulamıyordu.
    # Bu, kullanıcının transkriptinde "araç çağrısı bulunamadı" uyarısının
    # GERÇEK kök nedeniydi.
    metin_c = '{"name": "submit_answer", "arguments": {"grid": [[1, 1]]}}'
    cagrilar_c = arac_cagrilarini_ayikla(metin_c)
    _dogrula(len(cagrilar_c) == 1 and cagrilar_c[0]["name"] == "submit_answer",
              "ÇIPLAK (fence'siz) ve İÇ İÇE süslü parantez içeren GERÇEK biçimdeki bir araç çağrısı artık doğru ayıklanıyor")

    metin_d = 'Bazı açıklama metni {"amaçsız": "bir sözlük"} sonra gerçek çağrı: {"name": "execute_python", "arguments": {"code": "d = {1: 2, 3: 4}"}}'
    cagrilar_d = arac_cagrilarini_ayikla(metin_d)
    _dogrula(
        len(cagrilar_d) == 1 and cagrilar_d[0]["name"] == "execute_python" and cagrilar_d[0]["arguments"]["code"] == "d = {1: 2, 3: 4}",
        "metinde ARAÇLA ALAKASIZ bir süslü-parantez bloğu ve kodun İÇİNDE de iç içe süslü parantez olsa bile yalnızca GERÇEK ('name' anahtarlı) çağrı ayıklandı",
    )


def test_2_cevap_verme_araci_boyut_tutarliligi() -> None:
    print("[test 2] submit_answer: tutarsız satır/sütun sayısı REDDEDİLMELİ, kendimiz düzeltmemeliyiz...")

    defter = CevapDefteri()
    tutarsiz_grid = [[1, 2, 3], [4, 5], [6, 7, 8]]
    sonuc = submit_answer_arac(tutarsiz_grid, defter)

    _dogrula(sonuc["success"] is False, "tutarsız ızgara reddedildi")
    _dogrula(defter.kaydedilen_cevap is None, "reddedilen ızgara SESSİZCE düzeltilip kaydedilmedi")
    _dogrula("row 0: 3 columns" in sonuc["error"] and "row 1: 2 columns" in sonuc["error"],
              "hata mesajı hangi satırların kaç sütun olduğunu açıkça söylüyor (model'e İngilizce geri besleniyor)")
    print(f"    -> döndürülen hata: {sonuc['error']}")

    defter2 = CevapDefteri()
    tutarli_grid_farkli_boyut = [[9, 9, 9, 9, 9], [8, 8, 8, 8, 8]]
    sonuc2 = submit_answer_arac(tutarli_grid_farkli_boyut, defter2)
    _dogrula(sonuc2["success"] is True, "kendi içinde tutarlı fakat train örneklerinden FARKLI boyutlu ızgara kabul edildi (boyut değişebilir)")
    _dogrula(defter2.kaydedilen_cevap == tutarli_grid_farkli_boyut, "kaydedilen cevap AYNEN (yeniden boyutlandırılmadan) saklandı")


def test_3_arac_cagrisini_yurutme_ve_hata_donen_akis() -> None:
    print("[test 3] Ajan döngüsü: önce hatalı boyut dener, hatayı görür, sonra düzeltir...")

    defter = CevapDefteri()

    cagri_1 = {"name": "submit_answer", "arguments": {"grid": [[1, 1], [2]]}}
    sonuc_1 = arac_cagrisini_yurut(cagri_1, defter)
    _dogrula(not sonuc_1["success"], "1. deneme (tutarsız) reddedildi")
    _dogrula(defter.kaydedilen_cevap is None, "1. denemeden sonra kayıtlı cevap hâlâ yok")

    cagri_2 = {"name": "execute_python", "arguments": {"code": "sonuc = [x*2 for x in range(3)]"}}
    sonuc_2 = arac_cagrisini_yurut(cagri_2, defter)
    _dogrula(sonuc_2["success"] and sonuc_2["result"] == [0, 2, 4], "execute_python aracı gerçekten çalıştı ve doğru sonucu döndü")

    cagri_3 = {"name": "submit_answer", "arguments": {"grid": [[1, 1], [2, 2]]}}
    sonuc_3 = arac_cagrisini_yurut(cagri_3, defter)
    _dogrula(sonuc_3["success"], "2. deneme (tutarlı) kabul edildi")
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


def test_21_vram_tabanli_b_kesfi() -> None:
    print("[test 21] vram_izleyici.VramTabanliBKesifcisi: gerçek ölçümle azami-B tahmini doğru sıçrıyor mu, günlükler görev başına mı, OOM'a 1 B'lik payla mı tepki veriyor?...")

    from vram_izleyici import VramTabanliBKesifcisi, oom_korumali_calistir

    # --- Senaryo A: iki farklı B'de ölçüm alınınca marjinal maliyet
    # DOĞRU hesaplanıp azami B'ye DOĞRUDAN sıçranmalı (129,130 diye
    # sürünmeden) -- burada GERÇEK CUDA yok, bu yüzden bellek_olcer
    # enjekte edilerek "toplam 21 GB, ağırlık 14.6 GB, B başına 39 MB"
    # senaryosu SAYISAL olarak taklit ediliyor.
    TOPLAM_BAYT = 21 * 1024 ** 3
    AGIRLIK_BAYT = int(14.6 * 1024 ** 3)
    B_BASINA_BAYT = 39 * 1024 ** 2

    def _bellek_olcer_taklit(cihaz: str) -> Tuple[int, int]:
        b = kayitli_b["deger"]
        return AGIRLIK_BAYT + b * B_BASINA_BAYT, TOPLAM_BAYT

    kayitli_b = {"deger": 128}
    loglar: List[str] = []
    kesifci = VramTabanliBKesifcisi(
        "cuda:0", baslangic_b=128,
        bellek_olcer=_bellek_olcer_taklit, bellek_sifirla=lambda cihaz: None,
        log_yaz=loglar.append,
    )

    yeni_b = kesifci.gorev_sonrasi_olc_ve_ayarla()
    _dogrula(kesifci.azami_guvenli_b is None, "TEK ölçümle henüz azami B kesinleşmedi (marjinal maliyet bilinmiyor)")
    _dogrula(yeni_b == 129, "marjinal maliyet bilinmezken bir sonraki deneme İHTİYATLA yalnızca +1 arttı (129)")
    _dogrula(len(loglar) == 1, "her görev sonrası TAM OLARAK bir özet log basıldı (ne spam ne sessizlik)")

    kayitli_b["deger"] = 129
    yeni_b = kesifci.gorev_sonrasi_olc_ve_ayarla()
    # Artık iki farklı B ölçümü var -> gerçek marjinal maliyet (39MB/B)
    # hesaplanıp DOĞRUDAN tavana sıçranmalı.
    beklenen_ust_sinir = int(TOPLAM_BAYT * 0.93)
    beklenen_azami = 129 + int((beklenen_ust_sinir - (AGIRLIK_BAYT + 129 * B_BASINA_BAYT)) // B_BASINA_BAYT)
    _dogrula(kesifci.azami_guvenli_b == beklenen_azami,
              f"iki ölçümden GERÇEK marjinal maliyet (39MB/B) çıkarılıp azami B'ye DOĞRUDAN sıçrandı (beklenen={beklenen_azami}, bulunan={kesifci.azami_guvenli_b})")
    _dogrula(kesifci.calisan_b() == kesifci.azami_guvenli_b - 1,
              "çalışan B, azami güvenli B'den TAM OLARAK 1 eksik (kullanıcının istediği tek birimlik pay, fazlası değil)")
    _dogrula(len(loglar) == 3, "tahmin DEĞİŞTİĞİ için özet logun HEMEN ardından ayrı bir 'tavan güncellendi' logu da basıldı (2+1=3)")
    _dogrula("AZAMİ GÜVENLİ B TAHMİNİ GÜNCELLENDİ" in loglar[2], "tavan değişim logu belirgin biçimde işaretlendi")

    # --- Senaryo B: gerçek bir OOM yakalanınca azami B KESİN olarak
    # OOM'a düşen B - 1'e sabitlenmeli (artık tahmin değil).
    def _her_zaman_oom(b: int) -> str:
        raise __import__("torch").OutOfMemoryError("sahte OOM")

    loglar2: List[str] = []
    kesifci2 = VramTabanliBKesifcisi(
        "cuda:1", baslangic_b=200,
        bellek_olcer=lambda cihaz: (0, TOPLAM_BAYT), bellek_sifirla=lambda cihaz: None,
        log_yaz=loglar2.append,
    )
    kesifci2.azami_guvenli_b = 200  # önceden "sanılan" tavan
    try:
        oom_korumali_calistir(kesifci2, _her_zaman_oom)
        _dogrula(False, "OOM her defasında tekrarlanıyorsa sonunda pes edilip hata yükseltilmeliydi")
    except Exception:
        pass
    _dogrula(kesifci2.azami_guvenli_b < 200,
              "OOM sonrası azami güvenli B kesinlikle DÜŞÜRÜLDÜ (artık iyimser tahmin değil)")
    _dogrula(any("KESİN" in s for s in loglar2), "OOM'un HEMEN ardından, gecikmeden bir 'kesin sınır' logu basıldı")

    # --- Senaryo C: OOM YOKSA oom_korumali_calistir çağrıyı doğru B ile
    # yapar ve sonucu döndürür.
    kesifci3 = VramTabanliBKesifcisi(
        "cuda:2", baslangic_b=64,
        bellek_olcer=lambda cihaz: (1, TOPLAM_BAYT), bellek_sifirla=lambda cihaz: None,
        log_yaz=lambda s: None,
    )
    kullanilan_b_larla: List[int] = []

    def _basarili(b: int) -> str:
        kullanilan_b_larla.append(b)
        return "tamam"

    sonuc = oom_korumali_calistir(kesifci3, _basarili)
    _dogrula(sonuc == "tamam" and kullanilan_b_larla == [64], "OOM yoksa iş TEK seferde, kesifci'nin o anki çalışan B'siyle çalıştırıldı")


def test_22_coklu_gpu_loglarinda_hangi_gpu_oldugu_ayirt_edilebiliyor_mu() -> None:
    print("[test 22] coz_yurutucu/_tek_deneme_uret_artimli: kullanıcının gerçek Kaggle logunda fark ettiği gibi, konsol çıktısında HANGİ GPU'nun/vezirin çalıştığı hiç görünmüyordu (deneme_etiketi yalnızca transkript dosyasına yazılıyor, stdout'ta kayboluyordu) -- artık her satırda görünüyor mu?...")

    import io
    from contextlib import redirect_stdout

    import coz_yurutucu
    from rwkv_native import RWKVUyumluModel

    task = Task(
        test_example=Example(input=np.array([[0, 0], [0, 0]]), output=np.array([[0, 0], [0, 0]])),
        train_examples=[Example(input=np.array([[1, 2], [3, 4]]), output=np.array([[4, 3], [2, 1]]))],
        name="testgorev-etiket",
    )
    native = _SahteNativeRWKV()
    model = RWKVUyumluModel(native, "cpu fp32")
    tok = _KarakterTabanliRWKVTokenizer()

    class _SahteOturum:
        def __init__(self, model, tokenizer):
            pass

        def metin_isle(self, metin: str) -> None:
            pass

        def uret(self, azami_yeni_token, **kwargs) -> str:
            return '```json\n{"name": "submit_answer", "arguments": {"grid": [[1, 1]]}}\n```'

    import rwkv_oturum
    gercek_sinif = rwkv_oturum.RWKVSohbetOturumu
    rwkv_oturum.RWKVSohbetOturumu = _SahteOturum
    yakalanan = io.StringIO()
    try:
        with redirect_stdout(yakalanan):
            coz_yurutucu._tek_deneme_uret_artimli(model, tok, "rwkv", task, azami_tur=1, azami_yeni_token=50, deneme_etiketi="gpu2")
    finally:
        rwkv_oturum.RWKVSohbetOturumu = gercek_sinif

    cikti = yakalanan.getvalue()
    _dogrula("(gpu2)" in cikti, "coz_yurutucu'nun 'tur başlıyor' ve 'model çıktısı' logları artık HANGİ vezir/GPU olduğunu (deneme_etiketi='gpu2') açıkça gösteriyor")
    _dogrula(cikti.count("(gpu2)") >= 2, "etiket TEK bir satırda değil, o görevin İLGİLİ TÜM konsol satırlarında tekrarlanıyor (karışıklık olmasın diye)")


def test_23_gpu_tespit_derinlemesine_ve_gorunmeyen_indeksler_dogru_etiketleniyor() -> None:
    print("[test 23] gpu_tespit.kullanilabilir_gpu_indeksleri + coklu_gpu: 'görünüyor ama kullanılamıyor' GPU'lar elenip GERÇEK (olası ARALIKLI) indekslerle doğru etiketleniyor mu?...")

    import gpu_tespit

    # --- Senaryo A: CUDA hiç görünmüyorsa hiçbir alt süreç başlatılmadan
    # (yavaş/gereksiz olmadan) hemen boş liste dönmeli.
    class _SahteCuda:
        @staticmethod
        def is_available() -> bool:
            return False

    gercek_torch = __import__("torch")
    eski_cuda = gercek_torch.cuda
    gercek_torch.cuda = _SahteCuda
    try:
        sonuc = gpu_tespit.kullanilabilir_gpu_indeksleri()
    finally:
        gercek_torch.cuda = eski_cuda
    _dogrula(sonuc == [], "CUDA görünmüyorsa hiç alt süreç başlatılmadan boş liste döndü")

    # --- Senaryo B: coklu_gpu.dort_kopya_yukle, derin sınamadan HİÇBİR
    # GPU geçemezse (torch GPU görse bile) AÇIKÇA hata vermeli, sessizce
    # 0 GPU'ya düşmemeli.
    import coklu_gpu

    eski_kullanilabilir = gpu_tespit.kullanilabilir_gpu_indeksleri
    gpu_tespit.kullanilabilir_gpu_indeksleri = lambda azami_gpu=None, zaman_asimi_sn=45.0: []
    try:
        hata_alindi = False
        try:
            coklu_gpu.dort_kopya_yukle()
        except RuntimeError:
            hata_alindi = True
        _dogrula(hata_alindi, "derin sınamadan geçen hiç GPU yoksa dort_kopya_yukle AÇIKÇA RuntimeError verdi (sessizce yutmadı)")
    finally:
        gpu_tespit.kullanilabilir_gpu_indeksleri = eski_kullanilabilir

    # --- Senaryo C: derin sınamadan GEÇEN GPU'lar ARALIKLI olabilir (ör.
    # yalnızca cuda:0 ve cuda:2 çalışıyor, cuda:1/cuda:3 elendi). Bu
    # durumda modeller listesi 2 elemanlı olsa da (konum 0,1) GERÇEK
    # etiketler ["cuda:0","cuda:2"] olmalı -- ESKİ kodda konum==cuda
    # numarası varsayılıp "cuda:1" gibi YANLIŞ bir etiket basılırdı.
    import rwkv_native
    import ttt_lora

    gpu_tespit.kullanilabilir_gpu_indeksleri = lambda azami_gpu=None, zaman_asimi_sn=45.0: [0, 2]

    yuklenen_cihazlar: List[str] = []

    class _SahteYuklenmisModel:
        def __init__(self, cihaz: str):
            self.device = cihaz

    def _sahte_native_rwkv_yukle(yol, veri_tipi=None, cihaz=None):
        yuklenen_cihazlar.append(cihaz)
        return _SahteYuklenmisModel(cihaz)

    eski_native_yukle = rwkv_native.native_rwkv_yukle
    eski_rwkv_ham_pth_mi = rwkv_native.rwkv_ham_pth_mi
    eski_tokenizer_yukle = ttt_lora.tokenizer_yukle
    eski_yerel_model_yolu = ttt_lora.yerel_model_yolu
    rwkv_native.native_rwkv_yukle = _sahte_native_rwkv_yukle
    rwkv_native.rwkv_ham_pth_mi = lambda yol: True
    ttt_lora.tokenizer_yukle = lambda model_ailesi: "sahte-tokenizer"
    ttt_lora.yerel_model_yolu = lambda model_ailesi: "/sahte/yol/model.pth"
    try:
        modeller, tokenizer, gpu_etiketleri = coklu_gpu.dort_kopya_yukle()
    finally:
        rwkv_native.native_rwkv_yukle = eski_native_yukle
        rwkv_native.rwkv_ham_pth_mi = eski_rwkv_ham_pth_mi
        ttt_lora.tokenizer_yukle = eski_tokenizer_yukle
        ttt_lora.yerel_model_yolu = eski_yerel_model_yolu
        gpu_tespit.kullanilabilir_gpu_indeksleri = eski_kullanilabilir

    _dogrula(yuklenen_cihazlar == ["cuda:0", "cuda:2"], "yalnızca derin sınamadan GEÇEN (aralıklı) cuda:0 ve cuda:2'ye model yüklendi, cuda:1/3'e HİÇ dokunulmadı")
    _dogrula(gpu_etiketleri == ["cuda:0", "cuda:2"], "dönen etiketler GERÇEK cuda numaralarını taşıyor (konumsal 0,1 DEĞİL)")

    # --- Senaryo D: padisah_vezir_havuzuyla_coz, bu ARALIKLI etiketleri
    # LOGLARDA da doğru yansıtmalı (konumsal indeksle değil).
    import io
    from contextlib import redirect_stdout

    def _hizli_coz(gpu_index: int, task: Task) -> Dict[str, Any]:
        return {"attempt_1": [[1, 1]], "attempt_1_gonderildi_mi": True}

    tasks = [Task(test_example=Example(input=np.array([[0]]), output=np.array([[0]])), train_examples=[], name="g0")]
    yakalanan = io.StringIO()
    with redirect_stdout(yakalanan):
        coklu_gpu.padisah_vezir_havuzuyla_coz(2, tasks, _hizli_coz, etiketler=["cuda:0", "cuda:2"])
    cikti = yakalanan.getvalue()
    _dogrula("(cuda:2)" in cikti or "(cuda:0)" in cikti, "loglarda GERÇEK cuda etiketi (cuda:0/cuda:2) göründü")
    _dogrula("(cuda:1)" not in cikti, "asla var olmayan/elenmiş 'cuda:1' etiketiyle YANLIŞ bir log basılmadı")


def test_24_onisle_toplu_farkli_uzunluk_gercek_rwkv_ile_ragged_batch_dogrulamasi() -> None:
    print("[test 24] rwkv_batch.onisle_toplu_farkli_uzunluk: test_20 yalnızca EŞİT uzunluktaki diziler denemişti -- GERÇEKTEN FARKLI uzunluktaki (ragged) B prompt, GERÇEK rwkv paketiyle hâlâ birebir eşleşiyor mu?...")

    import os
    import tempfile

    os.environ["RWKV_V7_ON"] = "1"
    os.environ.setdefault("RWKV_JIT_ON", "0")
    os.environ.setdefault("RWKV_CUDA_ON", "0")
    from rwkv.model import RWKV as GercekRWKV

    import rwkv_batch

    vocab = 16
    with tempfile.TemporaryDirectory() as tmp:
        model_kok = os.path.join(tmp, "sentetik_model_ragged")
        _sentetik_rwkv_x070_pth_olustur(model_kok + ".pth", vocab=vocab)
        gercek_model = GercekRWKV(model=model_kok, strategy="cpu fp32")

        # KASITLI OLARAK farklı uzunlukta 3 "prompt" -- gerçek üretimde B
        # farklı ARC bulmacasının farklı uzunluktaki metinlerine karşılık
        # gelir (test_20'de HEPSİ aynı sabit uzunluktaydı, bu boşluğu kapatır).
        rastgele = torch.Generator().manual_seed(7)
        token_dizileri = [
            [int(t) for t in torch.randint(0, vocab, (n,), generator=rastgele)]
            for n in (3, 9, 5)
        ]
        _dogrula(len({len(t) for t in token_dizileri}) == 3, "sınama dizileri GERÇEKTEN 3 farklı uzunlukta (3,5,9) -- eşit uzunluk kaçamağı yok")

        referans_logitler = []
        for dizi in token_dizileri:
            durum = None
            logit = None
            for tok in dizi:
                logit, durum = gercek_model.forward([tok], durum)
            referans_logitler.append(logit)
        referans = torch.stack(referans_logitler, dim=0)

        toplu_logit, _durum = rwkv_batch.onisle_toplu_farkli_uzunluk(
            gercek_model.z, gercek_model.n_layer, gercek_model.n_embd,
            gercek_model.n_head, gercek_model.head_size, token_dizileri,
        )

        fark = (toplu_logit - referans).abs().max().item()
        _dogrula(fark < 1e-4,
                  f"FARKLI uzunluktaki (ragged) 3 prompt TEK batched prefill'de, kısa promptlar kendi sonlarında DONDURULARAK, GERÇEK forward_one() referansıyla birebir eşleşti (azami fark={fark:.2e})")


def test_25_toplu_gorevleri_coz_gercekten_farkli_sorulara_ayni_anda_bakiyor_mu() -> None:
    print("[test 25] coz_yurutucu_toplu.toplu_gorevleri_coz: B GERÇEKTEN FARKLI görev, AYNI promptun kopyası DEĞİL -- tek batched adım zincirinde EŞZAMANLI, HER BİRİ KENDİ DOĞRU cevabını mı üretiyor?...")

    import json as _json

    import coz_yurutucu_toplu as cyt

    class _TamTersinirTokenizer:
        pad_token_id = 0
        eos_token_id = 0

        def encode(self, metin: str, add_special_tokens: bool = True) -> List[int]:
            return [ord(c) for c in metin]

        def decode(self, token_idler: Any, skip_special_tokens: bool = True) -> str:
            if hasattr(token_idler, "tolist"):
                token_idler = token_idler.tolist()
            return "".join(chr(int(t)) for t in token_idler)

    tok = _TamTersinirTokenizer()

    # 3 GERÇEKTEN FARKLI görev -- farklı train/test ızgaraları, dolayısıyla
    # farklı prompt metinleri (aynı promptun 3 kopyası DEĞİL).
    tasks = [
        Task(test_example=Example(input=np.array([[1]]), output=np.array([[1]])),
             train_examples=[Example(input=np.array([[1, 2]]), output=np.array([[2, 1]]))], name="gorevA"),
        Task(test_example=Example(input=np.array([[3, 3], [3, 3]]), output=np.array([[3, 3], [3, 3]])),
             train_examples=[Example(input=np.array([[5]]), output=np.array([[6]]))], name="gorevB"),
        Task(test_example=Example(input=np.array([[9, 0, 9]]), output=np.array([[0, 9, 0]])),
             train_examples=[Example(input=np.array([[7, 7, 7]]), output=np.array([[8, 8, 8]]))], name="gorevC"),
    ]

    # Her göreve, BİRBİRİNDEN AYIRT EDİLEBİLİR, FARKLI bir doğru cevap
    # "senaryolandırılıyor" -- sonuçta HANGİ görevin HANGİ cevabı ürettiği
    # karışmışsa (ör. hepsi aynı/yanlış göreve yazılmışsa) test yakalar.
    beklenen_cevaplar = {
        "gorevA": [[1, 1]],
        "gorevB": [[2, 2], [2, 2]],
        "gorevC": [[3, 3, 3, 3]],
    }
    metinler = {
        ad: '{"name": "submit_answer", "arguments": {"grid": %s}}' % _json.dumps(beklenen_cevaplar[ad])
        for ad in beklenen_cevaplar
    }
    scripted = [[ord(c) for c in metinler[t.name]] for t in tasks]
    uzunluklar = {len(s) for s in scripted}
    _dogrula(len(uzunluklar) >= 2, "senaryolandırılan 3 cevap GERÇEKTEN farklı uzunlukta (kısa biten görev, uzun süren görevi HİÇ beklemeden bitmeli)")

    VOCAB = 256
    kayit = {"onisle_token_dizileri": None, "adim_sayisi": 0}

    def _mock_onisle(z, n_layer, n_embd, n_head, head_size, token_dizileri, ilerleme_geri_cagirma=None, ilerleme_adimi=200):
        kayit["onisle_token_dizileri"] = token_dizileri
        B = len(token_dizileri)
        logits = torch.full((B, VOCAB), -10.0)
        for b in range(B):
            logits[b, scripted[b][0]] = 10.0
        return logits, ["durum-baslangic"] * 1

    def _mock_adim(z, n_layer, n_embd, n_head, head_size, token_idler, durum, aktif_maske):
        kayit["adim_sayisi"] += 1
        pozisyon = kayit["adim_sayisi"]
        B = len(token_idler)
        logits = torch.full((B, VOCAB), -10.0)
        for b in range(B):
            if not aktif_maske[b]:
                continue
            if pozisyon < len(scripted[b]):
                logits[b, scripted[b][pozisyon]] = 10.0
            else:
                logits[b, ord(' ')] = 10.0
        return logits, durum

    eski_onisle = cyt.onisle_toplu_farkli_uzunluk
    eski_adim = cyt.adim_toplu_maskeli
    eski_ayarlar = cyt.uretim_ayarlarini_al
    cyt.onisle_toplu_farkli_uzunluk = _mock_onisle
    cyt.adim_toplu_maskeli = _mock_adim
    cyt.uretim_ayarlarini_al = lambda model_ailesi, tokenizer: {"do_sample": False, "pad_token_id": 0}

    class _SahteHamModel:
        z: Dict[str, Any] = {}
        n_layer = n_embd = n_head = head_size = 1

    try:
        sonuc = cyt.toplu_gorevleri_coz(_SahteHamModel(), tok, tasks, azami_yeni_token=500, kontrol_araligi=1, deneme_etiketi="test-toplu")
    finally:
        cyt.onisle_toplu_farkli_uzunluk = eski_onisle
        cyt.adim_toplu_maskeli = eski_adim
        cyt.uretim_ayarlarini_al = eski_ayarlar

    onisle_dizileri = kayit["onisle_token_dizileri"]
    _dogrula(onisle_dizileri is not None and len(onisle_dizileri) == 3, "toplu_gorevleri_coz, 3 görevi TEK bir batched prefill çağrısına (B=3) gönderdi")
    _dogrula(len({tuple(t) for t in onisle_dizileri}) == 3, "prefill'e giden 3 prompt GERÇEKTEN BİRBİRİNDEN FARKLI (aynı promptun 3 kopyası DEĞİL -- her görev kendi soru metnini taşıyor)")

    for task in tasks:
        _dogrula(sonuc[task.name]["attempt_1_gonderildi_mi"] is True, f"{task.name}: gerçekten submit_answer ile sonuçlandı")
        _dogrula(sonuc[task.name]["attempt_1"] == beklenen_cevaplar[task.name],
                  f"{task.name}: TEK batched çalıştırmada KENDİ doğru cevabını üretti ({sonuc[task.name]['attempt_1']}) -- başka görevin cevabıyla KARIŞMADI")

    en_uzun = max(len(s) for s in scripted)
    toplam_seri_olsaydi = sum(len(s) for s in scripted)
    _dogrula(
        kayit["adim_sayisi"] < toplam_seri_olsaydi and kayit["adim_sayisi"] <= en_uzun + 1,
        f"toplam batched adım sayısı ({kayit['adim_sayisi']}) EN UZUN görevin uzunluğuna ({en_uzun}) yakın, "
        f"3 görevi SIRAYLA çözseydik gereken toplam adıma ({toplam_seri_olsaydi}) DEĞİL -- kısa biten görev UZUN "
        f"olanı HİÇ beklemeden bitti, ikisi de AYNI batched adım zincirinde EŞZAMANLI ilerledi",
    )


def test_26_padisah_vezir_toplu_ise_baslamadan_once_esit_pay_veriyor_mu() -> None:
    print("[test 26] coklu_gpu.padisah_vezir_toplu_havuzuyla_coz: paylaşımlı TEK kuyruk yerine, işe başlamadan ÖNCE görevler eşit paylaştırılıp her vezir SADECE kendi payını mı çekiyor (hızlı bir vezirin kuyruğu tek başına yutup diğerlerini aç bırakması engelleniyor mu)?...")

    import threading

    import coklu_gpu

    # Kullanıcının somut senaryosu: 240 görev, 4 GPU, B çoğu görevden
    # BÜYÜK -- eski (paylaşımlı tek kuyruk) tasarımda 2 hızlı vezir
    # kuyruğun TAMAMINI kapıp diğer 2'sü HİÇ iş alamazdı.
    tasks = [
        Task(test_example=Example(input=np.array([[0]]), output=np.array([[0]])), train_examples=[], name=f"gorev{i}")
        for i in range(10)
    ]

    isleyen_partiler: List[Any] = []
    kilit = threading.Lock()

    def _gorevleri_coz_toplu(gpu_index: int, parti: List[Task]) -> Dict[str, Any]:
        with kilit:
            isleyen_partiler.append((gpu_index, [t.name for t in parti]))
        return {t.name: {"attempt_1": [[gpu_index]], "attempt_1_gonderildi_mi": True} for t in parti}

    # 4 vezirin HEPSİNE, gerçekte olduğu gibi, KENDİ payından çok daha
    # BÜYÜK bir B (100) veriliyor -- eğer hâlâ paylaşımlı TEK kuyruk
    # kullanılıyor olsaydı, gpu_index=0 (ilk başlayan) TÜM 10 görevi TEK
    # partide kapardı ve diğer vezirler HİÇ iş alamazdı.
    sonuclar = coklu_gpu.padisah_vezir_toplu_havuzuyla_coz(
        4, tasks, _gorevleri_coz_toplu, b_boyutu_al=lambda gpu_index: 100,
    )

    _dogrula(len(sonuclar) == 10, "10 görevin hepsi sonuçlandı")

    gpu_basina_gorev_sayisi: Dict[int, int] = {}
    for gpu_index, isimler in isleyen_partiler:
        gpu_basina_gorev_sayisi[gpu_index] = gpu_basina_gorev_sayisi.get(gpu_index, 0) + len(isimler)

    _dogrula(len(gpu_basina_gorev_sayisi) == 4, f"4 vezirin HEPSİ en az bir görev işledi (gördüğü GPU'lar: {sorted(gpu_basina_gorev_sayisi)}) -- hiçbiri aç bırakılmadı")
    sayilar = sorted(gpu_basina_gorev_sayisi.values())
    _dogrula(sayilar[-1] - sayilar[0] <= 1, f"10 görev 4 vezire MÜMKÜN OLDUĞUNCA EŞİT (fark ≤1) paylaştırıldı: {gpu_basina_gorev_sayisi}")

    # Her vezir yalnızca TEK bir partide (kendi payı B=100'den küçük
    # olduğu için) çalışmış olmalı -- başka vezirin payına asla dokunmadı.
    for gpu_index in range(4):
        bu_gpu_partileri = [isimler for g, isimler in isleyen_partiler if g == gpu_index]
        _dogrula(len(bu_gpu_partileri) == 1, f"gpu{gpu_index}: payı B'den küçük olduğu için TEK partide (kendi payının tamamı) çekildi, başka vezirin payına asla el atmadı")


def test_27_modele_geri_beslenen_arac_yanitlari_ingilizce_mi() -> None:
    print("[test 27] araclar.py: submit_answer/execute_python hata mesajları -- modele DOĞRUDAN geri beslenen (Türkçe eğitim verisi görmemiş modelin ANLAYAMAYACAĞI) hiçbir Türkçe karakter/kelime kalmamış mı?...")

    import json
    import re as _re

    from araclar import CevapDefteri, arac_cagrisini_yurut

    _TURKCE_HARF_DESENI = _re.compile(r"[çğıöşüÇĞİÖŞÜ]")

    defter = CevapDefteri()
    senaryolar = [
        {"name": "submit_answer", "arguments": {"grid": "gecersiz"}},
        {"name": "submit_answer", "arguments": {"grid": [[1, 2, 3], [4, 5]]}},
        {"name": "submit_answer", "arguments": {"grid": [[1, "x"]]}},
        {"name": "submit_answer", "arguments": {"grid": [[1, 2]]}},
        {"name": "execute_python", "arguments": {"code": "import os"}},
        {"name": "boyle_bir_arac_yok", "arguments": {}},
    ]
    for cagri in senaryolar:
        sonuc = arac_cagrisini_yurut(cagri, defter)
        metin = json.dumps(sonuc, ensure_ascii=False)
        _dogrula(not _TURKCE_HARF_DESENI.search(metin),
                  f"{cagri['name']} çağrısının modele geri beslenen tool_response'unda Türkçe karakter YOK: {metin!r}")


def test_28_uret_devam_yozlasmis_donguyu_erken_yakaliyor_mu() -> None:
    print("[test 28] rwkv_native.uret_devam: kullanıcının gerçek transkriptinde görülen 'aynı bloğu onlarca kez tekrarlama' döngüsü, TÜM bütçe tüketilmeden ERKEN yakalanıp durduruluyor mu?...")

    from rwkv_native import RWKVUyumluModel, _tekrara_kilitlenme_periyodu

    _dogrula(_tekrara_kilitlenme_periyodu(list(range(30))) is None, "gerçekten TEKRARSIZ (hep artan) bir dizi yozlaşmış döngü SANILMADI")
    tekrarli = ([1, 2, 3, 4, 5] * 3)
    _dogrula(_tekrara_kilitlenme_periyodu(tekrarli) == 5, "5 uzunluğunda bir bloğun 3 kez ardışık tekrarı doğru periyotla (5) tespit edildi")

    class _SonsuzTekrarEdenRWKV:
        """Gerçek transkriptteki gibi: bir noktadan sonra hep AYNI 20
        token'lık bloğu sonsuza dek tekrarlayan yozlaşmış bir model taklidi."""

        def __init__(self, vocab: int = 64, d: int = 4, blok_uzunlugu: int = 20):
            self.vocab = vocab
            self.d = d
            self.blok = list(range(1, blok_uzunlugu + 1))
            self.emb = torch.nn.Parameter(torch.randn(vocab, d))
            self.head = torch.nn.Parameter(torch.randn(d, vocab))
            self.w = {"emb.weight": self.emb, "head.weight": self.head}
            self._sayac = 0

        def forward(self, tokens, state, full_output=False):
            # HANGİ token verilirse verilsin, tekrarlayan bloktaki bir
            # sonraki token'ı KESİN seçtirecek tek-sıcak (one-hot) bir
            # logit üretir -- gerçek modelin döngüye KİLİTLENMESİNİN
            # matematiksel eşdeğeri.
            sonraki = self.blok[self._sayac % len(self.blok)]
            self._sayac += 1
            logit = torch.full((self.vocab,), -10.0)
            logit[sonraki] = 10.0
            return logit, (state or [torch.zeros(self.d)])

    native = _SonsuzTekrarEdenRWKV()
    model = RWKVUyumluModel(native, "cpu fp32")
    son_logits = torch.full((native.vocab,), -10.0)
    son_logits[native.blok[0]] = 10.0

    uretilenler, _son_logits, _durum = model.uret_devam(
        son_logits, None, max_new_tokens=50000, do_sample=False,
    )
    _dogrula(len(uretilenler) < 50000,
              f"YOZLAŞMIŞ DÖNGÜ erken yakalanıp üretim durduruldu ({len(uretilenler)} token üretildi, 50000 TOKENLİK BÜTÇENİN TAMAMI BOŞA HARCANMADI)")
    _dogrula(len(uretilenler) < 2000,
              f"tespit MAKUL bir sürede (birkaç kontrol adımı içinde) gerçekleşti, geç kalmadı ({len(uretilenler)} token)")


def test_29_tekrar_cezasi_gercekten_ayni_tokene_saplanmayi_zorlastiriyor_mu() -> None:
    print("[test 29] rwkv_native._tekrar_cezasi_uygula + uret_devam(repetition_penalty=...): greedy (do_sample=False) kararda, daha önce üretilmiş bir token'ın olasılığı GERÇEKTEN düşüyor mu -- kullanıcının istediği 'modele tekrar cezası' bu mu?...")

    from rwkv_native import RWKVUyumluModel, _tekrar_cezasi_uygula

    # --- Birim test: pozitif logit cezaya BÖLÜNÜR, negatif logit cezaYLA
    # ÇARPILIR (işaret korunur, büyüklük küçülür) -- HF'nin standart
    # repetition_penalty tanımıyla AYNI.
    logits = torch.tensor([4.0, -4.0, 1.0, 0.0])
    cezali = _tekrar_cezasi_uygula(logits, gecmis_tokenler=[0, 1], ceza=2.0)
    _dogrula(abs(cezali[0].item() - 2.0) < 1e-6, "pozitif logit (4.0) cezaya BÖLÜNDÜ (2.0)")
    _dogrula(abs(cezali[1].item() - (-8.0)) < 1e-6, "negatif logit (-4.0) cezaYLA ÇARPILDI (-8.0, işaret korundu)")
    _dogrula(cezali[2].item() == 1.0 and cezali[3].item() == 0.0, "hiç geçmemiş tokenler (2,3) DOKUNULMADAN kaldı")
    _dogrula(_tekrar_cezasi_uygula(logits, [], 2.0) is logits, "geçmiş boşsa ceza uygulanmadan AYNI tensör döndü (gereksiz kopya yok)")
    _dogrula(_tekrar_cezasi_uygula(logits, [0], 1.0) is logits, "ceza<=1.0 iken no-op (geriye dönük uyumluluk, varsayılan davranış bozulmadı)")

    # --- Uçtan uca: kasıtlı olarak "tek bir token'a saplanmaya EĞİLİMLİ"
    # (o tokenin logiti hep en yüksek) sahte bir model, CEZASIZ iken hep
    # AYNI tokeni seçer (yozlaşmış döngünün ta kendisi); ceza AÇILINCA
    # birden fazla FARKLI token arasında geçiş yapmaya BAŞLAMALI.
    class _TekTokene_Saplanan_RWKV:
        def __init__(self, vocab: int = 8, d: int = 4):
            self.vocab, self.d = vocab, d
            self.emb = torch.nn.Parameter(torch.randn(vocab, d))
            self.head = torch.nn.Parameter(torch.randn(d, vocab))
            self.w = {"emb.weight": self.emb, "head.weight": self.head}

        def forward(self, tokens, state, full_output=False):
            # Token 3'ün logiti HER ZAMAN en yüksek (5.5), diğerleri 5.0 --
            # ceza olmadan greedy karar SONSUZA DEK 3'ü seçer. Fark (0.5)
            # KASITLI OLARAK KÜÇÜK: repetition_penalty=1.3 uygulanınca
            # 5.5/1.3≈4.23 < 5.0 olup sıralamayı GERÇEKTEN değiştirir --
            # gerçek modeldeki ince olasılık farklarını temsil eder.
            logit = torch.full((self.vocab,), 5.0)
            logit[3] = 5.5
            return logit, (state or [torch.zeros(self.d)])

    native = _TekTokene_Saplanan_RWKV()
    model = RWKVUyumluModel(native, "cpu fp32")
    son_logits = torch.full((native.vocab,), 5.0)
    son_logits[3] = 5.5

    cezasiz, _l1, _d1 = model.uret_devam(son_logits.clone(), None, max_new_tokens=6, do_sample=False)
    _dogrula(cezasiz == [3, 3, 3, 3, 3, 3], "CEZASIZ (varsayılan): greedy karar beklendiği gibi hep AYNI tokende (3) SAPLANIP KALIYOR")

    cezali_uret, _l2, _d2 = model.uret_devam(son_logits.clone(), None, max_new_tokens=6, do_sample=False, repetition_penalty=1.3)
    _dogrula(len(set(cezali_uret)) > 1, f"repetition_penalty=1.3 İLE: greedy karar artık TEK bir tokende saplanıp kalmıyor, birden fazla farklı token üretti: {cezali_uret}")
    _dogrula(cezali_uret[0] == 3, "İLK token hâlâ 3 (henüz geçmişte yok, cezalanmadı) -- ceza yalnızca DAHA ÖNCE üretilmiş tokenleri etkiliyor")
    _dogrula(cezali_uret[1] != 3, "ceza uygulanınca İKİNCİ adımda artık 3 TEKRAR seçilmiyor (olasılığı düşürüldü)")

    # --- Üretim ayarlarının GERÇEKTEN devreye girdiğini doğrula: ajan
    # (fonksiyon_cagirma) preset'inde artık repetition_penalty>1.0 var mı?
    from model_yapilandirmalari import RWKV
    from ttt_lora import uretim_ayarlarini_al

    class _SahteTokenizer:
        pad_token_id = 0

    ayarlar = uretim_ayarlarini_al(RWKV, _SahteTokenizer())
    _dogrula(ayarlar.get("repetition_penalty", 1.0) > 1.0,
              f"ajan preset'i (fonksiyon_cagirma, temp=0.0 -> greedy) artık repetition_penalty>1.0 taşıyor: {ayarlar.get('repetition_penalty')}")


def test_30_rwkv_tokenizer_decode_tek_kotu_id_tum_metni_yok_etmiyor_mu() -> None:
    print("[test 30] rwkv_native.RWKVUyumluTokenizer.decode(): GERÇEK kurulu `rwkv` paketinin kendi decode()'u dizide TEK bir kötü id varsa (ör. bizim pad_token_id=0) TÜM çıktıyı '�' tek karaktere indirgiyor -- bizim sarmalayıcımız bunu düzeltip geri kalan GEÇERLİ metni koruyor mu?...")

    import os

    os.environ.setdefault("RWKV_V7_ON", "1")
    from rwkv.utils import PIPELINE

    from rwkv_native import native_rwkv_tokenizer_yukle

    ham_pipeline = PIPELINE(None, "rwkv_vocab_v20230424")
    tok = native_rwkv_tokenizer_yukle()

    gercek_ids = ham_pipeline.encode("Hello world")
    _dogrula(len(gercek_ids) >= 2, "sınama için gerçek tokenizer'dan en az 2 gerçek id alındı")

    # ÖNCE: kurulu `rwkv` paketinin KENDİ decode()'unun GERÇEKTEN bu kadar
    # kırılgan olduğunu kanıtla (bizim sarmalayıcımız olmadan) -- bu bir
    # varsayım DEĞİL, gerçek pakete karşı ölçülmüş bir gerçek.
    ids_pad_gomulu = gercek_ids + [0] + gercek_ids
    ham_sonuc = ham_pipeline.decode(ids_pad_gomulu)
    _dogrula(ham_sonuc == "�",
              f"KANIT: kurulu rwkv paketinin ham decode()'u, aralarında TEK bir pad(0) id'si olan iki 'Hello world' kopyasını (toplam {len(ids_pad_gomulu)} id) TAMAMEN yok edip TEK '�' karakterine indirgiyor (ölçülen: {ham_sonuc!r})")

    # SONRA: bizim RWKVUyumluTokenizer.decode() aynı diziyi GEÇERLİ metni
    # KORUYARAK doğru çözüyor.
    bizim_sonuc = tok.decode(ids_pad_gomulu)
    beklenen = "Hello worldHello world"  # pad(0) skip_special_tokens ile atlanır
    _dogrula(bizim_sonuc == beklenen,
              f"DÜZELTİLDİ: bizim decode() aynı diziyi doğru çözüyor, GEÇERLİ metin KAYBOLMUYOR (bulunan: {bizim_sonuc!r})")

    # Kesik (yarım kalmış çok-baytlı UTF-8 kuyruklu) bir dizi de -- yalnızca
    # KUYRUK '�' olmalı, BAŞTAKİ geçerli metin kaybolmamalı.
    emoji_ids = ham_pipeline.encode("plain text before, then an emoji: 😀 and more after")
    kesik_ids = emoji_ids[:-1]
    kesik_sonuc = tok.decode(kesik_ids)
    _dogrula(kesik_sonuc.startswith("plain text before, then an emoji:"),
              f"BAŞTAKİ geçerli metin, SONDAKİ kesik/geçersiz bayt dizisine rağmen KORUNDU (bulunan: {kesik_sonuc!r})")


def test_31_ayrintili_log_uzun_prefill_boyunca_sessiz_kalmiyor_mu() -> None:
    print("[test 31] rwkv_batch.onisle_toplu_farkli_uzunluk + coz_yurutucu_toplu: kullanıcının '800 saniyedir hiç log yok' diye fark ettiği batched-prefill sessizliği, ayrintili_log=True iken GERÇEKTEN kapatılıyor mu?...")

    import rwkv_batch

    # --- Birim test: ilerleme_geri_cagirma GERÇEKTEN periyodik (ve bitişte)
    # çağrılıyor mu -- en uzun promptun 6300+ adımlık bir prefill'i
    # boyunca sessiz kalmamalı.
    B, vocab, n_layer, n_embd, n_head, head_size = 2, 8, 1, 4, 1, 4
    z = {
        "emb.weight": torch.randn(vocab, n_embd), "head.weight": torch.randn(n_embd, vocab),
        "ln_out.weight": torch.ones(n_embd), "ln_out.bias": torch.zeros(n_embd),
        "blocks.0.ln1.weight": torch.ones(n_embd), "blocks.0.ln1.bias": torch.zeros(n_embd),
        "blocks.0.ln2.weight": torch.ones(n_embd), "blocks.0.ln2.bias": torch.zeros(n_embd),
        "blocks.0.att.x_r": torch.zeros(n_embd), "blocks.0.att.x_w": torch.zeros(n_embd),
        "blocks.0.att.x_k": torch.zeros(n_embd), "blocks.0.att.x_v": torch.zeros(n_embd),
        "blocks.0.att.x_a": torch.zeros(n_embd), "blocks.0.att.x_g": torch.zeros(n_embd),
        "blocks.0.att.w0": torch.zeros(n_embd), "blocks.0.att.w1": torch.zeros(n_embd, 2), "blocks.0.att.w2": torch.zeros(2, n_embd),
        "blocks.0.att.a0": torch.zeros(n_embd), "blocks.0.att.a1": torch.zeros(n_embd, 2), "blocks.0.att.a2": torch.zeros(2, n_embd),
        "blocks.0.att.v0": torch.zeros(n_embd), "blocks.0.att.v1": torch.zeros(n_embd, 2), "blocks.0.att.v2": torch.zeros(2, n_embd),
        "blocks.0.att.g1": torch.zeros(n_embd, 2), "blocks.0.att.g2": torch.zeros(2, n_embd),
        "blocks.0.att.k_k": torch.zeros(n_embd), "blocks.0.att.k_a": torch.zeros(n_embd), "blocks.0.att.r_k": torch.zeros(n_head, head_size),
        "blocks.0.att.receptance.weight": torch.eye(n_embd), "blocks.0.att.key.weight": torch.eye(n_embd),
        "blocks.0.att.value.weight": torch.eye(n_embd), "blocks.0.att.output.weight": torch.eye(n_embd),
        "blocks.0.att.ln_x.weight": torch.ones(n_embd), "blocks.0.att.ln_x.bias": torch.zeros(n_embd),
        "blocks.0.ffn.x_k": torch.zeros(n_embd), "blocks.0.ffn.key.weight": torch.eye(n_embd), "blocks.0.ffn.value.weight": torch.eye(n_embd),
    }
    token_dizileri = [[1, 2, 3, 4, 5], [1, 2]]  # farklı uzunluk -- 5 adımlık prefill

    cagrilar: List[Any] = []
    rwkv_batch.onisle_toplu_farkli_uzunluk(
        z, n_layer, n_embd, n_head, head_size, token_dizileri,
        ilerleme_geri_cagirma=lambda t, azami: cagrilar.append((t, azami)), ilerleme_adimi=2,
    )
    _dogrula(cagrilar == [(2, 5), (4, 5), (5, 5)],
              f"5 adımlık bir prefill'de, ilerleme_adimi=2 iken geri çağırma TAM OLARAK 2,4 ve bitişte (5) tetiklendi: {cagrilar}")

    cagrilar_yok: List[Any] = []
    rwkv_batch.onisle_toplu_farkli_uzunluk(z, n_layer, n_embd, n_head, head_size, token_dizileri)
    _dogrula(cagrilar_yok == [], "geri çağırma verilmezse (varsayılan davranış, YARISMA=True) HİÇ ek log üretilmedi")

    # --- toplu_gorevleri_coz uçtan uca: ayrintili_log=True iken prefill
    # SIRASINDA ("batched prefill:" satırları) stdout'ta GERÇEKTEN görünüyor
    # mu -- kullanıcının "800 saniyedir tek log yok" diye şikayet ettiği
    # tam o boşluk.
    import io
    from contextlib import redirect_stdout

    import coz_yurutucu_toplu as cyt

    def _mock_onisle(z, n_layer, n_embd, n_head, head_size, token_dizileri, ilerleme_geri_cagirma=None, ilerleme_adimi=200):
        if ilerleme_geri_cagirma is not None:
            for t in (200, 400, 500):
                ilerleme_geri_cagirma(t, 500)
        B = len(token_dizileri)
        return torch.zeros(B, 4), ["durum"]

    def _mock_adim(z, n_layer, n_embd, n_head, head_size, token_idler, durum, aktif_maske):
        B = len(token_idler)
        return torch.zeros(B, 4), durum

    tasks = [
        Task(test_example=Example(input=np.array([[1]]), output=np.array([[1]])), train_examples=[], name="uzun-gorev"),
    ]
    eski_onisle, eski_adim = cyt.onisle_toplu_farkli_uzunluk, cyt.adim_toplu_maskeli
    eski_ayarlar = cyt.uretim_ayarlarini_al
    cyt.onisle_toplu_farkli_uzunluk = _mock_onisle
    cyt.adim_toplu_maskeli = _mock_adim
    cyt.uretim_ayarlarini_al = lambda model_ailesi, tokenizer: {"do_sample": False, "pad_token_id": 0}
    try:
        yakalanan_sessiz = io.StringIO()
        with redirect_stdout(yakalanan_sessiz):
            cyt.toplu_gorevleri_coz(_SahteHamModelCyt(), _TamTersinirTokenizerCyt(), tasks, azami_yeni_token=1, kontrol_araligi=1, ayrintili_log=False)

        yakalanan_ayrintili = io.StringIO()
        with redirect_stdout(yakalanan_ayrintili):
            cyt.toplu_gorevleri_coz(_SahteHamModelCyt(), _TamTersinirTokenizerCyt(), tasks, azami_yeni_token=1, kontrol_araligi=1, ayrintili_log=True)
    finally:
        cyt.onisle_toplu_farkli_uzunluk, cyt.adim_toplu_maskeli = eski_onisle, eski_adim
        cyt.uretim_ayarlarini_al = eski_ayarlar

    _dogrula("batched prefill:" not in yakalanan_sessiz.getvalue(), "ayrintili_log=False (YARISMA=True varsayılanı) iken prefill İLERLEME logu basılmadı (yarışma logu şişirilmiyor)")
    _dogrula(yakalanan_ayrintili.getvalue().count("batched prefill:") == 3, "ayrintili_log=True (YARISMA=False) iken prefill SIRASINDA 3 ilerleme logu GERÇEKTEN basıldı -- kullanıcının fark ettiği sessizlik kapatıldı")


class _SahteHamModelCyt:
    z: Dict[str, Any] = {}
    n_layer = n_embd = n_head = head_size = 1


class _TamTersinirTokenizerCyt:
    pad_token_id = 0
    eos_token_id = 0

    def encode(self, metin: str, add_special_tokens: bool = True) -> List[int]:
        return [ord(c) for c in metin]

    def decode(self, token_idler: Any, skip_special_tokens: bool = True) -> str:
        if hasattr(token_idler, "tolist"):
            token_idler = token_idler.tolist()
        return "".join(chr(int(t)) for t in token_idler)


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
    test_21_vram_tabanli_b_kesfi()
    test_22_coklu_gpu_loglarinda_hangi_gpu_oldugu_ayirt_edilebiliyor_mu()
    test_23_gpu_tespit_derinlemesine_ve_gorunmeyen_indeksler_dogru_etiketleniyor()
    test_24_onisle_toplu_farkli_uzunluk_gercek_rwkv_ile_ragged_batch_dogrulamasi()
    test_25_toplu_gorevleri_coz_gercekten_farkli_sorulara_ayni_anda_bakiyor_mu()
    test_26_padisah_vezir_toplu_ise_baslamadan_once_esit_pay_veriyor_mu()
    test_27_modele_geri_beslenen_arac_yanitlari_ingilizce_mi()
    test_28_uret_devam_yozlasmis_donguyu_erken_yakaliyor_mu()
    test_29_tekrar_cezasi_gercekten_ayni_tokene_saplanmayi_zorlastiriyor_mu()
    test_30_rwkv_tokenizer_decode_tek_kotu_id_tum_metni_yok_etmiyor_mu()
    test_31_ayrintili_log_uzun_prefill_boyunca_sessiz_kalmiyor_mu()

    if BASARISIZLIK_SAYACI["n"] == 0:
        print("\n[test] TÜMÜ BAŞARILI.")
    else:
        print(f"\n[test] {BASARISIZLIK_SAYACI['n']} DOĞRULAMA BAŞARISIZ.")
        sys.exit(1)


if __name__ == "__main__":
    calistir()
