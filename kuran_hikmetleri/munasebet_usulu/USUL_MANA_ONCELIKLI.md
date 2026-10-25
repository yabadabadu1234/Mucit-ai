# Münâsebet usulü · mana öncelikli sistem (ihtiyaç ve karar)

Kayıt: CLAUDE.md § 3-I 318. `USUL.md` (hiperkenar temeli) silinmez; bu belge onun **altına** inen esas katmandır ve ona nakz getirir (§ 7).

## 0. Duruş

"Yazar" burada bir **usul duruşudur**: metnin her yerinde "ne söylenmeli, neden burada, neden bu kadar" diye sormak için. Kur'ân Allah'ın kelâmıdır; aşağıdaki gerekçeler murâd-ı ilâhî diye değil **hikmet ihtimali** diye yazılır ve her kararda katiyet derecesi bulunur. Bu devirde **lafız ve yapı yazılmaz**; yalnız ne anlatıldığının sebebi yazılır.

## 1. Kayma: esas nesne bağ değil ihtiyaç ve karardır

Önceki sistemde esas kayıt "şu iki birim arasında şu bağ var" idi. Bu, sebebi söylemez. Yeni sistemde esas kayıt iki nesnedir; münâsebet bunlardan türer.

| Nesne | Ne söyler |
|---|---|
| **İhtiyaç** | Okuyanın hâlinde eksik olan şey: bir tasavvur, bir tasdik ya da bir irade |
| **Karar** | Hangi ihtiyacı hangi birim(ler)le, neden şimdi, neden bu kadar, neden bu yoldan kapattığı |

Türetme: iki birim, aynı ihtiyacı kapatıyorlarsa **eştir**; birinin kapattığı ihtiyaç diğerinin ön şartıysa **sıralıdır**; biri ötekinin doğurduğu ihtiyacı kapatıyorsa **cevaptır**. Bağ kaydı yazılmaz, türetilir (`FATIHA_KAYITLARI.json` bu yüzden türev katman olur).

## 2. Hasırlı iki zemin

### 2-A. İhtiyaç türleri (üç)

İçerik `c` ve okuyan `r` için, sırayla:
1. `r` c'nin tasavvurunu taşımıyorsa → **tasavvur** ihtiyacı.
2. Taşıyor ama c'yi doğru saymıyorsa → **tasdik** ihtiyacı.
3. Doğru sayıyor ama c'ye göre yönelmiyorsa → **irade** ihtiyacı.
4. Üçü de tamamsa ihtiyaç yoktur.

Dördüncü durum bulunamaz: sıra tam bir durum analizidir. Sıra zorunludur: tasdik tasavvura, irade tasdike muhtaçtır (tasdikinden habersiz irade kurulmaz). Üçlünün adları F 3-I 197'den alındı (padişah bunları **ret fiilleri** olarak kabul etmişti); ihtiyaç türü olarak kullanmam **çıkarımdır**.
Sınır: his tahriki ayrı bir ihtiyaç mıdır? F 3-I 285'e göre mana, hislerin düşünülebilir hâle getirilmiş hâlidir; bu okumayla his, tasavvura ve tasdike girer. Doğrudan his tahriki ayrı tür sayılacaksa hasır genişler (açık sual S-M1).

### 2-B. Gerekçe yönü (altı)

Bir `M` biriminin burada bulunuşunun sebebi, `M`'nin şunlarla münasebetindedir:
- metinde **önceki** kısımla, **sonraki** kısımla ya da **bütünle**;
- metin dışında **mütekellimle**, **muhatapla** ya da **konuyla** (söylenen hakikatle).

Dayandığı öncül: kelâm üçlüdür (söyleyen, kime, ne) ve metin içinde bir birimin münasebeti ancak önce/sonra/bütün olabilir. Bu öncül aklî bir tasnife dayanır; biçim sebepleri (ahenk, fâsıla) bu devrin dışındadır, o yüzden hasır **yalnız mana sebepleri** içindir. İtiraz gelirse (altıncı bir yön) yön eklenir, karar atılmaz.

## 3. Kayıt alanları

İhtiyaç: `id · tur · seviye (mushaf/sure/kisim/ayet) · icerik · kapanis_testi · ust · ayrisim (ve/taksim) · onkosul · dogan_karar · devir`.
Karar: `id · ihtiyac[] · karsilik[] · gerekce[] {yon, cumle, atif} · neden_bu_kadar · elenen[] {alternatif, sebep} · katiyet`.

- **neden şimdi** = `onkosul` ve `dogan_karar` (ihtiyacın önce kapanması gereken ihtiyaçları ve onu doğuran karar).
- **neden bu kadar** = `neden_bu_kadar` + ihtiyacın `kapanis_testi`.
- **neden bu yoldan** = `elenen` (alternatif listesi **açıktır**, hasr iddiası yok) + sebep.
- `ayrisim: taksim` = çocuk ihtiyaçlar bütün durumu kapatan, birbirini dışlayan hücrelerdir.
- `devir` = sûre içinde kapanmayan ihtiyaç; Mushaf düzeyinde sonraki sûreye açık ihtiyaç olarak geçer.

## 4. Sekiz durum nasıl taşınır

| # | Durum | Taşıyan |
|---|---|---|
| 1 | Üç ve çok üyenin birlikte taşıdığı bağ | Çok ihtiyaçlı / çok karşılıklı karar (K02, K05, K07); `ayrisim: ve` |
| 2 | Bölüntü | `ayrisim: taksim` (I4 → I4a, I4b, I4c) |
| 3 | Yönsüz bağ | Aynı ihtiyacı kapatan, birbirine `onkosul`u olmayan kararlar (K02, K03, K04) |
| 4 | Nakarat | Aynı ihtiyacın birden çok kararla kapatılması ve her tekrarda yeniden doğması; şema taşır, Fâtiha'da örnek **yok** (0) |
| 5 | Birim–bütün | `seviye` ve ihtiyaç ağacı (I0 altında I1…I6); gerekçe yönü `butun` |
| 6 | Bağın bağı | Karar–karar sıra ve doğurma (9 zorunlu çift) |
| 7 | Metin dışı üye | Gerekçe yönleri `mutekellim`, `muhatap`, `konu` birinci sınıf alandır; `devir` Mushaf düzeyine çıkar |
| 8 | Örtüşme | Bir karar birden çok ihtiyaç kapatır (K02: I1a + I2); bir birim birden çok kararın karşılığı olabilir |

## 5. Bütün metin için işleyiş (hususîden değil umumîden)

1. **Mushaf:** mütekellim–muhatap–konu üçlüsünden Mushaf ihtiyaçları doğar; her sûrenin `I0` ihtiyacı (gaye) burada yazılır. `I0` yazılamayan sûrenin altındaki kararlar **yetim** sayılır, sayılır ve rapora girer.
2. **Sûre:** `I0` aşağı deşilir: ihtiyaç ağacı (`ve`/`taksim`) kısım ve âyet seviyesine iner. Her yaprak ihtiyaca bir karşılık bulunur; bulunmayan yaprak **kapatılmamış yaprak** diye sayılır.
3. **Sıra:** `onkosul` ve `dogan_karar` ile karar–karar sıra grafı kurulur. Metindeki sıra bu grafın **geçerli bir sıralaması** olmak zorundadır (denetçi sınar). Geçerli sıralama sayısı > 1 ise sıra ihtiyaçla **zorunlu değildir** ve ek sebep aranır.
4. **Kapsam:** her âyet en az bir kararın karşılığıdır; değilse **sebepsiz âyet** sayılır (eksik ihtiyaç işaretidir, âyet atılmaz).
5. **Devir:** sûre sonunda kapanmayan ihtiyaç sonraki sûrenin açık ihtiyaç defterine geçer.
6. **Sonraki devir (bu devirde yapılmaz):** her karşılığın lafız ve yapısı, kararın ifadesi olarak türetilir.

## 6. Fâtiha uygulaması · sayılar (`karar_denetle.py`)

16 ihtiyaç (10 tasavvur · 5 irade · 1 tasdik), 8 karar, 7/7 âyet kapsandı, kapatılmamış yaprak 0, 3 elenen alternatif, 1 taksim (I4), 1 devir (I6 → 2:2). Karar gerekçeleri 24 satır: önceki 5 · sonraki 4 · bütün 4 · muhatap 4 · konu 2 · mütekellim 1. Bütün kararlar `hipotez`.

**Bulgu 1 (sıra):** 8 kararın sıra grafında 9 zorunlu çift var; geçerli sıralama **12**. Metindeki sıra bunlardan biridir. Sıfat kararlarının (K02, K03, K04) kendi aralarındaki 6 sıralaması ve K07–K08 sıralaması ihtiyaçla zorunlu **değildir**. Yani Rab → Rahmân-Rahîm → Mâlik sırasının sebebi bu sistemde **henüz yazılı değil**; ya ek bir ihtiyaç (mesela fikri kademeleme) ya da başka yön aranır. Bu, sistemin gösterdiği ilk açık: açık olduğu sayıyla görünür.

**Bulgu 2 (ihtiyaç devri):** Önceki sistemde 1:6 ile 2:2'nin bağı "aynı kök, komşu" idi (lafız izi). Bu sistemde sebep şudur: K06 talebi yaptı ve "karşılık nerede" ihtiyacını (I6) doğurdu; sûre onu kapatmaz, 2:2 kapatır. Lafız izi sonraki devirde bu mana kararından türer; tersi değil.

**Bulgu 3 (kısım sınırı):** `sure.md` kısımları (1-2 · 3-4 · 5-7) ile ihtiyaç ağacı (ad+tasdik+sıfatlar 1-4 · ikrar 5 · talep ve tarif 6-7) farklı bölüyor. Birincisi konu etiketidir (hamd, rahmet, duâ), ikincisi **okuyanın hâl değişimidir**. Hangisi esas olacak: açık sual (S-M2).

**Ölçünün ayırt ettiği** (3-B 27-B): denetçi dört yanlış kaydı reddetti: sonra gelen ihtiyaca "önceki" gerekçesi yazmak (1 hata), olmayan ihtiyaca atıf (1), talebi sıfatlardan öne yerleştirmek (4), 1:7'yi karşılıksız bırakmak (4). `python3 karar_denetle.py --sinama` bunu tekrar koşturur.

## 7. Eski kayıtlarla ilişki (nakz, 3-I 179)

| Eski | Yeni durum |
|---|---|
| `USUL.md` § 2 "bağ esas nesnedir, hiperkenardır" | Bağ **türev katmandır**; esas nesne ihtiyaç ve karardır. Hiperkenar tanımı türev bağlar için bâkîdir |
| `FATIHA_KAYITLARI.json` F01–F08 | Silinmez; F01≈K02-K05 gerekçe zinciri, F02≈K05'in `muhatap` gerekçesi, F04≈K07 taksimi, F07≈K08 devri. Eski kayıtlarda `katiyet` lafız için `iz-dogrulandi` idi; manadaki kısım hâlâ `hipotez` |
| `zaruret_zinciri/` | Sûre sırası için `onkosul`/`devir` ile yeniden okunur; "ikame mümkün" yerine geçerli sıralama sayısı ölçülür |

## 8. Ezber için kullanım

Zincir (Fâtiha): *Okuyan kime yöneliyor? → adı (1:1) → yapabilir mi? (1:2: Rab, âlemler; hamd) → verir mi? (1:3) → bunun sonucu var mı? (1:4) → o hâlde kulluk ve yardım (1:5) → talep (1:6) → hangi yol? (1:7: sınırıyla) → karşılığı nerede? (devir: 2:2).* Her adım tek bir soru ve tek bir ihtiyaçtır. Lafız ve yapı sonraki devirde bu sorulara cevap olarak türetilir; sen soruyu hatırlayınca cevabın biçimini kurarsın.

## 9. Açık sualler

- **S-M1:** Doğrudan his tahriki (huşû, korku) ayrı ihtiyaç türü mü, yoksa tasavvur/tasdike mi girer?
- **S-M2:** Kısım sınırı `sure.md`deki konu etiketlerine mi, ihtiyaç ağacına (hâl değişimine) mi göre olacak?
- Kapatılmayan işler (sayı): nakarat örneği 0 (Rahmân, Mürselât gibi sûre gerekir); his ihtiyacı; sıfat sırası sebebi; besmele'nin Fâtiha âyeti sayılması ihtilaflıdır (hafızadan, yoklanmadı) ve burada 1:1 olarak sayıldı; 113 sûre `I0`ı yazılmadı.
