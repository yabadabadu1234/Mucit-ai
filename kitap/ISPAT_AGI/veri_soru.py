SORULAR = []
HUCRELER = []
FELSEFELER = []
OLUMSUZ = []

IHTILAFLI_SIFAT = ('hikmet',)

SIFAT_C1 = {
    'semi': 'Vâcib işitme kemâlinden mahrum değildir; işitmeme (sağırlık) noksanı Vâcib’de bulunamaz.',
    'basar': 'Vâcib görme kemâlinden mahrum değildir; görmeme (körlük) noksanı Vâcib’de bulunamaz.',
    'kelam': 'Vâcib konuşma kemâlinden mahrum değildir; konuşamama (dilsizlik) noksanı Vâcib’de bulunamaz. Fiilen konuştuğu, yani bildirdiği H3’ün meselesidir.',
    'tekvin': 'Vâcib’in var etme (tekvîn) kemâli vardır: var etmeye kâdirdir ve var eder. Bunun kudret ve iradenin taalluku mu ayrı bir ezelî sıfat mı olduğu c4’tedir.',
}

SIFAT_C4 = {
    'semi': ('ilimden ayrı sıfat', 'Semi’ ilimden ayrı, zâta zâid ezelî bir sıfattır (ilme döndürülmez).',
             'kelâm içi ihtilaf: Mu’tezile ilme döndürür (hafızadan, yoklanmadı); Mâtürîdî’nin Kâ’bî’ye karşı aktarımı V.2.12.7 ve V.2.12.10’dadır; kitap ortak çekirdeği (c1) iddia eder, bu hücreyi iddia etmez ve çürütmez (V.2.1.10)'),
    'basar': ('ilimden ayrı sıfat', 'Basar ilimden ayrı, zâta zâid ezelî bir sıfattır (ilme döndürülmez).',
              'kelâm içi ihtilaf: Mu’tezile ilme döndürür (hafızadan, yoklanmadı); kitap ortak çekirdeği (c1) iddia eder, bu hücreyi iddia etmez ve çürütmez (V.2.1.10)'),
    'kelam': ('kelâm-ı nefsî', 'Kelâm, zâtla kâim, ezelî ve mahlûk olmayan bir sıfattır (kelâm-ı nefsî); okunan ve yazılan lafız bunun mecazî adıdır ve hâdistir.',
              'kelâm içi ihtilaf: Kâ’bî ve Mu’tezile kelâmı hâdis sayar (Mâtürîdî’nin aktarımı V.2.13.1–19); Mâtürîdî’nin cevabı V.2.13.20–31; kelâm-ı nefsî ve lafzî ayrımı V.3.1.6; kitap ortak çekirdeği (c1) iddia eder, bu hücreyi iddia etmez (V.2.1.10)'),
    'tekvin': ('ayrı ezelî sıfat', 'Tekvîn, kudret ve iradeden ayrı, ezelî bir sıfattır (Mâtürîdî sayımı).',
               'kelâm içi ihtilaf: Mâtürîdî ayrı sıfat sayar (V.2.11); Eş’arî kudret ve iradeye döndürür (hafızadan, yoklanmadı); kitap ortak çekirdeği (c1) iddia eder, bu hücreyi iddia etmez (V.2.1.10)'),
}

SIFATLAR = [
    ('kidem', 'kıdem (ezelîlik)', 'zâtî', ''),
    ('beka', 'bekâ (yokluğun gelmemesi)', 'zâtî', ''),
    ('gina', 'gınâ (kıyam bi-nefsih: kendiyle kâim, hiçbir şeye muhtaç olmama)', 'zâtî', ''),
    ('hayat', 'hayat', 'subûtî', ''),
    ('ilim', 'ilim', 'subûtî', ''),
    ('kudret', 'kudret', 'subûtî', ''),
    ('irade', 'irade', 'subûtî', ''),
    ('semi', 'semi’ (işitme)', 'subûtî', 'ortak çekirdek c1, ilme dönüş ihtilafı c4 (V.2.1.10)'),
    ('basar', 'basar (görme)', 'subûtî', 'ortak çekirdek c1, ilme dönüş ihtilafı c4 (V.2.1.10)'),
    ('kelam', 'kelâm', 'subûtî', 'ortak çekirdek c1, kelâm-ı nefsî ve lafzî ihtilafı c4 (V.3.1.6)'),
    ('tekvin', 'tekvîn', 'subûtî', 'ortak çekirdek c1, ayrı sıfat mı kudret ve iradeye dönüş mü c4 (V.2.1.10)'),
    ('hikmet', 'hikmet (gâyeli fiil)', 'fiilî-kemâl', 'Allah’a vâcib olan bir şey yoktur kaidesi gözetilir (V.3.2.1)'),
    ('adalet', 'adâlet (zulümden münezzehlik)', 'fiilî-kemâl', 'insanî mânâ ile aynı mı: müşterek lafız ayrımı (V.2.4.2)'),
    ('rahmet', 'rahmet', 'fiilî-kemâl', 'insanî mânâ ile aynı mı: müşterek lafız ayrımı (V.2.4.2)'),
    ('sidk', 'sıdk (yalan ve noksandan münezzehlik)', 'fiilî-kemâl', 'H5’in köprüsü (V.5.1)'),
]


def S(id, ad, metin, hasir, hasir_notu, grup, atif, ust_hucre=''):
    SORULAR.append(dict(id=id, ad=ad, metin=metin, hasir=hasir, hasir_notu=hasir_notu, grup=grup, atif=atif, ust_hucre=ust_hucre))


def H(id, soru, ad, metin, hukum, tur, kapsam_cerhi=(), alt_soru='', not_=''):
    HUCRELER.append(dict(id=id, soru=soru, ad=ad, metin=metin, hukum=hukum, tur=tur, kapsam_cerhi=list(kapsam_cerhi), alt_soru=alt_soru, not_=not_))


def F(id, ad, aile, aciklama, hucreler, not_=''):
    FELSEFELER.append(dict(id=id, ad=ad, aile=aile, aciklama=aciklama, hucreler=list(hucreler), not_=not_))


def O(hucre, sonuc, tur, usul=''):
    OLUMSUZ.append(dict(hucre=hucre, sonuc=sonuc, tur=tur, usul=usul))


S('Q18', 'Ortak zemin: akıl ve evveliyyât', 'Aklın evveliyyâtı geçerli midir; doğru bilgi mümkün müdür?', 'aklî',
  'Doğru bilgi ya mümkündür ya değildir; değilse ya hakikat yoktur ya hakikat kişiye göredir ya hakikat vardır fakat bilinemez.',
  'zemin', 'V.0.3; V.0.4; I.7.3.8')
H('Q18.c1', 'Q18', 'geçerli', 'Aklın evveliyyâtı geçerlidir ve doğru bilgi mümkündür.', 'DOĞRU', 'zemin')
H('Q18.c2', 'Q18', 'hakikat yok', 'Hakikat yoktur (inâdiyye).', 'YANLIŞ', 'zemin')
H('Q18.c3', 'Q18', 'hakikat kişiye göre', 'Hakikat kişiye göredir (indiyye).', 'YANLIŞ', 'zemin')
H('Q18.c4', 'Q18', 'bilinemez', 'Hakikat vardır fakat hiçbir şey bilinemez (lâedriyye).', 'YANLIŞ', 'zemin')

S('Q00', 'Sebep ilkesi', 'Var olmaya başlayan her şeyin bir muhdisi var mıdır ve bu bilinir mi?', 'aklî',
  'İlke ya doğrudur ve bilinir, ya yanlıştır, ya doğruluk durumu bilinemez; her ilke hakkındaki hüküm bu üçünden biridir.',
  'zemin', 'V.1.4.3; V.1.4.9; V.0.3 tenkit')
H('Q00.c1', 'Q00', 'ilke doğru', 'Var olmaya başlayan her şeyin bir muhdisi vardır ve bu ilke doğrudur ve bilinir.', 'DOĞRU', 'zemin', not_='tartışmalı evveliyyât (zayıf=2)')
H('Q00.c2', 'Q00', 'sebepsiz hâdis', 'Bazı hâdisler sebepsiz meydana gelir (ilke yanlıştır).', 'YANLIŞ', 'zemin')
H('Q00.c3', 'Q00', 'ilke bilinemez', 'İlkenin doğru mu yanlış mı olduğu bilinemez; zorunlu bağ gösterilemez.', 'YANLIŞ', 'zemin')

S('Q01', 'İmkân', 'Vâcib kavramı tutarlı mıdır, yani Vâcib aklen mümkün müdür (mümteni değil midir)?', 'aklî',
  'Çelişki ya yoktur ya vardır; varsa ya kavramın kendi parçaları arasındadır ya kavramla kavram dışındaki kesin bir öncül arasındadır.',
  'Vâcib', 'I.4.1.4; I.4.1.6')
H('Q01.c1', 'Q01', 'tutarlı', 'Vâcib kavramı tutarlıdır; Vâcib aklen imkânsız değildir (mümkündür).', 'DOĞRU', 'kavram')
H('Q01.c2', 'Q01', 'parçalar çelişir', 'Kavramın kendi parçaları çelişir: zâtından var olan, kendi kendinin sebebi olmayı gerektirir.', 'YANLIŞ', 'kavram')
H('Q01.c3', 'Q01', 'dış öncülle çelişir', 'Kavramın parçaları çelişmez, fakat kavram dışındaki kesin bir öncülle bağdaşmaz: zorunluluk yalnız önermelere aittir, bir varlık zorunlu olamaz.', 'YANLIŞ', 'kavram')

S('Q02', 'Vücûd', 'Hiç değilse bir vâcib var mıdır?', 'aklî', 'Bir şey ya vardır ya yoktur (çelişmezlik ve üçüncü şıkkın imkânsızlığı).', 'Vâcib', 'V.1')
H('Q02.c1', 'Q02', 'vardır', 'Mümkinler bütününün dışında, varlığı zâtından olan en az bir Vâcib vardır.', 'DOĞRU', 'vacib-varlik')
H('Q02.c2', 'Q02', 'yoktur', 'Hiçbir vâcib yoktur.', 'YANLIŞ', 'vacib-varlik', alt_soru='Q03')

S('Q03', 'Vâcib yoksa mümkinlerin açıklaması', 'Hiçbir vâcib yoksa mümkinlerin varlığı nasıl açıklanır?', 'aklî',
  'Mümkinler ya yoktur ya vardır; varsa bütünün müreccihi ya yoktur ya vardır; varsa mümkinlerin içinden olmak zorundadır ve ya sonsuz doğrusal zincir ya dairesel zincir ya kendi kendinin sebebi olur.',
  'Vâcib', 'V.1.3.b; V.1.3.a', ust_hucre='Q02.c2')
H('Q03.c1', 'Q03', 'mümkin yok', 'Mümkin diye bir şey yoktur (varlık kuruntudur).', 'YANLIŞ', 'vacib-varlik')
H('Q03.c2', 'Q03', 'bütün sebepsiz', 'Mümkinler vardır ve bütünlerinin bir müreccihi yoktur (sebepsiz olgu).', 'YANLIŞ', 'vacib-varlik')
H('Q03.c3', 'Q03', 'sonsuz zincir', 'Mümkinlerin müreccihi, geriye doğru sonsuz giden mümkinler zinciridir.', 'YANLIŞ', 'vacib-varlik')
H('Q03.c4', 'Q03', 'dairesel zincir', 'Mümkinlerin müreccihi, kendi içinde dönen (dairesel) mümkinler zinciridir.', 'YANLIŞ', 'vacib-varlik')
H('Q03.c5', 'Q03', 'kendi kendine', 'Mümkinler bütünü kendi kendinin müreccihidir.', 'YANLIŞ', 'vacib-varlik')

S('Q04', 'Vâcibin sayısı', 'Vâcib kaç tanedir (sıfır durumu Q02.c2’dir)?', 'aklî',
  'En az bir vâcib varken sayı ya birdir ya ikiden çoktur; ikiden çok ya iki ya sonlu fazla ya sonsuzdur.', 'Vâcib', 'V.2.1')
H('Q04.c1', 'Q04', 'bir', 'Vâcib tamı tamına birdir.', 'DOĞRU', 'sayi')
H('Q04.c2', 'Q04', 'iki', 'Vâcib iki tanedir.', 'YANLIŞ', 'sayi')
H('Q04.c3', 'Q04', 'sonlu çok', 'Vâcib üç veya daha fazla, fakat sonlu sayıdadır.', 'YANLIŞ', 'sayi', kapsam_cerhi=['Q04.c2'])
H('Q04.c4', 'Q04', 'sonsuz çok', 'Vâcib sonsuz sayıdadır.', 'YANLIŞ', 'sayi', kapsam_cerhi=['Q04.c2'])

S('Q05', 'Basitlik', 'Vâcib basit midir, yoksa bir terkibi var mıdır?', 'istikrâî',
  'Terkip ya yoktur ya vardır; varsa türleri (maddî parça, zihnî parça, zât–sıfat, zât içi ayrım) sayımla bulunmuştur; sayım zannîdir (I.1.3.7).',
  'Vâcib', 'V.2.1.6; V.2.1.10')
H('Q05.c1', 'Q05', 'basit', 'Vâcib basittir: parçası ve terkibi yoktur (kelâm içi zât–sıfat ihtilafı hariç).', 'DOĞRU', 'tenzih')
H('Q05.c2', 'Q05', 'maddî parçalar', 'Vâcib maddî (hâricî) parçalardan terkiplidir.', 'YANLIŞ', 'tenzih')
H('Q05.c3', 'Q05', 'zihnî parçalar', 'Vâcib zihnî parçalardan (cins–fasıl veya mahiyet–vücûd) terkiplidir.', 'YANLIŞ', 'tenzih')
H('Q05.c4', 'Q05', 'zât–sıfat terkibi', 'Sıfatlar zâta zâid kadîm şeylerdir (zât–sıfat ilişkisi).', 'İHTİLAFLI', 'tenzih', not_='kelâm içi ihtilaf; kitap ortak çekirdeği iddia eder, bu hücreyi iddia etmez ve çürütmez (V.2.1.10)')
H('Q05.c5', 'Q05', 'zât içi ayrım', 'Tek zâtın içinde birbirinden ayrı üç bireysel kimlik (ukûnum) vardır.', 'YANLIŞ', 'tenzih', kapsam_cerhi=['Q04.c2', 'Q05.c3'], not_='Teslis’in kendi kaynakları okunmadan ilzam yazılmaz (V.2.3.8)')

S('Q06', 'Âlemle münasebet', 'Vâcib ile âlem arasındaki münasebet nedir?', 'aklî',
  'İkisi ya aynıdır ya aynı değildir; aynı değilse biri öbürünün parçasıdır ya hiçbiri değildir (ayrıdır).', 'Vâcib', 'V.2.1.9; V.2.3.5')
H('Q06.c1', 'Q06', 'özdeş', 'Vâcib ile (değişen mümkinlerle birlikte) âlem özdeştir (tek varlık).', 'YANLIŞ', 'tenzih')
H('Q06.c2', 'Q06', 'Vâcib parça', 'Vâcib, mümkin parçalarla birlikte tek bir bütünün parçasıdır ve bütünsüz var olmaz.', 'YANLIŞ', 'tenzih')
H('Q06.c3', 'Q06', 'âlem Vâcib’in parçası', 'Âlem Vâcib’in bir parçasıdır (Vâcib âlemi içerir ve ondan fazlasıdır).', 'YANLIŞ', 'tenzih', kapsam_cerhi=['Q05.c2'])
H('Q06.c4', 'Q06', 'ayrı', 'Vâcib âlemden ayrıdır: ne âlemdir ne âlemin parçasıdır ne âlem onun parçasıdır.', 'DOĞRU', 'tenzih')

S('Q07', 'Cisimlik ve mekân', 'Vâcib cisim midir; değilse mekânla sınırlı mıdır?', 'aklî',
  'Cisim ya vardır ya yoktur; cisim değilse mekânla sınırlı ya vardır ya yoktur.', 'Vâcib', 'V.2.1.7; V.2.1.8')
H('Q07.c1', 'Q07', 'cisim', 'Vâcib cisimdir.', 'YANLIŞ', 'tenzih', kapsam_cerhi=['Q05.c2'])
H('Q07.c2', 'Q07', 'cisim değil mekânsız', 'Vâcib cisim değildir ve mekânla sınırlı değildir.', 'DOĞRU', 'tenzih')
H('Q07.c3', 'Q07', 'cisim değil mekânlı', 'Vâcib cisim değildir fakat bir mekânla sınırlıdır.', 'YANLIŞ', 'tenzih')

S('Q08', 'Hulûl ve ittihâd', 'Vâcib bir mümkinle birleşir mi?', 'aklî',
  'Birleşme ya vardır ya yoktur; varsa ya birinin ötekine yerleşmesidir (hulûl) ya ikisinin bir olmasıdır (ittihâd).', 'Vâcib', 'V.2.1.9')
H('Q08.c1', 'Q08', 'hulûl', 'Vâcib bir mümkine (âleme veya bir şeye) hulûl eder, yani içine yerleşir.', 'YANLIŞ', 'tenzih')
H('Q08.c2', 'Q08', 'ittihâd', 'Vâcib bir mümkinle ittihâd eder, yani ikisi bir olur.', 'YANLIŞ', 'tenzih')
H('Q08.c3', 'Q08', 'birleşmez', 'Vâcib hiçbir mümkine hulûl veya ittihâd etmez.', 'DOĞRU', 'tenzih')

S('Q09', 'Âlemle fiil', 'Vâcib âlemin fâili midir; öyleyse ihtiyarlı mıdır, yaratıp bırakmış mıdır?', 'aklî',
  'Fâillik ya yoktur ya vardır; varsa zorunludur ya ihtiyarlıdır; ihtiyarlıysa fiil ya yalnız başlangıçtadır ya her an sürer.', 'Vâcib', 'V.1.5; V.2.2.3')
H('Q09.c1', 'Q09', 'fâil değil', 'Vâcib âlemin fâili değildir (âlem Vâcib’den bağımsız var olur).', 'YANLIŞ', 'fiil', kapsam_cerhi=['Q06.c1', 'Q04.c2'])
H('Q09.c2', 'Q09', 'zorunlu sudûr', 'Vâcib âlemin zorunlu (ihtiyarsız) sebebidir; âlem O’ndan taşar ve ezelîdir.', 'YANLIŞ', 'fiil')
H('Q09.c3', 'Q09', 'yarattı bıraktı', 'Vâcib âlemi ihtiyarla yarattı ve bıraktı; bekâsını sürdürmez.', 'YANLIŞ', 'fiil')
H('Q09.c4', 'Q09', 'ihtiyarla kayyûm', 'Vâcib âlemi ihtiyarla var etmiştir ve her an var edip ayakta tutar (kayyûm).', 'DOĞRU', 'fiil')

S('Q11', 'İlmin kapsamı', 'Vâcib neyi bilir?', 'istikrâî',
  'Kapsam ya her şeydir ya her şeyden bir kısmı dışarıda kalır; dışarıda kalan ya kendi dışındaki her şeydir, ya cüz’îlerin tamamıdır, ya yalnız gelecek cüz’îlerdir; sayım zannîdir (I.1.3.7).',
  'sıfat', 'V.2.2.1')
H('Q11.c1', 'Q11', 'yalnız kendini', 'Vâcib yalnız kendini bilir; âlemi bilmez.', 'YANLIŞ', 'sifat')
H('Q11.c2', 'Q11', 'küllî', 'Vâcib kendini ve küllîleri bilir, cüz’îleri bilmez.', 'YANLIŞ', 'sifat')
H('Q11.c3', 'Q11', 'her şey', 'Vâcib küllî ve cüz’î, geçmiş ve gelecek her şeyi bilir.', 'DOĞRU', 'sifat')
H('Q11.c4', 'Q11', 'gelecek hariç', 'Vâcib geleceğin cüz’îlerini bilmez (gelecek henüz belirlenmemiştir).', 'YANLIŞ', 'sifat')

S('Q12', 'Vücûbun illeti', 'Vâcib neden zorunlu olarak vardır?', 'aklî',
  'Açıklama ya vardır ya yoktur; varsa zâtındandır ya zâtı dışındandır; yoksa ya olması gerekirdi ama yoktur ya olması gerekmez.', 'Vâcib', 'I.4.6.16; V.1.4.7')
H('Q12.c1', 'Q12', 'zâtından', 'Vâcib zâtı gereği vardır; vücûbunun zâtı dışında bir sebebi yoktur ve sebep sorusu zâtına döner.', 'DOĞRU', 'illet')
H('Q12.c2', 'Q12', 'başka sebepten', 'Vâcib’in vücûbu zâtı dışında bir sebepten gelir.', 'YANLIŞ', 'illet')
H('Q12.c3', 'Q12', 'çıplak olgu', 'Vâcib’in vücûbunun açıklaması olması gerekirdi fakat yoktur (çıplak, açıklamasız olgu).', 'YANLIŞ', 'illet')
H('Q12.c4', 'Q12', 'soru geçersiz', 'Vâcib için ‘neden’ sorusu anlamsızdır; açıklama aranmaz.', 'YANLIŞ', 'illet')

S('Q13', 'Âlemin başlangıcı', 'Âlem hâdis midir?', 'aklî',
  'Âlemin başlangıcı ya vardır ya yoktur; yoksa ya zorunludur ya mümkindir.', 'Vâcib', 'V.1.3.a; V.1.3.b.10')
H('Q13.c1', 'Q13', 'hâdis', 'Âlem hâdistir (başlangıcı vardır).', 'DOĞRU', 'vacib-varlik', not_='kelâm çizgisi; Vâcib’in varlığı bu hükme bağlı değildir (V.1.3.b.10)')
H('Q13.c2', 'Q13', 'kadîm vâcib', 'Âlem kadîmdir ve zorunludur (âlemin kendisi vâcibdir).', 'YANLIŞ', 'vacib-varlik', kapsam_cerhi=['Q06.c1'])
H('Q13.c3', 'Q13', 'kadîm mümkin', 'Âlem kadîmdir fakat mümkindir: ezelden beri Vâcib’e muhtaçtır.', 'İHTİLAFLI', 'vacib-varlik', not_='Vâcib’in varlığıyla çelişmez; kelâm hâdis, felsefe kadîm der; sonucu Q09.c2 ile ilişkilidir')

S('Q14', 'Mutlak kemâl', 'Vâcib’in kemâli mutlak mıdır?', 'aklî',
  'Kemâl ya sınırsızdır ya sınırlıdır; sınırlıysa sınır ya sabittir ya değişir.', 'Vâcib', 'V.2.2.5; V.2.3.6')
H('Q14.c1', 'Q14', 'mutlak', 'Vâcib hiçbir kemâlden mahrum değildir (kemâli mutlaktır).', 'DOĞRU', 'sifat')
H('Q14.c2', 'Q14', 'sınırlı sabit', 'Vâcib’in kemâli sınırlıdır ve sınırı sabittir.', 'YANLIŞ', 'sifat')
H('Q14.c3', 'Q14', 'gelişen', 'Vâcib’in kemâli sınırlıdır ve zamanla gelişir veya değişir.', 'YANLIŞ', 'sifat')

S('Q15', 'Ulûhiyet', 'İbadete (nihaî bağlılığa) lâyık olan kimdir?', 'aklî',
  'İbadete lâyık olanlar kümesi ya yalnız Vâcib’dir, ya Vâcib ve başkalarıdır, ya Vâcib dışındakilerdir, ya boştur.', 'Vâcib', 'V.2.3')
H('Q15.c1', 'Q15', 'yalnız Vâcib', 'İbadete lâyık olan yalnız Vâcib’dir.', 'DOĞRU', 'ulûhiyet')
H('Q15.c2', 'Q15', 'Vâcib ve başkaları', 'İbadete lâyık olan Vâcib’in yanında başkaları da vardır (aracı ilâhlar, kutsal varlıklar).', 'YANLIŞ', 'ulûhiyet')
H('Q15.c3', 'Q15', 'Vâcib hariç', 'İbadete lâyık olan Vâcib dışındaki şeylerdir; Vâcib ilgisizdir.', 'YANLIŞ', 'ulûhiyet', kapsam_cerhi=['Q09.c3'])
H('Q15.c4', 'Q15', 'hiç kimse', 'İbadete lâyık hiç kimse yoktur (ibadet kavramı boştur).', 'YANLIŞ', 'ulûhiyet')

S('Q16', 'Nizamın sebebi', 'Âlemdeki nizam ve ayarın sebebi nedir?', 'aklî',
  'Nizamın sebebi ya tesadüftür ya zorunluluktur ya kasıttır (V.1.3.c.2).', 'Vâcib', 'V.1.3.c')
H('Q16.c1', 'Q16', 'tesadüf', 'Nizamın sebebi tesadüftür (çoklu evren ve ince ayar rastlantısı).', 'YANLIŞ', 'vacib-varlik')
H('Q16.c2', 'Q16', 'zorunluluk', 'Nizamın sebebi maddenin zâtından gelen zorunluluktur.', 'YANLIŞ', 'vacib-varlik')
H('Q16.c3', 'Q16', 'kasıt', 'Nizamın sebebi ilim ve iradeli bir fâilin kasdıdır.', 'DOĞRU', 'vacib-varlik', not_='netice zan-ı gâlip düzeyindedir (V.1.3.c.7)')

S('Q17', 'Bilinebilirlik', 'Vâcib’in varlığı hangi derecede bilinebilir?', 'aklî',
  'Bilgi ya yakîn derecesindedir ya yalnız zan derecesindedir ya hiçbir derecede değildir.', 'Vâcib', 'I.3.1; V.0.2.6')
H('Q17.c1', 'Q17', 'yakîn', 'Vâcib’in varlığı yakîn derecesinde bilinebilir.', 'DOĞRU', 'bilgi')
H('Q17.c2', 'Q17', 'yalnız zan', 'Vâcib’in varlığı yalnız zan derecesinde bilinebilir.', 'YANLIŞ', 'bilgi')
H('Q17.c3', 'Q17', 'bilinemez', 'Vâcib’in varlığı hiçbir derecede bilinemez (ilkesel olarak).', 'YANLIŞ', 'bilgi')

S('Q19', 'Kudretin kapsamı', 'Vâcib’in kudreti hangi mümkinlere yetişir?', 'aklî',
  'Kudret ya bir kısım mümkini dışarıda bırakır ya bütün mümkinlere yetişir; bütün mümkinlere yetişiyorsa ya dereceli ya derecesizdir.',
  'sıfat', 'V.2.2.26; Risâle derlemesi s.166, 171')
H('Q19.c1', 'Q19', 'hepsine, derecesiz', 'Vâcib’in kudreti bütün mümkinlere yetişir ve hiçbirine diğerinden daha zor gelmez (kudret derecesizdir).', 'DOĞRU', 'sifat')
H('Q19.c2', 'Q19', 'bir kısmı dışarıda', 'Bir kısım mümkin, Vâcib’in kudretinden bağımsız olarak (esbabın, tabiatın veya başka bir fâilin eliyle) var olur.', 'YANLIŞ', 'sifat')
H('Q19.c3', 'Q19', 'hepsine, dereceli', 'Vâcib’in kudreti bütün mümkinlere yetişir fakat dereceli olup bazılarında zorlanır.', 'YANLIŞ', 'sifat')

for sid, ad, grup, ihtilaf in SIFATLAR:
    S('Q10.' + sid, 'Sıfat: ' + ad, 'Vâcib ‘' + ad + '’ sıfatına sahip midir?', 'aklî',
      'Bir sıfat Vâcib için ya zorunludur ya mümkindir ya imkânsızdır (kip hasırı, aklî).', 'sıfat', 'V.2.2' + ('; ' + ihtilaf if ihtilaf else ''))
    H('Q10.' + sid + '.c1', 'Q10.' + sid, 'zorunlu', SIFAT_C1.get(sid, 'Vâcib ‘' + ad + '’ sıfatına zorunlu olarak sahiptir.'), 'İHTİLAFLI' if sid in IHTILAFLI_SIFAT else 'DOĞRU', 'sifat', not_=ihtilaf)
    H('Q10.' + sid + '.c2', 'Q10.' + sid, 'mümkin', 'Vâcib için ‘' + ad + '’ sıfatı mümkindir (olabilir de olmayabilir de).', 'YANLIŞ', 'sifat')
    H('Q10.' + sid + '.c3', 'Q10.' + sid, 'imkânsız', 'Vâcib için ‘' + ad + '’ sıfatı imkânsızdır (Vâcib bu sıfata sahip olamaz).', 'YANLIŞ', 'sifat')
    if sid in SIFAT_C4:
        H('Q10.' + sid + '.c4', 'Q10.' + sid, SIFAT_C4[sid][0], SIFAT_C4[sid][1], 'İHTİLAFLI', 'sifat', not_=SIFAT_C4[sid][2])

F('F01', 'Katı ateizm (ontolojik, cezmî)', 'maddeci', 'Allah yoktur, hiçbir vâcib yoktur diye hükmeder.', ['Q02.c2', 'Q03.c2'])
F('F02', 'Sebepsiz olgu savunusu (brute fact evrenciliği)', 'maddeci', 'Evren veya mümkinler bütünü açıklanması gerekmeyen çıplak olgudur (hafızadan: Russell tarzı).', ['Q03.c2', 'Q00.c2'])
F('F03', 'Ezelî madde (dehrîler, tabîiyyûn, diyalektik maddecilik)', 'maddeci', 'Madde ve enerji ezelî ve zorunludur; Allah’tan bağımsız vâcib madde vardır.', ['Q06.c1', 'Q13.c2', 'Q07.c1'], 'madde vâcib sayıldığında Q02.c1 doğru, fakat Allah yerine madde konur; çürütme Q06, Q07, Q13’tedir')
F('F04', 'Sonsuz geriye sebep zinciri (kozmik döngü, sonsuz geçmiş evren modelleri)', 'maddeci', 'Her mümkin başka bir mümkinden gelir ve zincir geriye sonsuza gider.', ['Q03.c3'])
F('F05', 'Karşılıklı bağlı doğuş (Budist pratîtyasamutpâda’ya yaklaşık okuma)', 'Doğu', 'Varlıklar birbirinin sebebidir; ilk sebep yoktur.', ['Q03.c4', 'Q03.c3'], 'yaklaşık eşleme; kendi kaynağı okunmadan ilzam yazılmaz')
F('F06', 'Kendi kendini var eden evren', 'maddeci', 'Evren kendi kendinin sebebidir (sınırsız evren önerileri; hafızadan: Hartle–Hawking’in felsefî okunuşu).', ['Q03.c5'])
F('F07', 'Solipsizm ve ontolojik nihilizm', 'şüpheci', 'Mümkin diye bir şey yoktur; varlık kuruntudur.', ['Q03.c1'])
F('F08', 'Kuantum sebepsizliğine dayanan sebepsiz hâdis savunusu', 'maddeci', 'Bazı hâdisler sebepsiz meydana gelir; ontolojik olarak sebepsizlik vardır.', ['Q00.c2'])
F('F09', 'Hume şüpheciliği (nedensellik zorunlu bağ değil, alışkanlıktır)', 'şüpheci', 'Sebep ilkesinin doğruluğu bilinemez.', ['Q00.c3'])
F('F10', 'Kant (kozmolojik delilin sınırı; saf aklın metafizikte sınırı)', 'şüpheci', 'Sebep ilkesi tecrübe alanıyla sınırlıdır; Vâcib bilinemez.', ['Q00.c3', 'Q17.c3', 'Q17.c2'])
F('F11', 'Güçlü agnostisizm', 'şüpheci', 'Vâcib’in varlığı ilkesel olarak bilinemez.', ['Q17.c3'])
F('F12', 'Bilimcilik ve mantıkî pozitivizm (sınanamayan anlamsızdır)', 'şüpheci', 'Duyuyla sınanamayan metafizik cümle anlamsızdır.', ['Q17.c3', 'Q01.c3'])
F('F13', 'Zorunlu varlık anlamsızdır (Findlay ve Quine çizgisi; hafızadan)', 'analitik', 'Zorunluluk yalnız önermelere aittir; zorunlu varlık kavramı boştur.', ['Q01.c3'])
F('F14', 'Çok tanrıcılık', 'çok tanrıcı', 'Birden fazla ilâh vardır.', ['Q04.c3', 'Q04.c4', 'Q15.c2'])
F('F15', 'Düalizm (iki ezelî ilke)', 'çok tanrıcı', 'İyilik ve kötülük gibi iki zıt ezelî ilke vardır.', ['Q04.c2'])
F('F16', 'Teslis (üçlü bireysel kimlik)', 'Ehl-i kitap', 'Tek zâtta üç ayrı ukûnum vardır.', ['Q05.c5', 'Q04.c2'], 'kaynak okunmadan ilzam yazılmaz (V.2.3.8)')
F('F17', 'Panteizm ve vahdet-i vücûd (Spinoza tarzı, Advaita okuması)', 'bütüncü', 'Allah ile âlem özdeştir.', ['Q06.c1'], 'Spinoza’da töz ile kipler ayrılırsa eşleme kısmidir; kaynak okunmadan ilzam yazılmaz')
F('F18', 'Panenteizm', 'bütüncü', 'Âlem Allah’ın içindedir ve Allah âlemden fazlasıdır.', ['Q06.c3'])
F('F19', 'Stoacı pnevma (Allah âlemin içkin ruhudur)', 'bütüncü', 'Vâcib kozmosun bir parçası ve düzenleyici ilkedir.', ['Q06.c2'])
F('F20', 'Müşebbihe ve mücessime', 'teşbihçi', 'Allah’ın cismi ve yönü vardır.', ['Q07.c1', 'Q07.c3'])
F('F21', 'Hulûl (enkarnasyon ve ifratçı sûfî iddiaları)', 'bütüncü', 'Allah bir mümkine yerleşir.', ['Q08.c1'])
F('F22', 'İttihâd', 'bütüncü', 'Allah bir mümkinle bir olur.', ['Q08.c2'])
F('F23', 'Deizm (yarattı ve bıraktı)', 'deist', 'Allah vardır, âlemi yaratmıştır ve bekâsını sürdürmez.', ['Q09.c3', 'Q15.c3'])
F('F24', 'Sudûrcu felsefeciler (ihtiyarsız taşma; hafızadan: Fârâbî ve İbn Sînâ çizgisi)', 'felsefeci', 'Âlem Vâcib’den zorunlu olarak taşar ve ezelîdir.', ['Q09.c2', 'Q13.c3'])
F('F25', 'Aristo (Birinci Hareket Ettirici yalnız kendini düşünür)', 'felsefeci', 'Vâcib kendini bilir, âlemi bilmez ve fâili değildir.', ['Q11.c1', 'Q09.c1'])
F('F26', 'Felsefeciler (küllîleri bilir, cüz’îleri bilmez; hafızadan: İbn Sînâ)', 'felsefeci', 'Vâcib’in ilmi küllîlerle sınırlıdır.', ['Q11.c2'])
F('F27', 'Açık teizm (gelecek henüz belirlenmemiştir)', 'çağdaş teist', 'Vâcib geleceği bilmez ve zamanla değişir.', ['Q11.c4', 'Q14.c3'])
F('F28', 'Süreç teolojisi (Tanrı gelişir)', 'çağdaş teist', 'Vâcib’in kemâli gelişir veya değişir.', ['Q14.c3'])
F('F29', 'Gnostik demiurge ve sınırlı tanrı', 'çok tanrıcı', 'Kemâli sınırlı ve noksanlıklı bir yaratıcı vardır.', ['Q14.c2', 'Q19.c3'])
F('F30', 'Sıfatsız mutlak (Vedânta’da nirguna Brahman’a yaklaşık okuma; Yeni-Eflâtuncu Bir)', 'Doğu', 'Mutlak varlık sıfatsız ve şuursuzdur.', ['Q10.hayat.c3', 'Q10.ilim.c3', 'Q10.irade.c3', 'Q10.kudret.c3'], 'yaklaşık eşleme; kaynak okunmadan ilzam yazılmaz')
F('F31', 'Taoist ilke (şuursuz Tao’ya yaklaşık okuma)', 'Doğu', 'Mutlak ilke şuursuz ve iradesizdir.', ['Q10.ilim.c3', 'Q10.irade.c3'], 'yaklaşık eşleme')
F('F32', 'Sıfat nefyi (Cehmiyye ve ileri Mu’tezile; hafızadan)', 'kelâm içi', 'Allah’a ilim, kudret ve diğer sıfatlar isnat edilemez.', ['Q10.hayat.c3', 'Q10.ilim.c3', 'Q10.kudret.c3', 'Q10.irade.c3', 'Q10.semi.c3', 'Q10.basar.c3', 'Q10.kelam.c3'], 'kaynak okunmadan ilzam yazılmaz')
F('F33', 'Mu’tezile (sıfatlar zâtın aynıdır)', 'kelâm içi', 'Zât–sıfat ayrımı yoktur; sıfatlar zâtın aynıdır.', ['Q05.c4'], 'ihtilaflı; kitap iddia etmez')
F('F46', 'Tabiatçılık ve esbaba bağımsız tesir verme (Risâle derlemesinin “ehl-i tabiat” tarifi)', 'maddeci', 'Bir kısım varlıklar Vâcib’in kudretinden bağımsız olarak maddenin ve esbabın kendi tesiriyle var olur.', ['Q19.c2'], 'Risâle derlemesinin tarifidir; kendi kaynakları okunmadı; ikinci derece sebepleri Vâcib’in kudreti dahilinde sayan görüş bu felsefe değildir')
F('F34', 'Şansa ve tesadüfe dayanan ince ayar açıklamaları (çoklu evren)', 'maddeci', 'Nizam rastlantıdır; çok sayıda evrenden biri yaşama elverişlidir.', ['Q16.c1'])
F('F35', 'Zorunlu madde nizamı (nizam maddenin zâtındandır)', 'maddeci', 'Nizam maddenin zâtından gelir; başka türlü olamazdı.', ['Q16.c2'])
F('F36', 'Hakikatin yokluğu (inâdiyye)', 'sofist', 'Hakikat yoktur.', ['Q18.c2'])
F('F37', 'Görecelik (indiyye)', 'sofist', 'Hakikat kişiye göredir.', ['Q18.c3'])
F('F38', 'Bilinemezcilik (lâedriyye)', 'sofist', 'Hiçbir şey bilinemez.', ['Q18.c4'])
F('F39', 'İbadetin boş sayılması (ahlâk ve kayıtsızlık)', 'şüpheci', 'İbadete lâyık kimse yoktur.', ['Q15.c4'])
F('F40', 'Vâcib’in illetsiz olgu sayılması (Allah da çıplak olgudur)', 'şüpheci', 'Allah da açıklaması olmayan bir olgudur.', ['Q12.c3', 'Q12.c4'])
F('F41', 'Vâcib’in başka sebepten gelmesi (üst ilke tasavvurları)', 'Doğu', 'Mutlak varlığın da bir üst sebebi veya zemini vardır.', ['Q12.c2'])
F('F42', 'Ehl-i sünnet kelâmı (Mâtürîdî ve Eş’arî ortak çekirdeği)', 'kelâm içi', 'Vâcib birdir, basittir, mücerrettir, ihtiyarlı fâildir, mutlak kemâl sahibidir.', ['Q02.c1', 'Q04.c1', 'Q05.c1', 'Q06.c4', 'Q07.c2', 'Q08.c3', 'Q09.c4', 'Q11.c3', 'Q12.c1', 'Q14.c1', 'Q15.c1'], 'doğru cevapla uyumlu; ikinci derece ihtilaflar (V.2.1.10) iddia edilmez')
F('F43', 'Mu’tezile (semi’ ve basar ilmin kendisidir)', 'kelâm içi', 'İşitme ve görme ayrı sıfat değil, ilmin işitilen ve görülene taalluku olarak ilme döner.', ['Q10.semi.c4', 'Q10.basar.c4'], 'ihtilaflı; kitap iddia etmez; Mu’tezile bilgisi hafızadandır, kaynak okunmadı')
F('F44', 'Tekvînin ayrı sıfat sayılmaması (kudret ve iradeye dönüş)', 'kelâm içi', 'Var etme ayrı bir ezelî sıfat değil, kudret ve iradenin taallukudur.', ['Q10.tekvin.c4'], 'ihtilaflı; kitap iddia etmez; hafızadan, yoklanmadı')
F('F45', 'Kelâmın hâdis sayılması (Kâ’bî ve Mu’tezile; Mâtürîdî’nin aktarımıyla)', 'kelâm içi', 'Allah’ın kelâmı yaratılmıştır; zâtla kâim ezelî bir kelâm sıfatı yoktur.', ['Q10.kelam.c4'], 'ihtilaflı; kitap iddia etmez; Kâ’bî’nin kendi kitabı okunmadı (V.2.12–V.2.13)')

O('Q01.c1', 'Vâcib mümteni ise hiçbir mümkin müreccihini bulamaz; fakat mümkinler vardır (m_mumkin): çelişki.', 'ÇELİŞKİ', 'U07')
O('Q02.c1', 'Hiçbir vâcib yoksa mümkinlerin varlığı beş yoldan birinde açıklanmak zorundadır (Q03): mümkin yok, bütün sebepsiz, sonsuz zincir, devir, kendi kendine; hepsi ayrı ayrı çürüğüdür.', 'ÇELİŞKİ-ZİNCİR', 'U08')
O('Q02.c1', 'Vâcib yoksa ‘mümkinler vardır’ (müşâhede) ile ‘her mümkin bir müreccih ister’ birlikte doğru olamaz.', 'ÇELİŞKİ-KOŞULLU', 'U03')
O('Q04.c1', 'İki vâcib olsaydı ya irade çatışması veya ayrım için bir terkip doğardı; ikisi de vâcib olmayı bozar.', 'ÇELİŞKİ', 'U07')
O('Q05.c1', 'Vâcib terkipli olsaydı parçalarına muhtaç olurdu; muhtaç olan mümkindir; vâcib olmazdı.', 'ÇELİŞKİ', 'U07')
O('Q06.c4', 'Vâcib âlemle özdeş olsaydı değişirdi; değişen vâcib olamaz.', 'ÇELİŞKİ', 'U07')
O('Q07.c2', 'Vâcib cisim olsaydı parçalı ve arazlı olurdu; muhtaç olan vâcib olmaz.', 'ÇELİŞKİ', 'U07')
O('Q08.c3', 'Hulûl muhtaçlıktır; ittihâd çelişmezliğe aykırıdır.', 'ÇELİŞKİ', 'U07')
O('Q09.c4', 'Vâcib fâil olmasaydı mümkin âlemin müreccihi bulunmazdı; deist veya sudûrcu cevap alternatifleri ayrı ayrı çürütülmelidir (Q09.c2 ve Q09.c3).', 'ÇELİŞKİ-KOŞULLU', 'U08')
O('Q10.ilim.c1', 'Vâcib ilimsiz olsaydı muhkem fiil ve tahsis açıklanamazdı.', 'MALİYET', 'U17')
O('Q10.irade.c1', 'Vâcib iradesiz olsaydı çokluk ve belirli hâl (tahsis) açıklanamazdı veya âlem Vâcib kadar zorunlu olurdu.', 'ÇELİŞKİ-KOŞULLU', 'U08')
O('Q10.kudret.c1', 'Vâcib kudretsiz olsaydı var etme fiili olmazdı; âlem bulunamazdı.', 'ÇELİŞKİ', 'U07')
O('Q10.hayat.c1', 'Vâcib hayy olmasaydı ilim ve kudret sahibi olmazdı.', 'ÇELİŞKİ', 'U07')
O('Q10.kidem.c1', 'Vâcib kadîm olmasaydı hâdis olur ve bir muhdise muhtaç olurdu.', 'ÇELİŞKİ', 'U07')
O('Q10.beka.c1', 'Vâcib’in yokluğu mümkin olsaydı vâcib olmazdı.', 'ÇELİŞKİ', 'U07')
O('Q10.gina.c1', 'Vâcib bir şeye muhtaç olsaydı mümkin olurdu.', 'ÇELİŞKİ', 'U07')
O('Q10.semi.c1', 'Vâcib işitmeseydi sağırlık noksanı Vâcib’de bulunurdu; noksanlı olan kemâli sınırlı demektir ve sınırı bir müreccihle belirlenirdi.', 'ÇELİŞKİ-KOŞULLU', 'U07')
O('Q10.basar.c1', 'Vâcib görmeseydi körlük noksanı Vâcib’de bulunurdu; noksanlı olan kemâli sınırlı demektir ve sınırı bir müreccihle belirlenirdi.', 'ÇELİŞKİ-KOŞULLU', 'U07')
O('Q10.kelam.c1', 'Vâcib konuşamasaydı dilsizlik noksanı Vâcib’de bulunurdu; ayrıca bildirme (H3) aklen imkânsız olurdu.', 'ÇELİŞKİ-KOŞULLU', 'U07')
O('Q10.tekvin.c1', 'Vâcib’in var etme kemâli olmasaydı âlem var edilemezdi; oysa âlem vardır ve mümkindir.', 'ÇELİŞKİ', 'U07')
O('Q19.c1', 'Vâcib’in kudreti bir mümkine yetişmeseydi o mümkinin varlığı başka bir fâile kalırdı; oysa âlem tek Vâcib’in ihtiyarlı fiilidir (Q04.c1, Q09.c4); çelişki doğardı.', 'ÇELİŞKİ-KOŞULLU', 'U07')
O('Q11.c3', 'Vâcib cüz’îleri bilmeseydi cüz’î fiil ve tahsis O’na isnat edilemezdi.', 'ÇELİŞKİ-KOŞULLU', 'U24')
O('Q12.c1', 'Vâcib’in vücûbunun başka bir sebebi olsaydı Vâcib mümkin olurdu.', 'ÇELİŞKİ', 'U07')
O('Q13.c1', 'Âlem hâdis değilse ya zorunludur (değişenin zorunluluğu çelişir) ya ezelî mümkindir (Vâcib’in varlığını etkilemez; fakat sudûrcu felsefe doğar).', 'KISMEN', 'U08')
O('Q14.c1', 'Vâcib’in kemâli sınırlı olsaydı sınırı bir müreccihle belirlenir ve Vâcib muhtaç olurdu.', 'ÇELİŞKİ-KOŞULLU', 'U07')
O('Q15.c1', 'İbadete lâyık başkaları olsaydı Vâcib’in nihaî ihsanı paylaştırılmış olurdu; varlığı veren yalnız Vâcib’dir.', 'MALİYET', 'U17')
O('Q16.c3', 'Nizamın sebebi kasıt değilse tesadüf veya zorunluluktur; ikisi de ayrı ayrı çürütülmeli, tesadüf yalnız zan-ı gâlip düzeyinde çürür.', 'ÇELİŞKİ-KOŞULLU', 'U08')
O('Q17.c1', 'Vâcib’in varlığı yakînen bilinemeseydi hiçbir burhân bu alana ulaşamazdı; bu hâlde bilinemezcilik ilzamla karşılaşırdı.', 'KISMEN', 'U26')
O('Q18.c1', 'Aklın evveliyyâtı geçerli olmasaydı hiçbir ret veya delil ifade edilemezdi.', 'ÇELİŞKİ', 'U26')
O('Q00.c1', 'Sebep ilkesi geçerli olmasaydı hiçbir hâdisin neden her yerde ve her zaman ortaya çıkmadığı açıklanamazdı.', 'MALİYET', 'U07')


SIFAT_TASNIFI = [
    dict(sinif='zâtî', sira=1, ad='Vücûd', sorular=['Q02'], mezhep='Senûsî sayımında “nefsiyye” sıfatı diye ayrı tutulur; kelâmcıların çoğu varlığı sıfat saymaz (hafızadan, yoklanmadı).'),
    dict(sinif='zâtî', sira=2, ad='Kıdem', sorular=['Q10.kidem'], mezhep='Senûsî sayımında “selbiyye”.'),
    dict(sinif='zâtî', sira=3, ad='Bekâ', sorular=['Q10.beka'], mezhep='Senûsî sayımında “selbiyye”.'),
    dict(sinif='zâtî', sira=4, ad='Vahdâniyyet', sorular=['Q04', 'Q05'], mezhep='Senûsî sayımında “selbiyye”; tevhidin üç kanadı (zâtta, sıfatta, fiilde) bazı kelâm kitaplarında ayrı anılır.'),
    dict(sinif='zâtî', sira=5, ad='Kıyâm bi-nefsihî (gınâ)', sorular=['Q10.gina', 'Q12'], mezhep='Senûsî sayımında “selbiyye”.'),
    dict(sinif='zâtî', sira=6, ad='Muhâlefetün li’l-havâdis', sorular=['Q06', 'Q07', 'Q08'], mezhep='Senûsî sayımında “selbiyye”; kitabın tenzih hücreleri (âlemden ayrılık, cisim ve mekân değil, hulûl ve ittihâd yok) bunun açılımıdır.'),
    dict(sinif='subûtî', sira=1, ad='Hayat', sorular=['Q10.hayat'], mezhep='Mâtürîdî ve Eş’arî ortak.'),
    dict(sinif='subûtî', sira=2, ad='İlim', sorular=['Q10.ilim'], mezhep='Mâtürîdî ve Eş’arî ortak; Mu’tezile zâtın aynı sayar.'),
    dict(sinif='subûtî', sira=3, ad='Semi’', sorular=['Q10.semi'], mezhep='Ortak çekirdek (işitme kemâlinden mahrum değildir) c1’de; ayrı sıfat mı ilme dönüş mü c4’te ihtilaflıdır, Mu’tezile ilme döndürür (hafızadan, yoklanmadı; V.2.1.10).'),
    dict(sinif='subûtî', sira=4, ad='Basar', sorular=['Q10.basar'], mezhep='Ortak çekirdek (görme kemâlinden mahrum değildir) c1’de; ayrı sıfat mı ilme dönüş mü c4’te ihtilaflıdır (hafızadan, yoklanmadı; V.2.1.10).'),
    dict(sinif='subûtî', sira=5, ad='Kudret', sorular=['Q10.kudret'], mezhep='Ortak.'),
    dict(sinif='subûtî', sira=6, ad='İrade', sorular=['Q10.irade'], mezhep='Ortak.'),
    dict(sinif='subûtî', sira=7, ad='Kelâm', sorular=['Q10.kelam'], mezhep='Ortak çekirdek (konuşma kemâlinden mahrum değildir) c1’de; kelâmın zâtî ve mahlûk olmadığı (kelâm-ı nefsî) c4’te ihtilaflıdır (V.2.13, V.3.1.6).'),
    dict(sinif='subûtî', sira=8, ad='Tekvîn', sorular=['Q10.tekvin'], mezhep='Ortak çekirdek (var etme kemâli) c1’de; Mâtürîdî ayrı sıfat sayar (sekiz), Eş’arî kudret ve iradeye döndürür (yedi), bu ayrım c4’te ihtilaflıdır; toplam bu yüzden 8 veya 7 çıkar.'),
    dict(sinif='fiilî', sira=1, ad='Hikmet', sorular=['Q10.hikmet'], mezhep='Sübûtî sayıya girmez; fiil sıfatıdır. Mâtürîdî’de tekvîne, Eş’arî’de kudret ve iradeye döner (hafızadan). Kitap bu dört hücreyi V.2.4 ve V.5 köprüsü için açtı.'),
    dict(sinif='fiilî', sira=2, ad='Adâlet', sorular=['Q10.adalet'], mezhep='Aynı; insanî mânâyla müşterek lafız ayrımı gerekir (V.2.4.2).'),
    dict(sinif='fiilî', sira=3, ad='Rahmet', sorular=['Q10.rahmet'], mezhep='Aynı.'),
    dict(sinif='fiilî', sira=4, ad='Sıdk', sorular=['Q10.sidk'], mezhep='Aynı; H5’in köprüsü (V.5.1).'),
]
