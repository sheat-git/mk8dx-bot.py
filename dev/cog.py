from io import BytesIO
from typing import Optional
import json
import discord
from discord import Embed
from discord.ext import commands


class DevCog(commands.Cog, name='Dev'):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    async def embed_to_json(self, sender: discord.abc.Messageable, fetcher: discord.abc.Messageable, message_id: int, embed_index: int):
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
    
    @commands.command(
        name='jsonM',
        aliases=['j', 'jm', 'json', 'jsonm'],
        hidden=True
    )
    async def embed_to_json_with_mid(self, ctx: commands.Context, message_id: int, embed_index: Optional[int] = 0):
        await self.embed_to_json(sender=ctx, fetcher=ctx, message_id=message_id, embed_index=embed_index)

    @commands.command(
        name='jsonC',
        aliases=['jc', 'jsonc'],
        hidden=True
    )
    async def embed_to_json_with_cid_and_mid(self, ctx: commands.Context, channel_id: int, message_id: int, embed_index: Optional[int] = 0):
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            channel = self.bot.fetch_channel(channel_id)
        await self.embed_to_json(sender=ctx, fetcher=channel, message_id=message_id, embed_index=embed_index)

    @commands.command(
        name='embed',
        aliases=['ebd', 'e'],
        hidden=True
    )
    async def json_to_embed(self, ctx, *, json_text: str):
        embed = Embed.from_dict(json.loads(json_text))
        await ctx.send(embed=embed)

    @commands.command(
        name='delete',
        aliases=['del'],
        hidden=True
    )
    async def delete_message(self, ctx, message_id: int):
        message = self.bot.get_message(message_id)
        if message is None:
            message = await ctx.fetch_message(message_id)
        if message.author.id == self.bot.user.id:
            await message.delete()

    @commands.command(
        name='resend',
        aliases=['rsd', 'rs'],
        hidden=True
    )
    async def resend_message(self, ctx: commands.Context, id1: Optional[int] = None, id2: Optional[int] = None):
        if id1 is None:
            return
        if id2 is None:
            message = self.bot.get_message(id1)
            if message is None:
                message = await ctx.fetch_message(id1)
        else:
            channel = self.bot.get_channel(id1)
            if channel is None:
                channel = await self.bot.fetch_channel(id1)
            message = await channel.fetch_message(id2)
        await ctx.send(content=message.content, tts=message.tts, embeds=message.embeds)
