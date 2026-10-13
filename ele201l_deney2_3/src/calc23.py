import sys, json, itertools
sys.path.insert(0, "/home/user/Mucit-ai/ele201l_on_calisma/src")
from calc import sim
R = {}
# Deney 2 - Thevenin
base = "Vs 1 0 DC {vs}\nR1 1 a 2.2k\nR2 a 0 3.3k\nR3 a oc 2.2k\n"
R["voc"] = sim(base.format(vs=10), ["v(oc)"])["v(oc)"]
R["isc"] = -sim(base.format(vs=10) + "Vsc oc 0 DC 0\n", ["i(vsc)"])["i(vsc)"] * -1
R["isc"] = abs(sim(base.format(vs=10) + "Vsc oc 0 DC 0\n", ["i(vsc)"])["i(vsc)"])
it = abs(sim(base.format(vs=0) + "Vt oc 0 DC 1\n", ["i(vt)"])["i(vt)"]); R["rth_zero"] = 1 / it
R["rth_ratio"] = R["voc"] / R["isc"]
# yuk
pl = {}
for rl in (500, 1000, 2000, 3000, 3520, 4000, 5000, 7000, 10000):
    r = sim(base.format(vs=10) + "RL oc 0 %g\n" % rl, ["v(oc)"]); pl[rl] = (r["v(oc)"], r["v(oc)"] / rl, r["v(oc)"] ** 2 / rl)
R["pl"] = pl
# Deney 2 - superpozisyon
def sp(v1, v2, extra=""):
    n = ("VS1 a 0 DC %g\nR1 a b 15k\nR2 a x 15k\nVS2 x 0 DC %g\nR5 x 0 1k\nR4 x c 1k\nR3 b c 3.9k\nR6 c 0 8.2k\n" % (v1, v2)) + extra
    return n
R["sp"] = {}
for k, (v1, v2) in {"both": (12, 5), "s2": (0, 5), "s1": (12, 0)}.items():
    R["sp"][k] = sim(sp(v1, v2), ["v(c)"])["v(c)"]
R["sp"]["isc"] = abs(sim(sp(12, 5, "Vsc c 0 DC 0\n"), ["i(vsc)"])["i(vsc)"])
R["sp"]["rth"] = 1 / abs(sim(sp(0, 0, "Vt c 0 DC 1\n"), ["i(vt)"])["i(vt)"])
R["sp"]["rth_s2"] = R["sp"]["rth"]
json.dump(R, open("../build/calc23.json", "w"), indent=1)
print(json.dumps(R, indent=1))
