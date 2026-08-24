# nefs — Nefs-i Müdrike mimarisi: 41 melekenin koşabilir hâli

Projenin üçüncü modülü. Kaynak iki risale `docs/kaynak/` altında:

* `nefs_i_mudrike_41_meleke.tex` — klasik riyazî zemin, 41×11 denklem
* `nefs_i_mudrike_hott_topos.tex` — HoTT / (∞,∞)-topos / kübik zemin, 41×12 denklem

```
python3 -m nefs.test_nefs      # 35 sınama (~1.3 s)
python3 -m nefs.akis           # küllî akışın raporu
```

Yalnız `numpy` gerekir.

## Ne iddia ediliyor, ne edilmiyor

**Bu modül mimariyi koşturur; ağırlıklar eğitilmemiştir.** Tohumlu
sözde-rastgele ve kısmen analitik kurulurlar. Dolayısıyla "sistem doğru
düşünüyor" diye bir iddia **yoktur**. İddia edilen ve sınanan üç şey var:

| kuşak | ne gösterir |
|---|---|
| **A. Sözleşme** | 41 melekenin hepsi koşuyor, alanları dolduruyor, boyutları koruyor; akış sırası hem bağımlılıkları hem metnin küllî silsilesini sağlıyor |
| **B. Riyazî özdeşlikler** | Metnin sınanabilir denklemleri fiilen sağlanıyor — bunlar ağırlığa bağlı olmadığı için eğitimsiz de doğrudur |
| **C. Davranış** | Teemmül duruyor, tefekkür potansiyeli düşürüyor, tenakuz zıt delilde yükseliyor, muhayyile haddinde kalıyor |

Anlam, eğitilmiş ağırlıkta yaşar; burada yoktur ve olduğu söylenmez.

## Mimari

```
uzaylar.py   temsil uzayları, Durum kaydı, müşterek işlemler, çelişki çekirdeği
meleke.py    Meleke sözleşmesi (okur / yazar / ihtiyari) ve sicil
idrak.py     𝒪₁–𝒪₁₀    duyudan mahiyete
akil.py      𝒪₁₁–𝒪₂₄   hüküm, gaye, burhân
murakabe.py  𝒪₂₅–𝒪₃₆   nefsin kendi hükmünü denetlemesi
beyan.py     𝒪₃₇–𝒪₄₁   hükmün dışarı çıkışı
akis.py      küllî ittisâl: akış sırası ve işletici
```

`Durum` alanlarını okuyup yazma **sözleşmesi** her melekede bildirilir ve
her adımda denetlenir; 41 melekelik zincirde sessizce `None` taşımak
imkânsızdır. Nefsin tabiî geri beslemeleri (ör. 𝒪₇ Mana'nın henüz
kurulmamış gayeye bakması) `ihtiyari` olarak işaretlenir ve bağımlılık
çizgesine katılmaz.

**𝒪₁₃ Tasdik akışta iki kere koşar** — bir kere kendi mertebesinde, bir
kere 𝒪₃₃ Muhakeme meclisinden sonra **mühür** olarak. Metnin kapanış
bölümü bunu böyle söylüyor ("Muhakeme meclisinde Tasdik mührünü alarak").

## Sınanan riyazî özdeşlikler

| meleke | özdeşlik | netice |
|---|---|---|
| 𝒪₅ Tecrit | `β₀` = bileşen sayısı, `β₁ = |E|−|V|+β₀` | dört bilinen çizgede tam |
| 𝒪₅ | `Δ = I − D^{-1/2}AD^{-1/2}` spektrumu `[0,2]` | sağlanıyor |
| 𝒪₈ Tahlil | HSIC bağımsızlıkta ~0 | `h₀ = 0.0006`, bağımlıda `> 5h₀` |
| 𝒪₁₁ Tenakuz | hiçbir önerme kendisiyle çelişmez; nakîziyle çelişir | ikisi de |
| 𝒪₁₇ İhtimal | Bayes normalizasyonu `Σ = 1` | `< 10⁻⁹` |
| 𝒪₁₈ Kıyas | bilinen `A` eşlemesini geri bulma | bağıl hata `< 10⁻⁶` |
| 𝒪₂₂ İllet | `Tr(exp(A∘A)) − d = 0` | DAG'da tam 0, devirde pozitif |
| 𝒪₂₂ | arka kapı `P(y|do(x))` | `0.8`, ham bağlanım yanlı |
| 𝒪₂₃ Mantık | modus ponens doğruluk tablosu | dört satır tam |
| 𝒪₃₂ Makam | Şek/Zan/Yakîn/Vehim parçalanışı tam+ayrık+monoton | 20 001 noktada |
| 𝒪₄₀ Sanat | `φ² = φ + 1`; harmoni simetrikte 1, ters simetrikte 0 | tam |
| her yer | `R = exp(θX)`, `X` ters simetrik ⟹ `RᵀR = I` | `< 10⁻¹⁰` |

## Metinden ayrıldığım yerler — hepsi ölçümle

Kaynak metne sadakat, metni **çalışmayan hâliyle kopyalamak** demek
değil. Aşağıdaki altı yerde metinden ayrıldım; her birinde önce metnin
yazdığı hâli kurdum, ölçtüm, ve ölçüm sebebiyle değiştirdim. Hepsi ilgili
dosyada gerekçesiyle yazılıdır.

1. **𝒪₁₁ çelişki çekirdeği.** "Hiçbir önerme kendisiyle çelişmez" şartını
   sağlamak için çekirdeği ters simetrik (`W = A − Aᵀ`) aldım. Sınama
   bunu **yakaladı**: `SᵢᵀW(−Sᵢ) = 0`, yani bir önerme kendi *nakîziyle*
   de çelişmez hâle geliyor. Ölçüm: birbirini teyit eden girdide tenakuz
   `0.158`, biri diğerinin tam zıddı olanda `0.017` — ölçü ters
   çalışıyordu. Çekirdek `C = −S(AᵀA)Sᵀ` oldu; yarı-pozitif çekirdek her
   iki şartı da sağlar.

2. **𝒪₃ fantezi süzgeci.** Metinde `Ẑ·𝕀(Serbestlik ≤ τ)` — eşik aşılınca
   çıktı sıfırlanır. Eğitilmemiş ağırlıkta Serbestlik `4`–`792` çıkıyor ve
   süzgeç **her seferinde** tetikleniyor; muhayyile bütünüyle susuyor.
   Sert kesme yerine adım `η` uyarlanır: serbestliği `τ`nun altına sokan
   en büyük adım seçilir. Netice aynı şartı sağlar (`Serbestlik ≤ τ`,
   sınanıyor) ama sureti yok etmez.

3. **𝒪₄₀ simetrik harmoni.** Metinde `1 − ‖Y − Yᵀ‖_F`. Paydasız hâlde ölçü
   `Y`nin büyüklüğüne bağlı; ayrıca `‖Y−Yᵀ‖ ≤ 2‖Y‖` olduğundan ölçü
   `[−1,1]`e taşıyor — nitekim "ahenk" `−0.351` çıktı. `2‖Y‖`a bölündü;
   şimdi `[0,1]`de, ters simetrikte tam 0, simetrikte tam 1.

4. **𝒪₃₂ makam parçalanışı.** Metindeki üç şart `P < 0.5 − ε_şek`
   aralığını **kapsamıyor**; orada `Makam` tanımsız kalıyordu. O aralık
   **Vehim** (aleyhte zan) diye adlandırıldı. Parçalanış artık tam, ayrık
   ve monoton.

5. **𝒪₁₆ deneme-yanılma.** Metindeki `θ ← θ + α r ∇log π` tabansız
   REINFORCE'tur. Kurulup ölçüldü: ödül `−0.49`'dan `−0.70`'e **düştü**.
   Sebep, bütün ödüller negatifken her hamlenin cezalandırılmasıdır.
   `r − taban` (kayan ortalama) eklendi; artık 6 tohumun 6'sında öğreniyor.

6. **𝒪₂₅ teemmül.** Metindeki `M + Attn(...)` artığı yakınsamadı (12 turda
   fark `0.51`'de takıldı). Sönümlü harman `(1−κ)M + κY` büzücüdür;
   `𝒦 = 200`, `ε = 10⁻³` ile tipik durma 30–60. turda.

Ayrıca bir **iddiamı geri aldım**: "ardışık farklar monoton azalır" diye
sınadım, kaldı. Büzücü eşleme geometrik yakınsama garanti eder, tur tur
monotonluk **etmez**. Ölçülen şey artık `azalma_oranı = son/ilk` (`< 10⁻³`)
ve geriye sıçrama sayısı (tipik 0, âzamî 2).

## Bulunan bir hata: süreçler arası tekrarlanabilirlik

`Parametreler.W` ağırlık tohumunu Python'un `hash()`inden türetiyordu.
Dizge hash'i **süreç başına rastgeleleşir** (`PYTHONHASHSEED`), dolayısıyla
her koşuda başka ağırlık üretiliyordu; aynı sınama ardışık iki koşuda bir
geçip bir kaldı. Süreç *içi* tekrarlanabilirlik sınaması bunu göremez.
`zlib.crc32`e geçildi ve `PYTHONHASHSEED`i değiştirerek koşan bir sınama
eklendi.

## Öbür modüllerle bağı

`yaklasim` modülünün usulleri burada **fiilen** koşuyor:

* 𝒪₁ Müşahede'de **FNO çekirdeği** (spektral ön-süzgeç)
* 𝒪₃ Muhayyile'de **KAN biçimi** (kenarlarda RBF, düğümlerde toplam)
* 𝒪₂₂ İllet'te **do-hesabı** ve NOTEARS asiklik ölçütü
* 𝒪₁₉ Temsil'de RKHS eşlemesi ve devir sadakati

Metnin tip teorisi tarafındaki satırları (`Path`, `transp`, `hcomp`,
`unglue(glue …)`, `Equiv`, `Lan_K`) bu modülde **hesaplanmaz**; onlar
`omega_kategori` / `omega_kategori_nbe` tarafındadır ve orada makine ile
denetlenir. Burada yerlerine, aynı şeyin sayısal karşılığı olan ölçüm
konur ve öyle işaretlenir.

## Durum

```
35 sınamanın 35'i geçiyor (~1.3 s)
41 melekenin 41'i kayıtlı ve koşuyor; akış sırası geçerli
```
