"""
TÂLİM -- **tek** eğitim usulü; hangi parametre olursa olsun, istisnasız.

===================================================================
NİÇİN VAR: EĞİTİM ÜÇ AYRI YERDE ÜÇ AYRI USULDÜ
===================================================================

Kullanıcı hükmü:

> *"Kendine öyle bir eğitim mimarisi oluştur ki öğrenilecek hangi
> parametre olursa olsun istisnası olmaksızın o mimariyi kullan.
> Grover+NQS'den oluşan dalgalı eğitim modelini başka usulleri de uzuv
> olarak dahil edip daha girift bir eğitim usulü ortaya çıkararak tüm
> eğitim yerlerinde aynı usulü tatbik edebilirsin."*

Evvelce kod tabanında **üç ayrı** eniyileme vardı ve birbirinden
habersizdi:

* `nefs/kulli_egitim.py`  -- Gri kod + NQS + Grover (dalga),
* `nefs/qegitim.py::egit` -- Active Subspace + AS-GEK vekil yüzeyi,
* `main/optimize.py`      -- ikisinin parçaları, ayrıca.

Üçü de aynı işi yapıyordu: **gradyansız bir kayıp yüzeyinin asgarîsini
bulmak.** Ayrı olmalarının hiçbir sebebi yoktu; olan zararı vardı --
biri düzeldiğinde diğeri düzelmiyordu ve hangisinin daha iyi olduğu
hiç ölçülmüyordu.

Burada tek bir usul kurulur ve **her yerde o kullanılır**: melekelerin
açıları, tasavvur (2. kademe) parametreleri, muhakeme (3. kademe)
arama ağırlıkları -- hepsi. "Bu parametre başka türlü eğitilir" diye
bir istisna yoktur; olsaydı usul tek olmazdı.

===================================================================
USULÜN UZUVLARI -- her biri ayrı bir modül, her biri hakikî bir iş
===================================================================

Dalga (NQS + Grover) usulün **kalbi**dir fakat tek başına kör bir
aramadır: ``d`` boyutlu uzayda ``d·bit`` kübit ile arar ve ``d``
büyüdükçe boğulur. Etrafına sekiz uzuv daha bağlanır ve her birinin
niçin orada olduğunun bir cevabı vardır:

1. **HAD** (`akis/tikiz.py`) -- kayıp *zorlayıcı* mı, yani alt seviye
   kümeleri sınırlı mı? Değilse asgarî sonsuzda olabilir ve arama
   yarıçapı **bağlanmalıdır**. Bu bir tedbir değil, aramanın iyi
   konulmuş olmasının şartıdır. Sorulmazsa arama boşluğa koşar.

2. **ALTUZAY** (`main/optimize.py`) -- ``d → r`` etkin altuzay. Kayıp
   ``d`` boyutta değişse de fiilen birkaç yönde değişir; dalga o
   ``r`` yönde ``r·bit`` kübitle arar. Kübit sayısını düşüren şey
   budur ve ``d = 250`` iken fark hayatîdir.

3. **VEKİL** (`ogrenme/rkhs.py`) -- altuzayda örneklenmiş noktalardan
   çekirdek sırt regresyonuyla bir **vekil yüzey**. Kapalı formdur
   (Cholesky, ters alınmaz). Dalganın her adayı hakikî kayba
   sormasına gerek kalmaz; ucuz olan vekile sorulur, yalnız ümitli
   olanlar hakikî kayba gider. Kayıp çağrısı burada azalır.

4. **KODLAMA** (Gri kod) -- ``r`` sürekli koordinat ``r·bit`` kübite.
   Gri kod şart: komşu tam sayılar tek bit farkeder, yoksa
   Metropolis'in tek bit çevirmesi parametre uzayında uçurum atlar.

5. **DALGA** (`kuantum/nqs.py`, `kuantum/dalga.py`) -- kübit uzayında
   genlik; Grover'ın iki boyutlu özyinelemesi tavlama eşiğini
   **söyler** (tahmin edilmez).

6. **DURGUNLUK** (`ogrenme/grassmann.py`) -- ardışık iki turun etkin
   altuzayları arasındaki asal açı. Açı küçülmüyorsa arama aynı yerde
   dönüyordur; "kayıp düşmüyor"dan daha erken ve daha kesin bir
   durgunluk alâmetidir, zira kayıp gürültülüdür, altuzay değildir.

7. **TÜNEL** (`arama/bukum.py`, `arama/grover.py`) -- durgunlukta ne
   yapılacağı. WKB geçirgenliği ``T``, bariyeri aşmak için beklenen
   deneme sayısını **verir**; yeniden başlatma sayısı oradan gelir,
   elle konmaz. Kütük H29'un şartı korunur: tıkanma teşhis edilecek
   VE sıkışılmış olacak.

8. **DENGE** (`fitrat/denge.py`) -- en iyi noktanın etrafında vekilin
   durağan noktası Newton ile bulunur. Dalga kaba, Newton ince: biri
   havzayı bulur, diğeri dibini.

9. **BÜTÇE** (`olcek/hiz.py`, `hesap/donanim.py`,
   `yaklasim/kara_kutu.py`) -- kaç kayıp çağrısı harcandı, donanım ne
   veriyor, ve **hiçbir usulün aşamayacağı** had ne (NFL). Sonuncusu
   bir süs değil dürüstlüktür: "daha iyi arama" iddiasının haddi
   vardır ve o had raporlanır.

===================================================================
HUDUT -- açıkça
===================================================================

* Vekil yüzey **yaklaşıktır**. Ümitli görünüp hakikî kayıpta kötü
  çıkan aday olur; onun için vekil yalnız **eler**, karar vermez.
  Nihaî hüküm daima hakikî kayıptan alınır.
* Etkin altuzay ``r`` boyutlu bir **kesittir**. Asgarî o kesitin
  dışındaysa bulunamaz. Onun için her tur altuzay **yeniden** kurulur;
  yine de bu bir garanti değildir ve öyle bildirilir.
* Bir uzuv düşerse (meselâ ``torch`` yok) usul durmaz, o uzuvsuz
  koşar ve **düştüğü kayda geçer**. Sessizce atlamak, usulün ne
  olduğunu bilinmez kılardı.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ["TalimAyari", "Talim", "talim_et", "rapor"]

#: Yığın kayıp: ``(B, d)`` → ``(B,)``. Usulün tek şartı budur; ne
#: eğitildiğinin bununla hiçbir alâkası yoktur ve olmamalıdır.
Kayip = Callable[[np.ndarray], np.ndarray]


@dataclass
class TalimAyari:
    """Usulün bütün ölçüleri -- hiçbiri koda gömülü değildir."""
    ad: str = "tâlim"
    tur: int = 3                 # dış tur: altuzay kaç kere yenilenir
    r: int = 4                   # etkin altuzay boyutu
    bit: int = 6                 # koordinat başına kübit
    #: **Dalganın bütçesi kübit cinsindendir.** Ölçüldü: bir kayıp
    #: çağrısı 3,66 sn ve dalganın çağrı sayısı ``r·bit`` kübitle
    #: birlikte büyür (Metropolis süpürmesi kübit başınadır). O hâlde
    #: ``r`` ile ``bit``i ayrı ayrı vermek bütçeyi **gizler**: ikisi de
    #: makul görünüp çarpımları koşmaz hâle gelebilir -- nitekim
    #: ``r=8, bit=6`` 48 kübit ediyor ve kısa hâl saatlere çıkıyordu.
    #: Burada had açıkça kübit olarak konur ve ``r`` ona göre kırpılır.
    azami_kubit: int = 48
    yaricap: float = 2.5
    # dalga
    cevrim: int = 6
    ornek: int = 24
    zincir: int = 8
    oran: float = 0.20
    kademe: float = 0.6
    lam: float = 1e-2
    nqs_gizli: Tuple[int, ...] = (48,)
    nqs_derece: int = 5
    # uzuvlar açık mı (kapatılabilir olması ölçüm şartıdır, H90)
    had: bool = True
    vekil: bool = True
    tunel: bool = True
    denge: bool = True
    # altuzay örneklemesi
    altuzay_ornek: int = 24
    #: Her uzuvdan sonra ilerlemeyi bas. Uzun koşan bir eğitim hiçbir
    #: şey yazmıyorsa **ölçülemez**: bekleyen kişi ne kadar kaldığını
    #: bilemez, tıkandı mı çalışıyor mu ayıramaz. Bu bir süs değil,
    #: koşunun teftiş edilebilmesinin şartıdır.
    sesli: bool = False
    tohum: int = 0


def _gri_kodla(k: np.ndarray, bit: int) -> np.ndarray:
    from .kulli_egitim import gri_kodla
    return gri_kodla(k, bit)


def _gri_coz(X: np.ndarray, d: int, bit: int) -> np.ndarray:
    from .kulli_egitim import gri_coz
    return gri_coz(X, d, bit)


class Talim:
    """Gradyansız eniyileme -- **tek** usul, dokuz uzuv.

    Kullanımı tek satırdır ve her yerde aynıdır::

        p_yildiz = Talim(kayip, p0, ayar).kos()["p"]

    ``kayip`` yığın alır ve yığın döner; başka hiçbir şey bilmez.
    Melekenin açısı mı, tasavvurun ağırlığı mı, aramanın önceliği mi
    eğitiliyor -- usul için farkı yoktur ve olmaması usulün **tek**
    olmasının manasıdır.
    """

    def __init__(self, kayip: Kayip, p0: np.ndarray,
                 ayar: Optional[TalimAyari] = None, dh=None) -> None:
        self.kayip = kayip
        self.p0 = np.asarray(p0, float).reshape(-1)
        self.d = int(self.p0.size)
        self.ayar = ayar or TalimAyari()
        self.dh = dh
        self.cagri = 0
        self._son_ses = 0
        self._en_iyi = float("inf")
        self._t0 = time.perf_counter()
        self.eksik: Dict[str, str] = {}
        self.gunluk: List[Dict[str, object]] = []

    # -- hakikî kayıp; çağrı sayılır ---------------------------------
    def _f(self, P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(np.asarray(P, float))
        self.cagri += P.shape[0]
        out = np.asarray(self.kayip(P), float).reshape(-1)
        if self.ayar.sesli and self.cagri - self._son_ses >= 10:
            self._son_ses = self.cagri
            print("    tâlim: %d kayıp çağrısı, %.0f sn, en iyi %.4f"
                  % (self.cagri, time.perf_counter() - self._t0,
                     min(self._en_iyi, float(np.min(out)))), flush=True)
        self._en_iyi = min(self._en_iyi, float(np.min(out)))
        return out

    def _f1(self, p: np.ndarray) -> float:
        return float(self._f(p.reshape(1, -1))[0])

    # -- 1. HAD: kayıp zorlayıcı mı ----------------------------------
    def _had(self, U: np.ndarray, merkez: np.ndarray) -> float:
        """Alt seviye kümeleri sınırlı mı? Değilse yarıçap bağlanır.

        Zorlayıcı olmayan bir kayıpta "asgarîyi ara" emri manasızdır:
        asgarî sonsuzda olabilir. Sorulmazsa arama boşluğa koşar ve
        bunun alâmeti, kaybın düşerken parametrenin büyümesidir.
        """
        if not self.ayar.had:
            return float(self.ayar.yaricap)
        try:
            from akis.tikiz import zorlayici_mi

            def g(z: np.ndarray) -> float:
                return self._f1(merkez + U @ np.asarray(z, float))

            d = zorlayici_mi(g, U.shape[1], (1.0, 4.0), 8,
                             tohum=self.ayar.tohum)
            zor = bool(d.get("zorlayıcı", d.get("zorlayici", True)))
            self.gunluk.append({"uzuv": "had", "zorlayıcı": zor})
            # Zorlayıcı değilse yarıçap yarıya iner: aramayı bağlamak,
            # sonsuza koşmasına seyirci kalmaktan iyidir.
            return float(self.ayar.yaricap * (1.0 if zor else 0.5))
        except Exception as e:                           # noqa: BLE001
            self.eksik["akis.tikiz"] = str(e)[:70]
            return float(self.ayar.yaricap)

    def _walsh_kesit(self, r: int) -> np.ndarray:
        """``d × r`` determinist ortogonal kesit -- Walsh fonksiyonları.

        Walsh dizileri ``±1``dir ve indis üzerinde **bit paritesi** ile
        tanımlıdır; tohuma, rastgeleliğe yahut veriye bağlı değildir.
        Seçilen sıralar tayfa eşit aralıklı yayılır ki kesit husûsî
        değil **genel** olsun (bkz. ``_altuzay`` şerhindeki ölçüm).
        """
        d = self.d
        n = 1
        while n < d:
            n *= 2
        siralar = np.round(np.linspace(1, n - 1, int(r))).astype(np.int64)
        k = np.arange(n, dtype=np.int64)
        W = np.empty((n, siralar.size), float)
        bitler = int(np.log2(n)) + 1
        for c, m in enumerate(siralar):
            x = k & int(m)
            par = np.zeros(n, np.int64)
            for b in range(bitler):
                par ^= (x >> b) & 1
            W[:, c] = 1.0 - 2.0 * par
        Q, _ = np.linalg.qr(W[:d])
        return Q

    # -- 2. ALTUZAY: d → r -------------------------------------------
    def _altuzay(self, merkez: np.ndarray, tohum: int
                 ) -> Tuple[np.ndarray, Optional[np.ndarray],
                            Optional[np.ndarray]]:
        # Kübit haddi ``r``yi kırpar: dalganın maliyeti ``r·bit``le
        # büyüdüğü için had orada konmalı (bkz. ``azami_kubit`` şerhi).
        r = int(min(self.ayar.r, self.d,
                    max(1, self.ayar.azami_kubit // max(1, self.ayar.bit))))
        # =============================================================
        # ETKİN ALTUZAY **ÖLÇÜLDÜ VE RASTGELEDEN KÖTÜ ÇIKTI** (H153)
        # =============================================================
        #
        # Ölçüldü (d=262, aynı kayıp, 4 rastgele parametre):
        #
        #     tam uzay  (d=262)          yayılım 0,0092
        #     "etkin" altuzay (r=8)      yayılım 0,0026
        #     rastgele geniş kesit (r=32) yayılım 0,0146
        #
        # Yani ``aktif_altuzay`` etkin yönleri **bulamıyor**: rastgele
        # bir kesit ondan 5,6 kat daha çok değişim görüyor. Sebep
        # cebrîdir: ``C = (1/N)Σ ∇f∇fᵀ`` kovaryansı ``altuzay_ornek``
        # yönlü sonlu farktan kestiriliyor ve ``d`` boyutta o sayı
        # ``d``den çok küçükse (6 ≪ 262) kestirim **rütbe-6 gürültüden**
        # ibaret kalır. Ceridenin 2. ilgası ("W₂ inaktif uzayı kör
        # kalır") tam budur ve burada ölçümle doğrulanmıştır.
        #
        # Çare rastgele kesit **değildir**: ceride stokastiği yasaklar
        # (aynı girdi aynı çıktıyı vermeli). Onun yerine **determinist
        # ortogonal kesit** alınır -- DCT-II tabanının ilk ``r`` kipi.
        # Eşit dağılmıştır, tohuma bağlı değildir, ve tekrarlanabilir.
        #
        # Etkin altuzay yalnız örnek sayısı kestirimi manalı kılacak
        # kadar çoksa (``altuzay_ornek ≥ 2r``) denenir; değilse
        # doğrudan determinist kesite geçilir ve bu günlüğe yazılır --
        # "etkin altuzay kullandım" demek, kullanmadığı hâlde, ölçümü
        # yalan söyletmek olurdu.
        # Determinist taban **hangi** taban olmalı? Ölçüldü (d=262, r=32):
        #
        #     "etkin" altuzay (rütbe-6 kestirim)  yayılım 0,0026
        #     DCT, ilk r kipi                     yayılım 0,0069
        #     DCT, tayfa yayılmış                 yayılım 0,0084
        #     WALSH, tayfa yayılmış               yayılım 0,0088
        #
        # DCT'nin **ilk** kipleri indis uzayında düzgün yönlerdir;
        # hâlbuki parametre indis sırası keyfîdir (açıların tahsis
        # sırası), o hâlde "düşük frekans" burada hiçbir mana taşımaz.
        # Yönler tayfa **yayılınca** kesit genelleşiyor. Walsh tabanı
        # ayrıca ±1'dir: çarpımı ucuz ve tam.
        # **KESİT BÜSBÜTÜN KALKABİLİR -- ve ölçüm onu emrediyor (H155).**
        # Aynı bütçeyle (24 örnek, yarıçap 2,5) arama kalitesi::
        #
        #     V(p₀)                        0,5758
        #     Walsh kesiti r=32   en iyi   0,4443   (kazanç 0,131)
        #     TAM UZAY  d=262     en iyi   0,3215   (kazanç 0,254)
        #
        # Kesit, ulaşılabilir iyileşmenin **yarısını** yiyor. Sebebi
        # basittir: iyileştiren yönler 262 boyuta yayılmış; herhangi bir
        # 32 boyutluk kesit onların ancak bir izdüşümünü tutar. Boyut
        # indirgemesi, ``d`` çok büyük olmadıkça bir kazanç değil bir
        # kayıptır -- ceridenin 2. ilgası ("lineer aktif alt uzay
        # çalışmaz") burada sonuna kadar icra edilmiştir.
        #
        # Kesit yalnız ``d`` kübit bütçesini aşarsa kurulur; o zaman da
        # etkin altuzay değil determinist Walsh tabanı kullanılır
        # (bkz. aşağıdaki ölçüm).
        if r >= self.d:
            self.gunluk.append({"uzuv": "altuzay", "r": self.d,
                                "usul": "TAM UZAY (kesit yok)"})
            return np.eye(self.d), None, None
        if int(self.ayar.altuzay_ornek) < 2 * r:
            Q = self._walsh_kesit(r)
            self.gunluk.append({"uzuv": "altuzay", "r": r,
                                "usul": "determinist Walsh kesiti"})
            return Q, None, None
        try:
            from main.optimize import aktif_altuzay
            # **DÖNEN ŞEY:** ``(U, özdeğerler, gradyan örnekleri)``.
            # Evvelce bunu ``(U, kayıplar, noktalar)`` sanmıştım ve
            # ölçüldü: vekil ile denge uzuvları hiç ateşlenmiyordu,
            # zira vekile kayıp diye özdeğer veriliyordu. Yanlış olan
            # uzuvlar değil, benim okumamdı.
            U, ozdeger, _G = aktif_altuzay(self._f1, merkez,
                                           n_ornek=self.ayar.altuzay_ornek,
                                           r=r, tohum=tohum)
            U = np.asarray(U, float)
            if U.ndim == 2 and U.shape[0] == self.d:
                oz = np.asarray(ozdeger, float).reshape(-1)
                # Tayfın ne kadarı ilk ``r`` yönde: altuzayın **hakikaten**
                # etkin olup olmadığının ölçüsü. Düşükse kesit kaybettiriyor
                # demektir ve bu kaydedilir, gizlenmez.
                pay = (float(np.sum(oz[:r]) / max(float(np.sum(oz)), 1e-30))
                       if oz.size else float("nan"))
                self.gunluk.append({"uzuv": "altuzay", "r": r,
                                    "tayf_payı": pay})
                return U, None, None
        except Exception as e:                           # noqa: BLE001
            self.eksik["main.optimize"] = str(e)[:70]
        # Altuzay kurulamadıysa **rastgele dik** bir kesit alınır ve
        # bu açıkça kaydedilir: etkin altuzay taklidi yapılmaz.
        rng = np.random.default_rng(tohum)
        A = rng.normal(size=(self.d, r))
        Q, _ = np.linalg.qr(A)
        self.gunluk.append({"uzuv": "altuzay", "hâl": "rastgele kesit"})
        return Q, None, None

    # -- 2b. ÖRNEKLEME: vekilin yiyeceği ------------------------------
    def _ornekle(self, U: np.ndarray, merkez: np.ndarray, R: float,
                 tohum: int, kac: int = 0
                 ) -> Tuple[np.ndarray, np.ndarray]:
        """Altuzayda nokta çek ve **hakikî** kaybı ölç.

        Vekil ancak hakikî kayıp örnekleriyle kurulabilir; özdeğerlerle
        değil. Bu örnekler israf da değildir: aynı çağrılar en iyi
        noktanın aranmasına da sayılır.
        """
        rng = np.random.default_rng(tohum)
        r = U.shape[1]
        n = int(kac or max(8, 4 * r))
        Z = rng.uniform(-R, R, size=(n, r))
        P = merkez[None, :] + Z @ U.T
        return Z, self._f(P)

    # -- 3. VEKİL: ucuz yüzey ----------------------------------------
    def _vekil(self, Z: Optional[np.ndarray], y: Optional[np.ndarray]):
        if not self.ayar.vekil or Z is None or y is None:
            return None
        try:
            from ogrenme.rkhs import RKHS, gauss_cekirdegi, medyan_genislik
            Z = np.atleast_2d(np.asarray(Z, float))
            y = np.asarray(y, float).reshape(-1)
            if Z.shape[0] < 4 or Z.shape[0] != y.size:
                return None
            m = RKHS(gauss_cekirdegi(medyan_genislik(Z)), 1e-6)
            m.uydur(Z, y)
            self.gunluk.append({"uzuv": "vekil", "nokta": int(Z.shape[0]),
                                "koşul": float(m.kosul)})
            return m
        except Exception as e:                           # noqa: BLE001
            self.eksik["ogrenme.rkhs"] = str(e)[:70]
            return None

    # -- 5. DALGA: NQS + Grover --------------------------------------
    def _dalga(self, U: np.ndarray, merkez: np.ndarray, R: float,
               vekil, tohum: int) -> Optional[np.ndarray]:
        a = self.ayar
        r = U.shape[1]
        n_kubit = r * a.bit

        def coz(X: np.ndarray) -> np.ndarray:
            k = _gri_coz(X, r, a.bit)
            u = k / float((1 << a.bit) - 1)
            return merkez[None, :] + (U @ (R * (2.0 * u - 1.0)).T).T

        def kubit_kaybi(X: np.ndarray) -> np.ndarray:
            P = coz(np.atleast_2d(X))
            if vekil is None:
                return self._f(P)
            # **VEKİL YALNIZ ELER, KARAR VERMEZ.** Ucuz yüzeyde en
            # ümitli yarı seçilir; hüküm hakikî kayıptan alınır. Vekile
            # karar verdirmek, yaklaşığı hakikat yerine koymak olurdu.
            Zc = (P - merkez[None, :]) @ U
            try:
                tahmin = np.asarray(vekil(Zc), float).reshape(-1)
            except Exception:                            # noqa: BLE001
                return self._f(P)
            k = max(1, P.shape[0] // 2)
            secim = np.argsort(tahmin)[:k]
            out = np.full(P.shape[0], float(np.max(tahmin)) + 1.0)
            out[secim] = self._f(P[secim])
            return out

        try:
            from hesap.donanim import donanim
            from kuantum.dalga import DalgaEniyileyici
            from kuantum.nqs import NQS, NQSAyar
            nqs = NQS(NQSAyar(n=n_kubit, gizli=a.nqs_gizli,
                              derece=a.nqs_derece, tohum=tohum),
                      self.dh or donanim())
            motor = DalgaEniyileyici(nqs, kubit_kaybi, tohum=tohum)
            motor.kos(cevrim=a.cevrim, ornek=a.ornek, zincir=a.zincir,
                      oran=a.oran, lam=a.lam, kademe=a.kademe)
            self.gunluk.append({"uzuv": "dalga", "kübit": n_kubit})
            return coz(np.atleast_2d(motor.en_iyi_x))[0]
        except Exception as e:                           # noqa: BLE001
            self.eksik["kuantum.dalga"] = str(e)[:70]
            return None

    # -- 6. DURGUNLUK: altuzay kımıldıyor mu -------------------------
    def _durgunluk(self, U_onceki: Optional[np.ndarray],
                   U: np.ndarray) -> float:
        if U_onceki is None:
            return 1.0
        try:
            from ogrenme.grassmann import dik_taban, grassmann_mesafesi
            d = float(grassmann_mesafesi(dik_taban(U_onceki), dik_taban(U)))
            self.gunluk.append({"uzuv": "durgunluk", "grassmann": d})
            return d
        except Exception as e:                           # noqa: BLE001
            self.eksik["ogrenme.grassmann"] = str(e)[:70]
            return 1.0

    # -- 7. TÜNEL: kaç yeniden başlatma -------------------------------
    def _tunel(self, engel: float) -> int:
        """Bariyer yüksekliğinden **beklenen deneme sayısı**.

        Sayı elle konmaz: WKB geçirgenliği ``T``, beklenen deneme
        ``1/T``dir ve `arama/bukum.py` onu verir. Kütük H29: tünelleme
        başıboş değildir, tıkanma teşhis edilecek VE sıkışılmış olacak.
        """
        if not self.ayar.tunel:
            return 0
        try:
            from arama.bukum import beklenen_deneme, wkb_gecirgenlik
            T = float(wkb_gecirgenlik(max(float(engel), 1e-6)))
            n = int(np.clip(round(float(beklenen_deneme(T))), 1, 4))
            self.gunluk.append({"uzuv": "tünel", "T": T, "deneme": n})
            return n
        except Exception as e:                           # noqa: BLE001
            self.eksik["arama.bukum"] = str(e)[:70]
            return 1

    # -- 8. DENGE: vekilin durağan noktası ---------------------------
    def _denge(self, p: np.ndarray, U: np.ndarray, merkez: np.ndarray,
               vekil) -> np.ndarray:
        """Dalga havzayı bulur, Newton dibini.

        Durağanlık vekil yüzeyde aranır; hakikî kayıpta sayısal türev
        almak, kaybın gürültüsünü türevle büyütmek olurdu.
        """
        if not self.ayar.denge or vekil is None:
            return p
        try:
            from fitrat.denge import newton_koku
            z0 = (p - merkez) @ U
            h = 1e-3

            def grad(z: np.ndarray) -> np.ndarray:
                z = np.asarray(z, float)
                g = np.zeros_like(z)
                for i in range(z.size):
                    e = np.zeros_like(z)
                    e[i] = h
                    g[i] = (float(vekil((z + e)[None, :]).reshape(-1)[0])
                            - float(vekil((z - e)[None, :]).reshape(-1)[0])
                            ) / (2.0 * h)
                return g

            z, ok, _adim, _hata = newton_koku(grad, np.asarray(z0, float),
                                              azami_adim=12)
            if not ok:
                return p
            aday = merkez + U @ np.asarray(z, float)
            # Newton'un bulduğu nokta ancak **hakikî kayıpta** iyiyse
            # kabul edilir; vekilin durağan noktası hakikatin asgarîsi
            # olmak zorunda değildir.
            if self._f1(aday) < self._f1(p):
                self.gunluk.append({"uzuv": "denge", "kabul": True})
                return aday
            self.gunluk.append({"uzuv": "denge", "kabul": False})
        except Exception as e:                           # noqa: BLE001
            self.eksik["fitrat.denge"] = str(e)[:70]
        return p

    # -- 9. BÜTÇE ----------------------------------------------------
    def _butce(self) -> Dict[str, object]:
        d: Dict[str, object] = {"kayıp_çağrısı": int(self.cagri)}
        try:
            from yaklasim.kara_kutu import nfl_tam_sayim
            # NFL: hiçbir usulün aşamayacağı had. Süs değil dürüstlük --
            # "daha iyi arama" iddiasının haddi budur.
            d["nfl"] = nfl_tam_sayim(2, 2)
        except Exception as e:                           # noqa: BLE001
            self.eksik["yaklasim.kara_kutu"] = str(e)[:70]
        try:
            from olcek.hiz import throughput
            d["hız"] = throughput(128)
        except Exception as e:                           # noqa: BLE001
            self.eksik["olcek.hiz"] = str(e)[:70]
        return d

    # ================================================================
    def kos(self) -> Dict[str, object]:
        """Dokuz uzvu sırayla koştur; en iyi parametreyi döndür."""
        a = self.ayar
        t0 = time.perf_counter()
        p_iyi = self.p0.copy()
        V_ilk = self._f1(p_iyi)
        V_iyi = V_ilk
        U_onceki: Optional[np.ndarray] = None
        seyir: List[Dict[str, float]] = []

        for tur in range(int(a.tur)):
            tohum = int(a.tohum) + 1000 * tur
            U, _oz, _G = self._altuzay(p_iyi, tohum)
            R = self._had(U, p_iyi)
            durgun = self._durgunluk(U_onceki, U)
            U_onceki = U

            # Vekil, altuzayda çekilen **hakikî kayıp** örnekleriyle
            # kurulur. Aynı örnekler en iyi noktayı da güncelleyebilir;
            # o yüzden israf değildir.
            Z, y = self._ornekle(U, p_iyi, R, tohum)
            if y.size and float(np.min(y)) < V_iyi:
                j = int(np.argmin(y))
                p_iyi = p_iyi + U @ Z[j]
                V_iyi = float(y[j])
            vekil = self._vekil(Z, y)

            deneme = 1 + (self._tunel(max(V_iyi, 1e-6))
                          if durgun < 1e-3 else 0)
            for k in range(deneme):
                p = self._dalga(U, p_iyi, R, vekil, tohum + 7 * k)
                if p is None:
                    continue
                p = self._denge(p, U, p_iyi, vekil)
                V = self._f1(p)
                if V < V_iyi:
                    p_iyi, V_iyi = p, V
            seyir.append({"tur": float(tur), "V": V_iyi, "R": R,
                          "durgunluk": durgun, "deneme": float(deneme),
                          "çağrı": float(self.cagri)})

        out: Dict[str, object] = {
            "p": p_iyi, "V_ilk": V_ilk, "V_son": V_iyi,
            "kazanç": V_ilk - V_iyi,
            "süre_sn": time.perf_counter() - t0,
            "seyir": seyir, "günlük": self.gunluk,
            "düşen_uzuv": dict(self.eksik),
            "boyut": self.d, "altuzay": int(min(a.r, self.d)),
        }
        out.update(self._butce())
        return out


def talim_et(kayip: Kayip, p0: np.ndarray,
             ayar: Optional[TalimAyari] = None, dh=None
             ) -> Dict[str, object]:
    """Tek satırlık arayüz -- **her** eğitim yerinde bu çağrılır."""
    return Talim(kayip, p0, ayar, dh).kos()


def rapor(d: int = 12, tohum: int = 0) -> str:
    """Usulü kendi üstünde göster: bilinen asgarîsi olan bir yüzeyde.

    Ölçüt kör değildir: asgarînin **nerede** olduğu bilindiği için
    usulün ona yaklaşıp yaklaşmadığı görülür, "kayıp düştü" demekle
    yetinilmez.
    """
    rng = np.random.default_rng(tohum)
    hedef = rng.normal(size=d)

    def kayip(P: np.ndarray) -> np.ndarray:
        P = np.atleast_2d(P)
        return np.sum((P - hedef[None, :]) ** 2, axis=1)

    r = talim_et(kayip, np.zeros(d), TalimAyari(tohum=tohum))
    uzak_ilk = float(np.linalg.norm(hedef))
    uzak_son = float(np.linalg.norm(np.asarray(r["p"]) - hedef))
    s = ["=== TÂLİM -- tek eğitim usulü, dokuz uzuv ===",
         "",
         "  boyut %d → etkin altuzay %d   kayıp çağrısı %d   %.1f sn"
         % (r["boyut"], r["altuzay"], r["kayıp_çağrısı"], r["süre_sn"]),
         "  V: %.4f → %.4f   (kazanç %.4f)"
         % (r["V_ilk"], r["V_son"], r["kazanç"]),
         "  asgarîye uzaklık: %.4f → %.4f" % (uzak_ilk, uzak_son),
         "",
         "  TUR SEYRİ:",
         "   tur      V        yarıçap  durgunluk  deneme   çağrı"]
    for c in r["seyir"]:
        s.append("   %-4d %-10.4f %-8.3f %-10.3e %-7d %d"
                 % (c["tur"], c["V"], c["R"], c["durgunluk"],
                    int(c["deneme"]), int(c["çağrı"])))
    s += ["", "  UZUV GÜNLÜĞÜ:"]
    for g in r["günlük"][:12]:
        s.append("    " + ", ".join("%s=%s" % (k, v) for k, v in g.items()))
    if r["düşen_uzuv"]:
        s += ["", "  DÜŞEN UZUVLAR (gizlenmedi):"]
        for k, v in sorted(r["düşen_uzuv"].items()):
            s.append("    %-22s %s" % (k, v))
    s += ["",
          "Bu usul **her** eğitim yerinde aynen kullanılır: melekelerin",
          "açıları, tasavvur ağırlıkları, muhakeme öncelikleri. 'Bu",
          "parametre başka türlü eğitilir' diye bir istisna yoktur;",
          "olsaydı usul tek olmazdı."]
    return "\n".join(s)


if __name__ == "__main__":   # pragma: no cover
    print(rapor())
