#!/usr/bin/env python3
"""Builds sample-home.html from index.html by adding one stylesheet.

The point of the sample is that it is the live home page and not a copy of it:
same markup, same layout, same behaviour, differing only by palette-sample.css
loading after style.css. Re-run it after build.py and the sample follows along.

Delete this file, palette-sample.css and sample-home.html to undo the whole
experiment. Promote it by folding the tokens into style.css :root instead.
"""
import hashlib
import pathlib

SRC = pathlib.Path('index.html')
OUT = pathlib.Path('sample-home.html')
CSS = 'assets/css/palette-sample.css'

src = SRC.read_text(encoding='utf-8')
ver = hashlib.sha1(pathlib.Path(CSS).read_bytes()).hexdigest()[:8]

# The override has to come after the stylesheet it overrides.
anchor = '<link rel="stylesheet" href="assets/css/style.css'
i = src.index(anchor)
j = src.index('>', i) + 1
out = (src[:j]
       + f'\n<link rel="stylesheet" href="{CSS}?v={ver}">'
       + '\n<meta name="robots" content="noindex">'
       + src[j:])

# Say what it is in the tab, and keep it out of search.
out = out.replace('<title>Is your idea worth building? | One flow first</title>',
                  '<title>Palette sample | One flow first</title>', 1)

# The page's own chrome colours are inline in the markup, so they are swapped
# here rather than in CSS: the theme colour and the favicon's three values.
out = out.replace('<meta name="theme-color" content="#FEF6F0">',
                  '<meta name="theme-color" content="#FAF3E3">', 1)
out = (out.replace("fill='%23160B02'", "fill='%23171B34'")
          .replace("stroke='%23FEF6F0'", "stroke='%23FAF3E3'")
          .replace("fill='%23CC5500'", "fill='%23C4522C'"))

# The first-load animation is keyed to localStorage and would not run here, and
# a palette sample is not the place to sit through it. Its colours are read from
# the tokens, so it follows the new palette wherever it does run.
out = out.replace("localStorage.getItem('ofo.intro') === '1'", 'true', 1)

OUT.write_text(out, encoding='utf-8')
print(f'wrote {OUT} from {SRC} (+{CSS}?v={ver})')
