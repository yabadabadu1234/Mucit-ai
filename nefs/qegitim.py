"""
Ana modelin eğitimi -- **gradyan inişi yoktur** (kütük H3/H28).

Kullanıcı hükmü: ölçüt "ikisi birden" olacak -- hem ARC potansiyeli
(dışarıdan sınanabilir), hem nefsin kendi mîzânı (kendi hükmüne bağlı):

    V(p) = −(1/n) Σ log P(doğru belirteç)          ← ARC
           + λ_m · mîzân cezası                     ← nefsin kendi hükmü
           + λ_t · topolojik ceza                   ← mertebe tıkanıklığı

**Mîzân cezası nedir.** Nefs, doğru cevabı vermekle mükellef olduğu
kadar doğru HÜKÜM vermekle de mükelleftir. Küllî hüküm alanlarından
okunan (yalnız burada, eğitim ölçütünde okunur; akış içinde hiçbir
meleke okumaz):

* ``tenakuz`` yüksekse ceza -- çelişkili bir zihin doğru cevap verse de
  tesadüfen vermiştir.
* ``nakz`` yüksekse ceza -- küllî iddia düşmüştür.
* ``tasdik`` düşükse ceza -- hüküm mühürlenmemiştir.
* ``sukut`` yüksekken cevap isteniyorsa ceza -- susmak, cevabı bilmemek
  hâlinde fazilettir (H10); cevabın bilindiği yerde kusurdur.

Motor ``ogrenme/optimize.py``dedir ve **aynen** kullanılır (H32'nin
mimarisi ana modele geçti): Active Subspaces ``d→r`` → Nyström AS-GEK
vekil yüzeyi → hedef bilgisi sızdırma → sanal zamanlı **dalga yayılımı**.
Ayrık motor (Postnikov + tersine tavlama) burada dinamik mertebeleri
seçer -- ``nefs/mertebe.py``in ``DINAMIK``ini.

Tünelleme (H29) başıboş değildir: tıkanma teşhis edilecek VE sıkışılmış
olacak; ilerleme olunca mühürlenir.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from idrak import arc
from ogrenme.optimize import as_gek_adimi, postnikov_adresi, tersine_tavlama

from . import melekeler as mertebe
from .melekeler import QNefs
from .qyazmac import QAyar, QYazmac

__all__ = ["ornekler", "belirtecleri_kodla", "uygunluk", "hedef_cezasi",
           "egit", "degerlendir"]


# =====================================================================
def belirtecleri_kodla(belirtecler: Sequence[int], kubit: int = 4,
                       sozluk: int = 16) -> np.ndarray:
    """Belirteç akışını ham duyu dizeyine çevir: satır başına bir belirteç.

    Her belirteç ``kubit`` bitine açılır ve her bit ``±1`` olarak bir
    sütuna yazılır. ``QYazmac.kodla`` bu sütunları açıya çevirir; ``+1``
    ile ``−1`` ayrı açılar verir, dolayısıyla kodlama **tersinirdir**
    ve hiçbir bit kaybolmaz (H14).
    """
    t = np.asarray(belirtecler, int) % int(sozluk)
    # --- HADAMARD HÂLİ (kütük H116). ``kubit ≥ sozluk`` ise belirteçler
    # **tam eşit uzaklıkta** kodlanabilir: Hadamard satırları birbirine
    # dik olduğu için bütün ikili mesafeler eşittir. ARC belirteçleri
    # RENKTİR, yani kategoriktir; 7 ile 8 arasında "yakınlık" manasızdır
    # ve ikili kodlama onu sahte olarak dayatır.
    #
    # ÖLÇÜLDÜ (16 belirteç, mesafe değişkesi = std/ort):
    #     ikili    4 boyut : 0,2163   (en az 2,000  en çok 4,000)
    #     gri      4 boyut : 0,2163   (küllî ölçüde ikiliyle AYNI)
    #     açısal   4 boyut : 0,2607   (daha kötü)
    #     Hadamard 4 boyut : 0,5000   (ÇARPIŞMA: en az mesafe 0)
    #     Hadamard 8 boyut : 0,2673   (yine çarpışma)
    #     Hadamard 16 boyut: **0,0000**  (bütün mesafeler 5,657)
    #
    # Yani 4 boyutta ikili kodlama elde edilebilecek EN İYİ hâldir ve
    # bir kusur değildir; tam kategorik kodlama ``kubit ≥ sozluk``
    # ister. Seçim bütçeye aittir ve burada açık tutulur.
    if int(kubit) >= int(sozluk):
        H = np.array([[1.0]])
        while H.shape[0] < int(sozluk):
            H = np.block([[H, H], [H, -H]])
        satir = H[t % H.shape[0]]
        out = np.zeros((len(t), int(kubit)))
        out[:, :H.shape[1]] = satir[:, :int(kubit)]
        if int(kubit) > H.shape[1]:
            out[:, H.shape[1]:] = 1.0
        return out
    bit = ((t[:, None] >> np.arange(kubit)[None, :]) & 1).astype(float)
    return 2.0 * bit - 1.0


def ornekler(gorevler: Sequence, azami: int = 24, pencere: int = 8,
             sozluk: int = 16, tohum: int = 0
             ) -> List[Tuple[List[int], int]]:
    """(bağlam, sonraki belirteç) çiftleri -- ARC akışından (kütük H5).

    ARC zaten metindir; model neyi verirsen onu konuşur. Pencere kısa
    tutulur ki eğitim bir oturumda bitsin -- kapasite iddiası ayrıdır ve
    ``main/`` onu 6 000 000 kübitte zaten ölçtü.
    """
    rng = np.random.default_rng(tohum)
    cikti: List[Tuple[List[int], int]] = []
    for g in gorevler:
        try:
            dizi, hedef = arc.gorev_dizisi(g, hedef_indis=0)
        except Exception:
            continue
        akis = [int(x) % sozluk for x in list(dizi) + list(hedef)]
        if len(akis) < pencere + 2:
            continue
        for _ in range(2):
            i = int(rng.integers(pencere, len(akis)))
            cikti.append((akis[i - pencere:i], int(akis[i])))
        if len(cikti) >= azami:
            break
    return cikti[:azami]


# =====================================================================
def _kos(nefs: QNefs, baglam: Sequence[int], sozluk: int
         ) -> Tuple[np.ndarray, Dict[str, float]]:
    E = belirtecleri_kodla(baglam, nefs.ayar.satir_kubiti, sozluk)
    q = nefs.idrak_et(E)
    return q.beyan(sozluk), q.olcumler()


def mizan_cezasi(o: Dict[str, float], cevap_isteniyor: bool = True) -> float:
    """Nefsin kendi hükmünün cezası -- eğitim ölçütünün ikinci yarısı."""
    ceza = 0.0
    ceza += 1.0 * float(o.get("tenakuz", 0.0))
    ceza += 1.0 * float(o.get("nakz", 0.0))
    ceza += 1.0 * (1.0 - float(o.get("tasdik", 0.0)))
    if cevap_isteniyor:
        ceza += 0.5 * float(o.get("sukut", 0.0))
    # Şek'te kalmak da bir kusurdur: delil varken hüküm verilmemiştir.
    ceza += 0.5 * float(o.get("P_Şek", 0.0))
    return ceza


def uygunluk(nefs: QNefs, veri: Sequence[Tuple[List[int], int]],
             p: Optional[np.ndarray] = None, sozluk: int = 16,
             lam_mizan: float = 0.25, lam_top: float = 0.1) -> float:
    """``V(p)`` -- dalganın gördüğü potansiyel; **kayıp fonksiyonu değil**.

    Aradaki fark lafzî değildir: bu potansiyelin gradyanı hiç alınmaz.
    Active Subspaces'in kurduğu ``r`` boyutlu yüzeyde dalga yayılır ve
    küresel minimum spektral çöküşle bulunur (H28).
    """
    if p is not None:
        nefs.yukle(p)
    if not len(veri):
        return 0.0
    top = 0.0
    ceza = 0.0
    for baglam, hedef in veri:
        P, o = _kos(nefs, baglam, sozluk)
        top -= float(np.log(P[hedef % len(P)] + 1e-12))
        ceza += lam_mizan * mizan_cezasi(o)
        # topolojik ceza: dolaşıklık ÖDÜLLENDİRİLİR (çarpım durumuna
        # çöken bir yazmaç süperpozisyonun zenginliğini kaybetmiştir)
        ceza -= lam_top * float(o.get("entropi", 0.0))
    return (top + ceza) / len(veri)


def hedef_cezasi(nefs: QNefs, veri: Sequence[Tuple[List[int], int]],
                 p: Optional[np.ndarray] = None, sozluk: int = 16) -> float:
    """``‖𝒢(u) − y_hedef‖²`` -- hedef bilgisinin potansiyele sızdırılması.

    Minimumun nerede olduğunu bilmiyoruz; orada ne olacağını biliyoruz.
    ``−log P`` yalnız doğru belirtece bakar; bu ise bütün dağılımın
    hedefe uzaklığını cezalandırır ve yanlışların hepsini bastırır.
    """
    if p is not None:
        nefs.yukle(p)
    if not len(veri):
        return 0.0
    top = 0.0
    for baglam, hedef in veri:
        P, _ = _kos(nefs, baglam, sozluk)
        y = np.zeros_like(P)
        y[hedef % len(P)] = 1.0
        top += float(np.sum((P - y) ** 2))
    return top / len(veri)


# =====================================================================
def egit(nefs: QNefs, veri: Sequence[Tuple[List[int], int]],
         cevrim: int = 4, r: int = 2, n_ornek: int = 8, izgara: int = 16,
         sozluk: int = 16, ayrik: bool = True, lam_hedef: float = 0.5,
         gama_azami: float = 0.3, tohum: int = 0,
         gunluk: Optional[List[str]] = None) -> Dict[str, object]:
    """Çift motorlu eğitim -- sürekli (AS-GEK + dalga) ve ayrık (Postnikov)."""
    # yer tahsisi ilk koşuda olur; vektör ondan sonra bilinir
    _kos(nefs, [0] * 4, sozluk)
    p = nefs.vektor()
    V0 = uygunluk(nefs, veri, p, sozluk)
    kayit: List[float] = [V0]
    t0 = time.perf_counter()
    D = tuple(mertebe.DINAMIK)
    gama = 0.0
    tunel: List[float] = []

    for c in range(cevrim):
        # --- TÜNELLEME VANASI (H29): teşhise kilitli, başıboş değil
        _, o = _kos(nefs, veri[0][0], sozluk)
        tikanik = float(o.get("tenakuz", 0.0))
        sikisti = c > 0 and kayit[-1] >= kayit[-2] - 1e-9
        if sikisti and tikanik > 0.5:
            gama = min(gama_azami, gama + 0.1)     # 𝒪₁₅ Merak Γ'yı yükseltir
        elif not sikisti:
            gama = 0.0                             # 𝒪₃₀ Tahkik mühürler
        tunel.append(gama)
        if gama > 0.0:
            # tünelleme: parametre uzayında enine alan -- dar bariyerin
            # ardındaki daha derin tabana sıçrama imkânı
            p = p + gama * np.random.default_rng(tohum + 100 + c).normal(
                scale=0.3, size=len(p))

        # --- SÜREKLİ MOTOR: AS → GEK → hedef sızdırma → dalga
        p_yeni, tani = as_gek_adimi(
            lambda q: uygunluk(nefs, veri, q, sozluk), p,
            yaricap=0.5, r=r, izgara=izgara, n_ornek=n_ornek,
            hedef_ceza=lambda q: hedef_cezasi(nefs, veri[:3], q, sozluk),
            lam_hedef=lam_hedef, tohum=tohum + c)
        V_yeni = uygunluk(nefs, veri, p_yeni, sozluk)
        if V_yeni < kayit[-1]:
            p, V = p_yeni, V_yeni
        else:
            V = kayit[-1]                          # kabul edilmedi; dürüst
        kayit.append(V)
        nefs.yukle(p)

        # --- AYRIK MOTOR: Postnikov adresi + tersine tavlama
        if ayrik:
            _, o = _kos(nefs, veri[0][0], sozluk)
            tik = {m: float(o.get("tenakuz", 0.0)) * (1.0 + i * 0.05)
                   for i, m in enumerate(D)}
            adres = postnikov_adresi(tik, D)
            aday = list(D)
            aday[int(np.argmax([tik[m] for m in aday]))] = adres

            def E_ayrik(vek: Tuple[int, ...]) -> float:
                # Mertebe değişince 20 lif YENİDEN kurulur ve yeniden
                # MAKİNE DENETİMİNDEN geçer (nefs/mertebe.py); ayrık
                # motorun seçtiği mertebe, tip denetiminden geçmeyen bir
                # lif olamaz.
                mertebe.DINAMIK = tuple(vek)
                return uygunluk(nefs, veri[:2], p, sozluk)

            D_yeni, _ = tersine_tavlama(E_ayrik, aday, adim=6,
                                        tohum=tohum + c)
            mertebe.DINAMIK = tuple(D_yeni)
            D = tuple(D_yeni)

        if gunluk is not None:
            gunluk.append("çevrim %d: V=%.4f  aktif_özdeğer=%.3f  Γ=%.2f  "
                          "hedef_ceza=%.3f  D=%s"
                          % (c, V, tani["özdeğer_oranı"], gama,
                             tani.get("hedef_cezası", float("nan")),
                             list(D)[:4]))

    nefs.yukle(p)
    return {"V_ilk": V0, "V_son": kayit[-1], "seyir": kayit,
            "süre_sn": time.perf_counter() - t0, "dinamik": D,
            "parametre": len(nefs), "tünel": tunel,
            "tünel_açıldı": float(sum(1 for g in tunel if g > 0.0))}


# =====================================================================
def _degerlendir_mudrike(nefs, gorevler: Sequence, azami: int,
                         derinlik: int) -> Dict[str, object]:
    """Müdrike çevrimiyle değerlendirme -- padişahın hakikî çıkarımı.

    Ölçü aynı ve sert kalır: hedef ızgara **tam** eşleşti mi. Fakat
    cevap belirteç kestirimiyle değil, **ispatlı kaide** ile üretilir ve
    yakîn eşiğini geçmeyen görevde model **susar**.
    """
    from .mudrike import mudrike as _mudrike

    deneme = cozulen = konusan = yanlis = sukut = 0
    hucre: List[float] = []
    sebepler: Dict[str, int] = {}
    for g in gorevler:
        if deneme >= azami:
            break
        if not getattr(g, "sinama", None) or not getattr(g, "egitim", None):
            continue
        deneme += 1
        r = _mudrike(g, derinlik=derinlik, dalga=True, nefs=nefs)
        if r["sükût"]:
            sukut += 1
            sebepler[r["sebep"]] = sebepler.get(r["sebep"], 0) + 1
            hucre.append(0.0)
            continue
        konusan += 1
        tam = True
        oran = []
        for (a, b), c in zip(g.sinama, r["cevap"]):
            if c is None or c.shape != b.shape:
                tam = False
                oran.append(0.0)
                continue
            e = float(np.mean(c == b))
            oran.append(e)
            if e < 1.0:
                tam = False
        hucre.append(float(np.mean(oran)) if oran else 0.0)
        cozulen += tam
        yanlis += (not tam)
    return {"deneme": deneme, "tam_çözülen": cozulen,
            "konuşan": konusan, "yanlış_cevap": yanlis,
            "sükût": sukut, "atlanan_uzun": 0,
            "sükût_sebepleri": sebepler,
            "ilk_belirteç_isabeti": cozulen,
            "isabet_konuşunca": (cozulen / konusan) if konusan else 0.0,
            "ortalama_hücre_isabeti":
                float(np.mean(hucre)) if hucre else 0.0}


def degerlendir(nefs: QNefs, gorevler: Sequence, azami: int = 8,
                pencere: int = 8, sozluk: int = 16,
                azami_uret: int = 0, mudrike_ile: bool = True,
                derinlik: int = 2) -> Dict[str, object]:
    """Hiç görülmemiş bulmacalar: hedef ızgara **tam** çözüldü mü?

    ===================================================================
    KÖK SEBEP -- niçin bu fonksiyon baştan yazıldı (kütük H133)
    ===================================================================

    Bu değerlendirme evvelce ARC'yi **bir sonraki belirteci kestirme**
    olarak koşuyordu: görev düz bir belirteç dizisine çevriliyor, sonra
    hedef ızgara ``argmax(beyan)`` ile **belirteç belirteç** üretiliyordu
    -- 8 belirteçlik bağlam penceresiyle, 16 sembollük sözlükten.

    Yani padişah, tam da olmamaya yemin ettiği şeyi yapıyordu: bir dil
    modeli. Ve bu usulle ARC çözülemez, sebebi cebridir:

    * 30×30 bir ızgara 900 hücredir; model 8 belirtecine bakıyor.
    * Tam eşleşme için ~100–900 belirtecin **hepsi** doğru olmalı.
      Belirteç başına %95 isabetle bile ``0,95^100 ≈ 0,006``.
    * Ve `idrak/cozucu.py` -- **ispatlı** ARC çözücüsü, cevap verdiğinde
      isabeti %100 -- çıkarım yolunda **hiç çağrılmıyordu**.

    Daha kötüsü: 41 melekenin kurduğu hüküm alanları (``tasdik``,
    ``makam``, ``sukut``) cevaba hiç dokunmuyordu; yalnız ``beyan``ın
    ``argmax``ı vardı. H115/H105/H129'da ölçülen "hüküm alanları
    yapısız" neticesi bunun **sonucudur**: hüküm zaten cevaba
    ulaşmıyordu.

    Artık çıkarım `nefs/mudrike.py`nin **müdrike çevrimi**dir: vazife
    nevi → tesadüf mü → örtü → kaide → yakîn → beyan. Dalga kaideyi
    bulmaz, **yakîni tartar** (𝒪₃₂/𝒪₃₃); kaideyi kaide cebri bulur.

    ``mudrike_ile=False`` eski (belirteç kestirimi) yolu geri verir --
    kıyas ölçümü yapılabilsin diye durur, akışta kullanılmaz.
    """
    if mudrike_ile:
        return _degerlendir_mudrike(nefs, gorevler, azami, derinlik)
    cozulen = isabet = deneme = atlanan = 0
    hucre: List[float] = []
    sukut_sayisi = 0
    # ``azami`` artık "kaç görev TARANIR" değil "kaç görev fiilen
    # DENENİR" demektir. Aksi hâlde had yüzünden atlanan görevler
    # denemenin yerini yiyor ve tarama boşa gidiyordu.
    for g in gorevler:
        if deneme >= azami:
            break
        try:
            dizi, hedef = arc.gorev_dizisi(g, hedef_indis=0)
        except Exception:
            continue
        deneme += 1
        baglam = [int(x) % sozluk for x in dizi]
        h = [int(x) % sozluk for x in hedef]
        # **Ölçülen ve düzeltilen kusur.** Evvelce had aşılınca görev
        # kesilip ``kesilen`` diye sayılıyor, yine de ``deneme``ye dâhil
        # ediliyordu. Ölçüldü ve KALDI: kısa koşuda 4 görevin 4'ü de
        # kesiliyor, netice "tam çözülen 0/4" görünüyordu -- oysa hiçbir
        # görev fiilen sonuna kadar denenmemişti. Yani ölçüt sıfır
        # değil, **boş**tu; sıfır gibi görünmesi daha kötüsüdür.
        #
        # Doğrusu, hadde SIĞMAYAN görevi hiç denememektir: uzun hedefli
        # görev atlanır ve atlandığı ayrıca yazılır. Böylece ``deneme``ye
        # giren her görev sonuna kadar üretilmiş olur ve ``tam_çözülen``
        # gerçekten bir orandır.
        if 0 < azami_uret < len(h):
            atlanan += 1
            deneme -= 1
            continue
        uretilen: List[int] = []
        kac = len(h)
        for _ in range(kac):
            pen = baglam[-pencere:] if len(baglam) >= pencere else \
                ([0] * (pencere - len(baglam)) + baglam)
            P, o = _kos(nefs, pen, sozluk)
            if o.get("sukut", 0.0) > 0.8:
                sukut_sayisi += 1
            t = int(np.argmax(P))
            uretilen.append(t)
            baglam.append(t)
        n = min(len(h), len(uretilen))
        dogru = sum(1 for i in range(n) if h[i] == uretilen[i])
        hucre.append(dogru / max(n, 1))
        if uretilen[:len(h)] == h:
            cozulen += 1
        if n and uretilen[0] == h[0]:
            isabet += 1
    return {"deneme": deneme, "tam_çözülen": cozulen,
            "atlanan_uzun": atlanan,
            "ilk_belirteç_isabeti": isabet, "sükût": sukut_sayisi,
            "ortalama_hücre_isabeti":
                float(np.mean(hucre)) if hucre else 0.0}
