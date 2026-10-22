import subprocess, sys, os
from PIL import Image, ImageChops
def goster(pcb, cikti, katmanlar, dpi=300, ayna=False):
    pdf = cikti + '.pdf'
    cmd = ['kicad-cli', 'pcb', 'export', 'pdf', '-l', katmanlar, '-o', pdf, pcb]
    if ayna: cmd.insert(4, '--mirror')
    subprocess.run(cmd, check=True, capture_output=True)
    subprocess.run(['pdftoppm', '-r', str(dpi), '-png', '-singlefile', pdf, cikti], check=True)
    im = Image.open(cikti + '.png').convert('RGB')
    bg = Image.new('RGB', im.size, (255, 255, 255))
    bb = ImageChops.difference(im, bg).getbbox()
    if bb:
        im = im.crop((max(bb[0]-10,0), max(bb[1]-10,0), bb[2]+10, bb[3]+10))
    im.save(cikti + '.png')
    os.remove(pdf)
    return im.size
if __name__ == '__main__':
    print(goster(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 300, len(sys.argv) > 5))
