import json
import uuid
from aiogram import Router
from aiogram.types import Message, InlineQuery, InlineQueryResultPhoto, InputMediaPhoto, InputMediaDocument, CallbackQuery
from enums import OutputFormat, OutputType
from aiogram import Bot, F
from aiogram.fsm.context import FSMContext
from runware import ILora
from images.utils import check_debounce
import time
from config import settings
from images.service import ImgToTxtService
from schemas import UserSettings
from runware.types import IImageInference
from images.states import ImageState
from loguru import logger
from images.keyboards import get_stop_gen_keyboard  
from index.router import start

router = Router()

@router.callback_query(F.data == "generate_image")
async def img_command(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ImageState.txt_to_img)
    await callback.message.edit_text('Вы вошли в режим генерации изображения. Пожалуйста, введите текст для генерации изображения')
    await callback.message.answer('Используйте кнопку ниже, чтобы выйти из режима генерации.\n\n<b>💡 Подсказка:</b> Вы можете использовать <code>|||</code> для разделения положительного и отрицательного промптов.', reply_markup=await get_stop_gen_keyboard())

@router.message(ImageState.txt_to_img, F.text == "🛑 Выйти из режима генерации")
async def stop_gen(message: Message, state: FSMContext):
    await start(message, state)

@router.message(ImageState.txt_to_img)
async def text_to_img(message: Message, bot: Bot, state: FSMContext):
    if not await check_debounce(state, message):
        await message.reply('Вы отправляете запросы слишком часто.')
        return
    
    prompt = message.text.strip()
    
    if not prompt:
        await message.answer("Пожалуйста, введите текст для генерации изображения")
        return
    
    user_data = await state.get_value(f'user_{message.from_user.id}')

    validated_user_data = UserSettings(**user_data)
    dump = validated_user_data.model_dump(exclude={'last_request_datetime'})

    dump['model'] = dump['model']['air']
    dump['lora'] = [ILora(model=lora['model'], weight=lora['weight']) for lora in dump['lora']]
    
    sticker_message = await bot.send_sticker(chat_id=message.chat.id, sticker=settings.waiting_sticker_id)

    positive_prompt = prompt.split('|||')[0].strip()
    negative_prompt = prompt.split('|||')[1].strip() if len(prompt.split('|||')) > 1 else ''

    img_request = IImageInference(
        positivePrompt=positive_prompt,
        negativePrompt=negative_prompt,
        **dump
    )

    try:
        time_start = time.time()
        logger.info(f"Positive: {positive_prompt},\nNegative: {negative_prompt}, UserID: {message.from_user.id}")
        imgs = await ImgToTxtService.generate(img_request)
        time_end = time.time()

        log_data = {'time_elapsed': time_end - time_start, 'imgs': [img.imageURL for img in imgs], 'user_id': message.from_user.id}
        logger.info(json.dumps(log_data, indent=2))

        photo_media = []
        document_media = []
        for img in imgs: 
            photo_media.append(InputMediaPhoto(media=img.imageURL))
            document_media.append(InputMediaDocument(media=img.imageURL))

        await message.reply_media_group(media=photo_media)
        await message.answer_media_group(media=document_media)
    except Exception as e:
        logger.error(e)
        await message.reply('Произошла ошибка: ' + str(e))
        return
    finally:
        await bot.delete_message(message.chat.id, sticker_message.message_id)
    

@router.inline_query()
async def txt_to_img_inline(inline_query: InlineQuery, state: FSMContext):
    prompt = inline_query.query.strip()

    if not prompt:
        return

    if not await check_debounce(state, inline_query):
        return
    
    positive_prompt = prompt.split('|||')[0].strip()
    negative_prompt = prompt.split('|||')[1].strip() if len(prompt.split('|||')) > 1 else ''

    
    
    # await inline_query.answer(results=[
    #     InlineQueryResultArticle(
    #         id=str(uuid.uuid4()),
    #         title="🪄 Генерирую...",
    #         input_message_content=InputTextMessageContent(
    #             message_text="⏳ Пожалуйста, подождите..."
    #         )
    #     )
    # ], cache_time=0)


    img_request = IImageInference(
        positivePrompt=positive_prompt,
        negativePrompt=negative_prompt,
        outputFormat=OutputFormat.jpg,
        outputType=OutputType.url,
        includeCost=True,
        outputQuality=95,
        steps=30,
        CFGScale=5,
        clipSkip=1,
        numberResults=1,
        height=960,
        width=640,
        model='urn:air:sdxl:checkpoint:civitai:1205141@1357130',
        scheduler='Euler A',
        # lora=[ILora(model='civitai:412551@969720', weight=0.5)],
        
    )
    logger.info('Отправил')
    imgs = await ImgToTxtService.generate(img_request)
    logger.info(imgs[0].imageURL)

    await inline_query.answer(
        results=[InlineQueryResultPhoto(
            id=uuid.uuid4().hex[:4],
            photo_url=imgs[0].imageURL,
            thumbnail_url=imgs[0].imageURL,
            photo_width=512,
            photo_height=512,
            caption=imgs[0].imageURL,
            description=prompt
        )],
        cache_time=0,
        is_personal=True
    )

