import itertools, subprocess
A={'ölçüp biçmek':'a','yoktan var etmek':'b','düzleştirmek':'c','eskimek':'d','huy, tabiat':'e','uydurmak':'f','pay, nasip':'g','yapan':'h','yapılan':'i'}
O={
 'خَلَقَ yarattı':'ab',
 'خالِق yaratıcı':'abh',
 'مَخْلُوق yaratılmış':'abi',
 'خَلْق yaratma':'ab',
 'خُلُق huy':'ae',
 'خَلْقاء düz kaya':'c',
 'خَلَق eski':'cd',
 'مُخَلَّق düzlenmiş':'ci',
 'اِخْتِلاق uydurma':'bf',
 'خَلاق nasip':'ag',
 'خَلِيق lâyık':'ei'}
inv={v:k for k,v in A.items()}
objs=list(O)
def ext(S): return frozenset(o for o in objs if set(S)<=set(O[o]))
def intent(E):
    s=set('abcdefghi')
    for o in E: s&=set(O[o])
    return frozenset(s)
C={}
for r in range(0,len(A)+1):
    for S in itertools.combinations('abcdefghi',r):
        e=ext(S); i=intent(e); C[i]=e
nodes=list(C)
def lt(x,y): return C[x]<C[y]  # x altında y
edges=[]
for x in nodes:
    for y in nodes:
        if C[x]<C[y] and not any(C[x]<C[z]<C[y] for z in nodes): edges.append((x,y))
# indirgenmiş etiket
own_attr={n:set(n)-set().union(*[set(m) for m in nodes if C[m]>C[n]]) if any(C[m]>C[n] for m in nodes) else set(n) for n in nodes}
own_obj={n:[o for o in C[n] if not any(o in C[m] for m in nodes if C[m]<C[n])] for n in nodes}
print(len(nodes),'kavram',len(edges),'kenar')
L=['digraph G{rankdir=BT;nodesep=.35;ranksep=.55;bgcolor="white";node[shape=box,style="rounded,filled",fontname="Amiri",fontsize=14,margin="0.10,0.05"];edge[arrowhead=none,color="#8a7a55"];']
for n in nodes:
    a=' · '.join(inv[c] for c in sorted(own_attr[n]))
    ob='\\n'.join(own_obj[n])
    if not a and not ob: lab='';fill='#f4efe0';sz='width=.15,height=.15,shape=circle,label=""'
    else:
        lab=(f'<<B>{a}</B>>' if False else '')
    if not a and not ob: L.append(f'n{abs(hash(n))} [{sz},fillcolor="{fill}"];'); continue
    fill='#ffe9a8' if a and not ob else ('#d9ecff' if ob and not a else '#e8f5d8')
    txt=(a+('\\n' if a and ob else '')+ob).replace('"','')
    L.append(f'n{abs(hash(n))} [label="{txt}",fillcolor="{fill}"];')
for x,y in edges: L.append(f'n{abs(hash(x))} -> n{abs(hash(y))};')
L.append('}')
open('kafes.dot','w').write('\n'.join(L))
