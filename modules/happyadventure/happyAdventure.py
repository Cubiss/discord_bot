import random

from classes.module import *
from classes.service import Service
from classes.users import User


class HappyAdventureModule(Module):
    def __init__(self, **kwargs):
        super().__init__("happyAdventure", **kwargs)

        self.addcom(
            Command(
                names=['roll', 'r'],
                regexp=r'^__name__(\s*(?P<dice>(?P<count>\d*)d(?P<faces>\d+))\s*((?P<bonus_sign>\+|\-)(?P<bonus>\d*))?)?$',
                function=self.roll,
                usage='__author__ Usage: !roll [n]d[n] [+bonus]',
                description='Rolls the dice. '
            )
        )

        self.addcom(
            Command(
                names=['rollstats', 'rs'],
                regexp=r'^__name__(\s*(?P<dice>(?P<count>\d*)d(?P<faces>\d+))\s*((?P<bonus_sign>\+|\-)(?P<bonus>\d*))?)?$',
                function=self.roll,
                usage='__author__ Usage: !roll [n]d[n] [+bonus]',
                description='Rolls the dice. '
            )
        )

    async def roll(self, message: discord.Message, count, faces, bonus, **__) -> bool:
        try:
            if count is None or count == '':
                count = 1
            else:
                count = int(count)

            faces = int(faces)

            if bonus is None or bonus == '':
                bonus = 0
            else:
                bonus = int(bonus)
        except:
            return False

        rolls = []
        rolls_str = []

        for i in range(0, count):
            result = random.randint(1, faces) + bonus
            rolls.append(result)
            rolls_str.append(str(result))

        bonus_msg = ""
        if bonus > 0:
            bonus_msg = f' with a bonus of {bonus}'

        if len(rolls) == 1:
            await message.channel.send(
                f'Rolling d{faces}{bonus_msg}... Your rolled **{sum(rolls)}**!')
        else:
            await message.channel.send(
                f'Rolling {count}d{faces}{bonus_msg}...\n {"... ".join(rolls_str)}... \nYour result is **{sum(rolls)}**!\nAverage roll was {sum(rolls) / len(rolls)}')

        return True


    async def rollstats(self, count, faces, bonus):
        max_roll = faces * count
        probabilities = []
        for i in range(1, 20):
            probabilities[i] = 1

        print(probabilities)
