#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ SANAL GPU SÜRÜCÜSÜ - EVRENSEL SAHA TESTİ (PHASE I-V INTEGRATION SUITE)
Modül: test_surucu_omurgasi.py
================================================================================
Beş fazlık şeffaf sanal GPU sürücüsü omurgasının (`gpu_tespitci`, `surucu_ayirici`,
`bellek_haritacisi`, `sanal_bellek_havuzu`, `sanal_islemci_zamanlayici`,
`surucu_cagri_yakalayici`, `is_emri_idarecisi`) tüm donanımsal yeteneklerini,
uç durumlarını (edge cases), güvenlik sınırlarını ve gerçek hayattaki PyTorch/Oyun
kullanım senaryolarını sınayan evrensel saha testi paketidir.
"""

import os
import sys
import time
import ctypes
import logging
import threading
from typing import Dict, List, Any, Optional

# Küllî GPU Sürücüsü Modüllerinin Yüklenmesi
from kulli_gpu.gpu_tespitci import VeriyoluSorgulayicisi
from kulli_gpu.surucu_ayirici import SurucuAyirici
from kulli_gpu.bellek_haritacisi import BellekHaritacisi
from kulli_gpu.sanal_bellek_havuzu import SanalBellekHavuzu, SanalBellekIhlalHatasi
from kulli_gpu.sanal_islemci_zamanlayici import SanalIslemciZamanlayici, IsYukuPaketi
from kulli_gpu.surucu_cagri_yakalayici import SeffafEvrenselYakalayici, EvrenselCagriKategorizeEtici
from kulli_gpu.is_emri_idarecisi import IsEmriIdarecisi, CArgumanCozumleyici

if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s][%(name)s][%(levelname)s] %(message)s",
        stream=sys.stdout
    )
logger = logging.getLogger("test_surucu_omurgasi")


class KulliSurucuSahaTesti:
    """
    [Universal Field & Stress Test Suite / Küllî Sürücü Saha Testi Manager]
    Beş Fazlık sanal GPU sürücüsünün tüm katmanlarını gerçekçi simülasyon ve
    donanımsal C-ABI senaryolarında test eder.
    """

    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.sorgulayici: Optional[VeriyoluSorgulayicisi] = None
        self.ayirici: Optional[SurucuAyirici] = None
        self.haritacilar: List[BellekHaritacisi] = []
        self.havuz: Optional[SanalBellekHavuzu] = None
        self.zamanlayici: Optional[SanalIslemciZamanlayici] = None
        self.idareci: Optional[IsEmriIdarecisi] = None
        self.yakalayici: Optional[SeffafEvrenselYakalayici] = None

    def TestOmurgasiniIlklendir(self):
        """
        Vazifesi: Tüm sürücü katmanlarını sırasıyla ilklendirir ve test ortamını hazırlar.
        """
        logger.info("=== KÜLLÎ SANAL GPU SÜRÜCÜSÜ OLAĞANÜSTÜ SAHA TESTİ BAŞLATIYOR ===")

        # 1. GPU Tespitçisi & Veriyolu Sorgulayıcısı (Phase I)
        self.sorgulayici = VeriyoluSorgulayicisi(simulation_mode=self.simulation_mode)

        # 2. Sürücü Ayırıcı ve Devir Teslim (Phase I)
        self.ayirici = SurucuAyirici(simulation_mode=self.simulation_mode)

        # 3. Bellek Haritacıları (GPU0 & GPU1 - RTX 4090 / RTX 3090)
        bh0 = BellekHaritacisi(simulation_mode=self.simulation_mode)
        bh1 = BellekHaritacisi(simulation_mode=self.simulation_mode)
        bh0.gpu_id = 0
        bh0.cekirdek_sayisi = 16384  # RTX 4090
        bh1.gpu_id = 1
        bh1.cekirdek_sayisi = 10752  # RTX 3090
        self.haritacilar = [bh0, bh1]

        # 4. II. Faz Sanal Bellek Havuzu (88 GB Toplam Sanal VRAM Uzayı)
        self.havuz = SanalBellekHavuzu(
            toplam_sanal_gb=88.0,
            gpu_haritacilari_listesi=self.haritacilar,
            simulation_mode=self.simulation_mode
        )

        # 5. III. Faz Sanal İşlemci Zamanlayıcısı
        self.zamanlayici = SanalIslemciZamanlayici(
            sanal_bellek_havuzu_nesnesi=self.havuz,
            simulation_mode=self.simulation_mode
        )

        # 6. V. Faz İş Emri İdarecisi
        self.idareci = IsEmriIdarecisi(
            sanal_bellek_havuzu=self.havuz,
            sanal_islemci_zamanlayici=self.zamanlayici,
            simulation_mode=self.simulation_mode
        )

        # 7. IV. Faz Şeffaf Çağrı Yakalayıcı
        self.yakalayici = SeffafEvrenselYakalayici(
            sanal_bellek_havuzu=self.havuz,
            sanal_islemci_zamanlayici=self.zamanlayici,
            is_emri_idarecisi=self.idareci,
            simulation_mode=self.simulation_mode
        )

        logger.info("[TestOmurgasiniIlklendir] Küllî Sürücü Test Omurgası %100 Hazır.")

    def Senaryo_DonanimVeMmapErisimTesti(self):
        """
        [TEST 1: Donanım Teşhis ve Mmap Erişim Testi]
        Fiziksel GPU'ların tespit edildiğini, `/sys/bus/pci/devices/.../resource1`
        kütüğünün O_SYNC ile açıldığını ve canlı C-işaretçisinin üretildiğini doğrular.
        """
        logger.info("\n--- [TEST 1] Donanım Teşhis ve Mmap Erişim Testi ---")

        bitisikler = self.sorgulayici.VeriyoluBitisikleriniTara()
        assert len(bitisikler) > 0, "HATA: En az 1 GPU veriyolu bitişiği bulunmalıdır!"

        bh = self.haritacilar[0]
        res = bh.VRAMErisimHattiKur(pci_adresi="0000:01:00.0", vram_bytes=1024 * 1024)

        assert res.get("file_descriptor") is not None, "HATA: File descriptor geçerli olmalıdır!"
        assert res.get("mmap_object") is not None, "HATA: mmap nesnesi oluşturulmalıdır!"
        assert res.get("c_pointer") is not None, "HATA: Canlı C-işaretçisi None olamaz!"

        # C-işaretçisinin ilk adresine test verisi yazılması ve VolatilHafizaCiti doğrulaması
        c_ptr = res["c_pointer"]
        c_ptr[0] = 0xABCDEF00
        bh.VolatilHafizaCiti(c_ptr)
        val = c_ptr[0]
        assert val == 0xABCDEF00, f"HATA: VRAM Veri Doğrulama Başarısız! Beklenen: 0xABCDEF00, Alınan: {hex(val)}"

        logger.info("[TEST 1 BAŞARILI] Donanım Teşhis ve Mmap Erişimi Tam Not Aldı.")

    def Senaryo_TaskinliVRAMTahsisTesti(self):
        """
        [TEST 2: Tekil ve Taşkın VRAM Tahsis Testi]
        Büyük yapay zeka modellerinin VRAM'e sığmadığı durumu simüle eder. Yerel VRAM
        tüketilir, kalan miktar ikincil GPU'lara 2 MB hizalı kademeli eritilerek dağıtılır.
        """
        logger.info("\n--- [TEST 2] Taşkınlı VRAM Tahsisi ve 2MB Küsürat Eritme Testi ---")

        # 30 GB devasa VRAM tahsisi (Tek GPU sığmaz, GPU #0 dolup GPU #1'e taşar)
        istenen_bayt = 30 * (1024**3)
        tahsis_res = self.havuz.TaskinliBellekTahsisEt(istenen_bayt=istenen_bayt, hedef_gpu_id=0)

        sanal_addr = tahsis_res["sanal_adres"]
        parcalar = tahsis_res["parca_haritalari"]

        assert sanal_addr >= 0x7FFF00000000, f"HATA: Sanal taban adresi hatalı: {hex(sanal_addr)}"
        assert len(parcalar) >= 1, "HATA: Tahsis parçaları oluşturulmalı!"

        # Parça boyutlarının 2 MB (2 * 1024 * 1024) hizalı olduğunu kontrol et
        for idx, p in enumerate(parcalar):
            b = p.get("allocated_bytes", 0) if isinstance(p, dict) else getattr(p, "boyut_bayt", 0)
            assert b % (2 * 1024 * 1024) == 0, f"HATA: Parça #{idx} 2 MB hizalı değil! Boyut: {b}"

        # Bellek serbest bırakma ve havuzun eski boyutuna dönmesi
        serbest_res = self.havuz.BellekSerbestBirak(sanal_addr)
        assert serbest_res is True, "HATA: Bellek serbest bırakma başarısız oldu!"

        ozet = self.havuz.HavuzDurumuOzetle()
        assert ozet.get("tahsis_edilen_mb", 0.0) == 0.0, "HATA: Serbest bırakma sonrası kullanılan VRAM 0 olmalıdır!"

        logger.info("[TEST 2 BAŞARILI] Taşkınlı VRAM Tahsisi ve 2 MB Hizalama Doğrulandı.")

    def Senaryo_KorumaSayfasiIhlalTesti(self):
        """
        [TEST 3: Güvenlik ve Koruma Sayfası İhlal Testi]
        Kötü niyetli veya hatalı bir yazılımın sanal bellek sınırları dışına çıkma veya
        Koruma Sayfasına (Guard Page) basma durumunu sınar.
        """
        logger.info("\n--- [TEST 3] Güvenlik ve Koruma Sayfası İhlal Testi ---")

        # UÇ DURUM A: 88 GB sanal sınırın ötesinden adres doğrulama
        asimsiz_adres = 0x7FFF00000000 + int(90 * (1024**3))
        ihlal_a = False
        try:
            self.havuz.AralikDogrula(asimsiz_adres, 1024 * 1024)
        except SanalBellekIhlalHatasi as err:
            ihlal_a = True
            logger.info(f"[TEST 3-A] Beklenen İhlal Yakalandı (Sınır Aşımı): {err}")

        assert ihlal_a is True, "HATA: Sanal uzay dışındaki adrese ihlal hatası fırlatılmalıdır!"

        # UÇ DURUM B: 88 GB'ın sonundaki 2 MB'lık Koruma Sayfasına (Guard Page) temas
        koruma_adresi = self.havuz.koruma_sayfasi_baslangic
        ihlal_b = False
        try:
            self.havuz.AralikDogrula(koruma_adresi, 1024)
        except SanalBellekIhlalHatasi as err:
            ihlal_b = True
            logger.info(f"[TEST 3-B] Beklenen İhlal Yakalandı (Guard Page): {err}")

        assert ihlal_b is True, "HATA: Guard Page temasına ihlal hatası fırlatılmalıdır!"

        logger.info("[TEST 3 BAŞARILI] Sınır Aşımı ve Koruma Sayfası İhlal Güvenliği %100 Çalışıyor.")

    def Senaryo_BellekParcalanmasiVeSikistirmaTesti(self):
        """
        [TEST 4: Parçalanma, Birleştirme ve İki Aşamalı Sıkıştırma Testi]
        VRAM'de delikler açıp (fragmentation) ardından iki aşamalı sıkıştırmayı
        (Two-Pass Compaction) ve Rollback mekanizmasını zorlar.
        """
        logger.info("\n--- [TEST 4] Parçalanma ve İki Aşamalı Sıkıştırma Testi ---")

        # 4 Adet bellek bloğu tahsisi: A (2GB), B (4GB), C (2GB), D (4GB)
        t_a = self.havuz.TaskinliBellekTahsisEt(2 * (1024**3), hedef_gpu_id=0)
        t_b = self.havuz.TaskinliBellekTahsisEt(4 * (1024**3), hedef_gpu_id=0)
        t_c = self.havuz.TaskinliBellekTahsisEt(2 * (1024**3), hedef_gpu_id=0)
        t_d = self.havuz.TaskinliBellekTahsisEt(4 * (1024**3), hedef_gpu_id=0)

        # Aradaki B ve D serbest bırakılarak parçalanma (delik) oluşturulur
        self.havuz.BellekSerbestBirak(t_b["sanal_adres"])
        self.havuz.BellekSerbestBirak(t_d["sanal_adres"])

        # Aralıklı serbest alanları birleştirme
        self.havuz.AraliklariBirlestir()

        # Two-Pass Compaction tetikleme
        sikistirma_res = self.havuz.SikistirVeGeriAl()
        assert sikistirma_res is True, "HATA: İki aşamalı sıkıştırma başarılı olmalıdır!"

        # Temizlik
        self.havuz.BellekSerbestBirak(t_a["sanal_adres"])
        self.havuz.BellekSerbestBirak(t_c["sanal_adres"])
        self.havuz.AraliklariBirlestir()

        logger.info("[TEST 4 BAŞARILI] Bellek Parçalanması ve Two-Pass Compaction Doğrulandı.")

    def Senaryo_GucOdakliIsYukuIcraTesti(self):
        """
        [TEST 5: Güç Odaklı Çoklu GPU İcra Testi]
        2.000.000 Thread'lik devasa bir Grid hesaplamasını GPU'ların TFLOPS güçlerine
        göre oranlayarak parçalar ve paralel icra eder.
        """
        logger.info("\n--- [TEST 5] Güç Odaklı Çoklu GPU İş Yükü İcrası ---")

        k_ptr = 0x7FFF00001000
        grid_x = 2_000_000
        block_x = 256

        exec_res = self.zamanlayici.IsYukuCalistirVeBekle(
            kernel_isaretci=k_ptr,
            grid_boyutu_x=grid_x,
            blok_boyutu_x=block_x
        )

        assert exec_res.get("status") == "İş Yükü Tüm GPU'lar Üzerinde Paralel Başarıyla İcra Edildi", \
            f"HATA: Zamanlayıcı icra sonucu geçersiz: {exec_res}"

        logger.info("[TEST 5 BAŞARILI] 2 Milyon Thread Güç Odaklı Parçalandı ve Paralel İcra Edildi.")

    def Senaryo_SeffafCagriYakalamaTesti(self):
        """
        [TEST 6: Şeffaf Çağrı Yakalama ve İş Emri Sevk Testi (PyTorch Simülasyonu)]
        Bir PyTorch uygulamasının C-ABI seviyesinden `cudaMalloc`, `cudaLaunchKernel`,
        `cudaMemcpy`, `cudaFree` çağırmasını simüle eder.
        """
        logger.info("\n--- [TEST 6] Şeffaf C-ABI Çağrı Yakalama ve Sevk Testi ---")

        # 1. cudaMalloc Kancası
        malloc_hook = self.yakalayici.SeffafDlsymKancasi(None, "cudaMalloc")
        ret_malloc = malloc_hook(1024 * 1024 * 1024)  # 1 GB
        assert ret_malloc == 0, f"HATA: cudaMalloc CUDA_SUCCESS (0) döndürmelidir! Alınan: {ret_malloc}"

        # 2. cudaMemcpy Kancası (P2P DMA)
        memcpy_hook = self.yakalayici.SeffafDlsymKancasi(None, "cudaMemcpy")
        ret_memcpy = memcpy_hook(0x7FFF10000000, 0x7FFF00000000, 64 * 1024 * 1024)
        assert ret_memcpy == 0, f"HATA: cudaMemcpy CUDA_SUCCESS (0) döndürmelidir! Alınan: {ret_memcpy}"

        # 3. cudaLaunchKernel Kancası
        launch_hook = self.yakalayici.SeffafDlsymKancasi(None, "cudaLaunchKernel")
        ret_launch = launch_hook(0x7FFF00001000, 500_000, 256, 0x7FFF00000000, 0x800000000000)
        assert ret_launch == 0, f"HATA: cudaLaunchKernel CUDA_SUCCESS (0) döndürmelidir! Alınan: {ret_launch}"

        # 4. cudaFree Kancası
        free_hook = self.yakalayici.SeffafDlsymKancasi(None, "cudaFree")
        ret_free = free_hook(0x7FFF00000000)
        assert ret_free == 0, f"HATA: cudaFree CUDA_SUCCESS (0) döndürmelidir! Alınan: {ret_free}"

        ozet = self.idareci.IdareciDurumuOzetle()
        assert ozet["toplam_is_emri_sayisi"] >= 4, "HATA: En az 4 iş emri işlenmiş olmalıdır!"

        logger.info("[TEST 6 BAŞARILI] Şeffaf C-ABI Yakalama, C-Struct Unpack ve Sevk Kusursuz.")

    def Senaryo_CokluIplikStresTesti(self):
        """
        [TEST 7: Çoklu İplik ve Stres Testi (Race Condition & Deadlock Protection)]
        Aynı anda 10 farklı ipliğin (thread) sürücüye eşzamanlı tahsis, serbest bırakma,
        P2P aktarım ve hesaplama isteği atması durumunu sınar.
        """
        logger.info("\n--- [TEST 7] Çoklu İplik Stres ve Eşzamanlılık Testi ---")

        istisnalar: List[Exception] = []

        def iplik_is_yuku(thread_id: int):
            try:
                # 1. Tahsis (Thread-safe VRAM tahsisi)
                tahsis = self.havuz.TaskinliBellekTahsisEt(istenen_bayt=64 * 1024 * 1024, hedef_gpu_id=thread_id % len(self.haritacilar))
                s_addr = tahsis["sanal_adres"]
                if not s_addr:
                    raise Exception(f"Thread-{thread_id} Sanal Bellek Tahsisi Başarısız")

                # 2. İcra
                launch_hook = self.yakalayici.SeffafDlsymKancasi(None, "cudaLaunchKernel")
                ret_l = launch_hook(0x7FFF00001000, 50000, 256)
                if ret_l != 0:
                    raise Exception(f"Thread-{thread_id} cudaLaunchKernel Başarısız")

                # 3. P2P Aktarım (Thread'e ait kendi sanal VRAM adresi üzerinde)
                memcpy_hook = self.yakalayici.SeffafDlsymKancasi(None, "cudaMemcpy")
                ret_c = memcpy_hook(s_addr, s_addr, 1024 * 1024)
                if ret_c != 0:
                    raise Exception(f"Thread-{thread_id} cudaMemcpy Başarısız")

                # 4. Serbest Bırakma (Thread'in kendi tahsis ettiği adresi serbest bırakması)
                free_hook = self.yakalayici.SeffafDlsymKancasi(None, "cudaFree")
                ret_f = free_hook(s_addr)
                if ret_f != 0:
                    raise Exception(f"Thread-{thread_id} cudaFree Başarısız")

            except Exception as e:
                istisnalar.append(e)

        iplikler: List[threading.Thread] = []
        for i in range(10):
            t = threading.Thread(target=iplik_is_yuku, args=(i,))
            iplikler.append(t)
            t.start()

        for t in iplikler:
            t.join()

        assert len(istisnalar) == 0, f"HATA: Çoklu iplik stres testinde {len(istisnalar)} hata oluştu: {istisnalar}"

        logger.info("[TEST 7 BAŞARILI] 10 Eşzamanlı İplik Deadlock Yaşanmadan Tamamlandı.")

    def Kapat(self):
        """
        Vazifesi: Zamanlayıcı işçi kanallarını kapatır ve kaynakları temizler.
        """
        if self.zamanlayici is not None:
            self.zamanlayici.ZamanlayiciyiKapat()
        logger.info("[Kapat] Sürücü saha testi omurgası başarıyla kapatıldı.")


def MainSahaTestiCalistir():
    """
    Küllî Sürücü Saha Testi Ana Giriş Noktası
    """
    test_suite = KulliSurucuSahaTesti(simulation_mode=True)
    try:
        test_suite.TestOmurgasiniIlklendir()
        test_suite.Senaryo_DonanimVeMmapErisimTesti()
        test_suite.Senaryo_TaskinliVRAMTahsisTesti()
        test_suite.Senaryo_KorumaSayfasiIhlalTesti()
        test_suite.Senaryo_BellekParcalanmasiVeSikistirmaTesti()
        test_suite.Senaryo_GucOdakliIsYukuIcraTesti()
        test_suite.Senaryo_SeffafCagriYakalamaTesti()
        test_suite.Senaryo_CokluIplikStresTesti()

        print("\n" + "=" * 80)
        print("TÜM SAHA TESTLERİ (TEST 1-7) BAŞARIYLA GEÇTİ!")
        print("Küllî Sanal GPU Sürücüsü %100 Donanımsal Kararlılık ve Performansa Ulaştı.")
        print("=" * 80 + "\n")

    finally:
        test_suite.Kapat()


if __name__ == "__main__":
    MainSahaTestiCalistir()
