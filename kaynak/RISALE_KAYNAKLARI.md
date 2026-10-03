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

## 2. Listede olup bulunamayanlar

Aşağıdakiler Turath kataloğunda (8609 kitap) ad ve yazar yoklamasıyla bulunamadı. Başka dijital kütüphanelerde bulunabilirler; oralarda aranmadı.

| Aşama | Eser |
| :-- | :-- |
| 2 | Râzî: el-Mebâhisü'l-Meşrikıyye, el-Muhassal, el-Erbaîn fî Usûli'd-Dîn, Risâle fi'n-Nübüvvât. Teftâzânî: Şerhu'l-Makâsıd, Şerhu'l-Akâid, Tehzîbü'l-Mantık. Cürcânî: Şerhu'l-Mevâkıf |
| 3 | Taşköprizâde: el-Âdâb fî İlmi'l-Bahs, Risâle fî Tahkîki'l-Külliyyât, Mevzûâtü'l-Ulûm. Gelenbevî: el-Burhân, Risâle fî İsbâti'l-Vâcib, Risâletü'l-İmkân, Hasînetü'l-Mîzân |
| 4 | Hocazâde: Tehâfütü'l-Felâsife, el-Hâşiye ale't-Tecrîd. Ali Tûsî: ez-Zehîre. Molla Fenârî: Aynü'l-A'yân, Misbâhü'l-Üns. Ali Kuşçu: eş-Şerhu'l-Cedîd ale't-Tecrîd, Risâle fî Vaz'i'l-İstitâa |
| 5 | İbn Kemâl: altı risâle. Devvânî: Risâletü İsbâti'l-Vâcib (el-Kadîme ve el-Cedîde), Sevâkılü'l-Hûr |
| 6 | Hızır Bey: en-Nûniyye ve şerhi. Kâdî Abdülcebbâr: el-Muğnî, Şerhu Usûli'l-Hamse. Gazâlî: el-Kıstâsü'l-Müstakîm. İbn Rüşd: el-Keşf an Menâhici'l-Edille. Harputlu İshak: Zübdetü'l-Kelâm, Ziyâü'l-Kulûb. Giridli Sırrı Paşa: Arâü'l-Milel, Akâid-i Diniyye Şerhi |
| 7 | İbn Sînâ: el-İşârât ve't-Tenbîhât, eş-Şifâ: el-İlâhiyyât, en-Necât. Nasîrüddîn Tûsî: Şerhu'l-İşârât, Tecrîdü'l-İ'tikâd |
| 9 | Molla Sadrâ: el-Hikmetü'l-Müteâliye, el-Mesâilü'l-Kudsiyye |
| ek | Molla Sadrâ: el-Meşâir |

Yoklamada yakın ad çıkan ama listedeki eser olmayanlar (alınmadı): "آداب البحث والمناظرة" (id 266; yazarı Şinkîtî, Taşköprizâde değil), "القسطاس في علم العروض" (id 658; Gazâlî'nin el-Kıstâs'ı değil).

Katalogda olup listede olmayan, Risâle'nin nübüvvet faslına doğrudan değen bir eser: İbn Teymiyye, en-Nübüvvât (Turath id 11817). Kullanıcı isterse eklenir; kendiliğinden alınmadı.

## 3. Depoya konmayanlar ve sebebi

| Eser grubu | Durum |
| :-- | :-- |
| Craig, Plantinga, Feser (Aşama 8) | Telif korumalı modern İngilizce kitaplar; Turath'ta yok; depoya alınmadı |
| Attas, Izutsu (Aşama 9) | Telif korumalı modern kitaplar; Turath'ta yok; depoya alınmadı |
| İzmirli, Said Nursi, Elmalılı, Filibeli Ahmed Hilmi, Mehmed Ali Ayni (Aşama 1, 10) | Türkçe ve Osmanlıca eserler; Turath'ta bulunmaz. Wikisource denemesi hız sınırına (HTTP 429) takıldı ve bırakıldı; başka dijital metin kaynağı yoklanmadı. Gerçek metin (OCR değil) kaynağı bulunmadığı için bu turda alınmadı; yazarların bir kısmının eserleri kamu malı olduğundan sebep telif değildir, kaynak bulma işidir |

Açık iş: yukarıdaki üç grup için gerçek metin kaynağı kullanıcıdan veya yeni bir aramadan gelecektir.

## 4. Okuma durumu (toplu)

Fihrist okundu: 12/12 eser (12.181/12.181 satır). Metin okundu: 0/12 eser. Metin dosyaları depoda durur ve sonraki okuma bölüm bütünlüğüyle (CLAUDE.md 3-A 25-B) yapılacaktır.
