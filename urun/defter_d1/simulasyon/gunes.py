import math

import guc


def panel_kur(p, hucre_verimi):
    g = p["gunes"]
    alan_m2 = g["arka_alan_mm"][0] * g["arka_alan_mm"][1] / 1e6 * g["dolgu_orani"]
    n = g["seri_serit"]
    nvt = g["ideallik"] * g["sicaklik_gerilimi_v"]
    voc_hucre = g["voc_hucre_v"]
    voc_n = voc_hucre / nvt
    dolgu_faktoru = (voc_n - math.log(voc_n + 0.72)) / (voc_n + 1.0)
    guc_stc = hucre_verimi * 1000.0 * alan_m2
    voc_toplam = n * voc_hucre
    isc_stc = guc_stc / (dolgu_faktoru * voc_toplam)
    return {
        "alan_m2": alan_m2, "n": n, "nvt": nvt, "voc_hucre": voc_hucre,
        "dolgu_faktoru": dolgu_faktoru, "guc_stc_w": guc_stc,
        "voc_stc_v": voc_toplam, "isc_stc_a": isc_stc,
    }


def voc_v(panel, isinim):
    if isinim <= 0:
        return 0.0
    return panel["n"] * (panel["voc_hucre"] + panel["nvt"] * math.log(isinim / 1000.0))


def akim_a(panel, isinim, v):
    if isinim <= 0:
        return 0.0
    voc = voc_v(panel, isinim)
    if voc <= 0 or v >= voc:
        return 0.0
    isc = panel["isc_stc_a"] * isinim / 1000.0
    vt_toplam = panel["n"] * panel["nvt"]
    i0 = isc / (math.exp(voc / vt_toplam) - 1.0)
    return max(0.0, isc - i0 * (math.exp(v / vt_toplam) - 1.0))


def en_yuksek_guc_w(panel, isinim, adim=0.01):
    voc = voc_v(panel, isinim)
    en_iyi = 0.0
    v = 0.0
    while v < voc:
        en_iyi = max(en_iyi, v * akim_a(panel, isinim, v))
        v += adim
    return en_iyi


def dpm_pile_giren_w(p, panel, isinim, pil_gerilimi_v):
    v_dpm = p["gunes"]["dpm_gerilimi_v"]
    if voc_v(panel, isinim) <= v_dpm:
        return 0.0
    akim = akim_a(panel, isinim, v_dpm)
    return akim * pil_gerilimi_v


def mppt_pile_giren_w(p, panel, isinim):
    return en_yuksek_guc_w(panel, isinim) * p["gunes"]["mppt_verimi"]


def gunluk_enerji_wh(p, panel, yontem, pil_gerilimi_v=3.7):
    g = p["gunes"]
    toplam = 0.0
    for senaryo, isinim in g["isinim_w_m2"].items():
        saat = g["gun_saat"][senaryo]
        if yontem == "dpm":
            w = dpm_pile_giren_w(p, panel, isinim, pil_gerilimi_v)
        else:
            w = mppt_pile_giren_w(p, panel, isinim)
        toplam += w * saat
    return toplam


def rapor(p):
    satirlar = []
    for verim in p["gunes"]["hucre_verimi_senaryolari"]:
        panel = panel_kur(p, verim)
        satirlar.append("HÜCRE VERİMİ %.0f%%: alan %.4f m2, 9 şerit seri, Voc %.2f V, Isc(STC) %.3f A, tepe güç(STC) %.2f W, doluluk faktörü %.3f" % (
            verim * 100, panel["alan_m2"], panel["voc_stc_v"], panel["isc_stc_a"], panel["guc_stc_w"], panel["dolgu_faktoru"]))
        satirlar.append("  %-24s %8s %10s %10s" % ("ışıma senaryosu", "W/m2", "DPM (W)", "MPPT (W)"))
        for senaryo, isinim in p["gunes"]["isinim_w_m2"].items():
            satirlar.append("  %-24s %8.1f %10.4f %10.4f" % (
                senaryo, isinim, dpm_pile_giren_w(p, panel, isinim, 3.7), mppt_pile_giren_w(p, panel, isinim)))
        dpm = gunluk_enerji_wh(p, panel, "dpm")
        mppt = gunluk_enerji_wh(p, panel, "mppt")
        tuketim = guc.gun_tuketimi_wh(p)
        satirlar.append("  Günlük toplanan: DPM %.3f Wh, MPPT %.3f Wh; günlük tüketim %.2f Wh -> karşılama DPM %.0f%%, MPPT %.0f%%" % (
            dpm, mppt, tuketim, 100 * dpm / tuketim, 100 * mppt / tuketim))
        satirlar.append("")
    return "\n".join(satirlar)


if __name__ == "__main__":
    print(rapor(guc.parametreleri_yukle()))
