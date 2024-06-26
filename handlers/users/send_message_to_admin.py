import pytz
from datetime import datetime
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from loader import dp, db, bot
from filters import IsPrivate
from utils import get_now
from utils.const_texts import submit_application, send_message_to_admin_text
from keyboards.inline.inline_buttons import agree_buttons, button_for_admins_application, button_for_admins_question
from keyboards.default.default_buttons import make_buttons
from states.submit_application import SubmitApplication, SendMessageToAdmin
from data.config import FOR_MAN_ADMINS, FOR_WOMAN_ADMINS


@dp.message_handler(IsPrivate(), text="💡 Javob yo'llash")
@dp.message_handler(IsPrivate(), text=send_message_to_admin_text)
async def bot_echo(message: types.Message):
    user_data = await db.select_user(telegram_id=message.from_user.id)
    gender = user_data.get("gender")
    if not gender:
        await message.answer("Jinsni tanglang:", reply_markup=make_buttons(["Erkak", "Ayol"], row_width=2))
        await SendMessageToAdmin.gender.set()
        return
    await message.answer(
        text="📝 Xabaringizni quyiga yozing:",
        reply_markup=make_buttons(["❌ Bekor qilish"])
    )
    await SendMessageToAdmin.message_text.set()


@dp.message_handler(IsPrivate(), state=SendMessageToAdmin.gender, text=["Erkak", "Ayol"])
async def submit_app(message: types.Message, state: FSMContext):
    gender = message.text
    await state.update_data(gender=gender)
    await db.update_user_gender(telegram_id=message.from_user.id, gender=gender)
    await message.answer(
        text="📝 Xabaringizni quyiga yozing:",
        reply_markup=make_buttons(["❌ Bekor qilish"])
    )
    await SendMessageToAdmin.message_text.set()


@dp.message_handler(IsPrivate(), state=SendMessageToAdmin.gender)
async def submit_app(message: types.Message, state: FSMContext):
    await message.answer(text="ℹ️ Iltimos quyidagilardan birini tanglang:", reply_markup=make_buttons(["Erkak", "Ayol"], row_width=2))
    await SubmitApplication.gender.set()


@dp.message_handler(IsPrivate(), state=SendMessageToAdmin.message_text)
async def send_to_admin(message: types.Message, state: FSMContext):
    text = message.text
    if text in ('/start', '/help', '❌ Bekor qilish'):
        await message.answer("💡 Iltimos savolingizni kiriting:")
        return
    full_name = message.from_user.full_name
    await message.answer(
        text=f"Jo'natuvchi: {full_name}\n\nYuborilayotgan xabar: <i>{text}</i>",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        text="Xabar jo'natilsinmi?",
        reply_markup=agree_buttons
    )
    await state.update_data(question=text)
    await state.update_data(sender_id=message.from_user.id)
    await SendMessageToAdmin.is_confirm.set()


@dp.callback_query_handler(text="agree_no", state=SendMessageToAdmin.is_confirm)
async def submit_app(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text="ℹ️ Xabar jo'natish bekor qilindi!", reply_markup=make_buttons(words=[f'{send_message_to_admin_text}', f"{submit_application}"], row_width=2))
    await state.finish()


@dp.callback_query_handler(text="agree_yes", state=SendMessageToAdmin.is_confirm)
async def submit_app(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    question_data = await state.get_data()
    question = question_data.get("question")
    sender_full_name = call.from_user.full_name
    user_id = call.from_user.id

    question_id = await db.add_question(
        sender_id=question_data.get("sender_id"),
        sender_full_name=sender_full_name,
        question=question,
        created_at=await get_now(),
    )
    user_data = await db.select_user(telegram_id=call.from_user.id)
    gender = user_data.get("gender")
    username = user_data.get("username")
    if username:
        username = f"<a href='https://t.me/{username}'>@{username}</a>"
        text = f"💡 Userdan xabar keldi.\n\nJo'natuvchi: {sender_full_name}\nUsername: {username}\n\nYuborilgan xabar: <i>{question}</i>"
    else:
        text = f"💡 Userdan xabar keldi.\n\nJo'natuvchi: {sender_full_name}\nUserID: {user_id}\n\nYuborilgan xabar: <i>{question}</i>"
    
    await send_message_to_admin_via_topic(
        text=text,
        for_purpose="accepted_messages",
        gender=gender,
        question_id=question_id,
        user_id=user_id
        )

    await call.message.answer("✅ Xabaringiz muaffaqiyatli yuborildi, tez orada javob qaytariladi.")
    await state.finish()


async def send_message_to_admin_via_topic(text: str, for_purpose: str, gender: str = None, user_id: int = None, is_application: bool = None, question_id: int = None, course_id=None):
    groups = {
        "Erkak": FOR_MAN_ADMINS,
        "Ayol": FOR_WOMAN_ADMINS,
    }
    if gender and (is_application or question_id):
        chat_id = groups.get(gender)
        topic_id = await db.get_topic_id(group_id=chat_id, for_purpose=for_purpose)
        service_message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            message_thread_id=topic_id,
            reply_markup=await button_for_admins_application(user_id=user_id, course_id=course_id) if is_application else await button_for_admins_question(question_id=question_id, chat_id=chat_id, user_id=user_id)
        )
        await bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=service_message.message_id,
            reply_markup=await button_for_admins_application(user_id=user_id, chat_id=chat_id, message_id=service_message.message_id, course_id=course_id) if is_application else await button_for_admins_question(question_id=question_id, chat_id=chat_id, message_id=service_message.message_id, user_id=user_id)
        )
        return
    
    if gender:
        chat_id = groups.get(gender)
        topic_id = await db.get_topic_id(group_id=chat_id, for_purpose=for_purpose)
        service_message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            message_thread_id=topic_id,
        )
        return


    for group in groups.values():
        topic_id = await db.get_topic_id(group_id=group, for_purpose=for_purpose)
        await bot.send_message(
            text=text,
            chat_id=group,
            message_thread_id=topic_id
        )
