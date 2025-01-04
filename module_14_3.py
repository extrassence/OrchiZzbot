from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import shmoken

API_TOKEN = shmoken.token

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
calculate_button = KeyboardButton(text="Рассчитать")
info_button = KeyboardButton(text="Информация")
buy_button = KeyboardButton(text='Купить средство для похудения')
keyboard.add(calculate_button, info_button)
keyboard.add(buy_button)

inline_keyboard = InlineKeyboardMarkup()
button_calculate = InlineKeyboardButton(text="Ваша норма калорий", callback_data="calories")
button_formulas = InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")
inline_keyboard.add(button_calculate, button_formulas)

buy_keyboard = InlineKeyboardMarkup()
button_pr1 = InlineKeyboardButton(text="Хубур-чубур", callback_data="product_buying")
button_pr2 = InlineKeyboardButton(text="Хрючево без калорий", callback_data="product_buying")
button_pr3 = InlineKeyboardButton(text="Эликсир Фламеля", callback_data="product_buying")
button_pr4 = InlineKeyboardButton(text="Обнулитель Калорий", callback_data="product_buying")
buy_keyboard.add(button_pr1, button_pr2)
buy_keyboard.add(button_pr3, button_pr4)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Привет! Я могу рассчитать вашу суточную норму калорий.", reply_markup=keyboard)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=keyboard)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=inline_keyboard)


@dp.message_handler(text='Купить средство для похудения')
async def buy_menu(message):
    img = {}
    for i in range(4):
        img[i] = open(f'{i + 1}.jpg', 'rb')
    await message.answer_photo(img[0], "Хубур-чубур\nБелки, жиры, углеводы и клетчатка для тех, "
                                       "кому лень готовить, цена 100 рублей.")
    await message.answer_photo(img[1], "Хрючево без калорий\nЕшьте сколько хотите и не поправляйтесь, "
                                       "на вкус не жалуйтесь, цена 200 рублей.")
    await message.answer_photo(img[2], "Эликсир Николаса Фламеля\nИсцеление от всех болезней, от старости, "
                                       "от рака и от тупости, цена 300 рублей.")
    await message.answer_photo(img[3], "Обнулитель Калорий (БАД)\nПриправьте любую еду этим БАДом и она "
                                       "потеряет калории и вкус, цена 400 рублей.")
    for i in range(4):
        img[i].close()
    await message.answer("Выберите продукт:", reply_markup=buy_keyboard)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text="formulas")
async def get_formulas(query):
    await query.message.answer("""Формула Миффлина-Сан Жеора:
Для мужчин: (10 × вес (кг) + 6.25 × рост (см) – 5 × возраст (лет) + 5) × А
Для женщин: (10 × вес (кг) + 6.25 × рост (см) – 5 × возраст (лет) – 161) × А
где А — коэффициент активности.""")


@dp.callback_query_handler(text="calories")
async def set_age(query):
    await query.message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    async with state.proxy() as data:
        data['age'] = int(message.text)
    await message.answer('Введите свой рост (в см):')
    await UserState.next()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    async with state.proxy() as data:
        data['growth'] = float(message.text)
    await message.answer('Введите свой вес (в кг):')
    await UserState.next()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    async with state.proxy() as data:
        data['weight'] = float(message.text)
    user_data = await state.get_data()
    age = user_data['age']
    growth = user_data['growth']
    weight = user_data['weight']

    calories_norm = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f"Ваша суточная норма калорий составляет примерно {int(calories_norm)} ккал.",
                         reply_markup=keyboard)
    await state.finish()


if __name__ == '__main__':
    from aiogram.utils import executor

    executor.start_polling(dp, skip_updates=True)
