/* one flow first — v2 choreography.
   Every effect here is an enhancement: the page reads complete without scripting,
   and under reduced motion it lands on each figure's final, meaningful frame. */
(function () {
  var root = document.documentElement;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var G = window.gsap, ST = window.ScrollTrigger;
  var motion = !reduce && G && ST;
  if (!motion) root.classList.add('no-motion');
  if (G && ST) G.registerPlugin(ST);

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function smooth(t) { t = clamp(t, 0, 1); return t * t * (3 - 2 * t); }

  /* ── Smooth scroll. Lenis carries the page; ScrollTrigger reads from it. ── */
  var lenis = null;
  if (motion && window.Lenis) {
    lenis = new Lenis({ lerp: 0.1, wheelMultiplier: 1 });
    lenis.on('scroll', ST.update);
    G.ticker.add(function (t) { lenis.raf(t * 1000); });
    G.ticker.lagSmoothing(0);
  }
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      var el = id.length > 1 && document.querySelector(id);
      if (!el) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(el, { offset: -20, duration: 1.4 });
      else el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
    });
  });

  /* ── Nav: docks once the page moves, steps aside while reading down, returns
        the moment the reader reverses. ── */
  var nav = document.querySelector('.nav');
  var fill = document.querySelector('.rail__fill'), dot = document.querySelector('.rail__dot');
  var lastY = 0;
  function onScroll() {
    var y = window.scrollY, max = document.documentElement.scrollHeight - innerHeight;
    nav.classList.toggle('is-docked', y > 40);
    nav.classList.toggle('is-hidden', y > 640 && y > lastY + 2);
    if (y < lastY - 2) nav.classList.remove('is-hidden');
    lastY = y;
    var p = max > 0 ? y / max : 0;
    fill.style.transform = 'scaleY(' + p + ')';
    dot.style.transform = 'translateY(' + (p * (innerHeight - 9)) + 'px)';
  }
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ── The dot field: the motif of the whole site, as a living surface ──
     Dots sit on a loose grid, lean away from the pointer on a spring, and can be
     asked to gather toward one point: the hero's field drains toward its clay dot
     as the reader leaves it, which is the sieve below, foreshadowed. */
  function Field(canvas, o) {
    var ctx = canvas.getContext('2d'), dpr = Math.min(devicePixelRatio || 1, 2);
    var dots = [], w = 0, h = 0, mx = -9999, my = -9999, running = false, visible = true, t0 = performance.now();
    var gather = 0;
    function build() {
      var r = canvas.getBoundingClientRect(); w = r.width; h = r.height;
      canvas.width = w * dpr; canvas.height = h * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      dots = [];
      var s = o.spacing(w);
      for (var y = s / 2; y < h; y += s) for (var x = s / 2; x < w; x += s) {
        var jx = (Math.sin(x * 12.9898 + y * 78.233) * 43758.5453) % 1, jy = (Math.sin(x * 39.34 + y * 11.13) * 24634.6345) % 1;
        var hx = x + jx * s * 0.35, hy = y + jy * s * 0.35;
        var a = o.alpha(hx / w, hy / h);
        if (a > 0.02) dots.push({ hx: hx, hy: hy, x: hx, y: hy, vx: 0, vy: 0, a: a, ph: Math.abs(jx) * 6.28 });
      }
      draw(performance.now());
    }
    function draw(now) {
      var t = (now - t0) / 1000;
      ctx.clearRect(0, 0, w, h);
      var ax = o.accent ? o.accent.x * w : 0, ay = o.accent ? o.accent.y * h : 0, R = o.radius;
      var settled = true;
      for (var i = 0; i < dots.length; i++) {
        var d = dots[i];
        var tx = lerp(d.hx, ax, gather * 0.92), ty = lerp(d.hy, ay, gather * 0.92);
        var dx = d.x - mx, dy = d.y - my, dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < R) {
          var f = (1 - dist / R); f = f * f * o.force;
          var nx = dx / (dist || 1), ny = dy / (dist || 1);
          if (o.mode === 'attract') { nx = -nx; ny = -ny; }
          tx += nx * f; ty += ny * f;
        }
        d.vx += (tx - d.x) * 0.07; d.vy += (ty - d.y) * 0.07;
        d.vx *= 0.8; d.vy *= 0.8;
        d.x += d.vx; d.y += d.vy;
        if (Math.abs(d.vx) + Math.abs(d.vy) > 0.02) settled = false;
        var breathe = reduce ? 1 : 1 + Math.sin(t * 1.2 + d.ph) * 0.12;
        ctx.globalAlpha = d.a * (1 - gather * 0.85);
        ctx.fillStyle = '#CCB58A';
        ctx.beginPath(); ctx.arc(d.x, d.y, o.size * breathe, 0, 6.283); ctx.fill();
      }
      if (o.accent) {
        var pulse = reduce ? 0 : (t % 2.8) / 2.8;
        ctx.globalAlpha = (1 - pulse) * 0.5;
        ctx.strokeStyle = '#B84B00'; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.arc(ax, ay, 8 + pulse * 22 + gather * 8, 0, 6.283); ctx.stroke();
        ctx.globalAlpha = 1; ctx.fillStyle = '#B84B00';
        ctx.beginPath(); ctx.arc(ax, ay, 6 + gather * 6, 0, 6.283); ctx.fill();
      }
      ctx.globalAlpha = 1;
      return settled;
    }
    function loop(now) {
      if (!visible) { running = false; return; }
      draw(now);
      requestAnimationFrame(loop);
    }
    function start() { if (!running && !reduce) { running = true; requestAnimationFrame(loop); } }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) start(); }).observe(canvas);
    }
    if (fine) {
      canvas.parentElement.addEventListener('pointermove', function (e) {
        var r = canvas.getBoundingClientRect(); mx = e.clientX - r.left; my = e.clientY - r.top;
      });
      canvas.parentElement.addEventListener('pointerleave', function () { mx = my = -9999; });
    }
    var rt; addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(build, 150); });
    build(); start();
    return { setGather: function (g) { gather = g; if (reduce) draw(performance.now()); } };
  }

  var heroCanvas = document.getElementById('field');
  var hero = heroCanvas && Field(heroCanvas, {
    spacing: function (w) { return w < 700 ? 30 : 36; },
    size: 2.1, radius: 140, force: 46, mode: 'repel',
    /* On a phone the open side is above the title, not beside the button. */
    accent: innerWidth < 700 ? { x: 0.86, y: 0.2 } : { x: 0.78, y: 0.4 },
    /* Faint behind the words, fuller toward the open right side. */
    alpha: function (x, y) { var a = smooth((x - 0.34) / 0.5) * 0.85; return innerWidth < 700 ? a * 0.45 : a; }
  });
  if (hero) {
    var heroEl = document.querySelector('.hero');
    addEventListener('scroll', function () {
      hero.setGather(smooth(window.scrollY / (heroEl.offsetHeight * 0.85)));
    }, { passive: true });
  }

  var closeCanvas = document.getElementById('closeField');
  if (closeCanvas) Field(closeCanvas, {
    spacing: function (w) { return w < 700 ? 34 : 42; },
    size: 1.9, radius: 220, force: 40, mode: 'attract', accent: null,
    /* A clearing around the words, so the field frames the ask rather than
       sitting under it. */
    alpha: function (x, y) { var dx = (x - 0.5) * 1.6, dy = (y - 0.5); var r = Math.sqrt(dx * dx + dy * dy); return smooth((r - 0.32) / 0.4) * 0.75; }
  });

  /* ── The sieve: forty possibilities, narrowed in stages to the one ── */
  (function () {
    var canvas = document.getElementById('sieveCanvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d'), dpr = Math.min(devicePixelRatio || 1, 2);
    var N = 40, nEl = document.getElementById('sieveN');
    var caps = [].slice.call(document.querySelectorAll('#sieveCaps p'));
    var marks = [].slice.call(document.querySelectorAll('#sieveMarks i'));
    function rnd(i, s) { var x = Math.sin((i + 1) * 12.9898 + s * 78.233) * 43758.5453; return x - Math.floor(x); }
    function pick(from, c) { var out = [], st = from.length / c; for (var i = 0; i < c; i++) out.push(from[Math.floor(i * st + st / 2)]); return out; }
    function grid(i, c, cols, dx, dy) { var rows = Math.ceil(c / cols); return { x: 500 + (i % cols - (cols - 1) / 2) * dx, y: 210 + (Math.floor(i / cols) - (rows - 1) / 2) * dy }; }
    var all = []; for (var i = 0; i < N; i++) all.push(i);
    var k12 = pick(all, 12), k4 = pick(k12, 4), k1 = k4[2];
    var dots = all.map(function (i) {
      var a = k12.indexOf(i), b = k4.indexOf(i);
      return { s: { x: 60 + rnd(i, 1) * 880, y: 20 + rnd(i, 2) * 380 }, p0: grid(i, N, 8, 52, 44),
        p1: a >= 0 ? grid(a, 12, 4, 74, 66) : null, p2: b >= 0 ? grid(b, 4, 2, 104, 86) : null, p3: i === k1,
        seed: rnd(i, 3), cull: rnd(i, 4), drift: rnd(i, 5) };
    });
    var W, H, sc, ox, oy;
    function size() {
      var r = canvas.getBoundingClientRect(); W = r.width; H = r.height;
      canvas.width = W * dpr; canvas.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      sc = Math.min(W / 1000, H / 420); ox = (W - 1000 * sc) / 2; oy = (H - 420 * sc) / 2;
    }
    function own(t, s, sp) { return clamp(t * (1 + sp) - s * sp, 0, 1); }
    function seg(p, a, b) { return smooth((p - a) / (b - a)); }
    function push(d, x, y, g) {
      var dx = x - 500, dy = y - 210, L = Math.sqrt(dx * dx + dy * dy) || 1, dist = g * (30 + d.drift * 50);
      return { x: x + dx / L * dist, y: y + dy / L * dist + g * 14 };
    }
    var lastStage = -1;
    function draw(p) {
      var tA = seg(p, 0, .14), tB = seg(p, .08, .3), tC = seg(p, .34, .52), tD = seg(p, .54, .7), tE = seg(p, .72, .88);
      ctx.clearRect(0, 0, W, H);
      var alive = 0, base = Math.max(3.4, 5 * sc);
      dots.forEach(function (d) {
        var g = own(tB, d.seed, .4);
        var x = lerp(d.s.x, d.p0.x, g), y = lerp(d.s.y, d.p0.y, g), a = 1, r = base, q;
        if (d.p1) { g = own(tC, d.seed, .25); x = lerp(x, d.p1.x, g); y = lerp(y, d.p1.y, g); }
        else if (tC > 0) { g = own(tC, d.cull, .6); a = 1 - g; q = push(d, x, y, g); x = q.x; y = q.y; }
        if (d.p2) { g = own(tD, d.seed, .25); x = lerp(x, d.p2.x, g); y = lerp(y, d.p2.y, g); }
        else if (d.p1 && tD > 0) { g = own(tD, d.cull, .6); a = 1 - g; q = push(d, x, y, g); x = q.x; y = q.y; }
        if (d.p3) {
          x = lerp(x, 500, tE); y = lerp(y, 210, tE);
          var R = Math.max(10, 15 * sc);
          r = lerp(base, R, smooth(tE / .8)) + R * .08 * Math.sin(Math.PI * clamp((tE - .55) / .45, 0, 1));
        } else if (d.p2 && tE > 0) { g = own(tE, d.cull, .6); a = 1 - g; q = push(d, x, y, g); x = q.x; y = q.y; }
        var entry = clamp(tA * 1.6 - d.seed * .4, 0, 1);
        if (a > .5) alive++;
        var X = ox + x * sc, Y = oy + y * sc;
        ctx.globalAlpha = a * (.2 + .8 * entry);
        ctx.fillStyle = d.p3 && tE > .5 ? '#B84B00' : '#C2A97A';
        ctx.beginPath(); ctx.arc(X, Y, r, 0, 6.283); ctx.fill();
        if (d.p3 && tE > .9) {
          var k = (tE - .9) / .1;
          ctx.globalAlpha = .35 * k; ctx.strokeStyle = '#B84B00'; ctx.lineWidth = 1;
          ctx.beginPath(); ctx.arc(X, Y, r + 14 * k, 0, 6.283); ctx.stroke();
          ctx.globalAlpha = .15 * k; ctx.beginPath(); ctx.arc(X, Y, r + 34 * k, 0, 6.283); ctx.stroke();
        }
      });
      ctx.globalAlpha = 1;
      /* The big number is the field counted, not a label: whatever is still
         standing is what it says. */
      nEl.textContent = alive;
      var stage = p < .5 ? 0 : p < .68 ? 1 : p < .86 ? 2 : 3;
      if (stage !== lastStage) {
        caps.forEach(function (c) { c.setAttribute('data-on', String(+c.dataset.i === stage)); });
        marks.forEach(function (m, i) { m.setAttribute('data-on', String(i <= stage)); });
        lastStage = stage;
      }
    }
    var state = { p: 0 };
    size(); draw(motion ? 0 : 1);
    addEventListener('resize', function () { size(); draw(state.p); });
    if (!motion) { state.p = 1; return; }
    G.to(state, { p: 1, ease: 'none', onUpdate: function () { draw(state.p); },
      scrollTrigger: { trigger: '.sieve', start: 'top top', end: 'bottom bottom', scrub: 0.9 } });
  })();

  /* ── The compare: before and after, under the reader's own hand ── */
  (function () {
    var box = document.getElementById('compare'), range = document.getElementById('compareRange');
    if (!box || !range) return;
    function set(v) { box.style.setProperty('--pos', v + '%'); }
    range.addEventListener('input', function () { set(range.value); });
    set(range.value);
    if (!motion) return;
    var o = { v: 88 };
    set(88); range.value = 88;
    /* A single sweep on arrival shows it is a handle, then hands it over. */
    G.to(o, { v: 46, duration: 1.8, ease: 'expo.inOut', delay: .3,
      onUpdate: function () { set(o.v); range.value = o.v; },
      scrollTrigger: { trigger: box, start: 'top 70%', once: true } });
  })();

  /* ── Doubts: tap or keyboard turns the thought into the answer ── */
  document.querySelectorAll('.doubt').forEach(function (b) {
    b.addEventListener('click', function () {
      var on = b.getAttribute('aria-expanded') === 'true';
      document.querySelectorAll('.doubt').forEach(function (x) { x.setAttribute('aria-expanded', 'false'); });
      b.setAttribute('aria-expanded', String(!on));
    });
  });

  if (!motion) { if (G === undefined) return; return; }

  /* ── Hero entrance ── */
  var tl = G.timeline({ defaults: { ease: 'expo.out' } });
  tl.to('.hero__title .line > span', { y: 0, duration: 1.3, stagger: .12 }, .15)
    .to('[data-hero]', { opacity: 1, y: 0, duration: 1.1, stagger: .08 }, .45);
  document.querySelectorAll('[data-count]').forEach(function (el) {
    var o = { n: 0 }, to = +el.dataset.count;
    tl.to(o, { n: to, duration: 1.6, ease: 'power3.out', onUpdate: function () { el.textContent = Math.round(o.n); } }, .9);
  });

  /* ── Generic reveals, batched so neighbours arrive as a phrase ── */
  ST.batch('[data-reveal]', { start: 'top 88%', once: true, onEnter: function (els) {
    els.forEach(function (e) { e.classList.add('is-in'); });
    G.to(els, { opacity: 1, y: 0, duration: 1, ease: 'power3.out', stagger: .09 });
  } });

  /* ── The bind: the sentence lights word by word as it is read ── */
  document.querySelectorAll('[data-words]').forEach(function (h) {
    (function split(node) {
      [].slice.call(node.childNodes).forEach(function (c) {
        if (c.nodeType === 3) {
          var frag = document.createDocumentFragment();
          c.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var s = document.createElement('span'); s.className = 'w'; s.textContent = part; frag.appendChild(s);
          });
          node.replaceChild(frag, c);
        } else if (c.nodeType === 1) split(c);
      });
    })(h);
    G.to(h.querySelectorAll('.w'), { opacity: 1, stagger: .1, ease: 'none',
      scrollTrigger: { trigger: h, start: 'top 82%', end: 'bottom 45%', scrub: .6 } });
  });

  /* ── Method: the three steps travel sideways, one rail of dots tracking them ── */
  var mm = G.matchMedia();
  mm.add('(min-width: 900px)', function () {
    var track = document.getElementById('methodTrack'), fillEl = document.getElementById('stepFill');
    var pips = [].slice.call(document.querySelectorAll('.steprail b'));
    function dist() { return Math.max(0, track.scrollWidth - innerWidth + parseFloat(getComputedStyle(track).marginLeft) * 0); }
    G.to(track, { x: function () { return -dist(); }, ease: 'none',
      scrollTrigger: { trigger: '.method', start: 'top top', end: function () { return '+=' + (dist() + innerHeight * .3); },
        pin: true, scrub: 1, invalidateOnRefresh: true,
        onUpdate: function (s) {
          fillEl.style.transform = 'scaleX(' + s.progress + ')';
          pips.forEach(function (b, i) { b.classList.toggle('is-on', s.progress >= i / 2 - .02); });
        } } });
    G.from('.panel__art', { opacity: 0, y: 20, stagger: .15, duration: 1, ease: 'power3.out',
      scrollTrigger: { trigger: '.method', start: 'top 60%', once: true } });
  });
  mm.add('(max-width: 899px)', function () {
    ST.batch('.panel', { start: 'top 88%', once: true, onEnter: function (els) {
      G.from(els, { opacity: 0, y: 30, duration: .9, stagger: .1, ease: 'power3.out' });
    } });
  });

  /* ── Proof: the lead card leans toward the pointer, and its light follows ── */
  if (fine) document.querySelectorAll('[data-tilt]').forEach(function (c) {
    var rx = G.quickTo(c, 'rotationX', { duration: .6, ease: 'power3.out' }),
        ry = G.quickTo(c, 'rotationY', { duration: .6, ease: 'power3.out' });
    G.set(c, { transformPerspective: 1100 });
    c.addEventListener('pointermove', function (e) {
      var r = c.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = (e.clientY - r.top) / r.height;
      rx((.5 - y) * 6); ry((x - .5) * 7);
      c.style.setProperty('--mx', x * 100 + '%'); c.style.setProperty('--my', y * 100 + '%');
    });
    c.addEventListener('pointerleave', function () { rx(0); ry(0); });
  });

  /* ── Fit: the ticks draw in, one after another ── */
  ST.batch('.fit__col li', { start: 'top 90%', once: true, onEnter: function (els) {
    G.fromTo(els, { '--ck': 0, opacity: 0, x: -10 }, { '--ck': 1, opacity: 1, x: 0, duration: .7, stagger: .1, ease: 'back.out(2)' });
  } });

  /* ── Magnetic buttons, and the cursor that marks where the reader is ── */
  if (fine) {
    document.querySelectorAll('[data-magnetic]').forEach(function (el) {
      var x = G.quickTo(el, 'x', { duration: .5, ease: 'power3.out' }), y = G.quickTo(el, 'y', { duration: .5, ease: 'power3.out' });
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        x((e.clientX - r.left - r.width / 2) * .22); y((e.clientY - r.top - r.height / 2) * .32);
      });
      el.addEventListener('pointerleave', function () {
        G.to(el, { x: 0, y: 0, duration: .9, ease: 'elastic.out(1,.45)' });
      });
    });
    var cur = document.querySelector('.cursor');
    var cx = G.quickTo(cur, 'x', { duration: .35, ease: 'power3.out' }), cy = G.quickTo(cur, 'y', { duration: .35, ease: 'power3.out' });
    addEventListener('pointermove', function (e) { cur.classList.add('is-on'); cx(e.clientX); cy(e.clientY); });
    document.addEventListener('pointerleave', function () { cur.classList.remove('is-on'); });
    document.querySelectorAll('a,button,input[type=range]').forEach(function (el) {
      el.addEventListener('pointerenter', function () { cur.classList.add('is-link'); });
      el.addEventListener('pointerleave', function () { cur.classList.remove('is-link'); });
    });
  }

  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ST.refresh(); });
})();
