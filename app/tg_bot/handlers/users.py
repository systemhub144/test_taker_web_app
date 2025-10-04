from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.tg_bot.keyboards.callback import get_start_keyboard, create_tests_keyboard
from app.models.dao import get_all_results, get_user_answers, get_all_test_attempts


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
