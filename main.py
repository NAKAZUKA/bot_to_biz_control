import asyncio
from aiogram import Bot, Dispatcher, types
import logging
from aiogram.filters import CommandStart, Command
import requests
from database import Database

BOT_TOKEN = ''
SERVICE_URL = 'http://127.0.0.1:8000'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

db = Database()


@dp.message(CommandStart())
async def process_start_command(message: types.Message):
    await message.reply("Привет! Я бот, который может взаимодействовать с вашим сервисом через JWT-токен.\n"
                        "Для начала, зарегистрируйтесь или войдите в систему.\n"
                        "Отправьте свои учетные данные в формате: /register username password email first_name last_name")


@dp.message(Command(commands=['register']))
async def register(message: types.Message):
    try:
        _, username, password, email, first_name, last_name = message.text.split()
        response = requests.post(f'{SERVICE_URL}/user_api/users/', data={
            'username': username,
            'password': password,
            'email': email,
            'first_name': first_name,
            'last_name': last_name
        })
        if response.status_code == 201:
            try:
                db.add_user(
                    telegram_id=message.from_user.id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email
                )
                logging.info(f"User {message.from_user.id} registered")
            except Exception as e:
                await message.answer(f"Произошла ошибка: {e}")
            await message.answer("Вы успешно зарегистрированы!")
        else:
            await message.answer("Ошибка регистрации. Проверьте свои учетные данные и попробуйте снова.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


@dp.message(Command(commands=['add_token']))
async def authenticate(message: types.Message):
    try:
        _, username, password = message.text.split()
        response = requests.post(f'{SERVICE_URL}/token/', data={'username': username, 'password': password})

        if response.status_code == 200:
            token = response.json().get('access')
            try:
                db.add_token(message.from_user.id, token)
            except Exception as e:
                await message.answer(f"Произошла ошибка: {e}")
            await message.answer(f"Вы успешно аутентифицированы! Токен:\n\n{token}")
        else:
            await message.answer("Ошибка аутентификации. Проверьте свои учетные данные и попробуйте снова.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
