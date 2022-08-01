from __future__ import annotations

from typing import Optional
import random

from discord import ApplicationContext, DMChannel, EmbedField, Option
from components import ColoredEmbed as Embed
from discord.ext import commands, pages


class ToolCog(commands.Cog, name='Tool'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.command(name='sheat', aliases=['func', 'Func', 'FUNC', 'SHEAT', 'Sheat'], brief='Shows instruction pages')
    async def command_instruction(self, ctx: commands.Context, locale: Optional[str] = None):
        if locale == 'en':
            await self.command_instruction_en(ctx)
            return
        await self.command_instruction_ja(ctx)
        return
    
    async def command_instruction_en(self, ctx: commands.Context):
        await ctx.author.send('The author is Japanese. Please note that my English is poor.')
        await pages.Paginator(pages=self.INSTRUCTION_EMBEDS_EN).send(ctx, target=ctx.author)
        if not isinstance(ctx.channel, DMChannel):
            await ctx.reply('Sent to DM.')

    async def command_instruction_ja(self, ctx: commands.Context):
        await ctx.author.send(r'If you want to see the English version, use `%sheat en` command.')
        await pages.Paginator(pages=self.INSTRUCTION_EMBEDS_JA).send(ctx, target=ctx.author)
        if not isinstance(ctx.channel, DMChannel):
            await ctx.reply('DMに送信しました。')

    @commands.slash_command(
        name='sheat',
        description='Shows introduction of sheat bot.',
        description_localizations={'ja': '使用方法'},
    )
    async def slash_instruction(
        self,
        ctx: ApplicationContext,
        # lang: Option(
        #     str,
        #     choices=['日本語', 'English'],
        #     required=False,
        #     name='lang',
        #     name_localizations={'ja': '言語'},
        # )
    ):
        lang = None
        if lang is None and (ctx.locale or 'ja') == 'ja' or lang == '日本語':
            e = self.INSTRUCTION_EMBEDS_JA
        else:
            e = self.INSTRUCTION_EMBEDS_EN
        await pages.Paginator(pages=e).respond(ctx.interaction, ephemeral=True)

    @commands.command(
        name='choose',
        aliases=['chs'],
        brief='Chooses one at random'
    )
    async def command_choose(self, ctx, *items):
        if not items:
            await ctx.send('Give Values')
            return
        await ctx.send(random.choice(items))


    # setup pages
    INSTRUCTION_EMBEDS_JA = [
        Embed(
            title='基本操作',
            fields=[
                EmbedField(
                    name='即時集計開始',
                    value='```%sokuji タグ1 タグ2 ...```チームの数だけ`タグ`を入力。',
                    inline=False
                ),
                EmbedField(
                    name='即時中の順位入力（6v6）',
                    value='チームの順位が、1, 3, 4, 5, 6, 11位のとき、```1345611```のように空白なしで入力。',
                    inline=False
                ),
                EmbedField(
                    name='即時中の順位入力（2v2, 3v3, 4v4）',
                    value='チーム1の順位が1,2,3、チーム2の順位が4,5,6、チーム3の順位が7,8,9、チーム4の順位が10,11,12のとき、'
                    '```123 456 789 101112```または```\n123\n456\n789\n101112```のようにチームごとに空白区切り、または随時送信で入力。',
                    inline=False
                ),
                EmbedField(
                    name='即時中のコース入力',
                    value='前回の即時の順位入力から次回の順位入力までにbotがコース情報を送信していた場合、その最新のものを即時に添付。\n'
                    '__交流戦中、コースが決まったらすぐにコースを送信しておくのがおすすめ！__',
                    inline=False
                ),
                EmbedField(
                    name='即時バナー',
                    value='```%banner```botが送信するURLをOBS等配信ソフトに設定することで即時を配信に反映させられる。',
                    inline=False
                ),
                EmbedField(
                    name='集計表',
                    value='```%result```',
                    inline=True
                ),
                EmbedField(
                    name='集計表転送',
                    value='```%send #チャンネル```',
                    inline=True
                ),
                EmbedField(
                    name='コース情報',
                    value='コース名のみのメッセージがあると、botがコースの選択場所とアイテムテーブルマップを送信。',
                    inline=False
                )
            ]
        ),
        Embed(
            title='即時編集コマンド',
            fields=[
                EmbedField(
                    name='タグを変更する',
                    value='```%tag 何番目 変更後タグ```',
                    inline=True
                ),
                EmbedField(
                    name='全てのタグを上書きする',
                    value='```%tags タグ1 タグ2 ...```チームの数だけ`タグ`を入力。',
                    inline=True
                ),
                EmbedField(
                    name='総レース数を変更する',
                    value='```%raceNum 総レース数``` `%rn`でも可能。',
                    inline=False
                ),
                EmbedField(
                    name='1つ前に戻る',
                    value='```%back```',
                    inline=True
                ),
                EmbedField(
                    name='コースを変更する',
                    value='```%track 何レース目 コース```'
                    'コースを指定しないことで、該当レースのコースを削除することも可能。',
                    inline=False
                ),
                EmbedField(
                    name='順位を変更する',
                    value='```%race 何レース目 順位情報```6v6以外の形式では、空白区切りの順位入力のみ可能。',
                    inline=False
                ),
                EmbedField(
                    name='リピックを登録する',
                    value='```%repick タグ```タグを指定しないと自チームがリピックしたものと認識。-15点固定。',
                    inline=True
                ),
                EmbedField(
                    name='ペナルティを登録する',
                    value='```%penalty 得点 タグ```減点したかったらマイナスをつけて得点を指定すること。',
                    inline=True
                ),
                EmbedField(
                    name='即時バナーを解除する',
                    value='```%removeBanner``` `%rb`でも可能。',
                    inline=False
                ),
                EmbedField(
                    name='英語化する',
                    value='```%englishize``` `%en`でも可能。',
                    inline=True
                ),
                EmbedField(
                    name='日本語化する',
                    value='```%japanize``` `%ja`でも可能。',
                    inline=True
                )
            ]
        ),
        Embed(
            title='ラウンジコマンド',
            fields=[
                EmbedField(
                    name='MMR',
                    value='```%mmr (プレイヤー)``` `%mmr4`でシーズン4のMMRを表示。',
                    inline=True
                ),
                EmbedField(
                    name='集計表',
                    value='```%table <id>```',
                    inline=True
                ),
                EmbedField(
                    name='Stats',
                    value='```%stats (プレイヤー)``` `%stats4`でシーズン4のstatsを表示。',
                    inline=False
                ),
                EmbedField(
                    name='First',
                    value='```%first# (プレイヤー)``` `%first10`で最初の10模擬のstatsを表示。',
                    inline=True
                ),
                EmbedField(
                    name='Mid',
                    value='```%mid#-# (プレイヤー)``` `%mid10-20`で中間10-20模擬のstatsを表示。',
                    inline=True
                ),
                EmbedField(
                    name='Last',
                    value='```%last# (プレイヤー)``` `%last10`で最新10模擬のstatsを表示。',
                    inline=True
                ),
                EmbedField(
                    name='Format Stats',
                    value='```%fs <形式> (プレイヤー)``` `%fs4 2`でシーズン4の2v2のstatsを表示。',
                    inline=True
                ),
                EmbedField(
                    name='Tier Stats',
                    value='```%ts <tier> (プレイヤー)``` `%ts4 sq`でシーズン4のSQのstatsを表示。',
                    inline=True
                ),
                EmbedField(
                    name='最新の集計表',
                    value='```%lm (プレイヤー)``` `%lm2`で最新から2番目の集計表を表示。',
                    inline=False
                ),
                EmbedField(
                    name='最新の集計表（形式指定）',
                    value='```%flm <形式> (プレイヤー)``` `%flm2 6`で最新から2番目の6v6の集計表を表示。',
                    inline=True
                ),
                EmbedField(
                    name='最新の集計表（Tier指定）',
                    value='```%tlm <tier> (プレイヤー)``` `%tlm3 sq`で最新から3番目のSQの集計表を表示。',
                    inline=True
                ),
                EmbedField(
                    name=':warning: コマンド内の`(プレイヤー)`',
                    value='指定がなければ、コマンド送信者のものを表示。\n'
                    '複数指定はコマンドによって可能。方法はコンマ(`,`)区切り。メンションとラウンジ名の混同OK。',
                    inline=False
                )
            ]
        ),
        Embed(
            title='その他のコマンド',
            fields=[
                EmbedField(
                    name='ランダム選択',
                    value='```%choose A B C ...```A、B、C、、、の選択肢からランダムで選択。`%chs`でも可能。',
                    inline=False
                ),
                EmbedField(
                    name='フレンドコード',
                    value='```%fc (プレイヤー)```',
                    inline=True
                ),
                EmbedField(
                    name='MKCアカウント',
                    value='```%mkc (プレイヤー)```',
                    inline=True
                ),
                EmbedField(
                    name=':warning: コマンド内の`(プレイヤー)`',
                    value='指定がなければ、コマンド送信者のものを表示。\n'
                    '複数指定はコマンドによって可能。方法はコンマ(`,`)区切り。メンションとラウンジ名の混同OK。',
                    inline=False
                ),
                EmbedField(
                    name='もっとコマンドが欲しい',
                    value='<@!426317116958965764> までDMを！',
                    inline=False
                )
            ]
        ),
        Embed(
            title='Tips（即時順位入力）',
            description='こんな入力もできるよ〜ってものです！もちろんTipsを使わない普通の入力もできるよ！',
            fields=[
                EmbedField(
                    name='連続した順位があるとき',
                    value='4位から9位のとき、```4-9```と入力が可能。',
                    inline=False
                ),
                EmbedField(
                    name='前○のとき',
                    value='前6のとき、```-6```と1位を省略して入力が可能。',
                    inline=False
                ),
                EmbedField(
                    name='下○をとったとき',
                    value='3, 5, 6, 10, 11, 12位のように、下3が含まれているとき、```356```のみ入力して下○の順位は全て省略可能。',
                    inline=False
                ),
                EmbedField(
                    name='10位以降の2桁の順位をとったとき',
                    value='10位は0、11位は+で代替入力が可能。上記の、下の順位は自動で埋める機能があるため、12位は入力しなくていい。',
                    inline=False
                )
            ]
        )
    ]
    INSTRUCTION_EMBEDS_EN = [
        Embed(
            title='Basics',
            fields=[
                EmbedField(
                    name='What is Sokuji?',
                    value='Sokuji helps you to know current scores per team.',
                    inline=False
                ),
                EmbedField(
                    name='Start Sokuji',
                    value='```%sokuji tag1 tag2 ...```Input as many `tag`s as there are teams.',
                    inline=False
                ),
                EmbedField(
                    name='Sokuji\'s Ranks Input (6v6)',
                    value='If your team\'s ranks are 1st, 3rd, 4th, 5th, 6th, 11th, input without spaces like below.```1345611```',
                    inline=False
                ),
                EmbedField(
                    name='Sokuji\'s Ranks Input (2v2, 3v3, 4v4)',
                    value='If team1\'s ranks are 1st,2nd,3rd, team2\'s ranks are 4th,5th,6ht, team3\'s ranks are 7th,8th,9ht, and team4\'s ranks are 10th,11th,12th,'
                    'input with space separator for each team or by sending by team like below.'
                    '```123 456 789 101112```or```\n123\n456\n789\n101112```',
                    inline=False
                ),
                EmbedField(
                    name='Sokuji\'s Track Input',
                    value='If this bot has sent track information between the last sokuji\'s ranks input and the next ranks input, the latest one is attached sokuji.\n'
                    '__During the war, it is recommended to send the track as soon as it is selected!__',
                    inline=False
                ),
                EmbedField(
                    name='Sokuji\'s Banner Overlay',
                    value='```%banner```Sokuji can be reflected in the broadcast by setting the URL sent by this bot to the broadcast software such as OBS.',
                    inline=False
                ),
                EmbedField(
                    name='Result Image (6v6 only)',
                    value='```%result```',
                    inline=True
                ),
                EmbedField(
                    name='Send Result (6v6 only)',
                    value='```%send #channel```',
                    inline=True
                ),
                EmbedField(
                    name='Track Information',
                    value='If there is a message with only the track name, this bot sends the location of the track selection and the item table map.',
                    inline=False
                )
            ]
        ),
        Embed(
            title='Edit Sokuji Commands',
            fields=[
                EmbedField(
                    name='Change One Tag',
                    value='```%tag tagNumber newTag```',
                    inline=True
                ),
                EmbedField(
                    name='Change All Tags',
                    value='```%tags tag1 tag2 ...```Input as many `tag`s as there are teams.',
                    inline=True
                ),
                EmbedField(
                    name='Change Total Number Of Races',
                    value='```%raceNum newTotalNumberOfRaces```alias : `%rn`',
                    inline=False
                ),
                EmbedField(
                    name='Restore One Previous State',
                    value='```%back```',
                    inline=True
                ),
                EmbedField(
                    name='Change One Track',
                    value='```%track raceNumber newTrack```'
                    'If newTrack is not existed, you can delete the track of the raceNum\'s race.',
                    inline=False
                ),
                EmbedField(
                    name='Change Ranks of One Race',
                    value='```%race raceNumter ranks```If the format is not 6v6, you can input only with space separator for each team.',
                    inline=False
                ),
                EmbedField(
                    name='Add Repick',
                    value='```%repick tag```If only `%repick` (not tag), adds repick to team1.',
                    inline=True
                ),
                EmbedField(
                    name='Add Penalty',
                    value='```%penalty score tag```If you wants to deduct scores, put a minus sign.',
                    inline=True
                ),
                EmbedField(
                    name='Stop Updating Banner',
                    value='```%removeBanner```alias : `%rb`',
                    inline=False
                ),
                EmbedField(
                    name='Translate into English',
                    value='```%englishize```alias : `%en`',
                    inline=True
                ),
                EmbedField(
                    name='Translate into Japanese',
                    value='```%japanize```alias : `%ja`',
                    inline=True
                )
            ]
        ),
        Embed(
            title='Lounge Commands',
            fields=[
                EmbedField(
                    name='MMR',
                    value='```%mmr (player)``` `%mmr4` shows mmr in the S4.',
                    inline=True
                ),
                EmbedField(
                    name='Table',
                    value='```%table <id>```',
                    inline=True
                ),
                EmbedField(
                    name='Stats',
                    value='```%stats (player)``` `%stats4` shows stats of the S4.',
                    inline=False
                ),
                EmbedField(
                    name='First',
                    value='```%first# (player)``` `%first10` shows first 10 stats.',
                    inline=True
                ),
                EmbedField(
                    name='Mid',
                    value='```%mid#-# (player)``` `%mid10-20` shows midium 10-20 stats.',
                    inline=True
                ),
                EmbedField(
                    name='Last',
                    value='```%last# (player)``` `%last10` shows last 10 stats.',
                    inline=True
                ),
                EmbedField(
                    name='Format Stats',
                    value='```%fs <format> (player)``` `%fs4 2` show 2v2 stats of the S4.',
                    inline=True
                ),
                EmbedField(
                    name='Tier Stats',
                    value='```%ts <tier> (player)``` `%ts4 sq` shows SQ stats of the S4.',
                    inline=True
                ),
                EmbedField(
                    name='The Latest Table',
                    value='```%lm (player)``` `%lm2` shows second latest table.',
                    inline=False
                ),
                EmbedField(
                    name='The Latest Table (in the format)',
                    value='```%flm <format> (player)``` `%flm2 6` shows second latest table in 6v6.',
                    inline=True
                ),
                EmbedField(
                    name='The Latest Table (in the tier)',
                    value='```%tlm <tier> (player)``` `%tlm3 sq` shows third latest table in tier SQ.',
                    inline=True
                ),
                EmbedField(
                    name=':warning: `(player)` in Commands',
                    value='If not specified, show the command sender\'s.\n'
                    'Multiple specifications are possible depending on the command. The method is comma(`,`) delimited. Mention and lounge name confusion is OK.',
                    inline=False
                )
            ]
        ),
        Embed(
            title='Other Commands',
            fields=[
                EmbedField(
                    name='Choose One at Random',
                    value='```%choose A B C ...```alias : `%chs`',
                    inline=False
                ),
                EmbedField(
                    name='FC',
                    value='```%fc (player)```',
                    inline=True
                ),
                EmbedField(
                    name='MKC Links',
                    value='```%mkc (player)```',
                    inline=True
                ),
                EmbedField(
                    name=':warning: `(player)` in Commands',
                    value='If not specified, show the command sender\'s.\n'
                    'Multiple specifications are possible depending on the command. The method is comma(`,`) delimited. Mention and lounge name confusion is OK.',
                    inline=False
                ),
                EmbedField(
                    name='Need More Commands',
                    value='DM <@426317116958965764> !',
                    inline=True
                )
            ]
        ),
        Embed(
            title='Tips (Sokuji Ranks)',
            description='You can use the following abbreviated input!',
            fields=[
                EmbedField(
                    name='Consecutive Ranks',
                    value='If ranks are 4th,5th,6th,7th,8th,9th, you can input like below.```4-9```',
                    inline=False
                ),
                EmbedField(
                    name='Top N',
                    value='If your team get top 6, you can input without 1st like below.```-6```',
                    inline=False
                ),
                EmbedField(
                    name='Bottom N',
                    value='If your team get 3rd,5th,6th,10th,11th,12th (includes bottom 3), you can input without bottom 3 like below.```356```',
                    inline=False
                ),
                EmbedField(
                    name='10th, 11th, and 12th',
                    value='The alternative for "10" is "0". And the alternative for "11" is "+". 12th is included in bottom N, so you don\'t have to input "12".',
                    inline=False
                )
            ]
        )
    ]
