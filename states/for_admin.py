from aiogram.dispatcher.filters.state import State, StatesGroup


class AddGroup(StatesGroup):
    submit_id = State()
    for_whom = State()
    name = State()


class AddCource(StatesGroup):
    name = State()
    description = State()
    for_man_group_id = State()
    for_man_group_name = State()
    for_woman_group_id = State()
    for_woman_group_name = State()


class AcceptApp(StatesGroup):
    first_data = State()
    confirm = State()


class CancelApp(StatesGroup):
    first_data = State()
    cause_text = State()
    confirm = State()


class MessageToUser(StatesGroup):
    qestion = State()


class AnswerToUser(StatesGroup):
    answer = State()
