const {chromium}=require('/opt/node22/lib/node_modules/playwright');
const fs=require('fs');
(async()=>{
 const id=process.argv[2];
 const d=JSON.parse(fs.readFileSync('press_'+id+'_body.json')).data;
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--ignore-certificate-errors-spki-list=PS48cX347wDVcRynzq+DFqswl2PLNE1sG6uQvxMCOS0='],proxy:{server:process.env.HTTPS_PROXY}});
 const ctx=await b.newContext({userAgent:'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'});
 const p=await ctx.newPage();
 await p.goto('https://veriportali.tuik.gov.tr/tr/press/'+id,{waitUntil:'load',timeout:90000});
 await p.waitForTimeout(3000);
 for(let k=0;k<d.tables.length;k++){
  const f='x'+id+'/t'+String(k).padStart(2,'0')+'.xls';
  if(fs.existsSync(f)&&fs.statSync(f).size>5000) continue;
  for(let a=0;a<4;a++){
   try{
    const r=await ctx.request.get('https://veriportali.tuik.gov.tr'+d.tables[k].url,{timeout:90000});
    const buf=await r.body();
    if(buf.length>5000){fs.writeFileSync(f,buf);console.log(k,'ok',buf.length);break}
    console.log(k,'small',buf.length,buf.slice(0,80).toString());
   }catch(e){console.log(k,'ERR',a)}
   await p.waitForTimeout(3000);
  }
 }
 await b.close();
})();
