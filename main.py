import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

from config import TOKEN, COINMARKETCAP_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Helper function for API requests
def get_crypto_price(crypto: str, fiat: str):
    url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}
    params = {"symbol": crypto.upper(), "convert": fiat.upper()}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            price = data["data"][crypto.upper()]["quote"][fiat.upper()]["price"]
            return round(price, 2)
        except KeyError:
            return None
    return None

# Команда /start
@dp.message(Command("start"))
async def start(message: Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Курсы криптовалют"), types.KeyboardButton(text="Конвертация")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я крипто-бот.\n\n"
        f"Я помогу узнать актуальные курсы криптовалют.",
        reply_markup=keyboard
    )

# Обработка кнопок
@dp.message(lambda msg: msg.text == "Курсы криптовалют")
async def handle_prices_button(message: Message):
    await message.answer("Введите криптовалюту и фиат для получения курса.\nПример: BTC USD")

@dp.message(lambda msg: msg.text == "Конвертация")
async def handle_conversion_button(message: Message):
    await message.answer("Введите количество, криптовалюту и фиат для конвертации.\nПример: 1 BTC USD")

@dp.message()
async def handle_input(message: Message):
    args = message.text.split()
    if len(args) == 2:  # Для получения курса
        crypto, fiat = args[0], args[1]
        price = get_crypto_price(crypto, fiat)
        if price:
            await message.answer(f"Текущий курс {crypto.upper()} в {fiat.upper()}: {price}")
        else:
            await message.answer("Не удалось получить данные. Проверьте правильность ввода.")
    elif len(args) == 3:  # Для конвертации
        try:
            amount = float(args[0])
            crypto, fiat = args[1], args[2]
            price = get_crypto_price(crypto, fiat)
            if price:
                total = round(amount * price, 2)
                await message.answer(f"{amount} {crypto.upper()} = {total} {fiat.upper()}")
            else:
                await message.answer("Не удалось получить данные. Проверьте правильность ввода.")
        except ValueError:
            await message.answer("Сумма должна быть числом.")
    else:
        await message.answer("Неправильный формат ввода. Попробуйте снова.")

# Установка команд в меню
async def set_commands():
    commands = [
        types.BotCommand(command="start", description="Начало работы")
    ]
    await bot.set_my_commands(commands)

# Главная функция
async def main():
    print("Запуск бота...")
    await set_commands()
    print("Установка команд...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())