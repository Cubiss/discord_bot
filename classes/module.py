import discord

from classes.command import Command
from classes.logger import Logger


class Module:
    def __init__(self, name: str, client=None, log: Logger = None):
        from classes.cubot import Cubot
        self.name = name
        self.client: Cubot = client

        self.commands = []
        if log is None:
            self.log = Logger(file=None, use_stdout=True, log_file_writes=False, add_timestamps=True)
        self.on_message_hook_priority = 0

    def addcom(self, command: Command):
        self.commands.append(command)

    async def on_message(self, message: discord.Message):
        pass
