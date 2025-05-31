from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
router = Router()

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(None)
    await message.answer("Привет! Я бот для генерации изображений по тексту. Отправь мне текст, и я сгенерирую для тебя картинку.")
