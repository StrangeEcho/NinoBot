from discord.ext import commands
import discord

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .nino import NinoBot

class NinoContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot: NinoBot
    
    async def send_ok(self, content: str) -> discord.Message:
        return await self.send(
            embed=discord.Embed(
                description=content,
                color=self.bot.ok_color
            )
        )

    async def send_error(self, content: str) -> discord.Message:
        return await self.send(
            embed=discord.Embed(
                description=content,
                color=self.bot.error_color
            )
        )
    
    