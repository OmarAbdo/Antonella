# Antonella — Roadmap

## Bugs / fixes
- [ ] **Fix Spotify and versioned app paths** — Discord and Spotify install into `app-1.x.x/` folders; glob resolution isn't finding them on all machines

## Quality of life
- [ ] **Auto-start with Windows** — register via Task Scheduler (runs as admin, no UAC prompt) or startup folder shortcut
- [ ] **Quieter startup** — configurable `STARTUP_MESSAGE` in settings; default to `"Ready."` or silence
- [ ] **Barge-in / interrupt** — if Antonella is speaking and the wake word is detected, cut TTS immediately and listen
- [ ] **"What can you do?"** — spoken command summary triggered by saying *"help"*

## Voice quality
- [ ] **HD voice option** — swap PowerShell SAPI for Kokoro or `edge-tts` (Microsoft neural voices, dramatically better quality, works offline after first use)
- [ ] **Porcupine wake word** — replace VAD+Whisper trigger with Picovoice Porcupine (free tier, custom wake words, far more reliable in noisy environments)

## New commands
- [ ] **Close apps** — *"close Chrome"* / *"close Spotify"* kills the process for any app Antonella can open; tracks what it launched so it knows what to close
- [ ] **Cancel any scheduled task** — *"cancel"* already works for shutdown; extend to cover sleep and hibernate timers too (currently only `shutdown /a` is wired up)
- [ ] **Reminders and timers** — *"remind me in 20 minutes to check the oven"* → Windows toast notification
- [ ] **Media control** — *"pause", "next track", "what's playing"* via Spotify's local HTTP API
- [ ] **Clipboard integration** — *"read my clipboard"* reads it aloud; *"copy that"* copies Antonella's last response
- [ ] **Custom user commands** — define *"when I say X, run Y"* entirely in `settings.py`; no Python knowledge needed

## Product / UX
- [ ] **System tray icon** — lives in the notification area (the `^` arrow near the clock), shows listening/speaking/idle state, right-click → Quit; replaces having to hunt for the process in Task Manager when auto-started
- [ ] **Voice exit** — *"Antonella, shut yourself down"* / *"exit"* / *"quit"* gracefully stops the process

## Codebase
- [ ] **Plugin architecture** — drop a `.py` file in `plugins/` and it auto-registers new intents; no changes to core files required
- [ ] **Unit tests for intent parser** — `intent.py` is pure functions; fast test suite that catches regressions when new commands are added
- [ ] **Structured logging** — rotating JSON logs instead of raw `.txt` files
- [ ] **YAML / env config** — move settings out of a Python file so non-developers can configure the assistant without touching code
- [ ] **Expose VAD / sensitivity constants** — `VAD_THRESHOLD`, `WAKE_CONFIDENCE` as named settings for tuning in noisy environments
