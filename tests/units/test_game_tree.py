import chess

from src.trainer.game_tree import GameTree


def test_valid_win_ratio(complete_pgn, username):
    game_tree = GameTree()
    game_tree.load_tree(username, 20, str_init=complete_pgn)

    board = chess.Board()
    board.push_san("e4")

    # Validate results as White
    node = game_tree.white[board.fen()]

    assert node.win_count == 37
    assert node.lose_count == 32
    assert node.mymove == True

    # Validate results as black
    node = game_tree.black[board.fen()]

    assert node.win_count == 20
    assert node.lose_count == 17
    assert node.draw_count == 3
    assert node.mymove == False


def test_valid_children(complete_pgn, username):
    game_tree = GameTree()
    game_tree.load_tree(username, 20, str_init=complete_pgn)

    board = chess.Board()
    node = game_tree.white[board.fen()]

    assert len(node.children) == 1

    # board once we pushed e4
    board.push_san("e4")
    assert next(iter(node.children)) == board.fen()
