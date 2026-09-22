"""
brain.py — turns a typed/spoken sentence into an action call.

Matching is simple keyword/pattern based on purpose: it's transparent,
easy to extend, and doesn't need any external NLP dependency to work.
To add a new capability:
  1. Write the function in actions.py
  2. Register a pattern for it below in `interpret()`
"""

import re
import actions
from config import ASSISTANT_NAME, CONFIRM_DESTRUCTIVE_ACTIONS

# Commands that need a "yes" before running
PENDING_CONFIRMATION = {"value": None}


def interpret(text: str) -> str:
    t = text.strip().lower()

    if not t:
        return "I didn't catch that."

    # Handle a pending confirmation first
    if PENDING_CONFIRMATION["value"]:
        action = PENDING_CONFIRMATION["value"]
        PENDING_CONFIRMATION["value"] = None
        if t in ("yes", "y", "confirm", "do it"):
            return action()
        else:
            return "Cancelled."

    # Greetings / identity
    if t in ("hello", "hi", "hey", "hi jarvis", "hello jarvis"):
        return f"At your service."

    if "who are you" in t or "what are you" in t:
        return f"I'm {ASSISTANT_NAME}, your desktop assistant."

    # Open app: "open firefox", "launch spotify", "start terminal"
    m = re.match(r"(open|launch|start)\s+(.+)", t)
    if m:
        return actions.open_app(m.group(2))

    # Close app: "close firefox", "quit spotify", "kill terminal"
    m = re.match(r"(close|quit|kill|stop)\s+(.+)", t)
    if m:
        return actions.close_app(m.group(2))

    if t in ("list apps", "what apps do you know", "show apps"):
        return actions.list_apps()

    # Volume
    if "volume up" in t or "increase volume" in t or "louder" in t:
        return actions.volume("up")
    if "volume down" in t or "decrease volume" in t or "quieter" in t:
        return actions.volume("down")
    if "mute" in t:
        return actions.volume("mute")

    # System info
    if "system status" in t or "system info" in t or "how are you running" in t or "stats" in t:
        return actions.system_info()

    # Screenshot
    if "screenshot" in t or "take a picture of my screen" in t:
        return actions.take_screenshot()

    # Lock
    if "lock" in t and "screen" in t:
        return actions.lock_screen()

    # Shutdown / restart — dangerous, so confirm first
    if "shut down" in t or "shutdown" in t or "power off" in t:
        if CONFIRM_DESTRUCTIVE_ACTIONS:
            PENDING_CONFIRMATION["value"] = actions.shutdown
            return "Shut down the system? Type 'yes' to confirm."
        return actions.shutdown()

    if "restart" in t or "reboot" in t:
        if CONFIRM_DESTRUCTIVE_ACTIONS:
            PENDING_CONFIRMATION["value"] = actions.restart
            return "Restart the system? Type 'yes' to confirm."
        return actions.restart()

    # Web search: "search for python tutorials", "google cat pictures"
    m = re.match(r"(search( for)?|google)\s+(.+)", t)
    if m:
        return actions.search_web(m.group(3))

    # Help
    if t in ("help", "commands", "what can you do"):
        return (
            "Try: 'open <app>', 'close <app>', 'list apps', 'volume up/down/mute', "
            "'system status', 'screenshot', 'lock screen', 'search for <query>', "
            "'shutdown', 'restart'."
        )

    return "I didn't understand that. Say 'help' to see what I can do."
