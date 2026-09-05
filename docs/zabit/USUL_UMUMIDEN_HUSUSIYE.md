# ▓▓▓ USUL FERMANI: UMUMİDEN HUSUSİYE -- EBEDİYYEN ▓▓▓

**Bu zabıt bir tarif değil, bir emirnâmedir. En kalın vurgularla nakşedilmiştir
ve asla unutulmayacaktır.**

---

## PADİŞAHIN SÖZÜ (harfiyen)

> *"egitim.py ve nazırlıklara yani main kodlarına yine ehemmiyet atfetmediğini,
> ayrık ayrık yeni dosyalar yazıp yazıp bağlamadan öylece bıraktığını
> görüyorum. Eskiden yaptığın her hatayı yine tekrarlamandan bıktım, **mümin
> yılan deliğinden iki kez sokulmaz!**
>
> Daha sonra terkip etmekle uğraşmamamız için iptal ettiklerimizi **anında,
> bağlı oldukları şeyleri bozmak pahasına sil**, yeni gelenleri **hiç
> oyalanmadan bağla**. Zaten bir şeyi iptal ediyorsak artık o şeye bağlı
> çalışanların da bizim yeniliğimize bağlı çalışmasını istiyoruz demektir;
> mantık icabı olan bir kaidedir.
>
> Bundan sonra böyle hatalara düşmemek için **evvela ortada hiçbir yeni dosya,
> kod, fonksiyon yokken sanki varmış gibi hayal edip en üst mertebe kodu
> güncelleyeceksin, sanki varmış gibi oraya çağrı kodunu ekleyeceksin.** Daha
> sonra fonksiyonu ayrı bir dosyada yazman serbest olabilir. Sen yazmaya
> hususiden başlayıp genelde bitiriyordun; artık bu stratejiyi **"EBEDİYYEN"**
> terk edeceksin, umumiden başlayıp hususiye gideceksin! Bunu hem hafızana hem
> zabıtlara **en kalın vurgularla nakşet, asla unutma!**"*

---

## I. TEŞHİS: HANGİ HATA TEKRARLANDI?

Bu oturumda `nefs/ayna.py` ve `main/hazine.py` yazıldı. İkisi de **hususiden**
başlandı: evvela dosya yazıldı, sonra "nereye bağlansa" diye yer arandı. Netice:

* `nefs/ayna.py` yazıldığında ne `main/egitim.py`de bir kip vardı, ne bir ayar
  alanı, ne bir rapor satırı. Tâlim hattı aynadan **habersiz** koştu.
* `main/hazine.py` bağlandı, fakat ancak dosya bittikten sonra "acaba nereye"
  diye düşünülerek. Bu, bağlanmama ihtimalini her defasında canlı tutar.

Bu tam olarak `yedek/`, `idrak/cozucu.py`, `kuantum/kubit_taksimati.py` ve
sekiz beylik modülü doğuran usuldür. Hususiden başlamak **yetimliği üretir**.

---

## II. HÜKÜM: DEĞİŞMEZ İCRA SIRASI

```
┌──────────────────────────────────────────────────────────────────────┐
│  1. UMUMİ (TAHT)      main/egitim.py · main/cikarim.py               │
│                       ────────────────────────────────────────       │
│                       Henüz OLMAYAN modülün ÇAĞRISI buraya yazılır.  │
│                       Kip eklenir. Ayar alanı eklenir. Rapor satırı  │
│                       eklenir. Dosya yokken de yazılır.              │
│                       "SANKİ VARMIŞ GİBİ."                           │
│                                    │                                 │
│                                    ▼                                 │
│  2. ARA KAT           nefs/ · ogrenme/ · kuantum/ · matematik/       │
│                       Çağrılan uzvun bağlanacağı meleke/akış yeri.   │
│                                    │                                 │
│                                    ▼                                 │
│  3. HUSUSİ            Fonksiyonun kendisi, ayrı dosyada.             │
│                       EN SON YAZILIR.                                │
└──────────────────────────────────────────────────────────────────────┘
```

### Niçin bu sıra yetimliği İMKÂNSIZ kılar

Hususiden başlanınca "bağlamak" ayrı bir iştir ve ertelenebilir; ertelenen her
şey borç olur. Umumiden başlanınca çağrı **zaten yazılmıştır**: bağlanmamış bir
dosya yazmak fizikî olarak mümkün değildir, çünkü çağrı onu bekliyordur ve
yazılmazsa taht koşmaz. Borç doğmadan ölür.

---

## III. İKİNCİ HÜKÜM: İPTAL = ANINDA İMHA

Bir usul iptal edildiği anda:

1. O usulün dosyası **derhal** silinir.
2. Ona bağlı çalışan **her şey** aynı turda yeni usule bağlanır.
3. Kırılma göze alınır: *"bağlı oldukları şeyleri bozmak pahasına."*

Sebebi mantıkîdir: bir şeyi iptal etmek, ona bağlı olanların da artık yeniye
bağlı çalışmasını istemek demektir. "Şimdilik dursun, sonra terkip ederiz"
demek iptali fiilen geri almaktır.

---

## IV. MANDAL: BU ZABIT NASIL DENETLENİR?

`tanilama/nizam.py` beylik modülü zaten sayıyor. Bu zabıt onu **bir adım öne**
alır: beylik sayısının sıfırdan büyük olması artık "borç" değil **usul
ihlâlidir**, çünkü doğru usulle beylik modül doğamaz.

`nefs/test_nefs.py:YETIM_BORCU` boş kalacaktır. Dolarsa, dolduran şey bir borç
değil, bu zabıtın çiğnenmesidir.
