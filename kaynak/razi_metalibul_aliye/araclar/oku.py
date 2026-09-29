#!/usr/bin/env python3
"""Kullanım: python3 oku.py CİLT BAŞ SON   (pdf sayfa indisi, 1'den başlar, SON dahil)
Sayfa metnini OCR'dan başlıklı basar. Okuma defterine yazılan kayıtlar 'durum.py' ile sayılır."""
import json,sys,os
k=os.path.dirname(os.path.abspath(__file__))+'/../sayfa_metni/'
v=int(sys.argv[1]); a=int(sys.argv[2]); b=int(sys.argv[3])
P=json.load(open(k+f'cilt_0{v}.json',encoding='utf-8'))
for i in range(a,min(b,len(P))+1):
    print(f'=== c{v} p{i} ===')
    print(P[i-1])
