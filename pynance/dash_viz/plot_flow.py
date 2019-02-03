import base64
import io

import dash
import flask

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from pynance.textimporter import read_csv, SupportedCsvTypes

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                server=server)


app.layout = html.Div([
    dcc.Upload(
        id='uploader',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '300px',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    dcc.Graph(
        figure=go.Figure(
            data=[],
            ),
        style={'height': 500},
        id='my-graph'
    )
])

def parse_contents(contents):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        csvtype = SupportedCsvTypes.DKBCash
        encoding = csvtype.encoding

        return read_csv(io.StringIO(decoded.decode(encoding)), csvtype)
    except:
        raise IOError("Could not load file.")

@app.callback(Output('my-graph', component_property='figure'),
              [Input('uploader', component_property='contents')])
def update_output(content):
    if content is not None:
        df = parse_contents(content)

        pos = df[df["amount"] > 0]
        neg = df[df["amount"] < 0]

        pos_bar = go.Bar(x=pos["date"],
                         y=pos["amount"],
                         text=pos["text"],
                         name="incoming")
        neg_bar = go.Bar(x=neg["date"],
                         y=neg["amount"],
                         text=neg["text"],
                         name="outgoing")

        fig = go.Figure(
            data=[pos_bar, neg_bar],
            layout=go.Layout(
                showlegend=True,
                legend=go.layout.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30)
            )
        )

        return fig
    else: return go.Figure(
            data=[],
            )

