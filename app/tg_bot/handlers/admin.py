from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.dao import (stop_testing,
                            get_all_users_results,
                            get_user_data,
                            get_test_info, get_test_answers,
                            add_new_admin)

admin_router = Router()


async def test_results_message_parts(test_id: int, session: AsyncSession, redis: Redis, bot: Bot, is_ending: bool) -> list:
    results = (await get_all_users_results(test_id,
                                           async_session_maker=session))
    results.reverse()
    test_info = await get_test_info(test_id, async_session_maker=session, redis=redis)

    message_parts = ['Test natijalari:\n\n'
                     f'Test nomi: {test_info["test_name"]}\n'
                     f'Test kodi: {test_id}\n\n']

    medals = ['🥇', '🥈', '🥉']
    for i, attempt in enumerate(results):
        user_data = await get_user_data(user_id=attempt.user_id, async_session_maker=session)
        full_name = f'{user_data.lastname} {user_data.username}'
        medal = medals[i] if i < len(medals) else ''

        if is_ending:
            await bot.send_message(chat_id=attempt.tg_user_id,
                text=f'Testda qatnashganingiz uchun rahmat,\n'
                     f'Natijalar:\n'
                     f'Test nomi: {test_info["test_name"]}\n'
                     f'Ball: {attempt.score}\n'
                     f'O\'rningiz: {i + 1}')
            await bot.send_document(chat_id=attempt.tg_user_id, document=bot.config.CERTIFICATE_ID[i]) if i <= 2 \
                else await bot.send_document(chat_id=attempt.tg_user_id, document=bot.config.CERTIFICATE_ID[3])

        message_parts.append(f'{full_name} - {attempt.score} ta {medal}')

    message_parts.append('\n\nToʻgʻri javoblar: ')

    answers = await get_test_answers(test_id, async_session_maker=session)
    for answer in answers:
        message_parts.append(f'{answer.question_number} - {answer.correct_answer}')

    message_parts.append('\nTestda ishtirok etgan barchaga rahmat😊')
    return message_parts


@admin_router.callback_query(F.data.split('::')[0] == 'stop_test')
async def stop_test(callback: CallbackQuery) -> None:
    await stop_testing(test_id=callback.data.split('::')[-1],
                    async_session_maker=callback.bot.async_session_maker,
                    redis=callback.bot.redis)
    await callback.message.reply('Test yakunlandi!')
    test_id = int(callback.data.split('::')[-1])
    message_parts = await test_results_message_parts(test_id=test_id,
                                                     session=callback.bot.async_session_maker,
                                                     redis=callback.bot.redis,
                                                     bot=callback.bot,
                                                     is_ending=True)

    await callback.message.reply(text='\n'.join(message_parts))


@admin_router.callback_query(F.data.split('::')[0] == 'get_results_test')
async def get_results_test(callback: CallbackQuery) -> None:
    test_id = int(callback.data.split('::')[-1])
    message_parts = await test_results_message_parts(test_id=test_id,
                                                     session=callback.bot.async_session_maker,
                                                     redis=callback.bot.redis,
                                                     bot=callback.bot,
                                                     is_ending=False)

    await callback.message.reply(text='\n'.join(message_parts))


@admin_router.callback_query(F.data.split('::')[0] == 'allow_admin')
async def allow_admin(callback: CallbackQuery) -> None:
    user_id = int(callback.data.split('::')[-1])

    await add_new_admin(user_id=user_id, async_session_maker=callback.bot.async_session_maker)
    await callback.bot.send_message(chat_id=callback.bot.config.ADMIN_ID,
                                    text=f'Siz {user_id} id bilan odamga test yaratishga ruhsat berdingiz')
    await callback.bot.send_message(chat_id=user_id, text='Sizga test yaratishga ruhsat berildi')


# @admin_router.message()
# def voice_cmd(message: Message) -> None:
#     # Узнаем id, если требуется
#     file_id = message.video.file_id
#     print(f'file_id: {file_id}') # Вывод id сообщения в консоль