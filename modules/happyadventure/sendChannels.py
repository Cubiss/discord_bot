import sqlite3
from classes.entity import Entity, EntityItem, Column


class SendChannel(EntityItem):
    def __init__(self, *args, **kwargs):
        self.SENDCHANNEL_ID = None
        self.SOURCE_CHANNEL = None
        self.TARGET_CHANNEL = None

        super().__init__(*args, **kwargs)


class SendChannels(Entity):
    def __init__(self, db: sqlite3.Connection):
        super().__init__(db,
                         "SendChannel",
                         [Column('SENDCHANNEL_ID', int, nullable=False, primary_key=True, auto_increment=True),
                          Column('SOURCE_CHANNEL', int, nullable=False),
                          Column('TARGET_CHANNEL', int)
                          ],
                         SendChannel
                         )


