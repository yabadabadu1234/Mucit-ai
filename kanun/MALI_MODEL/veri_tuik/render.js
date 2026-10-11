const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const id=process.argv[2];
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--ignore-certificate-errors-spki-list=PS48cX347wDVcRynzq+DFqswl2PLNE1sG6uQvxMCOS0='],proxy:{server:process.env.HTTPS_PROXY}});
 const p=await (await b.newContext({userAgent:'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})).newPage();
 const apis=[];
 p.on('response',async r=>{const u=r.url();const ct=r.headers()['content-type']||'';if(/json/.test(ct)){try{apis.push({u,body:(await r.text()).slice(0,2000000)})}catch(e){}}});
 await p.goto('https://veriportali.tuik.gov.tr/tr/press/'+id,{waitUntil:'networkidle',timeout:90000});
 await p.waitForTimeout(4000);
 fs.writeFileSync('press_'+id+'.txt',await p.innerText('body'));
 fs.writeFileSync('press_'+id+'_api.json',JSON.stringify(apis));
 console.log(id,'api',apis.map(a=>a.u+' '+a.body.length));
 await b.close();
})();
