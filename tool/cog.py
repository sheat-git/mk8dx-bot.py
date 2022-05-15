from __future__ import annotations

from typing import Optional
import random

from discord import ApplicationContext, DMChannel, Option
from components import ColoredEmbed as Embed
from discord.ext import commands, pages


class ToolCog(commands.Cog, name='Tool'):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.command(name='sheat', aliases=['func', 'Func', 'FUNC', 'SHEAT', 'Sheat'], brief='Shows instruction pages')
    async def instruction(self, ctx: commands.Context, locale: Optional[str] = None):
        if locale == 'en':
            await self.instruction_en(ctx)
            return
        await self.instruction_ja(ctx)
        return
    
    async def instruction_en(self, ctx: commands.Context):
        await ctx.author.send('The author is Japanese. Please note that my English is poor.')
        await pages.Paginator(pages=self.INSTRUCTION_PAGES_EN).send(ctx, target=ctx.author)
        if not isinstance(ctx.channel, DMChannel):
            await ctx.reply('Sent to DM.')

    async def instruction_ja(self, ctx: commands.Context):
        await ctx.author.send(r'If you want to see the English version, use `%sheat en` command.')
        await pages.Paginator(pages=self.INSTRUCTION_PAGES_JA).send(ctx, target=ctx.author)
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
            p = self.INSTRUCTION_PAGES_JA
        else:
            p = self.INSTRUCTION_PAGES_EN
        await pages.Paginator(pages=p).respond(ctx.interaction, ephemeral=True)

    @commands.command(name='choose', aliases=['chs'], brief='Chooses one at random')
    async def choose(self, ctx, *items):
        await ctx.send(random.choice(items))


    # setup pages

    INSTRUCTION_PAGES_JA = [
        Embed(
            title='基本操作',
        ),
        Embed(
            title='即時編集コマンド'
        ),
        Embed(
            title='ラウンジコマンド'
        ),
        Embed(
            title='その他のコマンド'
        ),
        Embed(
            title='Tips（即時順位入力）',
            description='こんな入力もできるよ〜ってものです！もちろんTipsを使わない普通の入力もできるよ！'
        )
    ]
    INSTRUCTION_PAGES_JA[0].add_field(
        name='即時集計開始',
        value='```%sokuji タグ1 タグ2 ...```チームの数だけ`タグ`を入力。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[0].add_field(
        name='即時中の順位入力（6v6）',
        value='チームの順位が、1, 3, 4, 5, 6, 11位のとき、```1345611```のように空白なしで入力。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[0].add_field(
        name='即時中の順位入力（2v2, 3v3, 4v4）',
        value='チーム1の順位が1,2,3、チーム2の順位が4,5,6、チーム3の順位が7,8,9、チーム4の順位が10,11,12のとき、'
        '```123 456 789 101112```または```\n123\n456\n789\n101112```のようにチームごとに空白区切り、または随時送信で入力。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[0].add_field(
        name='即時中のコース入力',
        value='前回の即時の順位入力から次回の順位入力までにbotがコース情報を送信していた場合、その最新のものを即時に添付。\n'
        '__交流戦中、コースが決まったらすぐにコースを送信しておくのがおすすめ！__',
        inline=False
    )
    INSTRUCTION_PAGES_JA[0].add_field(
        name='即時バナー',
        value='```%banner```botが送信するURLをOBS等配信ソフトに設定することで即時を配信に反映させられる。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[0].add_field(
        name='集計表',
        value='```%result```'
    )
    INSTRUCTION_PAGES_JA[0].add_field(
        name='集計表転送',
        value='```%send #チャンネル```'
    )
    INSTRUCTION_PAGES_JA[0].add_field(
        name='コース情報',
        value='コース名のみのメッセージがあると、botがコースの選択場所とアイテムテーブルマップを送信。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='タグを変更する',
        value='```%tag 何番目 変更後タグ```'
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='全てのタグを上書きする',
        value='```%tags タグ1 タグ2 ...```チームの数だけ`タグ`を入力。'
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='総レース数を変更する',
        value='```%raceNum 総レース数``` `%rn`でも可能。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='1つ前に戻る',
        value='```%back```'
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='コースを変更する',
        value='```%track 何レース目 コース```'
        'コースを指定しないことで、該当レースのコースを削除することも可能。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='順位を変更する',
        value='```%race 何レース目 順位情報```6v6以外の形式では、空白区切りの順位入力のみ可能。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='リピックを登録する',
        value='```%repick タグ```タグを指定しないと自チームがリピックしたものと認識。-15点固定。'
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='ペナルティを登録する',
        value='```%penalty 得点 タグ```減点したかったらマイナスをつけて得点を指定すること。'
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='即時バナーを解除する',
        value='```%removeBanner``` `%rb`でも可能。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='英語化する',
        value='```%englishize``` `%en`でも可能。'
    )
    INSTRUCTION_PAGES_JA[1].add_field(
        name='日本語化する',
        value='```%japanize``` `%ja`でも可能。'
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='MMR',
        value='```%mmr (プレイヤー)``` `%mmr4`でシーズン4のMMRを表示。'
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='stats',
        value='```%stats (プレイヤー)``` `%stats4`でシーズン4のstatsを表示。`'
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='集計表',
        value='```%table <id>```',
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='first',
        value='```%first#``` `%first10`で最初の10模擬のstatsを表示。'
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='mid',
        value='```%mid#-# (プレイヤー)``` `%mid10-20`で中間10-20模擬のstatsを表示。'
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='last',
        value='```%last# (プレイヤー)``` `%last10`で最新10模擬のstatsを表示。'
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='最新の集計表',
        value='```%lm (プレイヤー)``` `%lm2`で最新から2番目の集計表を表示。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='最新の集計表（形式指定）',
        value='```%flm <形式> (プレイヤー)``` `%flm2 6`で最新から2番目の6v6の集計表を表示。'
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name='最新の集計表（Tier指定）',
        value='```%tlm <tier> (プレイヤー)``` `%tlm3 sq`で最新から3番目のSQの集計表を表示。'
    )
    INSTRUCTION_PAGES_JA[2].add_field(
        name=':warning: コマンド内の`(プレイヤー)`',
        value='指定がなければ、コマンド送信者のものを表示。\n'
        '複数指定はコマンドによって可能。方法は`,`区切り。メンションとラウンジ名の混同OK。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[3].add_field(
        name='ランダム選択',
        value='```%choose A B C ...```A、B、C、、、の選択肢からランダムで選択。`%chs`でも可能。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[3].add_field(
        name='フレンドコード',
        value='```%fc (プレイヤー)```'
    )
    INSTRUCTION_PAGES_JA[3].add_field(
        name='MKCアカウント',
        value='```%mkc (プレイヤー)```'
    )
    INSTRUCTION_PAGES_JA[3].add_field(
        name=':warning: コマンド内の`(プレイヤー)`',
        value='指定がなければ、コマンド送信者のものを表示。\n'
        '複数指定はコマンドによって可能。方法は`,`区切り。メンションとラウンジ名の混同OK。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[3].add_field(
        name='もっとコマンドが欲しい',
        value='<@!426317116958965764> までDMを！',
        inline=False
    )
    INSTRUCTION_PAGES_JA[4].add_field(
        name='連続した順位があるとき',
        value='4位から9位のとき、```4-9```と入力が可能。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[4].add_field(
        name='前○のとき',
        value='前6のとき、```-6```と1位を省略して入力が可能。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[4].add_field(
        name='下○をとったとき',
        value='3, 5, 6, 10, 11, 12位のように、下3が含まれているとき、```356```のみ入力して下○の順位は全て省略可能。',
        inline=False
    )
    INSTRUCTION_PAGES_JA[4].add_field(
        name='10位以降の2桁の順位をとったとき',
        value='10位は0、11位は+で代替入力が可能。上記の、下の順位は自動で埋める機能があるため、12位は入力しなくていい。',
        inline=False
    )
    INSTRUCTION_PAGES_EN = [
        Embed(
            title='Basics',
        ),
        Embed(
            title='Edit Sokuji Commands'
        ),
        Embed(
            title='Lounge Commands'
        ),
        Embed(
            title='Other Commands'
        ),
        Embed(
            title='Tips (Sokuji Ranks)',
            description='You can use the following abbreviated input!'
        )
    ]
    INSTRUCTION_PAGES_EN[0].add_field(
        name='What is Sokuji?',
        value='Sokuji helps you to know current scores per team.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[0].add_field(
        name='Start Sokuji',
        value='```%sokuji tag1 tag2 ...```Input as many `tag`s as there are teams.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[0].add_field(
        name='Sokuji\'s Ranks Input (6v6)',
        value='If your team\'s ranks are 1st, 3rd, 4th, 5th, 6th, 11th, input without spaces like below.```1345611```',
        inline=False
    )
    INSTRUCTION_PAGES_EN[0].add_field(
        name='Sokuji\'s Ranks Input (2v2, 3v3, 4v4)',
        value='If team1\'s ranks are 1st,2nd,3rd, team2\'s ranks are 4th,5th,6ht, team3\'s ranks are 7th,8th,9ht, and team4\'s ranks are 10th,11th,12th,'
        'input with space separator for each team or by sending by team like below.'
        '```123 456 789 101112```or```\n123\n456\n789\n101112```',
        inline=False
    )
    INSTRUCTION_PAGES_EN[0].add_field(
        name='Sokuji\'s Track Input',
        value='If this bot has sent track information between the last sokuji\'s ranks input and the next ranks input, the latest one is attached sokuji.\n'
        '__During the war, it is recommended to send the track as soon as it is selected!__',
        inline=False
    )
    INSTRUCTION_PAGES_EN[0].add_field(
        name='Sokuji\'s Banner Overlay',
        value='```%banner```Sokuji can be reflected in the broadcast by setting the URL sent by this bot to the broadcast software such as OBS.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[0].add_field(
        name='Result Image (6v6 only)',
        value='```%result```'
    )
    INSTRUCTION_PAGES_EN[0].add_field(
        name='Send Table (6v6 only)',
        value='```%send #channel```'
    )
    INSTRUCTION_PAGES_EN[0].add_field(
        name='Track Information',
        value='If there is a message with only the track name, this bot sends the location of the track selection and the item table map.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Change One Tag',
        value='```%tag tagNumber newTag```'
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Change All Tags',
        value='```%tags tag1 tag2 ...```Input as many `tag`s as there are teams.'
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Change Total Number Of Races',
        value='```%raceNum newTotalNumberOfRaces```alias : `%rn`',
        inline=False
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Restore One Previous State',
        value='```%back```'
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Change One Track',
        value='```%track raceNumber newTrack```'
        'If newTrack is not existed, you can delete the track of the raceNum\'s race.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Change Ranks of One Race',
        value='```%race raceNumter ranks```If the format is not 6v6, you can input only with space separator for each team.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Add Repick',
        value='```%repick tag```If only `%repick` (not tag), adds repick to team1.'
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Add Penalty',
        value='```%penalty score tag```If you wants to deduct scores, put a minus sign.'
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Stop Updating Banner',
        value='```%removeBanner```alias : `%rb`',
        inline=False
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Translate into English',
        value='```%englishize```alias : `%en`'
    )
    INSTRUCTION_PAGES_EN[1].add_field(
        name='Translate into Japanese',
        value='```%japanize```alias : `%ja`'
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='MMR',
        value='```%mmr (player)``` `%mmr4` shows mmr in the S4.'
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='stats',
        value='```%stats (player)``` `%stats4` shows stats in the S4.'
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='Table',
        value='```%table <id>```',
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='first',
        value='```%first# (player)``` `%first10` shows first 10 stats.'
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='mid',
        value='```%mid#-# (player)``` `%mid10-20` shows midium 10-20 stats.'
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='last',
        value='```%last# (player)``` `%last10` shows last 10 stats.'
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='The Latest Table',
        value='```%lm (player)``` `%lm2` shows second latest table.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='The Latest Table (in the format)',
        value='```%flm <format> (player)``` `%flm2 6` shows second latest table in 6v6.'
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name='The Latest Table (in the tier)',
        value='```%tlm <tier> (player)``` `%tlm3 sq` shows third latest table in tier SQ.'
    )
    INSTRUCTION_PAGES_EN[2].add_field(
        name=':warning: `(player)` in Commands',
        value='If not specified, show the command sender\'s.\n'
        'Multiple specifications are possible depending on the command. The method is `,` delimited. Mention and lounge name confusion is OK.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[3].add_field(
        name='Choose One at Random',
        value='```%choose A B C ...```alias : `%chs`',
        inline=False
    )
    INSTRUCTION_PAGES_EN[3].add_field(
        name='FC',
        value='```%fc (player)```'
    )
    INSTRUCTION_PAGES_EN[3].add_field(
        name='MKC Links',
        value='```%mkc (player)```'
    )
    INSTRUCTION_PAGES_EN[3].add_field(
        name=':warning: `(player)` in Commands',
        value='If not specified, show the command sender\'s.\n'
        'Multiple specifications are possible depending on the command. The method is `,` delimited. Mention and lounge name confusion is OK.',
        inline=False
    )
    INSTRUCTION_PAGES_EN[3].add_field(
        name='Need More Commands',
        value='DM <@426317116958965764> !'
    )
    INSTRUCTION_PAGES_EN[4].add_field(
        name='Consecutive Ranks',
        value='If ranks are 4th,5th,6th,7th,8th,9th, you can input like below.```4-9```',
        inline=False
    )
    INSTRUCTION_PAGES_EN[4].add_field(
        name='Top N',
        value='If your team get top 6, you can input without 1st like below.```-6```',
        inline=False
    )
    INSTRUCTION_PAGES_EN[4].add_field(
        name='Bottom N',
        value='If your team get 3rd,5th,6th,10th,11th,12th (includes bottom 3), you can input without bottom 3 like below.```356```',
        inline=False
    )
    INSTRUCTION_PAGES_EN[4].add_field(
        name='10th, 11th, and 12th',
        value='The alternative for "10" is "0". And the alternative for "11" is "+". 12th is included in bottom N, so you don\'t have to input "12".',
        inline=False
    )
