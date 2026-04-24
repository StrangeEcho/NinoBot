from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from core.nino import NinoBot


class NinoHelpCommand(commands.HelpCommand):
    """Custom help command for Nino"""

    async def send_bot_help(self, _):
        excluded = ["Jishaku", "Listeners", "Tasks", "Help"]

        bot: NinoBot = self.context.bot

        await self.get_destination().send(
            embed=discord.Embed(
                title=":wave: Hi there I am Nino",
                description=(
                    "I am a private music/utility bot based off the best anime series "
                    "in the world aka Quintissential Quintuplets. uhhhhhhh- and thats basically all"
                ),
                color=bot.ok_color,
            )
            .add_field(
                name="Module List",
                value="\n".join(f"`{cog}`" for cog in bot.cogs if cog not in excluded),
                inline=False,
            )
            .set_footer(
                text=f"Use {self.context.clean_prefix}help <command/module>",
                icon_url=self.context.author.display_avatar.url,
            )
            .set_thumbnail(url=bot.user.display_avatar.url)
        )

    async def send_cog_help(self, cog: commands.Cog):
        bot: NinoBot = self.context.bot

        await self.get_destination().send(
            embed=discord.Embed(
                title=f"Module: `{cog.qualified_name}`",
                description=cog.description or "No description provided.",
                color=bot.ok_color,
            )
            .add_field(
                name=f"Commands ({len(cog.get_commands())}):",
                value=", ".join(f"`{cmd.name}`" for cmd in cog.get_commands())
                or "None",
                inline=False,
            )
            .set_thumbnail(url=bot.user.display_avatar.url)
            .set_footer(
                icon_url=self.context.author.display_avatar.url,
                text=f"Do {self.context.clean_prefix}help <cmd> to get more info on a specific command",
            )
        )

    async def send_command_help(self, cmd: commands.Command):
        bot: NinoBot = self.context.bot

        embed = discord.Embed(
            title=f"Command: `{cmd.qualified_name}`",
            description=cmd.description or "No description provided.",
            color=bot.ok_color,
        )

        embed.add_field(name="Module", value=f"`{cmd.cog_name}`", inline=False)

        # Cooldown
        if cmd._buckets and cmd._buckets._cooldown:
            cd = cmd._buckets._cooldown
            embed.add_field(
                name="Cooldown",
                value=f"Rate: {cd.rate} | Cooldown (seconds): {cd.per}",
                inline=False,
            )

        # Aliases
        if cmd.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join(f"`{alias}`" for alias in cmd.aliases),
                inline=False,
            )

        await self.get_destination().send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot: "NinoBot"):
        bot.help_command = NinoHelpCommand()


async def setup(bot: NinoBot):
    await bot.add_cog(Help(bot))
