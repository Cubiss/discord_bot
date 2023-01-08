import sqlite3
from classes.entity import Entity, EntityItem, Column
from .selectedCharacters import SelectedCharacters


class Character(EntityItem):
    def __init__(self, *args, **kwargs):
        self.CHARACTER_ID = None
        self.ROLE = None
        self.MAX_HP = 0
        self.HP = 0
        self.ARMOR = 0
        self.MAX_ARMOR = 0

        super().__init__(*args, **kwargs)


class Characters(Entity):
    def __init__(self, db: sqlite3.Connection):
        super().__init__(db,
                         "Characters",
                         [Column('CHARACTER_ID', str, nullable=False, primary_key=True),
                          Column('ROLE', int),
                          Column('HP', float, 0),
                          Column('MAX_HP', float, 0),
                          Column('ARMOR', float, 0),
                          Column('MAX_ARMOR', float, 0),
                          ],
                         Character
                         )

    def load(self, selector: str = None, selector_params: list = None):
        super(Characters, self).load(selector, selector_params)

        chars = ['DW', 'EL', 'HE', 'GN', 'HU']

        for c in self:
            if c.CHARACTER_ID in chars:
                chars.remove(c.CHARACTER_ID)
            else:
                raise Exception(f'Unknown charactrer_id: "{c.CHARACTER_ID}"')

        for cid in chars:
            self.create(CHARACTER_ID=cid)
