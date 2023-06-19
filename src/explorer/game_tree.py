import queue

import chess

from src.explorer.pgn import PGN
from src.explorer.player import Player


class PositionNode:
    def __init__(self, fen, player_to_move, opening):
        self.fen = fen
        self.player_to_move = player_to_move
        self.opening = opening
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
        hero_move = not (pgn.color == "white")
        visited = set()
        while depth <= max_depth and depth < len(game):
            move = game[depth]
            fen = board.fen()
            if fen not in tree.keys():
                node = PositionNode(fen, hero_move, pgn.opening)
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
            hero_move = not hero_move

    def get_worse_k_positions_from_tree(self, tree, thresh, k):
        init_board = chess.Board()
        pos_q = queue.Queue()
        output_q = queue.PriorityQueue()
        visited = set()
        pos_q.put(init_board.fen())
        visited.add(init_board.fen())

        while not pos_q.empty():
            pos_node = tree[pos_q.get()]
            if (not pos_node.player_to_move) and (pos_node.fen not in visited):
                output_q.put((pos_node.win_rate(), pos_node.fen))
            for child_id in pos_node.children:
                if child_id in tree.keys():
                    child = tree[child_id]
                    if child_id not in visited and child.n_games() >= thresh:
                        pos_q.put(child.fen)
            visited.add(pos_node.fen)

        out, i = [], 0
        while not output_q.empty() and i < k:
            out.append(tree[output_q.get()[1]])
        return Result(out)

    def get_worse_k_positions(self, thresh, k):
        return {
            "w": self.get_worse_k_positions_from_tree(self.white, thresh, k),
            "b": self.get_worse_k_positions_from_tree(self.black, thresh, k),
        }


class Result:
    def __init__(self, position_node_list):
        self.positions = position_node_list

    def to_tuples(self):
        return [
            (pos.fen, pos.win_count, pos.lose_count, pos.draw_count, pos.opening)
            for pos in self.positions
        ]
