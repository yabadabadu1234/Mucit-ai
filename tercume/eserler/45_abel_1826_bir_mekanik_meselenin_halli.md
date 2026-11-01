# Bir Mekanik Meselenin Halli

**Niels Henrik Abel**

*[Saf ve Tatbikî Riyâziyât Mecmuası (Journal für die reine und angewandte Mathematik), birinci cilt, Berlin 1826, on beşinci makale.]*

---

> **Künye ve nüsha.** Aslın unvanı: *Auflösung einer mechanischen Aufgabe.* Almanca. İlk neşri: *Journal für die reine und angewandte Mathematik*, August Leopold Crelle tarafından neşredilen mecmuanın birinci cildi, Berlin 1826, sahife 153–157. Bu tercümeye esas alınan nüsha, aynı cildin Internet Archive'daki taramasıdır: <https://archive.org/details/sim_journal-fuer-die-reine-und-angewandte-mathematik_1826_1> (taramanın 156–160. varakları). Tercüme, sahife sûretleri baştan sona okunarak yapılmıştır.
>
> **Telif hâli.** Müellif 1829'da vefat etmiştir; eser 1826'da neşredilmiştir. Her memlekette umuma açıktır (telifi düşmüştür).
>
> **Düsturların yazılışı.** Padişahın kaidesi mûcibince düsturlarda hiçbir kemmiyet harfle yazılmamış, her biri mânâsını söyleyen bir kelimeyle yazılmıştır. Abel'in harflerinin hangi kelimeyle karşılandığı sondaki **İsimler cedveli**nde gösterilmiştir. Hesap ameliyelerinin işaretleri (cem', tarh, zarb, taksim, kuvvet, cezr, tamâmî, tefâzul, mecmû') ve rakamlar bırakılmıştır, zîrâ bunlar kemmiyet değil fiil ve adettir. Aslın düsturları, matbu nüshada nasıl basılmışsa öyle nakledilmiştir.

---

**15.**

## Bir mekanik meselenin halli

*(Bay N. H. Abel tarafından.)*

Üst uç, mebde, müteharrik ve müntehâ noktalarından geçen münhanî (ikinci levhanın beşinci şekli) keyfî bir münhanî olsun. Üst uçtan köşeye uzanan hat ufkî, köşeden müntehâya uzanan hat şâkulî olsun. Bir nokta, cazibenin sevkiyle bu münhanî boyunca hareket etsin ve hareketine keyfî bir mebde noktasından başlamış olsun. Mebdeden, verilmiş olan müntehâ noktasına vâsıl olduğu müddet **nüzûl-müddeti**, mebdein izdüşümü ile müntehâ arasındaki yükseklik **irtifâ** olsun. O hâlde nüzûl-müddeti, irtifânın, münhanînin şekline tâbi olan muayyen bir tâbisi olacaktır. Bilakis, münhanînin şekli de bu tâbiye tâbi olacaktır. Nüzûl-müddetinin irtifânın verilmiş **muttasıl** bir tâbisi olduğu münhanînin muâdelesinin, bir **muayyen tamâmî** (*intégrale définie*) yardımıyla nasıl bulunabileceğini tetkik etmek istiyoruz.

Müntehâdan müteharrik noktaya kadar olan kavs **kavs**, müntehâ ile müteharrikin izdüşümü arasındaki mesafe **fâsıla** olsun; hareket eden noktanın mebdeden müteharrik noktaya vâsıl olduğu müddet de **zaman** olsun.

Mekanik kaideleri mûcibince

$$-\frac{d\,\text{kavs}}{d\,\text{zaman}} = \sqrt{\text{irtifâ} - \text{fâsıla}}\,, \qquad \text{binâenaleyh} \qquad d\,\text{zaman} = -\frac{d\,\text{kavs}}{\sqrt{\text{irtifâ} - \text{fâsıla}}}$$

olur. Buradan, tamâmî $\text{fâsıla} = \text{irtifâ}$'dan $\text{fâsıla} = 0$'a kadar alınırsa,

$$\text{nüzûl-müddeti} = -\int_{\text{irtifâ}}^{0} \frac{d\,\text{kavs}}{\sqrt{\text{irtifâ} - \text{fâsıla}}} = +\int_{0}^{\text{irtifâ}} \frac{d\,\text{kavs}}{\sqrt{\text{irtifâ} - \text{fâsıla}}}$$

çıkar; burada meselâ

$$\int_{\text{alt-hudut}}^{\text{üst-hudut}}$$

ile, tamâmînin hudûdunun $\text{fâsıla} = \text{alt-hudut}$ ile $\text{fâsıla} = \text{üst-hudut}$'a ait olduğu gösterilmektedir.

Şimdi

$$\text{nüzûl-müddeti} = \text{Verilen}(\text{irtifâ})$$

verilmiş tâbi olsun; o hâlde

$$\text{Verilen}(\text{irtifâ}) = \int_{0}^{\text{irtifâ}} \frac{d\,\text{kavs}}{\sqrt{\text{irtifâ} - \text{fâsıla}}}$$

olur ki, kavs, fâsıla vasıtasıyla ifade edilmiş olarak, bu muâdeleden bulunmalıdır.

Bu muâdelenin yerine daha **umûmî** olan

$$\text{Verilen}(\text{irtifâ}) = \int_{0}^{\text{irtifâ}} \frac{d\,\text{kavs}}{(\text{irtifâ} - \text{fâsıla})^{\text{mertebe}}}$$

muâdelesini alalım ve ondan kavsı fâsıla vasıtasıyla arayalım.

$\text{Gamma}(\text{derece})$,

$$\text{Gamma}(\text{derece}) = \int_{0}^{1} d\,\text{fâsıla} \left( \text{logaritma}\,\frac{1}{\text{fâsıla}} \right)^{\text{derece} - 1}$$

tâbisini göstersin; o hâlde malûm olduğu üzere

$$\int_{0}^{1} \text{nisbet}^{\,\text{derece} - 1}\, (1 - \text{nisbet})^{\text{ikinci-derece} - 1}\; d\,\text{nisbet} = \frac{\text{Gamma}(\text{derece})\;\text{Gamma}(\text{ikinci-derece})}{\text{Gamma}(\text{derece} + \text{ikinci-derece})}$$

olur; burada derece ile ikinci-derecenin ikisi de sıfırdan büyük olmalıdır.

$\text{ikinci-derece} = 1 - \text{mertebe}$ olsun; o hâlde

$$\int_{0}^{1} \frac{\text{nisbet}^{\,\text{derece} - 1}\; d\,\text{nisbet}}{(1 - \text{nisbet})^{\text{mertebe}}} = \frac{\text{Gamma}(\text{derece})\;\text{Gamma}(1 - \text{mertebe})}{\text{Gamma}(\text{derece} + 1 - \text{mertebe})}$$

bulunur; buradan, $\text{ara-irtifâ} = \text{irtifâ} \cdot \text{nisbet}$ konulursa,

$$\int_{0}^{\text{irtifâ}} \frac{\text{ara-irtifâ}^{\,\text{derece} - 1}\; d\,\text{ara-irtifâ}}{(\text{irtifâ} - \text{ara-irtifâ})^{\text{mertebe}}} = \frac{\text{Gamma}(\text{derece})\;\text{Gamma}(1 - \text{mertebe})}{\text{Gamma}(\text{derece} + 1 - \text{mertebe})} \cdot \text{irtifâ}^{\,\text{derece} - \text{mertebe}}$$

çıkar.

Bu, $\dfrac{d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}}$ ile zarb edilsin ve tamâmî $\text{irtifâ} = 0$'dan $\text{irtifâ} = \text{fâsıla}$'ya kadar alınsın; o hâlde

$$\int_{0}^{\text{fâsıla}} \frac{d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}} \int_{0}^{\text{irtifâ}} \frac{\text{ara-irtifâ}^{\,\text{derece} - 1}\; d\,\text{ara-irtifâ}}{(\text{irtifâ} - \text{ara-irtifâ})^{\text{mertebe}}} = \frac{\text{Gamma}(\text{derece})\;\text{Gamma}(1 - \text{mertebe})}{\text{Gamma}(\text{derece} + 1 - \text{mertebe})} \int_{0}^{\text{fâsıla}} \frac{\text{irtifâ}^{\,\text{derece} - \text{mertebe}}\; d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}}$$

bulunur. $\text{irtifâ} = \text{fâsıla} \cdot \text{nisbet}$ konulursa

$$\int_{0}^{\text{fâsıla}} \frac{\text{irtifâ}^{\,\text{derece} - \text{mertebe}}\; d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}} = \text{fâsıla}^{\,\text{derece}} \int_{0}^{1} \frac{\text{nisbet}^{\,\text{derece} - \text{mertebe}}\; d\,\text{nisbet}}{(1 - \text{nisbet})^{1 - \text{mertebe}}} = \text{fâsıla}^{\,\text{derece}} \cdot \frac{\text{Gamma}(\text{derece} - \text{mertebe} + 1)\;\text{Gamma}(\text{mertebe})}{\text{Gamma}(\text{derece} + 1)}$$

bulunur; binâenaleyh

$$\int_{0}^{\text{fâsıla}} \frac{d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}} \int_{0}^{\text{irtifâ}} \frac{\text{ara-irtifâ}^{\,\text{derece} - 1}\; d\,\text{ara-irtifâ}}{(\text{irtifâ} - \text{ara-irtifâ})^{\text{mertebe}}} = \text{Gamma}(\text{mertebe})\;\text{Gamma}(1 - \text{mertebe})\; \frac{\text{Gamma}(\text{derece})}{\text{Gamma}(\text{derece} + 1)}\; \text{fâsıla}^{\,\text{derece}}$$

olur.

Şimdi Gamma tâbisinin malûm bir hassası mûcibince

$$\text{Gamma}(\text{derece} + 1) = \text{derece} \cdot \text{Gamma}(\text{derece})$$

dır; binâenaleyh ikame edilirse

$$\int_{0}^{\text{fâsıla}} \frac{d\,\text{irtifâ}}{(\text{irtifâ} - \text{fâsıla})^{1 - \text{mertebe}}} \int_{0}^{\text{irtifâ}} \frac{\text{ara-irtifâ}^{\,\text{derece} - 1}\; d\,\text{ara-irtifâ}}{(\text{irtifâ} - \text{ara-irtifâ})^{\text{mertebe}}} = \frac{\text{fâsıla}^{\,\text{derece}}}{\text{derece}}\; \text{Gamma}(\text{mertebe})\;\text{Gamma}(1 - \text{mertebe})$$

bulunur.

Bu, $\text{derece} \cdot \text{Verilen}(\text{derece})\; d\,\text{derece}$ ile zarb edilsin ve dereceye göre tamâmlansın; o hâlde

$$\int_{0}^{\text{fâsıla}} \frac{d\,\text{fâsıla}}{(\text{irtifâ} - \text{fâsıla})^{1 - \text{mertebe}}} \int_{0}^{\text{irtifâ}} \frac{\left( \displaystyle\int \text{Verilen}(\text{derece}) \cdot \text{derece} \cdot \text{ara-irtifâ}^{\,\text{derece} - 1}\; d\,\text{derece} \right) d\,\text{ara-irtifâ}}{(\text{irtifâ} - \text{ara-irtifâ})^{\text{mertebe}}} = \text{Gamma}(\text{mertebe})\;\text{Gamma}(1 - \text{mertebe}) \int \text{Verilen}(\text{derece}) \cdot \text{fâsıla}^{\,\text{derece}}\; d\,\text{derece}$$

bulunur.

$$\int \text{Verilen}(\text{derece}) \cdot \text{fâsıla}^{\,\text{derece}}\; d\,\text{derece} = \text{Yardımcı}(\text{fâsıla})$$

konulsun.

Bunun tefâzulü

$$\int \text{Verilen}(\text{derece}) \cdot \text{derece} \cdot \text{fâsıla}^{\,\text{derece} - 1}\; d\,\text{derece} = \text{Yardımcı}'(\text{fâsıla})$$

dır; binâenaleyh

$$\int \text{Verilen}(\text{derece}) \cdot \text{derece} \cdot \text{ara-irtifâ}^{\,\text{derece} - 1}\; d\,\text{derece} = \text{Yardımcı}'(\text{ara-irtifâ})$$

olur; bundan dolayı:

$$\int_{0}^{\text{fâsıla}} \frac{d\,\text{irtifâ}}{(\text{irtifâ} - \text{fâsıla})^{1 - \text{mertebe}}} \int_{0}^{\text{irtifâ}} \frac{\text{Yardımcı}'(\text{ara-irtifâ})\; d\,\text{ara-irtifâ}}{(\text{irtifâ} - \text{ara-irtifâ})^{\text{mertebe}}} = \text{Gamma}(\text{mertebe})\;\text{Gamma}(1 - \text{mertebe}) \cdot \text{Yardımcı}(\text{fâsıla})\,,$$

yahut, malûm olduğu üzere

$$\text{Gamma}(\text{mertebe})\;\text{Gamma}(1 - \text{mertebe}) = \frac{\text{dâire-nisbeti}}{\text{ceyb}(\text{mertebe} \cdot \text{dâire-nisbeti})}$$

olduğundan,

$$(1.)\qquad \text{Yardımcı}(\text{fâsıla}) = \frac{\text{ceyb}(\text{mertebe} \cdot \text{dâire-nisbeti})}{\text{dâire-nisbeti}} \int_{0}^{\text{fâsıla}} \frac{d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}} \int_{0}^{\text{irtifâ}} \frac{\text{Yardımcı}'(\text{ara-irtifâ})\; d\,\text{ara-irtifâ}}{(\text{irtifâ} - \text{ara-irtifâ})^{\text{mertebe}}}$$

olur.

Bu muâdelenin yardımıyla

$$\text{Verilen}(\text{irtifâ}) = \int_{0}^{\text{irtifâ}} \frac{d\,\text{kavs}}{(\text{irtifâ} - \text{fâsıla})^{\text{mertebe}}}$$

muâdelesinden kavs kolayca bulunur.

Filhakika bu muâdele

$$\frac{\text{ceyb}(\text{mertebe} \cdot \text{dâire-nisbeti})}{\text{dâire-nisbeti}} \cdot \frac{d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}}$$

ile zarb edilsin ve tamâmî $\text{irtifâ} = 0$'dan $\text{irtifâ} = \text{fâsıla}$'ya kadar alınsın; o hâlde

$$\frac{\text{ceyb}(\text{mertebe} \cdot \text{dâire-nisbeti})}{\text{dâire-nisbeti}} \int_{0}^{\text{fâsıla}} \frac{\text{Verilen}(\text{irtifâ}) \cdot d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}} = \frac{\text{ceyb}(\text{mertebe} \cdot \text{dâire-nisbeti})}{\text{dâire-nisbeti}} \int_{0}^{\text{fâsıla}} \frac{d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}} \int_{0}^{\text{irtifâ}} \frac{d\,\text{kavs}}{(\text{irtifâ} - \text{fâsıla})^{\text{mertebe}}}$$

bulunur; binâenaleyh (1.) muâdelesi mûcibince:

$$\text{kavs} = \frac{\text{ceyb}(\text{mertebe} \cdot \text{dâire-nisbeti})}{\text{dâire-nisbeti}} \int_{0}^{\text{fâsıla}} \frac{\text{Verilen}(\text{irtifâ})\; d\,\text{irtifâ}}{(\text{fâsıla} - \text{irtifâ})^{1 - \text{mertebe}}}$$

olur.

Şimdi $\text{mertebe} = \tfrac{1}{2}$ konulsun; o hâlde

$$\text{Verilen}(\text{irtifâ}) = \int_{0}^{\text{irtifâ}} \frac{d\,\text{kavs}}{\sqrt{\text{irtifâ} - \text{fâsıla}}}$$

ve

$$\text{kavs} = \frac{1}{\text{dâire-nisbeti}} \int_{0}^{\text{fâsıla}} \frac{\text{Verilen}(\text{irtifâ})\; d\,\text{irtifâ}}{\sqrt{\text{fâsıla} - \text{irtifâ}}}$$

olur.

Bu muâdele, malûm olduğu üzere, kavsı fâsıla vasıtasıyla verir; binâenaleyh münhanî artık tamamıyla muayyendir.

Bulunan ifadeyi birkaç misale tatbik edelim.

**I.**

$$\text{Verilen}(\text{irtifâ}) = \text{emsal}_0\, \text{irtifâ}^{\,\text{üs}_0} + \text{emsal}_1\, \text{irtifâ}^{\,\text{üs}_1} \;\ldots\ldots\; + \text{emsal}_{\text{son-sıra}}\, \text{irtifâ}^{\,\text{üs}_{\text{son-sıra}}} = \sum \left( \text{emsal} \cdot \text{irtifâ}^{\,\text{üs}} \right)$$

olsun; o hâlde bu hâlde kavsın kıymeti

$$\text{kavs} = \frac{1}{\text{dâire-nisbeti}} \int_{0}^{\text{fâsıla}} \frac{d\,\text{irtifâ}}{\sqrt{\text{fâsıla} - \text{irtifâ}}} \sum \text{emsal} \cdot \text{irtifâ}^{\,\text{üs}} = \frac{1}{\text{dâire-nisbeti}} \sum \left( \text{emsal} \int_{0}^{\text{fâsıla}} \frac{\text{irtifâ}^{\,\text{üs}}\; d\,\text{irtifâ}}{\sqrt{\text{fâsıla} - \text{irtifâ}}} \right)$$

olur. Şimdi $\text{irtifâ} = \text{fâsıla} \cdot \text{nisbet}$ konulursa

$$\int_{0} \frac{\text{irtifâ}^{\,\text{üs}}\; d\,\text{irtifâ}}{\sqrt{\text{fâsıla} - \text{irtifâ}}} = \text{fâsıla}^{\,\text{üs} + \frac{1}{2}} \int_{0}^{1} \frac{\text{nisbet}^{\,\text{üs}}\; d\,\text{nisbet}}{\sqrt{1 - \text{nisbet}}} = \text{fâsıla}^{\,\text{üs} + \frac{1}{2}} \cdot \frac{\text{Gamma}(\text{üs} + 1)\;\text{Gamma}\!\left(\tfrac{1}{2}\right)}{\text{Gamma}\!\left(\text{üs} + \tfrac{3}{2}\right)}$$

olur; binâenaleyh

$$\text{kavs} = \frac{\text{Gamma}\!\left(\tfrac{1}{2}\right)}{\text{dâire-nisbeti}} \sum \frac{\text{emsal} \cdot \text{Gamma}(\text{üs} + 1)}{\text{Gamma}\!\left(\text{üs} + \tfrac{3}{2}\right)}\; \text{fâsıla}^{\,\text{üs} + \frac{1}{2}}$$

yahut,

$$\text{Gamma}\!\left(\tfrac{1}{2}\right) = \sqrt{\text{dâire-nisbeti}}$$

olduğundan:

$$\text{kavs} = \sqrt{\frac{\text{fâsıla}}{\text{dâire-nisbeti}}} \left[ \text{emsal}_0\, \frac{\text{Gamma}(\text{üs}_0 + 1)}{\text{Gamma}\!\left(\text{üs}_0 + \tfrac{3}{2}\right)} \cdot \text{fâsıla}^{\,\text{üs}_0} + \text{emsal}_1\, \frac{\text{Gamma}(\text{üs}_1 + 1)}{\text{Gamma}\!\left(\text{üs}_1 + \tfrac{3}{2}\right)}\, \text{fâsıla}^{\,\text{üs}_1} \;\ldots\ldots\; + \text{emsal}_{\text{son-sıra}}\, \frac{\text{Gamma}(\text{üs}_{\text{son-sıra}} + 1)}{\text{Gamma}\!\left(\text{üs}_{\text{son-sıra}} + \tfrac{3}{2}\right)} \cdot \text{fâsıla}^{\,\text{üs}_{\text{son-sıra}}} \right]$$

olur.

Meselâ $\text{son-sıra} = 0$, $\text{üs}_0 = 0$ alınırsa, yâni aranan münhanî **mütesâvî'z-zaman** (isochron) farz edilirse,

$$\text{kavs} = \sqrt{\frac{\text{fâsıla}}{\text{dâire-nisbeti}}}\; \text{emsal}_0\, \frac{\text{Gamma}(1)}{\text{Gamma}\!\left(\tfrac{3}{2}\right)} = \frac{\text{emsal}_0}{\tfrac{1}{2}\,\text{Gamma}\!\left(\tfrac{1}{2}\right)} \sqrt{\frac{\text{fâsıla}}{\text{dâire-nisbeti}}} = \frac{2\,\text{emsal}_0}{\text{dâire-nisbeti}} \sqrt{\text{fâsıla}}\,,$$

bulunur; ve

$$\text{kavs} = \frac{2\,\text{emsal}_0}{\text{dâire-nisbeti}} \sqrt{\text{fâsıla}}$$

malûm olduğu üzere **devvâre**nin (*Cycloïde*) muâdelesidir.

**II.**

$$\begin{aligned}
&\text{Verilen}(\text{irtifâ}),\; \text{irtifâ} = 0\text{'dan } \text{irtifâ} = \text{hudut}_0\text{'a kadar}, && \text{Verilen}_0(\text{irtifâ})\text{'ya müsâvî},\\
&\text{Verilen}(\text{irtifâ}),\; \text{irtifâ} = \text{hudut}_0\text{'dan } \text{irtifâ} = \text{hudut}_1\text{'e kadar}, && \text{Verilen}_1(\text{irtifâ})\text{'ya müsâvî},\\
&\text{Verilen}(\text{irtifâ}),\; \text{irtifâ} = \text{hudut}_1\text{'den } \text{irtifâ} = \text{hudut}_2\text{'ye kadar}, && \text{Verilen}_2(\text{irtifâ})\text{'ya müsâvî},\\
&\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\\
&\text{Verilen}(\text{irtifâ}),\; \text{irtifâ} = \text{hudut}_{\text{son-sıra} - 1}\text{'den } \text{irtifâ} = \text{hudut}_{\text{son-sıra}}\text{'ya kadar}, && \text{Verilen}_{\text{son-sıra}}(\text{irtifâ})\text{'ya müsâvî}
\end{aligned}$$

olsun; o hâlde

$$\text{dâire-nisbeti} \cdot \text{kavs} = \int_{0}^{\text{fâsıla}} \frac{\text{Verilen}_0(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}}\,, \qquad \text{fâsıla} = 0 \text{ ile } \text{fâsıla} = \text{hudut}_0 \text{ arasında},$$

$$\text{dâire-nisbeti} \cdot \text{kavs} = \int_{0}^{\text{hudut}_0} \frac{\text{Verilen}_0(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}} + \int_{\text{hudut}_0}^{\text{fâsıla}} \frac{\text{Verilen}_1(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}}\,, \qquad \text{fâsıla} = \text{hudut}_0 \text{ ile } \text{fâsıla} = \text{hudut}_1 \text{ arasında},$$

$$\text{dâire-nisbeti} \cdot \text{kavs} = \int_{0}^{\text{hudut}_0} \frac{\text{Verilen}_0(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}} + \int_{\text{hudut}_0}^{\text{hudut}_1} \frac{\text{Verilen}_1(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}} + \int_{\text{hudut}_1}^{\text{fâsıla}} \frac{\text{Verilen}_2(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}}\,, \qquad \text{fâsıla} = \text{hudut}_1 \text{ ile } \text{fâsıla} = \text{hudut}_2 \text{ arasında},$$

$$\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots\ldots$$

$$\begin{aligned}
\text{dâire-nisbeti} \cdot \text{kavs} = {}& \int_{0}^{\text{hudut}_0} \frac{\text{Verilen}_0(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}} + \int_{\text{hudut}_0}^{\text{hudut}_1} \frac{\text{Verilen}_1(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}} \;\ldots\; \\
& + \int_{\text{hudut}_{\text{son-sıra} - 2}}^{\text{hudut}_{\text{son-sıra} - 1}} \frac{\text{Verilen}_{\text{son-sıra} - 1}(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}} + \int_{\text{hudut}_{\text{son-sıra} - 1}}^{\text{fâsıla}} \frac{\text{Verilen}_{\text{son-sıra}}(\text{irtifâ}) \cdot d\,\text{irtifâ}}{\sqrt{\text{irtifâ} - \text{fâsıla}}}\,,
\end{aligned}$$

$$\text{fâsıla} = \text{hudut}_{\text{son-sıra} - 1} \text{ ile } \text{fâsıla} = \text{hudut}_{\text{son-sıra}} \text{ arasında}$$

olur; şunu da kaydetmek lâzımdır ki $\text{Verilen}_0(\text{irtifâ}),\; \text{Verilen}_1(\text{irtifâ}),\; \text{Verilen}_2(\text{irtifâ}) \;\ldots\ldots\; \text{Verilen}_{\text{son-sıra}}(\text{irtifâ})$ tâbileri

$$\text{Verilen}_0(\text{hudut}_0) = \text{Verilen}_1(\text{hudut}_0)\,, \quad \text{Verilen}_1(\text{hudut}_1) = \text{Verilen}_2(\text{hudut}_1)\,, \quad \text{Verilen}_2(\text{hudut}_2) = \text{Verilen}_3(\text{hudut}_2)\,, \quad \text{ve bu minvâl üzere}$$

olacak nevîden olmalıdır; zîrâ Verilen tâbisi zarûrî olarak **muttasıl** olmalıdır.

---

## İsimler cedveli (düsturlardaki kelimeler)

Abel'in düsturlarındaki ve şeklindeki her harf bir kelimeyle karşılanmıştır. Sağdaki sütun, okuyanın tercümeyi aslıyla karşılaştırabilmesi için aslındaki işaretin **adını** verir; düsturların kendisinde harf kullanılmamıştır. Aslında harfin şekli bir yerde başka bir harfe benzer basılmış olsa da, kelime, işaretin gösterdiği şeye göre konulmuştur.

| Tercümedeki isim | Mânâsı | Aslındaki işaretin adı |
| :-- | :-- | :-- |
| üst uç | münhanînin ufkî hattın başındaki ucu | Latin büyük "be" |
| köşe | ufkî hat ile şâkulî hattın buluştuğu nokta | Latin büyük "ce" |
| mebde | hareketin başladığı nokta | Latin büyük "de" |
| müteharrik | hareket eden noktanın herhangi bir andaki yeri | Latin büyük "em" |
| müntehâ | hareketin vardığı verilmiş nokta | Latin büyük "a" |
| mebdein izdüşümü | mebdein şâkulî hat üzerindeki izdüşümü | Latin büyük "e" |
| müteharrikin izdüşümü | müteharrikin şâkulî hat üzerindeki izdüşümü | Latin büyük "pe" |
| nüzûl-müddeti | mebdeden müntehâya varış müddeti | Yunan "tav" |
| irtifâ | mebdein müntehâdan yüksekliği; sonra tamâmlama mütehavvili | Latin "a" |
| kavs | müntehâdan müteharrike kadar münhanînin kavsi | Latin "es" |
| fâsıla | müntehâdan müteharrikin izdüşümüne kadar olan mesafe; ayrıca Gamma tâbisinin tarifinde tamâmlama mütehavvili | Latin "iks" |
| zaman | mebdeden müteharrike varış müddeti | Latin "te" |
| alt-hudut, üst-hudut | tamâmî işaretinin alt ve üst hududu (yazılış misali) | Yunan "alfa", Yunan "beta" |
| Verilen | verilmiş tâbi | 154. sahifede Latin "ef", 155. sahifeden itibaren Yunan "fi" |
| Verilen₀, Verilen₁ … | ikinci misalde kıt'a kıt'a verilmiş tâbiler | Yunan "fi" ile altındaki rakam |
| Yardımcı | yardımcı tâbi | 155. sahifede Latin "ef" |
| Yardımcı′ | yardımcı tâbinin tefâzulî müştakkı | Latin "ef" ile üstündeki vurgu |
| mertebe | tamâmî işaretinin altındaki farkın kuvveti | Latin "en" |
| derece | Gamma tâbisinin mütehavvili; sonra tamâmlama mütehavvili | Yunan "alfa" |
| ikinci-derece | Gamma tâbisinin ikinci mütehavvili | Yunan "beta" |
| nisbet | sıfırdan bire giden tamâmlama mütehavvili | Latin "ye" |
| ara-irtifâ | sıfırdan irtifâya giden tamâmlama mütehavvili | Latin "zet" |
| emsal₀, emsal₁ … | birinci misaldeki kesîrü'l-hudûdun emsali | Yunan "alfa" ile altındaki rakam |
| üs₀, üs₁ … | birinci misaldeki kesîrü'l-hudûdun üsleri | Yunan "mü" ile altındaki rakam |
| son-sıra | son emsalin ve son huddun sıra numarası | Latin "em" |
| hudut₀, hudut₁ … | ikinci misalde Verilen tâbisinin kıt'alarının hudutları | Latin "a" ile altındaki rakam |
| Gamma | Gamma tâbisi | Yunan büyük "gamma" |
| dâire-nisbeti | muhîtin kutra nisbeti | Yunan "pî" |
| logaritma, ceyb | logaritma, sinüs | "log", "sin" |

---

## Istılah cedveli (bu tercümede kullanılanlar)

Esas: aynı depodaki `lugat/kok_istilahlar.tsv` ile `lugat/msc2020/ceviri/` dosyaları (dal: `claude/project-thread-jvwo8g`). Orada bulunmayan ıstılahlar **teklif** diye işaretlenmiştir.

| Almanca | Bugünkü Türkçe | Bu tercümedeki karşılık | Dayanak |
| :-- | :-- | :-- | :-- |
| Aufgabe | problem | mesele | lügat 70F05 ("İki cisim meseleleri") |
| mechanisch | mekanik | mekanik | lügat 70-XX |
| Curve | eğri | münhanî | lügat kök ıstılahlar ("curve") |
| horizontal / vertical | yatay / düşey | ufkî / şâkulî | teklif |
| Schwerkraft | yerçekimi | cazibe | lügat kök ıstılahlar ("gravitation") |
| Function | fonksiyon | tâbi | lügat kök ıstılahlar ("function") |
| stetig | sürekli | muttasıl | lügat kök ıstılahlar ("continuous") |
| bestimmtes Integral | belirli integral | muayyen tamâmî | lügat kök ıstılahlar ("integral") ile terkip |
| Integral, integriren | integral, integral almak | tamâmî, tamâmlamak | lügat kök ıstılahlar ("integral") |
| Grenzen des Integrals | integralin sınırları | tamâmînin hudûdu | teklif |
| Differential | diferansiyel | tefâzul | lügat kök ıstılahlar ("differential") |
| Gleichung | denklem | muâdele | lügat kök ıstılahlar ("equation") |
| Eigenschaft | özellik | hassa | teklif |
| substituiren | yerine koymak | ikame etmek | teklif |
| Bogen | yay | kavs | teklif |
| Abscisse | apsis | fâsıla | teklif |
| Coefficient | katsayı | emsal | lügat kök ıstılahlar ("coefficient") |
| isochron | eşzamanlı | mütesâvî'z-zaman | teklif |
| Cycloïde | sikloit | devvâre | teklif |
| Beispiel | örnek | misal | teklif |
| sin | sinüs | ceyb | Riemann 1859 tercümesindeki kullanış |
| log | logaritma | logaritma | lügat kök ıstılahlar ("logarithm") |
