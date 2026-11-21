import re
import subprocess
import sys
import tempfile
import pathlib

from pypdf import PdfReader


def kontrol(ad, kosul, mesaj=""):
    durum = "TAMAM" if kosul else "RED"
    print("%-5s %s %s" % (durum, ad, mesaj))
    return 0 if kosul else 1


def ham_xref_denetimi(ham):
    hatalar = 0
    konum = int(re.search(rb"startxref\n(\d+)\n%%EOF\n$", ham).group(1))
    hatalar += kontrol("xref başlangıcı", ham[konum:konum + 4] == b"xref")
    satirlar = ham[konum:].split(b"\n")
    toplam = int(satirlar[1].split()[1])
    giris_sayisi = 0
    for no in range(1, toplam):
        giris = satirlar[3 + no - 1]
        ofset = int(giris[:10])
        beklenen = ("%d 0 obj" % no).encode()
        if ham[ofset:ofset + len(beklenen)] != beklenen:
            hatalar += kontrol("nesne ofseti %d" % no, False)
        giris_sayisi += 1
    hatalar += kontrol("xref giriş sayısı", giris_sayisi == toplam - 1, "%d nesne" % giris_sayisi)
    uzunluklar = re.findall(rb"/Length (\d+) >>\nstream\n", ham)
    for u in uzunluklar:
        u = int(u)
        baslangic = ham.index(b"stream\n", ham.index(b"/Length " + str(u).encode())) + 7
        bitis_isareti = ham.find(b"endstream", baslangic)
        gercek = bitis_isareti - baslangic
        if gercek != u and gercek != u + 1:
            hatalar += kontrol("akış uzunluğu", False, "bildirilen %d, gerçek %d" % (u, gercek))
    hatalar += kontrol("akış uzunlukları bildirilenle uyuşuyor", True)
    return hatalar


def main():
    pdf_yolu = sys.argv[1]
    jpeg_yolu = sys.argv[2]
    ham = pathlib.Path(pdf_yolu).read_bytes()
    jpeg = pathlib.Path(jpeg_yolu).read_bytes()
    hatalar = 0

    okuyucu = PdfReader(pdf_yolu, strict=True)
    hatalar += kontrol("sayfa sayısı", len(okuyucu.pages) == 2)
    kutu = okuyucu.pages[0].mediabox
    hatalar += kontrol("sayfa boyutu", abs(float(kutu.width) - 436.8) < 0.01 and abs(float(kutu.height) - 262.08) < 0.01,
                       "%sx%s pt" % (kutu.width, kutu.height))

    icerik = okuyucu.pages[0].get_contents().get_data().decode("ascii")
    hatalar += kontrol("ilk strok başlangıcı", "54.60 218.40 m" in icerik)
    hatalar += kontrol("üç strok", icerik.count(" m\n") == 3 and icerik.count("S\n") == 3)
    hatalar += kontrol("çizgi komutları", icerik.count(" l\n") == 4, "%d" % icerik.count(" l\n"))
    hatalar += kontrol("çizgi ayarı", "0 0 0 RG 1.20 w 1 J 1 j" in icerik)

    ikinci = okuyucu.pages[1]
    nesneler = ikinci["/Resources"]["/XObject"]
    resim = nesneler["/Im0"].get_object()
    hatalar += kontrol("resim boyutu", int(resim["/Width"]) == 64 and int(resim["/Height"]) == 48)
    hatalar += kontrol("resim süzgeci", resim["/Filter"] == "/DCTDecode")
    hatalar += kontrol("resim baytları aynen gömülü", resim._data == jpeg)
    hatalar += kontrol("birinci sayfada resim yok", "/XObject" not in okuyucu.pages[0]["/Resources"])

    hatalar += ham_xref_denetimi(ham)

    with tempfile.TemporaryDirectory() as gecici:
        onek = pathlib.Path(gecici) / "sayfa"
        sonuc = subprocess.run(["pdftoppm", "-r", "72", "-gray", "-f", "1", "-l", "1", "-singlefile", pdf_yolu, str(onek)],
                               capture_output=True)
        hatalar += kontrol("pdftoppm çizimi", sonuc.returncode == 0, sonuc.stderr.decode()[:80])
        if sonuc.returncode == 0:
            pgm = (pathlib.Path(str(onek) + ".pgm")).read_bytes()
            ust = re.match(rb"P5\s+(\d+)\s+(\d+)\s+255\s", pgm)
            gen, yuk = int(ust.group(1)), int(ust.group(2))
            veri = pgm[ust.end():]
            def piksel(x, y):
                return veri[y * gen + x]
            karanlik = sum(1 for b in veri if b < 128)
            hatalar += kontrol("çizim boş değil", karanlik > 50, "%d koyu piksel" % karanlik)
            ornek_x = int(150 * 0.546)
            ornek_y = int(85 * 0.546)
            civar = [piksel(x, y) for x in range(ornek_x - 2, ornek_x + 3) for y in range(ornek_y - 3, ornek_y + 3)]
            hatalar += kontrol("birinci strokun üstü koyu", min(civar) < 100, "en koyu %d" % min(civar))
            bos_x, bos_y = int(400 * 0.546), int(240 * 0.546)
            hatalar += kontrol("boş bölge beyaz", piksel(bos_x, bos_y) > 240)
            nokta_x, nokta_y = int(50 * 0.546), int(50 * 0.546)
            civar = [piksel(x, y) for x in range(nokta_x - 2, nokta_x + 3) for y in range(nokta_y - 2, nokta_y + 3)]
            hatalar += kontrol("tek noktalı strok çiziliyor", min(civar) < 128, "en koyu %d" % min(civar))

    print("PDF doğrulama: %d hata" % hatalar)
    sys.exit(1 if hatalar else 0)


main()
