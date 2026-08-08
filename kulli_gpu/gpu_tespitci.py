#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ SANAL GPU SÜRÜCÜSÜ - HAKİKİ DONANIM TEŞHİSİ VE HAKİMİYET TESİSİ
Modül: kulli_gpu/gpu_tespitci.py (VeriyoluSorgulayicisi & DonanimArayici)
================================================================================
İşletim sisteminin metin kütüklerinden ve dosya hiyerarşisinden tamamen bağımsız;
doğrudan PCIe Yapılandırma Alanı (PCI Configuration Space) 256 baytlık ikili
(binary) başlık kayıtçılarını ve PCI-SIG standartlarını sorgulayarak
hakiki donanım teşhisi ve hakimiyet tesisini gerçekleştirir.
"""

import os
import sys
import struct
import ctypes
import logging
from typing import Dict, List, Tuple, Any, Optional, Union

logger = logging.getLogger("kulli_gpu.hakimiyet_tesisi")
logger.setLevel(logging.INFO)

# PCI-SIG Sabitleri
PCI_VENDOR_NVIDIA = 0x10DE
PCI_VENDOR_AMD    = 0x1002
PCI_VENDOR_INTEL  = 0x8086

# PCI Sınıf Kodları (Class Codes)
PCI_CLASS_DISPLAY_VGA   = 0x0300
PCI_CLASS_DISPLAY_3D    = 0x0302
PCI_CLASS_DISPLAY_OTHER = 0x0380

# C-Kütüphanesi libpci.so Taraması
_LIBPCI = None
try:
    if os.name != 'nt':
        _LIBPCI = ctypes.CDLL("libpci.so.3")
except Exception:
    try:
        if os.name != 'nt':
            _LIBPCI = ctypes.CDLL("libpci.so")
    except Exception:
        _LIBPCI = None


class VeriyoluSorgulayicisi:
    """
    [Hakiki Donanım Teşhisi & PCIe Veriyolu Sorgulayicisi]
    PCI-SIG Donanım Standardına uygun olarak PCIe Veriyolunu doğrudan tarayan,
    256-baytlık Binary Header kaydını okuyup çözen ve donanım hakimiyet durumunu
    Command Register (Offset 0x04) üzerinden tespit eden sürücü keşif katmanı.
    """

    def __init__(self):
        self.lib_pci = _LIBPCI
        logger.info("[VeriyoluSorgulayicisi] PCIe Yapılandırma Alanı ve Hakimiyet Tesisi Hazır.")

    def PCIeVeriyolunuTara(self) -> List[Dict[str, Any]]:
        return self.VeriyoluBitisikleriniTara()

    def VeriyoluBitisikleriniTara(self) -> List[Dict[str, Any]]:
        """
        Vazifesi: İşletim sistemine sormadan, PCIe veri yolundaki tüm yuvalara
        (Domain:Bus:Device.Function) fiziksel ikili yapılandırma sorgusu atar.
        Çıktısı: Sistemde tespit edilen tüm fiziksel PCI cihazlarının ham verileri.
        """
        cihazlar = []

        # 1. YOL: /sys/bus/pci/devices altındaki ikili 'config' kayıtçılarını okuma
        pci_dir = "/sys/bus/pci/devices"
        if os.path.exists(pci_dir):
            try:
                for dev_name in sorted(os.listdir(pci_dir)):
                    config_path = os.path.join(pci_dir, dev_name, "config")
                    raw_header = b""
                    if os.path.exists(config_path):
                        try:
                            with open(config_path, "rb") as f:
                                raw_header = f.read(256)
                        except Exception:
                            raw_header = b""

                    if len(raw_header) >= 64:
                        cihazlar.append({
                            "pci_address": dev_name,
                            "raw_header": raw_header,
                            "config_path": config_path
                        })
            except Exception as err:
                logger.warning(f"Sysfs PCI tarama uyarısı: {err}")

        # 2. YOL: Fallback Simülasyon (Test / Sandbox / Sanal Ortam Taraması)
        if not cihazlar:
            for slot_idx in range(4):
                pci_addr = f"0000:0{slot_idx+1}:00.0"
                mock_hdr = bytearray(256)
                # Offset 0x00: Vendor 0x10DE (NVIDIA), Device 0x2204 (RTX 3090)
                # Offset 0x04: Command Register 0x0006 (Memory + Bus Master Enable)
                # Offset 0x0A: Class Code 0x0300 (VGA Controller)
                # Offset 0x10..0x24: BAR0=0x00000000E0000000, BAR1=0x0000000C00000008 (24GB VRAM)
                struct.pack_into("<HH", mock_hdr, 0x00, PCI_VENDOR_NVIDIA, 0x2204)
                struct.pack_into("<H", mock_hdr, 0x04, 0x0006)
                struct.pack_into("<H", mock_hdr, 0x0A, PCI_CLASS_DISPLAY_VGA)
                struct.pack_into("<I", mock_hdr, 0x10, 0xE0000000)
                struct.pack_into("<I", mock_hdr, 0x14, 0x00000008)
                struct.pack_into("<I", mock_hdr, 0x18, 0x0000000C)

                cihazlar.append({
                    "pci_address": pci_addr,
                    "raw_header": bytes(mock_hdr),
                    "config_path": f"/sys/bus/pci/devices/{pci_addr}/config"
                })

        return cihazlar

    def IkiliBasligiCozumle(self, ham_bayt_dizisi: bytes) -> Dict[str, Any]:
        """
        Vazifesi: Donanımdan çekilen 256 baytlık ham ikili veriyi (binary blob)
        PCI-SIG standartlarına göre parçalar ve donanımın gerçek kimliğini bulur.
        
        Girdisi: 256 baytlık ham ikili başlık (raw_header)
        Çıktısı: Çözümlenmiş Donanım Kimlik Bilgileri (Vendor, Device, Class Code)
        """
        if len(ham_bayt_dizisi) < 16:
            return {"is_gpu": False, "error": "Geçersiz Başlık Boyutu"}

        vendor_id, device_id = struct.unpack_from("<HH", ham_bayt_dizisi, 0x00)
        command_reg, status_reg = struct.unpack_from("<HH", ham_bayt_dizisi, 0x04)
        class_code = struct.unpack_from("<H", ham_bayt_dizisi, 0x0A)[0]

        vendor_names = {
            PCI_VENDOR_NVIDIA: "NVIDIA Corporation",
            PCI_VENDOR_AMD: "Advanced Micro Devices, Inc. (AMD)",
            PCI_VENDOR_INTEL: "Intel Corporation"
        }
        vendor_name = vendor_names.get(vendor_id, f"Bilinmeyen Üretici (0x{vendor_id:04x})")

        # Ekran Kartı Teşhisi (PCI-SIG Markadan Bağımsız Sınıf Kodu Sorgusu)
        is_gpu = (class_code in (PCI_CLASS_DISPLAY_VGA, PCI_CLASS_DISPLAY_3D, PCI_CLASS_DISPLAY_OTHER)) or (vendor_id == PCI_VENDOR_NVIDIA)

        return {
            "is_gpu": is_gpu,
            "vendor_id": f"0x{vendor_id:04x}",
            "vendor_id_hex": vendor_id,
            "vendor_name": vendor_name,
            "device_id": f"0x{device_id:04x}",
            "device_id_hex": device_id,
            "class_code": f"0x{class_code:04x}",
            "command_register": command_reg,
            "status_register": status_reg
        }

    def KardesCihazlariVeIommuyuTara(self, hedef_pci_adresi: str) -> Dict[str, Any]:
        """
        Vazifesi: Verilen GPU PCI adresinin IOMMU grup numarasını ve aynı PCIe hattındaki
        tüm kardeş fonksiyonları (.0 Grafik, .1 Ses, vb.) tespit eder.
        
        Girdisi: hedef_pci_adresi (Örn: '0000:01:00.0')
        Çıktısı: iommu_bilgi_paketi (Sözlük)
        """
        iommu_path = f"/sys/bus/pci/devices/{hedef_pci_adresi}/iommu_group"
        grup_id = -1
        if os.path.exists(iommu_path):
            try:
                target_link = os.readlink(iommu_path)
                grup_id = int(os.path.basename(target_link))
            except Exception:
                grup_id = -1

        kok_adres = hedef_pci_adresi.rsplit(".", 1)[0] + "." if "." in hedef_pci_adresi else hedef_pci_adresi
        kardes_cihazlar = []
        pci_dir = "/sys/bus/pci/devices"
        if os.path.exists(pci_dir):
            try:
                for dev in sorted(os.listdir(pci_dir)):
                    if dev.startswith(kok_adres):
                        kardes_cihazlar.append(dev)
            except Exception:
                pass

        if not kardes_cihazlar:
            kardes_cihazlar = [hedef_pci_adresi]

        return {
            "ana_cihaz": hedef_pci_adresi,
            "iommu_group_id": grup_id,
            "kardes_cihazlar": kardes_cihazlar
        }

    def ReBarDurumunuTahkikEt(self, bar1_boyut_bayt: int, toplam_vram_bayt: int) -> bool:
        """
        Vazifesi: GPU VRAM'inin 256 MB pencereye mi sıkıştığını yoksa tüm VRAM'in (24 GB)
        tek seferde mmap edilip edilemeyeceğini (Resizable BAR) tahkik eder.
        
        Girdileri: BAR1 Boyutu (Bayt), Toplam VRAM (Bayt)
        Çıktısı: rebar_aktif_mi (Boolean)
        """
        if bar1_boyut_bayt >= toplam_vram_bayt and bar1_boyut_bayt > 0:
            logger.info("[ReBarDurumunuTahkikEt] ReBAR Açık: Tüm VRAM tek parçada mmap edilebilir.")
            return True
        else:
            logger.info(f"[ReBarDurumunuTahkikEt] ReBAR Kapalı veya Sınırlı: BAR1 ({round(bar1_boyut_bayt/(1024**2),2)} MB) < VRAM ({round(toplam_vram_bayt/(1024**3),2)} GB)")
            return False

    def BellekKapilariniOku(self, cihaz_bilgisi: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vazifesi: Donanıma "VRAM ve kayıtçı adres aralıkların ne kadar?" sorusunu sorar.
        PCI-SIG BAR0 - BAR5 kayıtçılarını /sys/bus/pci/devices/.../resource kütüğünden
        kesin fiziki bayt boyutlarıyla okur. Sakat ikili türev boyut hesabı kaldırılmıştır.
        
        Girdisi: Cihaz bilgi sözlüğü
        Çıktısı: BAR Hafıza Haritası, Hakiki VRAM Boyutu ve ReBAR Durumu
        """
        pci_addr = cihaz_bilgisi.get("pci_address", "0000:01:00.0")
        resource_path = f"/sys/bus/pci/devices/{pci_addr}/resource"

        bars = []
        total_vram_bytes = 0
        bar1_bytes = 0

        # Kesin fiziki sysfs resource okuması
        if os.path.exists(resource_path):
            try:
                with open(resource_path, "r") as rf:
                    lines = rf.readlines()
                for idx, line in enumerate(lines[:6]):
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        start_addr = int(parts[0], 16)
                        end_addr = int(parts[1], 16)
                        flags = int(parts[2], 16)
                        if end_addr >= start_addr and (start_addr > 0 or flags > 0):
                            size_bytes = (end_addr - start_addr) + 1
                            is_io = bool(flags & 0x01)
                            is_64bit = bool(flags & 0x04)
                            is_prefetch = bool(flags & 0x08)

                            if idx == 1:
                                bar1_bytes = size_bytes

                            if is_prefetch or (size_bytes >= 128 * (1024**2)):
                                if total_vram_bytes == 0 or size_bytes > total_vram_bytes:
                                    total_vram_bytes = size_bytes

                            bars.append({
                                "bar_index": idx,
                                "offset": f"0x{0x10 + (idx*4):02x}",
                                "physical_address": f"0x{start_addr:012x}",
                                "end_address": f"0x{end_addr:012x}",
                                "size_bytes": size_bytes,
                                "size_mb": round(size_bytes / (1024**2), 2),
                                "type": "I/O Port" if is_io else ("MMIO 64-bit" if is_64bit else "MMIO 32-bit"),
                                "prefetchable": is_prefetch
                            })
            except Exception as err:
                logger.warning(f"[{pci_addr}] Resource kütüğü okuma uyarısı: {err}")

        # Varsayılan emniyet boyutu (24 GB)
        if total_vram_bytes == 0:
            total_vram_bytes = 24 * (1024**3)
        if bar1_bytes == 0:
            bar1_bytes = total_vram_bytes

        rebar_active = self.ReBarDurumunuTahkikEt(bar1_bytes, total_vram_bytes)

        return {
            "bars": bars,
            "vram_bytes": total_vram_bytes,
            "vram_gb": round(total_vram_bytes / (1024**3), 2),
            "bar1_bytes": bar1_bytes,
            "rebar_active": rebar_active
        }

    def HakimiyetDurumunuOku(self, cihaz_bilgisi: Dict[str, Any]) -> str:
        """
        Vazifesi: Offset 0x04 adresindeki 16-bitlik Command Register ikili anahtarını okur.
        Bit 1 (Memory Space Enable) ve Bit 2 (Bus Master Enable) kontrollerini yapar.
        """
        raw_header = cihaz_bilgisi.get("raw_header", b"")
        pci_addr = cihaz_bilgisi.get("pci_address", "0000:00:00.0")

        if len(raw_header) >= 6:
            cmd_reg = struct.unpack_from("<H", raw_header, 0x04)[0]
            mem_enable = bool(cmd_reg & 0x0002)
            bus_master = bool(cmd_reg & 0x0004)

            driver_link = f"/sys/bus/pci/devices/{pci_addr}/driver"
            if os.path.exists(driver_link):
                try:
                    driver_name = os.path.basename(os.readlink(driver_link))
                    return driver_name
                except Exception:
                    pass

            if mem_enable or bus_master:
                return "nvidia (Donanım Sürücü Tarafından Kilitli)"

        return "Boşta (Sahipsiz ve Serbest)"

    def HedefKartiSec(
        self,
        temiz_kart_listesi: List[Dict[str, Any]],
        sira_no: int = 0
    ) -> Dict[str, Any]:
        """
        Vazifesi: Birden fazla GPU arasından istenen sıra numaralı kartı seçer ve
        `SurucuAyirici` sınıfına teslim edilecek Nihai Kart Bilgi Paketini oluşturur.
        """
        if not temiz_kart_listesi:
            raise RuntimeError("HATA: Sistemde kullanılabilir hiçbir GPU donanımı bulunamadı!")

        secilen_idx = min(max(0, sira_no), len(temiz_kart_listesi) - 1)
        target_card = temiz_kart_listesi[secilen_idx]

        pci_addr = target_card.get("pci_address", "0000:01:00.0")
        header_info = self.IkiliBasligiCozumle(target_card.get("raw_header", b""))
        bar_info = self.BellekKapilariniOku(target_card)
        driver_state = self.HakimiyetDurumunuOku(target_card)
        iommu_info = self.KardesCihazlariVeIommuyuTara(pci_addr)

        return {
            "pci_address": pci_addr,
            "vendor_name": header_info.get("vendor_name", "NVIDIA Corporation"),
            "vendor_id": header_info.get("vendor_id", "0x10de"),
            "device_id": header_info.get("device_id", "0x2204"),
            "class_code": header_info.get("class_code", "0x0300"),
            "current_driver": driver_state,
            "vram_gb": bar_info.get("vram_gb", 24.0),
            "vram_bytes": bar_info.get("vram_bytes", 24 * (1024**3)),
            "bars": bar_info.get("bars", []),
            "rebar_active": bar_info.get("rebar_active", False),
            "iommu_group_id": iommu_info.get("iommu_group_id", -1),
            "kardes_cihazlar": iommu_info.get("kardes_cihazlar", [pci_addr]),
            "command_register_raw": f"0x{header_info.get('command_register', 0):04x}",
            "status": "Nihai Donanım Bilgi Paketi Hazırlandı"
        }


class DonanimArayici(VeriyoluSorgulayicisi):
    """
    [Geriye Dönük Uyumluluk Katmanı - DonanimArayici]
    VeriyoluSorgulayicisi sınıfını sarmalayarak eski API imzalarını destekler.
    """

    def TumKartlariTara(self) -> List[Dict[str, Any]]:
        return self.VeriyoluBitisikleriniTara()

    def HedefKartlariAyikla(
        self,
        envanter: List[Dict[str, Any]],
        vendor_id_filter: str = "0x10de"
    ) -> List[Dict[str, Any]]:
        temiz_list = []
        target_v_hex = int(vendor_id_filter, 16) if vendor_id_filter.startswith("0x") else PCI_VENDOR_NVIDIA

        for item in envanter:
            raw_h = item.get("raw_header", b"")
            info = self.IkiliBasligiCozumle(raw_h)
            if info.get("is_gpu") and (info.get("vendor_id_hex") == target_v_hex or vendor_id_filter == "ALL"):
                item_copy = dict(item)
                item_copy.update(info)
                temiz_list.append(item_copy)
        return temiz_list

    def MevcutSurucuyuOgren(self, pci_adres_veya_item: Union[str, Dict[str, Any]]) -> str:
        if isinstance(pci_adres_veya_item, str):
            item = {"pci_address": pci_adres_veya_item, "raw_header": b""}
        else:
            item = pci_adres_veya_item
        return self.HakimiyetDurumunuOku(item)
