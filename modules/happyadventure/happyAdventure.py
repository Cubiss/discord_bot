import asyncio
import random
from classes.module import *
from .characters import Characters, Character


class HappyAdventureModule(Module):
    def __init__(self, **kwargs):
        super().__init__("happyAdventure", **kwargs)

        self.channel = None

        self.addcom(
            Command(names=['roll', 'r'],
                    function=self.roll, usage='__author__ Usage: !roll [n]d[n] [+bonus]',
                    description='Rolls the dice. ',
                    positional_parameters={
                        'dice': r'((?P<count>\d*)d(?P<faces>\d+))?',
                        'bonus_info': r'((?P<bonus_sign>\+|\-)(?P<bonus>\d*))?'
                    }
                    )
        )

        self.addcom(
            Command(
                names=['character create', 'char create'],
                function=self.character_create,
                positional_parameters=['name'],
                optional_parameters=['description', 'hp', 'armor']
            )
        )

        self.characters = Characters(self.db)
        self.characters.load()

    async def roll(self, message: discord.Message, count, faces, bonus, log, **__) -> bool:
        try:
            if count is None or count == '':
                count = 1
            else:
                count = abs(int(count))

            faces = abs(int(faces))

            if bonus is None or bonus == '':
                bonus = 0
            else:
                bonus = abs(int(bonus))

            if count > 100000:
                await message.channel.send(f'For real?!')
        except:
            return False

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

    async def character(self, command, **kwargs):
        try:
            command = command.lower()

            if command == 'create':
                await self.character_create(**kwargs)
                pass
            elif command == 'select':
                pass
            else:
                raise Exception(f"Unknown command: {command}")
        except Exception as ex:
            pass

    async def character_create(self, message: discord.Message, name, description, hp, armor, **__):
        char: Character
        char = self.characters.create()
        char.USER_ID = message.author.id
        char.NAME = name
        char.DESCRIPTION = description
        char.HP = hp
        char.ARMOR = armor
        char.save()
