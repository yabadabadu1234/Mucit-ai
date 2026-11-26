import collections
import re

BAZ = {
    'VAR': ('VarEtme', 'Yoktan var etme, yaratma, doğurma, ortaya çıkarma, kurma ve yapma', ['verb.creation'], 'VarEtme'),
    'OLU': ('Oluş', 'Olma, kalma, bulunma, durma, var olma; hâlin sürmesi', ['verb.stative'], 'yok (veriden eklendi)'),
    'KIL': ('Kılma', 'Hâl ve nitelik dönüştürme: ol, -laş, -kıl', ['verb.change'], 'Kılma'),
    'DEG': ('Değiştirme', 'Ölçü yönünde değişim: artırma, eksiltme, genişletme, daraltma, ağırlaştırma, hafifletme', ['verb.change'], 'Değiştirme'),
    'AKT': ('Aktarım', 'Yer değiştirme ve aktarma: gelme, gitme, indirme, çıkarma, gönderme, akma, düşme', ['verb.motion', 'verb.weather'], 'Aktarım'),
    'KAP': ('Kapı', 'Açma, kapama, tutma, bırakma, engelleme, saklama, örtme, koruma', ['verb.contact (tutma)'], 'Kapı'),
    'TEM': ('Temas', 'Cisme fizikî etki: vurma, kesme, yırtma, kırma, yıkma, delme, yakma, öldürme', ['verb.contact'], 'yok (veriden eklendi)'),
    'BED': ('Beden', 'Canlı bedenin iç hâli: yeme, içme, uyuma, ölme, hastalanma, ağlama, gülme, nefes', ['verb.body', 'verb.consumption'], 'yok (veriden eklendi)'),
    'IDR': ('İdrâk', 'Bilme, görme, işitme, düşünme, hatırlama, unutma, sanma, anlama', ['verb.cognition', 'verb.perception'], 'İdrâk'),
    'BEY': ('Beyân', 'Söyleme, çağırma, bildirme, yazma, yemin, uyarma, müjdeleme, yalanlama', ['verb.communication'], 'Beyân'),
    'YON': ('Yönelim', 'İrade, duygu ve inanç yönelişi: iman, inkâr, sevgi, korku, umut, öfke, kibir, şükür, niyet', ['verb.emotion'], 'Yönelim'),
    'HUK': ('Hükmetme', 'Mülk, verme, alma, rızık, bağış, ceza, hüküm, ücret, ticaret', ['verb.possession'], 'Hükmetme'),
    'BAG': ('Bağ', 'İlişki kurma ve koparma: evlenme, dostluk, ortaklık, birleştirme, ayırma, ahit, yardım', ['verb.social'], 'yok (veriden eklendi)'),
    'MUC': ('Mücadele', 'Çatışma ve yarış: savaş, cihad, galibiyet, kovma, kuşatma, direnme', ['verb.competition'], 'yok (veriden eklendi)'),
}

G={
'VAR':"amel et;başla;bit;biçimle;biçimlen;biçimlendir;doğ;doğur;döllen;ek;ekin ek;ekmek yap;düzenle;gebe kal;hazırla;hazırlan;iplik eğir;iş yap;işle;kur;meyve ver;neden ol;ortaya çık;sağlamca yap;süt çalkala;tamamla;yap;yarat;yerine getir;yetiş;yol koy;önceden yap;başar;iz bırak;boya",
'OLU':"barın;başarısız ol;boşa git;boşa çık;bulun;dayan;değil ol;dul kal;dur;ebedi kal;geceyi geçir;gecik;gerekli ol;gözleri dönük kal;güneşe maruz kal;hazır bulun;iffetli kal;işsiz kal;kal;karar;konakla;kuruyup git;kök sal;meşgul ol;ol;oluş ol;orta ol;otur;refah içinde yaşa;sabit ol;tek kal;uzak kal;vakti gelme;var;var ol;yakın;yakın ol;yat;yaşa;yerleş;yet;yetim kal;yok ol;yüksek ol;yıl ol;zorunlu ol;âdet gör;oyn",
'KIL':"Araplaş;aciz bırak;akıllı ol;akılsız ol;alev ol;alevlen;alevlendir;alış;ağar;ağırbaşlı ol;ateşli ol;aydınlan;aydınlat;aziz kıl;bedbaht ol;benzeş;bilgisiz ol;bir şeyi yerinde olmayan yere koy;bozul;ceset ol;cimri ol;cisimleş;cömert ol;değiştir;delir;dengelen;denk ol;dikkatsiz ol;dişileş;don;doğrult;duvar ol;düz ol;eşit ol;gerdan ol;gerginleş;gevşek ol;gözü kamaş;güzel ol;güzelleştir;hoş ol;iyi ol;iyileş;kabalaş;kale ol;karan ol;karanlık çök;katılaş;kesinleş;kirlet;kol ol;kör ol;kötü ol;kötüleş;kısır ol;maviles;muhtaç ol;mutlu ol;neşelen;olgunlaş;onar;parla;parlat;paslan;rahat ol;rahatla;saf ol;sağır ol;sertleş;soğu;sön;süsle;tam ol;tazele;tedavi et;temizle;temizlen;tepe ol;toprakla temizlen;tüt;uygun kıl;yatış;yayvan yap;yumuşak ol;yıka;zeki ol;zenginleş;zor ol;çirkin ol;ıslah et;ısın;ışık ol;şekil değiştir;şifa ver;ısın;yıl ol;bulan;kuts",
'DEG':"alçal;alçalt;art;az;azal;azalt;ağırlaş;büyüt;dallan;daral;doldur;eksik ol;gevşe;genelleş;genişle;genişlet;gevşe;hafif ol;hafiflet;ikiye katla;incel;kalınlaş;kayna;kolaylaş;kuruyup coş;kıs;kısalt;sağlamlaş;sağlamlaştır;tüken;uza;uzat;yavaşla;yüceleş;yüksel;yükselt;zayıfla;çoğal;şiddetlen;güçlen",
'AKT':"acele et;adım at;ak;ayak bas;ayağa kalk;aş;bat;bin;bol akar;boşal;boşalt;dalgalan;damlat;denize açıl;derine in;dolaş;dök;dökül;dökülüp atıl;dön;döndür;dönüş;düş;es;etrafında dön;eğil;fışkır;fışkırt;gece yürü;gel;geri dön;geri çekil;geri çevir;getir;geç;gir;git;gönder;göç et;gürle;hareket et;heyet olarak gel;hızla koş;in;indir;izle;kaldır;kalk;karanlıkta yürü;karşılaş;kay;kaç;kaçır;koş;salla;sallan;sap;sarkıt;sars;sarsıl;sabaha eriş;sabahleyin git;savur;su çıkar;sür;sürükle;sürüklen;sürün;sız;takıl;taş;taşı;toplan;ulaş;uzaklaş;uzaklaştır;uç;yaklaş;yakınlaş;yay;yayıl;yağmur yağ;yere batır;yol tut;yuvarlan;yük taşı;yürü;yüz;yüz üstü düş;ziyaret et;çalkalan;çek;çekil;çekip çıkar;çevir;çök;çömel;çık;çıkar;önce gel;önce git;şimşek çak;açığa çık;boşa;ansızın bas",
'KAP':"aç;ağzını kapat;bürün;bırak;boğazda kal;daha çok sakla;dayandır;depola;ertele;engel ol;engelle;giy;giydir;gizle;gizlen;gölgele;göm;gözü kapat;hapset;içine al;kapat;kapsa;kaçın;kilitle;koru;korun;koy;kurtar;kurtul;kılıfla kapa;mühürle;önüne geç;perdele;sakın;sar;serbest bırak;sınırla;sıra sıra diz;sığın;soyun;terk et;tut;tutul;yasakla;yerleştir;yük bağla;yükle;yüklen;yığ;çevrele;çöz;ört;özgürleştir;üst üste koy;üst üste yığ",
'TEM':"as;at;ateş yak;ateşe at;ateşte yan;avucuyla al;bas;bastır;bağla;biç;boz;boğ;boğazla;bük;dal;del;delik aç;derisini yüz;dik;diri diri göm;dokun;dür;düğümle;ez;eziyet et;haşla;helâk et;it;kan akıt;kap;kavur;kaz;kazı;kendini helâk et;kes;kurban kes;kır;kıvır;kızart;ov;oyul;parça parça kes;parçala;sil;sök;soy;sık;sıyır;taşla;tıraş et;vur;yak;yan;yar;yarala;yarıla;yer kaz;yerinden kopar;yok et;yüzüstü at;yık;yıkıl;yırt;zarar ver;çak;çal;çatla;çiğne;çürüt;öldür;ısır;ıslat;boşuna uğraş",
'BED':"acık;acı çek;ağla;bayıl;besle;bitkin ol;bık;canlan;emzir;gül;hasta ol;helak ol;inle;iç;iç çek;işe;kaşlarını çat;kok;nefes al;oruç tut;otla;otlat;rahatla;semirt;sindir;soluk soluğa kal;sula;surat as;susuz ol;sıkıntı çek;sıkıntılan;titre;tüyleri diken diken ol;usan;uyanık kal;uyu;uyukla;uyuklama;uyut;ye;yedir;yut;zarar ver;öl;öğle uykusu uyu;üfle;aklet;yer;ağırlaş",
'IDR':"aldan;an;anla;araştır;bak;bekleyip gözetle;bil;bilme;bul;doğruyu bul;dönecek san;düşün;göz ucuyla bak;gözetle;gör;hata yap;hisset;işit;kendine gel;lezzet duy;san;sanan;say;sına;tahmin et;takdir et;tart;tat;unut;uy;ölç;örnek al;öğren;şaşkın ol;şaşır;şüphelen;görün;sorumluluk üstlen",
'BEY':"adıyla;allah'ın adıyla başla;alay et;anlat;ayıpla;azarla;açık konuş;açıkla;ağır ağır oku;bağır;boş konuş;doğru yola ilet;emret;feryat et;fetva iste;fısılda;gıybet et;haber ver;iddia et;ilham et;işaret et;işaretle;kanıtla;kanıtlan;kehanette bulun;kına;kitap yaz;konuş;lakap tak;lanetle;lânet oku;müjdele;mürekkeple yaz;nispet et;oku;sayfala;ses çıkar;seslen;sohbet et;söyle;söz ver;tarif et;tartış;tekrar et;temsil et;tenzih et;uğurla;vahyet;vasiyet et;vesvese ver;yalanla;yardım iste;yaz;yemin et;yemini boz;yüksek sesle söyle;çağır;çekiş;çekiştir;çirkin söyle;çiz;öf de;öv;övün;özür dile;öğüt ver;şahitlik et;şaka yap;şart koş;şefaat et;ahit ver;ada",
'YON':"aldat;amaçla;arzula;asi ol;aşağıla;başını eğ;bekle;boynu eğ;boyun eğ;bozguncu ol;borç;büyüklen;büyüle;caydır;cimrilik et;dalkavukluk yap;dile;diz çök;doğruya dön;dünyadan el çek;erken davran;esirge;gücen;günah işle;güven;haddi aş;hile kur;hile yap;hor gör;hoşlanma;hoşnut ol;hoşuna git;hırs göster;ibadet et;ihanet et;iman et;inat et;incelik göster;inkâr et;iste;isyan et;itaatten çık;içinde korku duy;kabul et;kararlı ol;karşı gel;karşı çık;kasten yap;kendini bir yere ver;keşke ol;kin besle;kinlen;kız;kork;korkut;kulluk et;merhamet et;meyilet;meylet;namaz kıl;nazlı davran;nefret et;nimete şükretme;nimeti tanıyıp teşekkür et;niyet et;ortak koş;pişman ol;reddet;sabırsız ol;sapık ol;sapıt;sev;sevin;sevindir;seç;suç işle;tamah et;teslim ol;teşvik et;tuzak kur;umudu kes;umudunu kes;umut et;uygun gör;vazgeç;yere kapan;yetin;yumuşak davran;yönel;yüz çevir;zina et;çabuk davran;çalış;çekeme;öfkelen;öfkelendir;özle;ümitsiz ol;ürk;üz;üzül;ısrar et;şımar;ne kö;gözleri;borçlan;aldan",
'HUK':"adil davran;affet;al;azap et;azık ver;başkanlık et;bağışla;biriktir;borç ver;cezalandır;din;edin;eksik tart;eksik ver;elde et;esir al;fayda ver;faydalan;fiyatla;ganimet al;görevden al;güzel davran;güç ver;haksızlık yap;halife kıl;hükmet;hüküm ver;ihsan et;ikramda bulun;imkân ver;intikam al;israf et;iyilik et;izin ver;kaybet;kazan;konuk et;kur'a çek;lütfede;meyve topla;meşru kıl;miras al;musallat kıl;mühlet ver;nimet ver;oy;rezil et;rızık ver;sadaka ver;sahip ol;sat;satın al;sert ele geçir;sorumluluk üstlen;sun;süre ver;sürgün et;taht kur;tam ver;tayin et;terbiye et;ticaret yap;vacip kıl;vakti belirlen;ver;vergi topla;yükümlü kıl;zengin et;zengin kıl;zorla;zorla al;çıkar;ödünç ver;ücret ver;üstün kıl;şöhret bul;saç;iz bırak",
'BAG':"arkadaşlık et;ayrıl;ayır;bağlan;bir araya getir;birle;bölün;dağıl;dağıt;destekle;dönüşümlü ol;eşlik et;evlen;gelin götür;hısım ol;ikiye böl;kardeş ol;karış;karıştır;kaynaştır;kenetle;sonuca bağla;sözünde dur;topla;yardım et;yardım etme;sıra ol",
'MUC':"akın et;avlan;baskın yap;bozguna uğrat;cihad et;diren;düşman ol;galip gel;koru;kov;kumar oyna;kuşat;savaş;silahlan;yen;yere ser;üstün gel;ansızın bas",
}

KOK_BAZ = {
    'بدع': 'VAR', 'حنك': 'HUK', 'درء': 'KAP', 'ذود': 'KAP', 'درج': 'AKT', 'ردف': 'OLU', 'ركن': 'YON', 'سبت': 'BED',
    'سكت': 'BEY', 'سكر': 'BED', 'صبو': 'YON', 'صمت': 'BEY', 'عسي': 'YON', 'غيث': 'AKT', 'فرش': 'VAR', 'فكه': 'YON',
    'لقم': 'BED', 'مهد': 'VAR', 'نصت': 'BEY', 'نهر': 'BEY', 'هاء': 'HUK', 'هات': 'AKT', 'هلم': 'AKT', 'هيت': 'AKT',
}

SAP_BAZ = {}
for _b, _s in G.items():
    for _x in _s.split(';'):
        _x = _x.strip()
        if _x and _x not in SAP_BAZ:
            SAP_BAZ[_x] = _b

ISIM_ZAYIF = set("ءبو ءله ءهل ءون بدن بقر بلد بوب ترب ثمن جبل جبه جحم جمم جند جيب حدب حصب حظظ حين خضر خمر خيط دمع دون ذرر رمد رمض رهن زبد زمر سبط سدس سقف سلسل سمم سنم سنو سوط شءم شتو شرذم شطن شكس شهب شيخ صخخ صفر صيف طرف طلل طور عسل عصب عنق غبر غدق غلم فقع فنن قرش قنطر لءلء لبن لحف ليل مجس محل مدن مصر ملح نجم نحل نطف نعل نور ورق وحش ودي وسل يمن يوم يدي".split())
ISIM_ZORLA = set("ءين بكك ثمم عدن عنن لوط ويل ثلث صبع".split())

BABLAR = {
    "fe'ale": ('I', 'sülâsî mücerred: baz fiilin kendisi'),
    "fe''ale": ('II', "tef'îl: çoklama, yoğunlaştırma, geçişli kılma"),
    'fâale': ('III', 'müfâale: karşılıklılık, birine yönelme, çaba'),
    "af'ale": ('IV', "if'âl: geçişli kılma, bir hâle sokma"),
    "tefe''ale": ('V', "tefa''ul: tef'îlin kendiliğinden hâli, dönüşlülük, zamanla edinme"),
    'tefâale': ('VI', 'tefâul: karşılıklılık, yapar görünme'),
    "infe'ale": ('VII', 'infiâl: kendiliğinden oluş'),
    "ifte'ale": ('VIII', 'iftiâl: dönüşlülük, edinme'),
    "if'alle": ('IX', "if'ilâl: renk ve ayıp hâli"),
    "istef'ale": ('X', "istif'âl: talep etme, o hâle girmiş sayma, o hâle dönüşme"),
}

DAYANAK = {
    'kuran-fiil': "Kur'ân'da bu kökten fiil geçer (Quranic Arabic Corpus 'V' veya kelime kaydında zaman kipi)",
    'fiil-yok': "Ne Kur'ân'da ne Vikisözlük'te bu kökten fiil var",
    'isimden-fiil': "Lügatte fiil var, fakat Türkçe fiil isimden kurulmuş yahut Vikisözlük fiili isimden türemiş sayıyor",
    'lugat-fiil': "Kur'ân'da fiil yok; lügatte fiil var ve Vikisözlük masdar kaydı veya Türkçe fiil lügattan geliyor",
    'claude-hukmu': 'Elle verilmiş Türkçe fiil ve kök manası okunarak Claude hükmü; zayıf',
    'turkce-fiil-isimden': "Kur'ân'da fiil var; Türkçe fiil sapı isimden kurulmuş",
}

HARF = re.compile('[ً-ٰٟـ]')


def norm(s):
    s = HARF.sub('', s or '')
    for a in 'أإآٱ':
        s = s.replace(a, 'ا')
    return s.replace('ى', 'ي').replace('ئ', 'ي').replace('ؤ', 'و').replace('ء', '')


def korpus(d):
    kcs = d['sozlukler'].get('kuran_korpusu') or []
    if isinstance(kcs, dict):
        kcs = [kcs]
    t = collections.Counter()
    for kc in kcs:
        t.update(kc.get('tur', {}))
    return t


def kok_turu(d):
    s = d['sozlukler']
    kk = s.get('kaikki_vikisozluk') or []
    lv = any(e.get('p') == 'verb' for e in kk)
    t = korpus(d)
    fv = t.get('V', 0)
    fi = sum(v for k, v in t.items() if k != 'V')
    zk = sum(1 for w in d['kelimeler'] if w.get('zaman'))
    kay = (d.get('turkce_fiil') or {}).get('kaynak')
    yazi = [(e.get('t') or '') + (e.get('e') or '') for e in kk]
    den = any(e.get('p') == 'verb' and re.search('denominal|Denominative|denominative|From the noun', y) for e, y in zip(kk, yazi))
    vn = any(e.get('p') == 'noun' and re.search('verbal noun|masdar', y, re.I) for e, y in zip(kk, yazi))
    if d['kok'] in ISIM_ZORLA:
        tur, guven, day = 'isim', 'orta', ['claude-hukmu']
    elif fv > 0 or zk > 0:
        tur, guven, day = 'fiil', 'kesin', ['kuran-fiil'] + (['turkce-fiil-isimden'] if kay == 'ad' else [])
    elif not lv:
        tur, guven, day = 'isim', 'kesin', ['fiil-yok']
    elif den or kay == 'ad':
        tur, guven, day = 'isim', 'orta', ['isimden-fiil']
    elif vn or kay in ('fiil', 'kuran-fiil'):
        tur, guven, day = 'fiil', 'orta', ['lugat-fiil']
    else:
        tur, guven, day = ('isim' if d['kok'] in ISIM_ZAYIF else 'fiil'), 'zayıf', ['claude-hukmu']
    return {'tur': tur, 'guven': guven, 'dayanak': day, 'kuran': {'fiil': fv, 'isim': fi}, 'lugat_fiil': lv}


def baz_fiil(d, kt):
    if kt['tur'] != 'fiil':
        return None
    sap = (d.get('turkce_fiil') or {}).get('sap')
    b = KOK_BAZ.get(d['kok']) or SAP_BAZ.get(sap)
    if b is None:
        return {'ad': None, 'ayrim': sap, 'acilim': None, 'guven': 'yok', 'dayanak': 'haritada yok'}
    ad = BAZ[b][0]
    return {'ad': ad, 'ayrim': sap, 'acilim': '%s := %s(ayrım: %s)' % (d['kok'], ad, sap), 'guven': 'orta', 'dayanak': 'Türkçe fiil sapı ve kök manası okunarak Claude hükmü'}
