import numpy as np
from common import *
from docbuilder import Doc
from docs1 import n2, sci, M, cursor_table
import exp3
import ltshots
import extras


def kohm(x):
    return n2(x / 1e3, 4)


def tbl_q(d, R, lang):
    q = R["q"]
    a_cs, a_no = R["av_mid"]
    c10, n10 = R["av_10k"]
    en = lang == "en"
    hdr = ["", "Circuit with $C_S$" if en else "$C_S$'li devre", "Circuit without $C_S$" if en else "$C_S$'siz devre"]
    rows = [
        ["$V_{GSQ}$ (V)", n2(q["vgs"], 4), n2(q["vgs"], 4)],
        ["$V_{DSQ}$ (V)", n2(q["vds"], 4), n2(q["vds"], 4)],
        ["$I_{DQ}$ (mA)", n2(q["id"] * 1e3, 4), n2(q["id"] * 1e3, 4)],
        ["$A_V=V_o/V_i$ (mid-band, $C_S$ ideal short)" if en else "$A_V=V_o/V_i$ (orta bant, $C_S$ ideal kısa devre)", n2(a_cs, 4), n2(a_no, 4)],
        ["$R_{in}$ (k$\\Omega$)", kohm(R["rin"]), kohm(R["rin"])],
        ["$R_{out}$ (k$\\Omega$)", kohm(R["rout"]), kohm(R["rout"])],
        ["$|A_V|$ at 10 kHz (phasor analysis)" if en else "10 kHz'te $|A_V|$ (fazör analizi)", n2(abs(c10), 4), n2(abs(n10), 4)],
    ]
    return hdr, rows


def mirror_rows(R, en=True):
    rows = []
    for (v, ih, oh, reg), (_, isp, osp) in zip(R["mirror_hand"], R["mirror_sp"]):
        if v == 1:
            rows.append([n2(v, 3), "0", "0", "\u2248 0", "\u2248 0", "cut-off" if en else "kesim"])
        else:
            rows.append([n2(v, 3), n2(ih * 1e3, 4), n2(oh * 1e3, 4), n2(isp * 1e3, 4), n2(osp * 1e3, 4), reg])
    return rows


def build_en(R):
    d = Doc("en")
    q = R["q"]
    a_cs, a_no = R["av_mid"]
    c10, n10 = R["av_10k"]
    d.title_block([
        ("TOBB University of Economics and Technology", 14, True),
        ("Department of Electrical and Electronics Engineering", 12, False),
        ("ELE 224L \u2013 Electronic Circuits Laboratory", 12, False),
        ("Experiment 3 \u2013 Preliminary Work: MOSFET Amplifiers", 13, True),
    ], [("Name Surname", ""), ("Student ID", ""), ("Date", "")])
    d.h(1, "Introduction")
    d.h(2, "Objective of the Experiment")
    d.p("The objective of this experiment is to learn the operating principle of the MOSFET as an amplifying element in the common-source amplifier and as a matched current source in the current mirror. The DC operating point (Q point), the small-signal gain, and the input and output resistances of a common-source amplifier are calculated for the cases with and without a source bypass capacitor, and the current mirror is analysed for a range of input voltages, including the voltage at which it stops working.")
    d.h(2, "Benefits of the Experiment")
    d.p("The experiment shows that an amplifier analysis consists of two separate steps (a DC bias analysis and a small-signal AC analysis), that a bypass capacitor changes the gain by a large factor, and that the capacitor values must be checked against the test frequency before a mid-band formula is used. It also shows how a current mirror copies a reference current and where this copying fails. These skills are required for the BJT amplifiers of the next experiments.")

    d.h(1, "Calculations and Simulations")
    d.h(2, "Common-Source Amplifier Circuit")
    d.p("The amplifier circuit is shown in [[f:cs]]. The values $V_{DD}=12$ V, $R_1=47$ k$\\Omega$, $R_2=33$ k$\\Omega$, $R_D=15$ k$\\Omega$, $R_S=10$ k$\\Omega$, $R_L=10$ k$\\Omega$, $C_{C1}=22$ nF, $C_{C2}=2.2$ nF and $C_S=22$ nF are used. The BS170 is modelled with the square-law equation $I_D=(K_N/2)(V_{GS}-V_{TH})^2$ with $K_N=72$ mA/V$^2$ and $V_{TH}=2.0$ V, and the channel-length modulation is neglected.")
    d.fig("cs", R["fig_cs_schem"], "Common-source amplifier circuit analysed in the experiment.", 13)
    d.p("**DC analysis.** All capacitors are open circuits for DC. The gate voltage is given by the divider, [[e:vg]]. The gate current is zero, so $V_{GS}=V_G-I_DR_S$. Substituting this into the square law and writing $V_{OV}=V_{GS}-V_{TH}$ gives the quadratic equation [[e:quad]].")
    d.eq(r"V_G=V_{DD}\frac{R_2}{R_1+R_2}=12\cdot\frac{33}{80}=%.2f\ \text{V}" % q["vg"], "vg")
    d.eq(r"\frac{K_N}{2}R_S\,V_{OV}^2+V_{OV}-\left(V_G-V_{TH}\right)=0\ \Rightarrow\ 360\,V_{OV}^2+V_{OV}-%.2f=0" % (q["vg"] - 2), "quad")
    d.p("The positive root is $V_{OV}=%s$ V, so $V_{GSQ}=2.0+%s=%s$ V, $I_{DQ}=(72/2)(%s)^2=%s$ mA, and $V_{DSQ}=V_{DD}-I_{DQ}(R_D+R_S)=12-%s\\times25=%s$ V. Since $V_{DSQ}>V_{OV}$, the transistor is in saturation, which verifies the assumption. The transconductance is $g_m=K_NV_{OV}=%s$ mS." % (
        n2(q["vov"], 4), n2(q["vov"], 4), n2(q["vgs"], 4), n2(q["vov"], 4), n2(q["id"] * 1e3, 4), n2(q["id"] * 1e3, 4), n2(q["vds"], 4), n2(q["gm"] * 1e3, 4)))
    d.p("**Small-signal analysis.** For mid-band frequencies, the coupling capacitors are short circuits and the supply is an AC ground. With $C_S$ present, the source is at AC ground and the gain is given by [[e:av1]]. Without $C_S$, the source resistor produces local feedback, and the gain is given by [[e:av2]]. In both cases, $R_{in}=R_1\\parallel R_2$ because the gate draws no current, and $R_{out}=R_D$ because the output resistance of the transistor is infinite in the model (the load $R_L$ is not included in $R_{out}$).")
    d.eq(r"A_V=-g_m\left(R_D\parallel R_L\right)=-%.3f\ \text{mS}\times6\ \text{k}\Omega=%.2f" % (q["gm"] * 1e3, a_cs), "av1")
    d.eq(r"A_V=-\frac{g_m\left(R_D\parallel R_L\right)}{1+g_mR_S}=\frac{%.2f}{1+%.3f\times10}=%.3f" % (a_cs, q["gm"] * 1e3, a_no), "av2")
    d.eq(r"R_{in}=R_1\parallel R_2=%.2f\ \text{k}\Omega,\qquad R_{out}=R_D=15\ \text{k}\Omega" % (R["rin"] / 1e3), "rinout")
    hdr, rows = tbl_q(d, R, "en")
    d.tab("q", hdr, rows, "Calculated Q point, gain and resistances of the common-source amplifier", widths=[7.4, 4, 4], size=9.5)
    d.p("The mid-band formulas assume that $C_S$ is a perfect short circuit. This assumption was checked for the test frequency of 10 kHz. At this frequency, the impedance of $C_S$ is $1/(2\\pi f C_S)=%.0f\\ \\Omega$, which is not small compared with $1/g_m=%.0f\\ \\Omega$; the parallel combination of $R_S$ and $C_S$ is %.0f $\\Omega$ in magnitude, and the gain is reduced by the factor $|1+g_mZ_S|$. A complete phasor analysis of the circuit (including $C_{C1}$, $C_{C2}$ and $C_S$) gives $|A_V|=%.2f$ with $C_S$ and %.3f without $C_S$ at 10 kHz, as listed in the last row of [[t:q]]. For $|A_V|$ at 10 kHz to reach 90%% of the mid-band value, $C_S$ would have to be about %.2f \u00b5F." % (
        1 / (2 * np.pi * 1e4 * 22e-9), 1 / q["gm"], abs(1 / (1 / 1e4 + 1j * 2 * np.pi * 1e4 * 22e-9)), abs(c10), abs(n10), R["cs_need"] * 1e6))
    d.p("**SPICE.** The circuit was built with the BS170 model. The Q point obtained from the DC analysis is compared with the calculation in [[t:qsp]]. A sinusoidal input of 100 mV amplitude and 10 kHz was applied, and the time-domain graphs are shown in [[f:tran1]] (with $C_S$) and [[f:tran2]] (without $C_S$); more than two periods are visible. The transient amplitude ratio was measured in steady state. The frequency response obtained with an AC analysis is shown in [[f:bode]].")
    op = R["op"][0]
    ta = R["tran_amp"]
    rows = [
        ["$V_{GSQ}$ (V)", n2(q["vgs"], 4), n2(op[0], 4), "%+.1f%%" % pct_err(q["vgs"], op[0])],
        ["$V_{DSQ}$ (V)", n2(q["vds"], 4), n2(op[1], 4), "%+.1f%%" % pct_err(q["vds"], op[1])],
        ["$I_{DQ}$ (mA)", n2(q["id"] * 1e3, 4), n2(op[2] * 1e3, 4), "%+.1f%%" % pct_err(q["id"], op[2])],
        ["$|A_V|$ at 10 kHz, with $C_S$", n2(abs(c10), 4), n2(ta[True][0] / ta[True][1], 4), "%+.1f%%" % pct_err(abs(c10), ta[True][0] / ta[True][1])],
        ["$|A_V|$ at 10 kHz, without $C_S$", n2(abs(n10), 4), n2(ta[False][0] / ta[False][1], 4), "%+.1f%%" % pct_err(abs(n10), ta[False][0] / ta[False][1])],
        ["Mid-band $|A_V|$, with $C_S$ (SPICE at 1 MHz)", n2(abs(a_cs), 4), n2(R["mid_sp"][0], 4), "%+.1f%%" % pct_err(abs(a_cs), R["mid_sp"][0])],
        ["Mid-band $|A_V|$, without $C_S$ (SPICE at 1 MHz)", n2(abs(a_no), 4), n2(R["mid_sp"][1], 4), "%+.1f%%" % pct_err(abs(a_no), R["mid_sp"][1])],
        ["$R_{in}$ at 10 kHz (k$\\Omega$)", kohm(R["rin"]), kohm(R["rin_sp"]), "%+.2f%%" % pct_err(R["rin"], R["rin_sp"])],
        ["$R_{out}$ (k$\\Omega$)", kohm(R["rout"]), kohm(R["rout_sp"]), "%+.2f%%" % pct_err(R["rout"], R["rout_sp"])],
    ]
    d.tab("qsp", ["Quantity", "Calculation", "SPICE", "Error"], rows, "Comparison of the calculation and SPICE for the common-source amplifier (Error = (SPICE $-$ calculation)/calculation)", widths=[7.2, 3, 3, 2.4], size=9)
    d.fig("tran1", R["fig_tran_1"], "Input and output voltages of the common-source amplifier with $C_S$ (100 mV, 10 kHz; ngspice).", 13.5)
    cursor_table(d, "e3_tran_1", "tran1")
    d.fig("tran2", R["fig_tran_0"], "Input and output voltages of the common-source amplifier without $C_S$ (100 mV, 10 kHz; ngspice).", 13.5)
    cursor_table(d, "e3_tran_0", "tran2")
    d.fig("bode", R["fig_bode"], "Frequency response of the amplifier: SPICE (solid) and the phasor calculation (dashed).", 13)
    cursor_table(d, "e3_bode", "bode")
    ltshots.add(d, "e3_tran_1", "lt_tran1")
    ltshots.add(d, "e3_tran_0", "lt_tran0")
    ltshots.add(d, "e3_ac_1", "lt_ac1")
    ltshots.add(d, "e3_ac_0", "lt_ac0")
    d.p("**Interpretation.** The DC values of SPICE differ from the calculation by less than 5%%, since the SPICE model has a larger transconductance parameter ($KP\\cdot W/L=123.3$ mA/V$^2$ against $K_N=72$ mA/V$^2$), a slightly higher threshold (2.1 V against 2.0 V), and series resistances $R_D$ and $R_S$ of 1.4 and 1.6 $\\Omega$. At 10 kHz, the measured gain with $C_S$ is %s, which is far below the mid-band value %s of the calculation, but it agrees with the phasor calculation (%s) to %.1f%%; the reason is that at this frequency the gain is determined by the impedance of $C_S$, $|A_V|\\approx R_L'/|Z_S|$, and not by $g_m$. The mid-band gain of SPICE (%s) is %.0f%% larger than the calculated mid-band gain since the SPICE transistor has a higher $g_m$ at the same current, and this difference is visible only above about 100 kHz in [[f:bode]]. Without $C_S$, the gain is almost independent of $g_m$ because $g_mR_S\\gg1$, $A_V\\approx-R_L'/R_S=-0.6$, and the SPICE result agrees with the calculation within %.1f%%." % (
        n2(ta[True][0] / ta[True][1], 3), n2(abs(a_cs), 3), n2(abs(c10), 3), abs(pct_err(abs(c10), ta[True][0] / ta[True][1])), n2(R["mid_sp"][0], 3), pct_err(abs(a_cs), R["mid_sp"][0]), abs(pct_err(abs(a_no), R["mid_sp"][1]))))

    d.h(2, "Current Mirror Circuit")
    d.p("The current mirror is shown in [[f:mir]]. The transistor M1 is diode connected (its gate and drain are tied), so it is always in saturation, and $V_{GS}$ is set by the reference current $I_{ref}$. Since M2 has the same $V_{GS}$ and is identical to M1, it carries the same current as long as it stays in saturation, i.e., as long as $V_{DS2}=V_{DD}-I_{out}R_2\\geq V_{OV}$. The reference current is found from the loop equation [[e:iref]], which is solved for $I_{ref}$ by iteration (or as a quadratic in $V_{OV}$).")
    d.fig("mir", R["fig_mirror_schem"], "Current mirror circuit analysed in the experiment.", 10)
    d.eq(r"V_i=R_1I_{ref}+V_{TH}+\sqrt{\frac{2I_{ref}}{K_N}}", "iref")
    d.p("For example, for $V_i=3$ V, $V_i-V_{TH}=1$ V gives the quadratic $24.48\\,V_{OV}^2+V_{OV}-1=0$ (with $V_{OV}$ in V and $R_1=0.68$ k$\\Omega$), and $V_{OV}=0.182$ V, $I_{ref}=36\\cdot0.182^2=1.20$ mA. Then $V_{DS2}=15-1.20\\times1=13.8$ V $>V_{OV}$, so M2 is in saturation and $I_{out}=I_{ref}=1.20$ mA. For $V_i=1$ V (below $V_{TH}$), M1 is off and both currents are zero. For $V_i=15$ V, $I_{ref}$ would be %s mA and M2 would require $V_{DS2}=15-18.1<0$, which is impossible; M2 therefore leaves saturation, enters the triode region, and the solution of the triode current equation together with $V_{DS2}=15-I_{out}R_2$ gives $I_{out}=%s$ mA. The hand-calculated and simulated values are given in [[t:mir]]." % (n2(R["mirror_hand"][-1][1] * 1e3, 4), n2(R["mirror_hand"][-1][2] * 1e3, 4)))
    d.tab("mir", ["$V_i$ (V)", "$I_{ref}$ calc. (mA)", "$I_{out}$ calc. (mA)", "$I_{ref}$ SPICE (mA)", "$I_{out}$ SPICE (mA)", "M2 region (calc.)"], mirror_rows(R),
          "Reference and output currents of the current mirror: calculation and SPICE", widths=[1.8, 3, 3, 3, 3, 2.6], size=9)
    d.fig("mirg", R["fig_mirror"], "$I_{ref}$\u2013$V_i$ and $I_{out}$\u2013$V_i$ graphs of the current mirror ($V_i$ on the x-axis) with the mirror ratio (ngspice).", 15.5)
    cursor_table(d, "e3_mirror", "mirg")
    ltshots.add(d, "e3_mirror", "lt_mir")
    d.p("The two currents are equal (within 0.1%%) up to $V_i=12$ V. The SPICE and calculated reference currents agree within %.1f%% for $V_i\\geq5$ V, whereas at 3 V the SPICE current is %s lower than the calculated one; this larger difference is caused by the different transconductance and threshold of the SPICE model when $V_{OV}$ is small. For $V_i=15$ V, $I_{out}$ stays at about %s mA while $I_{ref}$ continues to rise to %s mA, because M2 enters the triode region (the calculation predicts this for $V_i>%.1f$ V; in the 0.5 V steps of the SPICE sweep, the ratio $I_{out}/I_{ref}$ first falls below 0.99 at %.1f V). The mirror therefore works as long as the load drop $I_{out}R_2$ leaves at least $V_{OV}$ across M2, i.e., $V_{DD}-I_{out}R_2\\geq V_{OV}$. In saturation, the equality of the currents also relies on the neglect of channel-length modulation, which is zero in the BS170 model." % (
        max(abs(pct_err(R["mirror_hand"][k][1], R["mirror_sp"][k][1])) for k in range(2, 7)), "%.1f%%" % abs(pct_err(R["mirror_hand"][1][1], R["mirror_sp"][1][1])), n2(R["mirror_sp"][-1][2] * 1e3, 3), n2(R["mirror_sp"][-1][1] * 1e3, 3), R["vi_tri"], R["vi_tri_sp"]))

    d.h(1, "Conclusions")
    d.p("The calculated Q point of the common-source amplifier ($V_{GSQ}=%s$ V, $I_{DQ}=%s$ mA, $V_{DSQ}=%s$ V) agrees with SPICE within about 4%%, with the differences caused by the model parameters. The most important result is that the mid-band gain formulas cannot be applied at 10 kHz with the given capacitor values: the bypass capacitor of 22 nF is too small, and the measured gain with $C_S$ is %s instead of %s. A bypass capacitor of at least about %.2f \u00b5F would be required for this test frequency, or the test frequency should be raised above about 100 kHz. Without the bypass capacitor, the gain is small (%s) but stable, since it depends only on the resistor ratio. The analysis also gave $R_{in}=%s$ k$\\Omega$ (set by the bias divider) and $R_{out}=15$ k$\\Omega$ (set by $R_D$); the SPICE values agree within 0.1%%." % (
        n2(q["vgs"], 3), n2(q["id"] * 1e3, 3), n2(q["vds"], 3), n2(ta[True][0] / ta[True][1], 3), n2(abs(a_cs), 3), R["cs_need"] * 1e6, n2(a_no, 3), kohm(R["rin"])))
    d.p("In the current mirror, the output current follows the reference current until the output transistor loses saturation at about 12\u201313 V; the experiment taught the limit of the mirror (compliance voltage), the use of a diode-connected transistor as a bias generator, and the difference between an ideal copy and the real behaviour. The unexpected results above were explained by checking the capacitor impedances and the model parameters, which is a skill required in the remaining experiments.")
    d.h(1, "References")
    d.bullets([
        "Sedra, A. S., & Smith, K. C. (2014). Microelectronic circuits (7th ed.). New York: Oxford University Press.",
        "ON Semiconductor. (2017). BS170 small signal MOSFET 500 mA, 60 volts [Data sheet]. Retrieved October 11, 2026, from https://www.onsemi.com/download/data-sheet/pdf/bs170-d.pdf",
        "ngspice. (n.d.). ngspice user manual. Retrieved October 11, 2026, from https://ngspice.sourceforge.io/docs.html",
    ], numbered=True)
    d.h(1, "Appendices")
    d.h(2, "Appendix A: SPICE Netlists")
    d.code(clean_cir(os.path.join(SPICE, "e3_tran_1.cir")), "Netlist A.1  Common-source amplifier with $C_S$ (transient)")
    d.code(clean_cir(os.path.join(SPICE, "e3_mirror_dc.cir")), "Netlist A.2  Current mirror (DC sweep)")
    return d


def build_tr(R):
    d = Doc("tr")
    q = R["q"]
    a_cs, a_no = R["av_mid"]
    c10, n10 = R["av_10k"]
    ta = R["tran_amp"]
    d.title_block([
        ("Deney 3 \u2013 Ön Çalışma Öğretici Rehberi", 15, True),
        ("MOSFET Yükselteçleri: Ortak Kaynak ve Akım Aynası", 12, False),
        ("Bu belge SADECE ÖĞRENMEK içindir; teslim edilecek metin İngilizce rapordur.", 11, False),
    ], [("Ad Soyad", ""), ("Numara", ""), ("Tarih", "")])
    d.h(1, "Büyük Resim")
    d.p("Yükselteç, küçük bir giriş değişimini büyük bir çıkış değişimine çeviren devredir. MOSFET'le yükselteç kurmak için iki şey gerekir: (1) transistörü **doyma bölgesinde, doğru noktada** tutacak bir **DC kutuplama** (Q noktası); (2) bu noktanın etrafında küçük değişimleri büyüten bir **AC küçük sinyal** davranışı. Bu deneyin ana fikri **iki analizin ayrı yapılmasıdır**: DC'de kondansatörler açık devre, AC'de kondansatörler (yeterince büyükse) kısa devre ve DC kaynak (VDD) toprak gibidir.")
    d.box("Üç sihirli adım", [
        "**1. DC analiz:** kondansatörleri aç, $I_D$, $V_{GS}$, $V_{DS}$'yi bul (doymada olduğunu doğrula).",
        "**2. Küçük sinyal parametreleri:** $g_m=K_NV_{OV}=\\dfrac{2I_D}{V_{OV}}$ hesapla.",
        "**3. AC analiz:** kondansatörleri kısa, VDD'yi toprak yap; kazanç ve dirençleri yaz. Sonunda: *bu kısa devre varsayımı test frekansında gerçekten geçerli mi?* diye mutlaka kontrol et (bu deneyde geçerli DEĞİL!).",
    ])
    d.h(1, "Soru 1.1: Ortak Kaynak Yükselteç")
    d.fig("cs", R["fig_cs_schem"], "Ortak kaynak yükselteç devresi.", 13)
    d.h(2, "Adım 1 – DC analiz")
    d.p("Kapıdan DC akım akmadığı için $R_1$–$R_2$ bölücüsü yüksüzdür: ")
    d.eq(r"V_G=V_{DD}\frac{R_2}{R_1+R_2}=12\cdot\frac{33}{80}=%.2f\ \text{V}" % q["vg"], "vg")
    d.p("Kaynakta $R_S$ olduğu için $V_{GS}=V_G-I_DR_S$ (negatif geri besleme: akım artarsa $V_{GS}$ düşer, akım kendini sınırlar — kutuplamanın kararlı olmasının sebebi). Karesel modelle birleştirirsek:")
    d.eq(r"I_D=\frac{K_N}{2}V_{OV}^2,\quad V_{GS}=V_{TH}+V_{OV}=V_G-I_DR_S\ \Rightarrow\ \frac{K_N}{2}R_SV_{OV}^2+V_{OV}-(V_G-V_{TH})=0", "quad")
    d.p("Sayılarla: $\\tfrac{K_N}{2}R_S=0{,}036\\ \\text{A/V}^2\\times10^4\\ \\Omega=360$ ve $V_G-V_{TH}=%.2f$ V ⇒ $360V_{OV}^2+V_{OV}-%.2f=0$. İkinci derece denklemin pozitif kökü (negatif kök fizikî değil): $V_{OV}=\\dfrac{-1+\\sqrt{1+4\\cdot360\\cdot%.2f}}{720}=%s$ V." % (q["vg"] - 2, q["vg"] - 2, q["vg"] - 2, n2(q["vov"], 4)))
    d.bullets([
        "$V_{GSQ}=2{,}0+%s=%s$ V." % (n2(q["vov"], 4), n2(q["vgs"], 4)),
        "$I_{DQ}=36\\,\\text{mA/V}^2\\times(%s)^2=%s$ mA." % (n2(q["vov"], 4), n2(q["id"] * 1e3, 4)),
        "$V_{DSQ}=V_{DD}-I_{DQ}(R_D+R_S)=12-%s\\times25\\,\\text{k}\\Omega=%s$ V." % (n2(q["id"] * 1e3, 4), n2(q["vds"], 4)),
        "**Doğrulama:** $V_{DSQ}=%s\\ \\text{V}>V_{OV}=%s$ V ⇒ doyma varsayımı doğru." % (n2(q["vds"], 3), n2(q["vov"], 4)),
        "$g_m=K_NV_{OV}=72\\ \\text{mA/V}^2\\times%s=%s$ mS. (Kontrol: $2I_D/V_{OV}=%s$ mS ✓.)" % (n2(q["vov"], 4), n2(q["gm"] * 1e3, 4), n2(2 * q["id"] / q["vov"] * 1e3, 4)),
    ])
    d.box("Dikkat: Q noktası neden eşik değerine çok yakın?", [
        "$V_G=4{,}95$ V, $V_{GS}$ ise yalnızca 2,09 V: $R_S$ üzerinde ≈2,86 V düşüyor ve $V_{OV}=0{,}09$ V gibi çok küçük bir değer kalıyor. BS170'in eşiği veri sayfasında 0,8–3,0 V arasında yayılır; eşik 0,8 V olan parçada $V_{DS}$ yaklaşık 1,9 V'a düşer (doymaya yaklaşır), 3,0 V olan parçada ise akım 0,19 mA'e iner ve kazanç çok düşer (ayrıntı: sondaki ek sorular). Gerçek laboratuvarda bu yüzden gerilimler ölçülüp doğrulanır.",
    ], fill="FFF4E0")
    d.h(2, "Adım 2 – AC analiz (orta bant)")
    d.p("Kondansatörler kısa, $V_{DD}$ toprak. Küçük sinyal eşdeğerinde MOSFET: kapıdan kaynağa açık devre, savaktan kaynağa $g_mv_{gs}$ akım kaynağı ($r_o\\to\\infty$).")
    d.p("**$C_S$ varken:** kaynak AC'de topraklıdır, $v_{gs}=v_i$. Savak akımı $g_mv_i$ ve çıkış yükü $R_D\\parallel R_L=6$ kΩ üzerinden akar, işaret ters çevrilir:")
    d.eq(r"A_V=-g_m\left(R_D\parallel R_L\right)=-%.3f\ \text{mS}\times6\ \text{k}\Omega=%.2f" % (q["gm"] * 1e3, a_cs), "av1")
    d.p("**$C_S$ yokken:** kaynakta $R_S$ kalır. $v_i=v_{gs}+i_dR_S$ ve $i_d=g_mv_{gs}$ ⇒ $v_{gs}=\\dfrac{v_i}{1+g_mR_S}$. Çıkış $v_o=-i_d(R_D\\parallel R_L)$:")
    d.eq(r"A_V=-\frac{g_m\left(R_D\parallel R_L\right)}{1+g_mR_S}=\frac{%.2f}{1+%.3f\times10}=%.3f" % (a_cs, q["gm"] * 1e3, a_no), "av2")
    d.p("$g_mR_S=64\\gg1$ olduğundan kazanç $\\approx-\\dfrac{R_D\\parallel R_L}{R_S}=-0{,}6$: neredeyse yalnız dirençlere bağlıdır, $g_m$ ve dolayısıyla transistöre bağlı değildir. Bu **geri beslemenin** getirdiği kararlılıktır; bedeli kazanç kaybıdır (≈65 kat).")
    d.p("**Rin ve Rout:** Kapıya DC/AC akım girmediği için giriş direnci yalnızca bölücüdür: $R_{in}=R_1\\parallel R_2=%s$ kΩ (iki durumda da aynı). Çıkış direnci: giriş kaynağı kapatılınca ($v_i=0$ ⇒ $i_d=0$) savaktan bakınca yalnızca $R_D$ görünür: $R_{out}=R_D=15$ kΩ ($R_L$ dahil edilmez; $r_o$ ihmal edilir)." % kohm(R["rin"]))
    hdr, rows = tbl_q(d, R, "tr")
    d.tab("q", hdr, rows, "Föy Tablo 1'in hesaplanmış hâli (son satır ek)", widths=[7.4, 4, 4], size=9.5)
    d.h(2, "Adım 3 – \"Kısa devre\" varsayımı gerçekten geçerli mi? (10 kHz tuzağı)")
    d.p("Bir kondansatörün empedansı $1/(\\omega C)$'dir. Bir kondansatörü \"kısa devre\" saymak için empedansı, **karşılaştığı dirençlerden çok küçük** olmalıdır. Kontrol edelim ($f=10$ kHz):")
    d.bullets([
        "$C_{C1}=22$ nF: $1/(\\omega C)=%.0f\\ \\Omega\\ll R_{in}=19{,}4$ kΩ ✓ (kısa sayılır)." % (1 / (2 * np.pi * 1e4 * 22e-9)),
        "$C_{C2}=2{,}2$ nF: $1/(\\omega C)=%.1f$ kΩ, karşılaştığı $R_D+R_L=25$ kΩ ⇒ orta derecede (kazancı ~%%4 düşürür) ✓ yaklaşık." % (1 / (2 * np.pi * 1e4 * 2.2e-9) / 1e3),
        "**$C_S=22$ nF:** $1/(\\omega C_S)=%.0f\\ \\Omega$ ama karşılaştığı $1/g_m=%.0f\\ \\Omega$. 723 Ω, 156 Ω'dan **büyük**: kısa devre sayılamaz! ✗" % (1 / (2 * np.pi * 1e4 * 22e-9), 1 / q["gm"]),
    ])
    d.p("Doğru hesap için kaynak empedansı $Z_S=R_S\\parallel\\dfrac{1}{j\\omega C_S}$ alınır ve kazanç $A_V\\approx-\\dfrac{R_D\\parallel R_L}{Z_S+1/g_m}$ olur. $f=10$ kHz'de $|Z_S|\\approx%.0f\\ \\Omega$, bu yüzden $|A_V|\\approx6000/(%.0f+156)\\approx8$. Eksiksiz fazör çözümü (üç kondansatör birden) $|A_V|=%.2f$ verir: **orta bant değerinin (%.1f) beşte biri.**" % (abs(1 / (1 / 1e4 + 1j * 2 * np.pi * 1e4 * 22e-9)), abs(1 / (1 / 1e4 + 1j * 2 * np.pi * 1e4 * 22e-9)), abs(c10), abs(a_cs)))
    d.box("Bu ne demek? (aklınızda soru işareti kalmasın)", [
        "• Föydeki Tablo 1 **orta bant** kazancı ister: $-38{,}5$ (CS'li) ve $-0{,}59$ (CS'siz). Bunlar hesabın doğru cevabıdır; tabloya bunları yazın.",
        "• Ama simülasyonda 10 kHz ile ölçtüğünüz kazanç **38 değil ≈7,8 çıkacaktır.** Bu simülasyon hatası değil, 22 nF'ın 10 kHz için çok küçük olmasıdır. Raporun yorum kısmında bunu kendi hesabınızla (yukarıdaki fazör analizi) açıklarsanız tam puan alırsınız.",
        "• 10 kHz'de orta-bant kazancın %%90'ına ulaşmak için $C_S\\approx%.2f\\ \\mu$F gerekir (22 nF'ın ≈%.0f katı)." % (R["cs_need"] * 1e6, R["cs_need"] / 22e-9),
    ])
    d.h(2, "SPICE sonuçları")
    d.fig("tran1", R["fig_tran_1"], "$C_S$'li devre: giriş (100 mV, 10 kHz) ve çıkış.", 13.5)
    d.fig("tran2", R["fig_tran_0"], "$C_S$'siz devre.", 13.5)
    d.fig("bode", R["fig_bode"], "Frekans cevabı: SPICE (düz) ve fazör hesabı (kesikli).", 13)
    ltshots.add(d, "e3_tran_1", "lt_tran1", tr=True)
    ltshots.add(d, "e3_tran_0", "lt_tran0", tr=True)
    ltshots.add(d, "e3_ac_1", "lt_ac1", tr=True)
    ltshots.add(d, "e3_ac_0", "lt_ac0", tr=True)
    op = R["op"][0]
    rows = [
        ["$V_{GSQ}$ (V)", n2(q["vgs"], 4), n2(op[0], 4), "%+.1f%%" % pct_err(q["vgs"], op[0])],
        ["$V_{DSQ}$ (V)", n2(q["vds"], 4), n2(op[1], 4), "%+.1f%%" % pct_err(q["vds"], op[1])],
        ["$I_{DQ}$ (mA)", n2(q["id"] * 1e3, 4), n2(op[2] * 1e3, 4), "%+.1f%%" % pct_err(q["id"], op[2])],
        ["10 kHz $|A_V|$, $C_S$'li", n2(abs(c10), 4), n2(ta[True][0] / ta[True][1], 4), "%+.1f%%" % pct_err(abs(c10), ta[True][0] / ta[True][1])],
        ["10 kHz $|A_V|$, $C_S$'siz", n2(abs(n10), 4), n2(ta[False][0] / ta[False][1], 4), "%+.1f%%" % pct_err(abs(n10), ta[False][0] / ta[False][1])],
        ["Orta bant $|A_V|$, $C_S$'li (SPICE 1 MHz)", n2(abs(a_cs), 4), n2(R["mid_sp"][0], 4), "%+.1f%%" % pct_err(abs(a_cs), R["mid_sp"][0])],
        ["Orta bant $|A_V|$, $C_S$'siz (SPICE 1 MHz)", n2(abs(a_no), 4), n2(R["mid_sp"][1], 4), "%+.1f%%" % pct_err(abs(a_no), R["mid_sp"][1])],
        ["$R_{in}$ (kΩ)", kohm(R["rin"]), kohm(R["rin_sp"]), "%+.2f%%" % pct_err(R["rin"], R["rin_sp"])],
        ["$R_{out}$ (kΩ)", kohm(R["rout"]), kohm(R["rout_sp"]), "%+.2f%%" % pct_err(R["rout"], R["rout_sp"])],
    ]
    d.tab("qsp", ["Büyüklük", "Hesap", "SPICE", "Hata"], rows, "El hesabı ile SPICE", widths=[7.2, 3, 3, 2.4], size=9)
    d.bullets([
        "**Grafikte neyi okuyacaksınız?** Üstteki panel giriş (±100 mV), alttaki çıkış. $C_S$'li devrede çıkış tepesi ≈0,77 V (kazanç ≈7,7); $C_S$'siz devrede ≈57 mV (kazanç ≈0,57). Çıkış girişle **ters fazlıdır** (180°): giriş tepedeyken çıkış çukurdadır.",
        "**Bode grafiği:** $C_S$'li eğri 723 Hz'deki sıfırdan başlayarak yükselir ve 47 kHz civarında düzleşir (düz bölge SPICE'ta ≈49, el hesabında 38,5). $C_S$'siz eğri 1 kHz üstünde düzdür. 10 kHz düşey çizgisi, $C_S$'li eğrinin henüz **yükselmekte** olduğu yerde. Düşük frekanstaki düşüş $C_{C1}$, $C_{C2}$ ve $C_S$ kondansatörlerinin yüksek geçiren etkisidir.",
        "**SPICE'ın orta bant kazancı neden %27 fazla?** SPICE modelinin transkondüktans parametresi daha büyük ($K/2$=61,65 mA/V² — hesaptaki 36'ya karşı) ⇒ aynı akımda daha küçük $V_{OV}$ ($0{,}068$ V — hesapta 0,089 V) ⇒ $g_m=2I_D/V_{OV}$ daha büyük (≈8,2 mS — hesapta 6,4 mS). 10 kHz'de ise kazanç $g_m$'e değil $C_S$ empedansına bağlı olduğundan hesapla SPICE yaklaşık %1 farkla uyuşur. $C_S$'siz durumda $g_mR_S\\gg1$ olduğundan yine $g_m$'den bağımsızdır.",
    ])
    d.h(1, "Soru 2: Akım Aynası")
    d.fig("mir", R["fig_mirror_schem"], "Akım aynası devresi.", 10)
    d.h(2, "Mantık")
    d.bullets([
        "M1'in kapısı ile savağı birleşik (**diyot bağlı**). Bu durumda $V_{DS1}=V_{GS1}>V_{OV}$ olduğundan M1 **daima doymadadır.**",
        "M1'e $I_{ref}$ akıtılırsa, M1 bu akımı taşıyacak $V_{GS}$'yi kendi kendine kurar: $V_{GS}=V_{TH}+\\sqrt{2I_{ref}/K_N}$.",
        "M2'nin kapısı M1'inkiyle bağlı ⇒ aynı $V_{GS}$. M2 doymadaysa ve M1'in aynısıysa ⇒ $I_{out}=I_{ref}$ (kanal boyu modülasyonu ihmal edilirse). Bu, akımın **kopyalanması**dır.",
        "Sınır: M2'nin doymada kalması için $V_{DS2}=V_{DD}-I_{out}R_2\\geq V_{OV}$ olmalı. $I_{out}$ çok büyürse $R_2$ üzerinde fazla gerilim düşer, M2'ye az gerilim kalır, triyot bölgesine girer ve akım artık kopya olmaz.",
    ])
    d.h(2, "Hesap")
    d.p("Döngü denklemi: $V_i=R_1I_{ref}+V_{GS}$ ve $V_{GS}=V_{TH}+V_{OV}$, $I_{ref}=\\tfrac{K_N}{2}V_{OV}^2$:")
    d.eq(r"V_i-V_{TH}=R_1\frac{K_N}{2}V_{OV}^2+V_{OV}\ \Rightarrow\ 24.48\,V_{OV}^2+V_{OV}-(V_i-2)=0\quad(R_1=0.68\ \text{k}\Omega,\ V_{OV}\ \text{in V})", "iref")
    d.p("Örnek $V_i=3$ V: $24{,}48V_{OV}^2+V_{OV}-1=0$ ⇒ $V_{OV}=0{,}1824$ V ⇒ $I_{ref}=36\\times0{,}1824^2=1{,}20$ mA. Kontrol: $V_{GS}=2{,}1824$ V ve $V_i-R_1I_{ref}=3-0{,}68\\times1{,}20=2{,}184$ V ✓. $V_{DS2}=15-1{,}20=13{,}8$ V $>V_{OV}$ ⇒ M2 doymada ⇒ $I_{out}=1{,}20$ mA.")
    d.p("**Tabloyu doldurma stratejisi (her $V_i$ için):** (1) $V_i\\leq V_{TH}$ ise M1 kapalı: iki akım da 0 ($V_i=1$ V). (2) Değilse yukarıdaki ikinci derece denklemden $V_{OV}$ ve $I_{ref}$ bul. (3) M2'yi doymada varsay: $I_{out}=I_{ref}$; $V_{DS2}=15-I_{out}\\cdot1\\,\\text{k}\\Omega$ hesapla. (4) $V_{DS2}\\geq V_{OV}$ değilse (ör. $V_i=15$ V: $V_{DS2}=15-18{,}1<0$ imkânsız!) M2 triyottadır: $I_{out}=K_N\\left[V_{OV}V_{DS2}-\\tfrac{1}{2}V_{DS2}^2\\right]$ ve $V_{DS2}=15-1\\,\\text{k}\\Omega\\cdot I_{out}$ birlikte çözülür ⇒ $I_{out}=%s$ mA." % n2(R["mirror_hand"][-1][2] * 1e3, 4))
    d.tab("mir", ["$V_i$ (V)", "$I_{ref}$ el (mA)", "$I_{out}$ el (mA)", "$I_{ref}$ SPICE (mA)", "$I_{out}$ SPICE (mA)", "M2 bölgesi (el)"], mirror_rows(R, False), "Akım aynası: el hesabı ve SPICE", widths=[1.8, 3, 3, 3, 3, 2.6], size=9)
    d.fig("mirg", R["fig_mirror"], "$I_{ref}$–$V_i$ ve $I_{out}$–$V_i$ (soldaki), ayna oranı (sağdaki).", 15.5)
    ltshots.add(d, "e3_mirror", "lt_mir", tr=True)
    d.p("**Okuma:** İki eğri, $V_i\\approx12$ V'a kadar üst üste (kopyalama çalışıyor); sonra $I_{out}$ ~14,6 mA'de doyar (M2 triyota girer: $V_{DD}/R_2=15$ mA'in altında kalan, direnç tarafından sınırlanan akım), $I_{ref}$ ise artmaya devam eder (18,1 mA). Sağdaki grafikte oran 1'den düşer. El hesabına göre triyota geçiş $V_i=%.1f$ V civarındadır; SPICE'ta 0,5 V adımla taranan veride oran ilk kez %%1'den fazla sapma 13,0 V'ta görülür (adım 0,5 V olduğundan çözünürlük sınırlı)." % R["vi_tri"])
    d.h(1, "Programda Nasıl Yapılır?")
    d.bullets([
        "**Q noktası:** `.op` analizi; LTspice'ta sonuç penceresinde düğüm gerilimleri ve eleman akımları listelenir. $I_D$ için `Id(M1)` ya da $R_D$ üzerinden hesaplayın.",
        "**Geçici analiz:** Kaynak `SINE(0 0.1 10k)`; `.tran 8m` kullanın ama grafiği **kararlı hâle ulaştıktan sonraki** kısımda (ör. 7,5–8 ms) alın; ilk milisaniyelerde kondansatörler yüklenir. Birden fazla periyodun görünmesi istenir (burada 5 periyot var).",
        "**Frekans cevabı (ek):** `.ac dec 50 10 100Meg` ve kaynağa `AC 1` verin; çıkış izi dB cinsinden okunur (LTspice'ta dB/faz gösterir).",
        "**Akım aynası:** `.dc Vi 0 15 0.5`; $I_{ref}$ için `I(R1)`, $I_{out}$ için `I(R2)` izleri eklenir; x ekseni $V_i$.",
        "(Menüler ve ifadeler sürüme göre değişebilir; netlistler `spice/` klasöründedir.)",
    ])
    d.h(1, "Sık Sorulabilecek Sorular")
    qa = [
        ("Bypass kondansatörü ne işe yarar?", "$R_S$'i AC'de kısa devre eder. Böylece DC'de kutuplama kararlılığı için gerekli $R_S$ AC kazancı düşürmez."),
        ("Neden kazanç eksi işaretli?", "Kapı gerilimi artınca akım artar, $R_D$ üstündeki düşüm artar, savak gerilimi azalır: çıkış girişin tersidir (180° faz farkı)."),
        ("Rout'ta neden $R_L$ yok?", "Çıkış direnci yükten bağımsız yükselteç özelliğidir; yük bağlanınca oluşan bölme etkisi kazanca zaten $R_D\\parallel R_L$ ile girer."),
        ("Neden hesap (38,5) ile simülasyon (7,8) farklı?", "Hesap orta bant içindir (CS ideal kısa). 10 kHz'de 22 nF yeterli değildir; fazör analizi simülasyonu açıklar."),
        ("Akım aynasında $I_{out}$ neden $I_{ref}$'e eşit?", "İkisi aynı $V_{GS}$'e sahip, aynı tip transistör ve ikisi de doymada."),
        ("Kanal boyu modülasyonu olsaydı?", "$I_{out}=I_{ref}(1+\\lambda V_{DS2})/(1+\\lambda V_{GS})$ olurdu; $V_{DS2}$ büyüdükçe $I_{out}$ biraz artardı. BS170 modeli $\\lambda=0$ aldığından fark yoktur."),
    ]
    for qq, aa in qa:
        d.p("**S:** " + qq)
        d.p("**C:** " + aa)
    extras.tr_extra(3, d, R)
    return d
