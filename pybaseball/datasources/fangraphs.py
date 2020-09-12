from enum import Enum, unique
from typing import Callable, List, Optional, Union
from abc import ABC

import lxml
import pandas as pd
import requests

from .column_mapper import GenericColumnMapper, BattingStatsColumnMapper
from pybaseball.datahelpers import postprocessing
from pybaseball.datasources.html_table import HTMLTable
from pybaseball.enums.fangraphs import (
    FanGraphsBattingStat,
    FanGraphsFieldingStat,
    FanGraphsLeague,
    FanGraphsMonth,
    FanGraphsPitchingStat,
    FanGraphsPositions,
    FanGraphsStatTypes,
)


_FG_LEADERS_URL = "/leaders.aspx"

MIN_AGE = 0
MAX_AGE = 100


class FangraphsDataTable(ABC):
    _ROOT_URL = "https://www.fangraphs.com"
    _TABLE_CLASS = "rgMasterTable"
    _HEADINGS_XPATH = "({TABLE_XPATH}/thead//th[contains(@class, 'rgHeader')])[position()>1]/descendant-or-self::*/text()"
    _DATA_ROWS_XPATH = "({TABLE_XPATH}/tbody//tr)"
    _DATA_CELLS_XPATH = "td[position()>1]/descendant-or-self::*/text()"
    _QUERY_ENDPOINT = _FG_LEADERS_URL
    _STATS = None
    _TYPES = None
    _COLUMN_NAME_MAPPER = GenericColumnMapper().map_list
    _KNOWN_PERCENTAGES = []

    def __init__(self):
        self.html_accessor = HTMLTable(
            root_url=self._ROOT_URL,
            headings_xpath=self._HEADINGS_XPATH,
            data_rows_xpath=self._DATA_ROWS_XPATH,
            data_cell_xpath=self._DATA_CELLS_XPATH,
            table_class=self._TABLE_CLASS,
        )

    def _postprocess(self, df):
        return df

    def _validate(self, df):
        return df

    def __call__(
        self,
        start_season: int,
        end_season: int = None,
        league: FanGraphsLeague = FanGraphsLeague.ALL,
        qual: Optional[int] = None,
        split_seasons: bool = True,
        month: FanGraphsMonth = FanGraphsMonth.ALL,
        on_active_roster: bool = False,
        minimum_age: int = MIN_AGE,
        maximum_age: int = MAX_AGE,
        team: str = "0,ts",
        _filter: str = "",
        players: str = "0",
        position: FanGraphsPositions = FanGraphsPositions.ALL,
        max_results: int = 1000000,
    ) -> pd.DataFrame:

        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. "
                + "Try specifying start_season or start_season and end_season."
            )
        if end_season is None:
            end_season = start_season

        url_parameters = {
            "pos": position.value,
            "stats": self._STATS.value,
            "lg": league.value,
            "qual": qual if qual is not None else "y",
            "type": self._TYPES,
            "season": end_season,
            "month": month.value,
            "season1": start_season,
            "ind": "1" if split_seasons else "0",
            "team": team,
            "rost": "1" if on_active_roster else "0",
            "age": f"{minimum_age},{maximum_age}",
            "filter": _filter,
            "players": players,
            "page": f"1_{max_results}",
        }

        return self._validate(
            self._postprocess(
                self.html_accessor.get_tabular_data_from_options(
                    self._QUERY_ENDPOINT,
                    url_parameters,
                    self._COLUMN_NAME_MAPPER,
                    self._KNOWN_PERCENTAGES,
                )
            )
        )


class FangraphsBattingStats(FangraphsDataTable):
    _STATS = FanGraphsStatTypes.BATTING
    _TYPES = FanGraphsBattingStat.ALL()
    _COLUMN_NAME_MAPPER = BattingStatsColumnMapper().map_list
    _KNOWN_PERCENTAGES = ["GB/FB"]

    def _postprocess(self, df):
        return df.sort_values(["WAR", "OPS"], ascending=False)


class FangraphsPitchingStats(FangraphsDataTable):
    _STATS = FanGraphsStatTypes.PITCHING
    _TYPES = FanGraphsPitchingStat.ALL()

    def _postprocess(self, df):
        cols = df.columns.tolist()
        cols.insert(7, cols.pop(cols.index('WAR')))
        return df.reindex(columns=cols).sort_values(["WAR", "W"], ascending=False)



class FangraphsTeamBattingStats(FangraphsDataTable):
    _STATS = FanGraphsStatTypes.BATTING
    _TYPES = FanGraphsBattingStat.ALL()
    _COLUMN_NAME_MAPPER = BattingStatsColumnMapper().map_list


class FangraphsTeamFieldingStats(FangraphsDataTable):
    _STATS = FanGraphsStatTypes.FIELDING
    _TYPES = FanGraphsFieldingStat.ALL()


class FangraphsTeamPitchingStats(FangraphsDataTable):
    _STATS = FanGraphsStatTypes.PITCHING
    _TYPES = FanGraphsPitchingStat.ALL()
