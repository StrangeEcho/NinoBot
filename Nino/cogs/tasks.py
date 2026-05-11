import asyncio
import logging
from itertools import cycle

import discord
from core import NinoBot
from discord.ext import commands, tasks


class Tasks(commands.Cog):
    def __init__(self, bot: NinoBot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.activity_cycler.start()

    @tasks.loop()
    async def activity_cycler(self):
        activities = [
            discord.Game("with your feelings"),
            discord.Activity(
                type=discord.ActivityType.listening, name="to music with your mom"
            ),
            discord.Game(f"with {len(self.bot.users)} users"),
        ]
        await self.bot.wait_until_ready()
        for act in cycle(activities):
            await self.bot.change_presence(activity=act)
            self.logger.info(f"Changed bot activity to: {act}")
            await asyncio.sleep(360)


async def setup(bot: NinoBot):
    await bot.add_cog(Tasks(bot))
