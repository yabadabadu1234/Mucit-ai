"""
"Padişah/vezir" modeli: N GPU'da modelin N bağımsız kopyası, GERÇEK OS
thread'leriyle (threading.Thread) TAMAMEN bağımsız çalışır.

Token-seviyesinde round-robin/adım senkronu YOKTUR (kullanıcının açıkça
reddettiği yaklaşım) -- her "vezir" (GPU thread'i) kendisine atanan görevi
BAŞTAN SONA, kendi hızında, kimseyi beklemeden çözer. Padişah (ana süreç):

  1) vezir 1'i (thread) BAŞLATIR ve HEMEN -- vezir 1'in bitmesini hiç
     BEKLEMEDEN -- vezir 2'yi başlatır, sonra 3'ü, sonra 4'ü. Hiçbiri
     diğerinin bitmesini beklemez.
  2) "Kapıyı açık bırakır": her vezir, kendi göreviyle bitince ORTAK İŞ
     KUYRUĞUNDAN (queue.Queue, thread-güvenli) bir sonraki görevi kendisi
     alır -- padişah tek tek iş dağıtmaz, kimse boş beklemez, iş dinamik
     olarak yeniden dağıtılır ("hünkarım tamamladım" deyince "al sana
     yeni iş").
  3) Padişah yalnızca TÜM vezirlerin (nihayetinde) işini bitirmesini
     bekler (join) -- aralarında hiçbir sıra/bariyer/senkron YOKTUR.
"""
import multiprocessing
import queue
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from arc import Task
from coz_yurutucu import BOS_TAHMIN
from model_yapilandirmalari import RWKV


def _cihaz_etiketlerini_belirle(azami_gpu: int, cihaz_modu: str) -> List[str]:
    """`dort_kopya_yukle`'nin GPU/CPU KARAR mantığının, MODEL YÜKLEMEDEN
    ayrıştırılmış hali -- yalnızca HANGİ cihaz etiketlerinin (["cuda:0",
    "cuda:1", ...] ya da ["cpu"]) kullanılacağına karar verir, hiçbir
    model yüklemez. `CokluGPUTopluCozucu` artık modeli PADİŞAH'ta değil
    HER SÜRECİN KENDİSİNDE yüklediği için (bkz. dosya başındaki not) bu
    ayrım gerekli hale geldi -- padişahın modele hiç ihtiyacı yok, yalnızca
    kaç/hangi cihaza süreç başlatacağını bilmesi yeterli."""
    if cihaz_modu == "cpu":
        print("[coklu_gpu] cihaz_modu='cpu' -- GPU sınaması yapılmadan TEK bir 'cpu' süreci kullanılacak.")
        return ["cpu"]

    from gpu_tespit import kullanilabilir_gpu_indeksleri
    gpu_indeksleri = kullanilabilir_gpu_indeksleri(azami_gpu=azami_gpu)
    if not gpu_indeksleri:
        if cihaz_modu == "serbest":
            print("[coklu_gpu] cihaz_modu='serbest': derin sınamadan geçen GERÇEK GPU yok -- 'cpu'ya düşülüyor.")
            return ["cpu"]
        raise RuntimeError(
            "coklu_gpu: derinlemesine sınamadan (gerçek matmul) GEÇEN hiçbir GPU yok "
            "-- torch GPU görüyor olsa bile hiçbiri fiilen kullanılabilir değil."
        )
    return [f"cuda:{i}" for i in gpu_indeksleri]


def dort_kopya_yukle(model_ailesi: str = RWKV, azami_gpu: int = 4, cihaz_modu: str = "gpu"):
    """Modelin GPU başına BAĞIMSIZ bir kopyasını yükler (ağırlıklar
    paylaşılmaz -- her GPU kendi VRAM'inde tam bir kopya taşır).

    NOT: bu fonksiyon artık YALNIZCA geriye dönük uyumluluk için
    (CokluGPUCozucu -- eski, thread tabanlı, salt karşılaştırma amaçlı
    yol) tutuluyor. Gerçek üretim yolu (CokluGPUTopluCozucu) artık
    modeli PADİŞAH sürecinde DEĞİL, her GPU için AYRI bir OS SÜRECİNİN
    (multiprocessing.Process) kendi içinde yüklüyor -- bkz. dosya
    başındaki not."""
    from rwkv_native import native_rwkv_yukle, rwkv_ham_pth_mi
    from ttt_lora import tokenizer_yukle, yerel_model_yolu

    yol = yerel_model_yolu(model_ailesi)
    if not rwkv_ham_pth_mi(yol):
        raise RuntimeError("coklu_gpu şu an yalnızca native RWKV (.pth) yolunu destekliyor.")

    gpu_etiketleri = _cihaz_etiketlerini_belirle(azami_gpu, cihaz_modu)
    if gpu_etiketleri == ["cpu"]:
        print("[coklu_gpu] TEK bir model kopyası 'cpu' cihazına yükleniyor (yavaş olacaktır).")
        model = native_rwkv_yukle(yol, cihaz="cpu")
        tokenizer = tokenizer_yukle(model_ailesi)
        print("[coklu_gpu] CPU'da modelin TEK kopyası hazır.")
        return [model], tokenizer, ["cpu"]

    modeller = []
    for etiket in gpu_etiketleri:
        print(f"[coklu_gpu] {etiket} için model kopyası yükleniyor...")
        modeller.append(native_rwkv_yukle(yol, cihaz=etiket))

    tokenizer = tokenizer_yukle(model_ailesi)
    print(f"[coklu_gpu] {len(modeller)} GPU'da modelin BAĞIMSIZ birer kopyası hazır: {gpu_etiketleri}")
    return modeller, tokenizer, gpu_etiketleri


def padisah_vezir_havuzuyla_coz(
    gpu_sayisi: int,
    tasks: List[Task],
    gorevi_coz: Callable[[int, Task], Dict[str, Any]],
    bitis_zamani: Optional[float] = None,
    etiketler: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Genel amaçlı padişah/vezir iş havuzu -- `gorevi_coz(gpu_index, task)`
    RWKV'ye özgü değildir, bu yüzden testlerde de gerçek threading
    davranışını (senkronsuz dispatch + dinamik yeniden dağıtım) RWKV
    yüklemeden doğrudan sınamak mümkündür.

    `gpu_index` burada yalnızca `gorevi_coz`'un modeller listesindeki
    KONUM (0..gpu_sayisi-1) -- GERÇEK cuda cihaz numarasıyla AYNI OLMAK
    ZORUNDA DEĞİLDİR (bazı GPU'lar gpu_tespit.kullanilabilir_gpu_indeksleri
    tarafından elenmiş olabilir, ör. yalnızca cuda:0 ve cuda:2 çalışıyorsa
    konum 0->cuda:0, konum 1->cuda:2'dir). Log/etiket için GERÇEK cihaz
    adı `etiketler[gpu_index]`'ten okunur; verilmezse geriye dönük uyumluluk
    için "cuda:{gpu_index}" varsayılır."""
    gorev_kuyrugu: "queue.Queue[Task]" = queue.Queue()
    for task in tasks:
        gorev_kuyrugu.put(task)

    sonuclar: Dict[str, Dict[str, Any]] = {}
    kilit = threading.Lock()
    toplam = len(tasks)
    baslangic = time.time()

    def _etiket(gpu_index: int) -> str:
        if etiketler is not None and gpu_index < len(etiketler):
            return etiketler[gpu_index]
        return f"cuda:{gpu_index}"

    def _vezir(gpu_index: int) -> None:
        while True:
            if bitis_zamani is not None and time.time() > bitis_zamani:
                return
            try:
                task = gorev_kuyrugu.get_nowait()
            except queue.Empty:
                return  # kuyrukta iş kalmadı -- bu vezir görevini tamamladı
            try:
                sonuc = gorevi_coz(gpu_index, task)
            except Exception as hata:
                print(f"[coklu_gpu] ({_etiket(gpu_index)}) {task.name} başarısız: {hata}")
                sonuc = {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False}
            with kilit:
                sonuclar[task.name] = sonuc
                gecen = time.time() - baslangic
                print(f"[coklu_gpu] ({_etiket(gpu_index)}) ({len(sonuclar)}/{toplam}) {task.name} tamamlandı | toplam süre: {gecen:.1f} sn")
            gorev_kuyrugu.task_done()

    veziler = []
    for gpu_index in range(gpu_sayisi):
        # HER vezir HEMEN işbaşı yapar; padişah bir sonrakini başlatmadan
        # ÖNCEKİ vezirin bitmesini ASLA beklemez (thread.start() bloklamaz).
        vezir = threading.Thread(target=_vezir, args=(gpu_index,), daemon=True, name=f"vezir-{_etiket(gpu_index)}")
        vezir.start()
        veziler.append(vezir)

    # Kapı açık bırakılır: padişah yalnızca TÜM vezirlerin (nihayetinde)
    # işini bitirmesini bekler -- aralarında hiçbir sıra/engelleme yoktur.
    for vezir in veziler:
        vezir.join()

    for task in tasks:
        if task.name not in sonuclar:
            sonuclar[task.name] = {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False}

    return sonuclar


class CokluGPUCozucu:
    """N GPU'daki N bağımsız model kopyasını padisah_vezir_havuzuyla_coz
    ile kullanır: her vezir kendi GPU'sunda, coz_yurutucu._tek_deneme_uret_
    artimli ile (tek-GPU yolla AYNI, kanıtlanmış mantık) görevi baştan
    sona kendi hızında çözer."""

    def __init__(self, modeller: List[Any], tokenizer: Any, azami_tur: int = 1,
                 azami_yeni_token: int = 60000, gpu_etiketleri: Optional[List[str]] = None):
        self.modeller = modeller
        self.tokenizer = tokenizer
        self.azami_tur = azami_tur
        self.azami_yeni_token = azami_yeni_token
        # GERÇEK cuda cihaz adları (ör. ["cuda:0", "cuda:2"]) -- verilmezse
        # modeller listesindeki her elemanın kendi .device'ından okunur,
        # bu da olmazsa (çok eski/farklı sarmalayıcı) konumsal isim kullanılır.
        self.gpu_etiketleri = gpu_etiketleri or [
            str(getattr(m, "device", f"gpu{i}")) for i, m in enumerate(modeller)
        ]

    def coz(self, tasks: List[Task], bitis_zamani: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        from coz_yurutucu import _tek_deneme_uret_artimli

        def _gorevi_coz(gpu_index: int, task: Task) -> Dict[str, Any]:
            cevap = _tek_deneme_uret_artimli(
                self.modeller[gpu_index], self.tokenizer, RWKV, task,
                self.azami_tur, self.azami_yeni_token, self.gpu_etiketleri[gpu_index],
            )
            return {
                "attempt_1": cevap if cevap is not None else BOS_TAHMIN,
                "attempt_1_gonderildi_mi": cevap is not None,
            }

        return padisah_vezir_havuzuyla_coz(
            len(self.modeller), tasks, _gorevi_coz, bitis_zamani=bitis_zamani, etiketler=self.gpu_etiketleri,
        )


def _gorevleri_esit_dagit(tasks: List[Task], gpu_sayisi: int) -> List[List[Task]]:
    """Padişah, İŞ BAŞLAMADAN ÖNCE, CPU'da, görevleri gpu_sayisi kadar
    PAYA MÜMKÜN OLDUĞUNCA EŞİT böler (round-robin -- kalan varsa bazı
    paylara yalnızca BİR FAZLA düşer, ondan fazlası asla). Bu, ORTAK
    tek bir kuyruğun yol açacağı şu soruna karşı bir önlemdir: 240
    görev, 4 GPU, B=128 iken paylaşımlı bir kuyruktan çekilseydi ilk 2
    hızlı vezir kuyruğun TAMAMINI (240) kapıp diğer 2'sini HİÇ İŞ
    ALAMADAN atıl bırakabilirdi. Baştan sabit pay verilince her vezir
    YALNIZCA KENDİ payından çeker, başka vezirin payına asla dokunmaz."""
    if gpu_sayisi <= 0:
        return []
    paylar: List[List[Task]] = [[] for _ in range(gpu_sayisi)]
    for i, task in enumerate(tasks):
        paylar[i % gpu_sayisi].append(task)
    return paylar


# NOT (Turkce -- kullanicinin acik talebi, gercek Kaggle deneyimiyle
# DOGRULANMIS bir gozlem): B=65 (tek GPU) ~1.25-4 adim/sn iken B=1 (tek
# GPU, TEK vezir -- baska hicbir GPU thread'i AYNI ANDA calismiyorken)
# ~15 adim/sn olcduldu -- bu fark, salt B-olcekleme (bant genisligi-sinirli
# RNN'de B'nin adim suresine etkisinin sinirli olmasi beklenirdi) ile
# ACIKLANAMAYACAK kadar buyuk. Gercek ek kaynak: coklu_gpu.py ESKIDEN
# HER GPU'yu AYRI bir threading.Thread ile (AYNI Python surecinde, AYNI
# GIL'i PAYLASARAK) yonetiyordu. CUDA kernel'lerinin KENDISI GPU'da
# gercekten paralel calissa da, HER adimdaki PYTHON-taraf isi (32
# katmanli eager donguntin op dispatch'i, token secimi, tensor
# indeksleme vb.) SADECE TEK BIR thread'in ayni anda calisabildigi GIL
# tarafindan SIRALANIYORDU -- yani 4 GPU thread'i "paralel" gorunse de,
# Python'un KENDISI hala TEK SEFERDE bir thread'in isini yapiyordu; 4
# thread GIL icin birbirini BEKLETIYORDU. Duzeltme: her GPU artik GERCEK
# bir OS SURECINDE (multiprocessing.Process, kendi Python yorumlayicisi
# + kendi GIL'i + kendi CUDA baglami) calisiyor -- 4 surec GERCEKTEN
# PARALEL Python calistirir (isletim sistemi tarafindan farkli CPU
# cekirdeklerine zamanlanir), GIL PAYLASIMI YOKTUR. Modelin KENDISI de
# artik padisahta DEGIL, HER SURECIN KENDI ICINDE yukleniyor (bkz.
# _surec_gpu_calistir) -- CUDA baglamlarinin surecler arasinda
# PAYLASILAMAMASI zaten bunu GEREKTIRIYORDU.
def _surec_gpu_calistir(
    gpu_index: int,
    model_ailesi: str,
    gpu_etiketi: str,
    kendi_gorevleri: List[Task],
    b_boyutu_baslangic: int,
    azami_yeni_token: int,
    bitis_zamani: Optional[float],
    ayrintili_log: bool,
    sonuc_kuyrugu: "multiprocessing.Queue",
) -> None:
    """AYRI bir OS sürecinde (multiprocessing.Process hedefi) çalışır.
    Modelini KENDİSİ yükler, kendi payındaki görevleri SÜREKLİ ADMİSYONLA
    (bkz. coz_yurutucu_toplu.toplu_gorevleri_coz) çözer, HER görev
    bitirilir bitirilmez `sonuc_kuyrugu`'ya ("sonuc", task_adi, sonuc)
    mesajı koyar -- padişah bu kuyruktan OKUYUP submission.json'a ARA
    KAYIT yapar. Bitirdiğinde ("bitti", gpu_index) mesajıyla haber verir
    (padişahın ne zaman TÜM süreçlerin işini bitirdiğini bilmesi için)."""
    try:
        from rwkv_native import native_rwkv_yukle
        from ttt_lora import tokenizer_yukle, yerel_model_yolu
        from coz_yurutucu_toplu import toplu_gorevleri_coz

        if not kendi_gorevleri:
            return

        yol = yerel_model_yolu(model_ailesi)
        print(f"[coklu_gpu] (süreç, {gpu_etiketi}) model kopyası yükleniyor...")
        ham_model_sarmali = native_rwkv_yukle(yol, cihaz=gpu_etiketi)
        ham_model = getattr(ham_model_sarmali, "ham_model", ham_model_sarmali)
        tokenizer = tokenizer_yukle(model_ailesi)
        print(f"[coklu_gpu] (süreç, {gpu_etiketi}) model hazır -- kendi payı: {len(kendi_gorevleri)} görev.")
        # KONUS DOĞRULAMASI (kullanıcının açık talebi): bu sürece GERÇEKTEN
        # ulaşan azami_yeni_token'ı burada da basıyoruz -- notebook_giris.py
        # -> gonderim_uret.py -> CokluGPUTopluCozucu -> BU SÜRECE kadar
        # KONUS'un doğru taşındığını bir sonraki gerçek koşuda kanıtlamak için.
        print(f"[coklu_gpu] (süreç, {gpu_etiketi}) KONUS DOĞRULAMASI: bu sürece ulaşan azami_yeni_token={azami_yeni_token}.")

        vram_kesifci = None
        b_boyutu = max(1, b_boyutu_baslangic)
        if gpu_etiketi != "cpu":
            from vram_izleyici import VramTabanliBKesifcisi
            vram_kesifci = VramTabanliBKesifcisi(gpu_etiketi, baslangic_b=b_boyutu_baslangic)
            b_boyutu = max(1, vram_kesifci.calisan_b())

        kalan: List[Task] = list(kendi_gorevleri)
        ilk_parti = kalan[:b_boyutu]
        kalan = kalan[b_boyutu:]
        if not ilk_parti:
            return

        def _sonraki_gorev_al() -> Optional[Task]:
            if bitis_zamani is not None and time.time() > bitis_zamani:
                return None
            if not kalan:
                return None
            return kalan.pop(0)

        def _tamamlandi(task_adi: str, sonuc: Dict[str, Any]) -> None:
            sonuc_kuyrugu.put(("sonuc", task_adi, sonuc))
            if vram_kesifci is not None:
                vram_kesifci.gorev_sonrasi_olc_ve_ayarla()

        try:
            toplu_gorevleri_coz(
                ham_model, tokenizer, ilk_parti,
                azami_yeni_token=azami_yeni_token, deneme_etiketi=gpu_etiketi,
                ayrintili_log=ayrintili_log, bitis_zamani=bitis_zamani,
                sonraki_gorev_al=_sonraki_gorev_al, tamamlanma_geri_cagirma=_tamamlandi,
            )
        except Exception as hata:
            # NOT: toplu_gorevleri_coz zaten HER biten görevi kendi içinde
            # tamamlanma_geri_cagirma ile bildirir -- bu except yalnızca
            # toplu_gorevleri_coz'un KENDİSİ (ör. batched prefill sırasında)
            # çökerse devreye girer. Bildirilmemiş görevler için özel bir
            # şey yapmaya GEREK YOK -- padişah, TÜM süreçler bittikten
            # SONRA `tasks` listesinin TAMAMINI tarayıp sonuç ALAMADIĞI
            # her görevi zaten BOS_TAHMIN ile dolduruyor (bkz.
            # CokluGPUTopluCozucu.coz).
            print(f"[coklu_gpu] (süreç, {gpu_etiketi}) SÜREKLİ ADMİSYON partisi başarısız: {hata}")
    finally:
        sonuc_kuyrugu.put(("bitti", gpu_index))


class CokluGPUTopluCozucu:
    """N GPU'yu, HER BİRİNİ AYRI bir OS sürecinde (multiprocessing.Process)
    çalıştırarak kullanır -- her süreç kendi model kopyasını KENDİSİ
    yükler, kendi payındaki görevleri sürekli admisyonla (bkz.
    coz_yurutucu_toplu.toplu_gorevleri_coz) çözer. Padişah (bu sınıf)
    modeli HİÇ yüklemez, yalnızca süreçleri başlatır ve sonuç kuyruğunu
    dinler -- bkz. _surec_gpu_calistir'deki GIL notu (bunun NEDEN gerçek
    threading yerine gerçek süreçler kullandığı için)."""

    def __init__(self, model_ailesi: str, gpu_etiketleri: List[str], b_boyutu: int = 128,
                 azami_yeni_token: int = 60000, ayrintili_log: bool = False):
        self.model_ailesi = model_ailesi
        self.gpu_etiketleri = gpu_etiketleri
        self.b_boyutu = b_boyutu
        self.azami_yeni_token = azami_yeni_token
        # YARISMA=False (deneme) modunda gonderim_uret.py bunu True yapar:
        # kullanıcının fark ettiği gibi, en uzun promptlu görev tek başına
        # dakikalarca sürebilen batched prefill'de HİÇ log yoktu -- bu
        # bayrak açıkken prefill + üretim çok daha sık (200 adımda bir)
        # ilerleme logu basar. Gerçek yarışma koşusunda (YARISMA=True) log
        # hacmini şişirmemek için VARSAYILAN OLARAK KAPALIDIR.
        self.ayrintili_log = ayrintili_log

    def coz(self, tasks: List[Task], bitis_zamani: Optional[float] = None,
            tamamlanma_geri_cagirma: Optional[Callable[[str, Dict[str, Any]], None]] = None,
            surekli_admisyon: bool = True) -> Dict[str, Dict[str, Any]]:
        if not surekli_admisyon:
            raise NotImplementedError(
                "CokluGPUTopluCozucu.coz: süreç tabanlı yeni uygulama yalnızca surekli_admisyon=True'yu "
                "destekliyor -- hiçbir üretim çağrısı False geçmiyor, bu yüzden sessizce yok saymak yerine "
                "açıkça hata veriyoruz."
            )
        gpu_sayisi = len(self.gpu_etiketleri)
        if gpu_sayisi == 0 or not tasks:
            for task in tasks:
                pass
            return {task.name: {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False} for task in tasks}

        paylar = _gorevleri_esit_dagit(tasks, gpu_sayisi)
        print(
            f"[coklu_gpu] {len(tasks)} görev, {gpu_sayisi} SÜRECE İŞ BAŞLAMADAN ÖNCE EŞİT paylaştırıldı: "
            f"{[len(p) for p in paylar]} (her GPU AYRI bir OS sürecinde, kendi GIL'iyle, BAĞIMSIZ çalışacak)."
        )

        # NOT: 'spawn' KASITLI OLARAK seçildi -- 'fork' (Linux varsayılanı),
        # ana süreçte HERHANGİ bir CUDA bağlamı zaten kurulmuşsa (ör. daha
        # önceki bir GPU sınaması/olası bir torch.cuda çağrısı) çocuk
        # süreçte GÜVENSİZDİR/tanımsız davranışa yol açabilir. 'spawn' her
        # çocuğu SIFIRDAN bir Python yorumlayıcısıyla başlatır -- daha
        # yavaş başlar ama CUDA ile KANITLANMIŞ şekilde güvenlidir.
        baglam = multiprocessing.get_context("spawn")
        sonuc_kuyrugu = baglam.Queue()
        surecler = []
        for gpu_index, (etiket, pay) in enumerate(zip(self.gpu_etiketleri, paylar)):
            surec = baglam.Process(
                target=_surec_gpu_calistir,
                args=(gpu_index, self.model_ailesi, etiket, pay, self.b_boyutu,
                      self.azami_yeni_token, bitis_zamani, self.ayrintili_log, sonuc_kuyrugu),
                daemon=True, name=f"vezir-surec-{etiket}",
            )
            surec.start()
            surecler.append(surec)

        sonuclar: Dict[str, Dict[str, Any]] = {}
        toplam = len(tasks)
        baslangic = time.time()
        bitenler = 0
        while bitenler < gpu_sayisi:
            tur, *govde = sonuc_kuyrugu.get()
            if tur == "sonuc":
                task_adi, sonuc = govde
                sonuclar[task_adi] = sonuc
                gecen = time.time() - baslangic
                print(f"[coklu_gpu] ({len(sonuclar)}/{toplam}) {task_adi} tamamlandı (bağımsız SÜREÇ ile) | toplam süre: {gecen:.1f} sn")
                if tamamlanma_geri_cagirma is not None:
                    tamamlanma_geri_cagirma(task_adi, sonuc)
            elif tur == "bitti":
                bitenler += 1

        for surec in surecler:
            surec.join(timeout=30)
            if surec.is_alive():
                print(f"[coklu_gpu] UYARI: {surec.name} 30 sn içinde kapanmadı -- terminate ediliyor.")
                surec.terminate()
                surec.join()

        for task in tasks:
            if task.name not in sonuclar:
                sonuclar[task.name] = {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False}
        return sonuclar
