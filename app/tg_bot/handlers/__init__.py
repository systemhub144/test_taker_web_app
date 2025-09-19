from aiogram import Dispatcher

from .users import user_router


def include_all_routers(dp: Dispatcher) -> None:
    dp.include_router(user_router)
