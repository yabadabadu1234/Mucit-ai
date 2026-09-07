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

## ▓▓▓ 3. FERMAN: TERKİP ÜÇ ADIMDIR ▓▓▓

1. Her dosya **kendi içinde** terkip edilir.
2. Dosyalar birleştirilir.
3. Birleşik dosyada **bir daha** terkip yapılır.

Terkip bir **kimliktir**, tabela değildir. İki şeyi aynı isim altına koymak
terkip değildir; ikisinin **aynı şey olduğunu ispat etmek** terkiptir.

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
