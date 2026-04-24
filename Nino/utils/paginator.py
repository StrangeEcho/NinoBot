from asyncio import TimeoutError
from typing import Union

import discord
from discord.ext import commands


class Paginator:
    def __init__(
        self,
        embeds: list[discord.Embed],
    ):
        self.embeds = embeds
        self._index = 0
        self._reactions = ["⬅️", "🗑️", "➡️"]

    async def start(self, ctx: commands.Context) -> None:
        msg = await ctx.send(embed=self.embeds[self._index])
        for reaction in self._reactions:
            await msg.add_reaction(reaction)

        def check(reaction: discord.Reaction, user: discord.User):
            return reaction in self._reactions and user.id == ctx.author.id

        while True:
            try:
                r, u = await ctx.bot.wait_for("reaction_add", check=check, timeout=20)
            except TimeoutError:
                await msg.clear_reactions()
                break
            if r.emoji == "⬅️":
                self.page_left()
                await msg.edit(embed=self.embeds[self._index])
            if r.emoji == "🗑️":
                await msg.clear_reactions()
                break
            if r.emoji == "➡️":
                self.page_right()
                await msg.edit(embed=self.embeds[self._index])

    def page_right(self):
        if self._index != len(self.embeds):
            self._index += 1

    def page_left(self):
        if self._index != 0:
            self._index -= 1
