"""
actions.py — the actual work JARVIS does on your Linux machine.

Every function here takes no positional args beyond what's parsed from the
command, returns a short string that gets spoken/shown back to the user,
and never raises — errors are caught and turned into a friendly message.

This is the layer you extend when you add new capabilities (including,
later, smart-home calls — just add a function here and register it in
brain.py's COMMANDS table).
"""

import subprocess
import shutil
import datetime
import os

from config import APP_ALIASES


def _run(cmd, background=False):
    """Run a shell command. background=True launches and returns immediately."""
    try:
        if background:
            subprocess.Popen(
                cmd,
                shell=isinstance(cmd, str),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            return True, ""
        else:
            result = subprocess.run(
                cmd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return False, str(e)


def open_app(name: str) -> str:
    name = name.strip().lower()
    cmd = APP_ALIASES.get(name, name)  # fall back to raw name if not aliased

    if shutil.which(cmd.split()[0]) is None:
        return (
            f"I can't find '{cmd}' on this system. "
            f"Install it, or add the correct command name to config.py's APP_ALIASES."
        )

    ok, _ = _run(cmd, background=True)
    return f"Opening {name}." if ok else f"Something went wrong opening {name}."


def close_app(name: str) -> str:
    name = name.strip().lower()
    cmd = APP_ALIASES.get(name, name)
    proc_name = cmd.split()[0]

    ok, out = _run(["pkill", "-f", proc_name])
    if ok:
        return f"Closed {name}."
    return f"{name} doesn't appear to be running."


def list_apps() -> str:
    names = sorted(set(APP_ALIASES.keys()))
    return "Registered apps: " + ", ".join(names)


def volume(direction: str) -> str:
    """direction: 'up', 'down', or 'mute'"""
    if shutil.which("pactl") is None:
        return "pactl isn't installed, so I can't control volume. Try: sudo apt install pulseaudio-utils"

    if direction == "up":
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"])
        return "Volume up."
    elif direction == "down":
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"])
        return "Volume down."
    elif direction == "mute":
        _run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        return "Toggled mute."
    return "I didn't understand that volume command."


def system_info() -> str:
    lines = []
    try:
        with open("/proc/loadavg") as f:
            load = f.read().split()[0]
        lines.append(f"CPU load: {load}")
    except Exception:
        pass

    try:
        with open("/proc/meminfo") as f:
            mem = f.read()
        total = int([l for l in mem.splitlines() if l.startswith("MemTotal")][0].split()[1])
        avail = int([l for l in mem.splitlines() if l.startswith("MemAvailable")][0].split()[1])
        used_pct = round((1 - avail / total) * 100, 1)
        lines.append(f"RAM used: {used_pct}%")
    except Exception:
        pass

    try:
        disk = shutil.disk_usage("/")
        used_pct = round(disk.used / disk.total * 100, 1)
        lines.append(f"Disk used: {used_pct}%")
    except Exception:
        pass

    return " | ".join(lines) if lines else "Couldn't read system stats."


def take_screenshot() -> str:
    tool = None
    for candidate in ("gnome-screenshot", "scrot", "spectacle", "flameshot"):
        if shutil.which(candidate):
            tool = candidate
            break
    if not tool:
        return "No screenshot tool found. Try: sudo apt install gnome-screenshot"

    folder = os.path.expanduser("~/Pictures")
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"jarvis_{datetime.datetime.now():%Y%m%d_%H%M%S}.png")

    if tool == "gnome-screenshot":
        ok, _ = _run(["gnome-screenshot", "-f", filename])
    elif tool == "scrot":
        ok, _ = _run(["scrot", filename])
    elif tool == "spectacle":
        ok, _ = _run(["spectacle", "-b", "-n", "-o", filename])
    else:
        ok, _ = _run(["flameshot", "full", "-p", filename])

    return f"Screenshot saved to {filename}." if ok else "Screenshot failed."


def lock_screen() -> str:
    for cmd in (["loginctl", "lock-session"], ["gnome-screensaver-command", "-l"], ["xdg-screensaver", "lock"]):
        if shutil.which(cmd[0]):
            ok, _ = _run(cmd)
            if ok:
                return "Screen locked."
    return "Couldn't find a way to lock the screen on this system."


def shutdown() -> str:
    ok, _ = _run(["systemctl", "poweroff"])
    return "Shutting down." if ok else "Couldn't shut down (permissions?)."


def restart() -> str:
    ok, _ = _run(["systemctl", "reboot"])
    return "Restarting." if ok else "Couldn't restart (permissions?)."


def search_web(query: str) -> str:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    ok, _ = _run(["xdg-open", url], background=True)
    return f"Searching for '{query}'." if ok else "Couldn't open a browser."
