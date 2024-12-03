from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
calculate_button = KeyboardButton(text="Рассчитать")
info_button = KeyboardButton(text="Информация")
keyboard.add(calculate_button, info_button)
inline_keyboard = InlineKeyboardMarkup()
button_calculate = InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")
button_formulas = InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")
inline_keyboard.add(button_calculate, button_formulas)


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
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_keyboard)


@dp.callback_query_handler(text="formulas")
async def get_formulas(query: CallbackQuery):
    await bot.send_message(query.from_user.id, "Формула Миффлина-Сан Жеора:\n"
                                               "Для мужчин: (10 × вес (кг) + 6.25 × рост (см) – 5 × возраст (лет) + "
                                               "5) × А\n"
                                               "Для женщин: (10 × вес (кг) + 6.25 × рост (см) – 5 × возраст (лет) – "
                                               "161) × А\n"
                                               "где А — коэффициент активности.")


@dp.callback_query_handler(text="calories")
async def set_age(query: CallbackQuery):
    await bot.send_message(query.from_user.id, 'Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = int(message.text)
    await message.answer('Введите свой рост (в см):')
    await UserState.next()


@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['growth'] = float(message.text)
    await message.answer('Введите свой вес (в кг):')
    await UserState.next()


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
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
