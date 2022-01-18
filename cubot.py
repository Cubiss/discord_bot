#!/usr/bin/python3
import asyncio
import os
import random
import time
import traceback
import argparse
import signal

import c__lib

from classes.cubot import Cubot
from classes.logger import Logger
from classes.module import Module

from modules import *


def log(x):
    print(x)

#  ############################# COMMANDS #############################################################################


def load_modules():
    for root, dirs, files in os.walk('modules'):
        for f in files:
            path = os.path.join(root, f)
            if os.path.splitext(path)[1].lower() == '.py':
                module_path = os.path.split(path)[0].replace('/', '\\').replace('\\', '.')
                module_name = os.path.split(path)[1].replace('.py', '')
                full_module_path = f'{module_path}.{module_name}'

                try:
                    __import__(full_module_path)
                    log(f'Imported module: {full_module_path}')
                except Exception as ex:
                    log(f'Failed to import module {full_module_path}: {ex}')

    return Module.__subclasses__()


def run_bot(client: Cubot, token: str):

    if c__lib.get_platform() == c__lib.platform_windows:
        def signal_handler(_, __):
            client.loop.stop()
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)
    else:
        async def signal_handler():
            await client.close()
            client.loop.stop()

        for signame in ('SIGINT', 'SIGTERM'):
            client.loop.add_signal_handler(getattr(signal, signame), lambda: asyncio.create_task(signal_handler()))

    client.load_modules(load_modules())

    errors = 0
    while 1:
        # noinspection PyBroadException
        try:
            client.run(token)
            log(f'Client was stopped.')
        except Exception as ex:
            # todo: catch the right exception
            errors += 1
            log(f'client.run Exception[{errors}]:\n{ex}')
            time.sleep(15)


def main():
    global log
    try:
        random.seed(time.time())

        parser = argparse.ArgumentParser(description='Create thumbnails for all images recursively bottom up.')
        parser.add_argument('--token', type=str, default='token', required=False,
                            help='Path to file with a discord login token: '
                                 'https://discordpy.readthedocs.io/en/latest/discord.html#discord-intro')
        parser.add_argument('--log', type=str, default=None, required=False,
                            help='Working directory for making thumbnails.')
        parser.add_argument('--db', type=str, default='cubot.db', required=False,
                            help='Database file location.')
        parser.add_argument('--no_timestamps', action='store_true', default=False,
                            help='Don\'t add timestamps to log file.')
        args = parser.parse_args()
        if args.log is None:
            log = Logger(file=None, use_stdout=True, log_file_writes=False, add_timestamps=not args.no_timestamps)
        else:
            log = Logger.create_logger(path=args.log, add_timestamps=not args.no_timestamps)
        bot = Cubot(log_commands=True, log_function=log, database=args.db)
        run_bot(bot, open(args.token, 'r').read().strip())
    except Exception as ex:
        print("Fatal exception thrown:")
        print(ex)

        tb = '\n'.join(traceback.format_tb(ex.__traceback__))

        print(tb)

        exit(-1)


if __name__ == '__main__':
    main()
