#!/usr/bin/python3
import datetime
import builtins
import time
import traceback
import argparse
import discord
import numpy
import signal

from c__lib import seconds_to_czech_string
from c__lib import format_table

from classes.reactor import Reaction
from classes.command import Command
from classes.cubot import Cubot
from classes.logger import Logger
from classes.service import Service
from classes.users import User


#  ############################# COMMANDS #############################################################################


async def test(message: discord.Message, **__):
    log(message.content)
    pass


async def profile_picture(message: discord.Message, **kwargs):
    """
    Displays full sized profile picture of either user or a mentioned member.
    :param message:
    :param kwargs:
    :return:
    """
    if kwargs['mention'] is None:
        user = message.author
    else:
        user = message.guild.get_member(int(kwargs['mention']))

    embed = discord.Embed(
        title=f'{user.name}\'s profile picture.',
        # description='{}\'s profile picture.'.format(user.mention) , color=0xecce8b
    )
    embed.set_image(url=user.avatar_url)
    await message.channel.send(
        '',
        embed=embed
    )

    return True


async def get_user_id(message: discord.Message, **kwargs):
    """
    Displays full sized profile picture of either user or a mentioned member.
    :param message:
    :param kwargs:
    :return:
    """
    if kwargs['mention'] is None:
        user = message.author
    else:
        user = message.guild.get_member(int(kwargs['mention']))

    await message.channel.send(
        f'{str(user)}\'s id: {user.id}'
    )
    return True


async def classic_release(message: discord.Message, **__) -> bool:
    time_str = seconds_to_czech_string(
        (
                datetime.datetime.now() - datetime.datetime(year=2019, month=8, day=27, hour=00, minute=00)
        ).total_seconds())

    await message.channel.send(f'Classic je venku už {time_str}!')

    return True


async def love(message: discord.Message, **__) -> bool:
    await message.channel.send(f'Miluje tě, jj')

    return True


async def add_reactor(message: discord.Message, client: Cubot, **kwargs) -> bool:
    if len(message.mentions) == 0:
        await message.channel.send(f'{message.author.mention} you didn\'t mention anyone!')
        return False

    target = message.mentions[0]

    emote = kwargs['emote']
    chance = kwargs['percentage']
    cooldown = kwargs['cooldown']
    cooldown = 0 if cooldown is None or cooldown == '' else int(cooldown)

    server = 0 if kwargs['percentage'] is None else message.guild.id

    if chance.endswith('%'):
        chance = float(chance.strip('%')) / 100
    else:
        chance = float(chance)

    await message.channel.send(f'{message.author.mention} added a {emote} reactor to {target.mention}'
                               f' with a chance of {chance * 100}% and cooldown of {cooldown} seconds.')

    client.reactor.add(
        Reaction(
            user_id=target.id,
            user_name=target.name,
            server_id=server,
            emote=emote,
            chance=chance,
            cooldown=cooldown
        )
    )

    return True


async def remove_reactor(message: discord.Message, client: Cubot, **kwargs) -> bool:
    try:
        reactor_id = int(kwargs['id'])
    except ValueError:
        await message.channel.send(f'{message.author.mention} specify which one!')
        return False

    removed = client.reactor.remove(reactor_id)

    await message.channel.send(f'{message.author.mention} removed {removed} reactors.')

    return True


async def list_reactors(message: discord.Message, client: Cubot, **__) -> bool:
    table = []

    for r in client.reactor.reaction_list:
        table.append(['`' + str(r.id), r.user_name, str(r.chance), str(r.cooldown), '`' + r.emote])

    if len(table) == 0:
        await message.channel.send(f'There are no reactors present yet.')
        return True

    s = format_table(table, header=['`ID', 'Username', 'Chance', 'Cooldown', 'Emote`'])

    await message.channel.send(s)

    return True


async def change_username(message: discord.Message, client: Cubot, **__) -> bool:
    await client.user.edit(username="Karel")
    await message.channel.send(f'Yes, master.')

    return True


async def minecraft(message: discord.Message, user: User, cmd=None, **__) -> bool:
    cmd = (cmd or '').lower()

    if cmd not in ['', 'ip', 'status', 'start', 'stop', 'restart']:
        await message.channel.send(f"Invalid command: {cmd}")
        return True

    s = Service('minecraft.service', use_dbus=False)
    status_string = s.status_string()

    if cmd in ['', 'ip']:
        running = True
        status = ''
        address = 'firefly.danol.cz'
        from subprocess import CalledProcessError
        try:
            running = s.is_running()
            status = s.status_string()
        except CalledProcessError:
            pass

        if running:
            await message.channel.send(f'Minecraft server is running on {address}:\n{status})')
        else:
            await message.channel.send(f'Minecraft server is not running. Use "!minecraft start" to start it.\n'
                                       f'It will run on {address}.')
        return True

    elif cmd == 'status':
        await message.channel.send('Minecraft status:\n' + status_string)
        return True

    if user is not None and user.has_permission('minecraft'):
        if cmd == 'start':
            if s.is_running():
                await message.channel.send('Minecraft is already running:\n' + status_string)
            else:
                try:
                    s.start()
                except Exception as ex:
                    await message.channel.send(f'Failed to start the server: {ex}')
                    return False
                await message.channel.send('Minecraft status:\n' + s.status_string())
            return True

        elif cmd == 'stop':
            if s.is_running():
                try:
                    s.stop()
                except Exception as ex:
                    await message.channel.send(f'Failed to start the server: {ex}')
                    return False
                await message.channel.send('Stopping minecraft server:\n' + s.status_string())
            else:
                await message.channel.send('Minecraft server is not running:\n' + status_string)
            return True

        elif cmd == 'restart':
            try:
                s.stop()
            except Exception as ex:
                await message.channel.send(f'Failed to start the server: {ex}')
                return False
            await message.channel.send('Restarting minecraft server:\n' + s.status_string())
            return True
    else:
        await message.channel.send(f"You don't have permission for following command: {cmd}")
        return True


async def permissions(message: discord.Message, client: Cubot, **kwargs) -> bool:
    from classes.users import Users, User
    cmd = kwargs['command']
    mention: discord.Member
    mention = message.mentions[0] if len(message.mentions) > 0 else None
    permission = kwargs['permission']

    u: User
    ul: Users = client.user_list

    if cmd == 'add':
        u = ul.get_or_create(mention)
        if permission is None:
            await message.channel.send(f"Usage: !permissions add @who permissoin")
            return False
        if permission in u.permissions:
            await message.channel.send(f"{mention.nick or mention.display_name} already has that permission.")
            return True
        u.permissions.append(permission)
        u.save()
        await message.channel.send(f"Added '{permission}' permission to {mention.nick or mention.display_name}")
    elif cmd == 'remove':
        u = ul[mention.id]
        if u is None or permission not in u.permissions:
            await message.channel.send(f"{mention.display_name} doesn't have '{permission}' permission.")
        else:
            u.permissions.remove(permission)
            u.save()
            await message.channel.send(f"Removed '{permission}' permission from {mention.nick or mention.display_name}")
    elif cmd == 'list':
        if mention is not None:
            u = ul[mention.id]
            if u is None or len(u.permissions) == 0:
                await message.channel.send(f"{mention.nick or mention.display_name} has no permissions.")
            else:
                await message.channel.send(f"{mention.nick or mention.display_name}'s permissions:\n"
                                           f"{', '.join(u.permissions)}")
        if permission is not None:
            users = [u.name for u in ul if u.has_permission(permission)]
            if len(users) == 0:
                await message.channel.send(f"Nobody has '{permission}' permission.")
            else:
                await message.channel.send(f"Users with '{permission}' permissions:\n"
                                           f"{', '.join(users)}")
        pass
    else:
        await message.channel.send(f"Wrong command: '{cmd}'. Only one of following is available: add, remove, list")

    return True


async def random_iq(message: discord.Message, **__) -> bool:
    mention: discord.Member
    mention = message.mentions[0] if len(message.mentions) > 0 else None

    iq = int(numpy.random.normal(100, 15))

    await message.channel.send(f'{mention.name}\'s iq is {iq}.')

    return True


def run_bot(client: Cubot, token: str):
    def signal_handler(_, __):
        client.logout()
        exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    client.addcom(
        Command(
            names=['profilepicture', 'profilepic', 'pp'],
            regexp=r'^__name__(\s*<@!?(?P<mention>\d*?)>)?$',
            command=profile_picture,
            usage='__author__ Usage: !profilepicture [@mention]',
            description='Displays profile picture of you or a mentioned user.'
        )
    )

    client.addcom(
        Command(
            names=['test', 't'],
            regexp=r'^__name__(.*)?$',
            command=test,
            usage='__author__ Usage: !profilepicture [@mention]',
            description='Test command.',
            permissions=['admin']
        )
    )

    client.addcom(
        Command(
            names=['addreactor'],
            regexp=r'^__name__\s*(?P<mention><@.*>)\s*(?P<emote><.*?>)'
                   r'\s*(?P<percentage>\d?\.?\d+%?)\s*(?P<cooldown>\d*)\s*(?P<server>-server)?$',
            command=add_reactor,
            usage='__author__ Usage: !addreactor <@mention> <emote> <chance> [-server]',
            description='Adds reactor.)',
            permissions=['reactors']
        )
    )

    client.addcom(
        Command(
            names=['listreactors'],
            regexp=r'^__name__( .*)?$',
            command=list_reactors,
            usage=f'__author__ Usage: !listreactors',
            description='Lists all reactors relevant to this server.',
            permissions=['reactors']
        )
    )

    client.addcom(
        Command(
            names=['removereactor'],
            regexp=r'^__name__\s*(?P<id>\d*)\s*$',
            command=remove_reactor,
            usage=f'__author__ Usage: !removereactor <id>',
            description='Removes a reactor.',
            permissions=['reactors']
        )
    )

    client.addcom(
        Command(
            names=['get_id'],
            regexp=r'^__name__(\s+<@!?(?P<mention>\d*?)>)?$',
            command=get_user_id,
            usage='__author__ Usage: !permission <add|remove|list> [@mention] [permission_name]',
            description='Displays discord id of mentioned user. (For devs mainly.)'
        )
    )

    client.addcom(
        Command(
            names=['classic'],
            regexp=r'^__name__( .*)?$',
            command=classic_release,
            usage=f'__author__ Usage: !classic',
            description='Displays time since release of Classic WoW in czech language.'
        )
    )

    client.addcom(
        Command(
            names=['love'],
            regexp=r'^__name__( .*)?$',
            command=love,
            usage=f'__author__ Usage: !love',
            description='Řekne jestli tě miluje.'
        )
    )

    client.addcom(
        Command(
            names=['change_username', 'cu'],
            regexp=r'^__name__ (?P<name>.*)$',
            command=change_username,
            usage=f'__author__ Usage: !change_username <username>',
            description='Changes the bot''s username.',
            permissions=['admin']
        )
    )

    client.addcom(
        Command(
            names=['minecraft'],
            regexp=r'^__name__\s*(?P<cmd>\S*)$',
            command=minecraft,
            usage=f'__author__ Usage: !minecraft',
            description='Displays minecraft server\'s address.'
        )
    )

    client.addcom(
        Command(
            names=['permissions', 'permission'],
            regexp=r'^__name__\s+(?P<command>add|remove|list)(\s+<@!?(?P<mention>\d*?)>)?(\s+(?P<permission>.*?))?$',
            command=permissions,
            usage=f'__author__ Usage: !permissions <add|remove|list> [@who] [permission]',
            description='Change permissions.'
        )
    )

    client.addcom(
        Command(
            names=['iq'],
            regexp=r'^__name__(\s*<@!?(?P<mention>\d*?)>)?$',
            command=random_iq,
            usage='__author__ Usage: !iq [@mention]',
            description='Magically measures user\'s iq.'
        )
    )

    for tries in range(0, 30):
        # noinspection PyBroadException
        try:
            client.run(token)
        except Exception:
            # todo: catch the right exception
            time.sleep(60)


if __name__ == '__main__':
    try:
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
    except Exception as exc:
        builtins.print("Fatal exception thrown:")
        builtins.print(exc)

        tb = '\n'.join(traceback.format_tb(exc.__traceback__))

        builtins.print(tb)

        exit(-1)
