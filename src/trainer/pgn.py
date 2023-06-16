from src.data_import.extractor import Extractor


class PGN:
    def __init__(self, username, color=None, result=None, link=None, game=None):
        self.username = username
        self.color = color
        self.result = result
        self.link = link
        self.game = game

    @classmethod
    def extract_from_txt(cls, username, pgn_txt):
        e = Extractor(username)
        color = e.extract_color(pgn_txt)
        result = e.extract_result(pgn_txt)
        link = e.extract_link(pgn_txt)
        try:
            game = e.extract_game(pgn_txt)
        except:
            raise ValueError("failed extraction")
        return cls(username, color, result, link, game)
