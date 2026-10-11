import csv
D='veri_ilo/'
B=['AGE_10YRBANDS_Y15-24','AGE_10YRBANDS_Y25-34','AGE_10YRBANDS_Y35-44','AGE_10YRBANDS_Y45-54','AGE_10YRBANDS_Y55-64','AGE_10YRBANDS_YGE65']
AD=['15-24','25-34','35-44','45-54','55-64','65+']
def oku(f):
    o={}
    for r in csv.DictReader(open(D+f,encoding='utf-8-sig')):
        if r['time']=='2025' and r['sex']=='SEX_T' and r['classif1'] in B: o[r['classif1']]=float(r['obs_value'])
    return [o[b] for b in B]
POP,EAP,EMP,UNE,NIF=[oku(f) for f in ['POP.csv','EAP.csv','EMP.csv','UNE.csv','NIFL.csv']]
D15=1239.0  # bin: 2010 dogumlari (ozet kaydi); 15 yasindakiler, hepsi isgucu disi varsayildi
def huni(m,yas65_dahil=False):
    S=[]
    for i,a in enumerate(AD):
        pop=POP[i]-(D15 if i==0 else 0); eap=EAP[i]; emp=EMP[i]; une=UNE[i]; nif=NIF[i]
        dis=POP[i]-eap-(D15 if i==0 else 0); formal=emp-nif
        gelirsiz=dis+une; kd=nif
        memnun=m*formal; kalan_formal=formal-memnun
        havuz=gelirsiz+kd+kalan_formal
        if a=='65+' and not yas65_dahil: havuz=une+kd+kalan_formal  # emekli varsayimi: is gucu disi 65+ havuza girmez
        S.append(dict(yas=a,nufus16=pop,emp=emp,formal=formal,kayitdisi=nif,issiz=une,isgucu_disi=dis,gelirsiz=gelirsiz,memnun_dus=memnun,havuz=havuz,havuz_memnun_dusulmeden=gelirsiz+kd+formal if a!='65+' else une+kd+formal))
    return S
if __name__=="__main__":
    for m in (1.0,0.7,0.5):
        S=huni(m); print("\nm=%.1f (memnun formal payi)"%m)
        print("yas   nufus16   formal  kayitdisi issiz  isgdisi gelirsiz havuz")
        for s in S: print("%-5s %8.0f %8.0f %8.0f %7.0f %8.0f %8.0f %8.0f"%(s['yas'],s['nufus16'],s['formal'],s['kayitdisi'],s['issiz'],s['isgucu_disi'],s['gelirsiz'],s['havuz']))
        print("TOPLAM havuz %.0f bin; 16-34: %.0f bin"%(sum(s['havuz'] for s in S),sum(s['havuz'] for s in S[:2])))
    print("\nkayit disi orani (kayitdisi/emp):",["%s %.1f%%"%(AD[i],100*NIF[i]/EMP[i]) for i in range(6)])
    print("NEET 15-24: 2684.3 bin; 15-24 isgucu disi:",POP[0]-EAP[0])
