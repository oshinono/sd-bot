from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lora.schemas import ILoraExtended
from aiogram.types import InlineKeyboardMarkup

async def get_lora_settings_keyboard(loras: list[ILoraExtended]):
    kb = InlineKeyboardBuilder()
    for lora in loras:
        kb.add(InlineKeyboardButton(text=lora.shortname, callback_data=f"lora_{lora.model}"))
    kb.adjust(3, repeat=True)
    kb.row(InlineKeyboardButton(text="➕", callback_data="add_lora"))
    kb.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    return kb.as_markup()


async def get_lora_model_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="AIR ☁️", callback_data="change_lora_air"), InlineKeyboardButton(text="Вес ⚖️", callback_data="change_lora_weight"), InlineKeyboardButton(text="Название 📝", callback_data="change_lora_shortname")],
            [InlineKeyboardButton(text="❌", callback_data="delete_lora")],
            [InlineKeyboardButton(text="Назад", callback_data="back")]
        ]
    )