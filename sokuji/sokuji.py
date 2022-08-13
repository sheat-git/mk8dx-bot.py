from __future__ import annotations
from typing import Optional, Sequence

from discord import Embed, EmbedField
from mk8dx import Track, Race

from lang import Lang
from components import BotMessage
from sokuji.errors import *
from track.emoji import TrackEmoji

from sokuji import result_image
from sokuji.firebase import update
from sokuji.sokuji_child import SokujiChild
from sokuji.components import SokujiEmbed


class Sokuji:

    def __init__(self, embed: Embed, child_embed: Optional[Embed] = None) -> None:
        self._embed: Embed = embed
        self._embed.remove_image()
        self._flag_title: bool = False
        self._flag_description: bool = False
        self._flag_fields_name: bool = False
        self._flag_footer: bool = False
        self.child: Optional[SokujiChild] = None
        if child_embed is not None:
            self.child = SokujiChild(embed=child_embed, lang=self.lang)

    @property
    def flag_title(self) -> bool:
        if self._flag_title:
            return True
        return self.tags != self._old_tags

    @flag_title.setter
    def flag_title(self, flag: bool) -> None:
        self._flag_title = flag
        if not flag:
            self._old_tags = self.tags

    @property
    def flag_description(self) -> bool:
        if self._flag_description:
            return True
        return self.sum_scores != self._old_sum_scores

    @flag_description.setter
    def flag_description(self, flag: bool) -> None:
        self._flag_description = flag
        if not flag:
            self._old_sum_scores = self.sum_scores

    @property
    def flag_fields_name(self) -> bool:
        return self._flag_fields_name

    @flag_fields_name.setter
    def flag_fields_name(self, flag: bool) -> None:
        self._flag_fields_name = flag

    @property
    def flag_footer(self) -> bool:
        if self._flag_footer:
            return True
        return self.banner_users != self._old_banner_users

    @flag_footer.setter
    def flag_footer(self, flag: bool) -> None:
        self._flag_footer = flag
        if not flag:
            self._old_banner_users = self.banner_users

    @staticmethod
    def start(
        tags: list[str],
        format: int,
        lang: Lang,
        total_race_num: Optional[int] = None,
        banner_users: Sequence[str] = set()
    ) -> Sokuji:
        if total_race_num is None:
            total_race_num = 12
        title = '即時集計' if lang == Lang.JA else 'Sokuji'
        title += f' {format}v{format}\n{" - ".join(tags)}'
        embed = SokujiEmbed(
            title=title,
            description=f'`{Sokuji.scores_to_text(scores=[0]*(12//format), format=format)}`  `@{total_race_num}`'
        )
        sokuji = Sokuji(embed=embed)
        sokuji.banner_users = set(banner_users)
        return sokuji

    @property
    def embed(self) -> Embed:
        if self.flag_title:
            title = '即時集計' if self.lang == Lang.JA else 'Sokuji'
            title += f' {self.format}v{self.format}\n{" - ".join(self.tags)}'
            self._embed.title = title
            self.flag_title = False
        if self.flag_description:
            self._embed.description = f'`{self.scores_to_text(scores=self.sum_scores, format=self.format)}`  `@{self.left_race_num}`'
            self.flag_description = False
        if self.flag_fields_name:
            for i in range(len(self._embed.fields)):
                name = self._embed.fields[i].name
                if name in {'Repick', 'Penalty'} or '-' not in name:
                    continue
                track = Track.from_nick(name.rsplit(maxsplit=1)[-1])
                if track is None:
                    continue
                abbr = track.abbr_ja if self.lang == Lang.JA else track.abbr
                self._embed._fields[i].name = f'{name.rsplit(maxsplit=1)[0]} {abbr}'
            self.flag_fields_name = False
        if self.flag_footer:
            if not self.banner_users:
                self._embed.remove_footer()
            else:
                text = 'バナー更新' if self.lang == Lang.JA else 'Updating banner'
                self._embed.set_footer(text=f'{text} for @' + ',@'.join(sorted(self.banner_users)))
            self.flag_footer = False
        return self._embed

    @property
    def message(self) -> BotMessage:
        self.update_firebase()
        message = BotMessage(embeds=[])
        if self.child is not None:
            message.embeds.append(self.child.embed)
        if self.child is None or self.child_is_valid():
            message.embeds.append(self.embed)
        if self.left_race_num == 0 and self.format == 6:
            message.embeds[-1].set_image(url='attachment://result.png')
            message.file = result_image.make(tags=self.tags, scores=self.get_scores())
        return message

    @property
    def format(self) -> int:
        if not hasattr(self, '_format'):
            self._format: int = int(self._embed.title.split('v', maxsplit=1)[0][-1])
        return self._format

    @property
    def tags(self) -> list[str]:
        if not hasattr(self, '_tags'):
            self._old_tags: list[str] = self._embed.title.split('\n', maxsplit=1)[-1].split(' - ')
            self._tags: list[str] = self._old_tags.copy()
        return self._tags

    @tags.setter
    def tags(self, tags: list[str]) -> None:
        self._tags = tags
        self.flag_title = True
        if self.child is not None:
            self.child.tags = tags

    @property
    def sum_scores(self) -> list[int]:
        if not hasattr(self, '_sum_scores'):
            text = self._embed.description.replace('`', '').split('  @', maxsplit=1)[0]
            self._old_sum_scores: list[int] = self.text_to_scores(text=text)
            self._sum_scores: list[int] = self._old_sum_scores.copy()
        return self._sum_scores

    @sum_scores.setter
    def sum_scores(self, sum_scores: list[int]) -> None:
        self._sum_scores = sum_scores
        self.flag_description = True

    @property
    def left_race_num(self) -> int:
        if not hasattr(self, '_left_race_num'):
            text = self._embed.description.replace('`', '').split('  @', maxsplit=1)[-1]
            self._left_race_num: int = int(text)
        return self._left_race_num

    @left_race_num.setter
    def left_race_num(self, left_race_num: int) -> None:
        if left_race_num < 0:
            raise LeftRaceNumMinusError(self.lang)
        self._left_race_num = left_race_num
        self.flag_description = True

    @property
    def race_num(self) -> int:
        if not hasattr(self, '_race_num'):
            self._race_num: int = 0
            for field in reversed(self.embed.fields):
                text = field.name.split(maxsplit=1)[0]
                if text.isdecimal():
                    self._race_num = int(text)
                    break
        return self._race_num

    @race_num.setter
    def race_num(self, race_num: int) -> None:
        self._race_num = race_num

    @property
    def min_race_num(self) -> int:
        if not hasattr(self, '_min_race_num'):
            self._min_race_num: int = 0
            for field in self.embed.fields:
                text = field.name.split(maxsplit=1)[0]
                if text.isdecimal():
                    self._min_race_num = int(text)
                    break
        return self._min_race_num

    @min_race_num.setter
    def min_race_num(self, min_race_num: int) -> None:
        self._min_race_num = min_race_num

    @property
    def total_race_num(self) -> int:
        return self.race_num + self.left_race_num

    @total_race_num.setter
    def total_race_num(self, total_race_num: int) -> None:
        self.left_race_num = total_race_num - self.race_num

    @property
    def banner_users(self) -> set[str]:
        if not hasattr(self, '_banner_users'):
            if not self._embed.footer.text:
                self._old_banner_users: set[str] = set()
            else:
                self._old_banner_users: set[str] = set(self._embed.footer.text.split(' for @', maxsplit=1)[-1].split(',@'))
            self._banner_users: set[str] = self._old_banner_users.copy()
        return self._banner_users

    @banner_users.setter
    def banner_users(self, banner_users: set[str]) -> None:
        self._banner_users = banner_users
        self.flag_footer = True

    def get_old_lang(self) -> Lang:
        if self._embed.title.startswith('即時'):
            return Lang.JA
        return Lang.EN

    @property
    def lang(self) -> Lang:
        if not hasattr(self, '_lang'):
            if self._embed.title.startswith('即時'):
                self._lang: Lang = Lang.JA
            else:
                self._lang: Lang = Lang.EN
        return self._lang

    @lang.setter
    def lang(self, lang: Lang) -> None:
        self._lang = lang
        self.flag_title = True
        self.flag_fields_name = True
        self.flag_footer = True
        if self.child is not None:
            self.child.lang = lang

    def get_scores(self) -> list[list[int]]:
        scores = [self.sum_scores]
        for field in reversed(self.embed.fields):
            text = field.value.split('`', maxsplit=3)[1]
            scores.append([score-incleased_score for score, incleased_score in zip(scores[-1], self.text_to_scores(text))])
        scores.reverse()
        return scores

    def edit(self, race_num: Optional[int], track: Optional[Track], ranks_text: Optional[str]) -> None:
        race_num = race_num or self.race_num
        if race_num == 0 or race_num < self.min_race_num or race_num > self.race_num:
            if race_num == self.race_num + 1 and self.child is not None and not ranks_text:
                self.child.track = track
                return
            raise NotValidRaceNumError(self.lang)
        if ranks_text is not None:
            race = Race(format=self.format, ranks=[])
            race.add_ranks_from_text(text=ranks_text)
            if not race.is_valid():
                raise NotValidRanksError(self.lang)
        race_num_text = str(race_num)
        for i in range(len(self.embed._fields)):
            if self.embed.fields[i].name.split(maxsplit=1)[0] == race_num_text:
                name = self.embed.fields[i].name
                value = self.embed.fields[i].value
                if ranks_text is not None:
                    old_scores = self.text_to_scores(text=self.embed.fields[i].value.split('` | `', maxsplit=1)[0][1:])
                    new_scores = race.scores
                    for j in range(12 // self.format):
                        self.sum_scores[j] += new_scores[i] - old_scores[i]
                    value = f'`{self.scores_to_text(scores=new_scores, format=self.format)}` | `{",".join(map(str, race.ranks[0].data))}`'
                elif track is None:
                    name = race_num_text
                if track is not None:
                    if self.lang == Lang.JA:
                        name = f'{race_num_text}  - {TrackEmoji(track.id)} {track.abbr_ja}'
                    else:
                        name = f'{race_num_text}  - {TrackEmoji(track.id)} {track.abbr}'
                self.embed._fields[i] = EmbedField(
                    name=name,
                    value=value,
                    inline=False
                )
                return

    def back(self) -> None:
        if self.child is not None:
            self.child.back()
            if not self.child.ranks:
                self.child = None
            return
        scores = None
        for i in reversed(range(len(self._embed.fields))):
            text = self._embed.fields[i].name.split(maxsplit=1)[0]
            if text.isdecimal():
                field = self._embed._fields.pop(i)
                scores = self.text_to_scores(text=field.value.split('` | `', maxsplit=1)[0][1:])
                self.left_race_num += 1
            elif text in {'Repick', 'Penalty'}:
                field = self._embed._fields.pop(i)
                scores = self.text_to_scores(text=field.value[1:-1])
            if scores is not None:
                for i in range(12 // self.format):
                    self.sum_scores[i] -= scores[i]
                return
        raise NoBackableContentError(self.lang)

    def add_field(self, name: str, value: str, inline: bool = False) -> None:
        if len(self._embed.fields) >= 25:
            field: EmbedField = self._embed._fields.pop(0)
            if field.name.split(maxsplit=1)[0].isdecimal():
                self.min_race_num += 1
        self._embed.add_field(name=name, value=value, inline=inline)

    def get_tag_index(self, tag: Optional[str]) -> int:
        if not tag:
            return 0
        if tag not in self.tags:
            raise TagNotFoundError(self.lang)
        return self.tags.index(tag)

    def add_repick(self, tag: Optional[str]) -> Optional[BotMessage]:
        tag_index = self.get_tag_index(tag=tag)
        scores = [0] * (12 // self.format)
        scores[tag_index] = -15
        self.add_field(name='Repick', value=f'`{self.scores_to_text(scores=scores, simple=True)}`')
        self.sum_scores[tag_index] -= 15

    def add_penalty(self, score: int, tag: Optional[str]) -> bool:
        tag_index = self.get_tag_index(tag=tag)
        scores = [0] * (12 // self.format)
        scores[tag_index] = score
        self.add_field(name='Penalty', value=f'`{self.scores_to_text(scores=scores, simple=True)}`')
        self.sum_scores[tag_index] += score

    def add_race(self, race: Race) -> None:
        self.race_num += 1
        self.left_race_num -= 1
        if race.track is None:
            name = str(self.race_num)
        else:
            if self.lang == Lang.JA:
                name = f'{self.race_num}  - {TrackEmoji(race.track.id)} {race.track.abbr_ja}'
            else:
                name = f'{self.race_num}  - {TrackEmoji(race.track.id)} {race.track.abbr}'
        scores = race.scores
        self.add_field(name=name, value=f'`{self.scores_to_text(scores=scores, format=self.format)}` | `{",".join(map(str, race.ranks[0].data))}`')
        for i in range(12 // self.format):
            self.sum_scores[i] += scores[i]

    def add_text(self, text: str, track: Optional[Track] = None) -> None:
        if self.format == 6:
            race = Race(format=self.format, ranks=[], track=track)
            race.add_ranks_from_text(text=text)
            if not race.is_valid():
                raise NotValidRanksError(self.lang)
            self.add_race(race=race)
            return
        if self.child is None:
            self.child = SokujiChild.start(
                race_num = self.race_num+1,
                tags = self.tags,
                lang = self.lang,
                track = track
            )
        self.child.add_text(text=text, format=self.format)
        if self.child_is_valid():
            self.add_child()

    def add_child(self) -> None:
        self.race_num += 1
        self.left_race_num -= 1
        name = self.child.embed.title
        scores = list(map(lambda r: r.score, self.child.ranks))
        self.add_field(name=name, value=f'`{self.scores_to_text(scores=scores, format=self.format)}` | `{",".join(map(str, self.child.ranks[0].data))}`')
        for i in range(12 // self.format):
            self.sum_scores[i] += scores[i]

    def child_is_valid(self) -> bool:
        if self.child is None:
            return False
        return len(self.child.ranks) == 12 // self.format

    def end(self) -> None:
        self._embed.set_author(name='Archive')

    def resume(self) -> None:
        self._embed.remove_author()

    def update_firebase(self) -> None:
        if not self.banner_users:
            return
        data = {}
        if self.format == 6:
            dif = self.sum_scores[0] - self.sum_scores[1]
            win = int(dif > self.left_race_num*40)
            d = {'teams': self.tags, 'scores': self.sum_scores, 'left': self.left_race_num, 'dif': '{:+}'.format(dif), 'win': win}
            for user in self.banner_users:
                data[user] = d
            update(data)
            return
        teamscores = sorted(dict(zip(self.tags, self.sum_scores)), key=lambda x:x[1], reverse=True)
        d = {'teams': list(map(lambda i: i[0], teamscores)), 'scores': list(map(lambda i: i[1], teamscores)), 'left': self.left_race_num}
        for user in self.banner_users:
            data[user] = d
        update(data)

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
        return list(map(lambda x: int(x.split('(', maxsplit=1)[0]), text.split(' : ')))
