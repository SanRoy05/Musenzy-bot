# ── RETIRED ───────────────────────────────────────────────────────────────────
#
# This file has been superseded by the handlers/ package introduced in the
# permission-system refactor. It is no longer imported anywhere.
#
# All handler logic lives in:
#   handlers/__init__.py   — register() entry point
#   handlers/play.py       — /play, /vplay, inline callbacks
#   handlers/controls.py   — /pause, /resume, /skip, /stop, /vol, /loop, /queue, /now
#   handlers/settings.py   — /playmode, /auth, /unauth, /authlist
#   handlers/sudo.py       — /addsudo, /delsudo, /sudolist
#   handlers/misc.py       — /start, /help
#
# Safe to delete this file.
# ─────────────────────────────────────────────────────────────────────────────
