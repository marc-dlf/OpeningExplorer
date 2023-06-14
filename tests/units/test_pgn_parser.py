from src.pgn_parser import PGNParser
from src.fetcher import Fetcher


def test_parse_color(dummy_pgn, username):
    pgns = Fetcher.split(dummy_pgn)

    parser1 = PGNParser(pgns[0], username, init=False)
    assert parser1.parse_color() == "White"

    parser2 = PGNParser(pgns[1], username, init=False)
    assert parser2.parse_color() == "Black"


def test_parse_result(dummy_pgn, username):
    pgns = Fetcher.split(dummy_pgn)

    parser1 = PGNParser(pgns[0], username, init=False)
    assert parser1.parse_result() == "Win"

    parser2 = PGNParser(pgns[1], username, init=False)
    assert parser2.parse_result() == "Draw"

    parser3 = PGNParser(pgns[2], username, init=False)
    assert parser3.parse_result() == "Lose"


def test_parse_result(dummy_pgn, username):
    pgns = Fetcher.split(dummy_pgn)

    parser1 = PGNParser(pgns[0], username, init=False)
    expected_game_1 = "e4 e5"
    assert parser1.parse_game().unroll_game() == expected_game_1

    parser2 = PGNParser(pgns[2], username, init=False)
    expected_game_2 = (
        "e4 c6 d4 d5 e5 Bf5 Bd3 Bxd3 Qxd3 e6 Nf3 Nd7 Ne7 Nc3 a6 Ne2 c5 c3 Nc6 Bg5"
    )
    assert parser2.parse_game().unroll_game() == expected_game_2
