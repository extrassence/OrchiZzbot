from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = ''

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
calculate_button = KeyboardButton(text="Рассчитать")
info_button = KeyboardButton(text="Информация")
keyboard.add(calculate_button, info_button)


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
async def set_age(message):
    await message.answer('Введите свой возраст:')
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
