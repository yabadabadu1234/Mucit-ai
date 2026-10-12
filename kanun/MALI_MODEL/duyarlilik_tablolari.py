import model as m, genc3
out=["# DUYARLILIK TABLOLARI (F 3-I 300) -- her tabloda yalnız bir parametre değişir, düz oran %13,5, diğerleri baz; gelire bağlı prim baz (tam prim eşiği 6 asgari ücret), maaşlı payı baz (F 3-I 304)\n",
"Mali model: dördüncü yıl net etki, milyar TL (Kötümser / Orta / İyimser). Genç modeli: N=3000, tohum 1; teklif rejimi ve mevcut kayıtlı rejim.\n"]
def fm(ad,deg,key=None,oran=0.135):
    r=[]
    for sc in m.SENARYO:
        p=m.sc(sc);p['duz_oran']=oran;p['prim_devam']=0.0
        if key: p[key]=deg
        r.append(m.bes_yil(p)[3]['net']/1e9)
    return r
def tablo(baslik,key,vals):
    out.append("\n## %s\n\n| değer | Kötümser | Orta | İyimser |\n|:--|--:|--:|--:|"%baslik)
    for v in vals:
        a=fm(None,v,key); out.append("| %s | %.2f | %.2f | %.2f |"%(v,*a))
out.append("\n## Düz oran\n\n| oran | Kötümser | Orta | İyimser |\n|:--|--:|--:|--:|")
for o in (0.105,0.12,0.135,0.15,0.18,0.20,0.22,0.25,0.27,0.30):
    out.append("| %%%.1f | %.2f | %.2f | %.2f |"%(o*100,*fm(None,None,None,o)))
for k,v in [("prim_k",(3,4,6,8,12)),("prim_toplama",(0,.5,.8,1)),("prim_odeme",(.5,.65,.8,.9,1)),("s_kayitli",(.05,.15,.3,.45)),("u_ucretli",(.1,.2,.3,.4)),
 ("medyan_W",(3,4,5,6,8)),("sigma",(.6,.9,1.2)),("n_toplam",(100000,331000,700000,1096000)),("phi",(.005,.01,.02,.04)),
 ("onlem",(0,.3,.5,.7,.9)),("kurumsal_pay",(.3,.5,.7,.9)),("kgf_alim",(.03,.05,.08,.12)),("kgf_temerrut",(.06,.1,.15,.25)),
 ("itiraz_oran",(.02,.04,.08)),("denetim",(0,.005,.01,.02)),("bes_vazgecme",(.2,.35,.5,.8)),("myo_uygun",(.1,.2,.35,.5)),("iskonto",(.03,.05,.1))]:
    tablo(k,k,v)
out.append("\n# GENÇ MODELİ\n")
cols=['gecim72','yarim72','acik_firma','kalici','dip','canli12','devlet_pv']
def g(par,ad):
    out.append("\n## %s\n\n| değer | teklif geçim72 | teklif açık firma | teklif kalıcı | teklif dip | teklif canlı12 | teklif devlet PV | mevcut kayıtlı geçim72 | mevcut kayıtlı yıkım |\n|:--|--:|--:|--:|--:|--:|--:|--:|--:|"%ad)
    return
def sweep(key,vals):
    g(None,key)
    for v in vals:
        _,r=genc3.calistir(dict(genc3.VARSAYILAN,duz_oran=0.135,**{key:v}) if key!="duz_oran" else dict(genc3.VARSAYILAN,duz_oran=v),3000,1)
        t=r['teklif'];e=r['mevcut, kayıtlı']
        out.append("| %s | %.3f | %.3f | %.3f | %.3f | %.3f | %.0f | %.3f | %.3f |"%(v,t['gecim72'],t['acik_firma'],t['kalici'],t['dip'],t['canli12'],t['devlet_pv'],e['gecim72'],e['yikim']))
for k,v in [("duz_oran",(0.105,0.135,0.15,0.18,0.22,0.27)),("b0",(4000,5500,7000)),("L",(.3,.45,.6)),("kappa",(0,.05,.1,.2,.4)),("mal_pay",(.2,.4,.6)),
 ("c_mal",(.3,.5,.7)),("c_hiz",(.05,.15,.3)),("faiz",(0,.015,.03)),("sv",(.2,.5,.8)),("drag",(0,.1,.3)),("aile_olcek",(.5,1,1.5)),
 ("erisim_kd",(.4,.55,.8)),("kayip_kd",(.08,.12,.2)),("gss_ac",(True,False)),("gss_esik_katsayi",(0.5,1,2)),("dayanma",(True,False)),("hedef_canli12",(.65,.75,.85))]:
    sweep(k,v)
open("DUYARLILIK_TABLOLARI.md","w").write("\n".join(out)+"\n")
print(len(out))
