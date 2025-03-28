import os
import sys
import logging
import gspread
import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from oauth2client.service_account import ServiceAccountCredentials
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 🔐 Блокировка повторного запуска
LOCKFILE = "/data/data/com.termux/files/home/bot.lock"
if os.path.exists(LOCKFILE):
    print("⚠️ Бот уже работает. Второй запуск блокирован.")
    sys.exit()
with open(LOCKFILE, "w") as f:
    f.write("running")

# ⚙️ Настройки
TOKEN = "8080091792:AAED9X1dxlMDy3Xca5qwjGlzRIS31VGAkdA"
CHANNEL_ID = "@turanmarket001"
ADMIN_ID = 6608247548
SPREADSHEET_NAME = "AliExpress Turan Market"

# 🌐 Подключение к Google Таблице
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).sheet1

# 🛒 История публикаций
posted_titles = []

# 📤 Уведомление администратору
async def notify_admin(bot: Bot, message: str):
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=message)
    except Exception as e:
        logging.error(f"[✗] Ошибка при отправке уведомления: {e}")

# 🧹 Очистка ссылки
def clean_url(url):
    if "http" in url:
        parts = url.split("http")
        return "http" + parts[1].strip()
    return url.strip()

# 📦 Автопубликация товара
async def publish_next_product(app: Application):
    try:
        records = sheet.get_all_records()
        for row in records:
            title = row.get("Название", "").strip()
            price = row.get("Цена", "").strip()
            url = clean_url(row.get("Ссылка", ""))
            image = row.get("Картинка", "").strip()
            is_partner = str(row.get("Партнёрская", "")).strip()

            if title in posted_titles or is_partner != "✅":
                continue

            if not url.startswith("http"):
                continue

            text = f"🛍️ <b>{title}</b>\n💰 Цена: {price}"
            button = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Купить", url=url)]])

            try:
                if image and image.startswith("http"):
                    await app.bot.send_photo(chat_id=CHANNEL_ID, photo=image, caption=text, reply_markup=button, parse_mode="HTML")
                else:
                    await app.bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=button, parse_mode="HTML")
            except Exception as e:
                await app.bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=button, parse_mode="HTML")
                logging.warning(f"⚠️ Ошибка при отправке фото: {e}")

            posted_titles.append(title)
            await notify_admin(app.bot, f"✅ Опубликовано: {title}")
            break
    except Exception as e:
        await notify_admin(app.bot, f"❌ Ошибка при публикации: {e}")

# 🧾 Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "друг"
    welcome = f"👋 <b>Привет, {name}!</b>\nДобро пожаловать в TURAN Market!\n\n🛒 Здесь вы найдете лучшие товары с AliExpress с удобной кнопкой покупки.\n\n📦 Используйте /status, /next или /stop (для админа)."
    menu = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Перейти в магазин", url="https://t.me/turanmarket001")],
        [InlineKeyboardButton("📞 Поддержка", url="https://t.me/ASICCHIP")]
    ])
    await update.message.reply_text(welcome, reply_markup=menu, parse_mode="HTML")

# 👮 Команда /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text(f"📊 Бот активен. Опубликовано товаров: {len(posted_titles)}")
    else:
        await update.message.reply_text("⛔ Доступ запрещён")

# ⏭️ Команда /next
async def next_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await publish_next_product(context.application)
        await update.message.reply_text("⏭ Следующий товар опубликован.")
    else:
        await update.message.reply_text("⛔ Доступ запрещён")

# 🛑 Команда /stop
async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await notify_admin(context.bot, "⛔ Бот остановлен вручную.")
        await context.application.shutdown()
        if os.path.exists(LOCKFILE):
            os.remove(LOCKFILE)
        sys.exit()
    else:
        await update.message.reply_text("⛔ Доступ запрещён")

# 🚀 Запуск
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("next", next_post))
    app.add_handler(CommandHandler("stop", stop_bot))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(publish_next_product, "interval", args=[app], minutes=3)
    scheduler.start()

    await notify_admin(app.bot, "🤖 TURAN MARKET запущен!")
    await publish_next_product(app)
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        if os.path.exists(LOCKFILE):
            os.remove(LOCKFILE)

