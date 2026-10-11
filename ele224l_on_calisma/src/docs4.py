import numpy as np
from common import *
from docbuilder import Doc
from docs1 import n2, sci, M
import exp4
from exp4 import VCC_LIST, VBB_LIST


def vf(x, nd=4):
    return n2(x, nd)


def c3(x):
    if x == 0:
        return "0"
    t = ("%.2g" % x) if abs(x) < 0.1 else ("%.3g" % x)
    return t.replace("-", M)


def t1_tables(d, R, en=True):
    th, sp = R["t1_th"], R["t1_sp"]
    for vbb in VBB_LIST:
        hdr = ["$V_{BB}$ = %g V" % vbb + ("" if en else "")] + [("%g" % v) for v in VCC_LIST]
        hdr[0] = "$V_{CC}$ (V)"
        rows = [
            ["$V_{CE}$ calc. (V)" if en else "$V_{CE}$ el (V)"] + [c3(th[(vbb, v)][0]) for v in VCC_LIST],
            ["$I_C$ calc. (mA)" if en else "$I_C$ el (mA)"] + [c3(th[(vbb, v)][1] * 1e3) for v in VCC_LIST],
            ["$V_{CE}$ SPICE (V)"] + [c3(sp[(vbb, v)][0]) for v in VCC_LIST],
            ["$I_C$ SPICE (mA)"] + [c3(sp[(vbb, v)][1] * 1e3) for v in VCC_LIST],
        ]
        cap = ("Table 1 values for $V_{BB}$ = %g V (calculation and SPICE)" % vbb) if en else ("Föy Tablo 1, $V_{BB}$ = %g V (el hesabı ve SPICE)" % vbb)
        d.tab("t1_%g" % vbb, hdr, rows, cap, widths=[2.5] + [1.2] * 11, size=7)


def sat_cells(R):
    out = {}
    for vbb in VBB_LIST:
        out[vbb] = [v for v in VCC_LIST if R["t1_th"][(vbb, v)][3] != "active"]
    return out


def agree(R):
    th, sp = R["t1_th"], R["t1_sp"]
    res = {}
    for vbb in VBB_LIST:
        act = [v for v in VCC_LIST if th[(vbb, v)][3] == "active"]
        dv = max(abs(sp[(vbb, v)][0] - th[(vbb, v)][0]) for v in act)
        di = np.mean([100 * (sp[(vbb, v)][1] - th[(vbb, v)][1]) / th[(vbb, v)][1] for v in act])
        res[vbb] = (dv, di)
    return res


SC_ROWS = [
    ("ok", "Normal operation (reference)", "Normal çalışma (referans)"),
    ("vbb0", "$V_{BB}$ = 0 V (base supply missing)", "$V_{BB}$ = 0 V (taban kaynağı yok)"),
    ("rbopen", "$R_B$ open (or base lead not inserted)", "$R_B$ açık (ya da taban bacağı takılmamış)"),
    ("qrev", "Collector and emitter pins exchanged", "Kolektör ve emetör bacakları ters"),
    ("reopen", "$R_E$ open (emitter floating)", "$R_E$ açık (emetör havada)"),
    ("rcopen", "$R_C$ open (collector floating)", "$R_C$ açık (kolektör havada)"),
    ("vcc0", "$V_{CC}$ = 0 V (collector supply missing)", "$V_{CC}$ = 0 V (kolektör kaynağı yok)"),
    ("reshort", "$R_E$ shorted by a wire", "$R_E$ bir telle kısa devre"),
    ("rcbig", "$R_C$ = 12 k$\\Omega$ instead of 1.2 k$\\Omega$", "$R_C$ = 1,2 k$\\Omega$ yerine 12 k$\\Omega$"),
    ("ceshort", "Collector\u2013emitter short circuit", "Kolektör–emetör kısa devre"),
]


def scen_table(d, R, en=True):
    S = R["scen"]
    rows = []
    for k, e, t in SC_ROWS:
        vce, vbe, ic = S[k]
        vbe_s = "\u2248 0 (floating)" if k == "rbopen" else n2(vbe, 3)
        if k == "vbb0":
            vbe_s = "0"
        rows.append([e if en else t, n2(vce, 3) if abs(vce) > 1e-3 else "\u2248 0", vbe_s, n2(ic * 1e3, 3) if abs(ic) > 1e-6 else "0"])
    hdr = ["Condition", "$V_{CE}$ (V)", "$V_{BE}$ (V)", "$I_C$ (mA)"] if en else ["Durum", "$V_{CE}$ (V)", "$V_{BE}$ (V)", "$I_C$ (mA)"]
    cap = "SPICE results of the fault conditions in BJT biasing circuit 2 ($V_{BB}$ = 5 V, $V_{CC}$ = 12 V)" if en else "BJT kutuplama devresi 2'de ($V_{BB}$=5 V, $V_{CC}$=12 V) hata durumlarının SPICE sonuçları"
    d.tab("scen", hdr, rows, cap, widths=[7.4, 2.8, 2.8, 2.8], size=9)


def build_en(R):
    d = Doc("en")
    d.title_block([
        ("TOBB University of Economics and Technology", 14, True),
        ("Department of Electrical and Electronics Engineering", 12, False),
        ("ELE 224L \u2013 Electronic Circuits Laboratory", 12, False),
        ("Experiment 4 \u2013 Preliminary Work: BJT Circuits", 13, True),
    ], [("Name Surname", ""), ("Student ID", ""), ("Date", "")])
    th, sp = R["t1_th"], R["t1_sp"]
    c1, c1s, c2, c2s = R["c1"], R["c1_sp"], R["c2"], R["c2_sp"]
    ag = agree(R)
    sc = sat_cells(R)
    S = R["scen"]

    d.h(1, "Introduction")
    d.h(2, "Objective of the Experiment")
    d.p("The objective of this experiment is to investigate the current\u2013voltage characteristics of the bipolar junction transistor (BJT) and to learn the DC biasing methods. The BC238A transistor is used to find the operating point of two biasing circuits, to see how the collector current depends on $V_{CE}$ and on the base drive, and to compare two biasing schemes in terms of their sensitivity to the current gain $\\beta$. The ability to diagnose wrong measurements of $V_{CE}$ is also practised.")
    d.h(2, "Benefits of the Experiment")
    d.p("The experiment shows how a BJT is analysed with the assumed-region method (assume active region, calculate, verify the assumption, switch to saturation if the assumption fails), why a bias circuit with an emitter resistor is preferred, and how measured voltages reveal wiring faults. It also trains the correct reading of a datasheet and the correct placement of a TO-92 transistor on a breadboard. These skills are directly used in the BJT amplifier experiment.")

    d.h(1, "Calculations and Simulations")
    d.h(2, "BJT Properties")
    d.p("The parameters of the BC238A were taken from the datasheet of the BC237/238/239 family (Fairchild Semiconductor), and they are listed in [[t:ds]]. The current gain of the class A transistors is specified as $h_{FE}=120$\u2013220 at $V_{CE}=5$ V and $I_C=2$ mA; the average value of 170 is used as $\\beta$. The base\u2013emitter turn-on voltage is typically 0.62 V (0.55\u20130.70 V) at the same bias. The collector\u2013emitter saturation voltage is 0.2 V at most ($I_C=10$ mA, $I_B=0.5$ mA; typical 0.07 V), and 0.2 V is used as $V_{CE(sat)}$ in the calculations.")
    d.tab("ds", ["Parameter", "Value", "Condition"], [
        ["$\\beta$ (class A, average)", "170 (range 120\u2013220)", "$V_{CE}$ = 5 V, $I_C$ = 2 mA"],
        ["$V_{BE(on)}$ (typical)", "0.62 V (min 0.55 V, max 0.70 V)", "$V_{CE}$ = 5 V, $I_C$ = 2 mA"],
        ["$V_{CE(sat)}$ (maximum)", "0.2 V (typical 0.07 V)", "$I_C$ = 10 mA, $I_B$ = 0.5 mA"],
        ["Pin 1 / Pin 2 / Pin 3", "Collector / Base / Emitter", "TO-92, flat face towards the viewer, leads down"],
    ], "BC238A parameters and TO-92 pin order from the datasheet", widths=[4.6, 5.4, 6.0], size=9)
    d.p("The pin order is C\u2013B\u2013E for the Fairchild datasheet. Some other manufacturers use E\u2013B\u2013C for the same package, so the pin order of the physical part should be checked before the circuit is powered.")

    d.h(2, "BJT Circuit 1 on the Breadboard")
    d.p("BJT circuit 1 ([[f:s1]]) was drawn on the breadboard as shown in [[f:bb]]. The transistor is placed with its three legs on three adjacent columns (collector on column 10, base on column 11, emitter on column 12). $R_C$ is connected between the collector column and a column that is wired to the $+V_{CC}$ rail, $R_E$ is connected between the emitter column and a column that is wired to the ground rail, and $R_B$ is connected between the base column and the $V_{BB}$ supply lead. The connections of the drawing were verified automatically against the circuit diagram.")
    d.fig("s1", R["fig_s1"], "BJT circuit 1 of the experiment ($R_B$ = 150 k$\\Omega$, $R_C$ = 2.2 k$\\Omega$, $R_E$ = 1 k$\\Omega$).", 7.5)
    d.fig("bb", R["fig_bb"], "BJT circuit 1 drawn on the breadboard ($V_{BB}$, $V_{CC}$ and GND points are indicated).", 15)

    d.h(2, "Q-Point Calculations of BJT Circuit 1")
    d.p("The operating point of circuit 1 was calculated for $V_{BB}=1$, 2 and 5 V and for the $V_{CC}$ values of the experiment sheet with the model $\\beta=170$, $V_{BE(on)}=0.62$ V, $V_{CE(sat)}=0.2$ V and no Early effect. The base-loop equation [[e:kvl]] gives the base current when the transistor is in the active region, and the remaining quantities follow from [[e:ic]] and [[e:vce]].")
    d.eq(r"V_{BB}=I_BR_B+V_{BE(on)}+I_ER_E,\quad I_E=(\beta+1)I_B\ \Rightarrow\ I_B=\frac{V_{BB}-V_{BE(on)}}{R_B+(\beta+1)R_E}", "kvl")
    d.eq(r"I_C=\beta I_B,\qquad I_E=(\beta+1)I_B", "ic")
    d.eq(r"V_{CE}=V_{CC}-I_CR_C-I_ER_E", "vce")
    d.p("The active-region assumption is verified by $V_{CE}\\geq V_{CE(sat)}$. If it fails, the transistor is in saturation: $V_{CE}=V_{CE(sat)}$, and $I_B$ and $I_C$ are found from the two loop equations given in [[e:sat]]; $I_C=\\beta I_B$ no longer holds. If the supply is so small that even this solution gives $I_C\\leq0$, the collector current is practically zero and $V_{CE}=V_{CC}$.")
    d.eq(r"\begin{aligned}(R_B+R_E)I_B+R_EI_C&=V_{BB}-V_{BE(on)}\\ R_EI_B+(R_C+R_E)I_C&=V_{CC}-V_{CE(sat)}\end{aligned}", "sat")
    d.p("**Sample calculation 1 (active region).** For $V_{BB}=2$ V and $V_{CC}=10$ V: $I_B=(2-0.62)/(150\\text{ k}\\Omega+171\\cdot1\\text{ k}\\Omega)=4.299$ \u00b5A, $I_C=170\\cdot4.299\\ \\mu\\text{A}=0.7308$ mA, $I_E=0.7351$ mA, and $V_{CE}=10-0.7308\\cdot2.2-0.7351\\cdot1=7.657$ V $>0.2$ V, so the assumption is valid. **Sample calculation 2 (saturation).** For $V_{BB}=5$ V and $V_{CC}=4$ V: the active-region result would be $V_{CE}=4-7.44<0.2$ V, so the transistor is in saturation, and [[e:sat]] gives $I_C=1.181$ mA, $V_{CE}=0.2$ V. The other cells are calculated in the same way.")
    t1_tables(d, R, True)
    d.p("The results are plotted in [[f:t1]]. In the active region (large $V_{CC}$), $I_C$ is constant for a given $V_{BB}$ ($%s$, $%s$ and $%s$ mA for $V_{BB}$ = 1, 2, 5 V) and $V_{CE}$ increases linearly with $V_{CC}$, since the model has no Early effect; the three horizontal lines are the output characteristics of the transistor for three different base currents ($I_B=%s$, $%s$ and $%s$ \u00b5A). When $V_{CC}$ is decreased, the transistor enters the saturation region (the cells $V_{CC}\\leq%s$ V for $V_{BB}=5$ V, $\\leq%s$ V for $V_{BB}=2$ V and $\\leq%s$ V for $V_{BB}=1$ V), where $V_{CE}$ is clamped at about 0.2 V and $I_C$ falls linearly with $V_{CC}$; this is the steep part of the characteristic. For $V_{CC}=0$, all currents are zero." % (
        n2(th[(1, 20)][1] * 1e3, 3), n2(th[(2, 20)][1] * 1e3, 3), n2(th[(5, 20)][1] * 1e3, 3),
        n2((1 - 0.62) / (150e3 + 171e3) * 1e6, 3), n2((2 - 0.62) / (150e3 + 171e3) * 1e6, 3), n2((5 - 0.62) / (150e3 + 171e3) * 1e6, 3),
        max(sc[5]), max(sc[2]), max(sc[1])))
    d.fig("t1", R["fig_t1"], "$I_C$\u2013$V_{CE}$ points of Table 1 (calculation: circles; SPICE: crosses); right: zoom on the saturation region.", 15.5)
    d.p("The SPICE results (BC238A model with $I_S$ fitted to $V_{BE}=0.62$ V at 2 mA, $\\beta=170$, no Early effect; the model line is in Appendix A) are also given in the tables. In the active region, the largest difference in $V_{CE}$ is %s V ($V_{BB}$ = 1 V), %s V (2 V) and %s V (5 V), and the mean difference in $I_C$ is %+.1f%%, %+.1f%% and %+.1f%%, respectively. The difference is largest for $V_{BB}=1$ V because the real $V_{BE}$ depends logarithmically on the current: at $I_C\\approx0.2$ mA the real $V_{BE}$ is about 0.56 V, not 0.62 V, so the base current (which is proportional to $V_{BB}-V_{BE}$) is 15%% larger than the calculated value. For $V_{BB}=5$ V, the term $V_{BB}-V_{BE}$ is large and the effect of the error in $V_{BE}$ disappears. In the saturation region, SPICE gives $V_{CE}$ between 0.03 and 0.15 V (it decreases with the base drive), whereas the model uses a constant 0.2 V; hence the saturation cells have a difference of up to 0.15 V in $V_{CE}$ and a few percent in $I_C$." % (
        n2(ag[1][0], 3), n2(ag[2][0], 3), n2(ag[5][0], 3), ag[1][1], ag[2][1], ag[5][1]))

    d.h(2, "Biasing Circuit 1 (No Emitter Resistor)")
    d.p("The circuit in [[f:s2]] has no emitter resistor. For $V_{BB}=5$ V and $V_{CC}=12$ V, the base current is $I_{BQ}=(V_{BB}-V_{BE})/R_B=(5-0.62)/150\\text{ k}\\Omega=%s$ \u00b5A, the collector current is $I_{CQ}=\\beta I_{BQ}=%s$ mA, and the collector\u2013emitter voltage is $V_{CEQ}=V_{CC}-I_{CQ}R_C=12-%s\\times2.2=%s$ V, with $V_{BEQ}=0.62$ V. Since $V_{CEQ}>0.2$ V (and $V_{CEQ}>V_{BE}$, i.e., the collector junction is reverse biased), the active-region assumption is valid. The SPICE simulation gives $V_{BEQ}=%s$ V, $I_{BQ}=%s$ \u00b5A, $I_{CQ}=%s$ mA and $V_{CEQ}=%s$ V; the differences from the calculation result from the dependence of $V_{BE}$ on the current ($V_{BE}=0.644$ V at 5 mA)." % (
        n2(c1[1] * 1e6, 4), n2(c1[2] * 1e3, 4), n2(c1[2] * 1e3, 4), n2(c1[3], 4), n2(c1s[0], 4), n2(c1s[1] * 1e6, 4), n2(c1s[2] * 1e3, 4), n2(c1s[3], 4)))
    d.fig("s2", R["fig_s2"], "BJT biasing circuit 1 (no emitter resistor).", 7.0)
    sens = R["sens"]
    d.p("The operating point of this circuit is very sensitive to $\\beta$, because $I_C=\\beta I_B$ and $I_B$ is fixed by $V_{BB}$ and $R_B$. With the datasheet range of $\\beta$ for the class A transistors, $I_C$ changes from %s mA ($\\beta=120$) to %s mA ($\\beta=220$) in the active-region equations; for $\\beta=220$, the active-region result would give $V_{CE}<0$, so the transistor actually saturates with $V_{CE}=0.2$ V and $I_C=5.36$ mA, and the amplifier would be unusable. This is shown in the left graph of [[f:load]]." % (n2(sens[0][1] * 1e3, 3), n2(R["sens"][2][1] * 1e3, 3) + " (saturation limit)"))

    d.h(2, "Biasing Circuit 2 (With Emitter Resistor)")
    d.p("The circuit in [[f:s3]] has $R_B=22$ k$\\Omega$, $R_C=1.2$ k$\\Omega$ and $R_E=1$ k$\\Omega$. The calculation with [[e:kvl]]\u2013[[e:vce]] for $V_{BB}=5$ V and $V_{CC}=12$ V gives $I_{BQ}=4.38/(22\\text{ k}\\Omega+171\\text{ k}\\Omega)=%s$ \u00b5A, $I_{CQ}=%s$ mA, $I_{EQ}=%s$ mA, $V_{BEQ}=0.62$ V, and $V_{CEQ}=12-%s\\times1.2-%s\\times1=%s$ V. The transistor is in the active region. The SPICE simulation gives $V_{BEQ}=%s$ V, $I_{BQ}=%s$ \u00b5A, $I_{CQ}=%s$ mA and $V_{CEQ}=%s$ V." % (
        n2(c2[1] * 1e6, 4), n2(c2[2] * 1e3, 4), n2((c2[2] + c2[1]) * 1e3, 4), n2(c2[2] * 1e3, 4), n2((c2[2] + c2[1]) * 1e3, 4), n2(c2[3], 4), n2(c2s[0], 4), n2(c2s[1] * 1e6, 4), n2(c2s[2] * 1e3, 4), n2(c2s[3], 4)))
    d.fig("s3", R["fig_s3"], "BJT biasing circuit 2 (with emitter resistor).", 7.5)
    d.tab("sens", ["$\\beta$", "Circuit 1: $I_C$ (mA)", "Circuit 1: $V_{CE}$ (V)", "Circuit 2: $I_C$ (mA)", "Circuit 2: $V_{CE}$ (V)"],
          [[str(b), n2(i1 * 1e3, 3), n2(v1, 3) + (" (saturated)" if v1 <= 0.2 else ""), n2(i2 * 1e3, 3), n2(v2, 3)] for (b, i1, v1, i2, v2) in sens],
          "Sensitivity of the two bias circuits to $\\beta$ ($V_{BB}$ = 5 V, $V_{CC}$ = 12 V)", widths=[1.8, 3.4, 3.8, 3.4, 3.6], size=9)
    d.fig("load", R["fig_load"], "DC load lines and operating points of the two bias circuits for $\\beta$ = 120, 170 and 220 (calculation).", 15.5)
    d.p("In circuit 2, the emitter resistor provides negative feedback: if $I_C$ tries to increase, the voltage drop on $R_E$ increases, the base\u2013emitter voltage decreases, and $I_B$ decreases. As [[t:sens]] shows, a change of $\\beta$ from 120 to 220 changes $I_C$ only from %s to %s mA (%.0f%%), whereas $I_C$ of circuit 1 changes by %.0f%% and finally saturates. The operating point is stable because $(\\beta+1)R_E=171$ k$\\Omega$ is large compared with $R_B$, so that $I_C\\approx(V_{BB}-V_{BE})/R_E$ is almost independent of $\\beta$." % (n2(sens[0][3] * 1e3, 3), n2(sens[2][3] * 1e3, 3), 100 * (sens[2][3] - sens[0][3]) / sens[1][3], 100 * (sens[2][1] - sens[0][1]) / sens[1][1]))

    d.h(2, "Possible Reasons for Wrong $V_{CEQ}$ Readings")
    d.p("The reasons are listed item by item for biasing circuit 2 of [[f:s3]] (the correct value is $V_{CEQ}\\approx3.5$ V). The values in [[t:scen]] were obtained from SPICE simulations of each fault.")
    scen_table(d, R, True)
    d.p("**If $V_{CEQ}$ is measured as 12 V**, no current flows through $R_C$ and $R_E$ ($I_C\\approx0$), i.e., the transistor is in cut-off or the collector current path is broken. The possible reasons and the corresponding actions are:")
    d.bullets([
        "No base current: $V_{BB}$ is not applied or is 0 V (supply channel off, current limit at zero, ground wire not common). Action: measure $V_B$ with respect to ground; if it is 0 V, check the $V_{BB}$ channel and its wiring.",
        "Open $R_B$ or an unconnected base: a loose resistor leg, a hole in the wrong column, or a broken wire. Action: measure the voltage across $R_B$ (it should be about 0.5 V, i.e., $I_BR_B=22.7\\ \\mu\\text{A}\\times22\\text{ k}\\Omega$); if $V_B=V_{BB}$ and $V_{BE}\\approx0$, the base is connected but the emitter path is open; if the voltage at the base side is 0 V, the base is not connected.",
        "Transistor inserted incorrectly or damaged (open base\u2013emitter junction): a wrong pin order places the base on a wrong column. Action: check the pin order of the part (C\u2013B\u2013E), measure $V_{BE}$ (it should be 0.6\u20130.7 V when the transistor conducts), and replace the transistor if the junction does not conduct.",
        "Exchanged collector and emitter pins: the transistor works in the inverse mode with a very small current gain, and $V_{CE}$ is close to 12 V (%s V in the simulation, with $V_{BE}\\approx%s$ V and a small $I_C$). Action: exchange the two pins." % (n2(S["qrev"][0], 3), n2(S["qrev"][1], 2)),
        "A measurement error: the voltmeter is connected between $V_{CC}$ and a point instead of between collector and emitter, or $R_E$ is open (then $V_{CE}$ is not 12 V but %s V in the simulation, and $V_{BE}\\approx0.1$ V, which distinguishes this case)." % n2(S["reopen"][0], 2),
    ])
    d.p("**If $V_{CEQ}$ is measured as 0 V**, the transistor is in deep saturation or there is a short circuit between the collector and the emitter. The possible reasons and the corresponding actions are:")
    d.bullets([
        "Excessive base drive or too large a collector resistor: $R_E$ shorted by a wire (%s V in the simulation, $I_C=%s$ mA), or a wrong $R_C$ value such as 12 k$\\Omega$ (%s V). Action: measure each resistor with an ohmmeter and compare with the colour code; remove the unintended wire." % (n2(S["reshort"][0], 3), n2(S["reshort"][2] * 1e3, 2), n2(S["rcbig"][0], 3)),
        "A short circuit between collector and emitter (a wire or a solder bridge on the breadboard, or a damaged transistor). In this case, $V_{BE}$ is typically negative or abnormal (%s V in the simulation) and $I_C$ is about $V_{CC}/(R_C+R_E)=5.5$ mA. Action: remove the short, or replace the transistor if it is damaged." % n2(S["ceshort"][1], 2),
        "$V_{CC}$ is not applied (0 V): the supply channel is off or its wire is disconnected (%s V in the simulation, with a small reverse current in $R_C$). Action: measure $V_{CC}$ at the top of $R_C$." % n2(S["vcc0"][0], 3),
        "$R_C$ is open or not connected to the collector: the collector floats and the forward-biased collector junction pulls it to the emitter voltage (%s V in the simulation, $I_C=0$, $V_{BE}\\approx%s$ V). Action: check the continuity of $R_C$ and the column of the collector." % (n2(S["rcopen"][0], 3), n2(S["rcopen"][1], 2)),
        "A measurement error, such as both probes on the same node or the ground lead of the voltmeter on a floating ground. Action: repeat the measurement with the probes directly on the collector and emitter pins.",
    ])
    d.p("In every case, the systematic approach is to measure $V_B$, $V_E$ and $V_C$ with respect to ground and to compare them with the expected values ($V_B\\approx%s$ V, $V_E\\approx%s$ V, $V_C\\approx%s$ V) in order to find the first node where the measurement deviates." % (n2(c2[0] + (c2[2] + c2[1]) * 1e3, 3), n2((c2[2] + c2[1]) * 1e3, 3), n2(c2[3] + (c2[2] + c2[1]) * 1e3, 3)))

    d.h(1, "Conclusions")
    d.p("The calculated and the simulated results of Table 1 agree well in the active region when the base drive is large ($V_{BB}=5$ V: the difference in $I_C$ is %+.1f%% and in $V_{CE}$ %s V), and the difference grows when the base drive is small ($V_{BB}=1$ V: %+.1f%% in $I_C$), because the constant $V_{BE(on)}=0.62$ V of the model is valid only near 2 mA. In the saturation region, the constant $V_{CE(sat)}=0.2$ V of the model is larger than the SPICE values (0.03\u20130.15 V), which is a limitation of the simple model rather than a calculation error. In the bias circuits, the circuit without $R_E$ has an operating point that depends strongly on $\\beta$ (and even saturates for $\\beta\\geq184$, which is inside the datasheet range of 120\u2013220), whereas the circuit with $R_E$ changes its collector current by only about %.0f%% over the same range, which is why emitter feedback is used in practical amplifiers. The fault analysis showed that $V_{CE}=12$ V and $V_{CE}=0$ V can each arise from several different faults, and that the additional measurements of $V_{BE}$ and the node voltages are necessary to separate them." % (ag[5][1], n2(ag[5][0], 3), ag[1][1], 100 * (sens[2][3] - sens[0][3]) / sens[1][3]))
    d.h(1, "References")
    d.bullets([
        "Fairchild Semiconductor. (2002). BC237/238/239 NPN epitaxial silicon transistor [Data sheet, Rev. A2]. Retrieved October 11, 2026, from https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2309151357_onsemi-BC237_C3201628.pdf",
        "Sedra, A. S., & Smith, K. C. (2014). Microelectronic circuits (7th ed.). New York: Oxford University Press.",
        "ngspice. (n.d.). ngspice user manual. Retrieved October 11, 2026, from https://ngspice.sourceforge.io/docs.html",
    ], numbered=True)
    d.h(1, "Appendices")
    d.h(2, "Appendix A: SPICE Model and Netlists")
    d.p("The BC238A model was fitted to the datasheet typical values ($I_S$ for $V_{BE}=0.62$ V at 2 mA, $\\beta_F=170$); $\\beta_R=1$, $R_B=30\\ \\Omega$ and $R_C=1\\ \\Omega$ approximately reproduce the saturation voltages of the datasheet, and the Early voltage is infinite as required by the experiment sheet. The library model of the BC238 in another simulation program may differ slightly.")
    d.code(exp4.QM, "Code A.1  BJT model line used in the ngspice simulations")
    d.code(clean_cir(os.path.join(SPICE, "e4_t1_5_10.cir")), "Netlist A.2  BJT circuit 1 ($V_{BB}$ = 5 V, $V_{CC}$ = 10 V)")
    d.code(clean_cir(os.path.join(SPICE, "e4_c2.cir")), "Netlist A.3  BJT biasing circuit 2")
    return d


def build_tr(R):
    d = Doc("tr")
    th, sp = R["t1_th"], R["t1_sp"]
    c1, c1s, c2, c2s = R["c1"], R["c1_sp"], R["c2"], R["c2_sp"]
    sens = R["sens"]
    ag = agree(R)
    S = R["scen"]
    d.title_block([
        ("Deney 4 \u2013 Ön Çalışma Öğretici Rehberi", 15, True),
        ("BJT Devreleri (BC238A)", 12, False),
        ("Bu belge SADECE ÖĞRENMEK içindir; teslim edilecek metin İngilizce rapordur.", 11, False),
    ], [("Ad Soyad", ""), ("Numara", ""), ("Tarih", "")])
    d.h(1, "Büyük Resim")
    d.p("BJT (iki kutuplu eklem transistörü), **akımla kontrol edilen bir musluktur**: küçük bir baz akımı $I_B$, çok daha büyük bir kolektör akımı $I_C$'yi kontrol eder. NPN'de baz–emetör eklemi bir diyot gibi iletime geçer ($V_{BE}\\approx0{,}6$–$0{,}7$ V); bu olduğunda $I_C\\approx\\beta I_B$ olur. Deney bu devreleri analiz etmenin sistematik yolunu öğretir: **bölgeyi varsay → hesapla → varsayımı doğrula → tutmuyorsa bölgeyi değiştir.**")
    d.box("Üç bölge, üç denklem takımı", [
        "**Kesim:** $V_{BE}<V_{BE(on)}$ ⇒ $I_B=I_C=0$.",
        "**Aktif:** $V_{BE}=V_{BE(on)}$, $I_C=\\beta I_B$, $I_E=(\\beta+1)I_B$ ve $V_{CE}\\geq V_{CE(sat)}$ (sadece bu denetim yapılır).",
        "**Doyma:** $V_{CE}=V_{CE(sat)}\\approx0{,}2$ V. Burada $I_C<\\beta I_B$ ve $I_C$'yi dış devre (direnç ve besleme) belirler; $\\beta$ artık işe yaramaz.",
    ])
    d.h(1, "Soru 1: BC238A Parametreleri")
    d.tab("ds", ["Parametre", "Değer", "Koşul"], [
        ["$\\beta$ (A sınıfı, ortalama)", "170 (aralık 120–220)", "$V_{CE}$ = 5 V, $I_C$ = 2 mA"],
        ["$V_{BE(on)}$ (tipik)", "0,62 V (min 0,55; maks 0,70 V)", "$V_{CE}$ = 5 V, $I_C$ = 2 mA"],
        ["$V_{CE(sat)}$ (maksimum)", "0,2 V (tipik 0,07 V)", "$I_C$ = 10 mA, $I_B$ = 0,5 mA"],
        ["Bacak 1 / 2 / 3", "Kolektör / Baz / Emetör", "TO-92, düz yüz bize dönük, bacaklar aşağıda"],
    ], "BC238A parametreleri (Fairchild BC237/238/239 veri sayfası, Rev. A2; doğrudan okundu)", widths=[4.6, 5.4, 6.0], size=9)
    d.bullets([
        "**A sınıfı ne demek?** Veri sayfasında $h_{FE}$ üç gruba ayrılır: A: 120–220, B: 180–460, C: 380–800. BC238**A**'daki \"A\" bu gruptur. Föy 'tipik ya da ortalama' kullanın dediği için A grubunun ortalaması $(120+220)/2=170$ alındı.",
        "**$h_{FE}$ = $I_C/I_B$ (DC akım kazancı)** = $\\beta$ (föydeki ipucu).",
        "**Bacak sırası:** Fairchild: 1-C, 2-B, 3-E. Başka üreticiler (ör. bazı Motorola/ST parçaları) E-B-C yapabilir; takmadan önce parçanın üstündeki işarete ve veri sayfasına bakın. Yanlış takarsanız devre çalışmaz (hatta transistör ısınır).",
    ])
    d.h(1, "Soru 2: Breadboard'da Devre 1")
    d.p("Breadboard'da bir sütundaki beş delik (a–e) birbirine bağlıdır. Transistörün her bacağını **ayrı bir sütuna** takarsınız ve o sütunun boş deliklerine ilgili elemanı bağlarsınız. Çizim:")
    d.fig("s1", R["fig_s1"], "BJT devre 1.", 7.5)
    d.fig("bb", R["fig_bb"], "BJT devre 1'in breadboard çizimi (bağlantıları kod otomatik denetledi).", 15)
    d.bullets([
        "Sütun 10 = kolektör, 11 = baz, 12 = emetör (düz yüz bize dönükken soldan sağa C–B–E).",
        "$R_C$ (2,2 kΩ; kırmızı-kırmızı-kırmızı bantlar): kolektör sütunundan 6. sütuna; 6. sütun kırmızı telle $+V_{CC}$ rayına bağlı.",
        "$R_B$ (150 kΩ; kahverengi-yeşil-sarı): 3. sütundan baz sütununa; 3. sütuna $V_{BB}$ kaynağının + ucu verilir.",
        "$R_E$ (1 kΩ; kahverengi-siyah-kırmızı): emetör sütunundan 16. sütuna; 16. sütun siyah telle GND rayına.",
        "**İki ayrı kaynak:** $V_{BB}$ ve $V_{CC}$ ayrı gerilimlerdir; ikisinin **eksi uçları ortak toprağa** (GND rayı) bağlanır. Eksi uçları birleştirmezseniz gerilimler birbirine referanslanmaz ve devre çalışmaz (en sık yapılan hata).",
    ])
    d.box("Direnç renk kodu hatırlatması", [
        "İlk iki bant rakam, üçüncü bant 10'un kuvveti: 0 siyah, 1 kahverengi, 2 kırmızı, 3 turuncu, 4 sarı, 5 yeşil, 6 mavi, 7 mor, 8 gri, 9 beyaz. 2,2 kΩ = 2-2-×100; 150 kΩ = 1-5-×10 k; 1 kΩ = 1-0-×100.",
    ])
    d.h(1, "Soru 3.1: Tablo 1 (VBB = 1, 2, 5 V)")
    d.h(2, "Yöntem")
    d.p("Baz döngüsünde Kirchhoff yasası: $V_{BB}=I_BR_B+V_{BE}+I_ER_E$. $I_E=(\\beta+1)I_B$ yazarsak $I_B$ yalnız bırakılır:")
    d.eq(r"I_B=\frac{V_{BB}-V_{BE(on)}}{R_B+(\beta+1)R_E}", "ib")
    d.p("**Neden $(\\beta+1)R_E$?** Emetör akımı baz akımının $(\\beta+1)$ katıdır; bu akım $R_E$'den geçer. Baz tarafından bakınca $R_E$, $(\\beta+1)$ kat büyümüş görünür (\"yansıyan direnç\"). Sayılarla $(\\beta+1)R_E=171$ kΩ; yani $R_B=150$ kΩ'a eklenir (toplam 321 kΩ).")
    d.eq(r"I_C=\beta I_B,\quad I_E=(\beta+1)I_B,\quad V_{CE}=V_{CC}-I_CR_C-I_ER_E", "ic")
    d.p("**Doğrulama:** $V_{CE}\\geq0{,}2$ V ise aktif varsayım doğru. Değilse doyma: $V_{CE}=0{,}2$ V ve iki bilinmeyen için iki denklem (baz ve kolektör döngüleri):")
    d.eq(r"\begin{aligned}(R_B+R_E)I_B+R_EI_C&=V_{BB}-V_{BE(on)}\\ R_EI_B+(R_C+R_E)I_C&=V_{CC}-V_{CE(sat)}\end{aligned}", "sat")
    d.p("Doyma çözümü bile $I_C\\leq0$ çıkarsa (besleme 0,2 V'tan bile küçük) akım pratikte sıfırdır ve $V_{CE}=V_{CC}$ alınır.")
    d.box("Tamamen çözülmüş iki örnek", [
        "**Aktif ($V_{BB}=2$ V, $V_{CC}=10$ V):** $I_B=\\dfrac{2-0{,}62}{150\\,\\text{k}+171\\,\\text{k}}=4{,}299\\ \\mu$A; $I_C=170\\times4{,}299\\ \\mu\\text{A}=0{,}7308$ mA; $I_E=0{,}7351$ mA; $V_{CE}=10-0{,}7308\\times2{,}2-0{,}7351\\times1=7{,}657$ V $\\geq0{,}2$ ✓.",
        "**Doyma ($V_{BB}=5$ V, $V_{CC}=4$ V):** aktif çözüm $V_{CE}=4-7{,}44<0{,}2$ ✗ ⇒ doyma. $[151\\text{k}\\ \\ 1\\text{k};\\ 1\\text{k}\\ \\ 3{,}2\\text{k}]\\,[I_B;I_C]=[4{,}38;\\ 3{,}8]$ ⇒ $I_C=1{,}181$ mA, $V_{CE}=0{,}2$ V.",
    ])
    d.h(2, "Tablo ve yorum")
    t1_tables(d, R, False)
    d.fig("t1", R["fig_t1"], "Tablo 1 noktaları: $I_C$–$V_{CE}$ (daire: el hesabı; çarpı: SPICE).", 15.5)
    d.bullets([
        "**Düz kısım (aktif bölge):** $I_C$ yalnız $V_{BB}$'ye (yani $I_B$'ye) bağlı; $V_{CC}$ arttıkça sabit kalır; sadece $V_{CE}$ artar. Bu, transistörün kolektör akımının kolektör gerilimine duyarsız olduğu 'akım kaynağı' bölgesidir. Üç yatay çizgi üç farklı $I_B$ içindir (1,18 / 4,30 / 13,6 µA).",
        "**Dik kısım (doyma):** $V_{CC}$ küçülünce $V_{CE}$ 0,2 V'ta kilitlenir ve $I_C$ besleme ile birlikte düşer: bu bölgede transistör neredeyse bir kapalı anahtardır.",
        "**$V_{CC}=0$ sütunu:** her şey sıfır. **$V_{CC}=0{,}2$ V sütunu:** besleme 0,2 V'luk $V_{CE(sat)}$'i bile karşılayamadığı için akım ≈0 ve $V_{CE}=V_{CC}$ yazıldı. SPICE burada ~0,04 mA gösterir (gerçek transistörün doyma gerilimi 0,2 V'tan küçüktür); bu fark 'basit modelin sınırı'dır.",
        "**Elle ile SPICE farkı:** aktifte $V_{CE}$ farkı ≤%s V; $I_C$ farkı ortalama %+.1f%% ($V_{BB}$=1 V), %+.1f%% (2 V), %+.1f%% (5 V). $V_{BB}$=1 V'ta fark büyük çünkü $V_{BE}$ akıma logaritmik bağlıdır: 0,2 mA'de gerçek $V_{BE}\\approx0{,}56$ V (0,62 değil), dolayısıyla $V_{BB}-V_{BE}$ ve $I_B$ %%15 büyük çıkar. $V_{BB}$=5 V'ta $V_{BB}-V_{BE}$ büyük olduğundan $V_{BE}$ hatası önemsizleşir." % (n2(max(ag[v][0] for v in VBB_LIST), 3), ag[1][1], ag[2][1], ag[5][1]),
    ])
    d.h(1, "Soru 3.2 ve 3.3: Kutuplama Devreleri")
    d.h(2, "Devre 1 (RE yok)")
    d.fig("s2", R["fig_s2"], "BJT kutuplama devresi 1.", 7.0)
    d.p("$V_{BB}=5$ V, $V_{CC}=12$ V: $I_{BQ}=\\dfrac{5-0{,}62}{150\\,\\text{k}\\Omega}=%s\\ \\mu$A; $I_{CQ}=170\\times%s\\ \\mu\\text{A}=%s$ mA; $V_{CEQ}=12-%s\\times2{,}2=%s$ V; $V_{BEQ}=0{,}62$ V. Doğrulama: $V_{CEQ}=%s\\ \\text{V}>0{,}2$ V ✓ (ayrıca $V_{CE}>V_{BE}$: kolektör eklemi ters kutuplu ⇒ aktif). SPICE: $V_{BEQ}=%s$ V, $I_{CQ}=%s$ mA, $V_{CEQ}=%s$ V." % (
        n2(c1[1] * 1e6, 4), n2(c1[1] * 1e6, 4), n2(c1[2] * 1e3, 4), n2(c1[2] * 1e3, 4), n2(c1[3], 4), n2(c1[3], 3), n2(c1s[0], 4), n2(c1s[2] * 1e3, 4), n2(c1s[3], 4)))
    d.h(2, "Devre 2 (RE var)")
    d.fig("s3", R["fig_s3"], "BJT kutuplama devresi 2.", 7.5)
    d.p("$I_{BQ}=\\dfrac{5-0{,}62}{22\\,\\text{k}+171\\,\\text{k}}=%s\\ \\mu$A; $I_{CQ}=%s$ mA; $I_{EQ}=%s$ mA; $V_{CEQ}=12-%s\\times1{,}2-%s\\times1=%s$ V. Aktif ✓. SPICE: $V_{BEQ}=%s$ V; $I_{CQ}=%s$ mA; $V_{CEQ}=%s$ V." % (
        n2(c2[1] * 1e6, 4), n2(c2[2] * 1e3, 4), n2((c2[2] + c2[1]) * 1e3, 4), n2(c2[2] * 1e3, 4), n2((c2[2] + c2[1]) * 1e3, 4), n2(c2[3], 4), n2(c2s[0], 4), n2(c2s[2] * 1e3, 4), n2(c2s[3], 4)))
    d.h(2, "Neden devre 2 daha iyi? (β duyarlılığı)")
    d.tab("sens", ["$\\beta$", "Devre 1: $I_C$ (mA)", "Devre 1: $V_{CE}$ (V)", "Devre 2: $I_C$ (mA)", "Devre 2: $V_{CE}$ (V)"],
          [[str(b), n2(i1 * 1e3, 3), n2(v1, 3) + (" (doymada)" if v1 <= 0.2 else ""), n2(i2 * 1e3, 3), n2(v2, 3)] for (b, i1, v1, i2, v2) in sens],
          "β'nın A sınıfı aralığında devrelerin Q noktası", widths=[1.8, 3.4, 3.8, 3.4, 3.6], size=9)
    d.fig("load", R["fig_load"], "Yük doğruları ve Q noktaları.", 15.5)
    d.bullets([
        "**Devre 1'de** $I_C=\\beta(V_{BB}-V_{BE})/R_B$: $I_C$, $\\beta$ ile doğru orantılıdır. Aynı model numaralı iki transistörün β'sı 120 ile 220 arasında değişebilir; $I_C$ de aynı oranda değişir; $\\beta\\geq184$ olan bir parçada transistör **doymaya girer** (yükselteç olarak işe yaramaz). Ayrıca sıcaklıkla β artar; devre kendiliğinden kayar.",
        "**Devre 2'de** $R_E$ negatif geri besleme yapar: $I_C$ artmaya kalkarsa $R_E$ üzerindeki gerilim artar, $V_{BE}$ azalır, $I_B$ düşer, $I_C$ geri çekilir. $(\\beta+1)R_E=171$ kΩ ≫ $R_B$ olduğunda $I_C\\approx(V_{BB}-V_{BE})/R_E$ ve β'ya bağlı değildir.",
        "**Bir tesadüf:** iki devrede de DC yük doğrusu aynıdır ($R_C=2{,}2$ kΩ ve $R_C+R_E=2{,}2$ kΩ). Fark, Q noktasının yük doğrusu üzerinde ne kadar oynadığındadır.",
    ])
    d.p("Sayılarla: β 120→220 değişince devre 2'nin $I_C$'si %s → %s mA (%.0f%%), devre 1'in $I_C$'si ise %s mA → doyma (%.0f%% artış ve doyma)." % (
        n2(sens[0][3] * 1e3, 3), n2(sens[2][3] * 1e3, 3), 100 * (sens[2][3] - sens[0][3]) / sens[1][3], n2(sens[0][1] * 1e3, 3), 100 * (sens[2][1] - sens[0][1]) / sens[1][1]))

    d.h(1, "Soru 3.4 ve 3.5: Hata Teşhisi")
    d.p("Devre 2'de beklenen $V_{CEQ}\\approx3{,}5$ V. Ölçüm başka çıkarsa **akıl yürütme zinciri şudur:** $V_{CE}$, $V_{CC}$'den $R_C$ ve $R_E$ üzerindeki düşümlerin çıkarılmasıyla bulunur. $V_{CE}=12$ V ise düşümler sıfır (akım yok); $V_{CE}=0$ ise ya akım çok büyük (doyma) ya da C–E arası kısa devre ya da kolektörde gerilim yok. Her senaryo SPICE ile simüle edilmiştir; bu sayede 'hangi hata hangi sayıyı verir' kanıtlıdır:")
    scen_table(d, R, False)
    d.h(2, "$V_{CEQ}$ = 12 V ölçülürse (akım yok, kesim)")
    d.bullets([
        "**$V_{BB}$ uygulanmamış/0 V:** Taban gerilimini toprağa göre ölçün; 0 V ise kaynak kanalı kapalı ya da akım sınırı sıfır ya da topraklar ortak değil. Çözüm: kaynağı açın, $V_{BB}$ = 5 V ayarlayın, GND ortaklığını kurun.",
        "**$R_B$ açık / baz bacağı bağlı değil:** $R_B$ uçları arasında voltmetre ile gerilim ölçün: $R_B$ üzerinde ≈0,5 V düşmesi gerekirken (22,7 µA × 22 kΩ) hiç akım yoksa düşüm 0 V olur ve baz düğümü havada kalır ($V_B$ kararsız ya da ≈0 V ölçülür). Çözüm: direnç bacağını doğru sütuna takın, kopuk teli değiştirin.",
        "**Transistör hatalı takılmış ya da bozuk (BE ekleminde kopukluk):** $V_{BE}$'yi ölçün; iletimde 0,6–0,7 V olmalıdır. Çözüm: bacak sırasını veri sayfasından kontrol edin (C-B-E), transistörü diyot testiyle deneyin, gerekirse değiştirin.",
        "**Kolektör–emetör bacakları ters:** Transistör 'ters modda' çalışır, β çok küçüktür; simülasyonda $V_{CE}$ = %s V, $V_{BE}$ ≈ %s V, $I_C$ ≈ %s mA. 12 V'a çok yakın ama tam değil; ayırt edici işaret $V_{BE}$'nin 0,56 V gibi iletim değerinde olmasıdır. Çözüm: iki bacağı yer değiştirin." % (n2(S["qrev"][0], 3), n2(S["qrev"][1], 2), n2(S["qrev"][2] * 1e3, 2)),
        "**$R_E$ açık (emetör havada):** Bu durumda $V_{CE}$ = 12 V olmaz: simülasyonda %s V çıkar ($V_{BE}\\approx%s$ V, çünkü emetör gerilimi tabana yaklaşır). Yani 'tam 12 V' ölçerseniz sorun $R_E$ değildir; 7 V civarı ise $R_E$ kopuk olabilir." % (n2(S["reopen"][0], 2), n2(S["reopen"][1], 2)),
        "**Ölçüm hatası:** probu $V_{CE}$ yerine $V_{CC}$–toprak arasına koymak; ya da toprak ucunun yüzer olması. Çözüm: probları doğrudan kolektör ve emetör bacağına koyun.",
    ])
    d.h(2, "$V_{CEQ}$ = 0 V ölçülürse (derin doyma ya da kısa devre)")
    d.bullets([
        "**Aşırı baz sürmesi / yanlış direnç:** $R_E$'nin bir telle kısa devre edilmesi (simülasyonda %s V, $I_C$ ≈ %s mA) ya da $R_C$ yerine 12 kΩ takılması (%s V). Çözüm: dirençleri ohmmetreyle ölçüp renk koduyla karşılaştırın, istenmeyen teli kaldırın." % (n2(S["reshort"][0], 3), n2(S["reshort"][2] * 1e3, 2), n2(S["rcbig"][0], 3)),
        "**C–E arası kısa devre:** tel, lehim köprüsü ya da arızalı transistör. İpucu: bu durumda $V_{BE}$ **negatif** (≈ %s V) çıkar ve akım $V_{CC}/(R_C+R_E)\\approx5{,}5$ mA'dir. Çözüm: kısayı kaldırın, transistörü değiştirin." % n2(S["ceshort"][1], 2),
        "**$V_{CC}$ yok:** kolektör beslemesi 0 V ise simülasyonda $V_{CE}$ = %s V, $I_C$ eksi (baz akımı kolektörden dışarı akar). Çözüm: $R_C$'nin üstünde $V_{CC}$'yi ölçün." % n2(S["vcc0"][0], 3),
        "**$R_C$ açık / kolektör bağlı değil:** kolektör havada kalır, ileri kutuplu kolektör eklemi onu emetör gerilimine çeker: $V_{CE}$ = %s V ve $I_C$=0; $V_{BE}$ ≈ %s V. Çözüm: $R_C$ sürekliliğini ve kolektör sütununu kontrol edin." % (n2(S["rcopen"][0], 3), n2(S["rcopen"][1], 2)),
        "**Ölçüm hatası:** iki prob aynı düğümde ya da voltmetrenin toprağı yüzer.",
    ])
    d.box("Sistematik teşhis", [
        "Önce $V_{CC}$ ve $V_{BB}$'yi doğrudan devre girişinde ölçün (kaynaklar gerçekten orada mı?). Sonra $V_B$, $V_E$, $V_C$'yi toprağa göre ölçün ve beklenen değerlerle ($V_B\\approx%s$ V, $V_E\\approx%s$ V, $V_C\\approx%s$ V) karşılaştırın. **İlk sapma gösteren düğüm**, hatanın bulunduğu elemanın komşusudur. $V_{BE}$ değeri (0 / 0,6 / negatif) hatanın cinsini ayırt eder." % (n2(c2[0] + (c2[2] + c2[1]) * 1e3, 3), n2((c2[2] + c2[1]) * 1e3, 3), n2(c2[3] + (c2[2] + c2[1]) * 1e3, 3)),
    ])
    d.h(1, "Programda Nasıl Yapılır?")
    d.bullets([
        "**Tablo 1 için:** `.op` ile $V_{CC}$ değerlerini tek tek denemek yerine `.step param Vcc list 0 0.2 0.5 1 2 4 6 8 10 15 20` ve `.op` kullanılır; sonuçlar `View → SPICE Error/Output Log` içinde listelenir (LTspice'ta `.step` ve `.param` ile). Ya da `.dc Vcc 0 20 0.1` ile $I_C$–$V_{CC}$ eğrisi çizip tabloya karşılık gelen noktaları okuyabilirsiniz.",
        "**BC238A modeli:** Micro-Cap kütüphanesinde varsa onu seçin; yoksa `2N3904` gibi bir model β'sı farklı olabilir. Bu belgenin modeli ($\\beta=170$, $V_{BE}=0{,}62$ V@2 mA) Ek A'dadır ve `.model` olarak yapıştırılabilir.",
        "**Ölçüm kuralı:** Raporda hesaplar elle yazılmış değil **denklem düzeniyle** (Word Equation) yazılmalıdır (föy kuralı); bu belgedeki İngilizce raporda öyle yapıldı.",
    ])
    d.h(1, "Sık Sorulabilecek Sorular")
    qa = [
        ("Neden $V_{BE}$ 0,62 V ve neden sabit?", "Silisyum eklem için tipik iletim gerilimi; akımla logaritmik değiştiği için (60 mV/dekad) geniş akım aralığında sabit kabul edilir."),
        ("Doymada neden $V_{CE}=0{,}2$ V alıyoruz?", "Veri sayfasında maksimum $V_{CE(sat)}$=0,2 V; tipik 0,07 V. Basit model için güvenli sınır."),
        ("Aktif bölgede $V_{CE}$ en az kaç olmalı?", "Doyma sınırı 0,2 V; yükselteçte salınım için daha fazlası gerekir (Deney 5)."),
        ("Devre 1'in problemi nedir?", "Q noktası β'ya bağlı; β>184'te doyar. Çözüm: $R_E$ eklemek."),
        ("$R_E$ eklemenin bedeli?", "$R_E$ üzerinde gerilim düşer ve AC kazancı azalır (Deney 5'te bypass kondansatörüyle çözülür)."),
        ("$V_{CE}$=12 V ile $V_{CE}$=0 V arasında ayırt edici ölçüm?", "Her ikisinde de $V_{BE}$'ye bakın: 0 ise baz yolu kopuk; 0,6 civarı ise baz iletimde (doyma ya da kolektör yolu sorunu); negatif ise C–E kısa."),
    ]
    for q, a in qa:
        d.p("**S:** " + q)
        d.p("**C:** " + a)
    return d
