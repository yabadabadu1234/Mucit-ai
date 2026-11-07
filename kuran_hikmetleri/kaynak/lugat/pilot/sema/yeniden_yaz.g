BEGIN {
  string t, m, y, k, kes, sik, ad;
  node_t nt, nm;
  edge_t e, f, ne;
  node_t d;
}
BEG_G {
  t = gsub(gsub(ARGV[0], "_", " "), "~", "'");
  m = gsub(gsub(ARGV[1], "_", " "), "~", "'");
  y = gsub(gsub(ARGV[2], "_", " "), "~", "'");
  k = gsub(gsub(ARGV[3], "_", " "), "~", "'");
  kes = ARGV[4];
  sik = ARGV[5];
  ad = gsub(gsub(ARGV[6], "_", " "), "~", "'");
  $G.label = html($G, sprintf("<B>%s</B>", ad));
  $G.labelloc = "t";
  $G.fontname = "Helvetica";
  nt = isNode($G, "T");
  nm = isNode($G, "M");
  nt.label = html($G, sprintf("<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"7\"><TR><TD BGCOLOR=\"#ccfbf1\"><B>T</B> tutan</TD></TR><TR><TD>%s</TD></TR></TABLE>", t));
  nm.label = html($G, sprintf("<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"7\"><TR><TD BGCOLOR=\"#fde68a\"><B>M</B> tutulan</TD></TR><TR><TD>%s</TD></TR></TABLE>", m));
  d = isNode($G, "p");
  d.label = html($G, sprintf("<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"7\"><TR><TD BGCOLOR=\"#e2e8f0\"><B>p</B> yer</TD></TR><TR><TD>%s</TD></TR></TABLE>", y));
  d = isNode($G, "K");
  d.label = html($G, sprintf("<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"7\"><TR><TD BGCOLOR=\"#fecaca\"><B>K</B> çeken</TD></TR><TR><TD>%s</TD></TR></TABLE>", k));
  if (t == m) {
    for (e = fstin(nm); e; e = f) {
      f = nxtin(e);
      if (e.tail.name != "T") { ne = edge(e.tail, nt, ""); copyA(e, ne); }
    }
    for (e = fstout(nm); e; e = f) {
      f = nxtout(e);
      ne = edge(nt, e.head, ""); copyA(e, ne);
    }
    e = isEdge(nt, nm, "");
    if (e) { ne = edge(nt, nt, ""); copyA(e, ne); ne.label = "kendini tutar"; }
    delete($G, nm);
    nt.label = html($G, sprintf("<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"7\"><TR><TD BGCOLOR=\"#ccfbf1\"><B>T = M</B></TD></TR><TR><TD>%s</TD></TR></TABLE>", t));
  }
  nt = isNode($G, "T");
  nm = isNode($G, "M");
  if (!nm) nm = nt;
  if (kes == "1") {
    for (e = fstout(nt); e; e = nxtout(e)) {
      if (e.head == nm && e.label == "tutar") { e.style = "dashed"; e.color = "#b91c1c"; e.fontcolor = "#b91c1c"; e.label = "tutamaz"; }
      if (e.head == nm && e.label == "kendini tutar") { e.style = "dashed"; e.color = "#b91c1c"; e.fontcolor = "#b91c1c"; e.label = "tutamaz"; }
    }
    d = isNode($G, "p");
    for (e = fstout(nm); e; e = nxtout(e)) {
      if (e.head == d) { e.label = "p'den ayrılır"; e.color = "#b91c1c"; e.fontcolor = "#b91c1c"; e.style = "dotted"; }
    }
  }
  if (sik == "p") {
    d = isNode($G, "p");
    e = edge(nm, d, "sikayet");
    e.label = "şikâyet p'ye döner"; e.color = "#0f766e"; e.fontcolor = "#0f766e"; e.penwidth = 2.2; e.constraint = "false";
  }
  if (sik == "o") {
    d = node($G, "O");
    d.shape = "plain";
    d.label = html($G, "<TABLE BORDER=\"0\" CELLBORDER=\"1\" CELLSPACING=\"0\" CELLPADDING=\"7\"><TR><TD BGCOLOR=\"#fecaca\"><B>o</B> başkası</TD></TR></TABLE>");
    e = edge(nm, d, "sikayet");
    e.label = "şikâyet başkasına akar"; e.color = "#b91c1c"; e.fontcolor = "#b91c1c"; e.penwidth = 2.2;
  }
}
