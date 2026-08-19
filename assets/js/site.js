(function(){
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* data-ready starts the masked headline. On a first load the animation owns the
     moment that happens, so it says when. */
  function markReady(){ document.body.setAttribute('data-ready','true'); }
  if (document.documentElement.getAttribute('data-intro') === 'running'){
    document.addEventListener('intro:ready', markReady, {once:true});
  } else {
    requestAnimationFrame(markReady);
  }

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
        seed:rnd(i,3),
        /* Separate draws. Reusing seed would have made the dots that arrive last
           also the ones that leave last, and a field that culls in the same order
           it filled reads as a list being processed rather than a sieve. */
        cull:rnd(i,4),
        drift:rnd(i,5),
        away:rnd(i,6),
        last:{t:'',r:'',o:'',f:null}
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

    /* A dot's own clock inside a stage. The stage runs 0..1; this hands each dot a
       slightly later start according to its seed, and widens the run so every one
       of them still finishes exactly at 1 rather than being cut off mid-move.
       The entrance already did this and the culls did not, which was the whole
       problem: forty dots arrived one at a time and then twenty-eight left in a
       single block, so the field filled like a crowd and emptied like a curtain. */
    function own(t,seed,spread){ return clamp(t*(1+spread)-seed*spread); }

    /* Culled dots are pushed out of the field rather than dropped down it. Every one
       of them used to travel the same 26 units straight down, which reads as gravity
       -- the same thing happening to all of them -- where a sieve is supposed to be
       rejecting each one on its own account. Radially outward from the centre says
       discarded, the distance varies per dot, and a little downward bias keeps it
       from looking like an explosion. pushX carries the x out, since a JS function
       returns one value and this is called in an expression. */
    var pushX=0;
    function push(x,y,g,d,scale){
      var dx=x-500, dy=y-210, len=Math.sqrt(dx*dx+dy*dy)||1;
      var dist=g*(20+d.drift*34)*scale;
      pushX=x+(dx/len)*dist*(0.7+d.away*0.6);
      return y+(dy/len)*dist+g*12;
    }

    var A=[0.00,0.16], B=[0.16,0.36], C=[0.36,0.54], D=[0.54,0.70], E=[0.70,0.86];
    /* 0.86 → 1.00 is deliberately empty: the answer holds for a beat before
       the section releases, instead of resolving and vanishing. */

    function render(p){
      var tB=seg(p,B[0],B[1]), tC=seg(p,C[0],C[1]),
          tD=seg(p,D[0],D[1]), tE=seg(p,E[0],E[1]);

      dots.forEach(function(d){
        var x=d.scatter.x, y=d.scatter.y;
        var settle=own(tB,d.seed,0.35);
        x=lerp(x,d.p0.x,settle); y=lerp(y,d.p0.y,settle);

        var alive=1, r=4.6*dotScale, g;
        /* Survivors regroup on a light stagger. The formation still has to read as
           a formation, so this is a quarter of what the culls get: enough that the
           dots do not arrive as one piece, not enough to lose the shape. */
        if(d.p1){ g=own(tC,d.seed,0.22); x=lerp(x,d.p1.x,g); y=lerp(y,d.p1.y,g); }
        else if(tC>0){ g=own(tC,d.cull,0.6); alive=1-g; y=push(x,y,g,d,1); x=pushX; }

        if(d.p2){ g=own(tD,d.seed,0.22); x=lerp(x,d.p2.x,g); y=lerp(y,d.p2.y,g); }
        else if(d.p1&&tD>0){ g=own(tD,d.cull,0.6); alive=1-g; y=push(x,y,g,d,1); x=pushX; }

        if(d.p3){ x=lerp(x,d.p3.x,tE); y=lerp(y,d.p3.y,tE);
                  /* Past full size and back. The one that survives should arrive
                     with some weight rather than easing to a halt for the whole
                     segment and stopping dead on the last frame.
                     The growth is compressed into the first four fifths so there is
                     something for the overshoot to ride past: a bump that has to be
                     zero at tE=1 cannot exceed a size the dot only reaches at tE=1,
                     which is why the earlier attempt at this cleared its target by
                     2% by accident rather than by 7.5% on purpose. Peaks at 13.97,
                     settles on 13.00. */
                  var R=13*Math.min(dotScale,1.7);
                  r=lerp(4.6*dotScale, R, smooth(clamp(tE/0.8)))
                    + R*0.075*Math.sin(Math.PI*clamp((tE-0.55)/0.45)); }
        else if(d.p2&&tE>0){ g=own(tE,d.cull,0.6); alive=1-g; y=push(x,y,g,d,1); x=pushX; }

        var entry=clamp(seg(p,A[0],A[1])*1.6-d.seed*0.25);
        /* Written only when the value actually changes. Three attributes across
           forty dots is a hundred and twenty writes a frame, and the radius is
           identical on thirty-nine of them for the whole scroll: setting an SVG
           attribute costs a string parse whether or not it differs. */
        var ts='translate('+x.toFixed(1)+','+y.toFixed(1)+')',
            rs=r.toFixed(1),
            os=(alive*(0.25+0.75*entry)).toFixed(3),
            fs=!!(d.p3&&tE>0.55);
        if(ts!==d.last.t){ d.el.setAttribute('transform',ts); d.last.t=ts; }
        if(rs!==d.last.r){ d.el.setAttribute('r',rs); d.last.r=rs; }
        if(os!==d.last.o){ d.el.style.opacity=os; d.last.o=os; }
        if(fs!==d.last.f){ d.el.classList.toggle('final',fs); d.last.f=fs; }
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
    /* Staggered 70ms within a group, which the design system asks for and this did
       not do: everything that crossed the line in one observer batch arrived on the
       same frame, so a four-up grid appeared as one object rather than as four
       things. A batch is the group -- the browser hands over everything that
       crossed together -- so they are bucketed by parent and delayed by their index
       within their own bucket. Sorted by document position first, because the
       observer makes no promise about entry order and an unsorted stagger would
       run a row in whatever sequence the intersections happened to be reported.
       Capped at six, so a long list does not have its last item waiting most of a
       second for its turn. */
    var STAGGER = 0.07, STAGGER_MAX = 6;
    var io=new IntersectionObserver(function(es){
      var arriving = es.filter(function(e){return e.isIntersecting;});
      arriving.sort(function(a,b){
        var r = a.target.compareDocumentPosition(b.target);
        return (r & Node.DOCUMENT_POSITION_FOLLOWING) ? -1 : 1;
      });
      var seen = new Map();
      arriving.forEach(function(e){
        var group = e.target.parentElement || document.body;
        var i = seen.get(group) || 0;
        seen.set(group, i + 1);
        /* Only if nothing has set one already: .rev pieces inside the intro are
           handed their timing by intro.js, and overwriting it would desynchronise
           the handover. */
        if(i && !e.target.style.transitionDelay){
          /* Rounded: 3 * 0.07 is 0.21000000000000002 in binary floating point, and
             that lands in the DOM as the delay verbatim. */
          e.target.style.transitionDelay =
            (Math.min(i, STAGGER_MAX) * STAGGER).toFixed(3) + 's';
        }
        e.target.setAttribute('data-in','true');
        io.unobserve(e.target);
      });
    },{rootMargin:'0px 0px -8% 0px',threshold:.12});
    revealTargets.forEach(function(t){io.observe(t);});
  }

  /* Each margin is its own marker. No second list to keep in sync.
     Every margin, not every numbered section: the hero carries a margin without
     being a numbered section, so keying this to [data-node] left it as the one
     label on the page with no bead beside it. Its sec is null and it simply never
     lights. */
  var fill = document.getElementById('spinefill');
  var marks = [].slice.call(document.querySelectorAll('.margin')).map(function(note){
    return { note: note, sec: note.closest('[data-node]') };
  });

  function absTop(el){ return el.getBoundingClientRect().top + window.scrollY; }

  var railEl = document.querySelector('.spine');

  /* The pulse, built before the beads so the beads paint over it as it passes.
     Restarted by taking the attribute off and forcing a reflow, or a second hover
     inside the first would do nothing. */
  if(railEl && !reduce){
    var clip = document.createElement('i');
    clip.className = 'pulseclip';
    clip.setAttribute('aria-hidden', 'true');
    var pulse = document.createElement('i');
    pulse.className = 'pulse';
    clip.appendChild(pulse);
    railEl.appendChild(clip);
    var lockup = document.querySelector('.top .name');
    if(lockup){
      lockup.addEventListener('mouseenter', function(){
        railEl.removeAttribute('data-pulse');
        void railEl.offsetWidth;
        railEl.setAttribute('data-pulse', 'true');
      });
    }
  }

  /* One bead per section, living on the rail. See the .spine .bead note in the
     stylesheet for why they are not pseudo-elements of the margins. */
  var beads = marks.map(function(){
    if(!railEl) return null;
    var b = document.createElement('i');
    b.className = 'bead';
    b.setAttribute('aria-hidden', 'true');
    railEl.appendChild(b);
    return b;
  });
  /* Document coordinate of the rule's head: the masthead does not travel now, so
     the mark scrolls away and the rule has to pin to the top of the viewport
     once it does. Set here, resolved against scroll position in onScroll. */
  var railHead = 0;

  /* The bar comes back on the way up, once the hero is behind you. It docks only
     while off-screen, and undocks only at the very top, where the docked and
     in-flow positions coincide, so neither switch is ever visible. */
  var topBarEl = document.getElementById('top');
  var stickyEl = document.querySelector('.stickycta');
  var heroEnd = 0, lastY = window.scrollY, upBy = 0, downBy = 0,
      docked = false, shown = false;
  var TRIGGER = 24;   /* travel in one direction before the bar responds */

  function placeRail(){
    /* The rule starts at the logomark's lower edge, so the mark caps it. In
       document coordinates, because the bar scrolls away with the page. */
    var bar = topBarEl;
    if(bar){
      var glyph = bar.querySelector('.name .mark');
      railHead = glyph
        ? glyph.getBoundingClientRect().bottom + window.scrollY
        : bar.offsetHeight;
      /* Measured undocked, which is the height main has to give back. Docking
         while this runs would read the fixed height instead. */
      if(!docked) document.documentElement.style
                    .setProperty('--bar-h', bar.offsetHeight + 'px');
    }
    var heroEl = document.querySelector('.open');
    heroEnd = heroEl
      ? heroEl.getBoundingClientRect().bottom + window.scrollY
      : 600;
    if(!railEl || getComputedStyle(railEl).display === 'none') return;
    var col = document.querySelector('.band .margin');
    if(!col) return;
    var gap = parseFloat(getComputedStyle(document.documentElement)
                .getPropertyValue('--margin-gap')) || 64;
    /* Snapped to a whole pixel. A 1px rule sitting on x.5 is drawn across two
       device pixels, and the dot beside it rounds separately, so the two look a
       pixel apart however exactly the maths agrees. */
    var edge = col.getBoundingClientRect().right;
    var x = Math.round(edge + gap / 2);
    railEl.style.left = x + 'px';

  }

  function measure(){
    placeRail();
    marks.forEach(function(m){
      if(!m.sec) return;
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
      if(topBarEl){
        var y = window.scrollY, dy = y - lastY;
        if(dy < 0){ upBy -= dy; downBy = 0; }
        else if(dy > 0){ downBy += dy; upBy = 0; }
        lastY = y;

        if(!docked && y > heroEnd){ docked = true; shown = false; }
        else if(docked && y <= 2){ docked = false; shown = false; }

        if(docked){
          if(upBy > TRIGGER) shown = true;
          else if(downBy > TRIGGER) shown = false;
          /* An open menu is not something to whisk away underneath a thumb. */
          if(topBarEl.getAttribute('data-open') === 'true') shown = true;
        }
        topBarEl.setAttribute('data-dock', docked ? 'true' : 'false');
        topBarEl.setAttribute('data-reveal', shown ? 'true' : 'false');
      }

      /* The sticky call to action, phone widths only (the stylesheet gates it).
         On a wide screen the travelling button or the rail keeps the way forward
         in reach; on a phone neither exists, so between the hero and the closing
         section there was no path forward at all except the menu. Appears once the
         hero is behind you -- the same threshold the docking bar uses -- and stands
         down when the closing section arrives carrying the real button, so the two
         are never on screen together saying the same thing. */
      if(stickyEl){
        var closeEl = document.querySelector('.close');
        var closeUp = closeEl &&
          closeEl.getBoundingClientRect().top < window.innerHeight;
        var stickOn = window.scrollY > heroEnd && !closeUp;
        stickyEl.setAttribute('data-on', stickOn ? 'true' : 'false');
        stickyEl.setAttribute('aria-hidden', stickOn ? 'false' : 'true');
        stickyEl.tabIndex = stickOn ? 0 : -1;
      }

      /* The head of the rule rides down with the mark, then holds at the top. But
         once the bar has docked and dropped back in, the mark is at the top of the
         viewport again, so the rule has to start under it there too. Set after the
         dock state above, because it depends on it: while the bar is translucent
         the line would otherwise run straight up through the logo. */
      var head = Math.max(0, railHead - window.scrollY);
      if(docked && shown){
        var onBar = topBarEl.querySelector('.name .mark');
        if(onBar) head = onBar.getBoundingClientRect().bottom;
      }
      document.documentElement.style.setProperty('--spine-top', Math.round(head) + 'px');

      var mid=window.scrollY+window.innerHeight/2;
      var railTop=railEl ? parseFloat(getComputedStyle(railEl).top) || 0 : 0;
      /* Where the fill has actually got to, in the same viewport coordinates the
         beads are placed in: the fill is the rail's full length scaled from its
         top, so its tip is that length times the scroll fraction. */
      var fillTip=railTop + p * Math.max(0, window.innerHeight - railTop);
      marks.forEach(function(m,i){
        var on = !!m.sec && mid>=m.a && mid<m.b;
        m.note.setAttribute('data-on', on ? 'true':'false');
        var bead=beads[i];
        if(bead){
          /* Taken from the label, so the bead sits on the row the label, the bead
             and the heading already share, whatever the type scale does. */
          var lbl=m.note.querySelector('b');
          if(lbl){
            var r=lbl.getBoundingClientRect();
            var y=r.top + r.height/2;
            bead.style.top=(y - railTop)+'px';
            /* Lit when the line reaches it, which is a different statement from
               the label's: the label says this is the section you are reading, the
               bead says the rule has got this far. Kept on its own attribute so
               the two can disagree, because they mean different things. */
            bead.setAttribute('data-lit', y <= fillTip ? 'true':'false');
          }
        }
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

  /* Measured again once the webfonts have actually arrived. --bar-h and the rail's
     head both come from the bar's own height, which is a line box, so it depends on
     font metrics: measured against the fallback and never corrected, the rule starts
     a couple of pixels off the logomark and main gives back the wrong amount of
     room. Nothing moves when the fonts were already cached, which is the common
     case, so this costs one measurement. */
  if(document.fonts && document.fonts.ready){
    document.fonts.ready.then(function(){ measure(); onScroll(); });
  }
  /* The rail is display:none below its breakpoint and cannot be placed while it is
     hidden. Widening a window fires resize and so recovers on its own; this makes
     the recovery explicit rather than a side effect of that, and covers the case
     where the breakpoint is crossed without a resize the listener above sees. */
  var railMQ = matchMedia('(min-width:1180px)');
  if(railMQ.addEventListener){
    railMQ.addEventListener('change',function(){ measure(); onScroll(); });
  }

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

  /* ── The intake ──
     A real form in the markup, one long column of questions, which this turns into
     one question per screen. Built that way round on purpose: with scripting off it
     is still a complete form that works, so there is no second copy of any question
     anywhere and nothing to keep in sync.
     There is no server. The old version of this faked a send with a 700ms timer and
     then said "That's in. Talk soon.", which is worse than having no form: it told
     the reader their words had arrived when they had been dropped on the floor. What
     happens now is the answers are composed into a brief the reader can read, copy,
     and hand over themselves, and the page says plainly that nothing has moved until
     they do. Which is also the better version of the idea: the answers are worth more
     to them than to me, so they get them either way. */
  /* ── The takeover ──
     The intake fills the viewport rather than sitting in a card. That is the whole
     difference between it reading as a conversation and reading as a contact form
     that will not end: the same eleven questions inside a page, under a masthead and
     over a footer, are surrounded by things saying "there is more of this below".
     An overlay rather than a page of its own, so nothing is navigated away from and
     the reader lands back exactly where they were. It is a real dialog: the page
     behind it cannot be scrolled or tabbed into, Escape closes it, and focus returns
     to the button that opened it. */
  /* The overlay carries the id 'intake', not the form inside it, so that the button's
     href="#intake" is a real anchor: with scripting off it scrolls to the questions
     instead of pointing at nothing. */
  var over=document.getElementById('intake');
  /* Everything that points at the intake opens it: the card button on start.html,
     the closing button on every page, and the travelling button once it has become
     that closing button. Collected by href rather than by id, so a new link to
     #intake anywhere is an opener without anyone remembering this list exists. */
  var openers=[].slice.call(document.querySelectorAll('a[href="#intake"]'));
  var opener=openers[0]||null;
  if(over){
    /* Promoted here rather than in the markup, so that a reader without scripting gets
       the questions as an ordinary form at the foot of the page and the button above
       simply scrolls to them. data-modal is what the stylesheet keys the fixed
       positioning to, so until this line runs the overlay is a section. */
    over.setAttribute('data-modal','true');
    over.setAttribute('role','dialog');
    over.setAttribute('aria-modal','true');
    over.hidden=true;

    var lastFocus=null, scrollAt=0;
    var FOCUSABLE='a[href],button:not([disabled]),textarea,input,select,[tabindex]:not([tabindex="-1"])';
    /* Prefixing a comma-separated selector list scopes only its first term: the rest
       stay unscoped and match the whole subtree. It looked right and put focus on the
       Close button, because that is the first button in the overlay rather than the
       first thing in the step. Each term has to be prefixed on its own. */
    function within(scope, sel){
      return sel.split(',').map(function(part){ return scope+' '+part.trim(); }).join(',');
    }

    function openOver(from){
      if(!over.hidden) return;
      /* The element to hand focus back to. Passed by the click handlers, because a
         programmatic click does not focus the anchor first, so activeElement was
         still body and the close fell back to the first opener on the page --
         which is the closing button at the very bottom. */
      lastFocus=from||document.activeElement;
      scrollAt=window.scrollY;
      over.hidden=false;
      /* position:fixed on the body rather than overflow:hidden. Hiding overflow
         alone does not stop iOS scrolling the page behind a fixed overlay, and it
         loses the scroll position on the way back; this holds the page still and
         puts it back on exactly the pixel it was on. */
      document.body.style.position='fixed';
      document.body.style.top=(-scrollAt)+'px';
      document.body.style.left='0';
      document.body.style.right='0';
      document.documentElement.setAttribute('data-over','true');
      var first=over.querySelector(within('.intake__steps .qstep:not([hidden])', FOCUSABLE))
             || over.querySelector('button[type="submit"]');
      if(first) first.focus();
    }
    function closeOver(){
      if(over.hidden) return;
      over.hidden=true;
      document.body.style.position='';
      document.body.style.top='';
      document.body.style.left='';
      document.body.style.right='';
      document.documentElement.removeAttribute('data-over');
      if(location.hash==='#intake'){
        history.replaceState(null,'',location.pathname+location.search);
      }
      /* Back to the button that opened it. lastFocus is whatever had focus at the
         time, which is the opener when a person clicked it, but body when the overlay
         was opened from the hash -- and focusing body puts the reader at the top of
         the document with no idea where they are. */
      var back = (lastFocus && lastFocus.focus && lastFocus!==document.body)
               ? lastFocus : opener;
      /* preventScroll, and focus before the scroll restore: a bare focus() scrolls
         its target into view, and when the target is the closing button at the foot
         of the page that threw the reader to the bottom the instant they closed --
         the restore ran first and the focus undid it. */
      if(back && back.focus){ try{ back.focus({preventScroll:true}); }catch(e){ back.focus(); } }
      window.scrollTo(0, scrollAt);
      lastFocus=null;
    }

    openers.forEach(function(a){
      a.addEventListener('click',function(e){ e.preventDefault(); openOver(a); });
    });
    var exit=document.getElementById('takeover-exit');
    if(exit) exit.addEventListener('click',closeOver);

    document.addEventListener('keydown',function(e){
      if(over.hidden) return;
      if(e.key==='Escape'){ e.preventDefault(); closeOver(); return; }
      if(e.key!=='Tab') return;
      /* The trap. Without it Tab walks out of the overlay and into a page the reader
         cannot see, which is the specific way a modal betrays a keyboard user. */
      var f=[].slice.call(over.querySelectorAll(FOCUSABLE)).filter(function(el){
        return el.offsetParent!==null || el===document.activeElement;
      });
      if(!f.length) return;
      var first=f[0], last=f[f.length-1];
      if(e.shiftKey && document.activeElement===first){ e.preventDefault(); last.focus(); }
      else if(!e.shiftKey && document.activeElement===last){ e.preventDefault(); first.focus(); }
    });

    /* Linkable, so the hero's button on any page can point straight at it with
       start.html#intake and skip the explaining. */
    if(location.hash==='#intake') openOver();
    addEventListener('hashchange',function(){
      if(location.hash==='#intake') openOver();
    });
  }

  var form=document.getElementById('intake-form');
  if(form){
    var status=document.getElementById('form-status');
    var submit=form.querySelector('button[type="submit"]');
    var submitLabel=submit.querySelector('span')||submit;
    var inputs=[].slice.call(form.querySelectorAll('input,textarea'));
    var steps=[].slice.call(form.querySelectorAll('.qstep'));
    var bar=form.querySelector('.intake__bar');
    var back=form.querySelector('.intake__back');
    var count=form.querySelector('.intake__count');
    var KEY='ofo.intake';
    var at=0;

    /* ── The replies ──
       A person asking these questions out loud reacts between them, and the
       reaction depends on what just happened: an answer, a skip, a choice. Those
       three are knowable here without pretending to understand the words, so every
       line below is honest -- it responds to what the reader did, and the reading
       of what they wrote happens where the last step says it does.
       Set in the site's handwriting face, because that face is reserved for words
       a person says rather than interface copy, and these are exactly that.
       One reply per moment that deserves one, not one per step: acknowledging
       everything is how it would turn into theatre. */
    var reply=document.createElement('p');
    reply.className='qstep__reply';
    reply.setAttribute('aria-live','polite');
    var pendingReply=null, skippedOnce=false;

    function replyFor(step){
      var field=step.querySelector('textarea');
      var val=field?field.value.trim():'';
      if(step.id==='q-idea-step' && val)
        return 'Good. A sentence is enough to start.';
      if(field && !field.required && !val && !skippedOnce){
        skippedOnce=true;
        return 'Skipped is fine. We can do that one out loud.';
      }
      if(step.id==='q-true-step' && val)
        return 'Noted. That is the one that gets tested first.';
      if(step.id==='q-no-step' && val)
        return 'Thank you for being straight about that.';
      if(step.id==='q-want-step'){
        var picked=step.querySelector('input[type=radio]:checked');
        if(!picked) return null;
        return {
          'yes-no':'Then a straight yes or no is what you will get.',
          'built':'Then we make sure something real gets in front of people.',
          'rule':'Then the rule comes first, before anything is built.',
          'unsure':'Fair. It tends to get clear once the idea is written down.'
        }[picked.value]||null;
      }
      return null;
    }

    function placeReply(){
      var frame=steps[at].querySelector('.qstep__frame');
      if(pendingReply){
        reply.textContent=pendingReply;
        steps[at].insertBefore(reply, steps[at].firstChild);
        /* The reply is the spoken moment on this step, so the printed frame stands
           down rather than stacking two voices at the top of one screen. */
        if(frame) frame.hidden=true;
      } else {
        if(reply.parentNode) reply.parentNode.removeChild(reply);
        if(frame) frame.hidden=false;
      }
      pendingReply=null;
    }

    function wrap(el){return el.closest('.field')||el.closest('.qstep');}
    function check(el){
      var w=wrap(el); if(!w) return true;
      var ok=el.checkValidity();
      w.setAttribute('data-invalid', ok?'false':'true');
      el.setAttribute('aria-invalid', ok?'false':'true');
      return ok;
    }
    /* Validated on blur and never on keystroke: telling someone their email is
       invalid while they are still on the fourth character is not help. */
    inputs.forEach(function(el){
      el.addEventListener('blur',function(){check(el);});
      el.addEventListener('input',function(){
        var w=wrap(el);
        if(w && w.getAttribute('data-invalid')==='true') check(el);
        save();
      });
      el.addEventListener('change',save);
    });

    /* Kept in this browser, not sent anywhere. Eleven questions is more than anyone
       finishes in one sitting if the phone rings, and losing them to a closed tab
       would be the whole point of the thing thrown away. */
    function save(){
      try{
        var d={};
        inputs.forEach(function(el){
          if(el.type==='radio'){ if(el.checked) d[el.name]=el.value; }
          else if(el.value) d[el.name]=el.value;
        });
        d.__at=at;
        localStorage.setItem(KEY, JSON.stringify(d));
      }catch(e){}
    }
    function restore(){
      try{
        var d=JSON.parse(localStorage.getItem(KEY)||'{}');
        inputs.forEach(function(el){
          if(!(el.name in d)) return;
          if(el.type==='radio'){ el.checked = (el.value===d[el.name]); }
          else el.value=d[el.name];
        });
        return typeof d.__at==='number' ? d.__at : 0;
      }catch(e){ return 0; }
    }

    /* The welcome is a step so that Back out of question one has somewhere to go and
       so the un-paginated form reads as a paragraph above the questions. It is not a
       question though, so it does not count: "1 of 12" on a page that promises eleven
       is a small lie, and the reader is counting. */
    var counted = steps.filter(function(s){ return s.getAttribute('data-count')!=='skip'; });
    var prog = document.getElementById('intakeprog');

    function paint(){
      steps.forEach(function(s,i){ s.hidden = (i!==at); });
      var last = at===steps.length-1;
      var here = counted.indexOf(steps[at]);
      submitLabel.textContent = last ? 'Send it over'
                             : here<0 ? 'Begin' : 'Next';
      submit.setAttribute('data-role', last ? 'send' : 'next');
      back.hidden = at===0;
      count.textContent = here<0 ? '' : (here+1) + ' of ' + counted.length;
      bar.hidden = false;
      form.setAttribute('data-step', String(at+1));
      if(prog){
        var done = here<0 ? 0 : (here+1)/counted.length;
        prog.style.transform = 'scaleX(' + done.toFixed(4) + ')';
      }
      /* The hint is only true where there is a textarea for it to be true of: on the
         choice and contact steps plain interaction advances, and a hint about a
         chord that does nothing there is worse than none. */
      var kbd=form.querySelector('.intake__kbd');
      if(kbd) kbd.hidden = !steps[at].querySelector('textarea');
      placeReply();
    }
    function go(to){
      at = Math.max(0, Math.min(steps.length-1, to));
      paint(); save();
      var f = steps[at].querySelector('textarea,input:not([type=radio]),input');
      if(f) f.focus({preventScroll:true});
      /* The card, not the field: scrolling a focused field to centre on a short
         step jumps the page for no reason. */
      var card=form.closest('.form-card')||form;
      var r=card.getBoundingClientRect();
      if(r.top<0||r.top>window.innerHeight*0.5){
        window.scrollTo({top:r.top+window.scrollY-100,
                         behavior:reduce?'auto':'smooth'});
      }
    }
    /* Only what the current step requires can block leaving it. Every question but
       the idea and the address is optional, so an empty field is an answer. */
    function stepOk(){
      var bad=null;
      [].slice.call(steps[at].querySelectorAll('input,textarea')).forEach(function(el){
        if(!check(el) && !bad) bad=el;
      });
      if(bad){ bad.focus(); return false; }
      return true;
    }

    back.addEventListener('click',function(){ go(at-1); });

    /* Ctrl or Cmd with Enter, which is the convention for committing a textarea, and
       plain Enter in the single-line fields where it means the same thing. */
    form.addEventListener('keydown',function(e){
      if(e.key!=='Enter') return;
      var t=e.target;
      if(t.tagName==='TEXTAREA'){
        if(e.ctrlKey||e.metaKey){ e.preventDefault(); if(stepOk()) advance(); }
      } else if(t.tagName==='INPUT' && t.type!=='radio'){
        e.preventDefault(); if(stepOk()) advance();
      }
    });

    function advance(){
      if(at<steps.length-1){ pendingReply=replyFor(steps[at]); go(at+1); return; }
      finish();
    }

    /* The brief. Plain text on purpose: it has to survive being pasted into a mail
       client, a doc, or a notes app without carrying markup into any of them. */
    function compose(){
      var lines=['Idea intake — one flow first',''];
      steps.forEach(function(s){
        var legend=s.querySelector('legend');
        if(legend){
          var picked=s.querySelector('input[type=radio]:checked');
          if(picked){
            lines.push(legend.textContent.replace(/Optional$/,'').trim());
            lines.push(picked.parentElement.textContent.trim(), '');
          }
          return;
        }
        /* Every field on the step, not the first one. The contact step carries two,
           and taking only the first quietly composed a brief with a name and no
           address on it -- the one field the whole thing exists to collect. */
        [].slice.call(s.querySelectorAll('textarea,input:not([type=radio])'))
          .forEach(function(field){
            if(!field.value.trim()) return;
            var lbl=s.querySelector('label[for="'+field.id+'"]')||s.querySelector('label');
            var q=lbl?lbl.textContent.replace(/\*/g,'').replace(/Optional$/,'').trim()
                    :field.name;
            lines.push(q, field.value.trim(), '');
          });
      });
      return lines.join('\n');
    }

    function finish(){
      var bad=null;
      inputs.forEach(function(el){ if(!check(el) && !bad) bad=el; });
      if(bad){
        /* A required field can only be on a step other than this one if the reader
           got here before filling it, so go to it rather than reporting it. */
        var owner=bad.closest('.qstep');
        var i=steps.indexOf(owner);
        if(i>=0 && i!==at){ go(i); }
        bad.focus();
        return;
      }
      var brief=compose();
      var box=document.getElementById('brief');
      if(box) box.value=brief;
      /* By name, because they just told it to a person. First name only: the full
         name back verbatim is what a mail merge does. */
      var first=(document.getElementById('name').value.trim().split(/\s+/)[0]||'');
      var h3=status&&status.querySelector('h3');
      if(h3 && first) h3.textContent='Here it is, '+first+'. It\u2019s yours either way.';

      var mail=document.getElementById('brief-mail');
      if(mail){
        mail.addEventListener('click',function(){
          var to='hello@oneflowfirst.com';
          var subj='Idea intake — '+(document.getElementById('name').value||'').trim();
          /* Long bodies are truncated by some mail clients at around 2000
             characters, so the address is opened with the brief and the copy button
             stays on screen as the way that never loses a word. */
          location.href='mailto:'+to+'?subject='+encodeURIComponent(subj)+
                        '&body='+encodeURIComponent(brief);
        });
      }
      var copy=document.getElementById('brief-copy');
      if(copy){
        copy.addEventListener('click',function(){
          var done=function(){
            var t=copy.textContent; copy.textContent='Copied';
            window.setTimeout(function(){copy.textContent=t;},1400);
          };
          if(navigator.clipboard && navigator.clipboard.writeText){
            navigator.clipboard.writeText(brief).then(done,function(){box.select();});
          } else { box.select(); document.execCommand('copy'); done(); }
        });
      }
      form.hidden=true;
      if(status){ status.setAttribute('data-visible','true'); status.focus(); }
      try{ localStorage.removeItem(KEY); }catch(e){}
    }

    form.addEventListener('submit',function(e){
      e.preventDefault();
      if(!stepOk()) return;
      advance();
    });

    at=restore();
    if(at>steps.length-1) at=0;
    /* Answers already in this browser mean the reader has been here: greet them as
       a person would, and say the true thing -- nothing was lost. */
    if(at>0) pendingReply='Welcome back. Everything is where you left it.';
    paint();
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
