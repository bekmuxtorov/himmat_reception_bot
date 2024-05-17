from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from loader import dp, bot, db
from filters import IsPrivate
from utils import get_now
from utils.const_texts import submit_application, send_message_to_admin_text
from utils.set_message import set_message
from keyboards.inline.inline_buttons import agree_buttons, button_for_admins_application, button_for_admins_question
from keyboards.default.default_buttons import make_buttons
from states.submit_application import SubmitApplication
from .send_message_to_admin import send_message_to_admin_via_topic


@dp.message_handler(IsPrivate(), text="❌ Bekor qilish", state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer("💡 Jarayon bekor qilindi!", reply_markup=make_buttons(words=[f'{send_message_to_admin_text}', f"{submit_application}"], row_width=2))
    await state.finish()


@dp.message_handler(IsPrivate(), text=submit_application)
async def bot_echo(message: types.Message):


    await bot.copy_message(
        chat_id= message.chat.id,
        from_chat_id=-1001864130751,
        message_id=2915
    )
    # https://t.me/c/1938636106/1/195
    await bot.copy_message(
        chat_id= message.chat.id,
        from_chat_id=-1001864130751,
        message_id=2916
    )   
    service_message = await message.answer('.', reply_markup=ReplyKeyboardRemove())
    await service_message.delete() 
    await bot.copy_message(
        chat_id= message.chat.id,
        from_chat_id=-1001864130751,
        message_id=2917
    )
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
    # courses = await db.select_all_courses()
    # courses_name = [item.get("name")
    #                 for item in courses] + ["❌ Bekor qilish"]
    # await message.answer(text="📃 Kurslardan birini tanglang:", reply_markup=make_buttons(words=courses_name))
    course_id = 12
    await state.update_data(course_id=course_id)
    await state.update_data(course_name="Xos guruh")
    await message.answer("📝 Ism va familiyangizni kiriting:", reply_markup=ReplyKeyboardRemove())
    await SubmitApplication.full_name.set()


# @dp.message_handler(IsPrivate(), state=SubmitApplication.which_cource)
# async def submit_app(message: types.Message, state: FSMContext):
    # course_name = message.text
    # courses = await db.select_all_courses()
    # courses_name = {item.get("name"): item.get("id") for item in courses}
    # if not course_name in courses_name.keys():
    #     await message.answer(
    #         text="📝 Iltimos quyidagilardan biri tanglang:",
    #         reply_markup=make_buttons(
    #             words= list(courses_name.keys()) + ["❌ Bekor qilish"]
    #         )
    #     )
    #     return



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
    application_data = await state.get_data()
    telegram_id = call.message.from_user.id
    full_name = application_data.get("full_name")
    username = call.message.from_user.username
    gender = application_data.get("gender")
    course_id = application_data.get("course_id")
    course_name = application_data.get("course_name")
    user = await db.select_user(telegram_id=telegram_id)
    if not user:
        user = await db.add_user(
            full_name=full_name,
            username=username,
            telegram_id=telegram_id,
            created_at=await get_now()
        )
    else:
        if (username != user.get("username")) or (full_name != user.get("full_name")):
            await db.update_user("username", username, telegram_id)
            await db.update_user("full_name", full_name, telegram_id)
            text = "📝 User ma'lumotlarini o'zgartirdi.\n\n"
            text += f"👤 <b>FISH</b>: {full_name}\n"
            text += f"🆔 <b>Telegram ID</b>: <code>{telegram_id}</code>\n"
            text += f"👤 <b>Username</b>: {username}\n"
            text += f"💡 <b>Jins</b>: {gender}"
            await send_message_to_admin_via_topic(
                text=text,
                for_purpose="added_users",
                gender=gender
            )
    await db.add_application(
        user_id=int(user.get("id")),
        course_id=int(course_id),
        created_at=await get_now()
    )

    user_data = {
        "gender": gender,
        "full_name": full_name,
        "course_name": course_name
    }
    text = await set_message(user_data=user_data, to_admin=True)
    await send_message_to_admin_via_topic(
        gender=user_data.get("gender"),
        for_purpose="arrived_applications",
        text=text,
        user_id=call.from_user.id,
        is_application=True,
        course_id=course_id
    )

    await call.message.answer("✅ Arizangiz ko'rib chiqish uchun adminlar guruhiga yuborildi!\n\nTez orada qayta aloqaga chiqiladi.")
    await state.finish()
