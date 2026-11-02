import re,sys,os,html
kok,cikti=sys.argv[1],sys.argv[2]
col=open(os.path.join(kok,'collections/anatomy-and-physiology-2e.collection.xml')).read()
col=col.replace('<md:title>','<col:title>').replace('</md:title>','</col:title>')
bab=0;sira=0;babad=''
def temiz(x):
    x=re.sub(r'<media[^>]*>.*?</media>','',x,flags=re.S)
    x=re.sub(r'<link [^>]*target-id="([^"]*)"[^>]*/>',r'[atıf:\1]',x)
    x=re.sub(r'<link [^>]*url="([^"]*)"[^>]*>(.*?)</link>',r'\2 <\1>',x,flags=re.S)
    x=re.sub(r'<link [^>]*/>','[atıf]',x)
    x=re.sub(r'<term[^>]*>(.*?)</term>',r'**\1**',x,flags=re.S)
    x=re.sub(r'<emphasis effect="italics">(.*?)</emphasis>',r'_\1_',x,flags=re.S)
    x=re.sub(r'<emphasis[^>]*>(.*?)</emphasis>',r'**\1**',x,flags=re.S)
    x=re.sub(r'<sup>(.*?)</sup>',r'^\1^',x,flags=re.S)
    x=re.sub(r'<sub>(.*?)</sub>',r'~\1~',x,flags=re.S)
    x=re.sub(r'<title>(.*?)</title>',r'\n\n### \1\n\n',x,flags=re.S)
    x=re.sub(r'<figure[^>]*id="([^"]*)"[^>]*>',r'\n\n[ŞEKİL \1]\n',x)
    x=re.sub(r'<caption>',r'\nŞekil yazısı: ',x)
    x=re.sub(r'<item[^>]*>',r'\n- ',x)
    x=re.sub(r'<(para|section|note|exercise|problem|solution|list|table|row|entry|glossary|definition|meaning)[^>]*>',lambda m:{'row':'\n| ','entry':' ','exercise':'\n\n[SUAL]\n','solution':'\n[CEVAP] ','definition':'\n- ','meaning':': '}.get(m.group(1),'\n\n'),x)
    x=re.sub(r'</entry>',' |',x)
    x=re.sub(r'<[^>]+>','',x)
    x=html.unescape(x)
    x=re.sub(r'[ \t]*\n[ \t]*','\n',x); x=re.sub(r'[ \t]+',' ',x); x=re.sub(r'\n{3,}','\n\n',x)
    return x.strip()
for m in re.finditer(r'<col:subcollection>|<col:title>(.*?)</col:title>|<col:module document="(m\d+)"',col):
    if m.group(1) is not None:
        babad=m.group(1); continue
    if m.group(2) is None: continue
    sira+=1
    d=open(os.path.join(kok,'modules',m.group(2),'index.cnxml')).read()
    t=re.search(r'<title>(.*?)</title>',d).group(1).strip()
    ab=re.search(r'<md:abstract>(.*?)</md:abstract>',d,re.S)
    c=re.search(r"<content[^>]*>(.*)</content>",d,re.S).group(1)
    g=re.search(r'<glossary>(.*)</glossary>',d,re.S)
    metin='# %s\n\n(Kısım: %s; modül %s)\n\n'%(t,babad,m.group(2))
    if ab: metin+='[HEDEFLER]\n'+temiz(ab.group(1))+'\n\n'
    metin+=temiz(c)
    if g: metin+='\n\n[LÜGATÇE]\n'+temiz(g.group(1))
    open(os.path.join(cikti,'%03d_%s.txt'%(sira,m.group(2))),'w').write(metin+'\n')
print(sira)
