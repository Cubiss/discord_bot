from classes.module import *


class UtilitiesModule(Module):
    def __init__(self, **kwargs):
        super().__init__(
            "utilities",
            description="Useful commands",
            **kwargs)

        self.addcom(
            Command(names=['profilepicture', 'profilepic', 'pp'],
                    function=self.profile_picture, usage='__author__ Usage: !profilepicture [@mention][--global]',
                    description='Displays zoomable profile picture of you or a mentioned user.',
                    flags={
                        'is_global': '--global'},
                    positional_parameters={
                        'mention': '__mention__?',
                    },
                    help_scope=Command.HELP_SCOPE_GLOBAL
                    )
        )

        self.addcom(
            Command(names=['get_id'], function=self.get_user_id,
                    positional_parameters={
                        'mention': PARAM_PREFAB_MENTION
                    },
                    usage='__author__ Usage: !get_id <@mention>',
                    description='Displays discord id of mentioned user. (For devs mainly.)')
        )

        self.addcom(
            Command(names=['get_server_id'], function=self.get_server_id,
                    usage='__author__ Usage: !get_server_id',
                    description='Displays discord id of current server. (For devs mainly.)')
        )

    async def profile_picture(self, message: discord.Message, mention, is_global, **kwargs) -> bool:
        """
        Displays full sized profile picture of either user or a mentioned member.
        :param message:
        :param kwargs:
        :return:
        """

        if mention is not None:
            user = message.mentions[0]
        else:
            user = message.author

        use_global = True
        if is_global is not None:
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

    async def get_server_id(self, message: discord.Message, **kwargs):
        """
        Displays ID of either user or a mentioned member.
        :param message:
        :param kwargs:
        :return:
        """

        await message.channel.send(
            f'{str(message.guild.name)}\'s id: {message.guild.id}'
        )
        return True
