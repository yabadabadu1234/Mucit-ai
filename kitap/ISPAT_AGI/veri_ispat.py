ISPATLAR = []


def P(h, u, pr, oz, tag=None, hd='', sarti=None, kismi=''):
    ISPATLAR.append(dict(hucre=h, usul=u, prem=list(pr), ozet=oz, tag=tag, hudut=hd, sarti=sarti, kismi=kismi))


P('Q18.c1', 'U26', ['k_bilinemez_bilgi', 'k_hakikat_hakikat', 'e_celismezlik'],
  'Aklın evveliyyâtını ve doğru bilgiyi reddeden her cümle, kendi doğruluğunu iddia ederek reddettiği şeyi kabul etmiş olur.')
P('Q18.c1', 'U07', ['e_celismezlik', 'e_ucuncu_sik', 'k_hakikat_hakikat'],
  'Evveliyyât geçersiz olsaydı çelişmezlik de geçersiz olurdu; o zaman ret cümlesi de bir şeyi diğerinden ayıramazdı.')
P('Q18.c1', 'U12', ['m_ben', 'e_celismezlik'],
  'Düşünenin kendi varlığı vicdânî müşâhededir; şüphe etmek bile bir bilginin bulunduğunu gösterir.')
P('Q18.c2', 'U26', ['k_hakikat_hakikat', 'e_celismezlik'], '“Hakikat yoktur” cümlesi bir hakikat iddiasıdır ve kendini yıkar.')
P('Q18.c2', 'U07', ['k_hakikat_hakikat', 'e_ucuncu_sik'], 'Hakikat yoksa bu cümle de doğru değildir; doğruysa hakikat vardır.')
P('Q18.c3', 'U26', ['k_hakikat_hakikat'], '“Hakikat kişiye göredir” cümlesi herkes için doğru olmayı ister.')
P('Q18.c3', 'U27', ['k_hakikat_hakikat', 'e_celismezlik'], 'Görecelikçi kendi cümlesini herkes için doğru sayar; bu kendi öncülüyle çelişir.')
P('Q18.c4', 'U26', ['k_bilinemez_bilgi'], '“Hiçbir şey bilinemez” cümlesi bunun bilindiğini iddia eder.')
P('Q18.c4', 'U07', ['k_bilinemez_bilgi', 'e_celismezlik'], 'Hiçbir şey bilinemiyorsa bu cümle de bilinemez; öyleyse hükmü kendini kapsamaz veya kendini yıkar.')

P('Q00.c1', 'U17', ['k_sebepsiz_bilgi', 'm_nizam', 'm_degisim'],
  'Her hâdisin sebebi olduğu kabulü bütün ilmî açıklamanın zeminidir; kabul edilmeseydi açıklama aramanın anlamı kalmazdı.')
P('Q00.c1', 'U13', ['m_nizam', 'k_sebepsiz_bilgi'], 'Kontrollü ve tekrarlı gözlemlerde hâdis hep sebebiyle birlikte görülür.')
P('Q00.c1', 'U14', ['m_degisim'], 'Taranan hâdislerin hiçbiri sebepsiz çıkmadı; tarama tam değildir.')
P('Q00.c2', 'U26', ['k_sebepsiz_bagimsiz'], 'Sebepsizliği savunan bir gerekçe getirir; gerekçe getirmek açıklama aramaktır.')
P('Q00.c2', 'U07', ['k_sebepsiz_bilgi', 'm_nizam'], 'Sebepsiz hâdis mümkün olsaydı hâdislerin neden her yerde ve her zaman ortaya çıkmadığı açıklanamazdı.')
P('Q00.c2', 'U07', ['m_frekans_sans', 'p_sebepsiz_sans_yok', 't_bayes_aralik', 'p_apriori_ret'],
  'Sebepsiz hâdis kabul edilirse sıklıktan şansa çıkarım delil getirmez (Bayesçi ıraksama); ilmî çıkarım temelsiz kalır; bu yüzden sebepsiz hâdis a priori reddedilir.')
P('Q00.c3', 'U26', ['k_bilinemez_bilgi'], 'İlkenin doğruluğunun bilinemeyeceğini söyleyen bunu bildiğini iddia eder.')
P('Q00.c3', 'U29', ['k_yalniz_duyu_kendini_yikar', 'e_celismezlik'],
  'Zorunlu bağ görülmez itirazı, bilginin yalnız duyudan geldiği öncülüne dayanır; bu öncül kendini yıkar.')
P('Q00.c3', 'U07', ['k_yalniz_duyu_kendini_yikar', 'H:Q18.c1'], 'Aklın evveliyyâtı geçerliyse ilkenin doğruluğu akılla bilinebilir.')

P('Q01.c1', 'U28', ['t_vacib', 'k_zat_vacip_tutarli', 'k_sebep_istemez'], 'Tanımın parçaları arasında çelişki yoktur.', tag=('enne', 'suret'))
P('Q01.c1', 'U07', ['H:Q02.c1', 'k_vuku_imkan'], 'Vâcib mevcutsa mümteni olamaz; vukû imkânı gösterir.')
P('Q01.c2', 'U28', ['t_vacib', 'k_sebep_istemez', 'k_kendi_kendine'], '“Zâtından var olmak” kendini var etmek değil, sebebe ihtiyaç duymamaktır.')
P('Q01.c2', 'U29', ['k_sebep_istemez', 'k_kendi_kendine'], 'İtirazın yanlış öncülü: zâtından olmakla kendi kendinin sebebi olmak aynı sayılıyor.')
P('Q01.c3', 'U29', ['k_zorunluluk_dicto', 't_vacib'], 'İtiraz zorunluluğun yalnız önermelere ait olduğunu kabul eder; bu bir tercihtir, teorem değildir.')
P('Q01.c3', 'U07', ['H:Q02.c1', 'k_vuku_imkan'], 'Zorunlu bir varlık mevcutsa zorunlu varlığın olamayacağı söylenemez.')

P('Q02.c1', 'U03', ['m_mumkin', 'm_tahsis', 't_mumkin', 't_vacib', 'k_tercihsiz', 'k_butunun_dis_muhtac', 'H:Q03.c3', 'H:Q03.c4', 'H:Q03.c5'],
  'Mümkinlerin varlığı yokluklarına tercih edilmiştir; tercih bir müreccih ister; müreccih mümkinler zincirinde bulunamadığından bütünün dışındaki Vâcib vardır.',
  tag=('enne', 'fail'))
P('Q02.c1', 'U01', ['m_tahsis', 'k_tercihsiz_hal', 'H:Q03.c2', 'H:Q03.c3', 'H:Q03.c4'],
  'Âlemdeki belirli hâl (tahsis) bir eserdir; müessiri mümkinler içinde bulunamaz.', tag=('enne', 'fail'))
P('Q02.c1', 'U04', ['m_degisim', 't_alem', 'k_hudus_cisim', 'k_cisim_parcali', 'k_sonsuz_hadis', 'k_hadis_muhdis', 'H:Q03.c4', 'H:Q03.c5'],
  'Âlem hâdistir; hâdisin muhdisi vardır; muhdis âlemden ve hâdis olamaz; öyleyse kadîmdir.', tag=('enne', 'fail'))
P('Q02.c1', 'U31', ['m_ben', 't_vacib', 't_mumkin', 'k_tercihsiz', 'k_muhtac_mumkin', 'H:Q03.c3', 'H:Q03.c4', 'H:Q03.c5'],
  'Düşünenin kendi varlığından başlanır; varlık mümkin ve vâcibe taksim edilir; mümkinin müreccihi zincirde kapanmaz.', tag=('enne', 'suret'))
P('Q02.c1', 'U14', ['m_tahsis', 'k_tercihsiz_hal'], 'Bilinen bütün eserlerin müessiri bulunmuştur; tarama tam olmadığından netice zannîdir.')
P('Q02.c1', 'U32', ['m_bilinc'], 'İnsandaki mutlak varlığa yönelme eğilimi delil sayılmaz; muhatabı aramaya sevk eder.')

P('Q02.c2', 'U27', ['k_iddia_gerekce', 'k_destek_hasir', 's_kaza_kurali', 's_parca_butun', 'p_sadelik_orantisiz', 'H:Q01.c1'],
  'Cezmî nefyin gerekçesi ya bulamamaktır (hasmın yerelde reddettiği kural), ya iç açıklamaların başarı sicilinden bütüne geçiştir (hasmın terkip itirazının tersine yürüyen aynı geçiş), ya sadeliktir (yerelde her olayı çıplak sayardı), ya imkânsızlık delilidir (Q01’de çürüdü); hiçbiri kalmadığından cezmî nefy savunulamaz ve geriye yalnız tevakkuf kalır.')
P('Q02.c2', 'U08', ['k_destek_ikilik', 'H:Q01.c1', 'H:Q01.c3', 'k_gaybi_hiss_yok', 'k_haber_devir', 'k_tekduzelik_aciklama', 'k_istisna_delilsiz'],
  'Cezmî nefyin desteği ya çıkarımsızdır (duyu yetmez, haber devralır, evvelî değildir) ya çıkarımlıdır; çıkarımlıysa öncüller ya hükmü gerektirir (kavram çelişkisi veya kesin bir olguyla çelişki: Q01’de çürüdü) ya gerektirmez ve köprü ister; tek tecrübî köprü olan tekdüzelik “bütün de açıklanmıştır” sonucunu verir, “bütün istisnadır” köprüsünün ise evvelîliği ve delili yoktur; kollar tükendiğinden cezmî nefy savunulamaz ve geriye yalnız tevakkuf kalır.')
P('Q03.c1', 'U12', ['m_mumkin', 'm_degisim', 'k_degisen_vacib_degil'], 'Âlemde değişen ve başka türlü olabilen şeylerin bulunduğu müşâhede edilir.')
P('Q03.c1', 'U26', ['m_ben', 'e_celismezlik'], '“Varlık kuruntudur” diyen, kuruntu eden bir varlığı kabul eder.')
P('Q03.c1', 'U07', ['m_ben', 'e_celismezlik'], 'Hiçbir şey yoksa bu cümleyi söyleyen de yoktur.')
P('Q03.c2', 'U03', ['m_tahsis', 'k_tercihsiz', 'k_butunun_dis_muhtac', 'k_terkip'],
  'Bütünün müreccihi yoksa tahsis tercihsiz tercih olur; tercihsiz tercih imkânsızdır.')
P('Q03.c2', 'U07', ['k_tercihsiz_hal', 'k_butunun_dis_muhtac', 'm_tahsis'], 'Sebepsiz bütün kabul edilirse belirli hâl açıklanamaz.')
P('Q03.c2', 'U26', ['k_sebepsiz_bagimsiz'], 'Sebepsiz olgu savunusu kendi gerekçesini ister.')
P('Q03.c2', 'U27', ['m_frekans_sans', 't_sans_egilim', 'k_yoktan_sanssiz', 't_bayes_aralik', 'p_esdegerlik_kureselleme'],
  'Mümkinler bütününün müreccihsiz olması yokluktan varlık demektir; orada süreç ve eğilim yoktur; olasılığı [0,1] kalır; hasım düşük öncül yolunu yerelde kabul ediyorsa küreselde de vermek zorundadır; öyleyse kendi ölçüsüyle çıplak evren düşük öncüllüdür.')
P('Q03.c2', 'U17', ['k_sebepsiz_bilgi', 'm_tahsis'], 'Sebepsiz olgu kabul edilirse hiçbir ilmî açıklamanın temeli kalmaz.')
P('Q03.c2', 'U08', ['k_aciklama_temelli', 'k_istisna_yapi', 'H:Q03.c3', 'H:Q03.c4'],
  'Bütün açıklamasız fakat her parça içeriden açıklanmışsa açıklama ilişkisi temelsizdir; temelsiz ilişki ya sonsuz geriye gider (Q03.c3) ya devirdir (Q03.c4); ikisi de çürütüldü.',
  kismi='yalnız “her parça içeriden açıklanmıştır” istisna biçimini kapsar; açıklanmamış bir parçanın bulunduğu kolları (sebepsiz hâdis ve ezelî mümkinin çıplak varlığı) kapsamaz')
P('Q03.c2', 'U14', ['m_tahsis', 'k_simetri_kirilma'], 'Bilinen simetri kırılmalarının hepsinde kırıcı bulunmuştur; tarama tam olmadığından ve bütüne taşıma köprü istediğinden netice zannîdir.')
P('Q03.c3', 'U05', ['k_muhtac_mumkin', 'k_butunun_dis_muhtac', 'e_celismezlik'],
  'Hiçbir halka varlığı kendi başına kazandırmıyorsa bütün zincir de kazandıramaz.', tag=None, hd='Eşzamanlı zâtî zincir için işler.')
P('Q03.c3', 'U07', ['k_sonsuz_hadis', 'm_degisim'], 'Geçmişte sonsuz hâdis dizisi olsaydı bugüne ulaşan hâl hiç gelmezdi.')
P('Q03.c4', 'U06', ['k_devir_imkansiz', 'e_celismezlik'], 'Devirde her halka hem önce hem sonra olurdu.')
P('Q03.c4', 'U07', ['k_devir_imkansiz', 'e_celismezlik', 'k_kendi_kendine'], 'Dairesel zincir çelişmezlik evveliyyâtına aykırıdır.')
P('Q03.c5', 'U06', ['k_kendi_kendine', 'e_celismezlik'], 'Kendi varlığına sebep olan, önce var olmak zorunda kalır.')
P('Q03.c5', 'U28', ['k_kendi_kendine', 't_mumkin'], 'Mümkinin tanımı varlığını zâtından almamaktır; kendi sebebi olması tanıma aykırıdır.')
P('Q03.c5', 'U07', ['k_kendi_kendine', 'e_celismezlik'], 'Kendi kendine sebep olan hem önce hem sonra olmalıdır.')

P('Q04.c1', 'U17', ['m_nizam', 'm_ihkam', 'k_fail_vacib'], 'Nizamdaki birlik tek Vâcib’i en iyi açıklar; ikincisi gerekli olmayan hipotezdir.')
P('Q04.c2', 'U28', ['t_vacib', 'k_cokluk_terkip', 'k_basit_vacib'], 'İki vâcibi ayıran bir fark varsa her birinde ortak ve ayırıcı iki mâna bulunur; bu terkiptir.',
  tag=('enne', 'suret'))
P('Q04.c2', 'U07', ['t_vacib', 'k_aciz_vacib_degil', 'k_kudret_fiil', 'k_irade_cuzi'],
  'İki ihtiyarlı vâcib ihtilaf ederse biri aciz kalır veya ikisi de aciz kalır; aciz olan vâcib olamaz.',
  kismi='yalnız iki ihtiyarlı vâcib varsayımını kapsar; ihtiyarsız iki vâcib için terkip yolu (U28, U08) gerekir')
P('Q04.c2', 'U08', ['k_ozdes', 'k_cokluk_terkip', 'k_basit_vacib', 'e_ucuncu_sik'],
  'İki vâcib arasında ya hiçbir fark yoktur ve ikisi birdir, ya fark vardır ve terkip doğar.')
P('Q04.c2', 'U27', ['k_kemal', 'k_muhtac_mumkin'], 'İyilik ve kötülük gibi iki zıt ezelî ilkeyi savunan, her birini kendi kemâlinden mahrum sayar.')
P('Q04.c3', 'U07', ['H:Q04.c2', 'k_cok_vacib_cift'], 'Üç veya daha fazla vâcib içinden herhangi ikisi “iki vâcib” durumudur; o hâl yukarıda çürüdü.')
P('Q04.c4', 'U07', ['H:Q04.c2', 'k_cok_vacib_cift', 'k_sonsuz_vacib'], 'Sonsuz vâcib içinden herhangi ikisi “iki vâcib” durumudur; o hâl yukarıda çürüdü.')

P('Q05.c1', 'U07', ['k_basit_vacib', 'k_parca_muhtac', 'k_muhtac_mumkin', 't_vacib'], 'Parçası olan parçasına muhtaçtır; muhtaç mümkindir; Vâcib mümkin olamaz.',
  kismi='yalnız hâricî (maddî) parçaları kapsar; zihnî parça için k_zihni_parca gerekir')
P('Q05.c1', 'U07', ['k_basit_vacib', 'k_parca_muhtac', 'k_muhtac_mumkin', 't_vacib', 'k_zihni_parca'], 'Hâricî ve zihnî parça birlikte ele alınır; ikisi de muhtaçlık doğurur.')
P('Q05.c1', 'U28', ['t_vacib', 'k_basit_vacib', 'k_zat_vacip_tutarli', 'k_zihni_parca'], 'Tanım gereği Vâcib hiçbir bakımdan muhtaç değildir; öyleyse hâricî veya zihnî parçası yoktur.',
  hd='Kelâm içi zât–sıfat ihtilafı hariç tutulur.')
P('Q05.c2', 'U07', ['k_parca_muhtac', 'k_muhtac_mumkin', 't_vacib'], 'Hâricî parçalı Vâcib parçalarına muhtaç olurdu.')
P('Q05.c2', 'U28', ['t_vacib', 'k_parca_muhtac', 'k_muhtac_mumkin'], 'Vâcibin tanımı parça ile bağdaşmaz.')
P('Q05.c3', 'U07', ['k_zihni_parca', 'k_parca_muhtac', 'k_muhtac_mumkin'], 'Zihnî ayrım hâricî terkibe delâlet ediyorsa Vâcib muhtaç olurdu.')
P('Q05.c5', 'U07', ['H:Q04.c2', 'H:Q04.c3', 'H:Q05.c3', 'k_cok_vacib_cift'],
  'Üç kimlik ya ayrı vâcibdir (sayı çürüdü) ya zihnî ayrımdır (zihnî parça çürüdü).', hd='Teslis’in kendi kaynakları okunmadığından bu ilzam değil, aklî hasırdır.')

P('Q06.c1', 'U07', ['m_degisim', 'k_degisen_vacib_degil', 't_vacib'], 'Vâcib âlemle özdeş olsaydı değişirdi; değişen vâcib olamaz.')
P('Q06.c1', 'U07', ['m_cok', 'k_basit_vacib', 'k_parca_muhtac'], 'Âlemde çokluk vardır; Vâcib basittir; çoklukla basitlik özdeş olamaz.')
P('Q06.c2', 'U07', ['k_parca_muhtac', 'k_muhtac_mumkin', 't_vacib'], 'Bütünün parçası olan bütüne muhtaçtır.')
P('Q06.c3', 'U07', ['H:Q05.c2', 'k_parca_muhtac', 'm_degisim', 'k_degisen_vacib_degil'], 'Âlem Vâcib’in parçası olsaydı Vâcib parçalı ve değişken olurdu.')

P('Q07.c1', 'U07', ['t_cisim', 'k_cisim_parcali', 'k_parca_muhtac', 'H:Q05.c2'], 'Cisim parçalıdır; Vâcib’in hâricî parçası yoktur.')
P('Q07.c1', 'U28', ['t_cisim', 'k_cisim_parcali', 'k_basit_vacib'], 'Cisim tanımı gereği bölünebilir; Vâcib basittir.')
P('Q07.c1', 'U07', ['k_hudus_cisim', 'k_hadis_muhdis', 'k_muhtac_mumkin'], 'Cisim hâdistir; hâdis vâcib olamaz.')
P('Q07.c3', 'U07', ['k_mekan_cisim', 'H:Q07.c1', 'k_hulul_muhtac'], 'Mekânlı olan cisimdir veya cisimde kâim arazdır; cisim değilse araz olur ve mahalle muhtaçtır.')

P('Q08.c1', 'U07', ['t_hulul', 'k_hulul_muhtac', 'k_muhtac_mumkin'], 'Yerleşen mahalle muhtaçtır; muhtaç mümkindir.')
P('Q08.c1', 'U28', ['t_hulul', 'k_hulul_muhtac'], 'Hulûl tanımı mahalle muhtaçlığı içerir.')
P('Q08.c2', 'U07', ['t_ittihad', 'k_ittihad_imkansiz', 'e_celismezlik'], 'İki ayrı şey ayrı olarak devam ederken bir olamaz.')
P('Q08.c2', 'U28', ['t_ittihad', 'e_celismezlik'], 'İttihâd tanımı iki ve bir olmayı birleştirir.')

P('Q09.c1', 'U03', ['m_mumkin', 'k_tercihsiz', 'H:Q02.c1', 'H:Q06.c1', 'H:Q04.c2'],
  'Âlem mümkindir ve müreccihe muhtaçtır; müreccih tek ve âlemden ayrı olan Vâcib’dir; öyleyse âlem Vâcib’den bağımsız değildir.', tag=('enne', 'fail'))
P('Q09.c1', 'U04', ['m_degisim', 'k_hadis_muhdis', 'H:Q02.c1', 'H:Q06.c1', 'H:Q04.c2'], 'Âlemin muhdisi tek ve ayrı Vâcib’dir.', tag=('enne', 'fail'))
P('Q09.c2', 'U07', ['m_tahsis', 'm_degisim', 'k_zorunlu_sonuc', 'k_irade_cuzi'],
  'Zorunlu sebepten tek ve değişmez sonuç çıkar; âlemde belirli hâl ve değişim vardır.',
  kismi='Sudûrcu felsefecilerin akıllar silsilesi cevabı yoklanmadı; bu delil yalnız tek basamaklı zorunlu sudûru kapsar')
P('Q09.c2', 'U07', ['H:Q13.c1', 'k_zorunlu_sonuc'], 'Zorunlu sebebin sonucu ezelîdir; âlem hâdis olduğundan zorunlu sudûr çürür.')
P('Q09.c3', 'U03', ['k_beka_muhtac', 'm_mumkin', 'k_tercihsiz'], 'Mümkin âlemin devamı da her an müreccihe muhtaçtır.')
P('Q09.c3', 'U27', ['k_kemal', 'k_gaye'], 'Yaratıp bırakmak, fiilin gâyesinden ve yaratıcının kemâlinden vazgeçmektir.')
P('Q09.c4', 'U03', ['m_mumkin', 'k_tercihsiz', 'k_beka_muhtac', 'H:Q02.c1'], 'Mümkin her an müreccihe muhtaç olduğundan Vâcib her an var edip ayakta tutar.', tag=('enne', 'fail'))
P('Q09.c4', 'U07', ['m_tahsis', 'k_irade_cuzi', 'k_tercihsiz_hal'], 'Belirli hâlin seçilmesi iradeli fâilin işidir; zorunlu sebep belirli hâli seçemez.', tag=('enne', 'fail'))
P('Q09.c4', 'U17', ['m_nizam', 'm_ihkam', 'k_ihkam_ilim', 'k_fail_vacib'], 'Muhkem eser ilimli ve iradeli bir fâile işaret eder.', tag=('enne', 'gaye'))

P('Q11.c1', 'U07', ['m_tahsis', 'k_irade_ilim', 'k_irade_cuzi', 'H:Q09.c4'], 'Âlemi ihtiyarla var eden âlemi bilmek zorundadır.')
P('Q11.c2', 'U07', ['m_tahsis', 'k_irade_cuzi', 'k_irade_ilim', 'H:Q09.c4'], 'İrade belirliye taalluk eder; belirliyi bilmeden iradeden söz edilemez.')
P('Q11.c3', 'U17', ['m_ihkam', 'k_ihkam_ilim', 'k_fail_vacib'], 'Muhkem ve ayrıntılı eser ilmin kuşatıcı olduğunu gösterir.')
P('Q11.c3', 'U07', ['k_irade_ilim', 'k_irade_cuzi', 'H:Q10.irade.c1'], 'Her cüz’î hâl iradeye konu olduğundan her cüz’î bilinir.')
P('Q11.c4', 'U07', ['k_ilim_degisim', 't_vacib', 'k_zaman_vacib_degil', 'H:Q09.c4'], 'Geleceği sonradan öğrenen değişir; değişen vâcib olamaz.')

P('Q12.c1', 'U28', ['t_vacib', 'k_zorunlu_tanim', 'k_sebep_istemez'], 'Vâcib’in vücûbunun sebebi tanım gereği zâtıdır; sebep sorusu zâta döner.', tag=('enne', 'suret'))
P('Q12.c1', 'U07', ['k_zorunlu_tanim', 'k_muhtac_mumkin', 't_vacib'], 'Vücûbu başka sebepten olsaydı Vâcib mümkin olurdu.')
P('Q12.c2', 'U07', ['k_zorunlu_tanim', 'k_muhtac_mumkin', 't_vacib'], 'Vücûbunu başkasından alan mümkindir.')
P('Q12.c3', 'U28', ['t_vacib', 'k_zorunlu_tanim', 'k_sebep_istemez'], 'Tanım gereği açıklama zâtın kendisidir; açıklama yoktur demek tanıma aykırıdır.')
P('Q12.c4', 'U29', ['k_zorunlu_tanim', 'k_sibr_sebep'], 'Soru geçerlidir ve cevabı zâtın kendisidir.')
P('Q12.c4', 'U26', ['k_sebepsiz_bagimsiz'], 'Sorunun geçersizliğini savunan bir gerekçe getirir; gerekçe getirmek açıklama aramaktır.')

P('Q13.c1', 'U04', ['m_degisim', 't_alem', 'k_hudus_cisim', 'k_cisim_parcali', 'k_sonsuz_hadis'], 'Âlem değişen cisimlerden oluşur; cisim hâdistir; sonsuz hâdis dizisi imkânsızdır.',
  tag=('enne', 'fail'))
P('Q13.c1', 'U07', ['k_sonsuz_hadis', 'm_degisim', 'k_hudus_cisim'], 'Âlem ezelî olsaydı sonsuz hâdis dizisi gerekirdi.')
P('Q13.c2', 'U07', ['m_degisim', 'k_degisen_vacib_degil', 'H:Q06.c1'], 'Âlem değişir; değişen vâcib olamaz.')

P('Q14.c1', 'U07', ['k_sinirli_mumkin', 'k_muhtac_mumkin', 't_vacib'], 'Kemâli sınırlı olsaydı sınırı bir müreccihle belirlenir ve Vâcib muhtaç olurdu.')
P('Q14.c1', 'U09', ['k_kemal', 'm_bilinc', 'm_ihkam', 'k_fail_vacib'], 'Şâhidde (insanda) bulunan kemâl, onu verende eksik olamaz.',
  hd='Gâib–şâhid yalnız kemâl için işler, noksan için işlemez.')
P('Q14.c1', 'U17', ['k_kemal', 'm_bilinc', 'k_fail_vacib'], 'Bilinç ve anlam arayışı kemâli veren kaynağın mahrum olmadığını en iyi açıklar.')
P('Q14.c2', 'U07', ['k_sinirli_mumkin', 'k_muhtac_mumkin', 't_vacib'], 'Sabit sınır da bir müreccihle belirlenir.')
P('Q14.c3', 'U07', ['k_degisen_vacib_degil', 't_vacib'], 'Gelişen şey bir hâlini yitirir; vâcib olamaz.')
P('Q14.c3', 'U07', ['k_aciz_vacib_degil', 't_vacib'], 'Sonradan kemâl kazanan önceden aciz kalmıştır.')

P('Q15.c1', 'U17', ['k_muhtac_ibadet', 'H:Q09.c4', 'H:Q04.c1'], 'Varlığı veren tek ve ayakta tutan Vâcib olduğundan nihaî bağlılık yalnız O’na lâyıktır.')
P('Q15.c1', 'U32', ['m_bilinc'], 'Mutlak olana bağlanma eğilimi delil değil, muhatabı yönlendiren tenbihtir.')
P('Q15.c2', 'U07', ['k_muhtac_ibadet', 'H:Q09.c4', 'H:Q04.c1'], 'Başkaları mümkindir ve varlığını Vâcib’den alır; nihaî bağlılığa lâyık olamazlar.')
P('Q15.c3', 'U07', ['k_muhtac_ibadet', 'H:Q09.c3', 'H:Q09.c4'], 'Vâcib âlemi her an ayakta tuttuğundan ilgisiz değildir.')
P('Q15.c4', 'U28', ['k_muhtac_ibadet', 'H:Q09.c4'], 'İbadetin tanımı varlığı ve nimeti verene bağlılıktır; Vâcib bunu verir.')
P('Q15.c4', 'U07', ['k_muhtac_ibadet', 'H:Q09.c4', 'm_bilinc'], 'Bağlılık duygusu ve anlam arayışı boş değildir; muhatabı vardır.')

P('Q16.c1', 'U17', ['m_nizam', 'm_ihkam', 'k_ihkam_ilim'], 'İnce ayar ve muhkemlik rastlantıdan çok kasda işaret eder.')
P('Q16.c1', 'U07', ['k_tercihsiz_hal', 'm_nizam'], 'Çoklu evren de belirli bir çokluk mekanizması ister; çokluğun kendisi de tercihtir.',
  kismi='Çoklu evrenin kendi sebebine dair sorusu sebep ilkesine bağlıdır; ilke kabul edilmezse delil işlemez')
P('Q16.c2', 'U07', ['m_degisim', 'k_degisen_vacib_degil', 'm_tahsis'], 'Madde zâtından zorunlu olsaydı başka türlü olamaz ve değişmezdi.')
P('Q16.c3', 'U17', ['m_nizam', 'm_ihkam', 'k_ihkam_ilim'], 'Muhkem nizamın en iyi açıklaması ilim ve iradeli bir fâilin kasdıdır.', tag=('enne', 'gaye'))
P('Q16.c3', 'U25', ['k_gaye', 'm_ihkam'], 'Gâyeye uygun düzen gâî sebebe işaret eder.', tag=('enne', 'gaye'))

P('Q17.c1', 'U07', ['H:Q02.c1'], 'Vâcib’in varlığına yakîn derecede bir ispat bulunduğundan yakîn bilinebilir.', sarti='yakîn')
P('Q17.c2', 'U07', ['H:Q02.c1'], 'Yakîn derecede bir ispat bulunduğundan yalnız zan denemez.', sarti='yakîn')
P('Q17.c3', 'U26', ['k_bilinemez_bilgi', 'H:Q18.c1'], 'İlkesel bilinemezlik hükmü bir bilgi iddiasıdır.')
P('Q17.c3', 'U07', ['H:Q02.c1'], 'En az zan derecesinde ispat bulunduğundan hiçbir derecede bilinemez denemez.', sarti='zan')

for sid in ('kidem', 'beka', 'gina', 'hayat', 'ilim', 'kudret', 'irade', 'semi', 'basar', 'kelam', 'tekvin', 'hikmet', 'adalet', 'rahmet', 'sidk'):
    P('Q10.' + sid + '.c2', 'U07', ['k_muhtac_mumkin', 'k_tercihsiz_hal', 'k_sebep_istemez', 'k_zorunlu_tanim', 't_vacib'],
      'Sıfat mümkin olsaydı sıfatlı veya sıfatsız hâl bir müreccih isterdi; müreccih Vâcib’in dışında olamaz ve zâtı olursa sıfat zorunlu olur.')

P('Q10.kidem.c1', 'U28', ['t_vacib', 'e_celismezlik', 'k_zat_vacip_tutarli'], 'Vâcib hâdis olsaydı bir an yok olmuş olurdu; yokluğu imkânsız olan için bu çelişir.', tag=('enne', 'suret'))
P('Q10.kidem.c1', 'U07', ['t_vacib', 'e_celismezlik'], 'Kadîm değilse hâdistir; hâdis olan vâcib değildir.')
P('Q10.kidem.c3', 'U07', ['t_vacib', 'e_celismezlik'], 'Kıdem imkânsız olsaydı Vâcib başlangıçlı olur ve yokluğu mümkün olurdu.')
P('Q10.beka.c1', 'U28', ['t_vacib', 'e_celismezlik'], 'Yokluğu imkânsız olanın yokluğu gelemez.', tag=('enne', 'suret'))
P('Q10.beka.c3', 'U07', ['t_vacib', 'k_zorunlu_tanim'], 'Bekâ imkânsız olsaydı yokluk mümkin olur ve Vâcib mümkin olurdu.')
P('Q10.gina.c1', 'U07', ['t_vacib', 'k_muhtac_mumkin'], 'Bir şeye muhtaç olan mümkindir.')
P('Q10.gina.c3', 'U07', ['t_vacib', 'k_muhtac_mumkin'], 'Gınâ imkânsız olsaydı Vâcib muhtaç ve mümkin olurdu.')
P('Q10.hayat.c1', 'U07', ['k_aciz_vacib_hayat', 'H:Q10.ilim.c1', 'H:Q10.kudret.c1'], 'İlim ve kudret sahibi olan hayydır.')
P('Q10.hayat.c3', 'U07', ['k_aciz_vacib_hayat', 'H:Q10.ilim.c1'], 'İlim sahibi için hayat imkânsız olamaz.')
P('Q10.ilim.c1', 'U07', ['k_irade_ilim', 'H:Q10.irade.c1'], 'İrade murad edilenin bilinmesini gerektirir.')
P('Q10.ilim.c1', 'U17', ['m_ihkam', 'k_ihkam_ilim', 'k_fail_vacib'], 'Muhkem eser ilme işaret eder.')
P('Q10.ilim.c3', 'U07', ['k_irade_ilim', 'H:Q10.irade.c1'], 'İradeli fâil bilmeyen olamaz.')
P('Q10.kudret.c1', 'U07', ['k_kudret_fiil', 'H:Q09.c4'], 'Var etme fiili kudretsiz olmaz.')
P('Q10.kudret.c1', 'U24', ['k_kudret_fiil', 'H:Q09.c4'], 'Fâilden fiile geçilir.', tag=('enne', 'fail'))
P('Q10.kudret.c3', 'U07', ['k_kudret_fiil', 'H:Q09.c4'], 'Kudret imkânsız olsaydı var etme fiili olmazdı.')
P('Q10.irade.c1', 'U07', ['k_irade_cuzi', 'H:Q09.c4'], 'Belirli hâlin seçilmesi iradeyi gerektirir.')
P('Q10.irade.c1', 'U03', ['m_tahsis', 'k_irade_cuzi', 'k_tercihsiz_hal'], 'Mümkin hâller arasından birini seçen tahsis iradeyle olur.')
P('Q10.irade.c3', 'U07', ['k_irade_cuzi', 'H:Q09.c4'], 'İrade imkânsız olsaydı ihtiyarlı fâillik de imkânsız olurdu.')
for sid in ('semi', 'basar', 'kelam'):
    P('Q10.' + sid + '.c3', 'U07', ['k_kemal', 'H:Q14.c1'], 'Bu sıfatın imkânsızlığı bir noksandır; Vâcib noksandan münezzehtir.',
      hd='Yalnız noksandan münezzehliği kapsar; zâid sıfat mı zâtın aynı mı sorusu kelâm içi ihtilaftır.')
P('Q10.tekvin.c3', 'U07', ['k_kudret_fiil', 'H:Q09.c4', 'H:Q10.kudret.c1'], 'Var etme imkânsız olsaydı Vâcib âlemi var edemezdi.',
  hd='Zâid sıfat mı kudret ve iradeye dönüş mü sorusu kelâm içi ihtilaftır.')
P('Q10.hikmet.c1', 'U17', ['k_gaye', 'k_kemal', 'm_ihkam', 'k_fail_vacib'], 'Gâyesiz fiil kemâle ters düşer; eser gâyeli görünür.')
P('Q10.hikmet.c1', 'U25', ['k_gaye', 'm_ihkam', 'k_fail_vacib'], 'Gâyeye uygun düzen gâî sebebe işaret eder.', tag=('enne', 'gaye'))
P('Q10.hikmet.c3', 'U07', ['k_gaye', 'k_kemal'], 'Gâyesiz olmak kemâle ters düşer.')
P('Q10.adalet.c1', 'U07', ['k_zulum_noksan', 'H:Q14.c1'], 'Zulüm noksandan doğar; Vâcib noksandan münezzehtir.')
P('Q10.adalet.c3', 'U07', ['k_zulum_noksan', 'H:Q14.c1'], 'Adâlet imkânsız olsaydı zulüm mümkin olurdu.')
P('Q10.rahmet.c1', 'U17', ['m_ihkam', 'k_gaye', 'H:Q09.c4'], 'Varlık ve nimet verme gâyeli bir ihsandır.')
P('Q10.rahmet.c3', 'U07', ['k_gaye', 'H:Q09.c4', 'H:Q14.c1'], 'İhsan imkânsız olsaydı kemâl sınırlı olurdu.')
P('Q10.sidk.c1', 'U07', ['k_yalan_noksan', 'H:Q14.c1'], 'Yalan noksandan doğar; Vâcib noksandan münezzehtir.')
P('Q10.sidk.c3', 'U07', ['k_yalan_noksan', 'H:Q14.c1'], 'Sıdk imkânsız olsaydı yalan mümkin olurdu.')

# 3-I 242: Mâtürîdî okumasından türetilen ispatlar (Arş: V.2.16; tevhid: V.2.6; ihtiyar: V.2.14; hikmet: V.1.3.M)
P('Q07.c3', 'U07', ['t_alem', 'H:Q04.c1', 'H:Q13.c1', 'k_alem_parca_hadis', 'k_mekanda_olus_hal', 'k_degisen_vacib_degil', 'e_ucuncu_sik'],
  'Mekânlı Vâcib ya ezelden mekândadır (mekân âlemdendir ve ezelî olur; âlem hâdistir) ya sonradan mekâna girmiştir (hâl değiştirir; değişen vâcib olamaz); iki kol da çürür (Mâtürîdî, Arş).',
  hd='Mekânın âlemin parçası olduğu ve hâdis olduğu öncülleri ayrıca yazılmıştır (alem-parca ailesi); Kâ’bî’nin mekân edinmenin değişiklik gerektirmediği itirazı mekan-degisim ailesine düşer.')
P('Q07.c3', 'U07', ['k_mekanli_sinirli', 'k_sinirli_mumkin', 'k_muhtac_mumkin', 't_vacib'],
  'Mekânla sınırlı olanın hacmi ve sınırı vardır; sınır bir müreccihle belirlenir; müreccihe muhtaç olan mümkindir ve Vâcib olamaz (Mâtürîdî, Arş; imkân–vücûb çekirdeğine indirgenmiş biçim).')
P('Q07.c3', 'U07', ['k_mekan_uclu', 'k_kusatma_muhtac', 'k_muhtac_mumkin', 'k_basit_vacib', 'k_parca_muhtac', 't_vacib'],
  'Mekân Vâcib’i kuşatırsa kuşatılan kuşatana bağlıdır ve mümkin olur; Vâcib mekânı aşarsa bir kısmı mekânın içinde bir kısmı dışında olur ve parçalanır; iki şık da çürür (Mâtürîdî, üç ihtimal argümanı).',
  kismi='Yalnız kuşatma ve aşma şıklarını kapsar; eşitlik şıkkı Mâtürîdî’de “ilâve yaratılınca küçük kalır” ve acz argümanına bağlanır (V.2.16.28–29) ve burada kayıtlı değildir')
P('Q07.c3', 'U29', ['k_yon_delil_cift', 'e_celismezlik'],
  'El kaldırmanın Allah’ın yukarıda olduğunu gösterdiği iddiası, secde ve kıble eylemleri karşıt yönlere yöneldiğinden kendi gerekçesiyle çürür; ibadetin yönü ilâhın yönü değildir (Mâtürîdî, Arş).',
  kismi='Yalnız yön (el kaldırma, secde, kıble) delilini çürütür; mekânlı oluşun başka delillerini kapsamaz, bu yüzden hücreyi tek başına ispatlamaz')
P('Q13.c2', 'U27', ['k_asil_ikilem', 'k_kudret_fiil', 'k_irade_cuzi', 'm_tahsis', 'H:Q09.c4'],
  'Âlemi kadîm ve zorunlu bir asla bağlayan, o asla âlemi var etme ve yönetme gücü veriyorsa onu Vâcib’in sıfatlarıyla tanımlamıştır ve fark yalnız addır; vermiyorsa açıklama başka şeye kalır (Mâtürîdî, adlandırma farkı ilzamı).',
  hd='Yalnız ilk asılı var edici ve yönetici sayan muhatabı bağlar; bu fiilleri asıla vermeyen muhatap için açıklama sorusu Q03.c2’ye kalır.')
P('Q09.c2', 'U07', ['m_cok', 'm_tahsis', 'k_zorunlu_sonuc', 'k_tek_ozellik_cesitlilik'],
  'Zorunlu ve tek özellikli sebepten çeşitli ve zıt özellikli bir âlem çıkmaz; alıcı farkı ise ayrıca açıklama ister (Mâtürîdî, sudûr itirazı).',
  kismi='Sudûrcu felsefecilerin akıllar silsilesi ve alıcı farkının kaynağı cevabı yoklanmadı; bu kayıt yalnız tek basamaklı zorunlu sudûru kapsar')
P('Q10.irade.c1', 'U17', ['m_cok', 'm_tahsis', 'k_tabi_tek_tur', 'k_irade_cuzi'],
  'Âlemde çokluk ve çeşitlilik vardır; tabiatıyla iş yapan tek türde iş yapar; çeşitli fiil ihtiyarlı ve iradeli fâile işaret eder (Mâtürîdî, ilâhî fiillerin ihtiyarîliği).')
P('Q04.c2', 'U07', ['k_gizleme_gucu', 'k_aciz_vacib_degil', 'k_bilgisiz_vacib_degil', 't_vacib'],
  'İki ilâhtan biri diğerinden gizli fiil işleyebiliyorsa diğeri bilgisizdir, işleyemiyorsa kendisi güçte sınırlıdır; her iki hâlde biri noksandır ve vâcib olamaz (Mâtürîdî, gizleme argümanı).')
