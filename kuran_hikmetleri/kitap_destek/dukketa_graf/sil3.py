import html,textwrap
C={'hakîkî':'#7fd1a0','mecâz':'#e6b85c','örfî':'#e07a7a'}
H,M,O='hakîkî','mecâz','örfî'
G=[
('MÜCERRED · salt iş',[
 ('dekk ●','دَكّ masdar',[(H,'ezip düzleme işi'),(M,'düz ve sıkı yer'),(M,'doldurulmuş tümsek, höyük')]),
 ('dekke ●','دَكَّة merre/isim',[(H,'tek ezişlik darbe'),(O,'seki, oturak'),(O,'tezgâh ○'),(O,'ezen şey → ezme aleti ○')]),
 ('dâkk ○','دَاكّ fâil',[(H,'ezen')]),
 ('medkûk ○','مَدْكُوك mef‘ûl',[(H,'ezilmiş')]),
 ('dekkâk · dekûk ○','دَكَّاك مبالغة',[(H,'çok ezen')]),
 ('edekk ○','أَدَكّ tafdîl',[(H,'daha çok ezen, daha düz')]),
 ('dekkâ’ ●','دَكَّاء müennes sıfat',[(H,'dümdüz (yer)')]),
 ('midekk ○','مِدَكّ âlet',[(O,'ezme aleti')]),
 ('medekk ○','مَدَكّ mekân-zaman',[(H,'ezme yeri, zamanı')]),
 ('dukayk ○','دُكَيْك tasğîr',[(H,'küçük ezik')]),
 ('dekkî ○','دَكِّيّ mensûb',[(H,'ezmeye, düzlüğe ait')]),
 ('dukûk · dikâk ●','دُكُوك دِكَاك cem‘',[(H,'düzlükler')]),
 ('dukkân ○','دُكَّان',[(O,'satış yeri, dükkân')]),
 ('dek (Türkçe) ●','',[(O,'hile, oyun')]),
]),
('MEÇHUL · fâil gizli',[
 ('dukke ●','دُكَّ masdar sayılan',[(H,'ezilmek ○'),(M,'hastalıkla çökmek ●')]),
]),
('TEF‘ÎL · çokluk, ezdirme',[
 ('tedkîk ○','تَدْكِيك masdar',[(H,'defalarca ezme, ezdirme')]),
 ('mudekkik ○','مُدَكِّك fâil',[(H,'çok ezen, ezdiren')]),
 ('mudekkak ○','مُدَكَّك mef‘ûl',[(H,'çokça ezilmiş')]),
]),
('MUFÂALE · karşılıklı',[
 ('mudâkka · dikâk ○','مُدَاكَّة دِكَاك masdar',[(H,'ezişmek')]),
 ('mudâkk ○','مُدَاكّ fâil',[(H,'karşılıklı ezen')]),
]),
('İF‘ÂL · ezdirme',[
 ('idkâk ○','إِدْكَاك masdar',[(H,'ezdirmek, ezilmesine sebep olmak')]),
 ('mudikk ○','مُدِكّ fâil',[(H,'ezdiren')]),
 ('mudakk ○','مُدَكّ mef‘ûl',[(H,'ezdirilmiş')]),
]),
('TEFA‘‘UL · kendini, tekellüf',[
 ('tedekkuk ○','تَدَكُّك masdar',[(H,'ezile ezile bir hâle gelmek')]),
 ('mütedekkik ○','مُتَدَكِّك fâil',[(H,'ezile ezile bir hâle gelen')]),
]),
('TEFÂ‘UL · çoklu karşılıklı',[
 ('tedâkk ○','تَدَاكّ masdar',[(H,'birbirine çarpıp ezişmek')]),
 ('mütedâkk ○','مُتَدَاكّ fâil',[(H,'birbirini ezişen')]),
]),
('İNFİ‘ÂL · kendiliğinden',[
 ('indikâk ○','اِنْدِكَاك masdar',[(H,'kendiliğinden ezilmek, çökmek')]),
 ('mündekk ●','مُنْدَكّ fâil',[(H,'düzleşmiş, çökmüş')]),
]),
('İFTİ‘ÂL · kendi hâlinde',[
 ('iddikâk ○','اِدِّكَاك masdar',[(H,'ezilip düzlenmek')]),
 ('muddekk ○','مُدَّكّ fâil',[(H,'ezilip düzlenen')]),
]),
('İSTİF‘ÂL · talep',[
 ('istidkâk ○','اِسْتِدْكَاك masdar',[(H,'ezilmesini istemek')]),
 ('mustedikk ○','مُسْتَدِكّ fâil',[(H,'ezilmesini isteyen')]),
]),
('RUBÂ‘Î · tekrar, şiddet',[
 ('dekdeke ●','دَكْدَكَة masdar',[(H,'sarsıp sarsıp ezmek'),(M,'yeri titretmek, sancım ●')]),
 ('dikdâk ○','دِكْدَاك masdar',[(H,'sarsıp sarsıp ezmek')]),
 ('mudekdik ○','مُدَكْدِك fâil',[(H,'sarsıp ezen')]),
 ('mudekdak ○','مُدَكْدَك mef‘ûl',[(H,'sarsılıp ezilmiş')]),
]),
('TEFA‘LUL · rubâ‘înin mutâvaası',[
 ('tedekdük ○','تَدَكْدُك masdar',[(H,'darbeyle dökülüp çökmek')]),
 ('mütedekdik ○','مُتَدَكْدِك fâil',[(H,'dökülüp çöken')]),
]),
]
d=['digraph G{rankdir=LR;bgcolor="#0f1720";nodesep=0.1;ranksep=0.4;node[shape=box style="rounded,filled" fontname="DejaVu Sans" color="#7a7360" margin="0.06,0.03" fillcolor="#e4dcc6"];edge[arrowsize=0.5 penwidth=1.4 fontname="DejaVu Sans" fontsize=8];']
def lab(a,b=''):
    t='<FONT POINT-SIZE="11"><B>%s</B></FONT>'%html.escape(a)
    if b: t+='<BR/><FONT POINT-SIZE="9">%s</FONT>'%html.escape(b)
    return '<%s>'%t
d.append('r [label=%s fillcolor="#f2d98a"];'%lab('د ك ك','ezip düzlemek'))
n=0
for gi,(g,L) in enumerate(G):
    d.append('g%d [label=%s fillcolor="#9fc5e8"];'%(gi,lab(g)));d.append('r->g%d [color="#d9a441"];'%gi)
    for f,ar,Ms in L:
        n+=1;fid='f%d'%n
        d.append('%s [label=%s];'%(fid,lab(f,ar)));d.append('g%d->%s [color="#d9a441"];'%(gi,fid))
        for t,m in Ms:
            n+=1;mid='m%d'%n
            d.append('%s [label=%s fillcolor="#f7f3e8"];'%(mid,lab(m)));d.append('%s->%s [label=<<FONT COLOR="%s">%s</FONT>> color="%s"];'%(fid,mid,C[t],t,C[t]))
d.append('}')
open('sil3.dot','w',encoding='utf-8').write('\n'.join(d))
