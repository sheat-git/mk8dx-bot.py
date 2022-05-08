import asyncio
import string
from typing import Optional
from components import ColoredEmbed as Embed
from discord import Message, Member
from discord.abc import Messageable
from discord.ext import commands
import mk8dx.lounge_api as la
from mk8dx import Rank, Track
from .sokuji import Sokuji, SubSokuji, find
import sokuji.result as result
from .tag import to_tag
from locale_ import Locale


class SokujiCog(commands.Cog, name='Sokuji'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    def validate_tags(self, ctx: commands.Context, tags: list[str], format: Optional[int]) -> tuple[list[str], int]:
        if format is None:
            if len(tags) in {2, 3, 4, 6}:
                format = 12 // len(tags)
            elif len(tags) <= 1:
                format = 6
            else:
                format = 2
        if len(tags) < 12 // format:
            if ctx.guild is not None:
                tag = to_tag(ctx.guild.name)
            else:
                tag = ctx.author.display_name
            tags = [tag, *tags]
            for i in range(12 // format - len(tags)):
                tags.append(string.ascii_uppercase[i] * 2)
        elif len(tags) > 12 // format:
            tags = tags[:12//format]
        return tags, format

    async def _start(self, ctx: commands.Context, tags: list[str], format: Optional[int]) -> Message:
        if ctx.guild is not None and ctx.channel.permissions_for(ctx.guild.me).use_external_emojis == False:
            asyncio.ensure_future(ctx.send(
                'Please permit me to use external emojis. The display will be corrupted.\n'
                '「外部の絵文字を使用する」権限をください。表示が崩れます。'
            ))
        tags, format = self.validate_tags(ctx, tags=tags, format=format)
        locale = Locale.JA
        try:
            player = await asyncio.wait_for(la.get_player(discord_id=ctx.author.id), timeout=0.7)
            if player is not None and player.country_code is not None and player.country_code != 'JP':
                locale = Locale.EN
        except (la.LoungeAPIError, asyncio.TimeoutError):
            pass
        return await Sokuji.start(tags=tags, format=format, locale=locale).send(messageable=ctx)
    
    @commands.command(
        aliases=['sokuji', 'cal', 'c'],
        brief='Starts sokuji'
    )
    async def start(self, ctx, *tags):
        await self._start(ctx=ctx, tags=tags, format=None)
    
    @commands.command(
        aliases=['sokuji2', 'cal2', 'c2'],
        brief='Starts 2v2 sokuji'
    )
    async def start2(self, ctx, *tags):
        await self._start(ctx=ctx, tags=tags, format=2)

    @commands.command(
        aliases=['sokuji3', 'cal3', 'c3'],
        brief='Starts 3v3 sokuji'
    )
    async def start3(self, ctx, *tags):
        await self._start(ctx=ctx, tags=tags, format=3)

    @commands.command(
        aliases=['sokuji4', 'cal4', 'c4'],
        brief='Starts 4v4 sokuji'
    )
    async def start4(self, ctx, *tags):
        await self._start(ctx=ctx, tags=tags, format=4)

    @commands.command(
        aliases=['sokuji6', 'cal6', 'c6'],
        brief='Starts 6v6 sokuji'
    )
    async def start6(self, ctx, *tags):
        await self._start(ctx=ctx, tags=tags, format=6)

    @commands.command(
        brief='Ends sokuji'
    )
    async def end(self, ctx):
        sokuji_message, subsokuji_message, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        sokuji.end()
        await sokuji.edit(sokuji_message.message)
        if subsokuji_message is None:
            return
        await subsokuji_message.message.delete()

    @commands.command(
        aliases=['restart'],
        brief='Resumes ended sokuji'
    )
    async def resume(self, ctx):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id, include_ended=True)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        sokuji.resume()
        await sokuji.edit(sokuji_message.message)

    @commands.command(
        aliases=['english', 'en',],
        brief='Englishizes sokuji'
    )
    async def englishize(self, ctx):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id, include_ended=True)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if sokuji.locale == Locale.EN:
            return
        sokuji.locale = Locale.EN
        await sokuji.edit(sokuji_message.message)

    @commands.command(
        aliases=['japan', 'ja', 'jp'],
        brief='Japanizes sokuji'
    )
    async def japanize(self, ctx):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id, include_ended=True)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if sokuji.locale == Locale.JA:
            return
        sokuji.locale = Locale.JA
        await sokuji.edit(sokuji_message.message)
    
    @commands.command(
        name='tags',
        aliases=['set', 's'],
        brief='Edits all tags'
    )
    async def edit_tags(self, ctx, *tags):
        sokuji_message, subsokuji_message, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        tags, _ = self.validate_tags(ctx, tags=tags, format=sokuji.format)
        sokuji.tags = tags
        await sokuji.edit(sokuji_message.message)
        if subsokuji_message is None:
            return
        subsokuji: SubSokuji = subsokuji_message.data
        subsokuji.tags = tags
        await subsokuji.edit(subsokuji_message.message)

    @commands.command(
        name='tag',
        brief='Edits one tag'
    )
    async def edit_tag(self, ctx, tag_num: Optional[int] = None, tag: Optional[str] = None):
        if tag is None:
            return
        sokuji_message, subsokuji_message, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if tag_num is None:
            tag_num = 0
        tags = sokuji.tags
        tags[tag_num-1] = tag
        sokuji.tags = tags
        await sokuji.edit(sokuji_message.message)
        if subsokuji_message is None:
            return
        subsokuji: SubSokuji = subsokuji_message.data
        subsokuji.tags = tags
        await subsokuji.edit(subsokuji_message.message)

    @commands.command(
        name='track',
        aliases=['t'],
        brief='Edits one track'
    )
    async def edit_track(self, ctx, race_num: Optional[int] = None, nick: str = ''):
        sokuji_message, subsokuji_message, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        track = Track.from_nick(nick)
        sokuji: Sokuji = sokuji_message.data
        if subsokuji_message is None or race_num is not None:
            sokuji.edit_track(race_num=race_num, track=track)
            await sokuji.edit(sokuji_message.message)
        if subsokuji_message is None:
            return
        subsokuji: SubSokuji = subsokuji_message.data
        if race_num is None or subsokuji.race_num == race_num:
            subsokuji.track = track
            await subsokuji.edit(subsokuji_message.message)

    @commands.command(
        name='race',
        brief='Edits ranks of one race'
    )
    async def edit_race(self, ctx, race_num: int, *, text: str):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if sokuji.min_race_num > race_num or sokuji.race_num < race_num:
            if sokuji.locale == Locale.JA:
                await ctx.send(f'rece_num={race_num} は無効です。その rece_num は即時に含まれていません。')
            else:
                await ctx.send(f'Invalid race_num={race_num}. That race_num is not included.')
            return
        if sokuji.edit_race(race_num=race_num, text=text):
            await sokuji.edit(sokuji_message.message)

    @commands.command(
        name='raceNum',
        aliases=['racenum', 'rn'],
        brief='Edits total number of races'
    )
    async def edit_total_race_num(self, ctx, total_race_num: Optional[int] = 12):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        sokuji.total_race_num = total_race_num
        await sokuji.edit(sokuji_message.message)

    @commands.command(
        name='back',
        aliases=['b'],
        brief='Restores one previous state'
    )
    async def back(self, ctx):
        sokuji_message, subsokuji_message, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if subsokuji_message is None:
            sokuji: Sokuji = sokuji_message.data
            if sokuji.back():
                await sokuji.edit(sokuji_message.message)
            return
        subsokuji: SubSokuji = subsokuji_message.data
        if subsokuji.back():
            await subsokuji.edit(subsokuji_message.message)
            return
        await subsokuji_message.message.delete()

    @commands.command(
        name='repick',
        aliases=['re'],
        brief='Adds repick data'
    )
    async def add_repick(self, ctx, tag: Optional[str] = None):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if sokuji.add_repick(tag):
            await sokuji.send(ctx)
            await sokuji_message.message.delete()
            return
        if sokuji.locale == Locale.JA:
            await ctx.send(f'タグ {tag} が見つかりません。')
        else:
            await ctx.send(f'Tag {tag} not found.')

    @commands.command(
        name='penalty',
        aliases=['pe'],
        brief='Adds panalty data'
    )
    async def add_penalty(self, ctx, penalty: int, tag: Optional[str] = None):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if sokuji.add_penalty(penalty, tag):
            await sokuji.send(ctx)
            await sokuji_message.message.delete()
            return
        if sokuji.locale == Locale.JA:
            await ctx.send(f'タグ {tag} が見つかりません。')
        else:
            await ctx.send(f'Tag {tag} not found.')

    @commands.command(
        name='banner',
        aliases=['obs', 'o'],
        brief='Adds banner user'
    )
    async def add_banner(self, ctx: commands.Context, members: commands.Greedy[Member]):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if not members:
            new_banner_users = {f'{ctx.author.name}{ctx.author.discriminator}'}
        else:
            new_banner_users = {f'{member.name}{member.discriminator}' for member in members}
        sokuji.banner_users |= new_banner_users
        if sokuji.locale == Locale.JA:
            embed = Embed(
                title='即時集計バナー URL',
                description='どのサーバーでもユーザー毎のURLは変わりません！\n'
                    '※Discordのユーザー名を変更するとURLも変わってしまいます...（ニックネームは関係なし）'
            )
            for user in new_banner_users:
                embed.add_field(
                    name=f'{user[:-4]} さん用 更新開始',
                    value=f'https://sheat-git.github.io/sokuji/?user={user}'
                )
        else:
            embed = Embed(
                title='Sokuji Banner URL',
                description='The per-user URLs on any server do not change!\n'
                    'But if you change your Discord username, the URL will also change...(no matter what your nickname is)'
            )
            for user in new_banner_users:
                embed.add_field(
                    name=f'Start updating for {user[:-4]}',
                    value=f'https://sheat-git.github.io/sokuji/?user={user}'
                )
        embed.set_footer(text='Design: © GungeeSpla')
        await ctx.send(embed=embed)
        await sokuji.send(ctx)
        await sokuji_message.message.delete()

    @commands.command(
        name='removeBanner',
        aliases=['removebanner', 'rb', 'rB', 'removeobs'],
        brief='Removes banner user'
    )
    async def remove_banner(self, ctx, members: commands.Greedy[Member]):
        sokuji_message, _, _ = await find(messageable=ctx, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if not members:
            removed = {f'{ctx.author.name}{ctx.author.discriminator}'}
        else:
            removed = {f'{member.name}{member.discriminator}' for member in members}
        sokuji.banner_users -= removed
        await sokuji.edit(sokuji_message.message)
        if sokuji.locale == Locale.JA:
            await ctx.send('以下のユーザーのバナー更新を停止しました。\n' + ', '.join(member[:-4] for member in removed))
        else:
            await ctx.send('Stopped updating banner of the following users.\n' + ', '.join(member[:-4] for member in removed))

    async def _send_result(self, messageable: Messageable, sender: Messageable):
        sokuji_message, _, _ = await find(messageable=messageable, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if sokuji.format != 6:
            await messageable.send('Error: Format is not 6.')
            return
        tags = sokuji.tags
        embed = Embed(
            title=' - '.join(tags)
        )
        embed.set_image(url='attachment://result.png')
        await sender.send(embed=embed, file=result.make(tags=tags, scores=sokuji.scores))

    @commands.command(
        name='result',
        aliases=['r'],
        brief='Generates result image'
    )
    async def make_result(self, ctx):
        await self._send_result(ctx, ctx)

    @commands.command(
        name='sendResult',
        aliases=['sd', 'sr', 'send'],
        brief='Generates result image and sends to the specified channel'
    )
    async def send_result(self, ctx: commands.Context):
        sender = None
        if ctx.message.channel_mentions:
            sender = ctx.message.channel_mentions[0]
        else:
            channels = await ctx.guild.fetch_channels()
            for channel in channels:
                if channel.name in {'戦績', 'リザルト'}:
                    sender = channel
                    break
            if sender is None:
                for channel in channels:
                    if 'リザルト' in channel.name or '戦績' in channel.name:
                        sender = channel
                        break
        if sender is None:
            await ctx.send('Error: Channel Not Found.')
            return
        await self._send_result(ctx, sender)

    @commands.Cog.listener(name='on_message')
    async def add_text(self, message: Message):
        if message.author.bot:
            return
        text = Rank.validate_text(text=message.content)
        if text is None and message.content != 'back':
            return
        sokuji_message, subsokuji_message, track = await find(messageable=message.channel, user_id=self.bot.user.id)
        if sokuji_message is None:
            return
        sokuji: Sokuji = sokuji_message.data
        if message.content == 'back':
            if subsokuji_message is None:
                if sokuji.back():
                    await sokuji.send(message.channel)
                    await sokuji_message.message.delete()
                return
            subsokuji: SubSokuji = subsokuji_message.data
            if subsokuji.back():
                await subsokuji.send(message.channel)
            await subsokuji_message.message.delete()
            return
        if sokuji.left_race_num <= 0:
            return
        if subsokuji_message is None:
            subsokuji = sokuji.add_text(text=text, track=track)
            if subsokuji is None:
                await sokuji.send(message.channel)
                await sokuji_message.message.delete()
                return
            await subsokuji.send(message.channel)
        else:
            subsokuji: SubSokuji = subsokuji_message.data
            prev = len(subsokuji)
            subsokuji.add_text(text=text)
            if prev == len(subsokuji):
                return
            await subsokuji.send(message.channel)
            await subsokuji_message.message.delete()
        if subsokuji.is_valid():
            sokuji.add_subsokuji(subsokuji=subsokuji)
            await sokuji.send(message.channel)
