from aiogram.fsm.state import State, StatesGroup


class PostCreation(StatesGroup):
    topic = State()
    audience = State()
    tone = State()
    platform = State()
    requirements = State()
    confirm = State()
    editing = State()
