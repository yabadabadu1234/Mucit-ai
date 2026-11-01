# Lügat İş Parçacığının İlerleme Defteri

Bu defter, iş kesilirse kaldığı yerden devam edebilmek içindir. Her oturum işe bu defteri baştan sona okuyarak başlar ve bitirirken yeni bir kayıt ekler.

## Diğer iş parçacıkları için yol gösterici

- **Esas cedvel (telif dosyası):** `/mnt/project-files/lugat/telif/tip_lugati.jsonl`
  Her satır bir maddedir: kimlik, İngilizce ad, kaynak kayıtları, ebeveynler, eş anlamlılar, tarif ve Osmanlıca karşılıklar (mühürleriyle). Bir maddenin `karsiliklar` listesindeki son satır geçerli karşılıktır.
- **Göz ile okunacak hulâsa:** `/mnt/project-files/lugat/telif/tip_lugati.tsv`
- **Henüz telif dosyası doğmadıysa** (iki tasnif indirilmeden önce), karşılıklar doğrudan `/mnt/project-files/lugat/karsiliklar/` klasöründeki sekmeyle ayrılmış dosyalarda okunabilir.
- **Karşılığı olmayan ıstılah bildirimi:** Tercüme iş parçacığı karşılığını bulamadığı ıstılahı `/mnt/project-files/lugat/talepler/istilah_talepleri.tsv` dosyasına bir satır olarak ekler (sütunlar: tarih, isteyen, ingilizce, geçtiği eser ve yer, bağlam cümlesi) ve lügat iş parçacığına haber verir. Lügat iş parçacığı karşılığı yazınca satırın sonuna maddenin kimliğini ekler; satır silinmez.
- **Terkip kaideleri:** `/mnt/project-files/lugat/kaideler.md`

## Klasörün yapısı

| yol | içindekiler |
|---|---|
| `betikler/indir_mesh.py` | Tıbbî Mevzu Başlıkları'nı resmî neşir sunucusundan indirir, `ham/mesh_tavsifler.jsonl` dosyasına döker |
| `betikler/indir_icd11.py` | Hastalıklar Tasnifi'nin on birinci tâbını resmî arayüzden (yahut resmî neşir cedvelinden) indirir, `ham/icd11_unsurlar.jsonl` dosyasına döker; kesilirse ara kayıttan devam eder |
| `betikler/imtizac.py` | İki tasnifi tek telif dosyasında birleştirir, tekrarları ayıklar, hiyerarşiyi kurar, karşılıkları bağlar |
| `betikler/dogrula.py` | "birinci tasnif artı ikinci tasnif eksi tekrar" hesabını, hiçbir kaynağın ve karşılığın düşmediğini ve hiyerarşinin sağlamlığını yoklar |
| `betikler/karsilik_oku.py` | Karşılık dosyalarını okur, mühürleri ve yarı Latince şüphesini yoklar |
| `karsiliklar/` | Osmanlıca karşılıklar; dosyalar sıra numarasıyla adlandırılır, hiçbir satır silinmez |
| `ham/` | İndirilen ham veri (indirilen asıl arşivler `ham/indirilen/` içindedir ve depoya konmaz) |
| `telif/` | İmtizaç neticesi |
| `deneme/` | Betikleri sınamak için elle yazılmış SAHTE küçük veri; lügate girmez |

## Depo

- Asıl kayıt yeri: `https://github.com/yabadabadu1234/Mucit-ai` deposunun `tip-piri-lugat` dalında `lugat/` klasörü.
- `/mnt/project-files/lugat/` bu klasörün aynasıdır; her kayıttan sonra depodaki hâli buraya kopyalanır ki depoya erişemeyen iş parçacıkları da okuyabilsin. İkisi ayrılırsa depodaki hâl esastır.
- Deponun `CLAUDE.md` emirnamesi kod içinde şerh ve izah eden belge dizgisi yazmayı yasaklar. Bu sebeple betiklerin şerhi aşağıdaki "Betiklerin şerhi" babındadır.

## Betiklerin şerhi

**`indir_mesh.py`.** Millî Tıp Kütüphanesi'nin `https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh/` adresinden `desc<SENE>.gz` dosyasını (yoksa `.xml`) indirir. Sene verilmezse gelecek seneden geriye doğru dört sene dener; zira kütüphane bir sonraki senenin dosyasını içinde bulunulan senenin sonbaharında neşreder. Her tavsif kaydından şunları çıkarır: tavsif numarası, adı, ağaç numaraları, tercih edilen kavramın tarif notu ve bütün giriş terimleri. On altı kıtanın adları XML dosyasında tavsif kaydı olarak bulunmadığı için betikte sabit yazılıdır. Künye dosyasına indirilen arşivin özet değeri (SHA-256) yazılır ki aynı dosyadan çalışıldığı sonra ispat edilebilsin.

**`indir_icd11.py`.** İki yolu vardır. (1) Muhitte `ICD_CLIENT_ID` ve `ICD_CLIENT_SECRET` varsa resmî arayüzden: `https://icdaccessmanagement.who.int/connect/token` adresinden jeton alınır, `https://id.who.int/icd/release/11/mms` adresinden en yeni sürüm öğrenilir, kökten başlanarak her çocuk sekiz işçiyle ziyaret edilir. Her unsur `ham/icd11_ara_kayit.jsonl` dosyasına anında yazılır; iş kesilirse betik bu dosyayı okuyup kaldığı yerden devam eder. (2) Kimlik yoksa teşkilâtın "SimpleTabulation" neşir cedvelinden: başlıktaki "- " işaretlerinin sayısı derinliği verir, ebeveyn buradan kurulur. Bu cedvelin varsayılan adres kalıbı (`https://icdcdn.who.int/static/releasefiles/<sürüm>/SimpleTabulation-ICD-11-MMS-en.zip`) hatıradan yazılmıştır ve **şüphelidir**; tutmazsa adres `--cedvel-adresi` ile verilir. Adresi "/other" yahut "/unspecified" ile biten unsurlar artık (residual) unsurlardır ("başka yerde zikredilmiş", "tasrih edilmemiş").

**`imtizac.py`.** Tekrar yalnız şu dört şart beraber bulunursa kabul edilir: (a) Hastalıklar Tasnifi unsuru artık unsur değildir; (b) adı, normalleştirildikten sonra (küçük harf, tire ve noktalama boşluğa çevrilir) Tıbbî Mevzu Başlıkları'nda tek bir tavsifin adına yahut giriş terimine eşittir; (c) bu ad Hastalıklar Tasnifi'nde tek bir unsura aittir; (d) o tavsife başka hiçbir unsur eşleşmemiştir. Bire bir olmayan eşleşmeler birleştirilmez, `telif/muhtemel_tekrarlar.tsv` dosyasına yazılır ve elle tetkik edilir. Birleşen maddede iki kaynağın kaydı da aynen durur, iki hiyerarşideki ebeveynler de beraber tutulur. Yapı düğümleri ("KOK", "MeSH-kok", on altı "MeSH-kita", "ICD11-kok") sayıma girmez.

**`dogrula.py`.** Ham dosyalardan bağımsız sayar: her tavsif ve her unsur telifte tam bir defa kaynak olarak geçmeli; tekrar sayısı iki kaynağı birden taşıyan maddelerden yeniden hesaplanır ve "telif madde sayısı = birinci tasnif + ikinci tasnif - tekrar" eşitliği yoklanır; her ebeveyn mevcut olmalı, devir olmamalı, her madde köke ulaşmalı; her karşılık satırı ya bir maddeye bağlanmış ya `eslesmeyen_karsiliklar.tsv` dosyasında olmalı. Bir yoklama tutmazsa betik sıfırdan farklı çıkış koduyla biter.

**`karsilik_oku.py`.** Mühür yalnız "kadîm", "teklif", "şüpheli" olabilir; kadîm satırda delil boş olamaz. Yarı Latince yoklaması bir parça listesiyle (mesela "itis", "loji", "gastro") yapılır; bulunan satır reddedilmez, uyarılır, çünkü Osmanlıcaya asırlar önce girmiş kelimeler de bulunabilir.

## Kadîm mührün kaynakları

Şaheser iş parçacığının ikinci cüzü (`/mnt/project-files/saheser/cuz_02_kadim_islam_tibbi.md`) baştan sona okundu. "Kadîm" mührünün delili şu nüshalarda aranacaktır (hepsi Internet Archive'dedir; bu oturumda `archive.org` kapalıdır):

| eser | nüsha künyesi | lügatteki vazifesi |
|---|---|---|
| İbn-i Sînâ, el-Kânûn fi't-Tıbb, Roma 1593, Arapça | `QanunAvicennae` | Bütün kıtalar için birinci kaynak; bilhassa A (teşrîh), C (emrâz), G (kuvvetler ve ef'âl) |
| Zehrâvî, et-Tasrîf'in otuzuncu makalesi, Oxford 1778, Arapça ve Latince | `b30411427` | Cerrahî ıstılahı (E kıtası); Sabuncuoğlu'nun ana kaynağı |
| Şânîzâde Mehmed Atâullah, Hamse-i Şânîzâde ve Mir'âtü'l-Ebdân, İstanbul, 1820 civarı | `amseinzde01anizuoft` | Teşrih ıstılahı (A kıtası) ve terkip usulünün esas örneği; künyedeki 1810 tarihi şüpheli, hangi cilt olduğu tahkik edilecek |
| Râzî, Kitâbü'l-Cüderî ve'l-Hasbe, Greenhill tercümesi 1848 | `atreatiseonsmal00unkngoog` | Sâri hastalık ıstılahı |
| İbnü'l-Baytâr, el-Câmi' li-Müfredâti'l-Edviye ve'l-Ağdiye | tahkik edilecek | İlaç adları (D kıtası) |
| Sabuncuoğlu, Cerrâhiyyetü'l-Hâniyye | Internet Archive'de bulunamadı; Paris nüshası Gallica'da aranacak | Türkçe cerrahî ıstılahı |

Kaide: Bir karşılığın delili bu nüshalardan birinde sahife yahut varak numarasıyla gösterilince delil sütununa o künye yazılır. Birinci oturumda vurulan üç kadîm mühür (teşrîh, emrâz, emrâz-ı cildiyye) eser ve bab künyesiyle yazılmıştır, sahife numarası yoktur; nüshalar açılınca tamamlanacaktır.

## Çalıştırma sırası

```
cd /mnt/project-files/lugat
python3 -I betikler/indir_mesh.py
ICD_CLIENT_ID=... ICD_CLIENT_SECRET=... python3 -I betikler/indir_icd11.py   # kimlik yoksa: --yerel <SimpleTabulation dosyası>
python3 -I betikler/imtizac.py
python3 -I betikler/dogrula.py
```

## Kayıtlar

### 1 Teşrinisani 2026 (Kasım), birinci oturum

Yapılanlar:
- Depo yok; koordinatörün tarifiyle `/mnt/project-files/lugat/` içinde yerel git deposu açıldı.
- Ağ yoklandı: `nlmpubs.nlm.nih.gov`, `id.who.int`, `icd.who.int`, `icdaccessmanagement.who.int`, `archive.org` adreslerine oturumun ağ siyaseti izin vermiyor. Kullanıcıdan izin istendi. GitHub ve paket sunucuları açık.
- Beş betik yazıldı ve `deneme/` içindeki sahte küçük veriyle uçtan uca sınandı. Doğrulama neticesi: "3 + 5 - 2 = 6", DOĞRU.
- Terkip kaideleri yazıldı (`kaideler.md`).
- İlk karşılıklar yazıldı: Tıbbî Mevzu Başlıkları'nın on altı kıtası (`karsiliklar/001_mesh_kitalar.tsv`) ve Hastalıklar Tasnifi'nin yirmi altı babı ile iki zeyl kısmı (`karsiliklar/002_icd11_bablar.tsv`). Toplam kırk dört satır: üç kadîm, otuz sekiz teklif, üç şüpheli.

Şüpheli kalan noktalar:
- Hastalıklar Tasnifi babları `ICD11-bab:<numara>` anahtarıyla bağlandı. Resmî arayüzün bab unsurlarında numara `code` alanında gelmiyorsa bu satırlar `telif/eslesmeyen_karsiliklar.tsv` dosyasına düşer (silinmez); o zaman anahtar `ICD11:<unsur kimliği>` şekline çevrilmelidir.
- Neşir cedvelinin varsayılan adres kalıbı hatıradan yazılmıştır, doğrulanmamıştır.
- Bab adlarının İngilizce yazılışı hatıradan yazıldı; indirmeden sonra `telif/ingilizce_uyusmazligi.tsv` dosyasına bakılmalı.

Sıradaki iş:
1. Ağ izni gelince iki tasnifi indir, imtizaç ettir, doğrula, kayıt et.
2. Karşılıkları ağacın üst basamaklarından başlayarak aşağı doğru, kıta kıta doldur. Sıra: C (Emrâz), A (Teşrîh), G (Hâdisât; fizyoloji burada), Hastalıklar Tasnifi babları, sonra diğer kıtalar.
3. Ortak depo belli olunca bu klasörü oraya taşı.

### 1 Teşrinisani 2026 (Kasım), birinci oturumun devamı

- Kullanıcı ortak depo olarak `yabadabadu1234/Mucit-ai` deposunu seçti. Klasör, deponun `tip-piri-lugat` dalında `lugat/` altına taşındı.
- Deponun `CLAUDE.md` emirnamesi baştan sona okundu. Lügate dokunan hükümleri: `grep` ile arama yasak; kod içinde şerh ve izah eden belge dizgisi yasak; sessiz ikame yasak; hiçbir kayıt silinmez. Betiklerdeki şerhler bu deftere taşındı, betiklerden ayıklandı; deneme yeniden koşturuldu, netice yine DOĞRU.
- Ağ yeniden yoklandı: resmî adresler bu oturumda hâlâ kapalı. Kullanıcının yeni muhiti ancak yeni açılan oturumlarda geçerli olur.

### 1 Teşrinisani 2026 (Kasım), tercüme iş parçacığının ilk talebi

- Tercüme iş parçacığı, Cannon'un "The Wisdom of the Body" şerhindeki kırk bir ıstılahı bildirdi. Şerh dosyası (`/mnt/project-files/tercume/cannon_bedenin_hikmeti/serh.md`) baştan sona okundu.
- Hepsi tetkik edilip `karsiliklar/003_tercume_cannon.tsv` dosyasına kırk dört satır olarak yazıldı (umumî ziyâbitus ile şekerli ziyâbitus ayrıldı, "ra'şe" ile "kuş'ırîre" ayrıldı). Talepler `talepler/istilah_talepleri.tsv` dosyasına kaydedildi.
- Tashihler: shivering için "ra'şe" yerine "kuş'ırîre" (ra'şe tremor'dur); edema için umumî olanında "istiskâ-yı lahmî"; plasma proteins için "mevâdd-ı zülâliyye-i dem" (şüpheli); autonomic için "cihâz-ı asabî-i nebâtî"; carbonic acid için "hâmız-ı fahmî" yeğlendi.
- Anahtar şekli olarak `MeSH-ad:<İngilizce başlık>` ve tasnifte başlığı olmayanlar için `SERBEST:<ıstılah>` eklendi; imtizaç betiği buna göre güncellendi, deneme yeniden DOĞRU çıktı.
- Kadîm mühürlerin delilleri el-Kânûn'un kitap ve fen künyesiyle yazıldı; sahife numaraları `QanunAvicennae` nüshası açılınca eklenecek.

### 1 Teşrinisani 2026 (Kasım), devir

- Bu oturumun ağında resmî adresler kapalı kaldığı için iş, tam izinli muhitte açılan yeni lügat iş parçacığına devredildi. Bu oturum burada durur.
- Devir anında: iki tasnif henüz indirilmedi; `ham/` ve `telif/` klasörleri boştur (yalnız `deneme/` altında sahte deneme verisi vardır). Karşılık dosyalarında seksen sekiz satır vardır (`001`, `002`, `003`).
- Yeni oturumun ilk işi: `betikler/indir_mesh.py` ve `betikler/indir_icd11.py` koşturmak, sonra `imtizac.py` ve `dogrula.py`; `telif/ingilizce_uyusmazligi.tsv` ile `telif/eslesmeyen_karsiliklar.tsv` dosyalarını tetkik edip Hastalıklar Tasnifi bab anahtarlarının tutup tutmadığını yoklamak.
