import subprocess, tempfile, os, re, itertools, json
def sim(body, probes):
    net = "* c\n" + body + "\n.control\nset numdgt=12\nop\n" + "".join("print %s\n" % p for p in probes) + ".endc\n.end\n"
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "n.cir"); open(f, "w").write(net)
        o = subprocess.run(["ngspice", "-b", f], capture_output=True, text=True).stdout
    r = {}
    for p in probes:
        m = re.search(r"^%s\s*=\s*(\S+)" % re.escape(p), o, re.M | re.I)
        assert m, (p, o[-400:])
        r[p] = float(m.group(1))
    return r
def par(*r): return 1 / sum(1 / x for x in r)
def eq_sim(kind, rs):
    if kind == "s":
        n = "V1 1 0 DC 1\n"; nodes = ["1"] + ["m%d" % i for i in range(1, len(rs))] + ["0"]
    else:
        n = "V1 1 0 DC 1\n"; nodes = None
    if kind == "s":
        for i, r in enumerate(rs): n += "R%d %s %s %g\n" % (i, nodes[i], nodes[i + 1], r)
    else:
        for i, r in enumerate(rs): n += "R%d 1 0 %g\n" % (i, r)
    i = sim(n, ["i(v1)"])["i(v1)"]
    return -1 / i
def div(R, rm):
    n = "VS 1 0 DC 15\nR1 1 2 %g\nR2 2 0 %g\n" % (R, R) + ("Rm 2 0 %g\n" % rm if rm else "")
    return sim(n, ["v(2)"])["v(2)"]
def bridge(r1, r2, r3, rx, vs=15):
    n = "VS 1 0 DC %g\nR1 1 2 %.12g\nR2 1 3 %.12g\nR3 2 0 %.12g\nRx 3 0 %.12g\n" % (vs, r1, r2, r3, rx)
    r = sim(n, ["v(2)", "v(3)"]); return r["v(2)"], r["v(3)"]
def dac(bits, tol=None, v=16):
    t = tol or [1] * 7
    n = "".join("V%d a%d 0 DC %g\n" % (k + 1, k + 1, v * bits[k]) for k in range(3))
    n += "Rg1 a1 n1 %g\nRg2 a2 n2 %g\nRg3 a3 n3 %g\nRl1 n1 n2 %g\nRl2 n2 n3 %g\nRt n3 0 %g\nRL n1 0 %g\n" % tuple(
        x * y for x, y in zip((2000, 2000, 2000, 1000, 1000, 2000, 1000), t))
    r = sim(n, ["v(n1)", "v(n2)", "v(n3)", "i(v1)", "i(v2)", "i(v3)"])
    return r["v(n1)"], r["v(n2)"], r["v(n3)"], -(r["i(v1)"] + r["i(v2)"] + r["i(v3)"])
if __name__ == "__main__":
    out = {}
    out["eq"] = {k: (v, eq_sim(*k_)) for k, v, k_ in [
        ("s123", 13100, ("s", [3900, 1000, 8200])), ("p123", 1 / (1/3900+1/1000+1/8200), ("p", [3900, 1000, 8200])),
        ("s12", 4900, ("s", [3900, 1000])), ("s13", 12100, ("s", [3900, 8200])), ("s23", 9200, ("s", [1000, 8200])),
        ("p12", par(3900, 1000), ("p", [3900, 1000])), ("p13", par(3900, 8200), ("p", [3900, 8200])), ("p23", par(1000, 8200), ("p", [1000, 8200]))]}
    out["div"] = {R: (div(R, 0), div(R, 1e7)) for R in (470, 1e5, 1e7)}
    out["br"] = {rx: bridge(470, 470, 1000, rx) for rx in (100, 220, 470, 680, 820, 1000, 1200, 1500, 2200, 4700, 10000)}
    vb = []
    for c in itertools.product((0.95, 1.05), repeat=4):
        a, b = bridge(470 * c[0], 470 * c[1], 1000 * c[2], 1000 * c[3]); vb.append(a - b)
    out["br_tol"] = (min(vb), max(vb))
    out["dac"] = {}
    for d in range(10):
        code = 7 if d in (0, 8, 9) else d
        bits = [(code >> 2) & 1, (code >> 1) & 1, code & 1]
        out["dac"][d] = (code, dac(bits))
    vo = []
    for c in itertools.product((0.95, 1.05), repeat=7):
        vo.append(dac([1, 1, 1], list(c))[0])
    out["dac_tol"] = (min(vo), max(vo))
    json.dump(out, open("../build/calc.json", "w"), indent=1)
    print(json.dumps(out)[:1500])
