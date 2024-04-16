from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from loader import dp, bot, db
from filters import IsPrivate
from utils.const_texts import submit_application, terms, send_message_to_admin_text
from utils.set_message import set_message
from keyboards.inline.inline_buttons import agree_buttons, button_for_admins_application, button_for_admins_question
from keyboards.default.default_buttons import make_buttons
from states.submit_application import SubmitApplication


@dp.message_handler(IsPrivate(), text="❌ Bekor qilish", state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer("💡 Jarayon bekor qilindi!", reply_markup=make_buttons(words=[f'{send_message_to_admin_text}', f"{submit_application}"], row_width=2))
    await state.finish()


@dp.message_handler(IsPrivate(), text=submit_application)
async def bot_echo(message: types.Message):
    await message.answer(terms, reply_markup=ReplyKeyboardRemove())
    await message.answer(text="💡 Yuqoridagi shartlarga rozimisiz?", reply_markup=agree_buttons)
    await SubmitApplication.be_agree.set()


@dp.callback_query_handler(text="agree_no", state=SubmitApplication.be_agree)
async def bot_echo(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        text="Shartlarga rozi bo'lmasangiz loyihada qatnashish uchun so'rov jo'nata olmaysiz.",
        reply_markup=make_buttons(
            words=[f'{send_message_to_admin_text}', f"{submit_application}"], row_width=2)
    )
    await state.finish()


@dp.callback_query_handler(text="agree_yes", state=SubmitApplication.be_agree)
async def bot_echo(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("Jinsni tanglang:", reply_markup=make_buttons(["Erkak", "Ayol"], row_width=2))
    await SubmitApplication.gender.set()


@dp.message_handler(IsPrivate(), state=SubmitApplication.gender, text=["Erkak", "Ayol"])
async def submit_app(message: types.Message, state: FSMContext):
    gender = message.text
    await state.update_data(gender=gender)
    await db.update_user_gender(telegram_id=message.from_user.id, gender=gender)
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
    await call.message.answer(text="ℹ️ Ariza bekor qilindi!\n\nQayta urinib ko'rishingiz mumkin.", reply_markup=make_buttons(words=[f'{send_message_to_admin_text}', f"{submit_application}"], row_width=2))
    await state.finish()


@dp.callback_query_handler(text="agree_yes", state=SubmitApplication.be_send)
async def submit_app(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_data = await state.get_data()
    new_application = await set_message(user_data=user_data, to_admin=True)
    message_status = await send_message_to_admin(gender=user_data.get("gender"), text=new_application, user_id=call.from_user.id, is_application=True)
    if message_status:
        await call.message.answer("✅ Arizangiz ko'rib chiqish uchun adminlar guruhiga yuborildi!\n\nTez orada qayta aloqaga chiqiladi.")
        await state.finish()
        return
    await bot.send_message(chat_id=1603330179, text="⚡ Iltimos admin uchun guruhlarni biriktiring.")
    await call.message.answer("ℹ️ Ariza jo'natishda muammo paydo bo'ldi, iltimos birozdan keyin qayta urinib ko'ring.", reply_markup=make_buttons(words=[f'{send_message_to_admin_text}', f"{submit_application}"], row_width=2))
    await state.finish()


async def get_group_id():
    data_man = await db.select_group(for_whom="man_admin")
    data_woman = await db.select_group(for_whom="woman_admin")
    return {
        "for_man": data_man.get("group_id") if data_man else None,
        "for_woman": data_woman.get("group_id") if data_woman else None
    }


async def send_message_to_admin(gender: str, text: str, user_id: int, is_application: bool = False, question_id: int = None):
    groups = await get_group_id()
    if None in groups.values():
        return False

    if gender == "Erkak":
        group_id = groups.get("for_man")
        service_message = await bot.send_message(
            chat_id=group_id,
            text=text,
            reply_markup=await button_for_admins_application(user_id=user_id) if is_application else await button_for_admins_question(question_id=question_id, chat_id=group_id, user_id=user_id)
        )
        await bot.edit_message_text(
            text=text,
            chat_id=group_id,
            message_id=service_message.message_id,
            disable_web_page_preview=True,
            reply_markup=await button_for_admins_application(user_id=user_id, chat_id=group_id, message_id=service_message.message_id) if is_application else await button_for_admins_question(question_id=question_id, chat_id=group_id, message_id=service_message.message_id, user_id=user_id)
        )
    else:
        group_id = groups.get("for_woman")
        service_message = await bot.send_message(
            chat_id=group_id,
            text=text,
            reply_markup=await button_for_admins_application(user_id=user_id, chat_id=group_id) if is_application else await button_for_admins_question(question_id=question_id, chat_id=group_id, user_id=user_id)
        )
        await bot.edit_message_text(
            text=text,
            chat_id=group_id,
            message_id=service_message.message_id,
            disable_web_page_preview=True,
            reply_markup=await button_for_admins_application(user_id=user_id, chat_id=group_id, message_id=service_message.message_id) if is_application else await button_for_admins_question(question_id=question_id, chat_id=group_id, message_id=service_message.message_id, user_id=user_id)
        )

    return True
