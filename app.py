import asyncio
import secrets
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


# --- МИКРО-ФЛАСК ДЛЯ RENDER ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running", 200

def run_flask():
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

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
    auth_ref.child(token).set({
        "uid": message.from_user.id,
        "name": message.from_user.first_name
    })
    
    login_url = f"{SITE_URL}/auth/{token}"
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text="ВХОД ✅", url=login_url))
    await message.answer(f"Привет! Ссылка для входа:", reply_markup=kb.as_markup())

async def main():
    # 1. Запускаем Flask в фоновом потоке
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Чистим очередь (чтобы не было Conflict)
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("Бот и Flask-заглушка запущены...")
    # 3. Запускаем бота
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")