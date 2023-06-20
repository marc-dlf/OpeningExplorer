import chess

from src.explorer.game_tree import GameTree


def test_valid_win_ratio(username, csv_path):
    print(csv_path)
    game_tree = GameTree()
    game_tree.load_tree(username, 20, "2023-02", "2023-04", csv_path)

    board = chess.Board()
    board.push_san("e4")

    # Validate results as White
    node = game_tree.white[(board.fen(), True)]

    assert node.res_cnt.win == 37
    assert node.res_cnt.lose == 32
    assert node.player_to_move == True

    # Validate results as black
    node = game_tree.black[(board.fen(), False)]

    assert node.res_cnt.win == 20
    assert node.res_cnt.lose == 17
    assert node.res_cnt.draw == 3
    assert node.player_to_move == False


def test_valid_children(username, csv_path):
    game_tree = GameTree()
    game_tree.load_tree(username, 20, "2023-02", "2023-04", csv_path)

    board = chess.Board()
    node = game_tree.white[(board.fen(), False)]

    assert len(node.children) == 1

    # board once we pushed e4
    board.push_san("e4")
    assert next(iter(node.children))[0] == board.fen()
