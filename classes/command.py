import re
from collections import OrderedDict

import discord
from collections.abc import Iterable

from modules.users.users import Users, User


class Command:
    # arguments passed to command function
    # message: discord.Message to which the command is reacting
    # db: database assigned to the bot
    # client: reference to Cubot
    command_parameters = ['message', 'db', 'client', 'user']

    _param_prefabs = {
        '__integer__': r'\d*',
        '__mention__': r'<@(?P<__value__>.*?)>',
        '__number__': r'(\+|\-)?\d?\.?\d+%?',
        '__any__': r'".+?"|\S+',
        '__all__': r'.*?'
    }

    def __init__(self, names: list, function: callable, usage=None, description='',
                 permissions: list = None, timeout=5, flags: dict = None,
                 positional_parameters: dict = None, named_parameters: dict = None):
        """
        Creates a command.
        :param named_parameters: Automatically generated string parameters
        :param names: Aliases of the command. First name is
        :param function: coroutine(**kwargs) -> bool:
                        kwargs: arguments parsed from regexp groups + Command.command_parameters
        :param usage: String showing how the command should be called.
        :param description: String saying what command should do.
        """
        self.db = None
        self.names = names

        self.function = function

        self.flags = flags or {}
        self.positional_parameters = self.replace_prefabs(positional_parameters) or {}
        self.named_parameters = self.replace_prefabs(named_parameters) or {}

        self.regex = self.update_regexp()

        # check if regex contains invalid groups
        for group_name in self.regex.groupindex:
            if group_name in Command.command_parameters:
                raise Exception(f"Wrong command regexp: group name '{group_name}' is reserved.")

        self.usage = usage or self.build_usage()

        self.description = description
        if permissions is None:
            permissions = []
        if type(permissions) == str:
            permissions = [permissions]
        self.permissions = permissions

        self.timeout = timeout

    def is_match(self, text: str):
        for name in self.names:
            if text.lower().startswith(name):
                if len(text.lower()) > len(name) and not text.lower()[len(name)].isspace():
                    # this name is longer than my name
                    continue
                return True
        else:
            return False

    def user_has_permission(self, user):
        if type(user) is User:
            if self.permissions is not None and len(self.permissions) > 0:
                if any(user.has_permission(perm) for perm in self.permissions):
                    # user has an appropriate permission
                    return True
                else:
                    # user cannot use this command
                    return False
            else:
                return True
        else:
            raise Exception(f"user_has_permission not implemented for {type(user)}")

    async def execute(self, message: discord.Message, client: discord.Client, users: Users, log, text=None):
        if not self.user_has_permission(users.get_or_create(message.author)):
            return await message.channel.send(self._format_message(message=message,
                                                                   string="__author__ you can't do that!"))
        # get regex parsed arguments

        match = self.regex.match(text or message.content)
        if match is None:
            # no regex match found, return a usage message
            return await message.channel.send(self._format_message(message=message, string=self.usage))

        # parse arguments for the command function

        params = {
            'message': message,
            'db': self.db,
            'client': client,
            'user': users[message.author.id],
            'users': users,
            'log': log
        }

        params.update(match.groupdict())

        # finally run the command code
        return await self.function(**params)

    async def send_help(self, message: discord.Message):
        await message.channel.send(self._format_message(
            message=message, string=','.join(self.names) + '\n' + self.description + '\n' + self.usage))

    def _format_message(self, string: str, message: discord.Message):
        if string is None:
            return None
        string = string.replace('__name__', self.names[0])
        string = string.replace('__author__', f'<@{message.author.id}>')
        return string

    def __repr__(self):
        if self.names is None or len(self.names) == 0:
            return f'<Command() - uninitialized'
        else:
            return f'<Command({self.names[0]}) -> {repr(self.function)}>'

    def update_regexp(self):
        regexp = "^__name__"

        if self.flags is not None:
            flags = {}
            for f in self.flags:
                flags[f] = rf'\s*(?P<{f}>{self.flags[f]})\s*'

            regexp += f'(?P<_flags>({"|".join(flags.values())})*)'

        if self.positional_parameters is not None:
            if type(self.positional_parameters) is list:
                self.positional_parameters = dict.fromkeys(self.positional_parameters, r'.*?')

            for param in self.positional_parameters:
                # full = self.positional_parameters[param]
                # spaceless = self.positional_parameters[param].replace(".", r"\S")

                regexp += rf'\s*(?P<{param}>{self.positional_parameters[param]})\s*'

        if self.named_parameters is not None:
            named_params = {}
            for param in self.named_parameters:
                # full = self.named_params[param]
                # spaceless = self.named_params[param].replace(".", r"\S")

                real_name = param[1:] if param[0] == '_' else param

                named_params[param] = rf'(\s*{real_name}=(?P<{param}>{self.named_parameters[param]})\s*)'

            regexp += rf'\s*(?P<_optional_params>({"|".join(named_params.values())})*)'

        names = "|".join(self.names)
        regexp = regexp.replace("__name__", f'({names})')
        regexp += "$"

        self.regex = re.compile(regexp, flags=re.DOTALL|re.IGNORECASE|re.MULTILINE)
        return self.regex

    def replace_prefabs(self, params: dict):
        if params is None:
            return None

        if not isinstance(params, OrderedDict):
            params = OrderedDict(params)

        param_names = list(params.keys())

        for param_name in param_names:
            param = params[param_name]
            for prefab_name, prefab in self._param_prefabs.items():
                if prefab_name in param:
                    if '__value__' in prefab:
                        prefab = prefab.replace('__value__', param_name)

                        wrapper_name = '_' + param_name
                        change_key(params, param_name, wrapper_name)
                        param_name = wrapper_name
                    params[param_name] = param.replace(prefab_name, f'({prefab})')

        return params

    def build_usage(self):
        usage = f'Usage: {self.names[0]} '
        for f in self.flags:
            usage += f'[{f}] '

        for p in self.positional_parameters:
            usage += f'<{p}> '

        for opt in self.named_parameters:
            usage += f'[{opt}]'
        return usage


def change_key(d: OrderedDict, old, new):
    for _ in range(len(d)):
        k, v = d.popitem(False)
        d[new if old == k else k] = v
