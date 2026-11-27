import json,os,re,csv,collections,sys
K=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..')
sys.path.insert(0,os.path.join(K,'kitap_destek','turetme_motoru'))
import istikak as I
import mesmu as MS
KAYDET = '--yaz' in sys.argv
R=re.compile('[ً-ِْٰ]')
def f(x): return R.sub('',re.sub(r'\d+$','',x.strip())).replace('ـ','')
def okunur(o,g=0,en=110):
    ic='  '*(g+1);dis='  '*g
    if isinstance(o,dict):
        if not o: return '{}'
        return '{\n'+',\n'.join('%s%s: %s'%(ic,json.dumps(k,ensure_ascii=False),okunur(v,g+1,en)) for k,v in o.items())+'\n'+dis+'}'
    if isinstance(o,(list,tuple)):
        if not o: return '[]'
        if all(not isinstance(x,(dict,list,tuple)) for x in o):
            s='['+', '.join(json.dumps(x,ensure_ascii=False) for x in o)+']'
            if len(s)<=en: return s
        return '[\n'+',\n'.join(ic+okunur(x,g+1,en) for x in o)+'\n'+dis+']'
    return json.dumps(o,ensure_ascii=False)
yol={}
for ad in ('kuranda_var','kuranda_yok'):
    d=os.path.join(K,'kelime_kaydi',ad,'kokler')
    for fn in os.listdir(d): yol[fn[:-5]]=os.path.join(d,fn)
mus=collections.defaultdict(set)
for k in sorted(yol):
    j=json.load(open(yol[k],encoding='utf-8'))
    for v in MS.mustak_tam(j).values():
        for r in v: mus[f(r[2])].add(k)
kel=json.load(open(K+'/kaynak/sozluk/kelimeler.json',encoding='utf-8'))
kk={}
for x in kel:
    if x['kok']:
        kk[f(x['kelime'])]=I.normala(x['kok'])
        if x.get('lem'): kk[f(x['lem'])]=I.normala(x['lem'] and x['kok'])
ov={}
D=os.path.dirname(os.path.abspath(__file__))
for fn in sorted(os.listdir(D+'/cikti')):
    for x in json.load(open(D+'/cikti/'+fn,encoding='utf-8')):
        for w in x['kelimeler']: ov[(x['id'],w['kelime'])]=w
ont={r['conceptId']:r for r in csv.DictReader(open(K+'/kaynak/Concepts.csv',encoding='utf-8'))}
ust=collections.defaultdict(list)
for r in csv.DictReader(open(K+'/kaynak/Relations.csv',encoding='utf-8')):
    for alan,ad in (('subTypeOfID','alt_tur_of'),('partOfID','parca_of'),('instanceOfID','ornek_of')):
        v=r[alan]
        if v and v!='NULL': ust[r['concept_id']].append([ad,v])
kunye='Arabic Ontology, Birzeit University (SinaLab, Mustafa Jarrar), ücretsiz sürüm, çıkarım 09-06-2024; atıf: Jarrar 2021 Applied Ontology 16:1; Jarrar ve Amayreh 2019 NLDB'
yeni=collections.defaultdict(list);kelimeye=collections.defaultdict(list);yolsuz=0
for cid,c in ont.items():
    kayit={'id':cid,'arapca':[x.strip() for x in c['arabicSynset'].split('|') if x.strip()],
           'ingilizce':[x.strip() for x in c['englishSynset'].split('|') if x.strip() and x.strip()!='NULL'],
           'tanim':c['gloss'],'misal':(c['example'] if c['example']!='NULL' else ''),'veri_kaynagi':c['dataSourceId'],
           'ust':[[ad,v,(ont[v]['englishSynset'] if v in ont and ont[v]['englishSynset']!='NULL' else (ont[v]['arabicSynset'] if v in ont else ''))] for ad,v in ust.get(cid,[])],'kunye':kunye}
    yerler=set()
    for w in kayit['arapca']:
        a=f(w);s=None
        if a in kk: s={kk[a]}
        else:
            s=mus.get(a) or (mus.get(a[2:]) if a.startswith('ال') else None)
        if s and len(s)>1:
            o=ov[(cid,w)]
            s={o['kok']} if o['kok'] in s else None
        if s: yerler|={('k',x) for x in s if x in yol}
        else: yerler.add(('w',a))
    if not yerler: yerler.add(('w','concept_'+cid))
    for t,y in yerler:
        (yeni[y] if t=='k' else kelimeye[y]).append(kayit)
degisen=0
for k,p in yol.items():
    j=json.load(open(p,encoding='utf-8'))
    eski=[c['id'] for c in j.get('ontoloji',[])]
    yn=[c['id'] for c in yeni.get(k,[])]
    if eski!=yn:
        degisen+=1
        if KAYDET:
            mevcut={c['id']:c for c in j.get('ontoloji',[])}
            if yn:
                liste=[]
                for c in yeni[k]:
                    c={a:b for a,b in c.items() if a!='kunye'}
                    for a,b in mevcut.get(c['id'],{}).items():
                        if a.endswith('_tr'): c[a]=b
                    liste.append(c)
                j['ontoloji']=liste
            else: j.pop('ontoloji',None)
            open(p,'w',encoding='utf-8').write(okunur(j)+'\n')
print('değişen kök dosyası',degisen,'| köke bağlanan kavram yeri',sum(len(v) for v in yeni.values()))
