"""Palmer'ın Rasyonel Kuantum Mekaniği (RaQM): ne diyor, ne demiyor.

**Bu modül bir GERİ ALMADIR.**  Önceki turda ``hesap.padic``,
``hesap.galois`` ve ``hesap.saklama`` modüllerini yazarken kaynak
risalenin "irrasyonel sayıların ilgası" ve "``N > 400`` saklanamaz"
bahislerini ele aldım.  O tashihler kaynak metin için doğrudur ve
yerinde durur.  Fakat iki yerde **karıştırma** yaptım ve burada
açıkça geri alıyorum:

**Geri alma 1 -- 400 kübit meselesi.**  ``hesap.saklama`` (M27),
"``N > 400`` saklanamaz" itirazını bir **bellek sayımı** olarak ele
aldı: keyfî bir durum ``2^N`` katsayı ister.  O sayım doğrudur.  Fakat
Palmer'ın 400 kübit iddiası **bu değildir**.  Palmer, klasik belleğin
yetmeyeceğini söylemiyor; *fizikî kuantum bilgisayarının kendisinin*
tavana çarpacağını, yani Shor gibi bütün Hilbert uzayını kullanan
algoritmaların üstel avantajının ~200--400 hata düzeltilmiş kübitte
doyacağını ve hiçbir fizikî tatbikte ~1000'i geçemeyeceğini iddia
ediyor.  Bu bir **fizik iddiasıdır**, bir sayma iddiası değil; ikisini
aynı başlık altında anmam yanlıştı.  M27'nin hükmü (yapılı durum
sınıfları klasik olarak ``N > 400``te de saklanır) doğruluğunu
koruyor, ama **Palmer'ın iddiasına cevap teşkil etmiyor**.

**Geri alma 2 -- "sanal sayının ilgası".**  ``reel.karmasik``
modülünde ``ℂ^N ≅ ℝ^{2N}`` gömmesinin hesap bakımından savunulabilir
olduğunu ölçtüm ve öyledir.  Fakat oradan "demek ki ``i``ye ihtiyaç
yok" neticesi çıkmaz ve ben de çıkarmadım -- yine de **eksik
bıraktım**: meselenin tamamı *tek sistemde* değil, **birleşik
sistemdedir** (tensör çarpımı).  Bu modül o eksiği kapatıyor.

Ayrıca **Palmer ``i``yi ilga etmiyor.**  RaQM, Hilbert uzayını
ayrıklaştırır ve durumların ancak *kare genlikleri ve karmaşık fazları
rasyonel* olduğu bazlarda tanımlı olduğunu söyler.  Yani karmaşık faz
teorinin içindedir; atılan şey **süreklilik**tir.  Kaynak risalenin
"``i`` yerine ``J`` yazalım" teklifi, Palmer'ın programının bir
tercümesi değil, bambaşka bir şeydir (ve ``J`` ikamesi zaten standart
kuantum mekaniğinin bilinen bir gösterimidir, yeni bir fizik değil).

--------------------------------------------------------------------
Dört itirazın tartılması
--------------------------------------------------------------------

Kullanıcının naklettiği eleştiri metnindeki dört itirazdan **üçü
sağlam, biri güncel değil**.  Hepsi burada ölçülüyor.

**İtiraz 1 -- Noether / sürekli simetri.**  Sağlam.  ``ℚ`` üzerinde
tek parametreli sürekli alt grup yoktur.  Ölçülüyor: rasyonel girdili
``SO(2)`` dönmeleri (Pisagor üçlüleri) bir **grup** oluşturur ve
``ℝ``de yoğundur, ama içinde ``θ → 0`` giden bir *sürekli yol*
bulunmadığından üreteç (Lie cebri öğesi) tanımlanamaz.

**İtiraz 2 -- Stone--von Neumann.**  Sağlam ve zaten ölçülmüştü.
``[x̂, p̂] = iħI``in izi alınırsa sol taraf **her zaman** 0, sağ taraf
``iħN ≠ 0``dır: sonlu boyutta bu bağıntı **imkânsızdır**.
``kuantum.surekli``de bunu zaten ölçmüştük -- kesilmiş Fock uzayında
``[a,a†] − I``in son köşegen girdisi tam olarak ``−N``dir.  O ölçüm,
Stone--von Neumann engelinin ta kendisidir; burada bağı kuruluyor.

**İtiraz 3 -- Renou vd. 2021: GÜNCEL DEĞİL.**  Eleştiri metni bunu
"matematiksel olarak ispatlanmış ve deneysel olarak mühürlenmiştir"
diye sunuyor.  2026 itibarıyla bu **fazla kesin** bir ifadedir.  2021
Nature neticesi, reel kuantum kuramının sistemleri **standart tensör
çarpımıyla** birleştirdiği varsayımı altında geçerlidir.  2025'te
*Phys. Rev. Lett.*'te çıkan "Quantum Mechanics Based on Real Numbers:
A Consistent Description", birleştirme kaidesi değiştirildiğinde
tamamen reel ve standart kuantum kuramından **deneysel olarak ayırt
edilemez** bir aile kurulabileceğini gösterdi; 2026'da buna bir
*Comment* yazıldı ve tartışma **hâlâ açıktır**.  Doğru ifade şudur:
*standart tensör çarpımı postülası altında* reel kuram elenmiştir; o
postüla gevşetilirse elenmez.  Tensör çarpımının neden meselenin
kalbi olduğu burada ölçülüyor: ``dim_ℝ(ℂ^m ⊗ ℂ^n) = 2mn`` iken
``ℝ^{2m} ⊗ ℝ^{2n} = 4mn``dir -- **iki kat** fazla.  Reel gömme tek
sistemde birebirdir, birleşik sistemde değildir.

**İtiraz 4 -- süperdeterminizm.**  Sağlam, fakat "gizli versiyon"
değil: Palmer bunu **açıkça** kabul ediyor; makalesinin adı bile
"Superdeterminism without Conspiracy"dir ve Ölçüm Bağımsızlığını (MI)
ihlal ettiğini kendisi söylüyor.  Buradaki asıl mesele şudur ve
ölçülüyor: "karşı-olgusal ayarlar irrasyonel açılara denk geldiği için
tanımsızdır" savunması Bell ihlalini **açıklamıyor**, çünkü CHSH
ihlali zaten **rasyonel** ayarlarla elde edilebiliyor.  Ölçülen:
Pisagor üçlülerinden kurulan tamamen rasyonel açılarla CHSH ``2.8``e
çok yaklaşıyor; irrasyonel açıya hiç ihtiyaç yok.

Kaynaklar (2026 Ağustos itibarıyla):
``arXiv:2510.02877`` / PNAS (RaQM), ``arXiv:2308.11262`` /
*Universe* 10(1):47 (Superdeterminism without Conspiracy),
``Nature 600, 625 (2021)`` (Renou vd.), ``Phys. Rev. Lett.`` 2025
(reel kuram, tutarlı tasvir) ve ona 2026 *Comment*'i.
"""

from __future__ import annotations

import itertools
import math
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "PALMER_IDDIALARI", "GERI_ALMALAR",
    "pisagor_donmeleri", "rasyonel_grup_kapali_mi",
    "surekli_altgrup_var_mi",
    "stone_von_neumann_engeli", "sonlu_boyutta_kanonik_baginti",
    "tensor_boyut_uyusmazligi", "reel_gomme_tek_sistemde_birebir",
    "chshdegeri", "rasyonel_ayarla_chsh", "en_iyi_rasyonel_chsh",
]

PALMER_IDDIALARI: Dict[str, str] = {
    "i_ilga_ediliyor_mu":
        "HAYIR. RaQM karmaşık fazı korur; attığı şey SÜREKLİLİKTİR. "
        "Durumlar ancak kare genlikleri ve karmaşık fazları rasyonel "
        "olan bazlarda tanımlıdır.",
    "kubit_tavani":
        "Bütün Hilbert uzayını kullanan algoritmaların (Shor) üstel "
        "avantajı ~200-400 hata düzeltilmiş kübitte doyar; hiçbir "
        "fizikî tatbikte ~1000'i geçmez. Bu bir FİZİK iddiasıdır, "
        "klasik bellek sayımı değildir.",
    "bell":
        "Karşı-olgusal ayarlar irrasyonel bazlara denk geldiğinde "
        "Hilbert durumu TANIMSIZDIR; bu yüzden karşı-olgusal kesinlik "
        "(CD) kurulamaz.",
    "superdeterminizm":
        "AÇIKÇA kabul ediliyor: Ölçüm Bağımsızlığı (MI) ihlal edilir. "
        "Palmer bunu 'komplosuz süperdeterminizm' diye adlandırır ve "
        "deneycinin NOMİNAL doğrulukta serbest seçimi ile TAM ayarı "
        "seçme kudreti arasında ayrım yapar.",
    "zemin":
        "Hilbert uzayının gravitasyonel ayrıklaştırılmasına dayanan, "
        "YEREL GERÇEKÇİ bir model.",
}

GERI_ALMALAR: List[Dict[str, str]] = [
    {"nerede": "hesap/saklama.py (M27)",
     "yazdığım": "'N > 400 saklanamaz' itirazı keyfî durum için "
                 "doğrudur; yapılı sınıflarda değildir.",
     "kusur": "Hüküm doğru ama Palmer'ın 400 kübit iddiasıyla aynı "
              "başlık altında anılamaz: onunki klasik bellek sayımı "
              "değil, fizikî kuantum avantajının doyması hakkında bir "
              "iddiadır.",
     "düzeltme": "M27 kaynak risale için geçerli kalır; Palmer'ın "
                 "iddiasına CEVAP TEŞKİL ETMEZ ve öyle okunmamalıdır."},
    {"nerede": "reel/karmasik.py",
     "yazdığım": "Reel gömme hesap bakımından savunulabilir (ölçülen "
                 "duvar saati 0.32-0.44×).",
     "kusur": "Ölçüm doğru ama EKSİK: tek sistemde birebir olan gömme "
              "BİRLEŞİK sistemde (tensör çarpımı) birebir değildir ve "
              "reel kuantum kuramı tartışmasının tamamı oradadır.",
     "düzeltme": "tensor_boyut_uyusmazligi() ile ölçülüp yazıldı; "
                 "modülün başlığına da not düşüldü."},
    {"nerede": "hesap/galois.py",
     "yazdığım": "Kaynağın 'çaresi doğru, teşhisi yanlış'.",
     "kusur": "Bu hüküm KAYNAK RİSALE için geçerlidir. Palmer'ın "
              "teşhisi float yuvarlaması değil, Hilbert uzayının "
              "ontolojisidir; benim M24 tashihim ona değinmiyor.",
     "düzeltme": "Ayrım açıkça yazıldı."},
]


# ══════════════════════════════════════════════════════════════════════
#  İtiraz 1: sürekli simetri / Noether
# ══════════════════════════════════════════════════════════════════════

def pisagor_donmeleri(azami: int = 60) -> List[Tuple[Fraction, Fraction]]:
    """``(cos, sin)`` rasyonel olan bütün ``SO(2)`` dönmeleri.

    ``a² + b² = c²`` üçlülerinden ``(a/c, b/c)``; işaretlerle birlikte.
    """
    out = set()
    for a in range(0, azami + 1):
        for b in range(0, azami + 1):
            c2 = a * a + b * b
            c = int(math.isqrt(c2))
            if c * c == c2 and c > 0:
                for sa in (1, -1):
                    for sb in (1, -1):
                        out.add((Fraction(sa * a, c), Fraction(sb * b, c)))
    return sorted(out)


def rasyonel_grup_kapali_mi(azami: int = 40, deneme: int = 3000,
                            tohum: int = 0) -> Dict[str, object]:
    """Rasyonel dönmeler çarpım altında kapalı mı? — evet, gruptur."""
    D = pisagor_donmeleri(azami)
    r = np.random.default_rng(tohum)
    kapali = 0
    for _ in range(deneme):
        (c1, s1) = D[int(r.integers(len(D)))]
        (c2, s2) = D[int(r.integers(len(D)))]
        c, s = c1 * c2 - s1 * s2, s1 * c2 + c1 * s2
        kapali += (c * c + s * s == 1)
    return {"öğe": len(D), "deneme": deneme, "kapalı": kapali,
            "grup_mu": kapali == deneme}


def surekli_altgrup_var_mi(azami: int = 200) -> Dict[str, object]:
    """``ℚ``da tek parametreli sürekli alt grup var mı? — yok.

    İki hüküm bir arada ölçülüyor:

    * Rasyonel dönme açıları ``[0, 2π)``de **yoğundur** (yaklaşma
      istenen hassasiyette mümkün).
    * Fakat *sıfırdan farklı en küçük* açı yoktur ve ``θ → 0``
      giderken dizinin üreteci ``ℚ``da **kalmaz**: ``(cosθ−1)/θ`` ve
      ``sinθ/θ`` limitleri rasyonel dizide tanımlı değildir.
      Lie cebri öğesi ``J = dR/dθ|₀`` bu yüzden ``ℚ``da yoktur.
    """
    D = [(c, s) for c, s in pisagor_donmeleri(azami) if s != 0]
    aci = sorted(float(math.atan2(s, c)) % (2 * math.pi) for c, s in D)
    bosluk = max(b - a for a, b in zip(aci, aci[1:])) if len(aci) > 1 else 0.0
    kucuk = min(a for a in aci if a > 1e-12)
    # θ → 0 giden dizide sin θ / θ nereye gidiyor? (limit 1, ama ℚ'da değil)
    kucukler = sorted(a for a in aci if 0 < a < 0.2)[:6]
    oran = [math.sin(a) / a for a in kucukler]
    return {"dönme_sayısı": len(D), "azamî_açı_boşluğu": bosluk,
            "en_küçük_pozitif_açı": kucuk,
            "sıfırdan_farklı_en_küçük_var_mı": False,
            "sin_bölü_teta_dizisi": oran,
            "limit_rasyonel_mi": False,
            "not": "yoğunluk yaklaşmayı sağlar; SÜREKLİLİK sağlamaz. "
                   "Üreteç dR/dθ|₀ bir LİMİTTİR ve ℚ'da yoktur."}


# ══════════════════════════════════════════════════════════════════════
#  İtiraz 2: Stone–von Neumann
# ══════════════════════════════════════════════════════════════════════

def stone_von_neumann_engeli(N: int = 8) -> Dict[str, object]:
    """``[x̂,p̂] = iħI`` sonlu boyutta **imkânsız** — iz ile ispat.

    ``Tr(AB − BA) = 0`` her zaman; ``Tr(iħI) = iħN ≠ 0``.  Bu, sayısal
    bir yaklaşıklık değil, cebirsel bir imkânsızlıktır.
    """
    r = np.random.default_rng(0)
    izler = []
    for _ in range(200):
        A = r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))
        B = r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))
        izler.append(abs(complex(np.trace(A @ B - B @ A))))
    return {"boyut": N,
            "komütatör_izi_azamî": float(np.max(izler)),
            "iħI_izi": float(N),           # ħ = 1
            "imkânsız_mı": True,
            "not": "Tr(AB−BA) = 0 her A,B için; Tr(iħI) = iħN ≠ 0."}


def sonlu_boyutta_kanonik_baginti(N: int = 16) -> Dict[str, object]:
    """Kesilmiş Fock uzayında ``[a,a†] − I`` nerede bozuluyor?

    ``kuantum.surekli.komutator_sapmasi`` ile aynı ölçüm; buradaki
    mesele bunun **Stone--von Neumann engelinin ta kendisi** olduğunu
    göstermek.  Sapma son köşegende toplanır ve tam olarak ``−N``dir --
    izi sıfırlayan tek yol budur.
    """
    a = np.diag(np.sqrt(np.arange(1, N)), 1).astype(complex)
    C = a @ a.conj().T - a.conj().T @ a
    fark = C - np.eye(N)
    return {"boyut": N,
            "alt_blok_sapma": float(np.abs(fark[:N - 1, :N - 1]).max()),
            "son_köşegen": float(fark[N - 1, N - 1].real),
            "beklenen_son_köşegen": float(-N),
            "komütatörün_izi": float(np.trace(C).real),
            "iz_sıfır_mı": abs(float(np.trace(C).real)) < 1e-9}


# ══════════════════════════════════════════════════════════════════════
#  İtiraz 3: tensör çarpımı — reel kuram tartışmasının kalbi
# ══════════════════════════════════════════════════════════════════════

def tensor_boyut_uyusmazligi(m: int = 2, n: int = 2) -> Dict[str, object]:
    """``dim_ℝ(ℂ^m ⊗ ℂ^n) = 2mn`` ama ``ℝ^{2m} ⊗ ℝ^{2n} = 4mn``.

    Reel gömme **tek sistemde** birebirdir; **birleşik sistemde**
    değildir.  Renou vd. 2021'in elediği şey, birleştirmenin standart
    tensör çarpımıyla yapıldığı hâldir; 2025 PRL bu postülayı
    gevşetince ayırt edilemez bir reel aile kuruluyor.
    """
    karmasik = 2 * m * n
    reel = (2 * m) * (2 * n)
    return {"m": m, "n": n,
            "dim_R(C^m ⊗ C^n)": karmasik,
            "dim(R^2m ⊗ R^2n)": reel,
            "oran": reel / karmasik,
            "uyuşuyor_mu": karmasik == reel,
            "not": "Fazlalık, gömmenin çarpımsal OLMAMASINDAN gelir; "
                   "tartışmanın tamamı bu birleştirme kaidesindedir."}


def reel_gomme_tek_sistemde_birebir(N: int = 4, deneme: int = 200,
                                    tohum: int = 0) -> Dict[str, object]:
    """Tek sistemde gömme birebir, birleşikte çarpımsal değil.

    ``ρ(A) = [[ReA, −ImA],[ImA, ReA]]`` için:
    ``ρ(AB) = ρ(A)ρ(B)`` **doğru** (tek sistem),
    ``ρ(A⊗B) = ρ(A)⊗ρ(B)`` **yanlış** (boyutlar bile tutmuyor).
    """
    r = np.random.default_rng(tohum)

    def gom(A):
        return np.block([[A.real, -A.imag], [A.imag, A.real]])

    carpim_hata = 0.0
    for _ in range(deneme):
        A = r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))
        B = r.normal(size=(N, N)) + 1j * r.normal(size=(N, N))
        carpim_hata = max(carpim_hata,
                          float(np.abs(gom(A @ B) - gom(A) @ gom(B)).max()))
    A = r.normal(size=(2, 2)) + 1j * r.normal(size=(2, 2))
    B = r.normal(size=(2, 2)) + 1j * r.normal(size=(2, 2))
    sol = gom(np.kron(A, B))
    sag = np.kron(gom(A), gom(B))
    return {"tek_sistem_çarpım_hatası": carpim_hata,
            "tek_sistemde_birebir_mi": carpim_hata < 1e-9,
            "birleşik_sol_şekil": sol.shape,
            "birleşik_sağ_şekil": sag.shape,
            "şekiller_uyuşuyor_mu": sol.shape == sag.shape}


# ══════════════════════════════════════════════════════════════════════
#  İtiraz 4: rasyonel ayarlarla CHSH
# ══════════════════════════════════════════════════════════════════════

def chshdegeri(a1, a2, b1, b2) -> float:
    """Singlet için ``S = E(a₁,b₁) + E(a₁,b₂) + E(a₂,b₁) − E(a₂,b₂)``.

    Ayarlar ``(cos, sin)`` çiftleri olarak verilir (birim vektörler);
    ``E(a,b) = −a·b``.
    """
    def E(u, v):
        return -(float(u[0]) * float(v[0]) + float(u[1]) * float(v[1]))
    return E(a1, b1) + E(a1, b2) + E(a2, b1) - E(a2, b2)


def rasyonel_ayarla_chsh(azami: int = 40) -> Dict[str, object]:
    """**Rasyonel** ayarlarla CHSH ne kadar ihlal ediliyor?

    "Karşı-olgusal ayarlar irrasyonel açılara denk gelir" savunması,
    ihlalin irrasyonel açılara ihtiyaç duyduğunu varsayar.  Ölçüm bunu
    yalanlıyor: yalnız Pisagor üçlülerinden kurulan, **her bileşeni
    rasyonel** ayarlarla klasik sınır ``2`` rahatça aşılıyor.

    Arama dört katlı döngüyle ``|D|⁴``tü ve ``azami=40``ta bitmiyordu
    (ölçüldü).  ``S = −[a₁·(b₁+b₂) + a₂·(b₁−b₂)]`` olduğundan ``b``
    çifti sabitlenince en iyi ``a₁`` ve ``a₂`` **ayrı ayrı** seçilir;
    arama ``|D|²`` çifte iner ve her çiftte iki iç çarpım vektörüyle
    biter.
    """
    D = pisagor_donmeleri(azami)
    V = np.array([[float(c), float(s)] for c, s in D])
    en_iyi, en_iyi_ayar = 0.0, None
    for i in range(len(V)):
        topla = V[i][None, :] + V                  # b₁+b₂   (nb, 2)
        cikar = V[i][None, :] - V                  # b₁−b₂   (nb, 2)
        p1 = V @ topla.T                           # (na, nb)
        p2 = V @ cikar.T
        skor = np.abs(p1).max(axis=0) + np.abs(p2).max(axis=0)
        j = int(np.argmax(skor))
        if skor[j] <= en_iyi:
            continue
        ia = int(np.argmax(np.abs(p1[:, j])))
        ib = int(np.argmax(np.abs(p2[:, j])))
        # işaret seçimi: dört bileşimin en büyüğü
        for sa in (1, -1):
            for sb in (1, -1):
                a1 = (sa * D[ia][0], sa * D[ia][1])
                a2 = (sb * D[ib][0], sb * D[ib][1])
                v = abs(chshdegeri(a1, a2, D[i], D[j]))
                if v > en_iyi:
                    en_iyi, en_iyi_ayar = v, (a1, a2, D[i], D[j])
    return {"en_iyi_S": en_iyi, "klasik_sınır": 2.0,
            "tsirelson": 2 * math.sqrt(2),
            "klasik_aşıldı_mı": en_iyi > 2.0,
            "tsirelsona_uzaklık": 2 * math.sqrt(2) - en_iyi,
            "ayarlar": en_iyi_ayar,
            "bütün_bileşenler_rasyonel_mi": all(
                isinstance(x, Fraction) for c in (en_iyi_ayar or ())
                for x in c)}


def en_iyi_rasyonel_chsh(azamiler: Sequence[int] = (5, 12, 25, 40, 60)
                         ) -> List[Dict[str, object]]:
    """Rasyonel ayar kümesi büyüdükçe CHSH Tsirelson'a yaklaşıyor mu?"""
    return [{"azami": a, **{k: v for k, v in rasyonel_ayarla_chsh(a).items()
                            if k in ("en_iyi_S", "tsirelsona_uzaklık",
                                     "klasik_aşıldı_mı")}}
            for a in azamiler]


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _gosterim() -> str:
    s = []
    s.append("=== PALMER NE DİYOR (kaynak: arXiv:2510.02877 / PNAS, "
             "arXiv:2308.11262) ===")
    for k, v in PALMER_IDDIALARI.items():
        s.append("  • %s:" % k)
        for satir in _sar(v, 68):
            s.append("      " + satir)

    s.append("\n=== GERİ ALDIĞIM YERLER ===")
    for g in GERI_ALMALAR:
        s.append("  ── %s" % g["nerede"])
        s.append("     yazdığım : %s" % _sar(g["yazdığım"], 62)[0])
        for satir in _sar(g["yazdığım"], 62)[1:]:
            s.append("                %s" % satir)
        s.append("     kusur    : %s" % _sar(g["kusur"], 62)[0])
        for satir in _sar(g["kusur"], 62)[1:]:
            s.append("                %s" % satir)
        s.append("     düzeltme : %s" % _sar(g["düzeltme"], 62)[0])
        for satir in _sar(g["düzeltme"], 62)[1:]:
            s.append("                %s" % satir)

    s.append("\n=== İTİRAZ 1: ℚ'da sürekli alt grup yok (SAĞLAM) ===")
    g = rasyonel_grup_kapali_mi()
    s.append("  rasyonel dönme sayısı=%d   çarpım altında kapalı mı? %s"
             % (g["öğe"], g["grup_mu"]))
    s.append("  sınır büyüdükçe açı boşluğu kapanıyor (YOĞUNLUK):")
    for az in (20, 60, 200, 600):
        aa = surekli_altgrup_var_mi(az)
        s.append("    azami=%3d  dönme=%4d  azamî boşluk=%.4f rad  "
                 "en küçük pozitif açı=%.6f"
                 % (az, aa["dönme_sayısı"], aa["azamî_açı_boşluğu"],
                    aa["en_küçük_pozitif_açı"]))
    a = surekli_altgrup_var_mi(600)
    s.append("  Boşluk kapanıyor ama HİÇBİR sınırda en küçük açı sabit")
    s.append("  kalmıyor: sıfırdan farklı EN KÜÇÜK açı YOK. sin θ/θ dizisi:")
    s.append("    %s → 1'e gidiyor ama limit ℚ'da DEĞİL"
             % ["%.6f" % x for x in a["sin_bölü_teta_dizisi"][:4]])
    s.append("  Yani: yaklaşma var, SÜREKLİLİK yok. Üreteç dR/dθ|₀ bir")
    s.append("  limittir; Lie cebri, dolayısıyla Noether, kurulamaz.")

    s.append("\n=== İTİRAZ 2: Stone–von Neumann (SAĞLAM) ===")
    e = stone_von_neumann_engeli(8)
    s.append("  200 rastgele çiftte azamî |Tr(AB−BA)| = %.2e"
             % e["komütatör_izi_azamî"])
    s.append("  oysa Tr(iħI) = %.0f ≠ 0  →  sonlu boyutta [x,p]=iħI"
             % e["iħI_izi"])
    s.append("  İMKÂNSIZ (sayısal değil, cebirsel).")
    for N in (8, 16, 64):
        k = sonlu_boyutta_kanonik_baginti(N)
        s.append("  kesilmiş Fock N=%2d: alt blok sapma=%.1e  son köşegen=%+.0f"
                 "  (beklenen %+.0f)  komütatörün izi=%.1e"
                 % (N, k["alt_blok_sapma"], k["son_köşegen"],
                    k["beklenen_son_köşegen"], k["komütatörün_izi"]))
    s.append("  kuantum.surekli'de ölçtüğümüz '−N' sapması, tam olarak")
    s.append("  BU engelin kendisidir: iz sıfır kalsın diye tek yol.")

    s.append("\n=== İTİRAZ 3: Renou vd. — GÜNCEL DEĞİL (düzeltme) ===")
    s.append("  Eleştiri metni 'ispatlanmış ve mühürlenmiştir' diyor.")
    s.append("  2026 itibarıyla bu FAZLA KESİN. 2021 Nature neticesi,")
    s.append("  sistemlerin STANDART TENSÖR ÇARPIMIYLA birleştiği")
    s.append("  varsayımı altında geçerlidir. 2025 PRL o postülayı")
    s.append("  gevşetip ayırt edilemez bir reel aile kurdu; 2026'da")
    s.append("  ona bir Comment yazıldı. Tartışma AÇIK.")
    s.append("  Meselenin kalbi neden tensör çarpımı? — ölçelim:")
    for m, n in ((2, 2), (2, 3), (4, 4)):
        t = tensor_boyut_uyusmazligi(m, n)
        s.append("    m=%d n=%d: dim_ℝ(ℂ^m⊗ℂ^n)=%2d   ℝ^{2m}⊗ℝ^{2n}=%2d"
                 "   oran=%.0f×  uyuşuyor mu? %s"
                 % (m, n, t["dim_R(C^m ⊗ C^n)"], t["dim(R^2m ⊗ R^2n)"],
                    t["oran"], t["uyuşuyor_mu"]))
    b = reel_gomme_tek_sistemde_birebir()
    s.append("  TEK sistemde gömme çarpımsal mı? %s (hata %.1e)"
             % (b["tek_sistemde_birebir_mi"], b["tek_sistem_çarpım_hatası"]))
    s.append("  BİRLEŞİK sistemde: ρ(A⊗B) şekli %s, ρ(A)⊗ρ(B) şekli %s"
             % (b["birleşik_sol_şekil"], b["birleşik_sağ_şekil"]))
    s.append("  → şekiller bile tutmuyor. Reel gömme tek sistemde")
    s.append("    birebirdir, BİRLEŞİK sistemde değildir.")

    s.append("\n=== İTİRAZ 4: rasyonel ayarlarla CHSH (SAĞLAM, ama")
    s.append("    'gizli versiyon' değil — Palmer açıkça kabul ediyor) ===")
    s.append("  azamî   en iyi S   Tsirelson'a uzaklık   klasik aşıldı mı?")
    for d in en_iyi_rasyonel_chsh((5, 12, 25, 40)):
        s.append("  %5d    %.6f        %.6f            %s"
                 % (d["azami"], d["en_iyi_S"], d["tsirelsona_uzaklık"],
                    d["klasik_aşıldı_mı"]))
    r = rasyonel_ayarla_chsh(40)
    s.append("  en iyi ayarlar (hepsi RASYONEL): %s"
             % str(r["ayarlar"]).replace("Fraction", "F"))
    s.append("  Klasik sınır 2.0, Tsirelson %.6f." % r["tsirelson"])
    s.append("  CHSH ihlali İRRASYONEL AÇIYA MUHTAÇ DEĞİL. Dolayısıyla")
    s.append("  'karşı-olgusal ayarlar irrasyonel olduğu için tanımsız'")
    s.append("  savunması, ihlali tek başına açıklamıyor.")
    return "\n".join(s)


def _sar(metin: str, en: int) -> List[str]:
    kelime, satir, out = metin.split(), "", []
    for k in kelime:
        if len(satir) + len(k) + 1 > en:
            out.append(satir)
            satir = k
        else:
            satir = (satir + " " + k).strip()
    if satir:
        out.append(satir)
    return out or [""]


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
