import os
import discord
from discord.ext import commands
from sokuji.cog import SokujiCog
from track.cog import TrackCog
from tool.cog import ToolCog
from dev.cog import DevCog
from lounge.cog import LoungeCog

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=['%', '％'], intents=intents)

for cog in {
    SokujiCog,
    TrackCog,
    ToolCog,
    DevCog,
    LoungeCog
}:
    bot.add_cog(cog(bot))

async def update_activity():
    activity = discord.Activity(name=f'%sheat - {len(bot.guilds)} servers', type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)

@bot.event
async def on_ready():
    print('bot ready.')
    await update_activity()

@bot.event
async def on_guild_join(_: discord.Guild):
    await update_activity()

@bot.event
async def on_guild_remove(_: discord.Guild):
    await update_activity()

bot.run(os.environ['DISCORD_BOT_TOKEN'])
