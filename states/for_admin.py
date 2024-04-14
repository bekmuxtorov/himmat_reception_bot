from aiogram.dispatcher.filters.state import State, StatesGroup


class AcceptApp(StatesGroup):
    first_data = State()
    confirm = State()


class CancelApp(StatesGroup):
    confirm = State()


class MessageToUser(StatesGroup):
    confirm = State()
