import re
from loguru import logger
import asyncio

async def get_link_to_model_from_air(air: str) -> str:
    #пример urn:air:sd1:checkpoint:civitai:23521@28100
    values = air.split(':')
    if len(values) > 2:
        return f"https://civitai.com/models/{values[5].split('@')[0]}"
    else:
        return await get_link_to_model_from_short_air(air)
    
async def get_link_to_model_from_short_air(short_air: str) -> str:
    #пример civitai:23521@28100
    values = short_air.split(':')
    model_id = values[1].split('@')[0]
    return f"https://civitai.com/models/{model_id}"

async def validate_air(air: str) -> bool:
    return re.match(r"^(?:urn:)?(?:air:)?(?:([a-zA-Z0-9_\-\/]+):)?(?:([a-zA-Z0-9_\-\/]+):)?([a-zA-Z0-9_\-\/]+):([a-zA-Z0-9_\-\/]+)(?:@([a-zA-Z0-9_\-]+))?(?:\.([a-zA-Z0-9_\-]+))?$", air) is not None

async def ping_bot(bot):
    while True:
        try:
            await bot.get_me()
            logger.debug("Пинганул бота")
        except Exception as e:
            logger.error(f"Пинг failed: {e}")
        await asyncio.sleep(900)