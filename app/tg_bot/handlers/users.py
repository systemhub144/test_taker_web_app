from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from app.tg_bot.keyboards.callback import (get_start_keyboard,
                                           create_tests_keyboard,
                                           channel_subscription,
                                           instruction_videos_keyboard)
from app.models.dao import (get_all_results,
                            get_user_answers,
                            get_all_test_attempts)

user_router = Router()


async def channels_check_message(bot: Bot, user_id: int, user_full_name: str):
    unsubscribed_channels = []
    for channel in bot.config.CHANNELS_ID:
        print(channel)
        user_channel_status = await bot.get_chat_member(chat_id=f'@{channel}', user_id=user_id)
        if user_channel_status.status == 'left':
            unsubscribed_channels.append(channel)

    if not unsubscribed_channels:
        await bot.send_message(chat_id=user_id,
                               text=f"Assalomu alaykum! 👋 <b>{user_full_name}</b>\n"
                                    f"📋 Test ishlash uchun pastdagi tugmani bosing:",
                               reply_markup=get_start_keyboard(bot.config.BASE_URL, user_id))
        return

    await bot.send_message(chat_id=user_id,
                           text='Boshlashdan oldin \n'
                                'siz kanallarimizga obuna bo\'lishingiz lozim!',
                           reply_markup=channel_subscription(unsubscribed_channels))


@user_router.message()
async def command_start_handler(message: Message) -> None:
    await channels_check_message(bot=message.bot, user_id=message.from_user.id, user_full_name=message.from_user.full_name)


@user_router.callback_query(F.data == 'channels_check')
async def check_channels_subscription(callback: CallbackQuery) -> None:
    await channels_check_message(bot=callback.bot, user_id=callback.from_user.id, user_full_name=callback.from_user.full_name)


@user_router.callback_query(F.data == "results")
async def get_all_results_handler(callback: CallbackQuery) -> None:
    results = await get_all_results(user_id=callback.from_user.id, async_session_maker=callback.bot.async_session_maker)

    if not results.items():
        await callback.message.reply('Siz hali test yechmagansiz')
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
    await callback.message.reply(
        text=''.join(text_parts),
        parse_mode="HTML",
    )


@user_router.callback_query(F.data == 'analysis')
async def get_all_test(callback: CallbackQuery) -> None:
    attempts = (await get_all_test_attempts(user_id=callback.from_user.id,
                                            async_session_maker=callback.bot.async_session_maker))
    if not attempts:
        await callback.message.reply('Siz hali test yechmagansiz')
        return

    await callback.message.edit_text(
        text='Testni tanlang',
        reply_markup=create_tests_keyboard(attempts=attempts, user_id=callback.from_user.id)
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


@user_router.callback_query(F.data == 'video_instruction')
async def get_video_instruction(callback: CallbackQuery) -> None:
    await callback.message.answer('Video instruksiyalar',
                                  reply_markup=instruction_videos_keyboard())


@user_router.callback_query(F.data == 'instruction_videos_create')
async def get_instruction_videos_create(callback: CallbackQuery) -> None:
    await callback.bot.send_video(callback.from_user.id, video=callback.bot.config.VIDEO_ID[0])


@user_router.callback_query(F.data == 'instruction_videos_pass')
async def get_instruction_videos_create(callback: CallbackQuery) -> None:
    await callback.bot.send_video(callback.from_user.id, video=callback.bot.config.VIDEO_ID[1])