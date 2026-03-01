import asyncio
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8601680131:AAEoJSyfjO8Dd2MMc4jBoNPFaxyTIM1JUd0"  # Вставь сюда токен от BotFather
# URL базы данных для твоего проекта qrcod-8ada6
FIREBASE_URL = "https://qrcod-8ada6-default-rtdb.firebaseio.com/" 
SITE_URL = "https://tissuuuu.pythonanywhere.com/"


# --- УНИВЕРСАЛЬНЫЙ ПУТЬ К КЛЮЧУ ---
# На Render файл лежит в /etc/secrets/, на ПК — в той же папке, что и бот
key_path = "/etc/secrets/firebase-sdk.json"
if not os.path.exists(key_path):
    key_path = "firebase-sdk.json" # Локальный путь для ПК

# --- ИНИЦИАЛИЗАЦИЯ ---
try:
    if not firebase_admin._apps:
        # credentials.Certificate САМ правильно читает \n из JSON-файла
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})
        print(f"✅ Firebase успешно подключен через: {key_path}")
except Exception as e:
    print(f"❌ КРИТИЧЕСКАЯ ОШИБКА ИНИЦИАЛИЗАЦИИ: {e}")

auth_ref = db.reference('/auth_tokens')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- СЕРВЕР ДЛЯ RENDER (PORT BINDING) ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), HealthHandler).serve_forever()

# --- КОМАНДА /START ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    token = secrets.token_urlsafe(16)
    try:
        auth_ref.child(token).set({
            "uid": message.from_user.id,
            "name": message.from_user.first_name
        })
        login_url = f"{SITE_URL}/auth/{token}"
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="ВХОД ✅", url=login_url))
        await message.answer("Привет! Ваша ссылка для входа:", reply_markup=kb.as_markup())
    except Exception as e:
        print(f"❌ ОШИБКА ПРИ ЗАПИСИ: {e}")
        await message.answer("Ошибка связи с базой. Проверьте логи.")

async def main():
    threading.Thread(target=run_server, daemon=True).start()
    await bot.delete_webhook(drop_pending_updates=True)
    print("🚀 Бот запущен...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())