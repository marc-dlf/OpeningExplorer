from src.fetcher import Fetcher


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


def test_fetcher_fetch_all_good_number_of_games(username):
    start_month = "2023-03"
    fetcher = Fetcher(username, start_month)
    fetcher.fetch_all()
    assert fetcher.processing_queue.qsize() == 15
