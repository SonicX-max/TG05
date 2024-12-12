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
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton(text="Курсы криптовалют")
    )
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я крипто-бот.\n\n"
        f"Я помогу узнать актуальные курсы криптовалют.",
        reply_markup=keyboard
    )

# Команда /price
@dp.message(Command("price"))
async def price(message: Message):
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Использование: /price [CRYPTO] [FIAT]\nПример: /price BTC USD")
        return
    crypto, fiat = args[1], args[2]
    price = get_crypto_price(crypto, fiat)
    if price:
        await message.answer(f"Текущий курс {crypto.upper()} в {fiat.upper()}: {price}")
    else:
        await message.answer("Не удалось получить данные. Проверьте правильность ввода.")

# Команда /convert
@dp.message(Command("convert"))
async def convert(message: Message):
    args = message.text.split()
    if len(args) != 4:
        await message.answer("Использование: /convert [AMOUNT] [CRYPTO] [FIAT]\nПример: /convert 1 BTC USD")
        return
    try:
        amount = float(args[1])
        crypto, fiat = args[2], args[3]
        price = get_crypto_price(crypto, fiat)
        if price:
            total = round(amount * price, 2)
            await message.answer(f"{amount} {crypto.upper()} = {total} {fiat.upper()}")
        else:
            await message.answer("Не удалось получить данные. Проверьте правильность ввода.")
    except ValueError:
        await message.answer("Сумма должна быть числом.")

# Обработка кнопок
@dp.message(lambda msg: msg.text == "Курсы криптовалют")
async def handle_prices_button(message: Message):
    await message.answer("Введите команду /price [CRYPTO] [FIAT], чтобы узнать курс.")

# Установка команд в меню
async def set_commands():
    commands = [
        types.BotCommand(command="start", description="Начало работы"),
        types.BotCommand(command="price", description="Курс криптовалют"),
        types.BotCommand(command="convert", description="Конвертация криптовалют")
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