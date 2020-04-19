import sqlite3


class AccessLevel:
    def __init__(self, level: int, name: str = None):
        self.level = level
        self.name = name


class AccessLevels:
    def __init__(self, db: sqlite3.Connection):
        self.db = db
        pass

    def table_exists(self):
        c = self.db.cursor()
        c.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' and name = 'AccessLevels'"
            "ORDER BY name ;"
        )
        return len(c.fetchall()) > 0

    def create_table(self):
        c: sqlite3.Cursor = self.db.cursor()
        c.execute(
            '''CREATE TABLE "AccessLevels" (
                "ACCESS_LEVEL"	INTEGER NOT NULL,
                "NAME"	TEXT,
                PRIMARY KEY("ACCESS_LEVEL")
            );'''
        )
        self.db.commit()