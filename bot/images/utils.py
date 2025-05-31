from datetime import datetime
from config import settings
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineQuery

async def check_debounce(state: FSMContext, inline_query: InlineQuery) -> bool:
    state_data = await state.get_data()

    user_id = inline_query.from_user.id
    user_data = state_data.get(f"user_{user_id}")

    if user_data:
        delta = datetime.now() - user_data.get("last_request_datetime", 0)
        if delta.seconds > settings.debounce_seconds:
            updated_user_data = user_data.copy()
            updated_user_data["last_request_datetime"] = datetime.now()
            await state.update_data({f"user_{user_id}": updated_user_data})
        else:
            return False
    else:
        await state.update_data({f"user_{user_id}": {"last_request_datetime": datetime.now()}})
    return True