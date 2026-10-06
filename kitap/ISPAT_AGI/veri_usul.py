USULLER = []


def U(id, ad, grup, tur, atif, tanim, nasil, sart, hudut, safsata, tavan, mevki, ornek):
    USULLER.append(dict(id=id, ad=ad, grup=grup, tur=tur, atif=atif, tanim=tanim, nasil=nasil, sart=sart, hudut=hudut,
                        safsata=safsata, tavan=tavan, mevki=mevki, ornek=ornek))


U('U01', 'Burhân-ı innî (eserden müessire)', 'akıl', 'burhan', 'I.4.2.A.1; I.4.11',
  'Eserden müessire geçiştir: eserin varlığı müessirin varlığını gösterir. Fârâbî ölçüsüyle yalnız varlık veren (enne) burhânlardandır.',
  ['Eser müşâhede edilir.', 'Eserin yalnız o müessire özgü ve ona döndürülebilir olduğu gösterilir (I.4.11.5).', 'Müessirin varlığı netice olur.'],
  'Eser ile müessir arasındaki illiyetin evveliyyât veya yakînî öncüllerle gösterilmesi.',
  'Yalnız varlığı verir; müessirin sebebini ve mahiyetini vermez (I.4.6.12). Müessirin hangi sıfatlarla var olduğu ayrıca ispat ister.',
  'Eser tek müessire özgü ve ona döndürülebilir olduğu gösterilmeden delil kurulursa hatadır (yıldızın ateşten olduğunu parıldamasından çıkarmak, I.6.6.3).',
  'yakîn (öncüller yakînî ise)', 'teçhizat',
  'Duman görülür; duman varsa ateş vardır, ateş varsa duman şart değildir (I.4.10.16): netice ateşin varlığıdır, ateşin nasıl yandığı değildir.')

U('U02', 'Burhân-ı limmî (müessirden/zâttan esere)', 'akıl', 'burhan', 'I.4.2.A.2; I.4.6.4; I.4.12',
  'Sebepten sonuca geçiştir: orta terim sebeptir; sebebin bilinmesi sonucun bilinmesini verir.',
  ['Sonucun varlığı önceden bilinir (I.4.12.6).', 'Orta terim olarak yakın ve zâtî sebep seçilir.', 'Sonucun niçin var olduğu netice olur.'],
  'Sonucun varlığının bilinmesi ve sebebin yakın ve zâtî olması.',
  'Sebebi olmayan şeye uygulanamaz: Vâcib’in sebebi olmadığından varlığı için limmî kurulamaz (I.4.6.16, Claude çıkarımı); zâttan sıfata (zâtî araz) uygulanabilir.',
  'Uzak sebeple yetinip orta terimi burhân saymak (I.6.6.2).',
  'yakîn', 'teçhizat',
  'Ay tutulması: Dünya’nın Ay ile Güneş arasına girmesi, tutulmanın niçin olduğunu verir (I.4.12.13).')

U('U03', 'İmkân–vücûb delili', 'akıl', 'burhan', 'I.4.2.A.3; V.1.3.b',
  'Mümkin kendi başına varlığı gerektirmez; varlığını yokluğuna tercih edilmiş olarak bir müreccihe borçludur; mümkinler bütününün müreccihi bütünün dışındadır.',
  ['Mümkinlerin var olduğu gösterilir.', 'Mümkinin varlığının yokluğuna tercih edildiği, tercihin bir müreccih istediği gösterilir.', 'Müreccihin mümkin olamayacağı (teselsül ve devir ile) gösterilir.', 'Netice: bütünün dışında bir Vâcib vardır.'],
  'Yeter sebep (tercihsiz tercih imkânsızdır) ve terkip itirazına cevap (bütün de mümkindir).',
  'Neticesi yalnız Vâcib’in varlığıdır; birliği, sıfatları ve bildirmesi ayrıca ispat ister (V.1.5). Hudûstan bağımsızdır.',
  'Terkip safsatası (parçanın her biri mümkinse bütün de mümkin sayılır) cevaplanmadıkça delil eksiktir.',
  'yakîn (iki tartışmalı öncülün kabulüne bağlı)', 'teçhizat',
  'Bir kitaplıktaki her kitap başka bir yerde de durabilirdi; hâlâ burada durması bir sebeple açıklanır; bütün kitaplık için de sebep sorusu geçerlidir.')

U('U04', 'Hudûs delili', 'akıl', 'burhan', 'I.4.2.A.4; V.1.3.a',
  'Hâdis olan bir muhdise muhtaçtır; âlem hâdistir; öyleyse âlemin bir muhdisi vardır ve o hâdis olamaz.',
  ['Âlemde değişim müşâhede edilir.', 'Değişenin ilk hâlinin öncesiz olmadığı, geçmişte sonsuz hâdis dizisinin bulunamayacağı gösterilir.', 'Âlemin hâdis olduğu netice verilir.', 'Hâdisin muhdisi vardır; muhdis âlemden ve hâdis olamaz (devir ve teselsül); öyleyse kadîmdir.'],
  'Geçmişte sonsuz hâdis dizisinin imkânsızlığı (tatbik, tazâyüf) ve hâdisin muhdisi kaidesi.',
  'Âlemin başlangıcına bağlıdır; âlem ezelî kabul edilirse bu delil işlemez, imkân–vücûb işler. Neticesi yalnız bir Vâcib’in varlığıdır.',
  'Sonsuzluk tartışmasında ardışık sonsuzu (hâdis dizisi) eşzamanlı sonsuzla (sebepler zinciri) karıştırmak.',
  'yakîn (bir tartışmalı halkaya bağlı)', 'teçhizat',
  'Mum yanıyor; yanma bir hâlden başka hâle geçiştir; sonsuz geriye yanmış mum dizisi bulunsa ilk hâl hiç gelmezdi.')

U('U05', 'Teselsülün butlânı', 'akıl', 'negatif', 'I.4.2.A.5',
  'Sonsuz bir sebep zincirinde hiçbir halka varlığını kazanamaz; zincirin tamamı da muhtaçtır.',
  ['Her halkanın varlığını bir önceki halkaya borçlu olduğu kabul edilir.', 'Hiçbir halka kendi başına varlık kazandırmıyorsa bütün zincirin de kazandıramayacağı gösterilir.', 'Zincirin bir kazandırıcıda bitmesi gerektiği netice olur.'],
  'Sebeplerin eşzamanlı ve zâtî (asli) sıralanması; zincirin bütününe de muhtaçlığın uygulanması.',
  'Eşzamanlı zâtî zincir için işler; ardışık hâdis dizisi için ayrı delil (tatbik) ister.',
  'Ardışık ve eşzamanlı sonsuzu karıştırmak.',
  'yakîn', 'teçhizat',
  'Her tuğla yalnız altındaki tuğlaya yaslanıyor ve hiçbir tuğla zemine değmiyorsa duvar durmaz.')

U('U06', 'Devrin butlânı', 'akıl', 'negatif', 'I.4.2.A.6',
  'Bir şey kendi sebebinin sebebi olamaz: devirde her halka hem önce hem sonra olurdu (çelişmezlik).',
  ['Zincirin kendi başına döndüğü varsayılır.', 'Her halkanın kendinden önce olması gerektiği gösterilir.', 'Aynı şeyin aynı bakımdan hem önce hem sonra olması çelişmezlik evveliyyâtı ile reddedilir.'],
  'Çelişmezlik evveliyyâtı.', 'Dairesel sebeplenmeyi reddeder; sonsuz doğrusal zinciri reddetmez (o U05’tir).',
  'Karşılıklı bağımlılığı (aynı anda) ardışık sebeplenmeyle karıştırmak.', 'yakîn', 'teçhizat',
  'A’yı B, B’yi A kuruyorsa ikisi de kurulmadan önce kurulmuş olması gerekir.')

U('U07', 'Hulf (olmayana ergi)', 'akıl', 'negatif', 'I.4.2.A.7',
  'Karşı iddianın imkânsız bir sonuca götürdüğünü göstererek iddiayı ispat eder.',
  ['Karşı iddia kabul edilir.', 'Kabul edilen iddiadan çelişkili veya imkânsız bir netice türetilir.', 'Karşı iddia reddedilir; nefy–isbât gereği iddia kalır.'],
  'Türetmede kullanılan bütün öncüllerin yakînî olması; üçüncü şıkkın imkânsızlığı.',
  'Neticesi yalnız iddianın doğruluğudur; sebebini vermez (enne). Türetmede zannî öncül varsa netice o derece zannîdir.',
  'Karşı iddianın aslında üçüncü bir şıkla bağdaşmasını gözden kaçırmak (yanlış ikilem).',
  'öncüllerinin derecesi kadar', 'teçhizat',
  'Kare dairedir denirse dört köşeli şeyin köşesiz olması gerekir; çelişme olduğundan iddia düşer.')

U('U08', 'Sibr ve taksim (aklî hasırla)', 'akıl', 'negatif', 'I.4.2.A.8; I.1; V.6.2.50',
  'İhtimaller aklî hasırla (nefy–isbât) sayılır, her biri sırayla elenir, kalan ispatlanır.',
  ['Suâl konur ve cevap uzayı nefy–isbât zinciriyle kurulur (I.1.3.4).', 'Her yanlış hücre kendi usuluyle reddedilir.', 'Kalan hücre netice olur; kapalılık yapıdan gelir.'],
  'Cevap uzayının aklî hasır olması (istikrâî sayım ise netice zannîdir) ve her eleme adımının ispatlı olması.',
  'Netice, elemelerin en zayıf halkasından güçlü olamaz (zincir kaidesi I.3.5.5); eksik hücre bulunursa taksim bozulur.',
  'Hasır sahteciliği: sayıma dayanan taksimi aklî hasır diye sunmak (I.1.3.10).', 'öncüllerin en zayıfı', 'teçhizat',
  'Bir bilye ya sağ ya sol ya orta kutudadır; sağ ve sol boşsa orta kutudadır.')

U('U09', 'Temsil (kıyâs-ı fıkhî; gâib–şâhid)', 'akıl', 'zannî-akıl', 'I.4.2.A.9',
  'Bir hükmü illet ortaklığıyla bir şeyden öbürüne geçirir; delil değeri zannîdir.',
  ['Bilinen örnekte hüküm ve illet tespit edilir.', 'İlletin başka örnekte de bulunduğu gösterilir.', 'Hüküm geçirilir.'],
  'İllet ortaklığının ve farkın yokluğunun gösterilmesi.', 'Zannî kalır; benzeri olmayan şeye uygulanamaz.',
  'İlletsiz benzerliği illet saymak.', 'zan', 'teçhizat',
  'Bu ilâç bir hastada tuttu, aynı illetteki hastada da tutar.')

U('U10', 'Mütevâtir haber', 'haber', 'haber', 'I.4.2.B.2; I.4.5',
  'Yalan üzerinde birleşmeleri âdeten imkânsız çokluğun, her tabakada, his temelli ve birbirinden bağımsız haberidir; yakîn ifade eder.',
  ['Haberin dört şartı denetlenir (kesret, tabaka, his, bağımsızlık).', 'Kasd-ı kizb imkânsızlığı gösterilir.', 'Haber yakîn derecesine yükseltilir.'],
  'Tevâtürün dört şartı ve kaynağın tahrifsizliği.', 'Yalnız hissî ve vâkıa haberlerinde işler; aklî hükmü (Vâcib’in varlığı) haberle ispat etmez.',
  'Çok haberi bağımsız saymak (I.3.6.7).', 'yakîn (şartlar tutarsa)', 'teçhizat',
  'Şehrin varlığını hiç görmemiş biri, bağımsız çok kişiden duyunca yakînen bilir.')

U('U11', 'Haber-i vâhid', 'haber', 'haber', 'I.4.2.B.3',
  'Tek veya az sayıda kaynaktan gelen haber zan ifade eder; karîne ve çokluk yığılırsa zan-ı gâlibe yükselebilir.',
  ['Kaynağın sıdkı ve zabtı yoklanır.', 'Karîneler eklenir.', 'Derece zan veya zan-ı gâlib olarak işaretlenir.'],
  'Kaynağın güvenilirliği.', 'Katiyet kaynağından güçlü olamaz.', 'Otoriteye başvuru (I.6.3.11).', 'zan-ı gâlib', 'teçhizat',
  'Bir güvenilir yolcunun yol durumu haberi.')

U('U12', 'Müşâhede', 'duyu', 'duyu', 'I.4.2.C.1; I.3.3.2',
  'Duyunun (hissiyyât) veya iç duyunun (vicdâniyyât) şahitliğiyle hükme varmaktır; sağlıklı duyu ve uygun şart altında yakînîdir.',
  ['Duyu ve şart sağlıklı olduğu gösterilir.', 'Gözlenen vâkıa öncül olarak yazılır.'],
  'Sağlıklı duyu ve uygun şart.', 'Yalnız öncül sağlar; müşâhede edilemeyen (gayb, Vâcib) bir şeyi doğrudan ispat edemez (I.4.3.5).',
  'Duyuyu illüzyon şartında kullanmak.', 'yakîn', 'teçhizat', 'Âlemde değişim vardır: mum erir.')

U('U13', 'Tecrübe', 'duyu', 'duyu', 'I.4.2.C.2; I.3.3.3',
  'Şartları kontrol edilmiş tekrarlı gözlemle hükme varmaktır.',
  ['Şartlar kontrol edilir.', 'Gözlem tekrarlanır.', 'Tümel hüküm yazılır.'],
  'Tecrübe şartlarının kontrolü.', 'Metafizik bir varlığa uygulanamaz; öncül (kanun düzeni) sağlar.',
  'Tecrübe ile tümevarımı karıştırmak (I.3.13.19).', 'yakîn (şartlar kontrollüyse)', 'teçhizat', 'Su yüz derecede kaynar.')

U('U14', 'İstikrâ (tümevarım)', 'duyu', 'duyu', 'I.4.2.C.3',
  'Cüz’îlerin taranmasıyla küllîye varmaktır; tam istikrâ yakîn, nâkıs istikrâ zan verir.',
  ['Cüz’îler taranır.', 'Tarama tam ise küllî yakîn; değilse zan.'],
  'Taramanın kapsamının gösterilmesi.', 'Tam tarama yapılamıyorsa zan; âlemin tamamı hakkında hüküm vermez.',
  'Aceleci genelleme (I.6.3.13).', 'zan (nâkıs istikrâ)', 'teçhizat', 'Bütün kuğular beyaz sanılırken siyah kuğu bulundu.')

U('U15', 'Hads', 'duyu', 'duyu', 'I.4.2.C.4; I.3.3.4',
  'Orta terimin zihne birdenbire doğmasıyla varılan hükümdür; sonradan doğrulama ister.',
  ['Orta terim zihne doğar.', 'Sonradan doğrulanır; doğrulanmazsa zan kalır.'],
  'Sonradan doğrulanabilirlik.', 'Doğrulanmayan hads zannîdir.', 'Sezgiyi delil saymak.', 'zan', 'teçhizat', 'Ayın ışığının güneşten olduğu sezgisi.')

U('U16', 'Kümülatif delil', 'birleşik', 'birleşik', 'I.4.2.D.1; I.3.6',
  'Farklı yollardan gelen bağımsız delillerin bir sonuçta birleşmesi; bağımsızlık gösterilmeden katiyet artırmaz.',
  ['Her delil ayrı ayrı yazılır.', 'Zayıf halkaların ve ortak öncüllerin ailesi çıkarılır.', 'Ortak aile yoksa dayanıklılık artar; varsa artmaz.'],
  'Delillerin kaynakça ve öncül bakımından bağımsızlığı.', 'Bağımlı delillerin yığılması katiyeti artırmaz (I.3.6.3); bağımsız zannî deliller yakîne ancak tevâtür gibi şartlarla çıkar.',
  '"Çok delil var" cümlesi (I.3.6.7).', 'zan-ı gâlib; bağımsızsa dayanıklılık', 'teçhizat',
  'İki bağımsız şahit aynı olayı aktarıyorsa tek şahitten sağlamdır; ikisi aynı kişiden duymuşsa değildir.')

U('U17', 'En iyi açıklamaya çıkarım', 'birleşik', 'zannî-akıl', 'I.4.2.D.2',
  'Veriyi en iyi açıklayan hipotez seçilir; delil değeri zannî veya zan-ı gâliptir.',
  ['Veri belirlenir.', 'Rakip açıklamalar aklî hasırla sayılır.', 'Açıklama gücü ve sadeliği tartılır.'],
  'Rakip açıklamaların hasırla tüketilmesi.', 'Zan-ı gâlibi aşmaz.', 'Rakibi bulunmamasını tamlık saymak.', 'zan-ı gâlib', 'teçhizat',
  'Sabah yer ıslaksa yağmur geçmiştir; hortum ihtimali de değerlendirilir.')

U('U18', 'Nass ve delâlet', 'birleşik', 'haber', 'I.4.2.D.3',
  'Bir metnin lafzının mânâya delâleti; delâletin katiyeti metin ve ifade kurallarına bağlıdır.',
  ['Metnin sübûtu gösterilir.', 'Lafzın delâleti yoklanır.'],
  'Metnin sübûtunun kat’î ve delâletin kat’î olması.', 'Muhatabın kabul etmediği metin delil olamaz; H4 sonrasında bilgidir (V.0.5).',
  'Kur’ân’ı muhatabın kabul etmediği öncül olarak kullanmak (musâdere).', 'sübût ve delâlet derecesi kadar', 'teçhizat', 'Bir kanun maddesinin lafzından hüküm çıkarmak.')

U('U19', 'Enne burhânı (yalnız varlık veren)', 'Fârâbî', 'burhan', 'I.4.6.12; I.4.11',
  'Zorunlu kesinlikle kesinlenen öncüllerden kurulup şeyin yalnız varlığını veren kıyas.',
  ['Öncüller zorunlu kesin olur.', 'Orta terim sonradan gelen (delil) veya sebep olabilir.', 'Netice yalnız varlıktır.'],
  'Zorunlu kesin öncüller.', 'Sebebi vermez; sebep sorusu açık kalır (I.4.12.19).', 'Uzak sebeple yetinmek (I.6.6.2).', 'yakîn', 'teçhizat',
  'Ay’ın ışığı artar; öyleyse Ay yuvarlaktır (I.4.11.4).')

U('U20', 'Lime burhânı (yalnız sebep veren)', 'Fârâbî', 'burhan', 'I.4.6.4; I.4.12',
  'Varlığı önceden bilinen şeyin niçin var olduğunu veren kıyas.',
  ['Şeyin varlığı önceden bilinir.', 'Yakın ve zâtî sebep orta terim olur.', 'Niçin sorusu cevaplanır.'],
  'Varlığın önceden bilinmesi ve sebebin bulunması.', 'Sebebi olmayanda kurulamaz (I.4.6.16).', 'Uzak sebeple yetinmek.', 'yakîn', 'teçhizat',
  'İnsan niçin ölür: dört sebepten biri orta terim yapılır (I.4.12.7).')

U('U21', 'Mutlak burhân (varlık ve sebep birlikte)', 'Fârâbî', 'burhan', 'I.4.6.13; I.4.6.14',
  'Hem varlığı hem varlık sebebini bizâtihi veren kesin kıyas.',
  ['Enne ve lime aynı kıyasta toplanır.', 'Öncüller zâtî ve ilk olur.'],
  'Zâtî ve ilk öncüller.', 'Sebebi olmayan şey için kurulamaz.', 'Bilaraz sebebi mutlak saymak (I.4.7.3).', 'yakîn', 'teçhizat',
  'Üçgenin açılarının iki dik açıya eşitliği hem var olduğunu hem niçin olduğunu birlikte verir.')

U('U22', 'Orta terim: maddî sebep', 'Fârâbî', 'burhan', 'I.4.7.1',
  'Şeyin maddesini orta terim yaparak kurulan kıyas.',
  ['Maddeden sonuca geçilir.'], 'Maddenin zâtî olması.', 'Maddesi olmayan şeyde kurulamaz.', 'Bilaraz maddeyi sebep saymak.', 'yakîn', 'teçhizat',
  'İnsan zıtlardan mürekkep olduğu için ölür.')

U('U23', 'Orta terim: sûrî sebep', 'Fârâbî', 'burhan', 'I.4.7.1',
  'Şeyin tanımını (sûretini) orta terim yaparak kurulan kıyas.',
  ['Tanımdan sonuca geçilir.'], 'Tanımın tam olması.', 'Tanımı olmayan şeyde kurulamaz (I.2.2.6).', 'Eksik tanımla netice çıkarmak.', 'yakîn', 'teçhizat',
  'İnsan düşünen ölümlü canlı olduğu için ölür.')

U('U24', 'Orta terim: fâil sebep', 'Fârâbî', 'burhan', 'I.4.7.1',
  'Fâili orta terim yaparak kurulan kıyas.',
  ['Fiilden fâile veya fâilden fiile geçilir.'], 'Fâilin sonucu zorunlu kılmadığının kaydı (I.4.12.8).', 'Fâil sebep sonucu zorunlu kılmaz.',
  'Fâili zorunlu sebep saymak.', 'yakîn (zâtî ise)', 'teçhizat', 'Bu ev ustalar tarafından yapıldı.')

U('U25', 'Orta terim: gâî sebep', 'Fârâbî', 'burhan', 'I.4.7.1',
  'Gâyeyi orta terim yaparak kurulan kıyas.',
  ['Gâyeden sonuca geçilir.'], 'Gâyenin zâtî olması.', 'Gâî sebep sonucu zorunlu kılar (I.4.12.8) ama gâyenin varlığı ayrıca gösterilmelidir.',
  'Tesadüfî sonucu gâye saymak.', 'yakîn (zâtî ise); zan-ı gâlib (nizam çıkarımında)', 'teçhizat', 'Dişler yemek için vardır.')

U('U26', 'İlzam (reddin kendini çürütmesi)', 'müdafaa', 'negatif', 'I.7.3.7; V.0.4',
  'Reddin ancak reddedilen şey kabul edilerek ifade edilebildiğini göstermek.',
  ['Ret cümlesi alınır.', 'Cümlenin kendi doğruluğu için neyi varsaydığı çıkarılır.', 'Varsayımın reddedilen şey olduğu gösterilir.'],
  'Retin bir iddia olarak ileri sürülmesi.', 'İknâ değil ilzamdır; ilzam edilen inatla devam ederse tartışma ilzamla biter (I.7.3.9).', 'İlzamı çürütme saymak.',
  'yakîn', 'teçhizat', '"Hiçbir şey bilinemez" diyen bunu bildiğini iddia ediyorsa kendi cümlesini çürütür.')

U('U27', 'Nakz', 'müdafaa', 'negatif', 'I.5.3.2',
  'Muhatabın iddiasının kendi öncülleriyle çeliştiğini göstermek.',
  ['Muhatabın öncülleri toplanır.', 'İddia ile çelişkisi gösterilir.'],
  'Müsellemâtın muhatabın kendi kabulü olması.', 'Müsellemât burhan öncülü değildir (I.3.4.8); netice muhatap için ilzamdır.', 'Muhatabın iddiasını çarpıtmak (I.6.3.12).', 'muhatabın kabulü kadar', 'teçhizat',
  'Herkesin doğrusu kendisinedir diyen, bunu herkes için doğru sayıyorsa kendi öncülüyle çelişir.')

U('U28', 'Tanım tahlili (kavram tutarlılığı)', 'tanım', 'burhan', 'I.2',
  'Bir kavramın parçaları arasında veya kesin öncüllerle çelişki bulunup bulunmadığının tanım üzerinden yoklanması.',
  ['Tanım tam yazılır (I.2.3).', 'Parçalar arası çelişki aranır.', 'Çelişki yoksa kavramın imkânı, varsa imtinâı netice olur.'],
  'Tanımın câmi’ ve mâni’ olması ve muhatapla ortaklaştırılması.', 'Kavramın tutarlı olması varlığını göstermez (imkân vukû’u vermez, I.4.1.4).',
  'Tanımda devir ve müşterek lafız (I.2.3).', 'yakîn (tanım ortaksa)', 'teçhizat', 'Köşesiz kare tanımı kendi içinde çelişir.')

U('U29', 'Hall', 'müdafaa', 'negatif', 'I.5.3.4',
  'İtirazın hangi yanlış öncül veya geçersiz sûretten doğduğunu çözmek.',
  ['İtiraz kıyas şekline dökülür.', 'Yanlış öncül veya geçersiz sûret bulunur.', 'İtiraz bu noktada düşer.'],
  'İtirazın öncüllerinin açıkça yazılması.', 'İtirazın doğru kısmı kabul edilip hudut çekilir (U30).', 'Çarpıtma.', 'yakîn (öncül yanlışsa)', 'teçhizat',
  'Parçalar mümkinse bütün de mümkindir itirazı terkip safsatasından doğar.')

U('U30', 'Kabul ve tahdit', 'müdafaa', 'negatif', 'I.5.3.5',
  'İtirazın doğru olduğu yeri kabul edip delilin hududunu o yere çekmek.',
  ['İtirazın doğru kısmı belirlenir.', 'Neticenin hududu daraltılır.'], 'Hudutun açıkça yazılması.', 'Hududun ötesi iddia değildir.', 'Hududu gizlemek.', 'hududa kadar', 'teçhizat',
  'Bu delil bir yaratıcıyı gösterir, İslâm’ı değil: kabul edilir ve hudut yazılır (V.1.5.4).')

U('U31', 'Mefhum tahlili (sıddîkîn; en az öncüllü)', 'akıl', 'burhan', 'V.6.2.167',
  'Kâinattaki bir esere değil, varlık mefhumunun mümkin–vâcib bölünmesine ve düşünenin kendi varlığına dayanan ispat (Claude’un hafızasından; kaynak yoklanmadı).',
  ['"Bir şey vardır" öncülü alınır.', 'Varlık mümkin ve vâcibe taksim edilir.', 'Mümkinin müreccihe muhtaçlığı ve zincirin kapanışı gösterilir.'],
  'Bir şeyin varlığı (düşünenin kendisi) ve yeter sebep.', 'Öncülsüz değil, en az öncüllüdür; yeter sebep ailesine bağlıdır.', 'Mefhumdan hâriçte varlık çıkarmak (ontolojik delil hatası; V.1.4.11).', 'yakîn (koşullu)', 'taslak-namzet',
  'Kendi varlığından şüphe eden, şüphe ettiği için var olduğunu bilir.')

U('U32', 'Tenbih (fıtrat ve vicdan)', 'tenbih', 'tenbih', 'V.1.3.d',
  'Delil değil, muhataba yol gösteren işaret: insanda mutlak varlığa yönelme eğilimi.',
  ['Eğilim gösterilir.', 'Delil sayılmadığı ilan edilir.'], 'Muhataba yol göstermek.', 'Burhan sayılmaz (V.1.3.d.3).', 'Genetik safsata ile çakışma (I.6.3.8).', 'tenbih', 'taslak-namzet',
  'İnsan karanlıkta ışığa yönelir; bu ışığın varlığını ispat etmez, aramaya sevk eder.')

U('U33', 'Transandantal delil (aklın mümkün kılma şartı)', 'aday', 'aday', 'V.6.2.168',
  'Başka yapay zekânın önerisi: bilgi ve akıl mümkün olsun diye hangi şartın gerektiği.', ['(kabul edilmedi)'], '-', '-', '-', '-', 'aday (kabul edilmedi)', '-')

U('U34', 'Koherentist ağ', 'aday', 'aday', 'V.6.2.168',
  'Başka yapay zekânın önerisi: inançlar ağının iç tutarlılığı.', ['(kabul edilmedi)'], '-', '-', '-', '-', 'aday (kabul edilmedi)', '-')

U('U35', 'Bayesyen ittifak', 'aday', 'aday', 'V.6.2.168; V.6.2.169',
  'Başka yapay zekânın önerisi: bağımsız delillerin olasılık birleşimi; verilen örnek hesap yanlıştı (V.6.2.169).', ['(kabul edilmedi)'], '-', '-', '-', '-', 'aday (kabul edilmedi)', '-')
