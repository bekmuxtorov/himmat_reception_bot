from aiogram.dispatcher.filters import BoundFilter
from aiogram import types


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP)


class IsGroupAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin()
