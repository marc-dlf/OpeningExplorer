"""Dash app with the Opening Explorer."""
from typing import Dict, Tuple

from cairosvg import svg2png
import chess
import chess.svg
import dash
from dash import Dash, Input, Output, State, callback, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure
import pybase64

from src import config
from src.explorer.game_tree import load_tree_multiproc
from src.explorer.game_tree import Result

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Pre loading base board.
BASE_BOARD = chess.Board()
BASE_SVG = chess.svg.board(BASE_BOARD, size=500)
BASE_IMG = pybase64.b64encode(svg2png(bytestring=BASE_SVG)).decode()

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Img(
                    src=dash.get_asset_url("logo.png"), style={"margin-right": "30px"}
                ),
                html.H1(
                    children="Opening Weaknesses Explorer",
                    style={"textAlign": "left", "margin-top": "15px"},
                ),
            ],
            style={
                "display": "flex",
                "flex-direction": "row",
                "margin-top": "30px",
                "border-bottom": "3px solid grey",
                "padding-bottom": "20px",
            },
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
                        html.Img(id="board", style={"margin-bottom": "20px"}),
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
                            style={"display": "flex"},
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
def on_click(_: int, value: str) -> Tuple[Dict[str, Result.T], str]:
    """
    Update the positions in the explorer when a new username is submited.

        Parameters:
            value (str) : Username for which we explore opening.

        Returns:
            positions : Dictionnary with positions to explore.
            loading (str) : Empty string for the loading component.
    """
    if value is None:
        return None, ""
    game_tree = load_tree_multiproc(
        config.N_PROCS, value, config.MAX_DEPTH, config.START_MONTH, config.END_MONTH
    )
    positions = game_tree.get_worse_k_positions(
        config.N_GAMES_THRESHOLD, config.N_POSITIONS
    )
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
def load_board(
    index: str, positions: Dict[str, Result.T], color: str
) -> Tuple[str, str]:
    """
    Load the board svg in Store and returns opening name to be displayed.

        Parameters:
            index (str) : The index for the position selected.
            positions (Dict[str, Result.T]) : Dictionnary with positions to explore.
            color (str) : Selected color.

        Returns:
            svg (str) : SVG image of the board.
            opening (str) : Opening name.
    """
    if positions is None or index is None:
        return f"data:image/png;base64,{BASE_IMG}", "Opening Name"
    colored_position = positions["w"] if color == "White" else positions["b"]
    fen, _, _, _, opening = colored_position[int(index)]
    board = chess.Board(fen)
    if color == "Black":
        board = board.transform(chess.flip_vertical).transform(chess.flip_horizontal)
    svg = chess.svg.board(board, size=500)
    img = pybase64.b64encode(svg2png(bytestring=svg)).decode()
    return f"data:image/png;base64,{img}", opening


@callback(Output("board", "src"), Input("board-svg", "data"))
def update_img(src_img: str) -> str:
    """
    Update the svg inside the Img component.

        Parameters:
            src_img (str) : SVG image of the board.

        Returns:
            src_img (str) : SVG image of the board.
    """
    return src_img


@callback(
    Output("results-graph", "figure"),
    [
        Input("position-index", "value"),
        Input("positions", "data"),
        Input("color", "value"),
    ],
)
def update_bar_chart(index: str, positions: Dict[str, Result.T], color: str) -> Figure:
    """
    Update the bar chart with position's statistics.

        Parameters:
            index (str) : The index for the position selected.
            positions (Dict[str, Result.T]) : Dictionnary with positions to explore.
            color (str) : Selected color.

        Returns:
            fig (Figure) : Bar chart with position's statistics.
    """
    win, lose, draw = 0, 0, 0
    if positions is not None and index is not None:
        colored_pos = positions["w"] if color == "White" else positions["b"]
        current_pos = colored_pos[int(index)]
        _, win, lose, draw, _ = current_pos
    result_df = pd.DataFrame(
        {
            "Result": ["Win", "Lose", "Draw"],
            "Count": [win, lose, draw],
        }
    )
    fig = px.bar(result_df, x="Count", y="Result", color="Result")
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
