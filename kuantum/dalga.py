"""
Patlamasız dalga eniyilemesi: faz orağı → difüzyon → girişim → çöküş.

Vesikadaki dört merhale aynen icra edilir:

    |Ψ₀⟩ = Σ_x ψ_θ(x)|x⟩ / √Z                      (kompakt süperpozisyon)
    U_L  = Σ_x e^{−iγL(x)} |x⟩⟨x|                  (kayıp = faz)
    D    = 2|Ψ₀⟩⟨Ψ₀| − I                           (difüzyon)
    G    = D·U_L ,  |Ψ_k⟩ = G^k|Ψ₀⟩ → |x*⟩         (girişim ve çöküş)

**``2^N`` hiçbir yerde açılmaz.** Bunun sebebi bir hile değil, cebrin
kendisidir: ``U_L`` köşegen, ``D`` ise rütbe-bir düzeltmedir. Onun için
``G^k|Ψ₀⟩``ın genliği daima

    ψ_k(x) = ψ₀(x) · P_k( z(x) ) ,   z(x) = e^{−iγL(x)}

şeklindedir; ``P_k`` derecesi ``k`` olan bir polinomdur ve katsayıları
yalnız **momentlere** bağlıdır:

    m_j = 𝔼_{x∼|ψ₀|²}[ z(x)^j ] ,   s = ⟨Ψ₀|ψ⟩ = Σ_j a_j m_j
    a ← 2 s e₀ − shift(a)

Yani bütün Grover özyinelemesi ``k+1`` sayı üzerinde yürür. Bellek
``O(k)``dır; ``N`` hiç girmez. Kaggle'daki 84 GB VRAM'in tamamı boş
kalır -- ihtiyaç yoktur.

**EŞİK ORAĞI ve neden asıl yol odur.** ``z`` sürekli bir faz olunca
girişim "faz uyumu" (phase matching) şartına takılır ve Grover'ın kesin
neticesi kaybolur. Klasik Grover orağı ikilidir: ``z = −1`` (iyi),
``z = +1`` (kötü). O hâlde ``z``nin aldığı iki değer vardır, polinom
uzayı **iki boyuta** çöker ve özyineleme kapalı formda çözülür:

    α ← 2s − (−α) ... yani  (α_{k+1}, β_{k+1}) = (2s + α_k, 2s − β_k),
    s = −μ α_k + (1−μ) β_k ,  μ = P(iyi)

Bu, Grover'ın tam ve ispatlı hâlidir; ``k ≈ (π/4)/√μ`` de buradan çıkar.

**AŞIRI İDDİA ETMİYORUM.** Klasik bir GPU'da bu usul ``√`` hızlanma
**vermez**; Grover'ın hızlanması kuantum donanımına aittir. Burada
kazanılan şey başkadır ve ölçülebilir:

1. **Gradyansız**: ``∇L`` hiç alınmaz (kütük H3).
2. **Kapalı form**: en iyi ``k`` ve neticedeki yoğunlaşma analitik
   olarak bilinir, aranmaz.
3. **Kapalı formda öğrenme**: NQS'in son katı ``log ψ``de doğrusaldır;
   hedef genliğe **en küçük karelerle** oturtulur. Adam/SGD yoktur.
4. **Mahallî çukur**: eşik Dürr–Høyer usulüyle indirilir; dalga bütün
   uzayı aynı anda tartar, tek bir noktadan yürümez.

Bu dördü ölçülür ve raporlanır; beşincisi iddia edilmez.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from .nqs import NQS

__all__ = ["moment_kestir", "grover_katsayilari", "en_iyi_k",
           "grover_ikili", "DalgaEniyileyici"]

Kayip = Callable[[np.ndarray], np.ndarray]      # (B,n) → (B,)


# =====================================================================
#  1. Sürekli faz orağı: momentler ve polinom özyinelemesi
# =====================================================================
def moment_kestir(z: np.ndarray, k: int) -> np.ndarray:
    """``m_j = 𝔼[z^j]``, ``j = 0..k``. ``m₀ = 1`` **tam olarak**."""
    m = np.empty(k + 1, complex)
    kuvvet = np.ones_like(z)
    for j in range(k + 1):
        m[j] = 1.0 + 0j if j == 0 else kuvvet.mean()
        kuvvet = kuvvet * z
    return m


def grover_katsayilari(m: np.ndarray, k: int) -> np.ndarray:
    """``P_k``ın katsayıları: ``a ← 2(Σ_j a_j m_j) e₀ − shift(a)``."""
    a = np.zeros(1, complex)
    a[0] = 1.0
    for _ in range(k):
        ap = np.concatenate([[0.0 + 0j], a])          # z ile çarp
        s = complex(np.dot(ap, m[:len(ap)]))
        yeni = -ap
        yeni[0] += 2.0 * s
        a = yeni
    return a


def _polinom(a: np.ndarray, z: np.ndarray) -> np.ndarray:
    y = np.zeros_like(z)
    for c in a[::-1]:
        y = y * z + c
    return y


# =====================================================================
#  2. İkili (eşik) orak: Grover'ın TAM hâli, iki boyutta kapalı form
# =====================================================================
def grover_ikili(mu: float, k: int) -> Tuple[float, float]:
    """``(α_k, β_k)``: iyi ve kötü hâllerin genlik çarpanları.

    ``α₀ = β₀ = 1``. Her adımda ``U_L`` iyilerin işaretini çevirir,
    ``D`` ise ortalamaya göre yansıtır::

        s = −μ α + (1−μ) β ,   α ← 2s + α ,   β ← 2s − β

    Sabit noktası yoktur; ``sin((2k+1)θ)`` ile salınır (``sin θ = √μ``).
    Bu yüzden ``k``yı büyütmek daima iyileştirmez -- **fazla dönmek
    geri götürür**. ``en_iyi_k`` bunu hesaba katar.
    """
    al = be = 1.0
    for _ in range(max(int(k), 0)):
        s = -mu * al + (1.0 - mu) * be
        al, be = 2.0 * s + al, 2.0 * s - be
    return al, be


def en_iyi_k(mu: float) -> int:
    """``k* = round( (π/2 − θ) / (2θ) )``, ``θ = arcsin √μ``.

    Vesikadaki ``(π/4)√(2^N/M)`` bunun ``μ → 0`` haddidir; küçük uzayda
    o yaklaşım fazla döndürür, tam formül döndürmez.
    """
    mu = float(min(max(mu, 1e-12), 1.0))
    teta = math.asin(math.sqrt(mu))
    if teta <= 1e-9:
        return 0
    return max(0, int(round((math.pi / 2 - teta) / (2 * teta))))


def _ess(w: np.ndarray) -> float:
    """Müessir örnek sayısı: ``(Σw)² / Σw²``."""
    s1 = float(w.sum())
    s2 = float((w * w).sum())
    return (s1 * s1 / s2) if s2 > 0 else 0.0


def _tartili(L: np.ndarray, beta: float, taban_ess: float = 0.25
             ) -> np.ndarray:
    """``w ∝ exp(−sβ(L−L_min))``; ``s``, **müessir örnek sayısı** tabanı
    tutacak en büyük değer olarak ikiye bölerek bulunur.

    Ham ``s=1`` kuruldu ve ölçüldü: Rastrigin'de ``β·ΔL ≈ 67`` olduğu
    için tartı bir avuç noktaya çöküyor, uydurma o birkaç noktayı
    ezberliyor ve netice bozuluyordu (48,6; tartısız 43,8; rastgele
    35,4). Yani ne tartısız ne de tam tartılı doğrudur; doğru olan,
    tartının **kaç noktayı fiilen kullandığını** şart koşmaktır.
    """
    d = np.asarray(L, float) - float(np.min(L))
    n = len(d)
    hedef = taban_ess * n
    if _ess(np.exp(np.clip(-beta * d, -700, 0))) >= hedef:
        return np.exp(np.clip(-beta * d, -700, 0))
    alt, ust = 0.0, 1.0
    for _ in range(40):
        s = 0.5 * (alt + ust)
        w = np.exp(np.clip(-s * beta * d, -700, 0))
        if _ess(w) >= hedef:
            alt = s
        else:
            ust = s
    return np.exp(np.clip(-alt * beta * d, -700, 0))


# =====================================================================
@dataclass
class Cevrim:
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

    def __init__(self, nqs: NQS, L: Kayip, tohum: int = 0) -> None:
        self.nqs = nqs
        self.L = L
        self.tohum = int(tohum)
        self.seyir: List[Cevrim] = []
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

        k = en_iyi_k(mu)
        al, be = grover_ikili(mu, k)

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
        w = _tartili(self.tampon_L, self.beta_tavlama, taban_ess=0.25)
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
        wt = _tartili(self.tampon_L, self.beta_tavlama, taban_ess=0.10)
        wt = wt / (wt.sum() + 1e-300)
        self.kenar = (self.tampon_X * wt[:, None]).sum(0)

        c = Cevrim(no, esik, mu, k, al, be, p_once, p_sonra,
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
        m = moment_kestir(z, k)
        a = grover_katsayilari(m, k)
        P = _polinom(a, z)
        w = np.abs(P) ** 2
        w = w / (w.sum() + 1e-300)
        duz = np.ones(len(Ld)) / len(Ld)
        return {"γ": gama, "k": float(k),
                "ağırlıklı_L": float(np.dot(w, Ld)),
                "düz_L": float(np.dot(duz, Ld)),
                "en_iyi_L": float(Ld.min()),
                "yoğunlaşma": float(np.dot(w, Ld) - Ld.min())
                / (float(np.dot(duz, Ld) - Ld.min()) + 1e-12)}
