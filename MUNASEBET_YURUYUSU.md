# MÜNASEBET YÜRÜYÜŞÜ -- ÇALIŞMA DEFTERİ
(son hâli SERH.md'ye mühürlenecek)

## MAIN 1: main/egitim.py -- 820 satır, BAŞTAN SONA OKUNDU

### Tahtta kullanılmayan (ithal edilmiş, çağrılmamış)
- `main.cikarim.hazineden_yukle`   ithal 24, gövdede YOK
- `main.cikarim.hafizayi_yukle`    ithal 24, gövdede YOK
- `nefs.mihenk.MIHENK`             ithal 31, gövdede YOK
- `nefs.olcek.olcek_beyani`        ithal 44, gövdede YOK
- `nefs.keyfiyet.keyfiyet`         ithal 47, gövdede YOK (KeyfiyetAyari+beyani var)
- `main.kulliyat.kulliyat_beyani`  ithal 52, gövdede YOK
- GARABET: satır 468 `List[...]` kullanılıyor fakat `List` ithal edilmemiş
  (typing: Dict, Optional, Sequence, Tuple). `from __future__ import
  annotations` mahallî değişken annotasyonunu hiç değerlendirmediği için
  koşuda patlamıyor.

### Tahtın ÇAĞIRDIĞI fonksiyonların bulunduğu dosyalar (seviye 1)
 1. nefs/musahede.py        gorevleri_getir
 2. ogrenme/mecz.py         MeczAyari, mecz_egit, mecz_beyani
 3. main/hazine.py          koy, UZANTI, ust_coz, beyan
 4. nefs/kulli_mizan.py     MizanAyari, kulli_mizan, mizan_cetveli, rapor
 5. nefs/hafiza.py          Hafiza(.hazineye .beyan)
 6. main/cikarim.py         padisah, hazineden_devam, devam_agirligi  [MAIN 2]
 7. nefs/galois.py          GaloisAyari, tableau_kur, sbox_bukme, sbox_olcu, palmer_olcu
 8. nefs/tdd.py             TddAyari, kanonik_adres
 9. nefs/matchgate.py       MatchgateAyari, flo_evrimi
10. nefs/ayna.py            AynaAyari
11. nefs/mihenk.py          nobet_kur(.yokla .beyan)
12. nefs/faz_polinomu.py    FazAyari, faz_oturt
13. nefs/siklotomik.py      SiklotomikAyari, koset_indirge, iz_esitligi
14. nefs/qcekirdek.py       cekirdek_beyani
15. tanilama/hizolcer.py    Hizolcer(.saat), hizolcer_bagla, hizolcer_beyani
16. nefs/gpu_akis.py        GpuAyari, gpu_akisi
17. nefs/kararname.py       kararname
18. nefs/golge.py           GolgeAyari, golge_al, kestir
19. nefs/sadakat.py         SadakatAyari, sadakat_uygula, sadakat_beyani
20. nefs/olcek.py           Kok, olcek, denge
21. nefs/belirtec.py        belirtec_kapisi, belirtec_sozlugu, belirtec_beyani
22. nefs/keyfiyet.py        KeyfiyetAyari, keyfiyet_beyani
23. nefs/munasebet.py       MunasebetAyari, munasebet_kos, munasebet_beyani
24. main/kulliyat.py        kulliyat_verisi, kulliyat_dokumu
25. nefs/mukayese.py        hata_payi, kiplik, mukayese_beyani, vecih_kur
26. nefs/hendese.py         HendeseAyari, hendese_teshisi, hendese_beyani
27. nefs/casimir.py         CasimirAyari, blok_kosegen_artigi, casimir_beyani,
                            dhr_ayrismasi, gelfand_tsetlin_araya_girme, kartan_fazi
28. nefs/usul.py            usul_beyani
29. nefs/suphe.py           suphe_beyani
30. tanilama/beyan.py       talim_beyani, kaggle_beyani, sifir_beyani
31. nefs/illet.py           alan_cizgesi, cevrimler, kelam_ayrismasi, zaman_cizgesi
32. tanilama/hiz_teftisi.py BUTCE_SANIYESI, HAD, olc
33. ogrenme/izgara.py       bagintili_olcut, duzenli_uydur
34. nefs/kulli_kayip.py     kademe_parametreleri_ac
35. nefs/melekeler.py       QNefs(.idrak_et .p .yukle .__len__)
36. nefs/qegitim.py         degerlendir, ornekler, ornek_bol
37. nefs/zihin_durumu.py    QAyar(.kulli_alanlar)
38. main/kaggle_egitim.py   kaggle_talimini_baslat
39. main/kaggle_cikarim.py  kaggle_teslimat_dosyasi_uret
40. ogrenme/kaggle_donanim.py  ayar_sec
41. tanilama/sabit_teftisi.py  rapor
42. main/veri.py            rapor                                    [MAIN?]
43. nefs/qyazmac.py         QuditYazmac.sektor/.faz_birikimi/.faz_borcu/.psi/.ayar

## OKUMA SIRASI VE NETİCE
(her dosya okundukça buraya yazılır)

### [1] nefs/musahede.py -- 2403 satır OKUNDU
Dışarıdan ithal edilen (CANLI): gorevleri_getir, gorev_dizisi, gorev_boyu,
  sigan_nispet, ortu, iki_olcegin_acisi, bilesen_kutulari, devinim_olc, bak,
  kaide, artiklar, delil_dizileri, soyutlama_oku, Gorev(*), ayir(*),
  genlige_gom(*)   -- (*) yalnız nefs/gor.py'den, o da ölü
KULLANILMAYAN (sınıf/fonksiyon):
  rapor  (1903-2340, 437 satır) + `if __name__ == "__main__"` (2343) -- F.1-L
  _rapor_* iç yardımcıları (rapor içinde, 8 tane)
  izgara_belirtecle · belirtec_izgara · metin_izgara   (yalnız rapor)
  toplu_uret · istatistik
  Kodlayici · kodlayici · _yerel_tablo · OZEL_BELIRTECLER · TABLO_ADLARI
    · _O200K_DESEN · otele · IzafiMevki · YON_ADLARI
    -- İKİNCİ BELİRTEÇLEYİCİ. F.1-N ihlâli: `taban_sozluk=256` bayt yedeği
       ve 19 elle yazılmış özel belirteç. tek belirteçleyici tiktokendir.
  IzafiMevki2D · _komsuluk · tiktoken_2d_kodla · tiktoken_2d_coz
  qtt_parametre_sayisi · qtt_gomme · qtt_sadakat_cetveli
  genlige_gom · YazmacOlcusu · veri_yazmaci · bellek_cetveli
    -- F.7 ihlâli: genlige_gom "mps" kolu np.linalg.svd + bond truncation
  kopru
  Sahit · Bolutleme · ayir · nakz_bul · _akis_kur · _bir_deneme
  iki_sahit_ayri_mi · terkip_saglam_mi
  QTT_TABAN · QTT_KADEME · QTT_BAG · Boyut · KAIDE_ADLARI(kalip içinde kullanılıyor: CANLI)
GARABET: satır 359-362 `otele(ne="yön")` `ad` değişkenini kullanıyor fakat
  imzada `ad` YOK -- çağrılsa NameError. (Hiç çağrılmıyor.)
GARABET: satır 1042 `kalip` ve 1534 `kaide` gibi fonksiyonlar `ne=` ile
  8-10 ayrı işi tek gövdede taşıyor (F.2-C'nin "dallı budak" istediği
  yerde tek düz gövde).

### [2] ogrenme/mecz.py -- 407 satır OKUNDU
Dışarıdan: MeczAyari, mecz_egit, mecz_beyani (main/egitim.py),
  mecz_metni (tanilama/beyan.py:95) -- hepsi CANLI
KULLANILMAYAN:
  egim()            129-145  -- divan artık senet_egimi.egim_ek_durum/uretec
                                 kullanıyor; bu eski üreteç kolu yetim kaldı
  nakil()           184-198  -- yerine nakil_senetli koşuyor
  _uretec_vur()      81-102  -- yalnız egim/nakil çağırıyor, ikisi de ölü
  Memuriyet._harman_yeri  212-234  -- hiç çağrılmıyor
  Memuriyet._durum        236-243  -- hiç çağrılmıyor
  Memuriyet.kademeye_yay  302-309  -- hiç çağrılmıyor (yön artık tam boyda)
  `__all__`da ilan edilip ölü: uretecler(CANLI: _harman_yeri ölü ama
     egim/nakil ölü; fiilen yalnız ölü çağrı) -> ÖLÜ
GARABET: `__all__` 11 ad ilan ediyor, 5'i ölü.
GARABET (F.1-E yarım iş): ferman 2-P'nin beş memuriyeti iki kere yazılmış --
  bir kere üreteç ekseninde (egim/nakil/_uretec_vur), bir kere senet
  ekseninde (senet_egimi.*). İkincisi koşuyor, birincisi duruyor.

### [3] main/hazine.py -- 243 satır OKUNDU
CANLI: koy, al, ust_coz, beyan, UZANTI  (+ iç: _ayir _birlestir _yol, BICIM)
KULLANILMAYAN:
  rapor()   208-239  + `if __name__ == "__main__"` (242)  -- F.1-L
  listele() 192-205  -- yalnız rapor çağırıyor
  `__all__`da ilan edilip ölü: listele, rapor

### [4] nefs/kulli_mizan.py -- 938 satır OKUNDU
CANLI hepsi: MizanAyari, kulli_mizan, mizan_cetveli (taht), rapor (taht
  `mizan` kipi), givens (usul.py + tabakali_mizan.py), uhlmann/holonomi/
  holonomi_yigin/engellenme/_cevrimleri_tara/_monogami/_laplasyen/_ileri (iç)
KULLANILMAYAN: yok (fonksiyon/sınıf bazında)
GARABET: `if __name__ == "__main__"` (935-937) -- modülün kendi giriş
  noktası. `rapor` tahttan da çağrılıyor, o hâlde bu blok fazladır (F.1-L).
GARABET (ÇİFT BAŞLILIK): `holonomi` iki yerde tanımlı --
  nefs/kulli_mizan.py:110 (hâl dizisinden Givens çarpımı) ve
  nefs/zirh.py:693 (kenar fazlarından skaler). Aynı ad, ayrı mana.

### [5] nefs/hafiza.py -- 259 satır OKUNDU
CANLI: TASDIK/TEVAKKUF/CERH, Kayit, Hafiza(.yaz .zeno .taban_degistir
  .beyan .hazineye .hazineden ._tasfiye)
KULLANILMAYAN:
  Hafiza.oku()  91-104  -- iki çağrı yeri var, İKİSİ DE ÖLÜ KOD:
      nefs/kulli_kayip.py:580 `def _kullanilmayan(): d = None; if d is
        None: return []`   (adı bile "kullanılmayan")
      main/kaggle_cikarim.py:54 `d = None; if d is None: return ...`
  rapor() 203-255 + `if __name__ == "__main__"` (258)  -- F.1-L
  `mu_asgari` ayarı yalnız zeno'da; `_SONUM_PAYI` CANLI
GARABET (F.5 SESSİZ İKAME -- AĞIR): `main/kaggle_cikarim.py:gorev_cevabi_uret`
  daima `d = None` kurup "dalga_yok" ile GİRDİ IZGARASINI cevap olarak
  döndürüyor. Bu fonksiyon tahtın `kaggle` kipinden çağrılıyor
  (main/egitim.py:794). Yâni kaggle teslimatı fiilen kopya üretiyor ve
  bunu hiçbir ölçü kırmızı yakmıyor.

### [6] main/cikarim.py -- 177 satır OKUNDU  [MAIN 2 -- kendi turu da bu]
CANLI hepsi: hazineden_devam, devam_agirligi, hafizayi_yukle,
  hazineden_yukle, _motor, padisah, degerlendirme_kosusu, kos
KULLANILMAYAN: yok
MAIN 2'nin çağırdığı YENİ dosya (MAIN 1'de olmayan):
  44. nefs/soyle.py     soyle
  (belirtec.py, melekeler.py, kulli_kayip.py, beyan.py, sadakat.py,
   suphe.py, hazine.py, musahede.py, hafiza.py zaten listede)

### [7] nefs/galois.py -- 385 satır OKUNDU
CANLI: GaloisAyari, tableau_kur, sbox_bukme, sbox_olcu, palmer_olcu (taht),
  palmer_indir (faz_polinomu, qyazmac), gf_carp+gf_tablo (siklotomik,
  gpu_akis), sbox (qyazmac, gpu_akis), sbox_tablo (gfni), faz_borcu_metni
  (beyan), Tableau, palmer_i, _ham_carp, _uretec, _POLI, _SBOX, _GF
KULLANILMAYAN:
  olc()          306-322  -- yalnız rapor
  rapor()        325-381  + `__main__` (384) -- F.1-L; içinde 2000 ve
                              20000 turluk perf_counter döngüleri
  Tableau.xor_isle      255-260  -- yalnız rapor
  Tableau.faz_isle      262-266  -- yalnız rapor
  Tableau.galois_isle   272-277  -- hiçbir yerde
  Tableau.parite_alarmi 268-270  -- hiçbir yerde
GARABET (ÇİFT BAŞLILIK): ferman 1-I'nin birinci huddudu "parite alarmı
  sönük" der. O alarm FİİLEN nefs/sadakat.py'nin parite_dizini/
  sadakat_uygula'sı ve nefs/keyfiyet.py'nin "parite_taşması"yla ölçülüyor.
  `Tableau.parite_alarmi` ikinci ve ölü bir baştır.
GARABET: `Tableau` kurulup (tableau_kur) yalnız `beyan()`i okunuyor ve
  `sbox_bukme` ile genliği büküyor; X/Z/faz tablosuna ana akışta hiçbir
  kapı vurulmuyor (xor_isle/faz_isle/galois_isle ölü). Yâni stabilizer
  tableau kuruluyor fakat İŞLETİLMİYOR.

### [8] nefs/tdd.py -- 82 satır OKUNDU
CANLI: TddAyari, kanonik_adres (taht + kulli_mizan), esit_mi (kulli_mizan)
KULLANILMAYAN: rapor() 43-78 + `__main__` (81) -- F.1-L, 2×1000 turluk
  perf_counter döngüsü

### [9] nefs/matchgate.py -- 227 satır OKUNDU
CANLI: MatchgateAyari, flo_evrimi (taht), matchgate_mi (qyazmac:466,
  qcekirdek:414), Ortam(.dondur .antisimetri_hatasi .gaussluk_hatasi
  .parite .stabilizer_rank), pfaffyen, BRAVYI_GOSSET_ALFA
KULLANILMAYAN:
  matchgate_kur() 46-56  -- yalnız rapor
  rapor()        185-223 + `__main__` (226) -- F.1-L
GARABET: `Ortam.donme_deti` alanı kuruluyor, `dondur`da `*= 1.0` ile
  çarpılıyor (ölü satır 108), hiçbir yerde okunmuyor.
GARABET (ÜÇ BAŞLILIK): `Ortam` adı üç ayrı sınıf --
  nefs/matchgate.py:82 (Majorana kovaryansı), matematik/mizan.py:1768,
  matematik/tip_teorisi.py:853 (tip bağlamı). Üçü alâkasız.

### [10] nefs/ayna.py -- 461 satır OKUNDU
CANLI: AynaAyari (taht, soyle, kulli_mizan), kivilcim (soyle:46),
  halka + _halka_netice (kulli_mizan:313), bolucu (kivilcim/halka içinden)
KULLANILMAYAN:
  Isik (49-72, .kip .foton_sayisi) · vakum · sikistir · bogoliubov
  · _omega · _bs_simplektik · aynadan_gecir · faz_kaydir
  -- BÜTÜN CV (sürekli değişken) KANADI ÖLÜ
  olc()   350-411   -- yalnız rapor
  rapor() 414-457 + `__main__` (460) -- F.1-L
GARABET (ÇİFT BAŞLILIK): `vakum` ve `sikistirma` bir daha
  kuantum/surekli.py:70,100'de tanımlı. CV kanadı iki yerde, ikisi de ölü
  (surekli.py'yi ayrıca okuyacağım).
GARABET: `AynaAyari` 18 alan taşıyor; ölü CV kanadına ait olanlar
  (sikma_fazi, korunakli, kip, sahit_n) canlı yolda hiç okunmuyor --
  `sikma_fazi` kivilcim'de okunuyor (CANLI), `kip`/`sahit_n`/`korunakli`
  ölü.

### [11] nefs/mihenk.py -- 263 satır OKUNDU
CANLI hepsi: nobet_kur, Nobet(._sor .yokla .beyan), mihenk_sor, cevap_haddi,
  mihenk_metni, _basamaklar, _metne, _sozluk, MIHENK, MIHENK_CEVABI,
  CEVAP_PAYI
KULLANILMAYAN: yok. (Tahtın ithal ettiği `MIHENK` adı tahtta okunmuyor --
  [MAIN 1] listesinde yazıldı; fakat ad modül içinde CANLI.)
GARABET: `mihenk_sor`un `sozluk` argümanı alınıyor fakat gövdede hiç
  kullanılmıyor (sözlük `_sozluk(kodlama)`dan geliyor). Aynı şey
  `Nobet.sozluk` için de geçerli -- F.1-M: iki kaynak, biri ölü.

### [12] nefs/faz_polinomu.py -- 149 satır OKUNDU
CANLI: FazAyari, faz_oturt (taht:617), mobius+zeta (faz_oturt içinden)
KULLANILMAYAN:
  faz_uygula()  86-90  -- hiçbir yerde. (Faz genliğe qyazmac.py:373'te
     doğrudan `palmer_indir` ile iniyor; bu sarmalayıcı yetim kaldı --
     F.1-M çift kaynak.)
  rapor()       93-145 + `__main__` (148) -- F.1-L
  BRAVYI_GOSSET_ALFA -- burada bir daha tanımlı (nefs/matchgate.py:13'te
     de var). ÇİFT BAŞLILIK; faz_oturt içinde okunuyor, o hâlde canlı
     fakat iki kaynak.

### [13] nefs/siklotomik.py -- 176 satır OKUNDU
CANLI: SiklotomikAyari, koset_indirge (taht:620), iz_esitligi (taht:623),
  koset, frobenius, us_al, iz (iz_esitligi içinden)
KULLANILMAYAN:
  iz_uydur()  119-136  -- hiçbir yerde
  rapor()     139-172 + `__main__` (175) -- F.1-L
GARABET: `__all__` `us_al`ı ilan etmiyor fakat iz_esitligi/iz_uydur onu
  kullanıyor; `iz_uydur`u ilan ediyor fakat o ölü.

### [14] nefs/qcekirdek.py -- 597 satır OKUNDU
CANLI: HAT_TIPI (olcek.py), Bant (qyazmac.py:132; .karo .cift .dolu
  .bos_mu .bosalt ._karo_blas ._numpy_bosalt ._bolum), cekirdek_beyani
  (taht:727), derle, yoklama, kutuphane, CEKIRDEK_C, KARO/CIFT/MATCHGATE
KULLANILMAYAN:
  CekirdekAyari  291-297  -- hiçbir yerde kurulmuyor (Bant kendi `hat`/
     `bant` argümanını alıyor) -- F.1-M iki ayar kaynağı, biri ölü
  _ozet()        300-302  -- hiçbir yerde
  rapor()        531-593 + `__main__` (596) -- F.1-L; iki hattı A/B
     kıyaslıyor, bu tam ferman 1-L'nin yasakladığı "ikinci hat"
C TARAFINDA ÖLÜ KOD:
  `mucit_bant` (229-244) ve onun çağırdığı `karo_vur`(41) ve
     `cift_vur`(191) -- Python tarafı artık YALNIZ `mucit_cift_bant`
     çağırıyor; karo yolu `_karo_blas` ile BLAS'a gidiyor.
     C yorumu 190. satırda bunu kendi de söylüyor: "kıyas için duruyor".
  `mucit_ayristir` / `mucit_birlestir` (247, 263) -- AVX-512 ayrıştırma
     çekirdekleri; `kutuphane()` imzalarını bağlıyor fakat hiç
     çağrılmıyor (F.1-F: en derin kod koşturulmuyor).
GARABET: `Bant.__slots__` `_tampon` tutuyor, `__init__`te None ediliyor,
  hiç kullanılmıyor. `_tre`/`_tim` geçici tamponları yalnız ölü
  `mucit_bant` yolu için ayrılıyor.

### [15] tanilama/hizolcer.py -- 157 satır OKUNDU
CANLI: Hizolcer(.saat ._canli .beyan), hizolcer_bagla, hizolcer_beyani
  (taht:36,465,684,726)
KULLANILMAYAN:
  hizolcer_al()   117-118  -- hiçbir yerde
  hizolcer_coz()  112-114  -- hiçbir yerde (bağlanan ölçer hiç çözülmüyor)
  Hizolcer.ekle() 69-70    -- yalnız rapor
  rapor()        130-153 + `__main__` (156) -- F.1-L
GARABET: `sert` alanı ve `saat`in içindeki had assert'i hiç açılmıyor
  (taht `Hizolcer(...)`u `sert` vermeden kuruyor, öntanımlı False).
  Yâni hız haddi ölçülüyor fakat KIRMIZI YANAMIYOR (F.5): had yalnız
  `beyan()`da metin olarak "TUTMUYOR" yazıyor, akışı durdurmuyor.
  (Tahtın `gecit`indeki hız geçidi ayrı bir yerdir ve o sert.)

### [16] nefs/gpu_akis.py -- 279 satır OKUNDU
CANLI: GpuAyari, gpu_akisi (taht:626), symplectic_motoru, kaynasik_motoru,
  genlesme_motoru, dilim_motoru, ZABIT_IDDIASI (hepsi gpu_akisi içinden)
KULLANILMAYAN: rapor() 212-275 + `__main__` (278) -- F.1-L
GARABET (F.1-L ihlâli CANLI YOLDA): `kaynasik_motoru` ve `genlesme_motoru`
  her tâlim koşusunda `ayar.tekrar=10` turluk `perf_counter` zamanlama
  döngüleri koşturuyor ve 4 MiB'lık (`olcu_bayti = 1<<22`) diziler
  ayırıyor. Yâni tahtın içinde bir ÖLÇÜM BETİĞİ koşuyor: tâlimin kendi
  işi değil, hız kıyası. F.1-L "tahtın basmadığı sayı sayı değildir"
  der, fakat bu sayı da tâlimin işi değil.
GARABET: `GpuAyari.olcu_bayti` ve `tekrar` alanları yalnız bu kıyas için.

### [17] nefs/kararname.py -- 89 satır OKUNDU
CANLI: kararname (taht:589)
KULLANILMAYAN: rapor() 59-85 + `__main__` (88) -- F.1-L
GARABET (F.2-J): `kararname` canlı yolda `np.fft.fft` (31) ve
  `np.exp(2j·π·...)` (43) kullanıyor. CLAUDE.md 2-J'nin "gövdede hâlâ
  aşkın koşan" listesinde BU YOK. Liste eksik yazılmış; ferman 2-J
  "yeni bir aşkın çağrı görülünce derhal buraya eklenir" diyor.
  → CLAUDE.md 2-J listesine eklenecek.

### [18] nefs/golge.py -- 117 satır OKUNDU
CANLI: GolgeAyari, golge_al, kestir (taht:594,596)
KULLANILMAYAN: rapor() 77-113 + `__main__` (116) -- F.1-L
GARABET: `golge_al`ın ilk kolu (24-41) `hasattr(psi,"havuz")` ile bir
  "graf/havuz" temsilini yokluyor. Öyle bir nesne kodda YOK (havuz/kok/
  dugum/ic alanları olan sınıf kalmadı) -- ölü dal.
GARABET (ÇİFT BAŞLILIK): `kestir` adı bir daha
  nefs/musahede.py:1008'de `SekilKaidesi.kestir` olarak var (metot).

### [19] nefs/sadakat.py -- 190 satır OKUNDU
CANLI hepsi: SadakatAyari, parite_maskesi, parite_dizini, tenakuz_alarmi,
  sadakat_uygula (taht + melekeler:1231 + kulli_mizan raporu),
  mantiki_degil (suphe.py:74), sadakat_beyani, _bit
KULLANILMAYAN:
  sadakat_sifirla()  188-190  -- hiçbir yerde. Sayaç oturum boyu birikiyor,
     hiç sıfırlanmıyor; `alarm_nispeti` bütün koşunun ortalaması.
  `__all__`da ilan edilip ölü: sadakat_sifirla
GARABET (F.2-J): satır 98 `np.exp(2j·π·faz/16)` -- canlı yol mu? Bu kol
  ancak hedef `.genlik`+`.faz` alanlı bir nesne olduğunda koşar; taht
  ndarray, melekeler yazmaç veriyor. O hâlde bu dal ÖLÜ (Tableau'ya
  sadakat vurulmuyor). `m = 16.0` de elle yazılmış sabit (F.1-J).

### [20] nefs/olcek.py -- 363 satır OKUNDU
CANLI: Kok, olcek (taht:212), denge (taht:438), olcek_beyani
  (tanilama/beyan.py:60), hiz_yoklamasi, taban_sec, _ikinin_kuvveti,
  PENCERE_HADDI, PAYLAR
KULLANILMAYAN:
  _yukari_kuvvet()  35-37  -- hiçbir yerde
  satır 107 `from .belirtec import basamak_sayisi as _bs` -- ÖLÜ İTHAL,
     `_bs` gövdede hiç kullanılmıyor (taban_sec kendi ithalini yapıyor)
GARABET (F.1-J): `kapi_yogunlugu = 0.404` (74) elle yazılmış sabit ve
  ölçülen hızı doğrudan bölüyor. `doluluk = 0.25 + 0.65·c`, `yon = 8 +
  56·c`, `keyf = 2 + 10·c` … bunların hepsi cömertliğin AFİN
  fonksiyonu; keyfiyetin nispeti değil (F.1-J'nin istediği bu değil).
GARABET (F.5 sessiz ikame): 88-89 `except OSError: pass` -- hız önbelleği
  yazılamazsa sessizce geçiliyor.
GARABET (F.1-L): `hiz_yoklamasi` canlı yolda 3+24 turluk perf_counter
  zamanlama döngüsü koşturuyor ve neticeyi `depo/olcek_hiz.json`a
  yazıyor. Bu bir mikro mihenktir ve tahtın işi değildir; fakat
  `olcek`in bütün Formül 2'si buna dayanıyor.

### [21] nefs/belirtec.py -- 213 satır OKUNDU
CANLI hepsi: Kodlama, KODLAMALAR, onbellek_dizini, _kodlama, bpe_yerlestir,
  belirtec_kapisi, belirtec_sozlugu, basamak_sayisi, tip_vektoru, tipten,
  belirtecle, coz, belirtec_metni (beyan:98), belirtec_beyani, BPE_DEPOSU
KULLANILMAYAN: yok
GARABET: `KODLAMALAR` iki kodlama tanımlıyor fakat yalnız `o200k_base`
  kullanılıyor; `cl100k_base` satırı ölü veri (ölü kod değil).
GARABET: `belirtec_beyani` sözlüğü `_KAPI`den okuyor; kapı hiç
  açılmamışsa `"sözlük": 0` dönüyor -- F.5'in "sessizce sıfır dönmesin"
  hükmüne aykırı (fakat `belirtec_metni` bunu "ölçü kırmızı" diye
  yazıyor, o hâlde kırmızı YANIYOR: kabul).

### [22] nefs/keyfiyet.py -- 119 satır OKUNDU
CANLI: KeyfiyetAyari, keyfiyet (munasebet:117), esik (munasebet:120),
  keyfiyet_beyani (mecz:312, hizolcer:59, taht:719), keyfiyet_metni
  (beyan:100)
KULLANILMAYAN:
  keyfiyet_sifirla()  96-99  -- hiçbir yerde
GARABET (F.1-J'ye UYGUN, kayda geçiyorum): `esik` fonksiyonu sabit
  değil, `_HAL["en_iyi"]`e bağlı -- ferman 1-J'nin istediği budur.
  Fakat `KeyfiyetAyari.taban = 0.25` elle yazılmış bir sabittir ve
  eşiği doğrudan çarpıyor.

### [23] nefs/munasebet.py -- 187 satır OKUNDU
CANLI: MunasebetAyari, munasebet_kos (taht:523), munasebet_beyani
  (hizolcer:58, taht:718), munasebet_metni (beyan:99),
  Harita(.isle .zayiflik .doyma)
KULLANILMAYAN:
  munasebet_sifirla()  164-166  -- hiçbir yerde
  Harita.hazineye()     56-57   -- hiçbir yerde
GARABET (AĞIR -- F.1-I + F.1-Y): Ferman 1-I *"bir süre sonra tüm veriler
  için MÜŞTEREK BİR MÜNASEBET HARİTASI oluşacak"* diyor. Harita
  (`Harita.M`) her koşuda SIFIRDAN kuruluyor ve koşu bitince ÖLÜYOR:
  `hazineye()` yazılmış fakat `main/egitim.py`nin `hazine.koy` çağrısı
  yalnız `{"p": ...}` ve `hafiza.hazineye()`yi veriyor. Yâni müşterek
  harita hiç birikmiyor -- fermanın asıl hükmü icra edilmiyor.

### [24] nefs/mukayese.py -- 391 satır OKUNDU
CANLI: Vecih, VECIHLER, vecih_kur (taht:664, kulli_mizan:567),
  uyanik_vecihler, bargmann (usul:164, paylar_olc), hipotez_halkasi
  (kulli_mizan:574), swap_testi (hafiza:117, usul:181,201, hata_payi),
  spektrum (kulli_mizan:572), hata_payi (taht:668), kiplik (taht:672),
  paylar_olc (olcek:258), nesnelestir (usul:165,177), mukayese_beyani,
  mukayese_metni (beyan:93), sayac, _dilim/_genlik/_faz/_fark/_normalize
KULLANILMAYAN:
  simplisiyal()   174-192  -- yalnız istisna_yeri
  istisna_yeri()  195-207  -- hiçbir yerde
  choi()          210-220  -- hiçbir yerde
  zorunlu()       298-300  -- hiçbir yerde
  mumkun()        303-305  -- hiçbir yerde (nefs/suphe.py'deki `mumkun`
     ayrı bir mahallî değişken, bu değil)
GARABET (F.2-J): `nesnelestir` canlı yolda `np.exp(1j·fi·...)` (231)
  kullanıyor -- ferman 2-J'nin aşkın listesinde YOK. Eklenecek.
  Aynı şekilde `bargmann`/`simplisiyal`da `np.angle`, `hata_payi`de
  `math.acos`, `holonomi`de `math.acos` -- bunlar da aşkın.

### [25] nefs/usul.py -- 299 satır OKUNDU
CANLI: UsulAyari, usul_kos (kulli_mizan:620), usul_beyani (taht:630),
  gedik_bul, sefer, usul_sec, usul_imzasi, DEVRELER + on devre gövdesi,
  _bir, _householder, _dikleştir, _gaye
KULLANILMAYAN:
  usul_sifirla()  296-299  -- yalnız kulli_mizan.py:833'te İTHAL EDİLİYOR
     fakat o satırdan sonra rapor gövdesinde ÇAĞRILMIYOR (ölü ithal).
  USULLER (13-24) -- on usul adının tuple'ı; `DEVRELER` sözlüğü aynı
     adları taşıyor ve fiilen o kullanılıyor. ÇİFT BAŞLILIK: aynı
     liste iki yerde (F.1-M). `USULLER` hiç okunmuyor.
  UsulAyari.lan_esigi CANLI (sefer:240)
GARABET (ÇİFT BAŞLILIK): `USULLER` adı bir daha nefs/zirh.py:466'da
  BAŞKA bir şey olarak tanımlı (`Tuple[Usul, ...]`). İki ayrı mana,
  aynı ad.
GARABET (F.2-J): `gedik_bul` canlı yolda `np.arccos` (56) kullanıyor --
  ferman 2-J listesinde YOK. Eklenecek.

### [26] nefs/suphe.py -- 128 satır OKUNDU
CANLI: SupheAyari, modal_kip, suphe_manifoldu (kulli_mizan:613),
  suphe_beyani (taht:631, cikarim:158)
KULLANILMAYAN:
  tearuz()        31-36    -- hiçbir yerde. (Teâruz fiilen `suphe_manifoldu`
     içinde `np.einsum` ile hesaplanıyor; bu fonksiyon aynı işin ikinci
     kaynağı -- F.1-M.)
  suphe_sifirla() 126-128  -- hiçbir yerde
GARABET (F.1-J): `kip_kenari=0.25`, `tevakkuf_esigi=0.35`,
  `merak_esigi=0.5`, `sonum=0.05` -- dördü de elle yazılmış sabit eşik.
  (`kip_kenari` tahttan `a.kenar*5.0` ile geliyor, `kenar` de 0.0
  öntanımlı -- yâni fiilen 0.0 koşuyor ve `modal_kip` HİÇ "zorunlu"
  yahut "muhâl" dönemiyor: ω > 1.0 şartı sağlanamaz. Ölçü kırmızı
  yanamıyor.)

### [27] tanilama/beyan.py -- 531 satır OKUNDU
CANLI: talim_beyani (taht:781), cikarim_beyani (cikarim:172),
  kaggle_beyani (taht:799), sifir_beyani (taht:791), devam_metni
  (talim_beyani içinden), _bayt
KULLANILMAYAN: yok
!!! BULUNAN KIRIK (BU TURDA DÜZELTİLDİ): satır 96-97 `hendese_metni` ve
  `casimir_metni`yi ithal ediyordu; o iki fonksiyon geçen turda ferman
  1-G gereği imha edilmişti. O hâlde `talim_beyani` ImportError veriyor
  ve `python -m main.egitim tâlim` HİÇ KOŞAMIYORDU. İthal ve çağrılar
  kesildi, itildi.
GARABET: 531 satırın ~440'ı tek bir `talim_beyani` gövdesi; ferman 1-G
  raporu tahttan çıkarmayı emretti ve rapor buraya toplandı, fakat
  burada da tek düz gövdede duruyor (F.2-C'nin "dallı budak" hükmü).
GARABET: `talim_beyani` `kulli`nin 60'tan fazla anahtarına KÖR
  indisleme (`kulli["mizan"]`, `m["zırh_sheaf"]` …) yapıyor; bir uzuv
  anahtarını değiştirse KeyError. Yukarıdaki kırığın kardeşi.

### [28] nefs/illet.py -- 182 satır OKUNDU
CANLI: alan_cizgesi, zaman_cizgesi, cevrimler, kelam_ayrismasi (taht:271
  `gecit`), _melekelerin_bolgeleri, HUKUM_ALANLARI
KULLANILMAYAN: rapor() 115-178 + `__main__` (181) -- F.1-L
YENİ DOSYA (seviye 2): matematik/fitrat.py (Cizge, gecer_mi)
GARABET (ÇİFT BAŞLILIK): `HUKUM_ALANLARI` iki yerde ve FARKLI içerikle --
  nefs/illet.py:10 (9 alan: yerel makam mizan tenakuz tasdik sukut nakz
  gaye tertip) ve nefs/zirh.py:449 (mizan tasdik sukut nakz ...).
  Aynı ad, iki ayrı hüküm kümesi. F.1-M: tek kaynak olmalı.

### [29] tanilama/hiz_teftisi.py -- 153 satır OKUNDU
CANLI: HAD (taht:461 + gecit:290), BUTCE_SANIYESI (olcek:138, gecit:290),
  olc (gecit:291), Kalem, _saat
KULLANILMAYAN:
  teftis()  116-127  -- hiçbir yerde. Sert had assert'i BURADA duruyor
     fakat çağrılmıyor; tahtın `gecit`i kendi assert'ini yazıyor
     (main/egitim.py:313). F.1-M: aynı hüküm iki yerde, biri ölü.
  rapor()   130-149 + `__main__` (152) -- F.1-L
GARABET (AĞIR -- F.1-L, CANLI YOLDA): `olc` her tâlim koşusunun
  BAŞINDA (gecit → olc) koşuyor ve içinde: bütün örnekleri belirteçliyor,
  `tekrar` kere ileri geçiş, 41 melekeyi TEK TEK saatliyor, harman/
  olcumler/entropi/beyan saatliyor ve TAM bir `kulli_mizan` çağrısı
  yapıyor. Yâni tâlim başlamadan evvel BİR TAM KAYIP ÇAĞRISI + 41
  meleke koşusu zamanlama için harcanıyor. Bu bir ölçüm betiğidir ve
  tahtın kendi işi değildir (F.1-L), fakat tahttan çağrıldığı için
  "yan koşu" da değil -- tahtın içine girmiş bir mihenktir.
GARABET (F.1-J): `HAD = 1_000_000.0` ve `BUTCE_SANIYESI = 86_400.0`
  elle yazılmış iki sabit; ikisi de bütün ölçek formülünü tayin ediyor.
GARABET: satır 64 `veri[0][0]` -- `ornek_bol` kullanılmadan ham demete
  indisleme; 59-73 arası aynı veriyi ÜÇ ayrı yolla açıyor.

### [30] ogrenme/izgara.py -- 447 satır OKUNDU
CANLI: duzenli_uydur (taht:335), bagintili_olcut (taht:339),
  bukulme_dizeyi + _ikinci_turev_temeli + bukulme_enerjisi (duzenli_uydur
  içinden)
KULLANILMAYAN:
  artislardan_dugum   22-28   -- yalnız _gosterim
  dugum_gecerli_mi    31-33   -- yalnız _gosterim
  artis_gradyani      36-43   -- yalnız _gosterim
  SEMBOL_KUTUPHANESI 116-130  -- yalnız sembolik_kapanis
  sembolik_kapanis   143-174  -- hiçbir yerde
  _gosterim          177-300  (124 satır) -- F.1-L; içinde sayısal türev
     kıyası ve λ tablosu
  Terim · varsayilan_kutuphane · _uydur · bic · ara ·
    temiz_veride_bulunuyor_mu · ceza_fazla_terimi_eliyor_mu ·
    kutuphane_disinda_ne_oluyor · _rapor_simgesel  (303-440, 138 satır)
    -- İKİNCİ, TAMAMEN AYRI bir simgesel regresyon motoru; hiçbiri
       çağrılmıyor. `_rapor_simgesel` bile `rapor`dan çağrılmıyor.
  rapor() 442-443 + `__main__` (446) -- F.1-L
GARABET (ÇİFT BAŞLILIK -- ÜÇ KERE): sembol kütüphanesi iki ayrı yerde
  (`SEMBOL_KUTUPHANESI` 12 terim, `varsayilan_kutuphane` 8 terim);
  `ara` adı ayrıca nefs/ara.py:12'de BAŞKA bir fonksiyon.
GARABET (F.6 ihlâli adayı): `sembolik_kapanis` ve `ara` elle yazılmış
  bir sembol kütüphanesinden formül seçiyor -- ferman 6'nın yasakladığı
  "öznitelik mühendisliği/elle kâide" cinsinden. İkisi de ölü olduğu
  için şu an ihlâl KOŞMUYOR.
GARABET (F.2-J): `np.sin/np.cos/np.exp/np.tanh/np.log1p` her iki
  kütüphanede -- ikisi de ölü.
DOSYANIN 447 SATIRININ 262'Sİ (%59) ÖLÜ.

### [31] nefs/kulli_kayip.py -- 1394 satır OKUNDU
CANLI: OlcuUzayi, UZAYLAR (kulli_mizan:424,529), mertebe (Olcum.mertebe),
  Olcum (kulli_mizan:535), zayif_halka (kulli_mizan:428, bolge_degeri),
  SOZLESME (illet:18, melekeler:1191), kademe_parametreleri_ac (taht:379,
  cikarim:102), KADEME_VARSAYILAN, K_UZAY, MERTEBE_NOTU, Idrak/Hal/
  Namzet/Ispat/Yakin, Kademeler (bütün kademeleri + capraz_not),
  kademeleri_kos (kulli_mizan:544), meleke_olcumleri (kulli_mizan:536),
  bolge_degeri (melekeler:1218), _TAKSIMAT_ARTIGI (melekeler:1191),
  suz (qegitim:215), BOLGELER, ESIK, VERI_ORNEK, BETA, _mertebeler
KULLANILMAYAN:
  MERTEBE_UZAYI      29     -- hiçbir yerde
  sozunde_mi()      302-372 -- yalnız rapor
  _IZLENEN         1005-1011 -- hiçbir yerde (34 adlık liste)
  lan() / ran()    1054-1059 -- yalnız kan_ozellikleri/ezber_mi
  kan_ozellikleri  1062-1088 -- yalnız _rapor_ezber
  ezber_mi         1091-1185 -- yalnız _rapor_ezber (94 satır, 4 kip)
  _rapor_ezber     1188-1209 -- HİÇ ÇAĞRILMIYOR (rapor onu da çağırmıyor)
  rapor()          1211-1386 + `__main__` (1389) -- F.1-L
  MIZAN_AGIRLIK    1393     -- hiçbir yerde (dosyanın SON satırı)
  VAZIFE_NEVILERI   753     -- hiçbir yerde
  YAKIN_ESIGI       756     -- suz'un öntanımlısı (CANLI)
  DINAMIK_BETA      152     -- False; zayif_halka "beta" kolunu ölü kılıyor
  HEDEF_USSU        155     -- yalnız ölü "beta" kolunda
  Kademeler.muhakeme içindeki `_kullanilmayan()` 581-595 -- adı bile öyle
!!! KIRIK (F.5 SESSİZ İKAME): satır 533 `gorev_ozellikleri(_G())` --
  bu ad depoda HİÇBİR YERDE TANIMLI DEĞİL ve ithal de edilmiyor. O hâlde
  `_iki_olcek` her çağrıda NameError atıyor, `_dene` onu yutuyor ve
  `oz = None` oluyor. `Hal.ozellik` fiilen daima yalnız `tayf`tan geliyor.
  Ölçü kırmızı yanmıyor; günlüğe "özellik N boyut" diye yazıyor.
!!! KIRIK: `zayif_halka(ne="beta")` gövdesi (192, 195) tanımsız `alt` ve
  `ust` adlarını kullanıyor → çağrılsa NameError. `DINAMIK_BETA=False`
  olduğu için çağrılmıyor.
GARABET (F.1-U MECLİS): satır 953 `from .meclis import meclis` -- `suz`
  fiilen bir MECLİS topluyor ("Meclisi topluyorum: %d uzuv (rey %.3f),
  %d hakem"). Ferman 1-U meclisi yasaklıyor. `suz` qegitim:215'ten
  çağrılıyor → CANLI YOLDA MECLİS VAR.
  YENİ DOSYA: nefs/meclis.py
GARABET (F.6): `suz`un bütün gövdesi "kaide arama / şablon tutturma"
  usulüdür ve `K[0].ad`, `k(g)` diye çağrılan kaide nesneleri
  bekliyor; fakat `_ara()` daima `[]` döndüğü için `N.kaideler` daima
  BOŞ. Yâni müdrike zinciri kurulu fakat her zaman "kaide bulunamadı"
  ile susuyor.

### [32] nefs/melekeler.py -- 1421 satır OKUNDU
CANLI: QNefs (taht:419, cikarim:98, qegitim:12, hiz_teftisi:38),
  QParametre (kulli_kayip:13, mecz:213, optimize:1433), qsicil
  (kulli_mizan:555, illet:103, zirh:604, kulli_kayip:13), qmelekeler
  (kulli_kayip:307), QAKIS (illet:17, musahede:1805), harman_uretecleri
  + harman_anahtari (mecz:77,213), QMeleke + 44 meleke sınıfı, qkaydet,
  bec_faz_kilidi (idrak_et:1239), _kinetik, talim_kademesi (QTalim),
  lifleri_kur + Lif + _tam_kur + _temsilci_kur + SABIT + DINAMIK +
  AZAMI_TAM_MERTEBE (QTefekkur:737), ALTIN (QSanat), dikkat?,
  ehlilestir (dikkat içinden), devirler (zirh:201),
  grape_gradyani/tam_gradyan/sonlu_fark_gradyani/grape_kos/sadakat/
  _uexp/_genel_expm/_ileri_geri (yalnız zirh.py'nin RAPORUNDAN --
  aşağıya bak)
KULLANILMAYAN:
  MELEKE_SAYISI 157 · MERTEBE_SAYISI 158 · KANONIK_CETVEL 160-181
    · EKSIK_MELEKELER 183 · UMUM/TALIM/TAHSIL 186-188
    · MERTEBE_SIRA 287 · KULLI_SIRA 292-298 · AKIS 300-308
    · KAN_TEMELI 282 · ALTIN_ORAN 285 (ALTIN 311 ile ÇİFT BAŞLI!)
    · NIZAM_ACIK 313 + nizami_ac 316-320 (hiç çağrılmıyor)
    · KANONIK_ACIK 323 + kanoniklestir 326-330 (hiç çağrılmıyor;
        KANONIK_ACIK daima False → QMeleke.kosu'daki `q.y.kanonikle()`
        HİÇ KOŞMUYOR)
    · nizam_cetveli 351-352
    · QMeleke.satir_donmesi CANLI · QMeleke.birikim CANLI
    · rapor_qakis 1256-1292 -- F.1-L
    · tevafuk() 69-105 (4 tarz) -- hiçbir yerde
    · devirler() zirh:201'den ÇAĞRILIYOR → CANLI
    · dikkat() 152-154 -- hiçbir yerde
    · grape_gradyani · tam_gradyan · sonlu_fark_gradyani · grape_kos
      · sadakat · _uexp · _genel_expm · _ileri_geri (1295-1421, 127
      satır) -- YALNIZ nefs/zirh.py:761-780'den, o da zirh'in RAPOR
      gövdesi. Yâni GRAPE gradyan motoru ana akışta koşmuyor.
      AYRICA: ferman 2-P türevi senet_egimi'ne taşıdı; bu ikinci
      (Hamiltonyen-kontrol) gradyan motoru F.1-M çift başlılıktır.
    · YOGUSAN 1114 -- bec_faz_kilidi içinde CANLI
GARABET (ÇİFT BAŞLILIK): `ALTIN_ORAN`(285) ve `ALTIN`(311) aynı sayı,
  iki ad; `AKIS`(300) ve `QAKIS`(1102) neredeyse aynı sıra, ikincisi
  42/43/44'ü de içeriyor -- birincisi ölü.
GARABET (ÇİFT BAŞLILIK): `AZAMI_TAM_MERTEBE` + `SABIT` + `_temsilci_kur`
  mantığı idrak/kategori.py:23-86'da BİR DAHA var.
GARABET (F.2-J): `ehlilestir` np.exp (sigmoid/gelu/softmax),
  `tevafuk` np.exp (çekirdek), `_uexp` np.exp, `devirler` matris üsteli,
  `talim_kademesi` np.exp -- `dikkat`/`ehlilestir("softmax")`
  `QMeleke`lerde koşmuyor fakat `talim_kademesi` QTalim(43) içinden
  CANLI YOLDA np.exp koşuyor. F.2-J listesinde YOK. Eklenecek.
GARABET: `talim_kademesi` 195. satır `if ... is False and len(t) > 1:
  pass` -- hiçbir iş yapmayan ölü şart.
YENİ DOSYA (seviye 2): nefs/kule.py, nefs/zirh.py, ogrenme/optimize.py,
  kuantum/kapilar.py, matematik/mizan.py, matematik/tip_teorisi.py,
  matematik/fitrat.py, nefs/mantik.py

### [33] nefs/qegitim.py -- 305 satır OKUNDU
CANLI: ornek_bol (taht:410, mecz, kulli_mizan, munasebet, hiz_teftisi,
  zirh), belirtecleri_kodla (aynı yerler + musahede:1385, soyle:154),
  ornekler (taht:394, kulli_mizan:782, zirh:615, hiz_teftisi:45),
  adayin_tuttugu (soyle:54, degerlendir içinden),
  degerlendir (taht:555)
KULLANILMAYAN:
  egit()  142-210  -- hiçbir yerde. 69 satırlık İKİNCİ bir eniyileme
     döngüsü: `as_gek_adimi` + `ayrik_mertebede_sicra` + tünelleme +
     `mertebe.DINAMIK`ı GLOBAL olarak değiştirme. Ferman 2-P mecz'i
     tek motor yaptı; bu üçüncü eniyileyicidir (F.1-M, F.1-E).
  _degerlendir_mudrike() 213-254 -- yalnız `degerlendir(mudrike_ile=True)`
     ile, o bayrak hiçbir çağrıda verilmiyor → ÖLÜ. (`suz`u buradan
     çağırıyordu; o hâlde `suz` de fiilen ölü -- [31]'deki "CANLI"
     kaydımı DÜZELTİYORUM: `nefs/kulli_kayip.py:suz` yalnız bu ölü
     yoldan çağrılıyor, o hâlde ÖLÜ. Meclis de o yüzden koşmuyor.)
  belirtecleri_kodla'nın "sürekli"/"lie" kolu (31-38) -- `usul`
     hiçbir çağrıda verilmiyor, daima "kategorik". `nefs/lif.py`
     ithali ölü dalda.
  `from . import melekeler as mertebe` (11) -- yalnız ölü `egit`te
GARABET: `ornekler` ARC'ın hem ızgarasını hem sözlü çözümünü üretiyor
  (ferman 1-R'ye uygun) fakat ferman 1-R'nin ÜÇÜNCÜ kanadı (sözlü cins,
  "sen olsan ne söylerdin") BURADA YOK; külliyat verisi
  main/kulliyat.py'den ayrı geliyor.
YENİ DOSYA (seviye 2): nefs/lif.py (ölü dalda), nefs/soyle.py

### [34] nefs/zihin_durumu.py -- 364 satır OKUNDU
CANLI: QAyar (taht:233, olcek:96, musahede, kulli_kayip, qegitim),
  QYazmac (melekeler:26, zirh:15, optimize:16, kulli_kayip:14),
  MAKAM_ADLARI, donme, faz_z (melekeler:606), degil_x (melekeler:972,
  zirh:551), kontrollu_donme (melekeler'de 15 yerde), kodla, harman,
  cift_yigin, tek/tek_yigin/cift/uzak_cift/mpo_topla/mpo_dagit/
  veri_izgara/yereller/kulli/veri/yerel/olcumler/povm/beyan/
  alan_degeri/makam_dagilimi/bolge_var, superpozisyon (kulli_kayip:330,
  zirh:1053), blok_dagilimi (zirh:675), olcumler_yigin?
  makam_merdiveni/makam_derecesi/makam_mertebeleri/makam_kubit_manasi
  (nefs/mantik.py:45-55) -- mantik.py'nin canlı olup olmadığına bağlı
KULLANILMAYAN:
  QIz (51-59)      -- `self.iz = self.y.iz` QuditYazmac'ın izini alıyor;
     bu sınıf hiç kurulmuyor. `__all__`da ilan edilmiş ölü sınıf.
  QYazmac.kubit_sayisi 138-140 · meleke_kubiti 162-164 · ancilla 166-168
     · mpo_esigi 170-171 · bolge_olculeri 173-174 · kulli_bas 148-149
     · makam_mertebe_dagilimi 301-306 · makam_derece_vektoru 298-299
     · olcumler_yigin 292-293 · not_dus 131-132 -- hiçbirine atıf yok
  QYazmac.taksimat() 142-146 -- AŞAĞIDAKİ KIRIĞA BAK
!!! KIRIK: satır 336 `MAKAM_ESIKLERI` -- bu ad depoda HİÇBİR YERDE
  TANIMLI DEĞİL. `makam_mertebeleri` çağrılırsa NameError. O fonksiyon
  nefs/mantik.py:53,95'ten çağrılıyor.
!!! KIRIK (F.5): `taksimat` bir METOT ve sözlük döndürüyor; fakat
  melekeler.py:1091 `q.taksimat.bolge["parametre"][1]` diye ATTRIBUTE
  olarak okuyor → AttributeError. Kurtaran şey: 1089'daki
  `if not q.bolge_var("parametre"): return`. `bolge_var` "parametre"ye
  False döner (sadece _alan + meleke/veri/yerel). O hâlde:
  **𝒪44 QTahsil HİÇBİR ZAMAN HİÇBİR İŞ YAPMIYOR** -- 44 melekenin biri
  sessizce ölü. Aynı şey kulli_kayip.py:320'de de var (guard aynı).
GARABET: `superpozisyon(yalniz_veri=False)` argümanı hiç kullanılmıyor.
GARABET (F.2-J): `harman` (275) `np.cos/np.sin`, `donme` (351)
  `math.cos/sin`, `kodla` (238) `math.pi` -- `donme` BÜTÜN melekelerin
  taşıyıcısı, yâni en sıcak aşkın çağrı. F.2-J listesinde
  `zihin_durumu.py:harman` var fakat `donme` YOK. Eklenecek.

### [35] nefs/qyazmac.py -- 904 satır OKUNDU
CANLI: QuditAyar, QuditYazmac (zihin_durumu:9, zirh:13), Iz (+senedi_ac/
  senedi_kapat/kapi_yaz/bag_yaz/not_dus), SENET_ACIK (mecz:250),
  psi get/set, normalize, norm, norm_hatasi, faz, faz_birikimi,
  faz_borcu, _faz_indir, _bosalt, _karolari_banda, _karo_vur,
  _bit_kapisi_lifli, _cift_kapisi_lifli, bit_kapisi, tek, tek_yigin,
  cift, uzak_cift, cift_bit_kapisi, mpo_uygula, mpo_topla, mpo_dagit,
  sektor, sektor_agirligi, alan_degeri, olcumler, dolasiklik_entropisi,
  beyan, tekil_yogunluklar, blok_dagilimi, makam_dagilimi,
  makam_derece_vektoru (mantik:116), superpozisyon, veri/yerel/kulli/
  yereller/veri_izgara/gecerli/gecerli_toplu/lif_no_toplu/_lif_no/
  _bolum/_eksen/_bit/_gomulu/lifli/bolge_var/not_dus/sadakat/
  sadakat_log/sadakat_kapi_basina/kanonikle(ölü çağrıdan)/bayt(rapor)/
  genlik (zirh:657, stabilizer:147)
KULLANILMAYAN:
  yuva_yogunluklari   194-197 -- hiçbir yerde
  olcumler_yigin      210-213 -- hiçbir yerde
  ic_carpim           246-248 -- yalnız ogrenme/optimize.py:787 (o da
     ölü mü diye optimize.py okunduğunda karara bağlanacak)
  supurme / takas     250-254 -- yalnız melekeler.rapor_qakis (ölü)
  deger               259-260 -- hiçbir yerde (qyazmac'ın kendi `deger`i)
  parametre()         262-263 -- hiçbir yerde
  superpozisyona_sok  268-269 -- hiçbir yerde
  harman_kur          271-272 -- hiçbir yerde
  tek_kapi            274-276 -- yalnız zirh:222,226
  tek_kapi_yuva       278-279 -- hiçbir yerde
  cift_kapi           281-282 -- hiçbir yerde
  cift_kapi_yuva      284-285 -- hiçbir yerde
  tek_kapi_yigin      287-288 -- hiçbir yerde
  cift_kapi_yigin     290-296 -- hiçbir yerde
  lif_kapisi          301-305 -- NotImplementedError fırlatıyor; yalnız
     `uzak_cift`in `_ikinin_kuvveti` FALSE kolundan çağrılabilir.
     Lifler (16,16,16) daima ikinin kuvveti → o kol ÖLÜ.
  _duzlem             325-326 -- hiçbir yerde
  _bit_gorunumu       328-332 -- hiçbir yerde
  sektor_kapisi       504-512 -- hiçbir yerde (senet "sektör" kaydını
     yazan tek yer; o hâlde senedi_uygula'nın "sektör" dalı da ölü)
  povm(ad)            561-569 -- hiçbir yerde (zihin_durumu'nun
     `povm(yuvalar)`u AYRI bir fonksiyon -- ÇİFT BAŞLILIK, aynı ad
     iki ayrı imza)
  kodla(belirtecler)  571-586 -- hiçbir yerde. zihin_durumu.QYazmac'ın
     `kodla(E)`sı kullanılıyor. ÇİFT BAŞLILIK: aynı ad, iki ayrı
     kodlama usulü (biri Cauchy zarfı + sbox çeyreği, öteki tek-sıcak
     + basamak fazı). F.1-M.
  mpo_uygula_hizli    863-864 -- hiçbir yerde
  rapor()             888-904 -- hiçbir yerde
  property A          161-163 -- hiçbir yerde
  `uzak_cift`in 783-822 arası (ki==kj ve genel lif kolu) -- ÖLÜ
     (`_ikinin_kuvveti` daima True). 40 satır.
  `QuditYazmac.__init__`in `n is not None` kolu (97-102) -- hiçbir
     çağrı `n=` vermiyor
GARABET: `sadakat()` daima 1.0, `sadakat_kapi_basina()` daima 1.0 --
  kulli_mizan:432 `kesme_kesri`ni bundan okuyor, o hâlde "kesme
  yapısal" ölçüsü SABİT 1.0. Ölçü kırmızı yanamıyor (F.5).
GARABET: `mpo_topla`/`mpo_dagit` `duraklar` ve `j` argümanlarını alıp
  HİÇ KULLANMIYOR; melekeler onları veriyor (QFesahat j=0..kk,
  QTefekkur duraklar=dur). Yâni 𝒪7/𝒪21/𝒪30/𝒪34/𝒪37'nin durak ve
  kanal ayrımı sessizce DÜŞÜYOR: hepsi sektörün ortalama fazını
  vuruyor. F.5 sessiz ikame.
GARABET: `mpo_topla`/`mpo_dagit` `-> None` diye ilan edilmiş fakat
  `return 0.0` yapıyor; melekeler.py:1058 `q.iz.kesme += q.mpo_topla(...)`
  ile 0.0 topluyor.

### [36] nefs/soyle.py -- 186 satır OKUNDU
CANLI: soyle (cikarim:112), Cevap, _uret (mihenk:70), _sec (qegitim:289),
  _buda
KULLANILMAYAN:
  `usul="ara"` kolu (126-146) -- hiçbir çağrı `usul=` vermiyor;
     `nefs/ara.py` ve `AynaAyari` ithalleri o ölü dalda. 21 satır.
  `manzara` argümanı -- yalnız assert ile reddedilmek için var
  `tikaniklik_bak` -- hiçbir çağrı True vermiyor → `ortu(ne="tıkanıklık")`
     bu yoldan koşmuyor
  `ne="sukut_mu"` kipi -- hiçbir çağrıda
  `teta` argümanı -- gövdede HİÇ kullanılmıyor (ölü imza)
  `Cevap.aday_sayisi` daima 0, `Cevap.izgara` yalnız kurulup okunmuyor
     (cikarim/padisah `belirtec`i okuyor)
GARABET (F.1-J): `sukut_esigi=0.8` elle yazılmış sabit ve cevabın
  susup susmayacağını doğrudan tayin ediyor.
GARABET (F.2-J): satır 150 `np.exp(-bedel/...)` -- güven aşkın
  fonksiyondan. F.2-J listesinde YOK.
GARABET: `guvenler` daima TEK elemanlı liste; `np.mean` üstünde
  gereksiz.
YENİ DOSYA (seviye 2, ölü dalda): nefs/ara.py

### [37] main/kulliyat.py -- 660 satır OKUNDU
CANLI: Kaynak, KAYNAKLAR (44 kaynak), kulliyat_verisi (taht:400),
  kulliyat_dokumu (taht:721), kulliyat_beyani (beyan:101),
  kulliyat_cek (kulliyat_verisi:556), mucit_cevir, mucit_ac,
  _metin_akit, _parquet_akit, _belirtecle, _boy, _dizin, envanter
  (kulliyat_cek:518), yer_ac + bos_alan (kulliyat_verisi:564),
  MUCIT_DAMGA, MUCIT_UZANTI, KULLIYAT_DIZINI, BELIRTEC_PENCERESI
KULLANILMAYAN:
  hf_boru()  362-411  -- HİÇBİR YERDE. `huggingface_hub` ithal ediyor.
     Ferman 1-K: "HF vekilde siyaseten kapalı; şart açılırsa cetvele
     DERHAL girer". Boru hattı yazılmış fakat hiçbir çağrı yok ve
     cetvelde de HF kaynağı yok -- yâni kod "şart açılırsa" diye
     bekliyor. F.5'in "yapılmayan yapıldı diye yazılmaz"ına aykırı
     değil (iddia edilmiyor) fakat ÖLÜ.
  `Kaynak.surum`/`varlik` CANLI (Enigmata/SynLogic/ZebraLogic)
GARABET (F.5 SESSİZ İKAME -- ÜÇ YERDE): `_boy` (218), `yer_ac`
  (195,204), `hf_boru._akis` (395,402) `except OSError: pass` ile
  sessizce geçiyor. Dosya boyu okunamazsa veri sessizce düşüyor.
GARABET: `kulliyat_verisi` 566-568 `mucit_ac(...) is None` ise dosyayı
  SİLİYOR ve yeniden çeviriyor; `mucit_ac` damga/başlık bozuksa None
  döner. Bozuk bir dosya sessizce imha edilip yeniden indiriliyor --
  sebep raporlanmıyor.
GARABET (F.1-J): `BELIRTEC_PENCERESI = 1<<16`, `obek_bayt = 8<<20`,
  `int(ham*1.5) + (1<<30)`, `batch_size=4096` -- elle yazılmış dört
  sabit.
GARABET: `KAYNAKLAR` cetvelinde `pay` alanı elle yazılmış (0.5–3.0);
  ferman 1-J'ye göre keyfiyetten ölçülmeli, kemiyetten değil.

### [38] main/veri.py -- 239 satır OKUNDU  [tahtın `veri` kipi]
CANLI: rapor (taht:807) → kok, belirtecle, yaz, _bin_yaz, oku, PARCA_HADDI,
  HIZA, TIP_KUCUK, TIP_BUYUK
KULLANILMAYAN:
  _safetensors_yaz 101-114 · _zarr_yaz 117-129 -- `yaz(ne=...)` hiç
     "safetensors"/"zarr" ile çağrılmıyor
  yetki()  147-172  -- yalnız gonder
  gonder() 175-196  -- hiçbir yerde (Kaggle veri kümesi yükleyici)
  `__main__` (238) -- `veri` kipi tahtta var, o hâlde bu blok fazla
GARABET (F.5): `belirtecle` 45-48 `except Exception: continue` --
  ayrıştırılamayan görev SESSİZCE düşüyor.
GARABET (F.5): `yetki` 160,162 iki çıplak `except Exception` → sessiz
GARABET (F.1-N): `belirtecle` 49-50 `int(x) % int(sozluk)` -- belirteç
  kimliğini sözlük mertebesine göre KATLIYOR. Ferman 2-L bunu açıkça
  yasakladı ("coz() taşan kimliği katlayarak susturuyordu; bu sessiz
  ikamedir"). Aynı katlama `nefs/soyle.py:112,118`de de var.

### [39] main/kaggle_egitim.py -- 147 satır OKUNDU
!!! KIRIK -- TAHTIN `kaggle` KİPİ HİÇ KOŞAMAZ:
  satır 12 `from main.egitim import (..., KulliDalgaTalimMotoru, ...)`
  -- `KulliDalgaTalimMotoru` main/egitim.py'de YOK (depoda hiçbir yerde
  tanımlı değil). O hâlde `import main.kaggle_egitim` ImportError
  veriyor ve `main/egitim.py:793`teki `kaggle` kipi ÇÖKÜYOR.
  Ayrıca 78, 92, 93, 115, 117 satırları o motorun `veri_durumu_hazirla`,
  `talim_adimi_icra_et`, `kaydet`, `seyir` uzuvlarını çağırıyor;
  hiçbiri yok. `ayar.bag` (100) da EgitimAyari'de yok.
KULLANILMAYAN (kırık olduğu için tamamı): torch_var_mi, sarjorleri_bul,
  sarjor_oku, kaggle_sarjor_egitici_surec, kaggle_talimini_baslat,
  `__main__`
GARABET (F.5): `sarjor_oku` 50-53 `except Exception:` ile parquet
  okunamazsa SENTETİK rastgele ızgara üretiyor -- veri yerine gürültü
  koyup "[SENTETİK]" diye damgalıyor. Damga var fakat bu bir ikamedir.

### [40] main/kaggle_cikarim.py -- 127 satır OKUNDU
CANLI: kaggle_teslimat_dosyasi_uret (taht:794 -- fakat kaggle kipi
  zaten [39] yüzünden çöküyor), test_gorevlerini_oku, _cift_cikar,
  gorev_cevabi_uret
KULLANILMAYAN: `from main.cikarim import padisah` (11) -- `padisah`
  gövdede HİÇ kullanılmıyor. ÖLÜ İTHAL. Yâni teslimat motoru
  MODELİ HİÇ ÇAĞIRMIYOR.
!!! F.5 SESSİZ İKAME (en ağırı): `gorev_cevabi_uret` 54-56
  `d = None; if d is None: return [girdi], "dalga_yok"` -- teslimat
  daima GİRDİ IZGARASINI cevap olarak veriyor. Rapor bunu
  "dalga kurulamayan %d (girdi aynen teslim edildi)" diye yazıyor,
  o hâlde gizlenmiyor; fakat motor hiç çağrılmadığı için ARC
  teslimatı %0'dır ve `padisah` elin altında dururken kullanılmıyor.

### [41] ogrenme/kaggle_donanim.py -- 132 satır OKUNDU
CANLI: ayar_sec (taht:795)
KULLANILMAYAN:
  kos()  34-79  -- hiçbir yerde. AYRICA KIRIK: `donanim_raporu(dh)`
     çağrılıyor fakat `matematik/geometri.py:4840 rapor()` ARGÜMAN
     ALMIYOR → TypeError; `ayar.bag`, `ayar.cevrim`, `ayar.ornek`
     EgitimAyari'de YOK → AttributeError.
  BASLANGIC_HUCRESI 82-118 -- metin sabiti, yalnız `_ana`dan basılıyor
  _ana() 121-132 + `__main__` -- F.1-L (argparse'lı ikinci giriş noktası)
  `BASLANGIC_HUCRESI` içindeki hücre de `kos`u çağırıyor → kırık.
GARABET: modül seviyesinde `_TEK_IPLIK = tek_iplik_zorla()` (9) --
  ithal edilir edilmez yan tesir. `matematik/geometri.py`den geliyor,
  `main/egitim.py`nin kendi `tek_iplik_zorla`sıyla ÇİFT BAŞLI.

### [42] tanilama/sabit_teftisi.py -- 205 satır OKUNDU  [tahtın `sabit` kipi]
CANLI: rapor (taht:801), ozet, tara, _dosyalar, _deger, _sayi_mi, Sabit,
  KOK, ATLANAN
KULLANILMAYAN: `__main__` (203) -- `sabit` kipi tahtta var, blok fazla
GARABET: `_HARIC` (14) `"yedek"` dizinini eliyor; ferman 2 `yedek/`
  dizininin OLMADIĞINI ve açılmayacağını söylüyor. Ölü filtre.
GARABET: `tara` 82-86 `serhli()` fonksiyonu `while` içinde şartsız
  `return True` yapıyor → döngü hiç dönmüyor, fiilen
  `if satirlar[no-2].strip().startswith("#")` demek. Ferman 1-W
  yorumları imha ettiği için bu ölçü artık DAİMA False verir.
GARABET (F.1-J'nin ta kendisi): bu dosya "elle tayin edilmiş her sayıyı"
  sayan bir teftiştir ve tahttan koşuyor -- fakat NETİCESİ hiçbir
  hükme bağlı değil: sayı ne çıkarsa çıksın tâlim koşuyor. Ölçü
  kırmızı yanamıyor (F.5).

## !!! DÖRDÜNCÜ KIRIK: nefs/meclis.py DİYE BİR DOSYA YOK
`nefs/kulli_kayip.py:953` `from .meclis import meclis` -- dosya depoda
YOK. `suz`un o satırına ulaşılırsa ModuleNotFoundError. `suz` yalnız
`qegitim._degerlendir_mudrike`den çağrılıyor, o da `degerlendir(
mudrike_ile=True)`den, o da hiç verilmiyor → şu an patlamıyor.
Aynı şekilde `_dene("ispat.uzanma")`, `_dene("mizan.cikarim")`,
`_dene("token_uzaylari.fno")`, `_dene("main.main")` etiketleri
OLMAYAN dizinlere işaret ediyor (`ispat/`, `mizan/`, `token_uzaylari/`
yok; gerçek ithaller `matematik.mizan` ve `matematik.geometri`).
Etiketler yalan söylüyor: `self.eksik` sözlüğüne düşen ad okuyucuyu
var olmayan bir dosyaya yönlendirir.

## SEVİYE 2 DOSYA LİSTESİ (seviye 1'in çağırdıkları, 20 582 satır)
nefs/kule.py(85) zirh.py(1066) rust.py(143) qudit.py(408) tenakuz.py(88)
tabakali_mizan.py(111) derleyici.py(72) donanim.py(343) onbellek.py(88)
hizli.py(278) gfni.py(689) mantik.py(190) lif.py(240·ölü dal)
ara.py(21·ölü dal) gor.py(63·ölü)
ogrenme/optimize.py(2091) senet_egimi.py(264·okundu) grassmann.py(237)
rkhs.py(290) morse.py(124) operator.py(157·okundu)
kuantum/devre.py(36) eniyileme.py(284) topolojik.py(319) kapilar.py(371)
matematik/fitrat.py(1623) geometri.py(4852) mizan.py(2304)
tip_teorisi.py(3995)
idrak/kategori.py(171)

### [43] nefs/kule.py -- 85 satır OKUNDU
CANLI: kule_kur + kaba (kulli_kayip:538-540, `_kule`), ince (kaba
  içinden), kaba_kademe, TAVAN
KULLANILMAYAN: rapor() 50-81 + `__main__` (84) -- F.1-L
GARABET: melekeler.py:24 `from .kule import ince, kaba` -- ikisi de
  melekeler gövdesinde HİÇ kullanılmıyor. ÖLÜ İTHAL.

### [44] nefs/tenakuz.py -- 88 satır OKUNDU
CANLI hepsi: TenakuzAyari, birlikte_gorulme, dislama_dizeyi, log_bariyer,
  tenakuz_tavani (kulli_mizan:233-247)
KULLANILMAYAN: yok. `__main__` yok. (Bu dosya tertemiz.)
GARABET (F.2-J): `dislama_dizeyi` canlı yolda `np.exp` (46). F.2-J
  listesinde YOK. Eklenecek.

### [45] nefs/tabakali_mizan.py -- 111 satır OKUNDU
CANLI hepsi: kategori_kaybi, tasma_kaybi, nokta_kaybi (kulli_mizan:519-523)
KULLANILMAYAN: yok. `__main__` yok. (Tertemiz.)
GARABET (F.1-J): `nokta_kaybi`nin `eps=1e-12`si ve `tasma_kaybi`nin
  1e-300 payları elle yazılmış; `nokta_kaybi` sözlü cinse `nebze`
  ağırlığı veriyor ve o nebze ARC isabetinden ÖLÇÜLÜYOR -- F.1-J'ye
  uygun, kayda geçiyorum (nadir bir doğru örnek).

### [46] nefs/rust.py -- 143 satır OKUNDU
CANLI hepsi: RustAyari, gf2_rank, sinir_operatorleri, topolojik_yirtik,
  rust_kilidi (kulli_mizan:624-631)
KULLANILMAYAN: yok. `__main__` yok. (Tertemiz.)
GARABET (F.2-J): `rust_kilidi` canlı yolda `math.exp` iki yerde
  (137, 143 -- sigmoid ve muayene). F.2-J listesinde YOK.
GARABET (F.1-J): `t0=0.5`, `tau=0.15`, `kapanis=0.5` -- üçü de elle
  yazılmış sabit ve α_rüşt'ü doğrudan tayin ediyor (tenakuzun
  fıtrata mı hafızaya mı gideceğini).

### [47] nefs/derleyici.py -- 72 satır OKUNDU
CANLI hepsi: DERLEME_DIZINI + ORTAK_BAYRAK (qcekirdek:281, gfni),
  ozet (qcekirdek:301 ölü `_ozet`ten + derle içinden), derle
KULLANILMAYAN: yok. `__main__` yok. (Tertemiz.)
GARABET: `_ONBELLEK` anahtarı `ad`dır, `oz` DEĞİL. İki ayrı kaynak
  aynı `ad`la derlenirse ilki önbellekten dönüyor -- kaynak değişse
  de yeniden derlenmiyor. (Fiilen iki ad var: "qcekirdek", "gfni".)

### [48] nefs/onbellek.py -- 88 satır OKUNDU
CANLI: yigin_sec (olcek:133), onbellek_boylari
KULLANILMAYAN: rapor() 69-85 + `__main__` (87) -- F.1-L
KULLANILMAYAN DAL: `yigin_sec(gpu=True)` -- hiçbir çağrı gpu=True
  vermiyor; içindeki `cek = 7424` elle yazılmış GPU çekirdek sayısı
  (F.5-B: donanım ölçülür, yazılmaz).
GARABET (ÇİFT BAŞLILIK): önbellek boyu İKİ yerden okunuyor --
  `nefs/onbellek.py:onbellek_boylari` ("L1"/"L2"/"L3") ve
  `nefs/donanim.py:onbellekler` ("L1d"/"L2"/"L3"). `olcek.py` İKİSİNİ
  DE çağırıyor (95-104 donanim, 133 onbellek). F.1-M: tek kaynak.
GARABET (F.1-J): `PAY = 0.20`, `ASGARI = 8`, `AZAMI = 4096` elle.

### [49] nefs/donanim.py -- 343 satır OKUNDU
CANLI: donanim (gpu_akis:153), cekirdek_sayisi + onbellekler (olcek:95),
  bellek_haddi (olcek:143), + donanim'ın çağırdıkları: saat_ghz,
  simd_bilgisi, bellek_bandi, bellek_baytlari, tamsayi_hizi, gpu_olcu,
  gpu_var_mi
KULLANILMAYAN: rapor() 287-339 + `__main__` (342) -- F.1-L
GARABET (F.1-L, CANLI YOLDA -- AĞIR): `donanim()` tahtın ilk
  `gpu_akisi` çağrısında koşuyor ve içinde:
   - `saat_ghz`: 3 000 000 turluk saf Python döngüsü (73-75)
   - `bellek_bandi`: 5 tekrarlı 64 MiB STREAM
   - `tamsayi_hizi`: 20 tekrarlı 4096×64 uint64 XOR/AND
   - `gpu_olcu`: GPU varsa 10 tekrarlı VRAM/PCIe/tamsayı ölçümü
  Yâni tâlim başlarken ~3 milyon Python turu + yüz MB'lık bellek
  trafiği ölçüm için harcanıyor. F.5-B "donanım ölçülür" der ve bu
  doğrudur; fakat ölçüm HER KOŞUDA yeniden yapılıyor (`_ONBELLEK`
  yalnız süreç içinde). `nefs/olcek.py:hiz_yoklamasi` neticesini
  `depo/olcek_hiz.json`a yazıyor, `donanim` yazmıyor.
GARABET (F.5 sessiz ikame, 6 yerde): 22, 42, 68, 126, 136, 186-202
  çıplak `except` ile sessiz geçiş. Özellikle `gpu_var_mi` üç
  `except Exception` ile GPU'nun yokluğunu sebebe yazıyor (bu kabul:
  sebep yazılıyor) fakat `onbellekler`in `except OSError: continue`u
  bir önbellek kademesini sessizce düşürüyor.
GARABET (ÇİFT BAŞLILIK): bkz. [48] -- önbellek iki dosyada iki ayrı
  anahtar adıyla okunuyor.

### [50] nefs/ara.py -- 21 satır OKUNDU
KULLANILMAYAN: ara() -- yalnız nefs/soyle.py:127'nin ÖLÜ `usul="ara"`
  dalından. Dosyanın TAMAMI ölü. `en_iyiyi_ara`, `had`, `kuyudan_cik`
  ithalleri de o yüzden ölü zincir.

### [51] nefs/gor.py -- 63 satır OKUNDU
KULLANILMAYAN: Manzara, gor -- HİÇBİR YERDE. Dosyanın TAMAMI ölü.
  (`nefs/soyle.py:85` `manzara` argümanını assert ile REDDEDİYOR:
  "soyle manzara ALMAZ (ferman 6)". Yâni bu dosyanın tek müşterisi
  fermanla kapatıldı.)
  Ayrıca `musahede.Gorev/ayir/genlige_gom/kaide` ithallerinin TEK
  müşterisi bu dosya; o hâlde [1]'de "(*) yalnız gor.py'den" diye
  işaretlediğim üç ad da ölü.
GARABET: `gor(ne="kalıp")` ferman 1-P gereği ValueError fırlatıyor --
  imha edilmiş bir yolun mezar taşı. Ferman 2-B "kökünden kes" der.

### [52] nefs/mantik.py -- 190 satır OKUNDU
CANLI: MAKAM_MERTEBE (kulli_kayip:823 -- fakat o `suz(ne="dalga")`
  içinde, `suz` de ölü → fiilen ÖLÜ)
KULLANILMAYAN (dosyanın TAMAMI):
  istikra_mertebesi · MAKAM_MERTEBE · ESKI_SIRA · GRAY_SIRA · _kod ·
  komsuluk_denetimi · eksik_mertebeler · yakin_yuzlestirmesi ·
  rapor + `__main__`
  Dosyanın tek dış müşterisi (`MAKAM_MERTEBE`) ölü bir dalda.
!!! Bu dosya `makam_mertebeleri`nin TEK müşterisi; o da tanımsız
  `MAKAM_ESIKLERI` yüzünden KIRIK ([34]). Yâni kırık fonksiyonun
  kırık müşterisi -- ikisi de ölü olduğu için patlamıyor.
GARABET (F.5): `rapor` 176-179 `except Exception: continue` ile
  görevleri sessizce düşürüyor.

### [53] nefs/hizli.py -- 278 satır OKUNDU
CANLI: hesap (ayna.py:16 → kivilcim:172 ve halka:231)
KULLANILMAYAN:
  kronecker      43-59   -- hiçbir yerde. Ferman 7 "Matrix-free
     Kronecker-SIMD"i ASIL usul ilan ediyor; bu fonksiyon onun
     Python/einsum icrası ve HİÇ ÇAĞRILMIYOR. Kronecker fiilen
     nefs/qcekirdek.py'nin C `karo_vur`u ve `_karo_blas`ıyla yapılıyor.
     F.1-M: aynı iş iki yerde, biri ölü.
  SEKTOR         62-66   -- ("sentaks",0,512)("ontoloji",512,2560)
     ("mantık",2560,4096) -- ELLE YAZILMIŞ üç sektör. Fiilî sektörler
     `QuditAyar.kulli_alanlar`dan (11 alan) türüyor. ÇİFT BAŞLILIK +
     F.1-J (elle yazılmış hudut). ÖLÜ.
  blok_carp      69-85   -- hiçbir yerde
  faz_cevir      88-97   -- hiçbir yerde (faz `qyazmac.faz` ile)
  _FUSED_KAYNAK 100-136  -- CUDA çekirdeği, 37 satır
  cekirdek      139-208  -- hiçbir yerde. Üç hatlı (cupy/torch/numpy)
     Clenshaw-Chebyshev çekirdeği. Ferman 7 "transandantal faz
     e^{iθ} İPTAL" der; bu fonksiyon `__expf/__cosf/__sinf` ve
     `np.exp/cos/sin` üstüne kurulu. ÖLÜ olduğu için ihlâl koşmuyor.
  rapor         211-274 + `__main__` (277) -- F.1-L
  _bicimle -- yalnız ölü fonksiyonlardan
DOSYANIN 278 SATIRININ 245'İ (%88) ÖLÜ; yalnız `hesap` canlı.

### [54] nefs/qudit.py -- 408 satır OKUNDU
CANLI: QuditAyari + suz (kulli_mizan:503-506 -- QSVT Hodge süzgeci),
  agirlik (qyazmac.faz:487, hizli.faz_cevir ölü)
KULLANILMAYAN:
  _cheb        51-60  -- yalnız durum/durum_yigin
  durum        63-81  -- yalnız rapor
  durum_yigin  84-133 -- yalnız rapor. İçinde `from .hizli import
     cekirdek` ölü dalı (89-96) ve Clenshaw.
  ortusme     136-139 -- yalnız rapor
  dallanma    184-230 -- yalnız rapor. Gelfand-Tsetlin örüntü sayımı;
     Zabıt 11'in GT araya girme hükmü FİİLEN nefs/casimir.py'nin
     `gelfand_tsetlin_araya_girme`sıyla yapılıyor → ÇİFT BAŞLILIK.
  metrik      233-245 -- yalnız rapor. **SONLU FARKLA** Fubini-Study
     metriği; ferman 2-P bunu ilga etti (senet_egimi.egim_ek_durum
     metriği analitik veriyor) → ÇİFT BAŞLILIK, biri kör fark.
  dogal_adim  248-270 -- yalnız rapor. CG ile doğal gradyan adımı;
     ferman 2-P'nin yarıçap+eğim usulüyle ÇİFT BAŞLI.
  BLOKLAR     273-277 -- ("sentaks",0,512)... hizli.SEKTOR ile
     ÜÇ BAŞLILIK (hizli.py:62, qudit.py:273, ve fiilî
     QuditAyar.kulli_alanlar). İkisi ölü.
  blok        280-298 -- yalnız rapor
  rapor       301-404 + `__main__` (407) -- F.1-L; içinde
     perf_counter zamanlama tabloları ve 6 kere `durum_yigin`
GARABET (F.2-J): `suz` CANLI YOLDA `np.cos` (158, 164) ve `np.exp`
  (160) kullanıyor -- Chebyshev düğümleri ve süzgeç çekirdeği.
  F.2-J listesinde YOK. Eklenecek. (Bu, ℒ_Hodge kefesinin tam içinde.)
DOSYANIN 408 SATIRININ ~330'U (%81) ÖLÜ.

### [55] nefs/lif.py -- 240 satır OKUNDU
Tek dış müşteri: nefs/qegitim.py:32 `from .lif import kodla,
  KIP_TUTARLI, KIP_LIE` -- o da `belirtecleri_kodla`nın ÖLÜ
  "sürekli"/"lie" dalında ([33]). O hâlde DOSYANIN TAMAMI ÖLÜ.
KULLANILMAYAN (hepsi): KIP_QUDIT/KIP_TUTARLI/KIP_LIE, kodla, mesafe,
  ortusme, sadakat, Lif(.tak .tipler .kategoriler .uzaylar .terim
  .unfold .dogrula .ac .izdusum .sayim), _esitle, rapor + `__main__`
GARABET (ÇİFT BAŞLILIK -- ÜÇ `Lif`): `Lif` adı
  nefs/lif.py:81 (bağımlı lif defteri), nefs/melekeler.py:227
  (mertebe lifi), ve `QAyar.lif_yapisi`/`QuditAyar.lif` (yazmaç lifi).
  Üçü alâkasız.
GARABET (ÇİFT BAŞLILIK -- `ortusme`): nefs/lif.py:51 ve
  nefs/qudit.py:136, aynı iş, iki gövde.
GARABET (ÇİFT BAŞLILIK -- `sadakat`): nefs/lif.py:60,
  nefs/melekeler.py:1317, nefs/qyazmac.py:240 -- üç ayrı `sadakat`.
GARABET (F.2-J): `kodla(KIP_TUTARLI)` `kuantum/surekli.py:tutarli_durum`
  çağırıyor (aşkın); ölü.

### [56] nefs/zirh.py -- 1066 satır OKUNDU
CANLI: vicdan (melekeler:1207,1225,1230 -- her melekeden sonra "işaret",
  sonra "usul", sonra "intaç"), ZirhAyari + zirhla + zirh_kaybi
  (kulli_mizan:554-600), taahhude_yuzlestir(sinif=,dS=) (kulli_mizan:559),
  yama + delik + iz (zirhla içinden), USULLER + ALANLAR + Usul +
  _yasak_cetveli (vicdan "usul"), HUKUM_ALANLARI (vicdan "intaç"),
  SINIF_CIHETI + NIZAM_BANDI (taahhude_yuzlestir), devirler (ithal)
KULLANILMAYAN:
  vietoris_rips 290-309 · dogum_olum_cetveli 312-333 ·
    cetveller_arasi_mesafe 336-416 (81 satır, Hopcroft-Karp eşleşmesi) ·
    kahan_toplam 419-427 · _mesafe · _cember · _iki_cember
    -- hepsi yalnız rapor'dan. TOPOLOJİ (kalıcılık homolojisi) kanadı
       tamamen rapora ait.
  dalgayi_yokla 281-287 -- hiçbir yerde
  ZirhIzi 271-279 -- yalnız `zirhla`nın yazmaç kolundan, o kol da
    yalnız rapor'dan (`kos` içinde) → ÖLÜ
  `zirhla`nın YAZMAÇ KOLU (180-230, 51 satır) -- `hedef`in `n` alanı
    olduğu hâl. kulli_mizan ndarray veriyor → ÖLÜ. İçindeki
    `devirler("zincir_β0")`, `y.tek_kapi` çağrıları da ölü.
  `zirhla`nın S/Pi_betti/Pi_koho kolu (122-128) -- hiçbir çağrı
    onları vermiyor → ÖLÜ
  muhru_stabilizerle_yuzlestir 638-690 -- yalnız rapor + `zirh_kaybi`nin
    `q is not None` kolu; `zirh_kaybi` hiç `q=` almıyor → ÖLÜ.
    `kuantum/stabilizer.py` ithalinin TEK müşterisi bu → o dosya da ölü.
  holonomi 693-694 · cevrim_egriligi 697-704 · duz_mu 707-708 ·
    aharonov_bohm 711-717 -- yalnız _rapor_bukum
  _rapor_bukum 720-787 -- HİÇ ÇAĞRILMIYOR (`rapor` onu çağırmıyor)
  rapor 789-1062 (274 satır) + `__main__` -- F.1-L
  SADAKAT_SIDDETI 446 -- hiçbir yerde
  KORUYUCU_BANDI 492 -- hiçbir yerde
  taahhude_yuzlestir'in NEFS KOLU (604-635) -- kulli_mizan yalnız
    (sinif, dS) ile çağırıyor → o kol yalnız rapor'dan
!!! İKİ TANIMSIZ AD (F.5):
  1. satır 22 `__all__` `"isaret_vur"` ilan ediyor -- bu ad depoda
     HİÇBİR YERDE TANIMLI DEĞİL. `from nefs.zirh import *` patlar.
  2. satır 724 `tunel_maliyet_cetveli(...)` -- tanımsız ad;
     `_rapor_bukum` çağrılsa NameError. (Çağrılmıyor.)
GARABET (ÇİFT BAŞLILIK): `holonomi` (zirh:693) ile kulli_mizan:110;
  `HUKUM_ALANLARI` (zirh:449, 6 alan) ile illet:10 (9 alan);
  `USULLER` (zirh:466, mantık aksiyomları) ile usul:13 (kıyas adları);
  `iz` (zirh:102, bağlantı holonomisi) ile qyazmac.Iz (senet) --
  dört ayrı çift başlılık.
GARABET (F.2-J): `taahhude_yuzlestir.ihlal` `np.tanh` (599),
  `zirh_kaybi` `np.exp`+`math.log` (255-256), `zirhla`nın ölü kolu
  `np.exp` (203) -- ilk ikisi CANLI YOLDA. F.2-J listesinde YOK.
GARABET (F.1-U MECLİS): `zirh_kaybi` beş cezayı `τ`-yumuşak azamîyle
  TEK SKALERE indiriyor (249-256). Ferman 1-U bunu yasaklıyor.
  kulli_mizan bunu bilerek yapıyor ve beşini AYRI kefe olarak da
  ekliyor (_z_bes, 601-608) fakat `zirh_softmax` diye o meclisi de
  rapora basıyor ("KIYAS; kayba GİRMEZ"). Yâni meclis kurulup
  kullanılmıyor -- F.5'e uygun fakat ölü hesap.

### [57] kuantum/stabilizer.py -- 200+ satır, TAMAMEN ÖLÜ
Tek müşterisi nefs/zirh.py:12 `StabilizerDurum` ve o da yalnız ölü
`muhru_stabilizerle_yuzlestir` içinde kullanılıyor.
HÜKÜM: ferman 7 "Galois GF(2⁸) + Stabilizer Tableau" ASIL usul der;
fakat FİİLÎ tableau `nefs/galois.py:Tableau`dur ([7]) ve o da
işletilmiyor. `kuantum/stabilizer.py` ÜÇÜNCÜ bir stabilizer temsilidir
ve ölüdür. ÜÇ BAŞLILIK.

### [58] kuantum/surekli.py -- TAMAMEN ÖLÜ
Tek müşterisi nefs/lif.py:21 `tutarli_durum`, o da ölü dalda ([55]).
`vakum`/`sikistirma` adları nefs/ayna.py ile ÇİFT BAŞLI ([10]).

### [59] idrak/kategori.py -- 171 satır
Tek müşterisi nefs/zirh.py'nin `Uzay`ı; `zirhla`nın ölü yazmaç kolunda
ve rapor'da → FİİLEN ÖLÜ.
ÇİFT BAŞLILIK: `AZAMI_TAM_MERTEBE`, `SABIT`, `_temsilci_kur` mantığı
nefs/melekeler.py:217-279'da BİR DAHA var ([32]); `Uzay` ile
`melekeler.Lif` aynı işi yapıyor (mertebe lifi kurma). İkisi de aynı
`matematik/tip_teorisi.py` uzuvlarını çağırıyor. melekeler'inki CANLI
(QTefekkur), idrak'inki ÖLÜ.

### [60] nefs/gfni.py -- 689 satır OKUNDU (C gövdesi dâhil)
CANLI: GFNI_C, derle, yoklama, kutuphane, _p8, _p64, sbox_gfni
  (galois:175), symplectic_gfni (donanim:162), ayrik_gfni +
  kaynasik_gfni (gpu_akis:62), genlesme_gfni (gpu_akis:104),
  cpuid + olc (donanim:80), AES_AFFINE/AES_SABIT (affine_gfni'de)
KULLANILMAYAN:
  _ozet()        391-393  -- hiçbir yerde (qcekirdek'teki kardeşi gibi)
  affine_gfni    496-503  -- hiçbir yerde; AES_AFFINE/AES_SABIT'in TEK
     müşterisi → o iki sabit de fiilen ölü
  gfcarp_gfni    506-513  -- hiçbir yerde (GF çarpımı `gf_carp` tablosuyla)
  dfa_tablosu    565-567  -- yalnız faz_dfa_gfni/akis_gfni/akis_olc
  faz_dfa_gfni   570-578  -- hiçbir yerde
  akis_gfni      581-589  -- hiçbir yerde
  akis_olc       592-623  -- hiçbir yerde
  rapor          657-684 + `__main__` (687) -- F.1-L
C TARAFINDA ÖLÜ: `mucit_affine`, `mucit_gfcarp`, `mucit_faz_dfa`,
  `mucit_akis` -- dördü de `kutuphane()`de imzası bağlanıyor,
  hiçbiri Python'dan çağrılmıyor.
GARABET (F.7 / F.1-F): Ferman 7 cetveli "**`vpshufb` faz otomatı**:
  64 baytlık LUT yazmaçta, tek vuruş"u ASIL usul ilan ediyor.
  O usulün fiilî icrası `mucit_faz_dfa` + `faz_dfa_gfni`dir ve
  **HİÇ ÇAĞRILMIYOR**. Faz fiilen `nefs/qyazmac.py:faz` +
  `palmer_indir` ile numpy'da yapılıyor. Yâni ferman 7'nin bu satırı
  YAZILMIŞ FAKAT KOŞMUYOR. F.1-F: "en derin kod koşturulur".
GARABET: `dfa_tablosu` LUT'u RASTGELE üretiyor (`r.integers`) -- faz
  otomatının tablosu bir faz polinomundan değil rastgeleden geliyor.
  (Ölü olduğu için tesiri yok.)
GARABET (F.1-L): `akis_olc` 20 000 turluk L1 döngüsü; `olc` 20 turluk.
  `olc` CANLI (donanim:80 → simd_bilgisi) → her tâlim koşusunda
  4 MiB'lık 20 tekrarlı GFNI/tablo kıyası koşuyor.

### [61] kuantum/kapilar.py -- 371 satır OKUNDU
CANLI: dik_iki_kubit + dik_iki_kubit_yigin + _so4_ureteci (melekeler'de
  9 melekeden), dik_iki_kubit_turevi + _SO4_TEMELI + _so4_temeli
  (melekeler:467, tuğla türevi), chebyshev (optimize:70), uniter_mi
  (optimize:254)
KULLANILMAYAN:
  I2·X·Y·Z·H·S_·Sdg·T_·Tdg·PAULI  (21-31) -- hiçbiri dışarıdan
  _donme·Rx·Ry·Rz·U1·U2·U3·faz    (34-69)
  kron (72-76) · kontrollu (79-84) · CNOT·CZ·SWAP·iSWAP·TOFFOLI·
    FREDKIN (87-94) · CRx·CRz (97-102)
  _cift_donme·RXX·RYY·RZZ (105-120) · molmer_sorensen (123-131)
  yerlestir·_permutasyon_dizeyi (134-159) · esdeger_mi (170-184) ·
  komutator·antikomutator (187-192)
  _gosterim (195-300, 106 satır) · rapor (314-315) + `__main__` (318)
  KAPI_USULU (322) -- hiçbir yerde
  → `__all__`daki 33 addan 31'i ÖLÜ; yalnız `chebyshev` ve `uniter_mi`
    dışarıdan çağrılıyor. Asıl canlı uzuvlar (`dik_iki_kubit`,
    `dik_iki_kubit_turevi`) `__all__`da İLAN EDİLMEMİŞ.
GARABET (F.1-L): `_gosterim`, dosyanın ortasında (195-300) duruyor ve
  `chebyshev`i ikiye bölüyor -- `__main__` bloğu 318'de, ondan SONRA
  da hâlâ kod var (322-371). Dosya iki kere bitiyor.
GARABET (F.2-J): `dik_iki_kubit_yigin` ve `dik_iki_kubit_turevi`
  `np.linalg.eigh` + `np.exp(-1j·λ)` ile dizey üsteli kullanıyor --
  CLAUDE.md 2-J bunu ZATEN "en sıcak olanı budur" diye sayıyor. ✓
  (Türev de aynı yolda; 2-J'ye türev satırı eklenebilir.)

### [62] kuantum/devre.py -- 36 satır OKUNDU
CANLI: qft_dizeyi (ayna:160,191 -- kivilcim ve faz_kaydir)
KULLANILMAYAN: iqft_dizeyi, _uexp, trotter, suzuki2 -- hiçbiri
  dışarıdan. `__all__`ın 4 adından 3'ü ölü.
GARABET (ÇİFT BAŞLILIK): `_uexp` adı melekeler.py:1295'te de var,
  aynı iş (dizey üsteli). İkisi de ayrı gövde.

### [63] kuantum/eniyileme.py -- 284 satır OKUNDU (yapı okundu)
CANLI: baslangic_hamiltonyeni + maxcut_hamiltonyeni + tayf_araligi
  (ayna:321-344 → `_halka_netice`, o da `halka(ne="döküm")`den,
  o da kulli_mizan:313 `engellenme`den) -- CANLI YOL
  kesitli_hamiltonyen (tayf_araligi içinden), _tensor, _tek_kubit
KULLANILMAYAN: adiyabatik_kos, qaoa_durumu, qaoa_beklenen,
  qaoa_eniyile, _mixer_uygula, parametre_kaydirma, _sonlu_fark,
  kaydirma_sarti_ihlali, _gosterim (180-282, 103 satır) + `__main__`
GARABET (F.2-J): `tayf_araligi` CANLI YOLDA 41 kere `np.linalg.eigvalsh`
  çağırıyor (2^N × 2^N dizey, N≤8 → 256×256). `engellenme` her mizan
  çağrısında koşuyor. F.2-J listesinde YOK; ayrıca F.7'nin
  "yoğun matris" iptaline aykırı.
GARABET (F.1-M): `parametre_kaydirma` (parameter-shift gradyanı) ölü;
  ferman 2-P türevi senet_egimi'ne verdi. Dördüncü gradyan motoru.

### [64] kuantum/topolojik.py -- 319 satır OKUNDU (yapı okundu)
CANLI: orgu_ureticleri + yang_baxter_hatasi + fibonacci_F/R/B
  (ayna:85,356 -- `bolucu(korunakli=True)` ve `olc`)
  ** fakat `bolucu`nun `korunakli` kolu hiç açılmıyor (AynaAyari.
  korunakli öntanımlı False ve kimse True vermiyor) ve `olc` ölü →
  FİİLEN ÖLÜ
KULLANILMAYAN: orgu_kelimesi, _faz_anahtari, _hedef_mesafesi,
  orgu_yogunlugu, _jw_c, majorana, jw_zincirsiz_majorana,
  antikomutator_hatasi, YuzeyKodu (151-220, 70 satır), _gf2_sira,
  _gosterim (243-317) + `__main__`
  → DOSYANIN TAMAMI FİİLEN ÖLÜ.
GARABET (F.7 / ÇİFT BAŞLILIK): `majorana` ve `jw_zincirsiz_majorana`
  Majorana operatörlerini kuruyor; ferman 7-A(1) Matchgate/FLO'yu
  Majorana kovaryansında ASIL usul ilan ediyor ve o fiilen
  `nefs/matchgate.py:Ortam`da kurulu. İki ayrı Majorana temsili.

### [65] ogrenme/morse.py -- 124 satır OKUNDU
CANLI hepsi: euler_karakteristigi, morse_indisleri,
  morse_euler_denklik_tahkiki, _alt_bag_chi, _HALKA (ayna:295-301 →
  `_halka_netice` → `halka(ne="döküm")` → kulli_mizan `engellenme`)
KULLANILMAYAN: tahkik_cetveli (94-107) · rapor (110-122) + `__main__`
GARABET (F.1-L, CANLI YOLDA): `morse_indisleri` her renk için
  H×W çift döngü + 8 komşu taraması koşuyor; `engellenme` her mizan
  çağrısında `halka(ne="döküm")` ile bunu çağırıyor. Saf Python
  döngüsü, kayıp fonksiyonunun içinde.
GARABET (F.5): `morse_euler_denklik_tahkiki` ayna.py:297'de assert ile
  koşuluyor -- bu DOĞRU bir kırmızı ölçüdür. ✓

### [66] ogrenme/grassmann.py -- 237 satır OKUNDU (yapı)
CANLI: dik_taban, asal_acilar, grassmann_mesafesi (musahede:1788-1798
  `iki_olcegin_acisi(ne="açı")` -- o da yalnız musahede.rapor'dan;
  optimize:1490 `_grassmann_farki` -- optimize okunduğunda karara
  bağlanacak)
KULLANILMAYAN: izdusum, alt_uzay_hatasi, exp_haritasi, _log_cekirdegi,
  log_haritasi, log_haritasi_arcsin, gidis_donus_hatasi,
  grassmann_geodezigi, grassmann_ortalamasi, normalize_laplasyen,
  betti0_tayftan, tikhonov_cekirdegi_yok_eder, _rastgele,
  _gosterim (144-235, 92 satır) + `__main__`
GARABET (ÇİFT BAŞLILIK): `normalize_laplasyen` (grassmann:111) ile
  `devirler("laplasyen")` (melekeler:109) ve `_laplasyen`
  (kulli_mizan:329) -- ÜÇ ayrı Laplasyen kurucusu.
  `betti0_tayftan` (grassmann:118) ile `delik(ne="betti")` (zirh:84)
  ve `devirler("betti")` (melekeler:113) -- ÜÇ ayrı Betti sayıcısı.

### [67] ogrenme/rkhs.py -- 290 satır OKUNDU (yapı)
CANLI: RKHS, gauss_cekirdegi, medyan_genislik, psd_mi (musahede:1745-48
  `iki_olcegin_acisi(ne="sağîr")`; o da kulli_kayip:527/808 ve
  musahede.rapor'dan -- kulli_kayip:527 `tasavvur._iki_olcek`
  içinde ve O FONKSİYON `gorev_ozellikleri` yüzünden KIRIK ([31]),
  kulli_kayip:808 `suz(ne="dalga")` ölü → FİİLEN ÖLÜ)
  optimize:17 `gek_uydur` -- optimize okunduğunda karara bağlanacak
KULLANILMAYAN: _kare_mesafe(iç), laplace_cekirdegi, matern_cekirdegi,
  polinom_cekirdegi, gram, temsil_teoremi_sagmasi, nystrom,
  _gosterim (187-283) + rapor + `__main__`
GARABET (F.2-J): `gauss_cekirdegi` `np.exp`, `matern` `np.sqrt/exp`,
  `laplace` `np.exp` -- canlı yolda mı, optimize okunduktan sonra
  kesinleşecek.

### [68] ogrenme/optimize.py -- 2091 satır (yapı + canlı bölge okundu)
CANLI (TEK UZUV): `gaye_kos` (1403-1428) -- melekeler:1228'den, yâni
  `QNefs.idrak_et`in `self.gaye` kolundan. Onun çağırdıkları:
  `_aci` (1432), `donme`, `q.mpo_topla/mpo_dagit/tek/uzak_cift`,
  `EPSILON_DURGUN`, `math.tanh`.
  Ayrıca: `chebyshev`+`uniter_mi` ithalleri (kuantum.kapilar),
  `RKHS/gauss_cekirdegi/medyan_genislik` (rkhs), `QYazmac/donme`
  (zihin_durumu), `QParametre` (melekeler) -- son üçü ölü bölgelerde.
KULLANILMAYAN -- dosyanın geri kalanının TAMAMI (~2050 satır):
  NQSAyar + NQS (21-195)  -- Zabıt 11 Safha III'ün "NQS kollektif
     dalgası"; SERH.md'de "kodlu fakat hiç çağrılmıyor" diye zaten
     yazılıydı, TEYİT EDİLDİ.
  KIP_* sabitleri (199-214, 432-462) -- 16 adet kip adı
  _yansima_govdesi · blok_kodlama · faz_dizisinin_polinomu ·
    _izdusum_donmesi · qsvt · _devreyle_qsvt · ters_polinomu ·
    statik_faz_tablosu_oku · qsvt_gibbs_sogutma · gibbs_dogrulamasi ·
    chebyshev_tasarimi (217-430) -- QSVT kanadı. `nefs/qudit.py:suz`
    AYRI bir QSVT icrası → ÇİFT BAŞLILIK; suz canlı, bu ölü.
  J · _kappa_olc · _adimla · kestirmeden_sur (465-555)
  _SZ/_SX/_SY · qsp_fazlarini_bul (556-622)
  GIBBS_DERECE · GIBBS_FAZ_TABLOSU (32 elemanlı elle yazılmış faz
    tablosu) · gibbs_fazlari · fazlari_kilitle (623-723)
  yokus (724-856) -- 133 satır, önşartlı gradyan
  oragin_donusu (857-898) · tartinin_dayandigi_nokta (899-926)
  DalgaCevrimi · DalgaEniyileyici (927-1077) -- 151 satır, ESKİ
    eniyileyici. Ferman 2-P mecz'i tek motor yaptı → ÖLÜ.
  Ikiz · _sar · ikiz · tam_turev · _ureteci_ikiz · _birim_gibi · _iz
    (1078-1243) -- İKİZ SAYI (forward-mode AD). ogrenme/senet_egimi.py
    `egim_ikiz` AYRI bir ikiz icrası → ÇİFT BAŞLILIK; senet canlı,
    bu ölü.
  OgdaTarti · oyun_degeri (1244-1292)
  TabiiAyar · TabiiCevrim · TabiiGradyan (1293-1400) -- 108 satır,
    tabiî gradyan. `nefs/qudit.py:dogal_adim` ile ÇİFT BAŞLI, ikisi de ölü.
  odenen_bedel (1439-1482) · hareketin_altuzayi (1484-1507) ·
    _tavla_govdesi · ayrik_mertebede_sicra (1509-1545) ·
    gek_uydur (1546-1577) · dalga_yayilimi (1578-1595) ·
    as_gek_adimi (1596-1634) -- son ikisi yalnız `qegitim.egit`ten,
    o da ölü ([33])
  kuyudan_cik (1635-1790) -- 156 satır; yalnız nefs/ara.py'den, o ölü
  HBAR · _arama_izi · had (1791-1925) -- yalnız nefs/ara.py'den
  NesterovEnKotu (1926-1958) · esit_superpozisyon · faz_kehaneti ·
    esik_kehaneti · difuzyon · grover_turu · en_iyiyi_ara
    (1959-2065) -- Grover/Dürr-Høyer araması; yalnız nefs/ara.py'den
  _baslangic_H · tayf_araligi_asgari (2066-2091)
HÜKÜM: 2091 satırlık dosyanın 26 satırı (%1,2) canlı.
GARABET (F.1-M -- DÖRT GRADYAN MOTORU): senet_egimi (canlı),
  optimize.Ikiz/tam_turev (ölü), optimize.TabiiGradyan (ölü),
  melekeler.grape_* (ölü), kuantum/eniyileme.parametre_kaydirma (ölü),
  qudit.metrik+dogal_adim (ölü). ALTI ayrı türev/metrik icrası.
GARABET (F.1-J): `GIBBS_FAZ_TABLOSU` 32 elemanlı ELLE YAZILMIŞ faz
  dizisi; `EPSILON_DURGUN = 0.45` canlı yolda elle yazılmış sabit ve
  sükût alanına doğrudan vuruyor.
GARABET (F.2-J): `gaye_kos` CANLI YOLDA `np.tanh` (1411) kullanıyor.
  F.2-J listesinde YOK. Eklenecek.

## MATEMATİK KATI -- 12 774 SATIR, DÖRT DOSYA

Bu dört dosyanın her tanımı tek tek yoklandı (ad bazında, kendi dosyası
hariç dışarıda atıf var mı). Aşağıdaki "ÖLÜ" listeleri o yoklamanın
neticesidir; bir ad ancak kendi dosyasındaki CANLI bir giriş noktasından
çağrılıyorsa canlıdır.

### [69] matematik/fitrat.py -- 1623 satır, 76 tanım
CANLI GİRİŞ NOKTALARI:
  logsumexp (kulli_kayip:220 → zayif_halka "azamî" → meleke kefesi) CANLI
  Cizge + gecer_mi (illet:5 → alan_cizgesi/zaman_cizgesi/kelam_ayrismasi
    → tahtın `gecit`i) CANLI
  fazla_sayma + tevafuk_olcusu -- melekeler:14'te İTHAL EDİLİYOR fakat
    melekeler gövdesinde HİÇ KULLANILMIYOR (grep: yalnız 14. satır).
    ÖLÜ İTHAL. Gerçek müşterileri musahede.rapor ve
    musahede.iki_sahit_ayri_mi -- ikisi de ölü.
  cift_uyusmasi -- yalnız musahede.iki_sahit_ayri_mi (ölü)
  AyrikModel + kl + serbest_enerji_ayrisimi -- yalnız
    optimize.odenen_bedel (ölü)
ÖLÜ (76 tanımdan 68'i; dışarıdan sıfır atıf):
  _erisilenler _yollar _yol_acik_mi butun_ayrismalar _oku_sokulmus
  _oku_cikarilmis arka_kapi_kumeleri _yonlu_yollar_kesiliyor_mu
  ortak_ayrismalar _rapor_fitrat_ayrisma YapisalModel budayarak_mudahale
  abduction abduction_degismezi karsiolgusal abduction_tekil_mi
  _matris_ustel notears_h notears_gradyan cevrimsiz_mi_h_ile
  ortuk_sahte_baginti locus_izdusumu locus_uzerinde_yurut _ornek_model
  _rapor_fitrat_karsi_olgusal kanit_log elbo sinir_dogrula
  koordinat_inisi gauss_kl gauss_serbest_enerji
  _rapor_fitrat_serbest_enerji Oyun merkezi_jakobi newton_koku denge_bul
  spektral_yaricap kararli_mi en_iyi_karsilik_iterasyonu
  ortuk_fonksiyon_turevi hassasiyet_sonlu_farkla cournot
  cournot_kapali_cozum _rapor_fitrat_denge _pearson sartli_bagintisi
  log_olabilirlik_orani bayes_yigma sahit_uret _rapor_fitrat_tevafuk
  log_normalize Hukum Hipotez Havuz _bernoulli _havuz_kur
  _rapor_fitrat_havuz _egim _kismi_egim baglanim_mudahale_ayrimi
  olculmemis_karistirici catal_ve_carpisma _rapor_nedensel
GARABET (F.1-M): `notears_h`/`cevrimsiz_mi_h_ile` (DAG asiklik ölçüsü)
  ile `nefs/illet.py:cevrimler` aynı işi yapıyor; ikincisi canlı.
GARABET (F.1-M): `spektral_yaricap` ile `ogrenme/operator.py:
  spektral_rutbe` ve `matematik/geometri.py:spektral_enerji` -- üç
  ayrı tayf ölçüsü.

### [70] matematik/mizan.py -- 2304 satır, 130 tanım
CANLI GİRİŞ NOKTALARI:
  Onerme + Tablo + deg + degil + ise + ve (zirh:14 → USULLER +
    _yasak_cetveli → vicdan(ne="usul") → HER MELEKEDEN SONRA) CANLI
  MERTEBELER (melekeler:288 MERTEBE_SIRA -- o da ölü; kulli_kayip:33
    _mertebeler -- yalnız mertebe(ne="adlandır"), ölü) ÖLÜ
  ardisiklik_kaidesi/tam_istikra_mi/ZANN_I_GALIB_ESIGI/hukum_agirligi/
    ikili_entropi/makam_tayin/mertebe_adi/yakin_gazali/yakin_zinciri
    -- melekeler:16-19'da İTHAL, gövdede HİÇ KULLANILMIYOR. ÖLÜ İTHAL.
    (Gerçek müşteriler: kulli_kayip.suz/Kademeler.tasdik ve mantik.py;
     ikisi de ölü.)
  aksiyom + hukum -- yalnız kulli_kayip.Kademeler.ispat._mantik (ölü)
ÖLÜ (130 tanımdan 120'si): yukarıda listelenen 120 ad
  (_kur tablo_boyu xor elmas _tablo_kur … Munazara _rapor_mizan_munazara)
GARABET: Bu dosya klasik mantığın (kıyas, LK, sekans, Kripke çerçeveleri,
  çok değerli mantık, relevans, ortomodüler kafes, Nyaya, Stoa,
  münazara) TAM bir kütüphanesi ve ana akış bunun YALNIZ 6 adını
  (Onerme, Tablo, deg, degil, ise, ve) kullanıyor -- o da dört
  aksiyomluk bir doğruluk tablosu için.

### [71] matematik/geometri.py -- 4852 satır, 202 tanım
CANLI GİRİŞ NOKTALARI:
  bspline_temeli + bspline_turev_temeli + dugum_dizisi (izgara:12 →
    duzenli_uydur → tahtın `ogreniyor_mu`su) CANLI
  spektral_enerji (kulli_kayip:552 `_tayf` → tasavvur → kademeleri_kos
    → kulli_mizan meleke kefesi) CANLI
  Donanim + donanim + topla_paralel (optimize:14 -- modül seviyesi
    ithal; `gaye_kos` için optimize ithal edilince KOŞUYOR fakat
    adlar yalnız ölü bölgelerde kullanılıyor) ÖLÜ İTHAL
  tek_iplik_zorla + rapor + donanim (kaggle_donanim -- `kos` kırık,
    `ayar_sec` yalnız `donanim`ı kullanıyor; kaggle kipi zaten
    [39] yüzünden çöküyor) FİİLEN ÖLÜ
  Metrik + metrik + Morfizm + izometri_mi + jakobi (musahede:17-18 →
    yalnız `kopru`, ölü) ÖLÜ
ÖLÜ (202 tanımdan ~190'ı): yukarıdaki uzun liste
  (cas hartley … deeponet_sinamasi _rapor_asgari _rapor_modern)
GARABET (ÇİFT BAŞLILIK -- BÜYÜK): bu dosya `DeepONet` (4700),
  `FNO`/`SpektralKatman` (fno bölümü), `KAN211`, `EvrisimKatmani`,
  `Funktor`/`lan`/`ran` (Kan uzantıları), `so_izdusumu`,
  `kure_izdusumu`, `bochner_suzgeci`, `postnikov_indisi` taşıyor.
  `DeepONet` ogrenme/operator.py:23 ile ÇİFT BAŞLI ([ferman 2-H
  okuması]); `lan`/`ran` kulli_kayip:1054 ile ÇİFT BAŞLI;
  `tek_iplik_zorla` main/egitim.py:103 ile ÇİFT BAŞLI.
GARABET (F.1-L): `rapor()` (4840) 21 bölümlü bir gösteri ve
  `BOLUMLER` cetvelinden koşuyor; tahttan çağrılmıyor.

### [72] matematik/tip_teorisi.py -- 3995 satır, 312 tanım
CANLI GİRİŞ NOKTALARI:
  Baglam + Cember + Deg + Evren + Taban + denetle_t + dongu_uzayi_n +
    morfizm_tipi (melekeler:20 → `lifleri_kur` → QTefekkur(𝒪21) →
    HER İLERİ GEÇİŞTE) CANLI
  bosluklar (musahede:1804 `terkip_saglam_mi` -- ölü) ÖLÜ
  Sigma/Cift/Birinci/Ikinci/Dogal/degerlendir/geri_oku/BOS (lif -- ölü)
  Dugum/Lam/… (idrak/kategori -- ölü)
  Ard/Aralik/Poz/Sfr/Tamsayi/Terim/Transp/YANLIS/YolUygula/
    ardil_denkligi/esdeger_mi/nf/ozdeslik_denkligi/taze/ua/BIR/SIFIR
    (geometri:15 -- geometri'nin canlı uzuvları bunları kullanmıyor) ÖLÜ
ÖLÜ (312 tanımdan ~300'ü): yukarıdaki çok uzun liste
  (terim_taze … pres)
GARABET: ana akış bu 3995 satırdan yalnız `lifleri_kur`un ihtiyacı
  olan 8 adı kullanıyor; `lifleri_kur` da 20 lif için
  `morfizm_tipi(A, m)` kurup `denetle_t` ile denetliyor ve neticeyi
  YALNIZ `Lif.olcek`/`Lif.adim` gibi skalerler için okuyor.
  Yâni 3995 satırlık bağımlı tip teorisi kütüphanesi, 20 sayı üretmek
  için koşuyor.

## SON SAFHA: TAHTIN ÇAĞIRMADIĞI KALAN DOSYALAR (247 dosya)

### [73] Altı `__init__.py` -- 11 satır
`main/__init__.py` BOŞ. Öteki beşi `__all__` ilan ediyor ve
İLAN ETTİKLERİ MODÜLLERİN ÇOĞU YOK:
  nefs/__init__: uzaylar, meleke, idrak, akil, murakabe, beyan, akis
    → YEDİSİ DE YOK (nefs/ altında böyle dosya yok)
  ogrenme/__init__: rkhs, operator, izgara, grassmann → dördü var
  matematik/__init__: tip_teorisi, mizan, fitrat, geometri → dördü var
  kuantum/__init__: kapilar, devre, tda, qsvt, surekli, topolojik,
    eniyileme → `tda` ve `qsvt` YOK
  idrak/__init__: arc, kubit, model, egitim → DÖRDÜ DE YOK
HÜKÜM: on bir modül adı ilan edilmiş, ON BİRİ de yok. `from nefs import *`
  denirse ImportError. Ferman 5: yapılmayan yapıldı diye yazılmaz.

### [74] idrak/kategori.py -- 171 satır OKUNDU
Tek dış atıf `Uzay` (zirh, ölü kolda). ÖLÜ.
KULLANILMAYAN (hepsi): Uzay, SABIT, AZAMI_TAM_MERTEBE, _baglayici_say,
  _tam_kur, _temsilci_kur, uzaylari_kur, tikanma_tipi,
  kesit_tipi_ile_agirlik, akit_denetle, rapor + `__main__`
ÇİFT BAŞLILIK teyit: `_tam_kur`/`_temsilci_kur`/`SABIT`/
  `AZAMI_TAM_MERTEBE` nefs/melekeler.py:248-279'da HARFİYYEN aynı;
  melekeler'inki CANLI (QTefekkur), bu ölü.

### [75] kuantum/stabilizer.py -- 200 satır OKUNDU
KULLANILMAYAN (hepsi): ALFA, bgs_haddi, StabilizerDurum (.arti .kopya
  .z .s .cz .faz .genlik), StabilizerRank (.genlik .z .s .cz .t
  .budama .seyreklestir .durum), _gosterim + `__main__`
  (`StabilizerDurum` yalnız zirh'in ölü `muhru_stabilizerle_yuzlestir`i)
GARABET (F.7): `StabilizerRank.budama` ve `seyreklestir` -- ferman 7
  "SVD/bond truncation İPTAL" der; bu budama SVD değil fakat aynı
  cinsten bir kesmedir ve ferman 7-A Bravyi-Gosset'i tescil ediyor.
  Kod var, koşmuyor.
GARABET (F.2-J): `StabilizerRank.t` `np.exp(1j·π/4)`, `genlik`
  `1j**q` -- ölü.

### [76] kuantum/surekli.py -- 232 satır OKUNDU
KULLANILMAYAN (hepsi): HBAR, expm, yok_et, yarat, sayi, konum,
  momentum, komutator_sapmasi, yer_degistirme, sikistirma, isik_bolucu,
  kerr, kubik_faz, kesirsel_fourier, tutarli_durum, vakum, fock,
  _log_faktoriyel, foton_dagilimi, kuadratur_belirsizligi,
  uniterlik_sapmasi, kesme_hatasi, _gosterim + `__main__`
  (`tutarli_durum` yalnız nefs/lif.py'nin ölü dalı)
ÇİFT BAŞLILIK: `vakum`+`sikistirma` ↔ nefs/ayna.py:99,118 (`vakum`,
  `sikistir`); `expm` ↔ melekeler `_uexp`/`_genel_expm` ve
  devre `_uexp`. DÖRT dizey üsteli icrası.

### [77] idrak/veri/soyutlamalar/ -- 236 dosya, 41 899 satır, 120 dizin
BU DOSYALAR MODÜL DEĞİL, VERİDİR:
  - `idrak/veri/` altındadır ve `tanilama/sabit_teftisi.py:16`
    `_KOD_DEGIL` cetveli onu KOD SAYMIYOR.
  - Depoda hiçbir yerden ithal edilmiyorlar (grep: `soyutlamalar`
    yalnız musahede.py:29'da ve orada `abstractions.md` okunuyor,
    `.py` değil).
  - `soyutlama_oku` yalnız `abstractions.md` dosyasını okuyor.
O HÂLDE: 236 dosyanın TAMAMI, içindeki HER sınıf ve fonksiyon
  KULLANILMAYANDIR. (Tek tek okumak yerine tek hükümle tasnif ettim;
  yapısı tek örnekle teyit edildi: 0934a4d8/solution.py 99 satır,
  abstractions.py 183 satır, ikisi de göreve mahsus Python çözücü.)
!!! ÜÇ AYRI FERMAN İHLÂLİ:
  1. FERMAN 6 ("elle yazılmış kâide, göreve mahsus çözücü YASAKTIR"):
     120 ARC görevi için 120 ayrı elle yazılmış çözücü. Depoda
     duruyorlar. Koşmuyorlar fakat DURUYORLAR.
  2. FERMAN 4 (halkça isim): tanımların tamamı İNGİLİZCE --
     Candidate, Component, Lattice, Motif, Ring, Shape, bbox,
     load_dataset… Bütün proje Türkçe, bu ağaç İngilizce.
  3. KIRIK VERİ YOLU: `abstractions.py`lerin `DATA_PATH`i
     `idrak/veri/arc2_samples/<ad>.json` diyor; O DİZİN YOK.
     Yâni çalıştırılsalar da veriyi bulamazlar.
FERMAN 2-C gereği imha kararı SORULMADAN VERİLMEZ; burada yalnız
  tasnif ediliyor.

═══════════════════════════════════════════════════════════════════════
## HÜKÜM -- "MAINDE OLMASI GEREKİP DE OLMAYAN" NE VAR
═══════════════════════════════════════════════════════════════════════

Bu, emrin son maddesidir. Cevap dört başlıkta:

### A. TAHTIN KENDİSİNDE OLUP KOŞMAYAN (kırık): DÖRT
  ▓ DÖRDÜ DE KAPATILDI ▓  (1: beyan ithali; 2: kaggle üçlüsü kesilip
  tahtın kipine katlandı; 3: meclis ithali kesildi -- ferman 1-U onu
  zaten yasaklamıştı; 4: MAKAM_ESIKLERI ferman 1-J'ye uygun fonksiyona
  çevrildi, tunel_maliyet_cetveli ve isaret_vur kesildi,
  gorev_ozellikleri çağrısı kesildi.)
  ▓ SONRADAN BULUNAN: `nefs/musahede.py:IzafiMevki2D` -- `_komsuluk`
  tanımsız, hiç çağrılmıyor, `ebat_kanunu_coz` ferman 1-P'nin
  yasakladığı ölçü kestirimi. Kesildi.

### B. TAHTA BAĞLI OLUP İŞ GÖRMEYEN (ferman 1-C(b) münafıklığı)
  1. **𝒪44 QTahsil** -- `q.bolge_var("parametre")` daima False,
     meleke hiçbir zaman hiçbir şey yapmıyor. 44 melekenin biri ölü.
  2. **`mpo_topla`/`mpo_dagit`in `duraklar` ve `j` argümanları** --
     alınıp atılıyor; 𝒪7, 𝒪21, 𝒪30, 𝒪34, 𝒪37 ve `gaye_kos` durak ve
     kanal ayrımı veriyor, hepsi sektörün ortalama fazına çöküyor.
  3. **`Tableau`** kuruluyor, `beyan()`i okunuyor, X/Z/faz tablosuna
     ana akışta hiçbir kapı vurulmuyor (`xor_isle`/`faz_isle`/
     `galois_isle`/`parite_alarmi` ölü).
  4. ▓ KAPATILDI ▓ `Harita` artık hazineden yükleniyor ve hazineye
     geri konuyor; turlar boyunca birikiyor.
  5. ▓ KAPATILDI ▓ `Hizolcer.sert` tahtta açıldı; aşım ayrı bir kefe,
     tavan (hattın kendi ısınma nispeti) aşılınca assert.
  6. **`QuditYazmac.sadakat()`** daima 1.0 → "kesme yapısal" kefesi
     sabit.
  7. **`suz` / müdrike zinciri** -- `_ara()` daima `[]` döndüğü için
     kaide hiç bulunamıyor; zaten `degerlendir(mudrike_ile=True)`
     hiç verilmediği için tamamı ölü.
  8. ▓ KAPATILDI ▓ dosya kesildi; `main/cikarim.py:teslimat_uret`
     cevabı `padisah()` ile üretiyor, ızgara ayrıştırılamazsa YANLIŞ
     CEVAP sayılıyor (ferman 1-P).

### C. FERMAN 7'NİN "ASIL USUL" İLAN EDİP KOŞMAYANLARI
  1. `vpshufb` faz otomatı (`mucit_faz_dfa` + `faz_dfa_gfni`) -- C'de
     yazılı, imzası bağlı, HİÇ ÇAĞRILMIYOR. Faz numpy'da koşuyor.
  2. `mucit_bant` + `karo_vur` + `cift_vur` (qcekirdek C) -- yalnız
     `mucit_cift_bant` çağrılıyor; karo BLAS'a gidiyor.
  3. `mucit_ayristir`/`mucit_birlestir` (AVX-512) -- hiç çağrılmıyor.
  4. `mucit_affine`, `mucit_gfcarp` -- hiç çağrılmıyor.
  5. Matrix-free Kronecker (`nefs/hizli.py:kronecker`) -- ölü.

### D. SAYIM
  Okunan dosya            : 83  (taht zinciri + seviye 2 + kalanlar)
  Tasnif edilen dosya     : 319 (236'sı veri ağacı, tek hükümle)
  TAMAMEN ÖLÜ DOSYA       : 13 idi, ŞİMDİ 4
    ▓ CANLANDI ▓ nefs/ara.py (NAKİL memuru) · nefs/lif.py (silsile
      defteri + ℒ_Lif kefesi) · idrak/kategori.py (h-mertebe denetimi) ·
      idrak/veri/soyutlamalar (236 dosya, artık VERİ)
    ▓ KESİLDİ ▓ main/kaggle_egitim.py · main/kaggle_cikarim.py ·
      ogrenme/kaggle_donanim.py
    ▓ HÂLÂ ÖLÜ ▓ nefs/gor.py · nefs/mantik.py · kuantum/stabilizer.py ·
      kuantum/surekli.py · kuantum/topolojik.py
  %80'DEN FAZLASI ÖLÜ DOSYA : 6
    ogrenme/optimize.py (%98,8) · nefs/hizli.py (%88) ·
    matematik/tip_teorisi.py (~%96) · matematik/mizan.py (~%92) ·
    matematik/geometri.py (~%94) · matematik/fitrat.py (~%89) ·
    nefs/qudit.py (%81) · kuantum/kapilar.py (%94) ·
    ogrenme/izgara.py (%59)
  `rapor()` + `if __name__ == "__main__"` taşıyan dosya : 38
    (ferman 1-L: tahttan başka koşu yok; bunların 3'ü tahtın kipi --
     kulli_mizan.rapor, sabit_teftisi.rapor, veri.rapor -- 35'i ölü)
  ÇİFT/ÜÇ/DÖRT BAŞLI AD    : 24 tesbit edildi
    holonomi(2) · Ortam(3) · Lif(3) · sadakat(3) · ortusme(2) ·
    HUKUM_ALANLARI(2) · USULLER(2) · kestir(2) · povm(2) · kodla(2) ·
    _uexp/expm/_genel_expm(4) · Laplasyen(3) · Betti(3) ·
    DeepONet(2) · AZAMI_TAM_MERTEBE+SABIT(2) · tek_iplik_zorla(2) ·
    vakum+sikistirma(2) · SEKTOR/BLOKLAR/kulli_alanlar(3) ·
    ALTIN+ALTIN_ORAN(2) · AKIS+QAKIS(2) · BRAVYI_GOSSET_ALFA(2) ·
    ara(2) · iz(2) · Majorana temsili(2)
  GRADYAN/TÜREV MOTORU     : 6 (biri canlı: senet_egimi)
  QSVT İCRASI              : 2 (biri canlı: qudit.suz)
  STABILIZER TEMSİLİ       : 3 (biri yarı canlı: galois.Tableau)
  F.2-J LİSTESİNE EKLENECEK CANLI AŞKIN ÇAĞRI : 9
    kararname(np.fft+np.exp) · mukayese.nesnelestir(np.exp) ·
    mukayese.bargmann/hata_payi(np.angle/acos) · usul.gedik_bul(arccos) ·
    tenakuz.dislama_dizeyi(np.exp) · rust.rust_kilidi(math.exp×2) ·
    qudit.suz(np.cos/np.exp) · zirh.taahhude_yuzlestir(np.tanh) +
    zirh.zirh_kaybi(np.exp/log) · optimize.gaye_kos(np.tanh) ·
    zihin_durumu.donme(cos/sin -- EN SICAK) ·
    melekeler.talim_kademesi(np.exp) ·
    kuantum/eniyileme.tayf_araligi(eigvalsh×41) ·
    soyle(np.exp) · kulli_mizan.holonomi(math.acos)
  F.5 SESSİZ İKAME (çıplak except / `or 0` / sessiz katlama) : 17 yer
