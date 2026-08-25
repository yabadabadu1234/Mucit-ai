"""Karşıolgusal 3-pas, DAG öğrenmesi ve denge lokusu.

Kaynak: ``docs/kaynak/analitik_darbogazlar.txt`` Darboğaz 45-48.

**Karşıolgusal 3-pas (Darboğaz 46).**

1. *Abduction* — gözlemden gürültüyü çıkar: ``u = Y_göz − f(X_göz)``.
2. *Action* — çizgeyi buda: ``do(X_k = x)`` müdahalesi ``X_k``ye giren
   bütün okları siler.
3. *Prediction* — budanmış çizgeyi **aynı** ``u`` ile çöz.

Kaynağın kendi ölçütü doğrudur ve burada tartılıyor:
``Sol(G_orijinal, u) == Y_göz`` (Formül 46.5).  Bu "kayıpsız abduction
değişmezi", 1. pasın doğru yapıldığının şahididir; sağlanmıyorsa
3. pasın çıktısı **anlamsızdır**.

**Abduction ne zaman tekil kalır?**  Kaynak sorunu "denklem tekil
kalıyor" diye koyuyor ama şartı yazmıyor.  Şart şudur: yapısal
denklemler *tetikleyici* biçimde (``X_i = f_i(pa_i) + u_i``) yazıldığı
sürece ``u`` **her zaman** tek türlü çözülür -- Jacobi alt üçgenseldir
ve köşegeni ``I``dır.  Tekillik ancak gürültü *doğrusal olmayan* bir
biçimde girerse (``X_i = f_i(pa_i, u_i)``, ``∂f/∂u = 0`` olabilen)
doğar.  Bu iki hâl de burada kuruluyor ve ölçülüyor.

**DAG öğrenmesi (Darboğaz 45).**  NOTEARS değişmezi
``h(A) = tr(exp(A∘A)) − d``; ``h(A) = 0`` ⟺ ``A`` çevrimsiz.  Türevi
``∂h/∂A = 2(exp(A∘A))ᵀ ∘ A`` (Formül 45.3) -- kaynak bunu **doğru**
yazmış; sonlu farkla sağlaması yapılıyor.

**Örtük değişkenler (Darboğaz 47).**  Gözlenmeyen ``L``, ``X_i`` ile
``X_j`` arasında sahte bağıntı üretir; ``L``ye müdahale (``do``) veya
onu koşullamak bunu keser.  Ölçülen (``a=b=1``, ``n=4000``): ham
bağıntı **+0.5082** (kuramsal +0.5000), ``L``ye koşullu **−0.0137**,
``do(L)`` altında **−0.0076**.

**Denge lokusu (Darboğaz 48).**  ``S = {X : φ(X) = 0}`` üzerinde
gradyan iniş locus'tan fırlar; kaynak çareyi ``P = I − Jᵀ(JJᵀ)⁻¹J``
teğet izdüşümünde görüyor.  Ölçüm bunun **yetmediğini** gösteriyor:
teğet izdüşümü birinci mertebeden doğrudur, ikinci mertebeden kayma
her adımda birikir -- birim çemberde azamî ihlal ``adım=0.05``te
**9.9e-02**, ``adım=0.5``te **1.2e+00**.  Her adımdan sonra bir Newton
düzeltmesi (``x ← x − J⁺φ(x)``) eklendiğinde ihlal ``1.6e-06`` /
``1.3e-02``ye iniyor ve nokta doğru asgarîye varıyor.  Formül 48.2 ve
48.3 doğru ama **eksiktir**.
"""

from __future__ import annotations

import itertools
import math
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .ayrisma import Cizge

__all__ = [
    "YapisalModel", "budayarak_mudahale",
    "abduction", "karsiolgusal", "abduction_degismezi",
    "abduction_tekil_mi",
    "notears_h", "notears_gradyan", "cevrimsiz_mi_h_ile",
    "ortuk_sahte_baginti",
    "locus_izdusumu", "locus_uzerinde_yurut",
]


# ══════════════════════════════════════════════════════════════════════
#  1. Yapısal nedensel model
# ══════════════════════════════════════════════════════════════════════

class YapisalModel:
    """``X_i = f_i(pa_i, u_i)`` — topolojik sırada çözülür.

    ``denklemler[d]``: ``(ebeveyn_değerleri: Dict[str,float], u: float)
    -> float``.  Toplamsal gürültü şart değildir; şart olmadığı için
    abduction'ın ne zaman tekilleştiği ayrıca sınanabiliyor.
    """

    def __init__(self, cizge: Cizge,
                 denklemler: Dict[str, Callable[[Dict[str, float], float],
                                                float]]):
        eksik = set(cizge.dugumler) - set(denklemler)
        if eksik:
            raise ValueError("denklemi olmayan düğüm: %s" % sorted(eksik))
        self.g = cizge
        self.f = denklemler
        self.sira = self._topolojik()

    def _topolojik(self) -> List[str]:
        derece = {d: len(self.g.ebeveyn[d]) for d in self.g.dugumler}
        hazir = [d for d in self.g.dugumler if derece[d] == 0]
        sira: List[str] = []
        while hazir:
            d = hazir.pop(0)
            sira.append(d)
            for c in sorted(self.g.cocuk[d]):
                derece[c] -= 1
                if derece[c] == 0:
                    hazir.append(c)
        return sira

    def coz(self, u: Dict[str, float],
            sabit: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """``Sol(G, u)`` — ``sabit``teki düğümler zorlanır (müdahale)."""
        sabit = sabit or {}
        X: Dict[str, float] = {}
        for d in self.sira:
            if d in sabit:
                X[d] = float(sabit[d])
                continue
            pa = {p: X[p] for p in self.g.ebeveyn[d]}
            X[d] = float(self.f[d](pa, u.get(d, 0.0)))
        return X


def budayarak_mudahale(g: Cizge, dugum: str) -> Cizge:
    """``do(X_k)`` — ``X_k``ye **giren** okları sil (``G_ampüte``).

    Çıkan okları silmek yanlış olurdu: müdahale nedeni koparır,
    neticeyi değil.
    """
    return Cizge(g.dugumler,
                 tuple((a, b) for a, b in g.kenarlar if b != dugum))


# ══════════════════════════════════════════════════════════════════════
#  2. Üç pas
# ══════════════════════════════════════════════════════════════════════

def abduction(M: YapisalModel, gozlem: Dict[str, float],
              cozucu_tur: int = 80) -> Dict[str, float]:
    """1. pas: gözlemden ``u``yu geri çıkar.

    Toplamsal gürültüde ``u_i = X_i − f_i(pa_i, 0)`` doğrudan; genel
    hâlde ``f_i(pa_i, u) = X_i`` tek değişkenli denklemi sayısal
    olarak çözülür (kesme yöntemi, ``u ∈ [−10³, 10³]``).  Çözüm
    bulunamazsa **NaN** dönülür; sessizce sıfır koymak, 3. pasın
    çıktısını sahte kılardı.
    """
    u: Dict[str, float] = {}
    for d in M.sira:
        pa = {p: gozlem[p] for p in M.g.ebeveyn[d]}
        hedef = gozlem[d]

        def r(v):
            return M.f[d](pa, v) - hedef

        a, b = -1e3, 1e3
        ra, rb = r(a), r(b)
        if ra == 0.0:
            u[d] = a
        elif rb == 0.0:
            u[d] = b
        elif ra * rb > 0:
            u[d] = float("nan")          # kök yok ya da tek değil
        else:
            for _ in range(cozucu_tur):
                m = 0.5 * (a + b)
                rm = r(m)
                if ra * rm <= 0:
                    b, rb = m, rm
                else:
                    a, ra = m, rm
            u[d] = 0.5 * (a + b)
    return u


def abduction_degismezi(M: YapisalModel, gozlem: Dict[str, float]
                        ) -> Dict[str, object]:
    """Formül 46.5: ``Sol(G_orijinal, u) == Y_göz`` mi?

    Bu, 1. pasın sağlamasıdır.  Bozuksa 3. pasın çıktısına
    **güvenilemez**; o yüzden :func:`karsiolgusal` bunu önce koşuyor.
    """
    u = abduction(M, gozlem)
    if any(math.isnan(v) for v in u.values()):
        return {"u": u, "sağlanıyor": False, "hata": float("inf"),
                "sebep": "abduction tekil: bazı u çözülemedi"}
    tekrar = M.coz(u)
    hata = max(abs(tekrar[d] - gozlem[d]) for d in gozlem)
    return {"u": u, "yeniden_çözüm": tekrar, "hata": float(hata),
            "sağlanıyor": bool(hata < 1e-8), "sebep": ""}


def karsiolgusal(M: YapisalModel, gozlem: Dict[str, float],
                 mudahale: Dict[str, float]) -> Dict[str, object]:
    """Üç pası birlikte koş; değişmez bozuksa **hüküm verme**."""
    d = abduction_degismezi(M, gozlem)
    if not d["sağlanıyor"]:
        return {"geçerli": False, "sebep": d.get("sebep") or
                "abduction değişmezi bozuk (hata %.3e)" % d["hata"],
                "abduction_hatası": d["hata"], "u": d["u"]}
    u = d["u"]
    g2 = M.g
    for k in mudahale:
        g2 = budayarak_mudahale(g2, k)
    M2 = YapisalModel(g2, M.f)
    Y = M2.coz(u, sabit=mudahale)
    delta = math.sqrt(sum((Y[k] - gozlem[k]) ** 2 for k in gozlem))
    return {"geçerli": True, "u": u, "karşıolgusal": Y,
            "Δ_cf": delta, "abduction_hatası": d["hata"],
            "budanan_kenar": [e for e in M.g.kenarlar
                              if e not in g2.kenarlar]}


def abduction_tekil_mi(M: YapisalModel, gozlem: Dict[str, float]
                       ) -> Dict[str, object]:
    """Hangi düğümde ``u`` geri çıkarılamıyor? — kutuplu tanı."""
    u = abduction(M, gozlem)
    tekil = sorted(d for d, v in u.items() if math.isnan(v))
    return {"tekil_düğümler": tekil, "tekil_mi": bool(tekil), "u": u}


# ══════════════════════════════════════════════════════════════════════
#  3. NOTEARS çevrimsizlik değişmezi (Darboğaz 45)
# ══════════════════════════════════════════════════════════════════════

def _matris_ustel(M: np.ndarray, tur: int = 200) -> np.ndarray:
    """``exp(M)`` — ölçekle-kare-al + Taylor (``scipy`` yok)."""
    M = np.asarray(M, float)
    n = max(int(np.ceil(np.log2(max(np.abs(M).sum(axis=1).max(), 1e-30)))) + 4,
            0)
    A = M / (2.0 ** n)
    S = np.eye(A.shape[0])
    T = np.eye(A.shape[0])
    for k in range(1, tur):
        T = T @ A / k
        S = S + T
        if np.abs(T).max() < 1e-18:
            break
    for _ in range(n):
        S = S @ S
    return S


def notears_h(A: np.ndarray) -> float:
    """``h(A) = tr(exp(A∘A)) − d`` — ``0`` ⟺ çevrimsiz."""
    A = np.asarray(A, float)
    return float(np.trace(_matris_ustel(A * A)) - A.shape[0])


def notears_gradyan(A: np.ndarray) -> np.ndarray:
    """``∂h/∂A = 2 (exp(A∘A))ᵀ ∘ A`` (Formül 45.3) — kaynak doğru yazmış."""
    A = np.asarray(A, float)
    return 2.0 * _matris_ustel(A * A).T * A


def cevrimsiz_mi_h_ile(A: np.ndarray, esik: float = 1e-8
                       ) -> Dict[str, object]:
    """``h(A) ≤ esik`` (Formül 45.5) ile kombinatorik sayımı kıyasla."""
    A = np.asarray(A, float)
    B = (np.abs(A) > 0).astype(int)
    # Kahn: kombinatorik hakikat
    derece = B.sum(axis=0).tolist()
    kuyruk = [i for i, k in enumerate(derece) if k == 0]
    say = 0
    while kuyruk:
        i = kuyruk.pop()
        say += 1
        for j in np.nonzero(B[i])[0]:
            derece[j] -= 1
            if derece[j] == 0:
                kuyruk.append(int(j))
    h = notears_h(A)
    return {"h": h, "h_diyor_ki": bool(abs(h) <= esik),
            "kombinatorik": bool(say == B.shape[0]), "eşik": esik}


# ══════════════════════════════════════════════════════════════════════
#  4. Örtük değişken sahte bağıntısı (Darboğaz 47)
# ══════════════════════════════════════════════════════════════════════

def ortuk_sahte_baginti(n: int = 4000, a: float = 1.0, b: float = 1.0,
                        tohum: int = 0) -> Dict[str, float]:
    """``X ← L → Y``: ``L`` gözlenmezse ``X`` ile ``Y`` bağıntılı görünür.

    Üç okuma yan yana: (1) ham bağıntı, (2) ``L``ye koşullanmış kısmî
    bağıntı, (3) ``do(L = sabit)`` altındaki bağıntı.  İkisi de sahte
    bağıntıyı **keser**; ilki kesmez.
    """
    r = np.random.default_rng(tohum)
    L = r.normal(size=n)
    X = a * L + r.normal(size=n)
    Y = b * L + r.normal(size=n)

    def kor(u, v):
        return float(np.corrcoef(u, v)[0, 1])

    # L'ye koşullama = doğrusal artıklar üzerinden kısmî bağıntı
    ex = X - L * (X @ L) / (L @ L)
    ey = Y - L * (Y @ L) / (L @ L)
    Ld = np.zeros(n)                              # do(L = 0)
    Xd = a * Ld + r.normal(size=n)
    Yd = b * Ld + r.normal(size=n)
    return {"ham_bağıntı": kor(X, Y), "kısmî_bağıntı": kor(ex, ey),
            "do_L_altında": kor(Xd, Yd),
            "kuramsal_ham": a * b / math.sqrt((a * a + 1) * (b * b + 1))}


# ══════════════════════════════════════════════════════════════════════
#  5. Denge lokusu teğet izdüşümü (Darboğaz 48)
# ══════════════════════════════════════════════════════════════════════

def locus_izdusumu(J: np.ndarray) -> np.ndarray:
    """``P = I − Jᵀ(JJᵀ)⁻¹J`` — ``ker(dφ)``ye dik izdüşüm.

    ``JJᵀ`` tekilse (kısıtlar bağımlıysa) sözde ters kullanılır:
    ``inv`` çağırmak orada patlardı.
    """
    J = np.atleast_2d(np.asarray(J, float))
    return np.eye(J.shape[1]) - J.T @ np.linalg.pinv(J @ J.T) @ J


def locus_uzerinde_yurut(phi: Callable[[np.ndarray], np.ndarray],
                         jac: Callable[[np.ndarray], np.ndarray],
                         hedef_grad: Callable[[np.ndarray], np.ndarray],
                         x0: np.ndarray, adim: float = 0.05,
                         tur: int = 200, duzelt: bool = True
                         ) -> Dict[str, object]:
    """``S = {φ = 0}`` üzerinde inişi yürüt.

    ``duzelt=False`` iken salt teğet izdüşümü kullanılır: ikinci
    mertebeden **kayma** birikir ve nokta locus'tan çıkar.  ``True``
    iken her adımdan sonra bir Newton düzeltmesi
    (``x ← x − J⁺φ(x)``) yapılır ve kayma bastırılır.  İkisi
    kıyaslanıyor.
    """
    x = np.asarray(x0, float).copy()
    ihlal, deger = [], []
    for _ in range(tur):
        J = np.atleast_2d(jac(x))
        x = x - adim * (locus_izdusumu(J) @ hedef_grad(x))
        if duzelt:
            J = np.atleast_2d(jac(x))
            x = x - np.linalg.pinv(J) @ np.atleast_1d(phi(x))
        ihlal.append(float(np.abs(np.atleast_1d(phi(x))).max()))
        deger.append(x.copy())
    return {"x": x, "ihlal_seyri": ihlal, "son_ihlal": ihlal[-1],
            "azamî_ihlal": float(max(ihlal)), "yol": deger}


# ══════════════════════════════════════════════════════════════════════
#  Gösterim
# ══════════════════════════════════════════════════════════════════════

def _ornek_model() -> YapisalModel:
    """``Z → X → Y``, ``Z → Y`` — toplamsal gürültü."""
    g = Cizge(("Z", "X", "Y"), (("Z", "X"), ("X", "Y"), ("Z", "Y")))
    return YapisalModel(g, {
        "Z": lambda pa, u: u,
        "X": lambda pa, u: 2.0 * pa["Z"] + u,
        "Y": lambda pa, u: 3.0 * pa["X"] - 1.0 * pa["Z"] + u,
    })


def _gosterim() -> str:
    s = []
    M = _ornek_model()
    goz = M.coz({"Z": 0.5, "X": -0.2, "Y": 1.3})

    s.append("=== Karşıolgusal 3-pas ===")
    s.append("  model: Z→X, X→Y, Z→Y;  X = 2Z+u_X,  Y = 3X−Z+u_Y")
    s.append("  gözlem: " + ", ".join("%s=%.4f" % (k, goz[k])
                                      for k in ("Z", "X", "Y")))
    d = abduction_degismezi(M, goz)
    s.append("  1. pas (abduction): u = " +
             ", ".join("%s=%.4f" % (k, d["u"][k]) for k in ("Z", "X", "Y")))
    s.append("  Formül 46.5 değişmezi: Sol(G, u) == Y_göz mü? %s "
             "(hata %.2e)" % (d["sağlanıyor"], d["hata"]))
    for x in (-2.0, 0.0, 2.0):
        r = karsiolgusal(M, goz, {"X": x})
        s.append("  do(X=%+.1f): Y=%+.4f  (gözlemde %+.4f)   Δ_cf=%.4f   "
                 "budanan kenar=%s"
                 % (x, r["karşıolgusal"]["Y"], goz["Y"], r["Δ_cf"],
                    r["budanan_kenar"]))
    s.append("  Kapalı form: do(X=x) altında Y = 3x − Z + u_Y")
    for x in (-2.0, 0.0, 2.0):
        s.append("    x=%+.1f → %+.4f" % (x, 3 * x - goz["Z"] + d["u"]["Y"]))
    s.append("  Z gözlemden GELİYOR (müdahale onu koparmıyor); asıl")
    s.append("  karşıolgusallık burada: kişiye özgü u korunuyor.")

    s.append("\n=== Müdahale çıkan oku DEĞİL giren oku siler ===")
    g2 = budayarak_mudahale(M.g, "X")
    s.append("  do(X) sonrası kenarlar: %s" % (list(g2.kenarlar),))
    s.append("  X→Y duruyor (netice), Z→X gitti (sebep). Tersi olsaydı")
    s.append("  müdahalenin hiçbir tesiri kalmazdı.")

    s.append("\n=== Abduction ne zaman TEKİL kalır? ===")
    g = Cizge(("A", "B"), (("A", "B"),))
    iyi = YapisalModel(g, {"A": lambda pa, u: u,
                           "B": lambda pa, u: pa["A"] + u})
    kotu = YapisalModel(g, {"A": lambda pa, u: u,
                            "B": lambda pa, u: pa["A"] + u * u})
    for ad, mm in (("toplamsal  u", iyi), ("u² (tek yönlü)", kotu)):
        gg = mm.coz({"A": 1.0, "B": 2.0})
        t = abduction_tekil_mi(mm, gg)
        s.append("  %s: gözlem B=%.3f  tekil mi? %-5s  tekil düğüm=%s"
                 % (ad, gg["B"], t["tekil_mi"], t["tekil_düğümler"]))
    gg = {"A": 1.0, "B": 0.5}       # B < A: u² = −0.5, kök YOK
    t = abduction_tekil_mi(kotu, gg)
    s.append("  u² modelinde B=0.5 (yani u²=−0.5) istenirse: tekil mi? %s %s"
             % (t["tekil_mi"], t["tekil_düğümler"]))
    r = karsiolgusal(kotu, gg, {"A": 3.0})
    s.append("  bu hâlde karşıolgusal hüküm VERİLMİYOR: geçerli=%s (%s)"
             % (r["geçerli"], r["sebep"]))
    s.append("  Kaynağın 'denklem tekil kalıyor' dediği hâl budur; şartı")
    s.append("  yazmıyordu — gürültü doğrusal olmayan biçimde girerse.")

    s.append("\n=== NOTEARS h(A): çevrimsizlik değişmezi ===")
    ornekler = [
        ("üçgen DAG", np.array([[0, 1, 1], [0, 0, 1], [0, 0, 0.]])),
        ("2-çevrim", np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0.]])),
        ("3-çevrim", np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0.]])),
        ("öz-döngü", np.array([[0.3, 0, 0], [0, 0, 0], [0, 0, 0.]])),
        ("boş", np.zeros((3, 3))),
    ]
    for ad, A in ornekler:
        c = cevrimsiz_mi_h_ile(A)
        s.append("  %-10s h(A)=%.6e   h diyor ki=%-5s  kombinatorik=%-5s  "
                 "uyuşuyor: %s"
                 % (ad, c["h"], c["h_diyor_ki"], c["kombinatorik"],
                    c["h_diyor_ki"] == c["kombinatorik"]))
    s.append("  Gradyan sağlaması (Formül 45.3, sonlu farkla):")
    r2 = np.random.default_rng(0)
    for _ in range(3):
        A = r2.normal(size=(4, 4)) * 0.4
        G = notears_gradyan(A)
        S = np.zeros_like(A)
        h_ = 1e-6
        for i, j in itertools.product(range(4), repeat=2):
            Ap, Am = A.copy(), A.copy()
            Ap[i, j] += h_
            Am[i, j] -= h_
            S[i, j] = (notears_h(Ap) - notears_h(Am)) / (2 * h_)
        s.append("    azamî bağıl fark = %.2e"
                 % float(np.abs(G - S).max() / max(np.abs(S).max(), 1e-30)))

    s.append("\n=== Örtük değişken: sahte bağıntı ===")
    for a, b in ((1.0, 1.0), (2.0, 0.5), (1.0, 0.0)):
        o = ortuk_sahte_baginti(a=a, b=b, tohum=1)
        s.append("  a=%.1f b=%.1f: ham=%+.4f (kuram %+.4f)  "
                 "L'ye koşullu=%+.4f  do(L)=%+.4f"
                 % (a, b, o["ham_bağıntı"], o["kuramsal_ham"],
                    o["kısmî_bağıntı"], o["do_L_altında"]))
    s.append("  Ham bağıntı kuramsal değeri tutuyor; koşullama ve do(L)")
    s.append("  ikisi de sahte yolu kesiyor. b=0'da zaten bağıntı yok.")

    s.append("\n=== Denge lokusu: teğet izdüşümü yetiyor mu? ===")
    # φ(x) = ‖x‖² − 1 (birim çember), hedef: x₀'ı küçült
    def phi(x):
        return np.array([float(x @ x) - 1.0])

    def jac(x):
        return 2.0 * x[None, :]

    def grad(x):
        return np.array([1.0, 0.0])

    # Başlangıç (1,0) OLMAZ: orada gradyan tamamen normal yönde, teğet
    # izdüşümü sıfır verir ve hiçbir şey kımıldamaz (ölçüldü: ihlal 0,
    # varılan nokta yine (1,0)).  Genel bir noktadan başlanıyor.
    x0 = np.array([math.cos(0.4), math.sin(0.4)])
    for adim in (0.05, 0.2, 0.5):
        a_ = locus_uzerinde_yurut(phi, jac, grad, x0, adim=adim, duzelt=False)
        b_ = locus_uzerinde_yurut(phi, jac, grad, x0, adim=adim, duzelt=True)
        s.append("  adım=%.2f  düzeltmesiz azamî ihlal=%.2e   "
                 "düzeltmeli=%.2e   varılan x=(%+.4f,%+.4f)"
                 % (adim, a_["azamî_ihlal"], b_["azamî_ihlal"],
                    b_["x"][0], b_["x"][1]))
    s.append("  Teğet izdüşümü tek başına YETMİYOR: ikinci mertebeden")
    s.append("  kayma birikiyor ve adım büyüdükçe ihlal büyüyor.")
    s.append("  Newton düzeltmesiyle nokta locus'ta kalıyor ve")
    s.append("  x₀ = −1 asgarîsine varıyor (‖x‖=1 üzerinde doğru cevap).")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
