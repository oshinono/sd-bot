from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

async def get_stop_gen_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛑 Выйти из режима генерации")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )