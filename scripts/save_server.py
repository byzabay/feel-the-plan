"""Tiny local save server for pages built with edit mode (pageedit.py). Stdlib only.

usage: python3 scripts/save_server.py [--root DIR] [--port 8765]

Open a page (file:// or http://127.0.0.1:8765/<path>), press Edit page, change text, press Cmd+S / Ctrl+S.
The page talks to this server:

  GET  /health        -> {"ok": true, "root": "<root>"}
  GET  /<rel path>    -> the .html file at <root>/<rel path> (the page uses it to spot a rebuild since it was opened)
  POST /save          JSON {"path": "<absolute path, may be URL-encoded>", "html": "<full document>", "force": bool}
                      -> {"ok": true, "path": ..., "backup": ...}, or {"ok": false, "message": ...} with a 4xx status

Safety: binds 127.0.0.1 only; checks the Host header; accepts browser requests only from file:// pages
(Origin "null") or from this server itself; writes only existing .html files that resolve inside --root
(no "..", no symlink escape); copies the old file to <file>.bak first, then replaces it atomically.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote

MAX_BODY = 20 * 1024 * 1024
ROOT = ""        # absolute root as given (reported to the page, which matches it against its own file path)
ROOT_REAL = ""   # resolved root, used for every containment check
PORT = 8765


def inside_root(path):
    """Resolved path if `path` is a .html file inside the root, else None."""
    real = os.path.realpath(path)
    try:
        if os.path.commonpath([real, ROOT_REAL]) != ROOT_REAL:
            return None
    except ValueError:
        return None
    if not real.lower().endswith(".html") or not os.path.isfile(real):
        return None
    return real


def atomic_write(path, text):
    d = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=d, prefix="." + os.path.basename(path) + ".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class Handler(BaseHTTPRequestHandler):
    server_version = "save_server"

    def allowed_origins(self):
        return ("null", f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}")

    def host_ok(self):
        return self.headers.get("Host", "") in (f"127.0.0.1:{PORT}", f"localhost:{PORT}")

    def origin_ok(self):
        o = self.headers.get("Origin")
        return o is None or o in self.allowed_origins()

    def cors(self):
        o = self.headers.get("Origin")
        if o in self.allowed_origins():
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def reply(self, code, obj=None, body=None, ctype="application/json"):
        data = body if body is not None else json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.cors()
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def fail(self, code, message):
        self.reply(code, {"ok": False, "message": message})

    def guard(self):
        if not self.host_ok():
            self.fail(403, "bad Host header")
            return False
        if not self.origin_ok():
            self.fail(403, "origin not allowed")
            return False
        return True

    def do_OPTIONS(self):
        if not self.guard():
            return
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_GET(self):
        if not self.guard():
            return
        p = self.path.split("?", 1)[0]
        if p in ("/", "/health"):
            return self.reply(200, {"ok": True, "root": ROOT})
        rel = unquote(p).lstrip("/")
        if ".." in rel.replace("\\", "/").split("/"):
            return self.fail(404, "not found")
        real = inside_root(os.path.join(ROOT_REAL, rel))
        if not real:
            return self.fail(404, "not found")
        with open(real, "rb") as f:
            self.reply(200, body=f.read(), ctype="text/html")

    do_HEAD = do_GET

    def do_POST(self):
        if not self.guard():
            return
        if self.path.split("?", 1)[0].rstrip("/") != "/save":
            return self.fail(404, "only POST /save is supported")
        if (self.headers.get("Content-Type") or "").split(";")[0].strip().lower() != "application/json":
            return self.fail(415, "send JSON")
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self.fail(400, "bad Content-Length")
        if length <= 0 or length > MAX_BODY:
            return self.fail(413, f"body must be 1 to {MAX_BODY} bytes")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            raw, text = unquote(str(payload["path"])), payload["html"]
            if not isinstance(text, str):
                raise ValueError("html must be a string")
        except (ValueError, KeyError, TypeError, UnicodeDecodeError) as e:
            return self.fail(400, f"bad request: {e}")
        if not os.path.isabs(raw) or ".." in raw.replace("\\", "/").split("/"):
            return self.fail(403, "path must be absolute, with no '..'")
        real = inside_root(raw)
        if not real:
            return self.fail(403, "only existing .html files inside the root can be saved")
        backup = real + ".bak"
        try:
            shutil.copy2(real, backup)
            atomic_write(real, text)
        except OSError as e:
            return self.fail(500, f"write failed: {e.strerror}")
        self.reply(200, {"ok": True, "path": real, "backup": backup})

    def log_message(self, fmt, *args):
        pass


def main():
    global ROOT, ROOT_REAL, PORT
    ap = argparse.ArgumentParser(description="Local save server for edit-mode pages.")
    ap.add_argument("--root", default=os.getcwd(), help="folder whose .html files may be saved (default: current folder)")
    ap.add_argument("--port", type=int, default=8765, help="port (pages expect 8765)")
    a = ap.parse_args()
    ROOT = os.path.abspath(os.path.expanduser(a.root))
    ROOT_REAL = os.path.realpath(ROOT)
    PORT = a.port
    if not os.path.isdir(ROOT_REAL):
        sys.exit(f"root is not a folder: {ROOT}")
    srv = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"save_server: http://127.0.0.1:{PORT}  root={ROOT}  (Ctrl+C stops)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
