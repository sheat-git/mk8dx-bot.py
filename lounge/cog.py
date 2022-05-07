from typing import Optional, Union
import re
import asyncio
from discord import Embed, Message
import discord
from discord.abc import Messageable
from discord.ext import commands
from discord.utils import format_dt
from components import ColoredEmbed
from .components import LoungeEmbed
from mk8dx import lounge_api


NOW_SEASON = 6

_DISCORD_ID_RE = re.compile(r'<@.?[0-9]*?>')
_INT_RE = re.compile(r'[0-9]+')

class LoungeCog(commands.Cog, name='Lounge'):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    def extract_queries(self, ctx: commands.Context, players_text: Optional[str]) -> list[Union[str, int]]:
        queries = []
        if players_text is not None:
            for ps in map(lambda ps: ps.strip(), players_text.split(',')):
                for name in map(lambda n: n.strip(), _DISCORD_ID_RE.split(ps)):
                    if name:
                        queries.append(name)
                for id in _DISCORD_ID_RE.findall(ps):
                    queries.append(int(_INT_RE.search(id).group()))
        if not queries:
            queries = [ctx.author.id]
        return queries

    def extract_query(self, ctx: commands.Context, player_text: Optional[str]) -> Union[str, int]:
        if player_text is None or not player_text:
            return ctx.author.id
        s = _DISCORD_ID_RE.search(player_text)
        if s is None:
            return player_text
        return int(_INT_RE.search(s.group()).group())

    async def get_players(self, queries: list[Union[int, str]], season: Optional[int] = None) -> list[lounge_api.Player]:
        player_aws = []
        for query in queries:
            if isinstance(query, int):
                player_aws.append(lounge_api.get_player(discord_id=query, season=season))
            else:
                player_aws.append(lounge_api.get_player(name=query, season=season))
        return await asyncio.gather(*player_aws)

    async def get_player_detailses(self, queries: list[Union[int, str]], season: Optional[int] = None) -> list[lounge_api.PlayerDetails]:
        details_aws = []
        for query in queries:
            if isinstance(query, int):
                details_aws.append(self.get_player_details(discord_id=query, season=season))
            else:
                details_aws.append(lounge_api.get_player_details(name=query, season=season))
        return await asyncio.gather(*details_aws)

    async def get_player_details(self, discord_id: int, season: Optional[int] = None) -> Optional[lounge_api.PlayerDetails]:
        player = await lounge_api.get_player(discord_id=discord_id)
        if player is None:
            return None
        return await lounge_api.get_player_details(id=player.id, season=season)

    async def filter_not_found(
        self,
        ctx: commands.Context,
        queries: list[Union[str, int]],
        items: list
    ) -> list[Union[str, int]]:
        none_queries = []
        for i in range(len(queries)):
            if items[i] is None:
                items.pop(i)
                none_queries.append(queries[i])
        if none_queries:
            content = 'Not Found: ' + ', '.join(map(
                lambda q: f'<@!{q}>' if isinstance(q, int) else q,
                none_queries
            ))
            await ctx.send(content)

    @commands.command(
        name='mkc',
        aliases=['getMKC'],
        brief='Shows MKC Profile and Forum links'
    )
    async def mkc(self, ctx: commands.Context, *, players_text: Optional[str]):
        queries = self.extract_queries(ctx=ctx, players_text=players_text)
        players = await self.get_players(queries=queries)
        await self.filter_not_found(ctx=ctx, queries=queries, items=players)
        if not players:
            return
        if len(players) > 25:
            await ctx.send('There are too many args. The upper limit is 25. I will show only 25 players.')
        embed = ColoredEmbed(
            title='MKC Links'
        )
        for player in players[:25]:
            embed.add_field(
                name=f'{player.name} ({player.mkc_id})',
                value=f'[Profile](https://www.mariokartcentral.com/mkc/registry/users/{player.mkc_id})\n'
                f'[Forum](https://www.mariokartcentral.com/forums/index.php?members/{player.mkc_id})'
            )
        await ctx.send(embed=embed)

    @commands.command(
        name='fc',
        brief='Shows switch\'s friend code'
    )
    async def fc(self, ctx: commands.Context, *, players_text: Optional[str]):
        queries = self.extract_queries(ctx=ctx, players_text=players_text)
        players = await self.get_players(queries=queries)
        await self.filter_not_found(ctx=ctx, queries=queries, items=players)
        if not players:
            return
        if len(players) > 25:
            await ctx.send('There are too many args. The upper limit is 25. I will show only 25 players.')
            players = players[:25]
        embed = ColoredEmbed(
            title='Switch FC'
        )
        if len(players) > 1:
            embed.title += 's'
        for player in players:
            embed.add_field(
                name=player.name,
                value=player.switch_fc
            )
        await ctx.send(embed=embed)

    async def _mmr(self, ctx: commands.Context, players_text: Optional[str], season: Optional[int] = None):
        queries = self.extract_queries(ctx=ctx, players_text=players_text)
        players = await self.get_players(queries=queries, season=season)
        await self.filter_not_found(ctx=ctx, queries=queries, items=players)
        if not players:
            return
        if len(players) > 24:
            await ctx.send('There are too many args. The upper limit is 24. I will show only 24 players.')
            players = players[:24]
        if season is None:
            embed = ColoredEmbed(
                title='MMR'
            )
            season_q = ''
        else:
            embed = ColoredEmbed(
                title=f'S{season} MMR'
            )
            season_q = f'?season={season}'
        for player in players:
            embed.add_field(
                name=player.name,
                value=f'[{player.mmr}](https://www.mk8dx-lounge.com/PlayerDetails/{player.id}{season_q})'
            )
        if len(players) > 1:
            embed.title += 's'
            embed.add_field(
                name='Avg.',
                value='{:.1f}'.format(sum(map(lambda p: p.mmr, players)) / len(players))
            )
        await ctx.send(embed=embed)

    @commands.command(
        name='mmr',
        brief='Shows mmr'
    )
    async def mmr(self, ctx: commands.Context, *, players_text: Optional[str]):
        await self._mmr(ctx, players_text)

    async def table_embed(self, table: lounge_api.TableDetails) -> Embed:
        def table_text() -> Optional[str]:
            scores: list[lounge_api.TableDetails.Score] = []
            for team in table.teams:
                scores.extend(team.scores)
            max_name_length = max(map(lambda s: len(s.player_name), scores))
            text = '```\n'
            for score in scores:
                if score.prev_mmr is None or score.new_mmr is None or score.delta is None:
                    return
                text += score.player_name.ljust(max_name_length) + \
                ':{:>5} ⇨{:>5} ({:>+4})\n'.format(score.prev_mmr, score.new_mmr, score.delta)
            return text + '```'
        embed = ColoredEmbed(
            title='Table'
        )
        embed.add_field(
            name='ID',
            value=f'[{table.id}](https://www.mk8dx-lounge.com/TableDetails/{table.id})'
        )
        format = 12 // table.num_teams
        embed.add_field(
            name='Format',
            value='FFA' if format == 1 else f'{format}v{format}'
        )
        embed.add_field(
            name='Tier',
            value=table.tier
        )
        embed.add_field(
            name='Season',
            value=table.season
        )
        embed.add_field(
            name='Created on',
            value=format_dt(table.created_on)
        )
        if table.verified_on is not None:
            embed.add_field(
                name='Verified on',
                value=format_dt(table.verified_on)
            )
        if table.deleted_on is not None:
            embed.add_field(
                name='Deleted on',
                value=format_dt(table.deleted_on)
            )
        text = table_text()
        if text is not None:
            embed.add_field(
                name='MMR Changes',
                value=text,
                inline=False
            )
        embed.set_image(url=f'https://www.mk8dx-lounge.com{table.url}')
        return embed

    @commands.command(
        name='table',
        brief='Shows table'
    )
    async def table(self, ctx: commands.Context, table_id: int):
        table = await lounge_api.get_table(table_id)
        if table is None:
            await ctx.send('Table Not Found')
        await ctx.send(embed=await self.table_embed(table=table))

    async def _lastmatch(
        self,
        ctx: commands.Context,
        count: int = 1,
        player_text: Optional[str] = None,
        filter = lambda _: True
    ):
        query = self.extract_query(ctx=ctx, player_text=player_text)
        if isinstance(query, int):
            details = await self.get_player_details(discord_id=query)
            if details is None:
                await ctx.send(f'Not Found: <@!{query}>')
                return
        else:
            details = await lounge_api.get_player_details(name=query)
            if details is None:
                await ctx.send(f'Not Found: {query}')
                return
        season = NOW_SEASON
        while details is not None:
            for change in details.mmr_changes:
                if change.reason == lounge_api.PlayerDetails.MmrChange.Reason.TABLE and filter(change):
                    count -= 1
                    if count == 0:
                        table_id = change.change_id
                        break
            if count == 0:
                break
            season -= 1
            details = await lounge_api.get_player_details(id=details.player_id, season=season)
        if count != 0:
            await ctx.send('Valid Table Not Found')
            return
        await self.table(ctx, table_id)


    @commands.command(
        name='lastmatch',
        aliases=['lm'],
        brief='Shows the lastest table'
    )
    async def lastmatch(self, ctx: commands.Context, *, player: Optional[str] = None):
        await self._lastmatch(ctx, player_text=player)

    @commands.command(
        name='formatlastmatch',
        aliases=['flm'],
        brief='Shows the lastest table in the format'
    )
    async def formatlastmatch(self, ctx, *, player: Optional[str] = None):
        await self._lastmatch(ctx, player_text=player)

    @commands.command(
        name='tierlastmatch',
        aliases=['tlm'],
        brief='Shows the lastest table in the tier'
    )
    async def tierlastmatch(self, ctx, *, player: Optional[str] = None):
        await self._lastmatch(ctx, player_text=player)

    @commands.Cog.listener(name='on_command_error')
    async def additional_commands(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandNotFound):
            command = ctx.message.content[1:]
            command_name = command.split(maxsplit=1)[0]
            arg = command.replace(command_name, '', 1).strip()
            if command_name.startswith('mmr'):
                season = int(command_name[3:])
                await self._mmr(ctx=ctx, players_text=arg, season=season)
                return
            if command_name.startswith(('lastmatch', 'lm')):
                count = int(command_name[2:]) if command_name.startswith('lm') else int(command_name[9:])
                await self._lastmatch(ctx=ctx, count=count, player_text=arg)
                return
            if command_name.startswith(('formatlastmatch', 'flm')):
                format = int(command_name[3:]) if command_name.startswith('flm') else int(command_name[15:])
                if not format in {1, 2, 3, 4, 6}:
                    await ctx.send(f'Invalid Format: {format}')
                    return
                num_teams = 12 // format
                await self._lastmatch(ctx=ctx, player_text=arg, filter=lambda c: c.num_teams == num_teams)
                return
            if command_name.startswith(('tierlastmatch', 'tlm')):
                tier = (command_name[3:] if command_name.startswith('tlm') else command_name[13:]).upper()
                await self._lastmatch(ctx=ctx, player_text=arg, filter=lambda c: c.tier == tier)
                return
        raise error
