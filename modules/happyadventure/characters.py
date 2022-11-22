import sqlite3
from classes.entity import Entity, EntityItem, Column
from .selectedCharacters import SelectedCharacters


class Character(EntityItem):
    def __init__(self, *args, **kwargs):
        self.CHARACTER_ID = None
        self.USER_ID = None
        self.NAME = None
        self.DESCRIPTION = None
        self.MAX_HP = 0
        self.HP = 0
        self.ARMOR = 0

        super().__init__(*args, **kwargs)

    def info_page(self) -> str:
        return \
            f"""```
**{self.NAME}**
__________________________
{self.DESCRIPTION}
__________________________
HP:    {self.HP}/{self.MAX_HP}
ARMOR: {self.ARMOR}
```
"""

    def is_active(self):
        c = self.db.cursor()
        c.execute('select count() from SelectedCharacters where CHARACTER_ID = ?', [self.CHARACTER_ID])
        return int(c.fetchone()[0]) > 0


class Characters(Entity):
    def __init__(self, db: sqlite3.Connection):
        super().__init__(db,
                         "Characters",
                         [Column('CHARACTER_ID', int, nullable=False, primary_key=True, auto_increment=True),
                          Column('USER_ID', int, nullable=False),
                          Column('SERVER_ID', int, nullable=False),
                          Column('NAME', str, ''),
                          Column('DESCRIPTION', str, ''),
                          Column('MAX_HP', float, 0),
                          Column('ARMOR', float, 0),
                          Column('HP', float, 0)
                          ],
                         Character
                         )
        self.selected_characters = SelectedCharacters(self.db)
        self.selected_characters.load()

    def search(self, query: str = None, character_id: int = None, server_id: int = None, name: str = None,
               description: str = None, user_id: int = None) -> list:
        if character_id is not None:
            if character_id in self:
                c = self[character_id]
                if server_id is not None and c.SERVER_ID != server_id:
                    return []
                if user_id is not None and c.USER_ID != user_id:
                    return []
                return [c]
            else:
                return []

        found = []

        for c in self:
            if server_id is not None and c.SERVER_ID != server_id:
                continue

            if user_id is not None and c.USER_ID != user_id:
                continue

            if name is not None and name.lower().strip() not in c.NAME.lower():
                continue

            if description is not None and description.lower().strip() not in c.DESCRIPTION.lower():
                continue

            if query is not None and query != ''\
                    and query.lower().strip() not in c.NAME.lower() \
                    and query.lower() not in c.DESCRIPTION.lower() \
                    and (query.isnumeric() and int(query) != c.CHARACTER_ID):
                continue

            found.append(c)

        return found

    def select(self, character_id: int, user_id: int, server_id: int):
        user_characters = [c.CHARACTER_ID for c in self if c.USER_ID == user_id]

        if character_id not in user_characters:
            raise Exception(f'{character_id} does not belong to user {user_id}')

        self.selected_characters.select(character_id=character_id, user_id=user_id, server_id=server_id)
        return self[character_id]

    def get_selected(self, user_id: int, server_id: int):
        if (user_id, server_id) in self.selected_characters:
            return self[self.selected_characters[(user_id, server_id)].CHARACTER_ID]
        else:
            return None

