# 🎵 Musenzy — Telegram Group Voice Chat Music Bot

A powerful, production-ready Telegram music bot that streams YouTube audio and video directly into group voice chats using a **dual-client architecture** (bot + userbot).

---

## ✨ Features

| Feature | Details |
|---|---|
| **Play audio** | `/play <name or URL>` — searches YouTube or plays a direct link |
| **Play video** | `/vplay <name or URL>` — up to 480p video in voice chat |
| **Search results** | Shows top 5 results as inline buttons; user taps to choose |
| **Playlist support** | Queues up to `MAX_QUEUE_SIZE` tracks from a YouTube playlist URL |
| **Queue management** | `/queue` — view all queued tracks |
| **Now playing** | `/now` — see current track info and volume |
| **Playback controls** | `/pause`, `/resume`, `/skip`, `/stop` |
| **Volume control** | `/vol <0-200>` |
| **Loop mode** | `/loop` — toggle repeat on the current track |
| **Auto-advance** | Automatically plays the next track when one ends |
| **Auto-leave** | Userbot leaves VC when queue is empty |
| **Disk cleanup** | Downloaded files are deleted after playback |
| **Admin control** | Playback commands restricted to group admins or ADMIN_IDS |

---

## 🏗 Architecture

```
User sends /play  ──▶  Bot client (handles commands)
                             │
                             ▼
                     Downloads audio via yt-dlp
                             │
                             ▼
                  Userbot joins Group Voice Chat
                  (appears as your account name)
                             │
                             ▼
                  PyTgCalls streams audio/video
```

- **Bot client** — registered with `@BotFather`, receives all `/commands`.  
- **Userbot client** — your personal Telegram account (session string), joins the VC and streams media. It will appear in the participant list with your account's name.

---

## 📋 Prerequisites

| Requirement | Where to get it |
|---|---|
| Python 3.10+ | [python.org](https://python.org) |
| `ffmpeg` | `apt install ffmpeg` / `brew install ffmpeg` / [ffmpeg.org](https://ffmpeg.org) |
| Telegram API credentials | [my.telegram.org](https://my.telegram.org) → API development tools |
| Bot token | [@BotFather](https://t.me/BotFather) on Telegram |
| Session string | Run `generate_session.py` (see below) |

---

## 🚀 Quick Start (Local)

### 1. Clone & install dependencies

```bash
git clone https://github.com/yourname/musenzy-bot.git
cd musenzy-bot

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Get Telegram API credentials

1. Go to [my.telegram.org](https://my.telegram.org) and log in.
2. Click **"API development tools"**.
3. Create a new application — name it anything.
4. Copy the **App api_id** and **App api_hash**.

### 3. Get a Bot token

1. Open [@BotFather](https://t.me/BotFather) on Telegram.
2. Send `/newbot` and follow the prompts.
3. Copy the token it gives you.

### 4. Generate a userbot session string

```bash
python generate_session.py
```

- Enter your `API_ID` and `API_HASH` when prompted.
- Pyrogram will send an OTP to your Telegram account — enter it.
- If you have two-step verification enabled, enter your password too.
- The script prints a long session string — **copy it**.

> ⚠️ The session string grants full access to your Telegram account. **Never share it or commit it to git.**

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in all values:

```env
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
SESSION_STRING=BQABc...very long string...
ADMIN_IDS=123456789,987654321
MAX_QUEUE_SIZE=20
DEFAULT_VOLUME=100
DOWNLOAD_DIR=/tmp/musenzy
```

### 6. Run

```bash
python bot.py
```

You should see:
```
✅ Musenzy is live. Press Ctrl+C to stop.
```

---

## 📡 Deploy to Render

1. Push your repo to GitHub (make sure `.env` is in `.gitignore` — it is by default).
2. Go to [render.com](https://render.com) → **New** → **Blueprint**.
3. Connect your GitHub repo — Render will detect `render.yaml` automatically.
4. In the **Environment** tab, add all the secret variables (`API_ID`, `API_HASH`, `BOT_TOKEN`, `SESSION_STRING`, `ADMIN_IDS`).
5. Click **Apply** — Render builds the Docker image and starts the worker.

> The `render.yaml` already configures a **worker** service (no HTTP port required) with a 1 GB ephemeral disk mounted at `/tmp/musenzy` for downloads.

---

## 🚂 Deploy to Railway

1. Push your repo to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Select your repository.
4. Click **Variables** and add all env vars from `.env.example`.
5. Railway auto-detects the `Dockerfile` and deploys.

> Railway uses the `CMD` from the `Dockerfile` (`python -u bot.py`) — no extra config needed.

---

## 🤖 Bot Commands Reference

| Command | Description | Admin only |
|---|---|---|
| `/play <query or URL>` | Play audio (search or direct URL/playlist) | ❌ |
| `/vplay <query or URL>` | Play video up to 480p | ❌ |
| `/pause` | Pause the current stream | ✅ |
| `/resume` | Resume a paused stream | ✅ |
| `/skip` | Skip the current track | ✅ |
| `/stop` | Stop playback, clear queue, leave VC | ✅ |
| `/vol <0-200>` | Set playback volume | ✅ |
| `/loop` | Toggle loop mode on current track | ✅ |
| `/queue` | Show the current queue | ❌ |
| `/now` | Show now-playing info | ❌ |

---

## 📁 Project Structure

```
musenzy-bot/
├── bot.py               # Entry point — starts both clients
├── config.py            # Env var loading & validation
├── handlers.py          # All bot command & callback handlers
├── player.py            # PyTgCalls playback engine (uses userbot)
├── queue_manager.py     # In-memory per-chat queue & state
├── ytdl.py              # yt-dlp search, info, audio/video download
├── permissions.py       # Admin check (group admin or ADMIN_IDS)
├── generate_session.py  # Standalone script to generate session string
├── Dockerfile           # Docker image with ffmpeg
├── render.yaml          # Render.com deploy config
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ How It Works

1. **`/play` or `/vplay`** with a text query → bot searches YouTube and shows 5 results as inline buttons.
2. The user taps a button → bot downloads the audio/video in the background.
3. The **userbot** joins the group voice chat and streams the downloaded file via `PyTgCalls`.
4. When the track ends, `on_stream_end` fires → the next track in queue starts automatically.
5. If the queue is empty, the userbot leaves the voice chat.
6. The downloaded file is deleted from disk after each track finishes.

---

## 🛡 Security Notes

- The `SESSION_STRING` has the same power as logging into your Telegram account. Store it only in environment variables / a secrets manager — never in code or commit history.
- Revoke a compromised session at **Telegram → Settings → Privacy and Security → Active Sessions**.
- Consider using a dedicated Telegram account for the userbot rather than your primary account.

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| `NoActiveGroupCall` | Start a voice chat in the group before using `/play`. |
| `AlreadyJoinedError` | The userbot is already in VC — this is handled automatically. |
| `ffmpeg not found` | Install ffmpeg and ensure it is in your `PATH`. |
| Session string expired | Re-run `generate_session.py` and update `SESSION_STRING`. |
| Bot doesn't respond | Check that `BOT_TOKEN` is correct and the bot is added to the group. |
| No results | yt-dlp may be rate-limited — update it: `pip install -U yt-dlp`. |

---

## 📜 License

MIT — do whatever you want, just don't be evil.
