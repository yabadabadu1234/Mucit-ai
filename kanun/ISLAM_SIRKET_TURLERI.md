# ŞİRKET TÜRLERİ: TAM KÜME, İHTİLAF TERCİHLERİ, KANUNA ESLEME (F 3-I 281) -- İÇERİDE, DEVLETE GİTMEZ

Kaynak durumu: Kur'ân Ansiklopedisi "şirket" maddesi ve Diyanet'in Müşâreke maddesi (ikincil, okundu), Mecelle şirket kitabı metni **bulunamadı**, madde numarası yazılmaz. Mezhep ayrıntısı bir kısım hafızadandır ve yoklanmamıştır ("[H]"). İhtilaf tercihi: F 3-I 252 (4) sırası (delil sağlamlığı > taraf güvenilirliği > maslahat), padişaha sorulmadan.

## 1. Tam küme (hasır: kaynağı sermaye · emek · itibar × eşitlik şartı, artı ayrı iki ortaklık)
| Tür | Esas | Hanefî | Mâlikî | Şâfiî | Hanbelî | Tercih |
|---|---|---|---|---|---|---|
| Şirket-i mülk (ortak mülk) | iki kişinin bir şeye birlikte malik olması | caiz | caiz | caiz | caiz | Zaten var; ek hüküm gerekmez |
| İnân (sermaye, eşitlik şartsız) | oran serbest | caiz | caiz | caiz | caiz | **Esas tür**; ihtilafsız |
| Mufâvaza (tam eşitlik) | sermaye, kâr, yetki, kefalet eşit | caiz | caiz (şartları gevşek) | caiz değil | [H] ihtilaflı | **Kanuna yazılmaz** (eşitlik şartı gerçekçi değil, ihtilaflı, gereksiz); yerine kollektif şirket zaten var |
| Ebdân/sanâyi' (emek) | emekleri birleştirmek | caiz | caiz (aynı iş kolu serbest, farklıysa şartlı) | caiz değil | caiz | **Kabul**: üç mezhep caiz, maslahat çok büyük (sermayesiz genç) |
| Vücûh (itibar) | itibarla vadeli mal alıp satmak | caiz | caiz değil | caiz değil | caiz | **Kabul** (Hanefî+Hanbelî), şartla: alacaklıya ortaklar müteselsil sorumlu |
| Mudârebe (sermaye+emek) | sermaye bir tarafta, emek diğerinde, kâr oranlı | caiz [H] | caiz | caiz [H] | caiz | **Kabul**; dört mezhepte caiz [H, kaynak yalnız Mâlikî ve Hanbelî'yi saymış] |
| Azalan ortaklık (mütenâkısa) | ortak payı kademeli satın alır | modern | modern | modern | modern | **Kabul**, ayrı akit ve vaat yapısıyla [yoklanamadı: akademi kararı bulunamadı] |
| Müzâra'a, müsâkât, muğârese | arazi/bahçe + emek, ürün oranlı | [H] Ebû Hanîfe caiz görmez, İmâmeyn ve cumhur caiz | caiz | caiz | caiz | **Kabul** (cumhur), fetva Hanefîde İmâmeyn [H] |
| Sermaye şirketleri (LTD, AŞ) | tüzel kişilik + sınırlı sorumluluk | ihtilaflı | ihtilaflı | ihtilaflı | ihtilaflı | Mevcut hâliyle bırakılır; sermayesiz sınırlı sorumlu mikro tür ayrı (Madde H) |

## 2. İhtilaf kararları (sırayla)
- **Ebdân:** delil: emeğin sermaye gibi sermaye sayılması (kıyas, örf); Şâfiî itirazı "ortada mal yok" gerekçesine dayanır; üç mezhebin caiz görmesi ve ihtiyaç ağır basar. **Kabul.**
- **Vücûh:** delil: ortaklar birbirine vekil olarak alım yapar; Mâlikî ve Şâfiî "ortada mal yok" der. Maslahat: ticarete sermayesiz giriş. Garar riskine karşı alacaklıya ortakların müteselsil sorumluluğu şartı. **Kabul (şartlı).**
- **Mudârebe:** ihtilafsız; sermaye sahibi kayıpta sermayesini kaybeder, emek sahibi borçlanmaz (kusuru yoksa). **Kabul.**
- **Kâr tavanı:** mudârebede bir tarafa **sabit miktar** kâr şartı akdi bozar (aralarında ihtilaf yok [H]). Simülasyonda sermayedar payına tavan koymak gençler için gerekli çıktı (bk. §3). Bunun fıkhen uygun yolu tavan koymak değil, **azalan ortaklık**: kâr oranla paylaşılır, sermayedar payı ayrı bir satış akdiyle genç ortağa kademeli devredilir. Ayrı akit kaydı "tek akitte iki akit" itirazına karşı.
- **Mufâvaza:** kanuna yazılmaz.
- **Sermaye şirketleri:** Madde H şartları (rıza, ilan, haksız fiilde şahsî sorumluluk).

## 3. Simülasyon (`MALI_MODEL/ortaklik_sim.py`, `ortaklik_sim_out.txt`)
Orta kalibrasyon, soğuk başlangıç, N=3000, Teklif S rejimi. Başlangıç sermayesi gence verilir; kâr payı sermayedara gider.
| Senaryo | 12 ayda gelir | Yıkım | Kalıcı üst | Sermayedar 72 ay net getiri |
|---|---|---|---|---|
| Hizmet, sermayesiz | 0,75 | 0,57 | 0,092 | -- |
| Stoklu ticaret, borçla stok 20 000 | 0,74 | 0,67 | 0,081 | -- |
| Ortaklık, sermaye 20 000, pay 0,3, **süresiz** | 0,81 | 0,62 | 0,046 | +9,6× |
| Aynı, pay 0,5, süresiz | 0,81 | 0,76 | 0,019 | +12,7× |
| **Azalan (tavan 1,3×sermaye), pay 0,3** | 0,81 | **0,52** | **0,102** | +0,58× |
| Azalan (tavan 1,5×), pay 0,5 | 0,81 | 0,54 | 0,101 | +0,78× |
Okuma: süresiz kâr payı sermayedara aşırı getiri verir (×9–13) ve gencin kalıcı üst segmente geçişini yarıya (0,081→0,046) ve daha aza indirir; kanunun hata ölçütüne (F 3-I 258) **takılır**. Azalan yapıda genç kalıcı üstte 0,10, yıkım 0,52, sermayedar yine pozitif getiri alır (+0,6–0,8× 72 ayda), yani yapı hem gence hem sermayedara uygun.
**Sınırlar (dürüstlük):** (1) Sermaye modelde gencin geçim ve işletme nakdiyle karışıyor; faydayı abartmış olabilir. (2) Sermayedarın bulunacağı varsayılıyor (arz ölçülmedi). (3) Ebdân, vücûh ve tarım ortaklıkları simüle **edilmedi**: model tek kişilik; iki ortaklı hâl eksen ister. Bu türler gün-0 maliyeti artırmıyor ve tavan her ortak payı üzerinden sayıldığı için devlete ek yük getirmiyor (analitik, ölçülmedi); tavan çoğaltma riski Madde 1 (o)'daki gibi saklı.
