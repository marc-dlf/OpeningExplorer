from src.data_import.extractor import Extractor


def test_split_good_number_of_games(dummy_pgn):
    pgns = Extractor.split(dummy_pgn)
    assert len(pgns) == 3


def test_parse_color(dummy_pgn, username):
    pgns = Extractor.split(dummy_pgn)

    e = Extractor(username)
    assert e.extract_color(pgns[0]) == "white"
    assert e.extract_color(pgns[1]) == "black"


def test_parse_result(dummy_pgn, username):
    pgns = Extractor.split(dummy_pgn)

    e = Extractor(username)
    assert e.extract_result(pgns[0]) == "win"
    assert e.extract_result(pgns[1]) == "draw"
    assert e.extract_result(pgns[2]) == "lose"


def test_parse_result(dummy_pgn, username):
    pgns = Extractor.split(dummy_pgn)

    e = Extractor(username)
    # Example with castling
    expected_game_1 = "e4 e5 O-O O-O-O N8e7 a8=Q b8=Q+ N1xd2 R6xd5"
    assert e.extract_game(pgns[0]) == expected_game_1
    expected_game_2 = (
        "e4 c6 d4 d5 e5 Bf5 Bd3 Bxd3 Qxd3 e6 Nf3 Nd7 O-O Ne7 Nc3 a6 Ne2 c5 c3 Nc6 Bg5"
    )
    assert e.extract_game(pgns[2]) == expected_game_2


def test_parse_link(dummy_pgn, username):
    pgns = Extractor.split(dummy_pgn)

    e = Extractor(username)
    expected_link1 = "https://www.chess.com/game/live/75743501325"
    assert e.extract_link(pgns[0]) == expected_link1
