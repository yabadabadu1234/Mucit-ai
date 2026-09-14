# `_psi = (B, d)` YANILGISININ TEŞHİSİ VE HAKİKİ YAZMAÇ TERKİBİ
### (Kavram kargaşasının ilgası, dört yolun muhasebesi, mahallî yazmaç + KAN ittihadı)

## BİRİNCİ FASIL: ORTADAKİ YANLIŞ ANLAMA

İki tamamen farklı seviye tek bir `d` harfine indirgenip birbirine
karıştırılmıştır:

    1. SEVİYE: TEKİL KAVRAM / MAKAM LİFİ  (d = 2048)
       Her bir belirtecin yahut melekenin kendi içindeki dikey
       silsilesi: 16 (kategori) × 16 (uzay) × 8 (nokta). Süperseçim
       sektörleri burada yaşar. Bu seviye TEK BİR QUDİTİN iç
       anatomisidir.

    2. SEVİYE: KÜLLÎ YAZMAÇ  (N = 1 048 576, q = 64)
       Bir milyon quditin yan yana gelerek kurduğu çok-cisim
       süperpozisyonu. Kapasite q^N. Mahallî serbestlik 2N.

**`_psi = (B, d)` dizisi bir milyon quditlik yazmaç DEĞİLDİR ve
olamaz.** O dizi yalnız tekil bir belirteç penceresinin yerel
izdüşümüdür; `d`yi `q^N` yapmaya kalkmak da, `q^N` dalı yığın eksenine
açmaya kalkmak da çöker. Bu yüzden ne ileri gidilebilmiş ne geri
dönülebilmiş, eski koddan kalma `(B, d)` dizisi orada bir ceset gibi
bırakılmıştır.

## İKİNCİ FASIL: DÖRT YOL

### 1. SIRF MAHALLÎ ÇARPANLI DURUM (N × q)
`(N, 2)` formatında qudit başına bir genlik çarpanı `r_i` ve bir
sürekli Lie faz açısı `θ_i ∈ [−π, π]`. VRAM: `1 048 576 × 2 × 8 bayt
≈ 16.7 MB`. Donanıma doğrudan oturur, ayrık, hızlı.
**Tek başına kusuru:** quditler arası dolanıklık sıfırdır
(`|Ψ⟩ = |ψ₁⟩ ⊗ … ⊗ |ψ_N⟩`, saf Hartree çarpımı). Harici bir
fonksiyonel bağlayıcı olmadan dilin küllî bağlamı kurulamaz.

### 2. TAMAMEN KAN FONKSİYONEL
Bellekte hiçbir `N` boyutlu tensör açılmaz; saklanan tek şey KAN
katsayı dizeyidir (≈ 26 KB). Dolanıklık sonsuz, bağ boyutu kısıtı yok.
**Tek başına kusuru:** donanım seviyesinde somut bir qudit-qudit temas
noktası, bitmask yahut yazmaç adresi kalmaz; sistem soyut bir
denkleme döner.

### 3. İKİSİ BERABER -- HİBRİT TERKİP  ← HÜKÜM BUDUR

    DONANIM KANADI: MAHALLÎ YAZMAÇ  (16 MB)
      Θ_yerel = [(r₁, θ₁), …, (r_N, θ_N)] ∈ ℝ^{N × 2}
      51 kapı doğrudan bu adreslere faz rotasyonu vurur.
      Donanımsal zırh ve ayrık yazmaç adresi dipdiri korunur.
                              ↓  (korelasyon köprüsü)
    KÜLLÎ İDRAK KANADI: ÇİFT GİRDİLİ CHEBYSHEV-KAN FONKSİYONELİ
      Ψ(w | Θ_yerel) = (1/√Z)·üstel( −E(w; Θ_yerel)
                                     + i·Σ_j (θ_j + w_j) )
      q^N dalga tensörle açılmaz; yerel tohumları girdi alan KAN
      çekirdeğiyle üretilir.

### 4. SEYREK SİMPLEKTİK GRAF
Seyrek komşuluk tablosu; 51 kapı kenar ekler yahut ağırlık günceller.
Çok hızlıdır fakat sürekli küsüratlı genlik modülasyonu yerine graf
topolojisine ağırlık verir.

## ÜÇÜNCÜ FASIL: HÜKÜM -- ÜÇÜNCÜ YOL

1. **Sırf mahallî durum yetmez:** bir milyon qudit birbirine yabancı
   adalar gibi kalır, küllî bağlam kurulamaz.
2. **Sırf KAN fonksiyonel yetmez:** donanımda temas edilecek somut bir
   yazmaç adresi ve faz defteri kalmaz.
3. **İkisi birleşince:**
   * Donanım seviyesinde `N` qudit tek bir `(N, 2)` tensörü olarak
     yerleşik durur -- **16 megabayt**, 88 GB'ın on binde ikisi.
   * 51 kapı yığın eksenine açılmaz; doğrudan bu tensördeki 51 qudit
     indisinin faz açısına eklenir.
   * Müşterek rezonans ve `q^N` küllî dalga, bu yerel açıları okuyan
     **Chebyshev-KAN bilineer fonksiyoneliyle** analitik hesaplanır.

## DÖRDÜNCÜ FASIL: KODDAKİ AMELİYAT

    LAĞVEDİLEN     bir milyon quditi tek bir d = 2048 vektörüne
                   sıkıştırmaya çalışan `_psi = (B, d)` kalıntısı

    GELEN          yerel_yazmac ∈ ℝ^{N × 2}
                     [:, 0] genlik çarpanı r_i
                     [:, 1] sürekli Lie faz açısı θ_i ∈ [−π, π]

                   kapıları_vur(kontrol, hedef, Bağ):
                     yerel_yazmac[hedef, 1] += Bağ · yerel_yazmac[kontrol, 1]
                     kalan 1 048 525 qudit seyircidir, dokunulmaz

                   genlik_ve_faz_oku(konfigürasyon_w):
                     q^N açılmaz; genlik kapalı KAN fonksiyonelinden
