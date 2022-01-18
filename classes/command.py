import re
import inspect
import discord

from classes.users import Users


class Command:
    # arguments passed to command function
    # message: discord.Message to which the command is reacting
    # db: database assigned to the bot
    # client: reference to Cubot
    command_parameters = ['message', 'db', 'client', 'user']

    def __init__(
            self,
            names: list,
            regexp: str,
            function: callable,
            usage=None,
            description='',
            cmd_char='!',
            permissions: list = None):
        """
        Creates a command.
        :param names: Aliases of the command. First name is
        :param regexp: regex representation of messages that can be processed with this command
        :param function: coroutine(**kwargs) -> bool:
                        kwargs: arguments parsed from regexp groups + Command.command_parameters
        :param usage: String showing how the command should be called.
        :param description: String saying what command should do.
        :param cmd_char: String every command will start with.
        """
        self.db = None
        self.cmd_char = cmd_char
        self.names = names

        self.command = function

        self.re_list = [re.compile(regexp.replace('__name__', cmd_char + name), ) for name in names]

        # check if regex contains invalid groups
        for r in self.re_list:
            for group_name in r.groupindex:
                if group_name in Command.command_parameters:
                    raise Exception(f"Wrong command regexp: group name '{group_name}' is reserved.")

        self.usage = usage or f'Command is in wrong format: {self.re_list[0].pattern}'
        self.description = description
        if permissions is None:
            permissions = []
        if type(permissions) == str:
            permissions = [permissions]
        self.permissions = permissions

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
        if self.permissions is not None and len(self.permissions) > 0:
            u = users[message.author.id]
            if u is not None and \
               ('admin' in u.permissions or any(p in u.permissions for p in self.permissions)):
                # user has an appropriate permission
                pass
            else:
                # user cannot use this command
                return message.channel.send(
                    self.format_message(
                        message=message, string="__author__ you can't do that!"))

        # get regex parsed arguments
        for regex in self.re_list:
            match = regex.match(message.content)
            if match is not None:
                break
        else:
            # no regex match found, return a usage message
            return message.channel.send(self.format_message(message=message, string=self.usage))

        # parse arguments for the command function

        params = {
            'message': message,
            'db': self.db,
            'client': client,
            'user': users[message.author.id]
        }

        params.update(match.groupdict())

        # finally run the command code
        return self.command(**params)

    def format_message(self, string: str, message: discord.Message):
        string = string.replace('__name__', self.names[0])
        string = string.replace('__author__', f'<@{message.author.id}>')
        return string

    def __repr__(self):
        if self.names is None or len(self.names) == 0:
            return f'<Command() - uninitialized'
        else:
            return f'<Command({self.names[0]}) -> {repr(self.command)}>'
