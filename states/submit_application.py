from aiogram.dispatcher.filters.state import State, StatesGroup


class SubmitApplication(StatesGroup):
    be_agree = State()
    gender = State()
    which_cource = State()
    full_name = State()
    be_send = State()


class SendMessageToAdmin(StatesGroup):
    message_text = State()
    is_confirm = State()
    gender = State()
