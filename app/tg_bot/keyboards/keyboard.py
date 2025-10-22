from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text='➕Test yaratish'),
            KeyboardButton(text='✅Javobni tekshirish')
        ],
        [
            KeyboardButton(text='🤖Xizmatlar'),
            KeyboardButton(text='ℹ️Bot haqida ma\'lumotlar')
        ],
        [
            KeyboardButton(text='📊Natijalarim'),
            KeyboardButton(text='🔍Test tahlili')
        ],
        [KeyboardButton(text='🎬Video qo\'llanma')]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder='Quyidagi menyulardan birini tanlang'
    )

