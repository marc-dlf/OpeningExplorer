import chess

from src.data_import.fetcher import Fetcher
from src.trainer.game_tree import GameTree


def test_valid_win_ratio(complete_pgn, username):
    fetcher = Fetcher(username, "2023-03")
    q = fetcher.push_into_queue(Fetcher.split(complete_pgn))
    game_tree = GameTree(username)
    game_tree.build_from_pgn_queue(q, 20)

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
    fetcher = Fetcher(username, "2023-03")
    q = fetcher.push_into_queue(Fetcher.split(complete_pgn))
    game_tree = GameTree(username)
    game_tree.build_from_pgn_queue(q, 20)

    board = chess.Board()
    node = game_tree.white[board.fen()]

    assert len(node.children) == 1

    # board once we pushed e4
    board.push_san("e4")
    assert next(iter(node.children)) == board.fen()
