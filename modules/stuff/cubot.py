import datetime

import numpy
from c__lib import seconds_to_czech_string

from classes.module import *


class CubotModule(Module):
    def __init__(self, **kwargs):
        super().__init__("cubot", **kwargs)

        self.addcom(
            Command(
                names=['classic'],
                regexp=r'^__name__( .*)?$',
                function=self.classic_release,
                usage=f'__author__ Usage: !classic',
                description='Displays time since release of Classic WoW in czech language.'
            )
        )

        self.addcom(
            Command(
                names=['iq'],
                regexp=r'^__name__\s*(<@!?(?P<mention>\d*?)>)?$',
                function=self.random_iq,
                usage='__author__ Usage: !iq [@mention]',
                description='Magically measures user\'s iq.'
            )
        )

    async def classic_release(self, message: discord.Message, **__) -> bool:
        time_str = seconds_to_czech_string(
            (
                    datetime.datetime.now() - datetime.datetime(year=2019, month=8, day=27, hour=00, minute=00)
            ).total_seconds())

        await message.channel.send(f'Classic je venku už {time_str}!')

        return True

    async def random_iq(self, message: discord.Message, **__) -> bool:
        mention: discord.Member
        mention = message.mentions[0] if len(message.mentions) > 0 else message.author

        iq = int(numpy.random.normal(100, 15))

        await message.channel.send(f'{mention.name}\'s iq is {iq}.')

        return True

    async def slap(self, message: discord.Message, **kwargs) -> bool:
        # <person A> slaps <person B> around a bit with a large trout

        user = message.author

        if kwargs['mention'] is None:
            target = message.guild.get_member(int(kwargs['mention']))
        else:
            return False

        await message.channel.send(f'{user.name} slaps {target.name} around a bit with a large trout.')

        return True
