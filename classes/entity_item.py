import sqlite3


class EntityItem:
    def __init__(self, db: sqlite3.Connection, entity, db_values: dict = None, new=True):
        try:
            self.db = db
            self.loaded = False
            if not hasattr(entity, "is_entity") or not entity.is_entity:
                raise Exception(f"{entity} is not an entity")
            self.entity = entity
            self.new = new
            self.initialize(db_values)

            pass
        except Exception as ex:
            raise Exception(f"Error creating EntityItem: {ex}")

    def initialize(self, values):
        pks = self.get_primary_key_columns()

        for column in self.entity.columns:
            if column.name in values:
                value = values[column.name]
            else:
                value = column.default

            if column.name in pks:
                storage_name = "_" + column.name
                setattr(self, storage_name, column.type(value))

                # noinspection PyShadowingNames
                def getter(self):
                    return getattr(self, storage_name)

                # noinspection PyShadowingNames
                def setter(self, value):
                    setattr(self, storage_name, column.type(value))
                    self._update_primary_key()

                # noinspection PyShadowingNames
                def deleter(self):
                    delattr(self, storage_name)

                setattr(type(self), column.name, property(getter, setter, deleter, f"{self.entity.name}.{column.name} property."))
            else:
                setattr(self, column.name, column.type(value))

        self._update_primary_key()
        self.loaded = True

    def load(self):
        selector = ""

        for c in self.get_primary_key_columns():
            selector += f' {c} = ?'

        cursor: sqlite3.Cursor
        cursor = self.db.cursor()
        cursor.row_factory = sqlite3.Row

        cursor.execute(f"SELECT count() as cnt FROM {self.entity.name} WHERE {selector}", self.primary_key)
        row = cursor.fetchone()

        if int(row['cnt']) != 1:
            raise Exception(f"Loading item from {self.entity.name} based on pk {self.primary_key}:"
                            f" Found {int(row['cnt'])} items, expected 1.")

        sql = f"SELECT {', '.join(c.name for c in self.entity.columns)} FROM {self.entity.name} WHERE {selector}"
        cursor.execute(sql, self.primary_key)


        row = cursor.fetchone()
        values = {}
        key = ()
        for column in self.entity.columns:
            values[column.name] = row[column.name]
            if column.primary_key:
                key += values[column.name]

        self.initialize(values)

        if len(key) == 1:
            key = key[0]

        self.entity[key] = self

    def save(self, reload=True):
        insert_column_names = [c.name for c in self.entity.columns if
                               getattr(self, c.name) is not None or not c.auto_increment]
        update_column_names = [c.name for c in self.entity.columns if not c.primary_key]
        pk_column_names = [c.name for c in self.entity.columns if c.primary_key]

        sql = f"INSERT INTO {self.entity.name} ("
        sql += ", ".join(insert_column_names)
        sql += ") VALUES ( "
        sql += ", ".join(["?"] * len(insert_column_names))
        sql += ") ON CONFLICT ("
        sql += ", ".join(pk_column_names)
        sql += ") DO UPDATE SET "
        sql += ", ".join(f"{name} = ?" for name in update_column_names)

        insert_values = [getattr(self, name) for name in insert_column_names]
        update_values = [getattr(self, name) for name in update_column_names]

        cursor: sqlite3.Cursor
        cursor = self.db.cursor()
        cursor.execute(sql, insert_values + update_values)
        self.db.commit()

        if reload:
            self.load()

    def delete(self):
        sql = f"DELETE FROM {self.entity.name} WHERE "
        sql += "AND ".join(f"{c.name} = ?" for c in self.entity.columns if c.primary_key)

        c = self.db.cursor()
        c.execute(sql, [getattr(self, c.name) for c in self.entity.columns if c.primary_key])
        self.db.commit()

    def get_primary_key_columns(self):
        return self.entity.get_primary_key_columns()

    def _update_primary_key(self, pks=None):
        if pks is None:
            pkc = self.get_primary_key_columns()
            pks = ()

            for pk in pkc:
                pks += (pk, )

        self._primary_key = pks

    @property
    def primary_key(self):
        return self._primary_key
