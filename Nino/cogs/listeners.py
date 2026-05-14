import logging
import traceback
from datetime import datetime, timezone
from io import BytesIO

import discord
from core import NinoBot
from discord.ext import commands
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class Listeners(commands.Cog):
    def __init__(self, bot: NinoBot):
        self.bot = bot
        self.listener_logger = logging.getLogger("Nino.Listeners")

    async def send_error(
        self,
        ctx: commands.Context,
        content: str,
    ) -> discord.Message:

        return await ctx.send(
            embed=discord.Embed(
                description=content,
                color=discord.Color.red(),
            )
        )

    async def forward_to_owners(
        self,
        ctx: commands.Context,
        e: commands.CommandError,
    ) -> None:

        for oid in self.bot.owner_ids:
            owner = self.bot.get_user(oid)

            if not owner:
                continue
            full_error = "".join(traceback.format_exception(e))
            file_data = BytesIO(full_error.encode())
            file = discord.File(file_data, filename="error.txt")

            try:
                embed = discord.Embed(
                    title="Unexpected Error Caught",
                    description=(
                        f"Error Class: `{e.__class__.__name__}`\n"
                        f"Error Message:\n```py\n{e}\n```"
                    ),
                    color=discord.Color.red(),
                    timestamp=datetime.now(timezone.utc),
                ).add_field(
                    name="Context Information",
                    value=(
                        f"Guild: `{ctx.guild}` (`{ctx.guild.id}`)\n"
                        f"Channel: `{ctx.channel}` (`{ctx.channel.id}`)\n"
                        f"User: `{ctx.author}` (`{ctx.author.id}`)\n\n"
                        f"Usage:\n```py\n{ctx.message.content}\n```"
                    ),
                    inline=False,
                )

                await owner.send(embed=embed, file=file)

            except (discord.Forbidden, discord.HTTPException):
                self.listener_logger.exception("Failed to forward error to bot owner")

    @commands.Cog.listener()
    async def on_command_completion(
        self,
        ctx: commands.Context,
    ):

        execution_time = round(
            (datetime.now(timezone.utc) - ctx.message.created_at).total_seconds()
            * 1000,
            2,
        )

        table = Table(
            title="[bold green]Command Executed",
            border_style="green",
            show_header=False,
        )

        table.add_row(
            "[bold cyan]Command",
            f"{ctx.clean_prefix}{ctx.command.name}",
        )

        table.add_row(
            "[bold cyan]Guild",
            f"{ctx.guild.name} ({ctx.guild.id})",
        )

        table.add_row(
            "[bold cyan]Channel",
            f"{ctx.channel.name} ({ctx.channel.id})",
        )

        table.add_row(
            "[bold cyan]User",
            f"{ctx.author} ({ctx.author.id})",
        )

        table.add_row(
            "[bold cyan]Execution Time",
            f"{execution_time}ms",
        )

        table.add_row(
            "[bold cyan]Usage",
            ctx.message.content,
        )

        console.print(table)

    @commands.Cog.listener()
    async def on_command_error(
        self,
        ctx: commands.Context,
        e: commands.CommandError,
    ):

        msg = None

        if isinstance(e, commands.CommandNotFound):
            return

        elif isinstance(e, commands.MissingPermissions):

            msg = (
                "Insufficient permissions for command:\n"
                f"{', '.join(e.missing_permissions)}"
            )

        elif isinstance(e, commands.NotOwner):

            msg = "This command can only be used " "by the bot owner(s)."

        elif isinstance(e, commands.BotMissingPermissions):

            perms = "\n".join(f"• `{perm}`" for perm in e.missing_permissions)

            msg = "I am missing permissions " f"to execute this command:\n{perms}"

        elif isinstance(e, commands.MissingRequiredArgument):

            msg = f"Missing required argument: `{e.param.name}`"

        elif isinstance(e, commands.CommandOnCooldown):

            msg = (
                "Command is on cooldown.\n"
                f"Retry again after `{round(e.retry_after, 2)}s`"
            )

        else:

            self.listener_logger.exception(f"Unexpected command error in {ctx.command}")

            error_panel = Panel.fit(
                (f"[bold red]{e.__class__.__name__}[/bold red]\n\n" f"{e}"),
                title="[bold white]Unhandled Command Error",
                border_style="red",
            )

            console.print(error_panel)

            msg = f"Unexpected Error Raised\n\n" f"Error Type: `{
                    e.__class__.__name__
                }`\n" f"Message:\n```py\n{e}\n```"

            await self.forward_to_owners(ctx, e)

        await self.send_error(ctx, msg)


async def setup(bot: NinoBot):
    await bot.add_cog(Listeners(bot))
