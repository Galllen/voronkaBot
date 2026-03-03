##### В ЭТОМ ФАЙЛЕ СОЗДАЁМ ИНЛАЙН КНОПКИ И ПРИСВАИВАЕМ ИМ УНИКАЛЬНУЮ ДАТУ ##### 

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
#from core.special_func.memories.get_path_size import get_path_size
#from core.special_func.memories.check import get_current_directory
import json


get_guide_inline_button = InlineKeyboardMarkup(inline_keyboard=[
  [
    InlineKeyboardButton(
      text='ПОЛУЧИТЬ ГАЙД',
      callback_data= f'get_guide',
    )
  ]]
)

get_guestions_inline_button = InlineKeyboardMarkup(inline_keyboard=[
  [
    InlineKeyboardButton(
      text='Ответить на 4 вопроса',
      callback_data='get_questions',
    )
  ]]
)




get_form_inline_button = InlineKeyboardMarkup(inline_keyboard=[
  [
    InlineKeyboardButton(
      text='ЗАПОЛНИТЬ АНКЕТУ',
      callback_data= f'get_guide',
    )
  ]]
)