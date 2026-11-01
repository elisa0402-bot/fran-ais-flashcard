(function(root) {
  'use strict';
  const DAY = 86400000;
  function dayKey(time) { return new Date(time + 9 * 3600000).toISOString().slice(0,10); }
  function normalize(s) { return s.normalize('NFKC').toLocaleLowerCase('fr').replace(/[’‘]/g,"'").replace(/\s+/g,' ').trim(); }
  function emptyProgress() { return {due:0,reps:0,interval:0,ease:2.5,lapses:0,seen:false,successes:0}; }
  function validateCard(c) {
    return c && typeof c.id==='string' && c.id.length<160 && typeof c.fr==='string' && c.fr.trim().length>0 &&
      c.fr.length<2000 && typeof c.ko==='string' && c.ko.trim().length>0 && c.ko.length<4000 &&
      (!c.dates || (Array.isArray(c.dates) && c.dates.every(d=>typeof d==='string' && /^\d{4}-\d{2}-\d{2}$/.test(d)))) &&
      Array.isArray(c.examples) && c.examples.length<=20 && c.examples.every(e=>typeof e.fr==='string' && typeof e.ko==='string' && e.fr.length<6000 && e.ko.length<6000);
  }
  function mergeCards(oldCards,incoming) {
    const result = oldCards.map(c=>({...c,dates:[...(c.dates||[])]}));
    const map = new Map(result.map(c=>[normalize(c.fr),c]));
    const ids = new Set(result.map(c=>c.id));
    let added=0;
    for(const input of incoming) {
      if(!validateCard(input)) throw new Error('뜻과 예문 형식을 확인해 주세요.');
      const key=normalize(input.fr), prior=map.get(key);
      if(prior) {
        prior.dates=[...new Set([...(prior.dates||[]),...(input.dates||[])])].sort();
        if(prior.deck==='news' && input.deck==='news') {
          prior.ko=input.ko; prior.examples=input.examples;
        }
      } else {
        if(ids.has(input.id)) throw new Error('서로 다른 단어에 같은 번호가 있습니다.');
        const card={...input,dates:[...new Set(input.dates||[])]};
        result.push(card); map.set(key,card); ids.add(card.id); added++;
      }
    }
    return {cards:result,added};
  }
  function grade(progress,rating,now) {
    if(!['again','hard','good','easy'].includes(rating)) throw new Error('Invalid rating');
    const p={...emptyProgress(),...progress,seen:true,last:now};
    if(rating==='again') {
      p.interval=0; p.reps=0; p.lapses++; p.successes=0;
      p.ease=Math.max(1.3,p.ease-0.2); p.due=now+60000;
    } else if(rating==='hard') {
      p.interval=0; p.ease=Math.max(1.3,p.ease-0.1); p.due=now+600000;
    } else {
      const easy=rating==='easy';
      p.interval=p.reps===0 ? (easy?4:1) : p.reps===1 ? (easy?7:3) : Math.max(p.interval+1,Math.round(p.interval*p.ease*(easy?1.3:1)));
      p.reps++; p.successes++; if(easy)p.ease=Math.min(3.3,p.ease+0.15);
      p.due=now+Math.min(365,p.interval)*DAY;
    }
    return p;
  }
  function reverseUnlocked(progress,id) {
    return (progress[id+':fr']?.successes||0)>=2;
  }
  function candidates(cards,progress,settings,activity,now,mode,deck) {
    const today=dayKey(now);
    const newDirection=mode==='ko'?'ko':'fr';
    const used=new Set(activity.filter(a=>a.newWord&&a.dir===newDirection&&dayKey(a.time)===today).map(a=>a.id)).size;
    let remaining=Math.max(0,Number(settings.newPerDay||10)-used);
    const due=[], fresh=[];
    for(const c of cards) {
      if(deck!=='all' && c.deck!==deck) continue;
      if(mode!=='ko') {
        const p=progress[c.id+':fr'];
        if(p?.seen) { if(p.due<=now)due.push({card:c,dir:'fr',due:p.due}); }
        else fresh.push({card:c,dir:'fr',due:0});
      }
      if(mode==='ko' || (mode==='auto' && reverseUnlocked(progress,c.id))) {
        const p=progress[c.id+':ko'];
        if(p?.seen) { if(p.due<=now)due.push({card:c,dir:'ko',due:p.due}); }
        else if(mode==='ko') fresh.push({card:c,dir:'ko',due:0});
        else due.push({card:c,dir:'ko',due:0});
      }
    }
    due.sort((a,b)=>a.due-b.due);
    fresh.sort((a,b)=>(b.card.added||'').localeCompare(a.card.added||'')||a.card.fr.localeCompare(b.card.fr,'fr'));
    return due.concat(fresh.slice(0,remaining));
  }
  const api={DAY,dayKey,normalize,emptyProgress,validateCard,mergeCards,grade,reverseUnlocked,candidates};
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
  root.CarnetCore=api;
})(typeof globalThis!=='undefined'?globalThis:this);
