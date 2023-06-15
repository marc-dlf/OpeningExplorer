import re


class Move:
    def __init__(self, move):
        self.val = move
        self.next = None


class Game:
    def __init__(self, move):
        self.first_move = move

    def unroll_game(self):
        move = self.first_move
        out_str = ""
        while move is not None:
            out_str += f"{move.val} "
            move = move.next
        return out_str.strip()


class PGN:
    def __init__(self, pgn_txt, username, init=True):
        self.pgn_txt = pgn_txt
        self.username = username
        self.color = None
        self.result = None
        self.game = None

        if init:
            self.parse_info()

    def parse_info(self):
        self.color = self.parse_color()
        self.result = self.parse_result()
        self.game = self.parse_game()

    def parse_game(self):
        game_re = rf"(?<=\n)1\..*"
        try:
            game = re.findall(game_re, self.pgn_txt)[0]
            cleaning_re = r"[A-Za-z][0-9][A-Za-z][0-9]|[A-Za-z]+[0-9]|O-O-O|O-O"
            clean_game = re.findall(cleaning_re, game)
            move = Move(clean_game[0])
            game = Game(move)
            for i in range(1, len(clean_game)):
                move.next = Move(clean_game[i])
                move = move.next
            return game
        except:
            raise ValueError("Pattern did not permit to find game")

    def parse_color(self):
        color_re = rf'\[(.*?)\s"{self.username}"'
        try:
            return re.findall(color_re, self.pgn_txt)[0].lower()
        except:
            raise ValueError("Pattern did not permit to find player color")

    def parse_result(self):
        color = self.color
        if color is None:
            color = self.parse_color()
        result_re = rf'\[Result\s"(.*?)"\]'
        try:
            result = re.findall(result_re, self.pgn_txt)[0]
            if result == "1/2-1/2":
                return "draw"
            elif (result == "1-0" and color == "white") or (
                result == "0-1" and color == "black"
            ):
                return "win"
            else:
                return "lose"
        except:
            raise ValueError("Pattern did not permit to find result")
