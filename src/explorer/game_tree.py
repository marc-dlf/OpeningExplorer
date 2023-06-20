"""
Contains the GameTree class which goes through games and count the number of wins,draws,
losses per position.
"""

import queue
from functools import reduce
from typing import List, Tuple, Dict, TypeVar

import chess

from src.explorer.pgn import PGN
from src.explorer.player import Player
from src.explorer.position_node import PositionNode


class GameTree:
    def __init__(self):
        self.white = {}
        self.black = {}

    def __add__(self, other):
        for node_id, position in other.white.items():
            if node_id in self.white.keys():
                self.white[node_id] += position
            else:
                self.white[node_id] = position

        for node_id, position in other.black.items():
            if node_id in self.black.keys():
                self.black[node_id] += position
            else:
                self.black[node_id] = position

        return self

    @classmethod
    def from_pgn_list(cls, pgn_list, max_depth):
        tree = cls()
        for pgn in pgn_list:
            tree.add_pgn_to_tree(pgn, max_depth)
        return tree

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
            node_id = (fen, hero_move)
            if node_id not in tree.keys():
                node = PositionNode(fen, hero_move, pgn.opening)
                tree[node_id] = node
            else:
                node = tree[node_id]
            if node_id not in visited:
                node.increment_count(pgn.result)
                node.links.append(pgn.link)
                visited.add(node_id)
            try:
                board.push_san(move)
            except:
                raise ValueError(f"{depth},{move},{pgn.game,board.fen(),pgn.link}")
            hero_move = not hero_move
            next_id = (board.fen(), hero_move)
            node.children.add(next_id)
            depth += 1

    def get_worse_k_positions_from_tree(self, tree, color, thresh, k):
        init_board = chess.Board()
        pos_q = queue.Queue()
        output_q = queue.PriorityQueue()
        visited = set()
        hero_move = not (color == "white")
        node_id = (init_board.fen(), hero_move)
        pos_q.put(node_id)
        visited.add(node_id)

        while not pos_q.empty():
            node_id = pos_q.get()
            pos_node = tree[node_id]
            if (not pos_node.player_to_move) and (node_id not in visited):
                output_q.put((pos_node.win_rate(), node_id))
            for child_id in pos_node.children:
                if child_id in tree.keys():
                    child = tree[child_id]
                    if child_id not in visited and child.n_games() >= thresh:
                        pos_q.put(child_id)
            visited.add(node_id)

        out, i = [], 0
        while not output_q.empty() and i < k:
            _, node_id = output_q.get()
            out.append(tree[node_id])
        return DashInput(out)

    def get_worse_k_positions(self, thresh, k):
        return {
            "w": self.get_worse_k_positions_from_tree(self.white, "white", thresh, k),
            "b": self.get_worse_k_positions_from_tree(self.black, "black", thresh, k),
        }


def load_tree_multiproc(
    n_procs, username, max_depth, start_month, end_month, csv_path=None
):
    from multiprocessing import Pool

    pool = Pool(n_procs)
    player = Player(username)
    player.load_player_history(start_month, end_month, csv_path)
    chunk_size = len(player.pgn_list) // n_procs
    pgn_chunks = [
        player.pgn_list[i : i + chunk_size]
        for i in range(0, len(player.pgn_list), chunk_size)
    ]
    trees = pool.starmap(
        GameTree.from_pgn_list, zip(pgn_chunks, [max_depth] * n_procs)
    )
    out = reduce(lambda x, y: x + y, trees)
    return out


class Result:
    T = TypeVar("T")
    T: T = Tuple[str, int, int, int, int, str]

    def __init__(self, position_node_list: List[PositionNode]):
        self.positions = position_node_list

    def to_tuples(self) -> T:
        return [
            (pos.fen, pos.res_cnt.win, pos.res_cnt.lose, pos.res_cnt.draw, pos.opening)
            for pos in self.positions
        ]
