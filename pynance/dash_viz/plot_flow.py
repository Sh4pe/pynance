import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from pynance.textimporter import read_csv

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id='my-id', value='initial value', type='text'),
    html.Div(id='my-div')
])

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)
def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)

