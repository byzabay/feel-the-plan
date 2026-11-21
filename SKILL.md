---
name: feel-the-plan
description: Answer "how does this work", "what's the plan" or "what did you change" with one offline HTML page (lanes x steps, icons, hover cards, blue questions with a suggested pick) instead of long prose. Use whenever the user asks to diagram, map, sketch, visualise or explain a flow, a feature, an architecture or a build plan, and before building anything multi-step when the user wants to agree the plan first. Built for people who lose the thread in walls of text (ADHD-friendly).
---

# Feel the plan

Make one self-contained `.html` page the user opens from disk. The point: the whole shape is visible at a glance, detail appears only on hover, and every decision is small.

No server, CDN, remote font or network request. Pure Python 3 standard library.

## When to use

- The user asks how something works, what you plan to build, or what changed.
- A reply would run past about 15 lines, or explains more than 3 steps.
- Before a multi-step build: draw the plan, get a yes, then write code. A diagram is a proposal until the user approves it.

## The layout (always the same, so it's learned once)

- **Lanes (rows)** = who or what does the work. Each lane has a colour, a big icon tile, a bold name and a five-word line ("API server · runs in the cloud").
- **Columns** = the steps, left to right: a black numbered header, then a yellow strip with one short made-up example.
- **Boxes** = an icon, a bold plain-English title, one short line, and status tags. Nothing longer on the box face.
- **Arrows** = right angles only, no crossings. A short label only where it helps ("on error").
- **Hover cards** = the detail. Hover a box (tap on a phone) to see its card: facts table, longer text, code paths, a mini flow. Click keeps it open; Esc closes.
- **Around it**: a legend at the top, a one-line "short answer" box above the diagram, a "How to read it" box under it.
- **Complex step**: give it its own tab with its own diagram, and link to it from the box's card.

## Words

- Short sentences. Plain English. Define any jargon in five words.
- No code names on the box face. Put file paths in the hover card ("Code: `api/signup.py`, the 3 checks").
- **Blue boxes** = open questions. Each has your pick and one line of why. End the page with an "All questions" tab so the user can answer in one line ("1 yes, 2 no, 3 your pick").
- **Yellow notes** = examples and space for the user's notes. Mark made-up data as made up.
- **Red text** = what changed since the last version. Never overwrite: save `-v2`, `-v3` and keep the old file.

## Status tags

Use the same four everywhere, so status reads without reading:

- `live` green tick: working today
- `off` amber pause: built but switched off
- `next` red clock: in the next release
- `idea` grey dashed bulb: not built

Colour only where it means a status. Everything else is a neutral grey chip ("cloud:Hosted", "device:Your laptop", "app:Admin page").

## How to build it

```python
import sys; sys.path.insert(0, "<skill>/scripts")
import lanes, page, pageedit

spec = {
  "id": "signup", "title": "What happens when someone signs up",
  "lanes": [{"k": "you", "name": "You", "sub": "the developer", "tone": "you", "icon": "user"}, ...],
  "cols":  [{"k": "c1", "lv": "1", "name": "Form sent", "ex": "Sam types an email"}, ...],
  "nodes": [{"id": "form", "lane": "web", "col": "c1", "n": "1", "icon": "file-text",
             "t": "Sign-up form", "b": "Checks the email looks real", "tags": ["live"],
             "detail": page.facts([("What it does", "..."), ("Status", "live")])}, ...],
  "edges": [{"f": "form", "t": "api", "k": "flow", "lbl": "POST"}, ...],
  "opts":  {"gut": 150, "tries": 12},
}
diagram_html, d = lanes.render(spec)      # d.crossings should be 0
html = page.page(title, comment, stamp, header, legend, nav, sections_html, footer, look="v4")
pageedit.write_page("plan-v1.html", html)
```

- Worked example: `examples/build_example.py` (a made-up sign-up flow with a sub-flow tab).
- **Tones**: person, you, ai, app, db, cloud, tools, store, plain, mail, chat, code, code2.
- **Node kinds**: fix, ai, human, store, sys, gap, todo, note, q, hub, accent, done.
- **Edge kinds**: flow, email, login, data, move, loop, dash.
- **Page helpers**: `tabs_nav`, `section` (pass `textonly=True` for list-only tabs), `what` (user story first), `qbox` (blue question), `note_box` (yellow), `facts`, `miniflow`, `go` (link to a sub-flow tab), `prompt_block` (show a prompt formatted, never raw markdown).
- **Icons**: lucide line icons, names in `page.ICON_NAMES`. Use what the thing is (user, monitor, cloud, brain, database, wrench), never brand logos. Add an icon with `scripts/build_sprite.py`.
- If a label doesn't fit or a crossing remains: widen `opts.gut` (e.g. 150) or drop the label. Keep `row_gap` at 40 or more.

## Look rules

- Text at least 20px. Weights 400, 500 and 600 only.
- Sentence case. No uppercase labels, no emoji or text symbols as icons.
- One accent colour. Three text greys. A 4px spacing grid.
- Light/dark toggle on every page.
- Motion names what moves, one easing curve, respects reduced-motion.
- Every tab leads with a diagram, except list-only tabs (questions).

## Edit in place

Every v4 page has an "Edit page" button. The user clicks any text to change or delete it; Cmd+S saves into the file and keeps `<file>.bak`. Saving needs `python3 scripts/save_server.py --root <folder>` running; without it the page downloads an edited copy.

`pageedit.write_page()` refuses to overwrite a page the user edited in the browser. Read their edits first (diff the file), fold them into your spec, then rebuild with `FORCE=1`.

## Check it mechanically, then hand over

Run `python3 scripts/verify.py <file>`. It checks: balanced HTML and SVG, unique IDs, every arrow's ends exist, no box overlaps or crossings, the 20px floor, no network calls, every tab has a diagram.

Don't open a browser or take screenshots to judge the look unless the user says so. Whether it looks right is their call.

Hand over with: the file path, what changed (and what's red), and the questions the user needs to answer.
