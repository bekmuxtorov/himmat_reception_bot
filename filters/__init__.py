from aiogram import Dispatcher

from loader import dp
from .is_group import IsGroup, IsGroupAdmin, IsAdminInAdminGroups
from .is_private import IsPrivate


if __name__ == "filters":
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(IsGroupAdmin)
    dp.filters_factory.bind(IsAdminInAdminGroups)

