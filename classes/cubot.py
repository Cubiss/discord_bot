import asyncio

import discord
import datetime
import sqlite3
import os

from c__lib import yes_no_input

from classes.reactor import Reactor
from classes.users import Users
from classes.command import Command
from classes.module import Module


class Cubot(discord.Client):
    commands = []
    modules = []

    def __init__(self,
                 database=None,
                 log_commands=False,
                 log_function=print,
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
        if database is sqlite3.Connection:
            self.database = database
        elif type(database) == str or database is None:
            if database is None:
                database = 'cubot.db'
            if os.path.isfile(database):
                self.database = sqlite3.connect(database)
            elif yes_no_input('Database file not found. Should I create and initialize a new one? [y/n]'):
                self.database = sqlite3.connect(database)
            else:
                raise Exception('Database file not found.')

        self.log_commands = log_commands
        self.log = log_function
        
        self.reactor = Reactor(self.database, log_function)

        self.user_list = Users(self.database)

        intents = discord.Intents.default()
        intents.members = True
        kwargs['intents'] = intents

        self.running = True
        super(Cubot, self).__init__(*args, **kwargs)

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
        if message.author == self.user:
            return

        if message.content.startswith('!help'):
            return await self.help(message)

        for e in self.reactor.get_reactions(message.author.id, message.guild.id):
            await message.add_reaction(emoji=e)
            self.log(f"Adding reaction to {message.author.name}: {e}")

        command: Command
        for command in self.commands:
            if command.can_run(message):
                try:
                    await asyncio.wait_for(
                        command.run(message, self, self.user_list),
                        command.timeout
                    )
                    if self.log_commands:
                        self.log(f'[{datetime.datetime.now()}]'
                                          f'[{message.guild.name}]'
                                          f'{message.author}: '
                                          f'{message.content}')
                except asyncio.TimeoutError:
                    await message.reply(command.format_message(
                        f"__author__ Sorry, I don't have enough time for this.", message))
                except Exception as ex:
                    self.log(message.author)
                    self.log(message.content)
                    self.log(ex)
                    raise

    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return
        pass

    async def help(self, message: discord.Message):
        help_str = '```'
        help_str += 'Available commands:\n'

        max_command_len = max([len(c.names[0]) for c in self.commands])

        for command in self.commands:
            help_str += f'{command.names[0]:{max_command_len}}: {command.description}\n'

        help_str += '```'

        self.log(help_str)
        await message.channel.send(help_str)

        pass

    def load_modules(self, modules):
        for cls in modules:
            module: Module = Module('<Failed to load.>')
            try:
                module = cls(client=self, log=self.log)

                self.add_module(module)

                self.log(f'Loaded module {module.name}')
            except Exception as ex:
                self.log(f'Error loading module {module}: {ex}')

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

