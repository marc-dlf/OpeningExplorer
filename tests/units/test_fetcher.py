from src.data_import.fetcher import Fetcher


def test_split_good_number_of_games(dummy_pgn):
    pgns = Fetcher.split(dummy_pgn)
    assert len(pgns) == 3


def test_fetch_month_no_pgn(username):
    start_month = "2020-01"
    fetcher = Fetcher(username, start_month)
    assert fetcher.fetch_month("2017-01") == []


def test_fetch_month_good_number_of_games(username):
    start_month = "2020-01"
    fetcher = Fetcher(username, start_month)
    assert len(fetcher.fetch_month("2023-04")) == 8
