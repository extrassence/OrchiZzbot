from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands='start')
async def start_command(message: types.Message):
    await message.answer("Привет! Я могу рассчитать вашу суточную норму калорий. Чтобы начать, напишите /calories.")


@dp.message_handler(commands='calories', state="*")
async def set_age(message: types.Message):
    await message.answer('Введите свой возраст:')
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

    # Рассчитываем норму калорий по формуле Миффлина-Сан Жеора для мужчин
    calories_norm = 10 * weight + 6.25 * growth - 5 * age + 5

    await message.answer(f"Ваша суточная норма калорий составляет примерно {int(calories_norm)} ккал.")
    await state.finish()


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
