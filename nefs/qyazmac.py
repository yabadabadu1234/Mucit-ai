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

from main.yazmac import Yazmac, dik_iki_kubit, hadamard

__all__ = ["QAyar", "QYazmac", "donme", "faz_z", "kontrollu_donme",
           "MAKAM_ADLARI"]

#: Makam iki kübite kodlanır: 00=Şek, 01=Zan, 10=Yakîn, 11=Vehim.
#: Sıra kasıtlıdır: Şek ve Vehim uçlardadır, Zan ile Yakîn ortadadır;
#: tek kübitlik bir dönme Şek'ten Zan'a, Zan'dan Yakîn'e geçirir.
MAKAM_ADLARI: Tuple[str, ...] = ("Şek", "Zan", "Yakîn", "Vehim")


def donme(teta: float) -> np.ndarray:
    """``R(θ) = [[cos,−sin],[sin,cos]]`` -- reel tek kübitlik dönme.

    Reel cebirde faz işarettir (bkz. ``main/yazmac.py``); ``e^{iθ}``
    yerine ``SO(2)`` dönmesi taşınır. Dik olduğu için normu korur.
    """
    c, s = math.cos(float(teta)), math.sin(float(teta))
    return np.array([[c, -s], [s, c]], dtype=np.float64)


def faz_z() -> np.ndarray:
    """``σ_z`` -- işaret çevirme. Yıkıcı girişimi kuran kapı."""
    return np.array([[1.0, 0.0], [0.0, -1.0]], dtype=np.float64)


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
        ("makam", 2), ("mizan", 4), ("tenakuz", 2),
        ("tasdik", 2), ("sukut", 1), ("nakz", 2), ("kelam", 4),
    )

    @property
    def kulli_kubit(self) -> int:
        return sum(n for _, n in self.kulli_alanlar)

    def kubit_sayisi(self, n_satir: int) -> int:
        return n_satir * (self.satir_kubiti + self.yerel_kubit) + self.kulli_kubit


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
             teta: Optional[np.ndarray] = None) -> None:
        """MERA: dolanıklık çözücü ``U`` + izometri ``W`` (kütük H24).

        Dolaşıklığı üreten budur; süperpozisyon tek başına dolaşıklık
        vermez ve bu ölçülür (``entropi_once`` → ``entropi_sonra``).
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
        izler = self.y.mera_kur(kademe=kad, teta=teta)
        self.iz.mera_kademe += len(izler)
        self.iz.kapi += len(izler) * self.n      # MERA da kapıdır, sayılır
        self.iz.mera_kesme += float(sum(k.kesme_hatasi for k in izler))
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
        kesme = self.y.mpo_uygula({i: Wi, j: Wj}, D=r, bas=i, son=j + 1)
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

        kesme = self.y.mpo_uygula(W, D=2, bas=min(dur), son=hedef + 1)
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

        kesme = self.y.mpo_uygula(W, D=2, bas=min(dur), son=kaynak + 1,
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
        R = self.y.yuva_yogunluklari(list(yuvalar))       # (B, k, 2, 2)
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
            t1 = np.matmul(L.transpose(0, 2, 1),
                           Ak.reshape(Bn, X, 2 * X))  # (B,c,(i,b))
            t1 = t1.reshape(Bn, X, 2, X).transpose(0, 2, 1, 3)
            L = np.matmul(Ak.transpose(0, 2, 3, 1).reshape(Bn, 2, X, X
                                                           ).transpose(0, 1, 3, 2),
                          t1).sum(axis=1)
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
        """Makamın dört taban durumu üzerindeki dağılımı -- çöküşsüz.

        İki makam kübitinin yoğunluklarından çarpım dağılımı okunur:
        ``P(Şek), P(Zan), P(Yakîn), P(Vehim)``. Bu bir POVM'dir
        (``Σ E_x = I``); dalga diri kalır.
        """
        R = self.y.yuva_yogunluklari([self.kulli("makam", 0),
                                      self.kulli("makam", 1)])   # (B,2,2,2)
        p0 = np.clip(R[:, 0, 0, 0], 0.0, 1.0)
        p1 = np.clip(R[:, 1, 0, 0], 0.0, 1.0)
        P = np.stack([p0 * p1, p0 * (1 - p1), (1 - p0) * p1,
                      (1 - p0) * (1 - p1)], axis=1)
        t = P.sum(axis=1, keepdims=True)
        P = np.where(t > 1e-12, P / np.maximum(t, 1e-12), 0.25)
        return P if self.y.B > 1 else P[0]

    def alan_degeri(self, ad: str) -> float:
        """Bir küllî hüküm alanının ``[0,1]`` değeri -- zayıf okuma.

        Alanın kübitlerinin ``ρ₁₁`` nüfuslarının ortalamasıdır; yani
        "bu hüküm ne kadar uyanmış". Yalnız RAPOR ve nihaî beyan için
        çağrılır; akış içinde hiçbir meleke bunu okumaz.
        """
        bas, kac = self._alan[ad]
        R = self.y.yuva_yogunluklari(list(range(bas, bas + kac)))
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
        for i, ad in enumerate(MAKAM_ADLARI):
            d["P_" + ad] = P[:, i]
        return d
