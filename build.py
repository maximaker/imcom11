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


def shell(slug, title, desc, body, close_heading, close_body):
    nav = "\n      ".join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == slug else ""}>{t}</a>'
        for h, t in NAV)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#FEF6F0">
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
    '''      <p class="statement" id="statement">You should never be stuck with me.</p>
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
          <h3>[APP NAME 1]</h3>
          <p>[ONE LINE]</p>
          <p class="kill"><b>What I'd kill</b>[WHAT I'D KILL]</p>
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
        <p class="deck rev">Here's the thinking behind them, not just the screenshots. The change and kill notes are the point.</p>
      </div>
    </div>
  </section>
</div>''' + "\n\n" + "\n\n".join(
    band(f"App {i:02d}", f"App {i:02d}", "[App name]", "[One line you'd say to a friend.]",
         f'''      <h2 class="rev">[App name]</h2>
      <p class="lede">[One line: what it is, said the way you'd say it to a friend.]</p>
      <div class="case rev">
        <div class="case__block"><h4>The problem it solves</h4><p>[Who had the problem, what it cost them, and what they were doing instead before this existed.]</p></div>
        <div class="case__block change"><h4>What I'd change if this were a paid product</h4><p>[The one structural change that would make people pay, not the polish list.]</p></div>
        <div class="case__block kill"><h4>What I'd kill</h4><p>[The feature that was fun to build and earns nothing. Say why it survived as long as it did.]</p></div>
      </div>''',
         tinted=(i % 2 == 1))
    for i in (1, 2, 3)) + "\n\n" + band(
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
    ("about.html", "About | One flow first",
     "Twenty years of deciding what to build and what to cut, and why the work is scoped, small, and honest about where the value stops.",
     ABOUT, "Let's find out if your idea is <strong>real</strong>",
     "One call. You talk through your idea, you hear honestly whether this fits."),
    ("start.html", "Let's talk about your idea | One flow first",
     "A free 20 to 30 minute call. You share the idea, you hear honestly whether this fits and what step one would look like for you.",
     START, "Prefer <strong>email?</strong>",
     "Write to hello@oneflowfirst.com with the same one line about your idea."),
]

for slug, title, desc, body, ch, cb in PAGES:
    pathlib.Path(slug).write_text(shell(slug, title, desc, body, ch, cb))
    print("wrote", slug)
