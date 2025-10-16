from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_start_keyboard(web_app_url: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    create_test_web_app = types.WebAppInfo(url=f'{web_app_url}/create/test/?user_id={user_id}')
    create_test_web_app_butt = types.InlineKeyboardButton(text='🔬Test yaratish', web_app=create_test_web_app)
    builder.add(create_test_web_app_butt)

    pass_web_app = types.WebAppInfo(url=f'{web_app_url}/?user_id={user_id}')
    pass_web_app_butt = types.InlineKeyboardButton(text='✏️ Testni boshlash', web_app=pass_web_app)

    builder.add(pass_web_app_butt)

    builder.row(
        InlineKeyboardButton(text="📊 Natijalarim", callback_data="results"),
                InlineKeyboardButton(text="🔍 Test tahlili", callback_data="analysis")
    )

    return builder.as_markup()


def create_tests_keyboard(attempts: dict, user_id: int):
    builder = InlineKeyboardBuilder()

    for user_attempt, test in attempts.items():
        callback_data = f"testanalysis_{user_id}::{user_attempt.id}"
        builder.button(text=test.test_name, callback_data=callback_data)

    builder.adjust(1)

    return builder.as_markup()


def test_controls_keyboard(test_id: int):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='❌ Testni toxtatish', callback_data=f'stop_test::{test_id}'))
    builder.add(InlineKeyboardButton(text='📊 Natijalar', callback_data=f'get_results_test::{test_id}'))

    return builder.as_markup()


def allow_admin_keyboard(user_id: int):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='Ruhsat bermoq', callback_data=f'allow_admin::{user_id}'))

    return builder.as_markup()
