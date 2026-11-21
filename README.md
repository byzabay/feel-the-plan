# feel-the-plan

A Claude Code skill that turns "explain this to me" into **one picture you can take in at a glance**, instead of a wall of text.

Built for people with ADHD (and anyone else) who build software with Claude and lose the thread in long replies.

**[See a live example](https://byzabay.github.io/feel-the-plan/)**: a made-up "user signs up" flow. Hover or tap any box.

## The problem it solves

You ask Claude how a feature works, or what it plans to build. You get 60 lines of prose. By line 20 you've lost where you were. You skim, approve something you didn't fully read, and the build drifts.

This skill makes Claude answer with a single offline HTML page instead:

- **Lanes (rows)** = who or what does the work: you, the browser, the API, the database, the AI model.
- **Columns** = the steps, left to right, each with one short example.
- **Boxes** = one bold title and one short line. Detail hides in a card you see on hover (or tap on a phone).
- **Status at a glance**: icons and colours for live, built but off, next, and just an idea.
- **Questions in blue boxes**, each with Claude's suggested answer, so you decide in seconds.
- **Yellow notes** for examples. **Red text** marks what changed since the last version.
- **Edit in place**: click "Edit page", type over anything, Cmd+S saves it back into the file.

One page. One glance for the shape. Hover only where you care.

## Why this helps an ADHD brain

- **Less to hold in your head.** The whole flow is on screen at once, so working memory isn't doing the layout.
- **Detail on demand.** Nothing competes for attention until you point at it.
- **Same layout every time.** Lanes, then steps, then boxes. You learn to read it once.
- **Decisions are small.** Each question already has a pick; you say yes or change it.
- **Spot the change fast.** Version 2 shows edits in red, so you don't reread everything.

It is a working style, not medical advice.

## What's in the box

```
SKILL.md              the instructions Claude follows
scripts/lanes.py      lanes × steps diagram with right-angle arrows that never cross
scripts/page.py       page chrome: tabs, legend, notes, hover cards, light/dark toggle
scripts/pageedit.py   "Edit page" mode and Cmd+S save
scripts/save_server.py  tiny local helper that saves edits back into the file (optional)
scripts/verify.py     mechanical checks: valid HTML, no crossings, 20px text floor, no network calls
scripts/build_sprite.py  rebuilds the icon set from lucide
examples/build_example.py  a made-up "user signs up" flow
```

Pure Python 3 standard library. No server, CDN, font download or network call in the pages. Open them straight from disk.

## Install

```bash
git clone https://github.com/byzabay/feel-the-plan ~/.claude/skills/feel-the-plan
```

Then in Claude Code just ask: "diagram how sign-up works", "map the plan before you build", "show me this as a picture".

Try the example:

```bash
python3 ~/.claude/skills/feel-the-plan/examples/build_example.py && open ~/.claude/skills/feel-the-plan/examples/example.html
```

To save edits from the browser back into the file, run the helper in the folder that holds your pages:

```bash
python3 ~/.claude/skills/feel-the-plan/scripts/save_server.py --root .
```

Without it, Cmd+S downloads an edited copy instead.

## Tips for working with Claude this way

- Ask for the picture **before** the build: "diagram the plan first, don't write code until I say go".
- Answer the blue questions in one line: "1 yes, 2 no, 3 your pick".
- Ask for "v2" when you change your mind. The old version stays; changes show in red.
- Keep the hover cards for detail. If a box needs a paragraph on its face, the step is too big: split it.

## Licence

MIT, see [LICENSE](LICENSE). Icons are from [Lucide](https://lucide.dev) (ISC), see [NOTICE](NOTICE).
