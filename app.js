/* Football Without Barriers v0.2 - accessible, dependency-free synthetic match viewer.
 * The local experience is deterministic, NOT an AI model or a real-time football feed.
 * Optional Microsoft Foundry and Azure Speech endpoints are served by server.js.
 */
(() => {
  'use strict';
  const match = window.FWB_MATCH;
  if (!match || match.synthetic !== true || !Array.isArray(match.frames)) {
    document.body.textContent = 'Unable to load the synthetic match fixture. Check public/data/match.js.';
    return;
  }
  const $ = (id) => document.getElementById(id);
  const maxMs = match.duration_ms;
  const frameMs = 1000 / match.fps;
  const events = match.events;
  // Never report confirmed outcomes until the relevant tracking evidence is available.
  const availableAt = e => e.available_at_ms ?? e.t_ms;
  const byId = new Map(match.players.map(p => [p.id, p]));
  const svgNS = 'http://www.w3.org/2000/svg';
  const state = {t:0, playing:false, rate:1, previousTs:null, mode:'visual', detail:'detailed',
    speech:false, speechEngine:'browser', currentEvent:null, aiText:null,
    azureAI:false, azureSpeech:false, activeAudio:null, lastVoiceRequest:0,
    foundryInsights:new Map()};
  const $markers = $('playerMarkers');
  const playerViews = new Map();
  const fmt = ms => {
    const n = Math.floor(Math.max(0, ms) / 1000);
    return String(Math.floor(n/60)).padStart(2,'0') + ':' + String(n%60).padStart(2,'0');
  };
  const playerName = id => byId.get(id)?.name || 'the player';
  $('homeName').textContent = match.teams.find(t=>t.id==='home').name;
  $('awayName').textContent = match.teams.find(t=>t.id==='away').name;

  for(const p of match.players) {
    const group = document.createElementNS(svgNS,'g');
    const shape = document.createElementNS(svgNS, p.team_id === 'home' ? 'circle' : 'rect');
    if (p.team_id === 'home') {
      shape.setAttribute('r',1.75);shape.setAttribute('class','player-home');
    } else {
      shape.setAttribute('x',-1.7);shape.setAttribute('y',-1.7);
      shape.setAttribute('width',3.4);shape.setAttribute('height',3.4);
      shape.setAttribute('rx',.34);shape.setAttribute('class','player-away');
    }
    const number = document.createElementNS(svgNS,'text');
    number.setAttribute('class','player-label');number.textContent=p.number;
    group.append(shape,number); $markers.appendChild(group);
    playerViews.set(p.id,{group,shape});
  }

  for (const e of events) {
    const li=document.createElement('li');
    const button=document.createElement('button');
    button.type='button'; button.dataset.eventId=e.id;
    button.setAttribute('aria-label', `${fmt(availableAt(e))}. ${e.narration.essential}. Jump to confirmed event.`);
    const time=document.createElement('span');time.className='event-minute';time.textContent=fmt(availableAt(e));
    const tag=document.createElement('span');tag.className='event-tag';tag.textContent=e.kind.replaceAll('_',' ');
    const copy=document.createElement('span');copy.className='event-copy';copy.textContent=e.narration.essential;
    button.append(time,tag,copy);li.appendChild(button);$('eventList').appendChild(li);
    button.addEventListener('click',()=>{pause(); seek(availableAt(e),true);});
  }

  const lastEvent = t => {
    for(let i=events.length-1;i>=0;i--) if(availableAt(events[i]) <= t+1) return events[i];
    return events[0];
  };

  function renderFrame(t) {
    const idx=Math.min(match.frames.length-1,Math.floor(t/frameMs));
    const next=Math.min(match.frames.length-1,idx+1);
    const a=match.frames[idx], b=match.frames[next];
    const fraction=Math.min(1,Math.max(0,(t-a.t_ms)/(b.t_ms-a.t_ms||1)));
    for(let i=0;i<match.players.length;i++){
      const p0=a.players[i],p1=b.players[i];
      const view=playerViews.get(p0.id);
      if(!view)continue;
      const x=p0.x+(p1.x-p0.x)*fraction, y=p0.y+(p1.y-p0.y)*fraction;
      view.group.setAttribute('transform',`translate(${x.toFixed(2)},${y.toFixed(2)})`);
      const active=p0.id===state.currentEvent?.player_id;
      view.shape.setAttribute('stroke',active?'#ffffff':'#0b1324');
      view.shape.setAttribute('stroke-width',active?'1.1':'.75');
    }
    const bx=a.ball.x+(b.ball.x-a.ball.x)*fraction;
    const by=a.ball.y+(b.ball.y-a.ball.y)*fraction;
    $('ballMarker').setAttribute('cx',bx.toFixed(2));
    $('ballMarker').setAttribute('cy',by.toFixed(2));
    const possession = a.possession?.team_id === 'home' ? 'RIVERGATE' :
      a.possession?.team_id === 'away' ? 'NORTHBRIDGE' : 'UNCONFIRMED';
    $('possessionIndicator').textContent=possession==='UNCONFIRMED'?'POSSESSION NOT CONFIRMED':`${possession} IN POSSESSION`;
    $('phaseLabel').textContent=t<43000?'BUILD-UP':t<62000?'ATTACKING CHANCE':'DEFENSIVE RESET';
    $('matchClock').textContent=fmt(t);$('elapsed').textContent=fmt(t);$('timeSlider').value=Math.round(t);
  }
  function updateCounts(t){
    const elapsed=events.filter(e=>availableAt(e)<=t);
    $('passCount').textContent=elapsed.filter(e=>e.kind==='pass'&&e.outcome==='complete').length;
    $('shotCount').textContent=elapsed.filter(e=>e.kind==='shot'&&e.outcome==='on_target').length;
    $('pressureCount').textContent=elapsed.filter(e=>e.kind==='pressure').length;
  }
  function cancelVoice() {
    state.lastVoiceRequest++;
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    if (state.activeAudio){state.activeAudio.pause();state.activeAudio=null;}
  }
  async function speak(text,eventId,detail) {
    if (!state.speech || !text) return;
    cancelVoice();
    const request=state.lastVoiceRequest;
    if(state.speechEngine==='azure' && state.azureSpeech){
      try{
        const response=await fetch('./api/speak',{method:'POST',headers:{'Content-Type':'application/json'},
          body:JSON.stringify({eventId,detail})});
        if(!response.ok)throw new Error(`Azure Speech returned ${response.status}`);
        const blob=await response.blob();
        if(request!==state.lastVoiceRequest)return;
        const url=URL.createObjectURL(blob);
        const audio=new Audio(url); state.activeAudio=audio;
        audio.addEventListener('ended',()=>{URL.revokeObjectURL(url);if(state.activeAudio===audio)state.activeAudio=null;});
        audio.addEventListener('error',()=>URL.revokeObjectURL(url));
        await audio.play();
      }catch(error){console.warn('Azure speech unavailable:',error);$('speechButton').title='Speech service unavailable; choose Device speech to continue';}
    }else if('speechSynthesis' in window){
      const utterance=new SpeechSynthesisUtterance(text);
      utterance.lang='en-GB';utterance.rate=state.mode==='audio'?.94:1.04;
      window.speechSynthesis.speak(utterance);
    }
  }
  function updateEvent(e,announce) {
    const changed=state.currentEvent?.id!==e.id;
    if(changed){state.currentEvent=e;state.aiText=null;}
    const text=state.aiText||e.narration[state.detail];
    const renderKey=e.id+'|'+state.detail+'|'+(state.aiText||'');
    if(renderKey===state.lastRenderedNarrationKey)return;
    state.lastRenderedNarrationKey=renderKey;
    $('commentaryText').textContent=text;
    $('eventTime').textContent=fmt(availableAt(e));
    const insight=state.foundryInsights.get(e.id);
    $('whyText').textContent=insight?.explanation||e.why;
    $('whySource').textContent=insight?'Why it matters · Foundry batch':'Why it matters';
    $('whySource').title=insight?'Pre-generated Microsoft Foundry interpretation. NOT live inference; automatically checked but not human-reviewed.':'';
    $('evidenceRef').textContent=`${e.id} · ${fmt(availableAt(e))} · ${playerName(e.player_id)}`;
    $('sourceBadge').textContent=state.aiText?'FOUNDRY REPHRASE / REVIEW':'AUTHORED / EVENT-LINKED';
    const facts=e.facts;
    $('proofTitle').textContent=`${e.id} · ${e.kind.replaceAll('_',' ').toUpperCase()} · ${e.outcome.replaceAll('_',' ')}`;
    let details=`Action ${fmt(e.observed_at_ms ?? e.t_ms)}; confirmed ${fmt(availableAt(e))}. ${playerName(e.player_id)} at x=${e.location_m.x}m, y=${e.location_m.y}m.`;
    if(e.recipient_id)details+=` Recipient: ${playerName(e.recipient_id)}.`;
    if(facts.forward_progress_m!==null)details+=` Estimated forward movement: ${facts.forward_progress_m}m.`;
    if(e.kind==='pressure')details+=` Nearest opponent: ${facts.nearest_opponent_distance_m}m (synthetic approximation).`;
    $('proofDetail').textContent=details;
    for(const btn of document.querySelectorAll('#eventList button')){
      const isSelected=btn.dataset.eventId===e.id;
      btn.classList.toggle('selected',isSelected);
      if(isSelected)btn.setAttribute('aria-current','true');else btn.removeAttribute('aria-current');
    }
    if(announce && changed && state.speech) {
      // A save may interrupt the shot description after only 400 ms.
      // Include the shot again so the essential outcome is never lost in speech.
      const spoken=e.id==='E09' ?
        (state.detail==='essential' ? 'Taylor shoots. Cole saves it! No goal.' :
          'Taylor shoots from inside the area. Cole makes the save, and no goal is scored.') : text;
      void speak(spoken,e.id,state.detail);
    }
  }
  function render(announce=false){
    const e=lastEvent(state.t); updateEvent(e,announce);
    renderFrame(state.t);updateCounts(state.t);
  }
  function setPlaying(playing){
    state.playing=playing;$('playText').textContent=playing?'Pause':'Play sequence';
    $('playIcon').textContent=playing?'Ⅱ':'▶';
    $('playButton').setAttribute('aria-label',playing?'Pause sequence':'Play sequence');
  }
  function pause(){setPlaying(false);state.previousTs=null;cancelVoice();}
  function seek(ms,announce=false){
    const prev=state.currentEvent?.id;
    state.t=Math.max(0,Math.min(maxMs,Number(ms)||0));
    if(prev!==lastEvent(state.t).id)cancelVoice();
    render(announce);
  }
  function animate(ts){
    if(state.playing){
      if(state.previousTs!==null){
        state.t=Math.min(maxMs,state.t+(ts-state.previousTs)*state.rate);
        render(true);
        if(state.t>=maxMs){setPlaying(false);cancelVoice();}
      }
      state.previousTs=ts;
    }else{state.previousTs=null;}
    requestAnimationFrame(animate);
  }
  $('playButton').addEventListener('click',()=>{
    if(state.playing){pause();return;}
    if(state.t>=maxMs)seek(0);
    setPlaying(true);
    if(state.speech)void speak(state.currentEvent.narration[state.detail],state.currentEvent.id,state.detail);
  });
  $('restartButton').addEventListener('click',()=>{pause();seek(0);});
  $('timeSlider').addEventListener('input',e=>{pause();seek(e.target.value);});
  $('speedSelect').addEventListener('change',e=>{state.rate=Number(e.target.value);});
  $('detailSelect').addEventListener('change',e=>{
    state.detail=e.target.value;$('narrationMode').textContent=state.detail.toUpperCase();
    if(!state.aiText)updateEvent(state.currentEvent,false);
    if(state.speech&&state.playing)void speak(state.currentEvent.narration[state.detail],state.currentEvent.id,state.detail);
  });
  for (const btn of document.querySelectorAll('.mode-button')){
    btn.addEventListener('click',()=>{
      state.mode=btn.dataset.mode;
      document.body.classList.toggle('audio-mode',state.mode==='audio');
      for(const b of document.querySelectorAll('.mode-button')){
        const active=b===btn;b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',String(active));
      }
      if(state.mode==='audio' && !state.speech) $('speechButton').focus();
    });
  }
  $('speechButton').addEventListener('click',()=>{
    state.speech=!state.speech;
    $('speechButton').setAttribute('aria-pressed',String(state.speech));
    // Avoid narrating the same live region twice when device speech is enabled.
    $('commentaryText').setAttribute('aria-live',state.speech?'off':'polite');
    $('speechButton').querySelector('span').textContent=state.speech?'Mute spoken commentary':'Enable spoken commentary';
    $('speechButton').firstChild.textContent=state.speech?'🔊 ':'🔇 ';
    if(!state.speech)cancelVoice();else if(state.currentEvent)void speak(state.currentEvent.narration[state.detail],state.currentEvent.id,state.detail);
  });
  $('voiceSelect').addEventListener('change',e=>{state.speechEngine=e.target.value;cancelVoice();});
  $('aiButton').addEventListener('click',async()=>{
    if(!state.azureAI)return;
    const eventId=state.currentEvent?.id;
    if(!eventId)return;
    const b=$('aiButton');b.disabled=true;b.textContent='Asking Foundry…';
    try{
      const response=await fetch('./api/narrate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({eventId,detail:state.detail})});
      const data=await response.json();
      if(!response.ok||data.event_id!==eventId||typeof data.narration!=='string')throw new Error(data.error||'Unexpected AI response');
      if(state.currentEvent?.id===eventId){state.aiText=data.narration;updateEvent(state.currentEvent,false);
        /* AI output is a text suggestion. Speech remains the original verified baseline. */}
    }catch(error){$('aiStatus').textContent=`(${error.message||'AI unavailable'})`;}
    finally{b.disabled=false;b.textContent='Ask Foundry to rephrase this event';}
  });
  async function loadCapabilities(){
    if(!/^https?:$/.test(window.location.protocol))return;
    try{
      const res=await fetch('./api/capabilities',{cache:'no-store'});
      if(!res.ok)return;
      const cap=await res.json();state.azureAI=cap.foundry===true;state.azureSpeech=cap.speech===true;
      if(state.azureAI){$('aiButton').disabled=false;$('aiButton').textContent='Ask Foundry to rephrase this event';}
      if(state.azureSpeech){const option=$('voiceSelect').querySelector('[value="azure"]');option.disabled=false;option.textContent='Azure Speech';}
    }catch(_){/* Static GitHub Pages is expected not to have a backend. */}
  }
  async function loadBatchInsights(){
    // GitHub Pages is static. These insights are a PRE-GENERATED model output,
    // never a live cloud request from the browser and never a source of match facts.
    if(!/^https?:$/.test(window.location.protocol))return;
    try {
      const response=await fetch('./public/data/foundry_insights.json',{cache:'no-store'});
      if(!response.ok)return; // Optional asset, absent until owner runs the Foundry exporter.
      const data=await response.json();
      if(data.source!=='microsoft_foundry_responses'||data.synthetic!==true||
         data.match_id!==match.match_id||data.generation_mode!=='offline_batch'||!Array.isArray(data.events))return;
      const next=new Map();
      for(const item of data.events){
        const event=events.find(e=>e.id===item.event_id);
        if(!event||item.available_at_ms!==availableAt(event)||
           item.evidence_ids?.length!==1||item.evidence_ids[0]!==event.id||
           item.automated_checks_passed!==true||item.human_reviewed!==false||
           typeof item.explanation!=='string'||item.explanation.length>160||
           item.explanation.length<12)continue;
        next.set(item.event_id,item);
      }
      state.foundryInsights=next;
      state.lastRenderedNarrationKey=null;
      updateEvent(state.currentEvent,false);
    }catch(_){/* Keep independently usable authored baseline. */}
  }
  render(false);requestAnimationFrame(animate);void loadCapabilities();void loadBatchInsights();
})();
