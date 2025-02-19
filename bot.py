import logging
import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InputFile
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("TELEGRAM_API_TOKEN"))

dp = Dispatcher()

# Данные игры
users_in_game = {}
team_tasks = {
    "team1": {1: ("Задание 1 для команды 1", "ответ1"), 2: ("Задание 2 для команды 1", "ответ2"), 3: ("Задание 3 для команды 1", "ответ3")},
    "team2": {1: ("Задание 1 для команды 2", "ответ1"), 2: ("Задание 2 для команды 2", "ответ2"), 3: ("Задание 3 для команды 2", "ответ3")},
    "team3": {1: ("Задание 1 для команды 3", "ответ1"), 2: ("Задание 2 для команды 3", "ответ2"), 3: ("Задание 3 для команды 3", "ответ3")},
    "team4": {1: ("Задание 1 для команды 4", "ответ1"), 2: ("Задание 2 для команды 4", "ответ2"), 3: ("Задание 3 для команды 4", "ответ3")},
    "team5": {1: ("Задание 1 для команды 5", "ответ1"), 2: ("Задание 2 для команды 5", "ответ2"), 3: ("Задание 3 для команды 5", "ответ3")}
}

admin_password = os.getenv("ADMIN_PASSWORD")

@dp.message(CommandStart())
async def start_game(message: Message):
    user_id = message.from_user.id
    if user_id not in users_in_game:
        users_in_game[user_id] = {"team": None, "progress": {1: False, 2: False, 3: False}}
        await message.answer("Привет! Введи свою команду: team1, team2, team3, team4 или team5")
    else:
        await message.answer("Ты уже в игре!")

@dp.message(F.text.startswith("team"))
async def choose_team(message: Message):
    user_id = message.from_user.id
    team = message.text.lower()

    if team in team_tasks:
        users_in_game[user_id]["team"] = team
        await message.answer(f"Ты в команде {team}. Вот твое первое задание: {team_tasks[team][1][0]}")
    else:
        await message.answer("Такой команды нет. Выбери team1 - team5.")

@dp.message()
async def check_answer(message: Message):
    user_id = message.from_user.id
    if user_id not in users_in_game or users_in_game[user_id]["team"] is None:
        await message.answer("Ты не в игре или не выбрал команду!")
        return

    team = users_in_game[user_id]["team"]
    for level in range(1, 4):
        if not users_in_game[user_id]["progress"][level]:
            correct_answer = team_tasks[team][level][1]
            if message.text.lower().strip() == correct_answer.lower():
                users_in_game[user_id]["progress"][level] = True
                await message.answer(f"Молодец! Ты прошел {level}-е задание.")
                if level < 3:
                    await message.answer(f"Следующее задание: {team_tasks[team][level + 1][0]}")
                else:
                    await message.answer("Ты прошел все задания!")
            else:
                await message.answer("Неправильный ответ. Попробуй еще раз!")
            return

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
