/* Sample only: the call to action rides the rail.
   Past the hero it compacts to a dot on the rule and travels with the reader,
   trailing a little so it reads as keeping up rather than being pinned. Through the
   last third it grows into the disc the foot of the rail used to carry, and as the
   closing section arrives it crosses to that section's own button, becomes it, and
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
  var top = document.querySelector('.hero-cta');
  var start = top && top.querySelector('.act');
  if (!rail || !hero || !closing || !target || !top || !start) return;

  /* Nothing to ride: both real buttons simply show themselves. */
  if (still.matches || !wide.matches) {
    top.setAttribute('data-handed', 'true');
    closing.setAttribute('data-handed', 'true');
    return;
  }

  var DOT = 16, DISC = 58;
  var GROW_BACK = 2;   /* sections before the last one that the regrowth starts in */

  /* Where the growth begins is a place on the page, not a fraction of its height.
     A fraction reads differently on every page: the same 0.50 started the regrowth
     halfway down, which on this one is six sections early, and it would move again
     the moment a section is added. Counting back from the closing section instead
     means it always begins the same number of sections out, whatever the page is. */
  var pivot = null;
  (function () {
    var nodes = [].slice.call(document.querySelectorAll('[data-node]'));
    var i = nodes.indexOf(closing);
    if (i >= GROW_BACK) pivot = nodes[i - GROW_BACK];
  })();

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
  var label = ride.querySelector('.ride__label');
  var chip = ride.querySelector('.ride__chip');

  function clamp(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function smooth(t) { t = clamp(t); return t * t * (3 - 2 * t); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  /* A spring, not a fixed fraction of the remaining distance per frame. Two
     reasons. A fraction is tied to frame rate, so the same page moves twice as
     fast on a 120Hz screen as on a 60Hz one, which is the difference between
     trailing and merely being slow. And a spring carries velocity, so the thing
     arrives with momentum and settles, instead of only ever decelerating: that is
     most of what reads as natural rather than mechanical. */
  function Spring(value, stiffness, damping) {
    this.v = value; this.vel = 0; this.k = stiffness; this.c = damping;
  }
  Spring.prototype.to = function (goal, dt) {
    this.vel += ((goal - this.v) * this.k - this.vel * this.c) * dt;
    this.v += this.vel * dt;
    return this.v;
  };
  Spring.prototype.set = function (v) { this.v = v; this.vel = 0; };
  Spring.prototype.rests = function (goal) {
    return Math.abs(goal - this.v) < 0.3 && Math.abs(this.vel) < 2;
  };

  /* The vertical spring works in document coordinates, not viewport ones, and the
     scroll is subtracted at paint time. This is the whole effect: a target fixed to
     the middle of the screen never moves while the page scrolls, so there is
     nothing to trail and the dot is simply glued there. Chasing a point in the
     document instead means a fast scroll leaves it behind, drifting up the screen,
     and it slides back to the middle when the reader stops.
     Softest on that axis, since that is the one the reader is moving along. A shade under critical damping (2*sqrt(k) is
     about 19), which gives it the smallest overshoot rather than a bounce.
     Stiffer across, because the crossing to the closing button is a decision
     rather than a drift. Size critically damped, because a pill that overshoots
     its own width wobbles. */
  var sy = new Spring(0, 90, 16);
  var sx = new Spring(0, 190, 27);
  var sw = new Spring(DOT, 130, 23);
  var sh = new Spring(DOT, 130, 23);

  var atTop = true, atEnd = false, running = false, last = 0;
  var goal = { x: 0, y: 0, w: DOT, h: DOT, lift: 0, land: 0 };

  function aim() {
    var h = document.documentElement.scrollHeight - window.innerHeight;

    var seat = start.getBoundingClientRect();
    var slot = target.getBoundingClientRect();
    var railBox = rail.getBoundingClientRect();

    /* The rail's x is written by site.js from the real column edge, and it cannot be
       measured while the rail is hidden, so its stylesheet default parks it off to
       the left. Riding to that would send the dot off the side of the screen rather
       than simply not working, which is the worse of the two failures. */
    if (railBox.left < 0) { railBox = seat; }

    /* How far the hero's own button has climbed out of the way. This is the other
       half of the object: the dot on the rail is that button, compacted, so the ride
       begins life sitting exactly on it and takes its place as it leaves. 0 while
       the button is still comfortably in view, 1 once it has gone off the top. */
    goal.lift = smooth((window.innerHeight * 0.5 - (seat.top + seat.height / 2)) /
                       (window.innerHeight * 0.5));

    /* How near the end of the page the reader is, as a fraction over the last three
       quarters of a screen. The aim is blended across this rather than switched at a
       threshold: a target that jumps makes even a good spring look like it changed
       its mind.
       Measured against the end of the page and not against how high the closing
       button has climbed, which was the first attempt and does not work: the footer
       sits below that button, so at full scroll it only ever reaches the middle of
       the screen. The blend saturated at 0.44, the ride stopped half-crossed and
       half-grown, and the handover never fired. */
    var scroll = window.scrollY;
    var left = Math.max(0, h - scroll);
    goal.land = smooth((window.innerHeight * 0.75 - left) / (window.innerHeight * 0.75));

    /* Linear in scroll, and left to the spring to smooth. Two eases stacked on one
       value is what makes growth feel mushy.
       It starts the moment the pivot section first comes into view and is complete
       exactly where the crossing to the closing button begins, so the disc is at
       full size before it has to start becoming a pill and the two movements never
       fight. Falls back to fractions of the page if there is no section to count
       from, which is any page whose closing section is the second one. */
    var growFrom, growTo = h - window.innerHeight * 0.75;
    if (pivot) {
      growFrom = pivot.getBoundingClientRect().top + scroll - window.innerHeight;
    } else {
      growFrom = h * 0.50; growTo = h * 0.88;
    }
    var size = lerp(DOT, DISC, growTo > growFrom
      ? clamp((scroll - growFrom) / (growTo - growFrom))
      : (scroll >= growTo ? 1 : 0));

    /* Three places it can be, blended in order: the hero's button, the rail, the
       closing button. lift crosses the first pair and land the second, and the two
       never overlap, so the whole run is one continuous aim from a pill at the top,
       through a dot on the rule, to a pill at the bottom. Every y is a document
       position, so the trailing survives the blends. */
    var railX = railBox.left + railBox.width / 2;
    var railY = scroll + window.innerHeight * 0.5;

    var x = lerp(seat.left + seat.width / 2, railX, goal.lift);
    var y = lerp(scroll + seat.top + seat.height / 2, railY, goal.lift);
    var w = lerp(seat.width, size, goal.lift);
    var hh = lerp(seat.height, size, goal.lift);

    goal.x = lerp(x, slot.left + slot.width / 2, goal.land);
    goal.y = lerp(y, scroll + slot.top + slot.height / 2, goal.land);
    goal.w = lerp(w, slot.width, goal.land);
    goal.h = lerp(hh, slot.height, goal.land);
  }

  function paint() {
    var w = sw.v, h = sh.v;
    ride.style.width = w + 'px';
    ride.style.height = h + 'px';
    /* The corner follows the shape rather than being animated on its own: a circle
       is half its height, a pill is 16, and everything between is where it is. So
       the radius can never disagree with the outline it is rounding. */
    ride.style.borderRadius = lerp(h / 2, 16, clamp((w / Math.max(h, 1) - 1) / 2)) + 'px';
    /* Document space back to the screen. Where it has got to, minus where the page
       has got to, is how far behind it is. */
    ride.style.transform = 'translate(' + (sx.v - w / 2) + 'px,' +
                                          (sy.v - window.scrollY - h / 2) + 'px)';

    /* Label and chip are driven off the width itself, not off a class flip with its
       own transition. Two clocks on one movement is the other thing that reads as
       synthetic: the label used to arrive on its own schedule while the shape was
       still opening. */
    var lab = clamp((w - 148) / 76);
    label.style.opacity = lab;
    label.style.maxWidth = (lab * 210) + 'px';
    label.style.marginLeft = (lab * 22) + 'px';
    label.style.marginRight = (lab * 10) + 'px';
    chip.style.opacity = clamp((w - 26) / 18);
    ride.setAttribute('data-form', lab > 0.5 ? 'pill' : w > 34 ? 'disc' : 'dot');
  }

  /* The two swaps. Handing over shows the real button and puts the ride away;
     releasing does the reverse. */
  function hand(host) {
    host.setAttribute('data-handed', 'true');
    ride.setAttribute('data-in', 'false');
  }
  function release(host) {
    host.setAttribute('data-handed', 'false');
    ride.setAttribute('data-in', 'true');
  }

  function frame(now) {
    /* Real elapsed time, clamped: a backgrounded tab or one long frame would
       otherwise hand the spring a step it cannot integrate and throw it. */
    var dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
    last = now;

    aim();

    /* Parked on whichever real button is currently showing. The springs are held
       exactly on it rather than integrated, so the moment the reader moves, the ride
       takes over from a position identical to the button it replaces and the swap is
       never visible in either direction. */
    if (atTop || atEnd) {
      sx.set(goal.x); sy.set(goal.y); sw.set(goal.w); sh.set(goal.h);
      paint();
      if (atTop && goal.lift > 0.02) { atTop = false; release(top); }
      else if (atEnd && goal.land < 0.9) { atEnd = false; release(closing); }
      else { running = false; return; }
    }

    /* Integrated in fixed sub-steps rather than one step per frame. The spring is
       solved by plain Euler, whose error grows with the step, so a 60Hz screen and a
       120Hz screen were landing about 6% apart on the same scroll. Sub-stepping puts
       both on the same trajectory whatever the display does. */
    var step = 1 / 120, n = Math.max(1, Math.ceil(dt / step)), sub = dt / n;
    for (var i = 0; i < n; i++) {
      sx.to(goal.x, sub); sy.to(goal.y, sub);
      sw.to(goal.w, sub); sh.to(goal.h, sub);
    }

    /* A ceiling on how far behind it is allowed to fall. The spring's steady lag is
       proportional to scroll speed, so a gentle read leaves it 70px back and a hard
       flick would throw it most of a screen away, which stops reading as keeping up
       and starts reading as lost. Bounded at a third of the screen, and only while
       it is still on the rail: during the crossing the target is the button, and it
       is allowed to take as long as it takes. */
    if (goal.land < 0.01) {
      var maxLag = window.innerHeight * 0.34;
      var rest = window.scrollY + window.innerHeight * 0.5;
      if (rest - sy.v > maxLag) { sy.v = rest - maxLag; }
      else if (sy.v - rest > maxLag) { sy.v = rest + maxLag; }
    }
    paint();

    /* Handed over once it is sitting on a real button: same place, same size, so
       the swap is not visible at either end. */
    var settled = sx.rests(goal.x) && sy.rests(goal.y) && sw.rests(goal.w);
    if (!atEnd && goal.land > 0.99 && settled) { atEnd = true; hand(closing); }
    else if (!atTop && goal.lift < 0.01 && settled) { atTop = true; hand(top); }

    /* Still catching up? Keep going. Settled, and the reader is still? Stop: the
       page has no idle motion in it anywhere else either. */
    running = !atTop && !atEnd && !(sx.rests(goal.x) && sy.rests(goal.y) &&
                                    sw.rests(goal.w) && sh.rests(goal.h));
    if (running) requestAnimationFrame(frame);
  }

  function wake() {
    if (!running) { running = true; last = 0; requestAnimationFrame(frame); }
  }
  /* Starts parked on the hero's button, which is where the object begins. */
  top.setAttribute('data-handed', 'true');
  addEventListener('scroll', wake, { passive: true });
  addEventListener('resize', wake, { passive: true });
  wake();
})();
