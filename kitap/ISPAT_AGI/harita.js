const USUL_RENK={akıl:'#3a7bd5',haber:'#c46a00',duyu:'#2e9e6a',birleşik:'#8e5bd6',Fârâbî:'#c23b7a',müdafaa:'#0f8f9e',tanım:'#9a9a1f',tenbih:'#808080',aday:'#808080'};
const USUL_GRUP=Object.fromEntries(D.usul.map(u=>[u.id,u.grup]));
const TUR_SIRA=['evveliyyat','musahede','tanim','mantik','turetilmis'];
const TUR_AD={evveliyyat:'Evveliyyât',musahede:'Müşâhede',tanim:'Tanım',mantik:'Mantık',turetilmis:'Türetilmiş'};

function dunyaKur(){
  const nodes=[],map={},blocks=[];
  const BW=2300,BH=1900,GAP=200,COLS=6,X0=3000;
  const ekle=n=>{n.in=[];n.out=[];nodes.push(n);map[n.k]=n;return n};
  const H=Math.ceil(D.soru.length/COLS)*(BH+GAP)+GAP;
  const grup={};D.onerme.forEach(o=>(grup[o.tur]=grup[o.tur]||[]).push(o));
  TUR_SIRA.forEach((t,i)=>{
    (grup[t]||[]).sort((a,b)=>(a.aile||'~').localeCompare(b.aile||'~')||a.id.localeCompare(b.id)).forEach((o,j)=>{
      ekle({k:'o:'+o.id,t:'o',id:o.id,x:260+i*500,y:420+j*120,r:26,zayif:o.zayif,veri:o});
    });
  });
  const sutunBas=TUR_SIRA.map((t,i)=>({x:60+i*500,ad:TUR_AD[t]}));
  D.soru.forEach((s,i)=>{
    const bx=X0+(i%COLS)*(BW+GAP),by=GAP+Math.floor(i/COLS)*(BH+GAP);
    const hs=D.hucre.filter(x=>x.soru===s.id);
    blocks.push({id:s.id,ad:s.ad,x:bx,y:by,w:BW,h:BH,soru:s,hucreler:hs});
    hs.forEach((hc,ci)=>{
      const cx=bx+150+ci*430,cy=by+300;
      ekle({k:'h:'+hc.id,t:'h',id:hc.id,x:cx,y:cy,w:180,h:70,veri:hc});
      const pl=D.ispat.filter(p=>p.hucre===hc.id).sort((a,b)=>(a.tur==='direct'?0:1)-(b.tur==='direct'?0:1)||a.id.localeCompare(b.id));
      pl.forEach((p,k)=>{
        ekle({k:'p:'+p.id,t:'p',id:p.id,x:cx+20+(k%4)*44,y:cy+170+Math.floor(k/4)*66,r:14,veri:p,renk:USUL_RENK[USUL_GRUP[p.usul]]||'#808080'});
      });
    });
  });
  const edges=[];
  const bagla=(a,b,renk,tur)=>{
    if(!a||!b)return;
    const e={a,b,renk,tur};edges.push(e);a.out.push(e);b.in.push(e);
  };
  D.ispat.forEach(p=>{
    const hub=map['p:'+p.id];if(!hub)return;
    const renk=hub.renk;
    p.prem.forEach(pr=>{
      let t;
      if(pr.startsWith('H:')||pr.startsWith('D:'))t=map['h:'+pr.slice(2)];
      else if(pr.startsWith('P:'))t=map['p:'+pr.slice(2)];
      else t=map['o:'+pr];
      bagla(t,hub,renk,'dayanak');
    });
    bagla(hub,map['h:'+p.hucre],renk,'sonuc');
  });
  const W=X0+COLS*(BW+GAP),GS=400,grid={};
  nodes.forEach(n=>{
    const cx=n.t==='h'?n.x+n.w/2:n.x,cy=n.t==='h'?n.y+n.h/2:n.y;
    n.cx=cx;n.cy=cy;
    const key=Math.floor(cx/GS)+','+Math.floor(cy/GS);
    (grid[key]=grid[key]||[]).push(n);
  });
  return {nodes,map,blocks,edges,W,H,GS,grid,sutunBas};
}

function odakKumesi(d,key,derin){
  const up=new Set([key]),upE=new Set(),dn=new Set([key]),dnE=new Set();
  let kat=[key];
  for(let i=0;i<derin&&kat.length;i++){
    const yeni=[];
    kat.forEach(k=>d.map[k].in.forEach(e=>{upE.add(e);if(!up.has(e.a.k)){up.add(e.a.k);yeni.push(e.a.k)}}));
    kat=yeni;
  }
  kat=[key];
  for(let i=0;i<derin&&kat.length;i++){
    const yeni=[];
    kat.forEach(k=>d.map[k].out.forEach(e=>{dnE.add(e);if(!dn.has(e.b.k)){dn.add(e.b.k);yeni.push(e.b.k)}}));
    kat=yeni;
  }
  return {up,upE,dn,dnE,hepsi:new Set([...up,...dn])};
}

function agSayfasi(){
  const r=sayfalar.ag;
  const d=dunyaKur();
  r.append(h('h2',null,'İspat ağı haritası'),
    h('p',{class:'alt'},'Harita sürüklenerek gezilir, tekerlekle (veya iki parmakla) yakınlaşılır. Yalnız ekranda görünen kısım çizilir. Bir düğüme tıklayınca odak açılır: mavi oklar o düğümün dayandığı her şeyi (öncüller, ispatlar, hücreler), turuncu oklar ondan türeyen her şeyi gösterir; geri kalan sönükleşir. Kare = hücre, küçük daire = ispat (renk usul grubu), büyük daire = öncül (kırmızı kenar = zayıf halka).'));
  const kap=h('div',{class:'harita-kap'});
  const cv=h('canvas',{class:'harita'});
  const mini=h('canvas',{class:'mini'});
  const ipucu=h('div',{class:'ipucu',hidden:true});
  const panel=h('div',{class:'harita-panel'});
  const ara=h('input',{type:'search',placeholder:'Düğüm ara: Q02.c1, imkân, tercihsiz…',class:'harita-ara'});
  const sonuc=h('div',{class:'harita-sonuc',hidden:true});
  const mod=h('select',{onchange:()=>cizIste()},h('option',{value:'yakin'},'Kenarlar: yakın olanlar'),h('option',{value:'odak'},'Kenarlar: yalnız odakta'),h('option',{value:'hepsi'},'Kenarlar: görünen hepsi'));
  const derin=h('select',{onchange:()=>{if(secili)odaklan(secili)}},h('option',{value:'1'},'Odak derinliği: 1 adım'),h('option',{value:'2',selected:'selected'},'Odak derinliği: 2 adım'),h('option',{value:'3'},'Odak derinliği: 3 adım'),h('option',{value:'99'},'Odak derinliği: hepsi'));
  const bar=h('div',{class:'harita-bar'},ara,mod,derin,
    h('button',{onclick:()=>sigdir(0,0,d.W,d.H)},'Hepsini sığdır'),
    h('button',{onclick:()=>{if(odak)odagiSigdir()}},'Odağı sığdır'),
    h('button',{onclick:()=>odagiTemizle()},'Odağı temizle'));
  const lej=h('div',{class:'harita-lej'},Object.entries(USUL_RENK).filter(([k])=>k!=='aday').map(([k,v])=>h('span',null,h('i',{style:'background:'+v}),k)));
  kap.append(cv,mini,ipucu,panel);
  r.append(bar,sonuc,kap,lej);

  const ctx=cv.getContext('2d'),mctx=mini.getContext('2d');
  const view={x:0,y:0,s:0.05};
  let cw=0,ch=0,dpr=1,odak=null,secili=null,bekle=false,hover=null,anim=null;

  function boyut(){
    dpr=window.devicePixelRatio||1;
    cw=kap.clientWidth;ch=kap.clientHeight;
    cv.width=cw*dpr;cv.height=ch*dpr;cv.style.width=cw+'px';cv.style.height=ch+'px';
    const mw=170,mh=Math.round(170*d.H/d.W);
    mini.width=mw*dpr;mini.height=mh*dpr;mini.style.width=mw+'px';mini.style.height=mh+'px';
  }
  function sigdir(x,y,w,hh,hizli){
    if(!cw||!ch)return;
    const s=Math.min(cw/(w*1.08),ch/(hh*1.08));
    gotoView({x:x-(cw/s-w)/2,y:y-(ch/s-hh)/2,s},hizli);
  }
  function gotoView(t,hizli){
    if(hizli){view.x=t.x;view.y=t.y;view.s=t.s;cizIste();return}
    const b={x:view.x,y:view.y,s:view.s},t0=performance.now();
    const ls=Math.log(b.s),lt=Math.log(t.s);
    if(anim)cancelAnimationFrame(anim);
    const adim=now=>{
      let u=Math.min(1,(now-t0)/450);u=u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2;
      const s=Math.exp(ls+(lt-ls)*u);
      const cxw=(b.x+cw/b.s/2)*(1-u)+(t.x+cw/t.s/2)*u,cyw=(b.y+ch/b.s/2)*(1-u)+(t.y+ch/t.s/2)*u;
      view.s=s;view.x=cxw-cw/s/2;view.y=cyw-ch/s/2;cizIste();
      if(u<1)anim=requestAnimationFrame(adim);
    };
    anim=requestAnimationFrame(adim);
  }
  function odagiSigdir(){
    if(!odak)return;
    let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
    odak.hepsi.forEach(k=>{const n=d.map[k];const w=n.t==='h'?n.w:0,hh=n.t==='h'?n.h:0;x0=Math.min(x0,n.x-(n.r||0));y0=Math.min(y0,n.y-(n.r||0));x1=Math.max(x1,n.x+w+(n.r||0));y1=Math.max(y1,n.y+hh+(n.r||0))});
    sigdir(x0-100,y0-100,x1-x0+200,y1-y0+200);
  }
  function odaklan(k){odak=odakKumesi(d,k,Number(derin.value));secili=k;panelYaz(k);cizIste()}
  function odagiTemizle(){odak=null;secili=null;panel.replaceChildren();panel.classList.remove('acik');cizIste()}
  function cizIste(){if(bekle)return;bekle=true;requestAnimationFrame(()=>{bekle=false;ciz()})}

  function renkler(){
    const st=getComputedStyle(document.documentElement);
    const g=n=>st.getPropertyValue(n).trim();
    return {bg:g('--bg'),panel:g('--panel'),ink:g('--ink'),soft:g('--soft'),line:g('--line'),accent:g('--accent'),dogru:g('--dogru-bg'),yanlis:g('--yanlis-bg'),ihtilaf:g('--ihtilaf-bg'),dogruK:g('--dogru'),yanlisK:g('--yanlis'),ihtilafK:g('--ihtilaf'),zan:g('--zan')};
  }
  function gorunen(){
    const s=view.s,x0=view.x,y0=view.y,x1=x0+cw/s,y1=y0+ch/s,GS=d.GS;
    const out=[];
    for(let gx=Math.floor((x0-250)/GS);gx<=Math.floor((x1+250)/GS);gx++)for(let gy=Math.floor((y0-250)/GS);gy<=Math.floor((y1+250)/GS);gy++){
      const a=d.grid[gx+','+gy];if(a)for(const n of a)out.push(n);
    }
    return out;
  }
  function kisalt(t,n){return t.length>n?t.slice(0,n-1)+'…':t}
  function sar(c,metin,x,y,w,lh,maks){
    const kel=metin.split(' ');let satir='',say=0;
    for(let i=0;i<kel.length;i++){
      const dene=satir?satir+' '+kel[i]:kel[i];
      if(c.measureText(dene).width>w&&satir){
        say++;
        if(say>=maks){c.fillText(satir+'…',x,y+(say-1)*lh);return}
        c.fillText(satir,x,y+(say-1)*lh);satir=kel[i];
      }else satir=dene;
    }
    c.fillText(satir,x,y+say*lh);
  }
  function oklu(a,b,renk,kalin,alfa,bukum){
    const c=ctx;
    const dx=b.cx-a.cx,dy=b.cy-a.cy,len=Math.hypot(dx,dy)||1;
    const nx=-dy/len,ny=dx/len,off=bukum*len*0.12;
    const mx=(a.cx+b.cx)/2+nx*off,my=(a.cy+b.cy)/2+ny*off;
    c.globalAlpha=alfa;c.strokeStyle=renk;c.lineWidth=kalin;
    c.beginPath();c.moveTo(a.cx,a.cy);c.quadraticCurveTo(mx,my,b.cx,b.cy);c.stroke();
    const t=0.88,px=(1-t)*(1-t)*a.cx+2*(1-t)*t*mx+t*t*b.cx,py=(1-t)*(1-t)*a.cy+2*(1-t)*t*my+t*t*b.cy;
    const tx=2*(1-t)*(mx-a.cx)+2*t*(b.cx-mx),ty=2*(1-t)*(my-a.cy)+2*t*(b.cy-my),tl=Math.hypot(tx,ty)||1;
    const ux=tx/tl,uy=ty/tl,as=Math.max(8/view.s,kalin*4);
    c.fillStyle=renk;c.beginPath();c.moveTo(px+ux*as,py+uy*as);c.lineTo(px-ux*as*0.6+uy*as*0.5,py-uy*as*0.6-ux*as*0.5);c.lineTo(px-ux*as*0.6-uy*as*0.5,py-uy*as*0.6+ux*as*0.5);c.closePath();c.fill();
  }

  function ciz(){
    const R=renkler(),s=view.s;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    ctx.fillStyle=R.bg;ctx.fillRect(0,0,cw,ch);
    ctx.save();ctx.scale(s,s);ctx.translate(-view.x,-view.y);
    const x0=view.x,y0=view.y,x1=x0+cw/s,y1=y0+ch/s;
    const kesisir=(x,y,w,hh)=>x<x1&&x+w>x0&&y<y1&&y+hh>y0;
    const sonukluk=odak?0.16:1;
    ctx.textBaseline='middle';
    if(kesisir(0,0,3000,d.H)){
      ctx.fillStyle=R.panel;ctx.strokeStyle=R.line;ctx.lineWidth=2/s;
      ctx.fillRect(40,40,2900,d.H-80);ctx.strokeRect(40,40,2900,d.H-80);
      ctx.fillStyle=R.ink;ctx.font='600 150px "Source Serif 4",serif';ctx.textAlign='left';
      ctx.globalAlpha=Math.min(1,0.25+0.5/(s*10));
      ctx.fillText('ÖNCÜLLER',140,200);ctx.globalAlpha=1;
      ctx.font='600 46px "IBM Plex Sans",sans-serif';ctx.fillStyle=R.soft;
      d.sutunBas.forEach(b=>ctx.fillText(b.ad,b.x+200,330));
    }
    d.blocks.forEach(b=>{
      if(!kesisir(b.x,b.y,b.w,b.h))return;
      ctx.globalAlpha=1;
      ctx.fillStyle=R.panel;ctx.strokeStyle=R.line;ctx.lineWidth=2/s;
      ctx.fillRect(b.x,b.y,b.w,b.h);ctx.strokeRect(b.x,b.y,b.w,b.h);
      ctx.fillStyle=R.ink;ctx.textAlign='left';
      ctx.font='600 '+(s<0.12?120:70)+'px "Source Serif 4",serif';
      ctx.globalAlpha=odak?0.5:1;
      ctx.fillText(b.id,b.x+60,b.y+110);
      if(s>=0.06){ctx.font='500 52px "IBM Plex Sans",sans-serif';ctx.fillStyle=R.soft;ctx.fillText(kisalt(b.ad,38),b.x+60,b.y+200)}
      ctx.globalAlpha=1;
    });
    const gor=gorunen();
    const kenarMod=mod.value;
    let kenarSay=0;
    if(odak){
      const cizE=(E,renk)=>E.forEach(e=>{oklu(e.a,e.b,renk,2.4/s,0.8,(e.a.cx>e.b.cx?1:-1)*(1+(e.tur==='sonuc'?0:0.5)))});
      ctx.lineCap='round';
      cizE(odak.upE,'#2f6fdd');cizE(odak.dnE,'#e0780f');kenarSay=odak.upE.size+odak.dnE.size;
    }else if(kenarMod!=='odak'&&s>=0.12){
      const limit=kenarMod==='hepsi'?7000:2500,maxUz=kenarMod==='hepsi'?1e9:0.9*cw/s;
      const gorKeys=new Set(gor.map(n=>n.k));
      const cizildi=new Set();
      for(const n of gor){
        if(n.t!=='p')continue;
        for(const e of [...n.in,...n.out]){
          if(cizildi.has(e)||kenarSay>=limit)continue;
          cizildi.add(e);
          const uz=Math.hypot(e.a.cx-e.b.cx,e.a.cy-e.b.cy);
          if(uz>maxUz)continue;
          oklu(e.a,e.b,e.renk,(s>1?1.6:2.4)/s,0.5,(e.a.cx>e.b.cx?1:-1));kenarSay++;
        }
      }
    }
    ctx.globalAlpha=1;
    let cizilen=0;
    for(const n of gor){
      const soluk=odak&&!odak.hepsi.has(n.k);
      ctx.globalAlpha=soluk?sonukluk:1;
      if(n.t==='h'){
        if(!kesisir(n.x,n.y,n.w,n.h))continue;
        cizilen++;
        const hc=n.veri;
        ctx.fillStyle=hc.hukum==='DOĞRU'?R.dogru:(hc.hukum==='YANLIŞ'?R.yanlis:R.ihtilaf);
        ctx.strokeStyle=n.k===secili?R.accent:(hc.hukum==='DOĞRU'?R.dogruK:(hc.hukum==='YANLIŞ'?R.yanlisK:R.ihtilafK));
        ctx.lineWidth=(n.k===secili?6:2)/s;
        ctx.fillRect(n.x,n.y,n.w,n.h);ctx.strokeRect(n.x,n.y,n.w,n.h);
        if(s>=0.05){
          ctx.fillStyle=R.ink;ctx.textAlign='left';
          ctx.font='600 '+(s<0.12?44:30)+'px "IBM Plex Sans",sans-serif';
          ctx.fillText(s<0.12?n.id.replace(/^Q10\./,''):n.id,n.x+10,n.y+(s>=0.6?18:n.h/2));
          if(s>=0.6){
            ctx.font='500 22px "IBM Plex Sans",sans-serif';ctx.fillStyle=R.soft;
            ctx.fillText(kisalt(hc.durum,22),n.x+10,n.y+n.h-16);
          }
        }
        if(s>=1.3){
          ctx.fillStyle=R.ink;ctx.font='500 17px "IBM Plex Sans",sans-serif';ctx.textAlign='left';
          sar(ctx,hc.metin,n.x,n.y+n.h+34,n.w+240,22,5);
        }
      }else if(n.t==='p'){
        if(s<0.25)continue;
        if(!kesisir(n.x-n.r,n.y-n.r,n.r*2,n.r*2))continue;
        cizilen++;
        const dis=n.veri.tur!=='direct';
        ctx.fillStyle=n.renk;ctx.strokeStyle=n.k===secili?R.accent:R.bg;ctx.lineWidth=(n.k===secili?5:2)/s;
        ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,7);ctx.fill();
        if(dis){ctx.setLineDash([5/s,4/s]);ctx.strokeStyle=R.ink;ctx.lineWidth=1.5/s;ctx.stroke();ctx.setLineDash([])}
        else ctx.stroke();
        if(n.veri.kismi){ctx.fillStyle=R.bg;ctx.beginPath();ctx.arc(n.x,n.y,n.r*0.4,0,7);ctx.fill()}
        if(s>=0.9){
          ctx.fillStyle=R.ink;ctx.font='500 15px "IBM Plex Sans",sans-serif';ctx.textAlign='center';
          ctx.fillText(n.veri.usul,n.x,n.y+n.r+14);
        }
      }else{
        if(!kesisir(n.x-n.r,n.y-n.r,n.r*2,n.r*2))continue;
        cizilen++;
        ctx.fillStyle=R.panel;ctx.strokeStyle=n.zayif?'#d33a3a':R.soft;ctx.lineWidth=(n.k===secili?7:(n.zayif?5:2))/s;
        if(n.k===secili)ctx.strokeStyle=R.accent;
        ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,7);ctx.fill();ctx.stroke();
        if(s>=0.1){
          ctx.fillStyle=R.ink;ctx.textAlign='left';ctx.font='500 '+(s<0.3?34:24)+'px "IBM Plex Sans",sans-serif';
          ctx.fillText(s<0.3?'':kisalt(n.veri.metin,s>=1?60:30),n.x+n.r+10,n.y);
          if(s<0.3){ctx.font='500 30px "IBM Plex Sans",sans-serif';ctx.textAlign='center';ctx.fillText(n.id.replace(/^[a-z]_/,'').slice(0,10),n.x,n.y)}
        }
      }
    }
    ctx.globalAlpha=1;
    ctx.restore();
    ctx.fillStyle=R.soft;ctx.font='12px "IBM Plex Sans",sans-serif';ctx.textAlign='left';ctx.textBaseline='alphabetic';
    ctx.fillText('ölçek '+s.toFixed(3)+' · çizilen düğüm '+cizilen+'/'+d.nodes.length+' · çizilen kenar '+kenarSay+'/'+d.edges.length,10,ch-10);
    miniCiz(R);
  }
  function miniCiz(R){
    const mw=mini.width/dpr,mh=mini.height/dpr,k=mw/d.W;
    mctx.setTransform(dpr,0,0,dpr,0,0);
    mctx.fillStyle=R.panel;mctx.fillRect(0,0,mw,mh);
    mctx.fillStyle=R.line;mctx.fillRect(0,0,3000*k,mh);
    d.blocks.forEach(b=>{
      const hs=b.hucreler;
      const dog=hs.filter(x=>x.durum==='KAT’Î').length/hs.length;
      mctx.fillStyle=dog>0.9?R.dogru:(hs.some(x=>x.hukum==='İHTİLAFLI')?R.ihtilaf:R.yanlis);
      mctx.fillRect(b.x*k,b.y*k,b.w*k,b.h*k);
    });
    mctx.strokeStyle=R.accent;mctx.lineWidth=2;
    mctx.strokeRect(view.x*k,view.y*k,cw/view.s*k,ch/view.s*k);
  }

  function dunya(px,py){return [view.x+px/view.s,view.y+py/view.s]}
  function bul(px,py){
    const [wx,wy]=dunya(px,py),tol=10/view.s;
    let en=null,ed=1e9;
    for(const n of gorunen()){
      let dist;
      if(n.t==='h'){
        if(view.s<0.05)continue;
        const dx=Math.max(n.x-wx,0,wx-(n.x+n.w)),dy=Math.max(n.y-wy,0,wy-(n.y+n.h));dist=Math.hypot(dx,dy);
      }else if(n.t==='p'){
        if(view.s<0.25)continue;
        dist=Math.max(0,Math.hypot(n.x-wx,n.y-wy)-n.r);
      }else dist=Math.max(0,Math.hypot(n.x-wx,n.y-wy)-n.r);
      if(dist<=tol&&dist<ed){ed=dist;en=n}
    }
    return en;
  }
  function panelYaz(k){
    const n=d.map[k];panel.replaceChildren();panel.classList.add('acik');
    const kapat=h('button',{class:'lnk',onclick:odagiTemizle},'kapat ✕');
    if(n.t==='h'){
      const x=n.veri;
      panel.append(kapat,h('h3',null,x.id+' · '+x.ad),h('p',null,hukumChip(x.hukum),' ',durumChip(x.durum)),h('p',null,x.metin),
        h('p',{class:'not'},'Kaç yoldan: '+Number(x.yol).toLocaleString('tr')+' türetme ağacı · '+x.yol_altkume+' usul alt kümesi (asgarî '+x.asgari_yollar.length+')'),
        x.asgari_yollar.length?h('p',{class:'not'},'Asgarî yollar: '+x.asgari_yollar.slice(0,8).map(a=>a.join('+')).join(' · ')+(x.asgari_yollar.length>8?' …':'')):null,
        h('p',null,h('button',{class:'lnk',onclick:()=>hucreyeGit(x.id)},'hücre sayfasına git ›')));
    }else if(n.t==='p'){
      const p=n.veri;
      panel.append(kapat,h('h3',null,p.usul+' · '+USUL[p.usul].ad),h('p',null,durumChip(p.durum),' ',h('span',{class:'chip'},p.tur),p.kismi?h('span',{class:'chip c-İHTİLAFLI'},'kısmî'):null),
        h('p',null,p.ozet),h('p',{class:'not'},'Hücre: '+p.hucre+' · katman '+p.katman+' · bu ispatın türetme yolu: '+Number(p.yol).toLocaleString('tr')),
        h('p',null,h('button',{class:'lnk',onclick:()=>hucreyeGit(p.hucre)},'hücre sayfasına git ›')));
    }else{
      const o=n.veri;
      panel.append(kapat,h('h3',null,o.id),h('p',null,o.metin),h('p',null,h('span',{class:'chip'},o.kat),' ',h('span',{class:'chip'},o.tur),o.zayif?h('span',{class:'zayif'},' ⚠ zayıf halka'+(o.aile?' ['+o.aile+']':'')):null),
        o.not_?h('p',{class:'not'},o.not_):null);
    }
    panel.append(h('p',{class:'not'},'Odak: '+(odak?odak.up.size-1:0)+' düğüm dayanak, '+(odak?odak.dn.size-1:0)+' düğüm türev.'));
  }

  const ptr=new Map();let sur=null,pinch=null,tasindi=false;
  cv.addEventListener('pointerdown',e=>{
    cv.setPointerCapture(e.pointerId);ptr.set(e.pointerId,[e.offsetX,e.offsetY]);tasindi=false;
    if(ptr.size===1)sur={x:e.offsetX,y:e.offsetY,vx:view.x,vy:view.y};
    if(ptr.size===2){const a=[...ptr.values()];pinch={d:Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1]),s:view.s};sur=null}
  });
  cv.addEventListener('pointermove',e=>{
    if(ptr.has(e.pointerId))ptr.set(e.pointerId,[e.offsetX,e.offsetY]);
    if(pinch&&ptr.size===2){
      const a=[...ptr.values()],dd=Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1]),ns=Math.max(0.02,Math.min(6,pinch.s*dd/pinch.d));
      const mx=(a[0][0]+a[1][0])/2,my=(a[0][1]+a[1][1])/2,[wx,wy]=dunya(mx,my);
      view.s=ns;view.x=wx-mx/ns;view.y=wy-my/ns;tasindi=true;cizIste();return;
    }
    if(sur&&ptr.size===1){
      const dx=e.offsetX-sur.x,dy=e.offsetY-sur.y;
      if(Math.abs(dx)+Math.abs(dy)>4)tasindi=true;
      view.x=sur.vx-dx/view.s;view.y=sur.vy-dy/view.s;cizIste();ipucu.hidden=true;return;
    }
    if(e.pointerType==='mouse'){
      const n=bul(e.offsetX,e.offsetY);
      if(n!==hover){
        hover=n;cv.style.cursor=n?'pointer':'grab';
        if(n){ipucu.hidden=false;ipucu.textContent=n.t==='h'?n.id+' · '+n.veri.ad:(n.t==='p'?n.veri.usul+' · '+n.veri.hucre:n.id);}
        else ipucu.hidden=true;
      }
      if(n){ipucu.style.left=(e.offsetX+14)+'px';ipucu.style.top=(e.offsetY+14)+'px'}
    }
  });
  const birak=e=>{
    ptr.delete(e.pointerId);if(ptr.size<2)pinch=null;
    if(ptr.size===0){
      if(!tasindi){const n=bul(e.offsetX,e.offsetY);if(n)odaklan(n.k);else if(odak)odagiTemizle()}
      sur=null;
    }
  };
  cv.addEventListener('pointerup',birak);cv.addEventListener('pointercancel',birak);
  cv.addEventListener('wheel',e=>{
    e.preventDefault();
    const f=Math.exp(-e.deltaY*0.0015),ns=Math.max(0.02,Math.min(6,view.s*f));
    const [wx,wy]=dunya(e.offsetX,e.offsetY);view.s=ns;view.x=wx-e.offsetX/ns;view.y=wy-e.offsetY/ns;cizIste();
  },{passive:false});
  cv.addEventListener('dblclick',e=>{
    const [wx,wy]=dunya(e.offsetX,e.offsetY),ns=Math.min(6,view.s*2.2);
    gotoView({x:wx-e.offsetX/ns,y:wy-e.offsetY/ns,s:ns});
  });
  mini.addEventListener('pointerdown',e=>{
    const k=(mini.width/dpr)/d.W,wx=e.offsetX/k,wy=e.offsetY/k;
    gotoView({x:wx-cw/view.s/2,y:wy-ch/view.s/2,s:view.s});
  });
  ara.addEventListener('input',()=>{
    const q=ara.value.trim().toLowerCase();sonuc.replaceChildren();
    if(!q){sonuc.hidden=true;return}
    const bulunan=d.nodes.filter(n=>{
      const m=n.t==='h'?n.veri.metin+' '+n.veri.ad:(n.t==='p'?n.veri.ozet:n.veri.metin);
      return (n.id+' '+m).toLowerCase().includes(q);
    }).slice(0,10);
    bulunan.forEach(n=>sonuc.append(h('button',{class:'lnk',onclick:()=>{ara.value='';sonuc.hidden=true;git('ag');odaklan(n.k);odagiSigdir()}},n.id+' — '+kisalt(n.t==='h'?n.veri.metin:(n.t==='p'?n.veri.ozet:n.veri.metin),70))));
    sonuc.hidden=!bulunan.length;
  });
  window.agaGit=k=>{git('ag');setTimeout(()=>{odaklan(k);odagiSigdir()},50)};
  let hazir=false;
  function aktif(){
    if(!kap.clientWidth)return;
    boyut();
    if(!hazir){hazir=true;sigdir(0,0,d.W,d.H,true)}
    cizIste();
  }
  new ResizeObserver(aktif).observe(kap);
  document.querySelector('nav button[data-k="ag"]').addEventListener('click',()=>setTimeout(aktif,30));
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',cizIste);
}
