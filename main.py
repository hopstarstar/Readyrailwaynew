import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

BOT_TOKEN = os.getenv("8301751505:AAGI40o0LKp2YO2t3D7UI_xzWkgjgmwHfMg")
ADMIN_ID = int(os.getenv("5952515002"))

# Коди, які бот видає
CODES = {
    "8D3c": "https://mega.nz/folder/DB9XTZbB#4OTr7_IYHzlvvx8Qb9qq2g",
    "7w0G": "https://cloud.mail.ru/public/65gp/gfPVTuvF7",
    "99999": "https://example.com/3",
}

# Фото-режим (можна вимкнути /togglephoto)
PHOTO_MODE_ENABLED = True

# Очікувані докази
pending_photos = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Ввести код", callback_data="enter_code")],
        [InlineKeyboardButton("Відправити докази", callback_data="send_photo")],
    ]
    await update.message.reply_text(
        "Виберіть дію:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "enter_code":
        await query.message.reply_text("Введіть свій код:")
        context.user_data["waiting_code"] = True

    elif query.data == "send_photo":
        if not PHOTO_MODE_ENABLED:
            await query.message.reply_text("Відправка фото вимкнена адміном.")
            return

        await query.message.reply_text("Надішліть фото-доказ(и).")
        context.user_data["waiting_photo"] = True


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_photos

    # Користувач вводить код
    if context.user_data.get("waiting_code"):
        code = update.message.text.strip()
        context.user_data["waiting_code"] = False

        if code in CODES:
            await update.message.reply_text(f"Ваше посилання: {CODES[code]}")
        else:
            await update.message.reply_text("❌ Невірний код!")

        return

    # Фото-докази
    if context.user_data.get("waiting_photo") and update.message.photo:
        user_id = update.message.from_user.id
        username = update.message.from_user.username

        file_id = update.message.photo[-1].file_id
        pending_photos[user_id] = file_id

        keyboard = [
            [
                InlineKeyboardButton("Підтвердити", callback_data=f"ok_{user_id}"),
                InlineKeyboardButton("Відхилити", callback_data=f"no_{user_id}"),
            ]
        ]

        await context.bot.send_photo(
            ADMIN_ID,
            photo=file_id,
            caption=f"Доказ від @{username or user_id}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        await update.message.reply_text("Фото передано адмінам.")
        context.user_data["waiting_photo"] = False


async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_photos

    query = update.callback_query
    if query is None:
        return

    data = query.data
    await query.answer()

    if not data.startswith(("ok_", "no_")):
        return

    user_id = int(data.split("_")[1])

    if user_id not in pending_photos:
        await query.message.reply_text("Фото вже оброблене.")
        return

    if data.startswith("ok_"):
        await context.bot.send_message(
            user_id, "✅ Ваше завдання підтверджено!\nВаш код: 7w0G"
        )
        await query.message.reply_text("Підтверджено.")
    else:
        await context.bot.send_message(
            user_id, "❌ Завдання не виконано. Фото не підходить."
        )
        await query.message.reply_text("Відхилено.")

    pending_photos.pop(user_id, None)


async def toggle_photo_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PHOTO_MODE_ENABLED

    if update.message.from_user.id != ADMIN_ID:
        return

    PHOTO_MODE_ENABLED = not PHOTO_MODE_ENABLED

    await update.message.reply_text(
        f"Фото-режим: {'УВІМКНЕНО' if PHOTO_MODE_ENABLED else 'ВИМКНЕНО'}"
    )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add
    
