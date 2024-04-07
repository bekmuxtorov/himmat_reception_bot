from aiogram.dispatcher.filters import BoundFilter
from aiogram import types


class IsGroup(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.chat.type in (types.ChatType.GROUP, types.ChatType.SUPERGROUP)
