import pytz
from datetime import datetime


async def get_now():
    return pytz.timezone("Asia/Tashkent").localize(datetime.now())
