import sys, glob, subprocess, os
from PIL import Image
pdf, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
res = sys.argv[4] if len(sys.argv) > 4 else "55"
for f in glob.glob('/tmp/_sh-*.png'): os.remove(f)
subprocess.run(['pdftoppm','-r',res,'-png',pdf,'/tmp/_sh'])
fs = sorted(glob.glob('/tmp/_sh-*.png'))
ims = [Image.open(f) for f in fs]
w, h = ims[0].size
rows = (len(ims)+cols-1)//cols
sh = Image.new('RGB',(w*cols,h*rows),'white')
for i, im in enumerate(ims): sh.paste(im,((i%cols)*w,(i//cols)*h))
sh.save(out); print(len(ims), sh.size)
