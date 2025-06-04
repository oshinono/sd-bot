from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from index.utils import load_default_user_settings
from index.keyboards import get_start_keyboard
from settings.states import SettingsStates

router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    state_data = await state.get_data()
    user_data = state_data.get(f'user_{message.from_user.id}')
    if not user_data:
        await load_default_user_settings(state, message.from_user.id)
        await message.answer("Похоже, ты еще не пользовался ботом. Загрузил настройки по умолчанию.")

    await state.set_state(None)
    await message.answer("Привет! Я бот для генерации изображений по тексту. Отправь мне текст, и я сгенерирую для тебя картинку.",
                         reply_markup=await get_start_keyboard())
    
@router.callback_query(SettingsStates.index, F.data == "back")
async def back_from_settings(callback: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    await callback.message.edit_text("Привет! Я бот для генерации изображений по тексту. Отправь мне текст, и я сгенерирую для тебя картинку.",
                         reply_markup=await get_start_keyboard())

