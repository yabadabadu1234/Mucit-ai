# ARC-AGI-2 DALI -- BÜTÜNLÜKLÜ ŞEMA (CANLI BELGE)

Dayanak fermanlar: F 3-I 277, 278, 279, 280 (`CLAUDE.md`).
İşaret: **[P]** padişahın sözü · **[Ç]** Claude çıkarımı (padişahın sözü değildir) · **[?]** açık sual.
Güncelleme usulü: iş ilerledikçe bu dosya yerinde güncellenir; eski hüküm silinmez, nakzedilirse nakz yazılır (F 3-I 179).

---

## 0. Hedef ve sınırlar

| Madde | Hüküm | İşaret |
| :-- | :-- | :-- |
| Hedef | ARC-AGI-2'yi sinir ağına dayalı, sahtekârca olmayan bir çareyle çözmek | [P] F 277 |
| Fark | Modelin içinde çalışma alanı bulunması | [P] F 277 |
| Taşıyıcı | Belirteç girdisi; dil modeli | [P] F 277 |
| Donanım | Tek GPU, 20 GB | [P] F 277 |
| Veri | Sentetik veri yeterince var; padişah verecek | [P] F 277 |
| Eski mimari | "Eskiden kalma"; F 75 ve F 110 ile gerilim, nakz mı değil mi söylenmedi | [P] + [?] S-ARC-1 |
| İlham | İnsan zihni (kesin) | [P] F 280 |

## 1. Üst şema: iki ağ ve kaide cümlesi

```
 bulmaca = {(g₁→ç₁), (g₂→ç₂), …} + test girdisi g*
        │
        ▼
 ┌──────────────┐ doğurur  ┌─────────────────────────────┐
 │ A  DÜŞÜNME   │ ───────► │ B  DOĞAN AĞ (çalışma alanı) │
 │ AĞI          │          │ ağırlık + topoloji          │
 └──────▲───────┘          │ içinde KAİDE UZAYI:         │
        │                  │ kaide cümlesi/cümleleri     │
        │                  │ (ayrık + sürekli, hudut yok)│
        │                  └──────────────┬──────────────┘
        │                                 │ ĉᵢ = B(gᵢ | cümle)
        │                                 ▼
        │                      hata = fark(ĉᵢ , çᵢ)  bütün i
        │                                 │
        │  hata azalmıyor                 │ azalıyor
        │◄──── A'ya beslenir, ────────────┤
        │      yeni uzay üretilir         ▼
        │                      B gradyanla güncellenir
        │
        └── bütün misaller doğru ⇒ B biter ⇒ ĉ* = B(g* | cümle)
            bütün bulmacalar doğru ⇒ A biter                     [P] F 277
```

- Eğitim anında A'nın tamamı, test anında A'nın bir kısmı ve B eğitilir. [P] (hangi kısım: [?])
- Kaide uzayı, kaide cümlesini tutan uzaydır; cümle, akılda tutulunca bütün bulmacanın çözülebileceğini belirtir. [P] F 278
- Cümle ayrık ve sürekli ikisi birden olabilir, birkaç cümleden oluşabilir, hudut yoktur; yalnız vektörel olması da yeter; sürekli olan mutlaka olacak. [P] F 279
- Ölçü: vektör paketi düşünceye ve davranışa tesir ettiğinde doğru netice alınıyorsa iş bitmiştir; düşüncenin kendisi kuralın yanlışlığı intibaına varıyorsa cümle o nispette değişir. [P] F 279

## 2. İnsan zihni şeması: motorlar

Padişahın tezi: insan tasavvurlar üzerinden düşünür. [P] F 280

```
 girdi (bulmaca)
    │
    ▼
 ┌────────────────────────┐        ┌────────────────────┐
 │ TASAVVUR OLUŞTURMA     │◄───────│ TECRİT MOTORU      │ tasavvur motorunun çıktısına
 │ MOTORU                 │        │                    │ tesir eder (kesin) [P]
 │ tasavvur = bir MODEL   │        └────────────────────┘
 └──────────┬─────────────┘
            │ tasavvurlar
            ▼
 ┌────────────────────────┐   tasavvurları saklar [P: öznesi ?]
 │ MANTIK MOTORU          │   tasavvurun tasdike gidişinde
 │                        │   çelişkiden korur [P]
 └──────────┬─────────────┘
            ▼
        TASDİK  ( ne olduğu padişahça bilinmiyor [P] )
            ▲
            │ tasavvur ile tasdik arasındaki bağ
 ┌──────────┴─────────────┐
 │ İSTİFHAM MOTORU        │ bağın belirsizliğini teşhis eder [P]
 └──────────┬─────────────┘
            │ bağsızlık teşhisi
            ▼
 ┌────────────────────────┐        ┌────────────────────┐
 │ STRATEJİ GELİŞTİRME    │ usul   │ MUHAKEME MOTORU    │ bağsızlığı gidermek için
 │ MOTORU                 │ ─────► │                    │ yol arar, USULDE GİDER [P]
 │ usulü BELİRLER         │        └────────────────────┘
 └────────────────────────┘
 Fark: strateji usulü belirler; muhakeme usulde yürür. [P]
```

## 3. İki şemanın bağlanması (çıkarım, teyide muhtaç)

| Şema 1 | Şema 2 | İşaret |
| :-- | :-- | :-- |
| B (doğan ağ) | Tasavvur: bir model | [Ç] "tasavvur bir modeldir" sözüne dayanır |
| Kaide cümlesinin ihtimali pₖ | Tasdikin derecesi (cezm · zan · şek, F 3-I 197) | [Ç] tasdik sorusu açık olduğundan varsayım |
| Hata azalmıyor teşhisi | İstifham motoru | [Ç] |
| A'nın yeni uzay önermesi | Strateji + muhakeme | [Ç] |
| Durum ihtimali (token ihtimali değil) | Tasdik derecesi | [Ç] F 279 (4) ile uyumlu |
| Şartlı ihtimal motoru (F 279) | Yeri belirsiz | [?] S-ARC-3 |

## 4. Tasdik hakkında (padişah "ne bilmiyorum" dedi)

Claude'un hafızasındaki malumat (yoklanmadı): mantık ilminde ilim ya **tasavvur** (hükümsüz kavrayış) ya **tasdik** (bir nispetin olumlu ya da olumsuz hükmedilmesi); tasavvur tanımla, tasdik hüccetle (kıyas, istikra, temsil) kazanılır. Projedeki F 3-I 197 tasdiki **cezm · zan · şek** diye derecelendirir. Bu, tasdikin derecesinin olasılıkla anlatılabileceğine işaret eder ([Ç]).

## 5. "Tasavvur dışında düşünce var mı" sualine Claude'un cevabı (tenkitli)

- "Tasavvur" mantık ilmindeki anlamıyla (hükümsüz kavrayış) alınırsa, hükmün öncülleri de tasavvurlardan kurulduğundan karşı misal bulmak zordur; Claude bulamadı.
- "Tasavvur" zihnî **görüntü** manasına alınırsa karşı misal vardır: hayal gücü zayıf ya da hiç olmayan insanlar (afantazi) görüntüsüz de düşünür. Bu, tezi tasavvurun görüntü değil **kavram** manasında olduğuna zorlar. Yoklanmadı.
- Beceri bilgisi (el becerisi, sezgisel hamle) kavramsız ve sözsüz işleyebilir; bunun tasavvur sayılıp sayılmayacağı tanıma bağlıdır. Yoklanmadı.

## 6. Açık sualler (numaralı, güncellenir)

| # | Sual | Durum |
| :-- | :-- | :-- |
| S-ARC-1 | F 75 ve F 110 bu dal için nakz mı, ARC mihenk mi kalıyor | açık |
| S-ARC-2 | Tecrit motoru nedir; F 2-Ƶ hafıza tecriti ile aynı mı | açık |
| S-ARC-3 | Şartlı ihtimal motoru (F 279) bu motorlar arasında nerede | açık |
| S-ARC-4 | Tasdik tam olarak nedir; hangi çıktıya tekabül eder | açık |
| S-ARC-5 | "Tasavvurları saklıyor"un öznesi: mantık motoru mu ayrı bir saklama mı | açık |
| S-ARC-6 | Durum nedir (nesne/hücre hükmü mü, kural hükmü mü) | açık |
| S-ARC-7 | Düşüncenin intibası neyle ölçülür; misallerle farkın yanında mı yerine mi | açık |
| S-ARC-8 | Durma ölçüsü ("hata azalmıyor" eşiği ölçüden türer, sabit sayı yok) | açık |
| S-ARC-9 | A'nın test anında eğitilen kısmı hangisi | açık |
| S-ARC-10 | Aşırı uydurma ölçüsü: bir misali dışarıda bırakıp sınama usulü eklensin mi | açık |
| S-ARC-11 | Izgara belirteçlemesi (satır/sütun ayracı) | ayrıntı, sona kalır |
| S-ARC-12 | Hesap bütçesi: yarışma ortamının süre ve donanım sınırı yoklanacak | yoklanmadı |

---

## 7. Tasavvur oluşturma mekanizması -- TEKLİF (Claude çıkarımı, F 3-I 281; padişah kabul etmedikçe hüküm değildir)

Padişahın şartları [P]: tasavvur tokene eşleştirilmiş vektör değildir; bir şeye eşleşmez, bizzat kendi vardır; kaynağı token, tokenin manası, ses ya da herhangi bir duyu olabilir; hissi müşterekte bir motor vardır.

### 7.1 Şartlardan çıkan altı kayıt [Ç]

| # | Kayıt | Sebep |
| :-- | :-- | :-- |
| T1 | Kaynaktan bağımsız: aynı tasavvur token, şekil ya da ses yoluyla gelebilir | "token da olabilir, ses de" |
| T2 | Kendi kendine ayakta: kaynak çekilince de durur, saklanır, çağrılır, birleştirilir | "bizzat kendi vardır" |
| T3 | Oluşturulur, bakılıp alınmaz: bağlama göre kurulur; aynı token farklı bağlamda farklı tasavvur doğurur | "oluşturma motoru" |
| T4 | Hükümsüzdür: doğru ya da yanlış değildir; doğruluk tasdikin işi | mantık ilmi |
| T5 | İç içe girer: tasavvurun parçası tasavvurdur | mutasarrıfa |
| T6 | Çalıştırılabilir: "bunu itersem ne olur" sualine cevap verir | "tasavvur bir modeldir" |

### 7.2 Mekanizma

```
 duyu kapıları (kanıt üretir, tasavvur üretmez)
   token kapısı · (ileride) ses kapısı · ...
        │ kanıt
        ▼
 ┌──────────────────────────────────────────────┐
 │ HİSS-İ MÜŞTEREK MOTORU  (bağlayıcı çalışma    │
 │ alanı + iç ekran)                             │
 │ 1D token akışından 2D İÇ EKRAN kurar          │
 │ adaylar (yuvalar) kanıtı AÇIKLAMAK için       │
 │ yarışır; birkaç tur oturma                    │
 └───────────────────────┬──────────────────────┘
                         ▼
   TASAVVUR = ( z : kendi hâli , g(z) : kendi üretici ,
                f(z,Δ) : kendi dinamiği , kimlik )
   g her kapıya geri üretebilir; f ileri simüle eder
                         │
                         ▼
   TECRİT MOTORU: arızî (konum, renk, adet) ayıklanır; soyutlama merdiveni
   hissî → hayâlî → vehmî → aklî
```

- Oluşum bir çıkarımdır: kanıtı en iyi açıklayan tasavvur bulunur (analiz yoluyla sentez). Token, bu kanıtın yalnız bir kanalıdır.
- Tasavvurun doğru kurulduğunun ölçüsü, kapılar arası tutarlılıktır: token kanalından kurulan tasavvur, iç ekranı da üretebilmelidir, tersi de.
- Tecrit: İbn Sînâ'da tecrîd, sûretin maddî lâhikalardan soyulmasıdır (hafızadan, yoklanmadı). Burada: aynı kuralın birkaç misalinde ortak kalan, kaide cümlesinin ham maddesidir (F 3-I 278).

### 7.3 Tasdike bağ [Ç]

Tasdik, iki tasavvur arasında hükmedilen nispettir. Derecesi, birinin diğerini ne kadar açıkladığıdır (cezm · zan · şek). Bu, F 3-I 279'daki "durumun tek başına ihtimali"dir. İstifham zayıf nispeti bulur; muhakeme iki tasavvuru bağlayan orta tasavvuru (orta terim) arar.

### 7.4 Riskler (kendi tenkidim)

1. Yuvalar çökebilir (hepsi aynı şeyi taşır) ya da ARC'ta işe yaramaz parçalara bölünür.
2. Yeniden üretme ölçüsü anlamlı soyutlamayı garanti etmez; kural çıkarımı için ayrıca sınanmalı.
3. Tasavvur başına ayrı tam model bellek bakımından yürümez; ortak üretici ve yuvaya özgü kod gerekir.
4. "Vektör olmayan" bir tasavvur bu donanımda yoktur; fark vektör olup olmamasında değil, üretimin çıkarımla, kaynaktan bağımsız ve üretici olmasındadır.

### 7.5 Açık sualler

| # | Sual |
| :-- | :-- |
| S-ARC-13 | Bu mekanizma padişahın "bizzat kendi vardır" şartını karşılıyor mu |
| S-ARC-14 | Tasavvurun kimliği (zamanla aynı kalması) nasıl ölçülecek |
| S-ARC-15 | Soyutlama merdiveninin basamakları ARC'ta neye karşılık gelir |
| S-ARC-16 | Tecrit, hafıza tecritiyle (F 2-Ƶ) aynı mekanizma mı |
