import subprocess, json, re, sys
import lib
import p1, p2, p3, p4, p5, p6
# legend on first doubt-court slide
for s in lib.SLIDES:
    if s.get("kicker") == "The doubt court · 1 of 6":
        s["src"] = "Verdict on the doubt: " + lib.chip("no") + " the doubt fails · " + lib.chip("part") + " it holds within the limits the answer states · " + lib.chip("yes") + " it is right, and consistent with the ruling · " + lib.chip("out") + " not what the claim covers."
lib.assemble("deck.html")
chrome = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
r = subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--virtual-time-budget=4000", "--dump-dom", "file:///home/user/Mucit-ai/sunum/plan2/deck.html"], capture_output=True, text=True, timeout=180)
m = re.search(r"<title>(OVER:.*?)</title>", r.stdout)
print(m.group(1) if m else "no title found", len(lib.SLIDES), "slides")
subprocess.run([chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf=Planned_Obsolescence.pdf", "file:///home/user/Mucit-ai/sunum/plan2/deck.html"], capture_output=True, timeout=240)
