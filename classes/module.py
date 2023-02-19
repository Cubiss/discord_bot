import discord
import sqlite3

from classes.command import Command
from classes.commandTree import CommandTree
from classes.logger import Logger


class Module:
    name = '__uninitialized__'

    def __init__(self, name: str, client=None, log: Logger = None):
        from classes.cubot import Cubot
        self.name = name
        self.client: Cubot = client
        self.db = None
        if client is not None:
            self.db = client.database

        self.commands = []

        self.log = log or Logger(files=None, use_stdout=True, log_file_writes=False, add_timestamps=True)
        self.on_message_hook_priority = 0

    def addcom(self, command: Command):
        self.commands.append(command)

    async def on_message(self, message: discord.Message):
        pass

    def __repr__(self):
        return f"<Module({self.name})>"

    async def send_help(self, message: discord.Message):
        help_str = '```'
        help_str += f'Available commands in \'{self.name}\' module:\n'

        max_command_len = max([len(c.name) for c in self.commands])

        for command in self.commands:
            command: Command
            if command.help_scope_in(Command.help_scope_module):
                help_str += f'{command.name:{max_command_len}}: {command.description}\n'

        help_str += '```'

        self.log(help_str)
        return await message.channel.send(help_str)
