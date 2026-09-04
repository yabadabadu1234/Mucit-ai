"""``tashih_meleke`` cetvelinin makine sağlaması.

Usul :mod:`test_tashih_kuantum` ile aynı: her sınama, kaydın
``sağlama`` alanında adı geçen testtir ve **eski hâlin somut bir
örnekte çuvalladığını** gösterir.  Yalnız "yeni hâl doğru" demek
zayıftır.

Çalıştırma: ``python3 -m pytest docs/kaynak/test_tashih_meleke.py -q``
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from docs.kaynak import tashih_meleke as TM          # noqa: E402
from docs.kaynak import tex_denetle as TD            # noqa: E402

KAYNAK = os.path.dirname(os.path.abspath(__file__))
TASHIHLI = os.path.join(KAYNAK, "tashihli")


def _tashihli(ad: str) -> str:
    kok, uz = os.path.splitext(ad)
    return os.path.join(TASHIHLI, kok + "_tashihli" + uz)


# ══════════════════════════════════════════════════════════════════════
#  Cetvelin kendi tutarlılığı
# ══════════════════════════════════════════════════════════════════════

def test_her_tashih_tam_bir_kere_esliyor():
    uygulanan = TM.uygula()
    assert sum(len(v) for v in uygulanan.values()) == len(TM.T)


def test_numaralar_tekil_ve_sirali():
    nolar = [t.no for t in TM.T]
    assert nolar == sorted(nolar)
    assert len(set(nolar)) == len(nolar)


def test_cetvel_kayittan_uretiliyor():
    c = TM.cetvel()
    for t in TM.T:
        assert ("M%d — %s" % (t.no, t.baslik)) in c


def test_saglamasi_yazili_testler_gercekten_var():
    burada = {ad for ad in globals() if ad.startswith("test_")}
    for t in TM.T:
        if t.saglama:
            assert t.saglama in burada, (t.no, t.saglama)


def test_yedi_kaynak_da_kayitli():
    assert len(TM.DOSYALAR) == 7
    for ad in TM.DOSYALAR:
        assert os.path.exists(os.path.join(KAYNAK, ad)), ad


# ══════════════════════════════════════════════════════════════════════
#  M1-M8: derleme
# ══════════════════════════════════════════════════════════════════════

def _derleme_kiyasi(ad: str, en_az_bulgu: int):
    TM.uygula()
    ham = TD.dosya_denetle(os.path.join(KAYNAK, ad))
    assert len(ham) >= en_az_bulgu, "kaynak zaten temizse tashih gereksizdi"
    duzgun = TD.dosya_denetle(_tashihli(ad))
    assert duzgun == [], duzgun


def test_dalga_bukum_derleniyor():
    _derleme_kiyasi(TM.BUKUM, 3)
    metin = open(_tashihli(TM.BUKUM), encoding="utf-8").read()
    assert '\\end{align">' not in metin


def test_asgari_arama_derleniyor():
    _derleme_kiyasi(TM.ARAMA, 4)
    metin = open(_tashihli(TM.ARAMA), encoding="utf-8").read()
    assert '\\end{align">' not in metin
    assert '\\end{enumerate">' not in metin


def test_veri_akis_derleniyor():
    _derleme_kiyasi(TM.AKIS, 4)
    metin = open(_tashihli(TM.AKIS), encoding="utf-8").read()
    assert "\\end{caption{" not in metin
    assert "\\caption{Karmaşıklık Mukayese Cetveli}" in metin


def test_reel_meleke_derleniyor():
    _derleme_kiyasi(TM.REEL, 6)
    metin = open(_tashihli(TM.REEL), encoding="utf-8").read()
    assert '\\end{equation">' not in metin


def test_meleke_ve_hudutsuzluk_zaten_derleniyordu():
    """Dürüstlük: bu ikisinde yapısal bulgu YOKTU."""
    assert TD.dosya_denetle(os.path.join(KAYNAK, TM.MELEKE)) == []
    assert TD.dosya_denetle(os.path.join(KAYNAK, TM.HUDUT)) == []


# ══════════════════════════════════════════════════════════════════════
#  M9-M13: üniterlik
# ══════════════════════════════════════════════════════════════════════

def test_householder_butun_durumu_negatiflemiyor():
    """M9/M10: yansıma yalnız ``v`` bileşenini negatifler."""
    from matematik.geometri import kapi

    r = np.random.default_rng(0)
    d = 8
    v = r.normal(size=d); v /= np.linalg.norm(v)
    U = kapi("yansıma", v=v)
    psi = r.normal(size=d); psi /= np.linalg.norm(psi)
    # ESKİ HÂL: "UΨ = −Ψ" — yanlış
    assert np.linalg.norm(U(psi) + psi) > 0.5
    # YENİ HÂL: Ψ − 2⟨v|Ψ⟩v — doğru
    assert np.abs(U(psi) - (psi - 2 * (v @ psi) * v)).max() < 1e-14
    # ve norm korunuyor: genlik YOK EDİLEMEZ
    assert np.linalg.norm(U(psi)) == pytest.approx(1.0)
    # sadece paralel hâlde −Ψ
    assert np.linalg.norm(U(v) + v) < 1e-13
    # gerçekten silmek için izdüşüm gerekir ve o üniter DEĞİL
    P = kapi("silme", v=v)
    assert abs(v @ P(psi)) < 1e-13
    assert np.linalg.norm(P(psi)) < 1.0


def test_kok_p_kosegeni_uniter_degil():
    """M11/M12: ``diag(√P)`` ve ``diag(P)`` üniter değil."""
    P = np.array([0.4058, 0.2546, 0.1409, 0.1987])
    A = np.diag(np.sqrt(P))
    assert np.abs(A.T @ A - np.eye(4)).max() > 0.5
    assert np.abs(A.T @ A - np.diag(P)).max() < 1e-12
    B = np.diag(P)                                  # reel nüshadaki hâl
    assert np.abs(B.T @ B - np.eye(4)).max() > np.abs(
        A.T @ A - np.eye(4)).max()


def test_sek_zan_yakin_uniter_degil():
    """M13: kaynağın yazdığı üç terimli işleç üniter değil."""
    th = 0.7
    M = np.zeros((2, 2), complex)
    M[1, 1] = math.cos(th)
    M[0, 1] = math.sin(th)
    assert np.abs(M.conj().T @ M - np.eye(2)).max() > 0.5
    # tashihli hâl (SO(2)) üniter
    from matematik.geometri import kapi
    G = kapi("so2", theta=th, D=2).dizey()
    assert np.abs(G.T @ G - np.eye(2)).max() < 1e-14


# ══════════════════════════════════════════════════════════════════════
#  M14-M16: cebir
# ══════════════════════════════════════════════════════════════════════

def test_grup_komutatoru_cebirde_degil():
    """M14/M15: iki dik dizeyin komütatörü ``so(n)``de değil."""
    from matematik.geometri import grup_komutatoru_cebirde_mi

    for D in (6, 16):
        g = grup_komutatoru_cebirde_mi(D)
        assert g["grup_yatkın_sapması"] > 0.1     # so(D)'de DEĞİL
        assert g["üreteç_yatkın_sapması"] < 1e-10  # üreteçler so(D)'de


def test_carpim_usteli_ancak_komut_edende_esit():
    """M16: ``T exp(∫ΣH) = ΠU`` ancak sıra değiştirirse."""
    from matematik.geometri import carpim_trotter_farki

    c = carpim_trotter_farki()
    assert c["genel_fark"] > 0.1
    assert c["komut_eden_fark"] < 1e-12
    assert c["komutatör_normu"] > 1.0


# ══════════════════════════════════════════════════════════════════════
#  M17: no-communication
# ══════════════════════════════════════════════════════════════════════

def test_yerel_uniter_uzak_indirgenmisi_degistirmiyor():
    """M17: yerel kapı ``ρ_B``yi HİÇ değiştirmez."""
    r = np.random.default_rng(0)
    psi = r.normal(size=16) + 1j * r.normal(size=16)
    psi /= np.linalg.norm(psi)

    def rho_B(p):
        T = p.reshape(4, 4)
        return T.conj().T @ T

    A = r.normal(size=(4, 4)) + 1j * r.normal(size=(4, 4))
    A = A + A.conj().T
    lam, V = np.linalg.eigh(A)
    UA = (V * np.exp(-1j * lam)) @ V.conj().T
    psi2 = np.kron(UA, np.eye(4)) @ psi
    assert np.abs(rho_B(psi) - rho_B(psi2)).max() < 1e-13
    # ama ORTAK durum gerçekten değişiyor: iddia "hiçbir şey olmuyor" değil
    assert np.abs(psi - psi2).max() > 0.1


# ══════════════════════════════════════════════════════════════════════
#  M18-M19: arama
# ══════════════════════════════════════════════════════════════════════

def test_grover_yanlis_m_ile_basari_dusuyor():
    """M18: ``K`` bilinmeden ``m`` seçilemez."""
    from ogrenme.optimize import en_iyiyi_ara

    N = 1024
    f = np.random.default_rng(0).random(N)
    esik = np.sort(f)[64]
    kotu = en_iyiyi_ara(f, ne="grover", esik=esik,
                            m=en_iyiyi_ara(ne="tur", N=N, K=1))
    iyi = en_iyiyi_ara(f, ne="grover", esik=esik,
                            m=en_iyiyi_ara(ne="tur", N=N, K=64))
    assert kotu["başarı_olasılığı"] < 0.2
    assert iyi["başarı_olasılığı"] > 0.9
    # fazla dönmek zarar: 2·m_opt'ta çöküyor
    m = en_iyiyi_ara(ne="tur", N=N, K=1)
    e = en_iyiyi_ara(ne="eğri", N=N, K=1, azami_tur=2 * m)
    assert e[m] > 0.99 and e[2 * m] < 0.01


def test_adiyabatik_sonlu_T_de_tam_degil():
    """M19: hiçbir sonlu ``T``de başarı tam 1 değil."""
    from ogrenme.optimize import en_iyiyi_ara

    f = np.random.default_rng(5).random(16)
    f[3] = -1.0
    for T in (1.0, 16.0, 256.0):
        a = en_iyiyi_ara(f, ne="adiyabatik", T=T)
        assert a["tam_1_mi"] is False
        assert a["1_e_uzaklık"] > 0.0
    # ama T ile 1'e yaklaşıyor
    assert (en_iyiyi_ara(f, ne="adiyabatik", T=256.0)["başarı"]
            > en_iyiyi_ara(f, ne="adiyabatik", T=1.0)["başarı"])


# ══════════════════════════════════════════════════════════════════════
#  M20-M22: dalga bükümü
# ══════════════════════════════════════════════════════════════════════

def test_tunelleme_ussel_pahali():
    """M20: ``O(1)`` değil; beklenen deneme üstel."""
    from ogrenme.optimize import kuyudan_cik

    c = kuyudan_cik(ne="bedel", genislikler=(1, 2, 4, 8))
    assert c[-1]["beklenen_deneme"] / c[0]["beklenen_deneme"] > 1e6
    for d in c:
        assert d["T"] == pytest.approx(math.exp(-d["γ"]))


def test_duz_baglanti_trivial_holonomi_vermiyor():
    """M21: Aharonov–Bohm."""
    from nefs.zirh import aharonov_bohm

    d = aharonov_bohm(8, 0.37)
    assert d["F_yerel_sıfır_mı"]
    assert d["holonomi_trivial_mi"] is False
    assert d["|W−1|"] == pytest.approx(1.8355, abs=1e-3)
    # tam sayı akıda trivial: ölçüt akıya bağlı, F'ye değil
    assert aharonov_bohm(8, 1.0)["holonomi_trivial_mi"]


def test_grape_gradyani_dt_kare_yaklasimi():
    """M22: eşitlik değil, ``O(Δt²)`` yaklaşımı."""
    from nefs.melekeler import (grape_gradyani, sonlu_fark_gradyani,
                                tam_gradyan)

    n = 4

    def herm(sd):
        A = (np.random.default_rng(sd).normal(size=(n, n))
             + 1j * np.random.default_rng(sd + 99).normal(size=(n, n)))
        return A + A.conj().T

    H0, Hk = herm(1), [herm(2), herm(3)]
    psi0 = np.zeros(n, complex); psi0[0] = 1
    hedef = np.zeros(n, complex); hedef[n - 1] = 1
    oran = []
    for M in (20, 40, 80, 160):
        om = [np.full(M, 0.3), np.full(M, -0.2)]
        j, k = M // 3, 0
        sf = sonlu_fark_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        g = grape_gradyani(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        tam = tam_gradyan(H0, Hk, om, psi0, hedef, 1.0)[k][j]
        assert abs(g - sf) > 1e-6            # EŞİTLİK değil
        assert tam == pytest.approx(sf, abs=1e-8)   # tam türev uyuşuyor
        oran.append(abs(g - sf) * M * M)
    assert max(oran) / min(oran) < 1.5       # hata tam olarak O(Δt²)


# ══════════════════════════════════════════════════════════════════════
#  M23-M27: hesap
# ══════════════════════════════════════════════════════════════════════

def test_p_adik_toplam_normalizasyon_degil():
    """M23: ``Σ|c|_p² = 1`` ne Born'dur ne üniter altında korunur."""
    from fractions import Fraction

    from matematik.geometri import (arsimet_toplam, p_adik_toplam,
                             uniter_altinda_korunuyor_mu)

    c = [Fraction(1, 2)] * 4
    assert arsimet_toplam(c) == 1
    assert p_adik_toplam(c, 2) == 16              # 1 DEĞİL
    c2 = [Fraction(3, 5), Fraction(4, 5), Fraction(0), Fraction(0)]
    assert arsimet_toplam(c2) == 1
    assert p_adik_toplam(c2, 2) == Fraction(17, 16)
    u = uniter_altinda_korunuyor_mu(2, 200)
    assert u["arşimet_korunan"] == 200
    assert u["p_adik_korunan"] < 200              # korunmuyor


def test_float_hatasi_rasyonelde_de_var():
    """M24: teşhis 'irrasyonellik' değil, sonlu mantissa."""
    from matematik.geometri import float_hatasi_rasyonelde

    f = float_hatasi_rasyonelde()
    assert f["0.1+0.2==0.3"] is False
    assert f["on_kere_bir_mi"] is False
    assert f["tam_aritmetikte"] == 1.0
    # ve tam aritmetikte gerçekten sıfır hata (Galois halkası)
    from matematik.geometri import BIR, tam_devre
    t = tam_devre(["H"] * 20 + ["T"] * 20)
    assert t["norm_kare"] == BIR


def test_yapili_durumlar_400_kubitin_otesinde():
    """M27: itiraz keyfî durum için doğru, yapılı sınıfta değil."""
    from matematik.geometri import (Kararlayici, keyfi_durum_maliyeti,
                               kararlayici_maliyeti, mps_maliyeti)

    # keyfî: itiraz DOĞRU
    assert keyfi_durum_maliyeti(300)["evren_atomundan_fazla_mı"]
    assert keyfi_durum_maliyeti(400)["log10_katsayı_sayısı"] > 120
    # yapılı: 1024 kubit gerçekten koşuyor
    st = Kararlayici(1024)
    for i in range(0, 1024, 8):
        st.H(i)
    for i in range(0, 1023, 8):
        st.CNOT(i, i + 1)
    assert st.bellek_bayt() < 10e6
    assert st.olc(0, tohum=0)["netice"] in (0, 1)
    assert kararlayici_maliyeti(1024)["log10_bayt"] < 8
    assert mps_maliyeti(4096, 32)["log10_bayt"] < 9


# ══════════════════════════════════════════════════════════════════════
#  M28-M29: reel operatörler
# ══════════════════════════════════════════════════════════════════════

def test_reel_schrodinger_isareti():
    """M28: ``+J·H_ℝ`` zamanı tersine çeviriyor."""
    from matematik.geometri import (kaynak_isaretiyle_evrim, karmasik_coz,
                               reel_evrim, reel_goem)

    r = np.random.default_rng(0)
    N = 3
    A = r.normal(size=(N, N)); A = A + A.T
    B = r.normal(size=(N, N)); B = B - B.T
    H = A + 1j * B
    psi = r.normal(size=N) + 1j * r.normal(size=N)
    t = 0.6
    lam, V = np.linalg.eigh(H)
    ileri = (V * np.exp(-1j * lam * t)) @ (V.conj().T @ psi)
    geri = (V * np.exp(+1j * lam * t)) @ (V.conj().T @ psi)
    x = reel_goem(psi)
    assert np.abs(karmasik_coz(reel_evrim(H, t) @ x) - ileri).max() < 1e-12
    kotu = karmasik_coz(kaynak_isaretiyle_evrim(H, t) @ x)
    assert np.abs(kotu - ileri).max() > 0.5      # yanlış
    assert np.abs(kotu - geri).max() < 1e-12     # tam olarak zamanın tersi


def test_hartley_kosegen_evrisim_degil():
    """M29: RHT'de köşegen çarpan ancak çift simetride evrişim."""
    from matematik.geometri import (cift_simetrik_yap, dolasimli_hata,
                                    evrisim, hartley, hartley_evrisim)

    N = 8
    H = hartley(N=N, ne="dizey")
    r = np.random.default_rng(1).normal(size=N)
    assert dolasimli_hata(H.T @ np.diag(r) @ H) > 0.1        # evrişim DEĞİL
    assert dolasimli_hata(
        H.T @ np.diag(cift_simetrik_yap(r)) @ H) < 1e-12     # şart sağlanınca
    F = np.fft.fft(np.eye(N), axis=0) / math.sqrt(N)
    assert dolasimli_hata((F.conj().T @ np.diag(r) @ F).real) < 1e-12
    # evrişim kaidesi: naif çarpım yanlış, doğru kaide tutuyor
    rr = np.random.default_rng(2)
    f, g = rr.normal(size=N), rr.normal(size=N)
    sol = hartley(evrisim(f, g))
    Ff, Gg = hartley(f), hartley(g)
    assert np.abs(sol - hartley_evrisim(Ff, Gg, naif=True)).max() > 1.0
    assert np.abs(sol - hartley_evrisim(Ff, Gg)).max() < 1e-11


# ══════════════════════════════════════════════════════════════════════
#  M31-M34: ölçek
# ══════════════════════════════════════════════════════════════════════

def test_veri_akis_logaritma_aritmetigi():
    """M31: ``log₂²(10¹²) ≈ 1589``, 400 değil."""
    from nefs.hiz import log_aritmetigi

    a = log_aritmetigi(1e12)
    assert a["log2_kare"] == pytest.approx(1589.1, rel=1e-3)
    for anahtar in ("log2_kare", "log10_kare", "ln_kare"):
        assert abs(a[anahtar] - 400.0) > 100.0


def test_veri_akis_sikistirma_orani():
    """M32: ``N³/log²N = 6.29e32``, 1e28 değil."""
    from nefs.hiz import log_aritmetigi

    a = log_aritmetigi(1e12)
    assert a["N3_bolu_log2kare"] == pytest.approx(6.293e32, rel=1e-3)
    assert abs(math.log10(a["N2_bolu_log2kare"]) - 28.0) > 1.0


def test_bant_genisligi_carpimi_boyutsuz_degil():
    """M33: aynı külliyattaki iki belge mertebelerce çelişiyor."""
    from nefs.hiz import cati, esdegers_hiz_boyut_denetimi

    d = esdegers_hiz_boyut_denetimi()
    assert d["mertebe_farkı_D512"] == pytest.approx(37.0, abs=1.0)
    risale = 1e18 * 1e9
    assert math.log10(risale / (cati(D=512, ne="hız")["metin_MB_sn"] * 1e6)) \
        == pytest.approx(19.0, abs=0.5)


def test_aritmetik_yogunluk_yigina_bagli():
    """M34: raporun aritmetiği doğru, şartı yazılmamış."""
    from nefs.hiz import cati

    # rapor DOĞRU
    for D, mb in ((4096, 1.67), (512, 106.72)):
        assert cati(D=D, ne="hız")["metin_MB_sn"] == pytest.approx(mb, rel=2e-3)
    # ama B=1'de bellek bağlı
    for D in (512, 4096):
        c = cati(D=D, B=1)
        assert c["yoğunluk"] == pytest.approx(1.0, rel=0.05)
        assert c["bellek_bağlı_mı"]
        assert c["tepe_gücün_kaçta_biri"] == pytest.approx(524.0, rel=0.1)
        assert cati(D=D, ne="eşik") >= 1024
