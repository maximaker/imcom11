(function(){
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  requestAnimationFrame(function(){ document.body.setAttribute('data-ready','true'); });

  document.querySelectorAll('.rise > span').forEach(function(s,i){
    s.style.transitionDelay = (0.06 + i*0.075)+'s';
  });

  /* Split the statement into words so it can be read by the scroll. */
  var st = document.getElementById('statement');
  if (st){
    /* Which words light up is a copy decision, so it lives in the markup:
       data-key="never stuck with me." on the statement itself. */
    var keyWords = {};
    (st.getAttribute('data-key')||'').trim().split(/\s+/).forEach(function(k){
      if(k) keyWords[k]=1;
    });
    var words = st.textContent.trim().split(/\s+/);
    st.textContent='';
    words.forEach(function(word,i){
      var w=document.createElement('w');
      w.textContent=word;
      if(keyWords[word]) w.className='key';
      st.appendChild(w);
      if(i<words.length-1) st.appendChild(document.createTextNode(' '));
    });
  }

  /* ── The sieve: a pinned scene driven entirely by scroll position. ── */
  (function(){
    var NS='http://www.w3.org/2000/svg';
    var scene=document.getElementById('scene');
    if(!scene) return;
    var pin=scene.querySelector('.pin'),
        gDots=document.getElementById('dots'),
        halo=document.getElementById('halo'),
        counter=document.getElementById('counter'),
        caps=[].slice.call(document.querySelectorAll('#caption span')),
        ticks=[].slice.call(document.querySelectorAll('.ticks i'));
    var N=40;

    /* Deterministic, so the scatter is identical on every load and can never
       re-roll mid-scroll. */
    function rnd(i,salt){
      var x=Math.sin((i+1)*12.9898 + salt*78.233)*43758.5453;
      return x-Math.floor(x);
    }
    /* Survivors spread through the field, so narrowing reads as selection
       rather than "one region won". */
    function pick(from,count){
      var out=[],step=from.length/count;
      for(var i=0;i<count;i++) out.push(from[Math.floor(i*step+step/2)]);
      return out;
    }
    function gridPos(idx,count,cols,cx,cy,dx,dy){
      var rows=Math.ceil(count/cols),col=idx%cols,row=Math.floor(idx/cols);
      return {x:cx+(col-(cols-1)/2)*dx, y:cy+(row-(rows-1)/2)*dy};
    }

    var all=[]; for(var i=0;i<N;i++) all.push(i);
    var keep12=pick(all,12), keep4=pick(keep12,4), keep1=keep4[2];

    var dots=all.map(function(i){
      var el=document.createElementNS(NS,'circle');
      el.setAttribute('class','d'); el.setAttribute('r',4.6);
      el.setAttribute('cx',0); el.setAttribute('cy',0);
      gDots.appendChild(el);
      var k12=keep12.indexOf(i), k4=keep4.indexOf(i);
      return {
        el:el,
        scatter:{x:90+rnd(i,1)*820, y:30+rnd(i,2)*360},
        p0:gridPos(i,N,5,500,210,46,42),
        p1:k12>=0?gridPos(k12,12,3,500,210,62,58):null,
        p2:k4 >=0?gridPos(k4,4,2,500,210,86,76):null,
        p3:i===keep1?{x:500,y:210}:null,
        seed:rnd(i,3)
      };
    });

    /* The viewBox is 1000 units wide, so on a phone a 4.6-unit dot renders at
       about 1.5px. Scale the marks up as the frame shrinks. */
    var dotScale=1;
    function measureScale(){
      var w=pin.querySelector('svg').getBoundingClientRect().width||1000;
      dotScale = w<620 ? Math.min(2.6, 1000/Math.max(w,260)) : 1;
    }

    function clamp(v){return v<0?0:v>1?1:v;}
    function smooth(t){t=clamp(t);return t*t*(3-2*t);}
    function seg(p,a,b){return smooth((p-a)/(b-a));}
    function lerp(a,b,t){return a+(b-a)*t;}

    var A=[0.00,0.16], B=[0.16,0.36], C=[0.36,0.54], D=[0.54,0.70], E=[0.70,0.86];
    /* 0.86 → 1.00 is deliberately empty: the answer holds for a beat before
       the section releases, instead of resolving and vanishing. */

    function render(p){
      var tB=seg(p,B[0],B[1]), tC=seg(p,C[0],C[1]),
          tD=seg(p,D[0],D[1]), tE=seg(p,E[0],E[1]);

      dots.forEach(function(d){
        var x=d.scatter.x, y=d.scatter.y;
        var settle=clamp(tB*1.35-d.seed*0.35);
        x=lerp(x,d.p0.x,settle); y=lerp(y,d.p0.y,settle);

        var alive=1, r=4.6*dotScale;
        if(d.p1){ x=lerp(x,d.p1.x,tC); y=lerp(y,d.p1.y,tC); }
        else if(tC>0){ alive=1-tC; y+=tC*26; }

        if(d.p2){ x=lerp(x,d.p2.x,tD); y=lerp(y,d.p2.y,tD); }
        else if(d.p1&&tD>0){ alive=1-tD; y+=tD*26; }

        if(d.p3){ x=lerp(x,d.p3.x,tE); y=lerp(y,d.p3.y,tE);
                  r=lerp(4.6*dotScale, 13*Math.min(dotScale,1.7), tE); }
        else if(d.p2&&tE>0){ alive=1-tE; y+=tE*26; }

        var entry=clamp(seg(p,A[0],A[1])*1.6-d.seed*0.25);
        d.el.setAttribute('transform','translate('+x.toFixed(1)+','+y.toFixed(1)+')');
        d.el.setAttribute('r',r.toFixed(1));
        d.el.style.opacity=(alive*(0.25+0.75*entry)).toFixed(3);
        d.el.classList.toggle('final', !!(d.p3&&tE>0.55));
      });

      halo.classList.toggle('on', tE>0.9);

      /* Stage flips near the END of each transition, so the number on screen
         always matches the number of dots actually left. */
      var stage = p<0.51?0 : p<0.67?1 : p<0.83?2 : 3;
      caps.forEach(function(c){c.setAttribute('data-on',String(+c.dataset.i===stage));});
      ticks.forEach(function(t){t.setAttribute('data-fill',String(+t.dataset.k<=stage));});
      counter.textContent=['40 possible','12 plausible','4 worth testing','1 tested'][stage];
    }

    if(reduce){ measureScale(); render(1); return; }

    var t=false;
    function sieveScroll(){
      if(t) return; t=true;
      requestAnimationFrame(function(){
        var total=scene.offsetHeight-pin.offsetHeight;
        var p=total>0?clamp(-scene.getBoundingClientRect().top/total):0;
        render(p); t=false;
      });
    }
    addEventListener('scroll',sieveScroll,{passive:true});
    addEventListener('resize',function(){measureScale();sieveScroll();},{passive:true});
    measureScale(); render(0); sieveScroll();
  })();

  var revealTargets = document.querySelectorAll('.rev,.step,.asset');
  if (reduce || !('IntersectionObserver' in window)){
    revealTargets.forEach(function(t){t.setAttribute('data-in','true');});
    if(st) st.querySelectorAll('w').forEach(function(w){w.setAttribute('data-lit','true');});
  } else {
    var io=new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(!e.isIntersecting) return;
        e.target.setAttribute('data-in','true');
        io.unobserve(e.target);
      });
    },{rootMargin:'0px 0px -8% 0px',threshold:.12});
    revealTargets.forEach(function(t){io.observe(t);});
    document.querySelectorAll('.steps').forEach(function(g){
      g.querySelectorAll('.step').forEach(function(s,i){s.style.transitionDelay=(i*0.09)+'s';});
    });
  }

  /* Each section's own marginalia is its marker. No second list to keep in sync. */
  var fill = document.getElementById('spinefill');
  var marks = [].slice.call(document.querySelectorAll('[data-node]')).map(function(sec){
    return { sec: sec, note: sec.querySelector('.margin') };
  }).filter(function(m){ return m.note; });

  function absTop(el){ return el.getBoundingClientRect().top + window.scrollY; }

  var railEl = document.querySelector('.spine');

  function placeRail(){
    /* The rule runs out from under the masthead, so it has to know how tall the
       bar is. Measured rather than hardcoded. */
    var bar = document.getElementById('top');
    if(bar) document.documentElement.style
              .setProperty('--spine-top', bar.offsetHeight + 'px');
    if(!railEl || getComputedStyle(railEl).display === 'none') return;
    var col = document.querySelector('.band .margin');
    if(!col) return;
    var gap = parseFloat(getComputedStyle(document.documentElement)
                .getPropertyValue('--margin-gap')) || 64;
    var x = col.getBoundingClientRect().right + gap / 2;
    railEl.style.left = x + 'px';
    /* The foot disc is absolutely positioned inside .railfoot, so its `left`
       resolves against that box, not the viewport. Convert the coordinate. */
    var foot = document.querySelector('.railfoot');
    var link = foot && foot.querySelector('a');
    if(link) link.style.left = (x - foot.getBoundingClientRect().left) + 'px';
  }

  function measure(){
    placeRail();
    marks.forEach(function(m){
      m.a = absTop(m.sec);
      m.b = m.a + m.sec.offsetHeight;
    });
  }

  var ticking=false;
  function onScroll(){
    if(ticking) return; ticking=true;
    requestAnimationFrame(function(){
      var h=document.documentElement.scrollHeight-window.innerHeight;
      var p=h>0?Math.min(Math.max(window.scrollY/h,0),1):0;
      if(fill) fill.style.transform='scaleY('+p.toFixed(4)+')';
      document.getElementById('top').setAttribute('data-stuck', window.scrollY>10?'true':'false');

      var mid=window.scrollY+window.innerHeight/2;
      marks.forEach(function(m){
        m.note.setAttribute('data-on', (mid>=m.a && mid<m.b) ? 'true':'false');
      });

      /* Light the statement word by word as it crosses the middle of the screen. */
      if(st && !reduce){
        var r=st.getBoundingClientRect();
        var prog=(window.innerHeight*0.82 - r.top)/(r.height + window.innerHeight*0.30);
        prog=Math.min(Math.max(prog,0),1);
        var ws=st.querySelectorAll('w');
        ws.forEach(function(w,i){
          w.setAttribute('data-lit', (i/ws.length) < prog ? 'true':'false');
        });
      }
      ticking=false;
    });
  }
  addEventListener('scroll',onScroll,{passive:true});
  addEventListener('resize',function(){measure();onScroll();},{passive:true});
  measure(); onScroll();

  /* Pointer lamp, desktop only. */
  var hero=document.getElementById('heroband');
  if(hero && !reduce && matchMedia('(min-width:980px) and (pointer:fine)').matches){
    var tx=60,ty=40,cx=60,cy=40,raf=0;
    hero.addEventListener('pointermove',function(e){
      var r=hero.getBoundingClientRect();
      tx=((e.clientX-r.left)/r.width)*100;
      ty=((e.clientY-r.top)/r.height)*100;
      hero.setAttribute('data-lamp','true');
      if(!raf) raf=requestAnimationFrame(loop);
    });
    hero.addEventListener('pointerleave',function(){hero.setAttribute('data-lamp','false');});
    function loop(){
      cx+=(tx-cx)*0.09; cy+=(ty-cy)*0.09;
      hero.style.setProperty('--mx',cx.toFixed(2)+'%');
      hero.style.setProperty('--my',cy.toFixed(2)+'%');
      raf=(Math.abs(tx-cx)>0.1||Math.abs(ty-cy)>0.1)?requestAnimationFrame(loop):0;
    }
  }

  /* The CTA leans toward the pointer as it approaches, then springs back.
     Small enough to feel like attention rather than a trick. */
  var cta=document.getElementById('cta');
  if(cta && !reduce && matchMedia('(pointer:fine)').matches){
    var cx=0,cy=0,tx=0,ty=0,craf=0;
    function ctaLoop(){
      cx+=(tx-cx)*0.16; cy+=(ty-cy)*0.16;
      cta.style.transform='translate('+cx.toFixed(2)+'px,'+cy.toFixed(2)+'px)';
      craf=(Math.abs(tx-cx)>0.08||Math.abs(ty-cy)>0.08)?requestAnimationFrame(ctaLoop):0;
    }
    addEventListener('pointermove',function(e){
      var r=cta.getBoundingClientRect();
      var dx=e.clientX-(r.left+r.width/2), dy=e.clientY-(r.top+r.height/2);
      var dist=Math.hypot(dx,dy), reach=r.width*0.9;
      if(dist<reach){ var pull=(1-dist/reach)*0.22; tx=dx*pull; ty=dy*pull; }
      else { tx=0; ty=0; }
      if(!craf) craf=requestAnimationFrame(ctaLoop);
    },{passive:true});
  }

  /* Intro-call form: validate on blur, never on keystroke, and keep the error
     next to the field it belongs to. */
  var form=document.getElementById('intro-form');
  if(form){
    var status=document.getElementById('form-status');
    var submit=form.querySelector('button[type="submit"]');
    var inputs=form.querySelectorAll('input,textarea');

    function wrap(el){return el.closest('.field');}
    function check(el){
      var w=wrap(el); if(!w) return true;
      var ok=el.checkValidity();
      w.setAttribute('data-invalid', ok?'false':'true');
      el.setAttribute('aria-invalid', ok?'false':'true');
      return ok;
    }
    inputs.forEach(function(el){
      el.addEventListener('blur',function(){check(el);});
      el.addEventListener('input',function(){
        var w=wrap(el);
        if(w && w.getAttribute('data-invalid')==='true') check(el);
      });
    });

    form.addEventListener('submit',function(e){
      e.preventDefault();
      var firstBad=null;
      inputs.forEach(function(el){ if(!check(el) && !firstBad) firstBad=el; });
      if(firstBad){
        firstBad.focus();
        firstBad.scrollIntoView({block:'center',behavior:reduce?'auto':'smooth'});
        return;
      }
      submit.disabled=true;
      var label=submit.querySelector('span')||submit;
      var original=label.textContent;
      label.textContent='Sending';
      /* No backend yet: swap this for a real endpoint or a scheduler embed. */
      window.setTimeout(function(){
        form.hidden=true;
        if(status){ status.setAttribute('data-visible','true'); status.focus(); }
        submit.disabled=false; label.textContent=original;
      },700);
    });
  }

  /* Mobile menu. */
  var navBtn=document.querySelector('.navtoggle');
  var topBar=document.getElementById('top');
  if(navBtn && topBar){
    navBtn.addEventListener('click',function(){
      var open=topBar.getAttribute('data-open')==='true';
      topBar.setAttribute('data-open', open?'false':'true');
      navBtn.setAttribute('aria-expanded', open?'false':'true');
      navBtn.setAttribute('aria-label', open?'Open menu':'Close menu');
    });
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape' && topBar.getAttribute('data-open')==='true'){
        topBar.setAttribute('data-open','false');
        navBtn.setAttribute('aria-expanded','false');
        navBtn.focus();
      }
    });
  }

  /* Expandable deliverables. */
  document.querySelectorAll('.asset button').forEach(function(btn){
    btn.addEventListener('click',function(){
      var row=btn.closest('.asset');
      var open=row.getAttribute('data-open')==='true';
      row.setAttribute('data-open', open?'false':'true');
      btn.setAttribute('aria-expanded', open?'false':'true');
    });
  });

})();
