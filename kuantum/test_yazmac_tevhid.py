"""KÜME 1 TEVHİDİNİN ŞAHİTLERİ -- altı dosya tek çipte, ölçüyle.

Zabıtın (KÜME 1, IV. Terkip Harekât Plânı, 3. adım) istediği sınama
budur: *"Birleşen tekil çipin kendi kendini sınayan doğrulama
testlerini çalıştırıp; norm korunumunu, O(log N) ağaç mesafesini,
HDTF katlama hızını, Gray-kod komşuluğunu ve kararlı SVD geçişini
ölçeceğiz."*

**Bu dosyanın vazifesi tevhidi ÖVMEK değil, çürümesini ENGELLEMEKtir.**
Taşınan altı kabiliyetin her biri burada kendi ölçütüyle sınanır; biri
bozulursa kırmızı yanar. Ölçütler iddia değil, koşan sayıdır.

Taşınan dosyalar (hepsi ``git rm`` edildi, gövdeleri
``kuantum/yazmac.py``dedir):

    kuantum/katlama.py   → HDTF hiyerarşik ikili ağaç katlaması
    kuantum/ic_bag.py    → sanal bağın QTT faktörizasyonu
    kuantum/ptr.py       → polinomial tensör halkası (YÜZEY temsili)
    nefs/agac.py         → iki boyutlu ağaç tensör ağı (TTN)
    nefs/ucagac.py       → üç ağaç + boyut ihtimal uzayında
    nefs/ihtimal.py      → ızgara ihtimal uzayı
"""
from __future__ import annotations

import numpy as np
import pytest

from kuantum.yazmac import (AgacAyar, AgacYazmaci, IhtimalAyar,
                            IhtimalYazmaci, PolinomHalka, TensorHalka,
                            Yazmac, acik_parametre, hadamard,
                            hiyerarsik_ikili_agac_katlama,
                            iki_kademeli_donme, kubit_hesabi,
                            qtt_cekirdek_ac, qtt_cekirdek_ayristir,
                            qtt_parametre)


# ══════════════════════════════════════════════════════════════════════
#  1. HDTF -- katlama ``Yazmac``a bağlı mı, norm korunuyor mu
# ══════════════════════════════════════════════════════════════════════

def test_hdtf_katlamasi_yazmaca_baglaniyor_ve_norm_ORTUSUYOR():
    """HDTF çıktısı ``Yazmac``a girince ``⟨Ψ|Ψ⟩`` değişmemeli.

    Ölçüt bağımsızdır: ham çekirdek zinciri **elle** (transfer dizeyi
    döngüsüyle) büzülür ve ``Yazmac.norm()`` ile yüzleştirilir. İkisi
    ayrışırsa köprü yalan söylüyor demektir.
    """
    diziler = [np.random.default_rng(k).normal(size=13) for k in range(3)]
    cek, _kesme, _kademe = hiyerarsik_ikili_agac_katlama(diziler,
                                                         bag_boyutu=8)
    E = np.array([[1.0]])
    for c in cek:
        E = np.einsum("lr,lia,rib->ab", E, np.asarray(c, float),
                      np.asarray(c, float), optimize=True)
    elle = float(E[0, 0])

    yz, bilgi = Yazmac.hdtf_ile_kur(diziler, bag_boyutu=8)
    assert int(bilgi["çekirdek_sayısı"]) == len(cek)
    assert abs(float(yz.norm()[0]) - elle) < 1e-4 * max(abs(elle), 1e-30)


def test_hdtf_tek_cekirdek_sinir_hali():
    """Tek çekirdeğe inen dejenere hâlde de zincir kurulabilmeli."""
    yz, bilgi = Yazmac.hdtf_ile_kur([np.array([1.0])], bag_boyutu=4)
    assert int(bilgi["çekirdek_sayısı"]) == 1
    assert abs(float(yz.norm()[0]) - 1.0) < 1e-9


# ══════════════════════════════════════════════════════════════════════
#  2. QTT iç bağ -- izafî operatörler TAM taşınıyor mu
# ══════════════════════════════════════════════════════════════════════

def test_qtt_serpistirilmis_sira_otelemeyi_MAKINE_HASSASIYETINDE_tasiyor():
    """Öteleme operatörü ``χ`` boyutlu açık çekirdeğin **dörtte biriyle**
    ve makine hassasiyetinde taşınmalı.

    Bu, ``kuantum/ic_bag.py``nin merkezî iddiasıdır ve orası silindiği
    için şahidi buraya taşındı. Ölçüt iki taraflıdır: hem ayrıştırma
    hatası, hem de **geri açmanın** aslına dönmesi.
    """
    chi = 8
    T = np.zeros((chi, 2, chi))
    for i in range(chi):
        T[i, :, (i + 1) % chi] = 1.0          # izafî öteleme T̂
    cek, hata, _bag = qtt_cekirdek_ayristir(T, r=4, sira="serpistir")
    geri = qtt_cekirdek_ac(cek, chi, 2, sira="serpistir")

    assert hata < 1e-12                        # ölçüldü: ~1,9e-16
    assert np.max(np.abs(geri - T)) < 1e-12    # ölçüldü: ~4,4e-16
    # ve bunu açık çekirdekten AZ parametreyle yapmalı
    assert qtt_parametre(cek) < acik_parametre(chi, 2)


def test_qtt_rastgele_cekirdegi_sikistirMAZ_ve_bu_dogrudur():
    """Rastgele bir çekirdek sıkışmamalı -- iddia sınırını da sınarız.

    ``ic_bag.py``nin kendi şerhi bunu açıkça söylüyordu: *"rastgele
    çekirdek hâlâ sıkışmıyor ve sıkışmaması da doğrudur."* Sınama o
    haddin hâlâ ayakta olduğunu denetler; sıkışsaydı ölçüt bozulmuş
    olurdu.
    """
    rng = np.random.default_rng(0)
    G = rng.normal(size=(8, 2, 8))
    _cek, hata, _bag = qtt_cekirdek_ayristir(G, r=4, sira="serpistir")
    assert hata > 1e-3


# ══════════════════════════════════════════════════════════════════════
#  3. TTN ağaç -- O(log N) mesafe ve TAM büzülme
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("h,w", [(10, 10), (30, 30)])
def test_agac_mesafesi_zincirden_LOGARITMIK_kisa(h, w):
    """Köşeden köşeye: zincirde ``O(N)``, ağaçta ``O(log N)``.

    30×30'da ölçülen: zincir 899 adım, ağaç 18 adım (50 kat). Bu, MPS
    yerine TTN kullanmanın **yegâne** somut kazancıdır ve sayı olarak
    burada durur.
    """
    ag = AgacYazmaci(AgacAyar(h=h, w=w, renk=10, bag=8))
    zincir = h * w - 1
    agac = ag.mesafe((0, 0), (h - 1, w - 1))
    assert agac < zincir
    assert agac <= 4 * int(np.ceil(np.log2(h * w)))   # O(log N)


def test_agac_kapisi_TAM_hesapla_ortusuyor():
    """χ yeterken ağaç MPO'su tam bir üniterdir, yaklaşıklık değildir."""
    from kuantum.yazmac import _kapi_sinamasi
    r = _kapi_sinamasi(3, 3, 2, 64, 10)
    assert r["hata"] < 1e-10                   # ölçüldü: ~2,9e-15
    assert abs(r["norm"] - 1.0) < 1e-6


def test_agac_chi_kisilinca_hata_BUYUYOR():
    """Ölçüt kör olmasın: ``χ`` daralınca hata **artmalı** (H90)."""
    from kuantum.yazmac import _kapi_sinamasi
    dar = _kapi_sinamasi(3, 3, 2, 2, 10)["hata"]
    genis = _kapi_sinamasi(3, 3, 2, 64, 10)["hata"]
    assert dar > genis


# ══════════════════════════════════════════════════════════════════════
#  4. Üç ağaç -- genlik söndürmenin ÜNİTER yolu
# ══════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("teta", [0.0, 0.3, 0.9, 1.4])
def test_iki_kademeli_donme_UNITER(teta):
    """"Bu ihtimali sıfırla" ölçüm ister; "θ kadar dön" üniterdir."""
    d = 6
    u, v = np.eye(d)[0], np.eye(d)[3]
    G = iki_kademeli_donme(d, u, v, teta)
    assert np.max(np.abs(G.conj().T @ G - np.eye(d))) < 1e-12


# ══════════════════════════════════════════════════════════════════════
#  5. PTR halka -- DÖNGÜSEL hedefte zincirden iyi mi
# ══════════════════════════════════════════════════════════════════════

def test_halka_dongusel_hedefte_zincirden_IYI():
    """Halkanın tek meşru iddiası budur ve ölçülür.

    Uçları bağlı (döngüsel bakışımlı) bir hedefte halka zincirden
    belirgin daha az hata vermeli. Vermezse "çevrim bedeli"ne karşılık
    hiçbir şey alınmıyor demektir ve PTR'nin varlığı gerekçesiz kalır.
    """
    rng = np.random.default_rng(0)
    n = 5
    t = rng.uniform(-1, 1, size=(400, n))
    y = sum(np.cos(2 * t[:, k]) * np.cos(2 * t[:, (k + 1) % n])
            for k in range(n))
    y = (y - y.mean()) / (y.std() + 1e-12)
    sonuc = {}
    for ad, hlk in (("halka", True), ("zincir", False)):
        P = PolinomHalka(n, chi=4, derece=6, tohum=1, halka=hlk)
        sonuc[ad] = P.oturt(t, y, tur=8)[-1]
    # ölçüldü: halka 0,1229 -- zincir 0,2987
    assert sonuc["halka"] < sonuc["zincir"]


def test_tensor_halka_izi_dogru_buzuluyor():
    """``ψ(x) = Tr(Π G_k[:,x_k,:])`` -- yığın büzülmesi elle tutuyor mu."""
    th = TensorHalka(4, d=2, chi=3, tohum=0, halka=True)
    X = np.array([[0, 1, 1, 0], [1, 1, 0, 1]])
    bek = []
    for x in X:
        M = np.eye(3)
        for k in range(4):
            M = M @ th.G[k][:, x[k], :]
        bek.append(float(np.trace(M)))
    assert np.allclose(th.genlik(X), bek, atol=1e-10)


# ══════════════════════════════════════════════════════════════════════
#  6. Izgara ihtimal uzayı -- EVVELCE ÇÖKEN okuma yolu
# ══════════════════════════════════════════════════════════════════════

def test_ihtimal_okuma_yolu_ARTIK_COKMUYOR_ve_dogru_okuyor():
    """**Bu sınama bir kusurun şahididir (kütük H211).**

    ``nefs/ihtimal.py::hucre_dagilimi`` çevreleri kendi başına büzüyor
    ve ``A``yı ``A[k]`` diye indeksliyordu; hâlbuki ``Yazmac.A``nın ilk
    ekseni **yığın**dır, yuva değil. Fiilen koşturuldu::

        IndexError: index 11 is out of bounds for axis 0 with size 1

    Yani modülün bütün okuma yolu çalışmıyordu ve bunu kimse
    görmemişti: AST ile ölçüldü, o dosyayı **hiçbir modül import
    etmiyordu**. Nüsha ``Yazmac.blok_dagilimi``a indirilince kusur
    da kalktı.
    """
    iy = IhtimalYazmaci(IhtimalAyar(h=2, w=3, renk=4, kubit_basina=2,
                                    bag=8))
    iy.ac()
    iy.hucre_sabitle(0, 1, 2)                  # (0,1) → renk 2
    P = iy.hucre_dagilimi(0, 1)                # evvelce IndexError
    assert P.shape == (4,)
    assert int(np.argmax(P)) == 2              # kilitlenen renk okunuyor
    assert abs(float(P.sum()) - 1.0) < 1e-9


def test_ihtimal_kubit_hesabi_ceridenin_sayilariyla_tutuyor():
    """30×30, 10 renk: ``10⁹⁰⁰`` ihtimal, 3.600 fiilî kübit (H51)."""
    h = kubit_hesabi(30, 30, renk=10, kubit_basina=4)
    assert int(h["hücre"]) == 900
    assert abs(h["ihtimal_log10"] - 900.0) < 1e-9
    assert int(h["fiilî_kübit"]) == 3600


# ══════════════════════════════════════════════════════════════════════
#  7. Tevhidin kendisi -- nüsha tekleşti mi, dosyalar gitti mi
# ══════════════════════════════════════════════════════════════════════

def test_blok_dagilimi_TEK_NUSHA_ve_qyazmac_ayni_sayiyi_veriyor():
    """Üç nüsha vardı; biri çöküyordu. Şimdi tek nüsha, aynı sayı."""
    from nefs.qyazmac import QAyar, QYazmac
    q = QYazmac(4, QAyar(bag=8, bolge_ac=True))
    rng = np.random.default_rng(1)
    q.kodla(rng.normal(size=(4, 6)))
    q.superpozisyon()
    q.mera()
    for bas, kac in ((q.veri(0, 0), 3), (q.kulli("kelam", 0), 4)):
        a = np.asarray(q.blok_dagilimi(bas, kac), float)
        b = np.asarray(q.y.blok_dagilimi(bas, kac), float)
        assert np.allclose(a, b, atol=1e-12)


def test_tasinan_alti_dosya_ARTIK_YOK():
    """Tevhid yarım kalmasın: eski modüller içe aktarılamamalı."""
    import importlib
    for m in ("kuantum.katlama", "kuantum.ic_bag", "kuantum.ptr",
              "nefs.agac", "nefs.ucagac", "nefs.ihtimal"):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(m)


def test_kararli_svd_gram_yedegi_hala_ayakta():
    """``gesdd`` düşerse Gram özayrışımına geçiş -- belirlenimci yedek."""
    from kuantum.yazmac import _kararli_svd
    rng = np.random.default_rng(0)
    M = rng.normal(size=(12, 7))
    U, s, Vt = _kararli_svd(M)
    assert np.max(np.abs(U @ np.diag(s) @ Vt - M)) < 1e-10
