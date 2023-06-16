import requests

from src.constants import ADDRESS_ROOT


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
