from classes.module import *
from classes.cubot import Cubot


class AdministrationModule(Module):
    def __init__(self, **kwargs):
        super().__init__("administration", **kwargs)
        self.addcom(
            Command(
                names=['test', 't'],
                regexp=r'^__name__(.*)?$',
                function=self.test,
                usage='__author__ Usage: !profilepicture [@mention]',
                description='Test command.',
                permissions=['admin']
            )
        )

        self.addcom(
            Command(
                names=['change_username', 'cu'],
                regexp=r'^__name__ (?P<name>.*)$',
                function=self.change_username,
                usage=f'__author__ Usage: !change_username <username>',
                description='Changes the bot''s username.',
                permissions=['admin']
            )
        )

        self.addcom(
            Command(
                names=['permissions', 'permission'],
                regexp=r'^__name__\s+(?P<command>add|remove|list)(\s+<@!?(?P<mention>\d*?)>)?(\s+(?P<permission>.*?))?$',
                function=self.permissions,
                usage=f'__author__ Usage: !permissions <add|remove|list> [@who] [permission]',
                description='Change permissions.'
            )
        )

    async def test(self, message: discord.Message, **__):
        self.log(message.content)
        pass

    async def change_username(self, message: discord.Message, client: Cubot, **__) -> bool:
        await client.user.edit(username="Karel")
        await message.channel.send(f'Yes, master.')

        return True

    async def permissions(self, message: discord.Message, client: Cubot, **kwargs) -> bool:
        from classes.users import Users, User
        cmd = kwargs['command']
        mention: discord.Member
        mention = message.mentions[0] if len(message.mentions) > 0 else None
        permission = kwargs['permission']

        u: User
        ul: Users = client.user_list

        if cmd == 'add':
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
        elif cmd == 'remove':
            u = ul[mention.id]
            if u is None or permission not in u.permissions:
                await message.channel.send(f"{mention.display_name} doesn't have '{permission}' permission.")
            else:
                u.permissions.remove(permission)
                u.save()
                await message.channel.send(
                    f"Removed '{permission}' permission from {mention.nick or mention.display_name}")
        elif cmd == 'list':
            if mention is not None:
                u = ul[mention.id]
                if u is None or len(u.permissions) == 0:
                    await message.channel.send(f"{mention.nick or mention.display_name} has no permissions.")
                else:
                    await message.channel.send(f"{mention.nick or mention.display_name}'s permissions:\n"
                                               f"{', '.join(u.permissions)}")
            if permission is not None:
                users = [u.name for u in ul if u.has_permission(permission)]
                if len(users) == 0:
                    await message.channel.send(f"Nobody has '{permission}' permission.")
                else:
                    await message.channel.send(f"Users with '{permission}' permissions:\n"
                                               f"{', '.join(users)}")
            pass
        else:
            await message.channel.send(f"Wrong command: '{cmd}'. Only one of following is available: add, remove, list")

        return True

    async def role_manager(self, message: discord.Message, **__) -> bool:

        return True