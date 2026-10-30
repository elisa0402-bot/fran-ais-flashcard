(function() {
  'use strict';
  const Core=window.CarnetCore, KEY='onyva-news-carnet-v1';
  const RAW='https://raw.githubusercontent.com/elisa0402-bot/fran-ais-flashcard/main/news/data.json';
  const $=id=>document.getElementById(id);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const defaults=()=>({schemaVersion:1,cards:[],progress:{},stars:[],settings:{newPerDay:10,speechRate:.9},activity:[],lastSync:0,updated:''});
  let state=defaults(),current=null,revealed=false,busy=false,toastTimer;
  try {
    const raw=localStorage.getItem(KEY);
    if(raw) {
      const parsed=JSON.parse(raw);
      if(parsed.schemaVersion!==1 || !Array.isArray(parsed.cards) || !parsed.cards.every(Core.validateCard)) throw Error('saved data');
      state={...defaults(),...parsed,settings:{...defaults().settings,...parsed.settings}};
    }
  } catch(error) {
    $('storage-warning').hidden=false;
    $('storage-warning').textContent='저장된 기록을 읽지 못해 새 표현으로 시작합니다. 기존 백업 파일이 있다면 설정에서 가져와 주세요.';
  }
  const merged=Core.mergeCards(state.cards,window.CARNET_SEED.cards);
  state.cards=merged.cards; state.updated=state.updated||window.CARNET_SEED.updated;
  function save() {
    try {localStorage.setItem(KEY,JSON.stringify(state));return true;}
    catch(e){$('storage-warning').hidden=false;return false;}
  }
  function toast(message) {
    clearTimeout(toastTimer); $('toast').textContent=message; $('toast').hidden=false;
    toastTimer=setTimeout(()=>$('toast').hidden=true,4200);
  }
  function learned(c) {
    return (state.progress[c.id+':fr']?.interval||0)>=7 && (state.progress[c.id+':ko']?.interval||0)>=7;
  }
  function stats() {
    const now=Date.now(),queue=Core.candidates(state.cards,state.progress,state.settings,state.activity,now,'auto','all');
    $('total-count').textContent=state.cards.length;$('due-count').textContent=queue.length;
    $('nav-count').textContent=queue.length;$('learned-count').textContent=state.cards.filter(learned).length;
    const doneToday=state.activity.filter(a=>Core.dayKey(a.time)===Core.dayKey(now)).length;
    $('session-progress').textContent=doneToday ? '오늘 '+doneToday+'회 복습했어요' : '하루 '+state.settings.newPerDay+'개의 새 표현';
    $('streak').textContent=doneToday ? '오늘 '+doneToday+'번, 기억을 꺼냈어요.' : '오늘도 한 걸음.';
    $('sync-details').textContent='어휘 기준일 '+state.updated+' · 총 '+state.cards.length+'개 표현 · '+(state.lastSync ? new Date(state.lastSync).toLocaleString('ko-KR',{timeZone:'Asia/Seoul'})+' 확인' : '첫 업데이트 확인 전');
    $('connection').textContent=state.lastSync ? '어휘 기준 '+state.updated : '저장된 단어로 학습 중';
  }
  function queue(){return Core.candidates(state.cards,state.progress,state.settings,state.activity,Date.now(),$('direction').value,'all');}
  function intervalLabel(ms){
    if(ms<3600000)return Math.max(1,Math.round(ms/60000))+'분 후';
    return Math.round(ms/Core.DAY)+'일 후';
  }
  function nextCard() {
    current=queue()[0]||null;revealed=false;
    $('flashcard').hidden=!current;$('empty').hidden=!!current;
    if(!current) {
      const locked=$('direction').value==='ko' && !state.cards.some(c=>Core.reverseUnlocked(state.progress,c.id));
      $('empty-note').textContent=locked ? '프랑스어→한국어에서 같은 표현을 두 번 기억하면 한국어→프랑스어 카드가 열립니다.' :
        '새 표현은 하루 '+state.settings.newPerDay+'개까지 학습합니다. 짧은 재학습은 1분 또는 10분 뒤 다시 열려요. 필요하면 설정에서 새 표현 수를 바꿀 수 있어요.';
      stats(); return;
    }
    const c=current.card,dir=current.dir;
    $('direction-label').textContent=dir==='fr'?'COMPRENDRE · 프랑스어 → 한국어':'S’EXPRIMER · 한국어 → 프랑스어';
    $('source-date').textContent=c.deck==='news'?'뉴스에서 만난 날 '+(c.dates||[]).slice(-1)[0]:'내가 추가한 표현';
    $('prompt-label').textContent=dir==='fr'?'이 표현의 뜻을 떠올려 보세요.':'프랑스어로 어떻게 말할까요?';
    $('question').textContent=dir==='fr'?c.fr:c.ko;$('question').lang=dir==='fr'?'fr':'ko';
    $('speak-question').hidden=dir!=='fr';
    $('answer-main').textContent=dir==='fr'?c.ko:c.fr;$('answer-main').lang=dir==='fr'?'ko':'fr';
    $('examples').innerHTML=c.examples.map((e,i)=>'<div class="example"><button data-example="'+i+'" aria-label="예문 듣기">♫</button><p class="fr" lang="fr">'+esc(e.fr)+'</p><p class="ko">'+esc(e.ko)+'</p></div>').join('');
    $('card-source').textContent=(c.source||'내가 추가한 표현')+' · 예문은 어휘 연습을 위해 작성했습니다.';
    $('answer').hidden=true;$('grades').hidden=true;$('reveal').hidden=false;
    const p=state.progress[c.id+':'+dir],now=Date.now();
    for(const rating of ['again','hard','good','easy'])$('interval-'+rating).textContent=intervalLabel(Core.grade(p,rating,now).due-now);
    stats();
  }
  function reveal() {
    if(!current||revealed)return;
    revealed=true;$('answer').hidden=false;$('grades').hidden=false;$('reveal').hidden=true;
  }
  function grade(rating) {
    if(!current||!revealed)return;
    const key=current.card.id+':'+current.dir,old=state.progress[key],now=Date.now();
    state.progress[key]=Core.grade(old,rating,now);
    state.activity.push({id:current.card.id,dir:current.dir,rating,time:now,newWord:current.dir==='fr'&&!old?.seen});
    if(state.activity.length>10000)state.activity=state.activity.slice(-10000);
    save();nextCard();
  }
  function speak(text) {
    if(!('speechSynthesis' in window)){toast('이 브라우저에서는 발음 듣기를 지원하지 않습니다.');return;}
    const synth=window.speechSynthesis,utterance=new SpeechSynthesisUtterance(text);
    utterance.lang='fr-FR';utterance.rate=Number(state.settings.speechRate);
    const voice=synth.getVoices().find(v=>v.lang.startsWith('fr'));if(voice)utterance.voice=voice;
    utterance.onerror=()=>toast('프랑스어 음성을 재생하지 못했습니다. 기기에 프랑스어 음성이 있는지 확인해 주세요.');
    synth.cancel();synth.speak(utterance);
  }
  function switchView(view) {
    if(!['study','library','settings'].includes(view))view='study';
    for(const name of ['study','library','settings'])$(name+'-view').hidden=name!==view;
    document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
    if(view==='library')renderLibrary();
    if(view==='settings'){stats();$('new-per-day').value=state.settings.newPerDay;$('speech-rate').value=state.settings.speechRate;}
    if(view==='study')nextCard();
    history.replaceState(null,'','#'+view);window.scrollTo(0,0);
  }
  function renderLibrary() {
    const query=Core.normalize($('search').value),filter=$('library-filter').value;
    const result=state.cards.filter(c=>{
      const hasSeen=state.progress[c.id+':fr']?.seen, isLearned=learned(c);
      if(filter==='new'&&hasSeen || filter==='learning'&&(!hasSeen||isLearned) || filter==='learned'&&!isLearned || filter==='starred'&&!state.stars.includes(c.id))return false;
      return !query||Core.normalize([c.fr,c.ko,...c.examples.flatMap(e=>[e.fr,e.ko])].join(' ')).includes(query);
    }).sort((a,b)=>(b.added||'').localeCompare(a.added||'')||a.fr.localeCompare(b.fr,'fr'));
    $('library-count').textContent=result.length+'개 표현 · 전체 '+state.cards.length+'개';
    $('word-list').innerHTML=result.map(c=>{
      const p=state.progress[c.id+':fr'],status=learned(c)?'익숙해졌어요':p?.seen?'학습 중':'처음 만나는 표현';
      return '<article class="word"><div class="word-head"><div class="word-title"><h3 lang="fr">'+esc(c.fr)+'</h3><p class="meaning">'+esc(c.ko)+'</p><div class="tags">'+esc(status)+' · '+esc(c.deck==='news'?'뉴스 · '+(c.dates||[]).join(', '):'내 표현')+'</div></div><button class="word-sound" data-speak="'+esc(c.id)+'" aria-label="표현 듣기">♫</button><button class="star '+(state.stars.includes(c.id)?'on':'')+'" data-star="'+esc(c.id)+'" aria-label="별표" aria-pressed="'+state.stars.includes(c.id)+'">'+(state.stars.includes(c.id)?'★':'☆')+'</button></div><details><summary>예문 보기</summary>'+c.examples.map(e=>'<div class="example"><p class="fr" lang="fr">'+esc(e.fr)+'</p><p class="ko">'+esc(e.ko)+'</p></div>').join('')+'</details></article>';
    }).join('')||'<div class="empty"><p>조건에 맞는 표현이 없습니다.</p></div>';
  }
  async function sync(manual=false) {
    if(busy)return;busy=true;$('sync-button').disabled=true;$('settings-sync').disabled=true;
    $('connection').textContent='새 표현 확인 중…';
    let failure;
    const urls=location.hostname==='localhost'||location.hostname==='127.0.0.1'?['./data.json',RAW]:[RAW,'./data.json'];
    for(const url of urls) {
      const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),10000);
      try {
        if(location.protocol==='file:'&&url.startsWith('.'))continue;
        const response=await fetch(url,{cache:'no-store',signal:controller.signal});
        if(!response.ok)throw Error('HTTP '+response.status);
        const data=await response.json();
        if(data.schemaVersion!==1||!Array.isArray(data.cards)||data.cards.length>20000||typeof data.updated!=='string')throw Error('잘못된 어휘 파일');
        const result=Core.mergeCards(state.cards,data.cards);state.cards=result.cards;state.lastSync=Date.now();
        if(data.updated>state.updated)state.updated=data.updated;
        const stored=save();stats();
        if(!current)nextCard();
        if(!$('library-view').hidden)renderLibrary();
        if(manual||result.added)toast(stored?(result.added?'새 표현 '+result.added+'개를 추가했어요.':'현재 어휘가 최신입니다.'):'새 표현을 받았지만 저장 공간이 부족합니다. 백업해 주세요.');
        failure=null;break;
      } catch(e){failure=e;} finally{clearTimeout(timer);}
    }
    if(failure){$('connection').textContent='오프라인 · 저장된 표현 사용';if(manual)toast('새 어휘를 확인하지 못했어요. 저장된 카드로 계속 학습할 수 있습니다.');}
    busy=false;$('sync-button').disabled=false;$('settings-sync').disabled=false;
  }
  function download(name,content,type) {
    const url=URL.createObjectURL(new Blob([content],{type}));
    const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);
  }
  function parseCSV(text) {
    const rows=[];let row=[],cell='',quoted=false;text=text.replace(/^\uFEFF/,'');
    for(let i=0;i<text.length;i++){
      const ch=text[i];
      if(ch==='"'){if(quoted&&text[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}
      else if(ch===','&&!quoted){row.push(cell);cell='';}
      else if((ch==='\n'||ch==='\r')&&!quoted){if(ch==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(s=>s.trim()))rows.push(row);row=[];cell='';}
      else cell+=ch;
    }
    if(quoted)throw Error('CSV의 따옴표를 확인해 주세요.');
    row.push(cell);if(row.some(s=>s.trim()))rows.push(row);return rows;
  }
  function importCSV(text) {
    const rows=parseCSV(text);if(!rows.length)throw Error('빈 파일입니다.');
    if(/^(front|프랑스어|foreign|fr)$/i.test(rows[0][0].trim()))rows.shift();
    return rows.map((r,i)=>{
      if(r.length<2)throw Error((i+1)+'번째 줄의 뜻이 비어 있습니다.');
      let fr=r[0].trim(),ko=r[1].trim();
      const named=fr.match(/^(?:단어|동사|표현|관용구|구문)\s*:\s*(.*)$/);
      if(named)fr=named[1];
      else if(/[가-힣]/.test(fr)&&/^[a-zà-ÿ'’]/i.test(ko)) {
        const question=fr;fr=ko.replace(/\s*\([^)]*[가-힣][^)]*\)\s*$/,'').trim();ko=question;
      }
      ko=ko.replace(/^의미:\s*/,'');
      return {id:'import-'+crypto.randomUUID(),fr,ko,deck:'personal',added:Core.dayKey(Date.now()),dates:[],source:'가져온 CSV',examples:[]};
    });
  }
  function validProgress(input,cards) {
    if(!input||typeof input!=='object'||Array.isArray(input))throw Error('진도 파일이 올바르지 않습니다.');
    const ids=new Set(cards.map(c=>c.id)),entries=[];
    for(const [key,p] of Object.entries(input)){
      const match=key.match(/^(.*):(fr|ko)$/);
      if(!match||!ids.has(match[1])||!p||typeof p!=='object')continue;
      for(const field of ['due','reps','interval','ease','lapses','successes'])if(p[field]!==undefined&&(!Number.isFinite(p[field])||p[field]<0))throw Error('진도 수치가 올바르지 않습니다.');
      entries.push([key,{...Core.emptyProgress(),...p,seen:!!p.seen}]);
    }
    return Object.fromEntries(entries);
  }
  async function importFile(file) {
    if(file.size>15*1024*1024)throw Error('15MB 이하 파일을 선택해 주세요.');
    const text=await file.text();
    if(file.name.toLowerCase().endsWith('.csv')){
      const result=Core.mergeCards(state.cards,importCSV(text));state.cards=result.cards;save();nextCard();renderLibrary();toast(result.added+'개 표현을 가져왔어요.');return;
    }
    const data=JSON.parse(text);
    if(data.type==='onyva-backup') {
      const incoming=data.state;
      if(!incoming||incoming.schemaVersion!==1||!Array.isArray(incoming.cards)||!incoming.cards.every(Core.validateCard))throw Error('이 앱의 백업 파일이 아닙니다.');
      const progress=validProgress(incoming.progress,incoming.cards);
      const activity=(incoming.activity||[]).filter(a=>typeof a.id==='string'&&Number.isFinite(a.time));
      if(!confirm('이 파일의 학습 진도를 복원할까요? 현재 진도는 파일의 진도로 바뀝니다. 먼저 백업하면 현재 진도도 보관할 수 있습니다.'))return;
      const combined=Core.mergeCards(incoming.cards,state.cards);
      state={...defaults(),...incoming,cards:combined.cards,progress,activity,stars:(incoming.stars||[]).filter(s=>typeof s==='string'),settings:{...defaults().settings,...incoming.settings}};
      const perDay=Number(state.settings.newPerDay);if(!Number.isFinite(perDay)||perDay<1||perDay>100)state.settings.newPerDay=10;
    } else {
      const cards=Array.isArray(data)?data:data.cards;
      if(!Array.isArray(cards))throw Error('어휘 목록이 없는 파일입니다.');
      const result=Core.mergeCards(state.cards,cards);state.cards=result.cards;toast(result.added+'개 표현을 추가했어요.');
    }
    save();nextCard();renderLibrary();stats();toast('가져오기를 마쳤어요.');
  }
  $('reveal').onclick=reveal;
  $('grades').onclick=e=>{const b=e.target.closest('[data-grade]');if(b)grade(b.dataset.grade);};
  $('examples').onclick=e=>{const b=e.target.closest('[data-example]');if(b&&current)speak(current.card.examples[Number(b.dataset.example)].fr);};
  $('speak-question').onclick=()=>{if(current)speak(current.card.fr);};
  $('direction').onchange=nextCard;
  document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>switchView(b.dataset.view));
  $('browse-button').onclick=()=>switchView('library');
  $('search').oninput=renderLibrary;$('library-filter').onchange=renderLibrary;
  $('word-list').onclick=e=>{
    const star=e.target.closest('[data-star]'),sound=e.target.closest('[data-speak]');
    if(star){const id=star.dataset.star;state.stars=state.stars.includes(id)?state.stars.filter(x=>x!==id):state.stars.concat(id);save();renderLibrary();}
    if(sound){const c=state.cards.find(c=>c.id===sound.dataset.speak);if(c)speak(c.fr);}
  };
  $('sync-button').onclick=()=>sync(true);$('settings-sync').onclick=()=>sync(true);
  $('new-per-day').onchange=e=>{state.settings.newPerDay=Number(e.target.value);save();stats();toast('하루 새 표현 '+state.settings.newPerDay+'개로 설정했어요.');};
  $('speech-rate').onchange=e=>{state.settings.speechRate=Number(e.target.value);save();};
  $('backup').onclick=()=>download('on-y-va-backup-'+Core.dayKey(Date.now())+'.json',JSON.stringify({type:'onyva-backup',exportedAt:new Date().toISOString(),state},null,2),'application/json');
  $('import-button').onclick=()=>$('import-file').click();
  $('import-file').onchange=async e=>{try{if(e.target.files[0])await importFile(e.target.files[0]);}catch(error){toast('가져오지 못했어요. '+error.message);}finally{e.target.value='';}};
  $('export-anki').onclick=()=>{
    const lines=['#separator:tab','#html:true','#columns:Front\tBack\tTags'];
    for(const c of state.cards){
      const ex=c.examples.map(e=>'<p>'+esc(e.fr)+'<br>'+esc(e.ko)+'</p>').join('');
      lines.push(['프→한: '+esc(c.fr),esc(c.ko)+ex,'onyva-news fr-kr'].map(s=>s.replace(/[\t\r\n]/g,' ')).join('\t'));
      lines.push(['한→프: '+esc(c.ko),esc(c.fr)+ex,'onyva-news kr-fr'].map(s=>s.replace(/[\t\r\n]/g,' ')).join('\t'));
    }
    download('on-y-va-anki.tsv',lines.join('\n'),'text/tab-separated-values;charset=utf-8');
  };
  $('open-add').onclick=()=>$('add-dialog').showModal();$('close-add').onclick=()=>$('add-dialog').close();
  $('add-form').onsubmit=e=>{
    e.preventDefault();const f=new FormData(e.target);
    const card={id:'personal-'+crypto.randomUUID(),fr:String(f.get('fr')).trim(),ko:String(f.get('ko')).trim(),examples:[{fr:String(f.get('exfr')).trim(),ko:String(f.get('exko')).trim()}],deck:'personal',added:Core.dayKey(Date.now()),dates:[],source:'내가 추가한 표현'};
    try{const result=Core.mergeCards(state.cards,[card]);state.cards=result.cards;save();$('add-dialog').close();e.target.reset();renderLibrary();stats();toast(result.added?'나의 표현을 추가했어요.':'이미 단어장에 있는 표현이에요.');}catch(error){toast(error.message);}
  };
  document.addEventListener('keydown',e=>{
    if(e.target.closest('input,textarea,select,dialog')||$('study-view').hidden)return;
    if(e.code==='Space'){e.preventDefault();reveal();}
    if(revealed&&['1','2','3','4'].includes(e.key)){e.preventDefault();grade(['again','hard','good','easy'][Number(e.key)-1]);}
  });
  document.addEventListener('visibilitychange',()=>{if(!document.hidden){stats();if(!current)nextCard();}});
  window.addEventListener('online',()=>sync());
  window.addEventListener('storage',e=>{if(e.key===KEY)toast('다른 창에서 진도가 바뀌었습니다. 이 창을 새로 열어 최신 진도를 불러와 주세요.');});
  if('serviceWorker' in navigator && /^https?:$/.test(location.protocol))navigator.serviceWorker.register('./sw.js').catch(()=>{});
  $('today').textContent=new Date().toLocaleDateString('ko-KR',{timeZone:'Asia/Seoul',year:'numeric',month:'long',day:'numeric',weekday:'short'});
  save();switchView(location.hash.slice(1)||'study');sync();
  setInterval(()=>sync(),15*60000);
  setInterval(()=>{stats();if(!current&&!$('study-view').hidden)nextCard();},30000);
})();
