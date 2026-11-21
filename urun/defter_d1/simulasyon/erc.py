import copy
import json
import pathlib

import guc

NETLIST = guc.KOK / "donanim" / "blok_netlist.json"


def netlist_yukle(yol=None):
    yol = pathlib.Path(yol) if yol else NETLIST
    return json.loads(yol.read_text(encoding="utf-8"))


def ray_akimi_ma(nl, ray_adi):
    toplam = sum(y["ma_maks"] for y in nl["yukler"] if y["ray"] == ray_adi)
    for ad, ray in nl["raylar"].items():
        if ray.get("besleme") == ray_adi:
            toplam += ray_akimi_ma(nl, ad)
    return toplam


def kontrol_et(nl):
    bulgular = []

    def ekle(ad, tamam, mesaj):
        bulgular.append((ad, bool(tamam), mesaj))

    for ad, ray in nl["raylar"].items():
        if "max_ma" in ray:
            gerekli = ray_akimi_ma(nl, ad)
            sinir = 0.8 * ray["max_ma"]
            ekle("ray_akimi:" + ad, gerekli <= sinir,
                 "%s: en kötü yük %d mA, sınır (yüzde 80) %d mA" % (ad, gerekli, sinir))

    for y in nl["yukler"]:
        ray = nl["raylar"].get(y["ray"])
        if ray is None:
            ekle("ray_yok:" + y["blok"], False, "%s: %s rayı tanımlı değil" % (y["blok"], y["ray"]))
            continue
        uygun = y["vmin"] <= ray["v_min"] and ray["v_max"] <= y["vmax"]
        ekle("gerilim:" + y["blok"], uygun,
             "%s: ray %s–%s V, blok %s–%s V" % (y["blok"], ray["v_min"], ray["v_max"], y["vmin"], y["vmax"]))

    mcu_vdd = nl["raylar"]["V3V3"]["v_max"]
    for y in nl["yukler"]:
        if y.get("mcu_ile_arayuz"):
            ray = nl["raylar"][y["ray"]]
            gerekli = ray["v_max"] < mcu_vdd
            var = y["blok"] in nl.get("seviye_cevirici", [])
            ekle("seviye:" + y["blok"], (not gerekli) or var,
                 "%s: ray %.2f V, MCU %.2f V; seviye çevirici %s" % (
                     y["blok"], ray["v_max"], mcu_vdd, "var" if var else "yok"))

    pin_toplam = sum(a["pin"] for a in nl["arayuzler"])
    sinir = nl["mcu"]["gpio_toplam"] * (1.0 - nl["mcu"]["gpio_pay_birakma"])
    ekle("gpio_sayisi", pin_toplam <= sinir,
         "ihtiyaç %d pin, sınır %.1f pin (toplam %d, pay %.0f%%)" % (
             pin_toplam, sinir, nl["mcu"]["gpio_toplam"], nl["mcu"]["gpio_pay_birakma"] * 100))

    for veriyolu, cihazlar in nl["i2c_adresleri"].items():
        adresler = [c["adres"] for c in cihazlar]
        ekle("i2c_adres:" + veriyolu, len(adresler) == len(set(adresler)),
             "%s adresleri: %s" % (veriyolu, ", ".join(adresler)))

    usb = nl["usb"]
    ekle("usb_cc", usb["cc1_rd_kohm"] == 5.1 and usb["cc2_rd_kohm"] == 5.1,
         "CC1 %.1f kΩ, CC2 %.1f kΩ (alıcı için 5,1 kΩ gerekir)" % (usb["cc1_rd_kohm"], usb["cc2_rd_kohm"]))
    ekle("usb_esd", usb["esd_korumasi"], "USB hatlarında ESD koruması")

    ps = nl["pil_ve_sarj"]
    ekle("pil_koruma", ps["koruma_devresi"], "pil koruma devresi (aşırı şarj, aşırı deşarj, kısa devre)")
    ekle("gunes_diyodu", ps["gunes_girisi_diyodu"], "güneş girişinde ters akım diyodu")
    ekle("sarj_ilim", ps["ilim_direnci"], "şarj akımı sınırlama direnci")

    b = nl["bellek"]
    gerekli = b["cerceve_tamponu_adet"] * b["genislik"] * b["yukseklik"] * b["bit_derinligi"] // 8
    ekle("sdram_kapasite", gerekli <= b["sdram_bayt"],
         "çerçeve tamponları %d bayt, SDRAM %d bayt" % (gerekli, b["sdram_bayt"]))
    return bulgular


def rapor(nl):
    satirlar = []
    basarisiz = 0
    for ad, tamam, mesaj in kontrol_et(nl):
        satirlar.append("%-4s %s" % ("TAMAM" if tamam else "RED", mesaj))
        if not tamam:
            basarisiz += 1
    satirlar.append("")
    satirlar.append("Toplam kontrol: %d, reddedilen: %d" % (len(kontrol_et(nl)), basarisiz))
    return "\n".join(satirlar)


def bozuk_kopya(nl, degisiklik):
    kopya = copy.deepcopy(nl)
    degisiklik(kopya)
    return kopya


if __name__ == "__main__":
    print(rapor(netlist_yukle()))
