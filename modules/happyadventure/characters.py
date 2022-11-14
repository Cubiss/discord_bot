import sqlite3
from classes.entity import Entity, EntityItem, Column


class Characters(Entity):
    def __init__(self, db: sqlite3.Connection):
        super().__init__(db,
                         "Characters",
                         [Column('CHARACTER_ID', int, nullable=False, primary_key=True, auto_increment=True),
                          Column('USER_ID', int, nullable=False),
                          Column('NAME', str),
                          Column('DESCRIPTION', str),
                          Column('HP', int),
                          Column('ARMOR', int)
                          ],
                         Character
                         )


class Character(EntityItem):
    def __init__(self, *args, **kwargs):
        self.CHARACTER_ID = None
        self.USER_ID = None
        self.NAME = None
        self.DESCRIPTION = None
        self.HP = None
        self.ARMOR = None

        super().__init__(*args, **kwargs)
