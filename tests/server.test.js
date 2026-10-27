'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {cleanModelText,xmlEscape,serve,requestAI,requestSpeech}=require('../server');
const event=require('../public/data/match.json').events[1];
const {Readable}=require('node:stream');
class Response{
 constructor(){this.status=0;this.body=null;this.headers={};this.writableEnded=false;}
 writeHead(code,headers){this.status=code;this.headers=headers;}
 end(body){this.body=body;this.writableEnded=true;}
}
async function call(method,url,body){
 const req=Readable.from(body?[Buffer.from(body)]:[]);
 req.method=method;req.url=url;req.headers={host:'localhost:3000'};
 const res=new Response();await serve(req,res);return res;
}
test('AI response guard prevents key unsupported claims',()=>{
 const pass={kind:'pass'};
 assert.equal(cleanModelText('Hart makes a careful forward pass.',pass),'Hart makes a careful forward pass.');
 assert.throws(()=>cleanModelText('Hart scores a goal!',pass));
 assert.throws(()=>cleanModelText('VAR awards a penalty to Morgan.',pass));
 assert.throws(()=>cleanModelText('The score is now 2-1.',pass));
});
test('SSML text escaping is safe',()=>assert.equal(xmlEscape('A&B <C> "D"'), 'A&amp;B &lt;C&gt; &quot;D&quot;'));
test('Health and capabilities expose no credentials',async()=>{
 const response=await call('GET','/api/capabilities');
 assert.equal(response.status,200);const j=JSON.parse(response.body);
 assert.equal(j.foundry,false);assert.equal(j.speech,false);assert.equal(j.synthetic,true);
 assert.equal((await call('GET','/healthz')).status,200);
});
test('Unknown static route and unsupported method denied',async()=>{
 assert.equal((await call('GET','/.env')).status,404);
 assert.equal((await call('GET','/server.js')).status,404);
 assert.equal((await call('PUT','/')).status,405);
});
test('Offline AI and Speech routes do not pretend to be working',async()=>{
 const body=JSON.stringify({eventId:'E01',detail:'essential'});
 const ai=await call('POST','/api/narrate',body);
 const tts=await call('POST','/api/speak',body);
 assert.equal(ai.status,503);assert.equal(tts.status,503);
});

test('Mocked Microsoft Foundry REST request uses credentials only server-side',async()=>{
 const origFetch=global.fetch;
 const saved={base:process.env.FOUNDRY_BASE_URL,key:process.env.FOUNDRY_API_KEY,model:process.env.FOUNDRY_MODEL};
 process.env.FOUNDRY_BASE_URL='https://test.openai.azure.com/openai/v1';
 process.env.FOUNDRY_API_KEY='secret-testing-only';process.env.FOUNDRY_MODEL='test-deployment';
 let called=false;
 global.fetch=async(url,opts)=>{
  called=true;assert.equal(url,'https://test.openai.azure.com/openai/v1/chat/completions');
  assert.equal(opts.headers['api-key'],'secret-testing-only');
  const body=JSON.parse(opts.body);assert.equal(body.model,'test-deployment');
  assert.equal(body.messages[1].role,'user');
  return {ok:true,json:async()=>({choices:[{message:{content:'Hart makes a controlled forward pass to Imani.'}}]})};
 };
 try{assert.equal(await requestAI(event,'essential'),'Hart makes a controlled forward pass to Imani.');assert.equal(called,true);}
 finally{global.fetch=origFetch;for(const [k,v] of Object.entries({FOUNDRY_BASE_URL:saved.base,FOUNDRY_API_KEY:saved.key,FOUNDRY_MODEL:saved.model})){if(v===undefined)delete process.env[k];else process.env[k]=v;}}
});
test('Mocked Azure Speech creates escaped SSML with no browser-exposed key',async()=>{
 const origFetch=global.fetch;
 const oldRegion=process.env.AZURE_SPEECH_REGION,oldKey=process.env.AZURE_SPEECH_KEY;
 process.env.AZURE_SPEECH_REGION='uksouth';process.env.AZURE_SPEECH_KEY='fake-testing-key';
 global.fetch=async(url,opts)=>{
  assert.equal(url,'https://uksouth.tts.speech.microsoft.com/cognitiveservices/v1');
  assert.equal(opts.headers['Ocp-Apim-Subscription-Key'],'fake-testing-key');
  assert.match(opts.body,/<speak/);assert.match(opts.body,/Hart passes to Imani/);
  return {ok:true,arrayBuffer:async()=>Uint8Array.from([73,68,51]).buffer};
 };
 try{assert.equal((await requestSpeech(event,'essential')).toString('ascii'),'ID3');}
 finally{global.fetch=origFetch;if(oldRegion===undefined)delete process.env.AZURE_SPEECH_REGION;else process.env.AZURE_SPEECH_REGION=oldRegion;if(oldKey===undefined)delete process.env.AZURE_SPEECH_KEY;else process.env.AZURE_SPEECH_KEY=oldKey;}
});
