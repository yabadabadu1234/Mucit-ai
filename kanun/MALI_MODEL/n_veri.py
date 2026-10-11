import csv, json, math
B={}
for r in csv.DictReader(open('veri_ilo/UNE.csv',encoding='utf-8-sig')):
    if r['sex']=='SEX_T' and r['classif1'].startswith('AGE_5YRBANDS_Y') and 'YGE15' not in r['classif1']:
        B[r['classif1'].split('_Y')[1]]=float(r['obs_value'])
def yas(a,b):
    t=0.0
    for k,v in B.items():
        lo,hi=(int(k[2:]),99) if k.startswith('GE') else map(int,k.split('-'))
        t+=v*max(0,min(hi,b-1)-max(lo,a)+1)/(hi-lo+1)
    return t
res_2230=yas(22,31); res_3040=yas(31,40)
isgdisi_2534=3013+581; kd_2534=461+450
isgdisi_3544=3128+455; kd_3544=437+380
gay_2230=0.9*(isgdisi_2534+0.0)+0.9*(437+225)
gay_3040=isgdisi_3544+(437+380)
iyi=0.60*res_2230+0.20*gay_2230+0.30*res_3040+0.10*gay_3040
kotu=100.0
orta=math.sqrt(kotu*iyi)
print("resmi 22-30 %.1f  31-39 %.1f ; gayriresmi 22-30 %.0f 30-40 %.0f"%(res_2230,res_3040,gay_2230,gay_3040))
print("iyi %.0f bin  orta %.0f bin  kotu %.0f bin"%(iyi,orta,kotu))
q=0.3
for p in (0.02,0.05,0.15,0.40):
    F=0;out=[]
    for t in range(5):
        for _ in range(12): F+=(p+q*F)*(1-F)/12
        out.append(round(F,3))
    print(p,out)
json.dump(dict(iyi=iyi*1000,orta=orta*1000,kotu=kotu*1000),open('n_veri.json','w'))
