"""JPEG sayfaları A3 PDF'e gömer. Kullanım: python3 a3_pdf_yaz.py <sayfa_klasörü> <çıktı.pdf>

Her JPEG olduğu gibi (yeniden kodlamadan) DCTDecode nesnesi olarak yazılır; bellekte
tüm sayfa tutulmaz. Sayfalar A3 dikey (842 x 1191 pt) ve üstten hizalıdır.
"""
import glob
import os
import struct
import sys

A3_W, A3_H = 842.0, 1191.0


def jpeg_boyutu(yol):
    with open(yol, 'rb') as f:
        veri = f.read(2)
        if veri != b'\xff\xd8':
            raise ValueError(f'JPEG değil: {yol}')
        while True:
            isaret = f.read(4)
            if len(isaret) < 4:
                raise ValueError(f'Boyut bulunamadı: {yol}')
            uzunluk = struct.unpack('>H', isaret[2:4])[0]
            if isaret[1] in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack('>HH', f.read(5)[1:5])
                return w, h
            f.seek(uzunluk - 2, 1)


def main():
    klasor, cikti = sys.argv[1], sys.argv[2]
    sayfalar = sorted(glob.glob(os.path.join(klasor, 'p*.jpg')))
    if not sayfalar:
        raise SystemExit(f'JPEG sayfa yok: {klasor}')
    nesneler = []  # her nesne bayt dizisi; sıra: 1 katalog, 2 sayfalar, sonra her sayfa için 3 sayfa + 1 resim + 1 içerik
    sayfa_kimlikleri = []
    gövde = bytearray()
    konumlar = []

    def ekle(bayt):
        nesneler.append(bytes(bayt))
        return len(nesneler)

    ekle(b'')  # 1: katalog (sonra doldurulur)
    ekle(b'')  # 2: sayfalar ağacı (sonra doldurulur)
    for yol in sayfalar:
        w, h = jpeg_boyutu(yol)
        olcek = A3_W / w
        goruntu_h = h * olcek
        if goruntu_h > A3_H:
            raise SystemExit(f'Sayfa A3 yüksekliğini aşıyor: {yol}')
        with open(yol, 'rb') as f:
            jpg = f.read()
        resim_id = ekle(b'<< /Type /XObject /Subtype /Image /Width %d /Height %d '
                        b'/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n'
                        % (w, h, len(jpg)) + jpg + b'\nendstream')
        icerik = ('q %.4f 0 0 %.4f 0 %.4f cm /Im%d Do Q' % (A3_W, goruntu_h, A3_H - goruntu_h, resim_id)).encode()
        icerik_id = ekle(b'<< /Length %d >>\nstream\n' % len(icerik) + icerik + b'\nendstream')
        sayfa_id = ekle(b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.2f %.2f] '
                        b'/Resources << /XObject << /Im%d %d 0 R >> >> /Contents %d 0 R >>'
                        % (A3_W, A3_H, resim_id, resim_id, icerik_id))
        sayfa_kimlikleri.append(sayfa_id)
    nesneler[0] = b'<< /Type /Catalog /Pages 2 0 R >>'
    nesneler[1] = ('<< /Type /Pages /Kids [%s] /Count %d >>'
                   % (' '.join('%d 0 R' % k for k in sayfa_kimlikleri), len(sayfa_kimlikleri))).encode()

    with open(cikti, 'wb') as f:
        f.write(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
        for no, nesne in enumerate(nesneler, start=1):
            konumlar.append(f.tell())
            f.write(b'%d 0 obj\n' % no + nesne + b'\nendobj\n')
        xref = f.tell()
        f.write(b'xref\n0 %d\n0000000000 65535 f \n' % (len(nesneler) + 1))
        for k in konumlar:
            f.write(b'%010d 00000 n \n' % k)
        f.write(b'trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % (len(nesneler) + 1, xref))
    print(f'PDF: {cikti} ({len(sayfalar)} sayfa)')


if __name__ == '__main__':
    main()
