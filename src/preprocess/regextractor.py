import re


class RegExtractor:
    GAME_RE = r"(?<=\n)1\..*"
    RESULT_RE = r'\[Result\s"(.*?)"\]'
    LINK_RE = r'\[Link\s"(.*?)"\]'
    MONTH_RE = r'\[UTCDate\s"(.*?)"\]'
    OPENING_RE = r'openings\/"?(.*?)(?:\.|\-[0-9]|\n|")'
    COLOR_RE = r'\[(.*?)\s"PLACEHOLDER"'

    @classmethod
    def get_color(cls, pgn_txt, username):
        try:
            return re.findall(cls.COLOR_RE.replace("PLACEHOLDER", username), pgn_txt)[
                0
            ].lower()
        except:
            raise ValueError("Pattern did not permit to find player color")

    @classmethod
    def get_result(cls, pgn_txt, color):
        result = re.findall(cls.RESULT_RE, pgn_txt)[0]
        if result == "1/2-1/2":
            return "draw"
        elif (result == "1-0" and color == "white") or (
            result == "0-1" and color == "black"
        ):
            return "win"
        else:
            return "lose"

    @classmethod
    def get_game(cls, pgn_txt):
        game = re.findall(cls.GAME_RE, pgn_txt)[0]
        cleaning_re = r"[A-Za-z]+[0-9]?[x]?[A-Za-z]?[0-9]=?[A-Za-z]?\+?|O-O(?:-O)?"
        clean_game = re.findall(cleaning_re, game)
        return " ".join(clean_game)

    @classmethod
    def get_link(cls, pgn_txt):
        try:
            return re.findall(cls.LINK_RE, pgn_txt)[0].lower()
        except:
            raise ValueError("Pattern did not permit to find player link")

    @classmethod
    def get_month(cls, pgn_txt):
        try:
            date_str = re.findall(cls.MONTH_RE, pgn_txt)[0].lower()
        except:
            raise ValueError("Pattern did not permit to find player link")
        date_str = date_str.replace(".", "-")[:-3]
        return date_str

    @classmethod
    def get_opening(cls, pgn_txt):
        try:
            return re.findall(cls.OPENING_RE, pgn_txt)[0].replace("-", " ")
        except:
            raise ValueError(f"Pattern did not permit to find player opening{pgn_txt}")

    @staticmethod
    def split(multi_pgn_txt):
        regex = r'(?<=\[Event "Live Chess"\])[\s\S]*?(?=\[Event "Live Chess"\]|$)'
        matches = re.findall(regex, multi_pgn_txt, re.DOTALL)
        return matches
