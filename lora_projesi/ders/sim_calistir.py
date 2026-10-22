"""Yerel calisir (ngspice ister): simulasyon/*.cir dosyalarini kosar, dalga bicimlerini veri/sim_*.json olarak yazar. Genel modeller kullanilir (uretici modeli degil)."""
import os, re, json, subprocess, tempfile
K = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(K, '..', 'simulasyon')

def kos(cir, degisken, adim_bas=None):
    t = open(os.path.join(S, cir)).read()
    out = tempfile.mktemp(suffix='.dat')
    t = re.sub(r'\.control.*?\.endc', '.control\n%s\nwrdata %s %s\n.endc' % (adim_bas, out, ' '.join(degisken)), t, flags=re.S)
    f = tempfile.mktemp(suffix='.cir'); open(f, 'w').write(t)
    subprocess.run(['ngspice', '-b', f], capture_output=True, text=True, timeout=120)
    veri = [list(map(float, l.split())) for l in open(out) if l.strip()]
    return veri

def seyrelt(veri, n=400):
    k = max(1, len(veri) // n)
    return veri[::k]

# 36 V darbe
v = kos('giris_koruma_3_darbe.cir', ['v(in)', 'v(out)', 'v(g)-v(out)', 'i(Vtv)'], 'tran 10u 20m')
# wrdata her degisken icin (zaman, deger) cifti yazar -> sutunlar: t,v(in), t,v(out), t,vgs, t,i
d = seyrelt(v)
darbe = {'t_ms': [r[0] * 1e3 for r in d], 'vin': [r[1] for r in d], 'vout': [r[3] for r in d], 'vgs': [r[5] for r in d], 'itvs': [r[7] for r in d]}
json.dump({'giris_darbe': darbe}, open(os.path.join(K, 'veri', 'sim_giris.json'), 'w'))
# role surucusu
r = kos('role_surucu.cir', ['v(g)', 'i(LRL)', 'v(c)'], 'tran 2u 14m')
d = seyrelt(r, 600)
role = {'t_ms': [x[0] * 1e3 for x in d], 'vg': [x[1] for x in d], 'ic': [x[3] for x in d], 'vc': [x[5] for x in d]}
json.dump({'role': role}, open(os.path.join(K, 'veri', 'sim_role.json'), 'w'))
print('tamam', len(darbe['t_ms']), len(role['t_ms']), max(darbe['vout']), max(role['vc']), max(role['ic']))
