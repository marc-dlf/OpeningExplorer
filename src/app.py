# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, ctx, callback, Input, Output, State
import chess
import chess.svg
from cairosvg import svg2png
import pybase64

from src.trainer.game_tree import GameTree

app = Dash(__name__)

gt = GameTree()
gt.load_tree("julesbyt", 10)
q = gt.extract_most_interesting_positions(True, 5)

elts = [q.get()[1], q.get()[1], q.get()[1]]

board = chess.Board(q.get()[1])
svg = chess.svg.board(board, size=400)
img = pybase64.b64encode(svg2png(bytestring=svg)).decode()

app.layout = html.Div(
    children=[
        html.H1(children="Opening Weaknesses Explorer", style={"textAlign": "center"}),
        html.Div(
            children=[
                html.Div(
                    html.Img(
                        id="board",
                    ),
                    style={
                        "width": "50%",
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "center",
                    },
                ),
                html.H1(
                    children="Right",
                ),
            ],
            style={"display": "flex", "margin-bottom": "100px", "margin-top": "100px"},
        ),
        dcc.Input(id="playername", type="text", placeholder=""),
        html.Button("Submit", id="submit-val", n_clicks=0),
        dcc.Dropdown(["0", "1", "2"], "0", id="dropdown"),
        # dcc.Store stores the intermediate value
        dcc.Store(id="board-svg"),
        dcc.Store(id="player-examples"),
        html.Div(
            id="container-button-basic", children="Enter a value and press submit"
        ),
    ]
)


@callback(
    Output("player-examples", "data"),
    Input("submit-val", "n_clicks"),
    State("playername", "value"),
)
def on_click(n_clicks, value):
    gt = GameTree()
    gt.load_tree(value, 10, start_month="2023-04", end_month="2023-05")
    q = gt.extract_most_interesting_positions(True, 5)
    if q is not None:
        elts = [q.get()[1], q.get()[1], q.get()[1]]
        return elts
    else:
        return None


@callback(
    Output("board-svg", "data"),
    [Input("dropdown", "value"), Input("player-examples", "data")],
)
def clean_data(value, examples):
    if examples is None:
        return "data:image/png;base64,"
    else:
        board = chess.Board(examples[int(value)])
        svg = chess.svg.board(board, size=400)
        img = pybase64.b64encode(svg2png(bytestring=svg)).decode()
        return "data:image/png;base64,{}".format(img)


@callback(Output("board", "src"), Input("board-svg", "data"))
def update_img(src_img):
    return src_img


if __name__ == "__main__":
    app.run_server(debug=True)
