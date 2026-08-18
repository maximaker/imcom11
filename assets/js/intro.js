/* First load, once ever: the mark assembles itself, takes its place, and hands
   the page over.
   One idea appears. Others gather around it, settle onto a circle, and harden
   into the ring. The ring keeps its gap, one dot stays lit in the middle, and the
   whole thing walks to the masthead at the size it will live at. Then the page
   arrives behind it, a piece at a time.
   Whether this runs at all was decided in the head, before paint. */
(function () {
  var root = document.documentElement;
  var stage = document.getElementById('intro');
  if (root.getAttribute('data-intro') !== 'running' || !stage) return;

  /* Released without ceremony if GSAP never arrived: the page is hidden right
     now, so there is no version of this worth failing at. */
  function release() {
    root.removeAttribute('data-intro');
    stage.remove();
    document.dispatchEvent(new Event('intro:ready'));
    dispatchEvent(new Event('resize'));
  }
  if (!window.gsap) { release(); return; }
  window.__introStarted = true;

  var svg = document.getElementById('intro-mark');
  var swarm = document.getElementById('intro-swarm');
  var ring = document.getElementById('intro-ring');
  var lead = document.getElementById('intro-lead');
  var core = document.getElementById('intro-core');

  /* Read from the tokens rather than restated, so the animation cannot drift
     from the mark it is drawing. */
  var css = getComputedStyle(root);
  var SAND = css.getPropertyValue('--sand-500').trim() || '#C9AE99';
  var INK = css.getPropertyValue('--ink-3').trim() || '#6E5B4C';
  var CLAY = css.getPropertyValue('--clay-mark').trim() || '#CC5500';

  /* The mark's own geometry: centre 16,16, radius 11, and a gap on the right 34
     degrees either side of centre. The dots seat on the solid arc only, so the
     ring they harden into is the ring the brand actually uses, gap included. */
  var CX = 16, CY = 16, R = 11, GAP = 34, N = 14;
  var SOLID = 360 - 2 * GAP;
  var NS = 'http://www.w3.org/2000/svg';

  /* Deterministic, so the swarm is identical on every first load. */
  function rnd(i, salt) {
    var x = Math.sin((i + 1) * 12.9898 + salt * 78.233) * 43758.5453;
    return x - Math.floor(x);
  }

  var dots = [], els = [];
  for (var i = 0; i < N; i++) {
    var seat = (GAP + (SOLID * (i + 0.5)) / N) * Math.PI / 180;
    var away = (rnd(i, 1) * 360) * Math.PI / 180;
    var far = 21 + rnd(i, 2) * 15;
    var el = document.createElementNS(NS, 'circle');
    el.setAttribute('r', 1.15);
    el.setAttribute('cx', CX);
    el.setAttribute('cy', CY);
    swarm.appendChild(el);
    els.push(el);
    dots.push({
      from: { x: Math.cos(away) * far, y: Math.sin(away) * far },
      to: { x: Math.cos(seat) * R, y: Math.sin(seat) * R }
    });
  }

  /* Both strokes are drawn by hand: DrawSVG is a Club plugin, and dashoffset on
     a measured length does the same job with nothing added. */
  var ringLen = ring.getTotalLength(), leadLen = lead.getTotalLength();
  gsap.set(ring, { strokeDasharray: ringLen, strokeDashoffset: ringLen });
  gsap.set(lead, { strokeDasharray: leadLen, strokeDashoffset: leadLen });
  /* The core keeps its final radius and is scaled instead. Animating the r
     attribute re-rasterises the SVG every frame; a transform does not, and the
     dot is small enough that the two look identical. */
  var SEED = 1.5 / 3.7;
  gsap.set(core, { attr: { r: 3.7 }, fill: INK, scale: 0, transformOrigin: '16px 16px' });
  gsap.set(els, { fill: SAND, opacity: 0, scale: 0.6, transformOrigin: 'center' });
  els.forEach(function (el, n) { gsap.set(el, { x: dots[n].from.x, y: dots[n].from.y }); });

  /* Where the mark has to end up. Measured now, while the layout is settled: the
     masthead copy is hidden but still laid out, so its box is the real one. Held
     as plain numbers rather than measured mid-flight, so skipping ahead cannot
     land the mark somewhere else. */
  function landing() {
    var target = document.querySelector('.top .name .mark');
    if (!target) return null;
    var t = target.getBoundingClientRect(), s = svg.getBoundingClientRect();
    if (!t.width || !s.width) return null;
    return {
      scale: t.width / s.width,
      x: (t.left + t.width / 2) - (s.left + s.width / 2),
      y: (t.top + t.height / 2) - (s.top + s.height / 2)
    };
  }
  var end = landing();
  if (!end) { release(); return; }

  /* The page comes in behind the mark, in reading order. Held at opacity 0 by
     inline styles before the CSS gate lifts, or every piece would appear at once
     in the frame the attribute comes off. */
  function bringPageIn() {
    var pieces = [];
    ['.top .name span', '.top nav a', '.open .margin', '.open .deck',
      '.principle', '.hero-cta', '.act-note', '.stats', '.spine']
      .forEach(function (sel) {
        [].push.apply(pieces, document.querySelectorAll(sel));
      });
    if (!pieces.length) { release(); return; }

    gsap.set(pieces, { opacity: 0, y: 12 });
    /* Most of these carry .rev, which is opacity:0 until the scroll observer
       marks it. Their inline opacity wins while the tween runs, but clearProps at
       the end would hand them back to that rule and they would vanish, the button
       among them. So they are marked seen up front: the animation is their
       entrance, and the observer has nothing left to do for them. */
    pieces.forEach(function (el) {
      if (el.classList.contains('rev')) el.setAttribute('data-in', 'true');
    });
    /* Lifting the gate reveals the real mark and hides the stage in the same
       frame. They are the same size in the same place by now, so it reads as one
       object rather than a swap. */
    root.removeAttribute('data-intro');
    document.dispatchEvent(new Event('intro:ready'));   /* the headline rises */

    gsap.to(pieces, {
      opacity: 1, y: 0, duration: 0.65, ease: 'power2.out', stagger: 0.075,
      onComplete: function () {
        gsap.set(pieces, { clearProps: 'opacity,transform' });
        stage.remove();
        /* The rail measures itself against a layout that was hidden until now. */
        dispatchEvent(new Event('resize'));
      }
    });
  }

  var tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

  /* Unhurried on purpose: every phase overlaps the next, so nothing starts from a
     standstill, and the eases are gentle rather than snappy. Absolute start times
     rather than relative ones, so the overlaps stay where they are put. */

  /* One idea. */
  tl.to(core, { scale: SEED, duration: 0.65, ease: 'back.out(1.5)' }, 0)

    /* Then the others, from everywhere, in no particular order. */
    .to(els, { opacity: 1, scale: 1, duration: 0.55,
      stagger: { each: 0.04, from: 'random' } }, 0.40)

    /* They come around it. The group turns as they close in, so it reads as
       gathering rather than snapping onto marks. */
    .fromTo(swarm, { rotation: -30 },
      { rotation: 0, duration: 1.15, ease: 'power2.inOut',
        transformOrigin: '16px 16px' }, 0.95)
    .to(els, {
      x: function (n) { return dots[n].to.x; },
      y: function (n) { return dots[n].to.y; },
      duration: 1.15, ease: 'power2.inOut',
      stagger: { each: 0.03, from: 'random' }
    }, 0.95)

    /* The circle hardens: the stroke draws steadily through them as they give
       way, so there is no frame where the ring is neither dots nor line. */
    .to(ring, { strokeDashoffset: 0, duration: 0.95, ease: 'power1.inOut' }, 2.15)
    .to(els, { opacity: 0, scale: 0.4, duration: 0.45,
      stagger: { each: 0.025 } }, 2.40)

    /* One dot remains, lit, and the line runs out through the gap. */
    .to(core, { scale: 1, fill: CLAY, duration: 0.55, ease: 'back.out(1.4)' }, 2.95)
    .to(lead, { strokeDashoffset: 0, duration: 0.45 }, 3.10)

    /* A beat with the finished mark, before it goes anywhere. */

    /* Then its place on the page, at the size it lives at. The ground goes first,
       so the mark is already travelling across the real page. */
    .to(stage, { backgroundColor: 'rgba(0,0,0,0)', duration: 0.50 }, 3.90)
    .to(svg, { scale: end.scale, x: end.x, y: end.y,
      duration: 1.05, ease: 'power2.inOut' }, 3.90)

    /* Only once it has landed. */
    .add(bringPageIn, 4.95);

  /* A first-time visitor who starts scrolling or tapping has told you enough.
     Sped up rather than cut, so the mark still lands where it belongs. */
  function hurry() { gsap.to(tl, { timeScale: 4, duration: 0.4, overwrite: true }); }
  ['pointerdown', 'keydown', 'wheel', 'touchstart'].forEach(function (ev) {
    addEventListener(ev, hurry, { once: true, passive: true });
  });
})();
