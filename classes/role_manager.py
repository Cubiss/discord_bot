# import sqlite3
#
# class RoleManager:
#     def __init__(self, db: sqlite3.Connection):
#         self.db = db
#
#         if not self.table_exists():
#             self.create_table()
#
#         self._users = {}
#         self.load()
#         pass
#
#     def load(self):
#         c = self.db.cursor()
#         c.execute('select '
#                   ' USER_ID, '
#                   ' USER_NAME '
#                   'from '
#                   ' Users')
#         c.row_factory = sqlite3.Row
#
#         for row in c.fetchall():
#             user_id = int(row['USER_ID'])
#             self[user_id] = User(
#                 user_id=user_id,
#                 user_name=str(row['USER_NAME']),
#                 db=self.db
#             )
#
#         c = self.db.cursor()
#         c.execute('select '
#                   ' USER_ID, '
#                   ' PERMISSION_ID '
#                   'from '
#                   ' Permissions')
#         c.row_factory = sqlite3.Row
#
#         for row in c.fetchall():
#             u = self[int(row['USER_ID'])]
#             if u is not None:
#                 u.permissions.append(row['PERMISSION_ID'])
#
#     def table_exists(self):
#         c = self.db.cursor()
#         c.execute(
#             "SELECT name FROM sqlite_master "
#             "WHERE type='table' and name = 'RoleManagementMessages'"
#             "ORDER BY name ;"
#         )
#
#         return len(c.fetchall()) > 0
#
#     def create_table(self):
#         c: sqlite3.Cursor = self.db.cursor()
#         c.execute(
#             '''CREATE TABLE "RoleManagementMessages" (
#                 "messageID"	INTEGER NOT NULL,
#                 PRIMARY KEY("messageID")
#             );'''
#         )
#         self.db.commit()
#
#     def manage_reaction_add(self, reaction):
#         pass

