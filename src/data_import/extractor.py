import re


class Extractor:
    def __init__(self, username):
        self.username = username

    def extract_color(self, pgn_txt):
        color_re = rf'\[(.*?)\s"{self.username}"'
        try:
            return re.findall(color_re, pgn_txt)[0].lower()
        except:
            raise ValueError("Pattern did not permit to find player color")

    def extract_result(self, pgn_txt, color=None):
        if color is None:
            color = self.extract_color(pgn_txt)
        result_re = rf'\[Result\s"(.*?)"\]'
        result = re.findall(result_re, pgn_txt)[0]
        if result == "1/2-1/2":
            return "draw"
        elif (result == "1-0" and color == "white") or (
            result == "0-1" and color == "black"
        ):
            return "win"
        else:
            return "lose"

    def extract_game(self, pgn_txt):
        game_re = rf"(?<=\n)1\..*"
        try:
            game = re.findall(game_re, pgn_txt)[0]
        except:
            raise ValueError("No game")
        cleaning_re = r"[A-Za-z]+[0-9]?[x]?[A-Za-z]?[0-9]=?[A-Za-z]?\+?|O-O(?:-O)?"
        clean_game = re.findall(cleaning_re, game)
        return " ".join(clean_game)

    def extract_link(self, pgn_txt):
        link_re = rf'\[Link\s"(.*?)"\]'
        try:
            return re.findall(link_re, pgn_txt)[0].lower()
        except:
            raise ValueError("Pattern did not permit to find player link")

    @staticmethod
    def split(multi_pgn_txt):
        regex = r'(?<=\[Event "Live Chess"\])[\s\S]*?(?=\[Event "Live Chess"\]|$)'
        matches = re.findall(regex, multi_pgn_txt, re.DOTALL)
        return matches
