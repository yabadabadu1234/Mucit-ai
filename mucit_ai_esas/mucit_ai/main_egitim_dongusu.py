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
try:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CURRENT_DIR = os.path.abspath(os.getcwd())

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
import contextlib
from typing import Dict, Any, List, Tuple, Optional, Union

from kulli_gpu import CpuAnaIdareci, NvmeTakasYoneticisi
from mucit_ai.topolojik_islem_sevk import TopolojikIslemSevk

import kontratlar
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.checkpoint import checkpoint

from kontratlar import (
    AnlasmaliVramGuvencesiAl,
    vram_on_kontrol_ve_nvme_tahliye,
    AcilDurumOomYakalayiciVeKurtarici,
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
    """GRPO Topolojik Tutarlılık ve Doğruluk Skorlama Motoru (2D/3D Uyumlu)"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def hesapla(self, P: torch.Tensor, hedefler: torch.Tensor) -> torch.Tensor:
        if P.dim() == 2:
            B, N = P.shape
            is_correct = (P > 0.1).float().mean(dim=-1)
            topolojik_invaryant = 1.0 - torch.std(P, dim=-1)
        else:
            B, V_size, N = P.shape
            preds = torch.argmax(P, dim=1)
            min_len = min(N, hedefler.shape[1])
            is_correct = (preds[:, :min_len] == hedefler[:, :min_len]).float().mean(dim=-1)
            topolojik_invaryant = 1.0 - torch.std(P, dim=(1, 2))

        oduller = is_correct * 2.0 + topolojik_invaryant * 0.5
        return oduller


class Kayip_GRPO_Kriteri:
    """GRPO (Group Relative Policy Optimization) Kayıp Fonksiyonu (Çifte Logaritma Önlemeli & 2D/3D Uyumlu)"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def hesapla_vektor(self, P: torch.Tensor, hedefler: torch.Tensor, oduller: torch.Tensor) -> torch.Tensor:
        if P.dim() == 2:
            p_target = P
            nll = -torch.log(torch.clamp(p_target, min=1e-9, max=1.0)).mean(dim=-1)
        else:
            B, V_size, N = P.shape
            targets = hedefler[:, :N]
            p_target = P.gather(1, targets.unsqueeze(1)).squeeze(1)
            nll = -torch.log(torch.clamp(p_target, min=1e-9, max=1.0)).mean(dim=-1)

        std = oduller.std() if oduller.std() > 0 else 1e-8
        avantajlar = (oduller - oduller.mean()) / (std + 1e-8)
        kayip_vec = nll * avantajlar.detach()
        return kayip_vec

    def hesapla(self, P: torch.Tensor, hedefler: torch.Tensor, oduller: torch.Tensor) -> torch.Tensor:
        return self.hesapla_vektor(P, hedefler, oduller).mean()


class Odul_ButunculCumleKeyfiyetMotoru:
    """
    [Bütüncül Cümle Keyfiyet Motoru]

    Kelime-bazlı (token-level) kemmiyet kontrolünün (N14_OdulTopolojikDevresmezlikMotoru'nun
    P > 0.1 sezgiselinin) yanına, cümlenin bütününde organlar-arası mutabakatı ölçen
    ÇARPIMSAL (AND mantıklı — tek organ ahenksizse skor çöker) bir keyfiyet sinyali ekler.
    GRPO'ya 11. adlandırılmış Pareto-PCGrad-MGDA nesnesi olarak girer; mevcut GRPO/VICReg
    sinyallerinin YERİNE geçmez, onlarla çakışma-farkında birleştirilir.

    3 Organik Rükün:
      1. Sorgu-Cevap Ahengi (N4-N5): q_son ile a_son arasındaki kosinüs benzerliği.
      2. Eşsınır Kararlılığı (N4-N6/N7 üzerinden D0): c_defect = x @ D0^T normunun sönümü.
      3. Spektral Eğri / Cümle Kapasitesi Uyumu (N8-N9): L_arc/N_ste'nin hedef cümle
         uzunluğuyla örtüşmesi.

    Graf-Canlılık Notu: q_son ve L_arc/N_ste, çağıran tarafta HER SEFERİNDE TAZE
    (ayrı, bağımsız) forward çağrılarıyla üretilmelidir — mevcut R-döngüsü/Faz 4-5
    tensörlerinin (sorgu_q_list[-1], L_arc_tensor, N_ste_tensor) grafı önceki
    VJP'ler tarafından retain_graph=False ile zaten tüketilmiştir; onları ikinci
    kez canlı kullanmaya çalışmak "Trying to backward through the graph a second
    time" hatası doğurur (bkz. main döngüsündeki "HATA 1 DÜZELTMESİ" bloğu ve onun
    hemen ardındaki taze n4_sorgu/n8_b_uzunluk çağrıları). x_son ve a_son ise
    ÇAĞIRAN TARAF tarafından bilerek .detach() edilmiş olmalıdır. Bu motor kendi
    içinde HİÇBİR .detach() çağırmaz — sorumluluk çağırana aittir.
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def hesapla_vektor(
        self,
        q_son: torch.Tensor,        # [B, d_q] — CANLI (N4 parametrelerine gradyan taşır)
        a_son: torch.Tensor,        # [B, d_a] — detached (çağıran tarafça)
        x_son: torch.Tensor,        # [B, D]   — detached (çağıran tarafça)
        D0_op: torch.Tensor,        # [E*d_e, D]
        hedef_tokens: torch.Tensor, # [B, N*] (yalnızca hedef uzunluk için)
        L_arc: torch.Tensor,        # skaler veya [B] — CANLI (N8_B parametrelerine gradyan taşır)
        N_ste: torch.Tensor,        # skaler veya [B] — CANLI (N8_B parametrelerine gradyan taşır)
    ) -> torch.Tensor:
        # 1. SORGU-CEVAP AHENGİ: farklı boyutlu olabilirler (d_q != d_a), ortak boyuta kırp
        d_min = min(q_son.shape[-1], a_son.shape[-1])
        qa_ahenk = F.cosine_similarity(q_son[..., :d_min], a_son[..., :d_min], dim=-1)  # [B]

        # 2. EŞSINIR KARARLILIĞI: N4'ün ZATEN kullandığı AYNI formül (c_defect = x @ D0^T),
        # boyutsal olarak tutarlı ve anlamlı — q_son yerine x_son (D0 ile aynı D uzayında).
        c_defect_cumle = torch.matmul(x_son, D0_op.T)  # [B, E*d_e]
        c_kusur_norm = torch.norm(c_defect_cumle, p=2, dim=-1)  # [B]
        # Boyut-bağımsız sönüm: normu E*d_e'nin karekökü ile ölçekle (büyük D0'larda
        # norm doğal olarak büyür, ham norm sabit eşikle karşılaştırılamaz).
        olcek = max(1.0, float(D0_op.shape[0]) ** 0.5)
        topolojik_keyfiyet = torch.exp(-c_kusur_norm / olcek)  # [B], kusursuzsa -> 1.0

        # 3. SPEKTRAL EĞRİ / CÜMLE KAPASİTESİ UYUMU
        N_hedef = float(hedef_tokens.shape[1])
        kapasite_uyumu = torch.exp(-0.05 * torch.abs(N_ste - N_hedef))
        if kapasite_uyumu.dim() == 0:
            kapasite_uyumu = kapasite_uyumu.expand_as(qa_ahenk)

        # 4. ÇARPIMSAL (AND) MÜHÜRLEME: kemmiyetin toplama mantığı değil, keyfiyetin
        # çarpım mantığı — tek bir organ ahenksizse bütün skor çöker.
        cumle_keyfiyet_skoru = qa_ahenk * topolojik_keyfiyet * kapasite_uyumu  # [B]

        # GRPO tarzı grup-içi normalize edilmiş kayıp vektörü: keyfiyet yüksekse kayıp düşük.
        kayip_vec = 1.0 - cumle_keyfiyet_skoru
        return kayip_vec


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



def _tekil_egitim_adimi_icra(
    e1_girdi_metni: str,
    hedef_tensor: torch.Tensor,
    tum_moduller: Dict[str, Any],
    config: Any,
    optimizer: torch.optim.Optimizer,
    trainable_params: List[nn.Parameter],
    current_step: int,
    vram_denetci: Any,
    laplasyen_insa: Any,
    cheby_calc: Any,
    odul_motoru: Any,
    grpo_kriteri: Any,
    cumle_keyfiyet_motoru: Any,
    vicreg_kriteri: Any,
    pareto_pcgrad_operator: Any,
    stiefel_izdusurucu: Any,
    gpu_dagitici: Optional[Any] = None,
    gpu_cesitlendirici: Optional[Any] = None,
    takas_mgr: Optional[Any] = None
) -> Tuple[float, float, float, float]:
    """
    Tüm eğitim adımı bu müstakil iç fonksiyonun içinde icra edilir. Fonksiyon bittiği an (return)
    CPython tüm geçici tensörleri Stack Frame'den fiziken yok eder ve VRAM 178 MB seviyesine düşer!
    """
    optimizer.zero_grad(set_to_none=True)

    # NVMe Takas Yöneticisi: sağlanmışsa, bu adımın tüm forward/backward'ı boyunca
    # autograd'ın kaydedilen aktivasyon tensörlerini otomatik NVMe-tahliye kancalarıyla sarmalar.
    # AnlasmaliVramGuvencesiAl'daki gc.collect()/empty_cache() zaten-boşta-duran belleği temizler;
    # asıl "sıfır OOM" güvencesi canlı tensörleri diske süren bu kapsam muhafızından gelir.
    _takas_cm = takas_mgr.kapsam_muhafizi_aktifles() if takas_mgr is not None else None
    if _takas_cm is not None:
        _takas_cm.__enter__()

    n1_byte = tum_moduller['n1_byte']
    n2_topox = tum_moduller['n2_topox']
    n3_lif = tum_moduller['n3_phi']
    n4_sorgu = tum_moduller['n4']
    n5_cevap = tum_moduller['n5']
    n6_aktor = tum_moduller['n6_aktor']
    n7_cozucu = tum_moduller['n7']
    n8_chebyshev = tum_moduller['n8']
    n8_b_uzunluk = tum_moduller['n8_b']
    n9_vandermonde = tum_moduller['n9_vandermonde']
    n10_sozluk = tum_moduller['n10']
    meclis_bellek = tum_moduller['bellek']
    bellek_yazici = tum_moduller['bellek_yazici']

    max_chunk_len = getattr(config, 'N', 1024)
    e1_girdi_metni_chunk = e1_girdi_metni[:max_chunk_len] if len(e1_girdi_metni) > max_chunk_len else e1_girdi_metni
    e1_girdi = E1_HamMetinAkisi(X_text=e1_girdi_metni_chunk)

    def vjp_cerrahi_enjekte_et(vector_loss: torch.Tensor, target_params: List[nn.Parameter], scale: float = 1.0, retain_graph: bool = False) -> None:
        """
        [Faz-İzoleli VJP Cerrahi Gradyan İzolasyonu]

        Vektör hata sahasının (vector_loss) ilgili parametre alt-manifolduna (target_params)
        VJP (Vector-Jacobian Product) tensör kontraksiyonu ile doğrudan gradyan enjeksiyonu yapar.
        Skaler .backward() veya .mean() kullanılmaz! Autograd grafiği anında serbest bırakılır.

        RuntimeError Güvencesi:
          Adım 1'de hata_vektoru.detach() ile faz sınırı açıkça koparılır.
          Böylece Faz 4-5 kayıpları Faz 2-3'ün silinmiş grafini aramamaya çalışmaz.
          retain_graph=False (varsayılan) ile graf anında serbest bırakılarak VRAM
          birikmesi engellenir.

        KARDEŞ-VJP UYARISI (retain_graph parametresi): d_vec2/e_vec2 (Faz 2) ve
        d_vec3/e_vec3 (Faz 3) gibi İKİZ nesne çiftleri AYNI üst-grafı (ör. x_initial
        veya mevcut_durum.x_r, D0_op/Delta_0_op) paylaşır. Çiftin İLK çağrısı
        retain_graph=False (varsayılan) ile backward yaparsa, o paylaşılan üst-grafı
        ANINDA siler — çiftin İKİNCİ çağrısı aynı paylaşılan düğümlere tekrar
        erişmeye çalışınca "Trying to backward through the graph a second time"
        hatası fırlatır (bu fonksiyon bunu yutup sessizce logluyor — yani gradyan
        SESSİZCE kaybolur, çökme olmaz ama öğrenme de olmaz). Çözüm: bir kardeş
        grubundaki İLK çağrı retain_graph=True ile yapılır (paylaşılan üst-grafı
        canlı tutar), grubun SON çağrısı varsayılan retain_graph=False ile yapılır
        (artık kimse ihtiyaç duymadığı için gerçekten serbest bırakır).

        Gradyan İzolasyon Aksiyomu:
          Her faz kendi .grad'ını sıfırdan yazar (p.grad = g_clean).
          Faz geçişlerinde önceki fazın artık gradyanı birikmez.
          Faz gradyanlarının çakıştırılması görevi tamamen PCGrad operatörüne devredilmiştir.
        """
        trainable_in_group = [p for p in target_params if p.requires_grad]
        if not trainable_in_group:
            return

        # ADIM 1: FAZ SINIRI KOPARMA AKSİYOMU (Explicit State Detachment)
        # vector_loss'u türev grafiğinden tamamen kopar → "silinmiş graf" RuntimeError imkânsız
        temiz_hata = vector_loss.detach()
        temiz_hata = torch.nan_to_num(temiz_hata, nan=0.0, posinf=100.0, neginf=-100.0)
        temiz_hata = torch.clamp(temiz_hata, min=-100.0, max=100.0)

        # ADIM 2: EMNİYETLİ VEKTÖR NORMALİZASYONU (Sayısal Kararlılık)
        # torch.std() VARSAYILAN OLARAK unbiased=True'dur (n-1'e böler). temiz_hata
        # tek elemanlıysa (numel=1, ör. tek-objektifli bir faz) n-1=0 olur ve std_val
        # NaN döner (+ 1e-6 bunu DÜZELTMEZ, NaN kalır) — bu NaN sessizce v_probe'a ve
        # oradan enjekte edilen gradyana bulaşır. unbiased=False (n'e bölen popülasyon
        # std'si) numel>=1 için her zaman tanımlıdır ve bu dejenere durumu ortadan
        # kaldırır.
        std_val  = torch.std(temiz_hata, unbiased=False) + 1e-6
        norm_val = torch.norm(temiz_hata) + 1e-6
        v_probe  = scale * (1.0 / std_val) * (temiz_hata / norm_val)

        # ADIM 3: PARAMETRE TAMPONLARINI TEMİZLE (Kanonik Gradyan Hijyeni)
        # KAPSAMLI DENETİM DÜZELTMESİ: ÖNCEDEN yalnızca `trainable_in_group` (bu ÇAĞRININ
        # hedeflediği parametreler) temizleniyordu. Ama _grad_anlik_kopyala() HER çağrıdan
        # sonra TÜM trainable_params üzerinden anlık görüntü alıyor (bkz. o fonksiyonun
        # docstring'i) ve hedeflenmeyen bir parametrenin .grad'ı None DEĞİLSE (yani ÖNCEKİ
        # bir adlandırılmış-nesne VJP çağrısı onu ayarlamışsa) o ESKİ/İLGİSİZ değeri
        # kopyalıyordu — "Her faz kendi .grad'ını sıfırdan yazar, önceki fazın artık
        # gradyanı birikmez" aksiyomu (bkz. yukarıdaki docstring) yalnızca HEDEFLENEN
        # parametreler için doğruydu, hedeflenmeyenler için SESSİZCE İHLAL EDİLİYORDU.
        # Sonuç: bir nesnenin (ör. g_spektral) o parametreye GERÇEKTE hiç katkısı yokken,
        # o pozisyonda başka bir nesnenin (ör. g_grpo) gradyanı sızıp Pareto-PCGrad'ın
        # "her nesne kendi ayrı satırı" granülerlik varsayımını kirletiyordu. Artık TÜM
        # trainable_params temizleniyor — hedeflenmeyen parametreler bu çağrı için
        # doğru şekilde gerçek sıfır (_grad_anlik_kopyala'nın torch.zeros_like düşüşü)
        # olarak raporlanıyor.
        for p in trainable_params:
            p.grad = None

        # ADIM 4: TEK-SÜRÜM VJP TÜREV ÇAĞRISI (retain_graph=False)
        # outputs = temiz_hata: detach edilmiş kopya → graf tekrar-türev hatası imkânsız
        # retain_graph=False   → graf anında silinir, VRAM boşalır
        # allow_unused=True    → kullanılmayan parametreler None döner, hata vermez
        try:
            grads = torch.autograd.grad(
                outputs=vector_loss,        # orijinal tensör (canlı grad_fn üzerinden VJP)
                inputs=trainable_in_group,
                grad_outputs=v_probe,       # v_probe zaten detach edilmiş
                retain_graph=retain_graph,
                allow_unused=True
            )
            # Gradyanları parametrelere mühürle (faz izolasyonu: sıfırdan yaz, biriktirme)
            for p, g in zip(trainable_in_group, grads):
                if g is not None:
                    g_clean = torch.nan_to_num(g.detach(), nan=0.0, posinf=1.0, neginf=-1.0)
                    g_norm  = torch.norm(g_clean)
                    if g_norm > 1.0:
                        g_clean = g_clean / (g_norm + 1e-8)
                    # İzolasyon aksiyomu: mevcut grad'ı koru değil, üzerine yaz
                    p.grad = g_clean
        except Exception as exc:
            logger.warning(f"  [VJP Cerrahi Uyarısı] Gradyan enjeksiyonu uyarısı: {exc}")

    def _grad_anlik_kopyala() -> List[torch.Tensor]:
        """
        [Nesne-Seviyesi PCGrad/MGDA Granülaritesi]
        vjp_cerrahi_enjekte_et'ten hemen sonra çağrılır; o TEK adlandırılmış hata
        nesnesinin (d_vec2, relu(e_vec2), kayip_grpo_vec, l_var_vec, ... gibi farklı
        fiziksel büyüklüklerin ASLA aynı VJP'de birleştirilmeden) ürettiği anlık gradyan
        anlık görüntüsünü döndürür. Bu şekilde her nesne, dış Pareto-PCGrad-MGDA
        birleştiricisine (birlestir_ve_uygula_dagitik_gradyanlar) kendi ayrı satırı
        olarak girer — M~binlerce elemanlı tam Jacobiyen'in hesaplanamaz maliyetiyle,
        3 kaba fazda her şeyi tek VJP'de eritmenin çatışma-körlüğü arasındaki orta yol.
        """
        return [p.grad.detach().clone() if p.grad is not None else torch.zeros_like(p) for p in trainable_params]

    # ------------------------------------------------------------------------------
    # FAZ 2: TOPOLOJİK İSKELET VE LİF LAPLASYENİ HESABI (N1 -> N2 -> N3 -> N11)
    # ------------------------------------------------------------------------------
    AnlasmaliVramGuvencesiAl(n1_byte, e1_girdi, takas_mgr=takas_mgr)
    e2_byte, x_initial = AcilDurumOomYakalayiciVeKurtarici(n1_byte.forward, e1_girdi, modul_nesnesi=n1_byte, takas_mgr=takas_mgr)
    raw_n2_topox = gpu_dagitici.kok_modul_al(n2_topox) if gpu_dagitici is not None else (n2_topox.module if hasattr(n2_topox, 'module') else n2_topox)
    AnlasmaliVramGuvencesiAl(raw_n2_topox, e2_byte, takas_mgr=takas_mgr)
    e3_sinir = AcilDurumOomYakalayiciVeKurtarici(raw_n2_topox.forward, e2_byte, x_initial=x_initial, mode='train', modul_nesnesi=raw_n2_topox, takas_mgr=takas_mgr)
    AnlasmaliVramGuvencesiAl(n3_lif, e3_sinir, takas_mgr=takas_mgr)
    e4_lif = AcilDurumOomYakalayiciVeKurtarici(n3_lif.forward, e3_sinir, x_initial, modul_nesnesi=n3_lif, takas_mgr=takas_mgr)
    vram_denetci.yokla_ve_raporla("N1_N3_TopolojiIskelesi", adim_no=current_step)
    
    AnlasmaliVramGuvencesiAl(laplasyen_insa, e3_sinir.D1, takas_mgr=takas_mgr)
    # NOT (matrissiz Laplasyen): insa_et artık VARSAYILAN OLARAK [D,D] boyutunda yoğun
    # Delta_0'ı KURMUYOR (hesapla_yogun_delta0=False) — bu tek matris VRAM baskısının
    # başlıca kaynağıydı. Delta_0'a ihtiyaç duyan tüm tüketiciler (n7_cozucu) artık D0
    # üzerinden laplasyen_ile_carp ile matematiksel olarak BİREBİR eşdeğer, matrissiz
    # çalışıyor.
    # KAPSAMLI DENETİM DÜZELTMESİ: AnlasmaliVramGuvencesiAl yalnızca PROAKTİF bir tahmindir
    # (tahmin_et_vram_bayt formülüne dayanır) — bu tahmin tutmazsa (ör. F.pad/torch.cat'in
    # transient tepe belleği, VRAM parçalanması) GERÇEK bir OOM hâlâ patlayabilir. Bu tek
    # çağrı (D0'ı bizzat inşa eden, en büyük tekil tensörü üreten düğüm) diğer TÜM N1-N10
    # çağrılarının aksine hiçbir REAKTİF (AcilDurumOomYakalayiciVeKurtarici) yakalayıcısından
    # geçmiyordu — tam da bu yüzden bir önceki turda çıplak OOM ile çöktü.
    D0_op, _ = AcilDurumOomYakalayiciVeKurtarici(
        laplasyen_insa.insa_et, e3_sinir, e4_lif.phi_matrisleri,
        modul_nesnesi=laplasyen_insa, takas_mgr=takas_mgr
    )
    vram_denetci.yokla_ve_raporla("N11_LifLaplasyeniInsa", adim_no=current_step)

    # D0_op, AnlasmaliVramGuvencesiAl'ın laplasyen_insa için verdiği CPU kararına göre
    # CPU'da gelebilirken x_initial hâlâ GPU'da olabilir — çıplak çağrı "Expected all
    # tensors to be on the same device" ile çökerdi (bkz. n9/n10 vb. aynı desen).
    d_vec2 = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.hesapla_uyumsuzluk_vektoru, x_initial, D0_op,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )
    e_vec2 = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.hesapla_dirichlet_enerjisi_vektoru, x_initial, D0_op,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )

    # Kohomolojik uyumsuzluk (d_vec2) ve Dirichlet enerjisi (e_vec2) FİZİKSEL OLARAK
    # farklı büyüklüklerdir — tek bir torch.cat + tek VJP'de eritilmezler, her biri
    # kendi VJP'sini alır ve dış Pareto-PCGrad-MGDA birleştiricisine ayrı satır olarak girer.
    _faz2_hedef_params = list(n3_lif.parameters()) + list(n2_topox.parameters())
    # KARDEŞ-VJP: d_vec2 ve e_vec2 AYNI üst-grafı (x_initial, D0_op/Delta_0_op → N1/N2/N3)
    # paylaşır. İlk çağrı retain_graph=True ile bu paylaşılan grafı canlı tutar; son çağrı
    # varsayılan retain_graph=False ile gerçekten serbest bırakır (bkz. vjp_cerrahi_enjekte_et
    # docstring'indeki "KARDEŞ-VJP UYARISI").
    vjp_cerrahi_enjekte_et(d_vec2, _faz2_hedef_params, retain_graph=True)
    g_faz2_uyumsuzluk = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(F.relu(e_vec2), _faz2_hedef_params)
    g_faz2_dirichlet = _grad_anlik_kopyala()

    # BELLEK TUTMA (RETENTION) DÜZELTMESİ: D0_op (Faz2'nin Laplasyen'i, ~birkaç GB) bu
    # noktadan sonra BİR DAHA HİÇ KULLANILMIYOR (Faz3 kendi D0_op_sabit'ini kurar), ama
    # Python yerel değişken olarak fonksiyon sonuna kadar (Faz3/4/5, Pareto-PCGrad dahil)
    # canlı tutuyordu — tam da VRAM baskısının en yüksek olduğu anda gereksiz yer
    # kaplıyordu. NOT: d_vec2/e_vec2 SİLİNMEDİ — fonksiyonun sonunda
    # (_kayip_bileseni_listesi, satır ~1074) hâlâ okunuyorlar; VJP'leri tüketilmiş
    # olsa da .mean() ile tekrar erişilen SKALER değerler için tensörlerin kendisi
    # (küçük, [V] boyutunda) hâlâ gerekli — yalnızca D0_op ([E*d_e, D], gerçek
    # büyük tüketici) siliniyor.
    del D0_op
    import gc as _gc
    _gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    vram_denetci.yokla_ve_raporla("LOCO_Faz2_GrafSilindi", adim_no=current_step)

    # ------------------------------------------------------------------------------
    # FAZ 3: R-ADIMLI REKÜRENS DÖNGÜSÜ VE H^1 KOHOMOLOJİK AKIL YÜRÜTME (N4 -> N5 -> N6 -> N7)
    # ------------------------------------------------------------------------------
    GRPO_G = getattr(config, 'GRPO_G', 4)
    x_start_grouped = x_initial.repeat_interleave(GRPO_G, dim=0).detach()
    if gpu_cesitlendirici is not None:
        x_start_grouped = gpu_cesitlendirici.cesitlendir(x_start_grouped, step_seed=current_step)
    elif GRPO_G > 1:
        # FASİL 1 DÜZELTMESİ: Öklid gürültüsü Stiefel dikgenliğini bozduğu için
        # Teğet Uzayı Jeodezik Cayley çeşitlendirmesi uygulanır.
        # x_g = x_0 · Cayley(ε·A_g), A_g ∈ so(D) antisimetrik → x_g^T x_g = I garantili.
        _noise_std = 0.01
        _D = x_start_grouped.shape[-1]
        # DİĞER TÜM N1-N11 DÜĞÜMLERİNDEN FARKLI OLARAK bu blok herhangi bir
        # tahmin_et_vram_bayt() beyan eden modüle bağlı değildi ve hiç
        # AnlasmaliVramGuvencesiAl/NVMe-tahliye kontratı yapmadan doğrudan BEŞ ayrı
        # [D, D] tensör (_M_g, _A_g, _I_D, _left, _right) tahsis ediyordu — bu da
        # tam olarak Laplasyen'in D×D boyutu kadar VRAM ister ama VRAM zaten
        # kritik doluyken hiç kontrol edilmeden çöküyordu (OOM). Diğer düğümlerle
        # aynı ön-icra kontratını burada da açıkça uyguluyoruz.
        _cayley_gerekli_bayt = 5 * _D * _D * x_start_grouped.element_size()
        vram_on_kontrol_ve_nvme_tahliye(_cayley_gerekli_bayt, takas_mgr=takas_mgr)
        try:
            _M_g = torch.randn(_D, _D, device=x_start_grouped.device, dtype=x_start_grouped.dtype)
            _A_g = 0.5 * (_M_g - _M_g.T)  # Antisimetrik Lie cebiri üreteci ∈ so(D)
            _I_D = torch.eye(_D, device=x_start_grouped.device, dtype=x_start_grouped.dtype)
            _left  = _I_D - (_noise_std / 2.0) * _A_g
            _right = _I_D + (_noise_std / 2.0) * _A_g
            _cayley = torch.linalg.solve(_left, _right)  # Cayley(ε A_g) ∈ O(D)
        except Exception as _cayley_exc:
            # Tahsislerin KENDİSİ de (torch.linalg.solve değil, _M_g/_I_D/_left/_right
            # tahsisleri de) OOM atabilir — güvenli kimlik-matris fallback'i tüm
            # bloğu kapsayacak şekilde genişletildi (önceden sadece solve() sarılıydı).
            logger.warning(f"[Faz3_CayleyCesitlendirme] Tahsis/çözüm başarısız, kimlik fallback: {_cayley_exc}")
            _cayley = torch.eye(_D, device=x_start_grouped.device, dtype=x_start_grouped.dtype)
        x_start_grouped = torch.matmul(x_start_grouped, _cayley)

    x_current = x_start_grouped.clone().detach()
    e2_byte_grouped = E2_ByteTensoru(byte_tensor=e2_byte.byte_tensor.repeat_interleave(GRPO_G, dim=0))
    hedef_grouped = hedef_tensor.repeat_interleave(GRPO_G, dim=0)
    active_b = x_current.shape[0]
    # KAPSAMLI DENETİM (madde 5): meclis_bellek dosyanın geri kalanında (ör. write/yaz
    # çağrılarında) her zaman AnlasmaliVramGuvencesiAl + AcilDurumOomYakalayiciVeKurtarici
    # ile korunurken bu ilk get_memory çağrısı hiç korumasızdı — VRAM baskısı altında
    # çıplak OOM ile tüm adımı çökertebilirdi.
    AnlasmaliVramGuvencesiAl(meclis_bellek, active_b, takas_mgr=takas_mgr)
    M_current = AcilDurumOomYakalayiciVeKurtarici(
        meclis_bellek.get_memory, active_b, modul_nesnesi=meclis_bellek, takas_mgr=takas_mgr
    ).M
    # Güvenlik: config.R < 1 olursa döngü hiç çalışmaz; mevcut_durum başlangıç durumuna sabitlenir
    mevcut_durum = E5_A_MevcutGizilDurum(x_r=x_current)
    # KAPSAMLI DENETİM DÜZELTMESİ: raw_n2_topox.forward'ın Faz2'deki İLK çağrısı (yukarıda,
    # satır ~658-659) AnlasmaliVramGuvencesiAl + AcilDurumOomYakalayiciVeKurtarici ile tam
    # korumalıyken, bu Faz3 "sabit" çağrısı HİÇ KORUMASIZDI (ne proaktif kontrat ne reaktif
    # yakalayıcı) — aynı düğümün aynı adımdaki İKİNCİ çağrısı unutulmuştu.
    AnlasmaliVramGuvencesiAl(raw_n2_topox, e2_byte_grouped, takas_mgr=takas_mgr)
    e3_sinir_sabit = AcilDurumOomYakalayiciVeKurtarici(
        raw_n2_topox.forward, e2_byte_grouped, x_initial=x_start_grouped, mode='train',
        modul_nesnesi=raw_n2_topox, takas_mgr=takas_mgr
    )
    AnlasmaliVramGuvencesiAl(laplasyen_insa, e3_sinir_sabit.D1, takas_mgr=takas_mgr)
    # NOT (matrissiz Laplasyen): bkz. yukarıdaki D0_op açıklaması — dense Delta_0 artık
    # hiç kurulmuyor, n6_aktor/n7_cozucu doğrudan D0_op_sabit ile matrissiz çalışıyor.
    # KAPSAMLI DENETİM: bkz. yukarıdaki D0_op için eklenen aynı reaktif sarmalayıcı gerekçesi.
    D0_op_sabit, _ = AcilDurumOomYakalayiciVeKurtarici(
        laplasyen_insa.insa_et, e3_sinir_sabit, e4_lif.phi_matrisleri,
        modul_nesnesi=laplasyen_insa, takas_mgr=takas_mgr
    )
    if hasattr(n6_aktor, 'update_operators'):
        n6_aktor.update_operators(D0_op_sabit)

    sorgu_q_list = []
    cevap_a_list = []

    for r in range(1, config.R + 1):
        e5_a = E5_A_MevcutGizilDurum(x_r=x_current)
        e5_b = E5_B_BellekGonderimi(M=M_current)
        
        AnlasmaliVramGuvencesiAl(n4_sorgu, e5_a.x_r, takas_mgr=takas_mgr)
        e6_sorgu = AcilDurumOomYakalayiciVeKurtarici(
            n4_sorgu.forward, e5_a, D0_operator=D0_op_sabit, A_adjacency=e3_sinir_sabit.D1, bellek=e5_b,
            modul_nesnesi=n4_sorgu, takas_mgr=takas_mgr
        )
        AnlasmaliVramGuvencesiAl(n5_cevap, e6_sorgu.q_r, takas_mgr=takas_mgr)
        e7_lokal = AcilDurumOomYakalayiciVeKurtarici(n5_cevap.forward, e6_sorgu, e5_b, modul_nesnesi=n5_cevap, takas_mgr=takas_mgr)
        
        sorgu_q_list.append(e6_sorgu.q_r)
        cevap_a_list.append(e7_lokal.a_r)
        
        def _tekil_n6_n7_step(x_c, q_c, a_c):
            e5_a_st = E5_A_MevcutGizilDurum(x_r=x_c)
            e6_sorgu_st = E6_GizilSorgu(q_r=q_c)
            e7_lokal_st = E7_LokalBilgi(a_r=a_c)
            AnlasmaliVramGuvencesiAl(n6_aktor, x_c, takas_mgr=takas_mgr)
            # NOT: checkpoint(use_reentrant=False) bu fonksiyonu backward'da AYNEN
            # tekrar çalıştırır (recompute) — reaktif kurtarıcı try/except tabanlı,
            # saf ve yan etkisiz olduğu için hem forward hem recompute çağrısında
            # güvenle devreye girer.
            e8_sentetik_st = AcilDurumOomYakalayiciVeKurtarici(
                n6_aktor.forward, e5_a_st, e6_sorgu_st, e7_lokal_st, modul_nesnesi=n6_aktor, takas_mgr=takas_mgr
            )
            AnlasmaliVramGuvencesiAl(n7_cozucu, e8_sentetik_st.synthetic_state, takas_mgr=takas_mgr)
            e9_guncel_st = AcilDurumOomYakalayiciVeKurtarici(
                n7_cozucu.forward, e8_sentetik_st, D0_op_sabit, e5_a_st, modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
            )
            return e9_guncel_st.x_next, e8_sentetik_st.synthetic_state

        x_next_val, h_syn_val = checkpoint(
            _tekil_n6_n7_step,
            x_current,
            e6_sorgu.q_r,
            e7_lokal.a_r,
            use_reentrant=False
        )
        
        e8_sentetik = E8_SentetikAraDurum(synthetic_state=h_syn_val)
        e9_guncel = E9_GuncellenmisGizilDurum(x_next=x_next_val)
        
        if isinstance(meclis_bellek, SMW_SifirParazit_BellekYoneticisi):
            k_r_key = e6_sorgu.q_r[:, :getattr(config, 'K', 16)] if e6_sorgu.q_r.shape[1] >= getattr(config, 'K', 16) else F.pad(e6_sorgu.q_r, (0, getattr(config, 'K', 16) - e6_sorgu.q_r.shape[1]))
            v_r_val = e7_lokal.a_r
            AnlasmaliVramGuvencesiAl(meclis_bellek, k_r_key, takas_mgr=takas_mgr)
            e5_b_yeni = AcilDurumOomYakalayiciVeKurtarici(
                meclis_bellek.write, k_r=k_r_key, v_r=v_r_val, modul_nesnesi=meclis_bellek, takas_mgr=takas_mgr
            )
        else:
            AnlasmaliVramGuvencesiAl(bellek_yazici, e9_guncel.x_next, takas_mgr=takas_mgr)
            e5_b_yeni = AcilDurumOomYakalayiciVeKurtarici(
                bellek_yazici.yaz, e9_guncel.x_next, e6_sorgu, e5_b, e7_lokal, modul_nesnesi=bellek_yazici, takas_mgr=takas_mgr
            )
        
        x_current = e9_guncel.x_next
        M_current = e5_b_yeni.M
        mevcut_durum = E5_A_MevcutGizilDurum(x_r=x_current)

    d_vec3 = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.hesapla_uyumsuzluk_vektoru, mevcut_durum.x_r, D0_op_sabit,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )
    e_vec3 = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.hesapla_dirichlet_enerjisi_vektoru, mevcut_durum.x_r, D0_op_sabit,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )

    # Aynı gerekçeyle (bkz. Faz 2) d_vec3 ve e_vec3 ayrı VJP'lerdir. KARDEŞ-VJP: ikisi de
    # mevcut_durum.x_r/D0_op_sabit/Delta_0_op_sabit üzerinden AYNI üst-grafı (R-döngüsü,
    # checkpoint(N6/N7) zinciri) paylaşır — ilk çağrı retain_graph=True gerektirir.
    _R_norm = float(max(1, config.R))
    _faz3_hedef_params = list(n6_aktor.parameters()) + list(n4_sorgu.parameters()) + list(n5_cevap.parameters())
    vjp_cerrahi_enjekte_et(d_vec3 / _R_norm, _faz3_hedef_params, retain_graph=True)
    g_faz3_uyumsuzluk = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(F.relu(e_vec3) / _R_norm, _faz3_hedef_params)
    g_faz3_dirichlet = _grad_anlik_kopyala()
    vram_denetci.yokla_ve_raporla("LOCO_Faz3_GrafSilindi", adim_no=current_step)

    # ------------------------------------------------------------------------------
    # FAZ 4-5: CHEBYSHEV SPEKTRAL PROJEKSİYON VE GRPO ÖDÜL KANVASI (N8 -> N10)
    # ------------------------------------------------------------------------------
    e9_guncel_detached = E9_GuncellenmisGizilDurum(x_next=e9_guncel.x_next.detach())
    AnlasmaliVramGuvencesiAl(n8_chebyshev, e9_guncel_detached.x_next, takas_mgr=takas_mgr)
    e10_kulli = AcilDurumOomYakalayiciVeKurtarici(n8_chebyshev.forward, e9_guncel_detached, modul_nesnesi=n8_chebyshev, takas_mgr=takas_mgr)

    # DÜZELTME: n8_b_uzunluk.forward() "Dinamik Uzunluk Seçici" görevini yaparak
    # N* = Clamp(N_teorik + Delta_N, N_min, N_max) hesaplıyordu (sınıf docstring'i:
    # "Nihai Dinamik Uzunluk"), ama dönen N_star_int değeri `_` ile atılıyor, yerine
    # SABİT config.N kullanılıyordu — bu, N8_B'nin bütün mimari amacını (arc-length
    # geometrisine göre cümle uzunluğunu dinamik seçmek) tamamen devre dışı bırakıyordu.
    # KAPSAMLI DENETİM: n8_b_uzunluk hiçbir yerde proaktif AnlasmaliVramGuvencesiAl
    # kontratına girmiyordu (yalnızca reaktif sarmalayıcısı vardı) — diğer tüm N1-N10
    # düğümleriyle aynı desene tamamlandı.
    AnlasmaliVramGuvencesiAl(n8_b_uzunluk, e10_kulli.C, takas_mgr=takas_mgr)
    N_star_int, L_arc_tensor, N_ste_tensor, delta_n_tensor = AcilDurumOomYakalayiciVeKurtarici(
        n8_b_uzunluk.forward, e10_kulli, cheby_calc,
        modul_nesnesi=n8_b_uzunluk, takas_mgr=takas_mgr
    )
    N_star = N_star_int
    L_arc_val = L_arc_tensor.item()
    # KAPSAMLI DENETİM: cheby_calc.hesapla hiçbir korumadan (ne proaktif ne reaktif)
    # geçmiyordu — T_matrix boyutu N_star'a bağlı olduğundan (dinamik) OOM riski taşır.
    T_matrix = AcilDurumOomYakalayiciVeKurtarici(cheby_calc.hesapla, N=N_star, takas_mgr=takas_mgr)
    hedef_clamped = torch.clamp(hedef_grouped[:, :N_star], min=0, max=getattr(config, 'V_size', 32000) - 1)

    # NOT: N9 (Vandermonde) ve N10 (Softmax Sözlük İzdüşümü) [B, N, V_size] gibi devasa
    # boyutlu tensörler ürettiği için OOM riski en yüksek düğümlerdir — reaktif kurtarıcı
    # burada özellikle kritiktir.
    AnlasmaliVramGuvencesiAl(n9_vandermonde, (e10_kulli.C.shape[0], N_star), takas_mgr=takas_mgr)
    e11_gomulu = AcilDurumOomYakalayiciVeKurtarici(n9_vandermonde.forward, e10_kulli, T_matrix, modul_nesnesi=n9_vandermonde, takas_mgr=takas_mgr)
    AnlasmaliVramGuvencesiAl(n10_sozluk, e11_gomulu.X_output, takas_mgr=takas_mgr)
    e12_olasilik = AcilDurumOomYakalayiciVeKurtarici(n10_sozluk.forward, e11_gomulu, hedefler=hedef_clamped, modul_nesnesi=n10_sozluk, takas_mgr=takas_mgr)

    with torch.no_grad():
        x_start_detached = E9_GuncellenmisGizilDurum(x_next=x_start_grouped.detach())
        # KAPSAMLI DENETİM: n8_chebyshev'in bu (cevapsız) çağrısı reaktif sarmalıydı ama
        # kendi proaktif kontratı burada yoktu (yalnızca üstteki "cevaplı" çağrı guard'lıydı).
        AnlasmaliVramGuvencesiAl(n8_chebyshev, x_start_detached.x_next, takas_mgr=takas_mgr)
        e10_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n8_chebyshev.forward, x_start_detached, modul_nesnesi=n8_chebyshev, takas_mgr=takas_mgr)
        AnlasmaliVramGuvencesiAl(n9_vandermonde, (e10_cevapsiz.C.shape[0], N_star), takas_mgr=takas_mgr)
        e11_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n9_vandermonde.forward, e10_cevapsiz, T_matrix, modul_nesnesi=n9_vandermonde, takas_mgr=takas_mgr)
        # KAPSAMLI DENETİM: n9'un guard'ı yalnızca n9'u kapsar — n10_sozluk'ün bu (cevapsız)
        # çağrısının kendi proaktif kontratı hiç yoktu (yalnızca üstteki "cevaplı" çağrı
        # guard'lıydı).
        AnlasmaliVramGuvencesiAl(n10_sozluk, e11_cevapsiz.X_output, takas_mgr=takas_mgr)
        e12_olasilik_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n10_sozluk.forward, e11_cevapsiz, hedefler=hedef_clamped, modul_nesnesi=n10_sozluk, takas_mgr=takas_mgr)

    # e12_olasilik.P ve e12_olasilik_cevapsiz.P, n10_sozluk'ün (birbirinden BAĞIMSIZ)
    # iki ayrı çağrısından geliyor — her biri kendi VRAM kontratına göre CPU'ya
    # düşmüş olabilir. Reaktif yakalayıcı yalnızca belirli hata mesajı kalıplarını
    # tanıyor ("Expected all tensors..."); "CUDAGuardImpl initialized with non-CUDA
    # DeviceType" gibi bir varyant o kalıba uymuyor ve çıplak çöküyordu. Burada
    # tahmine/reaktif yakalamaya güvenmek yerine cihazı AÇIKÇA, tek kaynaktan
    # (x_start_grouped'ın GPU/CPU durumu) hizalıyoruz.
    _hesap_cihazi = x_start_grouped.device
    p_target_cevapli = e12_olasilik.P
    if p_target_cevapli.device != _hesap_cihazi:
        p_target_cevapli = p_target_cevapli.to(_hesap_cihazi)
    p_target_cevapsiz = e12_olasilik_cevapsiz.P
    if p_target_cevapsiz.device != _hesap_cihazi:
        p_target_cevapsiz = p_target_cevapsiz.to(_hesap_cihazi)
    kayip_cevapsiz = -torch.log(p_target_cevapsiz + 1e-9).mean(dim=-1)
    kayip_cevapli = -torch.log(p_target_cevapli + 1e-9).mean(dim=-1)

    son_q = sorgu_q_list[-1]
    son_a = cevap_a_list[-1]
    # n9/n10 gibi bu çağrı da AcilDurumOomYakalayiciVeKurtarici İLE sarmalanmalı:
    # Delta_0=D0_op_sabit artık (bkz. Riyazi_LifLaplasyeniBlokInsaEdici.insa_et
    # düzeltmesi) VRAM kontratı CPU'ya yönlendirdiğinde GERÇEKTEN CPU'da gelebiliyor,
    # oysa q_r/a_r/x_context/kayip_* burada hâlâ GPU'da — çıplak çağrı "Expected all
    # tensors to be on the same device" ile çöküyordu. Sarmalayıcı hem bunu hem de
    # olası OOM'u yakalayıp tüm argümanları ortak bir cihaza (CPU) çekip tekrar dener.
    R_q, metrikler_q = AcilDurumOomYakalayiciVeKurtarici(
        odul_motoru.hesapla_aktif_sorgu_odulu,
        q_r=son_q, a_r=son_a, x_context=x_start_grouped,
        kayip_cevapsiz=kayip_cevapsiz, kayip_cevapli=kayip_cevapli, Delta_0=D0_op_sabit,
        modul_nesnesi=odul_motoru, takas_mgr=takas_mgr
    )

    # Aynı gerekçe: e12_olasilik.P, n10_sozluk'ün VRAM kontratı CPU'ya yönlendirdiğinde
    # CPU'da gelebilir; hedef_grouped ise hâlâ GPU'da olabilir — çıplak çağrı "Expected
    # all tensors to be on the same device" ile çökerdi (bkz. toplam_oduller = oduller_base
    # + R_q çökmesi: oduller_base CPU'da, R_q GPU'daydı).
    oduller_base = AcilDurumOomYakalayiciVeKurtarici(
        odul_motoru.hesapla, e12_olasilik.P, hedef_grouped[:, :N_star],
        modul_nesnesi=odul_motoru, takas_mgr=takas_mgr
    )
    # odul_motoru (N14_OdulTopolojikDevresmezlikMotoru) parametresiz düz bir sınıf —
    # AcilDurumOomYakalayiciVeKurtarici'nin "geri_donus_cihazi" tahmini bu durumda
    # ilk tensör argümanının (e12_olasilik.P) cihazına dayanır, ki bu da başka bir
    # düğümün VRAM kontratına göre CPU olabilir. R_q ile toplanmadan ÖNCE tahmine
    # güvenmeyip cihazı burada AÇIKÇA hizalıyoruz — tek kaynaktan doğruluk.
    if oduller_base.device != R_q.device:
        oduller_base = oduller_base.to(R_q.device)
    toplam_oduller = oduller_base + R_q
    # e12_olasilik.P (n10_sozluk'ün CPU-fallback'inden kalmış olabilir) ve
    # hedef_grouped/toplam_oduller (GPU) aynı çağrıda karışabiliyordu.
    kayip_grpo_vec = AcilDurumOomYakalayiciVeKurtarici(
        grpo_kriteri.hesapla_vektor, e12_olasilik.P, hedef_grouped[:, :N_star], toplam_oduller,
        modul_nesnesi=grpo_kriteri, takas_mgr=takas_mgr
    )
    n_target = float(hedef_grouped.shape[1])
    kayip_length = (L_arc_tensor - 0.5 * N_ste_tensor)**2 + 0.05 * (N_ste_tensor - n_target)**2
    kayip_spektral_vec = (kayip_length + 0.01 * torch.abs(delta_n_tensor).mean()).unsqueeze(0)
    
    AnlasmaliVramGuvencesiAl(vicreg_kriteri, e11_gomulu.X_output, takas_mgr=takas_mgr)
    (l_var_vec, l_cov_vec, l_rec_vec), metrikler_vicreg = AcilDurumOomYakalayiciVeKurtarici(
        vicreg_kriteri, x=e9_guncel_detached.x_next, z=e11_gomulu.X_output, modul_nesnesi=vicreg_kriteri, takas_mgr=takas_mgr
    )
    
    # HATA #1/#2 DÜZELTMESİ (kapsamlı denetimde bulundu — 30 hatalık listenin 1. ve 2.
    # maddesi): Bu 5 çağrı (kayip_grpo_vec, l_var_vec, l_cov_vec, l_rec_vec,
    # kayip_spektral_vec) HEPSİ e10_kulli (n8_chebyshev'in çıktısı) üzerinden AYNI
    # paylaşılan üst-grafı paylaşan TEK bir KARDEŞ-VJP grubudur:
    #   kayip_grpo_vec        <- e12_olasilik.P <- n10_sozluk <- e11_gomulu <- n9_vandermonde <- e10_kulli
    #   l_var/l_cov/l_rec_vec <- z=e11_gomulu.X_output        <- n9_vandermonde <- e10_kulli
    #   kayip_spektral_vec    <- L_arc/N_ste/delta_n           <- n8_b_uzunluk  <- e10_kulli
    # ÖNCEDEN hepsi retain_graph=False (varsayılan) kullanıyordu: İLK çağrı (kayip_grpo_vec)
    # paylaşılan e10_kulli grafını ANINDA siliyor, sonraki 4 çağrının hepsi "Trying to
    # backward through the graph a second time" hatası alıp vjp_cerrahi_enjekte_et'in
    # çıplak `except`ine sessizce yutuluyordu — yani VICReg (var/cov/rec) ve spektral
    # kayıp GERÇEKTE HİÇ EĞİTMİYORDU, hiçbir hata/uyarı görünür olmadan.
    # DÜZELTME: grup içindeki İLK 4 çağrı retain_graph=True, yalnızca SON çağrı
    # (kayip_spektral_vec) varsayılan retain_graph=False ile grafı gerçekten serbest bırakır.
    #
    # AYRICA (aynı kökten 2. hata): l_var/l_cov/l_rec_vec, n10_sozluk'ün DEĞİL —
    # n9_vandermonde'un (ve onun atası n8_chebyshev'in) çıktısı olan z=e11_gomulu.X_output
    # üzerinden hesaplanıyor; n10_sozluk bu tensörlerin atası bile değil. Eskiden
    # `_n10_hedef_params` (n10_sozluk.parameters()) hedef olarak kullanılıyordu —
    # allow_unused=True bu durumda sessizce None döndürüyordu. Artık doğru atalar
    # (n9_vandermonde + n8_chebyshev; vicreg_kriteri parametresiz bir sınıf, dahil
    # edilmedi) hedefleniyor.
    _n10_hedef_params = list(n10_sozluk.parameters())
    _vicreg_hedef_params = list(n9_vandermonde.parameters()) + list(n8_chebyshev.parameters())
    vjp_cerrahi_enjekte_et(kayip_grpo_vec, _n10_hedef_params, retain_graph=True)
    g_grpo = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(l_var_vec, _vicreg_hedef_params, retain_graph=True)
    g_vicreg_var = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(l_cov_vec, _vicreg_hedef_params, retain_graph=True)
    g_vicreg_cov = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(l_rec_vec, _vicreg_hedef_params, retain_graph=True)
    g_vicreg_rec = _grad_anlik_kopyala()

    vjp_cerrahi_enjekte_et(kayip_spektral_vec, list(n8_chebyshev.parameters()) + list(n8_b_uzunluk.parameters()))
    g_spektral = _grad_anlik_kopyala()

    # --- HATA 1 DÜZELTMESİ: Canlı Graf Üzerinden N4 VJP Enjeksiyonu ---
    # sorgu_q_list[-1] kopuk graftan geliyor; N4 gradyanı için canlı forward gerekli
    # x_r'ı donduruyoruz çünkü amacımız sadece N4 parametrelerine gradyan iletmek
    _x_canli = mevcut_durum.x_r.detach()
    e5_a_canli_2 = E5_A_MevcutGizilDurum(x_r=_x_canli)
    e5_b_canli = E5_B_BellekGonderimi(M=M_current.detach())
    # n4_sorgu.forward'ın Faz3 döngüsündeki ilk çağrısı (yukarıda, e6_sorgu =
    # AcilDurumOomYakalayiciVeKurtarici(...)) zaten sarmalıyken bu TAZE çağrı
    # çıplaktı — D0_operator=D0_op_sabit VRAM kontratına göre CPU'da gelebilirken
    # n4_sorgu'nun kendi ağırlıkları GPU'da olabilir (ya da tam tersi, n4_sorgu'nun
    # kendisi de AnlasmaliVramGuvencesiAl ile CPU'ya yönlendirilmiş olabilir).
    e6_sorgu_canli = AcilDurumOomYakalayiciVeKurtarici(
        n4_sorgu.forward, e5_a_canli_2,
        D0_operator=D0_op_sabit, A_adjacency=e3_sinir_sabit.D1, bellek=e5_b_canli,
        modul_nesnesi=n4_sorgu, takas_mgr=takas_mgr
    )
    son_a_detached = cevap_a_list[-1].detach()
    E_sorgu_canli = (e6_sorgu_canli.q_r.unsqueeze(1) - son_a_detached.unsqueeze(2)).pow(2).mean(dim=-1)
    vjp_cerrahi_enjekte_et(E_sorgu_canli, list(n4_sorgu.parameters()))
    g_sorgu = _grad_anlik_kopyala()
    # -----------------------------------------------------------------------

    # --- BÜTÜNCÜL CÜMLE KEYFİYETİ: 11. Adlandırılmış PCGrad Nesnesi ---
    # Kelime-bazlı P > 0.1 sezgiselinin yanına, Sorgu-Cevap ahengi (N4), Eşsınır
    # kararlılığı (D0 üzerinden) ve Spektral/Kapasite uyumunun (N8-N9) ÇARPIMSAL
    # mutabakatını ölçen ayrı bir sinyal ekler.
    #
    # NOT: e6_sorgu_canli.q_r TEKRAR KULLANILAMAZ — g_sorgu'nun VJP'si
    # (vjp_cerrahi_enjekte_et(E_sorgu_canli, ...)) retain_graph=False ile onun
    # grafını zaten tüketti; aynı tensörü ikinci bir VJP'de kullanmaya çalışmak
    # "Trying to backward through the graph a second time" hatası doğurur — tam
    # olarak HATA 1'in kendisinin çözdüğü sorunun aynısı. Bu yüzden AYRI, TAZE bir
    # n4_sorgu.forward() çağrısı ile bağımsız bir graf üretilir (e5_a_canli_2 ve
    # e5_b_canli zaten detached/leaf girdiler olduğu için bu ikinci çağrı hiçbir
    # paylaşılan graf düğümüne dokunmaz, tamamen bağımsızdır).
    e6_sorgu_canli_cumle = AcilDurumOomYakalayiciVeKurtarici(
        n4_sorgu.forward, e5_a_canli_2,
        D0_operator=D0_op_sabit, A_adjacency=e3_sinir_sabit.D1, bellek=e5_b_canli,
        modul_nesnesi=n4_sorgu, takas_mgr=takas_mgr
    )
    # NOT 2: L_arc_tensor/N_ste_tensor DE TEKRAR KULLANILAMAZ — kayip_spektral_vec'in
    # VJP'si (n8_chebyshev + n8_b_uzunluk parametrelerini hedefleyerek) bu tensörlerin
    # TÜM grafını retain_graph=False ile zaten tüketti. n8_b_uzunluk.forward() TAZE
    # çağrılır (e10_kulli'nin KENDİ DEĞERİ hâlâ geçerlidir, yalnızca onun ESKİ backward
    # grafı ölüdür — yeni bir forward çağrısı yeni, bağımsız bir graf üretir). Ancak
    # e10_kulli'nin kendi atası (n8_chebyshev'e kadar) hâlâ ölü olduğu için bu VJP'nin
    # hedefi yalnızca n8_b_uzunluk.parameters() ile sınırlı tutulur — n8_chebyshev.
    # parameters() İSTENMEZ (aksi halde e10_kulli'nin ölü atasına geri backward
    # denemesi gerekirdi ve aynı "graph a second time" hatası tekrar oluşurdu).
    AnlasmaliVramGuvencesiAl(n8_b_uzunluk, e10_kulli.C, takas_mgr=takas_mgr)
    _, L_arc_cumle, N_ste_cumle, _ = AcilDurumOomYakalayiciVeKurtarici(
        n8_b_uzunluk.forward, e10_kulli, cheby_calc,
        modul_nesnesi=n8_b_uzunluk, takas_mgr=takas_mgr
    )
    # D0_op=D0_op_sabit burada da (bkz. yukarıdaki hesapla_aktif_sorgu_odulu /
    # n4_sorgu.forward düzeltmeleri) VRAM kontratına göre CPU'da gelebilirken diğer
    # argümanlar (e6_sorgu_canli_cumle.q_r, hedef_grouped vb.) GPU'da olabilir.
    kayip_cumle_keyfiyet_vec = AcilDurumOomYakalayiciVeKurtarici(
        cumle_keyfiyet_motoru.hesapla_vektor,
        q_son=e6_sorgu_canli_cumle.q_r,
        a_son=son_a_detached,
        x_son=_x_canli,
        D0_op=D0_op_sabit,
        hedef_tokens=hedef_grouped,
        L_arc=L_arc_cumle,
        N_ste=N_ste_cumle,
        modul_nesnesi=cumle_keyfiyet_motoru, takas_mgr=takas_mgr
    )
    _cumle_hedef_params = list(n4_sorgu.parameters()) + list(n8_b_uzunluk.parameters())
    vjp_cerrahi_enjekte_et(kayip_cumle_keyfiyet_vec, _cumle_hedef_params)
    g_cumle_keyfiyet = _grad_anlik_kopyala()
    # -----------------------------------------------------------------------

    vram_denetci.yokla_ve_raporla("LOCO_Faz4_5_GrafSilindi", adim_no=current_step)

    # ------------------------------------------------------------------------------
    # PARETO-PCGRAD DİKGEN PROJEKSİYONU VE NİHAİ KÜRESEL GÜNCELLEME
    # ------------------------------------------------------------------------------
    # [4. HATA DÜZELTMESİ] Nesne-Seviyesi Granülerlik: 3 kaba faz yerine, her adlandırılmış
    # hata büyüklüğü (11 nesne — Bütüncül Cümle Keyfiyeti dahil) kendi ayrı satırı olarak
    # Gram matrisine/PCGrad'a girer. Gerçek MGDA'nın istediği "her bileşen için ayrı gradyan"
    # idealinin, M~binlerce elemanlı tam Jacobiyen yerine VRAM'e sığan bir yaklaşımı
    # (bkz. _grad_anlik_kopyala).
    shard_gradyanlari = [
        g_faz2_uyumsuzluk, g_faz2_dirichlet,
        g_faz3_uyumsuzluk, g_faz3_dirichlet,
        g_grpo, g_vicreg_var, g_vicreg_cov, g_vicreg_rec,
        g_spektral, g_sorgu, g_cumle_keyfiyet,
    ]
    _P_toplam = sum(p.numel() for p in trainable_params)
    AnlasmaliVramGuvencesiAl(pareto_pcgrad_operator, (len(shard_gradyanlari), _P_toplam), takas_mgr=takas_mgr)
    alpha_pareto = pareto_pcgrad_operator.birlestir_ve_uygula_dagitik_gradyanlar(
        shard_gradyanlari=shard_gradyanlari,
        trainable_params=trainable_params,
        optimizer=optimizer,
        max_norm=1.0
    )

    grad_norm_pareto = math.sqrt(sum((p.grad.norm().item() ** 2 for p in trainable_params if p.grad is not None)))
    adapted_lr = config.lr / (1.0 + 0.01 * grad_norm_pareto)
    for param_group in optimizer.param_groups:
        param_group['lr'] = adapted_lr

    vram_denetci.yokla_ve_raporla("LOCO_Pareto_PCGrad_StepCompleted", adim_no=current_step)

    # ADIM SONUNDA SMW MECLİS BELLEĞİNİ TÜREV GRAFİĞİNDEN KOPAR
    if hasattr(meclis_bellek, 'detach_memory'):
        meclis_bellek.detach_memory()
    elif hasattr(meclis_bellek, 'M') and meclis_bellek.M is not None:
        meclis_bellek.M = meclis_bellek.M.detach()
        if hasattr(meclis_bellek, 'R') and meclis_bellek.R is not None:
            meclis_bellek.R = meclis_bellek.R.detach()

    # HAKİKİ BİLEŞKE KAYIP: rastgele/eksik bir ham toplam (eskiden yalnızca 6/11 nesneyi
    # kapsıyordu ve Pareto'nun uyguladığı gerçek ağırlıklandırmayla hiçbir illiyet bağı
    # yoktu) yerine, shard_gradyanlari ile AYNI SIRADAKİ 11 nesnenin skaler ortalaması,
    # optimizer.step()'e fiilen giren GERÇEK Pareto-optimal ağırlıklarla (alpha_pareto)
    # tartılarak birleştirilir. NOT: grad_norm_pareto burada KULLANILMAZ — o,
    # clip_grad_norm_(max_norm=1.0) SONRASI ölçüldüğü için neredeyse sabit (~1.0) bir
    # değerdir ve best_loss ayrımı için bilgi taşımaz; gradyan şiddeti zaten kayıp
    # kalitesiyle aynı şey değildir (yakınsama yaklaştıkça gradyan küçülür, bu "daha iyi
    # model" anlamına gelmez). Aşağıdaki ağırlıklı toplam ise gerçekten "o adımda hangi
    # bileşenin ne kadar önemsendiği" ile orantılı, kayıp-anlamlı bir skalerdir.
    _kayip_bileseni_listesi = [
        d_vec2.mean(), F.relu(e_vec2).mean(),
        (d_vec3 / _R_norm).mean(), (F.relu(e_vec3) / _R_norm).mean(),
        kayip_grpo_vec.mean(), l_var_vec.mean(), l_cov_vec.mean(), l_rec_vec.mean(),
        kayip_spektral_vec.mean(), E_sorgu_canli.mean(), kayip_cumle_keyfiyet_vec.mean(),
    ]
    kayip_val = float(sum(
        float(alpha_pareto[i].detach().item()) * float(_kayip_bileseni_listesi[i].detach().item())
        for i in range(len(_kayip_bileseni_listesi))
    ))
    
    raw_n3_lif = gpu_dagitici.kok_modul_al(n3_lif) if gpu_dagitici is not None else (n3_lif.module if hasattr(n3_lif, 'module') else n3_lif)
    stiefel_izdusurucu.izdüsür(raw_n3_lif.phi_base)

    d_discrepancy = float(d_vec3.mean().detach().item())
    dirichlet_energy = float(e_vec3.mean().detach().item())

    if _takas_cm is not None:
        _takas_cm.__exit__(None, None, None)
        # ADIMLAR ARASI SIZINTI DÜZELTMESİ: saved_tensors_hooks kapsamı (_takas_cm) tam
        # burada kapanıyor — yani bu adımda offload edilmiş ama backward'ı hiç çalışmamış
        # (retain_graph=False ile grafı erken serbest bırakılmış) her tensör artık KESİN
        # OLARAK yetimdir; bir daha asla geri çağrılmayacaktır. GuvenliVramVeTmpSupurgesi
        # bu tür kayıtları 120 sn'lik zaman aşımına kadar bekletiyordu (bkz. o sınıfın
        # docstring'i — ref_count hiç düşmediği için önceden HİÇ süpürülmüyordu); burada
        # adım sonunda AÇIKÇA temizleyerek /tmp/kulli_scratchpad'in ve kayıt defterinin
        # adım adım büyümesini (sızıntıyı) önlüyoruz.
        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
            takas_mgr.temizle(agresif=True)

    # CPYTHON STACK FRAME SONU: Fonksiyon return ettiği an tüm yerel bellek değişkenleri yok edilir!
    return kayip_val, L_arc_val, dirichlet_energy, d_discrepancy


# ==============================================================================
# III. HAKİKİ VE DETAYLI EĞİTİM YÜRÜTÜCÜ SÜRECİ (MAIN EXECUTION)
# ==============================================================================
def Main_EgitimYurutucu(konfig_yolu: Optional[str] = None, manifest_yolu: str = "/kaggle/working/verisetleri_manifest.json", idareci: Optional[Any] = None) -> None:
    # NOT: 'idareci' parametresi KULLANILMAZ (geriye dönük çağrı uyumluluğu için
    # kabul edilir, silinmez). Eski CpuAnaIdareci/GPU-işçi-süreci/NCCL çoklu-süreç
    # mimarisi bu fonksiyonun içinde HİÇ referans edilmez — VRAM/OOM idaresi tek
    # süreçte, AnlasmaliVramGuvencesiAl + AcilDurumOomYakalayiciVeKurtarici üzerinden
    # yürür. Çağıran notebook hücresinde CpuAnaIdareci().surecleri_baslat_ve_ilkle()
    # (4 GPU işçi süreci + NCCL halkası) çağrılıyorsa TAMAMEN GEREKSİZDİR, sadece
    # başlangıçta zaman kaybettirir — kaldırılmalıdır.
    logger.info("================================================================================")
    logger.info("BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS MİMARİSİ EĞİTİM YÜRÜTÜCÜSÜ (ÇOKLU GPU PARALEL DÖNGÜ)")
    logger.info("================================================================================")

    # TasmaFarkindaHesaplamaIdaresi.baslat() KASITLI OLARAK ÇAĞRILMIYOR — küresel
    # torch.matmul/F.linear monkey-patch'i yalnızca bizim çağrılarımızı değil
    # PyTorch'un KENDİ İÇ yollarını da (autograd backward ilkelleri, batched/broadcast
    # matmul, .T transpose view'ları) yakalıyor ve gerçek bir Kaggle koşusunda 2. eğitim
    # adımında "RuntimeError: self must be a matrix" üretti (insa_et içindeki
    # Delta_0 = D0^T @ D0 çağrısı üzerinden). Taşma-bazlı çoklu-GPU dağıtımı artık
    # yalnızca gerçekten büyük olduğu bilinen noktalarda AÇIKÇA
    # (tasma_bazli_capraz_gpu_matmul_sardla) kullanılıyor — bkz. insa_et.

    # NVMe Takas Yöneticisini İlkle (Sıfır OOM Garantisi)
    takas_mgr = NvmeTakasYoneticisi()
    
    # 1. Konfigürasyon Yükleme
    param_dict = {}
    if konfig_yolu and os.path.exists(konfig_yolu):
        with open(konfig_yolu, 'r', encoding='utf-8') as f:
            param_dict = json.load(f)
        logger.info(f"Konfigürasyon dosyasından yüklendi: {konfig_yolu}")
        
    config = Model_TopolojikKonfigurasyon(param_dict)
    config.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    
    GRPO_G = getattr(config, 'GRPO_G', 4)
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
    cumle_keyfiyet_motoru = Odul_ButunculCumleKeyfiyetMotoru(config)
    stiefel_izdusurucu = N13_StiefelManifolduIzdusumu()
    pareto_pcgrad_operator = Riyazi_Pareto_PCGrad_MGDA_Operator()
    vicreg_kriteri = Kayip_VICReg_UcluBilgiKorunumu().to(config.device)
    
    veri_yukleyici = Egitim_TopolojikVeriYukleyici(config, manifest_yolu=manifest_yolu)

    tum_moduller = {
        'n1_byte': n1_byte,
        'n2_topox': n2_topox,
        'n3_phi': n3_lif,
        'n4': n4_sorgu,
        'n5': n5_cevap,
        'n6_aktor': n6_aktor,
        'n7': n7_cozucu,
        'n8': n8_chebyshev,
        'n8_b': n8_b_uzunluk,
        'n9_vandermonde': n9_vandermonde,
        'n10': n10_sozluk,
        'bellek': meclis_bellek,
        'bellek_yazici': bellek_yazici
    }



    # Modül Ağırlıklarını Dikgen (Orthogonal) Olarak İlkle
    agirlik_ilkleyici = Riyazi_AgirlikIlkleyici()
    agirlik_ilkleyici.ilkle(list(tum_moduller.values()))

    # KÜLLÎ SANAL GPU: Modüller tekil sanal VRAM havuzunda doğrudan çalışır.
    
    trainable_params = []
    seen_params = set()
    for m in tum_moduller.values():
        for p in m.parameters():
            if p not in seen_params:
                seen_params.add(p)
                trainable_params.append(p)
        
    optimizer = optim.AdamW(trainable_params, lr=config.lr, weight_decay=1e-4)
    logger.info("Tüm Sinir Ağları ve Stiefel Parametreleri Optimizasyona Bağlandı.")

    vram_denetci = Hafiza_Izleyici_ve_VRAM_Denetci(cihaz=config.device, kritik_esik_yuzde=0.85)

    # Hakiki Checkpoint ve Hiyerarşik Hafıza Restorasyonu
    baslangic_step, loss_history = npz_mgr.load_pytorch_model(tum_moduller, optimizer)
    current_step = baslangic_step
    
    # Restore sonrası Stiefel dikgenliğini garantile
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

                    # CPYTHON STACK FRAME İZOLASYONU: Adım icrası müstakil fonksiyona devredilir
                    curr_loss_val, L_arc_val, dirichlet_energy, d_discrepancy = _tekil_egitim_adimi_icra(
                        e1_girdi_metni=e1_girdi_metni,
                        hedef_tensor=hedef_tensor,
                        tum_moduller=tum_moduller,
                        config=config,
                        optimizer=optimizer,
                        trainable_params=trainable_params,
                        current_step=current_step,
                        vram_denetci=vram_denetci,
                        laplasyen_insa=laplasyen_insa,
                        cheby_calc=cheby_calc,
                        odul_motoru=odul_motoru,
                        grpo_kriteri=grpo_kriteri,
                        cumle_keyfiyet_motoru=cumle_keyfiyet_motoru,
                        vicreg_kriteri=vicreg_kriteri,
                        pareto_pcgrad_operator=pareto_pcgrad_operator,
                        stiefel_izdusurucu=stiefel_izdusurucu,
                        gpu_dagitici=None,
                        gpu_cesitlendirici=None,
                        takas_mgr=takas_mgr
                    )

                    current_step += 1
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
                    # CPYTHON STACK FRAME SONRASI FİZİKSEL VRAM VE GARBAGE COLLECTION PROTOKOLÜ
                    # ==============================================================================
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











    