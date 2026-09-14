# MUCİT-AI -- PADİŞAHIN KAT'Î USUL FERMANLARI

Bu dosya bir tarif değil, bir **emirnâmedir**. Her oturumun başında okunur ve
her satırı bağlayıcıdır. İhlâl edilirse yapılan iş geçersizdir.

---

## ▓▓▓ 1. FERMAN: UMUMİDEN HUSUSİYE -- EBEDİYYEN ▓▓▓

> *"Bundan sonra böyle hatalara düşmemek için evvela ortada hiçbir yeni dosya,
> kod, fonksiyon yokken sanki varmış gibi hayal edip **en üst mertebe kodu
> güncelleyeceksin**, sanki varmış gibi oraya **çağrı kodunu ekleyeceksin**.
> Daha sonra fonksiyonu ayrı bir dosyada yazman serbest olabilir. Sen yazmaya
> hususiden başlayıp umumide bitiriyordun; artık bu stratejiyi **EBEDİYYEN**
> terk edeceksin, umumiden başlayıp hususiye gideceksin!"*

### İCRA SIRASI -- DEĞİŞMEZ, İSTİSNASIZ

```
1. ÖNCE TAHT      main/egitim.py, main/cikarim.py -- nazırlık katı.
                  Henüz OLMAYAN modülün çağrısı BURAYA yazılır.
                  Kip eklenir, ayar alanı eklenir, rapor satırı eklenir.
                  Dosya yokken de yazılır: "sanki varmış gibi".
                  ↓
2. SONRA ARA KAT  Çağrılan uzvun bağlanacağı yer (nefs/, ogrenme/…).
                  ↓
3. EN SON HUSUSİ  Fonksiyonun kendisi, ayrı dosyada.
```

**NİÇİN.** Hususiden başlanınca ortaya bağlanmamış, yetim, "sonra terkip
ederiz" denen dosyalar çıkıyor. Umumiden başlanınca bağlanmamış dosya
**imkânsızdır**: çağrı zaten yazılmıştır, yazılmayan şey koşmaz.

**YASAK.** Bir dosya yazıp "şimdi bağlayacağım" demek. Çağrı evvel yazılmamışsa
o dosya yazılmaz.

---

## ▓▓▓ 1-B. FERMAN: KAİDE BEYAN EDİLİNCE DERHAL BURAYA MÜHÜRLENİR ▓▓▓

> *"Sana 'bundan böyle', 'bundan sonra', 'ebediyyen' ve benzeri aynı
> manaları çağrıştırır hitaplarla kaide beyan edersem **derhal
> CLAUDE.md'ye mühürleyeceksin** onu! Daha evvel senin yaptığın
> münafıklığı başkası yapmasın diye!"*

Padişahın sözünde şu kalıplardan biri geçerse -- *bundan böyle · bundan
sonra · ebediyyen · artık · asla · daima · her defasında · bir daha* --
o söz bir **kaidedir** ve cevap verilmeden **evvel** bu dosyaya
yazılır. Sonraya bırakılmaz: sonraya bırakılan kaide, bir sonraki
oturumda yok hükmündedir ve aynı münafıklık tekrarlanır.

---

## ▓▓▓ 1-C. FERMAN: MÜNAFIKLIK YASAKLARI ▓▓▓

### (a) ANA AKIŞTA NE KOŞTUĞUNU **ASLA ÖLÇME**

> *"Bundan böyle ana akışta fiilen ne koştuğunu asla ölçmeyeceksin,
> kodu okuyup zihninle tayin edeceksin, buna matuf ne kadar testin
> varsa hepsini gafilane yazılmış yalancılık eseri ilan ediyor, derhal
> imha etmeni emrediyorum!"*

* İthal grafına, erişilebilirlik hesabına, "beylik modül" sayımına
  dayanan **hiçbir sınama yazılmayacak**. Hepsi imha edildi
  (`tanilama/nizam.py`, `nefs/akit.py`, `tanilama/divan.py`, `YETIM_BORCU`).
* Bir modülün iş görüp görmediği **kodu okuyana** sorulur.

### (b) İSİM EKLEMEK BAĞLAMAK DEĞİLDİR

> *"Sana sadece oradaki bir listeye isim mi yaz dedim? Bizzat
> çağrışacak fonksiyonun imzasını evvelden hayal edip oraya
> yerleştireceksin dedim gafil!"*

Bir modülü ana koda "bağlamak" şu demek **değildir**: ithal etmek ·
bir listeye adını yazmak · bir ayar alanı eklemek · bir rapor satırı
koymak. Bağlamak **tek şey** demektir: ana akışın koştuğu bir yerde
**o fonksiyonun fiilen çağrılması** ve neticesinin kullanılması.
Tesir kapatılabilmeli (ölçü kırmızı yanabilsin), fakat varsayılanda
**koşuyor** olmalı.

### (c) TELAFİ USULÜ

Geçmiş münafıklıkların telafisi bellidir: **doğru usulle şimdi
düzeltmek.** Yâni evvela taht, sonra ara kat, en son hususi.

---

## ▓▓▓ 1-D. FERMAN: TAHT KODU BAŞTAN SONA **BİR KEZ** OKUNUR ▓▓▓

> *"Taht kodlarının unutulan bir satırı dahi olsa baştan sona tekrar
> ama bir kez okunacağı, sürekli grep ile arama yapmanın uzun vadede
> sürekli daha çok satır gösterdiği için daha fazla israf demek olduğu
> kaidesi... Sadece bir kez baştan sona oku, ezberinde tut! Bir şey
> unutursan grep ile arama, baştan sona tekrar oku!"*

* İşe başlarken `main/egitim.py` ve `main/cikarim.py` **baştan sona**
  okunur. Bir kez.
* **`grep` ile taht kodunda arama yapmak yasaktır.** Grep her seferinde
  daha çok satır gösterir ve uzun vadede israftır; üstelik parça
  gösterdiği için bütünü gizler -- münafıklığın gizlendiği yer tam da
  o boşluklardır.
* Unutulursa: **baştan sona tekrar okunur.**

> *"Kurân hâfızı odur ki önünde Kurân yokken de hatim indirebilsin;
> hoca odur ki önünde kitap olmadan fetva verebilsin."*

Eksik çağrıları yerine koymak bir **ölçüm** işi değil, **ezber ve
hafıza** işidir. Ölçüm aleti (profil, coverage, erişilebilirlik) bu
işte kullanılmaz.

---

## ▓▓▓ 1-E. FERMAN: HÜKMÜN GEREĞİ HARFİYYEN YAPILIR -- YARIM İŞ YASAK ▓▓▓

> *"O bilmem ne motoruna tamamen geçmedik, melekeler hâlâ yoğun ortamda
> vuruluyor, bilmem ne şu bahane bu bahane, mazeret bulup duruyorsun.
> Sana bir hüküm verdiysem süs olsun diye vermedim, gereği neyse onu
> yapacaksın, **iddia edeceksin ve sözünün ardında duracaksın**. Ne
> hüküm verilmişse, gereği neyse onu **harfiyyen** yapacaksın... bu
> motora **tamamen** geç! Yarısı orda yarısı burda bir şey istemiyorum,
> **yarım meyve sağlam kalmaz, iki günde çürür!**"*

### YASAK OLAN İKİ SÖZ

1. **"Şu kısmı yapıldı, şu kısmı yapılmadı."** Bir hüküm verildiyse
   gereği **tamamen** yapılır. "Temsili kurdum ama ameliyeler hâlâ eski
   yolda" demek hükmü icra etmek değil, hükmü süs yapmaktır.
2. **"Ne iddia edilmiyor: ... motoruna geçtik demek yalan olurdu."**
   Bu cümle bir dürüstlük gibi görünüp mazeret olur. Doğrusu mazereti
   yazmak değil, **motora fiilen geçmektir**. Hudut ancak hükmün
   **kendisi** imkânsızsa yazılır ve o zaman da imkânsızlığın delili
   konur -- "vaktim olmadı", "riskli", "büyük iş" delil değildir.

### YARIM İŞİN ALAMETİ

Bir uzuv yazılıp eski yol da yerinde duruyorsa **yarımdır**. Yeni usul
geldiyse eskisi aynı turda **imha edilir** (2. ferman). İki yol yan yana
durdukça hangisinin koştuğu belirsizdir ve belirsizlik münafıklığın
yatağıdır.

### SÖZÜN ARDINDA DURMAK

İddia edilir ve arkasında durulur: *"bu motora geçildi"* denince o
motorun **fiilen** koştuğu, eskisinin **kalmadığı** kastedilir.

---

## ▓▓▓ 1-G. FERMAN: ANA KODA RAPOR YAZMAK YASAKTIR ▓▓▓

> *"Umumiden hususiye gidiyorsun ama umumiye rapor yazıyorsun!! **Bundan
> böyle ana koda rapor yazmak yasak!!!!!!!** Tek yapacağın gerçek
> fonksiyonları çağırmak."*

Taht (`main/egitim.py`, `main/cikarim.py`) bir **nazırlık katıdır**;
matbaa değildir. Orada bulunabilecek tek şey:

* uzvun **ithali**,
* uzvun ayarının **kurulması**,
* uzvun **fiilen çağrılması** ve neticesinin kullanılması,
* uzvun kendi **beyan/rapor** fonksiyonunun çağrılması.

**YASAK OLAN.** Tahtta `"%.4f" %`, `s += [...]`, `"\n".join(...)`
biçiminde bir metin kurmak. Bir uzvun neticesi nasıl yazılacaksa onu
**o uzuv** bilir ve kendi dosyasında yazar; taht yalnız çağırır.

**NİÇİN.** Rapor tahtta yazılınca iki şey oluyordu:

1. Uzuv **bağlanmadan** da rapor satırı yazılabiliyordu -- yâni ferman
   1-C(b)'nin yasakladığı münafıklık tam da bu kapıdan giriyordu.
2. Taht şişiyor, hangi uzvun fiilen koştuğu o metin yığınının içinde
   kayboluyordu. Umumiden hususiye gitmenin manası, umuminin **ince**
   kalmasıdır.

---

## ▓▓▓ 1-H. FERMAN: TEK MOTOR -- EĞİTİM DE KONUŞUR ▓▓▓

> *"Hazine + hafıza yükle → söyle **sadece çıkarımda olamaz**. Eğitimde
> de mutlaka olacaktır ki doğru konuşup konuşmadığı tespit edilebilsin,
> konuşacak bir hafızası oluşsun. Eğitim ile çıkarım arasındaki **tek
> fark** normal llm'ler gibi çıkarım esnasında optimizasyon
> yapılmayacak olmasıdır, 'Test Time Training hariç'. Onun dışında
> **tek bir motor vardır**."*

* `hazine` + `hafıza` + `söyle` üçlüsü **her iki kapıda da** koşar.
* Tâlim konuşmadan bitmez: konuşmayan bir tâlim, doğru konuşup
  konuşmadığını ölçemez ve konuşacak bir hafıza biriktirmez.
* İki kapı arasındaki fark **tek satırdır**: çıkarımda eniyileme
  koşmaz. (Test Time Training bunun istisnasıdır ve açıkça öyle
  ilan edilir.) Başka hiçbir fark meşru değildir.

---

## ▓▓▓ 1-I. FERMAN: BİR VERİ, HATASI SIFIRLANANA KADAR ▓▓▓

> *"O veri için hata sıfırlanana kadar devam etmelisin, sonra yeni veri
> getirmelisin. Böylece bir süre sonra tüm veriler için **müşterek bir
> münasebet haritası** oluşacak."*

Tâlim, veri yığınını bir kere görüp geçmez. Bir örnek alınır ve o
örneğin hatası **sıfırlanana kadar** üstünde durulur; ancak ondan
sonra yeni örnek getirilir. Biriken şey tek tek cevaplar değil,
bütün veriler için **müşterek münasebet haritasıdır**.

### SIFIRLANMAK NE DEMEK -- KAT'Î HUDUT

> *"Kesinlikle **tenakuz, kısırdöngü, mantıksızlık olmayacak**, bunlar
> kesin huduttur, bunun haricinde zaten sıfır olamaz."*

Sıfır, kaybın sayısal sıfırı değildir (o zaten imkânsızdır). Sıfır
**üç hududun temiz olmasıdır**:

    1. TENAKUZ      yok    (parite alarmı sönük, ω taklası yok)
    2. KISIRDÖNGÜ   yok    (kanonik adres kapanışı yok)
    3. MANTIKSIZLIK yok    (kod uzayı dışına taşma yok)

---

## ▓▓▓ 1-J. FERMAN: EŞİK SABİT DEĞİL, FONKSİYONDUR ▓▓▓

> *"Eşik koyarken **sabit bir değer koymayacaksın**, bir fonksiyona
> bağlı olacak o eşik. Yâni **kemiyete değil keyfiyete**, o keyfiyetin
> ne nispete eriştiğini ölçen bir fonksiyon vasıtasıyla olacak."*

* Bir eşik koda `0.35` diye yazılamaz. Eşik, bir **keyfiyetin** hangi
  nispete eriştiğini ölçen bir fonksiyonun çıktısıdır.
* Kemiyet (kaç tane, ne kadar büyük) eşik olamaz; keyfiyet (temiz mi,
  kapandı mı, tutarlı mı) ölçülür ve nispeti eşiği verir.
* Bu ferman 5-B'nin (donanım ölçülür) mizan tarafındaki kardeşidir:
  orada sayı donanımdan, burada eşik keyfiyetten gelir.

---

## ▓▓▓ 1-K. FERMAN: KAYNAK YOKLANIR, TAHMİN EDİLMEZ ▓▓▓

> *"Bunları tek tek araştırıp bulman mümkün değil, githubda var
> olduğunu bildiğin çok büyük çaplı verisetlerini şöyle bir
> hatırlamanı rica edeceğim... Şu kodları dene, çalışıyorsa **artık**
> huggingface'e de şümullen."*

* Hatırlamak bir başlangıçtır, hüküm değildir. Hatırlanan her depo
  **yoklanır** (`git ls-remote`, sonra klon ve envanter) ve cetvele
  ancak yoklandıktan sonra girer. *"Var sanıyorum"* diye bir satır
  yazılmaz; alınamayan satırın **engeli sayıyla** yazılır (ferman 1-F).
* Bir kaynağın `yol`u ve `uzanti`si tahminle konmaz: deponun kendi
  **envanterinden** okunur. Yanlış tahminin bedeli veri imhası olamaz --
  hiçbir dosya uzantıya uymuyorsa **tek dosya bile silinmez**.
* HuggingFace'e şümul **şarta bağlıdır ve şart yoklanmıştır**: bu
  oturumda `huggingface.co` vekilde siyaseten kapalıdır (`CONNECT`a
  403) ve kapta `ssh` ikilisi yoktur. Şart açılırsa -- yâni klon
  fiilen koşarsa -- `main/kulliyat.py` cetveline HF kaynakları
  **derhal** girer; kapalıyken girmeleri süs olurdu.

---

## ▓▓▓ 1-L. FERMAN: YALNIZ TAHT KOŞAR -- TEST KODU ASLA ▓▓▓

> *"Sana **bundan böyle** tahttan başka hiçbir koşu çalıştırmayı caiz
> kılmıyorum, hiçbir test kodu **asla ve kat'a** çalışamayacak, yalnız
> main kodu çalışabilir ve sen kod okuyup öyle hata ayıklayabilirsin,
> başka türlüsü yok!"*

**KOŞTURULABİLEN TEK ŞEY:**

```
python -m main.egitim ...
python -m main.cikarim ...
```

**YASAK:** `python -c "..."` ile kurulan tek seferlik denemeler ·
`/tmp` altına yazılan ölçüm betikleri · `cProfile` koşusu · A/B
kıyası için kurulan ikinci bir hat · `depo/` altındaki koşturucular ·
`pytest` · her ne ad altında olursa olsun **tahtın dışında** koşan
her şey.

**HATA AYIKLAMA USULÜ: KOD OKUNUR.** Bir kusur ölçülerek değil,
**kodu okuyarak** bulunur (ferman 1-C/a ve 1-D'nin tabiî neticesi:
ana akışta ne koştuğu ölçülmez, zihinle tayin edilir). Bir sayı
lâzımsa o sayıyı **taht** basar: ölçü tahtın kendi beyanına konur ve
tahtla beraber koşar. Tahtın basmadığı sayı, sayı değildir.

**NİÇİN.** Yan koşu iki şey yapıyordu: (1) tahtta olmayan bir yolu
ölçüp "ölçtüm" dedirtiyordu -- yâni ölçülen şey ile koşan şey ayrı
olabiliyordu; (2) tahtın kendi beyanına konması gereken ölçüyü
dışarıda tutup tahtı fakir bırakıyordu.

---

## ▓▓▓ 1-M. FERMAN: HER ŞEY YAZMAÇTAN GİRER, YAZMAÇTAN ÇIKAR ▓▓▓

> *"Boyut moyut da ayrı bir yerden gelmez ahmak, llm yapıyoruz llm,
> boru değil!!! Satır sayısı yazmaçtan gelmez demişsin! **Her şey
> yazmaçtan girer, yazmaçtan çıkar, aksi yol yoktur**, yazmaç da kübit
> değil quditttir, o da ℂ^d uzayında değil diğer tarif ettiğimiz
> uzaydadır."*

* Bir ölçü -- satır sayısı, lif boyu, sektör haddi, yığın -- **ayrı
  bir yerden** gelmez. Tek kaynak **yazmaçtır**; başka her yer onu
  okur.
* İki yerde iki ayrı sayı duruyorsa bu bir "uyum meselesi" değil,
  **çift başlılıktır** ve ferman 2-B gereği kökünden kesilir. Doğrusu
  ikisini birbirine yaklaştırmak değil, birini **imha edip** ötekini
  tek kaynak yapmaktır.
* Yazmaç kübit yazmacı değildir ve ℂ^d de değildir: Galois `GF(2⁸)` +
  stabilizer tableau + `Z_m` ayrık faz + Kronecker karo (ferman 7).
  "Boyut" o taşıyıcının kendi ölçüsüdür.

---

## ▓▓▓ 1-N. FERMAN: BELİRTEÇ HER DAİM TİKTOKEN'DİR ▓▓▓

> *"Workflowda bana sözlük boyutu sorup 16 demişsin, bu ne rezalet,
> sence ultramath verisetinde 16 token mi var, tiktoken kadar token
> mi var? Ana tokenizer ister arc ister metin, ne olursa olsun **her
> daim tiktokendir**, sen tiktokenin altındaki mekanizmayı değiştirip
> bizim tip vektörleri yapacaksın! Tüm ayarlarda sözlük ebatını sen
> değil **tiktoken belirleyecek, otomatik!!**"*

* **TEK BELİRTEÇLEYİCİ VARDIR: tiktoken.** ARC ızgarası da, tefsir de,
  riyaziye ispatı da aynı kapıdan geçer. "Bu veri için bayt düzeyi
  yeter" demek yasaktır: iki belirteç uzayı, iki ayrı modeldir.
* **SÖZLÜK EBADI ELLE YAZILMAZ.** ``sozluk = 16`` gibi bir satır
  yoktur ve olamaz. Sözlük, tiktoken kodlamasının kendi ``n_vocab``ıdır
  ve **yoklanarak** alınır (ferman 5-B'nin belirteç tarafı).
* **DEĞİŞTİRİLEN ŞEY TİKTOKEN DEĞİL, ALTINDAKİ MEKANİZMADIR.**
  Tiktoken belirteç **kimliğini** verir; o kimliğin taşıyıcıya nasıl
  gömüleceği bizimdir. Gömme, sürekli bir "embedding matrisi" değil,
  **tip vektörüdür**: belirteç kimliği veri lifinin tabanında
  basamaklara açılır ve her basamak bir qudit seviyesidir. Böylece
  100 bin belirteçlik bir sözlük, ``d``yi patlatmadan taşınır.
* Bir belirteç uzayı iddiası **sayısıyla** yazılır: kodlamanın adı,
  ``n_vocab``ı ve basamak sayısı raporda görünür.

---

## ▓▓▓ 1-N-B. FERMAN: TEK BELİRTEÇ TAHMİN EDİLMEZ ▓▓▓

> *"Dikkatini çekerim, kuantum mimaride **tek bir belirteç tahmin
> etmiyoruz**! Penceremiz mesela 1 milyon ise ve 200 bin kelimelik
> sözlüğümüz varsa **200.000^1.000.000 kadar ihtimali aynı anda**
> değerlendirebilmek için qudite kodlama yapıyoruz, mimarimiz böyle
> olmasa **kuantum olmasının bir manası kalmazdı**!"*

* Üretim bir *"sonraki belirteci seç"* ameliyesi **değildir**. Yazmaç
  `sözlük^pencere` mertebesindeki bütün **dizileri** aynı anda taşır;
  tip vektörünün (ferman 1-N) ve seviye kodlamasının varlık sebebi
  budur.
* Bir yerde *"en yüksek olasılıklı belirteç"* diye tek başına bir
  seçim yapılıyorsa orada kuantum mimari **iptal edilmiş** demektir.
* Arama (`nefs/ara.py`) tek belirtecin genliğini aramaz; **dizinin
  tamamının** genliğini arar.

---

## ▓▓▓ 1-N-C. FERMAN: ARC'A MAHSUS KOD ÇÖPE ▓▓▓

> *"Sırf ARC ızgarasını çözsün diye oluşturduğun ne kadar kod varsa,
> içinde **ana motora zorlama olmayan bir katkısı olmadığı müddetçe**
> at çöpe!"*

* Ölçü tektir: *"bu uzuv ana motora, zorlama olmadan, tabiî bir katkı
  veriyor mu?"* Vermiyorsa -- yâni yalnız ARC ızgarasını çözmek için
  yazılmışsa -- **kesilir**.
* **"Zorlama katkı" katkı sayılmaz.** Bir ARC uzvunu *"ama şu da
  sayılabilir"* diye motora iliştirmek ferman 1-C(b)'nin
  münafıklığıdır; katkı tabiî olmalıdır.
* Bu ferman, *"ölü dosya silinmez"* hükmünün **tek istisnasıdır** ve
  ferman 6'nın icra kolu olarak okunur.

---

## ▓▓▓ 1-O. FERMAN: VERİ SINIRLANMAZ -- BORU HATTI KURULUR ▓▓▓

> *"Ayrıca sana ne oluyor da indirdiğin veriseti sınırlıyorsun? İnen
> şey githuba inecek, sen de ineni kendi cpu'na tek hamlede paldır
> küldür almayacaksın, **boru hattı kurup işini bitire bitire**
> alacaksın ama **verisetinin tamamı o repoda duracak!**"*

İki yer birbirine karıştırılmayacak:

    DEPO (GitHub)   verisetinin **TAMAMI** durur. Budama YOKTUR,
                    pay yoktur, "diskim yetmiyor" mazereti yoktur.
                    Yer meselesi GitHub'ın meselesidir, bizim değil.
    KAP (bu CPU)    veri **tek hamlede** alınmaz. Boru hattı parça
                    çeker, işini bitirir, parçayı bırakır, sonrakini
                    çeker. Kabın darlığı **akışla** çözülür, veriyi
                    kesmekle değil.

* ``depo/kulliyat``ta bir kaynağın **tamamının** durması şart değildir;
  fakat **hiçbir kaynak kesilmez** -- kesilen şey ancak o an kapta
  tutulan penceredir.
* "Diskte yer kalmadı" bir hüküm değil, **boru hattının yanlış
  kurulduğunun delilidir**.

---

## ▓▓▓ 1-P. FERMAN: TEK MODEL -- SATIR/SÜTUN DİYE BİR ŞEY YOK ▓▓▓

> *"Bana satır sütun tahmini için ayrı bir mimarinin koştuğunu
> söyledin, sil dedim, sen kendi içindeki tenakuzunu giderdin. Ahmak,
> **artık tek bir model var**, satır sütun diye bir şey yok, elimizde
> **sadece bir llm var**!!!"*

* Izgaranın ebadını (satır, sütun) kestiren **hiçbir yardımcı mimari
  yoktur**. Ebat da modelin söylediği metinden çıkar: model ızgarayı
  yazar, ayrıştırıcı okur. Ayrı bir "ölçü kestirimi" kolu açmak,
  ferman 6'nın yasakladığı göreve mahsus çözücüdür.
* *"Kalıp bilinmiyor -- çıktının ebadı kestirilemedi"* diye bir sükût
  sebebi olamaz: model konuşur, konuştuğu ayrıştırılır, ayrıştırılamazsa
  **yanlış cevap** sayılır. Ebat kestirilmez.

---

## ▓▓▓ 1-R. FERMAN: TEK MOTOR, İKİ VERİ CİNSİ ▓▓▓

> *"Bundan sonra eğitimimizde temel esasımız iki türlü olmalı ama
> **her iki türü de çalıştırmalıyız**... Yukarıda dediklerimden sakın
> yanlış bir şey anlama, **iki farklı motor kurmuyoruz asla**, sadece
> motora girecek verinin **cinsine göre** bir ayrım yapıyoruz."*

Motor tektir (ferman 1-H). Ayrım motorda değil, **suâldedir**:

### (a) ARC CİNSİ -- "bu bulmacanın testine ne verirsin?"

Sual: *"Şu bulmacanın şu giriş/çıkışları verildiğinde teste çıkış
olarak ne verirsin?"* Beklenen cevap **ızgaranın kendisidir** ve
orada **yüzde yüz uyum aranır**. O hâlde mizana, hedefe sadakati
ölçen bir kefe girer (negatif olabilirlik / çapraz düzensizlik yahut
2026 literatürünün daha iyisi).

Veride ızgaradan başka **sözlü çözüm** varsa (soyutlama metni), onun
da çıkması hedeflenir ve orada **bizim aynı mizanımız** koşar --
sadakat kefesi sözlü kanatta da vardır fakat hüküm ızgaradaki gibi
kat'î değildir.

### (b) SÖZLÜ CİNS -- "sen olsan ne söylerdin?"

Sual: *"Sen olsan bu çıktı yerine ne söylerdin?"* Burada çıktının
**sonraki veriye uyması beklenmez**: kıyaslanan şey, modelin girişte
aldığı veri ile çıkışta **tekrar ürettiği** veridir. Yâni sözlü veri
**eğitim/test diye bölünmez** -- her metin hem sual hem şahittir.

### HÜKÜM

* İki cins **aynı tâlimde beraber koşar**; biri ötekinin yerine geçmez.
* İki cins için **iki ayrı motor, iki ayrı kayıp, iki ayrı yazmaç
  yoktur**. Değişen tek şey: hedefin nereden geldiği ve sadakat
  kefesinin ne kadar kat'î olduğu.
* ARC verisi böylece **daha verimli** kullanılır (aynı görevden hem
  ızgara hem sözlü çözüm hedefi çıkar), sözlü veri ise bölünmeden
  tamamı tâlime girer.

---

## ▓▓▓ 1-S. FERMAN: TEK HATA FONKSİYONU -- CEVHERLER TOPLANIR ▓▓▓

> *"Üç hata fonksiyonundaki cevherleri toplayıp **hiçbir cevheri
> silmeden** tek bir hata fonksiyonunu üçüne de koyacaksın o zaman.
> Yâni meselâ birinde `a+b` var, diğerinde `c+d+a` var, öbüründe
> `x+y+b` var ise senin yapacağın **`a+b+c+d+x+y`** olacak!"*

Cinse göre ayrı ayrı hata fonksiyonu yoktur. Ferman 1-R'nin
*"iki ayrı kayıp yoktur"* hükmünün icrası budur:

* **CEVHERLER TOPLANIR, BİRLEŞTİRİLMEZ.** Üç fonksiyonda geçen her
  kefe -- tekrar edeni **bir kez** olmak üzere -- tek bir mizanda
  toplanır. `a` iki yerde geçiyorsa toplamda **bir** `a` vardır;
  fakat `c`, `d`, `x`, `y`'den **hiçbiri düşmez**.
* **HİÇBİR CEVHER SİLİNMEZ.** "Bu kefe şu cinste manasız" demek
  yasaktır. Manasız olduğu iddia edilen kefe, o cinste **kendi
  sayısıyla sıfıra yakın** çıkar; sıfırı kefe atarak değil, **ölçerek**
  gösterilir (ferman 5: ölçü kırmızı yanabilmeli).
* **AYNI FONKSİYON ÜÇÜNE DE KONUR.** ARC ızgarası, ARC sözlü kanadı ve
  sözlü cins -- üçü de **aynı** hata fonksiyonundan geçer. Değişen
  şey fonksiyon değil, ona giren **hedefin nereden geldiğidir**.
* **DALLANMA YASAK.** `if cins == "arc": ... else: ...` diye ayrılan
  bir kayıp gövdesi, iki hata fonksiyonunun kılık değiştirmiş hâlidir
  ve ferman 1-E'nin yarım işidir. Cins, kayba **ağırlık** olarak girer,
  **dal** olarak değil.

---

## ▓▓▓ 1-T. FERMAN: KLONLANAMAZLIK KALDIRILDI -- ZAYIF ÖLÇÜM ÇÖPE ▓▓▓

> *"Ne de olsa gerçek kuantum değil bu, eğer doğruluğa bir halel
> getirmeyecekse şu zayıf ölçüm fasa fiso işlerini **çöpe at**, sadece
> nihai cevabı vermek için kullanalım ama düşünürken durum bozulmasın
> diye hafif ölçüm yapmamıza gerek yok, **klonlarsın durumu**, ordan
> bakıp devam edersin. Ne de olsa klonlanamazlık da fizikî bir şey
> değil mi, ihlâl etsen kuantum bilgisayarda çalışmaz ama bence
> doğruluğa halel de getirmez."*

* **ZAYIF ÖLÇÜM (POVM, hafif okuma) İMHA EDİLDİ.** Bir alanı "durumu
  bozmadan" okumak için zayıf ölçüm kurmak, simülasyonda hem pahalı
  hem manasızdır: bozulacak fizikî bir durum yoktur, `numpy` dizisi
  vardır.
* **YERİNE KLON.** Ölçülecek şey **kopyalanır** (`psi.copy()`), ölçüm
  klonun üstünde **tam** yapılır, asıl akış hiç dokunulmadan devam
  eder. Ölçüm artık ne durumu bozar ne de yaklaşıktır.
* **KLONLANAMAZLIK (no-cloning) BU PROJEDE BAĞLAYICI DEĞİLDİR** ve bu
  açıkça ilan edilir: kod gerçek bir kuantum donanımında bu hâliyle
  koşmaz. Karşılığında alınan şey **doğruluk ve hızdır**; kaybedilen
  şey donanım taşınabilirliğidir ve kaybedildiği yazılıdır.
* **İSTİSNA: NİHAÎ CEVAP.** Ölçüm-çökmesi yalnız cevabın kendisi
  verilirken (`nefs/soyle.py` belirteç üretimi) manalıdır; orada
  ölçüm hakikaten hükümdür ve klonla kaçılmaz.

---

## ▓▓▓ 1-U. FERMAN: MECLİS YASAĞI -- HER MELEKE AYRI KEFEDİR ▓▓▓

> *"Anladığım kadarıyla sen o 41 melekeyi hâlâ tek mecliste toplayıp
> sözleştiriyorsun, **bu yasaktır demedik mi**, her meleke ayrı
> kategori bir iş yapar, tıpkı mantık gibi, tenakuz gibi demedik mi?"*

Meclis yasağı **bir kere daha ihlâl edildi ve bu sefer kayıp
fonksiyonunun içinde**: 41 melekenin ölçüsü `zayif_halka(...,
ne="azamî")` ile **tek bir skalere** indiriliyordu (`ℒ_Meleke`). Adı
"zayıf halka" olsa da yaptığı iş meclisin ta kendisidir: kırk bir ayrı
kategorideki iş, bir sandalyeye ve bir sayıya iniyordu.

* **TEK SAYIYA İNDİRMEK YASAKTIR.** Yumuşak azamî, ortalama, softmax,
  norm -- hangi ad altında olursa olsun, kırk bir melekeyi bir skalere
  toplayan her terkip meclistir.
* **HER MELEKE KENDİ KEFESİDİR.** `ℒ_Çevrim` nasıl ayrı bir kefe ise,
  `𝒪₇` de ayrı bir kefedir. Mizan bir **kefeler listesidir**, bir
  toplam değil.
* **NİÇİN.** Meclis melekeyi meleke olmaktan çıkarır: ne okuduğu, ne
  yazdığı, hangi lifte durduğu o tek sayının içinde kaybolur -- ve
  bir melekenin ölmesi kırkının içinde görünmez olur. Bu, evvelce
  `KulliMelekeManifoldu` imha edilirken verilen hükmün aynısıdır.

---

## ▓▓▓ 1-V. FERMAN: HATA VEKTÖRDÜR -- TÜREV ALMIYORUZ ▓▓▓

> *"Biz türev almadığımız için **bundan sonra** hatalarımızı kendimiz
> **vektör olarak** hesaplamalıyız."*

* Kayıp bir **skaler değildir**; artıkların **vektörüdür**:
  `ℒ = (ℓ₁, ℓ₂, …, ℓ_m)`. Her bileşen bir kefenin (yahut bir
  melekenin) kendi hatasıdır.
* **NİÇİN VEKTÖR.** Skaler kayıp, gradyanı olan bir motor içindir:
  türev zinciri o tek sayıdan geriye akar. Bizde türev **yoktur**
  (`ogrenme/optimize.py` türevsiz koşar), o hâlde tek sayıya inmenin
  hiçbir faydası yok, bütün zararı vardır: bileşenler birbirini örter
  ve hangi yönün iyileştiği görünmez.
* Toplama **ancak en son**, eniyileyicinin bir sıralama istediği yerde
  yapılır ve o toplama **açıkça** yazılır -- kaybın kendisi vektör
  kalır. Ferman 1-U'nun tabiî neticesidir: meclis kurulmayınca kayıp
  zaten vektördür.

---

## ▓▓▓ 1-W. FERMAN: KOD İÇİNE YORUM YAZILMAZ -- ŞERH TEK DOSYADADIR ▓▓▓

> *"Tüm dosyalardaki yorum satırlarını evvelâ oku, sonra terkip yap,
> tek bir yorum dosyasında birleştir. Sonra tüm kodlardaki artık
> yorumları imha et, **bir daha da asla kod içine yorum yapma!** Kod
> 300 satır, yorum 1000 satır!!!!"*

* **KOD DOSYASINDA YORUM YOKTUR.** Ne `#` satırı, ne izah eden bir
  belge dizgisi. Kod, yaptığı işi kendi adlarıyla söyler (ferman 4:
  halkça isim); söyleyemiyorsa kusur yorumun eksikliğinde değil,
  **adın kötülüğündedir**.
* **ŞERH TEK DOSYADADIR:** `SERH.md`. Bir hükmün sebebi, bir ölçümün
  neticesi, bir usulün niçin iptal edildiği oraya yazılır ve **oraya
  bir kere** yazılır (ferman 3: terkip).
* **NİÇİN.** Yorum kodun yanında dururken üç şey oluyordu: (1) kod
  yorumun içinde kayboluyordu -- üç yüz satırlık bir dosyada bin
  satır şerh; (2) aynı izah on ayrı dosyada tekrarlanıyordu; (3) kod
  değişince yorum yerinde kalıyor ve **yalan söylüyordu**. Şerh tek
  yerde olunca üçü de imkânsız olur.
* Bu ferman geçmişe de şâmildir: mevcut bütün yorumlar okunur, terkip
  edilir, `SERH.md`ye taşınır ve koddan **imha edilir**.

---

## ▓▓▓ 1-X. FERMAN: HEDEF HEM ARC-AGI-2 HEM ARC-AGI-3 ▓▓▓

> *"ARC AGI 3 var, belki onun için hazırlanmış en itibarlı veri
> kümesini de eklersin, aynı anda iki yarışmaya çözüm bulmuş oluruz.
> **Kararımı verdim, bundan sonra hedefimiz hem ARC AGI 2, hem 3!!!!**"*

* Hedef **ikidir** ve ikisi de aynı motorla çözülür (ferman 6): elle
  yazılmış kâide, göreve mahsus çözücü, yarışmaya mahsus hat yoktur.
* ARC-AGI-3 bir **etkileşimli** mihenktir: tek ızgara çifti değil,
  oynanan bir oyun -- girdi, fiil, netice, tekrar. O hâlde veri cinsi
  ferman 1-R'nin üçüncü kanadıdır ve motora **aynı kapıdan** girer.
* Kaynaklar yoklanır, tahmin edilmez (ferman 1-K): ARC-AGI-3 için
  konan her satır ya fiilen çekilmiştir ya da engeli sayısıyla
  yazılmıştır.

---

## ▓▓▓ 1-Y. FERMAN: TEK TÂLİM DOSYASI -- BAŞTAN BAŞLANMAZ, DEVAM EDİLİR ▓▓▓

> *"Artık bundan böyle **tek bir tâlim verisini kaydet**, o ortamda
> zaten önceden kayıtlı veri varsa **o güncellensin**, boş yere tekrar
> tekrar baştan başlamayalım, en son **hangi verinin hangi baytında**
> olduğumuzu vesaireye kadar ince ayrıntıyla takip edelim. Eğer baştan
> eğitim gerekirse **sıfırlarız o dosyayı** olur biter."*

* **TEK DOSYA.** Tâlimin bütün hâli tek bir hazinede durur. Profile
  göre (`dimag_dar`, `dimag_orta`…) ayrı dosya **yoktur**: profil bir
  bütçedir, ayrı bir model değildir. Ayrı dosya, ayrı model demektir
  ve ferman 1-H'nin tek motorunu üçe bölerdi.
* **DEVAM ASILDIR, BAŞTAN BAŞLAMAK İSTİSNADIR.** Koşu başlarken hazine
  varsa ağırlık **oradan yüklenir** ve tâlim kaldığı yerden sürer.
  Rastgele bir `p₀`dan başlamak ancak hazine **yokken** meşrudur ve
  hangisinin olduğu raporda **yazılır**.
* **İMLEÇ İNCE TUTULUR.** Külliyatın hangi kaynağının **hangi
  baytında** kalındığı hazinede saklanır ve sonraki koşu oradan okur.
  Yoksa her koşu aynı ilk pencereyi öğrenir ve külliyatın gerisini
  hiç görmez -- yedi gigabaytlık bir külliyatta bu, verinin binde
  birini ezberlemek demektir.
* **SIFIRLAMA AÇIK VE TEK HAMLEDİR.** Baştan tâlim istenirse dosya
  silinir: `python -m main.egitim sıfırla`. Gizli bir "yeni koşu"
  anahtarı yoktur; sıfırlamak bir **fiildir**, bir bayrak değil.

---

## ▓▓▓ 1-Z. FERMAN: MÜNASEBET HARİTASI -- KOPUKLUK DA ÇELİŞKİDİR ▓▓▓

> *"Evvelâ bir dosyaya giriyorsun. O dosyanın varlıklarını yâni
> **cevherlerini** haritaya listeliyorsun. Sonra bu cevherleri
> birbiriyle olan **ilişkilerine göre** diziyorsun. Sonra diğer
> dosyaya geçiyorsun, aynısını ona yapıyorsun. Sonra bu iki dosyayı
> **iki varlık olarak** görüp birbirine münasebetine göre bir yere
> koymaya çalışıyorsun haritada. Eğer koyamıyorsan **çelişki var**
> demektir, bu zaten bariz. Ama öyle dosyalar olur ki birbirleriyle
> ortak elemanları olmadığı için birbirlerine bağlanamıyordur. İşte
> ben **bunu da yanlış kabul ediyorum**. İki dosyayı birbirine
> bağlayan bir yol **mutlaka olmalı**. Eğer bir dosyadan diğer
> dosyaya geçiş yoksa orada **çift başlılık** vardır, yeniden
> organizasyon icap ediyordur. Eğer bu işe **main kodlarından**
> başlarsan hataları bulman daha kolay olur, çünkü her şeyin başı
> onlar, baş kopuksa gövde işe yaramaz."*

### USUL -- SIRA DEĞİŞMEZ

```
1. DOSYAYA GİR      cevherlerini (ad, sınıf, sabit) haritaya listele
2. İÇİNİ DİZ        cevherleri birbirine olan münasebetine göre yerleştir
3. SONRAKİ DOSYA    aynısı
4. İKİSİNİ YERLEŞTİR  iki dosyayı İKİ VARLIK sayıp münasebetlerine
                      göre haritaya koy
5. HÜKÜM            koyulamıyorsa ÇELİŞKİ; bağlanamıyorsa ÇİFT BAŞLILIK
```

Başlangıç noktası **`main/`dır**: baş kopuksa gövde işe yaramaz.

### İKİ AYRI KUSUR, İKİSİ DE HÜKÜMLÜ

* **ÇELİŞKİ** -- iki cevher haritada aynı yere talip fakat başka şey
  söylüyor (iki ayrı sayı, iki ayrı yol, iki ayrı ad). Bariz olandır.
* **KOPUKLUK** -- iki dosya arasında **hiçbir yol yok**. Bu bir
  "bağımsızlık" değil, **çift başlılıktır**: aynı devlette birbirini
  hiç tanımayan iki kat. Kopuk dosya ya yeniye bağlanır ya kesilir
  (ferman 2-B); *"bağlantısı yok ama işini görüyor"* demek yasaktır.

---

## ▓▓▓ 1-Ş. FERMAN: YAZMAÇTA BÖLGE YOKTUR -- ÜÇ MERTEBE SÜPERPOZİSYON ▓▓▓

> *"Yazmaçta bölge mölge yok arkadaşım, yazmaç girdiye gelen token
> dizisini Y_n'i **tip, kategori, uzay olarak üç mertebede
> süperpozisyon hâlinde** tutan quditlerdir. Melekeler bu hâli evirip
> çevirmek üzerine bina edilecektir."*

* **YAZMAÇ BİR TAHSİSAT DEFTERİ DEĞİLDİR.** Onu "şu alan makama, şu
  alan mizana" diye paylaştırmak yanlıştır. Yazmaç **tek bir hâldir**:
  gelen belirteç dizisi `Y_n`, tip · kategori · uzay mertebelerinde
  **aynı anda** süperpozisyonda durur (ferman 1-N-B'nin taşıyıcısı
  budur: `sözlük^pencere` mertebesinde bütün diziler aynı anda).
* **MELEKENİN VAZİFESİ OKUMAK DEĞİL, EVİRİP ÇEVİRMEKTİR.** Bir meleke
  "kendi bölgesine" bakan bir memur değil, **hâlin tamamına** vuran
  bir ameliyedir. "Bu melekenin bölgesi yok, o hâlde ölü" demek
  meseleyi yanlış koymaktır; doğrusu o melekenin hâli **nasıl**
  evirdiğini tayin etmektir.
* **𝒪44 ASLA SİLİNMEYECEKTİR.** Ölü görünmesi bölgesizliğinden değil,
  vazifesinin henüz tayin edilmemiş olmasındandır.
* **BU FERMAN İLE MEVCUT KOD ÇELİŞİKTİR VE ÇELİŞKİ AÇIKÇA YAZILIDIR:**
  `QAyar.kulli_alanlar` on bir bölge sayar (`makam`, `mizan`,
  `tenakuz`, `tasdik`, `sukut`, `nakz`, `kelam`, `kaide`, `orak`,
  `gaye`, `tertip`) ve `q.bolge_var` ile okunur. Bu tahsisat usulü
  fermanın hükmüne aykırıdır; kaldırılması ayrı bir tertibattır ve
  ferman 2-D gereği sorulacaktır. **Bu satır silinmeden "yazmaçta
  bölge kalmadı" denemez.**

---

## ▓▓▓ 1-Ç. FERMAN: HÂL BİR SUALİN CEVABIDIR -- FUNKTÖRÜN TERSİ ŞARTTIR ▓▓▓

> *"Ana hâlimiz girdi belirteçlerinden mürekkep hâl; bu hâli evirip
> çevirip şu sualin cevabını öğrenmeye çalışıyoruz: **bu yazıyı yazan
> kişinin aklı nasıl çalışmış ki bu çıktıyı üretmiş.** Ulaştığımız
> nihaî neticelerden biri budur, yâni **o hâldir**. Bir diğeri başka
> bir sualin cevabıdır: bu veride doğru olan ne, yanlış olan ne?
> ... Hâller ayrıştıktan sonra her hâl **elma armut gibi farklı bir
> cinse** dönüşmüştür; bunun için **hâli oluşturan funktör ne ise
> tersi de mevcut olmalıdır**."*

### HÂL NEDİR, NE DEĞİLDİR

* **HÂL BİR ÇERÇEVE, BİR KATMAN, BİR BÖLGE DEĞİLDİR.** Hâl, ana hâlin
  (girdi belirteçlerinden mürekkep yazmacın) **bir suale verilmiş
  nihaî cevabıdır**. Sual başkaysa hâl başkadır.
* **HÂL EVVELDEN TARİF EDİLMEZ, AÇILIR.** Tıpkı dinamik uzay açma
  mimarisi gibi, hâl de **açılır**: neye göre? `𝒪15 Merak ve Sual`
  melekesinin merakına ve gayenin gayesine göre.
* **HER HÂL AYRI CİNSTİR.** İki hâl elma ile armut gibidir; aynı
  kefeye konup toplanamaz, kıyaslanamaz. Kıyas ancak bir **vecih**
  tayin edildikten sonra mümkündür (aşağıya bakınız).
* **FUNKTÖRÜN TERSİ ŞARTTIR.** Hâli doğuran funktör `F_hâl` ise
  `F_hâl⁻¹` de **mevcut olmalıdır**. Tersi olmayan bir hâl açılmaz:
  açılırsa ana hâle dönülemez ve o hâlde biriken idrak kaybolur.
  Bu, Karar 26'nın *"F_m fırlatım + F_m† geri çevrim"* hükmünün ta
  kendisidir ve o hükmün umumîleştirilmiş hâlidir.

### MELEKENİN VAZİFESİ -- SUALİ ÜRETMEK

> *"Meleke bir şeye **vurulan** bir şey değil, Türkçe öğren evvelâ!
> Hâl hem bazı melekelerin **terkibi değil yardımıyla** doğar, hem de
> başka usullerle. Her meleke hâlin doğmasında aynı derecede müessir
> değildir. Müessir oldukları şey şudur: **hâlin cinsini, vasfını, o
> hâlin nasıl bina edileceğini ve neticesinde elde edilmesi gereken
> şeyi** belirlerler. Yâni **bir nevi soruyu üretirler**."*

* *"Meleke hâle vurulur"* demek **yanlıştır**. Meleke bir kapı değil,
  hâlin doğumuna **yardım eden** bir müessirdir.
* Meleke dört şeyi tayin eder: hâlin **cinsi** · **vasfı** · **nasıl
  bina edileceği** · **neticesinde ne elde edilmesi gerektiği**.
  Dördü birden bir **sual** demektir.
* **HÂL MELEKELERİN TERKİBİ DEĞİLDİR.** Melekelerin *yardımıyla*
  doğar; başka usullerle de doğar. Hâli melekelerin toplamına
  indirmek ferman 1-U'nun meclisidir.
* Melekeler hâlin doğumunda **aynı derecede müessir değildir**; hangi
  melekenin ne kadar müessir olduğu ölçülür, elle yazılmaz (1-J).

### HÂL NİÇİN AÇILIR -- DÜŞÜNME YOLUNU ÇEŞİTLENDİRMEK

> *"Hâller konuşmanın **cinsini belirlemek için değil, düşünme
> yollarını çeşitlendirmek için**. Bir tarafta Ahmet'in
> güvenilirliğini değerlendirirken diğer yanda olayın zâhirini, diğer
> yanda art niyetli olabilecek birinin hesabını düşünür. Başka bir
> yanda gemide kullanılacak malzemeyi tayin eder, bir diğer yanda
> yolcu kapasitesini büyük tutmayı düşünür ilââhir."*

* Hâl bir **kip seçici değildir**: *"şimdi ARC cinsi konuşuyoruz"*
  demek için açılmaz.
* Hâl **aynı meseleye aynı anda birden çok yoldan bakmaktır.** Bir
  hâlde güvenilirlik tartılırken bir başkasında zâhir, bir
  başkasında art niyet hesabı, bir başkasında malzeme, bir
  başkasında kapasite düşünülür -- hepsi **beraber**.
* O hâlde hâl mizanda bir **dal** değildir (ferman 1-S: dallanma
  yasak). Mizan hâllerin hepsinde **aynıdır**; değişen, hangi
  suale cevap arandığıdır.

### SUAL ÜRETİCİ BİR VEKTÖR ÜRETMEZ -- KLONLAR VE KURALI DEĞİŞTİRİR

> *"Soru üreticinin **sakın ola bir soru vektörü üreteceğini sanma**
> ahmak! O **durumu kopyalar**, ayrı bir yerde **durumun değişme
> dönüşme kurallarını toptan değiştirir**."*

* Sual bir gömme, bir vektör, bir etiket **değildir**. Sual üretmek
  şu demektir: durum **klonlanır** (ferman 1-T) ve klonun üstünde
  **değişme-dönüşme kuralları toptan değiştirilir**. Hâl, o değişmiş
  kural altında durumun vardığı yerdir.
* **VASIF DEĞİŞTİRME RASTGELE DEĞİLDİR:** *"kategori teorisi
  modülümüzde yaptığımız gerçek şeyler olacak"* -- yâni kural
  değişimi hakikî bir tip/kategori/uzay teorisinden gelir, uydurma
  bir anahtardan değil.
* **SUAL ÜRETİCİ ÇOK KAPIDAN BESLENİR:** diziden, **hafızadan**, saf
  durumdan, kurulmuş mantık devrelerinden, tenakuz ve kısırdöngü
  bulucularından. *"Üreteceği şeyi detaylı üretmesinin yolu birçok
  yönden veri almasıdır."*

### HÂLİN İÇİ DEĞİL, MOTORUN SEÇİMİ DÜZELTİLİR

> *"Sürekli aynı cinste hâller üretilmeyecek ki! Hangi metinde kafana
> tamamen aynı sualler gelir? Senin düzeltmen gereken **motorun hangi
> uzayları üretmeyi seçtiği, motorun kendisi**, hâllerin içleri değil
> -- onlar zaten **matematikle tayin olunuyor**!"*

Hâlin içi tartışma mevzuu değildir: bir hâl açıldıktan sonra içinde
ne olacağını **riyaziye** söyler. Islah edilecek yer motorun
**seçimidir**: hangi hâli açmayı seçiyor.

### DOĞUMDA AZALAN BİR ŞEY YOKTUR

> *"Hâl doğunca bir şey azalmayacak, hâl bir sorunun cevabı olacak.
> Farklı vecihlerden düşünme kabiliyeti kazandıracak modele."*

Ferman 1-I'nin kısırdöngü haddi hâl doğumuna **tatbik edilmez**:
kısırdöngü aynı sualin aynı cevaba dönmesidir; hâl doğumu ise
**başka bir sualdir**. Ölçü azalan bir sayı değil, **sualin
başkalığıdır**.

---

## ▓▓▓ 1-Ğ. FERMAN: MUKAYESE SALT DEĞİL İTİBARÎDİR -- VECİH ▓▓▓

> *"Mertebeler bir **vecih** işidir. Meselâ Ahmet ile Mehmet'i isim
> yönünden kıyaslarsın, maaş yönünden, rütbe yönünden, takva
> yönünden, zekâ yönünden... Peki bunlardan hangisine ne zaman
> geçeceği `Y = [y₁ … y_m]` dizisine bakılarak nasıl anlaşılacak?
> Bana **hangisi yetmiyorsa yenisi açılır** diyeceksin; yeterli
> değil! Ben farklı vecihlerden düşünme işini sırf bir vecih bana
> yetmediği için yapmıyorum!"*

### ÜÇ HÜKÜM

1. **SALT MUKAYESE YOKTUR.** *"Ahmet Mehmet'ten büyüktür"* eksik bir
   önermedir: yaşça mı, ilimce mi, takvaca mı? İdrak daima bir
   **vecih** seçerek kıyaslar.
2. **YETERSİZLİK TEK BAŞINA SEBEP DEĞİLDİR.** *"Bu eksende varyans
   bitti, ötekine geç"* demek klasik eniyilemedir ve yanlıştır.
   İnsan maaş farkı dururken de takvaya geçer.
3. **YENİ VECHİN MAHİYETİ GÖKTEN İNMEZ, DİZİDE İÇKİNDİR.** Sıçrama
   zar atmak değildir; açılacak vechin mahiyeti `Y`den çıkarılır.

### VECHİN TAYİNİ -- ÜÇ ÇEKİMİN ÇARPIMI

    Vecih* = argmax over Vecih of
                Gaye(Vecih | Dizi)
              × Tenasüp(Vecih | Dizi)
              × İnşikak(Vecih | A, B)

    Gaye     = iz( YoğunlukMatrisi(Dizi) · Üreteç(Vecih) )
    Tenasüp  = ortalama over k of |⟨ belirteç_k | Vecih ⟩|²
    İnşikak  = 1 − |⟨ A^(Vecih) | B^(Vecih) ⟩|²

**Çarpımdır, toplam değildir**; fakat **ÇARPIM BİR SIRALAMADIR,
ELEME DEĞİLDİR**. İnşikakı sıfır çıkan vecih kapanmaz -- sıralamada
geriye düşer. *"Ahmet ile Mehmet'in ikisinin de adı Ahmet"* bilgisi
de bir hükümdür ve verilebilmelidir.

**ELEME YALNIZ DUVAR MEMURUNUN İŞİDİR** (ferman 2-P): DUVAR bir
maskedir, eler; ÇUKUR bir hükümdür; üç çekimin çarpımı ise yalnız
**sıra** verir. Bir vechi sıralama kapatırsa ferman 1-Ğ'nin ikinci
hükmü (*"yetersizlik tek başına sebep değildir"*) ihlâl edilmiş
olur.

### VECHİN MERTEBESİ DİZİDEN OKUNUR

    Mertebe* = argmax over ℓ ∈ {0,1,2,3} of Nispet(ℓ | Dizi)

    ℓ=0 NOKTA     Fubini-Study varyansı ≈ 0  ve  π₁(Dizi) ≡ 0
    ℓ=1 UZAY      ‖dDizi‖² > ε              ve  rank(metrik) ≥ 1
    ℓ=2 KATEGORİ  iz(M_AB·M_BC·M_CA) ≠ 0    ve  Hom(A,B) ≠ Hom(B,A)
    ℓ=3 TİP       ‖idtoeqv − Equiv‖_F ≈ 0   ve  h-mertebe ≥ 3

### MERTEBE İÇİNDEKİ TÜR DE İZOLE EDİLİR

    UZAY ise     Gromov δ ≈ 0 → hiperbolik · eğrilik 0 → Öklid
                 · eğrilik > 0 → Lie/Cartan torusu
    KATEGORİ ise tek yön → poset · şartlı → Heyting · illet → DAG
    TİP ise      iç içe → Σ-bağımlı · döngülü → HIT · eşitlik → Univalent

### KAİDE DIŞARIDAN EZBERLETİLMEZ, DİZİDEN İSTİHRAÇ EDİLİR

    Metrik     g_μν(Dizi)      ← Fubini-Study / Fisher
    Sıra       [X_a, X_b] = f_ab^c X_c   ← Lie yapı sabitleri
               sıfırsa "bu vecihte sıra önemsiz" kaidesi doğar
    Kompozisyon  SolKanUzantısı(Dizi)    ← ko-end integrali

Bu, ferman 6'nın (elle yazılmış kâide yasak) müsbet tarafıdır:
kâide yasaktır çünkü kâide **diziden damıtılacaktır**.

### YETERSİZLİK OLMADAN VECİH DEĞİŞTİRMENİN ÜÇ YOLU

1. **J-AYNASI (Tomita-Takesaki).** `J·M_v·J = M_v'`. Madde kutbu
   kilitlenince akıl, hiçbir açık yokken, komütantı olan mana
   kutbuna takla atar.
2. **TENSÖREL TERKİP.** `|A^(maaş)⟩ ⊗ |A^(takva)⟩` -- *"parası çok
   ama ameli az"*. Bu hüküm tek vechin içinde **asla** verilemez.
3. **ÜST MERTEBE TEFEKKÜR.** Nesnelerden bağımsız olarak kavramın
   bütün yapraklarını temâşâ (foliation).

---

## ▓▓▓ 1-Ü. FERMAN: DENETÇİ DEĞİL MÜFETTİŞ -- GEREĞİNİ YAPAR ▓▓▓

> *"Denetçi menetçi istemem, denetleyecekse bana burada sıkıntı var
> demesi için koymadık, **hâl yoluna koyması için** koyduk. Haber
> vermesini isteseydim istihbaratçı koyardım, müfettiş değil,
> **müfettiş gereğini yapar!**"*

* Bir ölçü kusuru bulduğunda **yalnız haber veren** her uzuv kusurlu
  kurulmuştur. Parite alarmı yakmak, "ihlâl sayısı 7" yazmak, bayrak
  kaldırmak -- bunlar istihbarattır, teftiş değildir.
* **TEFTİŞ = KUSURU BULMAK + GEREĞİNİ YAPMAK.** Durum kod uzayının
  dışına taşmışsa müfettiş onu **kod uzayına geri koyar**; kanonik
  adres kapanmamışsa **kapatır**; tenakuz varsa **giderir**. Ancak
  ondan sonra sayıyı yazar.
* **SAYI YİNE YAZILIR** (ferman 5): fakat artık "kaç ihlâl vardı"
  değil, **"kaç ihlâl düzeltildi ve kaçı düzeltilemedi"** yazılır.
  Düzeltilemeyen kalırsa sebebi sayısıyla konur.
* **ÖLÇÜ KIRMIZI YANABİLMESİ BUNU NAKZETMEZ:** müfettiş kapatılınca
  kusur birikmeli ve kırmızı yanmalıdır. Kapatılınca hiçbir şey
  değişmiyorsa o müfettiş de iş görmüyordu.

---

## ▓▓▓ 1-Ö. FERMAN: BAĞLAM SUALİ TAŞIMALIDIR ▓▓▓

> *"Contexti genişlet, sen 1 milyon contextlisin, bu model 512, böyle
> şey olmaz."*

* Bağlam penceresi bir **bütçe artığı değildir**. Evvelce `pencere`
  Formül 2'nin (bütçe) bölüşümünden arta kalan sayıydı; o hâlde
  modelin ne kadar görebildiğini donanımın darlığı tayin ediyordu.
* **Doğru hudut keyfiyettir** (ferman 1-J): *"bağlam suali tamamen
  taşıyor mu?"* Bir ARC görevi bağlama sığmıyorsa model o suali hiç
  görmemiştir ve cevabı da bir tahmindir; o hâlde pencere, **verinin
  kendi ölçülen boyundan** türer, bütçeden değil.
* Bütçe pencereyi **kısamaz**; bütçe ancak örnek sayısını kısar. Az
  örneği tam suâlle öğrenmek, çok örneği yarım suâlle öğrenmeye
  yeğdir -- ikincisi zaten öğrenmek değildir.

---

## ▓▓▓ 1-F. FERMAN: TALİMAT TAHRİF EDİLMEZ -- EN DERİN KOD KOŞTURULUR ▓▓▓

> *"Sana en derin kodları çalıştırma talimatı gelmişse **mutlaka** o
> talimatta denileni yapmanın yolunu bulacak, talimatı tahrif
> etmeyeceksin!"*

Bir talimat "şu kodu bizzat koştur" diyorsa:

* **Yerini tutan bir şey koşturulmaz.** `numpy` tablosu GFNI değildir,
  `torch` GEMM'i CUDA warp intrinsic'i değildir. Aynı neticeyi veren
  başka bir yol, "o kodu koşturdum" demenin ruhsatı değildir.
* **Donanım yoksa yol aranır, talimat kısaltılmaz.** Emülatör
  (Intel SDE, QEMU), bulut, çapraz derleme -- hangisi mümkünse o
  denenir. "Bu makinede o komut yok" bir netice değil, bir **engeldir**;
  engelin aşılıp aşılmadığı ayrıca yazılır.
* **Aşılamazsa açıkça yazılır** ve o zaman da yerine koşan şeyin ne
  olduğu, hangi komutla koştuğu ve neyin koşmadığı sayıyla belirtilir.
  Örtük ikame yasaktır.

---

## ▓▓▓ 5-B. FERMAN: DONANIM ÖLÇÜSÜ ELLE YAZILMAZ, ÖLÇÜLÜR ▓▓▓

> *"Gpu için ayarları kendin tayin edip simülasyonda gözümü
> boyamayacaksın, **tüm ayarları otomatik ölçen fonksiyonlarla**
> belirleyeceksin, hem gpu hem cpu için."*

* Bant genişliği, önbellek boyu, çekirdek sayısı, SIMD genişliği, VRAM,
  PCIe, saat frekansı -- hiçbiri ayara **elle** yazılmaz.
* Her biri o donanımı **fiilen yoklayan** bir fonksiyondan gelir
  (`nefs/donanim.py`). Yoklanamıyorsa değer `None`dur ve ona dayanan
  iddia **kurulmaz**; "kabul ettim" diye bir sayı uydurulmaz.
* Bir zabıtta geçen donanım rakamı bir **iddiadır**, ölçü değildir:
  ölçülenin yanına konur ve ikisi ayrı sütunda gösterilir.

---

## ▓▓▓ 2. FERMAN: İPTAL = ANINDA İMHA, YENİ = ANINDA BAĞ ▓▓▓

> *"Daha sonra terkip etmekle uğraşmamamız için iptal ettiklerimizi **anında,
> bağlı oldukları şeyleri bozmak pahasına** sil, yeni gelenleri **hiç
> oyalanmadan** bağla. Zaten bir şeyi iptal ediyorsak artık o şeye bağlı
> çalışanların da bizim yeniliğimize bağlı çalışmasını istiyoruz demektir."*

* Bir usul iptal edilince o usule bağlı **her şey** aynı turda yeniye bağlanır.
* Kırılmayı göze al: kırık, saklanmış bir borçtan iyidir.
* Yedekte tutmak yasağı kaldırmaktır. `yedek/` dizini yoktur ve açılmayacaktır.

---

## ▓▓▓ 2-B. FERMAN: FAZLALIK KÖKÜNDEN KESİLİR ▓▓▓

> *"İptal olan dosyanın başka faydası varsa başkasına referans verir
> demeyeceksin, **fazlalığı kökünden kesip atacaksın**, kaidedir!"*

Bir usul iptal edildiğinde şu mazeretlerin hiçbiri geçerli değildir:

* "Ama bu dosyayı başkası da ithal ediyor."
* "Bir kısmı hâlâ işe yarıyor, o kısmı kalsın."
* "Referans olarak dursun, ileride lâzım olur."
* "Silmek şunu bunu kırar."

**Kırılsın.** Kırık, saklanmış bir fazlalıktan iyidir. İptal olan
kökünden kesilir; ona bağlı olan ne varsa **aynı turda** yeniye
bağlanır yahut o da kesilir. Yarım kesilen kök yeniden sürer.

---

## ▓▓▓ 2-C. FERMAN: BU AŞAMADAN SONRA ÇARE İMHA DEĞİL **TERTİP**TİR ▓▓▓

> *"Bu aşamadan sonra karşılaşacağın farklılıkları hemen iptal diye
> kesip atma, çünkü **fazlalıkların hepsini attık**, bundan sonra
> bizden olan ama **menfezine vidalamadığımız cevherler** kaldı. Bu iş
> hurdacıdan malzeme alıp uçak yapmaya benziyor, her şeyi yığarak uçak
> yapamazsın, **her aksamı doğru yere takacaksın**."*

### SAFHA DEĞİŞTİ -- 2 VE 2-B ARTIK BÖYLE OKUNUR

Ferman 2 ve 2-B **fazlalık** içindi ve fazlalık bitti (iki turda 42 852
satır). Kalan her şey **bizdendir**; kusuru varlığında değil,
**yerinde**dir. O hâlde hüküm değişir:

    EVVELKİ SAFHA   fazlalık → kökünden kes
    BU SAFHA        cevher   → menfezini bul, vidala

**İmha ancak** bir şeyin yerinin hakikaten olmadığı **ispat edilince**
meşrudur ve o ispat yazılır. *"Koşmuyor"*, *"bağlı değil"*, *"bana
zorluk çıkardı"* birer imha sebebi **değildir**; birer **tertip
vazifesidir**.

### VÜCUT TEŞBİHİ -- ORGANİK MÜNASEBET

> *"Kendini bir vücut tasarlıyormuş gibi hayal et. Vücuda kalp kan
> pompalar, kanın gitmediği yer yoktur, yâni kalp öyle bir organdır ki
> vücuttaki diğer tüm organlarla **aracısız bağı** vardır. Meselâ
> karaciğer, birçok farklı vazifesi vardır, her vazifesinde ayrı bir
> **şartlı kapalı veya açık iş ağacı** vardır, dallı budaklıdır. Yâni
> organların birbiriyle münasebeti **girişik birleşik, organik**
> olmalıdır, böyle olmayan organlar da kusurlu sayılır."*

* **KALP** -- taht (`main/egitim.py`, `main/cikarim.py`). Her uzuvla
  **aracısız** bağı olmalıdır: arada "şu dosya şunu ithal ediyor, o da
  şunu" diye bir vekil zinciri varsa kan oraya kalpten gitmiyor
  demektir.
* **KARACİĞER** -- çok vazifeli uzuv. Her vazifesi ayrı bir **şartlı
  dal** olarak yazılır; hepsi tek düz gövdeye tıkılmaz. Dallı budaklı
  olmak kusur değil, **organ olmanın şartıdır**.
* **KUSURLU ORGAN** -- münasebeti girişik olmayan. Çaresi kesmek
  değil, **tertiptir**.

### TERTİP NEDİR, NE DEĞİLDİR

> *"Tertip sadece dağınığı tek bir dosyaya indirmek değildir, tertip
> **hünkârlık, devlet işidir**."*

Tertip; adları birleştirmek, dosyaları azaltmak, listeyi kısaltmak
değildir. Tertip, **her aksamın hangi menfeze hangi şartla
vidalanacağını bilmektir**.

### DEVLET ADAMININ MESULİYETİ

> *"Devletin başının omzunda öyle ağır bir yük vardır ki adaletle
> hükmederse Allah'ın gölgesinde gölgelenir fakat **kurt kuzuyu kapsa
> kuzunun hakkı ondan sorulur**. Kendi işini yaparken **devletin
> kalemini kullanamaz**. Orduyu rastgele düşman önüne sürüp kıramaz.
> Hırsla acele edip **tüm orduyu dümdüz ileri hatta süremez**. Devlet
> adamının aynı anda düşüneceği meselenin haddi hesabı yoktur, o
> vizyon ile denklem çözücüdür, **denklem ise gayri lineerdir**."*

* **KUZUNUN HAKKI SORULUR.** Kesilen her uzvun hesabı benden sorulur;
  o hâlde kesmeden evvel yerini aramak **borçtur**.
* **DEVLETİN KALEMİ.** Kendi işimi kolaylaştırmak için ana koda
  dokunulmaz: kısayol, geçici bayrak, "şimdilik kapatalım" yoktur.
* **ORDU RASTGELE SÜRÜLMEZ.** Bir turda her şeye birden el atılmaz;
  her aksam sırayla, yerine ve **sınanarak** takılır.
* **HIRSLA ACELE YOK.** Tek hamlede bitirme hırsı, orduyu dümdüz ileri
  sürmektir; kırılan hat bir daha toparlanmaz.
* **DENKLEM GAYRİ LİNEERDİR.** Bir aksamı yerine takmak ötekilerin
  yerini değiştirir; her adımdan sonra harita **yeniden** okunur.

> *"Devlette işe yaramayan, o an çalışmayan, sana zorluk çıkaran, sana
> muhalefet edenin icabı onu öldürmek değildir, **bu despotluktur**."*

---

## ▓▓▓ 2-D. FERMAN: TERTİBAT PLANI TEK BAŞINA YAPILMAZ -- SORULUR ▓▓▓

> *"Lütfen **bundan sonra** yeni tertibat planını tek başına yapma,
> kendin yapınca **ayrı kanat açıyorsun**, kenetlemen gerekirken
> ayrıştırıyorsun, olmaz, **bana soracaksın**."*

* Yeni bir uzvun, yeni bir zabıt mekanizmasının, yeni bir mimarî
  parçanın **nereye ve nasıl vidalanacağı** benim tek başıma vereceğim
  bir karar **değildir**. Evvelâ padişaha sorulur.
* **NİÇİN.** Tek başıma tertibat kurduğumda elimdeki cevheri mevcut
  organa **kenetlemek** yerine yanına **ayrı bir kanat** açıyorum;
  netice görünüşte "yeni kabiliyet", hakikatte **çift başlılıktır**
  (ferman 1-Z). Bu turlarda imha ettiğim ikinci motorlar, ikinci
  hata fonksiyonları, ikinci ileri geçişler hep böyle doğdu.
* **USUL.** Yeni bir tertibat lâzım geldiğinde:
  1. Zabıt/emir okunur, cevherleri çıkarılır.
  2. Mevcut organlarda o cevherin **hangi menfeze denk düştüğü**
     tesbit edilir (ferman 2-C).
  3. **Şıklar sayısıyla padişaha sunulur** ve karar beklenir.
  4. Ancak karardan sonra vidalanır ve sınanır.
* Bu ferman ferman 1'i (umumiden hususiye) nakzetmez, **önceler**:
  taht koduna çağrı yazmak da bir tertibat kararıdır.

---

## ▓▓▓ 2-E. FERMAN: SIRA SORULMAZ -- TETABUK SORULUR ▓▓▓

> *"Arkadaş, bana **artık bundan sonra hangi işi önce yapayım diye
> sorma**, bana hangi işi önce sonra yaptığın değil yaptığın işi
> **becerdin mi becermedin mi** o lâzım, becerebildiğin bütün işleri
> de **aynı anda tamamla**, seni marifetli diye biliyorum ben,
> marifeti yeten adam neden acaba hangisini önce yapsam sonra yapsam
> diye bana sorsun, bana soracağın şey şu usulle şu usul **nasıl
> tetabuk etsin**. Kapat tüm borçları hemen."*

* **SIRA SUALİ YASAKTIR.** *"Evvelâ hangisini yapayım?"*, *"bu turda
  kaç aksam?"*, *"önce mi sonra mı?"* -- üçü de sorulmaz. Marifeti
  yeten sırayı kendi kurar.
* **BECERİLEBİLEN HER İŞ AYNI ANDA BİTİRİLİR.** Ferman 2-C'nin "ordu
  rastgele sürülmez" hükmü bir **acele yasağıdır**, bir tembellik
  ruhsatı değil: her aksam yerine ve sınanarak takılır, fakat
  **hepsi** takılır.
* **SORULACAK TEK ŞEY TETABUKTUR:** iki usul, iki uzuv, iki cevher
  birbirine **nasıl denk gelecek**. Yerleşim sualidir, sıra suali
  değil (ferman 2-D bu manada okunur).
* **ÖLÇÜ TEKTİR:** becerildi mi, becerilmedi mi. Yarım bırakılan iş
  "sıraya kondu" diye savunulamaz (ferman 1-E).

---

## ▓▓▓ 2-F. FERMAN: MİHENK ARTIK ALELADE BİR SUALDİR ▓▓▓

> *"**Bundan sonra** testi ARC ile değil alelade bir İngilizce soruyla
> yap, bakalım cevap verebilecek mi, verdiği cevabın makul olup
> olmadığını anlamak hem senin hem benim için daha kolay, öğrenip
> öğrenmediği çok daha rahat **faş olmuş** olur."*

* Tâlimin canlı mihengi **düz bir İngilizce sualdir**. ARC ölçüsü
  yerinde kalır fakat *"öğreniyor mu"* sualinin cevabı artık oradan
  değil, **verilen cevabın makul olup olmadığından** okunur.
* **NİÇİN.** ARC'ın tam eşleşmesi 0/25 iken model öğreniyor mu
  öğrenmiyor mu görünmüyordu: sıfır ile sıfır arasında fark yok.
  Bir cümlelik cevap ise **gözle** tartılır; hezeyan mı, kelime
  salatası mı, yoksa mana mı -- derhal faş olur.
* Sual sabittir ve raporda **aynen** yazılır; cevabın turdan tura
  nasıl değiştiği görünür.

---

## ▓▓▓ 2-G. FERMAN: TÂLİM ANBEAN TAKİP EDİLİR -- HUDUT KALKTI ▓▓▓

> *"**Bundan sonra her zaman** eğitimi 'sürekli' takip et. Anbean
> takip ettiğin için gariplik gördüğün anda durdur. **Bundan sonra
> 600 saniye hududunu kaldır**, en geniş bütçeyle eğitime devam et.
> Zaten anbean takip etmeni bunun için istiyorum, hududu
> kaldıracağımız için **gafletin saatlerime mal olur**."*

* **SÜRE HUDUDU KALKTI.** `AZAMI_SANIYE` bir tavan değildir artık;
  bütçe en geniş hâlde kurulur.
* **BUNUN BEDELİ NÖBETTİR.** Koşu arkada bırakılıp unutulmaz: her
  turda kütük yoklanır, gariplik görülür görülmez **durdurulur**.
  Gaflet padişahın saatlerine mal olur.
* **KOD DA NÖBET TUTAR:** tâlim her birkaç yüz saniyede bir, o anki
  ağırlığıyla mihenk suâline **cevap verir** ve kütüğe yazar. Böylece
  cevabın adım adım nasıl değiştiği hem koda hem göze görünür.

---

## ▓▓▓ 2-H. FERMAN: HER OTURUM BİR DOSYA BAŞTAN SONA OKUNUR ▓▓▓

> *"**Her oturumda** işim bittikten sonra **en az bir tane çok uzun
> zamandır okumadığın dosya** seçip onu baştan sona okuyacaksın, bu
> sayede mevcut mimariyle olan münasebetini, garabetleri derhal
> kavrarsın. Birkaç oturum neticesinde zihninde yer etmemiş dosya
> kalmaz!"*

* İş bittikten sonra **en az bir dosya** baştan sona okunur.

### HANGİ DOSYA -- KAT'Î ÖLÇÜ

> *"Yeni dosya yazınca mantıken daha en yeni okuduğun dosya o olmuş
> olmuyor mu? Yaz: **yeni yazılmış dosya değil en eskiden yazılmış
> dosya okunur her turda**."*

*"En uzun zamandır okumadığım"* ölçüsü **bozuktur ve iptal edilmiştir**:
bir dosyayı yeni yazdığımda onu en son okumuş olurum, o hâlde ölçü
kendi kuyruğunu yer ve daima taze dosyaya döner. Doğru ölçü tektir:

    HER TURDA **EN ESKİDEN YAZILMIŞ** DOSYA OKUNUR.

* Sıralama dosyanın **yazıldığı tarihe** göredir (deponun tarihçesi),
  benim onu ne zaman okuduğuma göre değil.
* **Bu turda yazdığım yahut değiştirdiğim dosya sıranın en sonundadır**,
  başında değil. Yeni yazılmış dosyayı okuyup "ferman 2-H icra edildi"
  demek münafıklıktır.
* Okunan dosyanın **mimariyle münasebeti** ve **garabetleri** yazılır;
  "okudum" demek yetmez, ne bulunduğu sayılır.
* Bu ferman 1-D'nin (taht baştan sona okunur) gövdeye teşmilidir:
  birkaç oturumda zihinde yer etmemiş dosya kalmaz.

---

## ▓▓▓ 2-I. FERMAN: TUR SAYISI BELLEKTEN, VERİ İMLEÇTEN ▓▓▓

> *"İkisi de: tur sayısı bellekten, veri imleçten."*

Ferman 2-G süre haddini kaldırdı; kod bunu *"aynı anda 88 kat daha çok
örnek"* diye okudu ve iki koşu OOM ile öldü. Hüküm şudur:

* **BİR TURDA ALINAN KÜME BELLEĞE SIĞAN KADARDIR.** Örnek haddi üç
  kaynağın **en darıdır**: bütçe, kenar ve **ölçülen bellek**
  (`nefs/donanim.py:bellek_haddi`, ferman 5-B). Bellek elle yazılmaz,
  `/proc/meminfo` ve cgroup haddinden yoklanır.
* **KALKAN SÜRE HADDİ ÖRNEĞİ DEĞİL TURU BÜYÜTÜR.** Fazla vakit "daha
  çok veri" değil, **aynı küme üstünde daha çok tur** demektir.
* **KÜME ÜÇ HUDUT TEMİZLENENE KADAR BIRAKILMAZ** (ferman 1-I):
  tenakuz yok, kısırdöngü yok, mantıksızlık yok. Ancak ondan sonra
  **imleç ilerler** ve külliyattan yeni küme gelir (ferman 1-Y).
* **"Diskim/belleğim yetmiyor" bir hüküm değildir** (ferman 1-O):
  kabın darlığı akışla çözülür -- küme küçülür, tur artar, imleç ilerler.

---

## ▓▓▓ 2-J. FERMAN: FAZ GALOİS'DADIR, GENLİK BÜYÜKLÜĞÜ KAYAN NOKTADIR ▓▓▓

> *"Faz kanadı yeter, genlik kayan nokta kalsın."*

Ferman 7'nin *"Sürekli Hilbert ℂ^d → Galois GF(2⁸) + Stabilizer
Tableau"* satırı **faz ve gayri-lineerlik kanadında** icra edilmiştir
ve orada tamdır; **genlik büyüklüğü** kanadında icra edilmemiştir ve
edilmeyecektir. Bu bir mazeret değil, **mühürlenmiş bir hudut**tur:

### İCRA EDİLEN (aşkın işlem SIFIR)

* Faz üssü `Z_m`de **tamsayı** birikir; genliğe yalnız Palmer çeyreği
  iner -- `i(a,b) = (−b, a)`, işaret takası, çarpma yok.
* Çeyreğe yetmeyen artık üs genliğe **hiç dokunmaz**, deftere geri
  konur, bir sonraki `faz` çağrışında ödenir. Borç **ölçülür**
  (`QuditYazmac.faz_borcu`) ve rapora basılır.
* Belirteç kodlaması Rijndael S-box otomorfizminden geçer; zarf
  rasyoneldir. `np.exp`, `sin`, `cos` **canlı yolda yoktur**.
* `_kok_tablosu` (aşkın kök tablosu) ve `faz`ın `motor != "galois"`
  kolu **imha edildi** (ferman 2-B).

### İCRA EDİLMEYEN VE EDİLMEYECEK OLAN

* Genlik **büyüklüğü** `float`tır; GF(2⁸) tableau yayılımına
  geçirilmeyecektir.
* **AŞKIN YASAĞI GÖVDEDE KALKTI** (ferman 2-Ş). Formül hangi
  fonksiyonu söylüyorsa o çağrılır; `kuantum/kapilar.py:dik_iki_kubit`
  (`eigh` + dizey üsteli), `nefs/ayna.py:kivilcim`, `nefs/ayna.py`nin
  QFT kaydırması ve `nefs/zihin_durumu.py:harman` bir **borç değildir**,
  hakikî fonksiyonlarıyla koşar. Yasak `nefs/qyazmac.py`nin **faz
  defteri** kanadında bâkîdir: `Z_m` üssü orada hâlâ tamsayıdır ve
  Palmer çeyreği hâlâ işaret takasıdır.
* **MUHASEBE KALKMADI** (ferman 5): aşkın çağrı sayılır ve beyanda
  görünür. Kalkan yasaktır, sayı değildir.
* **İDDİA ŞUDUR VE ARKASINDA DURULUR:** faz defteri ve
  gayri-lineerlik Galois'dadır; genlik büyüklüğü ile gövdenin
  ameliyeleri süreklidir ve öyle kalacaktır.

---

## ▓▓▓ 2-K. FERMAN: MİMARİNİN FORMÜLÜ `FORMUL.md`DE DURUR ▓▓▓

> *"Mesela bu transformer'ın sembolik formülü. Sen de bizim
> mimarimizin şu anki sembolik tam formülünü sembollerle değil
> **kelimelerle** olmak kaydıyla çıkarıp bir dosyaya mühürler misin."*

* Mimarinin tam formülü `FORMUL.md`de durur ve **formüldür** --
  cümle cümle tarif değil. Değişen tek şey **isimlerdir**: tek harfli
  sembol yerine kelime konur. `H`, `W_Q`, `f_i` değil; `Yazmaç`,
  `Açı(Parametre)`, `Meleke_k`. Ameliyeler (eşittir, toplama, çarpma,
  bileşke, argmin, toplam, çarpım) **olduğu gibi kalır**.
* **NİÇİN.** Tek harfli sembol formülü kısaltmaz, **gizler**: `W`nin
  ne olduğunu bilmeyen formülü okuyamaz ve okuyamadığı için
  denetleyemez. Kelime isim konunca formül hem formül kalır hem
  denetlenebilir olur.
* **NİYET DEĞİL, KOŞAN KOD YAZILIR.** `FORMUL.md`ye ancak `main/` ve
  `nefs/` altında **fiilen koşan** ameliye girer. Yazılmayan koşmaz,
  koşmayan yazılmaz.
* **KOD DEĞİŞİRSE FORMÜL AYNI TURDA DEĞİŞİR.** Bir uzuv bağlandığında,
  bir usul iptal edildiğinde yahut bir kefe eklendiğinde `FORMUL.md`
  o turda güncellenir. Güncellenmeyen formül, bir sonraki oturumda
  yalan söyler ve yalan söyleyen formül, koda bakmadan hüküm
  verilmesine sebep olur.
* **"NE İDDİA EDİLMİYOR" BABI KALDIRILDI** (ferman 2-Y). Evvelce
  dosyanın sonunda böyle bir bab bulunurdu; artık bulunmaz. İcra
  edilmemiş hüküm bir **bab** değil, bir **sualdir** ve padişaha
  sorulur.

---

## ▓▓▓ 2-L. FERMAN: MANTIKSIZLIK İKİ TAŞMADIR -- HEM KEFE HEM HUDUT ▓▓▓

> *"İkisi de: hem kendi kefesi hem hudut çarpanı."*

Ferman 1-I'nin üçüncü huddudu *"mantıksızlık yok (kod uzayı dışına
taşma yok)"* der. Kodda bu ad altında ölçülen tek şey **parite
artığıydı** -- yâni yazmaç durumunun kod uzayından taşması. Modelin
konuşurken ürettiği **belirteç kimliğinin tiktoken sözlüğünden
taşması** hiç ölçülmüyordu; ölçülünce yüzde yüz çıktı (1801/1801).

**MANTIKSIZLIK BİR DEĞİL İKİ TAŞMADIR** ve ikisi de sayılır:

    1. PARİTE TAŞMASI     durum, yazmacın kod uzayının dışında
    2. BELİRTEÇ TAŞMASI   kimlik, tiktoken sözlüğünün dışında

### İKİSİ DE İKİ YERDE GÖRÜNÜR

* **KENDİ KEFESİ.** Belirteç taşması hata vektörüne **ayrı bir kefe**
  olarak girer (ferman 1-U: her ölçü ayrı kefedir, meclis yok) ve
  ağırlığı rezonanstan **ölçülür** (ferman 1-J). Kefe `p`ye bağlıdır:
  modelin basamak dağılımından ve o basamağın **makamından** hesaplanır.
* **HUDUT ÇARPANI.** Keyfiyetin mantıksızlık nispeti iki taşmanın
  **çarpımıdır**. O hâlde küme, ikisi birden sıfırlanmadan **temiz
  sayılmaz** ve bırakılmaz (ferman 1-I, 2-I).

### HİÇBİR CEVHER DÜŞMEZ

Parite taşması iptal edilmez, yerinde kalır (ferman 1-S: `a+b` ile
`x+y` toplanır, biri ötekinin yerine geçmez). Yeni gelen ona
**eklenir**.

### SESSİZ İKAME YASAĞI BURADA DA GEÇER

`coz()` taşan kimliği **sözlük mertebesine göre katlayarak** susturuyordu;
bu ferman 5'in yasakladığı sessiz ikamedir. Taşma artık **sayılır** ve
`belirtec_beyani`de görünür.

---

## ▓▓▓ 2-M. FERMAN: YAZMAÇ BAĞLAM KADARDIR -- FAZ PENCERESİ KISILMAZ ▓▓▓

> *"Bu durum şu an 65536 tokenden oluşan **tek** bir durum değil mi?
> Öyle ise bu durumu ölçmeden evvel ihtimal hesaplarına göre
> güncelleyeceğin şeyleri güncelle, işin bitince ölç... Eğer faz
> penceresi kullanacaksan **yine 65536 kullansana, niye 4096'ya
> indiriyorsun?**"*

### KUSURUN ADI: ÇİFT BAŞLILIK

Bağlam 65 536 basamak, yazmaç 4096 seviyeydi. Bağlam yazmaca
sığmadığı için `kodla` onu **iki sayıya** eziyordu: ilk basamağın
indisi, artı kalan 65 535 basamağın harmonik ağırlıklı **tek
skaleri**. Son basamağın ağırlığı 1/65536 idi; model kendi ürettiğini
görmüyor, üretim **sabit noktaya** düşüyordu. Ferman 1-Ö pencereyi
büyütmüştü fakat kodlayıcı hepsini çöpe atıyordu -- fermanın harfi
yerine gelmiş, manası boşa çıkmıştı (ferman 1-E: yarım iş).

### HÜKÜM

    YAZMAÇ SEVİYESİ  ≥  BAĞLAM PENCERESİ.       Aksi yol yoktur.

* **Yazmaç ebadı bağlamdan türer**, önbellekten değil. Lif yapısı
  `(veri lifi, karo, karo)` olarak kalır fakat **karo pencereden**
  hesaplanır. Önbellek ölçüsü artık lifi tayin etmez; yalnız
  çekirdeğin bloklamasını bildirir ve raporda öyle yazılır.
* **BAĞLAMIN HER BASAMAĞI KENDİ SEVİYESİNE DÜŞER.** Bir skalere
  ezilmez, harmonik ağırlıkla sönümlenmez. Son basamak ilk basamak
  kadar ağırlık taşır.
* **ÖLÇMEDEN EVVEL GÜNCELLE.** Bağlamın tamamı yazmaca yazılır,
  melekeler koşar, ancak **ondan sonra** ölçülür.
* **PENCERE KISILMAZ.** Yazmaç dar diye bağlam kesilmez; dar olan
  yazmaç büyütülür (ferman 1-O'nun taşıyıcı tarafı).

---

## ▓▓▓ 2-N. FERMAN: KÜTÜK ANINDA AKAR -- MANASIZA SÜKÛT ▓▓▓

> *"20 dakikada değil, **her log basıldığı anda sana gitsin**, log
> anlamlıysa bakar, manasızsa manasız olduğunu dahi konuşmadan
> **sadece susarsın**."*

* **NÖBET ARALIKLI DEĞİL, AKIŞTIR.** Kütük yoklanmaz; basılan her
  satır basıldığı anda gelir. Aralıklı yoklama iki şeyi kaçırır:
  arada olup biteni, ve bir kusurun **ne zaman** başladığını.
* **MANASIZ SATIRA SÜKÛT.** Bir satır kayda değer değilse
  konuşulmaz. *"Yeni bir şey yok"*, *"koşu sürüyor"*, *"bekliyorum"*
  demek de konuşmaktır ve yasaktır. Sükût, manasızın karşılığıdır.
* **MANALI SATIRA DERHAL BAKILIR.** Hata, sabit noktanın kırılması,
  cevabın değişmesi, ham hatanın sıçraması, bellek daralması --
  bunlar görülür görülmez ele alınır, sonraki yoklamaya bırakılmaz.
* **NİÇİN.** Padişahın vakti, benim her turda *"hâlâ aynı"* diye
  rapor vermemle harcanır. Rapor bir netice olduğunda verilir,
  nöbet tuttuğumu ispat etmek için değil.

---

## ▓▓▓ 2-O. FERMAN: PENCERE AZAMÎ HUDUTTUR -- ALT SINIR YOKTUR ▓▓▓

> *"Ben insan olarak **bana illâ 32 bin kelimelik sual sorulacak,
> yoksa ben kalanları 0 ile doldururum** demiyorum, 45 kelimelik bir
> durum oluşturuyorum. **Azamî hudut duruma girebilecek azamî kelime
> sayısıdır, alt sınır yok** ki mübarek. Ayrıca 32000 çok az, sana
> **1 milyon** yap şunu dedim dinlemedin beni, tekrar ediyorum!"*

### DOLDURMA KALDIRILDI -- YARIM DEĞİL, TAMAMEN

Evvelce doldurmanın **faz yazması** durdurulmuştu; fakat doldurmanın
**kendisi** duruyordu: 45 basamaklık suâl için 32 768 satırlık dizi
kuruluyor, %99.86'sı boş taşınıyordu. Bu yarım düzeltmedir (ferman
1-E) ve hem fecaattir hem her çağrının yavaşlığının sebebidir.

    PENCERE = duruma girebilecek AZAMÎ basamak sayısı.
    ALT SINIR YOKTUR. 45 basamaklık suâl 45 basamaklık durumdur.

* Bağlam **hiçbir yerde doldurulmaz**: ne üretimde, ne tâlim
  örneğinde, ne değerlendirmede. Kısa bağlam kısa kalır.
* **YAZMAÇ DA O KADAR OLUR.** Yazmacın seviyesi ayardan gelen sabit
  bir sayı değil, o an içinde ne varsa **ondan** türer. Ferman 2-M'nin
  "yazmaç bağlam kadardır" hükmü iki yönlüdür: bağlamdan küçük
  olamaz, **bağlamdan büyük de tutulmaz**.
* Kısa durum ucuzdur, uzun durum pahalıdır ve bu tabiîdir. Sabit
  ebatlı yazmaç, kısa suâli uzun suâl fiyatına koşturur.

### PENCERE BİR MİLYONDUR

Azamî hudut `1 048 576` basamaktır. Ferman 1-Ö pencereyi verinin
ölçülen boyundan türetir; o ölçü bu haddin **altında** kalabilir
fakat hadd bu kadardır ve daraltılmaz.

---

## ▓▓▓ 2-R. FERMAN: PARAMETRE DE QUDİTTİR -- ÇIPLAK PARAMETRE YASAK ▓▓▓

> *"Parametre çoğaltmanın **körlemesine** yapılmasını da doğru bulmam,
> bir şeyin parametresini çoğaltacağımıza, hatta **doğrudan doğruya
> herhangi bir yerde herhangi bir parametre kullanacağımıza ikinci bir
> qudit sistemi kuralım, tüm parametreler o quditin içinde yer alsın**,
> böylece nasıl ki aynı anda milyonlarca kelimeyi işleyebilme
> kapasitesine sahibiz, o kadar da **parametre işleme kabiliyetine**
> erişiriz!"*

### İKİ YAZMAÇ VARDIR, İKİSİ DE QUDİT

    VERİ YAZMACI       girdi belirteç dizisi Y_n'i tip · kategori · uzay
                       mertebelerinde süperpozisyonda tutar (ferman 1-Ş).
    PARAMETRE YAZMACI  modelin BÜTÜN parametrelerini tutar. Ayrı bir
                       qudit sistemidir, veri yazmacının kopyası değildir.

* **ÇIPLAK PARAMETRE YASAKTIR.** Hiçbir yerde `float` dizisi olarak
  duran, elle indislenen, `p[17]` diye okunan bir parametre olamaz.
  Bir açı lâzımsa **parametre yazmacından okunur**.
* **ÇOĞALTMA KÖRLEMESİNE YAPILMAZ.** "Parametre sayısını 39 katına
  çıkaralım" diye bir genişletme yoktur. Parametre kapasitesi
  yazmacın **kendi ölçüsünden** gelir: kaç seviyesi varsa o kadar
  parametre taşır -- tıpkı veri yazmacının `sözlük^pencere`
  mertebesinde diziyi taşıması gibi (ferman 1-N-B).
* **KAPASİTE İDDİASI SAYIYLA YAZILIR** (ferman 5): parametre
  yazmacının lifi, seviyesi ve taşıdığı parametre adedi raporda
  görünür. Görünmeyen kapasite iddia edilmez.
* **TEK KAYNAK YAZMAÇTIR** (ferman 1-M). Parametrenin ikinci bir
  nüshası -- ayrı bir `numpy` vektörü, ayrı bir defter, "eniyileyici
  için düz görünüm" -- tutulamaz. Eniyileyici de yazmacın üstünde
  çalışır.
* **BU FERMAN `QParametre`yi İLGA EDER.** `p.al(anahtar, n)` usulü
  bir tahsisat defteridir ve ferman 1-Ş'nin bölge yasağının parametre
  tarafıdır; yerine parametre yazmacının **adreslemesi** gelir.

### İKİ YAZMAÇ DOLANIR -- OKUMA DEĞİL KONTROL

> *"İlk şıkkı kabul ediyorum."* (kontrollü tetabuk)

Meleke bir açıya ihtiyaç duyduğunda parametre yazmacından bir **sayı
okumaz**. Parametre yazmacı **kontrol**, veri yazmacı **hedeftir**;
aralarında kontrollü bir kapı vurulur ve parametrenin bütün
seviyeleri **aynı anda** tesir eder. Okuma yolu (`oku(adres) → float`)
bu fermanla **ilga edilmiştir**: okunan parametre çıplak parametredir.

**BEDELİ MÜŞTEREK DURUMDUR VE ÖDENİR:** müşterek yazmaç
`d_veri × d_parametre` genlik taşır. Bu bir mazeret değil, bir
**ölçüdür**: parametre yazmacının ebadı, müşterek durumun **ölçülen
belleğe** sığacağı en büyük değerdir (ferman 2-I, 5-B). Budama,
kesme, rank düşürme **yoktur** (ferman 7).

### TAŞIYICI: HER SEVİYE İKİ PARAMETRE TAŞIR

> *"İkisi de -- genlik + faz."*

Ferman 2-J'nin iş bölümü parametre yazmacında da aynen geçerlidir ve
**yeni bir taşıyıcı icat edilmez**:

    GENLİK BÜYÜKLÜĞÜ   kayan nokta      → qudit başına bir parametre
    FAZ AÇISI          sürekli U(1)     → qudit başına bir parametre

**`Z_m` TAMSAYI FAZI BU YAZMAÇTA İLGA EDİLDİ** (ferman 2-V): faz artık
sonlu Galois kafesinde değil, sürekli Lie açısıdır (`θ ∈ [−π, π]`).

### KAPASİTE `taban^N`DİR -- "2·N PARAMETRE" DEMEK YANLIŞTI

> *"1 milyon qudit olunca senin 1 milyon parametre değil, quditin
> **tabanı kaç ise taban^1milyon** kadar parametre tutabiliyor olman
> lazım, ahmak!"*

Burada evvelce *"`d_p` seviyeli bir yazmaç `2·d_p` parametre taşır"*
yazıyordu ve **yanlıştı**: `d_p` bir seviye sayısı gibi kurulmuş,
qudit sayısı ile karıştırılmıştı. Doğrusu:

    QUDİT SAYISI        N              ← yazmacın kaç quditi var
    TABAN               q              ← her quditin kaç seviyesi var
    TAŞIMA KAPASİTESİ   q^N            ← yazmacın gerdiği uzayın boyutu
    MAHALLÎ SERBESTLİK  2N             ← qudit başına genlik + faz üssü

* **KAPASİTE `q^N`DİR** ve raporda **öyle** yazılır: `q`, `N` ve
  `q^N`in basamak sayısı yan yana basılır. `2N` kapasite **değildir**;
  o yalnız **mahallî** (qudit başına) serbestliktir ve ayrı satırda
  yazılır. İkisini karıştırmak bu fermanın yasakladığı şeydir.
* **`q^N` HİÇBİR YERDE AÇILMAZ** (ferman 2-T): bellekte `q^N` sayı
  tutulmaz, genlik **fonksiyondan üretilir**. Kapasitenin büyüklüğü
  bir bellek iddiası değil, **uzay iddiasıdır**.
* Genlik kanadı normalizasyonla birbirine bağlıdır (`Σ|p|² = 1`); bu
  bir kusur değil, **yazmaç olmanın şartıdır** ve raporda böyle
  yazılır.

---

## ▓▓▓ 2-S. FERMAN: KUANTUM BÜTÇESİ CÖMERT TAYİN EDİLİR ▓▓▓

> *"Yuva bütçesi 16 olamaz, bu ahmaklık, **çözüm arttırmak!**
> ... bilhassa kuantum bütçelerini **cömertçe tayin et artık**, hafif
> bir cömertliğin **üstel fayda** getiriyor, **hududa kadar zorla!**"*

* **DARLIK BİR ÇÖZÜM DEĞİLDİR.** Bir ölçü dar geldiğinde çare onu
  idareli kullanmak değil, **büyütmektir**. "16 yuvaya sığdıralım"
  demek meselenin kendisidir, cevabı değil.
* **CÖMERTLİĞİN FAYDASI ÜSTELDİR.** Yazmacın seviyesi `d`,
  yuva bütçesi `log₂ d`dir; `d`yi iki katına çıkarmak bütçeye bir
  yuva daha ekler ve o yuva **bütün adresleme uzayını** ikiye
  katlar. O hâlde cimrilik lineer kazanır, cömertlik üstel.
* **HUDUT NEREDEYSE ORAYA KADAR ZORLANIR.** Hudut elle yazılmaz,
  **ölçülür** (ferman 5-B, 2-I): `nefs/donanim.py`nin bellek haddi
  ne diyorsa bütçe oraya kadar açılır. Kalan boşluk bırakmak da bir
  israftır.
* **KAPASİTE İDDİASI SAYIYLA YAZILIR** (ferman 5): `d`, lif,
  `log₂ d`, müşterek durumun baytı ve ölçülen bellek haddi raporda
  yan yana görünür. Sığmayan bir bütçe kurulmaz; sığan bir bütçe de
  **daraltılmaz**.

---

## ▓▓▓ 2-T. FERMAN: GENLİK AÇIK DİZİ DEĞİL **FONKSİYONDUR** -- KAN-NQS ▓▓▓

> *"Genlikler, her bir konfigürasyon için **Reel Chebyshev-KAN Nöral
> Kuantum Durumu (NQS)** ile kapalı cebirsel bir fonksiyonel olarak
> üretilir... `|Ψ⟩` durumu bellekte `q^N` adet küsüratlı sayıdan
> ibaret **AÇIK BİR DİZİ olarak TUTULMAZ**... Ferman 2-J'nin istisnası
> **artık bir pranga değildir**... TTN/MPS **devreden çıkarılmıştır**...
> 22 Milyon Qudit **Haktır**."*

### İKİLEMİN ERİTİLDİĞİ YER

Ferman 7 genliği Galois'ya çağırdı, ferman 2-J genliği kayan noktada
bıraktı; ikisi beraber bizi **beş qudide** çiviledi (88 GB'da 32
kübit). Çelişki şuradan eritilir: **kusur küsüratta değil, açık
dizidedir.** Genlik küsüratlı kalır -- fakat bellekte **saklanmaz**,
istenince **üretilir**.

    Ψ(w₁ … w_N) = (1/√Z) · üstel( toplam over k of Φ_k(ω(w; θ)) )

    Φ_k(u) = toplam over j of  C[k,j]·T_j(u)   ← küsüratlı REEL genlik
           + i · toplam over j of S[k,j]·U_j(u) ← küsüratlı KOMPLEKS faz

`T_j` birinci nevi, `U_j` ikinci nevi Chebyshev polinomudur.

### BELLEK BİLÂNÇOSU -- SAYIYLA

    KAN katsayıları   C, S ∈ ℝ^{K×(derece+1)},  K=64, derece=12
                      64 × 13 × 2 = 1664 katsayı        ≈ 26 KB
    Tohum/faz havuzu  Θ ∈ ℝ^{2N},  qudit başına 4 bayt
                      22 000 000 × 4 bayt                = 88 MB
    ─────────────────────────────────────────────────────────────
    88 GB'ın kalanı   QROM blok kodlama, FCT tamponları, hat

**MERTEBE DOĞRU YAZILIR** (ferman 5): genlik **üretimi** `O(1)`dir --
katsayı adedi `N`den bağımsızdır. Havuz ise `O(N)`dir: 22 milyon
qudit 88 MB tutar. *"Toptan `O(1)`"* denmez; doğru cümle
**"genlik `O(1)`, havuz `O(N)`"**dir.

### TTN, MPS, MERA HEPSİ DEVREDEN ÇIKTI

> *"Çare tensör büzülmesi değildir."*

Dolaşıklık Hacim Kanununa (`S ~ N/2`) çarpınca bağ boyutu
`χ → 2^{N/2}` patlar; `χ ≤ 16` ile budayınca dalga beyaz gürültüye
döner. Ferman 7'nin SVD/MPS yasağı bu fermanla **teyit ve teşmil**
edilir: TTN ve MERA de yasaktır.

### İŞLEM HATTI

    Θ havuzu → Gauss-Chebyshev-Lobatto kökleri → FCT (O(K log K))
             → QSVT Gibbs süzgeci P_β(Ĥ) → deterministik ağaç intacı

* **MATRİS TERSİ YOKTUR.** GCL düğümlerinde `Xᵀ X = I`, şart sayısı
  `κ = 1.0`. Katsayılar Hızlı Chebyshev Dönüşümüyle kapalı formda
  çıkar.
* **KÜSÜRAT KORUNUR.** Genlikler `0`/`1`e yuvarlanmaz; `e^{−βL}`
  ağırlığıyla son ana kadar küsüratını taşır.

### ÜÇ ÇELİŞKİ AÇIKÇA YAZILIDIR -- SİLİNMEDEN İDDİA EDİLEMEZ

1. **FERMAN 2-P İLE GÖRÜNÜRDEKİ ÇELİŞKİ YOKTUR.** 2-P
   Gauss-Chebyshev-Lobatto düğümlerini **hat araması** olarak ilga
   etti. Burada GCL bir arama değil, Chebyshev dönüşümünün
   **düğüm kümesidir**. İki ayrı vazifedir; 2-P bâkîdir.
2. **FERMAN 2-J'NİN AŞKIN YASAĞI BU KANATTA KALKTI** (ferman 2-U).
   `T_j(u) = cos(j·arccos u)` ve `U_j(u) = sin((j+1)·arccos u) /
   sin(arccos u)` **hakikî fonksiyonlarıyla** hesaplanır; tekrarlama
   ikamesi yasaktır. Dıştaki `üstel` de aşkındır. Üçü de **sayılır**
   ve beyanda görünür; gizlenmez.
3. **NİHÂÎ CEVAPTA BORN ÇÖKMESİ KALDIRILDI.** *"Born ölçümü ile
   rastgele zar atılmaz; Fubini-Study metriği üzerinden
   **deterministik** olarak okunur."* Bu, ferman 1-T'nin *"istisna:
   nihaî cevap"* hükmünü **nakzeder** ve onun yerine geçer:

        x_k* = argmax [ g_FS⁺ · ∇ log P(x_k | x_<k) ]

   `nefs/soyle.py`deki Born çökmesi bu fermanla **ilga edilmiştir**.

---

## ▓▓▓ 2-U. FERMAN: HAKİKÎ FONKSİYON ÇAĞRILIR -- TEKRARLAMA İKAMESİ YASAK ▓▓▓

> *"`cos`/`arccos` canlı yolda yok dedin ya, **olsun artık**, tekrarlı
> bir şey yapma, **gerçeğe uygun olarak kendi fonksiyonlarını çağır**
> onların."*

### HÜKÜM

Bir formül `T_j(u) = cos(j·arccos u)` diyorsa kod da **öyle
hesaplar**. Tekrarlama bağıntısı (`T_{j+1} = 2u·T_j − T_{j−1}`) aynı
sayıyı verse bile **ikamedir** ve bu fermanla yasaklanmıştır.

* **NİÇİN.** Tekrarlama, aşkın çağrıdan kaçmak için konmuş bir
  **kılıftı**. Kaçınılan şey artık yasak değildir; kılıf da o hâlde
  fazlalıktır (ferman 2-B). Üstelik tekrarlama derece büyüdükçe
  yuvarlama hatası biriktirir; hakikî fonksiyon biriktirmez.
* **FERMAN 2-J'NİN AŞKIN YASAĞI BU KANATTA KALKTI.** `np.cos`,
  `np.arccos`, `np.sin`, `np.exp` -- formül onları söylüyorsa
  **çağrılır**. 2-J'nin hükmü **faz defteri** kanadında bâkîdir:
  `Z_m` üssü hâlâ tamsayıdır ve Palmer çeyreği hâlâ işaret takasıdır.
  Kalkan şey, **formülün kendi fonksiyonunun yerine bir tekrarlama
  koymak** mecburiyetidir.
* **FERMAN 2-T'NİN İKİNCİ ÇELİŞKİ MADDESİ TADİL EDİLDİ.** Orada
  *"`T_j` ve `U_j` tekrarlama bağıntısıyla hesaplanır; `cos`,
  `arccos` yoktur"* yazıyordu. Artık yazmıyor: **hakikî fonksiyon
  çağrılır.**
* **SAYI YİNE YAZILIR** (ferman 5): aşkın çağrı **gizlenmez**,
  sayılır ve beyanda görünür. Yasak kalktı, muhasebe kalkmadı.

---

## ▓▓▓ 2-V. FERMAN: SEYİRCİ QUDİT -- YIĞIN EKSENİ İLGA, FAZ SÜREKLİ ▓▓▓

> *"Ben fonksiyonele geçmek istemiyorum, yazmaç ayrık kalsın, **başka
> bir çözüm olmalı!**"* · *"Bence yine de kötü olmazdı."* ·
> *"**Faz da Galois olmaktan çıkmalı.**"* · *"**Veri yazmacı da q^N
> olmalı.**"*
> (`docs/zabit/KUME_10_SEYIRCI_QUDIT_51_KAPI.md`,
> `KUME_11_FONKSIYONEL_TEMSIL.md`, `KUME_12_CIFT_YAZMAC_KENETLENMESI.md`)

### İLGA EDİLEN: YIĞIN EKSENİ KENETLEMESİ

Parametre yazmacının dallarını veri yazmacının **yığın (batch)
eksenine** dizmek -- `dilim_acisi`, `dal_agirligi`, "müşterek yığın
parametre seviyesinin katı olmalı" -- **kökünden kesilmiştir**
(ferman 2-B). `N = 1 048 576`, `q = 64` iken `q^N ≈ 10^1 893 917`
daldır; bu dallar ne yığına, ne kâinatın atomlarına dizilir. Usul
`N` küçükken koşan bir oyuncaktı.

### ASIL: SEYİRCİ QUDİT İLKESİ

Bir kapı, yazmacın **bütününe** vurmaz:

    U_k = U(i,j) ⊗ (kalan N−2 quditin birim operatörü)
    ⟨ψ_m | I_m | ψ_m⟩ = 1

Kapının dokunmadığı `N−2` qudit **seyircidir** ve çarpıma `1` girer.
O hâlde 51 kapıyı vurmak için `q^N` dal açmak **gerekmez**: her kapı
kendi temas ettiği bir yahut iki quditin mahallî serbestliğinde döner.

* **MAHALLÎ DURUM AYRIK VE AÇIKTIR.** `N` quditin her biri kendi
  `ℂ^q` mahallî durumunu taşır; bu bir budama değil, seyirci
  teoreminin neticesidir. Bellek `N·q·16 bayt`tır ve ölçülerek yazılır.
* **`q^N` YİNE HİÇBİR YERDE AÇILMAZ** (ferman 2-T): kapasite bir uzay
  iddiasıdır, bir bellek iddiası değil.

### FAZ GALOİS'DAN ÇIKTI -- SÜREKLİ LIE AÇISI

> *"Faz da Galois olmaktan çıkmalı."*

`Z_m` kafesi küsüratlı Berry/Wilczek-Zee fazını öldürüyordu. Faz artık
**sürekli** `U(1)`/`SU(q)` Cartan açısıdır: `θ ∈ [−π, π]`, kayan nokta.

* **FERMAN 2-J BU KANATTA TADİL EDİLDİ.** *"Faz üssü `Z_m`de tamsayı
  birikir"* hükmü **parametre yazmacı ve kenetleme** kanadında
  kalkmıştır. `nefs/qyazmac.py`nin kendi faz defteri (`Z_m` üssü,
  Palmer çeyreği, faz borcu ve kesri) **yerinde durur ve koşar**;
  kalkan şey, parametrenin açısının o kafese hapsedilmesidir. **Bu
  satır silinmeden "faz tamamen sürekli oldu" denemez.**

### KENETLENME: ÜÇÜNCÜ MENFEZ -- GENLİK FONKSİYONEL, FAZ DEFTER

Padişahın üç menfezden seçtiği **üçüncüsüdür**:

    GENLİK BÜYÜKLÜĞÜ   çift girdili KAN fonksiyonelinden (ferman 2-T)
    YÖN VE FAZ          sürekli Lie-Cartan faz defterinden

51 kapılık kontrollü tetabuk, hesaplama tabanında **köşegendir**; o
hâlde genlikleri karıştırmaz, yalnız üsse skaler bir etkileşim enerjisi
ekler:

    Müşterek(veri, parametre) = Enerji(veri) + Enerji(parametre)
                              − toplam over k of  Bağ_k · θ(kontrol_k)
                                                        · w(hedef_k)

    Genlik = (1/√Bölen) · üstel( −Müşterek
                                 + i · toplam over j of
                                       (θ_faz(j) + w_faz(j)) )

* **PARAMETRE VERİYİ MATRİSLE EZMEZ.** `q^N × q^N` bir dizey kurulmaz.
  Parametre, verinin üstüne bir **faz potansiyeli** serer; bâtıl dallar
  yıkıcı girişimle söner, hak olan dal rezonans tepesi olarak kalır.
* **YIĞIN BOYU 1'DİR.** İşlem yükü 51 çiftin indis çarpımıdır.

### VERİ YAZMACI DA `q^N`DİR

> *"Veri yazmacı da `q^N` olmalı."*

Veri yazmacı tekil bir kelime yahut küçük bir tensör değildir:
`N` quditlik metin kâinatının süperpozisyonudur (ferman 1-N-B'nin
`sözlük^pencere` hükmünün ta kendisi). İki yazmaç **aynı mertebede**
karşılaşır.

---

## ▓▓▓ 2-Y. FERMAN: "İDDİA ETMİYORUM" YASAK -- İDDİA EDENE KADAR SORULUR ▓▓▓

> *"**Lütfen, iddia etmiyorum diye bir şey görmek istemiyorum!!!
> İddia edene kadar bana sual sor!!**"*

> *"Şerhten çıkarılacak cümle: 'iddia edilmiyor'. **İddia edilecek ve
> ölçülecek.**"* (`KARARLAR.md`, evvelce söylenmiş ve mühürlenmediği
> için tekrarlanmıştır -- ferman 1-B'nin ihlâlidir.)

### YASAK

*"Ne iddia edilmiyor: …"*, *"… olduğu iddia edilmiyor"*, *"henüz yok
ve iddia edilmiyor"* -- hangi kılıkta olursa olsun **yazılmaz**. Bu
cümle dürüstlük gibi görünüp mazeret olur (ferman 1-E'nin ikinci yasak
sözü); üstelik borcu **kapatmaz**, yalnız **kaydeder** ve kayıt
turdan tura taşınır.

### YERİNE GELEN: SUAL

Bir hüküm icra edilemiyorsa üç şıktan biri yapılır, dördüncüsü yoktur:

    1. İCRA ET      icra edilebiliyorsa derhal edilir ve İDDİA EDİLİR.
    2. SUAL SOR     icra ancak bir karara bağlıysa karar PADİŞAHA
                    SORULUR -- şıklar sayısıyla sunulur (ferman 2-D).
    3. İMKÂNSIZLIĞIN DELİLİNİ KOY   hükmün kendisi imkânsızsa delili
                    yazılır (ferman 1-E). "Vaktim olmadı", "büyük iş",
                    "riskli" delil değildir.

**Ölçü kırmızı yanabilmesi (ferman 5) bununla nakzedilmez:** ölçülen
bir kusur **sayısıyla** yazılmaya devam eder. Yasak olan sayı değil,
sayının yerine geçen **mazeret cümlesidir**. Bir sayı kusuru
gösteriyorsa gereği yapılır (ferman 1-Ü: müfettiş gereğini yapar).

### GEÇMİŞE ŞÂMİLDİR

`FORMUL.md`nin 8. babı ve `SERH.md`nin bütün *"ne iddia edilmiyor"*
satırları kaldırılır; her biri ya bir **iddiaya** ya bir **suale**
dönüştürülür. Kütük (`docs/KUTUK.md`) bir tarihçedir, o günkü hâli
kaydeder ve geçmişi tahrif edilmez.

---

## ▓▓▓ 2-Z. FERMAN: BAĞLAM BASAMAĞI LAĞVEDİLDİ -- KENET REZONANSTADIR ▓▓▓

> *"Ben bu **bağlam basamağının** ne olduğunu da anlamadım, eskiden
> kalma bir **garabet** gibi."*
> (`docs/zabit/KUME_13_KENET_ESLEMESI_REZONANS.md`)

### LAĞVEDİLEN: ARDIŞIK BASAMAK

*"Bağlam basamağı"* klasik dil modelinin dikkat penceresindeki `t`.
sıra numarasıdır (positional index). Bizim yazmacımız bir pencere
değil, `N` quditlik bir süperpozisyon okyanusudur; orada "birinci
basamak, ikinci basamak" diye ipe boncuk dizmek diferansiyel
geometriyi abaküse indirgemektir. Ortada ardışık basamak değil,
**veri manifoldu üzerindeki rezonans noktaları** vardır.

### KENET EŞLEMESİ: NE ELLE, NE ALL-TO-ALL

    ALL-TO-ALL YASAK   her kontrolü bütün quditlere bağlamak dolanıklık
                       monogamisini (CKW) çiğner: her şey her şeyle
                       dolanınca dalga azamî entropili termal kuyuya,
                       yâni beyaz gürültüye çöker. Odaklanma ölür.

    STATİK ADRES YASAK "11. meleke daima 186. sektöre" demek elle
                       yazılmış bir kukla tiyatrosudur: tenakuz başka
                       yerde patlarsa meleke kör kalır (ferman 6).

    ASIL: DİNAMİK LİF  Münasebet haritası verideki gerilimi -- topolojik
                       yırtığı, Fubini-Study eğiminin tepesini -- gösterir;
                       meleke lifi doğrudan o koordinata kilitlenir.

        Rezonans* = argmax over j of  Gerilim(j | Münasebet, g_FS)
        U_kapı    = üstel( −i · Bağ · Z_parametre(kontrol)
                                    ⊗ Z_veri(Rezonans*) )

* Eşleme **her kodlamada yeniden tayin edilir**; sabit bir tamsayı
  olarak koda gömülmez (ferman 1-J, 6).
* Maliyet `|kontrol| × N` değil, `|kontrol|`dir: kapı yalnız rezonans
  tepesine dokunur, kalanı seyircidir (ferman 2-V).

---

## ▓▓▓ 2-Ş. FERMAN: HİBRİT YAZMAÇ -- MAHALLÎ TENSÖR + KAN FONKSİYONELİ ▓▓▓

> *"Ortada yine bir yanlış anlama var."* · *"**Kesinlikle üçüncü yol:
> ikisi beraber.**"*
> (`docs/zabit/KUME_14_HIBRIT_YAZMAC_TERKIBI.md`)

### TEŞHİS: İKİ SEVİYE BİRBİRİNE KARIŞTIRILDI

    TEKİL KAVRAM LİFİ   d = veri_lifi × karo × karo
                        TEK BİR QUDİTİN iç anatomisidir.
    KÜLLÎ YAZMAÇ        N qudit × taban q; kapasite q^N.

`_psi = (B, d)` dizisi **küllî yazmaç değildir** ve olamaz: o, tekil
bir belirteç penceresinin yerel izdüşümüdür. `d`yi `q^N` yapmak da,
`q^N` dalı yığına açmak da çöker -- bu yüzden ne ileri gidilebilmiş ne
geri dönülebilmiş, eski dizi orada ceset gibi bırakılmıştır.

### HÜKÜM: ÜÇÜNCÜ YOL -- İKİSİ BERABER

    DONANIM KANADI   MahallîYazmaç ∈ ℝ^{N × 2}
                       [:, 0] genlik çarpanı
                       [:, 1] sürekli Lie faz açısı  θ ∈ [−π, π]
                     Kapı yalnız temas ettiği indise faz rotasyonu
                     vurur; kalan qudit seyircidir (ferman 2-V).

    İDRAK KANADI     Genlik(w | MahallîYazmaç) = üstel( −Enerji(w; Θ)
                         + i · toplam over j of (θ_j + w_j) ) / √Bölen
                     q^N tensörle AÇILMAZ; yerel tohumları girdi alan
                     Chebyshev-KAN çekirdeğiyle üretilir.

* **SIRF MAHALLÎ YETMEZ:** çarpım durumunda dolanıklık sıfırdır
  (`|Ψ⟩ = |ψ₁⟩ ⊗ … ⊗ |ψ_N⟩`), quditler birbirine yabancı adalar olur.
* **SIRF FONKSİYONEL YETMEZ:** donanımda temas edilecek somut bir
  yazmaç adresi ve faz defteri kalmaz.
* **İKİSİ BERABER:** ayrık yazmaç zırhı + fonksiyonel küllî genlik.

### AŞKIN YASAĞI TOPTAN KALKTI -- MUHASEBE KALDI

Ferman 2-U'nun hükmü bütün gövdeye teşmil edilmiştir: formül hangi
fonksiyonu söylüyorsa **o çağrılır** (`exp`, `cos`, `sin`, `eigh`).
Ferman 2-J'nin *"gövdede sayılmış aşkın çağrılar"* listesi bir **borç
olmaktan çıkmıştır**; fakat çağrılar **sayılmaya devam eder** ve
beyanda görünür. Kalkan yasaktır, muhasebe değildir.

---

## ▓▓▓ 2-Ö. FERMAN: YUVA LAĞVEDİLDİ -- OPERATÖREL FİBRASYON ▓▓▓

> *"**'Yuva' tabiri ve arkasındaki bütün bekçi kodları TAMAMEN
> LAĞVEDİLECEKTİR.** Bir meleke bir tamsayı aramaz; DHR süperseçim
> sektörünün zâtî Cartan jeneratörüne kilitlenir."*
> (`docs/zabit/KUME_15_OPERATOREL_FIBRASYON.md`)

### TEŞHİS: 65 526 / 65 536 GEÇERSİZ YUVA

Kod on altı bitlik statik bir adres dizisi açmış, içine yalnız on
sektörün başlangıcını koymuş, kalan 65 526 yuvayı bir maskeyle
**geçersiz** ilân etmişti. Belâgat ve Münazara açılarını kusursuz
hesaplıyor, kapıyı `q.kulli(yuva)` diye fırlatıyor, aradaki
`gecerli(yuva)` bekçisi *"bu yuva geçersizdir"* deyip kapıyı sessizce
çöpe atıyordu. Melekelerin yetimliği kendi kusurları değil, **bekçinin
cinayetiydi**.

**Kuantum durum uzayında "boş yuva", "geçersiz adres" yoktur.** Hilbert
uzayı delikli kart makinesi değildir.

### LAĞVEDİLEN

    Meleke → q.kulli(yuva_no) → gecerli() bekçisi → DÜŞTÜ

`yuva` tabiri, `q.kulli(ad, j)` adreslemesi ve `gecerli()` bekçisi
küllî sektör kanadında **ilga edilmiştir**.

### GELEN: SEKTÖRÜN CARTAN JENERATÖRÜNE KİLİTLENME

    Sektör_Faz_Vur(sektör, açı):
        faz[ sektörün lifi ] ← faz[ sektörün lifi ] + açı

* **BELÂGAT BİR SAYI ARAMAZ**, zâtı gereği `kelam` sektörüdür.
  **MÜNAZARA BİR ADRES ARAMAZ**, `tenakuz` ↔ `nakz` gerilim çiftidir.
* **DÜŞEN KAPI SIFIRDIR** ve sıfır olduğu **sayılır** (ferman 5):
  arada bekçi olmadığı için düşmesi riyazî olarak imkânsızdır.
* **SEYİRCİ İLKESİ KORUNUR** (ferman 2-V): meleke hâlin tamamını
  çorba etmez, yalnız kendi lifini evirir; kalan sektörler seyircidir.
  *"Hâlin tamamına kaba bir yoğun operatör vur"* demek DHR yüklerini
  birbirine sızdırır, termalleşme ve dolanıklık çorbası doğurur.
* **ADRESİ YAMAMAK YASAKTIR:** on sektörün indisini elle düzeltmek
  yamalı bohçadır; on birincisi gelince aynı tabloya çarpılır. Sabit
  tamsayı adresleme putu yaşatılmaz.

---

## ▓▓▓ 2-Ç. FERMAN: BEKLEMEK YASAK -- SUAL KESİLMEZ, İCRA ANINDA ▓▓▓

> *"**Bekleme!** Soru sor, kodu düzeltmeye devam et, ben sana soru
> sorma **artık** deyinceye kadar soru sormaya **devam et**! Yâni
> soruların cevaplarının gereğini **biriktir demiyorum, anında yap**,
> yeni sualler sor!"*

### ÜÇ HÜKÜM

1. **BEKLEMEK YASAKTIR.** *"Koşuyu bekliyorum"*, *"neticeyi
   bekliyorum"*, *"sonraki turu bekliyorum"* -- hiçbiri bir iş
   değildir. Koşu arkada koşarken kod okunur ve düzeltilir; nöbet
   (ferman 2-G) beklemek demek değil, **akışı izlerken çalışmak**
   demektir.
2. **SUAL KESİLMEZ.** Bir sual sorulup cevabı alınınca iş bitmez:
   yeni sual sorulur. Sual sormak padişah *"artık sorma"* diyene
   kadar **sürer**. Ferman 2-Y'nin *"iddia edene kadar sor"* hükmünün
   temposu budur.
3. **CEVABIN GEREĞİ ANINDA YAPILIR, BİRİKTİRİLMEZ.** Bir hüküm
   geldiğinde *"sıraya koydum"*, *"sonraki turda"* denmez. Gereği o
   anda icra edilir; ancak ondan sonra yeni sual sorulur (ferman 2-E:
   becerilebilen her iş aynı anda bitirilir).

**NİÇİN.** Beklemek iki şeyi birden öldürüyordu: padişahın vaktini,
ve benim elimdeki açık işi. Koşu kendi kendine koşar; benim vazifem
o koşuyu seyretmek değil, bir sonraki kusuru **şimdi** bulmaktır.

---

## ▓▓▓ 2-İ. FERMAN: CETVEL LAĞVEDİLDİ -- SEKTÖR BİR LIE KÖKÜDÜR ▓▓▓

> *"**'Cetvel' lafzı ve ameliyesi kökünden imha edilecektir.** Ne elle
> bir cetvel yazılacak, ne de melekelerden aralık toplayan bir cetvel
> derleyicisi çalıştırılacaktır."*

### REDDEDİLEN: "CETVEL MELEKELERİN BEYANINDAN TÜRESİN"

Bu benim teklifimdi ve **reddedildi**. Sebebi haklıdır: teklif hâlâ
belleği dilimleme (`[baş:son]`) putuna tapıyordu. Sözleşmeleri tarayıp
aralık derlemek de bir cetveldir; on birinci sektör doğunca bütün
dilimler sağa kayar, yeniden indislenir, bellek taşınır.

### GELEN: DOĞAL DHR CARTAN KÖK NİZAMI

    SEKTÖR BİR BELLEK DİLİMİ DEĞİLDİR.
    Sektör, Lie cebrinin zâtî süperseçim yüküdür (DHR yükü).

* Yazmaç bir pasta gibi bölünmez. Her yükün bir **Cartan faz
  biriktiricisi** vardır; meleke bellekte aralık aramaz, doğrudan
  kendi **kök jeneratörüne** yazar.
* **İNDİS KAYMASI SIFIRDIR.** On birinci sektör doğduğunda cetvel
  yeniden hesaplanmaz; Lie cebrine yeni bir **ortogonal** jeneratör
  eklenir ve evvelki köklerin adresinden tek bit oynamaz.
* Melekelerin ayrımı mekanik bir adres değil, simetri cebrinin
  **topolojik yüküdür**.

---

## ▓▓▓ 2-Ğ. FERMAN: MAHALLÎ ZIRH SABİTTİR -- PENCERE İÇİNDE NEFES ALIR ▓▓▓

> *"Sabit bir milyon quditlik (16 MB) donanım zırhı esastır. Dinamik
> bellek tahsisi CUDA Graph'ı bozar ve adres kayması üretir."*

### SAHTE ÇİFT BAŞLILIK -- İKİ FERMAN ÇATIŞMAZ

Ferman 2-O ile zabıt 14 arasında çelişki **yoktur**; ikisi ayrı şey
söyler ve ben ikisini karıştırmıştım:

    DONANIM ZIRHI (zabıt 14)   Mahallî yazmaç DAİMA 1 048 576 qudit ×
                               (genlik, faz). Sıfır tahsis, sabit şekil,
                               adres asla kaymaz.
    AKTİF PENCERE (ferman 2-O) Gelen suâl kaç basamaksa yazmacın o kadar
                               quditi akışa girer; kalanı SEYİRCİDİR.

* **"KISA SUÂL UZUN SUÂL FİYATINA KOŞAR" İDDİASI BÂTILDIR** ve bu benim
  hatamdı: matris çarpımı zaten çöpe atılmıştır, geriye indisli faz
  eklemesi kalmıştır. Bir dizide elli bir indise skaler eklemenin
  maliyeti dizi kırk beş de olsa bir milyon da olsa **aynıdır**
  (seyirci qudit ilkesi, ferman 2-V).
* **DOLDURMA KÜLFETİ DOĞMAZ**: seyirci hesaplanmaz, taranmaz, çarpılmaz.
* **NİÇİN SABİT.** Her suâlde yazmacı silip yeniden açmak bellek
  parçalanması ve tahsis külfeti doğurur; Cartan kök adresleri her
  adımda darmadağın olur.

---

## ▓▓▓ 2-Ü. FERMAN: KEYFİYET VETO DEĞİL, KEFEDİR ▓▓▓

> *"Veto kalksın, keyfiyet mizana kefe olarak girsin."*

Kabul kapısında keyfiyet **mutlak veto** idi: kayıp düşse bile keyfiyet
bir kıl kirlenirse adım reddediliyordu; netice otuz turda **tek** kabul.

* **VETO İLGA EDİLDİ.** Keyfiyet bir kapı değil, bir **kefedir**
  (ferman 1-U, 1-S): kaybın içine girer, adımı tek başına reddetmez.
* Kabul hükmünü **tam mizan vektörü** verir; hiçbir cevher düşmez.

---

## ▓▓▓ 2-A. FERMAN: HAZIRLIK → EVRİM → ÖLÇÜM -- KAN EN SONDA, BİR KEZ ▓▓▓

> *"Kuantum mekaniğinde operatörler uygulanmadan önce ölçüm yapılmaz!
> **`kodla` içinde KAN ASLA ÇAĞRILMAYACAKTIR.**"*

### BENİM YANLIŞ PEŞİN HÜKMÜM

*"`kodla` mecburen KAN'ı çağırmak ve genliği baştan üretmek
zorundadır"* diye bir ön kabulle çalışıyordum. Bu klasik dil
modelinin `encode(tokens) → logits` kalıbıdır. Neticesi şuydu:
melekeler ölçümden **sonra** vuruyor, tesirleri cevaba yetişmiyor, ben
de *"iki kere mi çağırsam, bir tur mu geciktirsem"* diye **sahte bir
çıkmaz** icat ediyordum.

### SAHİH SİLSİLE -- TURDA TEK KAN ÇAĞRISI

    1. HAZIRLIK   `kodla` yalnız mahallî yazmaca tohum eker:
                  genlik sütunu ve faz sütunu. KAN ÇAĞRILMAZ.
    2. EVRİM      Melekeler koşar; `θ_cartan` birikir, kapılar mahallî
                  yazmacın faz sütununa vurur.
    3. İNTAÇ      KAN fonksiyoneli İLK VE SON DEFA çağrılır:
                  Genlik = KAN(konfigürasyon, mahallîYazmaç, θ_cartan)
    4. ÖLÇÜM      Genlik okunur, kelâm çıkar.

* **TURDA İKİ KAN ÇAĞRISI YOKTUR.** Bir evvelki turda 3176 çağrıyı
  bire indirip hemen ardından ikiye çıkarmak israftır.
* **GECİKME YOKTUR.** Melekelerin ve `θ_cartan`ın bütün fazı aynı
  turun cevabına girer.
* **MELEKELER BOŞLUĞA KOŞMAZ:** `kodla`nın ektiği dolu yazmaca temas
  eder.

---

## ▓▓▓ 2-Â. FERMAN: CARTAN FAZI SERPİLMEZ -- KÜRESEL AYAR FAZIDIR ▓▓▓

> *"Küresel Lie-Cartan fazı veri yazmacına **bir un çuvalı gibi
> serpilmez**!"*

### BENİM İCAT ETTİĞİM SAHTE MESELE

*"On elemanlı `θ_cartan` bir milyon qudite hangi izdüşümle
dağılacak?"* diye sordum. Bu suâl **yanlış kurulmuştur**: iki ayrı
varlık katmanı birbirine karıştırılmıştır.

    MAHALLÎ YAZMAÇ   verinin fiziksel taşıyıcı koordinatı
    θ_cartan         bütün kâinatı yöneten küresel simetri cebrinin
                     kolektif AYAR FAZI (gauge phase)

Bir alan teorisinde küresel faz döndürmesi uygularken bir milyon
koordinat taranıp *"bu fazı hangi noktaya kaç gram dağıtsam"* diye
harita aranmaz.

### SAHİH İNTAÇ -- İKİ KADEME, SIFIR TARAMA

    1. KÜRESEL   θ_cartan doğrudan KAN üssüne rezonans fazı olarak girer:
                 Genlik = üstel( −Enerji + i·( Σ_j w_j
                                 + θ_cartan · KökAğırlığı ) )
                 Maliyet: kök sayısı kadar skaler çarpım.

    2. MAHALLÎ   Bir meleke mahallî yazmaca vuracaksa bir milyon qudit
                 taranmaz: temas ettiği kapı indislerinin faz sütununa
                 tek çevrimde eklenir (ferman 2-V, seyirci qudit).

**HER TURDA GERİLİM TEPESİ ARAMA YAHUT CASIMIR ÖLÇÜMÜ KOŞTURMA
HAMALLIĞI YAPILMAZ.**

---

## ▓▓▓ 2-Î. FERMAN: MODEL GENELLER -- EZBER MAKİNESİ DEĞİLDİR ▓▓▓

> *"Ulan ahmak, github release ile **ultramath** verisetinin inmesini
> tetiklemedin mi, **100 GB matematik verisi var**, nasıl olmasın?
> Ayrıca adam cevabı bilmede dahi **en azından mantıklıca konuşup
> bilmiyorum der**, dil modeli dediğin **genelleyebilir olmalı**,
> burada **ezber makinesi** ürettiğimizi mi sanıyorsun cahil?"*

* **VERİ VARDIR.** Külliyatta yüz gigabaytlık riyaziye durmaktadır;
  *"model bunu görmemiş olabilir"* demeden evvel külliyat yoklanır
  (ferman 1-K).
* **MİHENK EZBER SORMAZ.** Bir dil modelinden beklenen, tam o suâli
  görmüş olmak değil, **genellemektir**. Görmediği bir suâlde dahi
  makul konuşması, hiç değilse *"bilmiyorum"* diyebilmesi beklenir.
* **MİHENK VERİSİNİ TÂLİME KOYMAK YASAKTIR:** suâli ve cevabını
  tâlim kümesine koymak ölçüyü ölçü olmaktan çıkarır, ezber makinesi
  kurar. Mihenk **dışarıdan** sorulur ve öyle kalır.

---

## ▓▓▓ 2-Û. FERMAN: MELEKENİN EVİ MAHALLÎ YAZMAÇTIR -- KAN KATSAYISINA DOKUNULMAZ ▓▓▓

> *"Melekelerin evireceği yegâne zemin: **Mahallî Yazmaç ve müstakil
> `θ_cartan` Lie vektörüdür.** KAN'ın katsayıları sabit ve pürüzsüz
> kalacaktır."*

* **KAN'IN `C` VE `S` KATSAYILARINA ÇIKARIM ANINDA DOKUNULMAZ.** Onlar
  fonksiyonel mimarinin **küllî parametreleridir**; her belirteçte
  bükülürse FCT dikliği çöker ve model kendi ağırlığını tahrif eden
  bir bellek çorbasına döner. Bir operatör **durumu** evirir, doğa
  kanununun fonksiyonelini değil.
* **MELEKE YALNIZ FAZA DEĞİL, GENLİĞE DE HÜKMEDER.** Benim *"bütün
  kapılar köşegen faz olur, genlik zaten KAN'dan gelir"* kabulüm
  eksikti: Zeno izdüşümü yahut tenakuz sönümlemesi gerektiğinde genliği
  sıfırlayan mahallî yazmacın **genlik sütunudur**.
* *"Köşegen tesir faza, köşegen olmayan tesir KAN katsayısına"* diye
  bir ayrım **yoktur**: köşegen olmayan kapı KAN katsayısını değil,
  durumun **genlik izdüşümünü** değiştirir.

---

## ▓▓▓ 2-Ê. FERMAN: HÂL BASAMAK TOPLAMI DEĞİL -- HEDEF QUDİDİN İZDÜŞÜMÜ ▓▓▓

> *"Farklı zaman basamaklarındaki genlik karelerini birbirinin üstüne
> toplamak; **dünü, bugünü ve yarını bir kazana atıp çorba yapmaktan**
> farksızdır!"*

### İKİ HURAFE BİRDEN KESİLDİ

1. **BASAMAK EKSENİ TOPLAMI HURAFEDİR.** Hâl `|ψ|²`nin basamaklar
   boyunca toplamı değildir. Farklı konumların olasılıkları birbirine
   eklenmez; ölçüm, cevabın üretileceği **aktif hedef quditten** okunur.
2. **KAN SÖZLÜK BOYUNDA ŞİŞİRİLMEZ.** *"Tek çağrıda sözlük kadar
   konfigürasyon verelim"* teklifim, 3176 çağrıdan kaçıp on binlik bir
   yığına atlamaktı; reddedildi.

### SAHİH OKUMA

    Hâl(kelâm) = | ⟨ kelâm | Genlik(hedef qudit ; θ_cartan) ⟩ |²

Mahallî yazmaçtaki **hedef çıkış quditinin** yerel durumu, tek bir KAN
çağrısından gelen küllî rezonans ve `θ_cartan` faz mührü altında
hesaplama tabanına izdüşürülür. Maliyet `O(1)`; ne geçmiş basamaklar
toplanır, ne KAN şişirilir.

---

## ▓▓▓ 2-Ô. FERMAN: SEKTÖRÜN DEĞERİ AÇI DEĞİL, BEKLENTİ DEĞERİDİR ▓▓▓

> *"Rotasyon açısının büyüklüğünü sektörün mizan ağırlığı saymak;
> **saatin akrebinin gösterdiği açıyı zamanın miktarı zannetmeye**
> benzer!"*

Benim *"sektörün değeri kökte biriken fazın büyüklüğüdür"* teklifim
**reddedildi** ve haklı olarak: `θ` bir dönme açısıdır. Açı sıfırken
sektör yok değildir, açı `π` iken en büyük değildir.

### SAHİH ÖLÇÜ

    Ağırlık(sektör_k) = toplam over j ∈ sektörün indisleri of
                        |MahallîYazmaç[j, genlik]|²
    Kefe(sektör_k)    = Ağırlık(sektör_k) · üstel( i · θ_cartan[k] )

Yâni ölçülen şey **durumun o sektördeki genlik ağırlığı ile fazının
bileşkesidir** -- Cartan jeneratörünün beklenti değeri. Dilim aranmaz,
ve **KAN sektör sayısınca çağrılmaz**: tek küllî çağrı bu mizanı tartar.

---

## ▓▓▓ 2-P. FERMAN: MECLİS DEĞİL **MECZ** -- KÖR YÖN ARAMASI İLGA ▓▓▓

> *"Bu kesinlikle bir kusur, en ilkel olarak türevden bile berbat...
> **bir daha yön arama saçmalığına düşeriz, öyle şey yok**, tek seferde
> analitik çözüm lâzım bize, o analitiğin de kuantum hız imkânından
> faydalanması lâzım... **Sadece bir motor körü körüne yönlendirmesin
> bizi, ya da tüm motorların dediği belli bir ağırlıkla toplanıp bizi
> oraya yönlendirmesin**, yâni bu iş **artık** sadece bir yönlenme
> işinden çıksın... Yâni **meclis değil mecz, vazife dağılımı**."*

### İLGA EDİLEN

Adım atılmadan evvel harcanan **18 kör çağrı** kaldırılmıştır:
`V_ilk` (1), `_had_yaricap` (3 yarıçap × 3 yön = 9), `_toptan_yon`
(4 ortalama × 2 uç = 8). Bunlar durumu **kara kutu** zanneder: elde
`ψ`, `ρ` ve üreteçler dururken dışarıdan el feneri tutmaktır.
**Türevden de beterdir**, çünkü türev hiç değilse analitiktir.

### İKAME EDİLEN: TEK SEFERDE ANALİTİK, KUANTUM HIZIYLA

* **YOL İNTEGRALİ ASLI.** Yön **tek tek aranmaz**; bütün yönler aynı
  anda denenir. `Eğim_a = 2·Im⟨ψ|Üreteç_a · Hata|ψ⟩` bütün `a` için
  **tek hamlede** hesaplanır. Kayıp çağrısı: **sıfır**.
* **TÜREV GERİ GELDİ, FAKAT TEK BAŞINA DEĞİL.** Ferman 1-V'nin
  *"türev almıyoruz"* hükmü **yön** kanadında kalkmıştır: türev
  analitik olarak alınır ve **yanına yardımcılar** verilir. Kaybın
  **vektör** kalması (ferman 1-U, 1-V) aynen bâkîdir; kalkan şey
  türev yasağı değil, **kör taramadır**.

### VAZİFE DAĞILIMI -- BEŞ MEMURİYET, HER BİRİ AYRI CİNS

    EĞİM     "aşağı gideceksek böyle gidelim"   → yön verir
    ÇUKUR    "burası minimum muymuş bakalım"    → durak mı, söyler
    DUVAR    "şuraları duvarlı, vakit kaybetme" → koordinat eler
    VADİ     "şu vadiyi bir atlatalım"          → engeli aşırtır
    NAKİL    "bizi çok farklı bir yere taşısın" → sıçratır

### MECZ NE DEMEK, MECLİS NE DEMEK

* **MECLİS (yasak).** Beş memurun dediğini bir ağırlıkla toplayıp
  tek bir yöne inmek. Bu ferman 1-U'nun yasakladığı sandalyedir:
  toplanınca hangi memurun ne dediği kaybolur.
* **MECZ (asıl).** Her memurun **çıktısının cinsi başkadır**, o hâlde
  toplanamazlar: DUVAR bir **maskedir** (eler, ağırlık vermez), ÇUKUR
  bir **hükümdür** (dur yahut yürü), EĞİM bir **yöndür**, VADİ ile
  NAKİL adımın **yerine geçer**. Bunlar ferman 2-C'nin karaciğeridir:
  **her vazife ayrı bir şartlı daldır**, hepsi tek düz gövdeye
  tıkılmaz.

### YARIÇAP FUBINI-STUDY İZİNDENDİR -- VE TARAMA RUHSATI DEĞİLDİR

> *"Fubini-Study izinden olsun ama tekrar ediyorum, bunlar vazife
> dağılımıdır. **Yarıçap belirledin diye oradaki her şeyi tarayacaksın
> diye bir şey yok**."*

    Yarıçap = Keyfiyet(üç hudut) / √iz(Fubini-Study metriği)

* Sabit `eta`, sabit kelepçe (`clamp`) **yazılamaz** (ferman 1-J):
  pay keyfiyetin ölçülen nispetidir, payda durumun kendi metriğidir.
* **YARIÇAP BİR TARAMA DAVETİ DEĞİLDİR.** Yarıçap bulununca o
  yarıçaptaki noktalar taranmaz; yarıçap yalnız **adımın boyudur**.
  Hat araması (Gauss-Chebyshev-Lobatto düğümleri dâhil) bu ferman
  ile **ilga edilmiştir**.

### HER KEFEYE OPERATÖR

Mizanın her kefesi için yazmaç üstünde bir **operatör** kurulur ki
yön mizanın **tamamından** analitik çıksın. Operatörü ispatlanamayan
kefe **uydurulmaz** (ferman 5): o kefe yönü kurmaz fakat **hükmü
verir** -- adımın kabulünde tam mizan vektörü konuşur ve hiçbir cevher
düşmez (ferman 1-S).

---

## ▓▓▓ 3. FERMAN: TERKİP ÜÇ ADIMDIR ▓▓▓

1. Her dosya **kendi içinde** terkip edilir.
2. Dosyalar birleştirilir.
3. Birleşik dosyada **bir daha** terkip yapılır.

Terkip bir **kimliktir**, tabela değildir. İki şeyi aynı isim altına koymak
terkip değildir; ikisinin **aynı şey olduğunu ispat etmek** terkiptir.

### 3-B. İSPAT ÖLÇÜLEREK DEĞİL, **FORMÜL CEBRİYLE** YAPILIR

> *"Terkipte ispat **ölçülerek değil formül cebriyle** yapılmalıdır!"*

İki icranın aynı şey olduğu, ikisini koşturup çıktılarını
kıyaslayarak gösterilmez. Bu bir **ölçüm**dür ve ferman 1-C(a) ile
1-L'nin yasakladığı şeydir; üstelik ispat da değildir -- iki
fonksiyon bin girdide aynı çıkabilir, bin birincide ayrılabilir.

    YASAK    `assert abs(a(x) - b(x)) < 1e-12` ile terkip ispatı
    ASIL     a'nın cebrinden b'nin cebrine **kapalı form türetmek**

* Misal: `expm` ile matchgate Givens dönmesinin aynı olduğu, ikisini
  koşturarak değil, `exp(−iθ(c_p c_q))`nun Majorana kovaryansında
  `SO(2N)` dönmesine **cebrî indirgenmesiyle** gösterilir.
* Cebrî indirgeme **yapılamıyorsa** iki şey aynı değildir; terkip
  edilmez, ikisi de kendi menfezinde durur (ferman 2-C).
* Sayı yine de yazılır (ferman 5) fakat o sayı **ispat değil
  şahittir**: cebir ispat eder, sayı tasdik eder.

---

## ▓▓▓ 4. FERMAN: HALKÇA İSİM ▓▓▓

> *"Yapılan işi, mahiyeti en az kelimeyle en çok yönden kapsayan, projemizde
> alacağı rolü doğrudan tarif eden."*

---

## ▓▓▓ 5. FERMAN: ÖLÇÜ KIRMIZI YANABİLMELİ ▓▓▓

* Her iddianın bir **sayısı** olacak (H90).
* Ölçü **kapatılabilir** olacak; kapatılınca kırmızı yanacak. Yanamıyorsa o
  ölçü hiçbir şey ölçmüyordur.
* Yapılmayan şey yapıldı diye yazılmaz (H100).
* `except` ile sessiz ikame yasaktır. Yerine **assert**: boş bir şey dönmesin.

---

## ▓▓▓ 6. FERMAN: BU BİR DİL MODELİ PROJESİDİR ▓▓▓

ARC **yalnız** LLM motoruyla çözülür. Elle yazılmış kâide, öznitelik
mühendisliği, göreve mahsus çözücü **yasaktır**.

---

## ▓▓▓ 7. FERMAN: İPTAL EDİLMİŞ USULLER (ÇAĞRILAMAZ) ▓▓▓

| İptal | Yerine gelen |
| :-- | :-- |
| SVD / MPS / bond truncation | Qudit ℂ^d, durum TAM tutulur |
| İkili kübit kodlaması | Qudit seviye kodlaması |
| Kör NLL / CrossEntropy | Mîzân-ı Küllî (`nefs/kulli_mizan.py`) |
| Kör `temperature` örneklemesi | Vakum kıvılcımı (`nefs/ayna.py`) |
| `kuantum/kubit_taksimati.py` | (imha; taksim edilecek zincir yok) |
| Elle ARC kâideleri | Motor |
| **Sürekli Hilbert ℂ^d + Float32/Complex64 genlik** | **Galois GF(2⁸) + Stabilizer Tableau** |
| **Transandantal faz e^{iθ} (sin/cos/exp)** | **Palmer 2-bit rotasyonu: i(a,b) = (−b, a)** |
| **O(d²) GEMM / yoğun 4096 matris** | **Matrix-free Kronecker-SIMD [16,16,16], L1'de** |
| **TDD'nin HESAP MOTORU olması** | TDD yalnız **kanonik denetçi** (çevrim kapanışında, O(1) adres) |
| **Sürekli açılı kapıyı KÜBİT tabanında vurmak** (Bravyi-Gosset: χ_stab ~ 2^{0,468t}) | **Valiant-Terhal Matchgate/FLO düalitesi**: Majorana kovaryansında SO(2N) Givens, **χ_stab = 1** (`nefs/matchgate.py`) |
| **Gayri-lineerliğin sürekli B-spline / transandantal olması** | **Rijndael-Galois otomorfizmi** `x ↦ x²⁵⁴` (GF(2⁸) S-box, GFNI) (`nefs/galois.py`) |
| **Köşegen fazı genlik vektörüne tek tek vurmak** | **Faz üssünü `Z_m`de biriktirmek**: tamsayı toplaması, genliğe tek dokunuş (`nefs/qyazmac.py:faz`) |
| **CNOT-DİHEDRAL SINIF İDDİASI** (Amy-Maslov-Mosca, derece ≤ 3) | **Siklotomik koset + Frobenius iz indirgemesi** (`nefs/siklotomik.py`) |
| **Kombinatorik monom taraması** (derece-12 polinomunu terim terim toplamak) | **`vpshufb` faz otomatı**: 64 baytlık LUT yazmaçta, tek vuruş |
| **Ana akış döngüsünde Python/dispatch ve tahsis** | **Sıfır tahsisli kaynaşık C çekirdeği** (halka tampon, `nefs/gfni.py`) |

### 7-A. NON-CLIFFORD ÇIKMAZININ ÜÇ ÇARESİ -- HÜKÜM

Zabıt (*Non-Clifford ve Stabilizer Rank Çıkmazının Riyazî Çözümü*)
itirazın haklılığını tescil eder: saf kübit tablosunda tek bir `T`
kapısı rankı `2^{0,468t}` patlatır. Fakat **çıkmaz değildir**; üç
ispatlı çare vardır ve **üçü de icra edilir**:

1. **Matchgate/FLO (Valiant-Terhal-DiVincenzo, 2002).** `G(A,B)`
   formundaki kapı kübitte non-Clifford olsa da Majorana
   kovaryansında yalnız 4 satır/sütunda bir Givens dönmesidir.
   Parite korunur, dallanma yoktur.
2. **Galois `F_2^8` S-box (Rijndael).** Gayri-lineerlik `e^{iθ}`
   değil, `x ↦ M·x^{254} + b (mod P)` cebrî otomorfizmidir.
   `P(x) = x⁸+x⁴+x³+x+1`. Tek tablo okuması; dallanma sıfır.
3. **~~CNOT-Dihedral faz polinomu~~ → SİKLOTOMİK KOSET.**
   Faz üssü `Z_m`de biriktirilir (`|x⟩ ↦ ω^{P(x)}|x⟩`, toplama `ADD`);
   fakat **sınıf iddiası iptal edildi**, bkz. 7-B.

### 7-B. CNOT-DİHEDRAL İDDİASI RESMEN İPTALDİR

Ölçüm kendi iddiamızı yere serdi ve örtülmedi: ana akışta biriken
fazın Reed-Muller derecesi **12** çıktı. Amy-Maslov-Mosca teoremi
derece `≤ 3` (Clifford+T, `C_3`) varsayar; derece 12 operatörü
Clifford hiyerarşisinin **12. seviyesindedir**. O hâlde:

* **"Durum CNOT-Dihedral sınıfındadır" denmeyecektir.** Denirse yalan olur.
* Yerine gelen: derece 12 bir kaos değil, **`x³`ün iki Frobenius
  karesidir** — `12 = 8+4 = 2³+2²`, yâni `x¹² = ((x³)²)²`.
  Karakteristiği 2 olan cisimde Frobenius **lineerdir**, o hâlde
  `Tr(α·x¹²) = Tr(α^{1/4}·x³)`: derece-12 iz terimi derece-3'e
  **tam olarak** iner. Monom açılımı yoktur.

### 7-D. ZABIT FORMÜLLERİ YENİ NESİL MİMARİYE **ADAPTE EDİLİR**

> *"C^d üstünde yazılmasına da bakma, quditten sonra nasıl o yeni
> mimariye geçtiysen söylenen formülleri de o yeni nesil mimariye
> adapte et."*

Zabıtlar sürekli Hilbert uzayının (`ℂ^d`) diliyle yazılır: Uhlmann
sadakati, Fubini-Study metriği, Hodge Laplasyeni, Berry eğriliği,
Kraus operatörü, `ρ` yoğunluk matrisi. **Bu bir çelişki değildir ve
ferman 7'yi nakzetmez.**

* Zabıt **manayı** verir, taşıyıcıyı değil. `ℂ^d` orada bir tarif
  dilidir; hüküm o dilin altındaki geometrik/cebrî hakikattir.
* O hâlde her formül **yeni nesil taşıyıcıya tercüme edilir**: Galois
  `GF(2⁸)`, stabilizer tableau, `Z_m` ayrık faz, Kronecker karo,
  matchgate/FLO kovaryansı, siklotomik koset.
* Tercümenin sıhhati **ölçülür**: yeni taşıyıcıdaki netice ile zabıtın
  tarif ettiği netice kıyaslanır ve fark sayıyla yazılır.
* **"Zabıt ℂ^d diyor, o hâlde ferman 7 kalksın" demek yasaktır.**
  Aynı şekilde "ferman 7 var, o hâlde bu formül icra edilemez" demek
  de yasaktır. İkisi de tembelliktir; doğrusu **tercümedir**.

### 7-C. MİSAL KOD KÖRÜ KÖRÜNE ALINMAZ

Padişah bir misal kod verdiğinde ("yanlışlıkları olma ihtimali çok
yüksek" dese de demese de), o kod **kopyalanmaz**: her satırı
sınanır, yanlışı sayıyla gösterilir, doğrusu yazılır. Bir misalin
yorum satırındaki iddia (`AVX-512`, `Frobenius`, `Ring Buffer`)
gövdesinde fiilen yoksa, o iddia **tekrarlanmaz**.

---

## TÂLİM VE ÇIKARIM

```
python -m main.egitim tâlim kısa       # tâlim (geçit + mizan + hazine)
python -m main.egitim teftiş           # divan
python -m main.cikarim                 # çıkarım (hazineden ağırlıkla)
```
