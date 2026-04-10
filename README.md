# Musenzy Music Bot 🎵

A powerful Telegram Music Bot built with Pyrogram and Py-TgCalls 2.2.x.
Inspired by AnonXMusic, rebuilt for maximum performance and simplicity.

## Features
- 🎵 Audio & Video streaming
- 🖼️ Beautiful now-playing cards
- 📝 Local JSON database
- ⏭️ Queue management
- 🐳 Docker support

## Environment Variables
- `API_ID` - Get from [my.telegram.org](https://my.telegram.org)
- `API_HASH` - Get from [my.telegram.org](https://my.telegram.org)
- `BOT_TOKEN` - Get from [@BotFather](https://t.me/BotFather)
- `SESSION` - Pyrogram V2 Session String
- `OWNER_ID` - Your Telegram User ID

## Deployment
```bash
docker build -t musenzy-bot .
docker run -d --env-file .env musenzy-bot
```

### Manual Run
```bash
pip install -r requirements.txt
python -m MusenzyMusic
```
