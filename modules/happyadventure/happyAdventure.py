import asyncio
import random
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
            Command(
                names=['hp'],
                function=self.character_edit_hp,
                description='Add, remove or set health.',
                positional_parameters=OrderedDict([
                    ('mention', '__mention__?'),
                    ('query', r'__number__')
                    ])
            )
        )

        self.addcom(
            CommandTree(
                names=['character', 'char', 'characters', 'chars'],
                description='Manage characters.',
                children=[
                    Command(
                        names=['create'],
                        function=self.character_create,
                        positional_parameters={
                            'name': '__any__'},
                        named_parameters={
                            'description': '__any__',
                            'hp': '__number__',
                            'max_hp': '__number__',
                            'armor': '__number__',
                        }
                    ),
                    Command(
                        names=['select'],
                        function=self.character_select,
                        description='Select a chalacter.',
                        positional_parameters={
                            'query': '__any__??'
                        },
                        named_parameters={
                            'name': '__any__',
                            'id': '__integer__'
                        }
                    ),
                    Command(
                        names=['list'],
                        function=self.character_list,
                        description='List your characters',
                        flags={
                            'all': 'all'
                        },
                        positional_parameters={
                            'mention': '__mention__?'
                        }
                    ),
                    Command(
                        names=['info'],
                        function=self.character_info,
                        description='Display character info.',
                        positional_parameters={
                            'mention': '__mention__?'
                        }
                    ),
                    Command(
                        names=['edit'],
                        function=self.character_edit,
                        description='Edit character',
                        positional_parameters={
                            'mention': '__mention__?'
                        },
                        named_parameters={
                            'max_hp': '__number__',
                            'hp': '__number__',
                            'armor': '__number__',
                            'description': '__any__',
                        }
                    )
                ]
            )
        )

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

    async def character_create(self, message: discord.Message, name, description, hp, armor, max_hp, **__):
        char: Character

        hp = int(hp) if hp else 0
        armor = int(armor) if armor else 0

        char = self.characters.create(
            USER_ID=message.author.id,
            SERVER_ID=message.guild.id,
            NAME=name,
            DESCRIPTION=description,
            HP=hp,
            MAX_HP=max_hp,
            ARMOR=armor
        )

        current = self.characters.get_selected(message.author.id, message.guild.id)

        if current is not None:
            return await message.channel.send(
                f'Character "{char.NAME}" created. (id={char.CHARACTER_ID})\n'
                f'You may want to select it: !character select id={char.CHARACTER_ID}')
        else:
            self.characters.select(
                character_id=char.CHARACTER_ID, user_id=message.author.id, server_id=message.guild.id)

            return await message.channel.send(
                f'Character "{char.NAME}" created. It got automatically selected. (id={char.CHARACTER_ID})')

    async def character_select(self, query, id, name, message: discord.Message, **__):
        try:
            user_id = message.author.id
            id = int(id) if id else None

            found = self.characters.search(query=query, character_id=id, name=name, user_id=user_id)

            if found is None or len(found) == 0:
                return await message.channel.send(f'No characters found.')

            if len(found) == 1:
                current = self.characters.get_selected(user_id, message.guild.id)

                if current is not None and current == found[0]:
                    return await message.channel.send(f'Character "{found[0].NAME}" was already active.')

                self.characters.select(character_id=found[0].CHARACTER_ID, user_id=user_id, server_id=message.guild.id)
                return await message.channel.send(f'Character "{found[0].NAME}" set as active for you.')

            if len(found) > 1:
                header = ['id', 'name', 'description']
                t = [[c.CHARACTER_ID, c.NAME, c.DESCRIPTION] for c in found]
                return await message.channel.send(
                    f'Please choose one of following by id:\n{format_table(header=header, table=t)}')

        except Exception as ex:
            return await message.channel.send(f'character_select error: {ex}')

    async def character_list(self, message: discord.Message, mention, all, **__):

        server_id = None if all else message.guild.id

        user_id = message.author.id if mention is None else message.mentions[0].id

        found = self.characters.search(user_id=user_id, server_id=server_id)

        if len(found) == 0:
            return await message.channel.send(f'No characters.')

        header = ['id', 'name', 'description']
        t = [[c.CHARACTER_ID, c.NAME, c.DESCRIPTION] for c in found]

        return await message.channel.send(f'```{format_table(header=header, table=t)}```')

    async def character_info(self, message: discord.Message, mention, **__):
        user = message.mentions[0] if mention else message.author

        char = self.characters.get_selected(user.id, message.guild.id)

        if char is None:
            return await message.channel.send(f'No character selected.')
        else:
            return await message.channel.send('```' + char.info_page() + '```')

    async def character_edit(self, message: discord.Message, mention, max_hp, hp, armor, description, **__):
        user = message.author if mention is None else message.mentions[0]
        char = self.characters.get_selected(user.id, message.guild.id)
        if char is None:
            return await message.channel.send(f'No character selected.')

        char.MAX_HP = max_hp or char.MAX_HP
        char.HP = hp or char.HP
        char.ARMOR = armor or char.ARMOR
        char.DESCRIPTION = description or char.DESCRIPTION
        char.save()

        return await message.channel.send(char.info_page())

    async def character_edit_hp(self, message: discord.Message, mention, query, **__):
        user = message.author if mention is None else message.mentions[0]
        char = self.characters.get_selected(user.id, message.guild.id)
        if char is None:
            return await message.channel.send(f'No character selected.')

        old_hp = char.HP
        new_hp = old_hp
        query: str
        if query[0] in ['+', '-']:
            new_hp = old_hp + int(query)
        else:
            new_hp = int(query)

        if new_hp > char.MAX_HP:
            new_hp = char.MAX_HP

        char.HP = new_hp
        char.save()

        if new_hp == old_hp:
            return await message.channel.send(f"{char.NAME}'s health didn't change. They have {new_hp} now.")
        elif new_hp > old_hp:
            return await message.channel.send(f"{char.NAME}'s gained {new_hp - old_hp} health. They have {new_hp} now.")
        elif new_hp <= 0:
            return await message.channel.send(f"{char.NAME}'s lost {new_hp - old_hp} health. They **DIED**.")
        else:
            return await message.channel.send(f"{char.NAME}'s lost {old_hp - new_hp} health. They have {new_hp} now.")
