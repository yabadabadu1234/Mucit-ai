"""spice/*.cir -> ltspice/*.cir (temiz, .control bloğu yok; MOS modelleri föydeki aslî satırlarla)."""
import os, re, shutil
from common import SPICE, ROOT, clean_cir

OUTD = os.path.join(ROOT, "ltspice")
os.makedirs(OUTD, exist_ok=True)
NM = ".model BS170 NMOS (VTO=2.1 RG=270 RS=1.572 RD=1.436 RB=.768\n+ KP=.1233 Rds=1.2E8 IS=5p Tt=161.6n)"
PM = ".model BS250 PMOS (VTO=-1.0 Kp=150u Lambda=0.02 Rd=1 Rs=1 Rg=1 Is=20n)"
names = ["e1_dc_1n4148", "e1_tran", "e2_inv_tran", "e2_inv_dc", "e2_bs_dc", "e3_op_1", "e3_tran_1", "e3_tran_0", "e3_ac_1", "e3_ac_0", "e3_mirror_dc",
         "e4_c1", "e4_c2", "e4_t1_5_10", "e5_ce_ac_1", "e5_ce_ac_0", "e5_cc_ac"]
for n in names:
    p = os.path.join(SPICE, n + ".cir")
    if not os.path.exists(p):
        print("yok:", n); continue
    t = clean_cir(p)
    t = re.sub(r"^\.model BS170 NMOS \(.*\)\s*$", NM, t, flags=re.M)
    t = re.sub(r"^\.model BS250 PMOS \(.*\)\s*$", PM, t, flags=re.M)
    t = "* ELE224L - %s\n* ngspice ile uretildi/dogrulandi; LTspice'ta bu ortamda ACILMADI (File>Open ile acip calistirin).\n" % n + t
    open(os.path.join(OUTD, n + ".cir"), "w").write(t)
print(sorted(os.listdir(OUTD)))
