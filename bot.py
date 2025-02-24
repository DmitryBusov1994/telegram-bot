import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import aiohttp
import requests
from config import API_TOKEN, WB_API_KEY, ZMO_API_KEY, GROUP_ID, CENT_APP_API_KEY
from database import init_db, get_user, update_user, create_payment

# Инициализация
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Состояния
class UserStates(StatesGroup):
    QUERY = State()
    PHOTO = State()

# Проверка подписки на группу

async def check_group(user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(GROUP_ID, user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

# Создание платежа в Cent.app
async def create_cent_payment(user_id: int, amount: int, description: str) -> str:
    url = "https://cent.app/api/v1/payment/create"
    headers = {"Authorization": f"Bearer {CENT_APP_API_KEY}"}
    data = {
        "amount": amount,
        "description": description,
        "callback_url": "ВАШ_ВЕБХУК_URL/callback"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                await create_payment(result['id'], user_id, amount)
                return result['payment_url']
            return None

# Поиск на Wildberries
def search_wb(query: str) -> list:
    params = {"query": query, "resultset": "catalog", "sort": "popular", "limit": 5}
    headers = {"Authorization": WB_API_KEY}
    response = requests.get("https://search.wb.ru/exactmatch/ru/common/v4/search", headers=headers, params=params)
    return response.json().get("data", {}).get("products", []) if response.status_code == 200 else []

# Виртуальная примерка
async def virtual_try_on(model_image: str, clothing_image: str) -> str:
    async with aiohttp.ClientSession() as session:
        data = {
            "model_image_url": model_image,
            "clothing_image_url": clothing_image
        }
        headers = {"Authorization": f"Bearer {ZMO_API_KEY}"}
        async with session.post("https://api.zmo.ai/v1/virtual-try-on", headers=headers, json=data) as response:
            if response.status == 200:
                return (await response.json()).get("output_url")
            return None

# Команда /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if not await check_group(message.from_user.id):
        await message.answer("❌ Подпишитесь на нашу группу: https://t.me/Fresh_Fesh_Vision")
        return

    user = await get_user(message.from_user.id)
    if not user:
        await update_user(message.from_user.id, free_attempts=3)
        await message.answer("👋 Добро пожаловать! У вас есть 3 бесплатных поиска в неделю.")
    await show_main_menu(message)

# Главное меню
async def show_main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔍 Поиск")
    keyboard.add("📊 Мои тарифы", "📜 История поисков")
    await message.answer("Выберите действие:", reply_markup=keyboard)

# Показ тарифов
async def show_tariffs(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("Бесплатный (3 поиска)", callback_data="tariff_free"))
    keyboard.add(types.InlineKeyboardButton("Разовый доступ (10 поисков)", callback_data="tariff_single"))
    keyboard.add(types.InlineKeyboardButton("Месячный доступ (без ограничений)", callback_data="tariff_monthly"))
    await message.answer("Выберите тариф:", reply_markup=keyboard)

# Обработка выбора тарифа
@dp.callback_query_handler(lambda c: c.data.startswith('tariff_'))
async def process_tariff(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    tariff = callback_query.data.split('_')[1]

    if tariff == "free":
        await bot.answer_callback_query(callback_query.id, "Бесплатный тариф уже активен.")
    elif tariff == "single":
        payment_url = await create_cent_payment(user_id, 20, "Разовый доступ (10 поисков)")
        await bot.send_message(user_id, f"💳 Оплатите 20 рублей: {payment_url}")
    elif tariff == "monthly":
        payment_url = await create_cent_payment(user_id, 100, "Месячный доступ")
        await bot.send_message(user_id, f"💳 Оплатите 100 рублей: {payment_url}")

# Обработка запроса
@dp.message_handler(state=UserStates.QUERY)
async def process_query(message: types.Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if user['free_attempts'] > 0:
        await update_user(message.from_user.id, free_attempts=user['free_attempts'] - 1)
    elif user['paid_attempts'] > 0:
        await update_user(message.from_user.id, paid_attempts=user['paid_attempts'] - 1)

    products = search_wb(message.text)
    if not products:
        await message.answer("😔 Ничего не найдено.")
        return

    for product in products[:5]:
        try_image = await virtual_try_on(None, product['image_url'])
        if try_image:
            await message.answer_photo(
                try_image,
                caption=f"🔗 {product['name']} - {product['price']} руб.\nСсылка: {product['link']}"
            )

# Обработка кнопки "Мои тарифы"
@dp.message_handler(lambda message: message.text == "📊 Мои тарифы")
async def show_my_tariffs(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Вы не зарегистрированы.")
        return

    response = (
        f"📊 Ваши тарифы:\n"
        f"• Бесплатные попытки: {user['free_attempts']}\n"
        f"• Оплаченные попытки: {user['paid_attempts']}\n"
        f"• Подписка до: {user['subscription_end'] if user['subscription_end'] else 'нет'}"
    )
    await message.answer(response)

# Обработка кнопки "История поисков"
@dp.message_handler(lambda message: message.text == "📜 История поисков")
async def show_search_history(message: types.Message):
    conn = await asyncpg.connect(DATABASE_URL)
    history = await conn.fetch('SELECT query, timestamp FROM search_history WHERE user_id = $1 ORDER BY timestamp DESC', message.from_user.id)
    await conn.close()

    if not history:
        await message.answer("📜 История поисков пока пуста.")
        return

    response = "📜 Ваша история поисков:\n"
    for entry in history:
        response += f"• {entry['query']} ({entry['timestamp'].strftime('%Y-%m-%d %H:%M')})\n"
    await message.answer(response)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)