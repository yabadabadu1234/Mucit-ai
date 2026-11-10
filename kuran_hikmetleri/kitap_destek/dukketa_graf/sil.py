import html,textwrap
def n(i,ad,m,fill='#e4dcc6'):
    m='<BR/>'.join(html.escape(x) for x in (textwrap.wrap(m,22) or ['']))
    return '%s [label=<<FONT FACE="DejaVu Sans" POINT-SIZE="13"><B>%s</B></FONT><BR/><FONT FACE="DejaVu Sans" POINT-SIZE="10">%s</FONT>> fillcolor="%s"];'%(i,html.escape(ad),m,fill)
H=[ # hat adı, [(ad,mana)]
('İŞ: fâil ezer',[('دَكَّ dekke','ezdi'),('يَدُكُّ yedukku','eziyor'),('دُكَّ dukke','ezildi (fâil gizli)'),('اِنْدَكَّ indekke','kendiliğinden çöktü')]),
('ŞİDDET VE SAYI',[('دَكَّة dekke','tek ezişte'),('دَكّ dekk','tam ezip (tekit)'),('دَكْدَكَ dekdeke','sarsıp sarsıp ezdi'),('تَدَكْدَكَ','darbeyle döküldü')]),
('SONUÇ: ezilen hâl',[('مُنْدَكّ mündekk','düzleşmiş'),('دَكَّاء dekkâ’','dümdüz'),('دَكّ dekk','düz ve sıkı yer'),('دُكُوك dukûk','düzlükler')]),
('BİRİKEN: doldurunca',[('دَكّ dekk','höyük, doldurulmuş tümsek'),('دَكَّة dekke','seki, oturak'),('دَكَان dukkân ○','tezgâh, dükkân')]),
('MECAZ VE İSİM ○',[('دُكَّ dukke','hastalıkla çöktü'),('مَدْكُوك ○','ezilmiş'),('dek (Türkçe)','hile; altüst edip oyun')]),
]
d=['digraph G{rankdir=TB;bgcolor="#0f1720";nodesep=0.25;ranksep=0.35;node[shape=box style="rounded,filled" fontname="DejaVu Sans" color="#7a7360" margin="0.08,0.05"];edge[color="#d9a441" arrowsize=0.7 fontname="DejaVu Sans" fontsize=9 fontcolor="#d9a441"];']
d.append(n('c','د ك ك — ÖZ ÇEKİRDEK','kabarığı vurup ezmek, düz ve sıkı kılmak','#f2d98a'))
k=0
for hi,(h,L) in enumerate(H):
    d.append('h%d [label="%s" shape=plaintext fontcolor="#e8dcb0" fontname="DejaVu Sans" fontsize=11 style=""];'%(hi,html.escape(h)))
    d.append('c->h%d;'%hi)
    prev='h%d'%hi
    for ad,m in L:
        k+=1; d.append(n('w%d'%k,ad,m)); d.append('%s->w%d;'%(prev,k)); prev='w%d'%k
d.append(n('u','HUDUT','dakk: inceltir · dekîk: tam · kasr: kırar · hedm: yıkar · dekk: kabarığı alıp düzler','#7fb3d5'))
d.append('w4->u [style=dashed];w8->u [style=dashed];w12->u [style=dashed];w15->u [style=dashed];w18->u [style=dashed];')
d.append('{rank=sink;u}')
for hi,(h,L) in enumerate(H): pass
d.append('}')
open('sil.dot','w',encoding='utf-8').write('\n'.join(d))
