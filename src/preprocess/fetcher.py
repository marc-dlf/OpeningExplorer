"""Downloader class that fetches PGN files from Chess.com."""

from pathlib import Path
from typing import Optional

import pandas as pd
import requests

from src.config import ADDRESS_ROOT, DATA_FOLDER
from src.explorer.pgn import PGN
from src.preprocess.regextractor import RegExtractor


class Fetcher:
    """
    Fetcher class responsible to download all pgns over a given time period for a player.

    Those PGNs are then aggregated into a csv with the following shape:
    color,result,link,game,month,opening
    black,win,https://link/to/game,d4 d5 Bf4 c5,Sicilian Defense
    ...

    Attributes
    ----------
    username (str) : Username of the player.
    """

    def __init__(self, username: str):
        """
        Construct the fetcher with the username.

        Parameters
        ----------
            username : str
                Username of the player in Chess.com.
        """
        self.username = username

    def download_month(self, year_month: str) -> Optional[str]:
        """
        Download the raw file containing all player PGNs for a given month.

        Note: this is the only way to request games via the Chess.com public API for now.

            Parameters:
                year_month (str) : Year and month for which we request PGNs, it is in
                    the format YYYY-MM (eg: 2023-01).

            Returns:
                pgn (str) : Raw PGN multi-line string for the month with multiple PGNs
                    if history exists, else None.
        """
        year_str, month_str = year_month.split("-")
        address = f"{ADDRESS_ROOT}/{self.username}/games/{year_str}/{month_str}/pgn"
        r = requests.get(address)
        # API didn't return anything
        if r.status_code != 200:
            r.raise_for_status()
        # API returned a file of PGN
        pgn = r.text
        if len(pgn) == 0:
            return None
        else:
            return pgn

    def download_history(self, start, end):
        """
        Download all the history for a player over a time period and saves it in a csv.

        The csv is save in the data folder with filename = {self.username}.csv.
        The format of the csv is the following:
        color,result,link,game,month,opening
        black,win,https://link/to/game,d4 d5 Bf4 c5,Sicilian Defense

            Parameters:
                start (str) : Start month in format YYYY-MM (eg: 2023-01).
                end (str) : End month in format YYYY-MM (eg: 2023-01).
        """
        month_list = pd.date_range(start, end, freq="MS").strftime("%Y-%m").tolist()
        pgn_df = pd.DataFrame(
            columns=["color", "result", "link", "game", "month", "opening"]
        )
        for y_m in month_list:
            pgns = self.download_month(y_m)
            if pgns is not None:
                # Spliting multi pgn file in individual PGN blocks.
                for pgn_txt in RegExtractor.split(pgns):
                    # TODO: better error handling here to fix extractor.
                    try:
                        pgn = PGN.extract_from_txt(pgn_txt, self.username)
                        # Adding a row to the csv.
                        pgn_df = pd.concat(
                            [pgn_df, pd.DataFrame(pgn.__dict__, index=[0])]
                        )
                    except:
                        pass
        pgn_df.to_csv(Path(DATA_FOLDER) / f"{self.username}.csv", index=False)
