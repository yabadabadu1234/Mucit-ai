# KÜTÜK — verilen hükümlerin birikimli kaydı

Bu dosya bir tasarım belgesi değildir; **hüküm kütüğüdür**. Konuşma boyunca
verilen hükümler burada sıra sıra durur. Yeni bir hüküm eskisini silmez;
eskisi ancak açıkça *nakzedilirse* düşer ve nakzi de buraya yazılır.

Sebebi şudur: hükümleri yalnız en sonuncusunu tutup öncekileri atarak
işlemek, hâkimin karşısındaki aptalın hâlidir. Kütük bunun önündeki settir.

---

## H1 — Ana icra hattı `nefs/akis.py`'dir

`idrak/` bir **ARC denemesidir**, ana döngü değildir. Bir modülün "bağlı"
sayılması için `nefs/akis.py`'deki `AKIS` sırasında koşan bir melekenin
uzvu olması gerekir. Ölçüt: `𝒪ₙ`'in **gerçek bir uzvu** mu var, yoksa
yerine bir **vekil skaler** mi konmuş.

## H2 — 41 meleke asıl modeldir

`nefs/`'teki 41 meleke yardımcı değil, modelin kendisidir.

## H3 — Ana döngüde gradyan ve kayıp yoktur

Öğrenme:

* ağırlık = parametrize lifleşmenin kesiti, `w ∈ ℳ` (`kesit_tipi`, `agirlikta_lif`),
* doğrusalsızlık = kip/kesme/yerelleştirme funktoru,
* uydurma = RKHS kapalı formu / KAN sembolik kapanışı / FNO spektrali,
* uç değer = `RCrit(f)` + tıkızlaştırma (Alexandroff, zorlayıcılık, barriyer),
* akış = hacim akışı (MCF / Fokker–Planck / Liouville), tek boyutlu gradyan oku değil.

NFL ve tıkızlaştırılamayan fonksiyonlar **gizlenmez**, ölçülür ve raporlanır.

## H4 — Uzvun cinsi melekenin tabiatından çıkar

Sayısal meleke sayısal uzuv alır; **hüküm veren meleke sembolik kalır** —
ispat, hüküm, kaide üretir; float üretmez. "Hepsi torch olsun" hükmü
mülgadır (o cevap, benim bozuk çerçevem içinde alınmıştı).

## H5 — ARC zaten metindir

Tek dil yolu. Model neyi verirsen onu konuşur. "İki başlı ARC + metin"
planı mülgadır. Beyan melekeleri (`𝒪₃₇–𝒪₄₁`) ARC üzerinde de tanımlıdır.

## H6 — ARC'ye has tek yenilik: **şahitlik**

Bir bulmacanın her gösterim çifti bir **şahittir**. "Hepsi aynı kurala
tâbidir" bilgisi modele **bayrakla bildirilmez**; organlarla sezilir ve
sınanır:

```
şahit bölütlemesi → şahit başına kaide (𝒪₁₈ Kıyas)
   → nakz: tek karşı örnek küllî kaideyi düşürür (𝒪₂₃ Mantık)
   → tevafuk + fazla sayma: müteber şahit sayısı (𝒪₂₉ Teyit)
   → küllî kaide + taklit ayırımı (𝒪₃₀ Tahkik)
   → istikrâ (ardışıklık kaidesi) → makam (𝒪₃₂)
   → makam Şek ise **sükût** (𝒪₃₇–𝒪₄₁)
```

## H7 — Nizamnamenin beş kademesi

1. envanter ve arayüz akdi (`nefs/akit.py`)
2. bağımlılık DAG'ı (`sira_gecerli_mi`)
3. merkezî durum veri yolu + kayıpsız intibak (`Durum`)
4. ana orkestra hattı (`AKIS`, melekelerin `yazar` akitleri)
5. icra izi + hassasiyet + hata izolasyonu (`nefs/tesir.py`)

## H8 — İlerleme ölçüsü

Düşürüldüğünde neticeyi hiç değiştirmeyen meleke sayısı.

Ölçü **bileşiktir** ve öyle olmak zorundadır: yalnız `‖ΔN‖` bakmak,
hüküm üreten melekeleri (nakz, makam, mühür) görmez — çünkü onlar sayı
değil hüküm üretir (H4). `nefs/tesir.py` şunların herhangi birine bakar:

```
‖ΔN‖ ∨ makam değişti ∨ sükût değişti ∨ nakz değişti ∨ mühür değişti ∨ ΔP
```

Ölçülen (`python -m nefs.tesir`, yapılandırılmış şahitli girdi):

| ölçüm | tesirsiz |
|---|---|
| başlangıç (yalnız `‖ΔN‖`, rastgele girdi) | **27 / 40** |
| şimdi (bileşik ölçü, kurallı girdi) | **20 / 41** |

Bunun 8'i **yapısal zaruret**tir (düşürülünce akış kırılır), 13'ü
tesirlidir. Ayrıca `nefs/akit.py`: veri yoluna hiçbir şey yazmayan
meleke sayısı **20 → 10**, vekil kalan **3** (𝒪₁₆, 𝒪₁₉, 𝒪₂₀).

**Rastgele gürültüde ölçüm yanıltır ve öyle raporlanır.** O girdide
model doğru olarak **susar** (makam Şek → sükût), `N` zaten sıfırdır ve
`‖ΔN‖` hiçbir melekeyi ayırt edemez. `tesir.py` asıl ölçümü kurallı
girdide yapar, rastgeleyi bu kayıtla ikinci sırada verir.

## H9 — Mevcut modüller silinmez

Bağlanır. Uzuv olarak takılır. torch'a taşıma yalnız `idrak` uzvu için
düşünülebilir, hüküm veren uzuvlar için asla.

## H10 — Sükût hakkı

`makam == "Şek"` iken model **susar**. Ölçü üçlüdür: cevap verilen /
susulan / cevap verince isabet.

## H11 — "~14.500 satır bağlanamaz" hükmü **nakzedilmiştir**

`omega_kategori*`, `hesap`, `kuantum`, `arama`, `yaklasim`, `olcek`
merkezî uzuvlardır; ölü ağırlık değildir.

## H12 — Öngörülen dalgalar (mucit usulü)

* hız → QSVT (`kuantum/qsvt.py`), Grover–Dürr–Høyer (`arama/grover.py`)
* hafıza → Nyström (`ogrenme/rkhs.py`), FNO `k_kesme`, MPS (`hesap/saklama.py`)

Bunlar sonradan yapıştırılacak eklenti değil, gradyanın kaldırılmasının
tabiî dalgalarıdır.

## H13 — Mucit usulü

Bir aksamı değiştir → dalgayı gör → sonraki aksamı düzelt → alet kökten
yenilenene kadar devam. Devamını her defasında sormadan getirmek benim
vazifemdir.

---

## İcra kuyruğu (kütükten çıkan)

| # | iş | yer | hâl |
|---|---|---|---|
| 1 | kütük | `docs/KUTUK.md` | tamam |
| 2 | envanter ve akit | `nefs/akit.py` | tamam |
| 3 | veri yoluna şahit ve sembolik alanlar | `nefs/uzaylar.py` | tamam |
| 4 | şahit uzvu | `nefs/sahit.py` | tamam |
| 5 | vekil skalerlerin yerine uzuv | `nefs/{idrak,akil,murakabe,beyan}.py` | tamam |
| 6 | sükût | `nefs/beyan.py` | tamam |
| 7 | tesir/hassasiyet ölçümü | `nefs/tesir.py` | tamam |

## Kapatılan somut kopukluklar (ölçümle)

| kopukluk | nasıl bulundu | ne yapıldı |
|---|---|---|
| `S_kebîr` bir kere yazılıp hiç güncellenmiyor; 𝒪₇–𝒪₃₂ arasındaki bütün iş kelama ulaşmıyor | 𝒪₂₁, 𝒪₂₈, 𝒪₃₆ düşürülünce `‖ΔN‖ = 0` | 𝒪₃₃ Muhakeme meclisi mevcut `S`ten toplanıyor |
| kaide `S` üzerinde uyduruluyor, 𝒪₁'in öz-dikkati satırları karıştırdığı için hiçbir kaide tutmuyor | kurala tâbi olduğu **bilinen** 4 şahitte nakz 2 şahidi düşürüyordu | kıyas ham duyu (`E`) üzerinde yapılıyor |
| şahit bölütlemesi `Z_hayal` üzerinde; odak penceresi örnek sınırlarını siliyor | kurallı ve bozuk akış aynı bölütlemeyi veriyordu | bölütleme ham `E` üzerinde |
| nakz tek turlu; bir bozuk şahit hepsini suçlu gösteriyor | 4 şahitten 1'i bozukken nakz = [0,1,2,3] | nakz kademeli: en ağır karşı örnek ayrılır, kaide yeniden kurulur |
| çelişki eşiği `δ = 0.5` sabit, `‖S‖²` ile ölçeklenmiyor | girdi iki katına çıkınca "iki kat çelişkili" | `δ = ½·ortalama(−C_ii)` |
| "karar geçmedi" hükmünün hiçbir neticesi yok; program yine uygulanıyor | `muhakeme.karar_geçti = 0` iken `S_kebîr` yine değişiyordu | karar geçmezse meclis dağılır |
| tevafuk, fazla sayma, istikrâ, nakz, yakîn zinciri ana akışta **hiç çağrılmıyor** | sıfır ithal | 𝒪₂₃, 𝒪₂₉, 𝒪₃₂, 𝒪₄₁'e uzuv olarak bağlandı |
