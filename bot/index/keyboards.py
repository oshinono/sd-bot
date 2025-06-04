from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton 
from schemas import UserImgGenSettings
from aiogram.utils.keyboard import InlineKeyboardBuilder
from runware import ILora

async def get_start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖼️ Генерация изображений", callback_data="generate_image")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        ],
    )



