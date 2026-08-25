"""Tashihlerin makine sağlaması.

Bir tashihin gerekçesini yazmak yetmez; **gösterilebilir** olduğunu
iddia ettiysek göstermek lazım.  Bu dosyadaki her test, cetveldeki bir
kaydın ``sağlama`` alanında adı geçen testtir ve o kaydın *kaynaktaki
hâlinin yanlış*, *tashihli hâlinin doğru* olduğunu ölçer.

Ölçüt kasten iki yönlüdür: yalnız "tashihli hâl doğru" demek zayıftır,
çünkü doğru olan başka bir şey de yazılabilirdi.  Asıl mesele, **eski
hâlin somut bir örnekte çuvalladığını** göstermektir.

Çalıştırma: ``python3 -m pytest docs/kaynak/test_tashih_kuantum.py -q``
"""

from __future__ import annotations

import math
import os
import re
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

from docs.kaynak import tashih_kuantum as TK          # noqa: E402
from docs.kaynak import tex_denetle as TD             # noqa: E402

KAYNAK = os.path.dirname(os.path.abspath(__file__))
TASHIHLI = os.path.join(KAYNAK, "tashihli")


# ══════════════════════════════════════════════════════════════════════
#  Cetvelin kendi tutarlılığı
# ══════════════════════════════════════════════════════════════════════

def test_her_tashih_tam_bir_kere_esliyor():
    """``uygula`` zaten sınıyor; burada yeniden koşup teyit ediyoruz."""
    uygulanan = TK.uygula()
    assert sum(len(v) for v in uygulanan.values()) == len(TK.T)


def test_tashih_numaralari_tekil_ve_sirali():
    nolar = [t.no for t in TK.T]
    assert nolar == sorted(nolar)
    assert len(set(nolar)) == len(nolar)


def test_cetvel_kayittan_uretiliyor():
    c = TK.cetvel()
    for t in TK.T:
        assert ("K%d — %s" % (t.no, t.baslik)) in c
        assert t.sebep[:40] in c


def test_saglamasi_yazili_testler_gercekten_var():
    """Cetvelde adı geçen her test bu dosyada bulunmalı."""
        # Aksi hâlde cetvel, olmayan bir sağlamaya işaret eder.
    burada = {ad for ad in globals() if ad.startswith("test_")}
    for t in TK.T:
        if t.saglama:
            assert t.saglama in burada, (t.no, t.saglama)


# ══════════════════════════════════════════════════════════════════════
#  K1-K6: derleme
# ══════════════════════════════════════════════════════════════════════

def test_kuantum_kapi_derleniyor():
    """Kaynakta 7 yapısal bulgu var; tashihli nüshada sıfır olmalı."""
    ham = TD.dosya_denetle(os.path.join(KAYNAK, TK.KAPI))
    assert len(ham) > 0, "kaynak zaten temizse tashih gereksizdi"
    duzgun = TD.dosya_denetle(
        os.path.join(TASHIHLI, "kuantum_kapi_kulliyati_tashihli.tex"))
    assert duzgun == [], duzgun
    # Bozuk kapanışların hiçbiri kalmamalı:
    metin = open(os.path.join(TASHIHLI,
                              "kuantum_kapi_kulliyati_tashihli.tex"),
                 encoding="utf-8").read()
    assert '\\end{equation">' not in metin
    assert '\\end{align">' not in metin
    assert "\\##" not in metin


# ══════════════════════════════════════════════════════════════════════
#  K7: U_1 ile R_z
# ══════════════════════════════════════════════════════════════════════

def _Rz(t):
    return np.diag([np.exp(-1j * t / 2), np.exp(1j * t / 2)])


def _U1(t):
    return np.diag([1.0 + 0j, np.exp(1j * t)])


def _kontrollu(U):
    """``|1⟩⟨1| ⊗ U + |0⟩⟨0| ⊗ I`` — kontrollü kapı."""
    C = np.eye(4, dtype=complex)
    C[2:, 2:] = U
    return C


def test_U1_ile_Rz_kuresel_faz_kadar_farkli():
    """Tek başına ayırt edilemez; KONTROL altında ayırt edilebilir."""
    for t in (0.3, 1.0, 2.5, np.pi):
        U1, Rz = _U1(t), _Rz(t)
        # 1) Eşit DEĞİLLER:
        assert not np.allclose(U1, Rz), t
        # 2) Ama yalnız küresel faz kadar farklılar:
        assert np.allclose(U1, np.exp(1j * t / 2) * Rz), t
        # 3) Tek kübitte hiçbir ölçüm ayırt edemez (aynı yoğunluk):
        psi = np.array([0.6, 0.8j])
        psi /= np.linalg.norm(psi)
        r1, r2 = U1 @ psi, Rz @ psi
        assert np.allclose(np.outer(r1, r1.conj()),
                           np.outer(r2, r2.conj())), t
        # 4) KONTROL altında fark ÖLÇÜLEBİLİR hâle gelir:
        C1, C2 = _kontrollu(U1), _kontrollu(Rz)
        assert not np.allclose(C1, C2), t
        # ve aralarında küresel faz ilişkisi de KALMAZ:
        oran = C1[np.abs(C2) > 1e-12] / C2[np.abs(C2) > 1e-12]
        assert not np.allclose(oran, oran[0]), (
            t, "kontrollü hâlde hâlâ küresel faz — kıyas boş")


# ══════════════════════════════════════════════════════════════════════
#  K8: QFT köşegen değildir
# ══════════════════════════════════════════════════════════════════════

def _qft(n):
    N = 2 ** n
    j, k = np.meshgrid(np.arange(N), np.arange(N), indexing="ij")
    return np.exp(2j * np.pi * j * k / N) / np.sqrt(N)


def test_qft_kosegen_degil():
    """Kaynaktaki çarpım formu köşegen bir operatör yazıyor; QFT değil."""
    for n in (1, 2, 3):
        Q = _qft(n)
        # üniter:
        assert np.allclose(Q.conj().T @ Q, np.eye(2 ** n), atol=1e-12)
        # köşegen DEĞİL — köşegen dışı büyüklük kayda değer:
        kosegen_disi = Q - np.diag(np.diag(Q))
        assert np.max(np.abs(kosegen_disi)) > 0.1, n
        # Köşegen bir operatör |0…0⟩'ı süperpozisyona götüremez:
        e0 = np.zeros(2 ** n, dtype=complex)
        e0[0] = 1.0
        cikti = Q @ e0
        assert np.count_nonzero(np.abs(cikti) > 1e-12) == 2 ** n, n


# ══════════════════════════════════════════════════════════════════════
#  K9: Fubini–Study metriği
# ══════════════════════════════════════════════════════════════════════

def _kubit_hali(teta, fi):
    return np.array([np.cos(teta / 2),
                     np.sin(teta / 2) * np.exp(1j * fi)])


def test_fubini_study_metrigi():
    """İzdüşümsüz hâl (i) karmaşık, (ii) gauge'a duyarlı."""
    teta, fi = 0.9, 0.4
    h = 1e-6

    def d(k):
        p = [teta, fi]
        p[k] += h
        arti = _kubit_hali(*p)
        p[k] -= 2 * h
        eksi = _kubit_hali(*p)
        return (arti - eksi) / (2 * h)

    dmu, dnu = d(0), d(1)
    psi = _kubit_hali(teta, fi)

    ham = np.vdot(dmu, dnu)                      # kaynaktaki hâl
    # (i) karmaşık — simetrik reel metrik olamaz:
    assert abs(ham.imag) > 1e-6, "sağlama boş: sanal kısım zaten sıfır"

    # (ii) gauge'a duyarlı: |ψ⟩ → e^{iα(θ)}|ψ⟩ altında değişir.
    def gauge_hali(t, f):
        return np.exp(1j * 2.0 * t) * _kubit_hali(t, f)

    def dg(k):
        p = [teta, fi]
        p[k] += h
        a = gauge_hali(*p)
        p[k] -= 2 * h
        e = gauge_hali(*p)
        return (a - e) / (2 * h)

    ham_gauge = np.vdot(dg(0), dg(1))
    assert abs(ham_gauge - ham) > 1e-4, "gauge duyarlılığı görünmedi"

    # Tashihli hâl: reel VE gauge'dan bağımsız.
    def fs(dm, dn, p):
        return (np.vdot(dm, dn) - np.vdot(dm, p) * np.vdot(p, dn)).real

    fs_ham = fs(dmu, dnu, psi)
    fs_gauge = fs(dg(0), dg(1), gauge_hali(teta, fi))
    assert abs(fs_ham - fs_gauge) < 1e-5, (fs_ham, fs_gauge)


# ══════════════════════════════════════════════════════════════════════
#  K10: Tr(ρ²) ≤ 1 vakum denetim
# ══════════════════════════════════════════════════════════════════════

def _rastgele_yogunluk(d, rng):
    A = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
    R = A @ A.conj().T
    return R / np.trace(R).real


def test_iz_kare_olcutu_vakum_degil():
    """``Tr(ρ²) ≤ 1`` hiçbir yoğunluk matrisini elemez — o yüzden vakum."""
    rng = np.random.default_rng(0)
    hicbiri_elenmedi = True
    for _ in range(500):
        d = int(rng.integers(2, 6))
        rho = _rastgele_yogunluk(d, rng)
        assert np.trace(rho @ rho).real <= 1.0 + 1e-9
    assert hicbiri_elenmedi

    # Tashihli ölçüt AYIRT EDİYOR: saf hâl 1, karışık hâl < 1.
    saf = np.zeros((3, 3), dtype=complex)
    saf[0, 0] = 1.0
    karisik = np.eye(3, dtype=complex) / 3
    assert np.trace(saf @ saf).real == pytest.approx(1.0)
    assert np.trace(karisik @ karisik).real == pytest.approx(1 / 3)

    # Ve yoğunluk matrisi OLMAYAN bir şeyi eski ölçüt yakalamaz,
    # yenisi yakalar:
    # İzi 1, negatif özdeğerli, ve Tr(ρ²) = 0.76 ≤ 1:
    sahte = np.diag([0.6, 0.6, -0.2]).astype(complex)
    assert np.trace(sahte).real == pytest.approx(1.0)
    assert np.trace(sahte @ sahte).real == pytest.approx(0.76)
    assert np.trace(sahte @ sahte).real <= 1.0 + 1e-9   # eski ölçüt: GEÇİYOR
    assert np.min(np.linalg.eigvalsh(sahte)) < 0        # yeni ölçüt: ELİYOR


# ══════════════════════════════════════════════════════════════════════
#  K11: karşılıklı bilgi ≠ dolaşıklık
# ══════════════════════════════════════════════════════════════════════

def _von_neumann(rho):
    ozd = np.linalg.eigvalsh(rho)
    ozd = ozd[ozd > 1e-12]
    return float(-np.sum(ozd * np.log2(ozd)))


def _kismi_iz(rho, d1, d2, hangi):
    R = rho.reshape(d1, d2, d1, d2)
    return np.einsum("ikjk->ij", R) if hangi == 0 else np.einsum("kikj->ij", R)


def test_karsilikli_bilgi_dolasiklik_degil():
    """Ayrılabilir (dolaşıksız) bir hâlde karşılıklı bilgi > 0."""
    # Klasik bağıntılı ama AYRILABİLİR hâl: ½(|00⟩⟨00| + |11⟩⟨11|)
    r00 = np.zeros((4, 4), dtype=complex); r00[0, 0] = 1
    r11 = np.zeros((4, 4), dtype=complex); r11[3, 3] = 1
    ayrilabilir = 0.5 * (r00 + r11)

    ra = _kismi_iz(ayrilabilir, 2, 2, 0)
    rb = _kismi_iz(ayrilabilir, 2, 2, 1)
    I = _von_neumann(ra) + _von_neumann(rb) - _von_neumann(ayrilabilir)
    assert I == pytest.approx(1.0, abs=1e-9), I
    # Bu hâl AYRILABİLİRDİR (iki çarpım hâlin dışbükey birleşimi),
    # yani dolaşıklığı SIFIRDIR — ama "ölçü" 1 bit diyor.

    # Kıyas: gerçekten dolaşık Bell hâli
    bell = np.zeros(4, dtype=complex)
    bell[0] = bell[3] = 1 / np.sqrt(2)
    rbell = np.outer(bell, bell.conj())
    Ib = (_von_neumann(_kismi_iz(rbell, 2, 2, 0))
          + _von_neumann(_kismi_iz(rbell, 2, 2, 1))
          - _von_neumann(rbell))
    assert Ib == pytest.approx(2.0, abs=1e-9)

    # Tashihli ölçüt (saf hâlde dolaşıklık entropisi) ikisini ayırır:
    assert _von_neumann(_kismi_iz(rbell, 2, 2, 0)) == pytest.approx(1.0)
    # Ayrılabilir hâl saf değil; entropi ölçüsü oraya uygulanmaz —
    # asıl mesele de bu: tek bir sayı iki soruyu birden cevaplayamaz.
    assert _von_neumann(ayrilabilir) == pytest.approx(1.0)


# ══════════════════════════════════════════════════════════════════════
#  K12: kıyas tabanı
# ══════════════════════════════════════════════════════════════════════

def test_qft_ile_fft_kiyas_tabani():
    """``N`` nokta için klasik maliyet ``N log N``; ``2^N`` değil."""
    for n in (10, 20, 30):
        N = 2 ** n
        log2_fft = math.log2(N) + math.log2(math.log2(N))   # log2(N log N)
        log2_yanlis = float(N)                              # log2(2^N) = N
        log2_qft = 2 * math.log2(n)                         # log2(n²)
        # Yanlış taban kazanımı astronomik derecede şişiriyor:
        assert log2_yanlis - log2_fft > N / 2, n
        # Hakiki kazanım kayda değer ama sonlu:
        assert 3 < log2_fft - log2_qft < 30, (n, log2_fft - log2_qft)


# ══════════════════════════════════════════════════════════════════════
#  K13: koherens normalizasyonu
# ══════════════════════════════════════════════════════════════════════

def test_koherens_normalizasyonu():
    """``|Tr U| = 1`` şartı, birim operatörü ``d>1`` iken ELER."""
    rng = np.random.default_rng(3)
    for d in (2, 4, 8):
        birim = np.eye(d, dtype=complex)
        # Eski ölçüt: |Tr I| = d ≠ 1 → "tam ittisal DEĞİL" der. Yanlış.
        assert abs(np.trace(birim)) == pytest.approx(d)
        assert bool(abs(np.trace(birim)) == pytest.approx(1.0)) == (d == 1)
        # Tashihli ölçüt: |Tr I|/d = 1 → doğru cevap.
        assert abs(np.trace(birim)) / d == pytest.approx(1.0)
        # Ve rastgele bir üniter için ölçüt 1'in ALTINDA kalmalı:
        A = rng.normal(size=(d, d)) + 1j * rng.normal(size=(d, d))
        Q, _ = np.linalg.qr(A)
        assert abs(np.trace(Q)) / d < 0.999
        # Faz katı da tam ittisal saymalı:
        assert abs(np.trace(np.exp(0.7j) * birim)) / d == pytest.approx(1.0)


# ══════════════════════════════════════════════════════════════════════
#  K14: hLevel sırası
# ══════════════════════════════════════════════════════════════════════

def test_hlevel_sirasi():
    """hLevel 0 = büzülebilir, 1 = önerme, 2 = küme (Voevodsky)."""
    from omega_kategori_nbe import cekirdek as C
    from omega_kategori_nbe import kutuphane as L
    from omega_kategori_nbe import sozdizim as S
    Z = S.Tamsayi()                        # kapalı, somut bir tip
    a, b, c = (C.nf(L.iz_butun(Z)), C.nf(L.iz_onerme(Z)),
               C.nf(L.iz_kume(Z)))
    # Üç mertebe ÜÇ AYRI terim; aynı olsalardı hLevel ayrımı kalmazdı.
    assert not C.esdeger_mi(L.iz_butun(Z), L.iz_onerme(Z))
    assert not C.esdeger_mi(L.iz_onerme(Z), L.iz_kume(Z))
    assert not C.esdeger_mi(L.iz_butun(Z), L.iz_kume(Z))
    assert a is not None and b is not None and c is not None


# ══════════════════════════════════════════════════════════════════════
#  K15, K16: B-spline
# ══════════════════════════════════════════════════════════════════════

def test_bspline_temel_sayisi():
    """``G`` aralık, ``p`` derece → ``G+p`` temel. ``G`` ile kesilirse bozulur."""
    from token_uzaylari.kan_spline import bspline_temeli, dugum_dizisi
    for G, p in ((5, 3), (10, 2), (8, 4)):
        d = dugum_dizisi(G, p)
        t = np.linspace(-1, 1, 401)
        B = bspline_temeli(t, d, p)
        assert B.shape[1] == G + p, (G, p, B.shape)
        # Tam temelde birliğin bölünmesi:
        assert np.max(np.abs(B.sum(axis=1) - 1.0)) < 1e-12
        # Kaynaktaki gibi ilk G ile kesilirse SAĞ UÇTA çöker:
        kesik = B[:, :G].sum(axis=1)
        assert np.min(kesik) < 0.5, (G, p, np.min(kesik))


def test_cox_de_boor_sifir_payda():
    """Tekrarlı düğümde payda sıfırlanır; terim DÜŞMELİ, nan olmamalı."""
    from token_uzaylari.kan_spline import bspline_temeli
    # Uçlarda tekrarlı (clamped) düğüm dizisi:
    d = np.array([0.0, 0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0, 1.0])
    t = np.linspace(0.0, 1.0, 101)
    B = bspline_temeli(t, d, 3)
    assert np.all(np.isfinite(B)), "sıfır payda nan üretti"
    assert np.max(np.abs(B.sum(axis=1) - 1.0)) < 1e-12
    assert np.min(B) > -1e-12


# ══════════════════════════════════════════════════════════════════════
#  K18: bağıl kesme eşiği
# ══════════════════════════════════════════════════════════════════════

def test_kesme_kipi_bagil_esikle():
    """Mutlak eşik ölçekle kayar; bağıl eşik kaymaz."""
    from token_uzaylari.fno import kesme_kipi, spektral_enerji
    x = np.linspace(0, 1, 256, endpoint=False)
    # Kademeli spektrum: kesme yerinin ölçekle kayması burada görünür.
    v = sum(np.cos(2 * np.pi * k * x) / k ** 2
            for k in range(1, 40))[:, None]

    # Tashihli (bağıl) ölçüt: genlik değişse de aynı k.
    k1 = kesme_kipi(v, 1e-6)
    k2 = kesme_kipi(1000.0 * v, 1e-6)
    assert k1 == k2, (k1, k2)

    # Kaynaktaki (mutlak) ölçüt ölçekle kayar:
    def mutlak_kesme(vv, eps):
        E = spektral_enerji(vv)
        kuyruk = float(E.sum())
        for k in range(E.size):
            kuyruk -= float(E[k])
            if kuyruk < eps:
                return k
        return E.size - 1

    m1 = mutlak_kesme(v, 1.0)
    m2 = mutlak_kesme(1000.0 * v, 1.0)
    assert m1 != m2, ("sağlama boş: mutlak eşik de kaymadı", m1, m2)
    assert m2 > m1 + 10, (m1, m2)   # 17 → 39: kesme yeri tamamen kaydı


# ══════════════════════════════════════════════════════════════════════
#  K22: serbest enerji alt sınırı
# ══════════════════════════════════════════════════════════════════════

def test_serbest_enerji_alt_siniri():
    """Sürekli yoğunlukta ``F ≥ 0`` BOZULUR; ``F ≥ −ln p(X)`` bozulmaz."""
    from fitrat.serbest_enerji import gauss_serbest_enerji
    # Dar bir gözlem gürültüsü ⟹ p(x) > 1 ⟹ −ln p(x) < 0
    g = gauss_serbest_enerji(x=0.0, m_q=0.0, s_q=0.02,
                             m_p=0.0, s_p=0.05, s_g=0.02)
    assert g["sürpriz"] < 0.0, ("p(x) ≤ 1 çıktı, sağlama boş", g)
    # Doğru sınır her hâlde geçerli:
    assert g["boşluk"] >= -1e-9
    # Ve F'nin kendisi NEGATİF — yani ``F ≥ 0`` iddiası burada yanlış:
    assert g["F"] < 0.0, g

    # Ayrık hâlde ``F ≥ 0`` doğrudur (p ≤ 1); yani iddia şartlıdır.
    from fitrat.serbest_enerji import AyrikModel, serbest_enerji, ardil
    m = AyrikModel(np.array([0.2, 0.5, 0.3]),
                   np.array([[0.7, 0.2, 0.1], [0.1, 0.6, 0.3],
                             [0.3, 0.3, 0.4]]))
    assert serbest_enerji(m, ardil(m, 1), 1) > 0.0


# ══════════════════════════════════════════════════════════════════════
#  K23: eyer noktası ölçütü
# ══════════════════════════════════════════════════════════════════════

def test_eyer_noktasi_olcutu():
    """``λ_max > 0`` yerel ASGARÎDE de doğrudur — eyer ayırt edilemez."""
    asgari = np.diag([1.0, 2.0, 3.0])       # yerel asgarî
    eyer = np.diag([-1.0, 2.0, 3.0])        # eyer
    azami = np.diag([-1.0, -2.0, -3.0])     # yerel azamî

    for H in (asgari, eyer):
        assert np.max(np.linalg.eigvalsh(H)) > 0     # eski ölçüt: ikisi de
    # Yani eski ölçüt asgarîyi eyer sanıyor.

    def eyer_mi(H):
        oz = np.linalg.eigvalsh(H)
        return bool(oz.min() < 0 < oz.max())

    assert eyer_mi(asgari) is False
    assert eyer_mi(eyer) is True
    assert eyer_mi(azami) is False

    # Kaçış yönü λ_min'in öz vektörü olmalı, λ_max'ınki değil:
    oz, V = np.linalg.eigh(eyer)
    kacis = V[:, int(np.argmin(oz))]
    f = lambda z: float(z @ eyer @ z)
    assert f(1e-3 * kacis) < 0        # bu yönde ALÇALIYOR
    yukselen = V[:, int(np.argmax(oz))]
    assert f(1e-3 * yukselen) > 0     # λ_max yönünde yükseliyor


# ══════════════════════════════════════════════════════════════════════
#  K24: faz çekirdeği PSD değil
# ══════════════════════════════════════════════════════════════════════

def test_faz_cekirdegi_psd_degil():
    """``exp(i S(x,y))`` Gram dizeyi negatif özdeğer taşır."""
    rng = np.random.default_rng(1)
    n = 12
    x = rng.uniform(-3, 3, n)
    S = np.add.outer(x, 2.0 * x)          # simetrik olmayan bir eylem
    K = np.exp(1j * S)
    # (i) Hermitesel değil:
    assert np.max(np.abs(K - K.conj().T)) > 1e-6
    # (ii) Hermitesel kısmı bile PSD değil:
    H = 0.5 * (K + K.conj().T)
    assert np.min(np.linalg.eigvalsh(H)) < -1e-6, np.linalg.eigvalsh(H)

    # Tashihli inşa (öznitelik haritasının iç çarpımı) PSD'dir:
    yollar = rng.uniform(-2, 2, (40, 1))
    Phi = np.exp(1j * (yollar * x[None, :]))       # (yol, nokta)
    K2 = Phi.conj().T @ Phi / yollar.shape[0]
    assert np.max(np.abs(K2 - K2.conj().T)) < 1e-12
    assert np.min(np.linalg.eigvalsh(K2)) > -1e-10


# ══════════════════════════════════════════════════════════════════════
#  K25: Tikhonov çekirdeği yok eder
# ══════════════════════════════════════════════════════════════════════

def test_tikhonov_cekirdegi_yok_eder():
    """``L+εI``'nin çekirdeği BOŞTUR; β₀ oradan okunamaz."""
    from nefs.idrak import normalize_laplasyen
    # İki ayrık üçgen: β₀ = 2
    A = np.zeros((6, 6))
    for i, j in ((0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)):
        A[i, j] = A[j, i] = 1.0
    L = normalize_laplasyen(A)
    oz = np.linalg.eigvalsh(L)
    beta0 = int(np.sum(np.abs(oz) < 1e-9))
    assert beta0 == 2, oz

    eps = 1e-3
    L_eps = L + eps * np.eye(6)
    oz_eps = np.linalg.eigvalsh(L_eps)
    # Kaynaktaki ölçüt: dim ker(L_eps) — SIFIR çıkıyor, β₀=2 değil.
    assert int(np.sum(np.abs(oz_eps) < 1e-9)) == 0
    # Tashihli ölçüt: ε eşiğinin altındaki özdeğerleri say.
    assert int(np.sum(oz_eps <= eps + 1e-9)) == 2


# ══════════════════════════════════════════════════════════════════════
#  K26: Grassmann asal açıları
# ══════════════════════════════════════════════════════════════════════

def test_grassmann_asal_acilari():
    """``arccos σ`` ile ``arcsin σ`` farklı açılar verir."""
    rng = np.random.default_rng(2)
    U1, _ = np.linalg.qr(rng.normal(size=(6, 2)))
    U2, _ = np.linalg.qr(rng.normal(size=(6, 2)))
    s = np.linalg.svd(U1.T @ U2, compute_uv=False)
    s = np.clip(s, 0.0, 1.0)
    dogru = np.arccos(s)
    yanlis = np.arcsin(s)
    assert not np.allclose(dogru, yanlis)
    assert np.allclose(dogru + yanlis, np.pi / 2)

    # Doğru açılar geodezik mesafeyi verir; aynı uzayda mesafe SIFIR:
    s_ayni = np.linalg.svd(U1.T @ U1, compute_uv=False)
    assert np.linalg.norm(np.arccos(np.clip(s_ayni, 0, 1))) < 1e-7
    # arcsin ile aynı uzayda mesafe π/2·√k çıkar — anlamsız:
    assert np.linalg.norm(np.arcsin(np.clip(s_ayni, 0, 1))) > 2.0


# ══════════════════════════════════════════════════════════════════════
#  K27: Morse bağıntısı
# ══════════════════════════════════════════════════════════════════════

def test_morse_bagintisi():
    """Yükseklik fonksiyonlu torus: Σ(−1)^k M_k = χ, tam eşitlik."""
    # Torus: kritik noktalar 1 asgarî, 2 eyer, 1 azamî; χ(T²)=0.
    M = [1, 2, 1]
    beta = [1, 2, 1]
    chi = sum((-1) ** k * b for k, b in enumerate(beta))
    assert chi == 0
    assert sum((-1) ** k * m for k, m in enumerate(M)) == chi   # EŞİTLİK
    assert all(m >= b for m, b in zip(M, beta))                 # zayıf eşitsizlik

    # Kaynaktaki ``>=`` ifadesi mükemmel olmayan bir Morse fonksiyonunda
    # da "sağlanıyor" görünür, oysa eşitlik BOZULMAZ:
    M2 = [1, 3, 2]     # ek bir eyer-azamî çifti (iptal olan)
    assert sum((-1) ** k * m for k, m in enumerate(M2)) == chi
    # ...yani eşitlik gerçekten her Morse fonksiyonunda tutuyor.
    assert sum((-1) ** k * m for k, m in enumerate(M2)) >= chi  # ≥ de tutuyor
    # ama ≥ tek başına M=[5,0,0] gibi imkânsız bir dizilimi de geçirir:
    sahte = [5, 0, 0]
    assert sum((-1) ** k * m for k, m in enumerate(sahte)) >= chi
    assert sum((-1) ** k * m for k, m in enumerate(sahte)) != chi


# ══════════════════════════════════════════════════════════════════════
#  K28: simetrikleştirme idempotent yapmaz
# ══════════════════════════════════════════════════════════════════════

def test_simetriklestirme_idempotent_yapmaz():
    rng = np.random.default_rng(4)
    U, _ = np.linalg.qr(rng.normal(size=(5, 2)))
    P = U @ U.T
    bozuk = P + 0.05 * rng.normal(size=(5, 5))

    sim = 0.5 * (bozuk + bozuk.T)
    idem_hatasi = np.linalg.norm(sim @ sim - sim)
    assert idem_hatasi > 1e-3, ("simetrikleştirme tesadüfen düzeltti",
                                idem_hatasi)

    # Tashihli onarım: kutup ayrışımıyla tabanı yeniden dikle.
    Uu, _, Vt = np.linalg.svd(bozuk @ U, full_matrices=False)
    U_ortho = Uu @ Vt
    P_duz = U_ortho @ U_ortho.T
    assert np.linalg.norm(P_duz @ P_duz - P_duz) < 1e-12
    assert np.linalg.norm(P_duz - P_duz.T) < 1e-12


# ══════════════════════════════════════════════════════════════════════
#  K29: hcomp isSet ile indirgenmez
# ══════════════════════════════════════════════════════════════════════

def test_hcomp_isset_ile_indirgenmez():
    """``isSet`` tanımsal indirgeme vermez — değerlendirici nötr bırakır."""
    kok = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    # İddia: değerlendirici, "tip bir kümedir" bilgisine dayanarak
    # hcomp'u u₀'a İNDİRGEMİYOR. Sağlaması, indirgeme kurallarının
    # yazılı olduğu yerde böyle bir kuralın BULUNMAMASIDIR.
    for dosya in ("denklik.py", "cekirdek.py"):
        kaynak = open(os.path.join(kok, "omega_kategori_nbe", dosya),
                      encoding="utf-8").read()
        assert "isSet" not in kaynak and "iz_kume" not in kaynak, (
            dosya, "isSet'e dayalı bir indirgeme kuralı bulundu — "
                   "tashihin gerekçesi yeniden tartılmalı")
    # Ve hcomp'un fiilen indirgendiği tek hâl, bir yüzün ⊤ olmasıdır;
    # bu kural tipin küme olup olmamasına bakmıyor:
    denklik = open(os.path.join(kok, "omega_kategori_nbe", "denklik.py"),
                   encoding="utf-8").read()
    assert "ÇÖKER" in denklik or "çöker" in denklik


# ══════════════════════════════════════════════════════════════════════
#  K30: quadrature ağırlığı
# ══════════════════════════════════════════════════════════════════════

def test_quadrature_agirligi_alana_uygulanmaz():
    """Çarpanı alana uygulamak, alanı çözünürlüğe bağımlı kılar."""
    f = lambda z: np.sin(2 * np.pi * z)
    normlar_dogru, degerler_yanlis = [], []
    for N in (64, 256, 1024, 4096):
        x = np.linspace(0, 1, N, endpoint=False)
        v = f(x)
        # Tashihli: ağırlık NORMDA
        normlar_dogru.append(np.sqrt((1.0 / N) * np.sum(v ** 2)))
        # Kaynaktaki: ağırlık ALANDA
        v_olcekli = v * np.sqrt(1.0 / N)
        degerler_yanlis.append(float(np.max(np.abs(v_olcekli))))
    # Doğru norm çözünürlükten bağımsız:
    assert max(normlar_dogru) - min(normlar_dogru) < 1e-6, normlar_dogru
    # Yanlış ölçekleme alanın genliğini çözünürlükle çökertiyor:
    assert degerler_yanlis[0] / degerler_yanlis[-1] > 7.0, degerler_yanlis


# ══════════════════════════════════════════════════════════════════════
#  K31: sıfır kovaryans ≠ bağımsızlık
# ══════════════════════════════════════════════════════════════════════

def test_sifir_kovaryans_bagimsizlik_degil():
    """``Y = X²`` ile ``Cov = 0`` ama ``Y`` tamamen ``X``'e bağlı."""
    rng = np.random.default_rng(7)
    X = rng.uniform(-1, 1, 200_000)
    Y = X ** 2
    kov = float(np.cov(X, Y)[0, 1])
    assert abs(kov) < 5e-3, kov          # kovaryans ≈ 0
    # Ama bağımlılık tam: X bilinince Y kesin belli.
    assert np.allclose(Y, X ** 2)
    # Ölçülebilir bir bağımlılık şahidi: |X| ile Y arasında bağıntı 1.
    assert abs(float(np.corrcoef(np.abs(X), Y)[0, 1])) > 0.95


# ══════════════════════════════════════════════════════════════════════
#  K32: Kahan hata sınırı
# ══════════════════════════════════════════════════════════════════════

def _kahan(xs):
    s = 0.0
    c = 0.0
    for x in xs:
        y = x - c
        t = s + y
        c = (t - s) - y
        s = t
    return s


def test_kahan_hata_siniri_N_den_bagimsiz():
    """Kahan hatası ``N`` ile büyümüyor; naif toplamanınki büyüyor."""
    from fractions import Fraction
    hatalar_kahan, hatalar_naif = [], []
    for N in (1_000, 10_000, 100_000):
        rng = np.random.default_rng(N)
        xs = rng.normal(0, 1, N) * 10.0 ** rng.integers(-6, 6, N)
        tam = float(sum(Fraction(float(x)) for x in xs))
        olcek = float(np.sum(np.abs(xs)))
        hatalar_kahan.append(abs(_kahan(xs) - tam) / olcek)
        naif = 0.0
        for x in xs:
            naif += float(x)
        hatalar_naif.append(abs(naif - tam) / olcek)

    eps = np.finfo(float).eps
    # Kahan: bağıl hata birkaç eps mertebesinde, N ile büyümüyor.
    for h in hatalar_kahan:
        assert h <= 4 * eps, (h, h / eps)
    # Kaynaktaki N·eps sınırı Kahan için fena hâlde gevşek:
    for N, h in zip((1_000, 10_000, 100_000), hatalar_kahan):
        assert h < N * eps / 100, (N, h)
    # Naif toplama gerçekten daha kötü:
    assert max(hatalar_naif) > max(hatalar_kahan)


# ══════════════════════════════════════════════════════════════════════
#  K34: pencereden sonra Parseval
# ══════════════════════════════════════════════════════════════════════

def test_pencereden_sonra_parseval():
    """Pencere enerjiyi değiştirir; ham eşitlik bozulur."""
    N = 512
    x = np.linspace(0, 1, N, endpoint=False)
    v = np.sin(6 * np.pi * x) + 0.4 * np.cos(20 * np.pi * x)

    def parseval_farki(sinyal):
        V = np.fft.fft(sinyal)
        return abs(np.sum(sinyal ** 2) - np.sum(np.abs(V) ** 2) / N)

    # Penceresiz: Parseval tam.
    assert parseval_farki(v) < 1e-9

    # Kaiser penceresiyle: sinyalin ENERJİSİ değişiyor.
    w = np.kaiser(N, 8.0)
    vw = v * w
    assert abs(np.sum(vw ** 2) - np.sum(v ** 2)) > 0.1 * np.sum(v ** 2)
    # Parseval pencereli sinyalin KENDİ enerjisiyle hâlâ tutuyor:
    assert parseval_farki(vw) < 1e-9
    # ...ama ham katsayı toplamıyla tutmuyor — iddia edilen buydu.
    V = np.fft.fft(v)
    assert abs(np.sum(np.abs(np.fft.fft(vw)) ** 2) / N
               - np.sum(np.abs(V) ** 2) / N) > 0.1 * np.sum(v ** 2)


# ══════════════════════════════════════════════════════════════════════
#  K36-K38: kodlama sırasında ölçümle çıkan eksikler
# ══════════════════════════════════════════════════════════════════════

def test_iz_olcutu_yanlis_log_u_yakalamiyor():
    """K36: ``Tr(Exp(Log)) = Tr(G₂)`` ölçütü yanlış Log'u geçirir."""
    from ogrenme import grassmann as gr

    Y1, Y2 = gr._rastgele(8, 3, 0), gr._rastgele(8, 3, 1)
    kotu = gr.exp_haritasi(Y1, gr.log_haritasi_arcsin(Y1, Y2))
    # Eski ölçüt: iz eşitliği — yanlış Log'da da SAĞLANIYOR
    assert abs(float(np.trace(gr.izdusum(kotu)))
               - float(np.trace(gr.izdusum(Y2)))) < 1e-12
    # Yeni ölçüt: izdüşüm farkı — yanlış Log'u YAKALIYOR
    assert gr.alt_uzay_hatasi(kotu, Y2) > 0.5
    # ve doğru Log'da sıfır
    assert gr.gidis_donus_hatasi(Y1, Y2, gr.log_haritasi) < 1e-12


def test_dogrusal_olmayan_gurultude_tekil():
    """K37: abduction toplamsal gürültüde tekil DEĞİL, u²'de tekil."""
    from fitrat import karsi_olgusal as ko
    from fitrat.ayrisma import Cizge

    g = Cizge(("A", "B"), (("A", "B"),))
    toplamsal = ko.YapisalModel(g, {"A": lambda pa, u: u,
                                    "B": lambda pa, u: pa["A"] + u})
    kareli = ko.YapisalModel(g, {"A": lambda pa, u: u,
                                 "B": lambda pa, u: pa["A"] + u * u})
    goz = {"A": 1.0, "B": 2.0}
    assert not ko.abduction_tekil_mi(toplamsal, goz)["tekil_mi"]
    assert ko.abduction_degismezi(toplamsal, goz)["hata"] < 1e-12
    t = ko.abduction_tekil_mi(kareli, goz)
    assert t["tekil_mi"] and t["tekil_düğümler"] == ["B"]
    # B < A: u² = negatif — kök yok, hüküm verilmiyor
    assert ko.karsiolgusal(kareli, {"A": 1.0, "B": 0.5},
                           {"A": 3.0})["geçerli"] is False


def test_duzeltmesiz_tegetin_locustan_kaydigi():
    """K38: Formül 48.3 tek başına yetmiyor — kayma birikiyor."""
    import math

    from fitrat import karsi_olgusal as ko

    def phi(x):
        return np.array([float(x @ x) - 1.0])

    def jac(x):
        return 2.0 * x[None, :]

    def grad(x):
        return np.array([1.0, 0.0])

    x0 = np.array([math.cos(0.4), math.sin(0.4)])
    for adim in (0.05, 0.2, 0.5):
        a = ko.locus_uzerinde_yurut(phi, jac, grad, x0, adim=adim,
                                    duzelt=False)
        b = ko.locus_uzerinde_yurut(phi, jac, grad, x0, adim=adim,
                                    duzelt=True)
        assert a["azamî_ihlal"] > 1e-2
        assert b["azamî_ihlal"] < a["azamî_ihlal"] / 50
