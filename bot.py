import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

# Токен бота, полученный через BotFather
API_TOKEN = '7720527686:AAEx12QnjHKTbABTAlFXvpkYG7IYKp1CD8E'

# Пароль для админки
admin_password = 'Sad78Verkiai123'  # Заменить на свой пароль

# Список участников и их статуса (нажали ли они «Готово»)
users_in_game = {}

# Фразы для выдачи пользователям
phrases = [
    "Первая фраза: Успех не приходит случайно.",
    "Вторая фраза: Верь в себя и твои мечты сбудутся.",
    "Третья фраза: Путь к успеху начинается с первого шага."
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Старт игры
@dp.message_handler(commands=['start'])
async def start_game(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_in_game:
        users_in_game[user_id] = {'completed': False}
        await message.answer("Добро пожаловать в игру! Выполни задание и получи фразу.\n\nЗадание 1: [Задача здесь]")
        await message.answer("После выполнения задания нажми /done.")
    else:
        await message.answer("Ты уже в игре!")

# Команда завершения задания
@dp.message_handler(commands=['done'])
async def complete_task(message: types.Message):
    user_id = message.from_user.id
    if user_id in users_in_game:
        users_in_game[user_id]['completed'] = True
        # Считаем, сколько пользователей завершили задания
        completed_count = sum(user['completed'] for user in users_in_game.values())
        
        if completed_count == len(users_in_game):  # Все завершили
            part_index = completed_count - 1
            phrase = phrases[part_index]
            await message.answer(f"Все задания выполнены! Вот ваша фраза: {phrase}")
        else:
            await message.answer("Задание выполнено. Ожидайте остальных участников.")

# Админ команда для загрузки заданий
@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.text.split()[1] == admin_password:  # Проверка пароля
        await message.answer("Добро пожаловать в админ-панель!")
        # Здесь можно добавить логику загрузки текстов и картинок
    else:
        await message.answer("Неверный пароль.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
