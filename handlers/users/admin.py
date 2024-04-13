import asyncio
import pytz

from aiogram import types
from datetime import datetime

from data.config import ADMINS
from filters.is_group import IsGroup, IsGroupAdmin
from loader import dp, db, bot
from utils import get_now


@dp.message_handler(IsGroupAdmin(), IsGroup(), commands="group_for_users")
async def add_group(message: types.Message):
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
        for_whom="for_users"
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


@dp.message_handler(IsGroup(), commands=['group_for_man_admin', 'group_for_woman_admin', 'group_for_users'])
async def send_ad_to_all(message: types.Message):
    service_message = await message.answer("⚡ Ushbu buyruqni faqat guruh adminlari ishlata oladi.")
    await asyncio.sleep(12)
    await message.delete()
    await service_message.delete()
