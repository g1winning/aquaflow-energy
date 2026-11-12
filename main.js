/* AquaFlow Energy — page behaviour (main page only) */
(function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Where the investor enquiry form delivers. FormSubmit sends a one-time activation email
     to this address on the first submission; nothing arrives until that link is clicked. */
  const FORM_TO='lucabrew@gmail.com';

  /* legacy deep link: the FAQ used to live at #faq on this page */
  if(location.hash==='#faq'){location.replace('faq.html');return}

  /* ---------- sites dashboard: live-looking readouts ---------- */
  (function(){
    const clock=$('d-clock');if(!clock)return;
    const flow=$('d-flow'),set=$('d-set'),depth=$('d-depth'),pw=$('d-pw'),out=$('d-out'),state=$('d-state');
    const rho=1025,cp=0.35; // sea water density, power coefficient
    let t=0;
    function tick(){
      t+=1;
      const now=new Date();
      clock.textContent=now.toTimeString().slice(0,8);
      if(t%2===0){
        const u=1.72+Math.sin(t/9)*0.09+(Math.random()-.5)*0.04;
        const pa=0.5*rho*u*u*u*cp/1000; // kW/m²
        flow.textContent=u.toFixed(2)+' m/s';
        set.textContent=(214+Math.round(Math.sin(t/13)*3))+'°';
        depth.textContent=(14.2+Math.sin(t/31)*0.3).toFixed(1)+' m';
        pw.textContent=pa.toFixed(2)+' kW';
        out.textContent=(pa*4*Math.PI*Math.pow(3.1,2)/1000*0.9).toFixed(2)+' MW'; // 4 rotors, Ø6.2 m, 90% availability
        state.textContent=u>1.6?'EBB':'EBB · EASING';
      }
    }
    tick();if(!reduced)setInterval(tick,1000);
  })();

  /* ---------- build accordion: one open at a time, image follows ---------- */
  const acc=$('acc'),bpic=$('bpic'),bcap=$('bcap');
  acc.querySelectorAll('details').forEach(d=>d.addEventListener('toggle',()=>{
    if(!d.open)return;
    acc.querySelectorAll('details').forEach(o=>{if(o!==d)o.open=false});
    bpic.style.opacity=0;setTimeout(()=>{bpic.style.backgroundImage='url('+d.dataset.img+')';bcap.textContent=d.dataset.cap;bpic.style.opacity=1},200);
  }));

  /* ---------- markets: cycles on its own, pauses on hover/focus ---------- */
  /* slide copy lives in #mk-src in index.html (so it is real page content); read it here */
  const M=Array.from(document.querySelectorAll('#mk-src article')).map(a=>{const l=a.querySelector('a');return{k:a.querySelector('.k').textContent,h:a.querySelector('h3').textContent,p:a.querySelector('p:not(.k)').textContent,a:[l.textContent,l.getAttribute('href')]}});
  const mk=$('mk'),bgs=mk.querySelectorAll('.bg'),prog=$('mk-prog').children;
  const PERIOD=7000;let mi=0,timer=0;
  function showM(i){
    mi=(i+M.length)%M.length;const m=M[mi];
    bgs.forEach((b,j)=>b.classList.toggle('on',j===mi));
    $('mk-n').textContent=String(mi+1).padStart(2,'0')+' / 04';$('mk-k').textContent=m.k;$('mk-h').textContent=m.h;$('mk-p').textContent=m.p;
    $('mk-a').href=m.a[1];$('mk-a').querySelector('span').textContent=m.a[0];
    Array.from(prog).forEach((p,j)=>{p.classList.remove('run','done');if(j<mi)p.classList.add('done');if(j===mi){void p.offsetWidth;p.classList.add('run')}});
    restart();
  }
  function restart(){clearTimeout(timer);if(!reduced)timer=setTimeout(()=>showM(mi+1),PERIOD)}
  $('mk-prev').onclick=()=>showM(mi-1);$('mk-next').onclick=()=>showM(mi+1);
  Array.from(prog).forEach((p,j)=>p.onclick=()=>showM(j));
  let remaining=PERIOD,pausedAt=0;
  mk.addEventListener('mouseenter',()=>{mk.classList.add('paused');clearTimeout(timer)});
  mk.addEventListener('mouseleave',()=>{mk.classList.remove('paused');restart()});
  mk.addEventListener('focusin',()=>{mk.classList.add('paused');clearTimeout(timer)});
  mk.addEventListener('focusout',()=>{mk.classList.remove('paused');restart()});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)clearTimeout(timer);else restart()});
  if(reduced)$('mk-auto').textContent='USE THE ARROWS';
  showM(0);

  /* ---------- engineering review quotes (verbatim from the review) ---------- */
  /* quote copy lives in #rq-src in index.html; the tab buttons are already in the page */
  const Q=Array.from(document.querySelectorAll('#rq-src li')).map(li=>[null,li.textContent.trim(),li.dataset.img]);
  const tabs=$('rq-tabs');
  tabs.querySelectorAll('button').forEach((b,i)=>{b.onclick=()=>showQ(i)});
  function showQ(i){$('rq-q').textContent=Q[i][1];$('rq-n').textContent=String(i+1).padStart(2,'0');$('rq-card').style.backgroundImage='url('+Q[i][2]+')';
    tabs.querySelectorAll('button').forEach((b,j)=>b.setAttribute('aria-selected',j===i))}
  showQ(0);

  /* ---------- counters: numbers roll up when they scroll in ---------- */
  const fmt=(n,dec)=>n.toLocaleString('en-AU',{minimumFractionDigits:dec,maximumFractionDigits:dec});
  function rollTo(el,target,opts){
    const dec=opts.dec||0,pre=opts.prefix||'',suf=opts.suffix||'',ms=opts.ms||1400,from=opts.from||0;
    if(reduced){el.innerHTML=pre+fmt(target,dec)+(opts.em?'<em>'+suf+'</em>':suf);return}
    const t0=performance.now();el.classList.add('lit');
    const ease=t=>1-Math.pow(1-t,3);
    (function step(ts){
      const k=Math.min(1,(ts-t0)/ms);const v=from+(target-from)*ease(k);
      el.innerHTML=pre+fmt(v,dec)+(opts.em?'<em>'+suf+'</em>':suf);
      if(k<1)requestAnimationFrame(step);else setTimeout(()=>el.classList.remove('lit'),600);
    })(t0);
  }
  if('IntersectionObserver' in window){
    const cio=new IntersectionObserver(es=>es.forEach(e=>{
      if(!e.isIntersecting)return;const el=e.target;cio.unobserve(el);
      const d=el.dataset;
      setTimeout(()=>rollTo(el,parseFloat(d.count),{dec:parseInt(d.dec||'0',10),prefix:d.prefix,suffix:d.suffix,ms:1500+Math.random()*500}),parseInt(d.delay||'0',10));
    }),{threshold:.6});
    document.querySelectorAll('[data-count]').forEach((el,i)=>{el.dataset.delay=String((i%4)*120);cio.observe(el)});
  }

  /* ---------- bottom line: the plan's cases ---------- */
  const CASES={
    low:   {r3:278, r5:2335, e5:1095, c5:997,  s:['Only the first 50 MW in year three','The balance of the units falls in years four and five','Before interest, tax and depreciation','Peak funding need US$3.5M, inside year one'],
            note:'Low case: the first 50 MW, the part the plan calls very likely, is the only delivery in year three; the rest follows in years four and five. These are projections from the plan’s model, not forecasts, and the trials will change them.'},
    base:  {r3:1072,r5:2130, e5:1003, c5:1179, s:['The first 50 MW order is the anchor','Unit sales, batteries, leases, service, licences','Before interest, tax and depreciation','Peak funding need US$3.5M, inside year one'],
            note:'Base case: 1,320 MW installed by the fifth year, with 200 MW delivered in year three. Data-centre and city units sell at US$5.0M per MW for the first 50 MW, falling to US$3.5M. These are projections from the plan’s model, not forecasts, and the trials will change them.'},
    growth:{r3:1574,r5:10963,e5:5428, c5:4504, s:['Sixty cities, each with its own programme','5,000 MW more built by licensees','Before interest, tax and depreciation','Deposits on next year’s orders fund this year’s components'],
            note:'Growth case: sixty cities take up the model, with 5,000 MW built by licensed partners on top of AFE’s own plants. An illustration of scale rather than a forecast. The trials will change every number here.'}
  };
  const blGrid=$('bl-grid');let curCase='base';
  function showCase(name){
    const c=CASES[name];if(!c)return;const prev=CASES[curCase];curCase=name;
    document.querySelectorAll('.cases button').forEach(b=>b.setAttribute('aria-selected',b.dataset.case===name));
    ['r3','r5','e5','c5'].forEach((k,i)=>{const el=blGrid.querySelector('[data-k="'+k+'"]');rollTo(el,c[k],{prefix:'US$',suffix:'M',em:true,ms:900,from:prev[k]});$('bl-s'+(i+1)).textContent=c.s[i]});
    $('bl-note').textContent=c.note;
  }
  document.querySelectorAll('.cases button').forEach(b=>b.onclick=()=>showCase(b.dataset.case));

  /* ---------- investor enquiry form (FormSubmit, AJAX) ---------- */
  const form=$('enquire'),status=$('fstatus');let sending=false;
  form.addEventListener('submit',async e=>{
    e.preventDefault();if(sending)return;
    const btn=form.querySelector('button[type=submit]'),lbl=btn.querySelector('span');
    const name=form.name.value.trim(),email=form.email.value.trim();
    if(!name||!email||!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)){
      status.hidden=false;status.className='fstatus err';status.textContent='Please add your name and a working email address.';return;
    }
    const data=new FormData(form);
    data.set('wants',Array.from(form.querySelectorAll('input[name=wants]:checked')).map(c=>c.value).join(', ')||'Not specified');
    data.append('_replyto',email);
    data.append('page',location.href);
    sending=true;btn.disabled=true;lbl.textContent='Sending…';status.hidden=true;
    try{
      const r=await fetch('https://formsubmit.co/ajax/'+FORM_TO,{method:'POST',body:data,headers:{'Accept':'application/json'}});
      if(!r.ok)throw new Error('bad status');
      const res=await r.json().catch(()=>({}));
      if(res.success===false||res.success==='false')throw new Error('rejected');
      status.className='fstatus';status.textContent='Thank you, '+name.split(' ')[0]+'. Your enquiry is on its way. The NDA comes with our first reply.';
      form.reset();lbl.textContent='Sent';sending=false;
    }catch(err){
      status.className='fstatus err';status.textContent='That did not send. Email geoffrey@aquaflowenergy.com directly and we will reply the same way.';
      sending=false;btn.disabled=false;lbl.textContent='Send enquiry';
    }
    status.hidden=false;
  });

  /* ---------- hero video: respect reduced motion, retry play if autoplay was blocked ---------- */
  const hv=$('herovid');
  if(reduced){hv.removeAttribute('autoplay');hv.pause()}
  else{const pl=()=>{const r=hv.play();if(r&&r.catch)r.catch(()=>{})};pl();addEventListener('pointerdown',pl,{once:true})}

  /* ---------- second film: fetch and play only when it scrolls into view ---------- */
  const fv=$('filmvid');
  if(fv&&!reduced){
    const startFilm=()=>{fv.preload='auto';const r=fv.play();if(r&&r.catch)r.catch(()=>{})};
    if('IntersectionObserver' in window){
      const fio=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){startFilm();fio.disconnect()}}),{rootMargin:'300px 0px'});
      fio.observe(fv);
    }else startFilm();
  }

  /* ---------- gentle reveal; content is visible at rest ---------- */
  if('IntersectionObserver' in window && !reduced){
    const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.remove('pre');io.unobserve(e.target)}}),{threshold:.15});
    document.querySelectorAll('.reveal').forEach(el=>{const r=el.getBoundingClientRect();if(r.top>innerHeight){el.classList.add('pre');io.observe(el)}});
  }
})();
