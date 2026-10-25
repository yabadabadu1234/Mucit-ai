import json, re, sys, collections

YASAK = ("ilişkili", "benzer", "ayrılmaz")
SONUC = {"gecti", "kaldi", "uygulanmadi"}
DERECE = {"iz-dogrulandi", "hipotez", "rivayet-yoklanmadi"}
TASIYICI = {"lafiz", "yapi", "mana", "dis"}
TESTLER = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]

d = json.load(open("FATIHA_KAYITLARI.json", encoding="utf-8"))
kayit = d["kayitlar"]
ids = {k["id"] for k in kayit}
hata = []


def tur(ref):
    if re.fullmatch(r"\d+:\d+[a-z]?", ref):
        return "birim"
    if re.fullmatch(r"S\d{3}", ref):
        return "butun"
    if re.fullmatch(r"F\d+", ref):
        return "bag"
    if ref.startswith("dis:"):
        return "dis"
    return None


def ayet_gecerli(ref):
    s, a = re.match(r"(\d+):(\d+)", ref).groups()
    return int(a) >= 1 and (int(s) != 1 or int(a) <= 7)


for k in kayit:
    i = k["id"]
    for alan in ("cins", "uyeler", "tasiyici", "iz", "iddia", "yikan_sart", "katiyet", "testler", "geri_getirme"):
        if alan not in k or not k[alan]:
            hata.append(i + " eksik alan " + alan)
    if k.get("cins") not in d["cinsler"]:
        hata.append(i + " tanimsiz cins")
    for u in k["uyeler"]:
        t = tur(u["ref"])
        if t is None:
            hata.append(i + " tanimsiz uye " + u["ref"])
        elif t == "birim" and not ayet_gecerli(u["ref"]):
            hata.append(i + " gecersiz ayet " + u["ref"])
        elif t == "bag" and u["ref"] not in ids:
            hata.append(i + " bulunmayan bag " + u["ref"])
        if k.get("cins") in d["cinsler"] and u["rol"] not in d["cinsler"][k["cins"]]:
            hata.append(i + " rol imzasi disi " + u["rol"])
    if any(w in k["iddia"].lower() for w in YASAK):
        hata.append(i + " yasak sozcuk")
    if not set(k["tasiyici"]) <= TASIYICI:
        hata.append(i + " tasiyici")
    if set(k["katiyet"]) != set(k["tasiyici"]):
        hata.append(i + " katiyet tasiyiciyla ayni degil")
    if not set(k["katiyet"].values()) <= DERECE:
        hata.append(i + " derece")
    if set(k["testler"]) != set(TESTLER) or not set(k["testler"].values()) <= SONUC:
        hata.append(i + " testler")

ust = {k["id"]: [u["ref"] for u in k["uyeler"] if tur(u["ref"]) == "bag"] for k in kayit}


def dongu(a, gorulen):
    if a in gorulen:
        return True
    return any(dongu(b, gorulen | {a}) for b in ust.get(a, []))


for a in ids:
    if dongu(a, frozenset()):
        hata.append(a + " bag-bag dongusu")

uye_say = collections.Counter(len(k["uyeler"]) for k in kayit)
simetrik = [k["id"] for k in kayit if len({u["rol"] for u in k["uyeler"]}) == 1]
mertebe = collections.Counter(
    "-".join(sorted({tur(u["ref"]) for u in k["uyeler"]})) for k in kayit
)
ortusen = collections.defaultdict(list)
for k in kayit:
    for u in k["uyeler"]:
        ortusen[u["ref"]].append(k["id"])
coklu = {r: v for r, v in ortusen.items() if len(v) > 1 and tur(r) == "birim"}
gecti = sum(1 for k in kayit for v in k["testler"].values() if v == "gecti")
toplam = len(kayit) * len(TESTLER)
uygulanmadi = sum(1 for k in kayit for v in k["testler"].values() if v == "uygulanmadi")
yerlesmeyen = sum(1 for h in hata if "eksik alan" in h or "tanimsiz cins" in h)

print("kayit", len(kayit), "uye sayisi dagilimi", dict(uye_say))
print("simetrik", simetrik)
print("mertebe", dict(mertebe))
print("birden cok bagda yer alan birim", coklu)
print("test gecti", gecti, "uygulanmadi", uygulanmadi, "toplam", toplam)
print("yerlesmeyen", yerlesmeyen, "hata", len(hata))
for h in hata:
    print("HATA", h)
sys.exit(1 if hata else 0)
