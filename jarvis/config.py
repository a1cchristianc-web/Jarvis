"""
JARVIS configuration.

APP_ALIASES maps spoken/typed names to the actual Linux command used to
launch that program. Add your own here as you install things.

Run `jarvis` with the command "list apps" to see everything registered.
"""

APP_ALIASES = {
    "firefox": "firefox",
    "browser": "firefox",
    "terminal": "x-terminal-emulator",
    "files": "nautilus",
    "file manager": "nautilus",
    "text editor": "gedit",
    "editor": "gedit",
    "calculator": "gnome-calculator",
    "settings": "gnome-control-center",
    "spotify": "spotify",
    "code": "code",
    "vscode": "code",
    "vlc": "vlc",
}

# Assistant name used in responses
ASSISTANT_NAME = "JARVIS"

# If True, JARVIS will ask for confirmation before shutdown/restart/logout
CONFIRM_DESTRUCTIVE_ACTIONS = True
