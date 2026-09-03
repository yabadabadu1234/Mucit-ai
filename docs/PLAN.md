# KÜLLÎ PLAN — padişahı hakikaten padişah yapmak

> Kullanıcı hükmü: *"Padişahın modelin kendisi olduğunu unutmamalısın.
> Sadece içe aktarıp rapor verdirmek o kodları padişaha bağladığını
> göstermez… Mucit ol mucit, yazılımcı olma."*
>
> **Ana hedef: ARC görevlerinin en az YARISININ tam doğru çözülmesi.**
> İspatı test değil, **padişahın kendisini koşturmak**tır.

---

## 0. EVVELKİ HATAMIN İTİRAFI

H123'te 129 modülü `nefs/divan.py` ile içe aktarıp "beylik 0" ilan
ettim. `tanilama/nizam.py` de bunu doğruladı — çünkü o da **içe
aktarma** kapanışı ölçüyor. İkisi de doğru şeyi ölçüyor fakat yanlış
şeyi: **bir modülün yüklenmesi, padişahın onu çalıştırdığını
göstermez.**

Doğru ölçüt `tanilama/tefti.py`dir: padişah koşarken `sys.setprofile`
ile **fiilen çağrılan** her (dosya, fonksiyon). Bundan sonra "bağlı"
kelimesi yalnız bunu ifade eder.

---

## 1. PADİŞAH KİM?

```
ogrenme/kaggle_donanim.py :: kos()
    └── nefs/kulli_egitim.py :: KulliEgitim.kos()
            ├── EĞİTİM   → parametreler Θ
            └── ÇIKARIM  → değerlendirme: tam_çözülen / deneme
```

**Ölçüt tektir:** `d["tam_çözülen"] / d["deneme"] ≥ 0,50`.
Başka her sayı (entropi, sadakat, korelasyon) bu ölçüte hizmet ettiği
kadar kıymetlidir.

---

## 2. KÜLLÎ TEŞHİS — niçin şu an sıfıra yakın

Bu turlarda ölçülen dört yapısal hakikat, hepsi aynı yere çıkıyor:

| Kütük | Ölçülen | Neticesi |
|---|---|---|
| H115 | Schmidt rütbesi her χ'de doyuyor | akış **hacim kanunu** dolaşıklık üretiyor |
| H105/H121 | hüküm alanlarında tesadüf üstü fazlalık ≈ 0 | alanlar **yapısız** |
| H129 | ARC'nin her görevi zann-ı gālib'e düşüyor, makam onu taşıyamıyor | hüküm **doğru dereceyi gösteremiyor** |
| H130 | veri → kelam hükmü **atlıyor** | beyan hükümsüz konuşabiliyor |

**Tek cümlelik teşhis:** akış bir *karıştırıcı*dır, bir *muhakeme*
değil. Kırk bir meleke dalgayı büküyor fakat hiçbiri **bir şey
kurmuyor**; netice âzamî karışık bir durum ve ondan okunan düzgün bir
dağılım.

ARC'de yarıyı çözmek için gereken şey daha çok kapı değil, **bir
muhakeme çevrimi**dir.

---

## 3. ANA ALGORİTMA — MÜDRİKE ÇEVRİMİ

Kullanıcının tarifi aynen şudur ve mimarî karşılığı vardır:

> *"acaba bunlar benden ne istiyor, acaba burada konuşurken sanatlı mı
> konuşmalıyım bir şey mi çözmeliyim, hmmm, sürekli bir girdi var bir
> de çıktı var, herhalde bu bir bulmaca, hmmm, burada bir sürü renk
> rastgele dizilmiş gibi duruyor, hmm, rastgele olsa ben nasıl cevap
> bulacağım, demek ki rastgele değil hmmm"*

Bu **bir dizi hüküm**dür ve her biri ölçülebilir:

```
1. VAZİFE NEVİ    "benden ne isteniyor?"
   girdi–çıktı çifti var mı → BULMACA;  yoksa → KELÂM
   ölçüt: gösterim çifti sayısı ≥ 2  → mizan/istikra

2. TESADÜF MÜ?    "rastgele olsa ben nasıl cevap bulurdum?"
   çıktı girdiden kestirilebiliyor mu → yapı var
   ölçüt: karşılıklı malûmat / sıkıştırılabilirlik

3. ÖRTÜ KAPANIYOR MU?   "her örnek aynı kaideye mi bakıyor?"
   ölçüt: Čech H¹ (nefs/operad.py) — kapanmıyorsa SÜKÛT

4. KÂİDE NEDİR?   "hangi dönüşüm?"
   ölçüt: idrak/cozucu.py — ispatlı çözüm ya da sükût

5. YAKÎN NE MERTEBEDE?
   ölçüt: mizan/istikra + mizan/munazara — zann-ı gālib'in altındaysa sus

6. BEYAN          yalnız 5'ten geçerse; hükümsüz kelâm YASAK
```

**Bu çevrim ARC'ye mahsus değildir.** Kullanıcının şartı buydu:
*"ARC ile normal vazifeler arasında ayrım yapmak zorunda
kalmayalım."* 1. adım vazife nevini kendi kendine tayin eder; ARC
dalına da kelâm dalına da aynı kapıdan girilir.

---

## 4. BEYAN KAPISI — kullanıcının kat'î kararı

𝒪₃₇ Fesâhat, 𝒪₃₈ Talâkat, 𝒪₃₉ Belâgat, 𝒪₄₀ Sanat **ham veriden
beslenemez**. Mana yalnız tasdik mührü basılmış muhkem hükümden akar.

| Meleke | ESKİ girdi | YENİ girdi |
|---|---|---|
| 𝒪₃₇ Fesâhat | `veri`, `kelam` | `tasdik`, `yerel`, `kelam` |
| 𝒪₃₈ Talâkat | `veri`, `kelam` | `tasdik`, `kelam` |
| 𝒪₃₉ Belâgat | `makam`, `kelam`, `yerel` | `makam`, `tasdik`, `kelam` |
| 𝒪₄₀ Sanat | `veri`, `kelam` | `makam`, `kelam` |

**İspatı:** `nefs/illet.py :: kelam_ayrismasi()` — hüküm şartıyla
d-ayrık **True** olmalı. Şu an `False`.

---

## 5. İCRA SIRASI

1. **Teftiş** (`tanilama/tefti.py`) — ölü dosyaları bul. ✔ kuruldu
2. **Beyan kapısı** — 𝒪₃₇/₃₈/₃₉/₄₀ veriden koparılır; d-ayrışma ile ispat
3. **Müdrike çevrimi** (`nefs/mudrike.py`) — 6 adımlı hüküm zinciri,
   padişahın çıkarım yolunun **merkezi**
4. **Çözücü hattı** — `idrak/cozucu.py` ispatlı çözüm veriyor; padişaha
   fiilen bağlanır (şu an çıkarım onu çağırmıyor)
5. **Ölü dosyalar** — teftişin bulduğu her dosya ya çevrime girer ya
   kütüğe "uzuv değil" diye yazılır. İkisinin ortası yok.
6. **Padişahı koştur** — `tam_çözülen/deneme` ölç, hedefe kadar tamir et.

---

## 6. NE İDDİA ETMİYORUM

Bu plan bir vaat değil bir **istikamet**tir. Her adımın ölçütü
yazılıdır ve kırmızı yanabilir. Hedefe varılmazsa varılmadığı yazılır;
"çözdüğünü iddia etmiyorum" deyip kenara çekilmek de yok, olmayan bir
başarıyı ilan etmek de.
