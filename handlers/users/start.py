import asyncpg
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, db, bot
from data.config import ADMINS
from utils.define_is_member import is_member


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user_id = message.from_user.id
    groups = await db.select_all_groups()
    if groups:
        for item in groups:
            group = item["group_id"]
            if await is_member(bot=bot, group=group, user_id=user_id):
                await message.answer(f"Assalomu alekum, {message.from_user.full_name}\n\nOldingi guruhlarda qatnashganligiz uchun loyihada qayta qatnasha olmaysiz!\n\n{'-'*10}\n#TODO\nShu yerga mos matn yozish kerak")
                return
    await message.answer(
        text=f"Assalomu aleykum, {message.from_user.full_name}!\n\nHimmat 700+ loyihasiga qatnashish uchun ariza qabul qiluvchi botga xush kelibsiz!\n\nAriza yuborish uchun quyidagi tugmani bosing."
    )
