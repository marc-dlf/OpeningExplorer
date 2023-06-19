from src.preprocess.fetcher import Fetcher
from src.preprocess.regextractor import RegExtractor


def test_fetch_month_no_pgn(username):
    fetcher = Fetcher(username)
    assert fetcher.download_month("2017-01") == None


def test_fetch_month_good_number_of_games(username):
    fetcher = Fetcher(username)
    pgn = fetcher.download_month("2023-04")
    assert len(RegExtractor.split(pgn)) == 8
