# The discovery sprint

Static marketing site for a productized two-week discovery sprint.
Five pages, no build step, no dependencies, no webfont requests.

## Structure

    index.html            home
    how-it-works.html     the full process
    what-ive-built.html   proof (case notes are placeholders)
    about.html            the person
    start.html            intro-call form
    assets/css/style.css  the whole design system
    assets/js/site.js     all behaviour
    build.py              regenerates the five pages from one shell

Edit `build.py` and run `python3 build.py` to change shared chrome, or edit the
HTML directly for one-off copy changes.

## Design notes

- Warm palette on `#FEF6F0` paper with a `#CC5500` accent. The accent is split:
  `--clay-mark` for graphic marks, `--clay-500` for text, because the brand
  orange only reaches 4.04:1 on this paper and fails AA at label sizes.
- Single system sans; hierarchy comes from weight (300 / 640), not from families.
- Paper texture is two layers of inline SVG turbulence. No image requests.
- The left rail carries the wordmark at its top and the call to action at its
  foot. Below 1180px the rail is hidden and an inline button takes over, so
  there is always exactly one visible CTA.

## Before this goes live

1. Case notes on `what-ive-built.html` are bracketed placeholders.
2. The form has no backend: `assets/js/site.js` fakes the submit.
3. `hello@example.com` needs replacing.
