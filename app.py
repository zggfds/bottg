import asyncio
import secrets
import firebase_admin
from firebase_admin import credentials, db
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8601680131:AAEe6qFOIoCRs5U0cKkWTRU05l5X_PaFDjw"
FIREBASE_KEY_PATH = "firebase-sdk.json"
FIREBASE_URL = "https://qrcod-8ada6-default-rtdb.firebaseio.com/"
# Ссылка на твой ПЕРВЫЙ сервис (сайт)
SITE_URL = "https://siteprof.onrender.com/"

# Инициализация Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

auth_ref = db.reference('/auth_tokens')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    token = secrets.token_urlsafe(16)
    
    # Бот просто кладет токен в Firebase
    auth_ref.child(token).set({
        "uid": message.from_user.id,
        "name": message.from_user.first_name
    })
    
    login_url = f"{SITE_URL}/auth/{token}"
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="ВХОД НА САЙТ ✅", url=login_url))
    
    await message.answer(f"Привет, {message.from_user.first_name}! Вот твоя ссылка:", reply_markup=kb.as_markup())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())