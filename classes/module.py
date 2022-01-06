import discord

from classes.command import Command
from classes.logger import Logger


class Module:
    def __init__(self, name: str, log: Logger = None):
        self.name = name

        self.commands = []
        if log is None:
            self.log = Logger(file=None, use_stdout=True, log_file_writes=False, add_timestamps=True)

    def addcom(self, command: Command):
        self.commands.append(command)
