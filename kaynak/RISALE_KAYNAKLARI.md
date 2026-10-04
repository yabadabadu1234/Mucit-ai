# İslâm İspat Risâlesi Kaynak Listesi — Bulunanlar, Bulunamayanlar, Fihrist Mührü

- Tarih: 3 Ekim 2026
- Liste: kullanıcının verdiği "İslâm İspat Risâlesi için metodolojik ve kapsamlı kaynak okuma listesi" (10 aşama, ek olarak Molla Sadrâ el-Meşâir ve Şâtıbî el-Muvâfakât).
- Yöntem: Şâmile/Turath veri dosyaları (`files.turath.io/data-v4.sqlite` kataloğu, 8609 kitap; kitap metni `books-v3/<ID>.json`). Metin gerçek metindir, OCR değildir (CLAUDE.md 3-A 25-E). OCR veya taranmış PDF depoya alınmadı.
- Okuma: her eserin **yalnız fihristi** baştan sona okundu ve eserin klasöründeki `FIHRIST_MUHUR.md`'ye mühürlendi. Hiçbir eserin metni okunmadı; `metin.txt` dosyaları depoda durur.

## 1. Bulunan ve depoya konan: 12 eser

| Aşama | Eser | Klasör | Turath ID | Fihrist başlığı | Sayfa | metin.txt |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 2 | Râzî, Mefâtîhu'l-Ğayb (et-Tefsîru'l-Kebîr) | `razi_tefsir_kebir` | 23635 | 3768 | 6230 | 48,6 MB |
| 2 | Cürcânî, et-Ta'rîfât | `curcani_tarifat` | 7312 | 31 | 257 | 0,5 MB |
| 6 | Mâtürîdî, Kitâbü't-Tevhîd | `maturidi_kitabu_t_tevhid` | 6365 | 73 | 399 | 1,2 MB |
| 6 | Mâtürîdî, Te'vîlâtü Ehli's-Sünne (Te'vîlâtü'l-Kur'ân) | `maturidi_tevilat_ehl_i_sunne` | 95590 | 6257 | 5990 | 17,3 MB |
| 6 | Gazâlî, Tehâfütü'l-Felâsife | `gazali_tehafut_el_felasife` | 11055 | 580 | 216 | 0,5 MB |
| 6 | Gazâlî, el-İktisâd fi'l-İ'tikâd | `gazali_iktisad` | 9217 | 66 | 128 | 0,4 MB |
| 6 | Gazâlî, Mi'yârü'l-İlm | `gazali_miyar_el_ilm` | 26575 | 123 | 286 | 0,5 MB |
| 6 | Gazâlî, Mihakkü'n-Nazar | `gazali_mihakk_en_nazar` | 26538 | 48 | 77 | 0,3 MB |
| 6 | İbn Rüşd, Faslü'l-Makâl | `ibn_rushd_faslu_l_makal` | 12727 | 25 | 53 | 0,1 MB |
| 6 | İbn Teymiyye, Derü Te'ârudi'l-Akl ve'n-Nakl | `ibn_teymiyye_derr_teareuz` | 21506 | 1088 | 4031 | 6,5 MB |
| 6 | İbn Teymiyye, er-Redd ale'l-Mantıkıyyîn | `ibn_teymiyye_redd_mantikiyyin` | 7626 | 5 | 546 | 1,3 MB |
| ek | Şâtıbî, el-Muvâfakât | `satibi_muvafakat` | 11435 | 117 | 3211 | 9,7 MB |

Önceki turdan: Râzî, el-Metâlibü'l-Âliye (`razi_metalibul_aliye`, gerçek metin ve ayrı harita).

Her mührün içeriği: künye, okunan ve okunmayan sayıları, sayfa sırası denetimi, fihristin yapısı (tercümeler bana aittir), fihristteki kusurlar, Risâle ile alâka katmanı. Toplam fihrist satırı: 12.181.

### Mühürlerde işaretlenen fihrist kusurlarının özeti

- Te'vîlât: 113 sûre seviye 1'de görünür, القصص seviye 2'ye düşmüştür; âyet numaralamasında 225 boşluk, 20 tekrar, 5 geriye gidiş.
- Tefsîr-i Kebîr: âyet blokları sûre içinde boşluksuz ve çakışmasız (3414 blok, 114 sûre); Bakara 258–259 bloğu seviye 2; cüz 5'te 7. hüküm fihristte yok.
- Mi'yâr: fihrist 17. sayfadan başlar; 1–16. sayfa için satır yoktur.
- Redd: fihristte 5 satır; 4. makam 247. sayfadan eserin sonuna (300 sayfa) tek başlıktır.
- Tehâfüt: hâtimedeki mesele sayıları (1, 13, 17) fihristteki sıra ile uyuşmuyor; sebep metinden belirlenmedi.
- Der': "vecih 5" üç kez art arda; birkaç yazım hatası.

## 2. Gerçek metni bulunamayıp OCR olarak alınanlar (4 Ekim 2026)

Kullanıcı kararı: telif sorun değildir (kişisel araştırma, yeniden neşir yok); düz metin yoksa PDF yerine, okunması kolay olan OCR metni alınır. Kaynak: archive.org, yalnız indirmeye açık kayıtlar; ödünç-yalnız kayıtlar ve gölge kütüphaneler kullanılmadı. Her klasörde `ocr/` altında OCR metin dosyaları ve `KUNYE.md` (kayıt adresi, dosya listesi, Arapça kelime tanıma oranı) vardır. Başlık eşleşmesi kaydın üst bilgisine dayanır; içerik sayfa sayfa doğrulanmadı.

| Aşama | Eser | Klasör | Kalite notu |
| :-- | :-- | :-- | :-- |
| 2 | Râzî, Mebâhis-i Meşrikıyye | `razi_mebahis_musrikiyye` | iyi (%88–89); iki cilt, her biri iki kopya |
| 2 | Râzî, Muhassal | `razi_muhassal` | ağır bozuk (%36), 1905 baskısı |
| 2 | Râzî, el-Erbaîn fî Usûli'd-Dîn | `razi_erbain_usulid_din` | iyi (%83–87), 2 cilt |
| 2 | Urmevî, Lübâbü'l-Erbaîn (Der'de anılır) | `urmevi_lubab_erbain` | ölçülmedi (kaydedildi) |
| 2 | Teftâzânî, Şerhu'l-Makâsıd | `teftazani_serhu_makasid` | 6 dosya, kalite KUNYE'de |
| 2 | Teftâzânî, Şerhu'l-Akâid (+ Hayâlî hâşiyesi ayrı klasörde) | `teftazani_serhu_akaid`, `hayali_hasiye_serhul_akaid` | Hayâlî hâşiyesi ağır bozuk (%32) |
| 2 | Teftâzânî, Tehzîbü'l-Mantık | `teftazani_tehzib_mantik` | küçük metin |
| 2 | Cürcânî, Şerhu'l-Mevâkıf | `curcani_serhu_mevakif` | Dârü'l-Kütübi'l-İlmiyye 8 cilt iyi (%88–92); Bulak baskıları kötü (%46–52); karışık sürümler ve kopyalar var |
| 6 | Abdülcebbâr, el-Muğnî | `abdulcebbar_mugni` | 16 cilt dosyası, %70–82 (cilt 1–3, 10, 18–19 yok) |
| 6 | Abdülcebbâr, Şerhu Usûli'l-Hamse | `abdulcebbar_usul_hamse_serhi` | iyi (%81) |
| 6 | Gazâlî, el-Kıstâsü'l-Müstakîm | `gazali_kistas` | %77 |
| 6 | İbn Rüşd, el-Keşf an Menâhici'l-Edille | `ibn_rushd_kesf_menahic` | %89 ve %65 iki nüsha |
| 4 | Ali Kuşçu/Devvânî/Tûsî çevresi: Tecrîd şerhleri | `tecrid_serhleri` | Hillî Keşfü'l-Murâd ağır bozuk (%33); diğer ikisi ölçüldü |
| 5 | Devvânî, Şevâkilü'l-Hûr | `devvani_sevakil_hur` | iyi (%80) |
| 4 | Fenârî, Aynü'l-A'yân | `fenari_ayn_ul_ayan` | bozuk (%41) |
| 5 | İbn Kemâl: Risâleler külliyatı, Tehâfüt hâşiyesi (Kemalpaşazade) | `ibn_kemal_risaleler` | Arapça risâleler %71–80; hâşiye Türkçe/Latin harfli |
| 6 | Hızır Bey Nûniyye, Hayâlî şerhi | `hizir_bey_nuniyye_hayali_serhi` | iyi (%90) |
| 7 | İbn Sînâ, el-İşârât ve't-Tenbîhât | `ibn_sina_isarat` | 3 nüsha: %85, %61, 1893 baskısı bozuk |
| 7 | Tûsî, Şerhu'l-İşârât | `tusi_serhu_isarat` | 3 dosya, KUNYE'de |
| 7 | İbn Sînâ, eş-Şifâ (İlâhiyyât ve diğer bölümler) | `ibn_sina_sifa` | 14 dosya %60–75 + 1 gerçek metin dosyası (`versed--dea294ef`, %96) |
| 7 | İbn Sînâ, en-Necât | `ibn_sina_necat` | iyi (%90) |
| 9 | Molla Sadrâ, el-Hikmetü'l-Müteâliye, cilt 1–9 | `sadra_hikmet_mutealiye` | %52–67, ağır gürültülü |
| 9 | Molla Sadrâ, el-Meşâir | `sadra_mesair` | %87 |
| 1 | Said Nursî: Sözler, Lem'alar, Mektûbât, Şuâlar, Muhâkemât, İşârâtü'l-İ'câz | `nursi_risale_i_nur` | Latin harfli; ölçülmedi |
| 1 | Elmalılı, Hak Dini Kur'an Dili (10 cilt tek dosya) | `elmalili_hak_dini_kuran_dili` | Latin harfli; 12,9 MB, eksiksiz olup olmadığı doğrulanmadı |
| 8 | Craig (Kalâm cilt 1–2, Blackwell Companion) | `craig_kalam_ve_dogal_teoloji` | İngilizce OCR |
| 8 | Plantinga (Warranted Christian Belief, Nature of Necessity, Warrant and Proper Function) | `plantinga` | İngilizce OCR |
| 8 | Feser (Five Proofs, The Last Superstition) | `feser` | İngilizce OCR |
| 9 | Attas (Prolegomena, Islam and Secularism) | `attas` | İngilizce OCR |
| 9 | Izutsu, God and Man in the Koran | `izutsu_god_and_man` | İngilizce OCR |

## 3. Hâlâ bulunamayanlar

archive.org'da ad yoklamasıyla çıkmadı veya çıkan kayıt başka eserdi:
- Râzî, Risâle fi'n-Nübüvvât.
- Taşköprizâde: el-Âdâb, Risâle fî Tahkîki'l-Külliyyât, Mevzûâtü'l-Ulûm. Gelenbevî: el-Burhân, İsbâtü'l-Vâcib, Risâletü'l-İmkân, Hasînetü'l-Mîzân (yalnız Osman Kurt'un Tehzîb çalışmasının sayfa denklik tablosu ve "Resâilü'l-İmtihân" çıktı; alınmadı).
- Hocazâde: Tehâfüt, Hâşiye ale't-Tecrîd. Ali Tûsî: ez-Zehîra. Fenârî: Misbâhü'l-Üns. Ali Kuşçu: Şerhu'l-Cedîd, Risâle fî Vaz'i'l-İstitâa (`srhldedtjred` kaydı adına göre Şerhu'l-Cedîd olabilir, içeriği doğrulanmadığından alınmadı).
- İbn Kemâl'in listede adı geçen beş risâlesi: külliyat içinde olup olmadıkları doğrulanmadı.
- Devvânî, İsbâtü'l-Vâcib (Kadîme/Cedîde).
- Harputlu İshak: Zübdetü'l-Kelâm, Ziyâü'l-Kulûb. Sırrı Paşa: Arâü'l-Milel, Akâid-i Diniyye Şerhi.
- İzmirli: Yeni İlm-i Kelâm, Mi'yârü'l-Ulûm, Muhassalü'l-Kelâm. Elmalılı: Metâlib ve Mezâhib.
- Filibeli Ahmed Hilmi: Huzûr-ı Akl u Fende Maddiyyûn, Allah'ı İnkâr Mümkün müdür. Mehmed Ali Ayni: Reybiyyet.
- Molla Sadrâ: el-Mesâilü'l-Kudsiyye. Nasîrüddîn Tûsî: Tecrîdü'l-İ'tikâd'ın kendisi (yalnız Hillî şerhi alındı).
- Izutsu, Creation and the Timeless Order of Things.

Osmanlıca ve Türkçe eserler için yalnız archive.org arandı; başka dijital kütüphaneler bu turda taranmadı. Kaynak adresi verilirse alınır.

Katalogda olup listede olmayan ve alınmayanlar: İbn Teymiyye, en-Nübüvvât (Turath id 11817); Râzî, Meâlimü Usûli'd-Dîn (6372) ve İ'tikâdât Fıraki'l-Müslimîn (6516), Âmidî, Gâyetü'l-Merâm (6364), Abdülcebbâr, Tesbîtü Delâili'n-Nübüvve (9789). Bunlar gerçek metindir; istenirse eklenir.

## 4. Okuma durumu (toplu)

Fihrist okundu: yalnız 12 gerçek-metin eserde (12.181 satır). OCR eserlerin fihristi ve metni okunmadı. Metin okundu: 0 eser.
