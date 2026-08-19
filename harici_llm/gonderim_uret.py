import argparse
import atexit
import signal
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from arc import make_submission, read_tasks_from_single_file
from coz_yurutucu import gorevi_coz
from model_yapilandirmalari import MODEL_ONCELIK_SIRASI
from transkript import TRANSKRIPT_YOLU, transkript_satiri_yaz
from ttt_lora import lora_adaptoru_kur, temel_model_yukle, tokenizer_yukle

TEST_CHALLENGES_YOLU = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_test_challenges.json"

# YARISMA=False (deneme/kayıt modu) icin: gercek cevaplari BILEN iki kume
# (training + evaluation). read_tasks_from_single_file zaten solution_file
# destekliyor (arc.py) -- verilince task.test_example.output GERCEK cevapla
# doldurulur, boylece her cozumden sonra doğruluk KONTROL edilebilir.
# Kullanıcının açık talebi: "kayıt" (deneme) koşusu training VE evaluation
# kümesinin İKİSİNDEN de görev çekebilmeli -- yalnızca evaluation ile
# sınırlı DEĞİL.
TRAINING_CHALLENGES_YOLU = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_training_challenges.json"
TRAINING_SOLUTIONS_YOLU = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_training_solutions.json"
EVALUATION_CHALLENGES_YOLU = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_evaluation_challenges.json"
EVALUATION_SOLUTIONS_YOLU = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_evaluation_solutions.json"

# Verilen orijinal koddaki `global_end_time = time.time() + 12*3600 - 600`
# deseniyle aynı usul: 11 saat 30 dakikalık toplam çalışma bütçesi.
CALISMA_SURESI_SANIYE = 11 * 3600 + 30 * 60


class _SonuCuKaydedici:
    """Kod NASIL sona ererse ersin -- hata, dıştan kesme (SIGTERM/SIGINT),
    ya da süre bütçesinin dolması -- o ana kadar üretilmiş TÜM tahminlerin
    submission.json'a mutlaka yazılmasını garanti eder. Ana eğitim
    döngüsünde (main_egitim_dongusu.py) checkpoint'in HER durumda
    kaydolmasını sağlayan usulün aynısı: periyodik ara-kayıt + try/finally
    + sinyal yakalayıcı ile son-kayıt garantisi.

    GÖREV-ADI ANAHTARLI: kullanıcının gerçek Kaggle koşusunda gördüğü "5000/
    60000 adım ilerleme logu var ama submission.json BOMBOŞ" hatasının kök
    nedeni -- coklu_gpu_submission_uret ÖNCEDEN `ekle()`yi yalnızca TÜM 172
    görevlik attempt_1 koşusu (cozucu.coz() TAMAMEN dönene kadar) bittikten
    SONRA, sıraya göre çağırıyordu; koşu ORTASINDA çöken/kesilen bir süreçte
    tek bir `ekle()` bile hiç çalışmamış oluyordu. Artık her görev (SÜREKLİ
    ADMİSYON ile parti bitmeden de) bitirilir bitirilmez `guncelle(ad, ...)`
    ÇAĞRILABİLİR -- görev adına göre anahtarlanmış olduğu için sıra ÖNEMLİ
    DEĞİLDİR ve aynı görev ikinci kez (ör. attempt_2 ile) güncellenebilir."""

    def __init__(self, tasks: List[Any], cikti_yolu: str) -> None:
        self.tasks = tasks
        self.cikti_yolu = cikti_yolu
        self.tahminler_by_ad: Dict[str, List[Any]] = {}
        self._son_yazilan_sayi = -1
        self._kaydedildi = False

        atexit.register(self._son_kayit)
        signal.signal(signal.SIGTERM, self._sinyal_ile_kaydet)
        signal.signal(signal.SIGINT, self._sinyal_ile_kaydet)

    def guncelle(self, task_adi: str, attempt_1: Any, attempt_2: Optional[Any] = None) -> None:
        """Tek bir görevin tahminini (attempt_2 henüz yoksa attempt_1'in
        kopyasıyla) HEMEN kaydeder ve diske yazar -- görevin ait olduğu
        koşunun/partinin TAMAMEN bitmesini BEKLEMEZ."""
        self.tahminler_by_ad[task_adi] = [attempt_1, attempt_2 if attempt_2 is not None else attempt_1]
        self._ara_kayit()

    def ekle(self, task_adi: str, tahmin: List[Any]) -> None:
        self.tahminler_by_ad[task_adi] = tahmin
        self._ara_kayit()

    def _sirali_tahmin_listesi(self) -> List[List[Any]]:
        bos = [[[0, 0], [0, 0]], [[0, 0], [0, 0]]]
        return [self.tahminler_by_ad.get(task.name, bos) for task in self.tasks]

    def _bekleyen_gorevleri_bos_doldur(self) -> List[List[Any]]:
        return self._sirali_tahmin_listesi()

    def _ara_kayit(self) -> None:
        # Her görevden sonra diske yazılır; süreç o an ölse bile o ana
        # kadarki tüm sonuçlar submission.json'da kalır.
        if len(self.tahminler_by_ad) == self._son_yazilan_sayi:
            return
        tam_liste = self._sirali_tahmin_listesi()
        try:
            make_submission(self.tasks, tam_liste, path=self.cikti_yolu)
            self._son_yazilan_sayi = len(self.tahminler_by_ad)
        except Exception as yazma_hatasi:
            print(f"[gonderim_uret] ARA KAYIT HATASI (yoksayılıp devam edilecek): {yazma_hatasi}")

    def _son_kayit(self) -> None:
        if self._kaydedildi:
            return
        self._kaydedildi = True
        print(
            f"[gonderim_uret] SON KAYIT: {len(self.tahminler_by_ad)}/{len(self.tasks)} görev tamamlanmış "
            f"haliyle '{self.cikti_yolu}' yazılıyor..."
        )
        tam_liste = self._sirali_tahmin_listesi()
        make_submission(self.tasks, tam_liste, path=self.cikti_yolu)
        print(f"[gonderim_uret] SON KAYIT tamamlandı: '{self.cikti_yolu}'.")

    def _sinyal_ile_kaydet(self, signum: int, frame: Any) -> None:
        print(f"[gonderim_uret] Sinyal {signum} alındı, mevcut sonuçlar kaydedilip çıkılıyor...")
        self._son_kayit()
        raise SystemExit(128 + signum)


def ana_model_ile_dene_yedekle(oncelik_sirasi: List[str] = MODEL_ONCELIK_SIRASI) -> Tuple[str, Any, Any]:
    """oncelik_sirasi[0] ANA modeldir; yuklemesi basarisiz olursa (dosya
    eksik/bozuk, OOM, mimari desteklenmiyor vb.) sirayla sonraki yedek
    modele duser. Hicbiri yuklenemezse son hatayi firlatir."""
    son_hata: Optional[Exception] = None
    for i, aday_aile in enumerate(oncelik_sirasi):
        etiket = "ANA MODEL" if i == 0 else f"YEDEK MODEL #{i}"
        print(f"[gonderim_uret] {etiket} deneniyor: '{aday_aile}' (yerel dosya, internet KAPALI)...")
        try:
            base_model = temel_model_yukle(aday_aile)
            tokenizer = tokenizer_yukle(aday_aile)
            print(f"[gonderim_uret] '{aday_aile}' başarıyla yüklendi, bu model kullanılacak.")
            return aday_aile, base_model, tokenizer
        except Exception as exc:
            print(f"[gonderim_uret] '{aday_aile}' yüklenemedi: {exc}")
            son_hata = exc
    raise RuntimeError(
        f"Öncelik sırasındaki hiçbir model yüklenemedi ({oncelik_sirasi}). Son hata: {son_hata}"
    )


def _dogrulugu_kontrol_et(task: Any, sonuc: Dict[str, Any]) -> None:
    """YARISMA=False (deneme) modunda: gercek cevap (task.test_example.output,
    solution_file'dan doldurulmus) ile attempt_1/2'yi karsilastirir, hem
    dogruluk hem de GERCEKTEN submit_answer'in basariyla cagrilip
    cagrilmadigini (bos yer tutucuya dusup dusmedigini) hem stdout'a hem
    transkript.jsonl'e yazar."""
    gercek_cevap = task.test_example.output.tolist()
    sonuclar = {}
    for etiket in ("attempt_1", "attempt_2"):
        try:
            dogru_mu = np.array_equal(np.array(sonuc[etiket], dtype=object).astype(int), np.array(gercek_cevap))
        except (ValueError, TypeError):
            dogru_mu = False
        sonuclar[etiket] = {
            "dogru_mu": dogru_mu,
            "gercekten_submit_edildi_mi": sonuc.get(f"{etiket}_gonderildi_mi", False),
        }

    print(
        f"[gonderim_uret]   DEGERLENDIRME [{task.name}]: "
        f"attempt_1 doğru={sonuclar['attempt_1']['dogru_mu']} "
        f"(gerçekten submit edildi={sonuclar['attempt_1']['gercekten_submit_edildi_mi']}), "
        f"attempt_2 doğru={sonuclar['attempt_2']['dogru_mu']} "
        f"(gerçekten submit edildi={sonuclar['attempt_2']['gercekten_submit_edildi_mi']})"
    )
    transkript_satiri_yaz({
        "gorev": task.name, "rol": "degerlendirme",
        "icerik": {"gercek_cevap": gercek_cevap, **sonuclar},
    })


def _gorevleri_yukle(yarisma: bool, azami_soru_sayisi: Optional[int] = None) -> List[Any]:
    """`azami_soru_sayisi` verilirse (kullanıcının açık talebi -- deneme
    koşuları tüm kümeyle çok uzun sürüyor): toplam görev sayısı bu
    değerden BÜYÜK veya EŞİTSE hepsi kullanılır (davranış değişmez);
    KÜÇÜKSE ilk `azami_soru_sayisi` görev alınır (tasks[:N] -- kümenin
    BAŞINDAN seçim). None ise (varsayılan) davranış hiç değişmez.

    GÜVENLİK KİLİDİ (kullanıcının açık talebi): `yarisma=True` (GERÇEK
    yarışma koşusu) ise `azami_soru_sayisi` NE OLURSA OLSUN GÖRMEZDEN
    GELİNİR -- notebook_giris.py'de deneme için bırakılmış/unutulmuş bir
    SORU_SAYISI (ör. ortam değişkeninden gelen), gerçek yarışma
    gönderiminin YALNIZCA birkaç göreve indirgenerek eksik bir
    submission.json üretmesine ASLA yol açamaz. Yalnızca YARISMA=False
    (deneme/değerlendirme modu) iken kısaltma uygulanır."""
    if yarisma and azami_soru_sayisi is not None:
        print(
            f"[gonderim_uret] GÜVENLİK: YARISMA=True iken azami_soru_sayisi={azami_soru_sayisi} GÖRMEZDEN "
            f"GELİNİYOR -- gerçek yarışma koşusunda SORU_SAYISI ne olursa olsun TÜM sorular çözülür."
        )
        azami_soru_sayisi = None
    if yarisma:
        print(f"[gonderim_uret] YARISMA=True: gerçek yarışma test kümesi kullanılıyor (cevaplar bilinmiyor).")
        tasks = read_tasks_from_single_file(TEST_CHALLENGES_YOLU, test=True)
        print(f"[gonderim_uret] {len(tasks)} alt-görev bulundu: {TEST_CHALLENGES_YOLU}")
    else:
        print(
            f"[gonderim_uret] YARISMA=False: DENEME/KAYIT modu -- training + evaluation kümeleri (gerçek "
            f"cevaplar BİLİNİYOR) kullanılıyor, her görevden sonra doğruluk otomatik kontrol edilip loglanacak."
        )
        training_tasks = read_tasks_from_single_file(
            TRAINING_CHALLENGES_YOLU, solution_file=TRAINING_SOLUTIONS_YOLU,
        )
        print(f"[gonderim_uret] {len(training_tasks)} alt-görev bulundu: {TRAINING_CHALLENGES_YOLU} (+ çözümler: {TRAINING_SOLUTIONS_YOLU})")
        evaluation_tasks = read_tasks_from_single_file(
            EVALUATION_CHALLENGES_YOLU, solution_file=EVALUATION_SOLUTIONS_YOLU,
        )
        print(f"[gonderim_uret] {len(evaluation_tasks)} alt-görev bulundu: {EVALUATION_CHALLENGES_YOLU} (+ çözümler: {EVALUATION_SOLUTIONS_YOLU})")
        # NOT (Turkce): training ONCE, evaluation SONRA -- azami_soru_sayisi
        # ile kismi secim yapilirken (asagida) "kumenin BASINDAN" ilk once
        # training'den, o tukenirse evaluation'dan alinir.
        tasks = training_tasks + evaluation_tasks
        print(f"[gonderim_uret] toplam {len(tasks)} alt-görev (training+evaluation birleşik).")

    if azami_soru_sayisi is not None and azami_soru_sayisi < len(tasks):
        print(
            f"[gonderim_uret] SORU_SAYISI={azami_soru_sayisi} < toplam {len(tasks)} alt-görev -- "
            f"kümenin BAŞINDAN yalnızca ilk {azami_soru_sayisi} görev alınıyor (deneme koşusunu kısaltmak için)."
        )
        tasks = tasks[:azami_soru_sayisi]
    elif azami_soru_sayisi is not None:
        print(
            f"[gonderim_uret] SORU_SAYISI={azami_soru_sayisi} >= toplam {len(tasks)} alt-görev -- "
            f"tümü kullanılıyor, kısaltma yapılmadı."
        )
    return tasks


def coklu_gpu_submission_uret(
    model_ailesi: str = None,
    cikti_yolu: str = "submission.json",
    calisma_suresi_saniye: float = CALISMA_SURESI_SANIYE,
    yarisma: bool = True,
    azami_gpu: int = 4,
    toplu_mod: bool = True,
    b_boyutu: int = 128,
    azami_soru_sayisi: Optional[int] = None,
    azami_yeni_token: Optional[int] = None,
    cihaz_modu: str = "gpu",
) -> Dict[str, Any]:
    """submission_uret()'in coklu-GPU varyantı -- bkz. coklu_gpu.py
    başındaki not. Aynı modelin GPU başına BAĞIMSIZ bir kopyası yüklenir.

    `azami_soru_sayisi` (kullanıcının açık talebi -- SORU_SAYISI):
    verilirse `_gorevleri_yukle`'ye AYNEN aktarılır -- toplam görev
    sayısı bundan büyük/eşitse hepsi kullanılır, küçükse kümenin
    BAŞINDAN yalnızca bu kadarı alınır (deneme koşularını kısaltmak
    için). None ise (varsayılan) davranış hiç değişmez.

    `azami_yeni_token` (kullanıcının açık talebi -- KONUS): görev başına
    üretilecek AZAMİ token sayısı (coz_yurutucu_toplu.toplu_gorevleri_coz'a
    aynen aktarılır). None ise (varsayılan) altta yatan 60000 sabiti
    DEĞİŞMEDEN kullanılır -- 60000 ile deneme yapmak çok yavaş olduğu
    için, deneme koşularında bunu ör. 1000'e düşürmek amaçlanır.

    `cihaz_modu` (kullanıcının açık talebi -- CIHAZ, GPU kotası
    tükendiğinde bile çalışabilmek için) `dort_kopya_yukle`'ye AYNEN
    aktarılır: "gpu" (varsayılan, ESKİ davranış -- GERÇEK GPU yoksa
    RuntimeError, CPU'ya SESSİZCE düşülmez), "cpu" (GPU sınaması hiç
    yapılmadan doğrudan TEK bir CPU kopyası), "serbest" (önce GERÇEK
    GPU dener, yoksa CPU'ya düşer). CPU modunda VRAM ölçümü ANLAMSIZ
    olduğundan (torch.cuda.* çağrıları CUDA'sız bir makinede zaten
    çökerdi) vram_kesifcileri HİÇ kurulmuyor -- CokluGPUTopluCozucu
    sabit `b_boyutu`yu kullanır.

    toplu_mod=True (varsayılan): her GPU, kendisine atanan görevleri TEK
    TEK değil, B TANESİNİ AYNI ANDA (gerçek batched adım zinciriyle, bkz.
    coz_yurutucu_toplu.toplu_gorevleri_coz) çözer -- B, o GPU'nun gerçek
    VRAM ölçümüyle keşfedilen güvenli B'sidir (vram_izleyici.
    VramTabanliBKesifcisi, baslangic_b=b_boyutu). toplu_mod=False: eski
    davranış (GPU başına aynı anda TEK görev, bkz. CokluGPUCozucu) --
    yalnızca geriye dönük uyumluluk/karşılaştırma için tutulur.
    NOT: bu yol salt-çıkarımdır (görev-başına TTT/state-tuning burada
    YOK -- coz_yurutucu.gorevi_coz'un tek-GPU yolunda kalır)."""
    from model_yapilandirmalari import RWKV
    from coklu_gpu import CokluGPUCozucu, CokluGPUTopluCozucu, dort_kopya_yukle

    model_ailesi = model_ailesi or RWKV
    bitis_zamani = time.time() + calisma_suresi_saniye
    print(
        f"[gonderim_uret] [ÇOKLU-GPU] Çalışma bütçesi: {calisma_suresi_saniye / 3600:.2f} saat "
        f"(bitiş: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bitis_zamani))}) | toplu_mod={toplu_mod}"
    )

    tasks = _gorevleri_yukle(yarisma, azami_soru_sayisi=azami_soru_sayisi)
    kaydedici = _SonuCuKaydedici(tasks, cikti_yolu)
    # KONUS (kullanıcının açık talebi): None ise altta yatan sınıfların
    # kendi varsayılanı (60000) DOKUNULMADAN kullanılır -- bu yüzden
    # sadece verilmişse kwargs'a eklenir, aksi halde hiç geçilmez.
    azami_yeni_token_kwargs = {} if azami_yeni_token is None else {"azami_yeni_token": azami_yeni_token}

    # HIZ (kullanıcının açık talebi -- "4'ten az soru gönderirsem kaç soru
    # varsa o kadar GPU'ya model kopyalansın, geri kalanlarına
    # kopyalanmasın"): görev sayısı zaten BURADA (model yüklenmeden ÖNCE)
    # biliniyor -- azami_gpu'yu görev sayısının ÜZERİNE ÇIKARMANIN hiçbir
    # faydası yok, yalnızca hiç iş almayacak GPU'lara boşuna model kopyası
    # yükleyip (her kopya onlarca saniye/GB VRAM tutar) zaman kaybettirir.
    # len(tasks)==0 durumunda dokunulmuyor -- o zaten ayrı bir uç durum.
    if tasks and azami_gpu > len(tasks):
        print(
            f"[gonderim_uret] {len(tasks)} görev var, azami_gpu={azami_gpu} idi -- "
            f"gereksiz GPU kopyalamasını önlemek için azami_gpu={len(tasks)}'e düşürüldü "
            f"(görev sayısından fazla GPU'ya model yüklemenin faydası yok)."
        )
        azami_gpu = len(tasks)

    try:
        modeller, tokenizer, gpu_etiketleri = dort_kopya_yukle(model_ailesi, azami_gpu=azami_gpu, cihaz_modu=cihaz_modu)
        if toplu_mod:
            # CIHAZ='cpu' (ya da 'serbest' ile CPU'ya düşüldüyse): VRAM
            # ölçümü burada anlamsız -- gpu_etiketleri=["cpu"] iken
            # VramTabanliBKesifcisi'nin torch.cuda.* çağrıları CUDA'sız
            # bir makinede zaten çökerdi. Bu durumda vram_kesifcileri HİÇ
            # kurulmuyor, CokluGPUTopluCozucu sabit b_boyutu'yu kullanır.
            if gpu_etiketleri == ["cpu"]:
                vram_kesifcileri = None
            else:
                from vram_izleyici import VramTabanliBKesifcisi
                vram_kesifcileri = [VramTabanliBKesifcisi(etiket, baslangic_b=b_boyutu) for etiket in gpu_etiketleri]
            cozucu = CokluGPUTopluCozucu(
                modeller, tokenizer, b_boyutu=b_boyutu, gpu_etiketleri=gpu_etiketleri,
                vram_kesifcileri=vram_kesifcileri,
                # YARISMA=False (deneme) modunda ayrıntılı ilerleme logu
                # otomatik açılır -- kullanıcının "800 saniyedir hiç log
                # yok" diye fark ettiği sessiz boşluğu (batched prefill'in
                # KENDİSİ hiç ilerleme raporlamıyordu) kapatır.
                ayrintili_log=not yarisma,
                **azami_yeni_token_kwargs,
            )
        else:
            cozucu = CokluGPUCozucu(modeller, tokenizer, gpu_etiketleri=gpu_etiketleri, **azami_yeni_token_kwargs)
        # ARC ödül kuralı görev başına 2 BAĞIMSIZ deneme hakkı tanır, ve bir
        # ara sürümde bunu GERÇEKTEN kullanmak için bütçeyi ikiye bölüp
        # attempt_2'yi bağımsız bir ikinci koşu yapmıştık. KULLANICININ AÇIK
        # TALEBİYLE bu GERİ ALINDI: RWKV'nin gerçek başarı oranı o kadar
        # düşük (gerçek bir koşuda 259 görevden yalnızca 1 tanesi attempt_1'i
        # bile bitirebilmişti) ki bütçenin yarısını attempt_1'e ayırmak,
        # işi ortasından kesip görevlerin çoğunun HİÇ bitirilememesine yol
        # açıyordu. Artık TÜM bütçe (bitis_zamani) TEK bir koşuya (attempt_1)
        # veriliyor; attempt_2 HİÇ ayrı bir koşu YAPMIYOR, doğrudan attempt_1
        # ile AYNI cevabı taşıyor (kaydedici.guncelle'nin attempt_2=None
        # varsayılanı zaten bunu yapar).
        def _attempt1_tamamlandi(task_adi: str, sonuc: Dict[str, Any]) -> None:
            kaydedici.guncelle(task_adi, sonuc["attempt_1"])

        sonuclar = cozucu.coz(tasks, bitis_zamani=bitis_zamani, tamamlanma_geri_cagirma=_attempt1_tamamlandi)
        sonuclar_2: Dict[str, Dict[str, Any]] = {}

        if not yarisma:
            for task in tasks:
                sonuc = sonuclar.get(task.name, {"attempt_1": [[0, 0], [0, 0]], "attempt_1_gonderildi_mi": False})
                attempt_1 = sonuc["attempt_1"]
                sonuc_2 = sonuclar_2.get(task.name)
                if sonuc_2 is not None and sonuc_2.get("attempt_1_gonderildi_mi"):
                    attempt_2 = sonuc_2["attempt_1"]
                    attempt_2_gonderildi_mi = True
                else:
                    attempt_2 = attempt_1
                    attempt_2_gonderildi_mi = sonuc.get("attempt_1_gonderildi_mi", False)
                _dogrulugu_kontrol_et(task, {
                    "attempt_1": attempt_1, "attempt_2": attempt_2,
                    "attempt_1_gonderildi_mi": sonuc.get("attempt_1_gonderildi_mi", False),
                    "attempt_2_gonderildi_mi": attempt_2_gonderildi_mi,
                })
    finally:
        kaydedici._son_kayit()

    submission = make_submission(tasks, kaydedici._bekleyen_gorevleri_bos_doldur(), path=cikti_yolu)
    print(f"[gonderim_uret] [ÇOKLU-GPU] Yazıldı: {cikti_yolu} ({len(submission)} görev)")
    return submission


def submission_uret(
    model_ailesi: Optional[str] = None,
    oncelik_sirasi: List[str] = MODEL_ONCELIK_SIRASI,
    cikti_yolu: str = "submission.json",
    cogaltma_n: int = 16,
    ttt_adim_sayisi: int = 20,
    calisma_suresi_saniye: float = CALISMA_SURESI_SANIYE,
    yarisma: bool = True,
) -> Dict[str, Any]:

    bitis_zamani = time.time() + calisma_suresi_saniye
    print(
        f"[gonderim_uret] Çalışma bütçesi: {calisma_suresi_saniye / 3600:.2f} saat "
        f"(bitiş: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bitis_zamani))})"
    )
    print(
        f"[gonderim_uret] Modelin GERÇEKTEN ürettiği her metin (araç çağırdı/çağırmadı fark etmeksizin) "
        f"'{TRANSKRIPT_YOLU}' dosyasına ANINDA (flush+fsync ile) yazılıyor -- bir görev boş tahminle "
        f"bitse bile o süre boyunca model ne 'konuştu' orada görülebilir."
    )

    tasks = _gorevleri_yukle(yarisma)

    kaydedici = _SonuCuKaydedici(tasks, cikti_yolu)

    try:
        if model_ailesi is not None:
            print(f"[gonderim_uret] '{model_ailesi}' ailesi icin yerel model yukleniyor (internet KAPALI)...")
            base_model = temel_model_yukle(model_ailesi)
            tokenizer = tokenizer_yukle(model_ailesi)
        else:
            model_ailesi, base_model, tokenizer = ana_model_ile_dene_yedekle(oncelik_sirasi)

        lora_model = lora_adaptoru_kur(base_model, model_ailesi)

        varsayilan_lora_agirliklari = None
        if hasattr(lora_model, "durum_ayari"):
            varsayilan_lora_agirliklari = lora_model.durum_anlik_goruntusu_al()
        elif hasattr(lora_model, "peft_config"):
            from peft import get_peft_model_state_dict

            varsayilan_lora_agirliklari = get_peft_model_state_dict(lora_model, adapter_name="default")
            varsayilan_lora_agirliklari = {k: v.clone().detach() for k, v in varsayilan_lora_agirliklari.items()}

        baslangic = time.time()

        for i, task in enumerate(tasks, start=1):
            if time.time() > bitis_zamani:
                print(
                    f"[gonderim_uret] Çalışma süresi bütçesi doldu "
                    f"({(time.time() - baslangic) / 3600:.2f} saat), kalan {len(tasks) - i + 1} görev "
                    f"boş tahminle bırakılıp durduruluyor."
                )
                break

            try:
                sonuc = gorevi_coz(
                    lora_model, tokenizer, model_ailesi, task,
                    varsayilan_lora_agirliklari=varsayilan_lora_agirliklari,
                    cogaltma_n=cogaltma_n, ttt_adim_sayisi=ttt_adim_sayisi,
                )
                kaydedici.ekle(task.name, [sonuc["attempt_1"], sonuc["attempt_2"]])
                if not yarisma:
                    _dogrulugu_kontrol_et(task, sonuc)
            except Exception as exc:
                print(f"[gonderim_uret] Görev {task.name} başarısız, boş tahmin yazılıyor: {exc}")
                kaydedici.ekle(task.name, [[[0, 0], [0, 0]], [[0, 0], [0, 0]]])

            gecen = time.time() - baslangic
            print(f"[gonderim_uret] ({i}/{len(tasks)}) {task.name} tamamlandı | toplam süre: {gecen:.1f} sn")

    finally:
        # Hata ile mi, sinyal ile mi, süre bitmesiyle mi, yoksa normal
        # tamamlanma ile mi buraya gelindiği fark etmez -- o ana kadarki
        # tüm sonuçlar burada KESİN olarak diske yazılır.
        kaydedici._son_kayit()

    submission = make_submission(tasks, kaydedici._bekleyen_gorevleri_bos_doldur(), path=cikti_yolu)
    print(f"[gonderim_uret] Yazıldı: {cikti_yolu} ({len(submission)} görev)")
    return submission


def _cli() -> None:
    ayristirici = argparse.ArgumentParser(description="ARC-AGI 2026 TTT+LoRA+arac-cagirma gönderim üretici")
    ayristirici.add_argument(
        "--model_ailesi", type=str, default=None, choices=["rwkv", "mamba", "falcon_mamba"],
        help="Belirtilmezse MODEL_ONCELIK_SIRASI'na göre ana model denenir, başarısız olursa yedeğe düşer.",
    )
    ayristirici.add_argument("--cikti", type=str, default="submission.json")
    ayristirici.add_argument("--cogaltma_n", type=int, default=16)
    ayristirici.add_argument("--ttt_adim_sayisi", type=int, default=20)
    ayristirici.add_argument("--calisma_suresi_saniye", type=float, default=CALISMA_SURESI_SANIYE)
    ayristirici.add_argument(
        "--yarisma", type=lambda s: s.lower() != "false", default=True,
        help="False verilirse: değerlendirme kümesi (cevaplar bilinen arc-agi_evaluation_*) kullanılır, "
             "her görevden sonra doğruluk otomatik kontrol edilip loglanır.",
    )
    args = ayristirici.parse_args()

    submission_uret(
        model_ailesi=args.model_ailesi, cikti_yolu=args.cikti,
        cogaltma_n=args.cogaltma_n, ttt_adim_sayisi=args.ttt_adim_sayisi,
        calisma_suresi_saniye=args.calisma_suresi_saniye, yarisma=args.yarisma,
    )


if __name__ == "__main__":
    _cli()
