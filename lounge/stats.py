from typing import Optional
from discord import Embed, File
from mk8dx.lounge_api import PlayerDetails
from .components import LoungeEmbed
from .mmr_changes import make as make_changes


def make_content(details: PlayerDetails, filter=None) -> tuple[Embed, Optional[File]]:
    if filter is None:
        embed = LoungeEmbed(
            rank=details.rank,
            title=f'S{details.season} Stats',
            description=f'[{details.name}](https://www.mk8dx-lounge.com/PlayerDetails/{details.player_id}?season={details.season})'
        )
        embed.add_field(
            name='Rank',
            value=details.overall_rank if details.overall_rank is not None else '-'
        )
        embed.add_field(
            name='MMR',
            value=details.mmr if details.mmr is not None else '-'
        )
        embed.add_field(
            name='Peak MMR',
            value=details.max_mmr if details.max_mmr is not None else '-'
        )
        embed.add_field(
            name='Win Rate',
            value=format(details.win_rate, '.1%') if details.win_rate is not None else '-'
        )
        embed.add_field(
            name='W-L (Last10)',
            value=details.win_loss_last_ten
        )
        embed.add_field(
            name='+/- (Last10)',
            value=details.gain_loss_last_ten if details.gain_loss_last_ten is not None else '-'
        )
        embed.add_field(
            name='Avg.',
            value=format(details.average_score, '.1f') if details.average_score is not None else '-'
        )
        embed.add_field(
            name='Avg. (Last10)',
            value=format(details.average_last_ten, '.1f') if details.average_last_ten is not None else '-'
        )
        embed.add_field(
            name='Partner Avg.',
            value=format(details.partner_average, '.1f') if details.partner_average is not None else '-'
        )
        embed.add_field(
            name='Events Played',
            value=details.events_played
        )
        if details.largest_gain is None:
            largest_gain_value = '-'
        elif details.largest_gain_table_id is None:
            largest_gain_value = format(details.largest_gain, '+')
        else:
            largest_gain_value = f'[{format(details.largest_gain, "+")}](https://www.mk8dx-lounge.com/TableDetails/{details.largest_gain_table_id})'
        embed.add_field(
            name='Largest Gain',
            value=largest_gain_value
        )
        if details.largest_loss is None:
            largest_loss_value = '-'
        elif details.largest_loss_table_id is None:
            largest_loss_value = details.largest_loss
        else:
            largest_loss_value = f'[{details.largest_loss}](https://www.mk8dx-lounge.com/TableDetails/{details.largest_loss_table_id})'
        embed.add_field(
            name='Largest Loss',
            value=largest_loss_value
        )
        file = make_changes(details=details)
        embed.set_image(url='attachment://stats.png')
        return embed, file
