import copy
from io import BytesIO

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, BufferedInputFile
from redis import Redis
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy.ext.asyncio import AsyncSession

from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter


from app.models.dao import (stop_testing,
                            get_all_users_results,
                            get_user_data,
                            get_test_info, get_test_answers,
                            add_new_admin)
from app.config import PATH

admin_router = Router()

async def prepare_certificate(certificate, full_name: str) -> BufferedInputFile:
    overlay = BytesIO()
    c = canvas.Canvas(overlay, pagesize=(595, 842))

    font_name = "DejaVuSans-Bold"
    font_size = 28
    y = 410

    text_width = pdfmetrics.stringWidth(full_name, font_name, font_size)
    x = (549 - text_width) / 2

    c.setFont(font_name, font_size)
    c.drawString(x, y, full_name)
    c.save()

    overlay.seek(0)

    overlay_pdf = PdfReader(overlay)
    writer = PdfWriter()

    page = copy.copy(certificate)
    page.merge_page(overlay_pdf.pages[0])
    writer.add_page(page)

    result = BytesIO()
    writer.write(result)

    return BufferedInputFile(result.getvalue(), filename='certificate.pdf')


async def test_results_message_parts(test_id: int, session: AsyncSession, redis: Redis, bot: Bot, is_ending: bool) -> list:
    results = (await get_all_users_results(test_id,
                                           async_session_maker=session))
    test_info = await get_test_info(test_id, async_session_maker=session, redis=redis)

    message_parts = ['Test natijalari:\n\n'
                     f'Test nomi: {test_info["test_name"]}\n'
                     f'Test kodi: {test_id}\n\n']

    font_path = PATH / 'app/tg_bot/certificates/DejaVuSans-Bold.ttf'
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path))

    medals = ['🥇', '🥈', '🥉']
    for i, attempt in enumerate(results):
        user_data = await get_user_data(user_id=attempt.user_id, async_session_maker=session)
        full_name = f'{user_data.lastname} {user_data.username}'
        medal = medals[i] if i < len(medals) else ''
        message_parts.append(f'{i + 1}: {full_name} - {attempt.score} ball {medal}')

    message_parts.append('\n\nToʻgʻri javoblar: ')

    answers = await get_test_answers(test_id, async_session_maker=session)
    for answer in answers:
        message_parts.append(f'{answer.question_number} - {answer.correct_answer}')

    message_parts.append('\nTestda ishtirok etgan barchaga rahmat😊')
    return message_parts


async def send_certificates(test_id, bot: Bot, session: AsyncSession, redis: Redis):
    results = (await get_all_users_results(test_id,
                                           async_session_maker=session))
    test_info = await get_test_info(test_id, async_session_maker=session, redis=redis)

    certificate_list = [
        PdfReader(open(PATH / 'app/tg_bot/certificates/0.pdf', 'rb')).pages[0],
        PdfReader(open(PATH / 'app/tg_bot/certificates/1.pdf', 'rb')).pages[0],
        PdfReader(open(PATH / 'app/tg_bot/certificates/2.pdf', 'rb')).pages[0],
        PdfReader(open(PATH / 'app/tg_bot/certificates/3.pdf', 'rb')).pages[0],
    ]

    for i, attempt in enumerate(results):
        user_data = await get_user_data(user_id=attempt.user_id, async_session_maker=session)
        full_name = f'{user_data.lastname} {user_data.username}'
        await bot.send_message(chat_id=attempt.tg_user_id,
                               text=f'Testda qatnashganingiz uchun rahmat,\n'
                                    f'Natijalar:\n'
                                    f'Test nomi: {test_info["test_name"]}\n'
                                    f'Ball: {attempt.score}\n'
                                    f'O\'rningiz: {i + 1}')
        if i <= 2:
            file = await prepare_certificate(certificate_list[i], full_name)
        else:
            file = await prepare_certificate(certificate_list[3], full_name)
        await bot.send_document(chat_id=attempt.tg_user_id, document=file)


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
    await send_certificates(test_id=test_id,
                            session=callback.bot.async_session_maker,
                            redis=callback.bot.redis,
                            bot=callback.bot)


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
