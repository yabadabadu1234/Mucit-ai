import re, json, subprocess, html, sys
SRC='/home/user/Mucit-ai/kuran_hikmetleri/kaynak/lugat/etimoloji/ولد.md'
raw=open(SRC,encoding='utf-8').read()
def clean(s): return re.sub(r'\*+','',s)
lines=raw.split('\n'); title=None; secs=[]; cur=None; buf=[]
def flush():
    global buf
    if buf and cur is not None:
        txt='\n'.join(buf).strip()
        if txt: cur['bloklar'].append(txt)
    buf=[]
for ln in lines:
    if ln.startswith('# '): title=clean(ln[2:].strip()); continue
    if ln.startswith('## '):
        flush(); cur={'baslik':ln[3:].strip(),'bloklar':[]}; secs.append(cur); continue
    if ln.strip()=='' : flush(); continue
    buf.append(ln)
flush()
def sent(t):
    t=' '.join(t.split())
    return [x for x in re.split(r'(?<=[.?!])\s+',t) if x]
tree={'baslik':title,'bolumler':[]}
for s in secs:
    B=[]
    for b in s['bloklar']:
        L=b.split('\n')
        if L[0].startswith('|'):
            rows=[[c.strip() for c in r.strip().strip('|').split('|')] for r in L if not re.match(r'^\|[\s\-|]+\|$',r)]
            B.append({'tur':'tablo','satirlar':[[clean(c) for c in r] for r in rows]})
        elif re.match(r'^\d+\.\s',L[0]):
            B.append({'tur':'liste','ogeler':[clean(re.sub(r'^\d+\.\s*','',x)) for x in L]})
        else:
            t=clean(' '.join(L)); lead=re.match(r'^([^:]{2,40}):\s',t)
            B.append({'tur':'para','cumleler':sent(t),'etiket':lead.group(1) if lead and raw.find('**'+lead.group(1)+':')>=0 else None})
    tree['bolumler'].append({'baslik':s['baslik'],'bloklar':B})
json.dump(tree,open('agac.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
# sadakat: metin birebir mi
def norm(x): return re.sub(r'\s+','',clean(x))
src=norm(raw.split('\n',1)[1]); got=''
for s in tree['bolumler']:
    got+='##'+s['baslik']
    for b in s['bloklar']:
        if b['tur']=='tablo': got+=''.join('|'+'|'.join(r)+'|' for r in b['satirlar'])
        elif b['tur']=='liste': got+=''.join(f'{i+1}.'+o for i,o in enumerate(b['ogeler']))
        else: got+=''.join(b['cumleler'])
src2=norm(re.sub(r'\n\|[\s\-|]+\|\n','\n',raw.split('\n',1)[1]))
print(len(src2),len(re.sub(r'\s+','',got)), 'bolum',len(tree['bolumler']), [ (s['baslik'],len(s['bloklar'])) for s in tree['bolumler']])
import difflib
g=re.sub(r'\s+','',got)
for op in difflib.SequenceMatcher(None,src2,g,autojunk=False).get_opcodes():
    if op[0]!='equal': print(op[0],repr(src2[op[1]:op[2]]),repr(g[op[3]:op[4]]))
