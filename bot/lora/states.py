from aiogram.fsm.state import State, StatesGroup

class LoraStates(StatesGroup):
    index = State()
    add_lora_air = State()
    add_lora_weight = State()
    add_lora_shortname = State()
    add_lora_finish = State()
    lora_model = State()
    update_lora = State()
    delete_lora = State()
