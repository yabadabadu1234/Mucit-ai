import os,sys,re
kaynak,tercume,cikti=sys.argv[1],sys.argv[2],sys.argv[3]
bitmis={f.split('_')[0]+'_'+f.split('_')[1]:f for f in os.listdir(tercume) if f.endswith('.md')}
satirlar=['| Sıra | Modül | Asıl başlık | Asıl kelime | Tercüme kelime | Nisbet | Hâli |','|---|---|---|---|---|---|---|']
tk=ak=tam=0
for f in sorted(os.listdir(kaynak)):
    a=open(os.path.join(kaynak,f)).read(); anahtar=f[:-4]
    baslik=a.splitlines()[0].lstrip('# ').strip()
    ka=len(a.split()); ak+=ka
    if anahtar in bitmis:
        t=open(os.path.join(tercume,bitmis[anahtar])).read(); kt=len(t.split()); tk+=kt; tam+=1
        satirlar.append('| %s | %s | %s | %d | %d | %.2f | tercüme edildi |'%(anahtar[:3],anahtar[4:],baslik,ka,kt,kt/ka))
    else:
        satirlar.append('| %s | %s | %s | %d | 0 | 0 | eksik |'%(anahtar[:3],anahtar[4:],baslik,ka))
bas='Toplam modül: %d. Tercüme edilen: %d. Eksik: %d. Asıl kelime: %d. Tercüme edilen modüllerin asıl kelimesi oranı: yüzde %.1f.\n\n'%(len(os.listdir(kaynak)),tam,len(os.listdir(kaynak))-tam,ak,100*sum(len(open(os.path.join(kaynak,k+'.txt')).read().split()) for k in bitmis)/ak)
open(cikti,'w').write('# OpenStax Teşrîh ve Menâfi\'-i A\'zâ: Modül Modül İlerleme Cedveli\n\n'+bas+'\n'.join(satirlar)+'\n')
print(bas)
