# Muayyen Bir Kemmiyetten Küçük Olan A'dâd-ı Evveliyyenin Adedi Hakkında

**Bernhard Riemann**

*[Berlin İlimler Akademisi'nin Aylık Zabıtları (Monatsberichte der Berliner Akademie), Teşrîn-i sânî 1859.]*

---

> **Künye ve nüsha.** Aslın unvanı: *Ueber die Anzahl der Primzahlen unter einer gegebenen Grösse.* Almanca. İlk neşri: *Monatsberichte der Königlich Preußischen Akademie der Wissenschaften zu Berlin*, Kasım 1859, sahife 671–680. Bu tercümeye esas alınan metin: *Bernhard Riemann's Gesammelte Mathematische Werke und Wissenschaftlicher Nachlass*, Heinrich Weber tarafından Richard Dedekind'in iştirakiyle neşredilmiş, Leipzig, B. G. Teubner, 1892, sahife 145–153; bu metnin David R. Wilkins (Trinity College, Dublin) tarafından 1998'de yapılmış LaTeX istinsahı: <https://www.maths.tcd.ie/pub/HistMath/People/Riemann/Zeta/Zeta.tex>
>
> **Telif hâli.** Müellif 1866'da vefat etmiştir; eser 1859'da neşredilmiştir. Her memlekette umuma açıktır (telifi düşmüştür). Wilkins istinsahı aslın harfi harfine dizgisidir.
>
> **Tercüme usulü.** Metin cümle cümle, hiçbir cümle atlanmadan ve hiçbir şey ilâve edilmeden nakledilmiştir. Mütercimin her ilâvesi metnin içinde değil, sonda **Mütercim kayıtları** babında, numarasıyla verilmiştir; metindeki `[M1]`, `[M2]` … işaretleri o kayıtlara gösterir.
>
> **Düsturların yazılışı.** Padişahın kaidesi mûcibince düsturlarda hiçbir kemmiyet harfle yazılmamış, her biri mânâsını söyleyen bir kelimeyle yazılmıştır ("ağırlık × ehemmiyet = dikkat" gibi; "a × b = c" gibi değil). Riemann'ın harflerinin hangi kelimeyle karşılandığı, sondaki **İsimler cedveli**nde gösterilmiştir. Hesap ameliyeleri (cem', tarh, zarb, taksim, kuvvet, tamâmî, mecmû', hâsıl-ı zarb, hadd) bilinen işaretleriyle bırakılmıştır, zîrâ bunlar kemmiyet değil fiildir.

---

Akademinin, beni muhabir âzâları arasına kabul buyurmak suretiyle bana lâyık gördüğü şerefe karşı şükrânımı, bu vesileyle bahşedilen izinden bir an evvel istifade ederek a'dâd-ı evveliyyenin sıklığı hakkında bir tetkiki arz etmekle en güzel şekilde izhâr edebileceğimi zannediyorum. Bu mevzû, *Gauss* ile *Dirichlet*'nin uzun müddet kendisine göstermiş oldukları alâka sebebiyle, böyle bir arza belki büsbütün nâ-lâyık görünmez.

Bu tetkikte bana hareket noktası olan, *Euler*'in yaptığı şu tesbittir: **evvelî** yerine bütün a'dâd-ı evveliyye, **adet** yerine de bütün tam a'dâd konulduğunda

$$\prod_{\text{evvelî}} \frac{1}{1 - \dfrac{1}{\text{evvelî}^{\,\text{mütehavvil}}}} = \sum_{\text{adet}} \frac{1}{\text{adet}^{\,\text{mütehavvil}}}$$

olur. Bu iki ifadenin, mütekārib oldukları müddetçe temsil ettikleri, mürekkeb **mütehavvil**in tâbisini $\text{Zeta}(\text{mütehavvil})$ ile gösteriyorum. Her ikisi de ancak mütehavvilin hakîkî cüz'ü $1$'den büyük olduğu müddetçe mütekāribdir; maamâfih bu tâbinin daima muteber kalan bir ifadesi kolayca bulunabilir. [M1]

$$\int_0^\infty \text{Neper}^{-\text{adet}\cdot\text{kemmiyet}}\; \text{kemmiyet}^{\,\text{mütehavvil}-1}\; d\,\text{kemmiyet} = \frac{\text{Gauss-zarbı}(\text{mütehavvil} - 1)}{\text{adet}^{\,\text{mütehavvil}}}$$

muâdelesinin tatbikiyle evvelâ

$$\text{Gauss-zarbı}(\text{mütehavvil} - 1)\;\text{Zeta}(\text{mütehavvil}) = \int_0^\infty \frac{\text{kemmiyet}^{\,\text{mütehavvil}-1}\; d\,\text{kemmiyet}}{\text{Neper}^{\,\text{kemmiyet}} - 1}$$

elde edilir.

Şimdi

$$\int \frac{(-\text{kemmiyet})^{\text{mütehavvil}-1}\; d\,\text{kemmiyet}}{\text{Neper}^{\,\text{kemmiyet}} - 1}$$

tamâmîsini, $+\infty$'dan $+\infty$'a kadar, öyle bir kemmiyet sahasının etrafında müsbet istikamette uzatılmış olarak mülâhaza edelim ki bu saha $0$ kıymetini ihtivâ etsin, fakat tamâmî işaretinin altındaki tâbinin başka hiçbir inkıtâ' kıymetini içinde barındırmasın. Bu tamâmînin kolayca

$$\left(\text{Neper}^{-\text{dâire-nisbeti}\cdot\text{mütehavvil}\cdot\text{mevhûm-vâhid}} - \text{Neper}^{\,\text{dâire-nisbeti}\cdot\text{mütehavvil}\cdot\text{mevhûm-vâhid}}\right) \int_0^\infty \frac{\text{kemmiyet}^{\,\text{mütehavvil}-1}\; d\,\text{kemmiyet}}{\text{Neper}^{\,\text{kemmiyet}} - 1}$$

ifadesine müsâvî olduğu görülür; şu şartla ki çok kıymetli

$$(-\text{kemmiyet})^{\text{mütehavvil}-1} = \text{Neper}^{(\text{mütehavvil}-1)\,\text{logaritma}(-\text{kemmiyet})}$$

tâbisinde eksi kemmiyetin logaritması, menfî bir kemmiyet için hakîkî olacak şekilde tayin edilmiş olsun. Binâenaleyh, tamâmî demin beyan edilen mânâda anlaşılmak üzere,

$$2\,\text{ceyb}(\text{dâire-nisbeti}\cdot\text{mütehavvil})\;\text{Gauss-zarbı}(\text{mütehavvil} - 1)\;\text{Zeta}(\text{mütehavvil}) = \text{mevhûm-vâhid} \int_\infty^\infty \frac{(-\text{kemmiyet})^{\text{mütehavvil}-1}\; d\,\text{kemmiyet}}{\text{Neper}^{\,\text{kemmiyet}} - 1}$$

elde edilir. [M2]

Bu muâdele artık Zeta tâbisinin her keyfî mürekkeb mütehavvil için kıymetini verir ve gösterir ki bu tâbi tek kıymetlidir ve $1$ müstesnâ olmak üzere mütehavvilin bütün mütenâhî kıymetleri için mütenâhîdir; keza mütehavvil menfî bir çift adede müsâvî olduğunda sıfır olur.

Mütehavvilin hakîkî cüz'ü menfî olduğunda tamâmî, belirtilen kemmiyet sahası etrafında müsbet istikamette alınacağı yerde, geri kalan bütün mürekkeb kemmiyetleri ihtivâ eden kemmiyet sahası etrafında menfî istikamette de uzatılabilir; zîrâ o hâlde tamâmî, mikyâsı nihâyetsiz büyük olan kıymetler üzerinden alındığında nihâyetsiz küçüktür. Fakat bu kemmiyet sahasının içinde, tamâmî işaretinin altındaki tâbi ancak kemmiyet, $\pm 2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}$'in tam bir katına müsâvî olduğunda munkatı' olur; binâenaleyh tamâmî, bu kıymetlerin etrafında menfî istikamette alınan tamâmîlerin mecmû'una müsâvîdir. $\text{adet}\cdot 2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}$ kıymeti etrafındaki tamâmî ise

$$\left(-\text{adet}\cdot 2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}\right)^{\text{mütehavvil}-1}\left(-2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}\right)$$

kadardır. Bu sebeple

$$2\,\text{ceyb}(\text{dâire-nisbeti}\cdot\text{mütehavvil})\;\text{Gauss-zarbı}(\text{mütehavvil} - 1)\;\text{Zeta}(\text{mütehavvil}) = (2\,\text{dâire-nisbeti})^{\text{mütehavvil}} \sum_{\text{adet}} \text{adet}^{\,\text{mütehavvil}-1}\left((-\text{mevhûm-vâhid})^{\text{mütehavvil}-1} + \text{mevhûm-vâhid}^{\,\text{mütehavvil}-1}\right)$$

elde edilir; yâni $\text{Zeta}(\text{mütehavvil})$ ile $\text{Zeta}(1 - \text{mütehavvil})$ arasında bir münasebet ki, Gauss-zarbı tâbisinin malûm hassalarından istifade edilerek şöyle de ifade olunabilir:

$$\text{Gauss-zarbı}\!\left(\frac{\text{mütehavvil}}{2} - 1\right) \text{dâire-nisbeti}^{-\frac{\text{mütehavvil}}{2}}\;\text{Zeta}(\text{mütehavvil})$$

ifadesi, mütehavvil yerine $1 - \text{mütehavvil}$ konulduğunda değişmeden kalır. [M3]

Tâbinin bu hassası, beni, $\sum_{\text{adet}} \dfrac{1}{\text{adet}^{\,\text{mütehavvil}}}$ silsilesinin umûmî haddine $\text{Gauss-zarbı}(\text{mütehavvil} - 1)$ yerine $\text{Gauss-zarbı}\!\left(\dfrac{\text{mütehavvil}}{2} - 1\right)$ tamâmîsini idhâl etmeye sevk etti; bu suretle Zeta tâbisinin pek elverişli bir ifadesi elde edilir. Filhakika

$$\frac{1}{\text{adet}^{\,\text{mütehavvil}}}\;\text{Gauss-zarbı}\!\left(\frac{\text{mütehavvil}}{2} - 1\right) \text{dâire-nisbeti}^{-\frac{\text{mütehavvil}}{2}} = \int_0^\infty \text{Neper}^{-\text{adet}\cdot\text{adet}\cdot\text{dâire-nisbeti}\cdot\text{kemmiyet}}\; \text{kemmiyet}^{\frac{\text{mütehavvil}}{2} - 1}\; d\,\text{kemmiyet}$$

olur; binâenaleyh

$$\sum_{\text{adet}=1}^{\infty} \text{Neper}^{-\text{adet}\cdot\text{adet}\cdot\text{dâire-nisbeti}\cdot\text{kemmiyet}} = \text{Jacobi-mecmûu}(\text{kemmiyet})$$

konulursa

$$\text{Gauss-zarbı}\!\left(\frac{\text{mütehavvil}}{2} - 1\right) \text{dâire-nisbeti}^{-\frac{\text{mütehavvil}}{2}}\;\text{Zeta}(\text{mütehavvil}) = \int_0^\infty \text{Jacobi-mecmûu}(\text{kemmiyet})\; \text{kemmiyet}^{\frac{\text{mütehavvil}}{2} - 1}\; d\,\text{kemmiyet}$$

olur; yahut

$$2\,\text{Jacobi-mecmûu}(\text{kemmiyet}) + 1 = \text{kemmiyet}^{-\frac{1}{2}} \left( 2\,\text{Jacobi-mecmûu}\!\left(\frac{1}{\text{kemmiyet}}\right) + 1 \right) \quad \text{(Jacobi, Fundamenta, sahife 184)}$$

olduğundan [M4]

$$\begin{aligned}
\text{Gauss-zarbı}\!\left(\frac{\text{mütehavvil}}{2} - 1\right) \text{dâire-nisbeti}^{-\frac{\text{mütehavvil}}{2}}\;\text{Zeta}(\text{mütehavvil})
&= \int_1^\infty \text{Jacobi-mecmûu}(\text{kemmiyet})\; \text{kemmiyet}^{\frac{\text{mütehavvil}}{2} - 1}\; d\,\text{kemmiyet} \\
&\quad + \int_1^\infty \text{Jacobi-mecmûu}\!\left(\frac{1}{\text{kemmiyet}}\right) \text{kemmiyet}^{\frac{\text{mütehavvil}-3}{2}}\; d\,\text{kemmiyet} \\
&\quad + \tfrac{1}{2} \int_0^1 \left( \text{kemmiyet}^{\frac{\text{mütehavvil}-3}{2}} - \text{kemmiyet}^{\frac{\text{mütehavvil}}{2} - 1} \right) d\,\text{kemmiyet} \\
&= \frac{1}{\text{mütehavvil}\,(\text{mütehavvil}-1)} + \int_1^\infty \text{Jacobi-mecmûu}(\text{kemmiyet}) \left( \text{kemmiyet}^{\frac{\text{mütehavvil}}{2} - 1} + \text{kemmiyet}^{-\frac{1+\text{mütehavvil}}{2}} \right) d\,\text{kemmiyet}
\end{aligned}$$

olur.

Şimdi $\text{mütehavvil} = \tfrac{1}{2} + \text{irtifâ}\cdot\text{mevhûm-vâhid}$ koyuyorum ve

$$\text{Gauss-zarbı}\!\left(\frac{\text{mütehavvil}}{2}\right)(\text{mütehavvil} - 1)\; \text{dâire-nisbeti}^{-\frac{\text{mütehavvil}}{2}}\;\text{Zeta}(\text{mütehavvil}) = \text{Tekmîl-zeta}(\text{irtifâ})$$

diyorum; öyle ki

$$\text{Tekmîl-zeta}(\text{irtifâ}) = \tfrac{1}{2} - \left(\text{irtifâ}\cdot\text{irtifâ} + \tfrac{1}{4}\right) \int_1^\infty \text{Jacobi-mecmûu}(\text{kemmiyet})\; \text{kemmiyet}^{-\frac{3}{4}}\; \text{ceyb-i tamâm}\!\left(\tfrac{1}{2}\,\text{irtifâ}\; \text{logaritma}(\text{kemmiyet})\right) d\,\text{kemmiyet}$$

yahut

$$\text{Tekmîl-zeta}(\text{irtifâ}) = 4 \int_1^\infty \frac{d\left(\text{kemmiyet}^{\frac{3}{2}}\; \dfrac{d\,\text{Jacobi-mecmûu}(\text{kemmiyet})}{d\,\text{kemmiyet}}\right)}{d\,\text{kemmiyet}}\; \text{kemmiyet}^{-\frac{1}{4}}\; \text{ceyb-i tamâm}\!\left(\tfrac{1}{2}\,\text{irtifâ}\; \text{logaritma}(\text{kemmiyet})\right) d\,\text{kemmiyet}$$

olur.

Bu tâbi irtifânın bütün mütenâhî kıymetleri için mütenâhîdir ve $\text{irtifâ}\cdot\text{irtifâ}$'nın kuvvetlerine göre pek süratle mütekārib bir silsileye inkişâf ettirilebilir. Hakîkî cüz'ü $1$'den büyük olan bir mütehavvil kıymeti için

$$\text{logaritma}\,\text{Zeta}(\text{mütehavvil}) = -\sum_{\text{evvelî}} \text{logaritma}\left(1 - \text{evvelî}^{-\text{mütehavvil}}\right)$$

mütenâhî kaldığından ve Tekmîl-zeta tâbisinin diğer mazrûblarının logaritmaları için de aynı hüküm sâdık olduğundan, Tekmîl-zeta tâbisi ancak irtifânın mevhûm cüz'ü $\tfrac{1}{2}\,\text{mevhûm-vâhid}$ ile $-\tfrac{1}{2}\,\text{mevhûm-vâhid}$ arasında bulunduğunda sıfır olabilir. $\text{Tekmîl-zeta}(\text{irtifâ}) = 0$ muâdelesinin, hakîkî cüz'ü $0$ ile **hudut-irtifâ** arasında bulunan cezrlerinin adedi takrîben

$$= \frac{\text{hudut-irtifâ}}{2\,\text{dâire-nisbeti}}\; \text{logaritma}\frac{\text{hudut-irtifâ}}{2\,\text{dâire-nisbeti}} - \frac{\text{hudut-irtifâ}}{2\,\text{dâire-nisbeti}}$$

kadardır; zîrâ $\int d\, \text{logaritma}\,\text{Tekmîl-zeta}(\text{irtifâ})$ tamâmîsi, mevhûm cüz'ü $\tfrac{1}{2}\,\text{mevhûm-vâhid}$ ile $-\tfrac{1}{2}\,\text{mevhûm-vâhid}$ arasında ve hakîkî cüz'ü $0$ ile hudut-irtifâ arasında bulunan irtifâ kıymetlerinin heyet-i mecmûası etrafında müsbet istikamette uzatıldığında, ($\dfrac{1}{\text{hudut-irtifâ}}$ kemmiyeti mertebesinden bir kesir farkıyla)

$$\left( \text{hudut-irtifâ}\; \text{logaritma}\frac{\text{hudut-irtifâ}}{2\,\text{dâire-nisbeti}} - \text{hudut-irtifâ} \right) \text{mevhûm-vâhid}$$

kıymetine müsâvîdir; bu tamâmî ise bu sahada bulunan $\text{Tekmîl-zeta}(\text{irtifâ}) = 0$ cezrlerinin adedinin $2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}$ ile zarbına müsâvîdir. Filhakika bu hudutlar dâhilinde takrîben bu kadar hakîkî cezr bulunur ve bütün cezrlerin hakîkî olması pek muhtemeldir. Bunun kat'î bir burhânı elbette arzu olunurdu; maamâfih ben, birkaç sathî ve neticesiz teşebbüsten sonra, onu aramayı şimdilik bir tarafa bıraktım, zîrâ tetkikimin yakın maksadı için ona ihtiyaç yok gibi görünüyordu. [M5]

$\text{Tekmîl-zeta}(\text{cezr}) = 0$ muâdelesinin her cezri **cezr** ile gösterilirse, $\text{logaritma}\,\text{Tekmîl-zeta}(\text{irtifâ})$

$$\sum_{\text{cezr}} \text{logaritma}\left(1 - \frac{\text{irtifâ}\cdot\text{irtifâ}}{\text{cezr}\cdot\text{cezr}}\right) + \text{logaritma}\,\text{Tekmîl-zeta}(0)$$

ile ifade olunabilir; zîrâ irtifâ büyüklüğündeki cezrlerin kesâfeti irtifâ ile ancak $\text{logaritma}\dfrac{\text{irtifâ}}{2\,\text{dâire-nisbeti}}$ gibi arttığından bu ifade mütekāribdir ve nihâyetsiz bir irtifâ için ancak $\text{irtifâ}\;\text{logaritma}(\text{irtifâ})$ gibi nihâyetsiz olur; binâenaleyh $\text{logaritma}\,\text{Tekmîl-zeta}(\text{irtifâ})$'dan, ancak $\text{irtifâ}\cdot\text{irtifâ}$'nın bir tâbisi kadar farklıdır ki bu tâbi mütenâhî bir irtifâ için muttasıl ve mütenâhî kalır ve $\text{irtifâ}\cdot\text{irtifâ}$'ya taksim edildiğinde nihâyetsiz bir irtifâ için nihâyetsiz küçük olur. Bu fark, netice itibarıyla, kıymeti $\text{irtifâ} = 0$ konularak tayin olunabilen bir sâbittir.

Bu yardımcı vasıtalarla artık bir **hudut**tan küçük olan a'dâd-ı evveliyyenin adedi tayin edilebilir.

Hudut tam bir adet-i evvelîye müsâvî olmadığında $\text{Evvelî-adedi}(\text{hudut})$ bu adede müsâvî olsun; hudut bir adet-i evvelî olduğunda ise ondan $\tfrac{1}{2}$ fazla olsun; öyle ki Evvelî-adedi tâbisinin sıçrayarak değiştiği bir hudut için

$$\text{Evvelî-adedi}(\text{hudut}) = \frac{\text{Evvelî-adedi}(\text{hudut} + 0) + \text{Evvelî-adedi}(\text{hudut} - 0)}{2}$$

olsun. [M6]

Şimdi

$$\text{logaritma}\,\text{Zeta}(\text{mütehavvil}) = -\sum_{\text{evvelî}} \text{logaritma}\left(1 - \text{evvelî}^{-\text{mütehavvil}}\right) = \sum_{\text{evvelî}} \text{evvelî}^{-\text{mütehavvil}} + \tfrac{1}{2} \sum_{\text{evvelî}} \text{evvelî}^{-2\,\text{mütehavvil}} + \tfrac{1}{3} \sum_{\text{evvelî}} \text{evvelî}^{-3\,\text{mütehavvil}} + \cdots$$

ifadesinde

$$\text{evvelî}^{-\text{mütehavvil}} \text{ yerine } \text{mütehavvil} \int_{\text{evvelî}}^\infty \text{kemmiyet}^{-\text{mütehavvil}-1}\; d\,\text{mütehavvil}, \qquad \text{evvelî}^{-2\,\text{mütehavvil}} \text{ yerine } \text{mütehavvil} \int_{\text{evvelî}^2}^\infty \text{kemmiyet}^{-\text{mütehavvil}-1}\; d\,\text{mütehavvil}, \;\ldots$$

konulursa, [M7]

$$\text{Evvelî-adedi}(\text{hudut}) + \tfrac{1}{2}\, \text{Evvelî-adedi}\big(\text{hudut}^{\frac{1}{2}}\big) + \tfrac{1}{3}\, \text{Evvelî-adedi}\big(\text{hudut}^{\frac{1}{3}}\big) + \cdots$$

ifadesi $\text{Kuvvet-adedi}(\text{hudut})$ ile gösterildiği takdirde

$$\frac{\text{logaritma}\,\text{Zeta}(\text{mütehavvil})}{\text{mütehavvil}} = \int_1^\infty \text{Kuvvet-adedi}(\text{kemmiyet})\; \text{kemmiyet}^{-\text{mütehavvil}-1}\; d\,\text{kemmiyet}$$

elde edilir.

Bu muâdele, $\text{hakîkî-cüz} > 1$ olduğu müddetçe, mütehavvilin her mürekkeb $\text{hakîkî-cüz} + \text{mevhûm-cüz}\cdot\text{mevhûm-vâhid}$ kıymeti için muteberdir. Fakat bu vüs'atte

$$\text{Sûret}(\text{mütehavvil}) = \int_0^\infty \text{Asıl}(\text{kemmiyet})\; \text{kemmiyet}^{-\text{mütehavvil}}\; d\, \text{logaritma}(\text{kemmiyet})$$

muâdelesi sâdık ise, *Fourier* kaziyyesinin yardımıyla **Asıl** tâbisi **Sûret** tâbisi vasıtasıyla ifade olunabilir. $\text{Asıl}(\text{kemmiyet})$ hakîkî olduğunda ve

$$\text{Sûret}(\text{hakîkî-cüz} + \text{mevhûm-cüz}\cdot\text{mevhûm-vâhid}) = \text{Sûret-hakîkî}(\text{mevhûm-cüz}) + \text{mevhûm-vâhid}\;\text{Sûret-mevhûm}(\text{mevhûm-cüz})$$

olduğunda muâdele şu iki muâdeleye ayrılır:

$$\text{Sûret-hakîkî}(\text{mevhûm-cüz}) = \int_0^\infty \text{Asıl}(\text{kemmiyet})\; \text{kemmiyet}^{-\text{hakîkî-cüz}}\; \text{ceyb-i tamâm}\big(\text{mevhûm-cüz}\; \text{logaritma}(\text{kemmiyet})\big)\; d\, \text{logaritma}(\text{kemmiyet}),$$

$$\text{mevhûm-vâhid}\;\text{Sûret-mevhûm}(\text{mevhûm-cüz}) = -\text{mevhûm-vâhid} \int_0^\infty \text{Asıl}(\text{kemmiyet})\; \text{kemmiyet}^{-\text{hakîkî-cüz}}\; \text{ceyb}\big(\text{mevhûm-cüz}\; \text{logaritma}(\text{kemmiyet})\big)\; d\, \text{logaritma}(\text{kemmiyet}).$$

Her iki muâdele

$$\Big(\text{ceyb-i tamâm}\big(\text{mevhûm-cüz}\; \text{logaritma}(\text{nokta})\big) + \text{mevhûm-vâhid}\;\text{ceyb}\big(\text{mevhûm-cüz}\; \text{logaritma}(\text{nokta})\big)\Big)\; d\,\text{mevhûm-cüz}$$

ile zarb edilir ve $-\infty$'dan $+\infty$'a kadar tamâmlanırsa, *Fourier* kaziyyesi mûcibince her ikisinde de sağ tarafta $\text{dâire-nisbeti}\;\text{Asıl}(\text{nokta})\;\text{nokta}^{-\text{hakîkî-cüz}}$ elde edilir; binâenaleyh her iki muâdele cem' edilip $\text{mevhûm-vâhid}\;\text{nokta}^{\,\text{hakîkî-cüz}}$ ile zarb edilirse [M8]

$$2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}\;\text{Asıl}(\text{nokta}) = \int_{\text{hakîkî-cüz} - \infty\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \infty\cdot\text{mevhûm-vâhid}} \text{Sûret}(\text{mütehavvil})\; \text{nokta}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil}$$

olur; burada tamâmlama, mütehavvilin hakîkî cüz'ü sâbit kalacak şekilde icra edilmelidir.

Bu tamâmî, Asıl tâbisinde sıçramalı bir değişmenin vuku bulduğu bir nokta için, Asıl tâbisinin sıçramanın iki tarafındaki kıymetlerinin vasatî kıymetini temsil eder. Kuvvet-adedi tâbisinin burada farz edilen tayin tarzında bu tâbi de aynı hassaya sahiptir; ve binâenaleyh tamamıyla umûmî olarak

$$\text{Kuvvet-adedi}(\text{nokta}) = \frac{1}{2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}} \int_{\text{hakîkî-cüz} - \infty\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \infty\cdot\text{mevhûm-vâhid}} \frac{\text{logaritma}\,\text{Zeta}(\text{mütehavvil})}{\text{mütehavvil}}\; \text{nokta}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil}$$

elde edilir.

$\text{logaritma}\,\text{Zeta}$ yerine artık evvelce bulunan

$$\frac{\text{mütehavvil}}{2}\, \text{logaritma}(\text{dâire-nisbeti}) - \text{logaritma}(\text{mütehavvil} - 1) - \text{logaritma}\,\text{Gauss-zarbı}\!\left(\frac{\text{mütehavvil}}{2}\right) + \sum_{\text{cezr}} \text{logaritma}\left(1 + \frac{\left(\text{mütehavvil} - \frac{1}{2}\right)^2}{\text{cezr}\cdot\text{cezr}}\right) + \text{logaritma}\,\text{Tekmîl-zeta}(0)$$

ifadesi ikame edilebilir. Fakat bu ifadenin ayrı ayrı haddlerinin tamâmîleri nihâyetsize uzatıldıklarında mütekārib olmazlar; bu sebeple muâdeleyi evvelden cüz cüz tamâmlama ile

$$\text{Kuvvet-adedi}(\text{hudut}) = -\frac{1}{2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}}\; \frac{1}{\text{logaritma}(\text{hudut})} \int_{\text{hakîkî-cüz} - \infty\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \infty\cdot\text{mevhûm-vâhid}} \frac{d \dfrac{\text{logaritma}\,\text{Zeta}(\text{mütehavvil})}{\text{mütehavvil}}}{d\,\text{mütehavvil}}\; \text{hudut}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil}$$

şekline sokmak münasiptir.

$\text{son-adet} = \infty$ için

$$-\text{logaritma}\,\text{Gauss-zarbı}\!\left(\frac{\text{mütehavvil}}{2}\right) = \lim \left( \sum_{\text{adet}=1}^{\text{adet}=\text{son-adet}} \text{logaritma}\left(1 + \frac{\text{mütehavvil}}{2\,\text{adet}}\right) - \frac{\text{mütehavvil}}{2}\, \text{logaritma}(\text{son-adet}) \right)$$

olduğundan, binâenaleyh

$$-\frac{d \left(\dfrac{1}{\text{mütehavvil}}\, \text{logaritma}\,\text{Gauss-zarbı}\!\left(\dfrac{\text{mütehavvil}}{2}\right)\right)}{d\,\text{mütehavvil}} = \sum_{\text{adet}=1}^\infty \frac{d \left(\dfrac{1}{\text{mütehavvil}}\, \text{logaritma}\left(1 + \dfrac{\text{mütehavvil}}{2\,\text{adet}}\right)\right)}{d\,\text{mütehavvil}}$$

olduğundan, Kuvvet-adedi ifadesinin bütün haddleri,

$$\frac{1}{2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}}\; \frac{1}{\text{logaritma}(\text{hudut})} \int_{\text{hakîkî-cüz} - \infty\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \infty\cdot\text{mevhûm-vâhid}} \frac{1}{\text{mütehavvil}\cdot\text{mütehavvil}}\; \text{logaritma}\,\text{Tekmîl-zeta}(0)\; \text{hudut}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil} = \text{logaritma}\,\text{Tekmîl-zeta}(0)$$

müstesnâ olmak üzere,

$$\pm \frac{1}{2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}}\; \frac{1}{\text{logaritma}(\text{hudut})} \int_{\text{hakîkî-cüz} - \infty\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \infty\cdot\text{mevhûm-vâhid}} \frac{d\left( \dfrac{1}{\text{mütehavvil}}\, \text{logaritma}\left(1 - \dfrac{\text{mütehavvil}}{\text{umûmî-cezr}}\right) \right)}{d\,\text{mütehavvil}}\; \text{hudut}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil}$$

şeklini alır.

Halbuki

$$\frac{d\left( \dfrac{1}{\text{mütehavvil}}\, \text{logaritma}\left(1 - \dfrac{\text{mütehavvil}}{\text{umûmî-cezr}}\right) \right)}{d\,\text{umûmî-cezr}} = \frac{1}{(\text{umûmî-cezr} - \text{mütehavvil})\;\text{umûmî-cezr}}$$

olup, mütehavvilin hakîkî cüz'ü umûmî-cezrin hakîkî cüz'ünden büyük olduğunda

$$-\frac{1}{2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}} \int_{\text{hakîkî-cüz} - \infty\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \infty\cdot\text{mevhûm-vâhid}} \frac{\text{hudut}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil}}{(\text{umûmî-cezr} - \text{mütehavvil})\;\text{umûmî-cezr}} = \frac{\text{hudut}^{\,\text{umûmî-cezr}}}{\text{umûmî-cezr}} = \int_\infty^{\text{hudut}} \text{kemmiyet}^{\,\text{umûmî-cezr} - 1}\; d\,\text{kemmiyet},$$

yahut

$$= \int_0^{\text{hudut}} \text{kemmiyet}^{\,\text{umûmî-cezr} - 1}\; d\,\text{kemmiyet}$$

olur; hangisinin olacağı, umûmî-cezrin hakîkî cüz'ünün menfî yahut müsbet oluşuna bağlıdır. Binâenaleyh

$$\frac{1}{2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}}\; \frac{1}{\text{logaritma}(\text{hudut})} \int_{\text{hakîkî-cüz} - \infty\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \infty\cdot\text{mevhûm-vâhid}} \frac{d\left( \dfrac{1}{\text{mütehavvil}}\, \text{logaritma}\left(1 - \dfrac{\text{mütehavvil}}{\text{umûmî-cezr}}\right) \right)}{d\,\text{mütehavvil}}\; \text{hudut}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil}$$

$$\begin{aligned}
&= -\frac{1}{2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}} \int_{\text{hakîkî-cüz} - \infty\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \infty\cdot\text{mevhûm-vâhid}} \frac{1}{\text{mütehavvil}}\, \text{logaritma}\left(1 - \frac{\text{mütehavvil}}{\text{umûmî-cezr}}\right) \text{hudut}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil} \\
&= \int_\infty^{\text{hudut}} \frac{\text{kemmiyet}^{\,\text{umûmî-cezr} - 1}}{\text{logaritma}(\text{kemmiyet})}\; d\,\text{kemmiyet} + \text{sâbit, birinci hâlde,}
\end{aligned}$$

ve

$$= \int_0^{\text{hudut}} \frac{\text{kemmiyet}^{\,\text{umûmî-cezr} - 1}}{\text{logaritma}(\text{kemmiyet})}\; d\,\text{kemmiyet} + \text{sâbit, ikinci hâlde}$$

elde edilir.

Birinci hâlde tamâmlama sâbiti, umûmî-cezrin hakîkî cüz'ü menfî tarafta nihâyetsiz kılınarak tayin olunur. İkinci hâlde ise $0$'dan hududa kadar olan tamâmî, tamâmlamanın kavsi müsbet yahut menfî olan mürekkeb kıymetler üzerinden yapılmasına göre $2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}$ kadar farklı kıymetler alır; ve evvelki yoldan alındığında, umûmî-cezr kıymetindeki mevhûm vâhidin emsali müsbet tarafta nihâyetsiz olduğunda, sonraki yoldan alındığında ise bu emsal menfî tarafta nihâyetsiz olduğunda nihâyetsiz küçük olur. Buradan, tamâmlama sâbitinin düşmesi için sol tarafta $\text{logaritma}\left(1 - \dfrac{\text{mütehavvil}}{\text{umûmî-cezr}}\right)$'nın nasıl tayin edilmesi lâzım geldiği anlaşılır. [M9]

Bu kıymetler Kuvvet-adedi ifadesine konulursa

$$\begin{aligned}
\text{Kuvvet-adedi}(\text{hudut}) = {}& \text{Logaritmik-tamâmî}(\text{hudut}) - \sum_{\text{cezr}} \left( \text{Logaritmik-tamâmî}\!\left(\text{hudut}^{\frac{1}{2} + \text{cezr}\cdot\text{mevhûm-vâhid}}\right) + \text{Logaritmik-tamâmî}\!\left(\text{hudut}^{\frac{1}{2} - \text{cezr}\cdot\text{mevhûm-vâhid}}\right) \right) \\
& + \int_{\text{hudut}}^\infty \frac{1}{\text{kemmiyet}^2 - 1}\; \frac{d\,\text{kemmiyet}}{\text{kemmiyet}\;\text{logaritma}(\text{kemmiyet})} + \text{logaritma}\,\text{Tekmîl-zeta}(0)
\end{aligned}$$

elde edilir; şu şartla ki cezrler üzerinden alınan mecmû'da cezr yerine $\text{Tekmîl-zeta}(\text{cezr}) = 0$ muâdelesinin bütün müsbet (yahut müsbet bir hakîkî cüz ihtivâ eden) cezrleri, büyüklüklerine göre sıralanmış olarak konulsun. [M10] Tekmîl-zeta tâbisinin daha dakik bir münakaşası yardımıyla kolayca gösterilebilir ki, bu sıralamada

$$\sum_{\text{cezr}} \left( \text{Logaritmik-tamâmî}\!\left(\text{hudut}^{\frac{1}{2} + \text{cezr}\cdot\text{mevhûm-vâhid}}\right) + \text{Logaritmik-tamâmî}\!\left(\text{hudut}^{\frac{1}{2} - \text{cezr}\cdot\text{mevhûm-vâhid}}\right) \right) \text{logaritma}(\text{hudut})$$

silsilesinin kıymeti,

$$\frac{1}{2\,\text{dâire-nisbeti}\cdot\text{mevhûm-vâhid}} \int_{\text{hakîkî-cüz} - \text{mevhûm-cüz}\cdot\text{mevhûm-vâhid}}^{\text{hakîkî-cüz} + \text{mevhûm-cüz}\cdot\text{mevhûm-vâhid}} \frac{d \left(\dfrac{1}{\text{mütehavvil}} \displaystyle\sum_{\text{cezr}} \text{logaritma}\left(1 + \dfrac{\left(\text{mütehavvil} - \frac{1}{2}\right)^2}{\text{cezr}\cdot\text{cezr}}\right)\right)}{d\,\text{mütehavvil}}\; \text{hudut}^{\,\text{mütehavvil}}\; d\,\text{mütehavvil}$$

ifadesinin, mevhûm-cüz kemmiyeti durmaksızın arttıkça yaklaştığı hadd kıymetiyle mutabıktır; fakat sıralama değiştirilirse silsile her keyfî hakîkî kıymeti alabilirdi.

Kuvvet-adedi tâbisinden Evvelî-adedi tâbisi,

$$\text{Kuvvet-adedi}(\text{hudut}) = \sum_{\text{adet}} \frac{1}{\text{adet}}\; \text{Evvelî-adedi}\big(\text{hudut}^{\frac{1}{\text{adet}}}\big)$$

münasebetinin tersine çevrilmesinden hâsıl olan

$$\text{Evvelî-adedi}(\text{hudut}) = \sum_{\text{murabbasız}} (-1)^{\text{mazrûb-sayısı}}\; \frac{1}{\text{murabbasız}}\; \text{Kuvvet-adedi}\big(\text{hudut}^{\frac{1}{\text{murabbasız}}}\big)$$

muâdelesi vasıtasıyla bulunur; burada **murabbasız** yerine sırasıyla, $1$'den başka hiçbir murabbaa taksim olunamayan a'dâd konulmalıdır ve **mazrûb-sayısı**, o adedin evvelî mazrûblarının adedini gösterir. [M11]

Cezrler üzerinden alınan mecmû' mütenâhî adette hadde hasredilirse, Kuvvet-adedi ifadesinin müştakkı, yahut, hudut arttıkça pek süratle azalan bir cüz' hâriç tutulursa,

$$\frac{1}{\text{logaritma}(\text{hudut})} - 2 \sum_{\text{cezr}} \frac{\text{ceyb-i tamâm}\big(\text{cezr}\; \text{logaritma}(\text{hudut})\big)\; \text{hudut}^{-\frac{1}{2}}}{\text{logaritma}(\text{hudut})}$$

ifadesi; hudut büyüklüğündeki a'dâd-ı evveliyyenin kesâfeti, artı evvelî murabbaların kesâfetinin yarısı, artı evvelî mükâabların kesâfetinin üçte biri, ve bu minvâl üzere devam eden mecmû' için takrîbî bir ifade verir.

Binâenaleyh malûm

$$\text{Evvelî-adedi}(\text{hudut}) = \text{Logaritmik-tamâmî}(\text{hudut})$$

takrîb düstûru ancak $\text{hudut}^{\frac{1}{2}}$ mertebesinden kemmiyetlere kadar doğrudur ve biraz fazla büyük bir kıymet verir; zîrâ Evvelî-adedi ifadesindeki devrî olmayan haddler, hudut ile nihâyetsize doğru artmayan kemmiyetler bir tarafa bırakılırsa, şunlardır:

$$\text{Logaritmik-tamâmî}(\text{hudut}) - \tfrac{1}{2}\, \text{Logaritmik-tamâmî}\big(\text{hudut}^{\frac{1}{2}}\big) - \tfrac{1}{3}\, \text{Logaritmik-tamâmî}\big(\text{hudut}^{\frac{1}{3}}\big) - \tfrac{1}{5}\, \text{Logaritmik-tamâmî}\big(\text{hudut}^{\frac{1}{5}}\big) + \tfrac{1}{6}\, \text{Logaritmik-tamâmî}\big(\text{hudut}^{\frac{1}{6}}\big) - \tfrac{1}{7}\, \text{Logaritmik-tamâmî}\big(\text{hudut}^{\frac{1}{7}}\big) + \cdots$$

Filhakika *Gauss* ve *Goldschmidt* tarafından yapılıp hudut = üç milyona kadar devam ettirilen, Logaritmik-tamâmî kıymetinin hududdan küçük a'dâd-ı evveliyyenin adediyle mukayesesinde, bu adet daha birinci yüz binden itibaren daima Logaritmik-tamâmî kıymetinden küçük çıkmıştır; ve fark, birtakım dalgalanmalarla beraber, hudut ile tedricen artmaktadır. Fakat devrî haddlere bağlı olan, a'dâd-ı evveliyyenin yer yer sıklaşması ve seyrekleşmesi de sayımlarda nazar-ı dikkati celbetmiş, ancak bunda bir kanuniyet fark edilmemiştir. İleride yapılabilecek yeni bir sayımda, a'dâd-ı evveliyyenin kesâfeti için verilen ifadede bulunan ayrı ayrı devrî haddlerin tesirini takip etmek alâka çekici olurdu. Evvelî-adedi tâbisinden daha muntazam bir seyri Kuvvet-adedi tâbisi gösterirdi; bu tâbinin daha birinci yüz içinde, vasatî olarak

$$\text{Logaritmik-tamâmî}(\text{hudut}) + \text{logaritma}\,\text{Tekmîl-zeta}(0)$$

ile mutabık olduğu pek açık bir surette görülür. [M12]

---

## Mütercim kayıtları

Bu kayıtlar aslın parçası değildir; okuyanın aslı daha kolay takip etmesi için mütercim tarafından yazılmıştır. Her biri, hangi hükmün aslından, hangisinin mütercimin kendi bilgisinden olduğunu açıkça söyler.

**[M1] Gauss-zarbı.** Riemann, *Gauss*'un tâbisini kullanır; bugün bu tâbinin bir adım kaydırılmışı "gamma tâbisi" diye anılır: $\text{Gauss-zarbı}(\text{adet}) = 1 \cdot 2 \cdot 3 \cdots \text{adet}$ (tam a'dâd için). Bu tâbi, bir adede kadar olan bütün tam a'dâdın hâsıl-ı zarbını, kesirli ve mürekkeb kıymetlere de yayar; adını bu sebeple "Gauss-zarbı" koyduk.

**[M2] Sonsuzdan sonsuza tamâmî.** Burada kastedilen, müsbet hakîkî mihver boyunca nihâyetsizden gelip sıfırı müsbet istikamette dolaşan ve yine nihâyetsize dönen yoldur; bugün buna "Hankel yolu" denir. Riemann bunu bir cümle önce kelimelerle tarif etmiştir.

**[M3] Tâbiî muâdele.** Bu, bugün "zeta tâbisinin tâbiî muâdelesi" diye anılan münasebettir: Zeta tâbisinin, mütehavvil ile $1 - \text{mütehavvil}$ arasındaki aynalık. Ayna çizgisi, hakîkî cüz'ü $\tfrac{1}{2}$ olan kıymetlerdir.

**[M4] Jacobi atfı.** Aslında atıf kısaltılmış olarak geçer. Kastedilen, Carl Gustav Jacob Jacobi'nin *Fundamenta nova theoriae functionum ellipticarum* (Königsberg, 1829) adlı eserinin 184. sahifesidir. Düstur, teta tâbisinin tahvil düsturudur.

**[M5] Riemann farziyesi.** $\text{mütehavvil} = \tfrac{1}{2} + \text{irtifâ}\cdot\text{mevhûm-vâhid}$ konulduğundan, Tekmîl-zeta tâbisinin bir cezri olan irtifânın hakîkî olması, Zeta tâbisinin ona tekabül eden sıfırının hakîkî cüz'ünün tam $\tfrac{1}{2}$ olması demektir. "Bütün cezrlerin hakîkî olması pek muhtemeldir" cümlesi, bugün **Riemann farziyesi** diye bilinen ve riyâziyâtın halledilmemiş en meşhur meselesi sayılan iddianın ilk ve tek beyanıdır. Bu tercümenin yazıldığı tarihte (2026) bu farziye hâlâ ne ispat edilmiş, ne nakzedilmiştir; bu bilgi mütercimin kendi bilgisidir.

**[M6] Evvelî-adedi.** Bugün umûmiyetle Yunan harfi pî ile yazılan ve bir hududdan küçük a'dâd-ı evveliyyenin adedini sayan tâbidir; sıçrama noktalarında iki tarafın vasatîsi alınmıştır.

**[M7] Hangi mütehavvil üzerinden tamâmlama?** Wilkins istinsahında bu iki tamâmînin sonunda "d mütehavvil" yazılıdır. Tamâmlama kemmiyet üzerinden yapıldığından (kemmiyet, evvelîden nihâyetsize gider), mânâ itibarıyla doğrusu "d kemmiyet"tir: o takdirde $\text{mütehavvil} \int_{\text{evvelî}}^\infty \text{kemmiyet}^{-\text{mütehavvil}-1}\, d\,\text{kemmiyet} = \text{evvelî}^{-\text{mütehavvil}}$ olur. Metinde aslın yazısı muhafaza edilmiş, tashih buraya kaydedilmiştir. Bu farkın 1859 baskısında mı, 1892 baskısında mı, yoksa istinsahta mı doğduğunu bu oturumda yoklayamadım.

**[M8] Hakîkî-cüz mü, cezr mi?** Bu iki yerde istinsahta, sıfırların işareti olan Yunan harfi (bu tercümede "cezr" diye karşılanan) görünür; hesabın gidişine göre burada kastedilen, mütehavvilin hakîkî cüz'üdür: sağ taraf $\text{dâire-nisbeti}\;\text{Asıl}(\text{nokta})\;\text{nokta}^{-\text{hakîkî-cüz}}$ olur ve iki muâdele $\text{mevhûm-vâhid}\;\text{nokta}^{\,\text{hakîkî-cüz}}$ ile zarb edilir. Riemann'ın iki ayrı harfi birbirine pek benzediğinden, dizgide karışmış olması muhtemeldir. Tercümede doğrusu yazılmış, fark buraya kaydedilmiştir.

**[M9] Kavis.** Aslındaki "Arcus" kelimesi, mürekkeb bir kemmiyetin kutbî zaviyesidir; bugün "argüman" denir. Burada "kavis" ile karşılanmıştır.

**[M10] Asıl düstur.** Bu muâdele, bugün "Riemann'ın sarîh düsturu" diye anılan neticedir: a'dâd-ı evveliyyenin sayısını zeta tâbisinin sıfırları cinsinden tam olarak ifade eder. Logaritmik-tamâmî, $\int_0^{\text{hudut}} \frac{d\,\text{kemmiyet}}{\text{logaritma}(\text{kemmiyet})}$ tamâmîsidir (birdeki tekilliğin etrafından "esas kıymet" mânâsında alınmak üzere). Cezrler, Tekmîl-zeta tâbisinin cezrleridir; Zeta tâbisinin sıfırları $\tfrac{1}{2} \pm \text{cezr}\cdot\text{mevhûm-vâhid}$'dir. Bugünkü umûmî kabule göre $\text{logaritma}\,\text{Tekmîl-zeta}(0) = -\text{logaritma}(2)$'dir (mütercimin bilgisi).

**[M11] Möbius tersine çevirmesi.** Bu ameliye bugün "Möbius tersine çevirmesi" diye bilinir; $(-1)^{\text{mazrûb-sayısı}}$, murabbaa bölünmeyen bir adet için Möbius tâbisinin kıymetidir.

**[M12] Gauss ve Goldschmidt sayımları.** Riemann'ın, Logaritmik-tamâmî kıymetinin daima a'dâd-ı evveliyyenin sayısından büyük çıktığına dair naklettiği müşahede, üç milyona kadar doğrudur. Fakat 1914'te John Edensor Littlewood, farkın işaretinin nihâyetsiz defa değiştiğini ispat etmiştir; ilk işaret değişiminin vuku bulduğu yer çok büyüktür ve kesin olarak bilinmemektedir (mütercimin bilgisi).

---

## İsimler cedveli (düsturlardaki kelimeler)

Riemann'ın düsturlarındaki her harf bir kelimeyle karşılanmıştır. Sağdaki sütun, okuyanın tercümeyi aslıyla karşılaştırabilmesi için aslındaki işaretin **adını** verir; düsturların kendisinde harf kullanılmamıştır.

| Tercümedeki isim | Mânâsı | Aslındaki işaretin adı |
| :-- | :-- | :-- |
| mütehavvil | zeta tâbisinin mürekkeb mütehavvili | Latin "es" |
| hakîkî-cüz | mütehavvilin hakîkî cüz'ü | Latin "a" |
| mevhûm-cüz | mütehavvilin mevhûm cüz'ünün emsali | Latin "be" |
| evvelî | bütün a'dâd-ı evveliyye üzerinde gezen adet | Latin "pe" |
| adet | bütün tam a'dâd üzerinde gezen adet | Latin "en" |
| son-adet | hâsıl-ı zarbın kesildiği son adet | Latin "em" |
| murabbasız | murabbaa bölünmeyen adet | Latin "em" |
| mazrûb-sayısı | murabbasız adedin evvelî mazrûblarının sayısı | Yunan "mü" |
| kemmiyet | tamâmlama mütehavvili | Latin "iks" |
| hudut | a'dâd-ı evveliyyenin sayıldığı hudut | Latin "iks" |
| nokta | Fourier tersine çevirmesinde bakılan yer | Latin "ye" |
| irtifâ | Tekmîl-zeta tâbisinin mütehavvili | Latin "te" |
| hudut-irtifâ | cezrlerin sayıldığı irtifâ haddi | Latin büyük "te" |
| cezr | Tekmîl-zeta tâbisinin sıfırları | Yunan "alfa" |
| umûmî-cezr | herhangi bir cezri temsil eden yardımcı isim | Yunan "beta" |
| Zeta | zeta tâbisi | Yunan "zeta" |
| Gauss-zarbı | Gauss'un hâsıl-ı zarb tâbisi (bugün gamma) | Yunan büyük "pî" |
| Jacobi-mecmûu | teta mecmû'u | Yunan "psi" |
| Tekmîl-zeta | tamamlanmış zeta tâbisi | Yunan "ksi" |
| Evvelî-adedi | hududdan küçük evvelîlerin sayısı | Latin büyük "ef" |
| Kuvvet-adedi | evvelîlerin kuvvetlerini de ağırlıkla sayan tâbi | Latin "ef" |
| Logaritmik-tamâmî | logaritmik tamâmî | "Li" |
| Sûret, Sûret-hakîkî, Sûret-mevhûm | Fourier çiftinin sûret tarafı ve iki cüz'ü | Latin "ge", "ge bir", "ge iki" |
| Asıl | Fourier çiftinin asıl tarafı | Latin "he" |
| Neper | tabiî logaritmanın esası | Latin "e" |
| dâire-nisbeti | muhîtin kutra nisbeti | Yunan "pî" |
| mevhûm-vâhid | murabbaı eksi bir olan vâhid | Latin "i" |
| logaritma, ceyb, ceyb-i tamâm | logaritma, sinüs, kosinüs | "log", "sin", "cos" |

---

## Istılah cedveli (bu tercümede kullanılanlar)

Esas: aynı depodaki `lugat/msc2020/ceviri/11.tsv` (Nazariye-i a'dâd babı). Orada bulunmayan ıstılahlar için mütercimin teklifleri **teklif** diye işaretlenmiştir.

| Almanca | Bugünkü Türkçe | Bu tercümedeki karşılık | Dayanak |
| :-- | :-- | :-- | :-- |
| Primzahl | asal sayı | adet-i evvelî; cem'i a'dâd-ı evveliyye | lügat 11A41 |
| Function | fonksiyon | tâbi | lügat 11M |
| complexe Veränderliche | karmaşık değişken | mürekkeb mütehavvil | lügat 11F68 |
| reeller Theil | reel kısım | hakîkî cüz | lügat 11M20 ("hakîkî sıfırlar") |
| imaginärer Theil | sanal kısım | mevhûm cüz | teklif |
| convergiren | yakınsamak | mütekārib olmak | lügat 11N37 ("mukāribî") yakınında; teklif |
| Integral | integral | tamâmî; integrasyon: tamâmlama | lügat 11S80 ("p-adî tamâmlama") |
| partielle Integration | kısmî integrasyon | cüz cüz tamâmlama | teklif |
| Reihe | seri | silsile | lügat 11F27 ("Teta silsileleri") |
| Product | çarpım | hâsıl-ı zarb | lügat 11H46 |
| Wurzel (einer Gleichung) | kök | cezr | lügat 11A07 ("iptidâî cezrler") |
| Gleichung | denklem | muâdele | lügat 11D |
| Factor | çarpan | mazrûb | lügat 11A51 |
| Primfactor | asal çarpan | evvelî mazrûb | lügat 11A51 ile 11A41'den terkip |
| Dichtigkeit | yoğunluk | kesâfet | lügat 11B05 |
| Näherungsformel | yaklaşıklık formülü | takrîb düstûru | lügat 11J, 00A22 |
| Fourier'scher Satz | Fourier teoremi | Fourier kaziyyesi | lügat 11H60 ("kaziyyeler") |
| Unstetigkeit | süreksizlik | inkıtâ'; süreksiz: munkatı' | teklif |
| stetig | sürekli | muttasıl | lügat 11K41 ("Muttasıl") |
| endlich / unendlich | sonlu / sonsuz | mütenâhî / nihâyetsiz | lügat 11T ("Mütenâhî cisimler") |
| einwerthig / vieldeutig | tek değerli / çok değerli | tek kıymetli / çok kıymetli | teklif |
| Modul (komplexe Zahl) | mutlak değer | mikyâs | teklif |
| Grössengebiet | büyüklük bölgesi | kemmiyet sahası | teklif |
| Derivirte | türev | müştakk | teklif |
| Grenzwerth | limit | hadd kıymeti | teklif |
| Constante | sabit | sâbit | teklif |
| Glied | terim | hadd | teklif |
| Quadrat / Cubus | kare / küp | murabba / mükâab | lügat 11R11, 11R16 |
| periodisch | periyodik | devrî | lügat 11K70 ("takrîbî devrîlik") |
| Mittelwerth | ortalama değer | vasatî kıymet | lügat 11H60 |
| Arcus | argüman | kavis | teklif; bakınız [M9] |
| sin / cos | sinüs / kosinüs | ceyb / ceyb-i tamâm | kadîm Osmanlı ıstılahı (mütercimin bilgisi) |
