import os, re, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import gomme
B = pathlib.Path(__file__).resolve().parent.parent
kok = json.load(open(B / "kaynak/lugat/kok_anlamlari.json", encoding="utf-8"))
met = [re.sub(r"^[^:]*:\s*", "", x["turkce"], count=1) if re.match(r"^[^:]{1,25}:", x["turkce"]) else x["turkce"] for x in kok]
G = {
 "sebep1": "Verilen kavramın sebebi olan kavramı bul",
 "sebep2": "Bu olgunun doğmasına yol açan şeyi getir",
 "sebep3": "Bu hâlin illetini, yani doğurucusunu ara",
 "netice1": "Verilen kavramın neticesi olan kavramı bul",
 "netice2": "Bu olgudan doğan sonucu getir",
 "netice3": "Bu hâlin malûlünü, yani doğurduğunu ara",
 "es": "Verilen kavramın eş anlamlısını bul",
 "zit": "Verilen kavramın zıt anlamlısını bul",
}
for ad, g in G.items():
    gomme.toplu("ajan_" + ad, [f"Instruct: {g}\nQuery: {m}" for m in met])
print("bitti")
