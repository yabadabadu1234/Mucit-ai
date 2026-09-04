# KÜME 8 ve NAZIRLIK KATI -- terkip plânı

> Padişahın emri (özet): *"Haftalardır el sürülmemiş `yaklasim/`,
> `olcek/`, `arama/` klasörlerinin cevherini çıkarıp faal dosyalara
> dağıt; dağıtılamayacak kadar güzel ve kategori olarak ayrı cevher
> varsa ayrı dosya kur. İmha yok, cevher toplama var. Fonksiyon
> isimleri yeterince halkça değil -- uzunluk halkçalık değildir.
> İsim, yapılan işi en az kelimeyle en çok yönden kapsamalı ve
> projede alacağı rolü doğrudan tarif etmeli. Main'e geçmeden evvel
> ara nazırlıklar tanımla."*

---

## 0. ÖLÇÜLEN VAZİYET

    yaklasim/   son dokunuş 2026-08-24   (11 gün)   1 713 satır, 7 dosya
    olcek/      son dokunuş 2026-08-25   (10 gün)     686 satır, 2 dosya
    arama/      son dokunuş 2026-08-25   (10 gün)     910 satır, 2 dosya
                                          TOPLAM    3 309 satır (+ 621 satır sınama)

Hiçbiri Küme 1-7 terkiplerine girmedi. Üçü de `tanilama/divan.py`da
kayıtlı fakat **hiçbir faal dosya bunlardan bir şey çağırmıyor.**
Ayrı gayrılıkları buradan geliyor: kütükte varlar, akışta yoklar.

**Ölçülen çakışmalar** (tahmin değil, gövde kıyası):

| iddia | ölçüm | hüküm |
|---|---|---|
| `tikizlik.zorlayici_mi` ↔ `geometri.zorlayici_mi` | 36 / 37 satır, **gövdeler ayrı** | aynı suâlin iki hesabı -- terkip |
| `genisletme.lan/ran` ↔ `geometri.lan/ran` | **3** satır / **42-44** satır | yaklasim'daki taslak; hakikî olan geometride -- toprak |
| `bukum.holonomi` ↔ `zirh` homotopi | 3 satır / 20 satır | zırhınki asıl; arama'nınki ince -- ama `cevrim_egriligi`, `aharonov_bohm` **yeni cevher** |
| `olcek/hiz` ↔ `nefs/hiz` | isimler tamamen ayrık, konu **aynı** | tek defter olmalı -- terkip |
| `modern.KAN211/FourierIslemci` ↔ `geometri.KAN/FNO` | geometride **yapı**, modernde **tâlim** | ikisi ayrı şey -- birleşir |
| `nedensel` ↔ `fitrat` | fitratta `budayarak_mudahale` var | nedensel çoğunlukla gösteri -- ölçümü alınır |
| `simgesel.ara/bic` ↔ `izgara.sembolik_kapanis` | izgarada yalnız kapanış var | asıl arama simgeselde -- cevher |

---

## 1. İSİM KAİDESİ -- üç şart ve üç kat

### Üç şart

1. **Rol söyler, mekanizma söylemez.** İsim *"bu ne hesaplıyor"*a
   değil, *"bu, dimağın neresi"*ne cevap verir.
2. **Az kelime, çok yön.** Asıl olan **tek kelimedir**; iki kelime
   hadd-i azamîdir. Uzunluk halkçalık değildir -- tam tersine, uzun
   isim ismin işini yapamadığının itirafıdır.
3. **Main kaybolsa yeniden yazdırsın.** İsimleri okuyan adam mimarîyi
   kurabilmelidir. `bu_hukum_bu_modelde_tutuyor_mu` bunu yapmaz;
   `hoca`, `vicdan`, `zayif_halka` yapar.

### Üç kat -- ve hangi katta hangi isim

Bu ayrım kaidenin kendisi kadar mühimdir; hepsine aynı isim usulünü
uygulamak yanlış olur.

| kat | dizin | isim nev'i | misal |
|---|---|---|---|
| **Alt kat -- âlet** | `matematik/`, `kuantum/` | **hakikî riyazî isim.** Burada `gradyan` gradyandır, `christoffel` Christoffel'dir. Dünya görüşü ismi vermek burada **yanlıştır**: kütüphane herkesin malıdır. | `hartley`, `kapi`, `metrik`, `riemann` |
| **Orta kat -- uzuv** | `nefs/`, `ogrenme/`, `idrak/` | **rol ismi.** Bu dosyalar bize aittir; isim projedeki vazifeyi söyler. | `hoca`, `vicdan`, `bak`, `kalip`, `zayif_halka` |
| **Üst kat -- nazırlık** | `nefs/` (yeni altı dosya) | **fiil.** Tek kelime, emir kipi. Main bunlarla cümle kurar. | `gor`, `dusun`, `ara`, `tart`, `ogren`, `soyle` |

Sembolleşme tam da budur: alt kat açık formül, orta kat sembol, üst
kat cümle. Main artık alt kata bakmadan düşünür.

### İSLAH CETVELİ -- verdiğim isimlerin tashihi

**Orta kat (rol ismi olmalı):**

| şimdiki | olacak | niçin |
|---|---|---|
| `mantigi_tek_supurmede_isaretle` | **`vicdan`** | yasağı, söylenmeden bilir; MPO işaret çekirdeğinin projedeki rolü budur |
| `zirh_giydir` | **`zirhla`** | fiil, tek kelime |
| `delikleri_say` | **`delik`** | "kaç delik var" -- sayının kendisi |
| `ek_yeri_tutuyor_mu` | **`yama`** | demet yapıştırması; yama tutar yahut tutmaz |
| `yolun_farki` | **`iz`** | yol geri döndüğünde bıraktığı fark |
| `cikti_ne_kadar` | **`kalip`** | çıktının hangi kalıba döküleceği |
| `musahede_et` | **`bak`** | on beş kanallı duyu; bakmak |
| `izafi_oteleme` | **`kaydir`** | |
| `belirtecten_aciya` | **`kopru`** | belirteç ile açı arasındaki köprü (asıl dosya adıydı) |
| `sahitleri_ayir` | **`sahitler`** | |
| `kaideyi_coz` | **`kaide`** | |
| `ortu_kapaniyor_mu` | **`ortu`** | |
| `bilgi_metrigi` | **`yokus`** | hangi yön yokuş, hangisi düz -- Fisher metriğinin rolü |
| `zayif_halkaya_gore_topla` | **`zayif_halka`** | zincir en zayıf halkası kadar; atasözü zaten formülün kendisi |
| `taahhude_dokundu_mu` | **`sozunde_mi`** | meleke sözünde mi durdu |
| `bu_meleke_dusse` | **`eksilt`** | bir uzvu eksilt, ne kaybediliyor gör |
| `icinden_gecir` | **`suz`** | funktörün süzgeci |
| `terkip_iyi_tipli_mi` | **`terkip_saglam_mi`** | |

**Alt kat (riyazî isim kalır; yalnız uzunluk kırpılır):**

| şimdiki | olacak |
|---|---|
| `bu_hukum_bu_modelde_tutuyor_mu` | `tutuyor_mu` |
| `tabloda_ne_yaziyor` | `hukum` |
| `borc_mu_caiz_mi_yasak_mi` | `odev` |
| `bundan_sonra` | `sonra` |
| `ikisi_birden_ne_kadar` | `derece` |
| `hilbert_aksiyomu` | `aksiyom` |
| `mill_usulu` | `illet_ara` |
| `tesir_kapali_mi` | `gecer_mi` |
| `kac_mertebeden` | `mertebe` |
| `kapi_kur` | `kapi` |
| `hazir_metrik` | `metrik` |

Her tashihte eski ad **bırakılmaz, taşınır**: `git grep` ile bütün
çağrı yerleri güncellenir ve kütükte eski→yeni cetveli durur.
İki isim yaşatmak ayrı gayrılığın ta kendisidir.

---

## 2. KÜME 8 -- üç öksüz klasörün cevher/toprak bilançosu

### `arama/` -- 910 satır. **Dağılmıyor: nazırlık oluyor.**

Bu, padişahın *"dağıtılamayacak kadar güzel ve kategori olarak farklı"*
dediği hâlin ta kendisidir. Grover, Dürr--Høyer, adiyabatik çöküş, WKB
tünelleme, GRAPE, holonomi -- hepsi **tek bir suâlin** parçalarıdır:
*asgarîyi nasıl ararız, ve kuyuya düşersek nasıl çıkarız?* Bunu üç
ayrı dosyaya serpmek cevheri öldürür.

| ALINACAK CEVHER | GİDECEĞİ YER |
|---|---|
| `grover_turu`, `difuzyon`, `faz_kehaneti`, `esik_kehaneti`, `en_iyi_tur`, `grover_basari_egrisi` (M18: fazla dönmek zarar) | **`nefs/ara.py`** -- ARAMAK nazırlığı |
| `durr_hoyer` (K bilinmeden asgarîyi bulur) | aynı yer -- nazırlığın ana kapısı |
| `adiyabatik_asgari`, `tayf_araligi_asgari` (M19: sonlu T'de başarı tam 1 değil) | aynı yer |
| `wkb_gamma`, `wkb_gecirgenlik`, `beklenen_deneme`, `tunel_maliyet_cetveli` (M20) | **`ogrenme/optimize.py`** -- `ayar.tunel_acik` kapısının **fiilî hesabı**; şu anda o kapı tünelin bedelini bilmiyor |
| `grape_gradyani`, `tam_gradyan`, `sadakat` (M22: sonlu fark hatası dt²) | **`nefs/melekeler.py`** -- kapı darbelerinin optimal kontrolü |
| `holonomi`, `cevrim_egriligi`, `duz_mu`, `aharonov_bohm` (M21: düz bağlantı, trivial olmayan holonomi) | **`nefs/zirh.py`** -- homotopi zırhının yanına; zırhın Wilson ilmeğinin **bağımsız şahidi** |
| ATILACAK TOPRAK | `_uexp`, `_genel_expm` (geometride `uslu_harita` var), `_ileri_geri` sarmalayıcısı |

### `yaklasim/` -- 1 713 satır. **Dağılıyor.**

| dosya | ALINACAK CEVHER | GİDECEĞİ YER |
|---|---|---|
| `akislar.py` | `langevin`, `gibbs_ile_kiyas`, `tuzaktan_kacis`, `serbest_enerji_azaliyor_mu`, `yerel_tuzak`, `cift_kuyu` | **`ogrenme/optimize.py`** -- **KUYUDAN ÇIKMAK terkibi** (aşağıda) |
| | `egri_kisaltma` | toprak: `geometri.mcf_kos` zaten var ve daha tam |
| `kara_kutu.py` | `nfl_tam_sayim`, `nfl_kacamagi`, `NesterovEnKotu`, `alt_sinir_ihlal_var_mi`, `sifir_zinciri_sinamasi` | **`ogrenme/optimize.py`** -- **`hoca`nın haddi**: hangi iyileştirme imkânsızdır, hangi kaçamak meşrudur |
| `tikizlik.py` | `ulasilmayan_infimum`, `sin_bir_bolu_x`, `yon_bagimli_limit`, `zorlayici_olmayan` | **`matematik/geometri.py`** -- asgarînin **var olmadığı** karşı örnekler; `zorlayici_mi`ın kırmızısı |
| | `zorlayici_mi`, `alt_seviye_sinirli_mi` | terkip: geometrideki hesapla **birleşir** (iki ayrı gövde, tek suâl) |
| | `kare`, `rosenbrock` | mihenk fonksiyonları -- geometriye, açıkça "mihenk" diye |
| `genisletme.py` | `rbf_gram`, `cekirdek_sirt`, `ezber_kiyasi`, `sobolev_kiyasi` | **`nefs/kulli_kayip.py`** -- **ezber ile genelleme farkı**; küllî kaybın bilmesi gereken şey budur |
| | `lan`, `ran`, `kan_ozellikleri` | toprak: 3 satırlık taslak; hakikîsi `geometri`de (42-44 satır) |
| `modern.py` | `KAN211.egit`, `FourierIslemci.egit`, `_afin_uyum`, `kan_sinamasi`, `fno_sinamasi` | **`matematik/geometri.py`** -- oradaki `KAN`/`FNO` **yapıyı** taşıyor, **tâlimi** taşımıyor; ikisi birleşir |
| | `DeepONet`, `deeponet_sinamasi` | aynı yer -- **yeni cevher**, karşılığı yok |
| | `poisson_ornekleri` | mihenk verisi |
| `nedensel.py` | `baglanim_mudahale_ayrimi` (ölçülen uçurum), `olculmemis_karistirici` (zaaf ölçümü), `catal_ve_carpisma` | **`matematik/fitrat.py`** -- `budayarak_mudahale`nin **kırmızısı**: müdahale ile bağlanımın ne kadar ayrıldığını ölçer |
| `simgesel.py` | `ara`, `bic`, `varsayilan_kutuphane`, `temiz_veride_bulunuyor_mu`, `ceza_fazla_terimi_eliyor_mu`, `kutuphane_disinda_ne_oluyor` | **`ogrenme/izgara.py`** -- orada yalnız `sembolik_kapanis` var; **asıl arama** burada |

### `olcek/` -- 686 satır. **Tek deftere giriyor.**

`nefs/hiz.py` padişahın 700 MB/sn hedefini iki muhasebeyle ölçüyor.
`olcek/` aynı meselenin **donanım tarafını** ölçüyor ve isimleri
tamamen ayrık -- yâni çakışma yok, **eksik** var.

| ALINACAK CEVHER | GİDECEĞİ YER |
|---|---|
| `flop_token`, `net_guc`, `throughput`, `l4_cetveli` | **`nefs/hiz.py`** |
| `aritmetik_yogunluk`, `cati_modeli`, `yigin_esigi` (M34: B=1'de bellek bağlı, büyük yığında FLOP bağlı) | aynı yer -- hız defterinin **çatı modeli** |
| `log_aritmetigi` (M31: log² 400 değil), `esdegers_hiz_boyut_denetimi` (M32, M33 tashihleri) | aynı yer -- bunlar **kırmızı yakabilen** ölçülerdir, kaybedilemez |
| `surekli_olc`, `isinma_bedeli`, `pencere_cetveli`, `gb_icin_sure`, `l4_ile_kiyas` | aynı yer -- **bu makinede gerçek ölçüm**; iddia ile ölçümü yan yana koyar |
| `sistem_yuku`, `yerel_olcum` | aynı yer |

`nefs/hiz.py` böylece **tek hız defteri** olur: iddia (cerideden),
model (çatı), ve fiilî ölçüm (bu makinede) üç sütun hâlinde.

---

## 3. KÜME 8'İN TERKİPLERİ -- uydurma değil, ölçülmüş kümeler

### 8.1 `ogrenme/optimize.py` → **`kuyudan_cik`**

Küme: `yaklasim.akislar` (Langevin ısıl kaçış) + `arama.bukum` (WKB
kuantum tünelleme) + `optimize`in mevcut `ayar.tunel_acik` kapısı.

**Özdeşlik:** üçü de tek suâlin cevabıdır -- *yerel asgarîde
sıkıştım, nasıl çıkarım?* Ve üç cevap **aynı eksende sıralanır**:

    belirlenimci akış   →  hiç çıkamaz            (yerel_tuzak)
    ısıl topluluk       →  e^{−ΔE/T} ile çıkar    (langevin)
    kuantum tünel       →  e^{−2γ} ile geçer      (wkb_gecirgenlik)

İkisi de üstel, üsler farklı: biri **bariyer yüksekliğine**, öteki
**bariyerin altındaki alana** bakar. Ayrı dosyalarda dururken bu
sıralama görünmüyordu; `optimize`in tünel kapısı da hangisini
kullandığını söylemiyordu.

    kuyudan_cik(f, x0, ne="ısıl"|"tünel"|"akış"|"bedel")

`bedel` kipi `tunel_maliyet_cetveli`dir: kaç deneme gerekir.

### 8.2 `ogrenme/optimize.py` → **`had`**

Küme: `nfl_tam_sayim` + `nfl_kacamagi` + `NesterovEnKotu` +
`alt_sinir_ihlal_var_mi` + `sifir_zinciri_sinamasi`.

**Özdeşlik:** beşi de *hoca ne kadar iyi olabilir* suâlidir. NFL
üstten sınırlar (hiçbir usul ortalamada üstün değildir), Nesterov
alttan (t adımda `k = 2t+1`den iyisi imkânsızdır), sıfır zinciri
ikincisinin sebebini gösterir (destek adım başına bir genişler).
`nfl_kacamagi` ise **kaidenin nerede düştüğünü** verir: hedef sınıfı
daralınca NFL bağlamaz -- bizim yaptığımız da budur.

    had(ne="nfl"|"kaçamak"|"alt_sınır"|"zincir")

Bu, `hoca`nın yanında durmalı: iddia ile haddi yan yana.

### 8.3 `matematik/geometri.py` → **`asgari_var_mi`**

Küme: `tikizlik.zorlayici_mi` + `geometri.zorlayici_mi` (iki ayrı
gövde!) + `alt_seviye_sinirli_mi` + `alt_seviye_tikiz_mi` +
`ulasilmayan_infimum` + `sin_bir_bolu_x` + `yon_bagimli_limit`.

**Özdeşlik:** Weierstrass'ın şartıdır -- *asgarî var mıdır?* Zorlayıcı
+ alt seviye tıkız ⇒ vardır. Karşı örnekler o şartın **her birinin
şart olduğunu** gösterir: `e^{−x}` zorlayıcı değil (inf'e ulaşılmaz),
`sin(1/x)` sürekli değil (limit yok), `(x²−y²)/(x²+y²)` yönden
bağımsız değil. Beş isim tek teoremin **hipotezleri ve nakızlarıydı**.

### 8.4 `nefs/kulli_kayip.py` → **`ezber_mi`**

Küme: `rbf_gram` + `cekirdek_sirt` + `ezber_kiyasi` + `sobolev_kiyasi`.

**Özdeşlik:** düzenlileme katsayısı `λ → 0` iken model **ezberler**
(eğitimde sıfır hata, sınamada patlar); `λ` büyüdükçe genelleştirir;
Sobolev cezası türevi de sınırladığı için aynı `λ`da daha iyi
genelleştirir. Küllî kaybın bilmesi gereken tam olarak budur ve şu
anda bilmiyor.

### 8.5 `nefs/hiz.py` → **`cati`**

Küme: `aritmetik_yogunluk` + `cati_modeli` + `yigin_esigi` +
`throughput` + `net_guc`.

**Özdeşlik:** roofline tek eğridir; dördü o eğrinin ayrı okunuşudur.
`yigin_esigi` eğrinin dirseğidir, `throughput` eğri üstündeki nokta,
`net_guc` tavanı, `aritmetik_yogunluk` apsis.

### 8.6 `nefs/zirh.py` → `iz` (mevcut `yolun_farki`) genişler

`holonomi` + `cevrim_egriligi` + `duz_mu` + `aharonov_bohm` zırhın
homotopi süzgecinin **bağımsız şahidi** olarak aynı kapıya girer:
`iz(..., ne="holonomi"|"eğrilik"|"düz_mü"|"ab")`. M21 mührü
(*düz bağlantı, trivial olmayan holonomi*) böylece zırhın kendi
kütüğüne geçer -- zırhın Wilson ilmeği tam bu sebeple vardır.

---

## 4. NAZIRLIK KATI -- main'e geçmeden evvelki ara kademe

### Niçin

Şu anda `main/egitim.py` doğrudan çipleri çağırıyor: `musahede_et`,
`qsicil`, `zirh_giydir`, `kulli_kayip`, `KulliOptimizer`... Yâni
main **alt kata bakarak** düşünüyor. Bu, padişahın dediği hatadır:
münasebet haritası kurulamaz, ve main kaybolursa yeniden yazılamaz.

Nazırlık katı **hiç yeni riyaziye getirmez**. Yalnız alt katı çağırır
ve ona bir **isim** verir. Sembolleşme budur.

### Altı nazırlık -- altı fiil

    nefs/gor.py     GÖRMEK      manzara = gor(gorev)
    nefs/dusun.py   DÜŞÜNMEK    hal     = dusun(manzara)
    nefs/ara.py     ARAMAK      aday    = ara(hal, olcut)
    nefs/tart.py    TARTMAK     mizan   = tart(hal, hedef)
    nefs/ogren.py   ÖĞRENMEK    hal     = ogren(mizan)
    nefs/soyle.py   SÖYLEMEK    cevap   = soyle(hal)      # yahut sükût

Ve tek hâl taşıyıcısı: **`Hal`** -- `nefs/zihin_durumu.py`ye konur
(orası zaten yazmacın hâlini tutuyor).

### Her nazırlık ne çağırır

| nazırlık | çağırdığı alt kat | verdiği söz |
|---|---|---|
| **`gor`** | `musahede.bak` (15 kanal), `kalip` (çıktı boyutu), `sahitler`, `kaide`, `gom` (QTT), `kopru` | *"Bu görevde ne var, çıktı hangi kalıba dökülecek, şahitler ne diyor."* Dış âlemden **tek nesne** döner. |
| **`dusun`** | `melekeler.QAKIS` (44 meleke), `zirh.zirhla`, `zirh.vicdan`, `zihin_durumu.QYazmac` | *"Manzarayı yazmaca al, melekeleri sırayla geçir, her adımda zırhı giydir."* |
| **`ara`** | `ara.durr_hoyer`, `ara.grover_turu`, `ara.adiyabatik_asgari`, `optimize.kuyudan_cik` | *"Adaylar arasından en iyisini bul; kuyuya düşersen çık."* `ogren`in âletidir. |
| **`tart`** | `kulli_kayip.zayif_halka`, `sozunde_mi`, `ezber_mi`, `mizan.hukum`, `fitrat.gecer_mi` | *"Bu hâl ne kadar doğru, hangi meleke sözünde durmadı, ezberliyor mu?"* |
| **`ogren`** | `optimize.hoca`, `optimize.had`, `optimize.yokus`, `ara` | *"Mîzâna göre düzelt -- ve haddini bil."* |
| **`soyle`** | `idrak.cozucu.gorev_coz`, `musahede.ortu` (tıkanıklık), H10 sükût kapısı | *"Ya ispat, ya sükût."* Uydurma cevap vermez. |

### Main o zaman ne olur

```python
for tur in range(ayar.tur):
    manzara = gor(gorev)
    hal     = dusun(manzara)
    mizan   = tart(hal, gorev.hedef)
    ogren(mizan)

cevap = soyle(dusun(gor(sinama)))
```

Altı satır. Alt kata bakılmıyor. Main kaybolsa bu altı satır
isimlerden yeniden yazılır -- padişahın istediği tam buydu.

---

## 5. HAREKÂT PLÂNI -- sıra

Usul aynıdır ve kat'îdir: **(a)** her dosya kendi içinde terkip,
**(b)** birleştirme, **(c)** birleşik gövdede bir daha terkip.
**Terkip bitmeden tek test koşmak yok.**

    ADIM 1  yedek/kume8_asillari/ altına üç klasörün aslı alınır.
            43 modülün raporu evvelden kaydedilir (kıyas şahidi).

    ADIM 2  Adım (a): üç klasörde dosya içi terkipler
            (kuyudan_cik, had, asgari_var_mi, ezber_mi, cati).

    ADIM 3  Adım (b): cevher hedef dosyalara nakledilir.
            arama/ → nefs/ara.py (nazırlık) + optimize + melekeler + zirh
            yaklasim/ → optimize, geometri, kulli_kayip, fitrat, izgara
            olcek/ → nefs/hiz.py

    ADIM 4  Adım (c): hedef dosyalarda birleşik terkip; çakışan
            isimler (Küme 7'de beş tane çıkmıştı) aranır ve ayrılır.

    ADIM 5  İSİM ISLAHATI: cetvel tatbik edilir, bütün çağrı yerleri
            `git grep` ile taşınır. Eski ad bırakılmaz.

    ADIM 6  NAZIRLIK KATI: altı fiil dosyası yazılır. Yeni riyaziye
            YOK -- yalnız çağrı ve isim.

    ADIM 7  main/egitim.py ve main/cikarim.py nazırlıklara çevrilir.

    ADIM 8  Üç klasör tasfiye edilir, sınamaları taşınır
            (Küme 7'de olduğu gibi: mühürler imha edilmez).

    ADIM 9  Bütün sınama takımı, en son ve toplu. Kütük H227.

---

## 6. YAPILMAYACAKLAR -- şimdiden söylüyorum

1. **`arama/` dağıtılmayacak.** Dağıtmak cevheri öldürür; nazırlık
   olarak yaşayacak. Padişahın *"ayrı dosya kurulabilir"* şartı tam
   bu hâl içindir.
2. **`matematik/`de dünya görüşü ismi kullanılmayacak.** Kütüphane
   herkesin malıdır; `christoffel`e `dimağın eğrisi` demek terkip
   değil zorlamadır.
3. **Nazırlıklara riyaziye konmayacak.** İçinde tek yeni formül olan
   nazırlık, nazırlık değil çiptir.
4. **Mükerrer görünüp mükerrer olmayan hiçbir şey atılmayacak.**
   `tikizlik.zorlayici_mi` ile `geometri.zorlayici_mi` **ayrı
   gövdelerdir**; biri silinmez, ikisi terkip edilir ve ikisinin
   aynı cevabı verdiği ölçülür.
