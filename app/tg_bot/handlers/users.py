from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from app.tg_bot.keyboards.callback import (create_tests_keyboard,
                                           channel_subscription,
                                           instruction_videos_keyboard,
                                           get_test_create_url,
                                           get_test_pass_url)
from app.tg_bot.keyboards.keyboard import menu_keyboard
from app.models.dao import (get_all_results,
                            get_user_answers,
                            get_all_test_attempts)
from app.tg_bot.filters import ChannelSubscriptionFilter

user_router = Router()


@user_router.callback_query(F.data == 'channels_check')
async def check_channels_subscription(callback: CallbackQuery) -> None:
    if await ChannelSubscriptionFilter().__call__(callback.message, callback.bot):
        await callback.message.answer(text=f'Assalomu alaykum! 👋 <b>{callback.from_user.full_name}</b>\n'
                                           f'📋 Test ishlash uchun pastdagi tugmani bosing:',
                                      reply_markup=menu_keyboard())

    await callback.bot.send_message(chat_id=callback.from_user.id,
                                    text='Botdan foydalanish uchun quyidagi kanallarga a\'zo bo\'ling.',
                                    reply_markup=channel_subscription(callback.bot.config.CHANNELS_ID))


@user_router.message(CommandStart(), ChannelSubscriptionFilter())
async def start_handler(message: Message) -> None:
    await message.answer(text=f'Assalomu alaykum! 👋 <b>{message.from_user.full_name}</b>\n'
                              f'📋 Test ishlash uchun pastdagi tugmani bosing:',
                         reply_markup=menu_keyboard())


@user_router.message(F.text == '➕Test yaratish', ChannelSubscriptionFilter())
async def create_test_handler(message: Message) -> None:
    await message.bot.send_message(chat_id=message.from_user.id,
                                    text='Yoʻriqnoma https://telegra.ph/Test-yaratish-boyicha-yoriqnoma-10-22',
                                    reply_markup=get_test_create_url(message.bot.config.BASE_URL, message.from_user.id))


@user_router.message(F.text == '✅Javobni tekshirish', ChannelSubscriptionFilter())
async def pass_test_handler(message: Message) -> None:
    await message.bot.send_message(chat_id=message.from_user.id,
                                    text='Yoʻriqnoma https://telegra.ph/Test-topshirish-boyicha-yoriqnoma-10-22',
                                    reply_markup=get_test_pass_url(message.bot.config.BASE_URL, message.from_user.id))


@user_router.message(F.text == '🤖Xizmatlar', ChannelSubscriptionFilter())
async def get_services_handler(message: Message) -> None:
    await message.bot.send_message(chat_id=message.from_user.id,
                                    text='🤖 Xizmatlar — Jahongir Academy Bot\n'
                                         'Salom! @JahongirAcademyBot sizga quyidagi xizmatlarni taklif etadi 👇\n\n'
                                         '💡 1. Test yaratish va o‘tkazish\n'
                                         'O‘zingizning testlaringizni yarating 📝, savollar qo‘shing va boshqalar bilan '
                                         'ulashing.\n'
                                         '🎯 Ideal yechim o‘qituvchilar, kurs egalari va mentorlar uchun!\n\n'
                                         '🧠 2. Test topshirish\n'
                                         'Tayyor testlarni ishlang, natijalaringizni darhol bilib oling 📊\n'
                                         '🔍 Bilimingizni sinab ko‘ring va o‘zingizni rivojlantiring!\n\n'
                                         '📲 Boshlash uchun:\n'
                                         '👉 @JahongirAcademyBot ni oching va kerakli xizmatni tanlang!')


@user_router.message(F.text == 'ℹ️Bot haqida ma\'lumotlar', ChannelSubscriptionFilter())
async def get_bot_info_handler(message: Message) -> None:
    await message.bot.send_message(chat_id=message.from_user.id,
                                   text='ℹ️ Bot haqida ma’lumotlar\n\n'
                                        'Salom! 👋\n'
                                        '@JahongirAcademyBot — bu ta’lim sohasidagi yordamchi bot, sizga testlar '
                                        'yaratish va topshirish jarayonini oson va qulay tarzda tashkil etishda yordam '
                                        'beradi 🎓\n\n'
                                        '💼 Bot nimalarni qila oladi?\n'
                                        '1️⃣ Test yaratadi va o‘tkazadi — Siz o‘zingizning testlaringizni tuzishingiz, '
                                        'savollarni qo‘shishingiz va natijalarni kuzatishingiz mumkin.\n'
                                        '2️⃣ Test topshirish imkonini beradi — Foydalanuvchilar tayyor testlarni bajarib,'
                                        ' o‘z natijalarini darhol ko‘rishadi.\n'
                                        '3️⃣ Natijalarni tahlil qiladi — Test yakunida siz to‘g‘ri va noto‘g‘ri '
                                        'javoblaringizni ko‘rib chiqishingiz mumkin 📊\n\n'
                                        '🎯 Nima uchun kerak?\n'
                                        'Bu bot — o‘qituvchilar, o‘quv markazlari, talabalar va mustaqil o‘rganuvchilar '
                                        'uchun ajoyib yordamchi.\n'
                                        'U ta’lim jarayonini raqamlashtirish, tezkor natijalar olish va bilim darajasini '
                                        'oshirish imkonini beradi 🚀\n\n'
                                        '📲 Boshlash uchun:\n'
                                        '@JahongirAcademyBot ni oching va menyudan kerakli bo‘limni tanlang 🤖')


@user_router.message(F.text == "📊Natijalarim", ChannelSubscriptionFilter())
async def get_all_results_handler(message: Message) -> None:
    results = await get_all_results(user_id=message.from_user.id, async_session_maker=message.bot.async_session_maker)

    if not results.items():
        await message.reply('Siz hali test yechmagansiz')
        return

    text_parts = ['Test natijalari:\n']
    for test_name, result in results.items():
        text_parts.append(
            f"<b>📊 Test natijalari:</b> {test_name}\n"
            f"<b>✅ To'g'ri javoblar:</b> {result.correct_answers}\n"
            f"<b>❌ Noto'g'ri javoblar:</b> {result.wrong_answers}\n"
            f"<b>⭐ Ball:</b> {result.score}\n"
            f"<b>🕐 Boshlanish vaqti:</b> {result.started_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"<b>🕓 Tugash vaqti:</b> {result.completed_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"{'─' * 30}\n"
        )
    await message.reply(
        text=''.join(text_parts),
        parse_mode="HTML",
    )


@user_router.message(F.text == '🔍Test tahlili', ChannelSubscriptionFilter())
async def get_all_test(message: Message) -> None:
    attempts = (await get_all_test_attempts(user_id=message.from_user.id,
                                            async_session_maker=message.bot.async_session_maker))
    if not attempts:
        await message.reply('Siz hali test yechmagansiz')
        return

    await message.reply(
        text='Testni tanlang',
        reply_markup=create_tests_keyboard(attempts=attempts, user_id=message.from_user.id)
    )


@user_router.callback_query(F.data.split('_')[0] ==  'testanalysis')
async def get_analysis(callback: CallbackQuery) -> None:
    user_attempt = int(callback.data.split('::')[-1])
    answers = await get_user_answers(user_attempt=user_attempt, async_session_maker=callback.bot.async_session_maker)

    text_parts = ['<b>👤 Foydalanuvchi javoblari:</b>\n\n']
    question_number = 0
    for answer in answers:
        question_number += 1
        status = "✅" if answer.is_correct else "❌"
        text_parts.append(
            f'{question_number} || {answer.user_answer if answer.user_answer != "None" else "Javob yozilmagan"} :: {status}\n'
            )

    await callback.message.answer(text=''.join(text_parts))


@user_router.message(F.text == '🎬Video qo\'llanma')
async def get_video_instruction(message: Message) -> None:
    await message.answer('Video instruksiyalar',
                         reply_markup=instruction_videos_keyboard())


@user_router.callback_query(F.data == 'instruction_videos_create')
async def get_instruction_videos_create(callback: CallbackQuery) -> None:
    await callback.bot.send_video(callback.from_user.id, video=callback.bot.config.VIDEO_ID[0])


@user_router.callback_query(F.data == 'instruction_videos_pass')
async def get_instruction_videos_create(callback: CallbackQuery) -> None:
    await callback.bot.send_video(callback.from_user.id, video=callback.bot.config.VIDEO_ID[1])


@user_router.message()
async def check_channels_subscription(message: Message) -> None:
    await message.bot.send_message(chat_id=message.from_user.id,
                           text='Botdan foydalanish uchun quyidagi kanallarga a\'zo bo\'ling.',
                           reply_markup=channel_subscription(message.bot.config.CHANNELS_ID))
