import platform
import random
from datetime import datetime

import discord
from core import NinoBot, NinoContext
from discord.ext import commands
from utils import humanize_timedelta


class Meta(commands.Cog):
    """Commands more related to the Nino itself"""

    def __init__(self, bot: NinoBot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.is_owner()
    async def logout(self, ctx: NinoContext):
        """Logout/Close the bot process"""
        await ctx.send("Logging out now...")
        await self.bot.close()

    @commands.hybrid_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx: NinoContext):
        """Return back bots message and websocket latency"""
        msg: discord.Message = await ctx.send("Measuring now...")

        msg_latency: float = round(
            (msg.created_at - ctx.message.created_at).total_seconds() * 1000, 2
        )
        ws_latency: float = round(self.bot.latency * 1000, 2)

        await msg.edit(
            content="Finished Measuring...",
            embed=discord.Embed(title="Measured Latency", color=discord.Color.green())
            .add_field(
                name="Websocket / Gateway",
                value=f"{ws_latency}ms",
            )
            .add_field(name="Message Latency", value=f"{msg_latency}ms"),
        )

    @commands.hybrid_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx: NinoContext):
        """Information about the bot"""
        await ctx.send(
            embed=discord.Embed(
                title="Hi again! Heres sum info about me",
                description="First and foremost [this](https://github.com/StrangeEcho/NinoBot) right here is my source code",
                color=self.bot.ok_color,
            )
            .set_thumbnail(url=self.bot.user.display_avatar.url)
            .set_footer(
                text=f"This bot was made using discord.py {discord.__version__} and Python version {platform.python_version()}",
                icon_url=ctx.author.display_avatar.url,
            )
            .add_field(
                name="Guilds | Users",
                value=f"Guilds: {len(self.bot.guilds)} | Users: {len(self.bot.users)}",
            )
            .add_field(
                name="Uptime", value=discord.utils.format_dt(self.bot.start_time, "T")
            )
            .add_field(
                name="Owner(s)",
                value="\n".join(
                    [str(self.bot.get_user(oid)) for oid in self.bot.owner_ids]
                ),
            )
            .add_field(
                name="Cogs | Commands",
                value=f"Cogs: {len(self.bot.cogs)} | Commands: {len(self.bot.commands)}",
            )
            .add_field(
                name="Latency",
                value=f"{round(self.bot.latency * 1000)}ms",
                inline=False,
            )
        )

    @commands.hybrid_command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def uptime(self, ctx: NinoContext):
        """Return the bots current uptime since startup"""
        uptime = humanize_timedelta(datetime.now() - self.bot.start_time, precise=True)
        await ctx.send_ok(f"Current Uptime: `{uptime}`")


async def setup(bot: NinoBot):
    await bot.add_cog(Meta(bot))
