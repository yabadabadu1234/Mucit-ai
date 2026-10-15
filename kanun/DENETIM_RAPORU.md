# DENETİM RAPORU (Ekim 2026, Nihai Bertaraf ve İntibak Güncellemesi)

Kaynaklar: `MALI_MODEL/careler_testi.py`, `bolme_kazanci_yeni.py`, `notr_kural_sim.py`, `suistimal_sim.py`, `genc3.py`, `prim_asgari_esigi.py`. Tasarım: B2B Nötr Kural (%25 / %13,5), B Tasarımı Prim Eşiği (asgari ücret altı sıfır prim, üstü min(tam prim, aşan kısım)), Geçici Madde 2 intibak freni, 6 aylık tavan köprüsü desteği.

## 1. Gencin kazandığı kadar mesul olmasına mani kaldı mı?
* Gün-0 yük sıfırdır (tescil, hesap, adres, UETS ücretsiz; sabit prim ve zorunlu muhasebeci yok).
* **Tavan aşımı şoku çözüldü:** 792.720 TL tavan aşıldığında üreticinin aniden duvara çarpmasını önlemek için Madde 1 (h) uyarınca izleyen ilk 6 ay boyunca %50 prim indirimi ve defter-beyan köprüsü sağlanmıştır.
* **Genç modeli göstergeleri (72. ay):** Firmanın açık ve nakitte kalması **0,881** (mevcut kayıtlıda 0,626); geçim eşiğini sürdürme **0,800** (mevcut kayıtlıda 0,594); kalıcı üst segment **0,277**; yıkım/batış **0,498** (mevcut kayıtlıda 0,906). Teklif mevcut düzene göre gençleri her boyutta korumaktadır.

## 2. Devletin zaafiyette olduğu saha
* Tek kapı entegrasyonu (GİB, bankalar, UETS) için Geçici Madde 1 ve 3 ile 6 aylık geçiş güvencesi tanınmış, sistemsel aksaklıklarda vatandaşa sıfır kusur ilkesi getirilmiştir.
* Bildirim süresi 48 saatten 7 güne çıkarılmış, teyit alınmadan re'sen tevkifat kesilmesi yasaklanmıştır.
* Dijital Hakem Heyetine Barolar Birliği, TOBB, TÜRMOB ve YÖK temsilcileri dahil edilerek bağımsızlık teminat altına alınmıştır.

## 3. Sahtekârın engellenemediği / devletin malen zararda olduğu saha
* **Naylon fatura:** Doğrulanmamış B2B'de Nötr Kural uygulanarak azami kazanç **0,000 TL**'ye indirilmiştir (`notr_kural_sim.py`).
* **Tavan üstü bölme:** Eski raporda kimliklerin prim ödemeyeceği varsayımıyla 189 bin TL kâr çıktığı sanılmıştı. B Tasarımı prim kuralı (asgari ücret üstü kazanca prim) devreye girdiğinde, her bölünmüş kimlik prim ödediği için 1,5 mn TL'lik hasılatı bölmek sahtekâra **−289.949 TL net kayıp (%−19,3 zarar)** yaşatmaktadır (`bolme_kazanci_yeni.py`). Bölme teşviki matematiksel olarak imkânsız kılınmıştır!
* **Devletin malen zararda olduğu hâl bertaraf edildi:** 
  * Eski Kötümser senaryo: **−2,05 milyar TL** (Devlet zarardaydı).
  * Yeni Kötümser senaryo: **+0,70 milyar TL** (5 yıllık NPV: **+1,83 milyar TL** ile net fazlaya kavuştu).
  * Yeni Orta senaryo: **+9,50 milyar TL** (5 yıllık NPV: **+28,53 milyar TL**).
  * Yeni İyimser senaryo: **+50,96 milyar TL** (5 yıllık NPV: **+154,31 milyar TL**).

## 4. Mevcut kanuna göre kazanımlar
* Kayıt dışılık asgariye indirilmiş, 100 bin ila 1,1 milyon genç yasal çalışma ve sosyal güvence zeminine kavuşturulmuştur.
* Gençlerin anne-baba üzerinden GSS, burs ve sosyal destekleri kanun kalkanıyla korunmuştur.
* Bireysel Emeklilik katkısı ve 90 günlük kısmî prim günüyle gelecekteki emeklilik hakkı aktüeryal temele oturtulmuştur.

## 5. Eşitlik ve intibak
* Eski ve yeni mükellef eşit şartlarda sisteme kabul edilir. Geçici Madde 2 ile mevcut kayıtlıların geçişi 12 aylık kademeli intibak kurallarına bağlanmış, ani prim erimesi önlenmiş, kayıtlıların geçiş toleransı eşiği $s^*$ Orta senaryoda %18,8'den **%49'a** çıkarılmıştır.

## 6. Madde AG ve meslek mensuplarının rolü
* 3568 sayılı Kanun sınırları içinde kalarak SMMM/YMM'lere fiilî hizmet teftişi gibi hafiye rolleri yüklenmemiştir.
* Fiilî teslim doğrulaması nesnel platform kayıtları (git commit, platform teslimi, e-Teslim tutanağı, banka transferi) ile yapılır. Meslek mensubu yalnızca mali tutarlılık ve banka dekont uygunluğunu teyit eder.
* Muhasebecilere yapay iş uydurulmamış; tavanı aşarak gerçek usule geçen mikro mükelleflerin (yılda ~%20'si) meslek mensuplarına doğal ve daimi müşteri havuzu oluşturacağı ortaya konmuştur.
