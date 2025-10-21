from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def channel_subscription(channels_list: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for channel in channels_list:
        builder.row(InlineKeyboardButton(text=channel, url=f'https://t.me/{channel}'))

    builder.row(InlineKeyboardButton(text='Tekshirish✅', callback_data='channels_check'))

    return builder.as_markup()


def get_test_create_url(web_app_url: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    create_test_web_app = types.WebAppInfo(url=f'{web_app_url}/create/test/?user_id={user_id}')
    create_test_web_app_butt = types.InlineKeyboardButton(text='🔬 Test yaratish', web_app=create_test_web_app)
    builder.add(create_test_web_app_butt)

    return builder.as_markup()


def get_test_pass_url(web_app_url: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    pass_web_app = types.WebAppInfo(url=f'{web_app_url}/?user_id={user_id}')
    pass_web_app_butt = types.InlineKeyboardButton(text='✏️ Testni boshlash', web_app=pass_web_app)
    builder.add(pass_web_app_butt)

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

    builder.add(InlineKeyboardButton(text='❌ Testni toʻxtatish', callback_data=f'stop_test::{test_id}'))
    builder.add(InlineKeyboardButton(text='📊 Natijalar', callback_data=f'get_results_test::{test_id}'))

    return builder.as_markup()


def allow_admin_keyboard(user_id: int):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='Ruhsat bermoq', callback_data=f'allow_admin::{user_id}'))

    return builder.as_markup()


def instruction_videos_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text='🔬 Test yaratish', callback_data='instruction_videos_create'))
    builder.row(InlineKeyboardButton(text='✏️ Testdan oʻtish', callback_data='instruction_videos_pass'))

    return builder.as_markup()