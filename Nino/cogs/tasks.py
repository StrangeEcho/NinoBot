import asyncio
import logging
from itertools import cycle

import discord
from core import NinoBot
from discord.ext import commands, tasks
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class Tasks(commands.Cog):
    def __init__(self, bot: NinoBot):
        self.bot = bot

        self.logger = logging.getLogger("Nino.Tasks")

        self.activities = cycle(
            [
                discord.Game("with your feelings"),
                discord.Activity(
                    type=discord.ActivityType.listening,
                    name="to music with your mom",
                ),
                discord.Game(
                    f"with {len(self.bot.users)} users",
                ),
            ]
        )

        self.activity_cycler.start()

    def cog_unload(self):
        self.activity_cycler.cancel()

    @tasks.loop(minutes=6)
    async def activity_cycler(self):

        activity = next(self.activities)

        await self.bot.change_presence(activity=activity)

        activity_table = Table(
            title="[bold purple]Presence Updated",
            border_style="purple",
            show_header=False,
        )

        activity_table.add_row(
            "[bold cyan]Activity Type",
            str(activity.type).split(".")[-1].title(),
        )

        activity_table.add_row(
            "[bold cyan]Activity Name",
            activity.name,
        )

        console.print(activity_table)

    @activity_cycler.before_loop
    async def before_activity_cycler(self):

        loading_panel = Panel.fit(
            (
                "[bold yellow]Waiting for On Ready[/bold yellow]\n\n"
                "Activity cycler will start automatically."
            ),
            title="[bold white]Tasks",
            border_style="yellow",
        )

        console.print(loading_panel)

        await self.bot.wait_until_ready()

        ready_panel = Panel.fit(
            "[bold green]✓ Activity cycler initialized successfully",
            title="[bold white]Tasks",
            border_style="green",
        )

        console.print(ready_panel)

    @activity_cycler.error
    async def activity_cycler_error(
        self,
        error: Exception,
    ):

        self.logger.exception("Activity cycler encountered an error")

        console.print(
            Panel.fit(
                (f"[bold red]{error.__class__.__name__}[/bold red]\n\n" f"{error}"),
                title="[bold white]Task Failure",
                border_style="red",
            )
        )


async def setup(bot: NinoBot):
    await bot.add_cog(Tasks(bot))
