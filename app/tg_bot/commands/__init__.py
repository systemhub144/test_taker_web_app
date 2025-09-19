from aiogram import Bot

from .users import set_users_commands

async def set_all_commands(bot: Bot) -> None:
    await set_users_commands(bot)