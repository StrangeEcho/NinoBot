import logging
import traceback
from datetime import datetime, timezone

import discord
from core import NinoBot
from discord.ext import commands


class Listeners(commands.Cog):
    def __init__(self, bot: NinoBot):
        self.bot = bot
        self.listener_logger = logging.getLogger(__name__)

    async def send_error(self, ctx: commands.Context, content: str) -> discord.Message:
        return await ctx.send(
            embed=discord.Embed(description=content, color=discord.Color.red())
        )

    async def forward_to_owners(
        self, ctx: commands.Context, e: commands.CommandError
    ) -> None:
        for oid in self.bot.owner_ids:
            owner = self.bot.get_user(oid)
            try:
                await owner.send(
                    embed=discord.Embed(
                        title="Unexpected Error Caught",
                        description=f"Error Class: {e.__class__.__name__}\nError Message: {e}",
                        color=discord.Color.red(),
                    ).add_field(
                        name="Context Information",
                        value=f"Guild: {ctx.guild}({ctx.guild.id})\nChannel: {ctx.channel}({ctx.channel.id})\nUser: {ctx.author}({ctx.author.id})\nUsage: {ctx.message.content}",
                    )
                )
            except (discord.Forbidden, discord.HTTPException):
                self.listener_logger.error(f"{e.__class__.__name__}\n{e}")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        self.listener_logger.info(f"""
{ctx.clean_prefix}{ctx.command.name} - Succesfully Executed
Guild: {ctx.guild.name} (ID: {ctx.guild.id})
Channel: {ctx.channel.name} (ID: {ctx.channel.id})
User/Member: {ctx.author.name} (ID: {ctx.author.id})\n
Usage: {ctx.message.content}
Execution Time: {round((datetime.now(timezone.utc) - ctx.message.created_at).total_seconds() * 1000, 2)}ms
----------------------------------------------
        """)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, e: commands.CommandError):

        if isinstance(e, commands.MissingPermissions):
            msg = f"Insufficient Permissions for command:\n {'\n'.join(e.missing_permissions, )}"

        if isinstance(e, commands.NotOwner):
            msg = f"This command is only able to be used by application owner(s)"

        if isinstance(e, commands.BotMissingPermissions):
            msg = f"I am missing permissions to sucessfully execute this command:\n{'\n'.join([f'`{perm}`' for perm in e.missing_permissions])}"

        if isinstance(e, commands.MissingRequiredArgument):
            msg = f"Missing required argument: `{e.param}`"
            
        if isinstance(e, commands.CommandOnCooldown):
            msg = f"Command On Cooldown. Retry again after {e.retry_after}s"

        if isinstance(e, commands.CommandNotFound):
            pass

        else:
            msg = f"Unexpected Error Raised | Error Type: ***{e.__class__.__name__}***\nMessage:\n{e}"
            self.listener_logger.error("".join(traceback.format_exception(e)))
            await self.forward_to_owners(ctx, e)

        await self.send_error(ctx, msg)


async def setup(bot: NinoBot):
    await bot.add_cog(Listeners(bot))
