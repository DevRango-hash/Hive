import os
import logging
import random
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ============================================================
#  TOKENS — Set these in Railway Variables tab (never here)
# ============================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# ============================================================

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""You are Hive 🐝, a crypto and Web3 education assistant living inside Telegram.
Your personality is sharp, friendly, and knowledgeable — like a brilliant friend who knows everything about crypto.

Your capabilities:
1. EXPLAIN crypto topics clearly with simple language and relatable analogies
2. QUIZ MODE — generate multiple choice questions (A/B/C/D) silently rotating topics. Just fire the question directly with no topic announcement. Wait for answer then explain the correct one.
3. Answer any crypto/Web3 question naturally when asked

Rules:
- Never give financial advice or tell people to buy/sell anything
- Always be encouraging and patient
- Keep responses concise — no walls of text
- Use emojis sparingly but effectively
- If user specifies a quiz topic, quiz them on that specific topic"""
)

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
    "q_defi": "What is DeFi (Decentralized Finance)? Explain simply.",
    "q_nfts": "What are NFTs? Explain simply.",
    "q_web3": "What is Web3? Explain simply.",
    "q_stablecoin": "What is a stablecoin? Explain simply.",
    "q_wallet": "What is a crypto wallet? Explain simply.",
    "q_blockchain": "What is blockchain? Explain simply.",
}

user_data = {}

def get_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "history": [],
            "saved_chats": [],
            "chat_number": 1,
        }
    return user_data[user_id]

def save_current_chat(user):
    if user["history"]:
        first_msg = user["history"][0]["parts"] if user["history"] else ""
        title = f"Chat {user['chat_number']}"
        if first_msg:
            preview = str(first_msg)[:30]
            title = f"Chat {user['chat_number']} — {preview}..."
        user["saved_chats"].append({
            "title": title,
            "history": user["history"].copy()
        })
        user["chat_number"] += 1

async def ask_gemini(history, new_message):
    try:
        chat = model.start_chat(history=history)
        response = chat.send_message(new_message)
        return response.text
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        return "⚠️ Something went wrong. Please try again in a moment."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(STARTER_BUTTONS)
    await update.message.reply_text(
        "Gm! ☀️ I'm *Hive* 🐝 — your Web3 knowledge companion.\n\n"
        "Pick a topic below to get started, or just ask me anything!\n\n"
        "📚 Commands:\n"
        "/quiz — Test your knowledge\n"
        "/new — Start a fresh chat\n"
        "/history — View saved chats",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    save_current_chat(user)
    user["history"] = []
    keyboard = InlineKeyboardMarkup(STARTER_BUTTONS)
    await update.message.reply_text(
        "🔄 New chat started! Previous conversation saved.\n\nWhat are we learning today? 🐝",
        reply_markup=keyboard
    )

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if not user["saved_chats"]:
        await update.message.reply_text(
            "📭 No saved chats yet!\n\nChat with me and use /new to save and start fresh."
        )
        return
    history_text = "📚 *Your Saved Chats:*\n\n"
    for i, chat in enumerate(user["saved_chats"][-5:], 1):
        history_text += f"{i}. {chat['title']}\n"
    history_text += "\n_Showing your last 5 conversations._"
    await update.message.reply_text(history_text, parse_mode="Markdown")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    topic = random.choice(QUIZ_TOPICS)
    question_prompt = f"Give me a quiz question about {topic}. Ask the question directly with A, B, C, D options. No topic announcement, no preamble."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await ask_gemini(user["history"], question_prompt)
    user["history"].append({"role": "user", "parts": question_prompt})
    user["history"].append({"role": "model", "parts": reply})
    if len(reply) > 4000:
        reply = reply[:4000] + "..."
    await update.message.reply_text(reply, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)
    data = query.data

    if data == "q_quiz":
        topic = random.choice(QUIZ_TOPICS)
        question_prompt = f"Give me a quiz question about {topic}. Ask the question directly with A, B, C, D options. No topic announcement."
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
        reply = await ask_gemini(user["history"], question_prompt)
        user["history"].append({"role": "user", "parts": question_prompt})
        user["history"].append({"role": "model", "parts": reply})
    elif data in BUTTON_QUESTIONS:
        question = BUTTON_QUESTIONS[data]
        await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
        reply = await ask_gemini(user["history"], question)
        user["history"].append({"role": "user", "parts": question})
        user["history"].append({"role": "model", "parts": reply})
    else:
        return

    if len(reply) > 4000:
        reply = reply[:4000] + "..."
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=reply,
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    text = update.message.text
    if len(user["history"]) > 20:
        user["history"] = user["history"][-20:]
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    reply = await ask_gemini(user["history"], text)
    user["history"].append({"role": "user", "parts": text})
    user["history"].append({"role": "model", "parts": reply})
    if len(reply) > 4000:
        reply = reply[:4000] + "...\n\n_(Ask me to continue!)_"
    await update.message.reply_text(reply, parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_chat))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🐝 Hive is live!")
    app.run_polling()
