"""
ŞÜPHE MANİFOLDU -- TEÂRUZ, MODALİTE, MERAK VE LIOUVILLE SÖNÜMÜ

===================================================================
ŞÜPHE BİR EKSİKLİK DEĞİL, BİR ÖLÇÜDÜR
===================================================================

Bir dimağ her hâlde hüküm veriyorsa ya her şeyi biliyordur ya da
hiçbir şeyi. İkincisi vâkidir. Şüphe manifoldu, "bilmiyorum"u bir
kaçamak olmaktan çıkarıp **ölçülen bir hâl** yapar.

===================================================================
1. TEÂRUZ -- ``P`` İLE ``¬P`` DENK KUVVETTE
===================================================================

    μ ← μ · (1 − |⟨ψ_P | ψ_¬P⟩|)

İki kol birbirini tam örtüyorsa (``|⟨·⟩| = 1``) yakîn **sıfırlanır**:
delil hem tezi hem antitezi aynı kuvvette destekliyor demektir ve o
hâlde hüküm verilmez, **tevakkuf** edilir.

``¬P`` nereden gelir? Uydurulmaz: **mantıkî X operatörüdür** (``X̄``,
bkz. ``nefs/sadakat.py:mantiki_degil``). Tez ile antitez aynı cebirden
çıkar, ayrı bir "olumsuzlama modeli" yoktur.

**BİR ÖLÇÜM YANLIŞI BURADA DÜZELTİLDİ.** Evvelce ``¬P``yi stabilizerin
kendisiyle (``Ŝ|ψ⟩``) kurmuştum. Ölçüldü: ``sadakat_uygula``dan sonra
durum zaten ``Ŝ``nin ``+1`` öz-uzayındadır, o hâlde örtüşme **daima tam
1** çıkıyor, yakîn her seferinde sıfırlanıyor ve model **her göreve
susuyordu** (çıkarımda 4/4). Daima aynı sayıyı veren bir ölçü hiçbir
şey ölçmüyordur (ferman 5). ``X̄`` kod uzayını kendine götürür fakat
hükmü çevirir; teâruz ancak tez ile antitez hakikaten ayırt edilemezse
tam çıkar.

===================================================================
2. MODAL DALLANMA -- ZORUNLU / MÜMKÜN / MUHÂL
===================================================================

Bir hükmün kipi ``ω`` holonomisinden okunur:

    ω ≈ +1   zorunlu   (çevrim kendine kapanıyor, kaçış yok)
    |ω| < κ  mümkün    (dallanma var: birden çok dünya tutarlı)
    ω ≈ −1   muhâl     (kendi aksiyomunu inkâr ediyor)

"Mümkün" hâlinde şüphe **artar**, çünkü tutarlı birden çok dünya
varken tekini seçmek delilsiz zandır.

===================================================================
3. MERAK KANCASI
===================================================================

Şüphe kendi başına bir durgunluk değildir; ``nefs/usul.py``nin
seferine **gaye** üretir. Şüphesi en yüksek hâller merak kancasına
takılır ve sefer sırasında öne alınır.

===================================================================
4. LIOUVILLE SÖNÜMÜ -- DELİLSİZ ZAN BUHARLAŞIR
===================================================================

    dμ/dt = −γ μ      →      μ ← μ·(1 − γ)

Yeni delil gelmeyen bir zan, tekrarlandığı için kuvvetlenmez; aksine
zamanla söner. Bu, ``nefs/hafiza.py``nin Liouville sönümüyle **aynı
denklemdir** ve orada yoğunluk operatörüne, burada yakîn skalerine
uygulanır -- ikisi aynı hareketin iki yüzüdür (ferman 3).

===================================================================
ÖLÇÜ KIRMIZI YANABİLİR (FERMAN 5)
===================================================================

``SupheAyari.acik = 0`` denince manifold koşmaz: ``tevakkuf`` sıfır
olur, yâni model her hâlde hüküm verir. Rapor bunu yazar.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional, Sequence

import numpy as np

__all__ = ["SupheAyari", "tearuz", "modal_kip", "suphe_manifoldu",
           "suphe_beyani", "suphe_sifirla"]


@dataclass
class SupheAyari:
    """Şüphe manifoldunun ölçüleri."""

    #: ``0`` = manifold KAPALI: model her hâlde hüküm verir.
    acik: int = 1
    #: ``γ`` -- Liouville sönümü: delilsiz zannın buharlaşma hızı.
    sonum: float = 0.05
    #: ``κ`` -- "mümkün" kipinin genişliği.
    kip_kenari: float = 0.25
    #: Tevakkuf eşiği: yakîn bunun altına inerse hüküm verilmez.
    tevakkuf_esigi: float = 0.35
    #: Merak kancasının eşiği: şüphe bunu aşarsa sefere gaye olur.
    merak_esigi: float = 0.5
    #: Parite lifi -- ``¬P`` eşleniği buradan kurulur (``nefs/sadakat.py``).
    parite_lifi: int = 2
    lif_yapisi: tuple = (16, 16, 16)


_SAYAC: Dict[str, float] = {
    "çağrı": 0.0, "tearuz": 0.0, "dallanma": 0.0, "merak": 0.0,
    "buhar": 0.0, "tevakkuf": 0.0, "örnek": 0.0,
    "μ_önce": 0.0, "μ_sonra": 0.0}


def tearuz(psi_p: np.ndarray, psi_np: np.ndarray) -> float:
    """``|⟨ψ_P | ψ_¬P⟩|`` -- tezin antitezle örtüşmesi.

    ``1``e yakınsa teâruz tamdır: delil ikisini ayırmıyor.
    """
    a = np.asarray(psi_p, complex).reshape(-1)
    b = np.asarray(psi_np, complex).reshape(-1)
    na = max(float(np.linalg.norm(a)), 1e-300)
    nb = max(float(np.linalg.norm(b)), 1e-300)
    return float(abs(complex(np.vdot(a / na, b / nb))))


def modal_kip(omega: float, kenar: float = 0.25) -> str:
    """``ω``dan kip: zorunlu / mümkün / muhâl."""
    if omega > 1.0 - kenar:
        return "zorunlu"
    if omega < -1.0 + kenar:
        return "muhâl"
    return "mümkün"


def suphe_manifoldu(haller: Sequence[np.ndarray],
                    omegalar: Sequence[float],
                    yakin: Optional[np.ndarray] = None,
                    ayar: Optional[SupheAyari] = None) -> Dict[str, Any]:
    """Dört ameliyeyi sırayla koştur ve **yakîni** güncelle.

    ``yakin`` verilmezse hâllerin normundan kurulur (başlangıçta her
    hâl eşit kuvvette bir zandır). Dönen ``μ``, mizanın tevakkuf
    kararını ve seferin gaye sırasını besler.
    """
    from .sadakat import SadakatAyari
    a = ayar or SupheAyari()
    _SAYAC["çağrı"] += 1.0
    m = len(haller)
    if m == 0 or not int(a.acik):
        return {"μ": np.zeros(0), "tevakkuf": 0, "tearuz": 0,
                "dallanma": 0, "merak": [], "açık": bool(int(a.acik))}

    H = np.stack([np.asarray(h, complex).reshape(-1) for h in haller])
    H = H / np.maximum(np.linalg.norm(H, axis=-1, keepdims=True), 1e-300)
    mu = (np.ones(m, float) if yakin is None
          else np.asarray(yakin, float).reshape(-1).copy())
    assert mu.size == m, "yakîn vektörü %d, hâl %d" % (mu.size, m)
    _SAYAC["μ_önce"] += float(np.mean(mu))

    # ── 1. TEÂRUZ ─────────────────────────────────────────────────
    # ``¬P`` **mantıkî olumsuzlamadır** (``X̄``), stabilizerin kendisi
    # değil. Sebebi ``nefs/sadakat.py:mantiki_degil``de yazılı ve
    # ölçülmüştür: ``Ŝ|ψ⟩`` alınırsa örtüşme daima tam 1 çıkar ve
    # teâruz hiçbir şey ölçmez.
    from .sadakat import mantiki_degil
    sa = SadakatAyari(acik=1, parite_lifi=int(a.parite_lifi),
                      lif_yapisi=tuple(a.lif_yapisi))
    d = H.shape[1]
    lif_carpim = 1
    for x in a.lif_yapisi:
        lif_carpim *= int(x)
    if d == lif_carpim:
        S = mantiki_degil(H, sa)
    else:
        # Hâl belirteç lifidir (``n_v``), hükmün tamamı değil. ``X̄``
        # orada indisin en düşük **iki** basamağını çevirir: parite
        # korunur (çift popcount), hüküm çevrilir. Aynı operatörün
        # daha küçük uzaya kısıtı -- uydurma değil.
        maske = 3 if d >= 4 else 1
        S = H[:, np.arange(d) ^ maske]
    ortusme = np.abs(np.einsum('ij,ij->i', H.conj(), S))
    mu = mu * (1.0 - ortusme)
    t_say = int(np.count_nonzero(ortusme > 1.0 - float(a.kip_kenari)))
    _SAYAC["tearuz"] += float(t_say)

    # ── 2. MODAL DALLANMA ─────────────────────────────────────────
    om = np.asarray(list(omegalar), float)
    dal = 0
    if om.size:
        mumkun = np.array([modal_kip(float(o), float(a.kip_kenari))
                           == "mümkün" for o in om])
        dal = int(np.count_nonzero(mumkun))
        # "Mümkün" olan her çevrim, dokunduğu hâllerin yakînini kırar:
        # tutarlı birden çok dünya varken tekini seçmek delilsiz zandır.
        if dal:
            kir = 1.0 - float(dal) / float(om.size)
            mu = mu * max(kir, 0.0)
    _SAYAC["dallanma"] += float(dal)

    # ── 3. LIOUVILLE SÖNÜMÜ ───────────────────────────────────────
    g = float(a.sonum)
    assert 0.0 <= g < 1.0, "sönüm γ [0,1) olmalı"
    mu = mu * (1.0 - g)
    _SAYAC["buhar"] += float(np.count_nonzero(mu < float(a.tevakkuf_esigi)))

    # ── 4. MERAK KANCASI ──────────────────────────────────────────
    suphe = 1.0 - mu
    merak = [int(i) for i in np.nonzero(suphe > float(a.merak_esigi))[0]]
    _SAYAC["merak"] += float(len(merak))

    tevakkuf = int(np.count_nonzero(mu < float(a.tevakkuf_esigi)))
    _SAYAC["tevakkuf"] += float(tevakkuf)
    _SAYAC["örnek"] += float(m)
    _SAYAC["μ_sonra"] += float(np.mean(mu))
    assert np.all(np.isfinite(mu)), "yakîn sonlu değil"
    return {"μ": mu, "şüphe": suphe, "tevakkuf": tevakkuf,
            "tearuz": t_say, "dallanma": dal, "merak": merak,
            "açık": True}


def suphe_beyani() -> Dict[str, Any]:
    """Sayacın hâli. **Taht ``çağrı > 0`` diye denetler.**"""
    c = max(1.0, _SAYAC["çağrı"])
    return {"çağrı": int(_SAYAC["çağrı"]),
            "tearuz": int(_SAYAC["tearuz"]),
            "dallanma": int(_SAYAC["dallanma"]),
            "merak": int(_SAYAC["merak"]),
            "buhar": int(_SAYAC["buhar"]),
            "tevakkuf": int(_SAYAC["tevakkuf"]),
            "örnek": int(_SAYAC["örnek"]),
            "μ_önce": float(_SAYAC["μ_önce"] / c),
            "μ_sonra": float(_SAYAC["μ_sonra"] / c)}


def suphe_sifirla() -> None:
    for k in _SAYAC:
        _SAYAC[k] = 0.0
