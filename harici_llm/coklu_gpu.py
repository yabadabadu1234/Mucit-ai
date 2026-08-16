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
import queue
import threading
import time
from typing import Any, Callable, Dict, List, Optional

from arc import Task
from coz_yurutucu import BOS_TAHMIN
from model_yapilandirmalari import RWKV


def dort_kopya_yukle(model_ailesi: str = RWKV, azami_gpu: int = 4):
    """Modelin GPU başına BAĞIMSIZ bir kopyasını yükler (ağırlıklar
    paylaşılmaz -- her GPU kendi VRAM'inde tam bir kopya taşır).

    ÖNEMLİ: hangi GPU'lara kopya yükleneceği `torch.cuda.device_count()`
    gibi hazır bir sorguya KÖRÜ KÖRÜNE güvenilerek DEĞİL, gpu_tespit.
    kullanilabilir_gpu_indeksleri() ile HER cihazın GERÇEKTEN bir matmul
    çalıştırabildiği izole bir alt süreçte doğrulanarak belirlenir --
    "görünüyor ama arka planda kullanılamıyor" GPU'lar (kullanıcının
    gerçek Kaggle deneyiminde karşılaştığı durum) sessizce atlanır."""
    from gpu_tespit import kullanilabilir_gpu_indeksleri
    from rwkv_native import native_rwkv_yukle, rwkv_ham_pth_mi
    from ttt_lora import tokenizer_yukle, yerel_model_yolu

    gpu_indeksleri = kullanilabilir_gpu_indeksleri(azami_gpu=azami_gpu)
    if not gpu_indeksleri:
        raise RuntimeError(
            "coklu_gpu.dort_kopya_yukle: derinlemesine sınamadan (gerçek matmul) GEÇEN hiçbir GPU yok "
            "-- torch GPU görüyor olsa bile hiçbiri fiilen kullanılabilir değil."
        )

    yol = yerel_model_yolu(model_ailesi)
    if not rwkv_ham_pth_mi(yol):
        raise RuntimeError("coklu_gpu şu an yalnızca native RWKV (.pth) yolunu destekliyor.")

    modeller = []
    gpu_etiketleri = []
    for i in gpu_indeksleri:
        print(f"[coklu_gpu] cuda:{i} için model kopyası yükleniyor...")
        modeller.append(native_rwkv_yukle(yol, cihaz=f"cuda:{i}"))
        gpu_etiketleri.append(f"cuda:{i}")

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


def padisah_vezir_toplu_havuzuyla_coz(
    gpu_sayisi: int,
    tasks: List[Task],
    gorevleri_coz_toplu: Callable[[int, List[Task]], Dict[str, Dict[str, Any]]],
    b_boyutu_al: Callable[[int], int],
    bitis_zamani: Optional[float] = None,
    etiketler: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """padisah_vezir_havuzuyla_coz'un TOPLU (batched) varyantı.

    Padişah İŞE BAŞLAMADAN ÖNCE görevleri gpu_sayisi kadar EŞİT paya
    böler (bkz. _gorevleri_esit_dagit) -- her vezirin KENDİ AYRI kuyruğu
    vardır, ORTAK bir kuyruk YOKTUR. Her vezir yalnızca KENDİ payından,
    KENDİ o anki güvenli B boyutu kadar (b_boyutu_al(gpu_index) -- ör.
    vram_izleyici.VramTabanliBKesifcisi.calisan_b()) görevi BİRDEN çekip
    `gorevleri_coz_toplu` (gerçekte coz_yurutucu_toplu.toplu_gorevleri_coz)
    ile TEK bir batched adım zincirinde HEPSİNİ BİRLİKTE çözer:

      - Payı B'den BÜYÜKSE, kendi payını B'şer B'şer (birkaç toplu parti
        halinde) çeker.
      - Payı B'den KÜÇÜKSE, elindeki KADARINI (tek partide) çeker --
        fazlası zaten yoktur, başka vezirin payına el atmaz.

    "tek GPU'daki model gerçekten B soruya AYNI ANDA baksın" davranışı
    budur; padisah_vezir_havuzuyla_coz (B=1) yalnızca görevleri seri
    olarak, GPU başına tek tek çözer."""
    paylar = _gorevleri_esit_dagit(tasks, gpu_sayisi)
    kendi_kuyruklari: List["queue.Queue[Task]"] = []
    for pay in paylar:
        kuyruk: "queue.Queue[Task]" = queue.Queue()
        for task in pay:
            kuyruk.put(task)
        kendi_kuyruklari.append(kuyruk)

    sonuclar: Dict[str, Dict[str, Any]] = {}
    kilit = threading.Lock()
    toplam = len(tasks)
    baslangic = time.time()

    def _etiket(gpu_index: int) -> str:
        if etiketler is not None and gpu_index < len(etiketler):
            return etiketler[gpu_index]
        return f"cuda:{gpu_index}"

    print(
        f"[coklu_gpu] {toplam} görev, {gpu_sayisi} vezire İŞ BAŞLAMADAN ÖNCE EŞİT paylaştırıldı: "
        f"{[len(p) for p in paylar]} (hiçbir vezir başka vezirin payına dokunmayacak)."
    )

    def _vezir(gpu_index: int) -> None:
        kendi_kuyrugu = kendi_kuyruklari[gpu_index]
        while True:
            if bitis_zamani is not None and time.time() > bitis_zamani:
                return
            b_boyutu = max(1, b_boyutu_al(gpu_index))
            parti: List[Task] = []
            for _ in range(b_boyutu):
                try:
                    parti.append(kendi_kuyrugu.get_nowait())
                except queue.Empty:
                    break
            if not parti:
                return  # KENDİ payı tükendi -- başka vezirin payına asla el atmaz
            try:
                parti_sonuclari = gorevleri_coz_toplu(gpu_index, parti)
            except Exception as hata:
                print(f"[coklu_gpu] ({_etiket(gpu_index)}) {len(parti)} görevlik TOPLU parti başarısız: {hata}")
                parti_sonuclari = {t.name: {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False} for t in parti}
            with kilit:
                sonuclar.update(parti_sonuclari)
                gecen = time.time() - baslangic
                print(f"[coklu_gpu] ({_etiket(gpu_index)}) ({len(sonuclar)}/{toplam}) {len(parti)} görevlik TOPLU (B={len(parti)}) parti tamamlandı | toplam süre: {gecen:.1f} sn")
            for _ in parti:
                kendi_kuyrugu.task_done()

    veziler = []
    for gpu_index in range(gpu_sayisi):
        vezir = threading.Thread(target=_vezir, args=(gpu_index,), daemon=True, name=f"vezir-toplu-{_etiket(gpu_index)}")
        vezir.start()
        veziler.append(vezir)
    for vezir in veziler:
        vezir.join()

    for task in tasks:
        if task.name not in sonuclar:
            sonuclar[task.name] = {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False}

    return sonuclar


class CokluGPUTopluCozucu:
    """N GPU'daki N bağımsız model kopyasını, HER GPU'da B GÖREVİ TEK bir
    batched adım zinciriyle EŞZAMANLI çözecek şekilde kullanır (bkz.
    coz_yurutucu_toplu.toplu_gorevleri_coz). B, `vram_kesifcileri`
    verilirse (bkz. vram_izleyici.VramTabanliBKesifcisi) her partiden
    SONRA gerçek VRAM ölçümüyle otomatik ayarlanır; verilmezse sabit
    `b_boyutu` kullanılır."""

    def __init__(self, modeller: List[Any], tokenizer: Any, b_boyutu: int = 128,
                 azami_yeni_token: int = 60000, gpu_etiketleri: Optional[List[str]] = None,
                 vram_kesifcileri: Optional[List[Any]] = None, ayrintili_log: bool = False):
        self.modeller = modeller
        self.tokenizer = tokenizer
        self.b_boyutu = b_boyutu
        self.azami_yeni_token = azami_yeni_token
        self.gpu_etiketleri = gpu_etiketleri or [
            str(getattr(m, "device", f"gpu{i}")) for i, m in enumerate(modeller)
        ]
        self.vram_kesifcileri = vram_kesifcileri
        # YARISMA=False (deneme) modunda gonderim_uret.py bunu True yapar:
        # kullanıcının fark ettiği gibi, en uzun promptlu görev tek başına
        # dakikalarca sürebilen batched prefill'de HİÇ log yoktu -- bu
        # bayrak açıkken prefill + üretim çok daha sık (200 adımda bir)
        # ilerleme logu basar. Gerçek yarışma koşusunda (YARISMA=True) log
        # hacmini şişirmemek için VARSAYILAN OLARAK KAPALIDIR.
        self.ayrintili_log = ayrintili_log

    def coz(self, tasks: List[Task], bitis_zamani: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        from coz_yurutucu_toplu import toplu_gorevleri_coz

        def _b_boyutu_al(gpu_index: int) -> int:
            if self.vram_kesifcileri is not None:
                return self.vram_kesifcileri[gpu_index].calisan_b()
            return self.b_boyutu

        def _gorevleri_coz_toplu(gpu_index: int, gorev_partisi: List[Task]) -> Dict[str, Dict[str, Any]]:
            ham_model = getattr(self.modeller[gpu_index], "ham_model", self.modeller[gpu_index])
            sonuc = toplu_gorevleri_coz(
                ham_model, self.tokenizer, gorev_partisi,
                azami_yeni_token=self.azami_yeni_token, deneme_etiketi=self.gpu_etiketleri[gpu_index],
                ayrintili_log=self.ayrintili_log, bitis_zamani=bitis_zamani,
            )
            if self.vram_kesifcileri is not None:
                self.vram_kesifcileri[gpu_index].gorev_sonrasi_olc_ve_ayarla()
            return sonuc

        return padisah_vezir_toplu_havuzuyla_coz(
            len(self.modeller), tasks, _gorevleri_coz_toplu, _b_boyutu_al,
            bitis_zamani=bitis_zamani, etiketler=self.gpu_etiketleri,
        )
