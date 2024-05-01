from aiogram import types

from loader import dp, bot, db
from utils import get_now
from data.config import FOR_WOMAN_ADMINS, FOR_MAN_ADMINS


@dp.message_handler(commands="create_topics", chat_id=1603330179)
async def create_topic(message: types.Message):
    await message.answer("Topic'larni yaratish boshlandi.")
    for group in (FOR_MAN_ADMINS, FOR_WOMAN_ADMINS):
        # for accepted questions
        if not await db.select_topic(topic_created_group_id=group, for_purpose="accepted_messages"):
            data = await bot.create_forum_topic(chat_id=group, name="Kelib tushgan xabarlar")
            await db.add_topic(
                topic_id=data.message_thread_id,
                topic_name=data.name,
                topic_created_group_id=group,
                created_at=await get_now(),
                for_purpose="accepted_messages"
            )

        # for answered questions
        if not await db.select_topic(topic_created_group_id=group, for_purpose="send_message"):
            data = await bot.create_forum_topic(chat_id=group, name="Userga yuborilgan xabarlar")
            await db.add_topic(
                topic_id=data.message_thread_id,
                topic_name=data.name,
                topic_created_group_id=group,
                created_at=await get_now(),
                for_purpose="send_message"
            )

        # for created courses
        if not await db.select_topic(topic_created_group_id=group, for_purpose="created_courses"):
            data = await bot.create_forum_topic(chat_id=group, name="Yaratilgan kurslar")
            await db.add_topic(
                topic_id=data.message_thread_id,
                topic_name=data.name,
                topic_created_group_id=group,
                created_at=await get_now(),
                for_purpose="created_courses"
            )

        # for accepted applications
        if not await db.select_topic(topic_created_group_id=group, for_purpose="arrived_applications"):
            data = await bot.create_forum_topic(chat_id=group, name="Kelib tushgan arizalar")
            await db.add_topic(
                topic_id=data.message_thread_id,
                topic_name=data.name,
                topic_created_group_id=group,
                created_at=await get_now(),
                for_purpose="arrived_applications"
            )

        # for answered applications
        if not await db.select_topic(topic_created_group_id=group, for_purpose="accepted_applications"):
            data = await bot.create_forum_topic(chat_id=group, name="Qabul qilingan arizalar")
            await db.add_topic(
                topic_id=data.message_thread_id,
                topic_name=data.name,
                topic_created_group_id=group,
                created_at=await get_now(),
                for_purpose="accepted_applications"
            )

        # for canceled applications
        if not await db.select_topic(topic_created_group_id=group, for_purpose="canceled_applications"):
            data = await bot.create_forum_topic(chat_id=group, name="Bekor qilingan arizalar")
            await db.add_topic(
                topic_id=data.message_thread_id,
                topic_name=data.name,
                topic_created_group_id=group,
                created_at=await get_now(),
                for_purpose="canceled_applications"
            )

        # for added users
        if not await db.select_topic(topic_created_group_id=group, for_purpose="added_users"):
            data = await bot.create_forum_topic(chat_id=group, name="Bot foydalanuvchilari")
            await db.add_topic(
                topic_id=data.message_thread_id,
                topic_name=data.name,
                topic_created_group_id=group,
                created_at=await get_now(),
                for_purpose="added_users"
            )

        # for added groups
        if not await db.select_topic(topic_created_group_id=group, for_purpose="added_groups"):
            data = await bot.create_forum_topic(chat_id=group, name="Qo'shilgan guruhlar")
            await db.add_topic(
                topic_id=data.message_thread_id,
                topic_name=data.name,
                topic_created_group_id=group,
                created_at=await get_now(),
                for_purpose="added_groups"
            )
    await message.answer("Topic'larni yaratish tugadi.")
