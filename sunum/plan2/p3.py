from lib import *

tree = '<svg viewBox="0 0 1416 560" width="100%">' + DEFS
rows = [("Q1  Is anyone harmed?", "No", "D1  No harm", "“Nobody is hurt.”"),
        ("Q2  Did the buyer agree, knowing the limit?", "Yes", "D2  Consent", "“He accepted the terms.”"),
        ("Q3  Was the limit forced on the maker?", "Yes", "D3  Necessity", "“Batteries age; we have duties.”"),
        ("Q4  Does the maker claim a right to do it?", "Yes", "D4  Entitlement", "“It is our property or our law.”"),
        ("Q5  Does he claim it serves others?", "Yes", "D5  Others’ benefit", "“It funds innovation.”")]
y = 10
for i, (q, lab, leaf, quote) in enumerate(rows):
    tree += svg_node(10, y, 560, 56, [(q, True)], "d")
    tree += svg_line(570, y + 28, 690, y + 28, lab.lower(), True, 596, y + 19)
    tree += svg_node(690, y, 330, 56, [(leaf, True)], "t")
    tree += '<text x="1040" y="%d" font-size="21" fill="#4A5F73" font-style="italic" font-family="Inter,sans-serif">%s</text>' % (y + 35, esc(quote))
    if i < len(rows) - 1:
        tree += svg_line(290, y + 56, 290, y + 94, "no", True, 302, y + 82)
    y += 94
tree += svg_line(290, y - 94 + 56, 290, y + 4, "no", True, 302, y - 12)
tree += svg_node(10, y + 6, 1010, 56, [("No defense remains: a harmful, unagreed, unforced limit that claims no right and serves no one.", True)], "a")
tree += '</svg>'
slide("Closing the exits", "Every defense falls into one of five places", tree,
 "Each question is a yes/no split. A defense must answer &#8220;yes&#8221; at one of Q1&#8211;Q5, or it has no place to stand. Q4 and Q5 are asked in that order, so a defense that claims both a right and a benefit is split into its two claims.")

slide("Closing the exits", "Why the tree is complete: twelve defenses, each placed",
'''<table class="tight" style="font-size:18px"><tr><th style="width:540px">The defense as it is usually spoken</th><th style="width:240px">Where it falls</th><th>Remark</th></tr>
<tr><td>&#8220;Nobody is hurt; he would have replaced it anyway.&#8221;</td><td class="k">D1 No harm</td><td>A guess about a choice that concealment took away.</td></tr>
<tr><td>&#8220;The price was low.&#8221;</td><td class="k">D1 No harm</td><td>A low price lowers a buyer&#8217;s expectation only if he knows.</td></tr>
<tr><td>&#8220;It was in the terms and conditions.&#8221;</td><td class="k">D2 Consent</td><td>Tested by what an ordinary buyer saw and understood.</td></tr>
<tr><td>&#8220;Everyone does it; buyers know.&#8221;</td><td class="k">D2 Consent</td><td>Consent by custom, if the custom is settled and known.</td></tr>
<tr><td>&#8220;He clicked &#8216;accept&#8217; on the update.&#8221;</td><td class="k">D2 Consent</td><td>Consent after the sale.</td></tr>
<tr><td>&#8220;The buyer could have gone elsewhere.&#8221;</td><td class="k">D2 Consent</td><td>Means he was free to refuse; asks whether he knew.</td></tr>
<tr><td>&#8220;Batteries age and security demands it.&#8221;</td><td class="k">D3 Necessity</td><td>Nature and duty.</td></tr>
<tr><td>&#8220;It is our property, our patent, our license.&#8221;</td><td class="k">D4 Entitlement</td><td>A claimed right.</td></tr>
<tr><td>&#8220;It is legal where we sell.&#8221;</td><td class="k">D4 Entitlement</td><td>A permit claimed as a right.</td></tr>
<tr><td>&#8220;It funds innovation, jobs and cheap goods.&#8221;</td><td class="k">D5 Benefit</td><td>A good claimed for others.</td></tr>
<tr><td>&#8220;We never meant harm.&#8221;</td><td class="k" style="color:#4A5F73">Outside the claim</td><td>If it was not a choice, it is not planned; if it was, intent is present (art. 93).</td></tr>
<tr><td>&#8220;A supplier did it.&#8221;</td><td class="k" style="color:#4A5F73">Outside the claim</td><td>If the maker did not know, it is not planned; once he knows and ships it, it is his choice.</td></tr></table>
<p class="small" style="margin-top:8px;font-size:18px"><b>The test of completeness:</b> bring any defense not listed. If it fits none of D1&#8211;D5 and is not a denial that the act was planned, the tree must be extended. None has been found. The shape of defenses (deny the wrong, permit it, excuse it, justify it by a right, justify it by a good) is argued, not counted, so the tree is '''+chip("strong")+'''.</p>''')

slide("Defense 1", "&#8220;Nobody is harmed&#8221;",
'''<table><tr><th style="width:480px">The claim</th><th>The answer</th></tr>
<tr><td><b>&#8220;He would have replaced it anyway.&#8221;</b></td><td>That guesses at a choice which the concealment took from him. A simple test: tell him. If he would buy anyway, telling costs nothing; if he would not, he was harmed.</td></tr>
<tr><td><b>&#8220;The product was cheap.&#8221;</b></td><td>A low price lowers the expectation of a buyer who knows. It cannot turn a belief he holds into the maker&#8217;s smaller delivery. The shortfall formula is proportional at every price.</td></tr>
<tr><td><b>&#8220;It still works for ordinary use.&#8221;</b></td><td>&#8220;Ordinary use&#8221; is then the maker&#8217;s own minimum. Harm is measured against what a buyer ordinarily expects, not against what the maker finds enough.</td></tr>
<tr><td><b>&#8220;New devices are better, so he gains.&#8221;</b></td><td>A better device he must buy does not return the money paid for the old one. A loss is not cancelled by a gain he did not choose.</td></tr></table>
<p style="margin-top:16px">'''+chip("no")+''' <b>Defense 1 fails.</b> It denies the harm that Principles 1 and 2 establish.</p>''')

slide("Defense 2", "&#8220;The buyer agreed&#8221;: the test of consent",
'''<div class="cols"><div class="col" style="flex:1.2"><ol class="prem">
<li data-n="a">Was the limit disclosed before the sale, in plain words, where an ordinary buyer would see it? <b>Yes: consent.</b></li>
<li data-n="b">If not, is it the publicly known norm of this kind of product, so that no ordinary buyer expects more? <b>Yes: consent by custom.</b></li>
<li data-n="c">If not, did the buyer later accept it knowingly, specifically, and with a real option to refuse and keep the device as it was? <b>Yes: consent, for what he knew.</b></li>
<li class="concl" data-n="d">If none: <b>no consent.</b> The limit was concealed.</li></ol></div>
<div class="col"><div class="card teal"><div class="label">Why each test is fair</div>
<p class="small" style="margin:0 0 8px 0"><b>a</b> follows the grain-heap rule: what a buyer cares to see must be placed where he can see it (Muslim 102).</p>
<p class="small" style="margin:0 0 8px 0"><b>b</b> follows Mecelle 41&#8211;45: custom binds when it is settled, prevailing and known.</p>
<p class="small" style="margin:0"><b>c</b> follows N1: consent is to a known thing, freely given.</p></div>
<p class="small" style="margin-top:14px">The burden of showing a, b or c lies on the maker, who holds the facts; the buyer need only show the shortfall. <span class="tiny">(compare Mecelle 76: the proof is on the claimant, and here the maker claims consent)</span></p></div></div>''')

slide("Defense 2", "Hard cases of consent",
'''<table style="font-size:19.5px"><tr><th style="width:430px">The claim</th><th>The answer</th><th style="width:210px">Verdict</th></tr>
<tr><td><b>&#8220;It was in the terms and conditions.&#8221;</b></td><td>A term in pages no ordinary buyer reads, at the moment of buying, is not seen. The test is test a above, not the existence of a document.</td><td>'''+chip("no")+'''</td></tr>
<tr><td><b>&#8220;Everyone does it, so buyers know.&#8221;</b></td><td>Custom counts when settled and known (Mecelle 41&#8211;42). If it is known, there is no deception and the maker is right. If it is not known, universal concealment multiplies the wrong and gives the buyer nowhere to go.</td><td>'''+chip("part", "RIGHT ONLY IF KNOWN")+'''</td></tr>
<tr><td><b>&#8220;He clicked &#8216;accept&#8217; on the update.&#8221;</b></td><td>A yes given to keep what he already owns working is not free. Consent must name what the update does, and refusing must leave his device as it was.</td><td>'''+chip("part", "ONLY IF SPECIFIC AND FREE")+''' '''+chip("probable")+'''</td></tr>
<tr><td><b>&#8220;He bought the budget model.&#8221;</b></td><td>He consented to the lower price he saw. A limit the maker did not state is not part of what a cheaper price tells.</td><td>'''+chip("no")+'''</td></tr>
<tr><td><b>&#8220;The warranty period was stated.&#8221;</b></td><td>A warranty is a promise about repairs, not a statement of how long the product is expected to work. A design that fails just after the warranty is still hidden.</td><td>'''+chip("no")+'''</td></tr>
<tr><td><b>&#8220;He could have bought elsewhere.&#8221;</b></td><td>The question is not whether he could leave. It is whether he knew. A free buyer who does not know has not consented.</td><td>'''+chip("no")+'''</td></tr></table>''')

slide("Defense 3", "&#8220;It was forced on us&#8221;",
'''<table><tr><th style="width:430px">The claim</th><th>The answer</th></tr>
<tr><td><b>Nature:</b> &#8220;Batteries age; materials wear.&#8221;</td><td>Agreed, and outside the claim (the map, N). Necessity can excuse a limit; it never excuses hiding it. A slowdown with an engineering reason, disclosed, is honest; the same slowdown, silent, is the wrong.</td></tr>
<tr><td><b>Duty:</b> &#8220;We are bound by safety and security rules.&#8221;</td><td>A real duty justifies the act only to its measure (Mecelle 22), ends when the excuse ends (23), and does not cancel another&#8217;s right (33). The maker can protect the buyer <i>and</i> tell him, and give him the choice.</td></tr>
<tr><td><b>Cost:</b> &#8220;We cannot support a product forever.&#8221;</td><td>True. Hardship brings ease (Mecelle 17), so the maker may end support. It does not follow that he may disable a working device or close others&#8217; help. He gives notice; he leaves the device working; he does not block those who can repair it.</td></tr></table>
<p style="margin-top:16px">'''+chip("part")+''' <b>Defense 3 saves the limit, not the concealment.</b> Where a limit is genuinely forced, the ruling asks only that the maker disclose it and offer the choice.</p>''')

slide("Defense 4", "&#8220;It is our right&#8221;",
'''<table><tr><th style="width:430px">The claim</th><th>The answer</th></tr>
<tr><td><b>Property:</b> &#8220;We own the software, the design, the brand.&#8221;</td><td>He owns his design. He does not own the buyer&#8217;s device. A right to guard his design is a right over copying, not a right to control a thing already sold (Mecelle 96, 100).</td></tr>
<tr><td><b>Security:</b> &#8220;Locks protect users.&#8221;</td><td>A real security reason can be stated, limited to what it needs, and left to the owner&#8217;s choice. A lock that serves only the maker&#8217;s repair business is not a security reason.</td></tr>
<tr><td><b>Contract:</b> &#8220;He agreed to our license.&#8221;</td><td>Back at Defense 2. A condition counts only if it was known and freely accepted, and the schools void restrictions on the buyer&#8217;s own thing (Principle 3).</td></tr>
<tr><td><b>Law:</b> &#8220;It is legal where we sell.&#8221;</td><td>A permit changes what a court will enforce, not whether the buyer was wronged. The ruling here concerns the act, and a permit is not a reason.</td></tr></table>
<p style="margin-top:16px">'''+chip("no")+''' <b>Defense 4 fails</b> wherever the claimed right is taken from the buyer. Where the maker keeps ownership and says so, the answer is a lease, which is lawful.</p>''')

slide("Defense 5", "&#8220;It serves others&#8221;",
'''<table><tr><th style="width:430px">The claim</th><th>The answer</th></tr>
<tr><td><b>&#8220;It funds innovation.&#8221;</b></td><td>Real innovation sells by being better, openly. And a benefit that is only hoped for does not outweigh a loss that is certain (Mecelle 4: doubt does not remove certainty; 74: a mere imagining is not counted).</td></tr>
<tr><td><b>&#8220;A private harm is tolerated to repel a public harm.&#8221;</b> (Mecelle 26)</td><td>That maxim needs a public harm that is real and a private harm that is the least way to repel it. Planned obsolescence repels none: it adds waste.</td></tr>
<tr><td><b>&#8220;It keeps jobs and prices low.&#8221;</b></td><td>Repelling mischief comes before gaining benefit (Mecelle 30). And gain taken by concealment is not lawful gain, whoever else profits (Qur&#8217;an 4:29; Muslim 101).</td></tr>
<tr><td><b>&#8220;Banning it would slow progress.&#8221;</b></td><td>Whether a ban speeds or slows innovation is an empirical question. The ruling does not depend on its answer, and the ruling forbids concealment, not short-lived products.</td></tr></table>
<p style="margin-top:16px">'''+chip("no")+''' <b>Defense 5 fails.</b> A good for others does not license deceiving this buyer.</p>''')
