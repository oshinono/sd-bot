from aiogram.fsm.state import State, StatesGroup

class ImageState(StatesGroup):
    txt_to_img = State()