from src.preprocess.regextractor import RegExtractor


def test_split_good_number_of_games(dummy_pgn):
    pgns = RegExtractor.split(dummy_pgn)
    assert len(pgns) == 3


def test_extract_color(dummy_pgn, username):
    pgns = RegExtractor.split(dummy_pgn)

    assert RegExtractor.get_color(pgns[0], username) == "white"
    assert RegExtractor.get_color(pgns[1], username) == "black"


def test_extract_result(dummy_pgn):
    pgns = RegExtractor.split(dummy_pgn)

    assert RegExtractor.get_result(pgns[0], "white")(pgns[0]) == "win"
    assert RegExtractor.get_result(pgns[1], "black")(pgns[0]) == "draw"
    assert RegExtractor.get_result(pgns[2], "black")(pgns[0]) == "lose"


def test_extract_result(dummy_pgn):
    pgns = RegExtractor.split(dummy_pgn)

    # Example with castling
    expected_game_1 = "e4 e5 O-O O-O-O N8e7 a8=Q b8=Q+ N1xd2 R6xd5"
    assert RegExtractor.get_game(pgns[0]) == expected_game_1
    expected_game_2 = (
        "e4 c6 d4 d5 e5 Bf5 Bd3 Bxd3 Qxd3 e6 Nf3 Nd7 O-O Ne7 Nc3 a6 Ne2 c5 c3 Nc6 Bg5"
    )
    assert RegExtractor.get_game(pgns[2]) == expected_game_2


def test_get_link(dummy_pgn):
    pgns = RegExtractor.split(dummy_pgn)

    expected_link1 = "https://www.chess.com/game/live/75743501325"
    assert RegExtractor.get_link(pgns[0]) == expected_link1


def test_get_month(dummy_pgn):
    pgns = RegExtractor.split(dummy_pgn)

    assert RegExtractor.get_month(pgns[0]) == "2023-04"


def test_get_opening(dummy_pgn):
    pgns = RegExtractor.split(dummy_pgn)

    expected_opening1 = "Philidor Defense Exchange Variation"
    assert RegExtractor.get_opening(pgns[0]) == expected_opening1

    expected_opening2 = "Caro Kann Defense Advance Variation"
    assert RegExtractor.get_opening(pgns[1]) == expected_opening2
