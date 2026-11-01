# LÜGAT — Riyâziyât Mevzûlarının Osmanlıca Karşılıkları

Bu dizin, riyâziyâtın bütün mevzû listelerini bir araya toplamak ve her
unsura Osmanlıca bir karşılık bulmak için açılmıştır. İş iki kanattan
yürür:

1. **MSC2020** (Mathematics Subject Classification 2020) — Mathematical
   Reviews ile zbMATH'in müşterek tasnifi. Elde verilen PDF nüshası
   (224 sahife) baştan sona metne çevrilmiş, **6603 madde** çıkarılmıştır.
2. **Vikipedi atıf ağı** — `https://en.wikipedia.org/wiki/Lists_of_mathematics_topics`
   sahifesinden başlanır; oradan atıf yapılan bütün liste sahifeleri,
   onların atıf yaptığı liste sahifeleri, ve böylece içeride gezilecek
   liste kalmayıncaya kadar takip edilir.

## Dosya düzeni

| Yol | Muhteva |
| :-- | :-- |
| `msc2020/kaynak.tsv` | MSC2020'nin 6603 maddesi: `kod <sekme> İngilizce metin`. PDF'ten `araclar/msc_ayristir.py` ile çıkarıldı. |
| `msc2020/ceviri/NN.tsv` | Her bab (`NN` = 00, 01, 03 …) için elle yazılan karşılıklar: `kod <sekme> Osmanlıca [<sekme> kayıt]`. `@ilgi <sekme> …` satırı, o babın tekrar eden kalıp maddelerinde ("… hakkında umûmî mürâcaat eserleri" gibi) yerine konacak bab adıdır. |
| `msc2020/msc2020_osmanlica.tsv` | Birleşik netice: `kod · İngilizce · Osmanlıca · kayıt`. `araclar/msc_birlestir.py` üretir. |
| `msc2020/MSC2020_OSMANLICA.md` | Aynı neticenin okunaklı cedveli. |
| `araclar/ham/NN.ham` ve `araclar/jeton_genislet.py` | Uzun ve tekrar eden tabirleri (meselâ "kısmî tefâzulî muâdeleler") bir kere yazmak için kullanılan ham tercüme dosyaları. `@jeton <sekme> H <sekme> harekî nizâmlar` satırı `§H§` jetonunu tanıtır; `§H§in`, `§H§e`, `§H§de` ekleri ses uyumuna göre açılır. `python3 -I araclar/jeton_genislet.py araclar/ham/37.ham msc2020/ceviri/37.tsv` ile `ceviri/` dosyası üretilir; tashih ham dosyada yapılır. Kısaltma kalmaz: jetonlar daima tam metne açılır. |
| `kok_istilahlar.tsv` | Bütün tercümelerde müşterek kullanılan esas ıstılahlar ve her birinin derecesi. |
| `vikipedi/gezinti_defteri.tsv` | Ziyaret edilen her Vikipedi sahifesi: başlık, kimden gelindiği, derinlik, bulunan liste atıfları, hâl. İş kesilirse buradan devam edilir. |
| `vikipedi/DIZIN.md` | Bulunan bütün listelerin dizini (listelerin listesi). |
| `vikipedi/listeler/` | Her listenin unsurları ve Osmanlıca karşılıkları. |

## Kayıt biçimi ve dürüstlük kaidesi

Her karşılığın yanında bir **kayıt** sütunu vardır:

- **boş** → karşılık `kok_istilahlar.tsv`deki esas ıstılahlardan
  kaidesine uygun olarak terkip edilmiştir.
- **şüpheli: …** → karşılıktan emin değilim; sebebi yanına açıkça
  yazılmıştır (ıstılahın Osmanlı devrinde kullanılıp kullanılmadığını
  bilmiyorum, yahut İngilizce tabir birden çok mânâya gelir, gibi).
- **nakil** → hususî isim (Galois, Lie, Banach …) yahut harfî işaret
  (K-nazariyesi, p-adî) aynen nakledilmiştir.

`kok_istilahlar.tsv`de her esas ıstılahın derecesi ayrıca yazılır:

- **kadîm** → Osmanlı riyâziyât ve hikmet kitaplarında kullanıldığını
  bildiğim ıstılah (hendese, cebir, müsellesât, muâdele, silsile …).
  Bu bilgi hafızamdandır; her birinin kaynakla tek tek doğrulanması
  ayrı bir iştir ve yapılmamıştır.
- **teklif** → Osmanlı devrinde karşılığı bulunmayan yahut bilmediğim
  bir mefhum için Arapça/Farsça kökten kaidesine uygun olarak tarafımdan
  teklif edilen terkip. Uydurma bir "eski karşılık" diye sunulmaz.

## Usul

### MSC2020

1. PDF metne çevrildi, maddeler ayrıştırıldı, satır sonu heceleme
   kırıklıkları birleştirildi (6603 madde, ayrıştırılamayan satır sıfır).
2. Babların sırasıyla (00'dan 97'ye) her madde okunur ve karşılığı
   `ceviri/NN.tsv`ye yazılır. Seçmece yapılmaz; tekrar eden kalıp
   maddeler (her babdaki `-00, -01, -02, -04, -06, -08, -11` ve
   `…99 None of the above`) dahi birleştiricide tek tip kalıpla
   karşılanır ve babın kendi adı yerine konur.
3. Her bab bitince birleştirici koşturulur, kalan madde sayısı basılır,
   commit edilir.

### Vikipedi atıf ağı

1. Başlangıç: `Lists of mathematics topics`.
2. Her sahifenin asıl metnindeki atıflar Vikipedi'nin kendi arayüzünden
   (`api.php?action=parse&prop=links`) alınır.
3. **Liste sahifesi** sayılan atıf takip edilir: başlığı `List of`,
   `Lists of`, `Outline of`, `Glossary of`, `Index of`, `Table of`,
   `Timeline of` ile başlayan ve riyâziyâta ait olan sahifeler. Riyâziyâta
   aidiyet, sahifenin Vikipedi kategorilerinden yoklanır; şüpheli olanlar
   defterde ayrıca işaretlenir.
4. Her ziyaret `gezinti_defteri.tsv`ye yazılır; kuyrukta bekleyen sahife
   kalmayınca ağ kapanmış sayılır.
5. Sonra her listenin unsurları çıkarılıp `vikipedi/listeler/`e yazılır
   ve MSC2020'deki usulle Osmanlıca karşılıkları bulunur.

## Telif (imtizâc) kaidesi — kullanıcı hükmü

Karşılıklar bulununca MSC2020 ile Vikipedi listeleri tek bir **telif**
dosyasında birleştirilir:

1. Ana kaynaklar (`msc2020/kaynak.tsv`, `vikipedi/unsurlar.tsv`) ve
   karşılık dosyaları (`msc2020/ceviri/`, `vikipedi/ceviri/`) **asla
   silinmez**; telif ayrı bir dosyadır.
2. Yalnız **tekrarlar** birleştirilir; tekrar olmayan hiçbir unsur düşmez.
   Vikipedi'de 10, MSC'de 5 unsur varsa ve hiçbiri ötekinin tekrarı
   değilse telifte mutlaka 15 mensup bulunur.
3. Hiyerarşi kurulur: MSC başlıkları umûmiyetle Vikipedi unsurlarının
   üst başlığı olur; her unsurun hangi başlığın altına girdiği yazılır.
4. Telif betiği bu sayıyı kendisi doğrular:
   `telif mensup sayısı = MSC unsur sayısı + Vikipedi unsur sayısı − tekrar sayısı`
   tutmazsa betik hata verip durur.

## İmlâ

Osmanlıca karşılıklar Latin harfleriyle, uzun sesliler için şapka
(â, î, û) ve izafet kesresiyle (`nazariye-i a'dâd`) yazılır. Kısaltma
kullanılmaz.
