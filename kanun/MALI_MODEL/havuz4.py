import csv
D='veri_ilo/'
B=['AGE_10YRBANDS_Y15-24','AGE_10YRBANDS_Y25-34','AGE_10YRBANDS_Y35-44','AGE_10YRBANDS_Y45-54','AGE_10YRBANDS_Y55-64','AGE_10YRBANDS_YGE65']
AD=['15-24','25-34','35-44','45-54','55-64','65+']
def oku(f,sex):
    o={}
    for r in csv.DictReader(open(D+f,encoding='utf-8-sig')):
        if r['time']=='2025' and r['sex']==sex and r['classif1'] in B: o[r['classif1']]=float(r['obs_value'])
    return [o[b] for b in B]
D15={'SEX_M':1239.0*0.512,'SEX_F':1239.0*0.488}
NAG={'SEX_M':3088.424/5173.606,'SEX_F':1681.936/3486.215}
MEMUR=3715.638
UCRETLI_OZEL=8359/0.467
M2=0.127
def tablo():
    R={}
    for sx in ('SEX_M','SEX_F'):
        P,E,M,U,N=[oku(f,sx) for f in ['POP.csv','EAP.csv','EMP.csv','UNE.csv','NIFL.csv']]
        R[sx]=(P,E,M,U,N)
    formal={sx:[R[sx][2][i]-R[sx][4][i] for i in range(6)] for sx in R}
    ftot=sum(sum(v) for v in formal.values())
    f2564=sum(formal[sx][i] for sx in formal for i in range(1,5))
    S=[]
    for i,a in enumerate(AD):
        for sx in ('SEX_M','SEX_F'):
            P,E,M,U,N=R[sx]
            dis=P[i]-E[i]-(D15[sx] if i==0 else 0)
            memur=MEMUR*formal[sx][i]/f2564 if 1<=i<=4 else 0.0
            ozel_mem=M2*UCRETLI_OZEL*(formal[sx][i]-memur)/(ftot-MEMUR)
            kd=N[i]*NAG[sx]
            ilgili=0 if a=='65+' else dis
            havuz=U[i]+kd+(formal[sx][i]-memur-ozel_mem)+ilgili
            S.append((a,sx[-1],dis,U[i],kd,formal[sx][i],memur,ozel_mem,havuz))
    return S
if __name__=="__main__":
    S=tablo()
    print("yas  cins isgdisi issiz kd_tarimdisi formal memur ozel_memnun havuz")
    for s in S: print("%-5s %s %7.0f %6.0f %7.0f %7.0f %6.0f %6.0f %8.0f"%s)
    print("TOPLAM %.0f; 16-34 %.0f; kadin %.0f; erkek %.0f"%(sum(s[-1] for s in S),sum(s[-1] for s in S[:4]),sum(s[-1] for s in S if s[1]=='F'),sum(s[-1] for s in S if s[1]=='M')))
