import sqlite3
import discord


class User:
    def __init__(self,
                 db: sqlite3.Connection,
                 user_id: int = None,
                 user_name: str = None,
                 user: discord.User = None):
        self.db = db

        if user_id is None and user is None:
            raise Exception("Either user_id or user must be set.")

        self.id = user_id or user.id
        self.name = user_name or user.display_name
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

        if not self.permissions_table_exists():
            self.create_permissions_table()

        self._users = {}
        self.load()
        pass

    def __getitem__(self, user_id: int):
        if user_id in self._users:
            return self._users[user_id]
        else:
            return None

    def __setitem__(self, user_id: int, user: User):
        if user_id in self._users:
            raise KeyError("User already exists!")
        else:
            self._users[user_id](user)

    def get_or_create(self, user):
        assert(isinstance(user, discord.User) or isinstance(user, discord.Member))
        u = self._users[user.id]
        if u is None:
            u = User(db=self.db, user=user)
            self._users[u.id] = u
            u.save()

        return u

    def load(self):
        c = self.db.cursor()
        c.execute('select '
                  ' USER_ID, '
                  ' USER_NAME '
                  'from '
                  ' Users')
        c.row_factory = sqlite3.Row

        for row in c.fetchall():
            user_id = int(row['USER_ID'])
            self[user_id](
                User(
                    user_id=user_id,
                    user_name=str(row['USER_NAME']),
                    db=self.db
                )
            )

        c = self.db.cursor()
        c.execute('select '
                  ' USER_ID, '
                  ' PERMISSION_ID '
                  'from '
                  ' Permissions')
        c.row_factory = sqlite3.Row

        for row in c.fetchall():
            u = self[int(row['USER_ID'])]
            if u is not None:
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
                PRIMARY KEY("USER_ID")
            );'''
        )
        self.db.commit()

    def permissions_table_exists(self):
        c = self.db.cursor()
        c.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' and name = 'Permissions'"
            "ORDER BY name ;"
        )
        return len(c.fetchall()) > 0

    def create_permissions_table(self):
        c: sqlite3.Cursor = self.db.cursor()
        c.execute(
            '''CREATE TABLE "Users" (
                "USER_ID"	INTEGER NOT NULL,
                "PERMISSION_ID"	TEXT,
                PRIMARY KEY("USER_ID", "PERMISSION_ID")
            );'''
        )
        self.db.commit()
