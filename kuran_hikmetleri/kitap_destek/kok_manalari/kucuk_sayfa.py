"""Lügat sayfalarının küçük (önizleme) hâli: <no>_1_k.webp; hücre ekranda dar iken bu yüklenir."""
import pathlib
from PIL import Image
C = pathlib.Path(__file__).resolve().parent / 'lugat_sayfalari'
n = 0
for f in sorted(C.glob('*_1.webp')):
    o = C / (f.stem + '_k.webp')
    if o.exists() and o.stat().st_mtime >= f.stat().st_mtime: continue
    i = Image.open(f); i.resize((160, round(160 * i.height / i.width)), Image.LANCZOS).save(o, 'WEBP', quality=60, method=6); n += 1
print(n, 'önizleme')
