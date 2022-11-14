import sqlite3
from .entity_item import EntityItem
import datetime

_db_type_mapping = {
    int: "INTEGER",
    str: "TEXT",
    datetime.datetime: "TEXT",
    float: "REAL",
    bool: "INTEGER"
}


class Entity:
    is_entity = True

    def __init__(self, db: sqlite3.Connection, name: str, columns: list, entity_item_type=None):

        self.db = db
        self.name = name
        self.columns = columns

        if entity_item_type is not None and not issubclass(entity_item_type, EntityItem):
            raise Exception(f"{entity_item_type} is not subclass of {EntityItem}")

        self.entity_item_type = entity_item_type or EntityItem
        self._items = {}

        self.loaded = False

        if not self.table_exists():
            self.create_table()

    def create(self, **values):
        new_item = self.entity_item_type(db=self.db, entity=self, db_values=values)
        new_item.save()
        self[new_item.primary_key] = new_item
        return new_item

    def delete(self, primary_key):
        if primary_key in self._items:
            item: EntityItem
            item = self._items.pop(primary_key)
            item.delete()
            return item
        else:
            raise Exception(f"Item {primary_key} doesn't exist.")

    def load(self, selector: str = None, selector_params: list = None):
        try:
            if self.loaded:
                raise Exception("Table already loaded")

            sql = f"SELECT {', '.join(c.name for c in self.columns)} FROM {self.name}"

            if selector is not None:
                sql += f" WHERE {selector}"

            selector_params = selector_params or []

            c = self.db.cursor()
            c.execute(sql, selector_params)
            c.row_factory = sqlite3.Row

            for row in c.fetchall():
                values = {}
                key = ()
                for column in self.columns:
                    values[column.name] = row[column.name]
                    if column.primary_key:
                        key += (values[column.name], )

                item = self.entity_item_type(db=self.db, entity=self, db_values=values)

                if len(key) == 1:
                    key = key[0]

                self[key] = item
        except Exception as ex:
            raise Exception(f"Error loading entity: {ex}")

    def save(self):
        for i in self:
            self[i].save()

    def table_exists(self):
        c = self.db.cursor()
        c.execute(
            "SELECT name FROM sqlite_master "
            f"WHERE type='table' and name = '{self.name}'"
            "ORDER BY name ;"
        )

        return len(c.fetchall()) > 0

    def create_table(self):
        # raise NotImplementedError(f"create_table for '{self.name}' not implemented")

        sql = f'CREATE TABLE "{self.name}" ( '
        primary_keys = []
        for column in self.columns:
            sql += f' "{column.name}" {_db_type_mapping[column.type]} {"" if column.nullable else "NOT NULL"}, '
            if column.primary_key:
                primary_keys.append(f'"{column.name}"')

        sql += f'PRIMARY KEY({", ".join(primary_keys)})'
        sql += ');'

        c: sqlite3.Cursor = self.db.cursor()
        c.execute(sql)
        self.db.commit()

    def __getitem__(self, item_id: int):
        if item_id in self._items:
            return self._items[item_id]
        else:
            return None

    def __setitem__(self, user_id: int, item):
        if user_id in self._items:
            raise KeyError("User already exists!")
        else:
            self._items[user_id] = item

    def __iter__(self):
        yield from self._items.values()

    def get_primary_key_columns(self):
        primary_keys = ()
        for col in self.columns:
            if col.primary_key:
                primary_keys = primary_keys + (col.name, )

        return primary_keys


class Column:
    def __init__(self, name, data_type, nullable=True, primary_key=False, auto_increment=False, default=None):
        self.name = name
        if data_type not in _db_type_mapping.keys():
            raise Exception(f"Type {data_type} not one of the following: {', '.join(str(t) for t in _db_type_mapping)}")
        self.type = data_type
        self.nullable = nullable
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.default = default

    def __repr__(self):
        return f"<Column {'[pk]' if self.primary_key else ''}{self.name}>"

