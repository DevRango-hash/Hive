import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
import os
import anthropic
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import random

# ============================================================
#  PASTE YOUR TOKENS HERE
# ============================================================
TELEGRAM_TOKEN = "PASTE_YOUR_BOTFATHER_TOKEN_HERE"
ANTHROPIC_API_KEY = "PASTE_YOUR_ANTHROPIC_API_KEY_HERE"
# ============================================================

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are Hive 🐝, a crypto and Web3 education assistant living inside Telegram.
Your personality is sharp, friendly, and knowledgeable — like a brilliant friend who knows everything about crypto.

Your capabilities:
1. EXPLAIN crypto topics clearly with simple language and relatable analogies
2. QUIZ MODE — generate multiple choice questions (A/B/C/D) silently rotating topics, wait for answers, then explain the correct answer
3. Answer any crypto/Web3 question naturally when asked

Rules:
- Never give financial advice or tell people to buy/sell
- Always be encouraging and patient
- Keep responses concise — no walls of text
- Use emojis sparingly but effectively
- When in quiz mode, just fire the question directly with no topic announcement
- If user specifies a quiz topic, quiz them on that topic specifically"""

QUIZ_TOPICS = [
    "Bitcoin", "Ethereum", "DeFi", "NFTs", "Web3", "Stablecoins",
    "Flatcoins", "Blockchain", "Smart Contracts", "DAOs",
    "Layer 2", "Gas Fees", "Crypto Wallets", "Mining", "Proof of Stake"
]

STARTER_BUTTONS = [
    [
        InlineKeyboardButton("⚡ What is Bitcoin?", callback_data="q_bitcoin"),
        InlineKeyboardButton("🔷 What is Ethereum?", callback_data="q_ethereum"),
    ],
    [
        InlineKeyboardButton("🏦 What is DeFi?", callback_data="q_defi"),
        InlineKeyboardButton("🖼️ What are NFTs?", callback_data="q_nfts"),
    ],
    [
        InlineKeyboardButton("🌐 What is Web3?", callback_data="q_web3"),
        InlineKeyboardButton("💵 What is a Stablecoin?", callback_data="q_stablecoin"),
    ],
    [
        InlineKeyboardButton("🔑 What is a Crypto Wallet?", callback_data="q_wallet"),
        InlineKeyboardButton("⛓️ What is Blockchain?", callback_data="q_blockchain"),
    ],
    [
        InlineKeyboardButton("🎯 Test My Knowledge", callback_data="q_quiz"),
    ]
]

BUTTON_QUESTIONS = {
    "q_bitcoin": "What is Bitcoin? Explain simply.",
    "q_ethereum": "What is Ethereum? Explain simply.",
    "q_defi": "What is DeFi? Explain simply.",
    "q_nfts": "What are NFTs? Explain simply.",
    "q_web3": "What is Web3? Explain simply.",
    "q_stablecoin": "What is a stablecoin? Explain simply.",
    "q_wallet": "What is a crypto wallet? Explain simply.",
    "q_blockchain": "What is blockchain? Explain simply.",
    "q_quiz": None,  # Triggers quiz mode
}

# Store per-user state
user_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "mode": "chat",
            "history": [],
            "saved_chats": [],
            "chat_number": 1,
        }
    return user_data[user_id]

def save_current_chat(user):
    if user["history"]:
        chat_title = f"Chat {user['chat_number']}"
        # Try to generate a title from first message
        if user["history"]:
            first_msg = user["history"][0]["content"]
            chat_title = f"Chat {user['chat_number']} — {first_msg[:30]}..."
        user["saved_chats"].append({
            "title": chat_title,
            "history": user["history"].copy()
        })
        user["chat_number"] += 1


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(STARTER_BUTTONS)
    await update.message.reply_text(
        "Gm! ☀️ I'm *Hive* — your Web3 knowledge companion.\n\n"
        "Pick a topic below to get started, or just ask me anything! 🐝",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# /new command — start fresh chat
async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    save_current_chat(user)
    user["history"] = []
    user["mode"] = "chat"
    keyboard = InlineKeyboardMarkup(STARTER_BUTTONS)
    await update.message.reply_text(
        "🔄 New chat started! Your previous conversation has been saved.\n\nWhat are we learning today? 🐝",
        reply_markup=keyboard
    )


# /history command — show saved chats
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user["saved_chats"]:
        await update.message.reply_text("📭 No saved chats yet. Start chatting and use /new to save and start fresh!")
        return

    history_text = "📚 *Your Saved Chats:*\n\n"
    for i, chat in enumerate(user["saved_chats"][-5:], 1):  # Show last 5 chats
        history_text += f"{i}. {chat['title']}\n"

    history_text += "\n_Showing your last 5 conversations._"
    await update.message.reply_text(history_text, parse_mode="Markdown")


# /quiz command
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    user["mode"] = "quiz"
    topic = random.choice(QUIZ_TOPICS)
    await handle_message_logic(update, context,
        override_text=f"Give me a quiz question about {topic}. Just ask the question directly with A, B, C, D options. No topic announcement.")


# Handle inline button taps
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = get_user(query.from_user.id)

    if data == "q_quiz":
        user["mode"] = "quiz"
        topic = random.choice(QUIZ_TOPICS)
        await handle_message_logic(update, context,
            override_text=f"Give me a quiz question about {topic}. Just ask the question directly with A, B, C, D options. No topic announcement.",
            is_callback=True)
    elif data in BUTTON_QUESTIONS:
        question = BUTTON_QUESTIONS[data]
        await handle_message_logic(update, context, override_text=question, is_callback=True)


# Core message logic
async def handle_message_logic(update, context, override_text=None, is_callback=False):
    if is_callback:
        user_id = update.callback_query.from_user.id
        chat_id = update.callback_query.message.chat_id
    else:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

    user = get_user(user_id)
    text = override_text or update.message.text

    system = f"""{SYSTEM_PROMPT}
Current mode: {user['mode'].upper()}"""

    user["history"].append({"role": "user", "content": text})
    history = user["history"][-10:]

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system,
            messages=history
        )
        reply = response.content[0].text
        user["history"].append({"role": "assistant", "content": reply})

        # After quiz answer, rotate to new topic silently
        if user["mode"] == "quiz" and any(opt in text.upper() for opt in ["A", "B", "C", "D"]):
            reply += "\n\n_Type /quiz for another question!_"

        if len(reply) > 4000:
            reply = reply[:4000] + "...\n\n_(Reply truncated — ask me to continue!)_"

        if is_callback:
            await context.bot.send_message(chat_id=chat_id, text=reply, parse_mode="Markdown")
        else:
            await update.message.reply_text(reply, parse_mode="Markdown")

    except Exception as e:
        error_msg = "⚠️ Something went wrong. Please try again in a moment."
        if is_callback:
            await context.bot.send_message(chat_id=chat_id, text=error_msg)
        else:
            await update.message.reply_text(error_msg)
        print(f"Error: {e}")


# Regular message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_message_logic(update, context)


# ============================================================
#  RUN THE BOT
# ============================================================
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_chat))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🐝 Hive bot is running...")
    app.run_polling()
