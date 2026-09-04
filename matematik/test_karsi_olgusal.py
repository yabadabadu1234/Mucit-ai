"""``fitrat.karsi_olgusal`` sınamaları — Darboğaz 45-48."""

from __future__ import annotations

import itertools
import math

import numpy as np
import pytest

from matematik import fitrat as ko
from matematik.fitrat import Cizge


def _model():
    g = Cizge(("Z", "X", "Y"), (("Z", "X"), ("X", "Y"), ("Z", "Y")))
    return ko.YapisalModel(g, {
        "Z": lambda pa, u: u,
        "X": lambda pa, u: 2.0 * pa["Z"] + u,
        "Y": lambda pa, u: 3.0 * pa["X"] - 1.0 * pa["Z"] + u,
    })


# ── yapısal model ────────────────────────────────────────────────────

def test_topolojik_sira_ebeveynden_sonra_gelmiyor():
    M = _model()
    yer = {d: i for i, d in enumerate(M.sira)}
    for a, b in M.g.kenarlar:
        assert yer[a] < yer[b]


def test_coz_kapali_formla_uyusuyor():
    M = _model()
    u = {"Z": 0.5, "X": -0.2, "Y": 1.3}
    X = M.coz(u)
    assert X["Z"] == pytest.approx(0.5)
    assert X["X"] == pytest.approx(2 * 0.5 - 0.2)
    assert X["Y"] == pytest.approx(3 * X["X"] - X["Z"] + 1.3)


def test_eksik_denklem_reddediliyor():
    g = Cizge(("A", "B"), (("A", "B"),))
    with pytest.raises(ValueError):
        ko.YapisalModel(g, {"A": lambda pa, u: u})


# ── müdahale ─────────────────────────────────────────────────────────

def test_mudahale_giren_oku_siliyor_cikani_degil():
    M = _model()
    g2 = ko.budayarak_mudahale(M.g, "X")
    assert ("Z", "X") not in g2.kenarlar
    assert ("X", "Y") in g2.kenarlar
    assert ("Z", "Y") in g2.kenarlar


# ── 3-pas ────────────────────────────────────────────────────────────

def test_abduction_gurultuyu_geri_veriyor():
    M = _model()
    u = {"Z": 0.5, "X": -0.2, "Y": 1.3}
    geri = ko.abduction(M, M.coz(u))
    for k in u:
        assert geri[k] == pytest.approx(u[k], abs=1e-9)


def test_abduction_degismezi_46_5():
    M = _model()
    goz = M.coz({"Z": 0.5, "X": -0.2, "Y": 1.3})
    d = ko.abduction_degismezi(M, goz)
    assert d["sağlanıyor"]
    assert d["hata"] < 1e-12


@pytest.mark.parametrize("x", [-2.0, 0.0, 2.0, 5.5])
def test_karsiolgusal_kapali_formla_uyusuyor(x):
    M = _model()
    u = {"Z": 0.5, "X": -0.2, "Y": 1.3}
    goz = M.coz(u)
    r = ko.karsiolgusal(M, goz, {"X": x})
    assert r["geçerli"]
    # do(X=x): Y = 3x − Z + u_Y, Z gözlemden geliyor
    assert r["karşıolgusal"]["Y"] == pytest.approx(3 * x - goz["Z"] + u["Y"])
    assert r["karşıolgusal"]["Z"] == pytest.approx(goz["Z"])


def test_delta_cf_gozlenen_degerde_sifir():
    M = _model()
    goz = M.coz({"Z": 0.5, "X": -0.2, "Y": 1.3})
    r = ko.karsiolgusal(M, goz, {"X": goz["X"]})
    assert r["Δ_cf"] == pytest.approx(0.0, abs=1e-9)


def test_mudahale_gozlemi_degistirmiyor():
    """do(X) Z'yi koparmaz: kişiye özgü u korunur."""
    M = _model()
    goz = M.coz({"Z": 0.5, "X": -0.2, "Y": 1.3})
    r = ko.karsiolgusal(M, goz, {"X": 9.0})
    assert r["u"]["Z"] == pytest.approx(0.5)
    assert r["u"]["Y"] == pytest.approx(1.3)


# ── abduction tekilliği ──────────────────────────────────────────────

def _tekil_model():
    g = Cizge(("A", "B"), (("A", "B"),))
    return ko.YapisalModel(g, {"A": lambda pa, u: u,
                               "B": lambda pa, u: pa["A"] + u * u})


def test_toplamsal_gurultude_abduction_tekil_degil():
    g = Cizge(("A", "B"), (("A", "B"),))
    M = ko.YapisalModel(g, {"A": lambda pa, u: u,
                            "B": lambda pa, u: pa["A"] + u})
    assert not ko.abduction_tekil_mi(M, M.coz({"A": 1.0, "B": 2.0}))["tekil_mi"]


def test_dogrusal_olmayan_gurultude_tekil():
    """Şahit: kaynağın 'tekil kalıyor' dediği hâlin ŞARTI budur."""
    M = _tekil_model()
    t = ko.abduction_tekil_mi(M, M.coz({"A": 1.0, "B": 2.0}))
    assert t["tekil_mi"]
    assert t["tekil_düğümler"] == ["B"]


def test_tekil_halde_hukum_verilmiyor():
    M = _tekil_model()
    r = ko.karsiolgusal(M, {"A": 1.0, "B": 0.5}, {"A": 3.0})
    assert r["geçerli"] is False
    assert "tekil" in r["sebep"]


# ── NOTEARS ──────────────────────────────────────────────────────────

_DAG = np.array([[0, 1, 1], [0, 0, 1], [0, 0, 0.]])
_C2 = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0.]])
_C3 = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0.]])
_OZ = np.array([[0.3, 0, 0], [0, 0, 0], [0, 0, 0.]])


@pytest.mark.parametrize("A,cevrimsiz", [(_DAG, True), (_C2, False),
                                         (_C3, False), (_OZ, False),
                                         (np.zeros((3, 3)), True)])
def test_h_kombinatorikle_uyusuyor(A, cevrimsiz):
    c = ko.cevrimsiz_mi_h_ile(A)
    assert c["kombinatorik"] is cevrimsiz
    assert c["h_diyor_ki"] is cevrimsiz


def test_h_dagda_tam_sifir():
    assert ko.notears_h(_DAG) == pytest.approx(0.0, abs=1e-12)
    assert ko.notears_h(_C3) > 0.1


@pytest.mark.parametrize("tohum", range(4))
def test_notears_gradyani_sonlu_farkla_uyusuyor(tohum):
    A = np.random.default_rng(tohum).normal(size=(4, 4)) * 0.4
    G = ko.notears_gradyan(A)
    S = np.zeros_like(A)
    h = 1e-6
    for i, j in itertools.product(range(4), repeat=2):
        Ap, Am = A.copy(), A.copy()
        Ap[i, j] += h
        Am[i, j] -= h
        S[i, j] = (ko.notears_h(Ap) - ko.notears_h(Am)) / (2 * h)
    assert np.abs(G - S).max() / max(np.abs(S).max(), 1e-30) < 1e-6


def test_matris_usteli_ozayrisimla_uyusuyor():
    r = np.random.default_rng(0)
    M = r.normal(size=(5, 5))
    M = M + M.T                                   # simetrik → eigh ile kıyas
    lam, V = np.linalg.eigh(M)
    assert np.abs(ko._matris_ustel(M)
                  - (V * np.exp(lam)) @ V.T).max() < 1e-10


# ── örtük değişken ───────────────────────────────────────────────────

@pytest.mark.parametrize("a,b", [(1.0, 1.0), (2.0, 0.5), (0.5, 2.0)])
def test_ortuk_sahte_baginti_kesiliyor(a, b):
    o = ko.ortuk_sahte_baginti(a=a, b=b, tohum=1)
    assert o["ham_bağıntı"] == pytest.approx(o["kuramsal_ham"], abs=0.03)
    assert abs(o["ham_bağıntı"]) > 0.2               # sahte bağıntı VAR
    assert abs(o["kısmî_bağıntı"]) < 0.05            # koşullama kesiyor
    assert abs(o["do_L_altında"]) < 0.05             # do(L) de kesiyor


def test_baglantisizsa_ham_baginti_da_sifir():
    o = ko.ortuk_sahte_baginti(a=1.0, b=0.0, tohum=1)
    assert abs(o["ham_bağıntı"]) < 0.05


# ── denge lokusu ─────────────────────────────────────────────────────

def _cember():
    return (lambda x: np.array([float(x @ x) - 1.0]),
            lambda x: 2.0 * x[None, :],
            lambda x: np.array([1.0, 0.0]))


def test_locus_izdusumu_idempotent_ve_cekirdege_dusuyor():
    J = np.array([[2.0, 0.0]])
    P = ko.locus_izdusumu(J)
    assert np.abs(P @ P - P).max() < 1e-13
    assert np.abs(P - P.T).max() < 1e-13
    assert np.abs(J @ P).max() < 1e-13


def test_bagimli_kisitlarda_sozde_ters_patlamiyor():
    J = np.array([[1.0, 0.0], [2.0, 0.0]])       # ikinci satır birincinin katı
    P = ko.locus_izdusumu(J)
    assert np.all(np.isfinite(P))
    assert np.abs(J @ P).max() < 1e-12


@pytest.mark.parametrize("adim", [0.05, 0.2, 0.5])
def test_duzeltmesiz_tegetin_locustan_kaydigi(adim):
    """Şahit: Formül 48.2+48.3 tek başına yetmiyor."""
    phi, jac, grad = _cember()
    x0 = np.array([math.cos(0.4), math.sin(0.4)])
    a = ko.locus_uzerinde_yurut(phi, jac, grad, x0, adim=adim, duzelt=False)
    b = ko.locus_uzerinde_yurut(phi, jac, grad, x0, adim=adim, duzelt=True)
    assert a["azamî_ihlal"] > 50 * b["azamî_ihlal"]


def test_duzeltmeli_yurume_dogru_asgariye_variyor():
    phi, jac, grad = _cember()
    x0 = np.array([math.cos(0.4), math.sin(0.4)])
    r = ko.locus_uzerinde_yurut(phi, jac, grad, x0, adim=0.2, duzelt=True)
    assert r["x"][0] == pytest.approx(-1.0, abs=1e-3)
    assert float(np.linalg.norm(r["x"])) == pytest.approx(1.0, abs=1e-3)


def test_kritik_noktada_tegetin_sifirlandigi():
    """(1,0)'da gradyan tamamen normal: teğet izdüşümü hiç kımıldatmıyor."""
    phi, jac, grad = _cember()
    x0 = np.array([1.0, 0.0])
    r = ko.locus_uzerinde_yurut(phi, jac, grad, x0, adim=0.2, duzelt=False)
    assert np.abs(r["x"] - x0).max() < 1e-12
