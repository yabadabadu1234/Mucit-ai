import json, html, textwrap, subprocess, sys, math
from veri_d import K as T
W=int(sys.argv[1]) if len(sys.argv)>1 else 26
NC=int(sys.argv[2]) if len(sys.argv)>2 else 4
SK=json.loads(sys.argv[3]) if len(sys.argv)>3 else [1]*8
def lab(t,w=W,fs=11,color='#1b232a'):
    L=textwrap.wrap(t,width=w,break_long_words=False) or [t]
    return '<<FONT FACE="DejaVu Sans" POINT-SIZE="%d" COLOR="%s">%s<BR ALIGN="LEFT"/></FONT>>'%(fs,color,'<BR ALIGN="LEFT"/>'.join(html.escape(x) for x in L))
def lab2(ad,mana,w=W,fs=10):
    L=textwrap.wrap(mana,width=w,break_long_words=False)
    return '<<FONT FACE="DejaVu Sans" POINT-SIZE="%d" COLOR="#1b232a"><B>%s</B><BR ALIGN="LEFT"/>%s<BR ALIGN="LEFT"/></FONT>>'%(fs,html.escape(ad),'<BR ALIGN="LEFT"/>'.join(html.escape(x) for x in L))
def tab(rows):
    h='<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="3" COLOR="#7a7360">'
    for ri,r in enumerate(rows):
        h+='<TR>'+''.join('<TD BGCOLOR="%s" ALIGN="LEFT"><FONT FACE="DejaVu Sans" POINT-SIZE="10" COLOR="#1b232a">%s%s%s</FONT></TD>'%("#d9cfae" if ri==0 else "#f7f3e8","<B>" if ri==0 else "",html.escape(c),"</B>" if ri==0 else "") for c in r)+'</TR>'
    return h+'</TABLE>>'
# düğümler
nodes=[]  # {id,label,fill,kind}
def addn(label,fill,kind='cumle',text=None): 
    nodes.append({'id':len(nodes)+1,'label':label,'fill':fill,'kind':kind,'text':text}); return len(nodes)
S=[]
for sc in T['bolumler']:
    bl=[]
    for b in sc['bloklar']:
        ids=[addn(lab2(a,m),'#f7f3e8:#e4dcc6',text=a+' — '+m) for a,m in b['ogeler']]
        bl.append({'etiket':b['etiket'],'ids':ids,'ok':b['ok']})
    S.append({'baslik':sc['baslik'],'bloklar':bl})
# ölçüm
m=['digraph M{node [shape=box style=filled margin="0.045,0.025" fontname="DejaVu Sans"];']
for n in nodes:
    m.append('n%d [label=%s%s];'%(n['id'],n['label'],' shape=plain style=""' if n['kind']=='tablo' else ''))
m.append('}'); open('olc.dot','w',encoding='utf-8').write('\n'.join(m))
J=json.loads(subprocess.check_output(['dot','-Tjson0','olc.dot']))
size={}
for o in J['objects']:
    size[int(o['name'][1:])]=(float(o['width'])*72,float(o['height'])*72)
import os
GAP,PAD,LBL=[float(x) for x in os.environ.get('GPL','5,5,14').split(',')]
def stack(ids):  # dikey yığın
    w=max(size[i][0] for i in ids); h=sum(size[i][1] for i in ids)+GAP*(len(ids)-1); return w,h
# blok boyutları
for s in S:
    for b in s['bloklar']:
        w,h=stack(b['ids']); top=LBL if b['etiket'] else 0
        b['w']=w+2*PAD; b['h']=h+2*PAD+top; b['top']=top
k_of=lambda si:SK[si]
for si,s in enumerate(S):
    k=k_of(si); cols=[[] for _ in range(k)]; hs=[0]*k
    for b in s['bloklar']:
        j=hs.index(min(hs)); cols[j].append(b); hs[j]+=b['h']+GAP
    s['cols']=cols
    s['w']=sum(max(b['w'] for b in c) for c in cols if c)+GAP*(k-1)+2*PAD
    s['h']=max(sum(b['h'] for b in c)+GAP*(len(c)-1) for c in cols if c)+2*PAD+LBL+6
# bölümleri kolonlara dağıt (okuma sırası korunur)
tot=sum(s['h'] for s in S); target=tot/NC
cols=[[]];acc=0
for s in S:
    if acc>=target*0.92 and len(cols)<NC: cols.append([]);acc=0
    cols[-1].append(s);acc+=s['h']+GAP
colw=[max(s['w'] for s in c) for c in cols]
colh=[sum(s['h'] for s in c)+GAP*(len(c)-1) for c in cols]
RW=sum(colw)+GAP*(len(cols)-1)+2*PAD; RH=max(colh)+2*PAD+30
# koordinatlar (y yukarı artar; üstten aşağı çiz)
pos={}; boxes=[]  # (kind,x0,y0,x1,y1,label,depth)
boxes.append(('kok',0,0,RW,RH,T['baslik'],0)); boxcol=[-1]; nodecol={}
x=PAD
for ci,c in enumerate(cols):
    y=RH-PAD-30
    for s in c:
        sx0,sy1=x,y; sx1=x+colw[ci]; sy0=y-s['h']
        boxes.append(('bolum',sx0,sy0,sx1,sy1,s['baslik'],1)); boxcol.append(ci)
        bx=sx0+PAD
        for bc in s['cols']:
            if not bc: continue
            cw=max(b['w'] for b in bc); by=sy1-PAD-LBL-6
            for b in bc:
                b0=(bx,by-b['h'],bx+cw,by)
                boxes.append(('blok',b0[0],b0[1],b0[2],b0[3],b['etiket'] or '',2)); boxcol.append(ci)
                ny=by-PAD-b['top']
                for i in b['ids']:
                    w_,h_=size[i]; cx=bx+cw/2
                    pos[i]=(cx,ny-h_/2,w_,h_); nodecol[i]=ci; ny-=h_+GAP
                by-=b['h']+GAP
            bx+=cw+GAP
        y-=s['h']+GAP
    x+=colw[ci]+GAP
TOP=RH-PAD-30; maxh=max(colh)
for ci in range(len(cols)):
    f=maxh/colh[ci] if colh[ci]>0 else 1
    if f<=1.0001: continue
    for bi,b_ in enumerate(boxes):
        if boxcol[bi]==ci:
            k_,x0,y0,x1,y1,lb,dep=b_; boxes[bi]=(k_,x0,TOP-(TOP-y0)*f,x1,TOP-(TOP-y1)*f,lb,dep)
    for i in list(pos):
        if nodecol[i]==ci:
            cx,cy,w_,h_=pos[i]; pos[i]=(cx,TOP-(TOP-cy)*f,w_,h_)
json.dump({'W':RW,'H':RH,'boxes':boxes,'nodes':[{'id':n['id'],'text':n['text'],'kind':n['kind'],'x':pos[n['id']][0],'y':pos[n['id']][1],'w':pos[n['id']][2],'h':pos[n['id']][3]} for n in nodes],
 'zincir':[b['ids'] for s in S for b in s['bloklar'] if b['ok']],'rows':{str(b['ids'][0]):b['rows'] for s in S for b in s['bloklar'] if 'rows' in b}},open('yerlesim.json','w',encoding='utf-8'),ensure_ascii=False)
# neato -n2 çıktısı
def cl(t,fs,color): return '<<FONT FACE="DejaVu Sans" POINT-SIZE="%d" COLOR="%s"><B>%s</B></FONT>>'%(fs,color,html.escape(t))
FILL=[('#16222b:#1e3140','#4d6b80',17,'#e8b04a',1.6),('#2c4a5e:#355a72','#7fa3ba',14,'#ffffff',1.2),('#456f89:#4f7d99','#a9c4d4',10,'#ffffff',1.0)]
d=['digraph G {','graph [splines=line bgcolor="#0e151b" pad=0];','edge [color="#e8b04a" arrowsize=0.6 penwidth=1.3];']
for i,(kd,x0,y0,x1,y1,lb,dep) in enumerate(boxes):
    f,c,fs,fc,pw=FILL[dep]
    d.append('b%d [shape=box style="rounded,filled" fixedsize=true fillcolor="%s" gradientangle=270 color="%s" penwidth=%s width=%.4f height=%.4f pos="%.2f,%.2f!" labelloc=t label=%s];'%(i,f,c,pw,(x1-x0)/72,(y1-y0)/72,(x0+x1)/2,(y0+y1)/2,cl(lb,fs,fc) if lb else '""'))
for n in nodes:
    cx,cy,w_,h_=pos[n['id']]
    if n['kind']=='tablo': d.append('n%d [shape=plain style="" label=%s pos="%.2f,%.2f!"];'%(n['id'],n['label'],cx,cy))
    else: d.append('n%d [shape=box style="filled,rounded" fixedsize=true fillcolor="%s" gradientangle=270 color="#0b1218" penwidth=1.2 width=%.4f height=%.4f margin="0.045,0.025" fontname="DejaVu Sans" label=%s pos="%.2f,%.2f!"];'%(n['id'],n['fill'],w_/72,h_/72,n['label'],cx,cy))
for s in S:
    for b in s['bloklar']:
        if b['ok']:
            for a,c in zip(b['ids'],b['ids'][1:]): d.append('n%d -> n%d;'%(a,c))
d.append('}'); open('veled_n2.dot','w',encoding='utf-8').write('\n'.join(d))
cont=sum(s_['h']*s_['w'] for s_ in S); print('kök',round(RW),round(RH),round(RW/RH,2),'kolon',[len(c) for c in cols],'dolu',round(cont/(RW*RH),2))
