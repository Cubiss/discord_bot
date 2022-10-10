from classes.module import *


class UtilitiesModule(Module):
    def __init__(self, **kwargs):
        super().__init__("utilities", **kwargs)

        self.addcom(
            Command(
                names=['profilepicture', 'profilepic', 'pp'],
                regexp=r'^__name__(\s*<@!?(?P<mention>\d*?)\s*(?P<global>-g|--global|-global)?>)?\s*$',
                function=self.profile_picture,
                usage='__author__ Usage: !profilepicture [@mention][--global]',
                description='Displays profile picture of you or a mentioned user.'
            )
        )

        self.addcom(
            Command(
                names=['get_id'],
                regexp=r'^__name__(\s+<@!?(?P<mention>\d*?)>)?$',
                function=self.get_user_id,
                usage='__author__ Usage: !get_id <@mention>',
                description='Displays discord id of mentioned user. (For devs mainly.)'
            )
        )

        self.addcom(
            Command(
                names=['user_list'],
                regexp=r'^__name__(?P<id>.*)?$',
                function=self.get_user_id,
                usage='__author__ Usage: !get_id <@mention>',
                description='Displays discord id of mentioned user. (For devs mainly.)'
            )
        )

    async def profile_picture(self, message: discord.Message, **kwargs) -> bool:
        """
        Displays full sized profile picture of either user or a mentioned member.
        :param message:
        :param kwargs:
        :return:
        """

        if kwargs['mention'] is not None:
            user = message.guild.get_member(int(kwargs['mention']))
        else:
            user = message.author

        use_global = False
        if kwargs['global'] is not None:
            use_global = True

        embed = discord.Embed(
            title=f'{user.name}\'s profile picture.',
            # description='{}\'s profile picture.'.format(user.mention) , color=0xecce8b
        )
        if use_global:
            embed.set_image(url=user.avatar_url)
        else:
            embed.set_image(url=user.default_avatar_url)

        await message.channel.send(
            '',
            embed=embed
        )

        return True

    async def get_user_id(self, message: discord.Message, **kwargs):
        """
        Displays ID of either user or a mentioned member.
        :param message:
        :param kwargs:
        :return:
        """
        if kwargs['mention'] is None:
            user = message.author
        else:
            user = message.guild.get_member(int(kwargs['mention']))

        await message.channel.send(
            f'{str(user)}\'s id: {user.id}'
        )
        return True

    async def list_role_members(self, message: discord.Message, id, **kwargs):
        members = message.guild.members

        print(id)

        for m in members:
            print(m)
