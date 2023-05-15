
import sqlite3

class Database():
    def __init__(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

        with self.connection:
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
            """)

            self.connection.execute("""
                        create table if not exists yandex_folders (
                            id integer not null primary key autoincrement, 
                            user_id integer not null,
                            yatoken text,
                            folder_path varchar not null
                        )
                        """)

            self.connection.execute("""
                                    create table if not exists yandex_files (
                                        id integer not null primary key autoincrement, 
                                        folder_path integer not null,
                                        file_name varchar not null,
                                        user_id integer not null
                                    )
                                    """)

    async def db(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users").fetchall()

    async def insert_YaFolder(self, user_id, yatoken, folder_path):
        with self.connection:
            self.cursor.execute(f"INSERT INTO yandex_folders (user_id, yatoken, folder_path) VALUES ({user_id}, '{yatoken}', '{folder_path}')")

    async def select_folders(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT folder_path FROM yandex_folders WHERE user_id = {user_id}").fetchall()
            return result

    async def select_folder(self, user_id, path):
        with self.connection:
            result = self.cursor.execute(f"SELECT folder_path FROM yandex_folders WHERE user_id = {user_id} AND folder_path = '{path}'").fetchone()
            return result

    async def delete_folder(self, user_id, path):
        with self.connection:
            self.cursor.execute(f"DELETE FROM yandex_folders WHERE user_id = {user_id} AND folder_path = '{path}'")
            self.cursor.execute(f"DELETE FROM yandex_files WHERE user_id = {user_id} AND folder_path = '{path}'")

    async def add_folder(self, user_id, folder_path):
        with self.connection:
            return self.cursor.execute(f"INSERT INTO yandex_folders (user_id, folder_path) VALUES ({user_id}, '{folder_path}')")

    async def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}").fetchall()
            return bool(len(result))

    async def add_user(self, user_id, language, refferer_id, username):
        if refferer_id is None:
            self.cursor.execute(f"INSERT INTO users (user_id, lang, username) VALUES ({user_id}, '{language}', '{username}')")
        else:
            print(username)
            self.cursor.execute(f"INSERT INTO users (user_id, lang, refferer_id, status, username) VALUES ({user_id}, '{language}', {refferer_id}, 'Участник', '{username}')")


    async def user_info(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}").fetchone()
            return result

    async def get_lang(self, user_id):
        with self.connection:
            return self.cursor.execute(f"SELECT lang FROM users WHERE user_id = {user_id}").fetchone()

    async def get_yatoken(self, user_id):
        with self.connection:
            return self.cursor.execute(f"SELECT yatoken FROM users WHERE user_id = {user_id}").fetchone()

    async def update_lang(self, user_id, lang):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET lang = '{lang}' WHERE user_id = {user_id}")

    async def get_status(self, user_id):
        with self.connection:
            return self.cursor.execute(f"SELECT status FROM users WHERE user_id = {user_id}").fetchone()

    async def update_status(self, user_id, status):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET status = '{status}' WHERE user_id = {user_id}")

    async def delete_accaunt(self, user_id):
        with self.connection:
            self.cursor.execute(f"DELETE FROM users WHERE user_id = {user_id}")

    async def update_token(self, user_id, token):
        with self.connection:
            self.cursor.execute(f"UPDATE users SET yatoken = '{token}' WHERE user_id = {user_id}")

    async def get_referers(self, refferer_id):
        with self.connection:
            return len(self.cursor.execute(f"SELECT user_id FROM users WHERE refferer_id = {refferer_id}").fetchall())

    async def delete_all_folders(self, user_id):
        with self.connection:
            try:
                self.cursor.execute(f"DELETE FROM yandex_folders WHERE users_id = {user_id}")
            except:
                pass

    async def delete_all_files(self, user_id):
        with self.connection:
            try:
                self.cursor.execute(f"DELETE FROM yandex_files WHERE users_id = {user_id}")
            except:
                pass

    async def delete_reff_for_users(self, user_id):
        with self.connection:
            try:
                self.cursor.execute(f"UPDATE users SET refferer_id = None WHERE refferer_id = {user_id}")
            except:
                pass

    async def get_refferer_username(self, ref_id):
        with self.connection:
            return self.cursor.execute(f"SELECT username FROM users WHERE user_id = {ref_id}").fetchone()