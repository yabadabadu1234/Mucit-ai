# TERCÜME — Şâheserlerin Tam Metinlerinin Osmanlıcaya Nakli

Bu dizin, `saheserler/` defterinde (dal: `claude/project-thread-9mnlw4`) her saha için tespit edilen şâheserlerin **tam metinlerini** meşru nüshalarından bulup Osmanlıcaya tercüme etmek için açılmıştır.

## Kaideler

| # | Kaide | Kimin emri |
| :-- | :-- | :-- |
| 1 | **Düsturlarda harf yazılmaz, kelime yazılır.** Her kemmiyet mânâsını söyleyen bir kelimeyle adlandırılır: "ağırlık × ehemmiyet = dikkat" doğrudur, "a × b = c" yanlıştır. Aslın harfleri her eserin sonundaki **İsimler cedveli**nde, okuyanın aslıyla karşılaştırabilmesi için yalnız **adlarıyla** gösterilir. Hesap ameliyelerinin işaretleri (cem', tarh, zarb, taksim, kuvvet, tamâmî, mecmû', hâsıl-ı zarb, hadd) ve rakamlar kalır, zîrâ bunlar kemmiyet değil fiil ve adettir. | Padişah, 1 Teşrîn-i sânî 2026 |
| 2 | Tam metin tercümesi **yalnız telifi düşmüş yahut açık lisanslı** eserlerde yapılır. Telifli eserin tam metni depoya konmaz; yalnız künyesi, meşru nüshasının yeri ve telif hâli deftere yazılır. | Coordinator notu, Padişahın talebi üzerine |
| 3 | Metin cümle cümle, atlamadan ve ilâve etmeden nakledilir. Mütercimin her sözü metnin dışında, numaralı **Mütercim kayıtları**nda durur ve hangi hükmün aslından, hangisinin mütercimin bilgisinden olduğunu söyler. | Padişahın tercihleri: dürüstlük, seçmece yapmamak |
| 4 | Istılahlarda esas, aynı depodaki `lugat/` dizinidir (dal: `claude/project-thread-jvwo8g`). Orada bulunmayan karşılık **teklif** diye işaretlenir; uydurma bir "eski karşılık" diye sunulmaz. | Coordinator notu |
| 5 | Osmanlıca, edebî ve öğretici üslûp; Latin harfleriyle, uzun sesliler şapkalı (â, î, û), izafetler kesreli. **Kısaltma kullanılmaz**; aslında kısaltma varsa açılarak yazılır. | Padişahın tercihleri |
| 6 | Kaynak dosyalar `grep` ile taranmaz, baştan sona okunur. | Padişahın tercihleri |

## Telifin tayini

Bir eser şu iki şartın **ikisi birden** tutuyorsa "umuma açık" sayılır ve tam tercümesi yapılır:

1. **Müellifin vefatından 70 yıl geçmiş olmak** (Türkiye'de Fikir ve Sanat Eserleri Kanunu ile Avrupa memleketlerinin kaidesi). 2026 yılı itibarıyla: müellif 1955 yahut daha evvel vefat etmiş olmalıdır.
2. **Amerika'da 1930 yahut daha evvel neşredilmiş olmak** (orada 95 yıllık neşir müddeti; 1 Kânûn-ı sânî 2026'da 1930 neşirleri umuma açılmıştır).

İki şarttan yalnız biri tutuyorsa defterde **karışık** diye yazılır ve tercümeye girişilmeden evvel Padişaha sorulur. Eski bir aslın **sonraki bir mütercim tarafından yapılmış tercümesi** ayrı bir eserdir; onun telifi o mütercimin vefatına göre hesaplanır. Bu hesapların hepsi mütercimin bilgisinden yapılmıştır ve hukukî bir fetvâ değildir.

Açık lisanslı eserler (meselâ *Creative Commons Atıf-Aynı Lisansla Paylaş* lisanslı olanlar) lisansın şartlarına uyulmak kaydıyla tercüme edilir; tercüme de aynı lisansla neşredilir.

## Dosya düzeni

| Yol | Muhteva |
| :-- | :-- |
| `DEFTER.md` | İlerleme defteri: şâheserler defterindeki her eserin telif hâli, meşru nüshası ve tercüme durumu. |
| `eserler/SS_muellif_yil_unvan.md` | Tamamlanmış yahut süren tercümeler; `SS`, Riyâziyyât Mevzû Tasnîfi 2020 sahasının numarasıdır. |

## Her tercümenin şekli

1. Künye, kullanılan nüsha ve adresi, telif hâli.
2. Tercüme metni.
3. Mütercim kayıtları.
4. İsimler cedveli (düsturlardaki kelimeler ve aslın işaretlerinin adları).
5. Istılah cedveli (lügatteki dayanağıyla).
