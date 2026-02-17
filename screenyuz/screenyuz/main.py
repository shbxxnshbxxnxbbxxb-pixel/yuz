import os
import json
import base64
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web

# Load environment variables
load_dotenv()

# Sozlamalar
API_TOKEN = os.getenv('BOT_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL')
WEBHOOK_PATH = '/webhook'

# Logging
logging.basicConfig(level=logging.INFO)

# Token tekshirish
if not API_TOKEN:
    logging.warning("BOT_TOKEN topilmadi! .env fayl yoki muhit o'zgaruvchilarini tekshiring.")
    API_TOKEN = "dummy_token_for_ide_check"

# Bot va Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Webhook yo'llari
VERCEL_URL = os.getenv('VERCEL_URL', 'https://sizning-saytingiz.vercel.app')
WEBHOOK_URL = f"{VERCEL_URL}{WEBHOOK_PATH}"

@dp.message(Command("start"))
async def send_welcome(message: Message):
    """
    Foydalanuvchi /start yozganda WebApp tugmasini chiqaradi
    """
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Tasdiqlash va Davom etish ✅", web_app=WebAppInfo(url=WEB_APP_URL))]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "Xizmatdan foydalanish uchun quyidagi tugmani bosing va kamera ruxsatini tasdiqlang.",
        reply_markup=markup
    )

@dp.message(F.web_app_data)
async def web_app_data_handler(message: Message):
    """
    WebApp'dan rasm (Base64) kelganda uni qabul qiladi
    """
    try:
        data = json.loads(message.web_app_data.data)
        image_base64 = data.get("image")

        if image_base64:
            header, encoded = image_base64.split(",", 1)
            image_bytes = base64.b64decode(encoded)

            await bot.send_photo(
                chat_id=message.chat.id,
                photo=types.BufferedInputFile(image_bytes, filename="photo.jpg"),
                caption="✅ Shaxsingiz muvaffaqiyatli tasdiqlandi (Rasm qabul qilindi)."
            )
        else:
            await message.answer("Xatolik: Rasm ma'lumotlari topilmadi.")
            
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        await message.answer("Ma'lumotni qayta ishlashda xatolik yuz berdi.")

# Vercel uchun serverless funksiya handlerlari
async def on_startup(bot: Bot):
    await bot.set_webhook(WEBHOOK_URL)

async def handle_webhook(request):
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot=bot, update=update)
        return web.Response(text="OK")
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return web.Response(status=500)

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)

# Hook for startup
async def start_background_tasks(app):
    await on_startup(bot)

app.on_startup.append(start_background_tasks)
