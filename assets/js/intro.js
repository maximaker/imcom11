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
  /* A dot is exactly as thick as the ring it becomes, so the two fuse instead of
     the stroke stepping up in weight as it draws through them. */
  var DOT_R = parseFloat(getComputedStyle(ring).strokeWidth) / 2 || 1.55;
  var NS = 'http://www.w3.org/2000/svg';

  /* Deterministic, so the swarm is identical on every first load. */
  function rnd(i, salt) {
    var x = Math.sin((i + 1) * 12.9898 + salt * 78.233) * 43758.5453;
    return x - Math.floor(x);
  }

  /* Each dot is held in polar coordinates and its position written out by hand.
     Rotating the group would be the obvious way to swing them in, but a <g> whose
     bounding box is the union of its moving children is exactly the case GSAP
     cannot get right: the origin compensation is computed against a box that no
     longer exists, and a translate is left in the matrix even at rotation 0. Both
     transformOrigin and svgOrigin did it, off by 19 units. Polar has no origin. */
  var dots = [], els = [];
  for (var i = 0; i < N; i++) {
    /* Seated across the solid arc end to end, not inset half a step at each end:
       the circle they form has to reach exactly as far as the stroke that
       replaces it, or the ring visibly grows past where the dots were. */
    var seat = GAP + (SOLID * i) / (N - 1);
    var el = document.createElementNS(NS, 'circle');
    el.setAttribute('r', DOT_R);
    el.setAttribute('cx', CX);
    el.setAttribute('cy', CY);
    swarm.appendChild(el);
    els.push(el);
    dots.push({
      seat: seat,
      ang: seat + 26 + rnd(i, 1) * 26,     /* swings in, each by its own amount */
      rad: 21 + rnd(i, 2) * 15
    });
  }

  function place() {
    for (var n = 0; n < dots.length; n++) {
      var a = dots[n].ang * Math.PI / 180;
      gsap.set(els[n], { x: Math.cos(a) * dots[n].rad, y: Math.sin(a) * dots[n].rad });
    }
  }

  /* Both strokes are drawn by hand: DrawSVG is a Club plugin, and a dash offset
     on a measured length does the same job with nothing added.
     The offsets are written straight to style rather than tweened as properties,
     because GSAP renders a dash offset as a whole number of px whatever
     autoRound is set to, and these lengths are fractional. The lead is 11.2 units
     long; hidden at 11 it left 0.2 units of stroke with a round cap on it painted
     from the very first frame, as a stray dot beside the first idea. Rounding also
     made the drawing itself step, a unit at a time. So a plain object is tweened
     from 1 to 0 and the offsets are painted from it. */
  var ringLen = ring.getTotalLength(), leadLen = lead.getTotalLength();
  var draw = { ring: 1, lead: 1 };            /* 1 hidden, 0 fully drawn */
  function paint() {
    ring.style.strokeDashoffset = (ringLen * draw.ring) + 'px';
    lead.style.strokeDashoffset = (leadLen * draw.lead) + 'px';
  }
  ring.style.strokeDasharray = ringLen + 'px';
  lead.style.strokeDasharray = leadLen + 'px';
  paint();
  /* The core keeps its final radius and is scaled instead. Animating the r
     attribute re-rasterises the SVG every frame; a transform does not, and the
     dot is small enough that the two look identical.
     The seed is the size of one of the others, because that is what it is: at
     this point it is an idea among ideas, and only later the one that was kept. */
  var SEED = DOT_R / 3.7;
  /* svgOrigin, not transformOrigin. On an SVG element transformOrigin is measured
     from the element's own bounding box, so '16px 16px' on a circle whose box
     starts at 12.3 puts the origin at 28.3 and scaling throws the dot down and to
     the right, 7 units off centre. svgOrigin is the user-space point it reads as. */
  gsap.set(core, { attr: { r: 3.7 }, fill: INK, scale: 0, svgOrigin: '16 16' });
  gsap.set(els, { fill: SAND, opacity: 0, scale: 0.6, transformOrigin: 'center' });
  place();

  /* Where the mark has to end up. The masthead copy is hidden but still laid out,
     so its box is the real one. Measured through a function rather than frozen
     into numbers, because the move does not begin until 4.3 seconds in: a window
     resized or a phone turned before then would otherwise land the mark where the
     masthead used to be. */
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
  if (!landing()) { release(); return; }   /* nothing to aim at, so do not try */

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

  /* The painter hangs off the timeline rather than off a tween of its own, so it
     runs after the children have written their values. A tween's onUpdate can fire
     before the tweens that move the data, which paints the previous frame's
     positions: harmless at 60fps, but it means the dots reach their seats a frame
     after the stroke starts drawing through them. Fourteen gsap.set calls a frame
     is not worth optimising away. */
  var tl = gsap.timeline({ defaults: { ease: 'power2.out' }, onUpdate: place });

  /* Unhurried on purpose: every phase overlaps the next, so nothing starts from a
     standstill, and the eases are gentle rather than snappy. Absolute start times
     rather than relative ones, so the overlaps stay where they are put. */

  /* One idea. */
  tl.to(core, { scale: SEED, duration: 0.65, ease: 'back.out(1.5)' }, 0)

    /* Then the others, from everywhere, in no particular order. */
    .to(els, { opacity: 1, scale: 1, duration: 0.55,
      stagger: { each: 0.04, from: 'random' } }, 0.40)

    /* They come around it: each dot closes on its seat and swings the last of the
       way round, because the angle arrives at the same time as the radius. */
    .to(dots, {
      ang: function (n) { return dots[n].seat; }, rad: R,
      duration: 1.15, ease: 'power2.inOut',
      stagger: { each: 0.03, from: 'random' }
    }, 0.95)


    /* The circle hardens, and only once it is a circle. The converge above runs
       0.95 to 2.49 once its stagger is counted, so starting the stroke any earlier
       draws ring where dots have not arrived yet. The dots then give way under it,
       finishing together with it, so there is no frame where the ring is neither
       dots nor line. */
    .to(draw, { ring: 0, duration: 0.95, ease: 'power1.inOut', onUpdate: paint }, 2.50)
    .to(els, { opacity: 0, scale: 0.4, duration: 0.45,
      stagger: { each: 0.025 } }, 2.65)

    /* One dot remains, lit, and the line runs out through the gap as it closes. */
    .to(core, { scale: 1, fill: CLAY, duration: 0.55, ease: 'back.out(1.4)' }, 3.30)
    .to(draw, { lead: 0, duration: 0.45, onUpdate: paint }, 3.45)

    /* A beat with the finished mark, before it goes anywhere. */

    /* Then its place on the page, at the size it lives at. The ground goes first,
       so the mark is already travelling across the real page. */
    .to(stage, { backgroundColor: 'rgba(0,0,0,0)', duration: 0.50 }, 4.30)
    /* Read when the tween begins, not when it was written. */
    .to(svg, { scale: function () { return landing().scale; },
      x: function () { return landing().x; },
      y: function () { return landing().y; },
      duration: 1.05, ease: 'power2.inOut' }, 4.30)

    /* Only once it has landed. */
    .add(bringPageIn, 5.35);

  /* And if the window changes size mid-flight, the same values are read again. */
  function retarget() { tl.getChildren(false, true, false).forEach(function (t) {
    if (t.targets && t.targets()[0] === svg) t.invalidate();
  }); }
  addEventListener('resize', retarget, { passive: true });
  tl.eventCallback('onComplete', function () {
    removeEventListener('resize', retarget);
  });

  /* A first-time visitor who starts scrolling or tapping has told you enough.
     Sped up rather than cut, so the mark still lands where it belongs. */
  function hurry() { gsap.to(tl, { timeScale: 4, duration: 0.4, overwrite: true }); }
  ['pointerdown', 'keydown', 'wheel', 'touchstart'].forEach(function (ev) {
    addEventListener(ev, hurry, { once: true, passive: true });
  });
})();
