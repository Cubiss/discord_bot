import random
import cubot
from classes.module import *
from classes.service import Service
from classes.users import User


class HappyAdventureModule(Module):
    def __init__(self, **kwargs):
        super().__init__("happyAdventure", **kwargs)

        self.channel = None

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
                function=self.rollstats,
                usage='__author__ Usage: !roll [n]d[n] [+bonus]',
                description='Rolls the dice. '
            )
        )

        self.addcom(
            Command(
                names=['send'],
                regexp=r'^__name__\s*(\<\#(?P<channel>\d*)\>)?\s*(?P<text>(.|\n)*)?$',
                function=self.send,
                usage='__author__ Usage: !roll [#channel] Your message.',
                description='Sends a message in a channel.'
            )
        )

        self.addcom(
            Command(
                names=['setsend', 'sendset'],
                regexp=r'^__name__\s*\<\#(?P<channel>\d*)\>\s*(?P<text>.*)?$',
                function=self.setsend,
                usage='__author__ Usage: !setsay #channel',
                description='Sets a channel for !say command.'
            )
        )

    async def roll(self, message: discord.Message, count, faces, bonus, **__) -> bool:
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

    async def rollstats(self, count, faces, bonus):
        max_roll = faces * count
        probabilities = []
        for i in range(1, 20):
            probabilities[i] = 1

        print(probabilities)

    async def send(self, message: discord.Message, client: cubot.Cubot, channel, text: str,  **__):
        if text is None or text == '' or text.isspace():
            await message.channel.send(f"You need to tell me what to say.")
            return 0

        if channel is None:
            if self.channel is None:
                await message.channel.send(f"You need to mention a #channel or set it globally via !setsend #channel")
                return 0
            else:
                await self.channel.send(text)
                return 0

        channel = int(channel)
        for ch in message.guild.channels:
            if ch.id == channel:
                await ch.send(text)
                return 0
        else:
            await message.channel.send(f"Could not find channel: {channel}. Maybe I don't have access?")
            return 0

    async def setsend(self, message: discord.Message, channel, **__):
        for ch in message.guild.channels:
            if ch.id == int(channel):
                self.channel = ch
                await message.channel.send(f"Set current channel to {ch.name}")
                break
        else:
            await message.channel.send(f"Could not find channel: {channel}. Maybe I don't have access?")