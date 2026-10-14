from lib import *

raw('''<section class="slide dark"><div class="kick" style="margin-top:150px">Business Ethics · Presentation</div>
<h1 style="margin-top:6px">Planned Obsolescence</h1>
<div style="font-size:33px;line-height:1.35;color:#C9D6E2;margin-bottom:46px;max-width:1250px">A ruling, its proof, and why no defense survives it.</div>
<div style="border-left:9px solid #7AD0C8;padding:8px 0 8px 28px;font-size:29px;line-height:1.42;max-width:1330px">
<b>Thesis.</b> A maker may not shorten the useful life of a product he has sold, or take away its owner&#8217;s power to keep it working, without the buyer&#8217;s knowledge and consent. Doing so is unjust, and the classical rulings against it are sound.</div>
<div style="position:absolute;left:92px;bottom:58px;font-size:22px;color:#9FB1C2">Beşir Kerem Üstüntürk · 251201037 · October 2026</div></section>''')

slide("Orientation", "What this talk will do",
'''<div class="cols"><div class="col" style="flex:1.25"><ul class="b">
<li><b>Define the claim exactly</b>, and say what it leaves out.</li>
<li><b>Show how a moral ruling is proven</b>, step by step, so you can check each step yourself.</li>
<li><b>Prove the ruling from independent grounds</b>: consent, harm, ownership. A fourth ground, waste, is offered as support only.</li>
<li><b>Close every escape route</b> with a complete yes/no tree of defenses, then <b>meet the maker&#8217;s own case</b> (&#8220;it funds innovation&#8221;) with five logical tests.</li>
<li><b>Test the ruling</b> on four public cases and twenty-eight doubts.</li>
<li><b>State the ruling in force</b>: what is forbidden, what is required, what is permitted.</li>
</ul></div>
<div class="col"><div class="card" style="padding:22px 26px"><div class="label">How certain is each step?</div>
<p class="small" style="margin:0 0 12px 0">'''+chip("certain")+''' every premise is certain and the form is valid.</p>
<p class="small" style="margin:0 0 12px 0">'''+chip("strong")+''' sound texts or clear reasoning; a minority objection can be stated.</p>
<p class="small" style="margin:0 0 12px 0">'''+chip("probable")+''' analogy, or a point scholars dispute; the better view is adopted and named.</p>
<p class="small" style="margin:0 0 12px 0">'''+chip("support")+''' adds weight; the proof does not depend on it.</p>
<p class="small" style="margin:0"><b>Rule of the weakest link:</b> a conclusion is never stronger than the weakest step that leads to it.</p></div></div></div>''')

slide("The starting point", "Start with one purchase",
'''<p>You pay a price <i>P</i> for a device. You expect it to serve you for a time <i>E</i>, as devices of its kind ordinarily do. The maker knows, from a design or software decision he took, that it will serve for only <i>L</i>, and <i>L</i> is less than <i>E</i>. Nobody tells you.</p>
<div class="formula">Shortfall&nbsp;=&nbsp;<i>P</i>&nbsp;×&nbsp;(1&nbsp;−&nbsp;<i>L</i>&nbsp;/&nbsp;<i>E</i>)</div>
<p>If the device serves half as long as expected, half of the price bought nothing. The formula is only arithmetic: <i>P</i>, <i>E</i> and <i>L</i> are variables, and this talk claims no numbers for them.</p>
<div class="cols" style="margin-top:6px"><div class="card dash col"><b>Did you consent to pay for <i>E</i>?</b><br>Yes. You paid because you believed in it.</div><div class="card dash col"><b>Did you receive what you paid for?</b><br>No. You received <i>L</i>.</div><div class="card dash col"><b>Who could have prevented the gap at no cost?</b><br>The one who knew: the maker.</div></div>''')

slide("The claim", "What exactly is planned obsolescence?",
'''<div class="bar navy"><b>Definition.</b> Planned obsolescence is a choice, made by the maker, that shortens the useful life of a product he has sold, or removes its owner&#8217;s power to extend that life.</div>
<div class="cols" style="margin-top:22px"><div class="col"><div class="label">Three words that matter</div><ul class="b small">
<li><b>Choice.</b> An accident, or a flaw the maker did not know of, is not planned.</li>
<li><b>Maker.</b> The one who designs, sells, updates, supports or controls the parts and tools.</li>
<li><b>Useful life.</b> Durability plus maintainability: how long it works, and how long its owner can keep it working.</li></ul></div>
<div class="col"><div class="label">What the claim leaves out</div><ul class="b small">
<li><b>Natural wear</b> and accident: time, not a choice, ends the life.</li>
<li><b>Real progress:</b> a better new device leaves the old one unchanged.</li>
<li><b>Changing taste:</b> fashion alters desire, not the old device.</li>
<li><b>An honest short life:</b> a product whose short life the buyer knows about when he buys it.</li></ul></div></div>''')

# --- map tree
tree = '''<svg viewBox="0 0 1416 560" width="100%" style="margin-top:2px">''' + DEFS + \
 svg_node(10, 8, 330, 70, [("Q1  Is the shortening", True), ("a choice of the maker?", True)], "d") + \
 svg_line(340, 43, 470, 43, "no", True, 388, 34) + svg_node(470, 8, 360, 70, [("N  Natural wear, progress", True), ("outside the claim", False)], "g") + \
 svg_line(175, 78, 175, 130, "yes", True, 186, 112) + \
 svg_node(10, 130, 330, 70, [("Q2  Does the choice act on", True), ("the product itself?", True)], "d") + \
 svg_line(340, 165, 470, 165, "yes", True, 388, 156) + svg_node(470, 130, 360, 70, [("Q2a  When does it act?", True)], "d") + \
 svg_line(830, 150, 958, 110, None, True) + svg_line(830, 180, 958, 250, None, True) + \
 '<text x="846" y="104" font-size="17" font-weight="700" fill="#4A5F73" font-family="Inter,sans-serif">before sale</text><text x="846" y="270" font-size="17" font-weight="700" fill="#4A5F73" font-family="Inter,sans-serif">after sale</text>' + \
 svg_node(962, 68, 448, 84, [("A1  Built in", True), ("design, materials, firmware at sale", False)], "t") + \
 svg_node(962, 222, 448, 84, [("A2  Imposed", True), ("remote update, kill switch, lock", False)], "t") + \
 svg_line(175, 200, 175, 330, "no", True, 186, 270) + \
 svg_node(10, 330, 330, 90, [("Q3  Does the owner need", True), ("the maker's own help to", True), ("keep it working?", True)], "d") + \
 svg_line(340, 375, 470, 375, "yes", True, 388, 366) + \
 svg_node(470, 330, 500, 90, [("B  Withdrawn support", True), ("updates, parts, servers, service", False), ("ended or switched off", False)], "t") + \
 svg_line(175, 420, 175, 490, "no", True, 186, 466) + \
 svg_node(10, 490, 1000, 66, [("C  Blocked repair: the maker closes the means that others or the owner could use", True)], "t") + \
 '</svg>'
slide("The map", "A maker can cut a product&#8217;s life in four places", tree,
 "Every question is a yes/no split, so no case can fall between branches, and no case enters two. A case with several mechanisms is split into its mechanisms; each goes to one leaf.")

slide("The map", "The four leaves, in plain terms",
'''<table><tr><th style="width:80px">Leaf</th><th>What the maker does</th><th>What the owner loses</th><th>What the maker knows</th></tr>
<tr><td class="k">A1</td><td>Builds the product so that it fails or wears early: a filament, a sealed battery, a part with a short rated life.</td><td>The years he believed he was buying.</td><td>The life he designed.</td></tr>
<tr><td class="k">A2</td><td>Changes the device after the sale: a software update that slows it, a switch that stops it.</td><td>Speed, function, or the device itself, on a thing he owns.</td><td>What the update does, and that the owner did not ask for it.</td></tr>
<tr><td class="k">B</td><td>Ends the support the device needs: security updates, spare parts, the online service it depends on.</td><td>A working device that becomes useless or unsafe.</td><td>The date support will end.</td></tr>
<tr><td class="k">C</td><td>Keeps the means of repair to himself: reserved tools, parts that refuse to work unless paired, private manuals.</td><td>The power to fix it himself or through anyone else.</td><td>That he alone holds the key.</td></tr></table>
<p class="small" style="margin-top:16px">In all four, the buyer paid for a life he believed in, and the maker knew more than he did.</p>''')

slide("The map in use", "One product, three mechanisms, three separate verdicts",
'''<div class="card dash"><b>An invented illustration</b> (no company, no data). A maker sells a phone. <b>(1)</b> The battery is glued in and rated for a number of charge cycles that the maker knows ordinary use will exhaust long before the phone&#8217;s other parts age; the box says nothing. <b>(2)</b> The case uses a screw head and a pairing chip that only the maker&#8217;s service centers can obtain. <b>(3)</b> The maker will stop updates on a fixed date, which is printed on the box.</div>
<table style="margin-top:18px"><tr><th style="width:290px">Mechanism</th><th style="width:90px">Leaf</th><th>The test</th><th style="width:250px">Verdict</th></tr>
<tr><td>(1) Sealed battery with an unstated rated life</td><td class="k">A1</td><td>F1&#8211;F3 hold. No disclosure (D2 fails). Not a necessity (D3 fails): the limit could be printed.</td><td><b>Forbidden</b> as sold. Cure: state the rated life.</td></tr>
<tr><td>(2) Parts and tools reserved to the maker</td><td class="k">C</td><td>Not disclosed; no stated safety need; the owner cannot repair what he owns.</td><td><b>Forbidden</b> unless a narrow safety reason is stated.</td></tr>
<tr><td>(3) Updates end on a printed date</td><td class="k">B</td><td>Disclosed before sale; the phone keeps working.</td><td><b>Permitted.</b></td></tr></table>
<p class="small" style="margin-top:14px">The map&#8217;s rule at work: a case with several mechanisms is split, and each mechanism is judged alone. The same maker can be right about (3) and wrong about (1) and (2).</p>''')

slide("The method", "How a moral ruling is proven here",
'''<div class="cols"><div class="col" style="flex:1.35"><ol class="prem">
<li data-n="1">Name the act exactly. <span class="tiny">(Done: the map.)</span></li>
<li data-n="2">State the norms the ruling rests on, each with <b>a reason anyone can check</b>.</li>
<li data-n="3">Show where the classical jurists ruled on the same norm, with their texts and the grade of each text.</li>
<li data-n="4">Apply the norms to each leaf and state the conditions under which they bind.</li>
<li data-n="5">Close the proof: list every possible defense in a <b>complete yes/no tree</b> and answer each.</li>
<li data-n="6">Mark the certainty of each step. The weakest step sets the strength of the whole.</li></ol></div>
<div class="col"><div class="card teal"><div class="label">Why reasons come first</div><p class="small" style="margin:0 0 10px 0">A reader who does not accept a text cannot be moved by it. He can be moved by a premise he already holds.</p><p class="small" style="margin:0">So each norm is first shown to be one that its denier would have to give up everything else to refuse. The classical texts then confirm the norm and fix its details.</p></div>
<div class="card dash" style="margin-top:18px"><div class="label">What a classical jurist does with a new case</div><p class="small" style="margin:0">He finds the decided case that shares the <i class="t">cause</i> (<i class="t">ʿilla</i>) of the ruling, and extends the ruling by analogy (<i class="t">qiyās</i>). A new case needs no new rule, only the old reason.</p></div></div></div>''')

slide("The proof at a glance", "Three facts, three norms, one ruling",
'''<div class="cols" style="gap:26px"><div class="col"><div class="label">Facts of the case</div>
<div class="card" style="margin-bottom:12px"><b>F1</b> The maker knows the limit he put on the product&#8217;s life or repair.</div>
<div class="card" style="margin-bottom:12px"><b>F2</b> The buyer does not know it.</div>
<div class="card"><b>F3</b> The price was set for the life the buyer ordinarily expects.</div></div>
<div class="col"><div class="label">Norms</div>
<div class="card teal" style="margin-bottom:12px"><b>N1 Consent.</b> Wealth passes from one person to another only by informed consent.</div>
<div class="card teal" style="margin-bottom:12px"><b>N2 Harm.</b> No one may gain by another&#8217;s loss without a right.</div>
<div class="card teal" style="margin-bottom:12px"><b>N3 Ownership.</b> The owner alone governs use, repair and disposal.</div>
<div class="card" style="border-color:#8A97A3"><b>N4 Waste.</b> Usable value may not be destroyed for no benefit. <span class="tiny">(support only)</span></div></div>
<div class="col"><div class="label">Rulings</div>
<div class="card amber" style="margin-bottom:12px"><b>R1</b> Concealing the limit is forbidden.</div>
<div class="card amber" style="margin-bottom:12px"><b>R2</b> Changing or disabling a sold device, or blocking its repair, without informed consent is forbidden.</div>
<div class="card amber" style="margin-bottom:12px"><b>R3</b> The one who knows the limit must disclose it.</div>
<div class="card amber"><b>R4</b> The wronged buyer has a remedy.</div></div></div>
<p class="small" style="margin-top:14px">Where F1 to F3 are absent, there is no planned obsolescence and the ruling does not apply. The proof is conditional on the facts, and the facts are checked case by case.</p>''')
