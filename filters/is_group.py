from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
from loader import bot
from data.config import FOR_MAN_ADMINS, FOR_WOMAN_ADMINS


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP)


class IsGroupCall(BoundFilter):
    async def check(self, call: types.CallbackQuery) -> bool:
        return call.message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP)


class IsGroupAdmin(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_admin()


class IsGroupMember(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        member = await message.chat.get_member(message.from_user.id)
        return member.is_chat_member()


class IsAdminInAdminGroups(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        groups = [FOR_WOMAN_ADMINS, FOR_MAN_ADMINS]
        status = False
        for group in groups:
            member = await bot.get_chat_member(chat_id=group, user_id=message.from_user.id)
            status = status or member.is_chat_admin()
        return status
