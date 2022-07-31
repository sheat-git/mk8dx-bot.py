from discord.ext import commands


class GatherCog(commands.Cog, name='Gather'):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
    
    @commands.command(
        name='can',
        aliases=['c', 'C'],
        brief='Can play in Gathering'
    )
    async def command_can(self, ctx: commands.Context):
        await ctx.send(
            'This command is under development for Gather.\n'
            'Use `%v` to start Sokuji instead.\n'
            'このコマンドは募集用に開発中です。\n'
            '即時を開始するには `%v` を使用してください。\n'
        )
    
    @commands.command(
        name='sub',
        aliases=['s'],
        brief='Substitute for Gathering'
    )
    async def command_sub(self, ctx: commands.Context):
        return
    
    @commands.command(
        name='may',
        aliases=['rc', 'r', 'm'],
        brief='May play in Gathering'
    )
    async def command_tmpcan(self, ctx: commands.Context):
        await ctx.send(
            'This command is under development for Gather.\n'
            'Use `%rslt` to make result image instead.\n'
            'このコマンドは募集用に開発中です。\n'
            '集計画像を作成するには `%rslt` を使用してください。\n'
        )
