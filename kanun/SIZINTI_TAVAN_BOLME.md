# TAVAN ÜSTÜ BÖLME SIZINTISI: MATEMATİKSEL ÇÖZÜM VE ARBİTRAJIN BERTARAFI (Ekim 2026)

Kaynak: `MALI_MODEL/bolme_kazanci_yeni.py`, `bolme_b2c_test.py` (B Tasarımı Asgari Ücret Eşikli Prim + B2B Nötr Kural).

## 1. Eski Hata ve Yanılgı Neredeydi?

Eski hesaplamada (`SIZINTI_TAVAN_BOLME.md` ilk sürüm), geliri tavan altına bölünen kimliklerin yalnızca %13,5 vergi ödeyeceği ve **sıfır prim** ödeyeceği varsayılmış; bu eksik varsayım sebebiyle 189 bin ila 684 bin TL'lik hayali bir "fail kazancı" hesaplanmıştı.

## 2. Gerçek Kanun Hükmü Devreye Girince Ne Olur? (Matematiksel Çözüm)

Kanun teklifinin Madde 5 (o) bendinde yer alan **B Tasarımı Prim Eşiği** uyarınca:
* Bir kimliğin aylık net geliri brüt asgari ücreti aşıyorsa, aşan kısım üzerinden veya tam tavan primi (yıllık 141.699 TL) tahakkuk ettirilir.
* 1,5 milyon TL'yi 2 kimliğe bölen biri, her kimlikte 750.000 TL hasılat gösterir. 
* 750.000 TL hasılatta aylık net gelir ~54.000 TL olup brüt asgari ücretin (33.030 TL) çok üzerindedir.
* Dolayısıyla **her iki kimlik de tam 4/b primi ödemek zorundadır!**

| Gerçek hasılat | Kimlik sayısı | Normal rejimde toplam yük (Vergi + 4/b primi) | Bölünmüş rejimde toplam yük (Vergi + 4/b primleri) | Fail net kazancı (Hazine kaybı) | Sonuç |
| --: | --: | --: | --: | --: | :-- |
| **1,5 milyon TL** | 2 | 391.699 TL (%26,1) | **606.648 TL** (%40,4) [Vergi: 323.250 + 2xPrim: 283.398] | **−289.949 TL (%−19,3 ZARAR)** | **BÖLME İMKÂNSIZ / ZARARLI** |
| **3,0 milyon TL** | 4 | 759.199 TL (%25,3) | **1.213.296 TL** (%40,4) [Vergi: 646.500 + 4xPrim: 566.796] | **−604.097 TL (%−20,1 ZARAR)** | **BÖLME İMKÂNSIZ / ZARARLI** |
| **6,0 milyon TL** | 8 | 1.494.199 TL (%24,9) | **2.426.592 TL** (%40,4) [Vergi: 1.293.000 + 8xPrim: 1.133.592] | **−1.232.393 TL (%−20,5 ZARAR)** | **BÖLME İMKÂNSIZ / ZARARLI** |

*Saf B2C (%13,5 vergi) satışında dahi:*
* 1,5 mn TL bölündüğünde: Mikro vergi (202.500 TL) + 2xPrim (283.398 TL) = 485.898 TL.
* Failin kaybı: **−94.199 TL (%−6,3 zarar)**.

## 3. Netice

B Tasarımı prim kuralı sayesinde, tavanı aşan bir hasılatı birden çok kimliğe bölmek haksız kâr sağlamaz; bilakis her kimlik için fazladan tam prim ödeneceğinden sahtekâra **yaklaşık %20 net zarar** ettirir. Tavan üstü bölme arbitrajı matematiksel olarak kesin bir biçimde imkânsız kılınmış ve cezalandırıcı hale getirilmiştir.
