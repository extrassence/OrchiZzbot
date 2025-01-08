from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import shmoken
import crud_functions as crud

API_TOKEN = shmoken.token

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

products = crud.get_all_products()

title = []

for p in products:
    title = title + [p[1]]

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
calculate_button = KeyboardButton(text="Рассчитать")
info_button = KeyboardButton(text="Информация")
buy_button = KeyboardButton(text='Купить')
register_button = KeyboardButton(text='Регистрация')
keyboard.add(calculate_button, info_button)
keyboard.add(buy_button, register_button)

inline_keyboard = InlineKeyboardMarkup()
button_calculate = InlineKeyboardButton(text="Ваша норма калорий", callback_data="calories")
button_formulas = InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")
inline_keyboard.add(button_calculate, button_formulas)

buy_keyboard = InlineKeyboardMarkup()
button_pr1 = InlineKeyboardButton(text=title[0], callback_data="product_buying")
button_pr2 = InlineKeyboardButton(text=title[1], callback_data="product_buying")
button_pr3 = InlineKeyboardButton(text=title[2], callback_data="product_buying")
button_pr4 = InlineKeyboardButton(text=title[3], callback_data="product_buying")
buy_keyboard.add(button_pr1, button_pr2)
buy_keyboard.add(button_pr3, button_pr4)


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text=['Регистрация'])
async def sign_up(message):
    await message.answer('Введите имя пользователя:')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if not crud.is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer('Введите свой e-mail:')
        await RegistrationState.email.set()
    else:
        await message.answer('Такой пользователь уже зарегистрирован, введите другое имя:')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    if ('@' in message.text) and ('.' in message.text):
        await state.update_data(email=message.text)
        await message.answer('Введите свой возраст:')
        await RegistrationState.age.set()
    else:
        await message.answer('Неверный формат электронной почты, введите, пожалуйста, другой адрес:')
        await RegistrationState.email.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    try:
        age = int(message.text)
    except:
        await message.answer(f'Возраст должен быть целым числом. Введите ещё раз:')
        await RegistrationState.age.set()
        return
    await state.update_data(age=message.text)
    data = await state.get_data()
    # если все ок, добавляем в db:
    crud.add_user(data['username'], data['email'], int(data['age']))
    await message.answer('Спасибо за регистрацию!')
    await state.finish()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Привет! Я могу рассчитать вашу суточную норму калорий.", reply_markup=keyboard)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=keyboard)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer("Выберите опцию:", reply_markup=inline_keyboard)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    global products
    for p in products:
        msg = f'Название: {p[1]} | Описание: {p[2]} | Цена: {p[3]} ₽'
        with open(p[4], 'rb') as img:
            await message.answer_photo(img, msg)
    await message.answer('Выберите продукт для покупки:', reply_markup=buy_keyboard)

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
