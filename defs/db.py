
import sqlite3

class Database(): # класс для работы с базой данных
    def __init__(self):
        self.connection = sqlite3.connect('database.db') # подключаемся к базе данных, если файла нет - он создастся
        self.cursor = self.connection.cursor() # создаём объект cursor

        with self.connection: # при подключении к бд
            self.connection.execute("""
            create table if not exists users (
                id integer not null primary key autoincrement, 
                user_id integer not null,
                refferer_id integer,
                lang varchar,
                status varchar,
                yatoken text,
                username varchar not null
            )
            """) # создаём таблицу в бд

            self.connection.execute("""
                        create table if not exists yandex_folders (
                            id integer not null primary key autoincrement, 
                            user_id integer not null,
                            yatoken text,
                            folder_path varchar not null
                        )
                        """) # создаём таблицу в бд

            self.connection.execute("""
                                    create table if not exists yandex_files (
                                        id integer not null primary key autoincrement, 
                                        folder_path integer not null,
                                        file_name varchar not null,
                                        user_id integer not null
                                    )
                                    """) # создаём таблицу в бд

    async def db(self): # достаём все данные из таблицы users
        with self.connection:
            return self.cursor.execute("SELECT * FROM users").fetchall()

    async def insert_YaFolder(self, user_id, yatoken, folder_path): # внесение данных в таблицу yandex_folders
        with self.connection:
            self.cursor.execute(f"INSERT INTO yandex_folders (user_id, yatoken, folder_path) VALUES ({user_id}, '{yatoken}', '{folder_path}')")

    async def select_folders(self, user_id): # достаём все пути к папкам, которые пользователь загрузил
        with self.connection:
            result = self.cursor.execute(f"SELECT folder_path FROM yandex_folders WHERE user_id = {user_id}").fetchall()
            return result

    async def select_folder(self, user_id, path): # достаём нужную папку из бд
        with self.connection:
            result = self.cursor.execute(f"SELECT folder_path FROM yandex_folders WHERE user_id = {user_id} AND folder_path = '{path}'").fetchone()
            return result

    async def delete_folder(self, user_id, path): # удаляем ненужную папку и её файлы из бд
        with self.connection:
            self.cursor.execute(f"DELETE FROM yandex_folders WHERE user_id = {user_id} AND folder_path = '{path}'")
            self.cursor.execute(f"DELETE FROM yandex_files WHERE user_id = {user_id} AND folder_path = '{path}'")

    async def add_folder(self, user_id, folder_path): # добавляем путь к папке в бд
        with self.connection:
            return self.cursor.execute(f"INSERT INTO yandex_folders (user_id, folder_path) VALUES ({user_id}, '{folder_path}')")

    async def user_exists(self, user_id): # проверка есть ли пользователь в бд
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}").fetchall()
            return bool(len(result))

    async def add_user(self, user_id, language, refferer_id, username): # вносим пользователя в бд
        if refferer_id is None:
            self.cursor.execute(f"INSERT INTO users (user_id, lang, username) VALUES ({user_id}, '{language}', '{username}')") # если пользователь не реферал
        else:
            self.cursor.execute(f"INSERT INTO users (user_id, lang, refferer_id, status, username) VALUES ({user_id}, '{language}', {refferer_id}, 'Участник', '{username}')") # если пользователь реферал


    async def user_info(self, user_id): # получаем всю информацию о пользователе из бд
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}").fetchone()
            return result

    async def get_lang(self, user_id): # достаём язык пользователя из бд
        with self.connection:
            return self.cursor.execute(f"SELECT lang FROM users WHERE user_id = {user_id}").fetchone()

    async def get_yatoken(self, user_id): # достаём Яндекс токен пользователя из бд
        with self.connection:
            return self.cursor.execute(f"SELECT yatoken FROM users WHERE user_id = {user_id}").fetchone()

    async def update_lang(self, user_id, lang): # обновляем язык пользователя
        with self.connection:
            self.cursor.execute(f"UPDATE users SET lang = '{lang}' WHERE user_id = {user_id}")

    async def get_status(self, user_id): # достаём статус пользователя
        with self.connection:
            return self.cursor.execute(f"SELECT status FROM users WHERE user_id = {user_id}").fetchone()

    async def update_status(self, user_id, status): # обновляем статус пользователя
        with self.connection:
            self.cursor.execute(f"UPDATE users SET status = '{status}' WHERE user_id = {user_id}")

    async def delete_accaunt(self, user_id): # удаляем аккаунт пользователя
        with self.connection:
            self.cursor.execute(f"DELETE FROM users WHERE user_id = {user_id}")

    async def update_token(self, user_id, token): # обновляем токен пользователя
        with self.connection:
            self.cursor.execute(f"UPDATE users SET yatoken = '{token}' WHERE user_id = {user_id}")

    async def get_referers(self, refferer_id): # достаём количество рефералов у пользователя
        with self.connection:
            return len(self.cursor.execute(f"SELECT user_id FROM users WHERE refferer_id = {refferer_id}").fetchall())

    async def delete_all_folders(self, user_id): # удаляем все папки пользователя
        with self.connection:
            try:
                self.cursor.execute(f"DELETE FROM yandex_folders WHERE users_id = {user_id}")
            except:
                pass

    async def delete_all_files(self, user_id): # удаляем все файлы пользователя
        with self.connection:
            try:
                self.cursor.execute(f"DELETE FROM yandex_files WHERE users_id = {user_id}")
            except:
                pass

    async def delete_reff_for_users(self, user_id): # удаляем этого пользователя, как реферала у других пользователей
        with self.connection:
            try:
                self.cursor.execute(f"UPDATE users SET refferer_id = None WHERE refferer_id = {user_id}")
            except:
                pass

    async def get_refferer_username(self, ref_id): # получаем username пользователя, по его id
        with self.connection:
            return self.cursor.execute(f"SELECT username FROM users WHERE user_id = {ref_id}").fetchone()