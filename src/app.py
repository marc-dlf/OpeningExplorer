# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import chess
import chess.svg
from cairosvg import svg2png
import pybase64

app = Dash(__name__)

board = chess.Board()
svg = chess.svg.board(board, size=400)
img = pybase64.b64encode(svg2png(bytestring=svg)).decode()

app.layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        html.Div(
            children="""
        Dash: A web application framework for your data.
    """
        ),
        html.Img(src="data:image/png;base64,{}".format(img)),
        # html.Div(children=img),
        # html.Iframe(src=svg),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
