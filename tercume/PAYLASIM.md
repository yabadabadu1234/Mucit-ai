# Paylaştırma Defteri

**Esas dal: `claude/project-thread-y2govz`.** Bütün tercümanlar bu defteri bu dalda okur. Kendi dalında çalışan tercüman, bir esere başlamadan evvel o eseri bu defterde kendi adına görmelidir; görmüyorsa esas dalın tercümanına (birinci tercüman) haber verir, o yazar.

Eserlerin telif hâli ve nüshaları için: [DEFTER.md](DEFTER.md). Tercümenin kaideleri için: [README.md](README.md). Şerh, hâşiye ve mütercim kaydı yazılmaz.

## Hâl işaretleri

| İşaret | Mânâsı |
| :-- | :-- |
| **Sürüyor** | Tercüman şu an bu eserde çalışıyor. |
| **Sırada** | Tercüman bu eseri mevcut işinden sonra alacak; başkası almaz. |
| **Tamam** | Tercüme bitti; dosyası esas dala alındı. |

## Tercümanlar

| Tercüman | İş parçacığı | Dal |
| :-- | :-- | :-- |
| Birinci | Şaheserlerin tam metnini Osmanlıcaya tercüme etmek | `claude/project-thread-y2govz` (esas dal) |
| İkinci | Şaheserleri tercüme etmek, ikinci tercüman | `claude/project-thread-d9cec2` |
| Üçüncü | Şaheserleri tercüme etmek, üçüncü tercüman | `claude/project-thread-41r6m8` |
| Dördüncü | Şaheserleri tercüme etmek, dördüncü tercüman | `claude/project-thread-njf2rt` |

## Paylaştırma

| Saha | Eser | Tercüman | Hâl | Dosya |
| :-- | :-- | :-- | :-- | :-- |
| 11 | Riemann 1859, *Ueber die Anzahl der Primzahlen* | Birinci | Tamam | `eserler/11_riemann_1859_adad_i_evveliyye.md` |
| 05 | Euler 1741, *Solutio problematis ad geometriam situs pertinentis* | Birinci | Tamam | `eserler/05_euler_1741_konigsberg_kopruleri.md` |
| 00 | Hilbert 1900, *Mathematische Probleme* | Birinci | Tamam | `eserler/00_hilbert_1900_riyazi_meseleler.md` |
| 01 | Hârizmî, *el-Cebr ve'l-Mukābele* | Birinci | Tamam | `eserler/01_harizmi_cebr_ve_mukabele.md` |
| 15 | Hüseyin Tevfik Paşa 1882, *Linear Algebra* | Birinci | Durdu (birinci bab müsvedde; Padişahın yeni zaviyesi üzerine güncel esere geçildi) | `eserler/15_tevfik_1882_cebr_i_hatti.md` |
| 53 | Riemann 1854, *Über die Hypothesen, welche der Geometrie zu Grunde liegen* | İkinci | Tamam | `eserler/53_riemann_1854_hendesenin_esasi_olan_faraziyeler.md` |
| 26 | Dedekind 1872, *Stetigkeit und irrationale Zahlen* | İkinci | Sürüyor | `eserler/26_dedekind_1872_sureklilik_ve_gayri_muntazam_adedler.md` |
| 45 | Abel 1826, *Auflösung einer mechanischen Aufgabe* | Üçüncü | Tamam | `eserler/45_abel_1826_bir_mekanik_meselenin_halli.md` |
| 26 | Leibniz 1684, *Nova methodus pro maximis et minimis* | Üçüncü | Sürüyor | |
| 41 | Weierstrass 1885, *Über die analytische Darstellbarkeit sogenannter willkürlicher Functionen* | Üçüncü | Düştü (klasik; README kaide 7) | |
| 62 | Bayes 1763, *An Essay towards solving a Problem in the Doctrine of Chances* | Dördüncü | Sürüyor | `eserler/60_bayes_1763_…` |
| 62 | Gosset ("Student") 1908, *The Probable Error of a Mean* | Dördüncü | Düştü (klasik; README kaide 7) | |

## Güncel şâheserler (Padişahın 1 Teşrîn-i sânî 2026 emri: yalnız modern ve açık lisanslı eserler)

### Univalent Foundations Program, *Homotopy Type Theory: Univalent Foundations of Mathematics*, 2013

Lisans: Creative Commons Atıf-Aynı Lisansla Paylaş 3.0 (deponun `README.md` dosyasından yoklandı). Tercüme de aynı lisansla neşredilir. Kaynak: <https://github.com/HoTT/book> (LaTeX asıl; her bab ayrı bir `.tex` dosyasıdır). Bu eser, Mucit-AI'ın kalbindeki kübik tip nazariyesi çekirdeğinin dayandığı nazariyenin ana kitabıdır.

| Bab | Asıl dosya | Satır | Tercüman | Hâl | Dosya |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Önsöz ve Medhal | `preface.tex`, `introduction.tex` | 613 | Birinci | Sürüyor | `eserler/03_hott_2013_00_onsoz_ve_medhal.md` |
| 1. Tip nazariyesi | `preliminaries.tex` | 2044 | Birinci | Sırada | `eserler/03_hott_2013_01_tip_nazariyesi.md` |
| 2. Homotopi tip nazariyesi | `basics.tex` | 2699 | Birinci | Sırada | `eserler/03_hott_2013_02_homotopi_tip_nazariyesi.md` |
| 3. Mecmûalar ve mantık | `logic.tex` | 1278 | İkinci | Sırada (Dedekind'den sonra) | `eserler/03_hott_2013_03_mecmualar_ve_mantik.md` |
| 4. Müsâvîlikler | `equivalences.tex` | 1118 | İkinci | Sırada | `eserler/03_hott_2013_04_musavilikler.md` |
| 5. İstikrâ | `induction.tex` | 1402 | İkinci | Sırada | `eserler/03_hott_2013_05_istikra.md` |
| 6. Yüksek istikrâî tipler | `hits.tex` | 2192 | Üçüncü | Sırada (Leibniz'den sonra) | `eserler/03_hott_2013_06_yuksek_istikrai_tipler.md` |
| 7. Homotopi buud-sayısı tipleri | `hlevels.tex` | 2139 | Üçüncü | Sırada | `eserler/03_hott_2013_07_homotopi_tipleri.md` |
| 8. Homotopi nazariyesi | `homotopy.tex` | 2892 | Dördüncü | Sırada (Bayes'ten sonra) | `eserler/03_hott_2013_08_homotopi_nazariyesi.md` |
| 9. Makûleler nazariyesi | `categories.tex` | 1854 | Dördüncü | Sırada | `eserler/03_hott_2013_09_makuleler_nazariyesi.md` |
| 10. Mecmûalar nazariyesi | `setmath.tex` | 1970 | — | Boşta | |
| 11. Hakîkî adetler | `reals.tex` | 3301 | — | Boşta | |
| Zeyl: Sûrî tip nazariyesi | `formal.tex` | 1259 | — | Boşta | |

Istılahların birliği için: bir babda ilk defa karar verilen karşılık, o babın İsimler cedveline yazılır; sonraki bablar evvelki babların cedvellerine bakar. Bab adları burada muvakkattir; tercüman lügate göre düzeltebilir.

## Boştaki eserler

Klasik eser artık dağıtılmaz (README kaide 7). Elindeki klasik eseri bitirmek üzere olan tercüman bitirir; henüz başlanmamış klasik eserler ("Sırada" yazılı olanlar) düşer. Güncel şâheserler defteri yenilendikçe açık lisanslı eserler bu bölüğe eklenir. **Karışık** eserlere Padişaha sorulmadan başlanmaz.
