"""
Tashih sınamaları.

    python3 docs/kaynak/test_tashih.py

Sınanan:

  1. Her tashih kaydı kaynak metinde **tam olarak bir kere** eşleşiyor.
     (Bu, "düzeltme yanlış yere uygulandı" ihtimalini kapatır.)
  2. Hiçbir tashih numarası tekrarlanmıyor.
  3. Tashihli nüshalar yapı denetiminden geçiyor.
  4. **Kaynak** nüshalardaki derlemeyi kıran hatalar tashihli nüshalarda
     KALMIYOR -- yani tashih fiilen işe yarıyor.
  5. 41-meleke nüshası kendi iddiasını (11 denklem/meleke) sağlıyor.
  6. Cetvel, kayıttaki her tashihi içeriyor.
"""
from __future__ import annotations

import os
import sys
import traceback
from typing import Callable, List

BURASI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURASI)

import tashih as X          # noqa: E402
import tex_denetle as D     # noqa: E402


def _oku(ad: str, dizin: str = BURASI) -> str:
    with open(os.path.join(dizin, ad), encoding="utf-8") as f:
        return f.read()


def test_her_tashih_tam_bir_kere_eslesiyor():
    for t in X.T:
        for ad in t.dosyalar:
            n = _oku(ad).count(t.eski)
            assert n == 1, ("T%s (%s) %s dosyasında %d kere eşleşti"
                            % (t.no, t.yer, ad, n))


def test_numaralar_tekrarsiz():
    nolar = [t.no for t in X.T]
    assert len(nolar) == len(set(nolar)), "tekrarlanan tashih numarası"


def test_her_tashih_gerekce_tasiyor():
    for t in X.T:
        # gerekçe ya müstakil olarak yazılmış olmalı, ya da başka bir
        # tashihe atıf yapmalı ("Aynı sebep (bkz. Tn)") -- aynı hatanın
        # birden çok nüshadaki yazılışı için tekrar yazmak gereksizdir
        assert len(t.sebep) > 40 or "bkz. T" in t.sebep, (t.no, t.sebep)
        assert t.tur in ("tip", "boyut", "isaret", "mantik", "erisilmez",
                         "ozdes-sifir", "tanimsiz", "yapi", "sağlamlık"), t.tur


def test_tashihli_nushalar_yapi_denetiminden_geciyor():
    hedef = os.path.join(BURASI, "tashihli")
    assert os.path.isdir(hedef), "önce `python3 docs/kaynak/tashih.py` koşun"
    for ad in X.DOSYALAR:
        yol = os.path.join(hedef, ad.replace(".tex", "_tashihli.tex"))
        bulgular = D.dosya_denetle(yol)
        assert not bulgular, (ad, bulgular)


def test_derlemeyi_kiran_hatalar_gideriliyor():
    """Kaynakta VAR, tashihlide YOK."""
    for ad in (X.MIZAN, X.ZEYL):
        kaynak = D.denetle(_oku(ad))
        assert kaynak, "%s'te beklenen yapı hatası bulunamadı" % ad
        tashihli = D.denetle(_oku(ad.replace(".tex", "_tashihli.tex"),
                                  os.path.join(BURASI, "tashihli")))
        assert not tashihli, (ad, tashihli)
    # markdown başlığı sızıntısı da gitmiş olmalı
    for ad in (X.MIZAN, X.ZEYL):
        assert "\\##" in _oku(ad), ad
        assert "\\##" not in _oku(ad.replace(".tex", "_tashihli.tex"),
                                  os.path.join(BURASI, "tashihli")), ad


def test_41_meleke_kendi_iddiasini_sagliyor():
    """Metin 'her melekede 11 denklem' diyor; tashihliden sonra doğru mu?"""
    metin = _oku(X.MELEKE.replace(".tex", "_tashihli.tex"),
                 os.path.join(BURASI, "tashihli"))
    assert D.denklem_sayisi(metin) == 451, D.denklem_sayisi(metin)
    import re
    parcalar = re.split(r"\\subsection\{", metin)[1:]
    assert len(parcalar) == 41, len(parcalar)
    for p in parcalar:
        n = D.denklem_sayisi("\\subsection{" + p)
        assert n == 11, (p.split("}")[0], n)
    # kaynakta böyle DEĞİLDİ -- tashihin bir şey değiştirdiğinin delili
    assert D.denklem_sayisi(_oku(X.MELEKE)) == 416


def test_cetvel_butun_tashihleri_iceriyor():
    cetvel = X.cetvel()
    for t in X.T:
        assert ("### T%s " % t.no) in cetvel, t.no
    assert "**%d**" % len(X.T) in cetvel


def test_hicbir_dosya_tashihsiz_kalmadi():
    uygulanan = {ad: 0 for ad in X.DOSYALAR}
    for t in X.T:
        for ad in t.dosyalar:
            uygulanan[ad] += 1
    bos = [ad for ad, n in uygulanan.items() if n == 0]
    assert not bos, bos


def _sinamalar() -> List[Callable[[], None]]:
    g = globals()
    return [g[a] for a in sorted(g) if a.startswith("test_") and callable(g[a])]


def main() -> int:
    gecen, kalan = 0, []
    for f in _sinamalar():
        try:
            f()
            print("  ✓ %s" % f.__name__)
            gecen += 1
        except Exception:
            print("  ✗ %s" % f.__name__)
            traceback.print_exc()
            kalan.append(f.__name__)
    print("\n%d geçti, %d kaldı  (%d sınama, %d tashih)"
          % (gecen, len(kalan), gecen + len(kalan), len(X.T)))
    return 1 if kalan else 0


if __name__ == "__main__":
    raise SystemExit(main())
