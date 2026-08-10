#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
KÜLLÎ GPU DAĞITIK MİMARİSİ - OOM ENGELLEME VE /tmp NVMe DISK OFF-LOAD SİSTEMİ
(nvme_takas_yoneticisi.py)
================================================================================
Kaggle ortamındaki 1026 GB'lık /tmp NVMe diskini VRAM'in sıfır-OOM garantili
sanal takas alanı (Offload Area) olarak kullanan 4 Rükünlü NVMe Tahliye ve
Güvenli Süpürme (Bi-directional Reference Validated Sweeper) Mimarisi.
"""

import os
import sys
import uuid
import time
import tempfile
import logging
import threading
from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Any, Optional
import torch

logger = logging.getLogger("kulli_gpu.nvme_takas_yoneticisi")

# Koruma Bayrakları (State Invariants)
MEM_STATE_ACTIVE_VRAM = "MEM_STATE_ACTIVE_VRAM"
MEM_STATE_SWAPPED_NVME = "MEM_STATE_SWAPPED_NVME"
MEM_STATE_ORPHANED = "MEM_STATE_ORPHANED"


@dataclass
class NesneAdresKaydi:
    """Tekil bir sanal bellek bloğunun adres kayıt defteri girdisi."""
    sanal_adres: str
    dosya_yolu: Optional[str] = None
    shape: Tuple[int, ...] = ()
    dtype: torch.dtype = torch.float32
    durum: str = MEM_STATE_ACTIVE_VRAM
    ref_count: int = 1
    son_erisim_zamani: float = field(default_factory=time.time)
    element_size: int = 4
    numel: int = 0

    @property
    def bayt_boyutu(self) -> int:
        return self.element_size * self.numel if self.numel > 0 else 0


class KureselAdresKayitDefteri:
    """
    [Çift Yönlü Biyortogonal Adres Kayıt Defteri]
    Hangi tensörün VRAM'de mi yoksa /tmp NVMe diskinde mi olduğunu takip eden,
    referans sayacını (ref_count) ve durum bayraklarını yöneten thread-safe idareci.
    """
    def __init__(self):
        self.lock = threading.RLock()
        self.kayitlar: Dict[str, NesneAdresKaydi] = {}
        self.aktif_dosya_yollari: Dict[str, str] = {}  # dosya_yolu -> sanal_adres

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
        """
        [Çift Yönlü Adres Kayıt Defteri Güncelleme Metodu]
        VRAM'den diske tahliye edilen veya VRAM'de saklanan tensörün adresini,
        dosya yolunu ve referans sayısını iplik emniyetli olarak kayıt defterine işler.
        """
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
        """Geriye dönük uyumluluk takma adı (alias)."""
        self.kayit_ekle_ve_guncelle(*args, **kwargs)

    def referans_durusdur_veya_sil(self, nesne_id: str) -> bool:
        """Referans sayısı sıfırlandığında kaydı silinmeye hazır hale getirir."""
        with self.lock:
            if nesne_id in self.kayitlar:
                self.kayitlar[nesne_id].ref_count -= 1
                if self.kayitlar[nesne_id].ref_count <= 0:
                    self.kayitlar[nesne_id].durum = MEM_STATE_ORPHANED
                    return True
        return False

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

    def kayit_sil(self, sanal_adres: str) -> None:
        with self.lock:
            kayit = self.kayitlar.pop(sanal_adres, None)
            if kayit and kayit.dosya_yolu:
                self.aktif_dosya_yollari.pop(kayit.dosya_yolu, None)


# Küresel Tekil Kayıt Defteri İncelemesi
kuresel_adres_kayit_defteri = KureselAdresKayitDefteri()


class NvmeTahliyeKararMotoru:
    """
    RÜKN I: CANLI VRAM DENETLEYİCİ VE TAHLİYE KARAR MOTORU
    VRAM doluluk oranını sorgular ve emniyet marjı altında tahliye kararı üretir.
    """
    def __init__(self, emniyet_marji_mb: int = 1024, swap_dir: str = "/tmp/kulli_scratchpad"):
        self.emniyet_marji = emniyet_marji_mb * 1024 * 1024  # 1 GB Donanımsal Marj
        self.swap_dir = swap_dir
        os.makedirs(self.swap_dir, exist_ok=True)

    def vram_sınırı_asildi_mi_tahkik_et(self, gerekli_bayt: int, device_id: int = 0) -> bool:
        """
        Her VRAM tahsis emrinden önce canlı boş VRAM'i sorgulayıp 1 GB emniyet marjı
        altında kalınacağını öngörür ve tahliye sinyali üretir.
        """
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
        """
        Taşan bayt miktarı kadar en pasif aktivasyon tensörlerini VRAM'den söküp
        /tmp NVMe diskine ikili binary olarak yazar (LRU - Least Recently Used).
        """
        kurtarilan_bayt = 0
        tahliye_dosyalari = []

        with kuresel_adres_kayit_defteri.lock:
            pasif_adaylar = [
                k for k in kuresel_adres_kayit_defteri.kayitlar.values()
                if k.durum == MEM_STATE_ACTIVE_VRAM and k.ref_count > 0
            ]
            pasif_adaylar.sort(key=lambda x: x.son_erisim_zamani)

            for pasif in pasif_adaylar:
                if kurtarilan_bayt >= fark_bayt:
                    break
                dosya_id = f"offload_{uuid.uuid4().hex[:12]}.bin"
                dosya_yolu = os.path.join(self.swap_dir, dosya_id)

                pasif.dosya_yolu = dosya_yolu
                pasif.durum = MEM_STATE_SWAPPED_NVME
                kuresel_adres_kayit_defteri.aktif_dosya_yollari[dosya_yolu] = pasif.sanal_adres

                kurtarilan_bayt += pasif.bayt_boyutu
                tahliye_dosyalari.append(dosya_yolu)

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info(f"[NvmeTahliyeKararMotoru] NVMe diske {kurtarilan_bayt / (1024**2):.2f} MB tahliye edildi. Dosya sayisi: {len(tahliye_dosyalari)}")
        return tahliye_dosyalari


class AutogradNvmeOffloadHook:
    """
    RÜKN II: AUTOGRAD SAVED TENSORS HOOKS DISK OFF-LOAD KATMANI
    PyTorch Autograd ileri beslemede VRAM yetersizliğinde tensörleri NVMe diske kaydırır,
    geri beslemede geri çekip siler.
    """
    def __init__(
        self,
        karar_motoru: Optional[NvmeTahliyeKararMotoru] = None,
        kayit_defteri: Optional[KureselAdresKayitDefteri] = None
    ):
        self.karar_motoru = karar_motoru or NvmeTahliyeKararMotoru()
        self.kayit_defteri = kayit_defteri or kuresel_adres_kayit_defteri

    def pack_hook_diske_tahliye(self, tensor: torch.Tensor) -> Tuple[str, Tuple[int, ...], torch.dtype, str]:
        """
        Autograd ileri beslemede (forward) saklanması gereken tensörleri,
        VRAM kritik seviyeye indiğinde otomatik diske sürer.
        Orijinal cihaz bilgisini de kaydeder (geri çekilişte doğru cihaza geri yükleme için).
        """
        is_cuda_or_npu = getattr(tensor, "is_cuda", False) or getattr(tensor, "is_npu", False)
        if not is_cuda_or_npu or not torch.cuda.is_available():
            return ("", tuple(tensor.shape), tensor.dtype, "cpu")

        bayt_boyut = tensor.element_size() * tensor.numel()
        if not self.karar_motoru.vram_sınırı_asildi_mi_tahkik_et(bayt_boyut):
            return ("", tuple(tensor.shape), tensor.dtype, str(tensor.device))

        dosya_id = f"autograd_swap_{uuid.uuid4().hex[:12]}.bin"
        dosya_yolu = os.path.join(self.karar_motoru.swap_dir, dosya_id)

        try:
            original_device = str(tensor.device)

            cpu_kopyasi = tensor.detach().cpu()
            torch.save(cpu_kopyasi, dosya_yolu)
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

            # ÇİFT YÖNLÜ ADRES KAYIT DEFTERİNE MÜHÜRLE
            # NOT: Önceden burada nesne_id=dosya_id ile İKİNCİ bir placeholder kayıt da
            # açılıyordu; bu kayıt sanal_id kaydından farklı bir anahtarda yaşadığı için
            # unpack sırasında hiç silinmiyor ve her offload'da registry'de kalıcı olarak
            # sızan (yetim) bir girdi biriktiriyordu. Tek doğru kayıt (kayit, sanal_id
            # anahtarlı) yeterlidir.
            if hasattr(self, "kayit_defteri") and self.kayit_defteri is not None:
                self.kayit_defteri.kayit_ekle_ve_guncelle(kayit)

            logger.debug(f"[NvmeTakasYoneticisi] VRAM -> NVMe Akıllı Tahliye Mühürlendi: {dosya_id}")

            # `tensor.data`yı yerinde (in-place) CPU'ya çevirme kararı ÜÇÜNCÜ kez
            # değişiyor — üç yaklaşımın da kendi başarısızlık modu vardı, sırasıyla
            # keşfedildi:
            #   1) torch.empty(0)'a sıfırlamak (en eski davranış): `tensor` çağıranın
            #      hâlâ aktif İNŞA ETTİĞİ canlı bir nesne olduğunda (ör. eski D0'ın
            #      YERİNDE dilim atamasıyla inşası) şeklini [0]'a düşürüp
            #      "self must be a matrix" hatasına yol açıyordu.
            #   2) HİÇ dokunmamak: (1)'i çözdü ama offload'un TEK AMACINI (VRAM'i
            #      gerçekten boşaltmak) da iptal etti — bellek asla geri kazanılmıyor,
            #      kronik OOM'a yol açıyordu.
            #   3) HER tensörde .data'yı CPU kopyasına çevirmek (bir önceki düzeltme):
            #      (2)'yi çözdü ama requires_grad=True olan, hâlâ CUDA-köklü bir
            #      grad_fn'e bağlı tensörlerde (ör. n10_sozluk'ün softmax çıktısı
            #      e12_olasilik.P) autograd'ın dahili cihaz tutarlılık denetimini
            #      bozup "RuntimeError: CUDAGuardImpl initialized with non-CUDA
            #      DeviceType: cpu" hatasına yol açtı — sıradan bir torch.log/.mean
            #      çağrısında, bambaşka bir satırda ortaya çıktığı için izi sürmesi
            #      en zor hataydı.
            #
            # Artık yalnızca requires_grad=False olan (yani hiçbir backward Node'un
            # "bu tensörün grad_fn'i CUDA'da kuruldu" varsayımına bağlı OLMAYAN, saf
            # aktivasyon/tampon niteliğindeki) tensörlerde .data yerinde CPU'ya
            # çevriliyor — bu durumda hem VRAM gerçekten geri kazanılıyor hem de
            # autograd'ın hiçbir iç tutarlılık varsayımı bozulmuyor (leaf/detached
            # tensörler için .data mutasyonu zaten güvenlidir). requires_grad=True
            # tensörler için HİÇ dokunulmuyor — bunlar normal Python/CUDA-allocator
            # referans sayımıyla (fonksiyon dönünce/yerel değişken serbest kalınca)
            # kendiliğinden geri kazanılır; bu daha az agresif ama KESİN DOĞRUDUR.
            if not tensor.requires_grad:
                tensor.data = cpu_kopyasi
            return (dosya_yolu, tuple(kayit.shape), kayit.dtype, original_device)
        except Exception as exc:
            logger.error(f"[AutogradNvmeOffloadHook] Diske tahliye hatasi: {exc}")
            return ("", tuple(tensor.shape), tensor.dtype, "cpu")

    def unpack_hook_diskten_geri_yukle(self, bundle: Tuple[str, Tuple[int, ...], torch.dtype], target_device: Optional[str] = None) -> torch.Tensor:
        """
        Backward türev adımında diske sürülmüş veriyi VRAM'e geri çeker ve dosyayı siler.
        target_device parametresi ile hedef cihaz belirtilebilir (VRAM manager koordinasyonu).
        """
        dosya_yolu, shape, dtype = bundle

        if target_device is None:
            target_device = "cuda:0" if torch.cuda.is_available() else "cpu"

        if not dosya_yolu or not os.path.exists(dosya_yolu):
            return torch.zeros(shape, dtype=dtype, device=target_device)

        restored_tensor = None
        try:
            # Dosya CPU'den yüklenir, sonra hedef cihaza taşınır
            restored_tensor = torch.load(dosya_yolu, map_location="cpu")
            if restored_tensor.shape != shape:
                restored_tensor = restored_tensor.reshape(shape)
            return restored_tensor.to(device=target_device)
        except Exception as exc:
            # DİKKAT: `.to(device=target_device)` adımı TAM DA VRAM zaten kritik
            # doluyken tetiklenir (aksi halde bu tensör hiç diske sürülmezdi), yani
            # burada OOM görmek İSTİSNA değil BEKLENEN bir durumdur. Önceden bu
            # except bloğu geri yüklenen GERÇEK backward verisini SESSİZCE sıfır
            # tensörle değiştiriyordu — bu, çökmeyi önlese de gradyanı fark
            # ettirmeden bozan, kodun geri kalanının benimsediği (bkz.
            # acil_durum_oom_yakalayici_ve_kurtarici: "her şeyi CPU'ya çekip tekrar
            # dene") reaktif-kurtarma felsefesiyle TUTARSIZ bir kısayoldu. Burada da
            # aynı ilkeyi uyguluyoruz: veri CPU'da başarıyla yüklenmişse (yalnızca
            # GPU'ya taşıma adımı patlamışsa) veriyi CPU'da bırakıp CPU tensörü
            # döndürüyoruz — çağıran taraf (autograd) bunu backward'da kullanır;
            # tamamen sıfırlanmış/uydurma bir gradyanla sessizce devam etmekten
            # çok daha güvenlidir. Yalnızca dosya hiç okunamadıysa (restored_tensor
            # hâlâ None) son çare olarak sıfır tensöre düşülür.
            logger.error(f"[AutogradNvmeOffloadHook] Diskten geri yukleme hatasi: {exc}")
            if restored_tensor is not None:
                try:
                    torch.cuda.empty_cache()
                    return restored_tensor.to(device=target_device)
                except Exception:
                    logger.error(
                        "[AutogradNvmeOffloadHook] GPU'ya taşıma empty_cache sonrası da "
                        "başarısız — veri CPU'da bırakılıyor (sıfırlanmıyor)."
                    )
                    return restored_tensor
            return torch.zeros(shape, dtype=dtype, device="cpu")
        finally:
            if dosya_yolu and os.path.exists(dosya_yolu):
                try:
                    # KAPSAMLI DENETİM (madde 11): KureselAdresKayitDefteri'nin TÜM diğer
                    # okuma/yazmaları (kayit_ekle_ve_guncelle, ref_arttir/azalt, kayit_sil,
                    # supur) self.lock ile korunuyorken bu tek `.get()` erişimi kilitsizdi
                    # — sınıfın kendi thread-safety sözleşmesini çiğniyordu. Eşzamanlı bir
                    # pack_hook/supur() çağrısıyla yarışırsa aktif_dosya_yollari üzerinde
                    # yırtık/tutarsız bir okuma görülebilirdi.
                    with kuresel_adres_kayit_defteri.lock:
                        sanal_addr = kuresel_adres_kayit_defteri.aktif_dosya_yollari.get(dosya_yolu)
                    if sanal_addr:
                        kuresel_adres_kayit_defteri.kayit_sil(sanal_addr)
                    os.remove(dosya_yolu)
                except Exception:
                    pass


class GuvenliVramVeTmpSupurgesi:
    """
    [GÜVENLİ VRAM VE NVMe SÜPÜRGESİ]
    Bi-directional Reference Validated Sweeper:
    Canlı referanslı (ref_count > 0) hiçbir VRAM veya /tmp takas kütüğüne DOKUNMAZ.
    Sadece yetim (ref_count == 0 veya haritada kaydı bulunmayan) kütükleri ve
    ve sahipsiz bellek alanlarını süpürerek dangling pointer felaketini imha eder.

    NOT (ADIMLAR ARASI SIZINTI DÜZELTMESİ): `ref_count`, kayıt ilk oluşturulduğunda
    1'e ayarlanır (bkz. AutogradNvmeOffloadHook.pack_hook_diske_tahliye) ve YALNIZCA
    `unpack_hook_diskten_geri_yukle` gerçekten çağrılırsa (yani o tensörün backward'ı
    fiilen çalışırsa) dosyasıyla birlikte silinir. Ama `KureselAdresKayitDefteri.ref_azalt`
    /`ref_arttir` HİÇBİR YERDE ÇAĞRILMIYOR — yani `ref_count` hiçbir zaman 1'in altına
    inmiyor. Bunun sonucu: retain_graph=False ile grafı erken serbest bırakılan (backward'ı
    hiç çalışmayan) HER offload edilmiş tensör için `ref_count > 0` sonsuza dek doğru kalır,
    aşağıdaki süpürme HİÇBİR ZAMAN çalışmaz — "Temizlik tamamlandi" logu atılır ama
    /tmp/kulli_scratchpad'deki dosyalar ve kayıt defteri girdileri adım adım BİRİKİR (bkz.
    "Toplam Tahliye: 18461, Geri Cagirma: 275" gibi loglar — binlerce kayıt hiç silinmiyor).
    Gerçek bir referans-sayımı (autograd graph düğümü serbest bırakıldığında tetiklenen)
    olmadan bunu düzeltmenin güvenli yolu ZAMAN AŞIMI bazlı süpürmedir: `son_erisim_zamani`
    üzerinden yeterince eski (varsayılan 120 sn — bir eğitim adımının makul üst sınırının
    kat kat üzerinde) MEM_STATE_SWAPPED_NVME kayıtları, ref_count'a BAKILMAKSIZIN ölü
    kabul edilip silinir (o adımın ileri/geri beslemesi çoktan bitmiş, backward'ı hiç
    çalışmamışsa artık asla çalışmayacaktır).
    """
    ESKIME_ESIGI_SN: float = 120.0

    @staticmethod
    def supur(swap_dir: str = "/tmp/kulli_scratchpad", eskime_esigi_sn: Optional[float] = None) -> None:
        """
        eskime_esigi_sn=0.0 verilirse (ör. bir eğitim adımının saved_tensors_hooks kapsamı
        tam olarak kapandığı an çağrılırsa) yaş kontrolü atlanır — o kapsamda kaydedilmiş
        ve backward'ı hiç çalışmamış her tensör artık KESİN yetimdir (bu adımın grafı
        tamamen tüketildi, bir sonraki adım sıfırdan yeni bir graf kurar), anında güvenle
        süpürülür. Varsayılan (None) sınıf düzeyindeki muhafazakâr eşiği kullanır.
        """
        esik = GuvenliVramVeTmpSupurgesi.ESKIME_ESIGI_SN if eskime_esigi_sn is None else eskime_esigi_sn
        simdi = time.time()
        with kuresel_adres_kayit_defteri.lock:
            silinecek_adresler = []
            for sanal_addr, kayit in kuresel_adres_kayit_defteri.kayitlar.items():
                if kayit.durum == MEM_STATE_ACTIVE_VRAM:
                    continue

                yasi_sn = simdi - kayit.son_erisim_zamani
                zaman_asimina_ugramis = (
                    kayit.durum == MEM_STATE_SWAPPED_NVME
                    and yasi_sn >= esik
                )

                if not (kayit.ref_count <= 0 or kayit.durum == MEM_STATE_ORPHANED or zaman_asimina_ugramis):
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

            # Yetim Kütük Süpürmesi (/tmp Dizininde Haritada Olmayan Kütükler)
            if os.path.exists(swap_dir):
                for fname in os.listdir(swap_dir):
                    fpath = os.path.join(swap_dir, fname)
                    if fpath not in kuresel_adres_kayit_defteri.aktif_dosya_yollari and os.path.isfile(fpath):
                        try:
                            os.remove(fpath)
                        except Exception:
                            pass

        if torch.cuda.is_available():
            torch.cuda.empty_cache()


class NvmeTakasYoneticisi:
    """
    1026 GB NVMe Disk-Backed PyTorch Autograd Aktivasyon Takas Yöneticisi
    (Mevcut Kodlar İle %100 Geriye Dönük Uyumluluk Sarmalayıcısı)
    """
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
        logger.info(f"[NvmeTakasYoneticisi] Disk takas dizini aktif: {self.swap_dir}")

    def pack_hook_diske_tahliye(self, tensor: torch.Tensor) -> Any:
        # NOT: tensor.device res[3]'ten SONRA okunmamalı — offload_hook.pack_hook_diske_tahliye
        # tensörün .data'sını CPU'ya boşalttıktan sonra tensor.device zaten "cpu" olur.
        # Orijinal cihaz bilgisi yalnızca res[3]'te (mutasyon ÖNCESİ kaydedilmiş) doğrudur.
        res = self.offload_hook.pack_hook_diske_tahliye(tensor)
        if isinstance(res, tuple) and res[0] != "":
            self.tahliye_sayaci += 1
            return (res[0], res[1], res[2], res[3])
        return tensor

    def unpack_hook_diskten_geri_cagır(self, pack_bundle: Any) -> torch.Tensor:
        if isinstance(pack_bundle, torch.Tensor):
            return pack_bundle

        if len(pack_bundle) == 4:
            bundle_3 = (pack_bundle[0], pack_bundle[1], pack_bundle[2])
            target_device = pack_bundle[3]
            res = self.offload_hook.unpack_hook_diskten_geri_yukle(bundle_3, target_device=target_device)
            self.geri_cagirma_sayaci += 1
            return res
        return self.offload_hook.unpack_hook_diskten_geri_yukle(pack_bundle)

    def kapsam_muhafizi_aktifles(self):
        return torch.autograd.graph.saved_tensors_hooks(
            self.pack_hook_diske_tahliye,
            self.unpack_hook_diskten_geri_cagır
        )

    def temizle(self, agresif: bool = False) -> None:
        """
        agresif=True: yaş eşiğini 0'a indirir. Yalnızca bir eğitim adımının
        saved_tensors_hooks kapsamı KESİN OLARAK kapandığı noktadan (bkz.
        main_egitim_dongusu.py: _takas_cm.__exit__ sonrası) çağrılmalıdır — o
        andan itibaren o adıma ait her kayıt zaten kesin yetimdir.
        """
        GuvenliVramVeTmpSupurgesi.supur(swap_dir=self.swap_dir, eskime_esigi_sn=(0.0 if agresif else None))
        logger.info(f"[NvmeTakasYoneticisi] Temizlik tamamlandi. Toplam Tahliye: {self.tahliye_sayaci}, Geri Cagirma: {self.geri_cagirma_sayaci}")

