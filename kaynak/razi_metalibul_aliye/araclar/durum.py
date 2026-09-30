#!/usr/bin/env python3
"""Okuma defterlerini tarar (okuma_defteri/cilt_0X.md), her '## c{V} p{N}' başlığını sayar,
OKUMA_DURUMU.md dosyasını üretir: okunan/okunmayan sayfa aralıkları sayıyla."""
import json,re,os
d=os.path.dirname(os.path.abspath(__file__))+'/../'
rows=[]; tot_p=tot_r=0
SAYI=json.load(open(d+'metin_sekka/sayfa_sayilari.json',encoding='utf-8'))['pdf_sayfa_sayisi']
def ranges(nums):
    nums=sorted(nums); out=[]
    for n in nums:
        if out and n==out[-1][1]+1: out[-1][1]=n
        else: out.append([n,n])
    return ', '.join(f'{a}' if a==b else f'{a}–{b}' for a,b in out) or '—'
for v in range(1,10):
    n=SAYI[str(v)]
    f=d+f'okuma_defteri/cilt_0{v}.md'
    read=set()
    q={'iyi':0,'orta':0,'kötü':0}
    if os.path.exists(f):
        t=open(f,encoding='utf-8').read()
        for m in re.finditer(r'^## c%d p(\d+)\s*(.*)$'%v,t,flags=re.M): read.add(int(m.group(1)))
        for m in re.finditer(r'OCR: (iyi|orta|kötü)',t): q[m.group(1)]+=1
    unread=[i for i in range(1,n+1) if i not in read]
    rows.append((v,n,len(read),ranges(read),ranges(unread),q))
    tot_p+=n; tot_r+=len(read)
o=['# Okuma Durumu — el-Metâlibü\'l-Âliye (Sekkā neşri)\n',
'Bu dosya `araclar/durum.py` ile **okuma defterlerinden otomatik** üretilir; elle düzenlenmez.\n',
f'**Toplam:** {tot_r} / {tot_p} sayfa okundu ve deftere yazıldı ({100*tot_r/tot_p:.1f}%).\n',
'| Cilt | Sayfa | Okunan | % | OCR: iyi/orta/kötü | Okunan aralık (PDF sayfa indisi) | Okunmayan aralık |','| :-- | --: | --: | --: | :-- | :-- | :-- |']
for v,n,r,rr,ur,q in rows:
    o.append(f'| {v} | {n} | {r} | {100*r/n:.0f} | {q["iyi"]}/{q["orta"]}/{q["kötü"]} | {rr} | {ur} |')
o.append('\n"Okundu" = o sayfanın metni baştan sona okundu ve defterde kaydı var. Başlıktan/fihristten çıkarım "okundu" sayılmaz.\n')
open(d+'OKUMA_DURUMU.md','w',encoding='utf-8').write('\n'.join(o))
print('\n'.join(o))
