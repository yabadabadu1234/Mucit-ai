"""
Müşahede çekirdeği: İbnü'l-Heysem'in **22 mübser vasfı**, 15 kanala indirgenmiş.

Bu modül, modelin **gözüdür**. Evvelce göz diye bir şey yoktu: ham duyu
bir satır diliminin ortalaması alınıp ``tanh`` ile açıya çevriliyordu
(``qyazmac.kodla``). İki boyut, komşuluk, sınır, renk -- hiçbiri yoktu.
Model ARC bulmacasını **hiç görmedi**; 0/120 neticesinin sebebi budur,
kuantum makinesi değil.

**22 vasıf 22 müstakil kanal DEĞİLDİR.** Ham listeyi olduğu gibi kanala
çevirmek iki hata doğurur ve ikisi de ölçülüp düzeltildi:

* **Çakışma:** Zulmet (karanlık) ile Zıl (gölge) aynı devrededir --
  ikisi de ışık ekseninin negatif tarafıdır. Karanlık bir sinyal değil,
  sinyalin yokluğudur; ayrı detektörü olamaz.
* **Mertebe hatası:** Hüsn ve Kubh, Ziyâ ile aynı mertebeye konamaz.
  Tarifleri gereği (*"oranların, renklerin ve ahengin uyandırdığı
  intizam"*) bunlar Tenasüb + Teşabüh + Levn'den **türer**.

Çelişkisiz ve tekrarsız tasnif::

    ALTI İŞARETLİ EKSEN (13 vasfı yutar, her biri TEK kanal):
      1. Işık        : Ziyâ (+) / Zulmet (−) / Zıl (yerel negatif eğim)
      2. Devinim     : Hareket (+) / Sükûn (0)        [iki ızgara arası]
      3. Bağlantı    : İttisal (+) / Teferruk (−)
      4. Doku        : Huşunet (+) / Meles (−)
      5. Geçirgenlik : Şeffafiyet (+) / Kesafet (−)
      6. Mukayese    : Teşabüh (+) / İhtilaf (−)   [NESNELER arası,
                       hücreler arası değil -- ölçüm bunu mecbur kıldı]

    YEDİ İŞARETSİZ ASIL:
      7. Levn   8. Mekân   9. Bu'd   10. Şekil
     11. Izam  12. Adet   13. Tenasüb

    İKİ TÜREV (mertebe 2):
     14. Hüsn = f(Tenasüb, Teşabüh, Levn)      15. Kubh = nakîzi

**Tek tensör yetmez** (kullanıcı hükmü). Bu vasıflar aynı boyutta
yaşamaz: Levn bir hücrenin, İttisal bir kenarın, Izam bir nesnenin,
Adet bütün ızgaranın vasfıdır. Onun için çıktı bir dizey değil,
**tabakalı bir kayıttır** (``Mesud``):

    Tabaka 0 (noktasal / hücre)  : ışık, levn, geçirgenlik, mekân
    Tabaka 1 (çizgisel / kenar)  : bağlantı, doku
    Tabaka 2 (nesne / cisim)     : şekil, ızam, bu'd, nesne mekânı
    Tabaka 3 (küllî / münasebet) : adet, tenasüb, emsal, katman, hüsn, kubh
    Tabaka 4 (ızgaralar arası)   : devinim, ihtilaf

Hiçbir vasıf iki tabakada tekrar etmez; her tabaka bir öncekinden
türetilir fakat onu silmez.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["Nesne", "Mesud", "musahede_et", "devinim_olc"]

#: **KALDIRILDI.** Evvelce ARC'nin 10 rengine bir "algısal parlaklık"
#: tablosu dayatılmıştı. Ölçüldü ve çöktü: Δışık 174 çiftin **hiçbirinde**
#: baskın çıkmadı (0/174). Sebebi tabloda değil, tablonun kendisindeydi:
#: ARC renkleri **kategoriktir**; 3 ile 7 arasında "parlaklık farkı"
#: yoktur, ikisi ayrı sembolduir. O tablo İbnü'l-Heysem'in Ziyâ'sı değil,
#: benim uydurduğum sahte bir sıralamaydı.
#:
#: ARC'de Ziyâ'nın hakikati şudur (kullanıcı hükmü): **varlık / yokluk**.
#: Zulmet = 0 rengi = taban / boşluk / nötr zemin (kuantumda ``|0⟩``).
#: Ziyâ   = 1-9 = taban üzerindeki her türlü mevcudiyet.
#: Zıl    = bir figürün kenarındaki yerel negatif eğim (ayrı kanal değil).


@dataclass
class Nesne:
    """Bir bağlantılı bileşen -- Tabaka 2'nin sakini."""
    renk: int
    hucreler: np.ndarray            # (k, 2) satır-sütun
    izam: int                       # alan (hücre sayısı)
    kutu: Tuple[int, int, int, int]  # (üst, sol, alt, sağ)
    merkez: Tuple[float, float]
    sekil: np.ndarray               # kutuya kırpılmış ikili maske
    tenasub: Tuple[float, float, float]   # (en/boy, yatay sim., dikey sim.)
    tarif: Dict[str, float] = field(default_factory=dict)  # ŞEKLİN TARİFİ


@dataclass
class Mesud:
    """Müşahede edilenin tabakalı kaydı -- **tek tensör değildir**."""
    izgara: np.ndarray

    # --- Tabaka 0: noktasal (H, W)
    isik: np.ndarray                # Ziyâ(+)/Zulmet(−)/Zıl
    levn: np.ndarray                # (H, W, 3) karşıt renk kanalları
    gecirgenlik: np.ndarray         # Şeffafiyet(+)/Kesafet(−)
    mekan: np.ndarray               # (H, W, 2) normalize konum

    # --- Tabaka 1: çizgisel (H, W)
    baglanti: np.ndarray            # İttisal(+)/Teferruk(−)
    doku: np.ndarray                # Huşunet(+)/Meles(−)

    # --- Tabaka 2: nesne
    nesneler: List[Nesne]
    bud: np.ndarray                 # (H, W) en yakın nesneye mesafe

    # --- Tabaka 3: küllî
    adet: Dict[int, int]            # renk → bileşen sayısı
    tenasub: Tuple[float, float, float]   # nesne başına, ızam ağırlıklı
    mukayese: np.ndarray            # (H, W) aykırılık alanı (Teşabüh DEĞİL)
    emsal: Dict[str, float]         # NESNELER arası Teşabüh(+)/İhtilaf(−)
    katman: Dict[str, float]        # kavşak / kesafet / şeffafiyet
    sekil_ozeti: Dict[str, float]   # ŞEKLİN tarifi, ızam ağırlıklı
    sureklilik: Dict[str, float]    # örtme hadiseleri (katman delili)
    husn: float
    kubh: float

    def ozet(self) -> Dict[str, float]:
        """Küllî hükümlerin skaler hulâsası -- rapor ve ölçüm için."""
        return {
            "ışık_ort": float(self.isik.mean()),
            "ışık_sap": float(self.isik.std()),
            "bağlantı_ort": float(self.baglanti.mean()),
            "doku_ort": float(self.doku.mean()),
            "geçirgenlik_ort": float(self.gecirgenlik.mean()),
            "aykırılık_ort": float(self.mukayese.mean()),
            "emsal_şekil": self.emsal["emsal_şekil"],
            "emsal_dönük": self.emsal["emsal_dönük"],
            "ihtilaf": self.emsal["ihtilaf"],
            "şekil_sınıfı": self.emsal["sınıf"],
            "kavşak": self.katman["kavşak"],
            "kesafet": self.katman["kesafet"],
            "şeffafiyet": self.katman["şeffafiyet"],
            "nesne_sayısı": float(len(self.nesneler)),
            "renk_sayısı": float(len(self.adet)),
            "en_boy": float(self.tenasub[0]),
            "yatay_simetri": float(self.tenasub[1]),
            "dikey_simetri": float(self.tenasub[2]),
            "hüsn": float(self.husn),
            "kubh": float(self.kubh),
        }


# =====================================================================
#  Tabaka 0 — noktasal vasıflar
# =====================================================================
def _isik(g: np.ndarray) -> np.ndarray:
    """Işık ekseni: Ziyâ(+) = varlık, Zulmet(−) = taban, Zıl = kenar eğimi.

    ARC'de foton yoktur; Ziyâ **mevcudiyettir**. Dolu hücre uyarılmış
    (``+1``), zemin hücresi taban durumudur (``−1``). Zıl ayrı bir kanal
    değildir: figürün kenarında bu alanın yerel eğimi kendiliğinden
    negatifleşir, gölge oradan doğar.

    Uydurma parlaklık tablosuyla ölçülüp çökmüştü (0/174); bu hâliyle
    yeniden ölçülmelidir ve ölçülür.
    """
    varlik = np.where(g != 0, 1.0, -1.0)
    yerel = _pencere_ortalamasi(varlik, 3)
    # Ziyâ mevcudiyetin kendisi, Zıl ise yerel düşüştür; ikisi TEK eksende
    return 0.5 * varlik + 0.5 * (varlik - yerel)


def _levn(g: np.ndarray) -> np.ndarray:
    """Levn: karşıt renk kanalları (kırmızı-yeşil, mavi-sarı, parlaklık).

    Renk indisi bir **sayı değildir**: 3 ile 7 arasında "4 fark" yoktur,
    ikisi ayrı kategoridir. Onun için renk indisi doğrudan kanala
    yazılmaz; retinadaki gibi üç karşıtlık eksenine açılır. Böylece iki
    renk arasındaki mesafe algısal olur, keyfî olmaz.
    """
    idx = np.clip(g, 0, 9)
    # ARC paletinin kaba RGB karşılıkları (0-1)
    rgb = np.array([[0.00, 0.00, 0.00],   # siyah
                    [0.15, 0.35, 0.95],   # mavi
                    [0.95, 0.20, 0.20],   # kırmızı
                    [0.20, 0.80, 0.25],   # yeşil
                    [0.98, 0.90, 0.20],   # sarı
                    [0.60, 0.60, 0.60],   # gri
                    [0.95, 0.20, 0.70],   # fuşya
                    [0.98, 0.60, 0.15],   # turuncu
                    [0.45, 0.80, 0.95],   # açık mavi
                    [0.55, 0.10, 0.20]])  # bordo
    c = rgb[idx]                                   # (H, W, 3)
    R, G, B = c[..., 0], c[..., 1], c[..., 2]
    return np.stack([R - G,                        # kırmızı-yeşil
                     B - 0.5 * (R + G),            # mavi-sarı
                     0.3 * R + 0.6 * G + 0.1 * B], axis=-1)


def _gecirgenlik(g: np.ndarray) -> np.ndarray:
    """Şeffafiyet(+) / Kesafet(−).

    ARC'de zemin (0) ışığı geçiren, dolu hücre ise kesif olandır. Bu
    ikisi tek eksendir; ayrı iki kanal yazmak tekrar olurdu.
    """
    return np.where(g == 0, 1.0, -1.0)


def _mekan(g: np.ndarray) -> np.ndarray:
    """Mekân: normalize retinotopik koordinat.

    Mekân bir hücre tipinin **çıktısı değildir**; bütün haritanın
    zeminidir. Onun için ayrı bir detektör olarak değil, her tabakanın
    üzerine serilen koordinat alanı olarak taşınır.
    """
    H, W = g.shape
    r = np.linspace(0.0, 1.0, H)[:, None] * np.ones((1, W))
    c = np.ones((H, 1)) * np.linspace(0.0, 1.0, W)[None, :]
    return np.stack([r, c], axis=-1)


# =====================================================================
#  Tabaka 1 — çizgisel vasıflar
# =====================================================================
def _baglanti(g: np.ndarray) -> np.ndarray:
    """İttisal(+) / Teferruk(−): dört komşuluğun işaretli dengesi.

    Her hücre için ``(aynı renk komşu) − (farklı renk komşu)``. Bitişiklik
    ile ayrıklık aynı ölçünün iki ucudur; ayrı kanal yazmak tekrar olur.
    Kenar hücrelerinde eksik komşu **farklı** sayılmaz, hiç sayılmaz --
    ızgaranın kenarı bir ayrıklık delili değildir.
    """
    H, W = g.shape
    ayni = np.zeros((H, W), float)
    farkli = np.zeros((H, W), float)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        kaydir = np.full((H, W), -1, dtype=int)
        r0, r1 = max(0, dr), min(H, H + dr)
        c0, c1 = max(0, dc), min(W, W + dc)
        kaydir[r0 - dr:r1 - dr, c0 - dc:c1 - dc] = g[r0:r1, c0:c1]
        var = kaydir >= 0
        ayni += (var & (kaydir == g)).astype(float)
        farkli += (var & (kaydir != g)).astype(float)
    return (ayni - farkli) / 4.0


def _doku(g: np.ndarray) -> np.ndarray:
    """Huşunet(+) / Meles(−): yerel çeşitlilik, medyana göre işaretli.

    Pürüzlülük ile düzlük tek eksendir. Ölçü, 3×3 penceredeki **farklı
    renk sayısıdır**; varyans değil, çünkü renk kategoriktir (bkz.
    ``_levn``): 3 ile 7 arasındaki "fark" bir mesafe değildir.
    """
    H, W = g.shape
    cesit = np.zeros((H, W), float)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            kaydir = np.full((H, W), -1, dtype=int)
            r0, r1 = max(0, dr), min(H, H + dr)
            c0, c1 = max(0, dc), min(W, W + dc)
            kaydir[r0 - dr:r1 - dr, c0 - dc:c1 - dc] = g[r0:r1, c0:c1]
            cesit += ((kaydir >= 0) & (kaydir != g)).astype(float)
    cesit = cesit / 8.0
    return cesit - float(np.median(cesit))


# =====================================================================
#  Tabaka 2 — nesneler
# =====================================================================
def _bilesenler(g: np.ndarray, zemin: int = 0,
                capraz: bool = False) -> List[Nesne]:
    """Aynı renkli bağlantılı bileşenler -- birlik-bul ile ``O(HW·α)``.

    ``capraz`` kapalıdır: ARC'de köşeden temas ekseriya "ayrı nesne"
    demektir. Bu bir tercihtir ve ölçülmelidir; açık bırakılırsa iki
    ayrı şekil tek nesne sayılır ve Adet vasfı bozulur.
    """
    H, W = g.shape
    ata = -np.ones(H * W, dtype=int)

    def kok(x: int) -> int:
        while ata[x] != x:
            ata[x] = ata[ata[x]]
            x = ata[x]
        return x

    for i in range(H):
        for j in range(W):
            if g[i, j] == zemin:
                continue
            k = i * W + j
            ata[k] = k
    komsu = ((-1, 0), (0, -1)) if not capraz else \
            ((-1, 0), (0, -1), (-1, -1), (-1, 1))
    for i in range(H):
        for j in range(W):
            if g[i, j] == zemin:
                continue
            k = i * W + j
            for dr, dc in komsu:
                a, b = i + dr, j + dc
                if 0 <= a < H and 0 <= b < W and g[a, b] == g[i, j]:
                    ra, rb = kok(k), kok(a * W + b)
                    if ra != rb:
                        ata[ra] = rb

    kume: Dict[int, List[Tuple[int, int]]] = {}
    for i in range(H):
        for j in range(W):
            if g[i, j] == zemin:
                continue
            kume.setdefault(kok(i * W + j), []).append((i, j))

    out: List[Nesne] = []
    for hucreler in kume.values():
        A = np.array(hucreler)
        ust, sol = A.min(0)
        alt, sag = A.max(0)
        maske = np.zeros((alt - ust + 1, sag - sol + 1), dtype=bool)
        maske[A[:, 0] - ust, A[:, 1] - sol] = True
        out.append(Nesne(
            renk=int(g[A[0, 0], A[0, 1]]),
            hucreler=A,
            izam=len(A),
            kutu=(int(ust), int(sol), int(alt), int(sag)),
            merkez=(float(A[:, 0].mean()), float(A[:, 1].mean())),
            sekil=maske,
            tenasub=_tenasub_maske(maske),
            tarif=_sekil_tarifi(maske)))
    out.sort(key=lambda n: (-n.izam, n.kutu))
    return out


def _bud(g: np.ndarray, nesneler: Sequence[Nesne]) -> np.ndarray:
    """Bu'd: her hücrenin en yakın nesneye uzaklığı (Chebyshev).

    ARC'de derinlik yoktur; Bu'd burada **düzlem içi mesafedir**. Bunu
    "derinlik" diye sunmak yalan olurdu; vasfın adı korunur, mahiyeti
    ızgaraya göre yeniden tarif edilir ve öyle bildirilir.
    """
    H, W = g.shape
    if not nesneler:
        return np.zeros((H, W))
    dolu = (g != 0)
    if not dolu.any():
        return np.zeros((H, W))
    d = np.full((H, W), np.inf)
    d[dolu] = 0.0
    # Chebyshev mesafesi: iki geçişli dinamik programlama, O(HW)
    for i in range(H):
        for j in range(W):
            v = d[i, j]
            if i > 0:
                v = min(v, d[i - 1, j] + 1)
                if j > 0:
                    v = min(v, d[i - 1, j - 1] + 1)
                if j + 1 < W:
                    v = min(v, d[i - 1, j + 1] + 1)
            if j > 0:
                v = min(v, d[i, j - 1] + 1)
            d[i, j] = v
    for i in range(H - 1, -1, -1):
        for j in range(W - 1, -1, -1):
            v = d[i, j]
            if i + 1 < H:
                v = min(v, d[i + 1, j] + 1)
                if j > 0:
                    v = min(v, d[i + 1, j - 1] + 1)
                if j + 1 < W:
                    v = min(v, d[i + 1, j + 1] + 1)
            if j + 1 < W:
                v = min(v, d[i, j + 1] + 1)
            d[i, j] = v
    m = float(d[np.isfinite(d)].max()) if np.isfinite(d).any() else 1.0
    return d / max(m, 1.0)


# =====================================================================
#  Tabaka 3 — küllî vasıflar
# =====================================================================
def _sekil_tarifi(m: np.ndarray) -> Dict[str, float]:
    """**Şeklin hakiki tarifi.** Evvelce şekil diye bir şey yoktu.

    Şekil yalnız ``emsal_şekil`` içinde "maskeler birebir eşit mi" diye
    geçiyordu; bu son derece kırılgandır -- **tek hücre farkı emsalliği
    düşürür**. Ablasyonda 19 kanalın zararlı çıkmasının en kuvvetli
    şüphelisi buydu ve tarif yazılmadan hüküm verilemezdi.

    Yedi ölçü, hepsi ötelemeden bağımsız, çoğu ölçekten de:

    * ``betti1``   -- delik sayısı. Şeklin topolojik cinsi; ARC'de
      "içi dolu mu boş mu" bulmacalarının doğrudan cevabı.
    * ``cevre``    -- dış sınır uzunluğu (dolu hücrenin boş komşusu).
    * ``tıkızlık`` -- ``çevre²/alan``. Daire en tıkız, ince çizgi en
      dağınıktır; ölçekten bağımsızdır.
    * ``doluluk``  -- ``alan / kutu alanı``. Dikdörtgen 1, çapraz çizgi
      ``1/n``dir.
    * ``simetri``  -- 8 katlı dihedral grubun kaçı şekli sabit bırakıyor
      (1 = hiç simetri yok, 8 = kare/daire gibi tam simetrik).
    * ``m20/m02``  -- ikinci merkezî momentler, alana normalize. Şeklin
      yatay mı dikey mi uzandığını **maskeye bakmadan** söyler.
    * ``m11``      -- çapraz moment; eğik uzanımı verir.

    Bunlar bir "gömme" (embedding) değildir; her biri **okunabilir bir
    vasıftır** ve hangi ARC kaidesine dokunduğu söylenebilir.
    """
    h, w = m.shape
    alan = float(m.sum())
    if alan == 0:
        return {"betti1": 0.0, "çevre": 0.0, "tıkızlık": 0.0,
                "doluluk": 0.0, "simetri": 8.0,
                "m20": 0.0, "m02": 0.0, "m11": 0.0}

    # çevre: dolu hücrenin boş (yahut kutu dışı) komşu sayısı
    P = np.pad(m, 1, constant_values=False)
    cevre = 0.0
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        kaydir = P[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        cevre += float((m & ~kaydir).sum())

    # betti1: kutu içindeki boş bölgelerden kenara ULAŞAMAYANLARIN sayısı.
    # Kenara ulaşanlar dış boşluktur, delik değildir.
    bos = ~m
    gorulmus = np.zeros_like(bos)
    yigin = []
    for i in range(h):
        for j in (0, w - 1):
            if bos[i, j] and not gorulmus[i, j]:
                gorulmus[i, j] = True
                yigin.append((i, j))
    for j in range(w):
        for i in (0, h - 1):
            if bos[i, j] and not gorulmus[i, j]:
                gorulmus[i, j] = True
                yigin.append((i, j))
    while yigin:
        i, j = yigin.pop()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            a, b = i + dr, j + dc
            if 0 <= a < h and 0 <= b < w and bos[a, b] and not gorulmus[a, b]:
                gorulmus[a, b] = True
                yigin.append((a, b))
    ic_bos = bos & ~gorulmus
    delik = 0
    kalan = ic_bos.copy()
    while kalan.any():
        i, j = map(int, np.argwhere(kalan)[0])
        delik += 1
        y = [(i, j)]
        kalan[i, j] = False
        while y:
            a, b = y.pop()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                p_, q_ = a + dr, b + dc
                if 0 <= p_ < h and 0 <= q_ < w and kalan[p_, q_]:
                    kalan[p_, q_] = False
                    y.append((p_, q_))

    # dihedral simetri: 8 dönüşümün kaçı şekli sabit bırakıyor
    sim = 0
    for k in range(4):
        R = np.rot90(m, k)
        if R.shape == m.shape and np.array_equal(R, m):
            sim += 1
        Y = R[:, ::-1]
        if Y.shape == m.shape and np.array_equal(Y, m):
            sim += 1

    # merkezî momentler (alana normalize → ölçekten bağımsız)
    idx = np.argwhere(m)
    y0, x0 = idx.mean(0)
    dy = idx[:, 0] - y0
    dx = idx[:, 1] - x0
    n2 = alan ** 2
    return {"betti1": float(delik),
            "çevre": cevre,
            "tıkızlık": float(cevre * cevre / alan),
            "doluluk": float(alan / (h * w)),
            "simetri": float(sim),
            "m20": float((dy * dy).sum() / n2),
            "m02": float((dx * dx).sum() / n2),
            "m11": float((dy * dx).sum() / n2)}


def _sureklilik(g: np.ndarray) -> Dict[str, float]:
    """**Şeffafiyet, kavşakta değil SÜREKLİLİKTE aranır** (kullanıcı hükmü).

    Evvelce "kavşakta üçüncü renk var mı" diye arandı ve kanal öldü
    (sıfır oranı 0,99). Doğru testi kullanıcı verdi: *"bir ızgara
    çizgisinin renkli bir karenin içinden kesilmeden geçmesi"*.

    Ölçü şudur: bir ``c`` renkli dizi, bir ``d`` rengiyle kesilip
    öbür tarafta **aynı hizada** ``c`` ile devam ediyorsa, orada bir
    **örtme hadisesi** vardır: ``c`` arkada, ``d`` öndedir. Bu, tek
    ızgarada görülebilen hakiki bir katman delilidir.

    * ``örtme``     -- kaç yerde böyle bir kesinti-devam var.
    * ``ön_renk``   -- örten (öndeki) rengin çeşitliliği.
    * ``arka_renk`` -- örtülen (arkadaki) rengin çeşitliliği.
    """
    H, W = g.shape
    ortme = 0
    on: Dict[int, int] = {}
    arka: Dict[int, int] = {}

    def tara(A: np.ndarray) -> None:
        nonlocal ortme
        h, w = A.shape
        for i in range(h):
            j = 0
            while j < w:
                c = A[i, j]
                if c == 0:
                    j += 1
                    continue
                k = j
                while k < w and A[i, k] == c:
                    k += 1
                # dizi [j,k) ; kesinti ve devam var mı
                t = k
                while t < w and A[i, t] != c and A[i, t] != 0:
                    t += 1
                if k < t < w and A[i, t] == c and (t - k) <= 3:
                    ortme += 1
                    d = int(A[i, k])
                    on[d] = on.get(d, 0) + 1
                    arka[int(c)] = arka.get(int(c), 0) + 1
                j = k

    tara(g)
    tara(g.T)
    return {"örtme": float(ortme),
            "ön_renk": float(len(on)),
            "arka_renk": float(len(arka))}


def _tenasub_maske(m: np.ndarray) -> Tuple[float, float, float]:
    """Tenasüb: (en/boy oranı, yatay simetri, dikey simetri)."""
    h, w = m.shape
    oran = w / max(h, 1)
    yatay = float((m == m[:, ::-1]).mean())
    dikey = float((m == m[::-1, :]).mean())
    return (float(oran), yatay, dikey)


def _tenasub_kulli(g: np.ndarray, nesneler: Sequence[Nesne]
                   ) -> Tuple[float, float, float]:
    """Küllî tenasüb: nesnelerin oran ve simetrilerinin ızam ağırlıklı ortası.

    Nesne yoksa ızgaranın kendi oranına düşülür ve bu **işaretlenir**
    (boş ızgarada tenasüb ızgaranındır, uydurma değildir).
    """
    if not nesneler:
        return _tenasub_maske(g != 0)
    w = np.array([n.izam for n in nesneler], float)
    w = w / w.sum()
    T = np.array([n.tenasub for n in nesneler], float)
    return (float(w @ T[:, 0]), float(w @ T[:, 1]), float(w @ T[:, 2]))


def _dihedral_kanonik(sekil: np.ndarray) -> Tuple[Tuple[int, int], bytes]:
    """Şeklin **dihedral kanonik sûreti** -- 8 katlı grubun en küçüğü.

    Dört dönme ve onların yansımaları alınır; ``(şekil, baytlar)``
    ikililerinin **en küçüğü** kanonik sayılır. İki şekil dihedral
    denk ise kanonikleri **eşittir**; dolayısıyla denklik kıyası
    çift başına ``O(1)``dir.

    ===================================================================
    ÖLÇÜLEN VE DÜZELTİLEN KUSUR (kütük H197)
    ===================================================================

    ``_emsal``in çift döngüsü her çift için ``np.rot90``ı yeniden
    çağırıyordu: profilde **2.374.338 çağrı, 23,5 saniye**. Halbuki
    dönmeler nesnenin kendi vasfıdır, çiftin değil. Kanonik sûret
    nesne başına **bir kere** hesaplanır; ``m`` nesne için ``4m``
    dönme, ``m²/2`` değil.
    """
    en_kucuk: Optional[Tuple[Tuple[int, int], bytes]] = None
    for k in range(4):
        R = np.rot90(sekil, k)
        for V in (R, R[:, ::-1]):
            A = np.ascontiguousarray(V)
            aday = ((int(A.shape[0]), int(A.shape[1])), A.tobytes())
            if en_kucuk is None or aday < en_kucuk:
                en_kucuk = aday
    return en_kucuk                                    # type: ignore[return-value]


def _emsal(nesneler: Sequence[Nesne]) -> Dict[str, float]:
    """**İkinci mertebe müşahede**: Teşabüh(+) / İhtilaf(−), NESNELER arası.

    Kullanıcı hükmü: *"İki nesnenin şekilce benzediğini görmek hâlâ
    müşahededir (gözün emsal tespiti); lakin kuralı birinden ötekine
    aktarmak Kıyas'tır."* Sınır buradadır ve aşılmaz: bu fonksiyon
    hangi nesnelerin emsal olduğunu **söyler**, aralarında hüküm
    **taşımaz**.

    Evvelce Teşabüh hücre komşuluğunda hesaplanıyor ve ``doku`` ile
    ``bağlantı``dan türetildiği için onları **çift sayıyordu** (ölçüldü:
    86/174 çiftte baskın, bağımsız değil). Yeri burasıdır.
    """
    m = len(nesneler)
    if m < 2:
        return {"emsal_şekil": 0.0, "emsal_ızam": 0.0, "emsal_renk": 0.0,
                "emsal_dönük": 0.0, "ihtilaf": 0.0, "sınıf": float(m)}
    ayni_sekil = ayni_izam = ayni_renk = donuk = 0
    cift = 0
    # Vasıflar çift döngüsünün DIŞINDA, nesne başına bir kere.
    ham = [(n.sekil.shape, np.ascontiguousarray(n.sekil).tobytes())
           for n in nesneler]
    kan = [_dihedral_kanonik(n.sekil) for n in nesneler]
    for i in range(m):
        for j in range(i + 1, m):
            cift += 1
            a, b = nesneler[i], nesneler[j]
            if a.izam == b.izam:
                ayni_izam += 1
            if a.renk == b.renk:
                ayni_renk += 1
            if ham[i] == ham[j]:
                ayni_sekil += 1
            elif kan[i] == kan[j]:
                # dönme yahut yansımayla emsal (8 katlı dihedral grup)
                donuk += 1
    # şekil kümesi sayısı: kaç ayrı "cins" var
    imza = set()
    for n in nesneler:
        imza.add((n.sekil.shape, n.sekil.tobytes()))
    return {"emsal_şekil": ayni_sekil / cift,
            "emsal_ızam": ayni_izam / cift,
            "emsal_renk": ayni_renk / cift,
            "emsal_dönük": donuk / cift,
            "ihtilaf": 1.0 - (ayni_sekil + donuk) / cift,
            "sınıf": float(len(imza))}


def _seffafiyet(g: np.ndarray) -> Dict[str, float]:
    """Şeffafiyet: **katman topolojisi** -- Ziyâ ile çakışmaz (kullanıcı hükmü).

    Ziyâ varlık/yokluktur; Şeffafiyet ise iki figür üst üste bindiğinde
    arkadakinin hissedilip hissedilmediğidir. ARC'de bunun fiilî izi
    **kavşaklardır**: yatay bir dizi ile dikey bir dizi kesiştiğinde
    kavşak hücresini hangi renk tutuyor?

    * Kavşakta hep aynı renk kazanıyorsa → **Kesafet** (bir katman üstte,
      öteki kesilmiş).
    * Kavşak rengi değişiyorsa yahut üçüncü bir renkse → **Şeffafiyet**
      (katmanlar birbirini yok etmiyor).

    Bu bir **vekil ölçüdür** ve öyle bildirilir: hakiki katman sırası
    ARC'de verilmez, kavşaktan çıkarılır.
    """
    H, W = g.shape
    kavsak = 0
    yatay_kazandi = 0
    dikey_kazandi = 0
    ucuncu = 0
    for i in range(H):
        for j in range(W):
            c = g[i, j]
            if c == 0:
                continue
            # yatay komşuların hâkim rengi, dikey komşuların hâkim rengi
            y = [g[i, j - 1] if j > 0 else 0, g[i, j + 1] if j + 1 < W else 0]
            d = [g[i - 1, j] if i > 0 else 0, g[i + 1, j] if i + 1 < H else 0]
            ys = y[0] if y[0] == y[1] and y[0] != 0 else 0
            ds = d[0] if d[0] == d[1] and d[0] != 0 else 0
            if ys and ds and ys != ds:
                kavsak += 1
                if c == ys:
                    yatay_kazandi += 1
                elif c == ds:
                    dikey_kazandi += 1
                else:
                    ucuncu += 1
    if kavsak == 0:
        return {"kavşak": 0.0, "kesafet": 0.0, "şeffafiyet": 0.0}
    tutarli = max(yatay_kazandi, dikey_kazandi) / kavsak
    return {"kavşak": float(kavsak),
            "kesafet": float(tutarli),           # bir katman hep üstte
            "şeffafiyet": float(ucuncu / kavsak)}  # üçüncü renk = karışım


def _mukayese(g: np.ndarray, pencere: int = 3) -> np.ndarray:
    """**Aykırılık alanı** -- hücrenin, ızgaranın hâkim örgüsünden sapması.

    **Bu artık "Teşabüh/İhtilaf" DEĞİLDİR.** Öyle adlandırılmıştı ve
    ölçüm yalanladı: ``doku`` ve ``bağlantı``dan türetildiği hâlde
    174 çiftin 86'sında baskın çıkıyordu -- yani bağımsız bir eksen
    değil, ötekilerin toplamıydı. Tekrar günahı buydu.

    Teşabüh/İhtilaf'ın hakiki yeri **nesneler arasıdır** (``_emsal``).
    Burada kalan şey ise başka ve meşru bir şeydir: bir hücrenin
    ızgaranın genel örgüsüne göre **ne kadar sıra dışı** olduğu --
    ARC'de "tek farklı hücre" bulmacalarının doğrudan sinyali.
    """
    H, W = g.shape
    d = _doku(g)
    b = _baglanti(g)
    oz = np.stack([d, b], axis=-1).reshape(-1, 2)
    merkez = oz.mean(0)
    sapma = np.linalg.norm(oz - merkez, axis=1).reshape(H, W)
    olcek = float(sapma.max()) + 1e-12
    return 1.0 - 2.0 * (sapma / olcek)          # +1 benzer, −1 aykırı


def _pencere_ortalamasi(A: np.ndarray, k: int) -> np.ndarray:
    """``k×k`` kutu ortalaması -- kenarda kenar değeri tekrarlanır."""
    p = k // 2
    P = np.pad(A, p, mode="edge")
    out = np.zeros_like(A, dtype=float)
    for dr in range(k):
        for dc in range(k):
            out += P[dr:dr + A.shape[0], dc:dc + A.shape[1]]
    return out / (k * k)


# =====================================================================
def musahede_et(izgara: np.ndarray) -> Mesud:
    """Bir ızgarayı 15 kanallı tabakalı müşahedeye çevir.

    Hiçbir yerde öğrenilen ağırlık yoktur: bunlar **fıtrî** kanallardır,
    tıpkı retinanın ve V1'in doğuştan gelen devreleri gibi. Öğrenme
    bunların üzerinde olur, bunların yerine değil.
    """
    g = np.asarray(izgara, int)
    if g.ndim != 2:
        raise ValueError("müşahede iki boyutlu ızgara ister")
    nesneler = _bilesenler(g)
    adet: Dict[int, int] = {}
    for n in nesneler:
        adet[n.renk] = adet.get(n.renk, 0) + 1

    # **DÜZELTİLDİ.** Evvelce tenasüb ızgaranın tamamından ölçülüyordu;
    # ızgara şekli sabit kalınca ``Δen_boy`` cebren sıfır çıkıyordu
    # (ölçüldü: ortalama 0.0000, sıfır olma oranı 1.00 -- kanal ÖLÜYDÜ).
    # Tenasüb bir **nesnenin** vasfıdır; nesneler üzerinden toplanır.
    ten = _tenasub_kulli(g, nesneler)
    muk = _mukayese(g)
    ems = _emsal(nesneler)
    kat = _seffafiyet(g)
    sur = _sureklilik(g)
    if nesneler:
        w_ = np.array([n.izam for n in nesneler], float)
        w_ = w_ / w_.sum()
        anahtarlar = list(nesneler[0].tarif.keys())
        sek = {k: float(w_ @ np.array([n.tarif[k] for n in nesneler]))
               for k in anahtarlar}
    else:
        sek = {k: 0.0 for k in ("betti1", "çevre", "tıkızlık", "doluluk",
                                "simetri", "m20", "m02", "m11")}
    # Hüsn: intizam. Simetri yüksek, aykırılık düşük, oran dengeli ise
    # güzeldir. Türevdir; ayrı bir detektörü yoktur (mertebe 2).
    # Hüsn TÜREVDİR (mertebe 2): simetri × emsal-nizamı ÷ oran sapması.
    # Ayrı bir detektörü yoktur; Tenasüb + Teşabüh'ten doğar.
    husn = float(0.5 * (ten[1] + ten[2])
                 * (0.5 + 0.5 * ems["emsal_şekil"])
                 / (1.0 + abs(np.log(max(ten[0], 1e-6)))))
    return Mesud(
        izgara=g,
        isik=_isik(g),
        levn=_levn(g),
        gecirgenlik=_gecirgenlik(g),
        mekan=_mekan(g),
        baglanti=_baglanti(g),
        doku=_doku(g),
        nesneler=nesneler,
        bud=_bud(g, nesneler),
        adet=adet,
        tenasub=ten,
        mukayese=muk,
        emsal=ems,
        katman=kat,
        sekil_ozeti=sek,
        sureklilik=sur,
        husn=husn,
        kubh=1.0 - husn)


def devinim_olc(a: Mesud, b: Mesud) -> Dict[str, float]:
    """Tabaka 4: iki müşahede arasındaki Hareket / Sükûn / İhtilaf.

    ARC'de girdi ile çıktı arasındaki **kaide** buradadır. Ölçü, hangi
    kanalın değiştiğini söyler; kaidenin ne olduğunu değil. Müşahedenin
    haddi budur ve aşılmaz -- kaideyi çıkarmak Kıyas'ın (𝒪₁₈) işidir.
    """
    out: Dict[str, float] = {}
    ayni_sekil = a.izgara.shape == b.izgara.shape
    out["şekil_aynı"] = float(ayni_sekil)
    if ayni_sekil:
        deg = (a.izgara != b.izgara)
        out["hareket"] = float(deg.mean())            # değişen hücre oranı
        out["sükûn"] = float(1.0 - deg.mean())
        for ad, X, Y in (("ışık", a.isik, b.isik),
                         ("bağlantı", a.baglanti, b.baglanti),
                         ("doku", a.doku, b.doku),
                         ("geçirgenlik", a.gecirgenlik, b.gecirgenlik),
                         ("mukayese", a.mukayese, b.mukayese),
                         ("bu'd", a.bud, b.bud)):
            out["Δ" + ad] = float(np.abs(X - Y).mean())
        out["Δlevn"] = float(np.abs(a.levn - b.levn).mean())
    else:
        out["hareket"] = 1.0
        out["sükûn"] = 0.0
    out["Δadet"] = float(sum(abs(b.adet.get(k, 0) - a.adet.get(k, 0))
                             for k in set(a.adet) | set(b.adet)))
    out["Δnesne"] = float(len(b.nesneler) - len(a.nesneler))
    out["Δen_boy"] = float(b.tenasub[0] - a.tenasub[0])
    out["Δyatay_sim"] = float(b.tenasub[1] - a.tenasub[1])
    out["Δdikey_sim"] = float(b.tenasub[2] - a.tenasub[2])
    out["Δhüsn"] = float(b.husn - a.husn)
    for k in ("emsal_şekil", "emsal_dönük", "ihtilaf", "sınıf"):
        out["Δ" + k] = float(b.emsal[k] - a.emsal[k])
    for k in ("kavşak", "kesafet", "şeffafiyet"):
        out["Δ" + k] = float(b.katman[k] - a.katman[k])
    # ŞEKLİN tarifi -- yeni ve asıl kanal
    for k in a.sekil_ozeti:
        out["Δş_" + k] = float(b.sekil_ozeti[k] - a.sekil_ozeti[k])
    # ŞEFFAFİYET: kullanıcı hükmü gereği girdi-çıktı ARASINDA aranır.
    # Girdide örtülü olan çıktıda ortaya çıkıyorsa, örtme çözülmüştür;
    # tersi ise örtme kurulmuştur. Tek ızgarada görünmeyen budur.
    for k in ("örtme", "ön_renk", "arka_renk"):
        out["Δsür_" + k] = float(b.sureklilik[k] - a.sureklilik[k])
    out["örtme_çözüldü"] = float(a.sureklilik["örtme"] > 0
                                 and b.sureklilik["örtme"] == 0)
    out["örtme_kuruldu"] = float(a.sureklilik["örtme"] == 0
                                 and b.sureklilik["örtme"] > 0)
    return out
