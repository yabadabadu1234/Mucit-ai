from lib import *

def qa(q, a, v): return '<div class="qa"><span class="qq">%s</span> %s<br>%s</div>' % (q, '<span class="verdict">%s</span>' % v, a)

slide("The doubt court · 1 of 6", "Doubts about the claim&#8217;s scope",
 qa("1 · &#8220;Doesn&#8217;t this forbid cheap, short-lived products?&#8221;", "No. The ruling forbids hiding the limit, not having one. A short life, stated, is a lawful product, and a cheap one honestly described is a good choice for some buyers.", chip("no")) +
 qa("2 · &#8220;Who decides what a buyer ordinarily expects?&#8221;", "The custom of that kind of product among buyers and merchants (Mecelle 36&#8211;45), together with the maker&#8217;s own statements and advertising. Where custom is unclear, the maker ends the dispute by stating the life.", chip("part")) +
 qa("3 · &#8220;A maker cannot know a product&#8217;s exact life.&#8221;", "He need not state what he cannot know. He must state what he does know: rated cycles, design hours, planned support dates. Ignorance of the unknowable excuses; silence about the known does not.", chip("part")) +
 qa("4 · &#8220;Durability is just a feature the market can price.&#8221;", "Only a disclosed feature can be priced. A buyer cannot put a price on what he cannot see, and the market cannot punish a limit it does not know of.", chip("no")))

slide("The doubt court · 2 of 6", "Doubts about software, security and updates",
 qa("5 · &#8220;Software cannot be supported forever.&#8221;", "True. Hardship brings ease (Mecelle 17), so the maker may end support. He may not switch off a working device or forbid others to help.", chip("part")) +
 qa("6 · &#8220;Security sometimes requires dropping old hardware.&#8221;", "Then he says so, gives the owner the choice, and leaves the device able to run as it was. A real reason can be stated; a hidden one is not a reason.", chip("part")) +
 qa("7 · &#8220;Slowing an old battery protects the phone.&#8221;", "A protective measure is lawful if the owner is told and can choose. Silent, it is the wrong. Disclosed with a switch, it is honest. (Compare the Apple case.)", chip("part")) +
 qa("8 · &#8220;Must every update be approved one by one?&#8221;", "No. A general advance consent to improving updates is a real consent, and the owner can withdraw it. An update that reduces a function needs a specific one. " + chip("probable"), chip("part")))

slide("The doubt court · 3 of 6", "Doubts about proof and intent",
 qa("9 · &#8220;You cannot prove the maker&#8217;s intent.&#8221;", "The ruling attaches to what can be shown: that he knew the limit (tests, design documents, rated lives), that he did not disclose it, and that the buyer lost. Inner motive is not needed. The burden of showing consent lies on the maker, who claims it (Mecelle 76).", chip("no")) +
 qa("10 · &#8220;Perhaps the short life was an accident of cost-cutting.&#8221;", "If the maker did not know, it is not planned and the claim does not apply. Once he learns of it and keeps selling, the choice is his. A cost-cutter who chose cheaper parts knew what he chose.", chip("part")) +
 qa("11 · &#8220;The market will punish cheaters.&#8221;", "A market can punish only what buyers can see. A hidden limit is the one thing they cannot see. The market is blind exactly where the ruling is needed.", chip("no")) +
 qa("12 · &#8220;Doesn&#8217;t intent matter?&#8221;", "It matters for blame and punishment (Mecelle 92&#8211;93; <i class=\"t\">taʿzīr</i>). It does not matter for whether the buyer must be told: that duty binds whoever knows.", chip("part")))

slide("The doubt court · 4 of 6", "Doubts about buyers, markets and contracts",
 qa("13 · &#8220;Customers want a new model every year anyway.&#8221;", "Then telling them costs nothing, and a maker who is sure can say so. The only question is whether they were told.", chip("no")) +
 qa("14 · &#8220;Fashion makes old things feel obsolete.&#8221;", "Fashion changes desire, not the old device. The claim covers acts on the device or on the means of keeping it working. If a maker lies, saying the old device is unsafe when it is not, that lie is deceit, but it is not what this talk is about.", chip("out")) +
 qa("15 · &#8220;Business buyers are sophisticated.&#8221;", "Their expertise makes more defects apparent to them, so the maker&#8217;s duty narrows to what they cannot see. It does not disappear.", chip("part")) +
 qa("16 · &#8220;What about leases and subscriptions?&#8221;", "Lawful as a lease (<i class=\"t\">ijāra</i>), if called a lease and priced as rent. If the buyer pays a price for ownership, the contract is a sale whatever it is called (Mecelle 3).", chip("yes")))

slide("The doubt court · 5 of 6", "Doubts about the use of classical rulings",
 qa("17 · &#8220;Why use classical rulings for a modern problem?&#8221;", "Rulings follow causes, not objects. The cause behind the udder ruling, a false appearance of a quality that sets the price, is present here, so the ruling is extended by analogy. That is the classical method, not a stretch.", chip("no")) +
 qa("18 · &#8220;Isn&#8217;t the harm hadith weak?&#8221;", "Graded differently by different scholars, and this talk says so. But the norm does not rest on that single text: it is a maxim of the Mecelle (19&#8211;20), it matches the Qur&#8217;anic rejection of harm (2:231), and N2 is argued from reason too.", chip("part")) +
 qa("19 · &#8220;May a seller set any condition?&#8221;", "Only conditions that are known and freely accepted, and the schools differ on restrictions on the buyer&#8217;s own property. A hidden condition passes under none of them.", chip("no")) +
 qa("20 · &#8220;Is this just your opinion?&#8221;", "Each step carries its mark. To reject the ruling a reader must reject a named premise or accept a defense; the next-to-last slide lists the cost of each.", chip("no")))

slide("The doubt court · 6 of 6", "Doubts about reach and effect",
 qa("21 · &#8220;You gave the environment so little weight.&#8221;", "On purpose. The proof does not need it. Waste is marked as support only, so a reader who doubts the environmental claims loses nothing.", chip("yes")) +
 qa("22 · &#8220;What if a cartel sets the limit?&#8221;", "The wrong is the same, and wider: buyers had no maker to turn to, so even a pretext of a free alternative fails. (The Phoebus case.)", chip("no")) +
 qa("23 · &#8220;What if the buyer is told, understands, and still buys?&#8221;", "Then the sale is lawful. That is the point: the ruling protects knowledge and choice, not a particular durability.", chip("yes")) +
 qa("24 · &#8220;Does this make every maker a wrongdoer?&#8221;", "No. It makes concealment, remote disabling and closed repair without consent wrongful. A maker who tells the truth and leaves the owner in charge has nothing to answer for.", chip("no")))
