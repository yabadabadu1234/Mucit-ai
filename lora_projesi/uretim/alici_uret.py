import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import alici_pcb
from pcbgen import mm, vec
import yonlendir as Y

DIZIN = os.path.join(os.path.dirname(__file__), '..', 'alici')
XML = os.path.join(DIZIN, 'alici.xml')
GUC12 = ['+12V_IN', '+12V_F', '+12V']
GUC_ORTA = ['VBAT_MOD', 'LAMBA_SW', 'SW_3V3', 'SW_MOD']
KUCUK = ['ROLE_L']
RF = ['ANT_RF', 'MODEM_ANT', 'ANT_4G', 'MODEM_AUX', 'ANT_AUX']
PLANE = {'GND', '+3V3'}
RF_W = 0.40

def dsn_duzenle(yol, korunan):
    t = open(yol).read()
    m = re.search(r'    \(class kicad_default "" (.*?)\n      \(circuit', t, re.S)
    aglar = m.group(1).split()
    for a in PLANE:
        t = re.sub(r'    \(net %s\n      \(pins [^)]*\)\n    \)\n' % re.escape(a), '', t)
    t = re.sub(r'    \(plane [^\n]*\n', '', t)
    aglar = [a for a in aglar if a not in PLANE]
    g12 = [a for a in aglar if a in GUC12]
    go = [a for a in aglar if a in GUC_ORTA]
    rf = [a for a in aglar if a in RF]
    normal = [a for a in aglar if a not in g12 + go + rf]
    def sinif(ad, gen, liste):
        if not liste: return ''
        return ('    (class %s %s\n      (circuit\n        (use_via Via[0-3]_600:300_um)\n      )\n      (rule\n        (width %d)\n        (clearance 150)\n      )\n    )\n'
                % (ad, ' '.join('"%s"' % x if ('+' in x) else x for x in liste), gen))
    yeni = sinif('kicad_default', 200, normal) + sinif('g12', 800, g12) + sinif('gorta', 500, go) + sinif('rf', int(RF_W * 1000), rf)
    bas = t.index('    (class kicad_default')
    son = t.index('  (wiring')
    ag_son = t.rindex('  )\n', bas, son)
    t = t[:bas] + yeni + t[ag_son:]
    for a in korunan:
        t = re.sub(r'(\(net %s\)\(type )route\)' % re.escape(a), r'\1protect)', t)
    t = re.sub(r'\(clearance [\d.]+ \(type smd_smd\)\)', '(clearance 150 (type smd_smd))', t)
    t = re.sub(r'\(clearance 20?[01]?\.?[01]?\)', '(clearance 150)', t)
    t = t.replace('(clearance 200.1)', '(clearance 150)').replace('(clearance 150.1', '(clearance 150')
    t = re.sub(r'\(layer (In[12]\.Cu)\n      \(type signal\)', r'(layer \1\n      (type power)', t)
    open(yol, 'w').write(t)

def hazirla():
    p, y = alici_pcb.kur(XML)
    b = p.b
    ds = b.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.15); ds.m_MinClearance = mm(0.14); ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.2); ds.m_CopperEdgeClearance = mm(0.3); ds.m_HoleClearance = mm(0.1)
    ds.m_NetSettings.m_DefaultNetClass.SetClearance(mm(0.14))
    print('delik koruma', Y.delik_koruma(b))
    Y.zone(b, 'GND', pcbnew.In1_Cu, alici_pcb.W, alici_pcb.H, 0.3)
    Y.zone(b, '+3V3', pcbnew.In2_Cu, alici_pcb.W, alici_pcb.H, 0.3)
    return p

if __name__ == '__main__':
    gecis = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    p = hazirla()
    b = p.b
    b.Save(os.path.join(DIZIN, 'alici_once.kicad_pcb'))
    dsn = '/tmp/claude-0/alici.dsn'; ses = '/tmp/claude-0/alici.ses'
    pcbnew.ExportSpecctraDSN(b, dsn)
    dsn_duzenle(dsn, [])
    if len(sys.argv) > 2 and sys.argv[2] == 'tekrar' and os.path.exists(ses):
        print('ses yeniden kullanildi')
    else:
        log = Y.fr_calistir(dsn, ses, gecis, zaman=3000)
        print([l for l in log.split('\n') if 'completed' in l][:6])
    print('ses', Y.ses_uygula(b, ses))
    pv = Y.plane_via(b, ['GND', '+3V3'], alici_pcb.W, alici_pcb.H)
    print('plane via', pv['eklendi'], 'bulunamadi', pv['bulunamadi'])
    Y.doldur(b)
    b.BuildConnectivity()
    print('baglantisiz', b.GetConnectivity().GetUnconnectedCount(False))
    b.Save(os.path.join(DIZIN, 'alici.kicad_pcb'))
    rep = Y.drc(b, '/tmp/claude-0/drc_alici.rpt')
    s, o = Y.drc_ozet(rep, 6)
    print(dict(s))
    for k, v in o.items():
        if k.startswith('silk') or k.startswith('lib_footprint') or k.endswith('(w)'): continue
        print('==', k)
        for x in v: print('   ', x[:260])
