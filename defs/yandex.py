import asyncio

import yadisk_async
from pprint import pprint

import sqlite3

from .send_msgs import send_ref_mess

from threading import Thread

class Yandex_Disc():
    def __init__(self):
        pass
    async def check_token(self, token):
        y = yadisk_async.YaDisk(token=token)
        try:
            answer = await y.check_token()
            await y.close()
            return answer
        except:
            await y.close()
            return False

    async def check_folder(self, path, token):
        y = yadisk_async.YaDisk(token=token)
        try:
            if [i async for i in await y.listdir(f"disk:{path}")]:
                await y.close()
                return True
        except:
            await y.close()
            return False


async def check_new_files():
    while True:
        await asyncio.sleep(10)
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        with connection:
            data = cursor.execute("SELECT * FROM yandex_folders").fetchall()
        for i in data:
            author_id = int(i[1])
            y = yadisk_async.YaDisk(token=i[2])
            try:
                folder_data = [i async for i in (await y.listdir(f"disk:{i[3]}"))]
            except:
                folder_data = None
            if folder_data is None:
                pass
            else:
                for x in folder_data:
                    if x['file'] is None:
                        pass
                    else:
                        download_link = x['file']
                        file = cursor.execute(
                            f"""SELECT id FROM yandex_files WHERE file_name = '{x["name"]}' AND user_id = {author_id}""").fetchone()
                        if file is None:
                            cursor.execute(
                                f"""INSERT INTO yandex_files (folder_path, file_name, user_id) VALUES ('{i[3]}', '{x['name']}', {author_id})""")
                            connection.commit()
                            referals = cursor.execute(f"""SELECT user_id FROM users WHERE refferer_id = {author_id}""").fetchall()
                            if len(referals) == 0:
                                pass
                            else:
                                ref_username = cursor.execute(f"SELECT username FROM users WHERE user_id = {author_id}").fetchone()
                                reffs_id = cursor.execute(f"SELECT user_id FROM users WHERE refferer_id = {author_id}").fetchall()
                                await send_ref_mess(ref_username, reffs_id, download_link, x['name'])
                        else:
                            pass
            await y.close()

def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    asyncio.run(check_new_files())

