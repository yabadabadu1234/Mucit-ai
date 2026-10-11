import sys, subprocess, importlib, os
sys.path.insert(0, os.path.dirname(__file__))
from common import OUT

def build(n):
    ex = importlib.import_module("exp%d" % n)
    dc = importlib.import_module("docs%d" % n)
    R = ex.run()
    en = os.path.join(OUT, "EN_Experiment%d_Preliminary_Report.docx" % n)
    tr = os.path.join(OUT, "TR_Deney%d_Ogretici_Rehber.docx" % n)
    dc.build_en(R).save(en)
    dc.build_tr(R).save(tr)
    for f in (en, tr):
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, f], capture_output=True, timeout=300)
    print("built", n)

if __name__ == "__main__":
    for n in map(int, sys.argv[1:]):
        build(n)
