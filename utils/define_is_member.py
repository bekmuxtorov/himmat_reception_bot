from data.config import FOR_MAN_ADMINS, FOR_WOMAN_ADMINS


async def is_member(bot, group, user_id) -> bool:
    member = await bot.get_chat_member(chat_id=group, user_id=user_id)
    return member.is_chat_member()


async def is_admin(bot, user_id) -> bool:
    groups = [FOR_WOMAN_ADMINS, FOR_MAN_ADMINS]
    status = False
    for group in groups:
        member = await bot.get_chat_member(chat_id=group, user_id=user_id)
        status = status or member.is_chat_admin()
    return status
