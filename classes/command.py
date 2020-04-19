import re

from classes.users import User, Users
import discord


class Command:
    def __init__(
            self,
            names: list,
            regexp: str,
            command: callable,
            usage=None,
            description='',
            cmd_char='!',
            access_level=1):
        """
        Creates a command.
        :param names: Aliases of the command. First name is
        :param regexp: regex representation of messages that can be processed with this command
        :param command: coroutine(message: discord.Message, db: sqlite3.Connection, **kwargs) -> bool:
                        message is message object that command will react to,
                        db is connection to a database
                        kwargs are arguments parsed from regexp groups
        :param usage: String showing how the command should be called.
        :param description: String saying what command should do.
        :param cmd_char: String every command will start with.
        """
        self.db = None
        self.cmd_char = cmd_char
        self.names = names
        self.command = command
        self.re_list = [re.compile(regexp.replace('__name__', cmd_char + name)) for name in names]
        self.usage = usage or f'Command is in wrong format: {self.re_list[0].pattern}'
        self.description = description
        self.access_level = access_level

    def can_run(self, message: discord.Message):
        for name in self.names:
            if message.content.lower().startswith(self.cmd_char + name):
                if len(message.content.lower()) > len(self.cmd_char + name):
                    if not message.content.lower()[len(self.cmd_char + name)].isspace():
                        continue
                return True
        else:
            return False

    def run(self, message: discord.Message, client: discord.Client, users: Users):
        # check access
        if self.access_level > 1:
            u: User
            for user in [u for u in users.user_list if u.id == message.author.id]:
                if user.access_level.level >= self.access_level:
                    # user has appropriate access level
                    break
            else:
                # user cannot use this command
                return message.channel.send(self.format_message(message=message, string="__author__ you can't do that!"))

        # get regex parsed arguments
        for regex in self.re_list:
            match = regex.match(message.content)
            if match is not None:
                break
        else:
            # no regex match found, return a usage message
            return message.channel.send(self.format_message(message=message, string=self.usage))

        # finally run the command code
        return self.command(message, self.db, client, **match.groupdict())

    def format_message(self, string: str, message: discord.Message):
        string = string.replace('__name__', self.names[0])
        string = string.replace('__author__', f'<@{message.author.id}>')
        return string
