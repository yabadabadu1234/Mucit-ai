# Tahavvül-i Muttasıl Tip Nazariyesi: Riyâziyâtın Vahdet Esasları

## Üçüncü Bab: Mecmûalar ve Mantık

**Univalent Foundations Program (Vahdet Esasları Programı)**

---

> **Künye ve nüsha.** Aslın unvanı: *Homotopy Type Theory: Univalent Foundations of Mathematics*, birinci neşir, Institute for Advanced Study (Princeton), 2013. Müellifi: The Univalent Foundations Program (2012–2013 senesinde Institute for Advanced Study'de toplanan riyâziyeciler heyeti). Bu bab, aslın üçüncü babı olan *Sets and logic*'tir. Esas alınan metin, kitabın LaTeX aslının `logic.tex` dosyasıdır: <https://github.com/HoTT/book/blob/master/logic.tex> (deponun `master` dalı, 1 Teşrîn-i sânî 2026'da indirilmiştir).
>
> **Lisans.** Asıl eser *Creative Commons Atıf-Aynı Lisansla Paylaş 3.0 Umûmî (Creative Commons Attribution-ShareAlike 3.0 Unported)* lisansıyla neşredilmiştir (deponun `README.md` dosyasında yazılıdır): <http://creativecommons.org/licenses/by-sa/3.0/>. Bu tercüme de aynı lisansla, aynı şartlarla neşredilir. Atıf: The Univalent Foundations Program, *Homotopy Type Theory: Univalent Foundations of Mathematics*, Institute for Advanced Study, 2013. Tercümede asla nazaran yapılan değişiklik: metnin Osmanlıcaya nakli ve düsturlardaki harflerin kelimelerle değiştirilmesi.
>
> **Tercüme usulü.** Metin cümle cümle, hiçbir cümle atlanmadan ve hiçbir şey ilâve edilmeden nakledilmiştir. Şerh, hâşiye ve mütercim kaydı yoktur. Aslın LaTeX dosyasında yorum işaretiyle kapatılmış ve basılı kitapta görünmeyen satırlar tercüme edilmemiştir; fihrist (index) komutları da basılı metinde görünmediği için tercümeye girmemiştir. Diğer bablara yapılan atıflar aslın numaralarıyla verilmiştir; numarasını kesin olarak bilemediğim birkaç atıfta yalnız bab yahut fasıl adı yazılmıştır.
>
> **Düsturların yazılışı.** Padişahın kaidesi mûcibince düsturlarda hiçbir kemmiyet ve hiçbir tip harfle yazılmamış, her biri mânâsını söyleyen bir kelimeyle yazılmıştır. Aslın harflerinin hangi kelimeyle karşılandığı sondaki **İsimler cedveli**nde gösterilmiştir. Ameliye işaretleri (∏, ∑, →, ×, +, ≃, =, ≡, ¬, ∘, ∙, ⁻¹, ‖ ‖, ∧, ∨, ⇒, ⇔, ∀, ∃, ⊆, ∈, ∩, ∪, ∖) ile rakamlar ve kalın rakamlı tip adları ($\mathbf{0}$, $\mathbf{1}$, $\mathbf{2}$) bırakılmıştır, zîrâ bunlar kemmiyet değil fiil ve adettir.

---

Tip nazariyesi, sûrî olsun gayr-ı sûrî olsun, tipleri ve onların unsurlarını işlemeye mahsus bir kaideler mecmûudur. Fakat riyâziyâtı tabiî lisanla gayr-ı sûrî olarak yazarken, umûmiyetle âşinâ kelimeler, bilhassa "ve" ile "veya" gibi mantıkî rabıtalar ve "her biri için" ile "vardır" gibi mantıkî sûrlar kullanırız. Mecmûalar nazariyesinin aksine, tip nazariyesi bize bu İngilizce ibareleri tipler üzerinde ameliyeler olarak telakkî etmek için birden fazla yol sunar. Bu muhtemel iştirakin, mahallî yahut küllî itibarlar vaz' edilerek, gayr-ı sûrî riyâziyâta yeni işaretler idhâl edilerek, yahut her ikisiyle, giderilmesi lâzımdır. Bu biraz alışmayı gerektirir; fakat bunu şu vakıa telafi eder ki tip nazariyesi mantığın bu daha ince tahlîline imkân verdiği için, riyâziyâtı, mecmûalar nazariyesine dayanan esaslara nazaran daha az "lisan sû-i istimali" ile, daha sadık bir sûrette temsil edebiliriz. Bu babda ilgili meseleleri izah edecek ve yaptığımız tercihleri haklı çıkaracağız.

## 3.1 Mecmûalar ve buud-sayısı-tipler

Tip nazariyesinin mantığı ile mecmûalar nazariyesinin mantığı arasındaki irtibatı izah etmek için, tip nazariyesinde bir *mecmûa* mefhûmuna sahip olmak faydalıdır. Umûmiyetle tipler fezâlar yahut yüksek zümremsiler gibi davranırken, onların, an'anevî bir mecmûalar nazariyesi sistemindeki mecmûalara daha çok benzer şekilde davranan bir alt sınıfı vardır. Makûlî olarak, bir nesneler mecmûası ve yüksek teşâküller olarak yalnız ayniyet teşâkülleri ile tayin edilen *munfasıl* zümremsileri mülâhaza edebiliriz; vaz'î olarak ise munfasıl hendese-i vaz'iyyeye sahip fezâları mülâhaza edebiliriz. Daha umûmî olarak, bu nevîden olanlara *tekâfü' eden* zümremsileri yahut fezâları mülâhaza edebiliriz; tip nazariyesinde yaptığımız her şey tahavvül-i muttasıl kaydıyla olduğundan, farkı ayırt edebilmeyi bekleyemeyiz.

Hadsî olarak, bir tipin, eğer hiçbir yüksek tahavvül-i muttasıl malûmatı yoksa, bu mânâda "bir mecmûa olmasını" beklerdik: herhangi iki müvâzî tarîk (tahavvül-i muttasıl kaydıyla) müsâvîdir, ve bütün buudlarda müvâzî yüksek tarîkler için de benzer şekilde. Bereket versin, tahavvül-i muttasıl tip nazariyesinde her şey kendiliğinden funktorlu ve muttasıl olduğundan, bunu en alt mertebede sormanın kâfi olduğu ortaya çıkar.

**Tarif 3.1.1.** **Tip** bir tip olsun. Eğer her $\text{unsur}, \text{öteki} : \text{Tip}$ ve her $\text{tarîk}, \text{diğer-tarîk} : \text{unsur} = \text{öteki}$ için $\text{tarîk} = \text{diğer-tarîk}$ ise, Tip'e bir **mecmûa** denir.

Daha dakik olarak, $\text{mecmûa-mı}(\text{Tip})$ kaziyyesi şu tip olarak tarif edilir:

$$\text{mecmûa-mı}(\text{Tip}) :\equiv \prod_{\text{unsur}, \text{öteki} : \text{Tip}} \; \prod_{\text{tarîk}, \text{diğer-tarîk} : \text{unsur} = \text{öteki}} (\text{tarîk} = \text{diğer-tarîk}).$$

1.1. fasılda zikredildiği üzere, tahavvül-i muttasıl tip nazariyesindeki mecmûalar, küllî bir "mensubiyet mahmûlü" $\in$ bulunmaması bakımından, Zermelo-Fraenkel mecmûalar nazariyesindeki mecmûalara benzemez. Onlar daha çok bünyevî riyâziyâtta ve makûleler nazariyesinde kullanılan mecmûalara benzer ki bunların unsurları, tâbiler ve münasebetlerle bünye verdiğimiz "mücerred noktalar"dır. Onları mecmûalara dayanan riyâziyâtın çoğu için esasî bir sistem olarak kullanmak için ihtiyacımız olan bundan ibarettir; onuncu babda bazı misaller göreceğiz.

Hangi tipler mecmûadır? Yedinci babda bu suâlin daha umûmî bir şeklini derinlemesine tetkik edeceğiz; fakat şimdilik bazı kolay misaller gözlemleyebiliriz.

**Misal 3.1.2.** $\mathbf{1}$ tipi bir mecmûadır. Zîrâ Kaziyye 2.8.1 mûcibince, her $\text{unsur}, \text{öteki} : \mathbf{1}$ için $(\text{unsur} = \text{öteki})$ tipi $\mathbf{1}$'e tekâfü' eder. $\mathbf{1}$'in herhangi iki unsuru müsâvî olduğundan, bu, $\text{unsur} = \text{öteki}$'nin herhangi iki unsurunun müsâvî olmasını gerektirir.

**Misal 3.1.3.** $\mathbf{0}$ tipi bir mecmûadır; zîrâ verilmiş herhangi $\text{unsur}, \text{öteki} : \mathbf{0}$ için, $\mathbf{0}$'ın istikrâ mebde'i ile istediğimiz her şeyi istihrac edebiliriz.

**Misal 3.1.4.** Tabiî adetlerin **Tabiî** tipi de bir mecmûadır. Bu, Kaziyye 2.13.1'den çıkar; zîrâ bütün $\text{unsur} =_{\text{Tabiî}} \text{öteki}$ ayniyet tipleri ya $\mathbf{1}$'e ya $\mathbf{0}$'a tekâfü' eder, ve $\mathbf{1}$'in yahut $\mathbf{0}$'ın herhangi iki sâkini müsâvîdir. Bu vakıanın başka bir ispatını yedinci babda göreceğiz.

Şimdiye kadar mülâhaza ettiğimiz tip teşkil eden ameliyelerin çoğu mecmûaları da muhafaza eder.

**Misal 3.1.5.** **Tip** ve **Diğer-tip** mecmûa ise, $\text{Tip} \times \text{Diğer-tip}$ de öyledir. Zîrâ verilmiş $\text{unsur}, \text{öteki} : \text{Tip} \times \text{Diğer-tip}$ ve $\text{tarîk}, \text{diğer-tarîk} : \text{unsur} = \text{öteki}$ için, Kaziyye 2.6.2 mûcibince $\text{tarîk} = \text{çift-tarîki}(\text{izdüşüm-tarîki}_1(\text{tarîk}), \text{izdüşüm-tarîki}_2(\text{tarîk}))$ ve $\text{diğer-tarîk} = \text{çift-tarîki}(\text{izdüşüm-tarîki}_1(\text{diğer-tarîk}), \text{izdüşüm-tarîki}_2(\text{diğer-tarîk}))$ elde ederiz. Fakat Tip bir mecmûa olduğundan $\text{izdüşüm-tarîki}_1(\text{tarîk}) = \text{izdüşüm-tarîki}_1(\text{diğer-tarîk})$, ve Diğer-tip bir mecmûa olduğundan $\text{izdüşüm-tarîki}_2(\text{tarîk}) = \text{izdüşüm-tarîki}_2(\text{diğer-tarîk})$'dur; binâenaleyh $\text{tarîk} = \text{diğer-tarîk}$ olur.

Benzer şekilde, eğer Tip bir mecmûa ise ve $\text{Lif} : \text{Tip} \to \text{Kâinat}$ öyledir ki her $\text{Lif}(\text{unsur})$ bir mecmûadır, o zaman $\sum_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$ bir mecmûadır.

**Misal 3.1.6.** Eğer Tip *herhangi* bir tip ise ve $\text{Lif} : \text{Tip} \to \text{Kâinat}$ öyledir ki her $\text{Lif}(\text{unsur})$ bir mecmûadır, o zaman $\prod_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$ tipi bir mecmûadır. Zîrâ $\text{tâbi}, \text{diğer-tâbi} : \prod_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$ ve $\text{tarîk}, \text{diğer-tarîk} : \text{tâbi} = \text{diğer-tâbi}$ olduğunu farz edelim. Tâbi genişliği ile

$$\text{tarîk} = \text{tâbi-genişliği}\big(\text{unsur} \mapsto \text{noktada-tatbik}(\text{tarîk}, \text{unsur})\big) \quad\text{ve}\quad \text{diğer-tarîk} = \text{tâbi-genişliği}\big(\text{unsur} \mapsto \text{noktada-tatbik}(\text{diğer-tarîk}, \text{unsur})\big)$$

elde ederiz. Fakat her $\text{unsur} : \text{Tip}$ için

$$\text{noktada-tatbik}(\text{tarîk}, \text{unsur}) : \text{tâbi}(\text{unsur}) = \text{diğer-tâbi}(\text{unsur}) \qquad\text{ve}\qquad \text{noktada-tatbik}(\text{diğer-tarîk}, \text{unsur}) : \text{tâbi}(\text{unsur}) = \text{diğer-tâbi}(\text{unsur})$$

olur; binâenaleyh $\text{Lif}(\text{unsur})$ bir mecmûa olduğundan $\text{noktada-tatbik}(\text{tarîk}, \text{unsur}) = \text{noktada-tatbik}(\text{diğer-tarîk}, \text{unsur})$ elde ederiz. Şimdi tâbi genişliğini tekrar kullanarak, $(\text{unsur} \mapsto \text{noktada-tatbik}(\text{tarîk}, \text{unsur}))$ ve $(\text{unsur} \mapsto \text{noktada-tatbik}(\text{diğer-tarîk}, \text{unsur}))$ merbût tâbileri müsâvîdir; ve binâenaleyh ($\text{tatbik}_{\text{tâbi-genişliği}}$ uygulanarak) tarîk ile diğer-tarîk da müsâvîdir.

Daha fazla misal için Temrin 3.2 ve 3.3'e bakınız. Tahavvül-i muttasıl tip nazariyesindeki bütün mecmûaların alt sisteminin (makûlesinin) daha nizamlı bir tetkiki için onuncu babda bakınız.

Mecmûalar, *buud-sayısı tahavvül-i muttasıl tipleri* denen şeylerin bir merdiveninin ancak ilk basamağıdır. Bir sonraki basamak, makûleler nazariyesindeki 1-zümremsilere benzeyen *1-tipler*den ibarettir. Bir mecmûanın (ki ona *0-tip* de diyebiliriz) tarif edici hassası, hiçbir basit olmayan tarîke sahip olmamasıdır. Benzer şekilde bir 1-tipin tarif edici hassası, tarîkler arasında hiçbir basit olmayan tarîke sahip olmamasıdır:

**Tarif 3.1.7.** Eğer her $\text{unsur}, \text{öteki} : \text{Tip}$ ve $\text{tarîk}, \text{diğer-tarîk} : \text{unsur} = \text{öteki}$ ve $\text{yüksek-tarîk}, \text{diğer-yüksek-tarîk} : \text{tarîk} = \text{diğer-tarîk}$ için $\text{yüksek-tarîk} = \text{diğer-yüksek-tarîk}$ ise, **Tip** tipine bir **1-tip** denir.

Benzer şekilde 2-tipleri, 3-tipleri ve saireyi tarif edebiliriz. Buud-sayısı-tip umûmî mefhûmunu yedinci babda istikrâ ile tarif edecek ve **buud-sayısı**nın farklı kıymetleri için buud-sayısı-tipler arasındaki münasebetleri tetkik edeceğiz.

Maamâfih şimdilik iki vakıayı akılda tutmak faydalıdır. Evvelâ, buud-sayıları yukarıya doğru kapalıdır: eğer Tip bir buud-sayısı-tip ise, Tip bir $(\text{buud-sayısı} + 1)$-tiptir. Meselâ:

**Yardımcı Kaziyye 3.1.8.** Eğer Tip bir mecmûa ise (yâni $\text{mecmûa-mı}(\text{Tip})$ meskûn ise), Tip bir 1-tiptir.

*İspat.* $\text{şâhid} : \text{mecmûa-mı}(\text{Tip})$ olduğunu farz edelim; o zaman her $\text{unsur}, \text{öteki} : \text{Tip}$ ve $\text{tarîk}, \text{diğer-tarîk} : \text{unsur} = \text{öteki}$ için $\text{şâhid}(\text{unsur}, \text{öteki}, \text{tarîk}, \text{diğer-tarîk}) : \text{tarîk} = \text{diğer-tarîk}$ elde ederiz. unsur, öteki ve tarîk sâbit tutulsun ve $\text{seçici} : \prod_{\text{diğer-tarîk} : \text{unsur} = \text{öteki}} (\text{tarîk} = \text{diğer-tarîk})$ tâbisi $\text{seçici}(\text{diğer-tarîk}) :\equiv \text{şâhid}(\text{unsur}, \text{öteki}, \text{tarîk}, \text{diğer-tarîk})$ ile tarif edilsin. O zaman her $\text{yüksek-tarîk} : \text{diğer-tarîk} = \text{üçüncü-tarîk}$ için $\text{merbût-tatbik}_{\text{seçici}}(\text{yüksek-tarîk}) : \text{nakil}(\text{yüksek-tarîk}, \text{seçici}(\text{diğer-tarîk})) = \text{seçici}(\text{üçüncü-tarîk})$ elde ederiz. Binâenaleyh ikinci babın 2.11. faslındaki, tarîk tiplerinde nakle dair netice mûcibince $\text{seçici}(\text{diğer-tarîk}) \cdot \text{yüksek-tarîk} = \text{seçici}(\text{üçüncü-tarîk})$ elde ederiz.

Bilhassa, Tarif 3.1.7'deki gibi unsur, öteki, tarîk, diğer-tarîk ve $\text{yüksek-tarîk}, \text{diğer-yüksek-tarîk} : \text{tarîk} = \text{diğer-tarîk}$ verilmiş olsun ve seçici yukarıdaki gibi tarif edilsin. O zaman $\text{seçici}(\text{tarîk}) \cdot \text{yüksek-tarîk} = \text{seçici}(\text{diğer-tarîk})$ ve aynı zamanda $\text{seçici}(\text{tarîk}) \cdot \text{diğer-yüksek-tarîk} = \text{seçici}(\text{diğer-tarîk})$ olur; binâenaleyh sadeleştirme ile $\text{yüksek-tarîk} = \text{diğer-yüksek-tarîk}$ olur. ∎

Saniyen, tiplerin buud-sayısına göre bu tabakalaşması, bütün tiplerin mecmûa olmadığı mânâsında, bozuk değildir:

**Misal 3.1.9.** **Kâinat** bir mecmûa değildir. Bunu ispat etmek için, bir **Tip** tipi ile $\text{aksiyet}_{\text{Tip}}$'e müsâvî olmayan bir $\text{tarîk} : \text{Tip} = \text{Tip}$ tarîki göstermek kâfidir. $\text{Tip} = \mathbf{2}$ alınsın, ve $\text{çevirme} : \text{Tip} \to \text{Tip}$ tâbisi $\text{çevirme}(\text{kâzib}) :\equiv \text{sâdık}$ ve $\text{çevirme}(\text{sâdık}) :\equiv \text{kâzib}$ ile tarif edilsin. O zaman her unsur için $\text{çevirme}(\text{çevirme}(\text{unsur})) = \text{unsur}$ olur (kolay bir hâllere ayırma ile); binâenaleyh çevirme bir tekâfü'dür. Binâenaleyh vahdet ile çevirme bir $\text{tarîk} : \text{Tip} = \text{Tip}$ tarîki doğurur.

Eğer tarîk $\text{aksiyet}_{\text{Tip}}$'e müsâvî olsaydı, o zaman (yine vahdet ile) çevirme, Tip'in ayniyet tâbisine müsâvî olurdu. Fakat bu, $\text{kâzib} = \text{sâdık}$ olmasını gerektirirdi ki Mülâhaza 2.12.6'ya zıttır.

Altıncı ve sekizinci bablarda göstereceğiz ki her buud-sayısı için, buud-sayısı-tip olmayan tipler vardır.

Dikkat edilsin ki, Tip ancak ve ancak her $\text{unsur}, \text{öteki} : \text{Tip}$ için $\text{unsur} =_{\text{Tip}} \text{öteki}$ ayniyet tipi bir mecmûa olduğunda bir 1-tiptir. (Binâenaleyh Yardımcı Kaziyye 3.1.8, müsâvî olarak, bir mecmûanın ayniyet tiplerinin de mecmûa olduğunu söylüyor diye okunabilirdi.) Bu, yedinci babda vereceğimiz buud-sayısı-tiplerin rücû'lu tarifinin esası olacaktır.

Bu tavsifi mecmûalardan "aşağıya doğru" da teşmîl edebiliriz. Yâni bir Tip tipi, tam her $\text{unsur}, \text{öteki} : \text{Tip}$ için $\text{unsur} =_{\text{Tip}} \text{öteki}$'nin herhangi iki unsuru müsâvî olduğunda bir mecmûadır. Mecmûalar müsâvî olarak 0-tipler olduğundan, bu sonraki hassaya (onun herhangi iki unsurunun müsâvî olması hassasına) sahip bir tipe bir *(−1)-tip* demek tabiîdir. Böyle tipler *mahz kaziyyeler* sayılabilir ve onların tetkiki tam da umûmiyetle "mantık" denen şeydir; bu, babın geri kalanında bizi meşgul edecektir.

## 3.2 Tipler olarak kaziyyeler mi?

Şimdiye kadar, 1.11. fasılda tarif edilen dolaysız "tipler olarak kaziyyeler" felsefesini takip ediyorduk; buna göre "$\text{Kaziyye}(\text{unsur})$ olacak tarzda bir $\text{unsur} : \text{Tip}$ vardır" gibi İngilizce ibareler, $\sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$ gibi tekabül eden tiplerle tefsir edilir ve bir beyanın ispatı, muayyen bir unsurun o tipte sâkin olduğuna hükmetmek sayılır. Maamâfih bu okuyuştan çıkan "mantığın" klasik bir riyâziyeciye yabancı göründüğü bazı yollar da gördük. Meselâ Kaziyye 2.15.7'de şu beyanın

> (3.2.1) "Eğer her $\text{unsur} : \text{Esas}$ için $\text{Bağ}(\text{unsur}, \text{seçilen})$ olacak tarzda bir $\text{seçilen} : \text{Lif}(\text{unsur})$ varsa, o zaman her $\text{unsur} : \text{Esas}$ için $\text{Bağ}(\text{unsur}, \text{seçici}(\text{unsur}))$ olacak tarzda bir $\text{seçici} : \prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur})$ tâbisi vardır",

klasik *ihtiyar mütearifesine* benzeyen bu beyanın, bu okuyuş altında daima doğru olduğunu gördük. Bu, tipler olarak kaziyyeler mantığının dikkate şayan ve çok defa faydalı bir hususiyetidir; fakat aynı zamanda, ihtiyar mütearifesinin mantıkî bir hakikat değil ilâve bir "mütearife" olduğu klasik mantık tefsirinden ne kadar ehemmiyetli derecede farklı olduğunu da gösterir.

Diğer taraftan, şimdi klasik *çift nefy kanununa* ve *imtinâ'-ı vasat kanununa* benzeyen tekabül eden beyanların vahdet mütearifesi ile bağdaşmadığını da gösterebiliriz.

**Kaziyye 3.2.2.** Her $\text{Tip} : \text{Kâinat}$ için $\neg(\neg \text{Tip}) \to \text{Tip}$ olması doğru değildir.

*İspat.* Hatırlansın ki $\neg \text{Tip} \equiv (\text{Tip} \to \mathbf{0})$'dır. "… olması doğru değildir" sözünü de $\neg$ âmili olarak okuruz. Binâenaleyh bu beyanı ispat etmek için, verilmiş bir $\text{seçici} : \prod_{\text{Tip} : \text{Kâinat}} (\neg\neg \text{Tip} \to \text{Tip})$ farz etmek ve $\mathbf{0}$'ın bir unsurunu inşa etmek kâfidir.

Aşağıdaki ispatın fikri, seçicinin, tip nazariyesindeki her tâbi gibi, "muttasıl" olduğunu gözlemlemektir. Vahdet-i tekâfü' ile bu, seçicinin tiplerin tekâfü'lerine göre *tabiî* olmasını gerektirir. Bundan ve sâbit noktası olmayan bir zâtî tekâfü'den bir tenâkuz çıkarabileceğiz.

$\text{çevirme} : \mathbf{2} \simeq \mathbf{2}$, Misal 3.1.9'daki gibi $\text{çevirme}(\text{sâdık}) :\equiv \text{kâzib}$ ve $\text{çevirme}(\text{kâzib}) :\equiv \text{sâdık}$ ile tarif edilen tekâfü' olsun. $\text{tarîk} : \mathbf{2} = \mathbf{2}$, vahdet ile çevirmeye tekabül eden tarîk olsun, yâni $\text{tarîk} :\equiv \text{vahdet}(\text{çevirme})$. O zaman $\text{seçici}(\mathbf{2}) : \neg\neg\mathbf{2} \to \mathbf{2}$ ve

$$\text{merbût-tatbik}_{\text{seçici}}(\text{tarîk}) : \text{nakil}^{\,\text{Tip} \mapsto (\neg\neg \text{Tip} \to \text{Tip})}\big(\text{tarîk}, \text{seçici}(\mathbf{2})\big) = \text{seçici}(\mathbf{2})$$

elde ederiz. Binâenaleyh her $\text{şâhid} : \neg\neg\mathbf{2}$ için

$$\text{noktada-tatbik}\big(\text{merbût-tatbik}_{\text{seçici}}(\text{tarîk}), \text{şâhid}\big) : \text{nakil}^{\,\text{Tip} \mapsto (\neg\neg \text{Tip} \to \text{Tip})}\big(\text{tarîk}, \text{seçici}(\mathbf{2})\big)(\text{şâhid}) = \text{seçici}(\mathbf{2})(\text{şâhid})$$

elde ederiz.

Şimdi (2.9.4) mûcibince, $\text{seçici}(\mathbf{2}) : \neg\neg\mathbf{2} \to \mathbf{2}$'yi $\text{Tip} \mapsto (\neg\neg \text{Tip} \to \text{Tip})$ tip ailesinde tarîk boyunca nakletmek, kendi mütehavvilini $\text{Tip} \mapsto \neg\neg \text{Tip}$ tip ailesinde $\text{tarîk}^{-1}$ boyunca nakleden, $\text{seçici}(\mathbf{2})$'yi uygulayan, sonra neticeyi $\text{Tip} \mapsto \text{Tip}$ tip ailesinde tarîk boyunca nakleden tâbiye müsâvîdir:

$$\text{nakil}^{\,\text{Tip} \mapsto (\neg\neg \text{Tip} \to \text{Tip})}\big(\text{tarîk}, \text{seçici}(\mathbf{2})\big)(\text{şâhid}) = \text{nakil}^{\,\text{Tip} \mapsto \text{Tip}}\Big(\text{tarîk}, \text{seçici}(\mathbf{2})\big(\text{nakil}^{\,\text{Tip} \mapsto \neg\neg \text{Tip}}(\text{tarîk}^{-1}, \text{şâhid})\big)\Big).$$

Maamâfih herhangi iki $\text{şâhid}, \text{diğer-şâhid} : \neg\neg\mathbf{2}$ noktası, tâbi genişliği ile müsâvîdir; zîrâ her $\text{red} : \neg\mathbf{2}$ için $\text{şâhid}(\text{red}) : \mathbf{0}$ olur ve binâenaleyh her neticeyi, bilhassa $\text{şâhid}(\text{red}) = \text{diğer-şâhid}(\text{red})$'yi istihrac edebiliriz. Binâenaleyh $\text{nakil}^{\,\text{Tip} \mapsto \neg\neg \text{Tip}}(\text{tarîk}^{-1}, \text{şâhid}) = \text{şâhid}$ elde ederiz, ve böylece $\text{noktada-tatbik}(\text{merbût-tatbik}_{\text{seçici}}(\text{tarîk}), \text{şâhid})$'dan bir müsâvât elde ederiz:

$$\text{nakil}^{\,\text{Tip} \mapsto \text{Tip}}\big(\text{tarîk}, \text{seçici}(\mathbf{2})(\text{şâhid})\big) = \text{seçici}(\mathbf{2})(\text{şâhid}).$$

Nihayet, 2.10. fasılda münakaşa edildiği üzere, $\text{Tip} \mapsto \text{Tip}$ tip ailesinde $\text{tarîk} \equiv \text{vahdet}(\text{çevirme})$ tarîki boyunca nakletmek, çevirme tekâfü'ünü uygulamaya müsâvîdir; binâenaleyh

$$\text{çevirme}\big(\text{seçici}(\mathbf{2})(\text{şâhid})\big) = \text{seçici}(\mathbf{2})(\text{şâhid}) \tag{3.2.3}$$

elde ederiz.

Maamâfih şunu da ispat edebiliriz:

$$\prod_{\text{unsur} : \mathbf{2}} \neg\big(\text{çevirme}(\text{unsur}) = \text{unsur}\big). \tag{3.2.4}$$

Bu, unsur üzerinde hâllere ayırmadan çıkar: her iki hâl de çevirmenin tarifinden ve $\text{kâzib} \neq \text{sâdık}$ vakıasından (Mülâhaza 2.12.6) derhal görülür. Binâenaleyh (3.2.4)'ü $\text{seçici}(\mathbf{2})(\text{şâhid})$'ye ve (3.2.3)'e uygulayarak $\mathbf{0}$'ın bir unsurunu elde ederiz. ∎

**Mülâhaza 3.2.5.** Bilhassa bu, her boş olmayan tipin bir unsurunu seçen Hilbert tarzında bir "seçme âmili" bulunamayacağını gerektirir. Mesele şudur ki böyle hiçbir âmil *tabiî* olamaz, ve vahdet mütearifesi altında tipler üzerinde amel eden bütün tâbiler tekâfü'lere göre tabiî olmalıdır.

**Mülâhaza 3.2.6.** Maamâfih her Tip için $\neg\neg\neg \text{Tip} \to \neg \text{Tip}$ olduğu hâlâ doğrudur; Temrin 1.11'e bakınız.

**Netice 3.2.7.** Her $\text{Tip} : \text{Kâinat}$ için $\text{Tip} + (\neg \text{Tip})$ olması doğru değildir.

*İspat.* $\text{karar} : \prod_{\text{Tip} : \text{Kâinat}} (\text{Tip} + (\neg \text{Tip}))$ elimizde olduğunu farz edelim. O zaman $\prod_{\text{Tip} : \text{Kâinat}} (\neg\neg \text{Tip} \to \text{Tip})$ olduğunu göstereceğiz ki Kaziyye 3.2.2'yi uygulayabilelim. Binâenaleyh $\text{Tip} : \text{Kâinat}$ ve $\text{şâhid} : \neg\neg \text{Tip}$ farz edelim; Tip'in bir unsurunu inşa etmek istiyoruz.

Şimdi $\text{karar}(\text{Tip}) : \text{Tip} + (\neg \text{Tip})$'dir; binâenaleyh hâllere ayırma ile, ya bir $\text{nokta} : \text{Tip}$ için $\text{karar}(\text{Tip}) \equiv \text{sol-zerk}(\text{nokta})$, ya da bir $\text{red} : \neg \text{Tip}$ için $\text{karar}(\text{Tip}) \equiv \text{sağ-zerk}(\text{red})$ olduğunu farz edebiliriz. Birinci hâlde $\text{nokta} : \text{Tip}$ elimizdedir; ikinci hâlde ise $\text{şâhid}(\text{red}) : \mathbf{0}$ elimizdedir ve binâenaleyh istediğimiz her şeyi (meselâ Tip'i) elde edebiliriz. Binâenaleyh her iki hâlde de, istendiği gibi, Tip'in bir unsuru elimizdedir. ∎

Binâenaleyh eğer vahdet mütearifesini farz etmek (ki elbette istiyoruz) ve yine de kendimize klasik istidlal imkânını (ki o da arzu edilir) bırakmak istiyorsak, değiştirilmemiş tipler olarak kaziyyeler mebde'ini *bütün* gayr-ı sûrî riyâziyî beyanları tip nazariyesine tefsir etmek için kullanamayız; zîrâ o zaman imtinâ'-ı vasat kanunu yanlış olurdu. Maamâfih tipler olarak kaziyyeleri, birçok güzel hassası (sadelik, inşâîlik ve hesap edilebilirlik gibi) sebebiyle, bütünüyle atmak da istemeyiz. Şimdi tipler olarak kaziyyelerin bu meseleleri halleden bir tadilini münakaşa ediyoruz; 3.10. fasılda hangi mantığın ne zaman kullanılacağı suâline döneceğiz.

## 3.3 Mahz kaziyyeler

Tipler olarak kaziyyeler mantığının hem iyi hem kötü hassaları olduğunu gördük. Her ikisinin müşterek bir sebebi vardır: tipler kaziyye olarak telakkî edildiğinde, sırf doğruluk yahut yanlışlıktan fazla malûmat ihtiva edebilirler ve onlar üzerindeki bütün "mantıkî" inşalar bu ilâve malûmata riayet etmelidir. Bu, bir sıdk kıymetinden fazla hiçbir malûmat ihtiva *etmeyen* tiplere dikkatimizi hasrederek ve yalnız bunları mantıkî kaziyyeler sayarak daha âdet olan bir mantık elde edebileceğimizi telkin eder.

Böyle bir Tip tipi, eğer meskûn ise "doğru", eğer meskûniyeti bir tenâkuz doğuruyorsa (yâni $\neg \text{Tip} \equiv (\text{Tip} \to \mathbf{0})$ meskûn ise) "yanlış" olacaktır. Daha an'anevî bir mantık elde etmek için kaçınmak istediğimiz şey, bir unsurunu vermenin, sırf tipin meskûn olduğunu bilmekten fazla malûmat verdiği tipleri mantıkî kaziyyeler olarak ele almaktır. Meselâ bize $\mathbf{2}$'nin bir unsuru verilirse, $\mathbf{2}$'nin bir unsur ihtiva ettiği mahz vakıasından fazla malûmat alırız. Filhakika tam olarak *bir ikilik hane* fazla malûmat alırız: $\mathbf{2}$'nin *hangi* unsurunun bize verildiğini biliriz. Buna mukabil, bize $\mathbf{1}$'in bir unsuru verilirse, $\mathbf{1}$'in bir unsur ihtiva ettiği mahz vakıasından fazla hiçbir malûmat almayız; zîrâ $\mathbf{1}$'in herhangi iki unsuru birbirine müsâvîdir. Bu, şu tarifi telkin eder.

**Tarif 3.3.1.** Eğer her $\text{unsur}, \text{öteki} : \text{Kaziyye}$ için $\text{unsur} = \text{öteki}$ ise, **Kaziyye** tipine bir **mahz kaziyye** denir.

Dikkat edilsin ki hâlâ tip nazariyesinin *içinde* riyâziyât yaptığımız için, bu tip nazariyesinin *içinde* bir tariftir; bu da onun bir tip, yahut daha doğrusu bir tip ailesi olduğu mânâsına gelir. Hususiyle her $\text{Kaziyye} : \text{Kâinat}$ için $\text{kaziyye-mi}(\text{Kaziyye})$ tipi şöyle tarif edilir:

$$\text{kaziyye-mi}(\text{Kaziyye}) :\equiv \prod_{\text{unsur}, \text{öteki} : \text{Kaziyye}} (\text{unsur} = \text{öteki}).$$

Binâenaleyh "Kaziyye bir mahz kaziyyedir" iddiasında bulunmak, $\text{kaziyye-mi}(\text{Kaziyye})$'nin bir sâkinini, yâni Kaziyye'nin herhangi iki unsurunu bir tarîk ile bağlayan merbût bir tâbiyi göstermek demektir. Bu tâbinin ittisali yahut tabiîliği, Kaziyye'nin herhangi iki unsurunun müsâvî olmasından başka, Kaziyye'nin hiçbir yüksek tahavvül-i muttasıl da ihtiva etmemesini gerektirir.

**Yardımcı Kaziyye 3.3.2.** Eğer Kaziyye bir mahz kaziyye ve $\text{mebde'} : \text{Kaziyye}$ ise, $\text{Kaziyye} \simeq \mathbf{1}$ olur.

*İspat.* $\text{gidiş} : \text{Kaziyye} \to \mathbf{1}$ tâbisi $\text{gidiş}(\text{unsur}) :\equiv \star$ ile, $\text{dönüş} : \mathbf{1} \to \text{Kaziyye}$ tâbisi $\text{dönüş}(\text{şâhid}) :\equiv \text{mebde'}$ ile tarif edilsin. İddia, bir sonraki yardımcı kaziyyeden ve $\mathbf{1}$'in Kaziyye 2.8.1 mûcibince bir mahz kaziyye olduğu gözleminden çıkar. ∎

**Yardımcı Kaziyye 3.3.3.** Eğer Kaziyye ile Diğer-kaziyye, $\text{Kaziyye} \to \text{Diğer-kaziyye}$ ve $\text{Diğer-kaziyye} \to \text{Kaziyye}$ olacak tarzda mahz kaziyyeler ise, $\text{Kaziyye} \simeq \text{Diğer-kaziyye}$ olur.

*İspat.* $\text{gidiş} : \text{Kaziyye} \to \text{Diğer-kaziyye}$ ve $\text{dönüş} : \text{Diğer-kaziyye} \to \text{Kaziyye}$ verilmiş olsun. O zaman her $\text{unsur} : \text{Kaziyye}$ için, Kaziyye bir mahz kaziyye olduğundan, $\text{dönüş}(\text{gidiş}(\text{unsur})) = \text{unsur}$ olur. Benzer şekilde her $\text{öteki} : \text{Diğer-kaziyye}$ için, Diğer-kaziyye bir mahz kaziyye olduğundan, $\text{gidiş}(\text{dönüş}(\text{öteki})) = \text{öteki}$ olur; binâenaleyh gidiş ile dönüş şibh-i terslerdir. ∎

Yâni 1.11. fasılda va'd edildiği üzere, eğer iki mahz kaziyye mantıken müsâvî ise, onlar tekâfü' eder.

Tahavvül-i muttasıl nazariyesinde, $\mathbf{1}$'e tahavvül-i muttasıl tekâfü'ü olan bir fezâya *büzülebilir* denir. Binâenaleyh meskûn olan her mahz kaziyye büzülebilirdır (3.11. fasla da bakınız). Diğer taraftan, sâkinsiz $\mathbf{0}$ tipi de (boş yere) bir mahz kaziyyedir. Klasik riyâziyâtta, hiç değilse, bunlar yegâne iki imkândır.

Mahz kaziyyelere ayrıca (makûlî düşünülürse) *uca-tâbi nesneler*, (mecmûalar nazariyesine göre düşünülürse) *alt-tekler*, yahut *tahavvül-i muttasıl kaziyyeleri* de denir. 3.1. fasıldaki münakaşa, onlara *(−1)-tipler* de dememiz gerektiğini telkin eder; buna yedinci babda döneceğiz. "Mahz" sıfatı şunu tebarüz ettirir: her tip bir kaziyye sayılabilirse de (onu bir sâkinini vererek ispat ederiz), mahz kaziyye olan bir tip faydalı bir sûrette bir kaziyyeden *fazlası* sayılamaz: onun doğruluğunun bir şâhidinde hiçbir ilâve malûmat yoktur.

Dikkat edilsin ki bir Tip tipi, ancak ve ancak her $\text{unsur}, \text{öteki} : \text{Tip}$ için $\text{unsur} =_{\text{Tip}} \text{öteki}$ ayniyet tipi bir mahz kaziyye olduğunda bir mecmûadır. Diğer taraftan, Yardımcı Kaziyye 3.1.8'in ispatını kopyalayıp sadeleştirerek şunu elde ederiz:

**Yardımcı Kaziyye 3.3.4.** Her mahz kaziyye bir mecmûadır.

*İspat.* $\text{şâhid} : \text{kaziyye-mi}(\text{Tip})$ olduğunu farz edelim; binâenaleyh her $\text{unsur}, \text{öteki} : \text{Tip}$ için $\text{şâhid}(\text{unsur}, \text{öteki}) : \text{unsur} = \text{öteki}$ elde ederiz. $\text{unsur} : \text{Tip}$ sâbit tutulsun ve $\text{seçici}(\text{öteki}) :\equiv \text{şâhid}(\text{unsur}, \text{öteki})$ tarif edilsin. O zaman her $\text{öteki}, \text{üçüncü} : \text{Tip}$ ve $\text{tarîk} : \text{öteki} = \text{üçüncü}$ için $\text{merbût-tatbik}_{\text{seçici}}(\text{tarîk}) : \text{nakil}(\text{tarîk}, \text{seçici}(\text{öteki})) = \text{seçici}(\text{üçüncü})$ elde ederiz. Binâenaleyh ikinci babın 2.11. faslındaki, tarîk tiplerinde nakle dair netice mûcibince $\text{seçici}(\text{öteki}) \cdot \text{tarîk} = \text{seçici}(\text{üçüncü})$ elde ederiz ki bu, $\text{tarîk} = \text{seçici}(\text{öteki})^{-1} \cdot \text{seçici}(\text{üçüncü})$ demektir. Binâenaleyh her $\text{tarîk}, \text{diğer-tarîk} : \text{unsur} = \text{öteki}$ için $\text{tarîk} = \text{seçici}(\text{unsur})^{-1} \cdot \text{seçici}(\text{öteki}) = \text{diğer-tarîk}$ elde ederiz. ∎

Bilhassa bu şunu gerektirir:

**Yardımcı Kaziyye 3.3.5.** Her Tip tipi için $\text{kaziyye-mi}(\text{Tip})$ ve $\text{mecmûa-mı}(\text{Tip})$ tipleri mahz kaziyyelerdir.

*İspat.* $\text{şâhid}, \text{diğer-şâhid} : \text{kaziyye-mi}(\text{Tip})$ olduğunu farz edelim. Tâbi genişliği ile, $\text{şâhid} = \text{diğer-şâhid}$ olduğunu göstermek için her $\text{unsur}, \text{öteki} : \text{Tip}$ için $\text{şâhid}(\text{unsur}, \text{öteki}) = \text{diğer-şâhid}(\text{unsur}, \text{öteki})$ olduğunu göstermek kâfidir. Fakat $\text{şâhid}(\text{unsur}, \text{öteki})$ ile $\text{diğer-şâhid}(\text{unsur}, \text{öteki})$ ikisi de Tip'te tarîklerdir ve binâenaleyh müsâvîdir; zîrâ ya şâhid ile ya diğer-şâhid ile, Tip'in bir mahz kaziyye olduğu ve binâenaleyh Yardımcı Kaziyye 3.3.4 mûcibince bir mecmûa olduğu elimizdedir. Benzer şekilde $\text{şâhid}, \text{diğer-şâhid} : \text{mecmûa-mı}(\text{Tip})$ olduğunu farz edelim; bu, her $\text{nokta}, \text{diğer-nokta} : \text{Tip}$ ve $\text{tarîk}, \text{diğer-tarîk} : \text{nokta} = \text{diğer-nokta}$ için $\text{şâhid}(\text{nokta}, \text{diğer-nokta}, \text{tarîk}, \text{diğer-tarîk}) : \text{tarîk} = \text{diğer-tarîk}$ ve $\text{diğer-şâhid}(\text{nokta}, \text{diğer-nokta}, \text{tarîk}, \text{diğer-tarîk}) : \text{tarîk} = \text{diğer-tarîk}$ olduğunu söylemektir. Fakat o zaman Tip (ya şâhid ile ya diğer-şâhid ile) bir mecmûa ve binâenaleyh bir 1-tip olduğundan, $\text{şâhid}(\text{nokta}, \text{diğer-nokta}, \text{tarîk}, \text{diğer-tarîk}) = \text{diğer-şâhid}(\text{nokta}, \text{diğer-nokta}, \text{tarîk}, \text{diğer-tarîk})$ çıkar; binâenaleyh tâbi genişliği ile $\text{şâhid} = \text{diğer-şâhid}$ olur. ∎

Şimdiye kadar bir misal daha gördük: 2.4. fasıldaki (iii) şartı, her tâbi için $\text{tekâfü'-mü}(\text{tâbi})$ tipinin bir mahz kaziyye olması lâzım geldiğini ileri sürer.

## 3.4 Klasik ve hadsî mantık

Mahz kaziyye mefhûmu elde iken, tahavvül-i muttasıl tip nazariyesinde **imtinâ'-ı vasat kanunu**nun doğru ifadesini şimdi verebiliriz:

$$\text{İmtinâ'-ı-vasat} :\equiv \prod_{\text{Tip} : \text{Kâinat}} \Big(\text{kaziyye-mi}(\text{Tip}) \to (\text{Tip} + \neg \text{Tip})\Big). \tag{3.4.1}$$

Benzer şekilde **çift nefy kanunu** şudur:

$$\prod_{\text{Tip} : \text{Kâinat}} \Big(\text{kaziyye-mi}(\text{Tip}) \to (\neg\neg \text{Tip} \to \text{Tip})\Big). \tag{3.4.2}$$

İkisinin birbirine müsâvî olduğu da kolayca görülür (Temrin 3.18'e bakınız); binâenaleyh bundan sonra umûmiyetle yalnız İmtinâ'-ı-vasat'ten bahsedeceğiz.

İmtinâ'-ı-vasat'in bu ifadesi, $\mathbf{2}$ bir mahz kaziyye olmadığı için, Kaziyye 3.2.2 ile Netice 3.2.7'nin "mugalatalarından" kaçınır. Onu daha umûmî tipler olarak kaziyyeler ifadesinden ayırt etmek için sonrakinin adını değiştiriyoruz:

$$\text{İmtinâ'-ı-vasat}_{\infty} :\equiv \prod_{\text{Tip} : \text{Kâinat}} (\text{Tip} + \neg \text{Tip}).$$

Tebarüz ettirmek için doğru şekil (3.4.1), $\text{İmtinâ'-ı-vasat}_{-1}$ ile gösterilebilir; Temrin 7.7'ye de bakınız. İmtinâ'-ı-vasat birinci babda tarif edilen esas tip nazariyesinin bir neticesi değilse de, (nihâyetsiz mukabilinin aksine) tenâkuz doğurmaksızın bir mütearife olarak farz edilebilir. Meselâ onu 10.4. fasılda farz edeceğiz.

Maamâfih İmtinâ'-ı-vasat'i kullanmadan ne kadar ileri gidebildiğimiz şaşırtıcı olabilir. Çok defa bir tarifin yahut kaziyyenin basit bir yeniden ifadesi, imtinâ'-ı vasata başvurmaktan kaçınmamıza imkân verir. Bu bazen biraz alışmayı gerektirirse de, çok defa zahmetine değer ve daha zarif ve daha umûmî ispatlarla neticelenir. Bunun faydalarından bazılarını medhalde münakaşa ettik.

Meselâ klasik riyâziyâtta çift nefyler sık sık lüzumsuz yere kullanılır. Pek basit bir misal, bir Tip mecmûasının "boş olmadığı" yolundaki yaygın farzdır ki bu, lafzen Tip'in *hiçbir* unsur ihtiva etmediğinin doğru *olmadığı* mânâsına gelir. Hemen daima asıl kastedilen, Tip'in hiç değilse bir unsur ihtiva *ettiği* yolundaki müsbet iddiadır; ve çift nefyi kaldırarak beyanı İmtinâ'-ı-vasat'e daha az bağlı kılarız. Hatırlansın ki Tip'in kendisini bir kaziyye olarak ileri sürdüğümüzde (yâni Tip'in, umûmiyetle isimsiz, bir unsurunu inşa ettiğimizde) Tip tipinin *meskûn* olduğunu söyleriz. Binâenaleyh klasik bir ispatı inşâî mantığa tercüme ederken çok defa "boş olmayan" kelimesini "meskûn" ile değiştiririz (bazen bunun yerine "mahzen meskûn" ile değiştirmemiz lâzım gelse de; 3.7. fasla bakınız).

Benzer şekilde, klasik riyâziyâtta lüzumsuz yere hulf ile ispatlar bulmak nâdir değildir. Elbette hulf ile ispatın klasik şekli çift nefy kanunu yoluyla ilerler: $\neg \text{Tip}$'i farz eder ve bir tenâkuz istihrac ederiz, böylece $\neg\neg \text{Tip}$'yi çıkarırız ve böylece çift nefy ile Tip'i elde ederiz. Maamâfih çok defa $\neg \text{Tip}$'den bir tenâkuzun istihracı, İmtinâ'-ı-vasat'e ihtiyaçtan kaçınarak, Tip'in doğrudan bir ispatını verecek şekilde biraz yeniden ifade edilebilir.

Şunu kaydetmek de mühimdir ki eğer gaye bir *nefy*i ispat etmekse, o zaman "hulf ile ispat" İmtinâ'-ı-vasat'i ihtiva etmez. Filhakika $\neg \text{Tip}$ tarif mûcibince $\text{Tip} \to \mathbf{0}$ tipi olduğundan, tarif mûcibince $\neg \text{Tip}$'i ispat etmek, Tip farzı altında bir tenâkuzu ($\mathbf{0}$'ı) ispat etmektir. Benzer şekilde çift nefy kanunu nefy edilmiş kaziyyeler için muteberdir: $\neg\neg\neg \text{Tip} \to \neg \text{Tip}$. Mümâreseyle, nefy edilmiş ve nefy edilmemiş kaziyyeleri daha dikkatli ayırt etmeyi ve İmtinâ'-ı-vasat'in ne zaman kullanılıp ne zaman kullanılmadığını fark etmeyi öğrenir.

Binâenaleyh sathî olarak göründüğünün aksine, riyâziyâtı "inşâî olarak" yapmak umûmiyetle mühim kaziyyelerden vazgeçmeyi değil, bilakis mühim kaziyyeleri inşâî olarak ispat edilebilir kılacak tarzda tarifleri ifade etmenin en iyi yolunu bulmayı ihtiva eder. Yâni bir mevzûu ilk tetkik ederken İmtinâ'-ı-vasat'i serbestçe kullanabiliriz; fakat o mevzû daha iyi anlaşıldıktan sonra, onun tariflerini ve ispatlarını o mütearifeden kaçınacak tarzda inceltmeyi ümit edebiliriz. Bu türlü gözlem, vahdetun ve yüksek istikrâî tiplerin kuvvetli aletlerinin, an'anevî olarak klasik istidlal gerektirecek birçok meseleye inşâî olarak hücum etmemize imkân verdiği *tahavvül-i muttasıl* tip nazariyesinde daha da barizdir. Kitabın ikinci kısmında bunun birkaç misalini göreceğiz.

Şunu zikretmek de değer ki inşâî riyâziyâtta bile imtinâ'-ı vasat kanunu *bazı* kaziyyeler için muteber olabilir. Böyle kaziyyelere an'anevî olarak verilen isim *karar verilebilir*dir.

**Tarif 3.4.3.**

1. Eğer $\text{Tip} + \neg \text{Tip}$ ise, Tip tipine **karar verilebilir** denir.
2. Benzer şekilde, eğer $\prod_{\text{nokta} : \text{Tip}} (\text{Lif}(\text{nokta}) + \neg \text{Lif}(\text{nokta}))$ ise, $\text{Lif} : \text{Tip} \to \text{Kâinat}$ tip ailesi **karar verilebilir**dir.
3. Bilhassa, eğer $\prod_{\text{nokta}, \text{diğer-nokta} : \text{Tip}} ((\text{nokta} = \text{diğer-nokta}) + \neg(\text{nokta} = \text{diğer-nokta}))$ ise, Tip **karar verilebilir müsâvâta** sahiptir.

Binâenaleyh İmtinâ'-ı-vasat, tam olarak bütün mahz kaziyyelerin karar verilebilir olduğu ve binâenaleyh mahz kaziyyelerin bütün ailelerinin de öyle olduğu beyanıdır. Bilhassa İmtinâ'-ı-vasat, bütün mecmûaların (3.1. fasıldaki mânâda) karar verilebilir müsâvâta sahip olmasını gerektirir. Bu mânâda karar verilebilir müsâvâta sahip olmak pek kuvvetlidir; Kaziyye 7.2.5'e bakınız.

## 3.5 Alt mecmûalar ve kaziyyevî yeniden boyutlandırma

Mahz kaziyyelerin faydasının başka bir misali olarak, alt mecmûaları (ve daha umûmî olarak alt tipleri) münakaşa ediyoruz. $\text{Kaziyye} : \text{Tip} \to \text{Kâinat}$'ın, her $\text{Kaziyye}(\text{unsur})$ tipi bir kaziyye sayılan bir tip ailesi olduğunu farz edelim. O zaman Kaziyye'nin kendisi Tip üzerinde bir *mahmûl*, yahut Tip'in unsurlarının bir *hassası*dır.

Mecmûalar nazariyesinde, bir Tip mecmûası üzerinde bir Kaziyye mahmûlümüz olduğunda her defasında $\{\text{unsur} \in \text{Tip} \mid \text{Kaziyye}(\text{unsur})\}$ alt mecmûasını teşkil edebiliriz. 1.11. fasılda kısaca zikredildiği üzere, tip nazariyesindeki apaçık benzeri $\sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$ Sigma tipidir. $\sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$'in bir sâkini elbette bir $(\text{unsur}, \text{ispat})$ çiftidir ki burada $\text{unsur} : \text{Tip}$ ve ispat, $\text{Kaziyye}(\text{unsur})$'in bir ispatıdır. Maamâfih umûmî Kaziyye için, eğer $\text{Kaziyye}(\text{nokta})$ kaziyyesinin birden fazla farklı ispatı varsa, bir $\text{nokta} : \text{Tip}$ unsuru $\sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$'in birden fazla farklı unsurunu doğurabilir. Bu, bir alt mecmûanın âdet olan hadsine aykırıdır. Fakat eğer Kaziyye bir *mahz* kaziyye ise, bu vuku bulamaz.

**Yardımcı Kaziyye 3.5.1.** $\text{Kaziyye} : \text{Tip} \to \text{Kâinat}$'ın, her $\text{unsur} : \text{Tip}$ için $\text{Kaziyye}(\text{unsur})$ bir mahz kaziyye olacak tarzda bir tip ailesi olduğunu farz edelim. Eğer $\text{şâhid}, \text{diğer-şâhid} : \sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$, $\text{birinci-izdüşüm}(\text{şâhid}) = \text{birinci-izdüşüm}(\text{diğer-şâhid})$ olacak tarzda ise, $\text{şâhid} = \text{diğer-şâhid}$ olur.

*İspat.* $\text{tarîk} : \text{birinci-izdüşüm}(\text{şâhid}) = \text{birinci-izdüşüm}(\text{diğer-şâhid})$ olduğunu farz edelim. Kaziyye 2.7.2 mûcibince, $\text{şâhid} = \text{diğer-şâhid}$ olduğunu göstermek için $\text{nakil}(\text{tarîk}, \text{ikinci-izdüşüm}(\text{şâhid})) = \text{ikinci-izdüşüm}(\text{diğer-şâhid})$ olduğunu göstermek kâfidir. Fakat $\text{nakil}(\text{tarîk}, \text{ikinci-izdüşüm}(\text{şâhid}))$ ile $\text{ikinci-izdüşüm}(\text{diğer-şâhid})$ ikisi de bir mahz kaziyye olan $\text{Kaziyye}(\text{birinci-izdüşüm}(\text{diğer-şâhid}))$'in unsurlarıdır; binâenaleyh müsâvîdirler. ∎

Meselâ hatırlansın ki 2.4. fasılda şunu tarif etmiştik:

$$(\text{Tip} \simeq \text{Diğer-tip}) :\equiv \sum_{\text{tâbi} : \text{Tip} \to \text{Diğer-tip}} \text{tekâfü'-mü}(\text{tâbi}),$$

ki burada her $\text{tekâfü'-mü}(\text{tâbi})$ tipinin bir mahz kaziyye olması farz edilmişti. Buradan çıkar ki eğer iki tekâfü'ün temelindeki tâbiler müsâvî ise, onlar tekâfü'ler olarak da müsâvîdir.

Bundan böyle, eğer $\text{Kaziyye} : \text{Tip} \to \text{Kâinat}$ mahz kaziyyelerden bir aile ise (yâni her $\text{Kaziyye}(\text{unsur})$ bir mahz kaziyye ise),

$$\{\text{unsur} : \text{Tip} \mid \text{Kaziyye}(\text{unsur})\} \tag{3.5.2}$$

ifadesini $\sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$ için bir başka gösteriş olarak yazabiliriz. (Bu gösterişi keyfî Kaziyye için de kullanmamak için hiçbir fennî sebep yoktur; fakat böyle bir kullanış, kastedilmemiş çağrışımlar sebebiyle karışıklık doğurabilirdi.) Eğer Tip bir mecmûa ise, (3.5.2)'ye Tip'in bir **alt mecmûası** deriz; umûmî Tip için ona bir **alt tip** diyebiliriz. Kaziyye'nin kendisinden de Tip'in bir *alt mecmûası* yahut *alt tipi* diye bahsedebiliriz; bu aslında daha doğrudur, zîrâ (3.5.2) tipi tek başına Tip ile olan münasebetini hatırlamaz.

Böyle bir Kaziyye ve $\text{nokta} : \text{Tip}$ verilince, $\text{Kaziyye}(\text{nokta})$ mahz kaziyyesinden bahsetmek için $\text{nokta} \in \text{Kaziyye}$ yahut $\text{nokta} \in \{\text{unsur} : \text{Tip} \mid \text{Kaziyye}(\text{unsur})\}$ yazabiliriz. Eğer o sâdık ise, noktanın Kaziyye'nin bir **mensubu** olduğunu söyleyebiliriz. Benzer şekilde, eğer $\{\text{unsur} : \text{Tip} \mid \text{Diğer-kaziyye}(\text{unsur})\}$ Tip'in başka bir alt mecmûası ise, $\prod_{\text{unsur} : \text{Tip}} (\text{Kaziyye}(\text{unsur}) \to \text{Diğer-kaziyye}(\text{unsur}))$ elimizde olduğunda, Kaziyye'nin Diğer-kaziyye'de **ihtiva edildiğini** söyler ve $\text{Kaziyye} \subseteq \text{Diğer-kaziyye}$ yazarız.

Alt tiplerin daha başka misalleri olarak, bir Kâinat'ta mecmûaların ve mahz kaziyyelerin "alt kâinatlarını" tarif edebiliriz:

$$\text{Mecmûa}_{\text{Kâinat}} :\equiv \{\text{Tip} : \text{Kâinat} \mid \text{mecmûa-mı}(\text{Tip})\},$$
$$\text{Kaziyye}_{\text{Kâinat}} :\equiv \{\text{Tip} : \text{Kâinat} \mid \text{kaziyye-mi}(\text{Tip})\}.$$

$\text{Mecmûa}_{\text{Kâinat}}$'ın bir unsuru, $\text{şâhid} : \text{mecmûa-mı}(\text{Tip})$ delili ile beraber bir $\text{Tip} : \text{Kâinat}$ tipidir; ve $\text{Kaziyye}_{\text{Kâinat}}$ için de benzer şekilde. Yardımcı Kaziyye 3.5.1, $(\text{Tip}, \text{şâhid}) =_{\text{Mecmûa}_{\text{Kâinat}}} (\text{Diğer-tip}, \text{diğer-şâhid})$'in $\text{Tip} =_{\text{Kâinat}} \text{Diğer-tip}$'e (ve binâenaleyh $\text{Tip} \simeq \text{Diğer-tip}$'e) tekâfü' etmesini gerektirir. Binâenaleyh sık sık gösterişi sû-i istimal edip $(\text{Tip}, \text{şâhid}) : \text{Mecmûa}_{\text{Kâinat}}$ yerine sadece $\text{Tip} : \text{Mecmûa}_{\text{Kâinat}}$ yazacağız. Söz konusu kâinatı belirtmeye ihtiyaç yoksa, Kâinat alt işaretini de düşürebiliriz.

Hatırlansın ki herhangi iki $\text{Kâinat}_{\text{derece}}$ ve $\text{Kâinat}_{\text{derece}+1}$ kâinatı için, eğer $\text{Tip} : \text{Kâinat}_{\text{derece}}$ ise, aynı zamanda $\text{Tip} : \text{Kâinat}_{\text{derece}+1}$'dir. Binâenaleyh her $(\text{Tip}, \text{şâhid}) : \text{Mecmûa}_{\text{Kâinat}_{\text{derece}}}$ için aynı zamanda $(\text{Tip}, \text{şâhid}) : \text{Mecmûa}_{\text{Kâinat}_{\text{derece}+1}}$ elde ederiz, ve $\text{Kaziyye}_{\text{Kâinat}_{\text{derece}}}$ için de benzer şekilde; bu da tabiî tatbikler verir:

$$\text{Mecmûa}_{\text{Kâinat}_{\text{derece}}} \to \text{Mecmûa}_{\text{Kâinat}_{\text{derece}+1}}, \tag{3.5.3}$$
$$\text{Kaziyye}_{\text{Kâinat}_{\text{derece}}} \to \text{Kaziyye}_{\text{Kâinat}_{\text{derece}+1}}. \tag{3.5.4}$$

(3.5.3) tatbiki bir tekâfü' olamaz, zîrâ o zaman Cantor'un mecmûalar nazariyesinden âşinâ olduğumuz kendine atıf mugalatalarını yeniden üretebilirdik. Maamâfih (3.5.4), şimdiye kadar takdim ettiğimiz tip nazariyesinde kendiliğinden bir tekâfü' olmasa da, öyle olduğunu farz etmek tenâkuz doğurmaz. Yâni tip nazariyesine şu mütearifeyi eklemeyi mülâhaza edebiliriz.

**Mütearife 3.5.5 (Kaziyyevî yeniden boyutlandırma).** $\text{Kaziyye}_{\text{Kâinat}_{\text{derece}}} \to \text{Kaziyye}_{\text{Kâinat}_{\text{derece}+1}}$ tatbiki bir tekâfü'dür.

Bu mütearifeye **kaziyyevî yeniden boyutlandırma** deriz; zîrâ bu, $\text{Kâinat}_{\text{derece}+1}$ kâinatındaki her mahz kaziyyenin daha küçük $\text{Kâinat}_{\text{derece}}$ kâinatında tekâfü' eden birine "yeniden boyutlandırılabileceği" mânâsına gelir. Eğer $\text{Kâinat}_{\text{derece}+1}$ İmtinâ'-ı-vasat'i sağlıyorsa, bu kendiliğinden çıkar (Temrin 3.10'a bakınız). Bu mütearifeyi umûmiyetle farz etmeyeceğiz; fakat bazı yerlerde onu sarih bir farz olarak kullanacağız. O, mahz kaziyyeler için bir *gayr-ı tahmîlîlik* şeklidir ve onun kullanılmasından kaçınarak tip nazariyesinin *tahmîlî* kaldığı söylenir.

Tatbikatta en sık istediğimiz şey biraz farklı bir beyandır: mülâhaza edilen bir Kâinat'ın "bütün mahz kaziyyeleri sınıflandıran" bir tip ihtiva etmesi. Başka sözlerle, mahz kaziyyelerin, her mahz kaziyyeyi tekâfü' kaydıyla ihtiva eden, Hükümler ile fihristlenmiş bir ailesi ile beraber bir $\text{Hükümler} : \text{Kâinat}$ tipi istiyoruz. Bu beyan, eğer Kâinat en küçük $\text{Kâinat}_0$ kâinatı değilse, yukarıda ifade edildiği şekliyle kaziyyevî yeniden boyutlandırmanden çıkar; zîrâ o zaman $\text{Hükümler} :\equiv \text{Kaziyye}_{\text{Kâinat}_0}$ tarif edebiliriz.

Gayr-ı mahmûlîliğin bir kullanışı kuvvet mecmûalarını tarif etmektir. Bir Tip mecmûasının **kuvvet mecmûası**nı $\text{Tip} \to \text{Kaziyye}_{\text{Kâinat}}$ olarak tarif etmek tabiîdir; fakat gayr-ı tahmîlîliğin yokluğunda bu tarif (tekâfü' kaydıyla bile) Kâinat'ın seçilmesine bağlıdır. Fakat kaziyyevî yeniden boyutlandırma ile kuvvet mecmûasını şöyle tarif edebiliriz:

$$\text{Kuvvet}(\text{Tip}) :\equiv (\text{Tip} \to \text{Hükümler}),$$

ki o zaman bu Kâinat'tan müstakildir. W-tiplerine dair ilgili kısma da bakınız.

## 3.6 Mahz kaziyyelerin mantığı

1.1. fasılda zikretmiştik ki, yalnız bir temel mefhûmu (tipleri) olan tip nazariyesinin aksine, mecmûalar nazariyesi esaslarının iki temel mefhûmu vardır: mecmûalar ve kaziyyeler. Binâenaleyh klasik bir riyâziyeci bu iki nevi nesneyi ayrı ayrı işlemeye alışkındır.

Tip nazariyesinde de buna benzer bir ikiliği yeniden elde etmek mümkündür; burada mecmûalar nazariyesindeki kaziyyelerin rolünü, *mahz* kaziyye olan tipler (ve tip aileleri) oynar. Birçok hâlde mantıkî rabıtalar ve sûrlar bu mantıkta, tekabül eden tip kurucusunu sadece mahz kaziyyelere hasretmek sûretiyle temsil edilebilir. Elbette bu, söz konusu tip kurucusunun mahz kaziyyeleri muhafaza ettiğini bilmeyi gerektirir.

**Misal 3.6.1.** Eğer Kaziyye ile Diğer-kaziyye mahz kaziyyeler ise, $\text{Kaziyye} \times \text{Diğer-kaziyye}$ de öyledir. Bunu, hâsıl-ı zarblardaki tarîklerin tavsifini kullanarak, tıpkı Misal 3.1.5 gibi, fakat ondan daha basit olarak göstermek kolaydır. Binâenaleyh "ve" rabıtası mahz kaziyyeleri muhafaza eder.

**Misal 3.6.2.** Eğer Tip herhangi bir tip ise ve $\text{Kaziyye} : \text{Tip} \to \text{Kâinat}$ öyledir ki her $\text{unsur} : \text{Tip}$ için $\text{Kaziyye}(\text{unsur})$ tipi bir mahz kaziyyedir, o zaman $\prod_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$ bir mahz kaziyyedir. İspat tıpkı Misal 3.1.6 gibidir, fakat ondan daha basittir: $\text{tâbi}, \text{diğer-tâbi} : \prod_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$ verilince, her $\text{unsur} : \text{Tip}$ için, $\text{Kaziyye}(\text{unsur})$ bir mahz kaziyye olduğundan, $\text{tâbi}(\text{unsur}) = \text{diğer-tâbi}(\text{unsur})$ elde ederiz. Fakat o zaman tâbi genişliği ile $\text{tâbi} = \text{diğer-tâbi}$ elde ederiz.

Bilhassa, eğer Kaziyye bir mahz kaziyye ise, Tip ne olursa olsun $\text{Tip} \to \text{Kaziyye}$ de öyledir. Daha da hususî olarak, $\mathbf{0}$ bir mahz kaziyye olduğundan, $\neg \text{Tip} \equiv (\text{Tip} \to \mathbf{0})$ da öyledir. Binâenaleyh "gerektirir" ve "değil" rabıtaları, "her biri için" sûru gibi, mahz kaziyyeleri muhafaza eder.

Diğer taraftan, bazı tip kurucuları mahz kaziyyeleri muhafaza etmez. Kaziyye ile Diğer-kaziyye mahz kaziyyeler olsa bile, $\text{Kaziyye} + \text{Diğer-kaziyye}$ umûmiyetle öyle olmayacaktır. Meselâ $\mathbf{1}$ bir mahz kaziyyedir, fakat $\mathbf{2} = \mathbf{1} + \mathbf{1}$ değildir. Mantıkî olarak söylenirse, $\text{Kaziyye} + \text{Diğer-kaziyye}$ "sırf inşâî" bir nevi "veya"dır: onun bir şâhidi, *hangi* şıkkın doğru olduğuna dair ilâve malûmatı ihtiva eder. Bu bazen pek faydalıdır; fakat mahz kaziyyeleri muhafaza eden daha klasik bir nevi "veya" istiyorsak, bu ilâve malûmatı unutarak bu tipi bir mahz kaziyyeye "kat' etmenin" bir yoluna muhtacız.

Aynı mesele, Tip keyfî bir tip olmak üzere, $\sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$ Sigma tipinde de zuhur eder. Bu, "$\text{Kaziyye}(\text{unsur})$ olacak tarzda bir $\text{unsur} : \text{Tip}$ vardır" sözünün, unsur şâhidini hatırlayan sırf inşâî bir tefsiridir; binâenaleyh her $\text{Kaziyye}(\text{unsur})$ tipi bir mahz kaziyye olsa bile, umûmiyetle kendisi bir mahz kaziyye değildir. (Hatırlansın ki 3.5. fasılda $\sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$'in "Tip'in $\text{Kaziyye}(\text{unsur})$ olacak tarzdaki unsurlarının alt mecmûası" olarak da telakkî edilebileceğini müşahede etmiştik.)

## 3.7 Kaziyyevî kat'

*Kaziyyevî kat'*, ki ona *(−1)-kat'ı*, *köşeli parantez tipi* yahut *ezme tipi* de denir, bir tipi bir mahz kaziyyeye kadar "ezen" yahut "kat' eden", o tipin sâkinlerinde vücutlarından başka ihtiva edilen bütün malûmatı unutan, ilâve bir tip kurucusudur.

Daha dakik olarak, her Tip tipi için bir $\lVert \text{Tip} \rVert$ tipi vardır. Onun iki kurucusu vardır:

- Her $\text{nokta} : \text{Tip}$ için $\lvert \text{nokta} \rvert : \lVert \text{Tip} \rVert$ elde ederiz.
- Her $\text{unsur}, \text{öteki} : \lVert \text{Tip} \rVert$ için $\text{unsur} = \text{öteki}$ elde ederiz.

Birinci kurucu şu mânâya gelir: eğer Tip meskûn ise, $\lVert \text{Tip} \rVert$ de öyledir. İkincisi $\lVert \text{Tip} \rVert$'nin bir mahz kaziyye olmasını temin eder; umûmiyetle bu vakıanın şâhidini isimsiz bırakırız.

$\lVert \text{Tip} \rVert$'nin rücû' prensibi şunu söyler:

- Eğer Diğer-tip bir mahz kaziyye ise ve elimizde $\text{tâbi} : \text{Tip} \to \text{Diğer-tip}$ varsa, o zaman her $\text{nokta} : \text{Tip}$ için $\text{diğer-tâbi}(\lvert \text{nokta} \rvert) \equiv \text{tâbi}(\text{nokta})$ olacak tarzda, bundan doğan bir $\text{diğer-tâbi} : \lVert \text{Tip} \rVert \to \text{Diğer-tip}$ vardır.

Başka sözlerle, Tip'ten (yâni onun meskûn oluşundan) çıkan her mahz kaziyye, zaten $\lVert \text{Tip} \rVert$'den de çıkar. Binâenaleyh $\lVert \text{Tip} \rVert$, bir mahz kaziyye olarak, Tip'in meskûn oluşundan fazla malûmat ihtiva etmez. ($\lVert \text{Tip} \rVert$ için bir istikrâ prensibi de vardır; fakat o pek faydalı değildir; Temrin 3.17'ye bakınız.)

Temrin 3.14'te, Temrin 3.15'te ve 6.9. fasılda $\lVert \text{Tip} \rVert$'yi daha umûmî şeyler cinsinden inşa etmenin bazı yollarını tarif edeceğiz. Şimdilik onu sadece birinci babdakilerin yanında ilâve bir kaide olarak farz ediyoruz.

Kaziyyevî kat' ile "mahz kaziyyelerin mantığını" infisâli (veya'yı) ve vücûdî sûru kapsayacak şekilde genişletebiliriz. Hususiyle $\lVert \text{Tip} + \text{Diğer-tip} \rVert$, "Tip veya Diğer-tip"in, hangi şıkkın doğru olduğu malûmatını "hatırlamayan", mahz kaziyyevî bir şeklidir.

Kat'ın rücû' prensibi gerektirir ki, *bir mahz kaziyyeyi ispat etmeye çalışırken* $\lVert \text{Tip} + \text{Diğer-tip} \rVert$ üzerinde hâlâ hâllere ayırma yapabiliriz. Yâni elimizde bir $\text{şâhid} : \lVert \text{Tip} + \text{Diğer-tip} \rVert$ farzı bulunduğunu ve bir Kaziyye mahz kaziyyesini ispat etmeye çalıştığımızı farz edelim. Başka sözlerle, $\lVert \text{Tip} + \text{Diğer-tip} \rVert \to \text{Kaziyye}$'nin bir unsurunu tarif etmeye çalışıyoruz. Kaziyye bir mahz kaziyye olduğundan, kaziyyevî kat'ın rücû' prensibi mûcibince bir $\text{Tip} + \text{Diğer-tip} \to \text{Kaziyye}$ tâbisi inşa etmek kâfidir. Fakat şimdi $\text{Tip} + \text{Diğer-tip}$ üzerinde hâllere ayırmayı kullanabiliriz.

Benzer şekilde, bir $\text{Kaziyye} : \text{Tip} \to \text{Kâinat}$ tip ailesi için, "$\text{Kaziyye}(\text{unsur})$ olacak tarzda bir $\text{unsur} : \text{Tip}$ vardır"ın mahz kaziyyevî bir şekli olan $\lVert \sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur}) \rVert$'i mülâhaza edebiliriz. İnfisâlde olduğu gibi, kat'ın ve Sigma tiplerinin istikrâ prensiplerini birleştirerek, eğer elimizde $\lVert \sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur}) \rVert$ tipinden bir farz varsa, *bir mahz kaziyyeyi ispat etmeye çalışırken* yeni $\text{unsur} : \text{Tip}$ ve $\text{öteki} : \text{Kaziyye}(\text{unsur})$ farzlarını idhâl edebiliriz. Başka sözlerle, eğer $\text{Kaziyye}(\text{unsur})$ olacak tarzda bir $\text{unsur} : \text{Tip}$ bulunduğunu biliyor, fakat elimizde böyle muayyen bir unsur bulunmuyorsa, unsurun muayyen kıymetine bağlı olabilecek hiçbir şeyi inşa etmeye çalışmadığımız müddetçe böyle bir unsuru kullanmakta serbestiz. Varış sahasının bir mahz kaziyye olmasını istemek, neticenin şâhide bağlı olmadığını ifade eder; zîrâ böyle bir tipin bütün muhtemel sâkinleri müsâvî olmalıdır.

Mecmûa mertebesindeki riyâziyâtın maksatları için, ki onuncu ve on birinci bablarda çoğunlukla mecmûalar ve mahz kaziyyelerle uğraşacağız, an'anevî mantıkî işaretleri yalnız "kaziyyevî kat'lı mantığa" atıf için kullanmak elverişlidir.

**Tarif 3.7.1.** Kaziyye ile Diğer-kaziyye mahz kaziyyeleri (yahut onların ailelerini) göstermek üzere, **an'anevî mantıkî işareti** kat'ı kullanarak şöyle tarif ederiz:

$$\top :\equiv \mathbf{1}$$
$$\bot :\equiv \mathbf{0}$$
$$\text{Kaziyye} \land \text{Diğer-kaziyye} :\equiv \text{Kaziyye} \times \text{Diğer-kaziyye}$$
$$\text{Kaziyye} \Rightarrow \text{Diğer-kaziyye} :\equiv \text{Kaziyye} \to \text{Diğer-kaziyye}$$
$$\text{Kaziyye} \Leftrightarrow \text{Diğer-kaziyye} :\equiv \text{Kaziyye} = \text{Diğer-kaziyye}$$
$$\neg \text{Kaziyye} :\equiv \text{Kaziyye} \to \mathbf{0}$$
$$\text{Kaziyye} \lor \text{Diğer-kaziyye} :\equiv \lVert \text{Kaziyye} + \text{Diğer-kaziyye} \rVert$$
$$\forall (\text{unsur} : \text{Tip}).\, \text{Kaziyye}(\text{unsur}) :\equiv \prod_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$$
$$\exists (\text{unsur} : \text{Tip}).\, \text{Kaziyye}(\text{unsur}) :\equiv \Big\lVert \sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur}) \Big\rVert$$

$\land$ ve $\lor$ işaretleri, tahavvül-i muttasıl nazariyesinde, altıncı babda tanıtacağımız noktalı fezâların ezik hâsıl-ı zarbı ve kaması için de kullanılır. Bu, fennî olarak bir iştibah ihtimali doğurur; fakat umûmiyetle hiçbir karışıklık hâsıl olmayacaktır.

Benzer şekilde, 3.5. fasıldaki gibi alt mecmûaları münakaşa ederken, takātu', ictimâ' ve mütemmim için an'anevî işaretleri kullanabiliriz:

$$\{\text{unsur} : \text{Tip} \mid \text{Kaziyye}(\text{unsur})\} \cap \{\text{unsur} : \text{Tip} \mid \text{Diğer-kaziyye}(\text{unsur})\} :\equiv \{\text{unsur} : \text{Tip} \mid \text{Kaziyye}(\text{unsur}) \land \text{Diğer-kaziyye}(\text{unsur})\},$$
$$\{\text{unsur} : \text{Tip} \mid \text{Kaziyye}(\text{unsur})\} \cup \{\text{unsur} : \text{Tip} \mid \text{Diğer-kaziyye}(\text{unsur})\} :\equiv \{\text{unsur} : \text{Tip} \mid \text{Kaziyye}(\text{unsur}) \lor \text{Diğer-kaziyye}(\text{unsur})\},$$
$$\text{Tip} \setminus \{\text{unsur} : \text{Tip} \mid \text{Kaziyye}(\text{unsur})\} :\equiv \{\text{unsur} : \text{Tip} \mid \neg \text{Kaziyye}(\text{unsur})\}.$$

Elbette İmtinâ'-ı-vasat'ın yokluğunda sonrakiler âdet olan mânâda "mütemmim" değildir: Tip'in her Alt alt mecmûası için $\text{Alt} \cup (\text{Tip} \setminus \text{Alt}) = \text{Tip}$ elimizde olmayabilir.

## 3.8 İhtiyar mütearifesi

Artık ihtiyar mütearifesini tahavvül-i muttasıl tip nazariyesinde doğru olarak ifade edebiliriz. Bir Esas tipi ve

$$\text{Lif} : \text{Esas} \to \text{Kâinat} \qquad\text{ve}\qquad \text{Kaziyye} : \prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur}) \to \text{Kâinat}$$

tip aileleri farz edelim; ayrıca şunları da farz edelim:

- Esas bir mecmûadır,
- her $\text{unsur} : \text{Esas}$ için $\text{Lif}(\text{unsur})$ bir mecmûadır, ve
- her $\text{unsur} : \text{Esas}$ ve $\text{nokta} : \text{Lif}(\text{unsur})$ için $\text{Kaziyye}(\text{unsur}, \text{nokta})$ bir mahz kaziyyedir.

**İhtiyar mütearifesi** İhtiyar, bu farzlar altında şunu ileri sürer:

$$\Big(\prod_{\text{unsur} : \text{Esas}} \Big\lVert \sum_{\text{nokta} : \text{Lif}(\text{unsur})} \text{Kaziyye}(\text{unsur}, \text{nokta}) \Big\rVert\Big) \to \Big\lVert \sum_{\text{seçici} : \prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur})} \; \prod_{\text{unsur} : \text{Esas}} \text{Kaziyye}(\text{unsur}, \text{seçici}(\text{unsur})) \Big\rVert. \tag{3.8.1}$$

Elbette bu, "$\text{Lif}(\text{unsur})$ olacak tarzda $\text{unsur} : \text{Tip}$ vardır" sözünü $\lVert \sum_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur}) \rVert$ diye okuduğumuz takdirde (3.2.1)'in doğrudan bir tercümesidir; binâenaleyh beyanı âşinâ mantıkî işaretle şöyle de yazabilirdik:

$$\Big(\forall (\text{unsur} : \text{Esas}).\, \exists (\text{nokta} : \text{Lif}(\text{unsur})).\, \text{Kaziyye}(\text{unsur}, \text{nokta})\Big) \Rightarrow \Big(\exists \big(\text{seçici} : \textstyle\prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur})\big).\, \forall (\text{unsur} : \text{Esas}).\, \text{Kaziyye}(\text{unsur}, \text{seçici}(\text{unsur}))\Big).$$

Bilhassa dikkat edilsin ki kaziyyevî kat' iki defa görünür. Kalkış sahasındaki kat' şu mânâya gelir: her unsur için $\text{Kaziyye}(\text{unsur}, \text{nokta})$ olacak tarzda bir $\text{nokta} : \text{Lif}(\text{unsur})$ bulunduğunu farz ederiz, fakat bu kıymetler bilinen hiçbir tarzda seçilmiş yahut tayin edilmiş değildir. Varış sahasındaki kat' ise şu mânâya gelir: bir seçici tâbisi bulunduğu neticesine varırız, fakat bu tâbi bilinen hiçbir tarzda tayin edilmiş yahut belirtilmiş değildir.

Filhakika Kaziyye 2.15.7 sebebiyle bu mütearife daha basit bir şekilde de ifade edilebilir.

**Yardımcı Kaziyye 3.8.2.** İhtiyar mütearifesi (3.8.1), her Esas mecmûası ve her $\text{Lif}(\text{unsur})$'i bir mecmûa olan her $\text{Lif} : \text{Esas} \to \text{Kâinat}$ için

$$\Big(\prod_{\text{unsur} : \text{Esas}} \lVert \text{Lif}(\text{unsur}) \rVert\Big) \to \Big\lVert \prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur}) \Big\rVert \tag{3.8.3}$$

olduğu beyanına mütekâfidir.

Bu, klasik ihtiyar mütearifesinin iyi bilinen mütekâfi bir şekline, yâni "boş olmayan mecmûalardan bir ailenin kartezyen hâsıl-ı zarbı boş değildir" sözüne tekabül eder.

*İspat.* Kaziyye 2.15.7 mûcibince (3.8.1)'in varış sahası şuna mütekâfidir:

$$\Big\lVert \prod_{\text{unsur} : \text{Esas}} \; \sum_{\text{nokta} : \text{Lif}(\text{unsur})} \text{Kaziyye}(\text{unsur}, \text{nokta}) \Big\rVert.$$

Binâenaleyh (3.8.1), (3.8.3)'ün $\text{Lif}(\text{unsur}) :\equiv \sum_{\text{nokta} : \text{Lif}(\text{unsur})} \text{Kaziyye}(\text{unsur}, \text{nokta})$ olan hâline mütekâfidir. (Bu, Misal 3.1.5 ile Yardımcı Kaziyye 3.3.4 mûcibince bir mecmûadır.) Aksine olarak (3.8.3), (3.8.1)'in $\text{Lif}(\text{unsur})$'in (3.8.3)'teki aile ve $\text{Kaziyye}(\text{unsur}, \text{nokta}) :\equiv \mathbf{1}$ olan hâline mütekâfidir. Binâenaleyh ikisi mantıken mütekâfidir. İkisi de mahz kaziyye olduğundan, Yardımcı Kaziyye 3.3.3 mûcibince mütekâfi tiplerdir. ∎

İmtinâ'-ı-vasat'ta olduğu gibi, mütekâfi (3.8.1) ve (3.8.3) şekilleri esas tip nazariyemizin bir neticesi değildir; fakat tenâkuz doğurmaksızın mütearife olarak farz edilebilirler.

**Mülâhaza 3.8.4.** (3.8.3)'ün sağ tarafının daima sol tarafını gerektirdiğini göstermek kolaydır. İkisi de mahz kaziyye olduğundan, Yardımcı Kaziyye 3.3.3 mûcibince ihtiyar mütearifesi bir

$$\Big(\prod_{\text{unsur} : \text{Esas}} \lVert \text{Lif}(\text{unsur}) \rVert\Big) \simeq \Big\lVert \prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur}) \Big\rVert$$

tekâfü'ünü istemeye de mütekâfidir. Bu, yaygın bir tuzağı tasvir eder: merbût tâbi tipleri mahz kaziyyeleri muhafaza etse de (Misal 3.6.2), kat' ile yer değiştirmezler: $\lVert \prod_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur}) \rVert$ umûmiyetle $\prod_{\text{unsur} : \text{Tip}} \lVert \text{Kaziyye}(\text{unsur}) \rVert$'e mütekâfi değildir. İhtiyar mütearifesi, eğer onu farz edersek, bunun *mecmûalar için* doğru olduğunu söyler; aşağıda göreceğimiz üzere umûmiyetle sakıttır.

İhtiyar mütearifesinde mecmûa olan tiplere dair kayıt bir dereceye kadar gevşetilebilir. Meselâ (3.8.1)'deki Lif ile Kaziyye'nin yahut (3.8.3)'teki Lif'in keyfî tip aileleri olmasına izin verebiliriz; bu, aynı derecede tenâkuzsuz olan, görünüşte daha kuvvetli bir beyan verir. Kaziyyevî kat'ı yedinci babda mülâhaza edilecek daha umûmî buud-sayısı-kat'larıyla da değiştirebilir ve böylece, sadece İhtiyar (yahut tebarüz ettirmek için $\text{İhtiyar}_{-1}$) dediğimiz (3.8.1) ile, $\text{İhtiyar}_{\infty}$ diyeceğimiz Kaziyye 2.15.7 arasında yer alan bir $\text{İhtiyar}_{\text{buud-sayısı}}$ mütearifeler tayfı elde edebiliriz. Yedinci babın bu husustaki temrinlerine de bakınız. Bununla beraber şunu müşahede edin ki Esas'ın bir mecmûa olması şartını gevşetemeyiz.

**Yardımcı Kaziyye 3.8.5.** Öyle bir Esas tipi ve öyle bir $\text{Lif} : \text{Esas} \to \text{Kâinat}$ ailesi vardır ki her $\text{Lif}(\text{unsur})$ bir mecmûadır, fakat (3.8.3) yanlıştır.

*İspat.* $\text{Esas} :\equiv \sum_{\text{Tip} : \text{Kâinat}} \lVert \mathbf{2} = \text{Tip} \rVert$ tarif edilsin ve $\text{mebde'} :\equiv (\mathbf{2}, \lvert \text{aksiyet}_{\mathbf{2}} \rvert) : \text{Esas}$ olsun. O zaman Sigma tiplerindeki tarîklerin aynîleştirilmesi, $\lVert \text{Tip} = \mathbf{2} \rVert$'nin bir mahz kaziyye olması vakıası ve vahdet mûcibince, her $(\text{Tip}, \text{tarîk}), (\text{Diğer-tip}, \text{diğer-tarîk}) : \text{Esas}$ için $\big((\text{Tip}, \text{tarîk}) =_{\text{Esas}} (\text{Diğer-tip}, \text{diğer-tarîk})\big) \simeq (\text{Tip} \simeq \text{Diğer-tip})$ elde ederiz. Bilhassa $(\text{mebde'} =_{\text{Esas}} \text{mebde'}) \simeq (\mathbf{2} \simeq \mathbf{2})$'dir; binâenaleyh Misal 3.1.9'daki gibi Esas bir mecmûa değildir.

Diğer taraftan, eğer $(\text{Tip}, \text{tarîk}) : \text{Esas}$ ise, Tip bir mecmûadır; bu, $\text{tarîk} : \lVert \mathbf{2} = \text{Tip} \rVert$ için kat' üzerinde istikrâdan ve $\mathbf{2}$'nin bir mecmûa olması vakıasından çıkar. Tip ile Diğer-tip mecmûa olduğunda $\text{Tip} \simeq \text{Diğer-tip}$ bir mecmûa olduğundan, her $\text{birinci-unsur}, \text{ikinci-unsur} : \text{Esas}$ için $\text{birinci-unsur} =_{\text{Esas}} \text{ikinci-unsur}$'un bir mecmûa olduğu, yâni Esas'ın bir 1-tip olduğu çıkar. Bilhassa, eğer $\text{Lif} : \text{Esas} \to \text{Kâinat}$'ı $\text{Lif}(\text{unsur}) :\equiv (\text{mebde'} = \text{unsur})$ ile tarif edersek, her $\text{Lif}(\text{unsur})$ bir mecmûadır.

Şimdi tarif mûcibince her $(\text{Tip}, \text{tarîk}) : \text{Esas}$ için $\lVert \mathbf{2} = \text{Tip} \rVert$ ve binâenaleyh $\lVert \text{mebde'} = (\text{Tip}, \text{tarîk}) \rVert$ elde ederiz. Binâenaleyh $\prod_{\text{unsur} : \text{Esas}} \lVert \text{Lif}(\text{unsur}) \rVert$ elimizdedir. Eğer (3.8.3) bu Esas ve Lif için doğru olsaydı, $\lVert \prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur}) \rVert$ da elimizde olurdu. Bir mahz kaziyye olan bir tenâkuz ($\mathbf{0}$) çıkarmaya çalıştığımız için, $\prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur})$'u, yâni $\prod_{\text{unsur} : \text{Esas}} (\text{mebde'} = \text{unsur})$'u farz edebiliriz. Fakat bu Esas'ın bir mahz kaziyye ve binâenaleyh bir mecmûa olmasını gerektirir ki bu bir tenâkuzdur. ∎

## 3.9 Yegâne ihtiyar prensibi

Aşağıdaki müşahede âdidir, fakat pek faydalıdır.

**Yardımcı Kaziyye 3.9.1.** Eğer Kaziyye bir mahz kaziyye ise, $\text{Kaziyye} \simeq \lVert \text{Kaziyye} \rVert$ olur.

*İspat.* Elbette tarif mûcibince $\text{Kaziyye} \to \lVert \text{Kaziyye} \rVert$ elimizdedir. Ve Kaziyye bir mahz kaziyye olduğundan, $\lVert \text{Kaziyye} \rVert$'nin küllî hassası $\text{ayniyet}_{\text{Kaziyye}} : \text{Kaziyye} \to \text{Kaziyye}$'ye tatbik edilince $\lVert \text{Kaziyye} \rVert \to \text{Kaziyye}$ verir. Bu tâbiler Yardımcı Kaziyye 3.3.3 mûcibince şibh-i terslerdir. ∎

Bunun mühim neticeleri arasında şu vardır.

**Netice 3.9.2 (Yegâne ihtiyar prensibi).** Öyle bir $\text{Kaziyye} : \text{Tip} \to \text{Kâinat}$ tip ailesi farz edelim ki

1. Her unsur için $\text{Kaziyye}(\text{unsur})$ tipi bir mahz kaziyyedir, ve
2. Her unsur için $\lVert \text{Kaziyye}(\text{unsur}) \rVert$ elimizdedir.

O zaman $\prod_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$ elimizdedir.

*İspat.* İki farzdan ve evvelki yardımcı kaziyyeden derhal çıkar. ∎

Bu netice pek faydalı bir muhakeme usulünü de ihtiva eder. Yâni $\lVert \text{Tip} \rVert$'yi bildiğimizi ve bunu başka bir Diğer-tip tipinin bir unsurunu inşa etmek için kullanmak istediğimizi farz edelim. Diğer-tip'in bir unsurunu inşa ederken Tip'in bir unsurunu kullanmak isterdik; fakat buna ancak Diğer-tip bir mahz kaziyye ise izin verilir, ki $\lVert \text{Tip} \rVert$ kaziyyevî kat'ının istikrâ prensibini tatbik edebilelim; umûmiyetle yapmayı ümit edebileceğimiz en fazla şey $\lVert \text{Diğer-tip} \rVert$'yi göstermektir. Bunun yerine Diğer-tip'i, inşa etmek istediğimiz nesneyi *yegâne olarak* tavsif eden ilâve malûmatla genişletebiliriz. Hususiyle, $\sum_{\text{unsur} : \text{Diğer-tip}} \text{Diğer-kaziyye}(\text{unsur})$ bir mahz kaziyye olacak tarzda bir $\text{Diğer-kaziyye} : \text{Diğer-tip} \to \text{Kâinat}$ mahmûlü tarif ederiz. O zaman Tip'in bir unsurundan $\text{Diğer-kaziyye}(\text{öteki})$ olacak tarzda bir $\text{öteki} : \text{Diğer-tip}$ unsuru inşa ederiz; binâenaleyh $\lVert \text{Tip} \rVert$'den $\lVert \sum_{\text{unsur} : \text{Diğer-tip}} \text{Diğer-kaziyye}(\text{unsur}) \rVert$'i inşa edebiliriz; ve $\lVert \sum_{\text{unsur} : \text{Diğer-tip}} \text{Diğer-kaziyye}(\text{unsur}) \rVert$ tipi $\sum_{\text{unsur} : \text{Diğer-tip}} \text{Diğer-kaziyye}(\text{unsur})$'e mütekâfi olduğundan, ondan Diğer-tip'in bir unsuru izdüşürülebilir. Bir misal Temrin 3.19'da bulunabilir.

Benzer bir mesele mecmûalar nazariyesine dayanan riyâziyâtta da zuhur eder, gerçi biraz farklı tecellî eder. Eğer bir $\text{tâbi} : \text{Tip} \to \text{Diğer-tip}$ tâbisini tarif etmeye çalışıyorsak ve bir $\text{nokta} : \text{Tip}$ unsuruna bağlı olarak bir $\text{öteki} : \text{Diğer-tip}$'in mahz vücudunu ispat edebiliyorsak, henüz işimiz bitmemiştir; zîrâ Diğer-tip'in bir unsurunu sadece vücudunu ispat etmekle kalmayıp fiilen tayin etmemiz lâzımdır. Bir şık elbette, tip nazariyesinde yaptığımız gibi, delili $\text{öteki} : \text{Diğer-tip}$'in yegâne vücuduna kadar inceltmektir. Fakat mecmûalar nazariyesinde mesele çok defa, lâzım olan unsurları bizim için seçen ihtiyar mütearifesinin bir tatbikiyle daha basitçe atlatılabilir. Tahavvül-i muttasıl tip nazariyesinde ise, ihtiyardan kaçınma arzusundan tamamen ayrı olarak, mevcut ihtiyar şekilleri sadece daha az tatbik edilebilirdir; zîrâ ihtiyarın sahasının bir *mecmûa* olmasını gerektirirler. Binâenaleyh eğer Tip bir mecmûa değilse (meselâ belki bir Kâinat), tâbi(nokta)'yı tarif etmekte kullanmak üzere her $\text{nokta} : \text{Tip}$ için Diğer-tip'in bir unsurunu sadece seçmemize izin verecek tenâkuzsuz hiçbir ihtiyar şekli yoktur.

## 3.10 Kaziyyeler ne zaman kat'lıdır?

İlk bakışta, $+$ ile $\Sigma$'nın kat'lı şekilleri, "veya" ile "vardır"ın gayr-ı sûrî riyâzî mânâsına kat'sız olanlardan filhakika daha yakın görünebilir. Muhakkak ki sûrî mecmûalar nazariyesinin altında yatan birinci mertebe mantıkta "veya" ile "vardır"ın *dakik* mânâsına daha yakındırlar; zîrâ sonraki, kaziyyelerin doğruluğunun hiçbir şâhidini hatırlamaya teşebbüs etmez. Bununla beraber, *gayr-ı sûrî* riyâziyâtın amelinin çok defa kat'sız şekillerle daha doğru tasvir edildiğini fark etmek şaşırtıcı gelebilir.

Meselâ "her asal adet ya $2$'dir ya tektir" gibi bir beyanı düşünelim. Çalışan riyâziyeci bu vakıayı yalnız asal adetler hakkında *kaziyyeler* ispat etmek için değil, aynı zamanda asal adetler üzerinde *inşalar* icra etmek için, belki $2$ hâlinde bir şey ve tek bir asal hâlinde başka bir şey yaparak kullanmaktan hiç çekinmez. İnşanın nihaî neticesi sadece bir beyanın doğruluğu değil, asal adedin teklik çiftliğine bağlı olabilecek bir veri parçasıdır. Binâenaleyh tip nazariyesi nokta-i nazarından böyle bir inşa tabiî olarak, kaziyyevî kat'ı ile değil, "$(\text{asal} = 2) + (\text{asal tektir})$" munfasıl ictimâ tipinin istikrâ prensibi kullanılarak ifade edilir.

Kabul etmek lâzımdır ki bu ideal bir misal değildir; zîrâ "$\text{asal} = 2$" ile "asal tektir" birbirini dışlar, öyle ki $(\text{asal} = 2) + (\text{asal tektir})$ filhakika zaten bir mahz kaziyyedir ve binâenaleyh kendi kat'ına mütekâfidir (Temrin 3.7'ye bakınız). Daha ikna edici misaller vücûdî sûrdan gelir. "Öyle bir unsur vardır ki …" şeklinde bir kaziyye ispat edip sonra "Y Kaziyyesinde inşa edilen unsur"dan bahsetmek nâdir değildir (muarref edata dikkat edin). Bundan başka, bu unsurun daha ileri hassalarını istihrac ederken "Y Kaziyyesinin ispatındaki unsurun inşası mûcibince" gibi ibareler kullanılabilir.

Pek yaygın bir misal "Tip, Diğer-tip ile temâsül eder"dir ki bu, katı söylenirse yalnız Tip ile Diğer-tip arasında *bir* temâsülün var olduğu mânâsına gelir. Fakat böyle bir beyanı ispat ederken hemen daima muayyen bir temâsül gösterilir yahut evvelce bilinen bir tatbikin bir temâsül olduğu ispat edilir; ve hangi muayyen temâsülün verildiği çok defa sonradan ehemmiyet kazanır.

Mecmûalar nazariyesiyle yetişmiş riyâziyeciler böyle "lisan sû-i istimalleri" karşısında çok defa hafif bir vicdan azabı duyarlar. Onlar için özür dilemeye, onları son müsveddelerden silmeye, yahut "kanonik" gibi müphem kelimelerle onlardan sıyrılmaya teşebbüs edebiliriz. Mesele, sûrîleştirilmiş mecmûalar nazariyesinde fennî olarak nesneleri "inşa etmenin" hiçbir yolu bulunmaması vakıasıyla şiddetlenir; ancak muayyen hassaları olan bir nesnenin var olduğunu ispat edebiliriz. Binâenaleyh tip nazariyesindeki kat'sız mantık, gayr-ı sûrî riyâziyâtın, mecmûalar nazariyesine dayanan yeniden inşanın örttüğü bazı yaygın amellerini yakalar. (Bu, vahdet mütearifesinin temâsül eden nesneleri aynîleştirme hususundaki yaygın, fakat sûrî olarak haklı çıkarılmamış ameli nasıl muteber kıldığına benzer.)

Diğer taraftan, bazen kat'lı mantık elzemdir. Bunu İmtinâ'-ı-vasat'ın ve İhtiyar'ın ifadelerinde gördük; daha başka bazı misaller kitabın ilerisinde görünecektir. Binâenaleyh şu mesele ile karşı karşıyayız: gayr-ı sûrî tip nazariyesi yazarken "veya" ve "vardır" kelimeleriyle (ve "bulunur" ile "elimizdedir" gibi yaygın müteradifleriyle beraber) ne kastetmeliyiz?

Küllî bir ittifak mümkün olmayabilir. Belki yapılan riyâziyâtın nev'ine bağlı olarak bir itibar yahut öteki daha faydalı olabilir; yahut belki itibarın seçimi ehemmiyetsiz olabilir. Bu hâlde bir riyâzî makalenin başındaki bir mülâhaza, okuyucuyu orada kullanılan lisanî itibarlardan haberdar etmeye kâfi gelebilir. Bununla beraber, bir umûmî itibar seçildikten sonra bile, öteki nevi mantık umûmiyetle hiç değilse ara sıra zuhur edecektir; binâenaleyh ona atıf yapmanın bir yoluna muhtacız. Daha umûmî olarak, kaziyyevî kat'ı benzer şekilde davranan tipler üzerindeki başka bir ameliye ile, meselâ $\text{Tip} \mapsto \neg\neg \text{Tip}$ çift nefy ameliyesiyle yahut yedinci babda mülâhaza edilecek buud-sayısı-kat'larıyla değiştirmek de düşünülebilir. Takdim hususunda bir tecrübe olarak, bundan sonra kaziyyevî kat' gibi böyle "cihetlerin" tatbikini göstermek için ara sıra *zarflar* kullanacağız.

Meselâ eğer kat'sız mantık varsayılan itibar ise, kaziyyevî kat'ı göstermek için **mahzen** zarfını kullanabiliriz. Binâenaleyh

> "$\text{Kaziyye}(\text{unsur})$ olacak tarzda mahzen bir $\text{unsur} : \text{Tip}$ vardır"

ibaresi $\lVert \sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur}) \rVert$ tipine işaret eder. Benzer şekilde, bir Tip tipinin kaziyyevî kat'ı $\lVert \text{Tip} \rVert$'nin meskûn olduğunu (yâni onun isimsiz bir unsurunun elimizde bulunduğunu) kastetmek için Tip'in **mahzen meskûn** olduğunu söyleyeceğiz. Dikkat edilsin ki bu, "mahzen" zarfının gayr-ı sûrî riyâzî lisanımızda kullanılacağı şekliyle bir *tarif*idir; tıpkı "zümre" ve "halka" gibi isimleri ve "muntazam" ve "normal" gibi sıfatları dakik riyâzî mânâlara sahip olacak şekilde tarif ettiğimiz gibi. "Mahzen" kelimesinin lügat tarifinin kaziyyevî kat'a işaret ettiğini iddia etmiyoruz; kelimenin seçilmesi yalnız riyâziyeci okuyucuya, bir mahz kaziyyenin "mahzen" bir sıdk kıymetinin malûmatını ihtiva ettiğini ve fazlasını ihtiva etmediğini hatırlatmak içindir.

Diğer taraftan, eğer kat'lı mantık o anki varsayılan itibar ise, onun yokluğunu göstermek için **safiyen** yahut **inşâî olarak** gibi bir zarf kullanabiliriz; öyle ki

> "$\text{Kaziyye}(\text{unsur})$ olacak tarzda safiyen bir $\text{unsur} : \text{Tip}$ vardır"

$\sum_{\text{unsur} : \text{Tip}} \text{Kaziyye}(\text{unsur})$ tipini gösterirdi. "Safiyen" yahut "filhakika" kelimelerini, varsayılan itibar o olduğunda bile, sadece kat'ın yokluğunu tebarüz ettirmek için de kullanabiliriz.

Bu kitapta, birkaç sebepten dolayı, kat'sız mantığı varsayılan itibar olarak kullanmaya devam edeceğiz.

1. Yeni gelenin, sadece daha âşinâ olduğu için kat'lı mantığa sarılmak yerine onunla tecrübe yapmasını teşvik etmek istiyoruz.
2. Tip nazariyesinde varsayılan olarak kat'lı mantığı kullanmak, mecmûalar nazariyesi esaslarıyla aynı nevi "lisan sû-i istimali" dertlerinden muzdarip olur; kat'sız mantık ise bunlardan kaçınır. Meselâ "$\text{Tip} \simeq \text{Diğer-tip}$"yi, onun kaziyyevî kat'ı olarak değil, Tip ile Diğer-tip arasındaki tekâfü'lerin tipi olarak tarif etmemiz şu mânâya gelir: "$\text{Tip} \simeq \text{Diğer-tip}$" şeklinde bir kaziyyeyi ispat etmek, lafzen böyle muayyen bir tekâfü' inşa etmektir. Bu muayyen tekâfü'e sonra atıf yapılabilir.
3. "Mahz kaziyye" mefhûmunun tip nazariyesinin temel bir cüz'ü olmadığını tebarüz ettirmek istiyoruz. Yedinci babda göreceğimiz üzere, mahz kaziyyeler nihâyetsiz bir merdivenin ancak ikinci basamağıdır ve bu merdiven üzerinde hiç bulunmayan daha birçok cihet de vardır.
4. Klasik olarak mahz kaziyye olan birçok beyan tahavvül-i muttasıl tip nazariyesinde artık öyle değildir. Elbette bunların başında müsâvât gelir.
5. Diğer taraftan, tahavvül-i muttasıl tip nazariyesinin en alâka çekici müşahedelerinden biri, şaşırtıcı sayıda tipin hiçbir kat'a ihtiyaç duymadan *kendiliğinden* mahz kaziyye olması, yahut öyle olmak üzere biraz tadil edilebilmesidir. (Yardımcı Kaziyye 3.3.5'e ve dördüncü, yedinci, dokuzuncu ve onuncu bablara bakınız.) Binâenaleyh bu tipler bir sıdk kıymetinden öte hiçbir veri ihtiva etmese de, kaziyyevî kat'ın istikrâ prensibini kullanmaya hiç ihtiyaç olmadığından, onları kat'sız nesneler inşa etmek için yine de kullanabiliriz. Bu faydalı vakıa, eğer kaziyyevî kat' bütün beyanlara varsayılan olarak tatbik edilirse, ifade edilmesi daha hantal olur.
6. Nihayet, kat'lar bu kitapta yapacağımız riyâziyâtın çoğu için pek faydalı değildir; binâenaleyh zuhur ettikleri yerde onları açıkça işaretlemek daha basittir.

## 3.11 Büzülebilirlik

Yardımcı Kaziyye 3.3.2'de, meskûn bir mahz kaziyyenin $\mathbf{1}$'e mütekâfi olması gerektiğini müşahede ettik; aksinin de doğru olduğunu görmek güç değildir. Bu hassaya sahip bir tipe *büzülebilir* denir. Büzülebilirliğin, bazen elverişli olan mütekâfi başka bir tarifi de şudur.

**Tarif 3.11.1.** Eğer her $\text{unsur} : \text{Tip}$ için $\text{merkez} = \text{unsur}$ olacak tarzda, **büzülme merkezi** denen bir $\text{merkez} : \text{Tip}$ varsa, Tip tipine **büzülebilir** yahut **tekil** denir. Belirtilen $\text{merkez} = \text{unsur}$ tarîkini $\text{büzülme}_{\text{unsur}}$ ile gösteririz.

Başka sözlerle, $\text{büzülebilir-mi}(\text{Tip})$ tipi şöyle tarif edilir:

$$\text{büzülebilir-mi}(\text{Tip}) :\equiv \sum_{\text{merkez} : \text{Tip}} \; \prod_{\text{unsur} : \text{Tip}} (\text{merkez} = \text{unsur}).$$

Dikkat edilsin ki âdet olan tipler olarak kaziyyeler okuyuşu altında $\text{büzülebilir-mi}(\text{Tip})$'i "Tip tam olarak bir unsur ihtiva eder", yahut daha dakik olarak "Tip bir unsur ihtiva eder ve Tip'in her unsuru o unsura müsâvîdir" diye telaffuz edebiliriz.

**Mülâhaza 3.11.2.** $\text{büzülebilir-mi}(\text{Tip})$'i daha vaz'î olarak "öyle bir $\text{merkez} : \text{Tip}$ noktası vardır ki her $\text{unsur} : \text{Tip}$ için merkezden unsura bir tarîk vardır" diye de telaffuz edebiliriz. Dikkat edilsin ki klasik bir kulağa bu, büzülebilirlikten ziyade *ittisal*in bir tarifi gibi gelir. Mesele şudur ki bu cümledeki "vardır"ın mânâsı muttasıl/tabiî bir mânâdır.

İttisali ifade etmenin daha iyi bir yolu $\sum_{\text{merkez} : \text{Tip}} \prod_{\text{unsur} : \text{Tip}} \lVert \text{merkez} = \text{unsur} \rVert$ olurdu. Eğer Tip'in noktalı olduğu farz edilirse bu filhakika doğrudur (yedinci babda, noktalı tiplerin ittisaline dair yardımcı kaziyyeden sonraki mülâhazaya bakınız); fakat umûmiyetle bir tip noktalı olmadan muttasıl olabilir. 7.5. fasılda ittisali, umûmî bir buud-sayısı-ittisali mefhûmunun buud-sayısı sıfır olan hâli olarak tarif edeceğiz; ve yedinci babın bir temrininde okuyucudan, bu tarifin hem $\lVert \text{Tip} \rVert$'ye hem de $\prod_{\text{unsur}, \text{öteki} : \text{Tip}} \lVert \text{unsur} = \text{öteki} \rVert$'e sahip olmaya mütekâfi olduğunu göstermesi istenir.

**Yardımcı Kaziyye 3.11.3.** Bir Tip tipi için aşağıdakiler mantıken mütekâfidir.

1. Tip, Tarif 3.11.1 mânâsında büzülebilirdir.
2. Tip bir mahz kaziyyedir ve bir $\text{merkez} : \text{Tip}$ noktası vardır.
3. Tip, $\mathbf{1}$'e mütekâfidir.

*İspat.* Eğer Tip büzülebilir ise, muhakkak ki bir $\text{merkez} : \text{Tip}$ noktası (büzülme merkezi) vardır; her $\text{unsur}, \text{öteki} : \text{Tip}$ için ise $\text{unsur} = \text{merkez} = \text{öteki}$ elde ederiz; binâenaleyh Tip bir mahz kaziyyedir. Aksine olarak, eğer $\text{merkez} : \text{Tip}$ elimizde ise ve Tip bir mahz kaziyye ise, her $\text{unsur} : \text{Tip}$ için $\text{unsur} = \text{merkez}$ elde ederiz; binâenaleyh Tip büzülebilirdir. Ve (2)$\Rightarrow$(3)'ü Yardımcı Kaziyye 3.3.2'de gösterdik; aksi ise $\mathbf{1}$'in (2) hassasına kolayca sahip olmasından çıkar. ∎

**Yardımcı Kaziyye 3.11.4.** Her Tip tipi için $\text{büzülebilir-mi}(\text{Tip})$ tipi bir mahz kaziyyedir.

*İspat.* $\text{şâhid}, \text{diğer-şâhid} : \text{büzülebilir-mi}(\text{Tip})$ verilmiş olsun. $\text{nokta}, \text{diğer-nokta} : \text{Tip}$ ve $\text{tarîk} : \prod_{\text{unsur} : \text{Tip}} (\text{nokta} = \text{unsur})$ ve $\text{diğer-tarîk} : \prod_{\text{unsur} : \text{Tip}} (\text{diğer-nokta} = \text{unsur})$ için $\text{şâhid} \equiv (\text{nokta}, \text{tarîk})$ ve $\text{diğer-şâhid} \equiv (\text{diğer-nokta}, \text{diğer-tarîk})$ olduğunu farz edebiliriz. Sigma tiplerindeki tarîklerin tavsifi mûcibince, $\text{şâhid} = \text{diğer-şâhid}$ olduğunu göstermek için $\text{nakil}^{\text{bağ}}(\text{tarîk}) = \text{diğer-tarîk}$ olacak tarzda bir $\text{bağ} : \text{nokta} = \text{diğer-nokta}$ göstermek kâfidir. $\text{bağ} :\equiv \text{tarîk}(\text{diğer-nokta})$ seçeriz. Şimdi Tip (şâhid ile yahut diğer-şâhid ile) büzülebilir olduğundan, Yardımcı Kaziyye 3.11.3 mûcibince bir mahz kaziyyedir. Binâenaleyh Yardımcı Kaziyye 3.3.4 ve Misal 3.6.2 mûcibince $\prod_{\text{unsur} : \text{Tip}} (\text{diğer-nokta} = \text{unsur})$ de öyledir; binâenaleyh $\text{nakil}^{\text{bağ}}(\text{tarîk}) = \text{diğer-tarîk}$ kendiliğinden hâsıl olur. ∎

**Netice 3.11.5.** Eğer Tip büzülebilir ise, $\text{büzülebilir-mi}(\text{Tip})$ de öyledir.

*İspat.* Yardımcı Kaziyye 3.11.4 ve Yardımcı Kaziyye 3.11.3'ün (2) şıkkı mûcibince. ∎

Mahz kaziyyeler gibi, büzülebilir tipler de birçok tip kurucusu tarafından muhafaza edilir. Meselâ şu elimizdedir:

**Yardımcı Kaziyye 3.11.6.** Eğer $\text{Lif} : \text{Tip} \to \text{Kâinat}$, her $\text{Lif}(\text{nokta})$'sı büzülebilir olan bir tip ailesi ise, $\prod_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$ büzülebilirdir.

*İspat.* Misal 3.6.2 mûcibince, her $\text{Lif}(\text{unsur})$ bir mahz kaziyye olduğundan $\prod_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$ bir mahz kaziyyedir. Fakat onun bir unsuru da vardır, yâni her $\text{unsur} : \text{Tip}$'yi $\text{Lif}(\text{unsur})$'un büzülme merkezine gönderen tâbi. Binâenaleyh Yardımcı Kaziyye 3.11.3'ün (2) şıkkı mûcibince $\prod_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$ büzülebilirdir. ∎

(Filhakika Yardımcı Kaziyye 3.11.6'nın beyanı tâbi genişliği mütearifesine mütekâfidir. 4.9. fasla bakınız.)

Elbette eğer Tip, Diğer-tip'e mütekâfi ise ve Tip büzülebilir ise, Diğer-tip de öyledir. Daha umûmî olarak, Diğer-tip'in Tip'in bir *geri çekileni* olması kâfidir. Tarif mûcibince bir **geri çekme**, bir $\text{geri-çekme} : \text{Tip} \to \text{Diğer-tip}$ tâbisidir ki, onun **kesit**i denen bir $\text{kesit} : \text{Diğer-tip} \to \text{Tip}$ tâbisi ve bir $\text{telafi} : \prod_{\text{öteki} : \text{Diğer-tip}} (\text{geri-çekme}(\text{kesit}(\text{öteki})) = \text{öteki})$ tahavvül-i muttasılı vardır; o zaman Diğer-tip'in Tip'in bir **geri çekileni** olduğunu söyleriz.

**Yardımcı Kaziyye 3.11.7.** Eğer Diğer-tip, Tip'in bir geri çekileni ise ve Tip büzülebilir ise, Diğer-tip de öyledir.

*İspat.* $\text{merkez} : \text{Tip}$ büzülme merkezi olsun. $\text{diğer-merkez} :\equiv \text{geri-çekme}(\text{merkez}) : \text{Diğer-tip}$'nin Diğer-tip için bir büzülme merkezi olduğunu iddia ediyoruz. $\text{öteki} : \text{Diğer-tip}$ olsun; bir $\text{öteki} = \text{diğer-merkez}$ tarîkine muhtacız. Fakat $\text{telafi}_{\text{öteki}} : \text{geri-çekme}(\text{kesit}(\text{öteki})) = \text{öteki}$ ve $\text{büzülme}_{\text{kesit}(\text{öteki})} : \text{kesit}(\text{öteki}) = \text{merkez}$ elimizdedir; binâenaleyh terkip ile

$$\text{telafi}_{\text{öteki}}^{-1} \cdot \text{tatbik}_{\text{geri-çekme}}\big(\text{büzülme}_{\text{kesit}(\text{öteki})}\big) : \text{öteki} = \text{geri-çekme}(\text{merkez}) \equiv \text{diğer-merkez}. \quad ∎$$

Büzülebilir tipler, hepsi $\mathbf{1}$'e mütekâfi olduğundan, pek alâka çekici görünmeyebilir. Bu mefhûmun faydalı olmasının bir sebebi, tek tek âdi olmayan verilerden bir topluluğun bazen hep beraber büzülebilir bir tip teşkil etmesidir. Mühim bir misal, bir ucu serbest olan tarîklerin fezâsıdır. 5.8. fasılda göreceğimiz üzere, bu vakıa esasen ayniyet tipleri için mebde'li tarîk istikrâ prensibini ihtiva eder.

**Yardımcı Kaziyye 3.11.8.** Her Tip ve her $\text{merkez} : \text{Tip}$ için $\sum_{\text{unsur} : \text{Tip}} (\text{merkez} = \text{unsur})$ tipi büzülebilirdir.

*İspat.* Merkez olarak $(\text{merkez}, \text{aksiyet}_{\text{merkez}})$ noktasını seçeriz. Şimdi $(\text{unsur}, \text{tarîk}) : \sum_{\text{unsur} : \text{Tip}} (\text{merkez} = \text{unsur})$ olduğunu farz edelim; $(\text{merkez}, \text{aksiyet}_{\text{merkez}}) = (\text{unsur}, \text{tarîk})$ olduğunu göstermeliyiz. Sigma tiplerindeki tarîklerin tavsifi mûcibince, $\text{nakil}^{\text{bağ}}(\text{aksiyet}_{\text{merkez}}) = \text{tarîk}$ olacak tarzda bir $\text{bağ} : \text{merkez} = \text{unsur}$ göstermek kâfidir. Fakat $\text{bağ} :\equiv \text{tarîk}$ alabiliriz; bu hâlde $\text{nakil}^{\text{bağ}}(\text{aksiyet}_{\text{merkez}}) = \text{tarîk}$, tarîk tiplerindeki naklin tavsifinden çıkar. ∎

Bu vuku bulduğunda, büzülebilir verinin serbestçe ihmal edilebileceği gayr-ı sûrî prensibini kullanarak, girift bir inşayı tekâfü' kaydıyla sadeleştirmemize imkân verebilir. Bu prensip birçok yardımcı kaziyyeden ibarettir ki çoğunu okuyucuya bırakıyoruz; aşağıdaki bir misaldir.

**Yardımcı Kaziyye 3.11.9.** $\text{Lif} : \text{Tip} \to \text{Kâinat}$ bir tip ailesi olsun.

1. Eğer her $\text{Lif}(\text{unsur})$ büzülebilir ise, $\sum_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$, Tip'e mütekâfidir.
2. Eğer Tip, merkezi merkez olan bir büzülebilir tip ise, $\sum_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$, $\text{Lif}(\text{merkez})$'e mütekâfidir.

*İspat.* (1) hâlinde $\text{birinci-izdüşüm} : \sum_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur}) \to \text{Tip}$'nin bir tekâfü' olduğunu gösteririz. Şibh-i ters olarak, $\text{merkez}_{\text{unsur}}$ $\text{Lif}(\text{unsur})$'un merkezi olmak üzere $\text{dönüş}(\text{unsur}) :\equiv (\text{unsur}, \text{merkez}_{\text{unsur}})$ tarif ederiz. $\text{birinci-izdüşüm} \circ \text{dönüş}$ terkibi âşikâr olarak $\text{ayniyet}_{\text{Tip}}$'dir; ters terkip ise her $\text{Lif}(\text{unsur})$'un büzülmeleri kullanılarak ayniyete tahavvül-i muttasılca müsâvîdir.

(2)'nin ispatını okuyucuya bırakıyoruz (Temrin 3.20'ye bakınız). ∎

Büzülebilir tiplerin alâka çekici olmasının başka bir sebebi, 3.1. fasılda zikredilen buud-sayısı-tipler merdivenini bir basamak daha aşağıya doğru uzatmalarıdır.

**Yardımcı Kaziyye 3.11.10.** Bir Tip tipi, ancak ve ancak her $\text{unsur}, \text{öteki} : \text{Tip}$ için $\text{unsur} =_{\text{Tip}} \text{öteki}$ tipi büzülebilir olduğunda bir mahz kaziyyedir.

*İspat.* "Olduğunda" kısmı için, sadece her büzülebilir tipin meskûn olduğunu müşahede ederiz. "Ancak" kısmı için, 3.3. fasılda her mahz kaziyyenin bir mecmûa olduğunu müşahede etmiştik; öyle ki her $\text{unsur} =_{\text{Tip}} \text{öteki}$ tipi bir mahz kaziyyedir. Fakat o (Tip bir mahz kaziyye olduğundan) meskûndur da; binâenaleyh Yardımcı Kaziyye 3.11.3'ün (2) şıkkı mûcibince büzülebilirdir. ∎

Binâenaleyh büzülebilir tiplere **(−2)-tipler** de denebilir. Onlar buud-sayısı-tipler merdiveninin en alt basamağıdır ve yedinci babda buud-sayısı-tiplerin rücû'lu tarifinin esas hâli olacaklardır.

## Notlar

Mecmûaları, mahz kaziyyeleri ve büzülebilir tipleri, 3.1., 3.3. ve 3.11. fasıllardaki gibi bütün yüksek tahavvül-i muttasılların kendiliğinden hesaba katılmasıyla tip nazariyesinde tarif etmenin mümkün olduğu vakıası ilk defa Voevodsky tarafından müşahede edilmiştir. Filhakika o, yedinci babda yapacağımız gibi, buud-sayısı-tiplerin bütün silsilesini istikrâ ile tarif etmiştir.

Kaziyye 3.2.2 ve Netice 3.2.7 esas itibarıyla Hedberg'in klasik bir kaziyyesine dayanır ki onu 7.2. fasılda ispat edeceğiz. İmtinâ'-ı-vasat'ın tipler olarak kaziyyeler şeklinin vahdetle tenâkuz ettiği neticesi Martín Escardó tarafından Agda elektronik mektup listesinde müşahede edilmiştir. Kaziyye 3.2.2 için verdiğimiz ispat Thierry Coquand'a aittir.

Kaziyyevî kat', genişlemeli NuPRL tip nazariyesinde 1983'te Constable tarafından [Con85], "alt mecmûa" ve "bölüm" tiplerinin bir tatbiki olarak tanıtılmıştır. Burada "kaziyyevî kat'" denen şeye NuPRL tip nazariyesinde "ezme" denmiştir [constable+86nuprl-book]. Kaziyyevî kat'ı doğrudan tavsif eden kaideler, yine genişlemeli tip nazariyesinde, [ab:bracket-types]'da verilmiştir. Tahavvül-i muttasıl tip nazariyesindeki dahilî şekil Voevodsky tarafından gayr-ı tahmîlî bir sûr kullanılarak, sonra da Lumsdaine tarafından yüksek istikrâî tipler kullanılarak inşa edilmiştir (6.9. fasla bakınız).

Voevodsky [Universe-poly], 3.5. fasılda mülâhaza edilen nevîden yeniden boyutlandırma kaideleri teklif etmiştir. Bunlar, Russell'ın Whitehead ile beraber yazdığı *Principia Mathematica*'da [PM2] teklif ettiği meşhur *irca' mütearifesi* ile âşikâr olarak alâkalıdır.

Kat'sız mantığa atıf için kullanılan "safiyen" zarfı, programlama lisanlarında tesirleri nümûnelendirmek için tek-unsurlu (monadik) cihetlerin kullanılmasına bir işarettir; 7.7. fasla ve yedinci babın Notlarına bakınız.

Mantığın tip nazariyesine nisbetle ele alınabileceği birçok farklı yol vardır. Meselâ 1.11. fasılda tarif edilen düz tipler olarak kaziyyeler mantığına ve 3.6. fasılda tarif edildiği üzere yalnız mahz kaziyyeleri kullanan bedeline ilâveten, tiplere biraz benzer davranan fakat onlarla aynîleştirilmeyen ayrı bir kaziyyeler "nev'i" de idhâl edilebilir. Bu, mantıkla zenginleştirilmiş tip nazariyesinde [aczel2002collection] ve toposların ve alâkalı makûlelerin dahilî lisanlarının bazı takdimlerinde (meselâ [jacobs1999categorical, elephant]), aynı zamanda Coq ispat muâvininde benimsenen yaklaşımdır. Böyle bir yaklaşım daha umûmîdir, fakat daha az kudretlidir. Meselâ yegâne ihtiyar prensibi (3.9. fasıl), Coq'taki mecmûamsı denilen şeylerin makûlesinde [Spiwack], mantıkla zenginleştirilmiş tip nazariyesinde [aczel2002collection] ve asgarî tip nazariyesinde [maietti2005toward] sakıttır. Binâenaleyh vahdet mütearifesi, tip nazariyemizin bir toposun dahilî mantığına daha çok benzer davranmasını sağlar; onuncu baba da bakınız.

Martin-Löf [martin2006100] ihtiyar mütearifelerinin tarihine dair bir müzakere arz eder. Elbette inşâî ve hadsî riyâziyâtın uzun ve girift bir tarihi vardır ki ona burada dalmayacağız; meselâ [TroelstraI, TroelstraII]'ye bakınız.

## Temrinler

**Temrin 3.1.** Eğer $\text{Tip} \simeq \text{Diğer-tip}$ ise ve Tip bir mecmûa ise, Diğer-tip'in de öyle olduğunu ispat ediniz.

**Temrin 3.2.** Eğer Tip ile Diğer-tip mecmûa ise, $\text{Tip} + \text{Diğer-tip}$'nin de öyle olduğunu ispat ediniz.

**Temrin 3.3.** Eğer Tip bir mecmûa ise ve $\text{Lif} : \text{Tip} \to \text{Kâinat}$, her $\text{unsur} : \text{Tip}$ için $\text{Lif}(\text{unsur})$'un bir mecmûa olduğu bir tip ailesi ise, $\sum_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$'un bir mecmûa olduğunu ispat ediniz.

**Temrin 3.4.** Tip'in ancak ve ancak $\text{Tip} \to \text{Tip}$ büzülebilir olduğunda bir mahz kaziyye olduğunu gösteriniz.

**Temrin 3.5.** $\text{kaziyye-mi}(\text{Tip}) \simeq \big(\text{Tip} \to \text{büzülebilir-mi}(\text{Tip})\big)$ olduğunu gösteriniz.

**Temrin 3.6.** Eğer Tip bir mahz kaziyye ise, $\text{Tip} + (\neg \text{Tip})$'nin de öyle olduğunu gösteriniz. Binâenaleyh (3.4.1)'e bir kaziyyevî kat' koymaya ihtiyaç yoktur.

**Temrin 3.7.** Daha umûmî olarak, eğer Tip ile Diğer-tip mahz kaziyyeler ise ve $\neg(\text{Tip} \times \text{Diğer-tip})$ ise, $\text{Tip} + \text{Diğer-tip}$'nin de bir mahz kaziyye olduğunu gösteriniz.

**Temrin 3.8.** Bir $\text{tekâfü'-mü}(\text{tâbi})$ tipinin 2.4. fasıldaki (i)–(iii) şartlarını sağladığını farz ederek, $\lVert \text{şibh-i-ters}(\text{tâbi}) \rVert$ tipinin de aynı şartları sağladığını ve $\text{tekâfü'-mü}(\text{tâbi})$'ye mütekâfi olduğunu gösteriniz.

**Temrin 3.9.** Eğer İmtinâ'-ı-vasat doğru ise, $\text{Kaziyyeler} :\equiv \sum_{\text{Tip} : \text{Kâinat}} \text{kaziyye-mi}(\text{Tip})$ tipinin $\mathbf{2}$'ye mütekâfi olduğunu gösteriniz.

**Temrin 3.10.** Eğer $\text{Kâinat}_{\text{derece}+1}$ İmtinâ'-ı-vasat'ı sağlıyorsa, kanonik $\text{Kaziyye}_{\text{Kâinat}_{\text{derece}}} \to \text{Kaziyye}_{\text{Kâinat}_{\text{derece}+1}}$ dahil etme tatbikinin bir tekâfü' olduğunu gösteriniz.

**Temrin 3.11.** Her $\text{Tip} : \text{Kâinat}$ için $\lVert \text{Tip} \rVert \to \text{Tip}$ olmasının doğru olmadığını gösteriniz. (Bununla beraber $\lVert \text{Tip} \rVert \to \text{Tip}$'nin doğru olduğu hususî tipler bulunabilir. Temrin 3.8, $\text{şibh-i-ters}(\text{tâbi})$'nin böyle olduğunu gerektirir.)

**Temrin 3.12.** Eğer İmtinâ'-ı-vasat doğru ise, her $\text{Tip} : \text{Kâinat}$ için $\big\lVert (\lVert \text{Tip} \rVert \to \text{Tip}) \big\rVert$ olduğunu gösteriniz. (Bu hassa, İmtinâ'-ı-vasat'ın yokluğunda sakıt olabilen, ihtiyar mütearifesinin pek basit bir şeklidir; [krausgeneralizations]'a bakınız.)

**Temrin 3.13.** Netice 3.2.7'de İmtinâ'-ı-vasat'ın şu saf şeklinin vahdet ile tenâkuz ettiğini gösterdik:

$$\prod_{\text{Tip} : \text{Kâinat}} \big(\text{Tip} + (\neg \text{Tip})\big)$$

Vahdetin yokluğunda bu mütearife tenâkuzsuzdur. Bununla beraber, onun ihtiyar mütearifesini (3.8.1) gerektirdiğini gösteriniz.

**Temrin 3.14.** İmtinâ'-ı-vasat farz edilince, $\neg\neg \text{Tip}$ çift nefyinin, hükmî değil kaziyyevî bir hesap kaidesiyle de olsa, $\lVert \text{Tip} \rVert$ kaziyyevî kat'ı ile aynı rücû' prensibine sahip olduğunu gösteriniz. Başka sözlerle, İmtinâ'-ı-vasat farz edilince, eğer Diğer-tip bir mahz kaziyye ise ve $\text{tâbi} : \text{Tip} \to \text{Diğer-tip}$ elimizde ise, her $\text{nokta} : \text{Tip}$ için $\text{diğer-tâbi}(\lvert \text{nokta} \rvert) = \text{tâbi}(\text{nokta})$ olacak tarzda, bundan doğan bir $\text{diğer-tâbi} : \neg\neg \text{Tip} \to \text{Diğer-tip}$ bulunduğunu ispat ediniz. (İmtinâ'-ı-vasat farz edilince) $\neg\neg \text{Tip} \simeq \lVert \text{Tip} \rVert$ olduğunu istihrac ediniz. Binâenaleyh İmtinâ'-ı-vasat altında kaziyyevî kat', ayrı bir tip kurucusu olarak alınmaktan ziyade tarif edilebilir.

**Temrin 3.15.**

1. Her $\text{Tip} : \text{Kâinat}$ için
   $$\prod_{\text{Kaziyye} : \text{Kaziyye}_{\text{Kâinat}}} \big((\text{Tip} \to \text{Kaziyye}) \to \text{Kaziyye}\big)$$
   tipinin, hiç değilse Kâinat'taki kaziyyelere nisbetle, $\lVert \text{Tip} \rVert$ ile aynı rücû' prensibine, aynı hükmî hesap kaidesi *ile beraber*, sahip olduğunu gösteriniz.
2. Evvelki kısımda mülâhaza edilen tip aynı Kâinat'ta yer almaz ve onun rücû' prensibi yalnız Kâinat'taki kaziyyelere tatbik olunur. Eğer kaziyyevî yeniden boyutlandırmayı farz edersek, aynı Kâinat'ta yer alan ve, yalnız kaziyyevî bir hesap kaidesiyle de olsa, $\lVert \text{Tip} \rVert$ ile aynı rücû' prensibini sağlayan bir tip tarif edebileceğimizi gösteriniz. Binâenaleyh bu hâlde de kaziyyevî kat'ı tarif edebiliriz.

**Temrin 3.16.** İmtinâ'-ı-vasat farz edilince, çift nefyin, mahz kaziyyelerin mecmûalar üzerinde küllî sûrla bağlanmasıyla yer değiştirdiğini gösteriniz. Yâni eğer Esas bir mecmûa ise ve her $\text{Lif}(\text{unsur})$ bir mahz kaziyye ise, İmtinâ'-ı-vasat'ın

$$\Big(\prod_{\text{unsur} : \text{Esas}} \neg\neg \text{Lif}(\text{unsur})\Big) \simeq \Big(\neg\neg \prod_{\text{unsur} : \text{Esas}} \text{Lif}(\text{unsur})\Big) \tag{3.11.11}$$

olmasını gerektirdiğini gösteriniz. Müşahede ediniz ki eğer bunun yerine her $\text{Lif}(\text{unsur})$'un bir mecmûa olduğunu farz edersek, (3.11.11) ihtiyar mütearifesine (3.8.3) mütekâfi olur.

**Temrin 3.17.** 3.7. fasılda verilen kaziyyevî kat' kaidelerinin şu istikrâ prensibini gerektirmeye kâfi olduğunu gösteriniz: her $\text{Lif}(\text{unsur})$'u bir mahz kaziyye olan her $\text{Lif} : \lVert \text{Tip} \rVert \to \text{Kâinat}$ tip ailesi için, eğer her $\text{nokta} : \text{Tip}$ için $\text{Lif}(\lvert \text{nokta} \rvert)$ elimizde ise, her $\text{unsur} : \lVert \text{Tip} \rVert$ için $\text{Lif}(\text{unsur})$ elimizdedir.

**Temrin 3.18.** İmtinâ'-ı vasat kanununun (3.4.1) ve çift nefy kanununun (3.4.2) mantıken mütekâfi olduğunu gösteriniz.

**Temrin 3.19.** $\text{Kaziyye} : \text{Tabiî} \to \text{Kâinat}$'ın mahz kaziyyelerden müteşekkil karar verilebilir bir aile olduğunu (Tarif 3.4.3'ün (2) şıkkına bakınız) farz ediniz.

$$\Big\lVert \sum_{\text{adet} : \text{Tabiî}} \text{Kaziyye}(\text{adet}) \Big\rVert \;\to\; \sum_{\text{adet} : \text{Tabiî}} \text{Kaziyye}(\text{adet})$$

olduğunu ispat ediniz.

**Temrin 3.20.** Yardımcı Kaziyye 3.11.9'un (2) şıkkını ispat ediniz: eğer Tip, merkezi merkez olan bir büzülebilir tip ise, $\sum_{\text{unsur} : \text{Tip}} \text{Lif}(\text{unsur})$, $\text{Lif}(\text{merkez})$'e mütekâfidir.

**Temrin 3.21.** $\text{kaziyye-mi}(\text{Kaziyye}) \simeq (\text{Kaziyye} \simeq \lVert \text{Kaziyye} \rVert)$ olduğunu ispat ediniz.

**Temrin 3.22.** Klasik mecmûalar nazariyesinde olduğu gibi, ihtiyar mütearifesinin mütenâhî şekli bir kaziyyedir. Esas, (Temrin 1.9'da tarif edildiği gibi) bir $\text{Mütenâhî}(\text{adet})$ mütenâhî tipi olduğunda ihtiyar mütearifesinin (3.8.1) doğru olduğunu ispat ediniz.

**Temrin 3.23.** Temrin 3.19'un neticesinin, $\text{Kaziyye} : \text{Tabiî} \to \text{Kâinat}$ herhangi bir karar verilebilir aile olduğunda da doğru olduğunu gösteriniz.

**Temrin 3.24.** Kaziyye 2.13.1'in ispatını, evvelâ her $\text{birinci-adet}, \text{ikinci-adet}$ için $\text{şifre}(\text{birinci-adet}, \text{ikinci-adet})$'in bir mahz kaziyye olduğunu ispat ederek sadeleştiriniz.

---

## İsimler cedveli

Sağdaki sütun aslındaki işaretin **adını** verir; düsturların kendisinde harf kullanılmamıştır.

| Tercümedeki isim | Mânâsı | Aslındaki işaretin adı |
| :-- | :-- | :-- |
| Tip | keyfî bir tip | Latin büyük "a" |
| Diğer-tip | ikinci bir tip | Latin büyük "be" |
| Lif | bir tipin unsurlarına bağlı tip ailesi | Latin büyük "be" yahut "a" (aile olarak), Latin büyük "ye" |
| Esas | ihtiyar mütearifesinde ve Yardımcı Kaziyye 3.8.5'te sahayı teşkil eden tip | Latin büyük "iks" |
| Kaziyye, Diğer-kaziyye | mahz kaziyyeler yahut onların aileleri | Latin büyük "pe", "kû" |
| Bağ | (3.2.1)'deki münasebet | Latin büyük "er" |
| Alt | bir tipin alt mecmûası | Latin büyük "be" |
| Kâinat | tiplerin tipi | Latin büyük "u" (el yazısı) |
| $\text{Kâinat}_{\text{derece}}$ | derecesi belli kâinat | "u", altında Latin küçük "i" |
| Tabiî | tabiî adetler tipi | çift çizgili Latin büyük "en" |
| Hükümler | bütün mahz kaziyyeleri sınıflandıran tip | Yunan büyük "omega" |
| Kuvvet | kuvvet mecmûası | el yazısı Latin büyük "pe" |
| $\text{Mecmûa}_{\text{Kâinat}}$, $\text{Kaziyye}_{\text{Kâinat}}$ | bir kâinattaki mecmûalar ve mahz kaziyyeler | "Set", "Prop", altında "u" |
| Kaziyyeler | bütün mahz kaziyyelerin tipi (Temrin 3.9) | "Prop" |
| unsur, öteki, üçüncü | bir tipin unsurları | Latin küçük "iks", "ye", "ze" |
| nokta, diğer-nokta | bir tipin muayyen unsurları | Latin küçük "a", "a üssü" |
| birinci-unsur, ikinci-unsur | Esas'ın iki unsuru | Latin küçük "iks", altında "1" ve "2" |
| seçilen | (3.2.1)'deki seçilen unsur | Latin küçük "a" |
| mebde' | muayyen başlangıç noktası | Latin küçük "iks", altında "0"; Yardımcı Kaziyye 3.3.2'de Latin küçük "iks", altında "0" |
| tarîk, diğer-tarîk, üçüncü-tarîk | ayniyet tipinin hadleri | Latin küçük "pe", "kû", "er" |
| yüksek-tarîk, diğer-yüksek-tarîk | tarîkler arasındaki tarîkler | Latin küçük "er", "es" |
| bağ | büzülme ispatlarındaki yardımcı tarîk | Latin küçük "kû" |
| tâbi, diğer-tâbi | tâbiler | Latin küçük "ef", "ge" |
| gidiş, dönüş | bir tekâfü'ün iki yönü | Latin küçük "ef", "ge" |
| seçici | ihtiyar mütearifesinin verdiği tâbi; Kaziyye 3.2.2'deki farz edilen tâbi | Latin küçük "ge"; Kaziyye 3.2.2'de "ef" |
| çevirme | $\mathbf{2}$'nin unsurlarını yer değiştiren tekâfü' | Latin küçük "e" |
| karar | Netice 3.2.7'deki farz edilen tâbi | Latin küçük "ge" |
| şâhid, diğer-şâhid | bir kaziyyenin şâhidleri | Latin küçük "u", "ve"; Yardımcı Kaziyye 3.11.4'te "ce", "ce üssü" |
| red | bir nefyin şâhidi | Latin küçük "dabılyu" |
| sâdık, kâzib | $\mathbf{2}$'nin iki unsuru | "true", "false" (asılda 1₂, 0₂) |
| merkez, diğer-merkez | büzülme merkezleri | Latin küçük "a", "a altında 0", "be altında 0" |
| $\text{merkez}_{\text{unsur}}$ | $\text{Lif}(\text{unsur})$'un merkezi | Latin küçük "ce", altında "iks" |
| büzülme | büzülme tarîki | "contr" |
| geri-çekme, kesit, telafi | geri çekme, kesiti ve tahavvül-i muttasılı | Latin küçük "er", "es", Yunan küçük "epsilon" |
| asal | asal bir adet | Latin küçük "pe" |
| adet, birinci-adet, ikinci-adet | tabiî adetler | Latin küçük "en", "em" |
| Mütenâhî | mütenâhî tip | "Fin" |
| şifre | tabiî adetlerin tarîklerini tavsif eden tip ailesi | "code" |
| buud-sayısı | tahavvül-i muttasıl tipinin buudu | Latin küçük "en" |
| derece | kâinatın derecesi | Latin küçük "i" |
| mecmûa-mı, kaziyye-mi, büzülebilir-mi | mecmûa olma, mahz kaziyye olma, büzülebilir olma tipleri | "isSet", "isProp", "isContr" |
| tekâfü'-mü, şibh-i-ters | tekâfü' olma ve şibh-i ters tipleri | "isequiv", "qinv" |
| aksiyet | ayniyet tipinin kurucusu | "refl" |
| vahdet | vahdet mütearifesinin verdiği tatbik | "ua" |
| tâbi-genişliği, noktada-tatbik | tâbi genişliği ve onun tersi | "funext", "happly" |
| tatbik, merbût-tatbik | bir tâbinin tarîklere tatbiki | "ap", "apd" |
| nakil | tarîk boyunca nakil | "transport" (asılda yıldız işareti) |
| sol-zerk, sağ-zerk | munfasıl ictimâın kurucuları | "inl", "inr" |
| birinci-izdüşüm, ikinci-izdüşüm | Sigma tipinin izdüşümleri | "pr₁", "pr₂" |
| çift-tarîki, izdüşüm-tarîki | hâsıl-ı zarbda tarîklerin kurulması ve izdüşümü | "pair⁼", "ap pr" |
| ayniyet | ayniyet tâbisi | "id" |
| İmtinâ'-ı-vasat | imtinâ'-ı vasat kanunu | "LEM" |
| İhtiyar | ihtiyar mütearifesi | "AC" |

Ameliye işaretleri (∏, ∑, →, ×, +, ≃, =, ≡, :≡, ¬, ∘, ∙, ⁻¹, ‖ ‖, | |, ∧, ∨, ⇒, ⇔, ∀, ∃, ⊆, ∈, ∩, ∪, ∖, ⊤, ⊥, ⋆) bırakılmıştır.

## Istılah cedveli

Esas: aynı kitabın önsöz ve medhal tercümesinin ıstılah cedveli (`tercume/eserler/03_hott_2013_00_onsoz_ve_medhal.md`) ve `lugat/kok_istilahlar.tsv` (dal `claude/project-thread-jvwo8g`). Her ikisinde de bulunmayanlar **teklif** diye işaretlenmiştir.

| İngilizce | Bu tercümedeki karşılık | Dayanak |
| :-- | :-- | :-- |
| homotopy | tahavvül-i muttasıl | önsöz cedveli |
| type / term | tip / hadd | önsöz cedveli |
| set / n-type | mecmûa / buud-sayısı-tip | önsöz cedveli |
| mere proposition | mahz kaziyye | önsöz cedveli |
| path | tarîk | önsöz cedveli |
| equivalence / equivalent | tekâfü' / mütekâfi | önsöz cedveli |
| isomorphism | temâsül | önsöz cedveli |
| univalence | vahdet | önsöz cedveli |
| universe | kâinat | önsöz cedveli |
| truncation / propositional truncation | kat' / kaziyyevî kat' | önsöz cedveli |
| truncated / untruncated | kat'lı / kat'sız | önsöz cedveli; "kat'sız" teklif |
| axiom of choice | ihtiyar mütearifesi | önsöz cedveli |
| unique choice | yegâne ihtiyar | teklif |
| law of excluded middle | imtinâ'-ı vasat kanunu | önsöz cedveli |
| double negation | çift nefy | kadîm |
| contractible / contractibility | büzülebilir / büzülebilirlik | önsöz cedveli |
| center of contraction / singleton | büzülme merkezi / tekil | teklif |
| predicative / impredicative | tahmîlî / gayr-ı tahmîlî | önsöz cedveli |
| propositional resizing | kaziyyevî yeniden boyutlandırma | önsöz medhali ("kaziyyevî yeniden boyutlandırma mütearifesi") |
| predicate / subset / subtype | mahmûl / alt mecmûa / alt tip | kadîm; teklif |
| power set | kuvvet mecmûası | teklif |
| decidable | karar verilebilir | önsöz medhali ("karar verilebilirliği") |
| inhabited / merely inhabited | meskûn / mahzen meskûn | teklif |
| merely / purely / constructively | mahzen / safiyen / inşâî olarak | teklif; "inşâî" önsöz cedveli |
| modality | cihet | kadîm mantık ıstılahı |
| function extensionality | tâbi genişliği | önsöz medhali ("tâbi genişliği mütearifesi") |
| reflexivity | aksiyet | önsöz medhali |
| transport | nakil | teklif |
| quasi-inverse | şibh-i ters | teklif |
| constructor / type former | kurucu / tip kurucusu | önsöz medhali |
| recursion / induction principle | rücû' / istikrâ prensibi | "istikrâ" önsöz cedveli; "rücû'" teklif |
| case analysis | hâllere ayırma | teklif |
| universal property | küllî hassa | teklif |
| domain / codomain | kalkış sahası / varış sahası | teklif |
| disjunction / existential quantifier | infisâl / vücûdî sûr | kadîm mantık ıstılahları |
| intersection / union / complement | takātu' / ictimâ' / mütemmim | kadîm |
| smash product / wedge | ezik hâsıl-ı zarb / kama | teklif |
| pointed / connected / connectedness | noktalı / muttasıl / ittisal | "muttasıl" önsöz cedveli; diğerleri teklif |
| retraction / section / retract | geri çekme / kesit / geri çekilen | "kesit" önsöz cedveli; diğerleri teklif |
| first-order logic | birinci mertebe mantık | teklif |
| axiom of reducibility | irca' mütearifesi | teklif |
| setoid | mecmûamsı | teklif ("zümremsi" kıyasıyla) |
| bracket type / squash type | köşeli parantez tipi / ezme tipi | teklif |
| proof / theorem / lemma / corollary | ispat / kaziyye / yardımcı kaziyye / netice | önsöz medhali; "netice" teklif |
| definition / remark / example / axiom / exercise | tarif / mülâhaza / misal / mütearife / temrin | önsöz medhali; "mülâhaza" teklif |
| abuse of language | lisan sû-i istimali | önsöz medhali ("işaretin sû-i istimâli") |
