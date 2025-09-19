from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import load_config, PATH
from app.tg_bot.commands import set_all_commands
from app.tg_bot.handlers import include_all_routers


config = load_config(PATH / '.env')

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def bot_preparation() -> None:
    await set_all_commands(bot)
    webhook_url = config.get_webhook_url()
    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )

    bot.config = config

    include_all_routers(dp)
