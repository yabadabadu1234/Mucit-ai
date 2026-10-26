# Gaye ağacı şeması (sürüm 2)

Kayıt: CLAUDE.md § 3-I 333, 334, 335, 336. Sürüm 1 (`id · tur · tasiyici · ufuk · kip · ilim_cinsi · seviye · icerik · kapanis_testi · ust · ayrisim · onkosul · dogan_karar · devir` ve karar alanları) **bâkîdir**; sürüm 2 ona alan ve denetim ekler. Dosya `"sema": 2` taşıyorsa `karar_denetle.py` yeni denetimleri koşturur. Fâtiha ve 83:1-6 sürüm 2'dedir. Her alanın yanında kaynağı, denetimi ve ayırt etme sınaması yazılıdır (§ 3-B 27-B).

## 1. Gaye alanları

| Alan | Mânâsı | Kaynak (sayfadan okundu) | Denetim | Sınama |
| :-- | :-- | :-- | :-- | :-- |
| `mevzu` | Gayenin kazıyyesi: muhatabın tasdik edeceği, murâd edeceği ya da tanıyacağı şey | G&S s. 199–201: `Murâd eder(Mütekellim, Hâl(Muhatap, Mevzu))` | dolu olmalı | `mevzu veya sual yok` |
| `sual` | Gayenin zımnî sualı; cevabı âyette | Riester s. 8–10; § 3-I 332 | dolu; `sual_denetle.py` verilmişlik ve çıpa alâkası ölçer | `sual_denetle.py` (21 gaye: yeni mefhum yok 7, sızıntı 5, uydurma 9) |
| `ust_bag` | Her `ust` kenarı için `{bag, sual_turu, gerekce}` | G&S s. 200–201 (teyid, tevlid, hâkimiyet); Riester s. 6, 17 (söylem bağı = sual şablonu) | her kenar yazılı; `bag` ∈ {teyid, tevlid, tarif, karisik}; `sual_turu` ∈ {ne, nasil, neden, hakkinda_ne, paralel, nereden, kim}; teyid iki tasdik, tevlid iki irade, tarif iki tasavvur arasında; **karışık bağ aynı türde olamaz ve gerekçesiz olamaz** | 3 sınama |
| `kifaye` | Çocukları üst gayeyi **tam mı kısmen mi** kapatır; muhatabın bildiği sayılan malûmat | G&S s. 200 (söylem kifayeti) | her çocuklu gayede; kısmî ise malûmat boş olamaz; derece `hipotez` | 2 sınama |
| `alt_sira` | Alt sualler dizisi (Roberts'ın `Strat(q)`'sı) | Roberts (12); G&S SP | çocukların dizilişi olmalı; kardeşler arası `onkosul` sırası bozulamaz | 1 sınama |
| `sikler`, `hasr` | `taksim` gayesinin şıkları ve şıkların tamlığının dayanağı | Roberts (1) q-şık; § 3-I 207 | şıklar çocuklara eşit; `hasr.usul` ∈ {akli, nakli} ve gerekçeli; naklî hasr sayılır ve "kat'î değil" diye raporda görünür | 2 sınama |
| `oncul` | Sualın öncülü olan gayeler | Roberts (26), (28); Riester K2 | her öncül gaye, bu gayenin **etkin ön şartları** içinde olmalı (öncül tarifi ile `onkosul` aynı şeyi söylemeli) | 1 sınama |
| `capa` | Sualın doğduğu yer: `{ayet, blok}` ya da `kok` | QUDEVAL s. 3, DCQA s. 3–4 | çıpa konumu ilk cevaptan **kesin evvel** olmalı (blok mertebesinde) | 1 sınama |

## 2. Karar alanları

| Alan | Mânâsı | Kaynak | Denetim | Sınama |
| :-- | :-- | :-- | :-- | :-- |
| `odak` | Her gaye için cevaplayan bloklar | Riester T1 (odak boş olamaz) | her gaye için dolu; bloklar karşılığın içinde | 2 sınama |
| `fon` | Verilmiş malzeme olan bloklar | Riester T1 | odak ile çakışamaz | 1 sınama |
| `mesele_disi` | Cevaptan çıkarılsa cevap kalan blok; ya `alt_gaye`ye ya `devir`e bağlı | Riester T2 | alt gayenin kararı o bloğu **tekrar ediyor** ya da aynı âyeti kapsıyor olmalı | 1 sınama |
| (kapsam) | Karşılık âyetlerinin bütün blokları ya odak, ya fon, ya mesele dışıdır | Riester (cevabın bütün parçası bir işlev taşır) | **bölüntü**: kapsanmayan blok kusurdur | 1 sınama |
| `tekrar` | Daha evvel geçen bloğun yinelenmesi | Nakarat (§ 6 #4) | **Arapça metinler harekesiz eşit olmalı**; kaynak konumu hedeften evvel | 1 sınama |
| `paralel` | Ortak fonlu paralel cevaplar | Riester K5 | gayeler **kardeş** (aynı `ust` kümesi) ve karara bağlı | 1 sınama |
| `isaret` | Parçanın başındaki işaret: `edat`, `iltifat`, `emir`, `isaret_zamiri`, `yok` | G&S Şekil 12 (s. 198) | sicilde olmalı | 1 sınama |
| `daraltma` | "Yalnız" kalıbı: daraltılan hüküm ve elenen ihtimaller | Roberts (31)–(35) | blok karşılıkta, elenen boş olamaz | — |
| `cevap_uygunlugu` | Her gaye için {dogrudan, odaksiz, cevaplamaz} | QUDEVAL Q3 | her gaye için; **cevaplamayan karar kusurdur** | 1 sınama |

## 3. Türetilen (saklanmayan) çıktılar

| Çıktı | Kaynak | Nerede |
| :-- | :-- | :-- |
| Yığın işlemleri: itme, çıkarma, aynı, kesinti | G&S s. 180, 196–198 | `yigin_islemleri` (Fâtiha 8 itme / 7 çıkarma / 0 kesinti; 83:1-6 4 / 2 / 0) |
| Sıkı sual ağacı, `F` odak, `MD` mesele dışı, `BG` fon işaretli | Riester s. 11 | `python3 karar_denetle.py --agac` |
| Bağ türü sayısı | G&S + Riester | `sema2.bag_*` (Fâtiha: tarif 7, tevlid 5, **karışık 8**) |
| Kısmî ve tam kifaye sayısı | G&S s. 200 | `sema2.kifaye_*` (Fâtiha: kısmî 3, tam 3) |

## 4. Bu şemanın yakaladığı gerçek kusurlar

1. **Sual öncülü eksik ön şartı gösterdi.** `I4` ("İstenen doğru yol nasıl bir yoldur?") ve `I6` ("İstenen hidayet nereden gelir?") sualleri talebin yapılmış olduğunu öncüller (`I5`). Sürüm 1'de `I4` ve `I6`'nın `onkosul`u boştu. Düzeltildi: `onkosul: [I5]`.
2. **83:1'in yeri artık zorunlu.** `W6` ("Eksik ölçenler kimlerdir?") sualı eksik ölçenlerin anılmış olmasını öncüller (`W2`). Bu yüzden 83:1-6'nın geçerli sıralama sayısı **4'ten 1'e** indi; sürüm 1'deki "83:1'in yeri zorunlu değil, dikkat için başa konmuş" hükmü nakzedildi.
3. **Mesele dışı malzeme ve nakarat bir arada çıktı.** 1:1'in "Rahmân ve Rahîm olan." bloğu `I1d`'nin cevabında mesele dışıdır (çıkarılsa "Adıyla Allah'ın" cevap kalır); aynı blok 1:3'te `I1b`'nin odağı olarak **harekesiz aynen** tekrar eder (`tekrar` denetimi eşitliği doğruladı). Sürüm 1'de nakarat örneği sıfırdı; ilk örnek bu.
4. **Karışık kenar sayıldı.** Fâtiha'da 8 kenar saf inanç ya da saf eylem hâlinin dışındadır; her biri gerekçesini yazmak zorunda.
5. **Cevap uygunluğu "odaksız".** `H1`, `H2`, `H3` (his gayeleri) cevabı içerir ama odak değildir: his, âyette söylenen şeyin neticesidir, söylenen şey değildir.

## 5. Dönüşmeyen formüller ve sebebi

| Formül | Kaynak | Dönüşmedi, çünkü |
| :-- | :-- | :-- |
| Beklenen fayda `Σ P(g)·U(g, r)`, pişmanlık `max_r U(g, r) − U(g, r*)`, lojistik karar `P(r_cq) = Lojistik(τ·(BeklenenPişmanlık − c))` | Tsvilodub vd. 2026 | `P(g)` ve `U(g, r)` ölçülemez (gaye dağılımı ve fayda); model sınaması § 3-I 336 ile durduruldu. `elenen` alanı pişmanlığın niteliksel karşılığıdır |
| Kelime şaşırtıcılığı `−log p(u_t \| u_<t)`, belge şaşırtıcılığı, PMI | Tsipidi vd. 2024 | Ölçüm modele dayanır; § 3-I 336 ile durduruldu. `isaret` alanı, ölçüm yerine **sicil** olarak tutulur |
| Sual iktiza `⊨` ve q-şık kümesi | Roberts 2012 (1), (8), (9) | q-şık `sikler`e girdi; iktiza Riester T3 ile gevşetildi (alt sual iktiza edilmeyebilir) |
| Odak şıkları `‖β‖` ve uygunluk `‖β‖ = q-şık(α)` | Roberts (24)–(29) | `odak` bloğu seçilir; sualin şıklarıyla eşitliği sayıyla denetlenemiyor (şık kümesi üretilmiyor) |
| Hâkimiyet `DOM` ve takaddüm `SP` | G&S s. 179 | **Dönüştü:** `ust` ve `onkosul`; denklikler `ust_bag.bag` türüne |
| Destek ve tevlid formülleri F3–F6 | G&S s. 200–201 | **Dönüştü:** `ust_bag`, `kifaye`, `oncul` |
