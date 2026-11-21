import json
import pathlib

KOK = pathlib.Path(__file__).resolve().parent.parent


def parametreleri_yukle(yol=None):
    yol = pathlib.Path(yol) if yol else KOK / "parametreler.json"
    return json.loads(yol.read_text(encoding="utf-8"))


def mod_gucu_w(p, mod_adi, yuk_carpani=1.0):
    mod = p["modlar"][mod_adi]
    v = p["ray"]["v3v3"]
    mantik_w = sum(mod["yukler_ma"].values()) * yuk_carpani * v / 1000.0 / p["ray"]["buck_boost_verim"]
    arka_w = mod["arka_isik_w"] * yuk_carpani / p["ray"]["arka_isik_verim"]
    sabit_w = mod["sabit_mw"] * yuk_carpani / 1000.0
    return mantik_w + arka_w + sabit_w


def pil_enerjisi_wh(p):
    pil = p["pil"]
    return pil["kapasite_mah"] / 1000.0 * pil["nominal_v"] * pil["kullanilabilir_oran"]


def gun_tuketimi_wh(p, yuk_carpani=1.0):
    return sum(saat * mod_gucu_w(p, mod, yuk_carpani) for mod, saat in p["gun_profili_saat"].items())


def mod_suresi_saat(p, mod_adi, yuk_carpani=1.0):
    return pil_enerjisi_wh(p) / mod_gucu_w(p, mod_adi, yuk_carpani)


def gun_sayisi(p, yuk_carpani=1.0):
    return pil_enerjisi_wh(p) / gun_tuketimi_wh(p, yuk_carpani)


def rapor(p):
    alt, ust = p["modlar"]["belirsizlik_bandi"]
    satirlar = []
    satirlar.append("PİL ENERJİSİ (kullanılabilir): %.2f Wh" % pil_enerjisi_wh(p))
    satirlar.append("")
    satirlar.append("%-14s %10s %10s %10s %14s" % ("mod", "W (tip)", "W (alt)", "W (üst)", "süre saat (tip)"))
    for mod in p["modlar"]:
        if mod in ("yuk_isareti", "belirsizlik_bandi"):
            continue
        satirlar.append("%-14s %10.3f %10.3f %10.3f %14.1f" % (
            mod, mod_gucu_w(p, mod), mod_gucu_w(p, mod, alt), mod_gucu_w(p, mod, ust), mod_suresi_saat(p, mod)))
    satirlar.append("")
    satirlar.append("GÜN PROFİLİ (saat): %s" % json.dumps(p["gun_profili_saat"], ensure_ascii=False))
    satirlar.append("Günlük tüketim: %.2f Wh (alt %.2f, üst %.2f)" % (
        gun_tuketimi_wh(p), gun_tuketimi_wh(p, alt), gun_tuketimi_wh(p, ust)))
    satirlar.append("Güneşsiz şarjsız pil ömrü: %.1f gün (alt/üst: %.1f / %.1f)" % (
        gun_sayisi(p), gun_sayisi(p, ust), gun_sayisi(p, alt)))
    satirlar.append("24 saat sürekli ekran açık (yazma modu) ihtiyacı: %.1f Wh; pil %.1f Wh" % (
        24 * mod_gucu_w(p, "yazma"), pil_enerjisi_wh(p)))
    return "\n".join(satirlar)


if __name__ == "__main__":
    print(rapor(parametreleri_yukle()))
