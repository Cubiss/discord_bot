import sqlite3

from classes.accesslevels import AccessLevel


class User:
    def __init__(self, user_id: int, user_name: str, access_level: AccessLevel):
        self.id = user_id
        self.name = user_name
        self.access_level = access_level


class Users:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

        if not self.table_exists():
            self.create_table()

        self.user_list = []
        self.load()
        pass

    def load(self):
        c = self.db.cursor()
        c.execute('select '
                  ' USER_ID, '
                  ' USER_NAME, '
                  ' Users.ACCESS_LEVEL as ACCESS_LEVEL, '
                  ' AccessLevels.Name as ACCESS_LEVEL_NAME '
                  'from '
                  ' Users join AccessLevels on Users.ACCESS_LEVEL = AccessLevels.ACCESS_LEVEL')
        c.row_factory = sqlite3.Row

        for row in c.fetchall():
            self.user_list.append(
                User(
                    user_id=int(row['USER_ID']),
                    user_name=str(row['USER_NAME']),
                    access_level=AccessLevel(
                        level=int(row['ACCESS_LEVEL']),
                        name=str(row['ACCESS_LEVEL_NAME'])
                    )
                )
            )

    def table_exists(self):
        c = self.db.cursor()
        c.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' and name = 'Users'"
            "ORDER BY name ;"
        )
        return len(c.fetchall()) > 0

    def create_table(self):
        c: sqlite3.Cursor = self.db.cursor()
        c.execute(
            '''CREATE TABLE "Users" (
                "USER_ID"	INTEGER NOT NULL,
                "USER_NAME"	TEXT,
                "ACCESS_LEVEL"	INTEGER NOT NULL,
                PRIMARY KEY("USER_ID")
            );'''
        )
        self.db.commit()
