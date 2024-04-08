from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

agree_buttons = InlineKeyboardMarkup(row_width=2)
agree_buttons.insert(InlineKeyboardButton(text="Ha", callback_data="agree_yes"))
agree_buttons.insert(InlineKeyboardButton(text="Yo'q", callback_data="agree_no"))