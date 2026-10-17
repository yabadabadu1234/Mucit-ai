# DİĞER GİRDİLER: VERİ DURUMU (Ekim 2026)

| Girdi | Veri | Durum |
|:--|:--|:--|
| **s** (halen kayıtlı olanların geçiş payı) | Kayıtlı 4/b kendi hesabına çalışan (Haziran 2025): **2.542.183**; kendi hesabına çalışan toplamı (TÜİK, dolaylı) ≈ 5,2 milyon ([KTO / SGK-TEPAV, Haziran 2025](https://www.kto.org.tr/d/file/konya-istihdam-izleme-bulteni-2025-haziran.pdf)) | Türetilebilir **üst sınır**: kayıtlı payı = 2,54 / 5,20 ≈ **%49**. Modelde s ∈ [0; 0,49]; mevcut 0,30 / 0,15 / 0,05 bu aralığın içinde. Merkezî değer için veri yok. |
| **π** (4/b prim tahsil oranı) | SGK resmî istatistiği bulunamadı | Veri yok; varsayım 0,8 kalır. |
| **φ** (sahte fatura payı) | VDK/GİB'in oran yayını bulunamadı; yalnızca tek bir vergi müfettişliği örneği (4.500 mükellef, 3 milyar TL, yıl ve hasılat oranı belirsiz) ([Bigpara](https://bigpara.hurriyet.com.tr/haberleri/e-fatura)) | Oran türetilemiyor; varsayım kalır. |
| **Sızıntı** (tevkifatı atlatan sahte fatura payı) | Yapısal olarak ölçülemez (kaçak işlemin payı tanım gereği gözlenmez) | Varsayım; duyarlılık raporda. |
| **Kiralama** (kimlik kiralama payı) | Aynı nedenle ölçülemez | Varsayım; duyarlılık raporda. |

Ne yapıldı: s için veriye dayalı üst sınır (%49) kaydedildi; modelde değer değiştirilmedi. π, φ, sızıntı, kiralama için kamuya açık TÜİK/SGK/GİB verisi bulunamadı; bunlar varsayım olarak kalır ve duyarlılıkları `MALI_SIMULASYON_SONUCLARI.md` içindedir.
