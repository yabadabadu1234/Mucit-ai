P=1.0; FEE=(0.0,0.01,0.03)
def cift_net(t_s,k,dogrulandi,p_taklit,fee):
    sub=(k-t_s)*P if dogrulandi else 0.0
    return p_taklit*sub-fee
print("Çift (alıcı+satıcı) sahte işlemin net kazancı = P(taklit) x (alıcı mahsup oranı - satıcı vergi oranı) x P - ücret")
print("Hazine kaybı = aynı çarpım (korunum): sızıntı = sahte işleme verilen sübvansiyon\n")
print("%-34s %8s %8s %12s"%("kural","t_satici","k_alici","azamî kazanç"))
for ad,t,k,dog,pt in (("teklif (mevcut, doğrulama yok)",0.105,0.25,True,1.0),("nötr kural (AD)",0.25,0.25,False,1.0),("doğrulama yok, alıcı kredisi 10,5",0.105,0.105,False,1.0)):
    g=max(cift_net(t,k,dog,pt,f) for f in FEE)
    print("%-34s %8.3f %8.3f %+12.3f"%(ad,t,k,g))
print("\nDoğrulanmış kanal: sübvansiyon (k-t)=0,145 yalnız bağımsız şahitli işlemde; sahtekârın şahidi taklit etme olasılığı p")
for p in (0.0,0.01,0.05,0.2,1.0):
    print("  p_taklit=%.2f  azamî kazanç %+.4f"%(p,max(cift_net(0.105,0.25,True,p,f) for f in FEE)))
print("\nDürüst işlem yükü (birim 1,0 gerçek B2B; düzenli piyasa ayarı: satıcı %25 öder, alıcı %25 indirir):")
for ad,t,k in (("düzenli piyasa",0.25,0.25),("teklif doğrulanmış kanalda",0.105,0.25),("nötr kural doğrulanmamışta",0.25,0.25)):
    print("  %-30s satıcı payı %.3f  alıcı indirimi %.3f  Hazine sübvansiyonu %.3f"%(ad,t,k,k-t))
