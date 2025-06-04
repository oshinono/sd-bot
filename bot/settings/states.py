from aiogram.fsm.state import State, StatesGroup

class SettingsStates(StatesGroup):
    index = State()
    setting_update = State()
    model_update_air = State()
    model_update_shortname = State()
    model_update_finish = State()