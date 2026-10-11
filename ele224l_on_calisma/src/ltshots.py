import math
from common import ROOT, fmt
import os

LT = os.path.join(ROOT, "lt_shot")
M = "−"
SERIAL = "TOBB-7K3Q-0421"


def _n(x, nd=5):
    s = ("%." + str(nd) + "g") % x
    return s.replace("-", M)


def R(cur, xtxt, quant, lt, ng, unit, kind="rel"):
    """kind: rel -> % fark; abs -> mutlak fark (dB, derece)."""
    if kind == "rel":
        diff = "%+.3f%%" % (100 * (lt - ng) / abs(ng))
    else:
        diff = "%+.3f %s" % (lt - ng, unit)
    return [cur, xtxt, quant, "%s %s" % (_n(lt), unit), "%s %s" % (_n(ng), unit), diff]


def ac_rows(f1, m1, p1, m1n, p1n, f2, m2, p2, m2n, p2n):
    r = []
    for i, (f, m, p, mn, pn) in enumerate([(f1, m1, p1, m1n, p1n), (f2, m2, p2, m2n, p2n)]):
        r.append(R(str(i + 1), "f = %s" % f, "$|V_O|$", m, mn, "dB", "abs"))
        r.append(R(str(i + 1), "f = %s" % f, "$\\angle V_O$", p, math.degrees(pn), "°", "abs"))
    return r


SHOTS = {
    "e1_dc": ("lt_e1_dc_1n4148.png",
              "LTspice DC sweep of the half-wave rectifier with the 1N4148 model: diode current $I(D1)$ versus the source voltage $V_S$ (x-axis); device serial number visible in the plot",
              [R("1", "$V_S$ = 0.65104 V", "$I_D$", 152.12024, 152.1210, "µA"),
               R("2", "$V_S$ = 5 V", "$I_D$", 4.3467707, 4.34677, "mA")]),
    "e1_tran": ("lt_e1_tran.png",
                "LTspice transient simulation of the rectifier ($V_S$: green, $V_O$: blue; 1N4148 model, 5 V amplitude, 1 kHz)",
                [R("1", "t = 249.68 µs", "$V_O$", 4.3466134, 4.346702, "V"),
                 R("2", "t = 749.03 µs", "$V_O$", 2.0290635e-6, -2.837769e-6, "V", "abs")]),
    "e2_bs_dc": ("lt_e2_bs_dc.png",
                 "LTspice DC sweep of the BS170 bias circuit: drain current $I_D$ versus the source voltage $V_1$ of the gate divider",
                 [R("1", "$V_1$ = 5.0013 V", "$I_D$", 153.99938, 153.9993, "mA"),
                  R("2", "$V_1$ = 10.0026 V", "$I_D$", 900.05129, 900.0532, "mA")]),
    "e2_inv_dc": ("lt_e2_inv_dc.png",
                  "LTspice voltage transfer characteristic of the CMOS inverter (BS170/BS250): $V_{out}$ versus $V_{in}$",
                  [R("1", "$V_{in}$ = 2.2016 V", "$V_{out}$", 2.4988378, 2.499386, "V"),
                   R("2", "$V_{in}$ = 3.5 V", "$V_{out}$", 1.6637598e-3, 1.663760e-3, "V")]),
    "e2_inv_tran": ("lt_e2_inv_tran.png",
                    "LTspice transient response of the CMOS inverter ($V_{in}$: green, $V_{out}$: blue); the cursors read $V_{out}$",
                    [R("1", "t = 250.81 µs", "$V_{out}$", 101.81388e-9, 1.017825e-7, "V", "abs"),
                     R("2", "t = 750.49 µs", "$V_{out}$", 5.9999332, 6.0, "V")]),
    "e3_tran_1": ("lt_e3_tran_1z.png",
                  "LTspice transient result of the common-source amplifier with the bypass capacitor $C_S$ ($V_{in}$: green, $V_O$: blue); the time axis starts at 7 ms (data saved from 7 ms to 7.5 ms)",
                  [R("1", "t = 7 ms + 50.16 µs", "$V_O$", 761.19876, 761.3862, "mV"),
                   R("2", "t = 7 ms + 100 µs", "$V_O$", -781.77947, -781.8575, "mV")]),
    "e3_tran_0": ("lt_e3_tran_0z.png",
                  "LTspice transient result of the common-source amplifier without the bypass capacitor ($V_{in}$: green, $V_O$: blue); the time axis starts at 7 ms",
                  [R("1", "t = 7 ms + 50.16 µs", "$V_O$", 18.3892, 18.38001, "mV"),
                   R("2", "t = 7 ms + 100 µs", "$V_O$", -17.826432, -17.82844, "mV")]),
    "e3_ac_1": ("lt_e3_ac_1.png",
                "LTspice AC analysis of the common-source amplifier with $C_S$ (magnitude and phase of $V_O$ for $V_i=1$ V)",
                ac_rows("10.0306 kHz", 17.844976, -85.413093, 17.84460, -1.490700, "998.48 Hz", -10.21111, -35.425962, -10.21149, -6.182919e-1)),
    "e3_ac_0": ("lt_e3_ac_0.png",
                "LTspice AC analysis of the common-source amplifier without $C_S$",
                ac_rows("10.0306 kHz", -4.8958442, -161.77636, -4.895855, -2.823515, "998.48 Hz", -14.841371, -88.545506, -14.84160, -1.545393)),
    "e3_mirror": ("lt_e3_mirror_dc.png",
                  "LTspice DC sweep of the current mirror: reference-branch current $I_D(M1)$ (blue) and output current $I_D(M2)$ (green) versus $V_i$; the cursors read $I_D(M1)$",
                  [R("1", "$V_i$ = 5 V", "$I_D(M1)$", 3.8864687, 3.886870, "mA"),
                   R("2", "$V_i$ = 15 V", "$I_D(M1)$", 18.131161, 18.13116, "mA")]),
    "e5_ce_1": ("lt_e5_ce_ac_1.png",
                "LTspice AC analysis of the common-emitter amplifier with the emitter bypass capacitor $C_E$",
                ac_rows("99.695 kHz", 34.41899, -107.40747, 34.41968, -1.874229, "998.48 Hz", -4.408854, -77.108519, -4.408974, -1.345785)),
    "e5_ce_0": ("lt_e5_ce_ac_0.png",
                "LTspice AC analysis of the common-emitter amplifier without $C_E$",
                ac_rows("99.695 kHz", 6.9373008, -178.31297, 6.937444, -3.112146, "998.48 Hz", -4.6228868, -90.804002, -4.622991, -1.584814)),
    "e5_cc": ("lt_e5_cc_ac.png",
              "LTspice AC analysis of the common-collector (emitter-follower) amplifier",
              ac_rows("100.458 kHz", -0.06732786, 4.4149627, -0.06732945, 7.706116e-2, "996.96 Hz", -18.404808, 109.99758, -18.40537, 1.919850)),
}


def add(d, key, label, width=15.5, tr=False):
    f, cap, rows = SHOTS[key]
    path = os.path.join(LT, f)
    if tr:
        cap = cap + " (LTspice; cihaz seri no: %s)" % SERIAL
    else:
        cap = cap + " (device serial number: %s)" % SERIAL
    first = not getattr(d, "_ltn", 0)
    d._ltn = getattr(d, "_ltn", 0) + 1
    if tr:
        if first:
            d.p("Aynı benzetim LTspice ile de koşturuldu; imleçli dalga biçimi penceresi [[f:%s]]'de, imleç değerleri ile aynı x'te ngspice değerlerinin karşılaştırması [[t:%s_c]]'de verilmiştir. Sayıların birbirini tutması sonucun simülatöre bağlı olmadığını gösterir." % (label, label))
        else:
            d.p("LTspice sonucu [[f:%s]]'de, imleç karşılaştırması [[t:%s_c]]'de verilmiştir." % (label, label))
    else:
        if first:
            d.p("The simulation was repeated in LTspice; the waveform window with the cursors is shown in [[f:%s]], and the cursor readings are compared with the ngspice values at the same x in [[t:%s_c]]. The agreement shows that the result does not depend on the simulator." % (label, label))
        else:
            d.p("The LTspice result for this case is shown in [[f:%s]] and the cursor comparison is given in [[t:%s_c]]." % (label, label))
    d.fig(label, path, cap, width)
    hdr = ["Cursor", "x coordinate", "Quantity", "LTspice", "ngspice", "Difference"] if not tr else \
          ["İmleç", "x koordinatı", "Büyüklük", "LTspice", "ngspice", "Fark"]
    d.tab(label + "_c", hdr, rows,
          ("Cursor coordinates read in [[f:%s]] and the ngspice values at the same x" % label) if not tr else
          ("[[f:%s]] imleç değerleri ve aynı x'te ngspice değerleri" % label),
          widths=[1.4, 3.4, 2.2, 3.0, 3.0, 2.6], size=8.5)
