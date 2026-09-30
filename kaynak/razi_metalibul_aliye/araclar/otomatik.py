import re,json,collections,sys,os
sys.path.insert(0,'araclar')
from dogrula import dogrula
import os
S=os.environ.get('RAZI_OCR_DIZINI','ocr_gecici')+'/'   # OCR depoda DEĞİL: git geçmişinden (0102e86^) geçici olarak çıkarılır, depoya alınmaz (CLAUDE.md 25-E)
exec(open(S+'kiyas.py').read().split('res={}')[0])   # norm, realpages, defterpages
K=json.load(open(S+'kiyas.json'))
UYGULA = len(sys.argv)>1 and sys.argv[1]=='uygula'
manuel=[];stat=collections.Counter()
for c in range(1,10):
    R=realpages(c)
    t=open('metin_sekka/cilt_0%d.txt'%c,encoding='utf-8').read()
    ms=list(re.finditer(r'(?m)^\[(\d+)\]',t)); RT={}
    for i,x in enumerate(ms):
        e=ms[i+1].start() if i+1<len(ms) else len(t); RT[int(x.group(1))]=' '.join(norm(t[x.end():e]))
    d=open('okuma_defteri/cilt_0%d.md'%c,encoding='utf-8').read()
    for m in re.finditer(r'(?ms)^## c%d p(\d+)\b(.*?)(?=^## c\d|\Z)'%c,d):
        p=int(m.group(1)); e=m.group(2)
        if 'DOĞRULANDI' in e: continue
        v=K[str(c)].get(str(p))
        if not v: manuel.append((c,p,'eşleşme yok')); stat['C']+=1; continue
        f,s,rec,pre,nr,no=v
        ctx=' '.join(RT.get(x,'') for x in (s-1,s,s+1))
        # Arapça alıntılar: yalnız 'İçerik' satırındaki tırnaklı Arapça diziler (>=2 kelime)
        q=[ ' '.join(norm(a)) for a in re.findall(r'[ء-يً-ْ ]{8,}',e)]
        q=[x for x in q if len(x.split())>=2]
        yok=[x for x in q if x not in ctx]
        govde='\n'.join(l for l in e.split('\n') if not l.startswith('- OCR:'))
        isaret=bool(re.search(r'…|kısmî|kısmi|okunamad|bozuk|OCR|\(cümle',govde))
        bos=('Boş' in govde and len(govde)<400)
        if bos:
            ocw=len(norm(json.load(open(S+'ocr/cilt_0%d.json'%c,encoding='utf-8'))[p-1]))
            if ocw<15:
                stat['boş']+=1
                if UYGULA: dogrula(c,p,s=p,etiket='OTOMATİK DOĞRULANDI',ekle='OCR sayfası boş/çok kısa; gerçek metinde bu sayfa için içerik yok (boş sayfa).')
                continue
        if rec<0.50: manuel.append((c,p,'C recall %.2f'%rec)); stat['C']+=1; continue
        if yok: manuel.append((c,p,'alıntı bulunamadı: %s'%('|'.join(yok)[:80]))); stat['alıntı']+=1; continue
        if isaret: manuel.append((c,p,'girdide OCR sorunu işareti (…/kısmî/bozuk)')); stat['işaret']+=1; continue
        if rec<0.75: manuel.append((c,p,'recall %.2f<0.75'%rec)); stat['B']+=1; continue
        stat['A']+=1
        if UYGULA:
            dogrula(c,p,s=s,etiket='OTOMATİK DOĞRULANDI',ekle="OCR sayfası ile gerçek metin s.%d otomatik karşılaştırıldı: kelime kapsama %%%d, Arapça alıntı denetimi %d/%d bulundu, girdide OCR sorunu işareti yok (defter numarası ile gerçek sayfa farkı %+d). SINIR: bu ölçü elle bakılan 140 sayfada içerik düzeltmesi gereken 16 sayfanın 13'ünü yakaladı; geçen sayfaların yaklaşık %%5'inde hata kalabilir; özet yeniden okunmadı."%(s,round(rec*100),len(q),len(q),s-p))
print(dict(stat)); json.dump(manuel,open(S+'manuel_liste.json','w'),ensure_ascii=False)
print('manuel liste',len(manuel))
