import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8301751505:AAGI40o0LKp2YO2t3D7UI_xzWkgjgmwHfMg"
ADMIN_ID = 5952515002

CODES = {
    "8D3c": "https://mega.nz/folder/DB9XTZbB#4OTr7_IYHzlvvx8Qb9qq2g",
    "7w0G": "https://cloud.mail.ru/public/65gp/gfPVTuvF7",
    "test3": "https://example.com/3",
    "test4": "https://example.com/4",
    "test5": "https://example.com/5"
}

photo_system_enabled = True
pending_photos = {}

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Ввести код", callback_data="enter_code")],
        [InlineKeyboardButton("Відправити фото-доказ", callback_data="send_photo")]
    ]
    await update.message.reply_text(
        "Привіт 🔥\nОберіть дію:",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "enter_code":
        await query.message.reply_text("🔑 Введіть ваш код:")
        context.user_data["waiting_for_code"] = True

    elif query.data == "send_photo":
        if not photo_system_enabled:
            await query.message.reply_text("❌ Надсилання фото зараз вимкнено адміністратором.")
            return
        await query.message.reply_text("📸 Надішли фото як доказ виконання!")
        context.user_data["waiting_for_photo"] = True

    elif query.data.startswith("approve_") or query.data.startswith("deny_"):
        await admin_decision(update, context)

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("waiting_for_code"):
        context.user_data["waiting_for_code"] = False

        if text in CODES:
            await update.message.reply_text(f"✅ Код правильний!\nВаш лінк: {CODES[text]}")
        else:
            await update.message.reply_text("❌ Неправильний код.")

    else:
        await update.message.reply_text("Оберіть дію командою /start")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_photos

    if not context.user_data.get("waiting_for_photo"):
        return

    context.user_data["waiting_for_photo"] = False

    user = update.message.from_user
    file = update.message.photo[-1].file_id

    pending_photos[user.id] = file

    kb = [
        [InlineKeyboardButton("Підтвердити", callback_data=f"approve_{user.id}")],
        [InlineKeyboardButton("Відхилити", callback_data=f"deny_{user.id}")]
    ]

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file,
        caption=f"📩 Фото від @{user.username} (ID: {user.id})",
        reply_markup=InlineKeyboardMarkup(kb)
    )

    await update.message.reply_text("📤 Фото відправлено! Очікуйте перевірки.")

async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, user_id = data.split("_")
    user_id = int(user_id)

    if user_id not in pending_photos:
        await query.message.reply_text("Фото вже оброблено.")
        return

    if action == "approve":
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ Ваше завдання підтверджено!\nВаш код: 7w0G"
        )
        await query.message.reply_text("Підтверджено ✔")
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Ваше завдання не підтверджено."
        )
        await query.message.reply_text("Відхилено ❌")

    pending_photos.pop(user_id, None)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    await app.run_polling()

if __name__ == "__main__":
    main()
    
