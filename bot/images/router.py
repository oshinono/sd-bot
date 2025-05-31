import json
import uuid
from aiogram import Router
from aiogram.types import Message, InlineQuery, InlineQueryResultPhoto, InputMediaPhoto, InputMediaDocument
from images.enums import OutputFormat, OutputType
from images.states import ImageState
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from images.utils import check_debounce
from config import settings
from images.service import ImgToTxtService
from runware.types import IImageInference, ILora
from aiogram.filters import Command
from loguru import logger
router = Router()

@router.message(Command('img'))
async def img_command(message: Message, state: FSMContext):
    await state.set_state(ImageState.txt_to_img)
    await message.answer('Вы вошли в режим генерации изображения. Пожалуйста, введите текст для генерации изображения')

@router.message()
async def text_to_img(message: Message, bot: Bot, state: FSMContext):
    if not await check_debounce(state, message):
        await message.reply('Вы отправляете запросы слишком часто.')
        return
    
    prompt = message.text.strip()
    
    
    if not prompt:
        await message.answer("Пожалуйста, введите текст для генерации изображения")
        return
    
    sticker_message = await bot.send_sticker(chat_id=message.chat.id, sticker=settings.waiting_sticker_id)

    positive_prompt = prompt.split('|||')[0].strip()
    negative_prompt = prompt.split('|||')[1].strip() if len(prompt.split('|||')) > 1 else ''

    img_request = IImageInference(
        positivePrompt=positive_prompt,
        negativePrompt=negative_prompt,
        outputFormat=OutputFormat.png,
        outputType=OutputType.url,
        includeCost=True,
        outputQuality=95,
        steps=25,
        CFGScale=7.5,
        clipSkip=2,
        numberResults=3,
        height=1344,
        width=768,
        model='urn:air:sdxl:checkpoint:civitai:260267@293564',
        scheduler='DPM++ 2M SDE',
        # lora=[ILora(model='civitai:838474@938064', weight=0.7)],
    )

    try:
        imgs = await ImgToTxtService.generate(img_request)
        img = imgs[0]
        logger.info(img)

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

    

    
    