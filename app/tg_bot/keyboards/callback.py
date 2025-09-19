from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_start_keyboard(web_app_url: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    web_app = types.WebAppInfo(url=f'{web_app_url}/?user_id={user_id}')
    web_app_butt = types.InlineKeyboardButton(text='testan otish', web_app=web_app)

    builder.add(web_app_butt)

    builder.row(
        InlineKeyboardButton(text="meming natijalarim", callback_data="results"),
                InlineKeyboardButton(text="tahlil", callback_data="analysis")
    )

    return builder.as_markup()


def create_tests_keyboard(attempts: dict, user_id: int):
    builder = InlineKeyboardBuilder()

    for user_attempt, test in attempts.items():
        # Формируем callback_data в формате userid::test_key
        callback_data = f"testanalysis_{user_id}::{user_attempt.id}"

        # Добавляем кнопку с названием теста
        builder.button(text=test.test_name, callback_data=callback_data)

    # Располагаем кнопки в один столбец
    builder.adjust(1)

    return builder.as_markup()
