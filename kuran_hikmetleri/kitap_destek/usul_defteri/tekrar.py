import json, time, re, urllib.parse, urllib.request
d = json.load(open("tara_ham.json", encoding="utf-8"))
def toks(s): return set(w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 3)
def sor(q):
    u = "https://api.crossref.org/works?query.bibliographic=%s&rows=3&select=DOI,title,issued,author,container-title" % urllib.parse.quote(q)
    for k in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40)
            return json.load(r)["message"]["items"]
        except Exception as e:
            time.sleep(4 + 4 * k)
    return None
for o in d:
    s = o["crossref"] or {}
    if s.get("hata") or not s or o["crossref"] is None:
        time.sleep(1.2)
        it = sor(o["sorgu"])
        o["crossref"] = None
        if it:
            tq = toks(o["sorgu"])
            best = max(it, key=lambda m: len(tq & toks((m.get("title") or [""])[0])) / max(1, len(tq)))
            o["crossref"] = dict(doi=best["DOI"], baslik=(best.get("title") or [""])[0], yil=(best.get("issued", {}).get("date-parts") or [[None]])[0][0],
                                 yazar=[a.get("family") for a in best.get("author", [])][:3], yayin=(best.get("container-title") or [""])[0])
    s = o["crossref"]
    if s and s.get("baslik"):
        tq = toks(o["sorgu"]); tb = toks(s["baslik"])
        s["eslesme"] = round(len(tq & tb) / max(1, len(tq)), 2)
json.dump(d, open("tara_ham.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for o in d:
    s = o["crossref"] or {}
    print(str(s.get("eslesme", "-")).ljust(5), o["ad"][:40].ljust(42), s.get("yil") or "-", (s.get("baslik") or "yok")[:60])
