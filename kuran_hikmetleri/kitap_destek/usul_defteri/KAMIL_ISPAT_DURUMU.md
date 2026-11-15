# "Bütün usulleri şu şekilde terkip etmek en kâmil hâldir" önermesinin durumu

Önerme (padişahın sözü): bütün usulleri **şu şekilde** terkip etmek en kâmil hâldir. Bunun ispatı istendi.

## Önermenin ispat edilebilir hâle gelmesi için eksik üç şey
1. **"Şu şekilde"** tarif edilmedi. Hangi terkip biçimi kastedildiği sözde yok. Şu an elimizdeki terkip: kavram kafesi + sebep çizgisi + silindirik üç boyut + demet renkleri (`kafes_ornek/`). Bu, padişahın tarif ettiği terkip olduğu söylenmedi.
2. **"Kâmil"in ölçütü** söylenmedi. Ölçüt olmadan "en" kelimesi ispat edilemez.
3. **"Bütün usuller"** listesi. Depoda dünya usullerinin tam bir kaydı yok (`USUL_TEKLIFLERI.md` yalnız T1–T15 teklifidir). `USUL_DEFTERI.md`: 49 kayıt, yalnız Crossref'ten künyesi doğrulandı; **dünya literatürünün tamamı taranamaz** (Teorem 4).

## Biçimlendirme
Bir bağlam `K = (G, M, I)`: nesneler (kelimeler), vasıflar (manalar), `g I m` = "g, m manasını taşır". Bir **sunuş** `P`, bağlamdan bir sayfaya giden eşlemedir. Ölçütler: (a) kayıpsızlık, (b) fazlalıksızlık, (c) tek bakışta okunurluk, yani sayfa başına bir **bütçe** `B` (işaret sayısı), (d) padişahın yerleşim kuralları.

## Teorem 1 (kayıpsızlık: kavram kafesi bağlamı kaybetmeden taşır)
`K`'dan kafes `B(K)` kurulur. Nesne kavramı `γ(g) = ({g}'', {g}')`, vasıf kavramı `μ(m) = ({m}', {m}'')`. Her `g`, `m` için: `g I m ⇔ γ(g) ≤ μ(m)`.
**İspat.** (⇒) `g I m` ise `g ∈ {m}'`, dolayısıyla `{g}'' ⊆ {m}'` (çünkü `{m}'` kapalı bir kümedir ve `g`'yi içerir). Bu `γ(g) ≤ μ(m)` demektir (kavramlar genişlik içermesiyle sıralanır). (⇐) `γ(g) ≤ μ(m)` ise `g ∈ {g}'' ⊆ {m}'`, yani `g I m`. ∎
Sonuç: kafes çizilince `I` ilişkisi eksiksiz geri okunur. (Temel teorem, Ganter & Wille 1999.)

## Teorem 2 (fazlalıksızlık: Hasse çizimi en az kenarla düzeni taşır)
Sonlu bir kısmî düzende, geçişli kapanışı düzenin kendisi olan **en küçük** kenar kümesi, kapsama (cover) kenarlarıdır ve birdir.
**İspat.** `a < c` bir kapsama değilse `a < b < c` olan bir `b` vardır; `(a,c)` kenarı `(a,b)` ve `(b,c)` ile geçişlilikle elde edilir, atılabilir. Kapsama kenarı ise başka kenarlardan elde edilemez (aradaki eleman yok). Bu küme düzenin yalnız kendisinden belirlendiği için tektir. ∎
Etiketleme de indirgenir: her nesne ve her vasıf yalnız bir düğümde yazılır (`γ` ve `μ`).

## Teorem 3 (usul terkibi "hepsini birden" ile değil bütçeyle kurulur)
`N` usulün her biri `c_i` işaret maliyetiyle ve `v_i` kıymetle sayfaya eklensin; sayfanın bütçesi `B` olsun. Bütçeli terkip, `max Σ_{i∈S} v_i` şartıyla `Σ_{i∈S} c_i ≤ B` çözümüdür (sırt çantası problemi). **"Hepsi" (`S = {1..N}`) ancak `Σ c_i ≤ B` ise uygundur.**
**Karşı örnek.** `v = (5, 4, 4)`, `c = (6, 5, 5)`, `B = 10`: hepsinin maliyeti 16 > 10, uygun değil. Uygun olanlar arasında en iyisi `{2,3}` (kıymet 8); en yüksek tek kıymetli `{1}` (kıymet 5) bile daha kötü. Yani "hepsini terkip etmek" önermesi bütçeli ölçütle **yanlıştır**. Bütçesiz ölçütle (`B = ∞`) doğrudur ama sayfa ölçüt (c)yi, yani tek bakışta okunurluğu, yitirir.
Sırt çantası problemi genel hâlde NP-zordur; yani "en kâmil terkip" genel olarak bir formülle ilan edilemez, bir arama sonucudur.

## Teorem 4 (tek bakışta kayıpsızlık, sabit bütçeyle, her girdi için imkânsızdır)
Sayfa `C` bit ayırt edebilsin (yani en çok `2^C` farklı sayfa). `n` nesneli, `k` vasıflı bağlam sayısı `2^{nk}`; yeniden adlandırma sınıfı sayısı en az `2^{nk}/(n!·k!)`. Kayıpsız bir sunuş, farklı sınıfları farklı sayfalara eşlemek zorundadır: `C ≥ nk − log₂(n!) − log₂(k!)`. `C` sabitken yeterince büyük `n, k` için bu sağlanamaz (örnek: `n = k = 40` için en az ≈ 1280 bit).
**Sonuç.** "Bütün girdiler için, aynı sayfada, kayıpsız ve tek bakışta" bir usul yoktur. Büyük girdide ya kayıp (özet) ya da kademeli açılış (yakınlaşma, tıklama) şarttır. Bu yüzden mutlak "en kâmil" bir sunuş **ispatlanamaz**; ancak ilan edilmiş girdi büyüklüğü ve bütçesi için karşılaştırma yapılabilir.

## Teorem 5 (usullerin kümesi kapalı değildir)
`USUL_DEFTERI.md` büyüyen bir kayıttır (bu tarama 49 kayıt çıkardı, yenisi eklenir). "Bütün usulleri terkip et" önermesi her yeni kayıtla yeniden ispat gerektirir; bir defa ispatlanıp biten bir hüküm değildir. Dünya literatürünün tamamı da bu depodan, ya da bu oturumdan taranamaz: tarama aracı Crossref ve arama motorudur, yayıncı sayfaları bot engeline takılıyor (Springer: bot doğrulaması), kitap metinleri 3-I 230 gereği izne bağlıdır.

## Neyin ispatlandığı
- Teorem 1, 2: kavram kafesinin ve Hasse çiziminin **kayıpsız ve fazlalıksız** olduğu. Bu iki özellik `kafes_ornek/` çiziminde şu şekilde ölçüldü: 37 nesne, 16 vasıf, 23 kavram düğümü, 40 kenar; kapalılık denetimi (her kavramın derunu genişliğini geri verir) kodda `assert` ile geçti (`kafes3_kafes.py`).
- Teorem 3, 4, 5: "bütün usulleri birden, tek bakışta, kayıpsız terkip eden mutlak en kâmil hâl" önermesinin **bu hâliyle yanlış / ispatlanamaz** olduğu.

## Neyin ispatlanmadığı
- Seçilen terkibin (kafes + sebep + üç boyut + demet) padişahın ölçütlerine göre **daha iyi** olduğu. Elimizde yalnız ölçüm var: kural ihlali 0, hiza sapması 0°, üstten bakışta 3 kutu çifti örtüşüyor. Okuma hızına dair deney yok.
