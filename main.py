
# imports

from config.bot import TOKEN
from defs.db import Database
import defs.markups as nav
from defs.translation import _
from defs.yandex import Yandex_Disc, loop_in_thread

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InputFile

from threading import Thread

import asyncio

# инициализация бота

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

db = Database()
yd = Yandex_Disc()

async def on_startup(dp):
    print('Database:\n', await db.db())
    loop = asyncio.get_event_loop()
    t = Thread(target=loop_in_thread, args=(loop,))
    t.start()

# команда /start
@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    if not await db.user_exists(message.from_user.id): # Проверяем есть ли человек в базе данных
        start_command = message.text
        refferer_id = str(start_command[7:])
        await bot.send_message(message.from_user.id, '♻️ Выберите язык', reply_markup=nav.choose_lang(refferer_id))
    else: # Если человек есть в бд, то выводим текст
        lang = (await db.get_lang(message.from_user.id))[0]
        await message.answer('✅ '+_('Вы уже зарегестрировались!', lang), reply_markup=nav.MainMenu(lang))

# /profile - посмотреть профиль человека.
@dp.message_handler(commands=['profile', 'me', 'профиль'])
async def user_profile(message: types.Message):
    if await db.user_exists(message.from_user.id):
        lang = (await db.get_lang(message.from_user.id))[0]
        user = await db.user_info(message.from_user.id)
        lang = (await db.get_lang(message.from_user.id))[0]

        if user[2] is None:
            ref = ""
        else:
            ref_username = await db.get_refferer_username(user[2])
            ref = f"🎫 <i>{_('Вас приглосил', lang)}</i>: <b>@{ref_username[0]}</b>"

        if user[4] is None:
            stat = '♻️ ' + _('Выберите ваш статус ниже', lang)
            ref_url = ""
            yat = ""
            reffs = ""
        elif user[4] == 'Организатор':
            me = await bot.get_me()
            stat = f"⚜️ {_('Ваш статус', lang)}: <b><u>{_(user[4], lang)}</u></b>"
            ref_url = f"\n✉️ <i>{_('Ваша реферальная ссылка', lang)}</i>: \n<code><b>https://t.me/{me.username}?start={message.from_user.id}</b></code>"
            reffers = await db.get_referers(message.from_user.id)
            reffs = f"\n👥 <i>{_('Ваши рефералы', lang)}</i>: {reffers}"
            if user[5] is None:
                yat = f"<b>\n📃 {_('Пожалуйста, напишите /token, чтобы получить инструкции по получению токена.', lang)}</b>"
            else:
                yat = f"<i>\n🔑 {_('Ваш токен Яндекс', lang)}</i>: <code>{user[5]}</code>"
        else:
            stat = f"🃏 <i>{_('Ваш статус', lang)}</i>: <b><u>{_(user[4], lang)}</u></b>"
            ref_url = ""
            yat = ""
            reffs = ""


        text = f"""
👤 <i>{_('Ваше имя', lang)}</i>: <b>{message.from_user.full_name}</b>
{ref}
{stat}
{reffs}
{ref_url}
{yat}
    """
        await message.answer(text, reply_markup=nav.chooseStatus(user[4], lang), parse_mode='HTML')
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['add_folder'])
async def add_folder(message: types.Message):
    if await db.user_exists(message.from_user.id):
        lang = (await db.get_lang(message.from_user.id))[0]
        if (await db.get_status(message.from_user.id))[0] == 'Организатор':
            token = (await db.get_yatoken(message.from_user.id))[0]
            if token is None:
                await message.reply('❌ '+_('Для начала ваш необходимо загрузить в бота токен!\n\nДля этого воспользуйтесь командой /token', lang))
            else:
                if await yd.check_token(token):
                    data = message.text
                    dt = data.split()
                    if len(dt) == 1:
                        await help(message)
                    else:
                        path_folder = data[12:]
                        if path_folder[-1] == '/':
                            pass
                        else:
                            path_folder = path_folder + '/'
                        check_folder = await db.select_folders(message.from_user.id)
                        yatoken = (await db.get_yatoken(message.from_user.id))[0]
                        if check_folder is None:
                            if await yd.check_folder(path_folder, yatoken):
                                try:
                                    await db.insert_YaFolder(message.from_user.id, yatoken, path_folder)
                                    await message.answer('✅ '+_('Путь к вашей папке <b><code>{}</code></b> был успешно загружен!', lang).format(path_folder),
                                                         parse_mode='HTML')
                                except KeyError:
                                    await message.answer('❌ '+_('Неизвестная ошибка, попробуйте снова, если такое повторится, свяжитесь с администрацией.', lang))
                                    await message.answer(f'{KeyError}')
                            else:
                                await message.answer('❌ '+_('Ваша папка не найдена!', lang))
                        else:
                            if await db.select_folder(message.from_user.id, path_folder):
                                await message.answer('❌ '+_('Вы уже добавляли эту папку!', lang))
                            else:
                                if await yd.check_folder(path_folder, yatoken):
                                    try:
                                        await db.insert_YaFolder(message.from_user.id, yatoken, path_folder)
                                        await message.answer('✅ '+_('Путь к вашей папке <b><code>{}</code></b> был успешно загружен!', lang).format(path_folder), parse_mode='HTML')
                                    except KeyError:
                                        await message.answer('❌ '+_('Неизвестная ошибка, попробуйте снова, если такое повторится, свяжитесь с администрацией.', lang))
                                        await message.answer('⛔️ '+f'<code>{KeyError}</code>', parse_mode='HTML')
                                else:
                                    await message.answer('❌ '+_('Ваша папка не найдена!', lang))
                else:
                    await message.answer('❌ '+_('Ваш токен не валиден, попробуйте отправить его снова или получить новый', lang))
        else:
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['del_folder'])
async def delete_folder(message: types.Message):
    if await db.user_exists(message.from_user.id):
        lang = (await db.get_lang(message.from_user.id))[0]
        if (await db.get_status(message.from_user.id))[0] == 'Организатор':
            data = message.text
            dt = data.split()
            if len(dt) == 1:
                await message.answer('❌ '+_('Вы не ввели путь к папке.', lang))
            else:
                path_folder = data[12:]
                if path_folder[-1] == '/':
                    pass
                else:
                    path_folder = path_folder + '/'
                check_folder = await db.select_folders(message.from_user.id)
                if check_folder is None:
                    await message.answer('❌ '+_('Ваша папка не найдена!', lang))
                else:
                    try:
                        await db.delete_folder(message.from_user.id, path_folder)
                        await message.answer('✅ '+_('Данная папка больше не отслеживается', lang))
                    except KeyError:
                        await message.answer('❌ '+_('Неизвестная ошибка, попробуйте снова, если такое повторится, свяжитесь с администрацией.', lang))
                        await message.answer('⛔️ '+f'<code>{KeyError}</code>', parse_mode='HTML')
        else:
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['folders'])
async def delete_folder(message: types.Message):
    if await db.user_exists(message.from_user.id):
        lang = (await db.get_lang(message.from_user.id))[0]
        if (await db.get_status(message.from_user.id))[0] == 'Организатор':
            folders = (await db.select_folders(message.from_user.id))
            if len(folders) < 1:
                await message.answer('🔕 '+_('У вас пока нет отслеживаемых папок.', lang))
            else:
                tx = []
                for i in folders:
                    tx.append(i[0])
                t = "\n".join(map(str, tx))
                text = '📚 '+_('Вот все ваши папки:\n\n<b><code>{}</code></b>\n\nУдалить их можно введя команду <code>/del_folder [папка]</code>', lang).format(t)
                await message.answer(text, parse_mode='HTML')
        else:
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    if await db.user_exists(message.from_user.id):
        text = 'ℹ️ '+'Чтобы добавить папку для сканирования, вам необходимо ввести команду, как указано в примерах:\n<b>/add_folder /my_folder/</b>\n<b>/add_folder /Загрузки/my_folder1/my_folder2/\n/add_folder /Общий доступ/my_folder/</b>\n\nПо умолчанию бот ищет нужную вам папку во вкладке <b>"Файлы"</b>'
        await message.answer(text, parse_mode='HTML')
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['token'])
async def info_token(message: types.Message):
    if await db.user_exists(message.from_user.id):
        lang = (await db.get_lang(message.from_user.id))[0]
        if (await db.get_status(message.from_user.id))[0] == 'Организатор':
            data = message.text
            dt = data.split()
            if len(dt) == 1:
                await message.reply(
                    'ℹ️'+_("Для получения токена вам надо выполнить несколько несложных действий.\n\nНиже расписано всё по пунктам.", lang),
                    parse_mode='HTML')
                await bot.send_photo(chat_id=message.from_user.id, photo=InputFile("imgs/primer_photo_1.png"),
                                     caption=_("1. Зайти на <a href='https://oauth.yandex.ru/client/new'>сайт</a> яндекса и создать приложение.\nНеобходимо придумать любое название для приложения, поставить галочку <b><u>Веб-сервисы</u></b> и вставить эту ссылку: <b><code>https://oauth.yandex.ru/verification_code</code></b>", lang),
                                     parse_mode='HTML')
                await asyncio.sleep(0.5)
                await bot.send_photo(chat_id=message.from_user.id, photo=InputFile("imgs/primer_photo_2.png"),
                                     caption=_("2. Поставить разрешения как на скриншоте.", lang), parse_mode='HTML')
                await asyncio.sleep(0.5)
                await bot.send_photo(chat_id=message.from_user.id, photo=InputFile("imgs/primer_photo_3.png"),
                                     caption=_("3. Скопировать ваш <b><u>Client ID</u></b>, написать команду /client_id [ваш client id]\n\nНапример:\n<b>/client_id 80baa4fdjk4j54ff45gdba37</b>", lang),
                                     parse_mode='HTML')
                await asyncio.sleep(0.5)
                await bot.send_photo(chat_id=message.from_user.id, photo=InputFile("imgs/primer_photo_4.png"),
                                     caption=_("4. Далее копируем ваш <b><u>Token</u></b> и отправляем боту при помощи команды /token [ваш token]\n\nНапример:\n<b>/token y0_AgAAAAAy60ZURNGEUIINM545NvFTICdggmle22U-cDkOwI</b>", lang),
                                     parse_mode='HTML')

            elif len(dt) == 2:
                token = data[7:]
                db_token = (await db.get_yatoken(message.from_user.id))[0]
                if str(token) != str(db_token):
                    answer = await yd.check_token(token)
                    if answer is False:
                        await message.reply('❌ '+_('Ваш токен не валиден, попробуйте отправить его снова или получить новый', lang))
                    else:
                        await db.update_token(message.from_user.id, token)
                        await message.answer('✅ '+_('Ваш токен был успешно загружен, можете приступать к работе.', lang))
                else:
                    await message.answer('📥 '+_('Этот токен уже установлен.', lang))
            else:
                await message.answer('❌ '+_('Вы ввели более 1 аргумента!', lang))
        else:
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['check'])
async def check_yandex_token(message: types.Message):
    if await db.user_exists(message.from_user.id):
        lang = (await db.get_lang(message.from_user.id))[0]
        if (await db.get_status(message.from_user.id))[0] == 'Организатор':
            yatoken = (await db.get_yatoken(message.from_user.id))[0]
            answer = await yd.check_token(yatoken)
            if answer is False:
                await message.reply('❌ '+_('Ваш токен не валиден, попробуйте отправить его снова или получить новый', lang))
            else:
                await message.reply('✅ '+_('С вашим токеном всё в порядке!', lang))
        else:
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['client_id'])
async def info_token(message: types.Message):
    if await db.user_exists(message.from_user.id):
        lang = (await db.get_lang(message.from_user.id))[0]
        if (await db.get_status(message.from_user.id))[0] == 'Организатор':
            data = message.text
            client_id = data[11:]
            if len(client_id) > 0:
                await message.reply('🌐 '+_('<a href="https://oauth.yandex.ru/authorize?response_type=token&client_id={}">Перейдите по ссылке</a>', lang).format(client_id), parse_mode='HTML')
            else:
                await message.reply('❌ '+_('Укажите ваш client_id!', lang))
        else:
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler()
async def redirection(message: types.Message):
    if await db.user_exists(message.from_user.id):
        profile_ = ['👤 Профиль', '👤 профиль', 'Профиль', 'профиль', '👤 Profile', '👤 profile', 'Profile', 'profile']
        settings_ = ['⚙️ Настройки', '⚙️ настройки', 'Настройки', 'настройки', '⚙️ Settings', '⚙️ settings', 'Settings', 'settings']
        if message.text in profile_:
            await user_profile(message)
        if message.text in settings_:
            await settings(message)
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler()
async def settings(message: types.Message):
    if await db.user_exists(message.from_user.id):
        lang = (await db.get_lang(message.from_user.id))[0]
        await message.answer('♻️ '+_('Выберите язык', lang), reply_markup=nav.choose_lang())
    else:
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.callback_query_handler(text_contains="delete_account")
async def DeleteAccount(callback: types.CallbackQuery):
    if await db.user_exists(callback.from_user.id):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        lang = (await db.get_lang(callback.from_user.id))[0]
        await bot.send_message(callback.from_user.id, '🗑 '+_('Вы уверены, что хотите удалить аккаунт?', lang), reply_markup=nav.delete_account(lang))
    else:
        await bot.send_message(callback.from_user.id, '📃 Пожалуйства введите команду /start')

@dp.callback_query_handler(text_contains="delet_acc_")
async def DeleteAccountCheck(callback: types.CallbackQuery):
    if await db.user_exists(callback.from_user.id):
        lang = (await db.get_lang(callback.from_user.id))[0]
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        data = callback.data
        answer = data[10:]
        if answer == 'yes':
            await db.delete_accaunt(callback.from_user.id)
            await db.delete_all_folders(callback.from_user.id)
            await db.delete_all_files(callback.from_user.id)
            await db.delete_reff_for_users(callback.from_user.id)
            await bot.send_message(callback.from_user.id, '✅ '+_('Ваш аккаунт был успешно удалён!', lang))
    else:
        await bot.send_message(callback.from_user.id, '📃 Пожалуйства введите команду /start')


@dp.callback_query_handler(text_contains="status_")
async def setStatus(callback: types.CallbackQuery):
    if await db.user_exists(callback.from_user.id):
        lang = (await db.get_lang(callback.from_user.id))[0]
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        data = callback.data
        status = data[7:]
        if status == 'organizer':
            status = 'Организатор'
        elif status == 'participant':
            status = 'Участник'
        await db.update_status(callback.from_user.id, status)
        await bot.send_message(callback.from_user.id, '✅ '+_('Ваш статус был обновлён!', lang))
    else:
        await bot.send_message(callback.from_user.id, '📃 Пожалуйства введите команду /start')

@dp.callback_query_handler(text_contains="lang_")
async def setLanguage(callback: types.CallbackQuery):
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        data = callback.data
        dt = data[5:]
        if len(dt) == 3:
            lang = dt.strip()
            refferer_id = ""
        else:
            refferer_id = dt[3:]
            lang = dt[0:2]

        if not await db.user_exists(callback.from_user.id):  # Проверяем есть ли человек в базе данных
            r_id = None
            username = callback.from_user.username
            if str(refferer_id) != "": # Проверка на рефералку
                if str(refferer_id) == str(callback.from_user.id): # Проверка на собственную рефералку
                    await db.add_user(callback.from_user.id, lang, r_id, username)
                    await bot.send_message(callback.from_user.id, '✅ '+_('Вы успешно зарегистрировались!', lang), reply_markup=nav.MainMenu(lang))
                else:
                    await db.add_user(callback.from_user.id, lang, refferer_id, username)
                    await bot.send_message(callback.from_user.id, '✅ '+_('Вы успешно зарегистрировались!', lang), reply_markup=nav.MainMenu(lang))
                    await bot.send_message(refferer_id, '🆕 '+_('Добавлен новый пользователь', lang)+f': @{username}')
            else: # Если человек не реферал, то регестрируем иначе
                await db.add_user(callback.from_user.id, lang, r_id, username)
                await bot.send_message(callback.from_user.id, '✅ '+_('Вы успешно зарегистрировались!', lang), reply_markup=nav.MainMenu(lang))
        else:
            old_lang = await db.get_lang(callback.from_user.id)
            if lang != old_lang[0]:
                await db.update_lang(callback.from_user.id, lang)
                await bot.send_message(callback.from_user.id, '✅ '+_('Язык был успешно обновлён!', lang),reply_markup=nav.MainMenu(lang))
            else:
                await bot.send_message(callback.from_user.id, '📥 '+_('Выбранный язык уже установлен!', lang), reply_markup=nav.MainMenu(lang))


# запуск бота
if __name__ == '__main__':
    print('Bot is ready!')
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
