#!/usr/bin/env python3
"""Type into a machine's firmware through an IP-KVM, without the KVM's web UI.

Two backends:
  ssh-hidg  KVMs with root SSH and a USB HID gadget at /dev/hidg0 (Luckfox PicoKVM, and other
            Linux-gadget KVMs). Writes 8-byte boot-keyboard reports over SSH.
  pikvm     PiKVM / BliKVM / anything speaking the kvmd HTTP API (POST /api/hid/events/send_key).

Each token is a named key, a chord, or text:
  hid-keys.py --machine server Del                 # one key
  hid-keys.py --machine server --repeat 30 Del     # tap during POST to catch the setup prompt
  hid-keys.py --machine server Down Down Enter     # sequence
  hid-keys.py --machine server F10 Enter           # save and exit on most AMI/Insyde setups
  hid-keys.py --machine server text:abc123 Enter   # ASCII text (US layout)

--machine reads the KVM entry from machines.json in the overlay (scripts/overlay-paths.sh dir).
--kvm-host / --backend override it. pikvm credentials come from env KVMD_USER / KVMD_PASSWD.
Stdlib only.
"""
import argparse
import json
import os
import ssl
import string
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

MODS = {"ctrl": 0x01, "shift": 0x02, "alt": 0x04, "meta": 0x08, "win": 0x08,
        "rctrl": 0x10, "rshift": 0x20, "ralt": 0x40, "rmeta": 0x80}

KEYS = {"enter": 0x28, "esc": 0x29, "escape": 0x29, "backspace": 0x2A, "tab": 0x2B,
        "space": 0x2C, "insert": 0x49, "home": 0x4A, "pageup": 0x4B, "del": 0x4C,
        "delete": 0x4C, "end": 0x4D, "pagedown": 0x4E, "right": 0x4F, "left": 0x50,
        "down": 0x51, "up": 0x52, "printscreen": 0x46, "minus": 0x2D, "plus": 0x2E}
KEYS.update({f"f{i}": 0x3A + i - 1 for i in range(1, 13)})
KEYS.update({c: 0x04 + i for i, c in enumerate(string.ascii_lowercase)})
KEYS.update({str(d): 0x1E + (d - 1) for d in range(1, 10)})
KEYS["0"] = 0x27

PUNCT = {"-": (0x2D, 0), "_": (0x2D, 1), "=": (0x2E, 0), "+": (0x2E, 1), "[": (0x2F, 0),
         "{": (0x2F, 1), "]": (0x30, 0), "}": (0x30, 1), "\\": (0x31, 0), "|": (0x31, 1),
         ";": (0x33, 0), ":": (0x33, 1), "'": (0x34, 0), '"': (0x34, 1), "`": (0x35, 0),
         "~": (0x35, 1), ",": (0x36, 0), "<": (0x36, 1), ".": (0x37, 0), ">": (0x37, 1),
         "/": (0x38, 0), "?": (0x38, 1), " ": (0x2C, 0), "!": (0x1E, 1), "@": (0x1F, 1),
         "#": (0x20, 1), "$": (0x21, 1), "%": (0x22, 1), "^": (0x23, 1), "&": (0x24, 1),
         "*": (0x25, 1), "(": (0x26, 1), ")": (0x27, 1)}

# kvmd key names (web KeyboardEvent.code style) for the pikvm backend
KVMD = {"enter": "Enter", "esc": "Escape", "escape": "Escape", "backspace": "Backspace",
        "tab": "Tab", "space": "Space", "insert": "Insert", "home": "Home", "pageup": "PageUp",
        "del": "Delete", "delete": "Delete", "end": "End", "pagedown": "PageDown",
        "right": "ArrowRight", "left": "ArrowLeft", "down": "ArrowDown", "up": "ArrowUp",
        "printscreen": "PrintScreen", "minus": "Minus", "plus": "Equal",
        "ctrl": "ControlLeft", "shift": "ShiftLeft", "alt": "AltLeft", "meta": "MetaLeft",
        "win": "MetaLeft", "rctrl": "ControlRight", "rshift": "ShiftRight", "ralt": "AltRight",
        "rmeta": "MetaRight"}
KVMD.update({f"f{i}": f"F{i}" for i in range(1, 13)})
KVMD.update({c: f"Key{c.upper()}" for c in string.ascii_lowercase})
KVMD.update({str(d): f"Digit{d}" for d in range(10)})


def overlay_dir():
    script = Path(__file__).with_name("overlay-paths.sh")
    return Path(subprocess.check_output(["bash", str(script), "dir"], text=True).strip())


def load_machine(name):
    f = overlay_dir() / "machines.json"
    if not f.exists():
        sys.exit(f"no machines.json at {f}; run the bios-profile skill first")
    data = json.loads(f.read_text())
    for m in data.get("machines", []):
        if m.get("name") == name or name in m.get("aliases", []):
            return m
    sys.exit(f"machine {name!r} not in {f}")


def parse(tok):
    """-> list of (modifier_names, key_name); key_name None = bare modifier tap."""
    if tok.startswith("text:"):
        out = []
        for ch in tok[5:]:
            if ch in PUNCT:
                code, shift = PUNCT[ch]
                key = next(k for k, v in KEYS.items() if v == code)
            elif ch.isupper():
                key, shift = ch.lower(), 1
            elif ch.lower() in KEYS:
                key, shift = ch, 0
            else:
                sys.exit(f"cannot type {ch!r}")
            out.append((["shift"] if shift else [], key))
        return out
    *mods, key = tok.lower().split("+")
    for x in mods:
        if x not in MODS:
            sys.exit(f"unknown modifier {x!r}")
    if key in MODS and not mods:
        return [([key], None)]
    if key not in KEYS:
        sys.exit(f"unknown key {key!r} (known: {', '.join(sorted(KEYS))})")
    return [(mods, key)]


def send_ssh_hidg(host, strokes, delay):
    lines = ["s=$(cat /sys/class/udc/*/state 2>/dev/null)",
             '[ "$s" = configured ] || { echo "USB link to host is \'$s\', not configured" >&2; exit 3; }']
    for mods, key in strokes:
        m = 0
        for x in mods:
            m |= MODS[x]
        k = KEYS[key] if key else 0
        lines.append(f"printf '\\x{m:02x}\\x00\\x{k:02x}\\x00\\x00\\x00\\x00\\x00' > /dev/hidg0")
        lines.append(f"sleep {delay}")
        lines.append("printf '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00' > /dev/hidg0")
        lines.append(f"sleep {delay}")
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", host, "sh -s"],
                       input="\n".join(lines) + "\n", text=True)
    return r.returncode


def send_pikvm(host, strokes, delay, insecure):
    user, pw = os.environ.get("KVMD_USER", "admin"), os.environ.get("KVMD_PASSWD")
    if not pw:
        sys.exit("set KVMD_PASSWD (and KVMD_USER if not admin)")
    ctx = ssl._create_unverified_context() if insecure else None
    base = host if host.startswith("http") else f"https://{host}"

    def key(name, state):
        req = urllib.request.Request(f"{base}/api/hid/events/send_key?key={name}&state={state}",
                                     method="POST", headers={"X-KVMD-User": user, "X-KVMD-Passwd": pw})
        urllib.request.urlopen(req, context=ctx, timeout=10).read()

    for mods, k in strokes:
        names = [KVMD[m] for m in mods] + ([KVMD[k]] if k else [])
        for n in names:
            key(n, "true")
        time.sleep(delay)
        for n in reversed(names):
            key(n, "false")
        time.sleep(delay)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tokens", nargs="+")
    ap.add_argument("--machine", help="machine name or alias in machines.json")
    ap.add_argument("--kvm-host", help="ssh target (root@host) or pikvm base URL")
    ap.add_argument("--backend", choices=["ssh-hidg", "pikvm"])
    ap.add_argument("--repeat", type=int, default=1, help="send the whole sequence N times")
    ap.add_argument("--delay", type=float, default=0.08, help="seconds between taps (default 0.08)")
    ap.add_argument("--insecure", action="store_true", help="pikvm: accept the self-signed cert")
    a = ap.parse_args()

    kvm = load_machine(a.machine).get("kvm", {}) if a.machine else {}
    host = a.kvm_host or kvm.get("ssh") or kvm.get("url")
    backend = a.backend or kvm.get("keys_backend")
    if not host or not backend:
        sys.exit("need a KVM: --machine with a kvm entry, or --kvm-host and --backend")

    strokes = [s for t in a.tokens for s in parse(t)] * a.repeat
    if backend == "ssh-hidg":
        sys.exit(send_ssh_hidg(host, strokes, a.delay))
    sys.exit(send_pikvm(host, strokes, a.delay, a.insecure or kvm.get("insecure_tls", False)))


if __name__ == "__main__":
    main()
