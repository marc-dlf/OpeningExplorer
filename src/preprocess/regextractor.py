"""Extractor class to get all informations from raw PGNs from Chess.com."""

import re
from typing import List


class RegExtractor:
    """
    A class to represent a person.

    ...

    Attributes
    ----------
    GAME_RE : str
        Regex to extract the game moves.
    RESULT_RE : str
        Regex to extract the game result.
    LINK_RE : str
        Regex to extract the link of the game.
    MONTH_RE : str
        Regex to extract the month.
    OPENING_RE : str
        Regex to extract the opening name.
    COLOR_RE : str
        Regex to extract the color of the inspected player.
    """

    GAME_RE = r"(?<=\n)1\..*"
    RESULT_RE = r'\[Result\s"(.*?)"\]'
    LINK_RE = r'\[Link\s"(.*?)"\]'
    MONTH_RE = r'\[UTCDate\s"(.*?)"\]'
    OPENING_RE = r'openings\/"?(.*?)(?:\.|\-[0-9]|\n|")'
    COLOR_RE = r'\[(.*?)\s"PLACEHOLDER"'

    @classmethod
    def get_color(cls, pgn_txt: str, username: str) -> str:
        """
        Extract the game color with the provided regex and the username.

            Parameters:
                pgn_txt (str) : Individual raw pgn from chess.com.
                username (str) : Username of the inspected player.

            Returns:
                color (str) : Color of the inspected player.
        """
        try:
            return re.findall(cls.COLOR_RE.replace("PLACEHOLDER", username), pgn_txt)[
                0
            ].lower()
        except:
            raise ValueError("Pattern did not permit to find player color")

    @classmethod
    def get_result(cls, pgn_txt: str, color: str) -> str:
        """
        Extract the game result with the provided regex and the color.

            Parameters:
                pgn_txt (str) : Individual raw pgn from chess.com.
                color (str) : Color of the inspected player.

            Returns:
                result (str) : Result of the game.
        """
        result = re.findall(cls.RESULT_RE, pgn_txt)[0]
        if result == "1/2-1/2":
            return "draw"
        if (result == "1-0" and color == "white") or (
            result == "0-1" and color == "black"
        ):
            return "win"
        return "lose"

    @classmethod
    def get_game(cls, pgn_txt: str) -> str:
        """
        Extract the game moves with the provided regex.

            Parameters:
                pgn_txt (str) : Individual raw pgn from chess.com.

            Returns:
                game (str) : Succession of moves in the game separated by spaces.
        """
        game = re.findall(cls.GAME_RE, pgn_txt)[0]
        cleaning_re = r"[A-Za-z]+[0-9]?[x]?[A-Za-z]?[0-9]=?[A-Za-z]?\+?|O-O(?:-O)?"
        clean_game = re.findall(cleaning_re, game)
        return " ".join(clean_game)

    @classmethod
    def get_link(cls, pgn_txt: str) -> str:
        """
        Extract the game moves with the provided regex.

            Parameters:
                pgn_txt (str) : Individual raw pgn from chess.com.

            Returns:
                game (str) : Succession of moves in the game separated by spaces.
        """
        try:
            return re.findall(cls.LINK_RE, pgn_txt)[0].lower()
        except:
            raise ValueError("Pattern did not permit to find player link")

    @classmethod
    def get_month(cls, pgn_txt: str) -> str:
        """
        Extract the game month with the provided regex.

            Parameters:
                pgn_txt (str) : Individual raw pgn from chess.com.

            Returns:
                month (str) : Month of the game in the format YYYY-MM.
        """
        try:
            date_str = re.findall(cls.MONTH_RE, pgn_txt)[0].lower()
        except:
            raise ValueError("Pattern did not permit to find player link")
        date_str = date_str.replace(".", "-")[:-3]
        return date_str

    @classmethod
    def get_opening(cls, pgn_txt: str) -> str:
        """
        Extract the game opening's name with the provided regex.

            Parameters:
                pgn_txt (str) : Individual raw pgn from chess.com.

            Returns:
                opening (str) : Opening game.
        """
        try:
            return re.findall(cls.OPENING_RE, pgn_txt)[0].replace("-", " ")
        except:
            raise ValueError(f"Pattern did not permit to find player opening{pgn_txt}")

    @staticmethod
    def split(multi_pgn_txt: str) -> List[str]:
        """
        Split a raw Chess.com PGN file with multiple PGNs into a list of individual PGNs.

            Parameters:
                multi_pgn_txt (str) : Raw Chess.com PGN file with multiple PGNs.

            Returns:
                pgn_list (List[str]) : List of splited raw pgn strings.
        """
        regex = r'(?<=\[Event "Live Chess"\])[\s\S]*?(?=\[Event "Live Chess"\]|$)'
        matches = re.findall(regex, multi_pgn_txt, re.DOTALL)
        return matches
