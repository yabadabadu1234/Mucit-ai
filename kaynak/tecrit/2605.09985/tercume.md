# İnsan Tecrit Öğrenmesinde İleriye Dönük Sıkıştırma (Prospective Compression)

Yazarlar: Hernandez Cano ve ark. (yazar sırası ve tam liste `_meta.txt`'de) — arXiv:2605.09985 — 11 Mayıs 2026 (NeurIPS 2026 şablonu)

> Tercüme notu: İngilizce LaTeX kaynağından çevrilmiştir. Formüller aynen; `[anahtar]` atıflardır. Şekil dosyaları depoda yoktur, yalnız şekil başlıkları çevrilmiştir. "helper" = yardımcı (kalıcı alt-program); "library" = kütüphane; "compression utility (CU)" = sıkıştırma faydası; "retrospective" = geriye dönük; "prospective" = ileriye dönük. LLM istemleri (Ek F) çevrilmemiş, aynen bırakılmıştır (kod ve model girdisidir); amacı kısaca Türkçe özetlenmiştir.

## Özet

Program sentezinde temel bir güçlük **çevrim-içi kütüphane öğrenmesidir**: gelecekteki görev taleplerine dair belirsizlik altında yeniden kullanılabilir tecritlerin artımlı edinilmesi. Mevcut algoritmalar kütüphane öğrenmesini, öğrenilen kütüphanenin *geçmiş* görevler külliyatıyla belirlendiği durağan bir görev dağılımı üzerinde geriye dönük sıkıştırma olarak ele alır. Oysa gerçek-dünya öğrenme alanları çoğunlukla durağan değildir; görevler zamanla evrilen bir üretken süreçten doğar. Durağan olmayan alanlarda insanın kütüphane öğrenmesinin tecritleri *ileriye dönük* seçtiği, yani *gelecekteki* görevlerin sıkıştırılmasını hedeflediği hipotezini öne sürüyor ve sınıyoruz. Bu soruyu, katılımcıların küçük bir ilkel kümesi, dönüşümler ve denemeler arasında taşınan özel *yardımcılar* (helpers) ile giderek karmaşıklaşan geometrik örüntüler kurduğu görsel bir program sentezi paradigması olan *Örüntü Kurucu Görevi* ile inceliyoruz. Bu görevle, ileriye dönük sıkıştırmayla tutarlı davranışları alternatif kütüphane öğrenme açıklamalarından ayırmak üzere tasarlanmış, tamamlayıcı örtük müfredatlı iki deney yürütüyoruz. Çevrim-içi kütüphane öğrenme stratejilerini kapsayan altı hesaplamalı modelle gösteriyoruz ki insanın tecrit davranışı görev-üreten süreçteki örtük, durağan olmayan yapıya duyarlılığı yansıtır. Bu davranış ileriye dönük sıkıştırmayla tutarlıdır ve mevcut geriye dönük sıkıştırmaya dayalı algoritmalarla veya LLM tabanlı program sentezinin modellediği tümevarımsal yanlılıklarla yakalanamaz.

## 1. Giriş

Bir katedral inşa etmekten bir enstrüman çalmayı öğrenmeye dek insanlar karmaşık problemleri yeniden kullanılabilir alt-görevlere ayrıştırarak çözer [gobet2001chunking, qin2025planning]. Kütüphane öğrenmesi bu fikri program sentezi bağlamında biçimselleştirir: bir program külliyatı verildiğinde, her biri o ana kadar görülen programları azamî sıkıştıracak biçimde seçilmiş yeniden kullanılabilir alt-programlardan oluşan bir kütüphaneyi yinelemeli keşfeder [ellis2023dreamcoder, liang2010learning]. Bu yaklaşım, liste fonksiyonları [liang2010learning, rule2024symbolic], bilişsel haritalar [sharma2022mapi, kryven2025cognitive] ve hiyerarşik planlama politikaları [correa2025exploring] dahil alanlarda insan bilişindeki tecrit öğrenmesini modellemede verimli olmuştur.

Ancak birçok doğal problem alanı dinamiktir; görevler, mevcut kütüphane öğrenme yaklaşımlarının varsaydığı durağan görev dağılımı yerine durağan olmayan bir üretken süreçten doğar [bowers2023top, ellis2023dreamcoder]. Bu koşullarda öğrenen, yalnızca şimdiye kadar görülen görevler verildiğinde hangi tecritleri oluşturup yeniden kullanacağına nasıl karar vermelidir (Şekil 1)? Geriye dönük sıkıştırmaya dayalı algoritmalar bu tür durağan olmayan ortamlara doğal biçimde genişler mi?

**Şekil 1.** Mevcut kütüphane öğrenme algoritmaları geçmiş görevleri geriye dönük sıkıştırır (sol). İnsan tecrit öğrenmesi, gelecekteki görevlere aktarılacak tecritleri seçmek için görev-üreten süreç üzerinde ileriye dönük sıkıştırma olarak daha iyi karakterize edilir (sağ).

Bu çalışmada insan davranışını, durağan olmayan koşullar dahil çevrim-içi kütüphane öğrenmesinin altındaki hesaplamalı ilkeleri belirlemek için bir teşhis kâhini olarak kullanıyoruz [lake2015human, acquaviva2022communicating, johnson2021fast]. Bunun için, öğrenenlerin küçük bir ilkel örüntü ve dönüşüm işleci kümesiyle geometrik örüntüler kurduğu görsel bir program sentezi paradigması olan **Örüntü Kurucu Görevi**'ni (Pattern Builder Task, PBT) kullanıyoruz (Şekil 2). PBT'de çözümler bu ilkel ve dönüşümlerden oluşan programlarla ifade edilir; öğrenenler herhangi bir ara kurguyu sonraki denemelerde kullanılabilen *yardımcı* olarak saklayabilir. Şekil 2 (sol), PBT'de kurulan dört örüntü örneğini gösterir.

PBT'de çevrim-içi kütüphane öğrenmesini, bir görev dizisini çözerken artımlı olarak bir yardımcı (yeniden kullanılabilir tecrit) kümesi kurma problemi olarak biçimselleştiririz. Üç hesaplamalı ilkeyi ele alırız: (1) **Sıkıştırma:** çözümler üzerinde tarif uzunluğunu asgarîleştirmek [bowers2023top, ellis2023dreamcoder]; (2) **Tümevarımsal yanlılık:** temsiller üzerinde yapısal önseller [kryven2024approximate, kumar2022using]; ve (3) **Üretken çıkarım:** gelecek görevleri öngörmek için durağan olmayan görev dağılımını modellemek [cogsci2026].

İnsan tecrit kararlarının görev dağılımının örtük üretken yapısına duyarlı olduğunu bulduk; bu, insan kütüphane öğrenmesinin ileriye dönük sıkıştırmayla güdüldüğünü ve geriye dönük sıkıştırma veya tümevarımsal yanlılıkla tek başına açıklanamayacağını düşündürür. Toparlarsak katkılarımız: 1) ileriye dönük ile geriye dönük sıkıştırma stratejilerini örtük müfredatların ayırdığı çevrim-içi kütüphane öğrenmesi için denetimli bir deneysel paradigma; 2) geriye dönük sıkıştırmayı ve tümevarımsal yanlılığı somutlaştıran, insan davranışına karşı değerlendirilen bir hesaplamalı model ailesi; ve 3) insanın çevrim-içi tecrit öğrenmesinin görev-üreten sürecin ileriye dönük sıkıştırmasıyla güdüldüğünün ve geriye dönük sıkıştırma veya tümevarımsal yanlılıkla tek başına açıklanamayacağının ilk gösterimi.

## 2. Kütüphane Öğrenmesi

Örüntü kurmayı, örnekle programlama (PBE) paradigması [gulwani2017program] içinde tümevarımsal program sentezi olarak biçimselleştiririz. Bir alana özgü dil (DSL), geometrik ilkeller $\mathcal{X}$ ve dönüşüm işleçleri $\mathcal{T}$'den oluşan $p \in \mathcal{P}$ programlar uzayını tanımlar. $c$ hedef örüntü olsun; $c$'yi kurmak $\llbracket p \rrbracket = c$ olacak bir $p$ programı bulmak demektir.

Bir **kütüphane** $\mathcal{L}$, taban DSL'yi sonraki programlarda ilkel gibi iş gören sonlu bir yardımcı program kümesi $\mathcal{H} \subset \mathcal{P}$ ile genişletir. Bir $\mathcal{L}$ kütüphanesi verildiğinde programlar soyut sözdizim ağaçları (AST) olarak gösterilir; yapraklar ilkeller $\mathcal{X}$'e veya yardımcılar $\mathcal{H}$'ye, iç düğümler dönüşüm işleçleri $\mathcal{T}$'ye karşılık gelir. $\mathcal{L}$ verildiğinde $c$ hedef örüntüsü $\llbracket p' \rrbracket_{\mathcal{L}} = c$ ile çözülebilir; $\llbracket \cdot \rrbracket_{\mathcal{L}}$ kütüphane-genişletilmiş DSL altında yürütmeyi gösterir. $\mathcal{L} = \emptyset$ iken $\mathcal{P}_{\mathcal{L}}$ taban DSL'ye indirgenir.

Her $t$ için $\llbracket p_t \rrbracket = c_t$ olan $\mathcal{P}' = \{p_t\}_{t=1}^{T} \subset \mathcal{P}$ çözümlü bir hedefler dizisi $\mathcal{C} = (c_1, \ldots, c_T)$ verildiğinde klasik **kütüphane öğrenme problemi**, sıkıştırma faydasını (CU) azamîleştiren bir yardımcı kümesi $\mathcal{H}^*$ bulmaktır:

$$\mathcal{H}^* = \arg\max_{\mathcal{H} \subset \mathcal{P}} \mathrm{CU}(\mathcal{H}, \mathcal{P}'), \qquad \mathrm{CU}(\mathcal{H}, \mathcal{P'}) = \sum_{h \in \mathcal{H}} |h| \cdot \mathrm{occ}_\mathcal{H}(h, \mathcal{P'}) \tag{1}$$

Burada $|h|$ $h$ yardımcısının boyutunu (AST'sindeki DSL ilkeli sayısı), $\mathrm{occ}(h, \mathcal{P'})$ ise $h$'nin $\mathcal{H}$'deki başka bir programın alt-programı olmaksızın bir alt-program olarak göründüğü $\mathcal{P'}$ içindeki program sayısını gösterir (bu son şart çift saymayı önler). Denklem 1 standart sıkıştırma faydası tanımını [bowers2023top, ellis2023dreamcoder] izler ve bütün programlar boyunca kazanılan toplam AST düğüm sayısını yansıtır. Ek A'da, en iyi tek yardımcıyı bulmanın kısıtlı düz-program ortamında bile NP-tam olduğunu gösteririz.

Mevcut yöntemler $\mathcal{L}$ kütüphanesini, o ana dek görülen programlar üzerinde geriye dönük CU'yu (Denk. 1) azamîleştiren yardımcıları seçerek kurar [ellis2023dreamcoder, bowers2023top]. Buna karşılık biz insan kütüphane öğrenmesinin **ileriye dönük bir kütüphane öğrenme problemini** çözüyor olabileceğini ileri sürüyoruz: bütün çözüm külliyatı $P^*$'ın sıkıştırmasını eniyileyen $\mathcal{H}$'yi bulmak, $\mathrm{CU}(\mathcal{H}, \mathcal{P^*})$ (Şekil 1). Biçimsel olarak $\mathcal{C}_{1:t} = (c_1, \ldots, c_t)$ $t$ zamanına kadar gözlenen görevler külliyatı, $\mathcal{P}'_{1:t} = \{p_s\}_{s=1}^{t}$ çözümleri olsun; ileriye dönük kütüphane öğrenme problemi şunu bulmaktır:

$$\mathcal{H}^* = \arg\max_{\mathcal{H} \subset \mathcal{P}} \mathbb{E}_{P(P^* \mid \mathcal{C}_{1:t})} \left[ \mathrm{CU}(\mathcal{H}, P^*) \right] \tag{2}$$

Burada $P( P^* \mid \mathcal{C}_{1:t})$, bütün görev külliyatı $\mathcal{C}_{1:t+k}$ için tam çözüm kümesi $P^* = \{p_1, \ldots, p_{t+k}\}$ üzerinde bir dağılımdır.

İleriye dönük kütüphane öğrenmesinin insanların yeniden kullanılabilir tecritleri nasıl oluşturduğunu daha iyi yakaladığı hipotezini, PBT'deki insan yardımcı öğrenme davranışını geriye dönük sıkıştırmayı ve tümevarımsal yanlılığı somutlaştıran bir hesaplamalı model ailesiyle karşılaştırarak ve insan tecrit seçiminin bu açıklamaların öngördüğünü aşıp aşmadığını ölçerek sınarız.

**Şekil 2.** *Örüntü Kurucu*'dan örnek görevler. **A** Öğrenenlere 5 geometrik ilkelden oluşan bir başlangıç kümesi (yeşil kutu) ve yedi sabit işlem (mavi kutu) verilir. İlkeller işlemlerle birleştirilebilir ve yeni örüntüler 'yardımcı' olarak saklanabilir (örn. yeşille vurgulanmış çapraz çizgi). Yardımcılar sonraki görevlere taşınır. **B** Modeller arasında yardımcı oluşturma stratejisi örnekleri. Yeşil vurgu, her modelce öğrenilmiş kütüphaneye terfi ettirilen tecritleri (yardımcıları) gösterir. Yardımcı oluşturmadaki tümevarımsal yanlılıklar makul düzenli geometrik örüntüleri seçer (LLM program sentezinin modellediği gibi). Olasılıksal kütüphane öğrenmesi MDL çözümlerindeki adımları rastgele terfi ettirir. Geriye dönük (DreamCoder-tarzı) sıkıştırma, geçmişte gözlenen görevlerin sıkıştırmasını azamîleştiren yardımcıları terfi ettirir. Açgözlü sıkıştırma her zaman en son çözümü terfi ettirir, mevcut denemedeki sıkıştırmayı azamîleştirir. İleriye dönük terfi ettirilen yardımcılar, gelecekteki programlar üzerindeki dağılımı öngörmekten türer.

## 3. Hesaplamalı Modeller

PBT'deki program sentezi problemini kütüphane öğrenmeyle veya onsuz çözen bir model ailesi değerlendirir ve hangisinin insan davranışını en iyi yakaladığını belirleriz.

### 3.1 Taban çizgisi: Aşağıdan-yukarı Program Sentezi (Kütüphane Yok)

Bu model, $\mathcal{L} = \emptyset$ durumuna karşılık gelen, $\mathcal{P}_{\mathcal{L}}$'nin $\mathcal{P}$'ye indirgendiği taban DSL üzerinde kapsamlı arama yapar. $k$ boyutlu programların $\mathcal{P}_k$ hipotez sınıflarını kurarak program boyutu üzerinde aşağıdan-yukarı sayım yaparız: $\mathcal{P}_{k+1} = \{ t(p_1,\ldots,p_n) \mid t \in \mathcal{T}, p_i \in \mathcal{P}_{\le k} \}$. Arama artan $k$ sırasıyla, program uzayının genişlik-öncelikli gezintisine karşılık gelecek biçimde ilerler. Fazlalığı azaltmak için programları gözlemsel denklikle [albarghouthi2013recursive, udupa2013transit] budar, her denklik sınıfından tek bir en kısa temsilci tutarız. Bu model her görevi bağımsız olarak, yalnızca Asgarî Tarif Uzunluğu (MDL) yanlılığıyla [chater1999search, chater2003simplicity, rule2024symbolic] program sayımıyla çözer.

### 3.2 Geriye Dönük Sıkıştırmayla Kütüphane Öğrenmesi

İkinci model sınıfı aşağıdan-yukarı sentezi durağan görev dağılımları üzerinde artımlı tecrit yeniden kullanımıyla genişletir. $i$ görevini çözdükten sonra program sentezi bir türetim izi $\mathcal{D}^{(i)} = \{p^{(i)}_1, \ldots, p^{(i)}_{T_i}\}$ üretir; burada $p^{(i)}_{T_i} = p^{(i)}$ son çözüm programı ve ara öğeler aramada kurulan alt-programlara karşılık gelir. İzden kütüphaneye terfi ettirilecek aday alt-programların bir alt kümesini seçen bir tecrit işleci tanımlarız: $\mathcal{L}^{(i+1)} = \mathcal{L}^{(i)} \cup \mathcal{A}(\mathcal{D}^{(i)})$.

$\mathcal{A}$'nın farklı örneklenmeleri, sıkıştırmanın türetimler üzerinde nasıl yapıldığına dair farklı varsayımlara karşılık gelir. Üç varyantı ele alırız:

**Model 2a: Geriye Dönük Sıkıştırma (RC).** Tecrit işleci DreamCoder [ellis2023dreamcoder] ile aynı artımlı kütüphane kurma ilkesini izler. $i$ görevi çözüldükten sonra türetim izi $\mathcal{D}^{(i)}$'deki her aday, mevcut çözüm külliyatı $\{p_1, \ldots, p_i\}$'ye karşı sıkıştırma faydasıyla (Denk. 1) puanlanır. İlk $k$ yardımcı, açgözlü, azalan fayda sırasıyla (her yardımcı eklendikten sonra yeniden hesaplanarak) seçilir: $\mathcal{A}_{\mathrm{RC}}(\mathcal{D}^{(i)}) = \arg\max_{\mathcal{H} \subseteq \mathcal{D}^{(i)}, |\mathcal{H}|=k} \mathrm{CU}(\mathcal{H}, \{p_1, \ldots, p_i\})$. Görev başına tek yardımcı ekleyen DreamCoder'dan farklı olarak RC problem başına $k$ yardımcı ekler. RC'nin sıkıştırma faydasını insan katılımcılarla daha iyi karşılaştırmak için $k$'yi davranışsal deneylerde görev başına yaratılan ortalama yardımcı sayısı olarak ayarlarız.

**Model 2b: Açgözlü Kütüphane Öğrenmesi (GL).** Model 2a hesaplama bakımından pahalıdır ve insan bilişi çoğunlukla hesap kaynaklarıyla sınırlıdır [lieder2020resource, zhao2024model]. Bu nedenle yalnızca son programı seçen, tamamlanmış programlar üzerinde yerel açgözlü MDL güncellemesine karşılık gelen bir tecrit işleci ele alırız: $\mathcal{A}_{\mathrm{GLL}}(\mathcal{D}^{(i)}) = \{p^{(i)}_{T_i}\}$.

**Model 2c: Olasılıksal Kütüphane Öğrenmesi (PL).** Ayrıca türetim izinden elemanları rastgele seçerek gürültülü bir sıkıştırma süreci doğuran bir tecrit işleci ele alırız: $\mathcal{A}_{\mathrm{PLL}}(\mathcal{D}^{(i)}) = \{p \in \mathcal{D}^{(i)} \mid z_p = 1, z_p \sim \mathrm{Bernoulli}(q)\}$.

Bu üç model, durağan bir görev dağılımı üzerinde farklı sıkıştırma ölçütlerine dayanan yardımcı terfi stratejileri uygular; yani bir yardımcı kümesinin görülmemiş gelecek görevler için yararlı olup olmayacağını öngörmeden.

### 3.3 Yalnız Tümevarımsal Yanlılıkla Kütüphane Öğrenmesi (LLM tabanlı)

Üçüncü model ailesi, açık bir sıkıştırma amacı olmaksızın tümevarımsal yanlılık güdümlü tecrit öğrenmesini somutlaştırır. Genel amaçlı bir dilde (Python) program sentezi için büyük dil modeli (LLM) kullanırız. Her $t$ denemesinde modele şunlar verilir: (i) PBT alanının tarifi, (ii) mevcut hedef örüntü, (iii) Python fonksiyonları olarak kodlanmış DSL ilkelleri ve (iv) önceden getirilmiş yardımcı fonksiyonlar. Hedefin doğru kurulmadığı denemelerde LLM cevabını incelemesi için yönlendirilir. Yaratılan yardımcılar sonraki inceleme yinelemelerine taşınır. İnceleme en çok 5 kez tekrarlanır. Burada bütün modeller LLM arka ucu olarak \textsc{gpt5.2, düşük muhakeme} kullanır; deneyler boyunca 5 inceleme adımı içinde hedefleri tamamlamak için yeterli program sentezi kabiliyetine sahip \textsc{gpt} ailesinin asgarî sürümü olarak seçilmiştir. Tam istemler Ek F'dedir.

**Model 3a: Belleksiz (LLM-PS).** Modelden her örüntüyü yalnızca mevcut DSL ve yardımcı kümesine erişimle kurması istenir. Bu, mevcut yardımcılar dışında görev geçmişine açık koşullanma olmaksızın, yalnızca program yapısı üzerindeki önceden eğitilmiş tümevarımsal yanlılıklarla güdülen tecriti yakalar.

**Model 3b: Geçmişli LLM-PS (LLM-PS-H).** Model istemi ek olarak önceki görevler ve çözümlerin tam dizisini içerir. Bu, yardımcı kurmanın önceki görevlere koşullanmasına izin verir ve bunun paylaşılan görev yapısını geri kazanmaya ek yarar sağlayıp sağlamadığını sınar.

### 3.4 İleriye Dönük Sıkıştırma Olarak İnsan Kütüphane Öğrenmesi

*İleriye dönük sıkıştırmayı*, tecrit terfisi için normatif bir ilke olarak tanımlarız (Şekil 1). Denk. 2'yi izleyerek ileriye dönük tecrit işleci, hem mevcut hem öngörülen gelecek çözümler üzerinde beklenen sıkıştırma faydasını azamîleştiren yardımcıları seçer: $\mathcal{A}_{\mathrm{PC}}(\mathcal{D}^{(i)}) = \arg\max_{\mathcal{H} \subseteq \mathcal{D}^{(i)}} \mathbb{E}_{P(\mathcal{P}^* \mid \mathcal{C}_{1:i})}[\mathrm{CU}(\mathcal{H}, \mathcal{P}^*)]$; burada $P(\mathcal{P}^* \mid \mathcal{C}_{1:i})$ şimdiye dek gözlenen görevlere koşullu, tam (gelecek dahil) çözüm külliyatları üzerinde bir dağılımdır. Bu tanım, insan kütüphane öğrenmesinin ileriye dönük sıkıştırmayı somutladığı hipotezimizi biçimselleştirir ve $P(\mathcal{P}^* \mid \mathcal{C}_{1:i})$'nin nasıl belirtildiğine kasten kayıtsızdır; yalnızca yardımcı seçiminin geçmişi değil gelecek görevleri de sıkıştırmasını ister.

**Şekil 3 (kaynakta `curr.png`).** Deney 1 ve 2'deki iki tamamlayıcı müfredat, her deneyin ilk 8 hedefinin türetimleriyle gösterilmiştir. Renkli vurgular her müfredatın ima ettiği yardımcıları gösterir. Deney 2'de gri arka plan panelleri ortak işleç gruplarını gösterir. Her grup sabit dört dönüşüm kümesinden (+, −, ∪, (¬, +)) bir *yardımcıya* (grup içinde paylaşılan) ve başka bir geometrik ilkele uygulanmasıyla türer.

Şekil 2, bu modellerin belirli bir denemede kütüphaneye hangi tecritlerin terfi ettirileceğine dair ayrışan öngörülerini gösterir. Paylaşılan bir kurma görevi verildiğinde GL yalnızca son çözüm programını tutar, RC şimdiye kadar görülen görevlerin sıkıştırmasını eniyilemek için tecritleri seçer, LLM tabanlı modeller geometrik tümevarımsal yanlılıklarla tutarlı yardımcıları terfi ettirir ve ileriye dönük sıkıştırma gelecek görevlerce paylaşılacağını öngördüğü yardımcıları tutar.

## 4. Deneyler

Hangi modelin insan katılımcılarda kütüphane öğrenme stratejilerini en iyi yakaladığını, iki tamamlayıcı örtük müfredatla değerlendiririz: geriye dönük sıkıştırmanın etkili bir strateji olması beklenen *ardışık müfredat* (Deney 1) ve yalnızca görev-üreten dağılımın ileriye dönük sıkıştırması altında çözülebilir olacak biçimde tasarlanmış *işleç-grubu müfredatı* (Deney 2). Her iki deneyde insan top-$k$ yardımcılarının külliyat sıkıştırma faydasını RC ve LLM tabanlı modellerin (tümevarımsal yanlılıkla güdülen tecritlerin vekili olarak) seçtikleriyle karşılaştırırız.

### 4.1 Müfredat Tasarımları

Karşılık gelen çözüm programları $(p_1, \ldots, p_T)$ olan sıralı bir hedef örüntüleri dizisi $(c_1, \ldots, c_T)$ bir *müfredat* oluşturur. Müfredatlar meta-yapıları $\mathcal{G}$ bakımından ayrışır: çözümler üzerinde ya önceki çözümler ya da paylaşılan örtük alt-programlar aracılığıyla yapılı bağımlılıklar getiren üretken süreç. Şekil 3 iki olası yapıyı gösterir.

Deney 1, her çözümün bir önceki $p_{t-n}$ çözümüne ve $x \in \mathcal{X}$ ilkeline bir $\tau \in \mathcal{T}$ dönüşümü uygulanarak elde edildiği **ardışık** müfredatı sınar: $\mathcal{G}_{\mathrm{seq}}: p_{t} = \tau(p_{t-n}, x)$, $\tau \in \mathcal{T}$, $x \in \mathcal{X}$, $0 < n < t$. Bu geriye dönük sıkıştırmayı etkili bir strateji yapar; çünkü her hedef önceki bir çözümün artımlı genişletilmesiyle türetilebilir.

Buna karşılık Deney 2, ileriye dönük sıkıştırmayı daha etkili kılmak üzere tasarlanmış bir üretken yapıyı izler. $K$ ardışık hedeften oluşan bir $\{c_t, \ldots, c_{t+K-1}\}$ grubunun, örtük bir $h \in \mathcal{P}$ alt-programına göre **paylaşılan yardımcı** müfredatını izlediğini, $h$ gruptaki her çözümün alt-programı ise söyleriz: $\mathcal{G}_{\mathrm{hlp}}: h \sqsubseteq p_{t+k}$, $k = 0, \ldots, K-1$; burada $\sqsubseteq$ alt-program bağıntısıdır. $h$'yi geri kazanan öğrenen bütün $K$ hedefi kompakt temsil edebilir; böylece gelecek çözümler $K$ deneme öncesinden öngörülebilir olur.

Özel bir durum, her gruptaki $K$ çözümün $h$ paylaşılan alt-programına ve $x \in \mathcal{X}$ ilkeline sabit bir işleç kümesinin uygulanmasıyla üretildiği **$K$-işleç-grubu** müfredatıdır. Deney 2'de $K = 4$: $\mathcal{G}_{\mathrm{grp}}: \{p_{t+k}\}_{k=0}^{3} = \{\textsc{Add}(h, x), \textsc{Subtract}(h, x), \textsc{Overlap}(h, x), \textsc{Add}(\textsc{Invert}(h), x)\}$; $h$'nin tutumlu bir paylaşılan yapı olması kısıtıyla: gruptaki hiçbir hedef, gruptaki başka bir hedeften $\mathcal{G}_{\mathrm{grp}}$'nin öngördüğünden daha kısa bir programla türetilemez. Bu kısıt, Deney 2'de ileriye dönük sıkıştırmanın geriye dönük sıkıştırmaya üstün gelmesini sağlar; bunu Bölüm 4.4'te külliyat sıkıştırma faydasıyla (Denk. 1) deneysel doğrularız.

Şekil 3 her müfredattan ilk 8 denemeyi gösterir; bu tasarımların doğurduğu ayrı yardımcı terfi stratejilerini örnekler. Her iki deney için ayrıntılı müfredat tanımları Ek G'dedir.

### 4.2 İnsan Deneyleri

Deney 1'de ardışık müfredatı, Deney 2'de işleç-grubu müfredatını, Prolific Academic'ten toplanan insan katılımcılarla (toplam $N=60$) sınadık. Katılımcılar 6 ilkel, 3 ikili ve 4 tekli dönüşümden oluşan bir DSL'yle programlar kurarak $10\times10$ ikili örüntüleri yeniden kurmak için PBT arayüzünü kullandı (Şekil A-DSL); her ara kurguyu sonraki denemelerde yeniden kullanılabilir kalıcı bir yardımcıya terfi ettirme seçeneğiyle. Deney 1'de $N{=}30$ katılımcı (14 kadın; yaş $36.2 \pm 9.8$) ardışık müfredatı (14 hedef örüntü), Deney 2'de $N{=}30$ katılımcı (13 kadın; yaş $34.0 \pm 11.0$) işleç-grubu müfredatını (16 hedef örüntü) çözdü. Davranışsal deneylerin ayrıntıları Ek C'dedir.

### 4.3 Hesaplamalı ve Davranışsal Ölçüler

İnsan ve model başarımını şu ölçülerle çözümleriz:

**Adım sayısı.** Bir örüntüyü tamamlamak için gereken dönüşüm işlemi sayısı (\textsc{Add, Subtract, Refl\_H, Refl\_V, Refl\_D, Invert, Intersect}). Katılımcılar keşif eylemleri yapabilir veya hata yapabilir ve kütüphane kalitesinden bağımsız adım sayısını şişirebilir; bu yüzden insan verisinde bunu verimlilik için bir *üst sınır* sayarız. Üstelik yüksek kaliteli bir kütüphaneye sahip olmak daha kısa programları garanti etmez; çünkü insanlar eniyi aramadan sapma eğilimindedir [kryven2024approximate]. Bu nedenle adım sayısını yalnızca kaba bir verimlilik vekili olarak kullanırız.

**Kütüphane boyutu.** PBT'de saklanan yardımcı sayısı (insanlar için) veya LLM tabanlı modeller ve RC tarafından tecrit edilen alt-program (Python fonksiyonu veya alt-AST) sayısı.

**Top-$k$ yardımcılar ($h^k$).** Belirlenimci modeller (yani RC) için, $k$ deneysel ortalama insan kütüphane boyutuna eşitlenmiş şekilde, sıkıştırma faydasına göre sıralanmış ilk $k$ AST alt-ağacını seçeriz. İnsan ve LLM tabanlı modeller için, $k$ deneysel ortalama kütüphane boyutu olmak üzere, her denemede en sık yaratılan ilk $k$ yardımcıyı alırız. Gerekçe: yardımcı yaratımı kısmen ortak bir üretken süreçle, kısmen gürültüyle (arayüz keşfi, hatalar) güdülür. Katılımcılar boyunca toplamak ve sıklığa göre ilk $k$'yı seçmek, ortak işareti bireysel değişimden ayırır.

**Külliyat sıkıştırması.** Bir $h^k \subseteq \mathcal{H}$ yardımcı alt kümesinin tam (tutulmuş) program külliyatı $\mathcal{C}^*$'e karşı değerlendirilen sıkıştırma faydası. Bu, insan kütüphane öğrenmesinde ileriye dönük tecriti saptamak için *birincil* ölçümüzdür.

**Kâhin yardımcılar.** $t$ denemesine dek gerçek alt-AST'lerden türetilen, tam külliyat üzerinde sıkıştırma faydasına göre sıralanmış yardımcılar. Bunlar RC'nin geriye dönük bilgiyle seçeceği yardımcıları temsil eder ve kütüphane kalitesi için bir üst-sınır referansıdır.

### 4.4 Sonuçlar

**PBT insan katılımcılar için izlenebilirdir.** Her iki deneyde örüntü tamamlama başarı oranı yüksekti (D1: $M = 92.4\%$, $SD = 14.3\%$, %95 GA $[87.0\%, 97.7\%]$; D2: $M = 81.9\%$, $SD = 16.5\%$, %95 GA $[75.7\%, 88.0\%]$; her biri $n = 30$). Ayrıntılı doğruluk grafikleri Ek D'dedir. Bu sonuç PBT'nin insan katılımcılar için izlenebilir olduğunu doğrular ve tam görev dizisini tamamlayamayan modelleri elemeyi güdüler. Üç model bu ölçütte başarısız olur. Kütüphanesiz taban çizgisi, Ek H'de kurulan arama uzayının süper-üstel büyümesiyle uyumlu olarak, Deney 1'de 7. denemede ve Deney 2'de 9. denemede hesaplama bütçesini tüketir. GL, Deney 1 müfredatını tamamlar fakat Deney 2'de 9. denemeden itibaren başarısız olur; çünkü işleç-grubu yapısı açgözlü yerel güncellemelerin üretmediği yardımcılar gerektirir. PL, Deney 1'in son dört denemesinde başarısız olur. Kalan üç model RC, LLM-PS ve LLM-PS-H iki görev dizisini de tamamlar ve aşağıda insan davranışıyla karşılaştırılır.

**Şekil 4.** (Sol) Denemeler boyunca, adım sayısıyla ölçülen insan çözüm verimliliği, tahmini program uzunluğuyla (AST işlem sayısı) ve modellerin çözüm verimliliğiyle karşılaştırılmıştır. Ham program uzunluğu tahmini, RC'nin bulduğu en kısa programın kurucu DSL ilkellerine açılmasıyla elde edilmiştir. (Sağ) Katılımcıların yardımcı kütüphanelerinin ortalama biriken boyutu, modellerin öğrenilmiş kütüphaneleriyle karşılaştırılmıştır. LLM tabanlı modeller, büyüme eğilimini taklit ederken insanlara göre daha küçük kütüphaneler tutar.

**İnsanlar iki deneyde de görevleri tamamlamak için yardımcı kütüphaneleri kullanır.** Şekil 4, katılımcıların deneyler boyunca deneme başına eklediği yeni yardımcı sayısını gösterir (D1: $M = 1.16$, $SD = 0.67$, %95 GA $[0.91, 1.41]$; D2: $M = 1.30$, $SD = 1.11$, %95 GA $[0.89, 1.72]$). Katılımcıların büyük çoğunluğu en az bir yardımcı yarattı (D1: $28/30$; D2: $30/30$); bu, neredeyse herkesin kütüphane öğrenmesine girdiğini doğrular. Katılımcıların yardımcı kütüphanelerinin boyutu her deney boyunca arttı (Şekil 4). Kütüphane içerikleri bireyler arasında değişse de bireysel yardımcı kütüphaneleri arasında, deney tasarımımızın ima ettiği yardımcı stratejileriyle tutarlı anlamlı bir örtüşme vardı (Şekil 5 A).

**Kütüphane öğrenmesi arama karmaşıklığını azaltır.** İnsan adım sayısını çözümlemek için hedefin yanlış kurulduğu denemeleri (toplam denemelerin %3'ü) dışlarız. Her iki deneyde insanlar görevleri, yalnızca ham ilkellerle ifade edilen çözümlerden güvenilir biçimde daha az adımda çözdü (deneme başına toplanmış iki-yönlü eşleşmiş $t$-testi; D1: $M_{\text{insan}}=3.93$ karşı $M_{\text{prog}}=8.64$, $t(13)=-3.72$, $p=2.6\times10^{-3}$, Cohen $d_z=-1.00$; D2: $M_{\text{insan}}=4.51$ karşı $M_{\text{prog}}=9.56$, $t(15)=-5.04$, $p=1.5\times10^{-4}$, $d_z=-1.26$; Şekil 4). Ayrıca insanın kurduğu programların uzunluğu denemeler boyunca kabaca düz kaldı ($\sim$3–5 adım; D1: eğim $=-0.09$ adım/deneme, $p=0.22$; D2: eğim $=+0.05$, $p=0.19$), oysa ham-ilkel program uzunluğu denemeyle anlamlı büyüdü (D1: eğim $=+0.92$ işlem/deneme, $R^2=0.72$, $p=1.4\times10^{-4}$; D2: eğim $=+0.47$, $R^2=0.31$, $p=0.025$); bu, kütüphane öğrenmesinin sınırlı çözüm derinliğini korumaya hizmet ettiğiyle tutarlıdır.

**İnsan tecrit öğrenmesi ileriye dönük sıkıştırmayı izler.** Şekil 5, Deney 1'de RC'nin kâhin sıkıştırmasına yakından yaklaştığını gösterir; bu, ardışık müfredatının geriye dönük sıkıştırmayla etkili çözülebildiğini doğrular. İnsan külliyat sıkıştırması da Deney 1'de kâhin yardımcılara benzer biçimde yaklaşır; bu müfredat altında hem geriye dönük hem ileriye dönük açıklamalarla tutarlıdır. Buna karşılık ileriye dönük sıkıştırmayı kayıran işleç-grubu müfredatlı Deney 2'de, insan yardımcıların külliyat sıkıştırması hem RC'yi hem LLM tabanlı modelleri tutarlı olarak aşar ve kâhin sıkıştırmasını yakından izler. Bu sonuç, geriye dönük sıkıştırmanın tek başına insan tecrit seçimini açıklamaya yetmediğini düşündürür.

LLM-PS ve LLM-PS-H, insan yardımcılarıyla kısmen örtüşen geometrik olarak kanonik yardımcıların bir alt kümesini geri kazanır (Şekil 5); bu, tümevarımsal yanlılığın tecrit seçimine katkıda bulunabileceğini düşündürür. Ancak insan külliyat sıkıştırması her iki deneyde iki LLM tabanlı modeli tutarlı olarak geçer; bu, LLM tabanlı sentezin yakaladığı tümevarımsal yanlılığın tek başına, müfredat yapısı ne olursa olsun, insanın tecrit davranışını açıklayamayacağını gösterir.

**Şekil 5.** İnsanlar ve modellerce yaratılan kütüphaneler. **A.** İnsan ve model top-k yardımcılarının denemeler boyunca evrimi; $k$ belirli bir denemede ortalama insan kütüphane boyutuna ayarlanmıştır. **B.** Her iki deneyde insanlar ve LLM tabanlı modeller için öğrenilmiş kütüphane boyutlarının histogramları. **C.** Üst-k insan yardımcılarının modellere karşı Külliyat Sıkıştırması. Sıkıştırma değerleri, birkaç yardımcı eşit sıradayken rastgele eşitlik bozma ile hesaplanmış ortalamalardır.

## 5. İlgili Çalışmalar

**Program sentezinde kütüphane öğrenmesi.** Program sentezinde tecrit öğrenmesine merkezî bir yaklaşım, sıkıştırma yoluyla kütüphane öğrenmesidir [liang2010learning, allamanis2018mining, shin2019program, grand2024lilo]. DreamCoder [ellis2023dreamcoder] gibi sistemler uyanıklık-uyku usulüyle çözüm programlarını yeniden kullanılabilir tecritlere yinelemeli sıkıştırır; Stitch [bowers2023top] gibi yakın tarihli çalışmalar kütüphane indüksiyonunu program külliyatları üzerinde açgözlü MDL eniyilemesi olarak formüle eder. Ren vd. [ren2026library] caz armonik örüntülerine benzer sıkıştırma tabanlı bir yaklaşım uygular; tümdengelimli ayrıştırmayı e-graf'larda kütüphane öğrenmesiyle bütünleştirerek bir külliyattan yeniden kullanılabilir armonik tecritler keşfeder. Bu yaklaşımlar sabit görev dağılımlı çevrim-dışı ortamlarda güçlü başarım gösterir ama durağan bir külliyat varsayar ve hesaplama bakımından pahalı küresel eniyilemeye dayanır. Buna karşılık biz tecritlerin gelecek görevler hakkındaki belirsizlik altında artımlı oluşturulması gereken *çevrim-içi* kütüphane öğrenmesini inceliyoruz.

**Program indüksiyonu ve tecritin davranışsal çalışmaları.** Bilişsel bilimde artan bir çalışma kümesi, bileşimsel görevlerde insan davranışını modellemek için program sentezi çerçevelerini kullanmıştır. Tian vd. [tian2020learning], DreamCoder tarzı kütüphane öğrenmesinin insan tecrit yeniden kullanımını kısmen açıklayabildiğini, davranışı eşleştirmek için ek yanlılıkların (örn. motor verimliliği) gerektiğini göstermiştir. Daha yeni çalışmalar sembolik liste işleme [rule2024symbolic, ham2025teaching], hiyerarşik planlama [qin2025planning, correa2025exploring] ve bilişsel haritalar [sharma2022mapi, kryven2025cognitive] alanlarında tecrit öğrenmesini incelemiş; insan tecritlerinin saf sıkıştırmanın ötesinde yapılı tümevarımsal yanlılıkları yansıttığını düşündürmüştür [he2025bootstrapping]. Çalışmamız, görev dağılımının kendisinin evrildiği çevrim-içi bir ortamda *görevler arası* tecrit öğrenmesini inceleyerek bu hattı genişletir.

**Tümevarımsal yanlılıklar ve sinirsel program sentezi.** Büyük kod ve doğal dil külliyatlarında eğitilen LLM'ler, görsel tümevarımsal muhakeme görevleri dahil güçlü program sentezi yetenekleri göstermiştir [chen2021evaluating, austin2021program, acquaviva2022communicating, wang2023hypothesis] ve ön-eğitimden edinilen insan tümevarımsal yanlılıklarının örtük modelleri olarak önerilmiştir [binz2025foundation, kryven2025cognitive]. Bu bakış, geçmişin yokluğunda tümevarımsal yanlılık tecritinin hesaplamalı modeli olarak LLM tabanlı sentezi (LLM-PS) kullanmayı güdüler.

## 6. Tartışma

İnsan tecrit öğrenmesinin, yalnızca geriye dönük sıkıştırma ve tümevarımsal yanlılıklarla güdülmekten ziyade, gözlenen görev külliyatının ileriye dönük sıkıştırmasıyla daha iyi karakterize edildiğine dair yakınsayan davranışsal ve hesaplamalı delil sunuyoruz. Her iki deneyde de sonuçlarımız, insan davranışının gözlenen görev dağılımının örtük üretken yapısı üzerinde çıkarımla tutarlı olduğunu, bunun insanların tecrit seçimlerini gelecek görevlere uyarlamasına izin verdiğini düşündürür.

**Program sentezi ve bilişsel modelleme için çıkarımlar.** Program sentezi için sonuçlarımız, kütüphane öğrenme algoritmalarının geriye dönük sıkıştırma amaçlarının ötesine geçmesi ve durağan olmayan görev dağılımlarını açıkça modellemesi gerektiğini düşündürür. Tecrit seçimini görevler arası bağımlılıklara duyarlı kılmanın bir yolu, görev dizileri üzerinde açık yapı izleme, örneğin üretken süreçler üzerinde program indüksiyonuyla, uygulanabilir. Bilişsel bilim için sonuçlar, tecrit öğrenmesinin öngörücü yapı modellemesiyle sıkı bağlı olduğu görüşünü destekler: öğrenenler yalnızca tecrübeyi sıkıştırmaz, görev yapısının zamanla nasıl evrildiğini de çıkarır. Bu, kütüphane öğrenmesini bilişsel bilimde daha geniş hiyerarşik öngörü ve dizi öğrenme açıklamalarına bağlar.

**Sınırlamalar ve gelecek çalışma.** Çalışmamız, deney tasarımını hassas denetlememize ve farklı modelleme varsayımları altında davranışı derinlemesine çözümlememize izin veren kısıtlı bir görsel program sentezi alanına odaklanır. Gelecek çalışma ileriye dönük tecrit öğrenmesini başka alanlarda (sayı dizileri, iletişim) modellemelidir. Ayrıca çalışmamız örtük müfredatı açıkça çıkaran tam bir üretken-süreç öğrenicisi gerçeklemeden, insanda ileriye dönük tecrit öğrenmesini deneysel göstermeye odaklanır. Doğal sonraki adım, gelecek görevlerin ve çözümlerin olasılık dağılımını biçimsel modellemek ve hem kütüphane hem örtük görev-üreten süreç üzerinde ortak çıkarım yapmaktır.

**İleriye dönük tecrit için aday ölçüt olarak PBT.** Davranışsal bir paradigma olma rolünün ötesinde PBT, tecrit öğrenme algoritmalarını değerlendirmek için potansiyel bir çerçeve önerir. Bireysel PBT görevlerini çözmek prensipte çevrim-içi kütüphane öğrenmesi gerektirmez: yeterince güçlü bir sentezleyici her denemeyi kaba-kuvvet aramasıyla veya doğrudan üretimle bağımsız çözebilir. Ancak *insan tecrit davranışını eşleştirmek*, mevcut görev için mutlaka eniyi olmayan ama gelecekte yapısal ilişkili görevler arasında verimli aktarımı destekleyen yeniden kullanılabilir yapıyı seçmeyi gerektirir. Bu ayrım, yalnızca görev düzeyi başarım yerine örtük görev-üreten yapıya duyarlılığı işlevselleştirir. ARC-AGI [chollet2019measure] ve ilgili ardışık veya uyarlanabilir değerlendirme takımları gibi mevcut ölçütler öncelikle görev-içi bileşimsel muhakemeyi veya bölümsel genellemeyi yoklarken, PBT yapının zamanla evrilen bir görev dağılımı boyunca çıkarılması ve kullanılması gereken bir ortam sunar. Bu nedenle PBT, merkezî değerlendirme hedefinin durağan olmayan alanlarda yapıyı çıkarma ve yeniden kullanma yeteneği olduğu, ileriye dönük tecrit için gelecek ölçütlerin geliştirilmesine zemin sağlar.

*Yazar katkıları ve teşekkürler bölümleri çevrilmemiştir (isim/fon bilgisidir; özgün dosyada).*

## Ek A. Kütüphane Öğrenmesinin Zorluğu

Bir program külliyatı üzerinde sıkıştırma faydasını azamîleştiren tek bir yeniden kullanılabilir tecriti (yardımcıyı) öğrenmenin karmaşıklığını inceleriz. Bu problemin son derece kısıtlı bir sürümünün bile NP-tam olduğunu gösteririz.

**Üst düzey sezgi.** Kısıtlı ortam, kütüphane öğrenmesiyle genellikle ilişkilendirilen karmaşıklık kaynaklarının hemen hepsini kaldırır. Programların iç yapısı yoktur: her program yalnızca düz bir semboller demetidir ve bir yardımcı yalnızca bazı koordinatların sabit değerler alması gerektiğini belirtebilir. Dolayısıyla bir yardımcı öğrenmek, birçok program boyunca uyuşan bir konum alt kümesini seçmeye indirgenir.

Bu aşırı basitleştirmeye rağmen problem zor kalır. Neden: öğrenenin ortaklaşa (i) hangi konumları kısıtlayacağını ve (ii) hangi programların bu kısıtları karşılayacağını seçmesi gerekir. Bu iki seçim kombinatoryal olarak etkileşir: daha çok konumu kısıtlamak eşleşmeleri nadirleştirir, kısıtları gevşetmek kapsamı artırır. Bu takas, biklik saptama gibi yoğun alt-yapı problemlerini yansıtır.

Kütüphane öğrenmesinin genel sürümü ek karmaşıklık ekler. Programlar artık düz demetler değil ağaçlardır; bir yardımcı sabit konumlar yerine yeniden kullanılabilir bir alt-ağacı belirlemelidir. Değişkenler (veya *delikler*) yardımcının parçalarının oluşumlar arasında değişmesine izin verir; böylece aynı örüntü birçok farklı somut alt-programla (örn. farklı girdilerle aynı yapı) eşleşebilir [dechter2013bootstrap, ellis2023dreamcoder, cao2023babble, bowers2023top]. Bu esnekliği artırır ama arama uzayını da büyütür. Dahası eşleşme artık tam değildir: bir yardımcı bir programın içinde birçok farklı yere uygulanabilir ve örüntünün uyduğu bütün yerleri aramak gerekir [bowers2023top]. Aşağıdaki sonuç, bu ek katmanlardan önce bile çekirdek kombinatoryal problemin NP-zor olduğunu gösterir.

**Sözdizim ve programlar.** $\Sigma$ sonlu bir semboller kümesi, $f$ sabit bir $n$-li kurucu olsun. Her program $p \equiv f(c_1, \dots, c_n)$ olarak tanımlanır; her $c_i \in \Sigma$. $n$ arite sabittir ve bütün programlar için aynıdır.

**Külliyat.** $\mathcal C \equiv \{p^{(1)}, \dots, p^{(N)}\}$ külliyatı verilir; her program $p^{(j)} \equiv f(c_1^{(j)}, \dots, c_n^{(j)})$.

**Yardımcılar (tecritler).** Bir referans demeti $(a_1, \dots, a_n) \in \Sigma^n$ girdinin parçasıdır. Bir yardımcı, bir konum alt kümesiyle tanımlanır: $S \subseteq \{1, \dots, n\}$. Bir $p^{(j)}$ programı, $\forall i \in S,\ c_i^{(j)} = a_i$ ise $S$ ile eşleşir. $\mathrm{occ}(S) = \#\{ j : p^{(j)}\ S\text{ ile eşleşir} \}$, yardımcıyla uyumlu külliyat programlarının sayısıdır. Fayda $U(S) = |S| \cdot \mathrm{occ}(S)$ olarak tanımlanır.

**Örnek.** $\Sigma = \{A, B, X, Y\}$ ve arite 3 programları: $p^{(1)} = (A, A, X)$, $p^{(2)} = (A, A, Y)$, $p^{(3)} = (A, B, X)$. Referans demeti $(A, A, X)$ olsun. $S = \{1,2\}$ ise $p^{(1)}$ ve $p^{(2)}$ eşleşir; $\mathrm{occ}=2$ ve $U=4$. $S = \{1\}$ ise bütün programlar eşleşir; $U=3$.

**Karar problemi (En-İyi-Tek-Yardımcı).** Girdi: bir külliyat $\mathcal C$, bir referans demeti $(a_1,\dots,a_n)$ ve bir tamsayı $\omega$. Soru: $U(S) \ge \omega$ olan bir $S \subseteq \{1,\dots,n\}$ var mı?

**Önerme.** En-İyi-Tek-Yardımcı NP-tamdır.

*İspat.* **NP'ye üyelik.** Bir $S$ alt kümesi verildiğinde bütün programları tarayıp her konumda kısıtı denetleyerek $\mathrm{occ}(S)$ hesaplanabilir; bu $O(Nn)$ zaman alır. Dolayısıyla $U(S)$ polinom zamanda hesaplanabilir.

**İndirgemenin üst düzey fikri.** *Maksimum-Kenar-Biklik* problemini indirgeriz: iki parçalı bir çizge verildiğinde, aralarındaki bütün kenarların bulunduğu ve $|S|\cdot |T|$'yi azamîleştiren $S \subseteq L$ ve $T \subseteq R$ alt kümelerini bul. Karar sürümü, $|S|\cdot|T| \ge k$ olan böyle bir biklik var mı diye sorar; bunun NP-tam olduğu bilinir [peeters2003maximum]. Konumlar $L$'deki köşelere, programlar $R$'deki köşelere karşılık gelecek. Konumları seçmek yalnızca bütün bu köşelere komşu programların eşleşebilmesini zorlar; bu bir biklik yapısı verir.

**İndirgeme.** $G = (L \cup R, E)$, $L = \{u_1, \dots, u_n\}$, $R = \{v_1, \dots, v_m\}$ iki parçalı bir çizge ve $k$ hedef olsun. $M \equiv n + 1$ koyalım.

**Yapı.** $mM$ boyutlu bir külliyat $\mathcal C$ kurarız. $\Sigma$, $a_1, \dots, a_n$ sembollerini ve yeni $b_{ij\ell}$ sembollerini içersin. Her $v_j \in R$ ve her $\ell \in \{1,\dots,M\}$ için $p^{(j,\ell)} \equiv f(c_1^{(j,\ell)}, \dots, c_n^{(j,\ell)})$ tanımlarız; burada $c_i^{(j,\ell)} = a_i$ eğer $(u_i, v_j) \in E$, aksi halde $b_{ij\ell}$. $\omega \equiv Mk$ alınır. Bu yapı $G$'nin boyutunda polinomdur.

**Örnek (yapının matris görünümü).** $L = \{u_1, u_2\}$, $R = \{v_1, v_2\}$, kenarlar $(u_1,v_1), (u_2,v_1), (u_1,v_2)$ olan iki parçalı bir çizge düşünelim; $(u_2, v_2) \notin E$. $M = 3$ olsun. Yapı arite 2 programlı bir külliyat kurar: $p^{(1,\ell)} = (a_1, a_2)$ ($\ell=1,2,3$); $p^{(2,\ell)} = (a_1, b_{2,2,\ell})$ ($\ell=1,2,3$).

**İleri yön (iyi biklik ⇒ iyi yardımcı).** $|S|\cdot|T| \ge k$ olan bir $S \subseteq L$, $T \subseteq R$ biklik olsun. $S$ ilgili indis kümesini de göstersin. Her $v_j \in T$ ve her $i \in S$ için $(u_i,v_j)\in E$; dolayısıyla her $\ell$ için $c_i^{(j,\ell)} = a_i$. Böylece $v_j$ ile ilişkili $M$ programın hepsi $S$ ile eşleşir. Bu yüzden $\mathrm{occ}(S) \ge M|T|$, $U(S) \ge M|S||T| \ge Mk = \omega$.

**Ters yön (iyi yardımcı ⇒ iyi biklik).** $U(S) \ge Mk$ olan bir $S \subseteq \{1,\dots,n\}$ olsun. $S' = \{u_i : i \in S\}$ tanımlayalım. Bir $p^{(j,\ell)}$ programı $S$ ile ancak ve ancak her $i \in S$ için $(u_i,v_j)\in E$ ise eşleşir. Dolayısıyla: $v_j$, $S'$'deki bütün köşelere komşuysa $M$ programın $p^{(j,\ell)}$ hepsi $S$ ile eşleşir; aksi halde $v_j$'nin bir $u_i \in S'$'ye kenarı eksikse o $i$ için $c_i^{(j,\ell)} \neq a_i$ olup $p^{(j,\ell)}$ programlarından hiçbiri eşleşmez. $T = \{v_j \in R : (u_i,v_j)\in E\ \forall u_i \in S'\}$ olsun. O zaman $\mathrm{occ}(S) = M|T|$ ve $U(S) = |S|\cdot \mathrm{occ}(S) = M|S||T| \ge Mk$; bu da $|S||T| \ge k$ demektir. Böylece $(S',T)$ en az $k$ büyüklüğünde bir biklik oluşturur.

**Sonuç.** *Maksimum-Kenar-Biklik*'ten polinom-zamanlı bir indirgeme gösterdik ve problem NP'dedir; dolayısıyla En-İyi-Tek-Yardımcı NP-tamdır. ∎

## Ek B. Örüntü Kurucu Görevi

**Alan.** Hedefler $10\times10$ ızgarada tanımlı ikili örüntülerdir; her hücre dolu veya boştur. Her denemede denekler ve modeller hedefi sabit bir alana özgü dilde program kurarak yeniden üretmelidir.

**Alana Özgü Dil.** DSL (Şekil A-DSL) altı geometrik ilkelden ($\mathcal{X}$): `blank`, `line_horizontal`, `line_vertical`, `diagonal`, `square` (yalnız kenar) ve `triangle`; üç ikili işleçten ($\mathcal{T}_{\mathrm{bin}}$): `add`, `subtract` ve `overlap`; ve dört tekli işleçten ($\mathcal{T}_{\mathrm{un}}$): `invert`, `reflect_horizontal`, `reflect_vertical` ve `reflect_diag` oluşur. Programlar yaprakları ilkeller veya önceden tanımlı yardımcılar, iç düğümleri dönüşüm işleçleri olan ağaçlarla gösterilir. Bir programı yürütmek $10\times10$ ikili bir örüntü verir; bir deneme, bu çıktı hedefle tam eşleştiğinde doğru puanlanır.

**Yardımcı Mekanizması.** Bir denemenin herhangi bir noktasında denek bir adımın çıktısını *yardımcı* olarak saklayabilir. Bundan sonra yardımcı yeni bir ilkel gibi davranır: yardımcı panelinde görünür ve daha fazla yardımcı kuranlar dahil herhangi bir işleçe verilebilir. Her yardımcı örüntüsünün küçük resmi olarak gösterilir; yardımcılara ad verilmez ve özdeş örüntüler yalnızca bir kez saklanır. Kütüphane her denek için özeldir ve ana görevin ve serbest oyun fazının kalanında kalır. Denekler yardımcıları istedikleri an silebilir. Öğretici sırasında kurulan yardımcılar ana görevden önce temizlenir.

**Arayüz.** Her deneme hedefi (sol üst), mevcut programın çizildiği bir çalışma tuvalini (orta), program adımı başına bir satır olan adım listesini (sağ) ve yardımcı kütüphanesini (alt; Şekil 6'ya bkz.) gösterir. Denek bir ilkel veya yardımcı seçip bir işleç uygulayarak programı kurar. Her adım programa bir satır ekler ve tuvali günceller. Bir adım işlenmeden önce tuval sonucunu önizler ve denek iptal edebilir. İşlendikten sonra bir adım kaldırılamaz. Gönder her an kullanılabilir.

**Deneme Akışı.** Bir deneme, hedefin boş bir tuvalin yanında gösterilmesiyle başladı. Denekler programı adım adım kurdu. Her adımı işlemeden önce önizleyebilir, işlenmemiş bir adımı iptal edebilir, bir adımı yardımcı olarak saklayabilir veya bir yardımcıyı silebilirdi. İşlenmiş adımlar geri alınamazdı ve zaman sınırı yoktu. Gönder'e basmak denemeyi bitirdi: hedefle tam eşleşme 1, başka her şey 0 puan aldı. Sonra bir geri bildirim paneli sonucu, kullanılan adım sayısını ve birikmiş puanı gösterdi; ardından sonraki deneme taze bir tuvalle başladı. Bütün denekler denemeleri aynı sırada gördü.

**Öğretici ve Anlama Denetimi.** Denekler önce tuvali, ilkelleri, işleçleri ve yardımcıları rehberli alıştırmayla tanıtan etkileşimli bir öğreticiden geçti. Sonra bir denemenin amacını, puanlama kuralını, yardımcıların denemeler arası kalıcılığını ve önizleme özelliğini kapsayan dört maddelik çoktan seçmeli bir sınav aldılar. Herhangi bir yanlış cevap deneği devam etmeden önce sınavı yeniden almak için yönergelere geri gönderdi.

**Serbest Oyun ve Değerlendirme.** Son müfredat denemesinden sonra denekler hedefsiz bir serbest oyun bloğuna girdi (Şekil 7); orada aynı DSL ve yardımcı kütüphanesiyle istedikleri her şeyi kurabilirdi. Yaratımlar adlandırılıp bir galeriye sunulabilirdi. Sonra denekler yaş, cinsiyet, algılanan zorluk, ilgi, yardımcı faydası ve serbest oyun keyfi hakkında bir sonuç anketi doldurdu.

**Gerçekleme.** Deney, statik bir web uygulamasıdır (HTML ve JavaScript) ve herhangi bir modern masaüstü tarayıcıda çalışır. Her eylem (adımlar, yardımcı kaydetme, silme, gönderim ve zaman damgaları) tarayıcıda kaydedilir ve her fazın sonunda sunucuya yüklenir.

**Şekil 6.** Görev arayüzü. A. Bir denemenin başlangıç görünümü. Sol: şimdiye kadarki toplam puan ve bu deneme için hedef şekil. Orta: Verilen İşlemler ve İlkel şekillerle hedef şekle uydurmak için çalışma alanı. Sağ: Adım listesi; her adım programın bir satırına karşılık gelir. Siyah kenarlar makalede yalnız örnekleme için eklenmiştir. B. Örnek önizleme. C. Örnek programlar. Her satırda bir satır numarası, o satırın yarattığı örüntünün küçük resmi ve karşılık gelen program (ilkeller, adımlar veya yardımcılar üzerinde işlemler) vardır. D. İlk yardımcı alanı. E. Örnek yardımcılı yardımcı alanı.

**Şekil 7.** Serbest oyun arayüzü. Son müfredat denemesinden sonra denekler aynı DSL ve yardımcı kütüphanesini kullanarak hedefsiz istedikleri örüntüyü kurar. Yaratımlar adlandırılıp paylaşılan bir galeriye gönderilebilir.

## Ek C. Davranışsal Deneyler

**Örüntü Kurucu Görevi.** Örüntü Kurucu Görevi'nde (PBT) katılımcılar, 6 ilkel, 3 ikili işlem ve 4 tekli dönüşümden oluşan ortak bir alana özgü dilden (DSL) programlar kurarak $10\times10$ ikili örüntüleri yeniden kurar (Şekil A-DSL). Görevin temel özelliği, herhangi bir ara kurgunun kalıcı bir yardımcı fonksiyona terfi ettirilebilmesi ve bunun sonraki bütün denemelerde yeniden kullanılabilir olmasıdır (Şekil 6). Her iki deney de aynı görevi ve DSL'yi kullanır; yalnızca hedef dizisinin örtük üretken yapısında farklılaşırlar. PBT görevinin ve arayüzünün tam tarifi Ek B'dedir.

**Katılımcılar.** Katılımcılar Prolific Academic aracılığıyla toplandı ve katılmadan önce bilgilendirilmiş onam verdi. Çalışma kurumumuzun etik kurulunca onaylandı (anonimlik için referans çıkarıldı). Deney 1'de 30 katılımcı toplandı (14 kadın; ortalama yaş $36.2 \pm 9.8$ yıl); 4'ü göreve ilgisizlik nedeniyle dışlandı ve 26'sı çözümlemede kaldı. Katılımcılara saat başına £7,27 ödendi. Deney 2'de 30 katılımcı toplandı (13 kadın, 1 ikili-olmayan; ortalama yaş $34.0 \pm 11.0$ yıl); 5'i aynı ölçütlerle dışlandı ve 25'i çözümlemede kaldı. Ödeme £6,00/saatti.

*(Okuyucu notu: Ana metin "N=60 katılımcı, her biri n=30" ile sonuçları bildirir ve ortalamaları n=30 ile hesaplar; Ek C ise dışlamadan sonra 26 ve 25 katılımcıyı gösterir. Dışlamanın sonuçlara nasıl yansıdığı metinde belirtilmemiştir.)*

**Uyaranlar.** İki deney farklı hedef dizileri kullandı; her biri ayrı bir örtük yapıyı somutlaştıracak biçimde tasarlandı. Deney 1'de Küme 1'deki 14 hedef (Şekil A-E1) otoregresif bir yapıyı izler: her hedef bir öncekinin bir DSL dönüşümüdür ve dizi boyunca iki uzun-erimli bağımlılık geçer. Deney 2'de Küme 2'deki 16 hedef (Şekil A-E2) bir işleç-grubu yapısını izler: hedefler paylaşılan örtük bir yardımcıyı sabit dört dönüşüm kümesiyle birleştiren dörtlü gruplar halinde örgütlenir; ardışık denemeler yüzey benzerliğini asgarîleştirecek biçimde tasarlanmıştır, bu da sığ örüntü eşleştirmesi yerine alttaki grup yapısının keşfini özendirir. Biçimsel müfredat tasarımı Ek G'de tarif edilmiştir.

**Usul.** Deney tamamen katılımcıların kendi masaüstü veya dizüstü bilgisayarlarında bir web tarayıcısında yürütüldü. Her oturum, arayüze ve DSL'ye aşinalığı sağlamak için etkileşimli bir öğretici ve ardından bir anlama denetimiyle başladı. Sonra katılımcılar müfredat hedeflerini sabit bir sırada, hedef örüntünün yanında gösterilen bir tuvalde adım adım çözüm programı kurarak işlediler. Hiçbir noktada değerlendirici geri bildirim verilmedi ve zaman sınırı yoktu. Son denemeden sonra katılımcılar kısa bir serbest oyun bloğunu ve bir sonuç anketini tamamladı.

## Ek D. Davranışsal Sonuçlar

**Denemeler boyunca genel doğruluk.** **Şekil 8.** D1 (**A**) ve D2'de (**B**) deneme başına ortalama insan doğruluğu; her biri $n = 30$. Hata çubukları: $\pm 1$ SEM. Kesikli çizgi: genel ortalama ($M$). Her çubuğun altındaki küçük resimler hedef örüntüyü gösterir.

## Ek E. LLM İstemleri (Ek F) — Özet

*(Aşağıdaki istem metinleri LLM'ye girdi olarak verilen İngilizce kod ve metindir; çeviri yapılmamış, modelin gördüğü özgün biçimde `orijinal/neurips_2026.tex`'te durmaktadır. Burada yapılarının özeti verilir.)*

**Model 3b (LLM-PS-H) ana kullanıcı istemi:** LLM'ye bir görev dizisi verildiği, görevlerin her denemede tek tek, önceki denemelerdeki görev geçmişiyle birlikte sunulduğu bildirilir. Her denemede şunlar verilir: (1) hedef $10\times10$ ikili dizi, (2) $10\times10$ ikili diziler olarak geometrik İLKELLER ve Python fonksiyonları olarak DÖNÜŞÜM işlemleri, (3) önceki denemelerde yazılmış yardımcı fonksiyonlar. İLKELLER ve DÖNÜŞÜMLER sabit ve paylaşılandır; yardımcılar sonraki bütün denemelere taşınır. KRİTİK KURALLAR: 1. Yeni ilkel yaratılamaz, çıktıda dizi elemanı sabit kodlanamaz, verilen değişken/fonksiyon yeniden tanımlanamaz; ilkeller ve dönüşüm fonksiyonları doğrudan çağrılmalıdır. 2. Döngü, liste üretimi, import yok. 3. Bütün yeniden kurmalar yalnız verilen ilkeller, dönüşümler ve yardımcılarla yapılmalıdır. 4. Yardımcılar tümüyle verilen ilkellerden, dönüşümlerden ve önceki yardımcılardan türemelidir. 5. Yalnız Python kodu yazılacak, yorum veya açıklama yok. Sonra ilkellerin (`blank`, `line_horizontal`, `line_vertical`, `diagonal`, `square`, `triangle`) $10\times10$ dizi tanımları ve dönüşüm fonksiyonları (`add`=mantıksal VEYA, `subtract`=a VE (DEĞİL b), `intersect`=VE, `invert`=DEĞİL, `reflect_horizontal`=flipud, `reflect_vertical`=fliplr, `reflect_diag`=devrik) ile bir örnek (`add(line_horizontal, line_vertical)` = artı işareti) gelir.

**Mevcut deneme istemi:** Hedef $10\times10$ dizi isteme eklenir; ör. "Bu deneme 3/14". **Başlangıç kodu istemi:** boş `reconstructed` fonksiyonu ve önceki denemelerde başarıyla kullanılan yardımcı fonksiyonlar (örn. `make_thick_plus`) eklenir; "yorum ve import eklemeyin, şu kodu tamamlayarak cevap verin". **Deneme geçmişi istemi (yalnız LLM-PS-H):** önceki bütün hedef örüntüler ve her birinin doğru kurulup kurulmadığı ("Doğru kuruldu") eklenir. **İnceleme geri bildirimi istemi:** model hedefle tam eşleşmeyen kod üretirse sonraki yinelemede kalan hak sayısı (toplam 5), yanlış program, ürettiği dizi ve hedef dizi gösterilip "lütfen yeniden deneyin" denir. **Model 3a (LLM-PS):** aynı temel istemleri kullanır ama görevin bir dizinin parçası olduğunu belirten ifadeleri ve deneme geçmişi istemini çıkarır; model önceki denemelerden habersiz yalnız mevcut görevde çalışır.

**LLM üretimi yeniden kurma örnekleri** (özgün Python kodları `orijinal/`de): Deney 1 basit örnek (Bileşik 1): `make_double_vertical` ve `make_double_horizontal` yardımcıları `add` ile birleştirilir. Deney 1 karmaşık örnek (Bileşik 14): 12 yardımcı fonksiyon (`make_x`, `make_corners`, `make_center_square`, `make_no_middle_rows` vb.) zinciri. Deney 2 basit (Bileşik 2): `make_x` ve `inner_square` ile `intersect`. Deney 2 karmaşık (Bileşik 4): `make_x`, `make_double_vertical`, `make_all_ones`, `make_center_pixel`, `make_extra_pixel` ile `subtract(full, make_x())` üzerine eklemeler.

## Ek H. Arama Uzayı Karmaşıklığı

Bir $\mathcal{X}$ ilkelleri ve $\mathcal{T}$ dönüşümleri üzerinde bir DSL varsayarız. Deneyler için ortak olarak belirli DSL 6 geometrik ilkel ($|\mathcal{X}| = 6$), 3 ikili dönüşüm işleci ve 4 tekli dönüşüm işlecinden ($|\mathcal{T}| = 7$ toplam) oluşur (Şekil A-DSL).

**Şekil 9.** İki deneyde kullanılan dönüşümler ve geometrik ilkellerin DSL'si 6 geometrik ilkel, 3 ikili işlem ve 4 tekli işlemden oluşur.

Programlar ikili ağaçlar olarak gösterilir: iç düğümler ikili işleçlere karşılık gelir, tekli işleçler tek çocuğa uygulanır, yapraklar ilkellere veya kütüphane yardımcılarına karşılık gelir. Sözdizimsel olarak farklı programların sayısının ağaç derinliğiyle hızla büyüdüğünü, bunun kütüphane öğrenmesini zorunlu kıldığını gösteririz.

### H.1 Kütüphane araması olmadan arama uzayı

$d$ derinliğinde aday program sayısı $|\mathcal{H}_d|$, yaprakları $\mathcal{X}$'ten alınan $d$ derinlikli tam ikili ağaçların sayısıyla alttan sınırlıdır: $|\mathcal{H}_d| \geq |\mathcal{X}|^{2^d} \cdot |\mathcal{T}_{\mathrm{bin}}|^{2^d - 1}$; burada $|\mathcal{T}_{\mathrm{bin}}| = 3$ ikili işleç sayısıdır. Derinlik $d \leq 4$ ile sınırlansa bile bu alt sınır $10^6$ aday programı aşar. Pratikte uzay daha da büyüktür; çünkü tekli işleçler her iç düğümde uygulanabilir ve dallanma çarpanını daha da artırır. Gözlemsel denklik budamalı aşağıdan-yukarı sayım [albarghouthi2013recursive, udupa2013transit] boş tuvalde özdeş çıktılar veren programları çökerterek bu uzayı küçültür; ancak etkin arama uzayı program derinliğinde süper-üstel kalır. Bu, hedef programların 3'ü aşan derinlik gerektirdiği sonraki denemelerde kütüphanesiz taban çizgisinin başarısızlığını güdüler. Arama uzayını sıkıştıracak kütüphane öğrenmesi olmadan sentezleyici, karmaşık hedefleri yeniden kurmak için yeterli derinlikteki programlara ulaşmadan hesaplama bütçesini tüketir.

### H.2 PBT'de erişilebilir uzayın boyutunu stokastik keşifle karakterize etmek

PBT alanının önemsiz olmayacak büyüklükte olduğunu göstermek için kılavuzsuz aramayla erişilebilen uzayı karakterize ettik. Program uzayında stokastik keşif binlerce benzersiz örüntü buluyorsa, bu erişilebilir uzayın aramayı zorlaştıracak kadar büyük olduğunu gösterir ve deneysel usulümüzde müfredata dayalı yapıyı güdüler.

DSL üzerinde 5 milyon adım süren, simetri-yanlı bir rastgele yürüyüş koştuk. Yürüyüş sınırlı bir program havuzu sürdürür; her adımda havuzdan bir program örneklenir ve bir aday üretmek için rastgele seçilen bir işleç uygulanır. Adaylar yalnızca çizilen çıktıları daha önce görülmemişse ve çıktı en az bir eksen boyunca simetrikse kabul edilir; aksi halde atılır. Simetri kısıtı, basit bir gestalt önseli ifade ederek görsel olarak daha ilginç olması olası bir erişilebilir uzay alt kümesi üretmek için konuldu.

Havuz doluyken ve yeni bir program kabul edilmesi gerektiğinde havuzdaki en uzun program çıkarılır; bu, havuzu daha kısa programlara yanlı tutar. Dolayısıyla bildirilen sayı gerçek program çeşitliliğinin bir alt sınırıdır: yürüyüş yalnızca görsel olarak ayrı, simetrik çıktıları sayar ve çıkarma ilkesi keşfi uzayın orta uzunluktaki bölgesiyle daha da sınırlar.

**Keşif eğrisi.** Yürüyüş $5 \times 10^6$ adımda doygunluk belirtisi olmaksızın 8791 benzersiz program keşfetti (Şekil 10). Keşfedilen programların program uzunluğuna göre dağılımı (Şekil 11) nedenini açıklar: çıkarma ilkesi daha kısa programları havuzda tutar, bunların terkipleri 65–75 düğüm çevresinde yoğunlaşan simetrik çıktılar üretme eğilimindedir ve o uzunluk ölçeğindeki uzay, yürüyüşün baştan sona hızlanan bir oranda yeni çıktılar bulmaya devam etmesine yetecek kadar büyüktür. Kabaca 150 düğümden uzun programlar, ayrıntılı keşfedilmeden havuzdan çıkarıldıkları için nadiren keşfedilir. Bu, bildirilen sayının kuramsal uzay boyutunun bir alt sınırı olduğunu, yürüyüşün orta uzunluktaki bölgeyi bile tüketmeye yaklaşmadığını daha da kurar. Daha uzun program kuyruğu neredeyse tümüyle örneklenmemiş kalır.

**Şekil 10.** Şekil A-DSL'deki DSL'yle PBT alanının stokastik keşfinde bulunan benzersiz örüntü sayısı.

**Şekil 11.** Rastgele aramayla üretilen program uzunluklarının dağılımı (ham DSL ilkeli sayısı olarak).

**Program çeşitliliği.** Şekil 12 örneklenmiş 225 çıktıdan rastgele bir mozaik gösterir. Aramayı yönlendirecek müfredat yapısı olmaksızın, DSL üzerinde simetri-yanlı bir rastgele yürüyüş, farklı program uzunluklarında 8791 ayrı görsel program keşfeder. Bu iki noktayı somutlaştırır. Birincisi, bu alanda işleyen kütüphane öğrenme algoritmaları, bu rastgele yürüyüşün muhafazakâr alt-sınır koşulları altında bile, her iki deneyin tek başına düşündüreceğinden çok daha büyük bir aday uzayla karşılaşır. İkincisi, Deney 1 ve 2'deki yapılı müfredatlar erişilebilir uzaydan rastgele örnekler değildir: kılavuzsuz aramanın güvenilir biçimde yüzeye çıkarmadığı örtük üretken yapıyı ortaya koymak için tasarlanmış kasıtlı seçimlerdir. Mozaiğin görsel çeşitliliği, bu DSL'nin geniş ve çeşitli bir uzayın temelinde olduğunu, müfredat tasarımının ilkeli iş yaptığını doğrular.

**Şekil 12.** $5 \times 10^6$ adımlı rastgele yürüyüşle üretilen 8.791 şekilden örneklenmiş 225 şekil (%2,6).

## Ek G. Deney Tasarımında Dizi Meta-yapısı

**Tanım:** Bir **müfredat**, ardışık denemelerde sunulan sıralı bir hedefler dizisi $\mathbf{P} = (p_1, p_2, \ldots, p_T)$'dir. Müfredatın yapılanabileceği farklı yolları ele alırız.

**Tanım:** Bir $\mathbf{P}$ müfredatının **Meta-Yapısı** $\mathcal{G}$, çözümler üzerinde ya önceki çözümler ya da paylaşılan örtük alt-programlar aracılığıyla yapılı bağımlılıklar getiren; her $p_t$'nin dizinin $(p_{t-n}, \ldots, p_{t-1})$ alt kümesi verildiğinde nasıl üretilebileceğini belirten bir üretken süreçtir; $n$, bağımlılıkların kaç adım geriye uzandığını belirtir.

**Tanım:** **Ardışık** müfredat, her çözümün bir önceki $p_{t-n}$ çözümüne ve $x \in \mathcal{X}$ ilkeline bir $\tau \in \mathcal{T}$ dönüşümü uygulanarak elde edildiği süreçtir: $\mathcal{G}_{\mathrm{seq}}: p_{t} = \tau(p_{t-n}, x)$, $0 < n < t$.

**Tanım:** **Uzun-erimli** müfredat, bağımlılıkların hemen önceki denemenin ötesine uzandığı, yani $\mathcal{G}_{\mathrm{seq}}$'de $n > 1$ olan bir ardışık müfredattır. Ardışık ve uzun-erimli müfredatlar arasındaki ayrım örtük meta-yapı $\mathcal{G}$'nin ne kadar kolay çıkarılabileceğini etkiler: ardışık bağımlılıklar ($n = 1$) yerel ve komşu denemelerden keşfedilebilirdir; uzun-erimli bağımlılıklar ($n > 1$) öğrenenin daha geniş bir zamansal pencere boyunca bilgiyi bütünleştirmesini gerektirir. Meta-yapının her iki biçiminin de son hedeflerin yardımcı olarak eklenmesini doğurması beklenir.

**Tanım:** **Paylaşılan yardımcı** müfredatı, programları ortak yeniden kullanılabilir bir $h \in \mathcal{P}$ alt-programından türeten üretken bir usuldür: $K$ ardışık program grubu $\{p_{t}, \ldots, p_{t+K-1}\}$, $h$ gruptaki her çözümün alt-programıysa $h$'ye göre paylaşılan yardımcı müfredatını izler: $\mathcal{G}_{\mathrm{hlp}}: h \sqsubseteq p_{t+k}$, $k = 0, \ldots, K-1$.

**Tanım:** **İşleç-grubu** müfredatı, $K$ ardışık program grubu $\{p_{t}, \ldots, p_{t+K-1}\}$'nin hepsinin, sabit bir işleç kümesinden verilen sırada ve tam bir kez ayrı dönüşümlerin, paylaşılan bir $h \in \mathcal{P}$ alt-programına ve bir $x \in \mathcal{X}$ ilkeline uygulanmasıyla üretildiği süreçtir.

**Tanım:** Belirli bir **4-işleç-grubu** müfredatı: paylaşılan bir $h \in \mathcal{P}$ alt-programı ve bir $x \in \mathcal{X}$ ilkeli verildiğinde grup sabit işleç kümesiyle üretilen dört programdan oluşur: $\mathcal{G}_{\mathrm{grp}}: \{p_{t+k}\}_{k=0}^{3} = \{\textsc{Add}(h, x), \textsc{Subtract}(h, x), \textsc{Overlap}(h, x), \textsc{Add}(\textsc{Invert}(h), x)\}$; $h$'nin tutumlu bir paylaşılan yapı olması kısıtıyla: gruptaki hiçbir hedef, gruptaki başka bir hedeften $\mathcal{G}_{\mathrm{grp}}$'nin öngördüğünden daha kısa bir programla türetilemez. İşleç-grubu meta-yapısı farklı işleç kümelerine doğrudan genellenir.

### G.1 Deney 1 Meta-Yapısı ve deneme dizisi

Deney 1'in amacı, insanların kütüphane öğrenme modellerinin öngördüğü gibi yeniden kullanılabilir yardımcılara dayandığını kurmaktır.

**Tablo 2.** Deney 1 için müfredat yapısı. Her satır bir hedef örüntüyü ($P_t$), program ifadesini ve yapısal türünü belirtir. Ardışık denemeler hemen önceki hedefe, uzun-erimli denemeler daha önceki hedeflere bağlıdır. $P_4$ ve $P_5$ hedefleri ortak bir `Diagonal_Cross` yardımcısından türer.

| Örüntü | Program | Tür |
| :-- | :-- | :-- |
| $P_1$ | `fat_cross()` | – |
| $P_2$ | `add(`$P_1$`, square)` | Ardışık |
| $P_3$ | `invert(`$P_2$`)` | Ardışık |
| $P_4$ | `subtract(square, Diagonal_Cross)` | Yardımcı |
| $P_5$ | `add(square, Diagonal_Cross)` | Yardımcı |
| $P_6$ | `invert(`$P_5$`)` | Ardışık |
| $P_7$ | `add(Diagonal_Cross,` $P_1$`)` | Uzun-erimli |
| $P_8$ | `intersect(Diagonal_Cross,` $P_1$`)` | Uzun-erimli |
| $P_9$ | `add(`$P_8$`, square)` | Ardışık |
| $P_{10}$ | `invert(`$P_9$`)` | Ardışık |
| $P_{11}$ | `add(`$P_8$`, invert(`$P_1$`))` | Uzun-erimli |
| $P_{12}$ | `add(invert(`$P_{11}$`), square)` | Ardışık |
| $P_{13}$ | `subtract(Diagonal_Cross,` $P_8$`)` | Uzun-erimli |
| $P_{14}$ | `subtract(`$P_7$`,` $P_8$`)` | Uzun-erimli |

**Şekil 13.** Deney 1'den hedef dizisi.

**Öngörü:** Deney 1'de müfredata ardışık ve uzun-erimli bağımlılıklar hâkimdir (Tablo 2); dolayısıyla bu örtük meta-yapıya duyarlı katılımcıların giderek hedef programların kendilerini yardımcı olarak saklamaları beklenir.

**Şekil 14.** Deney 1'de bireysel kullanıcıların yaptığı yardımcı örnekleri. A, B, C, D panelleri farklı kullanıcıların yardımcılarını gösterir. Her kullanıcının kütüphanesi deney ilerledikçe nihai hedefleri yardımcı olarak içermeye yanlılaşır.

### G.2 Deney 2 Meta-Yapısı ve deneme dizisi

Amacımız, insanların örtük üretken sürecin kendisine (meta-yapı) duyarlı olduğunu göstermektir. Bunun için Deney 2, **4-işleç-grubu** müfredatıyla üretilen bir hedef dizisi kullanır. Deney 2'deki her hedef için aynı meta-yapı kullanılır. Burada her deneme bir yardımcının basit bir dönüşümüyle üretilir.

**Şekil 15.** Deney 2'den hedef dizisi.

**Şekil 16.** Deney 2 için tasarım gereği 4-işleç-grubunda kullanılan yardımcılar.

**Öngörü 1:** Alttaki meta-yapıyı çıkarmak birkaç örnek aldığından, insanların yapacağı yardımcılar tasarım yardımcılarından sapacak ama giderek gerçek küme yönünde yanlılaşacaktır.

**Öngörü 2:** İnsanların yapacağı yardımcılar, D1'deki gibi nihai hedefler yerine ara yapıyı temsil etmeye yanlılaşacaktır.

**Şekil 17.** Deney 2'de bireysel kullanıcıların yaptığı yardımcı örnekleri. A, B, C, D panelleri farklı kullanıcıların yardımcılarını gösterir. Her kullanıcının kütüphanesi (nihai hedeflerin aksine) tasarım yardımcılarını içermeye yanlıdır.

---

Kaynakça: orijinal `.bib` dosyası `orijinal/` dizinindedir; çevrilmemiştir.
