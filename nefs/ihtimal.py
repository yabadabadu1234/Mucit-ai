"""
İhtimal uzayı: **çıktı ızgarasının bütün muhtemel hâlleri, süperpozisyonda**.

Kullanıcı hükmü (H51): *"İhtimal uzayı o ızgaranın olabileceği tüm
ihtimallerdir. 30×30=900, yani 10⁹⁰⁰ ihtimal var; 22 milyon kübitle
2^22milyon olur. İhtimal uzayı bizzat o kübitlerin içidir."*

Hesap::

    30×30 ızgara            = 900 hücre
    hücre başına renk       = 10
    bütün muhtemel ızgaralar= 10⁹⁰⁰
    gereken kübit           = log₂(10⁹⁰⁰) = 900·3,3219 = 2.990
    hücre başına 4 kübitle  = 900·4 = 3.600 kübit

22.000.000 / 3.600 ≈ **6.100 ızgara**. Yani ihtimal uzayı kübitlerin
taşıdığı bir şey değil, **bizzat içidir**.

**Bu, el yazması kaide dağarcığının nakzıdır** (H48). Kaide yazılmaz,
aranmaz bile: bütün ızgaralar zaten oradadır; melekelerin işi kaideye
uymayanları **yıkıcı girişimle söndürmektir**. Ayakta kalan çıktıdır.

Usul üç adımdır ve üçü de üniterdir::

    1. AÇ      : her hücreye Hadamard → bütün ızgaralar eşit genlikte
                 (χ = 1; süperpozisyon bedava, dolaşıklık pahalı)
    2. SÖNDÜR  : müşahede edilen her kaide bir kısıt operatörüdür;
                 kaideye uymayan ızgaraların genliği ters işaret alıp
                 komşusuyla toplanınca sıfırlanır (kütük H19'un üçüncü
                 şartı: yıkıcı girişim)
    3. OKU     : POVM zayıf ölçüm; ayakta kalan dağılım okunur, çöküş yok

**Neyin iddia edilmediği.** Kuantum donanımı yoktur; 10⁹⁰⁰ hâlin hepsi
fiilen tutulmaz. MPS ``χ`` bağıyla **sıkıştırılmış** olarak tutulur ve
sıkıştırmanın bedeli ölçülür: kısıt uygulandıkça dolaşıklık artar, ``χ``
yetmezse kesme hatası doğar. Bu modülün asıl vazifesi o bedeli
**ölçmektir**, gizlemek değil.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from main.yazmac import Yazmac, dik_iki_kubit, hadamard

__all__ = ["IhtimalYazmaci", "kubit_hesabi"]


def kubit_hesabi(h: int, w: int, renk: int = 10,
                 kubit_basina: int = 4) -> Dict[str, float]:
    """``h×w`` ızgaranın ihtimal uzayı kaç kübit ister?

    İki hesap ayrı verilir ve karıştırılmaz:

    * **asgarî** -- ``log₂(renk^(h·w))``. Bilgi kuramının verdiği taban;
      hücreleri ayrı ayrı kodlamayan, en sıkı paketleme.
    * **fiilî**  -- ``h·w·kubit_basina``. Her hücre kendi kübitlerinde
      durur; kodlama basit ve yerel kapılar mümkün olur. Bedeli birkaç
      yüz kübittir, kazancı bütün mimarinin işleyebilmesidir.
    """
    hucre = h * w
    asgari = hucre * math.log2(renk)
    fiili = hucre * kubit_basina
    return {"hücre": float(hucre),
            "ihtimal_log10": float(hucre * math.log10(renk)),
            "asgarî_kübit": float(math.ceil(asgari)),
            "fiilî_kübit": float(fiili),
            "22M_kaç_ızgara": float(22_000_000 / max(fiili, 1))}


@dataclass
class IhtimalAyar:
    h: int = 3
    w: int = 3
    renk: int = 4                 # kaç renk (ARC'de 10; sınamada az)
    kubit_basina: int = 2         # 2^kubit_basina ≥ renk olmalı
    bag: int = 8                  # χ
    tohum: int = 0

    def __post_init__(self) -> None:
        if 2 ** self.kubit_basina < self.renk:
            raise ValueError("kübit_başına renk sayısını kodlamaya yetmiyor")

    @property
    def hucre(self) -> int:
        return self.h * self.w

    @property
    def n(self) -> int:
        return self.hucre * self.kubit_basina


class IhtimalYazmaci:
    """Bütün muhtemel ızgaraları aynı anda tutan kübit yazmacı."""

    def __init__(self, ayar: Optional[IhtimalAyar] = None) -> None:
        self.ayar = ayar or IhtimalAyar()
        a = self.ayar
        self.y = Yazmac(a.n, bag=a.bag, tohum=a.tohum, tip=np.float64)
        self.kesme = 0.0
        self.kapi = 0

    # -----------------------------------------------------------------
    def yuva(self, i: int, j: int, b: int = 0) -> int:
        """``(i,j)`` hücresinin ``b``inci kübitinin zincir yeri.

        Satır sırası (row-major) kasten seçildi: aynı satırdaki komşu
        hücreler zincirde de komşudur, dolayısıyla yatay kısıtlar
        **yerel kapıyla** kurulur. Dikey komşuluk ``w`` kadar uzaktır ve
        MPO ister -- bu bir bedeldir ve ölçülür.
        """
        a = self.ayar
        return (i * a.w + j) * a.kubit_basina + b

    # -----------------------------------------------------------------
    def ac(self) -> None:
        """**1. adım: AÇ.** Her hücreye Hadamard.

        Bundan sonra ``renk^(h·w)`` ızgaranın **hepsi** eşit genliktedir
        ve MPS'te ``χ = 1`` ile tam temsil edilir: süperpozisyon bedava,
        dolaşıklık pahalıdır. Entropi burada **sıfırdır** ve ölçülür --
        henüz hiçbir hücre ötekini kısıtlamıyor.
        """
        self.y.tek_kapi(hadamard().astype(self.y.tip))
        self.kapi += self.y.n

    def durum(self) -> Dict[str, float]:
        e = self.y.dolasiklik_entropisi()
        return {"entropi": float(e["entropi"]),
                "schmidt": float(e["schmidt"]),
                "norm_hatası": float(self.y.norm_hatasi(ornek=32)),
                "kesme": float(self.kesme),
                "kapı": float(self.kapi),
                "bayt": float(self.y.bayt)}

    # -----------------------------------------------------------------
    #  2. adım: SÖNDÜR -- kısıt operatörleri (hepsi üniter)
    # -----------------------------------------------------------------
    def hucre_sabitle(self, i: int, j: int, renk: int) -> None:
        """``(i,j)`` hücresini bir renge **kilitle** -- tam kısıt.

        En sert kısıttır: o hücrenin kübitleri artık süperpozisyonda
        değildir. Genliği söndürmez, **döndürür**: hücre hangi bitlerde
        olmalıysa oraya çevrilir. Üniterdir ve tersi vardır.
        """
        a = self.ayar
        # **UÇ SIRASI (endianness) KUSURU DÜZELTİLDİ.** Kodlayıcı küçük
        # uçlu (b=0 en düşük bit), okuyucu ise büyük uçlu idi: renk 2'ye
        # kilitlenen hücre okumada renk 1 görünüyordu. İkisi de büyük
        # uçlu yapıldı -- ``blok_dagilimi`` indisi ilk kübiti en anlamlı
        # sayar, kodlama da öyle sayar.
        for b in range(a.kubit_basina):
            bit = (renk >> (a.kubit_basina - 1 - b)) & 1
            # |+⟩ hâlinden |bit⟩ hâline döndüren dik kapı
            G = (np.array([[1.0, 1.0], [1.0, -1.0]]) / math.sqrt(2.0)
                 if bit == 0 else
                 np.array([[1.0, -1.0], [1.0, 1.0]]) / math.sqrt(2.0))
            self.y.tek_kapi_yuva(self.yuva(i, j, b), G)
            self.kapi += 1

    def komsu_bagla(self, i1: int, j1: int, i2: int, j2: int,
                    teta: float) -> None:
        """İki hücreyi **dolaştır** -- 'bunlar birbirine bağlı' kısıtı.

        Kaide "komşu hücreler aynı renk olsun" gibi bir şey söylüyorsa,
        o iki hücrenin kübitleri arasına kontrollü dönme konur: birinin
        değeri ötekini büker. Uymayan bileşimlerin genliği zıt işaret
        alır ve toplandığında **söner** (yıkıcı girişim, H19).
        """
        a = self.ayar
        for b in range(a.kubit_basina):
            u, v = self.yuva(i1, j1, b), self.yuva(i2, j2, b)
            c, s = math.cos(teta), math.sin(teta)
            G = np.eye(4)
            G[2, 2], G[2, 3] = c, -s
            G[3, 2], G[3, 3] = s, c
            if abs(u - v) == 1:
                self.kesme += self.y.cift_kapi_yuva(min(u, v), G)
            else:
                self.kesme += self._uzak(u, v, G)
            self.kapi += 1

    def _uzak(self, u: int, v: int, G: np.ndarray) -> float:
        """Uzak çifte kapı -- takas ağıyla, sonra iade.

        MPO burada kullanılamaz: MPO tek bir operatörü bütün zincire
        yayar, burada ise **tek bir çifte** vurulacak. Takasın bedeli
        ölçülür ve raporlanır (kütük H41: takas dolaşıklığı sürükler).
        """
        if u > v:
            u, v = v, u
        kesme = 0.0
        yer = v
        while yer > u + 1:
            kesme += self.y.takas(yer - 1)
            yer -= 1
        kesme += self.y.cift_kapi_yuva(u, G)
        while yer < v:
            kesme += self.y.takas(yer)
            yer += 1
        return kesme

    # -----------------------------------------------------------------
    #  3. adım: OKU -- POVM zayıf ölçüm, çöküş yok
    # -----------------------------------------------------------------
    def hucre_dagilimi(self, i: int, j: int) -> np.ndarray:
        """``(i,j)`` hücresinin renk dağılımı -- **ortak**, marjinal değil.

        Hücrenin bütün kübitleri birden okunur (``blok_dagilimi`` usulü):
        bitler dolaşık olabilir, ayrı ayrı okunursa yanıltır.
        """
        a = self.ayar
        bas = self.yuva(i, j, 0)
        X = self.y.bag
        A = self.y.A
        L = np.zeros((X, X))
        L[0, 0] = 1.0
        for k in range(bas):
            Ak = A[k].astype(np.float64)
            L = np.einsum("ac,aib,cid->bd", L, Ak, Ak, optimize=True)
        R = np.zeros((X, X))
        R[0, 0] = 1.0
        for k in range(self.y.n - 1, bas + a.kubit_basina - 1, -1):
            Ak = A[k].astype(np.float64)
            R = np.einsum("bd,aib,cid->ac", R, Ak, Ak, optimize=True)
        M = L
        for k in range(bas, bas + a.kubit_basina):
            Ak = A[k].astype(np.float64)
            M = np.einsum("...ac,aib,cjd->...ijbd", M, Ak, Ak, optimize=True)
            sk = M.shape
            M = M.reshape(sk[:-4] + (sk[-4], sk[-3], sk[-2], sk[-1]))
        rho = np.einsum("...bd,bd->...", M, R, optimize=True)
        kb = a.kubit_basina
        rho = rho.reshape([2] * (2 * kb))
        eks = list(range(0, 2 * kb, 2)) + list(range(1, 2 * kb, 2))
        boyut = 2 ** kb
        rho = np.transpose(rho, eks).reshape(boyut, boyut)
        P = np.clip(np.real(np.diag(rho)), 0.0, None)
        t = float(P.sum())
        P = P / t if t > 1e-30 else np.full(boyut, 1.0 / boyut)
        return P[:a.renk] / max(float(P[:a.renk].sum()), 1e-30)

    def izgara_oku(self) -> np.ndarray:
        """En muhtemel ızgara -- her hücrenin âzamî ihtimalli rengi.

        **Bu bir çöküş değildir**: dalga okunduktan sonra da diridir.
        Okunan şey, süperpozisyonda ayakta kalan dağılımın tepesidir.
        """
        a = self.ayar
        out = np.zeros((a.h, a.w), int)
        for i in range(a.h):
            for j in range(a.w):
                out[i, j] = int(np.argmax(self.hucre_dagilimi(i, j)))
        return out

    def izgara_ihtimali(self, g: np.ndarray) -> float:
        """Belirli bir ızgaranın ihtimali (hücre bağımsızlığı varsayımıyla).

        **Varsayım açıkça bildirilir**: hücreler dolaşıksa bu çarpım
        gerçek ortak ihtimal değildir, onun bir alt sınırı yahut kaba
        yaklaşığıdır. Tam ortak ihtimal bütün ızgarayı tek blok olarak
        okumayı ister ve ``4^(h·w)`` boyutunda bir dizey kurar --
        3×3'te 262.144, 30×30'da imkânsız.
        """
        a = self.ayar
        p = 1.0
        for i in range(a.h):
            for j in range(a.w):
                p *= float(self.hucre_dagilimi(i, j)[int(g[i, j]) % a.renk])
        return p
