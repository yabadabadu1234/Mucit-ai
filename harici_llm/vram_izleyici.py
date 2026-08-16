"""
Çalışma sırasında GERÇEK VRAM ölçümüyle "bu GPU'da kaç B (toplu/batched
bağımsız dizi) sığar" sorusunu kendi kendine keşfeden ve GERÇEK sayıya
göre çalışan B'yi ayarlayan modül.

Neden bu tasarım:
  - Teorik hesap (bkz. sohbet: ~39 MB/B) yalnızca bir TAHMİNDİR; gerçek
    değer modelin tam boyutuna, PyTorch'un caching allocator'ının
    davranışına ve GPU'ya göre değişir. Bu yüzden değeri VARSAYMAK yerine
    ÇALIŞMA SIRASINDA ölçmek gerekir.
  - Log israfı: her token'da/adımda basmak (eski "her 20 tokende" hatası
    gibi) logu boğar. Hiç basmamak da (yalnızca bir kere, başlangıçta)
    bulunamaz/kaybolur. Bu yüzden: HER GÖREV ÇÖZÜMÜNDEN SONRA (token
    başına değil, görev başına) TEK SATIRLIK bir özet log basılır; azami-B
    tahmini DEĞİŞTİĞİ anda ayrıca (o an, geciktirmeden) belirgin bir log
    daha basılır.
  - OOM'a karşı pay: kullanıcının açık talimatı gereği SADECE 1 B'lik pay
    bırakılır (aşırı tedbirli büyük bir güvenlik marjı DEĞİL) -- çalışan B
    her zaman "azami güvenli B" - 1'dir.

Ölçüm stratejisi:
  1. İlk ölçüm noktasında (tek B değeri) henüz B-başına marjinal bellek
     maliyeti bilinmediğinden, B 1'er 1'er ihtiyatla artırılır (128, 129,
     130, ...).
  2. İKİ farklı B için ölçüm birikince, B başına GERÇEK marjinal bayt
     maliyeti (ölçülen fark / B farkı) hesaplanır ve kalan boş VRAM bu
     marjinal maliyete bölünerek azami B'ye DOĞRUDAN sıçranır (emin
     olunduğunda 129, 130 diye sürünmeye gerek yoktur).
  3. Gerçek bir CUDA OOM (torch.cuda.OutOfMemoryError / torch.OutOfMemoryError)
     yakalanırsa azami güvenli B kesin olarak "OOM'a düşen B - 1" yapılır.
"""
import os
import time
from typing import Any, Callable, List, Optional, Tuple

from transkript import transkript_satiri_yaz

_ONEK = "[vram_izleyici]"


def _cihaz_indeksi(cihaz: str) -> int:
    if ":" in cihaz:
        return int(cihaz.split(":")[-1])
    return 0


class VramTabanliBKesifcisi:
    """Bir GPU (cihaz) için "kaç B sığar" sorusunu görev görev ölçerek
    kendi kendine kesinleştirir. `bellek_olcer` ve `bellek_sifirla` test
    edilebilirlik için enjekte edilebilir (gerçek CUDA olmadan da bu
    sınıfın MANTIĞI sınanabilsin diye) -- varsayılanları gerçek
    `torch.cuda` çağrılarıdır.
    """

    def __init__(
        self,
        cihaz: str,
        baslangic_b: int = 128,
        guvenlik_orani: float = 0.93,
        bellek_olcer: Optional[Callable[[str], Tuple[int, int]]] = None,
        bellek_sifirla: Optional[Callable[[str], None]] = None,
        log_yaz: Callable[[str], None] = print,
        transkript_yaz: Callable[[dict], None] = transkript_satiri_yaz,
    ) -> None:
        self.cihaz = cihaz
        self.aktif_b = baslangic_b
        self.guvenlik_orani = guvenlik_orani
        self._bellek_olcer = bellek_olcer or _gercek_bellek_olcer
        self._bellek_sifirla = bellek_sifirla or _gercek_bellek_sifirla
        self._log_yaz = log_yaz
        self._transkript_yaz = transkript_yaz

        self.olcumler: List[Tuple[int, int]] = []  # [(b, kullanilan_bayt), ...]
        self.azami_guvenli_b: Optional[int] = None  # OOM'suz çalıştığı KANITLANMIŞ/hesaplanmış tavan
        self.gorev_sayaci = 0

    # ------------------------------------------------------------------
    def calisan_b(self) -> int:
        """Kullanılacak (bir sonraki görev için) B: azami güvenli B
        biliniyorsa ondan TAM OLARAK 1 eksiği (kullanıcının istediği tek
        birimlik pay), bilinmiyorsa hâlâ ihtiyatla artan aktif_b."""
        if self.azami_guvenli_b is not None:
            return max(1, self.azami_guvenli_b - 1)
        return self.aktif_b

    # ------------------------------------------------------------------
    def gorev_sonrasi_olc_ve_ayarla(self) -> int:
        """Bir görev/batch BAŞARIYLA çözüldükten HEMEN sonra çağrılır.
        O ana kadarki azami bellek kullanımını okur, tahmini günceller,
        HER ZAMAN bir özet log basar (görev başına -- ne token başına
        spam, ne de hiç görünmeyen tek seferlik bir log), tahmin
        DEĞİŞTİYSE ayrıca bir "yeni tavan" logu basar. Bir sonraki görev
        için kullanılacak B'yi döndürür."""
        self.gorev_sayaci += 1
        kullanilan_b = self.aktif_b
        kullanilan_bayt, toplam_bayt = self._bellek_olcer(self.cihaz)
        self._bellek_sifirla(self.cihaz)
        self.olcumler.append((kullanilan_b, kullanilan_bayt))

        eski_azami = self.azami_guvenli_b
        self._tahmini_guncelle(kullanilan_b, kullanilan_bayt, toplam_bayt)

        self._ozet_logu_bas(kullanilan_b, kullanilan_bayt, toplam_bayt)
        if self.azami_guvenli_b != eski_azami:
            self._tavan_degisti_logu_bas(eski_azami)

        # Bir sonraki denemede kullanılacak B'yi belirle.
        if self.azami_guvenli_b is None:
            self.aktif_b = kullanilan_b + 1  # marjinal maliyet henüz bilinmiyor -> ihtiyatla +1
        else:
            self.aktif_b = self.calisan_b()
        return self.aktif_b

    # ------------------------------------------------------------------
    def oom_bildir(self, basarisiz_b: int) -> int:
        """Gerçek bir CUDA OOM yakalandığında çağrılır: azami güvenli B
        KESİN olarak basarisiz_b - 1'e sabitlenir (artık tahmin değil,
        kanıtlanmış sınır). Bir sonraki çalışacak B'yi döndürür."""
        eski_azami = self.azami_guvenli_b
        self.azami_guvenli_b = max(1, basarisiz_b - 1)
        self._bellek_sifirla(self.cihaz)
        self._log_yaz(
            f"{_ONEK} ({self.cihaz}) OOM alındı (B={basarisiz_b}): azami güvenli B KESİN "
            f"olarak {self.azami_guvenli_b}'ye sabitlendi (kanıtlanmış sınır, artık tahmin değil)."
        )
        self._transkript_yaz({
            "tur": "vram_b_tespiti", "cihaz": self.cihaz, "oom": True,
            "oom_b": basarisiz_b, "azami_guvenli_b": self.azami_guvenli_b,
            "calisan_b": self.calisan_b(),
        })
        if self.azami_guvenli_b != eski_azami:
            self._tavan_degisti_logu_bas(eski_azami)
        self.aktif_b = self.calisan_b()
        return self.aktif_b

    # ------------------------------------------------------------------
    def _tahmini_guncelle(self, b: int, kullanilan_bayt: int, toplam_bayt: int) -> None:
        hedef_ust_sinir = int(toplam_bayt * self.guvenlik_orani)

        farkli_b_olcumleri = sorted(set(self.olcumler))
        if len(farkli_b_olcumleri) >= 2:
            # GERÇEK marjinal maliyet: iki (farklı) B ölçümü arasındaki
            # bayt farkını B farkına bölerek B-başına GERÇEK bedeli çıkar
            # (varsayılan/teorik bir sayı değil, ölçülmüş bir sayı).
            (b1, m1), (b2, m2) = farkli_b_olcumleri[0], farkli_b_olcumleri[-1]
            if b2 != b1:
                b_basina_marjinal = (m2 - m1) / (b2 - b1)
                if b_basina_marjinal > 0:
                    kalan_pay = hedef_ust_sinir - kullanilan_bayt
                    ek_b = int(kalan_pay // b_basina_marjinal)
                    yeni_azami = max(1, b + ek_b)
                    # Emin olduğumuzda (marjinal maliyet ölçüldü) DOĞRUDAN
                    # tavana sıçranır -- 129, 130 diye sürünmeye gerek yok.
                    self.azami_guvenli_b = yeni_azami
                    return

        # Henüz marjinal maliyet ölçülemedi (tek nokta) -> hâlâ pay varsa
        # ihtiyatla 1 artırmaya devam (gorev_sonrasi_olc_ve_ayarla zaten
        # aktif_b'yi +1 yapıyor); pay YOKSA (eşiği aştıysak) mevcut B'yi
        # tavan kabul et.
        if kullanilan_bayt >= hedef_ust_sinir:
            self.azami_guvenli_b = b

    # ------------------------------------------------------------------
    def _ozet_logu_bas(self, b: int, kullanilan_bayt: int, toplam_bayt: int) -> None:
        kullanilan_gb = kullanilan_bayt / (1024 ** 3)
        toplam_gb = toplam_bayt / (1024 ** 3)
        tavan_metni = str(self.azami_guvenli_b) if self.azami_guvenli_b is not None else "henüz kesinleşmedi"
        mesaj = (
            f"{_ONEK} ({self.cihaz}) görev #{self.gorev_sayaci}: B={b} ile {kullanilan_gb:.2f}/{toplam_gb:.2f} GB "
            f"VRAM kullanıldı | azami güvenli B tahmini: {tavan_metni} | çalışan B (1 pay ile): {self.calisan_b()}"
        )
        self._log_yaz(mesaj)
        self._transkript_yaz({
            "tur": "vram_b_tespiti", "cihaz": self.cihaz, "gorev_no": self.gorev_sayaci,
            "b": b, "kullanilan_bayt": kullanilan_bayt, "toplam_bayt": toplam_bayt,
            "azami_guvenli_b": self.azami_guvenli_b, "calisan_b": self.calisan_b(),
        })

    def _tavan_degisti_logu_bas(self, eski_azami: Optional[int]) -> None:
        self._log_yaz(
            f"{_ONEK} ({self.cihaz}) *** AZAMİ GÜVENLİ B TAHMİNİ GÜNCELLENDİ: "
            f"{eski_azami} -> {self.azami_guvenli_b} (çalışan B şimdi {self.calisan_b()}) ***"
        )


def _gercek_bellek_olcer(cihaz: str) -> Tuple[int, int]:
    import torch
    idx = _cihaz_indeksi(cihaz)
    kullanilan = torch.cuda.max_memory_allocated(idx)
    toplam = torch.cuda.get_device_properties(idx).total_memory
    return kullanilan, toplam


def _gercek_bellek_sifirla(cihaz: str) -> None:
    import torch
    idx = _cihaz_indeksi(cihaz)
    torch.cuda.reset_peak_memory_stats(idx)


def oom_korumali_calistir(kesifci: VramTabanliBKesifcisi, b_ile_calistiran_fn: Callable[[int], Any]) -> Any:
    """`b_ile_calistiran_fn(b)`'yi kesifci'nin şu anki çalışan B'siyle
    çağırır; gerçek bir CUDA OOM alınırsa kesifci'ye bildirir, belleği
    temizler ve DAHA DÜŞÜK B ile (kesifci.calisan_b()) TEKRAR dener --
    böylece tek bir OOM koşusu ne çökertir ne de aynı hatayı sürekli
    tekrarlar."""
    import torch

    while True:
        b = kesifci.calisan_b()
        try:
            return b_ile_calistiran_fn(b)
        except torch.OutOfMemoryError:
            torch.cuda.empty_cache()
            kesifci.oom_bildir(b)
            if kesifci.calisan_b() >= b:
                raise  # tavan düşmedi -- tekrar denemek sonsuz döngüye yol açar, pes et
