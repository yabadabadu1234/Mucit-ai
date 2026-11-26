import json,sys,re,pathlib
KOK=pathlib.Path('../../kelime_kaydi/kuranda_var/kokler')
d=json.load(open('KOK_ESAS_MANALARI.json',encoding='utf-8'))
hk=re.compile('[ً-ْٰ]'); out={}
for k,v in d.items():
    m=hk.sub('',v['mekayis_asil']); m=re.sub(r'^\([^)]*\)\s*','',m)
    m=re.sub(r'^(\S+ ){2,3}\S+\s*:?\s*','',m) if m else ''
    en=[x for x in v['ingilizce_etymarab'] if not re.search(r'[éèêàâçûôî]|^\.\.\.$',x) and x.isascii()]
    gor=' / '.join(en)[:170]
    t=json.load(open(KOK/f'{k}.json',encoding='utf-8')).get('etymarab') or {}
    s=re.search(r'Semantic value spectrum[^‘]*‘([^’]+)’',t.get('kok_maddesi',''))
    sp=[x.strip() for x in re.split(r';',s.group(1))] if s else []
    ek=[x for x in sp if x and x not in gor]
    mk=m[110:].strip()
    if ek or mk: out[k]=(mk,ek)
if len(sys.argv)>1:
    ks=list(out); a,b=int(sys.argv[1]),int(sys.argv[2])
    for k in ks[a:b]: print(f"{k}|{('M+:'+out[k][0]+'|') if out[k][0] else ''}{'; '.join(out[k][1])}")
else: print(len(out), sum(len(x[0])+len('; '.join(x[1])) for x in out.values()))
