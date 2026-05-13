import discord
import wavelink
from core import NinoBot, NinoContext
from discord.ext import commands
from utils import ButtonPaginator, chunk_iter


class NinoPlayer(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = wavelink.Queue()


class NinoTrackSelector(discord.ui.Select):
    def __init__(self, ctx: NinoContext, tracks: list[wavelink.Playable]):
        self.ctx: NinoContext = ctx
        self.tracks: list[wavelink.Playable] = tracks

        options = []
        for i, track in enumerate(tracks[:5]):
            options.append(
                discord.SelectOption(
                    label=f"{i+1}. {track.title[:50]}",
                    description=f"{track.author[:50]}",
                    value=str(i),
                )
            )

        super().__init__(placeholder="Select a track", options=options)

    def to_embed(self, content: str, embed_type: str) -> discord.Embed:
        return discord.Embed(
            description=content,
            color=(
                self.ctx.bot.ok_color
                if embed_type == "ok"
                else self.ctx.bot.error_color
            ),
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message(
                embed=self.to_embed("You are not able to use this menu", "error"),
                ephemeral=True,
            )

        player: NinoPlayer = self.ctx.voice_client
        track = self.tracks[int(self.values[0])]

        if player.playing:
            player.queue.put(track)
            await interaction.response.send_message(
                embed=self.to_embed(f"Queued: `{track.title}`", "ok"), delete_after=5
            )
        else:
            await player.play(track)
            await interaction.response.send_message(
                embed=self.to_embed(f"Now playing: `{track.title}`", "ok"),
                delete_after=5,
            )


class TrackSelectView(discord.ui.View):
    def __init__(self, ctx: NinoContext, tracks: list[wavelink.Playable]):
        super().__init__(timeout=30)
        self.add_item(NinoTrackSelector(ctx, tracks))


class Music(commands.Cog):
    def __init__(self, bot: NinoBot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def connect(self, ctx: NinoContext):
        """Connect the bot's music player to the command author's VC"""
        if not ctx.author.voice:
            return await ctx.send_error("You must be in a voice channel.")

        if ctx.voice_client:
            return await ctx.send_error("There is already an existing player.")

        channel = ctx.author.voice.channel
        await channel.connect(cls=NinoPlayer, self_deaf=True)

        await ctx.send_ok(f"Joined `{channel.name}`")

    @commands.hybrid_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx: NinoContext, *, query: str):
        """
        Looks up a song with a given query and returns back 5 results (max). 
        Multiple songs can be played out the same drop down
        """
        if not ctx.author.voice:
            return await ctx.send_error("You must be in a voice channel.")

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(cls=NinoPlayer, self_deaf=True)

        player: NinoPlayer = ctx.voice_client

        tracks = await wavelink.Playable.search(query)

        if not tracks:
            return await ctx.send_ok("No results found.")

        # Playlist
        if isinstance(tracks, wavelink.Playlist):
            for t in tracks.tracks[:100]:  # Max 100 songs out of the playlist
                player.queue.put(t)

            if not player.playing:
                await player.play(player.queue.get())

            return await ctx.send_ok(f"Queued playlist: `{tracks.name}`.")

        # Single result
        if len(tracks) == 1:
            track = tracks[0]
            player.queue.put(track)

            if not player.playing:
                await player.play(player.queue.get())

            return await ctx.send_ok(f"Queued: `{track.title}`.")

        # Multiple results
        await ctx.send(
            embed=discord.Embed(
                title="Multiple Results Found - Select From Below",
                description=f"Search: `{query[:50]}`",
                color=self.bot.ok_color,
            ).set_footer(text="Deleting selector after 30 seconds..."),
            delete_after=30,
            view=TrackSelectView(ctx, tracks),
        )

    @commands.hybrid_command(aliases=["next"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def skip(self, ctx: NinoContext):
        """Skip the current song (if any) and goes to the next."""
        player: NinoPlayer = ctx.voice_client

        if not player:
            return await ctx.send_error("No player to skip songs in.")

        await player.stop()

        if player.queue:
            next_track = player.queue.get()
            await player.play(next_track)
            await ctx.send_ok(f"Now playing: `{next_track.title}`.")

    @commands.hybrid_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pause(self, ctx: NinoContext):
        """Pause the current song in the music player"""
        player: NinoPlayer = ctx.voice_client

        if not player:
            return await ctx.send_error("No player found.")

        await player.pause(not player.paused)
        await ctx.send_ok("Toggled pause.")

    @commands.hybrid_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def volume(self, ctx: NinoContext, volume: int):
        """Adjust the music players volume"""
        player: NinoPlayer = ctx.voice_client

        if not player:
            return await ctx.send_error("No player found to adjust volume for.")

        if not 0 <= volume <= 100:
            return await ctx.send_error("Volume range (0-100) only.")

        await player.set_volume(volume)
        await ctx.send(f"Volume set to `{self.volume}`")

    @commands.hybrid_command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def disconnect(self, ctx):
        """Disconnects the music player from VC"""
        player: NinoPlayer = ctx.voice_client

        if player:
            await player.disconnect()
        else:
            await ctx.send("No player connected.")

    @commands.hybrid_command(aliases=["np", "currentplaying"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nowplaying(self, ctx: NinoContext):
        """Returns the current song"""
        player: NinoPlayer = ctx.voice_client

        if not player or not player.current:
            return await ctx.send_error("There is currently nothing playing")

        track = player.current

        embed = discord.Embed(
            title=track.title,
            description=track.author,
            url=track.uri,
            color=self.bot.ok_color,
        )

        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        await ctx.send(embed=embed)

    @commands.hybrid_command(aliases=["listqueue", "songs"])
    async def queue(self, ctx: NinoContext):
        """Returns a list back of the songs in queue"""
        player: NinoPlayer = ctx.voice_client

        if not player or not player.queue:
            return await ctx.send_ok("Queue is empty.")

        pages = [
            discord.Embed(
                title=f"{ctx.guild.name} Queue",
                description="\n".join(f"`{i}. {t.title} - {t.author}`" for i, t in enumerate(chunk, 1)),
                color=self.bot.ok_color
            ).set_footer(text=f"Page {i}")
            for i, chunk in enumerate(discord.utils.as_chunks(player.queue, 10), 1)
        ]

        paginator = ButtonPaginator(pages)
        await paginator.start(ctx)


async def setup(bot: NinoBot):
    await bot.add_cog(Music(bot))
