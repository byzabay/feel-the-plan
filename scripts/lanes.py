"""Lane diagram generator: lanes (rows) x steps (columns), orthogonal SVG arrows.

Deterministic layout + A* routing on a 10px grid. Output is static HTML/SVG so the
diagram works offline with no JS (JS only adds zoom and click-to-detail).

Icons, all optional:
  - node "icon": a lucide name, drawn at the start of the title line (width reserved like the step number);
  - lane "icon": a 64px tile in the lane's tone with a 40px icon, above the lane name (height reserved);
  - opts "tag_icons": True (default map), False, or a dict {tag kind: icon or None}. Default "auto": on when any lane
    or node has an icon, so old specs (no icons) render byte-identical to before.
Icons are <use href="#i-NAME"> into the page sprite (page.SPRITE, from lucide_sprite.py).
"""
import heapq
import html
import random
import re

G = 10              # routing grid (px)
LINE = 26           # line height for 20px text
PAD_X = 14
PAD_Y = 12
BORDER = 2

_NARROW1 = set("ijl.,:;'!|")
_NARROW2 = set("ftrI()[]{}-/\"")
_WIDE_LC = set("mw")
_WIDE_UC = set("MW")


def char_w(ch, bold=False):
    if ch == " ":
        w = 5.6
    elif ch in _NARROW1:
        w = 5.8
    elif ch in _NARROW2:
        w = 7.8
    elif ch in _WIDE_LC:
        w = 15.8
    elif ch in _WIDE_UC:
        w = 17.5
    elif ch.isdigit():
        w = 11.6
    elif ch.islower():
        w = 10.8
    elif ch.isupper():
        w = 13.6
    elif ch in "—→←↑↓↔⇄":
        w = 20.0
    elif ch in "·•":
        w = 7.0
    else:
        w = 12.5
    w *= 1.13  # safety margin over SF Pro / Inter metrics
    return w * (1.07 if bold else 1.0)


def text_w(s, bold=False):
    return sum(char_w(c, bold) for c in s)


def plain(s):
    """HTML fragment -> visible text (for width estimates)."""
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)


def wrap_lines(s, width, bold=False, first_indent=0.0):
    """Lines needed: the larger of a per-character and a flat-width estimate."""
    return max(_wrap(s, width, bold, first_indent, False), _wrap(s, width, bold, first_indent, True))


def _wrap(s, width, bold, first_indent, flat):
    total = 0
    cw = 11.6 if bold else 10.9

    def tw(x):
        return len(x) * cw if flat else text_w(x, bold)
    sp = cw if flat else text_w(" ", bold)
    for pi, para in enumerate(plain(s).split("\n")):
        words = para.split()
        if not words:
            total += 1
            continue
        line_w = first_indent if pi == 0 else 0.0
        at_start = True
        lines = 1
        for w in words:
            ww = tw(w)
            add = ww if at_start else sp + ww
            if not at_start and line_w + add > width:
                lines += 1
                line_w = ww
            else:
                line_w += add
            at_start = False
            while line_w > width:
                lines += 1
                line_w -= width
        total += lines
    return total


def ceil10(v):
    return int((v + 9) // 10 * 10)


def ceil20(v):
    return int((v + 19) // 20 * 20)


TAG_TEXT = {
    "partly": "Partly",
    "nb": "Not built",
    "inflight": "In flight",
    "built": "Built",
    "notrun": "Not running",
    "parked": "Parked",
    "later": "Later",
    "live": "Live",
    "off": "Off",
    "next": "Next",
    "idea": "Idea",
}


def tag_list(node):
    out = []
    for t in node.get("tags", []):
        if ":" in t:
            k, v = t.split(":", 1)
            out.append((k, v))
        else:
            out.append((t, TAG_TEXT.get(t, t)))
    return out


def chip_w(txt, icon=False):
    return text_w(txt, True) + 22 + (TAG_ICON_W if icon else 0)


ICON_W = 30        # title icon: 20px glyph + 8px gap + 2px safety
LANE_TILE = 64     # lane tile: 64px square with a 40px icon, stacked above the lane name
LANE_TILE_H = LANE_TILE + 8   # tile + gap below it
TAG_ICON_W = 26    # tag icon: 20px glyph + 6px gap
TAG_ICONS = {
    "built": "circle-check", "partly": "circle-pause", "notrun": "circle-pause", "parked": "circle-pause",
    "inflight": "clock", "later": "lightbulb", "nb": "circle-dashed", "ai": "cpu", "where": "server",
    "red": "triangle-alert", "cloud": "cloud", "app": "monitor", "device": "laptop", "repo": "code",
    "live": "circle-check", "off": "circle-pause", "next": "clock", "idea": "lightbulb",
}


def icon_svg(name, cls="bxi"):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#i-{html.escape(name)}"/></svg>'


def tag_icon(icons, k, v):
    if not icons:
        return None
    if k == "where" and v.lower().startswith(("code", "none")):
        return icons.get("repo", "code")
    return icons.get(k)


class LaneDiagram:
    def __init__(self, spec):
        self.s = spec
        self.id = spec["id"]
        o = spec.get("opts", {})
        self.bw = o.get("bw", 300)
        self.gut = o.get("gut", 120)
        self.label_w = o.get("label_w", 250)
        self.x0 = o.get("x0", 40)
        self.lane_pad = o.get("lane_pad", 30)
        self.row_gap = o.get("row_gap", 40)
        self.cols = spec["cols"]
        self.lanes = spec["lanes"]
        self.col_idx = {c["k"]: i for i, c in enumerate(self.cols)}
        self.lane_idx = {l["k"]: i for i, l in enumerate(self.lanes)}
        self.nodes = spec["nodes"]
        self.nid = {n["id"]: n for n in self.nodes}
        if len(self.nid) != len(self.nodes):
            raise ValueError(f"{self.id}: duplicate node ids")
        self.edges = spec.get("edges", [])
        ti = o.get("tag_icons", "auto")
        if ti == "auto":
            ti = any(x.get("icon") for x in list(spec["lanes"]) + list(spec["nodes"]))
        self.tag_icons = dict(TAG_ICONS) if ti is True else ({**TAG_ICONS, **ti} if isinstance(ti, dict) else {})
        self.notes = []
        self.layout()
        self.route_all()

    # ---------------- layout ----------------
    def col_x(self, i):
        return self.x0 + i * (self.bw + self.gut)

    def node_size(self, n):
        span = n.get("span", 1)
        w = span * self.bw + (span - 1) * self.gut
        inner = w - 2 * PAD_X - 2 * BORDER
        num_w = (text_w(str(n["n"]), True) + 26) if n.get("n") else 0
        if n.get("icon"):
            num_w += ICON_W
        h = PAD_Y * 2 + 2 * BORDER
        tl = wrap_lines(n["t"], inner, True, num_w)
        h += tl * LINE
        if n.get("b"):
            h += 4 + wrap_lines(n["b"], inner) * LINE
        tags = tag_list(n)
        if tags:
            line_w, rows = 0.0, 1
            for k, txt in tags:
                cw = chip_w(txt, bool(tag_icon(self.tag_icons, k, txt)))
                if line_w and line_w + 8 + cw > inner:
                    rows += 1
                    line_w = cw
                else:
                    line_w += (8 if line_w else 0) + cw
            h += 8 + rows * 34 + (rows - 1) * 6
        h = max(h, n.get("min_h", 0))
        return w, ceil20(h)

    def layout(self):
        ncols = len(self.cols)
        self.width = self.col_x(ncols - 1) + self.bw + self.x0
        # header: step header (black) + example (yellow)
        hw_inner = self.bw - 28
        hdr_lines = max(wrap_lines(f"{c.get('lv', '')} {c['name']}", hw_inner, True) for c in self.cols)
        self.hdr_h = ceil10(hdr_lines * LINE + 24)
        ex_lines = max((wrap_lines(c.get("ex", ""), self.bw - 34) if c.get("ex") else 0) for c in self.cols)
        self.ex_h = ceil10(ex_lines * LINE + 26) if ex_lines else 0
        self.hdr_top = 20
        self.ex_top = self.hdr_top + self.hdr_h + 12
        self.lanes_top = ceil10((self.ex_top + self.ex_h + 30) if self.ex_h else (self.hdr_top + self.hdr_h + 30))
        # assign rows within each lane
        for n in self.nodes:
            if n["lane"] not in self.lane_idx or n["col"] not in self.col_idx:
                raise ValueError(f"{self.id}: node {n['id']} has unknown lane/col")
            n["_w"], n["_h"] = self.node_size(n)
        occ = {}
        for n in self.nodes:
            li, ci, span = self.lane_idx[n["lane"]], self.col_idx[n["col"]], n.get("span", 1)
            if ci + span > ncols:
                raise ValueError(f"{self.id}: node {n['id']} spans past the last column")
            r = n.get("row")
            if r is None:
                r = 0
                while any(occ.get((li, r, c)) for c in range(ci, ci + span)):
                    r += 1
            for c in range(ci, ci + span):
                if occ.get((li, r, c)):
                    raise ValueError(f"{self.id}: {n['id']} collides with {occ[(li, r, c)]} in lane {n['lane']} row {r}")
                occ[(li, r, c)] = n["id"]
            n["_row"] = r
        # row heights
        y = self.lanes_top
        self.lane_geo = []
        for li, lane in enumerate(self.lanes):
            rows = sorted({n["_row"] for n in self.nodes if self.lane_idx[n["lane"]] == li})
            maxr = max(rows) if rows else -1
            rh = []
            for r in range(maxr + 1):
                hs = [n["_h"] for n in self.nodes if self.lane_idx[n["lane"]] == li and n["_row"] == r]
                rh.append(max(hs) if hs else 0)
            lane_h = self.lane_pad * 2 + sum(rh) + self.row_gap * max(0, len([h for h in rh if h]) - 1)
            lane_h = max(lane_h, lane.get("min_h", 120))
            # label needs room too
            lab_lines = wrap_lines(lane["name"], self.label_w - 40, True) + (wrap_lines(lane.get("sub", ""), self.label_w - 40) if lane.get("sub") else 0)
            lane_h = max(lane_h, ceil10(lab_lines * LINE + 40 + (LANE_TILE_H if lane.get("icon") else 0)))
            lane_h = ceil10(lane_h)
            # row tops (centre rows vertically when lane is taller than content)
            content = sum(rh) + self.row_gap * max(0, len([h for h in rh if h]) - 1)
            ry = y + max(self.lane_pad, (lane_h - content) // 2)
            ry = ceil10(ry - 9) if ry % 10 else ry
            row_tops = []
            for r in range(maxr + 1):
                row_tops.append(ry)
                if rh[r]:
                    ry += rh[r] + self.row_gap
            self.lane_geo.append({"top": y, "h": lane_h, "rows": row_tops, "rh": rh})
            y += lane_h
        self.height = y + self.s.get("opts", {}).get("bottom", 40)
        for n in self.nodes:
            li, ci = self.lane_idx[n["lane"]], self.col_idx[n["col"]]
            lg = self.lane_geo[li]
            rt, rhh = lg["rows"][n["_row"]], lg["rh"][n["_row"]]
            n["_x"] = self.col_x(ci)
            top = rt + (rhh - n["_h"]) / 2
            n["_y"] = int(round(top / 10.0) * 10)
        self.check_overlaps()

    def check_overlaps(self):
        ns = self.nodes
        for i in range(len(ns)):
            a = ns[i]
            for b in ns[i + 1:]:
                if a["_x"] < b["_x"] + b["_w"] and b["_x"] < a["_x"] + a["_w"] and a["_y"] < b["_y"] + b["_h"] and b["_y"] < a["_y"] + a["_h"]:
                    raise ValueError(f"{self.id}: boxes overlap {a['id']} {b['id']}")

    # ---------------- routing ----------------
    def route_all(self):
        W, H = self.width // G + 1, self.height // G + 1
        self.GW, self.GH = W, H
        blocked = bytearray(W * H)
        infl = 1  # cells of clearance around boxes
        self.box_cells = {}
        for n in self.nodes:
            x1, y1 = n["_x"] // G - infl, n["_y"] // G - infl
            x2, y2 = (n["_x"] + n["_w"]) // G + infl, (n["_y"] + n["_h"]) // G + infl
            for gx in range(max(0, x1), min(W, x2 + 1)):
                for gy in range(max(0, y1), min(H, y2 + 1)):
                    blocked[gy * W + gx] = 1
        top_cell = self.lanes_top // G
        for gx in range(W):
            for gy in range(0, top_cell):
                blocked[gy * W + gx] = 1
        self.blocked = blocked
        self.used_h = bytearray(W * H)
        self.used_v = bytearray(W * H)
        # pin assignment
        sides = {}
        for e in self.edges:
            a, b = self.nid[e["f"]], self.nid[e["t"]]
            fs, ts = e.get("fs"), e.get("ts")
            ca, cb = self.col_idx[a["col"]], self.col_idx[b["col"]]
            la, lb = self.lane_idx[a["lane"]], self.lane_idx[b["lane"]]
            a_right = a["_x"] + a["_w"]
            if not fs or not ts:
                if b["_x"] >= a_right:
                    dfs, dts = "r", "l"
                elif b["_x"] + b["_w"] <= a["_x"]:
                    dfs, dts = "b", "b"
                elif b["_y"] >= a["_y"] + a["_h"]:
                    dfs, dts = "b", "t"
                else:
                    dfs, dts = "t", "b"
                fs, ts = fs or dfs, ts or dts
            e["_fs"], e["_ts"] = fs, ts
            sides.setdefault((a["id"], fs), []).append((e, "f"))
            sides.setdefault((b["id"], ts), []).append((e, "t"))
        for (nid, side), lst in sides.items():
            n = self.nid[nid]

            def other_key(item):
                e, role = item
                o = self.nid[e["t"] if role == "f" else e["f"]]
                if side in ("l", "r"):
                    return (o["_y"] + o["_h"] / 2, o["_x"])
                return (o["_x"] + o["_w"] / 2, o["_y"])
            def sort_key(item):
                e, role = item
                o = e.get("ford") if role == "f" else e.get("tord")
                return (0, o, 0) if o is not None else (1, 0, other_key(item))
            lst.sort(key=sort_key)
            k = len(lst)
            for i, (e, role) in enumerate(lst):
                if side in ("l", "r"):
                    lo, hi = n["_y"] + 10, n["_y"] + n["_h"] - 10
                    span = hi - lo
                    py = lo + span * (i + 1) / (k + 1)
                    py = int(round(py / G) * G)
                    px = n["_x"] if side == "l" else n["_x"] + n["_w"]
                else:
                    lo, hi = n["_x"] + 20, n["_x"] + n["_w"] - 20
                    span = hi - lo
                    px = lo + span * (i + 1) / (k + 1)
                    px = int(round(px / G) * G)
                    py = n["_y"] if side == "t" else n["_y"] + n["_h"]
                e["_p" + role] = (px, py)
        n = len(self.edges)
        base = sorted(range(n), key=lambda i: (self.edges[i].get("prio", 0), self._est_len(self.edges[i])))
        orders = [base, list(reversed(base)), list(range(n)), list(reversed(range(n)))]
        rng = random.Random(7)
        for _ in range(self.s.get("opts", {}).get("tries", 30)):
            o = list(range(n))
            rng.shuffle(o)
            orders.append(o)
        best = None
        for ai, order in enumerate(orders):
            res = self._attempt(order, ai)
            if res is None:
                continue
            score = (res["cross"], res["bends"], res["len"])
            if best is None or score < best[0]:
                best = (score, res)
            if best[0][0] == 0:
                break
        if best is None:
            raise ValueError(f"{self.id}: routing failed")
        self.crossings = best[0][0]
        for i, pts in best[1]["paths"].items():
            self.edges[i]["_pts"] = pts
        if self.crossings:
            self.notes.append(f"{self.id}: {self.crossings} crossing(s) left")

    def _attempt(self, order, seed):
        W, H = self.GW, self.GH
        self.used_h = bytearray(W * H)
        self.used_v = bytearray(W * H)
        if seed == 0:
            self.noise = None
        else:
            r = random.Random(seed)
            self.noise = [r.random() * 0.4 for _ in range(W * H)]
        paths, marks = {}, {}
        for i in order:
            res = self.route(self.edges[i])
            if res is None:
                return None
            paths[i], marks[i] = res
        for _ in range(4):
            bad = self._crossing_edges(paths)
            if not bad:
                break
            for i in sorted(bad):
                self._unmark(marks[i])
                res = self.route(self.edges[i])
                if res is None:
                    self._mark(marks[i])
                    continue
                paths[i], marks[i] = res
        cross = len(self._crossings(paths))
        bends = sum(len(p) - 2 for p in paths.values())
        length = sum(abs(x2 - x1) + abs(y2 - y1) for p in paths.values() for (x1, y1), (x2, y2) in zip(p, p[1:]))
        return {"cross": cross, "bends": bends, "len": length, "paths": paths}

    def _mark(self, ml):
        for idx, hv in ml:
            if hv:
                self.used_h[idx] = min(255, self.used_h[idx] + 1)
            else:
                self.used_v[idx] = min(255, self.used_v[idx] + 1)

    def _unmark(self, ml):
        for idx, hv in ml:
            if hv:
                self.used_h[idx] = max(0, self.used_h[idx] - 1)
            else:
                self.used_v[idx] = max(0, self.used_v[idx] - 1)

    @staticmethod
    def _segs(p):
        return [((x1, y1), (x2, y2)) for (x1, y1), (x2, y2) in zip(p, p[1:])]

    def _crossings(self, paths):
        out = []
        items = [(i, self._segs(p)) for i, p in paths.items()]
        for ai in range(len(items)):
            ia, sa = items[ai]
            for bi in range(ai + 1, len(items)):
                ib, sb = items[bi]
                for a1, a2 in sa:
                    for b1, b2 in sb:
                        ah, bh = a1[1] == a2[1], b1[1] == b2[1]
                        if ah == bh:
                            continue
                        hs, vs = ((a1, a2), (b1, b2)) if ah else ((b1, b2), (a1, a2))
                        hy = hs[0][1]
                        hx1, hx2 = sorted((hs[0][0], hs[1][0]))
                        vx = vs[0][0]
                        vy1, vy2 = sorted((vs[0][1], vs[1][1]))
                        if hx1 < vx < hx2 and vy1 < hy < vy2:
                            out.append((ia, ib))
        return out

    def _crossing_edges(self, paths):
        bad = set()
        for a, b in self._crossings(paths):
            bad.add(a)
            bad.add(b)
        return bad

    def _est_len(self, e):
        (x1, y1), (x2, y2) = e["_pf"], e["_pt"]
        return abs(x1 - x2) + abs(y1 - y2)

    DIRS = {"r": (1, 0), "l": (-1, 0), "t": (0, -1), "b": (0, 1)}

    def route(self, e):
        best = None
        for m in (12, 30, 80, 10000):
            r = self._route(e, m)
            if r is None:
                continue
            pts, ml, g, crossed = r
            if not crossed:
                if best is not None:
                    self._unmark(best[1])
                self._mark(ml)
                return pts, ml
            if best is None or g < best[2]:
                best = (pts, ml, g)
        if best is None:
            return None
        self._mark(best[1])
        return best[0], best[1]

    def _route(self, e, margin):
        W, H = self.GW, self.GH
        blocked, uh, uv = self.blocked, self.used_h, self.used_v
        noise = self.noise
        (sx, sy), (tx, ty) = e["_pf"], e["_pt"]
        dsx, dsy = self.DIRS[e["_fs"]]
        dtx, dty = self.DIRS[e["_ts"]]
        stub = 2
        s = (sx // G + dsx * stub, sy // G + dsy * stub)
        t = (tx // G + dtx * stub, ty // G + dty * stub)
        sdir = (dsx, dsy)
        tdir = (-dtx, -dty)
        for (gx, gy) in (s, t):
            if not (0 <= gx < W and 0 <= gy < H):
                raise ValueError(f"{self.id}: edge {e['f']}->{e['t']} stub leaves the canvas")
        lox = max(0, min(s[0], t[0]) - margin)
        hix = min(W - 1, max(s[0], t[0]) + margin)
        loy = max(0, min(s[1], t[1]) - margin)
        hiy = min(H - 1, max(s[1], t[1]) + margin)
        TURN, CROSS, NEAR = 12, 400, 3
        start = (s[0], s[1], sdir)
        openh = [(0, 0, start)]
        best = {start: 0}
        prev = {}
        goal = None
        cnt = 0
        while openh:
            f, g, st = heapq.heappop(openh)
            if best.get(st, 1e18) < g:
                continue
            x, y, d = st
            if (x, y) == t and d == tdir:
                goal = st
                break
            cnt += 1
            if cnt > 150000:
                break
            cur = y * W + x
            for nd in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if nd == (-d[0], -d[1]):
                    continue
                nx, ny = x + nd[0], y + nd[1]
                if not (lox <= nx <= hix and loy <= ny <= hiy):
                    continue
                idx = ny * W + nx
                if blocked[idx] and (nx, ny) != t:
                    continue
                horiz = nd[1] == 0
                if horiz and uh[idx]:
                    continue
                if (not horiz) and uv[idx]:
                    continue
                c = 1.0
                if nd != d:
                    c += TURN
                    if uh[cur] or uv[cur]:
                        continue
                if horiz and uv[idx]:
                    c += CROSS
                if (not horiz) and uh[idx]:
                    c += CROSS
                if horiz:
                    if (ny > 0 and uh[idx - W]) or (ny < H - 1 and uh[idx + W]):
                        c += NEAR
                else:
                    if (nx > 0 and uv[idx - 1]) or (nx < W - 1 and uv[idx + 1]):
                        c += NEAR
                if noise is not None:
                    c += noise[idx]
                ng = g + c
                nst = (nx, ny, nd)
                if ng < best.get(nst, 1e18):
                    best[nst] = ng
                    prev[nst] = st
                    h = abs(nx - t[0]) + abs(ny - t[1])
                    heapq.heappush(openh, (ng + h, ng, nst))
        if goal is None:
            return None
        cells = []
        st = goal
        while st in prev:
            cells.append(st)
            st = prev[st]
        cells.append(st)
        cells.reverse()
        pts = [(sx, sy)] + [(c[0] * G, c[1] * G) for c in cells] + [(tx, ty)]
        ml = []
        for a_, b_ in zip(cells, cells[1:]):
            hv = a_[1] == b_[1]
            ml.append((a_[1] * W + a_[0], hv))
            ml.append((b_[1] * W + b_[0], hv))
        for (px, py), (dx, dy) in (((sx, sy), (dsx, dsy)), ((tx, ty), (dtx, dty))):
            cx, cy = px // G, py // G
            for k in range(stub + 1):
                x_, y_ = cx + dx * k, cy + dy * k
                if 0 <= x_ < W and 0 <= y_ < H:
                    ml.append((y_ * W + x_, dy == 0))
        crossed = False
        for a_, b_ in zip(cells, cells[1:]):
            idx = b_[1] * W + b_[0]
            if a_[1] == b_[1] and uv[idx]:
                crossed = True
            if a_[0] == b_[0] and uh[idx]:
                crossed = True
        return simplify(pts), ml, best[goal], crossed

    # ---------------- render ----------------
    def render(self):
        pid = self.id
        out = []
        sc = self.s.get("scale_note", "")
        aria = html.escape(self.s.get("title", "Lane diagram"))
        out.append(f'<div class="lanes" id="{pid}" data-w="{self.width}" data-h="{self.height}" data-lw="{self.label_w}">')
        out.append('<div class="lanes-tools"><span class="lanes-hint">Read left → right. It fits your window; a bigger window shows it bigger. Press 100% to read up close, then scroll sideways.</span>'
                   f'<span class="zoom" role="group" aria-label="Zoom this diagram"><button type="button" data-zoom="out" data-for="{pid}" aria-label="Zoom out">−</button>'
                   f'<button type="button" data-zoom="reset" data-for="{pid}">100%</button><button type="button" data-zoom="in" data-for="{pid}" aria-label="Zoom in">+</button>'
                   f'<button type="button" data-zoom="fit" data-for="{pid}">Fit</button></span></div>')
        out.append('<div class="lanes-body">')
        # frozen lane labels
        out.append(f'<div class="lane-labels" style="width:{self.label_w}px"><div class="ll-stage" style="width:{self.label_w}px;height:{self.height}px">'
                   f'<div class="ll-canvas" style="width:{self.label_w}px;height:{self.height}px">')
        out.append(f'<div class="ll-corner" style="top:{self.hdr_top}px;height:{self.lanes_top - self.hdr_top - 20}px"><span>Steps →</span><span>Who or what ↓</span></div>')
        for li, lane in enumerate(self.lanes):
            lg = self.lane_geo[li]
            tone = lane.get("tone", "plain")
            sub = f'<span class="ll-sub">{lane["sub"]}</span>' if lane.get("sub") else ""
            red = " rd" if lane.get("red") else ""
            li_ = f'<span class="lli lli-lane">{icon_svg(lane["icon"])}</span>' if lane.get("icon") else ""
            out.append(f'<div class="ll tone-{tone}{red}" style="top:{lg["top"]}px;height:{lg["h"]}px">{li_}<span class="ll-name">{lane["name"]}</span>{sub}</div>')
        out.append('</div></div></div>')
        # scrolling canvas
        out.append(f'<div class="viewport" tabindex="0" aria-label="{aria}. Scroll sideways to follow every step.">'
                   f'<div class="stage" style="width:{self.width}px;height:{self.height}px"><div class="canvas" style="width:{self.width}px;height:{self.height}px">')
        for li, lane in enumerate(self.lanes):
            lg = self.lane_geo[li]
            tone = lane.get("tone", "plain")
            out.append(f'<div class="band tone-{tone}{" alt" if li % 2 else ""}" style="top:{lg["top"]}px;height:{lg["h"]}px;width:{self.width}px"></div>')
        for i, c in enumerate(self.cols):
            x = self.col_x(i)
            lv = f'<span class="lv">{c["lv"]}</span>' if c.get("lv") else ""
            red = " rd" if c.get("red") else ""
            out.append(f'<div class="colhead{red}" style="left:{x}px;top:{self.hdr_top}px;width:{self.bw}px;height:{self.hdr_h}px">{lv}<span>{c["name"]}</span></div>')
            if c.get("ex"):
                out.append(f'<div class="colex{red}" style="left:{x}px;top:{self.ex_top}px;width:{self.bw}px;height:{self.ex_h}px">{c["ex"]}</div>')
        # svg
        out.append(f'<svg class="wires" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}" aria-hidden="true">')
        out.append("<defs>")
        for k, col in (("flow", "#16181c"), ("login", "#7b3fa0"), ("data", "#2e7d32"), ("red", "#c62828"), ("grey", "#7a7f87")):
            out.append(f'<marker id="{pid}-m-{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')
        out.append("</defs>")
        labels = []
        for ei, e in enumerate(self.edges):
            k = e.get("k", "flow")
            mk = {"flow": "flow", "email": "flow", "login": "login", "data": "data", "move": "red", "loop": "grey", "dash": "flow"}.get(k, "flow")
            cls = f"w-{k}" + (" w-red" if e.get("red") else "")
            if e.get("red") and mk == "flow":
                mk = "red"
            pts = " ".join(f"{x},{y}" for x, y in e["_pts"])
            eid = f"{pid}-e{ei}"
            out.append(f'<polyline id="{eid}" class="{cls}" data-source="{pid}-{e["f"]}" data-target="{pid}-{e["t"]}" points="{pts}" marker-end="url(#{pid}-m-{mk})"/>')
            if e.get("n") or e.get("lbl"):
                labels.append((eid, e))
        placed = []
        for eid, e in labels:
            out.append(self.place_label(eid, e, placed))
        out.append("</svg>")
        for n in self.nodes:
            out.append(self.render_node(n))
        out.append("</div></div></div>")  # canvas stage viewport
        out.append("</div>")  # lanes-body
        key = [e for e in self.edges if e.get("key")]
        if key:
            out.append('<ol class="wire-key">')
            for e in sorted(key, key=lambda e: int(re.sub(r"\D", "", str(e.get("n", "0"))) or 0)):
                red = ' class="rd"' if e.get("red") else ""
                out.append(f'<li{red}><span class="wk-n">{e.get("n", "")}</span><span class="wk-k wk-{e.get("k", "flow")}"></span><span>{e["key"]}</span></li>')
            out.append("</ol>")
        out.append("</div>")
        return "\n".join(out)

    def place_label(self, eid, e, placed):
        pts = e["_pts"]
        segs = []
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            segs.append((abs(x2 - x1) + abs(y2 - y1), (x1, y1), (x2, y2)))
        segs_sorted = sorted(segs, key=lambda s: -s[0])
        boxes = [(n["_x"] - 4, n["_y"] - 4, n["_x"] + n["_w"] + 4, n["_y"] + n["_h"] + 4) for n in self.nodes]
        txt = str(e.get("n", "")) if e.get("n") else ""
        lbl = e.get("lbl", "")
        cls = "wl" + (" wl-red" if e.get("red") else "") + f" wl-{e.get('k', 'flow')}"

        def hits(r):
            x1, y1, x2, y2 = r
            for b in boxes + placed:
                if x1 < b[2] and b[0] < x2 and y1 < b[3] and b[1] < y2:
                    return True
            return False
        if txt:
            R = 17
            for L, (x1, y1), (x2, y2) in segs_sorted:
                if L < 2 * R + 20:
                    continue
                for frac in (0.5, 0.35, 0.65, 0.25, 0.75):
                    cx = x1 + (x2 - x1) * frac
                    cy = y1 + (y2 - y1) * frac
                    r = (cx - R - 2, cy - R - 2, cx + R + 2, cy + R + 2)
                    if not hits(r):
                        placed.append(r)
                        tw = text_w(txt, True)
                        return (f'<g class="{cls}" data-for="{eid}"><circle cx="{cx:.0f}" cy="{cy:.0f}" r="{R}"/>'
                                f'<text x="{cx:.0f}" y="{cy + 7:.0f}" text-anchor="middle">{html.escape(txt)}</text></g>')
            self.notes.append(f"{self.id}: no room for callout {txt} on {e['f']}->{e['t']}")
            return ""
        tw = text_w(lbl, False) + 12
        for L, (x1, y1), (x2, y2) in segs_sorted:
            horiz = y1 == y2
            if horiz and L >= tw + 16:
                cx = (x1 + x2) / 2
                r = (cx - tw / 2, y1 - 30, cx + tw / 2, y1 - 4)
                if not hits(r):
                    placed.append(r)
                    return f'<text class="{cls} wl-text" data-for="{eid}" x="{cx:.0f}" y="{y1 - 9}" text-anchor="middle">{html.escape(lbl)}</text>'
            if not horiz and L >= 60:
                cy = (y1 + y2) / 2
                r = (x1 + 6, cy - 14, x1 + 6 + tw, cy + 14)
                if not hits(r):
                    placed.append(r)
                    return f'<text class="{cls} wl-text" data-for="{eid}" x="{x1 + 10}" y="{cy + 7:.0f}" text-anchor="start">{html.escape(lbl)}</text>'
        self.notes.append(f"{self.id}: label '{lbl}' did not fit on {e['f']}->{e['t']}")
        return ""

    def render_node(self, n):
        pid = self.id
        kind = n.get("kind", "fix")
        cls = ["bx", f"k-{kind}"]
        if n.get("red"):
            cls.append("rd")
        if n.get("fx"):
            cls.append("made-up")
        if n.get("detail"):
            cls.append("has-detail")
        attrs = f'id="{pid}-{n["id"]}" class="{" ".join(cls)}" style="left:{n["_x"]}px;top:{n["_y"]}px;width:{n["_w"]}px;height:{n["_h"]}px"'
        if n.get("detail"):
            attrs += f' tabindex="0" role="button" data-detail="{pid}-d-{n["id"]}" aria-label="{html.escape(plain(n["t"]))}: show details below"'
        num = f'<span class="bn">{n["n"]}</span>' if n.get("n") else ""
        ico = icon_svg(n["icon"]) if n.get("icon") else ""
        body = f'<span class="bb">{n["b"]}</span>' if n.get("b") else ""
        parts = []
        for k, v in tag_list(n):
            ti = tag_icon(self.tag_icons, k, v)
            parts.append(f'<span class="tg tg-{k}">{icon_svg(ti, "tgi") if ti else ""}{v}</span>')
        tags = "".join(parts)
        tags = f'<span class="tgs">{tags}</span>' if tags else ""
        return f'<div {attrs}><span class="bt">{num}{ico}{n["t"]}</span>{body}{tags}</div>'

    def details_html(self, heading="Step details · click a box above to jump here"):
        items = [n for n in self.nodes if n.get("detail")]
        if not items:
            return ""

        def key(n):
            return (self.col_idx[n["col"]], self.lane_idx[n["lane"]], n["_row"])
        items.sort(key=key)
        out = [f'<div class="details"><h3 class="details-h">{heading}</h3><div class="dgrid">']
        for n in items:
            red = " rd" if n.get("red") else ""
            num = f'<span class="bn">{n["n"]}</span>' if n.get("n") else ""
            ln = self.lanes[self.lane_idx[n["lane"]]]
            lane = ln["name"]
            lic = f'<span class="lli tone-{ln.get("tone", "plain")}">{icon_svg(ln["icon"])}</span>' if ln.get("icon") else ""
            nic = icon_svg(n["icon"]) if n.get("icon") else ""
            out.append(f'<article class="dcard{red}" id="{self.id}-d-{n["id"]}"><h4>{num}{nic}{n["t"]}</h4>'
                       f'<p class="dwhere">{lic}{html.escape(plain(lane))}</p><div class="dbody">{n["detail"]}</div>'
                       f'<button type="button" class="dshow" data-show="{self.id}-{n["id"]}">Show in the diagram ↑</button></article>')
        out.append("</div></div>")
        return "\n".join(out)


def simplify(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if p == out[-1]:
            continue
        if len(out) >= 2:
            (x0, y0), (x1, y1) = out[-2], out[-1]
            if (x0 == x1 == p[0]) or (y0 == y1 == p[1]):
                out[-1] = p
                continue
        out.append(p)
    return out


def render(spec, details=True, details_heading=None):
    d = LaneDiagram(spec)
    h = d.render()
    if details:
        h += "\n" + (d.details_html(details_heading) if details_heading else d.details_html())
    return h, d
