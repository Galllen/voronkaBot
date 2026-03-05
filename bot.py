import os
import json
from aiogram import F, Bot, Dispatcher, types
from aiogram.types import WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, chat
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.formatting import as_line, BlockQuote
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from keyboards.inline import (get_guide_inline_button, get_form_inline_button, get_guestions_inline_button)
from keyboards.reply import (get_age_keyboard, get_income_keyboard, get_occupation_keyboard)
from db import add_user_db, update_user_answer, get_users_count, is_user_completed, mark_user_completed
import asyncio
import random

# Load environment variables (only in development)
if os.path.exists(".env"):
    load_dotenv(".env")

BOT_TOKEN = os.getenv("BOT_TOKEN")


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN должен быть задан в переменных окружения")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
pending_guide: set[int] = set()
pending_form_tasks: dict[int, asyncio.Task] = {}
pending_questions_tasks: dict[int, asyncio.Task] = {}
pending_guide_click_tasks: dict[int, asyncio.Task] = {}


class Questionnaire(StatesGroup):
    age = State()
    income = State()
    occupation = State()
    motivation = State()


def get_admin_ids() -> list[int]:
    try:
        with open("admin.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return [int(x) for x in data if isinstance(x, (int, str)) and str(x).isdigit()]
    except (OSError, json.JSONDecodeError):
        return []


async def schedule_nudge(user_id: int, chat_id: int) -> None:
    await asyncio.sleep(900)
    if user_id not in pending_guide:
        return
    pending_guide.discard(user_id)
    #photo = FSInputFile("media/dozhim_1.JPG")
    #caption = "Прожимай кнопку и гайд забирай\n\nВнутри - как тебе без вложений 40-80к уже на этой неделе получить"
    #await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=get_guide_inline_button)
    text = f'''Ты тут?

Нажимай кнопку и забирай гайд, в нем <strong>ты получишь связку с которой сможешь заработать 70-80к уже на этой неделе,</strong> просто берешь и делаешь по шагам<tg-emoji emoji-id='{5398001711786762757}'>✅</tg-emoji>
    '''
    await bot.send_message(chat_id = chat_id, text = text, reply_markup=get_guide_inline_button, parse_mode=ParseMode.HTML)


def cancel_form_nudge(user_id: int) -> None:
    task = pending_form_tasks.pop(user_id, None)
    if task:
        task.cancel()


def start_form_nudge(user_id: int, chat_id: int) -> None:
    cancel_form_nudge(user_id)
    pending_form_tasks[user_id] = asyncio.create_task(schedule_form_nudge(user_id, chat_id))


async def schedule_form_nudge(user_id: int, chat_id: int) -> None:
    try:
        await asyncio.sleep(900)
        if pending_form_tasks.get(user_id) != asyncio.current_task():
            return
        pending_form_tasks.pop(user_id, None)
        caption = '''Бро, тебе осталось только нажать кнопку и гайд уже у тебя <i>(все данные останутся только у меня, не переживай).</i>

Нажимай кнопку👇
        '''
        await bot.send_message(chat_id=chat_id, text=caption, reply_markup=get_guestions_inline_button, parse_mode=ParseMode.HTML)
        #await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, reply_markup=get_guestions_inline_button, parse_mode=ParseMode.HTML)
    except asyncio.CancelledError:
        pass
    finally:
        if pending_form_tasks.get(user_id) == asyncio.current_task():
            pending_form_tasks.pop(user_id, None)


QUESTIONS_NUDGE_MESSAGES = [
    "Ты жив?)",
    "Последний шаг до твоих 70к на РКО уже на этой неделе",
    "Забирай гайд)",
]


def cancel_questions_nudge(user_id: int) -> None:
    task = pending_questions_tasks.pop(user_id, None)
    if task:
        task.cancel()


def start_questions_nudge(user_id: int, chat_id: int) -> None:
    cancel_questions_nudge(user_id)
    pending_questions_tasks[user_id] = asyncio.create_task(schedule_questions_nudge(user_id, chat_id))


async def schedule_questions_nudge(user_id: int, chat_id: int) -> None:
    try:
        await asyncio.sleep(10)
        if pending_questions_tasks.get(user_id) != asyncio.current_task():
            return
        pending_questions_tasks.pop(user_id, None)
        text = random.choice(QUESTIONS_NUDGE_MESSAGES)
        await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)
    except asyncio.CancelledError:
        pass
    finally:
        if pending_questions_tasks.get(user_id) == asyncio.current_task():
            pending_questions_tasks.pop(user_id, None)


def cancel_guide_click_nudge(user_id: int) -> None:
    task = pending_guide_click_tasks.pop(user_id, None)
    if task:
        task.cancel()


def start_guide_click_nudge(user_id: int, chat_id: int) -> None:
    cancel_guide_click_nudge(user_id)
    pending_guide_click_tasks[user_id] = asyncio.create_task(schedule_guide_click_nudge(user_id, chat_id))


async def schedule_guide_click_nudge(user_id: int, chat_id: int) -> None:
    try:
        await asyncio.sleep(900)
        if pending_guide_click_tasks.get(user_id) != asyncio.current_task():
            return
        pending_guide_click_tasks.pop(user_id, None)
        caption = "Вижу, что ещё не написал мне. Может тебе не нужен гайд? Или потратишь 3 минуты, чтобы начать зарабатывать?"
        await bot.send_message(
            chat_id=chat_id, 
            text=caption, 
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(text="МОЯ ЛИЧКА", url='https://t.me/m/0-4vKeqhMmEy')
                ]]), 
            parse_mode=ParseMode.HTML
        )
    except asyncio.CancelledError:
        pass
    finally:
        if pending_guide_click_tasks.get(user_id) == asyncio.current_task():
            pending_guide_click_tasks.pop(user_id, None)


@dp.message(Command("start"))
async def start(message: types.Message):
    # Логируем юзернейм + айди пользователя
    if message.from_user:
        user_id = message.from_user.id
        username = message.from_user.username
        if not username:
            await message.answer("Нужен ник @username, чтобы получить гайд.")
            return
        if is_user_completed(user_id):
            await message.answer("Привет! Ты уже ответил на анкету! Скоро я с тобой свяжусь 🤝")
            return
        add_user_db(user_id, username)
        pending_guide.add(user_id)
        asyncio.create_task(schedule_nudge(user_id, message.chat.id))
    else:
        print(f"Bot: message.from_user is None")
    
    # Формируем приветствие
    greeting = '''
Бро, привет 🔥

Скажу честно — меня самого нормально так удивило, когда этой осенью я впервые сделал <strong>500к</strong> на РКО. И я делюсь этой цифрой, не потому что «вау, миллионы», а потому что я слишком хорошо знаю, <strong>насколько тяжело такие деньги вытаскиваются в других нишах</strong>.

Я больше 2 лет в онлайне, успел попробовать самые разные ниши и вот мой вывод: <strong>сейчас идеальный момент врываться в РКО</strong>, пока тема не заезжена и не задушена конкуренцией. Я вижу реальный потенциал тут в ближайшие 2-3 года.

👇 Ниже ты получаешь <strong>гайд</strong>, где я без воды как заработать свои первые 70-80к на РКО в 2026 году

Если ищешь направление, где можно начать зарабатывать <b>уже сейчас</b>, а не «когда-нибудь» — жми кнопку ниже.

Я потом задам пару вопросов, чтобы быть на связи и двигаться дальше 👇

'''
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(
        text="ПОЛУЧИТЬ ГАЙД"
    ))
    photo = FSInputFile("media/after_start.jpeg")
    await message.answer_photo(
        photo=photo,
        caption=greeting, 
        reply_markup=get_guide_inline_button,
        parse_mode=ParseMode.HTML
    )

async def main():
    # Удаляем webhook перед запуском polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("Webhook удален, запускаем polling...")
    except Exception as e:
        print(f"Ошибка при удалении webhook: {e}")
    
    await dp.start_polling(bot)





@dp.callback_query(F.data == "get_guide")
async def get_guide(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user:
        pending_guide.discard(callback.from_user.id)
        start_form_nudge(callback.from_user.id, callback.message.chat.id)
    text = '''
Я этот <strong>гайд отдаю чисто за респект</strong>, без продаж и всего такого. Будет круто, если ты просто поделишься инфой о себе — мне важно понимать, <strong>кто тот самый человек, с кем мы вместе сделаем первые 100–300к на РКО.</strong>

Сейчас закину пару вопросов.

Как ответишь — <strong>сразу скидываю гайд</strong>🤝

'''

    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(
        text="Ответить на 4 вопроса"
    ))
    photo = FSInputFile("media/before_questions.jpeg")
    await callback.message.answer_photo(
        photo=photo,
        caption=text, 
        reply_markup=get_guestions_inline_button,
        parse_mode=ParseMode.HTML
    )




@dp.callback_query(F.data == "get_questions")
async def get_questions(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user:
        pending_guide.discard(callback.from_user.id)
        cancel_form_nudge(callback.from_user.id)
        start_questions_nudge(callback.from_user.id, callback.message.chat.id)
    text = '''<b>ВОПРОС 1/4</b>

Сколько тебе лет?
    '''
    await callback.message.answer(
        text=text, 
        reply_markup=get_age_keyboard,
        parse_mode=ParseMode.HTML
    )
    await state.set_state(Questionnaire.age)


@dp.message(Questionnaire.age)
async def handle_age(message: types.Message, state: FSMContext):
    age_options = ["14-17", "18-20", "21-25", "26-40"]
    if message.text not in age_options:
        await message.answer("Пожалуйста, выбери один из вариантов кнопками ниже:")
        return
    update_user_answer(
        user_id=message.from_user.id if message.from_user else None,
        username=message.from_user.username if message.from_user else None,
        field="age",
        value=message.text,
    )
    
    await state.update_data(age=message.text)
    text = '''<b>ВОПРОС 2/4</b>
    
Сколько ты сейчас зарабатываешь?
'''
    await message.answer(
        text=text,
        reply_markup=get_income_keyboard,
        parse_mode=ParseMode.HTML
    )
    if message.from_user:
        start_questions_nudge(message.from_user.id, message.chat.id)
    await state.set_state(Questionnaire.income)




@dp.message(Questionnaire.income)
async def handle_income(message: types.Message, state: FSMContext):
    income_options = ["нет заработка", "до 20к", "20-40к", "40-70к", "70-100к", "100к+"]
    if message.text not in income_options:
        await message.answer("Пожалуйста, выбери один из вариантов кнопками ниже:")
        return
    update_user_answer(
        user_id=message.from_user.id if message.from_user else None,
        username=message.from_user.username if message.from_user else None,
        field="income",
        value=message.text,
    )
    await state.update_data(income=message.text)
    text = '''<b>ВОПРОС 3/4</b>
    
Чем ты сейчас занимаешься?
    '''
    await message.answer(
        text=text,
        reply_markup=get_occupation_keyboard,
        parse_mode=ParseMode.HTML
    )
    if message.from_user:
        start_questions_nudge(message.from_user.id, message.chat.id)
    await state.set_state(Questionnaire.occupation)


@dp.message(Questionnaire.occupation)
async def handle_occupation(message: types.Message, state: FSMContext):
    occupation_options = ["учусь", "работаю в найме", "работаю на себя", "уже занимаюсь РКО"]
    if message.text not in occupation_options:
        await message.answer("Пожалуйста, выбери один из вариантов кнопками ниже:")
        return
    update_user_answer(
        user_id=message.from_user.id if message.from_user else None,
        username=message.from_user.username if message.from_user else None,
        field="occupation",
        value=message.text,
    )
    await state.update_data(occupation=message.text)
    text = '''<b>ВОПРОС 4/4</b>
    
Зачем вообще тебе этот гайд и почему тебе интересна тема РКО? (хочешь попробовать что-то новое, хочешь зарабатывать онлайн, ищешь доп.заработок)

<blockquote>Ответь развёрнуто</blockquote>
    '''
    await message.answer(text=text, 
                        parse_mode=ParseMode.HTML)
    if message.from_user:
        start_questions_nudge(message.from_user.id, message.chat.id)
    await state.set_state(Questionnaire.motivation)


@dp.message(Questionnaire.motivation)
async def handle_motivation(message: types.Message, state: FSMContext):
    update_user_answer(
        user_id=message.from_user.id if message.from_user else None,
        username=message.from_user.username if message.from_user else None,
        field="motivation",
        value=message.text,
    )
    await state.update_data(motivation=message.text)
    if message.from_user:
        cancel_form_nudge(message.from_user.id)
        cancel_questions_nudge(message.from_user.id)
        mark_user_completed(message.from_user.id, message.from_user.username)
    data = await state.get_data()
    lead_number = get_users_count()
    username = f"@{message.from_user.username}" if message.from_user and message.from_user.username else "@example"
    lead_msg = (
        f"🔥 НОВЫЙ ЛИД #{lead_number}\n\n"
        f"👤 ЮЗ: {username}\n\n"
        f"❓ Сколько тебе лет? \n <blockquote>{data.get('age')}</blockquote>\n\n"
        f"❓ Сколько ты сейчас зарабатываешь? \n <blockquote>{data.get('income')}</blockquote>\n\n"
        f"❓ Чем ты сейчас занимаешься? \n <blockquote>{data.get('occupation')}</blockquote>\n\n"
        f"❓ Зачем вообще тебе это гайд и почему тебе интересна тема РКО? (хочешь попробовать что-то новое, хочешь зарабатывать онлайн, ищешь доп.заработок) \n <blockquote>{data.get('motivation')}</blockquote>\n\n"
    )
    for admin_id in get_admin_ids():
        try:
            await bot.send_message(chat_id=admin_id, text=lead_msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Не удалось отправить лид админу {admin_id}: {e}")
    await state.clear()
    text = '''Огонь, вижу твои ответы🔥

Напиши в личку <a href="https://t.me/m/0-4vKeqhMmEy">ССЫЛКА</a> и я скину тебе гайд
(В боте не у всех открывается в гайд, поэтому лично отправлю тебе)
'''
    await message.answer(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Я написал ✅", callback_data="guide_click")
        ]]),
        parse_mode=ParseMode.HTML
    )
    if message.from_user:
        start_guide_click_nudge(message.from_user.id, message.chat.id)


@dp.callback_query(F.data == "guide_click")
async def guide_click(callback: types.CallbackQuery):
    if callback.from_user:
        cancel_guide_click_nudge(callback.from_user.id)
        update_user_answer(
            user_id=callback.from_user.id,
            username=callback.from_user.username,
            field="guide_clicked",
            value="clicked"
        )
    await callback.answer("Вижу бро, скоро тебе отвечу 🤝", show_alert=True)



if __name__ == "__main__":
    asyncio.run(main()) 