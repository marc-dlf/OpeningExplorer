# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from cairosvg import svg2png
import chess
import chess.svg
from dash import Dash, Input, Output, State, callback, ctx, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import pybase64

import src.config as config
from src.explorer.game_tree import GameTree

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Pre loading base board
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
                # Div with board and selectors
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
                                # Input player username to search
                                dcc.Input(
                                    id="playername", type="text", placeholder=""
                                ),
                                # Validate search
                                html.Button("Submit", id="submit-val", n_clicks=0),
                                # Select position among proposed
                                dcc.Dropdown(
                                    [str(i) for i in range(config.N_POSITIONS)],
                                    "0",
                                    id="position-index",
                                ),
                                # Select color
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
                # Position stats graph
                dcc.Graph(id="results-graph"),
            ],
            style={"display": "flex", "margin-bottom": "50px", "margin-top": "100px"},
        ),
        dcc.Loading(id="loading", children=html.Div(id="loading-output")),
        # dcc.Store stores the intermediate value
        dcc.Store(id="board-svg"),
        dcc.Store(id="positions"),
    ]
)


@callback(
    Output("positions", "data"),
    Output("loading-output", "children"),
    Input("submit-val", "n_clicks"),
    State("playername", "value"),
)
def on_click(n_clicks, value):
    if value is None:
        return None, ""
    gt = GameTree()
    gt.load_tree(value, 14, config.START_MONTH, config.END_MONTH)
    positions = gt.get_worse_k_positions(3, 10)
    return {
        "w": positions["w"].to_tuples(),
        "b": positions["b"].to_tuples(),
    }, ""


@callback(
    Output("board-svg", "data"),
    Output("opening", "children"),
    [
        Input("position-index", "value"),
        Input("positions", "data"),
        Input("color", "value"),
    ],
)
def load_board(index, positions, color):
    if positions is None or index is None:
        return f"data:image/png;base64,{BASE_IMG}", "Opening Name"
    else:
        colored_position = positions["w"] if color == "White" else positions["b"]
        fen, _, _, _, opening = colored_position[int(index)]
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
    Output("results-graph", "figure"),
    [
        Input("position-index", "value"),
        Input("positions", "data"),
        Input("color", "value"),
    ],
)
def update_bar_chart(index, positions, color):
    win, lose, draw = 0, 0, 0
    if positions is not None and index is not None:
        colored_pos = positions["w"] if color == "White" else positions["b"]
        current_pos = colored_pos[int(index)]
        _, win, lose, draw, _ = current_pos
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
