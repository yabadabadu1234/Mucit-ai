import re,sys
lines=open(sys.argv[1],encoding='utf-8').read().replace('\f','').split('\n')
start=[i for i,l in enumerate(lines) if l.startswith('00-XX ')][0]
code=re.compile(r'^(\d\d(?:-XX|-\d\d|[A-Z]xx|[A-Z]\d\d))\s+(.*)$')
ents=[];bad=[]
for l in lines[start:]:
    if not l.strip(): continue
    if re.fullmatch(r'\s*\d+\s*',l): continue
    m=code.match(l.strip())
    if m: ents.append([m.group(1),m.group(2).strip()])
    else:
        ents[-1][1]+=' '+l.strip()
with open(sys.argv[2],'w',encoding='utf-8') as f:
    for c,t in ents:
        t=re.sub(r'\s+',' ',t).replace('– ','–')
        keep={'and','or','dimensional','theoretic','dependent','boundary','fluid'}
        t=re.sub(r'(\S+)- ([a-z][a-z]*)',lambda m: (m.group(1)+'- '+m.group(2) if m.group(2) in ('and','or') else m.group(1)+'-'+m.group(2)) if m.group(2) in keep else m.group(1)+m.group(2),t)
        t=re.sub(r'(\S)- (and|or) ',r'\1- \2 ',t)
        f.write(c+'\t'+t+'\n')
print(len(ents),'bad',len(bad)); print('\n'.join(bad[:40]))
