import asyncio
import pytz

from aiogram import types
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta

from filters.is_group import IsAdminInAdminGroups, IsGroupMember, IsMemberInAdminGroups
from filters.is_private import IsPrivate
from loader import dp, db, bot
from utils import get_now, create_referral_link, const_texts
from keyboards.default.default_buttons import make_buttons, admin_buttons
from states.for_admin import AcceptApp, CancelApp, MessageToUser, AnswerToUser, AddGroup, AddCource
from data.config import DAYS, MEMBER_LIMIT
from utils.const_texts import send_message_to_admin_text, submit_application, add_group, add_course, find_user, list_group, list_course
from .send_message_to_admin import send_message_to_admin_via_topic


@dp.message_handler(IsGroupMember(), text="Bekor qilish", state="*")
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer("💡 Jarayon bekor qilindi!", reply_markup=admin_buttons)
    await state.finish()

# Add group

"""
Guruh qo'shish
    - Guruhning id sini kiriting(Guruhning id'sini ...bot' yordamida olishingiz mumkin):
    - Guruh kimlar uchun[Faqat erkak, faqat ayol, Aralash]
    - Guruh success qo'shildi
"""


@dp.message_handler(IsPrivate(), text=add_group)
async def add_group(message: types.Message):
    await message.answer(
        text="Guruhning ID sini kiriting:\n\nGuruhning ID'sini @raw_data_bot yordamida olishingiz mumkin",
        reply_markup=make_buttons(
            words=["Bekor qilish"]
        )
    )
    await AddGroup.submit_id.set()


@dp.message_handler(IsPrivate(), state=AddGroup.submit_id)
async def add_group(message: types.Message, state: FSMContext):
    try:
        group_id = int(message.text)
    except:
        await message.answer("Iltimos guruh ID'sini to'g'ri holatda kiriting")
        return
    data = await db.select_group(group_id=group_id)
    if data:
        await message.answer(
            text=f"ℹ️ {data.get('group_name')}[{data.get('group_id')}] guruhi bazaga qo'shilgan.",
            reply_markup=admin_buttons
        )
        return

    await state.update_data(group_id=group_id)
    await message.answer(
        text="Guruh kimlar uchun:\n\nQuyidan tanlang.",
        reply_markup=make_buttons(
            words=["Erkaklar uchun", "Ayollar uchun", "Barcha uchun"],
            row_width=2
        )
    )
    await AddGroup.for_whom.set()


@dp.message_handler(IsPrivate(), state=AddGroup.for_whom)
async def add_group(message: types.Message, state: FSMContext):
    text = message.text
    if not text in ["Erkaklar uchun", "Ayollar uchun", "Barcha uchun"]:
        await message.answer(
            text="Iltimos quyidagilarni birini tanglang:",
            reply_markup=make_buttons(
                words=["Erkaklar uchun", "Ayollar uchun", "Barcha uchun"],
                row_width=2
            )
        )
        return
    if text == "Erkaklar uchun":
        for_whom = "man_users"
    elif text == "Ayollar uchun":
        for_whom = "woman_users"
    elif text == "Barcha uchun":
        for_whom = "mixed_users"

    group_data = await state.get_data()
    group_id = group_data.get("group_id")
    await db.add_group(
        by_user_id=message.from_user.id,
        by_user_name=message.from_user.full_name,
        group_id=group_id,
        group_name=None,
        created_at=await get_now(),
        for_whom=for_whom
    )
    await message.answer(
        text=f"✅ Guruh muaffaqiyatli qo'shildi!",
        reply_markup=admin_buttons
    )
    await state.finish()


@dp.message_handler(IsMemberInAdminGroups(), commands="groups")
@dp.message_handler(IsMemberInAdminGroups(), IsPrivate(), text=list_group)
async def add_group(message: types.Message):
    data = await db.select_all_groups()
    text = "-- Guruhlar --\n\n"
    for item in data:
        text += f"<b>ID:</b> <code>{item.get('group_id')}</code>\n"
        text += f"<b>Nomi:</b> {item.get('group_name')}\n"
        text += f"<b>Kimlar uchun:</b> {item.get('for_whom')}\n"
        text += f"<b>Vaqt:</b> {item.get('created_at')}\n"
        text += f"<b>Qo'shgan admin:</b> {item.get('by_user_name')}\n\n"
    await message.answer(text=text, reply_markup=admin_buttons)


# end add group


# Add course

"""
Course ochish
    --name
    --description
    --for_man_group_id
    --for_woman_group_id
    --created_at
"""


@dp.message_handler(IsMemberInAdminGroups(), commands="courses")
@dp.message_handler(IsPrivate(), text=list_course)
async def add_group(message: types.Message):
    data = await db.select_all_courses()
    text = "-- Kurslar --\n\n"
    for item in data:
        text += f"<b>ID:</b> <code>{item.get('id')}</code>\n"
        text += f"<b>Nomi:</b> {item.get('name')}\n"
        text += f"<b>Tavsif:</b> {item.get('description')}\n"
        text += f"<b>Erkaklar uchun:</b> {item.get('for_man_group_id')}\n"
        text += f"<b>Ayollar uchun:</b> {item.get('for_woman_group_id')}\n"
        text += f"<b>Vaqt:</b> {item.get('created_at')}\n"
    await message.answer(text=text, reply_markup=admin_buttons)


@dp.message_handler(IsAdminInAdminGroups(), IsPrivate(), text=add_course)
async def add_cource(message: types.Message):
    await message.answer(
        text="Kurs uchun nom kiriting:",
        reply_markup=make_buttons(
            words=["Bekor qilish"]
        )
    )
    await AddCource.name.set()


@dp.message_handler(IsPrivate(), state=AddCource.name)
async def add_cource(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer(
        text="Kurs uchun qisqacha tavsif yozing:",
        reply_markup=make_buttons(
            words=["Bekor qilish"]
        )
    )
    await AddCource.description.set()


@dp.message_handler(IsPrivate(), state=AddCource.description)
async def add_cource(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.answer(
        text="Erkaklar uchun guruhning ID sini kiriting:\n\nGuruhning ID'sini @raw_data_bot yordamida olishingiz mumkin",
        reply_markup=make_buttons(
            words=["Bekor qilish"]
        )
    )
    await AddCource.for_man_group_id.set()


@dp.message_handler(IsPrivate(), state=AddCource.for_man_group_id)
async def add_cource(message: types.Message, state: FSMContext):
    try:
        for_man_group_id = int(message.text)
    except:
        await message.answer(
            text="Iltimos guruh ID'sini to'g'ri holatda kiriting.",
            reply_markup=make_buttons(
                words=["Bekor qilish"]
            )
        )
        return

    await state.update_data(for_man_group_id=for_man_group_id)
    await message.answer(
        text="Ayollar uchun guruhning ID sini kiriting:\n\nGuruhning ID'sini @raw_data_bot yordamida olishingiz mumkin",
        reply_markup=make_buttons(
            words=["Bekor qilish"]
        )
    )
    await AddCource.for_woman_group_id.set()


@dp.message_handler(IsPrivate(), state=AddCource.for_woman_group_id)
async def add_cource(message: types.Message, state: FSMContext):
    try:
        for_woman_group_id = int(message.text)
    except:
        await message.answer(
            text="Iltimos guruh ID'sini to'g'ri holatda kiriting.",
            reply_markup=make_buttons(
                words=["Bekor qilish"]
            )
        )
        return

    data = await db.select_group(group_id=for_woman_group_id)
    if data:
        await message.answer(
            text=f"ℹ️ {data.get('group_name')}[{data.get('group_id')}] guruhi bazaga qo'shilgan.\n\nBoshqa guruh tashkil qilib uning ID'sini yuborishingiz mumkin.",
            reply_markup=admin_buttons
        )
        return

    cource_data = await state.get_data()
    name = cource_data.get("name")
    description = cource_data.get("description")

    for_man_group_id = cource_data.get("for_man_group_id")
    created_at = await get_now()

    await db.add_course(
        name=name,
        description=description,
        for_man_group_id=str(for_man_group_id),
        for_woman_group_id=str(for_woman_group_id),
        created_at=created_at
    )
    await db.add_group(
        by_user_id=message.from_user.id,
        by_user_name=message.from_user.full_name,
        group_id=for_man_group_id,
        group_name=None,
        created_at=created_at,
        for_whom="man_users"
    )

    await db.add_group(
        by_user_id=message.from_user.id,
        by_user_name=message.from_user.full_name,
        group_id=for_woman_group_id,
        group_name=None,
        created_at=created_at,
        for_whom="woman_users"
    )

    text = "✅ Kurs muvaffaqiyatli yaratildi.\n\n-- Barcha ma'lumotlar: --\n\n"
    text += f"<b>Nomi:</b> {name}\n"
    text += f"<b>Tavsif:</b> {description}\n"
    text += f"<b>Yaratgan admin:</b> {message.from_user.full_name}\n"
    text += f"<b>Yaratilgan:</b> {created_at}\n"
    text += f"<b>Erkaklar uchun guruh ID:</b> <code>{for_man_group_id}</code>\n"
    text += f"<b>Ayollar uchun guruh ID:</b> <code>{for_woman_group_id}</code>\n"
    await message.answer(
        text=text,
        reply_markup=admin_buttons
    )
    await state.finish()
    await send_message_to_admin_via_topic(text=text, for_purpose="created_courses")


@dp.message_handler(IsPrivate(), state=AddCource.for_man_group_id)
async def add_cource(message: types.Message, state: FSMContext):
    try:
        for_man_group_id = int(message.text)
    except:
        await message.answer("Iltimos guruh ID'sini to'g'ri holatda kiriting")
        return
    await state.update_data(for_man_group_id=for_man_group_id)
    await message.answer(
        text="Erkaklar uchun guruhning ID sini kiriting:\n\nGuruhning ID'sini @raw_data_bot yordamida olishingiz mumkin",
        reply_markup=make_buttons(
            words=["❌ Bekor qilish"]
        )
    )
    await AddCource.for_man_group_id.set()


async def accept_app(message: types.Message, payload: str, state: FSMContext = AcceptApp.first_data):
    payload_items = payload.split(":")
    user_id = payload_items[1]
    chat_id = payload_items[2]
    message_id = payload_items[3]
    course_id = payload_items[4]
    get_course = await db.select_course(id=int(course_id))

    for_man_group_id = get_course.get("for_man_group_id")
    for_woman_group_id = get_course.get("for_woman_group_id")     

    user_data = await db.select_user(telegram_id=int(user_id))
    user_full_name = user_data.get("full_name")
    gender = user_data.get("gender")
    username = user_data.get("username") 

    referral_link_man = await create_referral_link(bot, for_man_group_id)
    referral_link_woman = await create_referral_link(bot, for_woman_group_id)
    if gender == "Erkak":
        await bot.send_message(
            chat_id=user_id,
            text=f"Xurmatli <b>{user_full_name}</b>\nSiz guruhga qabul qilindingiz!\n\nSizning taklif havolangiz: {referral_link_man}\n\nMuhim: Havolaning yaroqlilik muddati {DAYS} kun bo'lib, faqat {MEMBER_LIMIT} marotaba ishlatishingiz mumkin.",
            reply_markup=make_buttons(
                words=[f'{send_message_to_admin_text}', f"{submit_application}"], row_width=2)
        )
    elif gender == "Ayol":
        await bot.send_message(
            chat_id=user_id,
            text=f"Siz guruhga qabul qilindingiz!\n\nSizning taklif havolangiz: {referral_link_woman}\n\nMuhim: Havolaning yaroqlilik muddati {DAYS} kun bo'lib, faqat {MEMBER_LIMIT} marotaba ishlatishingiz mumkin.")
    await bot.edit_message_text(
        text=f"{user_full_name}[<a href='https://{username}.t.me'>@{username}</a>]ning guruxga kirish arizasi tasdiqlandi va guruxga kirish xavolasi unga yuborildi.\n\nQabul qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>",
        chat_id=chat_id,
        message_id=message_id
    )
    await send_message_to_admin_via_topic(
        text=f"{user_full_name}[<a href='https://{username}.t.me'>@{username}</a>]ning guruxga kirish arizasi tasdiqlandi va guruxga kirish xavolasi unga yuborildi.\n\nQabul qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>",
        for_purpose = "accepted_applications",
        gender=gender
    )
    await message.answer(
            text=f"{user_full_name}[<a href='https://{username}.t.me'>@{username}</a>]ning guruxga kirish arizasi tasdiqlandi va guruxga kirish xavolasi unga yuborildi.\n\nQabul qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>",
    )


CANCEL_APPLICATION = {}


async def cancel_app(message: types.Message, payload: str):
    payload_items = payload.split(":")
    user_id = payload_items[1]
    chat_id = payload_items[2]
    message_id = payload_items[3]
    admin_user_id = message.from_user.id
    await message.answer("📝 Arizani bekor qilish sababini kiriting:")
    CANCEL_APPLICATION[f"cancel_app:{admin_user_id}"] = {}
    CANCEL_APPLICATION[f"cancel_app:{admin_user_id}"]["user_id"] = user_id
    CANCEL_APPLICATION[f"cancel_app:{admin_user_id}"]["message_id"] = message_id
    CANCEL_APPLICATION[f"cancel_app:{admin_user_id}"]["chat_id"] = chat_id
    await CancelApp.cause_text.set()


@dp.message_handler(IsPrivate(), state=CancelApp.cause_text)
async def cancel_app_ca(message: types.Message, state: FSMContext):
    admin_user_id = message.from_user.id
    user_id = CANCEL_APPLICATION[f"cancel_app:{admin_user_id}"]["user_id"]
    message_id = CANCEL_APPLICATION[f"cancel_app:{admin_user_id}"]["message_id"]
    chat_id = CANCEL_APPLICATION[f"cancel_app:{admin_user_id}"]["chat_id"]
    del CANCEL_APPLICATION[f"cancel_app:{admin_user_id}"]
    user_data = await db.select_user(telegram_id=int(user_id))
    user_full_name = user_data.get("full_name")
    gender = user_data.get("gender")
    cause_text = message.text
    await bot.send_message(
        chat_id=user_id,
        text=f"❌ Arizangiz bekor qilindi!\n\nSabab: <i>{cause_text}</i>",
        reply_markup=make_buttons(
            words=[f"{const_texts.send_message_to_admin_text}", f"{const_texts.submit_application}"])
    )
    
    await message.answer(
        text=f"{user_full_name}[{user_id}] foydalanuvchining arizasi bekor qilindi.\n\nBekor qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\n<b>Sabab</b>: <i>{cause_text}</i>",
    )
    
    await bot.edit_message_text(
        text=f"{user_full_name}[{user_id}] foydalanuvchining arizasi bekor qilindi.\n\nBekor qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\n<b>Sabab</b>: <i>{cause_text}</i>",
        chat_id=chat_id,
        message_id=message_id,
    )
    await send_message_to_admin_via_topic(
        text=f"{user_full_name}[{user_id}] foydalanuvchining arizasi bekor qilindi.\n\nBekor qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\n<b>Sabab</b>: <i>{cause_text}</i>",
        for_purpose="canceled_applications",
        gender=gender
    )
    await state.finish()


async def message_to_user(message: types.Message, payload):
    payload_items = payload.split(":")
    user_id = payload_items[1]
    chat_id = payload_items[2]
    message_id = payload_items[3]
    admin_user_id = message.from_user.id
    await message.answer("📝 Savolingizni quyidagi kiritishingiz mumkin:")
    CANCEL_APPLICATION[f"message_to_user:{admin_user_id}"] = {}
    CANCEL_APPLICATION[f"message_to_user:{admin_user_id}"]["user_id"] = user_id
    CANCEL_APPLICATION[f"message_to_user:{admin_user_id}"]["message_id"] = message_id
    CANCEL_APPLICATION[f"message_to_user:{admin_user_id}"]["chat_id"] = chat_id
    await MessageToUser.qestion.set()


@dp.message_handler(IsPrivate(), state=MessageToUser.qestion)
async def cancel_app_ca(message: types.Message, state: FSMContext):
    admin_user_id = message.from_user.id
    user_id = CANCEL_APPLICATION[f"message_to_user:{admin_user_id}"]["user_id"]
    message_id = CANCEL_APPLICATION[f"message_to_user:{admin_user_id}"]["message_id"]
    chat_id = CANCEL_APPLICATION[f"message_to_user:{admin_user_id}"]["chat_id"]
    del CANCEL_APPLICATION[f"message_to_user:{admin_user_id}"]
    user_data = await db.select_user(telegram_id=int(user_id))
    user_full_name = user_data.get("full_name")
    question = message.text
    await bot.send_message(
        chat_id=user_id,
        text=f"📝 Sizga xabar yo'llandi! Quyidagi tugma yordamida javob qaytarishingiz mumkin.\n\nXabar: <i>{question}</i>",
        reply_markup=make_buttons(
            words=[f"💡 Javob yo'llash"])
    )
    await message.answer(
        text=f"ℹ️ {user_full_name}[{user_id}] foydalanuvchiga xabar yo'llandi.\n\nXabar jo'natuvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\n<b>Xabar</b>: <i>{question}</i>",
    )
    await bot.edit_message_text(
        text=f"ℹ️ {user_full_name}[{user_id}] foydalanuvchiga xabar yo'llandi.\n\nXabar jo'natuvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\n<b>Xabar</b>: <i>{question}</i>",
        chat_id=chat_id,
        message_id=message_id,
    )
    await state.finish()


async def answer_to_question(message: types.Message, payload):
    await message.answer("📝 Xabaringizni quyiga kiriting:")
    payload_items = payload.split(":")
    user_id = payload_items[2]
    chat_id = payload_items[3]
    message_id = payload_items[4]
    admin_user_id = message.from_user.id
    CANCEL_APPLICATION[f"answer_to_question:{admin_user_id}"] = {}
    CANCEL_APPLICATION[f"answer_to_question:{admin_user_id}"]["user_id"] = user_id
    CANCEL_APPLICATION[f"answer_to_question:{admin_user_id}"]["chat_id"] = chat_id
    CANCEL_APPLICATION[f"answer_to_question:{admin_user_id}"]["message_id"] = message_id
    await AnswerToUser.answer.set()


@dp.message_handler(IsPrivate(), state=AnswerToUser.answer)
async def cancel_app_ca(message: types.Message, state: FSMContext):
    admin_user_id = message.from_user.id
    user_id = CANCEL_APPLICATION[f"answer_to_question:{admin_user_id}"]["user_id"]
    chat_id = CANCEL_APPLICATION[f"answer_to_question:{admin_user_id}"]["chat_id"]
    message_id = CANCEL_APPLICATION[f"answer_to_question:{admin_user_id}"]["message_id"]
    del CANCEL_APPLICATION[f"answer_to_question:{admin_user_id}"]
    user_data = await db.select_user(telegram_id=int(user_id))
    user_full_name = user_data.get("full_name")
    question = message.text
    await bot.send_message(
        chat_id=user_id,
        text=f"📝 Sizga xabar yo'llandi! Quyidagi tugma yordamida javob qaytarishingiz mumkin.\n\nXabar: <i>{question}</i>",
        reply_markup=make_buttons(
            words=[f"💡 Javob yo'llash"])
    )
    await message.answer(
        text=f"ℹ️ {user_full_name}[{user_id}] foydalanuvchiga xabar yo'llandi.\n\nXabar jo'natuvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\n<b>Xabar</b>: <i>{question}</i>",
    )
    await bot.edit_message_text(
        text=f"ℹ️ {user_full_name}[{user_id}] foydalanuvchiga xabar yo'llandi.\n\nXabar jo'natuvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\n<b>Xabar</b>: <i>{question}</i>",
        chat_id=chat_id,
        message_id=message_id
    )
    await state.finish()


# @dp.message_handler(IsPrivate(), text="create_topic")
# async def create_topic(message: types.Message):
#     await message.answer("Test uchun topic yaratish boshlandi.")
#     data = await bot.create_forum_topic(chat_id=-1002117894380, name="Test uchun topic")
#     print(data)
#     await message.answer("Test uchun topic yaratish tugadi.")
