import os, sys, subprocess, csv, glob, shutil
import xml.etree.ElementTree as ET
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))

KATMAN = 'F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'

def calistir(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(' '.join(cmd) + '\n' + r.stdout + r.stderr)
    return r.stdout

def bom_yaz(xml, yol):
    t = ET.parse(xml).getroot()
    gr = defaultdict(list)
    for c in t.find('components'):
        ref = c.get('ref')
        val = c.findtext('value') or ''
        fp = c.findtext('footprint') or ''
        alan = {f.get('name'): f.text for f in c.iter('field')}
        dnp = any(p.get('name') == 'dnp' for p in c.iter('property')) or val == 'DNP'
        gr[(val, fp, alan.get('MPN', ''), dnp)].append(ref)
    def anahtar(r):
        import re
        m = re.match(r'([A-Z]+)(\d+)', r)
        return (m.group(1), int(m.group(2)))
    with open(yol, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['Comment', 'Designator', 'Footprint', 'Quantity', 'MPN / Aciklama', 'DNP (takilmaz)', 'LCSC Part # (dogrulanmadi)'])
        for (val, fp, mpn, dnp), refs in sorted(gr.items(), key=lambda kv: anahtar(sorted(kv[1], key=anahtar)[0])):
            refs = sorted(refs, key=anahtar)
            w.writerow([val, ','.join(refs), fp, len(refs), mpn, 'evet' if dnp else '', ''])
    return sum(len(v) for v in gr.values())

def uret(ad, dizin, hedef):
    pcb = os.path.join(dizin, ad + '.kicad_pcb')
    sch = os.path.join(dizin, ad + '.kicad_sch')
    xml = os.path.join(dizin, ad + '.xml')
    os.makedirs(hedef, exist_ok=True)
    ger = os.path.join(hedef, 'gerber')
    if os.path.isdir(ger): shutil.rmtree(ger)
    os.makedirs(ger)
    calistir(['kicad-cli', 'pcb', 'export', 'gerbers', '-l', KATMAN, '--subtract-soldermask', '-o', ger + '/', pcb])
    calistir(['kicad-cli', 'pcb', 'export', 'drill', '--format', 'excellon', '--drill-origin', 'absolute', '--excellon-units', 'mm', '--excellon-separate-th', '-o', ger + '/', pcb])
    pos = os.path.join(hedef, ad + '_yerlestirme.csv')
    calistir(['kicad-cli', 'pcb', 'export', 'pos', '--format', 'csv', '--units', 'mm', '--side', 'both', '--smd-only', '-o', pos, pcb])
    n = bom_yaz(xml, os.path.join(hedef, ad + '_malzeme_listesi.csv'))
    calistir(['kicad-cli', 'sch', 'export', 'pdf', '-o', os.path.join(hedef, ad + '_sema.pdf'), sch])
    calistir(['kicad-cli', 'pcb', 'export', 'pdf', '-l', 'F.Cu,F.Silkscreen,F.Courtyard,Edge.Cuts', '-o', os.path.join(hedef, ad + '_pano_on.pdf'), pcb])
    calistir(['kicad-cli', 'pcb', 'export', 'pdf', '--mirror', '-l', 'B.Cu,B.Silkscreen,B.Courtyard,Edge.Cuts', '-o', os.path.join(hedef, ad + '_pano_arka.pdf'), pcb])
    # tek zip
    shutil.make_archive(os.path.join(hedef, ad + '_gerber'), 'zip', ger)
    return n

if __name__ == '__main__':
    print(uret(sys.argv[1], sys.argv[2], sys.argv[3]))
