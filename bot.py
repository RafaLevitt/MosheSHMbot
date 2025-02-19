import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Set up proxy if needed (example proxy URL)
PROXY_URL = "http://your_proxy_address:port"  # Replace with your actual proxy URL

bot = Bot(token=os.getenv("TELEGRAM_API_TOKEN"), proxy=PROXY_URL)
dp = Dispatcher()

# Game data
users_in_game = {}
team_tasks = {
    "team1": {1: ("Задание 1 для команды 1", "ответ1"), 2: ("Задание 2 для команды 1", "ответ2"), 3: ("Задание 3 для команды 1", "ответ3")},
    "team2": {1: ("Задание 1 для команды 2", "ответ1"), 2: ("Задание 2 для команды 2", "ответ2"), 3: ("Задание 3 для команды 2", "ответ3")},
    "team3": {1: ("Задание 1 для команды 3", "ответ1"), 2: ("Задание 2 для команды 3", "ответ2"), 3: ("Задание 3 для команды 3", "ответ3")},
    "team4": {1: ("Задание 1 для команды 4", "ответ1"), 2: ("Задание 2 для команды 4", "ответ2"), 3: ("Задание 3 для команды 4", "ответ3")},
    "team5": {1: ("Задание 1 для команды 5", "ответ1"), 2: ("Задание 2 для команды 5", "ответ2"), 3: ("Задание 3 для команды 5", "ответ3")}
}

admin_password = os.getenv("ADMIN_PASSWORD")
admin_users = set()  # Admin users list after login

@dp.message(CommandStart())
async def start_game(message: Message):
    """Start the game - player registration."""
    user_id = message.from_user.id
    if user_id not in users_in_game:
        users_in_game[user_id] = {"team": None, "progress": {1: False, 2: False, 3: False}}
        await message.answer("Привет! Введи свою команду: team1, team2, team3, team4 или team5.")
    else:
        await message.answer("Ты уже в игре!")

@dp.message(F.text.startswith("/admin"))
async def admin_login(message: Message):
    """Admin panel login."""
    user_id = message.from_user.id
    _, entered_password = message.text.split(" ", 1) if " " in message.text else ("", "")

    if entered_password == admin_password:
        admin_users.add(user_id)
        await message.answer("✅ Ты вошел в админ-панель. Теперь можешь использовать /vseloxi")
    else:
        await message.answer("❌ Неверный пароль!")

@dp.message(F.text == "/vseloxi")
async def wipe_vars(message: Message):
    """Reset game data (for admins only)."""
    if message.from_user.id in admin_users:
        global users_in_game
        users_in_game = {}
        await message.answer("✅ Все данные сброшены.")
    else:
        await message.answer("❌ У тебя нет прав для этой команды.")

@dp.message(F.text.startswith("team"))
async def choose_team(message: Message):
    """Choose a team."""
    user_id = message.from_user.id
    team = message.text.lower()

    if team in team_tasks:
        users_in_game[user_id]["team"] = team
        await message.answer(f"Ты в команде {team}. Вот твое первое задание: {team_tasks[team][1][0]}")
    else:
        await message.answer("Такой команды нет. Выбери team1 - team5.")

@dp.message(F.text.startswith("/"))
async def handle_command(message: Message):
    """Command handler (ignores commands as answers)."""
    pass  # Ignore commands here

@dp.message()
async def check_answer(message: Message):
    """Check the user's answer."""
    user_id = message.from_user.id
    if user_id not in users_in_game or users_in_game[user_id]["team"] is None:
        return  # Ignore messages if user hasn't selected a team

    team = users_in_game[user_id]["team"]
    for level, (task_text, correct_answer) in team_tasks[team].items():
        if not users_in_game[user_id]["progress"][level]:
            if message.text.lower().strip() == correct_answer.lower():
                users_in_game[user_id]["progress"][level] = True
                next_msg = f"Молодец! Ты прошел {level}-е задание."

                if level < len(team_tasks[team]):
                    next_msg += f"\nСледующее задание: {team_tasks[team][level + 1][0]}"
                else:
                    next_msg += "\nТы прошел все задания!"

                await message.answer(next_msg)
            else:
                await message.answer("Неправильный ответ. Попробуй еще раз!")
            return

async def main():
    """Run the bot."""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
