import guc


def govde_kalinligi_mm(p, ekran="lcd"):
    k = p["kalinlik_mm"]
    ekran_mm = k["ekran_ve_dokunmatik"]["deger"] if ekran == "lcd" else k["eink_modulu_7_5"]["deger"]
    return (ekran_mm + k["yapistirma_boslugu"]["deger"] + k["kart"]["deger"]
            + k["en_yuksek_bilesen"]["deger"] + k["gunes_laminati"]["deger"] + k["kabuk_on_arka"]["deger"])


def sirt_kalinligi_mm(p):
    return p["pil"]["silindir_capi_mm"] + p["kalinlik_mm"]["kabuk_on_arka"]["deger"]


def rapor(p):
    satirlar = []
    for ekran, ad in (("lcd", "Renkli ekran (kapasitif dokunmatikli)"), ("eink", "E-ink 7,5 inç (ikinci model, dokunmatiksiz)")):
        satirlar.append("%-45s gövde %.2f mm, sırt %.2f mm" % (ad, govde_kalinligi_mm(p, ekran), sirt_kalinligi_mm(p)))
    fark = govde_kalinligi_mm(p, "lcd") - govde_kalinligi_mm(p, "eink")
    satirlar.append("Ekran seçiminin gövdeye katkısı: %.2f mm" % fark)
    return "\n".join(satirlar)


if __name__ == "__main__":
    print(rapor(guc.parametreleri_yukle()))
