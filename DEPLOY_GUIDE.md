# 🐝 Hive Telegram Bot — Deployment Guide

## What's in this folder
- `bot.py` — The bot's brain (all the code)
- `requirements.txt` — Libraries the bot needs
- `railway.toml` — Tells Railway how to run everything

---

## Step 1 — Get Your BotFather Token (2 mins)
1. Open Telegram and search **@BotFather**
2. Send `/newbot`
3. Choose a name: **Hive**
4. Choose a username: **HiveWeb3Bot** (must end in "bot")
5. BotFather sends you a token like:
   `7481920345:AAFxyz123abc...`
6. **Copy that token**

---

## Step 2 — Get Your Anthropic API Key (2 mins)
1. Go to **console.anthropic.com**
2. Click **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-...`)

---

## Step 3 — Add Your Tokens to the Code (10 seconds)
Open `bot.py` and find these two lines near the top:

```python
TELEGRAM_TOKEN = "PASTE_YOUR_BOTFATHER_TOKEN_HERE"
ANTHROPIC_API_KEY = "PASTE_YOUR_ANTHROPIC_API_KEY_HERE"
```

Replace the placeholder text with your actual tokens. Save the file.

---

## Step 4 — Deploy to Railway (5 mins)
1. Go to **railway.app** and sign up (free)
2. Click **New Project** → **Deploy from GitHub repo**
   - OR click **New Project** → **Empty Project** → drag and drop this folder
3. Railway detects the files automatically
4. Click **Deploy**
5. Wait ~1 minute for it to build

✅ When you see "Active" in Railway — your bot is live!

---

## Step 5 — Test Your Bot
1. Go to Telegram
2. Search your bot by username (e.g. @HiveWeb3Bot)
3. Send `/start`
4. Hive should respond! 🐝

---

## Bot Commands (already built in)
| Command | What it does |
|---|---|
| `/start` | Welcome message + instructions |
| `/beginner` | Switch to simple explanations |
| `/advanced` | Switch to technical depth |
| `/quiz` | Start a quiz question |
| `/compare` | Compare two coins or concepts |
| `/reset` | Clear conversation history |

---

## Troubleshooting
- **Bot not responding?** Check Railway logs for errors
- **Token error?** Make sure you pasted the full token with no spaces
- **API error?** Check your Anthropic account has credits

---

## Cost
- Railway free tier: ✅ Covers small bots easily
- Anthropic API: ~$0.003 per conversation (very cheap)
- For a growing community, budget ~$10-20/month total
