
import os
import sys

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

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

from kulli_gpu import NvmeTakasYoneticisi, kuresel_ram_denetci
from mucit_ai.topolojik_islem_sevk import TopolojikIslemSevk
import dagitik_egitim

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

SESSIZ_URETIM_MODU: bool = True
OZET_ADIM_ARALIGI: int = 10
LOG_DOSYA_TAVANI_BAYT: int = 100 * 1024
DURUM_DOSYASI: str = 'egitim_durumu.txt'

def kur_logging_sistemi(log_dosyasi: str = 'egitim_dongusu_icra.log') -> None:
    root = logging.getLogger()
    root.handlers.clear()

    if SESSIZ_URETIM_MODU:
        root.setLevel(logging.ERROR)
        fh = RotatingFileHandler(log_dosyasi, maxBytes=LOG_DOSYA_TAVANI_BAYT,
                                 backupCount=1, encoding='utf-8')
        fh.setLevel(logging.ERROR)
        fh.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - (%(name)s) - %(message)s'))
        root.addHandler(fh)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.ERROR)
        ch.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s'))
        root.addHandler(ch)
        return

    root.setLevel(logging.DEBUG)

    fh = RotatingFileHandler(log_dosyasi, maxBytes=LOG_DOSYA_TAVANI_BAYT,
                             backupCount=1, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - (%(name)s) - %(message)s'))
    root.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s'))
    root.addHandler(ch)

def kur_ozet_kanali() -> logging.Logger:
    ozet = logging.getLogger('MucitOzet')
    ozet.handlers.clear()
    ozet.setLevel(logging.INFO)
    ozet.propagate = False
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(message)s'))
    ozet.addHandler(ch)
    return ozet

kur_logging_sistemi()
logger = logging.getLogger('MainEgitim')
ozet_logger = kur_ozet_kanali()

class SadeceAnaSurecHafiza:

    def __init__(self, gercek: Any):
        self._gercek = gercek

    def save_hafiza_state(self, *args: Any, **kwargs: Any) -> None:
        return None

    def save_pytorch_model(self, *args: Any, **kwargs: Any) -> str:
        return ""

    def __getattr__(self, ad: str) -> Any:
        return getattr(self._gercek, ad)

class SessizVramDenetci:

    def __init__(self, gercek_denetci: Any = None):
        self.gercek_denetci = gercek_denetci

    def yokla_ve_raporla(self, *args: Any, **kwargs: Any) -> None:
        return None

    def __getattr__(self, ad: str) -> Any:
        return getattr(self.gercek_denetci, ad)

def egitim_parametrelerini_topla(config: Any, trainable_params: List[nn.Parameter],
                                 adim: int, kayip: float, ek: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    with torch.no_grad():

        _kareler: Dict[Any, torch.Tensor] = {}
        _grad_kareler: Dict[Any, torch.Tensor] = {}
        _sayi = 0
        for p in trainable_params:
            _cihaz = p.device
            _v = p.detach().float().pow(2).sum()
            _kareler[_cihaz] = _v if _cihaz not in _kareler else _kareler[_cihaz] + _v
            _sayi += p.numel()
            if p.grad is not None:
                _gv = p.grad.detach().float().pow(2).sum()
                _grad_kareler[_cihaz] = _gv if _cihaz not in _grad_kareler else _grad_kareler[_cihaz] + _gv
        _norm_kare = sum(float(_v) for _v in _kareler.values())
        _grad_norm_kare = sum(float(_v) for _v in _grad_kareler.values())

    deger: Dict[str, Any] = {'adim': adim, 'kayip': kayip}
    for ad in ('V_nodes', 'd_v', 'd_e', 'd_q', 'd_a', 'd_m', 'd_h', 'd', 'D', 'M_plus_1',
               'N', 'N_max', 'R', 'K', 'V_size', 'V_byte_size', 'GRPO_G', 'beta_kl',
               'dt', 'lr', 'batch_size', 'azami_dugum_komsulugu', 'azami_dugum_sayisi',
               'device'):
        deger[ad] = getattr(config, ad, None)
    deger['parametre_sayisi'] = _sayi
    deger['agirlik_L2'] = _norm_kare ** 0.5
    deger['gradyan_L2'] = _grad_norm_kare ** 0.5
    if torch.cuda.is_available():
        deger['vram_MB'] = torch.cuda.memory_allocated() / (1024 ** 2)

        deger['vram_tepe_MB'] = torch.cuda.max_memory_allocated() / (1024 ** 2)
        torch.cuda.reset_peak_memory_stats()
    if ek:
        deger.update(ek)
    return deger

def durum_ozetini_bas(deger: Dict[str, Any], durum_dosyasi: str = DURUM_DOSYASI) -> None:

    satirlar = [f"===== MUCIT AI EGITIM DURUMU | adim {deger.get('adim')} ====="]
    for ad, v in deger.items():
        if isinstance(v, float):
            satirlar.append(f"  {ad:24s} = {v:.6g}")
        else:
            satirlar.append(f"  {ad:24s} = {v}")
    metin = "\n".join(satirlar)

    ozet_logger.info(metin)

    try:
        gecici = durum_dosyasi + ".tmp"
        with open(gecici, "w", encoding="utf-8") as f:
            f.write(metin + "\n")
        os.replace(gecici, durum_dosyasi)
    except OSError:
        pass

KOD_SURUM_ETIKETI = "2026-08-12-sizinti-giderildi-tekrar-dongusu-yok"

TF32_ACIK: bool = True

FUSED_ADAMW_ACIK: bool = False

N7_N2_MIKRO_ZAMAN_ACIK: bool = True

def donanim_hizlandirmasini_uygula() -> None:
    if not torch.cuda.is_available():
        logger.info("  [Hızlandırma] GPU yok; TF32/tensör çekirdeği ayarları atlandı.")
        return

    if TF32_ACIK:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        logger.info(
            "  [Hızlandırma] TF32 tensör çekirdekleri AÇIK. Uyarı: TF32 mantisi 10 bit "
            "(FP32'de 23 bit); üs aralığı aynı kaldığı için taşma/sönme olmaz ama "
            "çarpım hassasiyeti ~1e-3 mertebesine iner. Stiefel dikliği ve Cayley "
            "çözümü bundan etkilenebilir; şüphe halinde TF32_ACIK=False yapın."
        )
    else:
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        logger.info("  [Hızlandırma] TF32 kapalı; matris çarpımları tam FP32.")

    torch.backends.cudnn.benchmark = False
    logger.info(
        "  [Hızlandırma] cudnn.benchmark KAPALI bırakıldı: mimaride evrişim katmanı yok "
        "ve N* her adımda değiştiği için benchmark her yeni şekilde yeniden ölçüm yapıp "
        "zaman kaybettirirdi."
    )

def hizli_optimizer_kur(trainable_params: List[nn.Parameter], lr: float,
                        weight_decay: float = 1e-4) -> torch.optim.Optimizer:

    _cihazlar = {p.device for p in trainable_params}
    _dtipler = {p.dtype for p in trainable_params}
    _fused_uygun = (
        FUSED_ADAMW_ACIK
        and torch.cuda.is_available()
        and len(_cihazlar) == 1
        and len(_dtipler) == 1
        and next(iter(_cihazlar)).type == 'cuda'
    )

    if torch.cuda.is_available() and not _fused_uygun:
        logger.info(
            f"  [Hızlandırma] Fused AdamW KULLANILMIYOR. Sebep: "
            f"{'bayrak kapalı' if not FUSED_ADAMW_ACIK else f'parametreler {len(_cihazlar)} cihaz / {len(_dtipler)} dtype üzerinde dağılmış'}. "
            f"Fused çekirdek parametre, gradyan ve optimizer durumunun aynı cihaz ve "
            f"dtype'ta olmasını şart koşar; acil durum kurtarıcı modülleri CPU'ya "
            f"taşıyabildiği için bu şart garanti edilemez."
        )

    if _fused_uygun:
        try:
            opt = optim.AdamW(trainable_params, lr=lr, weight_decay=weight_decay, fused=True)
            logger.info(
                "  [Hızlandırma] Fused AdamW etkin: tüm parametreler tek CUDA çekirdeğinde "
                "güncelleniyor."
            )
            return opt
        except (RuntimeError, TypeError, ValueError) as exc:
            logger.warning(f"  [Hızlandırma] Fused AdamW kurulamadı ({exc}); foreach deneniyor.")

    try:
        opt = optim.AdamW(trainable_params, lr=lr, weight_decay=weight_decay, foreach=True)
        logger.info("  [Hızlandırma] foreach AdamW etkin (parametreler toplu güncelleniyor).")
        return opt
    except (RuntimeError, TypeError, ValueError):
        logger.info("  [Hızlandırma] Standart AdamW kullanılıyor.")
        return optim.AdamW(trainable_params, lr=lr, weight_decay=weight_decay)

ASGARI_BOS_DISK_MB: float = 1536.0
ASGARI_BOS_RAM_MB: float = 768.0

def _bos_disk_mb(dizin: str) -> float:
    try:
        import shutil as _shutil
        return _shutil.disk_usage(dizin).free / (1024 ** 2)
    except Exception:
        return float('inf')

def _bos_ram_mb() -> float:
    try:
        with open('/proc/meminfo', 'r', encoding='utf-8') as f:
            for satir in f:
                if satir.startswith('MemAvailable:'):
                    return int(satir.split()[1]) / 1024.0
    except Exception:
        pass
    return float('inf')

def kaynak_nobetcisi(izlenecek_dizinler: List[str], baglam: str = "") -> None:
    darlik: List[str] = []

    for dizin in izlenecek_dizinler:
        if not dizin or not os.path.isdir(dizin):
            continue
        bos = _bos_disk_mb(dizin)
        if bos < ASGARI_BOS_DISK_MB:
            darlik.append(f"disk '{dizin}': {bos:.0f} MB boş (eşik {ASGARI_BOS_DISK_MB:.0f} MB)")

    bos_ram = _bos_ram_mb()
    if bos_ram < ASGARI_BOS_RAM_MB:
        darlik.append(f"sistem RAM: {bos_ram:.0f} MB boş (eşik {ASGARI_BOS_RAM_MB:.0f} MB)")

    if not darlik:
        return

    logger.error("=" * 80)
    logger.error(f"KAYNAK NÖBETÇİSİ: süreç DERHAL sonlandırılıyor. Bağlam: {baglam}")
    for sebep in darlik:
        logger.error(f"  - {sebep}")
    logger.error(
        "Gerekçe: disk veya RAM tükendiğinde süreç yazma/ayırma çağrılarında asılı kalır; "
        "işletim sisteminin bunu fark edip öldürmesi çok geç olur ve oturum boşa gider. "
        "Beklemek yerine burada kesiliyor."
    )
    logger.error("=" * 80)

    for _islenmemis in logging.getLogger().handlers:
        try:
            _islenmemis.flush()
        except Exception:
            pass

    os._exit(9)

def kod_surumu_bildir() -> None:
    logger.info(f"  [Kod Sürümü] Etiket: {KOD_SURUM_ETIKETI}")
    logger.info(f"  [Kod Sürümü] Çalışan dosya: {os.path.abspath(__file__)}")

    _kok = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        _sonuc = subprocess.run(
            ["git", "-C", _kok, "log", "-1", "--format=%h %cI %s"],
            capture_output=True, text=True, timeout=10,
        )
        if _sonuc.returncode == 0 and _sonuc.stdout.strip():
            logger.info(f"  [Kod Sürümü] Git commit: {_sonuc.stdout.strip()}")
        else:
            logger.warning(
                "  [Kod Sürümü] Git bilgisi okunamadı — bu kod bir git deposundan DEĞİL, "
                "muhtemelen kopyalanmış bir anlık görüntüden çalışıyor. "
                "Günlükteki hataları düzeltilmiş sürümle karşılaştırırken bunu hesaba katın."
            )
    except Exception as _git_exc:
        logger.warning(f"  [Kod Sürümü] Git sorgusu başarısız: {_git_exc}")

    _beklenen_isaretler = {
        "tekrar döngüsü kaldırıldı": "Chunk ATLANMIYOR, yeniden DENENMİYOR" in _bu_dosyanin_metni(),
        "takas pack kancası detach": _takas_detach_var_mi(),
    }
    for _ad, _var in _beklenen_isaretler.items():
        logger.info(f"  [Kod Sürümü] {_ad}: {'VAR' if _var else 'YOK (ESKİ SÜRÜM!)'}")

def _bu_dosyanin_metni() -> str:
    try:
        with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def _takas_detach_var_mi() -> bool:
    try:
        import kulli_gpu.nvme_takas_yoneticisi as _takas_mod
        with open(_takas_mod.__file__, "r", encoding="utf-8") as f:
            return "return tensor.detach()" in f.read()
    except Exception:
        return False

KAGGLE_WORKING_DIR = "/kaggle/working" if os.path.exists("/kaggle/working") else "./checkpoints"

class KaggleDatasetUploader:
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
        if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
            self._configured = True
            return

        if os.path.isfile(self.cred_path):
            try:
                with open(self.cred_path, "r", encoding="utf-8") as f:
                    creds = json.load(f)
                os.environ["KAGGLE_USERNAME"] = creds.get("username", "")
                os.environ["KAGGLE_KEY"]      = creds.get("key", "")

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
                timeout=120,
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

class Odul_TopolojikDevresmezlikMotoru:
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
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def hesapla_vektor(
        self,
        q_son: torch.Tensor,
        a_son: torch.Tensor,
        x_son: torch.Tensor,
        D0_op: torch.Tensor,
        hedef_tokens: torch.Tensor,
        L_arc: torch.Tensor,
        N_ste: torch.Tensor,
    ) -> torch.Tensor:

        d_min = min(q_son.shape[-1], a_son.shape[-1])
        qa_ahenk = F.cosine_similarity(q_son[..., :d_min], a_son[..., :d_min], dim=-1)

        c_defect_cumle = kontratlar.d0_transpoze_carp(x_son, D0_op)
        c_kusur_norm = torch.norm(c_defect_cumle, p=2, dim=-1)

        olcek = max(1.0, float(D0_op.shape[0]) ** 0.5)
        topolojik_keyfiyet = torch.exp(-c_kusur_norm / olcek)

        N_hedef = float(hedef_tokens.shape[1])
        kapasite_uyumu = torch.exp(-0.05 * torch.abs(N_ste - N_hedef))
        if kapasite_uyumu.dim() == 0:
            kapasite_uyumu = kapasite_uyumu.expand_as(qa_ahenk)

        cumle_keyfiyet_skoru = qa_ahenk * topolojik_keyfiyet * kapasite_uyumu

        kayip_vec = 1.0 - cumle_keyfiyet_skoru
        return kayip_vec

class Riyazi_AgirlikIlkleyici:
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

HF_YOL_ONEKI = "hf://"
TOKEN_DEPOSU_ONEKI = "tokendepo://"

def hf_kaydini_metne_cevir(kayit: Any) -> str:
    if isinstance(kayit, str):
        return kayit
    if not isinstance(kayit, dict):
        return str(kayit)

    for sohbet_alani in ("messages", "conversations", "conversation"):
        mesajlar = kayit.get(sohbet_alani)
        if isinstance(mesajlar, list) and mesajlar:
            parcalar = []
            for m in mesajlar:
                if isinstance(m, dict):
                    rol = m.get("role") or m.get("from") or ""
                    icerik = m.get("content") or m.get("value") or ""
                    parcalar.append(f"{rol}: {icerik}" if rol else str(icerik))
                else:
                    parcalar.append(str(m))
            return "\n".join(parcalar)

    sirali_alanlar = (
        "description", "problem", "question", "instruction", "prompt",
        "text", "content", "body", "solution", "answer", "response",
        "code", "output",
    )
    parcalar = []
    for alan in sirali_alanlar:
        deger = kayit.get(alan)
        if isinstance(deger, str) and deger.strip():
            parcalar.append(deger)
    if parcalar:
        return "\n\n".join(parcalar)

    try:
        return json.dumps(kayit, ensure_ascii=False)
    except Exception:
        return str(kayit)

class Egitim_TopolojikVeriYukleyici:
    def __init__(self, config: Model_TopolojikKonfigurasyon, manifest_yolu: str = "/kaggle/working/verisetleri_manifest.json"):
        self.config = config
        self.manifest_yolu = manifest_yolu
        self.verisetleri: Dict[str, Dict[str, List[str]]] = {}
        self.hf_tanimlari: Dict[str, Dict[str, Any]] = {}
        self.ertelenmis_git_listesi: List[Any] = []
        self.token_deposu = None
        self.git_onbellek_dizini: str = "/tmp/mucit_git_kaynaklari"
        self.tarama_yap()

    def ertelenmis_git_kaynaklarini_yukle(self) -> Dict[str, Dict[str, List[str]]]:
        if not self.ertelenmis_git_listesi:
            return {}

        logger.info(
            f"  [Git Kaynağı] Yerel veri setleri bitti; {len(self.ertelenmis_git_listesi)} "
            f"ertelenmiş git kaynağı şimdi çekiliyor."
        )
        yollar = self.git_kaynaklarini_getir(
            self.ertelenmis_git_listesi, self.git_onbellek_dizini
        )
        self.ertelenmis_git_listesi = []

        st_extensions = ('.txt', '.md', '.json', '.py', '.c', '.cpp', '.h', '.csv', '.yaml', '.yml')
        yeni: Dict[str, Dict[str, List[str]]] = {}
        for idx, yol in enumerate(yollar):
            veriseti_adi = f"veriseti_git_{idx + 1}_" + os.path.basename(os.path.normpath(yol))
            yeni[veriseti_adi] = {}
            for root, _dirs, files in os.walk(yol):
                gecerli = [
                    os.path.normpath(os.path.join(root, f))
                    for f in files if f.endswith(st_extensions)
                ]
                if gecerli:
                    yeni[veriseti_adi][os.path.normpath(root)] = gecerli
            if not yeni[veriseti_adi]:
                del yeni[veriseti_adi]
        return yeni

    def git_kaynaklarini_getir(self, git_listesi: List[Any], onbellek_dizini: str) -> List[str]:
        indirilen_yollar: List[str] = []
        os.makedirs(onbellek_dizini, exist_ok=True)

        for ham in git_listesi:
            if isinstance(ham, str):
                tanim: Dict[str, Any] = {"url": ham}
            elif isinstance(ham, dict) and ham.get("url"):
                tanim = dict(ham)
            else:
                logger.warning(f"  [Git Kaynağı] Tanınmayan girdi atlandı: {ham!r}")
                continue

            url = tanim["url"]
            ad = tanim.get("ad") or os.path.basename(url.rstrip("/")).replace(".git", "")
            hedef = os.path.join(onbellek_dizini, ad)
            alt_klasor = tanim.get("alt_klasor")

            if os.path.isdir(os.path.join(hedef, ".git")):
                logger.info(f"  [Git Kaynağı] '{ad}' zaten indirilmiş, yeniden çekilmiyor: {hedef}")
            else:
                komut = ["git", "clone", "--depth", "1", "--single-branch"]
                if tanim.get("dal"):
                    komut += ["--branch", str(tanim["dal"])]
                komut += [url, hedef]
                logger.info(f"  [Git Kaynağı] İndiriliyor: {url}")
                try:
                    sonuc = subprocess.run(
                        komut, capture_output=True, text=True,
                        timeout=int(tanim.get("zaman_asimi_sn", 900)),
                    )
                except Exception as exc:
                    logger.error(f"  [Git Kaynağı] '{url}' çekilemedi, atlanıyor: {exc}")
                    continue
                if sonuc.returncode != 0:
                    logger.error(
                        f"  [Git Kaynağı] '{url}' çekilemedi (kod {sonuc.returncode}), atlanıyor. "
                        f"Sebep: {sonuc.stderr.strip()[:400]}"
                    )
                    logger.error(
                        "  [Git Kaynağı] Sık görülen sebepler: depo adresi yanlış, depo özel, "
                        "ya da ortamda internet erişimi kapalı."
                    )
                    continue

            tarama_koku = os.path.join(hedef, alt_klasor) if alt_klasor else hedef
            if not os.path.isdir(tarama_koku):
                logger.error(f"  [Git Kaynağı] '{ad}' içinde alt klasör bulunamadı: {tarama_koku}")
                continue

            try:
                toplam_bayt = sum(
                    os.path.getsize(os.path.join(k, f))
                    for k, _, dosyalar in os.walk(tarama_koku)
                    for f in dosyalar
                    if os.path.isfile(os.path.join(k, f))
                )
                logger.info(
                    f"  [Git Kaynağı] '{ad}' hazır: {tarama_koku} "
                    f"({toplam_bayt / (1024 ** 2):.1f} MB)"
                )
            except OSError:
                pass

            indirilen_yollar.append(tarama_koku)

        return indirilen_yollar

    def _hf_sanal_yol(self, tanim: Dict[str, Any]) -> str:
        return (
            f"{HF_YOL_ONEKI}{tanim['depo']}"
            f"|{tanim.get('yapilandirma') or '-'}"
            f"|{tanim.get('bolum', 'train')}"
        )

    def hf_verisetlerini_kaydet(self, hf_listesi: List[Any], baslangic_indeksi: int) -> None:
        for idx, ham in enumerate(hf_listesi):
            if isinstance(ham, str):
                tanim: Dict[str, Any] = {"depo": ham}
            elif isinstance(ham, dict) and ham.get("depo"):
                tanim = dict(ham)
            else:
                logger.warning(f"  [HF Veri Seti] Tanınmayan girdi atlandı: {ham!r}")
                continue

            tanim.setdefault("bolum", "train")
            tanim.setdefault("yapilandirma", None)
            tanim.setdefault("azami_ornek", 20000)

            sanal_yol = self._hf_sanal_yol(tanim)
            self.hf_tanimlari[sanal_yol] = tanim

            veriseti_adi = (
                f"veriseti_{baslangic_indeksi + idx + 1}_hf_"
                + str(tanim["depo"]).replace("/", "_")
            )
            self.verisetleri[veriseti_adi] = {HF_YOL_ONEKI.rstrip(":/"): [sanal_yol]}
            logger.info(
                f"  [HF Veri Seti] Kuyruğa alındı: {tanim['depo']} "
                f"(bölüm={tanim['bolum']}, azami örnek={tanim['azami_ornek']}, "
                f"akış modu — diske indirme YOK)"
            )

    def tarama_yap(self):
        klasorler_veya_dosyalar = []
        hf_listesi: List[Any] = []
        if os.path.exists(self.manifest_yolu):
            try:
                with open(self.manifest_yolu, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)
                    klasorler_veya_dosyalar = manifest_data.get("verisetleri", [])
                    hf_listesi = manifest_data.get("huggingface_verisetleri", [])
                    git_listesi = manifest_data.get("git_verisetleri", [])
                    git_onbellek = manifest_data.get(
                        "git_onbellek_dizini", "/tmp/mucit_git_kaynaklari"
                    )
                logger.info(f"Manifest dosyasından {len(klasorler_veya_dosyalar)} veri yolu okundu: {self.manifest_yolu}")
                if hf_listesi:
                    logger.info(f"Manifest dosyasından {len(hf_listesi)} HuggingFace veri seti okundu.")
                if git_listesi:
                    logger.info(
                        f"Manifest dosyasından {len(git_listesi)} git kaynağı okundu. "
                        f"İndirme ERTELENDİ: yerel veri setleri bittikten sonra çekilecek, "
                        f"böylece başlangıç gecikmiyor."
                    )
                    self.ertelenmis_git_listesi = list(git_listesi)
                    self.git_onbellek_dizini = git_onbellek
            except Exception as e:
                logger.warning(f"Manifest okunurken hata: {e}")

        if not klasorler_veya_dosyalar:
            klasorler_veya_dosyalar = ["./"]

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

        if manifest_data.get("on_tokenize"):
            self.on_tokenize_deposunu_kur(
                manifest_data.get("token_deposu_yolu", "/tmp/mucit_token_deposu")
            )

        if hf_listesi:
            self.hf_verisetlerini_kaydet(hf_listesi, len(klasorler_veya_dosyalar))

    def _adim_metni_uzunlugu(self) -> int:
        return max(int(getattr(self.config, 'N', 1024)), 1)

    def _metni_adim_dilimlerine_ayir(self, metin: str) -> List[str]:
        adim_uzunlugu = self._adim_metni_uzunlugu()
        return [
            metin[i:i + adim_uzunlugu]
            for i in range(0, len(metin), adim_uzunlugu)
        ]

    def on_tokenize_deposunu_kur(self, depo_yolu: str) -> None:
        from tokenli_veri_deposu import TokenliVeriDeposuInsaEdici, TokenliVeriDeposuOkuyucu

        yerel_dosyalar = [
            d
            for klasorler in self.verisetleri.values()
            for dosyalar in klasorler.values()
            for d in dosyalar
            if not str(d).startswith(HF_YOL_ONEKI)
        ]
        if not yerel_dosyalar:
            logger.info("  [Token Deposu] Ön-tokenize edilecek yerel dosya yok, atlandı.")
            return

        tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
        insa = TokenliVeriDeposuInsaEdici(depo_yolu, tokenizer, self.config.V_size)

        if insa.guncel_mi(yerel_dosyalar):
            logger.info(
                f"  [Token Deposu] Mevcut depo güncel ({len(yerel_dosyalar)} kaynak dosya), "
                f"yeniden tokenize edilmiyor: {depo_yolu}{'.bin'}"
            )
        else:
            logger.info(
                f"  [Token Deposu] {len(yerel_dosyalar)} yerel dosya tek seferde tokenize "
                f"edilip indeksli ikili depoya yazılıyor..."
            )
            insa.insa_et(yerel_dosyalar)

        try:
            self.token_deposu = TokenliVeriDeposuOkuyucu(depo_yolu)
        except Exception as exc:
            logger.error(
                f"  [Token Deposu] Depo açılamadı, klasik metin okuma yoluna dönülüyor: {exc}"
            )
            return

        self.verisetleri = {
            ad: kl
            for ad, kl in self.verisetleri.items()
            if any(str(d).startswith(HF_YOL_ONEKI) for dosyalar in kl.values() for d in dosyalar)
        }
        self.verisetleri["veriseti_0_tokenli_depo"] = {
            "tokenli_depo": [f"{TOKEN_DEPOSU_ONEKI}{depo_yolu}"]
        }
        logger.info(
            f"  [Token Deposu] Yerel dosyalar tek bir mmap depoya indirgendi; "
            f"{self.token_deposu.pencere_sayisi(self._adim_metni_uzunlugu()):,} adet "
            f"tam dolu {self._adim_metni_uzunlugu()}-token penceresi hazır."
        )

    def token_deposu_pencereleri_oku(self, depo_yolu: str):
        from tokenli_veri_deposu import TokenliVeriDeposuOkuyucu

        okuyucu = getattr(self, "token_deposu", None)
        if okuyucu is None:
            okuyucu = TokenliVeriDeposuOkuyucu(depo_yolu)

        tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
        N = self._adim_metni_uzunlugu()
        toplam_bayt = okuyucu.toplam_token * 4
        okunan = 0
        idx = 0

        for pencere, son_mu in okuyucu.pencereler(N):
            idler = [int(t) for t in pencere]
            try:
                metin = tokenizer.decode(idler)
            except Exception:
                metin = ""
            idx += 1
            okunan += N * 4
            yield (
                metin,
                self._token_penceresini_tensore_cevir(idler),
                son_mu, idx, okunan, toplam_bayt,
            )

    def token_pencerelerine_ayir(self, metin: str, artik: List[int]) -> Tuple[List[Tuple[str, List[int]]], List[int]]:
        tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
        N = self._adim_metni_uzunlugu()

        tokenlar = artik + tokenizer.encode(metin)
        pencereler: List[Tuple[str, List[int]]] = []

        i = 0
        while i + N <= len(tokenlar):
            pencere = tokenlar[i:i + N]
            try:
                pencere_metni = tokenizer.decode(pencere)
            except Exception:
                pencere_metni = ""
            pencereler.append((pencere_metni, pencere))
            i += N

        return pencereler, tokenlar[i:]

    def _token_penceresini_tensore_cevir(self, token_ids: List[int]) -> torch.Tensor:
        N = self._adim_metni_uzunlugu()
        if len(token_ids) < N:
            token_ids = token_ids + [0] * (N - len(token_ids))
        else:
            token_ids = token_ids[:N]
        token_ids = [t % self.config.V_size for t in token_ids]
        return torch.tensor(
            [token_ids] * self.config.batch_size,
            dtype=torch.long,
            device=self.config.device,
        )

    def _metni_hedef_tensore_cevir(self, metin: str) -> torch.Tensor:
        tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
        token_ids = tokenizer.encode(metin)
        if len(token_ids) < self.config.N:
            token_ids = token_ids + [0] * (self.config.N - len(token_ids))
        else:
            token_ids = token_ids[:self.config.N]
        token_ids = [t % self.config.V_size for t in token_ids]
        return torch.tensor(
            [token_ids] * self.config.batch_size,
            dtype=torch.long,
            device=self.config.device,
        )

    def hf_parcalari_oku(self, sanal_yol: str, chunk_size: int = 65536):
        tanim = self.hf_tanimlari.get(sanal_yol)
        if tanim is None:
            logger.warning(f"  [HF Veri Seti] Tanım bulunamadı: {sanal_yol}")
            return

        depo = tanim["depo"]
        try:
            from datasets import load_dataset
        except ImportError:
            logger.error(
                f"  [HF Veri Seti] '{depo}' atlanıyor: 'datasets' kütüphanesi kurulu değil. "
                f"Kurmak için: pip install datasets"
            )
            return

        try:
            akis = load_dataset(
                depo,
                tanim.get("yapilandirma") or None,
                split=tanim.get("bolum", "train"),
                streaming=True,
            )
        except Exception as exc:
            logger.error(
                f"  [HF Veri Seti] '{depo}' AÇILAMADI, bu veri seti atlanıyor (eğitim devam ediyor). "
                f"Sebep: {exc}"
            )
            logger.error(
                "  [HF Veri Seti] Sık görülen sebepler: veri seti adı yanlış, veri seti kapılı "
                "(gated) ve HF_TOKEN gerekiyor, ya da ortamda internet erişimi kapalı "
                "(Kaggle'da not defteri ayarlarından internet açılmalı)."
            )
            return

        azami_ornek = int(tanim.get("azami_ornek", 20000))
        tampon: List[str] = []
        tampon_uzunlugu = 0
        bytes_read = 0
        chunk_idx = 0
        islenen_ornek = 0

        def _parca_uret(metin: str, son: bool):
            nonlocal bytes_read, chunk_idx
            bytes_read += len(metin.encode('utf-8', errors='ignore'))
            chunk_idx += 1
            return metin, self._metni_hedef_tensore_cevir(metin), son, chunk_idx, bytes_read, 0

        bekleyen: Optional[str] = None
        adim_uzunlugu = self._adim_metni_uzunlugu()
        birikim = ""

        try:
            for kayit in akis:
                if islenen_ornek >= azami_ornek:
                    break
                islenen_ornek += 1

                metin = hf_kaydini_metne_cevir(kayit)
                if not metin or not metin.strip():
                    continue

                birikim += ("\n\n" if birikim else "") + metin

                while len(birikim) >= adim_uzunlugu:
                    dilim = birikim[:adim_uzunlugu]
                    birikim = birikim[adim_uzunlugu:]
                    if bekleyen is not None:
                        yield _parca_uret(bekleyen, False)
                    bekleyen = dilim
        except Exception as exc:
            logger.error(
                f"  [HF Veri Seti] '{depo}' akışı sırasında hata, bu veri seti sonlandırılıyor: {exc}"
            )

        if birikim.strip():
            if bekleyen is not None:
                yield _parca_uret(bekleyen, False)
            bekleyen = birikim

        if bekleyen is not None:
            yield _parca_uret(bekleyen, True)

        logger.info(
            f"  [HF Veri Seti] '{depo}' tamamlandı: {islenen_ornek} örnek, "
            f"{bytes_read / (1024 ** 2):.1f} MB metin akıtıldı (diske indirilmedi)."
        )

    def dosya_parcalari_oku(self, dosya_yolu: str, chunk_size: int = 65536):
        if str(dosya_yolu).startswith(TOKEN_DEPOSU_ONEKI):
            yield from self.token_deposu_pencereleri_oku(
                str(dosya_yolu)[len(TOKEN_DEPOSU_ONEKI):]
            )
            return

        if str(dosya_yolu).startswith(HF_YOL_ONEKI) or str(dosya_yolu).startswith("hf:/"):
            anahtar = dosya_yolu if dosya_yolu in self.hf_tanimlari else str(dosya_yolu).replace("hf:/", HF_YOL_ONEKI, 1)
            yield from self.hf_parcalari_oku(anahtar, chunk_size=chunk_size)
            return

        try:
            file_size = os.path.getsize(dosya_yolu)
        except Exception:
            file_size = 0

        bytes_read = 0
        chunk_idx = 0
        bekleyen: Optional[Tuple[str, List[int]]] = None
        artik_tokenlar: List[int] = []

        try:
            with open(dosya_yolu, 'r', encoding='utf-8', errors='ignore') as f:
                while True:
                    blok = f.read(chunk_size)
                    if not blok:
                        break

                    pencereler, artik_tokenlar = self.token_pencerelerine_ayir(blok, artik_tokenlar)
                    for pencere in pencereler:
                        if bekleyen is not None:
                            bytes_read += len(bekleyen[0].encode('utf-8', errors='ignore'))
                            chunk_idx += 1
                            yield (
                                bekleyen[0],
                                self._token_penceresini_tensore_cevir(bekleyen[1]),
                                False, chunk_idx, bytes_read, file_size,
                            )
                        bekleyen = pencere
        except Exception as e:
            logger.warning(f"Dosya okuma hatası ({dosya_yolu}): {e}")

        if artik_tokenlar:
            tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
            try:
                artik_metin = tokenizer.decode(artik_tokenlar)
            except Exception:
                artik_metin = ""
            if bekleyen is not None:
                bytes_read += len(bekleyen[0].encode('utf-8', errors='ignore'))
                chunk_idx += 1
                yield (
                    bekleyen[0],
                    self._token_penceresini_tensore_cevir(bekleyen[1]),
                    False, chunk_idx, bytes_read, file_size,
                )
            bekleyen = (artik_metin, artik_tokenlar)

        if bekleyen is not None:
            bytes_read += len(bekleyen[0].encode('utf-8', errors='ignore'))
            chunk_idx += 1
            yield (
                bekleyen[0],
                self._token_penceresini_tensore_cevir(bekleyen[1]),
                True, chunk_idx, bytes_read, file_size,
            )

    def dosya_okumu_yap(self, dosya_yolu: str) -> Tuple[str, torch.Tensor]:
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
    takas_mgr: Optional[Any] = None,
    arc_donusturucu: Optional[Any] = None
) -> Tuple[float, float, float, float]:
    optimizer.zero_grad(set_to_none=True)

    kontratlar.tahliye_sayaclarini_sifirla()
    if torch.cuda.is_available():
        _devreden_mb = torch.cuda.memory_allocated() / (1024 ** 2)
        if _devreden_mb > 512.0:
            logger.warning(
                f"  [Adım Başı Devreden Bellek] Adım {current_step} daha başlamadan "
                f"{_devreden_mb:.1f} MB VRAM dolu — önceki adımdan taşınan bellek var."
            )

    _takas_cm = takas_mgr.kapsam_muhafizi_aktifles() if takas_mgr is not None else None
    if _takas_cm is not None:
        _takas_cm.__enter__()

    n1_byte = tum_moduller['n1_byte']
    n2_topox = tum_moduller['n2_topox']
    n3_lif = tum_moduller['n3_lif']
    n4_sorgu = tum_moduller['n4_sorgu']
    n5_cevap = tum_moduller['n5_cevap']
    n6_aktor = tum_moduller['n6_aktor']
    n7_cozucu = tum_moduller['n7_cozucu']
    n8_chebyshev = tum_moduller['n8_chebyshev']
    n8_b_uzunluk = tum_moduller['n8_b_uzunluk']
    n9_vandermonde = tum_moduller['n9_vandermonde']
    n10_sozluk = tum_moduller['n10_sozluk']
    meclis_bellek = tum_moduller['bellek_yonetici']
    bellek_yazici = tum_moduller['n_yazici']

    sistem_yapilandirmasi = SistemYapilandirmasi(
        batch_boyutu=getattr(config, 'batch_size', 1),
        gizil_boyut=getattr(config, 'd_v', 32),
        sorgu_boyutu=getattr(config, 'd_q', 64),
        cevap_boyutu=getattr(config, 'd_a', 64),
        sentetik_durum_boyutu=getattr(config, 'd_h', 64),
        bellek_koleksiyon_boyutu=getattr(config, 'K', 16),
        bellek_vektor_boyutu=getattr(config, 'd_m', 64),
        gomulu_boyut=getattr(config, 'd', 128),
        spektral_cozunurluk=getattr(config, 'M_plus_1', 7),
        hedef_cumle_uzunlugu=getattr(config, 'N', 32),
        sozluk_boyutu=getattr(config, 'V_size', 256),
        rekurens_dongu_sayisi=getattr(config, 'R', 4),
    )
    logger.debug(f"  [SistemYapilandirmasi] Adım {current_step} yapılandırma anlık görüntüsü: {sistem_yapilandirmasi}")

    e1_girdi = E1_HamMetinAkisi(X_text=e1_girdi_metni)

    def vjp_cerrahi_enjekte_et(vector_loss: torch.Tensor, target_params: List[nn.Parameter], scale: float = 1.0, retain_graph: bool = False) -> None:
        trainable_in_group = [p for p in target_params if p.requires_grad]
        if not trainable_in_group:
            return

        temiz_hata = vector_loss.detach()
        temiz_hata = torch.nan_to_num(temiz_hata, nan=0.0, posinf=100.0, neginf=-100.0)
        temiz_hata = torch.clamp(temiz_hata, min=-100.0, max=100.0)

        std_val  = torch.std(temiz_hata, unbiased=False) + 1e-6
        norm_val = torch.norm(temiz_hata) + 1e-6
        v_probe  = scale * (1.0 / std_val) * (temiz_hata / norm_val)

        for p in trainable_params:
            p.grad = None

        try:
            grads = torch.autograd.grad(
                outputs=vector_loss,
                inputs=trainable_in_group,
                grad_outputs=v_probe,
                retain_graph=retain_graph,
                allow_unused=True
            )

            for p, g in zip(trainable_in_group, grads):
                if g is not None:
                    g_clean = torch.nan_to_num(g.detach(), nan=0.0, posinf=1.0, neginf=-1.0)
                    g_norm  = torch.norm(g_clean)
                    if g_norm > 1.0:
                        g_clean = g_clean / (g_norm + 1e-8)

                    p.grad = g_clean.to(device=p.device, dtype=p.dtype)
        except Exception as exc:
            logger.warning(f"  [VJP Cerrahi Uyarısı] Gradyan enjeksiyonu uyarısı: {exc}")

    _shard_saklama_dtype = torch.bfloat16 if torch.cuda.is_available() else None

    def _grad_anlik_kopyala() -> List[torch.Tensor]:
        if _shard_saklama_dtype is None:
            return [
                p.grad.detach().clone() if p.grad is not None else torch.zeros_like(p)
                for p in trainable_params
            ]
        return [
            p.grad.detach().to(_shard_saklama_dtype)
            if p.grad is not None
            else torch.zeros(p.shape, device=p.device, dtype=_shard_saklama_dtype)
            for p in trainable_params
        ]

    AnlasmaliVramGuvencesiAl(n1_byte, e1_girdi, takas_mgr=takas_mgr)
    e2_byte, x_initial = AcilDurumOomYakalayiciVeKurtarici(n1_byte.forward, e1_girdi, modul_nesnesi=n1_byte, takas_mgr=takas_mgr)
    raw_n2_topox = gpu_dagitici.kok_modul_al(n2_topox) if gpu_dagitici is not None else (n2_topox.module if hasattr(n2_topox, 'module') else n2_topox)
    AnlasmaliVramGuvencesiAl(raw_n2_topox, e2_byte, takas_mgr=takas_mgr)
    ham_skor = AcilDurumOomYakalayiciVeKurtarici(
        raw_n2_topox.ham_skor_hesapla, e2_byte, x_initial=x_initial,
        modul_nesnesi=raw_n2_topox, takas_mgr=takas_mgr
    )
    e3_sinir = AcilDurumOomYakalayiciVeKurtarici(
        raw_n2_topox.komsuluk_guncelle, ham_skor, mode='train',
        modul_nesnesi=raw_n2_topox, takas_mgr=takas_mgr
    )
    AnlasmaliVramGuvencesiAl(n3_lif, e3_sinir, takas_mgr=takas_mgr)
    e4_lif = AcilDurumOomYakalayiciVeKurtarici(n3_lif.forward, e3_sinir, x_initial, modul_nesnesi=n3_lif, takas_mgr=takas_mgr)
    vram_denetci.yokla_ve_raporla("N1_N3_TopolojiIskelesi", adim_no=current_step)

    AnlasmaliVramGuvencesiAl(laplasyen_insa, e3_sinir.D1, takas_mgr=takas_mgr)

    D0_op, _ = AcilDurumOomYakalayiciVeKurtarici(
        laplasyen_insa.insa_et, e3_sinir, e4_lif.phi_matrisleri,
        modul_nesnesi=laplasyen_insa, takas_mgr=takas_mgr
    )
    vram_denetci.yokla_ve_raporla("N11_LifLaplasyeniInsa", adim_no=current_step)

    d_vec2 = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.hesapla_uyumsuzluk_vektoru, x_initial, D0_op,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )
    e_vec2 = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.hesapla_dirichlet_enerjisi_vektoru, x_initial, D0_op,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )

    _faz2_hedef_params = list(n3_lif.parameters()) + list(n2_topox.parameters())

    vjp_cerrahi_enjekte_et(d_vec2, _faz2_hedef_params, retain_graph=True)
    g_faz2_uyumsuzluk = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(F.relu(e_vec2), _faz2_hedef_params)
    g_faz2_dirichlet = _grad_anlik_kopyala()

    del D0_op
    import gc as _gc
    _gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    vram_denetci.yokla_ve_raporla("LOCO_Faz2_GrafSilindi", adim_no=current_step)

    GRPO_G = getattr(config, 'GRPO_G', 4)
    x_start_grouped = x_initial.repeat_interleave(GRPO_G, dim=0).detach()
    if gpu_cesitlendirici is not None:
        x_start_grouped = gpu_cesitlendirici.cesitlendir(x_start_grouped, step_seed=current_step)
    elif GRPO_G > 1:

        _noise_std = 0.01
        _D = x_start_grouped.shape[-1]

        _cayley_gerekli_bayt = 5 * _D * _D * x_start_grouped.element_size()
        vram_on_kontrol_ve_nvme_tahliye(_cayley_gerekli_bayt, takas_mgr=takas_mgr)
        try:
            _M_g = torch.randn(_D, _D, device=x_start_grouped.device, dtype=x_start_grouped.dtype)
            _A_g = 0.5 * (_M_g - _M_g.T)
            _I_D = torch.eye(_D, device=x_start_grouped.device, dtype=x_start_grouped.dtype)
            _left  = _I_D - (_noise_std / 2.0) * _A_g
            _right = _I_D + (_noise_std / 2.0) * _A_g
            _cayley = torch.linalg.solve(_left, _right)
        except Exception as _cayley_exc:

            logger.warning(f"[Faz3_CayleyCesitlendirme] Tahsis/çözüm başarısız, kimlik fallback: {_cayley_exc}")
            _cayley = torch.eye(_D, device=x_start_grouped.device, dtype=x_start_grouped.dtype)
        x_start_grouped = torch.matmul(x_start_grouped, _cayley)

    x_current = x_start_grouped.clone().detach()
    e2_byte_grouped = E2_ByteTensoru(byte_tensor=e2_byte.byte_tensor.repeat_interleave(GRPO_G, dim=0))
    hedef_grouped = hedef_tensor.repeat_interleave(GRPO_G, dim=0)
    active_b = x_current.shape[0]

    AnlasmaliVramGuvencesiAl(meclis_bellek, active_b, takas_mgr=takas_mgr)
    M_current = AcilDurumOomYakalayiciVeKurtarici(
        meclis_bellek.get_memory, active_b, modul_nesnesi=meclis_bellek, takas_mgr=takas_mgr
    ).M

    mevcut_durum = E5_A_MevcutGizilDurum(x_r=x_current)

    AnlasmaliVramGuvencesiAl(raw_n2_topox, e2_byte_grouped, takas_mgr=takas_mgr)
    _gecmis_ceza = getattr(raw_n2_topox, '_gecmis_dugum_cezasi', None)
    _gecmis_gamma = getattr(raw_n2_topox, '_gecmis_gamma', None)

    _gruplama_kimlik = (
        GRPO_G == 1
        and gpu_cesitlendirici is None
        and _gecmis_ceza is None
        and _gecmis_gamma is None
    )

    if _gruplama_kimlik:
        ham_skor_sabit = {
            "skorlar": ham_skor["skorlar"].detach(),
            "V": ham_skor["V"],
            "cihaz": ham_skor["cihaz"],
            "dtype": ham_skor["dtype"],
        }
        e3_sinir_sabit = E3_SinirOperatorleri(
            D1=e3_sinir.D1.detach(), D2=e3_sinir.D2.detach()
        )
    else:
        ham_skor_sabit = AcilDurumOomYakalayiciVeKurtarici(
            raw_n2_topox.ham_skor_hesapla, e2_byte_grouped, x_initial=x_start_grouped,
            modul_nesnesi=raw_n2_topox, takas_mgr=takas_mgr
        )
        e3_sinir_sabit = AcilDurumOomYakalayiciVeKurtarici(
            raw_n2_topox.komsuluk_guncelle, ham_skor_sabit, mode='train',
            d_dugum_gecmis=_gecmis_ceza, gamma_gecmis=_gecmis_gamma,
            modul_nesnesi=raw_n2_topox, takas_mgr=takas_mgr
        )
    AnlasmaliVramGuvencesiAl(laplasyen_insa, e3_sinir_sabit.D1, takas_mgr=takas_mgr)

    D0_op_sabit, Delta_0_sabit = AcilDurumOomYakalayiciVeKurtarici(
        laplasyen_insa.insa_et, e3_sinir_sabit, e4_lif.phi_matrisleri,
        modul_nesnesi=laplasyen_insa, takas_mgr=takas_mgr, hesapla_yogun_delta0=False
    )
    if hasattr(laplasyen_insa, 'tasintilar_cihaza') and D0_op_sabit.device != x_start_grouped.device:
        D0_op_sabit, Delta_0_sabit = laplasyen_insa.tasintilar_cihaza(D0_op_sabit, Delta_0_sabit, x_start_grouped.device)
    if hasattr(n6_aktor, 'update_operators'):

        try:
            n6_aktor.update_operators(D0_op_sabit)
        except Exception as _update_ops_exc:
            logger.warning(f"  [N6 update_operators Uyarısı] {_update_ops_exc}")

    sorgu_q_son: Optional[torch.Tensor] = None
    cevap_a_son: Optional[torch.Tensor] = None
    _n7_syn_states_seq_list: List[torch.Tensor] = []

    _E_kenar_mevcut = int(e3_sinir_sabit.D1.shape[0])

    for r in range(1, config.R + 1):

        def _tekil_r_adimi(x_c, m_c, _D0_r=D0_op_sabit, _D1_r=e3_sinir_sabit.D1):
            e5_a_st = E5_A_MevcutGizilDurum(x_r=x_c)
            e5_b_st = E5_B_BellekGonderimi(M=m_c)

            AnlasmaliVramGuvencesiAl(n4_sorgu, x_c, takas_mgr=takas_mgr)
            e6_sorgu_st = AcilDurumOomYakalayiciVeKurtarici(
                n4_sorgu.forward, e5_a_st, D0_operator=_D0_r, A_adjacency=_D1_r, bellek=e5_b_st,
                modul_nesnesi=n4_sorgu, takas_mgr=takas_mgr
            )
            AnlasmaliVramGuvencesiAl(n5_cevap, e6_sorgu_st.q_r, takas_mgr=takas_mgr)
            e7_lokal_st = AcilDurumOomYakalayiciVeKurtarici(n5_cevap.forward, e6_sorgu_st, e5_b_st, modul_nesnesi=n5_cevap, takas_mgr=takas_mgr)

            n6_aktor._hafiza_korelasyon_R = getattr(meclis_bellek, 'R', None)
            AnlasmaliVramGuvencesiAl(n6_aktor, x_c, takas_mgr=takas_mgr)
            e8_sentetik_st = AcilDurumOomYakalayiciVeKurtarici(
                n6_aktor.forward, e5_a_st, e6_sorgu_st, e7_lokal_st, modul_nesnesi=n6_aktor, takas_mgr=takas_mgr
            )
            AnlasmaliVramGuvencesiAl(n7_cozucu, e8_sentetik_st.synthetic_state, takas_mgr=takas_mgr)
            e9_guncel_st = AcilDurumOomYakalayiciVeKurtarici(
                n7_cozucu.forward, e8_sentetik_st, _D0_r, e5_a_st, modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
            )
            return e9_guncel_st.x_next, e8_sentetik_st.synthetic_state, e6_sorgu_st.q_r, e7_lokal_st.a_r

        x_next_val, h_syn_val, q_r_val, a_r_val = checkpoint(
            _tekil_r_adimi,
            x_current,
            M_current,
            use_reentrant=False
        )

        e6_sorgu = E6_GizilSorgu(q_r=q_r_val)
        e7_lokal = E7_LokalBilgi(a_r=a_r_val)
        e8_sentetik = E8_SentetikAraDurum(synthetic_state=h_syn_val)
        e9_guncel = E9_GuncellenmisGizilDurum(x_next=x_next_val)
        e5_b = E5_B_BellekGonderimi(M=M_current)
        sorgu_q_son = e6_sorgu.q_r
        cevap_a_son = e7_lokal.a_r
        _n7_syn_states_seq_list.append(h_syn_val)

        if isinstance(meclis_bellek, SMW_SifirParazit_BellekYoneticisi):
            k_r_key = e6_sorgu.q_r[:, :getattr(config, 'K', 16)] if e6_sorgu.q_r.shape[1] >= getattr(config, 'K', 16) else F.pad(e6_sorgu.q_r, (0, getattr(config, 'K', 16) - e6_sorgu.q_r.shape[1]))
            v_r_val = e7_lokal.a_r
            AnlasmaliVramGuvencesiAl(meclis_bellek, k_r_key, takas_mgr=takas_mgr)
            e5_b_yeni = AcilDurumOomYakalayiciVeKurtarici(
                meclis_bellek.BiyortogonalKorelasyonYaz, k_r=k_r_key, v_r=v_r_val, q_r=e6_sorgu.q_r, a_r=e7_lokal.a_r, modul_nesnesi=meclis_bellek, takas_mgr=takas_mgr
            )
        else:
            AnlasmaliVramGuvencesiAl(bellek_yazici, e9_guncel.x_next, takas_mgr=takas_mgr)
            e5_b_yeni = AcilDurumOomYakalayiciVeKurtarici(
                bellek_yazici.yaz, e9_guncel.x_next, e6_sorgu, e5_b, e7_lokal, modul_nesnesi=bellek_yazici, takas_mgr=takas_mgr
            )

        x_current = e9_guncel.x_next
        M_current = e5_b_yeni.M
        mevcut_durum = E5_A_MevcutGizilDurum(x_r=x_current)

        if N7_N2_MIKRO_ZAMAN_ACIK and r < config.R:
            with torch.no_grad():
                _d_disc_r = n7_cozucu.hesapla_uyumsuzluk_vektoru(x_current.detach(), D0_op_sabit)
                _ceza_r, _gamma_r = N2_TopoXHucreOlusumu.kohomolojik_ceza_hazirla(
                    e3_sinir_sabit.D1, _d_disc_r, getattr(config, 'd_v', 32)
                )

            e3_sinir_sabit = raw_n2_topox.komsuluk_guncelle(
                ham_skor_sabit, mode='train',
                d_dugum_gecmis=_ceza_r, gamma_gecmis=_gamma_r,
            )

            _E_kenar_yeni = int(e3_sinir_sabit.D1.shape[0])
            if _E_kenar_yeni != _E_kenar_mevcut:
                e4_lif = AcilDurumOomYakalayiciVeKurtarici(
                    n3_lif.forward, e3_sinir_sabit, x_start_grouped,
                    modul_nesnesi=n3_lif, takas_mgr=takas_mgr
                )
                _E_kenar_mevcut = _E_kenar_yeni

            D0_op_sabit, Delta_0_sabit = AcilDurumOomYakalayiciVeKurtarici(
                laplasyen_insa.insa_et, e3_sinir_sabit, e4_lif.phi_matrisleri,
                modul_nesnesi=laplasyen_insa, takas_mgr=takas_mgr, hesapla_yogun_delta0=False
            )
            if hasattr(laplasyen_insa, 'tasintilar_cihaza') and D0_op_sabit.device != x_start_grouped.device:
                D0_op_sabit, Delta_0_sabit = laplasyen_insa.tasintilar_cihaza(
                    D0_op_sabit, Delta_0_sabit, x_start_grouped.device
                )
            if hasattr(n6_aktor, 'update_operators'):
                n6_aktor.update_operators(D0_op_sabit)

            logger.debug(
                f"  [N7->N2 Mikro-Zaman] r={r}->{r + 1}: gamma={float(_gamma_r):.6f}, "
                f"kenar sayisi {_E_kenar_mevcut}"
            )

    d_vec3 = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.hesapla_uyumsuzluk_vektoru, mevcut_durum.x_r, D0_op_sabit,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )
    e_vec3 = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.hesapla_dirichlet_enerjisi_vektoru, mevcut_durum.x_r, D0_op_sabit,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )

    _c_defect_ham_faz3 = kontratlar.d0_transpoze_carp(mevcut_durum.x_r, D0_op_sabit)
    _krylov_adjoint_faz3 = AcilDurumOomYakalayiciVeKurtarici(
        n6_aktor.VektorelChebyshevKrylovCozumu, _c_defect_ham_faz3, D0_op_sabit,
        modul_nesnesi=n6_aktor, takas_mgr=takas_mgr, P=5
    )
    _kayip_krylov_tutarlilik_vec = F.mse_loss(
        _krylov_adjoint_faz3, mevcut_durum.x_r.detach(), reduction='none'
    ).mean(dim=-1)
    del _c_defect_ham_faz3

    e15_bellek = E15_GuncellenmisBellekMatrisi(updated_memory=M_current)
    logger.debug(f"  [E15_GuncellenmisBellekMatrisi] Adım {current_step} güncel bellek matrisi normu: {float(e15_bellek.updated_memory.detach().norm().item()):.6f}")

    n7_lambda_max = AcilDurumOomYakalayiciVeKurtarici(
        n7_cozucu.laplasyen_lambda_max, D0_op_sabit,
        modul_nesnesi=n7_cozucu, takas_mgr=takas_mgr
    )
    e18_topoloji = E18_TopolojiDenetimRaporu(
        is_stable=bool(float(n7_lambda_max.detach().item()) < 1e4),
        max_eigenvalue=float(n7_lambda_max.detach().item()),
        spectral_gap=float(e_vec3.mean().detach().item()),
    )
    logger.debug(f"  [E18_TopolojiDenetimRaporu] Adım {current_step}: kararlı={e18_topoloji.is_stable}, lambda_max={e18_topoloji.max_eigenvalue:.6f}, spektral_boşluk={e18_topoloji.spectral_gap:.6f}")

    del _n7_syn_states_seq_list

    _R_norm = float(max(1, config.R))
    _faz3_hedef_params = list(n6_aktor.parameters()) + list(n4_sorgu.parameters()) + list(n5_cevap.parameters())
    vjp_cerrahi_enjekte_et(d_vec3 / _R_norm, _faz3_hedef_params, retain_graph=True)
    g_faz3_uyumsuzluk = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(F.relu(e_vec3) / _R_norm, _faz3_hedef_params, retain_graph=True)
    g_faz3_dirichlet = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(_kayip_krylov_tutarlilik_vec, list(n6_aktor.parameters()) + _faz3_hedef_params)
    g_faz3_krylov = _grad_anlik_kopyala()
    vram_denetci.yokla_ve_raporla("LOCO_Faz3_GrafSilindi", adim_no=current_step)

    e9_guncel_detached = E9_GuncellenmisGizilDurum(x_next=e9_guncel.x_next.detach())
    AnlasmaliVramGuvencesiAl(n8_chebyshev, e9_guncel_detached.x_next, takas_mgr=takas_mgr)
    e10_kulli = AcilDurumOomYakalayiciVeKurtarici(n8_chebyshev.forward, e9_guncel_detached, modul_nesnesi=n8_chebyshev, takas_mgr=takas_mgr)

    AnlasmaliVramGuvencesiAl(n8_b_uzunluk, e10_kulli.C, takas_mgr=takas_mgr)
    N_star_int, H_spec_tensor, N_ste_tensor, delta_n_tensor = AcilDurumOomYakalayiciVeKurtarici(
        n8_b_uzunluk.forward, e10_kulli, cheby_calc,
        modul_nesnesi=n8_b_uzunluk, takas_mgr=takas_mgr
    )
    N_star = N_star_int
    H_spec_val = H_spec_tensor.item()

    _hedef_uzunlugu = int(hedef_grouped.shape[1])
    if N_star > _hedef_uzunlugu:
        logger.debug(
            f"  [Erken Budama] N* {N_star} -> {_hedef_uzunlugu} (hedef uzunluğu). "
            f"N9 ve nedensel süzgeç artık kullanılmayacak {N_star - _hedef_uzunlugu} "
            f"pozisyonu hesaplamıyor."
        )
        N_star = _hedef_uzunlugu

    T_matrix = AcilDurumOomYakalayiciVeKurtarici(cheby_calc.hesapla, N=N_star, takas_mgr=takas_mgr)
    hedef_clamped = torch.clamp(hedef_grouped[:, :N_star], min=0, max=getattr(config, 'V_size', 32000) - 1)
    e13_hedef = E13_HedefTokenDizisi(target_tokens=hedef_clamped)
    logger.debug(f"  [E13_HedefTokenDizisi] Adım {current_step} hedef token dizisi şekli: {tuple(e13_hedef.target_tokens.shape)}")

    AnlasmaliVramGuvencesiAl(n9_vandermonde, (e10_kulli.C.shape[0], N_star), takas_mgr=takas_mgr)
    e11_gomulu = AcilDurumOomYakalayiciVeKurtarici(n9_vandermonde.forward, e10_kulli, T_matrix, modul_nesnesi=n9_vandermonde, takas_mgr=takas_mgr)
    AnlasmaliVramGuvencesiAl(n10_sozluk, e11_gomulu.X_output, takas_mgr=takas_mgr)
    e12_olasilik = AcilDurumOomYakalayiciVeKurtarici(n10_sozluk.forward_sifir_oom_chunking, e11_gomulu, hedefler=hedef_clamped, h_spec=H_spec_tensor, modul_nesnesi=n10_sozluk, takas_mgr=takas_mgr)

    try:
        with torch.no_grad():
            _p_uret = e12_olasilik.P
            _pred_ids = torch.argmax(_p_uret, dim=1)[0].detach().cpu().tolist() if _p_uret.dim() == 3 else []
            _uret_tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
            _uret_metin = _uret_tokenizer.decode([int(t) % getattr(config, 'V_size', 200000) for t in _pred_ids[:16]]) if _pred_ids else ""
            e16_uretim = E16_UretilenMetinCiktisi(generated_text=_uret_metin, token_ids=_pred_ids)
            logger.debug(f"  [E16_UretilenMetinCiktisi] Adım {current_step} model tahmini üretim (ilk 16 token): {e16_uretim.generated_text!r}")
    except Exception as _e16_exc:
        logger.debug(f"  [E16_UretilenMetinCiktisi] Adım {current_step} üretim özeti çıkarılamadı: {_e16_exc}")

    if arc_donusturucu is not None and current_step % 50 == 0:
        try:
            with torch.no_grad():
                izgara_ciktisi = arc_donusturucu.insa_et(e12_olasilik, hedef_boyut=(3, 3))
            logging.getLogger("mucit_ai.main_egitim_dongusu").debug(
                f"[N16_ArcIzgaraDonusturucu] Adım {current_step} tahmini ızgara: {izgara_ciktisi['attempt_1']}"
            )
        except Exception as _n16_exc:
            logging.getLogger("mucit_ai.main_egitim_dongusu").debug(
                f"[N16_ArcIzgaraDonusturucu] Izgara insa hatasi (yoksayildi): {_n16_exc}"
            )

    with torch.no_grad():
        x_start_detached = E9_GuncellenmisGizilDurum(x_next=x_start_grouped.detach())

        AnlasmaliVramGuvencesiAl(n8_chebyshev, x_start_detached.x_next, takas_mgr=takas_mgr)
        e10_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n8_chebyshev.forward, x_start_detached, modul_nesnesi=n8_chebyshev, takas_mgr=takas_mgr)
        AnlasmaliVramGuvencesiAl(n9_vandermonde, (e10_cevapsiz.C.shape[0], N_star), takas_mgr=takas_mgr)
        e11_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n9_vandermonde.forward, e10_cevapsiz, T_matrix, modul_nesnesi=n9_vandermonde, takas_mgr=takas_mgr)

        AnlasmaliVramGuvencesiAl(n10_sozluk, e11_cevapsiz.X_output, takas_mgr=takas_mgr)
        e12_olasilik_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n10_sozluk.forward_sifir_oom_chunking, e11_cevapsiz, hedefler=hedef_clamped, modul_nesnesi=n10_sozluk, takas_mgr=takas_mgr)

    _hesap_cihazi = x_start_grouped.device
    p_target_cevapli = e12_olasilik.P
    if p_target_cevapli.device != _hesap_cihazi:
        p_target_cevapli = p_target_cevapli.to(_hesap_cihazi)
    p_target_cevapsiz = e12_olasilik_cevapsiz.P
    if p_target_cevapsiz.device != _hesap_cihazi:
        p_target_cevapsiz = p_target_cevapsiz.to(_hesap_cihazi)
    kayip_cevapsiz = -torch.log(p_target_cevapsiz + 1e-9).mean(dim=-1)
    kayip_cevapli = -torch.log(p_target_cevapli + 1e-9).mean(dim=-1)

    del e10_cevapsiz, e11_cevapsiz, e12_olasilik_cevapsiz, p_target_cevapsiz, p_target_cevapli
    import gc as _gc_cevapsiz
    _gc_cevapsiz.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    son_q = sorgu_q_son
    son_a = cevap_a_son

    R_q, metrikler_q = AcilDurumOomYakalayiciVeKurtarici(
        odul_motoru.hesapla_aktif_sorgu_odulu,
        q_r=son_q, a_r=son_a, x_context=x_start_grouped,
        kayip_cevapsiz=kayip_cevapsiz, kayip_cevapli=kayip_cevapli, Delta_0=D0_op_sabit,
        modul_nesnesi=odul_motoru, takas_mgr=takas_mgr
    )

    oduller_base = AcilDurumOomYakalayiciVeKurtarici(
        odul_motoru.hesapla, e12_olasilik.P, hedef_grouped[:, :N_star],
        modul_nesnesi=odul_motoru, takas_mgr=takas_mgr
    )

    if oduller_base.device != R_q.device:
        oduller_base = oduller_base.to(R_q.device)
    toplam_oduller = oduller_base + R_q

    kayip_grpo_vec = AcilDurumOomYakalayiciVeKurtarici(
        grpo_kriteri.hesapla_vektor, e12_olasilik.P, hedef_grouped[:, :N_star], toplam_oduller,
        modul_nesnesi=grpo_kriteri, takas_mgr=takas_mgr
    )
    n_target = float(hedef_grouped.shape[1])
    kayip_length = 0.05 * (N_ste_tensor - n_target)**2
    kayip_spektral_vec = (kayip_length + 0.01 * torch.abs(delta_n_tensor).mean()).unsqueeze(0)

    AnlasmaliVramGuvencesiAl(vicreg_kriteri, e11_gomulu.X_output, takas_mgr=takas_mgr)
    (l_var_vec, l_cov_vec, l_rec_vec), metrikler_vicreg = AcilDurumOomYakalayiciVeKurtarici(
        vicreg_kriteri, x=e9_guncel_detached.x_next, z=e11_gomulu.X_output, modul_nesnesi=vicreg_kriteri, takas_mgr=takas_mgr
    )

    del e12_olasilik, e11_gomulu
    import gc as _gc_olasilik
    _gc_olasilik.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

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

    _x_canli = mevcut_durum.x_r.detach()
    e5_a_canli_2 = E5_A_MevcutGizilDurum(x_r=_x_canli)
    e5_b_canli = E5_B_BellekGonderimi(M=M_current.detach())

    e6_sorgu_canli = AcilDurumOomYakalayiciVeKurtarici(
        n4_sorgu.forward, e5_a_canli_2,
        D0_operator=D0_op_sabit, A_adjacency=e3_sinir_sabit.D1, bellek=e5_b_canli,
        modul_nesnesi=n4_sorgu, takas_mgr=takas_mgr
    )
    son_a_detached = cevap_a_son.detach()

    _q_r_canli = e6_sorgu_canli.q_r
    if _q_r_canli.device != son_a_detached.device:
        _q_r_canli = _q_r_canli.to(son_a_detached.device)
    E_sorgu_canli = (_q_r_canli.unsqueeze(1) - son_a_detached.unsqueeze(2)).pow(2).mean(dim=-1)
    vjp_cerrahi_enjekte_et(E_sorgu_canli, list(n4_sorgu.parameters()))
    g_sorgu = _grad_anlik_kopyala()

    e6_sorgu_canli_cumle = AcilDurumOomYakalayiciVeKurtarici(
        n4_sorgu.forward, e5_a_canli_2,
        D0_operator=D0_op_sabit, A_adjacency=e3_sinir_sabit.D1, bellek=e5_b_canli,
        modul_nesnesi=n4_sorgu, takas_mgr=takas_mgr
    )

    AnlasmaliVramGuvencesiAl(n8_b_uzunluk, e10_kulli.C, takas_mgr=takas_mgr)
    _, H_spec_cumle, N_ste_cumle, _ = AcilDurumOomYakalayiciVeKurtarici(
        n8_b_uzunluk.forward, e10_kulli, cheby_calc,
        modul_nesnesi=n8_b_uzunluk, takas_mgr=takas_mgr
    )

    kayip_cumle_keyfiyet_vec = AcilDurumOomYakalayiciVeKurtarici(
        cumle_keyfiyet_motoru.hesapla_vektor,
        q_son=e6_sorgu_canli_cumle.q_r,
        a_son=son_a_detached,
        x_son=_x_canli,
        D0_op=D0_op_sabit,
        hedef_tokens=hedef_grouped,
        L_arc=H_spec_cumle,
        N_ste=N_ste_cumle,
        modul_nesnesi=cumle_keyfiyet_motoru, takas_mgr=takas_mgr
    )
    _cumle_hedef_params = list(n4_sorgu.parameters()) + list(n8_b_uzunluk.parameters())
    vjp_cerrahi_enjekte_et(kayip_cumle_keyfiyet_vec, _cumle_hedef_params)
    g_cumle_keyfiyet = _grad_anlik_kopyala()

    vram_denetci.yokla_ve_raporla("LOCO_Faz4_5_GrafSilindi", adim_no=current_step)

    shard_gradyanlari = [
        g_faz2_uyumsuzluk, g_faz2_dirichlet,
        g_faz3_uyumsuzluk, g_faz3_dirichlet, g_faz3_krylov,
        g_grpo, g_vicreg_var, g_vicreg_cov, g_vicreg_rec,
        g_spektral, g_sorgu, g_cumle_keyfiyet,
    ]
















    dagitik_egitim.shardlari_esitle(shard_gradyanlari)

    _P_toplam = sum(p.numel() for p in trainable_params)
    AnlasmaliVramGuvencesiAl(pareto_pcgrad_operator, (len(shard_gradyanlari), _P_toplam), takas_mgr=takas_mgr)

    _bekleyen_restore = getattr(takas_mgr, "_bekleyen_cihaz_geri_yuklemeleri", None) if takas_mgr is not None else None
    if _bekleyen_restore:
        for _modul, _hedef_cihaz in _bekleyen_restore:
            try:
                _modul.to(_hedef_cihaz)
                _modul._vram_idare_zorunlu_cihaz = _hedef_cihaz
            except Exception as _restore_exc:
                logger.warning(f"  [Cihaz Geri Yükleme] Modül '{_modul}' GPU'ya geri taşınamadı: {_restore_exc}")
        _bekleyen_restore.clear()

    try:
        alpha_pareto = pareto_pcgrad_operator.birlestir_ve_uygula_dagitik_gradyanlar(
            shard_gradyanlari=shard_gradyanlari,
            trainable_params=trainable_params,
            optimizer=optimizer,
            max_norm=1.0
        )
    except (torch.cuda.OutOfMemoryError if hasattr(torch.cuda, "OutOfMemoryError") else RuntimeError) as _pareto_oom:
        logger.warning(f"  [Pareto-PCGrad OOM Kurtarıcı] Gerçek VRAM taşması yakalandı, GPU-içi temizlik sonrası tekrar deneniyor: {_pareto_oom}")
        import gc as _gc2
        _gc2.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
            takas_mgr.temizle(agresif=True)
        alpha_pareto = pareto_pcgrad_operator.birlestir_ve_uygula_dagitik_gradyanlar(
            shard_gradyanlari=shard_gradyanlari,
            trainable_params=trainable_params,
            optimizer=optimizer,
            max_norm=1.0
        )

    del shard_gradyanlari
    del g_faz2_uyumsuzluk, g_faz2_dirichlet, g_faz3_uyumsuzluk, g_faz3_dirichlet, g_faz3_krylov
    del g_grpo, g_vicreg_var, g_vicreg_cov, g_vicreg_rec, g_spektral, g_sorgu, g_cumle_keyfiyet
    import gc as _gc4
    _gc4.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    grad_norm_pareto = math.sqrt(sum((p.grad.norm().item() ** 2 for p in trainable_params if p.grad is not None)))
    adapted_lr = config.lr / (1.0 + 0.01 * grad_norm_pareto)
    for param_group in optimizer.param_groups:
        param_group['lr'] = adapted_lr

    e17_gradyan_paketi = E17_EgitimGradiyantPaketi(step_num=current_step, current_lr=adapted_lr, grad_norm=grad_norm_pareto)
    logger.debug(f"  [E17_EgitimGradiyantPaketi] Adım {e17_gradyan_paketi.step_num}: lr={e17_gradyan_paketi.current_lr:.8f}, grad_norm={e17_gradyan_paketi.grad_norm:.6f}")

    vram_denetci.yokla_ve_raporla("LOCO_Pareto_PCGrad_StepCompleted", adim_no=current_step)

    if hasattr(meclis_bellek, 'detach_memory'):
        meclis_bellek.detach_memory()
    elif hasattr(meclis_bellek, 'M') and meclis_bellek.M is not None:
        meclis_bellek.M = meclis_bellek.M.detach()
        if hasattr(meclis_bellek, 'R') and meclis_bellek.R is not None:
            meclis_bellek.R = meclis_bellek.R.detach()

    _kayip_bileseni_listesi = [
        d_vec2.mean(), F.relu(e_vec2).mean(),
        (d_vec3 / _R_norm).mean(), (F.relu(e_vec3) / _R_norm).mean(),
        _kayip_krylov_tutarlilik_vec.mean(),
        kayip_grpo_vec.mean(), l_var_vec.mean(), l_cov_vec.mean(), l_rec_vec.mean(),
        kayip_spektral_vec.mean(), E_sorgu_canli.mean(), kayip_cumle_keyfiyet_vec.mean(),
    ]
    kayip_val = float(sum(
        float(alpha_pareto[i].detach().item()) * float(_kayip_bileseni_listesi[i].detach().item())
        for i in range(len(_kayip_bileseni_listesi))
    ))

    e14_kayip_metrikleri = E14_SistemKayipMetrikleri(
        total_loss=torch.tensor(kayip_val),
        ce_loss=kayip_grpo_vec.mean().detach(),
        laplacian_loss=(F.relu(e_vec3) / _R_norm).mean().detach(),
        cohomology_loss=(d_vec3 / _R_norm).mean().detach(),
    )
    logger.debug(
        f"  [E14_SistemKayipMetrikleri] Adım {current_step}: toplam={float(e14_kayip_metrikleri.total_loss):.6f}, "
        f"ce={float(e14_kayip_metrikleri.ce_loss):.6f}, laplacian={float(e14_kayip_metrikleri.laplacian_loss):.6f}, "
        f"kohomoloji={float(e14_kayip_metrikleri.cohomology_loss):.6f}"
    )

    raw_n3_lif = gpu_dagitici.kok_modul_al(n3_lif) if gpu_dagitici is not None else (n3_lif.module if hasattr(n3_lif, 'module') else n3_lif)

    try:
        stiefel_izdusurucu.izdüsür(raw_n3_lif.phi_base)
    except (torch.cuda.OutOfMemoryError if hasattr(torch.cuda, "OutOfMemoryError") else RuntimeError) as _stiefel_oom:
        logger.warning(f"  [Stiefel İzdüşüm OOM Kurtarıcı] Gerçek VRAM taşması yakalandı, GPU-içi temizlik sonrası tekrar deneniyor: {_stiefel_oom}")
        import gc as _gc3
        _gc3.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        stiefel_izdusurucu.izdüsür(raw_n3_lif.phi_base)

    raw_n1_byte = gpu_dagitici.kok_modul_al(n1_byte) if gpu_dagitici is not None else (n1_byte.module if hasattr(n1_byte, 'module') else n1_byte)
    raw_n1_byte.izdusur_stiefel()

    d_discrepancy = float(d_vec3.mean().detach().item())
    dirichlet_energy = float(e_vec3.mean().detach().item())

    try:
        _dg = float(
            torch.sum((son_q.detach().float() - son_a_detached.float()) ** 2, dim=-1).mean().item()
        )
        _d_ort = abs(d_discrepancy)
        _e_ort = abs(dirichlet_energy)
        _toplam = _d_ort + _e_ort + 1e-8
        _lambda1 = _d_ort / _toplam
        _lambda2 = _e_ort / _toplam
        _dg_kare = _dg + _lambda1 * _d_ort + _lambda2 * _e_ort

        _onceki_dg = getattr(raw_n1_byte, '_gecmis_d_g_kare', None)
        _aci = raw_n1_byte.geodezik_suzgec_genislet(_dg_kare, _onceki_dg)
        raw_n1_byte._gecmis_d_g_kare = _dg_kare
        if _aci > 0.0:
            logger.debug(
                f"  [N14->N1 Geri Besleme] d_g^2={_dg_kare:.4f} "
                f"(lambda1={_lambda1:.3f}, lambda2={_lambda2:.3f}) -> Haar süzgeç dönme açısı {_aci:.3e}"
            )
    except Exception as _dg_exc:
        logger.debug(f"  [N14->N1 Geri Besleme] Geodezik ceza uygulanamadı, atlandı: {_dg_exc}")

    if not N7_N2_MIKRO_ZAMAN_ACIK:

        _yeni_ceza, _yeni_gamma = N2_TopoXHucreOlusumu.kohomolojik_ceza_hazirla(
            e3_sinir_sabit.D1, d_vec3, getattr(config, 'd_v', 32)
        )
        raw_n2_topox._gecmis_dugum_cezasi = _yeni_ceza
        raw_n2_topox._gecmis_gamma = _yeni_gamma

    if hasattr(n6_aktor, 'serbest_birak_operatorler'):
        _serbest_mb = n6_aktor.serbest_birak_operatorler()
        if _serbest_mb > 64.0:
            logger.info(
                f"  [Adım Sonu Tahliye] N6 üzerindeki D0 operatör tamponu bırakıldı: {_serbest_mb:.1f} MB "
                f"(adımlar arası taşınmıyor)"
            )

    if _takas_cm is not None:
        _takas_cm.__exit__(None, None, None)

        if takas_mgr is not None and hasattr(takas_mgr, "_aktif_kapsam_muhafizi"):
            takas_mgr._aktif_kapsam_muhafizi = None

        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
            takas_mgr.temizle(agresif=True)

    import gc as _gc_adim_sonu
    _gc_adim_sonu.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    _iade_edilen_bayt = kontratlar.cpu_yigin_belleginini_iade_et()
    _adim_sonu_rss = kontratlar.surec_rss_bayt()
    _onceki_taban = getattr(_tekil_egitim_adimi_icra, "_onceki_adim_sonu_rss", 0)
    _tekil_egitim_adimi_icra._onceki_adim_sonu_rss = _adim_sonu_rss
    if _onceki_taban > 0:
        _taban_kayma_mb = (_adim_sonu_rss - _onceki_taban) / (1024 ** 2)
        logger.info(
            f"  [Adım Sonu Taban RAM] Adım {current_step} | RSS: {_adim_sonu_rss / (1024 ** 2):.1f} MB "
            f"| Önceki adım sonuna göre kayma: {_taban_kayma_mb:+.1f} MB "
            f"| malloc_trim ile işletim sistemine iade: {_iade_edilen_bayt / (1024 ** 2):.1f} MB"
        )
    else:
        logger.info(
            f"  [Adım Sonu Taban RAM] Adım {current_step} | RSS: {_adim_sonu_rss / (1024 ** 2):.1f} MB "
            f"| ilk ölçüm, kıyas yok | malloc_trim ile işletim sistemine iade: "
            f"{_iade_edilen_bayt / (1024 ** 2):.1f} MB"
        )

    return kayip_val, H_spec_val, dirichlet_energy, d_discrepancy

def Main_EgitimYurutucu(konfig_yolu: Optional[str] = None, manifest_yolu: str = "/kaggle/working/verisetleri_manifest.json",
                        zorunlu_cihaz: Optional[str] = None) -> None:
    logger.info("================================================================================")
    logger.info("BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS MİMARİSİ EĞİTİM YÜRÜTÜCÜSÜ (ÇOKLU GPU PARALEL DÖNGÜ)")
    logger.info("================================================================================")
    kod_surumu_bildir()
    donanim_hizlandirmasini_uygula()

    if SESSIZ_URETIM_MODU:
        takas_mgr = None
    else:
        takas_mgr = NvmeTakasYoneticisi()

    param_dict = {}
    if konfig_yolu and os.path.exists(konfig_yolu):
        with open(konfig_yolu, 'r', encoding='utf-8') as f:
            param_dict = json.load(f)
        logger.info(f"Konfigürasyon dosyasından yüklendi: {konfig_yolu}")

    config = Model_TopolojikKonfigurasyon(param_dict)
    config.device = zorunlu_cihaz or ("cuda:0" if torch.cuda.is_available() else "cpu")

    GRPO_G = getattr(config, 'GRPO_G', 4)
    logger.info(f"Çalışma Cihazı: {config.device} | GRPO Grup (G): {GRPO_G} | Rekürens (R): {config.R}")

    ckpt_dizini = "/kaggle/working" if os.path.exists("/kaggle/working") else "./checkpoints"
    npz_mgr = NPZCheckpointManager(checkpoint_dir=ckpt_dizini)
    if not dagitik_egitim.ana_surec_mi():
        npz_mgr = SadeceAnaSurecHafiza(npz_mgr)
    n15_yedek_yoneticisi = N15_EgitimKontrolNoktasiYoneticisi(kaydetme_dizini=os.path.join(ckpt_dizini, "n15_tasinabilir_yedek"))
    n16_arc_donusturucu = N16_ArcIzgaraDonusturucu()

    npz_mgr.purge_orphan_checkpoints()
    npz_mgr.load_hafiza_state()

    kanvas_model = BiliselKanvasModeli(config).to(config.device)

    n1_byte = kanvas_model.n1_byte
    n2_topox = kanvas_model.n2_topox
    n3_lif = kanvas_model.n3_lif
    n4_sorgu = kanvas_model.n4_sorgu
    n5_cevap = kanvas_model.n5_cevap
    n6_aktor = kanvas_model.n6_aktor
    n7_cozucu = kanvas_model.n7_cozucu
    n8_chebyshev = kanvas_model.n8_chebyshev
    n8_b_uzunluk = kanvas_model.n8_b_uzunluk
    n9_vandermonde = kanvas_model.n9_vandermonde
    n10_sozluk = kanvas_model.n10_sozluk

    cheby_calc = kanvas_model.cheby_calc
    laplasyen_insa = kanvas_model.laplasyen_insa
    meclis_bellek = kanvas_model.bellek_yonetici
    bellek_yazici = kanvas_model.n_yazici
    odul_motoru = N14_OdulTopolojikDevresmezlikMotoru(config)
    grpo_kriteri = Kayip_GRPO_Kriteri(config)
    cumle_keyfiyet_motoru = Odul_ButunculCumleKeyfiyetMotoru(config)
    stiefel_izdusurucu = N13_StiefelManifolduIzdusumu()
    pareto_pcgrad_operator = Riyazi_Pareto_PCGrad_MGDA_Operator()
    vicreg_kriteri = Kayip_VICReg_UcluBilgiKorunumu().to(config.device)

    veri_yukleyici = Egitim_TopolojikVeriYukleyici(config, manifest_yolu=manifest_yolu)

    tum_moduller = {
        ad: getattr(kanvas_model, ad)
        for ad in (
            'n1_byte', 'n2_topox', 'n3_lif', 'n4_sorgu', 'n5_cevap', 'n6_aktor',
            'n7_cozucu', 'n8_chebyshev', 'n8_b_uzunluk', 'n9_vandermonde',
            'n10_sozluk', 'bellek_yonetici', 'n_yazici',
        )
    }

    _model_tensorleri = set(kanvas_model.state_dict().keys())
    _kaydedilecek_tensorler = {
        f"{_ad}.{_k}" for _ad, _m in tum_moduller.items() for _k in _m.state_dict()
    }
    _kapsanmayan = _model_tensorleri - _kaydedilecek_tensorler
    if _kapsanmayan:
        raise RuntimeError(
            f"Model yapısı ile kaydedilecek modül kümesi örtüşmüyor: {len(_kapsanmayan)} tensör "
            f"hiçbir modüle ait değil ve kontrol noktasına yazılmayacaktı. "
            f"Örnekler: {sorted(_kapsanmayan)[:5]}. "
            f"BiliselKanvasModeli'ne yeni bir alt modül eklendiyse tum_moduller listesine de eklenmelidir."
        )
    logger.info(
        f"  [Yapı Denetimi] Modelin {len(_model_tensorleri)} tensörünün tamamı "
        f"{len(tum_moduller)} modül altında kontrol noktasına yazılacak."
    )

    agirlik_ilkleyici = Riyazi_AgirlikIlkleyici()
    agirlik_ilkleyici.ilkle(list(tum_moduller.values()))

    trainable_params = []
    seen_params = set()
    for m in tum_moduller.values():
        for p in m.parameters():
            if p not in seen_params:
                seen_params.add(p)
                trainable_params.append(p)

    optimizer = hizli_optimizer_kur(trainable_params, lr=config.lr, weight_decay=1e-4)
    logger.info("Tüm Sinir Ağları ve Stiefel Parametreleri Optimizasyona Bağlandı.")

    vram_denetci = Hafiza_Izleyici_ve_VRAM_Denetci(cihaz=config.device, kritik_esik_yuzde=0.85)
    if SESSIZ_URETIM_MODU:
        vram_denetci = SessizVramDenetci(vram_denetci)

    baslangic_step, loss_history = npz_mgr.load_pytorch_model(tum_moduller, optimizer)

    if dagitik_egitim.dagitik_aktif():
        dagitik_egitim.agirliklari_ranktan_yay(list(tum_moduller.values()), kaynak=0)
        logger.info(
            f"  [Dagitik] rank {dagitik_egitim.rank()}: baslangic agirliklari rank 0'dan "
            f"yayinlandi; W_0 tum ranklarda birebir ayni."
        )
    current_step = baslangic_step

    with torch.no_grad():
        n3_lif.phi_base.copy_(stiefel_qr_projection(n3_lif.phi_base.data))

    gc.collect()
    gc.freeze()
    logger.info(
        f"  [GC Dondurma] Model, optimizer ve modul agaci kalici nesle tasindi "
        f"({len(gc.get_objects())} nesne tarama disi). Adim ici gc.collect cagrilari "
        f"artik yalnizca yeni nesneleri tariyor."
    )

    best_loss = min(loss_history) if loss_history else float('inf')
    SAVE_EVERY_N_STEPS = getattr(config, 'save_every_n_steps', 100)
    logger.info(f"Eğitim Başlangıç Adımı (Step): {current_step} | En İyi Kayıp (Best Loss): {best_loss:.6f} | Periyodik Kayıt Sıklığı: {SAVE_EVERY_N_STEPS} Adım")

    MAX_TRAINING_SECONDS = 41400.0
    egitim_baslangic_zamani = time.time()
    global_bytes_processed = 0
    last_logged_500mb_chunk = 0

    toplam_dosya_sayisi = sum(
        len(_dosyalar)
        for _klasorler in veri_yukleyici.verisetleri.values()
        for _dosyalar in _klasorler.values()
    )
    tamamlanan_dosya_sayisi = 0
    atlanan_dosya_sayisi = 0
    toplam_basarisiz_adim = 0
    logger.info(f"Eğitilecek toplam dosya sayısı: {toplam_dosya_sayisi}")

    def _veriseti_akisi():
        nonlocal toplam_dosya_sayisi
        for _ad, _kl in list(veri_yukleyici.verisetleri.items()):
            yield _ad, _kl

        _ek = veri_yukleyici.ertelenmis_git_kaynaklarini_yukle()
        if _ek:
            veri_yukleyici.verisetleri.update(_ek)
            toplam_dosya_sayisi += sum(
                len(_dosyalar) for _kl in _ek.values() for _dosyalar in _kl.values()
            )
            logger.info(
                f"  [Git Kaynağı] Kuyruğa {len(_ek)} yeni veri seti eklendi. "
                f"Güncel toplam dosya sayısı: {toplam_dosya_sayisi}"
            )
            for _ad, _kl in _ek.items():
                yield _ad, _kl

    for veriseti_adi, klasorler in _veriseti_akisi():
        tum_veriseti_klasorleri = list(klasorler.keys())
        for klasor_yolu, dosyalar in klasorler.items():
            tum_klasor_dosyalari = dosyalar
            try:
                dosya_boyutlari = [(d, os.path.getsize(d) if os.path.exists(d) else 0) for d in dosyalar]
                dengeli_dagitim = LPT_DosyaDengeliDagitici.dagit(dosya_boyutlari, num_gpus=1)
                dosyalar = dengeli_dagitim[0] if dengeli_dagitim else dosyalar
            except Exception as _lpt_exc:
                logger.debug(f"[LPT_DosyaDengeliDagitici] Dosya dengeleme atlandı (yoksayıldı): {_lpt_exc}")
            for dosya_yolu in dosyalar:

                if npz_mgr.hafiza.is_dosya_islenmis(dosya_yolu, klasor_yolu, veriseti_adi):
                    atlanan_dosya_sayisi += 1
                    logger.info(
                        f"  [Dosya ATLANDI] ({atlanan_dosya_sayisi}. atlama) Zaten eğitilmiş: "
                        f"{os.path.basename(dosya_yolu)}"
                    )
                    continue

                last_logged_pct = -1.0
                dosya_baslangic_step = current_step
                dosya_baslangic_zamani = time.time()
                dosya_kayiplari: List[float] = []
                logger.info(
                    f"  [Dosya BAŞLADI] ({tamamlanan_dosya_sayisi + 1}/{toplam_dosya_sayisi}) "
                    f"{os.path.basename(dosya_yolu)} | Boyut: {os.path.getsize(dosya_yolu) / (1024**2) if os.path.exists(dosya_yolu) else 0.0:.2f} MB "
                    f"| Veri seti: {veriseti_adi}"
                )
                for e1_girdi_metni, hedef_tensor, is_last_chunk, chunk_idx, bytes_read, file_size in dagitik_egitim.pencereleri_bolustur(veri_yukleyici.dosya_parcalari_oku(dosya_yolu, chunk_size=65536)):

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
                            is_best=False,
                            bekle=True
                        )
                        npz_mgr.save_hafiza_state()
                        if takas_mgr is not None and hasattr(takas_mgr, "kapat"):
                            takas_mgr.kapat()
                        logger.info("  [EMNİYET ZAMAN LİMİTİ] Tüm model ve hafıza durumu başarıyla kaydedildi. Oturum emniyetle kapatılıyor.")
                        logger.info("================================================================================")
                        return

                    epoch_baslangic = time.time()

                    try:
                        curr_loss_val, H_spec_val, dirichlet_energy, d_discrepancy = _tekil_egitim_adimi_icra(
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
                            takas_mgr=takas_mgr,
                            arc_donusturucu=n16_arc_donusturucu
                        )
                    except Exception as _adim_exc:
                        toplam_basarisiz_adim += 1
                        logger.error("=" * 80)
                        logger.error(
                            f"EĞİTİM DURDURULDU: Adım {current_step} başarısız oldu. "
                            f"Chunk ATLANMIYOR, yeniden DENENMİYOR."
                        )
                        logger.error(
                            f"Gerekçe: bir adım kurtarılamıyorsa aynı işi tekrar denemek ya da chunk atlayıp "
                            f"devam etmek eğitimi ilerletmez; yalnızca ilerliyormuş gibi gösterir. "
                            f"Adım sayacı {current_step} değerinde ve model bu chunk'tan hiçbir şey öğrenmedi."
                        )
                        logger.error(f"Dosya: {os.path.basename(dosya_yolu)} | Veri seti: {veriseti_adi}")
                        logger.error(f"Hata: {_adim_exc}")
                        logger.error(
                            "Çare: config.azami_dugum_sayisi, config.batch_size veya config.GRPO_G "
                            "değerlerini düşürün."
                        )
                        logger.error("=" * 80)

                        if takas_mgr is not None and hasattr(takas_mgr, "guvenli_kapat_varsa"):
                            takas_mgr.guvenli_kapat_varsa()
                        optimizer.zero_grad(set_to_none=True)
                        try:
                            npz_mgr.save_hafiza_state()
                        except Exception:
                            pass
                        if takas_mgr is not None and hasattr(takas_mgr, "kapat"):
                            takas_mgr.kapat()
                        gc.collect()
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                        raise

                    current_step += 1

                    dosya_kayiplari.append(curr_loss_val)
                    loss_history.append(curr_loss_val)
                    if len(loss_history) > 10:
                        del loss_history[:-10]
                    gecen_sure = time.time() - epoch_baslangic

                    chunk_byte_len = len(e1_girdi_metni.encode('utf-8', errors='ignore'))
                    global_bytes_processed += chunk_byte_len

                    curr_500mb_chunk = global_bytes_processed // (500 * 1024 * 1024)
                    mb_500_crossed = (curr_500mb_chunk > last_logged_500mb_chunk)
                    should_log = mb_500_crossed or (current_step == 1)

                    if should_log or (curr_loss_val < best_loss):
                        mb_processed = global_bytes_processed / (1024 * 1024)
                        logger.info(f"Adım [{current_step}] | Toplam İşlenen Veri: {mb_processed:.1f} MB | Dosya: {os.path.basename(dosya_yolu)} | GRPO Kayıp: {curr_loss_val:.6f} | H_spec: {H_spec_val:.4f} | E(x): {dirichlet_energy:.6f} | Uyumsuzluk: {d_discrepancy:.6f} | Süre: {gecen_sure:.3f} sn")
                        if mb_500_crossed:
                            last_logged_500mb_chunk = curr_500mb_chunk
                    else:
                        logger.debug(f"Adım [{current_step}] | İşlenen Veri: {global_bytes_processed:,} B | Uyumsuzluk: {d_discrepancy:.6f}")

                    if current_step % OZET_ADIM_ARALIGI == 0:
                        durum_ozetini_bas(egitim_parametrelerini_topla(
                            config, trainable_params, current_step, curr_loss_val,
                            ek={
                                'islenen_MB': global_bytes_processed / (1024 * 1024),
                                'H_spec': H_spec_val,
                                'dirichlet_E': dirichlet_energy,
                                'uyumsuzluk_d': d_discrepancy,
                                'adim_suresi_sn': gecen_sure,
                            },
                        ))

                    is_periodic = (current_step % SAVE_EVERY_N_STEPS == 0)
                    is_best = False
                    if curr_loss_val < best_loss:
                        best_loss = curr_loss_val
                        is_best = True

                    if (is_periodic or is_best) and dagitik_egitim.ana_surec_mi():
                        _kaydedilen_npz_yolu = npz_mgr.save_pytorch_model(
                            step=current_step,
                            token_offset=current_step * config.N,
                            model=tum_moduller,
                            optimizer=optimizer,
                            loss_history=loss_history,
                            is_best=is_best,
                            bekle=True
                        )
                        if not _kaydedilen_npz_yolu or not os.path.isfile(_kaydedilen_npz_yolu):
                            raise RuntimeError(
                                f"Adım {current_step}: kontrol noktası diske yazılamadı "
                                f"({_kaydedilen_npz_yolu!r}). Eğitim, kaydedilemeyen bir durumla "
                                f"devam etmez."
                            )

                        optimizer.zero_grad(set_to_none=True)
                        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
                            takas_mgr.temizle(agresif=True)
                        gc.collect()
                        if torch.cuda.is_available():
                            torch.cuda.synchronize()
                            torch.cuda.empty_cache()
                            torch.cuda.ipc_collect()
                        _ckpt_iade_bayt = kontratlar.cpu_yigin_belleginini_iade_et()
                        if _ckpt_iade_bayt > 64 * 1024 * 1024:
                            logger.info(
                                f"  [Ckpt Sonrası CPU Temizliği] Kontrol noktası kaydı/yüklemesinden artan "
                                f"{_ckpt_iade_bayt / (1024 ** 2):.1f} MB yığın belleği işletim sistemine iade edildi."
                            )

                        _yeniden_baslangic_step, _yeniden_loss_history = npz_mgr.load_pytorch_model(tum_moduller, optimizer)
                        if _yeniden_baslangic_step is not None and _yeniden_baslangic_step > 0:
                            current_step = _yeniden_baslangic_step
                        if _yeniden_loss_history:
                            loss_history = _yeniden_loss_history
                        logger.info(
                            f"  [Ckpt Yeniden Yükleme] Adım [{current_step}] kaydedilmiş ağırlıklardan temiz durumla yeniden ilklendirildi."
                        )

                    if is_best:
                        try:
                            n15_yedek_yoneticisi.kaydet(
                                epoch=current_step,
                                model=tum_moduller,
                                optimizer=optimizer,
                                kayip=curr_loss_val,
                                is_master=True
                            )
                        except Exception as _n15_exc:
                            logger.debug(f"[N15_EgitimKontrolNoktasiYoneticisi] Taşınabilir yedek kaydı başarısız (yoksayıldı): {_n15_exc}")

                    if is_last_chunk:
                        npz_mgr.hafiza.dosya_tamamlandi(
                            dosya_yolu=dosya_yolu,
                            klasor_yolu=klasor_yolu,
                            veriseti_adi=veriseti_adi,
                            tum_klasor_dosyalari=tum_klasor_dosyalari,
                            tum_veriseti_klasorleri=tum_veriseti_klasorleri
                        )
                        npz_mgr.save_hafiza_state()

                        tamamlanan_dosya_sayisi += 1
                        dosya_suresi = time.time() - dosya_baslangic_zamani
                        dosya_adim_sayisi = current_step - dosya_baslangic_step
                        _ilk_kayip = dosya_kayiplari[0] if dosya_kayiplari else float('nan')
                        _son_kayip = dosya_kayiplari[-1] if dosya_kayiplari else float('nan')
                        _ort_kayip = (sum(dosya_kayiplari) / len(dosya_kayiplari)) if dosya_kayiplari else float('nan')
                        logger.info(
                            f"  [DOSYA BİTTİ ✓] ({tamamlanan_dosya_sayisi}/{toplam_dosya_sayisi}) "
                            f"{os.path.basename(dosya_yolu)} | Adım: {dosya_adim_sayisi} "
                            f"({dosya_baslangic_step}->{current_step}) | Süre: {dosya_suresi:.1f} sn "
                            f"| Kayıp ilk->son: {_ilk_kayip:.6f} -> {_son_kayip:.6f} (ort {_ort_kayip:.6f}) "
                            f"| İşlenen: {file_size / (1024**2):.2f} MB | Başarısız adım: {toplam_basarisiz_adim} "
                            f"| Veri seti: {veriseti_adi}"
                        )
                        _kalan_dosya = toplam_dosya_sayisi - tamamlanan_dosya_sayisi - atlanan_dosya_sayisi
                        logger.info(
                            f"  [İLERLEME] Tamamlanan: {tamamlanan_dosya_sayisi} | Atlanan: {atlanan_dosya_sayisi} "
                            f"| Kalan: {max(_kalan_dosya, 0)} | Toplam geçen süre: {(time.time() - egitim_baslangic_zamani) / 60.0:.1f} dk"
                        )

                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

                    kaynak_nobetcisi(
                        [ckpt_dizini, "/tmp", getattr(takas_mgr, "swap_dir", None)],
                        baglam=f"adım {current_step} sonu",
                    )

                    if kuresel_ram_denetci.esik_asildi_mi():
                        logger.warning(
                            f"  [Dinamik RAM Denetçi] Sistem RAM eşiği aşıldı "
                            f"(%{int(kuresel_ram_denetci.oran*100)}, {kuresel_ram_denetci.esik_ram_bayt / (1024**3):.2f} GB) — "
                            f"agresif temizlik tetikleniyor."
                        )
                        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
                            takas_mgr.temizle(agresif=True)
                        gc.collect()
                        kontratlar.cpu_yigin_belleginini_iade_et()

    npz_mgr.save_pytorch_model(
        step=current_step,
        token_offset=current_step * config.N,
        model=tum_moduller,
        optimizer=optimizer,
        loss_history=loss_history,
        is_best=False,
        bekle=True
    )

    try:
        npz_mgr.tum_bekleyen_kayitlari_bekle(timeout=60.0)
    except Exception as _bekle_exc:
        logger.warning(f"  [Ckpt Mgr] Bekleyen kayıtlar beklenirken uyarı: {_bekle_exc}")

    try:
        _mevcut_kontrol_noktalari = npz_mgr.list_checkpoints()
        logger.info(f"  [Ckpt Mgr] Diskteki toplam kontrol noktası sayısı: {len(_mevcut_kontrol_noktalari)}")
        for _cn in _mevcut_kontrol_noktalari:
            logger.info(f"    - {_cn['filename']} | {_cn['size_mb']} MB | limit içinde: {_cn['within_limit']}")
    except Exception as _list_exc:
        logger.debug(f"  [Ckpt Mgr] Kontrol noktası listeleme uyarısı: {_list_exc}")

    try:
        npz_mgr.final_model_kopyala_kaggle_working(is_best=True)
    except Exception as _final_kopyala_exc:
        logger.debug(f"  [Ckpt Mgr] Kaggle working kopyalama denemesi atlandı: {_final_kopyala_exc}")

    try:
        _kaggle_uploader = KaggleDatasetUploader(working_dir=ckpt_dizini)
        _kaggle_upload_basarili = _kaggle_uploader.upload(step=current_step, message=f"Final checkpoint step {current_step}")
        if not _kaggle_upload_basarili:
            logger.info("  [Upload] Kaggle veri seti güncellemesi yapılmadı (kimlik bilgisi yok veya CLI hatası) — eğitim normal şekilde sonlandırılıyor.")
    except Exception as _kaggle_exc:
        logger.warning(f"  [Upload] Kaggle uploader beklenmedik hata ile atlandı: {_kaggle_exc}")

    if takas_mgr is not None and hasattr(takas_mgr, "kapat"):
        takas_mgr.kapat()

    logger.info("================================================================================")
    logger.info("EĞİTİM DÖNGÜSÜ VE TÜM VERİ KÜMELERİ BAŞARIYLA TAMAMLANDI")
    logger.info("================================================================================")

if __name__ == "__main__":
    Main_EgitimYurutucu()
