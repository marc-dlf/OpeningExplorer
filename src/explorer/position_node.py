class ResultCounter:
    def __init__(self):
        self.win = 0
        self.lose = 0
        self.draw = 0

    def __add__(self, other):
        self.win += other.win
        self.lose += other.lose
        self.draw += other.draw

        return self

    def add_win(self):
        self.win += 1

    def add_lose(self):
        self.lose += 1

    def add_draw(self):
        self.draw += 1


class PositionNode:
    def __init__(self, fen, player_to_move, opening):
        self.fen = fen
        self.player_to_move = player_to_move
        self.opening = opening
        self.res_cnt = ResultCounter()
        self.children = set()
        self.links = []

    def __add__(self, other):
        self.res_cnt += other.res_cnt
        self.children.update(other.children)
        self.links += other.links

        return self

    def increment_count(self, result):
        if result == "win":
            self.res_cnt.add_win()
        elif result == "lose":
            self.res_cnt.add_lose()
        elif result == "draw":
            self.res_cnt.add_draw()
        else:
            raise ValueError(f'The following result "{result}" is not authorized.')

    def win_rate(self):
        return float(self.res_cnt.win) / self.n_games()

    def n_games(self):
        return self.res_cnt.win + self.res_cnt.draw + self.res_cnt.lose
