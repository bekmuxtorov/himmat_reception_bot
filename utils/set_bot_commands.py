from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish"),
            types.BotCommand("group_for_man_users",
                             "Erkak foydalanuvchilar uchun guruh qo'shish"),
            types.BotCommand("group_for_woman_users",
                             "Ayol foydalanuvchilar uchun guruh qo'shish"),
            types.BotCommand("group_for_man_admin",
                             "Erkak adminlar uchun guruh qo'shish"),
            types.BotCommand("group_for_woman_admin",
                             "Ayol adminlar uchun guruh qo'shish"),
        ]
    )
