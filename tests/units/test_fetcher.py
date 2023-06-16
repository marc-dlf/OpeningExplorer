from src.data_import.fetcher import Fetcher
from src.data_import.extractor import Extractor


def test_fetch_month_no_pgn(username):
    fetcher = Fetcher(username)
    assert fetcher.download_month("2017-01") == None


def test_fetch_month_good_number_of_games(username):
    fetcher = Fetcher(username)
    pgn = fetcher.download_month("2023-04")
    assert len(Extractor.split(pgn)) == 8
