import datetime
import builtins
import traceback

import discord

from c__lib import seconds_to_czech_string
from c__lib import format_table


from classes.reactor import Reaction
from classes.command import Command
from classes.cubot import Cubot
from classes.logger import Logger
from classes.service import Service

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


async def minecraft(message: discord.Message, **__) -> bool:
    s = Service('minecraft.service')
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
        await message.channel.send(f'Minecraft server is not running. Use "!mcserver start" to start it.\n'
                                   f'It will run on {address}.')

    return True


async def minecraft_status(message: discord.Message, **__) -> bool:
    s = Service('minecraft.service')
    await message.channel.send('Minecraft status:\n' + s.status_string())
    return True


async def minecraft_start(message: discord.Message, **__) -> bool:
    s = Service('minecraft.service')
    if s.is_running():
        await message.channel.send('Minecraft is already running:\n' + s.status_string())
    else:
        s.start()
        await message.channel.send('Minecraft status:\n' + s.status_string())
    return True


async def minecraft_stop(message: discord.Message, **__) -> bool:
    s = Service('minecraft.service')
    if s.is_running():
        s.stop()
        await message.channel.send('Stopping minecraft server:\n' + s.status_string())
    else:
        await message.channel.send('Minecraft server is not running:\n' + s.status_string())
    return True


async def minecraft_restart(message: discord.Message, **__) -> bool:
    s = Service('minecraft.service')
    s.restart()
    await message.channel.send('Restarting minecraft server:\n' + s.status_string())
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
        u.permissions.append(permission)
        u.save()
        await message.channel.send(f"Added '{permission}' permission to {mention.nick or mention.display_name}")
    elif cmd == 'remove':
        u = ul[mention.id]
        if u is None or permission not in u.permissions:
            await message.channel.send(f"{u.name} doesn't have '{permission}' permission.")
        else:
            u.permissions.remove(permission)
            u.save()
            await message.channel.send(f"Removed '{permission}' permission from {mention.nick or mention.display_name}")
    elif cmd == 'list':
        if mention is not None:
            u = ul[mention.id]
            if u is None or len(u.permissions) == 0:
                await message.channel.send(f"{mention.nick or mention.display_name} has no pe")
            else:
                await message.channel.send(f"{mention.nick or mention.display_name}'s permissions:\n"
                                           f"{', '.join(u.permissions)}")

        pass
    else:
        await message.channel.send(f"Wrong command: '{cmd}'. Only one of following is available: add, remove, list")

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
            regexp=r'^__name__\s*$',
            command=minecraft,
            usage=f'__author__ Usage: !minecraft',
            description='Displays minecraft server\'s address.'
        )
    )

    client.addcom(
        Command(
            names=['mcserver start', 'mcs start'],
            regexp=r'^__name__\s*$',
            command=minecraft_start,
            usage=f'__author__ Usage: !mcserver start',
            description='Starts the minecraft server.',
            # permissions=['minecraft']
        )
    )

    client.addcom(
        Command(
            names=['mcserver stop', 'mcs stop'],
            regexp=r'^__name__\s*$',
            command=minecraft_stop,
            usage=f'__author__ Usage: !mcserver stop',
            description='Changes the bot''s username.',
            permissions=['minecraft']
        )
    )

    client.addcom(
        Command(
            names=['mcserver restart', 'mcs restart'],
            regexp=r'^__name__\s*$',
            command=minecraft_restart,
            usage=f'__author__ Usage: !mcserver restart',
            description='Changes the bot''s username.',
            permissions=['minecraft']
        )
    )

    client.addcom(
        Command(
            names=['mcserver status', 'mcs status'],
            regexp=r'^__name__\s*$',
            command=minecraft_status,
            usage=f'__author__ Usage: !mcserver status',
            description='Changes the bot\'s username.'
        )
    )

    client.addcom(
        Command(
            names=['permissions', 'permission'],
            regexp=r'^__name__\s+(?P<command>add|remove|list)(\s+<@!?(?P<mention>\d*?)>)?(\s+(?P<permission>.*?))?$',
            command=permissions,
            usage=f'__author__ Usage: !minecraft start',
            description='Change permissions.'
        )
    )

    client.run(open('token', 'r').read().strip())


if __name__ == '__main__':
    try:
        log = Logger.create_logger(path='./log.log', add_timestamps=True)
        bot = Cubot(log_commands=True, log_function=log)
        run_bot(bot)
    except Exception as exc:
        builtins.print("Fatal exception thrown:")
        builtins.print(exc)

        tb = '\n'.join(traceback.format_tb(exc.__traceback__))

        builtins.print(tb)

        exit(-1)

