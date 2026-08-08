#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS MİMARİSİ
Ana Eğitim Yürütücü Modülü (main_egitim_dongusu.py)
================================================================================
Bu modül; ham metin külliyatını ve ARC-AGI ızgara verilerini topolojik veri
kontratlarına dönüştürerek, R-adımlı gizil akıl yürütme döngüsü, kohomolojik
aktüatör (H^1-Combat), Lif Laplasyeni difüzyonu ve GRPO/RLVR takviyeli öğrenme
kriteri altında Stiefel manifoldu kısıtlarına riayet ederek eğiten ana Sevk ve
İdare Merkezidir.
"""

import os
import sys

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Bulunduğu dizini otomatik olarak sys.path'e ekle (Kaggle Dataset İçe Aktarma Güvenliği)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import json
import time
import logging
import math
import subprocess
import gc
from typing import Dict, Any, List, Tuple, Optional, Union

import kontratlar
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.checkpoint import checkpoint

from kontratlar import (
    Model_TopolojikKonfigurasyon,
    SistemYapilandirmasi,
    E1_HamMetinAkisi,
    E2_ByteTensoru,
    E3_SinirOperatorleri,
    E4_LifDemeti,
    E5_A_MevcutGizilDurum,
    E5_B_BellekGonderimi,
    E6_GizilSorgu,
    E7_LokalBilgi,
    E8_SentetikAraDurum,
    E9_GuncellenmisGizilDurum,
    E10_KulliManaMatrisi,
    E11_ParalelGomuluVektorlerMatrisi,
    E12_ParalelTokenOlasilikMatrisi,
    E13_HedefTokenDizisi,
    E14_SistemKayipMetrikleri,
    E15_GuncellenmisBellekMatrisi,
    E16_UretilenMetinCiktisi,
    E17_EgitimGradiyantPaketi,
    E18_TopolojiDenetimRaporu,
    N1_ByteAyristirici,
    N2_TopoXHucreOlusumu,
    N3_LifSinirlamaAtama,
    N4_SorguSecici,
    N5_CevapSuzucu,
    N6_KohomolojikAktor,
    N7_LifLaplasyeniCozucu,
    N8_ChebyshevKatsayiProjeksiyon,
    N8_B_DinamikUzunlukSecici,
    N9_ChebyshevVandermondeCarpim,
    N10_SozlukSoftmaxIzdusem,
    N11_LifLaplasyeniBlokInsaEdici,
    N12_BellekBaglamYoneticisi,
    N13_StiefelManifolduIzdusumu,
    N14_OdulTopolojikDevresmezlikMotoru,
    N15_EgitimKontrolNoktasiYoneticisi,
    N16_ArcIzgaraDonusturucu,
    Sheaf_KAN_Superpozisyon_Operatoru,
    SMW_SifirParazit_BellekYoneticisi,
    al_cevrimdisi_veya_tiktoken_tokenizer,
    LPT_DosyaDengeliDagitici,
    N4_SorguSecici_AltAg,
    N5_CevapSuzucu_AltAg,
    N6_KohomolojikAktor_AltAg,
    Maarif_NedenselSuzgec,
    Yardimci_ChebyshevMatrisHesaplayici,
    Riyazi_LifLaplasyeniBlokInsaEdici,
    Bellek_BaglamYoneticisi,
    Bellek_TopolojikDikkatYazici,
    Riyazi_StiefelManifolduIzdusumu,
    Riyazi_Pareto_PCGrad_MGDA_Operator,
    stiefel_qr_projection,
    BiliselKanvasModeli,
    Hafiza_Izleyici_ve_VRAM_Denetci,
    Kayip_VICReg_UcluBilgiKorunumu
)

from logging.handlers import RotatingFileHandler

# ==============================================================================
# LOGGING (GÜNLÜKLEME) YAPILANDIRMASI — DUPLICATE ENGELLEME VE SEVİYE AYRIMI
# ==============================================================================
def kur_logging_sistemi(log_dosyasi: str = 'egitim_dongusu_icra.log') -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()  # Çift basma (duplicate logging) sorununu kökten çözer

    # 1. Döner Dosya Handler'ı (Maksimum 10 MB - Disk Şişmesini Engeller)
    fh = RotatingFileHandler(log_dosyasi, maxBytes=10*1024*1024, backupCount=1, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - (%(name)s) - %(message)s'))
    root.addHandler(fh)

    # 2. Konsol Handler'ı (Sadece Temiz Metrik Özetleri: INFO ve üzeri)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s'))
    root.addHandler(ch)

kur_logging_sistemi()
logger = logging.getLogger('MainEgitim')

# ===========================================================================
# KAGGLE SABİTLERİ VE API CLI UPLOADER
# ===========================================================================
KAGGLE_WORKING_DIR = "/kaggle/working" if os.path.exists("/kaggle/working") else "./checkpoints"

class KaggleDatasetUploader:
    """
    Checkpoint NPZ dosyasını Kaggle özel veri seti olarak yükler.

    Komut:
      kaggle datasets version -p /kaggle/working -m "Commit checkpoint step N"

    Gereksinimler:
      - KAGGLE_USERNAME ve KAGGLE_KEY env var'ları set edilmiş olmalı
        VEYA /kaggle/input/kaggle-api-cred/kaggle.json mevcut olmalı
      - `kaggle` CLI kurulu olmalı (Kaggle notebook'larında varsayılan)

    Hata politikası:
      Upload başarısız olursa yalnızca uyarı loglanır.
      Eğitim bu hata nedeniyle DURDURULMAZ.
    """

    def __init__(self,
                 dataset_slug: str = "",
                 working_dir: str = KAGGLE_WORKING_DIR,
                 cred_path: str = "/kaggle/input/kaggle-api-cred/kaggle.json"):
        self.dataset_slug = dataset_slug
        self.working_dir  = working_dir
        self.cred_path    = cred_path
        self._configured  = False
        self._setup_credentials()

    def _setup_credentials(self) -> None:
        """Kaggle kimlik bilgilerini env var'a veya ~/.kaggle/kaggle.json'a kopyalar."""
        # Önce mevcut env var'ları kontrol et
        if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
            self._configured = True
            return

        # Bağlı credential dosyasını dene
        if os.path.isfile(self.cred_path):
            try:
                with open(self.cred_path, "r", encoding="utf-8") as f:
                    creds = json.load(f)
                os.environ["KAGGLE_USERNAME"] = creds.get("username", "")
                os.environ["KAGGLE_KEY"]      = creds.get("key", "")
                # ~/.kaggle/kaggle.json'a da yaz (CLI için)
                kaggle_dir = os.path.expanduser("~/.kaggle")
                os.makedirs(kaggle_dir, exist_ok=True)
                dest = os.path.join(kaggle_dir, "kaggle.json")
                if not os.path.isfile(dest):
                    with open(dest, "w", encoding="utf-8") as fw:
                        json.dump(creds, fw)
                    os.chmod(dest, 0o600)
                self._configured = True
                logger.info("  [Upload] Kaggle kimlik bilgileri yüklendi.")
            except Exception as exc:
                logger.warning(f"  [Upload] Kimlik bilgisi okunamadı: {exc}")
        else:
            logger.warning(
                "  [Upload] Kaggle kimlik bilgisi bulunamadı. "
                "Upload devre dışı (eğitim devam eder)."
            )

    def upload(self, step: int, message: Optional[str] = None) -> bool:
        """
        /kaggle/working dizinindeki checkpoint NPZ'yi yeni dataset versiyonu olarak yükler.

        Döndürür: True → başarılı, False → hata (eğitim devam eder)
        """
        if not self._configured:
            logger.warning("  [Upload] Kimlik bilgisi yok — upload atlandı.")
            return False

        commit_msg = message or f"Checkpoint step {step} — auto commit"
        cmd = [
            "kaggle", "datasets", "version",
            "-p", self.working_dir,
            "-m", commit_msg,
        ]

        logger.info(f"  [Upload] Kaggle CLI çalıştırılıyor: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,           # 2 dakika yükleme zaman aşımı
            )
            if result.returncode == 0:
                logger.info(
                    f"  [Upload] Başarılı: step={step}\n"
                    f"           {result.stdout.strip()}"
                )
                return True
            else:
                logger.warning(
                    f"  [Upload] CLI hata kodu {result.returncode}:\n"
                    f"           {result.stderr.strip()}"
                )
                return False
        except subprocess.TimeoutExpired:
            logger.warning("  [Upload] Zaman aşımı (120 s) — upload atlandı.")
            return False
        except FileNotFoundError:
            logger.warning("  [Upload] 'kaggle' CLI bulunamadı — upload atlandı.")
            return False
        except Exception as exc:
            logger.warning(f"  [Upload] Beklenmedik hata: {exc}")
            return False


            
# ==============================================================================
# I. GRPO ÖDÜL VE KANIT (RLVR) MOTORLARI
# ==============================================================================
class Odul_TopolojikDevresmezlikMotoru:
    """GRPO Topolojik Tutarlılık ve Doğruluk Skorlama Motoru"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def hesapla(self, P: torch.Tensor, hedefler: torch.Tensor) -> torch.Tensor:
        # P: [B, V_size, N], hedefler: [B, N]
        B, V_size, N = P.shape
        preds = torch.argmax(P, dim=1)  # [B, N]
        is_correct = (preds == hedefler[:, :N]).float().mean(dim=-1)
        topolojik_invaryant = 1.0 - torch.std(P, dim=(1, 2))
        oduller = is_correct * 2.0 + topolojik_invaryant * 0.5
        return oduller


class Kayip_GRPO_Kriteri:
    """GRPO (Group Relative Policy Optimization) Kayıp Fonksiyonu"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def hesapla_vektor(self, P: torch.Tensor, hedefler: torch.Tensor, oduller: torch.Tensor) -> torch.Tensor:
        B, V_size, N = P.shape
        targets = hedefler[:, :N]
        # 200.019 boyutlu dev matris üzerinde torch.log almak yerine önce hedef olasılıklarını gather et (VRAM 1.91 GB -> 1 KB):
        p_target = P.gather(1, targets.unsqueeze(1)).squeeze(1)  # [B, N]
        nll = -torch.log(p_target + 1e-9).mean(dim=-1)  # [B]
        
        # Ödül ile avantaj hesaplaması
        std = oduller.std() if oduller.std() > 0 else 1e-8
        avantajlar = (oduller - oduller.mean()) / (std + 1e-8)
        kayip_vec = nll * avantajlar.detach()  # [B]
        return kayip_vec

    def hesapla(self, P: torch.Tensor, hedefler: torch.Tensor, oduller: torch.Tensor) -> torch.Tensor:
        return self.hesapla_vektor(P, hedefler, oduller).mean()


# ==============================================================================
# II. EĞİTİM DESTEK VE KONTROL NOKTASI YÖNETİCİLERİ
# ==============================================================================
class Riyazi_AgirlikIlkleyici:
    """Ağırlık Dikgenleştirme ve İlklendirme Yöneticisi"""
    def __init__(self):
        pass

    def ilkle(self, modules: List[nn.Module]):
        for m in modules:
            if isinstance(m, nn.Module):
                for sub_m in m.modules():
                    if isinstance(sub_m, nn.Linear):
                        if hasattr(sub_m, 'weight'):
                            nn.init.orthogonal_(sub_m.weight)
                            if sub_m.bias is not None:
                                nn.init.constant_(sub_m.bias, 0.0)


class Egitim_KontrolNoktasiYoneticisi:
    """Hakiki Model Checkpoint Kaydedici ve Yükleyici (NPZEntegreli)"""
    def __init__(self, kaydetme_dizini: str = "./checkpoints"):
        self.kaydetme_dizini = kaydetme_dizini
        self._npz_mgr = NPZCheckpointManager(checkpoint_dir=kaydetme_dizini)

    def kaydet(self, step: int, model: Any, optimizer: Optional[optim.Optimizer] = None, kayip: float = 0.0, loss_history: Optional[List[float]] = None, is_best: bool = False) -> str:
        return self._npz_mgr.save_pytorch_model(
            step=step,
            token_offset=step * 256,
            model=model,
            optimizer=optimizer,
            loss_history=loss_history,
            is_best=is_best
        )


from checkpoint_manager import NPZCheckpointManager, HiyerarşikHafizaYoneticisi

class Egitim_TopolojikVeriYukleyici:
    """
    Çoklu Formatlı ve Klasör Yapılı Veri Yükleyici.
    .txt, .md, .json, .py vb. tüm dosyaları özyinelemeli (recursive) tarar
    ve hiyerarşik harita oluşturur.
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon, manifest_yolu: str = "/kaggle/working/verisetleri_manifest.json"):
        self.config = config
        self.manifest_yolu = manifest_yolu
        self.verisetleri: Dict[str, Dict[str, List[str]]] = {}
        self.tarama_yap()

    def tarama_yap(self):
        """Manifest dosyasından veya yerel dizinden tüm veri kümesi ağacını kurar."""
        klasorler_veya_dosyalar = []
        if os.path.exists(self.manifest_yolu):
            try:
                with open(self.manifest_yolu, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                    klasorler_veya_dosyalar = manifest_data.get("verisetleri", [])
                logger.info(f"Manifest dosyasından {len(klasorler_veya_dosyalar)} veri yolu okundu: {self.manifest_yolu}")
            except Exception as e:
                logger.warning(f"Manifest okunurken hata: {e}")

        if not klasorler_veya_dosyalar:
            klasorler_veya_dosyalar = ["./"]  # Varsayılan yerel arama

        st_extensions = ('.txt', '.md', '.json', '.py', '.c', '.cpp', '.h', '.csv', '.yaml', '.yml')

        for idx, yol in enumerate(klasorler_veya_dosyalar):
            veriseti_adi = f"veriseti_{idx+1}_" + os.path.basename(os.path.normpath(yol))
            self.verisetleri[veriseti_adi] = {}

            if os.path.isfile(yol):
                klasor = os.path.dirname(os.path.normpath(yol)) or "."
                self.verisetleri[veriseti_adi][klasor] = [os.path.normpath(yol)]
            elif os.path.isdir(yol):
                for root, dirs, files in os.walk(yol):
                    valid_files = [
                        os.path.normpath(os.path.join(root, f))
                        for f in files if f.endswith(st_extensions)
                    ]
                    if valid_files:
                        self.verisetleri[veriseti_adi][os.path.normpath(root)] = valid_files

    def dosya_parcalari_oku(self, dosya_yolu: str, chunk_size: int = 65536):
        """
        Büyük dosyaları (2 GB, 410 MB vb.) son baytına kadar parça parça (streaming chunk) okur.
        Hiçbir dosyayı ilk 4KB'ta yarım bırakmaz.
        Döndürür: (chunk_metin, hedef_tensor, is_last_chunk, chunk_idx, bytes_read)
        """
        try:
            file_size = os.path.getsize(dosya_yolu)
        except Exception:
            file_size = 0

        bytes_read = 0
        chunk_idx = 0
        
        try:
            with open(dosya_yolu, 'r', encoding='utf-8', errors='ignore') as f:
                while True:
                    metin = f.read(chunk_size)
                    if not metin:
                        break
                    
                    bytes_read += len(metin.encode('utf-8', errors='ignore'))
                    chunk_idx += 1
                    is_last = (file_size == 0) or (bytes_read >= file_size) or (len(metin) < chunk_size)

                    if not metin.strip():
                        if is_last:
                            break
                        continue

                    # Metnin SOTA BPE / Aksiyomatik Çevrimdışı Token ID'lerini hedef tensör olarak çıkar
                    tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
                    token_ids = tokenizer.encode(metin)
                    if len(token_ids) < self.config.N:
                        token_ids = token_ids + [0] * (self.config.N - len(token_ids))
                    else:
                        token_ids = token_ids[:self.config.N]
                    
                    token_ids = [t % self.config.V_size for t in token_ids]
                    hedef_tensor = torch.tensor([token_ids] * self.config.batch_size, dtype=torch.long, device=self.config.device)
                    yield metin, hedef_tensor, is_last, chunk_idx, bytes_read, file_size
        except Exception as e:
            logger.warning(f"Dosya okuma hatası ({dosya_yolu}): {e}")

    def dosya_okumu_yap(self, dosya_yolu: str) -> Tuple[str, torch.Tensor]:
        """Geriye dönük uyumluluk için tekil parça okuma sarmalayıcısı."""
        for metin, hedef_tensor, _, _, _, _ in self.dosya_parcalari_oku(dosya_yolu, chunk_size=65536):
            return metin, hedef_tensor
        return "Bos icerikli veri dosyasi.", torch.tensor([[32] * self.config.N] * self.config.batch_size, dtype=torch.long, device=self.config.device)


from paralel_gpu import GPU_Tespitci, GPU_EgitimDagitimcisi, Veri_Paralel_Dagitici, Topolojik_GPU_Cesitlendirici, Homojen_Chunk_Dagitici

# ==============================================================================
# III. HAKİKİ VE DETAYLI EĞİTİM YÜRÜTÜCÜ SÜRECİ (MAIN EXECUTION)
# ==============================================================================
def Main_EgitimYurutucu(konfig_yolu: Optional[str] = None, manifest_yolu: str = "/kaggle/working/verisetleri_manifest.json") -> None:
    logger.info("================================================================================")
    logger.info("BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS MİMARİSİ EĞİTİM YÜRÜTÜCÜSÜ (ÇOKLU GPU PARALEL DÖNGÜ)")
    logger.info("================================================================================")
    
    # 0. Otomatik GPU Tespiti ve Paralel Dağıtım Kurulumu
    gpu_tespitci = GPU_Tespitci()
    gpu_dagitici = GPU_EgitimDagitimcisi(gpu_tespitci)
    veri_dagitici = Veri_Paralel_Dagitici(gpu_tespitci)

    # 1. Konfigürasyon Yükleme
    param_dict = {}
    if konfig_yolu and os.path.exists(konfig_yolu):
        with open(konfig_yolu, 'r', encoding='utf-8') as f:
            param_dict = json.load(f)
        logger.info(f"Konfigürasyon dosyasından yüklendi: {konfig_yolu}")
        
    config = Model_TopolojikKonfigurasyon(param_dict)
    config.device = str(gpu_tespitci.device)
    gpu_cesitlendirici = Topolojik_GPU_Cesitlendirici(config, noise_std=0.0)
    
    GRPO_G = getattr(config, 'GRPO_G', 4)
    # Güçlü Ölçekleme (Strong Scaling): Toplam G sabit tutulur, GPU'lar 4 yörüngeyi bölüşerek adım süresini 2x/4x hızlandırır.
    if gpu_tespitci.coklu_gpu_mu:
        gpu_basina_g = max(1, GRPO_G // gpu_tespitci.gpu_sayisi)
        logger.info(f"  [Güçlü Ölçekleme Etkin] Sabit Toplam GRPO Grup (G): {GRPO_G} | {gpu_tespitci.gpu_sayisi} GPU İş Bölümü (GPU Başına: {gpu_basina_g} yörünge) | Adım Süresi {gpu_tespitci.gpu_sayisi}x Hızlandırıldı!")

    logger.info(f"Çalışma Cihazı: {config.device} | GRPO Grup (G): {GRPO_G} | Rekürens (R): {config.R}")

    # 2. Checkpoint ve Hiyerarşik Hafıza Yöneticisi
    ckpt_dizini = "/kaggle/working" if os.path.exists("/kaggle/working") else "./checkpoints"
    npz_mgr = NPZCheckpointManager(checkpoint_dir=ckpt_dizini)

    # Kaggle disk dolmasını engellemek için başlangıçta yetim ve eski dinamik dosyaları temizle
    npz_mgr.purge_orphan_checkpoints()
    npz_mgr.load_hafiza_state()

    # 3. Bilişsel Düğümler (N1 - N16) ve Modüllerin Açık İnşası
    n1_byte = N1_ByteAyristirici(config).to(config.device)
    n2_topox = N2_TopoXHucreOlusumu(config).to(config.device)
    n3_lif = N3_LifSinirlamaAtama(config).to(config.device)
    
    e_coboundary_dim = (config.V_nodes - 1) * config.d_e
    alt_n4 = N4_SorguSecici_AltAg(config).to(config.device)
    alt_n5 = N5_CevapSuzucu_AltAg(config).to(config.device)
    alt_n6 = N6_KohomolojikAktor_AltAg(config, e_coboundary_dim).to(config.device)
    
    n4_sorgu = N4_SorguSecici(config=config).to(config.device)
    n5_cevap = N5_CevapSuzucu(config=config).to(config.device)
    n6_aktor = N6_KohomolojikAktor(alt_n6, config=config).to(config.device)
    n7_cozucu = N7_LifLaplasyeniCozucu(config).to(config.device)
    n8_chebyshev = N8_ChebyshevKatsayiProjeksiyon(config).to(config.device)
    n8_b_uzunluk = N8_B_DinamikUzunlukSecici(config).to(config.device)
    n9_vandermonde = N9_ChebyshevVandermondeCarpim(config).to(config.device)
    n10_sozluk = N10_SozlukSoftmaxIzdusem(config).to(config.device)
    
    cheby_calc = Yardimci_ChebyshevMatrisHesaplayici(config)
    
    laplasyen_insa = N11_LifLaplasyeniBlokInsaEdici(config)
    meclis_bellek = N12_BellekBaglamYoneticisi(config).to(config.device)
    bellek_yazici = Bellek_TopolojikDikkatYazici(config).to(config.device)
    odul_motoru = N14_OdulTopolojikDevresmezlikMotoru(config)
    grpo_kriteri = Kayip_GRPO_Kriteri(config)
    stiefel_izdusurucu = N13_StiefelManifolduIzdusumu()
    pareto_pcgrad_operator = Riyazi_Pareto_PCGrad_MGDA_Operator()
    vicreg_kriteri = Kayip_VICReg_UcluBilgiKorunumu().to(config.device)
    
    veri_yukleyici = Egitim_TopolojikVeriYukleyici(config, manifest_yolu=manifest_yolu)

    tum_moduller = {
        'n1_byte': n1_byte,
        'n3_phi': n3_lif,
        'n4': n4_sorgu,
        'n5': n5_cevap,
        'n6': alt_n6,
        'n6_aktor': n6_aktor,
        'n7': n7_cozucu,
        'n8': n8_chebyshev,
        'n8_b': n8_b_uzunluk,
        'n10': n10_sozluk,
        'bellek': meclis_bellek,
        'bellek_yazici': bellek_yazici
    }



    # Modül Ağırlıklarını Dikgen (Orthogonal) Olarak İlkle
    agirlik_ilkleyici = Riyazi_AgirlikIlkleyici()
    agirlik_ilkleyici.ilkle(list(tum_moduller.values()))

    # Çoklu GPU için modülleri DataParallel ile sarmala
    tum_moduller = gpu_dagitici.modulleri_paralellestir(tum_moduller)
    
    trainable_params = []
    for m in tum_moduller.values():
        trainable_params.extend(list(m.parameters()))
        
    optimizer = optim.AdamW(trainable_params, lr=config.lr, weight_decay=1e-4)
    logger.info("Tüm Sinir Ağları ve Stiefel Parametreleri Optimizasyona Bağlandı.")

    vram_denetci = Hafiza_Izleyici_ve_VRAM_Denetci(cihaz=config.device, kritik_esik_yuzde=0.85)

    # Hakiki Checkpoint ve Hiyerarşik Hafıza Restorasyonu
    baslangic_step, loss_history = npz_mgr.load_pytorch_model(tum_moduller, optimizer)
    current_step = baslangic_step
    
    # Restore sonrası Stiefel dikgenliğini garantile
    if hasattr(n3_lif, 'phi_matrisleri'):
        stiefel_izdusurucu.izdüsür(n3_lif.phi_matrisleri)
    elif hasattr(n3_lif, 'phi_base'):
        with torch.no_grad():
            n3_lif.phi_base.copy_(stiefel_qr_projection(n3_lif.phi_base.data))
    
    best_loss = min(loss_history) if loss_history else float('inf')
    SAVE_EVERY_N_STEPS = getattr(config, 'save_every_n_steps', 100)
    logger.info(f"Eğitim Başlangıç Adımı (Step): {current_step} | En İyi Kayıp (Best Loss): {best_loss:.6f} | Periyodik Kayıt Sıklığı: {SAVE_EVERY_N_STEPS} Adım")

    # 4. Hiyerarşik Dosya Hafızası ile Sürekli Eğitim Döngüsü
    MAX_TRAINING_SECONDS = 41400.0  # 11 saat 30 dakika (Kaggle 12h aşımı öncesi emniyet kapaması)
    egitim_baslangic_zamani = time.time()
    global_bytes_processed = 0
    last_logged_500mb_chunk = 0
    global_chunk_idx = 0

    current_gpu_rank = getattr(gpu_tespitci, 'rank', 0)
    num_gpus = max(1, getattr(gpu_tespitci, 'gpu_sayisi', 1))
    chunk_dagitici = Homojen_Chunk_Dagitici(chunk_size_bytes=65536, rank=current_gpu_rank, world_size=num_gpus)

    for veriseti_adi, klasorler in veri_yukleyici.verisetleri.items():
        tum_veriseti_klasorleri = list(klasorler.keys())
        for klasor_yolu, dosyalar in klasorler.items():
            tum_klasor_dosyalari = dosyalar
            for dosya_yolu in dosyalar:
                # 3 Kademeli Hiyerarşik Hafıza Kontrolü
                if npz_mgr.hafiza.is_dosya_islenmis(dosya_yolu, klasor_yolu, veriseti_adi):
                    logger.debug(f"  [Atlandı] Zaten eğitilmiş içerik: {dosya_yolu}")
                    continue

                # Dosyayı SONUNA KADAR 64 KB parça parça (streaming chunk) oku ve eğit
                last_logged_pct = -1.0
                for e1_girdi_metni, hedef_tensor, is_last_chunk, chunk_idx, bytes_read, file_size in veri_yukleyici.dosya_parcalari_oku(dosya_yolu, chunk_size=65536):
                    # HAKİKİ DENGELİ DAĞITIM: Sadece bu GPU'nun payına düşen chunk'ı işle! (global_chunk_idx % world_size == rank)
                    process_this_chunk = chunk_dagitici.should_process_chunk(global_chunk_idx)
                    global_chunk_idx += 1
                    if not process_this_chunk:
                        continue

                    # 11 Saat 30 Dakika Emniyet Zaman Sınırı Denetimi
                    gecen_toplam_sure = time.time() - egitim_baslangic_zamani
                    if gecen_toplam_sure >= MAX_TRAINING_SECONDS:
                        logger.info("================================================================================")
                        logger.info(f"  [EMNİYET ZAMAN LİMİTİ] 11 Saat 30 Dakikalık sınır doldu ({gecen_toplam_sure/3600:.2f} saat). Tüm durum atomik olarak kaydediliyor...")
                        npz_mgr.save_pytorch_model(
                            step=current_step,
                            token_offset=current_step * config.N,
                            model=tum_moduller,
                            optimizer=optimizer,
                            loss_history=loss_history,
                            is_best=False
                        )
                        npz_mgr.save_hafiza_state()
                        logger.info("  [EMNİYET ZAMAN LİMİTİ] Tüm model ve hafıza durumu başarıyla kaydedildi. Oturum emniyetle kapatılıyor.")
                        logger.info("================================================================================")
                        return

                    epoch_baslangic = time.time()
                    optimizer.zero_grad(set_to_none=True)

                    max_chunk_len = getattr(config, 'N', 1024)
                    e1_girdi_metni_chunk = e1_girdi_metni[:max_chunk_len] if len(e1_girdi_metni) > max_chunk_len else e1_girdi_metni
                    e1_girdi = E1_HamMetinAkisi(X_text=e1_girdi_metni_chunk)

                    def vjp_cerrahi_enjekte_et(vector_loss: torch.Tensor, target_params: List[nn.Parameter], scale: float = 1.0) -> None:
                        """
                        Vektör hata sahasının (vector_loss) ilgili parametre alt-manifolduna (target_params)
                        VJP (Vector-Jacobian Product) tensör kontraksiyonu ile doğrudan gradyan enjeksiyonu yapar.
                        Skaler .backward() veya .mean() kullanılmaz! Autograd grafiği anında serbest bırakılır.
                        """
                        trainable_in_group = [p for p in target_params if p.requires_grad]
                        if not trainable_in_group:
                            return
                        # Kanonik Gradyan Temizliği (VJP öncesi artık gradyan birikmesini engeller)
                        for p in trainable_in_group:
                            p.grad = None
                        clean_vec_loss = torch.clamp(torch.nan_to_num(vector_loss, nan=0.0, posinf=100.0, neginf=-100.0), min=-100.0, max=100.0)
                        loss_std = torch.std(clean_vec_loss, dim=0, keepdim=True) if clean_vec_loss.numel() > 1 else torch.ones_like(clean_vec_loss)
                        v_probe = scale * (1.0 / (loss_std + 1e-6)) * (clean_vec_loss / (torch.norm(clean_vec_loss) + 1e-6))
                        try:
                            grads = torch.autograd.grad(
                                outputs=clean_vec_loss,
                                inputs=trainable_in_group,
                                grad_outputs=v_probe,
                                retain_graph=False,
                                allow_unused=True
                            )
                            for p, g in zip(trainable_in_group, grads):
                                if g is not None:
                                    g_clean = torch.nan_to_num(g.detach(), nan=0.0, posinf=1.0, neginf=-1.0)
                                    g_norm = torch.norm(g_clean)
                                    if g_norm > 1.0:
                                        g_clean = g_clean / (g_norm + 1e-8)
                                    if p.grad is None:
                                        p.grad = g_clean
                                    else:
                                        p.grad = p.grad + g_clean
                        except Exception as exc:
                            logger.warning(f"  [VJP Cerrahi Uyarısı] Gradyan enjeksiyonu uyarısı: {exc}")

                    # ------------------------------------------------------------------------------
                    # FAZ 2: TOPOLOJİK İSKELET VE LİF LAPLASYENİ HESABI (N1 -> N2 -> N3 -> N11)
                    # ------------------------------------------------------------------------------
                    optimizer.zero_grad(set_to_none=True)
                    e2_byte, x_initial = n1_byte.forward(e1_girdi)
                    raw_n2_topox = gpu_dagitici.kok_modul_al(n2_topox)
                    e3_sinir = raw_n2_topox.forward(e2_byte, x_initial=x_initial, mode='train')
                    e4_lif = n3_lif.forward(e3_sinir, x_initial)
                    vram_denetci.yokla_ve_raporla("N1_N3_TopolojiIskelesi", adim_no=current_step)
                    logger.debug(f"[N1-N3 Topoloji İskelesi] Byte Şekli: {e2_byte.byte_tensor.shape} | x^(0): {x_initial.shape} | Sınırlama Matrisleri Sayısı (phi): {len(e4_lif.phi_matrisleri)}")
                    
                    D0_op, Delta_0_op = laplasyen_insa.insa_et(e3_sinir, e4_lif.phi_matrisleri)
                    vram_denetci.yokla_ve_raporla("N11_LifLaplasyeniInsa", adim_no=current_step)
                    logger.debug(f"[N_LA Lif Laplasyeni İnşası] D0 Coboundary: {D0_op.shape} | Delta0 Laplasyen: {Delta_0_op.shape}")
                    
                    d_vec2 = n7_cozucu.hesapla_uyumsuzluk_vektoru(x_initial, D0_op)
                    e_vec2 = n7_cozucu.hesapla_dirichlet_enerjisi_vektoru(x_initial, Delta_0_op)
                    
                    # Doğrudan Parametre Cerrahisi: theta_1 (Stiefel Lif Demeti) ve theta_2 (Topox Kompleksi)
                    vjp_cerrahi_enjekte_et(d_vec2, list(n3_lif.parameters()) + list(n2_topox.parameters()))
                    vjp_cerrahi_enjekte_et(e_vec2, list(n3_lif.parameters()) + list(n2_topox.parameters()))
                    g_faz2 = [p.grad.detach().clone() if p.grad is not None else torch.zeros_like(p) for p in trainable_params]
                    vram_denetci.yokla_ve_raporla("LOCO_Faz2_GrafSilindi", adim_no=current_step)
                    logger.info(f"  [LOCO Faz 2] Topolojik İskelet VJP Cerrahisi Tamamlandı | L_coboundary: {d_vec2.mean().item():.6f} | L_dirichlet: {e_vec2.mean().item():.6f}")

                    # ------------------------------------------------------------------------------
                    # FAZ 3: R-ADIMLI REKÜRENS DÖNGÜSÜ VE H^1 KOHOMOLOJİK AKIL YÜRÜTME (N4 -> N5 -> N6 -> N7)
                    # ------------------------------------------------------------------------------
                    x_start_grouped = x_initial.repeat_interleave(GRPO_G, dim=0).detach()
                    x_start_grouped = gpu_cesitlendirici.cesitlendir(x_start_grouped, step_seed=current_step)
                    x_current = x_start_grouped.clone().detach()  # LOCO Faz 2 -> Faz 3 Sınır Koparma İlkesi (Strict Phase Detachment)
                    e2_byte_grouped = E2_ByteTensoru(byte_tensor=e2_byte.byte_tensor.repeat_interleave(GRPO_G, dim=0))
                    hedef_grouped = hedef_tensor.repeat_interleave(GRPO_G, dim=0)
                    active_b = x_current.shape[0]
                    M_current = meclis_bellek.get_memory(active_b).M
                    
                    sorgu_q_list = []
                    cevap_a_list = []
                    n6_aktor.update_operators(D0_op, Delta_0_op)
                    for r in range(1, config.R + 1):
                        e3_sinir = raw_n2_topox.forward(e2_byte_grouped, x_initial=x_current, mode='train', D0_base=D0_op)
                        D0_op, Delta_0_op = laplasyen_insa.insa_et(e3_sinir, e4_lif.phi_matrisleri)
                        n6_aktor.update_operators(D0_op, Delta_0_op)

                        e5_a = E5_A_MevcutGizilDurum(x_r=x_current)
                        e5_b = E5_B_BellekGonderimi(M=M_current)
                        
                        e6_sorgu = n4_sorgu.forward(e5_a, D0_operator=D0_op, A_adjacency=e3_sinir.D1, bellek=e5_b)
                        e7_lokal = n5_cevap.forward(e6_sorgu, e5_b)
                        
                        sorgu_q_list.append(e6_sorgu.q_r)
                        cevap_a_list.append(e7_lokal.a_r)
                        
                        def _tekil_n6_n7_step(x_c, q_c, a_c, D0_c, Delta0_c):
                            e5_a_st = E5_A_MevcutGizilDurum(x_r=x_c)
                            e6_sorgu_st = E6_GizilSorgu(q_r=q_c)
                            e7_lokal_st = E7_LokalBilgi(a_r=a_c)
                            e8_sentetik_st = n6_aktor.forward(e5_a_st, e6_sorgu_st, e7_lokal_st)
                            e9_guncel_st = n7_cozucu.forward(e8_sentetik_st, Delta0_c, e5_a_st)
                            return e9_guncel_st.x_next, e8_sentetik_st.synthetic_state

                        x_next_val, h_syn_val = checkpoint(
                            _tekil_n6_n7_step,
                            x_current,
                            e6_sorgu.q_r,
                            e7_lokal.a_r,
                            D0_op,
                            Delta_0_op,
                            use_reentrant=False
                        )
                        
                        e8_sentetik = E8_SentetikAraDurum(synthetic_state=h_syn_val)
                        e9_guncel = E9_GuncellenmisGizilDurum(x_next=x_next_val)
                        
                        if hasattr(n7_cozucu, 'analitik_matris_eksponansiyel_yesil_cozum'):
                            x_green_analitik = n7_cozucu.analitik_matris_eksponansiyel_yesil_cozum(
                                Delta_0=Delta_0_op,
                                h_syn=e8_sentetik.synthetic_state,
                                x_0=x_current,
                                r_step=r
                            )
                        
                        if isinstance(meclis_bellek, SMW_SifirParazit_BellekYoneticisi):
                            k_r_key = e6_sorgu.q_r[:, :getattr(config, 'K', 16)] if e6_sorgu.q_r.shape[1] >= getattr(config, 'K', 16) else F.pad(e6_sorgu.q_r, (0, getattr(config, 'K', 16) - e6_sorgu.q_r.shape[1]))
                            v_r_val = e7_lokal.a_r
                            e5_b_yeni = meclis_bellek.write(k_r=k_r_key, v_r=v_r_val)
                        else:
                            e5_b_yeni = bellek_yazici.yaz(e9_guncel.x_next, e6_sorgu, e5_b, e7_lokal)
                        
                        x_current = e9_guncel.x_next
                        M_current = e5_b_yeni.M
                        mevcut_durum = E5_A_MevcutGizilDurum(x_r=x_current)

                        d_disc_r = n7_cozucu.hesapla_uyumsuzluk(mevcut_durum.x_r, D0_op)
                        dirichlet_r = n7_cozucu.hesapla_dirichlet_enerjisi(mevcut_durum.x_r, Delta_0_op)
                        vram_denetci.yokla_ve_raporla(f"Rekurens_Adimi_r{r}", adim_no=current_step)
                        logger.debug(f"  └─ Gizil Rekürens Adımı r={r}/{config.R} | d_discrepancy: {d_disc_r:.6f} | Dirichlet E(x): {dirichlet_r:.6f}")

                    d_vec3 = n7_cozucu.hesapla_uyumsuzluk_vektoru(mevcut_durum.x_r, D0_op)
                    e_vec3 = n7_cozucu.hesapla_dirichlet_enerjisi_vektoru(mevcut_durum.x_r, Delta_0_op)
                    
                    # Doğrudan Parametre Cerrahisi: theta_2 (Sheaf-KAN & Aktor), theta_3 (Sorgu), theta_4 (Cevap)
                    l_loco3_vec = torch.cat([d_vec3.view(-1), F.relu(e_vec3).view(-1)]) / float(max(1, config.R))
                    vjp_cerrahi_enjekte_et(l_loco3_vec, list(alt_n6.parameters()) + list(n4_sorgu.parameters()) + list(n5_cevap.parameters()))
                    g_faz3 = [p.grad.detach().clone() if p.grad is not None else torch.zeros_like(p) for p in trainable_params]
                    vram_denetci.yokla_ve_raporla("LOCO_Faz3_GrafSilindi", adim_no=current_step)
                    logger.info(f"  [LOCO Faz 3] R-Adımlı Rekürens VJP Cerrahisi Tamamlandı | L_coboundary: {d_vec3.mean().item():.6f} | L_dirichlet: {e_vec3.mean().item():.6f}")

                    # ------------------------------------------------------------------------------
                    # FAZ 4-5: CHEBYSHEV SPEKTRAL PROJEKSİYON VE GRPO ÖDÜL KANVASI (N8 -> N10)
                    # ------------------------------------------------------------------------------
                    e9_guncel_detached = E9_GuncellenmisGizilDurum(x_next=e9_guncel.x_next.detach())
                    e10_kulli = n8_chebyshev.forward(e9_guncel_detached)
                    N_star, L_arc_tensor, N_ste_tensor, delta_n_tensor = n8_b_uzunluk.forward(e10_kulli, cheby_calc)
                    L_arc_val = L_arc_tensor.item()
                    N_teorik_val = N_ste_tensor.item()
                    T_matrix = cheby_calc.hesapla(N=N_star)
                    
                    e11_gomulu = n9_vandermonde.forward(e10_kulli, T_matrix)
                    e12_olasilik = n10_sozluk.forward(e11_gomulu)
                    vram_denetci.yokla_ve_raporla("N8_N10_SpektralSoftmax", adim_no=current_step)
                    logger.debug(f"[N8-N10 Spektral Softmax] N_star: {N_star} | Arc Length: {L_arc_val:.4f}")
                    
                    e12_olasilik_cevapsiz = n10_sozluk.forward(n9_vandermonde.forward(n8_chebyshev.forward(E9_GuncellenmisGizilDurum(x_next=x_start_grouped)), T_matrix))
                    hedef_clamped = torch.clamp(hedef_grouped[:, :N_star], min=0, max=getattr(config, 'V_size', 32000) - 1)
                    p_target_cevapsiz = e12_olasilik_cevapsiz.P.gather(1, hedef_clamped.unsqueeze(1)).squeeze(1)
                    p_target_cevapli = e12_olasilik.P.gather(1, hedef_clamped.unsqueeze(1)).squeeze(1)
                    kayip_cevapsiz = -torch.log(p_target_cevapsiz + 1e-9).mean(dim=-1)
                    kayip_cevapli = -torch.log(p_target_cevapli + 1e-9).mean(dim=-1)

                    son_q = sorgu_q_list[-1]
                    son_a = cevap_a_list[-1]
                    R_q, metrikler_q = odul_motoru.hesapla_aktif_sorgu_odulu(
                        q_r=son_q,
                        a_r=son_a,
                        x_context=x_start_grouped,
                        kayip_cevapsiz=kayip_cevapsiz,
                        kayip_cevapli=kayip_cevapli,
                        Delta_0=Delta_0_op
                    )

                    oduller_base = odul_motoru.hesapla(e12_olasilik.P, hedef_grouped[:, :N_star])
                    toplam_oduller = oduller_base + R_q
                    kayip_grpo_vec = grpo_kriteri.hesapla_vektor(e12_olasilik.P, hedef_grouped[:, :N_star], toplam_oduller)
                    n_target = float(hedef_grouped.shape[1])
                    kayip_length = (L_arc_tensor - 0.5 * N_ste_tensor)**2 + 0.05 * (N_ste_tensor - n_target)**2
                    kayip_spektral_vec = (kayip_length + 0.01 * torch.abs(delta_n_tensor).mean()).unsqueeze(0)
                    
                    (l_var_vec, l_cov_vec, l_rec_vec), metrikler_vicreg = vicreg_kriteri(x=e9_guncel_detached.x_next, z=e11_gomulu.X_output)
                    
                    # Doğrudan Parametre Cerrahisi: theta_3 (Sorgu Seçici Stiefel Matrisi - 6 Vektörel Şart), theta_5 (Chebyshev spektral) ve theta_6 (Sözlük kafası)
                    if "E_sorgu_node_matrix" in metrikler_q:
                        vjp_cerrahi_enjekte_et(metrikler_q["E_sorgu_node_matrix"], list(n4_sorgu.parameters()))
                    vjp_cerrahi_enjekte_et(kayip_grpo_vec, list(n10_sozluk.parameters()))
                    vjp_cerrahi_enjekte_et(kayip_spektral_vec, list(n8_chebyshev.parameters()) + list(n8_b_uzunluk.parameters()))
                    vjp_cerrahi_enjekte_et(l_var_vec, list(n10_sozluk.parameters()))
                    vjp_cerrahi_enjekte_et(l_cov_vec, list(n10_sozluk.parameters()))
                    vjp_cerrahi_enjekte_et(l_rec_vec, list(n10_sozluk.parameters()))

                    g_faz4_5 = [p.grad.detach().clone() if p.grad is not None else torch.zeros_like(p) for p in trainable_params]
                    vram_denetci.yokla_ve_raporla("LOCO_Faz4_5_GrafSilindi", adim_no=current_step)
                    logger.info(f"  [LOCO Faz 4-5] GRPO Spektral & VICReg VJP Cerrahisi Tamamlandı | VICReg(var={metrikler_vicreg['l_var']:.4f}, cov={metrikler_vicreg['l_cov']:.4f}, rec={metrikler_vicreg['l_rec']:.4f})")

                    # ------------------------------------------------------------------------------
                    # PARETO-PCGRAD DİKGEN PROJEKSİYONU VE NİHAİ KÜRESEL GÜNCELLEME
                    # ------------------------------------------------------------------------------
                    alpha_pareto = pareto_pcgrad_operator.birlestir_ve_uygula_dagitik_gradyanlar(
                        shard_gradyanlari=[g_faz2, g_faz3, g_faz4_5],
                        trainable_params=trainable_params,
                        optimizer=optimizer,
                        max_norm=1.0
                    )

                    # [GRAD_REPORT GERİBESLEME ORGANİ] Dinamik Adapte Edilebilir Öğrenme Hızı Kontrolü (eta_t = eta_0 / (1 + gamma * ||g_pareto||_2))
                    grad_norm_pareto = math.sqrt(sum((p.grad.norm().item() ** 2 for p in trainable_params if p.grad is not None)))
                    adapted_lr = config.lr / (1.0 + 0.01 * grad_norm_pareto)
                    for param_group in optimizer.param_groups:
                        param_group['lr'] = adapted_lr

                    vram_denetci.yokla_ve_raporla("LOCO_Pareto_PCGrad_StepCompleted", adim_no=current_step)
                    logger.info(f"  [Pareto-PCGrad] Dikgen Projeksiyonlu Optimizasyon Adımı Tamamlandı | alpha*: {alpha_pareto} | grad_norm: {grad_norm_pareto:.4f} | adapted_lr: {adapted_lr:.6e}")
                    
                    if hasattr(meclis_bellek, 'detach_memory'):
                        meclis_bellek.detach_memory()
                    
                    kayip = (d_vec2.mean() + e_vec2.mean() + d_vec3.mean() + e_vec3.mean() + kayip_grpo_vec.mean() + metrikler_vicreg['vicreg_total']).detach()
                    
                    raw_n3_lif = gpu_dagitici.kok_modul_al(n3_lif)
                    stiefel_izdusurucu.izdüsür(raw_n3_lif.phi_matrisleri)
                    
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        
                    # Lif Laplasyeni Küresel Kesit (Global Section) Uyumsuzluğu ve Dirichlet Enerjisi Hesabı [sistem_tarif.md:L504-L599]
                    d_discrepancy = n7_cozucu.hesapla_uyumsuzluk(mevcut_durum.x_r, D0_op)
                    dirichlet_energy = n7_cozucu.hesapla_dirichlet_enerjisi(mevcut_durum.x_r, Delta_0_op)

                    current_step += 1
                    curr_loss_val = kayip.detach().item()
                    loss_history.append(curr_loss_val)
                    gecen_sure = time.time() - epoch_baslangic

                    # Küresel İşlenen Bayt Hesabı ve 500 MB Log Throttling (Log Şişmesini Kökten Önleme)
                    chunk_byte_len = len(e1_girdi_metni.encode('utf-8', errors='ignore'))
                    global_bytes_processed += chunk_byte_len

                    curr_500mb_chunk = global_bytes_processed // (500 * 1024 * 1024)
                    mb_500_crossed = (curr_500mb_chunk > last_logged_500mb_chunk)
                    should_log = mb_500_crossed or (current_step == 1)

                    if should_log or (curr_loss_val < best_loss):
                        mb_processed = global_bytes_processed / (1024 * 1024)
                        logger.info(f"Adım [{current_step}] | Toplam İşlenen Veri: {mb_processed:.1f} MB | Dosya: {os.path.basename(dosya_yolu)} | GRPO Kayıp: {curr_loss_val:.6f} | L_arc: {L_arc_val:.4f} | E(x): {dirichlet_energy:.6f} | Uyumsuzluk: {d_discrepancy:.6f} | Süre: {gecen_sure:.3f} sn")
                        if mb_500_crossed:
                            last_logged_500mb_chunk = curr_500mb_chunk
                    else:
                        logger.debug(f"Adım [{current_step}] | İşlenen Veri: {global_bytes_processed:,} B | Uyumsuzluk: {d_discrepancy:.6f}")

                    # Periyodik ve En İyi Kayıp (Best Loss) Ağır Model Ağırlıkları Kaydı
                    is_periodic = (current_step % SAVE_EVERY_N_STEPS == 0)
                    is_best = False
                    if curr_loss_val < best_loss:
                        best_loss = curr_loss_val
                        is_best = True

                    if is_periodic or is_best:
                        npz_mgr.save_pytorch_model(
                            step=current_step,
                            token_offset=current_step * config.N,
                            model=tum_moduller,
                            optimizer=optimizer,
                            loss_history=loss_history,
                            is_best=is_best
                        )

                    # Dosyayı SADECE son parçaya ulaşıldığında (dosya bitince) 'tamamlandı' olarak işaretle
                    if is_last_chunk:
                        npz_mgr.hafiza.dosya_tamamlandi(
                            dosya_yolu=dosya_yolu,
                            klasor_yolu=klasor_yolu,
                            veriseti_adi=veriseti_adi,
                            tum_klasor_dosyalari=tum_klasor_dosyalari,
                            tum_veriseti_klasorleri=tum_veriseti_klasorleri
                        )
                        npz_mgr.save_hafiza_state()

                    # ==============================================================================
                    # HER ADIMIN SONUNDA ÇALIŞACAK HAKİKİ VRAM SÜPÜRME VE TEMİZLİK PROTOKOLÜ
                    # ==============================================================================
                    optimizer.zero_grad(set_to_none=True)
                    targets_to_delete = [
                        k for k in list(locals().keys())
                        if k.startswith(('e1_', 'e2_', 'e3_', 'e4_', 'e5_', 'e6_', 'e7_', 'e8_', 'e9_', 'e10_', 'e11_', 'e12_'))
                        or k.endswith(('_vec', '_vec2', '_vec3', '_loss', '_r', '_op', '_tensor', '_grouped', '_val', '_matrix', '_pareto', '_graf'))
                        or k in ('kayip', 'alpha_pareto', 'mevcut_durum', 'sorgu_q_list', 'cevap_a_list', 'toplam_oduller', 'oduller_base', 'R_q', 'metrikler_q')
                    ]
                    locs = locals()
                    for var_name in targets_to_delete:
                        if var_name in locs:
                            try:
                                del locs[var_name]
                            except Exception:
                                pass

                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

    # Eğitim Tamamlandığında Son Sabit Kayıt
    npz_mgr.save_pytorch_model(
        step=current_step,
        token_offset=current_step * config.N,
        model=tum_moduller,
        optimizer=optimizer,
        loss_history=loss_history,
        is_best=False
    )

    logger.info("================================================================================")
    logger.info("EĞİTİM DÖNGÜSÜ VE TÜM VERİ KÜMELERİ BAŞARIYLA TAMAMLANDI")
    logger.info("================================================================================")


if __name__ == "__main__":
    Main_EgitimYurutucu()











    