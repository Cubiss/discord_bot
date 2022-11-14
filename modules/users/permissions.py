import sqlite3
import discord
from classes.entity import Entity, Column, EntityItem


class Permissions(Entity):
    def __init__(self, db: sqlite3.Connection):
        super().__init__(db, "Permissions", [
                         Column("USER_ID", int, nullable=False, primary_key=True),
                         Column("PERMISSION_ID", str, nullable=False, primary_key=True)]
                         )

    def has_permission(self, user, permission):
        return (user, permission) in self


class Permission(EntityItem):
    def __init__(self, *args, **kwargs):
        self.USER_ID = None
        self.PERMISSION_ID = None

        super(Permission, self).__init__(*args, **kwargs)

    pass
