from datetime import datetime
from aiogram.fsm.context import FSMContext
from schemas import BaseSDModel, UserSettings
from enums import OutputFormat, OutputType

async def load_default_user_settings(state: FSMContext, user_id: int):
    default_settings = UserSettings(
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
        model=BaseSDModel(
            air='x:42@1379960',
            link='https://civitai.com/models/1224788?modelVersionId=1199750',
            shortname='Prefect illustrious XL'
        ),
        scheduler='Euler A',
        lora=[]
    )
    await state.update_data({f'user_{user_id}': default_settings.model_dump()})
        