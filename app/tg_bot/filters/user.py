from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message


class ChannelSubscriptionFilter(BaseFilter):
    async def __call__(self, message: Message, bot: Bot, user_id = None) -> bool:
        if user_id is None:
            user_id = message.from_user.id

        if not bot.config.CHANNELS_ID:
            return True

        for channel in bot.config.CHANNELS_ID:
            try:
                chat_member = await bot.get_chat_member(chat_id=f'@{channel}', user_id=user_id)
                if chat_member.status == 'left':
                    return False
            except Exception as e:
                print(f"Error checking subscription for channel {channel}: {e}")
                return False

        return True
