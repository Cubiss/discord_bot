import discord
import re

from .command import Command
from modules.users.users import Users


class CommandTree(Command):
    def __init__(self, names: list, children: list, permissions=None, description=''):
        try:
            self.children = {}

            _names = set()
            for c in children:
                for n in c.names:
                    if n in _names:
                        raise Exception(f"Duplicate subcommand name: {n}")
                    _names.add(n)
                self.children[c.names[0]] = c

            # self.regex = self.update_regexp()

            super(CommandTree, self).__init__(
                names=names, function=self.execute_branching, permissions=permissions, description=description)

            pass
        except Exception as ex:
            raise Exception(f"CommandTree({self.names[0]})")

    def update_regexp(self):
        c: Command
        children_names_regexes = []
        for subcommand_name, c in self.children.items():
            children_names_regexes.append(rf'(?P<{subcommand_name}>{"|".join(c.names)})')

        return re.compile(
            rf'(?P<command_name>{"|".join(self.names)})\s*(?P<subcommand>({"|".join(children_names_regexes)}).*)')

    async def execute_branching(self, subcommand, message: discord.Message, client: discord.Client, users: Users, log, **kwargs):
        for subcommand_name in self.children:
            if kwargs[subcommand_name] is not None:
                return await self.children[subcommand_name].execute(message=message, client=client, users=users, log=log,
                                                                    text=subcommand)

    def build_usage(self):
        return f'Allowed commands: {self.names[0]} ({"|".join(self.children)})'

    async def send_help(self, message: discord.Message, names=None):
        if names is not None and len(names) > 0:
            name = names.pop(0)

            for c in self.children.values():
                if name in c.names:
                    return await c.send_help(message, names)

        return await super().send_help(message)

    def __repr__(self):
        if self.names is None or len(self.names) == 0:
            return f'<CommandTree() - uninitialized'
        else:
            return f'<CommandTree({self.names[0]}) -> {repr(self.function)}>'
