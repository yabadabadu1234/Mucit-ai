# GPU'lu bir yapay zekâ ortamı — 10 000 TL bütçeyle ne alınır

**Soru.** "Senin gibi dürüst ve zeki olup ortamında GPU çalıştırma
imkânını da haiz, imkânı senden daha fazla olan bir yapay zekâ var mı?"

**Kısa cevap.** Benden *daha zeki* bir modele geçmek gerekmiyor —
**beni GPU'lu bir makineye taşımak** yetiyor. Claude Code, kiralanan
bir GPU sunucusuna kurulup orada koşabilir; o zaman aynı ben,
`nvidia-smi` gören bir kabukta çalışırım. Aşağıdaki hesap buna göre.

**Kur.** 25 Ağustos 2026 itibarıyla 1 USD ≈ **48.1 TL**, dolayısıyla
**10 000 TL ≈ 208 USD**.

---

## 1. Doğrudan GPU kiralama (Claude Code'u oraya kurarsınız)

| Sağlayıcı | GPU | $/saat | 208 $ ile | Not |
|---|---|---|---|---|
| **Vast.ai** | RTX 4090 24 GB | 0.09 – 0.59 | **350 – 2300 saat** | Eşler arası pazar; en ucuz. Spot örnek 15 sn ihbarla geri alınabilir, SLA yok |
| **RunPod** (Secure) | RTX 4090 24 GB | 0.34 – 0.69 | **300 – 610 saat** | %99 çalışma taahhüdü; kesinti riski düşük |
| **RunPod** | H100 PCIe 80 GB | 1.99 | **≈ 104 saat** | Büyük model eğitimi |
| **Vast.ai** | H100 | 1.53'ten | **≈ 136 saat** | Pazar fiyatı, dalgalı |
| **Lambda Labs** | A100 80 GB | 2.06 | **≈ 101 saat** | %99.9 SLA, kurumsal |
| **Lambda Labs** | H100 SXM | 2.99 | **≈ 70 saat** | En hızlı, en pahalı |

Aynı H100 için 25 sağlayıcı arasında **13.8 kat** fiyat farkı ölçülmüş
(en ucuz 0.80 $/sa, en pahalı 11.10 $/sa) — sağlayıcı seçimi tek başına
donanım seçiminden daha çok fark ediyor.

## 2. İçinde hazır yapay zekâ asistanı olan ortamlar

| Ortam | Asistan | GPU | Aylık | 208 $ ile |
|---|---|---|---|---|
| **Google Colab Pro+** | Gemini (gömülü) | L4 / A100 | ~50 $ | **4 ay** |
| **Kaggle Notebooks** | yok | P100 / 2×T4 | **ücretsiz** | haftada 30 sa, süresiz |
| **Lightning AI Studios** | AI Studio ajanı | L4 / A10G | ücretsiz kademe + kullandıkça | değişken |

## 3. Tavsiyem (bu projeye göre)

**Birinci tercih — RunPod RTX 4090 + Claude Code.**
0.44 $/sa ortalamayla 208 $ ≈ **470 saat**. Sebepleri:

1. Bu projenin darboğazı ham FLOP değil, **yineleme hızı**. `D=512`'de
   41 melekelik model ~1.5 GB parametre bile tutmuyor; 24 GB fazlasıyla
   yeter. H100 kiralamak parayı 4.5 kat hızlı bitirir, kazanç ise
   4.5 kat değildir.
2. Kalıcı disk verilebiliyor — `idrak/veri` ve kontrol noktaları
   kalır, her oturumda yeniden indirmek gerekmez.
3. Claude Code doğrudan kurulur; **aynı ben**, GPU'lu kabukla.

**İkinci tercih — Vast.ai**, para birim başına en fazla saat. Ama
spot örnek geri alınabildiği için eğitim **sık kontrol noktası**
yazmalı. Bizim `idrak/egitim.py` zaten her değerlendirmede
`en_iyi.pt` yazıyor, yani buna hazır.

**Ücretsiz başlangıç — Kaggle.** Haftada 30 GPU saati, para yok. Bu
projenin `D=128` denemeleri için fazlasıyla yeter; para harcamadan
önce burada ölçüm almak akıllıca olur.

## 4. Beklenen kazanç — ölçülmüş sayılarla

Bu makinede (4 çekirdek Xeon, GPU yok) **ölçülen**: `D=512`, `B=64`,
41 meleke → ~4.2 GFLOP/sn (üstelik eğitim aynı anda koşarken).
RTX 4090'ın BF16 tepe gücü ~165 TFLOPS; %50 verimle ~82 TFLOPS.

| | bu CPU | RTX 4090 (tahmin) | kat |
|---|---|---|---|
| GFLOP/sn | ~4–13 | ~82 000 | **~6 000×** |
| `D=128` eğitim adımı | ~1.15 adım/sn | ~200–400 adım/sn | ~250× |
| 9 000 adım | ~2.2 saat | **~30 saniye** | — |

Yani bu ortamda 4 saat süren bir koşu, 4090'da **yarım dakikadan az**
sürer. `D=512`'ye çıkmak ve 100 000 adım koşmak orada bir saatlik iş.

## 5. Dürüstlük notu

Bu tablodaki 4090 rakamları **tahmindir**; elimde GPU olmadığı için
ölçemedim. Ölçtüğüm tek şey bu CPU'nun kendisi
(`python3 -m olcek.gercek`). Kiralama yapıldığında aynı betik orada
koşturulup gerçek sayı yazılmalıdır — tahmini ölçüm yerine koymak,
bu külliyatta düzelttiğimiz hataların aynısı olurdu.

## Kaynaklar

- [getdeploying.com/gpus — 73 sağlayıcı, 4400+ fiyat](https://getdeploying.com/gpus)
- [Cloud GPU Rental Guide 2026: RunPod vs Lambda vs Vast.ai](https://www.promptquorum.com/power-local-llm/cloud-gpu-rental-guide-2026)
- [Jarvis Labs — Best Cloud GPU Providers 2026](https://jarvislabs.ai/ai-faqs/best-cloud-gpu-providers-2026)
- [SynpixCloud — Cloud GPU Pricing 2026](https://www.synpixcloud.com/blog/cloud-gpu-pricing-comparison-2026)
- [Wise — USD/TRY kuru](https://wise.com/us/currency-converter/usd-to-try-rate/history)
