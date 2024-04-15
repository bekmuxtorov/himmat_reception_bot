import asyncio
import pytz

from aiogram import types
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta

from filters.is_group import IsGroup, IsGroupAdmin, IsGroupCall
from loader import dp, db, bot
from utils import get_now, create_referral_link, const_texts
from keyboards.default.default_buttons import make_buttons
from states.for_admin import AcceptApp, CancelApp, MessageToUser
from data.config import DAYS, MEMBER_LIMIT


@dp.message_handler(IsGroupAdmin(), IsGroup(), commands=["group_for_man_users", "group_for_woman_users"])
async def add_group(message: types.Message):
    command = message.get_command()
    if '@' in command:
        needly_message = command.split("@")[0]
        command_items = needly_message.split('_')
    else:
        command_items = command.split('_')
    for_whom = command_items[2] + "_" + command_items[3]
    group_data = message.chat
    user_data = message.from_user
    data = await db.select_group(group_id=group_data.id)
    if data:
        service_message = await message.answer(f"ℹ️ {data.get('group_name')} guruhi bazaga qo'shilgan.")
        await asyncio.sleep(12)
        await message.delete()
        await service_message.delete()
        return

    await db.add_group(
        by_user_id=user_data.id,
        by_user_name=user_data.full_name,
        group_id=group_data.id,
        group_name=group_data.full_name,
        created_at=await get_now(),
        for_whom=for_whom
    )
    service_message = await message.answer(
        text=f"✅ Guruh muaffaqiyatli qo'shildi!"
    )
    await asyncio.sleep(12)
    await message.delete()
    await service_message.delete()


@dp.message_handler(IsGroupAdmin(), IsGroup(), commands=['group_for_man_admin', 'group_for_woman_admin'])
async def send_ad_to_all(message: types.Message):
    command = message.get_command()
    if '@' in command:
        needly_message = command.split("@")[0]
        command_items = needly_message.split('_')
    else:
        command_items = command.split('_')
    for_whom = command_items[2] + "_" + command_items[3]
    gender = "Erkak" if command_items[2] == "man" else "Ayol"
    group_data = message.chat
    user_data = message.from_user
    data = await db.select_group(group_id=group_data.id)
    if data:
        for_whom = data.get("for_whom")
        if for_whom == "man_admin":
            service_message = await message.answer(f"ℹ️ <b>{group_data.full_name}</b> guruhi erkaklar uchun admin guruhi sifatida qo'shilgan.")
        else:
            service_message = await message.answer(f"ℹ️ <b>{group_data.full_name}</b> guruhi ayollar uchun admin guruhi sifatida qo'shilgan.")
        await asyncio.sleep(12)
        await message.delete()
        await service_message.delete()
        return

    await db.delete_group(for_whom=for_whom)

    await db.add_group(
        by_user_id=user_data.id,
        by_user_name=user_data.full_name,
        group_id=group_data.id,
        group_name=group_data.full_name,
        created_at=await get_now(),
        for_whom=for_whom
    )
    service_message = await message.answer(
        text=f"✅ {gender}lar uchun admin guruh muaffaqiyatli qo'shildi!"
    )
    await asyncio.sleep(12)
    await message.delete()
    await service_message.delete()


@dp.message_handler(IsGroup(), commands=['group_for_man_admin', 'group_for_woman_admin', 'group_for_man_users', 'group_for_woman_users'])
async def send_ad_to_all(message: types.Message):
    service_message = await message.answer("⚡ Ushbu buyruqni faqat guruh adminlari ishlata oladi.")
    await asyncio.sleep(12)
    await message.delete()
    await service_message.delete()


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
            text=f"Xurmatli <b>{user_full_name}</b>\nSiz guruhga qabul qilindingiz!\n\nSizning taklif havolangiz: {referral_link_man}\n\nMuhim: Havolaning yaroqlilik muddati {DAYS} kun bo'lib, faqat {MEMBER_LIMIT} marotaba ishlatishingiz mumkin.")
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


async def cancel_app(message: types.Message, payload: str, state: FSMContext):
    payload_items = payload.split(":")
    user_id = payload_items[1]
    chat_id = payload_items[2]
    message_id = payload_items[3]
    await message.answer("📝 Arizani bekor qilish sababini kiriting:")
    await state.update_data(user_id=user_id)
    await state.update_data(message_id=message_id)
    await state.update_data(chat_id=chat_id)
    await CancelApp.cause_text.set()


@dp.message_handler(IsGroup(), state=CancelApp.cause_text)
async def cancel_app_ca(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    message_id = data.get("message_id")
    chat_id = data.get('chat_id')
    user_data = await db.select_user(telegram_id=user_id)
    user_full_name = user_data.get("full_name")
    cause_text = message.text
    await bot.send_message(
        text=f"❌ Arizangiz bekor qilindi!\n\nSabab: <i>{cause_text}</i>",
        reply_markup=make_buttons(
            words=[f"{const_texts.send_message_to_admin_text}", f"{const_texts.submit_application}"])
    )
    await message.answer(
        text=f"{user_full_name}[{user_id}] Foydalanuvchining arizasi bekor qilindi.\nBekor qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\nSabab: <i>{cause_text}</i>",
    )
    await bot.edit_message_text(
        text=f"{user_full_name}[{user_id}] Foydalanuvchining arizasi bekor qilindi.\nBekor qiluvchi: <b>{message.from_user.full_name}[{message.from_user.id}]</b>\n\nSabab: <i>{cause_text}</i>",
        chat_id=chat_id,
        message_id=message_id,
    )


async def message_to_user(message: types.Message, payload):
    pass


async def answer_to_question(message: types.Message, payload):
    pass
