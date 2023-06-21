"""Player class responsible to load all PGN for a given username."""
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import pandas as pd

from src.config import DATA_FOLDER, MINIMAL_MONTH
from src.explorer.pgn import PGN
from src.preprocess.fetcher import Fetcher


class Player:
    """
    Player class responsible to load all PGN for a given username.

    ...

    Attributes
    ----------
    username (str) : Username of the player.
    pgn_list (List[PGN]) : A list containing all the PGNs for a given period.
    """

    def __init__(self, username: str):
        """
        Construct Player class for the given username.

        Parameters
        ----------
            username : str
                Username of the player in Chess.com.
            pgn_list (List[PGN]) :  A list containing all the PGNs for a given period.
        """
        self.username = username
        self.pgn_list = []

    def load_player_history(
        self, start_month: str, end_month: str, csv_path: Optional[str] = None
    ):
        """
        Load the player's PGNs from csv to pgn_list attribute.

        First checks if a csv file path is provided to load from it directly. If not,
        checks if the username has already a csv file in the data folder and loads PGNs
        from it. Else, fetches the player history with th Fetcher class then loads from
        the csv.

        Parameters
        ----------
            start_month : str
                Start month in format YYYY-MM (eg: 2023-01).
            end_month : str
                End month in format YYYY-MM (eg: 2023-01).
            csv_path : str
                Path to a csv file from which the player history is loaded in priority.
        """
        # If path is provided, load from it.
        if csv_path is not None:
            self.pgn_list = self.load_from_csv(csv_path, start_month, end_month)
        else:
            username_path = self.path()
            # If csv file found in data folder load from it.
            if username_path is not None:
                self.pgn_list = self.load_from_csv(
                    username_path, start_month, end_month
                )
            else:
                # Fetch data from chess.com then load from csv file.
                f = Fetcher(self.username)
                f.download_history(MINIMAL_MONTH, datetime.now().strftime("%Y-%m"))
                self.pgn_list = self.load_from_csv(self.path(), start_month, end_month)

    def path(self):
        """
        Get the default filename of the csv file in the data folder if exists.

        Returns:
            path (Optional[str]) : Default filename of the csv file in the data folder
                if exists.
        """
        if f"{self.username}.csv" in os.listdir(DATA_FOLDER):
            return Path(DATA_FOLDER) / f"{self.username}.csv"

    def load_from_csv(self, path: str, start_month: str, end_month: str):
        """
        Iterate over csv rows and convert each row into a PGN instance, then adds to pgn_list.

        Parameters
        ----------
            path : str
                Path to player csv history file.
            start_month : str
                Start month in format YYYY-MM (eg: 2023-01).
            end_month : str
                End month in format YYYY-MM (eg: 2023-01).
        """
        pgn_df = pd.read_csv(path)
        pgn_df = pgn_df[
            (pgn_df["month"] >= start_month) & (pgn_df["month"] <= end_month)
        ]
        pgn_list = []
        for i in range(len(pgn_df)):
            pgn = PGN(*pgn_df.iloc[i].values)
            pgn_list.append(pgn)
        return pgn_list
