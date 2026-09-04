"""
Nöral Ağ Kuantum Durumu (NQS, Carleo–Troyer) -- KAN çekirdeğiyle.

Vesikadaki hüküm:

    |Ψ⟩ = Σ_{x∈{0,1}^N} ψ_θ(x)|x⟩ ,   ψ_θ(x) = exp( Σ_k KAN_k(x) )

**Meselenin kendisi.** ``2^N`` boyutlu bir uzayı bellekte **açmadan**
temsil etmek. MERA/MPS bunu bağ boyutu ``χ`` ile yapar ve ``χ`` alan
kanununa bağlıdır; kayıp yüzeyi hacim kanununa sıçrayınca ``χ ~ 2^{N/2}``
olur ve patlar (kütük H52'de bizzat ölçüldü: ARC için ``10³⁰``). NQS'te
durum bir **dizi değil, fonksiyondur**: hangi ``x`` sorulursa onun
genliği ``O(1)`` sürede hesaplanır. Bellek ``2^N`` değil,
``dim(θ)`` kadardır.

**Neden KAN.** Klasik RBM/MLP çekirdeğinde doğrusalsızlık düğümdedir ve
sabittir. KAN'da doğrusalsızlık **kenardadır** ve öğrenilir: her kenar
bir tek değişkenli fonksiyondur, Chebyshev tabanında açılır. Bu, bizim
mimarîye iki sebeple uygundur:

1. Kütük H3: *"uydurma = RKHS kapalı formu / KAN sembolik kapanışı /
   FNO spektrali."* KAN zaten hükmün içindedir, dışarıdan gelmemiştir.
2. Chebyshev katsayıları **sembolik olarak okunabilir**; öğrenilen şey
   bir kara kutu ağırlık yığını değil, açıkça yazılabilen bir
   fonksiyondur. Kütük H4'ün "hüküm veren meleke sembolik kalır"
   şartıyla çelişmez.

**Faz.** Son katman **karmaşıktır**: ``log ψ = a + i b``. Genliğin
sadece büyüklüğü değil **fazı** da öğrenilir; girişimin (interference)
mümkün olmasının şartı budur. Reel bir dalga ile Grover yapılamaz.

**Örnekleme.** ``|ψ|²``den örnek çekmek için Metropolis kullanılır
(tek bit çevirme, çok zincir, yığın hâlinde). Bu, NQS'in tabiî usulüdür;
``2^N`` üzerinden normalizasyon hiç hesaplanmaz -- zaten hesaplanamaz.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from hesap.donanim import Donanim, donanim, topla_paralel

__all__ = ["NQSAyar", "NQS", "chebyshev"]


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
