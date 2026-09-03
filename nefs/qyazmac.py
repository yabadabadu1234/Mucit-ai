"""
Ana modelin kübit yazmacı -- ``S`` diye ayrı bir reel hâl YOKTUR.

Nefsin bir andaki bütün hâli tek bir kuantum durumudur. ``main/`` ile
aynı yazmaç kullanılır (``main.yazmac.Yazmac``); iki model aynı fiziği
paylaşır, bu bir tekrar değil **tek nüshadır**.

Zincir düzeni (kullanıcı hükmü: "ikisi birden")::

    [sat0 veri × k][sat0 yerel h.] [sat1 veri × k][sat1 yerel h.] …
      … [satN-1 veri × k][satN-1 yerel h.]  [ K Ü L L Î   H Ü K Ü M ]

* **veri kübitleri** -- ham duyunun kübitlere kodlanmış hâli.
* **yerel hüküm kübiti** -- o satır hakkındaki hüküm (bu şahit nakzedildi
  mi, bu satır kusurlu mu). Satırın **bitişiğindedir**, dolayısıyla ona
  dokunan kapı yereldir ve ucuzdur.
* **küllî hüküm bloğu** -- zincirin sonunda: makam(2), mîzân(4),
  tenakuz(2), tasdik(2), sükût(1), nakz(2), **kelam(4)**. Bütünün hükmü
  buradadır.

**Kelam neden ayrı bir alan?** Ölçüldü: 41 meleke koştuktan sonra bir
satırın dört veri kübitinin ortak dağılımı **tam düzgün** çıkıyor
(16 durumun her biri 0.0625). Bu bir kusur değil, dolaşıklığın
tabiatıdır: her şey her şeyle dolaştığında küçük bir bloğun marjinali
âzamî karışıktır. Yani model o kübitlerden **konuşamaz**. Kelam bu
yüzden ayrı, ``|0⟩``da başlayan dört kübittir; beyan melekeleri
(𝒪₃₇–𝒪₄₁) hükmü ve manayı oraya MPO ile akıtır, belirteç oradan okunur.

Yerel hükümler küllî bloğa **tek süpürmeyle** akıtılır
(``main.yazmac.Yazmac.supurme``): naif usulde ``k`` durak × ``D`` mesafe
için ``2kD`` takas, süpürmede ``~2D``. Blok yerine iade edilir; edilmezse
yerellik gider ve takas dolaşıklığı sürükleyip ``χ``yi zorlar.

**MPO'lar ``mpo_uygula_hizli`` ile koşar (kütük H197).** Padişahın
ihtarı yerindeydi: ``kuantum/yazmac.py``e uyarlanabilir zip-up yolunu
kurmuştum fakat **akışa bağlamamıştım**; ana model hâlâ iki geçişli
yavaş yolu çağırıyordu. Bir ``idrak_et`` çağrısında 219 süpürme var ve
her biri o yoldan geçiyordu. Artık üçü de -- ``uzak_cift_mpo``,
``mpo_topla``, ``mpo_dagit`` -- kesmeye bakıp usul seçen hızlı yolu
çağırır; kesme ısırırsa kendiliğinden iki geçişliye döner, yani
doğruluktan taviz yok.

**Hiçbir yerde çöküş yoktur.** Hüküm melekeleri de üniterdir: makam
``|Şek⟩,|Zan⟩,|Yakîn⟩,|Vehim⟩`` taban durumlarına kodlanır ve bir dönme
ile çevrilir. Hükmün sayısı ancak en sonda, POVM zayıf ölçümüyle okunur
(kütük H31).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from kuantum.yazmac import Yazmac, dik_iki_kubit, hadamard

__all__ = ["QAyar", "QYazmac", "donme", "faz_z", "kontrollu_donme",
           "donme_yigin", "kontrollu_donme_yigin", "devret", "MAKAM_ADLARI",
           "MAKAM_ESIKLERI", "makam_merdiveni", "makam_derecesi",
           "makam_mertebeleri", "makam_kubit_manasi"]


def devret(a: np.ndarray, hedef: int) -> np.ndarray:
    """``a``nın **son eksenini** ``hedef`` uzunluğa devrederek uzat.

    ``np.resize`` diziyi DÜZLEŞTİRİP tekrarlar; yığın ekseni varken
    (``(B, n)``) bu, farklı yığın üyelerinin açılarını birbirine
    karıştırır -- sessiz ve öldürücü bir hata. Burada yalnız son eksen
    devreder, yığın ekseni el değmeden kalır.
    """
    a = np.asarray(a)
    n = a.shape[-1]
    if hedef <= 0 or n == 0:
        return a[..., :0]
    return a[..., np.arange(hedef) % n]


def donme_yigin(teta: np.ndarray) -> np.ndarray:
    """``(...,)`` açı → ``(..., 2, 2)`` dönme yığını.

    Tek açı için ``donme`` ile birebir aynıdır; farkı, yığın ekseniyle
    beraber çalışmasıdır. Melekeler ``np.stack([donme(float(t)) for t
    in a])`` yazıyordu; o kalıp ``a`` iki boyutlu olunca (parametre
    ekseni) kırılır ve Python döngüsü de cabasıdır.
    """
    t = np.asarray(teta, float)
    c, s = np.cos(t), np.sin(t)
    return np.stack([np.stack([c, -s], axis=-1),
                     np.stack([s, c], axis=-1)], axis=-2)


def kontrollu_donme_yigin(teta: np.ndarray) -> np.ndarray:
    """``(...,)`` açı → ``(..., 4, 4)`` kontrollü dönme yığını."""
    t = np.asarray(teta, float)
    G = np.zeros(t.shape + (4, 4))
    G[..., 0, 0] = 1.0
    G[..., 1, 1] = 1.0
    G[..., 2:, 2:] = donme_yigin(t)
    return G

#: Bilgi mertebeleri, **artan** sırada. Kaynağı `mizan/munazara.py`nin
#: ``MERTEBELER`` cetvelidir ve keyfî değildir.
#:
#: **KÜTÜK H129'UN AÇIK BORCU BURADA KAPANDI.** Makam evvelce **iki**
#: kübitti, yani dört taban durumu, yani dört mertebe -- ve mîzânın
#: cetvelinde **beş** mertebe vardır. Eksik olan ``zann-ı gālib``ti:
#: kuvvetli zan ile kat'î yakîn arasındaki fark, modelin makam
#: yazmacında **temsil edilemiyordu**. "Neredeyse eminim" ile "eminim"
#: aynı taban durumuna düşüyordu.
#:
#: Şimdi makam **üç** kübittir: sekiz konumlu bir merdiven. Beş mertebe
#: bu merdivene eşiklerle oturur (bkz. ``makam_mertebeleri``); merdiven
#: mertebelerden daha ince olduğu için ``zann-ı gālib`` de, iki
#: mertebe arasındaki geçiş de temsil edilebilir.
MAKAM_ADLARI: Tuple[str, ...] = ("Vehim", "Şek", "Zan", "Zann-ı gālib",
                                 "Yakîn")

#: Mertebenin alt eşiği (``mizan.munazara.MERTEBELER`` ile aynı sayılar,
#: fakat artan sırada ve görünen adla). Eşik **dâhildir**.
MAKAM_ESIKLERI: Tuple[float, ...] = (0.00, 0.25, 0.50, 0.75, 1.00)


def makam_merdiveni(kac: int) -> Tuple[int, ...]:
    """Makam yazmacının ``2^kac`` taban durumu, **epistemik sırada**.

    Dönen dizinin ``k``ıncı ögesi, merdivenin ``k``ıncı basamağındaki
    taban durumunun **indeksi**dir (``blok_dagilimi``in indeks düzeni:
    ilk kübit en anlamlı). Sıra **Gray koddur**: ``g(k) = k ⊕ (k≫1)``.

    **Niçin Gray (kütük H127).** Melekelerin elindeki tek alet tek
    kübitlik (kontrollü) dönmedir. Merdivende komşu iki basamak arasında
    tek kübit farkı yoksa, meleke o geçişi **yapamaz**. Evvelki
    ``("Şek","Zan","Yakîn","Vehim")`` sırasında üç geçişin ikisi Hamming
    2 idi; 𝒪₃₂ Zan'dan Yakîn'e hiç geçiremiyordu. Gray kodda **her**
    komşuluk Hamming 1'dir ve bu, sınamayla denetlenir.

    Üç kübitte merdiven ``000 001 011 010 110 111 101 100``tür ve
    kübitlerin manası ölçülebilir hâle gelir (bkz. ``makam_kubit_manasi``).
    """
    n = 1 << int(kac)
    return tuple(k ^ (k >> 1) for k in range(n))


def makam_derecesi(kac: int) -> np.ndarray:
    """Merdivenin her **basamağına** düşen yakîn derecesi, ``[0,1]``de.

    ``derece(k) = k / (2^kac − 1)``: en alt basamak 0 (vehm-i mutlak),
    en üst 1 (yakîn-i kat'î), arası düzgün bölünmüş. Basamak sayısı
    mertebe sayısından çok olabilir; olması da matluptur, zira mertebe
    bir **eşiktir**, bir nokta değil.
    """
    n = 1 << int(kac)
    return np.arange(n, dtype=float) / max(n - 1, 1)


def makam_mertebeleri(kac: int) -> Tuple[str, ...]:
    """Her basamağın hangi mertebeye düştüğü -- eşiklerden okunur.

    Eşik **alt sınırdır ve dâhildir** (`mizan/munazara.py` ile aynı
    kaide): derecesi ``d`` olan basamak, ``d``yi aşmayan en yüksek
    eşiğin mertebesindedir. Üç kübitte netice::

        basamak  0    1    2    3    4    5    6      7
        derece   .000 .143 .286 .429 .571 .714 .857  1.000
        mertebe  Vehim Vehim Şek  Şek  Zan  Zan  Zann-ı g.  Yakîn

    Dağılım eşit değildir ve **eşitlenmemiştir**: eşikler mîzânın
    cetvelinden gelir, oraya uydurulmaz. ``Yakîn``in yalnız tek
    basamağı olması cetvelin kendi hükmüdür -- *"kat'î; aksi muhal"*.
    """
    d = makam_derecesi(kac)
    out: List[str] = []
    for x in d:
        i = 0
        for j, e in enumerate(MAKAM_ESIKLERI):
            if x + 1e-12 >= e:
                i = j
        out.append(MAKAM_ADLARI[i])
    return tuple(out)


def makam_kubit_manasi(kac: int) -> Dict[int, Tuple[int, ...]]:
    """Her makam kübiti ``|1⟩`` iken merdivenin hangi basamakları açık.

    **İddia edilmez, hesaplanır.** Üç kübitte netice şudur ve manası
    şerhte değil burada durur::

        kübit 0 → basamak 4,5,6,7   = üst yarı  (Zan ve üstü)
        kübit 1 → basamak 2,3,4,5   = orta dörtlü (kararsızlık kuşağı)
        kübit 2 → basamak 1,2,5,6   = ara basamaklar (ince ayar)

    Yani ``makam₀`` hükmün **cihetidir**, ``makam₁`` kararsızlık
    kuşağıdır, ``makam₂`` ince ayardır. 𝒪₃₂ açılarını buna göre
    yöneltir; sınama bu tabloyu fiilen denetler.
    """
    merd = makam_merdiveni(kac)
    out: Dict[int, Tuple[int, ...]] = {}
    for b in range(int(kac)):
        vurgu = 1 << (int(kac) - 1 - b)          # ilk kübit en anlamlı
        out[b] = tuple(k for k, idx in enumerate(merd) if idx & vurgu)
    return out


def donme(teta: float) -> np.ndarray:
    """``R(θ) = [[cos,−sin],[sin,cos]]`` -- reel tek kübitlik dönme.

    Reel cebirde faz işarettir (bkz. ``kuantum/yazmac.py``); ``e^{iθ}``
    yerine ``SO(2)`` dönmesi taşınır. Dik olduğu için normu korur.
    """
    c, s = math.cos(float(teta)), math.sin(float(teta))
    return np.array([[c, -s], [s, c]], dtype=np.float64)


def faz_z() -> np.ndarray:
    """``σ_z`` -- işaret çevirme. Yıkıcı girişimi kuran kapı."""
    return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.float64)


def degil_x() -> np.ndarray:
    """``σ_x`` -- ``|0⟩ ↔ |1⟩``. Menfî kontrolü kurmak için sarmalayıcı.

    Reel yazmaçta ``X`` bir **permütasyondur**; karmaşık faza ihtiyaç
    duymaz ve olduğu gibi tatbik edilir (kütük H98). Menfî kontrollü bir
    kapı, kontrol kübitini ``X`` ile sarmakla kurulur::

        X_c · CU(c,t) · X_c   ≡   kontrol |0⟩ iken uygulanan kapı
    """
    return np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.float64)


def kontrollu_donme(teta: float) -> np.ndarray:
    """``CR(θ)``: kontrol ``|1⟩`` iken hedefe ``R(θ)``.

    İki kübitlik indeks düzeni ``2i+j``dir (``i`` kontrol, ``j`` hedef) --
    ``main.yazmac._cift_kapi_dilim``deki düzenle aynı. Dik bir dizeydir;
    dolayısıyla dolaşıklığı kurar ve normu korur.
    """
    R = donme(teta)
    G = np.eye(4, dtype=np.float64)
    G[2:, 2:] = R
    return G


@dataclass
class QAyar:
    """Yazmacın bütün ölçüleri -- hiçbiri koda gömülü değildir.

    Varsayılan **küçük** tutulur (kullanıcı hükmü): akış saniyeler içinde
    bitsin, her melekenin doğru çalıştığı ölçülebilsin. Kapasite ayrı
    ölçülür; ``main/`` onu 6 000 000 kübitte zaten ölçtü.
    """
    satir_kubiti: int = 4          # bir satır kaç veri kübitine kodlanır
    yerel_kubit: int = 1           # satır başına yerel hüküm kübiti
    bag: int = 8                   # χ
    mera_kademe: int = 3
    tohum: int = 0
    obek: int = 150_000
    #: Yığın büyüklüğü ``B = P·V`` (parametre × veri). 1 = tek durum.
    yigin: int = 1
    #: Küllî hüküm bloğunun alanları ve kaç kübit tuttukları.
    kulli_alanlar: Tuple[Tuple[str, int], ...] = (
        # ``makam`` 2 değil **3** kübittir (kütük H129'un kapanan borcu):
        # mîzânın cetvelinde beş mertebe var, dört taban durumu onları
        # taşıyamıyordu ve ``zann-ı gālib`` temsil edilemiyordu.
        ("makam", 3), ("mizan", 4), ("tenakuz", 2),
        ("tasdik", 2), ("sukut", 1), ("nakz", 2), ("kelam", 4),
        # --- kütük H91: kâide yazmacı ve orak kübiti.
        # ``kaide`` kâidenin İNDİSİNİ değil PARAMETRESİNİ tutar
        # (p, q, r; her biri ``kaide_bit`` bit). ``orak`` tek bir
        # yardımcı kübittir: şart sağlanan kolda hiç kımıldamaz,
        # sağlanmayan her kolda genlik sızdırır (bkz. nefs/qkaide.py).
        ("kaide", 12), ("orak", 1),
        # --- kütük H108: GAYE alanı (Dosya 7).
        # H105'te hüküm alanları YAPISIZ ölçüldü. Dosya 7'nin teşhisi:
        # teleolojik çekici (gaye) olmadan serbest enerji gradyanı
        # yönsüz kalır. Alan buraya konur ve hükümle DOLAŞTIRILIR;
        # hiçbir yerde okunmaz.
        ("gaye", 2),
        # --- kütük H109: TERTİP yazmacı (Dosya 8).
        # Her kübit bir mantık usulüne aittir ve SÜPERPOZİSYONDADIR:
        # usul hem denenir hem denenmez, hangisinin işe yaradığını
        # girişim tayin eder ("kalp seçmez, dolaştırır" -- H102).
        ("tertip", 4),
    )
    #: ``kaide`` alanındaki her parametrenin bit sayısı (p, q, r).
    kaide_bit: int = 4
    #: --- ceride taksimatı (H173). Zincire ``meleke``, ``parametre`` ve
    #: ``ancilla`` bölgeleri **eklenir**; ayrı bir model kurulmaz.
    #: Ölçüleri ``nefs.taksimat.CERIDE_TAKSIMAT`` nispetlerinden, veri
    #: bölgesine oranla çıkar. Kapatmak bir seçenektir fakat kapalıyken
    #: model ceridenin şemasına uymaz ve ``eklem_olcusu`` bunu görür.
    bolge_ac: bool = True
    #: Her bölgeye düşecek asgari kübit (nispet sıfıra yuvarlanmasın).
    bolge_asgari: int = 1

    @property
    def kulli_kubit(self) -> int:
        return sum(n for _, n in self.kulli_alanlar)

    def veri_kubiti(self, n_satir: int) -> int:
        return n_satir * (self.satir_kubiti + self.yerel_kubit)

    def bolge_olculeri(self, n_satir: int) -> Dict[str, int]:
        """Ceride nispetiyle bölge ölçüleri -- veri bölgesine oranla.

        Ceride ``veri = 2²³``, ``parametre = 2²¹``, ``meleke = 2¹⁹``,
        ``ancilla = 22.000.000 − ötekiler`` der. Nispetler veri'ye
        bölünerek ölçekten arındırılır: parametre veri'nin ¼'ü, meleke
        1/16'sı, ancilla 1,31 katıdır. Sayılar burada **hesaplanır**,
        elle yazılmaz.
        """
        from nefs.taksimat import CERIDE_TAKSIMAT
        v = self.veri_kubiti(n_satir)
        out: Dict[str, int] = {"veri": v, "hukum": self.kulli_kubit}
        if not self.bolge_ac:
            for ad in ("meleke", "parametre", "ancilla"):
                out[ad] = 0
            return out
        taban = CERIDE_TAKSIMAT["veri"]
        for ad in ("meleke", "parametre", "ancilla"):
            oran = CERIDE_TAKSIMAT[ad] / taban
            out[ad] = max(int(self.bolge_asgari), int(round(oran * v)))
        return out

    def kubit_sayisi(self, n_satir: int) -> int:
        return sum(self.bolge_olculeri(n_satir).values())


@dataclass
class QIz:
    """Bir kübit akışının icra izi -- nizamnamenin 5. kademesi."""
    kubit: int = 0
    satir: int = 0
    durum_bayt: int = 0
    mera_kademe: int = 0
    mera_kesme: float = 0.0
    entropi_once: float = 0.0
    entropi_sonra: float = 0.0
    schmidt: int = 1
    schmidt_once: int = 1
    norm_hatasi: float = 0.0
    kapi: int = 0
    takas: int = 0
    kesme: float = 0.0
    #: **HAKİKÎ kesme** -- ``1 − ⟨Ψ|Ψ⟩``, yani atılan ağırlığın kendisi.
    #: ``[0,1]`` aralığındadır ve kıyas edilebilir.
    #:
    #: ``kesme`` alanı, kapı başına NİSPÎ atılanların **toplamıdır**;
    #: kapı sayısı ve ölçüsü değiştikçe kıyas edilemez hâle gelir ve
    #: 1'i aşar. Ölçüldü (H111): χ 8→16→32 büyütülünce 18→28→31'e
    #: ÇIKIYORDU, halbuki azalması gerekirdi. O sayı bir ölçüt değildir;
    #: teşhis için tutulur, hüküm için **bu** kullanılır.
    kesme_hakiki: float = 0.0
    supurme: int = 0
    gunluk: List[str] = field(default_factory=list)

    def not_dus(self, meleke: str, mesaj: str) -> None:
        self.gunluk.append("%-24s %s" % (meleke, mesaj))


class QYazmac:
    """Nefsin bütün hâli: tek kuantum durumu, üniter melekeler."""

    def __init__(self, n_satir: int, ayar: Optional[QAyar] = None) -> None:
        self.ayar = ayar or QAyar()
        a = self.ayar
        self.n_satir = int(n_satir)
        self.oge = a.satir_kubiti + a.yerel_kubit        # satır başına kübit
        self.n = a.kubit_sayisi(self.n_satir)
        self.y = Yazmac(self.n, bag=a.bag, tohum=a.tohum, obek=a.obek,
                        yigin=a.yigin)
        self.iz = QIz(kubit=self.n, satir=self.n_satir,
                      durum_bayt=self.y.bayt)
        # küllî bloğun alan adresleri (blok başına göre kayma)
        self.kulli_bas = self.n_satir * self.oge
        self._alan: Dict[str, Tuple[int, int]] = {}
        k = 0
        for ad, kac in a.kulli_alanlar:
            self._alan[ad] = (self.kulli_bas + k, kac)
            k += kac
        # --- ceride taksimatı (H173): meleke / parametre / ancilla
        # bölgeleri **aynı zincirin** devamıdır. Ayrı bir yazmaç, ayrı
        # bir durum, ayrı bir model YOKTUR; ``self.y`` tektir.
        from nefs.taksimat import Taksimat
        self.taksimat = Taksimat.kur(a.bolge_olculeri(self.n_satir))
        if self.taksimat.n != self.n:                     # sessiz kayma freni
            raise AssertionError("taksimat %d, zincir %d"
                                 % (self.taksimat.n, self.n))

    # -----------------------------------------------------------------
    #  Adresler
    # -----------------------------------------------------------------
    def veri(self, i: int, j: int = 0) -> int:
        """``i``inci satırın ``j``inci veri kübitinin zincir yeri."""
        return i * self.oge + j

    def yerel(self, i: int) -> int:
        """``i``inci satırın yerel hüküm kübitinin zincir yeri."""
        return i * self.oge + self.ayar.satir_kubiti

    def kulli(self, ad: str, j: int = 0) -> int:
        """Küllî hüküm bloğundaki ``ad`` alanının ``j``inci kübiti."""
        bas, kac = self._alan[ad]
        return bas + (int(j) % kac)

    def yereller(self) -> List[int]:
        return [self.yerel(i) for i in range(self.n_satir)]

    # -- ceride bölgeleri (H173): |x⟩ parametre, |m⟩ meleke, |a⟩ ancilla
    def parametre(self, j: int = 0) -> int:
        """``|x⟩`` bölgesinin ``j``inci kübiti -- model ağırlığı θ."""
        return self.taksimat.yer("parametre", j)

    def meleke_kubiti(self, j: int = 0) -> int:
        """``|m⟩`` bölgesinin ``j``inci kübiti -- hangi uzuv uyanık."""
        return self.taksimat.yer("meleke", j)

    def ancilla(self, j: int = 0) -> int:
        """``|a⟩`` bölgesinin ``j``inci kübiti -- QSVT/FPAA iş alanı."""
        return self.taksimat.yer("ancilla", j)

    def bolge_var(self, ad: str) -> bool:
        return self.taksimat.bolge.get(ad, (0, 0))[1] > 0

    def eklem_olcusu(self, pencere: Optional[int] = None) -> Dict[str, object]:
        """Bölge sınırlarındaki dolaşıklık -- **eklem var mı**.

        Kullanıcı hükmü: *"tek ve paralel olmayan, yek vücut çok uzuvlu
        bir model"*. Bu ölçü onu denetler ve kırmızıya döner: bir
        sınırda entropi sıfırsa o iki uzuv **iki ayrı modeldir**.
        """
        from nefs.taksimat import eklem_olcusu as _eo
        return _eo(self.y, self.taksimat, pencere=pencere)

    # -----------------------------------------------------------------
    #  Ĥ_Dimağ -- bölgeleri birbirine EKLEMLEYEN operatör
    # -----------------------------------------------------------------
    def dimag(self, teta: Optional[np.ndarray] = None,
              olcek: float = 0.05) -> Dict[str, float]:
        """Ceridenin dimağ operatörünü zincire tatbik et.

        Ceride şöyle yazar::

            Ĥ_Dimağ(θ) = Σ_m Π_koho Π_betti 𝒮_m [Σ_a θ_m^a T^a]
                          𝒮_m† Π_betti Π_koho

        Buradaki iki indis, iki bölgedir: ``m`` **meleke** yazmacının
        kübiti (hangi uzuv uyanık), ``a`` **parametre** yazmacının
        kübiti (o uzvun ağırlığı). ``T^a`` üreteci hükme dokunur.
        Dolayısıyla operatör dört bölgeyi bir zincirde birbirine bağlar
        ve **eklem** tam budur:

            veri → meleke   : hangi satır hangi uzvu uyandırıyor
            meleke → parametre : θ_m^a bağı (m ile a burada buluşur)
            parametre → hüküm  : Σ_a θ^a T^a, üreteç hükme vurur
            parametre → ancilla: iş alanı genliği taşır

        Dört bağın dördü de kontrollü **reel** dönmedir; hiçbiri okumaz,
        hiçbiri çökertmez. Bölgeler kapalıysa (``bolge_ac=False``) bu
        usul sessizce hiçbir şey yapmaz -- ve ``eklem_olcusu`` o zaman
        kırmızı yanar; ikisi birbirini denetler.

        ``teta`` verilmezse açılar sabit ``olcek``tir; öğrenilen θ ile
        çağrılması matluptur (``kulli_egitim`` oradan besler).

        **``olcek`` varsayılanı ölçümle kondu, elle değil.** Dört açı
        (0,05 / 0,15 / 0,35 / 0,785) üç bağda (χ = 8/16/32) koşuldu::

            χ=8   : S her açıda tam ln 8;  kesme 0,087 → 2,158
            χ=16  : S her açıda tam ln 16; kesme 0,184 → 2,620
            χ=32  : S 1,384 → 3,083;       kesme 0,258 → 1,987

        Yani χ ≤ 16'da büyük açı **ölçülebilir hiçbir eklem kazancı
        vermiyor** (entropi zaten tavanda), fakat kesmeyi 25 kat
        artırıyor. Bedava olmayan bir şey karşılığında hiçbir şey almak
        israftır; onun için en küçük açı varsayılandır.
        """
        r: Dict[str, float] = {"kapı": 0.0, "kesme": 0.0}
        if not (self.bolge_var("meleke") and self.bolge_var("parametre")):
            return r
        nm = self.taksimat.bolge["meleke"][1]
        npar = self.taksimat.bolge["parametre"][1]
        t = (np.full(nm * npar, float(olcek)) if teta is None
             else devret(np.asarray(teta, float).ravel(), nm * npar))
        k0 = self.iz.kesme

        # (0) Parametre yazmacı SÜPERPOZİSYONDA olmalıdır. Bu bir süs
        #     değil, ceridenin bütün iddiasının şartıdır: "2²¹ parametre
        #     kübiti" bir θ değerini değil, **bütün θ'ların üst üste
        #     binmiş hâlini" taşır; QSVT Gibbs süzgeci o süperpozisyon
        #     üzerinde çalışır. |0⟩'da bırakılırsa kontrollü dönmelerin
        #     hepsi kimlik olur ve bölge ölü doğar -- eklem ölçüsü de
        #     bunu kırmızı gösterirdi.
        H = hadamard().astype(np.float64)
        self.tek_yigin([self.parametre(a) for a in range(npar)], H)
        # (1) veri → meleke: satırın yerel hükmü uzvu uyandırır.
        for i in range(self.n_satir):
            self.uzak_cift(self.yerel(i), self.meleke_kubiti(i),
                           kontrollu_donme(float(t[i % t.size])))
        # (2) meleke → parametre: θ_m^a. İki indis burada buluşur.
        for m in range(nm):
            for a in range(npar):
                self.uzak_cift(self.meleke_kubiti(m), self.parametre(a),
                               kontrollu_donme(float(t[m * npar + a])))
        # (3) parametre → hüküm: Σ_a θ^a T^a hükme vurur. Hüküm bloğu
        #     parametrenin SOLUNDA olduğu için kontrol sağdadır; kapı
        #     simetrik olmadığından ``uzak_cift`` düzeni kendi korur.
        for a in range(npar):
            self.uzak_cift(self.parametre(a),
                           self.kulli("mizan", a),
                           kontrollu_donme(float(t[a % t.size])))
        # (4) parametre → ancilla: iş alanı. Yoksa atlanır.
        if self.bolge_var("ancilla"):
            na = self.taksimat.bolge["ancilla"][1]
            for a in range(min(npar, na)):
                self.uzak_cift(self.parametre(a), self.ancilla(a),
                               kontrollu_donme(float(t[a % t.size])))
        r["kesme"] = float(self.iz.kesme - k0)
        r["kapı"] = float(self.n_satir + nm * npar + npar
                          + (min(npar, self.taksimat.bolge["ancilla"][1])
                             if self.bolge_var("ancilla") else 0))
        return r

    # -----------------------------------------------------------------
    #  Kodlama
    # -----------------------------------------------------------------
    def kodla(self, E: np.ndarray) -> None:
        """Ham duyuyu veri kübitlerine kodla -- **kayıpsız intibak** (H14).

        Her satırın ``d_in`` boyutlu vektörü ``satir_kubiti`` kübite
        indirilir. Kaba sıfırlama yasaktır; onun yerine satır, kübit
        sayısı kadar **dilime bölünüp** her dilimin ortalaması bir
        açıya çevrilir ve o açı kübite bir dönme olarak yazılır. Böylece
        bilgi atılmaz, açıya sarılır; ölçek ``tanh`` ile sınırlanır ki
        dönme sarmalanıp ayırt edilemez hâle gelmesin.
        """
        E = np.asarray(E, float)
        if E.ndim == 2:
            E = E[None]                       # bütün yığına aynı girdi
        B, n, d = E.shape
        if B != self.y.B and B != 1:
            raise ValueError("girdi yığını %d, yazmaç yığını %d"
                             % (B, self.y.B))
        k = self.ayar.satir_kubiti
        sinir = np.array_split(np.arange(d), k)
        ns = min(n, self.n_satir)
        # **Yığın hâlinde kodlama.** Evvelce ``n·k`` ayrı ``tek`` çağrısı
        # vardı; hepsi tek çağrıya iner ve yığının her üyesi KENDİ
        # girdisini alır (veri ekseni ancak böyle iş görür).
        v = np.stack([E[:, :ns, dil].mean(axis=2) if len(dil)
                      else np.zeros((E.shape[0], ns))
                      for dil in sinir], axis=2)        # (B, ns, k)
        teta = 0.25 * math.pi * (1.0 + np.tanh(v))
        c, sn = np.cos(teta), np.sin(teta)
        G = np.stack([np.stack([c, -sn], axis=-1),
                      np.stack([sn, c], axis=-1)], axis=-2)   # (B,ns,k,2,2)
        G = G.reshape(E.shape[0], ns * k, 2, 2)
        if E.shape[0] == 1 and self.y.B > 1:
            G = np.broadcast_to(G, (self.y.B, ns * k, 2, 2))
        yuv = [self.veri(i, j) for i in range(ns) for j in range(k)]
        self.tek_yigin(yuv, G)

    def superpozisyon(self, yalniz_veri: bool = True) -> None:
        """Hadamard: ``2^N`` taban durumu eşit genlikte.

        ``yalniz_veri`` iken hüküm kübitlerine dokunulmaz: hüküm henüz
        verilmemiştir, ``|0⟩`` (=Şek, mîzân sıfır) doğru başlangıçtır.
        Hepsine vurmak, daha hiçbir delil görülmeden bütün hükümleri
        eşit ihtimalli ilan etmek olurdu.
        """
        H = hadamard().astype(np.float64)
        if not yalniz_veri:
            self.y.tek_kapi(H.astype(self.y.tip))
            self.iz.kapi += self.n
            return
        for i in range(self.n_satir):
            for j in range(self.ayar.satir_kubiti):
                self.tek(self.veri(i, j), H)

    def mera(self, kademe: Optional[int] = None,
             teta: Optional[np.ndarray] = None,
             kulli_dahil: bool = False) -> None:
        """MERA: dolanıklık çözücü ``U`` + izometri ``W`` (kütük H24).

        Dolaşıklığı üreten budur; süperpozisyon tek başına dolaşıklık
        vermez ve bu ölçülür (``entropi_once`` → ``entropi_sonra``).

        **Küllî hüküm bloğuna DOKUNMAZ** ve bu bir tashihtir (kütük
        H119). Sözleşme yüzleştirmesinde ölçüldü: MERA bütün zincire
        vuruyordu, yani 𝒪₆ Tasavvur daha hiçbir delil görülmeden
        ``makam``, ``mizan``, ``tasdik``, ``kelam``, ``kâide``,
        ``gaye`` ve ``tertip`` alanlarını karıştırıyordu.

        Bu, projenin kendi hükmüyle çelişiyordu: ``superpozisyon``
        küllî bloğa kasten dokunmaz ve sebebini yazar -- *"hüküm henüz
        verilmemiştir, ``|0⟩`` doğru başlangıçtır; hepsine vurmak, daha
        hiçbir delil görülmeden bütün hükümleri eşit ihtimalli ilan
        etmek olurdu."* MERA'nın hemen ardından aynı bloğu karıştırması
        o hükmü fiilen iptal ediyordu. İddia edilen bir şey değildi;
        kimse bakmadığı için görülmemişti.

        ``kulli_dahil=True`` eski davranışı geri verir -- kıyas
        ölçümü yapılabilsin diye durur, akışta kullanılmaz.
        """
        a = self.ayar
        # ``entropi_once`` yalnız İLK MERA'da yazılır. Evvelce her
        # çağrıda üzerine yazılıyordu ve 𝒪₆ Tasavvur ikinci kademeyi
        # kurunca "MERA öncesi entropi" 1.77 görünüyordu -- oysa o an
        # 𝒪₁–𝒪₅ zaten dolaşıklık kurmuştu. Ölçüm yalanlanmasın diye
        # başlangıç bir kere zabıtlanır.
        if self.iz.mera_kademe == 0:
            self.iz.entropi_once = float(
                self.y.dolasiklik_entropisi()["entropi"])
            self.iz.schmidt_once = int(
                self.y.dolasiklik_entropisi()["schmidt"])
        kad = a.mera_kademe if kademe is None else int(kademe)
        ust = None if kulli_dahil else self.kulli_bas
        izler = self.y.mera_kur(kademe=kad, teta=teta, ust=ust)
        self.iz.mera_kademe += len(izler)
        self.iz.kapi += len(izler) * self.n      # MERA da kapıdır, sayılır
        # **ÖLÇÜLEN VE DÜZELTİLEN MUHASEBE HATASI.** MERA'nın kesmesi
        # yalnız ``mera_kesme``ye yazılıyor, ``kesme``ye eklenmiyordu.
        # Halbuki bütün akıştaki en büyük kayıp oradadır: χ=8'de MERA tek
        # başına normu 1,0'dan 8,8e-03'e düşürüyor (%99,1), ve
        # ``iz.kesme`` bunun için ``0,000e+00`` yazıyordu. Yani ölçüt,
        # en büyük kaybı hiç görmüyordu.
        mk = float(sum(k.kesme_hatasi for k in izler))
        self.iz.mera_kesme += mk
        self.iz.kesme += mk
        e = self.y.dolasiklik_entropisi()
        self.iz.entropi_sonra = float(e["entropi"])
        self.iz.schmidt = int(e["schmidt"])

    # -----------------------------------------------------------------
    #  Üniter kapılar
    # -----------------------------------------------------------------
    def tek(self, i: int, G: np.ndarray) -> None:
        self.y.tek_kapi_yuva(i, G)
        self.iz.kapi += 1

    def cift(self, i: int, G: np.ndarray) -> None:
        """Komşu ``(i, i+1)`` çiftine kapı."""
        self.iz.kesme += self.y.cift_kapi_yuva(i, G)
        self.iz.kapi += 1

    # -- YIĞIN KAPILAR: melekelerin Python döngüsünü kaldıran arayüz ---
    def tek_yigin(self, yuvalar: Sequence[int], G: np.ndarray) -> None:
        """``m`` ayrık yuvaya ``m`` ayrı tek kübitlik kapı -- tek çağrı.

        Melekeler ``for i: for j: q.tek(...)`` yazıyordu; ölçüldü, kapı
        başına ~0,8 ms'nin neredeyse tamamı Python çağrı masrafıydı
        (kütük H79). Burada hepsi tek yığın çarpımına iner. ``G`` ya
        ``(2,2)`` (hepsine aynı) ya ``(m,2,2)``dir.
        """
        yv = np.asarray(yuvalar, np.intp)
        if yv.size == 0:
            return
        self.y.tek_kapi_yigin(yv, G)
        self.iz.kapi += int(yv.size)

    def cift_yigin(self, sol_yuvalar: Sequence[int], G: np.ndarray) -> float:
        """Ayrık komşu çiftlerin **hepsine** tek yığın SVD'siyle kapı."""
        yv = np.asarray(sol_yuvalar, np.intp)
        if yv.size == 0:
            return 0.0
        k = float(self.y.cift_kapi_yigin(yv, G))
        self.iz.kesme += k
        self.iz.kapi += int(yv.size)
        return k

    # -- Uzak çift: iki yol, eşiği ÖLÇÜM koyar ------------------------
    @property
    def mpo_esigi(self) -> int:
        """Bu mesafeden itibaren takas yerine MPO -- **ölçümden çıktı**.

        `nefs/uzaklik_olcumu.py` ikisini aynı durumda koşturdu ve netice
        **beklentimin tersi** çıktı; ikisi de zabıtlanır:

        * **HIZ:** MPO takastan daha YAVAŞ. χ=32'de 2,8-3 kat yavaş,
          χ=16'da ~1,1 kat yavaş; yalnız χ=8 ve mesafe ≥ 8'de biraz
          hızlı (1,02-1,16 kat). Yani H41'in "MPO kazanır" hükmü hız
          için **yanlıştır** ve öyle yazılır.
        * **KESME:** MPO takası eziyor. χ=32, mesafe 5'te takas
          ``5,30e-03``, MPO ``1,18e-30`` -- yirmi yedi mertebe fark.
          χ=8, mesafe 5'te takas durumun **%65'ini** atıyor (6,48e-01);
          bu kabul edilebilir değildir.

        O hâlde eşik hıza göre değil **doğruluğa** göre konur: takasın
        kesmesi ihmal edilebilir olduğu sürece takas (ucuz), kesme
        başladığı anda MPO. Ölçümde takas kesmesinin patladığı mesafe
        ``χ`` ile logaritmik büyüyor (χ=8→5, χ=16→5, χ=32→8), onun için:

            eşik = max(4, ⌊log₂ χ⌋ + 2)

        Hız uğruna doğruluk satılmaz; bu satır o hükmün kendisidir.
        """
        return max(4, int(np.log2(max(self.ayar.bag, 2))) + 2)

    def _cift_carpanlari(self, G: np.ndarray
                         ) -> Tuple[np.ndarray, np.ndarray]:
        """``G = Σₖ Aₖ ⊗ Bₖ`` -- iki kübitlik kapının çarpan ayrışımı.

        İndeks düzeni ``2i+j``dir (``i`` sol, ``j`` sağ), dolayısıyla
        ``G[(i,j),(p,q)]`` yeniden dizilip ``(i,p)|(j,q)`` kesitinden
        SVD alınır. Rütbe ``r ≤ 4``tür ve çarpım kapılarında ``r = 1``
        çıkar -- o zaman kapı zaten iki tek kübitlik kapıdır ve MPO'ya
        hiç gerek kalmaz.
        """
        M = np.asarray(G, float).reshape(2, 2, 2, 2)      # i,j,p,q
        M = M.transpose(0, 2, 1, 3).reshape(4, 4)         # (i,p)|(j,q)
        U, s, Vt = np.linalg.svd(M)
        r = int(np.sum(s > 1e-12 * max(s[0], 1e-30)))
        r = max(r, 1)
        A = (U[:, :r] * s[:r]).T.reshape(r, 2, 2)
        B = Vt[:r, :].reshape(r, 2, 2)
        return A, B

    def uzak_cift_mpo(self, i: int, j: int, G: np.ndarray) -> float:
        """Uzak çifte kapı -- **kübit oynatmadan**, operatörü yayarak.

        Kütük H41: *"takas ağı kapalı yoldur; MPO kazanır."* O hüküm
        verilmişti fakat 13 meleke hâlâ takas kullanıyordu -- kendi
        hükmümüze uymuyorduk. Burada MPO yolu kurulur:

            W[i][0,·,·,k] = Aₖ ,  ara yuvalar = kimlik (bağ k taşınır),
            W[j][k,·,·,0] = Bₖ

        Bağ ``r = rank(G) ≤ 4``tür. Hiçbir kübit yer değiştirmez,
        dolayısıyla hiçbir dolaşıklık sürüklenmez.
        """
        i, j = int(i), int(j)
        if i > j:
            # kapı simetrik değildir: indeks düzeni korunmalı
            G = np.asarray(G, float).reshape(2, 2, 2, 2
                                             ).transpose(1, 0, 3, 2
                                                         ).reshape(4, 4)
            i, j = j, i
        A, B = self._cift_carpanlari(G)
        r = A.shape[0]
        Wi = np.zeros((r, 2, 2, r))
        Wj = np.zeros((r, 2, 2, r))
        for k in range(r):
            Wi[0, :, :, k] = A[k]
            Wj[k, :, :, 0] = B[k]
        kesme = self.y.mpo_uygula_hizli({i: Wi, j: Wj}, D=r,
                                        bas=i, son=j + 1)
        self.iz.kesme += float(kesme)
        self.iz.kapi += 1
        self.iz.supurme += 1
        return float(kesme)

    def uzak_cift(self, i: int, j: int, G: np.ndarray) -> None:
        """Uzak ``(i, j)`` çiftine kapı -- **yolu ölçüm seçer**.

        Mesafe ``mpo_esigi``nin altındaysa takas ağı (ucuz ve o mesafede
        kesmesi ihmal edilebilir), üstündeyse MPO (pahalı fakat
        dolaşıklığı sürüklemiyor). Eşik elle konmadı; bkz. ``mpo_esigi``.
        """
        if abs(int(j) - int(i)) >= self.mpo_esigi:
            self.uzak_cift_mpo(i, j, G)
            return
        self._uzak_cift_takas(i, j, G)

    def _uzak_cift_takas(self, i: int, j: int, G: np.ndarray) -> None:
        """Takas ağıyla uzak çift -- kısa mesafenin ucuz yolu."""
        i, j = int(i), int(j)
        if i == j:
            raise ValueError("uzak çift için i ≠ j olmalı")
        if i > j:
            i, j = j, i
        yer = j
        while yer > i + 1:
            self.iz.kesme += self.y.takas(yer - 1)
            self.iz.takas += 1
            yer -= 1
        self.cift(i, G)
        while yer < j:
            self.iz.kesme += self.y.takas(yer)
            self.iz.takas += 1
            yer += 1

    # -----------------------------------------------------------------
    #  MPO ile toplama -- kübitler HİÇ oynamaz
    # -----------------------------------------------------------------
    def mpo_topla(self, alan: str, acilar: Sequence[float],
                  duraklar: Optional[Sequence[int]] = None,
                  j: int = 0) -> float:
        """Bütün durakların hükmünü küllî alana **tek operatörle** akıt.

        Uygulanan üniter::

            U = Π_i exp(θ_i · n_i ⊗ Y_küllî) = exp((Σ_i θ_i n_i) ⊗ Y)

        ``n_i = |1⟩⟨1|_i`` sayı işlemcisidir; hepsi birbiriyle sıra
        değiştirir (aynı tabanda köşegen), dolayısıyla çarpım tam olarak
        üstele eşittir -- hiçbir Trotter hatası yoktur.

        **MPO bağı yalnız 2'dir** ve sebebi cebridir: küllî kübite
        uygulanan dönme ``R(φ) = cos φ·I + sin φ·J`` iki boyutlu bir
        cebirde yaşar (``J² = −I``), ve ``R(Σφ_i) = Π R(φ_i)``. Yani
        zincir boyunca taşınması gereken şey sayaç değil, o iki boyutlu
        cebir elemanıdır. Sayaç taşınsaydı bağ ``N+1`` olurdu.

        Takas ağıyla aynı neticeyi verir; farkı, hiçbir kübitin yer
        değiştirmemesi ve dolayısıyla dolaşıklığın sürüklenmemesidir.
        """
        dur = self.yereller() if duraklar is None else list(duraklar)
        acilar = list(acilar)
        if len(acilar) != len(dur):
            acilar = list(np.resize(np.asarray(acilar, float), len(dur)))
        hedef = self.kulli(alan, j)
        if any(d >= hedef for d in dur):
            raise ValueError("MPO toplaması duraklar hedefin solunda iken kurulur")

        W: Dict[int, np.ndarray] = {}
        for d, teta in zip(dur, acilar):
            # n_i = 0 → cebirde birim; n_i = 1 → R(θ) elemanı
            Wd = np.zeros((2, 2, 2, 2))
            Wd[0, 0, 0, 0] = 1.0                  # |0⟩⟨0| ⊗ birim
            Wd[1, 0, 0, 1] = 1.0
            c, s = math.cos(teta), math.sin(teta)
            # |1⟩⟨1| ⊗ R(θ):  (c,s) ile cebirde çarp
            Wd[0, 1, 1, 0] = c
            Wd[0, 1, 1, 1] = s
            Wd[1, 1, 1, 0] = -s
            Wd[1, 1, 1, 1] = c
            W[d] = Wd
        # küllî kübitte biriken cebir elemanı fiilen uygulanır
        Wh = np.zeros((2, 2, 2, 2))
        Wh[0, :, :, 0] = np.eye(2)                       # bileşen I
        Wh[1, :, :, 0] = np.array([[0.0, -1.0], [1.0, 0.0]])   # bileşen J
        W[hedef] = Wh

        kesme = self.y.mpo_uygula_hizli(W, D=2, bas=min(dur),
                                        son=hedef + 1)
        self.iz.kesme += float(kesme)
        self.iz.kapi += len(dur) + 1
        self.iz.supurme += 1
        return float(kesme)

    def mpo_dagit(self, alan: str, acilar: Sequence[float],
                  duraklar: Optional[Sequence[int]] = None,
                  j: int = 0) -> float:
        """``mpo_topla``ın aynası: küllî hüküm **duraklara dağıtılır**.

        Toplamada kontrol duraklardaydı, hedef küllî bloktu; burada
        tersi: küllî hüküm **kontrol**, duraklar hedeftir. Tafsil (𝒪₃₄)
        mücmeli dallarına açar, Belâgat (𝒪₃₉) makamı kelama sirayet
        ettirir; ikisi de bu operatördür.

        Uygulanan üniter::

            U = |0⟩⟨0|_küllî ⊗ I  +  |1⟩⟨1|_küllî ⊗ Π_d R(θ_d)

        Yani küllî hüküm uyanıksa bütün duraklar döner, uyanık değilse
        hiçbiri dönmez. İki dal iki ayrı bağ bileşeninde taşınır ve sol
        sınırda **ikisi de** toplanır -- ``sol_sinir = (1,1)``. Bağ yine
        2'dir; küllî blok zincirin sağında olduğu için akış sağdan
        soladır.
        """
        dur = self.yereller() if duraklar is None else list(duraklar)
        acilar = list(acilar)
        if len(acilar) != len(dur):
            acilar = list(np.resize(np.asarray(acilar, float), len(dur)))
        kaynak = self.kulli(alan, j)
        if any(d >= kaynak for d in dur):
            raise ValueError("MPO dağıtımı duraklar kaynağın solunda iken kurulur")

        W: Dict[int, np.ndarray] = {}
        for d, teta in zip(dur, acilar):
            Wd = np.zeros((2, 2, 2, 2))
            Wd[0, :, :, 0] = np.eye(2)                  # dal 0: kimlik
            Wd[1, :, :, 1] = donme(teta)                # dal 1: R(θ)
            W[d] = Wd
        Wk = np.zeros((2, 2, 2, 2))
        Wk[0, 0, 0, 0] = 1.0                            # |0⟩⟨0| → dal 0
        Wk[1, 1, 1, 0] = 1.0                            # |1⟩⟨1| → dal 1
        W[kaynak] = Wk

        kesme = self.y.mpo_uygula_hizli(W, D=2, bas=min(dur),
                                        son=kaynak + 1,
                                        sol_sinir=np.array([1.0, 1.0]),
                                        sag_sinir=np.array([1.0, 0.0]))
        self.iz.kesme += float(kesme)
        self.iz.kapi += len(dur) + 1
        self.iz.supurme += 1
        return float(kesme)

    def supur(self, alan: str, kapi: Callable[[int, int], Optional[np.ndarray]],
              duraklar: Optional[Sequence[int]] = None) -> Dict[str, float]:
        """Küllî hüküm alanını zincirde **tek** yürüt, geçerken kapıları vur.

        ``kapi(durak, blok_yeri) -> 4×4 | None``. Blok yerine iade edilir
        (``geri_gotur=True``): iade edilmezse yerellik gider ve takas,
        geçtiği kesitlerde dolaşıklığı sürükleyip ``χ``yi zorlar.
        """
        bas, kac = self._alan[alan]
        dur = self.yereller() if duraklar is None else list(duraklar)
        r = self.y.supurme(bas, kac, dur, kapi, geri_gotur=True)
        self.iz.takas += int(r["takas"])
        self.iz.kapi += int(r["kapı"])
        self.iz.kesme += float(r["kesme"])
        self.iz.supurme += 1
        return r

    # -----------------------------------------------------------------
    #  Hüküm kapıları -- hepsi ÜNİTER, hiçbiri okumaz
    # -----------------------------------------------------------------
    def hukum_cevir(self, alan: str, teta: float, j: int = 0) -> None:
        """Küllî hüküm alanının bir kübitini ``θ`` kadar çevir."""
        self.tek(self.kulli(alan, j), donme(teta))

    def hukum_bagla(self, alan: str, kaynak: int, teta: float,
                    j: int = 0) -> None:
        """Bir veri/yerel kübitini küllî hüküm kübitine **dolaştır**.

        Kontrollü dönme: kaynak ``|1⟩`` iken hüküm ``θ`` kadar çevrilir.
        Hükmün sayısı hiçbir yerde çıkmaz; hüküm delille dolaşır.
        """
        self.uzak_cift(kaynak, self.kulli(alan, j), kontrollu_donme(teta))

    # -----------------------------------------------------------------
    #  Ölçüm -- yalnız en sonda, ZAYIF (kütük H31)
    # -----------------------------------------------------------------
    def povm(self, yuvalar: Sequence[int]) -> np.ndarray:
        """``ρ_i = Tr_çevre|Ψ⟩⟨Ψ|``den Bloch benzeri iki reel sayı.

        Sert (Von Neumann) ölçüm yapılmaz: durum çökertilmez.
        Dönen ``(k, 2)``: ``z = ρ₀₀−ρ₁₁`` (nüfus farkı), ``x = 2ρ₀₁``
        (uyum).
        """
        R = self.y.tekil_yogunluklar(list(yuvalar))       # (B, k, 2, 2)
        return np.stack([R[..., 0, 0] - R[..., 1, 1],
                         2.0 * R[..., 0, 1]], axis=-1)

    def blok_dagilimi(self, bas: int, kac: int) -> np.ndarray:
        """``bas``tan itibaren ``kac`` kübitin **ortak** dağılımı -- tam.

        Tek yuva yoğunlukları (``yuva_yogunluklari``) bağımsızlık varsayar
        ve dolaşık bir durumda yanıltır; belirteç ise ``kac`` kübite
        birden kodlanmıştır. Onun için burada gerçek indirgenmiş yoğunluk
        kurulur: sol çevre ``E_L`` zincirin başından, sağ çevre ``E_R``
        sonundan sarılır, blok ikisinin arasına yerleştirilir::

            ρ_blok = Tr_çevre |Ψ⟩⟨Ψ|,   P(x) = ⟨x|ρ_blok|x⟩

        Bu bir POVM'dir (``Σ E_x = I``) ve **çöküş yoktur** (kütük H31):
        dalga okunduktan sonra da diridir, hiçbir yere çökertilmez.

        Maliyet ``O(N χ³ + 4^kac χ²)``; ``kac`` küçük tutulmalıdır
        (belirteç başına kübit sayısı kadar, varsayılan 4 → 16 durum).
        """
        bas = int(bas)
        kac = int(kac)
        if kac < 1 or bas + kac > self.n:
            raise IndexError("blok zincirin dışına taşıyor")
        X = self.y.bag
        A = self.y.A                                  # (B, n, X, 2, X)
        Bn = self.y.B

        # Yığın ekseni ``B`` bütün büzülmelerde taşınır: her üye kendi
        # dağılımını verir (kullanıcı hükmü). ``einsum`` yol araması
        # sıcak yolda israftı; çevre büzülmeleri açık ``matmul``dur.
        L = np.zeros((Bn, X, X))
        L[:, 0, 0] = 1.0
        for k in range(bas):
            Ak = A[:, k].astype(np.float64)           # (B,a,i,b)
            # L[b,d] = Σ_{a,c,i} L[a,c] A[a,i,b] A[c,i,d]
            #
            # **ÖLÇÜLEN VE DÜZELTİLEN HATA.** Bu büzülme iki adımdır:
            #   1) t1[i,c,b] = Σ_a L[a,c] A[a,i,b]
            #   2) L[b,d]    = Σ_{i,c} t1[i,c,b] A[c,i,d]
            # Evvelki kod 2. adımda ``A``nın **çıkış** bağını (b) ``t1``in
            # ``c``siyle büzüyordu; doğrusu **giriş** bağını (c) büzmektir.
            # Yanlış bacak büzüldüğü için sol çevre bambaşka bir dizey
            # çıkıyordu: tam dalgayla yüzleştirildi, fark 2,4–3,2 ölçüldü
            # (sağ çevre ise 1e-16 ile zaten doğruydu). Neticesi küçük
            # değildir: ``beyan`` bu ρ'dan okunur, yani modelin BÜTÜN
            # belirteç dağılımı yanlış çevreden çıkıyordu -- köşegende
            # negatif "olasılıklar" bile vardı. Düzeltme 20 halde tam
            # dalgayla 1e-16'da örtüşür ve negatif köşegen kalmaz.
            t1 = np.matmul(L.transpose(0, 2, 1),
                           Ak.reshape(Bn, X, 2 * X))  # (B,c,(i,b))
            t1 = t1.reshape(Bn, X, 2, X).transpose(0, 2, 1, 3)   # (B,i,c,b)
            Ai = Ak.transpose(0, 2, 1, 3)                        # (B,i,c,d)
            L = np.matmul(t1.transpose(0, 1, 3, 2), Ai).sum(axis=1)
        R = np.zeros((Bn, X, X))
        R[:, 0, 0] = 1.0
        for k in range(self.n - 1, bas + kac - 1, -1):
            Ak = A[:, k].astype(np.float64)
            # R[a,c] = Σ_{b,d,i} R[b,d] A[a,i,b] A[c,i,d]
            t1 = np.matmul(Ak.transpose(0, 2, 1, 3).reshape(Bn, 2 * X, X),
                           R).reshape(Bn, 2, X, X)     # (B,i,a,d)
            R = np.matmul(t1.transpose(0, 1, 2, 3),
                          Ak.transpose(0, 2, 3, 1)).sum(axis=1)

        M = L
        boyut = 1
        for k in range(bas, bas + kac):
            Ak = A[:, k].astype(np.float64)
            M = np.einsum("z...ac,zaib,zcjd->z...ijbd", M, Ak, Ak,
                          optimize=False)
            boyut *= 2
        rho = np.einsum("z...bd,zbd->z...", M, R, optimize=False)
        rho = rho.reshape([Bn] + [2] * (2 * kac))
        eks = [0] + [1 + x for x in
                     (list(range(0, 2 * kac, 2))
                      + list(range(1, 2 * kac, 2)))]
        rho = np.transpose(rho, eks).reshape(Bn, boyut, boyut)
        P = np.clip(np.real(np.diagonal(rho, axis1=1, axis2=2)), 0.0, None)
        t = P.sum(axis=1, keepdims=True)
        P = np.where(t > 1e-30, P / np.maximum(t, 1e-30), 1.0 / boyut)
        return P if Bn > 1 else P[0]

    def beyan(self, sozluk: int, satir: Optional[int] = None) -> np.ndarray:
        """Belirteç dağılımı: **kelam alanından** okunur.

        Model neyi konuşacaksa oradadır; veri kübitlerinden okunmaz,
        çünkü onların marjinali dolaşıklık yüzünden düzgündür (ölçüldü). ``sozluk`` ``2^k``den küçükse
        artan durumlar son sınıfa toplanır -- atılmaz (H14: kaba
        sıfırlama yasak).
        """
        _, k = self._alan["kelam"]
        P = self.blok_dagilimi(self.kulli("kelam", 0), k)
        if sozluk >= len(P):
            out = np.zeros(sozluk)
            out[:len(P)] = P
            return out
        out = np.zeros(sozluk)
        out[:sozluk - 1] = P[:sozluk - 1]
        out[sozluk - 1] = float(P[sozluk - 1:].sum())
        t = float(out.sum())
        return out / t if t > 1e-30 else np.full(sozluk, 1.0 / sozluk)

    def makam_dagilimi(self) -> np.ndarray:
        """Makamın taban durumları üzerindeki **ortak** dağılımı -- çöküşsüz.

        **ÖLÇÜLEN VE DÜZELTİLEN KUSUR (kütük H129).** Evvelce iki makam
        kübitinin yoğunluklarından **çarpım** dağılımı kuruluyordu::

            P = [p₀p₁, p₀(1−p₁), (1−p₀)p₁, (1−p₀)(1−p₁)]

        Bu, ``makam₀`` ile ``makam₁``in **bağımsız** olduğunu farzeder.
        Dolaşık bir durumda o farz yanlıştır ve ölçüldü: çarpım ile
        hakikî ortak dağılım arasındaki toplam değişinti mesafesi
        **0,0931** -- yani raporlardaki ``P_Şek``, ``P_Zan``,
        ``P_Yakîn``, ``P_Vehim`` sayıları yaklaşık **%9** yanlıştı.

        Doğrusu ``blok_dagilimi``dir: sol ve sağ çevreler kurulup
        bloğun **ortak** indirgenmiş yoğunluğu alınır. Bu bir POVM'dir
        (``Σ E_x = I``) ve **çöküş yoktur** (kütük H31).

        Kübit sayısından bağımsızdır: makam iki kübitse dört, üç kübitse
        sekiz taban durumu döner. Böylece mertebe sayısını artırmak
        (H129'un açık borcu) bu usulü değiştirmez.
        """
        _, kac = self._alan["makam"]
        return self.blok_dagilimi(self.kulli("makam", 0), kac)

    def alan_degeri(self, ad: str) -> float:
        """Bir küllî hüküm alanının ``[0,1]`` değeri -- zayıf okuma.

        Alanın kübitlerinin ``ρ₁₁`` nüfuslarının ortalamasıdır; yani
        "bu hüküm ne kadar uyanmış". Yalnız RAPOR ve nihaî beyan için
        çağrılır; akış içinde hiçbir meleke bunu okumaz.
        """
        bas, kac = self._alan[ad]
        R = self.y.tekil_yogunluklar(list(range(bas, bas + kac)))
        v = np.mean(R[..., 1, 1], axis=1)                # (B,)
        return float(v[0]) if self.y.B == 1 else v

    def olcumler(self) -> Dict[str, float]:
        """Küllî hükümlerin zayıf okuması + dolaşıklık -- ``B=1`` için.

        Yığın koşusunda ``olcumler_yigin`` kullanılır; **her üye kendi
        ölçümünü verir** (kullanıcı hükmü). Burada skaler dönmesinin
        sebebi ``B=1``in hâlâ en sık hâl olmasıdır; iki ayrı kod yolu
        değil, aynı ölçümün iki sunumudur.
        """
        y = self.olcumler_yigin()
        return {k: (float(v[0]) if isinstance(v, np.ndarray) else float(v))
                for k, v in y.items()}

    def olcumler_yigin(self) -> Dict[str, np.ndarray]:
        """Bütün küllî hükümler, **yığın üyesi başına** ``(B,)``."""
        Bn = self.y.B
        d: Dict[str, np.ndarray] = {}
        for ad, _ in self.ayar.kulli_alanlar:
            v = self.alan_degeri(ad)
            d[ad] = np.atleast_1d(np.asarray(v, float))
        e = self.y.dolasiklik_entropisi()
        d["entropi"] = np.asarray(e.get("entropi_yigin",
                                        np.full(Bn, e["entropi"])), float)
        d["schmidt"] = np.full(Bn, float(e["schmidt"]))
        d["norm_hatası"] = np.full(Bn, float(self.y.norm_hatasi(ornek=32)))
        P = np.atleast_2d(self.makam_dagilimi())
        for ad, v in self.makam_mertebe_dagilimi(P).items():
            d["P_" + ad] = v
        d["makam_derece"] = P @ self.makam_derece_vektoru()
        return d

    def makam_derece_vektoru(self) -> np.ndarray:
        """Her **taban durumuna** düşen yakîn derecesi, ``[0,1]``de.

        ``makam_derecesi`` merdiven **basamağına** göre sıralıdır;
        ``makam_dagilimi`` ise **taban durumu** indeksine göre. İkisini
        karıştırmak sessiz bir hatadır -- Gray sırasında basamak 4'ün
        indeksi 6'dır, 4 değil. Çevirme burada bir kere yapılır.
        """
        kac = self._alan["makam"][1]
        v = np.zeros(1 << kac)
        for basamak, idx in enumerate(makam_merdiveni(kac)):
            v[idx] = makam_derecesi(kac)[basamak]
        return v

    def makam_mertebe_dagilimi(self, P: Optional[np.ndarray] = None
                               ) -> Dict[str, np.ndarray]:
        """Taban durumu dağılımını **mertebe** dağılımına indir.

        Merdiven mertebeden incedir (üç kübitte 8 basamak, 5 mertebe),
        onun için bir mertebenin ihtimali, o mertebeye düşen bütün
        basamakların **toplamıdır**. Toplamak burada meşrudur: aynı
        mertebenin basamakları birbirinin alternatifidir, ayrı eksen
        değil (kıyas: H21'de mertebeler toplanmıyordu, zira onlar ayrı
        eksenlerdi).

        Adlar ``MAKAM_ADLARI``dan gelir; bir mertebeye hiç basamak
        düşmezse anahtar yine üretilir ve ``0`` olur -- rapor eksik
        anahtardan değil, sıfırdan bahsetsin.
        """
        kac = self._alan["makam"][1]
        if P is None:
            P = self.makam_dagilimi()
        P = np.atleast_2d(np.asarray(P, float))
        mert = makam_mertebeleri(kac)
        merd = makam_merdiveni(kac)
        out: Dict[str, np.ndarray] = {
            ad: np.zeros(P.shape[0]) for ad in MAKAM_ADLARI}
        # ``basamak`` merdiven sırası, ``merd[basamak]`` taban durumunun
        # indeksi. Gray sırasında ikisi aynı DEĞİLDİR.
        for basamak, ad in enumerate(mert):
            out[ad] = out[ad] + P[:, merd[basamak]]
        return out
