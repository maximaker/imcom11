# One flow first

Static marketing site for a productized two-week discovery engagement.
The offer keeps the two-week timeframe; the brand does not use the word "sprint".
Five pages plus a case study, no build step, no webfont requests, and nothing
fetched from anywhere else. Assets carry a content hash in their URL
(`style.css?v=…`), so an edit is never hidden behind a cached copy. GSAP is the one dependency and it is vendored, not
linked, so the site still makes no external request.

## Structure

    index.html            home
    how-it-works.html     the full process
    what-ive-built.html   proof (App 01 is written out, 02 and 03 are placeholders)
    case-slate.html       one app as a full case study, and the template for the rest
    about.html            the person
    start.html            intro-call form
    assets/css/style.css  the whole design system
    assets/img/mark.svg   the logomark, standalone
    assets/js/intro.js    the first-load animation
    assets/js/vendor/     gsap.min.js, vendored
    assets/js/site.js     all behavior
    build.py              regenerates the five pages from one shell

Edit `build.py` and run `python3 build.py` to change shared chrome, or edit the
HTML directly for one-off copy changes.

## The first-load animation

`assets/js/intro.js`, GSAP, once ever per browser.

The mark assembles itself: one dot, then others gathering around it, settling
onto the circle and hardening into the ring, gap included. One dot stays lit in
the middle, the line runs out through the gap, and the whole thing walks to the
masthead at the size it lives at. Then the page arrives behind it, a piece at a
time, in reading order.

Four things are load-bearing:

- **The gate is inline in the head.** Hiding the page from a deferred script means
  showing it first and snatching it back. It also injects GSAP itself, so the
  other 99% of loads never download 72KB they cannot use.
- **The flag is written when the animation starts,** not when it ends, so
  navigating away halfway still counts as having seen it. No storage means no
  animation, which is the safe way round.
- **The landing is measured, not guessed.** The masthead mark is hidden but still
  laid out, so its box is real. Verified pixel-exact: 30px onto 30px, centre
  delta [0, 0], which is what lets the stage vanish and the real mark appear in
  the same frame without a visible swap.
- **The pieces it brings in are marked `data-in`.** They carry `.rev`, which is
  `opacity:0` until the scroll observer marks it; without this, `clearProps` at
  the end of the stagger hands them back to that rule and they disappear, the
  button among them.

It runs unhurried: 5.35s to the mark landing, another 1.5s for the page, with
every phase overlapping the next so nothing starts from a standstill.

Four things keep it honest to the mark it is drawing, and all four are worth
leaving alone:

- **A dot is exactly as thick as the ring it becomes.** `DOT_R` is read from the
  ring's own stroke width, so the stroke fuses with the dots instead of stepping
  up in weight as it draws through them.
- **The dots span the solid arc end to end,** 34 to 326 degrees, seated at
  `GAP + SOLID * i / (N - 1)`. Inset by half a step, as an even distribution would
  be, the ring visibly grows past where the dots were.
- **Nothing solidifies before the circle exists.** The converge runs to 2.49s once
  its stagger is counted, so the stroke starts at 2.50s. Earlier and it draws ring
  where dots have not arrived.
- **Nothing is transformed that has a moving bounding box, and no origin is
  expressed in box-relative units.** On an SVG element `transformOrigin: '16px
  16px'` means 16px from the element's own bounding box, not the user-space point
  (16,16): it scaled the core 7 units off centre. And rotating the swarm `<g>` is
  worse, because its box is the union of its moving children, so GSAP's origin
  compensation is computed against a box that no longer exists and leaves a
  translate in the matrix even at rotation 0. `svgOrigin` fixes the first and not
  the second. The dots are held in polar coordinates and painted out by hand
  instead, which has no origin to get wrong. `svgOrigin` on the core, plain
  `transformOrigin: 'center'` on each dot, whose box never changes.
- **The painter hangs off the timeline, not off a tween.** A tween's `onUpdate` can
  fire before the tweens that move the data, which paints the previous frame's
  positions. Invisible at 60fps, but it made the dots reach their seats a frame
  after the stroke began drawing through them.
- **Dash offsets are written to `style` by hand, not tweened as properties.** GSAP
  renders a dash offset as a whole number of px regardless of `autoRound`, and
  these lengths are fractional: the lead is 11.2 units long, and hidden at 11 it
  painted 0.2 units of stroke with a round cap on it from the first frame, as a
  stray dot beside the first idea. Rounding also made the drawing step a unit at a
  time.

The core's size is a transform rather than its `r` attribute, which keeps it off
the rasteriser, and the seed is the size of one of the other dots, because that is
what it is at that point. The landing is read through a function rather than
frozen into numbers, so a window resized or a phone turned during the five seconds
before the move still lands the mark on the masthead. Any scroll, tap or keypress speeds the timeline up rather than
jumping it, so the mark still lands where it belongs.

Reduced motion skips it. So does a missing GSAP, a failed timeline, and a three
second failsafe in the gate: the page must never stay hidden.

**To watch it again:** a hard reload (ctrl+shift+R), or add `?intro` to the URL.
`#intro` works too, and `?intro` overrides reduced motion, since asking for it is
asking for it. The hard-reload check is the one heuristic here: a page cannot read
modifier keys on load, but a hard reload bypasses the cache, so the document
really comes down the wire while a plain reload is answered from cache or with a
304. `transferSize` is what separates them, and it must be compared against
`encodedBodySize` rather than simply being non-zero. `encodedBodySize` alone
reports the full body either way, so an earlier version of this replayed the
animation on every ordinary reload. Measured here: 300 bytes against 25,305 from
cache, 25,605 against 25,305 downloaded.

## Design notes

- Warm palette on `#FEF6F0` paper with a `#CC5500` accent. The accent is split:
  `--clay-mark` for graphic marks, `--clay-500` for text, because the brand
  orange only reaches 4.04:1 on this paper and fails AA at label sizes.
- Single system sans; hierarchy comes from weight (300 / 640), not from families.
- Hero leading is set by `.rise`'s bottom margin, not its line-height. Each line
  is a masked block, so its box must contain its own descenders: the stack's
  deepest face needs 1.33em for that, and anything tighter gets cut by the
  mask's `overflow:hidden`. The box keeps a 1.4em line and `-0.45em` of margin
  brings the step back to 0.95em.
- Paper texture is two layers of inline SVG turbulence. No image requests.
- The wordmark is `one flow.first`, the clay dot carrying the accent. Styling is
  deliberately quiet: one weight, one colored mark.
- The logomark is an open ring with one point of focus at its centre and one
  line running out through the gap. The gap is the idea, so nothing may close
  it: no background plate, no containing circle, no second dot. Three
  declarations in CSS (`.mark__ring`, `.mark__lead`, `.mark__core`), so it
  inherits the palette instead of hardcoding it. `assets/img/mark.svg` is the
  standalone copy for anywhere CSS cannot reach.
- The masthead has no ground of its own. It sits on the page like the first
  band, and therefore it does not travel: a transparent bar that follows the
  reader is a bar the page scrolls straight through, so at rest it neither
  sticks nor draws a hairline. It earns both back only when it docks (below). It
  stays `position:relative` rather than static, because the mobile menu is
  absolutely positioned against it, and it keeps `z-index:30`: `main` carries
  `z-2`, so without one the page paints over the header and the open menu panel
  renders behind the hero. That menu keeps its own opaque ground because it does
  overlay content. There is no blur anywhere on this site, and
  `saturate()` on a bar would quietly re-tint a palette whose ratios were
  measured. The row is a `.doc`, so the header's inner edges align with every
  band by construction and it inherits the same responsive gutter instead of
  repeating 1140px and 26px. Vertical padding sits on `.top`, not on the row,
  because `.doc`'s `padding` shorthand comes later in the sheet.
- Past the hero the bar docks: it leaves the flow, waits just above the
  viewport, and drops in when the reader scrolls back up, lifting away again when
  they carry on down. It docks only while already off-screen and undocks only at
  the very top, where the docked and in-flow positions coincide, so neither
  switch is visible. 24px of travel in one direction before it responds,
  accumulated rather than per-frame, so slow scrolls still trigger it and a
  jittery trackpad does not flap it. An open mobile menu pins it open. Docked it
  does take a ground and a hairline, because there it is over the text rather
  than beside it.
- Leaving the flow would pull the whole page up by the bar's height, so `main`
  takes that height back as padding (`--bar-h`, measured while undocked). The
  fixed bar then contributes nothing to layout, main's padding contributes
  exactly what the bar used to, and the document height and every scroll offset
  stay put. If you touch either half, check a band's document position across the
  switch: it must not move.
- The nav belongs to the tracked-label register (`.margin b`, `.verdict .k`,
  `.stair .k`), not to body copy: it is reference, and on a wide screen the rail
  disc is the only thing asking to be clicked. Its size lives in the shared
  label rule so it cannot drift from the rest of the meta layer. The current
  page lights clay and keeps its underline, the same way an active margin label
  lights its dot.
- Above 1180px the masthead adopts the same three columns as every band, so
  nothing in it is positioned by eye: the logotype right-aligns where every
  margin label ends, the logomark centres in the gutter the rail runs down and
  caps the rule, and the nav left-aligns on the text column's own edge, where
  every headline and paragraph below it starts.
- One lockup, in the masthead, at every width. It briefly moved onto the rail
  above 1180px, which needed a 124px opaque plate centred on the rule to break
  it: that plate punched a hole through whatever band was behind it and
  overlapped both the margin label and the heading. The bar is where a brand
  mark belongs. The rail is structure, and its only furniture is the foot disc,
  because a circle can sit on a rule without cutting a rectangle out of the page.
- A margin label, its dot on the rail, and the first line of the heading beside
  it share one invisible row. Both offsets come from `--lead-centre` (half a
  heading's first line, so `.55` of the h2's own clamped size) and `--label-half`,
  which is why the alignment holds as the type scales. A statement-led band leads
  with a slightly larger face and lands ~3px off, under a rounding error at these
  sizes.
- `main` deliberately carries no `z-index`. With one it becomes a stacking
  context, and then nothing inside it can rise above the rail at `z-20`, which is
  why the rule used to draw through the marginalia dots and the foot disc. Both
  now sit at `z-21`. Tinted panels stay unpositioned, so the rule still passes
  over them. `.act` has `isolation:isolate`, so its sheen at `z-index:-1` stays
  contained either way.
- The left rail is a progress rule headed by the logomark, carrying the call to
  action at its foot. `--spine-top` is measured in JS rather than hardcoded, or
  differing font metrics would leave a sliver or a gap, and it is resolved
  against scroll position rather than measured once: the masthead scrolls away,
  so the head rides down with the mark and holds at the top of the viewport once
  the mark has gone. The spine sits under the bar (z-20), which costs nothing
  while the bar is transparent and lets the docked bar clip the head of the rule.
  Below 1180px the rail is hidden and the inline button in the closing section
  takes over.
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
