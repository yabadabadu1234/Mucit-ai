"""
Uzaylar arası münasebetler, ayrık uzaylar, uç haller ve parametrik demetler.

Bu dosyanın en dikkate değer neticesi şudur: **zincir kuralı ve monoidal
uyum bu çatıda TANIMSAL olarak doğrudur** -- yani ``refl`` ile ispatlanır,
harici bir formül uydurmak gerekmez. ``dogrula_hepsi()`` bunları fiilen
``refl`` ile ispatlayıp tip denetiminden geçirir.

Kapsam:

  1. ``f : X → Y`` boyunca geri çekme ve itme:
     ``f^* P = λx. P (f x)``,
     ``Σ_f Q = λy. Σ(x:X). (f x = y) × Q x``,
     ``Π_f Q = λy. Π(x:X). (f x = y) → Q x``
     ve ``Σ_f ⊣ f^* ⊣ Π_f`` bitişiklik ifadeleri.
  2. ``(g∘f)^* ≡ f^* ∘ g^*``  -- **refl ile ispatlanır** (zincir kuralı).
     ``f^*(P × Q) ≡ f^*P × f^*Q`` -- **refl ile ispatlanır** (monoidal uyum).
  3. Teğet funktoru ``Tf`` ve ``T(g∘f) ≡ Tg ∘ Tf`` -- **refl**.
  4. Ayrık uzaylar: 0-kesilmişlik, ve "yüksek morfizmler önemsizleşir"
     iddiasının İSPATI (``isSet X → Π x. isContr (Ω(X,x))``).
  5. Uç haller: SDG'de kritik lokus ``Crit(f) = Σ(x:R). Π(d:D). f(x+d) = f(x)``.
  6. Parametrik lif demeti (moduli): ``E = Σ(w:M). F w``, kesitler,
     ve gayrilineerliği sağlayan kip (modality) -- kip POSTULATTIR.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import terimler as K
from . import cekirdek as C
from . import geometri as G
from . import kutuphane as L
from . import sozdizim as S
from . import turetimler as T
from .denetleyici import Baglam, denetle_tip
from .denetleyici import denetle_t as denetle
from .sozdizim import Terim

U = S.Evren(0)
U1 = S.Evren(1)
D = S.Deg


def bileske(f: Terim, g: Terim) -> Terim:
    """``g ∘ f``"""
    x = K.taze("x")
    return S.Lam(x, K.uygula(g, K.uygula(f, D(x))))


# =====================================================================
#  1. Geri çekme ve itme
# =====================================================================
def geri_cek(f: Terim, P: Terim) -> Terim:
    """``f^* P = λ x. P (f x)`` -- geri çekme (pullback) funktoru."""
    x = K.taze("x")
    return S.Lam(x, K.uygula(P, K.uygula(f, D(x))))


def toplam_it(X: Terim, Y: Terim, f: Terim, Q: Terim) -> Terim:
    """``Σ_f Q = λ y. Σ (x:X). (Path Y (f x) y) × Q x`` -- sol bitişik."""
    y, x = K.taze("y"), K.taze("x")
    return S.Lam(y, S.Sigma(x, X,
        S.carpim(S.yol(Y, K.uygula(f, D(x)), D(y)), K.uygula(Q, D(x)))))


def carpim_it(X: Terim, Y: Terim, f: Terim, Q: Terim) -> Terim:
    """``Π_f Q = λ y. Π (x:X). (Path Y (f x) y) → Q x`` -- sağ bitişik."""
    y, x = K.taze("y"), K.taze("x")
    return S.Lam(y, S.Pi(x, X,
        S.ok(S.yol(Y, K.uygula(f, D(x)), D(y)), K.uygula(Q, D(x)))))


def _aile_oku(A: Terim, F1: Terim, F2: Terim) -> Terim:
    """``Π (a:A). F1 a → F2 a`` -- aileler arası dönüşüm."""
    a = K.taze("a")
    return S.Pi(a, A, S.ok(K.uygula(F1, D(a)), K.uygula(F2, D(a))))


def bitisiklik_sol_tipi(X: Terim, Y: Terim, f: Terim,
                        Q: Terim, P: Terim) -> Terim:
    """``Denklik (Σ_f Q ⇒ P) (Q ⇒ f^* P)``  --  ``Σ_f ⊣ f^*``"""
    return L.denklik_tipi(_aile_oku(Y, toplam_it(X, Y, f, Q), P),
                          _aile_oku(X, Q, geri_cek(f, P)))


def bitisiklik_sag_tipi(X: Terim, Y: Terim, f: Terim,
                        P: Terim, Q: Terim) -> Terim:
    """``Denklik (f^* P ⇒ Q) (P ⇒ Π_f Q)``  --  ``f^* ⊣ Π_f``"""
    return L.denklik_tipi(_aile_oku(X, geri_cek(f, P), Q),
                          _aile_oku(Y, P, carpim_it(X, Y, f, Q)))


# =====================================================================
#  2. Zincir kuralı ve monoidal uyum -- TANIMSAL
# =====================================================================
def zincir_kurali_tipi(X: Terim, Z: Terim, f: Terim, g: Terim,
                       P: Terim) -> Terim:
    """``Path (X → U) ((g∘f)^* P) (f^* (g^* P))``"""
    return S.yol(S.ok(X, U), geri_cek(bileske(f, g), P),
                 geri_cek(f, geri_cek(g, P)))


def zincir_kurali_ispati(X: Terim, Z: Terim, f: Terim, g: Terim,
                         P: Terim) -> Terim:
    """İSPAT: ``refl``. İki taraf da ``λx. P (g (f x))``e indirgenir;
    yani zincir kuralı burada bir teorem değil, morfizm bileşkesinin
    TANIMSAL neticesidir."""
    return L.refl(geri_cek(bileske(f, g), P))


def monoidal_uyum_tipi(X: Terim, Y: Terim, f: Terim,
                       P: Terim, Q: Terim) -> Terim:
    """``Path (X → U) (f^*(P × Q)) (f^*P × f^*Q)``"""
    y = K.taze("y")
    carpim_ailesi = S.Lam(y, S.carpim(K.uygula(P, D(y)), K.uygula(Q, D(y))))
    x = K.taze("x")
    sag = S.Lam(x, S.carpim(K.uygula(geri_cek(f, P), D(x)),
                            K.uygula(geri_cek(f, Q), D(x))))
    return S.yol(S.ok(X, U), geri_cek(f, carpim_ailesi), sag)


def monoidal_uyum_ispati(X: Terim, Y: Terim, f: Terim,
                         P: Terim, Q: Terim) -> Terim:
    """İSPAT: ``refl`` -- tensör/çarpım yapısı geri çekmede TANIMSAL korunur."""
    y = K.taze("y")
    carpim_ailesi = S.Lam(y, S.carpim(K.uygula(P, D(y)), K.uygula(Q, D(y))))
    return L.refl(geri_cek(f, carpim_ailesi))


# =====================================================================
#  3. Teğet funktoru
# =====================================================================
def teget_donusumu(f: Terim) -> Terim:
    """``Tf : TX → TY``, ``v ↦ λd. f (v d)`` -- diferansiyel (Jacobian).

    Teğet demeti bir haritalama uzayı olduğundan ``Tf`` ayrıca inşa
    edilmez; ``f`` ile ard arda uygulamadan ibarettir.
    """
    v, d = K.taze("v"), K.taze("d")
    return S.Lam(v, S.Lam(d, K.uygula(f, K.uygula(D(v), D(d)))))


def teget_zincir_tipi(X: Terim, Z: Terim, f: Terim, g: Terim) -> Terim:
    """``Path (TX → TZ) (T(g∘f)) (Tg ∘ Tf)``"""
    TX, TZ = G.teget_demeti(X), G.teget_demeti(Z)
    return S.yol(S.ok(TX, TZ), teget_donusumu(bileske(f, g)),
                 bileske(teget_donusumu(f), teget_donusumu(g)))


def teget_zincir_ispati(X: Terim, Z: Terim, f: Terim, g: Terim) -> Terim:
    """İSPAT: ``refl`` -- teğet funktoru bileşkeyi TANIMSAL korur."""
    return L.refl(teget_donusumu(bileske(f, g)))


# =====================================================================
#  4. Ayrık uzaylar
# =====================================================================
def ayrik_mi(X: Terim) -> Terim:
    """Ayrıklık ölçütü: ``isSet X`` (0-kesilmişlik)."""
    return L.iz_kume(X)


def yuksek_morfizmler_onemsiz_tipi(X: Terim) -> Terim:
    """``isSet X → Π (x:X). isContr (Ω(X,x))``

    "Ayrık uzayda bütün yüksek morfizmler önemsizleşir" iddiasının tam
    ifadesi budur.
    """
    x = K.taze("x")
    return S.ok(L.iz_kume(X),
                S.Pi(x, X, L.iz_butun(L.dongu_uzayi(X, D(x)))))


def yuksek_morfizmler_onemsiz_ispati(X: Terim) -> Terim:
    """İSPAT: merkez ``refl x``; büzme, ``isSet``in kendisidir."""
    h, x, p = K.taze("h"), K.taze("x"), K.taze("p")
    return S.Lam(h, S.Lam(x, S.Cift(
        L.refl(D(x)),
        S.Lam(p, K.uygula(K.uygula(K.uygula(K.uygula(D(h), D(x)), D(x)),
                                  L.refl(D(x))), D(p))))))


def ayrik_uzay_tipi() -> Terim:
    """``Σ (X:U). isSet X`` -- ayrık uzaylar, hiyerarşinin en dip tabakası."""
    X = K.taze("X")
    return S.Sigma(X, U, ayrik_mi(D(X)))


def ayrik_postulatlari() -> List[T.Postulat]:
    """``Π₀ ⊣ Disc ⊣ Γ`` bitişiklik zinciri.

    ``Disc`` iç dilde zaten dâhil etmedir (bir küme bir tiptir); ``Π₀``
    ise küme-kesmesi (set truncation) bir HIT olduğundan ve bu çekirdekte
    genel HIT şeması bulunmadığından POSTULATTIR.
    """
    X = D("X")
    p0 = D("Pi0")
    x = K.taze("x")
    return [
        T.Postulat("Pi0", S.ok(U, U),
                   "Π₀ : bağlantılı bileşenler / küme-kesmesi (0-truncation)."),
        T.Postulat("Pi0_kume", S.Pi("X", U, L.iz_kume(K.uygula(p0, X))),
                   "Π₀X daima bir kümedir (0-kesilmiştir)."),
        T.Postulat("Pi0_birim", S.Pi("X", U, S.ok(X, K.uygula(p0, X))),
                   "Birim dönüşüm X → Π₀X."),
    ]


# =====================================================================
#  5. Uç haller: kritik lokus
# =====================================================================
def kritik_lokus(f: Terim) -> Terim:
    """``Crit(f) = Σ (x:R). Π (d:D). Path R (f (x+d)) (f x)``

    SDG'de "türev sıfırdır" şartı budur: fonksiyon sonsuz küçük her
    kaymada değişmiyorsa o nokta kritiktir. Asgari/azami noktalar bu
    alt-uzayın sakinleridir.
    """
    R = G.R
    x, d = K.taze("x"), K.taze("d")
    kayma = K.uygula(K.uygula(G.TOP, D(x)), S.Birinci(D(d)))
    return S.Sigma(x, R, S.Pi(d, G.sonsuz_kucukler(),
        S.yol(R, K.uygula(f, kayma), K.uygula(f, D(x)))))


def tikanma_postulati(X: Terim) -> T.Postulat:
    """Tıkanma (obstruction) sınıfı -- kohomoloji bu çekirdekte yok,
    POSTULATTIR."""
    return T.Postulat("tikanma", S.ok(S.ok(X, U), U),
                      "Bir ailenin global kesitinin varlığına engel olan "
                      "kohomolojik sınıf; sıfırdan farklıysa global inşa "
                      "imkânsızdır (tüylü top tipi haller).")


# =====================================================================
#  6. Parametrik lif demeti (moduli) -- "öğrenen geometri"
# =====================================================================
def evrensel_demet(M: Terim, F: Terim) -> Terim:
    """``E = Σ (w:M). F w`` -- parametre uzayı üzerindeki evrensel demet."""
    w = K.taze("w")
    return S.Sigma(w, M, K.uygula(F, D(w)))


def demet_izdusumu(M: Terim, F: Terim) -> Terim:
    """``π : E → M``"""
    e = K.taze("e")
    return S.Lam(e, S.Birinci(D(e)))


def agirlikta_lif(F: Terim, w: Terim) -> Terim:
    """``X_w = F w`` -- ağırlık ``w``de türetilen uzay (geri çekilmiş lif)."""
    return K.uygula(F, w)


def kesit_tipi(M: Terim, F: Terim) -> Terim:
    """``Π (w:M). F w`` -- seçim kesiti; "öğrenilmiş ağırlık" budur."""
    w = K.taze("w")
    return S.Pi(w, M, K.uygula(F, D(w)))


def lif_geri_cekme_ispati(M: Terim, F: Terim, w: Terim) -> Terim:
    """``E`` üzerinden ``w``deki lifi geri çekmek ``F w``yi verir --
    ``refl`` ile: parametrik geri çekme TANIMSALDIR."""
    return L.refl(K.uygula(F, w))


def kip_postulatlari() -> List[T.Postulat]:
    """Gayrilineerliği sağlayan kip (modality).

    Doğrusal funktorlar homotopik sınırları korur; gayrilineerlik, araya
    bir kip/kesme/lokalizasyon funktoru koyarak elde edilir. Kip bir HIT
    (kesme) gerektirdiğinden POSTULATTIR.
    """
    tau = D("tau")
    X = D("X")
    return [
        T.Postulat("tau", S.ok(U, U),
                   "Kip (modality): belirli homotopi katmanlarını bükerek "
                   "doğrusal geçişi kıran funktor -- ReLU'nun mukabili."),
        T.Postulat("tau_birim", S.Pi("X", U, S.ok(X, K.uygula(tau, X))),
                   "Kipin birim dönüşümü X → τX."),
        T.Postulat("tau_idempotent",
                   S.Pi("X", U, L.denklik_tipi(
                       K.uygula(tau, K.uygula(tau, X)), K.uygula(tau, X))),
                   "Kip idempotenttir: τ(τX) ≃ τX."),
    ]


# =====================================================================
#  Doğrulama
# =====================================================================
def _baglam() -> Baglam:
    g = G._geometri_baglami()
    for ad, tip in [("Y", U), ("Z", U)]:
        g = g.genislet_t(ad, tip)
    X, Y, Z = D("X"), D("Y"), D("Z")
    g = g.genislet_t("f", S.ok(X, Y))
    g = g.genislet_t("gg", S.ok(Y, Z))
    g = g.genislet_t("P", S.ok(Z, U))
    g = g.genislet_t("PY", S.ok(Y, U))
    g = g.genislet_t("QY", S.ok(Y, U))
    g = g.genislet_t("Q", S.ok(X, U))
    g = g.genislet_t("M", U)
    g = g.genislet_t("Fw", S.ok(D("M"), U))
    g = g.genislet_t("w", D("M"))
    g = g.genislet_t("fR", S.ok(G.R, G.R))
    return g


def dogrula_hepsi() -> List[Dict[str, str]]:
    g = _baglam()
    X, Y, Z = D("X"), D("Y"), D("Z")
    f, gg = D("f"), D("gg")
    P, PY, QY, Q = D("P"), D("PY"), D("QY"), D("Q")
    M, Fw, w = D("M"), D("Fw"), D("w")

    isler: List[Tuple[str, Callable[[], None]]] = [
        # 1. geri çekme / itme
        ("f^* : (Y→U) → (X→U)",
         lambda: denetle(geri_cek(f, PY), S.ok(X, U), g)),
        ("Σ_f : (X→U) → (Y→U)",
         lambda: denetle(toplam_it(X, Y, f, Q), S.ok(Y, U), g)),
        ("Π_f : (X→U) → (Y→U)",
         lambda: denetle(carpim_it(X, Y, f, Q), S.ok(Y, U), g)),
        ("bitişiklik Σ_f ⊣ f^* (tip) : U",
         lambda: denetle(bitisiklik_sol_tipi(X, Y, f, Q, PY), U, g)),
        ("bitişiklik f^* ⊣ Π_f (tip) : U",
         lambda: denetle(bitisiklik_sag_tipi(X, Y, f, PY, Q), U, g)),
        # 2. zincir kuralı ve monoidal uyum -- refl ile İSPATLANIR
        ("ZİNCİR KURALI (g∘f)^* ≡ f^*∘g^*  [refl ile İSPAT]",
         lambda: denetle(zincir_kurali_ispati(X, Z, f, gg, P),
                         zincir_kurali_tipi(X, Z, f, gg, P), g)),
        ("MONOİDAL UYUM f^*(P×Q) ≡ f^*P × f^*Q  [refl ile İSPAT]",
         lambda: denetle(monoidal_uyum_ispati(X, Y, f, PY, QY),
                         monoidal_uyum_tipi(X, Y, f, PY, QY), g)),
        # 3. teğet funktoru
        ("Tf : TX → TY",
         lambda: denetle(teget_donusumu(f),
                         S.ok(G.teget_demeti(X), G.teget_demeti(Y)), g)),
        ("TEĞET ZİNCİRİ T(g∘f) ≡ Tg∘Tf  [refl ile İSPAT]",
         lambda: denetle(teget_zincir_ispati(X, Z, f, gg),
                         teget_zincir_tipi(X, Z, f, gg), g)),
        # 4. ayrık uzaylar
        ("Ayrık uzay tipi : U₁", lambda: denetle(ayrik_uzay_tipi(), U1, g)),
        ("AYRIKTA YÜKSEK MORFİZMLER ÖNEMSİZ  [İSPAT]",
         lambda: denetle(yuksek_morfizmler_onemsiz_ispati(X),
                         yuksek_morfizmler_onemsiz_tipi(X), g)),
        # 5. uç haller
        ("Kritik lokus Crit(f) : U",
         lambda: denetle(kritik_lokus(D("fR")), U, g)),
        # 6. parametrik demet
        ("Evrensel demet E = Σ(w:M). F w : U",
         lambda: denetle(evrensel_demet(M, Fw), U, g)),
        ("π : E → M",
         lambda: denetle(demet_izdusumu(M, Fw),
                         S.ok(evrensel_demet(M, Fw), M), g)),
        ("Kesit (öğrenilmiş ağırlık) Π(w:M). F w : U",
         lambda: denetle(kesit_tipi(M, Fw), U, g)),
        ("Lif geri çekme TANIMSAL  [refl ile İSPAT]",
         lambda: denetle(lif_geri_cekme_ispati(M, Fw, w),
                         S.yol(U, agirlikta_lif(Fw, w),
                               agirlikta_lif(Fw, w)), g)),
    ]
    neticeler = [T._dene(ad, fn) for ad, fn in isler]

    # postulat tipleri iyi teşkil mi?
    gp = g
    for p in (ayrik_postulatlari() + kip_postulatlari()
              + [tikanma_postulati(X)]):
        neticeler.append(T._dene("POSTULAT tipi iyi teşkil: %s" % p.ad,
                                 lambda p=p, gp=gp: denetle_tip(p.tip, gp)))
        gp = gp.genislet_t(p.ad, p.tip)
    return neticeler


def rapor() -> str:
    satirlar = ["=" * 66,
                "omega_kategori.iliskiler -- uzaylar arası münasebetler",
                "=" * 66, ""]
    gecti = kaldi = 0
    for n in dogrula_hepsi():
        im = {"GEÇTİ": "  ✓ ", "EKSİK KURAL": "  ⊘ ", "HATA": "  ✗ "}[n["netice"]]
        satirlar.append("%s%s%s" % (im, n["ad"], "" if n["netice"] == "GEÇTİ"
                                    else "   [%s] %s" % (n["netice"],
                                                         n.get("izah", ""))))
        gecti += n["netice"] == "GEÇTİ"
        kaldi += n["netice"] != "GEÇTİ"
    satirlar += ["", "hulâsa: %d geçti, %d kaldı" % (gecti, kaldi), "=" * 66]
    return "\n".join(satirlar)
