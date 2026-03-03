from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json


get_age_keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="14-17"),
            KeyboardButton(text="18-20")
        ],
        [
            KeyboardButton(text="21-25"),
            KeyboardButton(text="26-40")
        ]
    ], resize_keyboard=True,one_time_keyboard=True)


get_income_keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="нет заработка")
        ],
        [
            KeyboardButton(text="до 20к"),
            KeyboardButton(text="20-40к")
        ],
        [
            KeyboardButton(text="40-70к"),
            KeyboardButton(text="70-100к")
        ],
                [
            KeyboardButton(text="100к+")
        ]
    ], resize_keyboard=True,one_time_keyboard=True)



get_occupation_keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text="учусь"),
            KeyboardButton(text="работаю в найме")
        ],
        [
            KeyboardButton(text="работаю на себя"),
            KeyboardButton(text="уже занимаюсь РКО")
        ]
    ], resize_keyboard=True,one_time_keyboard=True)

