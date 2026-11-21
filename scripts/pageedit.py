"""Edit mode for v4 diagram pages: type over or delete any text, then Cmd+S writes the page back into its own file.

How it works
- apply(html) adds an "Edit page" button to the stamp bar, the edit bar's CSS and JS, a page-build meta (12-char hash
  of the page as built) and lets the CSP talk to the local save server (scripts/save_server.py, http://127.0.0.1:8765).
  Safe to call twice.
- In the browser, Cmd+S (Ctrl+S) cleans a copy of the page (no edit state, no popover, no night mode, first tab on,
  typed notes kept) and POSTs it to the save server, which writes the file and keeps <file>.bak. If the file on disk
  was rebuilt since the page was opened, it refuses and offers "Save anyway". If the server is not running, it
  downloads <name>-edited.html instead.
- Start the server with: python3 scripts/save_server.py --root <folder that holds your pages>
- write_page(path, html) is how generators write pages: it refuses to overwrite a file whose bytes changed since the
  last build (someone saved edits in the browser) until those edits are folded into the source and it is rebuilt with
  FORCE=1.

Stdlib only.
"""
import hashlib
import json
import os
import re
import tempfile

DAEMON = "http://127.0.0.1:8765"   # scripts/save_server.py
STATE = os.path.join(os.path.expanduser("~"), ".cache", "feel-the-plan", "page-builds.json")

OLD_NOTE_HEAD = "Your notes (not saved, reply in chat)"
NEW_NOTE_HEAD = "Your notes (⌘S saves them into this page)"
OLD_NOTE_PH = "Type while you review, then paste into chat. Reloading loses it."
NEW_NOTE_PH = "Type while you review. ⌘S saves your notes into this page; you can still paste them into chat."

EDIT_BTN = '<button class="nightbtn editbtn" id="pgedit" type="button" aria-pressed="false">Edit page</button>'

EDIT_CSS = r"""
.editbtn[aria-pressed=true]{background:#fff;color:#16181c;border-color:#fff}
html.pg-editing .frame{outline:2px dashed var(--red);outline-offset:6px;padding-bottom:200px}
html.pg-editing .frame:focus{outline:2px dashed var(--red)}
#pgbar{position:fixed;left:0;right:0;bottom:0;z-index:80;display:flex;flex-wrap:wrap;gap:12px 16px;align-items:center;padding:12px 24px;
 background:var(--card);color:var(--ink);border-top:2px solid var(--red);font-size:20px;line-height:1.4}
#pgbar[hidden],#pgbar [hidden]{display:none}
#pgbar p{margin:0;flex:1 1 360px;font-size:20px}
#pgbar .pgmsg:empty{display:none}
#pgbar .pgbtns{display:inline-flex;gap:8px;flex-wrap:wrap}
#pgbar button{font-size:20px;border:1px solid var(--rule);background:var(--page);color:var(--ink);border-radius:8px;padding:6px 16px;
 transition:background-color 150ms var(--ease)}
#pgbar button.pgmain{background:var(--ink);color:var(--page);border-color:var(--ink)}
@media print{#pgbar{display:none}html.pg-editing .frame{outline:0}}
"""

EDIT_JS = r"""
(function () {
  "use strict";
  var DAEMON = "http://127.0.0.1:8765";
  var LOCK = "nav, button, summary, textarea, input, select, svg, .lanes, .canvas, [data-goto], [data-go]";
  var HELP = "Editing: click any text to change it, or select it and press Delete. ⌘Z undoes. ⌘S saves into this file.";
  var STALE = "Not saved: this page was rebuilt after you opened it. Reload to see the new version, or Save anyway to keep your version.";
  var doc = document, html = doc.documentElement, frame = doc.querySelector(".frame"), btn = doc.getElementById("pgedit");
  var editing = false, dirty = false, saving = false;
  function meta(src) {
    var m = /<meta name="page-build" content="([^"]*)"/.exec(src || "");
    return m ? m[1] : "";
  }
  var mine = (doc.querySelector('meta[name="page-build"]') || { getAttribute: function () { return ""; } }).getAttribute("content") || "";

  var bar = doc.createElement("div");
  bar.id = "pgbar"; bar.setAttribute("data-pg-edit", ""); bar.hidden = true;
  bar.setAttribute("role", "region"); bar.setAttribute("aria-label", "Edit page");
  bar.innerHTML = '<p class="pghelp"></p><p class="pgmsg" role="status" aria-live="polite"></p><span class="pgbtns">'
    + '<button type="button" class="pgmain" data-pg="save">Save (⌘S)</button>'
    + '<button type="button" data-pg="force" hidden>Save anyway</button>'
    + '<button type="button" data-pg="stop">Stop editing</button></span>';
  doc.body.appendChild(bar);
  var help = bar.querySelector(".pghelp"), msgEl = bar.querySelector(".pgmsg");
  var forceBtn = bar.querySelector('[data-pg="force"]'), stopBtn = bar.querySelector('[data-pg="stop"]');
  help.textContent = HELP;

  function sync() {
    bar.hidden = !editing && !msgEl.textContent;
    help.hidden = !editing; stopBtn.hidden = !editing;
    if (btn) { btn.setAttribute("aria-pressed", editing ? "true" : "false"); btn.textContent = editing ? "Stop editing" : "Edit page"; }
  }
  function say(t) { msgEl.textContent = t || ""; sync(); }

  function start() {
    if (!frame || editing) return;
    Array.prototype.forEach.call(frame.querySelectorAll(LOCK), function (el) {
      if (el.hasAttribute("contenteditable")) return;
      el.setAttribute("contenteditable", "false"); el.setAttribute("data-pg-lock", "");
    });
    frame.setAttribute("contenteditable", "true");
    html.classList.add("pg-editing");
    editing = true; say(""); forceBtn.hidden = true;
  }
  function stop() {
    if (!frame) return;
    Array.prototype.forEach.call(frame.querySelectorAll("[data-pg-lock]"), function (el) {
      el.removeAttribute("contenteditable"); el.removeAttribute("data-pg-lock");
    });
    frame.removeAttribute("contenteditable");
    html.classList.remove("pg-editing");
    editing = false; sync();
  }
  function stopAsked() {
    if (!dirty) { stop(); return; }
    save(false).then(function (r) { if (r !== "stale") stop(); });
  }

  /* ---------- the clean copy that goes into the file ---------- */
  function cleanCopy() {
    var root = html.cloneNode(true), i;
    var live = doc.querySelectorAll("textarea"), copy = root.querySelectorAll("textarea");
    for (i = 0; i < copy.length && i < live.length; i++) {
      if (copy[i].id === "notesout") { copy[i].textContent = ""; copy[i].hidden = true; }
      else copy[i].textContent = live[i].value;
    }
    function drop(sel) { Array.prototype.forEach.call(root.querySelectorAll(sel), function (el) { if (el.parentNode) el.parentNode.removeChild(el); }); }
    drop("[data-pg-edit]"); drop("body > .hpop"); drop("#hpop");
    Array.prototype.forEach.call(root.querySelectorAll(".pinned, .lit"), function (el) {
      el.classList.remove("pinned", "lit"); if (!el.getAttribute("class")) el.removeAttribute("class");
    });
    Array.prototype.forEach.call(root.querySelectorAll('.bx[aria-expanded="true"]'), function (el) { el.setAttribute("aria-expanded", "false"); });
    root.classList.remove("night", "pg-editing");
    if (!root.getAttribute("class")) root.removeAttribute("class");
    var st = (root.getAttribute("style") || "").replace(/--vw\s*:[^;]*;?\s*/g, "").trim();
    if (st) root.setAttribute("style", st); else root.removeAttribute("style");
    Array.prototype.forEach.call(root.querySelectorAll(".flow-tabs"), function (nav) {
      Array.prototype.forEach.call(nav.querySelectorAll("button[data-go]"), function (b, k) {
        b.classList.toggle("on", k === 0); b.setAttribute("aria-selected", k === 0 ? "true" : "false"); b.setAttribute("tabindex", k === 0 ? "0" : "-1");
      });
    });
    Array.prototype.forEach.call(root.querySelectorAll("section.screen"), function (s, k) { s.classList.toggle("on", k === 0); });
    Array.prototype.forEach.call(root.querySelectorAll("[contenteditable]"), function (el) { el.removeAttribute("contenteditable"); });
    Array.prototype.forEach.call(root.querySelectorAll("[data-pg-lock]"), function (el) { el.removeAttribute("data-pg-lock"); });
    var eb = root.querySelector("#pgedit"); if (eb) { eb.setAttribute("aria-pressed", "false"); eb.textContent = "Edit page"; }
    var nb = root.querySelector("#v4night"); if (nb) { nb.setAttribute("aria-pressed", "false"); nb.textContent = "Night mode"; }
    var out = [];
    Array.prototype.forEach.call(doc.childNodes, function (n) {
      if (n.nodeType === 8) out.push("<!--" + n.data + "-->");
      else if (n.nodeType === 10) out.push("<!doctype " + (n.name || "html") + ">");
      else if (n === html) out.push(root.outerHTML);
    });
    return out.join("\n") + "\n";
  }

  /* ---------- where the file is ---------- */
  function where(root) {
    root = String(root || "").replace(/\\/g, "/").replace(/\/+$/, "");
    var p = location.pathname || "", dec, rel, abs;
    try { dec = decodeURIComponent(p); } catch (e) { return null; }
    if (location.protocol === "file:") {
      if (/^\/[A-Za-z]:\//.test(dec)) { dec = dec.slice(1); p = p.slice(1); }
      if (dec.replace(/\\/g, "/").indexOf(root + "/") !== 0) return null;
      rel = dec.replace(/\\/g, "/").slice(root.length + 1); abs = p;
    } else if (/^(127\.0\.0\.1|localhost):8765$/.test(location.host)) {
      rel = dec.replace(/^\/+/, ""); abs = encodeURI(root + "/" + rel);
    } else return null;
    return { rel: rel, abs: abs, name: rel.split("/").pop() };
  }
  function fileName() { var n = (location.pathname || "page.html").split("/").pop() || "page.html"; try { n = decodeURIComponent(n); } catch (e) {} return n; }
  function hhmm() { var d = new Date(); return ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2); }

  function download(text, why) {
    var name = fileName().replace(/\.html?$/i, "") + "-edited.html";
    try {
      var url = URL.createObjectURL(new Blob([text], { type: "text/html" }));
      var a = doc.createElement("a");
      a.href = url; a.download = name; a.setAttribute("data-pg-edit", ""); a.hidden = true;
      doc.body.appendChild(a); a.click(); doc.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
      dirty = false;
      say("Not saved into the file: " + why + ". Your edited copy was downloaded as " + name + " instead.");
    } catch (e) {
      say("Not saved: " + why + ", and the download failed too. Keep this tab open and copy your changes out by hand.");
    }
    return "download";
  }
  function Refused(why) { this.why = why; }

  function save(force) {
    if (saving) return Promise.resolve("busy");
    saving = true;
    var text = cleanCopy(), loc = null;
    function done(r) { saving = false; return r; }
    function post() {
      return fetch(DAEMON + "/save", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: loc.abs, html: text, force: !!force }) }).then(function (r) {
        if (r.ok) return r.json();
        return r.text().then(function (t) { var w = t; try { w = JSON.parse(t).message || t; } catch (e) {} throw new Refused(String(w).slice(0, 160) || ("error " + r.status)); });
      }).then(function (j) {
        if (!j || !j.ok) throw new Refused("it did not confirm the save");
        dirty = false; forceBtn.hidden = true;
        say("Saved into this file at " + hhmm() + ". The previous version is kept next to it as a .bak file.");
        return "saved";
      });
    }
    return fetch(DAEMON + "/health", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (h) {
      loc = where(h && h.root);
      if (!loc) throw new Refused("this file is outside the folder the save helper can write to");
      if (force) return post();
      var rel = loc.rel.split("/").map(encodeURIComponent).join("/");
      return fetch(DAEMON + "/" + rel, { cache: "no-store" }).then(function (r) {
        if (!r.ok) throw new Refused("the save helper could not read this file (error " + r.status + ")");
        return r.text();
      }).then(function (disk) {
        if (meta(disk) !== mine) { forceBtn.hidden = false; say(STALE); return "stale"; }
        return post();
      });
    }).then(done, function (e) {
      saving = false;
      if (e instanceof Refused) return download(text, "the save helper said no (" + e.why + ")");
      return download(text, "the save helper on this computer isn't running");
    });
  }

  if (btn) btn.addEventListener("click", function () { if (editing) stopAsked(); else start(); });
  bar.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-pg]"); if (!b) return;
    var k = b.getAttribute("data-pg");
    if (k === "save") save(false); else if (k === "force") save(true); else if (k === "stop") stopAsked();
  });
  doc.addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && !e.altKey && (e.key === "s" || e.key === "S")) { e.preventDefault(); save(false); }
  }, true);
  if (frame) frame.addEventListener("input", function (e) {
    if (!editing) return;
    var t = e.target;
    if (t && t.closest && t.closest("textarea, input, select")) return;
    dirty = true;
  });
  window.addEventListener("beforeunload", function (e) { if (dirty) { e.preventDefault(); e.returnValue = ""; return ""; } });
  sync();
})();
"""


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def apply(html):
    """Add edit mode to a finished v4 page. Unchanged if already applied or if the page has no stamp buttons."""
    if 'name="page-build"' in html or 'id="pgedit"' in html or '<div class="stampbtns">' not in html:
        return html
    build = _sha(html.encode("utf-8"))[:12]
    h = html.replace('<div class="stampbtns">', '<div class="stampbtns">' + EDIT_BTN, 1)
    h = h.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="page-build" content="' + build + '">', 1)
    h = re.sub(r'(<meta http-equiv="Content-Security-Policy" content=")([^"]*)(")',
               lambda m: m.group(1) + (m.group(2) if "connect-src" in m.group(2) else m.group(2).rstrip("; ") + "; connect-src " + DAEMON) + m.group(3),
               h, count=1)
    h = h.replace(OLD_NOTE_HEAD, NEW_NOTE_HEAD).replace(OLD_NOTE_PH, NEW_NOTE_PH)
    h = h.replace("</style>", EDIT_CSS + "</style>", 1)
    i = h.rfind("</body>")
    if i >= 0:
        h = h[:i] + "<script>" + EDIT_JS + "</script>\n" + h[i:]
    return h


def _load_state():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _atomic(path, data, mode="w"):
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix="." + os.path.basename(path) + ".tmp-")
    try:
        with os.fdopen(fd, mode, encoding="utf-8", newline="") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)  # mkstemp makes 0600; a page stays readable like any other file
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_page(path, html, force=None):
    """Write a built page atomically, unless the file holds edits saved in the browser since the last build."""
    ap = os.path.abspath(path)
    state = _load_state()
    forced = bool(force) or os.environ.get("FORCE") == "1"
    if not forced and os.path.isfile(ap) and ap in state:
        with open(ap, "rb") as f:
            now = _sha(f.read())
        if now != state[ap]:
            raise SystemExit(
                f"Not written: {ap} was edited and saved in the browser after the last build.\n"
                f"  1. Read the edits: git diff -- {ap}  (or compare it with {ap}.bak)\n"
                f"  2. Fold them into the source or spec this page is built from.\n"
                f"  3. Rebuild with FORCE=1 to write over the file.")
    _atomic(ap, html)
    state[ap] = _sha(html.encode("utf-8"))
    _atomic(STATE, json.dumps(state, indent=1, sort_keys=True))
    return ap
