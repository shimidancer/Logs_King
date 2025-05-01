import os
import django
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# === Django setup ===
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NewProject.settings")
django.setup()

from django.contrib.auth.models import User, Group
from users.models import UserProfile

# === Telegram bot setup ===
logging.basicConfig(level=logging.INFO)

REGISTER_NAME = 1  # этап регистрации

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши своё имя для регистрации.")
    return REGISTER_NAME

# Регистрация имени
async def register_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip()
    telegram_id = update.effective_user.id

    # Проверка на существующий профиль
    if UserProfile.objects.filter(telegram_id=telegram_id).exists():
        await update.message.reply_text("Ты уже зарегистрирован.")
        return ConversationHandler.END

    # Проверка, свободен ли username
    if User.objects.filter(username=username).exists():
        await update.message.reply_text("Это имя уже занято. Попробуй другое.")
        return REGISTER_NAME

    password = "tg_auto_pass"
    user = User.objects.create_user(username=username, password=password)
    group, _ = Group.objects.get_or_create(name="Пользователь")
    user.groups.add(group)

    UserProfile.objects.create(user=user, telegram_id=telegram_id)

    await update.message.reply_text(
        f"✅ Готово! Ты зарегистрирован как *{username}*\n"
        f"Пароль: `{password}`\n"
        f"Telegram ID: `{telegram_id}`\n"
        f"💾 Профиль сохранён успешно!",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# Команда /профиль
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        user = profile.user
        await update.message.reply_text(
            f"👤 Твой профиль:\n"
            f"Имя: *{user.username}*\n"
            f"Telegram ID: `{telegram_id}`",
            parse_mode="Markdown"
        )
    except UserProfile.DoesNotExist:
        await update.message.reply_text("❌ Ты ещё не зарегистрирован. Напиши /start")

# Отмена регистрации
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Регистрация отменена.")
    return ConversationHandler.END

# Запуск бота
def main():
    bot_token = "8054244832:AAFpylcsYyYI7AiHCShGXChr-od_pJqzeQY"
    app = ApplicationBuilder().token(bot_token).build()

    # Диалог регистрации
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_name)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("profile", profile))  # 👈 добавили команду

    app.run_polling()

if __name__ == "__main__":
    main()
