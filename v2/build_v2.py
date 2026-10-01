"""v2 pages, rendered from the same content as the live site.

build.py stays the single source of truth for the words: this runs its content
definitions (everything above its write loop), takes each page's body and closing
copy, and wraps them in the v2 chrome. Fill a blank in build.py, run both, and
both versions say the same thing. The v2 home page is hand-built (index.html) and
is not touched here.

Run from the repository root:  python v2/build_v2.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / 'build.py').read_text(encoding='utf-8')
ns = {}
import os
os.chdir(ROOT)
exec(compile(src.split('\nfor page in PAGES:')[0], 'build.py', 'exec'), ns)

NAV = [("how-it-works.html", "How it works"), ("what-ive-built.html", "What I've built"),
       ("about.html", "About")]
ARROW = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13m0 0l-5.5-5.5M18 12l-5.5 5.5"/></svg>')
INTAKE = '../start.html#intake'


def adapt(body):
    """The v1 markup is kept as content; only what the v2 chrome needs changes."""
    body = body.replace('href="#intake"', f'href="{INTAKE}"')
    # The first opening section becomes the hero and gets the living field.
    body = body.replace('<section class="open">',
                        '<section class="open hero hero--page">'
                        '<canvas class="hero__field" id="field" aria-hidden="true"></canvas>', 1)
    # Statements light word by word as they are read, like the home page's bind.
    body = re.sub(r'class="statement"', 'class="statement" data-words', body)
    return body


def page(slug, title, desc, body, close_heading, close_body, opts):
    here = opts.get('nav_slug') or slug
    nav = '\n    '.join(
        f'<a href="{h}"{" aria-current=\"page\"" if h == here else ""}>{t}</a>' for h, t in NAV)
    ask_cur = ' aria-current="page"' if here == 'start.html' else ''
    robots = '<meta name="robots" content="noindex">'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<meta name="theme-color" content="#FAF3E3">
<link rel="preload" href="../assets/fonts/plex-sans-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="v2.css">
<link rel="stylesheet" href="v2-pages.css">
<script>document.documentElement.classList.add('js')</script>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%23171B34'/><path d='M24.3 21.6A10 10 0 1 1 24.3 10.4' fill='none' stroke='%23FAF3E3' stroke-width='3' stroke-linecap='round'/><circle cx='16' cy='16' r='3.5' fill='%23C4522C'/></svg>">
</head>
<body class="page">
<a class="skip" href="#main">Skip to main content</a>
<div class="grain" aria-hidden="true"></div>
<div class="cursor" aria-hidden="true"></div>
<div class="rail" aria-hidden="true"><i class="rail__track"></i><i class="rail__fill"></i><i class="rail__dot"></i></div>

<header class="nav">
  <a class="mark" href="./" aria-label="one flow first, home">
    <svg viewBox="0 0 32 32" aria-hidden="true"><path d="M25.1 22.2A11 11 0 1 1 25.1 9.8" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><circle cx="16" cy="16" r="3.7" fill="#B84B00"/></svg>
    <span><i>one flow</i><em></em><b>first</b></span>
  </a>
  <nav aria-label="Primary">
    {nav}
    <a class="nav__ask" href="start.html"{ask_cur} data-magnetic>First step</a>
  </nav>
</header>

<main id="main">
{adapt(body)}

<section class="close" id="close">
  <canvas class="close__field" id="closeField" aria-hidden="true"></canvas>
  <div class="wrap close__inner">
    <header class="label label--center" data-reveal><b>Next</b>Step one</header>
    <h2 class="close__title" data-reveal>{close_heading}</h2>
    <p class="close__deck" data-reveal>{close_body}</p>
    <div class="close__acts" data-reveal>
      <a class="btn btn--big" href="{INTAKE}" data-magnetic><span>Tell me about your idea</span><i class="btn__chip" aria-hidden="true">{ARROW}</i></a>
      <p class="close__note">No scoring, no auto-reply, no chatbot in between.</p>
    </div>
  </div>
</section>
</main>

<footer class="foot">
  <div class="wrap foot__row">
    <span>&copy; 2026 One flow first</span>
    <a href="mailto:hello@oneflowfirst.com">hello@oneflowfirst.com</a>
  </div>
</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js" defer></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js" defer></script>
<script src="v2.js" defer></script>
</body>
</html>
'''


for p in ns['PAGES']:
    slug, title, desc, body, ch, cb = p[:6]
    if slug == 'index.html':
        continue
    opts = p[6] if len(p) > 6 else {}
    (ROOT / 'v2' / slug).write_text(page(slug, title, desc, body, ch, cb, opts), encoding='utf-8')
    print('wrote v2/' + slug)
