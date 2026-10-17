import json
R=2966.0
DISCOURAGED=2608.0; MUSAIT_ARAMAYAN=2348.0; ARAYIP_MUSAIT_DEGIL=173.0
POTANSIYEL=DISCOURAGED+MUSAIT_ARAMAYAN+ARAYIP_MUSAIT_DEGIL
DIGER=4665.0; EGITIM=3795.0; UCRETSIZ_AILE_TARIM_DISI=599.0
NEET={'15-24':2684.0,'15-29':4711.0,'15-34':6672.0}
A1=0.40; A2=0.25
R_RESMI=A1*0.60+A2*0.30
R_GAYRI=A1*0.20+A2*0.10
def n_yeni(carpan=1.0,genis=False):
    g=POTANSIYEL+(DIGER if genis else 0.0)
    return carpan*(R*R_RESMI+g*R_GAYRI+UCRETSIZ_AILE_TARIM_DISI*R_GAYRI)
out=dict(potansiyel_isgucu=POTANSIYEL,r_resmi=R_RESMI,r_gayri=R_GAYRI,
 neet_25_29=NEET['15-29']-NEET['15-24'],neet_30_34=NEET['15-34']-NEET['15-29'],
 iyi_cekirdek=n_yeni(1.0,False),iyi_genis=n_yeni(1.0,True),orta_cekirdek=n_yeni(0.5,False),orta_genis=n_yeni(0.5,True),kotu=100.0)
json.dump(out,open('havuz_hesabi.json','w'),indent=1)
for k,v in out.items(): print(k,round(v,3) if v<10 else round(v))
