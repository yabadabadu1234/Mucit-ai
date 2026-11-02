# Tahavvül-i Muttasıl Tip Nazariyesi: Riyâziyâtın Vahdet Esasları

## Altıncı Bab: Yüksek İstikrâî Tipler

**Vahdet Esasları Programı (The Univalent Foundations Program)**

*[İleri Tetkikler Enstitüsü (Institute for Advanced Study), Princeton, 2013.]*

---

> **Künye ve nüsha.** Aslın unvanı: *Homotopy Type Theory: Univalent Foundations of Mathematics*, altıncı bab: *Higher inductive types.* İngilizce. Müellif: The Univalent Foundations Program, Institute for Advanced Study, Princeton, 2013. Bu tercümeye esas alınan asıl: kitabın LaTeX kaynağı, <https://github.com/HoTT/book>, dosya `hits.tex` (Teşrîn-i sânî 2026'da alınan nüsha). Kaziyye, tarif, düstur ve temrin numaraları aslın numaralarıdır.
>
> **Lisans.** Aslı *Creative Commons Atıf-Aynı Lisansla Paylaş 3.0 Umûmî* (Creative Commons Attribution-ShareAlike 3.0 Unported) lisansıyla neşredilmiştir: <http://creativecommons.org/licenses/by-sa/3.0/>. Bu tercüme de **aynı lisansla** neşredilir. Atıf: The Univalent Foundations Program, *Homotopy Type Theory: Univalent Foundations of Mathematics*, Institute for Advanced Study, 2013; Osmanlıca tercümesi, Mucit-AI tercüme heyeti, 2026. Tercümede aslın metni değiştirilmeden nakledilmiştir; değişiklik yalnız lisanın değişmesidir ve düsturların kelimeyle yazılmasıdır.
>
> **Düsturların yazılışı.** Düsturlarda harf yazılmamıştır; her kemmiyet mânâsını söyleyen kelimeyle adlandırılmıştır. Aslın işaretlerinin hangi kelimelerle karşılandığı sondaki **İsimler cedveli**ndedir. Ameliye işaretleri (Σ, Π, ×, +, →, =, ≃, ∼, ∘, ∙, ⁻¹, ↦, :) ile rakamlar bırakılmıştır. "≡" hükmî müsâvâtı, ":≡" tarif ile hükmî müsâvâtı, ":=" tarif ile kaziyyevî müsâvâtı gösterir. "birinci hadd =[aile | tarîk] ikinci hadd" yazısı, aileye göre tarîkin üstünde yatan mütevakkıf tarîkler tipidir.

---

## 6.1 Medhal

Beşinci babda müzakere ettiğimiz umûmî istikrâî tipler gibi, *yüksek istikrâî tipler* de bazı müessisler tarafından tevlîd olunan yeni tipler tarif etmek için umûmî bir şemadır. Fakat âdi istikrâî tiplerden farklı olarak, bir yüksek istikrâî tipi tarif ederken, o tipin yalnız *noktalarını* değil, o tipteki *tarîkleri* ve yüksek tarîkleri de tevlîd eden "müessisler"e sahip olabiliriz. Meselâ şunlar tarafından tevlîd olunan yüksek istikrâî tip olan Dâire'yi mülâhaza edebiliriz:

- bir nokta, kaide : Dâire, ve
- bir tarîk, ilmik : kaide =_{Dâire} kaide.

Bu, meselâ İkilik'in şunlar tarafından tevlîd olunan tip olarak tarifine tamamen benzer telakkî edilmelidir:

- bir nokta, İkilik-sıfırı : İkilik, ve
- bir nokta, İkilik-biri : İkilik;

yahut Tabiî'nin şunlar tarafından tevlîd olunan tip olarak tarifine:

- bir nokta, 0 : Tabiî, ve
- bir tâbi, ardıl : Tabiî → Tabiî.

Tipleri yüksek zümremsiler olarak düşündüğümüzde, "tevlîd"in daha umûmî mefhûmu pek tabiîdir: bir yüksek zümremsi, noktaların yanında tarîkleri ve yüksek tarîkleri de olan "çok cinsli bir nesne" olduğu için, bütün buudlarda "müvellidler"e izin vermeliyiz.

Âdi cinsten müessislere (kaide gibi) **nokta müessisleri** yahut *âdi müessisler*, diğerlerine (ilmik gibi) ise **tarîk müessisleri** yahut *yüksek müessisler* diyeceğiz. Her tarîk müessisi, tarîkin başlangıç ve bitiş noktasını tayin etmelidir; bunlara onun **mebdei** ve **müntehâsı** deriz; ilmik için hem mebde hem müntehâ kaidedir.

Dikkat edilsin ki ilmik gibi bir tarîk müessisi, bir ayniyet tipinin, evvelce mevcut olan böyle herhangi bir sâkine müsavi olmayan (hiç değilse *evvelî olarak* müsavi olmayan) *yeni* bir sâkinini tevlîd eder. Bilhassa ilmik, *evvelî olarak* aksiyet(kaide)'ye müsavi değildir (gerçi bunların kat'iyyen müsavi olmadığını ispat etmek biraz düşünmeyi ister; bakınız Yardımcı kaziyye 6.4.1). Dâire'yi âdi istikrâî tip olan birim tipten ayıran budur.

Bu umûmîleştirmeye dair söylenmesi lâzım gelen bazı mühim noktalar vardır.

Her şeyden evvel "tevlîd" kelimesi, bir zümrenin bir mecmûa tarafından serbestçe tevlîd olunabilmesi mânâsında, ciddiyetle alınmalıdır. Bilhassa bir yüksek zümremsi, tarîkler ve yüksek tarîkler üzerinde *ameliyeler* ile beraber geldiği için, böyle bir nesne muayyen müessisler tarafından "tevlîd" olunduğunda, ameliyeler, doğrudan doğruya müessislerin kendilerinden gelmeyen daha başka tarîkler hâsıl eder. Meselâ Dâire yüksek istikrâî tipinde, ilmik müessisi kaideden kaideye giden âdi olmayan biricik tarîk değildir; "ilmik ∙ ilmik" ve "ilmik ∙ ilmik ∙ ilmik" ve saire de, ilmik⁻¹ ve saire de vardır; bunların hepsi birbirinden farklıdır. Bu, zikredilmeye değmeyecek kadar âşikâr görünebilir; fakat istikrâî tipte, müessislerin doğrudan "koyduğu" şeyden başka hiçbir şey görmeyi beklemeyen "âdi" istikrâî tiplerin davranışından bir ayrılıştır.

İkinci olarak, bu tevlîd hakikaten *serbest* tevlîddir: yüksek istikrâî tipler, fennî olarak, "ilmik ∙ ilmik"in aksiyet(kaide)'ye müsavi olmaya mecbur edilmesi gibi "mütearifeler" koymamıza izin vermez. Bununla beraber nihâyetsiz zümremsiler âleminde "serbest tevlîd" ile "takdîm" arasında pek az fark vardır; zîrâ iki tarîki, onları birbirine bağlayan yeni bir iki buudlu müvellid ekleyerek (meselâ kaide = kaide içinde bir "ilmik ∙ ilmik = aksiyet(kaide)" tarîki) *tahavvül-i muttasıla kadar* müsavi kılabiliriz. O vakit elbette bu yeni müvellidin kendi "mütearifeler"ini sağlayıp sağlamaması gerektiği ve saire hakkında endişe etmemiz lâzım gelir; fakat prensip itibarıyla her "takdîm", mütearifeler müessislere çevrilerek "serbest" bir takdîme döndürülebilir. Göreceğimiz üzere "kat' müessisleri" ekleyerek, yüksek istikrâî tipleri zümre takdîmleri gibi klasik mefhûmları ifade etmek için de kullanabiliriz.

Üçüncü olarak, bir yüksek istikrâî tip, o tipin *içindeki tarîkleri* tevlîd eden "müessisler" ihtiva etse de, o yine de *tek bir* tipin istikrâî bir tarifidir. Bilhassa göreceğimiz üzere, (her zamanki gibi bir istikrâ mebdei ile ifade edilen) bir küllî hassa verilen şey yüksek istikrâî tipin kendisidir, onun ayniyet tipleri *değildir*. Bir yüksek istikrâî tipin ayniyet tipi, her ayniyet tipinin mûtat istikrâ mebdeini (yâni tarîk istikrâsını) muhafaza eder ve hiçbir yeni istikrâ mebdei kazanmaz.

Binâenaleyh, ikinci babda ayniyet tiplerinin bütün an'anevî tip teşkil ameliyeleri altındaki davranışının açık tavsiflerini verebildiğimizin aksine, bir yüksek istikrâî tipin ayniyet tiplerini muayyen bir tarzda tayin etmek âdi olmayan bir iş olabilir. Meselâ Dâire'de kaideden kaideye giden, sadece ilmik ile onun tersinin nüshalarının terkipleri olmayan tarîkler var mıdır? Sezgi ile cevabın "hayır" olması lâzım geldiği görünür (ve öyledir), fakat bunu ispat etmek âdi değildir. Filhakika böyle suâller bizi süratle kürelerin tahavvül-i muttasıl zümrelerinin hesabı gibi meselelere götürür ki bu, cebrî hendese-i vaz'iyyede basit hiçbir düsturu bilinmeyen eski bir meseledir. Tahavvül-i muttasıl tip nazariyesi böyle suâllere yeni ve kudretli bir nokta-i nazar getirir, fakat aynı zamanda tip nazariyesinin bu suâllerin cevapları kadar girift olmasını da gerektirir.

Dördüncü olarak, müessislerin "buudu" (yâni noktalar mı, tarîkler mi, tarîkler arasındaki tarîkler mi ve saire mi çıkardıkları), hâsıl olan tipin hangi buudlarda âdi olmayan tahavvül-i muttasıla sahip olduğu ile doğrudan bir irtibata sahip değildir. Basit bir misal olarak, bir hedef istikrâî tipin "tip → hedef tip" tipinde bir müessisi varsa, o müessis hiç de "yüksek" bir müessis olmadığı hâlde, tipteki her tarîk ve yüksek tarîk, hedef tipte tarîkler ve yüksek tarîkler hâsıl eder. Aynı şey yüksek müessislerde de olur: "tip → (birinci unsur =_{hedef tip} ikinci unsur)" tipinde bir müessise sahip olmak, yalnız tipin noktalarının hedef tipte birinci unsurdan ikinci unsura tarîkler verdiği değil, tipteki tarîklerin bu tarîkler arasında tarîkler verdiği ve saire mânâsına gelir. Göreceğimiz üzere yüksek istikrâî tiplerin kudretinin büyük kısmı bu imkândan gelir.

Diğer taraftan, girdilerinde yüksek tipler *bulunmayan* müessislerin "beklenmedik" yüksek tarîkler tevlîd etmesi bile mümkündür. Meselâ şunlar tarafından tevlîd olunan iki buudlu Küre'de:

- bir nokta, kaide : Küre, ve
- kaide = kaide içinde iki buudlu bir tarîk, sath : aksiyet(kaide) = aksiyet(kaide),

aksiyet(aksiyet(kaide))'den kendisine giden âdi olmayan bir *üç buudlu tarîk* vardır. Hendese-i vaz'iyye ehli bu tarîki *Hopf liflemesi*nin bir tecessüdü olarak tanıyacaklardır. Makûleler nazariyesi nokta-i nazarından bu, yukarıda zikredilen, Dâire'nin yalnız ilmiği değil "ilmik ∙ ilmik"i ve saireyi de ihtiva etmesi vakıasıyla aynı cinsten bir hâdisedir: sadece şu kadar ki bir *yüksek* zümremside buudu yükselten *ameliyeler* vardır. Filhakika bu ameliyelerin çoğunu 2.1. bahiste görmüştük: birleşme ve birim kanunları sadece hassalar değil, girdileri bir buudlu tarîkler, çıktıları iki buudlu tarîkler olan ameliyelerdir.

## 6.2 İstikrâ mebdeleri ve mütevakkıf tarîkler

Dâire gibi bir yüksek istikrâî tipi muayyen müessisler tarafından tevlîd olunmuş diye tarif ettiğimizde, bunun ne demek olduğunu, birinci babdaki temel tip müessislerine ait kaidelere benzer kaideler vererek izah etmemiz lâzımdır. Müessislerin kendileri *idhâl* kaidelerini verir; fakat *ihraç* kaidelerini, yâni istikrâ ve rücû' mebdelerini izah etmek biraz daha fazla düşünmeyi ister. Bu kitapta bir "yüksek istikrâî tarif"in neden ibaret olduğunun ve böyle bir tariften ihraç kaidesinin nasıl çıkarılacağının umûmî bir ifadesini vermeye teşebbüs etmiyoruz; filhakika bu ince bir suâldir ve bugünkü tetkiklerin mevzûudur. Onun yerine bazı umûmî gayr-ı sûrî müzakerelere ve sayısız misallere dayanacağız.

Rücû' mebdeini tarif etmek umûmiyetle kolaydır: müessislerin, söz konusu yüksek istikrâî tipe teçhiz ettiği aynı bünye ile teçhiz edilmiş herhangi bir tip verilince, müessisleri o bünyeye götüren bir tâbi vardır. Meselâ Dâire hâlinde rücû' mebdei şunu söyler: bir muayyen nokta : hedef tip ve bir muayyen tarîk : muayyen nokta = muayyen nokta ile teçhiz edilmiş herhangi bir hedef tip verilince, tâbi(kaide) = muayyen nokta ve tatbik[tâbi](ilmik) = muayyen tarîk olacak şekilde bir tâbi : Dâire → hedef tip vardır.

Sonraki iki müsâvât *hesap kaideleri*dir. Bununla beraber bu hesap kaidelerinin hükmî müsâvâtlar mı, yoksa kaziyyevî müsâvâtlar (tarîkler) mı olduğu suâli vardır. Âdi istikrâî tipler için onları hükmî yapmakta hiçbir tereddüdümüz olmamıştı; gerçi beşinci babda gördük ki onları kaziyyevî yapmak da tekâfü'e kadar yine aynı tipi verirdi. Âdi hâlde, hesap kaidelerinin, Medhal'de tarif edilen sezgî mânâda, hakikaten *tarifî* müsâvâtlar olduğu ileri sürülebilir.

Yüksek istikrâî tipler için bu o kadar açık değildir. Bundan başka, tatbik[tâbi] ameliyesi tip nazariyesinin hakikaten temel bir cüz'ü olmayıp, ayniyet tiplerinin istikrâ mebdeini kullanarak *tarif ettiğimiz* (ve başka, mütekâfi bir yolla da tarif edebileceğimiz) bir şey olduğu için, ona bir *hükmî* müsâvâtta açıkça atıf yapmak münasip görünmez. Hükmî müsâvâtlar istidlâl nizâmının bir cüz'üdür; bu nizâm ise, o nizâmın *içinde* yapabileceğimiz tariflerin hususî seçimlerine bağlı olmamalıdır. Mülâhaza edilmesi lâzım gelen mânâya ve tatbikata ait meseleler de vardır; bakınız Notlar.

Bir yüksek istikrâî tipin *nokta* müessislerine ait hesap kaidelerini hükmî yapmak ise müşkil görünmez. Yukarıdaki misalde bu, hükmen tâbi(kaide) ≡ muayyen nokta olması demektir. Bu tercih, yüksek istikrâî tiplere hesabî bir nazarla bakmayı kolaylaştırır. Bundan başka hayatımızı da pek sadeleştirir; zîrâ aksi hâlde ikinci hesap kaidesi tatbik[tâbi](ilmik) = muayyen tarîk kaziyyevî bir müsâvât olarak tip itibarıyla iyi kurulmuş bile olmazdı; bir tarafı yahut öteki tarafı, tâbi(kaide)'nin muayyen noktaya tayin edilmiş aynîleştirmesiyle terkip etmemiz lâzım gelirdi. (Böyle meseleler, yüksek buudlu tarîklerden bahsetmeye geldiğimizde elbette nihayet zuhur eder; fakat bu, burada bizi pek alâkadar etmeyecektir. Bakınız ayrıca 6.7. bahis.) Binâenaleyh nokta müessislerine ait hesap kaidelerini hükmî, tarîklere ve yüksek tarîklere ait olanları ise kaziyyevî kabul ediyoruz.[^1]

[^1]: Bilhassa 1.1. bahsin lisanıyla bu şu demektir ki yüksek istikrâî tiplerimiz *kaideler* (bu tipleri ve unsurlarını nasıl idhâl edebileceğimizi, istikrâ mebdelerini ve nokta müessislerine ait hesap kaidelerini tayin eden) ile *mütearifeler*in (muayyen ayniyet tiplerinin başkaca tayin edilmemiş hadlerle meskûn olduğunu iddia eden, tarîk müessislerine ait hesap kaideleri) bir karışımıdır. Ümit edebiliriz ki nihayet, yüksek istikrâî tiplerin, vahdet gibi, mütearifesiz yalnız kaidelerle takdim edileceği daha iyi bir tip nazariyesi olacaktır.

**Tenbih 6.2.1.** Hatırlansın ki âdi istikrâî tipler için, rücûî olarak tarif edilmiş bir tâbinin hesap kaidelerini sadece hükmî müsâvâtlar değil, *tarifî* müsâvâtlar sayarız ve binâenaleyh onlar için ":≡" işaretini kullanabiliriz. Meselâ kat'lı mukaddem tâbisi mukaddem : Tabiî → Tabiî, mukaddem(0) :≡ 0 ve mukaddem(ardıl(sayı)) :≡ sayı ile tarif edilir. Yüksek istikrâî tipler hâlinde bu çeşit işaret nokta müessisleri için makuldür (meselâ tâbi(kaide) :≡ muayyen nokta), fakat tarîk müessisleri için yanıltıcı olabilir; zîrâ tatbik[tâbi](ilmik) = muayyen tarîk gibi müsâvâtlar hükmî değildir. Binâenaleyh işaretleri melezleştirip, bu çeşit "tarif ile kaziyyevî müsâvât" için onun yerine tatbik[tâbi](ilmik) := muayyen tarîk yazıyoruz.

Şimdi istikrâ mebdei (mütevakkıf ihraç edici) ne olacak? Hatırlansın ki âdi bir istikrâî tip olan "W" için, istikrâ ile Π (unsur : W) aile(unsur) olduğunu ispat etmek üzere, W'nin her müessisi için, W'de o müessisin üstündeki "lifler" üzerinde amel eden bir ameliyeyi aile üzerinde tayin etmemiz lâzımdır. Meselâ W tabiî adetler Tabiî ise, istikrâ ile Π (unsur : Tabiî) aile(unsur) olduğunu ispat etmek üzere şunları tayin etmeliyiz:

- 0 : Tabiî müessisinin üstündeki lifte bir unsur, muayyen nokta : aile(0), ve
- her sayı : Tabiî için bir tâbi, aile(sayı) → aile(ardıl(sayı)).

İkincisi, muayyen nokta : aile(0)'ın 0 : Tabiî müessisinin üstünde yatmasını umûmîleştirerek, ardıl : Tabiî → Tabiî müessisinin *üstünde* yatan bir "aile → aile" tâbisi olarak görülebilir.

Binâenaleyh benzetme ile, Π (unsur : Dâire) aile(unsur) olduğunu ispat etmek üzere şunları tayin etmeliyiz:

- kaide : Dâire müessisinin üstündeki lifte bir unsur, muayyen nokta : aile(kaide), ve
- muayyen noktadan muayyen noktaya, "ilmik : kaide = kaide müessisinin üstünde yatan" bir tarîk.

Dikkat edilsin ki Dâire, ilmikten başka tarîkler (aksiyet(kaide) ve "ilmik ∙ ilmik" gibi) ihtiva etse de, yalnız müessisin *kendisinin* üstünde yatan bir tarîk tayin etmemiz lâzımdır. Bu, Dâire'nin müessisleri tarafından "serbestçe tevlîd" olunduğu sezgisini ifade eder.

Bununla beraber suâl şudur: başka bir tarîkin "üstünde yatan" bir tarîke sahip olmak ne demektir? Bu kat'iyyen sadece muayyen nokta = muayyen nokta tarîki demek *değildir*; zîrâ o, aile(kaide) lifindeki bir tarîk olurdu (vaz'î olarak, kaidedeki *sâbit* tarîkin üstünde yatan bir tarîk). Hakikatte ise bu suâli ikinci babda zaten cevaplamıştık: Yardımcı kaziyye 2.3.4'ten evvelki müzakerede, tarîk : birinci unsur = ikinci unsur üstünde yatan, birinci hadd : aile(birinci unsur)'dan ikinci hadd : aile(ikinci unsur)'a bir tarîkin, aile(ikinci unsur) lifinde bir nakil(tarîk, birinci hadd) = ikinci hadd tarîki ile temsil edilebileceği neticesine varmıştık. Bu babda böyle **mütevakkıf tarîkler**den çokça istifade edeceğimiz için, onlara mahsus bir işaret getiriyoruz:

> (birinci hadd =[aile | tarîk] ikinci hadd) :≡ (nakil[aile](tarîk, birinci hadd) = ikinci hadd). (6.2.2)

**Tenbih 6.2.3.** Mütevakkıf tarîkleri tarif etmenin başka mümkün yolları da vardır. Meselâ nakil(tarîk, birinci hadd) = ikinci hadd yerine birinci hadd = nakil(tarîk⁻¹, ikinci hadd)'yi mülâhaza edebilirdik. Onu daha umûmî bir "gayr-ı mütecânis müsâvât"ın hususî bir hâli olarak, yahut bir istikrâî tip ailesi olarak doğrudan bir tarifle de elde edebilirdik. Bu tariflerin hepsi mütekâfi tipler verir; binâenaleyh o mânâda hangisini seçtiğimizin pek ehemmiyeti yoktur. Bununla beraber nakil(tarîk, birinci hadd) = ikinci hadd'yi tarif olarak seçmek, mütevakkıf tarîkler hakkında başka şeylere, meselâ mütevakkıf-tatbik[tâbi]'nin onları hâsıl ettiğine, yahut onları muayyen tip ailelerinde 2.5. bahisteki nakil yardımcı kaziyyelerini kullanarak hesap edebileceğimize hükmetmeyi en kolay kılar.

Mütevakkıf tarîkler mefhûmu elimizde iken, Dâire'nin istikrâ mebdeini şimdi daha dakik olarak ifade edebiliriz: aile : Dâire → kâinat ile beraber

- bir unsur, muayyen nokta : aile(kaide), ve
- bir tarîk, muayyen tarîk : muayyen nokta =[aile | ilmik] muayyen nokta

verilince, tâbi(kaide) ≡ muayyen nokta ve mütevakkıf-tatbik[tâbi](ilmik) = muayyen tarîk olacak şekilde bir tâbi : Π (unsur : Dâire) aile(unsur) vardır. Gayr-ı mütevakkıf hâlde olduğu gibi, tâbiyi tâbi(kaide) :≡ muayyen nokta ve mütevakkıf-tatbik[tâbi](ilmik) := muayyen tarîk ile tarif etmekten bahsederiz.

**Tenbih 6.2.4.** Bu istikrâ mebdeinin bir tatbikini gayr-ı sûrî olarak tarif ederken, onu "her unsur : Dâire için aile(unsur)" gayesinin iki hâle ayrılması sayarız; bunları bazan sırasıyla "unsur kaide olduğunda" ve "unsur ilmik boyunca değiştiğinde" gibi ibarelerle getireceğiz. "Bir tarîk boyunca değişmek"e hususî hiçbir riyâzî mânâ verilmemiştir: o sadece bir ispatın tekabül eden kısmının başlangıcını göstermenin elverişli bir yoludur; bir misal için bakınız Yardımcı kaziyye 6.4.2.

Vaz'î olarak, Dâire'nin istikrâ mebdei Şekil 6.1'de gösterildiği gibi tasavvur edilebilir. Dâire üzerinde bir lifleme (resimde bir simit sathı) verilince, bu liflemenin bir kesitini tarif etmek, kaidenin üstündeki lifte bir muayyen nokta ile beraber, ilmiğin üstünde yatan, muayyen noktadan muayyen noktaya bir tarîk vermekle aynıdır. Bunu, mütevakkıf tarîkler tarifimizi kullanarak tip nazariyesine göre tefsir ediş tarzımız Şekil 6.2'de gösterilmiştir: ilmiğin üstündeki, muayyen noktadan muayyen noktaya tarîk, kaidenin üstündeki lifte nakil(ilmik, muayyen nokta)'dan muayyen noktaya bir tarîk ile temsil edilir.

**Şekil 6.1.** Dâire için vaz'î istikrâ mebdei.

**Şekil 6.2.** Dâire için tip nazariyesine göre istikrâ mebdei. Şekildeki yazı: muayyen tarîk : nakil(ilmik, muayyen nokta) = muayyen nokta.

Elbette rücû' mebdeini, aileyi sâbit bir tip ailesi alarak istikrâ mebdeinden ispat edebilmeyi bekleriz. Hakikaten de böyledir; gerçi ilmiğe ait gayr-ı mütevakkıf hesap kaidesini (tatbik[tâbi]'ye atıf yapan) mütevakkıf olanından (mütevakkıf-tatbik[tâbi]'ye atıf yapan) çıkarmak şaşırtıcı derecede biraz ince bir iştir.

**Yardımcı kaziyye 6.2.5.** Eğer tip, nokta : tip ve tarîk : nokta =_{tip} nokta ile beraber bir tip ise,

> tâbi(kaide) :≡ nokta
>
> tatbik[tâbi](ilmik) := tarîk

olacak şekilde bir tâbi : Dâire → tip vardır.

*İspat.* Dâire'nin istikrâ mebdeini sâbit tip ailesine, (unsur ↦ tip) : Dâire → kâinat'a tatbik etmek isteriz. Bunun için lâzım gelen farzlar, (unsur ↦ tip)(kaide) ≡ tip'in bir noktası ki elimizde vardır (yâni nokta : tip), ve nokta =[(unsur ↦ tip) | ilmik] nokta içinde bir mütevakkıf tarîk, yahut mütekâfi olarak nakil[unsur ↦ tip](ilmik, nokta) = nokta'dır. Bu sonraki tip, tarîkin yaşadığı nokta =_{tip} nokta tipiyle aynı değildir, fakat ona mütekâfidir; zîrâ Yardımcı kaziyye 2.3.5 ile sâbit-nakil[tip](ilmik, nokta) : nakil[unsur ↦ tip](ilmik, nokta) = nokta elimizdedir. Binâenaleyh nokta : tip ve tarîk : nokta = nokta verilince şu terkibi mülâhaza edebiliriz:

> sâbit-nakil[tip](ilmik, nokta) ∙ tarîk : (nokta =[(unsur ↦ tip) | ilmik] nokta).

İstikrâ mebdeini tatbik ederek,

> tâbi(kaide) ≡ nokta ve (6.2.6)
>
> mütevakkıf-tatbik[tâbi](ilmik) = sâbit-nakil[tip](ilmik, nokta) ∙ tarîk (6.2.7)

olacak şekilde bir tâbi : Dâire → tip elde ederiz. Geriye tatbik[tâbi](ilmik) = tarîk müsâvâtını çıkarmak kalır. Bununla beraber Yardımcı kaziyye 2.3.8 ile

> mütevakkıf-tatbik[tâbi](ilmik) = sâbit-nakil[tip](ilmik, tâbi(kaide)) ∙ tatbik[tâbi](ilmik)

elimizdedir. Bunu (6.2.7) ile birleştirip sâbit-nakil'in (ki (6.2.6) ile aynıdırlar) zuhurlarını sadeleştirerek tatbik[tâbi](ilmik) = tarîk'i elde ederiz. ∎

Buna tekabül eden bir yeganelik mebdeimiz de vardır.

**Yardımcı kaziyye 6.2.8.** Eğer tip bir tip ve birinci tâbi, ikinci tâbi : Dâire → tip, iki müsâvât ile beraber iki tatbik ise:

> birinci müsâvât : birinci tâbi(kaide) =_{tip} ikinci tâbi(kaide),
>
> ikinci müsâvât : birinci tâbi(ilmik) =[(unsur ↦ unsur =_{tip} unsur) | birinci müsâvât] ikinci tâbi(ilmik),

o hâlde her unsur : Dâire için birinci tâbi(unsur) = ikinci tâbi(unsur) olur.

*İspat.* Dâire'nin istikrâ mebdeini aile(unsur) :≡ (birinci tâbi(unsur) = ikinci tâbi(unsur)) tip ailesinde tatbik ederiz. Unsur kaide olduğunda, birinci müsâvât tam ihtiyacımız olan şeydir. Unsur ilmik boyunca değiştiğinde ise birinci müsâvât =[(unsur ↦ birinci tâbi(unsur) = ikinci tâbi(unsur)) | ilmik] birinci müsâvât'a ihtiyacımız vardır; bu, Kaziyye 2.11.3 ve Kaziyye 2.11.5 ile ikinci müsâvâta irca olunabilir. ∎

Bu iki yardımcı kaziyye, dâirenin beklenen küllî hassasını gerektirir:

**Yardımcı kaziyye 6.2.9.** Her tip için tabiî bir tekâfü' vardır:

> (Dâire → tip) ≃ Σ (unsur : tip) (unsur = unsur).

*İspat.* gidiş(tatbik) :≡ (tatbik(kaide), tatbik[tatbik](ilmik)) ile tarif edilen kanonik bir gidiş : (Dâire → tip) → Σ (unsur : tip) (unsur = unsur) tâbisi vardır. Öteki istikamette, bir (muayyen nokta, muayyen tarîk) çiftini, dâirenin rücû' mebdeinin verdiği Dâire → tip tâbisine götürerek tarif edilen dönüş : Σ (unsur : tip) (unsur = unsur) → (Dâire → tip) vardır.

Şimdi rücû' mebdeinin hesap kaidesi ile gidiş ∘ dönüş ∼ ayniyet tâbisi olur. Dönüş ∘ gidiş ∼ ayniyet tâbisi ise yeganelik mebdei iledir; zîrâ yine dâirenin rücû' mebdeinin hesap kaidesi ile (dönüş ∘ gidiş)(ilmik) =[(unsur ↦ unsur =_{tip} unsur) | aksiyet(kaide)] ilmik olur. Binâenaleyh gidişin bir şibh-i tersi vardır ve binâenaleyh bir tekâfü'dür. ∎

5.5. bahiste olduğu gibi, Yardımcı kaziyye 6.2.9'un neticesinin, kaziyyevî hesap kaidelerine sahip bir istikrâ mebdeine sahip olmaya mütekâfi olduğunu gösterebiliriz. Başka yüksek istikrâî tipler de Yardımcı kaziyye 6.2.5 ile Yardımcı kaziyye 6.2.9'a benzer yardımcı kaziyyeleri sağlar; onların ispatlarını umûmiyetle okuyucuya bırakacağız. Şimdi birçok misali mülâhaza etmeye geçiyoruz.

## 6.3 Aralık

Aralık diye işaret ettiğimiz **aralık**, belki dâireden de basit bir yüksek istikrâî tiptir. Şunlar tarafından tevlîd olunur:

- bir nokta, Aralık-sıfırı : Aralık,
- bir nokta, Aralık-biri : Aralık, ve
- bir tarîk, kıt'a : Aralık-sıfırı =_{Aralık} Aralık-biri.

Aralığın rücû' mebdei der ki, bir hedef tip ile beraber

- bir nokta, birinci muayyen nokta : hedef tip,
- bir nokta, ikinci muayyen nokta : hedef tip, ve
- bir tarîk, muayyen tarîk : birinci muayyen nokta = ikinci muayyen nokta

verilince, tâbi(Aralık-sıfırı) ≡ birinci muayyen nokta, tâbi(Aralık-biri) ≡ ikinci muayyen nokta ve tatbik[tâbi](kıt'a) = muayyen tarîk olacak şekilde bir tâbi : Aralık → hedef tip vardır. İstikrâ mebdei der ki, aile : Aralık → kâinat ile beraber

- bir nokta, birinci muayyen nokta : aile(Aralık-sıfırı),
- bir nokta, ikinci muayyen nokta : aile(Aralık-biri), ve
- bir tarîk, muayyen tarîk : birinci muayyen nokta =[aile | kıt'a] ikinci muayyen nokta

verilince, tâbi(Aralık-sıfırı) ≡ birinci muayyen nokta, tâbi(Aralık-biri) ≡ ikinci muayyen nokta ve mütevakkıf-tatbik[tâbi](kıt'a) = muayyen tarîk olacak şekilde bir tâbi : Π (unsur : Aralık) aile(unsur) vardır.

Sırf tahavvül-i muttasıla kadar bakılırsa aralık hakikaten alâka çekici değildir:

**Yardımcı kaziyye 6.3.1.** Aralık tipi büzülebilirdir.

*İspat.* Her unsur : Aralık için unsur =_{Aralık} Aralık-biri olduğunu ispat ederiz. Başka bir tabirle, Π (unsur : Aralık) (unsur =_{Aralık} Aralık-biri) tipinde bir tâbi isteriz. Tâbiyi şu tarzda tarif etmeye başlarız:

> tâbi(Aralık-sıfırı) :≡ kıt'a : Aralık-sıfırı =_{Aralık} Aralık-biri,
>
> tâbi(Aralık-biri) :≡ aksiyet(Aralık-biri) : Aralık-biri =_{Aralık} Aralık-biri.

Geriye, kıt'a =[(unsur ↦ unsur =_{Aralık} Aralık-biri) | kıt'a] aksiyet(Aralık-biri) tipinde olması lâzım gelen mütevakkıf-tatbik[tâbi](kıt'a)'yı tarif etmek kalır. Tarif ile bu tip nakil(kıt'a, kıt'a) =_{(Aralık-biri =_{Aralık} Aralık-biri)} aksiyet(Aralık-biri)'dir; bu da kendi sırasında kıt'a⁻¹ ∙ kıt'a = aksiyet(Aralık-biri)'ye mütekâfidir. Fakat o tipin kanonik bir unsuru vardır: tarîk terslerinin filhakika ters olduklarının ispatı. ∎

Bununla beraber tip nazariyesi bakımından aralığın, tıpkı klasik tahavvül-i muttasıl nazariyesindeki vaz'î aralık gibi, yine bazı alâka çekici hususiyetleri vardır. Meselâ tâbi genişliğinin kolay bir ispatını vermemize imkân verir. (Elbette 4.9. bahiste olduğu gibi, aşağıdaki ispat müddetince tâbi genişliği mütearifesine dair umûmî farzımızı askıya alıyoruz.)

**Yardımcı kaziyye 6.3.2.** Eğer birinci tâbi, ikinci tâbi : tip → hedef tip, her unsur : tip için birinci tâbi(unsur) = ikinci tâbi(unsur) olacak şekilde iki tâbi ise, o hâlde tip → hedef tip tipinde birinci tâbi = ikinci tâbi olur.

*İspat.* Elimizdeki ispata tarîkler : Π (unsur : tip) (birinci tâbi(unsur) = ikinci tâbi(unsur)) diyelim. Her unsur : tip için bir uzatılmış-tarîk(unsur) : Aralık → hedef tip tâbisini şöyle tarif ederiz:

> uzatılmış-tarîk(unsur)(Aralık-sıfırı) :≡ birinci tâbi(unsur),
>
> uzatılmış-tarîk(unsur)(Aralık-biri) :≡ ikinci tâbi(unsur),
>
> uzatılmış-tarîk(unsur)(kıt'a) := tarîkler(unsur).

Şimdi bir aralık-tâbisi : Aralık → (tip → hedef tip)'yi şöyle tarif ederiz:

> aralık-tâbisi(aralık noktası) :≡ (unsur ↦ uzatılmış-tarîk(unsur)(aralık noktası)).

O hâlde aralık-tâbisi(Aralık-sıfırı), unsur ↦ uzatılmış-tarîk(unsur)(Aralık-sıfırı) tâbisidir; uzatılmış-tarîk(unsur)(Aralık-sıfırı) birinci tâbi(unsur) ile tarif edildiği için bu, birinci tâbiye müsavidir. Bunun gibi aralık-tâbisi(Aralık-biri) = ikinci tâbi elimizdedir ve binâenaleyh

> aralık-tâbisi(kıt'a) : birinci tâbi =_{(tip → hedef tip)} ikinci tâbi. ∎

Temrin 6.10'da okuyucudan, tam tâbi genişliği mütearifesinin ispatını Yardımcı kaziyye 6.3.2'den tamamlamasını istiyoruz.

## 6.4 Dâireler ve küreler

Dâire'yi şunlar tarafından tevlîd olunan yüksek istikrâî tip olarak zaten müzakere ettik:

- bir nokta, kaide : Dâire, ve
- bir tarîk, ilmik : kaide =_{Dâire} kaide.

Onun istikrâ mebdei der ki, aile : Dâire → kâinat ile beraber muayyen nokta : aile(kaide) ve muayyen tarîk : muayyen nokta =[aile | ilmik] muayyen nokta verilince, tâbi(kaide) ≡ muayyen nokta ve mütevakkıf-tatbik[tâbi](ilmik) = muayyen tarîk olacak şekilde tâbi : Π (unsur : Dâire) aile(unsur) elimizde olur. Onun gayr-ı mütevakkıf rücû' mebdei der ki, muayyen nokta : hedef tip ve muayyen tarîk : muayyen nokta = muayyen nokta ile beraber bir hedef tip verilince, tâbi(kaide) ≡ muayyen nokta ve tatbik[tâbi](ilmik) = muayyen tarîk olacak şekilde tâbi : Dâire → hedef tip elimizde olur.

Dâire'nin âdi olmadığını müşahede ederiz.

**Yardımcı kaziyye 6.4.1.** ilmik ≠ aksiyet(kaide).

*İspat.* ilmik = aksiyet(kaide) olduğunu farz edelim. O hâlde, unsur : tip ve tarîk : unsur = unsur ile beraber her tip için tâbi(kaide) :≡ unsur ve tatbik[tâbi](ilmik) := tarîk ile tarif edilen bir tâbi : Dâire → tip bulunduğundan,

> tarîk = tâbi(ilmik) = tâbi(aksiyet(kaide)) = aksiyet(unsur)

elimizde olur. Fakat bu, her tipin bir mecmûa olmasını gerektirir ki, gördüğümüz üzere bu doğru değildir (bakınız Misal 3.1.9). ∎

Dâire'nin şu alâka çekici hassası da vardır ki, aksi misaller menbaı olarak faydalıdır.

**Yardımcı kaziyye 6.4.2.** Π (unsur : Dâire) (unsur = unsur)'un, unsur ↦ aksiyet(unsur)'a müsavi olmayan bir unsuru vardır.

*İspat.* tâbi : Π (unsur : Dâire) (unsur = unsur)'yu Dâire istikrâsı ile tarif ederiz. Unsur kaide olduğunda tâbi(kaide) :≡ ilmik deriz. Şimdi unsur ilmik boyunca değiştiğinde (bakınız Tenbih 6.2.4), nakil[unsur ↦ unsur = unsur](ilmik, ilmik) = ilmik olduğunu göstermeliyiz. Bununla beraber 2.11. bahiste nakil[unsur ↦ unsur = unsur](birinci tarîk, ikinci tarîk) = birinci tarîk⁻¹ ∙ ikinci tarîk ∙ birinci tarîk olduğunu müşahede etmiştik; binâenaleyh göstermemiz lâzım gelen şey ilmik⁻¹ ∙ ilmik ∙ ilmik = ilmik'tir. Fakat bu, bir tersi sadeleştirmekle âşikârdır.

tâbi ≠ (unsur ↦ aksiyet(unsur)) olduğunu göstermek için tâbi(kaide) ≠ aksiyet(kaide) olduğunu göstermek kâfidir. Fakat tâbi(kaide) = ilmik'tir; binâenaleyh bu sadece evvelki yardımcı kaziyyedir. ∎

Meselâ bu, Dâire'yi ihtiva eden hiçbir kâinatın bir buudlu tip olamayacağını göstererek Misal 3.1.9'u genişletmemize imkân verir.

**Netice 6.4.3.** Eğer Dâire tipi bir kâinata mensup ise, o kâinat bir buudlu tip değildir.

*İspat.* Kâinattaki Dâire = Dâire tipi, vahdet ile, Dâire'nin zâtî tekâfü'lerinin Dâire ≃ Dâire tipine mütekâfidir; binâenaleyh Dâire ≃ Dâire'nin bir mecmûa olmadığını göstermek kâfidir. Bunun için onun ayniyet tipinin, ayniyet tâbisi(Dâire) =_{(Dâire ≃ Dâire)} ayniyet tâbisi(Dâire)'nin bir mahz kaziyye olmadığını göstermek kâfidir. Tekâfü' olmak bir mahz kaziyye olduğundan, bu tip ayniyet tâbisi(Dâire) =_{(Dâire → Dâire)} ayniyet tâbisi(Dâire)'ye mütekâfidir. Fakat tâbi genişliği ile bu, Yardımcı kaziyye 6.4.2'de gördüğümüz üzere müsavi olmayan iki unsur ihtiva eden Π (unsur : Dâire) (unsur = unsur)'a mütekâfidir. ∎

İki buudlu Küre'nin şunlar tarafından tevlîd olunan yüksek istikrâî tip olması lâzım geldiğini de zikretmiştik:

- bir nokta, kaide : Küre, ve
- kaide = kaide içinde iki buudlu bir tarîk, sath : aksiyet(kaide) = aksiyet(kaide).

Küre için rücû' mebdei güç değildir: o der ki, muayyen nokta : hedef tip ve muayyen sath : aksiyet(muayyen nokta) = aksiyet(muayyen nokta) ile beraber bir hedef tip verilince, tâbi(kaide) ≡ muayyen nokta ve ikinci-tatbik[tâbi](sath) = muayyen sath olacak şekilde tâbi : Küre → hedef tip elimizde olur. Burada "ikinci-tatbik[tâbi](sath)" ile, tâbinin funktorî amelinin iki buudlu tarîklere bir genişletilmesini kastediyoruz; bu, dakik olarak şöyle ifade edilebilir.

**Yardımcı kaziyye 6.4.4.** tâbi : tip → hedef tip ve birinci unsur, ikinci unsur : tip ve birinci tarîk, ikinci tarîk : birinci unsur = ikinci unsur ve yüksek tarîk : birinci tarîk = ikinci tarîk verilince, bir ikinci-tatbik[tâbi](yüksek tarîk) : tatbik[tâbi](birinci tarîk) = tatbik[tâbi](ikinci tarîk) tarîki elimizde olur.

*İspat.* Tarîk istikrâsı ile birinci tarîk ≡ ikinci tarîk ve yüksek tarîkin aksiyet olduğunu farz edebiliriz. Fakat o hâlde ikinci-tatbik[tâbi](aksiyet(birinci tarîk)) :≡ aksiyet(tatbik[tâbi](birinci tarîk)) diye tarif edebiliriz. ∎

Umûmî istikrâ mebdeini ifade etmek için, bu yardımcı kaziyyenin mütevakkıf tâbiler için bir şekline ihtiyacımız vardır; bu da kendi sırasında mütevakkıf iki buudlu tarîkler mefhûmunu gerektirir. Evvelce olduğu gibi böyle bir şeyi tarif etmenin birçok yolu vardır; biri, nakilin iki buudlu bir şekli vasıtasıyladır.

**Yardımcı kaziyye 6.4.5.** aile : tip → kâinat ve birinci unsur, ikinci unsur : tip ve birinci tarîk, ikinci tarîk : birinci unsur = ikinci unsur ve yüksek tarîk : birinci tarîk = ikinci tarîk verilince, her hadd : aile(birinci unsur) için ikinci-nakil(yüksek tarîk, hadd) : nakil(birinci tarîk, hadd) = nakil(ikinci tarîk, hadd) elimizde olur.

*İspat.* Tarîk istikrâsı ile. ∎

Şimdi birinci unsur, ikinci unsur : tip ve birinci tarîk, ikinci tarîk : birinci unsur = ikinci unsur ve yüksek tarîk : birinci tarîk = ikinci tarîk ile beraber birinci hadd : aile(birinci unsur) ve ikinci hadd : aile(ikinci unsur) noktaları ve birinci mütevakkıf tarîk : birinci hadd =[aile | birinci tarîk] ikinci hadd ve ikinci mütevakkıf tarîk : birinci hadd =[aile | ikinci tarîk] ikinci hadd mütevakkıf tarîkleri verilmiş olsun. Mütevakkıf tarîkler tarifimizle bu, birinci mütevakkıf tarîk : nakil(birinci tarîk, birinci hadd) = ikinci hadd ve ikinci mütevakkıf tarîk : nakil(ikinci tarîk, birinci hadd) = ikinci hadd demektir. Binâenaleyh yüksek tarîkin üstündeki mütevakkıf iki buudlu tarîklerin tipini şöyle tarif etmek makuldür:

> (birinci mütevakkıf tarîk =[aile | yüksek tarîk] ikinci mütevakkıf tarîk) :≡ (birinci mütevakkıf tarîk = ikinci-nakil(yüksek tarîk, birinci hadd) ∙ ikinci mütevakkıf tarîk).

Şimdi Yardımcı kaziyye 6.4.4'ün mütevakkıf şeklini ifade edebiliriz.

**Yardımcı kaziyye 6.4.6.** aile : tip → kâinat ve birinci unsur, ikinci unsur : tip ve birinci tarîk, ikinci tarîk : birinci unsur = ikinci unsur ve yüksek tarîk : birinci tarîk = ikinci tarîk ve bir tâbi : Π (unsur : tip) aile(unsur) verilince, ikinci-mütevakkıf-tatbik[tâbi](yüksek tarîk) : mütevakkıf-tatbik[tâbi](birinci tarîk) =[aile | yüksek tarîk] mütevakkıf-tatbik[tâbi](ikinci tarîk) elimizde olur.

*İspat.* Tarîk istikrâsı. ∎

Şimdi Küre için istikrâ mebdeini ifade edebiliriz: aile : Küre → kâinat ile beraber muayyen nokta : aile(kaide) ve muayyen sath : aksiyet(muayyen nokta) =[ikinci aile | sath] aksiyet(muayyen nokta) verildiğini farz edelim; burada ikinci aile :≡ (tarîk ↦ muayyen nokta =[aile | tarîk] muayyen nokta)'dır. O hâlde tâbi(kaide) ≡ muayyen nokta ve ikinci-mütevakkıf-tatbik[tâbi](sath) = muayyen sath olacak şekilde bir tâbi : Π (unsur : Küre) aile(unsur) vardır.

Elbette bu açık yaklaşım, buudda yükseldikçe gittikçe daha girift hâle gelir. Binâenaleyh her buud-sayısı için buud-sayısı buudlu küreleri tarif etmek istersek, daha muntazam bir fikre ihtiyacımız vardır. Bir yaklaşım, umûmî buud-sayısı buudlu tarîkler yerine doğrudan buud-sayısı buudlu ilmiklerle çalışmaktır.

2.1. bahisten *noktalı tipler* kâinatının ve buud-sayısı katlı İlmik-fezâsı : noktalı kâinat → noktalı kâinat'ın tariflerini hatırlayalım (Tarif 2.1.7 ve Tarif 2.1.8). Şimdi buud-sayısı buudlu Küre'yi, şunlar tarafından tevlîd olunan yüksek istikrâî tip olarak tarif edebiliriz:

- bir nokta, kaide : Küre[buud-sayısı], ve
- bir buud-sayısı buudlu ilmik, buud-sayısı ilmiği : buud-sayısı katlı İlmik-fezâsı(Küre[buud-sayısı], kaide).

Bu takdîm için istikrâ mebdeini yazmak üzere, bir "mütevakkıf buud-sayısı buudlu ilmik" mefhûmunu, mütevakkıf tâbilerin buud-sayısı buudlu ilmikler üzerindeki ameli ile beraber tarif etmemiz lâzım gelirdi. Bunu okuyucuya bırakıyoruz (bakınız Temrin 6.4); gelecek bahiste küreleri tarif etmenin, bazan daha kolay ele alınabilen farklı bir yolunu müzakere edeceğiz.

## 6.5 Ta'lîkler

Bir tipin **ta'lîki**, tipin noktalarını tarîklere (ve binâenaleyh tipteki tarîkleri iki buudlu tarîklere ve saire) çevirmenin küllî yoludur. O, şu müvellidlerle tarif edilen bir Ta'lîk(tip) tipidir:[^2]

[^2]: Mütevakkıf çift tipleriyle talihsiz bir işaret çakışması vardır; onlar da elbette bir Σ ile yazılır. Bununla beraber siyak umûmiyetle iltibası giderir.

- bir nokta, Şimal : Ta'lîk(tip),
- bir nokta, Cenub : Ta'lîk(tip), ve
- bir tâbi, nısfünnehâr : tip → (Şimal =_{Ta'lîk(tip)} Cenub).

İsimler bir çeşit "küre"yi, bir şimal kutbu, bir cenub kutbu ve birinden ötekine tipin her noktası için bir nısfünnehâr hattı ile hatırlatmak için konmuştur. Filhakika göreceğimiz üzere, eğer tip = Dâire ise, onun ta'lîki âdi bir kürenin sathına, Küre'ye mütekâfidir.

Ta'lîk(tip) için rücû' mebdei der ki, bir hedef tip ile beraber

- şimal-noktası, cenub-noktası : hedef tip noktaları ve
- bir nısfünnehâr-tâbisi : tip → (şimal-noktası = cenub-noktası)

verilince, tâbi(Şimal) ≡ şimal-noktası ve tâbi(Cenub) ≡ cenub-noktası olacak, ve her unsur : tip için tatbik[tâbi](nısfünnehâr(unsur)) = nısfünnehâr-tâbisi(unsur) olacak şekilde bir tâbi : Ta'lîk(tip) → hedef tip elimizde olur. Bunun gibi istikrâ mebdei der ki, aile : Ta'lîk(tip) → kâinat ile beraber

- bir nokta, şimal-noktası : aile(Şimal),
- bir nokta, cenub-noktası : aile(Cenub), ve
- her unsur : tip için bir tarîk, nısfünnehâr-tâbisi(unsur) : şimal-noktası =[aile | nısfünnehâr(unsur)] cenub-noktası

verilince, tâbi(Şimal) ≡ şimal-noktası ve tâbi(Cenub) ≡ cenub-noktası olacak, ve her unsur : tip için mütevakkıf-tatbik[tâbi](nısfünnehâr(unsur)) = nısfünnehâr-tâbisi(unsur) olacak şekilde bir tâbi : Π (unsur : Ta'lîk(tip)) aile(unsur) vardır.

Ta'lîke dair ilk müşahedemiz, onun dâireyi tarif etmenin başka bir yolunu vermesidir.

**Yardımcı kaziyye 6.5.1.** Ta'lîk(İkilik) ≃ Dâire.

*İspat.* gidiş : Ta'lîk(İkilik) → Dâire'yi rücû' ile, gidiş(Şimal) :≡ kaide ve gidiş(Cenub) :≡ kaide olacak, tatbik[gidiş](nısfünnehâr(İkilik-sıfırı)) := ilmik fakat tatbik[gidiş](nısfünnehâr(İkilik-biri)) := aksiyet(kaide) olacak şekilde tarif edelim. dönüş : Dâire → Ta'lîk(İkilik)'yi rücû' ile, dönüş(kaide) :≡ Şimal ve tatbik[dönüş](ilmik) := nısfünnehâr(İkilik-sıfırı) ∙ nısfünnehâr(İkilik-biri)⁻¹ olacak şekilde tarif edelim. Şimdi gidiş ile dönüşün şibh-i ters olduklarını gösteriyoruz.

Evvelâ istikrâ ile her unsur : Ta'lîk(İkilik) için dönüş(gidiş(unsur)) = unsur olduğunu gösteriyoruz. Eğer unsur ≡ Şimal ise, o hâlde dönüş(gidiş(Şimal)) ≡ dönüş(kaide) ≡ Şimal olur; binâenaleyh aksiyet(Şimal) : dönüş(gidiş(Şimal)) = Şimal elimizdedir. Eğer unsur ≡ Cenub ise, o hâlde dönüş(gidiş(Cenub)) ≡ dönüş(kaide) ≡ Şimal olur ve nısfünnehâr(İkilik-biri) : dönüş(gidiş(Cenub)) = Cenub müsâvâtını seçeriz. Geriye, her ikilik unsuru : İkilik için, unsur nısfünnehâr(ikilik unsuru) boyunca değiştikçe bu müsâvâtların muhafaza edildiğini göstermek kalır; bu da, aksiyet(Şimal) nısfünnehâr(ikilik unsuru) boyunca nakledildiğinde nısfünnehâr(İkilik-biri)'yi verdiğini söylemektir. Tarîk fezâlarında ve geri çekilmiş liflemelerde nakil ile bu, şunu göstermemiz lâzım geldiği demektir:

> tatbik[dönüş](tatbik[gidiş](nısfünnehâr(ikilik unsuru)))⁻¹ ∙ aksiyet(Şimal) ∙ nısfünnehâr(ikilik unsuru) = nısfünnehâr(İkilik-biri).

Elbette aksiyet(Şimal)'i sadeleştirebiliriz. Şimdi İkilik istikrâsı ile ya ikilik unsuru ≡ İkilik-sıfırı ya da ikilik unsuru ≡ İkilik-biri olduğunu farz edebiliriz. Eğer ikilik unsuru ≡ İkilik-sıfırı ise, o hâlde

> tatbik[dönüş](tatbik[gidiş](nısfünnehâr(İkilik-sıfırı)))⁻¹ ∙ nısfünnehâr(İkilik-sıfırı)
>
> = tatbik[dönüş](ilmik)⁻¹ ∙ nısfünnehâr(İkilik-sıfırı)
>
> = (nısfünnehâr(İkilik-sıfırı) ∙ nısfünnehâr(İkilik-biri)⁻¹)⁻¹ ∙ nısfünnehâr(İkilik-sıfırı)
>
> = nısfünnehâr(İkilik-biri) ∙ nısfünnehâr(İkilik-sıfırı)⁻¹ ∙ nısfünnehâr(İkilik-sıfırı)
>
> = nısfünnehâr(İkilik-biri)

elimizdedir; eğer ikilik unsuru ≡ İkilik-biri ise, o hâlde

> tatbik[dönüş](tatbik[gidiş](nısfünnehâr(İkilik-biri)))⁻¹ ∙ nısfünnehâr(İkilik-biri)
>
> = tatbik[dönüş](aksiyet(kaide))⁻¹ ∙ nısfünnehâr(İkilik-biri)
>
> = aksiyet(Şimal)⁻¹ ∙ nısfünnehâr(İkilik-biri)
>
> = nısfünnehâr(İkilik-biri)

elimizdedir. Binâenaleyh her unsur : Ta'lîk(İkilik) için dönüş(gidiş(unsur)) = unsur elimizdedir.

Şimdi istikrâ ile her unsur : Dâire için gidiş(dönüş(unsur)) = unsur olduğunu gösteriyoruz. Eğer unsur ≡ kaide ise, o hâlde gidiş(dönüş(kaide)) ≡ gidiş(Şimal) ≡ kaide olur; binâenaleyh aksiyet(kaide) : gidiş(dönüş(kaide)) = kaide elimizdedir. Geriye, unsur ilmik boyunca değiştikçe bu müsâvâtın muhafaza edildiğini göstermek kalır; bu da onun ilmik boyunca kendisine nakledildiğini söylemektir. Yine tarîk fezâlarında ve geri çekilmiş liflemelerde nakil ile bu, şunu göstermek demektir:

> tatbik[gidiş](tatbik[dönüş](ilmik))⁻¹ ∙ aksiyet(kaide) ∙ ilmik = aksiyet(kaide).

Bununla beraber

> tatbik[gidiş](tatbik[dönüş](ilmik)) = tatbik[gidiş](nısfünnehâr(İkilik-sıfırı) ∙ nısfünnehâr(İkilik-biri)⁻¹)
>
> = tatbik[gidiş](nısfünnehâr(İkilik-sıfırı)) ∙ tatbik[gidiş](nısfünnehâr(İkilik-biri))⁻¹
>
> = ilmik ∙ aksiyet(kaide)

elimizdedir; binâenaleyh bu kolayca çıkar. ∎

Vaz'î olarak iki noktalı İkilik fezâsı *sıfır buudlu küre* Küre[0] diye de bilinir. (Meselâ o, bir buudlu hakîkî fezâda mebdeden 1 mesafedeki noktaların fezâsıdır; tıpkı vaz'î bir buudlu kürenin iki buudlu hakîkî fezâda mebdeden 1 mesafedeki noktaların fezâsı olması gibi.) Binâenaleyh Yardımcı kaziyye 6.5.1 ima edici bir tarzda Ta'lîk(Küre[0]) ≃ Dâire diye ifade edilebilir. Filhakika bu kalıp devam eder: bütün küreleri istikrâ ile şöyle tarif edebiliriz:

> Küre[0] :≡ İkilik ve Küre[buud-sayısı + 1] :≡ Ta'lîk(Küre[buud-sayısı]). (6.5.2)

Hattâ Küre[−1] :≡ boş tip diye tarif ederek bir buud aşağıdan bile başlayabilir ve Ta'lîk(boş tip) ≃ İkilik olduğunu müşahede edebiliriz.

Bunun, evvelki bahisteki Küre[buud-sayısı] tarifiyle örtüştüğünü dikkatle ispat etmek, sonrakini daha açık kılmayı gerektirirdi. Bununla beraber rücûî tarifin, ötekinin sahip olmasını bekleyeceğimiz aynı küllî hassaya sahip olduğunu gösterebiliriz. Eğer (tip, tipin merkez noktası) ile (hedef tip, hedefin merkez noktası) noktalı tipler ise (merkez noktaları çoğu kere zımnî bırakılarak), Noktalı-Tatbikler(tip, hedef tip) merkezî tatbiklerin tipini göstersin:

> Noktalı-Tatbikler(tip, hedef tip) :≡ Σ (tâbi : tip → hedef tip) (tâbi(tipin merkez noktası) = hedefin merkez noktası).

Dikkat edilsin ki her tip, merkez noktası sağ-idhâl(birim-unsur) olan bir Noktası-eklenmiş(tip) :≡ tip + birim tip noktalı tipini doğurur; buna *munfasıl bir merkez noktası eklemek* denir.

**Yardımcı kaziyye 6.5.3.** Bir tip ve bir (hedef tip, hedefin merkez noktası) noktalı tipi için

> Noktalı-Tatbikler(Noktası-eklenmiş(tip), hedef tip) ≃ (tip → hedef tip)

elimizdedir.

Dikkat edilsin ki sağda tipten hedef tipe giden *merkezsiz* tâbilerin âdi tipi vardır.

*İspat.* Soldan sağa, tarîk : tâbi(sağ-idhâl(birim-unsur)) = hedefin merkez noktası ile beraber tâbi : Noktası-eklenmiş(tip) → hedef tip verilince, tâbi ∘ sol-idhâl : tip → hedef tip elimizdedir. Sağdan sola ise, ikinci tâbi : tip → hedef tip verilince, uzatılmış tâbi : Noktası-eklenmiş(tip) → hedef tip'i uzatılmış tâbi(sol-idhâl(unsur)) :≡ ikinci tâbi(unsur) ve uzatılmış tâbi(sağ-idhâl(birim-hadd)) :≡ hedefin merkez noktası ile tarif ederiz. Bunların şibh-i ters ameliyeler olduğunu göstermeyi okuyucuya bırakıyoruz. ∎

Bilhassa dikkat edilsin ki İkilik ≃ Noktası-eklenmiş(birim tip)'tir. Binâenaleyh her noktalı hedef tip için

> Noktalı-Tatbikler(İkilik, hedef tip) ≃ (birim tip → hedef tip) ≃ hedef tip

elimizdedir. Şimdi hatırlayalım ki İlmik-fezâsı ameliyesi noktalı tipler üzerinde amel eder ve tarifi İlmik-fezâsı(tip, merkez noktası) :≡ (merkez noktası =_{tip} merkez noktası, aksiyet(merkez noktası))'dır. Ta'lîki de Ta'lîk(tip, merkez noktası) :≡ (Ta'lîk(tip), Şimal) ile noktalı tipler üzerinde amel ettirebiliriz.

**Yardımcı kaziyye 6.5.4.** (tip, tipin merkez noktası) ile (hedef tip, hedefin merkez noktası) noktalı tipleri için

> Noktalı-Tatbikler(Ta'lîk(tip), hedef tip) ≃ Noktalı-Tatbikler(tip, İlmik-fezâsı(hedef tip))

elimizdedir.

*İspat.* Evvelâ şu tekâfü' silsilesini müşahede ederiz:

> Noktalı-Tatbikler(Ta'lîk(tip), hedef tip) :≡ Σ (tâbi : Ta'lîk(tip) → hedef tip) (tâbi(Şimal) = hedefin merkez noktası)
>
> ≃ Σ (tâbi : Σ (şimal-noktası : hedef tip) Σ (cenub-noktası : hedef tip) (tip → (şimal-noktası = cenub-noktası))) (birinci-izdüşüm(tâbi) = hedefin merkez noktası)
>
> ≃ Σ (şimal-noktası : hedef tip) Σ (cenub-noktası : hedef tip) (tip → (şimal-noktası = cenub-noktası)) × (şimal-noktası = hedefin merkez noktası)
>
> ≃ Σ (çift : Σ (şimal-noktası : hedef tip) (şimal-noktası = hedefin merkez noktası)) Σ (cenub-noktası : hedef tip) (tip → (birinci-izdüşüm(çift) = cenub-noktası))
>
> ≃ Σ (cenub-noktası : hedef tip) (tip → (hedefin merkez noktası = cenub-noktası))

Birinci tekâfü', ta'lîklerin küllî hassası iledir; bu hassa şunu söyler:

> (Ta'lîk(tip) → hedef tip) ≃ (Σ (şimal-noktası : hedef tip) Σ (cenub-noktası : hedef tip) (tip → (şimal-noktası = cenub-noktası)))

ve sağdan sola giden tâbi rücû' edici ile verilir (bakınız Temrin 6.11). İkinci ve üçüncü tekâfü'ler, bileşenlerin yeniden tertibi ile beraber Temrin 2.10 iledir. Nihayet sonuncu tekâfü' Yardımcı kaziyye 3.11.9'dan çıkar; zîrâ Yardımcı kaziyye 3.11.8 ile Σ (şimal-noktası : hedef tip) (şimal-noktası = hedefin merkez noktası), merkezi (hedefin merkez noktası, aksiyet(hedefin merkez noktası)) olmak üzere büzülebilirdir.

İspat şu tekâfü' silsilesi ile tamamlanır:

> Σ (cenub-noktası : hedef tip) (tip → (hedefin merkez noktası = cenub-noktası))
>
> ≃ Σ (cenub-noktası : hedef tip) Σ (tâbi : tip → (hedefin merkez noktası = cenub-noktası)) Σ (tarîk : hedefin merkez noktası = cenub-noktası) (tâbi(tipin merkez noktası) = tarîk)
>
> ≃ Σ (çift : Σ (cenub-noktası : hedef tip) (hedefin merkez noktası = cenub-noktası)) Σ (tâbi : tip → (hedefin merkez noktası = birinci-izdüşüm(çift))) (tâbi(tipin merkez noktası) = ikinci-izdüşüm(çift))
>
> ≃ Σ (tâbi : tip → (hedefin merkez noktası = hedefin merkez noktası)) (tâbi(tipin merkez noktası) = aksiyet(hedefin merkez noktası))
>
> ≡ Noktalı-Tatbikler(tip, İlmik-fezâsı(hedef tip)).

Evvelki gibi birinci ve sonuncu tekâfü'ler Yardımcı kaziyye 3.11.9 ve Yardımcı kaziyye 3.11.8 ile, ikincisi ise Temrin 2.10 ve bileşenlerin yeniden tertibi iledir. ∎

Bilhassa (6.5.2)'deki gibi tarif edilen küreler için

> Noktalı-Tatbikler(Küre[buud-sayısı], hedef tip) ≃ Noktalı-Tatbikler(Küre[buud-sayısı − 1], İlmik-fezâsı(hedef tip)) ≃ ⋯ ≃ Noktalı-Tatbikler(İkilik, buud-sayısı katlı İlmik-fezâsı(hedef tip)) ≃ buud-sayısı katlı İlmik-fezâsı(hedef tip)

elimizdedir. Binâenaleyh bu Küre[buud-sayısı] küreleri, 6.4. bahisteki gibi doğrudan buud-sayısı katlı ilmik fezâları cinsinden tarif edilen kürelerden bekleyeceğimiz küllî hassaya sahiptir.

## 6.6 Hücre mürekkebleri

Klasik hendese-i vaz'iyyede bir *hücre mürekkebi*, kursların hudutları boyunca birbiri ardınca iliştirilmesiyle elde edilen bir fezâdır. Eğer buud-sayısı buudlu bir kursun hududunun, buudu buud-sayısından kat'iyyen küçük olan kurslarda (yâni buud-sayısı eksi bir iskeletinde) yatmasına kayıt konmuşsa ona bir *CW mürekkebi* denir.

Her mütenâhî CW mürekkebi, buud-sayısı buudlu kursları buud-sayısı buudlu tarîklere çevirerek ve iliştirme tatbikinin sûretini, her biri daha aşağı buudlu tarîklerin bir terkibi olarak yazılan bir mebde ile bir müntehâya bölerek, bir yüksek istikrâî tip olarak takdim edilebilir. 6.4. bahisteki Dâire ve Küre açık tariflerimiz bu şekildeydi.

Başka bir misal, şunlar tarafından tevlîd olunan Simit'tir:

- bir nokta, merkez : Simit,
- bir tarîk, birinci tarîk : merkez = merkez,
- başka bir tarîk, ikinci tarîk : merkez = merkez, ve
- iki buudlu bir tarîk, sath : birinci tarîk ∙ ikinci tarîk = ikinci tarîk ∙ birinci tarîk.

Bunun bir simit olduğunu görmenin belki en kolay yolu, birinci köşe, ikinci köşe, üçüncü köşe, dördüncü köşe diye dört köşesi, üst kenar, sağ kenar, sol kenar, alt kenar diye dört kenarı ve "üst kenar ∙ sağ kenar"dan "sol kenar ∙ alt kenar"a giden âşikâr bir iki buudlu tarîk olan bir içi bulunan bir müstatille başlamaktır:

> birinci köşe =(üst kenar)= ikinci köşe; birinci köşe =(sol kenar)= üçüncü köşe; ikinci köşe =(sağ kenar)= dördüncü köşe; üçüncü köşe =(alt kenar)= dördüncü köşe; içi ⇓ iç.

Şimdi sol kenarı sağ kenarla ve alt kenarı üst kenarla aynîleştirin; bunun neticesinde dört köşenin hepsi de aynîleştirilmiş olur. Vaz'î olarak bu aynîleştirmenin bir simit hâsıl ettiği görülebilir.

Simit için istikrâ mebdei şimdiye kadar yazdıklarımızın en incesidir. aile : Simit → kâinat verilince, bir Π (unsur : Simit) aile(unsur) kesiti için şunlar lâzımdır:

- bir nokta, muayyen merkez : aile(merkez),
- bir tarîk, muayyen birinci tarîk : muayyen merkez =[aile | birinci tarîk] muayyen merkez,
- bir tarîk, muayyen ikinci tarîk : muayyen merkez =[aile | ikinci tarîk] muayyen merkez, ve
- sathın üstünde yatan, "muayyen birinci tarîk ∙ muayyen ikinci tarîk" ile "muayyen ikinci tarîk ∙ muayyen birinci tarîk" "terkipleri" arasında iki buudlu bir tarîk, muayyen sath.

Bu son mu'tânın mânâlı olması için mütevakkıf tarîkler için bir terkip ameliyesine ihtiyacımız vardır, fakat bunu tarif etmek güç değildir. O hâlde istikrâ mebdei, tâbi(merkez) ≡ muayyen merkez ve mütevakkıf-tatbik[tâbi](birinci tarîk) = muayyen birinci tarîk ve mütevakkıf-tatbik[tâbi](ikinci tarîk) = muayyen ikinci tarîk olacak, ve "ikinci-mütevakkıf-tatbik[tâbi](sath) = muayyen sath" gibi bir şey olacak şekilde bir tâbi : Π (unsur : Simit) aile(unsur) verir. Bununla beraber bu, bu hâliyle tip itibarıyla iyi kurulmuş değildir; evvelâ mütevakkıf-tatbik[tâbi](birinci tarîk) = muayyen birinci tarîk ve mütevakkıf-tatbik[tâbi](ikinci tarîk) = muayyen ikinci tarîk müsâvâtları hükmî olmadığı için, ikinci olarak mütevakkıf-tatbik[tâbi] tarîk terkibini ancak tahavvül-i muttasıla kadar muhafaza ettiği için. Tafsilâtı okuyucuya bırakıyoruz (bakınız Temrin 6.1).

Elbette simidin başka bir tarifi Simit :≡ Dâire × Dâire'dir (Temrin 6.3'te okuyucudan bu ikisinin tekâfü'ünü tahkik etmesini istiyoruz). Bununla beraber hücre mürekkebi tarifi, böyle tavsifleri olmayan başka fezâlara, meselâ Klein şişesine, izdüşüm sathına ve saireye kolayca umûmîleştirilir. Fakat istikrâ mebdelerini yazmak gittikçe daha güç hâle gelir ve mütevakkıf buud-sayısı buudlu tarîkler ile buud-sayısı buudlu tarîkler üzerinde amel eden mütevakkıf-tatbik mefhûmlarını tarif etmemizi gerektirir. Bereket versin, küreler elimizde olunca bunun etrafından dolaşmanın bir yolu vardır.

## 6.7 Göbekler ve parmaklar

Hendese-i vaz'iyyede umûmiyetle CW mürekkeblerini buud-sayısı buudlu kursları onların buud-sayısı eksi bir buudlu hudut kürelerine iliştirerek kurmaktan bahsedilir. Bununla beraber bunu ifade etmenin başka bir yolu, buud-sayısı eksi bir buudlu bir kürenin *mahrûtu*nu yapıştırmaktır. Yâni bir kursu, bir mahrût noktasından (yahut "göbek"ten), o noktayı hududun her noktasına muttasıl olarak bağlayan nısfünnehâr hatlarıyla (yahut "parmaklar"la) mürekkeb sayarız; Şekil 6.3'te gösterildiği gibi.

**Şekil 6.3.** Bir göbekle parmaklardan yapılmış iki buudlu bir kurs.

Bu fikri, bir buuddan büyük buud-sayısı için buud-sayısı buudlu tarîk müessisleri ihtiva eden yüksek istikrâî tipleri, yalnız bir buudlu tarîk müessisleri ihtiva edenler cinsinden ifade etmek için kullanabiliriz. Mesele şudur ki buud-sayısı buudlu bir tarîki, buud-sayısı eksi bir buudlu bir nesne ile mukayyed bir buudlu tarîklerin muttasıl bir ailesi olarak elde edebiliriz. Kullanılacak en basit buud-sayısı eksi bir buudlu nesne buud-sayısı eksi bir buudlu küredir; gerçi bazı hâllerde başka biri tercih edilebilir. (Hatırlansın ki 6.5. bahiste küreleri, yalnız bir buudlu tarîk müessislerini içine alan ta'lîkleri kullanarak istikrâ ile tarif edebilmiştik. Filhakika ta'lîk de bu fikrin bir nümûnesi sayılabilir; zîrâ ta'lîk edilen tip ile mukayyed bir buudlu tarîklerin bir ailesini içine alır.)

Meselâ evvelki bahisteki Simit, onun yerine şunlar tarafından tevlîd olunan tip olarak tarif edilebilirdi:

- bir nokta, merkez : Simit,
- bir tarîk, birinci tarîk : merkez = merkez,
- başka bir tarîk, ikinci tarîk : merkez = merkez,
- bir nokta, göbek : Simit, ve
- her unsur : Dâire için bir tarîk, parmak(unsur) : sınır-tâbisi(unsur) = göbek; burada sınır-tâbisi : Dâire → Simit, sınır-tâbisi(kaide) :≡ merkez ve tatbik[sınır-tâbisi](ilmik) := birinci tarîk ∙ ikinci tarîk ∙ birinci tarîk⁻¹ ∙ ikinci tarîk⁻¹ ile tarif edilir.

Simidin bu şekli için istikrâ mebdei der ki, aile : Simit → kâinat verilince, bir Π (unsur : Simit) aile(unsur) kesiti için şunlar lâzımdır:

- bir nokta, muayyen merkez : aile(merkez),
- bir tarîk, muayyen birinci tarîk : muayyen merkez =[aile | birinci tarîk] muayyen merkez,
- bir tarîk, muayyen ikinci tarîk : muayyen merkez =[aile | ikinci tarîk] muayyen merkez,
- bir nokta, muayyen göbek : aile(göbek), ve
- her unsur : Dâire için bir tarîk, mütevakkıf sınır-tâbisi(unsur) =[aile | parmak(unsur)] muayyen göbek; burada mütevakkıf sınır-tâbisi : Π (unsur : Dâire) aile(sınır-tâbisi(unsur)), mütevakkıf sınır-tâbisi(kaide) :≡ muayyen merkez ve mütevakkıf-tatbik[mütevakkıf sınır-tâbisi](ilmik) := dönüştürme-tekâfü'ü(muayyen birinci tarîk ∙ muayyen ikinci tarîk ∙ (muayyen birinci tarîk)⁻¹ ∙ (muayyen ikinci tarîk)⁻¹) ile tarif edilir. Sonrakinde "∙" mütevakkıf tarîklerin terkibini gösterir ve dönüştürme-tekâfü'ü : (muayyen merkez =[aile | tatbik[sınır-tâbisi](ilmik)] muayyen merkez) ≃ (muayyen merkez =[aile ∘ sınır-tâbisi | ilmik] muayyen merkez)'nün tarifi okuyucuya bırakılmıştır.

Dikkat edilsin ki mütevakkıf iki buudlu tarîklere yahut ikinci-mütevakkıf-tatbik'e hiç ihtiyaç yoktur. Hesap kaidelerini yazmayı okuyucuya bırakıyoruz.

**Tenbih 6.7.1.** Göbek noktasının getirilmesinin lüzumu sorgulanabilir; niçin onun yerine, Şekil 6.4'te gösterildiği gibi, kursun hududunu o hududun *üzerindeki* bir noktaya muttasıl olarak bağlayan tarîkleri sadece ekleyemezdik? Bununla beraber bu, daha başka bir tadil olmaksızın işlemez. Zîrâ bir sınır-tâbisi : Dâire → fezâ verilince, her sınır-tâbisi(unsur)'u sınır-tâbisi(kaide)'ye bağlayan bir tarîk müessisi verirsek, nihayet elde ettiğimiz şey daha çok, Şekil 6.5'teki resim gibi, tepesi etrafında burulup tabanındaki bir noktaya yapıştırılmış bir mahrûta benzer. Mesele şudur ki sınır-tâbisi(kaide)'den kendisine tayin edilen tarîk aksiyet olmayabilir. Bunu temin etmek için iki buudlu bir tarîk müessisi ekleyerek meseleyi giderebilirdik; fakat ayrı bir göbek kullanmak 1'den yüksek buudlu herhangi bir tarîk müessisine ihtiyacı ortadan kaldırır.

**Şekil 6.4.** Göbeksiz parmaklar.

**Şekil 6.5.** Göbeksiz parmaklar, ikinci.

**Tenbih 6.7.2.** Şuna da dikkat edilsin ki yüksek tarîklerin bir buudlu tarîklere bu "tercüme"si, bu tarîkler için hükmî hesap kaidelerini muhafaza etmez, gerçi kaziyyevî olanları muhafaza eder.
