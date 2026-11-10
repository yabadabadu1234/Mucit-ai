import html,textwrap
C={'hakîkî':'#7fd1a0','mecâz':'#e6b85c','örfî':'#e07a7a','?':'#9aa7b4'}
FORM=[ # grup, [(biçim, ad_ar, [(tür, mana)])]
('FİİL',[
 ('dekke','دَكَّ · mâzî',[('hakîkî','ezdi, yerle bir etti')]),
 ('yedukku','يَدُكُّ · muzâri‘',[('hakîkî','eziyor, ezer')]),
 ('dukke','دُكَّ · meçhul',[('hakîkî','ezildi (fâil gizli)'),('mecâz','hastalıkla çöktü')]),
 ('indekke ○','اِنْدَكَّ · inf‘âl',[('hakîkî','kendiliğinden çöktü')]),
 ('dekdeke','دَكْدَكَ · rubâ‘î',[('hakîkî','sarsıp sarsıp ezdi'),('mecâz','yeri titretti')]),
 ('tedekdeke ○','تَدَكْدَكَ',[('hakîkî','darbeyle döküldü, çöktü')]),
]),
('İSİM',[
 ('dekk','دَكّ · masdar',[('hakîkî','ezip düzleme işi'),('mecâz','düz ve sıkı yer'),('mecâz','doldurulmuş tümsek, höyük')]),
 ('dekke','دَكَّة · merre',[('hakîkî','tek ezişlik darbe'),('örfî','seki, oturak'),('örfî','tezgâh'),('örfî','ezen şey → ezme aleti ○')]),
 ('dekkâ’','دَكَّاء · sıfat',[('hakîkî','dümdüz (yer)')]),
 ('mündekk','مُنْدَكّ · fâil',[('hakîkî','düzleşmiş, çökmüş')]),
 ('medkûk ○','مَدْكُوك · mef‘ûl',[('hakîkî','ezilmiş')]),
 ('dukûk · dikâk','دُكُوك · cem‘',[('hakîkî','düzlükler')]),
 ('dukkân ○','دُكَّان · mekân',[('örfî','satış yeri, dükkân')]),
 ('dek (Türkçe)','',[('örfî','hile, oyun (hokkabazlık)')]),
])]
d=['digraph G{rankdir=LR;bgcolor="#0f1720";nodesep=0.14;ranksep=0.5;node[shape=box style="rounded,filled" fontname="DejaVu Sans" color="#7a7360" margin="0.08,0.04" fillcolor="#e4dcc6"];edge[arrowsize=0.6 penwidth=1.6 fontname="DejaVu Sans" fontsize=9];']
def lab(a,b=''):
    t='<FONT POINT-SIZE="12"><B>%s</B></FONT>'%html.escape(a)
    if b: t+='<BR/><FONT POINT-SIZE="9">%s</FONT>'%html.escape(b)
    return '<%s>'%t
d.append('r [label=%s fillcolor="#f2d98a"];'%lab('د ك ك','ezip düzlemek'))
n=0
for g,L in FORM:
    d.append('g%s [label=%s fillcolor="#9fc5e8"];'%(g,lab(g)))
    d.append('r->g%s [color="#d9a441"];'%g)
    for f,ar,M in L:
        n+=1; fid='f%d'%n
        d.append('%s [label=%s];'%(fid,lab(f,ar)))
        d.append('g%s->%s [color="#d9a441"];'%(g,fid))
        for t,m in M:
            n+=1; mid='m%d'%n
            d.append('%s [label=%s fillcolor="#f7f3e8"];'%(mid,lab(m)))
            d.append('%s->%s [label=<<FONT COLOR="%s">%s</FONT>> color="%s"];'%(fid,mid,C[t],t,C[t]))
d.append('}')
open('sil2.dot','w',encoding='utf-8').write('\n'.join(d))
