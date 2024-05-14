async def set_message(user_data: dict, to_admin: bool) -> str:
    gender = user_data.get("gender")
    full_name = user_data.get("full_name")
    curse_name = user_data.get("course_name")
    text = ""
    if to_admin:
        text += "💡 Yangi ariza jo'natildi.\n\n"
    else:
        text += "💡 Yuborilayotgan ma'lumotlar.\n\n"

    text += f"<b>Jins</b>: {gender}\n"
    # text += f"<b>Kurs nomi</b>: {curse_name}\n"
    text += f"<b>Ism va familiya:</b> {full_name}"
    return text
