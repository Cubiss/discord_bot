import sqlite3
from classes.entity import Entity, EntityItem, Column


class SelectedCharacters(Entity):
    def __init__(self, db: sqlite3.Connection):
        super().__init__(db,
                         "SelectedCharacters",
                         [Column('USER_ID', int, nullable=False, primary_key=True),
                          Column('SERVER_ID', int, nullable=False, primary_key=True),
                          Column('CHARACTER_ID', int, nullable=False)
                          ],
                         SelectedCharacter
                         )

    def select(self, user_id, server_id, character_id):

        if (user_id, server_id) in self._items:
            sc = self[(user_id, server_id)]
            sc.CHARACTER_ID = character_id
            sc.save()
        else:
            self.create(
                USER_ID=user_id,
                SERVER_ID=server_id,
                CHARACTER_ID=character_id
            )


class SelectedCharacter(EntityItem):
    def __init__(self, *args, **kwargs):
        self.USER_ID = None
        self.SERVER_ID = None
        self.CHARACTER_ID = None

        super().__init__(*args, **kwargs)
