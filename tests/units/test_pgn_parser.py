from src.data_import.pgn import PGN
from src.data_import.fetcher import Fetcher


def test_parse_color(dummy_pgn, username):
    pgns = Fetcher.split(dummy_pgn)

    pgn1 = PGN(pgns[0], username, init=False)
    assert pgn1.parse_color() == "white"

    pgn2 = PGN(pgns[1], username, init=False)
    assert pgn2.parse_color() == "black"


def test_parse_result(dummy_pgn, username):
    pgns = Fetcher.split(dummy_pgn)

    pgn1 = PGN(pgns[0], username, init=False)
    assert pgn1.parse_result() == "win"

    pgn2 = PGN(pgns[1], username, init=False)
    assert pgn2.parse_result() == "draw"

    pgn3 = PGN(pgns[2], username, init=False)
    assert pgn3.parse_result() == "lose"


def test_parse_result(dummy_pgn, username):
    pgns = Fetcher.split(dummy_pgn)

    pgn1 = PGN(pgns[0], username, init=False)
    # Example with castling
    expected_game_1 = "e4 e5 O-O O-O-O N8e7"
    assert pgn1.parse_game().unroll_game() == expected_game_1

    pgn2 = PGN(pgns[2], username, init=False)
    expected_game_2 = (
        "e4 c6 d4 d5 e5 Bf5 Bd3 Bxd3 Qxd3 e6 Nf3 Nd7 O-O Ne7 Nc3 a6 Ne2 c5 c3 Nc6 Bg5"
    )
    assert pgn2.parse_game().unroll_game() == expected_game_2
