import asyncpg
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils.deep_linking import decode_payload

from loader import dp, db, bot
from utils.define_is_member import is_member
from utils.const_texts import submit_application

from filters.is_private import IsPrivate
from keyboards.default.default_buttons import make_buttons
from utils import get_now
from .admin import accept_app, cancel_app, message_to_user, answer_to_question


@dp.message_handler(IsPrivate(), CommandStart())
async def bot_start(message: types.Message):
    if message.get_args():
        payload = decode_payload(message.get_args())
        if 'accept' in payload:
            await accept_app(message=message, payload=payload)
        elif "cancel" in payload:
            await cancel_app(message=message, payload=payload)
        elif "message_to_user" in payload:
            await message_to_user(message=message, payload=payload)
        elif "question" in payload:
            await answer_to_question(message=message, payload=payload)
        return
    user_id = message.from_user.id
    groups = await db.select_all_groups()
    if groups:
        for item in groups:
            group = item["group_id"]
            if await is_member(bot=bot, group=group, user_id=user_id):
                await message.answer(f"Assalomu alekum, {message.from_user.full_name}\n\nOldingi guruhlarda qatnashganligiz uchun loyihada qayta qatnasha olmaysiz!\n\n{'-'*10}\n#TODO\nShu yerga mos matn yozish kerak")
                return

    try:
        await db.add_user(
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            telegram_id=message.from_user.id,
            created_at=await get_now(),
        )
    except:
        pass

    await message.answer(
        text=f"Assalomu aleykum, {message.from_user.full_name}!\n\nHimmat 700+ loyihasiga qatnashish uchun ariza qabul qiluvchi botga xush kelibsiz!\n\nAriza yuborish uchun quyidagi tugmani bosing.",
        reply_markup=make_buttons([submit_application], row_width=1)
    )
