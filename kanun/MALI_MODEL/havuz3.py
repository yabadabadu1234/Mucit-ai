import havuz as h
NAG=4770.36/8659.821
UCRETLI_DISK=8359/0.467
M2=0.127
AILE_TARIM=2463.66*2.6/3.1
def tablo():
    memnun_top=M2*UCRETLI_DISK
    formal=[h.EMP[i]-h.NIF[i] for i in range(6)]
    fs=sum(formal)
    S=[]
    for i,a in enumerate(h.AD):
        dis=h.POP[i]-h.EAP[i]-(h.D15 if i==0 else 0)
        mem=memnun_top*formal[i]/fs
        kd=h.NIF[i]*NAG
        havuz=h.UNE[i]+kd+(formal[i]-mem)+(0 if a=='65+' else dis)
        S.append((a,dis,h.UNE[i],kd,formal[i],mem,havuz))
    return S,memnun_top
if __name__=="__main__":
    S,mt=tablo()
    print("ucretli (DISK-AR tabani) %.0f; memnun (>=2x asgari) %.0f bin"%(UCRETLI_DISK,mt))
    print("yas  isgdisi issiz kd_tarimdisi formal memnun havuz")
    for s in S: print("%-5s %7.0f %6.0f %7.0f %7.0f %7.0f %8.0f"%s)
    print("TOPLAM %.0f; 16-34 %.0f; ek aile iscisi (tarim) %.0f"%(sum(s[6] for s in S),sum(s[6] for s in S[:2]),AILE_TARIM))
