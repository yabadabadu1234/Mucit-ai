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

Sızıntının şu ana kadar daraltıldığı yer: `main_egitim_dongusu.py` içindeki
`_tekil_r_adimi` kapanışları. Her adımda R adet üretiliyor ve hiçbiri serbest
kalmıyor; `torch.utils.checkpoint(..., use_reentrant=False)` bunları yeniden
hesaplama için grafta tutuyor, kapanış da `D0_op_sabit` ile `e3_sinir_sabit`i
beraberinde tutuyor. Kapanış sayısını doğrudan saymak için:

    kapanis = sum(1 for f in gc.get_objects()
                  if isinstance(f, types.FunctionType)
                  and f.__qualname__.endswith('_tekil_r_adimi'))

Grafı ayakta tutan asıl çapa **henüz bulunamadı**; sızıntı giderilmedi.

## Pareto operatörü doğrulaması

`dogrula_pareto.py`, PCGrad + MGDA'nın skaler cebir hâlini (R matrisi, A matrisi,
`G = A R Aᵀ`, `w = Aᵀα`) düz vektörlerle yazılmış referans uygulamaya karşı
karşılaştırır. Beklenen: alpha ve gradyan farkları float32 birikim mertebesinde
(~1e-7 nispi). Bit-aynılık beklenmiyor.
