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
BOT_TOKEN = "8601680131:AAGEnByhGyF2CPygt_mN_lpglwcyHbSNQDg"  # Вставь сюда токен от BotFather
# URL базы данных для твоего проекта qrcod-8ada6
FIREBASE_URL = "https://qrcod-8ada6-default-rtdb.firebaseio.com/" 
SITE_URL = "https://ВАШ-САЙТ.onrender.com"

# --- КОНФИГУРАЦИЯ ИЗ ТВОЕГО ФАЙЛА ---
fb_config = {
  "type": "service_account",
  "project_id": "qrcod-8ada6",
  "private_key_id": "71dab8fdc4862c544a0984e0ce777159f152ad72",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDVwO7lNlOcw3zY\naI84mbQe1Gxka0DVvY/cTpBUvXT5nyxL16lu1Kl+xwIwNNwwguF7eWCzkLmn72re\njO3WrTLakrta9YDFxExbjE2NjLF6aAcl6KcfBzI0q0o8e8xYQUTLbFwObBA6ttyJ\nhGnCvQQMHnssvPXMGxg+1bzNmRdBxf6rnHZ6ZpQLUuoi7tJa2J+7WaBTrpPr3vfR\nDfNi66Vik0z7VEwT2lwrlCQQSKlE56sOacF8dSjV6LvjYkI8Fac85lvyqMA+ZsXO\ntVnbm80vdYOk2ynCP8/ZngDOphkz0ayPjO160preL/bxJ6StSt408mABz+ZPK44Y\nIPETOVgVAgMBAAECggEAQh0bJwU/JlEmt87bYZ/U4OZGImc0Fgg8S2F3beZtnFnZ\nuxmY2+FmDYLjT+LBqjWJJYY83T1p1yIL1YsUc159yLIyxecCbekRzw0d3abDLD+p\n2lVT/5pbsoO6geuuoCuL6jl5XbKZ8HcnzlcI2UVaT59L7OIDSp6kyKaWb6cm1N4m\nGCOyvOVZGJ2GFNw6UyEuiKf0UFAreIYGQ/Qtyogzycy7BpHevzuRqO393xDy8Zib\nMi3MGgYYAYGcl4fdose7+RlL3Px2pdQLBl3bKBspaePSP53m5UPBV9vd5SYSAINl\nI1KKL1I9IV9QPxeCQPXYgvhtszGxGBflMNv9mHZVXwKBgQD7mOnIJlBeawYDs0K4\nCkKfkQWUrWZj5cmsICqKPOzhclTHIbU/l0XxUF0Aanex4wgYW956B5GDfrt3uqcA\nccLj31n+VrqLSlskAilGvPYm9sQuzP+cNGwxakEFSvi3m7/e6DlRIYKGbfM1rdkG\nvbJkO5YhAsiRMlAUMWOVvHLouwKBgQDZfn2gljMRORY51Aa3A2VwePOT6+NSK6/I\n71cinjgFp4gLv02pir1JbUbAXnHWOulh2batAP0bHn09Rj8VrlhPe2m2Liwh5GU8\n7KvHrGSgrtK733b+LDa2ZCIaG77r2D7+txxge2GKUWDsZixOLTmMrITPEyRZyCwk\nO/wCwifdbwKBgBbA+oueY3BWj4GwKZ2JWAMkU3PhxrvMIVQOyKod3nJ5K4+izciF\nfs7XLMIH3vFYjffd/x3cJ13UDVJDsCzLHQwMvA/TeiV0wQ9dnqwGFODrOkzdP1S6\nLPq/GEhJQnsge9bF+8EJnctYkEFPiqwgZczI0sgDf24aNcHNwareEypXAoGBAMeF\nM4gS4ewl247XRAW2NuOUAZesaRBjhVImxl+6l5gQVUy5hWxIG1d1yNcGjRXDW3/p\ncpyI8KhlMuz4OT0RgHABvjtjZhb9aCYY04lMS8/gMPAqkwWe195AQ8yBsYa4DSos\nHvsflJ6IAws6u+BHuqijRv6UB9/ZMy1WXdzF8j4/AoGBAPlXuBwaAF/KdIZA1kKg\nGG5Zy905uanfXdM/F56mNciZXG+PoIwrAgSFZbiPRMA2/xdqR0Cw3xnK9Sh2eZXp\nzDexdMHmSFzeCr8bHYoFssmUecn4khFLXo3sq+ItZldItSPgsjPdjd90SEsp7WBt\nYScRCXKMUNgAfrmkjtECxdjg\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@qrcod-8ada6.iam.gserviceaccount.com",
  "client_id": "102545588320138654247",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40qrcod-8ada6.iam.gserviceaccount.com"
}

# --- ИНИЦИАЛИЗАЦИЯ ---
if not firebase_admin._apps:
    cred = credentials.Certificate(fb_config)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

auth_ref = db.reference('/auth_tokens')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- МИНИ-СЕРВЕР ДЛЯ ПОРТА (ДЛЯ RENDER) ---
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")

def run_port_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    token = secrets.token_urlsafe(16)
    try:
        # Пытаемся записать токен в Firebase
        auth_ref.child(token).set({
            "uid": message.from_user.id,
            "name": message.from_user.first_name
        })
        
        login_url = f"{SITE_URL}/auth/{token}"
        kb = InlineKeyboardBuilder()
        kb.row(types.InlineKeyboardButton(text="ВХОД ✅", url=login_url))
        await message.answer(f"Привет! Ссылка для входа:", reply_markup=kb.as_markup())
        
    except Exception as e:
        # Если здесь ошибка — она выведется в консоль Render
        print(f"ОШИБКА FIREBASE: {e}")
        await message.answer("Ошибка авторизации. Проверьте логи сервера.")

async def main():
    threading.Thread(target=run_port_server, daemon=True).start()
    await bot.delete_webhook(drop_pending_updates=True)
    print("Бот запущен...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())