from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.deep_linking import get_start_link

agree_buttons = InlineKeyboardMarkup(row_width=2)
agree_buttons.insert(InlineKeyboardButton(
    text="Ha", callback_data="agree_yes"))
agree_buttons.insert(InlineKeyboardButton(
    text="Yo'q", callback_data="agree_no"))


async def button_for_admins_application(user_id, message_id=None, chat_id=None):
    for_accept_link = await get_start_link(f"accept:{user_id}:{chat_id}:{message_id}", encode=True)
    button_for_admins = InlineKeyboardMarkup(row_width=2)

    button_for_admins.insert(InlineKeyboardButton(
        text="✅ Qabul qilish",
        url=for_accept_link)
    )

    for_cancel_link = await get_start_link(f"cancel:{user_id}:{chat_id}:{message_id}", encode=True)
    button_for_admins.insert(InlineKeyboardButton(
        text="❌ Bekor qilish",
        url=for_cancel_link)
    )

    for_message_link = await get_start_link(f"message_to_user:{user_id}", encode=True)
    button_for_admins.insert(InlineKeyboardButton(
        text="📝 Userga xabar yuborish",
        url=for_message_link)
    )
    return button_for_admins


async def button_for_admins_question(question_id):
    link = await get_start_link(f"question:{question_id}")
    buttons = InlineKeyboardMarkup(row_width=2)
    buttons.insert(InlineKeyboardButton(
        text="Javob berish",
        url=link)
    )
    return buttons
