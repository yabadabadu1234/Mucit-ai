import json,sys,re
d=json.load(open('KOK_ESAS_MANALARI.json',encoding='utf-8'))
ks=list(d); a,b=int(sys.argv[1]),int(sys.argv[2])
hk=re.compile('[ً-ْٰ]')
for k in ks[a:b]:
    v=d[k]; m=hk.sub('',v['mekayis_asil'])
    m=re.sub(r'^\([^)]*\)\s*','',m)
    m=re.sub(r'^(\S+ ){2,3}\S+\s*:?\s*','',m) if m else ''
    import re as R
    en=[x for x in v['ingilizce_etymarab'] if not R.search('[éèêàâçûôî]|^\.\.\.$', x) and x.isascii()]
    e=' / '.join(en)[:170]
    print(f"{k}|T:{'/'.join(v['turkce'])}|M:{m[:110]}|E:{e}")
