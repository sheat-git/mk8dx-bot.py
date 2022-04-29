from __future__ import annotations

from typing import Optional
from discord import Embed, Message
from discord.abc import Messageable
from datetime import datetime, timedelta
from mk8dx import Mogi, Race, Rank, Track
from ..locale import Locale


async def find(messageable: Messageable, user_id: int) -> tuple[Optional[Sokuji], Optional[SubSokuji], Optional[Track]]:
    sokuji = None
    subsokuji = None
    track = None
    async for message in messageable.history(after=datetime.now()-timedelta(minutes=30)):
        if message.author.id == user_id and message.embeds:
            embed = message.embeds[0]
            if Sokuji.embed_is_valid(embed=embed):
                sokuji = Sokuji(embed=embed)
                if not subsokuji is None:
                    subsokuji.locale = sokuji.locale
                return sokuji, subsokuji, track
            elif embed.title.split('  -', maxsplit=1)[0].isdecimal():
                subsokuji = SubSokuji(embed=embed)
            elif not track is None:
                track = Track(embed.title)
    return None, None, None


class Sokuji:

    __slots__ = (
        'embed'
    )

    def __init__(self, embed: Embed) -> None:
        self.embed: Embed = embed

    @property
    def format(self) -> int:
        return int(self.embed.title.split('v', maxsplit=1)[0][-1])

    @property
    def tags(self) -> list[str]:
        return list(self.embed.title.split('\n', maxsplit=1)[-1].split(' - '))

    @property
    def sum_scores(self) -> list[int]:
        sum_scores_text: str = self.embed.description.replace('`', '').split('  @', maxsplit=1)[0]
        return Sokuji.text_to_scores(text=sum_scores_text)

    @sum_scores.setter
    def sum_scores(self, sum_scores: list[int]) -> None:
        self.embed.description = f'`{Sokuji.scores_to_text(scores=sum_scores)}`  `@{self.embed.description.split("`  `@", maxsplit=1)[-1]}'

    @property
    def left_race_num(self) -> int:
        left_race_num_text: str = self.embed.description.replace('`', '').split('  @', maxsplit=1)[-1]
        return int(left_race_num_text)

    @left_race_num.setter
    def left_race_num(self, left_race_num: int) -> None:
        self.embed.description = f'`{self.embed.description.split("`  `@", maxsplit=1)[0]}`  `@{left_race_num}`'

    def dif_update(self, sum_scores_dif: list[int], left_race_num_dif: int) -> None:
        sum_scores = self.sum_scores
        for i in range(len(sum_scores)):
            sum_scores[i] += sum_scores_dif[i]
        left_race_num = self.left_race_num + left_race_num_dif
        self.embed.description = f'{Sokuji.scores_to_text(scores=sum_scores)}`  `@{left_race_num}`'

    @property
    def race_num(self) -> int:
        for field in reversed(self.embed.fields):
            text = field.name.split(maxsplit=1)[0]
            if text.isdecimal():
                return int(text)
        return 0

    @property
    def total_race_num(self) -> int:
        return self.race_num + self.left_race_num

    @total_race_num.setter
    def total_race_num(self, total_race_num) -> None:
        self.left_race_num = total_race_num - self.race_num

    @property
    def banner_user(self) -> set[str]:
        if not self.embed.footer.text:
            return set()
        return set(self.embed.footer.text.split(' for @', maxsplit=1)[-1].split(',@'))

    @banner_user.setter
    def banner_user(self, banner_user: set[str]) -> None:
        if not banner_user:
            self.embed.remove_footer()
            return
        if self.locale == Locale.JA:
            self.embed.set_footer(text='バナー更新 for @' + ',@'.join(banner_user))
            return
        self.embed.set_footer('Updating banner for @' + ',@'.join(banner_user))

    @property
    def locale(self) -> Locale:
        title = self.embed.title
        if title.startswith('即時'):
            return Locale.JA
        return Locale.EN

    @locale.setter
    def locale(self, locale) -> None:
        if locale == self.locale:
            return
        if locale == Locale.JA:
            self.embed.title.replace('Sokuji', '即時集計')
            if self.embed.footer:
                self.embed.footer.text.replace('Updating banner', 'バナー更新')
            return
        self.embed.title.replace('即時集計', 'Sokuji')
        if self.embed.footer:
            self.embed.footer.text.replace('バナー更新', 'Updating banner')

    def add_field(self, name: str, value: str, inline: bool = False) -> None:
        if len(self.embed._fields) >= 25:
            self.embed._fields.pop(0)
        self.embed.add_field(name=name, value=value, inline=inline)

    def back(self) -> bool:
        for i in range(0, -len(self.embed.fields, -1)):
            text = self.embed.fields[i].name.split(maxsplit=1)[0]
            if text.isdecimal():
                field = self.embed.fields.pop(i)
                scores = Sokuji.text_to_scores(text=field.value.split('` | `', maxsplit=1)[0][1:])
                self.dif_update(sum_scores_dif=list(map(lambda s: -s, scores)), left_race_num_dif=1)
                return True
        return False

    def add_race(self, race: Race) -> None:
        race_num = self.race_num + 1
        if race.track is None:
            name = str(race_num)
        elif self.locale == Locale.JA:
            name = f'{race_num}  - {race.track.abbr_ja}'
        else:
            name = f'{race_num}  - {race.track.abbr}'
        self.add_field(name=name, value=f'`{Sokuji.scores_to_text(scores=race.scores, format=self.format)}` | `{",".join(map(str, race.ranks[0].data))}`')

    def add_text(self, text: str, track: Optional[Track] = None) -> Optional[SubSokuji]:
        format = self.format
        if format == 6:
            race = Race(format=format, track=track)
            race.add_ranks_from_text(text=text)
            if race.is_valid():
                self.add_race(race=race)
            return
        sub = SubSokuji.from_sokuji(sokuji=self, track=track)
        sub.add_text(text=text)
        return sub

    def add_subsokuji(self, subsokuji: SubSokuji):
        self.add_race(race=subsokuji.to_race())

    @staticmethod
    def from_mogi(mogi: Mogi, locale: Locale = Locale.JA, banner_user: list[str] = [], total_race_num: int = 12) -> Sokuji:
        if locale == Locale.JA:
            title = f'即時集計 {mogi.format}v{mogi.format}\n{" - ".join(mogi.tags)}'
        else:
            title = f'Sokuji {mogi.format}v{mogi.format}\n{" - ".join(mogi.tags)}'
        description = f'`{Sokuji.scores_to_text(scores=mogi.sum_scores, format=mogi.format)}`  `@{total_race_num - len(mogi.races)}`'
        sokuji = Sokuji(embed=Embed(title=title, description=description))
        sokuji.banner_user = banner_user
        for race in mogi.races:
            sokuji.add_race(race=race)
        return sokuji

    @staticmethod
    def scores_to_text(scores: list[int], format: Optional[int] = None) -> str:
        if not scores:
            return ''
        if format is None:
            format = 12 // len(scores)
        if format == 2:
            return ' : '.join(map(str, scores))
        text = str(scores[0])
        for score in scores[1:]:
            text += ' : {}({:+})'.format(score, scores[0]-score)
        return text

    @staticmethod
    def text_to_scores(text: str) -> list[int]:
        return list(map(lambda x: int(x.split('(')[0]), text.split(' : ')))

    @staticmethod
    def start(tags: list[str] = [], format: Optional[int] = None, locale: Locale = Locale.JA) -> Sokuji:
        mogi = Mogi.start(tags=tags, format=format)
        sokuji = Sokuji.from_mogi(mogi=mogi, locale=locale)
        return sokuji

    async def send(self, messageable: Messageable) -> Message:
        return await messageable.send(embed=self.embed)

    @staticmethod
    def embed_is_valid(embed: Embed) -> bool:
        title = embed.title
        return title.startswith('即時集計') or title.startswith('Sokuji')


class SubSokuji:

    __slots__ = (
        'embed',
        'locale'
    )

    def __init__(self, embed: Embed, locale: Locale = Locale.JA) -> None:
        self.embed: Embed = embed
        self.locale: Locale = locale

    @property
    def format(self) -> int:
        return 12 // len(self.embed._fields)

    @property
    def track(self) -> Optional[Track]:
        if '-' in self.embed.title:
            return Track.from_nick(self.embed.title.split('- ', maxsplit=1)[-1])

    @track.setter
    def track(self, track: Optional[Track]) -> None:
        race_num_text = self.embed.title.split('  -', maxsplit=1)[0]
        if track is None:
            self.embed.title = race_num_text
        elif self.locale == Locale.JA:
            self.embed.title = f'{race_num_text}  - {track.abbr_ja}'
        else:
            self.embed.title = f'{race_num_text}  - {track.abbr}'

    @property
    def ranks(self) -> list[Rank]:
        ranks = []
        for _field in self.embed._fields:
            if not _field.get('value', ''):
                break
            ranks.append(SubSokuji.text_to_rank(_field['value']))
        return ranks

    def to_race(self) -> Race:
        return Race(format=self.format, ranks=self.ranks, track=self.track)

    def is_valid(self) -> bool:
        for _field in self.embed._fields:
            if not _field.get('value', ''):
                return False
        return True

    def add_text(self, text: str) -> None:
        ranks = Rank.get_ranks_from_text(text=text, format=self.format, ranks=self.ranks)
        for i in range(len(self.embed._fields)):
            if not ranks:
                return
            if not self.embed._fields[i].get('value', ''):
                self.embed._fields[i]['value'] = SubSokuji.rank_to_text(rank=ranks.pop(0))
    
    @staticmethod
    def rank_to_text(rank: Rank) -> str:
        return f'score : `{rank.score}` | rank : `{",".join(rank.data)}`'
    
    @staticmethod
    def text_to_rank(text: str) -> Rank:
        return Rank(data=list(map(int, text.split('rank : `', maxsplit=1)[-1][:-1].split(','))))

    @staticmethod
    def from_sokuji(sokuji: Sokuji, track: Optional[Track] = None) -> SubSokuji:
        locale = sokuji.locale
        if track is None:
            title = f'{sokuji.race_num+1}'
        elif locale == Locale.JA:
            title = f'{sokuji.race_num+1}  - {track.abbr_ja}'
        else:
            title = f'{sokuji.race_num+1}  - {track.abbr}'
        embed = Embed(title=title)
        for tag in sokuji.tags:
            embed.add_field(name=tag, inline=False)
        return SubSokuji(embed=embed, locale=locale)
