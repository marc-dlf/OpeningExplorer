from src.preprocess.regextractor import RegExtractor


class PGN:
    def __init__(
        self,
        color,
        result,
        link,
        game,
        month,
        opening,
    ):
        self.color = color
        self.result = result
        self.link = link
        self.game = game
        self.month = month
        self.opening = opening

    @classmethod
    def extract_from_txt(cls, pgn_txt, username):
        color = RegExtractor.get_color(pgn_txt, username)
        result = RegExtractor.get_result(pgn_txt, color)
        link = RegExtractor.get_link(pgn_txt)
        month = RegExtractor.get_month(pgn_txt)
        opening = RegExtractor.get_opening(pgn_txt)
        game = RegExtractor.get_game(pgn_txt)
        return cls(color, result, link, game, month, opening)
