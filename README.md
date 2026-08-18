# One flow first

Static marketing site for a productized two-week discovery engagement.
The offer keeps the two-week timeframe; the brand does not use the word "sprint".
Five pages, no build step, no dependencies, no webfont requests.

## Structure

    index.html            home
    how-it-works.html     the full process
    what-ive-built.html   proof (case notes are placeholders)
    about.html            the person
    start.html            intro-call form
    assets/css/style.css  the whole design system
    assets/js/site.js     all behavior
    build.py              regenerates the five pages from one shell

Edit `build.py` and run `python3 build.py` to change shared chrome, or edit the
HTML directly for one-off copy changes.

## Design notes

- Warm palette on `#FEF6F0` paper with a `#CC5500` accent. The accent is split:
  `--clay-mark` for graphic marks, `--clay-500` for text, because the brand
  orange only reaches 4.04:1 on this paper and fails AA at label sizes.
- Single system sans; hierarchy comes from weight (300 / 640), not from families.
- Paper texture is two layers of inline SVG turbulence. No image requests.
- The wordmark is `one flow.first`, the clay dot carrying the accent. Styling is
  deliberately quiet: one weight, one colored mark.
- The left rail carries the wordmark at its top and the call to action at its
  foot. Below 1180px the rail is hidden and the inline button in the closing
  section takes over.
- The hero carries its own button ("Tell me about your idea") at every width,
  so the promise is never separated from the action. The rail disc and the
  closing button both read "Book a free intro call".

## Before this goes live

1. Case notes on `what-ive-built.html` are bracketed placeholders.
2. The form has no backend: `assets/js/site.js` fakes the submit.
3. `hello@oneflowfirst.com` is a stand-in until the real mailbox exists.
4. The three proof cards on `index.html` are `[APP NAME n]` placeholders.
