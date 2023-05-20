
# в этом файле все функции для работы с yandex

# импортируем нужные библиотеки
import asyncio

import yadisk_async

import sqlite3

# импортируем функцию для отправки сообщений
from .send_msgs import send_ref_mess

class Yandex_Disc(): #
    def __init__(self):
        pass
    async def check_token(self, token): # функция для проверки токена на валидность
        y = yadisk_async.YaDisk(token=token)
        try:
            answer = await y.check_token()
            await y.close()
            return answer
        except:
            await y.close()
            return False

    async def check_folder(self, path, token): # проверка папки на валидность
        y = yadisk_async.YaDisk(token=token)
        try:
            if [i async for i in await y.listdir(f"disk:{path}")]:
                await y.close()
                return True
        except:
            await y.close()
            return False


async def check_new_files(): # проверка дисков на новые файлы
    while True:
        await asyncio.sleep(18) # задержка
        connection = sqlite3.connect('database.db') # подключаемся к бд
        cursor = connection.cursor() # создаём объект cursor
        with connection:
            data = cursor.execute("SELECT * FROM yandex_folders").fetchall() # достаём все папки в бд
        for i in data:
            author_id = int(i[1]) # получаем id владельца папки
            y = yadisk_async.YaDisk(token=i[2]) # подключаемся к диску
            try:
                folder_data = [i async for i in (await y.listdir(f"disk:{i[3]}"))] # пытаемся достать информацию о файлах в папке
            except:
                folder_data = None # если не получилось, ставим значение None
            if folder_data is None: # если файлов нет, то пропускаем папку
                pass
            else: # иначе начинаем проверку
                for x in folder_data: # берём файлы последовательно
                    if x['file'] is None: # если это папка, то пропускаем
                        pass
                    else: # иначе начинаем проверку
                        file = cursor.execute(
                            f"""SELECT id FROM yandex_files WHERE file_name = '{x["name"]}' AND user_id = {author_id} AND folder_path = '{i[3]}'""").fetchone() # ищем этот файл в бд
                        if file is None: # если его нет, то заносим в бд и отправляем сообщение
                            download_link = x['file']
                            cursor.execute(
                                f"""INSERT INTO yandex_files (folder_path, file_name, user_id) VALUES ('{i[3]}', '{x['name']}', {author_id})""") # вносим файл в бд
                            connection.commit()
                            referals = cursor.execute(f"""SELECT user_id FROM users WHERE refferer_id = {author_id}""").fetchall() # достаём всех рефералов из бд
                            if len(referals) == 0: # если рефералов нет, то ничего не отправляем
                                pass
                            else: # иначе отправляем
                                ref_username = cursor.execute(f"SELECT username FROM users WHERE user_id = {author_id}").fetchone() # достаём username автора файла/папки
                                await send_ref_mess(ref_username, referals, download_link, x['name'], cursor) # вызываем функцию для отправки сообщений
                        else: # иначе пропускаем
                            pass
            await y.close() # закрываем соединение с диском

def loop_in_thread(loop): # запускаем асинхронную функцию для проверки файлов в другом потоке
    asyncio.set_event_loop(loop)
    asyncio.run(check_new_files())

