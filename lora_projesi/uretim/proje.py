import os, sys, json, shutil
D = os.path.dirname(__file__)

def proje_yaz(dizin, ad, ozel_lib=False):
    pro = {"meta": {"filename": ad + ".kicad_pro", "version": 1},
           "board": {"design_settings": {"rules": {"min_clearance": 0.15, "min_track_width": 0.15, "min_via_diameter": 0.5, "min_through_hole_diameter": 0.2,
                                                    "min_copper_edge_clearance": 0.3, "min_hole_clearance": 0.1}}},
           "net_settings": {"classes": [{"name": "Default", "clearance": 0.15, "track_width": 0.2, "via_diameter": 0.6, "via_drill": 0.3}], "meta": {"version": 3}},
           "sheets": [], "text_variables": {}}
    json.dump(pro, open(os.path.join(dizin, ad + '.kicad_pro'), 'w'), indent=2)
    if ozel_lib:
        lib = os.path.join(dizin, 'kutuphane')
        os.makedirs(lib, exist_ok=True)
        syms, fps = [], []
        for ad, aciklama in (('Simcom', 'A7670SA modulu (resmi veri sayfasindan)'), ('Ozel', 'Ra-01H ve LM66100')):
            shutil.copy(os.path.join(D, 'kutuphane', ad + '.kicad_sym'), lib)
            hedef = os.path.join(lib, ad + '.pretty')
            if os.path.isdir(hedef): shutil.rmtree(hedef)
            shutil.copytree(os.path.join(D, 'kutuphane', ad + '.pretty'), hedef)
            syms.append('  (lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/kutuphane/%s.kicad_sym")(options "")(descr "%s"))\n' % (ad, ad, aciklama))
            fps.append('  (lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/kutuphane/%s.pretty")(options "")(descr "%s"))\n' % (ad, ad, aciklama))
        open(os.path.join(dizin, 'sym-lib-table'), 'w').write('(sym_lib_table\n' + ''.join(syms) + ')\n')
        open(os.path.join(dizin, 'fp-lib-table'), 'w').write('(fp_lib_table\n' + ''.join(fps) + ')\n')

if __name__ == '__main__':
    proje_yaz(sys.argv[1], sys.argv[2], len(sys.argv) > 3)
