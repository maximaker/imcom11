#!/usr/bin/env python3
"""Builds the five pages from one shell so the chrome can never drift apart."""
import pathlib

NAV = [("how-it-works.html", "How it works"),
       ("what-ive-built.html", "What I've built"),
       ("about.html", "About"),
       ("start.html", "Start")]

ARROW = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
         '<path d="M5 12h13m0 0l-5.5-5.5M18 12l-5.5 5.5" stroke="currentColor" '
         'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

NOTCH = ('<div class="notch" aria-hidden="true"><i><svg viewBox="0 0 24 24" fill="none">'
         '<path d="M12 5v13m0 0l-5-5m5 5l5-5" stroke="currentColor" stroke-width="1.8" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg></i></div>')


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


def band(node, label, title, note, body, tinted=False, extra_class=""):
    """Every band carries its own wrappers, so blocks never depend on order."""
    inner = (f'    <section class="band {extra_class}" data-node="{node}">\n'
             f'      {margin(label, title, note)}\n'
             f'      <div>\n{body}\n      </div>\n'
             f'    </section>')
    if tinted:
        return (f'{NOTCH}\n<div class="tinted">\n  <div class="doc">\n'
                f'{inner}\n  </div>\n</div>')
    return f'<div class="doc">\n{inner}\n</div>'

def hero(margin_html, h1, deck, extra=""):
    return (f'<div class="doc">\n  <section class="open">\n    <div class="inner">\n'
            f'      {margin_html}\n      <div>\n        {h1}\n'
            f'        <p class="deck rev">{deck}</p>\n{extra}      </div>\n'
            f'    </div>\n  </section>\n</div>')


def shell(slug, title, desc, body, close_heading, close_body,
          nav_slug=None, robots=None):
    """nav_slug lets a child page mark its parent as current. robots is for
    pages that should stay out of search, such as the case study template."""
    here = nav_slug or slug
    robots = f'<meta name="robots" content="{robots}">\n' if robots else ''
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
{robots}<meta name="theme-color" content="#FEF6F0">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="stylesheet" href="assets/css/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23CC5500'/><path d='M8 17.5l5 5L24 10' stroke='%23FEF6F0' stroke-width='3' fill='none' stroke-linecap='round' stroke-linejoin='round'/></svg>">
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>

<div class="surface" aria-hidden="true"></div>

<div class="spine">
  <div class="track" aria-hidden="true"></div><div class="fill" id="spinefill" aria-hidden="true"></div>
  <div class="cap cap--top">
    <a class="railmark" href="index.html">one flow<em>.</em>first</a>
  </div>
</div>

<header class="top" id="top">
  <a class="name" href="index.html">one flow<em>.</em>first</a>
  <button class="navtoggle" type="button" aria-expanded="false" aria-controls="nav" aria-label="Open menu">
    <span aria-hidden="true"></span><span aria-hidden="true"></span>
  </button>
  <nav id="nav" aria-label="Primary">
      {nav}
  </nav>
</header>

<main id="main">
{body}

  <div class="doc">
  <section class="close rev" data-node="Start">
    <div class="margin"><b>Next</b>One call<em>Twenty minutes. It sorts out fit either way.</em></div>
    <div>
      <h2>{close_heading}</h2>
      <p class="lede" style="margin-bottom:32px">{close_body}</p>
      <a class="act" href="start.html" id="cta"><span>Book a free intro call</span>
        <span class="chip" aria-hidden="true">{ARROW}</span></a>
    </div>
  </section>

  </div>

  <div class="doc">
  <div class="railfoot">
    <a class="railcta" href="start.html">
      <span class="lbl">Book a free intro call</span>
      {ARROW}
    </a>
  </div>
  </div>
</main>

<footer class="colo">
  <span>&copy; 2026 One flow first</span>
  <span><a href="mailto:hello@oneflowfirst.com">hello@oneflowfirst.com</a></span>
</footer>

<script src="assets/js/site.js" defer></script>
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
      <div class="margin"><b>The offer</b>Two weeks<em>Fixed scope. Fixed price. One decision at the end.</em></div>
      <div>
        <h1>
          <span class="rise"><span>Know whether your idea</span></span>
          <span class="rise"><span><strong>is worth building,</strong></span></span>
          <span class="rise"><span>before you spend</span></span>
          <span class="rise"><span>months finding out.</span></span>
        </h1>
        <p class="deck rev">In two weeks you own <b>a working version of the one part that matters most</b>, evidence from real users, and a straight answer: keep going, or stop.</p>

        <p class="principle rev">One flow first. <span>Nothing else yet.</span></p>

        <p class="hero-cta rev"><a class="act" href="start.html"><span>Tell me about your idea</span>
          <span class="chip" aria-hidden="true">''' + ARROW + '''</span></a></p>
        <p class="act-note rev">Twenty minutes. You'll get a straight read on whether this fits, either way.</p>

        <div class="stats rev">
          <div class="stat"><b>20 years</b><span>Deciding what to build, and what to cut.</span></div>
          <div class="stat"><b>9 apps</b><span>Built and shipped in the last few months.</span></div>
          <div class="stat"><b>2 weeks</b><span>From an idea in a doc to a straight answer.</span></div>
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
          <span data-i="2"><b>Worth testing</b><i>Few enough to put in front of real people in two weeks.</i></span>
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
      <p class="lede">That instinct is right. Most ideas don't fail because nobody could build them. They fail because someone spent months and a pile of money before finding out that nobody wanted the thing that got built.</p>''',
    tinted=True) + "\n\n" + band(
    "Doubts", "Two", "Said out loud", "The three things people think and rarely say.",
    '''      <h2 class="rev">You might be <strong>thinking</strong></h2>
      <div class="doubts">
        <div class="doubt rev"><p class="q">"What if it's a bad idea and I find out too late."</p><p class="a">You find out first, before anything gets built.</p></div>
        <div class="doubt rev"><p class="q">"I'm not technical. I won't understand what's happening."</p><p class="a">You don't need to be. You'll get it explained clearly enough to decide with confidence.</p></div>
        <div class="doubt rev"><p class="q">"I don't want to be talked into a build I don't need."</p><p class="a">You won't be. You'll get an honest answer even when the honest answer is no.</p></div>
      </div>''') + "\n\n" + band(
    "After", "Three", "After", "The difference between hoping and knowing.",
    '''      <h2 class="rev">In two weeks, you go from <strong>guessing to knowing</strong></h2>
      <p class="lede">Instead of a doc full of hope and a knot in your stomach, you have something real in your hands and evidence about whether it works.</p>
      <p class="lede">You can walk into a room and show it, not describe it. You can point at what real people did with it, not at what you hope they'd do. And you can make the next call, spend or stop, with your eyes open.</p>
      <p class="lede">If it's a go, you know exactly what to build next. If it's a stop, you kept your money and a year of your life.</p>''',
    tinted=True) + "\n\n" + band(
    "Method", "Four", "Method", "Three steps. The first one can end the project, cheaply.",
    '''      <h2 class="rev">Three steps, <strong>start to answer</strong></h2>
      <div class="steps">
        <div class="step"><span class="n">Step one</span><h3>Find out if it's worth building.</h3><p>You bring the idea. Together you find the one thing that has to be true for it to work, and you get a straight call. If there's a fatal flaw, you find it here, cheaply, before anything gets built.</p></div>
        <div class="step"><span class="n">Step two</span><h3>Get a real version of the part that matters.</h3><p>One working flow that real people can actually use. Not a mockup. Something you can put in front of users.</p></div>
        <div class="step"><span class="n">Step three</span><h3>Test it and decide, with a clear rule.</h3><p>Before testing, you agree what result means go, what means adjust, what means stop. Then you decide with evidence instead of a gut feeling.</p></div>
      </div>
      <p class="rev" style="margin-top:34px"><a class="quiet" href="how-it-works.html">See how it works in detail ''' + ARROW + '''</a></p>''') + "\n\n" + band(
    "Deliverables", "Five", "Deliverables", "Named things. Yours to keep, extend, or hand to any team.",
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
            <span class="sm">The riskiest assumption, what the testing showed, and a straight call.</span>
            <span class="sign" aria-hidden="true"></span>
          </button>
          <div class="more" id="a2"><div><p>Short enough to read in one sitting and written so a co-founder or an investor can read it too. It states the call first, then the evidence behind it. If the two ever disagree, trust the evidence.</p></div></div>
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
      <p class="lede rev" style="margin-top:26px">That last one matters more than it looks. It's the part that keeps working long after the two weeks end.</p>''',
    tinted=True) + "\n\n" + band(
    "Terms", "Six", "Terms", "The unusual promise.",
    '''      <p class="statement" id="statement" data-key="never stuck with me.">You should never be stuck with me.</p>
      <p class="lede rev">Plenty of people in this business are quietly hoping you'll stay. This works the other way round. When the two weeks end, you can read your own evidence, make your own call, and move forward or walk away without another opinion. You keep the build, the brief, and the method.</p>
      <p class="lede rev">People do come back. Usually with the next idea, or the same one pointed somewhere new. That's a choice, not a dependency, and it's the only kind worth having.</p>''') + "\n\n" + band(
    "Trust", "Seven", "Why trust it", "Competence, stated as what you get.",
    '''      <h2 class="rev">Why you can <strong>trust the answer</strong></h2>
      <div class="grid3">
        <div class="rev"><h3>You get judgment, not just a build.</h3><p>Anyone can generate an app now. The hard part is knowing what to make and what to cut, and that's the part you're paying for.</p></div>
        <div class="rev"><h3>You get advice from someone who isn't paid to say yes.</h3><p>When the honest answer is "don't build this," you'll hear it. That's only possible because the value here is the clarity, not the code.</p></div>
        <div class="rev"><h3>You get speed without losing the thinking.</h3><p>The idea gets real in days, with a designer's read on how people actually behave built in.</p></div>
      </div>
      <p class="lede rev" style="margin-top:30px">The judgment comes from 20 years of deciding what to build and what to cut. The speed comes from nine working apps built in the last few months. If you want that story, it's on the <a href="about.html">about page</a>.</p>''',
    tinted=True) + "\n\n" + band(
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
      <p class="rev" style="margin-top:34px"><a class="quiet" href="what-ive-built.html">See the full thinking behind them ''' + ARROW + '''</a></p>''') + "\n\n" + band(
    "Fit", "Nine", "Fit", "A quick call sorts it out in twenty minutes.",
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
    "Pricing", "Ten", "Pricing", "You'll see the whole staircase before you take the first step.",
    '''      <h2 class="rev">How <strong>pricing works</strong></h2>
      <div class="stairs">
        <div class="stair rev"><p class="k">Step one</p><h3>Is this worth building?</h3><p>A small fixed price, set so it's worth it even when the answer is "don't build."</p></div>
        <div class="stair rev"><p class="k">Step two</p><h3>The build</h3><p>Scoped after step one, once you both know what's actually needed. No surprise numbers, no big commitment before you have proof.</p></div>
        <div class="stair rev"><p class="k">Optional</p><h3>Testing, done for you</h3><p>Prefer not to run the testing yourself? That can be added on.</p></div>
      </div>''',
    tinted=True) + "\n\n" + band(
    "Questions", "Eleven", "Questions", "The ones that actually get asked.",
    '''      <h2 class="rev">Questions <strong>people ask</strong></h2>
      <div class="faq rev">
        <details><summary>What if you tell me my idea is bad?<i aria-hidden="true"></i></summary><div><p>Then you've saved months and a fortune, and you'll get a clear reason why, not a vague no.</p></div></details>
        <details><summary>Do I need to understand the tech?<i aria-hidden="true"></i></summary><div><p>No. You need to understand your customer. The rest is handled.</p></div></details>
        <details><summary>Who owns what gets built?<i aria-hidden="true"></i></summary><div><p>You do. It's yours to take anywhere.</p></div></details>
        <details><summary>Is this a full product?<i aria-hidden="true"></i></summary><div><p>No, and that's the point. It's the smallest real thing that answers the biggest question. Building the full product before that answer is exactly the expensive mistake this avoids.</p></div></details>
        <details><summary>What if I already know it's a good idea?<i aria-hidden="true"></i></summary><div><p>Then step one is quick and you'll have saved nothing but a little time. Most people who are certain turn out to be certain about the wrong part.</p></div></details>
      </div>''')

HOWITWORKS = '''<div class="doc">
  <section class="open">
    <div class="inner">
      <div class="margin"><b>How it works</b>The full process<em>Written from your side, not mine.</em></div>
      <div>
        <h1><span class="rise"><span>Here's exactly what</span></span><span class="rise"><span><strong>happens.</strong></span></span></h1>
        <p class="deck rev">Two weeks, two steps, one decision at the end. No surprises for you.</p>
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
        <li><strong>What the testing showed.</strong> What people did, not what they said they'd do, with the moments that mattered called out.</li>
        <li><strong>The call.</strong> Go, adjust, or stop, measured against the rule you set in advance.</li>
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
      <p class="lede" style="margin-top:24px">It's included as guidance you can run yourself. If you'd rather not, the testing can be done for you as an add-on.</p>''',
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
        <div class="case__block"><h4>The problem it solves</h4><p>Around sixty regulars, a phone that never stopped, and a Sunday evening spent copying appointments into a paper diary. The alternative was answering the same message forty times a week.</p></div>
        <div class="case__block change"><h4>What I'd change if this were a paid product</h4><p>Make the confirmation the product. Nine of ten people booked unaided, and seven then messaged to check it had worked. The reply is the thing they wanted; the calendar was scaffolding.</p></div>
        <div class="case__block kill"><h4>What I'd kill</h4><p>The week view. Four days of work, used by two of ten people. It survived because it looks like the thing a booking tool is supposed to have.</p></div>
      </div>
      <p class="rev" style="margin-top:32px"><a class="quiet" href="case-slate.html">Read the full case note ''' + ARROW + '''</a></p>''',
    tinted=True) + "\n\n" + "\n\n".join(
    band(f"App {i:02d}", f"App {i:02d}", "[App name]", "[One line you'd say to a friend.]",
         f'''      <h2 class="rev">[App name]</h2>
      <p class="lede">[One line: what it is, said the way you'd say it to a friend.]</p>
      <div class="case rev">
        <div class="case__block"><h4>The problem it solves</h4><p>[Who had the problem, what it cost them, and what they were doing instead before this existed.]</p></div>
        <div class="case__block change"><h4>What I'd change if this were a paid product</h4><p>[The one structural change that would make people pay, not the polish list.]</p></div>
        <div class="case__block kill"><h4>What I'd kill</h4><p>[The feature that was fun to build and earns nothing. Say why it survived as long as it did.]</p></div>
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

START = '''<div class="doc">
  <section class="open">
    <div class="inner">
      <div class="margin"><b>Start</b>One call<em>Free, 20 to 30 minutes, on a video call.</em></div>
      <div>
        <h1><span class="rise"><span>Let's talk about</span></span><span class="rise"><span><strong>your idea.</strong></span></span></h1>
        <p class="deck rev">You share the idea. You hear honestly whether this fits, and what step one would look like for you specifically.</p>
      </div>
    </div>
  </section>

  <section class="band" data-node="The call">
    <div class="margin"><b>The call</b>What it is<em>No pitch, no pressure, no follow-up sequence.</em></div>
    <div class="startgrid">
      <div class="rev">
        <h2>What the <strong>call is</strong></h2>
        <ul class="checklist">
          <li>Free, 20 to 30 minutes, on a video call.</li>
          <li>You talk through the idea. No deck needed, a rough version is fine.</li>
          <li>You leave knowing whether this fits and what step one would cost.</li>
          <li>No pitch, no pressure, no follow-up sequence.</li>
        </ul>
        <p class="lede" style="margin-top:24px">If it's not a fit, you'll hear that too, and get pointed somewhere better.</p>
      </div>

      <div class="form-card rev">
        <div class="form-status" id="form-status" tabindex="-1" role="status" aria-live="polite">
          <div>
            <h3>That's in. Talk soon.</h3>
            <p>You'll get a reply within one working day with a couple of times to pick from. If the idea line tells me straight away that this isn't a fit, you'll hear that instead, along with a better direction.</p>
          </div>
        </div>
        <form id="intro-form" novalidate>
          <div class="field">
            <label class="field__label" for="name">Your name <span class="req" aria-hidden="true">*</span></label>
            <input class="input" type="text" id="name" name="name" autocomplete="name" required aria-describedby="name-error">
            <p class="field__error" id="name-error">Please add your name so I know who I'm talking to.</p>
          </div>
          <div class="field">
            <label class="field__label" for="email">Email <span class="req" aria-hidden="true">*</span></label>
            <input class="input" type="email" id="email" name="email" autocomplete="email" inputmode="email" required aria-describedby="email-error">
            <p class="field__error" id="email-error">Please enter an email address I can reply to.</p>
          </div>
          <div class="field">
            <label class="field__label" for="idea">Your idea, in one line <span class="req" aria-hidden="true">*</span></label>
            <span class="field__hint">Who it's for and what it does for them. Rough is fine.</span>
            <textarea class="textarea" id="idea" name="idea" required minlength="12" aria-describedby="idea-error" placeholder="A booking tool for independent physios who currently run everything through WhatsApp."></textarea>
            <p class="field__error" id="idea-error">A sentence is enough, but it needs to be a sentence.</p>
          </div>
          <button class="act act--block" type="submit"><span>Send it over</span></button>
          <p class="fineprint">Your details are used to reply to you about this call and nothing else. No list, no sequence.</p>
        </form>
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
      <p class="lede">That is a clear brief. It is also a guess about which part hurts.</p>''',
    tinted=True) + "\n\n" + band(
    "The bet", "Two", "The risky part", "The exciting part and the risky part are rarely the same part.",
    '''      <p class="statement" id="statement" data-key="book themselves">People would rather book themselves than ask.</p>
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
        <div class="case__block"><h4>What the two weeks bought</h4><p>A named change instead of a hunch, for the price of ten conversations and one flow. The version that would have shipped without this was a well-built calendar for a problem that was never about calendars.</p></div>
        <div class="case__block change"><h4>What I would change if this were a paid product</h4><p>Make the confirmation the product. The reply lands in WhatsApp, from the practice, within seconds. The booking page becomes the mechanism underneath it instead of the thing on the poster.</p></div>
        <div class="case__block kill"><h4>What I would kill</h4><p>The week view. It took four days and two of the ten people used it. Everyone else took the first sensible slot they were offered. It survived that long because it looks like the thing a booking tool is supposed to have, which is the worst reason for anything to exist.</p></div>
      </div>''',
    tinted=True) + "\n\n" + band(
    "The two weeks", "Eight", "How it ran", "Fixed scope, and most of it spent not building.",
    '''      <h2 class="rev">Where the <strong>two weeks went</strong></h2>
      <div class="stairs">
        <div class="stair rev"><p class="k">Days one and two</p><h3>Find the risky part</h3><p>The brief said calendar. The questions said reassurance. The decision rule got written before there was anything to look at.</p></div>
        <div class="stair rev"><p class="k">Days three to eight</p><h3>Build one flow</h3><p>Three screens, real times, no accounts. Four of those days went into a week view that later got cut, which is the tuition.</p></div>
        <div class="stair rev"><p class="k">Days nine to twelve</p><h3>Ten sessions, then the brief</h3><p>Ten regulars, one flow, no coaching. The call written against the rule, with the evidence underneath it.</p></div>
      </div>
      <p class="rev" style="margin-top:36px"><a class="quiet" href="what-ive-built.html">See the other apps ''' + ARROW + '''</a></p>''')

PAGES = [
    ("index.html", "Know whether your idea is worth building | One flow first",
     "In two weeks you own a working version of the one part that matters most, evidence from real users, and a straight answer: keep going, or stop.",
     HOME, "Let's find out if your idea is <strong>real</strong>",
     "One call. You talk through your idea, you hear honestly whether this fits. No pitch, no pressure."),
    ("how-it-works.html", "How it works | One flow first",
     "Exactly what happens across the two weeks: the qualifying questions, the decision rule, the build, the brief, the playbook, and what comes after.",
     HOWITWORKS, "Ready to <strong>find out?</strong>",
     "One call. You talk through your idea, you hear honestly whether this fits."),
    ("what-ive-built.html", "What I've built | One flow first",
     "Real apps, built for real ideas. The thinking behind them, including what I'd change and what I'd kill.",
     BUILT, "Let's find out if your idea is <strong>real</strong>",
     "One call. You talk through your idea, you hear honestly whether this fits."),
    ("case-slate.html", "Slate: booking was never the problem | One flow first",
     "A worked two-week case study. The bet, the decision rule agreed in advance, one flow built for real, ten test sessions, and the call: adjust, not go.",
     CASE, "Got an idea with a <strong>risky part?</strong>",
     "One call. You talk through the idea, you hear honestly whether this fits.",
     {"nav_slug": "what-ive-built.html", "robots": "noindex"}),
    ("about.html", "About | One flow first",
     "Twenty years of deciding what to build and what to cut, and why the work is scoped, small, and honest about where the value stops.",
     ABOUT, "Let's find out if your idea is <strong>real</strong>",
     "One call. You talk through your idea, you hear honestly whether this fits."),
    ("start.html", "Let's talk about your idea | One flow first",
     "A free 20 to 30 minute call. You share the idea, you hear honestly whether this fits and what step one would look like for you.",
     START, "Prefer <strong>email?</strong>",
     "Write to hello@oneflowfirst.com with the same one line about your idea."),
]

for page in PAGES:
    slug, title, desc, body, ch, cb = page[:6]
    opts = page[6] if len(page) > 6 else {}
    pathlib.Path(slug).write_text(shell(slug, title, desc, body, ch, cb, **opts))
    print("wrote", slug)
