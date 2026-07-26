import os
import io
import asyncio
from aiohttp import web
from PIL import Image
from aiogram import Bot, Dispatcher, types
import google.generativeai as genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранилище для альбомов (если пользователь шлет несколько фото сразу)
album_data = {}

@dp.message(lambda message: message.photo)
# Используем альбомы, чтобы бот не отвечал на каждое фото отдельно, а ждал всю пачку
async def handle_photos(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    # Берем самое качественное фото из сообщения
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    
    file_bytes = io.BytesIO()
    await bot.download_file(file.file_path, destination=file_bytes)
    img = Image.open(file_bytes)

    prompt = (
        "Ты профессиональный парсер скриншотов авиабилетов с trip.com. "
        "Пользователь может отправить один или несколько скриншотов. "
        "Тебе нужно проанализировать их все, выбрать билеты с багажом, "
        "отсортировать их по дате по порядку (от ранних к поздним), "
        "указать цену и время транзита. В конце обязательно укажи точный объем багажа "
        "(например: 🧳 Bagaj: 30 kg + Qo‘l yuki 10 kg). "
        "Оформи результат строго по шаблону заказчика на узбекском языке."
    )
    
    try:
        response = await model.generate_content_async([prompt, img])
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Xatolik yuz berdi.")

async def handle_ping(request):
    return web.Response(text="Bot is alive!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
