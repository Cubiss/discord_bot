import sqlite3
from collections import OrderedDict

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

        self.column_dict = {}

        self.primary_key_dict = OrderedDict()

        for c in columns:
            c: Column
            self.column_dict[c.name] = c
            if c.primary_key:
                self.primary_key_dict[c.name] = c

        if entity_item_type is not None and not issubclass(entity_item_type, EntityItem):
            raise Exception(f"{entity_item_type} is not subclass of {EntityItem}")

        self.entity_item_type = entity_item_type or type(f'{self.name}_auto_generated_item', (EntityItem,), {})
        self._items = {}

        self.loaded = False

        if not self.table_exists():
            self.create_table()

    def create(self, _reload=True, **values):
        new_item = self.entity_item_type(db=self.db, entity=self, db_values=values)
        new_item.save(reload=_reload)
        if not _reload:
            self[new_item.primary_key] = new_item
        return new_item

    def delete(self, primary_key):
        if primary_key in self:
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

            self.loaded = True
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

    def __getitem__(self, item_id):
        if item_id in self._items:
            return self._items[item_id]
        else:
            return None

    def __setitem__(self, item_id, item):
        if item_id in self._items and self._items[item_id] != item:
            raise KeyError(f"{self.entity_item_type.__name__} item '{item_id}' already exists!")
        else:
            self._items[item_id] = item

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        yield from self._items.values()

    def __contains__(self, item):
        return item in self._items

    def values(self):
        return self._items.values()

    def get_primary_key_column_names(self):
        return tuple(self.primary_key_dict.keys())

    def __repr__(self):
        return f'Entity<{self.name}[{len(self)}]>'


class Column:
    def __init__(self, name, data_type, default=None, nullable=True, primary_key=False, auto_increment=False):
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

    def convert(self, value):
        return None if value is None else self.type(value)
