import sys, os, re, shutil
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew
import tx_pcb
from pcbgen import mm, vec
import yonlendir as Y

DIZIN = os.path.join(os.path.dirname(__file__), '..', 'verici')
XML = os.path.join(DIZIN, 'verici.xml')
GUC = ['VIN', 'VBAT_RAW', 'VBAT_SW', 'VBUS', 'L1N', 'L2N']
RF_W = 0.40

def dsn_duzenle(yol, korunan_aglar):
    t = open(yol).read()
    m = re.search(r'    \(class kicad_default "" (.*?)\n      \(circuit', t, re.S)
    aglar = m.group(1).split()
    plane = {'GND', '+3V3'}
    for a in plane:
        t = re.sub(r'    \(net %s\n      \(pins [^)]*\)\n    \)\n' % re.escape(a), '', t)
    t = re.sub(r'    \(plane [^\n]*\n', '', t)
    aglar = [a for a in aglar if a not in plane]
    normal = [a for a in aglar if a not in GUC and a != 'ANT_RF']
    guc = [a for a in aglar if a in GUC]
    def sinif(ad, gen, liste):
        if not liste: return ''
        return ('    (class %s %s\n      (circuit\n        (use_via Via[0-3]_600:300_um)\n      )\n      (rule\n        (width %d)\n        (clearance 150)\n      )\n    )\n'
                % (ad, ' '.join(liste), gen))
    yeni = sinif('kicad_default', 200, normal) + sinif('guc', 250, guc) + sinif('rf', int(RF_W * 1000), ['ANT_RF'])
    bas = t.index('    (class kicad_default')
    son = t.index('  (wiring')
    # sinif blogunun sonu: wiring'den onceki '  )' ' ' kapatan network kapanisi
    ag_son = t.rindex('  )\n', bas, son)
    t = t[:bas] + yeni + t[ag_son:]
    for a in korunan_aglar:
        t = re.sub(r'(\(net %s\)\(type )route\)' % re.escape(a), r'\1protect)', t)
    t = t.replace('(clearance 200.1)', '(clearance 150)')
    t = re.sub(r'\(clearance [\d.]+ \(type smd_smd\)\)', '(clearance 150 (type smd_smd))', t)
    t = re.sub(r'\(clearance 150\.1', '(clearance 150', t)
    t = re.sub(r'\(layer (In[12]\.Cu)\n      \(type signal\)', r'(layer \1\n      (type power)', t)
    open(yol, 'w').write(t)

def hazirla():
    p = tx_pcb.kur(XML)
    b = p.b
    ds = b.GetDesignSettings()
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_MinClearance = mm(0.14)
    ds.m_ViasMinSize = mm(0.5)
    ds.m_MinThroughDrill = mm(0.2)
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_HoleClearance = mm(0.1)
    ds.m_NetSettings.m_DefaultNetClass.SetClearance(mm(0.14))
    # RF izi: U4 pin1 -> J2 pin1, duz
    f4 = p.fps['U4']; f2 = p.fps['J2']
    a = [pd for pd in f4.Pads() if pd.GetNumber() == '1'][0].GetPosition()
    c = [pd for pd in f2.Pads() if pd.GetNumber() == '1'][0].GetPosition()
    tr = pcbnew.PCB_TRACK(b)
    tr.SetStart(a); tr.SetEnd(c); tr.SetWidth(mm(RF_W)); tr.SetLayer(pcbnew.F_Cu); tr.SetNet(b.FindNet('ANT_RF'))
    b.Add(tr)
    print('delik koruma', Y.delik_koruma(b))
    Y.zone(b, 'GND', pcbnew.In1_Cu, tx_pcb.W, tx_pcb.H, 0.3)
    Y.zone(b, '+3V3', pcbnew.In2_Cu, tx_pcb.W, tx_pcb.H, 0.3)
    return p

if __name__ == '__main__':
    gecis = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    p = hazirla()
    b = p.b
    pre = os.path.join(DIZIN, 'verici_once.kicad_pcb')
    b.Save(pre)
    dsn = '/tmp/claude-0/verici.dsn'; ses = '/tmp/claude-0/verici.ses'
    pcbnew.ExportSpecctraDSN(b, dsn)
    dsn_duzenle(dsn, ['ANT_RF'])
    if len(sys.argv) > 2 and sys.argv[2] == 'tekrar' and os.path.exists(ses):
        print('ses yeniden kullanildi')
    else:
        log = Y.fr_calistir(dsn, ses, gecis)
        print([l for l in log.split('\n') if 'completed' in l or 'ERROR' in l and 'Version' not in l][:6])
    print('ses', Y.ses_uygula(b, ses))
    pv = Y.plane_via(b, ['GND', '+3V3'], tx_pcb.W, tx_pcb.H)
    print('plane via', pv['eklendi'], 'bulunamadi', pv['bulunamadi'])
    for ag, pn in [('USB_DM', 'A7'), ('USB_DP', 'A6')]:
        pass
    Y.doldur(b)
    b.BuildConnectivity()
    print('baglantisiz', b.GetConnectivity().GetUnconnectedCount(False))
    b.Save(os.path.join(DIZIN, 'verici.kicad_pcb'))
    rep = Y.drc(b, '/tmp/claude-0/drc_verici.rpt')
    s, o = Y.drc_ozet(rep, 6)
    print(dict(s))
    for k, v in o.items():
        if k.startswith('silk') or k.startswith('lib_footprint') or k.endswith('(w)'): continue
        print('==', k)
        for x in v: print('   ', x[:260])
