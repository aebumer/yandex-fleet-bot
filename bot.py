from flask import Flask, request
     import logging
     import requests
     import time
     from telegram import Update, ReplyKeyboardMarkup
     from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, Filters

     # Настройка логирования
     logging.basicConfig(
         filename="bot.log",
         level=logging.INFO,
         format="%(asctime)s - %(levelname)s - %(message)s",
     )

     app = Flask(__name__)

     # Настройки
     TELEGRAM_TOKEN = "7576993270:AAFYBEcXlsojTAULY-xnbSb8Dn0CzWw4kto"
     YANDEX_API_TOKEN = "ZEgaPmejqmUmjRCYnyoPvdtkeSaUoKQFPYHEdp"
     PARK_ID = "f10282c2f9424dc685b429acc2f6bc5a"

     # Инициализация бота
     application = Application.builder().token(TELEGRAM_TOKEN).build()

     # Клавиатура
     keyboard = ReplyKeyboardMarkup([["/start"]], resize_keyboard=True)

     async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
         logging.info(f"Получена команда /start от {update.effective_chat.id}")
         park_name = get_park_name()
         await update.message.reply_text(
             f"Таксопарк: {park_name}", reply_markup=keyboard
         )

     async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
         logging.info(f"Неизвестная команда от {update.effective_chat.id}: {update.message.text}")
         await update.message.reply_text(
             "Пожалуйста, используй /start.", reply_markup=keyboard
         )

     def get_park_name():
         url = "https://api.taxi.yandex.net/v1/parks"
         headers = {
             "Authorization": f"Bearer {YANDEX_API_TOKEN}",
             "X-Park-Id": PARK_ID,
             "Content-Type": "application/json",
         }
         for attempt in range(1, 4):
             try:
                 logging.info(f"Попытка {attempt}: запрос к API Яндекс.Флот")
                 response = requests.get(url, headers=headers, timeout=10)
                 data = response.json()
                 logging.info(f"Ответ API: {response.status_code} {data}")
                 if response.status_code == 200 and data.get("parks"):
                     return data["parks"][0].get("name", "Неизвестный парк")
                 else:
                     logging.error(f"Ошибка API: {response.status_code} {data}")
                     return f"Ошибка: не удалось получить название парка (статус {response.status_code})"
             except Exception as e:
                 logging.error(f"Ошибка запроса (попытка {attempt}): {str(e)}")
                 if attempt == 3:
                     return "Ошибка: не удалось подключиться к API Яндекс.Флот"
                 time.sleep(2)

     @app.route("/webhook", methods=["POST"])
     async def webhook():
         update = Update.de_json(request.get_json(), application.bot)
         await application.process_update(update)
         return "OK"

     def main():
         application.add_handler(CommandHandler("start", start))
         application.add_handler(MessageHandler(Filters.text & ~Filters.command, unknown_command))
         app.run(host="0.0.0.0", port=5000)

     if __name__ == "__main__":
         main()
