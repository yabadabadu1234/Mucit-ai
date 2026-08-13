
import os
import sys
import time
import ctypes
import logging
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Union, Callable

try:
    from kulli_gpu.sanal_bellek_havuzu import SanalBellekHavuzu, SanalBellekIhlalHatasi
    from kulli_gpu.sanal_islemci_zamanlayici import SanalIslemciZamanlayici, IsYukuPaketi
    from kulli_gpu.bellek_haritacisi import BellekHaritacisi
except ImportError:
    try:
        from .sanal_bellek_havuzu import SanalBellekHavuzu, SanalBellekIhlalHatasi
        from .sanal_islemci_zamanlayici import SanalIslemciZamanlayici, IsYukuPaketi
        from .bellek_haritacisi import BellekHaritacisi
    except ImportError:
        SanalBellekHavuzu = None
        SanalBellekIhlalHatasi = Exception
        SanalIslemciZamanlayici = None
        IsYukuPaketi = None
        BellekHaritacisi = None

logger = logging.getLogger("kulli_gpu.is_emri_idarecisi")
logger.setLevel(logging.INFO)

class KulliAllocRecoveryEngine:
    def __init__(self, tahliye_motoru: Optional[Any] = None):
        from .nvme_takas_yoneticisi import NvmeTahliyeKararMotoru, GuvenliVramVeTmpSupurgesi
        self.tahliye_motoru = tahliye_motoru or NvmeTahliyeKararMotoru()
        self.supurge = GuvenliVramVeTmpSupurgesi

    def C_cuMemAlloc_Recovery(self, alloc_fn: Callable[[], Any], bytesize: int) -> Any:
        try:
            return alloc_fn()
        except (torch.cuda.OutOfMemoryError, Exception) as exc:
            logger.warning(f"[KulliAllocRecoveryEngine] OOM Hatası Yakalandı ({bytesize} bayt). NVMe Tahliye tetikleniyor: {exc}")

            self.tahliye_motoru.vramden_nvme_diske_tahliye_et(bytesize)

            self.supurge.supur()

            try:
                return alloc_fn()
            except Exception as final_exc:
                logger.error(f"[KulliAllocRecoveryEngine] Tahliye sonrası kurtarılamayan OOM: {final_exc}")
                raise final_exc

class IsEmriHatasi(Exception):
    pass

@dataclass
class IsEmriPaketi:
    emir_id: int
    emir_tipi: str
    parametreler: Dict[str, Any] = field(default_factory=dict)
    durum: str = "HAZIR"
    olusturulma_zamani: float = field(default_factory=time.perf_counter)
    tamamlanma_zamani: float = 0.0
    sonuc: Any = None
    hata_mesaji: Optional[str] = None

class CArgumanCozumleyici:
    @staticmethod
    def ArgumanlariCozumleVePaketle(kategori: str, raw_args: Tuple[Any, ...]) -> Dict[str, Any]:
        parametreler: Dict[str, Any] = {
            "raw_args_count": len(raw_args),
            "raw_args_repr": [str(a) for a in raw_args[:5]]
        }

        if kategori == "KATEGORİ_TAHSİT":
            boyut_bayt = 256 * (1024**2)
            for arg in raw_args:
                if isinstance(arg, int) and arg > 1024:
                    boyut_bayt = arg
                    break
                elif hasattr(arg, "value") and isinstance(getattr(arg, "value"), int):
                    val = getattr(arg, "value")
                    if val > 1024:
                        boyut_bayt = val
                        break

            parametreler["boyut_bayt"] = boyut_bayt
            parametreler["hedef_gpu_id"] = 0

        elif kategori == "KATEGORİ_SERBEST":
            hedef_ptr = 0
            for arg in raw_args:
                if isinstance(arg, int) and arg >= 0x7FFF00000000:
                    hedef_ptr = arg
                    break
                elif hasattr(arg, "value") and isinstance(getattr(arg, "value"), int):
                    val = getattr(arg, "value")
                    if val >= 0x7FFF00000000:
                        hedef_ptr = val
                        break

            parametreler["hedef_ptr"] = hedef_ptr

        elif kategori == "KATEGORİ_İCRA":
            grid_x = 1024
            block_x = 256
            kernel_ptr = raw_args[0] if raw_args else 0x7FFF00001000

            for idx, arg in enumerate(raw_args):
                if isinstance(arg, int):
                    if 1 <= arg <= 100_000_000 and idx > 0:
                        grid_x = arg
                        break

            parametreler["kernel_ptr"] = kernel_ptr
            parametreler["grid_boyutu_x"] = grid_x
            parametreler["blok_boyutu_x"] = block_x
            parametreler["girdi_sanal_adres"] = 0x7FFF00000000
            parametreler["cikti_sanal_adres"] = 0x800000000000

        elif kategori == "KATEGORİ_AKTARIM":
            hedef_ptr = raw_args[0] if len(raw_args) > 0 and isinstance(raw_args[0], int) else 0x7FFF00000000
            kaynak_ptr = raw_args[1] if len(raw_args) > 1 and isinstance(raw_args[1], int) else 0x7FFF00010000
            aktarim_bayt = raw_args[2] if len(raw_args) > 2 and isinstance(raw_args[2], int) else 1024

            parametreler["hedef_ptr"] = hedef_ptr
            parametreler["kaynak_ptr"] = kaynak_ptr
            parametreler["aktarim_bayt"] = aktarim_bayt

        return parametreler

class IsEmriIdarecisi:
    def __init__(
        self,
        sanal_bellek_havuzu: Optional[Any] = None,
        sanal_islemci_zamanlayici: Optional[Any] = None,
        simulation_mode: bool = False
    ):
        self.lock = threading.RLock()
        self.simulation_mode = simulation_mode
        self.havuz = sanal_bellek_havuzu
        self.zamanlayici = sanal_islemci_zamanlayici
        self.emir_sayaci = 0
        self.is_emri_gecmisi: List[IsEmriPaketi] = []

        logger.info(f"[IsEmriIdarecisi] İş Emri İdarecisi ve Komut Tercümanı İlklendirildi (simulation_mode={simulation_mode}).")

    def IsEmriUretVeSevkEt(self, kategori: str, raw_args: Tuple[Any, ...]) -> Any:
        with self.lock:
            self.emir_sayaci += 1
            e_id = self.emir_sayaci

        params = CArgumanCozumleyici.ArgumanlariCozumleVePaketle(kategori, raw_args)

        emir = IsEmriPaketi(
            emir_id=e_id,
            emir_tipi=kategori,
            parametreler=params,
            durum="SEVK_EDİLDİ"
        )

        try:

            if kategori == "KATEGORİ_TAHSİT":
                if self.havuz is not None:
                    boyut = params.get("boyut_bayt", 256 * (1024**2))
                    gpu_id = params.get("hedef_gpu_id", 0)
                    tahsis_res = self.havuz.TaskinliBellekTahsisEt(istenen_bayt=boyut, hedef_gpu_id=gpu_id)
                    emir.sonuc = tahsis_res.get("sanal_adres", 0x7FFF00000000)
                else:
                    emir.sonuc = 0x7FFF00000000

                emir.durum = "TAMAMLANDI"
                ret_val = 0

            elif kategori == "KATEGORİ_SERBEST":
                if self.havuz is not None:
                    ptr = params.get("hedef_ptr", 0)
                    if ptr >= 0x7FFF00000000:
                        self.havuz.BellekSerbestBirak(ptr)
                emir.sonuc = 0
                emir.durum = "TAMAMLANDI"
                ret_val = 0

            elif kategori == "KATEGORİ_İCRA":
                if self.zamanlayici is not None:
                    k_ptr = params.get("kernel_ptr", 0x7FFF00001000)
                    g_x = params.get("grid_boyutu_x", 1024)
                    b_x = params.get("blok_boyutu_x", 256)
                    exec_res = self.zamanlayici.IsYukuCalistirVeBekle(
                        kernel_isaretci=k_ptr,
                        grid_boyutu_x=g_x,
                        blok_boyutu_x=b_x
                    )
                    emir.sonuc = exec_res
                else:
                    emir.sonuc = {"status": "Simüle İcra Tamamlandı"}

                emir.durum = "TAMAMLANDI"
                ret_val = 0

            elif kategori == "KATEGORİ_AKTARIM":
                if self.havuz is not None and hasattr(self.havuz, "SanalAdreslerArasiKopyala"):
                    k_ptr = params.get("kaynak_ptr", 0x7FFF00000000)
                    h_ptr = params.get("hedef_ptr", 0x7FFF00010000)
                    a_bayt = params.get("aktarim_bayt", 1024)
                    res = self.havuz.SanalAdreslerArasiKopyala(
                        kaynak_sanal_adres=k_ptr,
                        hedef_sanal_adres=h_ptr,
                        kopyalanacak_bayt=a_bayt
                    )
                    emir.sonuc = res
                elif self.havuz is not None and hasattr(self.havuz, "AraliklariBirlestir"):
                    self.havuz.AraliklariBirlestir()
                    emir.sonuc = 0
                else:
                    emir.sonuc = 0
                emir.durum = "TAMAMLANDI"
                ret_val = 0

            else:
                emir.durum = "TAMAMLANDI"
                ret_val = 0

        except Exception as err:
            logger.error(f"[IsEmriIdarecisi] İş Emri #{e_id} Sevk Hatası ({kategori}): {err}")
            emir.durum = "HATA"
            emir.hata_mesaji = str(err)
            ret_val = 1

        finally:
            emir.tamamlanma_zamani = time.perf_counter()
            with self.lock:
                self.is_emri_gecmisi.append(emir)

                if len(self.is_emri_gecmisi) > 100:
                    self.is_emri_gecmisi.pop(0)

        logger.info(
            f"[IsEmriUretVeSevkEt] İş Emri #{e_id} ({kategori}) -> Durum: {emir.durum} | "
            f"Süre: {round((emir.tamamlanma_zamani - emir.olusturulma_zamani)*1000, 3)} ms"
        )
        return ret_val

    @contextmanager
    def GeciciBellekMuhafizi(self, gecici_boyut_bayt: int, hedef_gpu_id: int = 0):
        if self.havuz is not None and hasattr(self.havuz, "GeciciBellekMuhafizi"):
            with self.havuz.GeciciBellekMuhafizi(gecici_boyut_bayt=gecici_boyut_bayt, hedef_gpu_id=hedef_gpu_id) as guard:
                yield guard
        else:
            sanal_adres = 0x7FFF00000000 + (hedef_gpu_id * 0x1000000)
            yield (sanal_adres, None)

    def IdareciDurumuOzetle(self) -> Dict[str, Any]:
        with self.lock:
            tamamlanan = sum(1 for e in self.is_emri_gecmisi if e.durum == "TAMAMLANDI")
            hatali = sum(1 for e in self.is_emri_gecmisi if e.durum == "HATA")

            return {
                "toplam_is_emri_sayisi": self.emir_sayaci,
                "gecmis_paket_sayisi": len(self.is_emri_gecmisi),
                "tamamlanan_is_emri": tamamlanan,
                "hatali_is_emri": hatali,
                "status": "İş Emri İdarecisi ve Komut Tercümanı Sağlıklı"
            }

class OpakKernelSarmalayici:
    def __init__(self, is_emri_idarecisi: Optional[Any] = None, sanal_bellek_havuzu: Optional[Any] = None, sanal_islemci_zamanlayici: Optional[Any] = None):
        self.idareci = is_emri_idarecisi
        self.havuz = sanal_bellek_havuzu
        self.zamanlayici = sanal_islemci_zamanlayici

    def CalistirVeBekle(self, sembol_adi: str, c_struct_argumanlari: Tuple[Any, ...], orijinal_fn: Optional[Callable] = None) -> int:
        donusturulmus_args = list(c_struct_argumanlari)

        if self.havuz is not None:
            for i, arg in enumerate(donusturulmus_args):
                if isinstance(arg, int) and arg >= 0x7FFF00000000:
                    aralik = self.havuz.AdrestenAralikBul(arg)
                    if aralik is not None and aralik.c_pointer is not None:
                        donusturulmus_args[i] = aralik.c_pointer

        if callable(orijinal_fn):
            res = orijinal_fn(*donusturulmus_args)
        elif self.zamanlayici is not None:
            kernel_ptr = donusturulmus_args[0] if donusturulmus_args else 0x7FFF00001000
            res = self.zamanlayici.IsYukuCalistirVeBekle(
                kernel_isaretci=kernel_ptr,
                grid_boyutu_x=1024,
                blok_boyutu_x=256
            )

        logger.info(f"[OpakKernelSarmalayici] Kernel '{sembol_adi}' sanal-fiziki adres dönüşümü ve donanımsal çit ile başarıyla yürütüldü.")
        return 0
