# TALEBE NOTLARI — Tercümelerden Damıtılmış Cevher

Bu dizin, `tercume/eserler/` altındaki Osmanlıca tam metin tercümelerinden **talebe notları** çıkarmak için açılmıştır. Gaye: toprağı süzüp cevheri ortaya çıkarmak; **hiçbir bilgiyi eksiltmeden**, malûmatı çok daha yoğun bir surette bir araya getirmek, sebep ile netice arasındaki illiyet bağını açıkça göstermek ve notu bir hedefe matuf kılmak.

## Kaideler

| # | Kaide | Kimin emri |
| :-- | :-- | :-- |
| 1 | Hiçbir bilgi eksiltilmez; en ince teferruat (künye, sahife, tarih, mütercim kaydı, tashih) dahi nota girer. | Padişah, 1 Teşrîn-i sânî 2026 |
| 2 | Her bab bir **illiyet zinciri**dir: her halka ⟹ ("bundan şu lâzım gelir") ve ⟸ ("çünkü") ile bir öncekine bağlanır; babın sonunda tek cümlelik **Cevher** durur. | Padişah, aynı gün |
| 3 | **Düsturlarda harf yazılmaz, kelime yazılır** ("ağırlık × ehemmiyet = dikkat"; "a × b = c" değil). Adlar tercümenin İsimler cedveliyle aynıdır; aslın harfleri yalnız sondaki cedvelde, adlarıyla görünür. | Padişah, aynı gün |
| 4 | Not sahibinin her ilâvesi **[N]** ile, mütercim kaydına atıf **[M…]** ile işaretlenir; hangi hükmün tercümeden, hangisinin not sahibinin bilgisinden olduğu daima ayırt edilir. Bilgiden emin olunmayan yerde bu açıkça yazılır. | Padişahın tercihleri: dürüstlük |
| 5 | Not, tercümeyi körü körüne tekrar etmez; tenkit eder. Tercümede yahut aslında bulunan sürçme, gizli şart ve ispatsız hüküm ayrı bir babda gösterilir. | Padişahın tercihleri: kendini tenkit |
| 6 | Her notun sonunda kendini yoklama sualleri ve adlar cedveli bulunur. | Talebe notunun gayesi |
| 7 | Istılahlarda esas `lugat/` dizinidir (dal: `claude/project-thread-jvwo8g`); kısaltma kullanılmaz; Osmanlıca, edebî ve öğretici üslûp. | Padişahın tercihleri |
| 8 | Kaynak dosyalar `grep` ile taranmaz, okunarak damıtılır. | Padişahın tercihleri |

## Defter

| Tercüme | Not | Hâl |
| :-- | :-- | :-- |
| Euler 1741, Königsberg köprüleri | [05_euler_1741_konigsberg_kopruleri_not.md](05_euler_1741_konigsberg_kopruleri_not.md) | Tamam (8 bab) |
| Riemann 1859, a'dâd-ı evveliyye | [11_riemann_1859_adad_i_evveliyye_not.md](11_riemann_1859_adad_i_evveliyye_not.md) | Tamam (16 bab ve iki ek) |
| Hilbert 1900, Riyâzî Meseleler | — | Tercümesi sürüyor (1–18. meseleler hazır); not tercüme bitince |

Yeni bir tercüme `tercume/DEFTER.md`de "Tamam" olunca notu bu dizine aynı adla, sonuna `_not` eklenerek yazılır.

## Tercümeye geri bildirilecek hususlar

Notları yazarken tercümede düzeltilmesi yahut yoklanması lâzım gelen yerler. Aşağıdaki üçü mütercime iletilmiş ve **üçü de** `claude/project-thread-y2govz` dalında 905dbab5 işlemesiyle **icra edilmiştir** (Euler yolu sahife resmiyle harf harf aynı çıkmıştır):

1. **Riemann, [M10]:** "logaritma Tekmîl-zeta(0) = − logaritma(2)" cümlesi yanlış anlaşılmaya müsaittir. Riemann'ın Tekmîl-zeta(0)'ı irtifâ sıfır, yâni mütehavvil ½ noktasındaki kıymettir ve takriben 0,497'dir. Sarîh düsturun doğru sâbiti − logaritma 2'dir; Riemann'ın yazdığı sâbit bundan çok az farklıdır ve bu fark Riemann'ın bir sürçmesi olarak bilinir. Kaydın "Riemann'ın yazdığı sâbit, doğrusu olan − logaritma 2'den çok az farklıdır" şeklinde tashihi teklif olunur.
2. **Euler, § 15 yolu ve son cedvel satırı:** sahife resmiyle harf harf karşılaştırma henüz yapılmamıştır ([M5]'in kendi ifadesi).
3. **Euler:** Kifâyet hükümlerinin zımnî **bağlılık** şartı (bütün arazilerin köprülerle tek bir bütün olması) kayıtlarda zikredilmemiştir; [M6]'ya bir cümle eklenmesi teklif olunur.
