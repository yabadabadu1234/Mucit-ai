import json, html, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent

M = 'm'
W = 'w'
nodes = {}
order_children = {}


def mana(i, metin, ebeveyn, sebep='', renk='esas'):
    nodes[i] = dict(id=i, tur=M, metin=metin, ebeveyn=list(ebeveyn), sebep=sebep, renk=renk)


def kelime(i, ar, tr, tag, ebeveyn, kuran=''):
    nodes[i] = dict(id=i, tur=W, ar=ar, tr=tr, tag=tag, kuran=kuran, ebeveyn=list(ebeveyn), renk=None)


mana('E', 'ham maddeyi, murad edilen belli bir şey olsun diye ölçüp biçerek hazırlamak', [], renk='esas')
mana('A', 'ölçüp biçmek', ['E'], 'çünkü hazırlamanın ilk işi ölçmektir; ölçülmeden kesilmez', 'a')
mana('B', 'düzgün ve pürüzsüz kılmak', ['E'], 'çünkü ham maddeyi murada uydurmak onu eğrilikten ve pürüzden arındırmaktır', 'b')
mana('C', 'ölçülüp ayrılmış pay', ['E'], 'çünkü bir iş için ayrılan şey, o iş için ölçülüp hazırlanmış paydır', 'c')
mana('H', 'hazırlanmış olduğu işe yakışmak', ['E'], 'çünkü ölçülüp hazırlanan şey hazırlandığı işe yakışır', 'h')

mana('D', 'yaratmak, var etmek', ['A'], 'çünkü ölçüp biçilen şey tamamlanınca meydana gelmiş olur', 'a')
mana('N', 'ölçülüp düzlenerek şekli belirmiş olmak', ['A', 'B'], 'çünkü hem ölçüp biçilen hem düzlenen şeyin şekli belli olur', 'ab')
mana('F', 'eskimek, aşınmak', ['B'], 'çünkü aşınan şey sürtülür, yüzeyi düzleşip yumuşar', 'b')
mana('G', 'yumuşatıp hoş kılmak (koku sürmek)', ['B'], 'çünkü sürülen koku kabalığı giderir, şeyi kabule şayan kılar', 'b')

mana('J', 'yaratılmış olan', ['D'], 'çünkü yaratma fiilinin sonucu yaratılmıştır', 'a')
mana('K', 'yaradılıştaki hâl ve suret', ['D'], 'çünkü her yaratılan, bir yapı ve hâl üzere yaratılmıştır', 'a')
mana('L', 'uydurmak', ['D'], 'çünkü olmayan sözü var göstermek, yaratmanın dille taklididir', 'a')
mana('U', 'huy', ['K'], 'çünkü yaradılışta verilen iç hâl, kişinin huyu olur', 'a')
mana('X', 'ahlâk', ['U'], 'çünkü huy yerleşip çoğalınca bir düzen ve ilim olur', 'a')
mana('Y', 'öfkelenmek', ['U'], 'çünkü huyun taşması öfkedir', 'a')
mana('Z', 'olmayan huyu takınmak', ['U'], 'çünkü başka huyu kendine yüklenmek, huyu giyinmektir', 'a')

kelime('w_A1', 'خَلَقَ', 'ölçüp biçti (deri)', 'fiil', ['A'])
kelime('w_C1', 'خَلَاق', 'nasip, pay', 'isim', ['C'], '★6')
kelime('w_H1', 'خَلِيق', 'lâyık', 'sıfat', ['H'])
kelime('w_H2', 'أَخْلَق', 'daha lâyık', 'tafdîl', ['H'])
kelime('w_H3', 'خَلُقَ', 'yaraştı', 'fiil', ['H'])
kelime('w_H4', 'اِخْلَوْلَقَ', 'hazırlandı, olmaya yakın', 'fiil', ['H'])
kelime('w_D1', 'خَلَقَ', 'yarattı', 'fiil', ['D'], '★184')
kelime('w_D2', 'خَلْق', 'yaratma', 'masdar', ['D'], '★52')
kelime('w_D3', 'خَالِق', 'yaratan', 'fâil', ['D'], '★12')
kelime('w_D4', 'خَلَّاق', 'çok yaratan', 'mübalağa', ['D'], '★2')
kelime('w_D5', 'تَخْلِيق', 'yaratma, birleştirip yapma', 'masdar', ['D'])
kelime('w_J1', 'مَخْلُوق', 'yaratılmış', 'mef‘ûl', ['J'])
kelime('w_J2', 'مَخْلُوقَات', 'yaratılmışlar', 'çoğul', ['J'])
kelime('w_J3', 'خَلْق', 'halk, insanlar', 'isim', ['J'], '★')
kelime('w_J4', 'خَلِيقَة', 'mahlûkat', 'isim', ['J'])
kelime('w_J5', 'مَخْلُوقِيَّة', 'yaratılmışlık', 'sınâî', ['J'])
kelime('w_K1', 'خِلْقَة', 'yaradılış, suret', 'isim', ['K'])
kelime('w_K2', 'خِلْقِيّ', 'yaradılıştan olan', 'mensûb', ['K'])
kelime('w_U1', 'خُلُق', 'huy', 'isim', ['U'], '★2')
kelime('w_U2', 'خَلُوق', 'huyu sağlam', 'sıfat', ['U'])
kelime('w_U3', 'خَلِيقَة', 'mizaç', 'isim', ['U'])
kelime('w_X1', 'أَخْلَاق', 'ahlâk', 'çoğul', ['X'])
kelime('w_X2', 'أَخْلَاقِيّ', 'ahlâkî', 'mensûb', ['X'])
kelime('w_X3', 'أَخْلَاقِيَّة', 'ahlâkîlik', 'sınâî', ['X'])
kelime('w_Y1', 'تَخَلَّقَ', 'öfkelendi', 'fiil', ['Y'])
kelime('w_Z1', 'تَخَلَّقَ', 'huy edindi, takındı', 'fiil', ['Z'])
kelime('w_L1', 'خَلَقَ', 'uydurdu (söz, iftira)', 'fiil', ['L'], '★')
kelime('w_L2', 'اِخْتَلَقَ', 'uydurdu', 'fiil', ['L'])
kelime('w_L3', 'اِخْتِلَاق', 'uydurma', 'masdar', ['L'], '★1')
kelime('w_L4', 'مُخْتَلَق', 'uydurulmuş', 'mef‘ûl', ['L'])
kelime('w_L5', 'مُخْتَلِق', 'uyduran', 'fâil', ['L'])
kelime('w_L6', 'تَخَلَّقَ', 'uydurdu', 'fiil', ['L'])
kelime('w_N1', 'مُخَلَّق', 'şekli belirmiş', 'mef‘ûl', ['N'], '★2')
kelime('w_N2', 'سَهْم مُخَلَّق', 'düzlenmiş ok', 'terkip', ['N'])
kelime('w_B1', 'أَخْلَق', 'düz, pürüzsüz', 'sıfat', ['B'])
kelime('w_B2', 'خَلْقَاء', 'düz kaya', 'müennes', ['B'])
kelime('w_B3', 'خَلَائِق', 'kuyu başı düz taşları', 'çoğul', ['B'])
kelime('w_F1', 'خَلِقَ', 'eskidi', 'fiil', ['F'])
kelime('w_F2', 'أَخْلَقَ', 'eskitti', 'fiil', ['F'])
kelime('w_F3', 'خَلَق', 'eski, yıpranmış', 'sıfat', ['F'])
kelime('w_F4', 'خُلْقَان', 'eski şeyler, paçavra', 'çoğul', ['F'])
kelime('w_F5', 'خُلُوقَة', 'eskilik', 'masdar', ['F'])
kelime('w_F6', 'اِخْلَوْلَقَ', 'eskidi (elbise)', 'fiil', ['F'])
kelime('w_G1', 'خَلُوق', 'safranlı ıtır', 'isim', ['G'])
kelime('w_G2', 'خَلَّقَ', 'kokuladı', 'fiil', ['G'])
kelime('w_G3', 'مُخَلَّق', 'kokulanmış', 'mef‘ûl', ['G'])

mana('R2', 'kök dışı: ödünç söz', [], renk='dis')
kelime('w_R21', 'خِلْقِين', 'kazan (Yunancadan)', 'isim', ['R2'])

