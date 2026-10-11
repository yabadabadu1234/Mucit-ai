import havuz as h
NAG=4770.36/8659.821
AILE=2463.66
AILE_TARIM_ORANI=2.6/3.1
M=0.181
def tablo(m=M,aile_tarim=True):
    S=[]
    for i,a in enumerate(h.AD):
        formal=h.EMP[i]-h.NIF[i]; kd=h.NIF[i]*NAG
        dis=h.POP[i]-h.EAP[i]-(h.D15 if i==0 else 0)
        base=h.UNE[i]+kd+(1-m)*formal+(0 if a=='65+' else dis)
        S.append((a,dis,h.UNE[i],kd,formal,m*formal,base))
    return S
if __name__=="__main__":
    S=tablo()
    print("yas  isgdisi issiz kd_tarimdisi formal memnun havuz")
    for s in S: print("%-5s %7.0f %6.0f %7.0f %7.0f %7.0f %8.0f"%s)
    tp=sum(s[6] for s in S); print("TOPLAM %.0f; 16-34 %.0f"%(tp,sum(s[6] for s in S[:2])))
    ek=AILE*AILE_TARIM_ORANI
    print("ucretsiz aile iscisi toplam %.0f, tarimda (2018 orani ile cikarim) %.0f -> havuza ek (yas dagilimi yok)"%(AILE,ek))
    print("tarimdisi kayitdisi/kayitdisi toplam: %.3f"%NAG)
