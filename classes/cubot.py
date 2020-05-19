import discord
import datetime
import sqlite3
import os
import traceback

from c__lib.c__input import yes_no_input

from classes.reactor import Reactor
from classes.users import Users
from classes.command import Command


class Cubot(discord.Client):
    commands = list()

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
        elif database is str or database is None:
            if database is None:
                database = './cubot.db'
            if os.path.isfile(database):
                self.database = sqlite3.connect(database)
            elif yes_no_input('Database file not found. Should I create and initialize a new one? [y/n]'):
                self.database = sqlite3.connect(database)
                # self.init_database(self.database)
            else:
                raise Exception('Database file not found.')

        self.log_commands = log_commands
        self.log_function = log_function
        
        self.reactor = Reactor(self.database)

        self.user_list = Users(self.database)

        super(Cubot, self).__init__(*args, **kwargs)

    def addcom(self, command):
        command.db = self.database
        self.commands.append(command)

    async def on_ready(self):
        self.log_function(datetime.datetime.now())
        self.log_function('Logged in as')
        self.log_function(self.user.name)
        self.log_function(self.user.id)
        self.log_function('------')

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.content.startswith('!help'):
            return await self.help(message)

        for e in self.reactor.get_reactions(message.author.id, message.guild.id):
            await message.add_reaction(emoji=e)
            self.log_function(f"Adding reaction to {message.author.name}: {e}")

        command: Command
        for command in self.commands:
            if command.can_run(message):
                try:
                    await command.run(message, self, self.user_list)
                    if self.log_commands:
                        self.log_function(f'[{datetime.datetime.now()}][{message.guild.name}]{message.author}: {message.content}')
                except Exception as ex:
                    self.log_function(message.author)
                    self.log_function(message.content)
                    raise

    async def help(self, message: discord.Message):
        help_str = '```'
        help_str += 'Available commands:\n'

        max_command_len = max([len(c.names[0]) for c in self.commands])

        for command in self.commands:
            help_str += f'{command.names[0]:{max_command_len}}: {command.description}\n'

        help_str += '```'

        self.log_function(help_str)
        await message.channel.send(help_str)
