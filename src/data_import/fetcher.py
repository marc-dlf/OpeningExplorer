import requests
import re
from datetime import datetime
import os
from pathlib import Path

import pandas as pd
import queue

from src.constants import ADDRESS_ROOT, DATA_FOLDER


class Fetcher:
    def __init__(self, username):
        self.username = username

    def download_all(self, start_month, end_month=None):
        output_folder = Path(DATA_FOLDER) / self.username
        if end_month is None:
            end_month = datetime.strftime(datetime.now(), "%Y-%m")
        month_list = (
            pd.date_range(start_month, end_month, freq="MS").strftime("%Y-%m").tolist()
        )
        os.makedirs(output_folder)
        for y_m in month_list:
            pgn = self.fetch_month(y_m)
            if pgn is not None:
                print(output_folder / f"{y_m}.txt")
                with open(output_folder / f"{y_m}.txt", "w") as out_file:
                    print()
                    out_file.write(pgn)

    def fetch_month(self, year_month: str):
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

    def push_into_queue(self, pgns_list):
        q = queue.Queue()
        if pgns_list:
            for pgn in pgns_list:
                q.put(pgn)

        return q
