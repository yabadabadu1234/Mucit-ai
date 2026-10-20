import os, json, math
H = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(H, "..", "assets"); SH = os.path.join(H, "..", "shots"); OUT = os.path.join(H, "..", "out"); os.makedirs(OUT, exist_ok=True)
a = lambda n: os.path.join(A, n)
s = lambda n: os.path.join(SH, n + ".png")
def n(x, d=2, unit=""):
    t = ("%." + str(d) + "f") % x
    ip, _, fp = t.partition(".")
    neg = ip.startswith("-"); ip = ip.lstrip("-")
    ip = "{:,}".format(int(ip)).replace(",", ".")
    r = ("-" if neg else "") + ip + ("," + fp if fp else "")
    return r + (" " + unit if unit else "")
def err(t, sv, d=3, unit="V"):
    e = abs(t - sv)
    return n(0.0 if e < 5 * 10 ** -(d + 1) else e, d, unit)
def load(name):
    p = os.path.join(H, "..", "build", name)
    return json.load(open(p)) if os.path.exists(p) else {}
def refs_block(D, refs):
    from docx.shared import Cm
    for i, r in enumerate(refs, 1):
        par = D.p("%d. %s" % (i, r)); par.paragraph_format.left_indent = Cm(0.9); par.paragraph_format.first_line_indent = Cm(-0.9)
