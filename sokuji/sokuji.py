from __future__ import annotations

from typing import Optional, Any

from components import ColoredEmbed as Embed
from discord import Message, Interaction
from discord.abc import Messageable
from discord.ui import View, Button
from datetime import datetime, timedelta
from mk8dx import Mogi, Race, Rank, Track
from track.emoji import TrackEmoji
from locale_ import Locale
from .firebase import update


async def find(messageable: Messageable, user_id: int, include_ended=False) -> tuple[Optional[BotMessage], Optional[BotMessage], Optional[Track]]:
    sokuji_message = None
    subsokuji_message = None
    track = None
    async for message in messageable.history(after=datetime.now()-timedelta(minutes=30), oldest_first=False):
        if message.author.id == user_id and message.embeds:
            embed = message.embeds[0]
            if Sokuji.embed_is_ended(embed=embed) and not include_ended:
                break
            elif Sokuji.embed_is_valid(embed=embed) or Sokuji.embed_is_ended(embed=embed) and include_ended:
                sokuji_message = BotMessage(message, Sokuji(embed=embed))
                if not subsokuji_message is None:
                    subsokuji_message.data.locale = sokuji_message.data.locale
                break
            elif subsokuji_message is None and embed.title.split('  -', maxsplit=1)[0].isdecimal():
                subsokuji_message = BotMessage(message, SubSokuji(embed=embed))
            elif track is None:
                track = Track.from_nick(embed.title.split(maxsplit=1)[0])
    return sokuji_message, subsokuji_message, track


class BotMessage:

    __slots__ = (
        'message',
        'data'
    )

    def __init__(self, message: Message, data: Any) -> None:
        self.message: Message = message
        self.data = data


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

    @tags.setter
    def tags(self, tags: list[str]):
        title_text = self.embed.title.split('\n', maxsplit=1)[0]
        self.embed.title = f'{title_text}\n{" - ".join(tags)}'

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
        self.embed.description = f'{self.embed.description.split("`  `@", maxsplit=1)[0]}`  `@{left_race_num}`'

    def dif_update(self, sum_scores_dif: list[int], left_race_num_dif: int) -> None:
        sum_scores = self.sum_scores
        for i in range(len(sum_scores)):
            sum_scores[i] += sum_scores_dif[i]
        left_race_num = self.left_race_num + left_race_num_dif
        self.embed.description = f'`{Sokuji.scores_to_text(scores=sum_scores)}`  `@{left_race_num}`'

    @property
    def race_num(self) -> int:
        for field in reversed(self.embed.fields):
            text = field.name.split(maxsplit=1)[0]
            if text.isdecimal():
                return int(text)
        return 0

    @property
    def min_race_num(self) -> int:
        for field in self.embed.fields:
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
    def banner_users(self) -> set[str]:
        if not self.embed.footer.text:
            return set()
        return set(self.embed.footer.text.split(' for @', maxsplit=1)[-1].split(',@'))

    @banner_users.setter
    def banner_users(self, banner_users: set[str]) -> None:
        if not banner_users:
            self.embed.remove_footer()
            return
        if self.locale == Locale.JA:
            self.embed.set_footer(text='バナー更新 for @' + ',@'.join(banner_users))
            return
        self.embed.set_footer(text='Updating banner for @' + ',@'.join(banner_users))

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
            if self.embed.title.startswith('Sokuji'):
                self.embed.title = self.embed.title.replace('Sokuji', '即時集計', 1)
            elif self.embed.title.startswith('Archive'):
                self.embed.title = self.embed.title.replace('Archive', '即時アーカイブ', 1)
            for i in range(len(self.embed.fields)):
                if self.embed._fields[i]['name'].split(maxsplit=1)[0].isdecimal() and '-' in self.embed._fields[i]['name']:
                    track = Track.from_nick(self.embed._fields[i]['name'].split()[-1])
                    if track is None:
                        continue
                    self.embed._fields[i]['name'] = self.embed._fields[i]['name'].replace(f' {track.abbr}', f' {track.abbr_ja}')
            if self.embed.footer:
                self.embed._footer['text'] = self.embed._footer['text'].replace('Updating banner', 'バナー更新')
            return
        if self.embed.title.startswith('即時集計'):
            self.embed.title = self.embed.title.replace('即時集計', 'Sokuji', 1)
        elif self.embed.title.startswith('即時アーカイブ'):
            self.embed.title = self.embed.title.replace('即時アーカイブ', 'Archive', 1)
        for i in range(len(self.embed.fields)):
            if self.embed._fields[i]['name'].split(maxsplit=1)[0].isdecimal() and '-' in self.embed._fields[i]['name']:
                track = Track.from_nick(self.embed._fields[i]['name'].split()[-1])
                if track is None:
                    continue
                self.embed._fields[i]['name'] = self.embed._fields[i]['name'].replace(track.abbr_ja, track.abbr)
        if self.embed.footer:
            self.embed._footer['text'] = self.embed._footer['text'].replace('バナー更新', 'Updating banner')

    def toggle_locale(self) -> None:
        if self.locale == Locale.JA:
            self.locale = Locale.EN
        else:
            self.locale = Locale.JA

    @property
    def scores(self) -> list[list[int]]:
        scores = [self.sum_scores]
        for field in reversed(self.embed.fields):
            text = field.value.split('`', maxsplit=3)[1]
            scores.append([score-incleased_score for score, incleased_score in zip(scores[-1], Sokuji.text_to_scores(text))])
        scores.reverse()
        return scores

    def edit_track(self, race_num: Optional[int], track: Optional[Track]) -> bool:
        if race_num is None:
            race_num = self.race_num
        race_num_text = str(race_num)
        for i in range(len(self.embed.fields)):
            if self.embed._fields[i]['name'].split(maxsplit=1)[0] == race_num_text:
                if track is None:
                    name = race_num_text
                elif self.locale == Locale.JA:
                    name = f'{race_num_text}  - {TrackEmoji(track.id)} {track.abbr_ja}'
                else:
                    name = f'{race_num_text}  - {TrackEmoji(track.id)} {track.abbr}'
                self.embed._fields[i]['name'] = name
                return True
        return False

    def edit_race(self, race_num: int, text: str) -> bool:
        race_num_text = str(race_num)
        race = Race(format=self.format, ranks=[])
        race.add_ranks_from_text(text=text)
        if not race.is_valid():
            return False
        for i in range(len(self.embed.fields)):
            if self.embed._fields[i]['name'].split(maxsplit=1)[0] == race_num_text:
                scores_dif = []
                for old, new in zip(
                    Sokuji.text_to_scores(text=self.embed._fields[i]['value'].split('` | `', maxsplit=1)[0][1:]),
                    race.scores
                ):
                    scores_dif.append(-old+new)
                self.embed._fields[i]['value'] = f'`{Sokuji.scores_to_text(scores=race.scores, format=self.format)}` | `{",".join(map(str, race.ranks[0].data))}`'
                self.dif_update(sum_scores_dif=scores_dif, left_race_num_dif=0)
                return True
        return False

    def add_field(self, name: str, value: str, inline: bool = False) -> None:
        if len(self.embed.fields) >= 25:
            self.embed._fields.pop(0)
        self.embed.add_field(name=name, value=value, inline=inline)

    def back(self) -> bool:
        for i in range(-1, -len(self.embed.fields)-1, -1):
            text = self.embed.fields[i].name.split(maxsplit=1)[0]
            if text.isdecimal():
                _field = self.embed._fields.pop(i)
                scores = Sokuji.text_to_scores(text=_field['value'].split('` | `', maxsplit=1)[0][1:])
                self.dif_update(sum_scores_dif=list(map(lambda s: -s, scores)), left_race_num_dif=1)
                return True
            if text in {'Repick', 'Penalty'}:
                _field = self.embed._fields.pop(i)
                scores = Sokuji.text_to_scores(text=_field['value'][1:-1])
                self.dif_update(sum_scores_dif=list(map(lambda s: -s, scores)), left_race_num_dif=0)
                return True
        return False

    def add_repick(self, tag: Optional[str]) -> bool:
        if tag is None:
            tag_index = 0
        else:
            if not tag in self.tags:
                return False
            tag_index = self.tags.index(tag)
        scores = [0]*(12//self.format)
        scores[tag_index] = -15
        self.dif_update(sum_scores_dif=scores, left_race_num_dif=0)
        self.add_field(name=f'Repick', value=f'`{Sokuji.scores_to_text(scores=scores, simple=True)}`')
        return True
    
    def add_penalty(self, penalty: int, tag: Optional[str]) -> bool:
        if tag is None:
            tag_index = 0
        else:
            if not tag in self.tags:
                return False
            tag_index = self.tags.index(tag)
        scores = [0]*(12//self.format)
        scores[tag_index] = penalty
        self.dif_update(sum_scores_dif=scores, left_race_num_dif=0)
        self.add_field(name=f'Penalty', value=f'`{Sokuji.scores_to_text(scores=scores, simple=True)}`')
        return True

    def add_race(self, race: Race) -> None:
        race_num = self.race_num + 1
        if race.track is None:
            name = str(race_num)
        else:
            if self.locale == Locale.JA:
                name = f'{race_num}  - {TrackEmoji(race.track.id)} {race.track.abbr_ja}'
            else:
                name = f'{race_num}  - {TrackEmoji(race.track.id)} {race.track.abbr}'
        self.add_field(name=name, value=f'`{Sokuji.scores_to_text(scores=race.scores, format=self.format)}` | `{",".join(map(str, race.ranks[0].data))}`')
        self.dif_update(sum_scores_dif=race.scores, left_race_num_dif=-1)

    def add_text(self, text: str, track: Optional[Track] = None) -> Optional[SubSokuji]:
        format = self.format
        if format == 6:
            race = Race(format=format, ranks=[], track=track)
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
    def from_mogi(mogi: Mogi, locale: Locale = Locale.JA, banner_users: list[str] = [], total_race_num: int = 12) -> Sokuji:
        if locale == Locale.JA:
            title = f'即時集計 {mogi.format}v{mogi.format}\n{" - ".join(mogi.tags)}'
        else:
            title = f'Sokuji {mogi.format}v{mogi.format}\n{" - ".join(mogi.tags)}'
        description = f'`{Sokuji.scores_to_text(scores=mogi.sum_scores, format=mogi.format)}`  `@{total_race_num - len(mogi.races)}`'
        sokuji = Sokuji(embed=Embed(title=title, description=description))
        sokuji.banner_users = banner_users
        for race in mogi.races:
            sokuji.add_race(race=race)
        return sokuji

    @staticmethod
    def scores_to_text(scores: list[int], format: Optional[int] = None, simple: bool = False) -> str:
        if not scores:
            return ''
        if format is None:
            format = 12 // len(scores)
        if format == 2 or simple:
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
        mogi = Mogi(tags=tags, format=format)
        sokuji = Sokuji.from_mogi(mogi=mogi, locale=locale)
        return sokuji

    def end(self):
        if self.locale == Locale.JA:
            self.embed.title = self.embed.title.replace('即時集計', '即時アーカイブ', 1)
        else:
            self.embed.title = self.embed.title.replace('Sokuji', 'Archive', 1)

    def resume(self):
        if self.locale == Locale.JA:
            self.embed.title = self.embed.title.replace('即時アーカイブ', '即時集計', 1)
        else:
            self.embed.title = self.embed.title.replace('Archive', 'Sokuji', 1)

    async def send(self, messageable: Messageable) -> None:
        if self.race_num == 0:
            await messageable.send(embed=self.embed, view=SokujiView(sokuji=self))
        else:
            await messageable.send(embed=self.embed)
        self.update_firebase()

    async def edit(self, message: Message) -> None:
        if self.race_num == 0:
            await message.edit(embed=self.embed, view=SokujiView(sokuji=self))
        else:
            await message.edit(embed=self.embed)
        self.update_firebase()
    
    def update_firebase(self):
        banner_users = self.banner_users
        if not banner_users:
            return
        sum_scores = self.sum_scores
        data = {}
        if self.format == 6:
            dif = sum_scores[0] - sum_scores[1]
            left = self.left_race_num
            win = int(dif > left*40)
            d = {'teams': self.tags, 'scores': sum_scores, 'left': left, 'dif': '{:+}'.format(dif), 'win': win}
            for user in banner_users:
                data[user] = d
            update(data)
            return
        teamscores = dict(zip(self.tags, sum_scores))
        teamscores: dict = sorted(teamscores.items(), key=lambda x:x[1], reverse=True)
        d = {'teams': list(map(lambda i: i[0], teamscores)), 'scores': list(map(lambda i: i[1], teamscores)), 'left': self.left_race_num}
        for user in banner_users:
            data[user] = d
        update(data)

    @staticmethod
    def embed_is_valid(embed: Embed) -> bool:
        title = embed.title
        return title.startswith('即時集計') or title.startswith('Sokuji')

    @staticmethod
    def embed_is_ended(embed: Embed) -> bool:
        title = embed.title
        return title.startswith('即時アーカイブ') or title.startswith('Archive')


class SokujiView(View):

    def __init__(self, sokuji: Sokuji) -> None:
        super().__init__()
        self.add_item(SokujiView.LoccalizeButton(sokuji.locale))

    class LoccalizeButton(Button):

        def __init__(self, locale: Locale):
            if locale == Locale.JA:
                super().__init__(label='English')
            else:
                super().__init__(label='日本語')
        
        async def callback(self, interaction: Interaction):
            message = interaction.message
            if message is None or not message.embeds:
                await interaction.response.send_message('This sokuji does not include data.')
                return
            sokuji = Sokuji(embed=message.embeds[0])
            sokuji.toggle_locale()
            await interaction.response.edit_message(embed=sokuji.embed, view=SokujiView(sokuji))


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
    def race_num(self) -> int:
        return int(self.embed.title.split(maxsplit=1)[0])

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
    def tags(self) -> list[str]:
        return list(map(lambda f: f.name, self.embed.fields))

    @tags.setter
    def tags(self, tags: list[str]):
        for i in range(min(len(tags), len(self.embed._fields))):
            self.embed._fields[i]['name'] = tags[i]

    @property
    def ranks(self) -> list[Rank]:
        ranks = []
        for field in self.embed.fields:
            if not 'rank' in field.value:
                break
            ranks.append(SubSokuji.text_to_rank(field.value))
        return ranks

    def __len__(self) -> int:
        i = 0
        for field in self.embed.fields:
            if not 'rank' in field.value:
                return i
            i += 1
        return i

    def to_race(self) -> Race:
        return Race(format=self.format, ranks=self.ranks, track=self.track)

    def is_valid(self) -> bool:
        for field in self.embed.fields:
            if not 'rank' in field.value:
                return False
        return True

    def add_text(self, text: str) -> None:
        ranks = Rank.get_ranks_from_text(text=text, format=self.format, ranks=self.ranks)
        for i in range(len(ranks)):
            if not 'rank' in self.embed._fields[i]['value']:
                self.embed._fields[i]['value'] = SubSokuji.rank_to_text(rank=ranks[i])

    def back(self) -> bool:
        for i in range(-1, -len(self.embed.fields)-1, -1):
            if 'rank' in self.embed._fields[i]['value']:
                self.embed._fields[i]['value'] = 'score : `0`'
                return True
        return False

    async def send(self, messageable: Messageable) -> Message:
        return await messageable.send(embed=self.embed)

    async def edit(self, message: Message) -> Message:
        return await message.edit(embed=self.embed)

    @staticmethod
    def rank_to_text(rank: Rank) -> str:
        return f'score : `{rank.score}` | rank : `{",".join(map(str, rank.data))}`'
    
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
            embed.add_field(name=tag, value='score : `0`', inline=False)
        return SubSokuji(embed=embed, locale=locale)
