import sys, subprocess, numpy as np, pypdf, io
from PIL import Image
src=sys.argv[1]; out=sys.argv[2]
subprocess.run(['pdftoppm','-png','-r','100','-singlefile',src,'_t'],check=True)
im=np.array(Image.open('_t.png').convert('RGB')); mask=(im.sum(axis=2)<600)
ys,xs=np.where(mask); x0,x1,y0,y1=max(xs.min()-3,0),xs.max()+4,max(ys.min()-3,0),ys.max()+4
r=pypdf.PdfReader(src); p=r.pages[0]; W=float(p.mediabox.width); H=float(p.mediabox.height)
k=72/100; cx0,cx1=x0*k,x1*k; cy0,cy1=H-y1*k,H-y0*k   # pdf koordinatı
cw,ch=cx1-cx0,cy1-cy0; A=(595.276,841.89); s=min(A[0]/cw,A[1]/ch)
p.add_transformation(pypdf.Transformation().translate(-cx0,-cy0).scale(s,s))
# koyu zemin: A4 sayfa + üstüne içerik üstten hizalı
bg=pypdf.PageObject.create_blank_page(width=A[0],height=A[1])
from pypdf.generic import DecodedStreamObject, NameObject
st=DecodedStreamObject(); st.set_data(b'0.055 0.082 0.106 rg 0 0 595.276 841.89 re f')
bg[NameObject('/Contents')]=pypdf.generic.ArrayObject([bg.indirect_reference]) if False else st
p.add_transformation(pypdf.Transformation().translate(0,A[1]-ch*s))
p.mediabox=pypdf.generic.RectangleObject([0,0,A[0],A[1]]); p.cropbox=p.mediabox
bg.merge_page(p)
w=pypdf.PdfWriter(); w.add_page(bg); w.write(out)
print('kutu',round(cw),round(ch),'ölçek',round(s,3),'sayfa',A)
