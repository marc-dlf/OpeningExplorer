# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, ctx, callback, Input, Output, State
import chess
import chess.svg
from cairosvg import svg2png
import pybase64
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd


from src.trainer.game_tree import GameTree
import src.config as config

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

BASE_BOARD = chess.Board()
BASE_SVG = chess.svg.board(BASE_BOARD, size=500)
BASE_IMG = pybase64.b64encode(svg2png(bytestring=BASE_SVG)).decode()

app.layout = html.Div(
    children=[
        html.H1(
            children="Opening Weaknesses Explorer",
            style={"textAlign": "center", "margin-top": "50px"},
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H3(
                            id="opening",
                            children="Opening name",
                            style={"textAlign": "center"},
                        ),
                        html.Img(
                            id="board",
                        ),
                        html.Div(
                            children=[
                                dcc.Input(
                                    id="playername", type="text", placeholder=""
                                ),
                                html.Button("Submit", id="submit-val", n_clicks=0),
                                dcc.Dropdown(
                                    [str(i) for i in range(config.N_POSITIONS)],
                                    "0",
                                    id="dropdown",
                                ),
                                dcc.RadioItems(
                                    ["White", "Black"], "White", id="color"
                                ),
                            ],
                            style={"display": "flex", "margin-top": "30px"},
                        ),
                    ],
                    style={
                        "width": "50%",
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "center",
                        "flex-direction": "column",
                    },
                ),
                dcc.Graph(id="graph"),
            ],
            style={"display": "flex", "margin-bottom": "50px", "margin-top": "100px"},
        ),
        dcc.Loading(id="loading01", children=html.Div(id="loading-output1")),
        # dcc.Store stores the intermediate value
        dcc.Store(id="board-svg"),
        dcc.Store(id="player-examples"),
    ]
)


@callback(
    Output("player-examples", "data"),
    Output("loading-output1", "children"),
    Input("submit-val", "n_clicks"),
    State("playername", "value"),
)
def on_click(n_clicks, value):
    if value is None:
        return None, ""
    gt = GameTree()
    gt.load_tree(value, 14, config.START_MONTH, config.END_MONTH)
    positions = gt.get_worse_k_positions(3, 10)
    positions_white = [
        (elt.id, elt.win_count, elt.lose_count, elt.draw_count, elt.opening)
        for elt in positions["white"]
    ]
    positions_black = [
        (elt.id, elt.win_count, elt.lose_count, elt.draw_count, elt.opening)
        for elt in positions["black"]
    ]
    return {"w": positions_white, "b": positions_black}, ""


@callback(
    Output("board-svg", "data"),
    Output("opening", "children"),
    [
        Input("dropdown", "value"),
        Input("player-examples", "data"),
        Input("color", "value"),
    ],
)
def load_board(value, examples, color):
    if examples is None or value is None:
        return f"data:image/png;base64,{BASE_IMG}", "Opening Name"
    else:
        e = examples["w"] if color == "White" else examples["b"]
        fen, _, _, _, opening = e[int(value)]
        board = chess.Board(fen)
        if color == "Black":
            board = board.transform(chess.flip_vertical).transform(
                chess.flip_horizontal
            )
        svg = chess.svg.board(board, size=500)
        img = pybase64.b64encode(svg2png(bytestring=svg)).decode()
        return f"data:image/png;base64,{img}", opening


@callback(Output("board", "src"), Input("board-svg", "data"))
def update_img(src_img):
    return src_img


@callback(
    Output("graph", "figure"),
    [
        Input("dropdown", "value"),
        Input("player-examples", "data"),
        Input("color", "value"),
    ],
)
def update_bar_chart(value, examples, color):
    win, lose, draw = 0, 0, 0
    if examples is not None and value is not None:
        e = examples["w"] if color == "White" else examples["b"]
        ex = e[int(value)]
        win, lose, draw = ex[1], ex[2], ex[3]
    df = pd.DataFrame(
        {
            "Result": ["Win", "Lose", "Draw"],
            "Count": [win, lose, draw],
        }
    )
    fig = px.bar(df, x="Count", y="Result", color="Result")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
