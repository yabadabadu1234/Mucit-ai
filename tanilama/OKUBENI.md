# Tanılama (av) betikleri

Bu klasördeki betikler eğitim döngüsündeki bellek sızıntısını ve Pareto
operatörünün doğruluğunu araştırmak için yazıldı. Hepsi tek başına çalışır ve
`local_run/config.json` + `local_run/verisetleri_manifest.json` ile CPU üzerinde
koşar. Depo kökünden çalıştırın:

    python tanilama/<betik>.py

## Sızıntı avı — kullanım sırası

| Betik | Ne yapar | Ne bulmuştu |
|---|---|---|
| `ram_repro.py` | Sadece checkpoint kaydet/yükle çevrimini döngüye sokar, RSS ölçer | Çevrim sızdırmıyor; RSS düzleşiyor |
| `sizinti_avi.py` | 4. ve 12. adımda canlı tensörleri şekle göre gruplar, farkı basar | Büyüyenler D0 operatör blokları `(E,d_e,d_v)`, çoğu `grad_fn` taşıyor |
| `referans_avi.py` | Sızan tensörlerin geri-referans zincirini ve nesne türü sayımlarını basar | Adım başına 1 `E3_SinirOperatorleri` + 1 `LifLaplasyenOperatoru` |
| `sahip_avi.py` | Bu nesneleri öznitelik / kapanış olarak tutanları arar | Hiçbir nesne öznitelik olarak tutmuyor |
| `graf_capasi.py` | Modüllerde ve optimizer'da `grad_fn` taşıyan uzun ömürlü tensör arar | Sıfır — çapa modül durumunda değil |
| `kok_avi.py`, `kok_avi2.py` | Geri-referans BFS ile çerçeve/traceback köküne ulaşmayı dener | Kök bulunamadı; zincir C++ autograd düğümlerinde kopuyor |

## Kök sebep (bulundu ve giderildi)

`NvmeTakasYoneticisi.pack_hook_diske_tahliye`, tahliye etmediği tensörü
**olduğu gibi** döndürüyordu:

    return tensor          # hatalı
    return tensor.detach() # doğru

PyTorch'un yerleşik `SavedVariable` mekanizması, bir tensör onu üreten düğümün
kendisi tarafından kaydedildiğinde `grad_fn`'e **zayıf** referans tutar; bu,
düğüm ile kaydedilen tensör arasında döngü oluşmasını engellemek içindir.
`saved_tensors_hooks` ile pack kancası devreye girince bu koruma devre dışı
kalır: kanca ne döndürürse graf onu güçlü referansla saklar. Canlı tensör
döndürülünce tensör kendi `grad_fn`'ini güçlü tutar ve C++ tarafında Python çöp
toplayıcısının kıramadığı bir döngü doğar.

Sonuç: her adımın `_CheckpointFrame`'i, içindeki `recompute_fn` kapanışı ve o
kapanışın yakaladığı her şey (`D0_op_sabit`, `e3_sinir_sabit`, aktivasyonlar)
kalıcı olarak yaşar. Ölçülen etki: yerel konfigde adım başına +25 MB, Kaggle
konfigünde +275 MB.

`detach()` depoyu paylaşır (ek bellek yok), `grad_fn`'i yoktur (döngü kırılır),
sürüm sayacı ortaktır (yerinde-değişim tespiti bozulmaz). Gradyanların
değişmediği bit-aynı olarak doğrulandı.

Ayrıca GPU yokken hiçbir tahliye mümkün olmadığından `kapsam_muhafizi_aktifles`
artık CPU'da `nullcontext` döndürüyor.

### Gerileme testi

    python tanilama/sizinti_gerileme_testi.py

Gerçek eğitim döngüsünü 7 adım koşturur, kapsam muhafızını CPU'da da zorla
aktif eder ve canlı `E3_SinirOperatorleri` sayısının adımlar arası büyümediğini
doğrular. Düzeltme geri alındığında büyüme 5, çıkış kodu 1 olur; düzeltme
yerindeyken büyüme 0'dır.

## Pareto operatörü doğrulaması

`dogrula_pareto.py`, PCGrad + MGDA'nın skaler cebir hâlini (R matrisi, A matrisi,
`G = A R Aᵀ`, `w = Aᵀα`) düz vektörlerle yazılmış referans uygulamaya karşı
karşılaştırır. Beklenen: alpha ve gradyan farkları float32 birikim mertebesinde
(~1e-7 nispi). Bit-aynılık beklenmiyor.
