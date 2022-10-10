import asyncio
import random
import cubot
from classes.module import *
from classes.service import Service
from classes.users import User


class SendModule(Module):
    def __init__(self, **kwargs):
        super().__init__("send", **kwargs)
        self.recently_sent_texts = []
        self.recently_sent_messages = []

        self.addcom(
            Command(
                names=['send'],
                regexp=r'^__name__\s*(\<\#(?P<channel>\d*)\>)?\s*(?P<text>(.|\n)*)?$',
                function=self.send,
                usage='__author__ Usage: !roll [#channel] Your message.',
                description='Sends a message in a channel.',
                permissions=['happyadmin']
            )
        )

        self.addcom(
            Command(
                names=['setsend', 'sendset'],
                regexp=r'^__name__\s*\<\#(?P<channel>\d*)\>\s*(?P<text>.*)?$',
                function=self.setsend,
                usage='__author__ Usage: !setsay #channel',
                description='Sets a channel for !say command.',
                permissions=['happyadmin']
            )
        )

    def on_message(self, message: discord.Message):
        super().on_message(message)

        if message.content in self.recently_sent_texts:
            self.recently_sent_messages.append(message)
            self.recently_sent_texts.remove(message.content)

    async def send(self, message: discord.Message, client: cubot.Cubot, channel, text: str, **__):
        if text is None or text == '' or text.isspace():
            await message.channel.send(f"You need to tell me what to say.")
            return 0

        if channel is None:
            if self.channel is None:
                await message.channel.send(
                    f"You need to mention a #channel or set it globally via !setsend #channel")
                return 0
            else:
                await self.channel.send(text)
                return 0

        channel = int(channel)
        for ch in message.guild.channels:
            if ch.id == channel:
                self.recently_sent_texts.append(text)
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


