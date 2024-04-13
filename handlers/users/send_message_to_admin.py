import pytz
from datetime import datetime
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from loader import dp, db, bot
from filters import IsPrivate
from utils import get_now
from utils.const_texts import submit_application, send_message_to_admin_text
from keyboards.inline.inline_buttons import agree_buttons
from keyboards.default.default_buttons import make_buttons
from states.submit_application import SubmitApplication, SendMessageToAdmin
from .apply_application import send_message_to_admin


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
        text=f"Jo'natuvchi: {full_name}\n\nYuborilayotgan savol: <i>{text}</i>",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        text="Savol jo'natilsinmi?",
        reply_markup=agree_buttons
    )
    await state.update_data(question=text)
    await state.update_data(sender_id=message.from_user.id)
    await SendMessageToAdmin.is_confirm.set()


@dp.callback_query_handler(text="agree_no", state=SendMessageToAdmin.is_confirm)
async def submit_app(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(text="ℹ️ Savolni jo'natish bekor qilindi!", reply_markup=make_buttons(words=[f'{send_message_to_admin_text}', f"{submit_application}"], row_width=2))
    await state.finish()


@dp.callback_query_handler(text="agree_yes", state=SendMessageToAdmin.is_confirm)
async def submit_app(call: types.CallbackQuery, state: FSMContext):
    question_data = await state.get_data()
    question = question_data.get("question")
    sender_full_name = call.from_user.full_name

    await db.add_question(
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
        text = f"Jo'natuvchi: {sender_full_name}\nUsername: {username}\n\nYuborilgan savol: <i>{question}</i>"
    else:
        text = f"Jo'natuvchi: {sender_full_name}\n\nYuborilgan savol: <i>{question}</i>"

    send_status = await send_message_to_admin(gender=gender, text=text)
    if not send_status:
        await bot.send_message(chat_id=1018544836, text="⚡ Iltimos admin uchun guruhlarni biriktiring.")
        return
    await call.message.answer("✅ Savolingiz muaffaqiyatli yuborildi, tez orada javob qaytariladi.")
