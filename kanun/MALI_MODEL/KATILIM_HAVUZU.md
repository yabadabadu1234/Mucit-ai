# KATILIM HAVUZU -- YAŞ SINIFLARINA GÖRE (F 3-I 260)

Kaynak: ILO ILOSTAT, Türkiye, 2025, TÜİK Hanehalkı İşgücü Araştırması (BA:622) verisi; ham dosyalar `veri_ilo/`, hesap `havuz.py`, çıktı `havuz_out.txt`. Rakamlar bin kişidir. Yaş sınıfları ILO'nun 10 yıllık bantlarıdır.

## Hüküm ve okuma
- Padişah: geliri olmayan herkes lazım; modele katılabilecek sayı; halinden memnun maaşlıları çıkar; kayıt dışılar namzet.
- Çıkarım (padişahın sözü değil): "çıkartmamamız" yazım hatası kabul edildi, **çıkarma** okundu. Hesap iki okumayı da verir (`havuz` çıkarılmış, `havuz_memnun_dusulmeden` çıkarılmamış).
- Havuz = işgücü dışı + işsiz + **kayıt dışı çalışan** + (1−m)·kayıtlı çalışan. m = halinden memnun kayıtlı çalışan payı.

## Bulgular (2025, bin kişi)
| Yaş | Nüfus (16+) | Kayıtlı çalışan | Kayıt dışı çalışan | İşsiz (TÜİK) | İşgücü dışı | Gelirsiz (işsiz+dışı) | Kayıt dışı oranı |
| :-- | --: | --: | --: | --: | --: | --: | --: |
| 15-24 | 10 266 | 3 229 | 1 409 | 840 | 4 789 | 5 629 | %30,4 |
| 25-34 | 12 610 | 6 906 | 1 197 | 912 | 3 594 | 4 506 | %14,8 |
| 35-44 | 12 671 | 6 970 | 1 520 | 598 | 3 583 | 4 181 | %17,9 |
| 45-54 | 11 480 | 4 834 | 1 956 | 393 | 4 296 | 4 689 | %28,8 |
| 55-64 | 8 846 | 1 701 | 1 682 | 190 | 5 273 | 5 462 | %49,7 |
| 65+ | 9 284 | 266 | 895 | 35 | 8 088 | 8 123 | %77,1 |

Havuz (m değerine göre; 65+ işgücü dışı emekli sayılıp çıkarıldı):
| m | 15-24 | 25-34 | 35-44 | 45-54 | 55-64 | 65+ | Toplam | 16-34 |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: |
| 1,0 (hiçbir kayıtlı çalışan arayışta değil) | 7 038 | 5 703 | 5 701 | 6 645 | 7 144 | 930 | 33 161 | 12 741 |
| 0,7 | 8 006 | 7 775 | 7 792 | 8 096 | 7 655 | 1 010 | 40 333 | 15 781 |
| 0,5 | 8 652 | 9 156 | 9 186 | 9 062 | 7 995 | 1 063 | 45 115 | 17 808 |

Ek sayı: ILO'nun NEET'i (15-24, ne çalışıyor ne eğitimde) 2 684 bin; aynı yaşta işgücü dışı 6 028 bin, yani işgücü dışının büyük kısmı eğitimdedir.

## Sınırlar (yoklanamayanlar -- sayıyla)
1. **m (memnun kayıtlı çalışan payı) için doğrulanmış veri bulunamadı.** İki arama (SGK prime esas kazanç dağılımı, asgari ücret altı oranı) yalnızca asgari ücret ve prim parametrelerini verdi. m = 1, 0,7, 0,5 **varsayımdır**; ölçülmedi. Aranacak kaynak: SGK istatistik yıllığı prime esas kazanç dağılımı ve TÜİK Kazanç Yapısı Araştırması.
2. **"Gelirsiz" = işgücü dışı + işsiz bir vekildir.** İşgücü dışındakilerin bir kısmı aileden, emeklilikten veya kiradan gelir alır; bu pay yoklanamadı. Dolayısıyla "geliri olmayan" sayısı üst sınırdır.
3. **Kayıt dışı = ILO bilgi tanımıdır** (kayıtsız çalışan, tarım ve ücretsiz aile işçisi dâhil). 55-64 ve 65+ yüksek oranlar büyük ölçüde tarımdan gelir; hepsi mikro mükellefiyet namzedi değildir. Tarım payı yaş sınıfına göre ayrılmadı.
4. **15 yaş çıkarımı:** 15 yaşındakiler (yaklaşık 1 239 bin; 2010 doğum sayısından çıkarım, kaynak burada yoklanmadı) 15-24 işgücü dışından düşüldü. Nüfus projeksiyonu ilave edilmedi.
5. **Eğitim × yaş (okuyor/okumuyor) tablosu bulunamadı**; yaş sınıfı içinde okuyanların payı yalnız NEET toplamından dolaylı görülür.
6. İşgücü dışındakilerin "katılabilirliği" (bakım yükü, engellilik) ölçülmedi; havuz katılabilecek **namzet** sayısıdır, katılacak sayısı değildir.

## Modele etkisi
Genç seyri modelinin (`genc2.py`) tip payları (okuyor-lise %15, okuyor-üniversite %20, okumuyor lise altı %20, lise %25, lisans+ %20) varsayımdı; bu havuz 15-34 için 12,7 / 15,8 / 17,8 milyon namzet verir (m'ye göre). Kayıt dışı çalışan genç namzetleri (15-34: 2 606 bin) modele ayrı tip olarak girmelidir; bu ekleme henüz yapılmadı.
