from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text='➕Test yaratish'),
            KeyboardButton(text='✅Javobni tekshirish')
        ],
        [
            KeyboardButton(text='🤖xizmatlar'),
            KeyboardButton(text='ℹ️Bot haqida ma\'lumot')
        ],
        [
            KeyboardButton(text='📊 Natijalarim'),
            KeyboardButton(text='🔍 Test tahlili')
        ],
        [KeyboardButton(text='🎬 Video instruksiyalar')]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder='Quyidagi menyulardan birini tanlang'
    )

