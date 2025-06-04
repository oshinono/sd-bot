from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from schemas import UserImgGenSettings
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def get_settings_keyboard(user_data: UserImgGenSettings):
    kb = InlineKeyboardBuilder()
    user_data_dict = user_data.model_dump()

    for key in user_data_dict.keys():
        kb.add(InlineKeyboardButton(text=key, callback_data=f"settings_{key}"))

    kb.adjust(3, repeat=True)
    kb.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    return kb.as_markup()


async def back_to_settings_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
            [InlineKeyboardButton(text="⚙️⬅️ Назад к настройкам", callback_data="back_to_settings")],
        ],
    )