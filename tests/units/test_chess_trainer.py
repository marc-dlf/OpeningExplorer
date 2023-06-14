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

    node = trainer.game_tree_white[board.fen]

    assert node.win_rate() == 0.4
