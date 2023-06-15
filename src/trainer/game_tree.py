import queue
import chess
from src.data_import.pgn import PGN


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
    def __init__(self, username):
        self.username = username
        self.white = {}
        self.black = {}

    def build_from_pgn_queue(self, pgn_queue: queue.Queue, max_depth):
        while not pgn_queue.empty():
            pgn = PGN(pgn_queue.get(), self.username)
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
            board.push_san(move.val)
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
