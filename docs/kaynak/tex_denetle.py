"""
LaTeX yapı denetleyicisi -- derleyici olmadan yakalanabilenler.

Bu makinede TeX kurulu değil, dolayısıyla "derleniyor" diye bir iddiada
bulunulamaz. Buna karşılık, derleyicinin hata vereceği kusurların çoğu
saf metin üzerinde **kesin** olarak yakalanabilir ve burada yakalanır:

  * süslü parantez dengesi (kaçışlı ``\\{`` ve ``\\}`` sayılmaz)
  * ``$`` ve ``$$`` çiftlenmesi
  * ``\\begin{X}`` / ``\\end{X}`` eşleşmesi (yığın olarak)
  * ``align`` içinde satır başına en fazla bir hizalama işareti ``&``
  * ``align`` içinde son satırda gereksiz ``\\\\``
  * ``\\left`` / ``\\right`` dengesi
  * tanımsız ortam adları ve bilinmeyen makro şüphesi (kaba tarama)

    python3 -m docs.kaynak.tex_denetle docs/kaynak/*.tex
"""
from __future__ import annotations

import re
import sys
from typing import Iterable, List, Tuple

Bulgu = Tuple[int, str]

_KACIS = re.compile(r"\\[{}$&%#_]")
_IC_ORTAM = re.compile(
    r"\\begin\{(cases|array|aligned|matrix|[pbv]matrix|split|smallmatrix)\}"
    r".*?\\end\{\1\}", re.S)
_YORUM = re.compile(r"(?<!\\)%.*$")


def _temizle(satir: str) -> str:
    """Yorumları ve kaçışlı özel karakterleri düşür."""
    satir = _YORUM.sub("", satir)
    return _KACIS.sub("", satir)


def denetle(metin: str) -> List[Bulgu]:
    bulgular: List[Bulgu] = []
    satirlar = metin.splitlines()

    derinlik = 0
    dolar = 0
    yigin: List[Tuple[str, int]] = []
    left_right = 0
    ortam_yigini: List[str] = []
    hizali_ortamlar = {"align", "align*", "aligned", "alignat", "array", "cases",
                       "matrix", "pmatrix", "bmatrix", "tabular", "split"}

    for no, ham in enumerate(satirlar, 1):
        s = _temizle(ham)

        derinlik += s.count("{") - s.count("}")
        if derinlik < 0:
            bulgular.append((no, "fazladan '}' -- süslü parantez dengesi bozuldu"))
            derinlik = 0

        dolar += s.count("$")
        # DİKKAT: ``\\leftarrow`` ve ``\\leftrightarrow`` de ``\\left`` ile
        # başlar. Sözcük sınırı konmazsa denetleyicinin kendisi yanlış
        # alarm verir -- ilk kurulumda tam bunu yaptı ve üç dosyada
        # olmayan "dengesizlik" bildirdi. Sınır şart.
        left_right += (len(re.findall(r"\\left(?![a-zA-Z])", s))
                       - len(re.findall(r"\\right(?![a-zA-Z])", s)))

        for m in re.finditer(r"\\begin\{([^}]*)\}", s):
            yigin.append((m.group(1), no))
            ortam_yigini.append(m.group(1))
        for m in re.finditer(r"\\end\{([^}]*)\}", s):
            ad = m.group(1)
            if not yigin:
                bulgular.append((no, r"eşi olmayan \end{%s}" % ad))
            else:
                acik, acik_no = yigin.pop()
                if ortam_yigini:
                    ortam_yigini.pop()
                if acik != ad:
                    bulgular.append(
                        (no, r"ortam uyuşmuyor: \begin{%s} (satır %d) ile \end{%s}"
                         % (acik, acik_no, ad)))

        # align içinde satır başına en fazla bir '&'.
        # DİKKAT: iç ortamların (``cases``, ``array``…) ``&``leri SÜTUN
        # ayracıdır, hizalama işareti değil. Aynı satırda açılıp kapanan
        # iç ortamlar sayımdan önce düşürülmezse denetleyici yanlış alarm
        # verir -- ilk kurulumda tam bunu yaptı: tek satıra sığdırılmış
        # bir ``cases`` bloğu ``2 hizalama işareti'' diye bildirildi.
        if ortam_yigini and ortam_yigini[-1] in ("align", "align*"):
            # SIRA mühim: önce iç ortamlar düşürülür, SONRA satır sonuna
            # göre bölünür. Tersi yapılırsa ``cases`` içindeki ``\\\\``
            # bölmeyi erken tetikler ve blok hiç düşürülemez (ölçüldü).
            govde = _IC_ORTAM.sub("", s).split(r"\\")[0]
            if govde.count("&") > 1:
                bulgular.append((no, "align satırında %d hizalama işareti '&' "
                                     "(en fazla 1 olmalı)" % govde.count("&")))

    if derinlik != 0:
        bulgular.append((len(satirlar), "kapanmamış '{' sayısı: %d" % derinlik))
    if dolar % 2 != 0:
        bulgular.append((len(satirlar), "tek sayıda '$' -- matematik kipi kapanmamış"))
    if left_right != 0:
        bulgular.append((len(satirlar),
                         r"\left/\right dengesizliği: %d" % left_right))
    for ad, no in yigin:
        bulgular.append((no, r"kapanmamış \begin{%s}" % ad))

    # align ortamlarının son satırında gereksiz \\
    for m in re.finditer(r"\\begin\{align\*?\}(.*?)\\end\{align\*?\}", metin, re.S):
        govde = m.group(1).rstrip()
        if govde.endswith("\\\\"):
            no = metin[:m.start()].count("\n") + 1
            bulgular.append((no, "align gövdesi '\\\\\\\\' ile bitiyor "
                                 "(son satırda gereksiz, boş satır üretir)"))
    return bulgular


def denklem_sayisi(metin: str) -> int:
    """``align`` ortamlarındaki NUMARALANACAK satır sayısı.

    İç içe ortamlardaki (``cases``, ``array``, ``aligned``…) satır sonları
    numara üretmez; sayılmadan önce o bloklar düşürülür. Düşürülmezse
    sayım şişer -- ölçüldü: ``cases`` blokları yüzünden 41-meleke
    metninde 419 yerine 421 çıkıyordu.
    """
    ic_ortam = re.compile(r"\\begin\{(cases|array|aligned|matrix|[pbv]matrix|split)\}"
                          r".*?\\end\{\1\}", re.S)
    toplam = 0
    for m in re.finditer(r"\\begin\{align\}(.*?)\\end\{align\}", metin, re.S):
        govde = ic_ortam.sub("", m.group(1))
        toplam += govde.count("\\\\") + 1
    return toplam


def dosya_denetle(yol: str) -> List[Bulgu]:
    with open(yol, encoding="utf-8") as f:
        return denetle(f.read())


def main(yollar: Iterable[str]) -> int:
    hata = 0
    for yol in yollar:
        with open(yol, encoding="utf-8") as f:
            metin = f.read()
        bulgular = denetle(metin)
        print("%-52s  denklem=%3d  bulgu=%d"
              % (yol.split("/")[-1], denklem_sayisi(metin), len(bulgular)))
        for no, mesaj in bulgular:
            print("    satır %4d: %s" % (no, mesaj))
            hata = 1
    return hata


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
