/* Sample only: the call to action rides the rail.
   Past the hero it compacts to a dot on the rule and travels with the reader,
   lagging a little so it reads as keeping up rather than being pinned. Through the
   last third it grows into the disc the foot of the rail used to carry, and as the
   closing section arrives it flies to that section's own button, becomes it, and
   hands over. The button it hands to is the real one in the markup, so what the
   reader ends up with is a link in a section rather than something floating.

   Wanted here and nowhere else: the live site keeps its hero button and its foot
   disc untouched. Loaded only by sample-home.html.
   Skipped entirely below the rail's breakpoint and under reduced motion, where the
   closing button simply shows itself. */
(function () {
  var wide = matchMedia('(min-width:1180px)');
  var still = matchMedia('(prefers-reduced-motion: reduce)');
  var rail = document.querySelector('.spine');
  var hero = document.querySelector('.open');
  var closing = document.querySelector('.close');
  var target = closing && closing.querySelector('.act');
  if (!rail || !hero || !closing || !target) return;

  /* Without the ride the closing button is just visible, which is what the
     stylesheet does by default. Nothing else to do. */
  if (still.matches || !wide.matches) { closing.setAttribute('data-handed', 'true'); return; }

  var DOT = 16, DISC = 58;
  var GROW_FROM = 0.55, GROW_TO = 0.86;   /* where the dot becomes the disc */
  var EASE = 0.09;                        /* how far it closes the gap each frame */

  var ride = document.createElement('a');
  ride.className = 'ride';
  ride.href = 'start.html';
  ride.setAttribute('aria-label', 'Tell me about your idea');
  ride.innerHTML =
    '<span class="ride__label">Tell me about your idea</span>' +
    '<span class="ride__chip" aria-hidden="true">' +
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none">' +
    '<path d="M5 12h13m0 0l-5.5-5.5M18 12l-5.5 5.5" stroke="currentColor" ' +
    'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>';
  document.body.appendChild(ride);

  /* Where it is, versus where it wants to be. The gap between the two is the whole
     effect: it is never quite where the scroll has got to. */
  var at = { x: 0, y: 0, w: DOT, h: DOT, r: 999 };
  var to = { x: 0, y: 0, w: DOT, h: DOT, r: 999 };
  var started = false, handed = false, running = false, shown = false;

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function smooth(t) { t = clamp(t); return t * t * (3 - 2 * t); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  function aim() {
    var y = window.scrollY;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? clamp(y / h) : 0;

    /* The hero keeps its own button, so the ride only exists once the hero has
       gone. 120px of overlap, or it appears while the button it replaces is still
       on screen. */
    started = hero.getBoundingClientRect().bottom < -120;

    var slot = target.getBoundingClientRect();
    /* The endgame begins when the closing button's own place comes into view. From
       here it is aiming at that, not at the rail. */
    var landing = slot.top < window.innerHeight - 80;

    if (landing) {
      to.x = slot.left + slot.width / 2;
      to.y = slot.top + slot.height / 2;
      to.w = slot.width; to.h = slot.height;
      to.r = 16;
    } else {
      var r = rail.getBoundingClientRect();
      to.x = r.left + r.width / 2;
      /* Level with the middle of the screen, which is where the reader is looking. */
      to.y = window.innerHeight * 0.5;
      to.w = to.h = lerp(DOT, DISC, smooth((p - GROW_FROM) / (GROW_TO - GROW_FROM)));
      to.r = 999;
    }
    return landing;
  }

  function paint() {
    ride.style.width = at.w + 'px';
    ride.style.height = at.h + 'px';
    ride.style.borderRadius = at.r + 'px';
    ride.style.transform = 'translate(' + (at.x - at.w / 2) + 'px,' +
                                          (at.y - at.h / 2) + 'px)';
    /* The label only exists once there is room for it, so it never clips. */
    ride.setAttribute('data-form', at.w > 150 ? 'pill' : at.w > 34 ? 'disc' : 'dot');
  }

  function frame() {
    var landing = aim();

    if (!started) {
      /* Back in the hero: put it away and stop, rather than easing it up the page. */
      if (shown) { shown = false; ride.setAttribute('data-in', 'false'); }
      at.x = to.x; at.y = to.y; at.w = at.h = DOT; at.r = 999;
      paint();
      running = false;
      return;
    }
    if (!shown) {
      shown = true;
      at.x = to.x; at.y = to.y;          /* arrive where it belongs, then ease */
      ride.setAttribute('data-in', 'true');
    }

    at.x = lerp(at.x, to.x, EASE);
    at.y = lerp(at.y, to.y, EASE);
    at.w = lerp(at.w, to.w, EASE);
    at.h = lerp(at.h, to.h, EASE);
    at.r = lerp(at.r, to.r, EASE);
    paint();

    /* Handed over once it is sitting on the real button: same place, same size, so
       the swap is not visible. */
    var close = landing &&
      Math.abs(at.x - to.x) < 1.5 && Math.abs(at.y - to.y) < 1.5 &&
      Math.abs(at.w - to.w) < 2;
    if (close && !handed) {
      handed = true;
      closing.setAttribute('data-handed', 'true');
      ride.setAttribute('data-in', 'false');
    } else if (handed && !landing) {
      handed = false;
      closing.setAttribute('data-handed', 'false');
      ride.setAttribute('data-in', 'true');
    }

    /* Still catching up? Keep going. Settled and nothing moving? Stop, because the
       page should be still when the reader is. */
    var moving = Math.abs(at.x - to.x) > 0.2 || Math.abs(at.y - to.y) > 0.2 ||
                 Math.abs(at.w - to.w) > 0.2;
    running = moving && !handed;
    if (running) requestAnimationFrame(frame);
  }

  function wake() { if (!running) { running = true; requestAnimationFrame(frame); } }
  addEventListener('scroll', wake, { passive: true });
  addEventListener('resize', wake, { passive: true });
  wake();
})();
