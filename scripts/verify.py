"""Mechanical checks for a lane-diagram HTML page (no browser).

usage: python3 -I verify.py file.html
"""
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
SVG_SELF = {"polyline", "path", "circle", "rect", "line", "use", "stop", "polygon", "ellipse"}


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors, self.ids, self.els = [], [], {}, []
        self.text_by_section = {}
        self.cur_section = None
        self.in_style = False
        self.styles = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.els.append((tag, a, self.getpos()))
        if "id" in a:
            if a["id"] in self.ids:
                self.errors.append(f"duplicate id {a['id']} at {self.getpos()}")
            self.ids[a["id"]] = (tag, a)
        if tag == "section" and a.get("role") == "tabpanel":
            self.cur_section = a.get("id")
            self.text_by_section[self.cur_section] = 0
        if tag == "style":
            self.in_style = True
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        a = dict(attrs)
        self.els.append((tag, a, self.getpos()))
        if "id" in a:
            if a["id"] in self.ids:
                self.errors.append(f"duplicate id {a['id']}")
            self.ids[a["id"]] = (tag, a)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "style":
            self.in_style = False
        if not self.stack:
            self.errors.append(f"stray </{tag}> at {self.getpos()}")
            return
        t, pos = self.stack.pop()
        if t != tag:
            self.errors.append(f"mismatch: <{t}> opened {pos} closed by </{tag}> at {self.getpos()}")
            # try to recover
            while self.stack and self.stack[-1][0] != tag:
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        if tag == "section":
            self.cur_section = None

    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)
        elif self.cur_section and data.strip():
            self.text_by_section[self.cur_section] += len(data.strip())


def style_px(st, key):
    m = re.search(rf"(?:^|;)\s*{key}\s*:\s*(-?[\d.]+)px", st or "")
    return float(m.group(1)) if m else None


def main(path):
    src = open(path, encoding="utf-8").read()
    p = P()
    p.feed(src)
    p.close()
    errs = list(p.errors)
    warns = []
    if p.stack:
        errs.append(f"unclosed tags: {p.stack[-5:]}")
    ids = p.ids
    # references
    for tag, a, pos in p.els:
        for k in ("aria-controls", "aria-labelledby", "data-for", "data-show", "data-detail", "data-source", "data-target"):
            v = a.get(k)
            if v and v not in ids:
                errs.append(f"{k}={v} has no target (line {pos[0]})")
        h = a.get("href", "")
        if h.startswith("#") and len(h) > 1 and h[1:] not in ids and not h.startswith("#i-"):
            errs.append(f"href {h} has no target")
        if tag == "use" and h.startswith("#i-") and h[1:] not in ids:
            warns.append(f"icon {h} has no symbol in the page sprite (line {pos[0]})")
    # external resources
    for tag, a, pos in p.els:
        for k in ("src", "href", "xlink:href", "action", "poster", "data"):
            v = (a.get(k) or "").strip().lower()
            if v.startswith(("http:", "https:", "//", "ftp:")):
                if tag == "a" and k == "href":
                    warns.append(f"external link (not loaded, click-only) line {pos[0]}: {v[:60]}")
                else:
                    errs.append(f"external resource {tag} {k}={v[:80]}")
    css = "\n".join(p.styles)
    if "@import" in css:
        errs.append("@import in CSS")
    for m in re.finditer(r"url\(([^)]*)\)", src):
        if not m.group(1).strip("'\" ").startswith("data:") and not m.group(1).startswith("#"):
            errs.append(f"url() reference {m.group(1)[:60]}")
    if "Content-Security-Policy" not in src:
        warns.append("no CSP meta")
    if re.search(r"<script[^>]+src=", src):
        errs.append("external script tag")
    # look rules: 400/500/600 weights, sentence case, named transitions
    style_text = css + "\n" + "\n".join(a.get("style", "") for _, a, _ in p.els)
    for m in re.finditer(r"font-weight\s*:\s*(\d+|bold(?:er)?)", style_text):
        v = m.group(1)
        if not v.isdigit() or int(v) > 600:
            errs.append(f"font-weight {v}: use 400, 500 or 600")
    if re.search(r"text-transform\s*:\s*uppercase", style_text):
        errs.append("uppercase label: use sentence case")
    for m in re.finditer(r"transition\s*:\s*([^;}]+)", style_text):
        v = m.group(1).strip()
        if v.startswith("all") or re.match(r"^[\d.]", v):
            errs.append(f"transition '{v}': name the property (color, background-color, opacity, transform)")
    if re.search(r"filter\s*:\s*brightness", style_text):
        warns.append("filter:brightness hover: use a background colour step")
    body = re.sub(r"<(style|script)\b.*?</\1>", "", src, flags=re.S)
    glyphs = set(re.findall(r"<button\b[^>]*>([^<]*[⌂✦✧✨◎◇◆⚙☰☵≡≣＋×✕▾▼▲✓✔✗][^<]*)</button>", body))
    for g in sorted(glyphs)[:10]:
        warns.append(f"text glyph used as an icon in a button: '{g.strip()[:30]}' (use an inline SVG line icon)")
    if re.search(r"[\U0001F300-\U0001FAFF]", body):
        warns.append("emoji in the page: use a line icon or nothing")
    for t in sorted(set(re.findall(r"<button\b[^>]*>([^<]{1,40}\.)</button>", body)))[:10]:
        warns.append(f"button label ends with a full stop: '{t}'")
    # font floor: every font size is at least 20px
    for m in re.finditer(r"font-size\s*:\s*([\d.]+)\s*(px|em|rem|%|pt|vw)?", src):
        val, unit = float(m.group(1)), (m.group(2) or "")
        if unit == "px" and val < 20:
            errs.append(f"font-size {val}px below the 20px floor (offset {m.start()})")
        elif unit in ("em", "rem", "%", "pt", "vw"):
            errs.append(f"non-px font-size {m.group(0)} (cannot prove 20px floor)")
    for m in re.finditer(r"\bfont\s*:\s*([\d.]+)px", src):
        if float(m.group(1)) < 20:
            errs.append(f"font shorthand {m.group(0)} below floor")
    for m in re.finditer(r'font-size="([\d.]+)"', src):
        if float(m.group(1)) < 20:
            errs.append(f"svg font-size {m.group(1)} below floor")
    # secrets
    for pat in (r"sk-[A-Za-z0-9]{16,}", r"ntn_[A-Za-z0-9]{10,}", r"xox[bap]-", r"AKIA[0-9A-Z]{12,}", r"-----BEGIN", r"\beyJ[A-Za-z0-9_-]{20,}", r"ghp_[A-Za-z0-9]{20,}", r"sb_secret_"):
        if re.search(pat, src):
            errs.append(f"possible secret pattern {pat}")
    # tabs
    tabs = [(a.get("data-go"), a.get("aria-controls"), a.get("id")) for t, a, _ in p.els if a.get("role") == "tab"]
    panels = [a.get("id") for t, a, _ in p.els if a.get("role") == "tabpanel"]
    if len(tabs) != len(panels):
        errs.append(f"{len(tabs)} tabs vs {len(panels)} panels")
    for go, ctl, tid in tabs:
        if ctl not in panels:
            errs.append(f"tab {tid} controls missing panel {ctl}")
        elif ids[ctl][1].get("aria-labelledby") != tid:
            errs.append(f"panel {ctl} not labelled by {tid}")
        if f"screen-{go}" != ctl:
            errs.append(f"tab {tid} data-go {go} does not match {ctl}")
    for sid, n in p.text_by_section.items():
        if n < 200:
            errs.append(f"panel {sid} has almost no text ({n} chars)")
    # every tab is visual: a v4 tab leads with a lanes diagram (or an old-style canvas); a list-only tab says so
    # with data-textonly. Older looks are left alone.
    v4page = 'class="frame v4look' in src
    for m in re.finditer(r'<section\b([^>]*)>(.*?)</section>', src, flags=re.S):
        attrs, body = m.group(1), m.group(2)
        cm = re.search(r'class="([^"]*)"', attrs)
        cls = cm.group(1).split() if cm else []
        if "screen" not in cls or not (v4page or "v4look" in cls) or "data-textonly" in attrs:
            continue
        if 'class="lanes' not in body and 'class="canvas' not in body:
            im = re.search(r'id="([^"]+)"', attrs)
            errs.append(f"tab {im.group(1) if im else '?'} has no diagram: lead it with a lanes diagram (icons, hover cards), "
                        "or mark a list-only tab data-textonly")
    # diagrams
    diag_count = 0
    total_edges = 0
    crossings_all = []
    for did, (tag, a) in ids.items():
        if "lanes" not in (a.get("class") or "").split():
            continue
        diag_count += 1
        W, H = float(a["data-w"]), float(a["data-h"])
        # collect boxes and wires belonging to this diagram by id prefix
        boxes = {}
        for t, aa, pos in p.els:
            cl = (aa.get("class") or "").split()
            if "bx" in cl and aa.get("id", "").startswith(did + "-"):
                st = aa.get("style", "")
                x, y, w, h = (style_px(st, k) for k in ("left", "top", "width", "height"))
                boxes[aa["id"]] = (x, y, x + w, y + h)
        for bid, (x1, y1, x2, y2) in boxes.items():
            if x1 < 0 or y1 < 0 or x2 > W or y2 > H:
                errs.append(f"{bid} outside canvas")
        bl = list(boxes.items())
        for i in range(len(bl)):
            for j in range(i + 1, len(bl)):
                (ia, A), (ib, B) = bl[i], bl[j]
                if A[0] < B[2] and B[0] < A[2] and A[1] < B[3] and B[1] < A[3]:
                    errs.append(f"boxes overlap: {ia} {ib}")
        wires = []
        for t, aa, pos in p.els:
            if t == "polyline" and aa.get("id", "").startswith(did + "-"):
                pts = [tuple(float(v) for v in q.split(",")) for q in aa["points"].split()]
                wires.append((aa["id"], aa.get("data-source"), aa.get("data-target"), pts))
        total_edges += len(wires)
        segs = []
        for wid, s, tg, pts in wires:
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                if x1 != x2 and y1 != y2:
                    errs.append(f"{wid}: diagonal segment {x1},{y1}->{x2},{y2}")
                segs.append((wid, (x1, y1), (x2, y2)))

            def on_border(pt, b):
                x, y = pt
                return (b[0] - 1 <= x <= b[2] + 1 and b[1] - 1 <= y <= b[3] + 1) and (
                    abs(x - b[0]) <= 1 or abs(x - b[2]) <= 1 or abs(y - b[1]) <= 1 or abs(y - b[3]) <= 1)
            if s not in boxes or tg not in boxes:
                errs.append(f"{wid}: source/target not a box ({s},{tg})")
                continue
            if not on_border(pts[0], boxes[s]):
                errs.append(f"{wid}: start {pts[0]} not on source {s} border")
            if not on_border(pts[-1], boxes[tg]):
                errs.append(f"{wid}: end {pts[-1]} not on target {tg} border")
            # passes through boxes
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                lx, hx, ly, hy = min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2)
                for bid, b in boxes.items():
                    if ly == hy:
                        hit = b[1] + 1 < ly < b[3] - 1 and lx < b[2] - 1 and hx > b[0] + 1
                    else:
                        hit = b[0] + 1 < lx < b[2] - 1 and ly < b[3] - 1 and hy > b[1] + 1
                    if hit:
                        errs.append(f"{wid}: segment crosses box {bid}")
        # overlaps and crossings between different wires
        for i in range(len(segs)):
            wa, a1, a2 = segs[i]
            for j in range(i + 1, len(segs)):
                wb, b1, b2 = segs[j]
                if wa == wb:
                    continue
                ah, bh = a1[1] == a2[1], b1[1] == b2[1]
                if ah and bh and a1[1] == b1[1]:
                    lo = max(min(a1[0], a2[0]), min(b1[0], b2[0]))
                    hi = min(max(a1[0], a2[0]), max(b1[0], b2[0]))
                    if hi - lo > 0:
                        errs.append(f"wires overlap horizontally: {wa} {wb} at y={a1[1]}")
                elif (not ah) and (not bh) and a1[0] == b1[0]:
                    lo = max(min(a1[1], a2[1]), min(b1[1], b2[1]))
                    hi = min(max(a1[1], a2[1]), max(b1[1], b2[1]))
                    if hi - lo > 0:
                        errs.append(f"wires overlap vertically: {wa} {wb} at x={a1[0]}")
                elif ah != bh:
                    hseg, vseg = ((a1, a2), (b1, b2)) if ah else ((b1, b2), (a1, a2))
                    hy, hx1, hx2 = hseg[0][1], min(hseg[0][0], hseg[1][0]), max(hseg[0][0], hseg[1][0])
                    vx, vy1, vy2 = vseg[0][0], min(vseg[0][1], vseg[1][1]), max(vseg[0][1], vseg[1][1])
                    if hx1 < vx < hx2 and vy1 < hy < vy2:
                        crossings_all.append(f"{wa} x {wb} at ({vx:.0f},{hy:.0f})")
        # callouts vs boxes
        for t, aa, pos in p.els:
            if t == "circle":
                pass
    for c in crossings_all:
        errs.append("crossing: " + c)
    print(f"{path}\n  diagrams={diag_count} wires={total_edges} tabs={len(tabs)} ids={len(ids)} bytes={len(src)}")
    for w in warns:
        print("  warn:", w)
    if errs:
        print(f"  FAIL {len(errs)}")
        for e in errs[:80]:
            print("   -", e)
        return 1
    print("  PASS all checks")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
