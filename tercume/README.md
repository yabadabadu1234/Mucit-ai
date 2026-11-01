# TERCÜME — Şâheserlerin Tam Metinlerinin Osmanlıcaya Nakli

Bu dizin, `saheserler/` defterinde (dal: `claude/project-thread-9mnlw4`) her saha için tespit edilen şâheserlerin **tam metinlerini** meşru nüshalarından bulup Osmanlıcaya tercüme etmek için açılmıştır.

## Kaideler

| # | Kaide | Kimin emri |
| :-- | :-- | :-- |
| 1 | **Düsturlarda harf yazılmaz, kelime yazılır.** Her kemmiyet mânâsını söyleyen bir kelimeyle adlandırılır: "ağırlık × ehemmiyet = dikkat" doğrudur, "a × b = c" yanlıştır. Aslın harfleri her eserin sonundaki **İsimler cedveli**nde, okuyanın aslıyla karşılaştırabilmesi için yalnız **adlarıyla** gösterilir. Hesap ameliyelerinin işaretleri (cem', tarh, zarb, taksim, kuvvet, tamâmî, mecmû', hâsıl-ı zarb, hadd) ve rakamlar kalır, zîrâ bunlar kemmiyet değil fiil ve adettir. | Padişah, 1 Teşrîn-i sânî 2026 |
| 2 | Tercümeler Padişahın **şahsî istifadesi** içindir, neşir için değildir. İnternette PDF'i yahut tam metni bulunan her eser, **telifine bakılmaksızın** tercüme edilir. Telifli eserlerin tercümeleri depoya konmaz; projenin paylaşılan klasöründe `/mnt/project-files/tercume_sahsi/` altına yazılır. Telifi düşmüş yahut açık lisanslı eserlerin tercümeleri eskisi gibi depoda `eserler/` altında durur. Asıl metin, müellifin sahifesi, arXiv, nâşirin açık sahifesi, üniversite ders sahifesi gibi yerlerden alınır; Padişahın kendisi bir PDF yükler yahut paylaşılan klasöre koyarsa, kaynağına bakılmadan tercüme sırasına alınır. *Nakz:* bu kaidenin evvelki şekli telifli eserin tercümesini yasaklardı; Padişahın 1 Teşrîn-i sânî 2026 tarihli emriyle kalktı. | Padişah, 1 Teşrîn-i sânî 2026 |
| 3 | Metin cümle cümle, atlamadan ve ilâve etmeden nakledilir. **Şerh, hâşiye, mütercim kaydı ve metin içi izah yazılmaz**; emek şerhe değil, eşzamanlı çalışan çok tercümana verilir. *Nakz:* bu kaidenin evvelki şekli "Mütercim kayıtları" isterdi; Padişahın 1 Teşrîn-i sânî 2026 tarihli emriyle kalktı. | Padişah, 1 Teşrîn-i sânî 2026 |
| 4 | Istılahlarda esas, aynı depodaki `lugat/` dizinidir (dal: `claude/project-thread-jvwo8g`). Orada bulunmayan karşılık **teklif** diye işaretlenir; uydurma bir "eski karşılık" diye sunulmaz. | Coordinator notu |
| 5 | Osmanlıca, edebî ve öğretici üslûp; Latin harfleriyle, uzun sesliler şapkalı (â, î, û), izafetler kesreli. **Kısaltma kullanılmaz**; aslında kısaltma varsa açılarak yazılır. | Padişahın tercihleri |
| 6 | Kaynak dosyalar `grep` ile taranmaz, baştan sona okunur. | Padişahın tercihleri |
| 7 | **Şâheser, en modern ve en güncel eserlerin en şâheseridir**, klasik eser değildir. Bundan sonra paylaştırmaya yalnız güncel eserler konur; klasik eser dağıtılmaz. Lisanslı eserin tercümesi aynı lisansla neşredilir ve künyede müellifler ile lisans adıyla gösterilir. | Padişah, 1 Teşrîn-i sânî 2026 |

## Telifin tayini

Bir eser şu iki şartın **ikisi birden** tutuyorsa "umuma açık" sayılır ve tam tercümesi yapılır:

1. **Müellifin vefatından 70 yıl geçmiş olmak** (Türkiye'de Fikir ve Sanat Eserleri Kanunu ile Avrupa memleketlerinin kaidesi). 2026 yılı itibarıyla: müellif 1955 yahut daha evvel vefat etmiş olmalıdır.
2. **Amerika'da 1930 yahut daha evvel neşredilmiş olmak** (orada 95 yıllık neşir müddeti; 1 Kânûn-ı sânî 2026'da 1930 neşirleri umuma açılmıştır).

İki şarttan yalnız biri tutuyorsa defterde **karışık** diye yazılır ve tercümeye girişilmeden evvel Padişaha sorulur. Eski bir aslın **sonraki bir mütercim tarafından yapılmış tercümesi** ayrı bir eserdir; onun telifi o mütercimin vefatına göre hesaplanır. Bu hesapların hepsi mütercimin bilgisinden yapılmıştır ve hukukî bir fetvâ değildir.

Açık lisanslı eserler (meselâ *Creative Commons Atıf-Aynı Lisansla Paylaş* lisanslı olanlar) lisansın şartlarına uyulmak kaydıyla tercüme edilir; tercüme de aynı lisansla neşredilir.

## Dosya düzeni

| Yol | Muhteva |
| :-- | :-- |
| `PAYLASIM.md` | Eşzamanlı çalışan tercümanlar arasında eserlerin paylaştırma defteri; bir esere başlamadan evvel buraya yazılır. |
| `DEFTER.md` | İlerleme defteri: şâheserler defterindeki her eserin telif hâli, meşru nüshası ve tercüme durumu. |
| `eserler/SS_muellif_yil_unvan.md` | Tamamlanmış yahut süren tercümeler; `SS`, Riyâziyyât Mevzû Tasnîfi 2020 sahasının numarasıdır. |

## Her tercümenin şekli

1. Künye, kullanılan nüsha ve adresi, telif hâli.
2. Tercüme metni.
3. İsimler cedveli (düsturlardaki kelimeler ve aslın işaretlerinin adları).
