import openpyxl, model as m
wb=openpyxl.load_workbook('MIKRO_MUKELLEF_MALI_MODEL.xlsx')
g=wb['Girdiler']
out=["# EXCEL DOSYASININ GÖRÜNÜMÜ: MIKRO_MUKELLEF_MALI_MODEL.xlsx (formüllü; sayfalar: Girdiler, Hesap, Sonuc, Senaryolar_Python)\n","Excel'in 'Sonuc' sayfası bağımsız formül hesaplayıcısıyla (`formulas` kütüphanesi) çalıştırıldı: Orta senaryoda net etki 1,3187 milyar TL; Python modeliyle aynıdır. Aşağıda Girdiler sayfası ve üç senaryonun sonucu yazılıdır.\n","## Girdiler\n","| Girdi | Kod | Kötümser | Orta | İyimser | Kaynak/durum |","| :-- | :-- | --: | --: | --: | :-- |"]
r=6
while g.cell(row=r,column=1).value and g.cell(row=r,column=2).value:
    v=[g.cell(row=r,column=c).value for c in (1,2,3,4,5,7)]
    out.append("| "+" | ".join("" if x is None else (("%g"%x) if isinstance(x,(int,float)) else str(x)) for x in v)+" |"); r+=1
out+=["\n## Sonuç (4. yıl, milyar TL)\n","| Kalem | Kötümser | Orta | İyimser |","| :-- | --: | --: | --: |"]
ys={sc:m.bes_yil(m.sc(sc))[3] for sc in m.SENARYO}
for ad,k,neg in [("Brüt tevkifat","brut_tevkifat",1),("BES ve Devlet katkısı","bes_ve_devlet_katkisi",-1),("90 gün prim hibesi","myo_primi",-1),("Donanım KDV mahsubu","kdv_mahsubu",-1),("Yutulma: vergi","yutulma_vergi",-1),("Yutulma: prim","yutulma_prim",-1),("**NET**","net",1)]:
    out.append("| %s | %s |"%(ad," | ".join(("%.2f"%(neg*ys[sc][k]/1e9)).replace(".",",") for sc in m.SENARYO)))
open('EXCEL_GORUNUMU.md','w').write("\n".join(out)+"\n")
