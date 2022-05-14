from typing import Optional
from discord import Embed, File
from mk8dx.lounge_api import PlayerDetails
from .components import LoungeEmbed
from .stats_unfiltered_image import make as make_unfiltered
from .stats_filtered_image import make as make_filtered


Reason = PlayerDetails.MmrChange.Reason

def make_content(details: PlayerDetails, filter_func=None, title='') -> Optional[tuple[Embed, Optional[File]]]:
    if filter_func is None:
        return _make_content_unfiltered(details=details)
    return _make_content_filtered(details=details, filter_func=filter_func, title=title)


def _make_content_unfiltered(details: PlayerDetails) -> tuple[Embed, Optional[File]]:

    # organize data
    ids = []
    new_mmrs = []
    top_score = -1
    top_score_table_id = None
    for change in reversed(details.mmr_changes):
        if change.reason == Reason.PLACEMENT:
            ids.append(change.change_id)
            new_mmrs.append([change.new_mmr])
        elif change.reason == Reason.TABLE:
            ids.append(change.change_id)
            new_mmrs.append([change.new_mmr])
            if change.score is not None and top_score < change.score:
                top_score = change.score
                top_score_table_id = change.change_id
        else:
            if change.reason == Reason.TABLE_DELETE:
                try:
                    i = ids.index(change.change_id)
                    if i > 0:
                        new_mmr = new_mmrs.pop(i)
                        new_mmrs[i-1].extend(new_mmr)
                except ValueError:
                    pass
            if len(new_mmrs) > 0:
                new_mmrs[-1].append(change.new_mmr)

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
        value=format(details.gain_loss_last_ten, '+') if details.gain_loss_last_ten is not None else '-'
    )
    embed.add_field(
        name='Avg.',
        value=format(details.average_score, '.1f') if details.average_score is not None else '-'
    )
    if top_score < 0:
        top_score_value = '-'
    elif top_score_table_id is None:
        top_score_value = top_score
    else:
        top_score_value = f'[{top_score}](https://www.mk8dx-lounge.com/TableDetails/{top_score_table_id})'
    embed.add_field(
        name='Top Score',
        value=top_score_value
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
    file = make_unfiltered(mmrs=new_mmrs, season=details.season)
    embed.set_image(url='attachment://stats.png')
    return embed, file


def _make_content_filtered(details: PlayerDetails, filter_func, title: str) -> Optional[tuple[Embed, Optional[File]]]:

    # organize data
    ids = []
    mmr_deltas = []
    top_score = -1
    top_score_table_id = None
    wins = 0
    total_delta = 0
    sum_scores = 0
    sum_partner_scores = 0
    sum_partners = 0
    events_played = 0
    largest_gain = 0
    largest_gain_table_id = None
    largest_loss = 1
    largest_loss_table_id = None
    for change in reversed(details.mmr_changes):
        if not filter_func(change):
            continue
        if change.reason == Reason.TABLE:
            ids.append(change.change_id)
            mmr_deltas.append([change.mmr_delta])
            if change.score is not None and top_score < change.score:
                top_score = change.score
                top_score_table_id = change.change_id
            if change.mmr_delta > 0:
                wins += 1
            total_delta += change.mmr_delta
            sum_scores += change.score
            if change.partner_scores is not None:
                sum_partner_scores += sum(change.partner_scores)
                sum_partners += len(change.partner_scores)
            events_played += 1
            if largest_gain < change.mmr_delta:
                largest_gain = change.mmr_delta
                largest_gain_table_id = change.change_id
            elif largest_loss > change.mmr_delta:
                largest_loss = change.mmr_delta
                largest_loss_table_id = change.change_id
        else:
            if change.reason == Reason.TABLE_DELETE:
                deleted_change = next(filter(lambda c: c.change_id == change.change_id and c.reason == Reason.TABLE, details.mmr_changes), None)
                if deleted_change is not None:
                    if deleted_change.mmr_delta > 0:
                        wins -= 1
                    sum_scores -= deleted_change.score
                    if deleted_change.partner_scores is not None:
                        sum_partner_scores -= sum(deleted_change.partner_scores)
                        sum_partners -= len(deleted_change.partner_scores)
                    events_played -= 1
                try:
                    i = ids.index(change.change_id)
                    if i > 0:
                        mmr_delta = mmr_deltas.pop(i)
                        mmr_deltas[i-1].extend(mmr_delta)
                except ValueError:
                    pass
            total_delta += change.mmr_delta
            if len(mmr_deltas) > 0 and change.mmr_delta is not None:
                mmr_deltas[-1].append(change.mmr_delta)

    if events_played < 1:
        return None

    embed = LoungeEmbed(
            rank=details.rank,
            title=f'S{details.season} {title} Stats',
            description=f'[{details.name}](https://www.mk8dx-lounge.com/PlayerDetails/{details.player_id}?season={details.season})'
        )
    embed.add_field(
        name='Win Rate',
        value=format(wins/events_played, '.1%') if events_played > 0 else '-'
    )
    embed.add_field(
        name='W-L',
        value=f'{wins} - {events_played - wins}'
    )
    embed.add_field(
        name='+/-',
        value=format(total_delta, '+')
    )
    embed.add_field(
        name='Avg.',
        value=format(sum_scores/events_played, '.1f') if events_played > 0 else '-'
    )
    if top_score < 0:
        top_score_value = '-'
    elif top_score_table_id is None:
        top_score_value = top_score
    else:
        top_score_value = f'[{top_score}](https://www.mk8dx-lounge.com/TableDetails/{top_score_table_id})'
    embed.add_field(
        name='Top Score',
        value=top_score_value
    )
    embed.add_field(
        name='Partner Avg.',
        value=format(sum_partner_scores/sum_partners, '.1f') if sum_partners > 0 else '-'
    )
    embed.add_field(
        name='Events Played',
        value=events_played
    )
    if largest_gain == 0:
        largest_gain_value = '-'
    elif largest_gain_table_id is None:
        largest_gain_value = format(largest_gain, '+')
    else:
        largest_gain_value = f'[{format(largest_gain, "+")}](https://www.mk8dx-lounge.com/TableDetails/{largest_gain_table_id})'
    embed.add_field(
        name='Largest Gain',
        value=largest_gain_value
    )
    if largest_loss == 1:
        largest_loss_value = '-'
    elif largest_loss_table_id is None:
        largest_loss_value = largest_loss
    else:
        largest_loss_value = f'[{largest_loss}](https://www.mk8dx-lounge.com/TableDetails/{largest_loss_table_id})'
    embed.add_field(
        name='Largest Loss',
        value=largest_loss_value
    )
    file = make_filtered(deltas=mmr_deltas)
    embed.set_image(url='attachment://stats.png')
    return embed, file
