#!/usr/bin/env python3
"""Defter girdisini gerçek metinle doğrulanmış diye işaretler; düzeltmeleri işler.
Kullanım (python içinden):  from dogrula import dogrula
  dogrula(cilt, defter_sayfa, s=basılı_sayfa, degistir=[(eski, yeni)], ekle="not")
'OCR: ...' satırı 'Kaynak: gerçek metin (Sekkā/Şâmile), s.N — DOĞRULANDI' olur."""
import re,os,sys
D=os.path.dirname(os.path.abspath(__file__))+'/../okuma_defteri/'
def dogrula(c,p,s=None,degistir=(),ekle=None,dosya=None):
    f=D+f'cilt_0{c}.md'; t=open(f,encoding='utf-8').read()
    m=re.search(r'(?ms)^## c%d p%d\b.*?(?=^## c\d|\Z)'%(c,p),t)
    assert m,(c,p); e=m.group(0)
    for a,b in degistir:
        assert a in e,(c,p,a[:40]); e=e.replace(a,b,1)
    s=s if s is not None else p
    e,n=re.subn(r'(?m)^- OCR:.*$',f'- Kaynak: gerçek metin (Sekkā/Şâmile), s.{s} — DOĞRULANDI',e)
    if n==0 and 'DOĞRULANDI' not in e: e=e.replace('\n','\n- Kaynak: gerçek metin (Sekkā/Şâmile), s.%d — DOĞRULANDI\n'%s,1)
    if ekle: e=e.rstrip('\n')+'\n- Doğrulama notu: '+ekle+'\n\n'
    open(f,'w',encoding='utf-8').write(t[:m.start()]+e+t[m.end():])
