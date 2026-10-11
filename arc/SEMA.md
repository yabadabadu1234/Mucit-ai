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
