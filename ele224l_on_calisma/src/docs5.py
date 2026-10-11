import numpy as np
from common import *
from docbuilder import Doc
from docs1 import n2, sci, M, cursor_table
import exp5
import ltshots

ERRS_EN = [
    ["E1", "The node where $R_1$ and $R_C$ meet (columns 14\u201315) is not connected to the + rail.", "No supply voltage reaches the circuit; $V_{CC}$ must be wired to this node (red wire from the + rail to column 15)."],
    ["E2", "The node where $R_2$ and $R_E$ meet (columns 23\u201324) is not connected to the \u2212 rail.", "The circuit has no ground reference; a wire from this node to the \u2212 (GND) rail is required."],
    ["E3", "The second leg of $R_L$ (column 17, upper block) is not connected to anything.", "The load is not grounded, so $C_{C2}$ and $R_L$ do not form a path to ground; $R_L$ must be wired to the GND rail."],
    ["E4", "The + (supply) rail is wired to the free leg of $C_{C1}$ (column 28).", "The input coupling capacitor would be tied to the supply instead of the signal source; this wire must be removed and the function-generator output connected to $C_{C1}$ ($v_i$)."],
    ["E5", "The emitter bypass capacitor $C_E$ is missing.", "$C_E$ (22 nF) must be connected in parallel with $R_E$ (between the emitter column and the ground node)."],
]
ERRS_TR = [
    ["E1", "$R_1$ ile $R_C$'nin birleştiği düğüm (14–15. sütunlar) + rayına bağlı değil.", "Devreye besleme gelmiyor; bu düğüm + rayına bir telle (kırmızı) bağlanmalı."],
    ["E2", "$R_2$ ile $R_E$'nin birleştiği düğüm (23–24. sütunlar) − rayına bağlı değil.", "Devrenin toprak referansı yok; bu düğümden − (GND) rayına tel çekilmeli."],
    ["E3", "$R_L$'nin ikinci bacağı (17. sütun, üst blok) hiçbir yere bağlı değil.", "Yük topraklanmamış; $R_L$ GND rayına bağlanmalı."],
    ["E4", "+ (besleme) rayı $C_{C1}$'in serbest bacağına (28. sütun) bağlanmış.", "Giriş kuplaj kondansatörü sinyal kaynağına değil beslemeye bağlı; bu tel kaldırılıp fonksiyon üreteci ($v_i$) buraya bağlanmalı."],
    ["E5", "Emetör köprüleme kondansatörü $C_E$ eksik.", "$C_E$ (22 nF), $R_E$'ye paralel (emetör sütunu ile toprak düğümü arasına) bağlanmalı."],
]


def els_table(d, en=True):
    rows = [
        ["Q1", "BC238A (NPN)", "Amplifying element" if en else "Yükselteç elemanı"],
        ["R1", "120 k$\\Omega$", "Upper bias resistor (+$V_{CC}$ to base)" if en else "Üst kutuplama direnci (+$V_{CC}$ ile baz arası)"],
        ["R2", "39 k$\\Omega$", "Lower bias resistor (base to GND)" if en else "Alt kutuplama direnci (baz ile GND arası)"],
        ["RC", "5.6 k$\\Omega$", "Collector resistor" if en else "Kolektör direnci"],
        ["RE", "1.8 k$\\Omega$", "Emitter resistor (DC stabilisation)" if en else "Emetör direnci (DC kararlılık)"],
        ["RL", "15 k$\\Omega$", "Load resistor" if en else "Yük direnci"],
        ["CC1", "22 nF", "Input coupling capacitor" if en else "Giriş kuplaj kondansatörü"],
        ["CC2", "2.2 nF", "Output coupling capacitor" if en else "Çıkış kuplaj kondansatörü"],
        ["CE", "22 nF (missing)" if en else "22 nF (eksik)", "Emitter bypass capacitor" if en else "Emetör köprüleme kondansatörü"],
    ]
    d.tab("els", ["Name", "Value", "Function"] if en else ["Ad", "Değer", "Görevi"], rows,
          "Names and values of the circuit elements of the common-emitter amplifier" if en else "Ortak emetörlü yükselteç devresinin elemanları", widths=[2.0, 3.6, 9.4], size=9)


def pc(a, b):
    return "%+.1f%%" % pct_err(a, b)


def build_en(R):
    d = Doc("en")
    ce, cc = R["ce"], R["cc"]
    dce, dcc = ce["d"], cc["d"]
    d.title_block([
        ("TOBB University of Economics and Technology", 14, True),
        ("Department of Electrical and Electronics Engineering", 12, False),
        ("ELE 224L \u2013 Electronic Circuits Laboratory", 12, False),
        ("Experiment 5 \u2013 Preliminary Work: BJT Amplifiers", 13, True),
    ], [("Name Surname", ""), ("Student ID", ""), ("Date", "")])
    d.h(1, "Introduction")
    d.h(2, "Objective of the Experiment")
    d.p("The objective of this experiment is to learn the operating principles of the common-emitter and the common-collector amplifiers, which are two of the three basic BJT amplifier configurations. For both circuits, the DC operating point, the small-signal voltage gain, the input and output resistances and the maximum output voltage swing are calculated and compared with SPICE simulations. The wiring of the circuits on a breadboard is also studied, including the detection of the errors in a given drawing.")
    d.h(2, "Benefits of the Experiment")
    d.p("The experiment shows how a BJT amplifier is analysed in two steps (DC bias, then AC small signal), how the emitter bypass capacitor changes the gain by a factor of about 80, why the emitter follower has a gain close to but never above one, and how the exponential characteristic of the BJT limits the undistorted output amplitude. It also trains the checking of the capacitor impedances at the test frequency, the use of a THD criterion for distortion, and the reading and correcting of a breadboard drawing. These skills are required in all analog design work.")

    d.h(1, "Calculations and Simulations")
    d.h(2, "BJT Amplifier Circuit Diagram and Breadboard")
    d.p("The parameters of the BC238A were taken from the datasheet (Fairchild BC237/238/239): $\\beta=170$ (the average of the class A range of 120\u2013220) and $V_{BE(on)}=0.62$ V (typical value at $I_C=2$ mA, $V_{CE}=5$ V). The Early voltage is neglected. These values are used in all calculations of this section.")
    d.tab("par", ["Parameter", "Value"], [["$\\beta$ (average)", "170"], ["$V_{BE(on)}$ (typical)", "0.62 V"]], "BJT parameters used in the calculations", widths=[5, 4], size=10)
    d.p("The connections of the given breadboard drawing ([[f:found]]) were read hole by hole, and the electrical nodes were extracted automatically and compared with the circuit diagram of the common-emitter amplifier ([[f:ces]]). The comparison showed the four wiring errors and one missing element that are listed in [[t:errs]] and marked in [[f:found]]. The values of the resistors read from the colour codes (5.6 k$\\Omega$, 120 k$\\Omega$, 1.8 k$\\Omega$, 39 k$\\Omega$, 15 k$\\Omega$) and the connections of the transistor ($C$ on column 18, $B$ on 19, $E$ on 20) are correct.")
    d.fig("found", R["fig_bb_found"], "The given breadboard drawing of the common-emitter amplifier; the errors are marked with red dashed circles.", 15.5)
    d.tab("errs", ["No.", "Error", "Correction"], [[e[0], e[1], e[2]] for e in ERRS_EN], "Errors found in the given breadboard drawing and their corrections", widths=[1.2, 6.6, 7.4], size=9)
    d.p("The corrected drawing is shown in [[f:bbce]]. The names and values of the circuit elements are given in [[t:els]]; the missing element is the bypass capacitor $C_E$ (drawn in red). The correctness of the corrected drawing was checked by the same automatic node extraction: the node lists of the drawing and of the circuit diagram are identical.")
    d.fig("ces", R["fig_ce_schem"], "Common-emitter amplifier circuit diagram.", 12)
    d.fig("bbce", R["fig_bb_ce"], "Corrected breadboard drawing of the common-emitter amplifier (with $C_E$ added).", 15.5)
    els_table(d, True)
    d.p("The common-collector amplifier of the experiment sheet ([[f:ccs]]) was drawn on the breadboard as shown in [[f:bbcc]]. The collector is wired directly to the + rail (there is no collector resistor), $R_1$ and $R_2$ form the base divider, the output is taken from the emitter through $C_{C2}$ and loaded by $R_L$, and the input is applied to the base through $C_{C1}$. The connections were verified automatically against the circuit diagram.")
    d.fig("ccs", R["fig_cc_schem"], "Common-collector amplifier circuit diagram.", 12)
    d.fig("bbcc", R["fig_bb_cc"], "Common-collector amplifier on the breadboard.", 15.5)

    # ------------------------------------------------ CE
    d.h(2, "Common-Emitter Amplifier Analysis")
    d.p("**DC analysis.** The capacitors are open circuits. The base divider is replaced by its Th\u00e9venin equivalent, $V_{TH}=V_{CC}R_2/(R_1+R_2)=%s$ V and $R_{TH}=R_1\\parallel R_2=%s$ k$\\Omega$, and the base loop gives [[e:ib]]." % (n2(dce["vth"], 4), n2(dce["rth"] / 1e3, 4)))
    d.eq(r"I_B=\frac{V_{TH}-V_{BE(on)}}{R_{TH}+(\beta+1)R_E}=\frac{%.4f-0.62}{%.3f\ \text{k}\Omega+171\cdot1.8\ \text{k}\Omega}=%.3f\ \mu\text{A}" % (dce["vth"], dce["rth"] / 1e3, dce["ib"] * 1e6), "ib")
    d.p("Then $I_C=\\beta I_B=%s$ mA, $I_E=(\\beta+1)I_B=%s$ mA, and $V_{CE}=V_{CC}-I_CR_C-I_ER_E=12-%s\\times5.6-%s\\times1.8=%s$ V. Since $V_{CE}>0.2$ V, the transistor is in the active region. The small-signal parameters are $g_m=I_C/V_T=%s$ mS, $r_\\pi=\\beta/g_m=%s$ k$\\Omega$ and $r_e=V_T/I_E=%s\\ \\Omega$ (with $V_T=26$ mV)." % (
        n2(dce["ic"] * 1e3, 4), n2(dce["ie"] * 1e3, 4), n2(dce["ic"] * 1e3, 4), n2(dce["ie"] * 1e3, 4), n2(dce["vce"], 4), n2(dce["gm"] * 1e3, 4), n2(dce["rpi"] / 1e3, 4), n2(dce["re"], 4)))
    d.p("**AC analysis (mid-band).** The coupling and bypass capacitors are short circuits and $V_{CC}$ is an AC ground. With $C_E$, the emitter is grounded and the gain is given by [[e:ave1]]; without $C_E$, the emitter resistor produces negative feedback and the gain is given by [[e:ave2]], where $R_L'=R_C\\parallel R_L=%s$ k$\\Omega$. The output resistance (looking into the collector, $R_L$ excluded) is $R_o=R_C=5.6$ k$\\Omega$, and the input resistance is given by [[e:rie]]." % n2(ce["rlp"] / 1e3, 4))
    d.eq(r"A_V=-g_mR_L'=-%.2f\ \text{mS}\times%.3f\ \text{k}\Omega=%.1f" % (dce["gm"] * 1e3, ce["rlp"] / 1e3, ce["av_ce"]), "ave1")
    d.eq(r"A_V=-\frac{\beta R_L'}{r_\pi+(\beta+1)R_E}=-\frac{170\times%.3f\ \text{k}\Omega}{%.3f\ \text{k}\Omega+171\times1.8\ \text{k}\Omega}=%.3f" % (ce["rlp"] / 1e3, dce["rpi"] / 1e3, ce["av_no"]), "ave2")
    d.eq(r"R_i=R_1\parallel R_2\parallel r_\pi=%.2f\ \text{k}\Omega\ \ (\text{with }C_E),\qquad R_i=R_1\parallel R_2\parallel\left[r_\pi+(\beta+1)R_E\right]=%.2f\ \text{k}\Omega\ \ (\text{without }C_E)" % (ce["ri_ce"] / 1e3, ce["ri_no"] / 1e3), "rie")
    d.p("**Maximum output swing.** The AC load line passes through the Q point with the slope $-1/R_L'$. With $C_E$, the collector voltage can increase by $I_{CQ}R_L'=%s$ V before the transistor is cut off and decrease by $V_{CEQ}-V_{CE(sat)}=%s$ V before it saturates, so that the symmetrical swing is limited by saturation: $V_{O,pp,max}=2\\times%s=%s$ V. Without $C_E$, the AC load seen by the emitter\u2013collector path is $R_L'+R_E$, the collector current can decrease by $I_{CQ}$ or increase by $(V_{CEQ}-0.2)/(R_L'+R_E)=%s$ mA, and the output swing is $V_{O,pp,max}=2\\times%s\\ \\text{mA}\\times R_L'=%s$ V." % (
        n2(ce["up"], 4), n2(ce["dn"], 4), n2(min(ce["up"], ce["dn"]), 4), n2(ce["vo_ce"], 4), n2(ce["ic_dn"] * 1e3, 4), n2(ce["ic_dn"] * 1e3, 4), n2(ce["vo_no"], 4)))
    hdr = ["", "With $C_E$", "Without $C_E$"]
    rows = [
        ["$V_{BEQ}$ (V)", "0.62", "0.62"],
        ["$V_{CEQ}$ (V)", n2(dce["vce"], 4), n2(dce["vce"], 4)],
        ["$I_{BQ}$ (mA)", n2(dce["ib"] * 1e3, 4), n2(dce["ib"] * 1e3, 4)],
        ["$I_{CQ}$ (mA)", n2(dce["ic"] * 1e3, 4), n2(dce["ic"] * 1e3, 4)],
        ["$A_V=V_o/V_i$ (mid-band)", n2(ce["av_ce"], 4), n2(ce["av_no"], 4)],
        ["$V_O$ (peak-to-peak, max.) (V)", n2(ce["vo_ce"], 4), n2(ce["vo_no"], 4)],
        ["$R_i$ (k$\\Omega$) / $R_o$ (k$\\Omega$)", "%s / 5.6" % n2(ce["ri_ce"] / 1e3, 3), "%s / 5.6" % n2(ce["ri_no"] / 1e3, 3)],
        ["$|A_V|$ at 100 kHz (phasor analysis)", n2(abs(ce["av100"][0]), 4), n2(abs(ce["av100"][1]), 4)],
    ]
    d.tab("t1", hdr, rows, "Calculated values for the common-emitter amplifier circuit (the last two rows are additional)", widths=[7.6, 3.6, 3.6], size=9.5)
    d.p("The mid-band gain assumes that $C_E$ is a perfect short circuit. At the test frequency of 100 kHz, the impedance of $C_E=22$ nF is $1/(2\\pi fC_E)=72\\ \\Omega$, which is larger than $r_e=%s\\ \\Omega$. The gain is then reduced to $|A_V|\\approx R_L'/(r_e+|Z_E|)$, and a complete phasor analysis (including $C_{C1}$, $C_{C2}$ and $C_E$) gives $|A_V|=%s$ at 100 kHz instead of %s. A bypass capacitor of about %.2f \u00b5F would be needed for 90%% of the mid-band gain at 100 kHz. Without $C_E$, the gain is independent of frequency in this range (%s)." % (
        n2(dce["re"], 3), n2(abs(ce["av100"][0]), 3), n2(abs(ce["av_ce"]), 3), R["ce_need"] * 1e6, n2(abs(ce["av100"][1]), 3)))
    d.p("**SPICE.** The circuit was built with the BC238A model (Appendix A). The DC and AC results are compared with the calculations in [[t:cesp]], the frequency response is shown in [[f:cebode]]. A sinusoidal input of 100 kHz with zero offset was applied, and the output was analysed with the total harmonic distortion (THD) obtained from the FFT of ten steady-state periods. The THD of the output as a function of the input amplitude is shown in [[f:cethd]]. An output waveform is called undistorted when THD $\\leq1\\%$ (a THD of 5% is also given for reference), since the visual detection of the distortion of a sine wave is possible only above about 5%.")
    op = R["ce_op"]
    sp100 = R["ce_sp_gain100"]
    rows = [
        ["$V_{BEQ}$ (V)", "0.62", n2(op["vbe"], 4), pc(0.62, op["vbe"])],
        ["$V_{CEQ}$ (V)", n2(dce["vce"], 4), n2(op["vce"], 4), pc(dce["vce"], op["vce"])],
        ["$I_{BQ}$ (\u00b5A)", n2(dce["ib"] * 1e6, 4), n2(op["ib"] * 1e6, 4), pc(dce["ib"], op["ib"])],
        ["$I_{CQ}$ (mA)", n2(dce["ic"] * 1e3, 4), n2(op["ic"] * 1e3, 4), pc(dce["ic"], op["ic"])],
        ["$|A_V|$ at 100 kHz, with $C_E$", n2(abs(ce["av100"][0]), 4), n2(sp100[0], 4), pc(abs(ce["av100"][0]), sp100[0])],
        ["$|A_V|$ at 100 kHz, without $C_E$", n2(abs(ce["av100"][1]), 4), n2(sp100[1], 4), pc(abs(ce["av100"][1]), sp100[1])],
        ["$|A_V|$ maximum of the curve, with $C_E$ (SPICE, at %.0f kHz)" % (R["ce_sp_peak"][1] / 1e3), n2(abs(ce["av_ce"]), 4), n2(R["ce_sp_peak"][0], 4), pc(abs(ce["av_ce"]), R["ce_sp_peak"][0])],
        ["$|A_V|$ mid-band, without $C_E$", n2(abs(ce["av_no"]), 4), n2(R["ce_sp_mid"][1], 4), pc(abs(ce["av_no"]), R["ce_sp_mid"][1])],
        ["$R_i$ at 100 kHz, with $C_E$ (k$\\Omega$)", n2(R["ri100"][True][0] / 1e3, 4), n2(R["ri100"][True][1] / 1e3, 4), pc(R["ri100"][True][0], R["ri100"][True][1])],
        ["$R_i$ at 100 kHz, without $C_E$ (k$\\Omega$)", n2(R["ri100"][False][0] / 1e3, 4), n2(R["ri100"][False][1] / 1e3, 4), pc(R["ri100"][False][0], R["ri100"][False][1])],
    ]
    d.tab("cesp", ["Quantity", "Calculation", "SPICE", "Error"], rows, "Comparison of the calculation and SPICE for the common-emitter amplifier (Error = (SPICE $-$ calculation)/calculation)", widths=[7.4, 2.8, 2.8, 2.2], size=9)
    d.fig("cebode", R["fig_ce_bode"], "Frequency response of the common-emitter amplifier (SPICE and phasor calculation).", 13)
    cursor_table(d, "e5_ce_bode", "cebode")
    ltshots.add(d, "e5_ce_1", "lt_ce1")
    ltshots.add(d, "e5_ce_0", "lt_ce0")
    lim = R["ce_lim"]
    lp = R["ce_lim_pp"]
    d.p("**Highest undistorted amplitude.** For the circuit with $C_E$, the THD reaches 1%% at an input amplitude of %s mV peak (%s mV peak-to-peak), at which the output is %s V peak-to-peak (gain %s, equal to the phasor result); the THD reaches 5%% at %s mV peak-to-peak. For the circuit without $C_E$, the THD reaches 1%% at %s V peak-to-peak input (%s V peak-to-peak output) and 5%% at %s V peak-to-peak. The corresponding waveforms are shown in [[f:cetran]] (with $C_E$) and [[f:cetran2]] (without $C_E$); the top panel of each figure shows the highest undistorted amplitude, and the other panels show a larger amplitude and an overdriven input." % (
        n2(lim[(True, 1.0)] * 1e3, 3), n2(lp[True][0] * 1e3, 3), n2(lp[True][1], 3), n2(lp[True][1] / lp[True][0], 3), n2(2 * lim[(True, 5.0)] * 1e3, 3),
        n2(lp[False][0], 3), n2(lp[False][1], 3), n2(2 * lim[(False, 5.0)], 3)))
    d.fig("cethd", R["fig_ce_thd"], "Total harmonic distortion of the output voltage versus input amplitude (SPICE, 100 kHz).", 11)
    d.fig("cetran", R["fig_ce_tran_ce"], "Input and output voltages of the circuit with $C_E$ at three input amplitudes (the output waveform is shown with its DC level removed).", 13.5)
    cursor_table(d, "e5_ce_tran_ce", "cetran")
    d.fig("cetran2", R["fig_ce_tran_noce"], "Input and output voltages of the circuit without $C_E$ at three input amplitudes.", 13.5)
    cursor_table(d, "e5_ce_tran_noce", "cetran2")
    d.p("The limits above are very different from the load-line limits of [[t:t1]] (%s V and %s V peak-to-peak). With $C_E$, the output is limited by the curvature of the exponential $I_C$\u2013$V_{BE}$ characteristic, long before clipping: the second harmonic is approximately $v_{be}/(4V_T)$ of the fundamental for a bypassed emitter, so that a base\u2013emitter signal of only a few millivolts already gives about 1%% distortion. Without $C_E$, the emitter resistor linearizes the stage (the base\u2013emitter signal is only a small fraction of $v_i$), so that the distortion starts only when the signal approaches the clipping level, at about the load-line value. When the input is increased much more, the output clips (with the coupling capacitor shifting the DC level, the clipped output swings %s V peak-to-peak with $C_E$ and %s V without $C_E$)." % (
        n2(ce["vo_ce"], 3), n2(ce["vo_no"], 3), n2(R["ce_clip_pp"][True], 3), n2(R["ce_clip_pp"][False], 3)))

    # ------------------------------------------------ CC
    d.h(2, "Common-Collector Amplifier Analysis")
    d.p("**DC analysis.** With $V_{TH}=12\\times39/61=%s$ V and $R_{TH}=%s$ k$\\Omega$, [[e:ibcc]] gives the base current, and $V_{CE}=V_{CC}-I_ER_E$ because the collector is connected to $V_{CC}$." % (n2(dcc["vth"], 4), n2(dcc["rth"] / 1e3, 4)))
    d.eq(r"I_B=\frac{V_{TH}-V_{BE(on)}}{R_{TH}+(\beta+1)R_E}=\frac{%.4f-0.62}{%.3f\ \text{k}\Omega+171\cdot3.3\ \text{k}\Omega}=%.3f\ \mu\text{A}" % (dcc["vth"], dcc["rth"] / 1e3, dcc["ib"] * 1e6), "ibcc")
    d.p("Then $I_C=%s$ mA, $I_E=%s$ mA, and $V_{CE}=12-%s\\times3.3=%s$ V (active region). The small-signal parameters are $g_m=%s$ mS, $r_\\pi=%s$ k$\\Omega$ and $r_e=%s\\ \\Omega$." % (
        n2(dcc["ic"] * 1e3, 4), n2(dcc["ie"] * 1e3, 4), n2(dcc["ie"] * 1e3, 4), n2(dcc["vce"], 4), n2(dcc["gm"] * 1e3, 4), n2(dcc["rpi"] / 1e3, 4), n2(dcc["re"], 3)))
    d.p("**AC analysis.** The AC load of the emitter is $R_E'=R_E\\parallel R_L=%s$ k$\\Omega$. The voltage gain, the input resistance and the output resistance (with an ideal source) are given by [[e:avcc]]\u2013[[e:rocc]]. The maximum symmetrical swing is limited by saturation on the positive side ($V_{CEQ}-0.2=%s$ V) and by cut-off on the negative side ($I_{EQ}R_E'=%s$ V), and $V_{O,pp,max}=2\\times%s=%s$ V." % (
        n2(cc["rep"] / 1e3, 4), n2(cc["up"], 4), n2(cc["dn"], 4), n2(min(cc["up"], cc["dn"]), 4), n2(cc["vo"], 4)))
    d.eq(r"A_V=\frac{(\beta+1)R_E'}{r_\pi+(\beta+1)R_E'}=\frac{171\times%.3f\ \text{k}\Omega}{%.3f\ \text{k}\Omega+171\times%.3f\ \text{k}\Omega}=%.4f" % (cc["rep"] / 1e3, dcc["rpi"] / 1e3, cc["rep"] / 1e3, cc["av"]), "avcc")
    d.eq(r"R_i=R_1\parallel R_2\parallel\left[r_\pi+(\beta+1)R_E'\right]=%.2f\ \text{k}\Omega" % (cc["ri"] / 1e3), "ricc")
    d.eq(r"R_o=R_E\parallel\frac{r_\pi}{\beta+1}=%.2f\ \Omega" % cc["ro"], "rocc")
    rows = [
        ["$V_{BEQ}$ (V)", "0.62"], ["$V_{CEQ}$ (V)", n2(dcc["vce"], 4)], ["$I_{BQ}$ (mA)", n2(dcc["ib"] * 1e3, 4)], ["$I_{CQ}$ (mA)", n2(dcc["ic"] * 1e3, 4)],
        ["$A_V=V_o/V_i$", n2(cc["av"], 4)], ["$V_O$ (peak-to-peak, max.) (V)", n2(cc["vo"], 4)],
        ["$R_i$ (k$\\Omega$) / $R_o$ ($\\Omega$) (additional)", "%s / %s" % (n2(cc["ri"] / 1e3, 3), n2(cc["ro"], 3))],
    ]
    d.tab("t2", ["", "Calculated value"], rows, "Calculated values for the common-collector amplifier circuit", widths=[8.4, 4.4], size=9.5)
    op = R["cc_op"]
    rows = [
        ["$V_{BEQ}$ (V)", "0.62", n2(op["vbe"], 4), pc(0.62, op["vbe"])],
        ["$V_{CEQ}$ (V)", n2(dcc["vce"], 4), n2(op["vce"], 4), pc(dcc["vce"], op["vce"])],
        ["$I_{BQ}$ (\u00b5A)", n2(dcc["ib"] * 1e6, 4), n2(op["ib"] * 1e6, 4), pc(dcc["ib"], op["ib"])],
        ["$I_{EQ}$ (mA)", n2(dcc["ie"] * 1e3, 4), n2(op["ie"] * 1e3, 4), pc(dcc["ie"], op["ie"])],
        ["$A_V$ at 100 kHz", n2(abs(cc["av100"]), 4), n2(R["cc_sp_gain100"], 4), pc(abs(cc["av100"]), R["cc_sp_gain100"])],
        ["$R_i$ at 100 kHz (k$\\Omega$)", n2(R["ri100_cc"][0] / 1e3, 4), n2(R["ri100_cc"][1] / 1e3, 4), pc(R["ri100_cc"][0], R["ri100_cc"][1])],
        ["$R_o$ at 100 kHz ($\\Omega$)", n2(cc["ro"], 4), n2(R["cc_sp_ro"], 4), pc(cc["ro"], R["cc_sp_ro"])],
    ]
    d.tab("ccsp", ["Quantity", "Calculation", "SPICE", "Error"], rows, "Comparison of the calculation and SPICE for the common-collector amplifier", widths=[6.4, 3, 3, 2.4], size=9.5)
    thd, a1, a_in = R["cc_tran"]
    d.p("The input and output voltage graphs of the common-collector amplifier (1 V peak, 100 kHz) are shown in [[f:cctran]], and the frequency response is shown in [[f:ccbode]]. The output follows the input with a gain of %s and without a phase shift (THD = %.3f%%). The DC level of the output is removed by $C_{C2}$, and the transistor stays in the active region. When the input is increased to 8 V peak ([[f:ccclip]]), the output clips at +%s V and %s V (peak-to-peak %s V), which is larger than the symmetrical load-line value of %s V, because at large signals the base-current peaks charge $C_{C1}$ and shift the bias point to a larger swing." % (
        n2(R["cc_sp_gain100"], 4), thd, n2(R["cc_clip_levels"][0], 3), n2(R["cc_clip_levels"][1], 3), n2(R["cc_clip_pp"], 3), n2(cc["vo"], 3)))
    d.fig("cctran", R["fig_cc_tran"], "Input and output voltages of the common-collector amplifier (ngspice).", 13.5)
    cursor_table(d, "e5_cc_tran", "cctran")
    d.fig("ccbode", R["fig_cc_bode"], "Frequency response of the common-collector amplifier.", 12.5)
    cursor_table(d, "e5_cc_bode", "ccbode")
    ltshots.add(d, "e5_cc", "lt_cc")
    d.fig("ccclip", R["fig_cc_clip"], "Overdriven common-collector amplifier (the output clips on both sides).", 13.5)
    d.p("**Is it possible to double the gain?** No. From [[e:avcc]], $A_V=\\dfrac{(\\beta+1)R_E'}{r_\\pi+(\\beta+1)R_E'}$ is smaller than one for any finite $\\beta$, because the denominator is larger than the numerator by $r_\\pi$. The gain approaches one only when $(\\beta+1)R_E'\\gg r_\\pi$ (equivalently $R_E'\\gg r_e$), and it is already %s. The largest possible improvement is therefore %.1f%%, and a gain of about 2 cannot be obtained by changing the resistors or the bias. Physically, the output follows $v_e=v_b-V_{BE}$ with $V_{BE}$ almost constant, so that the emitter follower provides current gain ($\\beta+1$) and impedance transformation, but not voltage gain. A voltage gain of 2 requires another configuration (for example, a common-emitter stage) or an additional gain stage." % (n2(cc["av"], 4), (1 - cc["av"]) / cc["av"] * 100))

    d.h(2, "Maximum Voltage Swing (Extra Points)")
    d.p("The voltage swing of the common-collector amplifier is limited by two boundaries of the AC load line: the saturation limit on the positive side, $V_{CEQ}-V_{CE(sat)}$, and the cut-off limit on the negative side, $I_{EQ}R_E'$. The largest symmetrical swing is obtained when the two limits are equal, i.e., when $V_{CEQ}=I_{EQ}R_E'$ with $V_{CEQ}=V_{CC}-I_{EQ}R_E$, which gives the optimum emitter current of [[e:iopt]].")
    d.eq(r"I_{EQ,opt}=\frac{V_{CC}}{R_E+R_E'}=\frac{12}{%.3f\ \text{k}\Omega+%.3f\ \text{k}\Omega}=%.3f\ \text{mA},\qquad V_{O,pp,max}\approx2\left(V_{CC}-V_{CE(sat)}\right)\frac{R_E'}{R_E+R_E'}" % (3.3, cc["rep"] / 1e3, cc["icopt"] * 1e3), "iopt")
    d.p("The designed circuit has $I_{EQ}=%s$ mA and $V_{CEQ}=%s$ V, which is almost exactly the optimum ($I_{EQ}R_E'=%s$ V). The most important parameters for the swing are therefore (1) the bias resistors $R_1$, $R_2$ (the Q point), (2) the emitter and load resistors $R_E$, $R_L$ (the slope of the AC load line), (3) the supply voltage $V_{CC}$ (the available range) and (4) $V_{CE(sat)}$. The effects were investigated by SPICE simulations in which $R_2$ and $R_L$ were changed ([[t:sweep]], [[f:sweep]]); in each case, the DC values $V_{CEQ}$ and $I_{EQ}$ were found first, the two limits were calculated, and the largest output amplitude with THD $\\leq1\\%%$ was found by simulation." % (n2(dcc["ie"] * 1e3, 4), n2(dcc["vce"], 4), n2(cc["dn"], 4)))
    rows = [[n2(s[0] / 1e3, 3), n2(s[7], 3), n2(s[1] * 1e3, 3), n2(s[3], 3), n2(s[4], 3), n2(s[5], 3), n2(s[6], 3)] for s in R["sweep"]]
    d.tab("sweep", ["$R_2$ (k$\\Omega$)", "$V_{CEQ}$ SPICE (V)", "$I_{EQ}$ (mA)", "Sat. limit (V)", "Cut-off limit (V)", "Load-line $V_{O,pp}$ (V)", "SPICE $V_{O,pp}$, THD\u22641% (V)"], rows,
          "Effect of the bias resistor $R_2$ on the output swing of the common-collector amplifier ($R_1$ = 22 k$\\Omega$)", widths=[1.9, 2.4, 2.0, 2.0, 2.3, 2.7, 2.9], size=8.5)
    rows = [[n2(s[0] / 1e3, 3), n2(s[1], 3), n2(s[2], 3), n2(s[3], 3), n2(s[4], 3)] for s in R["sweep_rl"]]
    d.tab("sweeprl", ["$R_L$ (k$\\Omega$)", "Sat. limit (V)", "Cut-off limit (V)", "Load-line $V_{O,pp}$ (V)", "SPICE $V_{O,pp}$ (V)"], rows,
          "Effect of the load resistor $R_L$ on the output swing ($R_1$ = 22 k$\\Omega$, $R_2$ = 39 k$\\Omega$)", widths=[2.4, 2.8, 3.0, 3.6, 3.2], size=9)
    d.fig("sweep", R["fig_sweep"], "Swing limits and simulated swing of the common-collector amplifier versus the bias current (left) and $R_2$ (right).", 15.5)
    d.p("The results show the following. (1) For a small bias current ($R_2\\leq27$ k$\\Omega$), the swing is limited by cut-off ($I_{EQ}R_E'$) and grows in proportion to $I_{EQ}$; the load-line prediction and the simulation agree within 4%%. (2) Around the optimum bias ($R_2\\approx39$ k$\\Omega$), both limits are almost equal and the load-line swing is maximum (%s V). (3) For a larger bias current, the load line predicts a decrease of the swing since $V_{CEQ}$ becomes small (saturation limit), but the simulation shows a plateau of about %s V peak-to-peak: with a large signal, the peaks of the base current charge the coupling capacitor $C_{C1}$ and lower the average base voltage (for $R_2=150$ k$\\Omega$ and a 4 V input, the average base voltage falls from 10.1 V to 8.7 V), which moves the bias point towards the centre of the available range automatically. (4) A larger load resistor increases the cut-off limit ($I_{EQ}R_E'$) until the saturation limit (%s V) takes over; for $R_L\\geq10$ k$\\Omega$, the swing no longer improves in the load-line prediction, and the simulation gives %s V peak-to-peak for $R_L=47$ k$\\Omega$, close to the supply limit of 12 V. In summary, the swing is maximum when the Q point is at the middle of the AC load line, the load resistance is not small compared with $R_E$, and the supply voltage is as high as possible; $V_{CEQ}$ must be kept above $V_{CE(sat)}$ plus the half swing, and $V_{CE}$ must be monitored during the simulation to see on which side the clipping starts." % (
        n2(max(s[5] for s in R["sweep"]), 3), n2(R["sweep"][-1][6], 3), n2(cc["up"], 3), n2(R["sweep_rl"][-1][4], 3)))

    d.h(1, "Conclusions")
    d.p("The comparison of the calculations and SPICE showed that the DC operating points agree within about 2%% ($V_{CEQ}$: %s for the common-emitter and %s for the common-collector circuit), and that the voltage gains at 100 kHz agree within 0.1%% (%s and %s) when the capacitor impedances are included in the calculation. The mid-band gain of the common-emitter amplifier with $C_E$ ($|A_V|=%s$) is not reached at 100 kHz, since the 22 nF bypass capacitor has an impedance of 72 $\\Omega$ at this frequency, which is larger than $r_e=%s\\ \\Omega$; the measured gain is %s, and the simulated maximum of the frequency response is %s at %.0f kHz (%s relative to the hand value) because the model parameters and the transistor capacitances differ from the ideal model. The input resistance with $C_E$ at 100 kHz is smaller in SPICE (%s versus %s k$\\Omega$) because of the Miller effect of the collector capacitance, which is not included in the hand analysis." % (
        pc(dce["vce"], op_ce_vce(R)), pc(dcc["vce"], R["cc_op"]["vce"]), pc(abs(ce["av100"][0]), R["ce_sp_gain100"][0]), pc(abs(cc["av100"]), R["cc_sp_gain100"]),
        n2(abs(ce["av_ce"]), 3), n2(dce["re"], 3), n2(R["ce_sp_gain100"][0], 3), n2(R["ce_sp_peak"][0], 3), R["ce_sp_peak"][1] / 1e3, pc(abs(ce["av_ce"]), R["ce_sp_peak"][0]),
        n2(R["ri100"][True][1] / 1e3, 3), n2(R["ri100"][True][0] / 1e3, 3)))
    d.p("The largest undistorted output of the common-emitter amplifier with $C_E$ is only %s V peak-to-peak, which is limited by the exponential characteristic and not by clipping (the load-line value is %s V); the emitter resistor increases the linear range by a factor of about %.0f at the cost of the gain (%s instead of %s). The emitter follower has a gain of %s, a high input resistance (%s k$\\Omega$), a low output resistance (%s $\\Omega$) and a large swing (%s V peak-to-peak by the load line), and its gain cannot be doubled. The swing is maximum when the Q point is at the middle of the AC load line, which the given design nearly satisfies." % (
        n2(lp[True][1], 3), n2(ce["vo_ce"], 3), lp[False][0] / lp[True][0], n2(abs(ce["av100"][1]), 3), n2(abs(ce["av100"][0]), 3), n2(cc["av"], 3), n2(cc["ri"] / 1e3, 3), n2(cc["ro"], 3), n2(cc["vo"], 3)))
    d.h(1, "References")
    d.bullets([
        "Fairchild Semiconductor. (2002). BC237/238/239 NPN epitaxial silicon transistor [Data sheet, Rev. A2]. Retrieved October 11, 2026, from https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2309151357_onsemi-BC237_C3201628.pdf",
        "Sedra, A. S., & Smith, K. C. (2014). Microelectronic circuits (7th ed.). New York: Oxford University Press.",
        "ngspice. (n.d.). ngspice user manual. Retrieved October 11, 2026, from https://ngspice.sourceforge.io/docs.html",
    ], numbered=True)
    d.h(1, "Appendices")
    d.h(2, "Appendix A: SPICE Model and Netlists")
    d.code(exp5.QM, "Code A.1  BJT model line used in the ngspice simulations (see Experiment 4 for the fitting of the parameters)")
    d.code(clean_cir(os.path.join(SPICE, "e5_ce_ac_1.cir")), "Netlist A.2  Common-emitter amplifier with $C_E$ (AC analysis; the transient netlist differs only in the analysis command)")
    d.code(clean_cir(os.path.join(SPICE, "e5_cc_ac.cir")), "Netlist A.3  Common-collector amplifier (AC analysis)")
    return d


def op_ce_vce(R):
    return R["ce_op"]["vce"]


def build_tr(R):
    d = Doc("tr")
    ce, cc = R["ce"], R["cc"]
    dce, dcc = ce["d"], cc["d"]
    d.title_block([
        ("Deney 5 \u2013 Ön Çalışma Öğretici Rehberi", 15, True),
        ("BJT Yükselteçleri: Ortak Emetör ve Ortak Kollektör", 12, False),
        ("Bu belge SADECE ÖĞRENMEK içindir; teslim edilecek metin İngilizce rapordur.", 11, False),
    ], [("Ad Soyad", ""), ("Numara", ""), ("Tarih", "")])
    d.h(1, "Büyük Resim")
    d.p("Yükselteç, BJT'yi doğru bir DC noktada tutup üzerine küçük bir AC sinyal bindirerek **büyük bir AC çıkış** elde etme işidir. BJT'nin üç temel bağlantı şekli vardır: ortak emetör (gerilim kazancı büyük, evirici), ortak kollektör (**emetör izleyici**: gerilim kazancı ≈1, giriş direnci yüksek, çıkış direnci düşük), ortak baz (bu deneyde yok). Bu deney ilk ikisini öğretir.")
    d.box("Önceki deneyle bağ", ["Deney 4'te devrenin DC noktasını (Q noktası) buldunuz. Bu deneyde aynı Q noktasının **etrafındaki küçük değişimlerin** (AC) nasıl büyütüldüğü incelenir. Her adım iki aşamalıdır: **(1) DC çöz** (kondansatörler açık devre), **(2) AC çöz** (kondansatörler kısa devre, $V_{CC}$ toprak).",])
    d.h(1, "Soru 1: Breadboard Hatalarını Bulmak")
    d.p("Sizden verilen çizimdeki hataları bulmanız ve eksik elemanı eklemeniz istendi. Bunu **tahmin ederek değil, bağlantıları delik delik okuyarak** yaptım: Breadboard'da bir sütunun a–e delikleri (alt blok) ve f–j delikleri (üst blok) kendi içinde bağlıdır; ray satırları boydan boya bağlıdır. Çizimdeki her bacak, tel ve eleman ucu hangi sütun/rayda ise o düğüme aittir. Çıkan düğüm listesi:")
    d.tab("nets", ["Düğüm (sütun)", "Üyeler", "Anlamı"], [
        ["Sütun 18 (alt)", "Q1.C, RC (bir ucu), CC2'ye giden tel", "Kolektör düğümü ✓"],
        ["Sütun 27 (alt)", "Q1.B, R1 (bir ucu), R2 (bir ucu), CC1 (bir ucu)", "Baz düğümü ✓ (yeşil tel 19→27 ile baza bağlı)"],
        ["Sütun 20 (alt)", "Q1.E, RE (bir ucu)", "Emetör düğümü: CE yok ✗ (E5)"],
        ["Sütun 15 (alt)", "RC'nin diğer ucu, R1'in diğer ucu", "$V_{CC}$ düğümü: ray yok ✗ (E1)"],
        ["Sütun 24 (alt)", "RE'nin diğer ucu, R2'nin diğer ucu", "Toprak düğümü: ray yok ✗ (E2)"],
        ["Sütun 17 (üst)", "RL'nin ikinci ucu", "Hiçbir yere bağlı değil ✗ (E3)"],
        ["+ rayı", "CC1'in serbest ucu (28. sütun)", "Beslemenin giriş kondansatörüne bağlanması ✗ (E4)"],
    ], "Verilen çizimden okunan düğümler (otomatik çıkarım)", widths=[3.2, 6.6, 5.2], size=9)
    d.fig("found", R["fig_bb_found"], "Verilen çizim: hatalar kırmızı kesikli dairelerle gösterildi.", 15.5)
    d.tab("errs", ["No.", "Hata", "Düzeltme"], [[e[0], e[1], e[2]] for e in ERRS_TR], "Hatalar ve düzeltmeleri", widths=[1.2, 6.6, 7.4], size=9)
    d.box("Neden bu 5 hata? (Eleştirel not)", [
        "Hatalar listesi **benim okumama** dayanır: çizim küçük olduğu için direnç renk kodlarını büyüterek okudum (5,6 kΩ: yeşil-mavi-kırmızı; 120 kΩ: kahverengi-kırmızı-sarı; 1,8 kΩ: kahverengi-gri-kırmızı; 39 kΩ: turuncu-beyaz-turuncu; 15 kΩ: kahverengi-yeşil-turuncu; hepsi doğru). E4 için not: + rayına giden telin ucunun CC1'in 28. sütunundaki bacağında bittiğini görüyorum; sizce o tel bilerek 'giriş' olarak konulduysa bile + rayı besleme olduğundan hata sayılır (giriş, fonksiyon üretecinden gelmelidir).",
        "Kondansatörlerin 22 nF mı 2,2 nF mı olduğu çizimde yazmadığından (mavi disk) değer doğrulanamaz; devre şemasına göre sağdaki (girişe yakın) CC1=22 nF, soldaki (çıkışa yakın) CC2=2,2 nF alındı.",
    ], fill="FFF4E0")
    d.fig("ces", R["fig_ce_schem"], "Ortak emetörlü yükselteç devre şeması.", 12)
    d.fig("bbce", R["fig_bb_ce"], "Düzeltilmiş breadboard çizimi ($C_E$ eklendi; bağlantılar otomatik denetlendi).", 15.5)
    els_table(d, False)
    d.h(2, "Ortak kollektörlü devrenin breadboard çizimi (Soru 1.3)")
    d.fig("ccs", R["fig_cc_schem"], "Ortak kollektörlü yükselteç devre şeması.", 12)
    d.fig("bbcc", R["fig_bb_cc"], "Ortak kollektörlü yükselteçin breadboard çizimi.", 15.5)
    d.bullets([
        "Kolektör **doğrudan +$V_{CC}$**'ye bağlanır (kırmızı tel, 12. sütun); kollektör direnci yoktur. AC'de $V_{CC}$ toprak olduğundan kolektör 'ortak' uçtur: bu yüzden adı ortak kollektör.",
        "$R_1$=22 kΩ (9→13) üstten, $R_2$=39 kΩ (7→13) alttan baz bölücüsünü kurar. Giriş $C_{C1}$ ile baza (13. sütun) verilir.",
        "Çıkış **emetörden** $C_{C2}$ ile alınır ve $R_L$=10 kΩ'a bağlanır; $R_E$=3,3 kΩ (14→18) emetörden toprağa.",
    ])
    d.h(1, "BC238A Parametreleri (hatırlatma)")
    d.p("$\\beta=170$ (A sınıfının 120–220 aralığının ortası), $V_{BE(on)}=0{,}62$ V (tipik; $I_C=2$ mA'de), Early gerilimi ihmal. $V_T=26$ mV alındı (föy Deney 1'deki gibi).")

    d.h(1, "Soru 2: Ortak Emetörlü Yükselteç")
    d.h(2, "Adım 1 – DC analiz")
    d.p("Kondansatörler açık devre. Bölücüyü Thévenin eşdeğeriyle değiştirin: $V_{TH}=12\\times\\tfrac{39}{159}=%s$ V; $R_{TH}=120\\parallel39=%s$ kΩ. (**Neden Thévenin?** Baz döngüsünü tek direnç ve tek kaynakla yazabilmek için.)" % (n2(dce["vth"], 4), n2(dce["rth"] / 1e3, 4)))
    d.eq(r"I_B=\frac{V_{TH}-V_{BE(on)}}{R_{TH}+(\beta+1)R_E}=\frac{%.4f-0.62}{%.3f\ \text{k}\Omega+171\cdot1.8\ \text{k}\Omega}=%.3f\ \mu\text{A}" % (dce["vth"], dce["rth"] / 1e3, dce["ib"] * 1e6), "ib")
    d.bullets([
        "$I_C=\\beta I_B=170\\times%s\\ \\mu\\text{A}=%s$ mA; $I_E=(\\beta+1)I_B=%s$ mA." % (n2(dce["ib"] * 1e6, 4), n2(dce["ic"] * 1e3, 4), n2(dce["ie"] * 1e3, 4)),
        "$V_{CE}=12-%s\\times5{,}6-%s\\times1{,}8=%s$ V. **Doğrulama:** $V_{CE}>0{,}2$ V ✓ (aktif)." % (n2(dce["ic"] * 1e3, 4), n2(dce["ie"] * 1e3, 4), n2(dce["vce"], 4)),
        "$g_m=I_C/V_T=%s$ mS; $r_\\pi=\\beta/g_m=%s$ kΩ; $r_e=V_T/I_E=%s\\ \\Omega$." % (n2(dce["gm"] * 1e3, 4), n2(dce["rpi"] / 1e3, 4), n2(dce["re"], 3)),
    ])
    d.h(2, "Adım 2 – AC analiz (orta bant)")
    d.p("**CE'li:** emetör AC'de topraklı ⇒ $v_{be}=v_i$, $i_c=g_mv_i$, çıkış $v_o=-g_mR_L'v_i$ ($R_L'=R_C\\parallel R_L=%s$ kΩ):" % n2(ce["rlp"] / 1e3, 4))
    d.eq(r"A_V=-g_mR_L'=-%.2f\ \text{mS}\times%.3f\ \text{k}\Omega=%.1f" % (dce["gm"] * 1e3, ce["rlp"] / 1e3, ce["av_ce"]), "ave1")
    d.p("**CE'siz:** $v_i=v_{be}+i_eR_E$. $i_e\\approx(\\beta+1)i_b$ ve $v_{be}=i_br_\\pi$ ⇒ $v_i=i_b[r_\\pi+(\\beta+1)R_E]$. Çıkış $v_o=-\\beta i_bR_L'$:")
    d.eq(r"A_V=-\frac{\beta R_L'}{r_\pi+(\beta+1)R_E}=-\frac{170\times%.3f\ \text{k}\Omega}{%.3f\ \text{k}\Omega+171\times1.8\ \text{k}\Omega}=%.3f" % (ce["rlp"] / 1e3, dce["rpi"] / 1e3, ce["av_no"]), "ave2")
    d.p("Yani bypass kondansatörü kazancı %.0f kat artırır (183,7 / 2,22). CE'siz kazanç yaklaşık $-R_L'/R_E=-2{,}3$; yani yalnızca dirençlere bağlıdır ve transistörün β'sına ya da sıcaklığına duyarsızdır (geri besleme)." % (abs(ce["av_ce"]) / abs(ce["av_no"])))
    d.p("**Ri ve Ro:** $R_i=R_1\\parallel R_2\\parallel r_\\pi=%s$ kΩ (CE'li); $R_i=R_1\\parallel R_2\\parallel[r_\\pi+(\\beta+1)R_E]=%s$ kΩ (CE'siz). Neden CE'li devrenin giriş direnci çok küçük? Çünkü CE emetörü topraklayınca bazdan bakınca yalnızca $r_\\pi$ kalır; CE'siz durumda $R_E$ $(\\beta+1)$ kat büyümüş görünür. $R_o=R_C=5{,}6$ kΩ ($R_L$ hariç)." % (n2(ce["ri_ce"] / 1e3, 3), n2(ce["ri_no"] / 1e3, 3)))
    d.h(2, "Adım 3 – Maksimum çıkış gerilimi (VO, tepeden tepeye)")
    d.p("AC yük doğrusu Q noktasından geçer ve eğimi $-1/R_L'$'dir (CE'li). Kolektör gerilimi **yukarı** doğru en fazla $I_{CQ}R_L'=%s$ V artabilir (sonra transistör kesime girer); **aşağı** doğru en fazla $V_{CEQ}-V_{CE(sat)}=%s$ V azalabilir (sonra doyar). Simetrik salınım küçük olanla sınırlıdır: $V_{O,pp,max}=2\\times%s=%s$ V. CE'siz devrede AC yükü $R_L'+R_E$ gibi davranır: $i_c$ aşağıda $-I_{CQ}$, yukarıda $+(V_{CEQ}-0{,}2)/(R_L'+R_E)=%s$ mA ile sınırlıdır ve çıkış $=i_cR_L'$: $V_{O,pp,max}=%s$ V." % (
        n2(ce["up"], 4), n2(ce["dn"], 4), n2(min(ce["up"], ce["dn"]), 4), n2(ce["vo_ce"], 4), n2(ce["ic_dn"] * 1e3, 4), n2(ce["vo_no"], 4)))
    rows = [
        ["$V_{BEQ}$ (V)", "0,62", "0,62"], ["$V_{CEQ}$ (V)", n2(dce["vce"], 4), n2(dce["vce"], 4)], ["$I_{BQ}$ (mA)", n2(dce["ib"] * 1e3, 4), n2(dce["ib"] * 1e3, 4)],
        ["$I_{CQ}$ (mA)", n2(dce["ic"] * 1e3, 4), n2(dce["ic"] * 1e3, 4)], ["$A_V=V_o/V_i$ (orta bant)", n2(ce["av_ce"], 4), n2(ce["av_no"], 4)],
        ["$V_O$ (tepeden tepeye, maks.) (V)", n2(ce["vo_ce"], 4), n2(ce["vo_no"], 4)],
        ["100 kHz'te $|A_V|$ (fazör analizi; ek)", n2(abs(ce["av100"][0]), 4), n2(abs(ce["av100"][1]), 4)],
    ]
    d.tab("t1", ["", "CE'li", "CE'siz"], rows, "Föy Tablo 1'in hesaplanmış hâli", widths=[7.6, 3.6, 3.6], size=9.5)
    d.h(2, "Adım 4 – 100 kHz tuzağı (Deney 3'teki gibi)")
    d.p("CE=22 nF'ın 100 kHz'teki empedansı $1/(2\\pi\\cdot10^5\\cdot22\\cdot10^{-9})=72\\ \\Omega$. Kısa devre sayılabilmesi için $r_e=%s\\ \\Omega$'dan **çok küçük** olması gerekir; değil! Bu yüzden 100 kHz'te kazanç kabaca $R_L'/(r_e+|Z_{CE}|)\\approx4078/(22+72)\\approx43$ mertebesine düşer (kaba tahmin). Eksiksiz fazör analizi $|A_V|=%s$ verir (orta bant %s). SPICE %s verir." % (n2(dce["re"], 3), n2(abs(ce["av100"][0]), 3), n2(abs(ce["av_ce"]), 3), n2(R["ce_sp_gain100"][0], 3)))
    d.fig("cebode", R["fig_ce_bode"], "CE'li ve CE'siz devrenin frekans cevabı (SPICE ve fazör hesabı).", 13)
    ltshots.add(d, "e5_ce_1", "lt_ce1", tr=True)
    ltshots.add(d, "e5_ce_0", "lt_ce0", tr=True)
    d.box("Ne yazmalısınız?", [
        "Tabloya **orta bant** değerlerini yazın (−183,7 ve −2,22; VO: 6,24 V ve 4,33 V). Yorum kısmında 100 kHz'te CE'nin kısa devre sayılamayacağını ve %.2f µF'lık bir kondansatörün %%90 kazanç için gerekeceğini yazın. Böylece hesapla simülasyon arasındaki farkı kendiniz açıklamış olursunuz." % (R["ce_need"] * 1e6),
    ])
    d.h(2, "Adım 5 – SPICE: bozulmasız en büyük genlik")
    d.p("Föy 'çıkışta bozulma olmayan en yüksek tepeden-tepeye giriş genliği'ni ister. 'Bozulma' sinüsten sapmadır. Bunu **sayıyla** tanımlamak için çıkışın **THD** değerine bakıldı: ana frekansın harmoniklerinin enerjisinin temel bileşene oranı (FFT ile). **THD ≤ %1 'bozulma yok' kabul edildi** (%5 için de değer verilir, çünkü gözle fark edilebilir bozulma yaklaşık %5'ten sonra başlar). Bu kabul benimdir; föy bir eşik vermiyor. Raporda kabulünüzü yazın.")
    lim, lp = R["ce_lim"], R["ce_lim_pp"]
    d.tab("thd", ["Devre", "THD=%1 sınırı: giriş (pp)", "çıkış (pp)", "THD=%5 sınırı: giriş (pp)"], [
        ["CE'li", "%s mV" % n2(lp[True][0] * 1e3, 3), "%s V" % n2(lp[True][1], 3), "%s mV" % n2(2 * lim[(True, 5.0)] * 1e3, 3)],
        ["CE'siz", "%s V" % n2(lp[False][0], 3), "%s V" % n2(lp[False][1], 3), "%s V" % n2(2 * lim[(False, 5.0)], 3)],
    ], "SPICE ile bulunan bozulmasız en büyük genlikler (100 kHz)", widths=[2.6, 4.6, 3.2, 4.6], size=9.5)
    d.fig("cethd", R["fig_ce_thd"], "Çıkış THD'sinin giriş genliğine göre değişimi.", 11)
    d.fig("cetran", R["fig_ce_tran_ce"], "CE'li devre: (üstte) bozulmasız sınır; (ortada) daha büyük giriş; (altta) aşırı sürme.", 13.5)
    d.fig("cetran2", R["fig_ce_tran_noce"], "CE'siz devre.", 13.5)
    d.bullets([
        "**CE'li devrede sınır çok küçük (≈%s mV pp giriş)**: BJT'nin $I_C=I_Se^{V_{BE}/V_T}$ karakteristiği **eğridir**. $v_{be}$ büyüdükçe $i_c$ simetrik değişmez; pozitif tepede fazla artar, negatif tepede az azalır ⇒ ikinci harmonik (kabaca $v_{be}/(4V_T)$ oranında). Yani sınır **kırpılma değil, eğrilik** belirler. CE'li devrede kazanç büyük olduğundan çıkış yine de ≈%s V pp'ye ulaşır." % (n2(lp[True][0] * 1e3, 3), n2(lp[True][1], 3)),
        "**CE'siz devrede sınır çok büyük (≈%s V pp giriş):** $R_E$ yerel geri besleme yapar; $v_{be}$ giriş sinyalinin küçük bir kısmıdır, eğrilik etkisi azalır. Sınırı bu kez kırpılma belirler; el hesabındaki %s V pp'ye yakındır." % (n2(lp[False][0], 3), n2(ce["vo_no"], 3)),
        "**Genel ilke:** Kazanç ile doğrusal aralık arasında takas vardır: kazancı CE ile büyütürseniz bozulmasız genlik küçülür.",
        "**Aşırı sürüldüğünde** çıkış her iki yönde kırpılır (CE'li: tepeden tepeye ≈%s V; CE'siz: ≈%s V — kuplaj kondansatörü DC seviyeyi kaydırdığı için yük doğrusu hesabından büyük çıkabilir)." % (n2(R["ce_clip_pp"][True], 3), n2(R["ce_clip_pp"][False], 3)),
    ])
    op = R["ce_op"]
    rows = [
        ["$V_{BEQ}$ (V)", "0,62", n2(op["vbe"], 4), pc(0.62, op["vbe"])],
        ["$V_{CEQ}$ (V)", n2(dce["vce"], 4), n2(op["vce"], 4), pc(dce["vce"], op["vce"])],
        ["$I_{CQ}$ (mA)", n2(dce["ic"] * 1e3, 4), n2(op["ic"] * 1e3, 4), pc(dce["ic"], op["ic"])],
        ["$|A_V|$ 100 kHz, CE'li", n2(abs(ce["av100"][0]), 4), n2(R["ce_sp_gain100"][0], 4), pc(abs(ce["av100"][0]), R["ce_sp_gain100"][0])],
        ["$|A_V|$ 100 kHz, CE'siz", n2(abs(ce["av100"][1]), 4), n2(R["ce_sp_gain100"][1], 4), pc(abs(ce["av100"][1]), R["ce_sp_gain100"][1])],
        ["$|A_V|$ eğrinin tepesi, CE'li (SPICE, %.0f kHz'te)" % (R["ce_sp_peak"][1] / 1e3), n2(abs(ce["av_ce"]), 4), n2(R["ce_sp_peak"][0], 4), pc(abs(ce["av_ce"]), R["ce_sp_peak"][0])],
    ]
    d.tab("cesp", ["Büyüklük", "Hesap", "SPICE", "Hata"], rows, "CE'li devre: hesap ve SPICE", widths=[7.4, 2.8, 2.8, 2.2], size=9)
    d.p("**SPICE'ta orta bant neden %s (el: %s)?** Hesapta $V_T=26$ mV ve ideal transistör kullanıldı; SPICE'ın $V_T=25{,}865$ mV'u, $V_{BE}=0{,}607$ V'luk gerçek $V_{BE}$'si ve $C_\\pi$, $C_\\mu$ kapasiteleri (yüksek frekansta kazancı düşürür; eğri tepesi bile frekanstan etkilenir) birlikte %s fark yapar. 100 kHz'te ise fazör analizi SPICE ile %%0,03 içinde uyuşur çünkü orada kazancı belirleyen şey $C_E$ empedansıdır." % (n2(R["ce_sp_peak"][0], 3), n2(abs(ce["av_ce"]), 3), pc(abs(ce["av_ce"]), R["ce_sp_peak"][0])))

    d.h(1, "Soru 3: Ortak Kollektörlü Yükselteç")
    d.h(2, "DC")
    d.p("$V_{TH}=12\\times\\tfrac{39}{61}=%s$ V; $R_{TH}=22\\parallel39=%s$ kΩ. $I_B=\\dfrac{%.4f-0{,}62}{%.3f\\ \\text{k}+171\\times3{,}3\\ \\text{k}}=%s\\ \\mu$A; $I_C=%s$ mA; $I_E=%s$ mA; **$V_{CE}=12-I_ER_E=12-%s\\times3{,}3=%s$ V** (kolektör doğrudan $V_{CC}$'de olduğundan $R_C$ yok). Aktif ✓. $g_m=%s$ mS; $r_\\pi=%s$ kΩ; $r_e=%s\\ \\Omega$." % (
        n2(dcc["vth"], 4), n2(dcc["rth"] / 1e3, 4), dcc["vth"], dcc["rth"] / 1e3, n2(dcc["ib"] * 1e6, 4), n2(dcc["ic"] * 1e3, 4), n2(dcc["ie"] * 1e3, 4), n2(dcc["ie"] * 1e3, 4), n2(dcc["vce"], 4), n2(dcc["gm"] * 1e3, 4), n2(dcc["rpi"] / 1e3, 4), n2(dcc["re"], 3)))
    d.h(2, "AC (emetör izleyici)")
    d.p("Çıkış emetörden alınır. $v_e=v_b-v_{be}$ ve $v_{be}$ küçük olduğundan çıkış girişi **izler** (aynı fazda). Emetörün AC yükü $R_E'=R_E\\parallel R_L=%s$ kΩ. $v_i=i_b[r_\\pi+(\\beta+1)R_E']$ ve $v_o=(\\beta+1)i_bR_E'$ ⇒" % n2(cc["rep"] / 1e3, 4))
    d.eq(r"A_V=\frac{(\beta+1)R_E'}{r_\pi+(\beta+1)R_E'}=\frac{171\times%.3f\ \text{k}\Omega}{%.3f\ \text{k}\Omega+171\times%.3f\ \text{k}\Omega}=%.4f" % (cc["rep"] / 1e3, dcc["rpi"] / 1e3, cc["rep"] / 1e3, cc["av"]), "avcc")
    d.eq(r"R_i=R_1\parallel R_2\parallel\left[r_\pi+(\beta+1)R_E'\right]=%.2f\ \text{k}\Omega,\qquad R_o=R_E\parallel\frac{r_\pi}{\beta+1}=%.2f\ \Omega" % (cc["ri"] / 1e3, cc["ro"]), "ricc")
    d.p("**Yorum:** $R_i$ büyük (13,6 kΩ; bölücü ile sınırlı) ve $R_o$ çok küçük (12 Ω): yani önceki katı yüklemeyen, sonraki yükü kolay süren bir **tampon (buffer)**. Çıkış direnci küçük çünkü emetörden bakınca $r_\\pi/(\\beta+1)\\approx r_e$ görünür (baz tarafındaki direnç $(\\beta+1)$ kat küçülerek yansır).")
    d.p("**VO(pp,maks):** pozitif yönde doyma sınırı $V_{CEQ}-0{,}2=%s$ V; negatif yönde kesim sınırı $I_{EQ}R_E'=%s$ V; simetrik salınım $2\\times%s=%s$ V." % (n2(cc["up"], 4), n2(cc["dn"], 4), n2(min(cc["up"], cc["dn"]), 4), n2(cc["vo"], 4)))
    d.tab("t2", ["", "Hesaplanan değer"], [
        ["$V_{BEQ}$ (V)", "0,62"], ["$V_{CEQ}$ (V)", n2(dcc["vce"], 4)], ["$I_{BQ}$ (mA)", n2(dcc["ib"] * 1e3, 4)], ["$I_{CQ}$ (mA)", n2(dcc["ic"] * 1e3, 4)],
        ["$A_V=V_o/V_i$", n2(cc["av"], 4)], ["$V_O$ (tepeden tepeye, maks.) (V)", n2(cc["vo"], 4)]], "Föy Tablo 2'nin hesaplanmış hâli", widths=[8.4, 4.4], size=9.5)
    d.h(2, "SPICE")
    thd, a1, a_in = R["cc_tran"]
    d.fig("cctran", R["fig_cc_tran"], "Ortak kollektörlü yükselteç: giriş ve çıkış (1 V tepe, 100 kHz).", 13.5)
    d.fig("ccbode", R["fig_cc_bode"], "Ortak kollektörlü yükselteçin frekans cevabı.", 12.5)
    ltshots.add(d, "e5_cc", "lt_cc", tr=True)
    op = R["cc_op"]
    rows = [
        ["$V_{BEQ}$ (V)", "0,62", n2(op["vbe"], 4), pc(0.62, op["vbe"])],
        ["$V_{CEQ}$ (V)", n2(dcc["vce"], 4), n2(op["vce"], 4), pc(dcc["vce"], op["vce"])],
        ["$I_{EQ}$ (mA)", n2(dcc["ie"] * 1e3, 4), n2(op["ie"] * 1e3, 4), pc(dcc["ie"], op["ie"])],
        ["$A_V$ 100 kHz", n2(abs(cc["av100"]), 4), n2(R["cc_sp_gain100"], 4), pc(abs(cc["av100"]), R["cc_sp_gain100"])],
        ["$R_i$ 100 kHz (kΩ)", n2(R["ri100_cc"][0] / 1e3, 4), n2(R["ri100_cc"][1] / 1e3, 4), pc(R["ri100_cc"][0], R["ri100_cc"][1])],
        ["$R_o$ 100 kHz (Ω)", n2(cc["ro"], 4), n2(R["cc_sp_ro"], 4), pc(cc["ro"], R["cc_sp_ro"])],
    ]
    d.tab("ccsp", ["Büyüklük", "Hesap", "SPICE", "Hata"], rows, "El hesabı ve SPICE", widths=[6.4, 3, 3, 2.4], size=9.5)
    d.p("Çıkış girişi 0,992 kazançla ve faz farkı olmadan izler (THD %%%.3f). Burada CC1/CC2 kondansatörleri ve 100 kHz uyumlu: $C_{C2}$ için $1/(\\omega C)=724\\ \\Omega\\ll R_L$ olduğundan el hesabı ile SPICE %%0,01 içinde uyuşur (CE'li devredeki tuzak burada yok, çünkü hiçbir kondansatör küçük bir dirençle karşılaşmıyor)." % thd)
    d.h(2, "Kazanç iki katına çıkarılabilir mi?")
    d.p("**Hayır.** $A_V=\\dfrac{(\\beta+1)R_E'}{r_\\pi+(\\beta+1)R_E'}$ paydası payından $r_\\pi$ kadar büyüktür, dolayısıyla her zaman **1'den küçüktür.** $R_E'\\to\\infty$ ya da $\\beta\\to\\infty$ olsa bile en fazla 1'e yaklaşır. Şimdiki değer %s; mümkün en büyük iyileşme %%%.1f. Kazancı 2 yapmak istiyorsanız başka bir devre (ör. ortak emetör) gerekir. Fiziksel neden: $V_E=V_B-V_{BE}$ ve $V_{BE}\\approx0{,}6$ V sabittir; yani çıkış girişten **daha büyük olamaz**. Emetör izleyici gerilim değil **akım kazancı** sağlar: giriş akımı $i_b$, çıkış akımı $(\\beta+1)i_b$." % (n2(cc["av"], 4), (1 - cc["av"]) / cc["av"] * 100))
    d.h(2, "Ekstra puan: En yüksek gerilim salınımı")
    d.p("Salınım iki sınırla belirlenir: pozitif tepede **doyma** ($V_{CEQ}-0{,}2$ V), negatif tepede **kesim** ($I_{EQ}R_E'$). En büyük simetrik salınım iki sınır eşit olunca elde edilir: $V_{CEQ}=I_{EQ}R_E'$. $V_{CEQ}=V_{CC}-I_{EQ}R_E$ yazarsak optimum akım:")
    d.eq(r"I_{EQ,opt}=\frac{V_{CC}}{R_E+R_E'}=\frac{12}{3.3\ \text{k}\Omega+%.3f\ \text{k}\Omega}=%.3f\ \text{mA}" % (cc["rep"] / 1e3, cc["icopt"] * 1e3), "iopt")
    d.p("Verilen devrede $I_{EQ}=%s$ mA: **tasarım neredeyse optimum** ($V_{CEQ}=%s$ V; $I_{EQ}R_E'=%s$ V). Parametre taramaları ($R_2$ ve $R_L$ değiştirilerek):" % (n2(dcc["ie"] * 1e3, 4), n2(dcc["vce"], 4), n2(cc["dn"], 4)))
    rows = [[n2(s[0] / 1e3, 3), n2(s[7], 3), n2(s[1] * 1e3, 3), n2(s[3], 3), n2(s[4], 3), n2(s[5], 3), n2(s[6], 3)] for s in R["sweep"]]
    d.tab("sweep", ["$R_2$ (kΩ)", "$V_{CEQ}$ SPICE (V)", "$I_{EQ}$ (mA)", "Doyma sınırı (V)", "Kesim sınırı (V)", "Yük doğrusu $V_{O,pp}$", "SPICE $V_{O,pp}$ (THD≤1%)"], rows, "$R_2$'nin salınıma etkisi ($R_1$=22 kΩ)", widths=[1.9, 2.4, 2.0, 2.0, 2.3, 2.7, 2.9], size=8.5)
    rows = [[n2(s[0] / 1e3, 3), n2(s[1], 3), n2(s[2], 3), n2(s[3], 3), n2(s[4], 3)] for s in R["sweep_rl"]]
    d.tab("sweeprl", ["$R_L$ (kΩ)", "Doyma sınırı (V)", "Kesim sınırı (V)", "Yük doğrusu $V_{O,pp}$", "SPICE $V_{O,pp}$"], rows, "$R_L$'nin salınıma etkisi", widths=[2.4, 2.8, 3.0, 3.6, 3.2], size=9)
    d.fig("sweep", R["fig_sweep"], "Salınım sınırları ve SPICE salınımı: bias akımına (sol) ve $R_2$'ye (sağ) göre.", 15.5)
    d.bullets([
        "**$R_2$ küçük (akım küçük):** Sınır **kesimdir** ($I_{EQ}R_E'$, akımla orantılı); yük doğrusu ile SPICE %4 içinde uyuşur.",
        "**$R_2\\approx39$ kΩ:** İki sınır eşit; yük doğrusu salınımı maksimum (%s V)." % n2(max(s[5] for s in R["sweep"]), 3),
        "**$R_2$ büyük (akım büyük, $V_{CEQ}$ küçük):** Yük doğrusu **azalma** öngörür (doyma sınırı). SPICE ise yaklaşık %s V pp'de bir **plato** gösterir: büyük sinyalde baz akımı tepeleri $C_{C1}$'i şarj eder ve ortalama baz gerilimini düşürür ($R_2=150$ kΩ, 4 V girişte ortalama baz gerilimi 10,1 V'tan 8,7 V'a iner); çalışma noktası kendiliğinden aralığın ortasına kayar. Bu **kuplaj kondansatörlü** devrelere özgüdür; el yük doğrusu Q noktasını sabit sayar." % n2(R["sweep"][-1][6], 3),
        "**$R_L$ büyütülürse** kesim sınırı ($I_{EQ}R_E'$) büyür, ta ki doyma sınırı devralana kadar.",
        "**Özet (parametreler):** (1) $R_1$, $R_2$ (Q noktası); (2) $R_E$ ve $R_L$ (AC yük doğrusunun eğimi); (3) $V_{CC}$ (üst sınır); (4) $V_{CE(sat)}$. Simülasyonda **$V_{CE}$ takibi** (ipucu): $V_{CE}$ tepelerde 0,2 V'a inerse doyma, $I_E\\to0$ olursa kesim başlamıştır; hangi taraf önce kırpılıyorsa Q noktası o yönün tersine kaydırılır.",
    ])
    d.h(1, "Programda Nasıl Yapılır?")
    d.bullets([
        "**Q noktası:** `.op`. **Frekans cevabı:** `.ac dec 50 10 100Meg` (kaynakta `AC 1`).",
        "**Geçici analiz:** kaynak `SINE(0 genlik 100k)`, ofset 0 V (föy). Kararlı hâle geçmeyi bekleyin: kuplaj kondansatörlerinin zaman sabitleri (örn. CC1 için $R_{in}C$) birkaç yüz mikrosaniyeye çıkabilir; bu yüzden grafiği simülasyonun **son periyotlarında** alın (LTspice'ta `.tran 0 2m 1.5m` gibi başlangıç ve bitiş zamanı verin).",
        "**THD:** LTspice'ta `.four 100k V(out)` ya da `FFT` ile; Micro-Cap'te Fourier analizi. Bu belgedeki sayılar 10 periyotluk FFT'den hesaplandı.",
        "**BC238A modeli:** kütüphanedekini kullanın; yoksa Ek A'daki `.model` satırını yapıştırın (β=170, $V_{BE}$=0,62 V@2 mA).",
    ])
    d.h(1, "Sık Sorulabilecek Sorular")
    qa = [
        ("Ortak emetör neden 'ortak emetör'?", "Emetör (AC'de) hem girişin hem çıkışın ortak ucudur: giriş bazdan, çıkış kolektörden alınır."),
        ("CE'siz devrede kazanç neden bu kadar küçük?", "$R_E$ AC'de baz–emetör sinyalinin büyük kısmını yutar (geri besleme): $A_V\\approx-R_L'/R_E$."),
        ("Neden CE'siz devrenin bozulması daha az?", "Geri besleme $v_{be}$'yi küçük tutar; BJT'nin eğri kısmı az kullanılır."),
        ("Emetör izleyicinin faydası ne?", "Yüksek giriş / düşük çıkış direnci: bir kaynağı yüksek yükten ayıran tampon."),
        ("Neden VO(pp) hesabında 0,2 V çıkarıyoruz?", "Doyma sınırı: $V_{CE}$ bunun altına inemez."),
        ("Bozulma ölçüsü nedir?", "THD: harmoniklerin temel bileşene oranı. Bu belgede ≤%1 kabul edildi."),
    ]
    for q, a in qa:
        d.p("**S:** " + q)
        d.p("**C:** " + a)
    return d
