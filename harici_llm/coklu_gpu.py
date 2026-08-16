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
    paylaşılmaz -- her GPU kendi VRAM'inde tam bir kopya taşır)."""
    import torch
    from rwkv_native import native_rwkv_yukle, rwkv_ham_pth_mi
    from ttt_lora import tokenizer_yukle, yerel_model_yolu

    if not torch.cuda.is_available():
        raise RuntimeError("coklu_gpu.dort_kopya_yukle: CUDA yok, GPU başına ayrı kopya yüklenemez.")
    gpu_sayisi = min(torch.cuda.device_count(), azami_gpu)
    if gpu_sayisi < 1:
        raise RuntimeError("coklu_gpu.dort_kopya_yukle: hiç CUDA cihazı görünmüyor.")

    yol = yerel_model_yolu(model_ailesi)
    if not rwkv_ham_pth_mi(yol):
        raise RuntimeError("coklu_gpu şu an yalnızca native RWKV (.pth) yolunu destekliyor.")

    modeller = []
    for i in range(gpu_sayisi):
        print(f"[coklu_gpu] cuda:{i} için model kopyası yükleniyor...")
        modeller.append(native_rwkv_yukle(yol, cihaz=f"cuda:{i}"))

    tokenizer = tokenizer_yukle(model_ailesi)
    print(f"[coklu_gpu] {gpu_sayisi} GPU'da modelin BAĞIMSIZ birer kopyası hazır: {[f'cuda:{i}' for i in range(gpu_sayisi)]}")
    return modeller, tokenizer


def padisah_vezir_havuzuyla_coz(
    gpu_sayisi: int,
    tasks: List[Task],
    gorevi_coz: Callable[[int, Task], Dict[str, Any]],
    bitis_zamani: Optional[float] = None,
) -> Dict[str, Dict[str, Any]]:
    """Genel amaçlı padişah/vezir iş havuzu -- `gorevi_coz(gpu_index, task)`
    RWKV'ye özgü değildir, bu yüzden testlerde de gerçek threading
    davranışını (senkronsuz dispatch + dinamik yeniden dağıtım) RWKV
    yüklemeden doğrudan sınamak mümkündür."""
    gorev_kuyrugu: "queue.Queue[Task]" = queue.Queue()
    for task in tasks:
        gorev_kuyrugu.put(task)

    sonuclar: Dict[str, Dict[str, Any]] = {}
    kilit = threading.Lock()
    toplam = len(tasks)
    baslangic = time.time()

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
                print(f"[coklu_gpu] (cuda:{gpu_index}) {task.name} başarısız: {hata}")
                sonuc = {"attempt_1": BOS_TAHMIN, "attempt_1_gonderildi_mi": False}
            with kilit:
                sonuclar[task.name] = sonuc
                gecen = time.time() - baslangic
                print(f"[coklu_gpu] (cuda:{gpu_index}) ({len(sonuclar)}/{toplam}) {task.name} tamamlandı | toplam süre: {gecen:.1f} sn")
            gorev_kuyrugu.task_done()

    veziler = []
    for gpu_index in range(gpu_sayisi):
        # HER vezir HEMEN işbaşı yapar; padişah bir sonrakini başlatmadan
        # ÖNCEKİ vezirin bitmesini ASLA beklemez (thread.start() bloklamaz).
        vezir = threading.Thread(target=_vezir, args=(gpu_index,), daemon=True, name=f"vezir-cuda{gpu_index}")
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
                 azami_yeni_token: int = 60000):
        self.modeller = modeller
        self.tokenizer = tokenizer
        self.azami_tur = azami_tur
        self.azami_yeni_token = azami_yeni_token

    def coz(self, tasks: List[Task], bitis_zamani: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        from coz_yurutucu import _tek_deneme_uret_artimli

        def _gorevi_coz(gpu_index: int, task: Task) -> Dict[str, Any]:
            cevap = _tek_deneme_uret_artimli(
                self.modeller[gpu_index], self.tokenizer, RWKV, task,
                self.azami_tur, self.azami_yeni_token, f"gpu{gpu_index}",
            )
            return {
                "attempt_1": cevap if cevap is not None else BOS_TAHMIN,
                "attempt_1_gonderildi_mi": cevap is not None,
            }

        return padisah_vezir_havuzuyla_coz(len(self.modeller), tasks, _gorevi_coz, bitis_zamani=bitis_zamani)
