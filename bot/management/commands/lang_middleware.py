import sys
from typing import Tuple, Any, Optional
from aiogram import types
from kaif.settings import dp
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from bot.models import *
import os


class ACLMidlleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> Optional[str]:
        user = types.User.get_current()

        try:
            return (await TelegramUser.objects.aget(user_id=user.id)).lang
        except TelegramUser.DoesNotExist:
            t = await TelegramUser.objects.acreate(user_id=user.id, username=user.username)
            # t.save()
            return t.lang


i18n = ACLMidlleware(
    'bot',
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'locales')
)
dp.middleware.setup(i18n)
