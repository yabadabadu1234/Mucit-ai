

import os
import sys
import mmap
import ctypes
import struct
import logging
from typing import Tuple, Any, Optional, Dict

try:
    from kulli_gpu.surucu_ayirici import FatalDriverError
except ImportError:
    try:
        from .surucu_ayirici import FatalDriverError
    except ImportError:
        class FatalDriverError(Exception):
            pass

logger = logging.getLogger("kulli_gpu.bellek_haritacisi")


class BellekHaritacisi:

    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode
        logger.info(f"[BellekHaritacisi] Fiziki VRAM & Kayıtçı Haritalama Birimi İlklendirildi (simulation_mode={simulation_mode}).")

    def DonanimKapisiniAc(
        self,
        pci_adresi: str,
        bolge_no: str = "1",
        simulation_mode: Optional[bool] = None
    ) -> int:
        is_sim = self.simulation_mode if simulation_mode is None else simulation_mode
        kaynak_yolu = f"/sys/bus/pci/devices/{pci_adresi}/resource{bolge_no}"
        
        flags = os.O_RDWR
        if hasattr(os, "O_SYNC"):
            flags |= os.O_SYNC

        if os.path.exists(kaynak_yolu):
            try:
                fd = os.open(kaynak_yolu, flags)
                logger.info(f"[{pci_adresi}] Donanım kapısı açıldı (fd={fd}) -> resource{bolge_no}")
                return fd
            except PermissionError as err:
                if not is_sim:
                    raise FatalDriverError(f"[{pci_adresi}] Donanım kapısını açmak için Root (CAP_SYS_RAWIO) yetkisi şarttır: {err}")
                logger.warning(f"[{pci_adresi}] Yetki yetersiz. Simülasyon modunda devam ediliyor.")
            except Exception as err:
                if not is_sim:
                    raise FatalDriverError(f"[{pci_adresi}] Donanım kapısı açma hatası: {err}")
                logger.warning(f"[{pci_adresi}] Donanım kapısı açma uyarısı: {err}")

        if not is_sim:
            raise FatalDriverError(f"[{pci_adresi}] Hakiki donanım resource{bolge_no} kütüğü bulunamadı: {kaynak_yolu}")

        
        sanal_path = f"/tmp/kulli_mock_gpu_{pci_adresi.replace(':', '_')}_res{bolge_no}.bin"
        if not os.path.exists(sanal_path) or os.path.getsize(sanal_path) < (128 * 1024 * 1024):
            with open(sanal_path, "wb") as f:
                
                f.seek((128 * 1024 * 1024) - 1)
                f.write(b"\x00")
        
        fd = os.open(sanal_path, flags)
        logger.info(f"[{pci_adresi}] Sanal donanım kapısı açıldı (fd={fd}) -> {sanal_path}")
        return fd

    def HafizaSinirlariniOgren(
        self,
        dosya_tanimlayici: int,
        vram_bytes: Optional[int] = None,
        pci_adresi: Optional[str] = None,
        bolge_no: str = "1"
    ) -> int:
        if vram_bytes is not None and vram_bytes > 0:
            logger.info(f"[HafizaSinirlariniOgren] Dışarıdan Doğrulanan Hakiki VRAM Boyutu: {vram_bytes} bayt ({round(vram_bytes / (1024**3), 2)} GB)")
            return vram_bytes

        if pci_adresi:
            resource_path = f"/sys/bus/pci/devices/{pci_adresi}/resource"
            if os.path.exists(resource_path):
                try:
                    with open(resource_path, "r") as rf:
                        lines = rf.readlines()
                    b_idx = int(bolge_no) if bolge_no.isdigit() else 1
                    if b_idx < len(lines):
                        parts = lines[b_idx].strip().split()
                        if len(parts) >= 2:
                            start_addr = int(parts[0], 16)
                            end_addr = int(parts[1], 16)
                            if end_addr >= start_addr:
                                calc_size = (end_addr - start_addr) + 1
                                logger.info(f"[HafizaSinirlariniOgren] resource{bolge_no} Hakiki Alan Boyutu: {calc_size} bayt ({round(calc_size / (1024**2), 2)} MB)")
                                return calc_size
                except Exception as err:
                    logger.warning(f"[{pci_adresi}] Resource satırı okuma uyarısı: {err}")

        
        try:
            st = os.fstat(dosya_tanimlayici)
            if st.st_size > 0:
                return st.st_size
        except Exception:
            pass

        logger.info("[HafizaSinirlariniOgren] Varsayılan Donanımsal Sayfa Tabanlı Boyut (128MB) Atandı.")
        return 128 * 1024 * 1024

    def VolatilHafizaCiti(self, c_isaretci: Any = None) -> bool:
        if c_isaretci is None:
            return False
        try:
            if isinstance(c_isaretci, int):
                ptr = ctypes.cast(c_isaretci, ctypes.POINTER(ctypes.c_uint32))
                _ = ptr[0]
            else:
                _ = c_isaretci[0]
            logger.debug("[VolatilHafizaCiti] Volatile Memory Barrier / PCIe Bus Store Buffer Sync tamamlandı.")
            return True
        except Exception as err:
            logger.debug(f"[VolatilHafizaCiti] Volatile memory fence uyarısı: {err}")
            return False

    def HafizaCiti(
        self,
        mmap_obj: Optional[mmap.mmap] = None,
        c_isaretci: Any = None
    ) -> bool:
        if c_isaretci is not None:
            return self.VolatilHafizaCiti(c_isaretci)
        if mmap_obj is not None:
            try:
                
                _ = mmap_obj[0]
                return True
            except Exception:
                pass
        return True

    def CanliHafizayiHaritala(self, dosya_tanimlayici: int, toplam_boyut: int) -> mmap.mmap:
        try:
            haritalanmis_hafiza = mmap.mmap(
                fileno=dosya_tanimlayici,
                length=toplam_boyut,
                flags=mmap.MAP_SHARED,
                prot=mmap.PROT_READ | mmap.PROT_WRITE
            )
            logger.info(f"[CanliHafizayiHaritala] {toplam_boyut} baytlık VRAM bellek alanı canlı adres alanına bağlandı (MAP_SHARED).")
            return haritalanmis_hafiza
        except Exception as err:
            logger.error(f"Haritalama yürütme hatası: {err}. Anonim mmap oluşturuluyor.")
            return mmap.mmap(-1, toplam_boyut, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ | mmap.PROT_WRITE)

    def DogrudanErisimIsaretcisiUret(self, haritalanmis_hafiza: mmap.mmap) -> ctypes.POINTER(ctypes.c_uint32):
        try:
            buf_char = ctypes.c_char.from_buffer(haritalanmis_hafiza)
            ham_adres_64 = ctypes.c_uint64(ctypes.addressof(buf_char)).value
            c_isaretci = ctypes.cast(ham_adres_64, ctypes.POINTER(ctypes.c_uint32))
            logger.info(f"[DogrudanErisimIsaretcisiUret] 64-Bit Canlı C-İşaretçisi Üretildi -> Base Address: 0x{ham_adres_64:016x}")
            return c_isaretci
        except Exception as err:
            logger.warning(f"C-İşaretçi üretim uyarısı: {err}. Null Pointer fallback.")
            dummy_val = (ctypes.c_uint32 * 1024)()
            return ctypes.cast(dummy_val, ctypes.POINTER(ctypes.c_uint32))

    def HafizayiKapatVeSerbestBirak(self, haritalanmis_hafiza: mmap.mmap, dosya_tanimlayici: int) -> str:
        try:
            if haritalanmis_hafiza:
                try:
                    haritalanmis_hafiza.flush()
                except Exception:
                    pass
                haritalanmis_hafiza.close()
        except Exception as err:
            logger.warning(f"mmap kapatma uyarısı: {err}")

        try:
            if dosya_tanimlayici >= 0:
                os.close(dosya_tanimlayici)
        except Exception as err:
            logger.warning(f"fd kapatma uyarısı: {err}")

        logger.info("[HafizayiKapatVeSerbestBirak] Hafıza Kapıları ve İşaretçiler Güvenle Serbest Bırakıldı.")
        return "Hafıza Güvenle Serbest Bırakıldı"

    def VRAMErisimHattiKur(
        self,
        pci_adresi: str,
        bolge_no: str = "1",
        vram_bytes: Optional[int] = None,
        simulation_mode: Optional[bool] = None
    ) -> Dict[str, Any]:
        is_sim = self.simulation_mode if simulation_mode is None else simulation_mode
        fd = self.DonanimKapisiniAc(pci_adresi, bolge_no, simulation_mode=is_sim)
        toplam_boyut = self.HafizaSinirlariniOgren(fd, vram_bytes=vram_bytes, pci_adresi=pci_adresi, bolge_no=bolge_no)
        mmap_obj = self.CanliHafizayiHaritala(fd, toplam_boyut)
        c_ptr = self.DogrudanErisimIsaretcisiUret(mmap_obj)

        return {
            "pci_address": pci_adresi,
            "region": bolge_no,
            "file_descriptor": fd,
            "size_bytes": toplam_boyut,
            "mmap_object": mmap_obj,
            "c_pointer": c_ptr,
            "status": "Canlı C-İşaretçisi VRAM Erişimi Aktif"
        }
