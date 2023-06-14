import queue
import chess
from src.pgn_parser import PGNParser


class TreeNode:
    def __init__(self, fen, mymove):
        self.id = fen
        self.mymove = mymove
        self.win_cnt = 0
        self.lose_cnt = 0
        self.draw_cnt = 0
        self.children = set()

    def increment_cnt(self, result):
        if result == "Win":
            self.win_cnt += 1
        elif result == "Lose":
            self.lose_cnt += 1
        elif result == "Draw":
            self.draw_cnt += 1
        else:
            raise ValueError(f'The following result "{result}" is not authorized.')

    def win_rate(self):
        return float(self.win_cnt) / self.n_games()

    def n_games(self):
        return self.win_cnt + self.lose_cnt + self.draw_cnt


class ChessTrainer:
    def __init__(self, username):
        self.username = username
        self.game_tree_white = {}
        self.game_tree_black = {}

    def build_from_pgn_queue(self, pgn_queue: queue.Queue, max_depth):
        while not pgn_queue.empty():
            pgn = PGNParser(pgn_queue.get(), self.username)
            if pgn.color == "White":
                curr_tree = self.game_tree_white
            else:
                curr_tree = self.game_tree_black
            self.process_pgn(pgn, max_depth, curr_tree)

    def process_pgn(self, pgn: PGNParser, max_depth, tree):
        board = chess.Board()
        game = pgn.game

        move = game.first_move
        depth = 0

        mymove = not (pgn.color == "White")
        visited = set()

        while move is not None and depth <= max_depth:
            fen = board.fen()
            if fen not in tree.keys():
                node = TreeNode(fen, mymove)
                tree[fen] = node
            else:
                node = tree[fen]
            if fen not in visited:
                node.increment_cnt(pgn.result)
                visited.add(fen)
            board.push_san(move.val)
            node.children.add(board.fen())
            move = move.next
            depth += 1
            mymove = not mymove

    def extract_most_interesting_positions(self):