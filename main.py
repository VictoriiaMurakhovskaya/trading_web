import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from pars import getData
from ga_trade import use_ga

stocks = [{'label': 'Tesla', 'value': 'TSLA'},
          {'label': 'Amazon', 'value': 'AMZN'},
          {'label': 'Alphabet Inc.', 'value': 'GOOG'}]


fig, df = getData(stocks[0]['value'])


def navBar():
    navbar = dbc.NavbarSimple(
        children=[],
        brand="Технический анализ в трейдинге",
        brand_href="/",
        color='DodgerBlue',
        dark=True,
    )
    return navbar


def dashboard():
    layout = dbc.Container([
        dbc.Row([
            dbc.Col(id='params', children=[params()], md=3, width='auto'),
        dbc.Col(id='main-graph', children=[dcc.Graph(figure=fig,
                                                     config={'displayModeBar': False})],
                    md=8, width='auto', style={"border":"0.5px lightgrey solid", 'margin-left': '20px',
                                               'margin-right': '10px'})])
    ], style={'margin': '20px'}, fluid=True)
    return layout


def params():
    controls = dbc.Card(
        [
            dbc.FormGroup(
                [
                    dbc.Label(children=['Эмитент акций'], style={'margin-top': '10px', 'margin-left': '20px'}),
                    dcc.Dropdown(id='stock-name',
                                 placeholder='Выберите эмитента',
                                 options=stocks,
                                 value='TSLA',
                                 multi=False,
                                 searchable=False,
                                 style={'margin-left': '10px', 'margin-right': '30px'})
                ]
            ),
            dbc.FormGroup(
                [
                    dbc.Label(children=['Рекомендация'], style={'margin-top': '10px', 'margin-left': '20px'}),
                    dbc.Button(id='indicator', children=['---'], color='primary', className='mr1',
                               style={'margin-left': '10px', 'margin-right': '20px', 'width': '128px'}, outline=True,)
                ]
            )
        ]
    )
    return controls


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
app.layout = html.Div([dcc.Location(id='loc', refresh=True),
                       navBar(),
                       html.Div(id='page-content', children=[dashboard()]),
                       html.Div(id='dummy', hidden=True)
                       ])


@app.callback(
    [Output('main-graph', 'children'),
     Output('indicator', 'children'),
     Output('indicator', 'color')],
    Input('stock-name', 'value')
)
def plot_stock(value):
    global df
    fig, df = getData(value)
    flag = use_ga(df)
    if flag:
        return dcc.Graph(figure=fig, config={'displayModeBar': False}), 'Покупать','success'
    else:
        return dcc.Graph(figure=fig, config={'displayModeBar': False}), 'Продавать','danger'


if __name__ == '__main__':
    app.run_server(debug=False)

