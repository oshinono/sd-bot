import random
import uuid
from aiogram import Router, F, Bot
from aiogram.filters import or_f
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from settings.states import SettingsStates
from schemas import BaseSDModel, UserImgGenSettings
from keyboards import back_keyboard
from lora.states import LoraStates
from settings.keyboards import get_settings_keyboard, back_to_settings_keyboard
from settings.utils import format_text_for_settings
from utils import validate_air, get_link_to_model_from_air

router = Router()

@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(SettingsStates.index)

    if callback.message.bot:
        await state.update_data(settings_message_id=callback.message.message_id)

    state_data = await state.get_data()
    user_data = state_data[f'user_{callback.from_user.id}']
    data = UserImgGenSettings(**user_data)
    text = await format_text_for_settings(data)

    message_to_edit_id = await state.get_value('settings_message_id')
    await bot.edit_message_text(disable_web_page_preview=True, message_id=message_to_edit_id, chat_id=callback.message.chat.id, text=text, reply_markup=await get_settings_keyboard(data))

@router.callback_query(or_f(SettingsStates.setting_update, LoraStates.index), F.data == "back")
async def back_from_setting_change(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await settings(callback, state, bot)

@router.callback_query(LoraStates.add_lora_finish, F.data == "back_to_settings")
async def back_to_settings_from_add_lora(callback: CallbackQuery, state: FSMContext, bot: Bot):
    new_lora = await state.get_value('new_lora')
    user_data = await state.get_value(f'user_{callback.from_user.id}')
    user_data['lora'].append(new_lora)

    await state.update_data({f'user_{callback.from_user.id}': user_data})
    await state.update_data(new_lora=None, new_lora_shortname=None, new_lora_weight=None, new_lora_air=None)

    await settings(callback, state, bot)

@router.callback_query(SettingsStates.model_update_finish, F.data == "back_to_settings")
async def back_to_settings_from_model_update(callback: CallbackQuery, state: FSMContext, bot: Bot):
    updated_model_air = await state.get_value('updated_model_air')
    updated_model_shortname = await state.get_value('updated_model_shortname')
    link = await get_link_to_model_from_air(updated_model_air)

    model = BaseSDModel(air=updated_model_air, shortname=updated_model_shortname, link=link)

    user_data = await state.get_value(f'user_{callback.from_user.id}')
    user_data['model'] = model.model_dump()
    await state.update_data({f'user_{callback.from_user.id}': user_data})

    await settings(callback, state, bot)


@router.message(SettingsStates.setting_update)
async def change_setting_value(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    
    state_data = await state.get_data()
    user_data = state_data[f'user_{message.from_user.id}']
    setting_to_change = state_data['setting_to_change']

    user_data[setting_to_change] = message.text
    await state.update_data({f'user_{message.from_user.id}': user_data})

    await settings(CallbackQuery(id=uuid.uuid4().hex, from_user=message.from_user, chat_instance=uuid.uuid4().hex, message=Message(message_id=state_data['settings_message_id'], chat=message.chat, date=message.date, from_user=message.from_user, text=message.text)), state, bot)


# ------------------------------------------------------------


@router.callback_query(SettingsStates.model_update_air, F.data == "back")
async def back_from_model_update_air(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await settings(callback, state, bot)

@router.callback_query(SettingsStates.index, F.data == "settings_model")
async def change_model(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.model_update_air)
    await state.update_data(message_to_edit_id=callback.message.message_id)

    await callback.message.edit_text("Введите AIR модели:", reply_markup=await back_keyboard())

@router.callback_query(SettingsStates.model_update_shortname, F.data == "back")
async def back_from_model_update_shortname(callback: CallbackQuery, state: FSMContext):
    await change_model(callback, state)

@router.message(SettingsStates.model_update_air)
async def change_model_air(message: Message, state: FSMContext, bot: Bot):
    if message.bot:
        await message.delete()
    message_to_edit_id = await state.get_value('message_to_edit_id')

    if not await validate_air(message.text.strip()):
        await bot.edit_message_text(message_id=message_to_edit_id, chat_id=message.chat.id, text="Неверный AIR модели\n\nПример: <code>urn:air:sdxl:checkpoint:civitai:260267@293564</code>", reply_markup=await back_keyboard())
        return

    await state.update_data(updated_model_air=message.text.strip())
    await state.set_state(SettingsStates.model_update_shortname)
    await bot.edit_message_text(message_id=message_to_edit_id, chat_id=message.chat.id, text="Введите название модели:", reply_markup=await back_keyboard())

@router.callback_query(SettingsStates.model_update_finish, F.data == "back")
async def back_from_model_update_air(callback: CallbackQuery, state: FSMContext, bot: Bot):
    updated_model_air = await state.get_value('updated_model_air')
    await change_model_air(Message(message_id=random.randint(1, 1000000), date=callback.message.date, chat=callback.message.chat, text=updated_model_air), state, bot)

@router.message(SettingsStates.model_update_shortname)
async def change_model_shortname(message: Message, state: FSMContext, bot: Bot):
    if message.bot:
        await message.delete()

    message_to_edit_id = await state.get_value('message_to_edit_id')

    await state.update_data(updated_model_shortname=message.text.strip())
    await state.set_state(SettingsStates.model_update_finish)

    updated_model_air = await state.get_value('updated_model_air')
    updated_model_shortname = message.text.strip()

    await bot.edit_message_text(message_id=message_to_edit_id, chat_id=message.chat.id, text=f"Модель успешно обновлена:\n\n<b>{updated_model_shortname}</b>\n<b>{updated_model_air}</b>", reply_markup=await back_to_settings_keyboard())


# ------------------------------------------------------------

@router.callback_query(F.data.startswith("settings_"), SettingsStates.index)
async def change_setting(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsStates.setting_update)

    state_data = await state.get_data()
    user_data = state_data[f'user_{callback.from_user.id}']
    setting_to_change = callback.data.split('_')[1]
    await state.update_data(setting_to_change=setting_to_change)

    setting_to_change_value = user_data[setting_to_change]
    
    await callback.message.edit_text(f"Введите новое значение для настройки\n\nТекущее значение {setting_to_change}: {setting_to_change_value}", reply_markup=await back_keyboard())