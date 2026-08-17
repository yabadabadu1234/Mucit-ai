"""
GERÇEK toplu (batched) çoklu-görev çözücü: B FARKLI ARC bulmacasını, AYNI
model ağırlıklarını paylaşarak, TEK GPU'da TEK bir batched adım zincirinde
EŞZAMANLI çözer.

Bu dosya, rwkv_batch.py'nin (Albatross incelemesinden çıkan "tek GPU'da
aynı ağırlıkları paylaşan çoklu bağımsız diziyi toplu işle" fikrinin)
GERÇEKTEN üretim hattına BAĞLANDIĞI yerdir -- önceki halde rwkv_batch.py
yalnızca test_boru_hatti.py'de İZOLE olarak doğrulanmıştı ama hiçbir
üretim kodu onu ÇAĞIRMIYORDU (coklu_gpu.py hâlâ her vezirde B=1, görevleri
TEK TEK, seri biçimde çözüyordu). Kullanıcının açık talebi: "B'lerin aynı
promptla değil, FARKLI sorular için çalışması, tek GPU'daki modelin
hakikaten 128 soruya AYNI ANDA bakması" -- bu dosya tam olarak bunu yapar:

  1. B FARKLI görev için B FARKLI prompt üretilir (aynı sistem şablonu,
     farklı bulmaca içeriği -- token dizileri de FARKLI UZUNLUKTADIR).
  2. rwkv_batch.onisle_toplu_farkli_uzunluk ile bu B FARKLI UZUNLUKTAKİ
     prompt, TEK bir batched prefill'de (maskeli adımlarla, kısa
     promptlar kendi sonlarında dondurularak) işlenir.
  3. Üretim de TEK bir batched döngüde ilerler: her adımda B dizinin
     HER BİRİ için AYRI AYRI örneklenen bir sonraki token, TEK bir
     adim_toplu_maskeli çağrısıyla hep birden işlenir. Periyodik olarak
     (KONTROL_ARALIGI token'da bir) her dizinin metni araç-çağrısı için
     kontrol edilir; submit_answer BAŞARIYLA çağrılan diziler
     "dondurulur" (aktif_maske'den çıkarılır) ve geri kalan diziler
     TEK batch içinde devam eder -- kimse kimseyi beklemez, biten
     dizinin "koltuğu" boşa düşer ama batch'in geri kalanı kesintisiz
     sürer.
"""
import time
from typing import Any, Callable, Dict, List, Optional

import torch

from arc import Task
from araclar import CevapDefteri, arac_cagrilarini_ayikla, arac_cagrisini_yurut, tool_response_mesaji_olustur
from coz_yurutucu import BOS_TAHMIN, IKAZ_ESIGI_TOKEN, IKAZ_METNI, _ARAC_CAGRISI_YOK_UYARISI, _ilk_mesajlar
from model_yapilandirmalari import RWKV
from rwkv_batch import _maske_uygula, adim_toplu_maskeli, onisle_toplu_farkli_uzunluk, sifir_durum_toplu
from rwkv_native import _tekrar_cezasi_uygula, _tekrara_kilitlenme_periyodu
from transkript import transkript_satiri_yaz
from ttt_lora import mesajlari_metne_donustur, rwkv_tek_mesaji_sar, uretim_ayarlarini_al

_ONEK = "[coz_yurutucu_toplu]"
_ILERLEME_ADIMI = 5000


def _boyutlari_al(ham_rwkv_modeli: Any):
    return ham_rwkv_modeli.n_layer, ham_rwkv_modeli.n_embd, ham_rwkv_modeli.n_head, ham_rwkv_modeli.head_size


def _sample_tek(logit_satiri: torch.Tensor, do_sample: bool, temperature: Optional[float],
                 repetition_penalty: Optional[float] = None, gecmis_tokenler: Optional[List[int]] = None) -> int:
    if repetition_penalty and repetition_penalty > 1.0 and gecmis_tokenler:
        logit_satiri = _tekrar_cezasi_uygula(logit_satiri, gecmis_tokenler, repetition_penalty)
    if not do_sample:
        return int(torch.argmax(logit_satiri).item())
    olasiliklar = torch.softmax(logit_satiri / max(temperature or 1.0, 1e-4), dim=-1)
    return int(torch.multinomial(olasiliklar, 1).item())


def _ek_metni_tek_diziye_besle(z, n_layer, n_embd, n_head, head_size, b: int, B: int,
                                token_idler: List[int], durum: List[torch.Tensor]) -> List[torch.Tensor]:
    """Yalnızca dizi b'yi, kalan B-1 diziyi DONDURARAK (aktif_maske'de
    False bırakarak) verilen ek token dizisiyle ilerletir -- IKAZ
    (yazma hakkı tükeniyor) metninin, YALNIZCA o eşiğe ulaşan diziye,
    diğerlerini etkilemeden enjekte edilmesini sağlar."""
    for tok in token_idler:
        aktif_maske = [False] * B
        aktif_maske[b] = True
        tum_tokenler = [tok] * B
        _logits, durum = adim_toplu_maskeli(z, n_layer, n_embd, n_head, head_size, tum_tokenler, durum, aktif_maske)
    return durum


def _slot_durumunu_sifirla(durum: List[torch.Tensor], b: int, B: int) -> List[torch.Tensor]:
    """Yalnızca slot b'nin state'ini (att_x_prev/att_kv/ffn_x_prev) SIFIRA
    döndürür, kalan B-1 slotun durumuna DOKUNMAZ -- KUYRUKTAN YENİ BİR
    GÖREV alıp aynı slotu (aynı batch koltuğunu) yeni görevle devam
    ettirebilmek için, o slotun ESKİ görevden kalan RNN belleğini
    silmemiz gerekir (_maske_uygula'nın MANTIKSAL TERSİ: burada 'yeni'
    tensör sıfırlardır, aktif olan tek slot b'dir)."""
    maske = [i == b for i in range(B)]
    maske_t = torch.as_tensor(maske, device=durum[0].device, dtype=torch.bool)
    for i in range(len(durum)):
        durum[i] = _maske_uygula(torch.zeros_like(durum[i]), durum[i], maske_t)
    return durum


def _slota_prompt_besle(z, n_layer, n_embd, n_head, head_size, b: int, B: int,
                         prompt_tokenleri: List[int], durum: List[torch.Tensor]) -> tuple:
    """Yeni görevin prompt'unu, YALNIZCA slot b'yi ilerleterek (kalan
    B-1 slot dondurularak) işler -- diğer slotlar KENDİ üretimlerine
    hiç kesintisiz devam ederken, boşalan slot arka planda yeni görevinin
    prefill'ini yapar. Döner: (son_logit, güncel durum)."""
    son_logit = None
    for tok in prompt_tokenleri:
        aktif_maske = [False] * B
        aktif_maske[b] = True
        tum_tokenler = [tok] * B
        logits, durum = adim_toplu_maskeli(z, n_layer, n_embd, n_head, head_size, tum_tokenler, durum, aktif_maske)
        son_logit = logits[b]
    return son_logit, durum


def toplu_gorevleri_coz(
    ham_rwkv_modeli: Any,
    tokenizer: Any,
    tasks: List[Task],
    azami_yeni_token: int = 60000,
    kontrol_araligi: int = 1000,
    deneme_etiketi: str = "toplu",
    ayrintili_log: bool = False,
    bitis_zamani: Optional[float] = None,
    sonraki_gorev_al: Optional[Callable[[], Optional[Task]]] = None,
    tamamlanma_geri_cagirma: Optional[Callable[[str, Dict[str, Any]], None]] = None,
) -> Dict[str, Dict[str, Any]]:
    """B = len(tasks) görevin HEPSİNİ, TEK GPU'da, AYNI ağırlıkları
    (ham_rwkv_modeli.z) paylaşan TEK bir batched adım zinciriyle EŞZAMANLI
    çözer. Döner: {task.name: {"attempt_1": grid, "attempt_1_gonderildi_mi": bool}}
    (yalnızca başlangıçtaki B görev İÇİN DEĞİL, `sonraki_gorev_al` ile
    ARADA ADMİT edilen HER görev için de -- bkz. aşağıda).

    `ayrintili_log=True` (YARISMA=False iken gonderim_uret.py tarafından
    otomatik açılır): en uzun promptlu görev tek başına dakikalarca
    sürebilen batched prefill AŞAMASINDA da (daha önce tamamen sessizdi --
    kullanıcının "800 saniyedir tek log yok" diye fark ettiği boşluk tam
    burasıydı) VE üretim aşamasında çok daha sık (varsayılan 5000 yerine
    200 adımda bir) ilerleme logu basılır.

    `bitis_zamani` (mutlak time.time() zaman damgası) verilirse: ÖNCEDEN
    yalnızca padisah_vezir_toplu_havuzuyla_coz KOTALAR ARASINDA bakıyordu
    -- TEK bir batched parti, kendi azami_yeni_token'ına (60000 adım)
    kadar süre bütçesini HİÇ dinlemeden çalışabiliyordu. Bu, kullanıcının
    fark ettiği yavaşlamanın gerçek nedenlerinden biri: attempt_1 + attempt_2
    (iki tam bağımsız koşu) art arda çalışırken, İÇERDEKİ bir parti tek
    başına saatler sürebiliyordu. Artık üretim döngüsü kontrol_araligi
    aralığında bitis_zamani'yi de kontrol eder; aşılmışsa HENÜZ BİTMEMİŞ
    dizileri "zaman aşımı" ile dondurup elindekiyle döner -- diğer
    vezirlerin/koşuların bütçesini yemez.

    `sonraki_gorev_al` (SÜREKLİ/continuous batching -- BlockServe ve JBAS
    makalelerinden çıkan "block-grained scheduling"/"admission control"
    fikri): verilirse, B slottan biri (submit_answer başarılı olduğunda VEYA
    yozlaşmış döngü tespit edildiğinde) boşaldığı anda, o koltuk PARTİNİN
    SONUNA KADAR BOŞ BEKLEMEK yerine HEMEN `sonraki_gorev_al()` ile kuyruktan
    çekilen YENİ bir görevle doldurulur (o slotun state'i sıfırlanıp yeni
    görevin prompt'u yalnızca o slotta -- diğer B-1 slot kesintisiz devam
    ederken -- prefill edilir). ÖNCEKİ halde biten bir görevin koltuğu,
    partideki EN YAVAŞ görev bitene kadar boşa gidiyordu (BlockServe'in
    "Effective Compute Ratio" dediği, statik batch'te 0.07'ye kadar düşen
    metrik) -- bu artık slot-recycling ile önlenir. `sonraki_gorev_al()`
    None dönerse (kuyruk boş) slot eskisi gibi kalıcı olarak dondurulur.

    `tamamlanma_geri_cagirma(task_adi, sonuc)` verilirse, HER görev (başlangıç
    B'si veya arada admit edilen) bitirilir bitirilmez -- partinin/koşunun
    TAMAMI bitmesini beklemeden -- çağrılır. gonderim_uret.py bunu, submission
    dosyasına ARA KAYDIN artık tüm 172 görev bitmeden değil, HER görev
    bitiminde yapılabilmesi için kullanır (kullanıcının gördüğü "5000/60000
    adım ilerleme logu var ama dosya bomboş" sorunu -- önceki kod yalnızca
    TÜM parti/koşu bittiğinde diske yazıyordu)."""
    B = len(tasks)
    z = ham_rwkv_modeli.z
    n_layer, n_embd, n_head, head_size = _boyutlari_al(ham_rwkv_modeli)
    uretim_ayarlari = uretim_ayarlarini_al(RWKV, tokenizer)
    do_sample = uretim_ayarlari.get("do_sample", True)
    temperature = uretim_ayarlari.get("temperature")
    repetition_penalty = uretim_ayarlari.get("repetition_penalty")
    ilerleme_adimi = 200 if ayrintili_log else _ILERLEME_ADIMI

    # 1) B FARKLI prompt -- FARKLI görev içeriği, dolayısıyla FARKLI
    # token dizileri (uzunlukları da genelde farklıdır). Bu, "aynı
    # promptu B kere kopyalama" hatasının TAM TERSİDİR.
    prompt_tokenleri: List[List[int]] = []
    defterler: List[CevapDefteri] = []
    for task in tasks:
        metin = mesajlari_metne_donustur(tokenizer, RWKV, _ilk_mesajlar(task))
        prompt_tokenleri.append(tokenizer.encode(metin))
        defterler.append(CevapDefteri())

    benzersiz_prompt_sayisi = len({tuple(t) for t in prompt_tokenleri})
    print(
        f"{_ONEK} ({deneme_etiketi}) B={B} görev, {benzersiz_prompt_sayisi} BENZERSİZ prompt "
        f"(uzunluklar: {[len(t) for t in prompt_tokenleri]}) -- TEK batched adım zincirinde eşzamanlı çözülüyor."
    )
    if benzersiz_prompt_sayisi != B:
        print(f"{_ONEK} ({deneme_etiketi}) UYARI: {B - benzersiz_prompt_sayisi} görev BİRBİRİNİN BİREBİR AYNI promptuna sahip (muhtemelen tekrarlanan görev adı/içerik).")

    # 2) Batched prefill: FARKLI uzunluktaki B prompt, TEK maskeli
    # döngüde işlenir (kısa promptlar kendi sonlarında dondurulur).
    baslangic = time.time()
    azami_prompt_uzunlugu = max(len(t) for t in prompt_tokenleri)

    def _prefill_ilerleme(t: int, azami: int) -> None:
        gecen = time.time() - baslangic
        print(f"{_ONEK} ({deneme_etiketi})   batched prefill: {t}/{azami} adım ({gecen:.1f} sn, {t / max(gecen, 1e-6):.2f} adım/sn TÜM batch için).")

    son_logits, durum = onisle_toplu_farkli_uzunluk(
        z, n_layer, n_embd, n_head, head_size, prompt_tokenleri,
        ilerleme_geri_cagirma=_prefill_ilerleme if ayrintili_log else None,
        ilerleme_adimi=ilerleme_adimi,
    )
    print(f"{_ONEK} ({deneme_etiketi}) batched prefill tamamlandı: {azami_prompt_uzunlugu} adım, {time.time() - baslangic:.1f} sn.")

    # 3) Batched üretim: her adımda B dizinin HER BİRİ İÇİN AYRI örneklenen
    # bir sonraki token, TEK adim_toplu_maskeli çağrısıyla hep birlikte
    # işlenir. Biten diziler (submit_answer başarılı) maskeden düşer.
    bitti = [False] * B
    uretilen_tokenler: List[List[int]] = [[] for _ in range(B)]
    ikaz_enjekte_edildi = [False] * B
    sonuclar: List[Optional[List[List[int]]]] = [None] * B
    slot_gorev: List[Task] = list(tasks)  # her slotun O ANKİ sakini -- admission ile DEĞİŞEBİLİR
    sonuclar_by_name: Dict[str, Dict[str, Any]] = {}
    admit_edilen_sayisi = 0

    def _slot_sonucla_bitir(b: int) -> None:
        """Slot b'nin O ANKİ sakinini SONUÇLANDIRIR (kayda geçirir, geri
        çağrıyı tetikler) -- YENİ görev ADMİT ETMEYE ÇALIŞMAZ (süre bütçesi
        dolduğunda/koşu tamamen bittiğinde kullanılır)."""
        ad = slot_gorev[b].name
        sonuclar_by_name[ad] = {
            "attempt_1": sonuclar[b] if sonuclar[b] is not None else BOS_TAHMIN,
            "attempt_1_gonderildi_mi": sonuclar[b] is not None,
        }
        if tamamlanma_geri_cagirma is not None:
            tamamlanma_geri_cagirma(ad, sonuclar_by_name[ad])
        bitti[b] = True

    def _slota_yeni_gorev_yukle(b: int, yeni_gorev: Task) -> None:
        nonlocal durum
        metin = mesajlari_metne_donustur(tokenizer, RWKV, _ilk_mesajlar(yeni_gorev))
        yeni_prompt = tokenizer.encode(metin)
        durum = _slot_durumunu_sifirla(durum, b, B)
        son_logit, durum = _slota_prompt_besle(z, n_layer, n_embd, n_head, head_size, b, B, yeni_prompt, durum)
        son_logits[b] = son_logit
        slot_gorev[b] = yeni_gorev
        defterler[b] = CevapDefteri()
        uretilen_tokenler[b] = []
        ikaz_enjekte_edildi[b] = False
        sonuclar[b] = None
        bitti[b] = False
        if ayrintili_log:
            print(
                f"{_ONEK} ({deneme_etiketi})   SLOT {b} YENİLENDİ: '{yeni_gorev.name}' "
                f"(prompt {len(yeni_prompt)} token) kuyruktan alınıp AYNI batch koltuğuna yüklendi -- "
                f"diğer {B - 1} slot bu sırada KESİNTİSİZ devam etti."
            )

    def _slot_ilerlet(b: int) -> None:
        """Slot b'nin O ANKİ sakini bitti -- sonucu kaydeder, geri çağrıyı
        tetikler, KUYRUKTA yeni görev varsa slotu HEMEN o görevle doldurup
        devam ettirir (bkz. fonksiyon docstring'i: continuous batching /
        admission control), yoksa slotu kalıcı olarak dondurur."""
        nonlocal admit_edilen_sayisi
        _slot_sonucla_bitir(b)
        if sonraki_gorev_al is None:
            return
        yeni_gorev = sonraki_gorev_al()
        if yeni_gorev is not None:
            admit_edilen_sayisi += 1
            _slota_yeni_gorev_yukle(b, yeni_gorev)

    uretim_baslangici = time.time()
    adim = 0
    while adim < azami_yeni_token and not all(bitti):
        aktif_maske = [not bitti[b] for b in range(B)]
        sonraki_tokenler: List[int] = []
        for b in range(B):
            if bitti[b]:
                sonraki_tokenler.append(0)
                continue
            tok = _sample_tek(son_logits[b], do_sample, temperature, repetition_penalty, uretilen_tokenler[b])
            uretilen_tokenler[b].append(tok)
            sonraki_tokenler.append(tok)

        yeni_logits, durum = adim_toplu_maskeli(z, n_layer, n_embd, n_head, head_size, sonraki_tokenler, durum, aktif_maske)
        for b in range(B):
            if aktif_maske[b]:
                son_logits[b] = yeni_logits[b]
        adim += 1

        if adim % ilerleme_adimi == 0:
            aktif_sayisi = sum(1 for x in bitti if not x)
            gecen = time.time() - uretim_baslangici
            print(f"{_ONEK} ({deneme_etiketi})   üretim: {adim}/{azami_yeni_token} adım, {aktif_sayisi}/{B} görev hâlâ aktif ({gecen:.1f} sn, {adim / max(gecen, 1e-6):.2f} adım/sn TÜM batch için).")

        if adim % kontrol_araligi != 0 and adim != azami_yeni_token:
            continue

        if bitis_zamani is not None and time.time() > bitis_zamani and not all(bitti):
            print(
                f"{_ONEK} ({deneme_etiketi})   SÜRE BÜTÇESİ TÜKENDİ: {adim} adımda, {sum(1 for x in bitti if not x)}/{B} "
                f"görev HÂLÂ bitmemişken durduruluyor -- bu partinin kalanı boş tahminle işaretlenecek "
                f"(kapanış anında YENİ görev ADMİT EDİLMEZ)."
            )
            for b in range(B):
                if not bitti[b]:
                    _slot_sonucla_bitir(b)
            break

        for b in range(B):
            if bitti[b]:
                continue
            metin_simdi = tokenizer.decode(uretilen_tokenler[b])
            cagrilar = arac_cagrilarini_ayikla(metin_simdi)
            if cagrilar:
                for cagri in cagrilar:
                    sonuc = arac_cagrisini_yurut(cagri, defterler[b])
                    transkript_satiri_yaz({
                        "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                        "rol": "arac-sonucu", "arac": cagri.get("name"), "icerik": sonuc,
                    })
                    if cagri.get("name") == "submit_answer" and sonuc.get("success"):
                        sonuclar[b] = defterler[b].kaydedilen_cevap
                        bitti[b] = True
                if bitti[b]:
                    transkript_satiri_yaz({
                        "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                        "rol": "assistant", "icerik": metin_simdi,
                    })
                    _slot_ilerlet(b)
                    continue
            # Yozlaşmış döngü kontrolü: tek bir dizi kilitlenip hiç bitmezse
            # (kullanıcının gerçek transkriptinde görülen davranış), paylaşılan
            # while döngüsü `not all(bitti)` şartı yüzünden TÜM batch'i azami_
            # yeni_token'a kadar bekletir -- bu diziyi ERKEN "bitti" işaretleyip
            # (cevapsız) dondurmak, aynı batch'teki DİĞER görevlerin beklemeden
            # bitmesini sağlar.
            periyot = _tekrara_kilitlenme_periyodu(uretilen_tokenler[b])
            if periyot is not None:
                print(
                    f"{_ONEK} ({deneme_etiketi})   {slot_gorev[b].name}: YOZLAŞMIŞ DÖNGÜ tespit edildi "
                    f"({periyot} token'lık alt-dizi 3 kez tekrarlandı) -- bu dizi ERKEN durduruldu, "
                    f"batch'teki DİĞER görevler beklemeden devam ediyor."
                )
                transkript_satiri_yaz({
                    "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                    "rol": "sistem-uyari", "icerik": f"yozlaşmış döngü tespit edildi (periyot={periyot}), üretim erken durduruldu",
                })
                _slot_ilerlet(b)
                continue
            if not ikaz_enjekte_edildi[b] and adim >= IKAZ_ESIGI_TOKEN:
                ikaz_enjekte_edildi[b] = True
                print(f"{_ONEK} ({deneme_etiketi})   {slot_gorev[b].name}: İKAZ enjekte ediliyor (yazma hakkı tükenmek üzere).")
                ikaz_tokenleri = tokenizer.encode(rwkv_tek_mesaji_sar({"role": "user", "content": IKAZ_METNI}))
                durum = _ek_metni_tek_diziye_besle(z, n_layer, n_embd, n_head, head_size, b, B, ikaz_tokenleri, durum)
                # o dizinin son_logits'ini IKAZ sonrası duruma göre yenile
                _tek_logit, durum = adim_toplu_maskeli(
                    z, n_layer, n_embd, n_head, head_size,
                    [uretilen_tokenler[b][-1] if uretilen_tokenler[b] else 0] * B, durum,
                    [i == b for i in range(B)],
                )
                son_logits[b] = _tek_logit[b]
                transkript_satiri_yaz({
                    "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                    "rol": "sistem-ikaz", "icerik": IKAZ_METNI,
                })

    for b in range(B):
        if not bitti[b]:
            print(f"{_ONEK} ({deneme_etiketi})   {slot_gorev[b].name}: {adim} adım sonunda HÂLÂ araç çağrısı yok (bütçe tükendi).")
            transkript_satiri_yaz({
                "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                "rol": "assistant", "icerik": tokenizer.decode(uretilen_tokenler[b]),
            })
            _slot_sonucla_bitir(b)

    tamamlanan = sum(1 for s in sonuclar_by_name.values() if s["attempt_1_gonderildi_mi"])
    print(
        f"{_ONEK} ({deneme_etiketi}) BİTTİ: başlangıç B={B} + {admit_edilen_sayisi} ADMİT edilen = "
        f"{len(sonuclar_by_name)} görevden {tamamlanan} tanesi GERÇEKTEN submit_answer ile sonuçlandı, "
        f"toplam {adim} batched adım, {time.time() - uretim_baslangici:.1f} sn."
    )

    return sonuclar_by_name
