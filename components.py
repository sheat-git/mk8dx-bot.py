from typing import Union, Any, TypeVar, Optional
import os
from discord.colour import Colour
from discord.embeds import Embed, _EmptyEmbed, EmptyEmbed
from discord.types.embed import EmbedType
import datetime


T = TypeVar("T")
MaybeEmptyEmbed = Union[T, _EmptyEmbed]

COLOR = Colour(int(os.environ['COLOR'], 0))

class ColoredEmbed(Embed):

    def __init__(
        self,
        *,
        color: Union[int, Colour, _EmptyEmbed] = COLOR,
        title: MaybeEmptyEmbed[Any] = EmptyEmbed,
        type: EmbedType = "rich",
        url: MaybeEmptyEmbed[Any] = EmptyEmbed,
        description: MaybeEmptyEmbed[Any] = EmptyEmbed,
        timestamp: Optional[datetime.datetime] = None
    ):
        super().__init__(
            colour=color,
            title=title,
            type=type,
            url=url,
            description=description,
            timestamp=timestamp
        )
