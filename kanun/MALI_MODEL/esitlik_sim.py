import model, numpy as np
def net(ad,eff,s,pi,phi=0.0):
    p=model.sc(ad); p['duz_oran']=eff; p['s_kayitli']=s; p['prim_devam']=0.0; p['prim_odeme']=pi; p['phi']=phi
    return model.yil(p,p['ramp'][3])['net']/1e9
def pistar(ad,eff,s):
    if net(ad,eff,s,0.0)<0: return None
    if net(ad,eff,s,1.0)>0: return 1.0
    lo,hi=0.0,1.0
    for _ in range(50):
        m=(lo+hi)/2
        if net(ad,eff,s,m)>0: lo=m
        else: hi=m
    return lo
print("EŞİT REJİM (eski ve yeni aynı: sabit prim yok, kapı yok): yıl-4 net (mlr TL), prim sürekliliği 0")
print("pi = eski sabit primin gerçekte tahsil edilen payı (modelde 0,8 varsayılmıştı, YOKLANAMADI)")
for ad in ("Kötümser","Orta","İyimser"):
    p=model.sc(ad)
    for nm,eff in (("düz %13,5",0.135),("A %35",0.35*0.25+0.65*0.135),("A %70",0.7*0.25+0.3*0.135)):
        row=[]
        for s in (p['s_kayitli'],0.5,1.0):
            ps=pistar(ad,eff,s)
            row.append("s=%.2f: net(pi=.8) %+7.2f, pi* %s"%(s,net(ad,eff,s,0.8),("%.2f"%ps if ps is not None else "yok(pi=0'da bile <0)")))
        print("  %-9s %-9s | "%(ad,nm)+" | ".join(row))
# muhasebeci doğrulama havuzu
print("\nMUHASEBECİ DOĞRULAMA GELİRİ: doğrulanmamış B2B hasılat havuzu x ücret oranı")
LOSS={"Kötümser":0.36,"Orta":0.60,"İyimser":0.66}
for ad in ("Kötümser","Orta","İyimser"):
    p=model.sc(ad); y=model.yil(p,p['ramp'][3]); toplam=y['N']*y['ort_H']
    for pb in (0.35,0.70):
        havuz=toplam*p['kurumsal_pay']*pb
        print("  %-9s toplam hasılat %6.1f mlr | doğrulanmamış B2B payı %.2f -> havuz %5.1f mlr | kaybı (%.2f mlr) karşılayan ücret oranı %.2f%% | AD'nin satıcıya getirdiği yük %.1f mlr"%(ad,toplam/1e9,pb,havuz/1e9,LOSS[ad],100*LOSS[ad]*1e9/havuz,havuz*(0.25-0.135)/1e9))
print("  aktif serbest SM+SMMM ~59 958 (ikincil, Ocak 2026 yazısı); kişi başı kayıp = kayıp / 59 958:",["%.0f TL"%(v*1e9/59958) for v in LOSS.values()])

print("\nDENGE ORANI: eşit rejimde (prim sürekliliği 0, pi=0,8) yıl-4 net=0 için gereken taban tevkifat oranı b (tüketici ve doğrulanmış kanal); doğrulanmamış B2B alıcı oranı 0,25")
for ad in ("Kötümser","Orta","İyimser"):
    p=model.sc(ad)
    for pb in (0.35,0.70):
        lo,hi=0.05,0.40
        f=lambda b: net(ad,pb*0.25+(1-pb)*b,p['s_kayitli'],0.8)
        if f(lo)>=0: print("  %-9s B2B %.2f: b=%%5 bile pozitif (net %+.2f)"%(ad,pb,f(lo))); continue
        for _ in range(50):
            m=(lo+hi)/2
            if f(m)>0: hi=m
            else: lo=m
        print("  %-9s doğrulanmamış B2B %.2f: gereken taban oran %%%.1f (teklifte %%13,5)"%(ad,pb,100*hi))
