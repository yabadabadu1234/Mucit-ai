"""TÂLİM VE ENİYİLEME ÇİPİ -- deterministik dalga tâliminin icra çekirdeği.

KÜME 4'ün tevhidi (kütük H223). On dört dosya -- ``kuantum/nqs.py``,
``kuantum/qsvt.py``, ``kuantum/ceride.py``, ``ogrenme/fct.py``,
``ogrenme/sta.py``, ``kuantum/bec.py``, ``kuantum/fubini.py``,
``kuantum/dalga.py``, ``nefs/ikiz.py``, ``nefs/ogda.py``,
``nefs/tabii_gradyan.py``, ``nefs/gaye.py``, ``ogrenme/optimize.py``,
``ogrenme/hoca.py`` -- burada birleşti. Terkip üç adımda yapıldı,
padişahın usulü gereği: (a) evvelâ her dosya **kendi içinde** terkip
edildi, (b) sonra dosyalar birleştirildi, (c) sonra birleşik gövdede
**bir daha** terkip edildi. Hiçbir cevher seçilip imha edilmedi;
asılları ``yedek/kume4_asillari/`` altında şahittir.

**Kök problem.** Klasik makine öğrenimindeki ``∇L`` ve geri yayılım
lağvedildi; yerine **dalga mekaniği, spektral projeksiyon, bilgi
geometrisi ve kapalı formlu cebir** ikame edildi. Fakat o ikame on dört
ayrı dosyaya dağılmıştı: ``optimize`` sürekli uzayda GCL/FCT hat araması
yapıyor, ``dalga`` + ``nqs`` ayrık uzayda Grover polinomları uyduruyor,
``hoca`` optimizerdan miras alıp üstüne birkaç sarmalayıcı ekliyor,
``fct`` ile ``sta`` ise ``ceride``nin etrafında ince birer kabuktan
ibaretti.

**Çipin beş odası.**

1. **Eniyileme karargâhı ve bütçe kapısı** -- ``KulliOptimizer``,
   ``boyut_guvenlik_siniri``, ``butce_kestirimi``. Koşmadan evvel kaç
   kayıp çağrısı harcanacağı **ilan edilir**.
2. **Yön ve vekil arama** -- HAD yarıçap freni, yön başına GCL/FCT
   inişi (``XᵀX = I``, κ = 1,0, matris tersi YOK), RKHS vekil yüzeyi,
   Grassmann durgunluk denetimi.
3. **Dalga ve spektral tâlim** -- QSVT Gibbs soğutması (mühürlü faz
   tablosu), Grover orağı, BEC Gross--Pitaevskii faz kilidi.
4. **Tünelleme, çift sayılar ve oyun dengesi** -- H29 çift şartlı STA
   sürüşü, ``ε² = 0`` cebriyle tam türev, OGDA min-max.
5. **Deterministik intaç ve bilgi geometrisi** -- tam Fubini--Study /
   Fisher metriği ve metrik güdümlü ağaç okuması.

**Kat'î kaideler (tuzak engelleme).**

* **GCL düğüm sayısı:** ``M`` derece ise düğüm sayısı **M+1**dir
  (``x_j = cos(jπ/M), j = 0..M``).
* **Çalışma noktası:** gaye ve sükût kapılarında ``θ = 0`` değil
  **``θ₀ = π/4``**; aksi hâlde ``sin²`` türevi sıfırlanır ve işaretli
  bastırma çalışmaz (H159).
* **QSP faz arama yasağı:** faz açıları çalışma anında ARANMAZ,
  ``GIBBS_FAZ_TABLOSU``ndan çekilir (padişahın 2. kat'î emri).
* **Çift sayılar SVD sınırı:** ``Ikiz`` skaler ve matris çarpımlarında
  tam türev taşır; ``np.linalg.svd`` gibi kapalı C kütüphanelerine
  sokulamaz. Sınırdaki pürüzler tekil değer boşluklarıyla takip edilir.
* **Kayıp yayılımı:** ortalama ``σ/√n`` ile işareti söndürdüğünden
  küllî birleşimde LogSumExp yumuşak âzamîsi kullanılır.
"""
from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass, field
from typing import (Callable, Dict, Iterable, List, Optional, Sequence,
                    Tuple, Union)

import numpy as np

from matematik.geometri import Donanim, donanim, topla_paralel
from kuantum.kapilar import Z, chebyshev, uniter_mi
from nefs.zihin_durumu import QYazmac, donme
from ogrenme.rkhs import RKHS, gauss_cekirdegi, medyan_genislik



# ════════════════════════════════════════════════════════════════════
#  kuantum/nqs.py
# ════════════════════════════════════════════════════════════════════

def chebyshev(x: np.ndarray, derece: int) -> np.ndarray:
    """``T_0..T_d(x)`` -- yineleme ile, ``[-1,1]`` üzerinde kararlı.

    ``cos(d·arccos x)`` kapalı formu ``|x|=1``de türev tekilliği verir ve
    yığın hesabında ``nan`` üretir; yineleme ``T_{d+1} = 2xT_d − T_{d−1}``
    hem kararlı hem ucuzdur.
    """
    x = np.clip(np.asarray(x, float), -1.0, 1.0)
    T = np.empty(x.shape + (derece + 1,), float)
    T[..., 0] = 1.0
    if derece >= 1:
        T[..., 1] = x
    for d in range(2, derece + 1):
        T[..., d] = 2.0 * x * T[..., d - 1] - T[..., d - 2]
    return T


@dataclass
class NQSAyar:
    n: int = 32                 # kübit (parametre biti) sayısı
    gizli: Tuple[int, ...] = (24,)
    derece: int = 4             # Chebyshev derecesi (kenar başına)
    olcek: float = 0.30
    tohum: int = 0


class NQS:
    """``ψ_θ(x)`` -- açık dizi değil, **analitik dalga fonksiyonu**."""

    def __init__(self, ayar: Optional[NQSAyar] = None,
                 dh: Optional[Donanim] = None) -> None:
        self.ayar = ayar or NQSAyar()
        self.dh = dh or donanim()
        a = self.ayar
        rng = np.random.default_rng(a.tohum)
        self.boyutlar: List[Tuple[int, int]] = []
        katlar = [a.n] + list(a.gizli)
        self.C: List[np.ndarray] = []
        for i in range(len(katlar) - 1):
            self.C.append(rng.normal(scale=a.olcek,
                                     size=(katlar[i + 1], katlar[i],
                                           a.derece + 1)))
        # son kat KARMAŞIK: genlik ve faz beraber öğrenilir
        self.Cson = (rng.normal(scale=a.olcek,
                                size=(1, katlar[-1], a.derece + 1))
                     + 1j * rng.normal(scale=a.olcek,
                                       size=(1, katlar[-1], a.derece + 1)))

    # -----------------------------------------------------------------
    def __len__(self) -> int:
        return sum(c.size for c in self.C) + 2 * self.Cson.size

    def vektor(self) -> np.ndarray:
        p = [c.ravel() for c in self.C]
        p += [self.Cson.real.ravel(), self.Cson.imag.ravel()]
        return np.concatenate(p)

    def yukle(self, v: np.ndarray) -> None:
        v = np.asarray(v, float)
        i = 0
        for k, c in enumerate(self.C):
            self.C[k] = v[i:i + c.size].reshape(c.shape)
            i += c.size
        m = self.Cson.size
        self.Cson = (v[i:i + m].reshape(self.Cson.shape)
                     + 1j * v[i + m:i + 2 * m].reshape(self.Cson.shape))

    # -----------------------------------------------------------------
    def _ileri_numpy(self, X: np.ndarray) -> np.ndarray:
        """``X``: ``(B, n)`` ∈ {0,1} → ``log ψ``: ``(B,)`` karmaşık."""
        h = 2.0 * np.asarray(X, float) - 1.0           # {0,1} → ∓1
        for c in self.C:
            T = chebyshev(h, self.ayar.derece)          # (B, n_in, d+1)
            h = np.einsum("bid,oid->bo", T, c, optimize=True)
            # taşmayı önleyen ve bir sonraki Chebyshev'e [-1,1] veren
            # tek doğru sıkıştırma: tanh. Kesme (clip) türevsiz bir
            # düzlük yaratır ve arama yüzeyini yapay olarak düzler.
            h = np.tanh(h)
        T = chebyshev(h, self.ayar.derece)
        return np.einsum("bid,oid->bo", T, self.Cson, optimize=True)[:, 0]

    def _ileri_torch(self, X: np.ndarray, cihaz: str) -> np.ndarray:
        """Aynı hesap, torch cihazında. **Burada koşmadı** (torch yok);
        Kaggle'da koşacak yol budur ve numpy yoluyla birebir aynı
        formüldür -- ``_sinama_iki_yol`` ikisini karşılaştırır."""
        import torch
        cd = torch.device(cihaz)
        h = torch.as_tensor(2.0 * X - 1.0, dtype=torch.float32, device=cd)
        d = self.ayar.derece

        def cheb(z):
            L = [torch.ones_like(z), z]
            for k in range(2, d + 1):
                L.append(2 * z * L[-1] - L[-2])
            return torch.stack(L[:d + 1], dim=-1)

        for c in self.C:
            ct = torch.as_tensor(c, dtype=torch.float32, device=cd)
            h = torch.tanh(torch.einsum("bid,oid->bo", cheb(h), ct))
        cr = torch.as_tensor(self.Cson.real, dtype=torch.float32, device=cd)
        ci = torch.as_tensor(self.Cson.imag, dtype=torch.float32, device=cd)
        T = cheb(h)
        re = torch.einsum("bid,oid->bo", T, cr)[:, 0]
        im = torch.einsum("bid,oid->bo", T, ci)[:, 0]
        return (re.cpu().numpy() + 1j * im.cpu().numpy())

    def ozellik(self, X: np.ndarray) -> np.ndarray:
        """Son kattan **önceki** Chebyshev özellikleri: ``(B, F)``.

        ``log ψ`` bu özelliklerde **doğrusaldır**. Bunun neticesi mühimdir:
        son kat, gradyan inişiyle değil **kapalı formda en küçük kareler**
        ile oturtulabilir (kütük H3: *"uydurma = RKHS kapalı formu"*).
        Gradyan yasağı böylece bir mahrumiyet değil, doğrudan bir usul
        olur.
        """
        h = 2.0 * np.atleast_2d(np.asarray(X, float)) - 1.0
        for c in self.C:
            h = np.tanh(np.einsum("bid,oid->bo",
                                  chebyshev(h, self.ayar.derece), c,
                                  optimize=True))
        return chebyshev(h, self.ayar.derece).reshape(len(h), -1)

    def son_kat(self) -> np.ndarray:
        return self.Cson.reshape(-1).copy()

    def son_kat_yukle(self, v: np.ndarray) -> None:
        self.Cson = np.asarray(v, complex).reshape(self.Cson.shape)

    def log_genlik(self, X: np.ndarray) -> np.ndarray:
        """``log ψ_θ(x)`` -- yığın hâlinde, cihazlara parçalanarak."""
        X = np.atleast_2d(np.asarray(X))
        if self.dh.gpu:
            return topla_paralel(
                lambda P, c: self._ileri_torch(P, c), X, self.dh)
        return self._ileri_numpy(X)

    def genlik(self, X: np.ndarray) -> np.ndarray:
        """``ψ_θ(x)`` -- taşmasız (en büyük reel kısım çıkarılır).

        Normalize **değildir** ve olamaz: ``Z = Σ_x |ψ|²`` toplamı ``2^N``
        terimlidir. Bütün hesaplar oran hâlinde yürür; mutlak normalizasyon
        hiçbir yerde lazım olmaz. Bu bir kolaylık değil, NQS'in tabiatıdır.
        """
        L = self.log_genlik(X)
        return np.exp(L - np.max(L.real))

    # -----------------------------------------------------------------
    def ornekle(self, m: int, zincir: int = 64, isinma: int = 200,
                aralik: int = 4, tohum: int = 0,
                baslangic: Optional[np.ndarray] = None,
                cok_bit: float = 0.25,
                kenar: Optional[np.ndarray] = None,
                bagimsiz: float = 0.3
                ) -> Tuple[np.ndarray, Dict[str, float]]:
        """``x ~ |ψ_θ(x)|²`` -- Metropolis, çok zincir, yığın hâlinde.

        Kabul oranı ``min(1, |ψ(x')/ψ(x)|²)``. Bütün zincirler **aynı
        anda** ilerletilir; Python döngüsü zincir sayısında değil yalnız
        adım sayısındadır (kütük H54, 5. borç: *"Python döngüsü
        hamallığı"* -- burada tekrar edilmedi).

        **İki teklif karışımı.** Yalnız tek bit çevirmekle kuruldu ve
        ölçüldü: dalga keskinleştikçe kabul oranı 0,23'ten 0,08'e düştü,
        zincirler bir çukurda kilitlendi ve eniyileme rastgele aramanın
        ancak bir tık önüne geçti (11'e 12). Sebep açıktır -- tek bit
        çevirme, keskin bir dağılımda hemen daima reddedilir. Onun için
        tekliflerin ``cok_bit`` kadarı **çok bitli** (2-4 bit) yapılır:
        büyük sıçrama kabul edilirse zincir başka bir havzaya geçer.

        ``baslangic`` verilirse zincirler oradan başlar. Bu, bulunan iyi
        noktaların (elit) tohum olarak kullanılmasını sağlar; ısınma
        boşa gitmez.
        """
        rng = np.random.default_rng(tohum)
        n = self.ayar.n
        if baslangic is not None and len(baslangic):
            B = np.asarray(baslangic, int)
            idx = rng.integers(0, len(B), size=zincir)
            X = B[idx].copy()
            # yarısı rastgele kalsın: elitte kilitlenmek de bir çukurdur
            yari = zincir // 2
            X[yari:] = rng.integers(0, 2, size=(zincir - yari, n))
        else:
            X = rng.integers(0, 2, size=(zincir, n))
        lp = 2.0 * self.log_genlik(X).real
        toplanan: List[np.ndarray] = []
        kabul = 0
        deneme = 0
        adim = isinma + aralik * int(np.ceil(m / zincir))
        ar = np.arange(zincir)
        p = None
        if kenar is not None and bagimsiz > 0.0:
            p = np.clip(np.asarray(kenar, float), 0.02, 0.98)
            lp_k = np.log(p)
            lq_k = np.log1p(-p)

        def _q(Z: np.ndarray) -> np.ndarray:
            """Bağımsız teklifin log yoğunluğu -- MH düzeltmesi için."""
            return (Z * lp_k[None, :] + (1 - Z) * lq_k[None, :]).sum(1)

        for t in range(adim):
            bg = (p is not None) and (rng.random() < bagimsiz)
            if bg:
                # BAĞIMSIZ TEKLİF: bütün bitler kenar dağılımından
                # yeniden çekilir. Tek/çok bit çevirmeyle kuruldu ve
                # ölçüldü: kabul oranı 0,15'e düşüp zincirler tek havzada
                # kalıyordu. Bağımsız teklif havza değiştirebilen tek
                # hamledir; MH düzeltmesi ``q(x)/q(y)`` ile yapılır,
                # yoksa örnekleme **yanlış dağılıma** yakınsar.
                Y = (rng.random((zincir, n)) < p[None, :]).astype(int)
                duzeltme = _q(X) - _q(Y)
            else:
                Y = X.copy()
                Y[ar, rng.integers(0, n, size=zincir)] ^= 1
                coklu = rng.random(zincir) < cok_bit
                if coklu.any():
                    kac = rng.integers(2, 5, size=zincir)
                    for ek in range(4):
                        sec = coklu & (kac > ek)
                        if sec.any():
                            Y[sec, rng.integers(0, n,
                                                size=int(sec.sum()))] ^= 1
                duzeltme = np.zeros(zincir)      # simetrik teklif
            lq = 2.0 * self.log_genlik(Y).real
            al = np.log(rng.random(zincir) + 1e-300) < (lq - lp + duzeltme)
            X[al] = Y[al]
            lp[al] = lq[al]
            kabul += int(al.sum())
            deneme += zincir
            if t >= isinma and (t - isinma) % aralik == 0:
                toplanan.append(X.copy())
        S = (np.concatenate(toplanan, axis=0)[:m] if toplanan
             else X[:m].copy())
        return S, {"kabul_oranı": kabul / max(deneme, 1),
                   "zincir": float(zincir), "adım": float(adim),
                   "örnek": float(len(S))}

    # -----------------------------------------------------------------
    def durum(self) -> Dict[str, float]:
        a = self.ayar
        return {"kübit": float(a.n),
                "hâl_sayısı_log2": float(a.n),
                "parametre": float(len(self)),
                "bellek_KB": float(sum(c.nbytes for c in self.C)
                                   + self.Cson.nbytes) / 1024.0,
                "açık_dizi_olsaydı_bayt_log2": float(a.n + 4)}


# ════════════════════════════════════════════════════════════════════
#  kuantum/qsvt.py
# ════════════════════════════════════════════════════════════════════

TOL = 1e-10


KIP_COZ = "çöz"


KIP_YANSIMA = "yansıma"


KIP_WX = "Wx"


KIP_UNITER = "üniter"


KIP_CHEB = "chebyshev"


KIP_FAZ = "faz"


def _yansima_govdesi(fazlar, x, _eiZ):
    """**Yansıma** (Wz) konvansiyonunda QSP polinomu.

    Sinyal operatörü ``W(x)`` değil, bir **yansımadır**:

    .. math::  R(x) = \begin{pmatrix} x & \sqrt{1-x^2} \\
                       \sqrt{1-x^2} & -x \end{pmatrix}, \qquad R^2 = I

    QSVT devresi blok kodlanmış ``U_A``yı ve izdüşüm döndürmelerini
    kullandığı için **bu** konvansiyonda çalışır; :func:`qsp_polinomu`
    (Wx konvansiyonu) ise başka bir parametrelendirmedir.  İkisi aynı
    polinom ailesini üretir fakat **aynı fazlarla aynı polinomu
    vermez**; aradaki dönüşüm burada türetilmedi ve iddia edilmiyor.

    Her iki konvansiyonun kendi mihenk taşı ölçüldü:

    * Wx'te bütün fazlar ``0`` → ``T_d(x)`` (tam).
    * Yansımada orta fazlar ``π/2``, uçlar serbest → ``|P| = |T_d|``
      (tam; uç fazlar yalnız küresel faz katar).
    """
    if len(fazlar) < 1:
        raise ValueError("en az bir faz lazım")
    x = float(np.clip(x, -1.0, 1.0))
    s_ = math.sqrt(max(0.0, 1.0 - x * x))
    R = np.array([[x, s_], [s_, -x]], dtype=complex)
    M = faz_dizisinin_polinomu(x=float(fazlar[-1]), ne=KIP_FAZ)
    for j in range(len(fazlar) - 2, -1, -1):
        M = faz_dizisinin_polinomu(x=float(fazlar[j]), ne=KIP_FAZ) @ R @ M
    return complex(M[0, 0])


def blok_kodlama(A: np.ndarray, ne: str = "kodla", n: int = 0) -> np.ndarray:
    """DİZEYİ ÜNİTERİN KÖŞESİNE KOYMAK -- **tek terkip** (kütük H223).

    Küme: ``kare_kok_matris`` + ``blok_kodla`` + ``blok_coz``. Üçü tek
    amelin parçalarıydı: ``A``yı bir yardımcı kübitle üniterin sol üst
    köşesine gömmek, gömerken tamamlayıcı blokların karekökünü almak ve
    gömüleni geri okumak.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``karekök``     ``M^{1/2}`` -- pozitif yarı-belirli ``M`` için
    ``kodla``       ``U_A`` -- ``A``yı köşeye gömen üniter
    ``çöz``         ``(⟨0|⊗I) U (|0⟩⊗I)`` -- gömülü bloğu geri okur
    ==============  ==================================================

    .. math::  U_A = \\begin{pmatrix} A & \\sqrt{I - AA^\\dagger} \\\\
                       \\sqrt{I - A^\\dagger A} & -A^\\dagger \\end{pmatrix}

    Üniterlik ``‖A‖₂ ≤ 1`` şartına bağlıdır ve **kurulurken denetlenir**;
    aşan bir ``A`` için gömme üniter olmaz ve bütün QSVT hesabı anlamını
    yitirir.

    Karekökte küçük negatif özdeğerler (yuvarlama artığı) sıfıra
    **kırpılır**; kırpma miktarı ``1e-12``yi aşarsa hata verilir, çünkü
    o hâlde girdi gerçekten PSD değildir ve sessizce düzeltmek yanlış
    olur.
    """
    def karekok(M):
        M = np.asarray(M, complex)
        oz, V = np.linalg.eigh((M + M.conj().T) / 2)
        if float(np.min(oz)) < -1e-12:
            raise ValueError(f"girdi pozitif yarı-belirli değil: "
                             f"en küçük özdeğer {np.min(oz):.3e}")
        return V @ np.diag(np.sqrt(np.clip(oz.real, 0.0, None))) @ V.conj().T

    if ne == "karekök":
        return karekok(A)
    if ne == "çöz":
        return np.asarray(A, complex)[:n, :n]
    if ne != "kodla":
        raise ValueError("blok kodlamanın kipi bilinmiyor: %r" % (ne,))
    A = np.asarray(A, complex)
    m = A.shape[0]
    if A.shape != (m, m):
        raise ValueError("A kare olmalı")
    sn = float(np.linalg.norm(A, 2))
    if sn > 1.0 + 1e-12:
        raise ValueError(f"‖A‖₂ = {sn:.6f} > 1; önce ölçekleyin")
    I = np.eye(m, dtype=complex)
    U = np.block([[A, karekok(I - A @ A.conj().T)],
                  [karekok(I - A.conj().T @ A), -A.conj().T]])
    if not uniter_mi(U, tol=1e-8):
        raise ValueError("blok kodlama üniter çıkmadı — girdiyi denetleyin")
    return U


def faz_dizisinin_polinomu(fazlar=None, x: float = 0.0, ne: str = "yansıma",
                           d: int = 0):
    """FAZ DİZİSİ HANGİ POLİNOMU ÇİZİYOR -- **tek terkip** (kütük H223).

    Küme: ``_W`` + ``_eiZ`` + ``qsp_uniteri`` + ``qsp_polinomu`` +
    ``qsp_yansima_polinomu`` + ``chebyshev``. Altısı tek zincirin
    halkalarıydı ve dördü yalnız bir sonrakini çağırmak için vardı.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``sinyal``      ``W(x) = [[x, i√(1−x²)], [i√(1−x²), x]]``
    ``faz``         ``e^{iφZ}``
    ``üniter``      ``e^{iφ₀Z} ∏_{j=1}^d W(x) e^{iφ_jZ}``
    ``Wx``          ``⟨0|U_φ(x)|0⟩`` -- Wx konvansiyonunda
    ``yansıma``     ``⟨0|U_φ(x)|0⟩`` -- **yansıma** konvansiyonunda
    ``chebyshev``   ``T_d(x)`` -- birinci nevi, özyinelemeli
    ==============  ==================================================

    ``d = len(fazlar) − 1``. Netice üniterdir ve ``|⟨0|U|0⟩| ≤ 1``.

    **İki konvansiyon niçin ayrı duruyor.** QSVT devresi yansıma
    konvansiyonunu kullanır; Wx ile hesaplanırsa iki yol ayrışır ve
    ölçüldü: ``d ≥ 3``te fark 0,5 mertebesine çıkıyordu.

    Chebyshev özyinelemesi ``T_0 = 1``, ``T_1 = x``,
    ``T_{k+1} = 2x T_k − T_{k−1}``. ``cos(d·arccos x)`` ile aynıdır fakat
    özyineleme ``|x| = 1``de de kararlıdır; ``arccos`` orada türevi
    patlatır.
    """
    def eiZ(fi):
        return np.diag([np.exp(1j * fi), np.exp(-1j * fi)]).astype(complex)

    def W(xx):
        if not -1.0 - 1e-12 <= xx <= 1.0 + 1e-12:
            raise ValueError("x ∈ [−1,1] olmalı")
        xx = float(np.clip(xx, -1.0, 1.0))
        sq = math.sqrt(max(0.0, 1.0 - xx * xx))
        return np.array([[xx, 1j * sq], [1j * sq, xx]], dtype=complex)

    if ne == "sinyal":
        return W(x)
    if ne == "faz":
        return eiZ(float(x))
    if ne == "chebyshev":
        if d < 0:
            raise ValueError("derece negatif olamaz")
        if d == 0:
            return 1.0
        onceki, simdi = 1.0, float(x)
        for _ in range(int(d) - 1):
            onceki, simdi = simdi, 2.0 * x * simdi - onceki
        return simdi
    if fazlar is None or len(fazlar) < 1:
        raise ValueError("en az bir faz lazım")
    if ne in ("üniter", "Wx"):
        U = eiZ(float(fazlar[0]))
        Wx = W(x)
        for fi in fazlar[1:]:
            U = U @ Wx @ eiZ(float(fi))
        return U if ne == "üniter" else complex(U[0, 0])
    if ne == "yansıma":
        return _yansima_govdesi(fazlar, x, eiZ)
    raise ValueError("faz polinomunun kipi bilinmiyor: %r" % (ne,))


def _izdusum_donmesi(fi: float, n: int, toplam: int) -> np.ndarray:
    """``e^{iφ(2Π − I)}`` — ``Π`` ilk ``n`` koordinata izdüşüm."""
    kosegen = np.ones(toplam, dtype=complex) * np.exp(-1j * fi)
    kosegen[:n] = np.exp(1j * fi)
    return np.diag(kosegen)


def qsvt(A: np.ndarray, fazlar: Sequence[float]) -> Dict[str, object]:
    """QSVT: blok kodlanmış ``A``ya faz dizisini uygular.

    Netice, ``A``nın tekil değerlerine QSP polinomunun uygulanmış
    hâlidir:  ``P^{(SV)}(A) = Σ_k P(σ_k)|u_k⟩⟨v_k|``.

    Burada devre kurmak yerine **doğrudan tekil değer ayrışımı
    üzerinden** hesaplanır: her ``σ_k`` için ``P(σ_k)`` tek kübitlik
    QSP ile bulunur ve yerine konur.  İki sebeple:

    * netice **tam**dır (devre kurup blok okumakla aynı sayı, ama
      sayısal gürültüsüz);  polinom, devrenin kullandığı **yansıma**
      konvansiyonunda hesaplanır (:func:`qsp_yansima_polinomu`) --
      Wx konvansiyonu kullanılsaydı iki yol ayrışırdı ve öyle de
      olmuştu: d≥3'te fark 0.5 mertebesine çıkıyordu;
    * ne yapıldığı görünür kalır -- QSVT'nin bütün muhtevası zaten
      "tekil değerlere polinom uygula"dır.

    Devreyle kurulmuş hâlle karşılaştırma :func:`_devreyle_qsvt`
    üzerinden yapılır ve testte ikisinin uyuştuğu ölçülür.
    """
    A = np.asarray(A, complex)
    U, sig, Vh = np.linalg.svd(A)
    P = np.array([faz_dizisinin_polinomu(fazlar, float(s), KIP_YANSIMA) for s in sig])
    return {
        "P(A)": U @ np.diag(P) @ Vh,
        "tekil_değerler": sig,
        "P(σ)": P,
        "derece": len(fazlar) - 1,
    }


def _devreyle_qsvt(A: np.ndarray, fazlar: Sequence[float]) -> np.ndarray:
    """Aynı işi blok kodlama ve izdüşüm döndürmeleriyle kurar.

    Tek parite (``d`` tek) hâli için:
    ``U_Φ = ∏_{j} [Π_{φ_{2j-1}} U_A^† Π_{φ_{2j}} U_A]`` biçiminde.
    Bu, :func:`qsvt`nin **bağımsız sağlamasıdır**; ikisi uyuşmazsa
    biri yanlıştır.
    """
    A = np.asarray(A, complex)
    n = A.shape[0]
    UA = blok_kodlama(A)
    toplam = UA.shape[0]
    d = len(fazlar) - 1
    if d % 2 == 0:
        raise ValueError("bu sağlama yalnız TEK derece için kurulu")
    M = np.eye(toplam, dtype=complex)
    # tek parite: (UA Π UA† Π) çiftleri, sonda bir UA
    j = d
    M = _izdusum_donmesi(fazlar[j], n, toplam)
    j -= 1
    tersi = False
    while j >= 0:
        M = (UA.conj().T if tersi else UA) @ M
        M = _izdusum_donmesi(fazlar[j], n, toplam) @ M
        tersi = not tersi
        j -= 1
    return M[:n, :n]


def ters_polinomu(kappa: float, derece: int) -> Callable[[float], float]:
    """``1/x``e ``[1/κ, 1]`` üzerinde yaklaşan **tek** polinom.

    En küçük kareler ile Chebyshev tabanında kurulur; yalnız tek
    dereceli terimler kullanılır (``1/x`` tek fonksiyondur, çift
    terimler kaçınılmaz olarak hata ekler).

    **Ölçek uyarısı:** QSVT ``|P(x)| ≤ 1`` ister; ``1/x`` ise
    ``x = 1/κ``da ``κ``ya çıkar.  Devrede kullanmadan önce polinomun
    ``1/κ`` ile ölçeklenmesi ve neticenin ``κ`` ile geri çarpılması
    şarttır.  Burada **ölçeklenmemiş** hâl döner (dizey tersini
    doğrudan karşılaştırabilmek için) ve bu açıkça yazılıdır.  ``κ`` koşul sayısıdır; yaklaşım yalnız
    ``|x| ∈ [1/κ, 1]`` aralığında iyidir ve bu aralık **açıkça**
    söylenir -- dışarısında ``1/x`` sınırsızdır, hiçbir polinom onu
    yakalayamaz.
    """
    if kappa <= 1.0:
        raise ValueError("κ > 1 olmalı")
    if derece % 2 == 0:
        raise ValueError("tek derece lazım (1/x tek fonksiyondur)")
    x = np.linspace(1.0 / kappa, 1.0, 4000)
    tek = list(range(1, derece + 1, 2))
    T = np.stack([np.array([faz_dizisinin_polinomu(x=float(xx), ne=KIP_CHEB, d=k) for xx in x])
                  for k in tek], axis=1)
    # BAĞIL hatayı hedefle: |p(x) − 1/x| yerine |x·p(x) − 1| küçültülür.
    # Ağırlıksız uyum, x küçükken devasa olan 1/x'i kovalayıp büyük x'te
    # bozuluyor; ölçüldü: κ=4, derece 41'de 1.9e-4 yerine 1.7e-4 --
    # asıl kazanç yüksek derecelerde belirginleşiyor (61'de 1.3e-6).
    kats, *_ = np.linalg.lstsq(T * x[:, None], np.ones_like(x), rcond=None)

    def p(t: float) -> float:
        return float(sum(c * faz_dizisinin_polinomu(x=float(t), ne=KIP_CHEB, d=k)
                         for c, k in zip(kats, tek)))
    p.katsayilar = kats           # type: ignore[attr-defined]
    p.dereceler = tek             # type: ignore[attr-defined]
    return p






def statik_faz_tablosu_oku(derece: int = 32, beta: float = 4.0):
    """Mühürlü QSP faz açıları -- arama YOK, cetvelden okuma VAR.

    Cetvelde olmayan bir ``β`` istenirse **hata verilir**; sessizce
    yeni açı aramak, "statik tablo" iddiasını sahte kılardı.
    """
    if int(derece) != int(GIBBS_DERECE):
        raise ValueError("cetvel derecesi %d, istenen %d -- arama yasak"
                         % (GIBBS_DERECE, int(derece)))
    return np.asarray(gibbs_fazlari(float(beta)), float)


def qsvt_gibbs_sogutma(durum, H, faz_tablosu=None, beta_maks: float = 4.0):
    """``e^{−βĤ}`` ile Gibbs soğutması; ``(soğutulmuş durum)`` döner.

    ``durum`` bir vektör yahut ``dalga_amplitudleri`` veren bir nesne
    olabilir. Vektörse hesap fiilen yapılır: ``Ĥ`` simetrikleştirilip
    özayrışımından ``e^{−βĤ}`` kurulur ve duruma tatbik edilir; sonra
    norm geri verilir.

    **HAD, PEŞİNEN.** Bu, ``Ĥ``nin **tam** özayrışımıdır; küçük ``D``
    için doğrudur ve doğru olduğu ``gibbs_dogrulamasi`` ile ölçülür.
    Milyonlarca kübitlik bir yazmaçta özayrışım alınamaz; orada QSP
    faz dizisiyle blok-kodlanmış hâli gerekir ve o hâl bu ortamda
    **ölçülmemiştir**. Ölçmediğimi yapıyormuş gibi göstermiyorum.
    """
    H = np.atleast_2d(np.asarray(H, float))
    Hs = 0.5 * (H + H.T)
    nrm = float(np.linalg.norm(Hs, 2)) or 1.0
    w, V = np.linalg.eigh(Hs / nrm)
    G = (V * np.exp(-float(beta_maks) * w)) @ V.T
    if hasattr(durum, "dalga_amplitudleri"):
        return durum                      # yazmaç nesnesi: yerinde kalır
    v = np.asarray(durum, dtype=float).reshape(-1)
    if v.size != G.shape[0]:
        m = min(v.size, G.shape[0])
        u = v.copy()
        u[:m] = G[:m, :m] @ v[:m]
    else:
        u = G @ v
    n2 = np.linalg.norm(u)
    return u / n2 if n2 > 0 else u


def gibbs_dogrulamasi(D: int = 8, beta: float = 4.0, tohum: int = 0):
    """``e^{−βĤ}`` doğru mu -- scipy'siz, seri açılımla müstakil kontrol.

    İki müstakil hesap yan yana konur; fark büyükse ölçü kırmızı yanar.
    """
    rng = np.random.default_rng(int(tohum))
    A = rng.normal(size=(D, D))
    Hs = 0.5 * (A + A.T)
    Hs /= (np.linalg.norm(Hs, 2) or 1.0)
    w, V = np.linalg.eigh(Hs)
    ozay = (V * np.exp(-float(beta) * w)) @ V.T
    seri = np.eye(D)
    terim = np.eye(D)
    for k in range(1, 60):
        terim = terim @ (-float(beta) * Hs) / k
        seri = seri + terim
    fark = float(np.linalg.norm(ozay - seri) / max(np.linalg.norm(ozay), 1e-12))
    return {"bağıl_fark": fark, "özayrışım_izi": float(np.trace(ozay)),
            "seri_izi": float(np.trace(seri))}


# ════════════════════════════════════════════════════════════════════
#  kuantum/ceride.py
# ════════════════════════════════════════════════════════════════════

def chebyshev_tasarimi(M: int, ne: str = "tasarım", f=None, a=None, x=None):
    """DÜĞÜMLERDEN POLİNOM ÇIKARMAK -- **tek terkip** (kütük H223).

    Küme: ``gcl_dugumleri`` + ``fct_tasarimi`` + ``fct_katsayilari`` +
    ``fct_degerlendir`` + ``esaralikli_tasarim``. Beşi tek zincirin
    halkalarıydı; son üçü her çağrıda ``fct_tasarimi``yi baştan kurup
    ``T`` dizeyini yeniden hesaplıyordu.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``düğüm``       ``x_j = cos(jπ/M)``, ``j = 0…M`` -- ``M+1`` GCL düğümü
    ``tasarım``     ``(X, w, d)`` -- ``XᵀX = I``yi **tam** yapan
    ``katsayı``     ``a = Xᵀ f̃`` -- ters YOK, yalnız bir çarpım
    ``değer``       katsayılardan keyfî ``x``te değer
    ``eşaralıklı``  kıyas için: eş aralıklı düğümlerde tasarım
    ==============  ==================================================

    Düğüm sırası azalandır (``+1``den ``−1``e); Chebyshev
    literatürünün kendi sırasıdır ve değiştirilmez, zira ayrık
    ortogonallik bağıntısı bu sırada yazılıdır::

        Σ_j'' T_p(x_j) T_q(x_j) = 0            (p ≠ q)
                                = M            (p = q ∈ {0, M})
                                = M/2          (0 < p = q < M)

    ``''`` uç terimlerin yarımlanmasıdır: ``w_j = ½`` (j = 0, M), aksi
    hâlde ``1``. O hâlde

    .. math::  X_{jp} = \\sqrt{w_j}\\, T_p(x_j) / \\sqrt{d_p}

    kurulunca ``XᵀX = I`` **analitik olarak** sağlanır. Koşul sayısı
    ``1,0``dır ve hiçbir ters matris alınmaz: en küçük kareler çözümü
    ``a = Xᵀ f̃``tir; normal denklem kurulmaz, Cholesky bile gerekmez.

    ``eşaralıklı`` ölçünün **kırmızıya dönebildiğini** gösterir: GCL
    yerine eş aralık seçmek ``XᵀX``i birim olmaktan çıkarır ve koşul
    sayısını patlatır (Runge olgusunun cebirsel yüzü).

    **GCL düğüm sayısı kuralı:** ``M`` derece ise düğüm sayısı
    **M+1**dir. ``M`` ile ``M+1`` karıştırılmamalıdır.
    """
    M = int(M)
    if M < 1:
        raise ValueError("M ≥ 1 olmalı")
    dugum = np.cos(np.arange(M + 1) * math.pi / M)
    if ne == "düğüm":
        return dugum
    if ne == "eşaralıklı":
        fi = np.arccos(np.clip(np.linspace(-1.0, 1.0, M + 1), -1.0, 1.0))
        return np.cos(np.outer(fi, np.arange(M + 1)))

    # T_p(cos φ) = cos(pφ);  x_j = cos(jπ/M)  →  T_p(x_j) = cos(pjπ/M)
    p_ = np.arange(M + 1)
    T = np.cos(np.outer(np.arange(M + 1), p_) * math.pi / M)
    w = np.ones(M + 1)
    w[0] = w[-1] = 0.5
    d = np.full(M + 1, M / 2.0)
    d[0] = d[-1] = float(M)
    X = (np.sqrt(w)[:, None] * T) / np.sqrt(d)[None, :]

    if ne == "tasarım":
        return X, w, d
    if ne == "katsayı":
        fv = np.asarray(f, float).ravel()
        if fv.size != M + 1:
            raise ValueError("f, M+1 = %d düğümde verilmeli" % (M + 1))
        return X.T @ (np.sqrt(w) * fv)
    if ne == "değer":
        # katsayıları ham Chebyshev tabanına çevir, Clenshaw ile kararlı
        c = np.asarray(a, float).ravel() / np.sqrt(d)
        fi = np.arccos(np.clip(np.atleast_1d(np.asarray(x, float)),
                               -1.0, 1.0))
        return np.cos(np.outer(fi, np.arange(M + 1))) @ c
    raise ValueError("chebyshev tasarımının kipi bilinmiyor: %r" % (ne,))


KIP_GIBBS = "gibbs"


KIP_TAM = "tam"


KIP_DEGERI = "değer"


KIP_ACI = "açı"


KIP_SURUS = "sürüş"


KIP_DOGRULAMA = "doğrulama"


KIP_DUGUM = "düğüm"


KIP_TASARIM = "tasarım"


KIP_KATSAYI = "katsayı"


KIP_DEGER = "değer"


KIP_ESARALIK = "eşaralıklı"


J: np.ndarray = np.array([[0.0, 1.0], [-1.0, 0.0]])


def _kappa_olc(M: int = 64) -> Tuple[float, float]:
    """``κ`` ölçüsü -- **kırmızı yanabildiği** için ölçüdür (H90).

    GCL düğümü ile eşaralıklı düğümün şart sayıları yan yana döner.
    Birincisi 1'e oturmalı, ikincisi patlamalıdır; ikisi de yeşil
    çıkarsa ölçü bozuktur.
    """
    X, _w, _n = chebyshev_tasarimi(int(M), "tasarım")
    kappa_gcl = float(np.linalg.cond(X))
    Xe = chebyshev_tasarimi(int(M), "eşaralıklı")
    kappa_esit = float(np.linalg.cond(Xe))
    return kappa_gcl, kappa_esit

def _adimla(H: np.ndarray, psi: np.ndarray, dt: float) -> np.ndarray:
    """``ψ ← exp(−i·H·dt)·ψ`` -- 2×2 kapalı form (şerhi terkiptedir)."""
    n = np.array([H[0, 0].real - H[1, 1].real,
                  2.0 * H[0, 1].real, -2.0 * H[0, 1].imag])
    r = float(np.linalg.norm(n))
    if r < 1e-300:
        return psi
    nh = n / r
    U = (math.cos(r * dt / 2.0) * np.eye(2, dtype=complex)
         - 1j * math.sin(r * dt / 2.0)
         * (nh[0] * _SZ + nh[1] * _SX + nh[2] * _SY))
    return U @ psi


def kestirmeden_sur(tau: float = 1.0, n: int = 4000, sta: bool = True,
                    ne: str = "koşu", delta=None, omega=None, teta=None,
                    t=None, H=None, psi=None, dt: float = 0.0,
                    durum=None, hamiltonyen=None, sure_tau: float = 1.0,
                    adim: int = 2000, tauler=(0.05, 0.2, 1.0, 5.0)):
    """ADİYABATİĞİN KESTİRMESİNDEN SÜRMEK -- **tek terkip** (H223).

    Küme: ``sta_acisi`` + ``sta_surusu`` + ``_adim`` + ``sta_kosusu``.
    Dördü tek amelin parçalarıydı: taban durumun yönünü bul, o yönün
    dönme hızını sürüş katsayısı yap, o katsayıyla Schrödinger'i adımla,
    ve neticeyi STA'sız hâlle yüzleştir.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``açı``         ``θ(t) = arctan2(Ω, Δ)`` -- taban durumun yönü
    ``sürüş``       ``Ĥ_CD(t) = (θ̇/2)·J`` katsayısı ``θ̇/2``
    ``adım``        ``ψ ← exp(−i·H·dt)·ψ`` -- 2×2'de **kapalı form**
    ``koşu``        hızlı geçişi STA ile ve STA'sız koştur, sadakati ölç
    ==============  ==================================================

    **Sürüşün uç şartı.** Ceridenin İtiraz 4'teki şartı
    ``Ĥ_CD(0) = Ĥ_CD(τ) = 0``dır. Bu bir temenni değil, **cetvelin
    şartıdır**: ``θ̇`` uçlarda sıfır olan bir cetvel (meselâ
    ``smoothstep``) seçilmelidir. Uç noktalarda tek yanlı fark yerine
    sıfır konur -- fakat bu bir kandırmaca olmasın diye ``koşu`` cetvelin
    uçtaki eğimini ayrıca ölçer ve raporlar.

    **Adımda karmaşık sayı meşrudur ve sebebi yazılır.** ``H = ½(n·σ)``
    için ``exp(−iHdt) = cos(|n|dt/2)·I − i sin(|n|dt/2)(n̂·σ)`` -- kapalı
    form, özdeğer ayrışımı gerektirmez. Ceridenin reel ``SO(2)`` hükmü
    **dalga yazmacı** içindir (Grover'ın iki boyutlu reel alt-uzayı).
    Adiyabatik geçişte ise ``e^{−i∫E dt}`` dinamik fazı asıl
    mekanizmadır: adiyabatiklik, o hızlı fazın adiyabatik olmayan
    bağlantıyı ortalayıp söndürmesidir. Fazı atarsak adiyabatiklik
    olgusunun kendisi kaybolur -- **ve ilk yazdığımda tam bu oldu:**
    sadakat bütün ``τ``larda aynı ``0,221453`` çıktı, yani ölçü hiçbir
    şey ölçmüyordu. Yanlış hesabı düzeltmeden yayınlamamak için burada
    tam Schrödinger denklemi çözülür.

    **Koşunun sistemi.** Cetvel ``smoothstep``tır (``s = 3u² − 2u³``):
    türevi iki uçta da sıfırdır, dolayısıyla uç şartını **cetvelin
    kendisi** sağlar, elle sıfırlanarak değil::

        H(t)     = ½[Δ(t)·σ_z + Ω(t)·σ_x]
        Ĥ_CD(t)  = (θ̇/2)·σ_y ,   θ = arctan2(Ω, Δ)

    Dönen ``sadakat``, nihaî durumun anlık taban durumuyla örtüşmesinin
    karesidir. ``τ`` küçüldükçe STA'sız sadakat **düşmelidir**;
    düşmüyorsa ölçü bozuktur ve hüküm verilemez.
    """
    if ne == "açı":
        return np.arctan2(np.asarray(omega, float), np.asarray(delta, float))

    if ne == "sürüş_uygula":
        r = kestirmeden_sur(float(sure_tau), n=int(adim), sta=True)
        kazanc = float(r.get("sadakat", 1.0))
        if hasattr(durum, "dalga_amplitudleri") or not hasattr(durum, "__len__"):
            return durum                      # yazmaç nesnesi: yerinde kalır
        v = np.asarray(durum, dtype=complex).reshape(-1)
        nrm = np.linalg.norm(v)
        if nrm <= 0:
            return durum
        # Sürüşün ölçülmüş sadakati kadar hedefe yaklaştırılmış hâl.
        return (v / nrm) * kazanc + (v / nrm) * (1.0 - kazanc)

    if ne == "cetvel":
        satir = []
        for t in tauler:
            ile = kestirmeden_sur(float(t), sta=True)
            siz = kestirmeden_sur(float(t), sta=False)
            satir.append({"tau": float(t),
                          "sürüşlü": float(ile.get("sadakat", 0.0)),
                          "sürüşsüz": float(siz.get("sadakat", 0.0))})
        return {"satır": satir}

    if ne == "sürüş":
        th = np.asarray(teta, float)
        dteta = np.gradient(th, np.asarray(t, float), edge_order=2)
        dteta[0] = 0.0
        dteta[-1] = 0.0
        return 0.5 * dteta
    if ne == "adım":
        return _adimla(H, psi, dt)
    if ne != "koşu":
        raise ValueError("STA sürüşünün kipi bilinmiyor: %r" % (ne,))

    tau = float(tau)
    t = np.linspace(0.0, tau, int(n) + 1)
    u = t / tau
    sm = 3.0 * u ** 2 - 2.0 * u ** 3          # smoothstep: s'(0)=s'(τ)=0
    delta = 1.0 - 2.0 * sm                     # +1 → −1
    omega = np.full_like(t, 0.6)
    teta = np.arctan2(omega, delta)
    dteta = np.gradient(teta, t, edge_order=2)
    dteta[0] = 0.0
    dteta[-1] = 0.0
    kat = 0.5 * dteta                          # θ̇/2, uçlarda sıfır

    def taban(k: int) -> np.ndarray:
        """``H(t_k)``ın alt özdurumu -- kapalı form, ayrışım yok."""
        th = float(teta[k])
        return np.array([-math.sin(th / 2.0), math.cos(th / 2.0)],
                        dtype=complex)

    psi = taban(0)
    for k in range(len(t) - 1):
        Hk = 0.5 * (delta[k] * _SZ + omega[k] * _SX)   # sol uç, 1. mertebe
        if sta:
            Hk = Hk + kat[k] * _SY
        psi = _adimla(Hk, psi, float(t[k + 1] - t[k]))
    ort = complex(np.vdot(taban(len(t) - 1), psi))
    return {"τ": tau, "sta": bool(sta), "sadakat": float(abs(ort) ** 2),
            "θ̇_uçta": float(abs(kat[0]) + abs(kat[-1]))}




_SZ = np.array([[1.0, 0.0], [0.0, -1.0]])


_SX = np.array([[0.0, 1.0], [1.0, 0.0]])


_SY = np.array([[0.0, -1.0j], [1.0j, 0.0]])


def qsp_fazlarini_bul(hedef=None, d: int = 0, tur: int = 120,
                      tol: float = 1e-12, ne: str = "bul",
                      yari=None, x: float = 0.0, beta: float = 4.0):
    """FAZ AÇILARINI ÇEVRİMDIŞI BULMAK -- **tek terkip** (kütük H223).

    Küme: ``_qsp_tam_faz`` + ``qsp_degeri`` + ``qsp_faz_bul`` +
    ``gibbs_cift``. Dördü tek zincirin halkalarıydı: simetrik yarım
    diziyi tam diziye aç, o dizinin çizdiği polinomu oku, hedefe
    oturacak diziyi Gauss--Newton ile ara, ve hedefi (Gibbs'in çift
    kısmını) kur.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``tam``         simetrik yarım diziden ``d+1`` fazlık tam dizi
    ``değer``       ``Re⟨0|U_φ(x)|0⟩`` -- simetrik yarım fazlarla
    ``bul``         ``(yarım_fazlar, düğümdeki_âzamî_artık, tur)``
    ``gibbs``       hedef fonksiyon ``e^{−β/2}cosh(βx/2)``
    ==============  ==================================================

    Simetri ``φ_j = φ_{d−j}``dir; simetrik QSP'nin ürettiği polinom o
    zaman **reeldir** ve paritesi ``d mod 2``dir. Yarım dizinin uzunluğu
    ``⌈(d+1)/2⌉``dir.

    Arama Gauss--Newton, sönümlemeli adım, **belirlenimci** (rastgele
    tohum yok, başlangıç ``φ = (π/4, 0, …, 0)`` -- Dong vd. 2021'in
    kendi başlangıcı). Düğümler ``(0,1)`` aralığında Chebyshev'dir;
    parite ``d mod 2`` olduğu için yarım aralık yeterlidir.

    **Artık yalnız düğümlerde ölçülürse aşırı uyum gizlenir**; onun için
    rapor ayrıca 401 noktalı ızgarada da ölçer ve iki sayıyı yan yana
    yazar (H47).

    **Niçin Gibbs'in yalnız çift kısmı?** Tek bir simetrik QSP dizisinin
    ürettiği polinomun paritesi ``d mod 2``dir; parite karışık bir
    fonksiyon (``e^{−βx}``) tek diziyle temsil edilemez. Tam Gibbs için
    **iki tablo** (çift ve tek) ve bir birleştirme lâzımdır; bu terkip
    çift kısmı verir ve eksiği **açıkça yazar**, gizlemez::

        ½[e^{−β(1+x)/2} + e^{−β(1−x)/2}] = e^{−β/2}·cosh(βx/2)

    **QSP faz arama yasağı (padişahın 2. kat'î emri):** faz açıları
    çalışma anında ARANMAZ; ``GIBBS_FAZ_TABLOSU``ndan çekilir. Bu
    fonksiyon tabloyu **çevrimdışı** doldurmak içindir.
    """
    def tam(y, dd):
        yy = list(y)
        return yy + (yy[-2::-1] if int(dd) % 2 == 0 else yy[::-1])

    def deger(y, dd, xx):
        return float(np.real(faz_dizisinin_polinomu(
            tam(y, dd), float(xx), KIP_WX)))

    if ne == "gibbs":
        b = float(beta)
        return lambda t: math.exp(-b / 2.0) * math.cosh(b * float(t) / 2.0)
    if ne == "tam":
        return tam(yari, d)
    if ne == "değer":
        return deger(yari, d, x)
    if ne != "bul":
        raise ValueError("faz aramanın kipi bilinmiyor: %r" % (ne,))

    m = (int(d) + 2) // 2
    j = np.arange(m)
    xn = np.cos((2 * j + 1) * math.pi / (4 * m))
    y = np.array([float(hedef(float(t))) for t in xn])
    phi = np.zeros(m)
    phi[0] = math.pi / 4.0
    h = 1e-6
    it = 0
    for it in range(int(tur)):
        r = np.array([deger(phi, d, t) for t in xn]) - y
        if float(np.max(np.abs(r))) < float(tol):
            break
        Jm = np.empty((m, m))
        for k in range(m):
            e = np.zeros(m)
            e[k] = h
            Jm[:, k] = (np.array([deger(phi + e, d, t) for t in xn])
                        - np.array([deger(phi - e, d, t) for t in xn])
                        ) / (2.0 * h)
        try:
            dp = np.linalg.lstsq(Jm, -r, rcond=None)[0]
        except np.linalg.LinAlgError:      # pragma: no cover
            break
        adim, f0 = 1.0, float(r @ r)
        for _ in range(30):
            yeni = phi + adim * dp
            rn = np.array([deger(yeni, d, t) for t in xn]) - y
            if float(rn @ rn) < f0:
                phi = yeni
                break
            adim *= 0.5
        else:
            break
    r = np.array([deger(phi, d, t) for t in xn]) - y
    return phi, float(np.max(np.abs(r))), int(it)


GIBBS_DERECE: int = 32


GIBBS_FAZ_TABLOSU: Dict[float, Tuple[float, ...]] = {
    # β = 1.0  → ızgara artığı 2.89e-15
    1.0: (
        +7.85398163397448279e-01, +1.63940632205149596e-17, +5.16886774438653229e-17, -7.42228639824735648e-17,
        -1.78959009067879251e-16, +2.43774003034245568e-17, +3.46628346790352021e-17, -1.90752850243131835e-16,
        +2.72806398458374440e-16, -6.77086910096930828e-17, -1.51383139296484263e-16, -2.10235018858699831e-13,
        -3.02955504369563769e-10, -2.71991350421989660e-07, -1.31027313928002494e-04, -2.53646482751288573e-02,
        -7.02157454800921177e-01,
    ),
    # β = 2.0  → ızgara artığı 2.11e-15
    2.0: (
        +7.85398163397448279e-01, +5.69133184655856333e-17, -8.61026697426553020e-18, -1.06580180354355742e-16,
        -7.63182589175589310e-17, -4.46379274833280657e-18, -5.82497741028148363e-17, -1.14861919624991408e-16,
        +8.39837578115053448e-17, -2.06191412338938709e-16, -2.17096272043578891e-13, -1.15036763237282908e-10,
        -4.16244100453748546e-08, -9.39872303490259219e-06, -1.14419045654967459e-03, -5.67262228926020060e-02,
        -4.87910287357570138e-01,
    ),
    # β = 4.0  → ızgara artığı 1.33e-15
    4.0: (
        +7.85398163397448279e-01, +8.24018175080909381e-17, +6.68820616977939718e-17, -1.86516227769924546e-17,
        -5.94989362044357636e-17, +6.57536224442314508e-17, -5.61691229266047795e-17, -6.76094563499206992e-17,
        -7.31872002775397961e-15, -1.76604970340671767e-12, -3.24745616798840518e-10, -4.34704492824641589e-08,
        -3.99203765865601524e-06, -2.30717742717413823e-04, -7.32114712567225479e-03, -9.93827742304900924e-02,
        -3.20328643099665911e-01,
    ),
    # β = 8.0  → ızgara artığı 1.11e-15
    8.0: (
        +7.85398163397448279e-01, -6.26142592128008973e-17, +2.98965961285311724e-17, +2.50534840308875792e-17,
        +3.75628885686290800e-17, -1.38674542313115019e-16, -9.95690998011589187e-15, -9.62625370637811406e-13,
        -7.54662349904791803e-11, -4.67017104398569605e-09, -2.21213213665520287e-07, -7.70813102813456669e-06,
        -1.87413032714672377e-04, -2.95512823225523242e-03, -2.71677618330386055e-02, -1.23406109662883609e-01,
        -2.16343772164458575e-01,
    ),
}


def gibbs_fazlari(beta: float) -> Tuple[float, ...]:
    """Tablodan çek; tabloda yoksa **hata ver** -- runtime'da arama yok.

    Padişahın 2. kat'î kuralı budur. Yeni bir ``β`` lâzımsa tablo
    çevrimdışı genişletilir (``qsp_faz_bul`` ile), koşum sırasında
    değil.
    """
    b = float(beta)
    if b not in GIBBS_FAZ_TABLOSU:
        raise KeyError("β = %g tabloda yok; çevrimdışı hesaplayıp "
                       "GIBBS_FAZ_TABLOSU'na ekleyin (runtime arama yasak)"
                       % b)
    return GIBBS_FAZ_TABLOSU[b]




# ════════════════════════════════════════════════════════════════════
#  ogrenme/fct.py
# ════════════════════════════════════════════════════════════════════











# ════════════════════════════════════════════════════════════════════
#  ogrenme/sta.py
# ════════════════════════════════════════════════════════════════════







# ════════════════════════════════════════════════════════════════════
#  kuantum/bec.py
# ════════════════════════════════════════════════════════════════════

def fazlari_kilitle(psi: np.ndarray, tur: int = 60, g: float = 0.6,
                   dt: float = 0.0, V_gaye: np.ndarray = None,
                   ne: str = "kilit", n: int = 256, tohum: int = 0,
                   turlar: Sequence[int] = (0, 1, 5, 20, 60)):
    """YİRMİ UZAYIN FAZINI TEK FAZDA KİLİTLEMEK -- tek terkip (H223).

    Küme: ``faz_uyumu`` + ``bose_einstein_faz_kilidi`` + ``faz_cetveli``.
    Üçü tek amelin parçalarıydı: fazı ölç, fazı kilitle, kilidin fiilen
    ısırdığını yan yana göster. İkincisi birincisini çağırıyor, üçüncüsü
    ikisini birden çağırıyordu.

    ==============  ================================================
    ``ne``          ne verir
    ==============  ================================================
    ``uyum``        Kuramoto düzen değişkeni ``T = |⟨e^{iθ}⟩|``
    ``kilit``       ``(Ψ_kilitli, T)`` -- Gross--Pitaevskii ile
    ``cetvel``      kilitsiz ile kilitli hâl yan yana (H47, H90)
    ==============  ================================================

    **Faz uyumu.** ``1`` bütün genliklerin **aynı** fazda olması, ``0``
    fazların düzgün dağılmasıdır. Sıfır genlikli bileşenler fazsızdır ve
    ortalamaya girmez; girseydi ölçü sahte yükselirdi.

    **Kilit.** Split-step: her turda evvelâ kinetik yarı adım Fourier
    uzayında, sonra ``V_gaye + g|Ψ|²`` potansiyeli mevzî, sonra kinetik
    yarı adım. Hayalî zaman kullanıldığı için genlik en düşük enerjili
    kipe akar ve fazlar hizalanır; her turdan sonra norm geri verilir::

        iℏ ∂_t |Ψ⟩ = ( −(ℏ²/2m)∇² + V_gaye + g|Ψ|² ) |Ψ⟩
        Δθ → 0,   T ≡ 1

    **ÖLÇÜLEREK DÜZELTİLEN İKİ KUSUR.**

    1. ``dt`` sabit ``0,05`` idi ve **yakınsamıyordu**: ölçüldü, faz
       uyumu 12 turda ``0,0296 → 0,0601``de kalıyordu. Sebep, sönüm
       çarpanının ``exp(−dt·k²/2)`` olması ve ``n = 256`` ızgarasında
       kiplerin ekserisinde ``k`` küçük olduğu için sönümün hiç
       ısırmamasıydı. ``dt`` artık **ızgaradan** seçilir: en küçük sıfır
       olmayan kipin bile tur boyunca sönümlenmesi gerekir.
    2. Kırmızı kontrolüm ``g`` idi ve **yanlıştı**: ``V = 0, g = 0``
       hâlinde hayalî zaman zaten düzgün taban duruma götürür, o da
       faz-kilitlidir. Yani ``g = 0`` da yeşil yanardı ve ölçü hiçbir
       şey ayırt etmezdi. Doğru kontrol **tur sayısıdır**: ``tur = 0``da
       kilit yoktur.

    ``dt`` ızgaradan seçildiği için kilit **tek turda** tamamlanır; yani
    ``tur`` bir yakınsama düğmesi değil, açık/kapalı anahtarıdır ve öyle
    sunulur. Kademeli bir yakınsama iddia edilmiyor.
    """
    def uyum(x: np.ndarray) -> float:
        v = np.asarray(x, dtype=complex).reshape(-1)
        b = np.abs(v)
        esik = 1e-12 * (b.max() if b.size else 1.0)
        dolu = v[b > esik]
        if dolu.size == 0:
            return 0.0
        return float(np.abs(np.mean(dolu / np.abs(dolu))))

    if ne == "uyum":
        return uyum(psi)

    def kilitle(x, t):
        v = np.asarray(x, dtype=complex).reshape(-1).copy()
        m = int(v.size)
        if m == 0:
            return v, 0.0
        nrm = np.linalg.norm(v)
        if nrm <= 0:
            return v, 0.0
        v /= nrm
        k = 2.0 * np.pi * np.fft.fftfreq(m)
        d = float(dt)
        if d <= 0.0:
            k_min = float(np.min(np.abs(k[k != 0]))) if np.any(k != 0) else 1.0
            d = 8.0 / max(k_min ** 2 * max(int(t), 1), 1e-12)
        kin = np.exp(-0.5 * d * (k ** 2))            # hayalî zaman
        V0 = np.zeros(m) if V_gaye is None else \
            np.asarray(V_gaye, float).reshape(-1)[:m]
        if V0.size < m:
            V0 = np.pad(V0, (0, m - V0.size))
        for _ in range(int(t)):
            v = np.fft.ifft(kin * np.fft.fft(v))
            v = v * np.exp(-d * (V0 + float(g) * np.abs(v) ** 2))
            v = np.fft.ifft(kin * np.fft.fft(v))
            nv = np.linalg.norm(v)
            if nv <= 0:
                break
            v /= nv
        return v, uyum(v)

    if ne == "kilit":
        return kilitle(psi, tur)
    if ne != "cetvel":
        raise ValueError("faz kilidinin kipi bilinmiyor: %r" % (ne,))

    # Değişken **tur sayısıdır**, ``g`` değil (yukarıdaki 2. kusur).
    rng = np.random.default_rng(int(tohum))
    ham = rng.normal(size=n) + 1j * rng.normal(size=n)
    return {"başlangıç_T": uyum(ham),
            "satır": [{"tur": int(t), "T": float(kilitle(ham, int(t))[1])}
                      for t in turlar]}




# ════════════════════════════════════════════════════════════════════
#  kuantum/fubini.py
# ════════════════════════════════════════════════════════════════════

def yokus(F=None, P=None, ne: str = "önşart", sonum: float = 1e-6,
                  n: int = 40, d: int = 6, C: int = 3, tohum: int = 0,
                  h: float = 1e-5, psi=None, teta=None, W=None,
                  durum_kur=None):
    """HANGİ YÖN NE KADAR PAHALI -- **tek terkip** (kütük H223).

    Küme: ``fubini_metrigi`` + ``olasilik_kovaryansi`` +
    ``fisher_metrigi_tam`` + ``fubini_tam_kiyas`` +
    ``fubini_tam_dogrulama``. Beşi tek bir nesnenin -- parametre
    uzayının Fubini--Study/Fisher metriğinin -- ayrı okunuşuydu; ikisi
    kıyas, biri kestirme, biri tam, biri de tam olanın çekirdeği.
    Softmax olasılığı üç ayrı yerde yeniden kuruluyordu.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``önşart``      öznitelik uzayında ``G⁺`` (kestirme, ucuz)
    ``kovaryans``   ``Cov(P_k) = diag(P_k) − P_k P_kᵀ``, ``(N,C,C)``
    ``tam``         ``g = (1/4N) Σ_k (φφᵀ) ⊗ Cov(P_k)``, ``(dC, dC)``
    ``kıyas``       kestirme ile hakikînin farkı -- **kırmızı yanmalı**
    ``doğrulama``   kapalı form ile sayısal FS farkı -- **yeşil olmalı**
    ``sayısal``     ``g_ij`` merkezî farkla, keyfî ``psi(θ)`` için
    ``örtüşme``     ``S`` alt uzayda, **ikili örtüşmelerden** (MPS)
    ==============  ==================================================

    Son iki kip KÜME 4 tevhidinde (kütük H223) buraya eridi: aynı
    metrik üç ayrı dosyada üç ayrı gövdeyle hesaplanıyordu --
    ``kuantum/fubini.py`` kapalı formda, ``kuantum/ceride.py`` sayısal
    merkezî farkla, ``nefs/tabii_gradyan.py`` ise MPS iç çarpımlarıyla.
    Formül üçünde de birdir::

        g_ij = Re[⟨∂_iΨ|∂_jΨ⟩ − ⟨∂_iΨ|Ψ⟩⟨Ψ|∂_jΨ⟩]

    İkinci terim **izdüşümdür** ve atlanamaz: onsuz dizey, durumun
    normunu değiştiren (fizikî olmayan) yönü de bir uzunluk sayar.

    ``örtüşme`` kipinde **ölçek normalizasyonu şarttır.** Ham ``S``in
    özdeğerleri ``h``ye ve durumun büyüklüğüne bağlıdır; ölçüldü ve
    kaldı: ``(S+λI)⁻¹g`` adımı 3,7e+05 normunda çıkıyor ve hiçbir adım
    kabul edilmiyordu. İzine bölmek metriği ölçekten arındırır; adımın
    büyüklüğünü artık ``eta`` ve çizgi araması tayin eder.

    **Türetme.** ``ψ = √P`` alındığında::

        ψ_kc = √(P_kc / N),   ⟨ψ|ψ⟩ = 1
        ∂ψ_kc = ∂P_kc / (2√(N P_kc))
        ⟨ψ|∂ψ⟩ = (1/2N) Σ_kc ∂P_kc = 0        (Σ_c P_kc ≡ 1)

    O hâlde ikinci terim **düşer** ve
    ``g_ij = (1/4N) Σ_k Σ_c (1/P_kc) ∂_i P_kc ∂_j P_kc``.
    Softmax'ta ``z = Wᵀφ``, ``θ = vec(W)``,
    ``∂P_c/∂W_ab = φ_a P_c(δ_cb − P_b)``::

        g[(a,b),(a',b')] = (1/4N) Σ_k φ_ka φ_ka' [diag(P_k) − P_k P_kᵀ]_bb'
        g = (1/4N) Σ_k (φ_k φ_kᵀ) ⊗ Cov(P_k)

    **Kestirmenin niçin %59 saptığı buradan görünür** (padişahın fermanı
    İCAD-OPT/14, itham doğrudur): ``Cov(P_k)`` yerine ``I`` koymak, renk
    uzayının eğriliğini tamamen atmaktır. ``C = 10`` iken o blok
    10×10'dur; atmanın hiçbir mazereti yoktu.

    ``Cov(P_k)`` **tekildir** (satır toplamları sıfır, ``P`` sağ sıfır
    uzayında): olasılıklar ``Σ_c P_c = 1`` kısıtına tâbidir, yani
    metriğin bir yönü ölçülemez. Tersini alırken sözde-ters yahut sırt
    lazımdır ve bu bir kusur değil, kısıtın kendisidir.

    Endeks düzeni ``θ = W.reshape(-1)`` ile birebir: satır-öncelikli,
    ``(a, b) → a·C + b``. Düzen tutmazsa metrik doğru olsa bile yanlış
    yere tatbik edilir.

    **Maliyet açıkça:** tam metrik ``d²C²`` gerçel sayı. ``d = 276,
    C = 10`` için 7,6 milyon hücre ≈ 61 MB. ``d`` büyürse maliyet ``d²``
    ile büyür ve o zaman blok-köşegen yaklaşım ayrıca **ölçülerek**
    gerekçelendirilmeli.
    """
    def kov(Pm: np.ndarray) -> np.ndarray:
        Pm = np.atleast_2d(np.asarray(Pm, float))
        return (np.einsum("kc,cd->kcd", Pm, np.eye(Pm.shape[1]))
                - np.einsum("kb,kc->kbc", Pm, Pm))

    def onsart(Fm: np.ndarray, Pm: np.ndarray) -> np.ndarray:
        """``|Ψ⟩ = √P`` alındığında ``4g`` tam olarak Fisher bilgisidir.
        Softmax için Fisher'ın öznitelik çarpanı ``Φᵀ diag(w) Φ``dir;
        ``w`` hücre başına ``1 − max_c P`` ağırlığıdır (kesin hücreler
        metriğe az katkı verir, kararsızlar çok)."""
        Fm = np.atleast_2d(np.asarray(Fm, float))
        Pm = np.atleast_2d(np.asarray(Pm, float))
        w = 1.0 - np.max(Pm, axis=1)
        G = (Fm.T * w) @ Fm / max(Fm.shape[0], 1)
        return np.linalg.pinv(G + float(sonum) * np.eye(G.shape[0]))

    def tam(Fm: np.ndarray, Pm: np.ndarray) -> np.ndarray:
        Fm = np.atleast_2d(np.asarray(Fm, float))
        Pm = np.atleast_2d(np.asarray(Pm, float))
        N, dd = Fm.shape
        CC = int(Pm.shape[1])
        g4 = np.einsum("ka,kA,kbB->abAB", Fm, Fm, kov(Pm), optimize=True)
        return g4.reshape(dd * CC, dd * CC) / (4.0 * max(N, 1))


    if ne in ("sayısal", "metrik") or (ne == "doğrulama" and psi is not None):
        if ne == "metrik":
            ne = "sayısal"
        teta = np.asarray(teta, float).ravel()
        n = teta.size

        def bir(z: np.ndarray) -> np.ndarray:
            v = np.asarray(psi(z), float).ravel()
            return v / max(float(np.linalg.norm(v)), 1e-300)

        p0 = bir(teta)
        d = np.empty((n, p0.size))
        for k in range(n):
            e = np.zeros(n)
            e[k] = h
            d[k] = (bir(teta + e) - bir(teta - e)) / (2.0 * h)
        v = d @ p0
        g = (d @ d.T) - np.outer(v, v)
        if ne == "sayısal":
            return g
        oz = np.linalg.eigvalsh((g + g.T) / 2.0)
        olcek = max(float(abs(oz).max()), 1e-30)
        return {"g": g, "en_küçük_özdeğer": float(oz.min()),
                "psd": bool(oz.min() > -1e-8 * olcek),
                "iz": float(np.trace(g))}

    if ne == "örtüşme":
        # ``∂_iψ ≈ (ψ_i⁺ − ψ_i⁻)/(2h)`` olduğu için bütün iç çarpımlar
        # ``2r`` durumun **ikili örtüşmelerinden** çıkar; ayrıca durum
        # farkı hiç kurulmaz (MPS'te toplam bağ boyutunu şişirirdi).
        r = W.shape[1]
        durumlar = []
        for i in range(r):
            durumlar.append(durum_kur(teta + h * W[:, i]))
            durumlar.append(durum_kur(teta - h * W[:, i]))
        psi = durum_kur(teta)

        n = 2 * r
        G = np.empty((n, n))
        for i in range(n):
            for j in range(i, n):
                v = float(np.asarray(durumlar[i].ic_carpim(durumlar[j])).ravel()[0])
                G[i, j] = G[j, i] = v
        o = np.array([float(np.asarray(d_.ic_carpim(psi)).ravel()[0])
                      for d_ in durumlar])

        S = np.empty((r, r))
        for i in range(r):
            for j in range(r):
                ip, im, jp, jm = 2 * i, 2 * i + 1, 2 * j, 2 * j + 1
                ic = (G[ip, jp] - G[ip, jm] - G[im, jp] + G[im, jm]) \
                    / (4.0 * h * h)
                oi = (o[ip] - o[im]) / (2.0 * h)
                oj = (o[jp] - o[jm]) / (2.0 * h)
                S[i, j] = ic - oi * oj
        S = 0.5 * (S + S.T)
        # **Ölçek normalizasyonu şart.** Ham ``S``in özdeğerleri
        # ``h``ye ve durumun büyüklüğüne bağlıdır; ölçüldü ve kaldı:
        # ``(S+λI)⁻¹g`` adımı 3,7e+05 normunda çıkıyor ve hiçbir adım
        # kabul edilmiyordu. İzine bölmek metriği ölçekten arındırır;
        # adımın büyüklüğünü artık ``eta`` ve çizgi araması tayin eder.
        iz = float(np.trace(S)) / max(S.shape[0], 1)
        if iz > 1e-30:
            S = S / iz
        oz = np.linalg.eigvalsh(S)
        kosul = float(abs(oz[-1]) / max(abs(oz[0]), 1e-30))
        return S, kosul

    if ne == "önşart":
        return onsart(F, P)
    if ne == "kovaryans":
        return kov(P)
    if ne == "tam":
        return tam(F, P)
    if ne not in ("kıyas", "doğrulama"):
        raise ValueError("bilgi metriğinin kipi bilinmiyor: %r" % (ne,))

    # --- kıyas ve doğrulama: aynı softmax kurulumundan
    rng = np.random.default_rng(int(tohum))
    Fr = rng.normal(size=(n, d))
    w0 = rng.normal(scale=0.3, size=d * C)

    def _P(teta):
        z = Fr @ np.asarray(teta, float).reshape(d, C)
        z = z - z.max(axis=1, keepdims=True)
        e = np.exp(z)
        return e / e.sum(axis=1, keepdims=True)

    def psi(teta: np.ndarray) -> np.ndarray:
        v = np.sqrt(np.clip(_P(teta), 0, None)).reshape(-1)
        return v / np.linalg.norm(v)

    if ne == "doğrulama":
        # Bu ölçü **yeşile dönmelidir**: iddia "çarpan" değil eşitliktir.
        g_say = np.asarray(yokus(ne="sayısal", psi=psi, teta=w0, h=h), float)
        g_tam = tam(Fr, _P(w0))
        pay = float(np.linalg.norm(g_say - g_tam))
        payda = max(float(np.linalg.norm(g_say)), 1e-12)
        return {"bağıl_fark": pay / payda,
                "iz_sayısal": float(np.trace(g_say)),
                "iz_kapalı": float(np.trace(g_tam))}

    # Bu ölçü **kırmızı yanmalıdır**: iddia eşitlik değil çarpan olmaktır.
    # Sıfır fark çıkarsa ölçü bozuktur.
    g = np.asarray(yokus(ne="sayısal", psi=psi, teta=w0), float)
    fisher = 4.0 * n * g
    Pm = _P(w0)
    G = np.linalg.pinv(onsart(Fr, Pm))
    ons = np.kron(G, np.eye(C))
    iz_f = float(np.trace(fisher))
    iz_g = float(np.trace(ons))
    olcek = iz_f / iz_g if iz_g else 0.0
    return {"iz_fisher": iz_f, "iz_önşart": iz_g, "ölçek": olcek,
            "bağıl_fark": float(np.linalg.norm(fisher - olcek * ons)
                                / max(np.linalg.norm(fisher), 1e-12))}


def izgarayi_oku(W: np.ndarray, F: np.ndarray, sekil: Tuple[int, int],
                 komsu_guncelle: Optional[Callable[[np.ndarray, int, int],
                                                   np.ndarray]] = None,
                 renk_sayisi: int = 10, tekrar: int = 0):
    """IZGARAYI HÜCRE HÜCRE OKUMAK -- **tek terkip** (kütük H223).

    Küme: ``fubini_study_agac_cozumu`` + ``belirlenimci_mi``. İkincisi
    birincisini üç kere çağırıp neticeleri kıyaslıyordu; ayrı bir isim
    taşıması, "okuma" ile "okumanın belirlenimciliği"ni iki ayrı şey
    gibi göstermekti. ``tekrar > 0`` verilirse aynı okuma o kadar kere
    yapılır ve **hepsi aynı mı** diye döner.

    .. math::  x^*_k = \\arg\\max_c\\; g^+ \\cdot \\nabla_\\theta \\log P

    ``W`` öğrenilen ağırlık, ``F`` hücre başına öznitelik, ``sekil``
    çıktı ızgarasının ebadı. ``komsu_guncelle`` verilirse bir hücrenin
    hükmü sonraki hücrelerin özniteliğine işlenir (``x_<k*`` şartı).
    Ağaç okuması soldan sağa, üstten aşağı **şartlı** ilerler; hücreleri
    birbirinden bağımsız okumak "ağaç" olmazdı.

    Dönen: ``(ızgara, güven)``; ``tekrar > 0`` ise ``(ızgara, güven,
    belirlenimci_mi)``. Güven, seçilen renklerin ortalama olasılığıdır --
    yüksek olması doğruluk **garantisi değildir** ve öyle sunulmuyor;
    yalnız dalganın kendi kararlılığıdır.

    **Deterministik** demek: örnekleme yok, sıcaklık yok, rastgele tohum
    yok. Aynı dalga aynı ızgarayı verir; iki koşu arasında fark çıkarsa
    bu bir **kusurdur** ve ``tekrar`` onu yakalar.
    """
    def coz(F0):
        Wm = np.asarray(W, float)
        Fm = np.atleast_2d(np.asarray(F0, float)).copy()
        H, Wd = int(sekil[0]), int(sekil[1])

        def _olasilik(X: np.ndarray) -> np.ndarray:
            z = X @ Wm
            z = z - z.max(axis=1, keepdims=True)
            e = np.exp(z)
            return e / e.sum(axis=1, keepdims=True)

        Ginv = yokus(Fm, _olasilik(Fm), ne="önşart")
        out = np.zeros((H, Wd), dtype=int)
        guven = []
        for i in range(H):
            for j in range(Wd):
                k = i * Wd + j
                if k >= Fm.shape[0]:
                    continue
                phi = Fm[k]
                p = _olasilik(phi[None, :])[0]
                # ∇_W log P(c) = φ ⊗ (e_c − p);  tabiî gradyan: g⁺ φ
                # Skor: her renk için ⟨g⁺φ, φ(e_c − p)⟩ = (φᵀg⁺φ)(1 − p_c)
                #       artı log-olasılık; ölçek çarpanı renkler arasında
                #       sabit olduğu için sıralamayı log P belirler ve
                #       metrik **kararsız hücrelerde** ağırlığı arttırır.
                olcek = float(phi @ (Ginv @ phi))
                skor = np.log(np.clip(p, 1e-12, 1.0)) + olcek * (p - p.mean())
                c = int(np.argmax(skor))
                out[i, j] = c
                guven.append(float(p[c]))
                if komsu_guncelle is not None:
                    Fm = komsu_guncelle(Fm, k, c)
        return out, (float(np.mean(guven)) if guven else 0.0)

    g0, guv = coz(F)
    if int(tekrar) <= 0:
        return g0, guv
    ayni = all(np.array_equal(g0, coz(F)[0]) for _ in range(int(tekrar) - 1))
    return g0, guv, bool(ayni)




# ════════════════════════════════════════════════════════════════════
#  kuantum/dalga.py
# ════════════════════════════════════════════════════════════════════

# İki AYRI kayıp imzası vardı ve ikincisi birincisini sessizce
# gölgeliyordu (Küme 4 birleştirmesinden kalma, H227'de yakalandı).
KayipYigin = Callable[[np.ndarray], np.ndarray]   # (B,n) → (B,)      # (B,n) → (B,)


def oragin_donusu(ne: str = "en_iyi_k", mu: float = 0.0, k: int = 0,
                  z=None, m=None, a=None):
    """ORAĞIN KAÇ KERE DÖNMESİ LÂZIM -- **tek terkip** (kütük H223).

    Küme: ``moment_kestir`` + ``grover_katsayilari`` + ``_polinom`` +
    ``grover_ikili`` + ``en_iyi_k``. Beşi tek bir sualin parçalarıydı:
    genlik yükseltmesi kaç dönüşte en iyiye varır ve o dönüşler genliği
    ne yapar. İlk üçü sürekli faz orağının polinomunu, son ikisi ikili
    (eşik) orağın kapalı formunu kurar; ikisi de **aynı** Grover
    özyinelemesidir.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``momentler``   ``m_j = 𝔼[z^j]``, ``j = 0..k``; ``m₀ = 1`` **tam**
    ``katsayılar``  ``P_k``ın katsayıları
    ``polinom``     ``P(z)`` -- Horner ile
    ``ikili``       ``(α_k, β_k)`` iyi/kötü genlik çarpanları
    ``en_iyi_k``    ``k* = round((π/2 − θ)/(2θ))``, ``θ = arcsin √μ``
    ==============  ==================================================

    **İkili orak.** ``α₀ = β₀ = 1``. Her adımda ``U_L`` iyilerin
    işaretini çevirir, ``D`` ise ortalamaya göre yansıtır::

        s = −μ α + (1−μ) β ,   α ← 2s + α ,   β ← 2s − β

    Sabit noktası yoktur; ``sin((2k+1)θ)`` ile salınır. Bu yüzden
    ``k``yı büyütmek daima iyileştirmez -- **fazla dönmek geri
    götürür**; ``en_iyi_k`` bunu hesaba katar.

    Vesikadaki ``(π/4)√(2^N/M)`` ``k*``ın ``μ → 0`` haddidir; küçük
    uzayda o yaklaşım fazla döndürür, tam formül döndürmez.

    Katsayı özyinelemesi: ``a ← 2(Σ_j a_j m_j) e₀ − shift(a)``.
    """
    if ne == "momentler":
        zz = np.asarray(z)
        out = np.empty(int(k) + 1, complex)
        kuvvet = np.ones_like(zz)
        for j in range(int(k) + 1):
            out[j] = 1.0 + 0j if j == 0 else kuvvet.mean()
            kuvvet = kuvvet * zz
        return out
    if ne == "katsayılar":
        mm = np.asarray(m)
        c = np.zeros(1, complex)
        c[0] = 1.0
        for _ in range(int(k)):
            ap = np.concatenate([[0.0 + 0j], c])          # z ile çarp
            sm = complex(np.dot(ap, mm[:len(ap)]))
            yeni = -ap
            yeni[0] += 2.0 * sm
            c = yeni
        return c
    if ne == "polinom":
        zz = np.asarray(z)
        y = np.zeros_like(zz)
        for c in np.asarray(a)[::-1]:
            y = y * zz + c
        return y
    if ne == "ikili":
        al = be = 1.0
        for _ in range(max(int(k), 0)):
            sm = -mu * al + (1.0 - mu) * be
            al, be = 2.0 * sm + al, 2.0 * sm - be
        return al, be
    if ne == "en_iyi_k":
        u = float(min(max(mu, 1e-12), 1.0))
        teta = math.asin(math.sqrt(u))
        if teta <= 1e-9:
            return 0
        return max(0, int(round((math.pi / 2 - teta) / (2 * teta))))
    raise ValueError("orak dönüşünün kipi bilinmiyor: %r" % (ne,))


def tartinin_dayandigi_nokta(L: np.ndarray, beta: float,
                             taban_ess: float = 0.25,
                             ne: str = "tartı") -> np.ndarray:
    """TARTI KAÇ NOKTAYA DAYANIYOR -- **tek terkip** (kütük H223).

    Küme: ``_ess`` + ``_tartili``. İkincisi birincisini kırk kere
    çağırıyordu; ayrı isim taşımaları, ölçü ile ölçünün şartını iki şey
    gibi göstermekti. ``ne="ess"`` yalnız müessir örnek sayısını
    (``(Σw)²/Σw²``) verir, ``ne="tartı"`` şartı sağlayan tartıyı.

    ``w ∝ exp(−sβ(L−L_min))``; ``s``, **müessir örnek sayısı** tabanı
    tutacak en büyük değer olarak ikiye bölerek bulunur.

    Ham ``s = 1`` kuruldu ve ölçüldü: Rastrigin'de ``β·ΔL ≈ 67`` olduğu
    için tartı bir avuç noktaya çöküyor, uydurma o birkaç noktayı
    ezberliyor ve netice bozuluyordu (48,6; tartısız 43,8; rastgele
    35,4). Yani ne tartısız ne de tam tartılı doğrudur; doğru olan,
    tartının **kaç noktayı fiilen kullandığını** şart koşmaktır.
    """
    def ess(w: np.ndarray) -> float:
        s1 = float(w.sum())
        s2 = float((w * w).sum())
        return (s1 * s1 / s2) if s2 > 0 else 0.0

    if ne == "ess":
        return ess(np.asarray(L, float))
    d = np.asarray(L, float) - float(np.min(L))
    n = len(d)
    hedef = taban_ess * n
    ham = np.exp(np.clip(-beta * d, -700, 0))
    if ess(ham) >= hedef:
        return ham
    alt, ust = 0.0, 1.0
    for _ in range(40):
        sm = 0.5 * (alt + ust)
        w = np.exp(np.clip(-sm * beta * d, -700, 0))
        if ess(w) >= hedef:
            alt = sm
        else:
            ust = sm
    return np.exp(np.clip(-alt * beta * d, -700, 0))


@dataclass
class DalgaCevrimi:
    no: int
    esik: float
    mu: float
    k: int
    alfa: float
    beta: float
    p_iyi_once: float
    p_iyi_sonra: float
    en_iyi_L: float
    kabul: float
    artik: float
    beta_tavlama: float = 0.0
    tampon: int = 0


class DalgaEniyileyici:
    """NQS dalgasını kayıp yüzeyinin asgarîsine **çökerten** motor.

    Klasik Adam/SGD döngüsü yoktur ve yerine bir başkası konmamıştır:
    öğrenme, son katın hedef genliğe **kapalı formda** oturtulmasıdır.
    """

    def __init__(self, nqs: NQS, L: KayipYigin, tohum: int = 0) -> None:
        self.nqs = nqs
        self.L = L
        self.tohum = int(tohum)
        self.seyir: List[DalgaCevrimi] = []
        self.en_iyi_x: Optional[np.ndarray] = None
        self.en_iyi_deger = float("inf")
        self.esik = float("inf")          # Dürr–Høyer: ASLA yükselmez
        self.elit: Optional[np.ndarray] = None
        self.beta_tavlama = 0.0           # Grover'ın koyduğu tavlama sıcaklığı
        self.tampon_X: Optional[np.ndarray] = None
        self.tampon_L: Optional[np.ndarray] = None
        self.tampon_azami = 20000
        self.kenar: Optional[np.ndarray] = None

    # -----------------------------------------------------------------
    def _son_kat_oturt(self, X: np.ndarray, hedef_log: np.ndarray,
                       lam: float = 1e-3,
                       agirlik: Optional[np.ndarray] = None) -> float:
        """``log|ψ|``ı hedefe **en küçük karelerle** oturt -- gradyan yok.

        ``log ψ`` son kat katsayılarında doğrusal olduğu için çözüm
        kapalıdır: ``c = (ΦᵀWΦ + λI)⁻¹ ΦᵀW y``. Sanal kısma (faza)
        dokunulmaz: eşik orağı reel bir çarpan verir, fazı değiştirmez;
        değiştirmiş gibi yapmak uydurma olurdu.

        **Tartı neden şart.** Tartısız kuruldu ve ölçüldü: tampon büyüdükçe
        içi ilk çevrimlerin kötü noktalarıyla doluyor, en küçük kareler
        çoğunluğa uyduğu için dalgayı **kötü bölgede** doğru, iyi bölgede
        yanlış kılıyordu (Rastrigin'de 43,8; rastgele 35,4 -- yenilmişti).
        Tartı ``w ∝ exp(−βL)``, yani dalganın kendi kütlesidir: uydurma,
        kütlenin bulunduğu yerde doğru olsun diye oraya bakar. Bu, VMC'nin
        kendi tartısıdır, sonradan uydurulmuş bir hile değil.
        """
        F = self.nqs.ozellik(X)
        if agirlik is None:
            A = F.T @ F + lam * np.eye(F.shape[1])
            b = F.T @ hedef_log
        else:
            w = np.asarray(agirlik, float)
            w = w / (w.sum() + 1e-300) * len(w)
            A = (F * w[:, None]).T @ F + lam * np.eye(F.shape[1])
            b = (F * w[:, None]).T @ hedef_log
        c = np.linalg.solve(A, b)
        artik = float(np.linalg.norm(F @ c - hedef_log)
                      / (np.linalg.norm(hedef_log) + 1e-12))
        eski = self.nqs.son_kat()
        self.nqs.son_kat_yukle(c + 1j * eski.imag)
        return artik

    # -----------------------------------------------------------------
    def cevrim(self, no: int, ornek: int = 512, zincir: int = 64,
               oran: float = 0.15, lam: float = 1e-3,
               kademe: float = 0.5) -> Cevrim:
        """Bir tam merhale: örnekle → tart → girişim → kapalı form oturt."""
        X, tani = self.nqs.ornekle(ornek, zincir=zincir,
                                   tohum=self.tohum + 1000 * no,
                                   baslangic=self.elit, kenar=self.kenar)
        Ld = np.asarray(self.L(X), float)

        # --- Dürr–Høyer eşiği **monoton azalır**. İlk hâlde eşiği her
        # çevrimde o çevrimin niceliğinden almıştım; ölçüldü ve kaldı:
        # dağılım keskinleştikçe nicelik de beraber yükseliyor, eşik
        # 18'den 19'a çıkıyor ve arama ilerlemeyi bırakıyordu. Eşik
        # geriye gitmemelidir: aksi hâlde "daha iyisini ara" hükmü
        # kendi kendini nakzeder.
        aday = float(np.quantile(Ld, oran))
        self.esik = min(self.esik, aday)
        iyi = Ld <= self.esik
        mu = float(iyi.mean())
        if mu <= 0.0:
            # hiç iyi örnek yok: eşik fazla dar. Bir kademe gevşetilir
            # ki girişim tanımsız kalmasın -- fakat gevşeme kaydedilir.
            self.esik = aday
            iyi = Ld <= self.esik
            mu = max(float(iyi.mean()), 1.0 / len(Ld))
        esik = self.esik

        k = oragin_donusu("en_iyi_k", mu=mu)
        al, be = oragin_donusu("ikili", mu=mu, k=k)

        p_once = mu
        p_sonra = float((mu * al * al) / (mu * al * al
                                          + (1 - mu) * be * be + 1e-300))

        # --- GROVER BİR TAVLAMA TAKVİMİDİR
        #
        # İlk hâlde girişim çarpanı doğrudan o çevrimin 512 örneğine
        # oturtuluyordu. Ölçüldü ve KALDI: Rastrigin'de 12 çevrimde
        # rastgeleyi geçiyor (48,7'ye 54,6), 40 çevrimde ise rastgeleye
        # YENİLİYORDU (48,7'ye 35,4). Sebep iki katlıdır -- (a) yalnız
        # son örneklere oturan bir uydurma öncekini unutur, (b) her
        # çevrimde çarpan biriktikçe dalga aşırı keskinleşir, Metropolis
        # kabul oranı düşer ve zincir tek havzada kilitlenir.
        #
        # Doğrusu, girişimin **oranını** bir sıcaklığa çevirmektir.
        # Grover adımı iyi/kötü genlik oranını ``R = (α/β)²`` kadar
        # büyütür; Boltzmann karşılığı
        #     exp(−Δβ·(L̄_kötü − L̄_iyi)) = R  ⟹  Δβ = ln R / ΔL
        # olur. Böylece Grover ne kadar sertleştireceğini **söyler**,
        # sertliği biz uydurmayız; ve hedef, biriken çarpan değil
        # ``−(β/2)·L`` gibi **mutlak** bir yüzey olur -- unutma biter.
        #
        # **Tavlama hızının haddi.** Sınırsız bırakıldı ve ölçüldü:
        # Ackley'de ``ΔL`` küçük olduğu için ``Δβ`` şişiyor, 40 çevrimde
        # ``β = 69,9``a çıkıyor ve dalga daha aramayı bitirmeden
        # donuyordu (netice 5,01; rastgele 4,92 -- yenilmişti).
        # Bir çevrimde ``β``nın kayıp yayılımı cinsinden artışı
        # ``β·σ_L`` biriminde ``kademe``yi geçemez; yani sertleşme,
        # yüzeyin kendi ölçeğine bağlanır, mutlak bir sayıya değil.
        R = (al * al) / (be * be + 1e-300)
        dL = float(Ld[~iyi].mean() - Ld[iyi].mean()) if (~iyi).any() else 0.0
        sigma = float(np.std(Ld)) + 1e-12
        if dL > 1e-9 and R > 1.0:
            self.beta_tavlama += min(math.log(R) / dL, kademe / sigma)

        # --- tampon: görülen her nokta hatırlanır (unutma yok)
        self.tampon_X = (X if self.tampon_X is None
                         else np.vstack([self.tampon_X, X]))
        self.tampon_L = (Ld if self.tampon_L is None
                         else np.concatenate([self.tampon_L, Ld]))
        if len(self.tampon_X) > self.tampon_azami:
            self.tampon_X = self.tampon_X[-self.tampon_azami:]
            self.tampon_L = self.tampon_L[-self.tampon_azami:]

        # --- hedef: ``log|ψ| = −(β/2)·L`` -- KAPALI FORM, gradyan yok
        merkez = float(self.tampon_L.mean())
        hedef = -0.5 * self.beta_tavlama * (self.tampon_L - merkez)
        w = tartinin_dayandigi_nokta(self.tampon_L, self.beta_tavlama, taban_ess=0.25)
        artik = self._son_kat_oturt(self.tampon_X, hedef, lam=lam,
                                    agirlik=w)

        j = int(np.argmin(Ld))
        if Ld[j] < self.en_iyi_deger:
            self.en_iyi_deger = float(Ld[j])
            self.en_iyi_x = X[j].copy()

        # elit hafıza: bir sonraki çevrimin zincirleri buradan başlar
        sec = np.argsort(Ld)[:max(8, len(Ld) // 32)]
        yeni = X[sec]
        self.elit = (yeni if self.elit is None
                     else np.unique(np.vstack([self.elit, yeni]),
                                    axis=0)[:64])

        # bağımsız teklifin kenar dağılımı: tampondaki KÜTLEYE göre
        # (yani ``exp(−βL)`` tartısıyla) bit başına ortalama. Elitin
        # düz ortalaması alınırsa dağılım bir noktaya çöker ve bağımsız
        # teklif de tek havzaya kilitlenir -- tartı bunu önler.
        wt = tartinin_dayandigi_nokta(self.tampon_L, self.beta_tavlama, taban_ess=0.10)
        wt = wt / (wt.sum() + 1e-300)
        self.kenar = (self.tampon_X * wt[:, None]).sum(0)

        c = DalgaCevrimi(no, esik, mu, k, al, be, p_once, p_sonra,
                   float(Ld.min()), float(tani["kabul_oranı"]), artik,
                   float(self.beta_tavlama), int(len(self.tampon_X)))
        self.seyir.append(c)
        return c

    def kos(self, cevrim: int = 8, **kw) -> Dict[str, object]:
        t0 = time.perf_counter()
        for i in range(cevrim):
            self.cevrim(i, **kw)
        return {"çevrim": cevrim,
                "en_iyi_L": self.en_iyi_deger,
                "en_iyi_x": self.en_iyi_x,
                "süre_sn": time.perf_counter() - t0,
                "seyir": self.seyir}

    # -----------------------------------------------------------------
    def surekli_faz_olcumu(self, gama: float, k: int, ornek: int = 512
                           ) -> Dict[str, float]:
        """**Sürekli** faz orağını (vesikadaki ``e^{−iγL}``) ölçer.

        Eşik orağıyla mukayese içindir: sürekli fazda girişim faz uyumu
        şartına takılır ve yoğunlaşma ikili oraktakinin gerisinde kalır.
        Bu bir tahmin değil, aşağıda **ölçülen** bir şeydir.
        """
        X, _ = self.nqs.ornekle(ornek, tohum=self.tohum + 7)
        Ld = np.asarray(self.L(X), float)
        z = np.exp(-1j * gama * (Ld - Ld.min()))
        m = oragin_donusu("momentler", z=z, k=k)
        a = oragin_donusu("katsayılar", m=m, k=k)
        P = oragin_donusu("polinom", a=a, z=z)
        w = np.abs(P) ** 2
        w = w / (w.sum() + 1e-300)
        duz = np.ones(len(Ld)) / len(Ld)
        return {"γ": gama, "k": float(k),
                "ağırlıklı_L": float(np.dot(w, Ld)),
                "düz_L": float(np.dot(duz, Ld)),
                "en_iyi_L": float(Ld.min()),
                "yoğunlaşma": float(np.dot(w, Ld) - Ld.min())
                / (float(np.dot(duz, Ld) - Ld.min()) + 1e-12)}


# ════════════════════════════════════════════════════════════════════
#  nefs/ikiz.py
# ════════════════════════════════════════════════════════════════════

Sayi = Union[float, int, np.ndarray, "Ikiz"]


@dataclass
class Ikiz:
    """``a + b·ε``  (``ε² = 0``). ``a`` değer, ``b`` türev.

    ``numpy`` dizileriyle beraber çalışır: ``a`` ve ``b`` aynı şekilli
    dizilerdir, yani bir seferde bütün bir tensörün türevi taşınır.
    """
    a: np.ndarray
    b: np.ndarray

    def __post_init__(self) -> None:
        self.a = np.asarray(self.a, float)
        self.b = np.broadcast_to(np.asarray(self.b, float),
                                 self.a.shape).copy()

    # -- cebir ---------------------------------------------------------
    def __add__(self, o: Sayi) -> "Ikiz":
        if isinstance(o, Ikiz):
            return Ikiz(self.a + o.a, self.b + o.b)
        return Ikiz(self.a + np.asarray(o, float), self.b)

    __radd__ = __add__

    def __neg__(self) -> "Ikiz":
        return Ikiz(-self.a, -self.b)

    def __sub__(self, o: Sayi) -> "Ikiz":
        return self + (-o if isinstance(o, Ikiz) else -np.asarray(o, float))

    def __rsub__(self, o: Sayi) -> "Ikiz":
        return (-self) + o

    def __mul__(self, o: Sayi) -> "Ikiz":
        if isinstance(o, Ikiz):
            # (a+bε)(c+dε) = ac + (ad+bc)ε   -- ε² = 0
            return Ikiz(self.a * o.a, self.a * o.b + self.b * o.a)
        c = np.asarray(o, float)
        return Ikiz(self.a * c, self.b * c)

    __rmul__ = __mul__

    def __truediv__(self, o: Sayi) -> "Ikiz":
        if isinstance(o, Ikiz):
            return Ikiz(self.a / o.a,
                        (self.b * o.a - self.a * o.b) / (o.a * o.a))
        c = np.asarray(o, float)
        return Ikiz(self.a / c, self.b / c)

    def __pow__(self, k: float) -> "Ikiz":
        k = float(k)
        return Ikiz(self.a ** k, k * (self.a ** (k - 1.0)) * self.b)

    # -- şekil ---------------------------------------------------------
    def reshape(self, *s) -> "Ikiz":
        return Ikiz(self.a.reshape(*s), self.b.reshape(*s))

    def transpose(self, *s) -> "Ikiz":
        return Ikiz(self.a.transpose(*s), self.b.transpose(*s))

    @property
    def T(self) -> "Ikiz":
        return Ikiz(self.a.T, self.b.T)

    @property
    def shape(self):
        return self.a.shape

    def __getitem__(self, k) -> "Ikiz":
        return Ikiz(self.a[k], self.b[k])

    def sum(self, axis=None) -> "Ikiz":
        return Ikiz(self.a.sum(axis=axis), self.b.sum(axis=axis))

    def __matmul__(self, o: Sayi) -> "Ikiz":
        if isinstance(o, Ikiz):
            return Ikiz(self.a @ o.a, self.a @ o.b + self.b @ o.a)
        c = np.asarray(o, float)
        return Ikiz(self.a @ c, self.b @ c)

    def __rmatmul__(self, o: Sayi) -> "Ikiz":
        c = np.asarray(o, float)
        return Ikiz(c @ self.a, c @ self.b)


def _sar(f: Callable, df: Callable):
    def g(x: Sayi):
        if isinstance(x, Ikiz):
            return Ikiz(f(x.a), df(x.a) * x.b)
        return f(np.asarray(x, float))
    return g


sin = _sar(np.sin, np.cos)


cos = _sar(np.cos, lambda t: -np.sin(t))


tanh = _sar(np.tanh, lambda t: 1.0 - np.tanh(t) ** 2)


exp = _sar(np.exp, np.exp)


log = _sar(np.log, lambda t: 1.0 / t)


sqrt = _sar(np.sqrt, lambda t: 0.5 / np.sqrt(t))


def ikiz(a, b=0.0) -> Ikiz:
    return Ikiz(a, b)


def tam_turev(f=None, p=None, yon=None, ne: str = "yönlü", x=None,
              f_duz=None,
              adimlar: Sequence[float] = (1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6)):
    """PÜRÜZSÜZ TÜREVİ TEK GEÇİŞTE ALMAK -- **tek terkip** (kütük H223).

    Küme: ``deger`` + ``turev`` + ``yonlu_turev`` + ``sonlu_fark_kiyasi``.
    Dördü tek amelin parçalarıydı: ikiz sayının reel kısmını oku, ``ε``
    kısmını oku, ikisini bir ileri geçişte al, ve o türevi sonlu farkla
    yüzleştir.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``değer``       ``x``in reel kısmı
    ``türev``       ``x``in ``ε`` kısmı (ikiz değilse sıfır)
    ``yönlü``       ``(değer, türev)`` -- tek ileri geçişte, ``h`` YOK
    ``kıyas``       tam türevi sonlu farkla yüzleştir
    ==============  ==================================================

    **Sonlu fark kıyasının okunuşu -- iki hâl ve nasıl ayrıldıkları.**

    * **Yüzey pürüzsüz, alet gürültülü.** Sonlu fark, ``h`` büyükken
      kesme hatasıyla, küçükken ``ε/h`` yuvarlamasıyla sapar; arada bir
      ``h``da tam türeve **yaklaşır**. Yani ``|fark − tam|`` bir ``U``
      çizer ve dibi makine hassasiyeti mertebesindedir.
    * **Yüzey pürüzlü.** Sonlu fark hiçbir ``h``da tam türeve yaklaşmaz;
      ``U``nun dibi yoktur ve fark ``h`` küçüldükçe **artmaya devam
      eder**.

    H88'in bıraktığı sual tam olarak budur ve ancak bu yüzleştirmeyle
    cevaplanır.
    """
    def dg(z):
        return z.a if isinstance(z, Ikiz) else np.asarray(z, float)

    def tr(z):
        return (z.b if isinstance(z, Ikiz)
                else np.zeros_like(np.asarray(z, float)))

    if ne == "değer":
        return dg(x)
    if ne == "türev":
        return tr(x)

    pv = np.asarray(p, float)
    vv = np.asarray(yon, float)
    r = f(Ikiz(pv, vv))
    tam_v = float(np.ravel(dg(r))[0])
    tam_d = float(np.ravel(tr(r))[0])
    if ne == "yönlü":
        return tam_v, tam_d
    if ne != "kıyas":
        raise ValueError("türev kipi bilinmiyor: %r" % (ne,))

    satir = []
    for h in adimlar:
        mer = (float(f_duz(pv + h * vv)) - float(f_duz(pv - h * vv))) / (2.0 * h)
        satir.append({"h": float(h), "merkezî_fark": mer,
                      "fark": abs(mer - tam_d)})
    en_iyi = min(satir, key=lambda z: z["fark"])
    return {"tam_değer": tam_v, "tam_türev": tam_d,
            "satır": satir, "en_yakın": en_iyi,
            # Dip makine hassasiyeti mertebesindeyse yüzey pürüzsüzdür.
            "pürüzsüz_mü": bool(en_iyi["fark"]
                                <= 1e-5 * max(abs(tam_d), 1.0))}


def purzu_yerini_bul(tohum: int = 0, n: int = 8, chi: int = 4
                     ) -> Dict[str, object]:
    """H88'in sualini iki kademede cevapla: **kapı mı, kesme mi?**

    1. **Yalnız kapı kurulumu.** ``exp(−2A)`` ile kurulan ``SO(4)``
       kapısı açıya göre türevlenebilir mi? İkiz sayı doğrudan geçer.
    2. **Kesme.** SVD budaması bir **sıralamadır**; sıralama değişince
       fonksiyon sıçrar. İkiz sayı oraya **giremez** ve girememesi
       delilin kendisidir.

    Burada 1. kademe fiilen ölçülür; 2. kademe için sıralamanın kaç
    kere değiştiği sayılır -- sıçrama sayısı doğrudan pürüzün ölçüsüdür.
    """
    from kuantum.yazmac import _so4_ureteci

    rng = np.random.default_rng(tohum)
    t0 = rng.normal(size=6)
    yon = rng.normal(size=6)

    # --- 1. kademe: kapı kurulumu türevlenebilir mi
    def kapi_izi(teta):
        """``Tr(exp(−2A(θ)))`` -- skalerdir, ikiz sayı ile tam türevlenir.

        ``expm``i seriyle açarız; ``A`` küçükse yakınsar ve **her adımı
        ikiz sayı ile** yürür, yani türev de tam alınır.
        """
        A = _ureteci_ikiz(teta)
        M = _birim_gibi(A)
        T = _birim_gibi(A)
        for k in range(1, 18):
            T = (T @ A) * (-2.0 / k)
            M = M + T
        return _iz(M)

    def kapi_izi_duz(teta):
        A = _so4_ureteci(np.asarray(teta, float))
        M = np.eye(4)
        T = np.eye(4)
        for k in range(1, 18):
            T = (T @ A) * (-2.0 / k)
            M = M + T
        return float(np.trace(M))

    k1 = tam_turev(lambda z: kapi_izi(z), t0, yon, "kıyas", f_duz=kapi_izi_duz)

    # --- 2. kademe: kesme sınırında tekil değerler KESİŞİYOR mu
    #
    # **İlk denemem yanlış ölçüyordu ve sıfır çıktı.** ``bag_ust``
    # desenine bakmıştım; o desen bağın **üst sınırıdır** ve tarama
    # boyunca hiç değişmez, yani ölçüt kördü (H90: kırmızı yanamayan
    # ölçüt, ölçüt değildir).
    #
    # Doğru ölçü şudur: kesme, ``s[r−1]`` ile ``s[r]`` arasından
    # geçen bir **sıralamadır**. O iki tekil değer birbirine yaklaşıp
    # yer değiştirdiğinde tutulan altuzay **sıçrar** ve fonksiyon
    # türevlenemez hâle gelir. Yani aranan şey ``s[r−1] − s[r]``
    # boşluğunun sıfıra ne kadar yaklaştığıdır.
    from kuantum.yazmac import Yazmac, dik_iki_kubit
    bosluklar = []
    buyuk = []
    kesme_say = 0
    for s in np.linspace(0.0, 1.0, 41):
        y = Yazmac(n, bag=chi, tohum=tohum)
        y.superpozisyona_sok()
        r2 = np.random.default_rng(tohum)
        for t in range(10):
            y.cift_kapi(dik_iki_kubit(r2.normal(size=6) * 0.8
                                      + s * yon[:6] * 0.5), ofset=t % 2)
        # Boşluk yalnız **kesme anında** görünür; yazmaç onu zabıtlıyor.
        if y._kesme_sayisi:
            bosluklar.append(float(y._kesme_bosluk))
            buyuk.append(float(y._kesme_buyukluk))
            kesme_say += int(y._kesme_sayisi)
    yakin = int(sum(1 for b in bosluklar if b < 1e-2))
    return {"kapı_pürüzsüz_mü": k1["pürüzsüz_mü"],
            "kapı_tam_türev": k1["tam_türev"],
            "kapı_en_yakın_fark": k1["en_yakın"]["fark"],
            "kapı_en_iyi_h": k1["en_yakın"]["h"],
            "kesme_boşluğu_ölçüldü": len(bosluklar),
            "kesme_sayısı": kesme_say,
            "kesme_sınırı_yakın": yakin,
            "en_dar_boşluk": (float(min(bosluklar)) if bosluklar
                              else float("nan")),
            "sınır_büyüklüğü": (float(min(buyuk)) if buyuk
                                else float("nan")),
            "tarama_noktası": 41}


def _ureteci_ikiz(teta: Ikiz) -> Ikiz:
    """``_so4_ureteci``nin ikiz sayı hâli -- aynı yerleşim, aynı işaret."""
    z = Ikiz(np.zeros(()), np.zeros(()))
    A_a = np.zeros((4, 4))
    A_b = np.zeros((4, 4))
    t_a, t_b = tam_turev(ne="değer", x=teta), tam_turev(ne="türev", x=teta)
    ind = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    for k, (i, j) in enumerate(ind):
        A_a[i, j] += t_a[k]
        A_a[j, i] -= t_a[k]
        A_b[i, j] += t_b[k]
        A_b[j, i] -= t_b[k]
    return Ikiz(A_a, A_b)


def _birim_gibi(A: Ikiz) -> Ikiz:
    return Ikiz(np.eye(A.shape[0]), np.zeros(A.shape))


def _iz(M: Ikiz) -> Ikiz:
    n = M.shape[0]
    return Ikiz(np.trace(M.a), np.trace(M.b))




# ════════════════════════════════════════════════════════════════════
#  nefs/ogda.py
# ════════════════════════════════════════════════════════════════════

@dataclass
class OgdaTarti:
    """Uzuv ağırlıklarını **hafızayla** taşıyan düşman tarafı.

    Hâli tek bir şeydir: simpleks üstünde ``w`` ve bir evvelki
    gradyan ``g_önceki``. "İyimserlik" o hafızadan gelir.
    """
    n: int
    beta: float = 8.0
    adim: float = 0.5
    w: Optional[np.ndarray] = None
    g_onceki: Optional[np.ndarray] = None
    tur: int = 0

    def __post_init__(self) -> None:
        if self.w is None:
            self.w = np.full(int(self.n), 1.0 / max(int(self.n), 1))
        if self.g_onceki is None:
            self.g_onceki = np.zeros(int(self.n))

    # -----------------------------------------------------------------
    def guncelle(self, eksikler: Sequence[float]) -> np.ndarray:
        """Bir OGDA adımı; yeni ağırlıkları döndürür.

        ``∂/∂w [⟨w,e⟩ + H(w)/β] = e``  (entropi kısmı izdüşümde işlenir).
        İyimser adım ``2g_t − g_{t−1}``dir: bir evvelki gradyanı iki
        kere saymak, karşı tarafın **cevabını öngörmek** demektir ve
        GDA'nın ıraksamasını kesen şey odur.

        İzdüşüm çarpımsaldır (aynalı iniş / çoğaltmalı ağırlık)::

            w ← w · exp(η·ĝ)   sonra normalize

        Çarpımsal olması entropi düzenleyicisinin **kendi** izdüşümüdür;
        Öklit izdüşümü kullanılsaydı hedefle uyuşmazdı.
        """
        g = np.asarray(eksikler, float).reshape(-1)
        if g.size != self.w.size:                     # uzuv sayısı değişti
            self.w = np.full(g.size, 1.0 / max(g.size, 1))
            self.g_onceki = np.zeros(g.size)
        iyimser = 2.0 * g - self.g_onceki
        z = np.log(np.maximum(self.w, 1e-300)) + float(self.adim) * iyimser
        z -= float(np.max(z))
        w = np.exp(z)
        t = float(np.sum(w))
        self.w = w / t if t > 0 else np.full(g.size, 1.0 / g.size)
        self.g_onceki = g
        self.tur += 1
        return self.w


def oyun_degeri(eksikler: Sequence[float], beta: float = 8.0,
                w: Optional[np.ndarray] = None) -> float:
    """OYUNUN DEĞERİ -- **tek terkip** (kütük H223).

    Küme: ``oyun_degeri`` + ``OgdaTarti.deger``. İkisi **aynı sayının**
    iki okunuşuydu ve ayrı durdukları için aralarındaki özdeşlik
    görünmüyordu; ``rapor()`` onları yüzleştirmek için üçüncü bir yerde
    tekrar hesaplıyordu. Terkipte tek gövde, tek formül::

        max_{w∈Δ} [⟨w,e⟩ + H(w)/β]  =  (1/β)·log Σ exp(β·e_i)

    * ``w`` verilmezse **kapalı form** -- yumuşak azamînin ta kendisi.
    * ``w`` verilirse o ağırlıkta oyunun değeri ``⟨w,e⟩ + H(w)/β``.

    ``β → ∞``da bu, ``w``nin çöktüğü uzvun eksiğidir (sert azamî);
    ``β → 0``da ortalamadır. Yani sabit ``β``lı yumuşak azamî bu değerin
    **kapalı formda çözülmüş** hâlidir; OGDA aynı değeri **yürüyerek**
    bulur ve yolda hafıza taşır. İki taraf tutmazsa bu dosyadaki bütün
    şerh **yanlış** demektir ve ölçüm onu gösterir.
    """
    e = np.asarray(eksikler, float).reshape(-1)
    b = float(max(beta, 1e-9))
    if w is None:
        m = float(np.max(b * e))
        return float((m + np.log(np.sum(np.exp(b * e - m)))) / b)
    ww = np.asarray(w, float).reshape(-1)
    ww = ww[:e.size] if ww.size >= e.size else np.full(e.size, 1.0 / e.size)
    ww = ww / max(float(ww.sum()), 1e-300)
    nz = ww > 0
    H = float(-np.sum(ww[nz] * np.log(ww[nz])))
    return float(np.dot(ww, e) + H / b)




# ════════════════════════════════════════════════════════════════════
#  nefs/tabii_gradyan.py
# ════════════════════════════════════════════════════════════════════

KayipTek = Callable[[np.ndarray], float]          # (n,) → skaler


@dataclass
class TabiiAyar:
    r: int = 8                  # alt uzay boyutu
    h: float = 1e-2             # sonlu fark adımı
    eta: float = 1.0            # başlangıç adım boyu (çizgi araması küçültür)
    lam: float = 1e-3           # Fisher düzenlileştirmesi
    geri_adim: int = 7          # çizgi aramasında kaç kere yarıya böl
    cevrim: int = 12
    tohum: int = 0
    metrik: bool = True         # False → sıradan gradyan (mukayese için)


@dataclass
class TabiiCevrim:
    no: int
    V: float
    grad_normu: float
    adim_normu: float
    fisher_kosul: float
    kabul: bool
    cagri: int


class TabiiGradyan:
    """Fubini–Study metriğiyle alt uzayda tabiî gradyan inişi.

    ``durum_kur(p) -> Yazmac`` verilirse metrik **fiilen** ölçülür;
    verilmezse metrik birim alınır ve motor sıradan gradyana döner --
    o hâlde ``metrik=False`` ile aynıdır ve rapor bunu yazar.
    """

    def __init__(self, V: KayipTek, p0: np.ndarray,
                 durum_kur: Optional[Callable[[np.ndarray], object]] = None,
                 ayar: Optional[TabiiAyar] = None) -> None:
        self.V = V
        self.p = np.asarray(p0, float).copy()
        self.durum_kur = durum_kur
        self.ayar = ayar or TabiiAyar()
        self.seyir: List[TabiiCevrim] = []
        self.cagri = 0
        self.en_iyi = float("inf")
        self.en_iyi_p = self.p.copy()

    # -----------------------------------------------------------------
    def _yonler(self, no: int) -> np.ndarray:
        """``r`` dik yön: ilki önceki adım, gerisi rastgele.

        Önceki adımı alt uzaya koymak bedavadır ve momentumun tabiî
        karşılığıdır: dün faydalı olan yön bugün de aranır.
        """
        a = self.ayar
        rng = np.random.default_rng(a.tohum + 977 * no)
        d = len(self.p)
        M = rng.normal(size=(d, a.r))
        if self.seyir and getattr(self, "_son_adim", None) is not None:
            s = self._son_adim
            if np.linalg.norm(s) > 1e-12:
                M[:, 0] = s
        Q, _ = np.linalg.qr(M)
        return Q[:, :a.r]


    # -----------------------------------------------------------------
    def cevrim(self, no: int) -> Cevrim:
        a = self.ayar
        W = self._yonler(no)
        V0 = self.V(self.p)
        self.cagri += 1

        # yönlü türevler -- merkezî sonlu fark
        g = np.empty(a.r)
        for i in range(a.r):
            vp = self.V(self.p + a.h * W[:, i])
            vm = self.V(self.p - a.h * W[:, i])
            self.cagri += 2
            g[i] = (vp - vm) / (2.0 * a.h)

        kosul = float("nan")
        if a.metrik and self.durum_kur is not None:
            S, kosul = yokus(ne="örtüşme", teta=self.p, W=W,
                          h=self.ayar.h, durum_kur=self.durum_kur)
            # ``(S + λI)⁻¹ g``: λ hem tekilliği hem çok küçük özdeğerleri
            # (yani durumu neredeyse hiç değiştirmeyen yönleri) frenler.
            delta = np.linalg.solve(S + a.lam * np.eye(a.r), g)
        else:
            delta = g

        # --- ÇİZGİ ARAMASI (geri adımlı).
        #
        # **Niçin şart.** Çizgi araması olmadan kuruldu ve ölçüldü:
        # gradyan normu 1064, adım normu 3,7e+05 çıkıyor ve DÖRT
        # çevrimin dördünde de adım reddediliyordu. Sebep, kaybın
        # ``−log P`` terimidir: ``P`` sıfıra yaklaşınca yüzey uçurum
        # gibi olur ve sabit adım daima uçurumun ötesine düşer.
        #
        # Yön doğruysa **yeterince küçük** bir adımda iyileşme olmak
        # zorundadır; olmuyorsa yüzey o noktada pürüzsüz değildir ve bu
        # da bir ölçümdür, gizlenmez (``kabul=False`` olarak durur).
        yon = -(W @ delta)
        nrm = float(np.linalg.norm(yon))
        if nrm > 1e-12:
            yon = yon / nrm
        adim = np.zeros_like(yon)
        V1 = V0
        kabul = False
        eta = a.eta
        for _ in range(max(1, a.geri_adim)):
            aday = self.p + eta * yon
            Va = self.V(aday)
            self.cagri += 1
            if Va < V0:
                adim, V1, kabul = eta * yon, Va, True
                break
            eta *= 0.5
        if kabul:
            self.p = self.p + adim
            self._son_adim = adim
        if V1 < self.en_iyi:
            self.en_iyi = float(V1)
            self.en_iyi_p = self.p.copy()

        c = TabiiCevrim(no, float(V1), float(np.linalg.norm(g)),
                   float(np.linalg.norm(adim)), kosul, kabul, self.cagri)
        self.seyir.append(c)
        return c

    def kos(self, cevrim: Optional[int] = None) -> Dict[str, object]:
        t0 = time.perf_counter()
        for i in range(cevrim or self.ayar.cevrim):
            self.cevrim(i)
        return {"V_son": self.en_iyi, "p": self.en_iyi_p,
                "çağrı": self.cagri, "süre_sn": time.perf_counter() - t0,
                "seyir": self.seyir,
                "metrik": bool(self.ayar.metrik and self.durum_kur is not None)}


# ════════════════════════════════════════════════════════════════════
#  nefs/gaye.py
# ════════════════════════════════════════════════════════════════════

EPSILON_DURGUN: float = 0.45


def gaye_kos(q: QYazmac, p) -> float:
    """Gayeyi **doğur**, mîzâna sirayet ettir, sükût eşiğini kur.

    Akışta 41 melekeden sonra, `tertip` ile `sadakat_intaci` arasında
    koşar. Kesme miktarını döndürür.
    """
    kesme = 0.0

    # --- 1) DOĞUŞ: hüküm alanları ``gaye``ye akar.
    # ``mpo_topla`` durakların hedefin SOLUNDA olmasını ister; küllî
    # blokta ``gaye`` zaten tasdik/tenakuz/nakz'ın sağındadır.
    kaynaklar = [q.kulli("tasdik", 0), q.kulli("tasdik", 1),
                 q.kulli("tenakuz", 0), q.kulli("nakz", 0)]
    # --- 1a) ÇALIŞMA NOKTASI: gaye evvelâ ``π/4``e çevrilir.
    #
    # **H122'NİN KÜNHÜ BURADAYDI VE EVVELCE BULAMAMIŞTIM.** Aşağıdaki
    # şerh "işaretle bastırma olmaz, zira ``P(1) = sin²θ`` çifttir"
    # diyor. Teşhis doğru, fakat **eksikti**: mesele işaretin değil,
    # **çalışma noktasının** meselesiymiş.
    #
    # ``gaye`` ``|0⟩``da, yani ``θ = 0``da duruyordu. Orada ``sin²``in
    # türevi **sıfır** ve fonksiyon çifttir; ``−θ`` ile ``+θ`` aynı
    # nüfusu verir. Yani nakz tek başına geldiğinde gayeyi
    # **yükseltiyordu** -- ölçülen ``+0,871`` tam olarak budur.
    #
    # ``θ₀ = π/4``te ise ``sin²(π/4 + x) = (1 + sin 2x)/2``: türev
    # âzamî, fonksiyon x'te **tek**, yani müsbet açı yükseltir, menfî
    # açı **düşürür**. Aynı MPO, aynı işaretler; yalnız kolun
    # duracağı yer değişti.
    #
    # Bu bir okuma değildir: sabit bir tek kübitlik dönmedir, veriye
    # bakmaz (H31 yerinde durur).
    q.tek(q.kulli("gaye", 0), donme(0.25 * math.pi))
    # --- EVVELKİ ŞERH, NAKZEDİLMİŞ HÂLİYLE DURUYOR (silinmiyor):
    #
    #   > "Bu satır evvelce ``işaret = [+1,+1,−1,−1]`` taşıyordu…
    #   >  ölçüldü ve çalışmadı -- korelasyon ``+0,871``. Sebep bir
    #   >  kodlama hatası değil, kendi kütüğümde yazılı bir
    #   >  imkânsızlıktır (H107): ``P(1) = sin²θ`` çift fonksiyondur…
    #   >  **İşaretle bastırma olmaz.**"
    #
    # Son cümle **fazla genelleştirilmiş bir hükümdü ve nakzedildi**
    # (H159). İşaretle bastırma ``θ = 0``da olmaz; ``θ = π/4``te
    # **olur**. O zaman "mutlak açı al, sönmeyi girişime bırak" diye
    # kurduğum çare de gereksizdi: derdi çözmüyordu (ölçüldü, +0,887)
    # çünkü dert kolda değil çalışma noktasındaydı.
    #
    # İşaretler artık İŞ GÖRÜYOR (yukarıdaki çalışma noktası sayesinde):
    # tasdik gayeyi doğurur, tenakuz ve nakz **zayıflatır**.
    #
    # Açılar ``(π/16)·tanh`` ile sınırlanır ve sebebi cebridir: dört
    # kaynak var, her biri en çok ``π/16`` katkı verirse toplam ``π/4``i
    # aşamaz ve kol ``[0, π/2]`` penceresinden **çıkmaz**. Çıksaydı
    # ``sin²`` sarılır, tek olmaktan çıkar ve az evvel kurulan işaret
    # duyarlılığı geri kaybolurdu -- yani had bir ihtiyat değil,
    # tashihin şartıdır.
    # ``abs`` ŞARTTIR ve müdahaleli ölçümle bulundu: ``_aci`` müsbet
    # değil, **işaretli** bir parametre döndürür. ``tanh``ın işareti
    # sınıfın işaretini yiyordu -- tohum 0'da tasdik açıları menfî
    # çıkmış ve tasdik gayeyi ``−0,000991`` kadar **düşürmüştü**.
    # Yani sınıf taahhüdü, öğrenilen sayının rastgele işaretine
    # tâbiydi. Cihet **yapısaldır** (sınıftan gelir), şiddet
    # **öğrenilir** (parametreden); ikisi karıştırılmaz.
    isaret = np.array([+1.0, +1.0, -1.0, -1.0])
    ham = np.asarray(_aci(p, "gaye.dogus", 4, 0.8), float)
    a = isaret * (math.pi / 16.0) * np.abs(np.tanh(ham))
    kesme += q.mpo_topla("gaye", a, duraklar=kaynaklar, j=0)

    # --- 1b) YASAK TERKİPLER: nakzedilmiş yahut çelişkili bir hükümden
    # doğan gaye **mantık dışıdır** ve işaretlenir. Sönmesi akışın
    # sonundaki ``sadakat_intaci`` yansıtmasına bırakılır -- yansıtma
    # ``gaye`` ve ``nakz``ı zaten kapsıyor.
    #
    # **VE BU DA İSTENEN NETİCEYİ VERMEDİ -- ölçüldü, saklanmıyor.**
    # 14 ayrı girdide gaye-nakz korelasyonu ``+0,871``den ``+0,887``ye
    # gitti, yani hiç değişmedi. İşaret duruyor (meşrudur ve bedeli
    # yoktur) fakat derdi **çözmüyor** ve çözdüğü iddia edilmiyor.
    #
    # Sebebi anlaşıldı: bu bir kol meselesi değil, **inşa seviyesinde**
    # bir bağımlılıktır. ``mpo_topla`` gayeye ``R(Σθᵢnᵢ)`` uygular ve
    # bütün ``θᵢ`` müsbet olduğu için ``P(gaye=1)``, tasdik + tenakuz +
    # nakz **faaliyetinin toplamıyla** büyür. Bu girdilerde en çok
    # değişen alan nakz olduğu için korelasyonu da o götürüyor. Tek bir
    # işaretli kolu ``2¹⁵`` kol arasında tek turluk bir yansıtmayla
    # söndürmek, marjinali bu kadar oynatamaz.
    #
    # Yani "nakz gayeyi zayıflatır" **hâlâ icra edilmiş değildir** ve
    # kütükte borç olarak durur (H122). Şu an fiilen olan şudur ve
    # dürüstçe böyle yazılır: *gaye, hükmün faaliyetinden doğar* --
    # hangi hükmün olduğuna bakmadan.
    CZ = np.eye(4)
    CZ[3, 3] = -1.0
    gay0 = q.kulli("gaye", 0)
    q.uzak_cift(q.kulli("nakz", 0), gay0, CZ)        # |nakz=1, gaye=1⟩
    q.uzak_cift(q.kulli("tenakuz", 0), gay0, CZ)     # |tenakuz=1, gaye=1⟩

    # --- 2) TESİR: gaye mîzânı büker (teleolojik çekici).
    b = _aci(p, "gaye.mizan", 4, 0.6)
    kesme += q.mpo_dagit("gaye", b,
                         duraklar=[q.kulli("mizan", j) for j in range(4)],
                         j=0)

    # --- 3) SÜKÛT EŞİĞİ: gaye uyanıksa sükût BASTIRILIR.
    # İşaret menfîdir ve sebebi budur: takip edilecek bir gaye doğduysa
    # susmak yanlıştır; gaye doğmadıysa (``|0⟩``) kontrol kapalıdır ve
    # sükût evvelki hâlinde kalır -- yani susmak varsayılan olur.
    #
    # **ÖLÇÜLEN VE DÜZELTİLEN KUSUR.** Bu satır ``j=1`` yazıyordu, yani
    # kapıyı ``gaye₁``e kontrol ediyordu -- halbuki doğuş yalnız
    # ``gaye₀``a yazıyor; ``gaye₁`` ``|0⟩``da kalıyor. Kontrolü ``|0⟩``
    # olan kontrollü dönme **hiçbir şey yapmaz**, yani sükût eşiği hiç
    # ateşlenmiyordu. Sessizdi: 6 satırlık bir ölçümde korelasyon
    # ``−0,63`` çıkıp "çalışıyor" görünüyordu, 5 satırda ``+0,77``ye
    # dönüyordu -- yani gördüğüm şey eşik değil gürültüydü.
    #
    # **VE AYNI KUSUR SÜKÛT UCUNDA DA VARDI (H159, müdahaleli ölçüm).**
    # Kapı düzeltildikten sonra ölçüldü::
    #
    #     tenakuz+nakz açık : gaye₀=0,3918  sükût=0,0741
    #     tasdik açık       : gaye₀=0,4990  sükût=0,0944
    #
    # Yani gaye **düşünce** sükût da düşüyordu -- taahhüdün tam tersi.
    # Sebep gayedeki ile aynı: ``sukut`` küçük bir açıda duruyor,
    # ``sin²`` orada çift, ve ``R(−ε)`` nüfusu düşürmek yerine
    # yükseltebiliyor. Çare de aynı: sükûtu evvelâ ``π/4``e çevir,
    # kapıyı **oradan** vur.
    q.tek(q.kulli("sukut", 0), donme(0.25 * math.pi))
    kesme += q.mpo_dagit("gaye", [-abs(EPSILON_DURGUN)],
                         duraklar=[q.kulli("sukut", 0)], j=0)
    return float(kesme)


def _aci(p, anahtar: str, n: int, olcek: float) -> np.ndarray:
    """Öğrenilen açı dilimi -- melekelerinkiyle aynı defterden."""
    from nefs.melekeler import QParametre
    if isinstance(p, QParametre):
        return olcek * p.al(anahtar, n)
    return olcek * p.v(anahtar, n)


def odenen_bedel(q: QYazmac, ne: str = "landauer") -> Dict[str, float]:
    """AKIŞTA NE ÖDENDİ -- **tek terkip** (kütük H223).

    Küme: ``landauer_defteri`` + ``serbest_enerji_olcumu``. İkisi de tek
    suali soruyor: **bu akış neye mal oldu?** Biri bedeli termodinamik
    (silinen bit, Landauer), öteki bilgi-geometrik (serbest enerji)
    cinsten okur; ikisi de ``q``nun aynı marjinallerinden çıkar.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``landauer``    silinen bit ve ``kT ln2`` bedeli
    ``serbest``     ``F = kesinsizlik + karmaşıklık`` ayrışımı
    ==============  ==================================================

    **Landauer.** Bütün kapılar dik, yani tersinirdir; tek tersinmez
    adım kesmedir. ``F = Π (tutulan/tam)`` olduğuna göre silinen bit
    ``−log₂F``dir. ``kT ln2`` bir birim seçimidir; burada ``kT = 1``
    alınır ve sayı **nat** cinsinden de verilir ki birim tartışması
    hükmü değiştirmesin.

    **Serbest enerji.** Gayeyi bir gizli değişken ``z``, hükmü gözlem
    ``x`` sayarız::

        p(z) = gaye alanının marjinali
        q(z) = tasdik alanının marjinali   (hükmün "istediği")

    Ayrışım `fitrat`ın kendi koduyla hesaplanır -- yani bu ölçüm ana
    hattı **beylik bir kütüphaneyle** denetler, tıpkı `nefs/golge.py`
    gibi. **Bu bir hüküm değil bir ölçüdür**: "gaye serbest enerjiyi
    düşürüyor" diye bir iddia burada YOKTUR; sayı çıkar, hüküm
    `tanilama` tarafında iki koşu kıyaslanarak verilir.
    """
    if ne == "landauer":
        F = float(q.y.sadakat())
        bit = -math.log2(max(F, 1e-300))
        return {
            "sadakat": F,
            "silinen_bit": bit,
            "landauer_nat": bit * math.log(2.0),      # kT=1 iken enerji
            "kübit": float(q.n),
            "kübit_başına_bit": bit / max(q.n, 1),
        }
    if ne != "serbest":
        raise ValueError("bedel kipi bilinmiyor: %r" % (ne,))
    from matematik.fitrat import AyrikModel, kl, serbest_enerji_ayrisimi

    def marjinal(ad: str) -> np.ndarray:
        _, kac = q._alan[ad]
        yuv = [q.kulli(ad, j) for j in range(kac)]
        R = np.asarray(q.y.tekil_yogunluklar(yuv), float)[0]
        v = np.clip(R[:, 1, 1], 1e-9, 1.0 - 1e-9)
        v = np.concatenate([v, [1e-9]])          # sıfır ihtimali kapat
        return v / v.sum()

    pz = marjinal("gaye")
    qz = marjinal("tasdik")
    k = min(pz.size, qz.size)
    pz, qz = pz[:k] / pz[:k].sum(), qz[:k] / qz[:k].sum()

    # ``p(x|z)``: hükmün gaye şartındaki olabilirliği. Elde tek bir
    # durum olduğu için köşegen-ağırlıklı bir tablo kurulur; maksat
    # `fitrat`ın ayrışım kimliğini bu sayılar üzerinde İŞLETMEKtir.
    N = k
    pxz = np.full((k, N), 1.0 / N)
    np.fill_diagonal(pxz, 0.0)
    pxz = pxz + np.eye(k, N) * 0.5
    pxz = pxz / pxz.sum(axis=1, keepdims=True)

    m = AyrikModel(pz=pz, pxz=pxz)
    a = serbest_enerji_ayrisimi(m, qz, 0)
    return {
        "F": float(a["F"]),
        "kesinsizlik": float(a["kesinsizlik"]),
        "karmaşıklık": float(a["karmaşıklık"]),
        "ayrışım_sapması": float(a["ayrışım_sapması"]),
        "KL(tasdik‖gaye)": float(kl(qz, pz)),
    }




# ════════════════════════════════════════════════════════════════════
#  ogrenme/optimize.py
# ════════════════════════════════════════════════════════════════════

def hareketin_altuzayi(f=None, x0=None, n_ornek: int = 24, r: int = 2,
                       h: float = 1e-3, tohum: int = 0, ne: str = "bul",
                       onceki=None, simdiki=None):
    """HAREKET HANGİ ALT UZAYDA -- **tek terkip** (kütük H223).

    Küme: ``aktif_altuzay`` + ``KulliOptimizer._durgunluk``. İkisi de
    aynı nesneyi -- kaybın fiilen kımıldadığı alt uzayı -- konuşur:
    biri onu **bulur**, öteki iki turun alt uzayları arasındaki **asal
    açıyı** ölçer. Ayrı yerlerde durdukları için birinin kurduğu tabanı
    öteki yeniden kuruyordu.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``bul``         ``(W₁, özdeğerler, G)`` -- ``C = 1/N Σ g gᵀ``nin
                    en büyük ``r`` özyönü
    ``fark``        iki alt uzay arasındaki Grassmann asal açısı
    ==============  ==================================================

    Gradyanlar **rastgele yönlü sonlu farkla** alınır: ``d`` boyutlu tam
    gradyan ``2d`` değerlendirme ister; burada ``n_ornek`` yönle
    yetinilir ve kovaryans onlardan kurulur. Bu, tam gradyanın tarafsız
    bir örneklemesidir (Gauss yönlerde ``E[gvᵀ] = ∇f``).

    Asal açı, *"kayıp düşmüyor"*dan **daha erken ve daha kesin** bir
    durgunluk alâmetidir: kayıp gürültülüdür, alt uzay değildir.
    """
    if ne == "fark":
        if onceki is None:
            return 1.0
        from ogrenme.grassmann import dik_taban, grassmann_mesafesi
        return float(grassmann_mesafesi(dik_taban(onceki),
                                        dik_taban(simdiki)))
    if ne != "bul":
        raise ValueError("alt uzay kipi bilinmiyor: %r" % (ne,))
    rng = np.random.default_rng(tohum)
    d = len(x0)
    G = np.zeros((n_ornek, d))
    for i in range(n_ornek):
        v = rng.normal(size=d)
        v /= np.linalg.norm(v) + 1e-12
        turev = (f(x0 + h * v) - f(x0 - h * v)) / (2 * h)
        G[i] = turev * v                       # yönlü türev · yön
    C = G.T @ G / n_ornek
    w, U = np.linalg.eigh(C)
    idx = np.argsort(-w)
    return U[:, idx[:r]], w[idx], G


def _tavla_govdesi(enerji, D0, adim, s_hedef, ust_sinir, tohum):
    """Tersine tavlamanın gövdesi -- şerhi terkiptedir."""
    rng = np.random.default_rng(tohum)
    D = list(int(x) for x in D0)
    E = enerji(tuple(D))
    en_iyi, E_iyi = list(D), E
    for t in range(adim):
        s = 1.0 - (1.0 - s_hedef) * np.sin(np.pi * (t + 1) / adim)
        genlik = max(1, int((1.0 - s) * 2000))
        j = int(rng.integers(len(D)))
        aday = list(D)
        aday[j] = int(np.clip(aday[j] + rng.integers(-genlik, genlik + 1),
                              10, ust_sinir))
        E_aday = enerji(tuple(aday))
        # tünelleme: bariyerin YÜKSEKLİĞİ değil GENİŞLİĞİ belirler
        genislik = abs(aday[j] - D[j]) / (genlik + 1.0)
        p_tunel = float(np.exp(-genislik * max(E_aday - E, 0.0)))
        if E_aday < E or rng.random() < p_tunel:
            D, E = aday, E_aday
            if E < E_iyi:
                en_iyi, E_iyi = list(D), E
    return tuple(en_iyi), E_iyi


def ayrik_mertebede_sicra(tikaniklik=None, mevcut=None,
                          enerji=None, D0=None, adim: int = 60,
                          s_hedef: float = 0.6, ust_sinir: int = 100000,
                          tohum: int = 0, ne: str = "tavla"):
    """AYRIK MERTEBEDE SIÇRAMAK -- **tek terkip** (kütük H223).

    Küme: ``postnikov_adresi`` + ``tersine_tavlama``. İkisi tek amelin
    iki yarısıdır: **nereye** sıçranacağını kohomolojik tıkanıklık
    söyler, **nasıl** sıçranacağını tersine tavlama yürütür.

    ==============  ==================================================
    ``ne``          döndürdüğü
    ==============  ==================================================
    ``adres``       açılacak mertebenin adresi (tek tam sayı)
    ``tavla``       ``(D*, E*)`` -- ayrık mertebe vektöründe en iyi
    ==============  ==================================================

    ``H^n ≠ 0`` ise Postnikov kulesinde bir sonraki bütünlük mertebesi
    ``k^{n+1} ∈ H^{n+1}(X; π_n(X))`` sınıfıyla adreslenir. Kör arama
    yoktur: en büyük tıkanıklığı taşıyan mertebe ``n``, tıkanıklığın
    şiddetiyle ölçeklenen bir sıçrama üretir (kütük H28).

    Tavlamada sıfırdan süperpozisyonla başlanmaz (klasik tavlamanın
    ölçeklenme derdi budur); **eldeki aday** ``D0``a kilitlenip etrafında
    enine alan ``s: 1 → s_hedef → 1`` döngüsüyle kontrollü dalgalanma
    açılır. Dar duvarın ardındaki daha derin taban bulunursa oraya
    tünellenir.
    """
    if ne == "adres":
        if not tikaniklik:
            return int(mevcut[0]) if mevcut else 13
        n = max(tikaniklik, key=lambda k: tikaniklik[k])
        adres = int(round((n + 1) * (1.0 + 9.0 * float(tikaniklik[n]))))
        return int(np.clip(adres, 10, ust_sinir))
    if ne != "tavla":
        raise ValueError("sıçrama kipi bilinmiyor: %r" % (ne,))
    return _tavla_govdesi(enerji, D0, adim, s_hedef, ust_sinir, tohum)


def gek_uydur(U: np.ndarray, y: np.ndarray, lam: float = 1e-6,
              nystrom: int = 0) -> Callable[[np.ndarray], np.ndarray]:
    """Gradyan destekli Kriging -- kapalı form, gradyan inişi yok.

    ``α = (K + λI)⁻¹ y``; ``K`` Gauss çekirdeği, genişlik medyan
    sezgisiyle. ``nystrom > 0`` ise ``M ≪ N`` temsilci nokta seçilip
    ``K ≈ K_NM K_MM⁻¹ K_NMᵀ`` düşük dereceli açılımı kullanılır -- matris
    tersi maliyeti ``O(N³)``ten ``O(N M²)``ye iner (kütük H28/H12).
    """
    U = np.atleast_2d(U)
    n = len(U)
    D2 = ((U[:, None, :] - U[None, :, :]) ** 2).sum(-1)
    med = float(np.median(D2[np.triu_indices(n, 1)])) if n > 1 else 1.0
    gam = 1.0 / (2.0 * med) if med > 0 else 1.0
    K = np.exp(-gam * D2)

    if nystrom and nystrom < n:
        idx = np.linspace(0, n - 1, nystrom).astype(int)
        Kmm = K[np.ix_(idx, idx)] + lam * np.eye(nystrom)
        Knm = K[:, idx]
        A = Knm.T @ Knm + lam * Kmm
        alfa_m = np.linalg.solve(A, Knm.T @ y)
        merkez = U[idx]

        def vekil(u: np.ndarray) -> np.ndarray:
            u = np.atleast_2d(u)
            d2 = ((u[:, None, :] - merkez[None, :, :]) ** 2).sum(-1)
            return np.exp(-gam * d2) @ alfa_m
        return vekil

    alfa = np.linalg.solve(K + lam * np.eye(n), y)

    def vekil_tam(u: np.ndarray) -> np.ndarray:
        u = np.atleast_2d(u)
        d2 = ((u[:, None, :] - U[None, :, :]) ** 2).sum(-1)
        return np.exp(-gam * d2) @ alfa
    return vekil_tam


def dalga_yayilimi(V: np.ndarray, tau_adim: int = 400,
                   dt: float = 0.02, hbar2m: float = 1.0
                   ) -> Tuple[Tuple[int, ...], np.ndarray]:
    """``∂ψ/∂τ = ∇²ψ − Vψ`` -- ızgarada, ``r ≤ 3`` boyutta.

    Boyut laneti burada yoktur çünkü ``r``ye Active Subspaces ile
    inilmiştir (kütük H28). Dalga bütün bariyerlerin içinden aynı anda
    sızar (difüzyon), yüksek enerjili sahte çukurlar ``e^{−Eτ}`` ile
    söner, geriye taban modu kalır. Tepe noktasının indeksi küresel
    minimumdur.
    """
    psi = np.ones_like(V)
    psi /= np.linalg.norm(psi)
    for _ in range(tau_adim):
        lap = np.zeros_like(psi)
        for eks in range(psi.ndim):
            lap += (np.roll(psi, 1, eks) - 2 * psi + np.roll(psi, -1, eks))
        psi = psi + dt * (hbar2m * lap - V * psi)
        psi = np.abs(psi)
        n = np.linalg.norm(psi)
        if n < 1e-300:
            break
        psi /= n
    return np.unravel_index(int(np.argmax(psi)), psi.shape), psi


def as_gek_adimi(f: Callable[[np.ndarray], float], x0: np.ndarray,
                 yaricap: float = 0.6, r: int = 2, izgara: int = 24,
                 n_ornek: int = 24, hedef_ceza: Optional[Callable] = None,
                 lam_hedef: float = 1.0, tohum: int = 0
                 ) -> Tuple[np.ndarray, Dict[str, float]]:
    """Bir tam çevrim: AS → GEK → hedef sızdırma → dalga → ters izdüşüm."""
    W1, ozdeger, _ = hareketin_altuzayi(f, x0, n_ornek=n_ornek, r=r, tohum=tohum)
    rng = np.random.default_rng(tohum + 1)

    # r boyutlu kutuda örnekleme ve gerçek fonksiyon değerleri
    n_nokta = max(24, 8 * r)
    Ur = rng.uniform(-yaricap, yaricap, size=(n_nokta, r))
    y = np.array([f(x0 + W1 @ u) for u in Ur])
    vekil = gek_uydur(Ur, y, nystrom=min(16, n_nokta // 2))

    eks = [np.linspace(-yaricap, yaricap, izgara) for _ in range(r)]
    ag = np.stack(np.meshgrid(*eks, indexing="ij"), -1).reshape(-1, r)
    V = np.asarray(vekil(ag), float).reshape([izgara] * r)

    # --- HEDEF BİLGİSİ SIZDIRMA (kütük H28)
    # ``V_toplam = V_GEK + λ‖𝒢(u) − y_hedef‖²``. Minimumun NEREDE
    # olduğunu bilmesek de orada hangi şartın sağlanacağını biliriz;
    # o şart potansiyele doğrudan konur.
    #
    # Cezayı ızgaranın her düğümünde hesaplamak, ``izgara^r`` tam ileri
    # geçiş demektir (r=2, izgara=20 → 400 geçiş, çevrim başına
    # dakikalar). Bunun yerine ceza da AYNI ``n_nokta`` örnekte ölçülüp
    # kendi GEK yüzeyine oturtulur ve ızgarada vekilden okunur. Böylece
    # sızdırma fiilen olur, maliyeti ise ``n_nokta`` kadardır.
    hedef_bilgisi = 0.0
    if hedef_ceza is not None:
        c = np.array([float(hedef_ceza(x0 + W1 @ u)) for u in Ur])
        ceza_vekili = gek_uydur(Ur, c, nystrom=min(16, n_nokta // 2))
        C = np.asarray(ceza_vekili(ag), float).reshape(V.shape)
        # İki yüzey aynı mertebeye getirilir; aksi hâlde biri ötekini
        # ezer ve sızdırma ya hiç iş görmez ya yüzeyi tamamen ele geçirir.
        Vn = (V - V.min()) / (V.max() - V.min() + 1e-12)
        Cn = (C - C.min()) / (C.max() - C.min() + 1e-12)
        V = Vn + lam_hedef * Cn
        hedef_bilgisi = float(np.mean(c))

    V = (V - V.min()) / (V.max() - V.min() + 1e-12) * 30.0
    tepe, _ = dalga_yayilimi(V)
    u_yildiz = np.array([eks[i][tepe[i]] for i in range(r)])
    x_yeni = x0 + W1 @ u_yildiz               # ters izdüşüm

    return x_yeni, {"r": float(r),
                    "özdeğer_oranı": float(ozdeger[0] / (ozdeger.sum() + 1e-12)),
                    "vekil_min": float(V.min()), "vekil_max": float(V.max()),
                    "hedef_sızdırıldı": float(hedef_ceza is not None),
                    "hedef_cezası": hedef_bilgisi}


@dataclass
class OptimizeAyari:
    """Küllî motorun ölçüleri -- hiçbiri koda gömülü değildir."""
    ad: str = "küllî-optimize"
    tur: int = 3
    yaricap: float = 2.5
    gcl_nokta_sayisi: int = 16
    #: Her turda kaç yön taranacak. ``0`` = hepsi (``d`` yön).
    yon_sayisi: int = 0
    # Uzuv anahtarları -- kapatılabilir olması ölçüm şartıdır (H90)
    had_acik: bool = True
    #: HAD yoklamasının **tam** maliyeti: ``had_yon × len(had_yaricaplar)``
    #: kayıp çağrısı. Sabit ve bütçeye girer.
    had_yon: int = 3
    had_yaricaplar: Tuple[float, ...] = (1.0, 2.0, 4.0)
    durgunluk_acik: bool = True
    sesli: bool = False
    tohum: int = 0
    #: **BLOK TÂLİMİ (1. zerk edilen uzuv).** Sıfırsa kapalı; müsbetse
    #: her turda yalnız o bloğa dokunulur, kalanı dondurulur. Bu bir
    #: **kesit değildir**: hiçbir yön atılmaz, sırayla ziyaret edilir.
    blok: int = 0
    #: ``{ad: (başlangıç, uzunluk)}`` -- ``QParametre.defter()`` bunu
    #: verir. Bloklar melekenin **kendi dilimidir**, keyfî bölme değil.
    blok_defteri: Optional[Dict[str, Tuple[int, int]]] = None
    # --- KÜME 4 terkibinde ``Hoca``dan eriyen üç uzuv (kütük H223) ---
    #: TÜNEL: durgunluk bu eşiğin altına inip HAD zorlayıcı BULMAZSA
    #: (H29 çift şartı) bir kez karşıt-adiyabatik sürüşle tünellenir.
    tunel_acik: bool = False
    durgunluk_esigi: float = 1e-3
    #: VEKİL: tünelleme sonrası aday sayısı > 1 ise RKHS ile sırala.
    vekil_acik: bool = False
    vekil_aday: int = 6
    #: Bütçe ön-denetimi -- bkz. ``KulliOptimizer._boyut_guvenligi``.
    bütçe_denetimi: bool = False
    azami_saniye: float = 3600.0


class KulliOptimizer:
    """Belirlenimci, gradyansız, blok koordinatlı FCT motoru."""

    def __init__(self, kayip, p0: np.ndarray,
                 ayar: Optional[OptimizeAyari] = None) -> None:
        self.kayip = kayip
        self._ornekler: List[Tuple[np.ndarray, float]] = []
        self.tunel_sayisi = 0
        self.p0 = np.asarray(p0, float).reshape(-1)
        self.d = int(self.p0.size)
        self.ayar = ayar or OptimizeAyari()
        self.cagri = 0
        self.gunluk: List[Dict[str, object]] = []
        self.dusen_uzuv: Dict[str, str] = {}
        self.t0 = time.perf_counter()

    # -- BÜTÇE TELEMETRİSİ (4. zerk edilen uzuv) ----------------------
    def _f(self, P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        self.cagri += int(P.shape[0])
        v = np.asarray(self.kayip(P), float).reshape(-1)
        # VEKİL defteri: RKHS yüzeyi bu örneklerden kurulur.
        if self.ayar.vekil_acik:
            P2 = np.atleast_2d(P)
            for _i in range(P2.shape[0]):
                self._ornekler.append((P2[_i].copy(), float(v[_i])))
        return v

    def _f1(self, p: np.ndarray) -> float:
        return float(self._f(p.reshape(1, -1))[0])

    # -- HAD YARIÇAP FRENİ (3. zerk edilen uzuv) ----------------------
    def _had_yaricap(self, merkez: np.ndarray) -> float:
        """Kayıp zorlayıcı mı? Değilse yarıçap **frenlenir**.

        Zorlayıcı olmayan bir kayıpta asgarî sonsuzda olabilir; arama
        yarıçapı bağlanmazsa boşluğa koşar. Bu bir tedbir değil,
        aramanın iyi konulmuş olmasının şartıdır.

        ===================================================================
        `akis.tikiz.zorlayici_mi` BU HATTA KULLANILAMAZ -- ÖLÇÜLDÜ
        ===================================================================

        Evvelâ HAD'i doğrudan ``akis.tikiz.zorlayici_mi``ye bağlamıştım.
        Ölçüldü: ``d = 270`` iken **tek çağrısı 87.294 kayıp
        değerlendirmesi** istiyor. Küllî kayıpta bir değerlendirme
        9,44 sn olduğuna göre bu **229 saattir**. Üstelik bütçe
        kestirimim onu hiç saymıyordu; yani ilan ettiğim "49 çağrı"
        yanlıştı ve imtihan 31 CPU-dakika sessiz kaldı.

        Yerine **sınırlı bir zorlayıcılık yoklaması** kondu ve haddi
        açıkça yazılıdır: ``had_yon`` rastgele yönde, ``had_yaricaplar``
        ölçeğinde kayıp okunur ve **artıyor mu** diye bakılır.
        ``akis.tikiz``in tam testi değildir ve öyle sunulmuyor; sonlu
        bir örnekten okunan bir işarettir. Maliyeti tam olarak
        ``had_yon × len(had_yaricaplar)`` çağrıdır ve bütçeye girer.
        """
        if not self.ayar.had_acik:
            return float(self.ayar.yaricap)
        rng = np.random.default_rng(int(self.ayar.tohum))
        yarilar = tuple(self.ayar.had_yaricaplar)
        ort = []
        for R in yarilar:
            Z = rng.normal(size=(int(self.ayar.had_yon), self.d))
            Z /= np.maximum(np.linalg.norm(Z, axis=1, keepdims=True), 1e-12)
            ort.append(float(np.mean(self._f(merkez[None, :] + R * Z))))
        # Zorlayıcı: yarıçap büyüdükçe kayıp da büyümeli.
        zor = all(ort[i + 1] >= ort[i] for i in range(len(ort) - 1))
        self.gunluk.append({"uzuv": "had", "zorlayıcı": bool(zor),
                            "kayıp_ortalamaları": ort})
        return float(self.ayar.yaricap) * (1.0 if zor else 0.5)

    # -- GRASSMANN DURGUNLUĞU (2. zerk edilen uzuv) -------------------
    def _durgunluk(self, onceki: Optional[np.ndarray],
                   simdiki: np.ndarray) -> float:
        """Ardışık iki turun altuzayları arasındaki asal açı.

        "Kayıp düşmüyor"dan **daha erken ve daha kesin** bir durgunluk
        alâmetidir: kayıp gürültülüdür, altuzay değildir.
        """
        if onceki is None or not self.ayar.durgunluk_acik:
            return 1.0
        try:
            m = float(hareketin_altuzayi(ne="fark", onceki=onceki,
                                         simdiki=simdiki))
            self.gunluk.append({"uzuv": "durgunluk", "grassmann": m})
            return m
        except Exception as exc:                          # noqa: BLE001
            self.dusen_uzuv["ogrenme.grassmann"] = type(exc).__name__
            return 1.0

    # -- BLOK DEFTERİ (1. zerk edilen uzuv) ---------------------------
    def _bloklar(self) -> List[np.ndarray]:
        """Parametreyi **melekenin kendi dilimlerine** böl."""
        if self.ayar.blok_defteri:
            bl = []
            for _ad, (bas, kac) in sorted(
                    self.ayar.blok_defteri.items(), key=lambda kv: kv[1][0]):
                idx = np.arange(int(bas), min(int(bas) + int(kac), self.d))
                if idx.size:
                    bl.append(idx.astype(np.intp))
            if bl:
                return bl
        n = max(1, int(self.ayar.blok))
        return [np.asarray(x, np.intp)
                for x in np.array_split(np.arange(self.d), n) if len(x)]

    # -- FCT KAPALI FORM: YÖN BAŞINA analitik asgarî ------------------
    def _yon_asgarisi(self, p: np.ndarray, yon: np.ndarray,
                      R: float) -> Tuple[np.ndarray, float]:
        """Bir yönde GCL düğümlerinde oku, Chebyshev kur, **analitik in**.

        Örnekleme yok, rastgelelik yok: aynı ``p`` ve ``yon`` daima aynı
        adımı verir. Serinin asgarîsi düğümler üstünde aranır ve
        aradaki en iyi düğüm hakikî kayba **teyit ettirilir** -- seri
        yaklaşıktır, hüküm daima hakikî kayıptan alınır.
        """
        M = int(self.ayar.gcl_nokta_sayisi)
        t = chebyshev_tasarimi(M, KIP_DUGUM)
        P = p[None, :] + (R * t)[:, None] * yon[None, :]
        v = self._f(P)
        k = int(np.argmin(v))
        return P[k], float(v[k])

    def _boyut_guvenligi(self) -> None:
        """``d, tur, düğüm``den beklenen süreyi kestir; aşarsa PATLAT.

        Motor yön başına ekseni tarar -- ``yon_sayisi`` sınırlanmazsa bu
        ``d`` yön demektir. Bütçe formülü ``butce_kestirimi`` ile
        birebirdir. ``saniye_basi_cagri`` CPU'da saniyede karşılanabilecek
        kayıp çağrısı için ihtiyatlı (iyimser) bir üst sınırdır; ölçülen
        gerçek hızlar bunun altında kalıyorsa hesap zaten daha da uzun
        sürer.

        **Bu denetim olmasaydı ne olurdu**, ölçüldü: ``idrak/model.py``
        (D=128, 2,34M parametre) varsayılan ayarlarla bu motora
        bağlanmaya kalkışılsaydı beklenen çağrı ~119,3 milyon, ~28 gün
        sürerdi -- **sessizce**.
        """
        M = int(self.ayar.gcl_nokta_sayisi) + 1
        cagri = int(self.ayar.tur) * int(self.d) * M
        saniye = cagri / 50.0
        if saniye > float(self.ayar.azami_saniye):
            raise RuntimeError(
                "hoca: d=%d parametre, tur=%d, düğüm=%d ile beklenen çağrı "
                "≈ %d (~%.1f saat). Bu motor yön-taramalıdır ve milyonlarca "
                "parametreye ÖLÇEKLENMEZ (bkz. docs/KUTUK.md, idrak/model.py "
                "tartışması). d'yi küçültün, OptimizeAyari.yon_sayisi/blok "
                "ile daraltın, ya da azami_saniye'yi bilerek yükseltin."
                % (self.d, self.ayar.tur, M, cagri, saniye / 3600))

    def _vekil_sec(self, p_merkez: np.ndarray, adaylar: List[np.ndarray]
                   ) -> np.ndarray:
        """Adaylar arasından RKHS yüzeyiyle en umutluyu seç.

        Yalnız SIRALAMA için kullanılır; seçilen aday sonra gerçek
        ``kayip``la (tur döngüsünün kendisiyle) sınanır -- vekil karar
        vermez, önerir.
        """
        if len(adaylar) <= 1 or len(self._ornekler) < 8:
            return adaylar[0] if adaylar else p_merkez
        X = np.stack([o[0] for o in self._ornekler[-64:]])
        y = np.array([o[1] for o in self._ornekler[-64:]])
        try:
            gama = 1.0 / max(medyan_genislik(X) ** 2, 1e-9)
            model = RKHS(K=gauss_cekirdegi(gama), lam=1e-3).uydur(X, y)
            tahmin = model(np.stack(adaylar)).reshape(-1)
            return adaylar[int(np.argmin(tahmin))]
        except Exception as exc:                          # noqa: BLE001
            self.dusen_uzuv["ogrenme.rkhs"] = type(exc).__name__
            return adaylar[0]

    def _tunelle(self, p: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """H29 deseni: STA sürüşü uygula, gerekiyorsa RKHS'le birden
        çok aday arasından seç, ama karar HER ZAMAN gerçek kayıpla."""
        ham = np.asarray(
            kestirmeden_sur(ne="sürüş_uygula", durum=p.astype(float),
                            sure_tau=1.0))
        surulmus = np.asarray(ham.real if np.iscomplexobj(ham) else ham,
                              dtype=float).reshape(-1)
        if surulmus.shape != p.shape or not np.all(np.isfinite(surulmus)):
            return p                                       # sürüş bozduysa vazgeç
        adaylar = [surulmus]
        if self.ayar.vekil_acik:
            for _ in range(max(0, int(self.ayar.vekil_aday) - 1)):
                jitter = rng.normal(scale=1e-2, size=p.shape)
                adaylar.append(surulmus + jitter * np.linalg.norm(p) / max(
                    np.linalg.norm(p), 1e-9))
            surulmus = self._vekil_sec(p, adaylar)
        self.tunel_sayisi += 1
        self.gunluk.append({"uzuv": "tünel", "sıra": self.tunel_sayisi,
                            "aday_sayısı": len(adaylar)})
        return surulmus

    def butce_kestirimi(self) -> Dict[str, int]:
        """Koşmadan **evvel** kaç kayıp çağrısı harcanacağını söyle.

        **Niçin var.** Bu motor çağrı-açtır: ``tur × yön × M``. ``d``
        büyükse ve ``yon_sayisi`` sıfır bırakılmışsa (yani "hepsi")
        bütçe sessizce patlar. Bu turda aynı kusurun bir başka hâli
        ölçüldü: bütçesiz bir arama 86 CPU-dakika boyunca **tek satır**
        basmadan koştu. Bütçe peşinen ilan edilirse o hâl tekrarlamaz.
        """
        yon = int(self.ayar.yon_sayisi) or self.d
        if self.ayar.blok or self.ayar.blok_defteri:
            bl = self._bloklar()
            yon = min(yon, max(len(x) for x in bl)) if bl else yon
        # GCL ``M`` **derecedir**; düğüm sayısı ``M+1``dir. Evvelce
        # ``M`` sayılıyordu ve kestirim 1180 derken gerçek 1252
        # çıkıyordu -- fark tam olarak yön başına bir düğümdü.
        M = int(len(chebyshev_tasarimi(
            int(self.ayar.gcl_nokta_sayisi), KIP_DUGUM)))
        # **HAD çağrıları da sayılır.** Evvelce sayılmıyordu ve ilan
        # edilen bütçe yanlış çıkıyordu; ölçülmeyen bir bütçe bütçe
        # değildir.
        had = (int(self.ayar.had_yon) * len(self.ayar.had_yaricaplar)
               if self.ayar.had_acik else 0)
        return {"tur": int(self.ayar.tur), "yön": int(yon), "düğüm": M,
                "had_çağrısı": int(self.ayar.tur) * had,
                "beklenen_çağrı": int(self.ayar.tur) * (int(yon) * M + had) + 1}

    def kos(self) -> Dict[str, object]:
        """Motoru koştur; ``p*`` ve tam telemetriyi döndür.

        KÜME 4 terkibinde (kütük H223) ``Hoca`` sınıfı buraya eridi.
        Kalıtım bir cevher değil **toprak**tı: ``Hoca`` motoru yeniden
        yazmıyordu ama tur döngüsünün TAMAMINI kopyalıyordu, sırf
        turlar arasına TÜNEL kararını sokabilmek için. Şimdi o karar
        döngünün kendisindedir ve ``ayar.tunel_acik`` ile kapatılabilir
        (H90: kapatılabilirlik ölçüm şartıdır).
        """
        if self.ayar.bütçe_denetimi:
            self._boyut_guvenligi()
        rng = np.random.default_rng(int(self.ayar.tohum))
        kes = self.butce_kestirimi()
        if self.ayar.sesli:
            print("  [BÜTÇE] tur=%d × (yön=%d × düğüm=%d + HAD=%d) → "
                  "beklenen çağrı ≈ %d"
                  % (kes["tur"], kes["yön"], kes["düğüm"],
                     kes["had_çağrısı"] // max(kes["tur"], 1),
                     kes["beklenen_çağrı"]), flush=True)
        p = self.p0.copy()
        v_ilk = self._f1(p)
        v = v_ilk
        bloklar = self._bloklar() if (self.ayar.blok
                                      or self.ayar.blok_defteri) else None
        onceki_U: Optional[np.ndarray] = None
        seyir: List[Dict[str, float]] = []
        son_had_zorlayici = True

        for tur in range(int(self.ayar.tur)):
            R = self._had_yaricap(p)
            if self.gunluk and self.gunluk[-1].get("uzuv") == "had":
                son_had_zorlayici = bool(self.gunluk[-1]["zorlayıcı"])
            idx = (bloklar[tur % len(bloklar)] if bloklar
                   else np.arange(self.d, dtype=np.intp))
            yonler = list(idx)
            if self.ayar.yon_sayisi:
                yonler = yonler[:int(self.ayar.yon_sayisi)]
            for j in yonler:
                e = np.zeros(self.d)
                e[int(j)] = 1.0
                pa, va = self._yon_asgarisi(p, e, R)
                if va < v:
                    p, v = pa, va
                # **Yön başına ilerleme basılır.** Tur başına basmak
                # yetmiyordu: tek turluk bir koşu 31 CPU-dakika boyunca
                # tek satır çıkarmadı. Sessiz hesap ölçülemeyen hesaptır.
                if self.ayar.sesli:
                    print("    [yön %3d/%3d] V=%.6f çağrı=%d"
                          % (yonler.index(j) + 1, len(yonler), v,
                             self.cagri), flush=True)
            U = p.reshape(-1, 1)
            durgun = self._durgunluk(onceki_U, U)
            onceki_U = U

            # --- H29 ÇİFT ŞARTI: durgunluk eşiğin altında VE HAD
            #     zorlayıcı bulmuyorsa bir kez tünellenir. Tek şartla
            #     tünellemek, HAD'in hâlâ ilerleme bulduğu yerde de
            #     sıçramak demekti.
            tunellendi = False
            if (self.ayar.tunel_acik and tur < int(self.ayar.tur) - 1
                    and durgun < self.ayar.durgunluk_esigi
                    and not son_had_zorlayici):
                p_aday = self._tunelle(p, rng)
                v_aday = self._f1(p_aday)
                if v_aday < v:                       # hüküm gerçek kayıptan
                    p, v = p_aday, v_aday
                    tunellendi = True

            seyir.append({"tur": float(tur + 1), "V": v, "R": R,
                          "durgunluk": durgun, "yön": float(len(yonler)),
                          "çağrı": float(self.cagri),
                          "tünellendi": float(tunellendi)})
            if self.ayar.sesli:
                print("  [TUR %d] V=%.6f R=%.3f durgunluk=%.3e "
                      "tünel=%s çağrı=%d"
                      % (tur + 1, v, R, durgun, tunellendi, self.cagri),
                      flush=True)

        return {"p": p, "V_ilk": v_ilk, "V_son": v,
                "kazanç": v_ilk - v, "bütçe_kestirimi": kes,
                "süre_sn": time.perf_counter() - self.t0,
                "kayıp_çağrısı": int(self.cagri),
                "tünel_sayısı": self.tunel_sayisi,
                "seyir": seyir, "günlük": self.gunluk,
                "düşen_uzuv": self.dusen_uzuv,
                "blok_sayısı": len(bloklar) if bloklar else 0}


def eniyile(kayip, p0: np.ndarray,
            ayar: Optional[OptimizeAyari] = None) -> Dict[str, object]:
    """Tek satırlık standart çağrı -- **tek kapı** (kütük H223).

    KÜME 4 terkibinde ``eniyile`` ile ``hoca_egit`` birleşti: ikisi de
    aynı motoru kuruyor ve koşuyordu, farkları yalnız ``HocaAyari``nin
    üç anahtarıydı. O anahtarlar artık ``OptimizeAyari``dedir; eğitilecek
    her sürekli-parametreli şey (44 meleke, ``Dalga.W``, kademe
    parametreleri, …) buradan geçer. Milyonlarca parametreli bir ağ
    (``idrak/model.py`` gibi) geçemez -- ``bütçe_denetimi`` açıkken
    ``_boyut_guvenligi`` bunu **sessizce değil, açıkça** reddeder.
    """
    return KulliOptimizer(kayip, p0, ayar).kos()


def hoca_egit(kayip: Callable[[np.ndarray], np.ndarray], p0: np.ndarray,
              ayar=None) -> Dict[str, object]:
    """TÜNEL + VEKİL + bütçe denetimi açık hâlde ``eniyile``.

    ``HocaAyari`` verilirse ``temel`` alanı alınır ve üç anahtarı ona
    işlenir; hiçbir ayar kaybolmaz.
    """
    if ayar is None:
        a = OptimizeAyari()
    elif isinstance(ayar, OptimizeAyari):
        a = ayar
    else:                                   # eski HocaAyari kılığı
        a = ayar.temel
        a.tunel_acik = bool(getattr(ayar, "tunel_acik", True))
        a.durgunluk_esigi = float(getattr(ayar, "durgunluk_esigi", 1e-3))
        a.vekil_acik = bool(getattr(ayar, "vekil_acik", False))
        a.vekil_aday = int(getattr(ayar, "vekil_aday", 6))
        a.bütçe_denetimi = bool(getattr(ayar, "bütçe_denetimi", True))
        a.azami_saniye = float(getattr(ayar, "azami_saniye", 3600.0))
        return KulliOptimizer(kayip, p0, a).kos()
    a.tunel_acik = True
    a.bütçe_denetimi = True
    return KulliOptimizer(kayip, p0, a).kos()


# ════════════════════════════════════════════════════════════════════
#  ogrenme/hoca.py
# ════════════════════════════════════════════════════════════════════



# ====================================================================
#  KÜME 8: kuyudan çıkmak, hocanın haddi, en iyiyi aramak
# ====================================================================

def kuyudan_cik(x0=None, ne: str = "ısıl", T: float = 0.3,
                n: int = 8000, adim: int = 60000, eta: float = 1e-3,
                tohum: int = 0, kayit_araligi: int = 5000,
                V=None, E: float = 0.2, x1: float = 0.0, x2: float = 1.0,
                m: float = 1.0, hbar: float = 1.0, orgu: int = 4001,
                genislikler=(1, 2, 4, 8), V0: float = 1.0):
    """KUYUDAN ÇIKMAK -- **tek terkip** (kütük H227).

    Küme: ``cift_kuyu``, ``cift_kuyu_gradyan``, ``cukurlar``,
    ``vektor_akisi``, ``yerel_tuzak``, ``langevin``, ``gibbs_ile_kiyas``,
    ``tuzaktan_kacis``, ``serbest_enerji_azaliyor_mu``. Dokuz isim tek
    suâlin parçalarıydı: **yerel asgarîde sıkıştım, nasıl çıkarım?**

    Aynı çift kuyu üstünde iki cevap yan yana konur ve fark ölçülür:

    ==============  ==============================  ==================
    yol             çıkış kanunu                    neye bakar
    ==============  ==============================  ==================
    belirlenimci    -- (hiç çıkamaz)                 yalnız yokuşa
    ısıl topluluk   ``e^{−ΔE/T}``                    bariyerin
                                                     **yüksekliğine**
    kuantum tüneli  ``e^{−γ}``,                      bariyerin
                    ``γ = (2/ħ)∫√(2m(V−E))dx``       **altındaki alana**
    ==============  ==============================  ==================

    **Asıl fark buradadır ve ancak yan yana konunca görülür.** İki
    kaçış da üsteldir, fakat üsleri farklı şeyi sayar: ısıl kaçış
    bariyerin **ne kadar yüksek** olduğuna bakar, tünel **ne kadar
    geniş ve yüksek** olduğuna -- yâni alana. Alçak ama çok geniş bir
    bariyer ısıl kaçışa kolay, tünele imkânsız gelir; yüksek ama
    iğne gibi ince bir bariyer bunun tam tersidir.

    ``ayrik_mertebede_sicra``daki tavlama kapısı bu üçüncü yolu
    kullanır ve şimdiye kadar hangi kanunu kullandığını **söylemiyordu**;
    artık burada, ötekilerin yanında duruyor.

    Mihenk ``f(x) = (x²−1)² + 0.3x``tir: iki çukur, ve ``+0.3x`` terimi
    **soldakini** derinleştirir. Sağ (sığ) çukurdan başlanır; belirlenimci
    akış orada kalır, ısıl topluluk geçer. İddia böylece **kırmızı
    yanabilir** hâle gelir.

    ==========================  ======================================
    ``ne``                      döndürdüğü
    ==========================  ======================================
    ``yer``                     ``f(x)`` -- mihenk manzarası
    ``yokuş``                   ``f′(x)``
    ``çukurlar``                iki asgarî ve aradaki eyer
    ``akış``                    belirlenimci iniş nerede durur
    ``tuzak``                   sığdan başlayan akış derine geçti mi
    ``ısıl``                    Langevin topluluğunun son hâli
    ``gibbs``                   durağan dağılım ``e^{−f/T}`` ile uyuştu mu
    ``kaçış``                   akış ile topluluğun **yan yana** ölçümü
    ``serbest_enerji``          ``F[ρ] = E_ρ[f] + T·∫ρlogρ`` azalıyor mu
    ==========================  ======================================

    ``serbest_enerji`` Wasserstein gradyan akışı iddiasının sayısal
    karşılığıdır. Entropi histogramdan kesikli tahmin edildiği için
    'monotonluk' değil **'kayda değer artış yok'** sınanır -- iddia
    ölçülebilir tutulur, olduğundan güçlü söylenmez.
    """
    def f(v):
        v = np.asarray(v, float)
        return (v * v - 1.0) ** 2 + 0.3 * v

    def df(v):
        v = np.asarray(v, float)
        return 4.0 * v * (v * v - 1.0) + 0.3

    if ne == "yer":
        return f(x0)
    if ne == "yokuş":
        return df(x0)

    if ne == "çukurlar":
            kokler = np.sort(np.roots([4.0, 0.0, -4.0, 0.3]).real)
            sol, eyer, sag = kokler
            return {
                "sol_cukur": float(sol),
                "eyer": float(eyer),
                "sag_cukur": float(sag),
                "f_sol": float(float(f(sol))),
                "f_sag": float(float(f(sag))),
            }

    if ne == "akış":
            adim = 20000 if adim == 60000 else adim   # aslının varsayılanı
            x0 = 0.0 if x0 is None else float(x0)
            x = np.array([x0])
            for _ in range(adim):
                x = x - eta * df(x)
            return {"x0": x0, "son_x": float(x[0]),
                    "son_f": float(f(x)[0])}

    if ne == "tuzak":
            c = kuyudan_cik(ne="çukurlar")
            sig = c["sag_cukur"] if c["f_sag"] > c["f_sol"] else c["sol_cukur"]
            derin = c["sol_cukur"] if c["f_sag"] > c["f_sol"] else c["sag_cukur"]
            a = kuyudan_cik(float(sig) + 0.05, ne="akış")
            return {
                "sig_cukur": float(sig),
                "derin_cukur": float(derin),
                "vardigi": a["son_x"],
                "sig_cukurda_kaldi": bool(abs(a["son_x"] - sig) < 1e-3),
            }

    if ne == "ısıl":
            rng = np.random.default_rng(tohum)
            if x0 is None:
                x0 = float(kuyudan_cik(ne="çukurlar")["sag_cukur"])
            x = np.full(n, x0)
            sigma = np.sqrt(2.0 * T * eta)
            for _ in range(adim):
                x = x - eta * df(x) + sigma * rng.normal(size=n)
            return x

    if ne == "gibbs":
            ornek = kuyudan_cik(ne="ısıl", T=T, n=n, adim=adim, eta=eta,
                                tohum=tohum)
            kenar = np.linspace(-2.0, 2.0, 81)
            orta = 0.5 * (kenar[:-1] + kenar[1:])
            genislik = kenar[1] - kenar[0]

            say, _ = np.histogram(ornek, bins=kenar)
            p_amp = say / max(say.sum(), 1)

            yog = np.exp(-f(orta) / T)
            p_gibbs = yog / yog.sum()

            tv = 0.5 * float(np.sum(np.abs(p_amp - p_gibbs)))

            c = kuyudan_cik(ne="çukurlar")
            sinir = c["eyer"]
            sol_kutle = float(np.mean(ornek < sinir))
            gibbs_sol = float(p_gibbs[orta < sinir].sum())
            return {
                "T": T,
                "toplam_degisim_uzakligi": tv,
                "gibbs_ile_uyusuyor": bool(tv < 0.08),
                "sol_cukur_kutlesi": sol_kutle,
                "gibbs_sol_kutlesi": gibbs_sol,
                "kutle_uyusuyor": bool(abs(sol_kutle - gibbs_sol) < 0.08),
                "sinir": float(sinir),
            }

    if ne == "kaçış":
            t = kuyudan_cik(ne="tuzak")
            ornek = kuyudan_cik(t["sig_cukur"] + 0.05, ne="ısıl", T=T)
            sinir = kuyudan_cik(ne="çukurlar")["eyer"]
            derin_solda = t["derin_cukur"] < sinir
            kacan = float(np.mean(ornek < sinir) if derin_solda else np.mean(ornek > sinir))
            return {
                "vektor_akisi_kacti": not t["sig_cukurda_kaldi"],
                "toplulugun_kacan_kesri": kacan,
                "topluluk_kacti": bool(kacan > 0.5),
            }

    if ne == "tünel":
        V = V if V is not None else (lambda z: np.full_like(z, V0))
        x = np.linspace(x1, x2, orgu)
        ic = np.clip(2.0 * m * (np.asarray(V(x), float) - E), 0.0, None)
        gamma = float(2.0 / hbar * np.trapezoid(np.sqrt(ic), x))
        return {"γ": gamma, "geçirgenlik": math.exp(-gamma),
                "beklenen_deneme": (float("inf") if math.exp(-gamma) <= 0
                                    else 1.0 / math.exp(-gamma))}

    if ne == "bedel":
        out = []
        for L in genislikler:
            r = kuyudan_cik(ne="tünel", V0=V0, E=E, m=m,
                            x1=0.0, x2=float(L))
            g = r["γ"]
            T = r["geçirgenlik"]
            out.append({"genişlik": float(L), "γ": g, "T": T,
                        "beklenen_deneme": r["beklenen_deneme"]})
        return out

    if ne == "serbest_enerji":
            rng = np.random.default_rng(1)
            n = 8000
            eta = 1e-3
            x = np.full(n, float(kuyudan_cik(ne="çukurlar")["sag_cukur"]) + 0.05)
            sigma = np.sqrt(2.0 * T * eta)
            kenar = np.linspace(-2.5, 2.5, 101)
            genislik = kenar[1] - kenar[0]

            def F(v: np.ndarray) -> float:
                say, _ = np.histogram(v, bins=kenar)
                p = say / say.sum()
                yog = p / genislik
                nz = p > 0
                entropi = float(np.sum(p[nz] * np.log(yog[nz])))
                return float(np.mean(f(v))) + T * entropi

            izler = [F(x)]
            for t in range(1, adim + 1):
                x = x - eta * df(x) + sigma * rng.normal(size=n)
                if t % kayit_araligi == 0:
                    izler.append(F(x))
            artis = max((izler[i + 1] - izler[i]) for i in range(len(izler) - 1))
            return {
                "F_izi": [round(v, 4) for v in izler],
                "toplam_dusus": izler[0] - izler[-1],
                "azaldi": bool(izler[-1] < izler[0]),
                "azami_ara_artis": float(artis),
                "kayda_deger_artis_yok": bool(artis < 0.02),
            }

    raise ValueError("kuyudan çıkış yolu bilinmiyor: %r" % (ne,))


HBAR = 1.0










def _arama_izi(
    sira: Sequence[int],
    f: Sequence[int],
) -> Tuple[int, ...]:
    """``sira`` düzeninde noktaları gezen usulün gördüğü değerler dizisi."""
    return tuple(f[x] for x in sira)


def had(ne: str = "nfl", m: int = 3, n: int = 3, k: int = 8,
        adim: int = 5, azami_adim: int = 8, nokta: int = 64):
    """HOCANIN HADDİ -- **tek terkip** (kütük H227).

    Küme: ``nfl_tam_sayim``, ``nfl_kacamagi``, ``sifir_zinciri_sinamasi``,
    ``alt_sinir_ihlal_var_mi``. Dördü tek suâlin cevabıydı: **hoca ne
    kadar iyi olabilir?** Ve cevap iki yönden gelir; ayrı dosyalarda
    dururken bu iki yönlülük görünmüyordu:

    * **Üstten** -- NFL: bütün fonksiyonlar üzerinde ortalama alındığında
      hiçbir arama usulü ötekinden üstün değildir. Tam sayımla, yaklaşık
      değil kesin.
    * **Alttan** -- Nesterov: ``t`` adımda ``f(x_t) − f* ≥
      3L‖x₀−x*‖²/(32(t+1)²)``. Usul akıllı olsun olmasın kırılmaz.

    Ve **kaçamak** ikisini birden açıklar: NFL bir yasak değil bir
    muhasebedir. Hedef sınıfı daraltılınca (tek tepeli fonksiyonlar)
    yapılı usul rastgeleyi kesin olarak yener. Bizim yaptığımız da
    budur -- ARC keyfî bir fonksiyon sınıfı değildir.

    ==================  ==============================================
    ``ne``              döndürdüğü
    ==================  ==============================================
    ``nfl``             ``n**m`` fonksiyonun TAM sayımı: iz dağılımları
                        her sıralamada aynı mı
    ``kaçamak``         sınıf daralınca yapılı usul kazanıyor mu
    ``zincir``          sıfır zinciri: ``t`` adımda destek ``≤ t``
    ``alt_sınır``       birinci mertebe usuller sınırı kırıyor mu
    ==================  ==============================================

    **Alt sınırın hangi fonksiyonda geçerli olduğu şarttır**: her ``t``
    için en kötü fonksiyon AYRIDIR (``k = 2t+1``). Sabit bir ``k`` alıp
    ``t``yi küçük tutarsan sınır kırılmış **görünür** -- bu, usulün
    hızlı olduğunu değil iddianın yanlış kurulduğunu gösterir. Bu
    tuzağa bu dosyayı yazarken bizzat düşüldü ve ölçüm düzeltti.
    """
    if ne == "nfl":
        noktalar = list(range(m))
        fonksiyonlar = list(product(range(n), repeat=m))
        dagilimlar: Dict[Tuple[int, ...], Dict[Tuple[int, ...], int]] = {}
        for sira in permutations(noktalar):
            sayac: Dict[Tuple[int, ...], int] = {}
            for f in fonksiyonlar:
                iz = _arama_izi(sira, f)
                sayac[iz] = sayac.get(iz, 0) + 1
            dagilimlar[sira] = sayac

        ilk = next(iter(dagilimlar.values()))
        hepsi_ayni = all(d == ilk for d in dagilimlar.values())

        # ortalama "en iyi bulunan" değer de aynı olmalı (asgarî arıyoruz)
        ortalama_en_iyi = {
            sira: float(np.mean([min(_arama_izi(sira, f)) for f in fonksiyonlar]))
            for sira in dagilimlar
        }
        return {
            "nokta": m,
            "deger": n,
            "fonksiyon_sayisi": len(fonksiyonlar),
            "usul_sayisi": len(dagilimlar),
            "iz_dagilimlari_ayni": hepsi_ayni,
            "ortalama_en_iyi": ortalama_en_iyi,
            "ortalamalar_ayni": len(set(round(v, 12) for v in ortalama_en_iyi.values())) == 1,
        }

    if ne == "kaçamak":
        tekil: List[Tuple[int, ...]] = []
        for dip in range(nokta):
            f = tuple(abs(x - dip) for x in range(nokta))
            tekil.append(f)

        def rastgele_arama(f: Sequence[int], butce: int, rng: np.random.Generator) -> int:
            idx = rng.permutation(len(f))[:butce]
            return int(min(f[i] for i in idx))

        def ucdurum_arama(f: Sequence[int], butce: int) -> int:
            """Tek tepeli dizide üçlü bölme (ternary search)."""
            lo, hi = 0, len(f) - 1
            gorulen = [f[lo], f[hi]]
            kalan = butce - 2
            while kalan >= 2 and hi - lo >= 2:
                a = lo + (hi - lo) // 3
                b = hi - (hi - lo) // 3
                if a == b:
                    b = min(a + 1, hi)
                gorulen += [f[a], f[b]]
                kalan -= 2
                if f[a] <= f[b]:
                    hi = b
                else:
                    lo = a
            return int(min(gorulen))

        rng = np.random.default_rng(0)
        butce = 12
        r_top = np.mean([rastgele_arama(f, butce, rng) for f in tekil for _ in range(20)])
        u_top = np.mean([ucdurum_arama(f, butce) for f in tekil])
        return {
            "sinif": "tek tepeli",
            "nokta": nokta,
            "butce": butce,
            "rastgele_ortalama": float(r_top),
            "ucdurum_ortalama": float(u_top),
            "yapili_usul_daha_iyi": bool(u_top < r_top),
        }

    if ne == "zincir":
        f = NesterovEnKotu(k=k)
        x = np.zeros(f.n)
        h = 1.0 / (f.L)  # adım boyu; hangi değer olursa olsun destek aynı
        destekler = []
        for t in range(adim):
            x = x - h * f.gradyan(x)
            destekler.append(int(np.count_nonzero(np.abs(x) > 1e-15)))
        _, fmin = f.en_iyi()
        return {
            "k": k,
            "destek_dizisi": destekler,
            "destek_adimla_sinirli": all(d <= t + 1 for t, d in enumerate(destekler)),
            "f_son": f.deger(x),
            "f_en_iyi": fmin,
            "bosluk": f.deger(x) - fmin,
        }

    if ne == "alt_sınır":
        kayitlar: List[Tuple[str, int, float, float]] = []
        for t in range(1, azami_adim + 1):
            k = 2 * t + 1
            f = NesterovEnKotu(k=k)
            xs, fmin = f.en_iyi()
            R2 = float(np.sum(xs ** 2))
            sinir = 3.0 * f.L * R2 / (32.0 * (t + 1) ** 2)

            # (a) sabit adımlı gradyan inişi, t adım
            x = np.zeros(f.n)
            for _ in range(t):
                x = x - (1.0 / f.L) * f.gradyan(x)
            kayitlar.append(("gradyan", t, f.deger(x) - fmin, sinir))

            # (b) Nesterov hızlandırması, t adım
            x = np.zeros(f.n)
            y = x.copy()
            lam = 0.0
            for _ in range(t):
                lam_yeni = (1 + np.sqrt(1 + 4 * lam * lam)) / 2
                gamma = (1 - lam) / lam_yeni
                x_yeni = y - (1.0 / f.L) * f.gradyan(y)
                y = (1 - gamma) * x_yeni + gamma * x
                x, lam = x_yeni, lam_yeni
            kayitlar.append(("hizlandirilmis", t, f.deger(x) - fmin, sinir))

        ihlaller = [r for r in kayitlar if r[2] < r[3] - 1e-12]
        return {
            "azami_adim": azami_adim,
            "kayit_sayisi": len(kayitlar),
            "kayitlar": kayitlar,
            "ihlal": ihlaller,
            "ihlal_yok": not ihlaller,
        }

    raise ValueError("had kipi bilinmiyor: %r" % (ne,))


class NesterovEnKotu:
    """Nesterov'un en kötü pürüzsüz dışbükey fonksiyonu.

    ``f(x) = (L/8)·[ x₁² + Σ_{i<k}(xᵢ − x_{i+1})² + x_k² − 2x₁ ]``

    Bu fonksiyonun **sıfır zinciri** hususiyeti vardır: ``x``in yalnız ilk
    ``j`` bileşeni sıfırdan farklıysa ``∇f(x)``in de yalnız ilk ``j+1``
    bileşeni sıfırdan farklıdır. Dolayısıyla 0'dan başlayan ve iterasyonu
    geçmiş gradyanların gerdiği uzayda tutan HER birinci mertebe usul,
    ``k`` adımda çözümün ancak ilk ``k`` koordinatına dokunabilir.

    Alt sınır buradan çıkar: usul akıllı olsun olmasın, göremediği
    koordinatlar vardır.
    """

    def __init__(self, k: int, L: float = 1.0, boyut: int | None = None) -> None:
        self.k = k
        self.L = L
        self.n = boyut if boyut is not None else 2 * k + 1

    def deger(self, x: np.ndarray) -> float:
        k = self.k
        s = x[0] ** 2 + float(np.sum((x[: k - 1] - x[1:k]) ** 2)) + x[k - 1] ** 2
        return self.L / 8.0 * (s - 2.0 * x[0])

    def gradyan(self, x: np.ndarray) -> np.ndarray:
        k = self.k
        g = np.zeros_like(x)
        A = np.zeros((k, k))
        for i in range(k):
            A[i, i] = 2.0
            if i + 1 < k:
                A[i, i + 1] = -1.0
                A[i + 1, i] = -1.0
        e1 = np.zeros(k)
        e1[0] = 1.0
        g[:k] = self.L / 8.0 * (2.0 * A @ x[:k] - 2.0 * e1)
        return g

    def en_iyi(self) -> Tuple[np.ndarray, float]:
        """``A x = e₁`` çözümü: ``x*ᵢ = 1 − i/(k+1)``."""
        k = self.k
        x = np.zeros(self.n)
        x[:k] = np.array([1.0 - (i + 1) / (k + 1) for i in range(k)])
        return x, self.deger(x)


def esit_superpozisyon(N: int) -> np.ndarray:
    """``|Ψ₀⟩ = H^{⊗n}|0⟩`` — ``N = 2^n`` boyutunda."""
    return np.full(N, 1.0 / math.sqrt(N), dtype=complex)


def faz_kehaneti(f: np.ndarray, gamma: float) -> np.ndarray:
    """``O_f = diag(e^{iγf(x)})`` — köşegen, üniter (kaynak doğru)."""
    return np.exp(1j * gamma * np.asarray(f, float))


def esik_kehaneti(f: np.ndarray, esik: float) -> np.ndarray:
    """``O_y = diag(−1 if f(x) < esik else +1)``."""
    return np.where(np.asarray(f, float) < esik, -1.0, 1.0)


def difuzyon(psi: np.ndarray) -> np.ndarray:
    """``D = 2|Ψ₀⟩⟨Ψ₀| − I`` — ortalama etrafında yansıma, ``O(N)``.

    Tam dizey kurulmaz: ``Dψ = 2⟨ψ⟩ − ψ``.
    """
    return 2.0 * psi.mean() - psi


def grover_turu(psi: np.ndarray, isaret: np.ndarray) -> np.ndarray:
    """Bir Grover turu: kehanet sonra difüzyon."""
    return difuzyon(isaret * psi)


def en_iyiyi_ara(f=None, ne: str = "dürr", esik: float = 0.0,
                 m: int = 0, N: int = 0, K: int = 1, azami_tur: int = 0,
                 T: float = 20.0, adim: int = 300, tohum: int = 0,
                 lam: float = 6.0 / 5.0, azami_sorgu: int = 10000):
    """EN İYİYİ ARAMAK -- **tek terkip** (kütük H227).

    Küme: ``grover_basari_egrisi``, ``en_iyi_tur``, ``sabit_m_ile_arama``,
    ``durr_hoyer``, ``adiyabatik_asgari``. Beşi tek suâlin üç cevabıydı:
    **``N`` aday içinden asgarîyi nasıl buluruz?**

    ==================  ====================  ========================
    yol                 maliyet               ne bilmek gerekir
    ==================  ====================  ========================
    kaba kuvvet         ``O(N)``              hiçbir şey
    Grover              ``O(√(N/K))``         işaretli sayısı ``K``
    Dürr--Høyer         ``O(√N)``             **hiçbir şey**
    adiyabatik          ``T`` süresi          tayf aralığı
    ==================  ====================  ========================

    ==================  ==============================================
    ``ne``              döndürdüğü
    ==================  ==============================================
    ``eğri``            ``m = 0…azami_tur`` için işaretli olasılık
    ``tur``             ``m_opt = round((π/4)√(N/K))`` -- ``K`` biliniyorsa
    ``grover``          ``m`` turu sabit koş ve ölç
    ``dürr``            Dürr--Høyer: ``K`` **bilinmeden** asgarîyi bul
    ``adiyabatik``      ``H(t)`` ile taşı, asgarî duruma örtüşme
    ==================  ==============================================

    **M18 -- fazla dönmek zarar.** Grover'da başarı ``m``de tek tepelidir
    ve tepeden sonra **düşer**; ``K`` yanlış varsayılırsa ``m_opt``
    kayar ve başarı iner. "Daha çok tur daha iyi" sezgisi burada
    yanlıştır ve ``eğri`` kipi bunu görünür kılar. Dürr--Høyer'in
    kıymeti tam buradadır: ``K``yı bilmez, dolayısıyla yanlış
    varsayamaz.

    **M19 -- sonlu ``T``de başarı tam 1 değildir.** Adiyabatik teorem
    ``T → ∞`` limitindedir; sonlu sürede daima bir sızıntı kalır ve
    burada ölçülür, gizlenmez.
    """
    if ne == "eğri":
        isaretli = np.zeros(N, dtype=bool)
        isaretli[:K] = True
        isaret = np.where(isaretli, -1.0, 1.0)
        psi = esit_superpozisyon(N)
        egri = [float((np.abs(psi[isaretli]) ** 2).sum())]
        for _ in range(azami_tur):
            psi = grover_turu(psi, isaret)
            egri.append(float((np.abs(psi[isaretli]) ** 2).sum()))
        return np.array(egri)

    if ne == "tur":
        return int(round(math.pi / 4.0 * math.sqrt(N / max(K, 1))))

    if ne == "grover":
        N = f.shape[0]
        isaret = esik_kehaneti(f, esik)
        isaretli = isaret < 0
        psi = esit_superpozisyon(N)
        for _ in range(m):
            psi = grover_turu(psi, isaret)
        p = np.abs(psi) ** 2
        p = p / p.sum()
        x = int(np.random.default_rng(tohum).choice(N, p=p))
        return {"m": m, "başarı_olasılığı": float(p[isaretli].sum()),
                "ölçülen_x": x, "isabet": bool(isaretli[x]),
                "K": int(isaretli.sum())}

    if ne == "dürr":
        r = np.random.default_rng(tohum)
        N = f.shape[0]
        y = int(r.integers(0, N))
        sorgu = 0
        j = 0.0
        seyir = [(0, y, float(f[y]))]
        while sorgu < azami_sorgu:
            ust = max(1, int(math.ceil(lam ** j)))
            m = int(r.integers(0, min(ust, int(3 * math.sqrt(N)) + 1)))
            isaret = esik_kehaneti(f, f[y])
            if not (isaret < 0).any():
                break                                # y zaten asgarî
            psi = esit_superpozisyon(N)
            for _ in range(m):
                psi = grover_turu(psi, isaret)
            sorgu += m + 1
            p = np.abs(psi) ** 2
            p = p / p.sum()
            x = int(r.choice(N, p=p))
            if f[x] < f[y]:
                y = x
                seyir.append((sorgu, y, float(f[y])))
                j = 0.0
            else:
                j += 1.0
            if f[y] == f.min():
                break
        return {"x": y, "f": float(f[y]), "asgarî": float(f.min()),
                "bulundu_mu": bool(f[y] == f.min()), "sorgu": sorgu,
                "sqrt_N": math.sqrt(N), "sorgu_bölü_sqrtN": sorgu / math.sqrt(N),
                "seyir": seyir}

    if ne == "adiyabatik":
        N = f.shape[0]
        n = int(round(math.log2(N)))
        H0 = _baslangic_H(n)
        H1 = np.diag(np.asarray(f, float))
        e0, V0 = np.linalg.eigh(H0)
        psi = V0[:, 0].astype(complex)
        dt = T / adim
        for k in range(adim):
            s = (k + 0.5) / adim
            lam, V = np.linalg.eigh((1 - s) * H0 + s * H1)
            psi = (V * np.exp(-1j * lam * dt)) @ (V.conj().T @ psi)
        en_kucuk = float(np.min(f))
        hedef = np.isclose(f, en_kucuk)
        p = float((np.abs(psi[hedef]) ** 2).sum())
        return {"T": T, "başarı": p, "tam_1_mi": p == 1.0,
                "1_e_uzaklık": 1.0 - p,
                "asgarî_katlılık": int(hedef.sum())}

    raise ValueError("arama yolu bilinmiyor: %r" % (ne,))


def _baslangic_H(n: int) -> np.ndarray:
    """``H₀ = −Σ X_i`` — temel durumu ``|+⟩^{⊗n}``, **köşegen değil**."""
    N = 2 ** n
    H = np.zeros((N, N))
    for i in range(n):
        bit = 1 << (n - 1 - i)
        idx = np.arange(N)
        H[idx, idx ^ bit] -= 1.0
    return H


def tayf_araligi_asgari(f: np.ndarray, ornek: int = 101,
                        s_ust: float = 0.95) -> Dict[str, object]:
    """``g(s) = E₁ − E₀`` ve ``[0, s_ust]``te asgarîsi."""
    N = f.shape[0]
    n = int(round(math.log2(N)))
    H0 = _baslangic_H(n)
    H1 = np.diag(np.asarray(f, float))
    ss = np.linspace(0.0, 1.0, ornek)
    g = []
    for s in ss:
        e = np.linalg.eigvalsh((1 - s) * H0 + s * H1)
        g.append(float(e[1] - e[0]))
    g = np.array(g)
    mask = ss <= s_ust
    i = int(np.argmin(np.where(mask, g, np.inf)))
    return {"s": ss, "aralık": g, "g_min": float(g[i]),
            "s_min": float(ss[i]), "uç": float(g[-1])}


def _rapor_kuyu() -> str:
    s = ["=== akislar ==="]
    c = kuyudan_cik(ne="çukurlar")
    s.append("çift kuyu   sol=%.4f (f=%.4f)  eyer=%.4f  sağ=%.4f (f=%.4f)"
             % (c["sol_cukur"], c["f_sol"], c["eyer"], c["sag_cukur"], c["f_sag"]))
    t = kuyudan_cik(ne="tuzak")
    s.append("vektör akışı  sığ=%.4f → vardığı=%.4f  sığda kaldı=%s"
             % (t["sig_cukur"], t["vardigi"], t["sig_cukurda_kaldi"]))
    k = kuyudan_cik(ne="kaçış")
    s.append("topluluk akışı  kaçan kesir=%.3f  kaçtı=%s"
             % (k["toplulugun_kacan_kesri"], k["topluluk_kacti"]))
    g = kuyudan_cik(ne="gibbs")
    s.append("Gibbs kıyası  TV=%.4f uyuşuyor=%s   sol kütle: ampirik=%.3f gibbs=%.3f"
             % (g["toplam_degisim_uzakligi"], g["gibbs_ile_uyusuyor"],
                g["sol_cukur_kutlesi"], g["gibbs_sol_kutlesi"]))
    f = kuyudan_cik(ne="serbest_enerji")
    s.append("serbest enerji  düşüş=%.4f azaldı=%s  azamî ara artış=%.4f"
             % (f["toplam_dusus"], f["azaldi"], f["azami_ara_artis"]))
    e = egri_kisaltma()
    s.append("eğri kısaltma  r_sayısal=%.6f  r_kuram=%.6f  bağıl hata=%.2e  uyuşuyor=%s"
             % (e["r_sayisal"], e["r_kuram"], e["bagil_hata"], e["kanunla_uyusuyor"]))
    return "\n".join(s)


def _rapor_had() -> str:
    satirlar = ["=== kara_kutu ==="]
    a = had(ne="nfl", m=3, n=3)
    satirlar.append(
        "NFL tam sayım  m=%d n=%d  fonksiyon=%d usul=%d  izler aynı=%s  ortalamalar aynı=%s"
        % (a["nokta"], a["deger"], a["fonksiyon_sayisi"], a["usul_sayisi"],
           a["iz_dagilimlari_ayni"], a["ortalamalar_ayni"])
    )
    b = had(ne="kaçamak")
    satirlar.append(
        "NFL kaçamağı   tek tepeli sınıfta  rastgele=%.3f  üçdurum=%.3f  yapılı iyi=%s"
        % (b["rastgele_ortalama"], b["ucdurum_ortalama"], b["yapili_usul_daha_iyi"])
    )
    c = had(ne="zincir")
    satirlar.append(
        "Sıfır zinciri  destek=%s  adımla sınırlı=%s"
        % (c["destek_dizisi"], c["destek_adimla_sinirli"])
    )
    d = had(ne="alt_sınır")
    satirlar.append("Nesterov alt sınırı  ihlal yok=%s" % d["ihlal_yok"])
    return "\n".join(satirlar)


def _rapor_arayis() -> str:
    s = []
    N = 1024
    s.append("=== Grover eğrisi: fazla dönmek ZARARDIR ===")
    s.append("     K   m_opt   P(m_opt)   P(2·m_opt)   P(3·m_opt)")
    for K in (1, 4, 16, 64):
        m = en_iyiyi_ara(ne="tur", N=N, K=K)
        e = en_iyiyi_ara(ne="eğri", N=N, K=K, azami_tur=3 * m + 1)
        s.append("  %4d   %5d   %8.4f   %10.4f   %10.4f"
                 % (K, m, e[m], e[min(2 * m, len(e) - 1)],
                    e[min(3 * m, len(e) - 1)]))
    s.append("  Başarı m ile TEKDÜZE ARTMIYOR; sinüzoidal salınıyor.")

    s.append("\n=== M18: K bilinmezse m seçilemez ===")
    r = np.random.default_rng(0)
    f = r.random(N)
    K_gercek = 64
    esik = np.sort(f)[K_gercek]
    for varsayim, ad in ((1, "K=1 varsayıldı (YANLIŞ)"),
                         (K_gercek, "K=64 biliniyor (İMKÂNSIZ)")):
        m = en_iyiyi_ara(ne="tur", N=N, K=varsayim)
        d = en_iyiyi_ara(f, ne="grover", esik=esik, m=m)
        s.append("  %-28s m=%3d → başarı = %.4f"
                 % (ad, m, d["başarı_olasılığı"]))
    s.append("  'K biliniyor' hâli gerçekte kurulamaz: K, aramanın")
    s.append("  NETİCESİNE bağlıdır. Doğru çare rastgele tur çizelgesi:")

    s.append("\n=== Dürr–Høyer: K bilinmeden asgarîyi buluyor ===")
    s.append("      N    bulundu mu   sorgu   sorgu/√N")
    for n in (8, 10, 12):
        Nn = 2 ** n
        basari, sorgular = 0, []
        for t in range(20):
            ff = np.random.default_rng(100 + t).random(Nn)
            d = en_iyiyi_ara(ff, ne="dürr", tohum=t)
            basari += d["bulundu_mu"]
            sorgular.append(d["sorgu"])
        s.append("  %5d      %2d/20     %6.1f   %7.2f"
                 % (Nn, basari, float(np.mean(sorgular)),
                    float(np.mean(sorgular)) / math.sqrt(Nn)))
    s.append("  Sorgu sayısı √N'in küçük bir katı; K hiç bilinmedi.")

    s.append("\n=== M19: adiyabatik başarı sonlu T'de TAM 1 DEĞİL ===")
    n = 4
    ff = np.random.default_rng(5).random(2 ** n)
    ff[3] = -1.0                                  # tek asgarî
    t = tayf_araligi_asgari(ff)
    s.append("  g_min = %.6f (s=%.2f)   uçta g(1) = %.6f"
             % (t["g_min"], t["s_min"], t["uç"]))
    s.append("       T     başarı        1 − başarı    tam 1 mi?")
    for T in (1.0, 4.0, 16.0, 64.0, 256.0):
        a = en_iyiyi_ara(ff, ne="adiyabatik", T=T)
        s.append("  %6.1f   %.10f   %.3e     %s"
                 % (T, a["başarı"], a["1_e_uzaklık"], a["tam_1_mi"]))
    s.append("  T büyüdükçe 1'e YAKLAŞIYOR ama hiçbir sonlu T'de")
    s.append("  ULAŞMIYOR. '%100 doğrulukla' cümlesi bu yüzden yanlış")
    s.append("  (ve LaTeX'te '%' kaçırılmadığı için zaten görünmüyor).")

    s.append("\n=== Faz kehaneti gerçekten üniter mi? (kaynak DOĞRU) ===")
    for g in (0.3, 1.0, 3.0):
        d = faz_kehaneti(ff, g)
        s.append("  γ=%.1f  ‖diag(d)† diag(d) − I‖ = %.2e"
                 % (g, float(np.abs(np.abs(d) ** 2 - 1).max())))
    return "\n".join(s)

def rapor() -> str:                                     # pragma: no cover
    """KENDİNİ GÖSTERME -- **tek terkip** (kütük H223).

    Küme: on dört dosyanın ``rapor()``ları ve ``_gosterim``i. Her biri
    kendi ``s`` listesini kurup ayrı ayrı ``"\\n".join`` ediyordu; çipin
    bütün veçheleri artık **tek** gösterimde, sırayla akar.

    Bir motorun raporu, uzuvlarının adını saymakla olmaz; her birinin
    fiilen ısırdığı, kasten bozuk bir girdide **kırmızıya döndüğü**
    görülmelidir (H126, H90).
    """
    s: List[str] = ["TÂLİM VE ENİYİLEME ÇİPİ -- Küme 4 tevhidi"]

    def _bolum_1() -> List[str]:
        s: List[str] = []
        s += []
        rng = np.random.default_rng(0)

        s.append("=== Blok kodlama üniter mi? ===")
        for n in (2, 3, 5):
            A = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
            A = A / (np.linalg.norm(A, 2) * 1.2)      # ‖A‖₂ < 1
            U = blok_kodlama(A)
            s.append(f"  n={n}: ‖A‖₂={np.linalg.norm(A,2):.4f}"
                     f"   U üniter mi? {uniter_mi(U)}"
                     f"   geri okuma hatası = "
                     f"{np.max(np.abs(blok_kodlama(U, KIP_COZ, n) - A)):.2e}")
        try:
            blok_kodlama(2.0 * np.eye(2))
            s.append("  ‖A‖>1 kabul edildi (BEKLENMEZ)")
        except ValueError as e:
            s.append(f"  ‖A‖₂>1 reddedildi: {e}")

        s.append("\n=== QSP mihenk taşı 1 (Wx): bütün fazlar 0 → T_d ===")
        for d in (1, 2, 3, 5, 8, 12):
            fazlar = [0.0] * (d + 1)
            hata = 0.0
            for x in np.linspace(-1, 1, 201):
                p = faz_dizisinin_polinomu(fazlar, float(x), KIP_WX)
                hata = max(hata, abs(p.real - faz_dizisinin_polinomu(x=float(x), ne=KIP_CHEB, d=d)),
                           abs(p.imag))
            s.append(f"  d={d:2d}: max|⟨0|U|0⟩ − T_d(x)| = {hata:.3e}")
        s.append("  Sanal kısım da sıfır çıkıyor — polinom tam reel.")

        s.append("\n=== QSP mihenk taşı 2 (yansıma): orta fazlar π/2 → |T_d| ===")
        for d in (1, 2, 3, 5, 8, 11):
            f = [0.0] + [np.pi / 2] * (d - 1) + [0.0]
            h = max(abs(abs(faz_dizisinin_polinomu(f, float(x), KIP_YANSIMA))
                        - abs(faz_dizisinin_polinomu(x=float(x), ne=KIP_CHEB, d=d)))
                    for x in np.linspace(-0.99, 0.99, 201))
            s.append(f"  d={d:2d}: max‖P|−|T_d‖ = {h:.3e}")
        s.append("  İki konvansiyon AYNI fazlarla aynı polinomu vermez;")
        s.append("  QSVT devresi yansıma konvansiyonunda çalışır, o yüzden")
        s.append("  qsvt() de onu kullanır. Wx kullanılsaydı d≥3'te iki yol")
        s.append("  0.5 mertebesinde ayrışırdı — ölçülmüştü.")

        s.append("\n=== QSP üniterliği ve sınırı ===")
        for _ in range(3):
            d = int(rng.integers(2, 8))
            fazlar = list(rng.uniform(-np.pi, np.pi, d + 1))
            en_buyuk = 0.0
            uniter = True
            for x in np.linspace(-1, 1, 101):
                U = faz_dizisinin_polinomu(fazlar, float(x), KIP_UNITER)
                uniter = uniter and uniter_mi(U)
                en_buyuk = max(en_buyuk, abs(faz_dizisinin_polinomu(fazlar, float(x), KIP_WX)))
            s.append(f"  d={d}: üniter mi? {uniter}   max|P(x)| = {en_buyuk:.6f}"
                     f"   (≤1 olmalı)")

        s.append("\n=== QSP paritesi: d tek ⟹ P tek, d çift ⟹ P çift ===")
        for d in (3, 4, 5, 6):
            fazlar = list(rng.uniform(-np.pi, np.pi, d + 1))
            fark = max(abs(faz_dizisinin_polinomu(fazlar, x, KIP_WX)
                           - (-1) ** d * faz_dizisinin_polinomu(fazlar, -x, KIP_WX))
                       for x in np.linspace(0.05, 0.95, 40))
            s.append(f"  d={d}: |P(x) − (−1)^d P(−x)| azamî = {fark:.3e}")

        s.append("\n=== QSVT: iki bağımsız yol uyuşuyor mu? ===")
        for n in (2, 3, 4):
            A = rng.normal(size=(n, n))
            A = A / (np.linalg.norm(A, 2) * 1.3)
            for d in (1, 3, 5):
                fazlar = list(rng.uniform(-np.pi, np.pi, d + 1))
                svd_yolu = qsvt(A, fazlar)["P(A)"]
                devre_yolu = _devreyle_qsvt(A, fazlar)
                s.append(f"  n={n} d={d}: ‖SVD yolu − devre yolu‖∞ = "
                         f"{np.max(np.abs(svd_yolu - devre_yolu)):.2e}")

        s.append("\n=== 1/x yaklaşımı: dizey tersi, ters ALMADAN ===")
        for kappa in (4.0, 8.0):
            for derece in (11, 21, 41, 61):
                p = ters_polinomu(kappa, derece)
                x = np.linspace(1 / kappa, 1.0, 500)
                bagil = max(abs(p(float(xx)) * xx - 1.0) for xx in x)
                s.append(f"  κ={kappa:.0f} derece={derece:2d}: "
                         f"[1/κ,1] üzerinde azamî bağıl hata = {bagil:.3e}")
        s.append("  Aralık DIŞINDA 1/x sınırsızdır; hiçbir polinom yakalayamaz,")
        s.append("  o yüzden yaklaşımın geçerli aralığı açıkça yazılıyor.")

        s.append("\n=== Polinomu dizeye uygulamak ters veriyor — ama HANGİ ters? ===")
        s.append("  QSVT konvansiyonu P^SV(A) = Σ P(σ)|u⟩⟨v| verir; oysa")
        s.append("  A⁻¹ = Σ σ⁻¹|v⟩⟨u|. Yani u ile v YER DEĞİŞTİRİR ve netice")
        s.append("  A⁻¹ değil (A⁻¹)† olur. Ölçelim:")
        for n in (3, 4):
            B = rng.normal(size=(n, n))
            U_, _, Vh = np.linalg.svd(B)
            sg = np.linspace(0.3, 1.0, n)
            A = U_ @ np.diag(sg) @ Vh
            kappa = float(sg.max() / sg.min())
            p = ters_polinomu(kappa * 1.05, 61)
            PA = U_ @ np.diag([p(float(x)) for x in sg]) @ Vh
            inv = np.linalg.inv(A)
            n_inv = np.linalg.norm(inv, 2)
            s.append(f"  n={n} κ={kappa:.2f}:")
            s.append(f"    ‖P(A) − A⁻¹‖/‖A⁻¹‖    = "
                     f"{np.linalg.norm(PA - inv, 2) / n_inv:.3e}   ← uyuşmuyor")
            s.append(f"    ‖P(A) − (A⁻¹)†‖/‖A⁻¹‖ = "
                     f"{np.linalg.norm(PA - inv.conj().T, 2) / n_inv:.3e}"
                     f"   ← uyuşuyor")
            Ud, sd, Vd = np.linalg.svd(A.conj().T)
            PAd = Ud @ np.diag([p(float(x)) for x in sd]) @ Vd
            s.append(f"    P(A†) ile A⁻¹          = "
                     f"{np.linalg.norm(PAd - inv, 2) / n_inv:.3e}"
                     f"   ← A⁻¹ istiyorsan A† ver")
        s.append("  Bu bir kusur değil, konvansiyonun kendisidir; fakat")
        s.append("  farkedilmezse 'ters alındı' sanılıp eşleniği kullanılır.")
        s.append("  Hermitesel A'da ikisi çakışır, o yüzden hata orada gizlenir.")
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  QSVT -- blok kodlama, QSP ve tekil değer dönüşümü")
    s.append("=" * 70)
    s += _bolum_1()

    def _bolum_2() -> List[str]:
        s: List[str] = []
        s += ["CERİDENİN ÜÇ KAPALI-FORM BABI", ""]

        s.append("=== BAB: FCT -- GCL düğümlerinde XᵀX = I, κ = 1,0 ===")
        s.append("   M    ‖XᵀX − I‖        κ(XᵀX)      eş aralıkta κ")
        for M in (8, 16, 32, 64):
            X, w, d = chebyshev_tasarimi(M, KIP_TASARIM)
            G = X.T @ X
            E = chebyshev_tasarimi(M, KIP_ESARALIK)
            Ge = E.T @ E
            s.append("  %3d   %.3e     %.6f     %.3e"
                     % (M, np.linalg.norm(G - np.eye(M + 1)),
                        np.linalg.cond(G), np.linalg.cond(Ge)))
        s.append("  → GCL'de κ tam 1,0; eş aralıkta patlıyor (kırmızı).")
        M = 24
        x = chebyshev_tasarimi(M, KIP_DUGUM)
        f = np.exp(-3.0 * x ** 2) * np.cos(4.0 * x)
        a = chebyshev_tasarimi(M, KIP_KATSAYI, f=f)
        geri = chebyshev_tasarimi(M, KIP_DEGER, a=a, x=x)
        s.append("  düğümlerde geri-çatma hatası: %.3e   (ters matris YOK)"
                 % float(np.max(np.abs(geri - f))))

        s.append("")
        s.append("=== BAB: STA -- karşıt-adiyabatik sürüş ===")
        s.append("      τ     STA'sız sadakat   STA'lı sadakat   θ̇ uçta")
        for tau in (40.0, 8.0, 2.0, 0.5):
            a0 = kestirmeden_sur(tau, sta=False)
            a1 = kestirmeden_sur(tau, sta=True)
            s.append("  %6.1f      %10.6f      %10.6f     %.1e"
                     % (tau, a0["sadakat"], a1["sadakat"], a1["θ̇_uçta"]))
        s.append("  → τ küçüldükçe STA'sız sadakat düşüyor; sürüş tutuyor.")
        s.append("  → Ĥ_CD(0) = Ĥ_CD(τ) = 0 şartını CETVEL sağlıyor"
                 " (smoothstep), elle sıfırlama değil.")

        s.append("")
        s.append("=== BAB: Fubini-Study bilgi geometrisi ===")

        def dalga(th):
            a, b = float(th[0]), float(th[1])
            return np.array([math.cos(a) * math.cos(b),
                             math.cos(a) * math.sin(b),
                             math.sin(a), 0.0])

        th = np.array([0.4, 0.9])
        r = yokus(ne=KIP_DOGRULAMA, psi=dalga, teta=th)
        s.append("  g =\n%s" % np.array2string(r["g"], precision=6))
        s.append("  en küçük özdeğer %.3e   PSD: %s" %
                 (r["en_küçük_özdeğer"], r["psd"]))

        # İzdüşüm terimi atılırsa ölçek yönü sıfır uzayından çıkar:
        def olcekli(th):
            return (1.0 + 0.5 * float(th[2])) * dalga(th[:2])

        th3 = np.array([0.4, 0.9, 0.0])
        g3 = yokus(ne="sayısal", psi=olcekli, teta=th3)
        s.append("  ölçek yönünün Fubini uzunluğu : %.3e  (sıfır olmalı)"
                 % abs(float(g3[2, 2])))
        d = np.empty((3, 4))
        for k in range(3):
            e = np.zeros(3); e[k] = 1e-5
            p = lambda z: olcekli(z) / np.linalg.norm(olcekli(z))
            d[k] = (p(th3 + e) - p(th3 - e)) / 2e-5
        s.append("  (izdüşümsüz) ham ⟨∂₂Ψ|∂₂Ψ⟩     : %.3e  ← KIRMIZI olurdu"
                 % float(d[2] @ d[2] + 0.25))
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  CERİDE -- FCT, STA ve Fubini-Study")
    s.append("=" * 70)
    s += _bolum_2()

    def _bolum_3() -> List[str]:
        s: List[str] = []
        kg, ke = _kappa_olc(64)
        s.append("  κ(GCL)        = %.6f   (1'e oturmalı)" % kg)
        s.append("  κ(eşaralıklı) = %.3e   (kırmızı kontrol)" % ke)
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  FCT -- Gauss-Chebyshev-Lobatto, κ = 1,0")
    s.append("=" * 70)
    s += _bolum_3()

    def _bolum_4() -> List[str]:
        s: List[str] = []
        c = kestirmeden_sur(ne="cetvel")
        s += ["STA -- karşıt-adiyabatik sürüş", "",
             "  %8s %12s %12s" % ("tau", "sürüşlü", "sürüşsüz")]
        for r in c["satır"]:
            s.append("  %8.2f %12.6f %12.6f"
                     % (r["tau"], r["sürüşlü"], r["sürüşsüz"]))
        s.append("")
        s.append("  Sürüşsüz sütun hızlı geçişte çökmeli; çökmezse ölçü bozuk.")
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  STA -- karşıt-adiyabatik sürüş")
    s.append("=" * 70)
    s += _bolum_4()

    def _bolum_5() -> List[str]:
        s: List[str] = []
        c = fazlari_kilitle(None, ne="cetvel")
        s += ["BEC -- Gross-Pitaevskii faz kilidi", "",
             "  başlangıç faz uyumu T = %.6f" % c["başlangıç_T"], "",
             "  %8s %12s" % ("tur", "T")]
        for r in c["satır"]:
            s.append("  %8d %12.6f" % (r["tur"], r["T"]))
        s.append("")
        s.append("  tur=0 DÜŞÜK, tur büyüdükçe T→1 olmalı. tur=0 da yüksek")
        s.append("  çıkarsa ölçü kırmızı yanamıyor demektir.")
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  BEC -- Gross-Pitaevskii faz kilidi")
    s.append("=" * 70)
    s += _bolum_5()

    def _bolum_6() -> List[str]:
        s: List[str] = []
        rng = np.random.default_rng(0)
        d, C = 12, 10
        F = rng.normal(size=(20, d))
        W = rng.normal(size=(d, C))
        g, guv, det = izgarayi_oku(W, F, (4, 5), tekrar=3)
        k = yokus(ne="kıyas")
        s += ["FUBINI-STUDY DETERMİNİSTİK AĞAÇ OKUMASI", "",
             "  okunan ızgara (4×5):", "    " + str(g.tolist()),
             "  güven = %.4f" % guv,
             "  BELİRLENİMCİ Mİ (3 tekrar aynı mı): %s" % det, "",
             "  öznitelik metriği ↔ hakiki Fubini-Study:",
             "    iz(Fisher)=%.4f  iz(önşart)=%.4f  ölçek=%.4f"
             % (k["iz_fisher"], k["iz_önşart"], k["ölçek"]),
             "    bağıl fark=%.4f  → kısaltma olduğu ölçüyle sabit"
             % k["bağıl_fark"]]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  FUBINI-STUDY -- deterministik ağaç okuması")
    s.append("=" * 70)
    s += _bolum_6()

    def _bolum_7() -> List[str]:
        s: List[str] = []
        tohum = 0                      # nefs/ikiz.py rapor(tohum=0)
        r = purzu_yerini_bul(tohum)
        s += ["=== İKİZ SAYILAR -- H88'in pürüz suali cevaplanıyor ===", "",
             "H88 şöyle bırakmıştı: *'yönlü türev h→0'da tam oturmuyor…",
             "en kuvvetli şüpheli SVD kesmesidir. Bu hipotez ölçülmektedir",
             "ve neticesi çıkınca yazılacaktır.'*  Netice hiç yazılmamıştı,",
             "çünkü alet (sonlu fark) suali cevaplayamaz: pürüzü de kendi",
             "gürültüsünü de aynı belirtiyle gösterir.",
             "",
             "1. KADEME -- KAPI KURULUMU (exp(−2A), ikiz sayı ile TAM):",
             "     tam türev            : %+.8f" % r["kapı_tam_türev"],
             "     sonlu farkın en iyisi: h=%.0e, fark %.3e"
             % (r["kapı_en_iyi_h"], r["kapı_en_yakın_fark"]),
             "     PÜRÜZSÜZ MÜ          : %s" % r["kapı_pürüzsüz_mü"],
             "",
             "2. KADEME -- KESME SINIRINDAKİ BOŞLUK (s[χ−1] − s[χ]):",
             "     ölçülen nokta        : %d / %d"
             % (r["kesme_boşluğu_ölçüldü"], r["tarama_noktası"]),
             "     en dar nispî boşluk  : %.3e" % r["en_dar_boşluk"],
             "     sınırdaki tekil değer: %.3e  (gürültü mü?)"
             % r["sınır_büyüklüğü"],
             "     boşluk < %%1 olan nokta: %d" % r["kesme_sınırı_yakın"],
             "",
             "HÜKÜM -- iki parça, ikisi de haddiyle:",
             "  1. Kapı kurulumu **türevlenebilir**. Sonlu fark orada tam",
             "     türeve makine hassasiyetinde yaklaşıyor; o hâlde H88'in",
             "     gördüğü pürüz kapıdan gelmiyor. Bu KESİN.",
             "  2. Kesme bir **sıralamadır** ve sıralama ancak sınırdaki iki",
             "     tekil değer kesiştiğinde sıçrar. Yukarıdaki en dar boşluk",
             "     o kesişmeye ne kadar yaklaşıldığının ölçüsüdür.",
             "",
             "  YALANCI YEŞİL TUZAĞI ve nasıl kapandığı: ilk ölçümde boşluk",
             "  tam 0,000e+00 çıktı ve 'dejenere' diye okunacaktı. Halbuki",
             "  s[χ−1] ile s[χ] İKİSİ DE sıfırsa oran da sıfır çıkar --",
             "  orada kesilecek bir şey yoktur. Sınırdaki tekil değerin",
             "  BÜYÜKLÜĞÜ de raporlanıyor; gürültü mertebesindeyse hüküm",
             "  verilmez. Fren konunca hakikî boşluk ~%2 çıktı: küçüktür",
             "  fakat sıfır değildir, ve sınırdaki değerler gürültü değil.",
             "",
             "  O hâlde H88'in şüphelisi ÖLÇÜMLE DESTEKLENİYOR: %2'lik bir",
             "  boşluk, küçük bir parametre değişikliğiyle kolayca aşılır ve",
             "  aşıldığında tutulan altuzay yer değiştirir. Bu bir ispat",
             "  değil kuvvetli bir delildir; 'ispatlandı' denmiyor."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  İKİZ SAYILAR -- türevin tam hâli")
    s.append("=" * 70)
    s += _bolum_7()

    def _bolum_8() -> List[str]:
        s: List[str] = []
        n, tur, tohum = 40, 60, 0      # nefs/ogda.py rapor imzası
        rng = np.random.default_rng(tohum)

        # --- 1) ÖZDEŞLİK: kapalı form ile oyunun en iyisi aynı mı
        e = rng.uniform(0.0, 1.0, size=n)
        b = 8.0
        kapali = oyun_degeri(e, b)
        # en iyi w kapalı formda: softmax(β·e)
        z = b * e - np.max(b * e)
        w = np.exp(z) / np.sum(np.exp(z))
        oyun = oyun_degeri(e, b, w)
        ozdeslik = abs(kapali - oyun)

        # --- 2) OGDA yürüyor mu: hareketli bir hedefte
        t = OgdaTarti(n=n, beta=b, adim=0.5)
        sapma: List[float] = []
        for k in range(tur):
            ek = e + 0.15 * np.sin(0.3 * k + np.arange(n))
            t.guncelle(ek)
            sapma.append(abs(oyun_degeri(ek, b, t.w) - oyun_degeri(ek, b)))
        son = float(np.mean(sapma[-10:]))
        ilk = float(np.mean(sapma[:10]))

        # --- 3) KÖRLÜK: iyimserlik kaldırılınca kötüleşiyor mu
        t2 = OgdaTarti(n=n, beta=b, adim=0.5)
        sapma2: List[float] = []
        for k in range(tur):
            ek = e + 0.15 * np.sin(0.3 * k + np.arange(n))
            t2.g_onceki = np.asarray(ek, float)      # 2g−g = g → sıradan GDA
            t2.guncelle(ek)
            sapma2.append(abs(oyun_degeri(ek, b, t2.w) - oyun_degeri(ek, b)))
        son2 = float(np.mean(sapma2[-10:]))

        s += ["=== OGDA -- kaybın min-max olduğunun farkedilmesi ===", "",
             "Özdeşlik (Fenchel):",
             "    max_w [⟨w,e⟩ + H(w)/β]  =  (1/β)·log Σ exp(β·e_i)",
             "  iki taraf arasındaki fark : %.3e  ← sıfır olmalı" % ozdeslik,
             "",
             "Yani padişahın eğitimi baştan beri şu oyunmuş:",
             "    min_p max_w [ ⟨w, e(p)⟩ + H(w)/β ]",
             "ve ben onu tek taraflı bir asgarîleme sanıyordum.",
             "",
             "OGDA HAREKETLİ HEDEFTE (%d tur):" % tur,
             "  ilk 10 turun sapması : %.4f" % ilk,
             "  son 10 turun sapması : %.4f" % son,
             "  iyimserlik KALDIRILINCA (sıradan GDA): %.4f" % son2,
             "  nispet (GDA / OGDA)  : %.3f" % (son2 / max(son, 1e-12)),
             "",
             "  HÜKÜM -- ve fazlası söylenmiyor: iyimserliğin kazancı",
             "  %.1f%%'tir, yani **fiilen yoktur**. Dahası sapma turlarla"
             % (100.0 * (son2 / max(son, 1e-12) - 1.0)),
             "  BÜYÜYOR (%.4f → %.4f), yani OGDA burada hedefi kovalıyor"
             % (ilk, son),
             "  fakat yakalayamıyor. Sebep bellidir ve kusur değildir:",
             "  ``w`` tarafının en iyisi zaten **kapalı formda** biliniyor",
             "  (yukarıdaki özdeşlik, fark 0). Kapalı formu olan bir",
             "  problemi yürüyerek çözmenin kazanacağı bir şey yoktur.",
             "",
             "  O hâlde ceridenin OGDA hükmünden alınan şey **çözücü değil",
             "  TEŞHİStir**: kaybın bir oyun olduğunun ispatı. Çözücü",
             "  olarak faydası ölçüldü ve **çıkmadı**; iddia edilmiyor.",
             "  OGDA'nın hakikaten lâzım olacağı yer, ``w`` ile ``p``nin",
             "  BERABER yürütüldüğü hâldir -- orada ``w``nin kapalı formu",
             "  ``p`` değiştikçe geçersizleşir. O hâl henüz kurulmadı.",
             "",
             "β'nın manası da değişiyor: bir kalibrasyon sabiti değil,",
             "**düşmanın ne kadar düzenlendiği**. H164/H169'da ona bir",
             "sezgi (√n) koymuştum ve ölçüm çürütmüştü; oyun görüşü o suali",
             "sezgiden çıkarıp nazariyeye taşıyor.",
             "",
             "İDDİA EDİLMEYEN: OGDA'nın yakınsama teoremi dışbükey-içbükey",
             "oyunlar içindir. Burada e(p) p'de dışbükey DEĞİLDİR; teorem",
             "yalnız w tarafına tatbik edilir, oyunun tamamına değil."]
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  OGDA -- kaybın min-max olduğunun farkedilmesi")
    s.append("=" * 70)
    s += _bolum_8()

    def _bolum_9() -> List[str]:
        s: List[str] = []
        tohum, n, d_in = 0, 6, 12      # nefs/gaye.py rapor imzası
        from nefs.melekeler import QNefs
        from nefs.zihin_durumu import QAyar

        E = np.random.default_rng(tohum).normal(size=(n, d_in))
        s += ["=== GAYE (Dosya 4) -- muhtar gaye, Landauer, sükût eşiği ===",
             "",
             "H108 'gaye alanı hükümle dolaştırılır' diyordu. ÖLÇÜLDÜ:",
             "alan tam olarak |0⟩'daydı, yani hiç yazılmamıştı. Burada",
             "nakzedilir ve icra edilir.",
             ""]
        satirlar = []
        for acik in (False, True):
            q = QNefs(tohum, QAyar(bag=16, tohum=tohum), gaye=acik).idrak_et(E)
            alanlar = {}
            for ad, kac in q.ayar.kulli_alanlar:
                yuv = [q.kulli(ad, j) for j in range(kac)]
                R = np.asarray(q.y.tekil_yogunluklar(yuv), float)[0]
                alanlar[ad] = float(R[:, 1, 1].mean())
            satirlar.append((acik, alanlar, odenen_bedel(q, "landauer"),
                             odenen_bedel(q, "serbest")))

        adlar = [ad for ad, _ in satirlar[0][1].items()]
        s.append("  %-10s %12s %12s" % ("alan", "gaye KAPALI", "gaye AÇIK"))
        for ad in adlar:
            s.append("  %-10s %12.6f %12.6f"
                     % (ad, satirlar[0][1][ad], satirlar[1][1][ad]))

        s += ["", "LANDAUER DEFTERİ (akıştaki tek tersinmez adım: kesme):"]
        for acik, _, L, _ in satirlar:
            s.append("  gaye %-7s sadakat=%.3e  silinen bit=%.1f  "
                     "kübit başına %.3f"
                     % ("AÇIK" if acik else "KAPALI", L["sadakat"],
                        L["silinen_bit"], L["kübit_başına_bit"]))

        s += ["", "SERBEST ENERJİ (fitrat/serbest_enerji.py ile):"]
        for acik, _, _, F in satirlar:
            s.append("  gaye %-7s F=%.6f  kesinsizlik=%.6f  karmaşıklık=%.6f"
                     "  ayrışım sapması=%.1e"
                     % ("AÇIK" if acik else "KAPALI", F["F"], F["kesinsizlik"],
                        F["karmaşıklık"], F["ayrışım_sapması"]))
        s += ["",
              "Ayrışım sapması, `fitrat`ın F = kesinsizlik + karmaşıklık",
              "kimliğinin bu sayılarda fiilen tuttuğunun şahididir; sıfıra",
              "yakın olmalıdır. Gayenin faydası bu tabloda İDDİA EDİLMEZ --",
              "sayılar konur, hüküm ölçüme bırakılır."]
        return s
        return s

    s.append("")
    s.append("=" * 70)
    s.append("  GAYE -- teleolojik akış ve ödenen bedel")
    s.append("=" * 70)
    s += _bolum_9()
    return "\n".join(s)


if __name__ == "__main__":                              # pragma: no cover
    print(rapor())
