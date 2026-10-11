# VERİ DEFTERİ (F 3-I 261, 262) -- gerçek / hafıza / yoklanamadı

## Gerçek veri (ILO ILOSTAT = TÜİK HİA, 2025; `veri_ilo/`)
- Nüfus, işgücü, istihdam, işsiz, kayıt dışı çalışan: yaş bandı 15-24 … 65+ (`POP/EAP/EMP/UNE/NIFL.csv`).
- Kayıt dışı çalışan 8 659,8 bin: tarım 3 889,5 bin, tarım dışı 4 770,4 bin (%55,1) (`NIFL_ECO.csv`). **Yaşa göre tarım ayrımı yok.**
- İstihdam durumu: ücretli/yevmiyeli 23 353,0 · işveren 1 515,7 · kendi hesabına 5 234,0 · ücretsiz aile işçisi 2 463,7 bin (`EMP_STE.csv`).
- Yaş × eğitim (nüfus, ISCED 2011): 15-24'te 4 950 bin ortaokul, 4 801 bin lise, 753 bin lisans; 25-34'te lisans+yükseklisans+doktora 5 631 bin (`POP_EDU.csv`).
- NEET 15-24: 2 684,3 bin.
- Girişim hayatta kalma (haber aktarımı, TÜİK bülteni birebir okunmadı): 1 yıl %75-78, 5 yıl ~%41,6.
- Kazanç: DİSK-AR aktarımı (Euronews, veri kümesi adı yok; 2022): ücretlilerin %18,1'i asgari ücretin 2 katından fazla alıyor, %33,8'i asgari altında.

## Karar (padişah, F 3-I 262)
Memnun = asgarinin 2 katı ve üzeri; kayıt dışı tarım sayılmaz; ücretsiz aile işçisi namzet.

## Uygulanan (havuz2.py)
m = 0,181 (üst sınır sayılır: asgari ücret payı yıllar içinde arttı, 2022 sonrası oran yoklanamadı); kayıt dışı tarım dışı payı tüm yaşlara %55,1 uniform (**yaşa göre yoklanamadı, kaba**); m tüm kayıtlı istihdama uygulandı (işveren ve kendi hesabına kayıtlılar maaşlı değil, **ayrım yoklanamadı**: pay m olduğundan yüksek çıkabilir, havuz biraz küçük kalır).
Sonuç: havuz 48 851 bin, 16-34 yaş 19 871 bin. Ücretsiz aile işçisi toplam 2 464 bin, tarımda ~2 066 bin (2018 oranı 2,6/3,1 ile çıkarım, yaş dağılımı yok) ayrıca eklenir.

## Yoklanamadı
Eğitim × işgücü durumu (okuyor mu); kazanç dağılımı 2023-2025 ve yaşa göre; kayıt dışının yaşa × sektör kırılımı; ilk yıl geliri ve iflas oranı gençler için; nüfus projeksiyonu 2026-31.

---
# EK (F 3-I 263): padişahın verdiği Orta Vadeli Program/Ekonomik Görünüm ekleri ve yeni bulgular

## Okuma durumu (sayıyla)
- II. İstihdam, Verimlilik, Ücretler ve Gelir Dağılımı (20 sayfa): **baştan sona okundu** (satır metni `veri_ek/`).
- Ekonomik Görünüm Eylül 2026 (82 sayfa): sayfa 1-46 okundu (makro göstergeler, OVP hedefleri, iç ticaret, mal ticareti); 47-82 (hizmet ticareti, yatırım ortamı, serbest bölge, ticaret anlaşmaları) **okunmadı**, modelle ilgisi görülmediği için; ilgisizliği okunmadan söylenmiştir.
- V. Fiyatlar (15 sayfa): sayfa 1-10 okundu; 11-15 okunmadı.
- IV. Kamu Maliyesi (23 sayfa): sayfa 1-7 okundu (borç, merkezî bütçe gelir/gider tabloları); tablo ayrıştırması bozuk, gelir vergisi ve prim kalemleri **güvenle çıkarılamadı** (yoklanamadı).
- I. Üretim ve Yatırım, III. Dış Ticaret ve Ödemeler Dengesi, VI. Mali Piyasalar: **okunmadı** (mikro mükellefiyet modeline girdisi yok; okunmadan söylenmiştir).
- DİSK-AR Asgari Ücret Araştırması 2026 (159 sayfa, Aralık 2025): sayfa 1-21 (genişletilmiş basın özeti) okundu; Bölüm 3-4 ayrıntıları okunmadı.

## Yeni gerçek veri
- Gelir dağılımı (TÜİK GYKA, OVP eki Tablo II.11-17; gelir referansı önceki yıl): Gini 2025 anketi %0,415 (eşdeğer %0,410); P80/P20 7,9; yıllık hanehalkı kullanılabilir gelir ortalaması en düşük %20: 200 100 TL, en yüksek %20: 1 587 404 TL, ortalama 662 414 TL; eşdeğer birey geliri en düşük %10: 85 090 TL/yıl (yaklaşık 7 090 TL/ay), en düşük %20: 106 058 TL/yıl.
- Göreli yoksulluk (eşdeğer gelir medyanının %50'si): sınır 120 575 TL/yıl, 10,93 milyon kişi (%13,0); %60: 144 690 TL/yıl, 17,36 milyon kişi (%20,6).
- İşgücü (2026-II): işsizlik %7,6; genç (15-24) işsizlik %13,3 (kadın %18,3, erkek %10,7); işgücüne katılma 15-24: kadın %32,4, erkek %59,3; istihdam 32 656 bin; ücretli 23 612 bin, kendi hesabına/işveren 6 699 bin, ücretsiz aile işçisi 2 345 bin.
- Ücret: DİSK-AR (TÜİK HİA mikro verisi, 2024): ücretlilerin %46,7'si (8 359 bin) asgari ve altında; %62,5'i asgari +%20 ve altında; **asgarinin iki katından fazla alan yalnız %12,7**; kayıt dışı ücretlilerin %40'ı asgarinin yarısı ve altında, %85,3'ü asgari +%5 ve altında. (Taban: ücretlilerin 17 899 bin; ikincil kaynak, mikro veri yoklanmadı.)
- Enflasyon: TÜFE yıllık 2026-Eylül %29,73; hizmet %37,65; 2025 yıl sonu %30,89. OVP: büyüme 2026 %3,3, 2027 %4,2; işsizlik 2027 %8,0.
- Girişim: MERSİS aktif şirket + ticari işletme + şube 2 673 735 (2026-Eylül), 2 594 461 (2025).

## Uygulanan (havuz3.py)
m değişti: halinden memnun = ücretlilerin %12,7'si (asgarinin 2 katı ve üzeri) ≈ 2 273 bin, yaşlara kayıtlı istihdam payıyla dağıtıldı (yaşa göre kazanç yoklanamadı). Sonuç havuz 50 905 bin; 16-34 yaş 20 742 bin; ayrıca ücretsiz aile işçisi (tarım) ~2 066 bin.

## Hâlâ yoklanamayan
Yaşa göre kazanç; kamu çalışanlarının (memur) memnun sayılıp sayılmayacağı; ilk yıl geliri ve işi bitirme oranı (genç, sermayesiz); kayıt dışının yaşa × sektör kırılımı; eğitim × işgücü durumu.
