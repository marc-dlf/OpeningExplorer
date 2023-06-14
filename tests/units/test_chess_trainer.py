import chess

from src.fetcher import Fetcher
from src.chess_trainer import ChessTrainer


def test_valid_win_ratio(complete_pgn, username):
    fetcher = Fetcher(username, "2023-03")
    fetcher.push_into_queue(Fetcher.split(complete_pgn))
    trainer = ChessTrainer(username)
    trainer.build_from_pgn_queue(fetcher.processing_queue, 20)

    board = chess.Board()
    board.push_san("e4")

    # Validate results as White
    node = trainer.game_tree_white[board.fen()]

    assert node.win_cnt == 37
    assert node.lose_cnt == 32
    assert node.mymove == True

    # Validate results as black
    node = trainer.game_tree_black[board.fen()]

    assert node.win_cnt == 20
    assert node.lose_cnt == 17
    assert node.draw_cnt == 3
    assert node.mymove == False


def test_valid_children(complete_pgn, username):
    fetcher = Fetcher(username, "2023-03")
    fetcher.push_into_queue(Fetcher.split(complete_pgn))
    trainer = ChessTrainer(username)
    trainer.build_from_pgn_queue(fetcher.processing_queue, 20)

    board = chess.Board()
    node = trainer.game_tree_white[board.fen()]

    assert len(node.children) == 1

    # board once we pushed e4
    board.push_san("e4")
    assert next(iter(node.children)) == board.fen()
