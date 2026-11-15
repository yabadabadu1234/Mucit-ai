import json, urllib.parse, urllib.request, concurrent.futures as cf, sys
# (ad, sınıf, müellif/yıl (hafıza), Crossref sorgusu, bir cümlelik iş)
G = [
 ("Kavram kafesi (Formal Concept Analysis)","kafes","Wille 1982; Ganter & Wille 1999","Restructuring lattice theory: an approach based on hierarchies of concepts","nesne×vasıf tablosundan bütün kavramları ve içerme düzenini çıkarır"),
 ("Kavram haritası (concept map)","grafik","Novak & Gowin 1984","Novak Gowin Learning how to learn concept maps","kavramlar düğüm, bağlayıcı sözcüklü etiketli ok"),
 ("Kavram haritası meta-analizi","kanıt","Schroeder vd. 2018","A Meta-Analysis of National Research: Effects of Teaching Strategies concept mapping","kavram haritası kurmanın okumaya üstünlüğü"),
 ("Yönlü dizilişli grafik çizimi (Sugiyama)","yerleşim","Sugiyama, Tagawa, Toda 1981","Methods for visual understanding of hierarchical system structures","DAG'ı katman katman çizer, kesişmeyi azaltır"),
 ("Yay diyagramı / matris yeniden sıralama","matris","Bertin 1967/1981","Bertin Graphics and Graphic Information Processing","satır sütunu yeniden sıralayarak gruplaşmayı görünür kılar"),
 ("Hazır görsel tasnifi: grafik organizatör meta-analizi","kanıt","Ponce, Mayer, Méndez 2025","Learner-Generated and Instructor-Provided Graphic Organizers as Aids to Learning from Text: A Meta-Analysis","hazır organizatörün okuma ve hatırlamaya etkisi"),
 ("Görsel gösterimlerin bilişsel işleme etkisi","kanıt","McCrudden & Rapp 2015","How Visual Displays Affect Cognitive Processing","dizi, hiyerarşi, matris, kavram haritası ayrımı"),
 ("Önce genel sonra ayrıntı (overview first)","etkileşim","Shneiderman 1996","The eyes have it: a task by data type taxonomy for information visualizations","genel bakış, yakınlaş ve süz, isteğe bağlı ayrıntı"),
 ("Odak+bağlam (fisheye)","etkileşim","Furnas 1986","Generalized fisheye views","odak ayrıntılı, çevre sıkıştırılmış"),
 ("Koni ağacı (3 boyutlu hiyerarşi)","3B","Robertson, Mackinlay, Card 1991","Cone Trees: animated 3D visualizations of hierarchical information","hiyerarşiyi üç boyutta koni olarak döşer"),
 ("Hiperbolik ağaç","ağaç","Lamping, Rao, Pirolli 1995","A focus+context technique based on hyperbolic geometry for visualizing large hierarchies","büyük ağacı hiperbolik düzlemde odaklı gösterir"),
 ("Treemap","hiyerarşi","Johnson & Shneiderman 1991","Tree-maps: a space-filling approach to the visualization of hierarchical information structures","hiyerarşiyi iç içe dikdörtgenlerle gösterir"),
 ("Sunburst / ışınsal doldurma","hiyerarşi","Stasko & Zhang 2000","Focus+context display and navigation techniques for enhancing radial, space-filling hierarchy visualizations","hiyerarşiyi dairesel dilimlerle gösterir"),
 ("Paralel koordinatlar","çok boyut","Inselberg 1985","The plane with parallel coordinates","çok boyutlu veriyi paralel eksenlerde çizgi olarak gösterir"),
 ("UpSet (küme kesişimleri)","küme","Lex vd. 2014","UpSet: Visualization of Intersecting Sets","çok kümenin kesişimlerini matris+çubukla gösterir"),
 ("Euler/Venn çizgesi","küme","Venn 1880","On the diagrammatic and mechanical representation of propositions and reasonings","kümeleri örtüşen bölgelerle gösterir"),
 ("Parallel Sets (kategorik akış)","küme","Kosara, Bendix, Hauser 2006","Parallel Sets: Interactive Exploration and Visual Analysis of Categorical Data","kategorik boyutlar arası akış"),
 ("Sankey şeması","akış","Sankey 1898/ Riehmann 2005","Interactive Sankey diagrams","akışı genişlikle gösterir"),
 ("Kuvvet yönlü yerleşim","yerleşim","Fruchterman & Reingold 1991","Graph drawing by force-directed placement","düğümleri yay ve itme kuvvetiyle yerleştirir"),
 ("Yay (arc) diyagramı","yerleşim","Wattenberg 2002","Arc diagrams: visualizing structure in strings","düğümler doğru üstünde, bağlar yaylar"),
 ("Küçük katlar (small multiples)","karşılaştırma","Tufte 1983","Tufte The Visual Display of Quantitative Information","aynı şemanın birçok kopyasını yan yana koyar"),
 ("Hasse diyagramı / sıralı küme çizimi","sıra","Birkhoff 1940; Hasse 1948","Lattice theory Birkhoff","kısmi düzeni içerme çizgileriyle gösterir"),
 ("Tabanlı sınıflandırma (Ranganathan PMEST)","tasnif","Ranganathan 1933","Ranganathan Colon Classification facet analysis","bir nesneyi bağımsız yönlerle (facet) tarif eder"),
 ("Facet'li gezinme","tasnif","Hearst 2006","Design recommendations for hierarchical faceted search interfaces","kullanıcıya birden çok yönde süzme verir"),
 ("Kavramsal çizgeler","mantık","Sowa 1984","Sowa Conceptual structures information processing in mind and machine","mantığı iki tür düğümlü çizgeyle ifade eder"),
 ("Bilişsel yük kuramı (iç, dış, ilgili yük)","kanıt","Sweller 1988","Cognitive load during problem solving: Effects on learning","öğrenme çizgesini işlenebilir parçalara böler"),
 ("Çoklu gösterim çerçevesi (DeFT)","kanıt","Ainsworth 2006","DeFT: A conceptual framework for considering learning with multiple representations","aynı bilginin birden çok gösterimini birlikte tasarlama"),
 ("Yapı eşleme kuramı","kanıt","Gentner 1983","Structure-mapping: A theoretical framework for analogy","benzetmede ilişki yapısı eşleşir"),
 ("Karşılaştırmalı durumlar (contrasting cases)","kanıt","Alfieri vd. 2013","Learning through case comparisons: A meta-analytic review","iki örneği yan yana koymak öğrenmeyi artırır"),
 ("Bilişsel esneklik kuramı","kanıt","Spiro vd. 1988/1992","Cognitive flexibility theory advanced knowledge acquisition ill-structured domains","aynı konuya farklı yönlerden dönülür"),
 ("Sinyalleme (vurgu) meta-analizi","kanıt","Alpizar, Adesope, Wong 2020","A meta-analysis of signaling principle in multimedia learning environments","vurgu işaretleri öğrenmeyi artırır"),
 ("Alanı bölünmüş dikkat (space contiguity)","kanıt","Schroeder & Cenkci 2018","Spatial Contiguity and Spatial Split-Attention Effects in Multimedia Learning Environments: a Meta-Analysis","yazı resmin yanına konunca öğrenme artar"),
 ("Sunum öğrenme: grafik organizatör (Bellack, Ausubel)","kanıt","Ausubel 1960","The use of advance organizers in the learning and retention of meaningful verbal material","ön düzenleyici metin"),
 ("Düşünme haritaları (Hyerle)","grafik","Hyerle 1996","Hyerle Thinking maps visual tools for learning","sekiz kalıplı görsel düşünme aracı"),
 ("Zihin haritası (mind map)","grafik","Buzan 1974","Buzan Use your head mind map","merkezden dallanan renkli notlar"),
 ("Anlamsal ağ","mantık","Quillian 1968","Semantic memory Quillian","kavramlar arası etiketli bağlar"),
 ("Çerçeveler (frames)","mantık","Minsky 1974","A framework for representing knowledge","kavramı yuvalı şablonla tarif eder"),
 ("OWL / betimleme mantıkları","mantık","Baader vd. 2003","The Description Logic Handbook","kavram ve rolleri biçimsel mantıkla tarif eder"),
 ("Argüman haritası","mantık","Toulmin 1958; Walton","The uses of argument Toulmin","iddia, delil, kefil, itiraz şeması"),
 ("Wigmore delil çizelgesi","mantık","Wigmore 1913","Wigmore The Principles of Judicial Proof","delil zincirini simgelerle çizer"),
 ("Hipergraf (çok üyeli bağ)","grafik","Berge 1973","Berge Hypergraphs combinatorics of finite sets","bir bağ ikiden çok düğümü birleştirir"),
 ("Çok katmanlı ağlar","grafik","Kivelä vd. 2014","Multilayer networks","aynı düğümleri farklı bağ türlerinde katmanlı gösterir"),
 ("Dairesel bağ şeması (chord)","akış","Krzywinski 2009","Circos: An information aesthetic for comparative genomics","daire üstünde ikili ilişkiler"),
 ("Bağlam içinde özet bakış (Overview+Detail, Focus+Context, Zooming meta-analizi)","kanıt","Cockburn, Karlson, Bederson 2008","A review of overview+detail, zooming, and focus+context interfaces","genel+ayrıntı tasarımlarının karşılaştırması"),
 ("Görsel analiz görev tipolojisi (Munzner what-why-how)","çerçeve","Munzner 2014","Visualization Analysis and Design","veri-görev-iz tasarımını sistemleştirir"),
 ("Dünya haritası gibi ölçekli gezinme (zoomable UI, Pad++)","etkileşim","Bederson & Hollan 1994","Pad++: a zooming graphical interface for exploring alternate interface physics","sonsuz ölçekli yüzey, yakınlaşınca ayrıntı"),
 ("Silindirik/ışınsal çok katmanlı hiyerarşi (InfoCylinder)","3B","Carrière & Kazman 1995","Interacting with huge hierarchies: beyond cone trees","silindir üstünde hiyerarşi"),
 ("Alan-doldurucu 3B çizge (Information Cube)","3B","Rekimoto & Green 1993","The information cube: using transparency in 3D information visualization","iç içe saydam küpler"),
 ("Üç boyutlu ağ çizimi çalışması","3B","Ware & Franck 1996","Evaluating stereo and motion cues for visualizing information nets in three dimensions","3B'nin 2B'ye faydası"),
]
def sor(g):
    q = urllib.parse.quote(g[3])
    u = f"https://api.crossref.org/works?query.bibliographic={q}&rows=1&select=DOI,title,issued,author,container-title"
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40)
        it = json.load(r)["message"]["items"]
        if not it: return None
        m = it[0]
        return dict(doi=m["DOI"], baslik=(m.get("title") or [""])[0], yil=(m.get("issued", {}).get("date-parts") or [[None]])[0][0],
                    yazar=[a.get("family") for a in m.get("author", [])][:3], yayin=(m.get("container-title") or [""])[0])
    except Exception as e:
        return dict(hata=str(e)[:80])
with cf.ThreadPoolExecutor(8) as ex:
    sonuc = list(ex.map(sor, G))
out = []
for g, s in zip(G, sonuc):
    out.append(dict(ad=g[0], sinif=g[1], hatira=g[2], sorgu=g[3], is_=g[4], crossref=s))
json.dump(out, open("tara_ham.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for o in out:
    s = o["crossref"] or {}
    print(o["ad"][:44].ljust(46), (s.get("yil") or "-"), (s.get("baslik") or s.get("hata") or "yok")[:70])
