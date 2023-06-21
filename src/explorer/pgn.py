"""PGN class which contains relevant fields from raw PGN."""
from src.preprocess.regextractor import RegExtractor


class PGN:
    """PGN class which contains relevant fields from raw PGN.

    Attributes
    ----------
    color (str): Color of Hero's pieces.
    result (str): Result of Hero.
    link (str): Link to Chess.com game.
    game (str): Succession of moves separated by spaces.
    month (str): Month in the format YYYY-MM.
    opening (str): Opening name.
    """

    def __init__(
        self,
        color: str,
        result: str,
        link: str,
        game: str,
        month: str,
        opening: str,
    ):
        """PGN class which contains relevant fields from raw PGN.

        Parameters
        ----------
            color : str
                Color of Hero's pieces.
            result : str
                Result of Hero.
            link : str
                Link to Chess.com game.
            game : str
               Succession of moves separated by spaces.
            month : str
                Month in the format YYYY-MM.
            opening : str
                Opening name.
        """
        self.color = color
        self.result = result
        self.link = link
        self.game = game
        self.month = month
        self.opening = opening

    @classmethod
    def extract_from_txt(cls, pgn_txt: str, username: str):
        """Construct a PGN from a raw PGN string.

        Parameters
        ----------
            pgn_txt : str
                Raw multi line individual PGN downloaded from Chess.com.
            username : str
                Username of Hero.
        """
        color = RegExtractor.get_color(pgn_txt, username)
        result = RegExtractor.get_result(pgn_txt, color)
        link = RegExtractor.get_link(pgn_txt)
        month = RegExtractor.get_month(pgn_txt)
        opening = RegExtractor.get_opening(pgn_txt)
        game = RegExtractor.get_game(pgn_txt)
        return cls(color, result, link, game, month, opening)
