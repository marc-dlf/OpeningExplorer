import os
from src.constants import DATA_FOLDER
import pandas as pd
from pathlib import Path
from src.trainer.pgn import PGN
from src.data_import.fetcher import Fetcher
from src.data_import.extractor import Extractor


class Player:
    def __init__(self, username):
        self.username = username
        self.pgn_list = []

    def load_player_history(self, start_month=None, end_month=None):
        if f"{self.username}.csv" in os.listdir(DATA_FOLDER):
            pgn_df = pd.read_csv(
                Path(DATA_FOLDER) / f"{self.username}.csv", index_col=None
            )
            for i in range(len(pgn_df)):
                pgn = PGN(*pgn_df.iloc[i].values)
                self.pgn_list.append(pgn)
        else:
            f = Fetcher(self.username)
            if start_month is None or end_month is None:
                raise ValueError(
                    "Both start month and end month should be specified to fetch data"
                )
            month_list = (
                pd.date_range(start_month, end_month, freq="MS")
                .strftime("%Y-%m")
                .tolist()
            )
            pgn_df = pd.DataFrame(
                columns=["username", "color", "result", "link", "game"]
            )
            for y_m in month_list:
                pgns = f.download_month(y_m)
                if pgns is not None:
                    for pgn_txt in Extractor.split(pgns):
                        pgn = PGN.extract_from_txt(self.username, pgn_txt)
                        pgn_df = pd.concat(
                            [pgn_df, pd.DataFrame(pgn.__dict__, index=[0])]
                        )
                        self.pgn_list.append(pgn)
            pgn_df.to_csv(Path(DATA_FOLDER) / f"{self.username}.csv", index=False)
