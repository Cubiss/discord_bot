import asyncio
import random

import c__lib
import discord

from classes.module import *
from .characters import Characters, Character
from c__lib import format_table
from collections import OrderedDict, namedtuple


class HappyAdventureModule(Module):
    def __init__(self, **kwargs):
        super().__init__("happyAdventure", **kwargs)

        self.channel = None

        self.addcom(
            Command(names=['roll', 'r'],
                    function=self.roll, usage='__author__ Usage: !roll [n]d[n] [+bonus]',
                    description='Rolls the dice. ',
                    positional_parameters=OrderedDict([
                        ('dice', r'((?P<count>\d*)d(?P<faces>\d+))?'),
                        ('bonus_info', r'((?P<bonus_sign>\+|\-)(?P<bonus>\d*))?')
                        ])
                    )
        )

        self.addcom(
            Command(names=['setrole'],
                    function=self.setrole,
                    description='Set role for a character.',
                    positional_parameters=OrderedDict([
                        ('char', r'(DW|EL|HE|GN|HU)'),
                        ('role', r'__role__')
                    ])
                    )
        )

        self.addcom(
            Command(names=['stats'],
                    function=self.stats
                    )
        )

        self.chars = ['DW', 'EL', 'HE', 'GN', 'HU']

        for c in self.chars:
            async def ach(**__):
                await self.add(c, "HP", **__)

            async def amh(**__):
                await self.add(c, "MAX_HP", **__)

            async def aca(**__):
                await self.add(c, "ARMOR", **__)

            async def ama(**__):
                await self.add(c, "MAX_ARMOR", **__)

            async def sch(**__):
                await self.set(c, "HP", **__)

            async def smh(**__):
                await self.set(c, "MAX_HP", **__)

            async def sca(**__):
                await self.set(c, "ARMOR", **__)

            async def sma(**__):
                await self.set(c, "MAX_ARMOR", **__)

            self.addcom(Command([f'a{c}ch', f'add{c}currenthp', f'add{c}currenthealth'],
                                function=ach,
                                description=f'Add current {c} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ])
                                ))

            self.addcom(Command([f'a{c}mh', f'add{c}maxhp', f'add{c}maxhealth'],
                                function=amh,
                                description=f'Add current {c} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ])
                                ))

            self.addcom(Command([f'a{c}ca', f'add{c}currentarmor'],
                                function=aca,
                                description=f'Add current {c} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ])
                                ))

            self.addcom(Command([f'a{c}ma', f'add{c}maxarmor'],
                                function=ama,
                                description=f'Add current {c} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ])
                                ))

            self.addcom(Command([f's{c}ch', f'set{c}currenthp', f'set{c}currenthealth'],
                                function=sch,
                                description=f'Set current {c} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ])
                                ))

            self.addcom(Command([f's{c}mh', f'set{c}maxhp', f'set{c}maxhealth'],
                                function=smh,
                                description=f'Set current {c} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ])
                                ))

            self.addcom(Command([f's{c}ca', f'set{c}currentarmor'],
                                function=sca,
                                description=f'Set current {c} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ])
                                ))

            self.addcom(Command([f's{c}ma', f'set{c}maxarmor'],
                                function=sma,
                                description=f'Set current {c} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ])
                                ))

        for c in self.commands:
            print(c.names)

        self.characters = Characters(self.db)
        self.characters.load()

    async def roll(self, message: discord.Message, count, faces, bonus, **__) -> bool:
        try:
            if count is None or count == '':
                count = 1
            else:
                count = abs(int(count))

            if faces is not None:
                faces = abs(int(faces))
            else:
                faces = 20

            if bonus is None or bonus == '':
                bonus = 0
            else:
                bonus = abs(int(bonus))

            if count > 100000:
                return await message.channel.send(f'For real?!')
        except:
            return await message.channel.send(f'Not like this')

        rolls = []
        rolls_str = []

        for i in range(0, count):
            result = random.randint(1, faces) + bonus
            rolls.append(result)
            rolls_str.append(str(result))
            if i % 420 == 0:
                # return control to the event loop
                await asyncio.sleep(0)

        bonus_msg = ""
        if bonus > 0:
            bonus_msg = f' with a bonus of {bonus}'

        if len(rolls) == 1:
            await message.channel.send(
                f'Rolling d{faces}{bonus_msg}... Your rolled **{sum(rolls)}**!')
        else:
            avgstr = f'{sum(rolls) / len(rolls):.2f}'

            msg = f'Rolling {count}d{faces}{bonus_msg}...\n {"... ".join(rolls_str)}... \nYour result is **{sum(rolls)}**!\nAverage roll was {avgstr}'

            if len(msg) > 1900:
                msg = f'Rolling {count}d{faces}{bonus_msg}... \nYour result is **{sum(rolls)}**!\nAverage roll was {avgstr}'

            await message.channel.send(msg)

        return True

    async def set(self, message, char, stat, query, **_):
        char = char.upper()
        if char.upper() not in self.chars:
            await message.channel.send(f"Character {char} not found.")
            return False

        c = self.characters[char]
        c.__setattr__(stat, float(query))
        c.save()
        return True

    async def add(self, message, char, stat, query, **_):
        char = char.upper()
        if char.upper() not in self.chars:
            await message.channel.send(f"Character {char} not found.")
            return False
        c = self.characters[char]
        c.__setattr__(stat, c.__getattr__(stat) + float(query))
        c.save()
        return True

    async def setrole(self, message, char, role, **_):
        char = char.upper()
        if char not in self.chars:
            await message.channel.send(f"Character {char} not found.")
            return False
        c = self.characters[char]
        c.ROLE = role
        c.save()

        return True

    async def stats(self, message: discord.Message, **_):
        roles = message.author.roles

        table = []
        for c in self.characters:
            for r in message.author.roles:
                if r.id == c.ROLE:
                    t = c__lib.format_table(
                            header=["CHAR", "HP", "ARMOR"],
                            table=[[c.CHARACTER_ID, f"{c.HP}/{c.MAX_HP}", f"{c.ARMOR}/{c.MAX_ARMOR}"]]
                        )

                    await message.channel.send(
                        f"```"
                        f"{t}"
                        f"```"
                    )
                    return True

            table.append([c.CHARACTER_ID, f"{c.HP}/{c.MAX_HP}", f"{c.ARMOR}/{c.MAX_ARMOR}"])

        t =  c__lib.format_table(
                header=["CHAR", "HP", "ARMOR"],
                table=table
            )
        await message.channel.send(
            "```"
            rf"{t}"
            "```"
        )

        return True
