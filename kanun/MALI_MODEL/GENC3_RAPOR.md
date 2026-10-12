# GENÇ SEYRİ MODELİ v3 -- F 3-I 296, 297

Kod: `genc3.py` (model), `genc3_duyarlilik.py` (küresel duyarlılık ve oran taraması). Çıktılar: `genc3_out.txt`, `genc3_duyarlilik_out.txt`.

## Girdi tablosu (kaynak durumu)

| Girdi | Değer | Durum | Yol |
| :-- | :-- | :-- | :-- |
| 15-24 nüfusu | 12 708 348 | veri | ADNKS 2025 (haber özeti; TÜİK tablosu açılmadı) |
| 15-17 / 18-19 / 20-22 / 23-24 payı | %30,3 / 20,4 / 29,2 / 20,1 | veri | aynı kaynak |
| 25-29 yıllık kohort | 1,35 milyon | varsayım | 15-24 ortalaması 1,27 milyon; eski kohortlar büyük diye yukarı seçildi, yoklanmadı |
| Örgün yükseköğretim | 3 714 449 (lisans 2 571 297, önlisans 1 143 152) | veri | YÖK/haber 2024-25 |
| Açıköğretim | 3 001 312 | veri | aynı |
| 18-24 örgün okuma oranı | %38 | **türetildi** | 3,34 milyon örgün (3,71 milyonun %90'ı 18-24 varsayımı) / 8,85 milyon |
| Yaşa göre üniversite payı | 18-22: %45, 23-24: %20 | **türetildi** | yukarıdaki %38'e ağırlıklı ortalamayla oturtuldu (kontrol: %37,8) |
| Ortaöğretim net okullaşma | %82,85 (düzeltilmiş %87,88); 16-17 yaş ~%66 | veri | MEB 2024-25, Eğitimİş |
| 16-17 yaş okuyan | %75 | **türetildi** | %66 ile %83 arası orta nokta |
| Lisans+ payı | 23-24: %15, 25-29: %35 | **türetildi** | örgün lisans 2,57 milyon / 4 yıl = 0,64 milyon mezun/yıl; kohort 1,3 milyon -> üst sınır %49; sıkıştırıldı. Hafıza: OECD 25-34 yükseköğretim ~%40 (yoklanmadı) |
| YKS 2025 | TYT 2 560 649; yerleşen 778 298; boş kontenjan 47 477 | veri | ÖSYM -- kapasite/doluluk çapraz kontrolü |
| LGS | 1,01 milyon başvuru (1,35 milyon iddiası çelişkili); puanlı okul yerleşme ~%20,5 (2024) | veri/uyuşmaz | haber özeti |
| Giriş (katılım) oranı | 16-22: 0 -> %2,5 doğrusal; 22-29: %5,6 | **türetildi** | F 266 eğrisi + F 269 oranları (resmî işsizin %60'ı, gayrıresmînin %20'si) x (işsiz payı ~%6 + gayrıresmî ~%10 varsayımı) |
| 1 yıllık girişim hayatta kalma | ~%75-78 (2023 kohortu) | veri (tüm girişimler) | TÜİK 2024 bülteni özeti; **mikro/gerçek kişi kırılımı bulunamadı** |
| GSS primi | %6 x brüt asgari = 1 981,80 TL/ay | veri | SGK 2026; kişi başı hane geliri 11 010 TL altında devlet öder |
| Gençlerde işsizlik | %15,3 (2025) | veri | TÜİK |
| NEET 15-24 | %22,9 (2024, Eurostat) | veri | BETAM |
| Sektör payı (mal/hizmet), gider oranları, faiz, tasarruf, aile desteği, rekabet, bölge talebi | bkz. VARSAYILAN | **varsayım, aralıkla tarandı** | genc3_duyarlilik.py |

## F 3-I 296 listesi ve v3'te karşılığı

| # | Kusur | v3 |
| :-- | :-- | :-- |
| A-1 | nüfus bileşimi uydurma | yaş, okul türü ve giriş oranı yukarıdaki tablodan türetildi |
| A-3 | kalibrasyon yok | b0, ilk yıl canlılığı hedefine (%75) bisection ile oturtuldu; hedef %50-85 taranır |
| A-4 | rejim çarpanları elle | kayıt dışı erişim (0,4-0,9) ve kayıp (0,08-0,20) taranır; kayıtlı rejimde erişim kısıtı yok (varsayım) |
| A-5, A-7, A-8 | aile desteği, beceri artışı, şok | aile ölçeği 0,5-1,3 taranır; beceri artışı ve şok sabit (taranmadı) |
| A-9 | iflas sonrası iş | sabit (taranmadı) |
| A-10 | segment sınırı | sabit: 2 asgari net (padişah söylemedi, Claude seçimi) |
| B-1 | kim girer | yaşa bağlı giriş ağırlığı |
| B-2 | rekabet | kapasite = 1/(1+kappa x z); z rejime bağlı; kappa 0-0,3 |
| B-3 | sağlık | GSS 1 981,80 TL/ay, 25 yaş altı öğrenci hariç, gelir eşiği taranır; emeklilik hakkı **modellenemedi** (değer biçilecek veri yok) |
| B-4 | stok/sermaye | mal işi payı 0,2-0,6, gerçek gider oranı mal 0,40-0,65, hizmet 0,10-0,25 |
| B-5 | borç faizi | aylık 0-%3 |
| B-6 | tüketim/tasarruf | tasarruf oranı 0,2-0,6; tüketim eşiği asgari net / 3 (F 259) |
| B-7 | enflasyon, dilim kayması | mevcut rejimde dilim kayması 0-%20/yıl |
| B-8 | kayıt dışı | kayıt dışı rejim ayrı sütun |
| B-9 | sahtekârlık | genç modelinde yok (ayrı simülasyonlarda) |
| B-10 | güven aralığı | 8 tohum, %95 aralık; 80 çekilişli küresel tarama |
| B-11 | yaş kullanılmıyor | yaş artık tipi ve giriş ağırlığını belirler |
| -- | il/bölge | `talep_bolge` ölçeği 0,6-1,1 taranır; il bazlı veri işlenmedi |
| -- | B2B doğrulayıcısız hizmette destek sıfır (Madde AD) | genç modeline girmedi |

## F 3-I 298 düzeltmesi (padişah: "sabit gider yoksa şirket niye batsın; hiç kapatmaz, kasasına girenle yemek yer")

Kusur (Claude'un): v3'ün ilk koşusunda (a) iflas eden gencin müşteri tabanı sıfırlanıyordu ve (b) uyuyan şirketin sabit primi/gideri **hiç işlemiyordu**. (b) mevcut kanunu lehine çarpıtıyordu: gerçekte 4/b primi ve sabit gider şirket uyurken de borç olarak işler.

Düzeltme (`dayanma=True`, `genc3.py`): iflas eden **kişi** dışarıda iş bulur (gig), **şirket açık kalır**, müşteri tabanı yalnız doğal kayıpla erir, yeni müşteri akışı çeyreğe iner; mevcut rejimde sabit prim ve gider uyku sırasında **ödenmemiş borç** olarak birikir (`sabit_borc`). Yeni ölçütler: `acik_firma` (72. ayda gelir getiren ve nakit açığında olmayan), `gecim72` (12 aylık ort. net ≥ net asgarinin 1/3'ü, F 3-I 259), `yarim72` (≥ 1/2), `bir72` (≥ 1).


## GÜNCEL SONUÇ: düz %13,5, ücretli çalışan modelde yok (F 3-I 299, 302)

`genc3.py` varsayılan oranı artık %13,5'tir (`duz_oran`). Genç modelinde ücretli çalışan yoktur (ajanlar geliri olmayan gençlerdir); Madde 1 (t) bu yüzden modeli değiştirmez. 8 tohum, N=2000, %95 aralık (`genc3_out.txt`):

| Ölçüt | Tarafsız | Mevcut kayıtlı | Mevcut kayıt dışı | **Teklif %13,5** |
| :-- | --: | --: | --: | --: |
| 12 ay canlılık (kalibre hedef) | 0,750 | 0,619 | 0,510 | 0,668 |
| 72. ayda şirket açık ve nakit açığında değil | 0,925 | 0,621 | 0,677 | **0,883** |
| Geçim eşiğini sürdürme (net asgarinin 1/3'ü), 72. ay | 0,890 | 0,586 | 0,555 | **0,805** |
| Net asgarinin yarısı | 0,821 | 0,348 | 0,346 | 0,658 |
| Net asgari | 0,716 | 0,259 | 0,229 | 0,493 |
| Kalıcı üst segment | 0,536 | 0,175 | 0,127 | 0,312 |
| Kalıcı alt (dip) | 0,263 | 0,735 | 0,743 | 0,474 |
| Yıkım (iflas yaşayan kişi) | 0,340 | 0,907 | 0,730 | 0,483 |
| Ödenmemiş sabit borç (TL, mevcut rejimde) | 0 | 423.594 | 0 | 0 |

Okunuş: teklif mevcut kayıtlı düzenden her ölçüde iyidir (80 çekilişin %97'sinde geçim, %100'ünde şirketin açık kalması ve yıkım); kayıt dışına göre %78-90'ında iyidir; tarafsız ölçüye (kanunsuz dünya) göre hâlâ geridedir (0,805 / 0,890). Oran taraması (`genc3_duyarlilik_out.txt` C): %10,5'ten %27'ye geçimi sürdüren oranı 0,820 → 0,731, dip oranı 0,443 → 0,589; yani oran artışı gence ödünç verir ama teklif %27'de bile kayıtlı mevcut düzenden (0,586) iyidir.
