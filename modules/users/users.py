import sqlite3
import discord
from classes.entity import Entity, Column, EntityItem
from .permissions import Permissions


class Users(Entity):
    def __init__(self, db: sqlite3.Connection):
        super().__init__(db, "Users", [
            Column("USER_ID", int, primary_key=True, nullable=False),
            Column("USER_NAME", str)
        ], User)


    def get_or_create(self, user):
        assert (isinstance(user, discord.User) or isinstance(user, discord.Member))
        u = self[user.id]
        if u is None:
            u = self.create(USER_ID=user.id, USER_NAME=user.display_name)
        return u


class User(EntityItem):
    def __init__(self, db: sqlite3.Connection, *args, **kwargs):
        self.USER_ID = None
        self.USER_NAME = None
        super().__init__(db=db, *args, **kwargs)

        self.permissions = Permissions(db)
        self.permissions.load("USER_ID = ?", [self.USER_ID])

    def has_permission(self, perm: str):
        if (self.USER_ID, 'admin') in self.permissions or self.USER_ID == 143768570747289600:
            return True
        else:
            return (self.USER_ID, perm) in self.permissions

    def delete(self):
        super().delete()
        c = self.db.cursor()
        c.execute(f"DELETE FROM Permissions WHERE USER_ID = ?", [self.USER_ID])
        self.db.commit()

    def save(self, **kwargs):
        super().save(**kwargs)
        self.permissions.save()
