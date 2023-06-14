import requests
import re
import queue
from datetime import datetime

import pandas as pd

from src.constants import ADDRESS_ROOT


class Fetcher:
    def __init__(self, username, start_month, end_month=None):
        self.username = username
        self.start_month = start_month
        self.end_month = end_month
        self.processing_queue = queue.Queue()

    def fetch_all(self):
        end_month = self.end_month
        if end_month is None:
            end_month = datetime.strftime(datetime.now(), "%Y-%m")

        month_list = (
            pd.date_range(self.start_month, end_month, freq="MS")
            .strftime("%Y-%m")
            .tolist()
        )

        for y_m in month_list:
            pgns = self.fetch_month(y_m)
            self.push_into_queue(pgns)

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
            return []
        else:
            return Fetcher.split(pgn)

    def push_into_queue(self, pgns_list):
        if pgns_list:
            for pgn in pgns_list:
                self.processing_queue.put(pgn)

    @staticmethod
    def split(raw_pgn):
        regex = r'(?<=\[Event "Live Chess"\])[\s\S]*?(?=\[Event "Live Chess"\]|$)'
        matches = re.findall(regex, raw_pgn, re.DOTALL)
        return matches
