from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.const_texts import add_course, add_group, find_user, list_group, list_course


def make_buttons(words: list, row_width: int = 1) -> ReplyKeyboardMarkup:
    buttons_group = ReplyKeyboardMarkup(
        row_width=row_width, resize_keyboard=True)
    for word in words:
        if word is not None:
            buttons_group.insert(KeyboardButton(text=word))
    return buttons_group


admin_buttons = make_buttons(
    words=[
        add_group,
        # add_course,
        # find_user,
        list_group,
        # list_course
    ],
    row_width=2
)
