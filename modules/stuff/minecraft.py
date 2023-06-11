from classes.module import *
from classes.service import Service
from modules.users.users import User


class MinecraftModule(Module):
    def __init__(self, **kwargs):
        super().__init__(
            "minecraft",
            description="Minecraft server manager",
            **kwargs)

        self.addcom(
            Command(names=['minecraft'], function=self.minecraft,
                    description='Displays minecraft server\'s address.',
                    help_scope=Command.HELP_SCOPE_GLOBAL
                    )
        )

    async def minecraft(self, message: discord.Message, user: User,  **__) -> bool:
        s = Service('minecraft.service', use_dbus=False)

        running = True
        status = ''
        address = 'cubiss.cz'
        from subprocess import CalledProcessError
        try:
            running = s.is_running()
            status = s.status_string()
        except CalledProcessError:
            pass

        if running:
            await message.channel.send(f'Minecraft server is running on {address}:\n{status})')
        else:
            await message.channel.send(f'Minecraft server is not running. Use "!minecraft start" to start it.\n'
                                       f'It will run on {address}.')
        return True
