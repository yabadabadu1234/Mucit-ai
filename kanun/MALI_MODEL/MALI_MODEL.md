# MİKRO MÜKELLEFİYET MALİ ETKİ MODELİ

Dosyalar: `model.py` (hesap), `analiz.py` (senaryo, tornado, Monte Carlo, varyant), `grafik.py`, `xlsx_uret.py`, `MIKRO_MUKELLEF_MALI_MODEL.xlsx` (canlı formüllü Excel), `sonuc.json`. Grafikler `../GORSELLER/model_*.png`.

**Doğrulama.** Excel'deki formüller (Girdiler, Hesap, Sonuc sayfaları) bağımsız bir formül hesaplayıcısıyla (`formulas` kütüphanesi) çalıştırılıp Python modelinin Orta senaryo çıktılarıyla karşılaştırıldı; 14 kalemde göreli fark 10⁻¹⁵ mertebesindedir. Excel dosyası değerleri önbelleğe almadan kaydedilmiştir; Excel açıldığında kendisi hesaplar. Monte Carlo ve tornado Python'dadır; Excel'de statik değer olarak `Senaryolar_Python` sayfasındadır.

## 1. Yapı

1. **Nüfus.** Katılımcı sayısı $N$ (kararlı durumda); yıllık hasılat $H$ log-normal (medyan $m$ asgari ücret, yayılım $\sigma$), 0,1 ile 24 asgari ücret arasına kırpılmış, 60 geometrik dilimle ayrıklaştırılmış.
2. **Üç tür katılımcı.** (a) yeni: daha önce hiç vergi ve prim ödemeyen; (b) halen kayıtlı ($s$, giriş kapısına rağmen rejime giren; kapı sızıntısı): eski rejimde gelir vergisi (kâr marjı × $H$ üzerinden tarife) ve 4/b primi ödüyordu; (c) ücretli ek gelir ($u$): eski rejimde marjinal oranla ve kısmî uyumla vergi ödüyordu.
3. **Yeni rejim geliri.** $T(H)$ = GVK m.103 genel tarifesi (190.000 TL %15; 400.000'e kadar %20; 1.000.000'a kadar %27; 5.300.000'e kadar %35; üstü %40) uygulanan safi matrah $0{,}7\,H$ (götürü gider %30).
4. **Giderler.** BES aktarımı (tevkifatın %3'ü, vazgeçme payı kadar azalır) ve Devlet katkısı (%20); 90 günlük MYÖ primi hibesi ($H \geq 12$ asgari ücret ve çakışmasız olanlar için $3 \times W \times 0{,}21$); donanım KDV mahsubu (üst sınır tevkifatın %50'si); KGF (kullanım × kefalet × temerrüt × (1 − kurtarma)); PTT UETS; BT tek seferlik ve yıllık; itiraz; denetim.
5. **Sahte fatura.** Kurumsal akıştaki sahte pay $\varphi$, önlem etkinliği kadar azalır; kayıp = hacim × (kurumlar vergisi oranı − etkin tevkifat oranı).
6. **Zaman.** Beş yıl; katılım rampası %25, %55, %80, %100, %100; 1. yılda tek seferlik BT ve PTT; reel iskonto %5; sabit 2026 TL.
7. **Çıktılar.** Yıl yıl net etki, 5 yıllık bugünkü değer, kırılma noktası $s^*$, politika varyantları, tornado, Monte Carlo (4000 deneme, sabit tohum 20261010).

## 2. Girdi tablosu ve durumu

Durum sütunu: **M** mevzuattan okundu, **İ** ikincil kaynak, **H** varsayım (ölçülmemiş, veriyle doldurulacak).

| Girdi | Kötümser | Orta | İyimser | Durum |
| :-- | :-- | :-- | :-- | :-- |
| Medyan hasılat (asgari ücret katı) | 4.0 | 5.0 | 6.0 | H |
| Katılımcı sayısı N | 150000 | 350000 | 700000 | H |
| Kapı sızıntısı s (halen kayıtlı payı) | 0.45 | 0.25 | 0.1 | H |
| Ücretli ek gelir payı u | 0.25 | 0.2 | 0.15 | H |
| Sahte fatura payı φ | 0.02 | 0.01 | 0.005 | H |
| Önlem etkinliği | 0.3 | 0.5 | 0.7 | H |
| 90 gün primi hak edenler | 0.5 | 0.35 | 0.2 | H |
| BES vazgeçme payı | 0.2 | 0.35 | 0.5 | H |
| KGF kullanım oranı | 0.08 | 0.05 | 0.03 | H |
| KGF temerrüt oranı | 0.15 | 0.1 | 0.06 | H |
| Donanım alan payı | 0.5 | 0.4 | 0.3 | H |
| Brüt asgari ücret 2026 | 33.030 | 33.030 | 33.030 | İ (birden çok kaynakta tutarlı) |
| Tarife eşikleri ve oranlar | 103. madde | 103. madde | 103. madde | M |
| MYÖ prim oranı %21, 4/b toplam %35,75 | | | | M (5510 m.81) |
| Devlet katkısı %20 | | | | İ (4632 Ek 1 dipnotu M; 10811 sayılı Karar metni okunmadı) |
| Götürü gider %30, BES %3, hibe prim 90 gün, donanım mahsup tavanı %50 | | | | Teklif hükmü |
| Eski rejim kâr marjı, eski prim ödeme oranı, ücretli uyumu, ücretli marjinal oranı, kurumsal pay, KGF kurtarma, PTT birim, BT giderleri, itiraz oranı ve birim gideri, denetim oranı | bkz. xlsx Girdiler | | | H |


## 3. Sonuçlar (4. yıl, milyar TL)

**Tasarım kararı.** Modelin ilk sürümü (halen kayıtlı olanlara giriş açıkken, s = %45/%25/%10) net etkiyi olumsuz buldu: Orta −5,6, Kötümser −6,9, İyimser +5,6 milyar TL; kırılma noktası s* = %12,6. Bu yüzden teklifte Madde 1 (p) ile **halen kayıtlı olanlara 24 ay giriş kapısı** konuldu ve Geçici Madde 1 (statü geçişi) kaldırıldı. Aşağıdaki sonuçlar kapıyla hesaplanmıştır; s artık kapı sızıntısıdır.

| Kalem | Kötümser | Orta | İyimser |
| :-- | :-- | :-- | :-- |
| Katılımcı (kişi) | 150.000 | 350.000 | 700.000 |
| Kapı sızıntısı s | %8 | %5 | %2 |
| Brüt tevkifat | 2.93 | 8.18 | 18.74 |
| BES ve Devlet katkısı | -0.08 | -0.19 | -0.34 |
| 90 gün prim hibesi | -0.15 | -0.36 | -0.53 |
| Donanım KDV mahsubu | -0.32 | -0.63 | -0.97 |
| Yutulma: vergi | -0.60 | -1.26 | -1.91 |
| Yutulma: SGK primi | -1.36 | -1.98 | -1.59 |
| KGF | -0.11 | -0.13 | -0.10 |
| Sahte fatura | -0.04 | -0.03 | -0.02 |
| BT işletme, itiraz, denetim | -0.09 | -0.16 | -0.29 |
| **Net (Hazine + SGK)** | **+0.17** | **+3.44** | **+12.98** |
| Net, yalnız vergi tarafı | +1.53 | +5.42 | +14.57 |
| 5 yıllık bugünkü değer | +0.21 | +10.13 | +39.08 |

Kırılma noktası: **s* = %12.6** (Orta). Monte Carlo (4000 deneme; s ortalaması %5 varsayımıyla; kapının işlemesine koşullu) 4. yıl net: P5 0.4, P50 3.7, P95 10.8 milyar TL; net > 0 olasılığı %97.

## 4. Varyantlar (Orta, 4. yıl net, milyar TL)

| Varyant | Net |
| :-- | :-- |
| G0 Güncel teklif: 24 ay giriş kapısı var (Orta, s=0,05) | 3.44 |
| G1 Önceki taslak: kapı yok (s=0,25) | -5.62 |
| G2 Kapı sızıntısı yüksek (s=0,10) | 1.18 |
| G3 Kapı sızıntısı çok yüksek (s=0,20) | -3.35 |
| G4 Kapı + götürü gider %25 | 4.10 |
| G5 Kapı + (e) bendi yok: düz %10,5 | 2.87 |
| G6 Kapı + 90 gün prim hibesi yok | 3.80 |
| G7 Kapı + donanım KDV mahsubu yok | 4.07 |
| G8 Kapı yok + geçenler primi yarı oranda sürdürür (s=0,25) | -0.66 |

## 5. Ne anlama geliyor

1. **Net etki, kapının işlediği varsayımıyla pozitiftir**, ancak kötümser senaryoda marj incedir (+0,17). İşaret, s'ye bağlıdır: sızıntı %10'da Orta +1,2; %12,6'da sıfır; %20'de −3,4 milyar TL.
2. Pozitifliği iddia ederken "kapı işlerse" şartı **her yerde** yazılmalıdır. s ölçülmemiştir; kapı e-Devlet ve SGK kayıtlarıyla başvuruda otomatik denetlenebilir, ama aile bireyi adına tescil gibi dolaşma yolları vardır.
3. Bedel: halen kayıtlı esnaf rejime giremez (24 ay bekleyerek girebilir). Eşitlik ve haksız rekabet itirazı doğabilir. Bu bedeli kapının işlevinden ayırmak mümkün değildir.
4. Kademeli oran (Madde 1 (e)) +0,6 milyar TL katkı yapar ve oran arbitrajını kapatır. Götürü gideri %25'e çekmek +0,7 daha getirir ama ana mesajı (%30) değiştirir; uygulanmadı.
5. Model; geri akış karinesi (r) ve kimlik tekliği (s) gibi önlemlerin etkisini yalnız sahte fatura kalemi üzerinden yakalar; bu kalem küçüktür.

## 6. Veri talebi (modelin ölçülmemiş girdilerini kapatacak)

| Girdi | Kurum | İstenen |
| :-- | :-- | :-- |
| s (kapı sızıntısı), eski vergi ve prim | SGK, GİB | Son 24 ayda 4/b sigortalısı veya gelir vergisi mükellefi olup tescil başvurusu yapabilecek kişi sayısı; hizmet ve fikir sektörü hasılat dağılımı; prim tahsilat oranı |
| N, u | TÜİK, GİB | Serbest çalışan ve ek iş yapan ücretli sayısı; 20/B kapsamındaki mükellef sayısı ve hasılatı |
| φ | GİB, MASAK | Hizmet faturalarında sahte fatura oranı |
| BES vazgeçme | EGM | Otomatik katılımda vazgeçme oranı |
| KGF | KGF, Hazine | Mikro ölçek faizsiz finansman temerrüt oranı |
| PTT, BT | PTT, GİB, BDDK | UETS birim gideri; portal ve banka entegrasyon maliyeti |
