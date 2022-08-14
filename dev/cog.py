import datetime
import traceback
from io import BytesIO, StringIO
from typing import Optional
import json
import discord
from discord import (
    Embed,
    EmbedField,
    TextChannel,
    ApplicationContext,
    ApplicationCommandError,
    ApplicationCommandInvokeError
)
from discord.ext import commands
from discord.utils import format_dt

from components import ColoredEmbed
from errors import BotError


LOG_CHANNEL_ID = 1003228025774682122

class DevCog(commands.Cog, name='Dev', command_attrs=dict(hidden=True)):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.LOG_CHANNEL: TextChannel = None
    
    @commands.Cog.listener(name='on_ready')
    async def setup(self):
        self.LOG_CHANNEL = self.bot.get_channel(LOG_CHANNEL_ID)
    
    async def command_log_error(self, ctx: commands.Context, error: Exception) -> None:
        now = datetime.datetime.utcnow()
        embed = ColoredEmbed(
            title=str(type(error)),
            description=f'```{error}```',
            fields=[
                EmbedField(
                    name='Command',
                    value=f'```{ctx.message.content}```',
                    inline=False
                ),
                EmbedField(
                    name='Errored on',
                    value=format_dt(now, 'd')+format_dt(now, 'T'),
                    inline=False
                )
            ]
        )
        binary = StringIO()
        traceback.print_exception(error, file=binary)
        binary.seek(0)
        file = discord.File(fp=binary, filename='traceback.txt')
        binary.close()
        await self.LOG_CHANNEL.send(embed=embed, file=file)

    async def slash_log_error(self, ctx: ApplicationContext, error: Exception) -> None:
        now = datetime.datetime.utcnow()
        embed = ColoredEmbed(
            title=str(type(error)),
            description=f'```{error}```',
            fields=[
                EmbedField(
                    name='Command',
                    value=f'```{ctx.command.qualified_name}```',
                    inline=False
                ),
                EmbedField(
                    name='Options',
                    value=f'```{ctx.selected_options}```',
                    inline=False
                ),
                EmbedField(
                    name='Errored on',
                    value=format_dt(now, 'd')+format_dt(now, 'T'),
                    inline=False
                )
            ]
        )
        binary = StringIO()
        traceback.print_exception(error, file=binary)
        binary.seek(0)
        file = discord.File(fp=binary, filename='traceback.txt')
        binary.close()
        await self.LOG_CHANNEL.send(embed=embed, file=file)

    async def embed_to_json(
        self,
        sender: discord.abc.Messageable,
        fetcher: discord.abc.Messageable,
        message_id: int,
        embed_index: int
    ) -> None:
        message = self.bot.get_message(message_id)
        if message is None:
            message = await fetcher.fetch_message(message_id)
        embed = message.embeds[embed_index]
        binary = BytesIO()
        binary.write(json.dumps(embed.to_dict(), ensure_ascii=False, indent=2).encode())
        binary.seek(0)
        file = discord.File(fp=binary, filename='embed.json')
        binary.close()
        await sender.send(file=file)

    @commands.Cog.listener(name='on_command_error')
    async def command_catch_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, BotError):
            await error.original.message.send(ctx)
            return
        if isinstance(error, commands.CommandNotFound):
            return
        await self.command_log_error(ctx, error)

    @commands.Cog.listener(name='on_application_command_error')
    async def slash_catch_error(self, ctx: ApplicationContext, error: ApplicationCommandError) -> None:
        if isinstance(error, ApplicationCommandInvokeError) and isinstance(error.original, BotError):
            await error.original.message.respond(ctx, ephemeral=True)
            return
        await self.slash_log_error(ctx, error)

    @commands.command(
        name='jsonM',
        aliases=['j', 'jm', 'json', 'jsonm']
    )
    async def embed_to_json_with_mid(self, ctx: commands.Context, message_id: int, embed_index: Optional[int] = 0):
        await self.embed_to_json(sender=ctx, fetcher=ctx, message_id=message_id, embed_index=embed_index)

    @commands.command(
        name='jsonC',
        aliases=['jc', 'jsonc']
    )
    async def embed_to_json_with_cid_and_mid(self, ctx: commands.Context, channel_id: int, message_id: int, embed_index: Optional[int] = 0):
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = self.bot.fetch_channel(channel_id)
        await self.embed_to_json(sender=ctx, fetcher=channel, message_id=message_id, embed_index=embed_index)

    @commands.command(
        name='embed',
        aliases=['ebd', 'e']
    )
    async def json_to_embed(self, ctx, *, json_text: str):
        embed = Embed.from_dict(json.loads(json_text))
        await ctx.send(embed=embed)

    @commands.command(
        name='delete',
        aliases=['del']
    )
    async def delete_message(self, ctx, message_id: int):
        message = self.bot.get_message(message_id)
        if message is None:
            message = await ctx.fetch_message(message_id)
        if message.author.id == self.bot.user.id:
            await message.delete()

    @commands.command(
        name='resend',
        aliases=['rsd', 'rs']
    )
    async def resend_message(self, ctx: commands.Context, channel_id: int, message_id: Optional[int] = None):
        if message_id is None:
            message_id = channel_id
            message = self.bot.get_message(message_id)
            if message is None:
                message = await ctx.fetch_message(message_id)
        else:
            channel = self.bot.get_channel(channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(channel_id)
            message = await channel.fetch_message(message_id)
        await ctx.send(content=message.content, tts=message.tts, embeds=message.embeds)
