from discord import Message
from discord.ext import commands
from discord.abc import Messageable
from .sokuji import Sokuji, SubSokuji
from ..locale import Locale


class SokujiCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def start(ctx: commands.Context, tags: list[str], format: int, locale: Locale = Locale.JA) -> Message:
        return await Sokuji.start(tags=tags, format=format, locale=locale).send(messageable=ctx)
