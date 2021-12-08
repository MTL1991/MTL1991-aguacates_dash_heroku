import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, dcc, html


import krakenex
from datetime import datetime
import time
import pandas as pd
import json

def get_pairs_available():
    posibles_valores = k.query_public('AssetPairs',data="info=info")['result']
    human_name_list = []
    api_name_list = []
    for i in posibles_valores:
        human_name_list.append(posibles_valores[i]['wsname'])
        api_name_list.append(i)
    
    data = {'label':human_name_list,'value':api_name_list}
    return pd.DataFrame(data)

def get_df_ohlc(pair="XXBTZUSD",interval=1,start_time=time.mktime(datetime(2000, 1, 1,0,0,0).timetuple())):
    rt = k.query_public('OHLC',data="pair="+pair+"&interval="+str(interval)+"&since="+str(start_time))
    time_list=[]
    open_list=[]
    close_list=[]
    high_list=[]
    low_list=[]
    vwap_list=[]

    for row in rt['result'][pair]:
        #time = datetime.utcfromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S')
        time_list.append(datetime.utcfromtimestamp(row[0]).strftime('%Y-%m-%d %H:%M:%S'))
        open_list.append(float(row[1]))
        close_list.append(float(row[4]))
        high_list.append(float(row[2]))
        low_list.append(float(row[3]))
        vwap_list.append(float(row[5]))
        
    data = {'time_list':time_list,'open_list':open_list,'close_list':close_list,'high_list':high_list,'low_list':low_list,'vwap_list':vwap_list}
    return pd.DataFrame(data)

df_pairs = get_pairs_available()
result = df_pairs.to_json(orient="records")
parsed = json.loads(result)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Analisis criptomonedas"
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Cotización criptomonedas", className="header-title"
                ),
                html.P(
                    children="Grafico con la cotización de un par de monedas",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Par monedas", className="menu-title"),
                        dcc.Dropdown(
                            id='choose-pair',
                            options=parsed,
                            value='XBTUSDC',
                            clearable=False,
                            className="dropdown",
                        )
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Agrupación", className="menu-title"),
                        dcc.Dropdown(
                            id='choose-grouptime',
                            options=[
                                {'label': '1 minuto', 'value': 1},
                                {'label': '5 minutos', 'value': 5},
                                {'label': '15 minutos', 'value': 15},
                                {'label': '30 minutos', 'value': 30},
                                {'label': '1 hora', 'value': 60},
                                {'label': '4 hora', 'value': 240},
                                {'label': '1 dia', 'value': 1440},
                                {'label': '1 semana', 'value': 10080},
                                {'label': '15 dias', 'value': 21600},
                            ],
                            value=60,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="line-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    Output("line-chart", "figure"), 
    [Input("choose-pair", "value"),Input("choose-grouptime", "value")])
def update_line_chart(pair_to_call,interval_to_call):
    fig = go.Figure()
    if interval_to_call == None:
        interval_to_call=5
    if pair_to_call!=None:
        df = get_df_ohlc(pair=pair_to_call,interval=interval_to_call)
        velas = go.Candlestick(x=df.time_list,
                                open=df.open_list,
                                high=df.high_list,
                                low=df.low_list,
                                close=df.close_list,
                                xaxis="x",
                                yaxis="y",
                                name='cotizacion',
                                visible=True)
        linea = go.Scatter(
                x=df.time_list,
                y=df.vwap_list,
                mode='lines',
                name='vwap'

            )
        fig.add_trace(velas)
        fig.add_trace(linea)
        fig.update(layout_xaxis_rangeslider_visible=False)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)