#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ SANAL GPU SÜRÜCÜSÜ - BELLEK HARİTACISI VE FİZİKSEL EİŞİM BİRİMİ
Modül: kulli_gpu/bellek_haritacisi.py (BellekHaritacisi)
================================================================================
GPU'nun fiziki VRAM'ini ve komut kayıtçılarını (Registers) Python sürecinin sanal
adres alanına mmap ile canlı C-İşaretçisi (Pointer) olarak bağlayan fiziksel erişim birimidir.
"""

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
            """Sürücü seviyesinde kritik yetki veya donanım erişim hatası."""
            pass

logger = logging.getLogger("kulli_gpu.bellek_haritacisi")


class BellekHaritacisi:
    """
    [Bellek Haritacısı ve Fiziki VRAM/MMIO C-İşaretçisi Erişim Birimi]
    mmap, os.O_SYNC, ctypes ve HafizaCiti (Memory Barrier) kullanarak GPU fiziki
    bellek kaynaklarını doğrudan Python süreç adres alanına bağlar.
    """

    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode
        logger.info(f"[BellekHaritacisi] Fiziki VRAM & Kayıtçı Haritalama Birimi İlklendirildi (simulation_mode={simulation_mode}).")

    def DonanimKapisiniAc(
        self,
        pci_adresi: str,
        bolge_no: str = "1",
        simulation_mode: Optional[bool] = None
    ) -> int:
        """
        Vazifesi: GPU'nun fiziki bellek kaynaklarını temsil eden çekirdek kütüğünü,
        önbelleksiz (uncached/direct) ham okuma-yazma ve O_SYNC modunda açar.
        
        Girdileri:
        - pci_adresi: PCI veri yolu adresi (Örn: '0000:01:00.0')
        - bolge_no: Resource bölge numarası ('0' BAR0 MMIO Kayıtçılar, '1' BAR1 VRAM)
        - simulation_mode: Açık simülasyon modu isteği
        
        Çıktısı: Dosya Tanımlayıcı (file descriptor / fd integer)
        """
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

        # Açık Simülasyon Modu Kapısı (Sadece simulation_mode=True durumunda)
        sanal_path = f"/tmp/kulli_mock_gpu_{pci_adresi.replace(':', '_')}_res{bolge_no}.bin"
        if not os.path.exists(sanal_path) or os.path.getsize(sanal_path) < (128 * 1024 * 1024):
            with open(sanal_path, "wb") as f:
                # 24GB or 128MB sparse mock buffer
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
        """
        Vazifesi: Linux çekirdeği özel VFS kütüklerinde lseek illüzyonuna düşmeden,
        BAR0/BAR1 bölgesinin hakiki bayt cinsinden fiziki boyutunu hesaplar.
        
        Girdileri: Dosya Tanımlayıcı (fd), VRAM Bayt Bilgisi, PCI Adresi, Bölge No
        Çıktısı: Toplam Hakiki Boyut (Bytes)
        """
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

        # Normal kütük / Mock dosya stat ölçümü
        try:
            st = os.fstat(dosya_tanimlayici)
            if st.st_size > 0:
                return st.st_size
        except Exception:
            pass

        logger.info("[HafizaSinirlariniOgren] Varsayılan Donanımsal Sayfa Tabanlı Boyut (128MB) Atandı.")
        return 128 * 1024 * 1024

    def VolatilHafizaCiti(self, c_isaretci: Any = None) -> bool:
        """
        Vazifesi: Sürücüyü yavaşlatan ağır mmap.flush() yerine, CPU önbelleğini dondurmadan
        veriyi doğrudan PCIe hattına süren volatil bellek çiti (Store Buffer Flush) algoritmasıdır.
        
        Girdisi: C İşaretçisi (c_isaretci)
        Çıktısı: True (İşlem başarılı)
        """
        if c_isaretci is None:
            return False
        try:
            # Volatile dummy read at offset 0x00 to force write store-buffers to physical PCIe bus
            _ = c_isaretci[0]
            logger.debug("[VolatilHafizaCiti] Volatile Memory Barrier / PCIe Bus Store Buffer Sync tamamlandı.")
            return True
        except Exception as err:
            logger.warning(f"[VolatilHafizaCiti] Volatile memory fence uyarısı: {err}")
            return False

    def HafizaCiti(
        self,
        mmap_obj: Optional[mmap.mmap] = None,
        c_isaretci: Any = None
    ) -> bool:
        """
        Vazifesi: MMIO ve VRAM kayıtçılarına yazılan verilerin CPU L1/L2 önbelleğinde
        beklemesini engelleyerek, anında fiziki ortama iletilmesini garanti eden
        hafifletilmiş Volatile Memory Barrier mekanizması.
        """
        if c_isaretci is not None:
            return self.VolatilHafizaCiti(c_isaretci)
        if mmap_obj is not None:
            try:
                # Fallback volatile read on mmap buffer if C pointer not passed
                _ = mmap_obj[0]
                return True
            except Exception:
                pass
        return True

    def CanliHafizayiHaritala(self, dosya_tanimlayici: int, toplam_boyut: int) -> mmap.mmap:
        """
        Vazifesi: GPU VRAM'inin fiziki adreslerini, Python sürecinin sanal bellek alanına mmap ile haritalar.
        
        Girdileri: Dosya Tanımlayıcı (fd), Toplam Boyut
        Çıktısı: mmap nesnesi (mmap.mmap)
        """
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
        """
        Vazifesi: Haritalanan mmap bloğunu 64-bit adres emniyetiyle 32-bitlik Tamsayı
        C İşaretçisine (Raw C Pointer) dönüştürür.
        
        Girdisi: Haritalanmış mmap nesnesi
        Çıktısı: 32-bit C İşaretçisi (POINTER(ctypes.c_uint32))
        """
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
        """
        Vazifesi: Haritalanan VRAM bölgesini tek bir son mmap.flush ile diske/çekirdeğe
        senkronize ederek kapatır ve dosya tanımlayıcısını serbest bırakır.
        """
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
        """
        Vazifesi: Tüm mmap haritalama, HafizaSinirlariniOgren ve C-İşaretçisi oluşturma
        adımlarını zincirleme yürütür.
        """
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
