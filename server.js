/** Minimal no-dependency Node server for the synthetic demonstration.
 * Optional backend adapters use Azure OpenAI/Foundry chat completions and Azure Speech REST.
 * Run locally: node server.js
 * For Azure credentials: node --env-file=.env server.js  (Node 20+)
 * DO NOT deploy secrets or this backend on GitHub Pages. It is a static-only host.
 */
'use strict';
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const ROOT=__dirname;
const FIXTURE=JSON.parse(fs.readFileSync(path.join(ROOT,'public/data/match.json'),'utf8'));
const foundry=Boolean(process.env.FOUNDRY_BASE_URL&&process.env.FOUNDRY_API_KEY&&process.env.FOUNDRY_MODEL);
const speech=Boolean(process.env.AZURE_SPEECH_KEY&&process.env.AZURE_SPEECH_REGION);
const port=Number(process.env.PORT||3000);
const MIME={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8'};

function send(res,status,data,kind='application/json; charset=utf-8'){
 res.writeHead(status,{'Content-Type':kind,'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"});
 res.end(kind.startsWith('application/json')?JSON.stringify(data):data);
}
async function getBody(req){
 let txt=''; for await(const chunk of req){txt+=chunk;if(txt.length>2048)throw new Error('Payload too large');}
 let obj;try{obj=JSON.parse(txt);}catch{throw new Error('Invalid JSON');}
 if(!obj||typeof obj.eventId!=='string'||!/^E\d{2}$/.test(obj.eventId)||!['essential','detailed'].includes(obj.detail))throw new Error('Invalid event request');
 const event=FIXTURE.events.find(e=>e.id===obj.eventId);if(!event)throw new Error('Unknown event');
 return {event,detail:obj.detail};
}
function cleanModelText(text, event){
 if(typeof text!=='string'||text.length<8||text.length>460)throw new Error('AI response invalid length');
 text=text.trim().replace(/[\r\n]+/g,' ');
 // Sanity filter; not a comprehensive factuality verifier.
 if(/\b(premier league|VAR|red card|penalty kick|hat.trick|offside)\b/i.test(text))throw new Error('Unexpected unsupported football claim');
 if(/\b(\d+)\s*[-:]\s*(\d+)\b/.test(text))throw new Error('Unverified score');
 if(event.kind!=='shot'&&event.kind!=='save'&&/\b(scored|scores|a goal|the goal|netted)\b/i.test(text))throw new Error('Unverified scoring claim');
 if(event.kind==='shot'&&/\b(scored|scores|a goal|the goal|netted)\b/i.test(text))throw new Error('A shot is not a confirmed goal');
 return text;
}
async function requestAI(event,detail){
 const base=process.env.FOUNDRY_BASE_URL.replace(/\/+$/,'');
 if(!/^https:\/\//.test(base))throw new Error('Foundry endpoint must be HTTPS');
 const url=new URL(base+'/chat/completions');
 const messages=[
  {role:'system',content:'You are a football audio-description writer for blind and partially sighted fans. Rephrase the provided SYNTHETIC EVENT in plain, direct British English. Never invent a goal, score, foul, specific tactical intention, player, statistic, or outcome. Treat authored narration as the only permitted event-specific claims. For essential output use at most 22 words; for detailed output use at most 45 words. Output only narration text, no markdown or extra explanation.'},
  {role:'user',content:JSON.stringify({event_id:event.id,kind:event.kind,team_id:event.team_id,player_id:event.player_id,recipient_id:event.recipient_id,outcome:event.outcome,player_position_m:event.location_m,why:event.why,verified_baseline:event.narration[detail],detail})}
 ];
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),12000);
 try{
  const result=await fetch(url.toString(),{method:'POST',headers:{'Content-Type':'application/json','api-key':process.env.FOUNDRY_API_KEY},body:JSON.stringify({model:process.env.FOUNDRY_MODEL,messages,max_tokens:160,temperature:.2}),signal:controller.signal});
  if(!result.ok)throw new Error('Foundry model request failed');
  const output=await result.json();const text=output.choices?.[0]?.message?.content;
  return cleanModelText(text,event);
 }finally{clearTimeout(timeout);}
}
function xmlEscape(t){return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');}
async function requestSpeech(event,detail){
 const region=process.env.AZURE_SPEECH_REGION;
 if(!/^[a-z0-9-]{2,40}$/i.test(region))throw new Error('Invalid Speech region');
 const voice=process.env.AZURE_SPEECH_VOICE||'en-GB-SoniaNeural';
 if(!/^[a-z0-9-]+$/i.test(voice))throw new Error('Invalid Speech voice');
 const ssml=`<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-GB"><voice name="${xmlEscape(voice)}">${xmlEscape(event.narration[detail])}</voice></speak>`;
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),12000);
 try{
  const res=await fetch(`https://${region}.tts.speech.microsoft.com/cognitiveservices/v1`,{method:'POST',headers:{'Ocp-Apim-Subscription-Key':process.env.AZURE_SPEECH_KEY,'Content-Type':'application/ssml+xml','X-Microsoft-OutputFormat':'audio-16khz-128kbitrate-mono-mp3','User-Agent':'FootballWithoutBarriersPOC'},body:ssml,signal:controller.signal});
  if(!res.ok)throw new Error('Azure Speech request failed');
  const bytes=Buffer.from(await res.arrayBuffer());if(bytes.length>2_500_000)throw new Error('Audio size unexpectedly large');
  return bytes;
 }finally{clearTimeout(timeout);}
}
async function serve(req,res){
 let url;try{url=new URL(req.url,`http://${req.headers.host||'localhost'}`);}catch{send(res,400,{error:'Invalid URL'});return;}
 const pathname=url.pathname;
 if(req.method==='GET'&&pathname==='/healthz'){send(res,200,{status:'ok',synthetic:true});return;}
 if(req.method==='GET'&&pathname==='/api/capabilities'){send(res,200,{foundry,speech,synthetic:true});return;}
 if(req.method==='POST'&&(pathname==='/api/narrate'||pathname==='/api/speak')){
  const enabled=pathname==='/api/narrate'?foundry:speech;
  if(!enabled){send(res,503,{error:'Azure integration is not configured. Offline demonstration is available.'});return;}
  let query;try{query=await getBody(req);}catch(e){send(res,400,{error:e.message});return;}
  try{
   if(pathname==='/api/narrate'){
    const narration=await requestAI(query.event,query.detail);
    send(res,200,{event_id:query.event.id,narration,source:'foundry_rephrase',verified:false});
   }else{
    const bytes=await requestSpeech(query.event,query.detail);
    send(res,200,bytes,'audio/mpeg');
   }
  }catch(error){console.error('Azure adapter failure:',error.message);send(res,502,{error:'Azure operation failed; baseline narration is available.'});}
  return;
 }
 if(req.method!=='GET'&&req.method!=='HEAD'){send(res,405,{error:'Method not allowed'});return;}
 const allowed=new Set(['/','/index.html','/styles.css','/app.js','/public/data/match.js','/public/data/match.json']);
 if(!allowed.has(pathname)){send(res,404,{error:'Not found'});return;}
 const full=path.join(ROOT,pathname==='/'?'index.html':pathname.slice(1));
 fs.readFile(full,(error,data)=>{
  if(error){send(res,404,{error:'File missing'});return;}
  const mime=MIME[path.extname(full)]||'application/octet-stream';
  res.writeHead(200,{'Content-Type':mime,'Cache-Control':'max-age=120','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
   'Content-Security-Policy':"default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; media-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"});
  res.end(req.method==='HEAD'?'':data);
 });
}
if(require.main===module){
 http.createServer((req,res)=>{serve(req,res).catch(err=>{console.error('Server error:',err);if(!res.writableEnded)send(res,500,{error:'Server error'});});}).listen(port,'127.0.0.1',()=>console.log(`FWB demo running at http://127.0.0.1:${port} (Foundry ${foundry?'on':'off'}, Speech ${speech?'on':'off'})`));
}
module.exports={serve,cleanModelText,xmlEscape,requestAI,requestSpeech};
