import model
def net(ad,eff,s,pdv=1.0,phi=None):
    p=model.sc(ad); p['duz_oran']=eff; p['s_kayitli']=s; p['prim_devam']=pdv
    if phi is not None: p['phi']=phi
    return model.yil(p,p['ramp'][3])['net']/1e9
def kirilma(ad,eff,pdv,phi):
    lo,hi=0.0,0.95
    if net(ad,eff,lo,pdv,phi)<0: return None
    if net(ad,eff,hi,pdv,phi)>0: return 1.0
    for _ in range(50):
        m=(lo+hi)/2
        if net(ad,eff,m,pdv,phi)>0: lo=m
        else: hi=m
    return lo
print("Yıl-4 net (mlr TL). eff = etkin tevkifat oranı; s = rejime geçen kayıtlı payı; prim sürekliliği (pdv)")
for ad in ("Kötümser","Orta","İyimser"):
    p0=model.sc(ad)
    for nm,eff,phi in (("düz %10,5 (Madde P), sahte kaybı modelde",0.105,None),("A kuralı %35 doğrulanmamış B2B, sahte=0",0.35*0.25+0.65*0.105,0.0),("A kuralı %70, sahte=0",0.7*0.25+0.3*0.105,0.0)):
        for pdv in (1.0,0.5):
            print("  %-9s %-44s prim sürekliliği %.1f: net(s=taban %.2f) %+7.2f | s kırılma %s | herkes geçse(s=0.8) %+7.2f"%(ad,nm,pdv,p0['s_kayitli'],net(ad,eff,p0['s_kayitli'],pdv,phi),("%.2f"%kirilma(ad,eff,pdv,phi) if kirilma(ad,eff,pdv,phi) is not None else "yok(her s'de zarar)"),net(ad,eff,0.8,pdv,phi)))
