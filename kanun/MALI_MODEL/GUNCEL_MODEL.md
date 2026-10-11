# GÜNCEL MODEL -- 11 Ekim 2026 (F 3-I 261, 266-269, 273; padişah: "modeli verilere göre güncelle, tüm modelleri")

Kod: `n_veri.py` (N), `guncel.py` (ayrışım, tek ödeme, stres), `model.py` (güncellenmiş girdi), `analiz.py`, `risk.py`, `g_final.py`, `genc2.py` yeniden koşturuldu; Excel yeniden üretildi. Çıktılar: `*_cikti.txt`, `guncel_out.txt`, `sonuc*.json`. Eski sayılar (N=350 bin vb.) `MALI_MODEL.md`, `MODEL_G.md`, `RISK_SIMULASYONU.md`, `MODEL_GENC2.md`, `KARSILASTIRMALI_HUKUK.md` §D içinde kalmıştır ve **bu dosyadaki sayılarla değişmiştir** (nakz; eski değerler git geçmişindedir).

## 1. Nelerin güncellendiği (sayıyla)
| Girdi | Eski (K/O/İ) | Yeni (K/O/İ) | Dayanak |
| :-- | :-- | :-- | :-- |
| Katılımcı N (kararlı durum) | 150 / 350 / 700 bin | **100 / 331 / 1 096 bin** | Kötümser: padişah "en fazla 100 bin" (F 268). İyimser: padişah oranları (F 269) × ILO 2025: resmî işsiz 22-30 yaş 957 bin × %60 + 31-39 yaş 618 bin × %30 + gayrıresmî 22-30 yaş 1 083 bin × %20 + 30-40 yaş 1 204 bin × %10. **Gayrıresmî = F 273:** iş arayabilecek durumdaki işgücü dışı, emekli ve ev hanımı hariç, çalışamaz hariç; TÜİK t05 2025'e göre potansiyel işgücü (erkek 1 944, kadın 3 185 bin) + "diğer" (775 ve 3 891 bin), yaş dağılımı işgücü dışının yaş payıyla **yaklaştırıldı** (nedene göre yaş kırılımı yoktur). Dar okuma (yalnız potansiyel işgücü): 923 bin. Orta: ikisinin geometrik ortalaması (**Claude'un seçimi**, ölçüm değil) |
| Genç tip payları (`genc2.py`) | okuyor 35%, okumuyor 65% | okuyor-lise 24, okuyor-üni 37, okumuyor lise altı 15, lise 18, lisans+ 6 (%) | Okumayan-çalışmayan 15-24: 2 684 bin, bunların eğitimi 79 bin okuryazar değil, 975 lise altı, 781 lise, 471 meslek lisesi, 378 yükseköğretim (TÜİK t14). Okuyan sayısı = 11 505 − 4 638 istihdam − 2 684 = ~4 183 bin (çalışan öğrenci düşülmemiş). Okuyanın lise/üniversite bölümü **varsayımdır** (24/37) |
| Medyan hasılat, σ | 4/5/6 W, 0,9 | **değişmedi** | Kendi hesabına yıllık ortalama esas iş geliri 348 045 TL (2024; TÜİK GYKA) → medyan ≈ 232 bin (ort/medyan = e^(σ²/2) = 1,5) → 2026 TL (×1,68, TÜFE 2025 %30,89 ve 2026 Eylül yıllık %29,73'ten **kabaca**) ≈ 390 bin gelir ≈ 557 bin hasılat ≈ **17 W**. Bu *mevcut* esnaf içindir; sermayesiz yeni girenin medyanı için **veri yoktur**, bu yüzden 5 W kaldı ve 3-17 W duyarlılığı koşturuldu |
| Prim, vergi, asgari ücret | -- | değişmedi | 141 699 TL/yıl, 4/b %35,75 |

## 2. Yıl-4 net etki (mlr TL), güncel N ile
| | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| **Seçilen (prim sürer)** | +0,71 | **+4,60** | +22,24 |
| Prim kalkarsa | −2,69 | −1,03 | +16,03 |
| Düz %23 tek ödeme, prim kalkar, hibe yok | −0,61 | +7,01 | +45,61 |
| Herkes geçse (s=1), prim sürer | -- | +1,01 | -- |
| 5 yıllık BD | +1,84 | +13,64 | +67,16 |
Monte Carlo (4000): Orta net P5/P50/P95 = 1,29 / 3,98 / 10,70; net>0 olasılığı %100 (prim sürekliliği varsayımı dışarıda). Tornado en büyük etken **N** (100 bin → −3,2; 1,10 milyon → +10,7), sonra medyan hasılat, s, ücretli uyumu.
Risk simülasyonu (`risk.py`) Orta: risksiz +4,60; prim sürekliliği %50 → +1,78; hiç tutmazsa −1,03; bileşik risk +1,32. Kötümser'de prim %50 bile tutsa −0,99. Monte Carlo (prim sürekliliği %25 olasılıkla kısmen tutmaz, vb.): P(net<0) Kötümser %19,4, Orta %5,7 (Model K1: Orta %3,8).
Model G (gelire bağlı, sabit yüksüz) Orta +2,00, Kötümser −1,88, İyimser +27,1; rastgele çekilişte Orta P(net<0) %50,1 (önlemli %28,2), Kötümser %100.
Genç seyri (kalıcı üst segment, %): zor / orta / kolay -- tarafsız 3,1 / 14,0 / 38,0; mevcut kanun kayıtlı 0,0 / 0,7 / 3,2; kayıt dışı 0,1 / 1,0 / 5,0; **Teklif S 1,5 / 7,8 / 25,1**; Model G 0,9 / 4,2 / 14,5. Yani gençte S hâlâ mevcut kanundan çok iyi, fakat tarafsız ölçüye göre eksik (okuyan öğrenci payı artınca hem tarafsız hem S düştü; sebep kanun değil okuma vakti).

## 3. SORU: devleti zarara sokan yalnız SSK/Bağ-Kur primlerinin azalması mı?
**Hayır tek kalem değil; ama işareti çeviren tek kalem odur.** Yıl-4 Orta, mlr TL:
| Kalem | Tutar |
| :-- | --: |
| Brüt tevkifat geliri | +7,73 |
| Vergi yutulması (eskiden daha çok vergi ödeyenin azalması) | −1,72 |
| 90 gün prim hibesi | −0,34 |
| Donanım KDV mahsubu | −0,59 |
| BES + Devlet katkısı | −0,18 |
| KGF, sahte fatura, BT, itiraz, denetim | −0,30 |
| **Prim hariç net** | **+4,60** |
| **Prim kaybı (4/b primi kalkarsa)** | **−5,63** |
| Net (prim kalkarsa) | −1,03 |
Prim hariç bütün giderler brütün %40'ı (3,13 / 7,73); prim kaybı tek başına brütün %73'ü. Kötümser'de aynı: gider 1,24, prim kaybı 3,40, brüt 1,95. Yani **diğer kalemler tek başına zarar yapmaz; prim kaybı yapar**, çünkü eski sistemde en düşük gelirli kişi bile yılda ~113 bin TL (141 699 × tahsilat 0,8) prim öder: 1 W hasılatta eski yük yeni yükün **33,4 katı**, 4 W'de 8,9, 8 W'de 4,8, 24 W'de 1,6 katıdır.
**Sınırlar:** tahsilat oranı 0,8 benim varsayımımdır (harici metin %35-40 dedi, **yoklanmadı**); 4/b'li herkes bu primi ödemez, ödemeyenin primi zaten gelir değildir. Bu yüzden prim kaybı fazla görünüyor olabilir.

## 4. SORU: Fransa gibi tek ödeme alıp SSK'ya vermek
**Düzeltme (isnat değil kayıt):** deftere Fransa için "ciroya oranlı tek ödeme" yazılmıştı; "%15 vergi + kalanı SSK" ifadesi Fransa'dan değil, harici metnin Yol 1'inden ("düz %15, %5 prim payı") gelir. Fransa'nın sayıları bu turda arandı (ikincil kaynaklar, URSSAF birincil sayfası okunmadı): sosyal katkı ciroya karşı BIC hizmet **%21,2**, BNC (serbest meslek) **%26,1** (2026; bir kaynak %25,6 yazıyor, doğrulanmadı), isteğe bağlı vergi *versement libératoire* yalnız **%1,7-2,2**. Yani Fransa'da yükün büyük kısmı **SSK tarafındadır** (toplam yaklaşık %23-28), vergi küçüktür. Kaynak: [propulsebyca](https://propulsebyca.fr/micro-entrepreneur/cotisations-micro-entrepreneur), [swim.legal](https://www.swim.legal/blog/taux-autoentrepreneur-2026-cotisations-impots).
**Modelde:** tek oran r, ciro üzerinden, vergi + SSK birlikte kasaya girer, eski 4/b primi kalkar, hibe ve KDV mahsubu yok. Orta, yıl-4 net (mlr TL); s = rejime geçen mevcut kayıtlı payı:
| s \ r | %5 | %10 | %15 | %20 | %23 | %28 | %35 | %45 | %60 |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| 0,05 | 0,00 | 3,31 | 6,63 | 9,95 | 11,94 | 15,25 | 19,87 | 26,48 | 36,40 |
| 0,15 | −4,29 | −0,97 | 2,35 | 5,67 | 7,66 | 10,97 | 15,59 | 22,20 | 32,12 |
| 0,30 | −10,71 | −7,39 | −4,08 | −0,76 | 1,23 | 4,54 | 9,17 | 15,78 | 25,69 |
| 1,00 | −39,76 | −36,44 | −33,13 | −29,81 | −27,82 | −24,51 | −19,88 | −13,27 | −3,36 |
**Zarar olmaması için gereken oran r\*** (net = 0): 
| s | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| 0,05 | %6,2 | %5,0 | %4,4 |
| 0,15 | %13,6 | %11,5 | %10,2 |
| 0,30 | %24,8 | %21,1 | %18,9 |
| 0,60 | %47,4 | %40,6 | %36,2 |
| 1,00 | %76,2 | %65,1 | %58,0 |
Okunuş: (1) %23 (Fransa'ya yakın) tek ödeme, mevcut kayıtlıların **%31'ine kadar** sızıntıda Orta'da zarar yazmaz; %15'te sızıntı sınırı %19, %35'te %50, bugünkü seçilen tasarımda sınır yoktur. (2) **Herkes geçerse hiçbir makul tek oran yetmez** (r\*=%65): eski primin ciroya oranı 1-4 W'de %93-350'dir. (3) Yani Fransız tarzı ancak **sızıntıyı sınırlayan** bir kapıyla (geriye bakış, prim sürekliliği, yalnız yeni girenler) zarar yazmaz; kapısız ve prim kalkan her tasarımda s büyüdükçe zarar büyür.
**Mevcut stok stresi** (kayıtlı kendi hesabına 2 123 bin = 5 234 − 3 111 kayıt dışı, TÜİK; **tarım Bağ-Kur'u dâhil olabilir**, ayrışmadı): hepsi geçse, prim sürerse net +6,8 (medyan 5 W) ile +16,7 mlr TL (17 W); prim kalkarsa **−234 ile −224** mlr TL (yutulan prim 240,7 mlr TL, tahsilat 0,8 varsayımı ile); düz %23 tek ödeme ile bile −182 ile −129. Bu, prim sürekliliği şartının neden belirleyici olduğunun en sert rakamıdır.

## 5. Zarar olmaması için ne lazım (özet)
1. **Prim sürer** (bugünkü seçim): Orta +4,60, tüm s için pozitif; ya da
2. **Prim kalkar ama sızıntı sınırı vardır:** s ≤ s\* (düz %15 → %19; %23 → %31; %35 → %50; hibe yok, KDV mahsubu yok); ya da
3. **Giriş yalnız yeni girenlere:** s = 0'a yaklaşır, r\* = %4-6.
Tek ödeme oranı arttıkça padişahın F 257 ölçütü (parası yokken yük yok) ciro oranlı olduğu için **bozulmaz**, ama düşük ciroda yüksek oran geçim eşiğini (net asgarinin 1/3'ü) aşındırır; genç seyri modelinde bu ayrıca koşturulmadı (açık iş).

## 6. Hâlâ yoklanamayan / varsayım
Tahsilat oranı π=0,8; "diğer" nedenli işgücü dışının iş arayabilecek sayılması (F 273 sınırı söylenmedi); Orta N'nin geometrik ortalaması; medyan hasılat (yeni girenler); okuyanın lise/üniversite bölümü; Fransa oranlarının birincil kaynağı (URSSAF); tek ödeme oranının davranış etkisi (katılım kaybı) bu tabloda yok.

## 7. F 273 ile değişen (nakz)
İlk sürümde gayrıresmî = bütün işgücü dışı + kayıt dışı tarım dışı alınmıştı (İyimser N 1 966 bin). Padişah emekli ve ev hanımını hariç tuttu, yalnız iş arayabilecek durumdakileri saydı; N 1 096 bine (dar okumada 923 bine) indi ve yukarıdaki bütün sayılar yeniden koşturuldu.

## 8. Muhasebeci mesleğine etki ve Brezilya dersi (padişah itirazı, 11/10/2026)
**Hesap (çıkarım):** muhasebeci ücreti aylık 1 000 TL = yılda 12 000 TL (padişahın F 3-I 257'deki rakamı). Kaybeden yalnız *halen kayıtlı ve muhasebeciyle çalışırken rejime geçenler*dir (yeni girenler zaten müşteri değildi, kayıt dışı veya gelirsizdi). s×N×12 000: Kötümser 30 bin kişi = 0,36; Orta 49,7 bin = 0,60; İyimser 54,8 bin = 0,66 milyar TL/yıl. Üst sınır stresi (kayıtlı kendi hesabına 2 123 bin hepsi geçse): 25,5 milyar TL/yıl. Ücret 12 000 TL varsayımdır, ölçülmemiştir; mesleğin toplam cirosu yoklanamadı.
**Dengeleyici (çıkarım, ölçülmedi):** tevkifat alıcıda kesildiği için kurumsal alıcının uyum işi artar; tavanı (24 asgari ücret) aşanlar defter tutar; gönüllü danışmanlık serbest kalır.
**Brezilya dersi:** MEI'de vergi indirimi yeni firma doğurmadı ve net vergi kaybı yazdı (ISTIHDAM_EMSALLERI E7). Bizde fark: tevkifat alıcıdan kesilir ve gelire oranlıdır; aynı risk: yutulma (s) ve düşük ödemeyle sigorta hakkı. Teklifin emeklilik/sağlık hakkı doğurup doğurmadığı ve geleceğe dönük yükü bu modelde **hesaplanmadı** (açık kalem).
