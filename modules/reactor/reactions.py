from classes.entity import Entity, EntityItem, Column
import sqlite3
import datetime


class Reactions(Entity):
    def __init__(self, db: sqlite3.Connection):
        super().__init__(db,
                         "Reactor",
                         [Column('ID', int, nullable=False, primary_key=True, auto_increment=True),
                          Column('USER_ID', int, nullable=False),
                          Column('USER_NAME', str, nullable=False),
                          Column('EMOTE', str, nullable=False),
                          Column('CHANCE', float, nullable=False, default=0),
                          Column('SERVER_ID', int),
                          Column('COOLDOWN', int, nullable=False, default=0),
                          Column('ENABLED', bool, nullable=False, default=True)
                          ],
                         Reaction
                         )


class Reaction(EntityItem):
    def __init__(self, *args, **kwargs):
        self.ID = None
        self.USER_ID = None
        self.USER_NAME = None
        self.EMOTE = None
        self.CHANCE = None
        self.SERVER_ID = None
        self.COOLDOWN = None
        self.ENABLED = None

        self.last_used = datetime.datetime.min

        super().__init__(*args, **kwargs)
        pass

    def get_emote(self):
        return self.EMOTE.replace('<', '').replace('>', '')

