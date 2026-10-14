import subprocess, json, re, sys
import lib
import p1, p2, p3, p4, p5
n0=len(lib.SLIDES)
import p7
new=lib.SLIDES[n0:]; del lib.SLIDES[n0:]
import p6
def find(kick,title,nth=0):
    c=[i for i,s in enumerate(lib.SLIDES) if s.get('kicker')==kick and s.get('title')==title]
    return c[nth]
plan=[(('Principle 1 · Consent','Where the principle stops, and the best objection'),new[0:1]),
(('Principle 2 · Harm','Where the principle stops, and the best objection'),new[1:2]),
(('Principle 4 · Waste','Usable value may not be destroyed: offered as support only'),new[2:3]),
(('Defense 5','&#8220;It serves others&#8221;'),new[3:8]),
(('The doubt court · 6 of 7','Doubts about reach and effect'),new[8:9])]
for (k,t),sl in plan:
    i=find(k,t); lib.SLIDES[i+1:i+1]=sl
for i,s in enumerate(lib.SLIDES): print(i+1,s.get('kicker','RAW'),'|',s.get('title',''))
# legend on first doubt-court slide
for s in lib.SLIDES:
    if s.get("kicker") == "The doubt court · 1 of 7":
        s["src"] = "Verdict on the doubt: " + lib.chip("no") + " the doubt fails · " + lib.chip("part") + " it holds within the limits the answer states · " + lib.chip("yes") + " it is right, and consistent with the ruling · " + lib.chip("out") + " not what the claim covers."
lib.assemble("deck.html")
chrome = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
r = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=4000", "--dump-dom", "file:///home/user/Mucit-ai/sunum/plan2/deck.html"], capture_output=True, text=True, timeout=180)
m = re.search(r"<title>(OVER:.*?)</title>", r.stdout)
print(m.group(1) if m else "no title found", len(lib.SLIDES), "slides")
subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=Planned_Obsolescence.pdf", "file:///home/user/Mucit-ai/sunum/plan2/deck.html"], capture_output=True, timeout=240)
