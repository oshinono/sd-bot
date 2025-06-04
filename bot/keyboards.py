from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def back_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")],
        ],
    )

