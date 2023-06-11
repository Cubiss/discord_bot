from collections import OrderedDict
import re

import discord
from c__lib import format_table

from classes.command import Command
from classes.module import Module


class HelpModule(Module):
    def __init__(self, **kwargs):
        super().__init__(
            name="help",
            description="!help implementation",
            default_permissions=[],
            **kwargs)

        self.addcom(
            Command(names=['help', 'h'], function=self.send_help,
                    usage='__author__ Usage: !test __any__', description='Test command.',
                    positional_parameters=OrderedDict([
                        ("msgcontent", r'__any__')
                    ]))
        )

        self.addcom(
            Command(
                names=['modules'],
                description='List loaded modules',
                function=self.list_modules
            )
        )

    async def help(self, message: discord.Message, **_):
        regex = re.compile(r'!help(\s+(?P<name>.*))?')

        if (m := regex.match(message.content)) is not None:
            m: re.Match
            names = m.group('name')
            if names:
                names = names.split()
            else:
                help_str = '```'
                help_str += 'Available commands:\n'

                max_command_len = max([len(c.name) for c in self.client.commands])

                for command in self.client.commands:
                    command: Command
                    if command.help_scope_in(Command.HELP_SCOPE_GLOBAL):
                        help_str += f'{command.name:{max_command_len}}: {command.description}\n'

                help_str += '```'

                self.log(help_str)
                return await message.channel.send(help_str)

            while len(names) > 0:
                name = names.pop(0).lower()

                for module in self.client.modules:
                    module: Module
                    if module.name.lower() == name.lower():
                        return await module.send_help(message)

                for command in self.client.commands:
                    if name in command.names:
                        return await command.send_help(message, names=names)

                else:
                    return await message.channel.send(f'Command "{name}" not found.')

    async def list_modules(self, message: discord.Message, **_):
        modules_str = '```'
        modules_str += 'Loaded modules:\n'

        modules = []

        for m in self.client.modules:
            m: Module
            modules.append([m.name, m.description])

        modules_str += format_table(modules, ['Name', 'Description'])
        modules_str += '```'

        await message.channel.send(modules_str)
