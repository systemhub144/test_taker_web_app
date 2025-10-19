from aiogram import Dispatcher

from .users import user_router
from .admin import admin_router


def include_all_routers(dp: Dispatcher) -> None:
    dp.include_router(user_router)
    dp.include_router(admin_router)
