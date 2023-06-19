from pathlib import Path

import pandas as pd
import requests

from src.config import ADDRESS_ROOT, DATA_FOLDER
from src.explorer.pgn import PGN
from src.preprocess.regextractor import RegExtractor


class Fetcher:
    def __init__(self, username):
        self.username = username

    def download_month(self, year_month: str):
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
        month_list = pd.date_range(start, end, freq="MS").strftime("%Y-%m").tolist()
        pgn_df = pd.DataFrame(
            columns=["color", "result", "link", "game", "month", "opening"]
        )
        for y_m in month_list:
            pgns = self.download_month(y_m)
            if pgns is not None:
                for pgn_txt in RegExtractor.split(pgns):
                    try:
                        pgn = PGN.extract_from_txt(pgn_txt, self.username)
                        pgn_df = pd.concat(
                            [pgn_df, pd.DataFrame(pgn.__dict__, index=[0])]
                        )
                    except:
                        pass
        pgn_df.to_csv(Path(DATA_FOLDER) / f"{self.username}.csv", index=False)
