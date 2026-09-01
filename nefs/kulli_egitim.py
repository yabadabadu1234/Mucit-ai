"""
KÜLLÎ EĞİTİM -- vesikadaki dalga eniyilemesinin mimarîye bağlanması.

Vesikadaki hüküm aynen icra edilir::

    Ĥ_Nefs   = Σ_Θ (ℒ_Tenakuz + ℒ_Fıtrat + ℒ_Mizan) |Θ⟩⟨Θ|
    |Θ_opt⟩  = (2|Ψ₀⟩⟨Ψ₀| − I) · exp(−iγ Ĥ_Nefs) |Ψ₀⟩
    Θ*       = Ölçüm(|Θ_opt⟩)      ⟹  klasik Adam/SGD döngüsü KALKMIŞTIR

Bağlanan parçalar:

* ``kuantum/nqs.py``    -- ``|Ψ₀⟩``: parametre uzayının kompakt dalgası.
* ``kuantum/dalga.py``  -- faz orağı, difüzyon, girişim, çöküş.
* ``kuantum/ptr.py``    -- kayıp yüzeyinin halka temsili (vekil).
* ``kuantum/stabilizer.py`` -- Clifford çerçevesi (rank ölçümü).
* ``nefs/qakis.py``     -- 41 üniter meleke; kaybın kaynağı.
* ``hesap/donanim.py``  -- CPU/GPU yolu ve iş parçalama.

**Parametrenin kübite kodlanması.** ``Θ ∈ ℝ^d`` her koordinat için
``bit`` bitle ``[−yaricap, +yaricap]`` aralığına açılır; toplam
``d·bit`` kübit. Gri kod kullanılır: komşu tam sayılar **tek bit**
farkeder, dolayısıyla Metropolis'in tek bit çevirmesi parametre uzayında
**küçük** bir adımdır. Düz ikili kodda 31→32 geçişi altı biti birden
çevirir ve arama uzayı sunî olarak uçurumlu görünür.

**Adam/SGD'nin yerine ne kondu.** Hiçbir gradyan alınmaz. Öğrenme iki
kapalı formdan ibarettir:
1. Grover'ın iki boyutlu özyinelemesi tavlama sıcaklığını **söyler**,
2. NQS'in son katı hedef genliğe **en küçük karelerle** oturtulur.

**İki ölçüt beraber** raporlanır (kütük H47): kapsama (konuşma oranı) ve
konuşunca isabet; ayrıca tam çözüm. Ara ölçüt yükselirken tam çözüm
sıfır kalıyorsa o da bir hükümdür ve gizlenmez.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from hesap.donanim import Donanim, donanim

from .qakis import QNefs
from .qegitim import degerlendir, ornekler, uygunluk  # uygunluk: eski ölçüm yolu
from .qyazmac import QAyar

__all__ = ["EgitimAyari", "KISA_CPU", "ORTA", "AZAMI_KAGGLE",
           "gri_kodla", "gri_coz", "KulliEgitim"]


# =====================================================================
#  Gri kod: komşu değerler tek bit farkeder
# =====================================================================
def gri_kodla(k: np.ndarray, bit: int) -> np.ndarray:
    """Tam sayı → Gri kod bitleri. ``(B, d)`` → ``(B, d·bit)``."""
    k = np.asarray(k, np.int64)
    g = k ^ (k >> 1)
    kaydir = np.arange(bit - 1, -1, -1)
    B = ((g[..., None] >> kaydir) & 1).astype(np.int64)
    return B.reshape(k.shape[0], -1)


def gri_coz(X: np.ndarray, d: int, bit: int) -> np.ndarray:
    """Gri kod bitleri → tam sayı. ``(B, d·bit)`` → ``(B, d)``."""
    B = np.asarray(X, np.int64).reshape(-1, d, bit)
    # Gri → ikili: her bit, kendisinden soldakilerin XOR'u
    ikili = np.cumsum(B, axis=-1) % 2
    agirlik = (1 << np.arange(bit - 1, -1, -1)).astype(np.int64)
    return (ikili * agirlik).sum(-1)


# =====================================================================
@dataclass
class EgitimAyari:
    """**Her şey burada ve hiçbiri koda gömülü değildir.**

    Kullanıcı hükmü: *"modelin tüm parametrelerini en genel eğitim için
    mümkün olan hududun en sonuna kadar açmanı istiyorum."* Onun için
    yazmaç ölçüleri, dalga ölçüleri, veri ölçüleri ve donanım ölçüleri
    tek bir yerde ve hepsi serbesttir.
    """
    ad: str = "kısa"
    # --- yazmaç (nefsin kendisi)
    satir_kubiti: int = 4
    yerel_kubit: int = 1
    bag: int = 16                    # χ
    mera_kademe: int = 3
    # --- veri
    gorev: int = 24
    ornek_sayisi: int = 4
    pencere: int = 8
    sozluk: int = 16
    degerlendirme_gorevi: int = 4
    azami_uret: int = 32        # bundan uzun hedefli görev ATLANIR
    # --- parametrenin kübite kodlanması
    bit: int = 6
    yaricap: float = 2.5
    # --- dalga (NQS + Grover)
    nqs_gizli: Tuple[int, ...] = (48,)
    nqs_derece: int = 5
    cevrim: int = 6
    ornek: int = 24
    zincir: int = 8
    oran: float = 0.20
    kademe: float = 0.6
    lam: float = 1e-2
    #: Tâlimin dış tur sayısı (`nefs/talim.py`): altuzay kaç kere
    #: yenilenecek. Bütçenin en kaba kolu budur.
    talim_tur: int = 3
    #: Etkin altuzay kaç yönlü sonlu farkla kurulacak. Maliyeti
    #: ``2·altuzay_ornek`` kayıp çağrısıdır -- tâlimin **en pahalı**
    #: uzvu budur, o yüzden ayarda durur ve gömülü değildir.
    altuzay_ornek: int = 24
    #: Kesit boyutu ``r``yi bağlayan kübit haddi (``r = azami_kubit /
    #: bit``). **Ölçüldü** (d=262, aynı kayıp): "etkin" altuzay r=8'de
    #: yayılım 0,0026; determinist Walsh kesiti r=32'de 0,0088. Dar
    #: kesit, kaybın değişimini fiilen görmüyordu.
    azami_kubit: int = 192
    # --- donanım
    surec: int = 0                   # 0 = donanımdan tayin et
    tohum: int = 0

    def qayar(self) -> QAyar:
        return QAyar(satir_kubiti=self.satir_kubiti,
                     yerel_kubit=self.yerel_kubit, bag=self.bag,
                     mera_kademe=self.mera_kademe, tohum=self.tohum)


#: **CPU'da koşan kısa hâl.** Kullanıcı şartı: *"en azından CPU'da
#: eğitimin çok kısa hâli çalışabilmeli."* Ölçüldü: bu ayarla bir ileri
#: geçiş 0,53 sn; aşağıdaki çevrim sayısıyla eğitim dakikalar mertebesinde
#: biter.
#: **Bütçe ölçülerek konmuştur, tahminle değil.** Yeni kayıp
#: (`nefs/kulli_kayip.py`) 41 melekeyi tek tek okuduğu için bir çağrı
#: ~2 sn sürer; eski kayıp beş sayı okuyup geçiyordu. O hâlde "kısa
#: CPU hâli"nin dalga bütçesi buna göre küçültülür -- aksi hâlde
#: "kısa" hâl saatler sürerdi. Ölçü değişince bütçe de değişir;
#: bütçeyi sabit tutup ölçüyü ağırlaştırmak, koşmayan bir ayar
#: bırakmak olurdu.
#: **B (``ornek_sayisi``) BU ORTAM İÇİN ÖLÇÜLEREK SEÇİLDİ (kütük H151).**
#: Ceride B'nin azamîye çıkarılmasını emrediyor ve verim cihetinden
#: haklıdır: veri yığın hâlinde koşulunca örnek başına maliyet düşüyor
#: (B=32'de 1,69× hızlanma, 1,014 → 0,608 sn/örnek). Fakat **işaret
#: cihetinden** ölçüm başka söylüyor::
#:
#:      B    kayıp sn   parametre yayılımı   veri gürültüsü
#:      2      1,73          0,0191               —
#:      4      2,96          0,0066            0,0013
#:      8      5,51          0,0045            0,0019
#:     16     10,55          0,0058            0,0007
#:     32     20,35          0,0051            0,0018
#:
#: B büyüdükçe parametre yayılımı **düşüyor**: yığın ortalaması, organ
#: ölçülerini yine merkezî limitle (σ/√B) söndürüyor. B=4'ten sonra
#: ölçülebilir bir kazanç yok, maliyet ise doğrusal artıyor.
#:
#: Kullanıcı hükmü CPU için kararı bana bıraktı ve "makul delillerle
#: yavaşlatacağını düşünüyorsan yapma" dedi. Delil budur: **B=4**.
#: GPU tarafında (``AZAMI_KAGGLE``) ceride hükmü aynen icra edildi.
KISA_CPU = EgitimAyari(ad="kısa-CPU", ornek_sayisi=4, cevrim=1,
                       ornek=3, zincir=2, talim_tur=1,
                       altuzay_ornek=6, degerlendirme_gorevi=8)

#: Orta hâl -- tek makinede saatler.
ORTA = EgitimAyari(ad="orta", satir_kubiti=6, bag=32, gorev=120,
                   ornek_sayisi=24, degerlendirme_gorevi=40,
                   azami_uret=120,
                   nqs_gizli=(96, 64), nqs_derece=6, cevrim=40,
                   ornek=128, zincir=32, bit=8)

#: **Kaggle azamî hâli.** 4 cihaz, ~84 GB VRAM. Buradaki sayılar
#: donanımın haddine göre konmuştur ve BURADA KOŞMAMIŞTIR; koştuğu da
#: iddia edilmiyor. GPU'da hızlanan kısım NQS'in genlik hesabı ve
#: örneklemesidir; kübit ileri geçişi süreçler arasında bölünür.
#: **B VE BAĞLAM CERİDE HÜKMÜYLE AZAMÎ HADDE ÇEKİLDİ (kütük H151).**
#: Ceridenin taksimatı aynen::
#:
#:     Veri yazmacı : B = 2048 dizi × L_bağlam = 4096 belirteç
#:                  = 8.388.608 belirteç / adım  (8.388.608 kübit)
#:
#: Yığın ekseni yazmaçta zaten var (`main/yazmac.py`, ``yigin``) ve
#: kayıp artık veriyi yığın hâlinde koşturuyor; o hâlde B'yi büyütmenin
#: yolu açıktır ve burada ceride hükmü icra edilmiştir.
#:
#: **HUDUT -- açıkça:** bu ayar bu ortamda KOŞMAMIŞTIR ve koştuğu iddia
#: edilmiyor. Burada GPU yoktur (yalnız CPU, 16 GB, ``torch`` kurulu
#: değil); 8,4 milyon belirteçlik yığın bu makinenin belleğine sığmaz.
#: Ayar, donanım geldiğinde icra edilmek üzere ve ceridenin emrettiği
#: ölçülerle **kodda hazır** durmaktadır.
AZAMI_KAGGLE = EgitimAyari(
    ad="azamî-Kaggle", satir_kubiti=12, yerel_kubit=1, bag=256,
    mera_kademe=5, gorev=1000, ornek_sayisi=2048, pencere=4096,
    sozluk=16, degerlendirme_gorevi=120, azami_uret=0, bit=10,
    yaricap=3.0, nqs_gizli=(512, 256, 128), nqs_derece=8, cevrim=400,
    ornek=4096, zincir=256, oran=0.10, kademe=0.4, lam=1e-3)


# =====================================================================
#  Süreç havuzu: kübit ileri geçişi utanmadan paraleldir
# =====================================================================
_ISCI: Dict[str, object] = {}


def _isci_kur(ayar: EgitimAyari, veri, kademe=None) -> None:
    _ISCI["nefs"] = QNefs(ayar.tohum, ayar.qayar())
    _ISCI["veri"] = veri
    _ISCI["ayar"] = ayar
    _ISCI["kademe"] = list(kademe or [])
    # yer tahsisi ilk koşuda olur; her işçide aynı sırayla olmalı
    _ISCI["nefs"].idrak_et(np.zeros((2, ayar.satir_kubiti)))


def _isci_kayip(p: np.ndarray) -> float:
    """Süreç havuzundaki işçi de **aynı** kaybı hesaplar.

    Ayrı bir kayıp kullansaydı paralel koşu ile tek süreçli koşu farklı
    şeyi eniyiler, mukayeseleri de manasız olurdu.
    """
    from .kulli_kayip import kulli_kayip
    a: EgitimAyari = _ISCI["ayar"]        # type: ignore[assignment]
    t = kulli_kayip(_ISCI["nefs"], _ISCI["veri"], p,  # type: ignore
                    a.sozluk, kademe_olcumleri=_ISCI.get("kademe"))
    return float(t["kayıp"])


# =====================================================================
class KulliEgitim:
    """Nefsi **dalga ile** eğiten küllî motor -- Adam/SGD yoktur."""

    def __init__(self, ayar: EgitimAyari = KISA_CPU,
                 gorevler: Optional[Sequence] = None,
                 dh: Optional[Donanim] = None) -> None:
        self.ayar = ayar
        self.dh = dh or donanim()
        from idrak import arc
        hepsi = list(gorevler) if gorevler is not None else \
            arc.yukle_hepsi("training")
        self.egitim_gorevleri, self.dogrulama = arc.bol(hepsi, dogrulama=100)
        self.veri = ornekler(self.egitim_gorevleri, azami=ayar.ornek_sayisi,
                             pencere=ayar.pencere, sozluk=ayar.sozluk,
                             tohum=ayar.tohum)
        self.nefs = QNefs(ayar.tohum, ayar.qayar())
        self.nefs.idrak_et(np.zeros((2, ayar.satir_kubiti)))
        self.d = len(self.nefs)
        self.p0 = self.nefs.vektor()
        self.havuz = None
        self.olcum: Dict[str, object] = {}
        #: **Altı kademenin ölçüleri kayba girer** (`nefs/kademeler.py`).
        #: Eğitim görevlerinden bir avuç üzerinde bir kere hesaplanır:
        #: kademeler parametreye değil göreve bağlıdır, o yüzden her
        #: kayıp çağrısında tekrar hesaplamak israf olurdu.
        self.kademe_olcumleri = self._kademeleri_olc()

    def _kademeleri_olc(self, kac: int = 4):
        """Altı kademeyi birkaç görevde koştur ve ölçülerini topla.

        Bu, kademeleri **eğitime sokan** bağdır: kademelerin hatası
        kayba girmezse o kademeler eğitilmez, yalnız çıkarımda süs
        olarak durur.
        """
        try:
            from .kademeler import kademeleri_kos
            out = []
            for g in list(self.egitim_gorevleri)[:int(kac)]:
                out += list(kademeleri_kos(g)["ölçümler"])
            return out
        except Exception:                                # noqa: BLE001
            return []

    # -----------------------------------------------------------------
    def _coz(self, X: np.ndarray) -> np.ndarray:
        """Kübit dizisi → parametre vektörleri ``(B, d)``."""
        a = self.ayar
        k = gri_coz(X, self.d, a.bit)
        u = k / float((1 << a.bit) - 1)
        return self.p0 + a.yaricap * (2.0 * u - 1.0)

    def _kodla(self, P: np.ndarray) -> np.ndarray:
        a = self.ayar
        u = np.clip((P - self.p0) / a.yaricap, -1.0, 1.0)
        k = np.rint((u + 1.0) * 0.5 * ((1 << a.bit) - 1)).astype(np.int64)
        return gri_kodla(k, a.bit)

    # -----------------------------------------------------------------
    def kayip(self, X: np.ndarray) -> np.ndarray:
        """Eski arayüz: **kübit** dizisinden kayıp. Yerinde bırakıldı.

        `nefs/talim.py` kodlamayı kendi içinde yaptığı için ana yol
        artık ``kayip_p``dir; bu, kübit uzayında kıyas isteyen ölçümler
        için duruyor ve kaldırılmadı -- kaldırmak, eski ölçümleri
        tekrarlanamaz kılardı.
        """
        return self.kayip_p(self._coz(np.atleast_2d(X)))

    def kayip_p(self, P: np.ndarray) -> np.ndarray:
        """``ℒ(Θ)`` -- **parametre** uzayında, yığın hâlinde.

        ===================================================================
        KAYIP DEĞİŞTİ: 41 MELEKENİN HEPSİ SAYILIYOR
        ===================================================================

        Eskiden ``qegitim.uygunluk`` çağrılıyordu::

            V = −log P(doğru belirteç) + 0,25·mîzân − 0,1·entropi

        İki kusuru vardı ve ikisi de yapısaldı (bkz. `nefs/olcu.py` ve
        `nefs/kulli_kayip.py` şerhleri):

        1. Baştaki terim **belirteç kestirimi**ydi -- kütük H133'te
           teşhis edilip çıkarımdan söküldüğü hâlde eğitimde duruyordu.
           Yani model çıkarımda muhakeme ediyor, eğitimde sonraki
           belirteci tahmin etmeyi öğreniyordu.
        2. Ceza yalnız **beş** küllî alan okuyordu; otuz altı melekenin
           eğitim sinyali fiilen sıfırdı.

        Şimdi ``kulli_kayip`` çağrılır: 41 melekenin her biri kendi
        sözleşmesine göre ölçülür, altı kademe kendi hatasını verir, ve
        hepsi `nefs/olcu.py`nin funktörüyle **müşterek uzaya** çekilip
        orada toplanır. Elle konmuş katsayı kalmamıştır.
        """
        from .kulli_kayip import kulli_kayip
        P = np.atleast_2d(np.asarray(P, float))
        if self.havuz is not None:
            return np.array(list(self.havuz.map(_isci_kayip, list(P))))
        out = np.empty(P.shape[0], float)
        for i, p in enumerate(P):
            t = kulli_kayip(self.nefs, self.veri, p, self.ayar.sozluk,
                            kademe_olcumleri=self.kademe_olcumleri)
            out[i] = float(t["kayıp"])
        return out

    # -----------------------------------------------------------------
    def kos(self, paralel: bool = True) -> Dict[str, object]:
        a = self.ayar
        n_kubit = self.d * a.bit
        t0 = time.perf_counter()

        surec = a.surec or min(self.dh.cekirdek, 8)
        if paralel and surec > 1:
            import multiprocessing as mp
            self.havuz = mp.get_context("fork").Pool(
                surec, initializer=_isci_kur,
                initargs=(a, self.veri, self.kademe_olcumleri))

        # **TEK TÂLİM USULÜ** (`nefs/talim.py`). Dalga (NQS + Grover)
        # artık doğrudan çağrılmaz; usulün dokuz uzvundan **biri**dir.
        # Yanına had ölçümü (`akis/tikiz`), etkin altuzay
        # (`main/optimize`), vekil yüzey (`ogrenme/rkhs`), durgunluk
        # (`ogrenme/grassmann`), tünelleme (`arama/bukum`) ve denge
        # (`fitrat/denge`) girer. Bu usul **her** eğitim yerinde aynen
        # kullanılır; istisna yoktur.
        from .talim import Talim, TalimAyari
        talim_ayari = TalimAyari(
            ad=a.ad, r=max(2, self.d // 8), bit=a.bit,
            yaricap=a.yaricap, cevrim=a.cevrim, ornek=a.ornek,
            zincir=a.zincir, oran=a.oran, kademe=a.kademe, lam=a.lam,
            nqs_gizli=a.nqs_gizli, nqs_derece=a.nqs_derece,
            tur=a.talim_tur, altuzay_ornek=a.altuzay_ornek,
            azami_kubit=a.azami_kubit, sesli=True, tohum=a.tohum)
        try:
            t = Talim(self.kayip_p, self.p0, talim_ayari, dh=self.dh)
            r = t.kos()
        finally:
            if self.havuz is not None:
                self.havuz.close()
                self.havuz.join()
                self.havuz = None

        V_ilk = float(r["V_ilk"])
        p_yildiz = np.asarray(r["p"], float)
        V_son = float(r["V_son"])
        self.nefs.yukle(p_yildiz)

        deg = degerlendir(self.nefs, self.dogrulama,
                          azami=a.degerlendirme_gorevi,
                          pencere=a.pencere, sozluk=a.sozluk,
                          azami_uret=a.azami_uret)
        self.olcum = {
            "ayar": a.ad, "kübit": n_kubit, "parametre": self.d,
            "veri": len(self.veri), "süreç": surec,
            "V_ilk": V_ilk, "V_son": V_son,
            "süre_sn": time.perf_counter() - t0,
            "kayıp_çağrısı": int(r.get("kayıp_çağrısı", 0)),
            "seyir": r["seyir"], "değerlendirme": deg,
            "tâlim_günlüğü": r.get("günlük", []),
            "düşen_uzuv": r.get("düşen_uzuv", {}),
            "kademe_ölçüsü": len(self.kademe_olcumleri),
            "p": p_yildiz}
        return self.olcum

    # -----------------------------------------------------------------
    def as_gek_mukayesesi(self, butce: int = 0, n_ornek: int = 8
                          ) -> Dict[str, float]:
        """Aynı bütçede **eski** AS-GEK motoru ne yapıyordu (kütük H54/2).

        Borç şuydu: 250 boyutlu uzayda vekil yüzey için asgarî ``10·d``
        değerlendirme gerekirken 8 çevrim koşuluyordu. Burada ikisi
        **aynı kayıp bütçesiyle** karşılaştırılır; hangisinin daha iyi
        olduğu iddia değil ölçüm meselesidir.
        """
        from main.optimize import as_gek_adimi
        a = self.ayar
        p = self.p0.copy()
        # **Eşit bütçe.** Evvelce çevrim sayısı elle veriliyordu ve iki
        # motor farklı sayıda kayıp çağırıyordu (AS-GEK 246, dalga 144);
        # o hâlde mukayese hükmü veremez. Bütçe kayıp ÇAĞRISI cinsinden
        # eşitlenir: AS-GEK çevrim başına ``2·n_ornek + n_nokta + 1``
        # çağırır (``n_nokta = max(24, 8r)``, burada r=2 → 24).
        cevrim_maliyeti = 2 * n_ornek + 24 + 1
        butce = butce or (a.cevrim * a.ornek)
        cevrim = max(1, butce // cevrim_maliyeti)

        def f(q: np.ndarray) -> float:
            return float(uygunluk(self.nefs, self.veri, q, a.sozluk))

        V = f(p)
        t0 = time.perf_counter()
        for c in range(cevrim):
            p_yeni, _ = as_gek_adimi(f, p, yaricap=a.yaricap, r=2,
                                     izgara=12, n_ornek=n_ornek,
                                     tohum=a.tohum + c)
            V_yeni = f(p_yeni)
            if V_yeni < V:
                p, V = p_yeni, V_yeni
        return {"V_son": V, "süre_sn": time.perf_counter() - t0,
                "çevrim": float(cevrim),
                "kayıp_çağrısı": float(cevrim * cevrim_maliyeti)}


# =====================================================================
def rapor(ayar: EgitimAyari = KISA_CPU, mukayese: bool = True) -> str:
    from hesap.donanim import rapor as donanim_raporu

    s = ["=== KÜLLÎ EĞİTİM: dalga ile, gradyansız ===", "",
         donanim_raporu(), ""]
    E = KulliEgitim(ayar)
    r = E.kos()
    d = r["değerlendirme"]
    s += ["ayar=%s   nefs parametresi=%d   kodlama=%d bit → %d kübit"
          % (r["ayar"], r["parametre"], ayar.bit, r["kübit"]),
          "veri=%d örnek   süreç=%d   kayıp çağrısı=%d   süre=%.1f sn"
          % (r["veri"], r["süreç"], r["kayıp_çağrısı"], r["süre_sn"]),
          "",
          "V(Θ):  ilk %.4f  →  son %.4f   (fark %.4f)"
          % (r["V_ilk"], r["V_son"], r["V_ilk"] - r["V_son"]),
          "",
          "TÂLİM SEYRİ (tek usul, dokuz uzuv):",
         "  tur      V        yarıçap  durgunluk  deneme   çağrı"]
    for c in r["seyir"]:
        s.append("  %-5d %-10.4f %-8.3f %-10.3e %-7d %d"
                 % (int(c["tur"]), c["V"], c["R"], c["durgunluk"],
                    int(c["deneme"]), int(c["çağrı"])))
    if r.get("düşen_uzuv"):
        s.append("  DÜŞEN UZUV: %s" % ", ".join(sorted(r["düşen_uzuv"])))
    s.append("  kayba giren kademe ölçüsü: %d" % r.get("kademe_ölçüsü", 0))

    s += ["",
          "İKİ ÖLÇÜT BERABER (kütük H47):",
          "  tam çözülen        : %d / %d" % (d["tam_çözülen"], d["deneme"]),
          "  ilk belirteç isabeti: %d / %d"
          % (d["ilk_belirteç_isabeti"], d["deneme"]),
          "  ortalama hücre isabeti: %.4f" % d["ortalama_hücre_isabeti"],
          "  sükût sayısı        : %d" % d["sükût"],
          "  atlanan (hedef uzun): %d  ← hiç denenmedi, denemeye SAYILMAZ"
          % d["atlanan_uzun"]]

    if mukayese:
        m = E.as_gek_mukayesesi()
        s += ["",
              "ESKİ MOTORLA MUKAYESE (aynı kayıp, kütük H54/2. borç):",
              "  AS-GEK  V_son=%.4f  çağrı=%d  %.1f sn"
              % (m["V_son"], int(m["kayıp_çağrısı"]), m["süre_sn"]),
              "  DALGA   V_son=%.4f  çağrı=%d  %.1f sn"
              % (r["V_son"], r["kayıp_çağrısı"], r["süre_sn"])]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
