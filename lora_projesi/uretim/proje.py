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
        shutil.copy(os.path.join(D, 'kutuphane', 'Simcom.kicad_sym'), lib)
        if os.path.isdir(os.path.join(lib, 'Simcom.pretty')): shutil.rmtree(os.path.join(lib, 'Simcom.pretty'))
        shutil.copytree(os.path.join(D, 'kutuphane', 'Simcom.pretty'), os.path.join(lib, 'Simcom.pretty'))
        open(os.path.join(dizin, 'sym-lib-table'), 'w').write('(sym_lib_table\n  (lib (name "Simcom")(type "KiCad")(uri "${KIPRJMOD}/kutuphane/Simcom.kicad_sym")(options "")(descr "SIM7600 modulu (resmi veri sayfasindan)"))\n)\n')
        open(os.path.join(dizin, 'fp-lib-table'), 'w').write('(fp_lib_table\n  (lib (name "Simcom")(type "KiCad")(uri "${KIPRJMOD}/kutuphane/Simcom.pretty")(options "")(descr "SIM7600 LCC87 ayak izi"))\n)\n')

if __name__ == '__main__':
    proje_yaz(sys.argv[1], sys.argv[2], len(sys.argv) > 3)
