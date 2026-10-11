# MODEL G — GELİRE BAĞLI, SABİT YÜKSÜZ MODEL (F 3-I 257)

> **GÜNCELLEME (11/10/2026, nakz F 3-I 179):** Güncel N ile sonuçlar GUNCEL_MODEL.md §2'dedir (S Orta +6,17; G Orta +2,69; Kötümser −1,88). Aşağıdaki eski sayılar tarihî kayıttır.

Kod: `model_m.py`, `g_final.py`; sonuç: `sonuc_g.json`, `sonuc_g_tarama.json`. Hepsi modeldir; esneklik ve sahtekârlık parametreleri benim varsayımımdır, ölçülmemiştir.

## 1. Padişahın ölçütü ve teklif metninin denetimi
Ölçüt (3-I 257): **yük kazanılan paraya bağlıdır; geliri yoksa yükü yoktur.** Teklifin 5 Eylül'den beri okunan metni (`DEVLETE_SUNULACAK_METIN.md` satır 1–150 okundu) üç yerde bu ölçütü sağlıyor, iki yerde sağlamıyor:
| Hüküm | Durum |
| :-- | :-- |
| Madde 1 (a)–(e): tevkifat tahsilat anında, kümülatif tarife, tahsil edilmemiş faturada vergi doğmaz | Sağlıyor |
| Madde 2: defter, beyanname, muhasebeci, iş yeri, ruhsat yükü yok | Sağlıyor (ofis ve muhasebeci yükü kalkıyor) |
| I.A: "mükelleften hasılat doğmadan hiçbir bedel talep etmez" | Sağlıyor |
| **Madde 1 (p) + Madde 5 (o) son cümle: halen 4/b'li olanın sabit asgari primi sürer** | **Sağlamıyor** (gelirden bağımsız sabit yük) |
| **Madde 5 (o): hak sahipliği olmayan, genel sağlık sigortası primini ödeyerek güvenceye girer (5510 m.60/1-(g))** | **Sağlamıyor, kısmen:** sabit tutarlı prim; tutar metinde ve bu oturumda yoklanmadı. Gelire bağlı yapılabilir (tevkifatla kesilen pay) |
| Madde 5 (o): öğrenci/hak sahibi GSS'si kesilmez | Sağlıyor |

## 2. Model G
Eski ve yeni mükellef **aynı** gelir primini öder (sabit tutar yok); prim = net gelirin %10'u (net gelir 10 asgari ücret çarpanı üstünde %20), alt eşik net gelir 2 W (W=33.030 TL) altında sıfır; alıcı katkısı %2; vergi dilimleri: ilk %15, ikinci %24, üst dilimler aynı (G); G2'de 400 bin TL üstü dilimler ×1,3. Prim gelir sıfırken sıfırdır.

Yıl-4 net etki (mlr TL):
| Tasarım | Kötümser | Orta | İyimser |
| :-- | :-- | :-- | :-- |
| S (mevcut teklif: eski sabit prim sürer) | +1,08 | +4,86 | +14,19 |
| G | **−2,79** | +2,12 | +17,28 |
| G2 | −2,79 | +2,14 | +17,36 |

Rastgele çekiliş (1500; sahtekârlık ve esneklik dâhil; G'de vergi artışının kaçakçılık esnekliği U(0,25–1,5)):
| Tasarım | Senaryo | P(net<0) | %5 | medyan | %95 |
| :-- | :-- | :-- | :-- | :-- | :-- |
| S | Kötümser | %21,1 | −3,43 | +0,57 | +0,86 |
| S | Orta | %8,6 | −1,09 | +3,56 | +4,30 |
| G, önlemsiz | Kötümser | %100 | −3,58 | −2,96 | −2,42 |
| G, önlemsiz | Orta | %50,1 | −1,20 | 0,00 | +1,20 |
| G + önlemler | Kötümser | %100 | −3,35 | −2,76 | −2,22 |
| G + önlemler | Orta | %28,2 | −0,71 | +0,51 | +1,67 |
(önlemler: tek müşteri testi, hibenin 12 ay sonra ve 2 ödeyiciyle verilmesi, kapatıp açmaya karşı 60 ay bakış, e-fatura ve bankadan tahsilat; G2 sonuçları G ile aynı.)

## 3. Okunuşu (tenkitli)
1. **Maksada sadık tasarım Kötümser'de zarardır ve Orta'da kâr belirsizdir.** Sebep: halen kayıtlı mükelleflerin sabit primi (Kötümser'de 150 bin kişinin %30'u) bugün Hazine/SGK'nın en büyük geliridir; maksada uygun olarak kaldırılınca bu gelir gider. Kötümser'in pozitif kalması için eski mükellefin gelirin yaklaşık **%100**'ünü prim ödemesi gerekir (tarama: r_e=1,0 → +0,27); bu hem maksada hem akla aykırıdır.
2. **Vergi oranını artırmak kâr getirmedi.** Düz artışta (×1,1…×1,5) net, esneklik 1'de azalır, 0,5'te ancak sınırda artar; esneklik ölçülmediği için artış bir kumardır. Üst dilimleri artırmak (G2) neredeyse etkisiz, çünkü tavanın (24 brüt asgari ücret) altında üst dilimde az kişi vardır.
3. **Yeni katılımcıdan gelen kâr ayakta kalıyor** (İyimser +17,3), fakat Orta'da sahtekârlıkla sıfıra iner. Sahtekârlık önlemleri değer katıyor (Orta medyan 0,00 → +0,51; zarar olasılığı %50 → %28).
4. **Teklif metni** genç için maksada büyük ölçüde uyuyor; çatışan yer yalnız eski mükellefin sabit primi (Madde 1 (p)) ve (belki) sabit GSS primi.

## 4. Şıklar (karar padişahındır; 3-I 257 (4))
- **A. Mevcut S:** eski sabit prim sürer. Net pozitif (Kötümser +1,08), ama 3-I 257'nin maksadına aykırı (eski mükellef gelirsizken de öder).
- **B. G:** eski de gelire bağlı. Maksada uygun, Orta +2,12 (şartlı), Kötümser −2,79; 3-I 253/255'teki "net pozitif" şartıyla çelişir.
- **C. Karma (öneri, simüle edildi 'cap' ve 'kısmî süreklilik' olarak):** eski mükellef sabit primi **gelirin %50'sinden fazla olmamak üzere** öder (hiç gelirsizken sıfır değildir ama gelirini aşamaz); bu kısmen maksada uyar. Kötümser −1,04, Orta +4,14 (M-A cap 0,5 sonuçları).
