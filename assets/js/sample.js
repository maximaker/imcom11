/* Behaviour for the sample redesign. Four things only, all of them replies to
   something the reader did, per the reference's motion rules: a hairline progress
   report, arrivals that happen once, disclosure that animates to a measured
   height, and a sticky bar that appears after the first screen on small screens. */
(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Hairline progress. Reports rather than decorates. ── */
  var bar = document.getElementById('progress');
  var dock = document.getElementById('dock');
  var ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () {
      var h = document.documentElement.scrollHeight - innerHeight;
      if (bar) bar.style.width = (h > 0 ? Math.min(Math.max(scrollY / h, 0), 1) * 100 : 0) + '%';
      /* The bar is the only thing that appears without being asked for, and only
         once the hero's own button has gone by. */
      if (dock) dock.setAttribute('data-in', scrollY > innerHeight * 0.9 ? 'true' : 'false');
      ticking = false;
    });
  }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll, { passive: true });
  onScroll();

  /* ── Arrival, once. 70ms stagger within a group, then never again. ── */
  var risers = [].slice.call(document.querySelectorAll('.up'));
  if (reduce || !('IntersectionObserver' in window)) {
    risers.forEach(function (el) { el.setAttribute('data-in', 'true'); });
  } else {
    /* Grouped by the section they sit in, so a stagger reads as one block
       arriving rather than as a queue down the whole page. */
    var seen = new WeakMap();
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var group = e.target.closest('section') || document.body;
        var n = seen.get(group) || 0;
        e.target.style.transitionDelay = (n * 0.07) + 's';
        seen.set(group, n + 1);
        e.target.setAttribute('data-in', 'true');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
    risers.forEach(function (el) { io.observe(el); });
  }

  /* ── Disclosure to a measured height, never to a guess. The marker rotates. ── */
  document.querySelectorAll('.q button').forEach(function (btn) {
    var row = btn.closest('.q');
    var panel = row.querySelector('.ans');
    btn.addEventListener('click', function () {
      var open = row.getAttribute('data-open') === 'true';
      row.setAttribute('data-open', open ? 'false' : 'true');
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      if (reduce) { panel.style.height = open ? '0px' : 'auto'; return; }
      if (open) {
        panel.style.height = panel.scrollHeight + 'px';
        requestAnimationFrame(function () { panel.style.height = '0px'; });
      } else {
        panel.style.height = panel.scrollHeight + 'px';
        /* Released to auto once it has arrived, so reflowing text cannot be
           clipped by a height measured at a different width. */
        panel.addEventListener('transitionend', function once(ev) {
          if (ev.propertyName !== 'height') return;
          panel.removeEventListener('transitionend', once);
          if (row.getAttribute('data-open') === 'true') panel.style.height = 'auto';
        });
      }
    });
  });
})();
