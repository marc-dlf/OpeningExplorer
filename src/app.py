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
    positions = gt.get_worse_k_positions(True, 3, 10)
    positions = [
        (elt.id, elt.win_count, elt.lose_count, elt.draw_count) for elt in positions
    ]
    return positions, ""


@callback(
    Output("board-svg", "data"),
    [Input("dropdown", "value"), Input("player-examples", "data")],
)
def clean_data(value, examples):
    if examples is None or value is None:
        return f"data:image/png;base64,{BASE_IMG}"
    else:
        board = chess.Board(examples[int(value)][0])
        svg = chess.svg.board(board, size=500)
        img = pybase64.b64encode(svg2png(bytestring=svg)).decode()
        return f"data:image/png;base64,{img}"


@callback(Output("board", "src"), Input("board-svg", "data"))
def update_img(src_img):
    return src_img


@callback(
    Output("graph", "figure"),
    [Input("dropdown", "value"), Input("player-examples", "data")],
)
def update_bar_chart(value, examples):
    win, lose, draw = 0, 0, 0
    if examples is not None and value is not None:
        ex = examples[int(value)]
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
