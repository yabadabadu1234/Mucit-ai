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
import json
import time
from typing import Any, Callable, Dict, List, Optional

import torch

from arc import Task
from araclar import CevapDefteri, arac_cagrilarini_ayikla, arac_cagrisini_yurut, tool_response_mesaji_olustur
from coz_yurutucu import BOS_TAHMIN, IKAZ_ESIGI_TOKEN, IKAZ_METNI, _ARAC_CAGRISI_YOK_UYARISI, _ilk_mesajlar
from model_yapilandirmalari import RWKV
from rwkv_batch import _maske_uygula, adim_toplu_maskeli, onisle_toplu_farkli_uzunluk, sifir_durum_toplu
from rwkv_native import _tekrara_kilitlenme_periyodu
from transkript import transkript_satiri_yaz
from ttt_lora import mesajlari_metne_donustur, rwkv_tek_mesaji_sar, uretim_ayarlarini_al

_ONEK = "[coz_yurutucu_toplu]"
_ILERLEME_ADIMI = 5000
# Yozlaşmış döngüye giren ama HENÜZ geçerli bir cevabı olmayan bir slot,
# kuyruktan YENİ bir göreve geçmeden önce AYNI promptla en fazla kaç kez
# baştan denenir (kullanıcının açık talebi: "yoksa sadece o silinsin ve
# yeniden aynı promptla çözülmeye çalışılsın") -- do_sample=True olduğu
# sürece her deneme FARKLI örneklenir; bu sınır yalnızca greedy/şanssız
# durumlarda sonsuz döngüye karşı bir GÜVENLİK ÇATISIdır.
AZAMI_AYNI_PROMPT_YENIDEN_DENEME = 3


def _boyutlari_al(ham_rwkv_modeli: Any):
    return ham_rwkv_modeli.n_layer, ham_rwkv_modeli.n_embd, ham_rwkv_modeli.n_head, ham_rwkv_modeli.head_size


def _ek_metni_tek_diziye_besle(z, n_layer, n_embd, n_head, head_size, b: int, B: int,
                                token_idler: List[int], durum: List[torch.Tensor]) -> tuple:
    """Yalnızca dizi b'yi, kalan B-1 diziyi DONDURARAK (aktif_maske'de
    False bırakarak) verilen ek token dizisiyle ilerletir -- IKAZ (yazma
    hakkı tükeniyor) metninin VEYA bir araç-çağrısı sonucunun (bkz.
    toplu_gorevleri_coz'daki tool_response enjeksiyonu), YALNIZCA o slota,
    diğerlerini etkilemeden enjekte edilmesini sağlar. Döner: (son_logit,
    güncel durum) -- son_logit, b'nin beslenen metnin SON tokenından
    sonraki tahminidir; çağıran taraf bunu DOĞRUDAN son_logits[b] için
    kullanabilir, ekstra bir "yenile" adımına GEREK YOKTUR."""
    son_logit = None
    for tok in token_idler:
        aktif_maske = [False] * B
        aktif_maske[b] = True
        tum_tokenler = [tok] * B
        logits, durum = adim_toplu_maskeli(z, n_layer, n_embd, n_head, head_size, tum_tokenler, durum, aktif_maske)
        son_logit = logits[b]
    return son_logit, durum


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
    çekilen YENİ bir görevle doldurulur. ÖNCEKİ halde biten bir görevin
    koltuğu, partideki EN YAVAŞ görev bitene kadar boşa gidiyordu
    (BlockServe'in "Effective Compute Ratio" dediği, statik batch'te 0.07'ye
    kadar düşen metrik) -- bu artık slot-recycling ile önlenir.
    `sonraki_gorev_al()` None dönerse (kuyruk boş) slot eskisi gibi kalıcı
    olarak dondurulur.

    ÖNEMLİ (kullanıcının haklı itirazı -- "neden birbirlerini beklesinler,
    42 tanesi 1000. token'i üretirken 43'üncü 100. token'inde olabilir"):
    yeni/yeniden denenen bir görevin prompt'u ARTIK AYRI, SENKRON bir alt
    döngüde (o bitene kadar TÜM diğer slotları donduran bir iç `for` ile)
    HEMEN baştan sona işlenmiyor. Bunun yerine slot b, `bekleyen_prompt[b]`
    kuyruğuna KONUP paylaşılan ana adım döngüsüne GERİ dönüyor -- her paylaşılan
    `adim`'de, HENÜZ prompt'u tüketmekte olan slotlar kuyruklarından BİR
    sonraki prompt token'ini, AYNI ANDA gerçekten ÜRETMEKTE olan diğer
    slotlar da KENDİ örneklenen bir sonraki token'lerini alır -- hepsi TEK
    bir `adim_toplu_maskeli` çağrısında birlikte ilerler. Böylece bir slotun
    (binlerce token olabilen) prompt'unu yeniden işlemesi, diğer B-1 slotun
    tek bir adımını bile GECİKTİRMEZ -- her slot GERÇEKTEN kendi hızında,
    kendi "pozisyonunda" ilerler (biri 100. adımdayken diğeri 1000. adımda
    olabilir), yalnızca ALT SEVİYEDE aynı batched matris çarpımını paylaşırlar.

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
    yeniden_deneme_sayisi = [0] * B  # yozlaşmış döngüden AYNI promptla kaç kez yeniden başlandı
    # Slot b niye bu listede boş DEĞİL: o slot HENÜZ yeni (admit edilmiş/
    # yeniden denenen) bir görevin PROMPT'unu tüketiyor -- her paylaşılan
    # `adim`de listenin BAŞINDAN bir token çekilip beslenir, diğer B-1 slot
    # bu sırada KENDİ üretimine (sampling) devam eder, KİMSE KİMSEYİ
    # BEKLEMEZ (bkz. fonksiyon docstring'i).
    bekleyen_prompt: List[List[int]] = [[] for _ in range(B)]
    # Her slotun DAHA ÖNCE çalıştırılmış/yanıtlanmış araç-çağrısı
    # "parmak izlerini" (isim+argümanlar) tutar -- aynı çağrı bir daha
    # görülünce (bkz. ana döngüdeki gerekçe) tekrar ÇALIŞTIRILMAZ/
    # YANITLANMAZ.
    islenen_cagri_izleri: List[set] = [set() for _ in range(B)]

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
        """Slot b'yi yeni_gorev ile YENİDEN BAŞLATIR -- ama prompt'u BURADA
        senkron olarak İŞLEMEZ (eski davranış tüm B-1 diğer slotu bloke
        ediyordu). Bunun yerine slotun state'i sıfırlanır ve prompt'un
        TAMAMI `bekleyen_prompt[b]`ye KUYRUKLANIR -- paylaşılan ana adım
        döngüsü, her adımda bu kuyruktan BİR token çekip besleyerek,
        DİĞER slotların KENDİ gerçek üretim adımlarıyla AYNI ANDA (tek
        `adim_toplu_maskeli` çağrısında) ilerletecek."""
        nonlocal durum
        metin = mesajlari_metne_donustur(tokenizer, RWKV, _ilk_mesajlar(yeni_gorev))
        yeni_prompt = tokenizer.encode(metin)
        durum = _slot_durumunu_sifirla(durum, b, B)
        bekleyen_prompt[b] = list(yeni_prompt)
        slot_gorev[b] = yeni_gorev
        defterler[b] = CevapDefteri()
        uretilen_tokenler[b] = []
        ikaz_enjekte_edildi[b] = False
        sonuclar[b] = None
        bitti[b] = False
        islenen_cagri_izleri[b] = set()
        gorulen_maske[b, :] = False  # yeni görevin tekrar-cezası geçmişi TEMİZ başlar
        if ayrintili_log:
            print(
                f"{_ONEK} ({deneme_etiketi})   SLOT {b} YENİLENDİ: '{yeni_gorev.name}' (prompt {len(yeni_prompt)} "
                f"token) kuyruklandı -- paylaşılan adım döngüsünde diğer {B - 1} slotla AYNI ANDA, hiçbirini "
                f"BEKLETMEDEN tüketilecek."
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
            yeniden_deneme_sayisi[b] = 0

    # HIZ (kullanıcının açık talebi -- adım/sn çok düşüktü, kaynağı CUDA
    # DEĞİL, Python tarafındaki formül/tekrar fazlalığıydı): ÖNCEKİ kod
    # HER adımda B kez ayrı ayrı _sample_tek() çağırıyordu -- her çağrı
    # KENDİ softmax/multinomial GPU çağrısını başlatıyordu (B küçük GPU
    # çağrısı, TEK büyük bir çağrı yerine) VE repetition_penalty için
    # `sorted(set(uretilen_tokenler[b]))`'i O DİZİ NE KADAR UZUNSA O KADAR
    # PAHALI olacak şekilde HER ADIMDA SIFIRDAN yeniden kuruyordu (5000+
    # tokenlik bir üretimde bu, üretim boyunca toplamda O(n²) Python işi
    # demekti -- asıl yavaşlığın kaynağı muhtemelen buydu). Artık TÜM B
    # satır TEK bir vektörize softmax/multinomial çağrısında birlikte
    # örnekleniyor; "daha önce görülen token" takibi de dizi geçmişini
    # yeniden taramak yerine kalıcı bir (B, vocab) bool tensörünü TEK bir
    # scatter-yazma ile güncelliyor (O(1) artımlı, O(n) yeniden-tarama
    # DEĞİL).
    vocab_boyutu = son_logits.shape[-1]
    cihaz = son_logits.device
    gorulen_maske = torch.zeros(B, vocab_boyutu, dtype=torch.bool, device=cihaz)

    uretim_baslangici = time.time()
    adim = 0
    while adim < azami_yeni_token and not all(bitti):
        aktif_maske = [not bitti[b] for b in range(B)]
        aktif_maske_t = torch.tensor(aktif_maske, device=cihaz, dtype=torch.bool)
        gercek_uretim_maskesi = torch.tensor(
            [not bitti[b] and not bekleyen_prompt[b] for b in range(B)], device=cihaz, dtype=torch.bool
        )

        if repetition_penalty and repetition_penalty > 1.0 and gercek_uretim_maskesi.any():
            etkilenen = gorulen_maske & gercek_uretim_maskesi.unsqueeze(1)
            son_logits = torch.where(etkilenen & (son_logits > 0), son_logits / repetition_penalty, son_logits)
            son_logits = torch.where(etkilenen & (son_logits <= 0), son_logits * repetition_penalty, son_logits)

        if do_sample:
            olasiliklar = torch.softmax(son_logits / max(temperature or 1.0, 1e-4), dim=-1)
            ornekler = torch.multinomial(olasiliklar, 1).squeeze(1)
        else:
            ornekler = torch.argmax(son_logits, dim=-1)
        ornekler_liste = ornekler.tolist()

        sonraki_tokenler: List[int] = []
        for b in range(B):
            if bitti[b]:
                sonraki_tokenler.append(0)
                continue
            if bekleyen_prompt[b]:
                # Bu slot HENÜZ (admit edilmiş/yeniden denenen) bir görevin
                # prompt'unu tüketiyor -- ÖRNEKLEME YOK, kuyruktan bir
                # SONRAKİ gerçek prompt token'i beslenir; diğer, GERÇEKTEN
                # üretmekte olan slotlar bu satırın etkilenmeden AŞAĞIDAKİ
                # normal örnekleme yoluna girer -- aynı `adim`de, aynı tek
                # adim_toplu_maskeli çağrısında birlikte ilerlerler.
                sonraki_tokenler.append(bekleyen_prompt[b].pop(0))
                continue
            tok = ornekler_liste[b]
            uretilen_tokenler[b].append(tok)
            sonraki_tokenler.append(tok)
            gorulen_maske[b, tok] = True

        yeni_logits, durum = adim_toplu_maskeli(z, n_layer, n_embd, n_head, head_size, sonraki_tokenler, durum, aktif_maske)
        son_logits = torch.where(aktif_maske_t.unsqueeze(1), yeni_logits, son_logits)
        adim += 1

        if adim % ilerleme_adimi == 0:
            aktif_sayisi = sum(1 for x in bitti if not x)
            gecen = time.time() - uretim_baslangici
            print(f"{_ONEK} ({deneme_etiketi})   üretim: {adim}/{azami_yeni_token} adım, {aktif_sayisi}/{B} görev hâlâ aktif ({gecen:.1f} sn, {adim / max(gecen, 1e-6):.2f} adım/sn TÜM batch için).")

        if adim % kontrol_araligi != 0 and adim != azami_yeni_token:
            continue

        if bitis_zamani is not None and time.time() > bitis_zamani and not all(bitti):
            # NOT (Turkce): "SURE BUTCESI TUKENDI" burada YALNIZCA bu ÇAĞRIYA
            # verilen bitis_zamani (ör. attempt_1'e ayrılan YARI bütçe) icin
            # gecerlidir -- TOPLAM calisma_suresi_saniye (ornegin 11.5 saat)
            # DEGIL. Kullanicinin "daha 11.5 saat olmamis ki" itirazi tam bu
            # noktada: mesaj bunu acikca soylemedigi icin TUM kosunun
            # bitis sanılıyordu. Artik hangi bitis_zamani'nin doldugu ve
            # bunun TOPLAM butceyle AYNI olmayabilecegi acikca belirtiliyor.
            print(
                f"{_ONEK} ({deneme_etiketi})   BU ÇAĞRIYA AYRILAN SÜRE (bitis_zamani={time.strftime('%H:%M:%S', time.localtime(bitis_zamani))}) "
                f"DOLDU -- TOPLAM koşu bütçesi değil, yalnızca bu partiye/denemeye (attempt) ayrılan pay. "
                f"{adim} adımda, {sum(1 for x in bitti if not x)}/{B} görev HÂLÂ bitmemişken durduruluyor -- "
                f"bu partinin kalanı boş tahminle işaretlenecek (kapanış anında YENİ görev ADMİT EDİLMEZ)."
            )
            for b in range(B):
                if not bitti[b]:
                    _slot_sonucla_bitir(b)
            break

        for b in range(B):
            if bitti[b]:
                continue
            if bekleyen_prompt[b]:
                # Prompt'u HÂLÂ tüketiyor -- henüz hiç GERÇEK içerik
                # üretmedi, araç-çağrısı/yozlaşmış-döngü/İKAZ kontrolünün
                # bu slot için bir anlamı yok (uretilen_tokenler[b] hâlâ
                # boş). Diğer slotlar bu kontrolden ETKİLENMEDEN devam eder.
                continue
            metin_simdi = tokenizer.decode(uretilen_tokenler[b])
            # NOT (KRITIK -- kullanicinin gercek Kaggle transkriptinde
            # binlerce "Unknown tool"/basarisiz sonuc gorulmesinin GERCEK
            # kok nedeni burasiydi): arac_cagrilarini_ayikla, HER kontrolde
            # metin_simdi'nin TAMAMINI (ONCEKI turlarda ZATEN islenmis
            # cagrilar DAHIL) yeniden tarar -- bu, PARCALI/yarim JSON'un
            # bir sonraki kontrolde TAMAMLANMIS haliyle yakalanabilmesi
            # icin BILEREK boyle (kisa vadeli metin dilimi taramak bunu
            # kacirirdi). Ama bu, DAHA ONCE ZATEN calistirilmis/yanit
            # verilmis bir cagrinin (ozellikle basarisiz/execute_python
            # gibi bitti[b]=True YAPMAYAN her cagrinin) HER SONRAKI
            # kontrolde YENIDEN calistirilmasi anlamina geliyordu -- tek
            # bir execute_python cagrisi, o slot calismaya devam ettigi
            # surece DUZINELERCE kez tekrar tekrar sandbox'ta calisiyordu.
            # islenen_cagri_izleri[b], HER cagrinin (isim+argumanlar)
            # parmak izini tutar -- ayni cagri ikinci kez gorulunce
            # calistirilmadan/yanit verilmeden atlanir.
            cagrilar = arac_cagrilarini_ayikla(metin_simdi)
            if cagrilar:
                for cagri in cagrilar:
                    izi = json.dumps(cagri, sort_keys=True, default=str)
                    if izi in islenen_cagri_izleri[b]:
                        continue
                    islenen_cagri_izleri[b].add(izi)

                    sonuc = arac_cagrisini_yurut(cagri, defterler[b])
                    transkript_satiri_yaz({
                        "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                        "rol": "arac-sonucu", "arac": cagri.get("name"), "icerik": sonuc,
                    })
                    if cagri.get("name") == "submit_answer" and sonuc.get("success"):
                        sonuclar[b] = defterler[b].kaydedilen_cevap
                        bitti[b] = True
                    else:
                        # NOT (KRITIK -- kullanicinin ana sikayeti): bu
                        # ARTIK modele HIC geri beslenmiyordu -- model
                        # kendi execute_python ciktisini, submit_answer
                        # reddini ("once execute_python calistir" gibi)
                        # veya "Unknown tool" hatasini HICBIR ZAMAN
                        # GORMEDEN, tamamen KOR bicimde uretmeye devam
                        # ediyordu. coz_yurutucu.py'nin (ardisik/tek-gorev
                        # yolu) ZATEN yaptigi <tool_response> enjeksiyonu,
                        # burada da AYNI bicimde -- YALNIZCA bu slota,
                        # diger B-1 slota DOKUNMADAN -- uygulaniyor.
                        tool_yaniti_metni = rwkv_tek_mesaji_sar({"role": "user", "content": tool_response_mesaji_olustur(sonuc)})
                        tool_yaniti_tokenleri = tokenizer.encode(tool_yaniti_metni)
                        if tool_yaniti_tokenleri:
                            yeni_logit, durum = _ek_metni_tek_diziye_besle(
                                z, n_layer, n_embd, n_head, head_size, b, B, tool_yaniti_tokenleri, durum
                            )
                            son_logits[b] = yeni_logit
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
            # yeni_token'a kadar bekletir. Kullanıcının açık talebi: ÖNCE bu
            # slotta ZATEN kaydedilmiş GEÇERLİ bir cevap var mı diye bak --
            # varsa o cevabı KORU (döngüdeki gevezelik atılır, cevap atılmaz).
            # Yoksa üretileni SİL ve AYNI promptla (kuyruktan YENİ bir görev
            # ÇEKMEDEN) yeniden dene -- diğer B-1 slota HİÇ dokunulmaz. Sonsuz
            # döngüye karşı AZAMI_AYNI_PROMPT_YENIDEN_DENEME kez denenir,
            # sonra pes edilip (kuyruk varsa) slot normal admisyon yoluna girer.
            #
            # HIZ NOTU: _tekrara_kilitlenme_periyodu ESKİDEN p=4000..6000
            # arasını O(p) liste-dilimi karşılaştırmasıyla TARAYIP HER
            # kontrol_araligi'nde B aktif slotun HER BİRİ için milyonlarca
            # eleman karşılaştırması yapabiliyordu. Bu artık rwkv_native.py
            # içinde Rabin-Karp rolling-hash (bkz. oradaki not) ile O(pencere)
            # tek geçişte + O(1) aday karşılaştırmasıyla çalışıyor -- bu
            # yüzden ARTIK seyrekleştirmeye GEREK YOK, her kontrol_araligi'nde
            # (eskisi gibi) çalıştırmak hem ucuz hem de yozlaşmış döngüyü
            # daha ERKEN yakalıyor.
            periyot = _tekrara_kilitlenme_periyodu(uretilen_tokenler[b])
            if periyot is not None:
                if defterler[b].kaydedilen_cevap is not None:
                    sonuclar[b] = defterler[b].kaydedilen_cevap
                    print(
                        f"{_ONEK} ({deneme_etiketi})   {slot_gorev[b].name}: YOZLAŞMIŞ DÖNGÜ tespit edildi ama "
                        f"DAHA ÖNCE KAYDEDİLMİŞ geçerli bir cevap var -- o cevap KORUNUYOR, döngüdeki gevezelik atılıyor."
                    )
                    transkript_satiri_yaz({
                        "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                        "rol": "sistem-uyari", "icerik": f"yozlaşmış döngü (periyot={periyot}) ama önceden kaydedilmiş cevap korundu",
                    })
                    _slot_ilerlet(b)
                    continue

                yeniden_deneme_sayisi[b] += 1
                if yeniden_deneme_sayisi[b] <= AZAMI_AYNI_PROMPT_YENIDEN_DENEME:
                    print(
                        f"{_ONEK} ({deneme_etiketi})   {slot_gorev[b].name}: YOZLAŞMIŞ DÖNGÜ tespit edildi "
                        f"({periyot} token'lık alt-dizi 3 kez tekrarlandı), HENÜZ geçerli bir cevap YOK -- "
                        f"üretilen metin SİLİNİP AYNI promptla {yeniden_deneme_sayisi[b]}/{AZAMI_AYNI_PROMPT_YENIDEN_DENEME}. kez "
                        f"YENİDEN deneniyor (diğer {B - 1} slota DOKUNULMUYOR, kuyruktan YENİ görev ÇEKİLMEDİ)."
                    )
                    transkript_satiri_yaz({
                        "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                        "rol": "sistem-uyari",
                        "icerik": f"yozlaşmış döngü (periyot={periyot}), cevap yok, {yeniden_deneme_sayisi[b]}. kez aynı promptla yeniden deneniyor",
                    })
                    _slota_yeni_gorev_yukle(b, slot_gorev[b])
                    continue

                print(
                    f"{_ONEK} ({deneme_etiketi})   {slot_gorev[b].name}: YOZLAŞMIŞ DÖNGÜ {AZAMI_AYNI_PROMPT_YENIDEN_DENEME} kez "
                    f"aynı promptla yeniden denendi, HÂLÂ geçerli cevap yok -- pes ediliyor."
                )
                transkript_satiri_yaz({
                    "gorev": slot_gorev[b].name, "deneme": deneme_etiketi, "tur": 1,
                    "rol": "sistem-uyari", "icerik": f"yozlaşmış döngü {AZAMI_AYNI_PROMPT_YENIDEN_DENEME} yeniden denemeden sonra pes edildi",
                })
                _slot_ilerlet(b)
                continue
            if not ikaz_enjekte_edildi[b] and adim >= IKAZ_ESIGI_TOKEN:
                ikaz_enjekte_edildi[b] = True
                print(f"{_ONEK} ({deneme_etiketi})   {slot_gorev[b].name}: İKAZ enjekte ediliyor (yazma hakkı tükenmek üzere).")
                ikaz_tokenleri = tokenizer.encode(rwkv_tek_mesaji_sar({"role": "user", "content": IKAZ_METNI}))
                yeni_logit, durum = _ek_metni_tek_diziye_besle(z, n_layer, n_embd, n_head, head_size, b, B, ikaz_tokenleri, durum)
                son_logits[b] = yeni_logit
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
