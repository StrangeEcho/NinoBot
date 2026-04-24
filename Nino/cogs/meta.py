import platform
import random

import discord
from core import NinoBot, NinoContext
from discord.ext import commands


class Meta(commands.Cog):
    """Commands more related to the Nino itself"""

    def __init__(self, bot: NinoBot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx: NinoContext):
        """Logout/Close the bot process"""
        await ctx.send("Logging out now...")
        await self.bot.close()

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx: NinoContext):
        msg: discord.Message = await ctx.send("Measuring now...")
        
        msg_latency: float = round((msg.created_at - ctx.message.created_at).total_seconds() * 1000, 2)
        ws_latency: float = round(self.bot.latency * 1000, 2)
        
        await msg.edit(
            content="Finished Measuring...",
            embed=discord.Embed(
                title="Measured Latency",
                color=discord.Color.green()
            )
            .add_field(
                name="Websocket / Gateway",
                value=f"{ws_latency}ms",
            )
            .add_field(
                name="Message Latency",
                value=f"{msg_latency}ms"
            )
        )

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx: NinoContext):
        """Information about the bot itself"""
        await ctx.send(
            embed=discord.Embed(
                title="Hi again! Heres sum info about me",
                description="First and foremost [this](https://github.com/StrangeEcho/NinoBot) right here is my source code",
                color=discord.Color.green(),
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
                name="Uptime", value=discord.utils.format_dt(self.bot.start_time, "R")
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
    
    @commands.command(aliases=["8ball"])
    async def eightball(self, ctx: NinoContext, *, question: str):
        responses = ["yes", "no", "maybe"]
        response = random.choice(responses)
        await ctx.send_ok(f"Question: {question}\nAnswer: {response}")



async def setup(bot: NinoBot):
    await bot.add_cog(Meta(bot))
