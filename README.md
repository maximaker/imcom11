# One flow first

Static marketing site for a productized two-week discovery engagement.
The offer keeps the two-week timeframe; the brand does not use the word "sprint".
Five pages, no build step, no dependencies, no webfont requests.

## Structure

    index.html            home
    how-it-works.html     the full process
    what-ive-built.html   proof (App 01 is written out, 02 and 03 are placeholders)
    case-slate.html       one app as a full case study, and the template for the rest
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

## Scope, and the one thing the copy must not promise

The two weeks covers the risky assumption, the decision rule, one working flow,
and the playbook. It does **not** cover running the sessions. Recruiting the
right people takes real calendar time and depends on strangers being free, so
promising evidence inside a fixed two weeks would mean either padding the
timeline or rushing the recruiting. The sessions are an add-on.

That constraint shapes copy on every page: the hero promises a bar and a method,
not evidence; the after-state section says guessing turns into something
testable; the decision brief states the question and the bar, and the call gets
written once the sessions are done. If a line ever implies testing happens
inside the two weeks, it is wrong.

## The case study template

`case-slate.html` is a worked example and the pattern for every one after it.
Its band order is the method itself, which is the point: the idea, the risky
part, the decision rule agreed in advance, the one flow, what testing showed,
the call, the change and the kill, where the two weeks went. Copy the `CASE`
block in `build.py`, keep that order, change the content.

It reuses the existing components (`.verdicts`, `.probe`, `.stats`, `.stairs`,
`.case`) and adds two: `.quote` for a session quote with the moment attached,
and `.screen` for a phone-sized line drawing standing in for a screenshot.
There are no photographs anywhere on this site, so the screens are drawn in the
same idiom as the deliverable glyphs. To use a real screenshot, swap a
`screen(...)` call for `<img src="assets/img/name.png" alt="...">`; `.shot`
styles the figure, not the medium.

The page is `robots=noindex` and its hero margin says the numbers are
illustrative. Both come off in one line each once a real case replaces it.

## Before this goes live

1. Case notes on `what-ive-built.html` are bracketed placeholders.
2. The form has no backend: `assets/js/site.js` fakes the submit.
3. `hello@oneflowfirst.com` is a stand-in until the real mailbox exists.
4. Proof cards 2 and 3 on `index.html`, and App 02 and App 03 on
   `what-ive-built.html`, are still bracketed placeholders.
5. `case-slate.html` carries invented session counts and quotes. Replace them,
   drop the hero margin note, and remove `robots` from its `PAGES` entry. The
   page says up front that Slate is a self-built app whose testers were already
   reachable, which is why its timeline is faster than a client engagement's.
