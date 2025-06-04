from datetime import datetime, timedelta
from config import settings
from aiogram.fsm.context import FSMContext
from images.consts import DATETIME_FORMAT

async def check_debounce(state: FSMContext, event) -> bool:
    user_id = event.from_user.id
    user_data: dict = await state.get_value(f"user_{user_id}")
    
    if not user_data:
        return True
        
    last_request_datetime = datetime.strptime(user_data.get("last_request_datetime"), DATETIME_FORMAT) if user_data.get("last_request_datetime") else datetime.now() - timedelta(hours=settings.debounce_seconds)

    delta = datetime.now() - last_request_datetime
    if delta.seconds > settings.debounce_seconds:
        updated_user_data = user_data.copy()
        updated_user_data["last_request_datetime"] = datetime.now().strftime(DATETIME_FORMAT)
        await state.update_data({f"user_{user_id}": updated_user_data})
        return True
    return False

async def validate_user_data(state: FSMContext, user_id: int) -> bool:
    state_data = await state.get_data()
    user_data = state_data.get(f"user_{user_id}")
    if user_data:
        return True
    else:
        return False