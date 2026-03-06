from aiogram.fsm.state import State, StatesGroup


class AdminBroadcast(StatesGroup):
    text = State()


class AdminCredits(StatesGroup):
    target_tg_id = State()
    amount = State()
