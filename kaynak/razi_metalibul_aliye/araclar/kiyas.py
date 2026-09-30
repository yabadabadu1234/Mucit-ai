import re,json,collections,sys
import os
S=os.environ.get('RAZI_OCR_DIZINI','ocr_gecici')+'/'   # OCR depoda DEĞİL: git geçmişinden (0102e86^) geçici olarak çıkarılır, depoya alınmaz (CLAUDE.md 25-E)
def norm(s):
    s=re.sub(r'[ً-ْـٰ]','',s)
    for a,b in (('أ','ا'),('إ','ا'),('آ','ا'),('ٱ','ا'),('ى','ي'),('ة','ه'),('ؤ','و'),('ئ','ي'),('ی','ي'),('ک','ك'),('ھ','ه')): s=s.replace(a,b)
    s=re.sub(r'[^ء-ي ]',' ',s)   # yalnız Arapça harfler
    return s.split()
def realpages(c):
    t=open('metin_sekka/cilt_0%d.txt'%c,encoding='utf-8').read()
    ms=list(re.finditer(r'(?m)^\[(\d+)\]',t)); R={}
    for i,x in enumerate(ms):
        e=ms[i+1].start() if i+1<len(ms) else len(t); R[int(x.group(1))]=collections.Counter(norm(t[x.end():e]))
    return R
def defterpages(c):
    d=open('okuma_defteri/cilt_0%d.md'%c,encoding='utf-8').read()
    return [int(m.group(1)) for m in re.finditer(r'(?m)^## c%d p(\d+)'%c,d)]
res={}
for c in range(1,10):
    O=json.load(open(S+'ocr/cilt_0%d.json'%c,encoding='utf-8')); R=realpages(c); out={}
    for p in defterpages(c):
        oc=collections.Counter(norm(O[p-1])) if p-1<len(O) else collections.Counter(); no=sum(oc.values())
        best=None
        for s in range(p-3,p+4):
            if s not in R: continue
            nr=sum(R[s].values()); ov=sum((oc&R[s]).values())
            rec=ov/nr if nr else 0; pre=ov/no if no else 0; f=2*rec*pre/(rec+pre) if rec+pre else 0
            if best is None or f>best[0]: best=(f,s,rec,pre,nr,no)
        out[p]=best
    res[c]=out
json.dump({c:{p:v for p,v in o.items()} for c,o in res.items()},open(S+'kiyas.json','w'))
for c,o in res.items():
    fs=[v[0] for v in o.values() if v]
    hist=collections.Counter(int(f*10) for f in fs)
    off=collections.Counter((v[1]-p) for p,v in o.items() if v)
    print('cilt',c,'sayfa',len(o),'ort F1 %.2f'%(sum(fs)/len(fs)),'histogram(onluk)',sorted(hist.items()),'kayma',dict(off))
