import logging
import os
import tomllib
import traceback
from datetime import datetime
from typing import Any, Optional

import discord
import wavelink
from discord.ext import commands

from utils import humanize_timedelta

from .context import NinoContext


class NinoConfigHandler:
    """A simple config helper for Nino"""

    with open("./Nino/core/config/config.toml", "rb") as confile:
        config: dict[Any, Any] = tomllib.load(confile)

    def get(self, config_name: str) -> Any:
        """Fetch specified config from config.toml file"""
        return self.config.get(config_name)  # Returns None if no config found


class NinoBot(commands.AutoShardedBot):
    """Nino bot subclass for added functionality"""

    discord.utils.setup_logging(level=logging.INFO)

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("n!"),
            help_command=commands.MinimalHelpCommand(),
            intents=discord.Intents.all(),
        )
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config: NinoConfigHandler = NinoConfigHandler()
        self.owner_ids = set(self.config.get("owner_ids"))
        self.start_time = datetime.now()
        self.ok_color: int = int(self.config.get("ok_color"), 16)
        self.error_color: int = int(self.config.get("error_color"), 16)

    async def on_message(self, message: discord.Message):
        ctx = await self.get_context(message, cls=NinoContext)
        await self.invoke(ctx)

    async def setup_hook(self) -> None:
        self.logger.info("Attempting Connection with Lavalink")
        self.nodes = [wavelink.Node(uri="http://127.0.0.1:2333", password="password1")]
        try:
            await wavelink.Pool.connect(
                nodes=self.nodes, client=self, cache_capacity=100
            )
            self.logger.info("wavelink connection... success")
        except Exception as e:
            self.logger.error(
                f"wavelink connection... failure:\n{''.join(traceback.format_exception(e))}"
            )

    async def startup(self) -> None:
        """Startup method for the bot"""
        self.logger.info(f"Starting Nino (PID {os.getpid()})")
        await self._load_extensions()
        await self.start(self.config.get("token"))

    async def _load_extensions(self) -> None:
        self.logger.info("Attempting to load cogs:")
        for ext in os.listdir("Nino/cogs"):
            if ext.endswith(".py"):
                cog = f"cogs.{ext[:-3]}"
                try:
                    await self.load_extension(cog)
                    self.logger.info(f"{cog}... success")
                except commands.ExtensionError as e:
                    self.logger.warning(
                        f"{cog}... failure\n - {''.join(traceback.format_exception(e))}"
                    )

    async def close(self):
        run_time = humanize_timedelta(datetime.now() - self.start_time)
        await wavelink.Pool.close()
        self.logger.info("Closed Wavelink Node Pool")
        self.logger.info(f"Shutting down Nino now... (Run Time: {run_time})")
        await super().close()

    async def on_ready(self):
        self.logger.info(f"{self.user} is ready!")
