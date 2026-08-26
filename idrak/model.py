"""Nefs-i Müdrike ARC modeli — risalelerin mimarisinin fiilî hâli.

Bu modül, külliyattaki parçaları **tek bir çalışan modelde** birleştirir:

===========================  =========================================
risaledeki parça             buradaki karşılığı
===========================  =========================================
Reel Hartley süzgeci (§6,15) :class:`HartleySuzgec` -- ve **M29
                             şartıyla**: spektral kazanç çift simetrik
                             tutuluyor, yoksa evrişim olmazdı
KAN kenar fonksiyonu         :class:`KanKenar` -- öğrenilen taban
                             karışımı
41 meleke dik kapıları       :class:`DikKarisim` -- Cayley dönüşümüyle
                             **tam dik** kanal karışımı
Kübit yazmacı                :mod:`idrak.kubit` -- reel dik kapılarla
Müşahede/Tahlil/Terkip       kodlayıcı yığını
Muhakeme/İntaç               çözücü yığını + baş
===========================  =========================================

**Neden bu mimari CPU'da çalışabiliyor.**  Risalenin ``RHT⁻¹ R RHT``
süzgeci bir **evrişimdir** ve ``O(N log N)``dir; dikkat ``O(N²)``dir.
Bağlam 768 belirteçte tam dikkat ~590 bin çift ister, Hartley süzgeci
~7 bin işlem.  Yani risalenin teklifi burada gerçekten işe yarıyor --
ama ancak M29 şartı konursa (çift simetri) o şey bir evrişimdir.

**Nedensellik.**  Hartley karışımı bütün diziyi karıştırır, yani
**nedensel değildir**.  Kodlayıcıda bu bir kusur değil (bağlam tamamen
gözlenmiştir); çözücüde ise nedensellik şart olduğundan orada
Hartley yerine **nedensel evrişim** ve çapraz dikkat kullanılıyor.
Bu ayrım keyfî değil, ölçülebilir: :func:`nedensellik_hatasi`
gelecekteki bir belirteci değiştirip çıktının değişip değişmediğine
bakar.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .arc import DOLGU, SOZLUK
from .kubit import KubitKaydi

__all__ = [
    "VARSAYILAN_BOYUT", "HIZLI_BOYUT", "Ayar", "HartleySuzgec",
    "KanKenar", "DikKarisim", "KodlayiciBlok", "CozucuBlok",
    "NefsModeli", "nedensellik_hatasi", "parametre_sayisi",
]

VARSAYILAN_BOYUT = 512
HIZLI_BOYUT = 128


class Ayar:
    """Model ayarları — varsayılan ``D=512``, hızlı deneme ``D=128``."""

    def __init__(self, D: int = HIZLI_BOYUT, kodlayici: int = 4,
                 cozucu: int = 4, bas: int = 4, kubit_n: int = 4,
                 kubit_derinlik: int = 3, azami_baglam: int = 768,
                 azami_hedef: int = 320, cekirdek: int = 15,
                 sozluk: int = SOZLUK, azami_baglam_ornek: int = 2):
        self.D, self.kodlayici, self.cozucu = D, kodlayici, cozucu
        self.bas, self.kubit_n, self.kubit_derinlik = bas, kubit_n, kubit_derinlik
        self.azami_baglam, self.azami_hedef = azami_baglam, azami_hedef
        self.cekirdek, self.sozluk = cekirdek, sozluk
        self.azami_baglam_ornek = azami_baglam_ornek

    def sozlugu(self) -> Dict[str, int]:
        return dict(self.__dict__)


# ══════════════════════════════════════════════════════════════════════
#  1. Reel Hartley spektral süzgeç (M29 şartıyla)
# ══════════════════════════════════════════════════════════════════════

class HartleySuzgec(nn.Module):
    """``RHT⁻¹ diag(r) RHT`` — dizi boyunca evrişim, ``O(N log N)``.

    **M29:** ``r`` çift simetrik olmalı (``r[k] = r[N−k]``), yoksa
    netice bir evrişim değildir.  Burada ``r``nin yalnız yarısı
    öğrenilir ve simetrik olarak açılır -- şart **yapı gereği**
    sağlanır, sonradan denetlenerek değil.
    """

    def __init__(self, D: int, azami_n: int):
        super().__init__()
        self.D, self.azami_n = D, azami_n
        yari = azami_n // 2 + 1
        self.yari_kazanc = nn.Parameter(torch.ones(D, yari)
                                        + 0.02 * torch.randn(D, yari))

    def kazanc(self, N: int) -> torch.Tensor:
        """``(D, N)`` çift simetrik kazanç."""
        yari = self.yari_kazanc[:, :N // 2 + 1]
        if N % 2 == 0:
            ayna = torch.flip(yari[:, 1:-1], dims=[1])
        else:
            ayna = torch.flip(yari[:, 1:], dims=[1])
        return torch.cat([yari, ayna], dim=1)[:, :N]

    @staticmethod
    def rht(x: torch.Tensor) -> torch.Tensor:
        """``H[k] = Re F[k] − Im F[k]``, ``1/√N`` ölçekli."""
        N = x.shape[-1]
        Fx = torch.fft.fft(x.float(), dim=-1)
        return (Fx.real - Fx.imag) / math.sqrt(N)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """``x``: ``(B, N, D)``."""
        B, N, D = x.shape
        v = x.transpose(1, 2)                      # (B, D, N)
        V = self.rht(v)
        V = V * self.kazanc(N).unsqueeze(0)
        y = self.rht(V)                            # RHT kendi tersi
        return y.transpose(1, 2).to(x.dtype)


# ══════════════════════════════════════════════════════════════════════
#  2. KAN kenarı ve dik karışım
# ══════════════════════════════════════════════════════════════════════

class KanKenar(nn.Module):
    """Öğrenilen taban karışımı — KAN kenar fonksiyonunun ucuz hâli.

    ``φ(x) = Σ_b w_b ψ_b(x)``; taban ``{x, silu(x), sin(x), cos(x)}``.
    Sabit bir etkinleştirme yerine **öğrenilen** bir eğri: risalenin
    "kenar üstünde fonksiyon" fikrinin doğrudan karşılığı.
    """

    def __init__(self, D: int, ic: int = 4):
        super().__init__()
        self.ileri = nn.Linear(D, D * ic)
        self.taban_agirlik = nn.Parameter(torch.tensor([1.0, 1.0, 0.1, 0.1]))
        self.geri = nn.Linear(D * ic, D)
        self.ic = ic

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.ileri(x)
        w = self.taban_agirlik
        h = (w[0] * h + w[1] * F.silu(h)
             + w[2] * torch.sin(h) + w[3] * torch.cos(h))
        return self.geri(h)


class DikKarisim(nn.Module):
    """Cayley dönüşümüyle **tam dik** kanal karışımı.

    ``Q = (I − A)(I + A)⁻¹``, ``A`` yatkın-simetrik ⟹ ``Q ∈ SO(D)``.
    ``reel.meleke``deki 41 kapının öğrenilebilir hâli: diklik
    parametrelemeden gelir, cezayla zorlanmaz.  Norm korunduğu için
    derin yığında ne patlar ne söner.
    """

    def __init__(self, D: int):
        super().__init__()
        self.A_ham = nn.Parameter(0.02 * torch.randn(D, D))
        self.D = D

    def Q(self) -> torch.Tensor:
        A = self.A_ham - self.A_ham.T
        I = torch.eye(self.D, device=A.device, dtype=A.dtype)
        return torch.linalg.solve(I + A, I - A)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x @ self.Q().T


# ══════════════════════════════════════════════════════════════════════
#  3. Bloklar
# ══════════════════════════════════════════════════════════════════════

class KodlayiciBlok(nn.Module):
    """Hartley karışımı (küresel) + dik kanal + KAN."""

    def __init__(self, ayar: Ayar):
        super().__init__()
        D = ayar.D
        self.n1, self.n2 = nn.LayerNorm(D), nn.LayerNorm(D)
        self.suzgec = HartleySuzgec(D, ayar.azami_baglam)
        self.dik = DikKarisim(D)
        self.kan = KanKenar(D)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.dik(self.suzgec(self.n1(x)))
        return x + self.kan(self.n2(x))


class CozucuBlok(nn.Module):
    """Nedensel evrişim + çapraz dikkat + KAN.

    Hartley karışımı burada **kullanılmaz**: nedensel değildir.
    """

    def __init__(self, ayar: Ayar):
        super().__init__()
        D, K = ayar.D, ayar.cekirdek
        self.n1, self.n2, self.n3 = (nn.LayerNorm(D), nn.LayerNorm(D),
                                     nn.LayerNorm(D))
        self.K = K
        self.evrisim = nn.Conv1d(D, D, K, groups=D)
        self.dik = DikKarisim(D)
        self.dikkat = nn.MultiheadAttention(D, ayar.bas, batch_first=True)
        self.kan = KanKenar(D)

    def forward(self, y: torch.Tensor, bellek: torch.Tensor,
                bellek_maske: Optional[torch.Tensor]) -> torch.Tensor:
        h = self.n1(y).transpose(1, 2)
        h = F.pad(h, (self.K - 1, 0))              # NEDENSEL dolgu
        y = y + self.dik(self.evrisim(h).transpose(1, 2))
        h = self.n2(y)
        a, _ = self.dikkat(h, bellek, bellek,
                           key_padding_mask=bellek_maske, need_weights=False)
        y = y + a
        return y + self.kan(self.n3(y))


# ══════════════════════════════════════════════════════════════════════
#  4. Model
# ══════════════════════════════════════════════════════════════════════

class NefsModeli(nn.Module):
    """Kodlayıcı (Hartley) + kübit yazmacı + nedensel çözücü."""

    def __init__(self, ayar: Ayar):
        super().__init__()
        self.ayar = ayar
        D = ayar.D
        self.gomme = nn.Embedding(ayar.sozluk, D)
        self.k_konum = nn.Parameter(0.02 * torch.randn(ayar.azami_baglam, D))
        self.c_konum = nn.Parameter(0.02 * torch.randn(ayar.azami_hedef, D))
        self.kodlayici = nn.ModuleList(
            [KodlayiciBlok(ayar) for _ in range(ayar.kodlayici)])
        self.kubit = KubitKaydi(ayar.kubit_n, ayar.kubit_derinlik, D)
        self.cozucu = nn.ModuleList(
            [CozucuBlok(ayar) for _ in range(ayar.cozucu)])
        self.son = nn.LayerNorm(D)
        self.bas = nn.Linear(D, ayar.sozluk)
        # Şekil başı: çıktı ızgarasının (satır, sütun) sayısı.
        # ÖLÇÜLDÜ: şekil başı yokken model %96 iyi biçimli ızgara
        # üretiyordu ama ŞEKLİ %0 doğruydu -- yani tam eşleşme
        # imkânsızdı. Şekil ayrı ve kolay öğrenilen bir alt problemdir;
        # ayrı baş + kısıtlı çözümleme bu hata sınıfını tamamen kaldırır.
        self.azami_kenar = 30                       # ARC ızgara sınırı
        self.satir_bas = nn.Linear(D, self.azami_kenar + 1)
        self.sutun_bas = nn.Linear(D, self.azami_kenar + 1)

    def kodla(self, baglam: torch.Tensor) -> Tuple[torch.Tensor,
                                                   torch.Tensor,
                                                   torch.Tensor]:
        maske = baglam.eq(DOLGU)
        x = self.gomme(baglam) + self.k_konum[:baglam.shape[1]].unsqueeze(0)
        for blok in self.kodlayici:
            x = blok(x)
        gecerli = (~maske).float().unsqueeze(-1)
        havuz = (x * gecerli).sum(1) / gecerli.sum(1).clamp(min=1.0)
        return x, maske, havuz

    @property
    def cozucu_penceresi(self) -> int:
        """Çözücünün **tam** alıcı alanı: ``katman·(K−1) + 1``.

        Çözücüde y üstünde öz-dikkat **yoktur**; yalnız genişliği ``K``
        olan nedensel evrişim vardır (çapraz dikkat belleğe bakar,
        y'ye değil).  Dolayısıyla ``t`` anındaki çıktı yalnız son
        ``katman·(K−1)+1`` belirtece bağlıdır -- daha eskisi çıktıyı
        **matematiken** değiştiremez.  Üretimde bütün ön eki yeniden
        işlemek bu yüzden gereksizdir; pencere kaydırmak **birebir aynı
        sayıyı** verir (sınamada bitsel eşitlik olarak denetleniyor).
        """
        return len(self.cozucu) * (self.cozucu[0].K - 1) + 1

    def coz(self, bellek: torch.Tensor, maske: torch.Tensor,
            kb: torch.Tensor, hedef_giris: torch.Tensor,
            konum_basi: int = 0) -> torch.Tensor:
        n = hedef_giris.shape[1]
        y = (self.gomme(hedef_giris)
             + self.c_konum[konum_basi:konum_basi + n].unsqueeze(0) + kb)
        for blok in self.cozucu:
            y = blok(y, bellek, maske)
        return self.bas(self.son(y))

    def sekil_tahmini(self, havuz: torch.Tensor
                      ) -> Tuple[torch.Tensor, torch.Tensor]:
        """``(satır, sütun)`` sınıflandırma çıktıları."""
        return self.satir_bas(havuz), self.sutun_bas(havuz)

    def forward(self, baglam: torch.Tensor, hedef_giris: torch.Tensor,
                sekil_de: bool = False):
        bellek, maske, havuz = self.kodla(baglam)
        # kübit yazmacı: bağlamdan evrilen dik kayıt, belleğe eklenir
        kb = self.kubit(havuz).unsqueeze(1)
        c = self.coz(bellek, maske, kb, hedef_giris)
        if sekil_de:
            sa, su = self.sekil_tahmini(havuz)
            return c, sa, su
        return c

    @torch.no_grad()
    def uret(self, baglam: torch.Tensor, azami: int, baslangic: int = DOLGU,
             dur: Optional[int] = None) -> torch.Tensor:
        """Açgözlü üretim — ``(B, azami)`` belirteç.

        **Bağlam bir kere kodlanır.**  İlk hâlde her belirteçte yeniden
        kodluyordum; ölçüldü, değerlendirme buna takılıyordu.  Pahalı
        olan taraf kodlayıcıdır (768 uzunlukta dört Hartley bloğu),
        çözücü ucuzdur -- bir kerelik kodlama üretimi ``azami`` kat
        hızlandırıyor.  ``dur`` verilirse o belirteç bütün yığında
        görülünce erken kesilir.
        """
        bellek, maske, havuz = self.kodla(baglam)
        kb = self.kubit(havuz).unsqueeze(1)
        B = baglam.shape[0]
        y = torch.full((B, 1), baslangic, dtype=torch.long,
                       device=baglam.device)
        for _ in range(azami):
            m = self.coz(bellek, maske, kb, y)[:, -1].argmax(-1, keepdim=True)
            y = torch.cat([y, m], dim=1)
            if dur is not None and bool((y == dur).any(dim=1).all()):
                break
        return y[:, 1:]

    @torch.no_grad()
    def uret_kisitli(self, baglam: torch.Tensor,
                     satir: Optional[int] = None, sutun: Optional[int] = None
                     ) -> Tuple[torch.Tensor, int, int]:
        """**Kısıtlı** çözümleme: tam ``satır × sütun`` ızgara üret.

        Şekil verilmezse şekil başından okunur.  Satır sonu ve ızgara
        sonu belirteçleri **zorlanır**; renk belirteçleri yalnız renk
        aralığından (``0-9``) seçilir.  Böylece çıktı **her zaman**
        iyi biçimli ve istenen şekilde olur; geriye yalnız renkleri
        doğru bilmek kalır.
        """
        from .arc import IZGARA_SONU, RENK, SATIR_SONU
        bellek, maske, havuz = self.kodla(baglam)
        kb = self.kubit(havuz).unsqueeze(1)
        if satir is None or sutun is None:
            sa, su = self.sekil_tahmini(havuz)
            satir = int(sa[0].argmax()) if satir is None else satir
            sutun = int(su[0].argmax()) if sutun is None else sutun
        satir = max(1, min(satir, self.azami_kenar))
        sutun = max(1, min(sutun, self.azami_kenar))
        # Belirteç bütçesi: satır×(sütun+1) hücre/satır-sonu + 1 ızgara
        # sonu + 1 başlangıç.  Konum gömmesi ``azami_hedef`` uzunluğunda
        # olduğundan bütçe aşılırsa satır sayısı KIRPILIR.
        # (Ölçüldü: 30×30 = 931 belirteç isterken bütçe 320'ydi ve
        #  yayın hatası veriyordu -- sınama yakaladı.)
        butce = self.ayar.azami_hedef - 2
        if satir * (sutun + 1) > butce:
            satir = max(1, butce // (sutun + 1))
        B = baglam.shape[0]
        y = torch.full((B, 1), DOLGU, dtype=torch.long,
                       device=baglam.device)
        # HIZ. Bütün ön eki her belirteçte yeniden işlemek O(L²) idi ve
        # 30×30 ızgarada 931 adım ediyordu.  Çözücünün alıcı alanı
        # sonlu olduğundan (bkz. ``cozucu_penceresi``) yalnız son
        # pencere işlenir: O(L). Doğruluktan taviz yok -- sınama
        # ``test_pencere_bitsel_ayni`` bitsel eşitliği denetliyor.
        p = self.cozucu_penceresi
        for i in range(satir):
            for _ in range(sutun):
                t0 = max(0, y.shape[1] - p)
                mant = self.coz(bellek, maske, kb, y[:, t0:], t0)[:, -1]
                r = mant[:, :RENK].argmax(-1, keepdim=True)
                y = torch.cat([y, r], dim=1)
            y = torch.cat([y, torch.full((B, 1), SATIR_SONU,
                                         dtype=torch.long,
                                         device=y.device)], dim=1)
        y = torch.cat([y, torch.full((B, 1), IZGARA_SONU, dtype=torch.long,
                                     device=y.device)], dim=1)
        return y[:, 1:], satir, sutun


def parametre_sayisi(m: nn.Module) -> Dict[str, int]:
    t = sum(p.numel() for p in m.parameters())
    e = sum(p.numel() for p in m.parameters() if p.requires_grad)
    return {"toplam": t, "eğitilebilir": e, "MB_fp32": t * 4 // (1 << 20)}


# ══════════════════════════════════════════════════════════════════════
#  Denetimler
# ══════════════════════════════════════════════════════════════════════

@torch.no_grad()
def nedensellik_hatasi(model: NefsModeli, B: int = 2, N: int = 48,
                       T: int = 24, tohum: int = 0) -> Dict[str, float]:
    """Çözücü nedensel mi? — geleceği değiştir, geçmiş değişmemeli.

    Ayrıca kodlayıcı için aynı ölçüm yapılıyor: orada nedensellik
    **beklenmiyor** ve ölçüm bunu gösteriyor.  İki hüküm yan yana.
    """
    g = torch.Generator().manual_seed(tohum)
    baglam = torch.randint(0, 10, (B, N), generator=g)
    y = torch.randint(0, 10, (B, T), generator=g)
    a = model(baglam, y)
    y2 = y.clone()
    y2[:, T // 2:] = torch.randint(0, 10, (B, T - T // 2), generator=g)
    b = model(baglam, y2)
    gecmis = float((a[:, :T // 2] - b[:, :T // 2]).abs().max())
    gelecek = float((a[:, T // 2:] - b[:, T // 2:]).abs().max())
    # kodlayıcı: bağlamın sonunu değiştir, baştaki temsil değişiyor mu?
    bellek1, _, _ = model.kodla(baglam)
    baglam2 = baglam.clone()
    baglam2[:, N // 2:] = torch.randint(0, 10, (B, N - N // 2), generator=g)
    bellek2, _, _ = model.kodla(baglam2)
    kod_gecmis = float((bellek1[:, :N // 2] - bellek2[:, :N // 2]).abs().max())
    return {"çözücü_geçmiş_değişimi": gecmis,
            "çözücü_gelecek_değişimi": gelecek,
            "kodlayıcı_geçmiş_değişimi": kod_gecmis}


def _gosterim() -> str:
    import time
    s = []
    torch.manual_seed(0)
    ayar = Ayar(D=HIZLI_BOYUT)
    m = NefsModeli(ayar)
    p = parametre_sayisi(m)
    s.append("=== Model (D=%d, hızlı deneme boyutu) ===" % ayar.D)
    s.append("  parametre: %s (%.1f M)   fp32 bellek ~%d MB"
             % (f"{p['toplam']:,}", p["toplam"] / 1e6, p["MB_fp32"]))
    s.append("  kodlayıcı %d blok (Hartley) + çözücü %d blok (nedensel)"
             % (ayar.kodlayici, ayar.cozucu))
    s.append("  kübit yazmacı: n=%d (%d genlik), derinlik=%d"
             % (ayar.kubit_n, 2 ** ayar.kubit_n, ayar.kubit_derinlik))

    s.append("\n=== M29 şartı YAPI GEREĞİ sağlanıyor mu? ===")
    f = HartleySuzgec(8, 64)
    for N in (16, 17, 32):
        k = f.kazanc(N)[0]
        ters = torch.cat([k[:1], torch.flip(k[1:], dims=[0])])
        s.append("  N=%2d  ‖r[k] − r[N−k]‖ = %.2e   ← çift simetri"
                 % (N, float((k - ters).abs().max())))
    s.append("  Kazancın yalnız yarısı öğreniliyor, öbür yarısı ayna.")
    s.append("  Şart sonradan denetlenmiyor; bozulması İMKÂNSIZ.")

    s.append("\n=== Süzgeç gerçekten evrişim mi? (dolaşımlı dizey) ===")
    N = 16
    f2 = HartleySuzgec(1, 32)
    M = torch.zeros(N, N)
    for i in range(N):
        e = torch.zeros(1, N, 1)
        e[0, i, 0] = 1.0
        M[:, i] = f2(e)[0, :, 0]
    c = M[:, 0]
    C = torch.stack([torch.roll(c, i) for i in range(N)], dim=1)
    s.append("  ‖M − dolaşımlı(M)‖ = %.2e   → evrişim mi? %s"
             % (float((M - C).abs().max()),
                bool((M - C).abs().max() < 1e-4)))

    s.append("\n=== DikKarisim gerçekten dik mi? (Cayley) ===")
    for D in (16, 64, 128):
        q = DikKarisim(D).Q()
        s.append("  D=%3d  ‖QᵀQ−I‖ = %.2e   det = %+.6f"
                 % (D, float((q.T @ q - torch.eye(D)).abs().max()),
                    float(torch.linalg.det(q))))

    s.append("\n=== Nedensellik: çözücü nedensel, kodlayıcı değil ===")
    d = nedensellik_hatasi(m)
    s.append("  çözücü:  geçmiş değişimi = %.2e   ← 0 OLMALI"
             % d["çözücü_geçmiş_değişimi"])
    s.append("           gelecek değişimi = %.4f   ← 0 OLMAMALI"
             % d["çözücü_gelecek_değişimi"])
    s.append("  kodlayıcı: geçmiş değişimi = %.4f   ← küresel karışım,"
             % d["kodlayıcı_geçmiş_değişimi"])
    s.append("             nedensellik BEKLENMİYOR (bağlam tam gözlenmiş)")

    s.append("\n=== Hız: Hartley O(N log N) vs dikkat O(N²) ===")
    D = 128
    for N in (256, 768, 2048):
        x = torch.randn(1, N, D)
        h = HartleySuzgec(D, 4096)
        h(x)
        t0 = time.perf_counter()
        for _ in range(5):
            h(x)
        th = (time.perf_counter() - t0) / 5
        att = nn.MultiheadAttention(D, 4, batch_first=True)
        att(x, x, x, need_weights=False)
        t0 = time.perf_counter()
        for _ in range(5):
            att(x, x, x, need_weights=False)
        ta = (time.perf_counter() - t0) / 5
        s.append("  N=%4d  Hartley %7.2f ms   dikkat %7.2f ms   (%5.1f×)"
                 % (N, th * 1e3, ta * 1e3, ta / max(th, 1e-9)))
    s.append("  Risalenin spektral süzgeç teklifi burada GERÇEKTEN")
    s.append("  işe yarıyor -- ama ancak M29 şartıyla evrişim olur.")
    return "\n".join(s)


if __name__ == "__main__":  # pragma: no cover
    print(_gosterim())
