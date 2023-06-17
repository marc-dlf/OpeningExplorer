import queue
import chess
from src.trainer.pgn import PGN
from src.trainer.player import Player


class PositionNode:
    def __init__(self, fen, mymove):
        self.id = fen
        self.mymove = mymove
        self.win_count = 0
        self.lose_count = 0
        self.draw_count = 0
        self.children = set()
        self.links = []

    def increment_count(self, result):
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

    def load_tree(self, username, max_depth, start_month, end_month, csv_path=None):
        player = Player(username)
        player.load_player_history(start_month, end_month, csv_path)
        for pgn in player.pgn_list:
            self.add_pgn_to_tree(pgn, max_depth)

    def add_pgn_to_tree(self, pgn: PGN, max_depth):
        board = chess.Board()
        tree = self.white if pgn.color == "white" else self.black
        game = pgn.game.split(" ")
        depth = 0
        mymove = not (pgn.color == "white")
        visited = set()
        while depth <= max_depth and depth < len(game):
            move = game[depth]
            fen = board.fen()
            if fen not in tree.keys():
                node = PositionNode(fen, mymove)
                tree[fen] = node
            else:
                node = tree[fen]
            if fen not in visited:
                node.increment_count(pgn.result)
                node.links.append(pgn.link)
                visited.add(fen)
            try:
                board.push_san(move)
            except:
                raise ValueError(f"{depth},{move},{pgn.game,board.fen(),pgn.link}")
            node.children.add(board.fen())
            depth += 1
            mymove = not mymove

    def get_worse_k_positions(self, white: bool, thresh, k):
        init_board = chess.Board()
        pos_q = queue.Queue()
        output_q = queue.PriorityQueue()
        tree = self.white if white else self.black
        visited = set()
        pos_q.put(init_board.fen())
        visited.add(init_board.fen())

        while not pos_q.empty():
            pos_node = tree[pos_q.get()]
            if (not pos_node.mymove) and (pos_node.id not in visited):
                output_q.put((pos_node.win_rate(), pos_node.id))
            for child_id in pos_node.children:
                if child_id in tree.keys():
                    child = tree[child_id]
                    if child_id not in visited and child.n_games() >= thresh:
                        pos_q.put(child.id)
            visited.add(pos_node.id)

        out, i = [], 0
        while not output_q.empty() and i < k:
            out.append(tree[output_q.get()[1]])
        return out
