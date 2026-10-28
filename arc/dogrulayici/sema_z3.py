import sys
from z3 import Bool, Solver, And, Or, Not, Implies, sat, unsat

V1 = [
    "kabul_1", "tecrit_1", "terkip_1", "hukum_1", "hifz_1", "kelam_1", "fiil_1",
    "kabul_2", "tecrit_2", "terkip_2", "hukum_2", "hifz_2", "kelam_2", "fiil_2",
    "zaruret", "refleks",
]

EK = {
    "kabul_isaret": "S6 kabul tarafında da sorulur: alınan şey işaret mi (anlamak)",
    "hal_kapi": "dış kabul ve fiil kanalının açık/kapalı hâli (uyku, tefekkür)",
    "kip_farz": "muhtevanın kipi: vâki değil farz/itibarî (oyun kuralı, rüya, varsayım)",
    "kip_zaman": "muhtevanın kipi: şimdi değil geçmiş/gelecek (plan, hatıra)",
    "gayri_istidad": "2. derecenin nesnesi kendi istidadı değil başkasınınki (rakip, muhatap modeli)",
}

SENARYO = {
    "uyku":            {"iste": ["hal_kapi", "hifz_2", "terkip_2"], "kapali": ["kabul_1", "fiil_1"]},
    "ruya":            {"iste": ["hal_kapi", "terkip_1", "kip_farz", "hifz_1"], "kapali": ["kabul_1", "fiil_1"]},
    "kitap_okuma":     {"iste": ["kabul_isaret", "hifz_1", "hukum_1", "tecrit_1"], "kapali": []},
    "savas_taktigi":   {"iste": ["gayri_istidad", "kip_zaman", "terkip_1", "hukum_2"], "kapali": []},
    "savasma":         {"iste": ["kabul_1", "fiil_1", "hukum_1", "hukum_2"], "kapali": []},
    "oyun":            {"iste": ["kip_farz", "gayri_istidad", "fiil_1", "hukum_1"], "kapali": []},
    "mesele_cozme":    {"iste": ["tecrit_1", "hukum_1", "terkip_2", "hukum_2", "refleks", "zaruret"], "kapali": []},
    "icat":            {"iste": ["terkip_1", "terkip_2", "hukum_1", "fiil_1", "zaruret", "kip_zaman"], "kapali": []},
    "dil_ogrenme":     {"iste": ["kabul_isaret", "kabul_2", "terkip_2", "hifz_2", "kelam_1"], "kapali": []},
    "sessiz_tefekkur": {"iste": ["hal_kapi", "hukum_1", "tecrit_1"], "kapali": ["kabul_1", "fiil_1", "kelam_1"]},
    "yalan":           {"iste": ["kelam_1", "gayri_istidad", "hukum_2", "kip_farz"], "kapali": []},
    "ogretmek":        {"iste": ["kelam_2", "gayri_istidad", "tecrit_2"], "kapali": []},
    "hatirlamak":      {"iste": ["hifz_1", "hukum_1", "kip_zaman"], "kapali": []},
    "taklit":          {"iste": ["kabul_2", "fiil_1", "hifz_2"], "kapali": []},
}

HEPSI = V1 + list(EK)
B = {n: Bool(n) for n in HEPSI}


def kur(sema):
    z = Solver()
    for n in HEPSI:
        if n not in sema:
            z.add(Not(B[n]))
    for n in ("kabul_1", "fiil_1", "kelam_1"):
        if n in sema:
            z.add(Or(B[n], B["hal_kapi"]))
    return z


def sina(sema, adi):
    netice = {}
    for s, r in SENARYO.items():
        z = kur(sema)
        faraziye = [B[n] for n in r["iste"]]
        kapa = {Bool("kapali_" + n): n for n in r["kapali"]}
        for k, n in kapa.items():
            z.add(Implies(k, Not(B[n])))
        sonuc = z.check(*(faraziye + list(kapa)))
        eksik = sorted(str(x) for x in z.unsat_core()) if sonuc == unsat else []
        netice[s] = (sonuc == sat, eksik)
    tut = sum(1 for v in netice.values() if v[0])
    print("## %s: %d/%d senaryo tutar" % (adi, tut, len(SENARYO)))
    for s, (t, e) in netice.items():
        print("- %s: %s%s" % (s, "TUTAR" if t else "TUTMAZ", "" if t else " (çekirdek: " + ", ".join(e) + ")"))
    print()
    return netice


def asgarilik(sema):
    print("## Asgarîlik: her ek unsur çıkarılınca düşen senaryolar")
    for n in EK:
        dar = [x for x in sema if x != n]
        dusen = [s for s, (t, _) in sessiz(dar).items() if not t]
        print("- %s çıkarılırsa düşen: %s" % (n, ", ".join(dusen) if dusen else "hiçbiri (fazlalık)"))
    print()


def sessiz(sema):
    netice = {}
    for s, r in SENARYO.items():
        z = kur(sema)
        for n in r["kapali"]:
            z.add(Not(B[n]))
        netice[s] = (z.check(*[B[n] for n in r["iste"]]) == sat, [])
    return netice


def ayirt_ediyor_mu(sema):
    z = Solver()
    for m in HEPSI:
        if m not in sema:
            z.add(Not(B[m]))
    z.add(And(B["kabul_1"], Not(B["kabul_1"])))
    print("## Ayırt etme ispatı (F 3-B 27-B): çelişik senaryo (kabul_1 ve değil-kabul_1) -> %s" % z.check())
    print()


if __name__ == "__main__":
    v1 = sina(V1, "Şema v1 (7 hücre × 2 derece + zaruret + refleks)")
    v2 = sina(HEPSI, "Şema v2 (v1 + %d ek unsur)" % len(EK))
    asgarilik(HEPSI)
    ayirt_ediyor_mu(HEPSI)
    sys.exit(0 if all(t for t, _ in v2.values()) else 1)
