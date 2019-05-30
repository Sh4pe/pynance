import base64
import io

import dash
import flask

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from pynance.textimporter import read_csv
from pynance.dkb import SupportedCsvTypes

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                server=server)

app.layout = html.Div([
    html.H2("Incoming and outcoming cash"),
    html.Table([
        html.Tr([
            html.Td(dcc.Dropdown(
                id='csvtype-selection',
                options=[{'label': 'DKB Cash', 'value': 'DKBCash'},
                         {'label': 'DKB Visa', 'value': 'DKBVisa'}
                         ],
                style={'width': 200},
                placeholder="Select csv type",
                value=None,
                searchable=False,
                clearable=False)),
            html.Td(dcc.Upload(
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
                multiple=False,

            ))
        ]),
    ]),
    dcc.Store(id='csvtype',
              storage_type='session'),

    dcc.Graph(
        figure=go.Figure(
            data=[],
        ),
        style={'height': 500},
        id='graph_bar'
    ),

    dcc.Graph(
        figure=go.Figure(
            data=[],
        ),
        style={'height': 500},
        id='graph_line'
    )
])


def parse_contents(contents, csvtype_str):
    """
    Format the undecoded content of a csv file to a dataframe

    Params:
    -------
    contents: byte like with header, base64 encoded
        Output from the upload component. The first is file type description,
        second part the undecoded content of the file
    csvtype_str: str
        name of a supported csv type, should be name of the attribute of
        SupportedCsvTypes

    Returns:
    --------
    DataFrame
        Data from the file, formatted as defined by CSV-Type
    """
    csvtype_desc = csvtype_string2description(csvtype_str)

    try:
        content_string = contents.split(',')[1]
        byte_decoded = base64.b64decode(content_string)

        encoding = csvtype_desc.encoding
        decoded = byte_decoded.decode(encoding)
    except:
        raise IOError("Could not decode file.")

    string_io = io.StringIO(decoded)
    return read_csv(string_io, csvtype_desc)


def make_cashflow_figure(df):
    """
    Take a transactions dataframe and make a figure out of it,
    which contains two bar charts: one with green bars for positive
    transactions, and one with red bars for negative transactions

    Params:
    -------
    df: pandas.Dataframe
        Dataframe which must have the columns date, amount and text

    Returns:
    --------
    plotly.graph_objs.Figure
        Figure with the visualized data
    """

    pos = df[df["amount"] >= 0]
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


def make_line_figure(df):
    """
    Take a transactions dataframe and make a figure out of it, which
    shows the total balance as a function of time

    Params:
    -------
    df: pandas.Dataframe
        Dataframe which must have the columns date and total_balance

    Returns:
    --------
    plotly.graph_objs.Figure
        Figure with the visualized data
    """

    lineplot = go.Scatter(x=df["date"],
                          y=df["total_balance"])

    fig = go.Figure(
        data=[lineplot]
    )
    return fig


@app.callback(Output('graph_bar', 'figure'),
              [Input('uploader', 'contents')],
              [State('csvtype', 'data')])
def update_bar_chart(content, csvtype_str):
    """
    Visualizes the raw data content of a file as a time-amount bar graph

    Params:
    -------
    content: byte-like
        undecoded csv file content
    csvtype_str: str
        name of a supported csv type, should be name of the attribute of
        SupportedCsvTypes

    Returns:
    --------
    Figure:
        Bar chart figure, with time on x and total balance on y
    """
    if content is not None:
        df = parse_contents(content, csvtype_str)
        return make_cashflow_figure(df)
    else:
        return go.Figure(data=[])


@app.callback(Output('graph_line', 'figure'),
              [Input('uploader', 'contents')],
              [State('csvtype', 'data')])
def update_line(content, csvtype_str):
    """
    Visualizes the raw data content of a file as a time-amount line graph

    Params:
    -------
    content: byte-like
        undecoded csv file content
    csvtype_str: str
        name of a supported csv type, should be name of the attribute of
        SupportedCsvTypes

    Returns:
    --------
    Figure:
        Line figure, with time on x and amount on y
    """
    if content is not None:
        df = parse_contents(content, csvtype_str)
        return make_line_figure(df)
    else:
        return go.Figure(data=[])


@app.callback(Output("uploader", "disabled"),
              [Input("csvtype-selection", "value")])
def onselect_csvtype(dropdown_value):
    """disable the uploader if no csvtype is selected"""
    return dropdown_value is None


@app.callback(Output("csvtype", "data"),
              [Input("csvtype-selection", "value")])
def update_csvtype_store(dropdown_value):
    """write the value of the csvtype selection to storage"""
    return dropdown_value


def csvtype_string2description(csvtype_string):
    """get the right csv type object from the list of supported its name"""
    return getattr(SupportedCsvTypes, csvtype_string)
