# JARVIS — Desktop Assistant

A lightweight desktop assistant for Linux that controls apps and system
functions through a dark, JARVIS-style GUI. Type commands (voice is
optional — see below).

## Quick start

```bash
# tkinter is usually preinstalled, but if not:
sudo apt install python3-tk

python3 main.py
```

That's it — no other dependencies required for text mode.

## What it can do out of the box

| Say / type                        | Does                                      |
|------------------------------------|--------------------------------------------|
| `open firefox`                     | Launches an app (see `config.py` aliases)  |
| `close firefox`                    | Kills a running app                        |
| `list apps`                        | Shows all registered app aliases           |
| `volume up` / `volume down` / `mute` | Adjusts system volume (needs `pactl`)    |
| `system status`                    | CPU load, RAM %, disk %                    |
| `screenshot`                       | Saves a screenshot to `~/Pictures`         |
| `lock screen`                      | Locks your session                         |
| `search for <query>`               | Opens a Google search in your browser      |
| `shutdown` / `restart`             | Powers off / reboots (asks to confirm)     |
| `help`                             | Lists commands                             |

## Adding your own apps

Edit `config.py`:

```python
APP_ALIASES = {
    "discord": "discord",
    "obs": "obs",
    ...
}
```

The key is what you'll type/say; the value is the actual Linux command
that launches it (find it with `which <program>` in a terminal).

## Adding new capabilities

1. Write a function in `actions.py` that does the work and returns a
   short string response.
2. Register a matching pattern for it in `brain.py`'s `interpret()`.

This is also where you'd plug in smart-home control later — e.g. add a
`smart_home.py` with calls to a Home Assistant or Hue REST API, then
route commands like "turn on the lights" to it from `brain.py`.

## Optional: voice control

Voice is off by default so the app has zero required dependencies. To
enable it:

```bash
sudo apt install portaudio19-dev python3-pyaudio
pip3 install SpeechRecognition pyttsx3 pyaudio
```

Once installed, restart `main.py` — a 🎤 button will appear next to Send.
Voice recognition uses Google's free web API by default (requires
internet); for fully offline recognition, look into swapping in
`pocketsphinx` inside `main.py`'s `on_voice()` method.

## Notes

- `shutdown`/`restart`/`lock screen` use `systemctl` / `loginctl`, which
  are standard on most modern Linux distros (systemd-based).
- Screenshot support auto-detects `gnome-screenshot`, `scrot`,
  `spectacle`, or `flameshot` — install whichever matches your desktop
  environment if none are found.
- Volume control uses `pactl` (PulseAudio/PipeWire). Install with
  `sudo apt install pulseaudio-utils` if missing.
