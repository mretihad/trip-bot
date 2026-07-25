import os
import io
from PIL import Image
from aiogram import Bot, Dispatcher, types
import google.generativeai as genai

# Теперь ключи спрятаны и будут браться напрямую с сервера Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(lambda message: message.photo)
async def handle_photo(message: types.Message):
    # Показываем статус "печатает" пока обрабатывается фото
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    
    file_bytes = io.BytesIO()
    await bot.download_file(file.file_path, destination=file_bytes)
    img = Image.open(file_bytes)

    prompt = (
        "Ты бот, который парсит скриншоты авиабилетов с trip.com. "
        "Ищи только билеты с багажом. Выводи цену, дату и время транзита "
        "строго по шаблону заказчика на узбекском. Например: 27.07: 517$ | 1 soat 30 min. "
        "Вытащи данные из этого скриншота и оформи в список."
    )
    
    try:
        response = await model.generate_content_async([prompt, img])
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Xatolik yuz berdi.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
