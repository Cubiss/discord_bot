from collections import OrderedDict

from c__lib import format_table
import random
import datetime

from classes.module import *
from .reactions import Reactions, Reaction


class ReactorModule(Module):
    def __init__(self, **kwargs):
        super().__init__("reactor",
                         description="Make the bot react to messages",
                         **kwargs)

        self.addcom(
            CommandTree(
                names=['reactor'],
                children=[
                    Command(
                        names=['add'],
                        function=self.add_reactor,
                        description='Add a reactor.',
                        flags={
                            'is_global': '-global'},
                        positional_parameters=OrderedDict([
                            ('mention', PARAM_PREFAB_MENTION),
                            ('emote', PARAM_PREFAB_ANY)
                            ]),
                        named_parameters={
                            'chance': PARAM_PREFAB_NUMBER,
                            'cooldown': PARAM_PREFAB_INTEGER
                        }
                    ),
                    Command(
                        names=['list'],
                        flags={
                          'all': 'all'
                        },
                        function=self.list_reactors,
                        description='List all reactors relevant to this server.'
                    ),
                    Command(
                        names=['remove'],
                        function=self.remove_reactor,
                        description='Remove reactor.',
                        positional_parameters={
                            'reactor_id': PARAM_PREFAB_INTEGER
                        }
                    )
                ],
                permissions=['reactor'],
                description='Manage reactors.'
            )
        )

        self.reactions = Reactions(self.db)
        self.reactions.load()

    async def add_reactor(self, message: discord.Message, emote, chance, cooldown, is_global, **__) -> bool:
        if len(message.mentions) == 0:
            await message.channel.send(f'{message.author.mention} you didn\'t mention anyone!')
            return False

        target = message.mentions[0]

        cooldown = 0 if cooldown is None or cooldown == '' else int(cooldown)

        server = message.guild.id if is_global is None else None

        if chance.endswith('%'):
            chance = float(chance.strip('%')) / 100
        else:
            chance = float(chance)

        self.reactions.create(
            USER_ID=target.id,
            USER_NAME=target.name,
            SERVER_ID=server,
            EMOTE=emote,
            CHANCE=chance,
            COOLDOWN=cooldown,
        )

        await message.channel.send(f'{message.author.mention} added a {emote} reactor to {target.mention}'
                                   f' with a chance of {chance * 100}% and cooldown of {cooldown} seconds.')

        return True

    async def remove_reactor(self, message: discord.Message, reactor_id, **__) -> bool:
        try:
            reaction: Reaction
            reaction = self.reactions.delete(int(reactor_id))

            await message.channel.send(f"{message.author.mention} removed {reaction.USER_NAME}'s "
                                       f"{reaction.get_emote()} reactor.")

            return True
        except Exception as ex:
            await message.channel.send(f'{message.author.mention} There was an error: {ex}')

    async def list_reactors(self, message: discord.Message, all, **__) -> bool:
        table = []

        r: Reaction
        for r in self.reactions:
            if all or r.SERVER_ID is None or r.SERVER_ID == message.guild.id:
                table.append(['`' + str(r.ID), r.USER_NAME, str(r.CHANCE), str(r.COOLDOWN), '`' + r.EMOTE])

        if len(table) == 0:
            await message.channel.send(f'There are no reactors present yet.')
            return True

        s = format_table(table, header=['`ID', 'Username', 'Chance', 'Cooldown', 'Emote`'])

        if len(s) > 2000:
            message.channel.send("The list is too long to be displayed in discord. Ping Cubi to finally fix it.")

        await message.channel.send(s)

        return True

    async def on_message(self, message: discord.Message) -> bool:
        r: Reaction
        for reaction in [r for r in self.reactions if r.USER_ID == message.author.id
                         and r.SERVER_ID in (message.guild.id, None)]:
            rnd = random.random()
            # self.log(f'{user_id}: {reaction.chance}|{r}')
            if reaction.CHANCE > rnd:
                if datetime.datetime.now() > reaction.last_used + datetime.timedelta(seconds=reaction.COOLDOWN):
                    await message.add_reaction(emoji=reaction.get_emote())
                    reaction.last_used = datetime.datetime.now()
                    self.log(f"Adding reaction to {message.author.name}: {reaction.ID}")

        return False
