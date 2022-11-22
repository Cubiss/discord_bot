# from classes.module import *
# from classes.service import Service
# from modules.users.users import User
#
#
# class MinecraftModule(Module):
#     def __init__(self, **kwargs):
#         super().__init__("minecraft", **kwargs)
#
#         # self.addcom(
#         #     Command(names=['minecraft'], regexp=r'^__name__\s*(?P<cmd>\S*)$', function=self.minecraft,
#         #             usage=f'__author__ Usage: !minecraft', description='Displays minecraft server\'s address.')
#         # )
#
#     async def minecraft(self, message: discord.Message, user: User, cmd=None, **__) -> bool:
#         cmd = (cmd or '').lower()
#
#         if cmd not in ['', 'ip', 'status', 'start', 'stop', 'restart']:
#             await message.channel.send(f"Invalid command: {cmd}")
#             return True
#
#         s = Service('minecraft.service', use_dbus=False)
#         status_string = s.status_string()
#
#         if cmd in ['', 'ip']:
#             running = True
#             status = ''
#             address = 'cubiss.cz'
#             from subprocess import CalledProcessError
#             try:
#                 running = s.is_running()
#                 status = s.status_string()
#             except CalledProcessError:
#                 pass
#
#             if running:
#                 await message.channel.send(f'Minecraft server is running on {address}:\n{status})')
#             else:
#                 await message.channel.send(f'Minecraft server is not running. Use "!minecraft start" to start it.\n'
#                                            f'It will run on {address}.')
#             return True
#
#         elif cmd == 'status':
#             await message.channel.send('Minecraft status:\n' + status_string)
#             return True
#
#         if user is not None and user.has_permission('minecraft'):
#             if cmd == 'start':
#                 if s.is_running():
#                     await message.channel.send('Minecraft is already running:\n' + status_string)
#                 else:
#                     try:
#                         s.start()
#                     except Exception as ex:
#                         await message.channel.send(f'Failed to start the server: {ex}')
#                         return False
#                     await message.channel.send('Minecraft status:\n' + s.status_string())
#                 return True
#
#             elif cmd == 'stop':
#                 if s.is_running():
#                     try:
#                         s.stop()
#                     except Exception as ex:
#                         await message.channel.send(f'Failed to start the server: {ex}')
#                         return False
#                     await message.channel.send('Stopping minecraft server:\n' + s.status_string())
#                 else:
#                     await message.channel.send('Minecraft server is not running:\n' + status_string)
#                 return True
#
#             elif cmd == 'restart':
#                 try:
#                     s.stop()
#                 except Exception as ex:
#                     await message.channel.send(f'Failed to start the server: {ex}')
#                     return False
#                 await message.channel.send('Restarting minecraft server:\n' + s.status_string())
#                 return True
#         else:
#             await message.channel.send(f"You don't have permission for following command: {cmd}")
#             return True
