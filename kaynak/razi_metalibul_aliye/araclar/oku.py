#!/usr/bin/env python3
"""Kullanım: python3 oku.py CİLT BAŞ SON   (Sekkā neşrinin BASILI sayfa numarası, SON dahil)
Metni metin_sekka/cilt_0V.txt'den (Şâmile .bok'un gerçek metni) sayfa başlıklı basar."""
import re,sys,os
k=os.path.dirname(os.path.abspath(__file__))+'/../metin_sekka/'
v=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
t=open(k+f'cilt_0{v}.txt',encoding='utf-8').read()
m=list(re.finditer(r'(?m)^\[(\d+)\]',t))
for i,x in enumerate(m):
    n=int(x.group(1))
    if a<=n<=b:
        e=m[i+1].start() if i+1<len(m) else len(t)
        print(f'=== c{v} s{n} ==='); print(t[x.end():e].strip())
