import os
import json
import base64
import logging
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# Sozlamalar
API_TOKEN = os.getenv('BOT_TOKEN')
WEB_APP_URL = os.getenv('WEB_APP_URL')
WEBHOOK_PATH = '/webhook'  # Define the webhook path

# Logging
logging.basicConfig(level=logging.INFO)

# Token tekshirish
if not API_TOKEN:
    logging.warning("BOT_TOKEN topilmadi! .env fayl yoki muhit o'zgaruvchilarini tekshiring.")
    # Agar token bo'lmasa, bot ishga tushmaydi, lekin kod xatosiz tugaydi (crash bo'lmaydi)
    # Vercel'da bu muhim emas, chunki u yerda token bo'ladi.
    # Ammo lokal testda qulay bo'lishi uchun dummy token qo'yamiz yoki shunchaki ogohlantiramiz.
    API_TOKEN = "dummy_token_for_ide_check"

# Bot va Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Webhook yo'llari
VERCEL_URL = os.getenv('VERCEL_URL', 'https://sizning-saytingiz.vercel.app')
WEBHOOK_URL = f"{VERCEL_URL}{WEBHOOK_PATH}"

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    Foydalanuvchi /start yozganda WebApp tugmasini chiqaradi
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    webapp = types.WebAppInfo(url=WEB_APP_URL)
    button = types.KeyboardButton(text="Tasdiqlash va Davom etish ✅", web_app=webapp)
    markup.add(button)
    
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "Xizmatdan foydalanish uchun quyidagi tugmani bosing va kamera ruxsatini tasdiqlang.",
        reply_markup=markup
    )

@dp.message_handler(content_types=['web_app_data'])
async def web_app_data_handler(message: types.Message):
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
                photo=image_bytes,
                caption="✅ Shaxsingiz muvaffaqiyatli tasdiqlandi (Rasm qabul qilindi)."
            )
        else:
            await message.answer("Xatolik: Rasm ma'lumotlari topilmadi.")
            
    except Exception as e:
        logging.error(f"Xatolik yuz berdi: {e}")
        await message.answer("Ma'lumotni qayta ishlashda xatolik yuz berdi.")

# Vercel uchun serverless funksiya handlerlari
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

# Bu qism Vercel muhitida ishlash uchun kerak

async def handle_webhook(request):
    url = str(request.url)
    # Simple check for webhook path
    if request.path == WEBHOOK_PATH:
        try:
            data = await request.json()
            update = types.Update(**data)
            Dispatcher.set_current(dp)
            Bot.set_current(bot)
            await dp.process_update(update)
            return web.Response(text="OK")
        except Exception as e:
            logging.error(f"Webhook error: {e}")
            return web.Response(status=500)
    return web.Response(status=403)

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)