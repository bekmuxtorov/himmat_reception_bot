from datetime import datetime, timedelta
from data.config import DAYS, MEMBER_LIMIT


async def create_referral_link(bot, chat_id: int):
    expire_date = datetime.now() + timedelta(days=DAYS)
    referral_link = await bot.create_chat_invite_link(
        chat_id=chat_id,
        expire_date=expire_date,
        member_limit=MEMBER_LIMIT,
        creates_join_request=False
    )
    return referral_link.invite_link
