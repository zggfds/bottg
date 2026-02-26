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
BOT_TOKEN = "8601680131:AAGNLQW4vu_vrR7gCkEPqpZGDzLnkNOX5Is"
FIREBASE_KEY_PATH = "firebase-sdk.json"
FIREBASE_URL = "https://qrcod-8ada6-default-rtdb.firebaseio.com/"
# Ссылка на твой ПЕРВЫЙ сервис (сайт)
SITE_URL = "https://siteprof.onrender.com/"





# --- МИНИ-СЕРВЕР ДЛЯ RENDER (ЧТОБЫ НЕ БЫЛО ОШИБКИ PORT) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is healthy")

def run_health_server():
    # Render всегда передает порт в переменную окружения PORT (обычно 10000)
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Заглушка порта запущена на порту {port}")
    server.serve_forever()

# --- ЛОГИКА БОТА ---
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

auth_ref = db.reference('/auth_tokens')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    token = secrets.token_urlsafe(16)
    
    # Сохраняем токен в Firebase
    auth_ref.child(token).set({
        "uid": message.from_user.id,
        "name": message.from_user.first_name
    })
    
    login_url = f"{SITE_URL}/auth/{token}"
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="ВХОД ✅", url=login_url))
    
    await message.answer(f"Привет, {message.from_user.first_name}! Вот твоя ссылка:", reply_markup=kb.as_markup())

async def main():
    # 1. Запускаем веб-сервер в отдельном потоке, чтобы он не мешал боту
    threading.Thread(target=run_health_server, daemon=True).start()
    
    # 2. Очищаем очередь обновлений, чтобы не было Conflict
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Бот запущен...")
    # 3. Стартуем прослушивание Telegram
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())