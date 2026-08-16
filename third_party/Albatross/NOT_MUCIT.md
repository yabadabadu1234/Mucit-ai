# Bu klasör hakkında

Bu, https://github.com/BlinkDL/Albatross reposunun (kullanıcı isteğiyle
incelenmek üzere) düz dosya kopyasıdır -- kendi git geçmişi kaldırıldı,
`harici_llm/`'deki üretim koduna DAHİL EDİLMEMİŞTİR/bağlanmamıştır.

## İnceleme özeti

README'deki "145 token/s" ile "11289 token/s" gibi görünüşte farklı
sayılar FARKLI YÖNTEMLER değil; AYNI motorun (örn. `faster3a_2607/
rwkv7_fast_v3a.py`) FARKLI B (batch/eşzamanlı dizi sayısı) ve T (prefill
uzunluğu) değerleriyle ölçülmüş sonuçlarıdır:
  - B=1, T=1  -> 145 tok/s   (tek dizi, tek adım -- bant genişliği sınırlı)
  - B=1, T=256 -> 14199 tok/s (tek dizi ama 256 tokenlik prefill -- matris
    çarpımları büyüyüp GPU'yu doyurur)
  - B=256, T=1 -> 13134 tok/s (256 BAĞIMSIZ dizi aynı anda, tek adım --
    ağırlık okuma maliyeti 256 diziye bölünür)

Yani hızı asıl artıran, bizim `harici_llm/rwkv_batch.py`'de (2026-08-16
tarihli commit `faa6254`) zaten uyguladığımız ve GERÇEK `rwkv` paketine
karşı sayısal doğrulaması yapılmış fikrin AYNISI: TEK GPU'da AYNI
ağırlıkları paylaşan ÇOKLU bağımsız diziyi TOPLU işlemek.

Albatross'un kendisinin (bu klasördeki kod) sağladığı EK kazanç ise
RTX5090'a özel, elle ayarlanmış cuBLASLt algoritma tabloları
(`rwkv7_fast_v3a.py` içindeki `HEAD_ALL_LOGITS_GEMM_4096` vb. sözlükler,
"tune linear_orig_layout for your GPU" notuyla) ve çalışma-zamanında
derlenen özel CUDA kernelleri (`cuda/*.cu`, `torch.utils.cpp_extension.load`
ile). Bunlar GPU'ya özel ayar gerektirir, Kaggle'ın L4/T4 gibi farklı ve
muhtemelen daha eski CUDA araç zincirine sahip ortamında doğrulanmadan
kullanmak riskli ("görünüşte doğru ama gerçekte çalışmayan kod" riski) --
bu yüzden entegre edilmedi, yalnızca fikri alındı.
