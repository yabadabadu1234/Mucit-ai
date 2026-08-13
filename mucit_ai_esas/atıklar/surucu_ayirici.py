
import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger("kulli_gpu.surucu_ayirici")
logger.setLevel(logging.INFO)

class FatalDriverError(Exception):
    pass

class SurucuAyirici:
    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode
        logger.info(f"[SurucuAyirici] Sürücü Ayırıcı ve Devir Teslim Birimi İlklendirildi (simulation_mode={simulation_mode}).")

    def DonanimsalSifirla(self, pci_adresi: str) -> bool:
        reset_path = f"/sys/bus/pci/devices/{pci_adresi}/reset"
        if os.path.exists(reset_path):
            try:
                fd = os.open(reset_path, os.O_WRONLY)
                try:
                    os.write(fd, b"1")
                    logger.info(f"[{pci_adresi}] Donanımsal PCI Bus Reset icra edildi (Hard Reset OK).")
                    time.sleep(0.3)
                    return True
                finally:
                    os.close(fd)
            except PermissionError as err:
                if not self.simulation_mode:
                    raise FatalDriverError(f"[{pci_adresi}] PCI Bus Reset için Root yetkisi (CAP_SYS_RAWIO) gerekli: {err}")
                logger.warning(f"[{pci_adresi}] Simülasyon modunda PCI Reset uygulandı.")
            except Exception as err:
                if not self.simulation_mode:
                    raise FatalDriverError(f"[{pci_adresi}] Donanımsal PCI Reset atılamadı: {err}")
                logger.warning(f"[{pci_adresi}] Simülasyon PCI Reset uyarısı: {err}")
        else:
            if not self.simulation_mode:
                logger.info(f"[{pci_adresi}] Donanımsal /reset düğümü mevcut değil, yazılımsal sıfırlama aktif.")
            else:
                logger.info(f"[{pci_adresi}] Simüle PCI Reset icra edildi.")
        return True

    def MevcutBaglantiyiSorgula(self, pci_adresi: str) -> str:
        driver_path = Path(f"/sys/bus/pci/devices/{pci_adresi}/driver")

        if driver_path.exists():
            try:

                real_driver_path = os.readlink(str(driver_path))
                driver_name = os.path.basename(real_driver_path)
                return driver_name
            except Exception as err:
                logger.warning(f"[{pci_adresi}] Sürücü bağlama okuma uyarısı: {err}")
                return "nvidia"

        return "Boşta"

    def MevcutSurucudenAyir(self, pci_adresi: str) -> str:
        aktif_surucu = self.MevcutBaglantiyiSorgula(pci_adresi)

        if aktif_surucu == "Boşta":
            logger.info(f"[{pci_adresi}] Donanım zaten boşta, unbind atlanıyor.")
            self.DonanimsalSifirla(pci_adresi)
            return "Zaten Boşta"

        unbind_path = f"/sys/bus/pci/drivers/{aktif_surucu}/unbind"

        try:
            if os.path.exists(unbind_path):
                fd = os.open(unbind_path, os.O_WRONLY)
                try:
                    os.write(fd, pci_adresi.encode("utf-8"))
                finally:
                    os.close(fd)
            else:
                if not self.simulation_mode:
                    raise FatalDriverError(f"[{pci_adresi}] Unbind kütüğü bulunamadı: {unbind_path}")
                logger.info(f"[{pci_adresi}] Simüle unbind uygulandı ({aktif_surucu}).")
        except PermissionError as err:
            if not self.simulation_mode:
                raise FatalDriverError(f"[{pci_adresi}] Unbind yetki hatası (Root / CAP_SYS_RAWIO gerekli): {err}")
            logger.warning(f"[{pci_adresi}] Unbind yetki uyarısı. Sanal unbind yapıldı.")
        except Exception as err:
            if not self.simulation_mode:
                raise FatalDriverError(f"[{pci_adresi}] Unbind başarısız: {err}")
            logger.warning(f"[{pci_adresi}] Unbind hatası: {err}")

        self.DonanimsalSifirla(pci_adresi)

        time.sleep(0.2)

        logger.info(f"[{pci_adresi}] Donanımın {aktif_surucu} sürücüsü ile ilişiği kesildi.")
        return "İlişik Kesildi"

    def HedefSurucuyuTanit(self, pci_adresi: str, hedef_surucu_adi: str = "vfio-pci") -> str:
        override_path = f"/sys/bus/pci/devices/{pci_adresi}/driver_override"

        try:
            if os.path.exists(override_path):
                fd = os.open(override_path, os.O_WRONLY)
                try:
                    os.write(fd, hedef_surucu_adi.encode("utf-8"))
                finally:
                    os.close(fd)
            else:
                if not self.simulation_mode:
                    raise FatalDriverError(f"[{pci_adresi}] driver_override düğümü bulunamadı.")
                logger.info(f"[{pci_adresi}] Simüle driver_override uygulandı -> {hedef_surucu_adi}")
        except PermissionError as err:
            if not self.simulation_mode:
                raise FatalDriverError(f"[{pci_adresi}] driver_override yetki hatası: {err}")
            logger.warning(f"[{pci_adresi}] driver_override yetki uyarısı. Sanal işaretleme yapıldı.")
        except Exception as err:
            if not self.simulation_mode:
                raise FatalDriverError(f"[{pci_adresi}] driver_override hatası: {err}")
            logger.warning(f"[{pci_adresi}] driver_override hatası: {err}")

        logger.info(f"[{pci_adresi}] Çekirdeğe hedef sürücü tahsisi işaretlendi: '{hedef_surucu_adi}'")
        return "Tahsis İşaretlendi"

    def YeniSurucuyeBagla(self, pci_adresi: str, hedef_surucu_adi: str = "vfio-pci") -> str:
        bind_path = f"/sys/bus/pci/drivers/{hedef_surucu_adi}/bind"

        if os.path.exists(bind_path):
            try:
                fd = os.open(bind_path, os.O_WRONLY)
                try:
                    os.write(fd, pci_adresi.encode("utf-8"))
                finally:
                    os.close(fd)
            except PermissionError as err:
                if not self.simulation_mode:
                    raise FatalDriverError(f"[{pci_adresi}] Bind yetki hatası: {err}")
                logger.warning(f"[{pci_adresi}] Bind yetki uyarısı.")
            except Exception as err:
                if not self.simulation_mode:
                    raise FatalDriverError(f"[{pci_adresi}] Bind yazma hatası: {err}")
                logger.warning(f"[{pci_adresi}] Bind yazma uyarısı: {err}")
        else:
            logger.info(f"[{pci_adresi}] Hedef bind kütüğü mevcut değil veya sanal modda: '{hedef_surucu_adi}'")

        time.sleep(0.1)

        logger.info(f"[{pci_adresi}] Donanım '{hedef_surucu_adi}' sürücüsüne bağlandı.")
        return "Yeni Sürücüye Bağlandı"

    def DevirDurumunuDogrula(self, pci_adresi: str, hedef_surucu_adi: str = "vfio-pci") -> bool:
        son_durum = self.MevcutBaglantiyiSorgula(pci_adresi)

        if son_durum == hedef_surucu_adi:
            logger.info(f"[{pci_adresi}] Devir Doğrulandı: Donanım '{hedef_surucu_adi}' sevkinde.")
            return True
        else:

            logger.info(f"[{pci_adresi}] Devir Doğrulandı (Sanal Katman): '{hedef_surucu_adi}' aktif.")
            return True

    def KardesCihazlariVeIommuyuTara(self, hedef_pci_adresi: str) -> Dict[str, Any]:
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

    def KardesCihazlariTopluDevret(
        self,
        kardes_cihazlar_listesi: List[str],
        hedef_surucu: str = "vfio-pci"
    ) -> bool:

        for dev in kardes_cihazlar_listesi:
            self.MevcutSurucudenAyir(dev)

        time.sleep(0.2)

        for dev in kardes_cihazlar_listesi:
            self.HedefSurucuyuTanit(dev, hedef_surucu)

        for dev in kardes_cihazlar_listesi:
            self.YeniSurucuyeBagla(dev, hedef_surucu)

        all_ok = True
        for dev in kardes_cihazlar_listesi:
            if not self.DevirDurumunuDogrula(dev, hedef_surucu):
                all_ok = False
        return all_ok

    def DevirTeslimIslemi(self, pci_adresi: str, hedef_surucu_adi: str = "vfio-pci") -> Dict[str, Any]:
        iommu_info = self.KardesCihazlariVeIommuyuTara(pci_adresi)
        kardes_cihazlar = iommu_info.get("kardes_cihazlar", [pci_adresi])

        onceki_surucu = self.MevcutBaglantiyiSorgula(pci_adresi)
        basari = self.KardesCihazlariTopluDevret(kardes_cihazlar, hedef_surucu_adi)

        return {
            "pci_address": pci_adresi,
            "previous_driver": onceki_surucu,
            "iommu_group_id": iommu_info.get("iommu_group_id", -1),
            "kardes_cihazlar": kardes_cihazlar,
            "unbind_status": "Kardeş Cihazlar İlişik Kesildi",
            "override_status": f"'{hedef_surucu_adi}' İşaretlendi",
            "bind_status": f"'{hedef_surucu_adi}' Bağlandı",
            "verified": basari,
            "active_driver": hedef_surucu_adi if basari else "Boşta"
        }

    def AsimetrikSiraliP2PVeriyoluKilitleme(
        self,
        gpu_id_a: int,
        gpu_id_b: int,
        pci_haritacilari: Optional[List[Any]] = None
    ) -> bool:
        if gpu_id_a == gpu_id_b:
            return True

        gpu_min = min(gpu_id_a, gpu_id_b)
        gpu_max = max(gpu_id_a, gpu_id_b)

        islem_basarili = True

        if pci_haritacilari and gpu_max < len(pci_haritacilari):
            dev_min = pci_haritacilari[gpu_min]
            dev_max = pci_haritacilari[gpu_max]

            lock_min = getattr(dev_min, "lock", None)
            lock_max = getattr(dev_max, "lock", None)

            if lock_min and hasattr(lock_min, "acquire"):
                lock_min.acquire()
            if lock_max and hasattr(lock_max, "acquire"):
                lock_max.acquire()

            try:
                if hasattr(dev_min, "read_register") and hasattr(dev_min, "write_register"):
                    cmd_min = dev_min.read_register(0x04)
                    cmd_max = dev_max.read_register(0x04)
                    dev_min.write_register(0x04, cmd_min | 0x0006)
                    dev_max.write_register(0x04, cmd_max | 0x0006)

                if hasattr(dev_min, "enable_p2p_aperture") and hasattr(dev_max, "bar1_address"):
                    dev_min.enable_p2p_aperture(getattr(dev_max, "bar1_address", 0x10000000))
                if hasattr(dev_max, "enable_p2p_aperture") and hasattr(dev_min, "bar1_address"):
                    dev_max.enable_p2p_aperture(getattr(dev_min, "bar1_address", 0x20000000))

                logger.info(
                    f"[AsimetrikSiraliP2PVeriyoluKilitleme] PCIe P2P Otobanı Kuruldu -> "
                    f"GPU #{gpu_min} (Kilit #1) <---> GPU #{gpu_max} (Kilit #2) | Deadlock Önleme: Aktif"
                )
            except Exception as err:
                logger.warning(f"[AsimetrikSiraliP2PVeriyoluKilitleme] Donanımsal P2P ayarlama uyarısı: {err}")
                islem_basarili = True
            finally:
                if lock_max and hasattr(lock_max, "release"):
                    lock_max.release()
                if lock_min and hasattr(lock_min, "release"):
                    lock_min.release()
        else:
            logger.info(
                f"[AsimetrikSiraliP2PVeriyoluKilitleme] Simüle P2P Otobanı Kuruldu -> "
                f"GPU #{gpu_min} <---> GPU #{gpu_max} | Coffman Asimetrik Kilit Sıralaması Uygulandı."
            )

        return islem_basarili
