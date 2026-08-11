

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


def kur_logging_sistemi(log_dosyasi: str = 'egitim_dongusu_icra.log') -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.handlers.clear()  

    
    fh = RotatingFileHandler(log_dosyasi, maxBytes=10*1024*1024, backupCount=1, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - (%(name)s) - %(message)s'))
    root.addHandler(fh)

    
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s'))
    root.addHandler(ch)

kur_logging_sistemi()
logger = logging.getLogger('MainEgitim')


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

        
        c_defect_cumle = torch.matmul(x_son, D0_op.T)  
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

class Egitim_TopolojikVeriYukleyici:
    def __init__(self, config: Model_TopolojikKonfigurasyon, manifest_yolu: str = "/kaggle/working/verisetleri_manifest.json"):
        self.config = config
        self.manifest_yolu = manifest_yolu
        self.verisetleri: Dict[str, Dict[str, List[str]]] = {}
        self.tarama_yap()

    def tarama_yap(self):
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

    def dosya_parcalari_oku(self, dosya_yolu: str, chunk_size: int = 65536):
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
    optimizer.zero_grad(set_to_none=True)

    
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
                    
                    p.grad = g_clean
        except Exception as exc:
            logger.warning(f"  [VJP Cerrahi Uyarısı] Gradyan enjeksiyonu uyarısı: {exc}")

    def _grad_anlik_kopyala() -> List[torch.Tensor]:
        return [p.grad.detach().clone() if p.grad is not None else torch.zeros_like(p) for p in trainable_params]

    
    AnlasmaliVramGuvencesiAl(n1_byte, e1_girdi, takas_mgr=takas_mgr)
    e2_byte, x_initial = AcilDurumOomYakalayiciVeKurtarici(n1_byte.forward, e1_girdi, modul_nesnesi=n1_byte, takas_mgr=takas_mgr)
    raw_n2_topox = gpu_dagitici.kok_modul_al(n2_topox) if gpu_dagitici is not None else (n2_topox.module if hasattr(n2_topox, 'module') else n2_topox)
    AnlasmaliVramGuvencesiAl(raw_n2_topox, e2_byte, takas_mgr=takas_mgr)
    e3_sinir = AcilDurumOomYakalayiciVeKurtarici(raw_n2_topox.forward, e2_byte, x_initial=x_initial, mode='train', modul_nesnesi=raw_n2_topox, takas_mgr=takas_mgr)
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
    e3_sinir_sabit = AcilDurumOomYakalayiciVeKurtarici(
        raw_n2_topox.forward, e2_byte_grouped, x_initial=x_start_grouped, mode='train',
        modul_nesnesi=raw_n2_topox, takas_mgr=takas_mgr
    )
    AnlasmaliVramGuvencesiAl(laplasyen_insa, e3_sinir_sabit.D1, takas_mgr=takas_mgr)
    
    
    D0_op_sabit, _ = AcilDurumOomYakalayiciVeKurtarici(
        laplasyen_insa.insa_et, e3_sinir_sabit, e4_lif.phi_matrisleri,
        modul_nesnesi=laplasyen_insa, takas_mgr=takas_mgr
    )
    if hasattr(n6_aktor, 'update_operators'):
        
        
        try:
            n6_aktor.update_operators(D0_op_sabit)
        except Exception as _update_ops_exc:
            logger.warning(f"  [N6 update_operators Uyarısı] {_update_ops_exc}")

    
    sorgu_q_son: Optional[torch.Tensor] = None
    cevap_a_son: Optional[torch.Tensor] = None

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
        
        sorgu_q_son = e6_sorgu.q_r
        cevap_a_son = e7_lokal.a_r
        
        def _tekil_n6_n7_step(x_c, q_c, a_c):
            e5_a_st = E5_A_MevcutGizilDurum(x_r=x_c)
            e6_sorgu_st = E6_GizilSorgu(q_r=q_c)
            e7_lokal_st = E7_LokalBilgi(a_r=a_c)
            AnlasmaliVramGuvencesiAl(n6_aktor, x_c, takas_mgr=takas_mgr)
            
            
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

    
    _R_norm = float(max(1, config.R))
    _faz3_hedef_params = list(n6_aktor.parameters()) + list(n4_sorgu.parameters()) + list(n5_cevap.parameters())
    vjp_cerrahi_enjekte_et(d_vec3 / _R_norm, _faz3_hedef_params, retain_graph=True)
    g_faz3_uyumsuzluk = _grad_anlik_kopyala()
    vjp_cerrahi_enjekte_et(F.relu(e_vec3) / _R_norm, _faz3_hedef_params)
    g_faz3_dirichlet = _grad_anlik_kopyala()
    vram_denetci.yokla_ve_raporla("LOCO_Faz3_GrafSilindi", adim_no=current_step)

    
    e9_guncel_detached = E9_GuncellenmisGizilDurum(x_next=e9_guncel.x_next.detach())
    AnlasmaliVramGuvencesiAl(n8_chebyshev, e9_guncel_detached.x_next, takas_mgr=takas_mgr)
    e10_kulli = AcilDurumOomYakalayiciVeKurtarici(n8_chebyshev.forward, e9_guncel_detached, modul_nesnesi=n8_chebyshev, takas_mgr=takas_mgr)

    
    AnlasmaliVramGuvencesiAl(n8_b_uzunluk, e10_kulli.C, takas_mgr=takas_mgr)
    N_star_int, L_arc_tensor, N_ste_tensor, delta_n_tensor = AcilDurumOomYakalayiciVeKurtarici(
        n8_b_uzunluk.forward, e10_kulli, cheby_calc,
        modul_nesnesi=n8_b_uzunluk, takas_mgr=takas_mgr
    )
    N_star = N_star_int
    L_arc_val = L_arc_tensor.item()
    
    
    T_matrix = AcilDurumOomYakalayiciVeKurtarici(cheby_calc.hesapla, N=N_star, takas_mgr=takas_mgr)
    hedef_clamped = torch.clamp(hedef_grouped[:, :N_star], min=0, max=getattr(config, 'V_size', 32000) - 1)

    
    AnlasmaliVramGuvencesiAl(n9_vandermonde, (e10_kulli.C.shape[0], N_star), takas_mgr=takas_mgr)
    e11_gomulu = AcilDurumOomYakalayiciVeKurtarici(n9_vandermonde.forward, e10_kulli, T_matrix, modul_nesnesi=n9_vandermonde, takas_mgr=takas_mgr)
    AnlasmaliVramGuvencesiAl(n10_sozluk, e11_gomulu.X_output, takas_mgr=takas_mgr)
    e12_olasilik = AcilDurumOomYakalayiciVeKurtarici(n10_sozluk.forward, e11_gomulu, hedefler=hedef_clamped, modul_nesnesi=n10_sozluk, takas_mgr=takas_mgr)

    with torch.no_grad():
        x_start_detached = E9_GuncellenmisGizilDurum(x_next=x_start_grouped.detach())
        
        
        AnlasmaliVramGuvencesiAl(n8_chebyshev, x_start_detached.x_next, takas_mgr=takas_mgr)
        e10_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n8_chebyshev.forward, x_start_detached, modul_nesnesi=n8_chebyshev, takas_mgr=takas_mgr)
        AnlasmaliVramGuvencesiAl(n9_vandermonde, (e10_cevapsiz.C.shape[0], N_star), takas_mgr=takas_mgr)
        e11_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n9_vandermonde.forward, e10_cevapsiz, T_matrix, modul_nesnesi=n9_vandermonde, takas_mgr=takas_mgr)
        
        
        AnlasmaliVramGuvencesiAl(n10_sozluk, e11_cevapsiz.X_output, takas_mgr=takas_mgr)
        e12_olasilik_cevapsiz = AcilDurumOomYakalayiciVeKurtarici(n10_sozluk.forward, e11_cevapsiz, hedefler=hedef_clamped, modul_nesnesi=n10_sozluk, takas_mgr=takas_mgr)

    
    _hesap_cihazi = x_start_grouped.device
    p_target_cevapli = e12_olasilik.P
    if p_target_cevapli.device != _hesap_cihazi:
        p_target_cevapli = p_target_cevapli.to(_hesap_cihazi)
    p_target_cevapsiz = e12_olasilik_cevapsiz.P
    if p_target_cevapsiz.device != _hesap_cihazi:
        p_target_cevapsiz = p_target_cevapsiz.to(_hesap_cihazi)
    kayip_cevapsiz = -torch.log(p_target_cevapsiz + 1e-9).mean(dim=-1)
    kayip_cevapli = -torch.log(p_target_cevapli + 1e-9).mean(dim=-1)

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
    kayip_length = (L_arc_tensor - 0.5 * N_ste_tensor)**2 + 0.05 * (N_ste_tensor - n_target)**2
    kayip_spektral_vec = (kayip_length + 0.01 * torch.abs(delta_n_tensor).mean()).unsqueeze(0)
    
    AnlasmaliVramGuvencesiAl(vicreg_kriteri, e11_gomulu.X_output, takas_mgr=takas_mgr)
    (l_var_vec, l_cov_vec, l_rec_vec), metrikler_vicreg = AcilDurumOomYakalayiciVeKurtarici(
        vicreg_kriteri, x=e9_guncel_detached.x_next, z=e11_gomulu.X_output, modul_nesnesi=vicreg_kriteri, takas_mgr=takas_mgr
    )
    
    
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
    _, L_arc_cumle, N_ste_cumle, _ = AcilDurumOomYakalayiciVeKurtarici(
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
        L_arc=L_arc_cumle,
        N_ste=N_ste_cumle,
        modul_nesnesi=cumle_keyfiyet_motoru, takas_mgr=takas_mgr
    )
    _cumle_hedef_params = list(n4_sorgu.parameters()) + list(n8_b_uzunluk.parameters())
    vjp_cerrahi_enjekte_et(kayip_cumle_keyfiyet_vec, _cumle_hedef_params)
    g_cumle_keyfiyet = _grad_anlik_kopyala()
    

    vram_denetci.yokla_ve_raporla("LOCO_Faz4_5_GrafSilindi", adim_no=current_step)

    
    shard_gradyanlari = [
        g_faz2_uyumsuzluk, g_faz2_dirichlet,
        g_faz3_uyumsuzluk, g_faz3_dirichlet,
        g_grpo, g_vicreg_var, g_vicreg_cov, g_vicreg_rec,
        g_spektral, g_sorgu, g_cumle_keyfiyet,
    ]
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
    del g_faz2_uyumsuzluk, g_faz2_dirichlet, g_faz3_uyumsuzluk, g_faz3_dirichlet
    del g_grpo, g_vicreg_var, g_vicreg_cov, g_vicreg_rec, g_spektral, g_sorgu, g_cumle_keyfiyet
    import gc as _gc4
    _gc4.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    grad_norm_pareto = math.sqrt(sum((p.grad.norm().item() ** 2 for p in trainable_params if p.grad is not None)))
    adapted_lr = config.lr / (1.0 + 0.01 * grad_norm_pareto)
    for param_group in optimizer.param_groups:
        param_group['lr'] = adapted_lr

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
        kayip_grpo_vec.mean(), l_var_vec.mean(), l_cov_vec.mean(), l_rec_vec.mean(),
        kayip_spektral_vec.mean(), E_sorgu_canli.mean(), kayip_cumle_keyfiyet_vec.mean(),
    ]
    kayip_val = float(sum(
        float(alpha_pareto[i].detach().item()) * float(_kayip_bileseni_listesi[i].detach().item())
        for i in range(len(_kayip_bileseni_listesi))
    ))
    
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

    d_discrepancy = float(d_vec3.mean().detach().item())
    dirichlet_energy = float(e_vec3.mean().detach().item())

    if _takas_cm is not None:
        _takas_cm.__exit__(None, None, None)
        
        
        if takas_mgr is not None and hasattr(takas_mgr, "_aktif_kapsam_muhafizi"):
            takas_mgr._aktif_kapsam_muhafizi = None
        
        
        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
            takas_mgr.temizle(agresif=True)

    
    return kayip_val, L_arc_val, dirichlet_energy, d_discrepancy


def Main_EgitimYurutucu(konfig_yolu: Optional[str] = None, manifest_yolu: str = "/kaggle/working/verisetleri_manifest.json", idareci: Optional[Any] = None) -> None:
    
    
    logger.info("================================================================================")
    logger.info("BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS MİMARİSİ EĞİTİM YÜRÜTÜCÜSÜ (ÇOKLU GPU PARALEL DÖNGÜ)")
    logger.info("================================================================================")

    
    takas_mgr = NvmeTakasYoneticisi()
    
    
    param_dict = {}
    if konfig_yolu and os.path.exists(konfig_yolu):
        with open(konfig_yolu, 'r', encoding='utf-8') as f:
            param_dict = json.load(f)
        logger.info(f"Konfigürasyon dosyasından yüklendi: {konfig_yolu}")
        
    config = Model_TopolojikKonfigurasyon(param_dict)
    config.device = "cuda:0" if torch.cuda.is_available() else "cpu"
    
    GRPO_G = getattr(config, 'GRPO_G', 4)
    logger.info(f"Çalışma Cihazı: {config.device} | GRPO Grup (G): {GRPO_G} | Rekürens (R): {config.R}")

    
    ckpt_dizini = "/kaggle/working" if os.path.exists("/kaggle/working") else "./checkpoints"
    npz_mgr = NPZCheckpointManager(checkpoint_dir=ckpt_dizini)

    
    npz_mgr.purge_orphan_checkpoints()
    npz_mgr.load_hafiza_state()

    
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


    agirlik_ilkleyici = Riyazi_AgirlikIlkleyici()
    agirlik_ilkleyici.ilkle(list(tum_moduller.values()))

    
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

    
    baslangic_step, loss_history = npz_mgr.load_pytorch_model(tum_moduller, optimizer)
    current_step = baslangic_step
    
    
    with torch.no_grad():
        n3_lif.phi_base.copy_(stiefel_qr_projection(n3_lif.phi_base.data))
    
    best_loss = min(loss_history) if loss_history else float('inf')
    SAVE_EVERY_N_STEPS = getattr(config, 'save_every_n_steps', 100)
    logger.info(f"Eğitim Başlangıç Adımı (Step): {current_step} | En İyi Kayıp (Best Loss): {best_loss:.6f} | Periyodik Kayıt Sıklığı: {SAVE_EVERY_N_STEPS} Adım")

    
    MAX_TRAINING_SECONDS = 41400.0  
    egitim_baslangic_zamani = time.time()
    global_bytes_processed = 0
    last_logged_500mb_chunk = 0

    for veriseti_adi, klasorler in veri_yukleyici.verisetleri.items():
        tum_veriseti_klasorleri = list(klasorler.keys())
        for klasor_yolu, dosyalar in klasorler.items():
            tum_klasor_dosyalari = dosyalar
            for dosya_yolu in dosyalar:
                
                if npz_mgr.hafiza.is_dosya_islenmis(dosya_yolu, klasor_yolu, veriseti_adi):
                    logger.debug(f"  [Atlandı] Zaten eğitilmiş içerik: {dosya_yolu}")
                    continue

                
                last_logged_pct = -1.0
                for e1_girdi_metni, hedef_tensor, is_last_chunk, chunk_idx, bytes_read, file_size in veri_yukleyici.dosya_parcalari_oku(dosya_yolu, chunk_size=65536):

                    
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
                        logger.info("  [EMNİYET ZAMAN LİMİTİ] Tüm model ve hafıza durumu başarıyla kaydedildi. Oturum emniyetle kapatılıyor.")
                        logger.info("================================================================================")
                        return

                    epoch_baslangic = time.time()

                    
                    try:
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
                    except Exception as _adim_exc:
                        logger.error(
                            f"  [Adım Kurtarıcı] Adım {current_step} kurtarılamaz bir hatayla "
                            f"başarısız oldu, bu chunk ATLANIYOR (eğitim devam ediyor): {_adim_exc}"
                        )
                        if takas_mgr is not None and hasattr(takas_mgr, "guvenli_kapat_varsa"):
                            takas_mgr.guvenli_kapat_varsa()
                        
                        
                        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
                            takas_mgr.temizle(agresif=True)
                        
                        
                        _bekleyen_restore_temizle = getattr(takas_mgr, "_bekleyen_cihaz_geri_yuklemeleri", None) if takas_mgr is not None else None
                        if _bekleyen_restore_temizle:
                            _bekleyen_restore_temizle.clear()
                        optimizer.zero_grad(set_to_none=True)
                        import gc as _gc_step
                        _gc_step.collect()
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                        continue

                    current_step += 1
                    
                    
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
                        logger.info(f"Adım [{current_step}] | Toplam İşlenen Veri: {mb_processed:.1f} MB | Dosya: {os.path.basename(dosya_yolu)} | GRPO Kayıp: {curr_loss_val:.6f} | L_arc: {L_arc_val:.4f} | E(x): {dirichlet_energy:.6f} | Uyumsuzluk: {d_discrepancy:.6f} | Süre: {gecen_sure:.3f} sn")
                        if mb_500_crossed:
                            last_logged_500mb_chunk = curr_500mb_chunk
                    else:
                        logger.debug(f"Adım [{current_step}] | İşlenen Veri: {global_bytes_processed:,} B | Uyumsuzluk: {d_discrepancy:.6f}")

                    
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

                    
                    if is_last_chunk:
                        npz_mgr.hafiza.dosya_tamamlandi(
                            dosya_yolu=dosya_yolu,
                            klasor_yolu=klasor_yolu,
                            veriseti_adi=veriseti_adi,
                            tum_klasor_dosyalari=tum_klasor_dosyalari,
                            tum_veriseti_klasorleri=tum_veriseti_klasorleri
                        )
                        npz_mgr.save_hafiza_state()

                    
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

    
    npz_mgr.save_pytorch_model(
        step=current_step,
        token_offset=current_step * config.N,
        model=tum_moduller,
        optimizer=optimizer,
        loss_history=loss_history,
        is_best=False,
        bekle=True
    )

    logger.info("================================================================================")
    logger.info("EĞİTİM DÖNGÜSÜ VE TÜM VERİ KÜMELERİ BAŞARIYLA TAMAMLANDI")
    logger.info("================================================================================")


if __name__ == "__main__":
    Main_EgitimYurutucu()

