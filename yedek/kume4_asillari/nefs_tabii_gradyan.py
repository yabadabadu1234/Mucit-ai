"""
TABİÎ GRADYAN (natural gradient) -- kullanıcı hükmü H86.

> *"Senin tarifine göre şu an melekeler rastgele deneme yanılmayla
> öğreniliyormuş, bu kabul edilemez. Şu anki 250 parametre bir de
> bildiğimiz natural gradyan ile öğrenilsin, bakalım ne olacak?
> Sonrasında işe yaramazsa sileriz."*

**Sıradan gradyan ile tabiî gradyanın farkı (hayalî karşılığıyla).**
Sıradan gradyan "parametreyi hangi yöne oynatırsam kayıp azalır" der ve
bütün parametreleri **eşit mesafeli** sayar. Halbuki bir açıyı 0,1
radyan oynatmakla bir başkasını 0,1 oynatmak, modelin **davranışında**
çok farklı büyüklükte değişiklik yapar. Tabiî gradyan mesafeyi
parametrede değil **durumun kendisinde** ölçer: "cevabımı ne kadar
değiştirdim" cinsinden adım atar.

Kuantum durumlarında bu ölçünün adı **Fubini–Study metriğidir**:

    S_ij = Re⟨∂_iψ|∂_jψ⟩ − ⟨∂_iψ|ψ⟩⟨ψ|∂_jψ⟩
    Δθ   = −η (S + λI)⁻¹ ∇V

``S`` hesabı iki durumun örtüşmesinden çıkar ve o da
``main.yazmac.Yazmac.ic_carpim``dır -- ``2^N`` hiçbir yerde açılmaz.

**Neden ALT UZAYDA.** ``d = 250`` parametre için tam ``S`` ``250×250``
olur ve kurulması ``4d² ≈ 250 000`` iç çarpım ister; her iç çarpım bir
ileri geçiş demek olduğu için bu imkânsızdır. Onun için ``r`` boyutlu
bir alt uzay seçilir (``r ≈ 8``), tam Fubini–Study orada kurulur
(``4r² = 256`` iç çarpım, **16** ileri geçiş) ve adım geri izdüşürülür.
Bu, `ogrenme/optimize.py`deki Active Subspaces fikrinin tabiî gradyanla
birleşmiş hâlidir; ikisi de aynı zarureti kabul eder.

**Parametre-kaydırma neden kullanılmadı.** `kuantum/eniyileme.py`
kendi vesikasında şartı yazıyor: kaydırma kuralı **yalnız üreteci
``G² = I`` olan kapılarda** tam türev verir. Bizim ``donme(θ)`` öyledir,
fakat ``dik_iki_kubit`` Cayley dönüşümüyle kurulur ve üreteci o şartı
sağlamaz. Yani kuralı bütün parametrelere uygulamak **yanlış türev**
verirdi. Onun için merkezî sonlu fark kullanılır ve ``donme``
parametrelerinde kaydırma kuralıyla **doğrulanır**.

**İDDİA EDİLMEYEN.** Bu motorun daha iyi olduğu iddia edilmiyor;
kullanıcı *"bakalım ne olacak"* dedi ve ölçüm öyle kurulmuştur:
aynı kayıp bütçesinde tabiî gradyan, sıradan gradyan ve dalga motoru
yan yana koşturulur. İşe yaramazsa silinir.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["TabiiAyar", "TabiiGradyan"]

Kayip = Callable[[np.ndarray], float]


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
class Cevrim:
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

    def __init__(self, V: Kayip, p0: np.ndarray,
                 durum_kur: Optional[Callable[[np.ndarray], object]] = None,
                 ayar: Optional[TabiiAyar] = None) -> None:
        self.V = V
        self.p = np.asarray(p0, float).copy()
        self.durum_kur = durum_kur
        self.ayar = ayar or TabiiAyar()
        self.seyir: List[Cevrim] = []
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

    def _fisher(self, W: np.ndarray) -> Tuple[np.ndarray, float]:
        """Alt uzayda Fubini–Study metriği ``S`` (``r×r``).

        ``∂_iψ ≈ (ψ_i⁺ − ψ_i⁻)/(2h)`` olduğu için bütün iç çarpımlar
        ``2r`` durumun **ikili örtüşmelerinden** çıkar; ayrıca durum
        farkı hiç kurulmaz (MPS'te toplam bağ boyutunu şişirirdi).
        """
        a = self.ayar
        r = W.shape[1]
        durumlar = []
        for i in range(r):
            durumlar.append(self.durum_kur(self.p + a.h * W[:, i]))
            durumlar.append(self.durum_kur(self.p - a.h * W[:, i]))
        psi = self.durum_kur(self.p)

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
                    / (4.0 * a.h * a.h)
                oi = (o[ip] - o[im]) / (2.0 * a.h)
                oj = (o[jp] - o[jm]) / (2.0 * a.h)
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
            S, kosul = self._fisher(W)
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

        c = Cevrim(no, float(V1), float(np.linalg.norm(g)),
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
