from __future__ import annotations

from typing import Optional, Union, Any, TypeVar, TYPE_CHECKING
from discord.colour import Colour
from discord.embeds import _EmptyEmbed, EmptyEmbed
from discord import EmbedField, Message
from discord.abc import Messageable
import datetime
from mk8dx import Track

from components import ColoredEmbed

if TYPE_CHECKING:
    from discord.types.embed import EmbedType
    T = TypeVar("T")
    MaybeEmpty = Union[T, _EmptyEmbed]


class SokujiEmbed(ColoredEmbed):

    def __init__(
        self,
        *,
        color: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        title: MaybeEmpty[Any] = EmptyEmbed,
        type: EmbedType = "rich",
        url: MaybeEmpty[Any] = EmptyEmbed,
        description: MaybeEmpty[Any] = EmptyEmbed,
        timestamp: datetime.datetime = None,
        fields: Optional[list[EmbedField]] = None
    ) -> None:
        super().__init__(
            color=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
            fields=fields
        )
        # self.set_author(name='Sokuji')

class SokujiChildEmbed(ColoredEmbed):

    def __init__(
        self,
        *,
        color: Union[int, Colour, _EmptyEmbed] = EmptyEmbed,
        title: MaybeEmpty[Any] = EmptyEmbed,
        type: EmbedType = "rich",
        url: MaybeEmpty[Any] = EmptyEmbed,
        description: MaybeEmpty[Any] = EmptyEmbed,
        timestamp: datetime.datetime = None,
        fields: Optional[list[EmbedField]] = None
    ) -> None:
        super().__init__(
            color=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp,
            fields=fields
        )
        self.set_author(name='Sokuji Child')
