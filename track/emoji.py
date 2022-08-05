from __future__ import annotations

from typing import Optional
from enum import Enum
from discord import Emoji
from discord.ext.commands import Bot


class TrackEmoji(Enum):

    __slots__ = (
        'emoji_id',
        'emoji'
    )

    def __new__(cls: type[TrackEmoji], track_id: int, *_) -> TrackEmoji:
        obj = object.__new__(cls)
        obj._value_ = track_id
        return obj

    def __init__(self, _: int, emoji_id: int) -> None:
        self.emoji_id: int = emoji_id
        self.emoji: Optional[Emoji] = None

    @classmethod
    def setup(cls, bot: Bot):
        for emoji in cls:
            emoji.emoji = bot.get_emoji(emoji.emoji_id)

    @property
    def track_id(self) -> int:
        return self.value
    
    def is_usable(self):
        return self.emoji is not None and self.emoji.is_usable()

    def __str__(self) -> str:
        if not self.is_usable():
            return ''
        return str(self.emoji)

    MKS = (
        0,
        968803509334073344
    )
    WP = (
        1,
        968803586110791690
    )
    SSC = (
        2,
        968803703857508353
    )
    TR = (
        3,
        968803703899443220
    )
    MC = (
        4,
        968803703870062613
    )
    TH = (
        5,
        968803704146911283
    )
    TM = (
        6,
        968803703995904020
    )
    SGF = (
        7,
        968803703962337330
    )
    SA = (
        8,
        968803703886848020
    )
    DS = (
        9,
        968803703895244840
    )
    ED = (
        10,
        968803704012701757
    )
    MW = (
        11,
        968803703903637544
    )
    CC = (
        12,
        968803703463239691
    )
    BDD = (
        13,
        968803703572287511
    )
    BC = (
        14,
        968803704004313138
    )
    RR = (
        15,
        968803704004292608
    )
    DYC = (
        16,
        968803704176279622
    )
    DEA = (
        17,
        968803703895232552
    )
    DDD = (
        18,
        968803703966560316
    )
    DMC = (
        19,
        968803703937171487
    )
    DBP = (
        20,
        968803704063012884
    )
    DCL = (
        21,
        968803703991717918
    )
    DWW = (
        22,
        968803703983321118
    )
    DAC = (
        23,
        968803704004309002
    )
    RMMM = (
        24,
        968803703983337492
    )
    RMC = (
        25,
        968803704222396446
    )
    RCCB = (
        26,
        968803704151080980
    )
    RTT = (
        27,
        968803703966543912
    )
    RDDD = (
        28,
        968803703836540970
    )
    RDP3 = (
        29,
        968803704012677140
    )
    RRRY = (
        30,
        968803704042033202
    )
    RDKJ = (
        31,
        968803704130117672
    )
    RWS = (
        32,
        968803704042045460
    )
    RSL = (
        33,
        968816714999541761
    )
    RMP = (
        34,
        968816714995368006
    )
    RYV = (
        35,
        968816714999554048
    )
    RTTC = (
        36,
        968816715142160434
    )
    RPPS = (
        37,
        968816715020517376
    )
    RGV = (
        38,
        968816715100217354
    )
    RRRD = (
        39,
        968816715473510421
    )
    DWGM = (
        40,
        968816715083415562
    )
    DRR = (
        41,
        968816714638831637
    )
    DIIO = (
        42,
        968816715142139924
    )
    DHC = (
        43,
        968816715192471572
    )
    DNBC = (
        44,
        968816715070857246
    )
    DRIR = (
        45,
        968816715163127890
    )
    DSBS = (
        46,
        968816715075039272
    )
    DBB = (
        47,
        968816715142160384
    )
    BPP = (
        48,
        968817382225236010
    )
    BTC = (
        49,
        968817382254587975
    )
    BCMO = (
        50,
        968817382678204456
    )
    BCMA = (
        51,
        968817382464319529
    )
    BTB = (
        52,
        968817382543986720
    )
    BSR = (
        53,
        968817382623674378
    )
    BSG = (
        54,
        968817382623678464
    )
    BNH = (
        55,
        968817382749528094
    )
    BNYM = (
        56,
        1005158625221812364
    )
    BMC3 = (
        57,
        1005159802890092584
    )
    BKD = (
        58,
        1005160676790124584
    )
    BWP = (
        59,
        1005173373283868702
    )
    BSS = (
        60,
        1005173790440964166
    )
    BSL = (
        61,
        1005174057362280448
    )
    BMG = (
        62,
        1005174359155015700
    )
    BSHS = (
        63,
        1005174786781094001
    )
