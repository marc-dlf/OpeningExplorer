"""Position Node class which wraps all relevant informations about a position node."""
from __future__ import annotations


class ResultCounter:
    """Simple Counter Class for win/draw/lose at a given position.

    Attributes
    ----------
    win (int) : Number of wins from this position.
    draw (int)  : Number of draws from this position.
    lose (int) : Number of losses from this position.
    """

    def __init__(self):
        """Construct an initial counter."""
        self.win = 0
        self.lose = 0
        self.draw = 0

    def __add__(self, other: ResultCounter) -> ResultCounter:
        """Define add operator for ResultCounter."""
        self.win += other.win
        self.lose += other.lose
        self.draw += other.draw

        return self

    def add_win(self):
        """Increment win count."""
        self.win += 1

    def add_lose(self):
        """Increment lose count."""
        self.lose += 1

    def add_draw(self):
        """Increment draw count."""
        self.draw += 1


class PositionNode:
    """Position Node class which wraps all relevant informations about a position node.

    Attributes
    ----------
    fen (str) : String describing the board position in a compact way.
    last_move_hero (bool)  : Boolean set to True if Hero played the last move.
    opening (str) : Name of the opening.
    res_cnt (ResultCounter) : ResultCounter for the node.
    children (Set[Tuple[str,bool]]) : Node ids which start from this node.
    links (List[str]) = List of links to games in chess.com from this node.
    """

    def __init__(self, fen: str, last_move_hero: bool, opening: str):
        """
        Construct empty PositionNode.

        Parameters
        ----------
            fen : str
                String describing the board position in a compact way.
            last_move_hero : bool
                Boolean set to True if Hero played the last move.
            opening :str
                Name of the opening.
        """
        self.fen = fen
        self.last_move_hero = last_move_hero
        self.opening = opening
        self.res_cnt = ResultCounter()
        self.children = set()
        self.links = []

    def __add__(self, other: PositionNode) -> PositionNode:
        """Define add operator for PositionNode.

        The result counters are added, children from others are added to self children
        and links to games from other are added to self.
        """
        self.res_cnt += other.res_cnt
        self.children.update(other.children)
        self.links += other.links

        return self

    def increment_count(self, result):
        """Increment ResultCounter.

        Parameters
        ----------
            result : str
                String describing the result, it can be win/draw/lose.
        """
        if result == "win":
            self.res_cnt.add_win()
        elif result == "lose":
            self.res_cnt.add_lose()
        elif result == "draw":
            self.res_cnt.add_draw()
        else:
            raise ValueError(f'The following result "{result}" is not authorized.')

    def win_rate(self):
        """Compute win rate."""
        return float(self.res_cnt.win) / self.n_games()

    def n_games(self):
        """Compute number of games."""
        return self.res_cnt.win + self.res_cnt.draw + self.res_cnt.lose
