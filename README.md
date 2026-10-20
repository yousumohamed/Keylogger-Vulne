# Local Keystroke Visualizer

## What this is

A small Python tool that:

* Captures keyboard input on the machine it runs on using `pynput`.
* Serves a live dashboard at `http://127.0.0.1:8000` showing recent keystrokes with timestamps.
* Writes a plain-text log to `log.txt` next to the executable.
* Auto-refreshes the dashboard every 2 seconds via a small `http.server` + HTML/JS page.

It is intended for local, same-machine use only — e.g., demonstrating how `pynput` works, testing a keyboard hook, or watching your own typing. It is not a remote-monitoring tool.

---

## What this is NOT

* ❌ **Not a remote keylogger.** It does not phone home, does not connect to a VPS, and does not accept inbound connections from other machines.
* ❌ **Not hidden.** The process is visible in Task Manager; the dashboard is localhost-only.
* ❌ **Not a parental-control or employee-monitoring product.** For those use cases, use Microsoft Family Safety, Qustodio, Bark, or an MDM solution — they are legal, visible to the monitored user, and designed for that purpose.
* ❌ **Not safe to deploy on a machine you do not own or administer**, or on a machine used by another person without their informed consent. Doing so is illegal in most jurisdictions and is indistinguishable from malware.

---

## Requirements (development only)

On the machine where you build the `.exe`:

```powershell
python -m pip install pynput pyinstaller
```

The target machine needs nothing — no Python, no packages. The `.exe` is self-contained.

---

## Files

```text
keylg/
├── keylog_html.py         # main script
├── build_exe.ps1          # optional build helper (see below)
├── dist/
│   └── keylog_html.exe    # built executable
└── log.txt                # created at runtime, next to the exe
```

---

## Running from source

```powershell
cd C:\code\keylg
python .\keylog_html.py
```

Then open in a browser on the same machine:

```text
http://127.0.0.1:8000
```

Type anywhere — characters appear in the dashboard within ~2 seconds. Press `Ctrl+C` in the terminal to stop.

> **Note:** Use this mode for debugging. `--noconsole` (below) hides all errors; if something breaks, run from source first.

---

## Building the exe (Windows)

### One-liner (recommended)

PowerShell 7 does not use `^` for line continuation — use a single line:

```powershell
python -m PyInstaller --onefile --noconsole --hidden-import pynput.keyboard._win32 --hidden-import pynput.mouse._win32 keylog_html.py
```

The two `--hidden-import` flags are required. `pynput` loads its Windows backend dynamically via `importlib`, so PyInstaller cannot see it. Without these flags, the `.exe` builds fine but crashes at startup with:

```text
ModuleNotFoundError: No module named 'pynput.keyboard._win32'
```

### Build order (don't skip)

1. Build with `--console` first, run it, and confirm it works.
2. Rebuild with `--noconsole`.
3. Test the final `.exe` on the same machine before copying it anywhere.

### Multi-line version (PowerShell)

Backtick `` ` `` is the continuation character — no space after it:

```powershell
python -m PyInstaller --onefile --noconsole `
  --hidden-import pynput.keyboard._win32 `
  --hidden-import pynput.mouse._win32 `
  keylog_html.py
```

`^` is the CMD continuation character. Using it in PowerShell produces `Script file '^' does not exist` and `Missing expression after unary operator '--'`.

### Build output

```text
INFO: Building EXE from EXE-00.toc completed successfully.
Result: dist\keylog_html.exe (~10–30 MB).
```

---

## Running the exe

1. Copy `dist\keylog_html.exe` to the target machine (one you own/administer).
2. **Add the exe's folder to Windows Security exclusions before running:**
   * *Windows Security → Virus & threat protection → Manage settings → Exclusions → Add folder.*
   * PyInstaller `--onefile` + a global keyboard hook + a local HTTP server is a textbook malware heuristic — Defender will quarantine it otherwise. This is expected, not a bug.
3. Double-click the `.exe`.
4. Open on that same machine:
   ```text
   http://127.0.0.1:8000
   ```

`log.txt` is created in the same folder as the `.exe`. It appends across runs.

### Important: `127.0.0.1` is same-machine only

`127.0.0.1` means "this computer." The dashboard is reachable only from the machine running the `.exe`. Opening `http://127.0.0.1:8000` on a different laptop will not reach it — it will look for a server on that laptop and find nothing.

If you ever need LAN access (not recommended, and only on networks you trust, between machines you own), you would have to:

1. Change the bind address from `127.0.0.1` to `0.0.0.0` in the script.
2. Open firewall port `8000` on the host machine.
3. Browse to `http://<host LAN IP>:8000` from the other machine.

That change is out of scope for this README and is not needed for the tool's intended local use.

---

## Configuration

In `keylog_html.py`:

| Setting | Default | Meaning |
| :--- | :--- | :--- |
| `HTTPServer(("127.0.0.1", 8000), ...)` | `localhost, port 8000` | Where the dashboard listens |
| `MAX_ENTRIES = 2000` | `2000` | Max entries kept in memory (older ones drop off the dashboard but stay in `log.txt`) |
| `LOG_FILE` | `log.txt next to exe` | Where keystrokes are persisted |
| Refresh interval | `2000 ms` | How often the dashboard polls `/data` (in the HTML `<script>`) |

---

## Troubleshooting

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `Script file '^' does not exist` | Used CMD `^` in PowerShell | Use one line, or backtick `` ` `` |
| `Missing expression after unary operator '--'` | Pasted a multi-line command into PowerShell without continuation | Same as above |
| `keylog_html.py is not recognized` | PowerShell doesn't run scripts from CWD by default | Use `.\keylog_html.py` |
| Exe builds, crashes immediately | Missing `pynput` hidden imports | Add both `--hidden-import` flags |
| Exe builds, Defender quarantines it | PyInstaller + keyhook heuristic | Add folder to Defender exclusions |
| Dashboard shows "No keystrokes yet..." | Listener not started, or exe not running | Check Task Manager; run with `--console` to see errors |
| `log.txt` not created | Exe run from a read-only folder (e.g. Program Files) | Run from a user-writable folder |
| Dashboard works locally, not from another machine | By design — `127.0.0.1` is same-machine only | See "Important" section above |

---

## Legal / ethical notes (read before using)

* This tool captures every keystroke on the machine, including passwords, private messages, and financial data. Treat `log.txt` as sensitive.
* Only run it on a machine you own and administer.
* Do not deploy it on another person's device, or on a shared/school/work device, without explicit written authorization from the device owner and (where applicable) the user.
* In many jurisdictions, hidden monitoring of another person — even a family member — without their informed consent is illegal. If you need parental or employee monitoring, use a commercial product built for that purpose (Microsoft Family Safety, Qustodio, Bark, an MDM) which displays consent and complies with data-protection law.
* A hidden `--noconsole` keylogger that connects to a remote host is malware by definition, regardless of intent. This tool deliberately does not do that. Keep it that way.

---

## Cleanup

1. Stop the `.exe` (**Task Manager → End task**).
2. Delete `log.txt` and `dist\keylog_html.exe` when done.
3. If a crashed run left a temp folder behind: `%TEMP%\_MEI*` — safe to delete.
4. Remove the Defender exclusion you added.