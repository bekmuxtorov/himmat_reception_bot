async def is_member(bot, group, user_id) -> bool:
    member = await bot.get_chat_member(chat_id=group, user_id=user_id)
    return member.is_chat_member()
