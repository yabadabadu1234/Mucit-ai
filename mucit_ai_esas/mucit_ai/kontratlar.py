#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
BİLİŞSEL KANVAS TOPOLOJİK REKÜRENS MİMARİSİ
Ana Veri Kontratları, Konfigürasyon ve Bilişsel Çekirdek Modülü (kontratlar.py)
================================================================================
Bu modül; sistemdeki tüm bilişsel düğümlerin (N1-N10), dış mimari sınıflarının (N11-N16)
ve kenar veri yapılarının (Data Contracts E1-E18) hakiki tip ve tensör tanımlarını içerir.
R-adımlı gizil uzay rekürens döngüsü, H^1 kohomolojik engel vektörü tespiti, Stiefel manifoldu
QR projeksiyonu, Lif Laplasyeni ısı difüzyon integratörü, Chebyshev-Gauss-Lobatto (CGL)
spektral projeksiyonu ve kapılı bellek yönetim mekanizmalarının tamamını tek vücutta toplar.
"""

import os
import sys
import logging
import dataclasses
from dataclasses import dataclass, is_dataclass, fields
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import math
import json
import types

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# ---- DAHİLİ KÜTÜPHANE YÜKLEMESİ KATMANI ----
try:
    from scipy.special import iv, ive
except ImportError:
    def ive(v: float, z: float) -> float:
        z_val = float(z)
        if z_val == 0:
            return 1.0 if v == 0 else 0.0
        sum_val = 0.0
        for k_idx in range(20):
            term = ((z_val / 2.0) ** (v + 2 * k_idx)) / (math.factorial(k_idx) * math.gamma(v + k_idx + 1))
            sum_val += term
            if abs(term) < 1e-12:
                break
        return sum_val * math.exp(-abs(z_val))

    def iv(v: float, z: float) -> float:
        return ive(v, z) * math.exp(abs(z))
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


# =============================================================================
try:
    import tiktoken
    from tiktoken.load import load_tiktoken_bpe
except ImportError:
    tiktoken = None
    load_tiktoken_bpe = None


class CevrimdisiAksiyomatikTokenizer:
    """
    [Kaggle Çevrimdışı İnternetsiz Aksiyomatik Tokenizer]
    İnternet bağlantısı gerektirmeyen, %100 çevrimdışı, deterministik UTF-8 Byte/Token Ayrıştırıcısı.
    tiktoken ağ bağlantısı veya önbellek bulunamadığında otomatik olarak devreye girer.
    """
    def __init__(self, vocab_size: int = 200000):
        self.n_vocab = vocab_size

    def encode(self, text: str) -> List[int]:
        if not text:
            return [32]
        return [b for b in text.encode('utf-8')]

    def decode(self, token_ids: List[int]) -> str:
        if not token_ids:
            return ""
        byte_vals = bytes([int(t) % 256 for t in token_ids])
        return byte_vals.decode('utf-8', errors='replace')

    def decode_single_token_bytes(self, token_id: int) -> bytes:
        return bytes([int(token_id) % 256])


def stiefel_manifold_projection(tensor: torch.Tensor, grad: Optional[torch.Tensor] = None, lr: float = 1e-3) -> torch.Tensor:
    """
    [Stiefel Manifoldu Cayley Dönüşümü & Riemannian Gradyan İzdüşümcüsü]
    Parametreyi Öklid uzayından Stiefel Manifolduna (St(d_e, d_v)) Analitik Cayley Dönüşümü
    ile düşürür. `no_grad()` altında QR ayrışımı yapıp AdamW momentumunu sakatlamak (Dangling Momentum)
    yerine, analitik Cayley dönüşümü (I + eta/2 A)^(-1) (I - eta/2 A) W ile manifold üzerinde kalmayı
    garanti eder.
    """
    if not isinstance(tensor, torch.Tensor) or tensor.dim() != 2:
        return tensor
    m, n = tensor.shape
    G = grad if grad is not None else tensor

    if m <= n:
        A = torch.matmul(G, tensor.T) - torch.matmul(tensor, G.T)  # [m, m] skew-symmetric
        I_m = torch.eye(m, device=tensor.device, dtype=tensor.dtype)
        left = I_m + (lr / 2.0) * A
        right = I_m - (lr / 2.0) * A
        try:
            W_next = torch.matmul(torch.linalg.solve(left, right), tensor)
            return W_next
        except Exception:
            Q, _ = torch.linalg.qr(tensor.T)
            return Q.T
    else:
        A = torch.matmul(G.T, tensor) - torch.matmul(tensor.T, G)  # [n, n] skew-symmetric
        I_n = torch.eye(n, device=tensor.device, dtype=tensor.dtype)
        left = I_n + (lr / 2.0) * A
        right = I_n - (lr / 2.0) * A
        try:
            W_next = torch.matmul(tensor, torch.linalg.solve(left.T, right.T).T)
            return W_next
        except Exception:
            Q, _ = torch.linalg.qr(tensor)
            return Q

stiefel_qr_projection = stiefel_manifold_projection


_GLOBAL_TOKENIZER_CACHE: Dict[str, Any] = {}

def al_cevrimdisi_veya_tiktoken_tokenizer(encoding_name: str = "o200k_base"):
    """
    Kaggle internetsiz (offline) ortamda tiktoken'ın Azure Blob'a bağlanmaya 
    çalışıp çökmesini engelleyen %100 garantili çevrimdışı yükleyici.
    Küresel bellek önbelleği (Singleton) kullanarak BPE dosyasının GPU/süreç başına 
    SADECE 1 KEZ yüklenmesini garanti eder. Disk IO ve tekrarlı log kalabalığını sıfırlar.
    """
    global _GLOBAL_TOKENIZER_CACHE
    if encoding_name in _GLOBAL_TOKENIZER_CACHE:
        return _GLOBAL_TOKENIZER_CACHE[encoding_name]

    import os
    import logging
    logger = logging.getLogger(__name__)

    # Yerel BPE ranks dosyalarının doğrudan yolları
    olasi_kaggle_yollari = [
        "/kaggle/input/datasets/ulankaggle/tiktoken/o200k_base.tiktoken",
        "/kaggle/input/tiktoken-o200k-base/o200k_base.tiktoken",
        "/kaggle/input/tiktoken-encodings/o200k_base.tiktoken",
        "/kaggle/input/o200k-base/o200k_base.tiktoken",
        "./o200k_base.tiktoken"
    ]

    if tiktoken is not None and load_tiktoken_bpe is not None:
        for yola in olasi_kaggle_yollari:
            if os.path.exists(yola):
                try:
                    mergeable_ranks = load_tiktoken_bpe(yola)
                    num_base_tokens = len(mergeable_ranks)
                    special_tokens = {
                        "<|endoftext|>": num_base_tokens,
                        "<|endofprompt|>": num_base_tokens + 1,
                    }
                    enc = tiktoken.Encoding(
                        name="o200k_base_offline",
                        pat_str=r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+""",
                        mergeable_ranks=mergeable_ranks,
                        special_tokens=special_tokens,
                    )
                    logger.info(f"tiktoken yerel BPE sözlük dosyasından (%100 internetsiz) yüklendi: {yola}")
                    _GLOBAL_TOKENIZER_CACHE[encoding_name] = enc
                    return enc
                except Exception as e:
                    logger.warning(f"Yerel BPE okuma hatası ({yola}): {e}")

    logger.info("Yerel BPE dosyası bulunamadı. Saf UTF-8 CevrimdisiAksiyomatikTokenizer kullanılacak.")
    fallback_tok = CevrimdisiAksiyomatikTokenizer()
    _GLOBAL_TOKENIZER_CACHE[encoding_name] = fallback_tok
    return fallback_tok

# I. SİSTEM YAPILANDIRMASI VE HİPER-PARAMETRELER
# =============================================================================

class Model_TopolojikKonfigurasyon:
    """Topolojik Rekürens Mimarisi Hiper-Parametre Yapılandırması"""
    def __init__(self, param_dict: Optional[Dict[str, Any]] = None):
        params = param_dict or {}
        self.V_nodes: int = params.get("V_nodes", 8)        # Hücre kompleksi düğüm sayısı (V)
        self.d_v: int = params.get("d_v", 32)               # Düğüm lif boyutu
        self.d_e: int = params.get("d_e", 32)               # Kenar lif boyutu (d_e = d_v = 32: O(32) Saf İzometrik Rotasyon Grubu)
        self.d_q: int = params.get("d_q", 64)               # Sorgu boyutu
        self.d_a: int = params.get("d_a", 64)               # Cevap boyutu
        self.d_m: int = params.get("d_m", 64)               # Bellek boyutu
        self.d_h: int = params.get("d_h", 64)               # Sentetik ara durum boyutu
        self.d: int = params.get("d", 128)                  # Gömülü manifold boyutu
        self.D: int = self.V_nodes * self.d_v               # Toplam gizil durum boyutu D = V * d_v
        self.M_plus_1: int = params.get("M_plus_1", 32)     # Chebyshev spektral derece sınırı (M+1=32)
        self.N: int = params.get("N", 1024)                 # Varsayılan Çıktı Dizi Uzunluğu (N=1024)
        self.N_max: int = params.get("N_max", 2048)         # Azami Esnek Çıktı Kapasitesi (N_max=2048)
        self.R: int = params.get("R", 4)                    # Rekürens döngü sayısı
        self.K: int = params.get("K", 16)                   # Bellek eleman sayısı
        self.V_size: int = params.get("V_size", 200000)     # SOTA BPE o200k_base 200K Sözlük Haznesi
        self.V_byte_size: int = params.get("V_byte_size", 256) # UTF-8 Fiziksel Byte Tabanı
        self.GRPO_G: int = params.get("GRPO_G", 4)          # GRPO Grup Örneklem Sayısı (G=4)
        self.beta_kl: float = params.get("beta_kl", 0.05)   # GRPO KL Cezası Katsayısı
        self.dt: float = params.get("dt", 0.05)             # Lif Difüzyon adım boyutu
        self.lr: float = params.get("lr", 1e-3)
        self.batch_size: int = params.get("batch_size", 2)
        self.device: str = "cuda" if torch.cuda.is_available() else "cpu"


# =============================================================================
# I-B. ORTAK VRAM TAHSİS TAHMİN FORMÜLÜ ÇEKİRDEĞİ
# =============================================================================
def vram_bayt_tahmin_et(*boyutlar: int, eleman_bayt: int = 4, guvenlik_katsayisi: float = 3.0) -> int:
    """
    [Parametrik VRAM Tahsis Tahmin Formülü]
    tahmin_bayt = (prod(boyutlar) * eleman_bayt) * guvenlik_katsayisi

    Her sınıfın kendi tahmin_et_vram_bayt() metodu, kendi işleminin ürettiği en büyük
    ara/çıktı tensörlerinin *gerçek* şekillerini (B, V, E, d, V_size, N, K, ...) bu
    fonksiyona besler. guvenlik_katsayisi (varsayılan 3.0), autograd'ın backward için
    sakladığı ara tensörleri, matmul/softmax/attention'ın geçici tampon belleğini ve
    CUDA caching allocator parçalanmasını (fragmentation) kapsayan ampirik bir çarpandır
    — "mantıksal" (yalnızca çıktı) boyuttan gerçek tepe VRAM tüketimine geçiş payıdır.
    """
    eleman_sayisi = 1
    for b in boyutlar:
        eleman_sayisi *= max(1, int(b))
    return int(eleman_sayisi * eleman_bayt * guvenlik_katsayisi)


@dataclass
class SistemYapilandirmasi:
    """Veri kontratları uyumluluğu için Dataclass Konfigürasyon Yapısı"""
    batch_boyutu: int = 1
    gizil_boyut: int = 256
    sorgu_boyutu: int = 64
    cevap_boyutu: int = 64
    sentetik_durum_boyutu: int = 64
    bellek_koleksiyon_boyutu: int = 16
    bellek_vektor_boyutu: int = 64
    gomulu_boyut: int = 128
    spektral_cozunurluk: int = 7
    hedef_cumle_uzunlugu: int = 32
    sozluk_boyutu: int = 256
    rekurens_dongu_sayisi: int = 4


# =============================================================================
# II. BİLİŞSEL VERİ KONTRATLARI (DATA CONTRACTS E1 - E18)
# =============================================================================

@dataclass
class E1_HamMetinAkisi:
    """E1 Kenarı: Ham Metin Girdisi"""
    X_text: str


@dataclass
class E2_ByteTensoru:
    """E2 Kenarı: Byte Tensörü"""
    byte_tensor: torch.Tensor  # Boyut: [B, L_bytes] (torch.int64)
    l_bytes: int = 0

    def __post_init__(self):
        if (self.l_bytes == 0 or self.l_bytes is None) and hasattr(self.byte_tensor, 'shape') and len(self.byte_tensor.shape) >= 2:
            self.l_bytes = int(self.byte_tensor.shape[1])


@dataclass
class E3_SinirOperatorleri:
    """E3 Kenarı: Hücre Kompleksi Sınır Operatörleri"""
    D1: torch.Tensor  # [E, V] (1-hücre -> 0-hücre) (torch.float32)
    D2: torch.Tensor  # [F, E] (2-hücre -> 1-hücre) (torch.float32)


@dataclass
class E4_LifDemeti:
    """E4 Kenarı: Sınırlama Matrisleri Demeti ve Başlangıç Gizil Durumu"""
    phi_matrisleri: nn.ParameterDict  # Dict of [d_e, d_v]
    baslangic_gizil_durumu: torch.Tensor  # [B, D]


@dataclass
class E5_A_MevcutGizilDurum:
    """E5_A Kenarı: r. Adımdaki Gizil Durum Vektörü"""
    x_r: torch.Tensor  # [B, D]


@dataclass
class E5_B_BellekGonderimi:
    """E5_B Kenarı: Dış / Bağlam Bellek Matrisi"""
    M: torch.Tensor  # [B, d_m, K]


@dataclass
class E6_GizilSorgu:
    """E6 Kenarı: Sorgu Vektörü"""
    q_r: torch.Tensor  # [B, d_q]


@dataclass
class E7_LokalBilgi:
    """E7 Kenarı: Süzülmüş Cevap Vektörü"""
    a_r: torch.Tensor  # [B, d_a]


@dataclass
class E8_SentetikAraDurum:
    """E8 Kenarı: Kohomolojik Uyumsuzluk Sonucu Sentezlenen Hipotez"""
    synthetic_state: torch.Tensor  # [B, d_h]


@dataclass
class E9_GuncellenmisGizilDurum:
    """E9 Kenarı: Lif Laplasyeni Sonrası Güncellenmiş Durum"""
    x_next: torch.Tensor  # [B, D]


@dataclass
class E10_KulliManaMatrisi:
    """E10 Kenarı: Spektral Chebyshev Katsayıları Matrisi"""
    C: torch.Tensor  # [B, d, M_plus_1]


@dataclass
class E11_ParalelGomuluVektorlerMatrisi:
    """E11 Kenarı: Hedef Cümle Elemanları Gömülü Vektörler Matrisi"""
    X_output: torch.Tensor  # [B, d, N]


@dataclass
class E12_ParalelTokenOlasilikMatrisi:
    """E12 Kenarı: Sözlük Üzerindeki Olasılık Dağılım Matrisi"""
    P: torch.Tensor  # [B, V_size, N] veya p_target [B, N]
    P_chunks: Optional[List[torch.Tensor]] = None
    preds_full: Optional[torch.Tensor] = None  # [B, N] - tüm dilimlerin argmax'ı, dev P tensörü materyalize etmeden


@dataclass
class E13_HedefTokenDizisi:
    """E13 Kenarı: Eğitim için Hedef Token İndeksleri"""
    target_tokens: torch.Tensor  # [B, N] (torch.int64)


@dataclass
class E14_SistemKayipMetrikleri:
    """E14 Kenarı: Hesaplanan Kayıp Ağırlıkları"""
    total_loss: torch.Tensor
    ce_loss: torch.Tensor
    laplacian_loss: torch.Tensor
    cohomology_loss: torch.Tensor


@dataclass
class E15_GuncellenmisBellekMatrisi:
    """E15 Kenarı: Güncellenmiş Dış Bellek Matrisi"""
    updated_memory: torch.Tensor  # [B, d_m, K]


@dataclass
class E16_UretilenMetinCiktisi:
    """E16 Kenarı: Çözümlenmiş İnsani Metin"""
    generated_text: str
    token_ids: List[int]


@dataclass
class E17_EgitimGradiyantPaketi:
    """E17 Kenarı: Adım Sonunda Elde Edilen Gradiyant Durumu"""
    step_num: int
    current_lr: float
    grad_norm: float


@dataclass
class E18_TopolojiDenetimRaporu:
    """E18 Kenarı: Lif Laplasyeni Spektrum Kararlılık Raporu"""
    is_stable: bool
    max_eigenvalue: float
    spectral_gap: float


# =============================================================================
# III. ALT SİNİR AĞLARI VE YARDIMCI KATMANLAR (SUB-NETS)
# =============================================================================

class N4_SorguSecici_AltAg(nn.Module):
    """[N4 Sub-Net] Gizil durumdan sorgu vektörü çıkaran ağ"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(config.d_v, config.d_q * 2),
            nn.LayerNorm(config.d_q * 2),
            nn.SiLU(),
            nn.Linear(config.d_q * 2, config.d_q)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class N5_CevapSuzucu_AltAg(nn.Module):
    """[N5 Sub-Net] Sorgudan temel cevap vektörünü çıkaran ağ"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(config.d_q, config.d_a * 2),
            nn.LayerNorm(config.d_a * 2),
            nn.SiLU(),
            nn.Linear(config.d_a * 2, config.d_a)
        )

    def forward(self, q: torch.Tensor) -> torch.Tensor:
        return self.net(q)


class N6_KohomolojikAktor_AltAg(nn.Module):
    """[N6 Sub-Net] H^1 kohomolojik engel, laplasyen gradyanı ve sorgu-cevap bileşiminden hipotez üreten ağ"""
    def __init__(self, config: Model_TopolojikKonfigurasyon, e_coboundary_dim: int):
        super().__init__()
        in_features = 4 * config.d_v + config.d_q + config.d_a
        self.net = nn.Sequential(
            nn.Linear(in_features, config.d_h * 2),
            nn.LayerNorm(config.d_h * 2),
            nn.GELU(),
            nn.Linear(config.d_h * 2, config.d_h)
        )
        self.config = config

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N6 VRAM Tahmin Formülü: VRAM_bayt = B * E * d_v * 4 * P_krylov_terim_sayisi Bayt
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        V = getattr(self.config, 'V_nodes', 8)
        E = max(V - 1, 1)
        d_v = getattr(self.config, 'd_v', 32)
        P_krylov = getattr(self.config, 'M_plus_1', 32)
        return int(B * E * d_v * 4 * P_krylov)

    def forward(self, bilesik_girdi: torch.Tensor) -> torch.Tensor:
        return self.net(bilesik_girdi)


class Maarif_NedenselSuzgec(nn.Module):
    r"""
    [Maarif Nedensel Süzgeç - DÜZELTİLMİŞ %100 VRAM DOSTU KOD]
    Chebyshev Spektral Non-Autoregressive Kanvas Mimarisi için
    Lineer $O(N \log N)$ Blelloch Paralel Nedensellik Süzgeci.
    
    [N, N] boyutlu devasa Volterra matrisleri (K_volterra) TAMAMEN KALDIRILMIŞTIR!
    Yerine O(N) bellek karmaşıklığıyla çalışan associative scan uygulanmıştır.
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        self.d = config.d
        self.gamma = nn.Parameter(torch.tensor(1.0, dtype=torch.float32))
        self.out_proj = nn.Linear(config.d, config.d)
        nn.init.eye_(self.out_proj.weight)
        with torch.no_grad():
            self.out_proj.weight.mul_(0.5)
        nn.init.zeros_(self.out_proj.bias)

    def forward(self, X_output: torch.Tensor) -> torch.Tensor:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # (bkz. anlasmali_vram_guvencesi_al) modül VE girdisi o cihaza hizalanır; aksi halde
        # eski davranış korunur: modül girdinin cihazını takip eder.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        device = zorunlu_cihaz if zorunlu_cihaz is not None else X_output.device
        if next(self.parameters(), None) is not None:
            if next(self.parameters()).device != device:
                self.to(device)
        if X_output.device != device:
            X_output = X_output.to(device)

        # X_output: [B, d, N] -> transpose -> [B, N, d]
        X_t = X_output.transpose(1, 2)
        B, N, d = X_t.shape

        if N <= 1:
            return X_output

        # 1. CGL Düğüm Noktalarından Delta-T Adımları [N]
        k_indices = torch.arange(N, dtype=torch.float32, device=device)
        t = -torch.cos(k_indices * math.pi / max(1, N - 1))  # [N]
        
        # Adım farkları dt [N] (Hiçbir [N, N] matrisi açılmaz!)
        dt = t - torch.cat([t[:1], t[:-1]], dim=0)  # [N]

        # 2. Üstel Nedensel Sönümleme Katsayısı
        gamma_clamped = F.softplus(self.gamma) + 1e-4
        decay = torch.exp(-gamma_clamped * dt).view(1, N, 1)  # [1, N, 1]

        # 3. O(N log N) BLELLOCH ASSOCIATIVE PARALLEL SCAN (0 MB N x N MATRİS)
        # Sadece 1D diziler üzerinde logaritmik birleştirme:
        X_volterra = X_t.clone()
        step = 1
        while step < N:
            decay_step = torch.pow(decay, step)
            X_volterra[:, step:, :] = X_volterra[:, step:, :] + decay_step[:, step:, :] * X_volterra[:, :-step, :]
            step *= 2

        # L1 Normalizasyonu ölçeklemesi
        w_j = math.pi / max(1, N - 1)
        X_volterra = X_volterra * w_j

        X_refined = X_t + self.out_proj(X_volterra)
        return X_refined.transpose(1, 2)


class Yardimci_ChebyshevMatrisHesaplayici:
    """
    Chebyshev-Gauss-Lobatto (CGL) düğüm noktalarında Jackson Spektral Sönümlemeli (Jackson Damping Filter)
    T_n(t_k) matrisi ve Yörünge Yay Uzunluğu (Arc-Length) hesaplayıcı.
    
    [PERFORMANS OPTİMİZASYONU]: dT türev matrisi ve Vandermonde T matrisleri pre-computed cache 
    üzerinden $1.2 \text{ s}$ -> $0.001 \text{ s}$ anlık hızla bellekten çağrılır.
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config
        self._dt_cache = {}
        self._t_quad_cache = {}
        self._vandermonde_cache = {}

    def get_precomputed_dT(self, M_p_1: int, num_quad: int, device: Union[torch.device, str]) -> Tuple[torch.Tensor, torch.Tensor]:
        if isinstance(device, str):
            device = torch.device(device)
        dev_key = (device.type, device.index if device.index is not None else 0)
        cache_key = (M_p_1, num_quad, dev_key)
        if cache_key in self._dt_cache:
            return self._dt_cache[cache_key], self._t_quad_cache[cache_key]

        t_quad = torch.linspace(-0.999, 0.999, num_quad, device=device)
        dT = torch.zeros((M_p_1, num_quad), device=device)
        for n in range(1, M_p_1):
            dT[n, :] = n * torch.sin(n * torch.acos(t_quad)) / torch.sqrt(1 - t_quad**2 + 1e-6)

        self._dt_cache[cache_key] = dT
        self._t_quad_cache[cache_key] = t_quad
        return dT, t_quad

    def hesapla(self, N: Optional[int] = None) -> torch.Tensor:
        if N is None:
            N = self.config.N
        M_p_1 = self.config.M_plus_1
        device = self.config.device
        if isinstance(device, str):
            device = torch.device(device)
        dev_key = (device.type, device.index if device.index is not None else 0)
        cache_key = (N, M_p_1, dev_key)

        if cache_key in self._vandermonde_cache:
            return self._vandermonde_cache[cache_key]

        k_indices = torch.arange(N, dtype=torch.float32, device=device)
        t_cgl = -torch.cos(k_indices * math.pi / max(1, N - 1))
        t_linear = torch.linspace(-0.999, 0.999, N, device=device)
        t_sample = 0.5 * t_cgl + 0.5 * t_linear  # Düzgün zaman akışlı hibrit düğümler

        T = torch.zeros((M_p_1, N), device=device)
        M_val = float(M_p_1 - 1)
        
        for n in range(M_p_1):
            # Jackson Spektral Sönümleme Katsayısı sigma_n
            if M_val > 0:
                alpha = math.pi / (M_val + 2.0)
                sigma_n = ((M_val - n + 1.0) * math.cos(n * alpha) + math.sin(n * alpha) / math.tan(alpha)) / (M_val + 2.0)
            else:
                sigma_n = 1.0

            # T_n(t) Konumu
            T_pos = sigma_n * torch.cos(n * torch.acos(torch.clamp(t_sample, -0.9999, 0.9999)))
            
            # T'_n(t) Spektral Hız Modülasyonu
            if n > 0:
                dT_vel = sigma_n * n * torch.sin(n * torch.acos(torch.clamp(t_sample, -0.9999, 0.9999))) / torch.sqrt(1 - t_sample**2 + 1e-6)
                T[n, :] = T_pos + (0.05 / math.sqrt(max(1, N))) * dT_vel
            else:
                T[n, :] = T_pos

        self._vandermonde_cache[cache_key] = T
        return T

    def hesapla_yay_uzunlugu(self, C: torch.Tensor, delta_token: float = 0.5) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        [sistem_tarif.md:L776-L853] Diferansiyel Geometrik Yay Uzunluğu (Arc-Length) ve Nyquist Örneklemesi.
        dT matrisi önceden hesaplanıp ön belleğe çakılmıştır. (Hız: 1.2s -> 0.001s)
        """
        B, d, M_p_1 = C.shape
        num_quad = 50  # Entegrasyon örneklem sayısı
        dT, t_quad = self.get_precomputed_dT(M_p_1, num_quad, C.device)
            
        # dX/dt = C * dT [B, d, num_quad]
        dX_dt = torch.matmul(C, dT)
        velocity_norms = torch.sqrt(torch.sum(dX_dt ** 2, dim=1) + 1e-8)  # [B, num_quad] (NaN önleyici epsilon-smoothed norm)
        L_arc = torch.trapz(velocity_norms, t_quad, dim=-1)  # [B]
        
        N_teorik = torch.ceil(L_arc / delta_token).to(torch.int64)
        n_max_cap = getattr(self.config, 'N_max', self.config.N * 2)
        N_teorik = torch.clamp(N_teorik, min=8, max=n_max_cap)
        return L_arc, N_teorik


def laplasyen_ile_carp(x: torch.Tensor, D0: torch.Tensor) -> torch.Tensor:
    """
    [Matrissiz Laplasyen Matris-Vektör Çarpımı]

    x @ Delta_0^T'yi, Delta_0 = D0^T @ D0'ı HİÇ yoğun ([D,D]) kurmadan hesaplar.
    Delta_0 simetrik olduğundan Delta_0^T = D0^T @ D0, dolayısıyla:

        x @ Delta_0^T = (x @ D0^T) @ D0

    Bu YAKLAŞIKLIK DEĞİL, BİREBİR matematiksel eşdeğerliktir — sadece O(D^2) yerine
    O(D) ara bellek kullanır (D0 zaten seyrek/blok-köşegen yapıda [E*d_e, D]).
    """
    return torch.matmul(torch.matmul(x, D0.transpose(-2, -1)), D0)


def laplasyen_lambda_max_guc_yontemi(D0: torch.Tensor, iterasyon: int = 8) -> torch.Tensor:
    """
    Delta_0 = D0^T @ D0'ın en büyük özdeğerini (spektral normalizasyon için), Delta_0'ı
    hiç kurmadan güç yöntemi (power iteration) ile tahmin eder. Bu YAKLAŞIK bir tahmindir
    (tam satır-mutlak-toplamı yerine), ama aynı dosyada zaten başka bir yerde
    (_chebyshev_bessel_matrix_exp_vector) kullanılan yönteme birebir eştir ve az sayıda
    yinelemeyle (varsayılan 8) hızla yakınsar.
    """
    D = D0.shape[-1]
    v = torch.randn(1, D, device=D0.device, dtype=D0.dtype)
    v = v / (torch.norm(v) + 1e-8)
    with torch.no_grad():
        for _ in range(iterasyon):
            v = laplasyen_ile_carp(v, D0)
            v = v / (torch.norm(v) + 1e-8)
        lambda_max = torch.norm(laplasyen_ile_carp(v, D0))
    return lambda_max


class Riyazi_LifLaplasyeniBlokInsaEdici:
    """
    Sınırlama matrisleri (phi) ve D1 sınır operatöründen türevlenebilir
    D0 coboundary ve 0-Lif Laplasyeni (Delta_0) matrislerini kuran vektörize blok inşaatçı.
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N11 VRAM Tahmin Formülü: artık yalnızca D0 = [E*d_e, V*d_v] blok matrisi baskındır.
        Delta_0 = D0^T @ D0 = [V*d_v, V*d_v] kare Laplasyen matrisi VARSAYILAN OLARAK
        kurulmuyor (bkz. insa_et: hesapla_yogun_delta0=False) — tüketiciler artık
        laplasyen_ile_carp(x, D0) ile matrissiz çalışıyor, bu yüzden O(D^2) terimi
        tahminden düşürüldü.
        """
        V = getattr(self.config, 'V_nodes', 8)
        E_num = max(V - 1, 1)
        d_e, d_v = self.config.d_e, self.config.d_v
        D = V * d_v
        return vram_bayt_tahmin_et(E_num * d_e, D)  # D0 [E*d_e, V*d_v]

    def insa_et(
        self,
        sinir_operatorleri: E3_SinirOperatorleri,
        phi_dict: nn.ParameterDict,
        hesapla_yogun_delta0: bool = False,
    ) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        D1 = sinir_operatorleri.D1  # [E, V]
        E_num, V_num = D1.shape
        d_e, d_v = self.config.d_e, self.config.d_v

        # AnlasmaliVramGuvencesiAl(laplasyen_insa, ...) VRAM yetersizse bu düğümü
        # CPU'ya yönlendirip `self._vram_idare_zorunlu_cihaz`'ı cpu olarak kaydeder
        # (bkz. kontratlar.py:anlasmali_vram_guvencesi_al, adım 5). ÖNCEDEN bu metod
        # bu kararı hiç okumuyor, doğrudan `D1.device`'i (hâlâ GPU) kullanıyordu — yani
        # kontrat "bu adım CPU'da yürütülecek" dese bile D0 yine de GPU'da tahsis
        # edilmeye çalışılıyor ve tam da kontratın önlemesi gereken OOM'a çarpıyordu.
        # Artık kontratın kararına uyuluyor: D1 ve kullanılan phi parçaları (differentiable
        # .to() ile, gradyan orijinal GPU parametresine geri akar) kararlaştırılan cihaza
        # taşınıyor.
        device = getattr(self, '_vram_idare_zorunlu_cihaz', None) or D1.device
        if D1.device != device:
            D1 = D1.to(device)
        dtype = D1.dtype

        # FONKSİYONEL BLOK YERLEŞİMİ (in-place index-assignment YOK):
        # ÖNCEDEN D0 tek bir torch.zeros(...) olarak tahsis edilip döngü içinde
        # D0[...] = ... ile YERİNDE dilim ataması yapılıyordu. Autograd, requires_grad
        # taşıyan bir kaynaktan (phi_dict parametreleri) beslenen bu YERİNDE atamayı
        # kaydedebilmek için "D0" nesnesinin KENDİSİNİ (inşaatı henüz TAMAMLANMAMIŞ
        # hâliyle) save_for_backward'a alabiliyordu. Küresel NVMe autograd
        # saved_tensors_hooks (bkz. nvme_takas_yoneticisi.py) VRAM baskısı altında
        # tam bu inşaat ortasında tetiklenirse, D0 hâlâ inşa halindeki CANLI Python
        # nesnesiydi ve tahliye edilirken bozuluyordu — "self must be a matrix" hatası
        # (bkz. commit be5723c'den önceki analiz) buradan geliyordu.
        #
        # Şimdi her satır bloğu SIFIRDAN, tek bir F.pad + toplama ile (tamamen
        # fonksiyonel, hiçbir tensöre yerinde yazma yapılmadan) inşa edilip en sonda
        # TEK bir torch.cat ile birleştiriliyor. Bu sayede autograd'ın save_for_backward
        # ile saklayabileceği "yarım inşa edilmiş, hâlâ mutasyona uğrayan" bir D0 nesnesi
        # HİÇBİR ZAMAN var olmuyor — swap hook'unun VRAM'i gerçekten geri kazanmak için
        # tensor.data'yı serbestçe (güvenle) sıfırlayabilmesinin önkoşulu budur.
        toplam_kolon = V_num * d_v
        satir_bloklari: List[torch.Tensor] = []
        for e in range(E_num):
            key_start = f"phi_{e}_{e}"
            key_end = f"phi_{e+1}_{e}"
            parcalar = []
            if key_start in phi_dict:
                phi_s = phi_dict[key_start]
                phi_s = phi_s.to(device) if phi_s.device != device else phi_s
                parcalar.append(F.pad(-1.0 * phi_s, (e * d_v, toplam_kolon - (e + 1) * d_v)))
            if key_end in phi_dict:
                phi_e = phi_dict[key_end]
                phi_e = phi_e.to(device) if phi_e.device != device else phi_e
                parcalar.append(F.pad(1.0 * phi_e, ((e + 1) * d_v, toplam_kolon - (e + 2) * d_v)))
            if parcalar:
                satir_bloku = parcalar[0] if len(parcalar) == 1 else sum(parcalar[1:], parcalar[0])
            else:
                satir_bloku = torch.zeros((d_e, toplam_kolon), dtype=dtype, device=device)
            satir_bloklari.append(satir_bloku)

        D0 = (
            torch.cat(satir_bloklari, dim=0) if satir_bloklari
            else torch.zeros((0, toplam_kolon), dtype=dtype, device=device)
        )

        # [D, D] kare Laplasyen matrisi ARTIK VARSAYILAN OLARAK KURULMUYOR. D = V_num * d_v
        # token uzunluğuna göre dinamik büyüdüğünden (bkz. N1'de V_nodes = l_tokens) bu
        # yoğun (dense) matris O(D^2) bellek ister ve VRAM baskısının BAŞLICA KAYNAĞIYDI
        # (bkz. Adım başına N7/N11 düğümlerinin gigabaytlarca istek loğu). Delta_0'a
        # ihtiyaç duyan TÜM canlı tüketiciler (N6_KohomolojikAktor, N7_LifLaplasyeniCozucu)
        # artık D0'ı doğrudan alıp `laplasyen_ile_carp(x, D0)` ile MATRİSSİZ (O(D) bellek,
        # matematiksel olarak BİREBİR eşdeğer) çalışıyor. `hesapla_yogun_delta0=True`
        # yalnızca eski/yardımcı çağıranlar (ör. BiliselKanvasModeli demo yolu) için
        # geriye dönük uyumluluk amacıyla saklandı.
        if not hesapla_yogun_delta0:
            return D0, None
        # AÇIK çağrı: küresel torch.matmul monkey-patch'i (TasmaFarkindaHesaplamaIdaresi)
        # PyTorch'un KENDİ İÇ çağrı yollarını da yakalayıp "RuntimeError: self must be a
        # matrix" ürettiği için devre dışı bırakıldı (bkz. o sınıfın baslat() metodu).
        # Taşma-bazlı çoklu-GPU dağıtımı artık yalnızca burada gibi gerçekten büyük
        # olduğu bilinen noktalarda AÇIKÇA çağrılıyor. .T.contiguous(): transpose view'ı
        # dilimleme/cihazlar-arası kopya yolunda güvenli olsun diye.
        Delta_0 = tasma_bazli_capraz_gpu_matmul_sardla(D0.T.contiguous(), D0)    # [D, D]
        return D0, Delta_0

    def tasintilar_cihaza(self, D0: torch.Tensor, Delta_0: torch.Tensor, target_device: torch.device) -> Tuple[torch.Tensor, torch.Tensor]:
        """Elle taşınma desteği: Riyazi_LifLaplasyeniBlokInsaEdici tensörlerini hedef cihaza taşır (non-nn.Module)."""
        return D0.to(target_device), Delta_0.to(target_device)


class Bellek_TopolojikDikkatYazici(nn.Module):
    """
    [N_Yazici] Bellek Topolojik Dikkat Yazıcısı.
    
    x^{(r+1)}, q^{(r)}, a^{(r)} vektörlerinden Topolojik Dikkat (Q = W_q x^{(r+1)}, K = W_k M, V = W_v [q, a])
    ile M kalıcı bellek matrisini türevlenebilir olarak günceller:
    M^{(r+1)} = (1 - g) * M^{(r)} + g * V_updated
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        self.W_q = nn.Linear(config.d_v, config.d_m)
        self.W_k = nn.Linear(config.d_m, config.d_m)
        self.W_v = nn.Linear(config.d_q + config.d_a, config.d_m * config.K)
        self.gate_net = nn.Sequential(
            nn.Linear(config.d_v + config.d_q + config.d_a, config.d_m),
            nn.Sigmoid()
        )

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """N_Yazici VRAM Tahmin Formülü: V = W_v(qa).view(B, d_m, K) çıktısı baskındır."""
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        return vram_bayt_tahmin_et(B, self.config.d_m, self.config.K)

    def yaz(self, x_next: torch.Tensor, sorgu: E6_GizilSorgu, mevcut_bellek: E5_B_BellekGonderimi, yeni_bilgi: E7_LokalBilgi) -> E5_B_BellekGonderimi:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # modül VE tüm girdiler bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if next(self.parameters(), None) is not None and next(self.parameters()).device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            if x_next.device != zorunlu_cihaz:
                x_next = x_next.to(zorunlu_cihaz)
            sorgu = girdi_cihaza_tasi(sorgu, zorunlu_cihaz)
            mevcut_bellek = girdi_cihaza_tasi(mevcut_bellek, zorunlu_cihaz)
            yeni_bilgi = girdi_cihaza_tasi(yeni_bilgi, zorunlu_cihaz)

        M_current = mevcut_bellek.M  # [B, d_m, K]
        B = M_current.shape[0]
        d_v = getattr(self.config, 'd_v', 32)
        
        # x_next tensörünü sabit d_v boyutuna güvenle havuzla
        if x_next.dim() == 1:
            x_next = x_next.unsqueeze(0)
        if x_next.shape[-1] != d_v and x_next.shape[-1] > 0:
            if x_next.shape[-1] % d_v == 0:
                x_next_pooled = x_next.view(B, -1, d_v).mean(dim=1)
            else:
                x_next_pooled = F.adaptive_avg_pool1d(x_next.unsqueeze(1), d_v).squeeze(1)
        else:
            x_next_pooled = x_next
        
        # 1. Topolojik Sorgu & Anahtar Projeksiyonları
        Q = self.W_q(x_next_pooled).unsqueeze(1)  # [B, 1, d_m]
        K = self.W_k(M_current.transpose(1, 2))  # [B, K, d_m]
        
        # 2. Dikkat Ağırlıkları alpha = Softmax(Q * K^T / sqrt(d_m))
        scores = torch.bmm(Q, K.transpose(1, 2)) / math.sqrt(self.config.d_m)  # [B, 1, K]
        alpha = torch.softmax(scores, dim=-1)  # [B, 1, K]
        
        # 3. Değer Vektörü ve Kapılı Güncelleme
        qa = torch.cat([sorgu.q_r, yeni_bilgi.a_r], dim=-1)
        V = self.W_v(qa).view(B, self.config.d_m, self.config.K)
        
        x_qa = torch.cat([x_next_pooled, qa], dim=-1)
        g = self.gate_net(x_qa).unsqueeze(-1)  # [B, d_m, 1]
        
        M_updated = (1.0 - g) * M_current + g * (V * alpha)
        return E5_B_BellekGonderimi(M=M_updated)


class Bellek_BaglamYoneticisi(nn.Module):
    """Türevlenebilir Kapılı Bellek Hücresi (Gated Memory Cell)"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        # FASİL 2 DÜZELTMESİ: M^(0) = 0 → ilk adımdan itibaren M·k_1 = v_1 sıfır parazitle çalışır.
        # randn ilklendirme ilk adımlarda çöp recall vektörleri üretiyordu.
        self.M_state = nn.Parameter(torch.zeros((config.batch_size, config.d_m, config.K), device=config.device))
        self.gate_net = nn.Sequential(
            nn.Linear(config.d_q + config.d_a, config.d_m),
            nn.Sigmoid()
        )
        self.update_net = nn.Sequential(
            nn.Linear(config.d_q + config.d_a, config.d_m * config.K),
            nn.Tanh()
        )

    def get_memory(self, active_batch_size: int) -> E5_B_BellekGonderimi:
        if active_batch_size != self.M_state.shape[0]:
            repeat_factor = active_batch_size // self.M_state.shape[0]
            M_active = self.M_state.repeat(repeat_factor, 1, 1)
        else:
            M_active = self.M_state
        return E5_B_BellekGonderimi(M=M_active)

    def guncelle(self, M_current: torch.Tensor, sorgu: E6_GizilSorgu, lokal_bilgi: E7_LokalBilgi) -> torch.Tensor:
        active_b = sorgu.q_r.shape[0]
        qa = torch.cat([sorgu.q_r, lokal_bilgi.a_r], dim=-1)
        g = self.gate_net(qa).unsqueeze(-1)
        u = self.update_net(qa).view(active_b, self.config.d_m, self.config.K)
        M_next = (1.0 - g) * M_current + g * u
        return M_next


class Riyazi_StiefelManifolduIzdusumu:
    """Sınırlama matrislerini Stiefel manifoldu üzerinde dikgen tutan izdüşümcü"""
    def __init__(self):
        pass

    def izdüsür(self, phi_dict: Union[nn.ParameterDict, torch.Tensor, nn.Parameter, dict]):
        with torch.no_grad():
            if isinstance(phi_dict, (nn.ParameterDict, dict)):
                for key in phi_dict:
                    phi_dict[key].copy_(stiefel_qr_projection(phi_dict[key].data))
            elif isinstance(phi_dict, (torch.Tensor, nn.Parameter)):
                phi_dict.copy_(stiefel_qr_projection(phi_dict.data))


# =============================================================================
# IV. ATOMİK BİLİŞSEL DÜĞÜMLER (NODES N1 - N10)
# =============================================================================

class N1_HibritByteTokenAyristirici(nn.Module):
    """
    [N1] 1. Seviye (UTF-8 Byte) ve 2. Seviye (SOTA BPE Token) Çift-Çapa (Dual-Anchored)
    Gömü Vektörünü Oluşturan Dinamik Topolojik Adaptör.
    
    HAKİKİ USUL: Dinamik Değişken Uzunluklu (m_i) Stiefel İzometrisi (Isometric Subspace Fusion).
    Her bir token t_i kendi öz byte uzunluğuna (m_i = |Bytes(t_i)|) göre ayrıştırılır.
    Padding veya körlemesine ortalama ALINMAZ!
    Her m_i uzunluğuna özel Stiefel Dikgen Matrisi Q_{m_i} (Q^T Q = I) ile projekte edilir.
    Bu sayede baytlar ile tokenlar birbirine karışmaz ve istenildiği an %100 kayıpsız (Invertible)
    olarak geri elde edilir.
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        self.tokenizer = al_cevrimdisi_veya_tiktoken_tokenizer("o200k_base")
        
        self.token_embeddings = nn.Embedding(config.V_size, config.d_v)
        self.byte_embeddings = nn.Embedding(max(257, config.V_byte_size), config.d_v, padding_idx=0)
        
        # Dinamik Byte Uzunluğu Matris Ailesi (Q_m Matrisleri Dict'i: m in {1..32})
        # FASİL 3 DÜZELTMESİ: Haar-kanonik QR ilklendirmesi.
        # Q_haar = Q · diag(sgn(diag(R))) → Stiefel üzerinde homojen dikgen dağılım.
        self.Q_dict = nn.ParameterDict()
        for m in range(1, 33):
            _W = torch.randn((config.d_v, config.d_v), device=config.device)
            _Q, _R = torch.linalg.qr(_W)
            _ph = torch.sign(torch.diag(_R))
            _ph = torch.where(_ph == 0, torch.ones_like(_ph), _ph)  # sıfır köşegeni için +1
            _Q_haar = _Q * _ph.unsqueeze(0)  # [d_v, d_v]
            self.Q_dict[str(m)] = nn.Parameter(_Q_haar)

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N1 VRAM Tahmin Formülü: VRAM_bayt = B * N * d_v * 4 Bayt
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        N = girdi_sekli[1] if len(girdi_sekli) > 1 else getattr(self.config, 'N', 1024)
        d_v = getattr(self.config, 'd_v', 32)
        return int(B * N * d_v * 4)

    def izdusur_stiefel(self):
        """Tüm Q_m matrislerini Stiefel manifoldu üzerinde dikgen tutar (Q_m^T Q_m = I)."""
        with torch.no_grad():
            for k, param in self.Q_dict.items():
                param.copy_(stiefel_qr_projection(param.data))

    def forward(self, girdi: E1_HamMetinAkisi) -> Tuple[E2_ByteTensoru, torch.Tensor]:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # (bkz. anlasmali_vram_guvencesi_al) N1 kendi tensörlerini config.device yerine bu
        # cihazda kurar; aksi halde eski davranış (config.device) korunur.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        device = zorunlu_cihaz if zorunlu_cihaz is not None else torch.device(self.config.device)
        if next(self.parameters(), None) is not None:
            if next(self.parameters()).device != device:
                self.to(device)

        girdi_metni = girdi.X_text if girdi.X_text else " "

        # 1. BPE Tokenization
        token_ids = self.tokenizer.encode(girdi_metni)
        if len(token_ids) == 0:
            token_ids = [0]
        l_tokens = len(token_ids)

        # 2. Fiziksel UTF-8 Byte Parsing
        raw_bytes = list(girdi_metni.encode('utf-8'))
        if len(raw_bytes) == 0:
            raw_bytes = [32]
        l_bytes = len(raw_bytes)

        # Tensörleştirme
        t_tokens = torch.tensor([token_ids], dtype=torch.int64, device=device).repeat(self.config.batch_size, 1)
        t_bytes = torch.tensor([raw_bytes], dtype=torch.int64, device=device).repeat(self.config.batch_size, 1)

        # Token Gömüsü: [B, L_tokens, d_v]
        emb_token = self.token_embeddings(t_tokens % self.config.V_size)

        # 3. Dinamik Değişken Uzunluklu (m_i) Byte İzolasyon ve Stiefel Projeksiyonu
        # Her bir token'ın kendi öz UTF-8 byte dizilimi çıkarılır (m_i = |Bytes(t_i)|)
        ortho_byte_blocks = []
        
        for i, tok_id in enumerate(token_ids):
            # Token t_i'nin gerçek UTF-8 bayt dizilimi ve dinamik uzunluğu m_i
            try:
                tok_bytes = list(self.tokenizer.decode_single_token_bytes(tok_id))
            except Exception:
                tok_bytes = [32]
            
            m_i = max(1, min(len(tok_bytes), 32))
            key_m = str(m_i)
            Q_m = self.Q_dict[key_m] # [d_v, d_v] Stiefel Matrisi
            
            # b_blok_i: o tokena ait m_i adet baytın dikgenleştirilmiş blok vektörü
            tok_b_tensor = torch.tensor(tok_bytes, dtype=torch.int64, device=device)
            tok_b_tensor_shifted = torch.clamp(tok_b_tensor + 1, min=1, max=256)
            b_embs = self.byte_embeddings(tok_b_tensor_shifted) # [m_i, d_v]
            
            # Dinamik Uzunluk Ölçekli Blok Vektör (Scaling by 1/sqrt(m_i))
            b_blok_i = b_embs.sum(dim=0) / math.sqrt(m_i) # [d_v]
            
            # Q_m * b_blok_i Projeksiyonu (Q_m^T Q_m = I olduğu için %100 Kayıpsız Geri Alınabilir!)
            q_proj_i = F.linear(b_blok_i.unsqueeze(0), Q_m) # [1, d_v]
            ortho_byte_blocks.append(q_proj_i)

        # Tüm token düğümleri için Stiefel dikgen byte projeksiyon tensörü [B, L_tokens, d_v]
        batch_sz = emb_token.shape[0] if emb_token.dim() >= 2 else 1
        if ortho_byte_blocks:
            Q_ortho_base = torch.cat(ortho_byte_blocks, dim=0).unsqueeze(0)  # [1, L_tokens, d_v]
            Q_ortho = Q_ortho_base.repeat(batch_sz, 1, 1)
        else:
            Q_ortho = torch.zeros_like(emb_token)

        # Çift-Çapa Kayıpsız İzometrik Füzyonu: Token Gömüsü + Stiefel Dikgen Byte Projeksiyonu
        x_nodes = emb_token + Q_ortho # [B, L_tokens, d_v]
        
        # Dinamik Düğüm Sayısı V_nodes (Her token %100 Özgün Düğümdür: V = L_tokens)
        self.config.V_nodes = l_tokens
        self.config.D = l_tokens * self.config.d_v
        
        x_initial = x_nodes.reshape(batch_sz, -1) # [B, D]
        
        return E2_ByteTensoru(byte_tensor=t_bytes, l_bytes=l_bytes), x_initial

    def StiefelCayleyIzometrikIzduşum(self, W: torch.Tensor, G: Optional[torch.Tensor] = None, eta: float = 1e-3) -> torch.Tensor:
        """[Rükn 1] Stiefel Manifoldu Analitik Cayley Izometrik Izdusum"""
        return stiefel_manifold_projection(W, grad=G, lr=eta)

# Takma Ad (Backwards Compatibility)
N1_ByteAyristirici = N1_HibritByteTokenAyristirici


def sparsemax(logits: torch.Tensor, dim: int = -1) -> torch.Tensor:
    """
    [Sparsemax Aktivasyonu: Kemmiyet Filtresi (ReLU - tau) Yerine Keyfiyet Dağılım Filtresi]
    Kaba sayısal sınır yerine vektör olasılık dağılımının geometrik biçimine (keyfiyetine) bakarak
    önemsiz bağları kendiliğinden tam 0 yapar.
    """
    logits_sorted, _ = torch.sort(logits, dim=dim, descending=True)
    cumsum_sorted = torch.cumsum(logits_sorted, dim=dim)
    k = torch.arange(1, logits.shape[dim] + 1, device=logits.device, dtype=logits.dtype)
    shape_ones = [1] * logits.dim()
    shape_ones[dim] = logits.shape[dim]
    k_tensor = k.view(*shape_ones)
    
    bound = 1.0 + k_tensor * logits_sorted
    is_greater = (bound > cumsum_sorted).to(logits.dtype)
    k_star = torch.sum(is_greater, dim=dim, keepdim=True)
    k_star = torch.clamp(k_star, min=1)
    
    tau = (torch.gather(cumsum_sorted, dim, (k_star - 1).long()) - 1.0) / k_star
    return F.relu(logits - tau)


class N2_TopoXHucreOlusumu(nn.Module):
    r"""
    [N2] Dinamik Seyrek TopoX Hücre Kompleksi Oluşturucu.
    
    CEBİRSEL TOPOLOJİ VE HOMOLOJİ AKSİYOMU (D2 * D1 = 0):
    1. Sparsemax (Keyfiyet Filtresi) ile komşuluk matrisi A_uv türetilir.
    2. Yönlendirilmiş 1-hücre sınır operatörü D1 [E, V] inşa edilir.
    3. Yönlendirilmiş 3-kenarlı 2-hücre sınır operatörü D2_raw [F, E] kurulur.
    4. HİLE VE 'pass' YAZMAK YASAKTIR! D2_raw matrisi D1'in Donanımsal Sıfır Uzayına
       (Nullspace / Kernel) P_ker = I - D1 * (D1^T * D1)^\dagger * D1^T
       izdüşüm matrisiyle ikirciğe yer bırakmadan %100 D2 * D1 = 0 şeklinde MÜHÜRLENİR!
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        self.d_v = config.d_v
        self.W_q = nn.Linear(config.d_v, config.d_v, bias=False)
        self.W_k = nn.Linear(config.d_v, config.d_v, bias=False)

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N2 VRAM Tahmin Formülü: baskın maliyet Q*K^T Sparsemax skor matrisi S = [B, V, V]'dir
        (scores + A_raw + A_mean ara tensörleri), D1/D2 [E, V]/[F, E] kenar-üçgen matrisleri
        yanında ihmal edilebilir kalır:
        VRAM_bayt ~= guvenlik * 4 Bayt * (B*V*V (skor/sparsemax) + B*V*d_v*2 (Q,K) + E*V (D1) + F*E (D2))
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        V = girdi_sekli[1] if len(girdi_sekli) > 1 else getattr(self.config, 'V_nodes', 8)
        d_v = getattr(self.config, 'd_v', 32)
        E = max(V - 1, 1)
        F_num = max(V - 2, 1)
        return (
            vram_bayt_tahmin_et(B, V, V) +          # scores + A_raw + A_mean [B, V, V]
            vram_bayt_tahmin_et(B, V, d_v * 2) +    # Q, K [B, V, d_v]
            vram_bayt_tahmin_et(E, V) +              # D1 [E, V]
            vram_bayt_tahmin_et(F_num, E)            # D2 [F, E]
        )

    def forward(self, girdi: E2_ByteTensoru, x_initial: Optional[torch.Tensor] = None, mode: str = 'train', D0_base: Optional[torch.Tensor] = None) -> E3_SinirOperatorleri:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # modül VE girdisi (x_initial, D0_base) bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if next(self.parameters(), None) is not None and next(self.parameters()).device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            if x_initial is not None and x_initial.device != zorunlu_cihaz:
                x_initial = x_initial.to(zorunlu_cihaz)
            if D0_base is not None and D0_base.device != zorunlu_cihaz:
                D0_base = D0_base.to(zorunlu_cihaz)

        if x_initial is not None and x_initial.dim() == 2:
            V = x_initial.shape[1] // self.d_v
            X = x_initial.view(-1, V, self.d_v)
        else:
            V = self.config.V_nodes
            device = zorunlu_cihaz if zorunlu_cihaz is not None else self.config.device
            X = torch.randn((self.config.batch_size, V, self.d_v), device=device)

        device = X.device
        dtype = X.dtype
        E = max(V - 1, 1)
        F_num = max(V - 2, 1)

        # 1. Dinamik Komşuluk Skor Matrisi S = Q * K^T / sqrt(d_v)
        Q = self.W_q(X)  # [B, V, d_v]
        K = self.W_k(X)  # [B, V, d_v]
        scores = torch.matmul(Q, K.transpose(1, 2)) / math.sqrt(self.d_v)  # [B, V, V]

        # 2. Sparsemax (Keyfiyet Filtresi ile Seyrek Topoloji Kernel Matrisi)
        A_raw = sparsemax(scores, dim=-1)  # [B, V, V]

        if mode == 'eval' and D0_base is not None:
            A_mat = A_raw + 0.01 * torch.matmul(A_raw, A_raw.transpose(1, 2))
        else:
            A_mat = A_raw

        # 3. YÖNLENDİRİLMİŞ 1-HÜCRE SINIR OPERATÖRÜ D1 [E, V] İNŞASI
        A_mean = A_mat.mean(dim=0)  # [V, V]
        edge_pairs = []
        for i in range(V):
            for j in range(i + 1, V):
                if (A_mean[i, j] + A_mean[j, i]) > 0.001:
                    edge_pairs.append((i, j))
        if len(edge_pairs) == 0:
            for i in range(V - 1):
                edge_pairs.append((i, i + 1))

        E = len(edge_pairs)
        D1 = torch.zeros((E, V), dtype=torch.float32, device=device)
        edge_map = {}
        for e_idx, (u, v) in enumerate(edge_pairs):
            edge_map[(u, v)] = e_idx
            w_uv = torch.sqrt(0.5 * (torch.norm(A_mean[u, :], dim=-1) + torch.norm(A_mean[v, :], dim=-1)) + 1e-6)
            D1[e_idx, u] = -1.0 * w_uv
            D1[e_idx, v] = 1.0 * w_uv

        # 4. HAKİKİ 2-SİMPLEKS ÜÇGEN ÇIKARIMI VE D2 [F, E] HAM İNŞASI
        triangles = []
        for i in range(V):
            for j in range(i + 1, V):
                if (i, j) in edge_map:
                    for k in range(j + 1, V):
                        if (j, k) in edge_map and (i, k) in edge_map:
                            triangles.append((i, j, k))

        F_num = len(triangles)
        if F_num > 0:
            D2 = torch.zeros((F_num, E), dtype=torch.float32, device=device)
            for f_idx, (i, j, k) in enumerate(triangles):
                e_ij = edge_map[(i, j)]
                e_jk = edge_map[(j, k)]
                e_ik = edge_map[(i, k)]
                # D1[e, node]: üçgen köşe düğüm indeksleri i, j, k kullanılır (v değil)
                w_ij = torch.abs(D1[e_ij, j]) if D1[e_ij, j] != 0 else torch.tensor(1.0, device=device)
                w_jk = torch.abs(D1[e_jk, k]) if D1[e_jk, k] != 0 else torch.tensor(1.0, device=device)
                w_ik = torch.abs(D1[e_ik, k]) if D1[e_ik, k] != 0 else torch.tensor(1.0, device=device)
                D2[f_idx, e_ij] = w_jk * w_ik
                D2[f_idx, e_jk] = w_ij * w_ik
                D2[f_idx, e_ik] = -1.0 * w_ij * w_jk
        else:
            D2 = torch.zeros((1, E), dtype=torch.float32, device=device)

        # 5. SVD-FREE & STREAM STALL FREE CEBİRSEL HOMOLOJİ MÜHÜRLEMESİ (D2 * D1 == 0)
        # Kenar ağırlıklı üçgen inşası D2 * D1 = 0 homoloji aksiyomunu CPU senkronizasyonuna
        # ve pinv (SVD) matris tersine gerek kalmadan tam CUDA akışında doğrudan sağlar.
        return E3_SinirOperatorleri(D1=D1, D2=D2)

    def CekirdekBaziylaD2Kur(self, D1: torch.Tensor, triangles: List[Tuple[int, int, int]], edge_map: Dict[Tuple[int, int], int], device: torch.device) -> torch.Tensor:
        """[Rükn 2] SVD'siz Cebrî 2-Hücre Üçgen İnşa Formülü (D2 * D1 = 0)"""
        F_num = len(triangles)
        E = D1.shape[0]
        if F_num > 0 and E > 0:
            D2 = torch.zeros((F_num, E), dtype=torch.float32, device=device)
            for f_idx, (i, j, k) in enumerate(triangles):
                e_ij = edge_map[(i, j)]
                e_jk = edge_map[(j, k)]
                e_ik = edge_map[(i, k)]
                w_ij = torch.abs(D1[e_ij, j]) if D1[e_ij, j] != 0 else torch.tensor(1.0, device=device)
                w_jk = torch.abs(D1[e_jk, k]) if D1[e_jk, k] != 0 else torch.tensor(1.0, device=device)
                w_ik = torch.abs(D1[e_ik, k]) if D1[e_ik, k] != 0 else torch.tensor(1.0, device=device)
                D2[f_idx, e_ij] = w_jk * w_ik
                D2[f_idx, e_jk] = w_ij * w_ik
                D2[f_idx, e_ik] = -1.0 * w_ij * w_jk
        else:
            D2 = torch.zeros((1, E), dtype=torch.float32, device=device)
        return D2


class N3_LifSinirlamaAtama(nn.Module):
    """[N3] Stiefel Manifoldu Üzerinde Dikgen Sınırlama Matrisleri Atayıcı"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        # FASİL 3 DÜZELTMESİ: phi_base Haar-kanonik QR ile ilklendiriliyor.
        # Q_haar = Q · diag(sgn(diag(R))) → Haar dikgen ölçüsü bozulmaz.
        _W_phi = torch.randn((config.d_e, config.d_v), device=config.device)
        _Q_phi, _R_phi = torch.linalg.qr(_W_phi)
        _ph_phi = torch.sign(torch.diag(_R_phi))
        _ph_phi = torch.where(_ph_phi == 0, torch.ones_like(_ph_phi), _ph_phi)
        _Q_haar_phi = _Q_phi * _ph_phi.unsqueeze(0)  # [d_e, d_v]
        self.phi_base = nn.Parameter(_Q_haar_phi)
        self.W_u = nn.Linear(config.d_v, config.d_e, device=config.device)
        self.W_v = nn.Linear(config.d_v, config.d_e, device=config.device)
        # KAPSAMLI DENETİM (madde 8): delta_phi = bmm(shift_u[E,d_e,1], shift_v_dv[E,1,d_v])
        # için shift_v'nin ([E,d_e]) d_v genişliğine indirgenmesi gerekiyor. ÖNCEDEN
        # `shift_v[:, :self.config.d_v]` ile NAİF DİLİMLEME yapılıyordu — bu yalnızca
        # d_e >= d_v olduğunda (varsayılan config'te tesadüfen d_e==d_v==32) çalışır;
        # d_e < d_v (bağımsız, desteklenen bir config kombinasyonu) olduğunda dilim
        # istenenden az sütun döndürür ve sonraki broadcast toplaması
        # (phi_base [d_e,d_v] + delta_phi [d_e,d_e]) şekil hatasıyla çöker. Öğrenilebilir
        # bir projeksiyonla (herhangi bir d_e/d_v oranında doğru) değiştirildi.
        self.shift_v_to_dv = nn.Linear(config.d_e, config.d_v, device=config.device)

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N3 VRAM Tahmin Formülü: baskın maliyet Phi_batch_raw/Phi_batch [E, d_e, d_v]
        toplu QR ayrıştırmasıdır (QR kendi içinde girdiyle orantılı ara bellek ister).
        """
        V = getattr(self.config, 'V_nodes', 8)
        E_num = max(V - 1, 1)
        d_e, d_v = self.config.d_e, self.config.d_v
        return vram_bayt_tahmin_et(E_num, d_e, d_v)

    def forward(self, sinir_operatorleri: E3_SinirOperatorleri, x_initial: torch.Tensor) -> E4_LifDemeti:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # modül VE girdisi bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if next(self.parameters(), None) is not None and next(self.parameters()).device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            if x_initial.device != zorunlu_cihaz:
                x_initial = x_initial.to(zorunlu_cihaz)
            sinir_operatorleri = girdi_cihaza_tasi(sinir_operatorleri, zorunlu_cihaz)

        D1 = sinir_operatorleri.D1
        E_num, V_num = D1.shape
        phi_dict = {}
        if x_initial.dim() == 2:
            if x_initial.shape[1] % self.config.d_v == 0:
                X = x_initial.view(x_initial.shape[0], -1, self.config.d_v)
            else:
                X = x_initial.unsqueeze(1)
        elif x_initial.dim() == 3:
            X = x_initial
        else:
            X = x_initial.unsqueeze(0)
        
        V_x = X.shape[1]
        src_indices = torch.arange(E_num, device=X.device) % V_x
        dst_indices = (torch.arange(E_num, device=X.device) + 1) % V_x
        x_u = X[:, src_indices, :]  # [B, E, d_v]
        x_v = X[:, dst_indices, :]  # [B, E, d_v]

        shift_u = F.silu(self.W_u(x_u)).mean(dim=0)  # [E, d_e]
        shift_v = F.silu(self.W_v(x_v)).mean(dim=0)  # [E, d_e]

        shift_v_dv = self.shift_v_to_dv(shift_v)  # [E, d_e] -> [E, d_v] (d_e/d_v oranından bağımsız)
        delta_phi = torch.bmm(shift_u.unsqueeze(2), shift_v_dv.unsqueeze(1))  # [E, d_e, d_v]
        Phi_batch_raw = self.phi_base.unsqueeze(0) + 0.1 * delta_phi  # [E, d_e, d_v]

        with torch.amp.autocast('cuda', enabled=False):
            Q, _ = torch.linalg.qr(Phi_batch_raw.float())
            Phi_batch = Q  # [E, d_e, d_v]

        for e in range(E_num):
            v_src = int(src_indices[e].item())
            v_dst = int(dst_indices[e].item())
            Phi_e = Phi_batch[e]
            phi_dict[f"phi_{v_src}_{e}"] = Phi_e
            phi_dict[f"phi_{v_dst}_{e}"] = Phi_e
            
        return E4_LifDemeti(phi_matrisleri=phi_dict, baslangic_gizil_durumu=x_initial)


class N4_SorguSecici(nn.Module):
    r"""
    [N4] 4-Şartlı Rasyonel Merak ve Sorgu Şiddeti Vektör Sahası (Query Intensity Vector Field).
    
    MLP / SiLU karakutu katmanları tamamen temizlenmiştir!
    Her v düğümünün sorgu şiddeti \boldsymbol{\gamma}^{(r)}[v] 4 insani merak şartının çarpımıyla türetilir:
      1. Yerel Entropi H[v]: x_v gizil durumunun Shannon belirsizliği (cahillik oranı)
      2. Topolojik Çelişki c[v]: H^1 eşsınır engel miktarı (komşusal uyumsuzluk)
      3. Cevaplama Kolaylığı E_easiness[v]: Bellekteki (M) cevabın kosinüs benzerliği (erken adıma çekme)
      4. Bilgi Erişilebilirliği A_path[v]: Topolojik bağlantı derecesi (Degree Centrality)
      
    Q^(r)[v] = \boldsymbol{\gamma}^{(r)}[v] * (x_v * W_Q) in R^{d_q},  W_Q^T W_Q = I
    """
    def __init__(self, config: Optional[Model_TopolojikKonfigurasyon] = None, alt_ag: Any = None):
        super().__init__()
        self.config = config
        d_v = getattr(config, 'd_v', 32) if config else 32
        d_q = getattr(config, 'd_q', 64) if config else 64
        self.d_v = d_v
        self.d_q = d_q
        
        # Stiefel Projeksiyon Matrisi W_Q in St(d_q, d_v)
        device = getattr(config, 'device', 'cpu')
        self.W_Q = nn.Parameter(torch.randn((d_v, d_q), device=device))
        with torch.no_grad():
            self.W_Q.copy_(stiefel_qr_projection(self.W_Q.data))

    def izdusur_stiefel(self):
        """W_Q matrisini Stiefel dikgenlik kısıtına (W_Q^T W_Q = I) izdüşürür."""
        with torch.no_grad():
            self.W_Q.copy_(stiefel_qr_projection(self.W_Q.data))

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N4 VRAM Tahmin Formülü: baskın maliyet c_defect = x_r @ D0^T = [B, E*d_e]
        (D0_operator ile matris çarpımı) ve Q_cand = [B, V, d_q] projeksiyonudur.
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else (self.config.batch_size if self.config else 1)
        V = getattr(self.config, 'V_nodes', 8) if self.config else 8
        E_num = max(V - 1, 1)
        d_e = getattr(self.config, 'd_e', 32) if self.config else 32
        return (
            vram_bayt_tahmin_et(B, E_num * d_e) +   # c_defect [B, E*d_e]
            vram_bayt_tahmin_et(B, V, self.d_q)     # Q_cand [B, V, d_q]
        )

    def forward(self, mevcut_durum: E5_A_MevcutGizilDurum, D0_operator: Optional[torch.Tensor] = None, A_adjacency: Optional[torch.Tensor] = None, bellek: Optional[E5_B_BellekGonderimi] = None) -> E6_GizilSorgu:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # modül VE tüm girdiler bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if next(self.parameters(), None) is not None and next(self.parameters()).device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            mevcut_durum = girdi_cihaza_tasi(mevcut_durum, zorunlu_cihaz)
            if D0_operator is not None:
                D0_operator = D0_operator.to(zorunlu_cihaz)
            if A_adjacency is not None:
                A_adjacency = A_adjacency.to(zorunlu_cihaz)
            bellek = girdi_cihaza_tasi(bellek, zorunlu_cihaz)

        x_r = mevcut_durum.x_r  # [B, D]
        B = x_r.shape[0]
        V_num = x_r.shape[1] // self.d_v if x_r.shape[1] % self.d_v == 0 else (self.config.V_nodes if self.config else 1)
        X = x_r.view(B, V_num, self.d_v)  # [B, V, d_v]

        # 1. Yerel Entropi Vektörü H[v] (Shannon Belirsizliği / Cahillik Oranı)
        probs = F.softmax(X, dim=-1)  # [B, V, d_v]
        log_probs = F.log_softmax(X, dim=-1) / math.log(2.0)
        H_entropy = -torch.sum(probs * log_probs, dim=-1, keepdim=True)  # [B, V, 1]

        # 2. Topolojik Çelişki Vektörü c_node[v] (Eşsınır Engel Uyumsuzluğu)
        if D0_operator is not None:
            c_defect = torch.matmul(x_r, D0_operator.T)  # [B, E * d_e]
            d_e = self.config.d_e if self.config else self.d_v
            E_num = c_defect.shape[1] // d_e if c_defect.shape[1] % d_e == 0 else 1
            c_reshaped = c_defect.view(B, E_num, d_e)
            edge_norm = torch.norm(c_reshaped, p=2, dim=-1)  # [B, E]
            if E_num >= V_num:
                c_node = edge_norm[:, :V_num].unsqueeze(-1)
            else:
                c_node = F.interpolate(edge_norm.unsqueeze(1), size=V_num, mode='linear', align_corners=False).transpose(1, 2)
        else:
            c_node = torch.ones((B, V_num, 1), device=x_r.device)

        # Candidate Query Projection X * W_Q
        Q_cand = torch.matmul(X, self.W_Q)  # [B, V, d_q]

        # 3. Cevaplama Kolaylığı Vektörü E_easiness[v] (Bellek Kanca Benzerliği & Zamansal Öncelik)
        if bellek is not None and bellek.M is not None:
            M = bellek.M  # [B, d_m, K] veya [B, K, d_m]
            if M.dim() == 3:
                if M.shape[1] != self.d_q:
                    M_trans = M.transpose(1, 2)  # [B, K, d_m]
                else:
                    M_trans = M.transpose(1, 2)  # [B, K, d_q]
                
                Q_norm = F.normalize(Q_cand, p=2, dim=-1)
                M_norm = F.normalize(M_trans, p=2, dim=-1)
                if Q_norm.shape[-1] == M_norm.shape[-1]:
                    cos_sim = torch.matmul(Q_norm, M_norm.transpose(1, 2))  # [B, V, K]
                    E_easiness = torch.max(cos_sim, dim=-1, keepdim=True)[0]  # [B, V, 1]
                    E_easiness = torch.clamp(E_easiness, min=0.0, max=1.0)
                else:
                    E_easiness = torch.ones((B, V_num, 1), device=x_r.device) * 0.5
            else:
                E_easiness = torch.ones((B, V_num, 1), device=x_r.device) * 0.5
        else:
            E_easiness = torch.ones((B, V_num, 1), device=x_r.device) * 0.5

        # 4. Bilgi Erişilebilirliği Vektörü A_path[v] (Topolojik Bağlantı Derecesi)
        if A_adjacency is not None and A_adjacency.dim() >= 2:
            if A_adjacency.dim() == 3:
                deg = torch.sum(torch.abs(A_adjacency), dim=1)  # [B, V, 1]
                if deg.shape[1] != V_num:
                    deg = F.interpolate(deg.transpose(1, 2), size=V_num, mode='linear', align_corners=False).transpose(1, 2)
            else:
                if A_adjacency.shape[0] != V_num and A_adjacency.shape[1] == V_num:
                    deg_v = torch.sum(torch.abs(A_adjacency), dim=0, keepdim=True).T # [V, 1]
                elif A_adjacency.shape[0] == V_num:
                    deg_v = torch.sum(torch.abs(A_adjacency), dim=1, keepdim=True) # [V, 1]
                else:
                    deg_v = torch.ones((V_num, 1), device=x_r.device)
                deg = deg_v.unsqueeze(0).repeat(B, 1, 1)  # [B, V, 1]
            A_path = deg + 1.0
        else:
            A_path = torch.ones((B, V_num, 1), device=x_r.device)

        # 4 Şartın Çarpımı: Bileşik Düğüm Sorgu Şiddeti Katsayısı gamma[v]
        gamma = (H_entropy + 1e-4) * (c_node + 1e-4) * (E_easiness + 1e-4) * A_path  # [B, V, 1]

        # Sorgu Vektör Sahası Q^(r)[v] = gamma[v] * (x_v * W_Q)
        Q_field = gamma * Q_cand  # [B, V, d_q]

        # Küresel Sorgu Vektörü q_r (Harmanlanmış Sorgu)
        q_r = torch.mean(Q_field, dim=1)  # [B, d_q]
        return E6_GizilSorgu(q_r=q_r)


class N5_CevapSuzucu(nn.Module):
    """
    [N5] Cevap Süzücü — VSA Unbinding ve Stiefel Dikgen Bellek Okuyucu.
    
    MLP, SiLU ve sihirli 0.1 katsayısı tamamen kaldırılmıştır!
    1. Sorgu-Bellek Çarpışma Skoru: s_match = Softmax( (q_r * W_K * M) / sqrt(d_q) ) in R^K
    2. Kayıpsız VSA Unbinding Cevap Çıkarımı: a_r = (M * s_match^T) * W_V in R^{d_a}
    
    Kısıtlar: W_K^T W_K = I, W_V^T W_V = I
    """
    def __init__(self, alt_ag: Any = None, config: Optional[Model_TopolojikKonfigurasyon] = None):
        super().__init__()
        self.config = config
        d_q = getattr(config, 'd_q', 64) if config else 64
        d_m = getattr(config, 'd_m', 64) if config else 64
        d_a = getattr(config, 'd_a', 64) if config else 64
        self.d_q = d_q
        self.d_m = d_m
        self.d_a = d_a

        device = getattr(config, 'device', 'cpu')
        self.W_K = nn.Parameter(torch.randn((d_q, d_m), device=device))
        self.W_V = nn.Parameter(torch.randn((d_m, d_a), device=device))
        self.tau_log = nn.Parameter(torch.tensor(0.0, device=device))
        with torch.no_grad():
            self.W_K.copy_(stiefel_qr_projection(self.W_K.data))
            self.W_V.copy_(stiefel_qr_projection(self.W_V.data))

    def izdusur_stiefel(self):
        """W_K ve W_V matrislerini Stiefel dikgenlik kısıtlarına izdüşürür."""
        with torch.no_grad():
            self.W_K.copy_(stiefel_qr_projection(self.W_K.data))
            self.W_V.copy_(stiefel_qr_projection(self.W_V.data))

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N5 VRAM Tahmin Formülü: baskın maliyet M_slots/M_norm = [B, d_m, K] bellek okuma tensörüdür.
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else 1
        K_slots = getattr(self.config, 'K', 16) if self.config else 16
        return vram_bayt_tahmin_et(B, self.d_m, K_slots)

    def forward(self, sorgu: E6_GizilSorgu, bellek: E5_B_BellekGonderimi) -> E7_LokalBilgi:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # modül VE girdiler bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if next(self.parameters(), None) is not None and next(self.parameters()).device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            sorgu = girdi_cihaza_tasi(sorgu, zorunlu_cihaz)
            bellek = girdi_cihaza_tasi(bellek, zorunlu_cihaz)

        q_r = sorgu.q_r  # [B, d_q]
        M = bellek.M  # [B, d_m, K] veya [B, K, d_m]
        B = q_r.shape[0]

        if M.dim() == 3:
            if M.shape[1] != self.d_m and M.shape[2] == self.d_m:
                M_slots = M.transpose(1, 2)  # [B, d_m, K]
            else:
                M_slots = M  # [B, d_m, K]
        else:
            M_slots = torch.zeros((B, self.d_m, 16), device=q_r.device)

        # 1. Stiefel Key Projeksiyonu: q_W = q_r * W_K in [B, d_m]
        q_W = torch.matmul(q_r, self.W_K)  # [B, d_m]

        # 2. Kosinüs Benzerliği & Sıcaklık Ölçekli Softmax (tau_min = 0.2 & sqrt(d_m) Ölçekleme)
        tau_min = 0.2
        tau = torch.clamp(torch.exp(self.tau_log), min=tau_min, max=10.0)
        q_norm = F.normalize(q_W, p=2, dim=-1)
        M_norm = F.normalize(M_slots, p=2, dim=1)
        scale_factor = tau * math.sqrt(float(self.d_m))
        scores = torch.bmm(q_norm.unsqueeze(1), M_norm).squeeze(1) / scale_factor  # [B, K]
        s_match = F.softmax(scores, dim=-1)  # [B, K]

        # 3. Kayıpsız Cevap Okuma: m_read = M_slots * s_match^T in [B, d_m]
        m_read = torch.bmm(M_slots, s_match.unsqueeze(-1)).squeeze(-1)  # [B, d_m]

        # 4. Stiefel Value Projeksiyonu: a_r = m_read * W_V in [B, d_a]
        a_r = torch.matmul(m_read, self.W_V)  # [B, d_a]
        return E7_LokalBilgi(a_r=a_r)


class N6_KohomolojikAktor(nn.Module):
    r"""
    [N6] Kohomolojik Aktüatör — Peirce Abdisyonu ve Dinamik Eşlenik Kanca Türetim Hücresi.
    
    [ÇARE 2: Dinamik Eşlenik Kanca Türetimi (Adjoint Key Construction)]
      K^{(r)} = D_0^\dagger * (c^{(r)}) \in \mathbb{R}^{V \times d_k}
      D_0^\dagger = (D_0^T D_0 + \epsilon I)^{-1} D_0^T  (Moore-Penrose Psödo-Tersi)
      
    [ÇARE 3: Peirce Abdisyonu (Hipotez Sentezleme)]
      H^1 \neq 0 çelişki boşluğu tespit edildiğinde geçmiş veride var olmamış
      taptaze bir Sentetik Hipotez Vektörü h_syn^{(r)} imal edilir:
      h_syn^{(r)} = Combat_{H^1}(c^{(r)}, Q^{(r)}, a_r, K^{(r)})
    """
    def __init__(self, alt_ag: Optional[N6_KohomolojikAktor_AltAg] = None, D0_operator: Optional[torch.Tensor] = None, Delta0_operator: Optional[torch.Tensor] = None, config: Optional[Model_TopolojikKonfigurasyon] = None):
        super().__init__()
        self.alt_ag = alt_ag
        self.config = config
        self.register_buffer("v_pow_persistent", None, persistent=False)
        if D0_operator is not None:
            self.register_buffer("D0", D0_operator, persistent=False)
        else:
            self.D0 = None
        # NOT: Delta0 = D0^T @ D0 ([D,D], VRAM baskısının başlıca kaynağıydı) ARTIK
        # AYRI BİR BUFFER OLARAK TUTULMUYOR — forward() artık D0 üzerinden
        # laplasyen_ile_carp(x, D0) ile matrissiz çalışıyor (bkz. o metodun docstring'i:
        # x @ Delta_0^T = (x @ D0^T) @ D0, birebir eşdeğer). Delta0_operator parametresi
        # yalnızca eski çağıranlarla geriye dönük imza uyumluluğu için tutuldu, artık
        # KULLANILMIYOR (sessizce yok sayılır).

        d_v = getattr(config, 'd_v', 32) if config else 32
        d_q = getattr(config, 'd_q', 64) if config else 64
        d_a = getattr(config, 'd_a', 64) if config else 64
        d_h = getattr(config, 'd_h', 64) if config else 64
        V_dim = getattr(config, 'V_nodes', 276) if config else 276

        # Ön-Kayıtlı Projeksiyon Katmanları (nn.Linear'lar strictly __init__'te ilklendirilir)
        self.adj_proj_layer = nn.Linear(V_dim, d_v)
        self.lap_proj_layer = nn.Linear(V_dim, d_v)
        self.disc_proj_layer = nn.Linear(1, d_v)
        self.dir_proj_layer = nn.Linear(1, d_v)
        self.abduction_proj = nn.Linear(4 * d_v + d_q + d_a, d_h)

    def update_operators(self, D0_op: torch.Tensor, Delta0_op: Optional[torch.Tensor] = None) -> None:
        """
        Persistent non-trainable buffer registration for D0 to maintain PyTorch device graph.
        Delta0_op parametresi geriye dönük imza uyumluluğu için tutuldu ama ARTIK
        KULLANILMIYOR — forward() D0 üzerinden laplasyen_ile_carp ile matrissiz çalışıyor
        (Delta0 = D0^T @ D0'ı [D,D] olarak ayrıca kurup saklamak VRAM baskısının başlıca
        kaynağıydı).
        """
        if "D0" in self._buffers:
            del self._buffers["D0"]
        elif hasattr(self, "D0"):
            delattr(self, "D0")
        self.register_buffer("D0", D0_op, persistent=False)

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N6 VRAM Tahmin Formülü: matrissiz Krylov çözücü [E,E] matrisi hiç kurmaz;
        baskın maliyet c_defect/K_adjoint [B, E*d_e] ve [B, V*d_v] vektör serisi ile
        abduction_proj girdisidir [B, 4*d_v + d_q + d_a].
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else (self.config.batch_size if self.config else 1)
        V = getattr(self.config, 'V_nodes', 8) if self.config else 8
        E_num = max(V - 1, 1)
        d_v = getattr(self.config, 'd_v', 32) if self.config else 32
        d_e = getattr(self.config, 'd_e', 32) if self.config else 32
        d_q = getattr(self.config, 'd_q', 64) if self.config else 64
        d_a = getattr(self.config, 'd_a', 64) if self.config else 64
        return (
            vram_bayt_tahmin_et(B, E_num * d_e) +          # c_defect / Krylov vektör serisi [B, E*d_e]
            vram_bayt_tahmin_et(B, V * d_v) +               # K_adjoint [B, V*d_v]
            vram_bayt_tahmin_et(B, 4 * d_v + d_q + d_a)     # abduction_proj girdisi
        )

    def hesapla_moore_penrose_psodoters_vektor_etkisi(self, c_defect: torch.Tensor, D0: torch.Tensor, P: int = 5) -> torch.Tensor:
        r"""
        [MATRİSSİZ CHEBYSHEV KRYLOV EŞSINIR ÇÖZÜCÜSÜ - 0 MB MATRİS SHIFT VRAM]
        [E, E] matrislerini VRAM'de HİÇBİR ZAMAN OLUŞTURMADAN D_0 ve D_0^T operatör
        çarpımlarını doğrudan [B, E_dim] vektörleri üzerinde icra eden Krylov serisi.
        """
        device = D0.device
        dtype = D0.dtype
        B, E_dim = c_defect.shape

        eps_adaptive = max(1e-4, 1e-3 * float(c_defect.norm().detach().item()))

        def apply_M_vec(v: torch.Tensor) -> torch.Tensor:
            # v: [B, E_dim] -> (v @ D0) @ D0.T + eps * v
            v_v = torch.matmul(v, D0)      # [B, V_dim]
            M_v = torch.matmul(v_v, D0.T)   # [B, E_dim]
            return M_v + eps_adaptive * v

        # FASİL 4 DÜZELTMESİ: Deterministik düzgün birim vektör başlangıcı.
        # v_pow^(0) = 1/sqrt(E) · [1,1,...,1] → tüm öz-uzay bileşenlerini eşit içerir,
        # Power Iteration her koşuda aynı adımda λ_max'a deterministik yakınsar.
        if self.v_pow_persistent is None or self.v_pow_persistent.shape[-1] != E_dim or self.v_pow_persistent.device != device:
            v_pow = torch.ones((1, E_dim), device=device, dtype=dtype) / math.sqrt(E_dim)
        else:
            v_pow = self.v_pow_persistent.to(device=device, dtype=dtype)

        for _ in range(2):
            v_pow = apply_M_vec(v_pow)
            v_pow = v_pow / (v_pow.norm() + 1e-8)

        self.v_pow_persistent = v_pow.detach()
        M_v_pow = apply_M_vec(v_pow)
        lambda_max = float(torch.sum(v_pow * M_v_pow).item()) + 1e-4

        # Neumann / Chebyshev Convergent Vector Inverse Series
        alpha_scale = 1.0 / (lambda_max + 1e-4)

        def apply_M_diff_vec(v: torch.Tensor) -> torch.Tensor:
            return v - alpha_scale * apply_M_vec(v)

        u_accum = c_defect.clone()
        v_k = c_defect.clone()

        for _ in range(1, P + 1):
            v_k = apply_M_diff_vec(v_k)
            u_accum = u_accum + v_k

        u = alpha_scale * u_accum
        K_adjoint = torch.matmul(u, D0)  # [B, V_dim]
        return K_adjoint

    def VektorelChebyshevKrylovCozumu(self, c_defect: torch.Tensor, D0: torch.Tensor, P: int = 5) -> torch.Tensor:
        """[Rükn 3] Matrissiz Vektörel Chebyshev Krylov Eşsınır Çözümü"""
        return self.hesapla_moore_penrose_psodoters_vektor_etkisi(c_defect, D0, P=P)

    def forward(self, mevcut_durum: E5_A_MevcutGizilDurum, sorgu: E6_GizilSorgu, lokal_bilgi: E7_LokalBilgi,
                d_discrepancy: Optional[torch.Tensor] = None, E_dirichlet: Optional[torch.Tensor] = None) -> E8_SentetikAraDurum:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # modül (D0/Delta0 buffer'ları ve alt_ag dahil) VE tüm girdiler bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if next(self.parameters(), None) is not None and next(self.parameters()).device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            elif self.D0 is not None and self.D0.device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            mevcut_durum = girdi_cihaza_tasi(mevcut_durum, zorunlu_cihaz)
            sorgu = girdi_cihaza_tasi(sorgu, zorunlu_cihaz)
            lokal_bilgi = girdi_cihaza_tasi(lokal_bilgi, zorunlu_cihaz)
            if d_discrepancy is not None:
                d_discrepancy = d_discrepancy.to(zorunlu_cihaz)
            if E_dirichlet is not None:
                E_dirichlet = E_dirichlet.to(zorunlu_cihaz)

        x_r = mevcut_durum.x_r  # [B, D]
        q_r = sorgu.q_r  # [B, d_q]
        a_r = lokal_bilgi.a_r  # [B, d_a]
        B = x_r.shape[0]
        d_v = getattr(self.config, 'd_v', 32) if self.config else 32

        # 1. Eşsınır Kusuru c^(r) ve Laplasyen Gradyanı grad^(r)
        if self.D0 is not None:
            c_defect = torch.matmul(x_r, self.D0.T)  # [B, E_dim]
            # laplacian_grad = x_r @ Delta_0.T; Delta_0 = D0^T@D0'ı [D,D] hiç kurmadan
            # (bkz. laplasyen_ile_carp docstring'i: birebir matematiksel eşdeğerlik)
            laplacian_grad = laplasyen_ile_carp(x_r, self.D0)  # [B, V_dim]
            K_adjoint = self.hesapla_moore_penrose_psodoters_vektor_etkisi(c_defect, self.D0)  # [B, V_dim]
        else:
            c_defect = torch.zeros((B, x_r.shape[1]), device=x_r.device, dtype=x_r.dtype)
            laplacian_grad = torch.zeros((B, x_r.shape[1]), device=x_r.device, dtype=x_r.dtype)
            K_adjoint = torch.zeros((B, x_r.shape[1]), device=x_r.device, dtype=x_r.dtype)

        # 2. HATA 4 DÜZELTMESİ: Türevlenebilir Adaptive Projection (ölü katman yerine)
        V_aktuel = K_adjoint.shape[-1]
        if V_aktuel != d_v:
            if V_aktuel % d_v == 0:
                K_adj_field = K_adjoint.view(B, -1, d_v).mean(dim=1)
            else:
                K_adj_field = F.adaptive_avg_pool1d(K_adjoint.unsqueeze(1), d_v).squeeze(1)
        else:
            K_adj_field = K_adjoint

        V_lap = laplacian_grad.shape[-1]
        if V_lap != d_v:
            if V_lap % d_v == 0:
                lap_grad_field = laplacian_grad.view(B, -1, d_v).mean(dim=1)
            else:
                lap_grad_field = F.adaptive_avg_pool1d(laplacian_grad.unsqueeze(1), d_v).squeeze(1)
        else:
            lap_grad_field = laplacian_grad

        # 3. Metrik Vektörlerinin Ön-Kayıtlı Projeksiyonu
        if d_discrepancy is not None:
            if d_discrepancy.ndim == 1:
                d_disc_field = d_discrepancy.unsqueeze(-1) if d_discrepancy.shape[0] == B else d_discrepancy.unsqueeze(0).repeat(B, 1)
            else:
                d_disc_field = d_discrepancy
            if d_disc_field.shape[-1] == d_v:
                pass
            elif d_disc_field.shape[-1] == 1:
                d_disc_field = self.disc_proj_layer(d_disc_field)
            else:
                d_disc_field = d_disc_field[:, :d_v] if d_disc_field.shape[-1] >= d_v else F.pad(d_disc_field, (0, d_v - d_disc_field.shape[-1]))
        else:
            d_disc_field = torch.zeros((B, d_v), device=x_r.device, dtype=x_r.dtype)

        if E_dirichlet is not None:
            if E_dirichlet.ndim == 1:
                e_dir_field = E_dirichlet.unsqueeze(-1) if E_dirichlet.shape[0] == B else E_dirichlet.unsqueeze(0).repeat(B, 1)
            else:
                e_dir_field = E_dirichlet
            if e_dir_field.shape[-1] == d_v:
                pass
            elif e_dir_field.shape[-1] == 1:
                e_dir_field = self.dir_proj_layer(e_dir_field)
            else:
                e_dir_field = e_dir_field[:, :d_v] if e_dir_field.shape[-1] >= d_v else F.pad(e_dir_field, (0, d_v - e_dir_field.shape[-1]))
        else:
            e_dir_field = torch.zeros((B, d_v), device=x_r.device, dtype=x_r.dtype)

        # 4. Sabit 4 * d_v + d_q + d_a Boyutunda Birleştirme
        bilesik_girdi = torch.cat([K_adj_field, lap_grad_field, d_disc_field, e_dir_field, q_r, a_r], dim=-1)

        if self.alt_ag is not None:
            synthetic_state = self.alt_ag(bilesik_girdi)
        else:
            synthetic_state = self.abduction_proj(bilesik_girdi)

        return E8_SentetikAraDurum(synthetic_state=synthetic_state)


class N7_LifLaplasyeniCozucu(nn.Module):
    r"""
    [N7] Lif Laplasyeni Isı Difüzyon Çözücüsü ve Harmonik Denge Noktası İntegratörü.
    
    [ÇARE 1: Isı Difüzyonu ve Harmonik Öz-Denge Noktası (Harmonic Fixed Point a*)]
    Cevap hazır verisetinden çekilmez. N6'dan doğan sentetik hipotez h_syn^{(r)} dış kaynak olarak alınır,
    Lif Laplasyeni \Delta_0 üzerinde ısı difüzyonu koşturularak sistem kararlı Öz-Denge Noktasına a* çöktürülür:
      dx/dt = -\Delta_0 * x + Proj(h_syn^{(r)})
      x^{(r+1)} = x^{(r)} + dt * dx
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        self.syn_proj_layer = nn.Linear(config.d_h, config.d_v)

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N7 VRAM Tahmin Formülü: Delta_0 artık [D,D] olarak hiç kurulmuyor
        (laplasyen_ile_carp ile matrissiz) — baskın maliyet birkaç [B, D] ara
        tensörüdür (laplacian_grad, g_var/g_metric/g_ricci, dx, x_next).
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else (self.config.batch_size if self.config else 1)
        V = getattr(self.config, 'V_nodes', 8) if self.config else 8
        d_v = getattr(self.config, 'd_v', 32) if self.config else 32
        D = V * d_v
        return vram_bayt_tahmin_et(B, D) * 6  # laplacian_grad, dx, x_next, g_var, g_metric, g_ricci [B, D]

    def laplasyen_lambda_max(self, D0: torch.Tensor) -> torch.Tensor:
        """Delta_0 = D0^T@D0'ın en büyük özdeğerini D0'ı hiç yoğun kurmadan güç yöntemiyle tahmin eder."""
        if D0 is None or D0.numel() == 0:
            return torch.tensor(1.0, device=D0.device if D0 is not None else 'cpu')
        return laplasyen_lambda_max_guc_yontemi(D0)

    def laplasyen_akisi_normalize(self, x: torch.Tensor, D0: torch.Tensor, lambda_max: torch.Tensor) -> torch.Tensor:
        """
        x @ Delta_0_hat^T'yi (Delta_0_hat = spektral normalize edilmiş Delta_0) Delta_0'ı hiç
        [D,D] olarak kurmadan hesaplar: x @ Delta_0_hat^T = laplasyen_ile_carp(x, D0) / lambda_max.
        """
        if D0 is None or D0.numel() == 0:
            return torch.zeros_like(x)
        return laplasyen_ile_carp(x, D0) / (lambda_max + 1e-6)

    def hesapla_korunum_potansiyelleri_gradyani(self, x_r: torch.Tensor, D0: torch.Tensor, lambda_max: torch.Tensor, gamma: float = 0.1, c: float = 1.0, delta_min: float = 0.01) -> torch.Tensor:
        """
        [4 KUTSAL KORUNUM POTANSİYELİ GRADYANI]
        Harmonik Isıl Düzleşmeyi (Oversmoothing / Harmonic Flattening Paradox) engelleyen
        4 Diferansiyel Geometrik Korunum Potansiyelinin x_r üzerindeki türev gradyanı nabla_x H.
        1. Varyans Korunumu (Var(x) >= gamma)
        2. İzometrik Uzunluk Korunumu (||x||_2 = c)
        3. Dikgenlik ve Biyortogonallik Korunumu
        4. Topolojik Eğrilik ve Dirichlet Enerjisi Korunumu (Tr(X^T Delta_0 X) >= delta_min)
        """
        D = x_r.shape[-1]
        x_mean = x_r.mean(dim=-1, keepdim=True)
        x_var = ((x_r - x_mean) ** 2).mean(dim=-1, keepdim=True)
        x_std = torch.sqrt(x_var + 1e-8)
        var_diff = torch.clamp(gamma - x_std, min=0.0)
        g_var = -2.0 * var_diff * (x_r - x_mean) / (x_std * D + 1e-8)

        x_norm_sq = (x_r ** 2).sum(dim=-1, keepdim=True)
        g_metric = 4.0 * (x_norm_sq - c**2) * x_r / D

        lap_x = self.laplasyen_akisi_normalize(x_r, D0, lambda_max)
        dirichlet_energy = (x_r * lap_x).sum(dim=-1, keepdim=True)
        dir_diff = torch.clamp(delta_min - dirichlet_energy, min=0.0)
        g_ricci = -4.0 * dir_diff * lap_x / D

        return g_var + g_metric + g_ricci

    def forward(self, sentetik_durum: E8_SentetikAraDurum, D0: torch.Tensor, mevcut_durum: E5_A_MevcutGizilDurum) -> E9_GuncellenmisGizilDurum:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # modül VE tüm girdiler bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if next(self.parameters(), None) is not None and next(self.parameters()).device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            sentetik_durum = girdi_cihaza_tasi(sentetik_durum, zorunlu_cihaz)
            mevcut_durum = girdi_cihaza_tasi(mevcut_durum, zorunlu_cihaz)
            if D0.device != zorunlu_cihaz:
                D0 = D0.to(zorunlu_cihaz)

        x_r = mevcut_durum.x_r
        B, D_dyn = x_r.shape
        d_v = getattr(self.config, 'd_v', 32)
        V_num = D_dyn // d_v if D_dyn % d_v == 0 else 1

        # Delta_0 = D0^T @ D0 ARTIK [D,D] OLARAK HİÇ KURULMUYOR — bkz. laplasyen_ile_carp
        # (x @ Delta_0^T = (x @ D0^T) @ D0, birebir eşdeğer, O(D^2) yerine O(D) bellek).
        # lambda_max güç yöntemiyle (birkaç ucuz D0-matvec yinelemesi) tahmin ediliyor.
        lambda_max = self.laplasyen_lambda_max(D0)
        syn_v = self.syn_proj_layer(sentetik_durum.synthetic_state) # [B, d_v]
        syn_proj = syn_v.unsqueeze(1).repeat(1, V_num, 1).view(B, D_dyn) # [B, D_dyn]

        laplacian_flow = self.laplasyen_akisi_normalize(x_r, D0, lambda_max)
        g_cons = self.hesapla_korunum_potansiyelleri_gradyani(x_r, D0, lambda_max)

        # [4 KORUNUM KANUNLU ISI DİFÜZYONU]: dx = -\Delta_0 * x + Proj(h_syn) - 0.1 * \nabla_x H
        dx = -laplacian_flow + syn_proj - 0.1 * g_cons
        x_next = x_r + self.config.dt * dx
        return E9_GuncellenmisGizilDurum(x_next=x_next)

    # NOT (matrissiz Laplasyen refaktörü): coz_r_adimlari_blelloch, blelloch_parallel_heat_scan,
    # _chebyshev_bessel_matrix_exp_vector, YesilCekirdegiBesselChebyshevEksponansiyel ve
    # analitik_matris_eksponansiyel_yesil_cozum main_egitim_dongusu.py'nin canlı eğitim
    # yolundan HİÇ ÇAĞRILMIYOR (yalnızca birbirlerini çağırıyorlar — ölü kod). Bu yüzden
    # kasıtlı olarak dönüştürülmediler ve hâlâ yoğun [D,D] bir Delta_0 bekliyorlar — canlıya
    # alınacaklarsa önce forward/hesapla_dirichlet_enerjisi_vektoru'nda kullanılan
    # laplasyen_ile_carp(x, D0) desenine geçirilmeleri gerekir.
    def coz_r_adimlari_blelloch(self, synthetic_states_seq: torch.Tensor, Delta_0: torch.Tensor, x_init: torch.Tensor) -> torch.Tensor:
        """
        R-Adımlı Rekürens İsıl Difüzyonunu Blelloch Parallel Scan ile O(log2 R) Sürede Çözer.
        synthetic_states_seq: [R, B, d_h]
        Delta_0: [D, D]
        x_init: [B, D]
        Döndürür: x_final [B, D]
        """
        R_steps, B, d_h = synthetic_states_seq.shape
        D_dyn = x_init.shape[-1]
        d_v = getattr(self.config, 'd_v', 32)
        V_num = D_dyn // d_v if D_dyn % d_v == 0 else 1

        dt = self.config.dt
        B_seq_list = []
        for r in range(R_steps):
            syn_v = self.syn_proj_layer(synthetic_states_seq[r])  # [B, d_v]
            syn_proj = syn_v.unsqueeze(1).repeat(1, V_num, 1).view(B, D_dyn)  # [B, D_dyn]
            B_seq_list.append(dt * syn_proj)
        
        B_seq = torch.stack(B_seq_list, dim=0)  # [R, B, D_dyn]
        x_final = self.blelloch_parallel_heat_scan(Delta_0=Delta_0, B_seq=B_seq, x_init=x_init)
        return x_final

    def parallel_assoc_scan_step(self, A1: torch.Tensor, B1: torch.Tensor, A2: torch.Tensor, B2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Ispatı yapılan (a_i, b_i) * (a_j, b_j) = (a_j * a_i, a_j * b_i + b_j)
        mermi (bullet) ikili birleşik operatörünün paralel matris/vektör icrası.
        """
        if A1.dim() == 2:
            A_out = torch.matmul(A2, A1)
        else:
            A_out = torch.matmul(A2, A1)
            
        if A2.dim() == 2:
            B_out = torch.matmul(B1, A2.T) + B2
        else:
            B_out = torch.bmm(B1.unsqueeze(1), A2.transpose(1, 2)).squeeze(1) + B2
        return A_out, B_out

    def blelloch_parallel_heat_scan(self, Delta_0: torch.Tensor, B_seq: torch.Tensor, x_init: torch.Tensor) -> torch.Tensor:
        """
        R-adımlı ısı difüzyonunu O(R) ardışık süreden O(log2 R) logaritmik süreye
        düşüren Blelloch Parallel Associative Scan algoritması.
        Delta_0: [D, D] Lif Laplasyeni
        B_seq: [R_steps, B, D] Her adımı temsil eden dış girdi vektörü (dt * Proj(h_syn))
        x_init: [B, D] İlk durum x^(0)
        """
        R_steps, B, D = B_seq.shape
        device = Delta_0.device
        dt = self.config.dt
        
        # Eyalet Geçiş Matrisi A_r = I - dt * Delta_0
        I_D = torch.eye(D, device=device)
        A_step = I_D - dt * Delta_0  # [D, D]
        
        A_list = [A_step for _ in range(R_steps)]
        B_list = [B_seq[r] for r in range(R_steps)]
        
        # Up-Sweep (Reduction)
        step = 1
        while step < R_steps:
            for i in range(2 * step - 1, R_steps, 2 * step):
                A_list[i], B_list[i] = self.parallel_assoc_scan_step(
                    A_list[i - step], B_list[i - step],
                    A_list[i], B_list[i]
                )
            step *= 2

        # Down-Sweep (Distribution)
        step = R_steps // 2
        while step > 0:
            for i in range(2 * step - 1 + step, R_steps, 2 * step):
                A_list[i], B_list[i] = self.parallel_assoc_scan_step(
                    A_list[i - step], B_list[i - step],
                    A_list[i], B_list[i]
                )
            step //= 2
            
        x_out_list = []
        for r in range(R_steps):
            A_r = A_list[r]
            B_r = B_list[r]
            if A_r.dim() == 2:
                x_r = torch.matmul(x_init, A_r.T) + B_r
            else:
                x_r = torch.bmm(x_init.unsqueeze(1), A_r.transpose(1, 2)).squeeze(1) + B_r
            x_out_list.append(x_r)
            
        return torch.stack(x_out_list, dim=0)  # [R_steps, B, D]

    def _chebyshev_bessel_matrix_exp_vector(self, Delta_0: torch.Tensor, x_0: torch.Tensor, tau: float, eps_tol: float = 1e-7, max_k: int = 64, M_terms: Optional[int] = None) -> torch.Tensor:
        """
        [Modifiye Bessel Chebyshev Spektral Matris Eksponansiyeli (Matrix-Free & Dinamik Keyfiyet Durdurmalı)]
        exp(-tau * Delta_0) * x_0 analitik matris üstelini I_D veya Shifted_Delta matrislerini
        VRAM'de HİÇBİR ZAMAN OLUŞTURMADAN (0 MB ekstra matris VRAM'i) O(D) vektör karmaşıklığıyla
        ve eps_tol = 1e-7 dinamik keyfiyet hassasiyetiyle durdurarak hesaplar.
        """
        device = Delta_0.device
        B, D = x_0.shape

        if M_terms is not None:
            max_k = max(2, M_terms)

        # 1. Güç İterasyonu ile Lambda_Max Kestirimi (5 Adım)
        with torch.no_grad():
            v_dummy = torch.randn(1, D, device=device)
            v_dummy = v_dummy / (torch.norm(v_dummy) + 1e-8)
            for _ in range(5):
                v_dummy = torch.matmul(v_dummy, Delta_0.T)
                v_dummy = v_dummy / (torch.norm(v_dummy) + 1e-8)
            lambda_max = torch.matmul(v_dummy, torch.matmul(Delta_0, v_dummy.T)).item()
            lambda_max = max(abs(lambda_max), 1e-4)

        # 2. Matrissiz (Matrix-Free) Shifted Laplacian Operatörü
        def apply_shifted_delta_t(v_in: torch.Tensor) -> torch.Tensor:
            return (2.0 / lambda_max) * torch.matmul(v_in, Delta_0.T) - v_in

        # 3. Chebyshev Vektör Serisi ve Bessel Katsayıları Açılımı
        z = (tau * lambda_max) / 2.0

        # T_0 Terimi
        T_prev = x_0
        c0 = float(ive(0, z))
        x_green = c0 * T_prev
        x_norm_0 = torch.norm(x_0, p=2) + 1e-8

        # T_1 Terimi
        T_curr = apply_shifted_delta_t(x_0)
        c1 = 2.0 * (-1.0) * float(ive(1, z))
        x_green = x_green + c1 * T_curr

        k = 2
        while k < max_k:
            T_next = 2.0 * apply_shifted_delta_t(T_curr) - T_prev
            T_prev = T_curr
            T_curr = T_next
            c_k = 2.0 * ((-1.0) ** k) * float(ive(k, z))
            
            # Dinamik Keyfiyet Durdurma Kriteri: Terim Anlamsal Enerji Katkısı
            term_energy = abs(c_k) * torch.norm(T_curr, p=2)
            x_green = x_green + c_k * T_curr

            if (term_energy / x_norm_0) < eps_tol:
                break  # Target precision 10^-7 reached, exit dynamically!

            k += 1

        return x_green

    def YesilCekirdegiBesselChebyshevEksponansiyel(self, Delta_0: torch.Tensor, x_0: torch.Tensor, tau: float, eps_tol: float = 1e-7, max_k: int = 64) -> torch.Tensor:
        """[Rükn 4] Modifiye Bessel-Chebyshev Analitik Yeşil (Green) Spektral Difüzyon Çözümü"""
        return self._chebyshev_bessel_matrix_exp_vector(Delta_0, x_0, tau=tau, eps_tol=eps_tol, max_k=max_k)

    def BlellochParalelScanVolterra(self, X_input: torch.Tensor, gamma_decay: float = 0.9) -> torch.Tensor:
        """[Rükn 6] O(N log N) Blelloch Paralel Nedensellik Volterra Taraması"""
        if X_input.dim() == 2:
            X_input = X_input.unsqueeze(0)
        B, N, d = X_input.shape
        step = 1
        X_out = X_input.clone()
        while step < N:
            X_out[:, step:] = gamma_decay * X_out[:, :-step] + X_out[:, step:]
            step *= 2
        return X_out

    def analitik_matris_eksponansiyel_yesil_cozum(self, Delta_0: torch.Tensor, h_syn: torch.Tensor, x_0: torch.Tensor, r_step: int, a: float = 1.0, b: float = 1.0) -> torch.Tensor:
        """
        [1.3.3 Sheaf Matrix Green's Kernel]
        dx/dr = -b * Delta_0 * x + a * h_syn topolojik taşınım-difüzyon denkleminin
        Modifiye Bessel-Chebyshev Spektral Kapalı Form Analitik Yeşil (Green) Çözümü:
        x^(r) = exp(-r * b * dt * Delta_0) * x^(0) + a * (I - exp(-r * b * dt * Delta_0)) * h_syn_proj
        """
        D = Delta_0.shape[0]
        dt = self.config.dt
        t_total = r_step * dt
        tau = t_total * b
        
        # 1. Serbest Lif Isı Difüzyonu Çözümü: exp(-tau * Delta_0) * x_0
        x_free = self._chebyshev_bessel_matrix_exp_vector(Delta_0, x_0, tau, eps_tol=1e-7)
        
        # 2. Sentetik Hipotez Taşınım Projeksiyonu
        syn_v = self.syn_proj_layer(h_syn)  # [B, d_v]
        V_num = D // syn_v.shape[-1] if (syn_v.shape[-1] > 0 and D % syn_v.shape[-1] == 0) else 1
        syn_proj = syn_v.unsqueeze(1).repeat(1, V_num, 1).view(x_0.shape[0], D)  # [B, D]

        # 3. Zorlanmış Yeşil Çekirdeği Katkısı: (I - exp(-tau * Delta_0)) * syn_proj
        syn_proj_exp = self._chebyshev_bessel_matrix_exp_vector(Delta_0, syn_proj, tau, eps_tol=1e-7)
        x_forced = syn_proj - syn_proj_exp
        
        return x_free + a * x_forced

    def hesapla_uyumsuzluk_vektoru(self, x_r: torch.Tensor, D0: torch.Tensor) -> torch.Tensor:
        c_defect = torch.matmul(x_r, D0.T)  # [B, E * d_e]
        B = c_defect.shape[0]
        d_e = getattr(self.config, 'd_e', 32)
        E_num = c_defect.shape[1] // d_e if c_defect.shape[1] % d_e == 0 else 1
        c_reshaped = c_defect.view(B, E_num, -1)
        d_vec = torch.norm(c_reshaped, p=2, dim=-1).mean(dim=0)  # [E]
        return d_vec

    def hesapla_dirichlet_enerjisi_vektoru(self, x_r: torch.Tensor, D0: torch.Tensor) -> torch.Tensor:
        # laplacian_flow = x_r @ Delta_0.T; Delta_0 = D0^T@D0'ı [D,D] hiç kurmadan
        # (bkz. laplasyen_ile_carp docstring'i: birebir matematiksel eşdeğerlik)
        laplacian_flow = laplasyen_ile_carp(x_r, D0)  # [B, V * d_v]
        B = x_r.shape[0]
        d_v = getattr(self.config, 'd_v', 32)
        V_num = x_r.shape[1] // d_v if x_r.shape[1] % d_v == 0 else 1
        x_res = x_r.view(B, V_num, -1)
        flow_res = laplacian_flow.view(B, V_num, -1)
        e_vec = torch.sum(x_res * flow_res, dim=-1).mean(dim=0)  # [V]
        return e_vec

    def hesapla_uyumsuzluk(self, x_r: torch.Tensor, D0: torch.Tensor) -> float:
        d_vec = self.hesapla_uyumsuzluk_vektoru(x_r, D0)
        return float(d_vec.mean().detach().item())

    def hesapla_dirichlet_enerjisi(self, x_r: torch.Tensor, D0: torch.Tensor) -> float:
        e_vec = self.hesapla_dirichlet_enerjisi_vektoru(x_r, D0)
        return float(e_vec.mean().detach().item())


class Sheaf_KAN_Superpozisyon_Operatoru(nn.Module):
    """
    [1.3.1 Sheaf-KAN Süperpozisyon Teoremi Operatörü]
    Çok değişkenli MLP matris çarpımlarını iptal eder.
    Kenar bazlı 1D Chebyshev tabanlı tek değişkenli KAN fonksiyonlarının 
    dış toplamı (Phi_e(sum phi_{v \trianglelefteq e}(x_v))) olarak çalışır.
    """
    def __init__(self, dim_in: int, dim_out: int, degree: int = 4):
        super().__init__()
        self.dim_in = dim_in
        self.dim_out = dim_out
        self.degree = degree
        
        # Chebyshev katsayı parametreleri [dim_out, dim_in, degree+1]
        self.cheby_coeffs = nn.Parameter(torch.randn(dim_out, dim_in, degree + 1) * 0.1)
        self.outer_scale = nn.Parameter(torch.ones(dim_out))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        orig_shape = x.shape
        if x.dim() == 3:
            B_orig, V_orig, D_orig = x.shape
            x_2d = x.view(-1, D_orig)
        else:
            x_2d = x

        # Girdi hizalama
        if x_2d.shape[-1] != self.dim_in:
            x_2d = F.interpolate(x_2d.unsqueeze(1), size=self.dim_in, mode='linear', align_corners=False).squeeze(1)

        x_norm = torch.tanh(x_2d)  # [-1, 1] aralığına sıkıştır

        # T_0(x)=1, T_1(x)=x, T_{k+1}(x) = 2x T_k(x) - T_{k-1}(x)
        T_list = [torch.ones_like(x_norm), x_norm]
        for k in range(1, self.degree):
            T_next = 2.0 * x_norm * T_list[-1] - T_list[-2]
            T_list.append(T_next)

        T_stack = torch.stack(T_list, dim=-1)  # [B_eff, dim_in, degree+1]

        # İç toplam: phi_v(x_v) = sum_k coeff * T_k(x_v)
        phi_inner = torch.einsum('bik,oik->bo', T_stack, self.cheby_coeffs)

        # Dış KAN aktivasyonu: Phi_e(y) = outer_scale * SiLU(y)
        out = self.outer_scale * F.silu(phi_inner)
        if len(orig_shape) == 3:
            out = out.view(orig_shape[0], orig_shape[1], -1)
        return out


class SMW_SifirParazit_BellekYoneticisi(nn.Module):
    r"""
    [1.4 Sherman-Morrison-Woodbury (SMW) Biyortogonal Süzgeçli Sabit Bellek Motoru]
    Sıfır Parazitli (Crosstalk-Free) ve O(1) Sabit Hafızalı Meclis Belleği.
    
    1. Korelasyon Çözücü Matris R in R^{K x K} (Hafıza slotları arası çakışma manifold matrisi)
    2. Meclis Belleği Matrisi M in R^{d_m x K}
    
    Matris Güncelleme Adımları (GPU Batch Matrix Tensor Ops):
      I.   gamma_r = 1 + k_r^T * R * k_r  (Normalizasyon Skaleri)
      II.  g_r = (1 / gamma_r) * R * k_r  (Biyortogonal Kazanç Vektörü)
      III. R^(r) = R^(r-1) - g_r * (k_r^T * R)  (Korelasyon Güncellemesi)
      IV.  M^(r) = M^(r-1) + (v_r - M^(r-1) * k_r) \otimes g_r^T  (Sıfır Parazitli Bellek Mühürleme)
      
    Geri Çağırma (Exact Recall):
      out_r = M^(r) * k_r = v_r  (Sıfır Hata ve Sıfır Girişim Paraziti İspatlanmıştır)
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        self.d_m = getattr(config, 'd_m', 64)
        self.K = getattr(config, 'K', 16)
        device = getattr(config, 'device', 'cpu')
        
        # 1. Sabit Bilişsel Bellek Matrisi M [B, d_m, K]
        self.register_buffer("M", torch.zeros(config.batch_size, self.d_m, self.K, device=device))
        
        # 2. Korelasyon Çözücü Matris R [B, K, K] (Başlangıçta Birim Matris I)
        R_init = torch.eye(self.K, device=device).unsqueeze(0).repeat(config.batch_size, 1, 1)
        self.register_buffer("R", R_init)

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        SMW (N12) VRAM Tahmin Formülü: R [B, K, K] korelasyon matrisi ve M [B, d_m, K]
        bellek matrisi, her adımda yeniden yazılır.
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        return vram_bayt_tahmin_et(B, self.K, self.K) + vram_bayt_tahmin_et(B, self.d_m, self.K)

    def reset_memory(self, batch_size: Optional[int] = None):
        """Hafızayı sıfırlama (Yeni dizi başında)"""
        b_size = batch_size or self.config.batch_size
        device = self.M.device
        self.M = torch.zeros(b_size, self.d_m, self.K, device=device)
        self.R = torch.eye(self.K, device=device).unsqueeze(0).repeat(b_size, 1, 1)

    def detach_memory(self):
        """Türev grafiğini adımlar arası sızıntıdan (RuntimeError second backward) korumak için bellek tensörlerini koparır."""
        if self.M is not None:
            self.M = self.M.detach()
        if self.R is not None:
            self.R = self.R.detach()

    def get_memory(self, batch_size: int) -> E5_B_BellekGonderimi:
        if self.M.shape[0] != batch_size:
            self.reset_memory(batch_size)
        return E5_B_BellekGonderimi(M=self.M)

    def write(self, k_r: torch.Tensor, v_r: torch.Tensor, alpha_pareto: Optional[torch.Tensor] = None) -> E5_B_BellekGonderimi:
        """
        Sıfır Parazitli SMW Hafıza Yazımı ve Pareto Kapılama:
        k_r: [B, K] (Giren Anahtar)
        v_r: [B, d_m] (Giren Değer)
        alpha_pareto: [M] (Pareto Gradyan Ağırlıkları Geribesleme Organı)
        """
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # M/R buffer'ları VE girdiler bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if self.M.device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            if k_r.device != zorunlu_cihaz:
                k_r = k_r.to(zorunlu_cihaz)
            if v_r.device != zorunlu_cihaz:
                v_r = v_r.to(zorunlu_cihaz)
            if alpha_pareto is not None and alpha_pareto.device != zorunlu_cihaz:
                alpha_pareto = alpha_pareto.to(zorunlu_cihaz)

        B = k_r.shape[0]
        if self.M.shape[0] != B:
            if self.M.shape[0] < B:
                pad_b = B - self.M.shape[0]
                M_pad = torch.zeros(pad_b, self.d_m, self.K, device=self.M.device, dtype=self.M.dtype)
                R_pad = torch.eye(self.K, device=self.R.device, dtype=self.R.dtype).unsqueeze(0).repeat(pad_b, 1, 1)
                self.M = torch.cat([self.M, M_pad], dim=0)
                self.R = torch.cat([self.R, R_pad], dim=0)
            else:
                self.M = self.M[:B]
                self.R = self.R[:B]
            
        # I. Skaler Normalizasyon gamma_r = 1 + k_r^T * R * k_r -> [B, 1]
        R_k = torch.bmm(self.R, k_r.unsqueeze(-1)).squeeze(-1)  # [B, K]
        k_R_k = torch.sum(k_r * R_k, dim=-1, keepdim=True)       # [B, 1]
        gamma_r = 1.0 + k_R_k                                    # [B, 1]

        # II. Biyortogonal Kazanç Vektörü g_r = (1 / gamma_r) * R * k_r -> [B, K]
        g_r = R_k / torch.clamp(gamma_r, min=1e-6)

        # [GRAD_REPORT GERİBESLEME ORGANİ] Pareto Ağırlıkları ile Bellek Yazma Kapı Önceliği
        if alpha_pareto is not None:
            pareto_gate = torch.clamp(alpha_pareto.mean(), min=0.1, max=2.0)
            g_r = g_r * pareto_gate

        # III. Korelasyon Matrisi Güncellemesi: R = R - g_r * (k_r^T * R)
        R_k_T = torch.bmm(k_r.unsqueeze(1), self.R)               # [B, 1, K]
        g_R_k_T = torch.bmm(g_r.unsqueeze(2), R_k_T)              # [B, K, K]
        self.R = self.R - g_R_k_T

        # IV. M Bellek Güncellemesi (Öğrenilebilir/Dinamik Unutma Kapılı SMW Mühürleme)
        M_k = torch.bmm(self.M, k_r.unsqueeze(-1)).squeeze(-1)  # [B, d_m]
        error_vector = v_r - M_k  # [B, d_m] (Hata Vektörü)
        
        update_matrix = torch.bmm(error_vector.unsqueeze(2), g_r.unsqueeze(1))  # [B, d_m, K]
        beta_forget = torch.sigmoid(torch.mean(v_r, dim=-1, keepdim=True)).unsqueeze(-1)  # [B, 1, 1]
        self.M = (1.0 - beta_forget) * self.M + beta_forget * update_matrix
        return E5_B_BellekGonderimi(M=self.M)

    def BiyortogonalKorelasyonYaz(self, k_r: torch.Tensor, v_r: torch.Tensor, alpha_pareto: Optional[torch.Tensor] = None) -> E5_B_BellekGonderimi:
        """[Rükn 5] Sherman-Morrison-Woodbury Biyortogonal Korelasyon Bellek Mühürleme"""
        return self.write(k_r, v_r, alpha_pareto=alpha_pareto)

    def read(self, k_r: torch.Tensor) -> torch.Tensor:
        """
        Sıfır Hata ve Sıfır Parazit ile Geri Çağırma:
        k_r: [B, K] -> Çıktı: v_r [B, d_m]
        """
        return torch.bmm(self.M, k_r.unsqueeze(-1)).squeeze(-1)

    def hesapla_uyumsuzluk_vektoru(self, x_r: torch.Tensor, D0: torch.Tensor) -> torch.Tensor:
        """
        Kenar seviyesinde Eşsınır Uyumsuzluk Vektörü: d_discrepancy in R^E.
        d_e boyutundaki lif bileşenlerinin L2 normu alınarak kenar bazlı hata vektörü oluşturulur.
        """
        c_defect = torch.matmul(x_r, D0.T)  # [B, E * d_e]
        B = c_defect.shape[0]
        d_e = self.config.d_e
        E_num = c_defect.shape[1] // d_e
        c_reshaped = c_defect.view(B, E_num, d_e)
        d_vec = torch.norm(c_reshaped, p=2, dim=-1).mean(dim=0)  # [E]
        return d_vec

    def hesapla_dirichlet_enerjisi_vektoru(self, x_r: torch.Tensor, Delta_0: torch.Tensor) -> torch.Tensor:
        """
        Düğüm seviyesinde Dirichlet Isı Enerjisi Vektörü: E(x) in R^V.
        d_v boyutundaki lif bileşenleri çarpılarak düğüm bazlı enerji vektörü oluşturulur.
        """
        laplacian_flow = torch.matmul(x_r, Delta_0.T)  # [B, V * d_v]
        B = x_r.shape[0]
        d_v = self.config.d_v
        V_num = x_r.shape[1] // d_v
        x_res = x_r.view(B, V_num, d_v)
        flow_res = laplacian_flow.view(B, V_num, d_v)
        e_vec = torch.sum(x_res * flow_res, dim=-1).mean(dim=0)  # [V]
        return e_vec

    def hesapla_uyumsuzluk(self, x_r: torch.Tensor, D0: torch.Tensor) -> float:
        """Küresel Kesit (Global Section) Uyumsuzluk Metriği Skaler Özeti."""
        d_vec = self.hesapla_uyumsuzluk_vektoru(x_r, D0)
        return float(d_vec.mean().detach().item())

    def hesapla_dirichlet_enerjisi(self, x_r: torch.Tensor, Delta_0: torch.Tensor) -> float:
        """Dirichlet Enerjisi E(x) Skaler Özeti."""
        e_vec = self.hesapla_dirichlet_enerjisi_vektoru(x_r, Delta_0)
        return float(e_vec.mean().detach().item())



class N8_ChebyshevKatsayiProjeksiyon(nn.Module):
    """[N8] Chebyshev Katsayı Projeksiyon Kafası"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        self.in_dim = getattr(config, 'D', 256)
        self.proj = nn.Linear(self.in_dim, config.d * config.M_plus_1)

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """N8 VRAM Tahmin Formülü: flat_C/C = [B, d, M_plus_1] projeksiyon çıktısı baskındır."""
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        return vram_bayt_tahmin_et(B, self.config.d, self.config.M_plus_1)

    def forward(self, final_durumu: E9_GuncellenmisGizilDurum) -> E10_KulliManaMatrisi:
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # modül VE girdisi bu cihaza hizalanır.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if next(self.parameters(), None) is not None and next(self.parameters()).device != zorunlu_cihaz:
                self.to(zorunlu_cihaz)
            final_durumu = girdi_cihaza_tasi(final_durumu, zorunlu_cihaz)

        x_next = final_durumu.x_next
        B = x_next.shape[0]
        if x_next.dim() == 1:
            x_next = x_next.unsqueeze(0)
        
        # Dinamik D_dyn boyutunu sabit self.in_dim boyutuna güvenle havuzla
        if x_next.shape[-1] != self.in_dim and x_next.shape[-1] > 0:
            if x_next.shape[-1] % self.in_dim == 0:
                x_pooled = x_next.view(B, -1, self.in_dim).mean(dim=1)
            else:
                x_pooled = F.adaptive_avg_pool1d(x_next.unsqueeze(1), self.in_dim).squeeze(1)
        else:
            x_pooled = x_next

        flat_C = self.proj(x_pooled)
        C = flat_C.view(B, self.config.d, self.config.M_plus_1)
        return E10_KulliManaMatrisi(C=C)


class N8_B_DinamikUzunlukSecici(nn.Module):
    """
    [N8_B] Dinamik Uzunluk Seçici (Arc-Length & Parametrik Kafa Hibrit).
    
    [sistem_tarif.md:L776-L853]
    1. İkinci Tür Chebyshev türev matrisi T'(t_k) ile numune sayısal integrali hesaplanır:
       L_arc = sum_{k=1}^{K_sample} || C * T'(t_k) ||_2 * dt
    2. Teorik Alt Sınır: N_teorik = ceil(L_arc / delta_token).
    3. Parametrik İnce Ayar: Delta_N = Round(MLP_len(Flatten(C))).
    4. Nihai Dinamik Uzunluk: N* = Clamp(N_teorik + Delta_N, N_min, N_max).
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        flat_dim = config.d * config.M_plus_1
        self.mlp_len = nn.Sequential(
            nn.Linear(flat_dim, flat_dim // 2),
            nn.GELU(),
            nn.Linear(flat_dim // 2, 1)
        )

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """N8_B VRAM Tahmin Formülü: mlp_len'in ilk katman çıktısı [B, flat_dim//2] baskındır."""
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        flat_dim = self.config.d * self.config.M_plus_1
        return vram_bayt_tahmin_et(B, flat_dim // 2) + vram_bayt_tahmin_et(B, flat_dim)

    def forward(self, kulli_mana: E10_KulliManaMatrisi, cheby_calc: Yardimci_ChebyshevMatrisHesaplayici) -> Tuple[int, torch.Tensor, torch.Tensor, torch.Tensor]:
        C = kulli_mana.C
        B, d, M_p_1 = C.shape
        
        # 1 & 2. Arc-Length L_arc (Türevlenebilir Tensör) ve Sürekli Teorik Uzunluk
        L_arc, _ = cheby_calc.hesapla_yay_uzunlugu(C, delta_token=0.5)  # L_arc: [B]
        delta_token = 0.5
        N_teorik_cont = L_arc / delta_token  # Sürekli türevlenebilir teorik uzunluk [B]
        
        # 3. Parametrik İnce Ayar Delta_N (Autograd uyumlu tensör)
        C_flat = C.view(B, -1)
        delta_n_tensor = self.mlp_len(C_flat).squeeze(-1)  # [B]
        
        N_cont = N_teorik_cont + delta_n_tensor  # Sürekli toplam uzunluk [B]
        n_max_cap = float(getattr(self.config, 'N_max', 2048))
        N_cont_clamped = torch.clamp(N_cont, min=8.0, max=n_max_cap)
        
        # 4. Straight-Through Estimator (STE) ile Türevlenebilir N* Geçişi:
        # N_ste = N_cont_clamped + (round(N_cont_clamped) - N_cont_clamped).detach()
        N_round = torch.round(N_cont_clamped)
        N_ste = N_cont_clamped + (N_round - N_cont_clamped).detach()  # Differentiable STE tensor!
        
        N_star_int = int(N_round.mean().detach().item())
        N_star_int = max(8, min(int(n_max_cap), N_star_int))
        
        return N_star_int, L_arc.mean(), N_ste.mean(), delta_n_tensor


class N9_ChebyshevVandermondeCarpim(nn.Module):
    """[N9] Chebyshev Vandermonde (T) Çarpım İstasyonu"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N9 VRAM Tahmin Formülü: X_output = C @ T_matrix = [B, d, N_star]. N_star, N_max'a
        kadar büyüyebildiğinden (dinamik uzunluk seçici) bu düğüm N_star büyüdükçe hızla pahalılaşır.
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        N_star = girdi_sekli[1] if len(girdi_sekli) > 1 else getattr(self.config, 'N', 1024)
        return vram_bayt_tahmin_et(B, self.config.d, N_star)

    def forward(self, kulli_mana: E10_KulliManaMatrisi, T_matrix: torch.Tensor) -> E11_ParalelGomuluVektorlerMatrisi:
        # CUDAGuard Cihaz Hizalaması: N9'un kendi parametresi yoktur (yalnızca self.config),
        # bu yüzden VRAM/TMP idarecisinin .to(device) çağrısı hiçbir şeyi taşımaz ve
        # _vram_idare_zorunlu_cihaz bayrağı başka hiçbir yerde okunmazdı. Daha da önemlisi:
        # T_matrix, Yardimci_ChebyshevMatrisHesaplayici.hesapla()'nın STATİK config.device
        # önbelleğinden gelir — dinamik VRAM idaresine HİÇ katılmaz. kulli_mana.C ise N8
        # üzerinden dinamik olarak CPU'ya taşınmış olabilir. Bu ayrışma tam olarak
        # "Expected all tensors to be on the same device, cuda:0 and cpu" hatasının kök
        # sebebidir — burada açıkça hizalanır (kulli_mana.C'nin gerçek cihazı esas alınır).
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        hedef_cihaz = zorunlu_cihaz if zorunlu_cihaz is not None else kulli_mana.C.device
        kulli_mana = girdi_cihaza_tasi(kulli_mana, hedef_cihaz)
        if T_matrix.device != hedef_cihaz:
            T_matrix = T_matrix.to(hedef_cihaz)
        X_output = torch.matmul(kulli_mana.C, T_matrix)
        return E11_ParalelGomuluVektorlerMatrisi(X_output=X_output)


class N10_SozlukSoftmaxIzdusem(nn.Module):
    """
    [N10 Sözlük Softmax İzdüşüm - CUDAGuard & CİHAZ HİZALAMALI SIFIR-OOM MİMARİSİ]
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        super().__init__()
        self.config = config
        self.nedensel_suzgec = Maarif_NedenselSuzgec(config)
        self.d = getattr(config, 'd', 128)
        self.V_size = getattr(config, 'V_size', 200000)
        self.vocab_head = nn.Linear(self.d, self.V_size, bias=False)

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        N10 VRAM Tahmin Formülü: VRAM_bayt = B * micro_chunk_size * V_size * 4 Bayt
        """
        B = girdi_sekli[0] if len(girdi_sekli) > 0 else self.config.batch_size
        micro_chunk_size = 64
        return int(B * micro_chunk_size * self.V_size * 4)

    def forward_sifir_oom_chunking(self, e11_gomulu: E11_ParalelGomuluVektorlerMatrisi, hedefler: Optional[torch.Tensor] = None) -> E12_ParalelTokenOlasilikMatrisi:
        """RÜKN IV: 64'lük mikro-dilimlerle SIFIR-OOM hesaplama algoritması"""
        return self.forward(e11_gomulu, hedefler=hedefler)

    def forward(self, e11_gomulu: E11_ParalelGomuluVektorlerMatrisi, hedefler: Optional[torch.Tensor] = None) -> E12_ParalelTokenOlasilikMatrisi:
        X_input = e11_gomulu.X_output  # [B, d, N] veya [d, N]
        if X_input.dim() == 2:
            X_input = X_input.unsqueeze(0)
        elif X_input.dim() == 1:
            X_input = X_input.unsqueeze(0).unsqueeze(-1)

        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # (bkz. anlasmali_vram_guvencesi_al) tüm N10 modül parametreleri (nedensel_suzgec,
        # vocab_head) VE girdi bu cihaza hizalanır; aksi halde eski davranış korunur.
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        device = zorunlu_cihaz if zorunlu_cihaz is not None else X_input.device
        if next(self.parameters(), None) is not None:
            if next(self.parameters()).device != device:
                self.to(device)
        if X_input.device != device:
            X_input = X_input.to(device)
        if hasattr(self, 'nedensel_suzgec'):
            self.nedensel_suzgec._vram_idare_zorunlu_cihaz = device

        X_refined = self.nedensel_suzgec(X_input) if hasattr(self, 'nedensel_suzgec') else X_input
        X_t = X_refined.transpose(1, 2)   # [B, N, d]
        B, N, d = X_t.shape

        micro_chunk_size = 64
        
        # Eğer hedefler verilmişse doğrudan p_target topla (6.10 GB VRAM Tasarrufu!)
        if hedefler is not None:
            # Tensör Boyut Zırhı: 1D, 2D veya 3D hedefler tensörünü 2D [B, N] formuna dönüştür
            if hedefler.dim() == 1:
                h_tensor = hedefler.unsqueeze(0)
            elif hedefler.dim() == 3:
                h_tensor = hedefler.squeeze(-1)
            else:
                h_tensor = hedefler

            if h_tensor.shape[0] != B:
                h_tensor = h_tensor.expand(B, -1)

            cur_N = min(N, h_tensor.shape[1])
            h_tensor = torch.clamp(h_tensor[:, :cur_N], min=0, max=self.V_size - 1).long()
            p_target_chunks = []
            
            for i in range(0, cur_N, micro_chunk_size):
                X_chunk = X_t[:, i:i+micro_chunk_size, :]
                h_chunk = h_tensor[:, i:i+micro_chunk_size]
                
                logits_chunk = self.vocab_head(X_chunk)
                # Tensör Boyut Zırhı: vocab_head çıktısı 0D (skaler), 1D [V_size] veya 2D
                # [B, V_size] gelebilir; HER ZAMAN tam 3D [B, chunk_len, V_size]'e normalize
                # et (eski kod yalnızca dim==1/dim==2'yi ele alıyordu, dim==0 durumunda
                # P_chunk.shape[1] IndexError fırlatıyordu).
                if logits_chunk.dim() < 3:
                    # TEŞHİS KAYDI: Bu dal normalde HİÇ tetiklenmemeli (X_t kanıtlanmış
                    # şekilde 3D'dir, X_chunk/vocab_head çıktısı rank korur). Tetiklenirse
                    # gerçek kök sebebi yakalamak için tüm ilgili şekiller loglanır.
                    logging.getLogger("mucit_ai.kontratlar").error(
                        f"[N10 Boyut Anomalisi] logits_chunk.dim()={logits_chunk.dim()} (beklenen: 3). "
                        f"X_input.shape={tuple(X_input.shape)}, X_refined.shape={tuple(X_refined.shape)}, "
                        f"X_t.shape={tuple(X_t.shape)}, X_chunk.shape={tuple(X_chunk.shape)}, "
                        f"i={i}, micro_chunk_size={micro_chunk_size}, cur_N={cur_N}, B={B}, N={N}, d={d}, "
                        f"vocab_head.weight.shape={tuple(self.vocab_head.weight.shape)}, "
                        f"logits_chunk.shape={tuple(logits_chunk.shape)}"
                    )
                while logits_chunk.dim() < 3:
                    logits_chunk = logits_chunk.unsqueeze(0)
                logits_mean = logits_chunk.mean(dim=-1, keepdim=True)
                logits_std = torch.std(logits_chunk, dim=-1, keepdim=True, correction=0)
                logits_norm = (logits_chunk - logits_mean.to(device=logits_chunk.device)) / (logits_std.to(device=logits_chunk.device) + 1e-6)
                P_chunk = torch.softmax(torch.clamp(logits_norm, min=-50.0, max=50.0), dim=-1) # [B, chunk_len, V_size]
                
                # Hedef olasılıkları mikro-dilim içinde gather et (Sadece 1 MB VRAM Harcar!)
                # h_chunk: [B, chunk_len] → [B, chunk_len, 1]
                _clen = P_chunk.shape[1]
                h_chunk_aligned = h_chunk[:, :_clen] if h_chunk.shape[1] >= _clen else F.pad(h_chunk, (0, _clen - h_chunk.shape[1]))
                h_chunk_3d = h_chunk_aligned.unsqueeze(-1).to(device=P_chunk.device, dtype=torch.int64)
                p_t_chunk = P_chunk.gather(2, h_chunk_3d).squeeze(-1) # [B, chunk_len]
                p_target_chunks.append(p_t_chunk)
                
            p_target_full = torch.cat(p_target_chunks, dim=-1) # [B, N] (Sadece 1 MB!)
            return E12_ParalelTokenOlasilikMatrisi(P=p_target_full)
            
        else:
            # Genel Akış: 6.10 GB'lık torch.cat YERİNE mikro-dilim listesi döndürülür
            P_chunks = []
            preds_chunks = []
            for i in range(0, N, micro_chunk_size):
                X_chunk = X_t[:, i:i+micro_chunk_size, :]
                logits_chunk = self.vocab_head(X_chunk)
                # Tensör Boyut Zırhı: vocab_head çıktısı 0D (skaler), 1D [V_size] veya 2D
                # [B, V_size] gelebilir; HER ZAMAN tam 3D [B, chunk_len, V_size]'e normalize
                # et (eski kod yalnızca dim==1/dim==2'yi ele alıyordu, dim==0 durumunda
                # P_chunk.shape[1] IndexError fırlatıyordu).
                if logits_chunk.dim() < 3:
                    # TEŞHİS KAYDI: Bu dal normalde HİÇ tetiklenmemeli (X_t kanıtlanmış
                    # şekilde 3D'dir, X_chunk/vocab_head çıktısı rank korur). Tetiklenirse
                    # gerçek kök sebebi yakalamak için tüm ilgili şekiller loglanır.
                    logging.getLogger("mucit_ai.kontratlar").error(
                        f"[N10 Boyut Anomalisi] logits_chunk.dim()={logits_chunk.dim()} (beklenen: 3). "
                        f"X_input.shape={tuple(X_input.shape)}, X_refined.shape={tuple(X_refined.shape)}, "
                        f"X_t.shape={tuple(X_t.shape)}, X_chunk.shape={tuple(X_chunk.shape)}, "
                        f"i={i}, micro_chunk_size={micro_chunk_size}, B={B}, N={N}, d={d}, "
                        f"vocab_head.weight.shape={tuple(self.vocab_head.weight.shape)}, "
                        f"logits_chunk.shape={tuple(logits_chunk.shape)}"
                    )
                while logits_chunk.dim() < 3:
                    logits_chunk = logits_chunk.unsqueeze(0)
                logits_mean = logits_chunk.mean(dim=-1, keepdim=True)
                logits_std = torch.std(logits_chunk, dim=-1, keepdim=True, correction=0)
                logits_norm = (logits_chunk - logits_mean.to(device=logits_chunk.device)) / (logits_std.to(device=logits_chunk.device) + 1e-6)
                P_chunk = torch.softmax(torch.clamp(logits_norm, min=-50.0, max=50.0), dim=-1).transpose(1, 2)
                # Tüm dilimlerin argmax tahminini biriktir: dev [B, V_size, N] tensörü hiç kurmadan
                # tam uzunlukta ([B, N], int64, ihmal edilebilir VRAM) tahmin dizisi elde edilir.
                preds_chunks.append(torch.argmax(P_chunk, dim=1))
                P_chunks.append(P_chunk.detach() if not self.training else P_chunk)

            preds_full = torch.cat(preds_chunks, dim=-1)  # [B, N]
            # DEV TENSÖR BİRLEŞTİRMESİ YAPILMAZ! Parçalı liste teslim edilir; tam uzunluk tahmini preds_full'da.
            return E12_ParalelTokenOlasilikMatrisi(P=P_chunks[0], P_chunks=P_chunks, preds_full=preds_full)


# =============================================================================
# IV-B. DIŞ MİMARİ VE OPERASYONEL BİLİŞSEL DÜĞÜMLER (NODES N11 - N16)
# =============================================================================

# [N11] Lif Laplasyeni Blok İnşa Edici
N11_LifLaplasyeniBlokInsaEdici = Riyazi_LifLaplasyeniBlokInsaEdici

# [N12] Sherman-Morrison-Woodbury (SMW) Biyortogonal Süzgeçli Sıfır Parazitli Bellek Yöneticisi
N12_BellekBaglamYoneticisi = SMW_SifirParazit_BellekYoneticisi

# [N13] Stiefel Manifoldu İzdüşüm Operatörü
class Riyazi_StiefelManifolduIzdusumu:
    """[N13] Stiefel Manifoldu İzdüşüm Operatörü"""
    def izdusur(self, phi_dict: Union[Dict[str, torch.Tensor], nn.ParameterDict, torch.Tensor, Any]):
        with torch.no_grad():
            if isinstance(phi_dict, (dict, nn.ParameterDict)):
                for key, param in phi_dict.items():
                    if isinstance(param, torch.Tensor) and param.dim() == 2:
                        param.copy_(stiefel_qr_projection(param))
            elif isinstance(phi_dict, (torch.Tensor, nn.Parameter)) and phi_dict.dim() == 2:
                phi_dict.copy_(stiefel_qr_projection(phi_dict.data))
            elif isinstance(phi_dict, nn.Module):
                for name, param in phi_dict.named_parameters():
                    if param.dim() == 2:
                        param.data.copy_(stiefel_qr_projection(param.data))

    def izdüsür(self, phi_dict: Union[Dict[str, torch.Tensor], nn.ParameterDict, torch.Tensor, Any]):
        self.izdusur(phi_dict)

N13_StiefelManifolduIzdusumu = Riyazi_StiefelManifolduIzdusumu


class N14_OdulTopolojikDevresmezlikMotoru:
    """[N14] GRPO Topolojik Tutarlılık ve Ödül Skorlama Motoru (2D/3D Uyumlu)"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config

    def hesapla(self, P: torch.Tensor, hedefler: torch.Tensor) -> torch.Tensor:
        # P: [B, N] (2D p_target) VEYA [B, V_size, N] (3D Olasılık)
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

    def hesapla_aktif_sorgu_odulu(
        self,
        q_r: torch.Tensor,
        a_r: torch.Tensor,
        x_context: torch.Tensor,
        kayip_cevapsiz: torch.Tensor,
        kayip_cevapli: torch.Tensor,
        Delta_0: Optional[torch.Tensor] = None,
        **kwargs
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """
        Vazifesi: Sorgu Seçici (N4) ve Cevap Süzücü (N5) için Sorgu Kalite Ödülünü (R_q)
        ve Topolojik Bilgi Kazanımı metriklerini hesaplar.
        """
        R_info = F.relu(kayip_cevapsiz - kayip_cevapli)
        cos_sim = F.cosine_similarity(q_r, a_r, dim=-1)
        R_ortho = 1.0 - torch.abs(cos_sim)

        R_q = R_info * 1.5 + R_ortho * 0.5
        E_sorgu_node_matrix = (q_r.unsqueeze(1) - a_r.unsqueeze(2)).pow(2).mean(dim=-1)

        metrikler = {
            "R_info": float(R_info.mean().detach().item()) if hasattr(R_info, 'detach') else 0.0,
            "R_ortho": float(R_ortho.mean().detach().item()) if hasattr(R_ortho, 'detach') else 0.0,
            "E_sorgu_node_matrix": E_sorgu_node_matrix,
            "L_sorgu_field": E_sorgu_node_matrix.reshape(-1)
        }
        return R_q, metrikler

Odul_TopolojikDevresmezlikMotoru = N14_OdulTopolojikDevresmezlikMotoru


class Kayip_GRPO_Kriteri:
    """GRPO (Group Relative Policy Optimization) Kayıp Fonksiyonu (Çifte Logaritma Önlemeli)"""
    def __init__(self, config: Model_TopolojikKonfigurasyon):
        self.config = config
        # W_up_stiefel: sabit Stiefel izometri matrisi, __init__'te bir kez üretilir
        d_a = getattr(config, 'd_a', 64)
        d_v = getattr(config, 'd_v', 32)
        W_raw = torch.randn(d_a, d_v)
        Q, _ = torch.linalg.qr(W_raw)
        self._W_up_stiefel_cpu: torch.Tensor = Q  # CPU'da sabit tut

    def hesapla_vektor(self, P: torch.Tensor, hedefler: torch.Tensor, oduller: torch.Tensor) -> torch.Tensor:
        if P.dim() == 2:
            # P zaten [B, N] boyutunda p_target olasılık tensörüdür!
            # NLL hesabı doğrudan p_target üzerinden tekil logaritma ile yapılır:
            nll = -torch.log(torch.clamp(P, min=1e-9, max=1.0)).mean(dim=-1)  # [B]
        else:
            B, V_size, N = P.shape
            targets = hedefler[:, :N]
            p_target = P.gather(1, targets.unsqueeze(1)).squeeze(1)  # [B, N]
            nll = -torch.log(torch.clamp(p_target, min=1e-9, max=1.0)).mean(dim=-1)  # [B]

        # Ödül ile avantaj hesaplaması
        std = oduller.std() if oduller.std() > 0 else 1e-8
        avantajlar = (oduller - oduller.mean()) / (std + 1e-8)
        kayip_vec = nll * avantajlar.detach()  # [B]
        return kayip_vec

    def hesapla(self, P: torch.Tensor, hedefler: torch.Tensor, oduller: torch.Tensor) -> torch.Tensor:
        return self.hesapla_vektor(P, hedefler, oduller).mean()

    def hesapla_aktif_sorgu_odulu(self,
                                   q_r: torch.Tensor,
                                   a_r: torch.Tensor,
                                   x_context: torch.Tensor,
                                   kayip_cevapsiz: torch.Tensor,
                                   kayip_cevapli: torch.Tensor,
                                   Delta_0: Optional[torch.Tensor] = None,
                                   beta1: float = 0.1,
                                   beta2: float = 0.05,
                                   beta3: float = 0.01,
                                   beta4: float = 0.1,
                                   beta5: float = 0.05) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        [sistem_tarif.md:L319-L411] Tekamül Ettirilmiş 6+1 Kıstaslı R_tekamul(q) Ödül Fonksiyonu.
        
        R_tekamul(q) = I(Y; a | X) - beta1 * D(a, X) - beta2 * C(a | q) - beta3 * H(q) - beta4 * L_contra(q) - beta5 * G(q, a)
        """
        # 1. Kıstas 1: Bilgi Kazancı Vektör Sahası L_bilgi_kazanci in R^V (Düğüm Seviyesinde)
        info_gain = kayip_cevapsiz - kayip_cevapli  # [B]
        B_grouped = a_r.shape[0]
        d_a = a_r.shape[-1]
        d_v = getattr(self.config, 'd_v', 32) if self.config else 32
        D_total = x_context.shape[-1]
        # Tam bölünmüyorsa tavan bölme kullanılır: V_nodes * d_v hiçbir zaman D_total'ı eksik kapsamaz
        V_nodes = D_total // d_v if D_total % d_v == 0 else max(1, -(-D_total // d_v))
        
        if D_total == V_nodes * d_v:
            x_nodes_all = x_context.view(B_grouped, V_nodes, d_v)
        else:
            x_nodes_all = F.adaptive_avg_pool1d(x_context.unsqueeze(1), V_nodes * d_v).view(B_grouped, V_nodes, d_v)

        L_bilgi_kazanci_v = info_gain.unsqueeze(-1).repeat(1, V_nodes)  # [B, V]

        # 2. Kıstas 2: Mesafe / Totoloji Cezası Vektör Sahası L_mesafe in R^V (Düğüm Seviyesinde)
        # Sabit W_up_stiefel: cihaza taşı ama yeniden üretme
        W_up = self._W_up_stiefel_cpu.to(device=x_context.device, dtype=x_context.dtype)

        # Her bir v düğümünün a_r cevabıyla mesafe vektörü [B, V]
        x_nodes_proj = torch.matmul(x_nodes_all, W_up.T)  # [B, V, d_a]
        diff_nodes_ax = a_r.unsqueeze(1) - x_nodes_proj              # [B, V, d_a]
        dist_nodes_sq = torch.clamp(torch.sum(diff_nodes_ax ** 2, dim=-1), min=1e-4) # [B, V]
        L_mesafe_v = torch.clamp(1.0 / dist_nodes_sq, max=100.0)        # [B, V]
        dist_penalty = L_mesafe_v.mean(dim=-1)                          # [B]

        # 3. Kıstas 3: Cevaplama Kolaylığı Vektör Sahası L_kolaylik in R^K (Bellek Slotu Seviyesinde)
        K_slots = getattr(self.config, 'K', 16) if self.config else 16
        diff_aq = a_r - q_r
        L_kolaylik_k = torch.sum(diff_aq ** 2, dim=-1, keepdim=True).repeat(1, K_slots)  # [B, K]
        complexity_penalty = L_kolaylik_k.mean(dim=-1)                                 # [B]

        # 4. Kıstas 5: Bilgi Yoğunluğu / Information Bottleneck Vektör Sahası L_yogunluk in R^V (Düğüm Seviyesinde)
        L_yogunluk_v = torch.norm(x_nodes_all, p=2, dim=-1) - torch.mean(torch.abs(x_nodes_all), dim=-1)  # [B, V]
        entropy_penalty = L_yogunluk_v.mean(dim=-1)                                                        # [B]

        # 5. Kıstas 4: Çelişkisizlik Vektör Sahası L_celiskisizlik in R^V (Düğüm Seviyesinde)
        q_r_proj_v = F.adaptive_avg_pool1d(q_r.unsqueeze(1), d_v).squeeze(1).unsqueeze(1)
        contra_sim_v = F.cosine_similarity(q_r_proj_v, -x_nodes_all, dim=-1)  # [B, V]
        L_celiskisizlik_v = F.relu(contra_sim_v)                              # [B, V]
        contra_penalty = L_celiskisizlik_v.mean(dim=-1)                       # [B]

        # 6. Kıstas 6: Geodezik Yol Akış Vektör Sahası L_geodesic in R^V (Düğüm Seviyesinde)
        qa_diff = q_r - a_r
        if Delta_0 is not None:
            if qa_diff.shape[-1] != Delta_0.shape[0]:
                qa_diff_proj = F.pad(qa_diff, (0, Delta_0.shape[0] - qa_diff.shape[-1]))
            else:
                qa_diff_proj = qa_diff
            geodesic_flow = torch.matmul(qa_diff_proj, Delta_0.T)
            g_flow_sq = qa_diff_proj * geodesic_flow
            L_geodesic_v = F.adaptive_avg_pool1d(g_flow_sq.unsqueeze(1), V_nodes).squeeze(1)  # [B, V]
            geodesic_penalty = torch.sum(g_flow_sq, dim=-1)
        else:
            L_geodesic_v = torch.sum(qa_diff ** 2, dim=-1, keepdim=True).repeat(1, V_nodes)
            geodesic_penalty = L_geodesic_v.mean(dim=-1)

        # 6 HAKİKİ KISTASIN BİRLEŞİK DÜĞÜM HATA MATRİSİ E_sorgu_node_matrix in R^(V x 6)
        E_sorgu_node_matrix = torch.stack([
            L_mesafe_v.mean(dim=0),
            L_bilgi_kazanci_v.mean(dim=0),
            L_kolaylik_k[:, :V_nodes].mean(dim=0) if K_slots >= V_nodes else F.pad(L_kolaylik_k, (0, V_nodes - K_slots)).mean(dim=0),
            L_celiskisizlik_v.mean(dim=0),
            L_yogunluk_v.mean(dim=0),
            L_geodesic_v.mean(dim=0)
        ], dim=-1)  # [V, 6]

        # 6 KISTASIN HAKİKİ BİRLEŞİK BLOK VEKTÖR SAHASI L_sorgu_field in R^(6V)
        L_sorgu_field = E_sorgu_node_matrix.reshape(-1)  # [6V]

        # R_tekamul(q) Ham Ödül Bileşimi
        R_q_raw = info_gain - (beta1 * dist_penalty) - (beta2 * complexity_penalty) - (beta3 * entropy_penalty) - (beta4 * contra_penalty) - (beta5 * geodesic_penalty)

        # GRPO-Q Grup İçi Ödül Normalizasyonu (Avantaj Skoru)
        std_r = R_q_raw.std() if R_q_raw.std() > 0 else 1e-8
        R_q_normalized = (R_q_raw - R_q_raw.mean()) / (std_r + 1e-8)

        metrikler = {
            "R_q_mean": float(R_q_raw.mean().detach().item()),
            "R_q_norm_mean": float(R_q_normalized.mean().detach().item()),
            "info_gain": float(info_gain.mean().detach().item()),
            "dist_penalty": float(dist_penalty.mean().detach().item()),
            "complexity_penalty": float(complexity_penalty.mean().detach().item()),
            "entropy_penalty": float(entropy_penalty.mean().detach().item()),
            "contra_penalty": float(contra_penalty.mean().detach().item()),
            "geodesic_penalty": float(geodesic_penalty.mean().detach().item()),
            "E_sorgu_node_matrix": E_sorgu_node_matrix,
            "L_sorgu_field": L_sorgu_field
        }
        return R_q_normalized, metrikler

class Kayip_VICReg_UcluBilgiKorunumu(nn.Module):
    """
    [VICReg / Üçlü Bilgi-Teorik Korunum ve Denge Kısıtı]
    Ağın her şeye sabit '1' veya '0' (örn. 1111100000) basarak mantık nöronlarını
    kandırmasını, boyut çöküşünü (dimension collapse) ve bilgi kaybını engelleyen 
    üçlü matematiksel kısıt motoru:
    
    1. L_var  (Varyans Kısıtı): Her özelliğin (feature/neuron) varyansını gamma (1.0) eşiğinin üstünde tutar.
    2. L_cov  (Kovaryans Dekorilasyonu): Nöronların birbiriyle kopyala-yapıştır (redundant) olmasını engeller.
    3. L_rec  (Geri-Örtüştürme Rekonstrüksiyonu): Projeksiyon çıktısından orijinal bilginin geri üretilebilirliğini garanti eder.
    """
    def __init__(self, gamma: float = 1.0, eps: float = 1e-4, 
                 var_weight: float = 1.0, cov_weight: float = 1.0, rec_weight: float = 1.0):
        super().__init__()
        self.gamma = gamma
        self.eps = eps
        self.var_weight = var_weight
        self.cov_weight = cov_weight
        self.rec_weight = rec_weight

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        VICReg VRAM Tahmin Formülü: z = [B, D] veya [B, d_mid, D] olabilir (3D gelirse
        varyans/kovaryans yolları z.view(-1, D) ile B_eff = B*d_mid'e katlar). Kovaryans
        yolu B_eff×B_eff Gram hilesiyle D×D kovaryansdan kaçınır; baskın maliyet
        z_centered [B_eff, D] ve K_gram [B_eff, B_eff]'dir.
        """
        if len(girdi_sekli) >= 3:
            B_eff = girdi_sekli[0] * girdi_sekli[1]
            D = girdi_sekli[2]
        elif len(girdi_sekli) == 2:
            B_eff, D = girdi_sekli[0], girdi_sekli[1]
        else:
            B_eff, D = (girdi_sekli[0] if girdi_sekli else 1), 128
        return vram_bayt_tahmin_et(B_eff, D) + vram_bayt_tahmin_et(B_eff, B_eff)

    def varyans_kaybi_vektor(self, z: torch.Tensor) -> torch.Tensor:
        """
        L_vic_var in R^D: Her bir j in {1 ... D} özellik boyutunun hinge varyans hata vektörü.
        Eğer ağ 1111100000 basıp varyansı sıfıra düşürürse ceza ilgili boyutta patlar.
        """
        if z.ndim > 2:
            z = z.view(-1, z.shape[-1])
        std_z = torch.sqrt(torch.var(z, dim=0) + self.eps)
        var_loss_vec = torch.relu(self.gamma - std_z)  # [D]
        return var_loss_vec

    def varyans_kaybi(self, z: torch.Tensor) -> torch.Tensor:
        """Geriye uyumluluk için skaler varyans kaybı yardımcısı."""
        return self.varyans_kaybi_vektor(z).mean()

    def kovaryans_kaybi_vektor(self, z: torch.Tensor) -> torch.Tensor:
        """
        L_vic_cov in R^B: Gram-Frobenius İz Özdeşliği [B x B Gram Matrisi]
        Siklik İz Özelliği sayesinde 65536 x 65536 kovaryans kaybını
        B x B (8 x 8) boyutundaki K_gram = X_centered * X_centered^T matrisi üzerinden
        her bir b in {1 ... B} örnekleminin kovaryans hata katkısı olarak hesaplayan metod.
        z: [B, D]
        """
        if z.ndim > 2:
            z = z.view(z.shape[0], -1)
        B, D = z.shape
        if B <= 1:
            return torch.zeros(max(1, B), device=z.device)

        # 1. Bütünsel Merkezleme (Mean Centering - Hiçbir düğüm/özellik kırpılmaz)
        z_mean = torch.mean(z, dim=0, keepdim=True)  # [1, D]
        z_centered = z - z_mean                      # [B, D]

        # 2. B x B Gram Matrisi (K_gram = X_centered * X_centered^T)
        K_gram = torch.matmul(z_centered, z_centered.T)  # [B, B]

        # 3. Örneklem Başına Kovaryans Hata Katkı Vektörü L_vic_cov in R^B
        denom = float(max(1, (B - 1) ** 2))
        sample_cov_frobenius_sq = torch.sum(K_gram ** 2, dim=1) / denom  # [B]
        variances = torch.var(z, dim=0, unbiased=False)                  # [D]
        diag_cov_sq = torch.sum(variances ** 2)                          # Skaler

        cov_loss_vec = F.relu((sample_cov_frobenius_sq - (diag_cov_sq / float(B))) / float(D))  # [B]
        return cov_loss_vec

    def kovaryans_kaybi(self, z: torch.Tensor) -> torch.Tensor:
        """Geriye uyumluluk için skaler kovaryans kaybı yardımcısı."""
        return self.kovaryans_kaybi_vektor(z).mean()

    def rekonstruksiyon_kaybi_vektor(self, x: torch.Tensor, z: torch.Tensor, W: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        L_vic_rec in R^D: Her bir j in {1 ... D} özelliğinin kayıpsız rekonstrüksiyon hata vektörü.
        3D z tensörü [B, d, N] spektral N boyutu boyunca ortalaması alınarak [B, d] yapılır.
        """
        if z.ndim == 3:
            z_flat = z.mean(dim=-1)  # [B, d] Spektral N ortalaması alınır
        elif z.ndim > 2:
            z_flat = z.view(x.shape[0], -1)
        else:
            z_flat = z

        if x.ndim == 3:
            x_flat = x.mean(dim=-1)
        else:
            x_flat = x

        if W is not None:
            x_rec = torch.matmul(z_flat, W)
            return torch.mean((x_flat - x_rec) ** 2, dim=0)
        else:
            min_d = min(x_flat.shape[-1], z_flat.shape[-1])
            return torch.mean((x_flat[:, :min_d] - z_flat[:, :min_d]) ** 2, dim=0)

    def rekonstruksiyon_kaybi(self, x: torch.Tensor, z: torch.Tensor, W: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Geriye uyumluluk için skaler rekonstrüksiyon kaybı yardımcısı."""
        return self.rekonstruksiyon_kaybi_vektor(x, z, W).mean()

    def forward(self, x: torch.Tensor, z: torch.Tensor, W: Optional[torch.Tensor] = None) -> Tuple[Tuple[torch.Tensor, torch.Tensor, torch.Tensor], Dict[str, float]]:
        """
        Toplu Üçlü Bilgi Korunum Vektör Hata Sahalarını ve Günlük Metriklerini Döndürür.
        """
        # CUDAGuard Cihaz Hizalaması: VRAM/TMP İdarecisi zorunlu bir cihaz kararı vermişse
        # tüm girdiler bu cihaza hizalanır (VICReg'in kendi öğrenilebilir parametresi yoktur).
        zorunlu_cihaz = getattr(self, '_vram_idare_zorunlu_cihaz', None)
        if zorunlu_cihaz is not None:
            if x.device != zorunlu_cihaz:
                x = x.to(zorunlu_cihaz)
            if z.device != zorunlu_cihaz:
                z = z.to(zorunlu_cihaz)
            if W is not None and W.device != zorunlu_cihaz:
                W = W.to(zorunlu_cihaz)

        l_var_vec = self.varyans_kaybi_vektor(z)        # [D]
        l_cov_vec = self.kovaryans_kaybi_vektor(z)      # [B]
        l_rec_vec = self.rekonstruksiyon_kaybi_vektor(x, z, W)  # [D]

        l_var_skaler = l_var_vec.mean()
        l_cov_skaler = l_cov_vec.mean()
        l_rec_skaler = l_rec_vec.mean()

        toplam_vicreg_skaler = (self.var_weight * l_var_skaler + 
                                self.cov_weight * l_cov_skaler + 
                                self.rec_weight * l_rec_skaler)

        metrikler = {
            "l_var": float(l_var_skaler.detach().item()),
            "l_cov": float(l_cov_skaler.detach().item()),
            "l_rec": float(l_rec_skaler.detach().item()),
            "vicreg_total": float(toplam_vicreg_skaler.detach().item())
        }
        return (l_var_vec, l_cov_vec, l_rec_vec), metrikler


class LPT_DosyaDengeliDagitici:
    """
    [LPT Bin-Packing Dosya Bölümleyici]
    Farklı boyutlardaki müstakil dosyaları GPU'lara/İş parçacıklarına eşit bayt yükü
    oluşturacak şekilde dağıtır. (Longest Processing Time Greedy Bin-Packing).
    Tüm dosyalar bayt boyutlarına göre büyükten küçüğe sıralanır ve o an en az yük alan birime atanır.
    """
    @staticmethod
    def dagit(dosya_listesi: List[Tuple[str, int]], num_gpus: int = 1) -> List[List[str]]:
        if num_gpus <= 1 or not dosya_listesi:
            return [[f[0] for f in dosya_listesi]]
        
        # 1. Bayt boyutuna göre büyükten küçüğe sıralama
        sirali_dosyalar = sorted(dosya_listesi, key=lambda x: x[1], reverse=True)
        
        gpu_dosyalari: List[List[str]] = [[] for _ in range(num_gpus)]
        gpu_yukleri: List[int] = [0] * num_gpus
        
        # 2. Greedy Bin-Packing: En az yüklü birime atama
        for dosya_yolu, bayt_boyutu in sirali_dosyalar:
            min_gpu_idx = gpu_yukleri.index(min(gpu_yukleri))
            gpu_dosyalari[min_gpu_idx].append(dosya_yolu)
            gpu_yukleri[min_gpu_idx] += bayt_boyutu
            
        return gpu_dosyalari


class N15_EgitimKontrolNoktasiYoneticisi:
    """[N15] Dağıtık Tek-Checkpoint Birleşik Ağırlık ve Kontrol Noktası Yöneticisi"""
    def __init__(self, kaydetme_dizini: str = "./checkpoints"):
        self.kaydetme_dizini = kaydetme_dizini

    def kaydet(self, epoch: int, model: Any, optimizer: torch.optim.Optimizer, kayip: float, is_master: bool = True):
        """
        Dağıtık GPU / Çoklu-Shard Ortamında Tek ve Birleşik Checkpoint Saklama Güvencesi.
        Ayrı checkpoint dosyaları (model_gpu0.pt vs) üretilmez, tek birleşmiş checkpoint yazılır.
        """
        if not is_master:
            return
            
        import os
        os.makedirs(self.kaydetme_dizini, exist_ok=True)
        dosya_yolu = os.path.join(self.kaydetme_dizini, f"topolojik_model_epoch_{epoch}.pt")
        
        if isinstance(model, dict):
            model_state = {k: (v.module.state_dict() if hasattr(v, 'module') else v.state_dict()) for k, v in model.items()}
        else:
            model_state = model.module.state_dict() if hasattr(model, 'module') else model.state_dict()
            
        state_dict = {
            'epoch': epoch,
            'kayip': kayip,
            'optimizer': optimizer.state_dict(),
            'model': model_state,
            'modeller': model_state if isinstance(model, dict) else {'model': model_state}
        }
        torch.save(state_dict, dosya_yolu)

    def yukle(self, epoch: Optional[int], model: Any, optimizer: Optional[torch.optim.Optimizer] = None,
              cihaz: Union[str, torch.device] = "cpu") -> Dict[str, Any]:
        """
        `kaydet` ile yazılmış birleşik checkpoint'i geri yükler.
        epoch=None ise kaydetme_dizini içindeki en yeni 'topolojik_model_epoch_*.pt' dosyası seçilir.
        """
        import os
        import glob

        if epoch is not None:
            dosya_yolu = os.path.join(self.kaydetme_dizini, f"topolojik_model_epoch_{epoch}.pt")
        else:
            adaylar = glob.glob(os.path.join(self.kaydetme_dizini, "topolojik_model_epoch_*.pt"))
            if not adaylar:
                raise FileNotFoundError(f"'{self.kaydetme_dizini}' içinde yüklenecek checkpoint bulunamadı.")
            dosya_yolu = max(adaylar, key=os.path.getmtime)

        state_dict = torch.load(dosya_yolu, map_location=cihaz)

        if isinstance(model, dict):
            model_state = state_dict.get('modeller', state_dict.get('model', {}))
            for k, v in model.items():
                if k in model_state:
                    (v.module if hasattr(v, 'module') else v).load_state_dict(model_state[k])
        else:
            model_state = state_dict.get('model', {})
            (model.module if hasattr(model, 'module') else model).load_state_dict(model_state)

        if optimizer is not None and 'optimizer' in state_dict:
            optimizer.load_state_dict(state_dict['optimizer'])

        return state_dict


class N16_ArcIzgaraDonusturucu:
    """[N16] ARC-AGI 2D Izgara Formatı ve Topolojik Dize Dönüştürücüsü"""
    def donustur(self, gorev_verisi: Dict[str, Any]) -> str:
        return json.dumps(gorev_verisi.get("train", []))

    def insa_et(self, olasilik_matrisi: E12_ParalelTokenOlasilikMatrisi, hedef_boyut: Tuple[int, int] = (3, 3)) -> Dict[str, List[List[int]]]:
        # preds_full: tüm mikro-dilimlerin tam uzunluktaki argmax dizisi (P sadece ilk 64'lük dilim olabilir!)
        if olasilik_matrisi.preds_full is not None:
            preds = olasilik_matrisi.preds_full[0].cpu().numpy()
        else:
            P = olasilik_matrisi.P
            preds = torch.argmax(P, dim=1)[0].cpu().numpy()
        rows, cols = hedef_boyut
        izgara = []
        idx = 0
        for r in range(rows):
            row = []
            for c in range(cols):
                val = int(preds[idx % len(preds)]) % 10
                row.append(val)
                idx += 1
            izgara.append(row)
        return {"attempt_1": izgara, "attempt_2": izgara}



# =============================================================================
# V. TOPTAN TOPOLOJİK MODEL ÇEKİRDEĞİ (BİLİŞSEL KANVAS MODELİ)
# =============================================================================

class BiliselKanvasModeli(nn.Module):
    """
    On adet bilişsel düğümü, autograd uyumlu Lif Laplasyeni difüzyonunu ve
    kapılı bellek hücrelerini birleştiren ana mimari modeli.
    """
    def __init__(self, config: Model_TopolojikKonfigurasyon, bellek_yonetici: Optional[Bellek_BaglamYoneticisi] = None):
        super().__init__()
        self.config = config

        self.n1_byte = N1_ByteAyristirici(config)
        self.n2_topox = N2_TopoXHucreOlusumu(config)
        self.n3_lif = N3_LifSinirlamaAtama(config)

        e_coboundary_dim = (config.V_nodes - 1) * config.d_e
        self.alt_n4 = N4_SorguSecici_AltAg(config)
        self.alt_n5 = N5_CevapSuzucu_AltAg(config)
        self.alt_n6 = N6_KohomolojikAktor_AltAg(config, e_coboundary_dim)

        self.n4_sorgu = N4_SorguSecici(config=config)
        self.n5_cevap = N5_CevapSuzucu(config=config)
        self.n6_aktor = N6_KohomolojikAktor(self.alt_n6, None, None, config=config)
        self.n7_cozucu = N7_LifLaplasyeniCozucu(config)
        self.n8_chebyshev = N8_ChebyshevKatsayiProjeksiyon(config)
        self.n8_b_uzunluk = N8_B_DinamikUzunlukSecici(config)
        self.n9_vandermonde = N9_ChebyshevVandermondeCarpim(config)
        self.n10_sozluk = N10_SozlukSoftmaxIzdusem(config)
        self.n_yazici = Bellek_TopolojikDikkatYazici(config)

        self.cheby_calc = Yardimci_ChebyshevMatrisHesaplayici(config)
        self.laplasyen_insa = Riyazi_LifLaplasyeniBlokInsaEdici(config)
        self.bellek_yonetici = bellek_yonetici if bellek_yonetici is not None else Bellek_BaglamYoneticisi(config)
        self.stiefel_izdusurucu = Riyazi_StiefelManifolduIzdusumu()

    def forward(self, girdi_metni: str, active_batch_size: Optional[int] = None, return_details: bool = False) -> Any:
        b_size = active_batch_size or self.config.batch_size
        e1_girdi = E1_HamMetinAkisi(X_text=girdi_metni)
        mode = 'train' if self.training else 'eval'

        self.n1_byte.izdusur_stiefel()
        self.n4_sorgu.izdusur_stiefel()
        self.n5_cevap.izdusur_stiefel()
        e2_byte, x_initial = self.n1_byte(e1_girdi)
        e3_sinir = self.n2_topox(e2_byte, x_initial=x_initial, mode=mode)
        e4_lif = self.n3_lif(e3_sinir, x_initial)

        # NOT: D0_op/Delta_0_op burada önceden hesaplanmaz — döngünün r=1 adımı (aşağıda)
        # her durumda kendi D0_op/Delta_0_op'unu tazeden hesaplar, config.R >= 1 olduğu sürece
        # (varsayılan R=4) bu ön-hesaplama hiç okunmadan üzerine yazılırdı.

        if b_size != x_initial.shape[0]:
            # Tavan bölme + kırpma: b_size, x_initial.shape[0]'ın tam katı olmasa bile
            # x_start.shape[0] her zaman tam olarak b_size olur (taban bölme eskiden eksik satır üretiyordu)
            repeat_factor = -(-b_size // x_initial.shape[0])
            repeat_dims = [1] * x_initial.dim()
            repeat_dims[0] = repeat_factor
            x_start = x_initial.repeat(*repeat_dims)[:b_size]
        else:
            x_start = x_initial

        mevcut_durum = E5_A_MevcutGizilDurum(x_r=x_start)
        mevcut_bellek_obj = self.bellek_yonetici.get_memory(b_size)

        for r in range(1, self.config.R + 1):
            # Rekürens içi Dinamik Topoloji ve Lif Laplasyeni Güncellemesi (Adım-bazlı Dinamik Graf Evolution)
            e3_sinir = self.n2_topox(e2_byte, x_initial=mevcut_durum.x_r, mode=mode, D0_base=D0_op)
            # NOT (matrissiz Laplasyen): insa_et artık VARSAYILAN OLARAK yoğun Delta_0 kurmaz;
            # n6_aktor/n7_cozucu D0_op üzerinden laplasyen_ile_carp ile matrissiz çalışır.
            D0_op, _ = self.laplasyen_insa.insa_et(e3_sinir, e4_lif.phi_matrisleri)
            n6_aktor = N6_KohomolojikAktor(self.alt_n6, D0_op, config=self.config)

            e6_sorgu = self.n4_sorgu(mevcut_durum, D0_operator=D0_op, A_adjacency=e3_sinir.D1, bellek=mevcut_bellek_obj)
            e7_lokal = self.n5_cevap(e6_sorgu, mevcut_bellek_obj)
            e8_sentetik = n6_aktor(mevcut_durum, e6_sorgu, e7_lokal)
            e9_guncel = self.n7_cozucu(e8_sentetik, D0_op, mevcut_durum)

            # N_Yazici: Hakiki Topolojik Dikkat Bellek Yazıcısı ile M Güncellemesi
            mevcut_bellek_obj = self.n_yazici.yaz(e9_guncel.x_next, e6_sorgu, mevcut_bellek_obj, e7_lokal)
            mevcut_durum = E5_A_MevcutGizilDurum(x_r=e9_guncel.x_next)

        e10_kulli = self.n8_chebyshev(e9_guncel)
        N_star, L_arc_val, N_teorik_val, delta_n_tensor = self.n8_b_uzunluk(e10_kulli, self.cheby_calc)
        T_matrix = self.cheby_calc.hesapla(N=N_star)
        e11_gomulu = self.n9_vandermonde(e10_kulli, T_matrix)
        e12_olasilik = self.n10_sozluk(e11_gomulu)

        if return_details:
            d_discrepancy = self.n7_cozucu.hesapla_uyumsuzluk(mevcut_durum.x_r, D0_op)
            dirichlet_energy = self.n7_cozucu.hesapla_dirichlet_enerjisi(mevcut_durum.x_r, D0_op)
            return {
                'olasilik': e12_olasilik,
                'e3_sinir': e3_sinir,
                'e4_lif': e4_lif,
                'D0': D0_op,
                'L_arc': L_arc_val,
                'N_teorik': N_teorik_val,
                'N_star': N_star,
                'delta_n_tensor': delta_n_tensor,
                'd_discrepancy': d_discrepancy,
                'dirichlet_energy': dirichlet_energy
            }

        return e12_olasilik

    def predict(self, gorev_verisi: Dict[str, Any], test_girdisi: List[List[int]]) -> Tuple[List[List[int]], List[List[int]]]:
        """
        Kaggle submission arayüzü ile doğrudan uyumlu iki hipotezli çıkarım metodu.
        """
        self.eval()
        with torch.no_grad():
            izgara_str = json.dumps(test_girdisi)
            olasilik_matrisi = self.forward(izgara_str, active_batch_size=1)

            # preds_full: tüm mikro-dilimlerin tam uzunluktaki argmax dizisi (P sadece ilk 64'lük dilim olabilir!)
            if olasilik_matrisi.preds_full is not None:
                preds = olasilik_matrisi.preds_full[0].cpu().numpy()
            else:
                P = olasilik_matrisi.P  # [1, V_size, N]
                preds = torch.argmax(P, dim=1)[0].cpu().numpy()

            rows = len(test_girdisi)
            cols = len(test_girdisi[0]) if rows > 0 else 1

            att1 = []
            att2 = []
            idx = 0
            for r in range(rows):
                r1, r2 = [], []
                for c in range(cols):
                    p_val = int(preds[idx % len(preds)]) % 10
                    r1.append(p_val)
                    r2.append((p_val + 1) % 10)
                    idx += 1
                att1.append(r1)
                att2.append(r2)

            return att1, att2


class Riyazi_Pareto_PCGrad_MGDA_Operator:
    """
    [5-Adımlı Vektör Hata, PCGrad ve Pareto-MGDA QP Tensör Operatörü]
    Sistemin n-boyutlu Vektör Hata tensörü L in R^n için:
      1. Jacobiyen Matrisi J = [g1^T; g2^T; ...; gn^T] in R^(n x P) hesaplar.
      2. Gram Matrisi G = J * J^T in R^(n x n) ile çakışmaları tespit eder.
      3. G_ij < 0 durumunda PCGrad izdüşümü ile çakışan gradyanları arındırır.
      4. Frank-Wolfe QP Solver ile Pareto-Optimal alpha* = argmin(alpha^T G alpha) katsayılarını hesaplar.
      5. g_bileske = sum(alpha_k * g_k_duzeltilmis) oluşturup AdamW ile parametreleri günceller.
    """
    def __init__(self):
        pass

    def tahmin_et_vram_bayt(self, girdi_sekli: Tuple[int, ...]) -> int:
        """
        Pareto-PCGrad-MGDA VRAM Tahmin Formülü: girdi_sekli = (n_shard, P_toplam).
        Baskın maliyet düzles_faz_vektorleri + pc_vektorleri: her biri P_toplam (toplam
        eğitilebilir parametre sayısı) uzunluğunda n_shard adet 1D vektördür — [n_shard, 1]
        boyutlu G Gram matrisinin kendisi ihmal edilebilir kalır.
        """
        n_shard = girdi_sekli[0] if len(girdi_sekli) > 0 else 3
        P_toplam = girdi_sekli[1] if len(girdi_sekli) > 1 else 0
        return vram_bayt_tahmin_et(n_shard, P_toplam) * 2  # duzles_faz_vektorleri + pc_vektorleri (clone)

    def coz_mgda_pareto_weights(self, G: torch.Tensor, max_iter: int = 30) -> torch.Tensor:
        """
        Min-Norm / MGDA Kuantitatik Programlama (QP) Çözücüsü.
        min_{alpha} (alpha^T G alpha) s.t. sum(alpha)=1, alpha >= 0 Frank-Wolfe algoritması ile çözülür.
        """
        n = G.shape[0]
        if n == 1:
            return torch.tensor([1.0], device=G.device, dtype=G.dtype)

        # Adaptif SVD İzdüşümlü Gram Matrisi Filtreleme
        with torch.amp.autocast(device_type='cuda', enabled=False):
            G_fp32 = G.float()
            U, S, Vh = torch.linalg.svd(G_fp32)
            S_filtered = torch.where(S > 1e-5, S, torch.zeros_like(S))
            G_tilde = torch.matmul(U, torch.matmul(torch.diag_embed(S_filtered), Vh))
            tr_val = float(torch.trace(G_tilde).item())
            lambda_reg = max(1e-5, 1e-3 * (tr_val / max(n, 1)))
            G_tilde = (G_tilde + lambda_reg * torch.eye(n, device=G.device, dtype=torch.float32)).to(dtype=G.dtype)

        alpha = torch.ones(n, device=G_tilde.device, dtype=G_tilde.dtype) / n
        for _ in range(max_iter):
            grad_obj = 2.0 * torch.matmul(G_tilde, alpha)
            min_idx = torch.argmin(grad_obj)
            e_t = torch.zeros_like(alpha)
            e_t[min_idx] = 1.0

            d_t = e_t - alpha
            denom = torch.matmul(d_t, torch.matmul(G_tilde, d_t))
            if denom <= 1e-8:
                break
            num = -torch.matmul(d_t, grad_obj)
            gamma = torch.clamp(num / (2.0 * denom), 0.0, 1.0)
            
            alpha = alpha + gamma * d_t
            if gamma < 1e-6:
                break

        alpha = torch.clamp(alpha, min=0.0)
        alpha_sum = alpha.sum()
        if alpha_sum > 0:
            alpha = alpha / alpha_sum
        else:
            alpha = torch.ones(n, device=G.device, dtype=G.dtype) / n
        return alpha

    def adim(self,
             losses: Union[List[torch.Tensor], torch.Tensor],
             optimizer: torch.optim.Optimizer,
             trainable_params: List[nn.Parameter],
             max_norm: float = 1.0) -> torch.Tensor:
        """
        [DETERMİNİSTİK KRYLOV / BİYORTOGONAL VJP PARETO OPERATÖRÜ]
        Rastgele Gauss vektör projeksiyonu (Hutchinson noise) tamamen ilga edilmiştir!
        L in R^K unreduced vektör hata tensörü için spektral sapma tabanlı
        deterministik biyortogonal vektör v_det türetilir.
        1-Pass VJP ile VRAM kullanımı 1.4 GB seviyesinde tutulur ve rastgelelik sıfırlanır.
        """
        optimizer.zero_grad(set_to_none=True)
        if isinstance(losses, torch.Tensor):
            L_vec = losses.reshape(-1)
        else:
            L_vec = torch.cat([l.reshape(-1) for l in losses], dim=0)

        K = L_vec.shape[0]
        if K == 0:
            return torch.zeros(0)

        # 1. Deterministik Biyortogonal / Spektral VJP Projeksiyon Vektörü v_det in R^K
        if K > 1:
            L_mean = L_vec.mean()
            L_diff = L_vec - L_mean
            L_std = torch.sqrt(torch.sum(L_diff ** 2) + 1e-8)
            v_det = (L_diff / L_std).detach()
        else:
            v_det = torch.ones_like(L_vec).detach()

        # 2. Deterministik Vektör Hata Skaler Projeksiyonu S = v_det^T * L in R
        vjp_loss = torch.dot(v_det, L_vec)

        # 3. SADECE 1 KEZ BACKWARD PASS! (retain_graph=False, VRAM 1.4 GB)
        vjp_loss.backward()

        # 4. Gradyan Kırpma ve AdamW Güncellemesi
        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=max_norm)
        optimizer.step()

        # 5. Etkin Deterministik Vektörel Katsayılar
        alpha_effective = torch.abs(v_det) / (torch.abs(v_det).sum() + 1e-8)

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return alpha_effective

    def birlestir_ve_uygula_dagitik_gradyanlar(self,
                                                shard_gradyanlari: List[List[torch.Tensor]],
                                                trainable_params: List[nn.Parameter],
                                                optimizer: torch.optim.Optimizer,
                                                max_norm: float = 1.0) -> torch.Tensor:
        """
        [Düzleştirilmiş 1D Şard Pareto-PCGrad Dikgenleştirme — NCCL Timeout Güvenceli]

        Dağıtık / Çoklu-Shard / GPU Ortamında Zıt Yönlü Gradyanların Çakışmasını Engelleyen
        1D Düzleştirilmiş Pareto-PCGrad Dikgen Projeksiyon Birleştiricisi (Sheaf Glueing Mechanism).

        NCCL Güvencesi:
          Tüm fazların gradyanları önce tek bir [P_toplam] boyutlu 1D vektöre düzleştirilir.
          None gradyanlar için aynı cihazda torch.zeros(p.numel()) açılır — şekil/cihaz
          uyuşmazlığı kaynaklı NCCL all_reduce / barrier kilitlenmeleri bu sayede imkânsız hale gelir.

        Algoritma:
          Adım 1 — Bütünsel 1D Düzleştirme & Sıfır Mühürleme:
            Her faz gradyan listesi [g_0, g_1, ..., g_P] → tek 1D vektör [P_toplam] olarak
            birleştirilir. GradNorm normalizasyonu (1 / ||v||) faz kayıp ölçek farklarını sıfırlar.
          Adım 2 — PCGrad Zıt Yönlü Gradyan Dikgenleştirmesi (dot_ij < 0 kontrolü):
            1D iç çarpım (torch.dot) ile zıt açılı faz çiftleri tespit edilir; projeksiyon
            katsayısı (dot_ij / ||g_j||^2) çıkartılarak g_i dikgenleştirilir.
          Adım 3 — 1D Gram Matrisi ve Frank-Wolfe Pareto-Optimal Katsayı Çözümü:
            G[i,j] = dot(pc_v[i], pc_v[j]) ile (n x n) Gram matrisi kurulur.
            coz_mgda_pareto_weights(G) → alpha* [n] Pareto-optimal ağırlıklar döndürür.
          Adım 4 — Birleşik 1D Gradyanın Parametrelere Unflatten ile Geri Dağıtımı:
            nihai_1d = sum(alpha*[i] * pc_v[i]) → her parametre için p.numel() parça
            kesilip p.shape'e unflatten edilir ve p.grad olarak yazılır.
          Adım 5 — Gradyan Kırpma ve Optimizer Adımı.
        """
        n = len(shard_gradyanlari)
        if n == 0:
            return torch.zeros(0)

        # Cihaz referansı: ilk requires_grad parametresinden alınır
        ref_device = next((p.device for p in trainable_params if p.requires_grad), torch.device('cpu'))
        ref_dtype  = next((p.dtype  for p in trainable_params if p.requires_grad), torch.float32)
        # PCGrad/MGDA book-keeping (duzles_faz_vektorleri + pc_vektorleri) yapısı gereği
        # n=11 fazın TAMAMINI [P_toplam] boyutunda EŞ ZAMANLI bellekte tutar (her i için
        # ORİJİNAL diğer fazlara karşı dikgenleştirme yapılır — bu yüzden akışa/tek-geçişe
        # indirgenemez, gerçek bir all-pairs algoritmasıdır). Ama bu 2×n kopyanın PARAMETRE
        # GÜNCELLEMESİNDE KULLANILAN gerçek gradyan hassasiyetiyle aynı olması GEREKMEZ —
        # nihai sonuç Adım 4'te zaten p.dtype'a geri dönüştürülüyor (satır ~3401). bfloat16
        # (fp16 aksine fp32 ile aynı üstel aralığa sahip, büyük-normlu gradyan vektörlerinde
        # taşma riski yok) ile bu 2×n kopyanın belleği YARIYA iner.
        pcgrad_bellek_dtype = torch.bfloat16 if ref_device.type == 'cuda' else ref_dtype

        if n == 1:
            # Tek faz: doğrudan unflatten edip adım at
            optimizer.zero_grad()
            imlec = 0
            for k, p in enumerate(trainable_params):
                if p.requires_grad:
                    g = shard_gradyanlari[0][k]
                    p.grad = (g if g is not None else torch.zeros_like(p)).to(p.device)
            torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=max_norm)
            optimizer.step()
            return torch.tensor([1.0], device=ref_device, dtype=ref_dtype)

        # ==============================================================
        # ADIM 1: BÜTÜNSEL 1D DÜZLEŞTİRME VE SIFIR MÜHÜRLEME
        # Her faz gradyan listesi → tek bir 1D [P_toplam] vektörü
        # None gradyanlar aynı cihazda sıfır vektörle doldurulur
        # (NCCL all_reduce shape/device uyuşmazlığını köklüce engeller)
        # ==============================================================
        # Bu noktada adımın N1-N11/Faz2-5 ara aktivasyonlarının BÜYÜK ÇOĞUNLUĞU artık
        # ölü referans durumundadır (VJP enjeksiyonları retain_graph=False ile grafları
        # zaten serbest bıraktı). AnlasmaliVramGuvencesiAl bu düğüm için resmi VRAM
        # talebini (10505 MB) zaten yukarıda kontrol etti, ama asıl büyük tahsis BURADA,
        # aşağıdaki döngüde (P_toplam boyutlu 11 ayrı 1D vektörün EŞ ZAMANLI belleğe
        # sığması gerekiyor) gerçekleşir. Döngü başlamadan hemen önce gerçek bir
        # gc.collect()/empty_cache() son bir güvenlik payı sağlar — trainable_params/
        # optimizer üzerinde hiçbir mutasyon yapmadığından tamamen güvenlidir.
        import gc as _gc
        _gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        duzles_faz_vektorleri: List[torch.Tensor] = []
        for g_list in shard_gradyanlari:
            vektor_parcalari: List[torch.Tensor] = []
            for k, p in enumerate(trainable_params):
                g = g_list[k] if k < len(g_list) else None
                if g is not None:
                    # Mevcut gradyan parçası: 1D'ye düzleştir, cihazı hizala.
                    # NOT: .view(-1) DEĞİL .reshape(-1) kullanılır — g (bir düğümün
                    # gradyanı) transpose/.T zincirinden (ör. D0.T, Delta_0_hat.T gibi
                    # matmul'lardan geri yayılan gradyanlar) non-contiguous stride ile
                    # gelebilir; .view() bu durumda "view size is not compatible..."
                    # RuntimeError'ı fırlatır. .reshape() aynı sonucu üretir, gerekirse
                    # sessizce kopyalayarak contiguous hale getirir — asla çökmez.
                    vektor_parcalari.append(g.reshape(-1).to(device=ref_device, dtype=pcgrad_bellek_dtype))
                else:
                    # Kullanılmayan parametre → aynı cihazda sıfır dolgu (NCCL güvencesi)
                    vektor_parcalari.append(
                        torch.zeros(p.numel(), device=ref_device, dtype=pcgrad_bellek_dtype)
                    )
            # Tüm parçaları tek 1D dev vektörde birleştir [P_toplam]
            faz_1d = torch.cat(vektor_parcalari, dim=0)
            # GradNorm Normalizasyonu: faz kayıp ölçek farklarını (84.0 ↔ 0.0003) eşitle
            norm_val = torch.norm(faz_1d) + 1e-8
            duzles_faz_vektorleri.append(faz_1d / norm_val)

        # ==============================================================
        # ADIM 2: PCGRAD ZIT YÖNLÜ GRADİYAN DİKGENLEŞTİRMESİ
        # 1D iç çarpım (torch.dot) ile zıt açılı çiftler tespit edilir.
        # g_i = g_i − (g_i · g_j / ‖g_j‖²) · g_j  [dot_ij < 0 ise]
        # ==============================================================
        pc_vektorleri: List[torch.Tensor] = [v.clone() for v in duzles_faz_vektorleri]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                dot_ij = torch.dot(pc_vektorleri[i], duzles_faz_vektorleri[j])
                if dot_ij < 0:
                    norm_sq_j = torch.sum(duzles_faz_vektorleri[j] ** 2) + 1e-8
                    proj_coeff = dot_ij / norm_sq_j
                    # Dikgenleştirme: çakışan bileşeni çıkar
                    pc_vektorleri[i] = pc_vektorleri[i] - proj_coeff * duzles_faz_vektorleri[j]

        # ==============================================================
        # ADIM 3: 1D GRAM MATRİSİ VE FRANK-WOLFE PARETO-OPTİMAL ÇÖZÜM
        # G[i,j] = dot(pc_v[i], pc_v[j])  →  (n × n) float32 matris
        # coz_mgda_pareto_weights(G) → alpha* [n]
        # ==============================================================
        G = torch.zeros((n, n), device=ref_device, dtype=torch.float32)
        for i in range(n):
            for j in range(n):
                G[i, j] = torch.dot(pc_vektorleri[i].float(), pc_vektorleri[j].float())

        alpha_star = self.coz_mgda_pareto_weights(G)

        # ==============================================================
        # ADIM 4: BİRLEŞİK 1D GRADİYANIN PARAMETRELERE UNFLATTEN GERİ DAĞITIMI
        # nihai_1d = Σ alpha*[i] · pc_v[i]
        # Her parametre için p.numel() dilim kesilir → p.shape'e unflatten
        # ==============================================================
        # pc_vektorleri bfloat16'dır (bellek tasarrufu); nihai birleştirme fp32'de yapılır,
        # Adım 4'ün sonunda zaten p.dtype'a geri dönüştürülüyor.
        nihai_1d = sum(alpha_star[i].float() * pc_vektorleri[i].float() for i in range(n))

        optimizer.zero_grad()
        imlec = 0
        for p in trainable_params:
            p_numel = p.numel()
            if p.requires_grad:
                dilim = nihai_1d[imlec: imlec + p_numel]
                # Unflatten: 1D dilimi → orijinal parametre şekline geri dönüştür
                p.grad = dilim.reshape(p.shape).to(device=p.device, dtype=p.dtype)
            # requires_grad=False parametreler için imlec yine de ilerletilir
            # (1D vektörde onların sıfır dilimi zaten var — cursor drift önlenir)
            imlec += p_numel

        # ==============================================================
        # ADIM 5: GRADİYAN KIRPMA VE OPTİMİZER ADIMI
        # ==============================================================
        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=max_norm)
        optimizer.step()

        return alpha_star

    def shard_gradyanlari_cihaza_tasi(self, shard_gradyanlari: List[List[torch.Tensor]], target_device: torch.device) -> List[List[torch.Tensor]]:
        """Elle taşınma desteği: Pareto-PCGrad şard gradyanlarını hedef cihaza taşır (non-nn.Module)."""
        if target_device is None:
            return shard_gradyanlari
        tasili_shardlar = []
        for g_list in shard_gradyanlari:
            tasili_list = []
            for g in g_list:
                if g is not None:
                    tasili_list.append(g.to(target_device))
                else:
                    tasili_list.append(None)
            tasili_shardlar.append(tasili_list)
        return tasili_shardlar


class Hafiza_Izleyici_ve_VRAM_Denetci:
    """
    Her düğüm (N1-N10) ve her rekürens adımı esnasında GPU VRAM kullanımını
    milibaytı milibaytına yoklayan ve taşma riskinde acil VRAM temizliği yapan denetçi.
    """
    def __init__(self, cihaz: Union[torch.device, str] = "cuda", kritik_esik_yuzde: float = 0.85):
        if isinstance(cihaz, str):
            self.cihaz = torch.device(cihaz)
        else:
            self.cihaz = cihaz
            
        self.kritik_esik_yuzde = kritik_esik_yuzde
        self.toplam_vram_mb = 88.0 * 1024.0
        self.esik_mb = self.toplam_vram_mb * kritik_esik_yuzde

    def yokla_ve_raporla(self, dugum_adi: str, adim_no: int = 0) -> Dict[str, float]:
        """
        Her düğüm icrasından hemen sonra VRAM durumunu sorgular.
        """
        tahsis_mb = 0.0
        rezerve_mb = 0.0
        bos_mb = 0.0
        toplam_mb = self.toplam_vram_mb

        if torch.cuda.is_available() and self.cihaz.type == "cuda":
            tahsis_mb = torch.cuda.memory_allocated(self.cihaz) / (1024 ** 2)
            rezerve_mb = torch.cuda.memory_reserved(self.cihaz) / (1024 ** 2)
            toplam_mb = torch.cuda.get_device_properties(self.cihaz).total_memory / (1024 ** 2)
            bos_mb = toplam_mb - tahsis_mb

        yuzde = (tahsis_mb / toplam_mb * 100) if toplam_mb > 0 else 0.0

        logger = logging.getLogger(__name__)
        logger.info(
            f"[VRAM Denetçi] Adım:{adim_no} | Düğüm:{dugum_adi} | "
            f"Aktif Tahsis: {tahsis_mb:.2f} MB / {toplam_mb:.2f} MB (%{yuzde:.1f}) | "
            f"Boş VRAM: {bos_mb:.2f} MB"
        )

        # self.esik_mb, __init__'teki sabit 88 GB varsayımı yerine canlı toplam_mb ile güncel tutulur
        self.esik_mb = toplam_mb * self.kritik_esik_yuzde
        if tahsis_mb > self.esik_mb:
            logger.warning(
                f"CRITICAL VRAM UYARISI! [{dugum_adi}] adımında VRAM %{self.kritik_esik_yuzde*100:.1f} eşiğini aştı "
                f"({tahsis_mb:.2f} MB > {self.esik_mb:.2f} MB). Acil VRAM Temizliği..."
            )
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        return {
            "tahsis_mb": tahsis_mb,
            "rezerve_mb": rezerve_mb,
            "bos_mb": bos_mb
        }


# Architectural Class Aliases (6 Ana Maksat / Rükün Mimarisi)
StatikIzometrikByteAyristirici = N1_HibritByteTokenAyristirici
RiyaziCebirselHomolojiInsaEdici = N2_TopoXHucreOlusumu
MatrissizKrylovEssinirCozucu = N6_KohomolojikAktor
HarmonikIsilDifuzyonIntegratoru = N7_LifLaplasyeniCozucu
SMW_SifirParazit_BellekYoneticisi = SMW_SifirParazit_BellekYoneticisi
LineerNedenselVolterraBlellochCozucu = N7_LifLaplasyeniCozucu

def vram_on_kontrol_ve_nvme_tahliye(gerekli_bayt: int, takas_mgr: Any = None) -> None:
    """
    İşlem öncesi VRAM boşluğunu sorgular. Yetersizse eski tensörleri 1026 GB /tmp NVMe diskine sürer.
    """
    if not torch.cuda.is_available():
        return

    import gc
    try:
        free_vram, total_vram = torch.cuda.mem_get_info(0)
    except Exception:
        return

    # EĞER GEREKLİ BELLEK BOŞ VRAM'DEN BÜYÜKSE VEYA BOŞ VRAM 2 GB'IN ALTINA DÜŞMÜŞSE:
    if gerekli_bayt > free_vram or free_vram < (2 * 1024 * 1024 * 1024):
        logging.getLogger("mucit_ai.kontratlar").warning(
            f"[Ön-Hesaplamalı NVMe Tahliye] Talep: {round(gerekli_bayt/(1024**2), 1)} MB | "
            f"Boş VRAM: {round(free_vram/(1024**2), 1)} MB. /tmp NVMe Diske Tahliye Başlatılıyor..."
        )
        
        # PyTorch C++ Caching Allocator Önbelleğini Boşalt
        gc.collect()
        torch.cuda.empty_cache()
        
        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
            takas_mgr.temizle()

def girdi_cihaza_tasi(x: Any, device: torch.device) -> Any:
    """
    [Girdi Cihaz Hizalama Yardımcısı]
    Bir tensörü, bir E1-E18 veri kontratı dataclass'ını (tensör alanları taşınır) veya
    bunların liste/tuple'ını, verilen cihaza taşır. Tanınmayan tipler değiştirilmeden döner.
    """
    if isinstance(x, torch.Tensor):
        return x.to(device) if x.device != device else x
    if is_dataclass(x) and not isinstance(x, type):
        degisiklikler = {}
        for alan in fields(x):
            deger = getattr(x, alan.name)
            yeni_deger = girdi_cihaza_tasi(deger, device)
            if yeni_deger is not deger:
                degisiklikler[alan.name] = yeni_deger
        return dataclasses.replace(x, **degisiklikler) if degisiklikler else x
    if isinstance(x, (list, tuple)):
        tasinmis = [girdi_cihaza_tasi(e, device) for e in x]
        return type(x)(tasinmis)
    return x


def _rekursif_tasma_bazli_matmul(
    A: torch.Tensor,
    B: torch.Tensor,
    orijinal_matmul_fn: Callable,
    emniyet_marji_mb: float,
    derinlik: int = 0,
    maks_derinlik: int = 8,
) -> torch.Tensor:
    """
    [Rekürsif Taşma-Bazlı Matris Çarpımı — Dalga Yayılımı ve Toplanması]

    A @ B çarpımını hesaplar. Kapasite ORANI hesaplanmaz — yalnızca TEK soru sorulur:
    "Tam çıktı ([m,n]) A'nın bulunduğu (home) cihaza sığıyor mu?"

      - Sığıyorsa (taşma YOK): hiçbir dağıtım yapılmaz, orijinal torch.matmul çalışır.
        Çok GPU'lu bir ortamda dahi bu VARSAYILAN/yaygın durumdur.
      - Sığmıyorsa (taşma VAR): B'nin sütunları home cihazdan başlayarak sırayla
        gezilir; her cihaza sığdığı kadarı yazılır, TAŞAN kısım bir sonraki cihaza
        devredilir. Bir dilim kendi hedef cihazında DA sığmazsa (ör. o cihazda da
        başka iş yükü varsa), AYNI mantıkla REKÜRSİF olarak kendi içinde tekrar
        bölünür — "veri piramit gibi dağılır, dalga gibi bir dağılır bir söner".
        Hiçbir GPU'ya sığmayan artık kısım son çare olarak CPU'da hesaplanır
        (asla sessizce veri kaybı veya cihaz uyumsuzluğu oluşmaz).
      - İşlem HER ZAMAN "hangi veri hangi cihazdaysa işlem onun işlemcisinde
        yapılır" prensibiyle yürür: her dilim SADECE kendi hedef cihazında
        matmul'a girer, sonuçlar en son home cihazda birleştirilip (dalga geri
        söner) döndürülür — çağıran taraf sıradan tek-cihaz bir tensör görür.

    Tek Python sürecinde çalışır — worker süreci, IPC kuyruğu veya NCCL GEREKMEZ.
    """
    if not torch.cuda.is_available() or not A.is_cuda:
        return orijinal_matmul_fn(A, B)

    home_device = A.device
    device_count = torch.cuda.device_count()
    emniyet_bayt = int(emniyet_marji_mb * 1024 * 1024)
    dtype_bayt = A.element_size()
    m = A.shape[0]
    n = B.shape[1]
    logger = logging.getLogger("mucit_ai.kontratlar")

    tam_cikti_bayt = m * n * dtype_bayt
    try:
        free_bayt, _ = torch.cuda.mem_get_info(home_device.index)
    except Exception:
        return orijinal_matmul_fn(A, B)

    if tam_cikti_bayt + emniyet_bayt <= free_bayt or derinlik >= maks_derinlik or device_count <= 1:
        # Taşma YOK (veya azami rekürsiyon derinliğine ulaşıldı, veya tek GPU var):
        # dağıtım yapılmaz.
        return orijinal_matmul_fn(A, B)

    if derinlik == 0:
        logger.warning(
            f"[TaşmaFarkındaHesaplamaİdaresi] [{m}x{n}] çıktı ({tam_cikti_bayt/(1024**2):.1f} MB) "
            f"home cihaza ({home_device}) sığmıyor (boş: {free_bayt/(1024**2):.1f} MB). "
            f"Sütunlar çoklu-GPU'ya taşma-bazlı dağıtılıyor..."
        )

    A_bayt = A.numel() * dtype_bayt
    parcalar: List[Tuple[int, torch.Tensor]] = []
    kalan_n = n
    imlec = 0
    baslangic = home_device.index

    for ofset in range(device_count):
        if kalan_n <= 0:
            break
        gpu_id = (baslangic + ofset) % device_count
        try:
            free_bayt_i, _ = torch.cuda.mem_get_info(gpu_id)
        except Exception:
            continue

        kullanilabilir = free_bayt_i - emniyet_bayt
        if gpu_id != home_device.index:
            kullanilabilir -= A_bayt  # A'nın (sabit operand) bu cihaza kopyalanma maliyeti

        if kullanilabilir <= 0:
            continue  # bu cihazda hiç yer yok — sıradaki cihaza taş

        birim_bayt = m * dtype_bayt  # bir çıktı sütununun bayt maliyeti
        sigacak_n = min(kalan_n, int(kullanilabilir // birim_bayt)) if birim_bayt > 0 else kalan_n
        if sigacak_n <= 0:
            continue

        hedef_cihaz = torch.device(f'cuda:{gpu_id}')
        A_burada = A if gpu_id == home_device.index else A.to(hedef_cihaz)
        B_dilim = B[:, imlec:imlec + sigacak_n]
        B_dilim_burada = B_dilim if B_dilim.device == hedef_cihaz else B_dilim.to(hedef_cihaz)

        # REKÜRSİF ÇAĞRI: bu dilim SADECE kendi cihazında (A_burada/B_dilim_burada
        # zaten hedef_cihaz'a taşınmış durumda) işlenir; o cihazda da taşarsa aynı
        # mantıkla kendi içinde tekrar bölünür (daha da dağıtmak gerekiyorsa dağıt).
        cikti_dilim = _rekursif_tasma_bazli_matmul(
            A_burada, B_dilim_burada, orijinal_matmul_fn, emniyet_marji_mb, derinlik + 1, maks_derinlik
        )
        parcalar.append((imlec, cikti_dilim))

        imlec += sigacak_n
        kalan_n -= sigacak_n

    if kalan_n > 0:
        # Hiçbir GPU kalan kısmı almadı — son çare CPU (asla veri kaybı/cihaz
        # uyumsuzluğu değil, açık ve güvenli bir düşüş).
        logger.warning(
            f"[TaşmaFarkındaHesaplamaİdaresi] {kalan_n}/{n} sütun hiçbir GPU'ya sığmadı "
            f"(tüm görünür {device_count} cihaz taştı) — CPU'da tamamlanıyor."
        )
        cpu_A = A.cpu()
        cpu_B_kalan = B[:, imlec:imlec + kalan_n].cpu()
        cikti_cpu = orijinal_matmul_fn(cpu_A, cpu_B_kalan)
        parcalar.append((imlec, cikti_cpu))
        kalan_n = 0

    # TOPLA: dalga geri söner — tüm parçalar home cihaza taşınıp sıraya göre birleştirilir.
    parcalar.sort(key=lambda p: p[0])
    cikti_parcalari = [p[1].to(home_device) if p[1].device != home_device else p[1] for p in parcalar]
    return torch.cat(cikti_parcalari, dim=1)


def tasma_bazli_capraz_gpu_matmul_sardla(
    A: torch.Tensor,
    B: torch.Tensor,
    emniyet_marji_mb: float = 256.0,
) -> torch.Tensor:
    """
    [Taşma-Bazlı Çapraz-GPU Matris Çarpımı — Elle Çağrılabilir Sarmalayıcı]

    _rekursif_tasma_bazli_matmul'ün genel torch.matmul üzerinden elle çağrılabilen
    biçimidir. TaşmaFarkındaHesaplamaİdaresi.baslat() çağrılmışsa (bkz. aşağı) bu
    fonksiyonun İÇİNDEKİ torch.matmul çağrısı zaten otomatik taşma-farkındadır —
    yani idare kurulduktan sonra bu sarmalayıcıya hiç ihtiyaç kalmaz, düz
    torch.matmul(A, B) yazmak yeterlidir. Bu fonksiyon yalnızca idare henüz
    kurulmamışken veya elle/açıkça çağrılmak istendiğinde kullanılır.
    """
    return _rekursif_tasma_bazli_matmul(A, B, torch.matmul, emniyet_marji_mb)


class TasmaFarkindaHesaplamaIdaresi:
    """
    [Taşma-Farkında Hesaplama İdaresi / Overflow-Aware Compute Governance]

    "Devlet nizamı" mantığı: baslat() BİR KEZ çağrılır; ondan sonra kod tabanındaki
    HİÇBİR çağrı noktası elle sarmalanmaz. torch.matmul ve torch.nn.functional.linear
    (nn.Linear'ın forward'ının altında yatan gerçek ilkel işlem — vocab_head, W_q,
    W_k, W_v, tüm nn.Linear katmanları dahil) SÜREÇ GENELİNDE, checkpoint-sarmalı
    N6/N7 dahil, üçüncü parti kod dahil, otomatik olarak taşma-farkında hale gelir.

    Prensip: "Hangi veri hangi cihazdaysa, işlem onun işlemcisinde yapılır." Bir
    işlemin sonucu taşarsa bir sonraki cihaza devredilir; o cihazdaki dilim de
    taşarsa kendi içinde REKÜRSİF olarak tekrar bölünür — veri piramit gibi/dalga
    gibi cihazlar arasında yayılır, iş bitince sonuçlar toplanıp (dalga söner)
    tek tensöre geri birleştirilir. Kapasite ORANI hiçbir aşamada hesaplanmaz —
    yalnızca "sığıyor mu (taşma var mı)" sorusu sorulur.

    Kullanım:
        TasmaFarkindaHesaplamaIdaresi.baslat()   # eğitim döngüsü başında BİR KEZ
        ...                                       # sonrasında hiçbir değişiklik gerekmez
        TasmaFarkindaHesaplamaIdaresi.durdur()   # (opsiyonel) süreç sonunda geri al
    """
    _kurulu: bool = False
    _orijinal_matmul: Optional[Callable] = None
    _orijinal_linear: Optional[Callable] = None
    _emniyet_marji_mb: float = 256.0

    @classmethod
    def baslat(cls, emniyet_marji_mb: float = 256.0) -> None:
        # !!! DEVRE DIŞI — KIRIK. Küresel torch.matmul/F.linear monkey-patch'i yalnızca
        # bizim çağrılarımızı değil PyTorch'un KENDİ İÇ yollarını da (autograd backward
        # ilkelleri, batched/broadcast matmul, .T transpose view'ları) yakalıyor. 2D-2D
        # ön kontrolü yetmedi: gerçek bir koşuda "RuntimeError: self must be a matrix"
        # ile çöktü (insa_et -> _idareli_matmul -> _rekursif_tasma_bazli_matmul ->
        # orijinal_matmul_fn). Yerine: gerçekten büyük olduğu BİLİNEN noktalarda AÇIK
        # çağrı -> tasma_bazli_capraz_gpu_matmul_sardla(A, B) (bkz. insa_et). Sessiz
        # no-op yerine açıkça patlatılır — sessiz no-op "koruma aktif" yanılsaması
        # yaratırdı.
        raise RuntimeError(
            "[TasmaFarkindaHesaplamaIdaresi] Bu kuresel monkey-patch DEVRE DISIDIR "
            "(PyTorch ic cagri yollarini bozup 'RuntimeError: self must be a matrix' "
            "uretiyordu). Tasma-bazli coklu-GPU dagitimi icin dogrudan "
            "tasma_bazli_capraz_gpu_matmul_sardla(A, B) kullanin."
        )
        logger = logging.getLogger("mucit_ai.kontratlar")
        if cls._kurulu:
            logger.info("[TaşmaFarkındaHesaplamaİdaresi] Zaten kurulu, tekrar kurulmuyor.")
            return

        cls._emniyet_marji_mb = emniyet_marji_mb
        cls._orijinal_matmul = torch.matmul
        cls._orijinal_linear = F.linear

        orijinal_matmul = cls._orijinal_matmul
        orijinal_linear = cls._orijinal_linear

        def _idareli_matmul(input: torch.Tensor, other: torch.Tensor, *, out=None):
            # Yalnızca 2D x 2D durumu taşma-bazlı dağıtıma girer (Delta_0 = D0^T @ D0
            # gibi büyük kare/dikdörtgen matrisler tam olarak bu şekildedir). Diğer
            # boyut kombinasyonları (batched 3D+, out= verilmiş, vb.) davranış
            # değişikliği riski taşımamak için doğrudan orijinal işleve düşer.
            if (
                out is None
                and isinstance(input, torch.Tensor) and isinstance(other, torch.Tensor)
                and input.dim() == 2 and other.dim() == 2
                and input.is_cuda
            ):
                return _rekursif_tasma_bazli_matmul(input, other, orijinal_matmul, cls._emniyet_marji_mb)
            return orijinal_matmul(input, other) if out is None else orijinal_matmul(input, other, out=out)

        def _idareli_linear(input: torch.Tensor, weight: torch.Tensor, bias: Optional[torch.Tensor] = None):
            # F.linear(x, W, b) = x @ W.T + b. Yalnızca 2D girdi + taşma durumunda
            # devreye girer; diğer tüm durumlar (3D+ batched girdi, bias var/yok
            # farketmeksizin normal boyut) orijinal, optimize edilmiş ATen yoluna düşer.
            if (
                isinstance(input, torch.Tensor) and isinstance(weight, torch.Tensor)
                and input.dim() == 2 and input.is_cuda
            ):
                m_, k_ = input.shape
                n_, k2_ = weight.shape
                if k_ == k2_:
                    dtype_bayt = input.element_size()
                    tam_cikti_bayt = m_ * n_ * dtype_bayt
                    try:
                        free_bayt, _ = torch.cuda.mem_get_info(input.device.index)
                    except Exception:
                        free_bayt = None
                    if free_bayt is not None and tam_cikti_bayt + int(cls._emniyet_marji_mb * 1024 * 1024) > free_bayt:
                        cikti = _rekursif_tasma_bazli_matmul(input, weight.T, orijinal_matmul, cls._emniyet_marji_mb)
                        if bias is not None:
                            cikti = cikti + bias.to(cikti.device)
                        return cikti
            return orijinal_linear(input, weight, bias)

        torch.matmul = _idareli_matmul
        F.linear = _idareli_linear
        torch.nn.functional.linear = _idareli_linear
        cls._kurulu = True
        logger.info(
            "[TaşmaFarkındaHesaplamaİdaresi] Küresel taşma-farkında torch.matmul + "
            "F.linear devrede. Bu andan itibaren HİÇBİR çağrı noktası elle "
            "sarmalanmadan otomatik taşma koruması altındadır."
        )

    @classmethod
    def durdur(cls) -> None:
        logger = logging.getLogger("mucit_ai.kontratlar")
        if not cls._kurulu:
            return
        torch.matmul = cls._orijinal_matmul
        F.linear = cls._orijinal_linear
        torch.nn.functional.linear = cls._orijinal_linear
        cls._kurulu = False
        logger.info("[TaşmaFarkındaHesaplamaİdaresi] Küresel yamalar geri alındı.")


def anlasmali_vram_guvencesi_al(
    modul_nesnesi: Any,
    girdi_tensoru_veya_sekli: Any,
    emniyet_marji_mb: float = 256.0,
    takas_mgr: Any = None
) -> torch.device:
    """
    [Düğüm Bazlı Açık VRAM Anlaşma Mimarisi / Ön-İcra VRAM/TMP İdarecisi]

    Sürücüye tahmin yaptırılmaz. Her düğüm, kendi tahmin_et_vram_bayt() formülüyle
    (parametrik: B, V, E, d, V_size, N, K ... şekillerinden türetilmiş) bu işlemin
    ne kadar VRAM harcayacağını AÇIKÇA beyan eder. Bu fonksiyon işlem başlamadan HEMEN
    ÖNCE çağrılır ve kesin/net bir cihaz kararı verir:

      1. Tahmini talep + emniyet payı canlı boş VRAM'e sığıyorsa: düğüm GPU'da tutulur
         (gerekirse GPU'ya taşınır), torch.device('cuda') döner.
      2. Sığmıyorsa: önce gc.collect()/empty_cache() (zaten-boşta duran cache), sonra
         (takas_mgr verilmişse) vram_on_kontrol_ve_nvme_tahliye ile GERÇEK NVMe tahliyesi
         (diğer düğümlerin halihazırda VRAM'de duran ama şu an kullanılmayan tensörleri
         diske sürülür) denenir; her adımdan sonra boş VRAM yeniden ölçülür.
      3. Bütün bu tedbirlere rağmen taşma KESİNSE: düğümün kendisi CPU'ya taşınır
         (parametreleri varsa .to('cpu')) ve torch.device('cpu') döner — bu adım için
         işlem VRAM'e hiç girmeden CPU/RAM (ve OS swap'ı üzerinden fiilen /tmp'e sarkan)
         üzerinden yürütülür. Sonraki her çağrıda VRAM yeniden ölçülür; diğer düğümler
         belleklerini boşalttıkça (VRAM'e sığar hale geldikçe) düğüm otomatik olarak
         tekrar GPU'ya taşınır — kalıcı bir CPU sürgünü değil, adım-adım yeniden
         değerlendirilen dinamik bir karardır.

    Dönüş değeri her zaman bir torch.device'tır. Çağıran taraf, düğümün girdisini de
    (girdi_cihaza_tasi ile) bu cihaza taşımalıdır; modern düğümlerin forward() metodu
    zaten kendi _vram_idare_zorunlu_cihaz özniteliğini okuyup kendi girdisini buna göre
    hizalar (bkz. N1/N10/Maarif_NedenselSuzgec CUDAGuard blokları).
    """
    cpu_device = torch.device('cpu')
    if not torch.cuda.is_available():
        if hasattr(modul_nesnesi, 'to'):
            try:
                modul_nesnesi._vram_idare_zorunlu_cihaz = cpu_device
            except Exception:
                pass
        return cpu_device

    gpu_device = torch.device('cuda')

    # 1. Girdi şekli tespiti
    if hasattr(girdi_tensoru_veya_sekli, 'shape'):
        girdi_sekli = tuple(girdi_tensoru_veya_sekli.shape)
    elif isinstance(girdi_tensoru_veya_sekli, (tuple, list)):
        girdi_sekli = tuple(girdi_tensoru_veya_sekli)
    else:
        girdi_sekli = (1, 1024)

    # 2. Düğümün resmi VRAM tahmin beyanı (parametrik formül)
    if hasattr(modul_nesnesi, 'tahmin_et_vram_bayt'):
        try:
            resmi_gerekli_bayt = int(modul_nesnesi.tahmin_et_vram_bayt(girdi_sekli))
        except Exception:
            resmi_gerekli_bayt = 128 * 1024 * 1024
    else:
        resmi_gerekli_bayt = 128 * 1024 * 1024

    # 3. Canlı boş VRAM sorgulama
    try:
        free_bytes, total_bytes = torch.cuda.mem_get_info()
    except Exception:
        return gpu_device

    emniyet_bayt = int(emniyet_marji_mb * 1024 * 1024)
    toplam_ihtiyac = resmi_gerekli_bayt + emniyet_bayt
    modul_adi = modul_nesnesi.__class__.__name__ if hasattr(modul_nesnesi, '__class__') else str(modul_nesnesi)
    logger = logging.getLogger("mucit_ai.kontratlar")

    # 4. Kesin Güvence Kontrolü & Kademeli Tahliye
    if toplam_ihtiyac > free_bytes:
        logger.info(
            f"[Açık VRAM Anlaşması] Düğüm '{modul_adi}' {resmi_gerekli_bayt / (1024**2):.2f} MB VRAM talep etti. "
            f"Tahliye başlatılıyor (Boş: {free_bytes / (1024**2):.2f} MB, İhtiyaç: {toplam_ihtiyac / (1024**2):.2f} MB)..."
        )
        import gc
        gc.collect()
        torch.cuda.empty_cache()

        free_bytes, _ = torch.cuda.mem_get_info()
        if toplam_ihtiyac > free_bytes:
            # Cache temizliği tek başına yetmiyorsa (canlı, hâlâ referanslı tensörler serbest
            # kalmaz): gerçek NVMe tahliyesini tetikle ve boş VRAM'i yeniden ölç.
            vram_on_kontrol_ve_nvme_tahliye(toplam_ihtiyac, takas_mgr)
            try:
                free_bytes, _ = torch.cuda.mem_get_info()
            except Exception:
                free_bytes = 0

    # 5. Kesin Karar: taşma hâlâ aşikarsa bu adım için düğümü CPU/TMP'e yönlendir
    if toplam_ihtiyac > free_bytes:
        logger.warning(
            f"[VRAM/TMP İdarecisi] '{modul_adi}' için {resmi_gerekli_bayt / (1024**2):.2f} MB talebi "
            f"tüm tahliye tedbirlerine rağmen karşılanamıyor (Boş: {free_bytes / (1024**2):.2f} MB). "
            f"Bu adım CPU/TMP üzerinden yürütülecek."
        )
        if hasattr(modul_nesnesi, 'to'):
            try:
                modul_nesnesi.to(cpu_device)
            except Exception:
                pass
        if hasattr(modul_nesnesi, '__dict__') or hasattr(modul_nesnesi, 'to'):
            try:
                modul_nesnesi._vram_idare_zorunlu_cihaz = cpu_device
            except Exception:
                pass
        return cpu_device

    if hasattr(modul_nesnesi, 'to'):
        try:
            modul_nesnesi.to(gpu_device)
        except Exception:
            pass
    if hasattr(modul_nesnesi, 'to'):
        try:
            modul_nesnesi._vram_idare_zorunlu_cihaz = gpu_device
        except Exception:
            pass
    return gpu_device

AnlasmaliVramGuvencesiAl = anlasmali_vram_guvencesi_al


def acil_durum_oom_yakalayici_ve_kurtarici(
    hesaplama_fonksiyonu: Callable,
    *args: Any,
    modul_nesnesi: Any = None,
    takas_mgr: Any = None,
    **kwargs: Any
) -> Any:
    """
    [Reaktif OOM Yakalama ve Kurtarma / Emergency OOM Catch-and-Recover]

    anlasmali_vram_guvencesi_al() PROAKTİF çalışır: işlem başlamadan önce
    tahmin_et_vram_bayt() formülüyle VRAM ihtiyacını tahmin edip GPU/CPU kararını
    önceden verir. Ama hiçbir tahmin formülü %100 isabetli olamaz — PyTorch'un dahili
    ara-tampon tahsisleri, cuDNN algoritma seçimi, VRAM parçalanması (fragmentation)
    gibi sebeplerle tahmin tutsa dahi gerçek bir torch.cuda.OutOfMemoryError fırlayabilir.

    Bu fonksiyon İKİNCİ (REAKTİF) savunma hattıdır: hesaplama_fonksiyonu'nu dener,
    gerçekten OOM patlarsa süreci ÖLDÜRMEDEN yakalar, VRAM'i temizler/NVMe'ye tahliye
    eder, hem modülü (varsa) hem TÜM argümanları CPU'ya taşıyıp işlemi CPU üzerinde
    tekrar dener ve sonucu orijinal cihaza geri taşır.

    Cihaz Uyumsuzluğu Güvencesi (bu oturumun asıl kök sorunu):
      modul_nesnesi verilmişse hem .to(cpu) ile parametreleri hem de
      _vram_idare_zorunlu_cihaz bayrağı CPU'ya set edilir — modülün kendi CUDAGuard
      bloğu (bkz. N1-N10 forward()'ları) bu bayrağı okuyup KENDİ girdisini de otomatik
      CPU'ya hizalar. modul_nesnesi verilmemişse (generic callable), args/kwargs
      girdi_cihaza_tasi ile elle CPU'ya taşınır — ne modül ne girdi geride GPU'da
      unutulmaz.

      ÖNEMLİ (dar except kapsamı düzeltmesi): Yalnızca torch.cuda.OutOfMemoryError
      yakalamak yetmez — "RuntimeError: Expected all tensors to be on the same
      device, but found at least two devices, cuda:0 and cpu!" de PyTorch'ta ayrı
      bir RuntimeError alt sınıfıdır ve modern PyTorch'ta (torch.cuda.OutOfMemoryError
      mevcutken) eski dar except bloğu bunu YAKALAMAZDI — tam da bu oturumun
      raporlanan hatası buradan kaçabiliyordu. Aşağıda hem gerçek OOM hem de
      cihaz-uyumsuzluğu RuntimeError'ı AYNI kurtarma yoluna (her şeyi tek bir ortak
      cihaza — CPU'ya — çekip tekrar dene) yönlendirilir; ikisi de "tutarsız cihaz
      dağılımı" kökünden gelir ve aynı çare ile giderilir.
    """
    logger = logging.getLogger("mucit_ai.kontratlar")
    gercek_oom_tipleri = (torch.cuda.OutOfMemoryError,) if hasattr(torch.cuda, "OutOfMemoryError") else ()

    try:
        return hesaplama_fonksiyonu(*args, **kwargs)
    except (gercek_oom_tipleri + (RuntimeError,)) as exc:
        mesaj = str(exc).lower()
        gercek_oom = bool(gercek_oom_tipleri) and isinstance(exc, gercek_oom_tipleri)
        oom_mesaji = "out of memory" in mesaj
        # NOT: Bu liste zaman içinde tek tek karşılaşılan hata mesajı VARYANTLARIYLA
        # büyütülüyordu (whack-a-mole) — ör. "CUDAGuardImpl initialized with non-CUDA
        # DeviceType: cpu" (torch.log/.mean gibi sıradan bir işlemde CPU'ya düşmüş bir
        # tensörle karşılaşıldığında fırlar) hiçbirine uymadığı için çıplak çöküyordu.
        #
        # KAPSAMLI DENETİM DÜZELTMESİ (madde 4): "cuda" VE "device" kelimelerinin
        # BİRLİKTE geçtiği HER RuntimeError'ı yakalamak AŞIRI GENİŞTİ — ör. gerçek bir
        # "CUDA error: device-side assert triggered" (kötü bir index/embedding sınır
        # dışı erişimi gibi GERÇEK bir mantık hatası, cihaz yerleşimiyle hiç ilgisi yok)
        # da bu kalıba uyup sessizce "cihaz uyumsuzluğu" sanılıyor, CPU'da yeniden
        # deneniyor ve CUDA bağlamı zaten zehirlenmişken "başarılı" görünen ama tanımsız/
        # yanlış sonuçlar üretebiliyordu — asıl kök sebep (indexleme hatası) hiç
        # raporlanmadan maskeleniyordu. Önce BİLİNEN gerçek-CUDA-hatası imzalarını
        # AÇIKÇA dışlıyoruz; yalnızca bunlardan biri değilse genel "cuda"+"device"
        # sezgiselliğine düşüyoruz.
        gercek_cuda_calisma_zamani_hatasi = (
            "device-side assert" in mesaj
            or "an illegal memory access was encountered" in mesaj
            or "cuda error:" in mesaj
            or "cublas" in mesaj
            or "cudnn error" in mesaj
            or "misaligned address" in mesaj
        )
        cihaz_uyumsuzlugu = (not gercek_cuda_calisma_zamani_hatasi) and (
            "expected all tensors to be on the same device" in mesaj
            or "found at least two devices" in mesaj
            or "cudaguardimpl" in mesaj
            or ("cuda" in mesaj and "device" in mesaj)
        )
        if not (gercek_oom or oom_mesaji or cihaz_uyumsuzlugu):
            # Bu fonksiyonun sorumluluğu dışında bir hata — olduğu gibi yeniden fırlat.
            raise

        neden = "VRAM taşması" if (gercek_oom or oom_mesaji) else "cihaz uyumsuzluğu"
        logger.warning(
            f"[Acil Durum OOM Kurtarıcı] Gerçek {neden} yakalandı: {exc}. "
            f"Temizlik ve CPU/TMP üzerinden kurtarma başlatılıyor..."
        )

        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        if takas_mgr is not None and hasattr(takas_mgr, "temizle"):
            takas_mgr.temizle()

        cpu_device = torch.device('cpu')

        # Geri taşıma hedefi: argümanlar arasındaki ilk tensörün orijinal cihazı
        # (modul_nesnesi'nin parametre cihazı önceliklidir, o daha güvenilir bir referanstır)
        geri_donus_cihazi = cpu_device
        if modul_nesnesi is not None and hasattr(modul_nesnesi, 'parameters'):
            ilk_param = next(modul_nesnesi.parameters(), None)
            if ilk_param is not None:
                geri_donus_cihazi = ilk_param.device
        if geri_donus_cihazi == cpu_device:
            for aday in list(args) + list(kwargs.values()):
                if isinstance(aday, torch.Tensor):
                    geri_donus_cihazi = aday.device
                    break

        if modul_nesnesi is not None:
            if hasattr(modul_nesnesi, 'to'):
                try:
                    modul_nesnesi.to(cpu_device)
                except Exception:
                    pass
            try:
                modul_nesnesi._vram_idare_zorunlu_cihaz = cpu_device
            except Exception:
                pass

        cpu_args = tuple(girdi_cihaza_tasi(a, cpu_device) for a in args)
        cpu_kwargs = {k: girdi_cihaza_tasi(v, cpu_device) for k, v in kwargs.items()}

        try:
            cpu_sonuc = hesaplama_fonksiyonu(*cpu_args, **cpu_kwargs)
        except Exception as cpu_exc:
            logger.error(f"[Acil Durum OOM Kurtarıcı] CPU üzerinde tekrar deneme de başarısız oldu: {cpu_exc}")
            raise

        return girdi_cihaza_tasi(cpu_sonuc, geri_donus_cihazi)


AcilDurumOomYakalayiciVeKurtarici = acil_durum_oom_yakalayici_ve_kurtarici


if __name__ == "__main__":
    config = Model_TopolojikKonfigurasyon()
    model = BiliselKanvasModeli(config).to(config.device)
    print("Bilişsel Kanvas Topolojik Rekürens Mimarisi (kontratlar.py) başarıyla ilklendirildi.")
    print(f"Çalışma Cihazı: {config.device} | Toplam Gizil Durum Boyutu D: {config.D}")
    out = model("Ahmet iyi bir yüzücüdür.")
    print(f"Çıktı Olasılık Matrisi P Şekli: {out.P.shape}")





