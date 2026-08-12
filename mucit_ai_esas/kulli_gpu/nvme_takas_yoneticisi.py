

import os
import sys
import uuid
import time
import shutil
import tempfile
import logging
import threading
import weakref
import contextlib
import concurrent.futures
from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Any, Optional
import torch

logger = logging.getLogger("kulli_gpu.nvme_takas_yoneticisi")


class TakasVerisiKayipHatasi(RuntimeError):
    pass


class _IzlenebilirDosyaYolu(str):
    pass


def _paket_gc_edildi_geri_cagirma(sanal_id: str, kayit_defteri_ref) -> None:
    kayit_defteri = kayit_defteri_ref()
    if kayit_defteri is None:
        return
    try:
        kayit_defteri.referans_durusdur_veya_sil(sanal_id)
    except Exception as exc:
        logger.debug(f"[NvmeTakasYoneticisi] GC-tetiklemeli referans düşürme uyarısı: {exc}")


MEM_STATE_ACTIVE_VRAM = "MEM_STATE_ACTIVE_VRAM"
MEM_STATE_SWAPPED_NVME = "MEM_STATE_SWAPPED_NVME"
MEM_STATE_ORPHANED = "MEM_STATE_ORPHANED"


@dataclass
class NesneAdresKaydi:
    sanal_adres: str
    dosya_yolu: Optional[str] = None
    shape: Tuple[int, ...] = ()
    dtype: torch.dtype = torch.float32
    durum: str = MEM_STATE_ACTIVE_VRAM
    ref_count: int = 1
    son_erisim_zamani: float = field(default_factory=time.time)
    element_size: int = 4
    numel: int = 0
    canli_tensor_ref: Optional[Any] = None

    @property
    def bayt_boyutu(self) -> int:
        return self.element_size * self.numel if self.numel > 0 else 0


class KureselAdresKayitDefteri:
    def __init__(self):
        self.lock = threading.RLock()
        self.kayitlar: Dict[str, NesneAdresKaydi] = {}
        self.aktif_dosya_yollari: Dict[str, str] = {}  

    def kayit_ekle_ve_guncelle(
        self,
        kayit: Optional[Any] = None,
        nesne_id: Optional[str] = None,
        virtual_ptr: int = 0,
        file_path: str = "",
        size_bytes: int = 0,
        ref_count: int = 1,
        state: str = MEM_STATE_SWAPPED_NVME,
        **kwargs
    ) -> None:
        with self.lock:
            if isinstance(kayit, NesneAdresKaydi):
                self.kayitlar[kayit.sanal_adres] = kayit
                if kayit.dosya_yolu:
                    self.aktif_dosya_yollari[kayit.dosya_yolu] = kayit.sanal_adres
            else:
                n_id = nesne_id or f"addr_{uuid.uuid4().hex[:8]}"
                f_path = file_path or (kayit if isinstance(kayit, str) else "")
                kayit_obj = NesneAdresKaydi(
                    sanal_adres=n_id,
                    dosya_yolu=f_path if f_path else None,
                    durum=state,
                    ref_count=ref_count,
                    element_size=1,
                    numel=size_bytes
                )
                self.kayitlar[n_id] = kayit_obj
                if f_path:
                    self.aktif_dosya_yollari[f_path] = n_id

    def kayit_ekle_veya_guncelle(self, *args, **kwargs) -> None:
        self.kayit_ekle_ve_guncelle(*args, **kwargs)

    def referans_durusdur_veya_sil(self, nesne_id: str) -> bool:
        dosya_yolu_silinecek = None
        with self.lock:
            if nesne_id in self.kayitlar:
                self.kayitlar[nesne_id].ref_count -= 1
                if self.kayitlar[nesne_id].ref_count <= 0:
                    dosya_yolu_silinecek = self.kayitlar[nesne_id].dosya_yolu
                    self.kayit_sil(nesne_id)
        if dosya_yolu_silinecek and os.path.exists(dosya_yolu_silinecek):
            try:
                os.remove(dosya_yolu_silinecek)
            except OSError as exc:
                logger.debug(f"[KureselAdresKayitDefteri] Anlık imha başarısız: {exc}")
        return dosya_yolu_silinecek is not None

    def kayit_getir(self, sanal_adres: str) -> Optional[NesneAdresKaydi]:
        with self.lock:
            return self.kayitlar.get(sanal_adres)

    def ref_arttir(self, sanal_adres: str) -> None:
        with self.lock:
            if sanal_adres in self.kayitlar:
                self.kayitlar[sanal_adres].ref_count += 1

    def ref_azalt(self, sanal_adres: str) -> None:
        with self.lock:
            if sanal_adres in self.kayitlar:
                self.kayitlar[sanal_adres].ref_count -= 1
                if self.kayitlar[sanal_adres].ref_count <= 0:
                    self.kayitlar[sanal_adres].durum = MEM_STATE_ORPHANED

    def aktif_vram_tensor_kaydet(self, tensor: "torch.Tensor", sanal_id: Optional[str] = None) -> str:
        with self.lock:
            n_id = sanal_id or f"addr_{uuid.uuid4().hex[:8]}"
            kayit = NesneAdresKaydi(
                sanal_adres=n_id,
                dosya_yolu=None,
                shape=tuple(tensor.shape),
                dtype=tensor.dtype,
                durum=MEM_STATE_ACTIVE_VRAM,
                ref_count=1,
                element_size=tensor.element_size(),
                numel=tensor.numel(),
                canli_tensor_ref=weakref.ref(tensor)
            )
            self.kayitlar[n_id] = kayit
            return n_id

    def kayit_sil(self, sanal_adres: str) -> None:
        with self.lock:
            kayit = self.kayitlar.pop(sanal_adres, None)
            if kayit and kayit.dosya_yolu:
                self.aktif_dosya_yollari.pop(kayit.dosya_yolu, None)


kuresel_adres_kayit_defteri = KureselAdresKayitDefteri()


def al_dinamik_toplam_ram_bayt() -> int:
    try:
        import psutil
        return int(psutil.virtual_memory().total)
    except ImportError:
        pass
    try:
        return os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    except (ValueError, AttributeError, OSError):
        pass
    try:
        if os.path.exists('/proc/meminfo'):
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal:'):
                        return int(line.split()[1]) * 1024
    except OSError:
        pass
    return 8 * 1024 * 1024 * 1024


class DinamikSistemRamDenetci:
    def __init__(self, oran: float = 0.90):
        self.oran = oran
        self.toplam_ram_bayt = al_dinamik_toplam_ram_bayt()
        self.esik_ram_bayt = int(self.toplam_ram_bayt * self.oran)
        logger.info(
            f"[Dinamik RAM Denetçi] Cihaz Toplam RAM: {self.toplam_ram_bayt / (1024**3):.2f} GB | "
            f"Eşik (%{int(self.oran * 100)}): {self.esik_ram_bayt / (1024**3):.2f} GB"
        )

    def aktif_ram_bayt(self) -> int:
        try:
            import psutil
            return int(psutil.virtual_memory().used)
        except ImportError:
            pass
        try:
            if os.path.exists('/proc/meminfo'):
                mem_available = None
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemAvailable:'):
                            mem_available = int(line.split()[1]) * 1024
                            break
                if mem_available is not None:
                    return self.toplam_ram_bayt - mem_available
        except OSError:
            pass
        return 0

    def esik_asildi_mi(self) -> bool:
        return self.aktif_ram_bayt() >= self.esik_ram_bayt


kuresel_ram_denetci = DinamikSistemRamDenetci()


class NvmeTahliyeKararMotoru:
    def __init__(self, emniyet_marji_mb: int = 1024, swap_dir: str = "/tmp/kulli_scratchpad", azami_disk_kullanimi_mb: float = 20480.0):
        self.emniyet_marji = emniyet_marji_mb * 1024 * 1024
        self.swap_dir = swap_dir
        self.azami_disk_kullanimi_bayt = azami_disk_kullanimi_mb * 1024 * 1024
        os.makedirs(self.swap_dir, exist_ok=True)

    def disk_kullanimini_olc(self) -> int:
        toplam = 0
        try:
            with os.scandir(self.swap_dir) as it:
                for entry in it:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            toplam += entry.stat().st_size
                    except OSError:
                        continue
        except OSError:
            return 0
        return toplam

    def disk_tavanini_zorla(self, esik_bayt_ekstra: float = 0.0) -> None:
        if kuresel_ram_denetci.esik_asildi_mi():
            logger.warning(
                f"[NvmeTahliyeKararMotoru] Dinamik RAM eşiği (%{int(kuresel_ram_denetci.oran*100)}, "
                f"{kuresel_ram_denetci.esik_ram_bayt / (1024**3):.2f} GB) aşıldı — agresif süpürme tetikleniyor."
            )
            GuvenliVramVeTmpSupurgesi.supur(swap_dir=self.swap_dir, eskime_esigi_sn=0.0)

        kullanim = self.disk_kullanimini_olc()
        if kullanim + esik_bayt_ekstra <= self.azami_disk_kullanimi_bayt:
            return

        logger.warning(
            f"[NvmeTahliyeKararMotoru] Disk tavanı aşıldı: {kullanim / (1024**2):.1f} MB "
            f"kullanılan / {self.azami_disk_kullanimi_bayt / (1024**2):.1f} MB tavan — agresif süpürme tetikleniyor."
        )
        GuvenliVramVeTmpSupurgesi.supur(swap_dir=self.swap_dir, eskime_esigi_sn=0.0)

        kullanim = self.disk_kullanimini_olc()
        if kullanim + esik_bayt_ekstra <= self.azami_disk_kullanimi_bayt:
            return

        logger.warning(
            f"[NvmeTahliyeKararMotoru] Süpürme sonrası hâlâ tavan üzerinde "
            f"({kullanim / (1024**2):.1f} MB) — en eski dosyalar zorla siliniyor."
        )
        try:
            with kuresel_adres_kayit_defteri.lock:
                canli_yollar = set(kuresel_adres_kayit_defteri.aktif_dosya_yollari.keys())

            referanssiz = []
            canli_bayt = 0
            with os.scandir(self.swap_dir) as it:
                for entry in it:
                    try:
                        if not entry.is_file(follow_symlinks=False):
                            continue
                        st = entry.stat()
                        if entry.path in canli_yollar:
                            canli_bayt += st.st_size
                            continue
                        referanssiz.append((st.st_mtime, entry.path, st.st_size))
                    except OSError:
                        continue

            referanssiz.sort(key=lambda x: x[0])
            silinen_bayt = 0
            for _mtime, fpath, fsize in referanssiz:
                if kullanim + esik_bayt_ekstra <= self.azami_disk_kullanimi_bayt:
                    break
                try:
                    os.remove(fpath)
                    kullanim -= fsize
                    silinen_bayt += fsize
                except OSError:
                    continue

            logger.warning(
                f"[NvmeTahliyeKararMotoru] Referanssız dosyalardan {silinen_bayt / (1024**2):.1f} MB "
                f"serbest bırakıldı."
            )

            if kullanim + esik_bayt_ekstra > self.azami_disk_kullanimi_bayt:
                logger.error(
                    f"[NvmeTahliyeKararMotoru] Disk tavanı hâlâ aşılıyor "
                    f"({kullanim / (1024**2):.1f} MB), ancak kalan {canli_bayt / (1024**2):.1f} MB "
                    f"autograd tarafından HÂLÂ KULLANILAN takas verisidir ve SİLİNMEYECEKTİR. "
                    f"Silinmesi, geri yayılımda sessizce sıfır gradyan üretip modeli bozardı. "
                    f"config.azami_dugum_sayisi / batch boyutu düşürülmeli."
                )
        except OSError as exc:
            logger.error(f"[NvmeTahliyeKararMotoru] Zorla silme sırasında hata: {exc}")

    def vram_sınırı_asildi_mi_tahkik_et(self, gerekli_bayt: int, device_id: int = 0) -> bool:
        if not torch.cuda.is_available():
            return False
        try:
            free_vram_bytes, total_vram_bytes = torch.cuda.mem_get_info(device_id)
            if (gerekli_bayt + self.emniyet_marji) > free_vram_bytes:
                return True
        except Exception as exc:
            logger.warning(f"[NvmeTahliyeKararMotoru] VRAM sorgu uyarisi: {exc}")
        return False

    def vramden_nvme_diske_tahliye_et(self, fark_bayt: int) -> List[str]:
        canli_cuda = 0
        canli_bayt = 0
        otograd_bagli = 0

        with kuresel_adres_kayit_defteri.lock:
            for kayit in kuresel_adres_kayit_defteri.kayitlar.values():
                if kayit.durum == MEM_STATE_SWAPPED_NVME:
                    continue
                tensor = kayit.canli_tensor_ref() if kayit.canli_tensor_ref is not None else None
                if tensor is None or not getattr(tensor, "is_cuda", False):
                    continue
                canli_cuda += 1
                canli_bayt += tensor.numel() * tensor.element_size()
                if tensor.requires_grad or getattr(tensor, "grad_fn", None) is not None:
                    otograd_bagli += 1

        if canli_cuda == 0:
            logger.info(
                f"[NvmeTahliyeKararMotoru] Elle tahliye edilebilir kayıtlı VRAM tensörü yok "
                f"(talep {fark_bayt / (1024 ** 2):.1f} MB). Aktivasyon tahliyesi autograd "
                f"pack/unpack kancası üzerinden yürütülüyor; o yolun sayaçları "
                f"NvmeTakasYoneticisi.tahliye_sayaci / geri_cagirma_sayaci alanlarındadır."
            )
            return []

        logger.warning(
            f"[NvmeTahliyeKararMotoru] Kayıtlı {canli_cuda} canlı VRAM tensörü "
            f"({canli_bayt / (1024 ** 2):.1f} MB) var; {otograd_bagli} tanesi autograd grafına bağlı. "
            f"HİÇBİRİ elle tahliye EDİLMEYECEK: kayıt defteri yalnızca zayıf referans (weakref) tutar, "
            f"tensörün sahibi ileri geçiştir. Sahibin altından depolamayı çekmek (.data değiştirmek) "
            f"ileri geçişi ve geri yayılımı bozar, üstelik geri yükleme kancası yoktur. "
            f"Güvenli tahliyenin tek yolu saved_tensors_hooks (pack/unpack) mekanizmasıdır."
        )
        return []


class AutogradNvmeOffloadHook:
    def __init__(
        self,
        karar_motoru: Optional[NvmeTahliyeKararMotoru] = None,
        kayit_defteri: Optional[KureselAdresKayitDefteri] = None
    ):
        self.karar_motoru = karar_motoru or NvmeTahliyeKararMotoru()
        self.kayit_defteri = kayit_defteri or kuresel_adres_kayit_defteri
        
        
        self._yazma_havuzu = concurrent.futures.ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="nvme_takas_yazici"
        )
        self._bekleyen_yazmalar: Dict[str, concurrent.futures.Future] = {}
        self._bekleyen_yazmalar_lock = threading.Lock()
        self._bekleyen_yazma_semaforu = threading.BoundedSemaphore(4)

    def pack_hook_diske_tahliye(self, tensor: torch.Tensor) -> Tuple[str, Tuple[int, ...], torch.dtype, str]:
        is_cuda_or_npu = getattr(tensor, "is_cuda", False) or getattr(tensor, "is_npu", False)
        if not is_cuda_or_npu or not torch.cuda.is_available():
            return ("", tuple(tensor.shape), tensor.dtype, "cpu")

        bayt_boyut = tensor.element_size() * tensor.numel()
        if not self.karar_motoru.vram_sınırı_asildi_mi_tahkik_et(bayt_boyut):
            return ("", tuple(tensor.shape), tensor.dtype, str(tensor.device))

        try:
            self.karar_motoru.disk_tavanini_zorla(esik_bayt_ekstra=bayt_boyut)
        except Exception as _tavan_exc:
            logger.warning(f"[AutogradNvmeOffloadHook] Disk tavanı kontrolü başarısız: {_tavan_exc}")

        dosya_id = f"autograd_swap_{uuid.uuid4().hex[:12]}.bin"
        dosya_yolu = os.path.join(self.karar_motoru.swap_dir, dosya_id)

        self._bekleyen_yazma_semaforu.acquire()
        _semafor_devredildi = False
        try:
            original_device = str(tensor.device)

            cpu_kopyasi = tensor.detach().cpu()

            
            gereken_bayt = cpu_kopyasi.element_size() * cpu_kopyasi.numel()
            try:
                disk_durumu = shutil.disk_usage(self.karar_motoru.swap_dir)
                if disk_durumu.free < (gereken_bayt + 64 * 1024 * 1024):  
                    raise OSError(
                        f"NVMe takas dizininde yetersiz disk alanı: gereken~{gereken_bayt} bayt, "
                        f"boş={disk_durumu.free} bayt ({self.karar_motoru.swap_dir})"
                    )
            except OSError:
                raise
            except Exception as _disk_exc:
                logger.warning(f"[AutogradNvmeOffloadHook] Disk alanı sorgulanamadı, yazma denemesi yine de yapılacak: {_disk_exc}")

            
            sanal_id = f"addr_{uuid.uuid4().hex[:8]}"
            kayit = NesneAdresKaydi(
                sanal_adres=sanal_id,
                dosya_yolu=dosya_yolu,
                shape=tuple(tensor.shape),
                dtype=tensor.dtype,
                durum=MEM_STATE_SWAPPED_NVME,
                ref_count=1,
                element_size=tensor.element_size(),
                numel=tensor.numel()
            )






            if hasattr(self, "kayit_defteri") and self.kayit_defteri is not None:
                self.kayit_defteri.kayit_ekle_ve_guncelle(kayit)

            yazma_future = self._yazma_havuzu.submit(torch.save, cpu_kopyasi, dosya_yolu)
            yazma_future.add_done_callback(lambda _f: self._bekleyen_yazma_semaforu.release())
            _semafor_devredildi = True
            with self._bekleyen_yazmalar_lock:
                self._bekleyen_yazmalar[dosya_yolu] = yazma_future

            logger.debug(f"[NvmeTakasYoneticisi] VRAM -> NVMe Akıllı Tahliye Mühürlendi: {dosya_id}")


            izlenebilir_dosya_yolu = _IzlenebilirDosyaYolu(dosya_yolu)
            kayit_defteri_hedefi = self.kayit_defteri if hasattr(self, "kayit_defteri") else None
            if kayit_defteri_hedefi is not None:
                weakref.finalize(
                    izlenebilir_dosya_yolu,
                    _paket_gc_edildi_geri_cagirma,
                    sanal_id,
                    weakref.ref(kayit_defteri_hedefi)
                )
            return (izlenebilir_dosya_yolu, tuple(kayit.shape), kayit.dtype, original_device)
        except Exception as exc:
            if not _semafor_devredildi:
                self._bekleyen_yazma_semaforu.release()
            logger.error(f"[AutogradNvmeOffloadHook] Diske tahliye hatasi: {exc}")
            return ("", tuple(tensor.shape), tensor.dtype, "cpu")

    def unpack_hook_diskten_geri_yukle(self, bundle: Tuple[str, Tuple[int, ...], torch.dtype], target_device: Optional[str] = None) -> torch.Tensor:
        dosya_yolu, shape, dtype = bundle

        if target_device is None:
            target_device = "cuda:0" if torch.cuda.is_available() else "cpu"

        
        bekleyen_future = None
        yazici = getattr(self, "_bekleyen_yazmalar", None)
        if yazici is not None and dosya_yolu:
            with self._bekleyen_yazmalar_lock:
                bekleyen_future = self._bekleyen_yazmalar.pop(dosya_yolu, None)
        if bekleyen_future is not None:
            try:
                bekleyen_future.result()
            except Exception as _yazma_exc:
                raise TakasVerisiKayipHatasi(
                    f"Takas dosyasi diske yazilamadi ({dosya_yolu}): {_yazma_exc}. "
                    f"Sessiz sifir tensor DONDURULMEDI; modelin bozuk gradyanla egitilmesi engellendi."
                ) from _yazma_exc

        if not dosya_yolu or not os.path.exists(dosya_yolu):
            raise TakasVerisiKayipHatasi(
                f"Takas dosyasi geri yukleme aninda diskte bulunamadi: {dosya_yolu!r}. "
                f"Bu, hala kullanimda olan bir dosyanin tahliye/supurme tarafindan silindigi anlamina gelir. "
                f"Sessiz sifir tensor DONDURULMEDI; modelin bozuk gradyanla egitilmesi engellendi."
            )

        restored_tensor = None
        try:
            
            restored_tensor = torch.load(dosya_yolu, map_location="cpu")
            if restored_tensor.shape != shape:
                restored_tensor = restored_tensor.reshape(shape)
            return restored_tensor.to(device=target_device)
        except Exception as exc:
            
            
            logger.error(f"[AutogradNvmeOffloadHook] Diskten geri yukleme hatasi: {exc}")
            if restored_tensor is not None:
                try:
                    import gc as _gc_geri_yukleme
                    _gc_geri_yukleme.collect()
                    torch.cuda.empty_cache()
                    return restored_tensor.to(device=target_device)
                except Exception:
                    logger.error(
                        "[AutogradNvmeOffloadHook] GPU'ya taşıma empty_cache sonrası da "
                        "başarısız — veri CPU'da bırakılıyor (sıfırlanmıyor)."
                    )
                    return restored_tensor
            raise TakasVerisiKayipHatasi(
                f"Takas dosyasi okunamadi ({dosya_yolu}): {exc}. "
                f"Sessiz sifir tensor DONDURULMEDI."
            ) from exc
        finally:












            pass


class GuvenliVramVeTmpSupurgesi:
    ESKIME_ESIGI_SN: float = 120.0

    @staticmethod
    def supur(swap_dir: str = "/tmp/kulli_scratchpad", eskime_esigi_sn: Optional[float] = None) -> None:
        esik = GuvenliVramVeTmpSupurgesi.ESKIME_ESIGI_SN if eskime_esigi_sn is None else eskime_esigi_sn
        simdi = time.time()
        with kuresel_adres_kayit_defteri.lock:
            silinecek_adresler = []
            for sanal_addr, kayit in kuresel_adres_kayit_defteri.kayitlar.items():
                if kayit.durum == MEM_STATE_ACTIVE_VRAM:
                    continue

                if not (kayit.ref_count <= 0 or kayit.durum == MEM_STATE_ORPHANED):
                    continue

                if kayit.durum in (MEM_STATE_SWAPPED_NVME, MEM_STATE_ORPHANED):
                    if kayit.dosya_yolu and os.path.exists(kayit.dosya_yolu):
                        try:
                            os.remove(kayit.dosya_yolu)
                        except Exception:
                            pass
                    silinecek_adresler.append(sanal_addr)

            for addr in silinecek_adresler:
                kuresel_adres_kayit_defteri.kayit_sil(addr)

            
            if os.path.exists(swap_dir):
                for fname in os.listdir(swap_dir):
                    fpath = os.path.join(swap_dir, fname)
                    if fpath not in kuresel_adres_kayit_defteri.aktif_dosya_yollari and os.path.isfile(fpath):
                        try:
                            os.remove(fpath)
                        except Exception:
                            pass

        import gc as _gc_temizle
        _gc_temizle.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class NvmeTakasYoneticisi:
    def __init__(self, swap_dir: Optional[str] = None):
        if swap_dir is None:
            if os.path.exists("/tmp"):
                self.swap_dir = "/tmp/kulli_scratchpad"
            else:
                self.swap_dir = os.path.join(tempfile.gettempdir(), "kulli_scratchpad")
        else:
            self.swap_dir = swap_dir

        os.makedirs(self.swap_dir, exist_ok=True)
        self.kayit_defteri = kuresel_adres_kayit_defteri
        self.karar_motoru = NvmeTahliyeKararMotoru(emniyet_marji_mb=1024, swap_dir=self.swap_dir)
        self.offload_hook = AutogradNvmeOffloadHook(karar_motoru=self.karar_motoru, kayit_defteri=self.kayit_defteri)
        self.tahliye_sayaci = 0
        self.geri_cagirma_sayaci = 0
        
        
        self._sayac_lock = threading.Lock()
        self._aktif_kapsam_muhafizi = None
        logger.info(f"[NvmeTakasYoneticisi] Disk takas dizini aktif: {self.swap_dir}")

    def pack_hook_diske_tahliye(self, tensor: torch.Tensor) -> Any:
        
        
        res = self.offload_hook.pack_hook_diske_tahliye(tensor)
        if isinstance(res, tuple) and res[0] != "":
            with self._sayac_lock:
                self.tahliye_sayaci += 1
            return (res[0], res[1], res[2], res[3])






        return tensor.detach()

    def unpack_hook_diskten_geri_cagır(self, pack_bundle: Any) -> torch.Tensor:
        if isinstance(pack_bundle, torch.Tensor):
            return pack_bundle

        if len(pack_bundle) == 4:
            bundle_3 = (pack_bundle[0], pack_bundle[1], pack_bundle[2])
            target_device = pack_bundle[3]
            res = self.offload_hook.unpack_hook_diskten_geri_yukle(bundle_3, target_device=target_device)
            with self._sayac_lock:
                self.geri_cagirma_sayaci += 1
            return res
        return self.offload_hook.unpack_hook_diskten_geri_yukle(pack_bundle)

    def kapsam_muhafizi_aktifles(self):




        if not torch.cuda.is_available():
            self._aktif_kapsam_muhafizi = contextlib.nullcontext()
            return self._aktif_kapsam_muhafizi

        self._aktif_kapsam_muhafizi = torch.autograd.graph.saved_tensors_hooks(
            self.pack_hook_diske_tahliye,
            self.unpack_hook_diskten_geri_cagır
        )
        return self._aktif_kapsam_muhafizi

    def guvenli_kapat_varsa(self) -> None:
        cm = getattr(self, "_aktif_kapsam_muhafizi", None)
        if cm is not None:
            try:
                cm.__exit__(None, None, None)
            except Exception as _kapat_exc:
                logger.warning(f"[NvmeTakasYoneticisi] Kapsam muhafızı zorla kapatılırken uyarı: {_kapat_exc}")
            finally:
                self._aktif_kapsam_muhafizi = None

    def temizle(self, agresif: bool = False) -> None:
        GuvenliVramVeTmpSupurgesi.supur(swap_dir=self.swap_dir, eskime_esigi_sn=(0.0 if agresif else None))
        logger.info(f"[NvmeTakasYoneticisi] Temizlik tamamlandi. Toplam Tahliye: {self.tahliye_sayaci}, Geri Cagirma: {self.geri_cagirma_sayaci}")

    def kapat(self, timeout: float = 30.0) -> None:
        havuz = getattr(self.offload_hook, "_yazma_havuzu", None)
        if havuz is not None:
            try:
                havuz.shutdown(wait=True, cancel_futures=False)
                logger.info("[NvmeTakasYoneticisi] Yazma iş parçacığı havuzu kapatıldı.")
            except Exception as exc:
                logger.warning(f"[NvmeTakasYoneticisi] İş parçacığı havuzu kapatılırken uyarı: {exc}")

    def __del__(self) -> None:
        try:
            self.kapat(timeout=5.0)
        except Exception:
            pass
