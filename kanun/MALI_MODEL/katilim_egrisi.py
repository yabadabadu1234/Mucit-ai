import csv
B={}
for r in csv.DictReader(open('veri_ilo/UNE.csv',encoding='utf-8-sig')):
    if r['sex']=='SEX_T' and r['classif1'].startswith('AGE_5YRBANDS_Y') and 'YGE15' not in r['classif1']:
        B[r['classif1'].split('_Y')[1]]=float(r['obs_value'])
def yas(a,b):
    t=0.0
    for k,v in B.items():
        if k.startswith('GE'):
            lo,hi=int(k[2:]),99
        else:
            lo,hi=map(int,k.split('-'))
        n=hi-lo+1
        ov=max(0,min(hi,b-1)-max(lo,a)+1)
        t+=v*ov/n
    return t
D=[('16-21',16,22,None),('22-29',22,30,0.60),('30-39',30,40,0.40),('40+',40,100,None)]
print('Resmi issiz (ILO 2025, bin), bant icinde tekduze varsayim')
tot=0
for ad,a,b,o in D:
    n=yas(a,b)
    print(ad,round(n,1),'' if o is None else f'oran {o:.2f} -> {n*o:.1f}')
    if o: tot+=n*o
print('22-39 padisah tahmini gecen (bin):',round(tot,1))
print('Haberdar olma duyarlilik: Bass p (ilan) q=0.3, ilk 3 yil kumulatif pay')
q=0.3
for p in (0.02,0.05,0.15,0.40):
    F=0;out=[]
    for t in range(3):
        for _ in range(12):
            F+= (p+q*F)*(1-F)/12
        out.append(round(F,2))
    print('p=',p,out)
