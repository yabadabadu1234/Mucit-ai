# KAGGLE — 4 cihazda küllî eğitim

Bu vesika, modelin Kaggle defterinde nasıl koşturulacağını ve **neyin
ölçüldüğünü, neyin ölçülmediğini** yazar.

---

## 1. Tek hücrelik başlangıç

Kaggle defterinde **Settings → Accelerator: GPU**, **Internet: ON**.
Aşağıdaki kodu tek hücreye yapıştırın:

```python
import os, sys, subprocess

KOK = "/kaggle/working/Mucit-ai"
DAL = "claude/project-gaps-integration-ubwi2r"

if not os.path.isdir(KOK):
    subprocess.run(["git", "clone", "--depth", "1", "-b", DAL,
                    "https://github.com/yabadabadu1234/Mucit-ai.git", KOK],
                   check=True)
sys.path.insert(0, KOK)
os.chdir(KOK)

assert os.path.isdir(os.path.join(KOK, "idrak/veri/arc_agi_2")), \
    "ARC verisi bulunamadı: idrak/veri/arc_agi_2"

from hesap.donanim import rapor
print(rapor())

from ogrenme.kaggle_donanim import kos
netice = kos(zorla=None,                       # donanıma göre kendi seçer
             cikti="/kaggle/working/nefs_dalga",
             mukayese=True)
```

Hücreyi `python -m main.kaggle --hucre` ile de bastırabilirsiniz.

`zorla` üç değer alır: `"kısa"` (CPU), `"orta"` (tek GPU), `"azamî"`
(çok GPU). Verilmezse **yoklanır**: `≥2` cihaz ve `≥40 GB` toplam VRAM
varsa azamî, tek GPU varsa orta, hiç yoksa kısa.

---

## 2. Paralellik nasıl kuruldu

Gradyan **yoktur** (kütük H3). Bunun doğrudan bir neticesi vardır:
cihazlar arası `all_reduce` de yoktur, `DistributedDataParallel` de.
Bölünen şey ağırlık değil **iştir**:

| iş | tabiatı | nasıl bölünüyor |
|---|---|---|
| `ℒ_Nefs(Θ)` kübit ileri geçişi | her `Θ` bağımsız | `multiprocessing` süreçleri (çekirdek kadar) |
| NQS genlik + Metropolis örneklemesi | yığın hâlinde | `hesap/donanim.topla_paralel` → cihaz başına dilim |
| Grover özyinelemesi | `k+1` sayı | bölünmüyor; zaten bedava |

`hesap/donanim.parcala` artığı **ilk parçalara** dağıtır; `n//k` + kalan
usulü son cihaza `k−1` fazla iş yükler ve 4 cihazda %25'e varan
dengesizlik doğurur.

**Tek cihazda netice birebir aynıdır.** `topla_paralel`, tek cihazda
`f(X)`den başka bir şey değildir; paralellik hiçbir davranış farkı
doğurmaz, yalnız hızı değiştirir.

---

## 3. 84 GB nereye gidiyor — dürüst cevap

**Çoğu boşta kalır.** Bu bir kusur değil, mimarînin neticesidir:

* `2^N` hiçbir yerde açılmaz. NQS parametreleri megabaytlar,
  Grover katsayıları (`k+1` karmaşık sayı) kilobaytlar tutar.
* VRAM'i tüketen tek şey **yığın büyüklüğüdür** (`ornek`, `zincir`).

Onun için `AZAMI_KAGGLE` ayarında büyütülen şey "belleğe sığdırma
numarası" değil **örnek sayısıdır** — yani istatistikî sağlamlık.
Kütükteki H54/2. borç (*"8 örnekli AS-GEK istatistikî olarak
imkânsız; 250 boyutlu uzayda asgarî 10·d = 2 500 değerlendirme
gerekir"*) ancak böyle kapanır: `azamî` ayarında çevrim başına 4 096
örnek, 400 çevrimde ~1,6 milyon kayıp değerlendirmesi.

---

## 4. Ayarlar — hepsi açık, hiçbiri koda gömülü değil

`nefs/kulli_egitim.py:EgitimAyari`. Üç hazır ayar:

| alan | kısa-CPU | orta | azamî-Kaggle |
|---|---|---|---|
| `satir_kubiti` | 4 | 6 | **12** |
| `bag` (χ) | 16 | 32 | **256** |
| `mera_kademe` | 3 | 3 | **5** |
| `gorev` | 24 | 120 | **1000** |
| `ornek_sayisi` | 8 | 24 | **256** |
| `pencere` | 8 | 8 | **32** |
| `bit` (parametre başına) | 6 | 8 | **10** |
| `nqs_gizli` | (48,) | (96, 64) | **(512, 256, 128)** |
| `nqs_derece` | 5 | 6 | **8** |
| `cevrim` | 6 | 40 | **400** |
| `ornek` | 24 | 128 | **4096** |
| `zincir` | 8 | 32 | **256** |
| `degerlendirme_gorevi` | 8 | 40 | **120** |

Kendi ayarınızı kurmak için:

```python
from nefs.kulli_egitim import EgitimAyari, KulliEgitim
a = EgitimAyari(ad="kendi", satir_kubiti=8, bag=128, cevrim=100,
                ornek=1024, bit=12, yaricap=4.0)
print(KulliEgitim(a).kos())
```

---

## 5. Ne ölçüldü, ne ölçülmedi

**Ölçüldü (bu makinede, CPU'da, torch olmadan):**

* `hesap/donanim.py` numpy yoluna düşüyor ve her şey koşuyor.
* Kısa CPU eğitimi baştan sona bitiyor; sayılar `nefs/kulli_egitim.py`
  raporundadır.
* `kuantum/stabilizer.py`, `kuantum/ptr.py`, `kuantum/dalga.py`
  ölçümleri kendi `_gosterim()`lerindedir.

**ÖLÇÜLMEDİ ve koştuğu İDDİA EDİLMİYOR:**

* GPU yolu (`NQS._ileri_torch`). Burada torch yoktur. O yol numpy
  yoluyla **aynı formüldür**, fakat aynı sayıyı verdiği ancak Kaggle'da
  ölçülebilir. İlk koşuda `rapor()` çıktısındaki "yol" satırına bakın.
* `AZAMI_KAGGLE` ayarının süresi ve bellek tüketimi. Burada
  koşturulamaz (satır kübiti 12, χ=256).

---

## 6. Kaggle'a mahsus tuzaklar

* **Süre haddi.** Kaggle GPU oturumu ~9 saat/hafta 30 saattir.
  `AZAMI_KAGGLE`de `cevrim=400`; süre yetmezse `cevrim`i düşürün,
  `ornek`i düşürmeyin — istatistikî sağlamlık ondadır.
* **`/kaggle/working` kalıcıdır, `/tmp` değildir.** Çıktıyı `cikti=`
  ile working altına yazın.
* **`multiprocessing` başlatma usulü.** `fork` kullanılıyor; Kaggle
  Linux'ta çalışır. Windows'ta çalışmaz ve orada `paralel=False`
  verilmelidir.
* **Torch sürümü.** Hiçbir sürüm şart koşulmuyor; torch yoksa da koşar.
