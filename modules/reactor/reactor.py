from c__lib import format_table

from classes.cubot import Cubot
from classes.module import *
from classes.reactor import Reaction


class ReactorModule(Module):
    def __init__(self, **kwargs):
        super().__init__("reactor", **kwargs)

        self.addcom(
            Command(
                names=['addreactor'],
                regexp=r'^__name__\s*(?P<mention><@.*>)\s*(?P<emote><.*?>)'
                       r'\s*(?P<percentage>\d?\.?\d+%?)\s*(?P<cooldown>\d*)\s*(?P<server>-server)?$',
                function=self.add_reactor,
                usage='__author__ Usage: !addreactor <@mention> <emote> <chance> [-server]',
                description='Adds reactor.)',
                permissions=['reactors']
            )
        )

        self.addcom(
            Command(
                names=['listreactors'],
                regexp=r'^__name__( .*)?$',
                function=self.list_reactors,
                usage=f'__author__ Usage: !listreactors',
                description='Lists all reactors relevant to this server.',
                permissions=['reactors']
            )
        )

        self.addcom(
            Command(
                names=['removereactor'],
                regexp=r'^__name__\s*(?P<id>\d*)\s*$',
                function=self.remove_reactor,
                usage=f'__author__ Usage: !removereactor <id>',
                description='Removes a reactor.',
                permissions=['reactors']
            )
        )

    async def add_reactor(self, message: discord.Message, client: Cubot, **kwargs) -> bool:
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

    async def remove_reactor(self, message: discord.Message, client: Cubot, **kwargs) -> bool:
        try:
            reactor_id = int(kwargs['id'])
        except ValueError:
            await message.channel.send(f'{message.author.mention} specify which one!')
            return False

        removed = client.reactor.remove(reactor_id)

        await message.channel.send(f'{message.author.mention} removed {removed} reactors.')

        return True

    async def list_reactors(self, message: discord.Message, client: Cubot, **__) -> bool:
        table = []

        for r in client.reactor.reaction_list:
            table.append(['`' + str(r.id), r.user_name, str(r.chance), str(r.cooldown), '`' + r.emote])

        if len(table) == 0:
            await message.channel.send(f'There are no reactors present yet.')
            return True

        s = format_table(table, header=['`ID', 'Username', 'Chance', 'Cooldown', 'Emote`'])

        await message.channel.send(s)

        return True