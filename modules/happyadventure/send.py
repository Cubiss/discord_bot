from collections import OrderedDict

import c__lib

import cubot
from classes.module import *
from .sendChannels import SendChannel, SendChannels


class SendModule(Module):
    def __init__(self, **kwargs):
        super().__init__("send", **kwargs)
        self.recently_sent_texts = []
        self.recently_sent_messages = []
        self.channel = None

        self.addcom(
            Command(names=['send'],
                    function=self.send, usage='__author__ Usage: !roll [#channel] Your message.',
                    description='Sends a message in a channel.',
                    positional_parameters=OrderedDict([
                        ('_channel', r'(\<\#(?P<channel>\d*)\>)?'),
                        ('text', r'(.|\n)*')
                    ])
                    )
        )

        self.addcom(
            Command(names=['setsend', 'sendset'],
                    function=self.setsend, usage='__author__ Usage: !setsay #channel',
                    description='Sets a channel for !say command.',
                    positional_parameters={
                        '_channel': r'(\<\#(?P<channel>\d*)\>)',
                    })
        )

        self.addcom(
            Command(names=['setsendchannel'],
                    function=self.setsendchannel,
                    description='Sets source channel from which all messages will be mirrored to target channel.',
                    positional_parameters=OrderedDict([
                        ("source", "__channel__"),
                        ("target", "__channel__"),
                    ])
                    )
        )

        self.addcom(
            Command(names=['removesendchannel'],
                    function=self.removesendchannel,
                    description='Removes sendchannel.',
                    positional_parameters=OrderedDict([
                        ("scid", "__number__")
                    ])
                    )
        )

        self.addcom(
            Command(names=['listsendchannels'],
                    function=self.listsendchannels,
                    description='Lists sendchannels.'
                    )
        )

        self.sendchannels = SendChannels(self.db)
        self.sendchannels.load()

    async def on_message(self, message: discord.Message):
        await super().on_message(message)

        if message.content in self.recently_sent_texts:
            self.recently_sent_messages.append(message)
            self.recently_sent_texts.remove(message.content)

        if message.content.startswith(self.client.command_character):
            return

        for sc in self.sendchannels.values():
            if message.channel.id == sc.SOURCE_CHANNEL:
                await self.client.get_channel(sc.TARGET_CHANNEL).send(message.content)

    async def send(self, message: discord.Message, channel, text: str, **__):
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

    async def setsendchannel(self, message: discord.Message, source, target, **__):
        for sc in self.sendchannels.values():
            if sc.SOURCE_CHANNEL == source and sc.TARGET_CHANNEL == target:
                await message.channel.send(f"This link already exists (id={sc.SENDCHANNEL_ID})")

        sc = self.sendchannels.create(SOURCE_CHANNEL=source, TARGET_CHANNEL=target)

        await message.channel.send(f"SendChannel {sc.SENDCHANNEL_ID} added.")

    async def removesendchannel(self, message, scid, **__):
        self.sendchannels.delete(int(scid))
        await message.channel.send(f"SendChannel {scid} removed.")

    async def listsendchannels(self, message, **__):
        table = []
        for sc in self.sendchannels.values():
            table.append([sc.SENDCHANNEL_ID, sc.SOURCE_CHANNEL, sc.TARGET_CHANNEL])

        if len(table) == 0:
            await message.channel.send("No SendChannels.")

        header = ["SENDCHANNEL_ID", "SOURCE_CHANNEL", "TARGET_CHANNEL"]

        await message.channel.send(
            c__lib.format_table(header=header, table=table)
        )
