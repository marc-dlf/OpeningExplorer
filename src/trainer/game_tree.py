import queue
import chess
from pathlib import Path
from src.data_import.pgn import PGN
from src.data_import.fetcher import Fetcher
from src.constants import DATA_FOLDER
import os


class PositionNode:
    def __init__(self, fen, mymove):
        self.id = fen
        self.mymove = mymove
        self.win_count = 0
        self.lose_count = 0
        self.draw_count = 0
        self.children = set()

    def increment_cnt(self, result):
        if result == "win":
            self.win_count += 1
        elif result == "lose":
            self.lose_count += 1
        elif result == "draw":
            self.draw_count += 1
        else:
            raise ValueError(f'The following result "{result}" is not authorized.')

    def win_rate(self):
        return float(self.win_count) / self.n_games()

    def n_games(self):
        return self.win_count + self.lose_count + self.draw_count


class GameTree:
    def __init__(self):
        self.white = {}
        self.black = {}

    def load_tree(
        self, username, max_depth, start_month=None, end_month=None, str_init=None
    ):
        if str_init is not None:
            self.process_multi_pgn(str_init, max_depth, username)
        else:
            if username not in os.listdir(DATA_FOLDER):
                f = Fetcher(username)
                f.download_all(start_month, end_month)

            path = Path(DATA_FOLDER) / username
            for pgn_month in os.listdir(path):
                with open(path / f"{pgn_month}", "r") as f:
                    multi_pgn = f.read()
                self.process_multi_pgn(multi_pgn, max_depth, username)

    def process_multi_pgn(self, multi_pgn, max_depth, username):
        for pgn_txt in PGN.split(multi_pgn):
            try:
                pgn = PGN(pgn_txt, username, True)
            except:
                print(f"Failed extraction for : {pgn_txt}")
                continue
            self.process_pgn(pgn, max_depth)

    def process_pgn(self, pgn: PGN, max_depth):
        board = chess.Board()
        tree = self.white if pgn.color == "white" else self.black
        move = pgn.game.first_move
        depth = 0
        mymove = not (pgn.color == "white")
        visited = set()
        while move is not None and depth <= max_depth:
            fen = board.fen()
            if fen not in tree.keys():
                node = PositionNode(fen, mymove)
                tree[fen] = node
            else:
                node = tree[fen]
            if fen not in visited:
                node.increment_cnt(pgn.result)
                visited.add(fen)
            try:
                board.push_san(move.val)
            except:
                if move.val == "bxa8":
                    return
                raise ValueError(f"{move.val},{pgn.game.unroll_game(),board.fen()}")
            node.children.add(board.fen())
            move = move.next
            depth += 1
            mymove = not mymove

    def extract_most_interesting_positions(self, white: bool, thresh=3):
        init_board = chess.Board()
        pos_q = queue.Queue()
        output_q = queue.PriorityQueue()
        if white:
            tree = self.white
        else:
            self.black
        visited = set()
        pos_q.put(init_board.fen())
        visited.add(init_board.fen())
        while not pos_q.empty():
            curr_pos = pos_q.get()
            for child_id in tree[curr_pos].children:
                if child_id in tree.keys():
                    child = tree[child_id]
                    if child_id not in visited:
                        pos_q.put(child.id)
                        if not child.mymove and child.n_games() >= thresh:
                            output_q.put((child.win_rate(), child.id))
            visited.add(curr_pos)
        return output_q
