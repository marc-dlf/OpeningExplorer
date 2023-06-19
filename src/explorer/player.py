import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import DATA_FOLDER, MINIMAL_MONTH
from src.explorer.pgn import PGN
from src.preprocess.fetcher import Fetcher


class Player:
    def __init__(self, username):
        self.username = username
        self.pgn_list = []

    def load_player_history(self, start_month, end_month, csv_path=None):
        if csv_path is not None:
            self.pgn_list = self.load_from_csv(csv_path, start_month, end_month)
        else:
            username_path = self.path()
            if username_path is not None:
                self.pgn_list = self.load_from_csv(
                    username_path, start_month, end_month
                )
            else:
                f = Fetcher(self.username)
                f.download_history(MINIMAL_MONTH, datetime.now().strftime("%Y-%m"))
                self.pgn_list = self.load_from_csv(self.path(), start_month, end_month)

    def path(self):
        if f"{self.username}.csv" in os.listdir(DATA_FOLDER):
            return Path(DATA_FOLDER) / f"{self.username}.csv"

    def load_from_csv(self, path, start_month, end_month):
        pgn_df = pd.read_csv(path)
        pgn_df = pgn_df[
            (pgn_df["month"] >= start_month) & (pgn_df["month"] <= end_month)
        ]
        pgn_list = []
        for i in range(len(pgn_df)):
            pgn = PGN(*pgn_df.iloc[i].values)
            pgn_list.append(pgn)
        return pgn_list
