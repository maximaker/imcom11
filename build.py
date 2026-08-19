#!/usr/bin/env python3
"""Builds the five pages from one shell so the chrome can never drift apart."""
import hashlib
import re
import pathlib


def ver(path):
    """Content hash for an asset URL. The pages are regenerated on every build, so
    a changed stylesheet or script always arrives under a new URL and a browser
    cannot serve a stale copy against new markup. Without this, an edit to
    style.css or site.js is invisible until a hard reload."""
    p = pathlib.Path(path)
    return hashlib.sha1(p.read_bytes()).hexdigest()[:8] if p.exists() else '0'


V_CSS = ver('assets/css/style.css')
V_SITE = ver('assets/js/site.js')
V_INTRO = ver('assets/js/intro.js')
V_GSAP = ver('assets/js/vendor/gsap.min.js')
V_RIDE = ver('assets/js/ride.js')

NAV = [("how-it-works.html", "How it works"),
       ("what-ive-built.html", "What I've built"),
       ("about.html", "About"),
       ("start.html", "Start")]

ARROW = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
         '<path d="M5 12h13m0 0l-5.5-5.5M18 12l-5.5 5.5" stroke="currentColor" '
         'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

MARK = ('<svg class="mark" viewBox="0 0 32 32" aria-hidden="true">'
        '<path class="mark__ring" d="M25.1 22.2A11 11 0 1 1 25.1 9.8"/>'
        '<path class="mark__lead" d="M18.6 16h11.2"/>'
        '<circle class="mark__core" cx="16" cy="16" r="3.7"/></svg>')

# Split so the two halves can differ in weight: the design system sets "one
# flow" light and "first" semibold, with the dot as the accent, so the mark
# says which half of it is the name. Kept inside the one <span> because
# intro.js reveals '.top .name span'.
WORDMARK = '<i>one flow</i><em aria-hidden="true"></em><b>first</b>'

GATE = '''<script>
/* Decides, before anything paints, whether the first-load animation runs. It has
   to be inline and here: hiding the page from a deferred script means showing it
   first and then snatching it back. */
(function(){
  var d=document.documentElement, force=false, hard=false;
  try{
    /* An explicit way in, for reviewing it on demand: ?intro or #intro. */
    force = new URLSearchParams(location.search).has('intro') || location.hash === '#intro';
    /* And a best effort at ctrl+shift+R. A page cannot read modifier keys on
       load, but a hard reload bypasses the cache, so the document really comes
       down the wire; a plain reload is answered from cache or with a 304.
       transferSize is what tells them apart. encodedBodySize does not: it reports
       the full body either way, so a plain reload looks like a download by that
       measure and the animation would replay on every single one. Downloaded means
       the bytes on the wire cover the body; from cache it is headers only. */
    var nav = performance.getEntriesByType('navigation')[0];
    hard = !!nav && nav.type === 'reload' &&
           nav.transferSize > 0 && nav.transferSize >= nav.encodedBodySize;
  }catch(e){}
  try{
    if(!force && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if(!force && !hard && localStorage.getItem('ofo.intro') === '1'){
      if(window.console) console.info(
        'one flow first: first-load animation already seen. ' +
        'A hard reload replays it, or add ?intro to the URL.');
      return;
    }
    /* Written now rather than when the animation ends, so navigating away
       halfway still counts as having seen it. */
    localStorage.setItem('ofo.intro','1');
  }catch(e){ if(!force) return; }   /* no storage, no animation: never twice */
  d.setAttribute('data-intro','running');
  /* Fetched here rather than linked in the markup: this runs once, and the other
     99% of loads should not pay 72KB for it. async=false on an injected script
     keeps execution order without blocking the parser. */
  ['assets/js/vendor/gsap.min.js?v=@GSAP@','assets/js/intro.js?v=@INTRO@'].forEach(function(src){
    var el=document.createElement('script');
    el.src=src; el.async=false; d.appendChild(el);
  });
  /* If the script never arrives, the page must not stay hidden. Generous enough
     that a slow connection still gets the animation, bounded enough that a
     broken one is not a blank page. */
  setTimeout(function(){
    if(d.getAttribute('data-intro')==='running' && !window.__introStarted){
      d.removeAttribute('data-intro');
      document.dispatchEvent(new Event('intro:ready'));
    }
  },3000);
})();
</script>'''

NOSCRIPT = '''<noscript><style>
/* Almost every block on the page is a .rev, revealed by the observer in
   site.js. Without it the page is a masthead over an empty column, so the
   reveal is opt-in: present the content, and let the motion be the thing that
   needs JS. The accordions collapse with grid-template-rows and would take
   their bodies with them, so they stand open here too. */
.rev{opacity:1;transform:none}
.asset .more{grid-template-rows:1fr}
.asset .sign{display:none}
</style></noscript>
'''

# Hoisted out of shell()'s f-string for the same reason GATE is: the CSS above
# is all braces, and an f-string reads every one of them as a field.

# Versions are substituted rather than interpolated: GATE is a plain string,
# and the script inside it is full of braces an f-string would try to read.
GATE = GATE.replace('@GSAP@', V_GSAP).replace('@INTRO@', V_INTRO)


def screen(label, body):
    """A phone-sized line drawing standing in for a screenshot. Swap the whole
    <svg> for <img src="assets/img/name.png" alt="..."> when a real one exists:
    .shot styles the figure, not the medium."""
    return (f'<svg class="screen" viewBox="0 0 320 600" role="img" aria-label="{label}">'
            f'<rect class="fr" x="8" y="8" width="304" height="584" rx="30"/>'
            f'{body}</svg>')


def shot(caption, label, body):
    return (f'        <figure class="shot rev">{screen(label, body)}'
            f'<figcaption>{caption}</figcaption></figure>')


def margin(label, title, note):
    return (f'<div class="margin"><b>{label}</b>{title}'
            f'<em>{note}</em></div>')


def slug(node):
    """A section's id, from its own node name. Needed for two things: a reader can
    be sent to a section by link, and the rail's beads can become the navigation
    they already look like."""
    return 'n-' + re.sub(r'[^a-z0-9]+', '-', node.lower()).strip('-')


def band(node, label, title, note, body, tinted=False, extra_class=""):
    """Every band carries its own wrappers, so blocks never depend on order."""
    inner = (f'    <section class="band {extra_class}" id="{slug(node)}" data-node="{node}">\n'
             f'      {margin(label, title, note)}\n'
             f'      <div>\n{body}\n      </div>\n'
             f'    </section>')
    if tinted:
        return (f'<div class="tinted">\n  <div class="doc">\n'
                f'{inner}\n  </div>\n</div>')
    return f'<div class="doc">\n{inner}\n</div>'

def hero(margin_html, h1, deck, extra=""):
    return (f'<div class="doc">\n  <section class="open">\n    <div class="inner">\n'
            f'      {margin_html}\n      <div>\n        {h1}\n'
            f'        <p class="deck rev">{deck}</p>\n{extra}      </div>\n'
            f'    </div>\n  </section>\n</div>')


def shell(slug, title, desc, body, close_heading, close_body,
          nav_slug=None, robots=None, close_cta="Tell me about your idea"):
    """nav_slug lets a child page mark its parent as current. robots is for
    pages that should stay out of search, such as the case study template.

    close_cta is the label on the closing button. It is a parameter because of the
    travelling call to action: on a page where that runs, the button the reader ends
    up with is the hero's button, carried down, so the two have to read the same or
    the words change in the instant the handover is meant to be invisible. Pages
    without a hero button keep the plainer wording, since nothing travels there."""
    here = nav_slug or slug
    robots = f'<meta name="robots" content="{robots}">\n' if robots else ''
    # The ride is the hero's button, compacted and carried down the rail, so it is
    # only shipped to a page that has one to start from. Asking the markup rather
    # than keeping a list of slugs: add a hero button to a page and it rides.
    RIDE = (f'<script src="assets/js/ride.js?v={V_RIDE}" defer></script>'
            if 'class="hero-cta' in body else '')
    nav = "\n      ".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == here else ""}>{t}</a>'
        for h, t in NAV)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}<meta name="theme-color" content="#FAF3E3">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="assets/css/style.css?v={V_CSS}">
{NOSCRIPT}{GATE}
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23171B34'/><path d='M24.3 21.6A10 10 0 1 1 24.3 10.4' fill='none' stroke='%23FAF3E3' stroke-width='3' stroke-linecap='round'/><circle cx='16' cy='16' r='3.5' fill='%23C4522C'/></svg>">
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>

<div class="surface" aria-hidden="true"></div>

<div class="intro" id="intro" aria-hidden="true">
  <svg class="intro__mark" id="intro-mark" viewBox="0 0 32 32">
    <g id="intro-swarm"></g>
    <path class="mark__ring" id="intro-ring" d="M25.1 22.2A11 11 0 1 1 25.1 9.8"/>
    <path class="mark__lead" id="intro-lead" d="M18.6 16h11.2"/>
    <circle class="mark__core" id="intro-core" cx="16" cy="16" r="3.7"/>
  </svg>
</div>

<div class="spine" aria-hidden="true">
  <div class="track"></div><div class="fill" id="spinefill"></div>
</div>

<header class="top" id="top">
  <div class="doc top__row">
    <a class="name" href="index.html" aria-label="one flow first, home">{MARK}<span>{WORDMARK}</span></a>
    <button class="navtoggle" type="button" aria-expanded="false" aria-controls="nav" aria-label="Open menu">
      <span aria-hidden="true"></span><span aria-hidden="true"></span>
    </button>
    <nav id="nav" aria-label="Primary">
      {nav}
    </nav>
  </div>
</header>

<main id="main">
{body}

  <div class="doc">
  <section class="close rev" data-node="Start">
    <div class="margin"><b>Next</b>Step one<em>Ten minutes of questions, then a reply from a person.</em></div>
    <div>
      <h2>{close_heading}</h2>
      <p class="lede" style="margin-bottom:32px">{close_body}</p>
      <a class="act" href="#intake" id="cta"><span>{close_cta}</span>
        <span class="chip" aria-hidden="true">{ARROW}</span></a>
    </div>
  </section>

  </div>

{TAKEOVER}
</main>

<footer class="colo">
  <span>&copy; 2026 One flow first</span>
  <span><a href="mailto:hello@oneflowfirst.com">hello@oneflowfirst.com</a></span>
</footer>

<script src="assets/js/site.js?v={V_SITE}" defer></script>
{RIDE}
</body>
</html>
'''


# ─────────────────────────── page bodies ───────────────────────────

HOME_HERO = '''<div class="heroband" id="heroband">
  <div class="bloom" aria-hidden="true"><i></i><i></i><i></i></div>
  <div class="lamp" aria-hidden="true"></div>
  <div class="doc">
  <section class="open" id="hero">
    <div class="inner">
      <div class="margin"><b>The offer</b>Two weeks<em>Fixed scope. Fixed price. The bar agreed before the build.</em></div>
      <div>
        <h1>
          <span class="rise"><span>Is your idea</span></span>
          <span class="rise"><span><strong>worth building?</strong></span></span>
        </h1>
        <p class="deck rev">In two weeks you own <b>the one part that matters most</b>, built for real, and a bar agreed before anyone sees it.</p>

        <p class="principle rev">One flow first. <span>Nothing else yet.</span></p>

        <p class="hero-cta rev"><a class="act" href="start.html"><span>Tell me about your idea</span>
          <span class="chip" aria-hidden="true">''' + ARROW + '''</span></a></p>
        <p class="act-note rev">Twenty minutes. You'll get a straight read on whether this fits, either way.
          <a class="quiet quiet--inline" href="#n-fit">Not sure yet? See who this works for ''' + ARROW + '''</a></p>

        <div class="stats rev">
          <div class="stat"><b>20 years</b><span>Deciding what to build, and what to cut.</span></div>
          <div class="stat"><b>9 apps</b><span>Built and shipped in the last few months.</span></div>
          <div class="stat"><b>2 weeks</b><span>From an idea in a doc to something real to test.</span></div>
        </div>
      </div>
    </div>
  </section>
  </div>
</div>

<div class="doc">
  <section class="band band--scene" data-node="The shape of it">
    <div class="margin"><b>Figure</b>The shape of it<em>Most of what you could build never needed building.</em></div>
    <div class="scene" id="scene">
      <div class="pin">
        <svg viewBox="0 0 1000 420" role="img" aria-label="Forty possible things to build narrow in stages to the single one worth testing">
          <g id="dots"></g>
          <circle class="halo" id="halo" cx="500" cy="210" r="34"/>
        </svg>
        <div class="caption" id="caption">
          <span data-i="0"><b>Everything you could build</b><i>Every feature, every version, every direction the idea could take.</i></span>
          <span data-i="1"><b>Plausible</b><i>The ones that survive a hard look at the customer and the money.</i></span>
          <span data-i="2"><b>Worth testing</b><i>Few enough to put in front of real people at all.</i></span>
          <span data-i="3" data-key="true" data-final="true"><b>The one that decides it</b><i>Built for real, tested against a bar you set in advance.</i></span>
        </div>
        <div class="ticks" aria-hidden="true">
          <i data-k="0"></i><i data-k="1"></i><i data-k="2"></i><i data-k="3"></i>
          <span class="counter" id="counter">40 possible</span>
        </div>
      </div>
    </div>
  </section>
</div>'''

HOME = HOME_HERO + "\n\n" + band(
    "The bind", "One", "The bind", "Most ideas die of the wrong question, not the wrong code.",
    '''      <h2>The scary part isn't building it. <strong>It's building the wrong thing.</strong></h2>
      <p class="lede">Your idea has probably been sitting in a doc for a while. Not because you're lazy, but because committing real money to it feels like a leap and you can't quite see where you'd land.</p>
      <p class="lede">That instinct is right. Most ideas don't fail because nobody could build them. They fail because someone spent months and a pile of money before finding out that <strong>nobody wanted the thing that got built</strong>.</p>''',
    tinted=True) + "\n\n" + band(
    "After", "Two", "After", "The difference between hoping and being able to find out.",
    '''      <h2 class="rev">In two weeks, guessing turns into <strong>something you can test</strong></h2>
      <p class="lede">Instead of a doc full of hope and a knot in your stomach, you have something real in your hands and <strong>a bar you agreed to before you saw a single result</strong>.</p>
      <p class="lede">You can walk into a room and show it, not describe it. And when you put it in front of real people, you already know what a good result looks like, so the answer can't quietly become whatever you were hoping for.</p>
      <p class="lede">If it's a go, you know exactly what to build next. If it's a stop, you kept your money and a year of your life.</p>''') + "\n\n" + band(
    "Method", "Three", "Method", "Three steps. The first one can end the project, cheaply.",
    '''      <h2 class="rev">Three steps, <strong>start to answer</strong></h2>
      <div class="steps">
        <div class="step"><span class="n">Step one</span><h3>Find out if it's worth building.</h3><p>You bring the idea. Together you find the one thing that has to be true for it to work, and you get a straight call. If there's a fatal flaw, you find it here, cheaply, before anything gets built.</p></div>
        <div class="step"><span class="n">Step two</span><h3>Get a real version of the part that matters.</h3><p>One working flow that real people can actually use. Not a mockup. Something you can put in front of users.</p></div>
        <div class="step"><span class="n">Step three</span><h3>Test it and decide, with a clear rule.</h3><p>The bar gets set inside the two weeks, before anyone sees the build. The sessions themselves run when your people are actually free, and the playbook tells you exactly how. Or they can be run for you.</p></div>
      </div>
      <p class="rev" style="margin-top:34px"><a class="quiet" href="how-it-works.html">See how it works in detail ''' + ARROW + '''</a></p>''') + "\n\n" + band(
    "Deliverables", "Four", "Deliverables", "Named things. Yours to keep, extend, or hand to any team.",
    '''      <h2 class="rev">What you <strong>own</strong> at the end</h2>
      <div class="assets">
        <div class="asset" data-open="false">
          <button type="button" aria-expanded="false" aria-controls="a1">
            <svg class="glyph" viewBox="0 0 24 24" aria-hidden="true"><rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M9.5 8.5h5M9.5 12h5M9.5 15.5h2.5"/></svg>
            <span class="nm">The working build</span>
            <span class="sm">One real flow through the core of your idea, usable on a phone.</span>
            <span class="sign" aria-hidden="true"></span>
          </button>
          <div class="more" id="a1"><div><p>Yours to keep, extend, or hand to any team. No license, no lock-in, no dependency on me continuing to exist. If you take it to another developer tomorrow, everything they need is in the repository.</p></div></div>
        </div>
        <div class="asset" data-open="false">
          <button type="button" aria-expanded="false" aria-controls="a2">
            <svg class="glyph" viewBox="0 0 24 24" aria-hidden="true"><path d="M5.5 3.5h9l4 4v13h-13z"/><path d="M14.5 3.5v4h4"/><path d="M8.5 14l2.5 2.5 4.5-5"/></svg>
            <span class="nm">The decision brief</span>
            <span class="sm">The riskiest assumption, the bar it has to clear, and how to read what comes back.</span>
            <span class="sign" aria-hidden="true"></span>
          </button>
          <div class="more" id="a2"><div><p>Short enough to read in one sitting and written so a co-founder or an investor can read it too. It states the question and the bar first, then how to tell a go from an adjust from a stop. Once the sessions are done the call goes at the top, with the evidence behind it. If the two ever disagree, trust the evidence.</p></div></div>
        </div>
        <div class="asset" data-open="false">
          <button type="button" aria-expanded="false" aria-controls="a3">
            <svg class="glyph" viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 17.5l5-5 3.5 3 4-6.5"/><circle cx="8.5" cy="12.5" r="1.6"/><circle cx="12" cy="15.5" r="1.6"/><circle cx="16" cy="9" r="1.6"/></svg>
            <span class="nm">The testing playbook</span>
            <span class="sm">How to find the right people and run sessions that stay honest.</span>
            <span class="sign" aria-hidden="true"></span>
          </button>
          <div class="more" id="a3"><div><p>Where to find people with the problem rather than people who like you, how many you actually need (fewer than you would expect), and how to keep politeness from quietly ruining your results. Reusable on every idea you have after this one.</p></div></div>
        </div>
      </div>
      <p class="lede rev" style="margin-top:26px">That last one matters more than it looks. It's <strong>the part that keeps working long after the two weeks end</strong>.</p>''',
    tinted=True) + "\n\n" + band(
    "Terms", "Five", "Terms", "The unusual promise.",
    '''      <h2 class="statement" id="statement" data-key="never stuck with me.">You should never be stuck with me.</h2>
      <p class="lede rev">Plenty of people in this business are quietly hoping you'll stay. This works the other way round. When the two weeks end, you can read your own evidence, make your own call, and move forward or walk away without another opinion. You keep the build, the brief, and the method.</p>
      <p class="lede rev">People do come back. Usually with the next idea, or the same one pointed somewhere new. That's <strong>a choice, not a dependency</strong>, and it's the only kind worth having.</p>''') + "\n\n" + band(
    "Pricing", "Six", "Pricing", "You'll see the whole staircase before you take the first step.",
    '''      <h2 class="rev">How <strong>pricing works</strong></h2>
      <div class="stairs">
        <div class="stair rev"><p class="k">Step one</p><h3>Is this worth building?</h3><p>A small fixed price, set so it's worth it even when the answer is "don't build."</p></div>
        <div class="stair rev"><p class="k">Step two</p><h3>The build</h3><p>Scoped after step one, once you both know what's actually needed. No surprise numbers, no big commitment before you have proof.</p></div>
        <div class="stair rev"><p class="k">Optional</p><h3>The testing, run for you</h3><p>Finding the right people and getting them in front of it takes real calendar time, which is why it sits outside the two weeks. Run it yourself with the playbook, or have it added on.</p></div>
      </div>''',
    tinted=True) + "\n\n" + band(
    "Trust", "Seven", "Why trust it", "Competence, stated as what you get.",
    '''      <h2 class="rev">Why you can <strong>trust the answer</strong></h2>
      <div class="grid3">
        <div class="rev"><h3>You get judgment, not just a build.</h3><p>Anyone can generate an app now. The hard part is knowing what to make and what to cut, and that's the part you're paying for.</p></div>
        <div class="rev"><h3>You get advice from someone who isn't paid to say yes.</h3><p>When the honest answer is "don't build this," you'll hear it. That's only possible because the value here is the clarity, not the code.</p></div>
        <div class="rev"><h3>You get speed without losing the thinking.</h3><p>The idea gets real in days, with a designer's read on how people actually behave built in.</p></div>
      </div>
      <p class="lede rev" style="margin-top:30px">The judgment comes from 20 years of deciding what to build and what to cut. The speed comes from nine working apps built in the last few months. If you want that story, it's on the <a href="about.html">about page</a>.</p>''') + "\n\n" + band(
    "Proof", "Eight", "Proof", "Not theory. Things that run.",
    '''      <h2 class="rev">Nine apps, and <strong>what each one taught me</strong></h2>
      <p class="lede">These were built for real ideas, with the same tools and the same speed you'd get. What matters isn't that they work. It's what got cut to make them work.</p>
      <div class="proofs">
        <div class="proof rev">
          <h3>Slate</h3>
          <p>A booking page for independent physios who ran everything through WhatsApp.</p>
          <p class="kill"><b>What I'd kill</b>The week view. Four days of work, used by two of ten people.</p>
        </div>
        <div class="proof rev">
          <h3>[APP NAME 2]</h3>
          <p>[ONE LINE]</p>
          <p class="kill"><b>What I'd kill</b>[WHAT I'D KILL]</p>
        </div>
        <div class="proof rev">
          <h3>[APP NAME 3]</h3>
          <p>[ONE LINE]</p>
          <p class="kill"><b>What I'd kill</b>[WHAT I'D KILL]</p>
        </div>
      </div>
      <p class="rev" style="margin-top:34px"><a class="quiet" href="what-ive-built.html">See the full thinking behind them ''' + ARROW + '''</a></p>''',
    tinted=True) + "\n\n" + band(
    "Fit", "Nine", "Fit", "Two lists. Ten minutes of questions settle which one is yours.",
    '''      <h2 class="rev">Who this <strong>works for</strong></h2>
      <div class="fit">
        <div class="fit__col rev">
          <p class="fit__title yes">This fits if</p>
          <ul class="checklist">
            <li>You have an idea you believe in but can't build yourself.</li>
            <li>You'd rather hear a hard truth early than a comfortable one late.</li>
            <li>You're ready to put something in front of real people in the next month or two.</li>
          </ul>
        </div>
        <div class="fit__col no rev">
          <p class="fit__title no">This probably isn't it if</p>
          <ul class="checklist cross">
            <li>You already know exactly what you want built and just need hands.</li>
            <li>You need a finished, scalable product rather than something to learn from.</li>
            <li>You'd rather not hear that the idea has a problem.</li>
          </ul>
        </div>
      </div>
      <p class="lede rev" style="margin-top:26px">No hard feelings either way.</p>''') + "\n\n" + band(
    "Doubts", "Ten", "Said out loud", "The three things people think and rarely say.",
    '''      <h2 class="rev">You might be <strong>thinking</strong></h2>
      <div class="doubts">
        <div class="doubt rev" tabindex="0"><p class="q">"What if it's a bad idea and I find out too late."</p><p class="a">You find out first, before anything gets built.</p></div>
        <div class="doubt rev" tabindex="0"><p class="q">"I'm not technical. I won't understand what's happening."</p><p class="a">You don't need to be. You'll get it explained clearly enough to decide with confidence.</p></div>
        <div class="doubt rev" tabindex="0"><p class="q">"I don't want to be talked into a build I don't need."</p><p class="a">You won't be. You'll get an honest answer even when the honest answer is no.</p></div>
      </div>''',
    tinted=True) + "\n\n" + band(
    "Questions", "Eleven", "Questions", "The ones that actually get asked.",
    '''      <h2 class="rev">Questions <strong>people ask</strong></h2>
      <div class="faq rev">
        <details><summary>What if you tell me my idea is bad?<i aria-hidden="true"></i></summary><div><p>Then you've saved months and a fortune, and you'll get a clear reason why, not a vague no.</p></div></details>
        <details><summary>Do I need to understand the tech?<i aria-hidden="true"></i></summary><div><p>No. You need to understand your customer. The rest is handled.</p></div></details>
        <details><summary>Who owns what gets built?<i aria-hidden="true"></i></summary><div><p>You do. It's yours to take anywhere.</p></div></details>
        <details><summary>Is this a full product?<i aria-hidden="true"></i></summary><div><p>No, and that's the point. It's the smallest real thing that answers the biggest question. Building the full product before that answer is exactly the expensive mistake this avoids.</p></div></details>
        <details><summary>How long until I actually have an answer?<i aria-hidden="true"></i></summary><div><p>The build and the bar take two weeks. The answer takes as long as it takes to get the right people in front of it, usually a week or two more, and that part nobody can promise. Which is exactly why the sessions sit outside the fixed scope: putting them inside would mean either padding the timeline or rushing the recruiting, and rushed recruiting is how you end up testing on whoever was available instead of whoever has the problem.</p></div></details>
        <details><summary>What if I already know it's a good idea?<i aria-hidden="true"></i></summary><div><p>Then step one is quick and you'll have saved nothing but a little time. Most people who are certain turn out to be certain about the wrong part.</p></div></details>
      </div>''')

HOWITWORKS = '''<div class="doc">
  <section class="open">
    <div class="inner">
      <div class="margin"><b>How it works</b>The full process<em>Written from your side, not mine.</em></div>
      <div>
        <h1><span class="rise"><span>Here's exactly what</span></span><span class="rise"><span><strong>happens.</strong></span></span></h1>
        <p class="deck rev">Two weeks, two steps, and a bar set before anyone sees the build. No surprises for you.</p>
      </div>
    </div>
  </section>
</div>''' + "\n\n" + band(
    "Step one", "One", "Step one", "If something fatal shows up, you find it here.",
    '''      <h2 class="rev">Is this <strong>worth building?</strong></h2>
      <p class="lede">Before a line of anything gets made, you get clarity on the questions that decide whether the idea survives contact with the real world.</p>
      <ul class="probe">
        <li><strong>Is this a real, painful problem, or a feature that sounds cool?</strong> One gets paid for. The other gets admired and forgotten.</li>
        <li><strong>Who exactly is the customer, and can you reach them?</strong> "Everyone" is not a customer. A reachable group of people with the same problem is.</li>
        <li><strong>Would people pay, or would they just say "I'd use it"?</strong> Those are not the same sentence, and only one of them is evidence.</li>
        <li><strong>Is the exciting part actually the risky part?</strong> Usually not. The risk is somewhere quieter, and that's the thing worth testing.</li>
      </ul>''',
    tinted=True) + "\n\n" + band(
    "The rule", "Two", "The decision rule", "A bar set after seeing the data is a bar that moves.",
    '''      <h2 class="rev">Agreed <strong>before testing</strong></h2>
      <p class="lede">You agree in advance what a result means. Not after you've seen the data, when hope starts quietly moving the bar. Before.</p>
      <div class="verdicts">
        <div class="verdict go rev"><p class="k">Go</p><p>People do the thing without being nudged, and they come back to it. You know what to build next.</p></div>
        <div class="verdict adjust rev"><p class="k">Adjust</p><p>The problem is real but the shape is wrong. You know specifically what to change, not just "iterate."</p></div>
        <div class="verdict stop rev"><p class="k">Stop</p><p>People are polite but nothing pulls them. You keep your money and move on to a better idea.</p></div>
      </div>''') + "\n\n" + band(
    "Step two", "Three", "Step two", "What gets left out is a decision, not an oversight.",
    '''      <h2 class="rev">The part that matters, <strong>made real</strong></h2>
      <p class="lede">One idea, one flow, the one that matters. You end up with something a real person can pick up and use on a phone, without you standing over their shoulder explaining it.</p>
      <p class="lede"><strong>Real enough to test</strong> means the core action works end to end, it's fast, and it doesn't look like a prototype. People behave differently in front of something that feels real, and that difference is where the honest data comes from.</p>
      <p class="lede"><strong>What gets left out on purpose:</strong> accounts and settings you don't need yet, edge cases nobody will hit in a test session, admin screens, polish on flows that aren't the question, and anything built for scale you haven't earned.</p>''',
    tinted=True) + "\n\n" + band(
    "The brief", "Four", "The decision brief", "Read the call first, then the evidence.",
    '''      <h2 class="rev">What the <strong>brief contains</strong></h2>
      <ul class="probe">
        <li><strong>The riskiest assumption.</strong> Stated in one sentence, the way you'd say it out loud.</li>
        <li><strong>How to read what comes back.</strong> What to count as a signal, which flattering moments to ignore, and what people doing rather than saying looks like on paper.</li>
        <li><strong>The call.</strong> Go, adjust, or stop, measured against the rule you set in advance and written once the sessions are done.</li>
        <li><strong>What you'd do next.</strong> Either the shortest path forward or the honest reason there isn't one.</li>
      </ul>
      <p class="lede" style="margin-top:24px">If the call and the evidence ever disagree, trust the evidence and come argue about it.</p>''') + "\n\n" + band(
    "The playbook", "Five", "The testing playbook", "The method, handed over.",
    '''      <h2 class="rev">So the next idea <strong>needs no one else</strong></h2>
      <ul class="probe">
        <li><strong>Where to find the right people.</strong> The ones with the problem, not the ones who like you.</li>
        <li><strong>How many you actually need.</strong> Fewer than you'd expect. The big patterns show up early, and the rest is confirmation.</li>
        <li><strong>How to run a session.</strong> What to ask, what never to ask, and how to keep politeness from quietly ruining your results.</li>
        <li><strong>What to measure.</strong> The handful of signals that mean something, and the flattering ones that don't.</li>
      </ul>
      <p class="lede" style="margin-top:24px">Finding the right people is the part that takes real calendar time, and it depends on strangers being free. That's why the sessions sit outside the two weeks rather than inside a timeline nobody can honestly promise. Run them yourself with this, or have them run for you as an add-on.</p>''',
    tinted=True) + "\n\n" + band(
    "After", "Six", "What happens after", "All three outcomes beat not knowing.",
    '''      <h2 class="rev">What <strong>happens after</strong></h2>
      <p class="lede">Three ways this ends.</p>
      <div class="verdicts">
        <div class="verdict go rev"><p class="k">Continue</p><p>The core assumption held. You know what to build next, and you can build it with anyone, including me.</p></div>
        <div class="verdict adjust rev"><p class="k">Pivot</p><p>Part of it held and part of it didn't. The idea points somewhere new, and the same two weeks can run again on the changed version. New question, same method.</p></div>
        <div class="verdict stop rev"><p class="k">Stop</p><p>It didn't hold. You'll get a clear reason why it's a real stop and not "try harder", and you'll have kept the money you would have spent finding out the long way.</p></div>
      </div>
      <p class="lede rev" style="margin-top:26px">Some people come back after a pivot, or later with a different idea. None of that is decided up front. The two weeks stand on their own.</p>''')

BUILT = '''<div class="doc">
  <section class="open">
    <div class="inner">
      <div class="margin"><b>Proof</b>What I've built<em>Chosen for judgment shown, not technical polish.</em></div>
      <div>
        <h1><span class="rise"><span>Real apps, built</span></span><span class="rise"><span><strong>for real ideas.</strong></span></span></h1>
        <p class="deck rev">Here's the thinking behind them, not just the screenshots. The change and kill notes are the point, and the first one is written out in full.</p>
      </div>
    </div>
  </section>
</div>''' + "\n\n" + band(
    "App 01", "App 01", "Slate", "Booking for independent physios. An adjust, not a go. A worked example: the numbers are illustrative.",
    '''      <h2 class="rev">Slate</h2>
      <p class="lede">A booking page for independent physios who ran everything through WhatsApp.</p>
      <div class="case rev">
        <div class="case__block"><h3 class="case__k">The problem it solves</h3><p>Around sixty regulars, a phone that never stopped, and a Sunday evening spent copying appointments into a paper diary. The alternative was answering the same message forty times a week.</p></div>
        <div class="case__block change"><h3 class="case__k">What I'd change if this were a paid product</h3><p>Make the confirmation the product. Nine of ten people booked unaided, and seven then messaged to check it had worked. The reply is the thing they wanted; the calendar was scaffolding.</p></div>
        <div class="case__block kill"><h3 class="case__k">What I'd kill</h3><p>The week view. Four days of work, used by two of ten people. It survived because it looks like the thing a booking tool is supposed to have.</p></div>
      </div>
      <p class="rev" style="margin-top:32px"><a class="quiet" href="case-slate.html">Read the full case note ''' + ARROW + '''</a></p>''',
    tinted=True) + "\n\n" + "\n\n".join(
    band(f"App {i:02d}", f"App {i:02d}", "[App name]", "[One line you'd say to a friend.]",
         f'''      <h2 class="rev">[App name]</h2>
      <p class="lede">[One line: what it is, said the way you'd say it to a friend.]</p>
      <div class="case rev">
        <div class="case__block"><h3 class="case__k">The problem it solves</h3><p>[Who had the problem, what it cost them, and what they were doing instead before this existed.]</p></div>
        <div class="case__block change"><h3 class="case__k">What I'd change if this were a paid product</h3><p>[The one structural change that would make people pay, not the polish list.]</p></div>
        <div class="case__block kill"><h3 class="case__k">What I'd kill</h3><p>[The feature that was fun to build and earns nothing. Say why it survived as long as it did.]</p></div>
      </div>''',
         tinted=(i % 2 == 0))
    for i in (2, 3)) + "\n\n" + band(
    "Pattern", "Then", "The pattern", "The building is the easy half now.",
    '''      <h2 class="rev">Nine apps, and the <strong>same lesson each time</strong></h2>
      <p class="lede">Every one of these got built fast, with the same tools and the same speed you'd get. And in every one, the interesting decision was not what to add. It was what to leave out.</p>
      <p class="lede">That's the judgment you're hiring.</p>''')

ABOUT = '''<div class="doc">
  <section class="open">
    <div class="inner">
      <div class="margin"><b>About</b>The short version<em>Twenty years, and nine things that actually run.</em></div>
      <div>
        <h1><span class="rise"><span>Twenty years of deciding</span></span><span class="rise"><span>what to build, and</span></span><span class="rise"><span><strong>what to cut.</strong></span></span></h1>
        <p class="deck rev">That's the short version. Here's why it matters to you, which is the only reason it's worth reading.</p>
      </div>
    </div>
  </section>
</div>''' + "\n\n" + band(
    "Who", "One", "Who", "Long enough to have been wrong often enough.",
    '''      <h2 class="rev">Two decades in <strong>product and design</strong></h2>
      <p class="lede">Twenty plus years spent working out what a product should be, mostly by watching people fail to use things that looked great on a slide.</p>
      <p class="lede"><strong>What that means for you:</strong> when you describe your idea, you're talking to someone who has seen a lot of versions of it, including the ones that quietly didn't work and why.</p>''',
    tinted=True) + "\n\n" + band(
    "Why", "Two", "Why", "The gap between designed and real closed.",
    '''      <h2 class="rev">Why I <strong>work this way</strong></h2>
      <p class="lede">For most of those years there was a gap between "designed" and "real." A design could be right and still take months and a team before anyone found out. So a founder with an idea had exactly two options: pay a lot to find out, or don't find out.</p>
      <p class="lede">That gap closed. Building something real enough to test is now days, not quarters, and nine working apps in the last few months is what proved it to me rather than a claim someone made online.</p>
      <p class="lede"><strong>What that means for you:</strong> the reality check comes first, and it's cheap enough that hearing "no" is still a good day.</p>''') + "\n\n" + band(
    "Honesty", "Three", "Honesty", "It's structural, not a marketing line.",
    '''      <h2 class="rev">Why the honesty <strong>isn't a line</strong></h2>
      <p class="lede">If the money were in the build, "you should build this" would be the profitable answer to every question, and you'd never quite know whether you were hearing judgment or a quote.</p>
      <p class="lede">Here the value is the clarity. That makes "don't build this" a perfectly good outcome, and it's the only arrangement in which the advice is worth anything.</p>
      <p class="lede"><strong>What that means for you:</strong> you can take the answer at face value, including the one you didn't want.</p>''',
    tinted=True) + "\n\n" + band(
    "How", "Four", "How I work", "Small, scoped, real.",
    '''      <h2 class="rev">How I <strong>work</strong></h2>
      <ul class="probe">
        <li><strong>Small.</strong> One idea, one flow, one question at a time. Anything bigger is a way of avoiding the question.</li>
        <li><strong>Scoped.</strong> Fixed price, clean start and end. No hourly anything, no meter running, no scope quietly growing.</li>
        <li><strong>Real.</strong> Working software, not slides. People behave differently in front of a thing that works, and that difference is the whole point.</li>
        <li><strong>Honest about where the value stops.</strong> When the work grows past what one person should handle, you'll hear that, plus help handing it to the right team.</li>
      </ul>
      <p class="statement" id="statement" style="margin-top:44px">Not hundreds of clients. Twenty years and nine things that run.</p>''')


TAKEOVER = f'''<!-- Ships as an ordinary section at the foot of the page, and site.js promotes it
     to a dialog. The other way round -- hidden and role="dialog" in the markup -- meant
     that with scripting off the intake did not exist at all, and the button pointing at
     it jumped to nothing. -->
<div class="takeover" id="intake" aria-labelledby="takeover-title">
  <i class="intakeprog" id="intakeprog" aria-hidden="true"></i>
  <div class="takeover__top">
    <span class="name" aria-hidden="true">{MARK}<span>{WORDMARK}</span></span>
    <button class="exit" type="button" id="takeover-exit">Close<span aria-hidden="true">&times;</span></button>
  </div>
  <div class="takeover__body intakepage">
    <div class="form-status" id="form-status" tabindex="-1" role="status" aria-live="polite">
      <h3>Here it is. It&rsquo;s yours either way.</h3>
      <p>Nothing has been sent yet &mdash; this site has no server to send it to, and a
        form that says &ldquo;sent&rdquo; when it means &ldquo;discarded&rdquo; is worse than no form. Copy it
        or open it in your mail app, and it reaches me the moment you hit send. Keep a
        copy either way: the answers are more use to you than they are to me.</p>
      <label class="field__label" for="brief">Your brief</label>
      <textarea class="textarea" id="brief" rows="14" readonly></textarea>
      <div class="briefacts">
        <button class="act" type="button" id="brief-mail"><span>Open in your mail app</span></button>
        <button class="quiet" type="button" id="brief-copy">Copy it instead</button>
      </div>
    </div>
    <form class="intake" id="intake-form" novalidate>
      <ol class="intake__steps">
        <li class="qstep qstep--open" data-count="skip">
          <h2 class="qstep__q qstep__q--big" id="takeover-title">A few questions about your idea.</h2>
          <p class="lede">About ten minutes if you take your time. There are no right
            answers and none of this is a test &mdash; a rough answer is more use to me
            than a polished one.</p>
          <p class="lede">Only the idea and your email are needed. Skip anything you&rsquo;d
            rather say out loud. It saves as you go, so you can close this and come back.</p>
        </li>
        <li class="qstep" id="q-idea-step" data-q="1">
          <label class="field__label" for="q-idea">What's the idea? <span class="req" aria-hidden="true">*</span></label>
          <span class="field__hint">One or two sentences. Rough is fine &mdash; this is not a pitch.</span>
          <textarea class="textarea" id="q-idea" name="idea" required aria-describedby="q-idea-error" rows="3" placeholder="It&rsquo;s a&hellip;"></textarea>
          <p class="field__error" id="q-idea-error">A sentence is enough, but it needs to be a sentence.</p>
        </li>
        <li class="qstep" id="q-who-step" data-q="2">
          <label class="field__label" for="q-who">Who is it for, specifically? <span class="qstep__opt">Optional</span></label>
          <span class="field__hint">Not everyone. The narrower you can make this, the more useful the two weeks are.</span>
          <textarea class="textarea" id="q-who" name="who" rows="3" placeholder="It&rsquo;s for&hellip;"></textarea>
        </li>
        <li class="qstep" id="q-instead-step" data-q="3">
          <label class="field__label" for="q-instead">What do they do instead today? <span class="qstep__opt">Optional</span></label>
          <span class="field__hint">Whatever you&rsquo;d be replacing, even if it&rsquo;s a spreadsheet, a WhatsApp thread, or nothing.</span>
          <textarea class="textarea" id="q-instead" name="instead" rows="3" placeholder="Right now they&hellip;"></textarea>
        </li>
        <li class="qstep" id="q-true-step" data-q="4">
          <p class="qstep__frame">This is the one the two weeks gets built around.</p>
          <label class="field__label" for="q-true">What has to be true for this to work? <span class="qstep__opt">Optional</span></label>
          <span class="field__hint">The one thing that, if it turned out false, would make the rest pointless.</span>
          <textarea class="textarea" id="q-true" name="assumption" rows="3" placeholder="It only works if&hellip;"></textarea>
        </li>
        <li class="qstep" id="q-unsure-step" data-q="5">
          <label class="field__label" for="q-unsure">Which part are you least sure about? <span class="qstep__opt">Optional</span></label>
          <span class="field__hint">It&rsquo;s usually not the part that&rsquo;s hardest to build.</span>
          <textarea class="textarea" id="q-unsure" name="unsure" rows="3" placeholder="I&rsquo;m least sure that&hellip;"></textarea>
        </li>
        <li class="qstep" id="q-wrong-step" data-q="6">
          <label class="field__label" for="q-wrong">How would you know you were wrong? <span class="qstep__opt">Optional</span></label>
          <span class="field__hint">A number, a behaviour, anything you could actually watch happen.</span>
          <textarea class="textarea" id="q-wrong" name="wrong" rows="3" placeholder="I&rsquo;d know if&hellip;"></textarea>
        </li>
        <li class="qstep" id="q-no-step" data-q="7">
          <p class="qstep__frame">An honest answer here is worth more than a polite one.</p>
          <label class="field__label" for="q-no">What would you do if the answer came back no? <span class="qstep__opt">Optional</span></label>
          <textarea class="textarea" id="q-no" name="ifno" rows="3" placeholder="If it&rsquo;s a no, I&rsquo;d&hellip;"></textarea>
        </li>
        <li class="qstep" id="q-sitting-step" data-q="8">
          <label class="field__label" for="q-sitting">How long has this been sitting? <span class="qstep__opt">Optional</span></label>
          <span class="field__hint">A doc, a note, a conversation you keep having.</span>
          <textarea class="textarea" id="q-sitting" name="sitting" rows="3" placeholder="About&hellip;"></textarea>
        </li>
        <li class="qstep" id="q-pressure-step" data-q="9">
          <label class="field__label" for="q-pressure">What&rsquo;s the pressure? <span class="qstep__opt">Optional</span></label>
          <span class="field__hint">A date, a competitor, money running out, a person waiting on you. Or none.</span>
          <textarea class="textarea" id="q-pressure" name="pressure" rows="3" placeholder="The pressure is&hellip;"></textarea>
        </li>
        <li class="qstep" id="q-want-step" data-q="10">
          <fieldset class="qfield">
            <legend class="field__label">What do you want out of the two weeks? <span class="qstep__opt">Optional</span></legend>
            <label class="pick"><input type="radio" name="want" value="yes-no"><span>A straight yes or no</span></label>
            <label class="pick"><input type="radio" name="want" value="built"><span>Something built I can put in front of people</span></label>
            <label class="pick"><input type="radio" name="want" value="rule"><span>A rule I can trust for the next decision</span></label>
            <label class="pick"><input type="radio" name="want" value="unsure"><span>Not sure yet</span></label>
          </fieldset>
        </li>
        <li class="qstep" id="q-contact-step" data-q="11">
          <p class="qstep__frame">Last one.</p>
          <h2 class="qstep__q">Where should I send my reply?</h2>
          <p class="qstep__hint">I read every one of these myself. No scoring, no
            auto-reply, nothing in between.</p>
          <div class="field">
            <label class="field__label" for="name">Your name <span class="req" aria-hidden="true">*</span></label>
            <input class="input" type="text" id="name" name="name" autocomplete="name" required aria-describedby="name-error">
            <p class="field__error" id="name-error">Please add your name so I know who I&rsquo;m talking to.</p>
          </div>
          <div class="field">
            <label class="field__label" for="email">Email <span class="req" aria-hidden="true">*</span></label>
            <input class="input" type="email" id="email" name="email" autocomplete="email" inputmode="email" required aria-describedby="email-error">
            <p class="field__error" id="email-error">Please enter an email address I can reply to.</p>
          </div>
        </li>
      </ol>
      <p class="intake__kbd" hidden aria-hidden="true">Ctrl + Enter to continue</p>
      <div class="intake__bar" hidden>
        <button class="quiet intake__back" type="button">Back</button>
        <p class="intake__count" aria-live="polite"></p>
      </div>
      <button class="act" type="submit"><span>Send it over</span></button>
      <p class="fineprint">Your answers stay in this browser until you send them, and
        are used to reply to you about this call and nothing else. No list, no sequence.</p>
    </form>
  </div>
</div>'''

START = '''<div class="doc">
  <section class="open">
    <div class="inner">
      <div class="margin"><b>Start</b>Step one<em>Write it down. The call comes after, if there is one to have.</em></div>
      <div>
        <h1><span class="rise"><span>Tell me about</span></span><span class="rise"><span><strong>your idea.</strong></span></span></h1>
        <p class="deck rev">Eleven questions, one at a time. They are the ones I would
          ask you out loud, so writing them down first means the call &mdash; if we get
          that far &mdash; starts at the interesting part instead of at the beginning.</p>
      </div>
    </div>
  </section>

  <section class="band" id="n-what-happens" data-node="What happens">
    <div class="margin"><b>What happens</b>Three steps<em>You write, I read, we talk. Nothing automatic anywhere in it.</em></div>
    <div class="startgrid">
      <div class="rev">
        <h2>What happens <strong>after you send it</strong></h2>
        <ol class="checklist checklist--ord">
          <li><b>You answer the questions.</b> Ten minutes if you take your time, two if
            you don&rsquo;t. Only the idea and your email are needed &mdash; skip anything
            you would rather say out loud.</li>
          <li><b>I read them and reply within one working day.</b> Either with a couple of
            times for a call, or, if what you wrote already tells me this is not a fit,
            with that and a better direction. I read every one myself.</li>
          <li><b>The call, if there is a fit.</b> Free, 20 to 30 minutes, on video. We
            talk through what you wrote rather than starting from nothing. No pitch, no
            pressure, no follow-up sequence.</li>
        </ol>
        <p class="lede" style="margin-top:24px">The answers are yours to keep either way,
          and they are worth more to you than to me: they are the same questions the two
          weeks would start with.</p>
      </div>

      <div class="form-card rev">
        <p class="lede" style="margin-bottom:28px">One question at a time, nothing else on
          the screen, and it saves as you go &mdash; so you can close it and come back.</p>
        <a class="act act--block" href="#intake" id="intake-open"><span>Tell me about your idea</span>
          <span class="chip" aria-hidden="true">''' + ARROW + '''</span></a>
        <p class="fineprint">Or write to
          <a href="mailto:hello@oneflowfirst.com">hello@oneflowfirst.com</a> if you would
          rather just say hello. The questions are the faster route to a useful reply,
          not a gate in front of one.</p>
      </div>
    </div>
  </section>
</div>'''

# ────────────────────── worked case study (template) ──────────────────────
# Structure, order, and prose are the reusable part. The session counts and the
# two quotes are illustrative. Before this page goes public: replace those, drop
# the note in the hero margin, and remove robots=noindex from its PAGES entry.
#
# The three screens are line drawings standing in for screenshots. To use real
# ones, swap a screen(...) call for an <img>: .shot styles the figure, not the
# medium. No photograph is used anywhere on the site, on purpose.

S_TIMES = ('<text class="t" x="34" y="66">This week</text>'
           '<text class="s" x="34" y="90">Pick a time. That is the whole thing.</text>'
           '<text class="d" x="34" y="142">TUE 14</text>'
           '<rect class="pill" x="34" y="154" width="80" height="36" rx="18"/><text class="p" x="74" y="177">09:00</text>'
           '<rect class="pill" x="122" y="154" width="80" height="36" rx="18"/><text class="p" x="162" y="177">11:30</text>'
           '<rect class="pill" x="210" y="154" width="76" height="36" rx="18"/><text class="p" x="248" y="177">16:00</text>'
           '<text class="d" x="34" y="230">WED 15</text>'
           '<rect class="pill on" x="34" y="242" width="80" height="36" rx="18"/><text class="p" x="74" y="265">08:30</text>'
           '<rect class="pill" x="122" y="242" width="80" height="36" rx="18"/><text class="p" x="162" y="265">13:00</text>'
           '<text class="d" x="34" y="318">THU 16</text>'
           '<rect class="pill" x="34" y="330" width="80" height="36" rx="18"/><text class="p" x="74" y="353">10:00</text>'
           '<rect class="pill" x="122" y="330" width="80" height="36" rx="18"/><text class="p" x="162" y="353">15:30</text>'
           '<rect class="pill" x="210" y="330" width="76" height="36" rx="18"/><text class="p" x="248" y="353">17:00</text>'
           '<path class="rule" d="M34 406h252"/>'
           '<text class="s" x="34" y="436">Nothing else on this screen.</text>')

S_CONFIRM = ('<text class="t" x="34" y="66">Wednesday, 8:30</text>'
             '<text class="s" x="34" y="90">45 minutes. Same room as last time.</text>'
             '<rect class="card" x="34" y="120" width="252" height="120" rx="14"/>'
             '<path class="rule" d="M58 156h140M58 182h96M58 208h120"/>'
             '<rect class="btn" x="34" y="272" width="252" height="54" rx="14"/>'
             '<text class="btnt" x="160" y="305">Book it</text>'
             '<text class="s" x="34" y="360">No account. No card. No password.</text>')

S_REPLY = ('<circle class="ring" cx="160" cy="152" r="38"/>'
           '<path class="tick" d="M146 152l11 11 21-24"/>'
           '<text class="t mid" x="160" y="238">You are in.</text>'
           '<text class="s mid" x="160" y="266">Wednesday, 8:30.</text>'
           '<rect class="card" x="34" y="306" width="252" height="88" rx="14"/>'
           '<path class="rule" d="M58 340h150M58 366h104"/>'
           '<text class="s" x="34" y="430">This screen is where the idea broke.</text>')

CASE_SHOTS = (
    shot("Pick a time. Three days, a handful of slots, nothing else competing for attention.",
         "The times screen: three days, each offering a few bookable slots", S_TIMES) + "\n" +
    shot("Confirm. No account, no card, no password, because none of those were the question.",
         "The confirm screen: the chosen appointment and a single button", S_CONFIRM) + "\n" +
    shot("Confirmed. Seven of ten people read this screen and went to message anyway.",
         "The confirmation screen: a tick, the appointment, and a quiet receipt", S_REPLY))

CASE = '''<div class="doc">
  <section class="open">
    <div class="inner">
      <div class="margin"><b>Case study</b>Slate<em>A worked example. Numbers and quotes are illustrative until a real one lands.</em></div>
      <div>
        <h1><span class="rise"><span>Booking was never</span></span><span class="rise"><span><strong>the problem.</strong></span></span></h1>
        <p class="deck rev">Slate was going to be a booking page for independent physios. Ten sessions said the calendar was the easy part, and the thing people wanted was a reply. Here is the whole trail, including what got killed.</p>
      </div>
    </div>
  </section>
</div>''' + "\n\n" + band(
    "The idea", "One", "The idea", "A clear brief is still a guess about which part hurts.",
    '''      <h2 class="rev">The idea, <strong>in one line</strong></h2>
      <p class="lede">A booking tool for independent physios who currently run everything through WhatsApp.</p>
      <p class="lede">The physio who described it had around sixty regulars, a phone that never stopped, and a Sunday evening spent copying appointments into a paper diary. She wanted what the big clinics have: a booking page, a calendar, confirmations that send themselves.</p>
      <p class="lede">That is a clear brief. It is also a guess about which part hurts.</p>
      <p class="lede">One thing worth saying up front: Slate is one of my own nine apps, not a client engagement. The regulars were already reachable, so the sessions ran the same week the build finished. On someone else's idea that is the part you cannot count on, which is why testing sits outside the two weeks and can be added on.</p>''',
    tinted=True) + "\n\n" + band(
    "The bet", "Two", "The risky part", "The exciting part and the risky part are rarely the same part.",
    '''      <h2 class="statement" id="statement" data-key="book themselves">People would rather book themselves than ask.</h2>
      <p class="lede rev">The exciting part was the calendar. The risky part was six words further down the brief: "so she stops answering messages." Everything else depended on sixty regulars choosing a form over a thread, and nobody had ever asked them to.</p>
      <p class="lede rev">Three things were ruled out as not the risk, on purpose:</p>
      <ul class="probe">
        <li><strong>Taking payment.</strong> Everyone already paid in the room. Adding cards would have tested a problem nobody had.</li>
        <li><strong>More than one practitioner.</strong> A real constraint one day, an excuse to build a calendar system now.</li>
        <li><strong>Insurance codes.</strong> Fiddly, visible, and irrelevant to whether anyone books at all.</li>
      </ul>''') + "\n\n" + band(
    "The rule", "Three", "The decision rule", "Written on day two, while the idea was still flattering.",
    '''      <h2 class="rev">Agreed <strong>before any testing</strong></h2>
      <p class="lede">Three sentences, written down before there was anything to look at, so the bar could not move later.</p>
      <div class="verdicts">
        <div class="verdict go rev"><p class="k">Go</p><p>Six of ten regulars book their next appointment through the page unaided, and nobody messages afterwards to check it worked.</p></div>
        <div class="verdict adjust rev"><p class="k">Adjust</p><p>They book, then message anyway. The booking works and something else is missing.</p></div>
        <div class="verdict stop rev"><p class="k">Stop</p><p>They open the page, close it, and go back to WhatsApp. Booking was never the friction.</p></div>
      </div>''',
    tinted=True) + "\n\n" + band(
    "The flow", "Four", "The one flow", "Three screens. Everything else deliberately absent.",
    '''      <h2 class="rev">One flow, <strong>made real</strong></h2>
      <p class="lede">See this week, pick a time, done. Usable on a phone, in ninety seconds, by someone standing in a hallway.</p>
      <div class="shots">
''' + CASE_SHOTS + '''
      </div>
      <p class="lede rev" style="margin-top:36px"><strong>What got left out on purpose:</strong></p>
      <ul class="probe">
        <li><strong>Accounts and passwords.</strong> A first name and a phone number identify a regular well enough for two weeks.</li>
        <li><strong>The practice-side calendar.</strong> A spreadsheet did that job behind the scenes. Nobody was testing the spreadsheet.</li>
        <li><strong>Cancellation rules, reminders, profiles, a policy page.</strong> All real one day. None of them the question.</li>
      </ul>''') + "\n\n" + band(
    "The evidence", "Five", "What testing showed", "What people did, not what they said they would do.",
    '''      <h2 class="rev">What ten sessions <strong>showed</strong></h2>
      <div class="stats rev">
        <div class="stat"><b>10</b><span>Regulars, recruited from the practice's own list.</span></div>
        <div class="stat"><b>9</b><span>Booked unaided, most of them in under a minute.</span></div>
        <div class="stat"><b>7</b><span>Sent a message anyway, right after booking.</span></div>
      </div>
      <p class="lede rev" style="margin-top:36px">Nine out of ten cleared the bar the tool was built to clear. Then seven of them opened WhatsApp and typed the thing the tool had just made unnecessary.</p>
      <div class="quotes">
        <blockquote class="quote rev">
          <p>"I've booked it, but can you just confirm you got it?"</p>
          <footer>Sent about forty seconds after a successful booking. Session four.</footer>
        </blockquote>
        <blockquote class="quote rev">
          <p>"I don't mind messaging her. I mind not knowing if she's seen it."</p>
          <footer>Asked why she messaged after the confirmation screen. Session seven.</footer>
        </blockquote>
      </div>
      <p class="lede rev" style="margin-top:32px">Booking was never the friction. Waiting was. The confirmation screen said the appointment existed. It did not say a person knew about it, and that is the reassurance people were actually chasing.</p>''',
    tinted=True) + "\n\n" + band(
    "The call", "Six", "The call", "Measured against the rule, not against the mood in the room.",
    '''      <h2 class="rev">The call: <strong>adjust</strong></h2>
      <p class="lede">The rule said go only if nobody messaged afterwards. Seven did. So this is an adjust, and the flat version of that is worth more than a generous one.</p>
      <div class="verdicts">
        <div class="verdict adjust rev"><p class="k">Adjust</p><p>The problem is real and the shape is wrong. This is not a booking system with reminders bolted on. It is a confirmation system that happens to take bookings.</p></div>
      </div>
      <p class="lede rev" style="margin-top:32px">The change is one sentence: lead with the reply, not the calendar. A regular should get a message from a person, in the thread they already use, and the booking page should be the quiet mechanism underneath it rather than the thing being sold. The same two weeks can run again on that version, against a new bar.</p>''') + "\n\n" + band(
    "The cuts", "Seven", "What I would kill", "The change and the kill are the reason any of this is written down.",
    '''      <h2 class="rev">What I would <strong>change and kill</strong></h2>
      <div class="case rev">
        <div class="case__block"><h3 class="case__k">What the two weeks bought</h3><p>A named change instead of a hunch, for the price of ten conversations and one flow. The version that would have shipped without this was a well-built calendar for a problem that was never about calendars.</p></div>
        <div class="case__block change"><h3 class="case__k">What I would change if this were a paid product</h3><p>Make the confirmation the product. The reply lands in WhatsApp, from the practice, within seconds. The booking page becomes the mechanism underneath it instead of the thing on the poster.</p></div>
        <div class="case__block kill"><h3 class="case__k">What I would kill</h3><p>The week view. It took four days and two of the ten people used it. Everyone else took the first sensible slot they were offered. It survived that long because it looks like the thing a booking tool is supposed to have, which is the worst reason for anything to exist.</p></div>
      </div>''',
    tinted=True) + "\n\n" + band(
    "The two weeks", "Eight", "How it ran", "Fixed scope, and most of it spent not building.",
    '''      <h2 class="rev">Where the <strong>two weeks went</strong></h2>
      <div class="stairs">
        <div class="stair rev"><p class="k">Days one and two</p><h3>Find the risky part</h3><p>The brief said calendar. The questions said reassurance. The decision rule got written before there was anything to look at.</p></div>
        <div class="stair rev"><p class="k">Days three to eight</p><h3>Build one flow</h3><p>Three screens, real times, no accounts. Four of those days went into a week view that later got cut, which is the tuition.</p></div>
        <div class="stair rev"><p class="k">Days nine to twelve</p><h3>Ten sessions, then the call</h3><p>Ten regulars, one flow, no coaching. Fast only because the list was already mine. The call written against the rule, with the evidence underneath it.</p></div>
      </div>
      <p class="rev" style="margin-top:36px"><a class="quiet" href="what-ive-built.html">See the other apps ''' + ARROW + '''</a></p>''')

# The overlay is appended rather than interpolated. START is assembled from three
# concatenated literals because ARROW sits in the middle of it, and only the first of
# those was an f-string, so a {TAKEOVER} written inline landed in whichever segment
# happened to be scanned -- which is how it ended up inside HOME_HERO instead.
# The overlay is emitted by shell() on every page now: the closing button opens
# it in place, so no page has to route through start.html to ask the questions.

PAGES = [
    ("index.html", "Is your idea worth building? | One flow first",
     "In two weeks you own the one part that matters most, built for real, and a bar agreed before anyone sees it. Then real people tell you whether it holds.",
     HOME, "Let's find out if your idea is <strong>real</strong>",
     "Ten minutes of questions, in your own words. Then a straight read on whether this "
     "fits, from a person who read them. No pitch, no pressure, and the answers are "
     "yours to keep either way."),
    ("how-it-works.html", "How it works | One flow first",
     "Exactly what happens across the two weeks: the qualifying questions, the decision rule, the build, the brief, the playbook, and what comes after.",
     HOWITWORKS, "Ready to <strong>find out?</strong>",
     "Ten minutes of questions, in your own words, then a straight read on whether this "
     "fits. The answers are yours to keep either way."),
    ("what-ive-built.html", "What I've built | One flow first",
     "Real apps, built for real ideas. The thinking behind them, including what I'd change and what I'd kill.",
     BUILT, "Let's find out if your idea is <strong>real</strong>",
     "Ten minutes of questions, in your own words, then a straight read on whether this "
     "fits. The answers are yours to keep either way."),
    ("case-slate.html", "Slate: booking was never the problem | One flow first",
     "A worked two-week case study. The bet, the decision rule agreed in advance, one flow built for real, ten test sessions, and the call: adjust, not go.",
     CASE, "Got an idea with a <strong>risky part?</strong>",
     "Ten minutes of questions about the risky part, then a straight read on whether this "
     "fits. The answers are yours to keep either way.",
     {"nav_slug": "what-ive-built.html", "robots": "noindex"}),
    ("about.html", "About | One flow first",
     "Twenty years of deciding what to build and what to cut, and why the work is scoped, small, and honest about where the value stops.",
     ABOUT, "Let's find out if your idea is <strong>real</strong>",
     "Ten minutes of questions, in your own words, then a straight read on whether this "
     "fits. The answers are yours to keep either way."),
    ("start.html", "Let's talk about your idea | One flow first",
     "A free 20 to 30 minute call. You share the idea, you hear honestly whether this fits and what step one would look like for you.",
     START, "Prefer <strong>email?</strong>",
     "Write to hello@oneflowfirst.com with the same one line about your idea."),
]

for page in PAGES:
    slug, title, desc, body, ch, cb = page[:6]
    opts = page[6] if len(page) > 6 else {}
    # encoding is not optional. write_text without it uses the platform's locale
    # codepage, which on Windows is cp1252, and every page declares utf-8. It went
    # unnoticed for as long as the pages happened to be pure ASCII; the first
    # ellipsis in a placeholder came out as a single 0x97 byte and rendered as a
    # question mark in the browser.
    pathlib.Path(slug).write_text(
        shell(slug, title, desc, body, ch, cb, **opts), encoding='utf-8')
    print("wrote", slug)
