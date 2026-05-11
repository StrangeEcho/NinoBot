from typing import Optional

import discord
from core import NinoBot, NinoContext
from discord.ext import commands
from utils import ButtonPaginator, Project, VercelClient


class Vercel(commands.Cog):
    def __init__(self, bot: NinoBot):
        self.bot = bot
        self.vercel_client: VercelClient = VercelClient(
            self.bot.config.get("vercel_token")
        )

    @commands.command()
    @commands.is_owner()
    async def projectlist(self, ctx: NinoContext):
        """Recieve Information about current Vercel projects"""

        embeds: list[Optional[discord.Embed]] = []
        projects: Project = await self.vercel_client.get_projects()
        for idx, project in enumerate(projects, 1):
            embeds.append(
                discord.Embed(title=project.name, color=self.bot.ok_color)
                .add_field(name="ID", value=f"`{project.id}`")
                .add_field(name="Framework", value=f"`{project.framework}`")
                .add_field(name="Domain", value=f"`{project.production_domain[0]}`")
                .add_field(
                    name="Deployment Status",
                    value="`Deployed`" if project.is_deployed else "`Inactive`",
                )
                .set_footer(text=f"Page {idx} of {len(projects)}")
            )
        paginator = ButtonPaginator(embeds)
        await paginator.start(ctx.channel)


async def setup(bot: NinoBot):
    await bot.add_cog(Vercel(bot))
