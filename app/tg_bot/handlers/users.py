from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.tg_bot.keyboards.callback import get_start_keyboard, create_tests_keyboard
from app.models.dao import (get_all_results,
                            get_user_answers,
                            get_all_test_attempts,
                            stop_testing,
                            get_all_users_results,
                            get_user_data,
                            get_test_info, get_test_answers,
                            add_new_admin)

user_router = Router()

@user_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    await message.answer(f"Assalomu alaykum! 👋 <b>{message.from_user.full_name}</b>"
                              f"📋 Test ishlash uchun pastdagi tugmani bosing:",
                         reply_markup=get_start_keyboard(message.bot.config.BASE_URL, message.from_user.id))


@user_router.callback_query(F.data == "results")
async def get_all_results_handler(callback: CallbackQuery) -> None:
    results = await get_all_results(user_id=callback.from_user.id, async_session_maker=callback.bot.async_session_maker)

    if not results.items():
        await callback.message.reply('Siz hali test yechmagansiz')
        return

    text_parts = ['Test natijalari']
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
        text='testni tanlang',
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


async def test_results_message_parts(test_id: int, session: AsyncSession, redis: Redis) -> list:
    results = (await get_all_users_results(test_id,
                                           async_session_maker=session))
    results.reverse()
    test_info = await get_test_info(test_id, async_session_maker=session, redis=redis)

    message_parts = ['Test natijalari:\n\n'
                     f'Test nomi: {test_info["test_name"]}'
                     f'Test kodi: {test_id}\n\n']

    medals = ['🥇', '🥈', '🥉']
    for i, attempt in enumerate(results):
        user_data = await get_user_data(user_id=attempt.user_id, async_session_maker=session)
        full_name = f'{user_data.lastname} {user_data.username}'
        medal = medals[i] if i < len(medals) else ''

        message_parts.append(f'{full_name} - {attempt.score} ta {medal}')

    message_parts.append('\n\nToʻgʻri javoblar: ')

    answers = await get_test_answers(test_id, async_session_maker=session)
    for answer in answers:
        message_parts.append(f'{answer.question_number} - {answer.correct_answer}')

    message_parts.append('\nTestda ishtirok etgan barchaga rahmat😊')
    return message_parts


@user_router.callback_query(F.data.split('::')[0] == 'stop_test')
async def stop_test(callback: CallbackQuery) -> None:
    await stop_testing(test_id=callback.data.split('::')[-1],
                    async_session_maker=callback.bot.async_session_maker,
                    redis=callback.bot.redis)
    await callback.message.reply('Test yakunlandi!')
    test_id = int(callback.data.split('::')[-1])
    message_parts = await test_results_message_parts(test_id=test_id,
                                                     session=callback.bot.async_session_maker,
                                                     redis=callback.bot.redis)

    await callback.message.reply(text='\n'.join(message_parts))


@user_router.callback_query(F.data.split('::')[0] == 'get_results_test')
async def get_results_test(callback: CallbackQuery) -> None:
    test_id = int(callback.data.split('::')[-1])
    message_parts = await test_results_message_parts(test_id=test_id,
                                                     session=callback.bot.async_session_maker,
                                                     redis=callback.bot.redis)

    await callback.message.reply(text='\n'.join(message_parts))


@user_router.callback_query(F.data.split('::')[0] == 'allow_admin')
async def allow_admin(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split('::')[-1])

    await add_new_admin(user_id=user_id, async_session_maker=callback.bot.async_session_maker)
    await callback.bot.send_message(chat_id=callback.bot.config.ADMIN_ID,
                                    text=f'Siz {user_id} id bilan odamga test yaratishga ruhsat berdingiz')
    await callback.bot.send_message(chat_id=user_id, text='Sizga test yaratishga ruhsat berilindi')
