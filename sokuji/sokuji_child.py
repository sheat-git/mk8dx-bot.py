from __future__ import annotations
from typing import Optional

from discord import Embed
from mk8dx import Track, Rank

from lang import Lang
from sokuji.components import SokujiChildEmbed
from track.emoji import TrackEmoji


class SokujiChild:

    def __init__(self, embed: Embed, lang: Lang) -> None:
        self._embed: Embed = embed
        self._lang: Lang = lang
        self._flag_title: bool = False
        self._flag_fields_name: bool = False
        self._flag_fields_value: bool = False

    @property
    def flag_title(self) -> bool:
        return self._flag_title

    @flag_title.setter
    def flag_title(self, flag: bool) -> None:
        self._flag_title = flag

    @property
    def flag_fields_name(self) -> bool:
        if self._flag_fields_name:
            return True
        return self.tags != self._old_tags

    @flag_fields_name.setter
    def flag_fields_name(self, flag: bool) -> None:
        self._flag_fields_name = flag

    @property
    def flag_fields_value(self) -> bool:
        if self._flag_fields_value:
            return True
        return self.ranks != self._old_ranks

    @flag_fields_value.setter
    def flag_fields_value(self, flag: bool) -> None:
        self._flag_fields_value = flag

    @staticmethod
    def start(race_num: int, tags: list[str], lang: Lang, track: Optional[Track]) -> SokujiChild:
        if track is None:
            title = str(race_num)
        elif lang == Lang.JA:
            title = f'{race_num}  - {TrackEmoji(track.id)} {track.abbr_ja}'
        else:
            title = f'{race_num}  - {TrackEmoji(track.id)} {track.abbr}'
        embed = SokujiChildEmbed(title=title)
        for tag in tags:
            embed.add_field(name=tag, value='score : `0`', inline=False)
        return SokujiChild(embed=embed, lang=lang)

    @property
    def embed(self) -> Embed:
        if self.flag_title:
            self._embed.title = self._embed.title.split(maxsplit=1)[0]
            if self.track is not None:
                abbr = self.track.abbr_ja if self.lang == Lang.JA else self.track.abbr
                self._embed.title += f'  - {TrackEmoji(self.track.id)} {abbr}'
            self.flag_title = False
        if self.flag_fields_name:
            for i, tag in enumerate(self.tags):
                self._embed._fields[i].name = tag
            self.flag_fields_name = False
        if self.flag_fields_value:
            for i in range(len(self._embed.fields)):
                if i < len(self.ranks):
                    self._embed._fields[i].value = self.rank_to_text(self.ranks[i])
                else:
                    self._embed._fields[i].value = 'score : `0`'
            self.flag_fields_value = False
        return self._embed

    @property
    def tags(self) -> list[str]:
        if not hasattr(self, '_tags'):
            self._old_tags: list[str] = list(map(lambda f: f.name, self._embed.fields))
            self._tags: list[str] = self._old_tags.copy()
        return self._tags

    @tags.setter
    def tags(self, tags: list[str]):
        self._tags = tags
        self.flag_fields_name = True

    @property
    def track(self) -> Optional[Track]:
        if not hasattr(self, '_track'):
            if '-' not in self._embed.title:
                self._track: Optional[Track] = None
            else:
                self._track: Optional[Track] = Track(self._embed.title.rsplit(maxsplit=1)[-1])
        return self._track

    @track.setter
    def track(self, track: Optional[Track]) -> None:
        self._track = track
        self.flag_title = True

    @property
    def lang(self) -> Lang:
        return self._lang

    @lang.setter
    def lang(self, lang: Lang) -> None:
        self._lang = lang
        self.flag_title = True

    @property
    def ranks(self) -> list[Rank]:
        if not hasattr(self, '_ranks'):
            ranks = []
            for field in self._embed.fields:
                if 'rank' not in field.value:
                    break
                ranks.append(self.text_to_rank(field.value))
            self._old_ranks: list[Rank] = ranks
            self._ranks: list[Rank] = self._old_ranks.copy()
        return self._ranks

    @ranks.setter
    def ranks(self, ranks: list[Rank]) -> None:
        self._ranks = ranks
        self.flag_fields_value = True

    def back(self) -> None:
        self.ranks.pop(-1)

    def add_text(self, text: str, format: int) -> None:
        self.ranks = Rank.get_ranks_from_text(text=text, format=format, ranks=self.ranks)

    @staticmethod
    def rank_to_text(rank: Rank) -> str:
        return f'score : `{rank.score}` | rank : `{",".join(map(str, rank.data))}`'

    @staticmethod
    def text_to_rank(text: str) -> Rank:
        return Rank(data=list(map(int, text.split('rank : `', maxsplit=1)[-1][:-1].split(','))))
