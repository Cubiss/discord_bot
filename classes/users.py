import sqlite3


class User:
    def __init__(self, user_id: int, user_name: str, db: sqlite3.Connection):
        self.db = db
        self.id = user_id
        self.name = user_name
        self.permissions = []

    def save(self):
        c = self.db.cursor()

        c.execute(f"INSERT INTO Users (USER_ID, USER_NAME) VALUES ({self.id}, '{self.name}') "
                  f"ON CONFLICT(USER_ID) DO "
                  f"UPDATE SET USER_ID={self.id}, USER_NAME='{self.name}'")

        for p in self.permissions:
            c.execute(f"INSERT INTO Permissions(USER_ID, PERMISSION_ID) VALUES ({self.id}, '{p}') "
                      f"ON CONFLICT(USER_ID, PERMISSION_ID) DO NOTHING ")

    def remove(self):
        c = self.db.cursor()

        c.execute(f"DELETE FROM Users WHERE USER_ID = '{self.id}'")
        c.execute(f"DELETE FROM Permissions WHERE USER_ID = '{self.id}'")


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
                  ' USER_NAME '
                  'from '
                  ' Users')
        c.row_factory = sqlite3.Row

        for row in c.fetchall():
            self.user_list.append(
                User(
                    user_id=int(row['USER_ID']),
                    user_name=str(row['USER_NAME']),
                    db=self.db
                )
            )

        c = self.db.cursor()
        c.execute('select '
                  ' USER_ID, '
                  ' PERMISSION_ID '
                  'from '
                  ' Users')
        c.row_factory = sqlite3.Row

        for row in c.fetchall():
            for u in [u for u in self.user_list if u.id == int(row['USER_ID'])]:
                u.permissions.append(row['PERMISSION_ID'])

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
