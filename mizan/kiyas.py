"""
Kıyas-ı iktiranî: dört şekil, yirmi dört mûteber darb.

**Usul.** Darbların geçerliliği bir LİSTEDEN okunmaz; **tam model
sayımıyla** karara bağlanır. Bu, listeyi doğru kopyalayıp kopyalamadığımı
da sınar.

Üç terimli (``S``, ``M``, ``P``) tekli (monadic) yüklem mantığında bir
model, temel-eşdeğerlik bakımından tam olarak şu bilgiyle belirlenir:
**sekiz atomdan hangileri boş değil.** Atom, bir bireyin hangi terimleri
sağladığını söyleyen üçlüdür:

    atom a ∈ {0,…,7};  bit0 = S(a),  bit1 = M(a),  bit2 = P(a)

Dolayısıyla model = 8 bitlik bir tam sayı, ve **256 model tamamını
tüketir**. Yaklaşıklık yoktur; karar kesindir.

Önerme biçimleri bu temsilde birer bit işlemidir:

    A(X,Y) ∀x(X→Y)   ⟺  m & X & ~Y == 0
    E(X,Y) ∀x(X→¬Y)  ⟺  m & X & Y  == 0
    I(X,Y) ∃x(X∧Y)   ⟺  m & X & Y  != 0
    O(X,Y) ∃x(X∧¬Y)  ⟺  m & X & ~Y != 0

Bir darbın geçerliliği 256 modelde sabit zamanlı dört bit işlemiyle
sınanır; bütün ``4 × 4³ = 256`` darb-şekil bileşimi için toplam 65 536
sınama eder ve milisaniyeler sürer. Ölçüldü.

**Varlık faraziyesi.** Aristo terimlerin boş olmadığını zımnen kabul
eder; yüklem mantığında bu kabul YAZILMAK zorundadır. Burada faraziye
bir parametredir ve hangi darbın hangi terimin boş olmamasına muhtaç
olduğu **türetilir** (kaynak metinlere uygulanan T77--T81 tashihlerinin
fiilî sağlaması budur).
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

# --- terimler ve atomlar ----------------------------------------------
S, M, P = 0, 1, 2
TERIM_ADI = {S: "S", M: "M", P: "P"}

TUM = (1 << 8) - 1


def _terim_maskesi(t: int) -> int:
    """``t`` terimini sağlayan atomların maskesi."""
    return sum(1 << a for a in range(8) if (a >> t) & 1)


MASKE = (_terim_maskesi(S), _terim_maskesi(M), _terim_maskesi(P))


# --- önerme biçimleri --------------------------------------------------
def bu_hukum_bu_modelde_tutuyor_mu(m: int, x: int, y: int, bicim: str,
                                   maskeli: bool = False) -> bool:
    """BU HÜKÜM BU MODELDE TUTUYOR MU -- tek terkip (kütük H226).

    Küme: ``_A``, ``_E``, ``_I``, ``_O``. Dört isim, **tek** bit
    ameliydi ve o amel şudur:

        ``var = (m & S(x) & (P(y) yahut ~P(y))) != 0``

    * **kemiyet** (küllî A,E / cüz'î I,O) neyin sorulduğunu söyler:
      küllî böyle bir şeyin **yokluğunu** ister (``== 0``), cüz'î
      **varlığını** (``!= 0``).
    * **keyfiyet** (olumlu A,I / olumsuz E,O) yüklemin **tümleneceğini**
      söyler -- ve iki eksen ``XOR`` ile kenetlenir:
      ``tümlenmiş = (küllî ≠ olumsuz)``. Sebep cebrîdir: bir varlık
      önermesini değillemek keyfiyeti çevirir, zira
      ``¬∃(S ∧ ¬P)`` "her S P'dir" (A), ``¬∃(S ∧ P)`` ise
      "hiçbir S P değildir" (E)dir.

    Yâni dört biçim, iki ikili tercihin çarpımıdır ve Aristo'nun
    karşıtlık murabbaı tam bu iki eksendir. Ayrı ayrı yazıldıklarında
    ne murabba ne de o ``XOR`` görünüyordu.

    ``maskeli=True`` iken ``x`` ve ``y`` terim indisi değil **doğrudan
    maskedir**; aks-i nakîz (``¬P, ¬S``) böyle kurulur ve dört biçim
    orada da ikinci kere yazılmaz.
    """
    if bicim not in ("A", "E", "I", "O"):
        raise ValueError("önerme biçimi bilinmiyor: %r" % (bicim,))
    kulli = bicim in ("A", "E")           # kemiyet: yokluk mu istenir
    olumsuz = bicim in ("E", "O")         # keyfiyet
    mx = x if maskeli else MASKE[x]
    my = y if maskeli else MASKE[y]
    var = (m & mx & (~my if kulli != olumsuz else my)) != 0
    return (not var) if kulli else var


BICIMLER: Tuple[str, ...] = ("A", "E", "I", "O")

BICIM_ADI = {
    "A": "Mûcebe-i Külliyye",
    "E": "Sâlibe-i Külliyye",
    "I": "Mûcebe-i Cüz'iyye",
    "O": "Sâlibe-i Cüz'iyye",
}

# --- şekiller: (büyük öncülün terimleri, küçük öncülün terimleri) -----
# Netice dâima (S, P).
SEKIL: Dict[int, Tuple[Tuple[int, int], Tuple[int, int]]] = {
    1: ((M, P), (S, M)),
    2: ((P, M), (S, M)),
    3: ((M, P), (M, S)),
    4: ((P, M), (M, S)),
}

SEKIL_ADI = {
    1: "Şekl-i Evvel (orta terim birincide yüklem, ikincide özne)",
    2: "Şekl-i Sânî (orta terim her iki öncülde yüklem)",
    3: "Şekl-i Sâlis (orta terim her iki öncülde özne)",
    4: "Şekl-i Râbi' (Galenik)",
}

# --- klasik darb adları -----------------------------------------------
DARB_ADI: Dict[Tuple[int, str], str] = {
    (1, "AAA"): "Barbara", (1, "EAE"): "Celarent", (1, "AII"): "Darii",
    (1, "EIO"): "Ferio", (1, "AAI"): "Barbari", (1, "EAO"): "Celaront",
    (2, "EAE"): "Cesare", (2, "AEE"): "Camestres", (2, "EIO"): "Festino",
    (2, "AOO"): "Baroco", (2, "EAO"): "Cesaro", (2, "AEO"): "Camestros",
    (3, "AAI"): "Darapti", (3, "IAI"): "Disamis", (3, "AII"): "Datisi",
    (3, "EAO"): "Felapton", (3, "OAO"): "Bocardo", (3, "EIO"): "Ferison",
    (4, "AAI"): "Bamalip", (4, "AEE"): "Camenes", (4, "IAI"): "Dimatis",
    (4, "EAO"): "Fesapo", (4, "EIO"): "Fresison", (4, "AEO"): "Camenos",
}


# =====================================================================
#  Model sayımı
# =====================================================================
def modeller(bos_olmayan: Iterable[int] = ()) -> List[int]:
    """Verilen terimlerin boş olmadığı bütün modeller (8 bitlik maskeler).

    Faraziye yoksa 256 modelin tamamı döner.
    """
    sart = tuple(bos_olmayan)
    if not sart:
        return list(range(256))
    return [m for m in range(256)
            if all((m & MASKE[t]) != 0 for t in sart)]


_MODEL_ONBELLEK: Dict[FrozenSet[int], List[int]] = {}


def _modeller(sart: FrozenSet[int]) -> List[int]:
    """``modeller`` fonksiyonunun belleklenmiş hâli.

    256 darb-şekil bileşimi aynı model listesini tekrar tekrar ister;
    liste bir kere kurulup paylaşılır. Netice değişmez, yalnız tekrar
    hesap düşer.
    """
    l = _MODEL_ONBELLEK.get(sart)
    if l is None:
        l = modeller(sorted(sart))
        _MODEL_ONBELLEK[sart] = l
    return l


# =====================================================================
#  Geçerlilik
# =====================================================================
def gecerli_mi(sekil: int, darb: str,
               bos_olmayan: Iterable[int] = ()) -> bool:
    """``darb`` (üç harf: büyük öncül, küçük öncül, netice) geçerli mi?"""
    (bx, by), (kx, ky) = SEKIL[sekil]
    B = bu_hukum_bu_modelde_tutuyor_mu
    fb, fk, fn = (lambda m, x, y, c=c: B(m, x, y, c) for c in darb[:3])
    for m in _modeller(frozenset(bos_olmayan)):
        if fb(m, bx, by) and fk(m, kx, ky) and not fn(m, S, P):
            return False
    return True


def karsi_model(sekil: int, darb: str,
                bos_olmayan: Iterable[int] = ()) -> Optional[int]:
    """Geçersizse öncülleri doğrulayıp neticeyi yalanlayan bir model."""
    (bx, by), (kx, ky) = SEKIL[sekil]
    B = bu_hukum_bu_modelde_tutuyor_mu
    fb, fk, fn = (lambda m, x, y, c=c: B(m, x, y, c) for c in darb[:3])
    for m in _modeller(frozenset(bos_olmayan)):
        if fb(m, bx, by) and fk(m, kx, ky) and not fn(m, S, P):
            return m
    return None


def model_yaz(m: int) -> str:
    """Modeli okunur biçimde: hangi atomlar boş değil."""
    if m == 0:
        return "{ } (bütün terimler boş)"
    parcalar = []
    for a in range(8):
        if (m >> a) & 1:
            ad = "".join(TERIM_ADI[t] if (a >> t) & 1 else "¬" + TERIM_ADI[t]
                         for t in (S, M, P))
            parcalar.append(ad)
    return "{ " + ", ".join(parcalar) + " }"


def butun_darblar() -> List[Tuple[int, str]]:
    """4 şekil × 4³ darb = 256 bileşim."""
    return [(s, a + b + c)
            for s in (1, 2, 3, 4)
            for a in "AEIO" for b in "AEIO" for c in "AEIO"]


def gecerli_darblar(bos_olmayan: Iterable[int] = ()) -> List[Tuple[int, str]]:
    sart = tuple(bos_olmayan)
    return [(s, d) for (s, d) in butun_darblar() if gecerli_mi(s, d, sart)]


def asgari_varlik_faraziyesi(sekil: int, darb: str) -> Optional[FrozenSet[int]]:
    """Darbı geçerli kılan EN KÜÇÜK boş-olmama şartı.

    ``frozenset()`` : faraziyesiz geçerli.
    Tek terimli küme : o terimin boş olmaması yeter.
    ``None``         : üç terim birden boş olmasa dahi geçersiz.
    """
    if gecerli_mi(sekil, darb):
        return frozenset()
    for t in (S, M, P):
        if gecerli_mi(sekil, darb, (t,)):
            return frozenset({t})
    for ikili in ((S, M), (S, P), (M, P)):
        if gecerli_mi(sekil, darb, ikili):
            return frozenset(ikili)
    if gecerli_mi(sekil, darb, (S, M, P)):
        return frozenset({S, M, P})
    return None


# =====================================================================
#  Aks (çevirme) kanunları
# =====================================================================
def aks_gecerli_mi(kaynak: str, hedef: str, ters: bool = True,
                   bos_olmayan: Iterable[int] = ()) -> bool:
    """``kaynak(S,P)`` öncülünden ``hedef`` neticesi çıkar mı?

    ``ters=True`` ise hedefin terimleri ÇEVRİLİR (``P,S``); aks-i müstevî
    budur. ``ters=False`` iken hedef ``(S,P)`` üzerindedir.
    """
    B = bu_hukum_bu_modelde_tutuyor_mu
    def fk(m, x, y): return B(m, x, y, kaynak)
    def fh(m, x, y): return B(m, x, y, hedef)
    x, y = (P, S) if ters else (S, P)
    for m in _modeller(frozenset(bos_olmayan)):
        if fk(m, S, P) and not fh(m, x, y):
            return False
    return True


def aks_nakiz_gecerli_mi(kaynak: str, hedef: str) -> bool:
    """Aks-i nakîz: ``kaynak(S,P)`` ⟹ ``hedef(¬P, ¬S)``.

    Değillenmiş terimler için maskeler tümleyendir; bit işlemleri aynı
    kalır, yalnız maske değişir.
    """
    B = bu_hukum_bu_modelde_tutuyor_mu
    mx, my = ~MASKE[P] & TUM, ~MASKE[S] & TUM

    for m in range(256):
        if B(m, S, P, kaynak) and not B(m, mx, my, hedef, maskeli=True):
            return False
    return True


# =====================================================================
#  Sorites (zincirleme kıyas)
# =====================================================================
def sorites_gecerli_mi(zincir: Sequence[Tuple[int, int]], n_terim: int,
                       netice: Tuple[int, int],
                       bos_olmayan: Iterable[int] = ()) -> bool:
    """``A₁⊆A₂⊆…⊆A_k ⟹ A₁⊆A_k`` (tümel olumlu zincir).

    ``n_terim`` terim üzerinde ``2^{2^{n}}`` model olurdu; bunun yerine
    ATOM temsili yine kullanılır: atom sayısı ``2^n``, model sayısı
    ``2^{2^n}``. ``n ≤ 4`` için ``2^{16} = 65 536`` model, tam sayımla
    işlenebilir.
    """
    if n_terim > 4:
        raise ValueError("sorites tam sayımı 4 terime kadar")
    atom_sayisi = 1 << n_terim
    maske = [sum(1 << a for a in range(atom_sayisi) if (a >> t) & 1)
             for t in range(n_terim)]
    sart = [maske[t] for t in bos_olmayan]
    for m in range(1 << atom_sayisi):
        if any((m & s) == 0 for s in sart):
            continue
        if all((m & maske[x] & ~maske[y]) == 0 for (x, y) in zincir):
            if (m & maske[netice[0]] & ~maske[netice[1]]) != 0:
                return False
    return True


# =====================================================================
#  Rapor
# =====================================================================
def rapor() -> str:
    faraziyesiz = gecerli_darblar()
    faraziyeli = gecerli_darblar((S, M, P))
    fark = [x for x in faraziyeli if x not in faraziyesiz]

    satir = ["=== kıyas-ı iktiranî: tam model sayımı ===",
             "model uzayı: 2⁸ = 256 (tekli yüklem mantığında TAM)",
             "sınanan darb-şekil bileşimi: %d" % len(butun_darblar()),
             "",
             "varlık faraziyesi YOK  → geçerli darb: %d" % len(faraziyesiz),
             "varlık faraziyesi VAR  → geçerli darb: %d" % len(faraziyeli),
             "aradaki fark (faraziyeye MUHTAÇ olanlar): %d" % len(fark),
             ""]
    satir.append("Faraziyeye muhtaç darblar ve muhtaç oldukları terim:")
    for (s, d) in fark:
        asg = asgari_varlik_faraziyesi(s, d)
        terimler = ", ".join(TERIM_ADI[t] for t in sorted(asg or ()))
        satir.append("  %d. şekil %-3s %-10s → %s boş olmamalı"
                     % (s, d, DARB_ADI.get((s, d), "(adsız)"), terimler))
    satir.append("")
    satir.append("Adlandırılmış 24 darbın hepsi faraziyeli listede mi: %s"
                 % all(k in faraziyeli for k in DARB_ADI))
    return "\n".join(satir)


if __name__ == "__main__":
    print(rapor())
