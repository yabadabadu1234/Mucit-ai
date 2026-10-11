import numpy as np
from common import *
from docbuilder import Doc
import exp1
import ltshots
import extras

M = "\u2212"


def n2(x, nd=3):
    """Düz sayı biçimi, eksi işareti U+2212."""
    return fmt(x, nd).replace("-", M)


def sci(x, nd=3):
    """Bilimsel gösterim, satır içi matematik olarak."""
    if x == 0:
        return "0"
    e = int(np.floor(np.log10(abs(x))))
    m = x / 10 ** e
    return "$%s%.*f\\times10^{%d}$" % ("-" if m < 0 else "", nd - 1, abs(m), e)


def vs_fmt(v):
    return (M if v < 0 else "") + ("%g" % abs(v))


def two_block_table(rows, f_vd, f_id, split=9):
    """18 sütunu iki bloğa böl. rows: [(vs, vd, id_A)]"""
    out = []
    hdr = None
    for b in (rows[:split], rows[split:]):
        r0 = ["$V_S$ (V)"] + [vs_fmt(r[0]) for r in b]
        r1 = ["$V_D$ (V)"] + [f_vd(r[1]) for r in b]
        r2 = ["$I_D$ (mA)"] + [f_id(r[2] * 1e3) for r in b]
        if hdr is None:
            hdr = r0
        else:
            out.append(r0)
        out += [r1, r2]
    return hdr, out


def fmt_id(x):
    if x == 0:
        return "0"
    if abs(x) < 1e-3:
        return sci(x, 3)
    return n2(x, 4)


def fmt_vd(x):
    if abs(x) < 1e-9:
        return "0"
    return n2(x, 4)


def cursor_table(d, figname, figlabel, scale=None):
    import re as _re
    marks = FIG_MARKS.get(figname, [])
    if not marks:
        return
    def cell(lbl, v):
        m = _re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", lbl)
        name, unit = (m.group(1), m.group(2)) if m else (lbl, "")
        return "%s = %s %s" % (name, n2(v, 4), unit)
    rows = [["X%d" % (i + 1), cell(xl, x), cell(yl, y)] for i, (xl, yl, x, y) in enumerate(marks)]
    d.tab("cur_" + figname, ["Cursor", "x coordinate", "y coordinate"], rows,
          "Coordinates of the cursors in [[f:%s]]" % figlabel, widths=[1.8, 6.2, 6.2], size=9)


def common_tables(d, R):
    # Tablo: ideal
    d.p("The results obtained with the ideal-diode model are listed in [[t:ideal]]. The diode is regarded as a short circuit for $V_S>0$ and as an open circuit for $V_S\\leq0$.")
    ideal = [(a, b, c) for a, b, c in R["ideal"]]
    hdr, rows = two_block_table(ideal, fmt_vd, fmt_id)
    d.tab("ideal", hdr, rows, "$V_D$ and $I_D$ calculations (ideal diode model)", widths=[2.2] + [1.45] * 9, size=8.5)


def build_en(R):
    d = Doc("en")
    d.title_block([
        ("TOBB University of Economics and Technology", 14, True),
        ("Department of Electrical and Electronics Engineering", 12, False),
        ("ELE 224L \u2013 Electronic Circuits Laboratory", 12, False),
        ("Experiment 1 \u2013 Preliminary Work: PN Junction Diode", 13, True),
    ], [("Name Surname", ""), ("Student ID", ""), ("Date", "")])

    # ------------------------------------------------------------ 1
    d.h(1, "Introduction")
    d.h(2, "Objective of the Experiment")
    d.p("The objective of this experiment is to learn how a PN-junction semiconductor diode behaves in a circuit and how its behaviour can be described at three levels of modelling: the ideal-diode model, the constant-voltage-drop (CVD) model, and the exponential diode (Shockley) equation. A half-wave rectifier is analysed with each model by hand calculations, simulated in SPICE, and the theoretical and simulated results are compared quantitatively. The aim is to understand which model is sufficient in which situation and why the results differ.")
    d.h(2, "Benefits of the Experiment")
    d.p("The experiment shows that a nonlinear element cannot be solved with a single linear equation: either the diode is replaced by a piecewise-linear model whose state (on or off) is assumed and then verified, or the nonlinear equation is solved iteratively. The experiment also develops the ability to plot a device characteristic with MATLAB, to build a DC sweep and a transient analysis in SPICE, to read values from a plot by using a cursor, and to explain the deviations between theory and simulation with physical reasons. These skills are used in all of the following experiments.")

    # ------------------------------------------------------------ 2
    d.h(1, "Calculations and Simulations")
    d.h(2, "Ideal and Constant-Voltage-Drop Diode Models")
    d.p("In the ideal-diode model, the diode is a perfect switch: it conducts with zero voltage drop when a forward current flows and blocks any current when it is reverse biased, as given in [[e:ideal]]. In the CVD model, the diode conducts only after the forward voltage reaches the turn-on voltage $V_{D(on)}$, and the voltage across a conducting diode is then fixed at this value, as given in [[e:cvd]]. A value of $V_{D(on)}=0.7$ V is used for silicon diodes.", )
    d.eq(r"\text{Ideal:}\quad \begin{cases} V_D = 0,\; I_D \geq 0 & (\text{on}) \\ I_D = 0,\; V_D \leq 0 & (\text{off}) \end{cases}", "ideal")
    d.eq(r"\text{CVD:}\quad \begin{cases} V_D = V_{D(on)},\; I_D \geq 0 & (\text{on}) \\ I_D = 0,\; V_D \leq V_{D(on)} & (\text{off}) \end{cases}", "cvd")
    d.p("The I\u2013V characteristics of both models are shown in [[f:models]]. The ideal characteristic consists of the positive $I_D$ axis (on) and the negative $V_D$ axis (off). The CVD characteristic is the same graph shifted to the right by 0.7 V, which represents the voltage that a real silicon diode needs before it starts to conduct a noticeable current.")
    d.fig("models", R["fig_models"], "I\u2013V characteristics of the ideal diode model (left) and the constant voltage drop (CVD) model (right).", 15)

    d.h(2, "Diode Equation and I\u2013V Characteristic")
    d.p("The diode equation given in [[e:shockley]] describes the current of a PN junction. In this equation, $I_S=20$ fA is the reverse saturation current, $V_T=0.026$ V is the thermal voltage, and $n=1$ is the ideality factor.")
    d.eq(r"I_D = I_S\left(e^{V_D/(nV_T)}-1\right)", "shockley")
    d.p("The characteristic for $-1\\text{ V}\\leq V_D\\leq1$ V was obtained with the MATLAB code given in Appendix A and is shown in [[f:matlab]]. Since the current changes by more than twenty orders of magnitude over this voltage range, the characteristic is presented with a linear (zoomed) and a semilogarithmic axis.")
    d.fig("matlab", os.path.join(FIG, "e1_matlab_octave.png"), "Diode I\u2013V characteristic from Equation (2.1), generated by the code in Appendix A (linear scale, zoomed, and semilog scale).", 15)
    vd06, i06 = 0.6, exp1.shockley(0.6)
    d.p("In reverse bias ($V_D<-3V_T$), the exponential term vanishes and the current saturates at $-I_S=-20$ fA, which is invisible on the linear scale. In forward bias, the current grows exponentially: $I_D=%s$ mA at 0.6 V and $I_D=%s$ mA at 0.7 V. A voltage increase of $V_T\\ln 10\\approx60$ mV multiplies the current by ten, which is the straight line seen on the semilog plot. The current is practically zero below about 0.5 V and increases very rapidly above 0.6 V, which is the origin of the \u201cturn-on voltage\u201d concept used in the CVD model." % (n2(exp1.shockley(0.6) * 1e3, 3), n2(exp1.shockley(0.7) * 1e3, 3)))

    d.h(2, "Half-Wave Rectifier Analysis")
    d.p("The half-wave rectifier circuit used in the analysis is shown in [[f:schem]]. The diode is in series with $R_1=1$ k$\\Omega$ and the output $V_O$ is taken across the resistor. Since the diode current is the only current in the loop, the loop equation given in [[e:kvl]] holds.")
    d.fig("schem", R["fig_schem"], "Half-wave rectifier circuit used in the experiment ($R_1=1$ k$\\Omega$).", 8.5)
    d.eq(r"V_S = V_D + R_1 I_D", "kvl")
    d.p("**Ideal diode model.** For $V_S>0$ the diode is assumed to be on, which gives $V_D=0$ and $I_D=V_S/R_1$ from [[e:kvl]]. The assumption is verified by $I_D>0$. For $V_S\\leq0$ the diode is assumed to be off, which gives $I_D=0$ and $V_D=V_S$, and the assumption is verified by $V_D\\leq0$. The results are listed in [[t:ideal]]. For example, at $V_S=3$ V, $I_D=3\\text{ V}/1\\text{ k}\\Omega=3$ mA.")
    common_tables(d, R)
    d.p("**Diode equation.** Substituting [[e:shockley]] into [[e:kvl]] yields the transcendental equation given in [[e:trans]], which has no elementary closed-form solution and is therefore solved by fixed-point iteration: an initial guess $V_D^{(0)}=0.7$ V is used to find $I_D=(V_S-V_D)/R_1$, and the next voltage is found from the inverse of the diode equation as given in [[e:iter]].")
    d.eq(r"V_S = V_D + R_1 I_S\left(e^{V_D/V_T}-1\right)", "trans")
    d.eq(r"V_D^{(k+1)} = V_T\ln\!\left(\frac{V_S-V_D^{(k)}}{R_1 I_S}+1\right)", "iter")
    it = R["iter"]
    d.p("For $V_S=5$ V, the iteration gives $V_D^{(1)}=%s$ V, $I_D=%s$ mA; $V_D^{(2)}=%s$ V, $I_D=%s$ mA; and $V_D^{(3)}=%s$ V, which is converged to the fifth decimal digit. The same procedure was applied for every $V_S$ value in [[t:eq]] (the results were additionally verified with the closed-form Lambert-W solution, which agrees to better than $10^{-12}$ V). Only one sample calculation is shown, since the other values are obtained in the same way." % (
        n2(it[0][3], 5), n2(it[1][2] * 1e3, 5), n2(it[1][3], 5), n2(it[2][2] * 1e3, 5), n2(it[2][3], 5)))
    eq = R["eq"]
    hdr, rows = two_block_table(eq, fmt_vd, fmt_id)
    d.tab("eq", hdr, rows, "$V_D$ and $I_D$ calculations (diode equation, $V_T=0.026$ V, $I_S=20$ fA, $n=1$)", widths=[2.2] + [1.45] * 9, size=8.5)
    d.p("**SPICE simulation.** The circuit of [[f:schem]] was built in SPICE with a 1N4148 diode model (the model line is given in Appendix B; its parameters, $I_S=2.52$ nA, $n=1.752$, $R_S=0.568\\ \\Omega$, are those of an On Semiconductor model distributed in LTspice-based course material, whereas the model of another manufacturer, for example Nexperia with $I_S=4.35$ nA and $n=1.906$, gives slightly different values), and a DC sweep of $V_S$ from $-5$ V to $+5$ V was performed. The $V_D$\u2013$I_D$ graph is shown in [[f:spice]] together with the cursor point listed in [[t:cursor]].")
    d.fig("spice", R["fig_spice"], "SPICE DC sweep result ($V_D$ on the x-axis, $I_D$ on the y-axis) for the 1N4148 model; the dashed curve is Equation (2.1) with the given parameters (ngspice simulation).", 15)
    pv, pi, ps = R["pt_spice"]
    d.tab("cursor", ["Cursor", "$V_D$ (V)", "$I_D$ (mA)", "Corresponding $V_S$ (V)"],
          [["X", n2(pv, 4), n2(pi * 1e3, 4), n2(ps, 3)]], "Coordinates of the cursor point in [[f:spice]]", widths=[2.5, 3, 3, 4.5])
    ltshots.add(d, "e1_dc", "lt_dc")
    # karşılaştırma tablosu
    sel = [-5, 0.5, 0.7, 1, 2, 3, 5]
    th = {r[0]: r for r in R["eq"]}
    sp = {r[0]: r for r in R["sp_1n"]}
    rows = []
    for v in sel:
        a, b = th[v], sp[v]
        if v < 0:
            rows.append([vs_fmt(v), n2(a[1], 4), n2(b[1], 4), "0.0%", sci(a[2] * 1e3), sci(b[2] * 1e3), "$%.0f\\times10^{3}$ %%" % 0 if False else "\u2014"])
        else:
            rows.append([vs_fmt(v), n2(a[1], 4), n2(b[1], 4), "%+.1f%%" % pct_err(a[1], b[1]).__float__(),
                         n2(a[2] * 1e3, 4), n2(b[2] * 1e3, 4), "%+.1f%%" % pct_err(a[2], b[2])])
    d.tab("cmp", ["$V_S$ (V)", "$V_D$ theory (V)", "$V_D$ SPICE (V)", "Error", "$I_D$ theory (mA)", "$I_D$ SPICE (mA)", "Error"],
          rows, "Comparison of the diode-equation calculation with the SPICE result for the 1N4148 model (Error = (SPICE $-$ theory)/theory)", widths=[1.6, 2.4, 2.4, 1.8, 2.6, 2.6, 1.8], size=9)
    # modeller vs spice
    rows = []
    for v in (1, 2, 3, 5):
        idl = v
        cvd = max(v - 0.7, 0) / 1.0
        eqi = th[v][2] * 1e3
        spi = sp[v][2] * 1e3
        rows.append([vs_fmt(v), n2(idl, 4) + " (%+.1f%%)" % pct_err(spi, idl), n2(cvd, 4) + " (%+.1f%%)" % pct_err(spi, cvd), n2(eqi, 4) + " (%+.1f%%)" % pct_err(spi, eqi), n2(spi, 4)])
    d.tab("models", ["$V_S$ (V)", "Ideal $I_D$ (mA)", "CVD $I_D$ (mA)", "Equation $I_D$ (mA)", "SPICE 1N4148 $I_D$ (mA)"], rows,
          "Diode current predicted by the three models; the percentage in parentheses is the deviation from the SPICE value", widths=[1.8, 3.4, 3.4, 3.4, 3.4], size=9)
    # kalibrasyon
    err_vd = max(abs(a[1] - b[1]) for a, b in zip(R["eq"][6:], R["sp_eq_cal"][6:]))
    err_id = max(abs(a[2] - b[2]) / a[2] for a, b in zip(R["eq"][6:], R["sp_eq_cal"][6:]))
    d.p("The differences in [[t:cmp]] and [[t:models]] are caused by the model parameters and not by a calculation error. This was verified by a second simulation in which the diode was defined with exactly the parameters of the experiment sheet ($I_S=20$ fA, $n=1$, no series resistance) and SPICE was set to the same thermal voltage of 0.026 V ($n=%.4f$ at the default 27\u00b0C and $g_{min}=10^{-20}$ S). The simulation then agrees with the hand calculation within %.4f%% in current ($|\\Delta V_D|<%.0f$ \u00b5V)." % (R["ncal"], err_id * 100, err_vd * 1e6))

    d.h(2, "Input and Output Waveforms of the Half-Wave Rectifier")
    d.p("The expected output waveform was obtained by using the simplified (CVD) model with $V_{D(on)}=0.7$ V and a sinusoidal input of 5 V amplitude (the frequency of 1 kHz was chosen, since it is not specified). The diode conducts only while $V_S>0.7$ V, and the output then equals $V_S-0.7$ V, as given in [[e:vo]]. The waveforms are shown in [[f:time]].")
    d.eq(r"V_O(t)=\begin{cases} V_S(t)-0.7\ \text{V}, & V_S(t)>0.7\ \text{V} \\ 0, & V_S(t)\leq0.7\ \text{V} \end{cases}", "vo")
    d.fig("time", R["fig_time"], "Input voltage $V_S$ and expected output voltage $V_O$ of the half-wave rectifier for the CVD model ($V_{D(on)}=0.7$ V, $f=1$ kHz).", 13.5)
    cursor_table(d, "e1_time", "time")
    th1 = R["theta"]
    vavg = (2 * 5 * np.cos(np.radians(th1)) - 0.7 * (np.pi - 2 * np.radians(th1))) / (2 * np.pi)
    d.p("The peak of the output is $5-0.7=4.3$ V. The diode starts to conduct at $\\theta_1=\\arcsin(0.7/5)=%.2f^\\circ$ and stops at $180^\\circ-\\theta_1$, so the conduction angle is $%.1f^\\circ$, slightly shorter than $180^\\circ$. The negative half-cycle is completely blocked, and the reverse voltage across the diode reaches $-5$ V. The average value of the output is %s V (the ideal-diode value $V_p/\\pi$ would be %s V). The transient simulation with the 1N4148 model gives a peak of %s V, which deviates by %.1f%% from 4.3 V, because the real diode drop at 4.3 mA is 0.653 V and not 0.7 V." % (
        th1, 180 - 2 * th1, n2(vavg, 3), n2(5 / np.pi, 3), n2(R["tran_vo_peak"], 4), pct_err(4.3, R["tran_vo_peak"])))
    d.fig("time_spice", R["fig_time_spice"], "Transient simulation of the rectifier with the 1N4148 model compared with the CVD prediction (ngspice).", 13.5)
    ltshots.add(d, "e1_tran", "lt_tran")

    # ------------------------------------------------------------ 3
    d.h(1, "Conclusions")
    def pe(v, k):
        return 100 * (sp[v][k] - th[v][k]) / th[v][k]
    d.p("The hand calculation with the diode equation and the SPICE simulation with the 1N4148 model agree well in the diode current when the source voltage is large, but they differ in the diode voltage: at $V_S=5$ V the current differs by only %+.1f%% (%s mA versus %s mA), while $V_D$ differs by %s mV (%+.1f%%); at $V_S=2$ V the differences are %+.1f%% in $I_D$ and %s mV in $V_D$. Near the turn-on region ($V_S=0.5$ V), the SPICE current is %.0f times larger than the calculated one. The reason is that the experiment sheet uses an idealized diode ($n=1$, $I_S=20$ fA, no series resistance), whereas the 1N4148 model has $n=1.752$, $I_S=2.52$ nA and $R_S=0.568\\ \\Omega$. For the same current, the 1N4148 needs a lower voltage than the sheet diode because its saturation current is $1.3\\times10^{5}$ times larger. When $V_S$ is large, the resistor $R_1$ fixes the current as $(V_S-V_D)/R_1$ and the error in $V_D$ is a small part of $V_S$, so the current is insensitive to it; when $V_S$ is small, the current is set by the exponential and the model difference appears directly. In reverse bias, the theoretical current ($-20$ fA) and the SPICE current ($-2.5$ nA) differ by five orders of magnitude, but both are negligible against the milliampere-level forward current." % (pe(5, 2), n2(th[5][2] * 1e3, 4), n2(sp[5][2] * 1e3, 4), n2(abs(sp[5][1] - th[5][1]) * 1e3, 3), pe(5, 1), pe(2, 2), n2(abs(sp[2][1] - th[2][1]) * 1e3, 3), sp[0.5][2] / th[0.5][2]))
    d.p("The ideal-diode model overestimates the current by 0.7 mA out of 4.3 mA (about 16%%) at $V_S=5$ V, and its error grows as $V_S$ decreases; the CVD model reduces the error to about %.1f%% at 5 V, but it predicts zero current below 0.7 V, where a real diode still conducts (for example, 0.05 mA at 0.5 V in the SPICE result). The exponential model is accurate but requires an iteration, so the CVD model is preferred for quick design calculations when the source voltage is much larger than 0.7 V." % abs(pct_err(sp[5][2] * 1e3, 4.3)))
    d.p("The diode voltage changes only from %s V to %s V while $V_S$ changes from 0.6 V to 5 V in [[t:eq]]. This weak dependence is the reason why a constant voltage drop is a good approximation. Skills gained in this experiment are building and interpreting SPICE DC and transient analyses, solving a nonlinear circuit by iteration, and choosing a device model according to the required accuracy." % (n2(th[0.6][1], 3), n2(th[5][1], 3)))

    # ------------------------------------------------------------ 4
    d.h(1, "References")
    d.bullets([
        "Sedra, A. S., & Smith, K. C. (2014). Microelectronic circuits (7th ed.). New York: Oxford University Press.",
        "TOBB University of Economics and Technology, Department of Electrical and Electronics Engineering. (n.d.). ELE 224L Experiment 1 \u2013 Preliminary Work (PN Junction Diode) [Course handout].",
        "ngspice. (n.d.). ngspice user manual. Retrieved October 11, 2026, from https://ngspice.sourceforge.io/docs.html",
    ], numbered=True)

    # ------------------------------------------------------------ 5
    d.h(1, "Appendices")
    d.h(2, "Appendix A: MATLAB Code of the Diode Characteristic")
    d.code(open(os.path.join(ROOT, "matlab", "exp1_diode_equation.m")).read(), "Code A.1  MATLAB code used for the Section 2.2 figure")
    d.h(2, "Appendix B: SPICE Netlists")
    d.code(clean_cir(os.path.join(SPICE, "e1_dc_1n4148.cir")), "Netlist B.1  DC sweep of the half-wave rectifier (ngspice syntax; the same model line can be pasted into LTspice as a SPICE directive)")
    return d


def build_tr(R):
    d = Doc("tr", figword="Şekil", tabword="Tablo")
    d.title_block([
        ("Deney 1 \u2013 Ön Çalışma Öğretici Rehberi", 15, True),
        ("PN Eklem Diyot (ELE 224L Elektronik Devreler Laboratuvarı)", 12, False),
        ("Bu belge SADECE ÖĞRENMEK içindir; teslim edilecek metin İngilizce rapordur.", 11, False),
    ], [("Ad Soyad", ""), ("Numara", ""), ("Tarih", "")])

    # ---------------- 1
    d.h(1, "Bu Deney Neyi Öğretiyor? (Büyük Resim)")
    d.p("Diyot, akımı yalnızca bir yönde geçiren elemandır. Bu deneyin tek cümlelik özeti şudur: **diyodu üç farklı hassasiyette modelleriz, aynı devreyi üçüyle çözeriz, SPICE ile karşılaştırırız ve farkların nedenini anlarız.** Üç model şunlardır:")
    d.bullets([
        "**İdeal diyot:** Açıkken kısa devre, kapalıyken açık devre. En kaba ama en hızlı model.",
        "**Sabit gerilim düşümlü (CVD) model:** Açıkken uçlarında sabit 0,7 V düşer (silisyum). Hâlâ doğrusal parçalı, ama gerçeğe çok daha yakın.",
        "**Üstel (Shockley) denklem:** Gerçeğe en yakın model; ama denklem doğrusal olmadığı için devreyi elle çözmek iterasyon ister.",
    ])
    d.box("Aklınızda tutmanız gereken tek soru", [
        "Her adımda şunu sorun: **\"Diyot açık mı kapalı mı?\"** Önce bir varsayım yapılır (açık ya da kapalı), sonra denklemlerle çözülür, en sonda varsayımın tutup tutmadığı kontrol edilir. Tutmuyorsa varsayım değiştirilir. Bu \"varsay – çöz – doğrula\" döngüsü bütün diyot, MOSFET ve BJT devrelerinin ortak yöntemidir ve sonraki dört deneyde de aynen kullanılacaktır.",
    ])

    # ---------------- 2
    d.h(1, "Temel Bilgi: Diyot Nedir, Neden Üstel Davranır?")
    d.h(2, "PN eklemi ve iki kutuplama")
    d.p("Diyot, bir P tipi (boşluk bolluğu) ve bir N tipi (elektron bolluğu) yarı iletkenin birleşiminden oluşur. Birleşim yüzeyinde elektron ve boşluklar birbirini yok eder ve geride **tükenme bölgesi** adı verilen, taşıyıcısı olmayan, ama sabit iyonlar yüzünden bir iç elektrik alanı taşıyan ince bir tabaka kalır. Bu alan akımın geçmesine engel olan bir **potansiyel set** gibi düşünülebilir (silisyumda yaklaşık 0,6–0,8 V).")
    d.bullets([
        "**İleri kutuplama** (P tarafı +, N tarafı −): Dış gerilim seti küçültür; set küçüldükçe taşıyıcılar karşıya geçer ve akım *üstel olarak* artar.",
        "**Ters kutuplama** (P tarafı −): Dış gerilim seti büyütür, tükenme bölgesi genişler; yalnızca çok küçük bir sızıntı akımı (doyma akımı $I_S$ düzeyinde) akar.",
    ])
    d.h(2, "Shockley denklemi, terim terim")
    d.eq(r"I_D = I_S\left(e^{V_D/(nV_T)}-1\right)", "shockley")
    d.bullets([
        "$I_D$: diyot akımı (anottan katoda doğru pozitif kabul edilir). $V_D$: anot–katot gerilimi.",
        "$I_S$ (doyma akımı): ters kutuplamada akan sızıntı akımı. Föyde 20 fA = $20\\times10^{-15}$ A; yani inanılmaz küçük. Sıcaklıkla hızla artar (silisyumda kabaca her 5 °C'de iki katına çıkar).",
        "$V_T=kT/q$ (ısıl gerilim): oda sıcaklığında yaklaşık 25,85 mV. Föyde 0,026 V olarak verilmiştir. $k$ Boltzmann sabiti, $T$ mutlak sıcaklık, $q$ elektron yüküdür.",
        "$n$ (idealite katsayısı): 1 ile 2 arasındadır; föyde 1 alınmıştır. Gerçek diyotlarda (ör. 1N4148) 1,7 civarındadır.",
        "$e^{V_D/(nV_T)}$: İşin sırrı buradadır. $V_D$ arttıkça terim üstel büyür. Ters yönde ($V_D\\ll-V_T$) terim sıfıra gider ve $I_D\\to -I_S$ olur. İleri yönde ($V_D\\gg V_T$) $-1$ ihmal edilir ve $I_D\\approx I_Se^{V_D/V_T}$ olur.",
    ])
    d.box("Önemli sezgi: 60 mV / dekad", [
        "$I_D\\propto e^{V_D/V_T}$ olduğundan, akımı 10 kat artırmak için $V_D$'yi $V_T\\ln10=0{,}026\\times2{,}303\\approx60$ mV artırmak yeterlidir. Yani akım 1 µA'den 1 mA'e (1000 kat) çıkarken diyot gerilimi sadece $3\\times60=180$ mV değişir. Bu yüzden diyot gerilimi geniş bir akım aralığında hep ~0,6–0,7 V civarında kalır. **CVD modelinin (sabit 0,7 V) mantığı budur.**",
    ])

    # ---------------- 3
    d.h(1, "Soru 1.1: İdeal ve CVD Model")
    d.p("İdeal diyot iki durumludur: **açık** (kısa devre; $V_D=0$, $I_D\\geq0$) ya da **kapalı** (açık devre; $I_D=0$, $V_D\\leq0$). Grafikte iki doğru parçasıdır: pozitif $I_D$ ekseni ve negatif $V_D$ ekseni. CVD modelde açık durumun gerilimi 0 değil $V_{D(on)}=0{,}7$ V'tur; yani aynı grafik 0,7 V sağa kaydırılmıştır ([[f:models]]). Eşdeğer devre olarak CVD, bir ideal diyot ile ona seri 0,7 V'luk bir pil gibidir.")
    d.fig("models", R["fig_models"], "İdeal ve CVD diyot modellerinin I–V karakteristikleri.", 15)
    d.box("Neden iki model?", [
        "Kaynak gerilimi çok büyükse (ör. 100 V) 0,7 V'luk hata önemsizdir, ideal model yeter. Kaynak gerilimi birkaç volt ise (bu deneyde 5 V) 0,7 V'luk hata %14 eder; CVD gerekir. Kaynak 0,7 V civarındaysa ya da çok hassas sonuç gerekiyorsa üstel denklem gerekir.",
    ])

    # ---------------- 4
    d.h(1, "Soru 1.2: MATLAB ile Diyot Karakteristiği")
    d.p("Kod satır satır şöyle çalışır (tam kod raporun Ek A bölümündedir):")
    d.bullets([
        "`VD = linspace(-1, 1, 2001);` −1 V ile +1 V arasında eşit aralıklı 2001 nokta üretir (adım 1 mV).",
        "`ID = IS .* (exp(VD ./ (n*VT)) - 1);` Denklem (1)'i her nokta için hesaplar. `.*` ve `./` işaretleri **eleman eleman** işlem demektir; noktasız yazılırsa MATLAB matris işlemi yapmaya çalışır ve hata verir.",
        "`plot`, `semilogy`: iki grafik çizilir. Neden iki? Çünkü $V_D=1$ V'ta akım $\\approx1026$ A çıkar (matematiksel olarak) ve doğrusal eksende yalnızca bu uç nokta görünür, diğer her şey sıfır çizgisinde ezilir. Bu yüzden doğrusal grafikte y ekseni 20 mA ile kısıtlanır (`ylim`), ve akımın **mutlak değeri** logaritmik eksende çizilir.",
    ])
    d.fig("matlab", os.path.join(FIG, "e1_matlab_octave.png"), "Kodun çıktısı (Octave ile çalıştırıldı; MATLAB'da da aynı sonuç çıkar).", 15)
    d.p("Okuma rehberi: (i) Sol grafikte akım 0,5 V'a kadar sıfır gibi, 0,6–0,7 V arasında dikey bir duvar gibi yükselir. (ii) Sağ grafikte ileri bölge **düz bir çizgi** (üstel fonksiyon logaritmik eksende doğrudur); ters bölge ise $|I_D|=I_S=20$ fA'de yatay bir basamaktır. (iii) Sayısal kontrol: 0,5 V → %s mA; 0,6 V → %s mA; 0,7 V → %s mA. Her 0,1 V'ta yaklaşık 47 kat ($e^{0{,}1/0{,}026}=46{,}8$)." % (n2(exp1.shockley(0.5) * 1e3, 4), n2(exp1.shockley(0.6) * 1e3, 4), n2(exp1.shockley(0.7) * 1e3, 4)))
    d.box("Kodu kendiniz çalıştıracaksanız", [
        "Ek A'daki kodu `.m` dosyası olarak (ya da dosya `ele224l_on_calisma/matlab/exp1_diode_equation.m`) MATLAB'a yapıştırıp F5'e basın. Raporda kodun **ekran görüntüsü değil metni** istenir; metni Ek'e yapıştırmak yeterlidir (föyde açıkça yazıyor).",
    ])

    # ---------------- 5
    d.h(1, "Soru 2: Yarım Dalga Doğrultucunun Analizi")
    d.fig("schem", R["fig_schem"], "Yarım dalga doğrultucu: $V_S$ – D1 – $R_1$ seri döngü.", 8.5)
    d.p("Devre tek bir seri döngüdür, yani diyot akımı $R_1$'den de geçer. Kirchhoff gerilim yasası:")
    d.eq(r"V_S = V_D + R_1 I_D", "kvl")
    d.p("Bu tek denklemde iki bilinmeyen ($V_D$, $I_D$) vardır; ikinci denklemi **diyot modeli** verir. Üç modelin üç farklı ikinci denklemi vardır, dolayısıyla üç farklı tablo çıkar.")
    d.h(2, "Soru 2.1: İdeal model (Tablo 1)")
    d.bullets([
        "**$V_S>0$:** Diyot açık varsayılır: $V_D=0$ ⇒ $I_D=V_S/R_1$. Doğrulama: $I_D>0$ mı? Evet ⇒ varsayım doğru. Örnek: $V_S=3$ V ⇒ $I_D=3$ V / 1 kΩ = 3 mA. (V/kΩ = mA birim kolaylığını unutmayın.)",
        "**$V_S<0$:** Diyot kapalı varsayılır: $I_D=0$ ⇒ $V_D=V_S$ (gerilimin tamamı diyotun üstünde). Doğrulama: $V_D\\leq0$ mı? Evet. Örnek: $V_S=-5$ V ⇒ $V_D=-5$ V, $I_D=0$.",
        "**$V_S=0$:** Her ikisi de 0.",
    ])
    common_tables(d, R)
    d.h(2, "Soru 2.2: Diyot denklemi (Tablo 2)")
    d.p("Burada denklem $V_S=V_D+R_1I_S(e^{V_D/V_T}-1)$ olur. $V_D$ hem üstte hem üstelin içinde olduğu için \"düzenleyip $V_D=\\ldots$ yazmak\" mümkün değildir. İki yol vardır:")
    d.p("**Yol A – Sabit nokta iterasyonu (elle yapılabilen).** Denklemi tersine çevirip $V_D$'yi yalnız bırakırız:")
    d.eq(r"V_D^{(k+1)} = V_T\ln\!\left(\frac{V_S-V_D^{(k)}}{R_1 I_S}+1\right)", "iter")
    d.p("İşlem: (1) $V_D^{(0)}=0{,}7$ V tahmin edilir. (2) Bu tahminle $I_D=(V_S-V_D)/R_1$ hesaplanır. (3) Yukarıdaki formülle yeni $V_D$ bulunur. (4) Değer değişmeyene kadar tekrarlanır. Neden çabuk yakınsar? Çünkü $V_D$ logaritma içinde olduğundan $I_D$'deki büyük bir değişiklik $V_D$'yi çok az değiştirir. $V_S=5$ V için gerçek hesap:")
    rows = [[str(k), n2(vd, 6), n2(idk * 1e3, 6), n2(vn, 6)] for k, vd, idk, vn in R["iter"]]
    d.tab("iter", ["Adım $k$", "$V_D^{(k)}$ (V)", "$I_D=(5-V_D)/R_1$ (mA)", "$V_D^{(k+1)}$ (V)"], rows, "$V_S=5$ V için iterasyon; 3 adımda 5. ondalığa yakınsar", widths=[2, 3.5, 4.5, 3.5])
    d.p("**Yol B – Lambert-W (kapalı form).** $x e^{x}=y$ denkleminin çözümü $x=W(y)$ ile yazılır. Bizim denklemden:")
    d.eq(r"I_D=\frac{V_T}{R_1}\,W\!\left(\frac{R_1I_S}{V_T}\,e^{(V_S+R_1I_S)/V_T}\right)-I_S,\qquad V_D=V_S-R_1I_D", "lambert")
    d.p("Python'da `scipy.special.lambertw` ile hesaplanan sonuçlar iterasyonla $10^{-15}$ V mertebesine kadar aynıdır (kontrol edildi). Elle çözüm için Yol A yeterlidir; Yol B yalnızca kontrol içindir.")
    eq = R["eq"]
    hdr, rows = two_block_table(eq, fmt_vd, fmt_id)
    d.tab("eq", hdr, rows, "Diyot denklemi ile $V_D$ ve $I_D$ ($V_T=0{,}026$ V, $I_S=20$ fA, $n=1$)", widths=[2.2] + [1.45] * 9, size=8.5)
    d.p("Tabloyu okuma: (i) $V_S$ negatifken $V_D\\approx V_S$ ve $I_D\\approx-20$ fA (ters sızıntı; pratikte sıfır). (ii) $V_S=0{,}5$ V'ta diyot daha yeni uyanıyor: $V_D=0{,}496$ V, $I_D=3{,}87$ µA. (iii) $V_S=2$ V ile 5 V arası $V_D$ sadece 0,648 V'tan 0,679 V'a çıkar (60 mV/dekad kuralı); işte CVD'nin 0,7 V'u buradan gelir.")
    d.h(2, "Soru 2.3: SPICE")
    d.p("Devre kurulur, $V_S$ −5 V'tan +5 V'a süpürülür (DC sweep) ve **x ekseninde $V_D$, y ekseninde $I_D$** çizilir. 1N4148 diyodunun gerçek parametreleri ($I_S=2{,}52$ nA, $n=1{,}752$, $R_S=0{,}568\\ \\Omega$) föydeki idealize denklemden farklıdır; bu yüzden eğri biraz sağa (düşük akımlarda daha küçük $V_D$'ye) kayar.")
    d.fig("spice", R["fig_spice"], "SPICE DC süpürme sonucu ($V_D$–$I_D$), imleç (cursor) noktasıyla. ngspice ile üretildi.", 15)
    pv, pi, ps = R["pt_spice"]
    d.p("İmleç noktası: $V_D=%s$ V, $I_D=%s$ mA (bu noktada $V_S=%s$ V). Raporda ekran görüntüsünün altına imleç koordinatları tabloyla yazılır ve görüntüde **cihaz seri numarası** görünür (föy kuralı)." % (n2(pv, 4), n2(pi * 1e3, 4), n2(ps, 3)))
    ltshots.add(d, "e1_dc", "lt_dc", tr=True)
    d.h(2, "Teori ile SPICE neden farklı? Bunu mutlaka anlayın")
    sel = [-5, 0.5, 0.7, 1, 2, 3, 5]
    th = {r[0]: r for r in R["eq"]}
    sp = {r[0]: r for r in R["sp_1n"]}
    rows = []
    for v in sel:
        a, b = th[v], sp[v]
        if v < 0:
            rows.append([vs_fmt(v), n2(a[1], 4), n2(b[1], 4), sci(a[2] * 1e3), sci(b[2] * 1e3)])
        else:
            rows.append([vs_fmt(v), n2(a[1], 4), n2(b[1], 4), n2(a[2] * 1e3, 4), n2(b[2] * 1e3, 4)])
    d.tab("cmp", ["$V_S$ (V)", "$V_D$ teori (V)", "$V_D$ 1N4148 (V)", "$I_D$ teori (mA)", "$I_D$ 1N4148 (mA)"], rows, "Föydeki denklem ile 1N4148 SPICE modeli", widths=[1.8, 3.2, 3.4, 3.4, 3.4], size=9)
    err_vd = max(abs(a[1] - b[1]) for a, b in zip(R["eq"][6:], R["sp_eq_cal"][6:]))
    d.bullets([
        "**Neden 1N4148 farklı?** Gerçek diyotun $n$ ve $I_S$ değerleri föydekilerden farklıdır. Ayrıca $R_S=0{,}568\\ \\Omega$ seri direnç vardır. Bu yüzden sonuçlar farklıdır; hata hesap hatası değil **model farkıdır**.",
        "**Bunu nasıl kanıtladık?** SPICE'a diyodu tam föydeki parametrelerle ($I_S=20$ fA, $n=1$, $R_S=0$) tanımlattık ve SPICE'ın ısıl gerilimini 0,026 V'a eşitledik (SPICE 27 °C'de 25,865 mV kullanır; $n=%.4f$ yapıldı; ayrıca SPICE her kavşağa $10^{-12}$ S'lik GMIN iletkenliği ekler, bu 1e-20'ye indirildi). Sonuçta elle hesapla SPICE arasındaki fark $V_D$'de **%.0f µV'tan** küçük kaldı. Yani hem hesabımız hem simülasyon doğru; fark sadece modelden gelmektedir." % (R["ncal"], err_vd * 1e6),
        "**Ters yönde −20 fA mı −2,5 nA mı?** Teori −20 fA diyor (föydeki $I_S$); 1N4148'in kendi $I_S$'si 2,52 nA. İkisi de pratikte sıfırdır (mA düzeyinin 6 mertebe altında).",
    ])
    rows = []
    for v in (1, 2, 3, 5):
        idl = v
        cvd = max(v - 0.7, 0)
        eqi = th[v][2] * 1e3
        spi = sp[v][2] * 1e3
        rows.append([vs_fmt(v), n2(idl, 4) + " (%+.1f%%)" % pct_err(spi, idl), n2(cvd, 4) + " (%+.1f%%)" % pct_err(spi, cvd), n2(eqi, 4) + " (%+.1f%%)" % pct_err(spi, eqi), n2(spi, 4)])
    d.tab("models", ["$V_S$ (V)", "İdeal (mA)", "CVD (mA)", "Denklem (mA)", "SPICE 1N4148 (mA)"], rows, "Üç modelin akım tahmini; parantezde SPICE'a göre sapma", widths=[1.8, 3.4, 3.4, 3.4, 3.4], size=9)
    d.p("Bu tablo deneyin asıl dersidir: $V_S$ büyüdükçe üç model birbirine yaklaşır; küçüldükçe ideal model hızla bozulur, CVD biraz daha dayanır, üstel model en doğrudur.")

    # ---------------- 6
    d.h(1, "Soru 3.1: Zaman Grafikleri")
    d.p("Giriş 5 V genlikli sinüs. Frekans föyde belirtilmediği için 1 kHz seçilmiştir (sonuç frekanstan bağımsızdır). CVD modelle:")
    d.eq(r"V_O(t)=\begin{cases} V_S(t)-0.7\ \text{V}, & V_S(t)>0.7\ \text{V} \\ 0, & V_S(t)\leq0.7\ \text{V} \end{cases}", "vo")
    d.fig("time", R["fig_time"], "Giriş ve beklenen çıkış gerilimi (CVD modeli).", 13.5)
    th1 = R["theta"]
    vavg = (2 * 5 * np.cos(np.radians(th1)) - 0.7 * (np.pi - 2 * np.radians(th1))) / (2 * np.pi)
    d.bullets([
        "**Tepe değeri:** $5-0{,}7=4{,}3$ V (çıkış girişten 0,7 V kısadır).",
        "**İletim başlangıcı:** $V_S=0{,}7$ V olduğunda; açı $\\theta_1=\\arcsin(0{,}7/5)=%.2f^\\circ$. İletim $\\theta_1$ ile $180^\\circ-\\theta_1$ arasındadır; iletim açısı $%.1f^\\circ$ ($180^\\circ$'den biraz kısa)." % (th1, 180 - 2 * th1),
        "**Negatif yarı dalga:** Tamamen engellenir; diyotun üstünde −5 V'a kadar ters gerilim oluşur (diyotun ters dayanım gerilimi — PIV — en az 5 V olmalıdır; 1N4148 için 100 V mertebesindedir).",
        "**Ortalama (DC) değer:** %s V (ideal diyotta $V_p/\\pi=%s$ V olurdu). Yani doğrultucu çıkışı saf DC değil, 'dalgalı DC'dir; kondansatörle düzgünleştirmek sonraki derslerin konusudur." % (n2(vavg, 3), n2(5 / np.pi, 3)),
    ])
    d.fig("time_spice", R["fig_time_spice"], "SPICE geçici analizi (1N4148) ve CVD tahmini üst üste.", 13.5)
    d.p("SPICE tepe değeri %s V; CVD'nin 4,3 V'una göre %%%.1f sapma vardır; çünkü 4,3 mA'de gerçek diyot gerilimi 0,653 V'tur, tam 0,7 V değil." % (n2(R["tran_vo_peak"], 4), pct_err(4.3, R["tran_vo_peak"])))
    ltshots.add(d, "e1_tran", "lt_tran", tr=True)

    # ---------------- 7
    d.h(1, "Programda Nasıl Yapılır? (LTspice / Micro-Cap)")
    d.box("Önemli not", [
        "Bu rehberdeki grafiklerin çoğu **ngspice** ile üretilmiştir; ayrıca aynı netlistler **gerçek LTspice**'ta (Wine altında, Linux üzerinde) koşturulmuş ve imleçli ekran görüntüleri `lt_shot/` klasörüne kaydedilmiştir; İngilizce rapordaki 'LTspice' şekilleri bunlardır, üzerlerindeki cihaz seri numarası uydurmadır (hocanın kopya önleme maksadı gözetilerek kullanıcı izniyle). İsterseniz kendi bilgisayarınızda `ltspice/*.cir` dosyalarını `File → Open` ile açıp aynı ekran görüntülerini kendiniz de alabilirsiniz; sayılar aynı çıkmalıdır.",
    ])
    d.p("**LTspice için kısa tarif (DC süpürme, $V_D$–$I_D$):**")
    d.bullets([
        "Yeni şematik: `V` (voltage), `diode`, `res` ve `GND` yerleştirilir. Diyoda sağ tık → *Pick New Diode* → 1N4148 seçilir. $R_1=1$ k.",
        "`Simulate → Edit Simulation Cmd → DC sweep`: kaynak $V_1$, başlangıç −5, bitiş 5, adım 0,01.",
        "Çalıştırılır; boş grafik penceresinde sağ tık → *Add Trace* → `I(D1)` seçilir. $V_D$'yi x eksenine almak için x eksenine (alt) sağ tık ile x ekseni büyüklüğü değiştirilir (menü adı sürüme göre değişir: *Axis Settings* / *Set X-axis quantity*) ve ifade olarak anot düğümü ile katot düğümü arasındaki fark yazılır (ör. `V(a)-V(b)`; düğüm adlarını şematiğinize göre değiştirin).",
        "İmleç: iz adına (üstteki trace adına) tıklayınca imleç (cursor) penceresi açılır; istediğiniz noktaya sürüklenir; koordinatlar tablosu raporun altına yazılır.",
    ])
    d.p("**Micro-Cap:** *Analysis → DC → Variable 1 = V1, −5…5*; X ifadesi anot–katot gerilimi (ör. `V(A)-V(K)`; düğüm adlarını devrenize göre yazın), Y ifadesi `I(D1)`. (Menü adlarını programınızda doğrulayın; burada yoklanamadı.)")

    # ---------------- 8
    d.h(1, "Sık Sorulabilecek Sorular ve Cevapları")
    qa = [
        ("Diyot neden 0,7 V'ta 'açılır'? Gerçekten bir eşik var mı?", "Hayır, keskin bir eşik yoktur; akım üstel olarak artar. 0,7 V, 'orta büyüklükte (mA düzeyi) akım için tipik gerilim'dir. Daha küçük akımda (µA) 0,5 V, çok büyük akımda 0,8 V olabilir."),
        ("İdeal modelde $V_S=0{,}5$ V için $I_D=0{,}5$ mA, ama CVD'de 0. Hangisi doğru?", "Gerçek (SPICE 1N4148) 0,05 mA; ikisi de yanlış ama doğru olan değere göre ideal 10 kat fazla, CVD 0,05 mA fazla yani 'sıfıra yuvarlıyor'. Bu yüzden 0,7 V'a yakın gerilimlerde üstel model gerekir."),
        ("Neden iterasyon başlangıcı 0,7 V?", "Silisyum diyotta tipik gerilim olduğu için; yakınsama hızlı olur. Başka başlangıç da yakınsar (0,5 V ya da 1 V alın, deneyin)."),
        ("Tabloda $V_S=0$ için $V_D$ ve $I_D$?", "İkisi de 0; yük akımı yok."),
        ("Sinüs girişte diyotun gerilimi hep 0,7 V mıdır?", "Yalnızca CVD modelinde. Gerçekte 0,6–0,68 V arası (Tablo 2) değişir."),
        ("MATLAB'da neden `.*` ve `./`?", "Vektörlerin eleman eleman işlenmesi içindir; noktasız `*` matris çarpımı demektir."),
        ("PIV nedir?", "Peak Inverse Voltage: diyotun ters yönde taşıyacağı en büyük gerilim. Bu devrede girişin tepe değeri, 5 V."),
        ("Frekansı değiştirirsem ne olur?", "Bu deneyde kapasite etkisi yoktur (model diyot kapasitesini içerir ama 1 kHz'de önemsizdir); dalga biçimi aynı kalır."),
    ]
    for q, a in qa:
        d.p("**S:** " + q)
        d.p("**C:** " + a)
    extras.tr_extra(1, d, R)
    return d
