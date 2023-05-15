
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
async def send_ref_mess(ref_username, reffs_id, download_link, file_name):
    for i in reffs_id:
        lang = await db.get_lang(i[0])
        await bot.send_message(i[0], _('Пользователь @{} добавил новый файл на свой Яндекс Диск.\nФайл: <a href="{}">{}</a>', lang).formate(ref_username[0], download_link, file_name), parse_mode='HTML')
