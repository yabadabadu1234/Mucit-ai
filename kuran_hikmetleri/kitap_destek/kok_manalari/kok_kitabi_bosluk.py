"""Sayfa doluluğu ölçüsü (F 3-I 413: sayfanın çeyreğinden fazlası boş olamaz).
Her sayfa 20 dpi'da çizilir; içerik alanı 6 mm'lik karelere bölünür; mürekkep taşımayan kare boştur.
Tek komut: python3 kok_kitabi_bosluk.py cilt.pdf [...]  →  boş oranı > 0.25 olan sayfaların listesi ve sayısı."""
import sys, subprocess, tempfile, pathlib, glob
from PIL import Image
DPI = 24; MM = DPI / 25.4
SOL, UST, SAG, ALT = 13, 12, 148 - 13, 210 - 15            # içerik alanı (mm)
KARE = 4

def oranlar(pdf):
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(['pdftoppm', '-r', str(DPI), '-png', '-gray', str(pdf), t + '/p'], check=True)
        out = []
        for f in sorted(glob.glob(t + '/p-*.png')):
            im = Image.open(f).convert('L'); W, H = im.size; px = im.load()
            x0, x1, y0, y1 = int(SOL * MM), int(SAG * MM), int(UST * MM), int(ALT * MM); k = max(int(KARE * MM), 1)
            nx = (x1 - x0) // k; ny = (y1 - y0) // k; h = [0] * nx; en = 0
            for j in range(ny):
                y = y0 + j * k
                for i in range(nx):
                    x = x0 + i * k; koyu = False
                    for yy in range(y, y + k, 2):
                        for xx in range(x, x + k, 2):
                            if px[xx, yy] < 215: koyu = True; break
                        if koyu: break
                    h[i] = 0 if koyu else h[i] + 1
                st = []                                           # histogramda en büyük dikdörtgen
                for i in range(nx + 1):
                    c = h[i] if i < nx else 0; bas = i
                    while st and st[-1][1] >= c:
                        bs, hh = st.pop(); en = max(en, hh * (i - bs)); bas = bs
                    st.append((bas, c))
            bos = en; top = nx * ny
            out.append(bos / top)
    return out

if __name__ == '__main__':
    esik = 0.25; T = B = 0
    for pdf in sys.argv[1:]:
        o = oranlar(pdf); kotu = [(i + 1, round(v, 2)) for i, v in enumerate(o) if v > esik]
        T += len(o); B += len(kotu)
        print('%s: %d sayfa, ortalama en büyük boş dikdörtgen %.2f, >%.2f boş: %d  %s' % (pathlib.Path(pdf).name, len(o), sum(o) / len(o), esik, len(kotu), kotu[:25]))
    print('TOPLAM %d sayfa, çeyrekten fazla boş: %d (%.1f%%)' % (T, B, 100 * B / max(T, 1)))
