from __future__ import annotations

from typing import Optional, Union, Any, TypeVar
from enum import Enum
from mk8dx.lounge_api.rank import Rank
from discord.colour import Colour
from discord.embeds import Embed, _EmptyEmbed, EmptyEmbed
from discord.types.embed import EmbedType
import datetime


T = TypeVar("T")
MaybeEmptyEmbed = Union[T, _EmptyEmbed]

class LoungeEmbed(Embed):
    def __init__(
        self,
        *,
        rank: Rank,
        title: MaybeEmptyEmbed[Any] = EmptyEmbed,
        type: EmbedType = "rich",
        url: MaybeEmptyEmbed[Any] = EmptyEmbed,
        description: MaybeEmptyEmbed[Any] = EmptyEmbed,
        timestamp: Optional[datetime.datetime] = None,
        thumbnail: bool = True
    ):
        rd = RankDivision(rank)
        super().__init__(
            colour=rd.color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp
        )
        if thumbnail and rd.url is not None:
            self.set_thumbnail(url=rd.url)


class RankDivision(Enum):

    __slots__ = (
        'color',
        'url'
    )

    def __new__(cls: type[RankDivision], name: str, *_) -> RankDivision:
        obj = object.__new__(cls)
        obj._value_ = name
        return obj

    def __init__(
        self,
        _: str,
        hex_color: str,
        url: Optional[str] = None
    ):
        self.color: Colour = Colour(int(hex_color, 16))
        self.url: Optional[str] = url

    @classmethod
    def _missing_(cls, value: object) -> Any:
        if isinstance(value, Rank):
            return RankDivision(value.division.value)
        if isinstance(value, Rank.Division):
            return RankDivision(value.value)
        return super()._missing_(value)

    GRANDMASTER = (
        'Grandmaster',
        'a3022c',
        'https://i.imgur.com/EWXzu2U.png'
    )
    MASTER = (
        'Master',
        '9370db',
        'https://i.imgur.com/3yBab63.png'
    )
    DIAMOND = (
        'Diamond',
        'b9f2ff',
        'https://i.imgur.com/RDlvdvA.png'
    )
    RUBY = (
        'Ruby',
        'd51c5e',
        'https://i.imgur.com/WU2NlJQ.png'
    )
    SAPPHIRE = (
        'Sapphire',
        '286cd3',
        'https://i.imgur.com/bXEfUSV.png'
    )
    PLATINUM = (
        'Platinum',
        '3fabb8',
        'https://i.imgur.com/8v8IjHE.png'
    )
    GOLD = (
        'Gold',
        'f1c40f',
        'https://i.imgur.com/6yAatOq.png'
    )
    SILVER = (
        'Silver',
        '7d8396',
        'https://i.imgur.com/xgFyiYa.png'
    )
    BRONZE = (
        'Bronze',
        'e67e22',
        'https://i.imgur.com/DxFLvtO.png'
    )
    IRON = (
        'Iron',
        '817876',
        'https://i.imgur.com/AYRMVEu.png'
    )
    PLACEMENT = (
        'Placement',
        '000000'
    )
    UNKNOWN = (
        'Unknown',
        'ff0000'
    )


class Span:
 
    __slots__ = (
        'max',
        'min',
        'color'
    )

    def __init__(self, max: int, min: int, color: Colour) -> None:
        self.max: int = max
        self.min: int = min
        self.color: str = '#' + format(color.value, 'x')


class SeasonDivision(Enum):

    __slots__ = (
        'spans',
        'lines',
        'top_color'
    )

    def __new__(cls: type[SeasonDivision], season: int, *_) -> RankDivision:
        obj = object.__new__(cls)
        obj._value_ = season
        return obj

    def __init__(
        self,
        _: int,
        rank: list[int],
        level: list[int]
    ) -> None:
        divisions = list(RankDivision)
        self.spans: list[Span] = [Span(max=rank[i-1], min=rank[i], color=divisions[i].color) for i in range(len(rank)-1, 0, -1)]
        self.lines: list[int] = level
        self.top_color: str = '#' + format(divisions[0].color.value, 'x')

    S4 = (
        4,
        [14500, 13000, 11500, 11500, 10000, 8500, 7000, 5500, 4000, 0],
        [2000]
    )
    S5 = (
        5,
        [14000, 13000, 11000, 11000, 10000, 8000, 6000, 4000, 2000, 0],
        [12000, 9000, 7000, 5000, 3000, 1000]
    )
    S6 = (
        6,
        [15000, 14000, 12000, 12000, 10000, 8000, 6000, 4000, 2000, 0],
        [13000, 11000, 9000, 7000, 5000, 3000, 1000]
    )
    S7 = (
        7,
        [15000, 14000, 12000, 12000, 10000, 8000, 6000, 4000, 2000, 0],
        [13000, 11000, 9000, 7000, 5000, 3000, 1000]
    )
    S8 = (
        8,
        [17000, 16000, 14000, 12000, 10000, 8000, 6000, 4000, 2000, 0],
        [15000, 13000, 11000, 9000, 7000, 5000, 3000, 1000]
    )
