from classes.module import *


class UtilitiesModule(Module):
    def __init__(self, **kwargs):
        super().__init__("utilities", **kwargs)
        pass

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

        embed = discord.Embed(
            title=f'{user.name}\'s profile picture.',
            # description='{}\'s profile picture.'.format(user.mention) , color=0xecce8b
        )
        embed.set_image(url=user.avatar_url)
        await message.channel.send(
            '',
            embed=embed
        )

        return True

    async def get_user_id(message: discord.Message, **kwargs):
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