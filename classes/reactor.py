import sqlite3
import datetime
import random


class Reaction:
    def __init__(self, user_id, user_name, server_id, emote, chance, cooldown=0, enabled=True, db_id=None):
        self.id = db_id
        self.chance = chance
        self.emote = emote
        self.user_name = user_name
        self.user_id = user_id
        self.server_id = server_id
        self.cooldown = cooldown
        self.enabled = enabled
        self.last_used = datetime.datetime.min

    def save(self, db):
        c = db.cursor()
        if self.id is None:
            c.execute('SELECT MAX(ID) from Reactor')

            max_id = c.fetchone()[0]

            self.id = 1 if max_id is None else max_id + 1

            c.execute(
                'INSERT INTO Reactor(ID, USER_ID, USER_NAME, SERVER_ID, EMOTE, CHANCE, COOLDOWN, ENABLED) VALUES'
                f"({self.id}, {self.user_id}, '{self.user_name}', {self.server_id}, '{self.emote}', "
                f"{self.chance}, {self.cooldown}, {1 if self.enabled else 0})")
            db.commit()

    def remove(self, db: sqlite3.Connection):
        c = db.cursor()
        c.execute(f'DELETE from Reactor where ID = {self.id}')
        db.commit()


class Reactor:
    def __init__(self, db: sqlite3.Connection):
        self.reaction_list = []
        self.db = db
        if not self.table_exists():
            print('Table Reactor not found, creating a new one.')
            self.create_table()

        self.load()

    def load(self):
        c = self.db.cursor()
        c.execute('SELECT ID, USER_ID, USER_NAME, SERVER_ID, EMOTE, CHANCE, COOLDOWN, ENABLED from Reactor')
        c.row_factory = sqlite3.Row

        for row in c.fetchall():
            self.reaction_list.append(
                Reaction(
                    user_id=int(row['USER_ID']),
                    user_name=str(row['USER_NAME']),
                    server_id=int(row['SERVER_ID']),
                    emote=str(row['EMOTE']),
                    chance=float(row['CHANCE']),
                    enabled=int(row['ENABLED']) != 0,
                    cooldown=int(row['COOLDOWN']),
                    db_id=int(row['ID']),
                )
            )

    def add(self, reaction: Reaction):
        self.reaction_list.append(reaction)
        reaction.save(self.db)

    def get_reactions(self, user_id, server_id):
        retval = []
        for reaction in [r for r in self.reaction_list if r.user_id == user_id and r.server_id == server_id]:
            if reaction.chance > random.random():
                if datetime.datetime.now() > reaction.last_used + datetime.timedelta(seconds=reaction.cooldown):
                    retval.append(reaction.emote.replace('<', '').replace('>', ''))
                    reaction.last_used = datetime.datetime.now()

        return retval

    def table_exists(self):
        c = self.db.cursor()
        c.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' and name = 'Reactor'"
            "ORDER BY name ;"
        )
        return len(c.fetchall()) > 0

    def create_table(self):
        c: sqlite3.Cursor = self.db.cursor()
        c.execute(
            'CREATE TABLE "Reactor" ( '
            '	"ID"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '
            '	"USER_ID"	INTEGER, '
            '	"USER_NAME"	TEXT, '
            '	"EMOTE"	TEXT, '
            '	"CHANCE"	REAL DEFAULT 0, '
            '	"SERVER_ID"	INTEGER, '
            '	"COOLDOWN"	INTEGER, '
            '	"ENABLED"	INTEGER DEFAULT 1 '
            '); '
        )

    def remove(self, id: int):
        reactors = [r for r in self.reaction_list if r.id == id]
        for r in reactors:
            r.remove(self.db)
            self.reaction_list.remove(r)

        return len(reactors)
