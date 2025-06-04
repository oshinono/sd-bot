import uuid

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from lora.states import LoraStates
from lora.keyboards import get_lora_settings_keyboard, get_lora_model_keyboard
from schemas import UserImgGenSettings
from settings.states import SettingsStates
from settings.keyboards import back_to_settings_keyboard
from keyboards import back_keyboard
from utils import get_link_to_model_from_air, validate_air

router = Router()

@router.callback_query(SettingsStates.index, F.data == "settings_lora")
async def lora_settings(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    user_data = state_data[f'user_{callback.from_user.id}']
    data = UserImgGenSettings(**user_data)

    await state.set_state(LoraStates.index)
    
    await callback.message.edit_text("Выберите Lora-модель:", reply_markup=await get_lora_settings_keyboard(data.lora))

@router.callback_query(LoraStates.add_lora_air, F.data == "back")
async def back_from_add_lora(callback: CallbackQuery, state: FSMContext):
    await lora_settings(callback, state)

@router.callback_query(LoraStates.lora_model, F.data == "back")
async def back_from_lora_model(callback: CallbackQuery, state: FSMContext):
    await lora_settings(callback, state)

@router.callback_query(LoraStates.index, F.data == "add_lora")
async def add_lora(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LoraStates.add_lora_air)
    await state.update_data(message_to_edit_id=callback.message.message_id)

    await callback.message.edit_text("Введите AIR Lora-модели:", reply_markup=await back_keyboard())

@router.callback_query(LoraStates.add_lora_weight, F.data == "back")
async def back_from_add_lora_weight(callback: CallbackQuery, state: FSMContext):
    await add_lora(callback, state)


@router.message(LoraStates.add_lora_air)
async def add_lora_air(message: Message, state: FSMContext, bot: Bot):
    if message.bot:
        await message.delete()
        
    message_to_edit_id = await state.get_value('message_to_edit_id')

    if not await validate_air(message.text.strip()):
        await bot.edit_message_text(message_id=message_to_edit_id, chat_id=message.chat.id, text="Неверный AIR Lora-модели\n\nПример: <code>urn:air:sdxl:checkpoint:civitai:260267@293564</code>", reply_markup=await back_keyboard())
        return

    await state.update_data(new_lora_air=message.text.strip())
    await state.set_state(LoraStates.add_lora_weight)

    await bot.edit_message_text(message_id=message_to_edit_id, chat_id=message.chat.id, text="Введите вес Lora-модели:", reply_markup=await back_keyboard())

@router.callback_query(LoraStates.add_lora_shortname, F.data == "back")
async def back_from_add_lora_weight(callback: CallbackQuery, state: FSMContext, bot: Bot):
    new_lora_air = await state.get_value('new_lora_air')
    await add_lora_air(Message(message_id=int(uuid.uuid4()), text=new_lora_air, chat=callback.message.chat, date=callback.message.date), state, bot)

@router.message(LoraStates.add_lora_weight)
async def add_lora_weight(message: Message, state: FSMContext, bot: Bot):
    if message.bot:
        await message.delete()

    message_to_edit_id = await state.get_value('message_to_edit_id')

    await state.update_data(new_lora_weight=message.text.strip())
    await state.set_state(LoraStates.add_lora_shortname)
    await bot.edit_message_text(message_id=message_to_edit_id, chat_id=message.chat.id, text="Введите короткое название Lora-модели:", reply_markup=await back_keyboard())

@router.callback_query(LoraStates.add_lora_finish, F.data == "back")
async def back_from_add_lora_shortname(callback: CallbackQuery, state: FSMContext, bot: Bot):
    new_lora_weight = await state.get_value('new_lora_weight')
    await add_lora_weight(Message(message_id=int(uuid.uuid4()), text=new_lora_weight, chat=callback.message.chat, date=callback.message.date), state, bot)

@router.message(LoraStates.add_lora_shortname)
async def add_lora_shortname(message: Message, state: FSMContext, bot: Bot):
    if message.bot:
        await message.delete()

    message_to_edit_id = await state.get_value('message_to_edit_id')

    await state.update_data(new_lora_shortname=message.text.strip())
    await state.set_state(LoraStates.add_lora_finish)

    state_data = await state.get_data()
    new_lora_shortname = state_data.get('new_lora_shortname')
    new_lora_weight = state_data.get('new_lora_weight')
    new_lora_air = state_data.get('new_lora_air')
    new_lora_link = await get_link_to_model_from_air(new_lora_air)

    await state.update_data(new_lora={
        "shortname": new_lora_shortname,
        "weight": new_lora_weight,
        "model": new_lora_air,
        "link": new_lora_link
    })

    await bot.edit_message_text(message_id=message_to_edit_id, chat_id=message.chat.id, text=f"Добавлена новая Lora-модель:\n\n<b>Название:</b> {new_lora_shortname}\n<b>Вес:</b> {new_lora_weight}\n<b>AIR:</b> <code>{new_lora_air}</code>\n<b>Ссылка:</b> {new_lora_link}", reply_markup=await back_to_settings_keyboard())

@router.callback_query(LoraStates.add_lora_finish, F.data == "back")
async def back_from_add_lora_finish(callback: CallbackQuery, state: FSMContext, bot: Bot):
    new_lora_shortname = await state.get_value('new_lora_shortname')
    await add_lora_shortname(Message(message_id=int(uuid.uuid4()), text=new_lora_shortname, chat=callback.message.chat, date=callback.message.date), state, bot)


@router.callback_query(LoraStates.index, F.data.startswith("lora_"))
async def change_lora(callback: CallbackQuery, state: FSMContext):
    await state.set_state(LoraStates.lora_model)
    user_data = await state.get_value(f'user_{callback.from_user.id}')
    lora_to_change_air = callback.data.split('_')[1]
    picked_lora = next((lora for lora in user_data['lora'] if lora['model'] == lora_to_change_air), None)

    if picked_lora is None:
        await callback.message.edit_text("Lora-модель не найдена", reply_markup=await back_keyboard())
        return
    
    await state.update_data(lora_to_change_air=lora_to_change_air)

    text = f"<b><a href='{picked_lora['link']}'>{picked_lora['shortname']}</a></b>\nВес: {picked_lora['weight']}"
    await callback.message.edit_text(text=text, reply_markup=await get_lora_model_keyboard())



@router.callback_query(LoraStates.lora_model, F.data == "delete_lora")
async def delete_lora(callback: CallbackQuery, state: FSMContext):
    lora_air = await state.get_value('lora_to_change_air')

    key_for_update = f'user_{callback.from_user.id}'

    user_data = await state.get_value(key_for_update)
    user_data['lora'] = [lora for lora in user_data['lora'] if lora['model'] != lora_air]

    await state.update_data({key_for_update: user_data})

    await lora_settings(callback, state)
