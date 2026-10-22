(function(){
'use strict';
function $(s,k){return (k||document).querySelector(s)}
function $$(s,k){return Array.prototype.slice.call((k||document).querySelectorAll(s))}
function f(x,n){if(!isFinite(x))return '—';var a=Math.abs(x);if(a!==0&&(a<1e-3||a>=1e6))return x.toExponential(3);return Number(x.toPrecision(n||5)).toString().replace('.',',')}
function pf(v){return parseFloat(String(v).replace(',','.'))}

/* ---------- şemada parça tıklama / işaret vurgusu ---------- */
document.addEventListener('click',function(e){
  var g=e.target.closest&&e.target.closest('.parca[data-ref]');
  if(!g)return;
  var ref=g.getAttribute('data-ref');
  var kart=document.getElementById('kart-'+ref);
  $$('.parca.secili').forEach(function(x){x.classList.remove('secili')});
  $$('.parca[data-ref="'+ref+'"]').forEach(function(x){x.classList.add('secili')});
  if(kart){kart.scrollIntoView({behavior:'smooth',block:'center'});kart.classList.add('flas');setTimeout(function(){kart.classList.remove('flas')},1800)}
});
$$('ol.isaretli>li').forEach(function(li,i){
  li.addEventListener('mouseenter',function(){var m=$('.isaret[data-no="'+(i+1)+'"]');if(m)m.classList.add('vurgu');li.classList.add('vurgu')});
  li.addEventListener('mouseleave',function(){var m=$('.isaret[data-no="'+(i+1)+'"]');if(m)m.classList.remove('vurgu');li.classList.remove('vurgu')});
});

/* ---------- hesap makineleri ---------- */
var H={
bolucu:{b:'Gerilim bölücü: Çıkış = Giriş × Alt / (Üst + Alt)',a:[['Giriş gerilimi (V)',12],['Üst direnç (Ω)',31600],['Alt direnç (Ω)',10000]],
 h:function(v){var o=v[0]*v[2]/(v[1]+v[2]);return 'Çıkış = '+f(v[0])+' × '+f(v[2])+' / ('+f(v[1])+' + '+f(v[2])+') = '+f(o)+' V\nBölücüden akan akım = '+f(v[0]/(v[1]+v[2])*1e6)+' µA\nBölücünün harcadığı güç = '+f(v[0]*v[0]/(v[1]+v[2])*1e3)+' mW'}},
geribesleme:{b:'Anahtarlamalı çevirici geri besleme dirençleri: Çıkış = Referans × (1 + Üst/Alt)',a:[['Referans gerilimi (V)',0.8],['Üst direnç (Ω)',31600],['Alt direnç (Ω)',10000]],
 h:function(v){var o=v[0]*(1+v[1]/v[2]);return 'Çıkış = '+f(v[0])+' × (1 + '+f(v[1])+'/'+f(v[2])+') = '+f(o)+' V\nÜst direnç %1 yukarı, alt direnç %1 aşağıda iken: '+f(v[0]*(1+v[1]*1.01/(v[2]*0.99)))+' V\nÜst direnç %1 aşağı, alt direnç %1 yukarıda iken: '+f(v[0]*(1+v[1]*0.99/(v[2]*1.01)))+' V (referansın kendi toleransı ayrıca eklenir)\nÜst direnç, çıkış hedefi için gereken değer: Alt × (Çıkış/Referans − 1)'}},
led:{b:'Işık yayan diyot (LED) için seri direnç',a:[['Besleme (V)',3.3],['LED düşümü (V)',2.0],['Hedef akım (mA)',2]],
 h:function(v){var r=(v[0]-v[1])/(v[2]/1000);return 'R = (Besleme − LED düşümü) / Akım = ('+f(v[0])+' − '+f(v[1])+') / '+f(v[2]/1000)+' = '+f(r)+' Ω\nRezistörde harcanan güç = '+f((v[0]-v[1])*v[2])+' mW\nStandart değere yuvarla: bir üstteki standart değer akımı biraz düşürür, bir alttaki biraz artırır.'}},
rc:{b:'Direnç–kondansatör: zaman sabiti ve kesme frekansı',a:[['Direnç (Ω)',10000],['Kondansatör (µF)',1]],
 h:function(v){var t=v[0]*v[1]*1e-6;return 'Zaman sabiti τ = R × C = '+f(t*1e3)+' ms\n%63 dolma süresi = '+f(t*1e3)+' ms, %95 dolma süresi ≈ 3τ = '+f(3*t*1e3)+' ms, %99 ≈ 4,6τ = '+f(4.6*t*1e3)+' ms\nKesme frekansı = 1/(2πRC) = '+f(1/(2*Math.PI*t))+' Hz'}},
bobin:{b:'Düşüren (buck) çevirici: bobin dalgalanma akımı',a:[['Giriş (V)',12],['Çıkış (V)',3.3],['Anahtarlama frekansı (kHz)',500],['Bobin (µH)',4.7]],
 h:function(v){var D=v[1]/v[0];var di=(v[0]-v[1])*D/(v[2]*1e3*v[3]*1e-6);return 'Görev oranı D = Çıkış/Giriş = '+f(D)+'\nDalgalanma ΔI = (Giriş−Çıkış)×D / (f×L) = '+f(di)+' A (tepeden tepeye)\nYük akımının yarısı kadar tepe: Itepe = Iyük + ΔI/2\nPratik kural: ΔI, azami yük akımının %20–40\'ı olsun.'}},
yukselten:{b:'Yükselten çalışma (TPS63031 veri sayfası denklem 2 ve 3): bobin tepe akımı',a:[['Giriş (V)',1.8],['Çıkış (V)',3.3],['Yük akımı (A)',0.3],['Verim',0.9],['Frekans (MHz)',2.4],['Bobin (µH)',1.5]],
 h:function(v){var D=(v[1]-v[0])/v[1];var I=v[2]/(v[3]*(1-D))+v[0]*D/(2*v[4]*1e6*v[5]*1e-6);return 'D = (Çıkış−Giriş)/Çıkış = '+f(D)+'\nItepe = Iyük/(η×(1−D)) + Giriş×D/(2×f×L) = '+f(I)+' A\nVeri sayfası önerisi: bobinin doyma akımı bunun %20 fazlası olsun = '+f(I*1.2)+' A\nAnahtar akım sınırı (tipik) 1,0 A; Itepe bunu aşıyorsa çıkış çökmeye başlar.'}},
ohm:{b:'Ohm ve güç kanunları',a:[['Gerilim (V)',3.3],['Direnç (Ω)',100]],
 h:function(v){var i=v[0]/v[1];return 'Akım = V/R = '+f(i*1e3)+' mA\nGüç = V×I = '+f(v[0]*i*1e3)+' mW'}},
pil:{b:'Pil ömrü tahmini',a:[['Pil kapasitesi (mAh)',1000],['Uyku akımı (µA)',10],['Basış başına enerji (mAs)',60],['Günde basış sayısı',100],['Verim',0.85]],
 h:function(v){var uyku=v[1]/1000*24;var bas=v[2]/3600*v[3];var gun=v[0]*v[4]/(uyku+bas);return 'Günlük uyku tüketimi = '+f(uyku)+' mAh\nGünlük basış tüketimi = '+f(bas)+' mAh\nTahmini ömür = '+f(gun)+' gün ≈ '+f(gun/365)+' yıl\n(Bu bir hesap; ölçüm değil. Pilin kendi kendine boşalması ve düşük sıcaklık ayrıca hesaba katılmalı.)'}},
mikroserit:{b:'Mikroşerit hat empedansı (Hammerstad yaklaşımı, geniş hat w/h ≥ 1 ve dar hat için)',a:[['Hat genişliği w (mm)',0.4],['Dielektrik kalınlığı h (mm)',0.21],['Bakır kalınlığı t (mm)',0.035],['Bağıl dielektrik sabiti εr',4.4]],
 h:function(v){var w=v[0],h=v[1],t=v[2],er=v[3];var we=w+(t/Math.PI)*(1+Math.log(2*h/t));var u=we/h,ee,Z;if(u<=1){ee=(er+1)/2+(er-1)/2*(Math.pow(1+12/u,-0.5)+0.04*Math.pow(1-u,2));Z=60/Math.sqrt(ee)*Math.log(8/u+u/4)}else{ee=(er+1)/2+(er-1)/2*Math.pow(1+12/u,-0.5);Z=120*Math.PI/(Math.sqrt(ee)*(u+1.393+0.667*Math.log(u+1.444)))}
 return 'Etkin genişlik w_e = '+f(we)+' mm\nEtkin dielektrik sabiti = '+f(ee)+'\nEmpedans Z0 ≈ '+f(Z)+' Ω\nHedef 50 Ω. Üreticinin gerçek katman kalınlığı ve εr değeri alınmadan bu sayı nihai değildir; ±%10 sapma normaldir.'}},
iz:{b:'Bakır iz akım kapasitesi (IPC-2221 yaklaşımı)',a:[['Akım (A)',2],['İzin sıcaklık artışı (°C)',10],['Bakır kalınlığı (µm)',35],['Dış katman mı? (1=evet, 0=iç)',1]],
 h:function(v){var k=v[3]?0.048:0.024;var A=Math.pow(v[0]/(k*Math.pow(v[1],0.44)),1/0.725);var w=A/(v[2]/25.4)*0.0254;return 'Gereken kesit = '+f(A)+' mil² (1 mil = 0,0254 mm)\nGereken iz genişliği ≈ '+f(w)+' mm\n(IPC-2221 eğrisi; kısa izlerde ve geniş bakır dökümlerde gerçek değer daha rahattır.)'}},
dalga:{b:'Telsiz dalga boyu ve çeyrek dalga anten',a:[['Frekans (MHz)',915],['Hız çarpanı (hat için 1; kablo/anten gövdesinde 0,95 civarı)',0.95]],
 h:function(v){var l=299792458/(v[0]*1e6);return 'Boşlukta dalga boyu λ = c/f = '+f(l*100)+' cm\nÇeyrek dalga = '+f(l*25)+' cm, hız çarpanıyla = '+f(l*25*v[1])+' cm\nYarım dalga = '+f(l*50)+' cm'}},
izdirenc:{b:'İz direnci ve gerilim kaybı',a:[['Uzunluk (mm)',30],['Genişlik (mm)',0.3],['Bakır kalınlığı (µm)',35],['Akım (A)',0.5]],
 h:function(v){var R=1.724e-8*(v[0]*1e-3)/((v[1]*1e-3)*(v[2]*1e-6));return 'Direnç = ρL/(w·t) = '+f(R*1e3)+' mΩ\nGerilim kaybı = '+f(R*v[3]*1e3)+' mV\nIsınma gücü = '+f(R*v[3]*v[3]*1e3)+' mW'}},
baglanti:{b:'Telsiz bağlantı bütçesi ve serbest uzay menzili',a:[['Verici gücü (dBm)',20],['Verici anten kazancı (dBi)',2],['Alıcı anten kazancı (dBi)',2],['Alıcı duyarlılığı (dBm)',-136],['Kayıp payı (dB)',10],['Frekans (MHz)',915]],
 h:function(v){var tol=v[0]+v[1]+v[2]-v[3]-v[4];var d=Math.pow(10,(tol-32.44-20*Math.log10(v[5]))/20);return 'İzin verilen toplam yol kaybı = '+f(tol)+' dB\nSerbest uzay kaybı: FSPL(dB) = 32,44 + 20·log10(km) + 20·log10(MHz)\nSerbest uzayda en fazla uzaklık ≈ '+f(d)+' km\nGerçekte binalar, yer yansıması, bitki örtüsü ve Fresnel bölgesi menzili çok kısaltır: kentte tipik olarak bu değerin yüzde birine kadar düşer. Gerçek menzil sahada ölçülür.'}},
kondgerilim:{b:'Seramik kondansatörde gerilim altında kapasite kaybı (DC kayma) — kaba bakış',a:[['Anma kapasitesi (µF)',10],['Anma gerilimi (V)',6.3],['Uygulanan gerilim (V)',3.3],['Kılıf (1=0603, 2=0805, 3=1206)',1]],
 h:function(v){var oran=v[2]/v[0];var kayip=[0,0.60,0.45,0.35][v[3]|0]||0.5;var q=Math.min(1,oran)*kayip;return 'Gerilim/anma = '+f(oran*100)+' %\nBu değerler kabaca bir model: gerçek parçanın üretici eğrisine (örn. Murata SimSurfing) bakmadan kesin sayı verilemez.\nKaba kayıp tahmini ≈ %'+f(q*100,3)+' → etkin kapasite ≈ '+f(v[0]*(1-q))+' µF\nÖğüt: küçük kılıfta ve düşük anma geriliminde 10 µF yazan parçadan, gerilim altında yarıya yakın kapasite bekle.'}}
};
$$('.hesap[data-hesap]').forEach(function(kut){
  var ad=kut.getAttribute('data-hesap'),t=H[ad];if(!t)return;
  var onay=kut.getAttribute('data-varsayilan');var vs=onay?JSON.parse(onay):null;
  var html='<b>'+t.b+'</b><br>';
  t.a.forEach(function(a,i){html+='<label>'+a[0]+' <input type="text" inputmode="decimal" value="'+String(vs?vs[i]:a[1]).replace('.',',')+'" data-i="'+i+'"></label>'});
  html+='<div class="sonuc"></div>';kut.innerHTML=html;
  function hesapla(){var v=$$('input',kut).map(function(x){return pf(x.value)});$('.sonuc',kut).textContent=t.h(v)}
  kut.addEventListener('input',hesapla);hesapla();
});

/* ---------- kart görüntüleyici ---------- */
$$('svg.pano').forEach(function(svg){
  var kap=svg.parentElement.parentElement;
  var bilgi=$('.panobilgi',kap);
  var vb=svg.getAttribute('viewBox').split(' ').map(parseFloat);var tam=vb.slice();
  var surukle=null;
  function ayar(){svg.setAttribute('viewBox',vb.join(' '))}
  svg.addEventListener('wheel',function(e){e.preventDefault();var r=svg.getBoundingClientRect();var mx=(e.clientX-r.left)/r.width,my=(e.clientY-r.top)/r.height;var k=e.deltaY<0?0.8:1.25;var w=vb[2]*k,h=vb[3]*k;if(w>tam[2]*1.2){w=tam[2]*1.2;h=tam[3]*1.2}vb[0]+=(vb[2]-w)*mx;vb[1]+=(vb[3]-h)*my;vb[2]=w;vb[3]=h;ayar()},{passive:false});
  svg.addEventListener('pointerdown',function(e){surukle={x:e.clientX,y:e.clientY};svg.setPointerCapture(e.pointerId)});
  svg.addEventListener('pointermove',function(e){if(!surukle)return;var r=svg.getBoundingClientRect();vb[0]-=(e.clientX-surukle.x)*vb[2]/r.width;vb[1]-=(e.clientY-surukle.y)*vb[3]/r.height;surukle={x:e.clientX,y:e.clientY};ayar()});
  svg.addEventListener('pointerup',function(){surukle=null});
  var ag=null;
  function agVurgu(a){$$('.secili',svg).forEach(function(x){x.classList.remove('secili')});ag=a;if(!a)return;$$('[data-ag="'+a.replace(/"/g,'\\"')+'"]',svg).forEach(function(x){x.classList.add('secili')})}
  svg.addEventListener('click',function(e){
    var el=e.target.closest('[data-ag],[data-ref]');if(!el)return;
    var a=el.getAttribute('data-ag'),r=el.getAttribute('data-ref'),n=el.getAttribute('data-no');
    if(a!==null){agVurgu(a)}
    var s=[];if(r)s.push('Parça: <b>'+r+'</b>'+(n?' ayak '+n:''));if(a)s.push('Ağ: <b>'+a+'</b>');
    if(a){var ref={};$$('[data-ag="'+a.replace(/"/g,'\\"')+'"][data-ref]',svg).forEach(function(x){ref[x.getAttribute('data-ref')+'.'+x.getAttribute('data-no')]=1});s.push('Bu ağa bağlı ayaklar: '+Object.keys(ref).join(', '))}
    bilgi.innerHTML=s.join('<br>');
    if(r){var k=document.getElementById('kart-'+r);if(k){bilgi.innerHTML+=' — <a href="#kart-'+r+'">parça kartına git</a>'}}
  });
  $$('input[data-katman]',kap).forEach(function(c){c.addEventListener('change',function(){var k=c.getAttribute('data-katman');$$('.k-'+k,svg).forEach(function(x){x.classList.toggle('gizli',!c.checked)})});});
  var sf=$('button[data-sifirla]',kap);if(sf)sf.addEventListener('click',function(){vb=tam.slice();ayar()});
  $$('button[data-git]',kap).forEach(function(b){b.addEventListener('click',function(){var p=b.getAttribute('data-git').split(',').map(parseFloat);vb=p.slice();ayar()})});
});
})();
