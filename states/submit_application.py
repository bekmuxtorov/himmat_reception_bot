from aiogram.dispatcher.filters.state import State, StatesGroup


class SubmitApplication(StatesGroup):
    be_agree = State()
    gender = State()
    full_name = State()
    be_send = State()
