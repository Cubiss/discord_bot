import asyncio

import discord
import datetime
import sqlite3
import os
import re

from c__lib import yes_no_input

from modules.users.users import Users
from classes.command import Command
from classes.module import Module


class Cubot(discord.Client):
    commands = []
    modules = []

    def __init__(self,
                 database=None,
                 log_commands=False,
                 log_function=print,
                 command_character='!',
                 *args, **kwargs):
        """
        Inits discord.Client and Cubot
        :param database: Either path to file or
        :param log_commands:
        :param currency_gain_interval:
        :param currency_gain_increment:
        :param args: passed to discord.py constructor
        :param kwargs: passed to discord.py constructor
        """

        self.command_character = command_character

        self.database = self._db_init(database)

        self.log_commands = log_commands
        self.log = log_function

        self.user_list = Users(self.database)
        self.user_list.load()

        intents = discord.Intents.default()
        intents.members = True
        kwargs['intents'] = intents

        self.running = True
        super(Cubot, self).__init__(*args, **kwargs)

    @staticmethod
    def _db_init(database):
        try:
            if database is sqlite3.Connection:
                return database
            elif type(database) == str or database is None:
                if database is None:
                    database = 'cubot.db'
                if os.path.isfile(database):
                    return sqlite3.connect(database)
                elif yes_no_input('Database file not found. Should I create and initialize a new one? [y/n]'):
                    return sqlite3.connect(database)
                else:
                    raise Exception('Database file not found.')
        except Exception as ex:
            raise Exception(f"Failed to initialize database: ({type(database)}){database}\n{ex}")

    def addcom(self, command: Command):
        names = []
        for n in [cmd.names for cmd in self.commands]:
            for name in n:
                names.append(name)

        for n in command.names:
            if n in names:
                raise Exception(f"Duplicate command name: {n}")
            # for name in names:
            #     if name.startswith(n) or n.startswith(name):
            #         raise Exception(f"Incompatible command names: {n} - {name}")

        command.db = self.database
        self.commands.append(command)

    async def on_ready(self):
        self.log(datetime.datetime.now())
        self.log('Logged in as')
        self.log(self.user.name)
        self.log(self.user.id)
        self.log('------')

    async def on_message(self, message: discord.Message):
        # ignore bot's messages
        if message.author == self.user:
            return

        # handle all modules
        for m in sorted(self.modules, key=lambda module: module.on_message_hook_priority):
            m: Module
            if await m.on_message(message):
                break

        # check for command char
        if not message.content.startswith(self.command_character):
            return

        text = message.content[len(self.command_character):]

        command: Command
        for command in self.commands:
            if command.is_match(text):
                try:
                    if self.log_commands:
                        self.log(f'[{message.guild.name}]'
                                 f'{message.author}: '
                                 f'{message.content}'
                                 ' -> '
                                 f'Command: {command.name}, Timeout: {command.timeout}'
                                 )

                    await asyncio.wait_for(
                        command.execute(message=message,text=text, client=self, users=self.user_list, log=self.log),
                        command.timeout
                    )

                except asyncio.TimeoutError:
                    if self.log_commands:
                        self.log(f'{command.name} timed out.')
                    await message.reply(command.format_message(
                        f"__author__ Sorry, I don't have enough time for this.", message))
                except Exception as ex:
                    self.log(message.author)
                    self.log(message.content)
                    self.log(ex)
                    raise

    def load_modules(self, modules):
        for cls in modules:
            module: Module = Module('<Failed to load.>')
            try:
                module = cls(client=self, log=self.log)

                self.add_module(module)

                self.log(f'Loaded module {module.name}')
            except Exception as ex:
                self.log(f'Error loading module {cls}: {ex}')

    def add_module(self, module: Module):
        if any(module.name == m.name for m in self.modules):
            raise Exception(f"Module named '{module.name}' has alredy been added")

        self.modules.append(module)

        for command in module.commands:
            self.addcom(command)

    async def start(self, *args, **kwargs):
        self.running = True
        await super().start(*args, **kwargs)

    def stop(self):
        self.running = False
        pass
