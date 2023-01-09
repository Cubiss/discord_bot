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
            Command(names=['listroles'],
                    function=self.listroles,
                    description='List roles for all characters.'
                    )
        )

        self.addcom(
            Command(names=['stats'],
                    function=self.stats,
                    description='Display player\'s stats.'
                    )
        )

        self.addcom(
            Command(names=['coinflip'],
                    function=self.coinflip,
                    description='Toss a coin.'
                    )
        )


        self.chars = {
            'DW': 'Dwarf',
            'EL': 'Elf',
            'HE': 'Half-elf',
            'HU': 'Human',
            'GN': 'Gnome'
        }

        for char in self.chars:
            self.addcom(Command([f'a{char}ch', f'add{char}currenthp', f'add{char}currenthealth'],
                                function=self.add,
                                description=f'Add current {self.chars[char]} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ]),
                                show_help=False
                                ))

            self.addcom(Command([f'a{char}mh', f'add{char}maxhp', f'add{char}maxhealth'],
                                function=self.add,
                                description=f'Add current {self.chars[char]} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ]),
                                show_help=False
                                ))

            self.addcom(Command([f'a{char}a', f'add{char}currentarmor'],
                                function=self.add,
                                description=f'Add current {self.chars[char]} armor',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ]),
                                show_help=False
                                ))

            self.addcom(Command([f's{char}ch', f'set{char}currenthp', f'set{char}currenthealth'],
                                function=self.set,
                                description=f'Set current {self.chars[char]} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ]),
                                show_help=False
                                ))

            self.addcom(Command([f's{char}mh', f'set{char}maxhp', f'set{char}maxhealth'],
                                function=self.set,
                                description=f'Set current {self.chars[char]} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ]),
                                show_help=False
                                ))

            self.addcom(Command([f's{char}a', f'set{char}currentarmor'],
                                function=self.set,
                                description=f'Set current {self.chars[char]} hp',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ]),
                                show_help=False
                                ))

            self.addcom(Command([f'd{char}', f'damage{char}'],
                                function=self.damage,
                                description=f'Damage {self.chars[char]}',
                                positional_parameters=OrderedDict([
                                        ('query', '__number__')
                                    ]),
                                ))


        self.characters = Characters(self.db)
        self.characters.load()

    async def coinflip(self, message: discord.Message, **_):
        await message.channel.send(f"The coin spins for a while... And it lands on **{random.choice(['HEADS', 'TAILS'])}**!")

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

    async def set(self, message, query, **_):

        char = message.content[2:4].upper()
        stat = message.content[4:6].lower()
        query = int(query)

        char = char.upper()
        if char.upper() not in self.chars:
            await message.channel.send(f"Character {char} not found.")
            return False

        c = self.characters[char]
        c: Character
        if stat == "mh":
            c.MAX_HP = query
            if c.HP == 0:
                c.HP = c.MAX_HP
            await message.channel.send(f"{self.chars[c.CHARACTER_ID]}'s HP changed to {c.HP}/{c.MAX_HP}")
        elif stat == "ch":
            c.HP = min(query, c.MAX_HP)
            await message.channel.send(f"{self.chars[c.CHARACTER_ID]}'s HP changed to {c.HP}/{c.MAX_HP}")
        # elif stat == 'ma':
        #     c.MAX_ARMOR = query
        #     if c.ARMOR == 0:
        #         c.ARMOR = c.MAX_ARMOR
        #     await message.channel.send(f"{char}'s ARMOR changed to {c.ARMOR}/{c.MAX_ARMOR}")
        elif stat == 'a ':
            c.ARMOR = query
            await message.channel.send(f"{self.chars[c.CHARACTER_ID]}'s ARMOR changed to {c.ARMOR}")
        else:
            await message.channel.send(f"Unknown stat: {stat}")
        c.save()

        return True

    async def add(self, message, query, **_):

        char = message.content[2:4].upper()
        stat = message.content[4:6].lower()
        query = int(query)

        char = char.upper()
        if char.upper() not in self.chars:
            await message.channel.send(f"Character {char} not found.")
            return False

        c = self.characters[char]
        c: Character
        if stat == "mh":
            c.MAX_HP = c.MAX_HP + query
            await message.channel.send(f"{self.chars[c.CHARACTER_ID]}'s HP changed to {c.HP}/{c.MAX_HP}")
        elif stat == "ch":
            c.HP = min(c.HP + query, c.MAX_HP)
            await message.channel.send(f"{self.chars[c.CHARACTER_ID]}'s HP changed to {c.HP}/{c.MAX_HP}")
        # elif stat == 'ma':
        #     c.MAX_ARMOR = c.MAX_ARMOR + query
        #     await message.channel.send(f"{char}'s ARMOR changed to {c.ARMOR}/{c.MAX_ARMOR}")
        elif stat == 'a ':
            c.ARMOR = c.ARMOR + query
            await message.channel.send(f"{self.chars[c.CHARACTER_ID]}'s ARMOR changed to {c.ARMOR}")
        else:
            await message.channel.send(f"Unknown stat: {stat}")
        c.save()

        return True

    async def damage(self, message: discord.Message, query, **_):
        query = int(query)
        char = message.content[2:4].upper()
        if char not in self.chars:
            await message.channel.send(f"Character {char} not found.")
            return False

        c: Character
        c = self.characters[char]
        dmg = max(query - c.ARMOR, 0)
        c.HP = c.HP - dmg
        c.save()
        await message.channel.send(f"{self.chars[c.CHARACTER_ID]} took {dmg}! They now have {c.HP}/{c.MAX_HP} health.")



    async def setrole(self, message, char, role, **_):
        char = char.upper()
        if char not in self.chars:
            await message.channel.send(f"Character {char} not found.")
            return False
        c = self.characters[char]
        c.ROLE = role
        c.save()
        await message.channel.send(f"Character {self.chars[c.CHARACTER_ID]} is now represented by <@&{role}>.")

        return True

    async def listroles(self, message, **__):
        table = []

        for c in self.characters.values():
            if c.ROLE:
                table.append([f"`{c.CHARACTER_ID}`", f'<@&{c.ROLE}>'])
            else:
                table.append([f"`{c.CHARACTER_ID}`", 'UNASSIGNED'])

        await message.channel.send(c__lib.format_table(table))

    async def stats(self, message: discord.Message, **_):
        roles = message.author.roles

        table = []
        for c in self.characters:
            for r in message.author.roles:
                if r.id == c.ROLE:
                    t = c__lib.format_table(
                            header=["CHAR", "HP", "ARMOR"],
                            table=[[self.chars[c.CHARACTER_ID], f"{c.HP}/{c.MAX_HP}", f"{c.ARMOR}"]]
                        )

                    await message.channel.send(
                        f"```"
                        f"{t}"
                        f"```"
                    )
                    return True

            table.append([self.chars[c.CHARACTER_ID], f"{c.HP}/{c.MAX_HP}", f"{c.ARMOR}"])

        t = c__lib.format_table(
                header=["CHAR", "HP", "ARMOR"],
                table=table
            )

        await message.channel.send(
            "```"
            rf"{t}"
            "```"
        )

        return True
