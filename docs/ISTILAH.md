# ISTILÂH — kullandığım her terimin mânâsı

Kullanıcı hükmü:

> *"Ben bazı sorularına senin kullandığın tabirleri anlamadan cevap
> verdiğim için de böyle oluyor olabilir. Ben sadece hayal kurmayı
> biliyorum, kendimden terim ürettiğim yok; dolayısıyla anlaşabilmemiz
> için terimlerinin manasını detaylı izah etmen lazım."*

Bu haklı bir tenkittir ve benim kusurumdur. Sual sorarken cevabı
anlaşılmaz kılan terimler kullandım; alınan cevap da o yüzden benim
kurduğum çerçeveye mahkûm oldu. Aşağıda kullandığım her terim,
**önce hayalî karşılığıyla**, sonra riyazî tarifiyle yazılmıştır.

---

## 1. DURUM ve ONU TUTMA USULLERİ

### Kübit
Bir kübit, klasik bir bitin (0 yahut 1) yerine **hem 0 hem 1 olabilen**
bir şeydir: `a|0⟩ + b|1⟩`. `a` ve `b` iki sayıdır, kareleri toplamı 1.

`N` kübit bir arada `2^N` ihtimali **aynı anda** tutar. 20 kübit bir
milyondan fazla ihtimal demektir. Sizin *"kübitin tutabildiği her bir
ihtimali bir kelime olarak düşününce aynı anda 1 belirteç değil
1 milyon belirteç işlenebilir"* dediğiniz şey tam olarak budur ve
**doğrudur**.

### Süperpozisyon
Bütün ihtimallerin aynı anda askıda olması. Hadamard kapısı `|0⟩`ı
`(|0⟩+|1⟩)/√2` yapar; `N` kübite vurulunca `2^N` ihtimalin hepsi eşit
ağırlıkta doğar. **Ucuzdur** — hafızada hiçbir şey büyümez.

### Dolaşıklık (entanglement)
İki kübitin ayrı ayrı tarif edilememesi. "A'ya bakınca B hakkında bir
şey öğreniyorsam ikisi dolaşıktır." **Pahalıdır** — hafıza asıl bunun
yüzünden büyür. Süperpozisyon bedava, dolaşıklık pahalı.

### MPS (Matris Çarpım Durumu)
`2^N` genliği açık açık yazmak imkânsızdır (`N=100` için evrendeki
atomdan çok sayı). MPS bunun yerine **her kübite küçük bir matris**
koyar ve genliği o matrislerin çarpımından üretir:

    genlik(i₁i₂…i_N) = A₁[i₁] · A₂[i₂] · … · A_N[i_N]

Hafıza `N·χ²` olur, `2^N` değil. Kod'da `main/yazmac.py`.

### χ (chi) — "bağ boyutu"
O küçük matrislerin kenar uzunluğu. **Ne kadar dolaşıklık
taşıyabileceğinizin ölçüsüdür.** `χ=1` hiç dolaşıklık yok (çarpım
durumu); `χ` büyüdükçe daha karmaşık dolaşıklık tutulur, fakat maliyet
`χ³` ile büyür. `χ=64` ile `χ=32` arasında 8 kat maliyet farkı vardır.

### Schmidt rütbesi ve kesme (truncation)
Bir kesitte durumu tarif etmek için kaç sayı gerektiği. `χ` yetmezse
en küçük sayılar **atılır** — buna *kesme* denir ve atılan ağırlık
raporlanır. Kesme, modelin unutması demektir; onun için hiçbir yerde
gizlenmez.

### MPO (Matris Çarpım Operatörü)
MPS durumu tutar; MPO **işlemi** tutar. Zincirin uzak iki ucuna aynı
anda dokunan bir kapıyı, kübitleri yerinden oynatmadan uygulamanın
yoludur. Alternatifi *takas ağıdır* (kübitleri yan yana getirip geri
götürmek) ve o, geçtiği her yerde dolaşıklığı sürükler.

### Ayar (gauge)
Aynı durum, **farklı matrislerle** yazılabilir — tıpkı aynı yönün
farklı koordinat sistemlerinde farklı sayılarla yazılması gibi.
Bu yüzden iki modelin matrislerini karşılaştırmak **yanlıştır**;
karşılaştırılacak şey genliklerdir. (Bu hatayı yaptım ve kütükte
H80'de zabıtladım.)

### Kanonik hâl
Ayar serbestliğini sabitlemek. Kesmenin **en iyi** olması ancak
kanonik hâlde garantidir; değilse atılan sayılar hakikî hatayı vermez.

---

## 2. AĞAÇ ve GEOMETRİ

### MPS zinciri vs 2 boyutlu ızgara
ARC ızgaraları iki boyutludur. MPS bir **zincirdir** (tek boyut).
Izgarayı zincire sermek, komşu iki hücreyi zincirde birbirinden çok
uzağa düşürür. Ölçüldü (H52): ARC için gereken `χ` `10³⁰` çıkıyor —
imkânsız.

### PEPS
İki boyutlu tensör ağı. Hendese doğru, fakat ağda **çevrim (loop)**
var ve çevrimli ağı hesaplamak `#P`-zordur; ancak yaklaşık hesaplanır
ve o yaklaşıklığın hatası kontrol edilemez.

### Ağaç (TTN) — `nefs/agac.py`
Izgarayı ikiye böl, blokları bir üst düğüme bağla. **Çevrim yoktur**,
onun için hesap MPS gibi **tamdır**; hendese ise iki boyutludur. İki
hücre arası mesafe zincirde `O(N)`, ağaçta `O(log N)` — 30×30'da 899'a
karşı 18 adım. Bu, sizin *"MERA ile PEPS'i barıştır"* hükmünüzün
karşılığıdır.

---

## 3. ÖLÇÜM

### POVM ve "zayıf ölçüm"
Klasik kuantum ölçümü durumu **çökertir** (bütün ihtimaller ölür,
biri kalır). POVM ise bir **dağılım** okur ve dalgayı diri bırakır.
Kütükte H31: *"hükmün sayısı ancak en sonda doğar ve bir sayı değil
dağılımdır."*

### Marjinal (indirgenmiş yoğunluk)
Bir kübite tek başına bakmak; ötekilerin üzerinden "iz alınır".
Tehlikesi: her şey her şeyle dolaşıksa küçük bir bloğun marjinali
**tam düzgün** çıkar ve model konuşamaz. Bu ölçüldü ve `kelam` alanı
o yüzden ayrıldı.

---

## 4. ÖĞRENME (gradyansız)

### Gradyan / Adam / SGD
Klasik öğrenme: kaybın eğimini hesapla, ters yöne küçük adım at,
tekrarla. Kütük H3 bunu **yasaklıyor**.

### Kapalı form
Adım atmadan, tek denklem çözerek cevabı bulmak. En küçük kareler
(`c = (ΦᵀΦ+λI)⁻¹Φᵀy`) böyledir: yaklaşık değil, **tam** çözümdür.

### Ansatz
"Cevabın şu şekilde olduğunu varsayıyorum" demek. NQS'te dalga
fonksiyonunun bir KAN ağıyla yazılacağını varsaymak bir ansatzdır.
**Ansatz sığası**: o varsayımın ne kadar karmaşık şeyi
temsil edebildiği. Sığa yetmezse öğrenme durur — H76'da bu ölçüldü.

### NQS (Nöral Kuantum Durumu)
Durumu bir **dizi** olarak değil bir **fonksiyon** olarak tutmak:
hangi ihtimal sorulursa genliği hesaplanır. Hafıza `2^N` değil,
fonksiyonun parametreleri kadar.

### Faz orağı, difüzyon, Grover
- **Faz orağı**: kaybı bir **dönme açısına** çevirmek. İyi cevaplar az
  döner, kötüler çok.
- **Difüzyon**: ortalamaya göre yansıtma.
- **Grover**: bu ikisini tekrarlayınca iyi cevapların genliği büyür,
  kötülerinki söner. **Yıkıcı girişim** budur: iki dalga zıt işaretle
  buluşup birbirini siler.

### Tavlama (annealing) ve `β`
Isıyı yavaşça düşürmek. `β` "sertlik"tir: küçükken her ihtimal
mümkün, büyükken yalnız en iyiler. Grover adımı bu sertliğin ne kadar
artacağını **söyler**; ben uydurmam.

### Metropolis, kabul oranı, karışma
Dalgadan örnek çekme usulü: bir hamle teklif et, iyiyse kabul et.
**Kabul oranı** düşükse (`<0,1`) zincir kilitlenmiştir ve örnekler
birbirinin aynısıdır — ölçü bozulur.

---

## 5. HIZ

### Yığın (batch)
Aynı işi `B` tane veri üzerinde **aynı anda** yapmak. `A` dizisinin
şekli `(B, N, χ, 2, χ)` olur.

### LAPACK / BLAS
numpy'nin arkasındaki lineer cebir kütüphaneleri. **Çağrı masrafı**:
küçük bir matris için asıl hesaptan çok, çağrının kendisi vakit alır.
Ölçüldü: yığın SVD'de matris başına maliyet ancak 1,7 kat iniyor —
yani numpy'nin yığını *gerçek* yığın değil.

### float32 / float64
Sayıların hassasiyeti. float32 iki kat hızlı ve iki kat az yer tutar;
bedeli `1,2e-07`lik yuvarlama hatasıdır.

---

## 6. BU PROJENİN KENDİ ISTILÂHI

| terim | mânâsı |
|---|---|
| **meleke (𝒪ₙ)** | zihnin bir kabiliyeti; kodda bir üniter kapı dizisi |
| **küllî hüküm bloğu** | zincirin sonundaki makam/mîzân/tasdik/tenakuz/sükût/nakz/kelam kübitleri |
| **yerel hüküm** | bir satır hakkındaki hüküm, o satırın bitişiğinde |
| **makam** | Şek / Zan / Yakîn / Vehim — hükmün derecesi, iki kübite kodlu |
| **kelam** | modelin konuşacağı alan; `|0⟩`dan başlar, yalnız beyan melekeleri yazar |
| **sükût** | "bilmiyorum" diyebilme kabiliyeti; bir kusur değil fazilet |
| **nakz** | tek karşı örneğin küllî hükmü düşürmesi |
| **şahit** | bir ARC görevindeki her gösterim çifti |
| **kesme** | `χ` yetmediğinde atılan ağırlık = modelin unutması |
| **tebaa / beylik** | padişahın (ana akışın) eli uzanan / uzanmayan modül |

---

## 7. BUNDAN SONRA

Size sual sorarken:

1. Terimi **önce hayalî karşılığıyla** yazacağım, sonra riyazî
   tarifini.
2. Şıkların her birinin **ne kaybettireceğini** de yazacağım, yalnız
   ne kazandıracağını değil.
3. Cevabınızı benim çerçeveme sıkıştırmayacağım: "başka / ben tarif
   edeceğim" şıkkı daima duracak.

Bu vesika eksik kaldıkça genişletilecektir; anlamadığınız bir terim
görürseniz söyleyin, buraya yazayım.
