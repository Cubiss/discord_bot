from collections import OrderedDict

from c__lib import format_table

from classes.module import *
from classes.cubot import Cubot

from modules.users.users import Users, User


class AdministrationModule(Module):
    def __init__(self, **kwargs):
        super().__init__(
            "administration",
            description="Administrative commands",
            default_permissions="admin",
            priority=Module.PRIORITY_MAX,
            **kwargs)
        self.addcom(
            Command(names=['test', 't'], function=self.test,
                    usage='__author__ Usage: !test __any__', description='Test command.',
                    positional_parameters=OrderedDict([
                        ("msgcontent", PARAM_PREFAB_ANY)
                    ]))
        )

        self.addcom(
            Command(names=['change_username', 'cu'], function=self.change_username,
                    positional_parameters={'name': PARAM_PREFAB_ANY},
                    usage=f'__author__ Usage: !change_username <username>', description='Changes the bot''s username.')
        )

        self.addcom(
            CommandTree(
                names=['permission', 'permissions'],
                description='Manage permissions',
                children=[
                    Command(
                        names=['add'],
                        function=self.add_permission,
                        positional_parameters=OrderedDict([
                            ('mention', PARAM_PREFAB_MENTION),
                            ('permission', PARAM_PREFAB_ANY)
                            ])
                    ),
                    Command(
                        names=['remove'],
                        function=self.remove_permission,
                        positional_parameters=OrderedDict([
                            ('mention', PARAM_PREFAB_MENTION),
                            ('permission', PARAM_PREFAB_ANY)
                        ])
                    ),
                    Command(
                        names=['list'],
                        function=self.list_permissions,
                        named_parameters={
                            'mention': PARAM_PREFAB_MENTION,
                            'permission': PARAM_PREFAB_ANY
                        }
                    )
                ]
            )
        )

    async def test(self, message: discord.Message, **__):
        print(message.content)
        pass

    async def change_username(self, message: discord.Message, client: Cubot, **__) -> bool:
        await client.user.edit(username="Karel")
        await message.channel.send(f'Yes, master.')

        return True

    async def add_permission(self, message: discord.Message, client: Cubot, permission, **kwargs):
        u: User
        ul: Users = client.user_list

        mention: discord.Member
        mention = message.mentions[0] if len(message.mentions) > 0 else None

        u = ul.get_or_create(mention)
        if permission is None:
            await message.channel.send(f"Usage: !permissions add @who permissoin")
            return False
        if permission in u.permissions:
            await message.channel.send(f"{mention.nick or mention.display_name} already has that permission.")
            return True
        u.permissions.append(permission)
        u.save()
        await message.channel.send(f"Added '{permission}' permission to {mention.nick or mention.display_name}")

    async def remove_permission(self, message: discord.Message, client: Cubot, permission, **kwargs):
        u: User
        ul: Users = client.user_list

        mention: discord.Member
        mention = message.mentions[0] if len(message.mentions) > 0 else None

        u = ul[mention.id]
        if u is None or permission not in u.permissions:
            await message.channel.send(f"{mention.display_name} doesn't have '{permission}' permission.")
        else:
            u.permissions.delete(permission)
            u.save()
            await message.channel.send(
                f"Removed '{permission}' permission from {mention.nick or mention.display_name}")

    async def list_permissions(self, message: discord.Message, client: Cubot, permission, **kwargs):
        u: User
        ul: Users = client.user_list

        mention: discord.Member
        mention = message.mentions[0] if len(message.mentions) > 0 else None

        if mention is not None:
            u = ul[mention.id]
            if u is None or len(u.permissions) == 0:
                await message.channel.send(f"{mention.nick or mention.display_name} has no permissions.")
            else:
                await message.channel.send(f"{mention.nick or mention.display_name}'s permissions:\n"
                                           f"{', '.join(u.permissions)}")
        elif permission is not None:
            users = [u.USER_NAME for u in ul if u.has_permission(permission)]
            if len(users) == 0:
                await message.channel.send(f"Nobody has '{permission}' permission.")
            else:
                await message.channel.send(f"Users with '{permission}' permissions:\n"
                                           f"{', '.join(users)}")
        else:
            await message.channel.send(f"You must specify permission_id or user.")
