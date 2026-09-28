#!/usr/bin/env python3
"""KHSEO capture_rendered — receive one rendered DOM from a real browser and save it to a file.

Why: sites behind bot shields (Reblaze, Cloudflare, DataDome…) block the raw probe *and*
headless browsers, but the host's real browser session gets through. This one-shot receiver
lets any host that can run JavaScript in a browser tab hand the rendered DOM to seo_probe.py.

Usage:
    python capture_rendered.py out.html            # prints a JS snippet, waits for one POST
    # run the snippet in the browser tab (e.g. via the host's javascript tool), then:
    python seo_probe.py https://site/page --rendered out.html

Security: binds to 127.0.0.1 only, requires a random one-time token in the URL, accepts a single
POST (≤ 10 MB), then exits. Nothing is fetched or executed; the saved HTML is untrusted data.
"""
from __future__ import annotations

import argparse
import http.server
import secrets
import sys
import threading

MAX_BODY = 10_000_000


def serve_once(out_path: str, timeout: float = 300.0, port: int = 0) -> tuple[str, threading.Event, http.server.HTTPServer]:
    token = secrets.token_urlsafe(16)
    done = threading.Event()

    class Handler(http.server.BaseHTTPRequestHandler):
        def _cors(self):
            # Constant "*", never the request's Origin: reflecting a client-supplied header is a
            # response-splitting/CORS risk (CodeQL py/http-response-splitting). The capture
            # fetch sends no credentials, so "*" is sufficient; the URL token is the access control.
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            # Chrome Private Network Access: public page -> loopback needs this opt-in.
            self.send_header("Access-Control-Allow-Private-Network", "true")

        def do_OPTIONS(self):
            self.send_response(204 if self.path == f"/{token}" else 404)
            self._cors()
            self.end_headers()

        def do_POST(self):
            try:
                n = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                n = -1
            if n <= 0 or n > MAX_BODY:
                self.close_connection = True  # don't read an oversized/unknown body
                self.send_response(413)
                self._cors()
                self.end_headers()
                return
            data = self.rfile.read(n)  # always drain, so a rejected client gets a clean response
            if self.path != f"/{token}" or done.is_set():
                self.send_response(404)
                self.end_headers()
                return
            with open(out_path, "wb") as fh:
                fh.write(data)
            self.send_response(200)
            self._cors()
            self.end_headers()
            self.wfile.write(b"saved")
            done.set()

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/{token}"
    return url, done, srv


def snippet(url: str) -> str:
    return (f"fetch('{url}', {{method: 'POST', headers: {{'Content-Type': 'text/plain'}}, "
            f"body: '<!doctype html>\\n' + document.documentElement.outerHTML}})"
            f".then(r => r.text())")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Receive one rendered DOM from a browser tab")
    ap.add_argument("out", help="file to write the rendered HTML to")
    ap.add_argument("--timeout", type=float, default=300.0, help="seconds to wait (default 300)")
    ap.add_argument("--port", type=int, default=0, help="loopback port (default: random)")
    a = ap.parse_args(argv)
    url, done, srv = serve_once(a.out, a.timeout, a.port)
    print("Run this in the browser tab that shows the rendered page:\n")
    print(snippet(url), flush=True)
    ok = done.wait(a.timeout)
    srv.shutdown()
    srv.server_close()
    if not ok:
        print(f"\ncapture_rendered: no DOM received within {a.timeout:.0f}s", file=sys.stderr)
        return 1
    print(f"\nsaved rendered DOM -> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
