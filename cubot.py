import datetime
import sqlite3
import builtins
import traceback

import discord

from c__lib.c__string import seconds_to_czech_string
from c__lib.c__string import format_table

from classes.reactor import Reaction
from classes.command import Command
from classes.cubot import Cubot
from classes.logger import Logger
from classes.service import Service

#  ############################# COMMANDS #############################################################################


async def test(message: discord.Message, __: sqlite3.Connection, client: Cubot, **kwargs):
    print(message.content)
    pass


async def profile_picture(message: discord.Message, __: sqlite3.Connection, client: Cubot, **kwargs):
    """
    Displays full sized profile picture of either user or a mentioned member.
    :param client:
    :param __:
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


async def get_user_id(message: discord.Message, __: sqlite3.Connection, client: Cubot, **kwargs):
    """
    Displays full sized profile picture of either user or a mentioned member.
    :param client:
    :param __:
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


async def classic_release(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    time_str = seconds_to_czech_string(
        (
                datetime.datetime.now() - datetime.datetime(year=2019, month=8, day=27, hour=00, minute=00)
        ).total_seconds())

    await message.channel.send(f'Classic je venku už {time_str}!')

    return True


async def love(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    await message.channel.send(f'Miluje tě, jj')

    return True


async def add_reactor(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
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

    await message.channel.send(f'{message.author.mention} added a {emote} reactor to {target.mention}  with a chance of {chance * 100}% and cooldown of {cooldown} seconds.')

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


async def remove_reactor(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    id: int
    try:
        id = int(kwargs['id'])
    except Exception as ex:
        await message.channel.send(f'{message.author.mention} specify which one!')
        return False

    removed = client.reactor.remove(id)

    await message.channel.send(f'{message.author.mention} removed {removed} reactors.')

    return True


async def list_reactors(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    table = []

    for r in client.reactor.reaction_list:
        table.append(['`' + str(r.id), r.user_name, str(r.chance), str(r.cooldown), '`' + r.emote])

    if len(table) == 0:
        await message.channel.send(f'There are no reactors present yet.')
        return True

    s = format_table(table, header=['`ID', 'Username', 'Chance', 'Cooldown', 'Emote`'])

    await message.channel.send(s)

    return True

    # await message.channel.send(f'Adding {emote} reactor to {target.mention}  with a chance of {chance*100}%')


async def change_username(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    await client.user.edit(username="Karel")
    await message.channel.send(f'Yes, master.')

    return True


async def minecraft(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    s = Service('minecraft.service')
    running = True
    status = ''
    address = 'firefly.danol.cz'
    try:
        running = s.is_running()
        status = s.status_string()
    except:
        pass

    if running:
        await message.channel.send(f'Minecraft server is running on {address}:\n{status})')
    else:
        await message.channel.send(f'Minecraft server is not running. Use "!minecraft start" to start it.\n'
                                   f'It will run on {address}.)')

    return True


async def minecraft_status(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    s = Service('minecraft.service')
    await message.channel.send('Minecraft status:\n' + s.status_string())
    return True


async def minecraft_start(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    s = Service('minecraft.service')
    if s.is_running():
        await message.channel.send('Minecraft is already running:\n' + s.status_string())
    else:
        s.start()
        await message.channel.send('Minecraft status:\n' + s.status_string())
    return True


async def minecraft_stop(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    s = Service('minecraft.service')
    if not s.is_running():
        s.stop()
        await message.channel.send('Stopping minecraft server:\n' + s.status_string())
    else:
        await message.channel.send('Minecraft server is not running:\n' + s.status_string())
    return True


async def minecraft_restart(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    s = Service('minecraft.service')
    s.restart()
    await message.channel.send('Restarting minecraft server:\n' + s.status_string())
    return True


async def permissions(message: discord.Message, db: sqlite3.Connection, client: Cubot, **kwargs) -> bool:
    s = Service('minecraft.service')
    s.restart()
    await message.channel.send('Restarting minecraft server:\n' + s.status_string())
    return True


def run_bot(client: Cubot):
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
            regexp=r'^__name__\s*(?P<mention><@.*>)\s*(?P<emote><.*?>)\s*(?P<percentage>\d?\.?\d+%?)\s*(?P<cooldown>\d*)\s*(?P<server>-server)?$',
            command=add_reactor,
            usage='__author__ Usage: !addreaction <@mention> <emote> <chance> [-server]',
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
            regexp=r'^__name__(\s*<@!?(?P<mention>\d*?)>)?$',
            command=get_user_id,
            usage='__author__ Usage: !get_id [@mention]',
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
            names=['minecraft', 'mc'],
            regexp=r'^__name__ (?P<name>)\s*$',
            command=minecraft,
            usage=f'__author__ Usage: !minecraft',
            description='Displays minecraft server\'s address.'
        )
    )

    client.addcom(
        Command(
            names=['minecraft start', 'mc start'],
            regexp=r'^__name__ (?P<name>)\s*$',
            command=minecraft_start,
            usage=f'__author__ Usage: !minecraft start',
            description='Starts the minecraft server.',
            # permissions=['minecraft']
        )
    )

    client.addcom(
        Command(
            names=['minecraft stop', 'mc stop'],
            regexp=r'^__name__ (?P<name>)\s*$',
            command=minecraft_stop,
            usage=f'__author__ Usage: !minecraft stop',
            description='Changes the bot''s username.',
            permissions=['minecraft']
        )
    )

    client.addcom(
        Command(
            names=['minecraft restart', 'mc restart'],
            regexp=r'^__name__ (?P<name>)\s*$',
            command=minecraft_restart,
            usage=f'__author__ Usage: !minecraft restart',
            description='Changes the bot''s username.',
            permissions=['minecraft']
        )
    )

    client.addcom(
        Command(
            names=['minecraft status', 'mc status'],
            regexp=r'^__name__ (?P<name>)\s*$',
            command=minecraft_status,
            usage=f'__author__ Usage: !minecraft start',
            description='Changes the bot''s username.'
        )
    )

    client.addcom(
        Command(
            names=['permissions', 'permission', 'p'],
            regexp=r'^__name__ (?P<name>)\s*$',
            command=minecraft_status,
            usage=f'__author__ Usage: !minecraft start',
            description='Changes the bot''s username.'
        )
    )

    client.run(open('token', 'r').read().strip())


if __name__ == '__main__':
    try:
        printer = Logger('./log.log', timestamps=True)
        print = printer.log
        bot = Cubot(log_commands=True, log_function=printer.log)
        run_bot(bot)
    except Exception as exc:
        builtins.print("Fatal exception thrown:")
        builtins.print(exc)

        tb = traceback.format_tb(exc.__traceback__)

        builtins.print(tb)

        exit(-1)
