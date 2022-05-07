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
            self.set_thumbnail(rd.url)


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
        'f1c232',
        'https://i.imgur.com/6yAatOq.png'
    )
    SILVER = (
        'Silver',
        'cccccc',
        'https://i.imgur.com/xgFyiYa.png'
    )
    BRONZE = (
        'Bronze',
        'b45f06',
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
