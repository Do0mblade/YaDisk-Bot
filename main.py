
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

async def on_startup(dp): # выполняется при запуске бота
    print('Database:\n', await db.db())
    loop = asyncio.get_event_loop() # создаём loop event
    t = Thread(target=loop_in_thread, args=(loop,)) # создаём функцию в другом потоке
    t.start() # запускаем

# команда /start
@dp.message_handler(commands = ['start'])
async def start(message: types.Message): # /start - регистрация
    if not await db.user_exists(message.from_user.id): # Проверяем есть ли человек в базе данных
        start_command = message.text
        refferer_id = str(start_command[7:]) # делаем срез команды, для получения id пригласившего пользователя
        await bot.send_message(message.from_user.id, '♻️ Выберите язык', reply_markup=nav.choose_lang(refferer_id)) # просим выбрать язык
    else: # Если человек есть в бд, то выводим текст
        lang = (await db.get_lang(message.from_user.id))[0] # получаем язык пользователя
        await message.answer('✅ '+_('Вы уже зарегистрировались!', lang), reply_markup=nav.MainMenu(lang)) # отправляем сообщение, что пользователь уже зарегестрирован и выводим клавиатуру главного меню

@dp.message_handler(commands=['profile', 'me', 'профиль'])
async def user_profile(message: types.Message): # /profile - посмотреть профиль человека.
    if await db.user_exists(message.from_user.id): # проверка на пользователя в бд
        user = await db.user_info(message.from_user.id) # достаём всю инфу о пользователе
        lang = user[3] # получаем язык пользователя

        if user[2] is None: # проверяем есть ли у пользователя реферал
            ref = ""
        else: # если есть, то добавляем его в строку
            ref_username = await db.get_refferer_username(user[2])
            ref = f"🎫 <i>{_('Вас приглосил', lang)}</i>: <b>@{ref_username[0]}</b>"

        if user[4] is None: # если нет статуса, то добавляем об этом информацию и ставим все остальные строки пустыми
            stat = '♻️ ' + _('Выберите ваш статус ниже', lang)
            ref_url = ""
            yat = ""
            reffs = ""
        elif user[4] == 'Организатор': # если пользователь организатор
            me = await bot.get_me() # получаем инфу о боте
            stat = f"⚜️ {_('Ваш статус', lang)}: <b><u>{_(user[4], lang)}</u></b>" # добавляем статус в строку
            ref_url = f"\n✉️ <i>{_('Ваша реферальная ссылка', lang)}</i>: \n<code><b>https://t.me/{me.username}?start={message.from_user.id}</b></code>" # добавляем реферальную ссылку в строку
            reffers = await db.get_referers(message.from_user.id) # получаем количество рефералов пользователя
            reffs = f"\n👥 <i>{_('Ваши рефералы', lang)}</i>: {reffers}" # добавляем количество рефералов в строку
            if user[5] is None: # если нет токена, то просим его добавить по инструкции
                yat = f"<b>\n📃 {_('Пожалуйста, напишите /token, чтобы получить инструкции по получению токена.', lang)}</b>"
            else: # если токен есть, добавляем его в строку
                yat = f"<i>\n🔑 {_('Ваш токен Яндекс', lang)}</i>: <code>{user[5]}</code>"
        else: # если пользователь участник, то добавляем его статус в строку и оставляем остальные строки пустыми
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
    """ # структурируем текст
        await message.answer(text, reply_markup=nav.chooseStatus(user[4], lang), parse_mode='HTML') # отправляем пользователю
    else:
        await message.answer('📃 Пожалуйства введите команду /start') # если пользователь не зарегистрирован, просим его это сделать

@dp.message_handler(commands=['add_folder'])
async def add_folder(message: types.Message): # функция для добавки паки в бд
    if await db.user_exists(message.from_user.id): # проверка на регистрацию
        lang = (await db.get_lang(message.from_user.id))[0] # получаем язык пользователя
        if (await db.get_status(message.from_user.id))[0] == 'Организатор': # проверка на статус
            token = (await db.get_yatoken(message.from_user.id))[0] # получаем токен
            if token is None: # если токена нет, то просим его добавить
                await message.reply('❌ '+_('Для начала ваш необходимо загрузить в бота токен!\n\nДля этого воспользуйтесь командой /token', lang))
            else: # иначе продолжаем проверку
                if await yd.check_token(token): # если токен валиден, идём дальше
                    data = message.text # получаем текст сообщения
                    dt = data.split() # разделяем сообщение
                    if len(dt) == 1: # если нет пути к папке, то пересылаем на инструкцию
                        await help(message)
                    else: # иначе продолжаем проверку
                        path_folder = data[12:] # делаем срез, чтобы получить путь к папке
                        if path_folder[-1] == '/': # проверяем какой последний символ
                            pass
                        else: # если не /, то ставим
                            path_folder = path_folder + '/'
                        check_folder = await db.select_folders(message.from_user.id) # достаём все папки пользователя
                        yatoken = (await db.get_yatoken(message.from_user.id))[0] # достаём Яндекс токен
                        if check_folder is None: # если папок нет, то идём дальше
                            if await yd.check_folder(path_folder, yatoken): # проверяем валидность папки
                                try:
                                    await db.insert_YaFolder(message.from_user.id, yatoken, path_folder) # добавляем папку в бд
                                    await message.answer('✅ '+_('Путь к вашей папке <b><code>{}</code></b> был успешно загружен!', lang).format(path_folder),
                                                         parse_mode='HTML') # выводим сообщение об успешном добавлении
                                except KeyError: # если есть ошибка, то обрабатываем её
                                    await message.answer('❌ '+_('Неизвестная ошибка, попробуйте снова, если такое повторится, свяжитесь с администрацией.', lang))
                                    await message.answer(f'{KeyError}')
                            else: # иначе отправляем сообщение об ошибке
                                await message.answer('❌ '+_('Ваша папка не найдена!', lang))
                        else: # иначе делаем проверку
                            if await db.select_folder(message.from_user.id, path_folder): # если папка найдена в бд, выводим сообщение об ошибке
                                await message.answer('❌ '+_('Вы уже добавляли эту папку!', lang))
                            else: # иначе продолжаем проверку
                                if await yd.check_folder(path_folder, yatoken): # проверяем валидность папки
                                    try:
                                        await db.insert_YaFolder(message.from_user.id, yatoken, path_folder) # добавляем папку в бд
                                        await message.answer('✅ '+_('Путь к вашей папке <b><code>{}</code></b> был успешно загружен!', lang).format(path_folder), parse_mode='HTML') # выводим сообщение об супешном добавлении
                                    except KeyError: # если есть ошибка, то обрабатываем её
                                        await message.answer('❌ '+_('Неизвестная ошибка, попробуйте снова, если такое повторится, свяжитесь с администрацией.', lang))
                                        await message.answer('⛔️ '+f'<code>{KeyError}</code>', parse_mode='HTML')
                                else: # иначе отправляем сообщение об ошибке
                                    await message.answer('❌ '+_('Ваша папка не найдена!', lang))
                else: # если токен не валиден, выводим об этом сообщение
                    await message.answer('❌ '+_('Ваш токен не валиден, попробуйте отправить его снова или получить новый', lang))
        else: # если у пользователя нет прав, для использования этой команды, то выводим сообщение
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else: # если пользователь не найден в бд, то просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['del_folder'])
async def delete_folder(message: types.Message): # удаление папки из бд
    if await db.user_exists(message.from_user.id): # проверка не регистрацию
        lang = (await db.get_lang(message.from_user.id))[0] # получаем язык пользователя
        if (await db.get_status(message.from_user.id))[0] == 'Организатор': # проверка статуса
            data = message.text # получаем текст сообщения
            dt = data.split() # разделяем текст
            if len(dt) == 1: # если не указан путь, выводим сообщение с ошибкой
                await message.answer('❌ '+_('Вы не ввели путь к папке.', lang))
            else: # иначе продолжаем проверку
                path_folder = data[12:] # делаем срез, чтобы получить путь
                if path_folder[-1] == '/':  # проверяем какой последний символ
                    pass
                else:  # если не /, то ставим
                    path_folder = path_folder + '/'
                check_folder = await db.select_folder(message.from_user.id, path_folder) # ищем папку в бд
                if check_folder is None: # если папки нет, то выводим сообщение с ошибкой
                    await message.answer('❌ '+_('Ваша папка не найдена!', lang))
                else: # иначе удаляем папку
                    try:
                        await db.delete_folder(message.from_user.id, path_folder) # удаляем папку
                        await message.answer('✅ '+_('Данная папка больше не отслеживается', lang)) # выводим сообщение
                    except KeyError: # если есть ошибка, обрабатываем её
                        await message.answer('❌ '+_('Неизвестная ошибка, попробуйте снова, если такое повторится, свяжитесь с администрацией.', lang))
                        await message.answer('⛔️ '+f'<code>{KeyError}</code>', parse_mode='HTML')
        else: # если у пользователя нет прав, для использования данной команды, выводим сообщение
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else: # если пользователь не найден в бд, то просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['folders'])
async def delete_folder(message: types.Message): # функция для вывода всех папок пользователя
    if await db.user_exists(message.from_user.id): # проверка на регистрацию
        lang = (await db.get_lang(message.from_user.id))[0] # получаем язык
        if (await db.get_status(message.from_user.id))[0] == 'Организатор': # проверка на права
            folders = (await db.select_folders(message.from_user.id)) # получаем все папки
            if len(folders) < 1: # если их нет, выводим сообщение
                await message.answer('🔕 '+_('У вас пока нет отслеживаемых папок.', lang))
            else: # иначе выводим список папок
                tx = []
                for i in folders:
                    tx.append(i[0])
                t = "\n".join(map(str, tx))
                text = '📚 '+_('Вот все ваши папки:\n\n<b><code>{}</code></b>\n\nУдалить их можно введя команду <code>/del_folder [папка]</code>', lang).format(t)
                await message.answer(text, parse_mode='HTML')
        else:  # если у пользователя нет прав, для использования данной команды, выводим сообщение
            await message.reply('❌ ' + _('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else:  # если пользователь не найден в бд, то просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['help'])
async def help(message: types.Message): # help - инструкция для добавления папок ( доработать )
    if await db.user_exists(message.from_user.id): # проверка на регистрацию
        text = 'ℹ️ '+'Чтобы добавить папку для сканирования, вам необходимо ввести команду, как указано в примерах:\n<b>/add_folder /my_folder/</b>\n<b>/add_folder /Загрузки/my_folder1/my_folder2/\n/add_folder /Общий доступ/my_folder/</b>\n\nПо умолчанию бот ищет нужную вам папку во вкладке <b>"Файлы"</b>'
        await message.answer(text, parse_mode='HTML')
    else: # если пользователя нет в бд, просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['token'])
async def info_token(message: types.Message): # инструкция по получению токена или его загрузка
    if await db.user_exists(message.from_user.id): # проверка на регистрацию
        lang = (await db.get_lang(message.from_user.id))[0] # получаем язык
        if (await db.get_status(message.from_user.id))[0] == 'Организатор': # проверка прав
            data = message.text
            dt = data.split()
            if len(dt) == 1: # если нет аргументов, выводим инструкцию
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

            elif len(dt) == 2: # если аргумента 2, проверяем потенциальный токен
                token = data[7:] # делаем срез, для получения токена
                db_token = (await db.get_yatoken(message.from_user.id))[0] # получаем токен пользователя из бд
                if str(token) != str(db_token): # если они разные, то продолжаем проверку
                    answer = await yd.check_token(token) # отправляем токен на проверку
                    if answer is False: # если ошибка, то выводим сообщение
                        await message.reply('❌ '+_('Ваш токен не валиден, попробуйте отправить его снова или получить новый', lang))
                    else: # иначе выгружаем токен в бд и выводим сообщение
                        await db.update_token(message.from_user.id, token)
                        await message.answer('✅ '+_('Ваш токен был успешно загружен, можете приступать к работе.', lang))
                else: # иначе выводим ошибку
                    await message.answer('📥 '+_('Этот токен уже установлен.', lang))
            else: # иначе выводим ошибку
                await message.answer('❌ '+_('Вы ввели более 1 аргумента!', lang))
        else: # если у пользователя нет прав, для использования данной команды, выводим сообщение
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else: # если пользователя нет в бд, просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['check'])
async def check_yandex_token(message: types.Message): # функция для проверки токена
    if await db.user_exists(message.from_user.id): # проверка на регистрацию
        lang = (await db.get_lang(message.from_user.id))[0] # получаем язык
        if (await db.get_status(message.from_user.id))[0] == 'Организатор': # проверка на права
            yatoken = (await db.get_yatoken(message.from_user.id))[0] # получаем токен из бд
            answer = await yd.check_token(yatoken) # отправляем на проверку
            if answer is False: # не валиден - выводим ошибку
                await message.reply('❌ '+_('Ваш токен не валиден, попробуйте отправить его снова или получить новый', lang))
            else: # валиден - выводим сообщение
                await message.reply('✅ '+_('С вашим токеном всё в порядке!', lang))
        else: # если у пользователя нет прав, для использования данной команды, выводим сообщение
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else: # если пользователя нет в бд, просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.message_handler(commands=['client_id'])
async def info_token(message: types.Message): # функция для получения ссылки на token через client id
    if await db.user_exists(message.from_user.id): # проверка на регистрацию
        lang = (await db.get_lang(message.from_user.id))[0] # получаем язык
        if (await db.get_status(message.from_user.id))[0] == 'Организатор': # проверка прав
            data = message.text # получаем текст сообщения
            client_id = data[11:] # делаем срез
            if len(client_id) > 0: # если аргументом больше 1, то выводим ссылку
                await message.reply('🌐 '+_('<a href="https://oauth.yandex.ru/authorize?response_type=token&client_id={}">Перейдите по ссылке</a>', lang).format(client_id), parse_mode='HTML')
            else: # иначе выводим ошибку
                await message.reply('❌ '+_('Укажите ваш client_id!', lang))
        else: # если у пользователя нет прав, для использования данной команды, выводим сообщение
            await message.reply('❌ '+_('Вы не можете воспользоваться данной командой, так как не являетесь организатором!', lang))
    else: # если пользователя нет в бд, просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

async def settings(message: types.Message): # настройки языка
    if await db.user_exists(message.from_user.id): # проверка на регистрацию
        lang = (await db.get_lang(message.from_user.id))[0] # получаем язык
        await message.answer('♻️ '+_('Выберите язык', lang), reply_markup=nav.choose_lang()) # предлагаем выбор языка
    else: # если пользователя нет в бд, просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

@dp.callback_query_handler(text_contains="delete_account")
async def DeleteAccount(callback: types.CallbackQuery): # спрашиваем пользователя, точно ли он хочет удалить аккаунт
    if await db.user_exists(callback.from_user.id): # проверка на регистрацию
        await bot.delete_message(callback.from_user.id, callback.message.message_id) # удаляем предыдущее сообщение
        lang = (await db.get_lang(callback.from_user.id))[0] # получаем язык
        await bot.send_message(callback.from_user.id, '🗑 '+_('Вы уверены, что хотите удалить аккаунт?', lang), reply_markup=nav.delete_account(lang)) # уточняем
    else: # если пользователя нет в бд, просим зарегистрироваться
        await bot.send_message(callback.from_user.id, '📃 Пожалуйства введите команду /start')

@dp.callback_query_handler(text_contains="delet_acc_")
async def DeleteAccountCheck(callback: types.CallbackQuery): # обработка удаления аккаунта
    if await db.user_exists(callback.from_user.id): # проверка на регистрацию
        lang = (await db.get_lang(callback.from_user.id))[0] # получаем язык
        await bot.delete_message(callback.from_user.id, callback.message.message_id) # удаляем предыдущее сообщение
        data = callback.data # получаем дату
        answer = data[10:] # делаем срез, чтобы узнать ответ
        if answer == 'yes': # если да, то удаляем аккаунт и всё остальное
            await db.delete_accaunt(callback.from_user.id) # удаляем аккаунт
            await db.delete_all_folders(callback.from_user.id) # удаляем все папки
            await db.delete_all_files(callback.from_user.id) # удаляем все файлы
            await db.delete_reff_for_users(callback.from_user.id) # удаляем у всех рефералку
            await bot.send_message(callback.from_user.id, '✅ '+_('Ваш аккаунт был успешно удалён!', lang)) # отправляем сообщение
    else: # если пользователя нет в бд, просим зарегистрироваться
        await bot.send_message(callback.from_user.id, '📃 Пожалуйства введите команду /start')


@dp.callback_query_handler(text_contains="status_")
async def setStatus(callback: types.CallbackQuery): # обработка выдачи статуса
    if await db.user_exists(callback.from_user.id): # проверка на регистрацию
        lang = (await db.get_lang(callback.from_user.id))[0] # получаем язык
        await bot.delete_message(callback.from_user.id, callback.message.message_id) # удаляем предыдущее сообщение
        data = callback.data # получаем дату
        status = data[7:] # делаем срез
        if status == 'organizer' or status == 'Organizer': # заменяем английский текст на русский
            status = 'Организатор'
        elif status == 'participant' or status == 'Participant': # заменяем английский текст на русский
            status = 'Участник'
        await db.update_status(callback.from_user.id, status) # обновляем статус
        await bot.send_message(callback.from_user.id, '✅ '+_('Ваш статус был обновлён!', lang)) # отправляем сообщение
    else: # если пользователя нет в бд, просим зарегистрироваться
        await bot.send_message(callback.from_user.id, '📃 Пожалуйства введите команду /start')

@dp.callback_query_handler(text_contains="lang_")
async def setLanguage(callback: types.CallbackQuery): # обрабатываем регистрацию или смену языка
        await bot.delete_message(callback.from_user.id, callback.message.message_id) # удаляем предыдущее сообщение
        data = callback.data # получаем дату
        dt = data[5:] # делаем срез
        if len(dt) == 3: # проверка на код языка
            lang = dt.strip() # удаляем лишние пробелы
            refferer_id = "" # оставляем реферала пустым
        else: # иначе добавляем реферала и пишем код языка
            refferer_id = dt[3:] # реферал
            lang = dt[0:2] # код языка

        if not await db.user_exists(callback.from_user.id):  # Проверяем есть ли человек в базе данных
            r_id = None # по дефолту None
            username = callback.from_user.username # получаем username пользователя
            if str(refferer_id) != "": # Проверка на рефералку
                if str(refferer_id) == str(callback.from_user.id): # Проверка на собственную рефералку
                    await db.add_user(callback.from_user.id, lang, r_id, username) # добавляем в бд
                    await bot.send_message(callback.from_user.id, '✅ '+_('Вы успешно зарегистрировались!', lang), reply_markup=nav.MainMenu(lang)) # отправляем сообщение
                else:
                    await db.add_user(callback.from_user.id, lang, refferer_id, username) # добавляем в бд
                    await bot.send_message(callback.from_user.id, '✅ '+_('Вы успешно зарегистрировались!', lang), reply_markup=nav.MainMenu(lang)) # отправляем сообщение
                    await bot.send_message(refferer_id, '🆕 '+_('Добавлен новый пользователь', lang)+f': @{username}') # отправляем сообщение, что добавлен новый реферал
            else: # Если человек не реферал, то регестрируем иначе
                await db.add_user(callback.from_user.id, lang, r_id, username) # добавляем в бд
                await bot.send_message(callback.from_user.id, '✅ '+_('Вы успешно зарегистрировались!', lang), reply_markup=nav.MainMenu(lang)) # отправляем сообщение
        else:
            old_lang = await db.get_lang(callback.from_user.id) # получаем старый язык
            if lang != old_lang[0]: #  есл они не равны
                await db.update_lang(callback.from_user.id, lang) # меняем язык
                await bot.send_message(callback.from_user.id, '✅ '+_('Язык был успешно обновлён!', lang),reply_markup=nav.MainMenu(lang)) # отправляем сообщение
            else: #  иначе отправляем сообщение
                await bot.send_message(callback.from_user.id, '📥 '+_('Выбранный язык уже установлен!', lang), reply_markup=nav.MainMenu(lang)) # отправляем сообщение

@dp.message_handler()
async def redirection(message: types.Message): # переадресация
    if await db.user_exists(message.from_user.id): # проверка на регистрацию
        profile_ = ['👤 Профиль', '👤 профиль', 'Профиль', 'профиль', '👤 Profile', '👤 profile', 'Profile', 'profile']
        settings_ = ['⚙️ Настройки', '⚙️ настройки', 'Настройки', 'настройки', '⚙️ Settings', '⚙️ settings', 'Settings', 'settings']
        if message.text in profile_:
            await user_profile(message)
        if message.text in settings_:
            await settings(message)
    else: # если пользователя нет в бд, просим зарегистрироваться
        await message.answer('📃 Пожалуйства введите команду /start')

# запуск бота
if __name__ == '__main__': # запуск проекта
    print('Bot is ready!')
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True) # запуск бота
