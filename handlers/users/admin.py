import asyncio
import pytz

from aiogram import types
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta

from filters.is_group import IsGroup, IsGroupAdmin, IsGroupCall
from filters.is_private import IsPrivate
from loader import dp, db, bot
from utils import get_now, create_referral_link, const_texts
from keyboards.default.default_buttons import make_buttons
from states.for_admin import AcceptApp, CancelApp, MessageToUser, AnswerToUser, AddGroup
from data.config import DAYS, MEMBER_LIMIT
from utils.const_texts import send_message_to_admin_text, submit_application, add_group, add_course, find_user

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
            words=["❌ Bekor qilish"]
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
            reply_markup=make_buttons(
                words=[
                    add_group,
                    add_course,
                    find_user,
                ],
                row_width=2
            )
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
        text=f"✅ Guruh muaffaqiyatli qo'shildi!"
    )


# end add group


async def accept_app(message: types.Message, payload: str, state: FSMContext = AcceptApp.first_data):
    payload_items = payload.split(":")
    user_id = payload_items[1]
    chat_id = payload_items[2]
    message_id = payload_items[3]
    woman_user_groups = await db.select_group_by_for_whom(for_whom="woman_users")
    man_user_groups = await db.select_group_by_for_whom(for_whom="man_users")

    if not (woman_user_groups and man_user_groups):
        await message.answer(
            text="⚡ Iltimos foydalanuvchilar uchun barcha guruhlarni qo'shing."
        )
        return

    user_data = await db.select_user(telegram_id=int(user_id))
    user_full_name = user_data.get("full_name")
    gender = user_data.get("gender")

    for_man_group_id = man_user_groups.get("group_id")
    for_woman_group_id = woman_user_groups.get("group_id")
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
        text=f"{user_full_name}[{user_id}] foydalanuvchi guruhga qabul qilindi va taklif havolasi yuborildi.\n\nQabul qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>",
        chat_id=chat_id,
        message_id=message_id
    )
    await message.answer(f"{user_full_name}[{user_id}] foydalanuvchi guruhga qabul qilindi va taklif havolasi yuborildi")
#     text = f"Ariza topshiruvchi:<b>{user_full_name}[{user_id}] qabul qilinsinmi?</b>"
#     await state.update_data(user_id=user_id)
#     await message.answer(
#         text=text,
#         reply_markup=agree_buttons
#     )
#     await AcceptApp.confirm.set()


# @dp.callback_query_handler(text="agree_no", state=AcceptApp.confirm)
# async def bot_echo(call: types.CallbackQuery, state: FSMContext):
#     await call.message.delete()
#     await call.message.answer(
#         text="✅ Yaxshi, ariza qabul qilinmadi!",
#     )
#     await state.finish()


# @dp.callback_query_handler(text="agree_yes", state=AcceptApp.confirm)
# async def bot_echo(call: types.CallbackQuery, state: FSMContext):
#     await call.message.delete()
    # woman_user_groups = await db.select_group_by_for_whom(for_whom="woman_users")
    # man_user_groups = await db.select_group_by_for_whom(for_whom="man_users")

    # if not (woman_user_groups and man_user_groups):
    #     await call.message.answer(
    #         text="⚡ Iltimos foydalanuvchilar uchun barcha guruhlarni qo'shing."
    #     )
    #     return

    # user_data = await state.get_data()
    # user_id = user_data.get("user_id")
    # print(user_id)
    # gender = user_data.get("gender")

    # for_man_group_id = man_user_groups.get("group_id")
    # for_woman_group_id = woman_user_groups.get("group_id")

    # referral_link_man = await create_referral_link(for_man_group_id)
    # referral_link_woman = await create_referral_link(for_woman_group_id)
    # if gender == "Erkak":
    #     await call.message.answer(
    #         text=f"Siz guruhga qabul qilindingiz!\n\nSizning taklif havolangiz: {referral_link_man}\n\nMuhim: Havolaning yaroqlilik muddati {DAYS} kun bo'lib, faqat {MEMBER_LIMIT} marotaba ishlatishingiz mumkin.")
    # elif gender == "Ayol":
    #     await call.message.answer(
    #         text=f"Siz guruhga qabul qilindingiz!\n\nSizning taklif havolangiz: {referral_link_woman}\n\nMuhim: Havolaning yaroqlilik muddati {DAYS} kun bo'lib, faqat {MEMBER_LIMIT} marotaba ishlatishingiz mumkin.")
    # await state.finish()

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


@dp.message_handler(IsPrivate(), text="create_topic")
async def create_topic(message: types.Message):
    await message.answer("Test uchun topic yaratish boshlandi.")
    data = await bot.create_forum_topic(chat_id=-1002117894380, name="Test uchun topic")
    print(data)
    await message.answer("Test uchun topic yaratish tugadi.")
