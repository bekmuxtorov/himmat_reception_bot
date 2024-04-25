from aiogram import Dispatcher

from loader import dp
from .is_group import IsGroup, IsGroupAdmin, IsAdminInAdminGroups, IsGroupMember, IsMemberInAdminGroups
from .is_private import IsPrivate


if __name__ == "filters":
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(IsGroupAdmin)
    dp.filters_factory.bind(IsGroupMember)
    dp.filters_factory.bind(IsAdminInAdminGroups)
    dp.filters_factory.bind(IsMemberInAdminGroups)
