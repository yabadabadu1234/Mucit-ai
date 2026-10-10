import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os
OUT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams['font.family']='DejaVu Sans'
NOT="Taslak görsel; tutarlar teklifin örnek hesabıdır, ölçülmüş veri değildir."
# 1 akış şeması
fig,ax=plt.subplots(figsize=(13,7.2)); ax.set_xlim(0,13); ax.set_ylim(0,7.2); ax.axis('off')
def kutu(x,y,w,h,t,c='#e8eef6',ec='#1f3a5f',fs=10):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.04",fc=c,ec=ec,lw=1.4)); ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=fs,wrap=True)
def ok(x1,y1,x2,y2): ax.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle="->",color='#34475f',lw=1.4))
kutu(0.3,5.9,2.6,1.0,"Mükellef\nfatura keser\n(portal, e-Devlet onayı)",'#fff3d6')
kutu(3.6,5.9,2.4,1.0,"Portal\nreferans kodu üretir\n(M.1 (a))")
ok(2.9,6.4,3.6,6.4)
kutu(0.3,3.7,3.6,1.3,"KURUMSAL ALICI\nÖdemede %15 × (hasılat − %30)\nmuhtasarla öder; ödemeden gider yazamaz\n(M.1 (b))")
kutu(4.5,3.7,3.6,1.3,"VADELİ (30-90 gün)\nVadeli Tevkifat Senedi + elektronik teminat\nVadede teminattan Hazine'ye\n(M.1 (b))")
kutu(8.7,3.7,4.0,1.3,"NİHAÎ TÜKETİCİ veya PLATFORM\nBanka / ödeme kuruluşu tahsilatta\n%10,5 keser, Hazine'ye aktarır\n(M.1 (c), (l))")
ok(4.8,5.9,2.1,5.0); ok(4.8,5.9,6.3,5.0); ok(5.4,5.9,10.7,5.0)
kutu(0.3,1.7,3.6,1.2,"YURT DIŞI MÜŞTERİ\nDöviz intikalinde %15 × %70\ntransferi yapan kuruluş keser\n(M.1 (ç))")
ok(4.8,5.9,1.0,2.9) if False else None
kutu(4.5,1.7,3.6,1.2,"KODSUZ GİRİŞ\n48 saat bekler, bloke edilmez;\nmükellef eşleştirir; yoksa hizmet bedeli\n(M.1 (c))",'#fff3d6')
kutu(8.7,1.7,4.0,1.2,"AŞIRI GİRİŞ (5× ortalama ve ≥ 2 asgari ücret)\n15 gün inceleme askısı,\ngelir kaynağı beyanı (M.1 (j))",'#fdeaea','#a11d1d')
kutu(3.5,0.15,6.0,0.9,"Tüm tahsilat münhasır hesaba girer → net bakiye serbest\nTavan: 24 brüt asgari ücret (792.720 TL) → aşılınca genel hükümler (M.1 (h))",'#e8f5ec','#14662b')
for x in (2.1,6.3,10.7): ok(x,3.7,6.5,1.05) if False else None
ax.text(6.5,3.15,"Alıcı türüne göre tevkifat (üst sıra) ve istisnai hâller (alt sıra)",ha="center",fontsize=9,color="#555"); ax.text(6.5,7.05,"Tevkifat akışı: alıcı türüne göre",ha='center',fontsize=14,fontweight='bold',color='#1f3a5f')
ax.text(0.1,0.0,NOT,fontsize=8,color='#555')
fig.savefig(os.path.join(OUT,"sema_01_tevkifat_akisi.png"),dpi=110,bbox_inches='tight'); plt.close()
# 2 100 TL dağılım
fig,ax=plt.subplots(figsize=(11,6)); 
ad=["Gayrisafi\nhasılat","Götürü gider\n(%30)","Tevkifat\nmatrahı","Tevkifat\n(%15)","Mükellefe\nnet","  İçinden BES\n(tevkifatın %3'ü)"]
vals=[100,-30,70,-10.5,89.5,0.315]
cols=['#2d6aa8','#9aa7b8','#2d6aa8','#a11d1d','#14662b','#c98b00']
ax.bar(0,100,color=cols[0]); ax.bar(1,30,bottom=70,color=cols[1]); ax.bar(2,70,color=cols[2]); ax.bar(3,10.5,color=cols[3]); ax.bar(4,89.5,color=cols[4]); ax.bar(5,0.315*100/100*3.33,color=cols[5])
for x,t in [(0,"100"),(1,"−30"),(2,"70"),(3,"10,5"),(4,"89,5"),(5,"0,315 TL\n(+0,063 Devlet katkısı)")]: ax.text(x,(100 if x==0 else 100 if x==1 else 72 if x==2 else 12.5 if x==3 else 91.5 if x==4 else 3.8),t,ha='center',fontsize=11,fontweight='bold')
ax.set_xticks(range(6)); ax.set_xticklabels(ad,fontsize=10); ax.set_ylabel("TL (yüz liralık hasılat için)"); ax.set_ylim(0,112)
ax.set_title("100 TL'lik hasılatın dağılımı (nihaî tüketiciye hizmet)",fontsize=13,fontweight='bold',color='#1f3a5f'); ax.spines[['top','right']].set_visible(False)
ax.text(0,-22,"Etkin oran: 70 × 0,15 = %10,5. Not: 5. sütun ölçeksizdir (görünürlük için büyütülmüştür).  "+NOT,fontsize=8,color='#555',transform=ax.transData)
fig.savefig(os.path.join(OUT,"grafik_01_yuz_lira.png"),dpi=110,bbox_inches='tight'); plt.close()
# 3 kişi başı Hazine
h=["2 asgari\n66.060","6 asgari\n198.180","12 asgari\n396.360","24 asgari\n792.720"]
tev=[6936,20809,41618,83236]; bes=[250,749,1498,2996]; myo=[0,0,20809,20809]; net=[6687,20060,19311,59430]
import numpy as np
x=np.arange(4); fig,ax=plt.subplots(figsize=(11,6.2))
ax.bar(x,net,color='#14662b',label="Hazine'de kalan net"); ax.bar(x,bes,bottom=net,color='#c98b00',label="BES yükü (%3,6)"); ax.bar(x,myo,bottom=np.array(net)+np.array(bes),color='#a11d1d',label="90 gün MYÖ primi (%21)")
for i in range(4): ax.text(i,tev[i]+1500,f"Tevkifat {tev[i]:,}".replace(",","."),ha='center',fontsize=10,fontweight='bold')
ax.set_xticks(x); ax.set_xticklabels(h); ax.set_ylabel("TL / kişi / yıl"); ax.legend(frameon=False)
ax.set_title("Kişi başına tevkifatın dağılımı (teklif III.D.2 tablosu)",fontsize=13,fontweight='bold',color='#1f3a5f'); ax.spines[['top','right']].set_visible(False)
fig.text(0.01,-0.02,"Yutulma (halen kayıtlı mükelleflerin geçişi) bu grafikte yoktur; III.D.4'e bakınız. "+NOT,fontsize=8,color='#555')
fig.savefig(os.path.join(OUT,"grafik_02_kisi_basi.png"),dpi=110,bbox_inches='tight'); plt.close()
# 4 durum akışı
fig,ax=plt.subplots(figsize=(13,4.6)); ax.set_xlim(0,13); ax.set_ylim(0,4.6); ax.axis('off')
def k2(x,y,t,c='#e8eef6',ec='#1f3a5f',w=2.3): ax.add_patch(FancyBboxPatch((x,y),w,1.2,boxstyle="round,pad=0.04",fc=c,ec=ec,lw=1.4)); ax.text(x+w/2,y+0.6,t,ha='center',va='center',fontsize=10)
k2(0.2,2.9,"Tescil\n(e-Devlet)"); k2(3.0,2.9,"AKTİF\nmikro mükellef",'#e8f5ec','#14662b'); k2(6.0,2.9,"Tavan aşıldı\n(792.720 TL)",'#fdeaea','#a11d1d'); k2(9.0,2.9,"Genel hükümler\n(ertesi ay başından)",'#f3f3f3','#555',w=2.8)
k2(3.0,0.7,"Gönüllü çıkış\n→ ertesi yıl sonuna\nkadar yeniden tescil yok",'#fff3d6','#9a5b00',w=3.0); k2(7.5,0.7,"Yıl sonu hasılat < tavan\n→ ertesi yıl başı\nyeniden tescil talebi",'#e8eef6',w=3.2)
for a,b in [((2.5,3.5),(3.0,3.5)),((5.3,3.5),(6.0,3.5)),((8.3,3.5),(9.0,3.5)),((4.1,2.9),(4.1,1.9)),((10.4,2.9),(9.4,1.9))]: ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="->",lw=1.4))
ax.annotate("",xy=(3.6,3.0),xytext=(8.6,1.9)) if False else None
ax.text(6.5,4.35,"Mükellefiyet yaşam döngüsü (M.1 (h))",ha='center',fontsize=14,fontweight='bold',color='#1f3a5f'); ax.text(0.1,0.1,NOT,fontsize=8,color='#555')
fig.savefig(os.path.join(OUT,"sema_02_yasam_dongusu.png"),dpi=110,bbox_inches='tight'); plt.close()
print("grafikler tamam")
