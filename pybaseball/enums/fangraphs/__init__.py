from typing import Union

from .batting_stats import FanGraphsBattingStat
from .fielding_stats import FanGraphsFieldingStat
from .league import FanGraphsLeague
from .month import FanGraphsMonth
from .pitching_stats import FanGraphsPitchingStat
from .positions import FanGraphsPositions
from .stat_types import FanGraphsStatTypes
from.fangraphs_stats_base import type_list_to_str

FanGraphsStat = Union[FanGraphsBattingStat, FanGraphsFieldingStat, FanGraphsPitchingStat]
