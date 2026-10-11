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
