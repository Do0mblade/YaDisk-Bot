
import sys

from config.bot import TOKEN
from .db import Database
from .translation import _

from aiogram import Bot
from aiogram.dispatcher import Dispatcher

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

db = Database()

@dp.message_handler()
async def send_ref_mess(ref_username, reffs_id, download_link, file_name, cursor):
    for i in reffs_id:
        lang = (cursor.execute(f"SELECT lang FROM users WHERE user_id = {i[0]}").fetchone())[0]
        await bot.send_message(i[0], ('🆕 '+_('Пользователь @{} добавил новый файл на свой Яндекс Диск.\nФайл: <a href="{}">{}</a>', lang).format(ref_username[0], download_link, file_name)), parse_mode='HTML')


