import asyncio
import logging
import os
import tomllib
from datetime import datetime
from typing import Any

import discord
import wavelink
from discord.ext import commands
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.traceback import install
from utils import humanize_timedelta

from .context import NinoContext

# Rich Setup
install()

console = Console()

LOG_FORMAT = "%(message)s"

handler = RichHandler(
    console=console,
    rich_tracebacks=True,
    tracebacks_show_locals=True,
    show_time=True,
    show_level=True,
    show_path=False,
    markup=True,
)

discord.utils.setup_logging(
    level=logging.INFO,
    handler=handler,
    formatter=logging.Formatter(LOG_FORMAT),
    root=True,
)

# Reduce noisy discord logs
logging.getLogger("discord.http").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
logging.getLogger("wavelink").setLevel(logging.INFO)


class NinoConfigHandler:
    """A simple config helper for Nino"""

    with open("./Nino/core/config/config.toml", "rb") as confile:
        config: dict[Any, Any] = tomllib.load(confile)

    def get(self, config_name: str) -> Any:
        return self.config.get(config_name)


class NinoBot(commands.AutoShardedBot):
    """Nino bot subclass for added functionality"""

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("n!"),
            help_command=commands.MinimalHelpCommand(),
            intents=discord.Intents.all(),
        )

        self.logger = logging.getLogger("Nino")

        self.config = NinoConfigHandler()

        self.owner_ids = set(self.config.get("owner_ids"))

        self.start_time = datetime.now()

        self.ok_color = int(self.config.get("ok_color"), 16)
        self.error_color = int(self.config.get("error_color"), 16)

    async def on_message(self, message: discord.Message):
        ctx = await self.get_context(message, cls=NinoContext)
        await self.invoke(ctx)

    async def setup_hook(self) -> None:
        self.logger.info("[bold cyan]Connecting to Lavalink...")

        self.nodes = [
            wavelink.Node(
                uri="http://127.0.0.1:2333",
                password="password1",
            )
        ]

        try:
            await wavelink.Pool.connect(
                nodes=self.nodes,
                client=self,
                cache_capacity=None,
            )

            console.print(
                Panel.fit(
                    "[bold green]✓ Wavelink connection successful",
                    border_style="green",
                )
            )

        except Exception:
            self.logger.exception("[bold red]Failed to connect to Lavalink")

        self.logger.info("[bold cyan]Syncing command tree...")

        try:
            synced = await self.tree.sync()

            console.print(
                Panel.fit(
                    f"[bold green]✓ Synced {len(synced)} application commands",
                    border_style="green",
                )
            )

        except Exception:
            self.logger.exception("[bold red]Failed to sync command tree")

    async def startup(self) -> None:
        """Startup method for the bot"""

        startup_text = Text(
            f"Starting Nino (PID {os.getpid()})",
            style="bold purple",
        )

        console.print(
            Panel(
                startup_text,
                title="[bold white]Nino",
                border_style="purple",
                expand=False,
            )
        )

        await self._load_extensions()
        console.print(
            Rule(
                "[bold purple]The Start of Something New",
                style="purple",
            )
        )
        await self.start(self.config.get("token"))

    async def _load_extensions(self) -> None:
        console.print(
            Rule(
                "[bold yellow]Loading Extensions",
                style="yellow",
            )
        )

        loaded = 0
        failed = 0

        for ext in os.listdir("Nino/cogs"):
            if ext.endswith(".py"):
                cog = f"cogs.{ext[:-3]}"

                try:
                    await self.load_extension(cog)

                    loaded += 1

                    console.print(f"[green]✓[/green] Loaded [bold]{cog}[/bold]")

                except commands.ExtensionError:
                    failed += 1

                    self.logger.exception(f"[bold red]Failed loading {cog}")

        console.print(
            Panel.fit(
                (
                    f"[bold green]Loaded:[/bold green] {loaded}\n"
                    f"[bold red]Failed:[/bold red] {failed}"
                ),
                title="[bold white]Extension Summary",
                border_style="cyan",
            )
        )

    async def restart(self):
        """Calls normal Bot.close() to restart because of Systemd keeping the process alive"""
        run_time = humanize_timedelta(
            datetime.now() - self.start_time,
            precise=True,
        )

        await wavelink.Pool.close()

        console.print(
            Panel.fit(
                (
                    "[bold red]Nino restart now[/bold red]\n\n"
                    f"Runtime: [bold white]{run_time}[/bold white]"
                ),
                border_style="red",
            )
        )

        await super().close()  # Systemd will wake the process backup

    async def shutdown(self):
        """True shutdown. Manual cleanup of bot proccess with 0 exit code"""
        run_time = humanize_timedelta(
            datetime.now() - self.start_time,
            precise=True,
        )

        console.print(
            Panel.fit(
                (
                    "[bold red]Nino shutting down[/bold red]\n\n"
                    f"Runtime: [bold white]{run_time}[/bold white]"
                ),
                border_style="red",
            )
        )

        for cog in self.cogs.values():  # Attempt to unload all cogs
            try:
                await cog.cog_unload()
            except:
                pass
        if self.ws and self.ws.open:  # Close WS connection
            await self.ws.close(1000)
        await wavelink.Pool.close()

        await self.http.close()
        exit(0)

    async def on_ready(self):
        console.print(
            Panel.fit(
                (
                    f"[bold green]{self.user}[/bold green]\n"
                    f"Guilds: [bold white]{len(self.guilds)}[/bold white]\n"
                    f"Users: [bold white]{len(self.users)}[/bold white]\n"
                    f"Commands [bold white]{len(self.commands)}[/bold white]"
                ),
                title="[bold purple]Bot Ready",
                border_style="green",
            )
        )
        console.print(Rule(style="purple"))
