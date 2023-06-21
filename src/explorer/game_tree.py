"""GameTree class which holds count of number of wins,draws,losses per position."""

from __future__ import annotations
import queue
from functools import reduce
from typing import List, Tuple, Dict, TypeVar


import chess

from src.explorer.pgn import PGN
from src.explorer.player import Player
from src.explorer.position_node import PositionNode


class GameTree:
    """GameTree class which holds count of number of wins,draws,losses per position.

    Contains two dictionaries, one for which the analysed player (which will be called
    Hero from now on) has white pieces and the other black pieces.
    Dictionary's keys are unique positions which corresponds to:
        1.the positions of pieces on the board
        2.which player played the last move.
    Dictionary's values corresponds to instances of PositionNode which encapsulate
    information for the given unique position (opening name,result count and link
    to games).
    ...

    Attributes
    ----------
    white (Dict[Tuple[str,bool],PositionNode]) : Position dictionary for white.
    black (Dict[Tuple[str,bool],PositionNode])  : Position dictionary for black.
    """

    def __init__(self):
        """Construct an empty GameTree."""
        self.white = {}
        self.black = {}

    def __add__(self, other: GameTree) -> GameTree:
        """Add operator for GameTree.

        For each node_id in other trees, if the node_id is also in the similar tree of
        self, nodes are added, else the node is added to self tree.

        Parameters
        ----------
            other : GameTree
                GameTree to add to self.

        Returns:
            self (GameTree) : Updated GameTree.
        """
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
    def from_pgn_list(cls, pgn_list: List[PGN], max_depth: int) -> GameTree:
        """Instantiate a GameTree instance from a PGN list.

        Parameters
        ----------
            pgn_list : List[PGN]
                A list containing all the PGNs of Hero from csv.
            max_depth : int
                Maximum number of moves in the game used to build tree.

        Returns:
            tree (GameTree) : GameTree from loaded PGNs.
        """
        tree = cls()
        for pgn in pgn_list:
            tree.add_pgn_to_tree(pgn, max_depth)
        return tree

    def load_tree(
        self,
        username: str,
        max_depth: int,
        start_month: str,
        end_month: str,
        csv_path: str = None,
    ):
        """Load a tree from a username and a time period or a csv.

        Parameters
        ----------
            username : str
                Username of Hero.
            max_depth : int
                Maximum number of moves in the game used to build tree.
            start_month : str
                Start month in format YYYY-MM (eg: 2023-01).
            end_month : str
                End month in format YYYY-MM (eg: 2023-01).
            csv_path : str
                Path to a csv file from which the player history is loaded in priority.

        """
        # pylint: disable=line-too-long
        player = Player(username)
        player.load_player_history(start_month, end_month, csv_path)
        for pgn in player.pgn_list:
            self.add_pgn_to_tree(pgn, max_depth)

    def add_pgn_to_tree(self, pgn: PGN, max_depth: int):
        """Increment result all nodes of unique positions found in the game.

        Parameters
        ----------
            pgn : PGN
                Individual PGN instance
            max_depth : int
                Maximum number of moves in the game used to build tree.

        """
        # pylint: disable=line-too-long
        # Choosing the tree depending on the pgn color attribte.
        tree = self.white if pgn.color == "white" else self.black
        # Spliting game string to get a list of individual moves.
        game = pgn.game.split(" ")
        # If hero has white pieces, we consider that his opponent played the last move for init.
        last_move_hero = pgn.color == "black"
        # Number of moves played.
        depth = 0
        # Initial chess board.
        board = chess.Board()
        visited = set()
        # Iterating through unique positions encountered in the game to increment their counters.
        while depth <= max_depth and depth < len(game):
            move = game[depth]
            fen = board.fen()
            node_id = (fen, last_move_hero)
            if node_id not in tree.keys():
                node = PositionNode(fen, last_move_hero, pgn.opening)
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
            # Inverting the variable : if hero just played, he made the last move.
            last_move_hero = not last_move_hero
            next_id = (board.fen(), last_move_hero)
            node.children.add(next_id)
            depth += 1

    def get_worse_k_positions_from_tree(
        self, tree: GameTree, color: str, thresh: int, k: int
    ) -> Result:
        """Extract from the tree the worst k positions with respect to win rate.

        Parameters
        ----------
            tree : GameTree
                Tree with all positions node with incremented counters.
            color : str
                Color of hero's pieces.
            thresh : int
                Minimal number of games at a given node to be considered in the final solution.
            k: int
                Number of positions to extract.

        Returns:
            out (Result) : All the positions to be analyzed for this tree.
        """
        # pylint: disable=line-too-long
        board = chess.Board()
        last_move_hero = color == "black"
        node_id = (board.fen(), last_move_hero)
        # Position queue for tree traversal.
        pos_q = queue.Queue()
        # Priority Queue where the positions with minimal win rates will be on top.
        output_q = queue.PriorityQueue()
        visited = set()
        pos_q.put(node_id)
        visited.add(node_id)
        # Traversing the game tree to add positions node to priority queue with win rate as priority value.
        while not pos_q.empty():
            node_id = pos_q.get()
            pos_node = tree[node_id]
            if (not pos_node.last_move_hero) and (node_id not in visited):
                output_q.put((pos_node.win_rate(), node_id))
            for child_id in pos_node.children:
                if child_id in tree.keys():
                    child = tree[child_id]
                    # Stopping exploration once we reach a position with a number of games below threshold.
                    if child_id not in visited and child.n_games() >= thresh:
                        pos_q.put(child_id)
            visited.add(node_id)

        out, i = [], 0
        # Unpacking priority queue to get top k elements (with worst win rates).
        while not output_q.empty() and i < k:
            _, node_id = output_q.get()
            out.append(tree[node_id])
        return Result(out)

    def get_worse_k_positions(self, thresh: int, k: int):
        """Get worse k positions for white and black trees.

        Parameters
        ----------
            thresh : int
                Minimal number of games at a given node to be considered in the final solution.
            k: int
                Number of positions to extract.

        Returns:
            out (Dict[str:Result]) : Worst k positions in terms of win rate of white and black tree in a dict.
        """
        # pylint: disable=line-too-long
        return {
            "w": self.get_worse_k_positions_from_tree(self.white, "white", thresh, k),
            "b": self.get_worse_k_positions_from_tree(self.black, "black", thresh, k),
        }


def load_tree_multiproc(
    n_procs: int,
    username: str,
    max_depth: int,
    start_month: str,
    end_month: str,
    csv_path: str = None,
):
    """Multiprocessing version of the load_tree method.

    Leverages the fact that we can parallelize the tree building and then due to the
    type of operations performed, it is possible to apply a reduce method to get our
    final output.

    Parameters
    ----------
        n_procs : int
            Number of processors to be used.
        username : str
            Username of Hero.
        max_depth : int
            Maximum number of moves in the game used to build tree.
        start_month : str
            Start month in format YYYY-MM (eg: 2023-01).
        end_month : str
            End month in format YYYY-MM (eg: 2023-01).
        csv_path : str
            Path to a csv file from which the player history is loaded in priority.

    Returns:
        out (GameTree):  An initiated GameTree with Hero's games.
    """
    # pylint: disable=too-many-arguments
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
    """Wrapper for Result."""

    T = TypeVar("T")
    T: T = Tuple[str, int, int, int, int, str]

    def __init__(self, position_node_list: List[PositionNode]):
        """Construct Result."""
        self.positions = position_node_list

    def to_tuples(self) -> T:
        """Convert Result to tuples which can be stored in Dash app Store."""
        return [
            (pos.fen, pos.res_cnt.win, pos.res_cnt.lose, pos.res_cnt.draw, pos.opening)
            for pos in self.positions
        ]
