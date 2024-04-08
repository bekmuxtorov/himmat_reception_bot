from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from loader import dp
from filters import IsPrivate
from utils.const_texts import submit_application, terms, send_message_to_admin
from utils.set_message import set_message
from keyboards.inline.inline_buttons import agree_buttons
from keyboards.default.default_buttons import make_buttons
from states.submit_application import SubmitApplication


@dp.message_handler(IsPrivate(), text=submit_application)
async def bot_echo(message: types.Message):
    await message.answer(terms, reply_markup=ReplyKeyboardRemove())
    await message.answer(text="💡 Yuqoridagi shartlarga rozimisiz?", reply_markup=agree_buttons)
    await SubmitApplication.be_agree.set()


@dp.callback_query_handler(text="agree_no", state=SubmitApplication.be_agree)
async def bot_echo(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer(
        text="Shartlarga rozi bo'lmasangiz loyihada qatnashish uchun so'rov jo'nata olmaysiz.",
        reply_markup=make_buttons([send_message_to_admin])
    )


@dp.callback_query_handler(text="agree_yes", state=SubmitApplication.be_agree)
async def bot_echo(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Jinsni tanglang:", reply_markup=make_buttons(["Erkak", "Ayol"], row_width=2))
    await SubmitApplication.gender.set()


@dp.message_handler(IsPrivate(), state=SubmitApplication.gender, text=["Erkak", "Ayol"])
async def submit_app(message: types.Message, state: FSMContext):
    gender = message.text
    await state.update_data(gender=gender)
    await message.answer(text="👤 Ism va familiyani kiriting:", reply_markup=ReplyKeyboardRemove())
    await SubmitApplication.full_name.set()


@dp.message_handler(IsPrivate(), state=SubmitApplication.gender)
async def submit_app(message: types.Message, state: FSMContext):
    await message.answer(text="ℹ️ Iltimos quyidagilardan birini tanglang:", reply_markup=make_buttons(["Erkak", "Ayol"], row_width=2))
    await SubmitApplication.gender.set()


@dp.message_handler(IsPrivate(), state=SubmitApplication.full_name)
async def submit_app(message: types.Message, state: FSMContext):
    full_name = message.text
    if len(full_name.split(' ')) < 2:
        await message.answer("💡 Iltimos ism va familiyani to'liq kiriting:")
        return

    await state.update_data(full_name=full_name)
    user_data = await state.get_data()
    new_message_for_user = await set_message(user_data, to_admin=False)
    await message.answer(new_message_for_user)
    await message.answer("⚡ Ariza yuborilsinmi?", reply_markup=agree_buttons)
    await SubmitApplication.be_send.set()


@dp.callback_query_handler(text="agree_no", state=SubmitApplication.be_send)
async def submit_app(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        text="ℹ️ Ariza bekor qilindi!\n\nQayta urinib ko'rishingiz mumkin.",
        reply_markup=make_buttons(
            [send_message_to_admin, submit_application], row_width=2)
    )
    await state.finish()


@dp.callback_query_handler(text="agree_yes", state=SubmitApplication.be_send)
async def submit_app(call: types.Message, state: FSMContext):
    user_data = await state.get_data()
    new_application = await set_message(user_data=user_data, to_admin=True)
