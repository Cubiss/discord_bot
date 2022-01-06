from classes.module import *


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

    async def test(self, message: discord.Message, **__):
        self.log(message.content)
        pass
