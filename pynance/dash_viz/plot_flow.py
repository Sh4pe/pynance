import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import base64
import io

from pynance.textimporter import read_csv, SupportedCsvTypes

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    try:
        if 'csv' in filename:
            decoded = base64.b64decode(content_string)
            
            csvtype = SupportedCsvTypes.DKBCash
            encoding = csvtype.encoding

            print(decoded[:500])

            df = read_csv(io.StringIO(decoded.decode(encoding)), csvtype)
            print(df.columns)

            return html.Div([
                    dash_table.DataTable(
                        data=df.to_dict('rows'),
                        columns=[{'name': i, 'id': i} for i in df.columns]
                    )
                ])
        else:
            return html.Div([
                            'Unsupported file extension'
                            ])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])   


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(content, name, date):
    if content is not None:
        return parse_contents(content, name, date)
