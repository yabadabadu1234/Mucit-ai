# MİKRO MÜKELLEFİYET MALİ ETKİ MODELİ (güncel: F 3-I 299, 304, 310, 313)

**Tasarım (padişah kararları):** düz tevkifat gayrisafi hasılatın %13,5'i (kanunda üst sınır %27, Cumhurbaşkanı kararıyla); halen 4/b sigortalı olanlar primini sürdürür (F 3-I 310); yeni girenlerde gelirden bağımsız sabit prim yok, yerine **gelire bağlı prim**: aylık net mikro gelir geçim haddini (brüt asgari/3 = 11.010 TL) aşmazsa prim yok, aşarsa gelirle doğrusal artar, brüt asgari ücretin altı katında tam prim (11.808,25 TL/ay); maaşlı çalışan isterse mikro mükellef olabilir (payı u). Vadeli ödemede ceza süreli imtiyaz çıkarmadır (F 3-I 312, 313); faiz yoktur, mali modelde senet kalemi yoktur. Eski sürümlerin sayıları (götürü gider, kademeli oran, çare paketi, 24 aylık giriş kapısı, sabit prim yutulması) **geçersizdir**; git geçmişindedir.

Dosyalar: `model.py` (hesap, `python3 model.py` ile yeniden üretilir), `analiz.py` (varyant, tornado, Monte Carlo), `duyarlilik_tablolari.py` (tek tek parametre tabloları), `DUYARLILIK_TABLOLARI.md` (çıktı), `genc3.py` (genç seyri), `prim_esigi.py` (tam prim eşiği taraması), `MIKRO_MUKELLEF_MALI_MODEL.xlsx` (Excel).

## 1. Yapı

1. **Nüfus.** Katılımcı sayısı N = açık mikro mükellef namzeti stoku × katılım (`aday_n.json`): açık gerçek kişi girişimi 2024 = 1.683.000; ciroya göre aday payı 0,706 (ciro ≤ 24 asgari ücret, σ 1,75) → aday 1.188.000; katılım Kötümser %10 (119.000), Orta %20 (238.000), İyimser %40 (475.000). Yıllık hasılat H log-normal, ortalama 43 asgari ücret (`veri_kalibrasyon.json`), σ 1,25–2,0 (Kötümser 2,0; İyimser 1,5), 0,1 ile 24 asgari ücret arasına kırpılmış.
2. **Katılımcı türleri.** (a) yeni (daha önce vergi ve prim ödemeyen), (b) halen kayıtlı (s): eski rejimde vergi ve sabit 4/b primi öderdi; yeni rejimde vergi tevkifatla, sabit 4/b primi **sürer** (F 3-I 310), (c) maaşlı mikro mükellef (u): ayrı ve nihaî %13,5 öder.
3. **Gelir.** T(H) = 0,135 × H (düz oran, gider tenzili yok). Yeni girenlerde gelire bağlı prim: yıl boyunca eşit aylık hasılat varsayımıyla 12 × 11.808,25 × min(1, max(0, (y − 11.010)/(198.180 − 11.010))), y = (H − T)/12; tahsil oranı 1 (tevkifatla birlikte kaynakta kesilir; ölçülmemiş).
4. **Giderler.** BES (tevkifatın %3'ü) ve Devlet katkısı (%20); 90 gün prim hibesi (model değerinde 0); donanım KDV mahsubu; KGF; PTT; BT; itiraz; denetim.
5. **Sahte fatura.** Kayıp = hacim × (kurumlar vergisi %25 − etkin tevkifat) × φ × (1 − önlem) × kurumsal pay. Bu bir eşitlik-benzeri varsayımdır; kv=%25'te kayıp sıfıra iner, kv=%35'te küçük kalan kayıp oluşur (`careler_testi.py`).
6. **Zaman.** Beş yıl; rampa %25, %55, %80, %100, %100; reel iskonto %5; sabit 2026 TL.

## 2. Sonuçlar (4. yıl, milyar TL)

Kaynak: `model.py` (`python3 model.py`).

| Kalem (4. yıl, milyar TL) | Kötümser | Orta | İyimser |
| :-- | --: | --: | --: |
| Katılımcı (kişi) | 119.000 | 238.000 | 475.000 |
| Brüt tevkifat (%13,5) | 3,03 | 7,38 | 18,11 |
| Yeni girenlerde gelire bağlı prim geliri | 3,56 | 6,64 | 11,34 |
| BES ve Devlet katkısı | −0,07 | −0,22 | −0,62 |
| Donanım KDV mahsubu | −0,23 | −0,62 | −1,57 |
| MYO (bireysel emeklilik) tarafı | −0,10 | −0,34 | −0,83 |
| Yutulma: halen kayıtlı ve maaşlı vergi kaybı | −0,70 | −1,72 | −3,60 |
| Yutulma: eski sabit 4/b primi kaybı | 0,00 | 0,00 | 0,00 |
| Sahte fatura kaybı (kv ve φ varsayımına bağlı) | −0,02 | −0,03 | −0,03 |
| KGF | −0,07 | −0,12 | −0,16 |
| PTT, BT (4. yıl) | 0,00 | 0,00 | 0,00 |
| İtiraz | −0,01 | −0,03 | −0,09 |
| Denetim | −0,02 | −0,09 | −0,35 |
| **Net (genel devlet: Hazine + SGK)** | **+2,36** | **+3,78** | **+11,04** |
| 5 yıllık bugünkü değer (NPV, reel %5) | **+6,87** | **+11,16** | **+33,18** |

*Not: Tabloda yer almayan kalemler ve yuvarlama farkları nedeniyle satırların toplamı net sonucu birebir vermeyebilir; net değer `model.py` çıktısıdır. Eski sürümde yer alan "−2,05 Kötümser açık" yalnızca kayıtlı primin düşmesinden doğuyordu; kayıtlı prim sürdüğü için bu kalem artık sıfırdır.*

## 3. Duyarlılık

Bu bölüm bu turda yeniden hesaplanmadı. Eski varyant tabloları (çare paketi döneminden) geçersizdir ve kaldırıldı. Yeniden üretmek için `duyarlilik_tablolari.py` ve `analiz.py` çalıştırılmalıdır. Kötümser senaryoda marj incedir: net etkinin pozitif kalması, sahte fatura sızıntısının küçük kaldığı ve kayıtlı sigortalının prim sürdürme oranının beklenen düzeyde olduğu varsayımına bağlıdır.

## 4. Ne anlama geliyor

1. **Bütün senaryolarda net bakiye pozitiftir** (model varsayımları altında): Kötümser +2,36 milyar TL, Orta +3,78 milyar TL, İyimser +11,04 milyar TL.
2. **Kayıtlı primin sürmesi** kayıtlı sigortalılar için yutulmayı kapatır; bedeli, yeni girenle kayıtlı arasındaki prim asimetrisidir (F 3-I 310'un eşitlik istisnası).
3. **Sahte fatura kaybı sıfır değildir:** kv ve φ varsayımına bağlı olarak 0,02–0,03 milyar TL. "Sıfır" ifadesi bu modelde kullanılmaz.
4. **Tavan üstü bölme** ve **gelire bağlı primin** etkisi bu turda yeniden ölçülmedi; eski `bolme_kazanci_yeni.py` çıktısı eski modele dayanır ve güncellenmelidir.

## 5. Varsayım girdileri (yeni kategori için ölçülmüş veri yoktur)

Mikro mükellefiyet yeni bir kategoridir; bu kategoriye özgü ölçülmüş veri yoktur ve bu model bunu beklemez. Aşağıdaki girdiler varsayımdır; her biri için duyarlılık aralığı `tornado_senaryo.py` ve `mc_uc.py` içinde tanımlıdır. Sonuçlar bu varsayımlar koşulunda geçerlidir.

| Girdi | Durum | Duyarlılık nerede |
| :-- | :-- | :-- |
| N (katılımcı sayısı) | Aday stok (1,19 milyon) × katılım %10/%20/%40 (119 bin / 238 bin / 475 bin); katılım oranı veriye bağlı değil, varsayımdır | tornado, MC, kırılma ızgarası |
| s (kayıtlı geçiş payı) | Senaryo varsayımı | tornado, MC, kırılma ızgarası |
| π (4/b prim tahsil oranı) | Varsayım 0,8 | tornado (prim_odeme) |
| sahte fatura φ, sızıntı, kiralama | Varsayım; sızıntı ve kiralama modelde açık | `sizinti_analiz.py` |
| KGF, BES vazgeçme, MYÖ, donanım, PTT, BT | Varsayım | tornado |
