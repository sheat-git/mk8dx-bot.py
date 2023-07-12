from typing import Union, Optional
import re
from discord.abc import Messageable
from discord import (
    Member,
    Message,
    ApplicationContext,
    Option,
    SlashCommandGroup,
    Embed,
    TextChannel,
    File
)
from discord.ext import commands
import string
import asyncio
import datetime
import mk8dx.lounge_api as lapi
from mk8dx import Track, Rank

from components import BotMessage, ColoredEmbed
from lang import Lang
from sokuji.sokuji import Sokuji
from sokuji.errors import *
from sokuji import result_image


Context = Union[commands.Context, ApplicationContext]

BOT_ID = None

class SokujiMessage():

    __slots__ = (
        'sokuji',
        'message',
        'child_message',
        'track'
    )

    def __init__(self) -> None:
        self.sokuji: Optional[Sokuji] = None
        self.message: Optional[Message] = None
        self.child_message: Optional[Message] = None
        self.track: Optional[Track] = None

    async def fetch(self, messageable: Messageable, include_archive: bool = False) -> None:
        child_embed = None
        async for message in messageable.history(
            after = datetime.datetime.now() - datetime.timedelta(minutes=30),
            oldest_first = False
        ):
            if message.author.id != BOT_ID or not message.embeds:
                continue
            embed = message.embeds[-1].copy()
            if 'URL' in embed.title:
                continue
            if embed.title.startswith(('即時', 'Sokuji')):
                self.message = message
                self.sokuji = Sokuji(embed, child_embed)
                if embed.author.name == 'Archive' and not include_archive:
                    raise SokujiArchivedError(self.sokuji.lang)
                return
            elif embed.author.name == 'Sokuji Child':
                self.child_message = message
                child_embed = embed
            elif embed.author.name == 'Track' and self.track is None:
                self.track = Track.from_nick(embed.title.split(maxsplit=1)[0])
        raise SokujiNotFoundError()

    @staticmethod
    async def fetched(messageable: Messageable, include_archive: bool = False) -> 'SokujiMessage':
        sm = SokujiMessage()
        await sm.fetch(messageable, include_archive)
        return sm

    async def edit_sokuji(self) -> None:
        embeds = self.message.embeds
        embeds[-1] = self.sokuji.embed
        self.sokuji.update_firebase()
        if self.sokuji.left_race_num == 0 and self.sokuji.format == 6:
            embeds[-1].set_image(url='attachment://result.png')
            await self.message.edit(embeds=embeds, file=result_image.make(tags=self.sokuji.tags, scores=self.sokuji.get_scores()))
        else:
            await self.message.edit(embeds=embeds)

    async def edit(self) -> None:
        await self.edit_sokuji()
        if self.child_message is not None:
            if self.sokuji.child is None:
                await self.child_message.delete()
            else:
                await self.child_message.edit(embed=self.sokuji.child.embed)

    async def delete_sokuji(self) -> None:
        embeds = self.message.embeds
        embeds.pop(-1)
        if embeds:
            await self.message.edit(embeds=embeds)
        else:
            await self.message.delete()

    async def delete(self) -> None:
        if self.sokuji.child is None or self.sokuji.child_is_valid():
            await self.delete_sokuji()
        if self.child_message is not None:
            await self.child_message.delete()


class SokujiCog(commands.Cog, name='Sokuji'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    sokuji = SlashCommandGroup('sokuji', 'Sokuji')
    banner = sokuji.create_subgroup('banner', 'Banner')
    race = sokuji.create_subgroup('race', 'Race')

    @commands.Cog.listener('on_ready')
    async def setup(self):
        global BOT_ID
        BOT_ID = self.bot.user.id

    def validate(self, ctx: Context, tags_text: str, format: Optional[int]) -> tuple[list[str], int]:
        tags = tags_text.split()
        if format is None:
            if len(tags) in {2, 3, 4, 6}:
                format = 12 // len(tags)
            elif len(tags) <= 1:
                format = 6
            else:
                format = 2
        if len(tags) < 12 // format:
            if ctx.guild is not None:
                tag = {
                    899957283230994442: 'HαM',
                    834383470021050399: 'TT'
                }.get(ctx.guild.id, ctx.guild.name.split(maxsplit=1)[0])
            else:
                tag = ctx.author.display_name
            tags = [tag, *tags]
            for i in range(12 // format - len(tags)):
                tags.append(string.ascii_uppercase[i] * 2)
        elif len(tags) > 12 // format:
            tags = tags[:12//format]
        return tags, format

    def start(
        self,
        ctx: Context,
        tags_text: str,
        format: Optional[int],
        lang: Lang,
    ) -> BotMessage:
        tags, format = self.validate(ctx=ctx, tags_text=tags_text, format=format)
        message = Sokuji.start(tags=tags, format=format, lang=lang).message
        if ctx.guild is not None and ctx.channel is not None and ctx.channel.permissions_for(ctx.guild.me).use_external_emojis == False:
            message.content = 'Please permit me to use external emojis. The display will be corrupted.\n「外部の絵文字を使用する」権限をください。表示が崩れます。'
        return message

    async def command_start(self, ctx: commands.Context, tags_text: str, format: Optional[int]):
        lang = Lang.JA
        try:
            player = await asyncio.wait_for(lapi.get_player(discord_id=ctx.author.id), timeout=0.7)
            if player is not None and player.country_code is not None and player.country_code != 'JP':
                lang = Lang.EN
        except (lapi.LoungeAPIError, asyncio.TimeoutError):
            pass
        await self.start(ctx=ctx, tags_text=tags_text, format=format, lang=lang).send(ctx)

    @commands.command(
        name='sokuji',
        aliases=['start', 'cal', 'versus', 'vs', 'v'],
        brief='Starts sokuji'
    )
    async def command_start0(self, ctx, *, tags=''):
        await self.command_start(ctx=ctx, tags_text=tags, format=None)

    @commands.command(
        name='sokuji2',
        aliases=['start2', 'cal2', 'versus2', 'vs2', 'v2'],
        brief='Starts 2v2 sokuji'
    )
    async def command_start2(self, ctx, *, tags=''):
        await self.command_start(ctx=ctx, tags_text=tags, format=2)

    @commands.command(
        name='sokuji3',
        aliases=['start3', 'cal3', 'versus3', 'vs3', 'v3'],
        brief='Starts 3v3 sokuji'
    )
    async def command_start3(self, ctx, *, tags=''):
        await self.command_start(ctx=ctx, tags_text=tags, format=3)

    @commands.command(
        name='sokuji4',
        aliases=['start4', 'cal4', 'versus4', 'vs4', 'v4'],
        brief='Starts 4v4 sokuji'
    )
    async def command_start4(self, ctx, *, tags=''):
        await self.command_start(ctx=ctx, tags_text=tags, format=4)

    @commands.command(
        name='sokuji6',
        aliases=['start6', 'cal6', 'versus6', 'vs6', 'v6'],
        brief='Starts 6v6 sokuji'
    )
    async def command_start6(self, ctx, *, tags=''):
        await self.command_start(ctx=ctx, tags_text=tags, format=6)

    @sokuji.command(
        name='start',
        description='Starts sokuji',
        description_localizations={'ja': '即時集計開始'}
    )
    async def slash_start(
        self,
        ctx: ApplicationContext,
        tags: Option(
            str,
            name='tags',
            name_localizations={'ja': 'タグ'},
            description='Enter tags with separated by spaces.',
            description_localizations={'ja': 'タグを空白区切りで入力'}
        ),
        format: Option(
            int,
            choices=[2, 3, 4, 6],
            required=False,
            name='format',
            name_localizations={'ja': '形式'},
            description='Enter format',
            description_localizations={'ja': '形式を入力'}
        )
    ) -> None:
        if (ctx.locale or 'ja') == 'ja':
            lang = Lang.JA
        else:
            lang = Lang.EN
        await self.start(ctx=ctx, tags_text=tags, format=format, lang=lang).respond(ctx)

    async def end(self, ctx: Context) -> BotMessage:
        sm = await SokujiMessage.fetched(ctx)
        sm.sokuji.end()
        await sm.edit_sokuji()
        if sm.child_message is not None:
            await sm.child_message.delete()
        return BotMessage(content={
            Lang.JA: '即時を終了しました。',
            Lang.EN: 'Sokuji ended.'
        }[sm.sokuji.lang])

    @commands.command(
        name='end',
        brief='Ends sokuji'
    )
    async def command_end(self, ctx: commands.Context) -> None:
        await (await self.end(ctx)).send(ctx)

    @sokuji.command(
        name='end',
        description='Ends sokuji',
        description_localizations={'ja': '即時を終了'}
    )
    async def slash_end(self, ctx: ApplicationContext) -> None:
        await (await self.end(ctx)).respond(ctx)

    async def resume(self, ctx: Context) -> BotMessage:
        sm = await SokujiMessage.fetched(ctx, include_archive=True)
        sm.sokuji.resume()
        await sm.edit_sokuji()
        return BotMessage(content={
            Lang.JA: '即時を再開します。',
            Lang.EN: 'Resumes sokuji.'
        }[sm.sokuji.lang])

    @commands.command(
        name='resume',
        aliases=['restart'],
        brief='Resumes ended sokuji'
    )
    async def command_resume(self, ctx: commands.Context) -> None:
        await (await self.resume(ctx)).send(ctx)

    @sokuji.command(
        name='resume',
        description='Resumes ended sokuji',
        description_localizations={'ja': '終了した即時を再開'}
    )
    async def slash_resume(self, ctx: ApplicationContext) -> None:
        await (await self.resume(ctx)).respond(ctx)

    async def localize(self, ctx: Context, lang: Lang) -> BotMessage:
        sm = await SokujiMessage.fetched(ctx, include_archive=True)
        if sm.sokuji.lang == lang:
            return BotMessage(content={
                Lang.JA: '即時はすでに日本語表記です。',
                Lang.EN: 'Sokuji is already in English.'
            }[lang])
        sm.sokuji.lang = lang
        await sm.edit()
        return BotMessage(content={
            Lang.JA: '即時を日本語化しました。',
            Lang.EN: 'Sokuji is now in English.'
        }[lang])

    @commands.command(
        name='englishize',
        aliases=['english', 'en'],
        brief='Englishizes sokuji'
    )
    async def command_localize_en(self, ctx: commands.Context) -> None:
        await (await self.localize(ctx, Lang.EN)).send(ctx)

    @commands.command(
        name='japanize',
        aliases=['japanese', 'japan', 'jp', 'ja'],
        brief='Japanizes sokuji'
    )
    async def command_localize_ja(self, ctx: commands.Context) -> None:
        await (await self.localize(ctx, Lang.JA)).send(ctx)

    @sokuji.command(
        name='localize',
        description='Localizes sokuji',
        description_localizations={'ja': '即時の言語変更'}
    )
    async def slash_localize(
        self,
        ctx: ApplicationContext,
        locale: Option(
            str,
            name='locale',
            name_localizations={'ja': '言語'},
            choices=['English', '日本語']
        )
    ) -> None:
        if locale == 'English':
            lang = Lang.EN
        else:
            lang = Lang.JA
        await (await self.localize(ctx, lang)).respond(ctx)

    async def edit(
        self,
        ctx: Context,
        tag_text: Optional[str] = None,
        tags_text: Optional[str] = None,
        total_race_num: Optional[int] = None
    ) -> BotMessage:
        if not tag_text and not tags_text and not total_race_num:
            raise NoArgumentToEditError()
        sm = await SokujiMessage.fetched(ctx)
        if tags_text:
            tags, _ = self.validate(ctx, tags_text, sm.sokuji.format)
            sm.sokuji.tags = tags
        elif tag_text:
            tag_texts = tag_text.split()
            tag_num = 0
            tag = tag_texts[0]
            if len(tag_texts) >= 2 and tag_texts[0].isdecimal():
                tag_num = int(tag_texts[0])
                tag = tag_texts[1]
            sm.sokuji.tags[tag_num-1] = tag
        if total_race_num:
            sm.sokuji.total_race_num = total_race_num
        await sm.edit()
        if tags_text and total_race_num:
            return BotMessage(content={
                Lang.JA: 'タグと総レース数を変更しました。',
                Lang.EN: 'Edited all tags and total number of races.'
            }[sm.sokuji.lang])
        elif tag_text and total_race_num:
            return BotMessage(content={
                Lang.JA: 'タグと総レース数を変更しました。',
                Lang.EN: 'Edited one tag and total number of races.'
            }[sm.sokuji.lang])
        elif tags_text:
            return BotMessage(content={
                Lang.JA: 'タグを変更しました。',
                Lang.EN: 'Edited all tags.'
            }[sm.sokuji.lang])
        elif tag_text:
            return BotMessage(content={
                Lang.JA: 'タグを変更しました。',
                Lang.EN: 'Edited one tag.'
            }[sm.sokuji.lang])
        elif total_race_num:
            return BotMessage(content={
                Lang.JA: '総レース数を変更しました。',
                Lang.EN: 'Edited total number of races.'
            }[sm.sokuji.lang])
        return BotMessage(content={
            Lang.JA: '変更しました。',
            Lang.EN: 'Edited.'
        }[sm.sokuji.lang])

    @commands.command(
        name='tag',
        brief='Edits one tag'
    )
    async def command_tag(self, ctx: commands.Context, *, tag: str) -> None:
        await (await self.edit(ctx, tag_text=tag)).send(ctx)

    @commands.command(
        name='tags',
        brief='Edits all tags'
    )
    async def command_tags(self, ctx: commands.Context, *, tags: str) -> None:
        await (await self.edit(ctx, tags_text=tags)).send(ctx)

    @commands.command(
        name='totalRaceNum',
        aliases=['totalracenum', 'raceNum', 'racennum', 'trn', 'rn'],
        brief='Edits total number of races'
    )
    async def command_total_race_num(self, ctx: commands.Context, total_race_num: int) -> None:
        await (await self.edit(ctx, total_race_num=total_race_num)).send(ctx)

    @sokuji.command(
        name='edit',
        description='Edits tag or total number of races',
        description_localizations={'ja': '即時のタグまたは総レース数を変更'}
    )
    async def slash_edit(
        self,
        ctx: ApplicationContext,
        tag: Option(
            str,
            name='tag',
            name_localizations={'ja': 'タグ'},
            description='Enter tag number and new tag with separated by space. Not given tag number, edit the last tag.',
            description_localizations={'ja': '何番目かと新しいタグを空白区切りで入力（何番目かを省略すると最後のタグを編集）'},
            required=False
        ),
        tags: Option(
            str,
            name='tags',
            name_localizations={'ja': '複数のタグ'},
            description='Enter tags with separated by spaces.',
            description_localizations={'ja': 'タグを空白区切りで入力'},
            required=False
        ),
        total_race_num: Option(
            int,
            name='total_race_num',
            name_localizations={'ja': '総レース数'},
            description='Enter valid total number of races.',
            description_localizations={'ja': '有効な総レース数を入力'},
            min_value=1,
            required=False
        )
    ) -> None:
        await (await self.edit(ctx, tag, tags, total_race_num)).respond(ctx)

    def back(self, sm: SokujiMessage) -> BotMessage:
        sm.sokuji.back()
        return sm.sokuji.message

    @commands.command(
        name='back',
        brief='Restores one previous state'
    )
    async def command_back(self, ctx: commands.Context) -> None:
        sm = await SokujiMessage.fetched(ctx)
        await self.back(sm).send(ctx)
        await sm.delete()

    @sokuji.command(
        name='back',
        description='Restores one previous state',
        description_localizations={'ja': '即時を1つ戻す'}
    )
    async def slash_back(
        self,
        ctx: ApplicationContext
    ) -> None:
        sm = await SokujiMessage.fetched(ctx)
        await self.back(sm).respond(ctx)
        await sm.delete()

    async def repick(
        self,
        ctx: Context,
        tag: Optional[str]
    ) -> BotMessage:
        sm = await SokujiMessage.fetched(ctx)
        sm.sokuji.add_repick(tag)
        await sm.edit_sokuji()
        return BotMessage(content={
            Lang.JA: 'リピックを追加しました。',
            Lang.EN: 'Added repick.'
        }[sm.sokuji.lang])

    @commands.command(
        name='repick',
        aliases=['re'],
        brief='Adds repick'
    )
    async def command_repick(self, ctx: commands.Context, tag: Optional[str] = None) -> None:
        await (await self.repick(ctx, tag)).send(ctx)

    @sokuji.command(
        name='repick',
        description='Adds repick',
        description_localizations={'ja': '即時にリピックを追加'}
    )
    async def slash_repick(
        self,
        ctx: ApplicationContext,
        tag: Option(
            str,
            name='tag',
            name_localizations={'ja': 'タグ'},
            description='Adds repick to given tag.',
            description_localizations={'ja': '指定されたタグにリピックを追加'},
            required=False
        )
    ) -> None:
        await (await self.repick(ctx, tag)).respond(ctx)

    async def penalty(
        self,
        ctx: Context,
        score: int,
        tag: Optional[str]
    ) -> BotMessage:
        sm = await SokujiMessage.fetched(ctx)
        sm.sokuji.add_penalty(score, tag)
        await sm.edit_sokuji()
        return BotMessage(content={
            Lang.JA: 'ペナルティを追加しました。',
            Lang.EN: 'Added penalty.'
        }[sm.sokuji.lang])

    @commands.command(
        name='penalty',
        aliases=['pe'],
        brief='Adds penalty'
    )
    async def command_penalty(self, ctx: commands.Context, score: int, tag: Optional[str] = None) -> None:
        await (await self.penalty(ctx, score, tag)).send(ctx)

    @sokuji.command(
        name='penalty',
        description='Adds penalty',
        description_localizations={'ja': '即時にペナルティを追加'}
    )
    async def slash_penalty(
        self,
        ctx: ApplicationContext,
        score: Option(
            int,
            name='score',
            name_localizations={'ja': 'スコア'},
            description='Adds given score as penalty.',
            description_localizations={'ja': 'ペナルティとして指定されたスコアを使用'}
        ),
        tag: Option(
            str,
            name='tag',
            name_localizations={'ja': 'タグ'},
            description='Adds penalty to given tag.',
            description_localizations={'ja': '指定されたタグにペナルティを追加'},
            required=False
        )
    ) -> None:
        await (await self.penalty(ctx, score, tag)).respond(ctx)

    async def result(
        self,
        ctx: Context,
        channel: Optional[TextChannel] = None
    ) -> BotMessage:
        if channel is not None and not channel.can_send(Embed, File):
            raise ChannelCanNotSendError(channel.id)
        sm = await SokujiMessage.fetched(ctx)
        if sm.sokuji.format != 6:
            raise ResultNotValidFormatError(sm.sokuji.lang)
        embed = ColoredEmbed(title=' - '.join(sm.sokuji.tags))
        embed.set_image(url='attachment://result.png')
        message = BotMessage(
            embed=embed,
            file=result_image.make(
                tags=sm.sokuji.tags,
                scores=sm.sokuji.get_scores()
            )
        )
        if channel is None:
            return message
        await message.send(channel)
        return BotMessage(content={
            Lang.JA: f'<#{channel.id}> に送信しました。',
            Lang.EN: f'Sended to <#{channel.id}>.'
        }[sm.sokuji.lang])

    @commands.command(
        name='result',
        aliases=['rslt'],
        brief='Generates result image'
    )
    async def command_result(self, ctx) -> None:
        await (await self.result(ctx)).send(ctx)

    @commands.command(
        name='sendResult',
        aliases=['sd', 'sr', 'send', 'sR'],
        brief='Generates result image and sends to the given channel'
    )
    async def command_result_send(self, ctx: commands.Context):
        channel = None
        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
        else:
            cs = await ctx.guild.fetch_channels()
            for c in cs:
                if c.name in {'戦績', 'リザルト'}:
                    channel = c
                    break
            if channel is None:
                for c in cs:
                    if 'リザルト' in c.name or '戦績' in c.name:
                        channel = c
        if channel is None:
            await ctx.send('Channel Not Found')
            return
        await (await self.result(ctx, channel)).send(ctx)

    @sokuji.command(
        name='result',
        description='Generates result image',
        description_localizations={'ja': '集計表を作成'}
    )
    async def slash_result(
        self,
        ctx: ApplicationContext,
        channel: Option(
            TextChannel,
            name='channel',
            name_localizations={'ja': 'チャンネル'},
            description='If given, send result image to the channel.',
            description_localizations={'ja': '指定された場合、そのチャンネルに送信'},
            required=False
        )
    ) -> None:
        await (await self.result(ctx, channel)).respond(ctx)

    async def banner_add(
        self,
        ctx: Context,
        members: set[Member]
    ) -> BotMessage:
        sm = await SokujiMessage.fetched(ctx)
        if not members:
            members = {ctx.author}
        def toStr(member: Member) -> str:
            name = member.name if member.discriminator == '0' else f'{member.name}{member.discriminator}'
            return re.sub(r'[.$#\[\]/]', ' ', name)
        new_banner_users = set(map(toStr, members))
        sm.sokuji.banner_users |= new_banner_users
        if sm.sokuji.lang == Lang.JA:
            embed = ColoredEmbed(
                title='即時集計バナー URL',
                description='どのサーバーでもユーザー毎のURLは変わりません!\n'
                    '※Discordのユーザー名を変更するとURLも変わってしまいます...（ニックネームは関係なし）'
            )
            for user in new_banner_users:
                embed.add_field(
                    name=f'{user} さん用 更新開始',
                    value=f'https://sheat-git.github.io/sokuji/?user={user}'
                )
        else:
            embed = ColoredEmbed(
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
        await sm.edit_sokuji()
        return BotMessage(embed=embed)

    @commands.command(
        name='banner',
        aliases=['obs', 'o'],
        brief='Adds banner user'
    )
    async def command_banner_add(self, ctx: commands.Context, members: commands.Greedy[Member]) -> None:
        await (await self.banner_add(ctx, members)).send(ctx)

    @banner.command(
        name='add',
        description='Adds banner user',
        description_localizations={'ja': 'バナーの更新を開始'}
    )
    async def slash_banner_add(
        self,
        ctx: ApplicationContext,
        member: Option(
            Member,
            name='user',
            name_localizations={'ja': 'ユーザー'},
            description='If not given, adds you to banner users.',
            description_localizations={'ja': '指定がない場合、コマンド使用者を追加'},
            required=False
        )
    ) -> None:
        members = set() if member is None else {member}
        await (await self.banner_add(ctx, members)).respond(ctx, ephemeral=(member is None))

    async def banner_remove(
        self,
        ctx: Context,
        members: set[Member]
    ) -> BotMessage:
        sm = await SokujiMessage.fetched(ctx)
        if not members:
            members = {ctx.author}
        removed = {f'{member.name}{member.discriminator}' for member in members}
        sm.sokuji.banner_users -= removed
        await sm.edit_sokuji()
        return BotMessage(content={
            Lang.JA: '以下のユーザーのバナー更新を停止しました。\n',
            Lang.EN: 'Stopped updating banner of the following users.\n'
        }[sm.sokuji.lang] + ','.join(member[:-4] for member in removed))

    @commands.command(
        name='removeBanner',
        aliases=['removebanner', 'rb', 'rB', 'removeObs', 'removeobs', 'ro', 'rO'],
        brief='Removes banner user'
    )
    async def command_banner_remove(self, ctx: commands.Context, members: commands.Greedy[Member]) -> None:
        await (await self.banner_remove(ctx, members)).send(ctx)

    @banner.command(
        name='remove',
        description='Removes banner user',
        description_localizations={'ja': 'バナーの更新を停止'}
    )
    async def slash_banner_remove(
        self,
        ctx: ApplicationContext,
        member: Option(
            Member,
            name='user',
            name_localizations={'ja': 'ユーザー'},
            description='If not given, removes you from banner users.',
            description_localizations={'ja': '指定がない場合、コマンド使用者を削除'},
            required=False
        )
    ) -> None:
        members = set() if member is None else {member}
        await (await self.banner_remove(ctx, members)).respond(ctx, ephemeral=(member is None))

    async def race_edit(
        self,
        ctx: Context,
        race_num: Optional[int] = None,
        track_text: Optional[str] = None,
        ranks_text: Optional[str] = None
    ) -> BotMessage:
        sm = await SokujiMessage.fetched(ctx)
        sm.sokuji.edit(race_num, Track.from_nick(track_text or ''), ranks_text)
        await sm.edit()
        return BotMessage(content={
            Lang.JA: f'{race_num or sm.sokuji.race_num}レース目を編集しました。',
            Lang.EN: f'Edited {race_num or sm.sokuji.race_num}-th race.'
        }[sm.sokuji.lang])

    @commands.command(
        name='track',
        aliases=['t'],
        brief='Edits one track'
    )
    async def command_race_edit_track(
        self,
        ctx: commands.Context,
        race_num: Optional[int] = None,
        track: str = ''
    ) -> None:
        await (await self.race_edit(ctx, race_num, track_text=track)).send(ctx)

    @commands.command(
        name='race',
        brief='Edits ranks of one race'
    )
    async def command_race_edit_race(
        self,
        ctx: commands.Context,
        race_num: Optional[int] = None,
        *,
        ranks: str = ''
    ) -> None:
        if not ranks:
            ranks = str(race_num)
            race_num = None
        await (await self.race_edit(ctx, race_num, ranks_text=ranks)).send(ctx)

    @race.command(
        name='edit',
        description='Edits track or ranks of one race',
        description_localizations={'ja': '即時の1レース分のコースまたは順位を編集'}
    )
    async def slash_race_edit(
        self,
        ctx: ApplicationContext,
        track: Option(
            str,
            name='track',
            name_localizations={'ja': 'コース'},
            required=False
        ),
        ranks: Option(
            str,
            name='ranks',
            name_localizations={'ja': '順位'},
            required=False
        ),
        race_num: Option(
            int,
            min_value=1,
            name='race_num',
            name_descriptions={'ja': 'レース番号'},
            required=False
        )
    ) -> None:
        await (await self.race_edit(ctx, race_num, track, ranks)).respond(ctx)

    def race_add(
        self,
        sm: SokujiMessage,
        ranks_text: str,
        track_text: Optional[str] = None
    ) -> BotMessage:
        if track_text:
            track = Track.from_nick(track_text)
        else:
            track = sm.track
        sm.sokuji.add_text(text=ranks_text, track=track)
        return sm.sokuji.message

    @race.command(
        name='add',
        description='Adds race data',
        description_localizations={'ja': 'レース順位を追加'}
    )
    async def slash_race_add(
        self,
        ctx: ApplicationContext,
        ranks: Option(
            str,
            name='ranks',
            name_localizations={'ja': '順位'},
            description='Enter the rankings for each team, separated by spaces. No spaces needed for the rankings of one.',
            description_localizations={'ja': 'チームごとに順位を空白区切りで入力（同チームの順位は空白なし）'}
        ),
        track: Option(
            str,
            name='track',
            name_localizations={'ja': 'コース'},
            description='Enter the run track.',
            description_localizations={'ja': '走ったコース'},
            required=False
        )
    ) -> None:
        ranks_text = Rank.validate_text(ranks)
        if not ranks_text:
            raise NotValidRanksTextError()
        sm = await SokujiMessage.fetched(ctx)
        await self.race_add(sm, ranks_text, track).respond(ctx)
        await sm.delete()

    @commands.Cog.listener(name='on_message')
    async def add_text(self, message: Message) -> None:
        if message.author.bot:
            return
        if message.content == 'back':
            sm = await SokujiMessage.fetched(message.channel)
            await self.back(sm).send(message.channel)
            await sm.delete()
            return
        ranks = Rank.validate_text(message.content)
        if not ranks:
            return
        sm = await SokujiMessage.fetched(message.channel)
        await self.race_add(sm, ranks).send(message.channel)
        await sm.delete()
