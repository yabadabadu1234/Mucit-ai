import numpy as np
from common import *
from docbuilder import Doc
from docs1 import n2, sci, M, cursor_table
import exp2

KP_N, KP_P = 0.1233, 150e-6


def vm_lambda0():
    kn, kp = KP_N / 2, KP_P / 2
    return (2.1 * np.sqrt(kn) + 5.0 * np.sqrt(kp)) / (np.sqrt(kn) + np.sqrt(kp))


def ds_table(d):
    rows = [
        ["Parameter", "BS170 (NMOS)", "BS250 (PMOS)"],
        ["$V_{GS(th)}$ min / typ / max", "0.8 / 2.0 / 3.0 V", "$-1.0$ / $-2.0$ / $-3.0$ V (General Semiconductor); $-1$ / – / $-3.5$ V (Diodes Inc.)"],
        ["$V_{TH}$ used in calculations", "2.0 V (typical)", "$-2.0$ V (typical)"],
        ["$I_{D(max)}$ (continuous)", "500 mA", "$-250$ mA (General Semiconductor); $-230$ mA (Diodes Inc.)"],
        ["Pin 1 / Pin 2 / Pin 3 (flat face towards the viewer, leads down)", "Drain / Gate / Source", "Source / Gate / Drain"],
    ]
    d.tab("ds", rows[0], rows[1:], "MOSFET parameters taken from the datasheets and TO-92 pin order", widths=[4.6, 3.6, 6.8], size=9)


def build_en(R):
    d = Doc("en")
    d.title_block([
        ("TOBB University of Economics and Technology", 14, True),
        ("Department of Electrical and Electronics Engineering", 12, False),
        ("ELE 224L – Electronic Circuits Laboratory", 12, False),
        ("Experiment 2 – Preliminary Work: MOSFET Circuits", 13, True),
    ], [("Name Surname", ""), ("Student ID", ""), ("Date", "")])

    d.h(1, "Introduction")
    d.h(2, "Objective of the Experiment")
    d.p("The objective of this experiment is to learn the operating principle of enhancement-mode MOSFETs, the DC biasing of a MOSFET with a resistive voltage divider, and the operation of the CMOS inverter, which is the basic cell of CMOS logic. The BS170 (N-channel) and BS250 (P-channel) transistors are studied through their datasheet parameters, hand calculations with the square-law model, and SPICE simulations.")
    d.h(2, "Benefits of the Experiment")
    d.p("The experiment shows how the datasheet parameters ($V_{TH}$, $I_{D(max)}$, pin order) are obtained and used, how the three operating regions (cut-off, saturation, triode) are identified from the voltages, and why a complementary pair conducts significant current only while the input is switching. It also develops the skills of drawing a circuit on a breadboard without wiring errors and of explaining the differences between a simple analytical model and a SPICE model.")

    d.h(1, "Calculations and Simulations")
    d.h(2, "MOSFET Properties")
    d.p("The parameters of the two transistors were taken from the datasheets and are listed in [[t:ds]]. The pin order of the two transistors is opposite: the source of the BS250 is on pin 1, whereas the source of the BS170 is on pin 3. Since both packages look identical and both are used in the same inverter circuit, this difference must be considered during wiring. The pin order of the BS250 was derived from the bottom-view drawing in its datasheet (D\u2013G\u2013S from below, i.e., S\u2013G\u2013D when the flat face is towards the viewer), and it should be confirmed on the physical part because the datasheet states that other pin configurations exist on special request. The two datasheets of the BS250 give slightly different limits ($-1.0$ to $-3.0$ V and $-1$ to $-3.5$ V for the threshold, 250 mA and 230 mA for the current) because they belong to different manufacturers, and the typical values are used in the calculations.")
    ds_table(d)

    d.h(2, "CMOS Inverter Circuit")
    d.p("The inverter was drawn on the breadboard as shown in [[f:bb]], and its circuit diagram is shown in [[f:inv]]. The source pin (S) of the PMOS is connected to $V_{DD}$, the source pin (S) of the NMOS is connected to ground, the two gates are tied together to form $V_{IN}$, and the two drains are tied together to form $V_{OUT}$. The pin order of each transistor is observed in the drawing (S–G–D for the BS250 and D–G–S for the BS170). The connections in the drawing were checked automatically against the circuit diagram of the experiment sheet.")
    d.fig("bb", R["fig_bb"], "CMOS inverter on the breadboard (BS250 PMOS on columns 6–8, BS170 NMOS on columns 16–18).", 15)
    d.fig("inv", R["fig_inv_schem"], "CMOS inverter circuit diagram.", 7.5)
    vm0 = vm_lambda0()
    vm_sp, _, vm_h = R["vm"]
    d.p("**Operating principle.** When $V_{IN}$ is below the NMOS threshold ($V_{TN}=2.1$ V in the given model), the NMOS is in cut-off and the PMOS (with $V_{SG}=V_{DD}-V_{IN}>|V_{TP}|$) pulls the output to $V_{DD}=6$ V. When $V_{IN}>V_{DD}-|V_{TP}|=5$ V, the PMOS turns off and the NMOS pulls the output to 0 V. Between these values both transistors conduct, and the output switches. The switching threshold $V_M$ (where $V_{OUT}=V_{IN}$) is found by equating the saturation currents of the two transistors. Neglecting channel-length modulation, this gives [[e:vm]].")
    d.eq(r"V_M=\frac{V_{TN}\sqrt{K_n}+\left(V_{DD}-|V_{TP}|\right)\sqrt{K_p}}{\sqrt{K_n}+\sqrt{K_p}},\qquad K_n=\frac{KP_n}{2}\frac{W}{L},\ K_p=\frac{KP_p}{2}\frac{W}{L}", "vm")
    d.p("With $KP_n=0.1233$ A/V$^2$, $KP_p=150$ µA/V$^2$ and the same $W/L$ for both transistors, $K_n=61.65$ mA/V$^2$ and $K_p=75$ µA/V$^2$. The result is $V_M=%s$ V (%s V when $\\lambda_p=0.02$ V$^{-1}$ of the PMOS model is included by solving the current equation numerically). The switching threshold is therefore not at $V_{DD}/2=3$ V, but close to the NMOS threshold, because the NMOS of the given models is about 800 times stronger than the PMOS." % (n2(vm0, 4), n2(vm_h, 4)))
    d.p("**SPICE results.** The inverter was simulated with the models given in the experiment sheet (ngspice netlist in Appendix B), with $V_{IN}=3+3\\sin(2\\pi\\cdot1\\text{ kHz}\\cdot t)$ V and $V_{DD}=6$ V. The time-domain result is shown in [[f:tran]], the $V_{IN}$–$V_{OUT}$ characteristic in [[f:vtc]], and the $V_{IN}$–$I_D$ characteristic in [[f:idv]]. The cursor coordinates are given in [[t:cur]].")
    d.fig("tran", R["fig_tran"], "$V_{IN}$ and $V_{OUT}$ of the CMOS inverter versus time (ngspice simulation).", 14)
    d.fig("vtc", R["fig_vtc"], "$V_{IN}$–$V_{OUT}$ characteristic of the inverter ($V_{IN}$ on the x-axis, $V_{OUT}$ on the y-axis) (ngspice simulation and hand model).", 11)
    d.fig("idv", R["fig_idv"], "$V_{IN}$–$I_D$ characteristic of the inverter ($V_{IN}$ on the x-axis, $I_D$ on the y-axis) (ngspice simulation and hand model).", 11)
    (t1, a1, b1), (t2, a2, b2) = R["cur_tran"]
    ipk = R["ipk"]
    d.tab("cur", ["Figure", "Cursor", "x", "y"], [
        ["[[f:tran]]", "X1 ($V_{IN}$)", "%s ms" % n2(t1 * 1e3, 3), "%s V" % n2(a1, 4)],
        ["[[f:tran]]", "X2 ($V_{OUT}$)", "%s ms" % n2(t2 * 1e3, 3), "%s V" % n2(b2, 4)],
        ["[[f:vtc]]", "$V_M$", "%s V ($V_{IN}$)" % n2(vm_sp, 4), "%s V ($V_{OUT}$)" % n2(vm_sp, 4)],
        ["[[f:idv]]", "peak $I_D$", "%s V ($V_{IN}$)" % n2(ipk[0], 4), "%s mA" % n2(ipk[1] * 1e3, 4)]],
        "Cursor coordinates read from the simulation figures", widths=[2.2, 3.2, 4.2, 4.2])
    rows = []
    for v, voh, vos, ih, is_, rn, rp in R["inv_tab"]:
        rows.append([n2(v, 3), n2(voh, 4), n2(vos, 4), n2(ih * 1e3, 4) if ih > 0 else "0", n2(is_ * 1e3, 4) if is_ > 1e-9 else "≈0", rn + " / " + rp])
    d.tab("inv", ["$V_{IN}$ (V)", "$V_{OUT}$ hand (V)", "$V_{OUT}$ SPICE (V)", "$I_D$ hand (mA)", "$I_D$ SPICE (mA)", "NMOS / PMOS region (hand)"], rows,
          "Hand calculation (square-law model) versus SPICE for the CMOS inverter", widths=[1.9, 2.5, 2.5, 2.4, 2.4, 3.8], size=9)
    d.p("The behaviour in [[f:tran]] is explained as follows. While $V_{IN}$ is below about 2.1 V, the output is held at 6 V; while $V_{IN}$ is above about 2.3 V, the output is almost 0 V. Since the transition range is only about 0.2 V wide, the output is practically a square wave although the input is a sinusoid, and its transitions occur close to the lower part of the input swing (at about 2.2 V instead of 3 V), so the output stays low for more than half of the period. In [[f:idv]], the current is zero for $V_{IN}<2.1$ V (NMOS off) and for $V_{IN}>5$ V (PMOS off), and it is maximum (%s mA) at $V_{IN}\\approx%s$ V, where both transistors conduct at the same time. The peak is determined by the weaker PMOS: the current that the PMOS can supply in saturation with $V_{SG}=%s$ V is $K_p(V_{SG}-|V_{TP}|)^2\\approx%s$ mA (about 6%% more when its channel-length modulation is included). According to the hand model, the regions change at $V_{IN}=%.2f$ V (NMOS turns on), %.2f V (PMOS enters saturation), %.2f V (NMOS enters triode), and %.2f V (PMOS turns off)." % (
        n2(ipk[1] * 1e3, 3), n2(ipk[0], 3), n2(6 - ipk[0], 3), n2(75e-6 * (6 - ipk[0] - 1) ** 2 * 1e3, 3), R["b_nmos_on"], R["b_pmos_sat"], R["b_nmos_tri"], R["b_pmos_off"]))

    d.h(2, "MOSFET Bias (Common-Source) Circuit")
    d.p("The circuit of the experiment sheet consists of the divider $R_{G1}=33$ k$\\Omega$ and $R_{G2}=120$ k$\\Omega$ driving the gate of an NMOS whose source is grounded and whose drain is connected directly to $V_2=5$ V. Since the gate current of a MOSFET is zero, the divider is unloaded and the gate voltage is given by [[e:div]]. The drain-source voltage is fixed by the supply, $V_{DS}=V_2=5$ V.")
    d.eq(r"V_{GS}=V_1\,\frac{R_{G2}}{R_{G1}+R_{G2}}=\frac{120}{153}V_1\ \Longrightarrow\ V_1=\frac{153}{120}V_{GS}=1.275\,V_{GS}", "div")
    d.p("For a transistor in saturation, the square-law model of [[e:sq]] is used with the given $K_N=72$ mA/V$^2$ and the typical datasheet threshold $V_{TH}=2.0$ V. This form of the model (with the factor 1/2) was chosen because it reproduces two independent datasheet values of the BS170: it gives $r_{DS(on)}=1/[K_N(V_{GS}-V_{TH})]=%s\\ \\Omega$ at $V_{GS}=10$ V (datasheet typical: 1.8 $\\Omega$) and $g_m=\\sqrt{2K_NI_D}=%.0f$ mS at $I_D=250$ mA (datasheet typical: 200 mS), whereas the form without the factor 1/2 would give %.2f $\\Omega$ and %.0f mS." % (n2(R["rds_on"], 3), R["gfs"] * 1e3, R["rds_neamen"], R["gfs_neamen"] * 1e3))
    d.eq(r"I_D=\frac{K_N}{2}\left(V_{GS}-V_{TH}\right)^2\ \Longleftrightarrow\ V_{GS}=V_{TH}+\sqrt{\frac{2I_D}{K_N}}", "sq")
    d.p("The saturation condition $V_{DS}\\geq V_{GS}-V_{TH}$ is checked for every column: since $V_{DS}=5$ V, it holds up to $V_{GS}=7$ V. As an example, for $I_D=10$ mA, $V_{GS}=2.0+\\sqrt{2\\cdot10/72}=%s$ V and $V_1=1.275\\times%s=%s$ V; for $V_{GS}=4$ V, $I_D=36\\cdot(4-2)^2=144$ mA. The other columns are calculated in the same way and are given in [[t:bias]]." % (n2(R["bs_th"][2][2], 4), n2(R["bs_th"][2][2], 4), n2(R["bs_th"][2][4], 4)))
    cols = R["bs_th"]
    hdr = ["$I_D$ (mA)"] + [("0" if c[1] == 0 else n2(c[1] * 1e3, 4 if c[0] == "VGS" else 3)) for c in cols]
    rows = [["$V_{GS}$ (V)"] + [("0" if c[2] == 0 else n2(c[2], 4)) for c in cols],
            ["$V_{DS}$ (V)"] + ["5"] * 8,
            ["$V_1$ (V)"] + [("0" if c[4] == 0 else n2(c[4], 4)) for c in cols]]
    d.tab("bias", hdr, rows, "Calculated values of the MOSFET bias circuit (square-law model, $K_N$ = 72 mA/V$^2$, $V_{TH}$ = 2.0 V)", widths=[2.2] + [1.6] * 8, size=8.5)
    d.p("The three last columns ($V_{GS}=3$, 4 and 5 V) require attention: the calculated drain currents are 36 mA, 144 mA and 324 mA, and with $V_{DS}=5$ V the transistor would dissipate 0.18 W, 0.72 W and 1.62 W. The datasheet gives a total dissipation of 350 mW for the BS170, so the 144 mA and 324 mA points (and also 100 mA at 0.5 W) cannot be applied continuously on hardware, although they are harmless in a simulation. The cut-off column ($I_D=0$) is valid for any $V_{GS}\\leq V_{TH}$.")
    d.p("**SPICE.** The circuit was built with the BS170 model, $V_1$ was swept from 0 V to 12.75 V ($V_{GS}$ from 0 V to 10 V), and the $I_D$–$V_{GS}$ graph of [[f:idvgs]] was obtained. In the hand calculation, the $V_1$ values of [[t:bias]] were applied to the SPICE circuit, and the results are compared in [[t:bsp]].")
    d.fig("idvgs", R["fig_idvgs"], "$I_D$–$V_{GS}$ characteristic of the BS170 circuit ($V_{GS}$ on the x-axis, $I_D$ on the y-axis) with the operating regions and the pinch-off point (left); square-root plot for the threshold voltage (right) (ngspice simulation).", 15.5)
    cursor_table(d, "e2_idvgs", "idvgs")
    rows = []
    for (kind, i, vgs, vds, v1), sp in zip(R["bs_th"], R["bs_sp"]):
        if kind == "ID":
            if i == 0:
                rows.append(["0 (given)", "—", "—", "—"])
            else:
                rows.append(["%s (given)" % n2(i * 1e3, 3), n2(vgs, 4), n2(sp[2], 4), "%+.1f%%" % pct_err(vgs, sp[2])])
        else:
            rows.append(["%s (from $V_{GS}$=%d V)" % (n2(i * 1e3, 4), int(vgs)), n2(i * 1e3, 4), n2(sp[1] * 1e3, 4), "%+.1f%%" % pct_err(i, sp[1])])
    d.tab("bsp", ["Column", "Hand", "SPICE", "Error"], rows, "Hand calculation versus SPICE for the bias circuit (first rows: $V_{GS}$ in V required for the given $I_D$ in mA; last rows: $I_D$ in mA at the given $V_{GS}$)", widths=[5.6, 3, 3, 2.4], size=9)
    pv = R["pinch"]
    d.p("**Operating regions and pinch-off.** In [[f:idvgs]], the transistor is in cut-off for $V_{GS}<V_{TH}$ (the current is practically zero), in saturation (square-law region, $\\sqrt{I_D}$ linear in $V_{GS}$) for larger $V_{GS}$, and in the triode region after the pinch-off point. The pinch-off point is the point at which $V_{DS}=V_{GS}-V_{TH}$ and the channel at the drain end is pinched off. With the ideal square-law model, it occurs at $V_{GS}=V_{DS}+V_{TH}=5+2.0=%.1f$ V ($I_D=%.0f$ mA). In the SPICE model, the drain and source series resistances ($R_D=1.436\\ \\Omega$, $R_S=1.572\\ \\Omega$) reduce the internal $V_{DS}$ and $V_{GS}$ at large currents, and the pinch-off occurs earlier: at $V_{GS}=%.2f$ V and $I_D=%.0f$ mA, which is marked in the figure. Both points are beyond the 500 mA datasheet limit, so they are not reachable in a hardware experiment. The threshold extracted from the square-root plot is %.2f V, which agrees with the model parameter $V_{TO}=2.1$ V." % (pv[2], pv[3] * 1e3, pv[0], pv[1] * 1e3, R["vth_extr"]))

    d.h(1, "Conclusions")
    th_, sp_ = R["bs_th"], R["bs_sp"]
    vg_err = ["%+.1f%%" % pct_err(th_[k][2], sp_[k][2]) for k in (1, 2, 3, 4)]
    id_err = ["%+.1f%%" % pct_err(th_[k][1], sp_[k][1]) for k in (5, 6, 7)]
    d.p("The datasheet reading showed that the BS170 and BS250 have opposite pin orders (D\u2013G\u2013S and S\u2013G\u2013D). If one of them is inserted with the pin pattern of the other, the gate stays on the middle pin but the source and the drain are exchanged, so the transistor does not work as intended (the body diode conducts). The switching threshold of the CMOS inverter was found as %s V in SPICE and %s V in the hand model, a difference of %.1f mV, which is caused by the series resistances of the model and by the interpolation of the sweep. Outside the narrow transition region, the hand model and SPICE agree to within a few millivolts. Inside the transition region, a few millivolts of difference in $V_{IN}$ changes $V_{OUT}$ by volts (for example, at $V_{IN}=2.20$ V the hand model gives %s V and SPICE %s V), because the voltage gain is very high there; this is also the reason why the inverter works as a digital element." % (n2(vm_sp, 4), n2(vm_h, 4), abs(vm_sp - vm_h) * 1e3, n2(R["inv_tab"][5][1], 3), n2(R["inv_tab"][5][2], 3)))
    d.p("In the bias circuit, the gate voltage required by SPICE for $I_D$ = 1, 10, 50 and 100 mA differs from the hand calculation by %s, %s, %s and %s, respectively, and the SPICE drain current at $V_{GS}$ = 3, 4 and 5 V is higher than the hand-calculated current by %s, %s and %s (the difference in current is larger than the difference in voltage, since the current depends on the square of $V_{GS}-V_{TH}$). The reasons are the larger transconductance parameter of the SPICE model ($KP\\cdot W/L=123.3$ mA/V$^2$, i.e., 61.65 mA/V$^2$ in the $K/2$ form, against $K_N/2=36$ mA/V$^2$), the different threshold ($V_{TO}=2.1$ V against 2.0 V), and the series resistances $R_D$ and $R_S$ of the model, which reduce the internal $V_{GS}$ at high currents. The datasheet range of $V_{GS(th)}=0.8$\u20133.0 V shows that the real bias point also changes strongly from device to device, so the gate voltage must be adjusted for each transistor in the laboratory. The experiment taught the use of datasheets, the identification of operating regions, and the comparison of an analytical model with a SPICE model." % (*vg_err, *id_err))

    d.h(1, "References")
    d.bullets([
        "ON Semiconductor. (2017). BS170 small signal MOSFET 500 mA, 60 volts [Data sheet]. Retrieved October 11, 2026, from https://www.onsemi.com/download/data-sheet/pdf/bs170-d.pdf",
        "General Semiconductor. (1999). BS250 DMOS transistor (P-channel) [Data sheet]. Retrieved October 11, 2026, from https://hippo.feld.cvut.cz/katalog/pdf/BS250.PDF",
        "Diodes Incorporated. (2019). BS250P P-channel enhancement mode vertical DMOS FET [Data sheet]. Retrieved October 11, 2026, from https://www.diodes.com/assets/Datasheets/BS250P.pdf",
        "Sedra, A. S., & Smith, K. C. (2014). Microelectronic circuits (7th ed.). New York: Oxford University Press.",
        "ngspice. (n.d.). ngspice user manual. Retrieved October 11, 2026, from https://ngspice.sourceforge.io/docs.html",
    ], numbered=True)
    d.h(1, "Appendices")
    d.h(2, "Appendix A: Model Definitions")
    d.p("The model definitions of the experiment sheet were used. In the ngspice simulation, the parameters RG, RB, Rds and Tt, which are not available in the level-1 model of ngspice, were omitted; they have no effect on the DC results (RG is a gate series resistor without gate current, Rds = 120 M$\\Omega$ is practically an open circuit, and Tt only affects the bulk-diode charge).")
    d.code(exp2.NM + "\n" + exp2.PM, "Code A.1  Model lines used in the ngspice simulations")
    d.h(2, "Appendix B: SPICE Netlists")
    d.code(clean_cir(os.path.join(SPICE, "e2_inv_tran.cir")), "Netlist B.1  CMOS inverter transient analysis")
    d.code(clean_cir(os.path.join(SPICE, "e2_bs_dc.cir")), "Netlist B.2  BS170 bias circuit DC sweep")
    return d


def build_tr(R):
    d = Doc("tr")
    d.title_block([
        ("Deney 2 – Ön Çalışma Öğretici Rehberi", 15, True),
        ("MOSFET Devreleri (ELE 224L Elektronik Devreler Laboratuvarı)", 12, False),
        ("Bu belge SADECE ÖĞRENMEK içindir; teslim edilecek metin İngilizce rapordur.", 11, False),
    ], [("Ad Soyad", ""), ("Numara", ""), ("Tarih", "")])
    vm0 = vm_lambda0()
    vm_sp, _, vm_h = R["vm"]
    ipk = R["ipk"]
    pv = R["pinch"]

    d.h(1, "Bu Deney Neyi Öğretiyor?")
    d.p("MOSFET, **gerilimle kontrol edilen bir musluktur**: kapı (gate) ucuna uygulanan gerilim, kaynak (source) ile savak (drain) arasından geçecek akımı belirler. Bu deney üç şeyi öğretir: (1) veri sayfasından (datasheet) doğru parametreyi bulmak ve bacakları doğru bağlamak; (2) tek bir MOSFET'i bir gerilim bölücüyle kutuplayıp çalışma bölgesini belirlemek; (3) bir N-kanal ve bir P-kanal MOSFET'i birleştirip dijital elektroniğin temel taşı olan **CMOS eviriciyi** (inverter) anlamak.")
    d.box("Tek cümlelik özet", ["NMOS: $V_{GS}$ eşiği aşınca **açılır**. PMOS: kapı gerilimi kaynak geriliminden eşik kadar **aşağı** inince açılır. Evirici: ikisini seri bağlayıp kapılarını birleştirirsek, giriş yüksekken çıkış alçak, giriş alçakken çıkış yüksek olur.",])

    d.h(1, "Temel Bilgi: Geliştirme Modlu MOSFET")
    d.h(2, "Dört bölge, üç terminal")
    d.p("Kapı (G), savak (D), kaynak (S) üç terminaldir (gövde/body kaynağa bağlı kabul edilir). Kapı, kanaldan ince bir oksit tabaka ile yalıtılmıştır; bu yüzden **DC kapı akımı sıfırdır**. Bu çok önemlidir: kapıya bağlı bir gerilim bölücü yüklenmez; $V_G$ doğrudan bölücü formülüyle bulunur.")
    d.p("N-kanal geliştirme (enhancement) MOSFET'te $V_{GS}$ eşik gerilimi $V_{TH}$'ı aşmadıkça kanal oluşmaz ve akım akmaz. $V_{GS}>V_{TH}$ olunca kapının altında elektronlardan oluşan bir kanal doğar. Üç çalışma bölgesi vardır ($V_{OV}=V_{GS}-V_{TH}$ aşırı sürme gerilimidir):")
    d.bullets([
        "**Kesim (cut-off):** $V_{GS}\\leq V_{TH}$ ⇒ $I_D\\approx0$.",
        "**Triyot (doğrusal) bölge:** $V_{GS}>V_{TH}$ ve $V_{DS}<V_{OV}$ ⇒ MOSFET gerilimle ayarlanan bir direnç gibidir: $I_D=K_N\\left[(V_{GS}-V_{TH})V_{DS}-\\tfrac{1}{2}V_{DS}^2\\right]$.",
        "**Doyma (saturation) bölgesi:** $V_{GS}>V_{TH}$ ve $V_{DS}\\geq V_{OV}$ ⇒ akım $V_{DS}$'e bağlı değildir (akım kaynağı gibi): $I_D=\\tfrac{K_N}{2}(V_{GS}-V_{TH})^2$.",
    ])
    d.box("Pinch-off (sıkışma) ne demek?", [
        "$V_{DS}$ büyüdükçe savak ucundaki kanal inceleir; $V_{DS}=V_{GS}-V_{TH}$ olduğunda savak ucunda kanal kalınlığı sıfıra iner, yani kanal \"sıkışır\". Bu nokta triyot ile doyma arasındaki sınırdır. Bu devrede $V_{DS}$ sabit 5 V olduğundan, $V_{GS}$ arttıkça **bir noktada** $V_{GS}-V_{TH}$ 5 V'a ulaşır; işte o $V_{GS}$ değeri pinch-off noktasıdır: $V_{GS}=V_{DS}+V_{TH}$.",
    ])
    d.h(2, "K_N tanımı ve neden 1/2 çarpanı")
    d.p("Kaynaklarda $K$ iki farklı şekilde tanımlanır: (a) $I_D=\\tfrac{K}{2}(V_{GS}-V_{TH})^2$ (Sedra–Smith tarzı), (b) $I_D=K(V_{GS}-V_{TH})^2$ (Neamen tarzı). Föy yalnızca \"$K_N=72$ mA/V²\" diyor, bu yüzden hangisinin kastedildiğini **veri sayfasıyla sınadık**:")
    d.tab("kn", ["Büyüklük", "Veri sayfası (tipik)", "(a) $K/2$ tanımı", "(b) $K$ tanımı"],
          [["$r_{DS(on)}$ ($V_{GS}$=10 V)", "1,8 Ω", "%s Ω" % n2(R["rds_on"], 3), "%s Ω" % n2(R["rds_neamen"], 3)],
           ["$g_{fs}$ ($I_D$=250 mA)", "200 mS", "%.0f mS" % (R["gfs"] * 1e3), "%.0f mS" % (R["gfs_neamen"] * 1e3)]],
          "$K_N$ = 72 mA/V² tanımının veri sayfasıyla sınanması", widths=[4.2, 3.6, 3.6, 3.6])
    d.p("(a) iki değeri de tutturuyor (yaklaşık %4 ve %5 sapma), (b) ikisini de tutturamıyor (2 kat ve %34 sapma). Bu yüzden bütün hesaplarda **(a)** kullanıldı: $I_D=\\tfrac{K_N}{2}(V_{GS}-V_{TH})^2$. Hocanız (b)'yi kullanıyorsa $I_D$ değerleri iki katı, $V_{OV}$ değerleri ise $1/\\sqrt2$ katı olur; hesap yöntemi aynıdır. **Raporda kullandığınız tanımı mutlaka yazın.**")
    d.h(2, "Veri sayfasından ne okunur?")
    ds_table(d)
    d.bullets([
        "**$V_{GS(th)}$** aynı model numaralı transistörlerde bile geniş yayılır (BS170: 0,8–3,0 V). Hesaplarda \"tipik\" değer (2,0 V) kullanılır; ama gerçek devrede her transistör farklı çıkar. Şekil [[f:vthsp]] bunun akım üzerindeki etkisini gösterir.",
        "**Bacak sırası TERS:** BS170: D-G-S (onsemi veri sayfası, doğrudan okundu); BS250: S-G-D (General Semiconductor veri sayfasındaki ALTTAN görünüş çiziminde D-G-S yazıyor; düz yüzden bakınca sıra tersine döner — bu çıkarım bana ait; veri sayfası özel istekle başka bacak düzeni de üretildiğini söylüyor, bu yüzden parçanızı fiziksel olarak da doğrulayın). Yanlış takarsanız kaynak ile savak yer değiştirir ve gövde diyodu yüzünden devre çalışmaz ya da transistör ısınır.",
        "**$I_{D(max)}$** tek başına yetmez: güç sınırı vardır. BS170 toplam güç kaybı 350 mW (onsemi); $V_{DS}$=5 V'ta bu yalnızca ~70 mA'e karşılık gelir.",
    ])
    d.fig("vthsp", R["fig_vth_spread"], "Veri sayfasındaki $V_{TH}$ yayılımının akıma etkisi.", 11)

    d.h(1, "Soru 2: CMOS Evirici")
    d.h(2, "Breadboard çizimi nasıl okunur?")
    d.p("Breadboard'da her sütunun beş deliği (a–e ya da f–j) elektriksel olarak birbirine bağlıdır; ortadaki boşluk iki yarıyı ayırır; üst ve alt kenardaki ray çiftleri boydan boya bağlıdır. Çizimde transistörlerin bacakları e sırasındadır; her bacağın bulunduğu sütundaki diğer deliklere (a–d) tel ya da başka eleman bağlanır.")
    d.fig("bb", R["fig_bb"], "CMOS eviricinin breadboard çizimi (bağlantılar otomatik denetlendi).", 15)
    d.bullets([
        "Kırmızı tel: + rayından PMOS kaynağının (S) sütununa → $V_{DD}$.",
        "Siyah tel: − rayından NMOS kaynağının (S) sütununa → toprak.",
        "Mavi tel: iki kapının sütunlarını birleştirir → $V_{IN}$ (fonksiyon üretecinin ucu da bu sütuna).",
        "Turuncu tel: iki savağın sütunlarını birleştirir → $V_{OUT}$ (osiloskop probu bu sütunda).",
    ])
    d.fig("inv", R["fig_inv_schem"], "CMOS evirici devre şeması.", 7.5)
    d.h(2, "Evirici nasıl çalışır?")
    d.p("$V_{DD}=6$ V. NMOS için $V_{TN}=2{,}1$ V, PMOS için $V_{TP}=-1{,}0$ V (föydeki modeller). Üç durum:")
    d.bullets([
        "**$V_{IN}<2{,}1$ V:** NMOS kesimde. PMOS'un $V_{SG}=6-V_{IN}>1$ V olduğundan açık. PMOS çıkışı $V_{DD}$'ye çeker ⇒ $V_{OUT}=6$ V. Akım yok (NMOS kapalı).",
        "**$V_{IN}>5$ V:** $V_{SG}<1$ V ⇒ PMOS kapalı. NMOS açık ve çıkışı toprağa çeker ⇒ $V_{OUT}\\approx0$. Akım yok (PMOS kapalı).",
        "**Aradaki bölge:** İkisi de açıktır; çıkış bir transistörün tarafından yukarı, diğerinden aşağı çekilir. Akım **yalnızca bu geçiş sırasında** akar (CMOS'un düşük güç tüketiminin sebebi).",
    ])
    d.p("**Eşik gerilimi $V_M$** ($V_{OUT}=V_{IN}$ olduğu nokta): iki transistör de doymadayken akımlar eşitlenir:")
    d.eq(r"K_n\left(V_M-V_{TN}\right)^2=K_p\left(V_{DD}-V_M-|V_{TP}|\right)^2\ \Rightarrow\ V_M=\frac{V_{TN}\sqrt{K_n}+(V_{DD}-|V_{TP}|)\sqrt{K_p}}{\sqrt{K_n}+\sqrt{K_p}}", "vm")
    d.p("Burada $K_n=\\tfrac{KP_n}{2}\\tfrac{W}{L}=61{,}65$ mA/V² ve $K_p=\\tfrac{KP_p}{2}\\tfrac{W}{L}=75$ µA/V² (SPICE'ın varsayılan $W/L=1$'i). Sonuç: $V_M=%s$ V (λ dahil sayısal çözümle %s V; SPICE: %s V). **Dikkat:** bu $V_{DD}/2=3$ V değildir! Çünkü föydeki NMOS modeli PMOS'tan yaklaşık 800 kat güçlü ($K_n/K_p=%.0f$). Güçlü olan transistör az bir kapı gerilimiyle akımı karşılayabildiği için geçiş NMOS eşiğine yakın bir yerde olur. Dengeli bir evirici için PMOS'un $W/L$ oranı büyütülürdü; burada büyütülmedi." % (n2(vm0, 4), n2(vm_h, 4), n2(vm_sp, 4), (KP_N / 2) / (KP_P / 2)))
    d.h(2, "SPICE sonuçları ve nasıl yorumlanır")
    d.fig("tran", R["fig_tran"], "$V_{IN}$ ve $V_{OUT}$ zaman grafiği.", 14)
    d.p("Giriş sinüs ($0\\ldots6$ V, ortalama 3 V). Çıkış ise 6 V ile ≈0 V arasında geçen neredeyse kare bir dalgadır; çünkü geçiş bölgesi yalnızca ~0,2 V genişliğindedir. Geçişin girişin 3 V'luk orta noktasında değil ~2,2 V'ta olması yüzünden çıkış periyodun yarısından fazla süre **alçak** kalır (duty < %50: çıkış yüksek olduğu süre azdır).")
    d.fig("vtc", R["fig_vtc"], "$V_{IN}$–$V_{OUT}$ karakteristiği ($V_{IN}$ x ekseninde).", 11)
    d.fig("idv", R["fig_idv"], "$V_{IN}$–$I_D$ karakteristiği ($V_{IN}$ x ekseninde).", 11)
    d.p("Akım grafiğinin okunuşu: iki ucu sıfır (bir transistör kapalı), ortada tek bir tepe: %s mA, $V_{IN}=%s$ V'ta. Tepe değerini zayıf transistör (PMOS) belirler: $\\approx K_p(V_{SG}-|V_{TP}|)^2=75\\ \\mu\\text{A/V}^2\\times(%s-1)^2\\approx%s$ mA. Bu akım **kısa devre (shoot-through) akımıdır**; hızlı anahtarlamada çok sayıda eviricide toplam güç kaybının önemli kısmını oluşturur." % (n2(ipk[1] * 1e3, 3), n2(ipk[0], 3), n2(6 - ipk[0], 3), n2(75e-6 * (6 - ipk[0] - 1) ** 2 * 1e3, 3)))
    rows = []
    for v, voh, vos, ih, is_, rn, rp in R["inv_tab"]:
        rows.append([n2(v, 3), n2(voh, 4), n2(vos, 4), n2(ih * 1e3, 4) if ih > 0 else "0", n2(is_ * 1e3, 4) if is_ > 1e-9 else "≈0", rn + " / " + rp])
    d.tab("inv", ["$V_{IN}$ (V)", "$V_{OUT}$ el (V)", "$V_{OUT}$ SPICE (V)", "$I_D$ el (mA)", "$I_D$ SPICE (mA)", "NMOS / PMOS bölgesi"], rows, "El modeli ile SPICE karşılaştırması", widths=[1.9, 2.5, 2.5, 2.4, 2.4, 3.8], size=9)
    d.bullets([
        "El hesabı = föydeki SPICE modelinin 1. seviye denklemleri (λ dahil); SPICE ile fark çok küçüktür (ör. $V_M$'de 0,001 V); bu hem modelin hem hesabın doğru olduğunu gösterir.",
        "$V_{IN}=2{,}2$ V'ta el modeli %s V, SPICE %s V verir: fark büyük görünür ama giriş farkı sadece mV'tur; bu bölgede kazanç (eğim) yüzlerce olduğu için küçük bir mV farkı volt farkı yapar. Bu sebeple geçiş bölgesinde \"hata yüzdesi\" yanıltıcıdır; asıl bakılacak şey eşik gerilimi $V_M$'dir." % (n2(R["inv_tab"][5][1], 3), n2(R["inv_tab"][5][2], 3)),
        "Bölge sınırları (el modeli): NMOS %.2f V'ta açılır; PMOS %.2f V'ta doymaya girer; NMOS %.2f V'ta triyota girer; PMOS %.2f V'ta kapanır." % (R["b_nmos_on"], R["b_pmos_sat"], R["b_nmos_tri"], R["b_pmos_off"]),
    ])

    d.h(1, "Soru 3: MOSFET Kutuplama Devresi (Tablo 1 ve SPICE)")
    d.h(2, "Adım adım hesap")
    d.p("Devre: $V_1$ → $R_{G1}$=33 kΩ → kapı düğümü → $R_{G2}$=120 kΩ → toprak. Kaynak topraklı, savak doğrudan $V_2$=5 V'a bağlı. Kapı akımı sıfır olduğundan bölücü yüksüzdür:")
    d.eq(r"V_{GS}=V_1\,\frac{R_{G2}}{R_{G1}+R_{G2}}=\frac{120}{153}V_1\ \Longrightarrow\ V_1=1.275\,V_{GS}", "div")
    d.p("Savak doğrudan 5 V'a bağlı ve kaynak topraklı olduğundan **$V_{DS}=5$ V sabittir** (savakta direnç yok, o yüzden akımdan bağımsız). Tabloyu doldurma stratejisi: iki tür sütun var.")
    d.bullets([
        "**$I_D$ verilen sütunlar (0, 1, 10, 50, 100 mA):** $V_{GS}=V_{TH}+\\sqrt{2I_D/K_N}$; sonra $V_1=1{,}275V_{GS}$. Örnek ($I_D=10$ mA): $V_{GS}=2+\\sqrt{2\\cdot10/72}=2+0{,}527=2{,}527$ V; $V_1=3{,}222$ V. ($I_D=0$ sütunu için tablo $V_{GS}=0$ vermiş: kesimde, $V_1=0$.)",
        "**$V_{GS}$ verilen sütunlar (3, 4, 5 V):** $I_D=\\tfrac{K_N}{2}(V_{GS}-V_{TH})^2$. Örnek ($V_{GS}=4$ V): $36\\cdot(4-2)^2=144$ mA.",
        "**Doğrulama (her sütun):** $V_{DS}\\geq V_{GS}-V_{TH}$ ⇒ 5 ≥ $V_{GS}-2$ ⇒ $V_{GS}\\leq7$ V. Hepsi doymada.",
    ])
    cols = R["bs_th"]
    hdr = ["$I_D$ (mA)"] + [("0" if c[1] == 0 else n2(c[1] * 1e3, 4 if c[0] == "VGS" else 3)) for c in cols]
    rows = [["$V_{GS}$ (V)"] + [("0" if c[2] == 0 else n2(c[2], 4)) for c in cols], ["$V_{DS}$ (V)"] + ["5"] * 8, ["$V_1$ (V)"] + [("0" if c[4] == 0 else n2(c[4], 4)) for c in cols]]
    d.tab("bias", hdr, rows, "Föy Tablo 1'in hesaplanmış hâli", widths=[2.2] + [1.6] * 8, size=8.5)
    d.box("Güvenlik uyarısı", ["$V_{GS}=4$ V ve 5 V sütunlarında akım 144 mA ve 324 mA, $V_{DS}=5$ V olduğu için güç 0,72 W ve 1,62 W eder. BS170 350 mW'a dayanır. Yani bu iki noktayı **gerçek devrede sürekli uygulamayın** (ya da çok kısa tutun); simülasyonda sakıncası yoktur. Hesapta $I_{D(max)}$=500 mA sınırının güç sınırından daha gevşek olduğunu görürsünüz: tek bir sınıra bakmak yetmez."])
    d.h(2, "SPICE ve karşılaştırma")
    d.fig("idvgs", R["fig_idvgs"], "Sol: $I_D$–$V_{GS}$ ve çalışma bölgeleri; sağ: $\\sqrt{I_D}$–$V_{GS}$ grafiğinden eşik çıkarımı.", 15.5)
    rows = []
    for (kind, i, vgs, vds, v1), sp in zip(R["bs_th"], R["bs_sp"]):
        if kind == "ID":
            rows.append(["0 (verilen)", "—", "—", "—"] if i == 0 else ["%s mA (verilen) → $V_{GS}$ (V)" % n2(i * 1e3, 3), n2(vgs, 4), n2(sp[2], 4), "%+.1f%%" % pct_err(vgs, sp[2])])
        else:
            rows.append(["$V_{GS}$=%d V → $I_D$ (mA)" % int(vgs), n2(i * 1e3, 4), n2(sp[1] * 1e3, 4), "%+.1f%%" % pct_err(i, sp[1])])
    d.tab("bsp", ["Sütun", "El", "SPICE", "Hata"], rows, "El hesabı ile SPICE", widths=[6, 3, 3, 2.4], size=9)
    d.p("**Neden fark var?** (i) SPICE modelinde $KP\\cdot W/L=123{,}3$ mA/V² (yani $K/2=61{,}65$) var; föyde $K_N/2=36$. SPICE'ın transistörü hesabımızdan daha 'güçlü'dür: aynı akım için daha küçük $V_{GS}$ gerekir. (ii) SPICE'ta $V_{TO}=2{,}1$ V, hesapta 2,0 V. (iii) $R_D=1{,}436\\ \\Omega$ ve $R_S=1{,}572\\ \\Omega$ seri dirençleri yüksek akımda ($>100$ mA) iç $V_{GS}$'yi düşürür. Bu etkiler sonucunda verilen $I_D$ için gereken $V_{GS}$ farkı %0–4, verilen $V_{GS}$ için akım farkı ise %6–19 mertebesindedir (akım, $V_{GS}-V_{TH}$'ın karesine bağlı olduğundan küçük bir gerilim farkı akımda büyür); hata hesap hatası değildir, **model farkıdır**.")
    d.p("**Pinch-off noktası:** ideal karesel modelde $V_{GS}=5+2{,}0=%.1f$ V (akım %.0f mA); SPICE'ta seri dirençler yüzünden %.2f V'ta ve %.0f mA'de (grafikte çarpıyla işaretli). İkisi de veri sayfası sınırı olan 500 mA'in üstünde. Eşik gerilimi grafiğinden: $\\sqrt{I_D}$ düz çizgi olduğundan çizgiyi $I_D=0$'a uzatınca $V_{TH}=%.2f$ V bulunur (modelin $V_{TO}=2{,}1$ V'u ile uyumlu)." % (pv[2], pv[3] * 1e3, pv[0], pv[1] * 1e3, R["vth_extr"]))
    d.box("Alternatif tanım ($I_D=K_N(V_{GS}-V_{TH})^2$) kullanılırsa", [
        "$V_{GS}=V_{TH}+\\sqrt{I_D/K_N}$ ve $I_D=K_N(V_{GS}-V_{TH})^2$. Sayılar: $I_D=10$ mA için $V_{GS}=2{,}373$ V; 100 mA için 3,178 V; $V_{GS}=3,4,5$ V için $I_D=72, 288, 648$ mA (648 mA > 500 mA sınırı!). Pinch-off: 7,0 V.",
    ], fill="FFF4E0")

    d.h(1, "Programda Nasıl Yapılır? (LTspice / Micro-Cap)")
    d.bullets([
        "LTspice'ta `nmos` ve `pmos` sembollerini yerleştirin, sağ tıklayıp model adlarını `BS170` ve `BS250` yapın. Föydeki iki `.model` satırını `.op` ile birlikte bir SPICE direktifi olarak (S tuşu) şematiğe yazın. **Bu satırlar LTspice'ta olduğu gibi çalışır; ngspice'ta RG, RB, Rds, Tt parametreleri desteklenmediği için çıkarılmıştır** (DC sonuçları etkilemez).",
        "Zaman analizi için kaynağı `SINE(3 3 1k)` yapın: ofset 3 V, genlik 3 V, 1 kHz. $V_{DD}$ = 6 V DC. Çıkış düğümüne etiket verin; `.tran 3m`.",
        "$V_{IN}$–$V_{OUT}$ için `.dc Vin 0 6 0.005` kullanın; $V_{OUT}$ trace'i eklenir. Akım için $V_{DD}$ kaynağının akımı (`I(Vdd)`) ya da NMOS'un `Id(M1)` izi alınır (LTspice'ta işareti kaynak tanımına göre eksi olabilir).",
        "BS170 kutuplama devresi için `.dc V1 0 12.75 0.01` ve trace olarak `Id(M1)` ile `V(g)`; x eksenini $V(g)$ yapın. İmleç (cursor) ve seri numarası kuralı için Deney 1 rehberine bakın.",
        "Micro-Cap'te hazır MOSFET modelleri kütüphanede vardır; ancak föydeki modeli kullanmanız isteniyorsa `.model` satırlarını *Text* olarak şematiğe ekleyin.",
    ])
    d.p("Menü adlarını kendi programınızda doğrulayın; bu ortamda LTspice/Micro-Cap yoktu, netlistler `spice/` klasöründedir (ngspice sözdizimi; LTspice'ta `File→Open` ile açılabilir).")

    d.h(1, "Sık Sorulabilecek Sorular")
    qa = [
        ("MOSFET'te kapı akımı neden sıfır?", "Kapı oksitle yalıtılmıştır; DC'de akım geçmez. Bu yüzden gerilim bölücü yüksüzdür."),
        ("Doyma bölgesinde neden $V_{DS}$ akımı etkilemiyor?", "Savak ucunda kanal sıkışmıştır; akım kanalın kaynak ucundaki yük miktarı ($V_{GS}-V_{TH}$) tarafından belirlenir. (Gerçekte $\\lambda$ ile çok az eğim vardır.)"),
        ("Evirici neden $V_{DD}/2$'de değil de 2,2 V'ta anahtarlıyor?", "NMOS ≈800 kat güçlü. Eşitlenmiş eviricide PMOS'un genişliği büyütülür."),
        ("Neden evirici durgun hâlde akım çekmiyor?", "Daima seri yoldaki iki transistörden biri kapalıdır."),
        ("BS170 ile BS250 yer değiştirirse?", "Bacak sırası ters olduğundan fark etmeden S ve D'yi tersine bağlarsınız; gövde diyodu iletir, devre çalışmaz."),
        ("$V_{TH}$ yayılımı neden önemli?", "Şekil [[f:vthsp]]: $V_{GS}=3$ V'ta $V_{TH}=0{,}8$ V'luk bir parça 174 mA, 3 V'luk bir parça 0 mA verir."),
    ]
    for q, a in qa:
        d.p("**S:** " + q)
        d.p("**C:** " + a)
    return d
