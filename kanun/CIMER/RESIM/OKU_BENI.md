# CİMER'E RESİM OLARAK YÜKLEME REHBERİ (F 3-I 300, 301)

CİMER'e PDF yüklenmediği için (padişahın beyanı) bütün ek paket **sayfa sayfa resim** (PNG, A4, 150 dpi) hâline getirilmiştir. Hiçbir kaynak dosya silinmemiştir; PDF, kod ve Excel dosyaları depoda durur. Resimleri `resimle.py` ve `kapak.py` üretir; kaynak dosya değişirse betik yeniden koşturulur.

**Önerilen yükleme sırası** (CİMER'in resim sayısı ve boyut sınırı yoklanmamıştır; yükleme ekranındaki uyarıya bakınız):
1. `00_KAPAK_KARTLARI/` (3 kart: özet, mali etki, emeklilik): ana iddia, sayfa sayısı az.
2. `A_MURACAAT_METNI/` (8 sayfa): ayrıntılı müracaat.
3. `B_KANUN_TEKLIFI/` (kanun teklifi, gerekçeler, mali matematik, risk cetveli) ve `B2_EK_MADDELER/`.
4. `D_TEBLIG/`, `E_KOMISYON_PAKETI/`, `H_KALAN_RISKLER/`.
5. `F_MALI_MODEL/` (model, parametre tabloları, genç modeli, emeklilik, denetim).
6. `G_GRAFIK_VE_EKRANLAR/` (grafikler, uygulama ekranı taslakları, TBMM hata ekran görüntüsü).
7. `C_DELIL_EKI/` (dayanak kanun metinleri, 33 sayfa; idare mevzuattan okuyabileceği için en sona).
8. `I_KOD/` ve `J_SIMULASYON_CIKTILARI/` (model kodları ve çıktıları; doğrulanabilirlik için).

**Dahil olmayanlar (sebep sayılı):** `ISLAM_UYGUNLUK_DEFTERI.md`, `ISLAM_SIRKET_TURLERI.md`, `TEHLIKE_DEFTERI.md`, `IC_CALISMA_NOTLARI.md`, `ISTIHDAM_*` ve eski taslaklar: iç dosyalardır ve dinî dayanak ifadeleri taşır; devlete giden hiçbir yerde dinî sebep yazılmaz (F 3-I 246, 252). Silinmemiştir.
