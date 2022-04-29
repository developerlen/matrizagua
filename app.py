import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import copy
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import json
import math
import numpy as np
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import openpyxl
import psycopg2
from plotly.subplots import make_subplots
from calendar import isleap

ctx = dash.callback_context

mapbox_access_token = 'pk.eyJ1IjoiZm1hY2VkbyIsImEiOiJjanp0a3FlZzEwNXdyM2hteDRmOTNsZDI3In0.UMzEBHFVDraOT5AkHcbe7A'

# family_generico = "'Abel', sans-serif"
family_generico = "'Questrial', sans-serif"
size_generico = 15
cl_scale_blues = [[0, '#c6dbf7'], [1, '#165bb8']]


layout = dict(
    font=dict(
        size=size_generico,
        family=family_generico,
    ),
    hovermode="closest",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    hoverlabel=dict(font=dict(size=size_generico, family=family_generico))
)

unidade = "m\u00b3"
unidade_1 = "M m\u00b3"

unidade_2 = "x10\u00b3 m\u00b3"

file_path_freg = "data/Freguesias_agua_potavel.xlsx"
# file_path_freg_dom = 'data/Freguesias_domestico_agua_potavel.xlsx'
file_path_sector = "data/sector.xlsx"
file_path_freg_center = 'data/freguesias_centro.csv'
file_path_ndom = "data/nao_domestico.xlsx"
# file_path_balanco_geral = "data/Balanco_geral.xlsx"
file_path_balanco_potavel = "data/Balanco_potavel.xlsx"
file_path_bal_potavel_ts = "data/bal_potavel_ts.xlsx"
file_path_ar = "data/aguas_residuais.xlsx"
file_path_ar_centro = "data/ar_centro.xlsx"
file_path_ar_reu = "data/ar_reutilizadas.xlsx"

df_fregs = pd.read_excel(file_path_freg)
# df_fregs_dom = pd.read_excel(file_path_freg_dom)

freg_center = pd.read_csv(file_path_freg_center, encoding='utf-8')
sector_df = pd.read_excel(file_path_sector, index_col='Ano')
ndom_df = pd.read_excel(file_path_ndom, index_col='Ano')
bal_potavel_df = pd.read_excel(file_path_balanco_potavel, index_col='Ano')
bal_pot_ts_df = pd.read_excel(file_path_bal_potavel_ts, index_col='Ano')
aguas_r_df = pd.read_excel(file_path_ar, index_col='Ano')
ar_centro_df = pd.read_excel(file_path_ar_centro)
ar_reu_df = pd.read_excel(file_path_ar_reu, index_col='Ano')
perc_ndom = ((ndom_df['Total'] / 1000) / (sector_df['Total'] - sector_df['Perdas económicas'])) * 100
anos_cons = sector_df.index.unique().tolist()
anos_ar = aguas_r_df.index.unique().tolist()
anos_bal = bal_potavel_df.index.unique().tolist()

populacao = pd.Series(
    [563149, 550934, 549998, 548422, 537412, 524282, 511667, 513064, 506892, 504718, 505526, 506654, 509515],
    index=[2001, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019],
)

max_sector_total = math.ceil(sector_df.iloc[:, :-1].max().max() / 1000)
size_small = 192
color_live = ["#8DD3C7", "#fff069", "#BEBADA", "#FB8072", "#80B1D3", "#FDB462", "#B3DE69", "#f032e6", "#000075",
              "#4a915f", "#ffe119"]
color_dead = ["#96ebde", "#f7efa6", "#c1bae8", "#f0ada5", "#a7d0eb", "#f0c595", "#d4f0a3", "#e691e0", "#9595e8",
              "#90e8ab", "#f0e79e"]

color_sector_live_d = {"Doméstico": color_live[0],
                       "Comércio e Indústria": color_live[1],
                       "Instituições": color_live[2],
                       "Estado e embaixadas": color_live[3],
                       "Câmara Municipal de Lisboa": color_live[4],
                       "Delegações CML": color_live[5],
                       "Perdas económicas": color_live[6],
                       "Total": "#8F9090",
                       "Doméstico Per Capita": color_live[7]
                       }

color_sector_dead_d = {"Doméstico": color_dead[0],
                       "Comércio e Indústria": color_dead[1],
                       "Instituições": color_dead[2],
                       "Estado e embaixadas": color_dead[3],
                       "Câmara Municipal de Lisboa": color_dead[4],
                       "Delegações CML": color_dead[5],
                       "Perdas económicas": color_dead[6],
                       "Total": "#8F9090",
                       "Doméstico Per Capita": color_dead[7]
                       }

color_ndom_live_d = {
    "CML  + Delegações CML": color_live[0],
    "Restauração e Hotelaria": color_live[1],
    "Saúde": color_live[2],
    "Escritórios": color_live[3],
    "Instituições/Organ.Públicos/Instit. Militares": color_live[4],
    "Cultura, Lazer e Recreio": color_live[5],
    "Estabelecimentos e Centros Comerciais": color_live[6],
    "Ensino (Escolas/Universidades)": color_live[7],
    "Consumo Habitacional": color_live[8],
    "Outros": color_live[9],
    "Total": "#8F9090"

}

color_ndom_dead_d = {
    "CML  + Delegações CML": color_dead[0],
    "Restauração e Hotelaria": color_dead[1],
    "Saúde": color_dead[2],
    "Escritórios": color_dead[3],
    "Instituições/Organ.Públicos/Instit. Militares": color_dead[4],
    "Cultura, Lazer e Recreio": color_dead[5],
    "Estabelecimentos e Centros Comerciais": color_dead[6],
    "Ensino (Escolas/Universidades)": color_dead[7],
    "Consumo Habitacional": color_dead[8],
    "Outros": color_dead[9],
    "Total": "#8F9090"

}

color_balanco_live_d = {"Água utilizada em Lisboa": color_live[0],
                        "Água consumida em Lisboa": color_live[1],
                        "Perdas económicas": color_live[2],
                        "Perdas reais": color_live[3],
                        "Entrega a outros municípios": color_live[4],
                        "Água para consumo humano": color_live[5],
                        }

color_balanco_dead_d = {"Água utilizada em Lisboa": color_dead[0],
                        "Água consumida em Lisboa": color_dead[1],
                        "Perdas económicas": color_dead[2],
                        "Perdas reais": color_dead[3],
                        "Entrega a outros municípios": color_dead[4],
                        "Água para consumo humano": color_dead[5],
                        }

color_ar_live_d = {
    "Alcântara": color_live[0],
    "Beirolas": color_live[7],
    "Chelas": color_live[2],
    "Total - Água Tratada": "#8F9090",
    "Água reutilizada internamente pela AdTA": color_live[6],
    "Água reutilizada pela CML e JF": color_live[8],
    "Total - Água Reutilizada": "#8F9090",
}

color_ar_dead_d = {
    "Alcântara": color_dead[0],
    "Beirolas": color_dead[7],
    "Chelas": color_dead[2],
    "Total - Água Tratada": "#8F9090",
    "Água reutilizada internamente pela AdTA": color_dead[6],
    "Água reutilizada pela CML e JF": color_dead[8],
    "Total - Água Reutilizada": "#8F9090",
}

sector_options = [{'label': sect,
                   'value': str(sect_val)}
                  for sect, sect_val in zip(sector_df.columns.to_list(), sector_df.columns.to_list())]
sector_options = sector_options + [{'label': 'Doméstico Per Capita', 'value': 'Doméstico Per Capita'}]
sector_options = sorted(sector_options, key=lambda k: k['label'])

ndom_options = [{'label': sect,
                 'value': str(sect_val)}
                for sect, sect_val in zip(ndom_df.columns.to_list(), ndom_df.columns.to_list())]

bal_pot_options = [{'label': sect,
                    'value': str(sect_val)}
                   for sect, sect_val in zip(list(bal_potavel_df.Ordem.unique()), list(bal_potavel_df.Ordem.unique()))]

ar_labels = [
    "Alcântara - Água Tratada", "Beirolas - Água Tratada", "Chelas - Água Tratada", "Total - Água Tratada",
    "Total - Água Reutilizada", 'Água reutilizada internamente pela AdTA', 'Água reutilizada pela CML e JF']
ar_values = list(aguas_r_df.Subsistema.unique()) + list(ar_reu_df.Subsistema.unique())
ar_options = [{'label': sect,
               'value': str(sect_val)}
              for sect, sect_val in zip(ar_labels, ar_values)]

ar_totais = pd.concat([aguas_r_df.drop(['Lisboa', 'Outros Concelhos', 'lis_perc', 'out_perc'], axis=1), ar_reu_df])
ar_totais.sort_index(inplace=True)

with open("data/Freguesias2012/Freguesias2012") as geofile:
    freguesias_jsn = json.load(geofile)
i = 1
for freg in freguesias_jsn["features"]:
    freg['id'] = str(i).zfill(2)
    i += 1

freg_center['id'] = [str(a + 1).zfill(2) for a in freg_center.index]

TITLE_STYLE = {'textAlign': 'center', 'font-family': family_generico}
INSTRUCTION_STYLE_center = {'textAlign': "center", 'font-family': family_generico, 'font-style': 'italic'}
INSTRUCTION_STYLE_right = {'textAlign': "right", 'font-family': family_generico, 'font-style': 'italic'}
INSTRUCTION_STYLE_left_cons = {'textAlign': "left", 'font-family': family_generico, 'font-style': 'italic',
                               'margin-left': '19%', 'position': 'relative'}
INSTRUCTION_STYLE_left = {'textAlign': "left", 'font-family': family_generico, 'font-style': 'italic'}

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,

                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ],
                )
# para prevenir erros
app.config['suppress_callback_exceptions'] = True
server = app.server
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# app.server.config['SECRET_KEY'] = '60b69ea75d65bfc586c4e778a9357219'
# app.server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# HEROKU - FALTA ADAPTAR ESTES VALORES
app.server.config['SECRET_KEY'] = '60b69ea75d65bfc586c4e778a9357219'
app.server.config[
    'SQLALCHEMY_DATABASE_URI'] = 'postgres://yibvjryninkbcv:28fce500a912b4a78e6277719ed598082c19543ca5a1c394d235e3fe79f641e9@ec2-54-247-171-30.eu-west-1.compute.amazonaws.com:5432/d2719tk9ncf4kl'

app.server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app.server)


class Pessoas(db.Model):
    __tablename__ = "registo"
    id = db.Column(db.Integer, primary_key=True)
    consumo = db.Column(db.String(20))
    freguesias = db.Column(db.String(20))
    aguasresiduais = db.Column(db.String(20))
    balanco = db.Column(db.String(20))

    def __repr__(self):
        return f"pessoas('{self.consumo}', '{self.freguesias}', '{self.aguasresiduais}', '{self.balanco}')"


# radioitems_modal = dbc.FormGroup(
#     [
#
#     ]
# )

# dwnld_btn = html.Div([
#
# ])

nomes = ['consumo', 'freg', 'ar', 'bal']
headers = ['Consumo de Água Potável', 'Consumo de Água Potável por Freguesia', 'Águas Residuais', 'Balanço de Água']
id_m = ['modal-consumo', 'modal-freg', 'modal-ar', 'modal-bal']
id_l = ['link-file-consumo', 'link-file-freg', 'link-file-ar', 'link-file-bal']
id_c = ['close-consumo', 'close-freg', 'close-ar', 'close-bal']
id_d = ['download-consumo', 'download-freg', 'download-ar', 'download-bal']
id_r = ['radio-consumo', 'radio-freg', 'radio-ar', 'radio-bal']
id_t = ['target-consumo', 'target-freg', 'target-ar', 'target-bal']
links = ['/download/Consumo_AguaPotavel.xlsx', '/download/Consumo_Freguesias.xlsx',
         '/download/Aguas_Residuais_e_Reutilizadas.xlsx', '/download/Balanco_Agua_Potavel.xlsx']
divs = ['hidden-consumo', 'hidden-freg', 'hidden-ar', 'hidden-bal']

ids_modal = {nom: {
    'header': h,
    'id_m': m,
    'id_l': l,
    'id_c': c,
    'id_d': d,
    'id_r': r,
    'id_t': t,
    'link': l2,
    'div': div

} for nom, h, m, l, c, d, r, t, l2, div in zip(nomes, headers, id_m, id_l, id_c, id_d, id_r, id_t, links, divs)}


def create_year_button(ano, tab, anos, classe):
    tamanho = 100 / len(anos)
    if tamanho < 7:
        tamanho = tamanho * 2
    butao = dbc.Button(ano, color='primary', outline=True, id='sel_{0}_{1}'.format(ano, tab), className=classe)

    return butao


def create_year_button_last(ano, tab, anos, classe):
    tamanho = 100 / len(anos)
    if tamanho < 7:
        tamanho = tamanho * 2
    butao = dbc.Button(ano, color='primary', outline=False, id='sel_{0}_{1}'.format(ano, tab), className=classe)

    return butao


def create_modal(tab):
    header = ids_modal[tab]['header']
    id_m = ids_modal[tab]['id_m']
    id_l = ids_modal[tab]['id_l']
    id_c = ids_modal[tab]['id_c']
    id_d = ids_modal[tab]['id_d']
    id_r = ids_modal[tab]['id_r']
    link = ids_modal[tab]['link']
    div = ids_modal[tab]['div']
    return html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader("DOWNLOAD DE FICHEIROS - {}".format(header)),
                    dbc.ModalBody(["Qual o propósito deste download?",
                                   dcc.RadioItems(
                                       options=[
                                           {"label": "Pessoal", "value": 1},
                                           {"label": "Profissional", "value": 2},
                                           {"label": "Académico", "value": 3},
                                       ],
                                       # value=1,
                                       id=id_r,
                                   ),
                                   html.Div(id=div, style={'display': 'none'})

                                   ]),

                    dbc.ModalFooter(

                        [
                            html.A(
                                children=dbc.Button("Download", id=id_d, className="ml-auto", color="primary",
                                                    size="lg",
                                                    disabled=True),
                                href=link,
                                id=id_l
                            ),
                            dbc.Button(
                                "Close", id=id_c, className="m1-auto", size="lg", color="danger"
                            )]
                    ),
                ],
                id=id_m,
                centered=True,
                style={'font-family': family_generico}
            ),
        ], style={'font-family': family_generico},
    )


modal_cons = create_modal('consumo')
modal_freg = create_modal('freg')

modal_ar = create_modal('ar')
modal_bal = create_modal('bal')

collapse_side_cons = html.Div(
    [
        dbc.Button(
            "+ Info",
            id="collapse-btn-cons",
            size="lg",
            # className="mb-3",
            # outline=True,
            color="link",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(
                dcc.Markdown('''
                _O consumo anual apresentado inclui também as **perdas económicas** (ou aparentes)._ 


                '''),
                id='info-cons'),
                # style= {'font-style': 'italic'}
            ),
            id="collapse-cons",
        ),
    ], style={'font-family': family_generico, 'margin-bottom': '2%'},
)
pop_radio = html.Div(dcc.RadioItems(
    options=[
        {"label": "Total", "value": 1},
        {"label": "Per Capita", "value": 2},
    ],
    value=1,
    labelStyle={'display': 'inline-block', 'margin-left': '4%', 'margin-top': '4%'},
    id="radio-pop",
), style={'textAlign': "center", 'font-family': family_generico})

side_bar_cons = html.Div(
    [
        pop_radio,
        html.Hr(className='blurb2'),
        html.H6('Consumo Total Anual de Água, em Lisboa ({})'.format(unidade),
                style=TITLE_STYLE, id='head-ano-bar-cons'),
        html.P(dcc.Markdown('''**Seleccione o ano pretendido:**'''), style=INSTRUCTION_STYLE_center),

        html.Div(
            [create_year_button(ano, 'cons', anos_cons, 'bt-cons') for ano in anos_cons[:-1]] + [
                create_year_button_last(anos_cons[-1], 'cons', anos_cons, 'bt-cons')],
            # style={'textAlign': "center", "margin-left": "1rem", "margin-right": "1rem", "padding": "1rem 1r1em"}
        ),
        html.Div(id='mem-year-cons', style={'display': 'none'}),
        dcc.Loading(type="circle",
                    style={'margin': '30%'},

                    children=dcc.Graph(id="ano-bar-graph", config={'displayModeBar': False}), ),
        # html.Div([dcc.Slider(
        #     id='year-slider',
        #     min=sector_df.index.min(),
        #     max=sector_df.index.max(),
        #     value=sector_df.index.max(),
        #     marks={
        #         str(ano): {'label': '', 'style': {'writingMode': 'vertical-rl', 'textOrientation': 'mixed'}}
        #         for ano in sector_df.index.unique()
        #     },
        #     step=None,
        # )], style={'textAlign': "center", "margin-left": "7%", "margin-right": "5%", "padding": "2% 2%"}),
        # html.Hr(),
        collapse_side_cons
    ]
)

side_bar_bal = html.Div(
    [
        dbc.Row(html.H6('Consumo Total Anual de Água, em Lisboa ({})'.format(unidade),
                        style=TITLE_STYLE), align="center", justify="center"),
        html.P(dcc.Markdown('''**Seleccione o ano pretendido:**'''), style=INSTRUCTION_STYLE_center),
        html.Div(
            [create_year_button(ano, 'bal', anos_bal, 'bt-bal') for ano in anos_bal[:-1]] + [
                create_year_button_last(anos_bal[-1], 'bal', anos_bal, 'bt-bal')],
            # style={'textAlign': "center", "margin-left": "1rem", "margin-right": "1rem", "padding": "1rem 1rem"}
        ),
        html.Div(id='mem-year-bal', style={'display': 'none'}),

        dcc.Loading(type="circle",
                    style={'margin': '20%'},
                    children=dcc.Graph(id="ano-bar-graph-bal", config={'displayModeBar': False})
                    ),
        # html.Div([dcc.Slider(
        #     id='year-slider-bal',
        #     min=bal_potavel_df.index.min(),
        #     max=bal_potavel_df.index.max(),
        #     value=bal_potavel_df.index.max(),
        #     marks={
        #         str(ano): {'label': '', 'style': {'writingMode': 'vertical-rl', 'textOrientation': 'mixed'}}
        #         for ano in bal_potavel_df.index.unique()
        #     },
        #     step=None,
        # )], style={'textAlign': "center", "margin-left": "2.5%", "margin-right": "2.5%", "padding": "2% 2%"})
    ])

side_bar_ar = html.Div(
    [

        dbc.Row(html.H6('Total Anual de Água Residual Tratada, em Lisboa ({})'.format(unidade),
                        style=TITLE_STYLE), align="center", justify="center"),
        html.P(dcc.Markdown('''**Seleccione o ano pretendido:**'''), style=INSTRUCTION_STYLE_center),
        html.Div(
            [create_year_button(ano, 'ar', anos_ar, 'bt-ar') for ano in anos_ar[:-1]] + [
                create_year_button_last(anos_ar[-1], 'ar', anos_ar, 'bt-ar')],
            # style={'textAlign': "center", "margin-left": "1rem", "margin-right": "1rem", "padding": "1rem 1rem"}
        ),
        html.Div(id='mem-year-ar', style={'display': 'none'}),

        dcc.Loading(type="circle",
                    style={'margin': '30%'},
                    children=dcc.Graph(id="ano-bar-graph-ar", config={'displayModeBar': False})),
        # html.Div([dcc.Slider(
        #     id='year-slider-ar',
        #     min=aguas_r_df.index.min(),
        #     max=aguas_r_df.index.max(),
        #     value=aguas_r_df.index.max(),
        #     marks={str(ano): {'label': '', 'style': {'writingMode': 'vertical-rl', 'textOrientation': 'mixed'}} for ano in aguas_r_df.index.unique()},
        #     step=None,
        # )], style={'textAlign': "center", "margin-left": "0.3%", "margin-right": "1.3%", "padding": "2% 2%"})
    ]
)

collapse_freg = html.Div(
    [
        dbc.Button(
            "+ Info",
            id="collapse-btn-freg",
            size="lg",
            # className="mb-3",
            # outline=True,
            color="link",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(
                id='info-freg'),
                # style= {'font-style': 'italic'}
            ),
            id="collapse-freg",
        ),
    ], style={'font-family': family_generico, 'margin-bottom': '2%'},
)

download_button_freg = html.Div(
    [
        html.A(
            children=html.I(
                className="fas fa-file-download fa-lg",
                id="target-freg",
            ),
            href="javascript:void(0);",
            id='link-dummy'
        ),
        dbc.Tooltip(
            "Download dos Consumos de água potável (doméstico e total), número de contadores e número de smartmeters, por freguesia (.xlsx).",
            target="target-freg", style={'font-size': '1.4rem'}),
    ],
    className="p-3 text-muted")

freg_container = html.Div([
    dbc.Row([
        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),
        dbc.Col([
            html.Div([dbc.Row([html.H6(id="header-freg", style=TITLE_STYLE), download_button_freg], align="center",
                              justify="center", no_gutters=True)], id='freg-title-geral'),
            dbc.Alert(
                color="danger",
                id='alert-map',
                is_open=False,
                style={'textAlign': 'center', 'font-family': family_generico}
            ),
        ], lg=7, align='center'),
        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),
    ], justify='center'),

    html.Div([dbc.Row([
        dbc.Col([
            html.P(dcc.Markdown('''**Filtrar por Freguesia:**'''), style=INSTRUCTION_STYLE_center),
            dcc.Dropdown(
                id='drop-freg',
                options=[
                    {'label': 'Consumo Total de Água Potável', 'value': 'consumo_total'},
                    {'label': 'Consumo Doméstico de Água Potável', 'value': 'consumo_dom'},
                    {'label': 'Contadores', 'value': 'contadores'},
                    {'label': 'Smartmeters', 'value': 'smartmeters'}],
                value='consumo_total',
                clearable=False,
                style={'font-family': family_generico, 'margin-bottom': '2%'}
            ),
        ], lg=6)
    ], justify='center'),
    ], id="drop-freg-container"),
    dbc.Row(
        [

            dbc.Col([
                dbc.Row(
                    dbc.Col(
                        html.Div(

                            dcc.Loading(type="circle",
                                        style={'margin-left': '0%', 'margin-top': '20%'},
                                        children=dcc.Graph(id='mapa-freguesias', config={'displayModeBar': False})
                                        ), id="map-freg-container")
                    ), justify='center'
                )
            ], xl=6),

            dbc.Col([

                html.Div(

                    dcc.Loading(type="circle",
                                style={'margin-left': '0%', 'margin-top': '20%'},
                                children=dcc.Graph(id='bar-freguesias', config={'displayModeBar': False})
                                ), id="bar-freg-container"

                )

            ], xl=6
            ),
        ], align="center", justify="center"
    ),
    collapse_freg
], className='pretty_container twelve columns', style={"padding": "0% 1% 1% 1%", 'margin': '0'})

collapse_donut = html.Div(
    [
        dbc.Button(
            "+ Info",
            id="collapse-btn-donut",
            size="lg",
            # className="mb-3",
            # outline=True,
            color="link",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(id='info-donut'),
                     # style= {'font-style': 'italic'}
                     ),
            id="collapse-donut",
        ),
    ], style={'font-family': family_generico, 'margin-bottom': '2%'},
)
donut_container = html.Div(
    [
        # , tanks
        html.H6(id="header-donut", style=TITLE_STYLE),

        dcc.Loading(type="circle",
                    style={'margin': '30%'},
                    children=dcc.Graph(id='donut-sector', config={'displayModeBar': False})),
        collapse_donut,

    ],
)

info_button_consumo = html.Div(
    [
        html.I(className="fas fa-question-circle fa-sm", id="target"),
        dbc.Tooltip(
            "O consumo de água potável em Lisboa pode ser desagregado de várias formas. Nesta matriz, apresenta-se o consumo de água potável por sector de consumo e por consumo não doméstico.",
            target="target", style={'font-size': '1.4rem'}),
    ],
    className="p-2 text-muted"
)

ano_line_container = html.Div(
    [
        dbc.Row([
            html.H6(id="header-ano-line", style=TITLE_STYLE)

        ], align="center", justify="center", no_gutters=True),
        dbc.Row([

            dbc.Col(id="sector-tipo-inst",
                    style=INSTRUCTION_STYLE_center, width=12, align="start"),
            # dbc.Col(dcc.Markdown('''**Personalizar:**'''),
            #         style=INSTRUCTION_STYLE_center, width=6, align="start")

        ], justify='center', style={'margin-bottom': '2%'}),
        dbc.Row([
            dbc.Col(
                dcc.RadioItems(
                    options=[
                        {"label": "Todos", "value": "Todos"},
                        {"label": "Personalizado", "value": "Personalizado"},
                        {"label": "Total", "value": "Total"},
                    ],
                    value="Personalizado",
                    id="radio-ano-line",
                    labelStyle={'display': 'inline-block', 'margin-left': '4%'},

                ),
                md=6, align="center", style={'textAlign': "center", 'font-family': family_generico}

            ),
            dbc.Col(
                dcc.Dropdown(
                    value="Doméstico",
                    id='drop-ano-line',
                    clearable=False,
                    multi=True,
                    style={'font-family': family_generico}
                ), md=6, align="center"

            ),
        ], justify='center'),

        dcc.Loading(type="circle",
                    style={'margin-left': '0%', 'margin-top': '12%'},
                    children=dcc.Graph(id='ano-line-graph', config={'displayModeBar': False}))
    ],
)

download_button_consumo = html.Div(
    [
        html.A(
            children=html.I(
                className="fas fa-file-download fa-lg",
                id="target-consumo",
            ),
            href='javascript:void(0);',
            id='link-dummy'
        ),
        dbc.Tooltip(
            "Download do Consumo de água potável, por sector e por consumo não doméstico (.xlsx).",
            target="target-consumo", style={'font-size': '1.4rem'}),
    ],

    className="p-2 text-muted")

header_consumo = html.Div([
    dbc.Row([
        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),
        dbc.Col(dbc.Row([html.H6("Consumo de Água Potável",
                                 style={'textAlign': 'Center', 'font-family': family_generico}),
                         info_button_consumo, download_button_consumo], align="center", justify="center",
                        no_gutters=True), md=5, align="center"),
        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),

    ], justify="center"),

    dbc.Row([
        # dbc.Col([html.Div(className='vl', style={'height': 'inherit'})]),
        dbc.Col([
            html.P(dcc.Markdown('''**Seleccione a desagregação pretendida:**'''), style=INSTRUCTION_STYLE_center),
            dcc.Dropdown(
                id='drop-cons',
                options=[
                    {'label': 'Consumo por Sector', 'value': 'consumo_sector'},
                    {'label': 'Consumo não Doméstico', 'value': 'ndom'},
                ],
                value='consumo_sector',
                clearable=False,
                style={'font-family': family_generico}
            ),
        ], md=6, align='center'),
        # dbc.Col([html.Div(className='vl', style={'height': 'inherit'})]),
    ], justify='center'),

])

tab_consumo = html.Div(
    [
        dbc.Row([

            dbc.Col(side_bar_cons,

                    className='pretty_container sidebar'),

            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col([

                                dbc.Row([

                                    dbc.Col(
                                        header_consumo
                                    )

                                ]),

                                dbc.Row([
                                    dbc.Col(donut_container, xl=6),
                                    dbc.Col(ano_line_container, xl=6)
                                ])
                            ], lg=12, align='center')

                        ], className='pretty_container'),
                    dbc.Row([freg_container])
                ], xl=10, md=8, className='cons-m'
            )
        ]),
        modal_cons,
        modal_freg,
        html.Div(html.P('Dados disponibilizados pela EPAL e pela Águas do Tejo Atlântico (ADTA).',
                        style=INSTRUCTION_STYLE_left_cons))

    ], style={'margin-top': '0.8%'}
)

collapse_bal = html.Div(
    [
        dbc.Button(
            "+ Info",
            id="collapse-btn-bal",
            size="lg",
            # className="mb-3",
            # outline=True,
            color="link",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(
                dcc.Markdown('''
                _De toda a água potável que entra na cidade de Lisboa (Água para consumo humano) parte é entregue a outros municípios e a restante é utilizida na capital._ 

                _Da água utilizada na cidade, existem dois tipos de perdas principais:_
                * _**Perdas físicas ou reais**: traduzem a água realmente perdida na sequência de fugas e/ou roturas na rede de distribuição; _
                * _**Perdas aparentes ou económicas**: resultantes de consumos não autorizados, fornecimentos não medidos e erros de medição. _                
                '''),
                id='info-bal'),
                # style= {'font-style': 'italic'}
            ),
            id="collapse-bal",
        ),
    ], style={'font-family': family_generico, 'margin-bottom': '2%'},
)

download_button_balanco = html.Div(
    [
        html.A(
            children=html.I(
                className="fas fa-file-download fa-lg",
                id="target-bal",
            ),
            href='javascript:void(0);',
            id='link-dummy'
        ),
        dbc.Tooltip(
            "Download do balanço de água potável em Lisboa (.xlsx).",
            target="target-bal", style={'font-size': '1.4rem'}),
    ],

    className="p-3 text-muted")

bal_container = html.Div([

    dbc.Row(
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),

                        dbc.Col(dbc.Row([html.H6(id='bal-header', style=TITLE_STYLE), download_button_balanco],
                                        align='center', justify='center', no_gutters=True), lg=6, align='center'),
                        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),

                    ], align="center", justify="center"),

                dcc.Loading(type="circle",
                            style={'margin': '20%'},
                            children=dcc.Graph(
                                figure={'layout': {'autosize': True}}, id='bal-potavel',
                                hoverData={'points': [
                                    {'group': False, 'pointNumber': 5, 'label': 'Água para consumo humano: 93.5',
                                     'color': '#ccbbaf',
                                     'index': 5, 'value': 93.5, 'depth': 0, 'height': 3, 'x0': 0, 'x1': 30,
                                     'y0': 2.433608869978343e-13,
                                     'y1': 270, 'originalX': 15, 'originalY': 135.0000000000001,
                                     'originalLayerIndex': 0,
                                     'originalLayer': 0, 'dx': 30, 'dy': 269.9999999999998, 'curveNumber': 0}]},
                                config={'displayModeBar': False},
                                # style={'width': 1000}
                            )
                            ),
                collapse_bal,

                html.Hr()
            ]
        )
    ),
    dbc.Row(
        dbc.Col(
            [
                dbc.Row(
                    [
                        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),

                        dbc.Col(html.H6('Variação Anual dos Diferentes Fluxos de Água', style=TITLE_STYLE), lg=6,
                                align='center'),

                        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),

                    ], justify="center"),

                dbc.Row([
                    dbc.Col(dcc.Markdown('''**Filtrar por fluxo de água:**'''), lg=2, align="center",
                            style={'font-family': family_generico, 'font-style': 'italic'}, className='textbl'),
                    dbc.Col(
                        dcc.RadioItems(
                            options=[
                                {"label": "Todos", "value": "Todos"},
                                {"label": "Personalizado", "value": "Personalizado"},
                                # {"label": "Total", "value": "Total", 'disabled': True},
                            ],
                            value="Personalizado",
                            id="radio-bal-anual",
                            labelStyle={'display': 'inline-block', 'margin-left': '4%'},
                            # inline=True,
                            # switch=True,

                        ),
                        lg=3, align="center", style={'textAlign': "center", 'font-family': family_generico}

                    ),
                    dbc.Col(
                        dcc.Dropdown(

                            value=["Entrega a outros municípios"],
                            id='drop-bal',
                            clearable=False,
                            multi=True,
                            style={'font-family': family_generico}
                        ), lg=6
                    ),
                ], justify='center', align="start", no_gutters=True),
                dcc.Graph(id='bal-timeseries', config={'displayModeBar': False})]
        )
    ),

])
tab_balanco = html.Div([
    dbc.Row([
        dbc.Col(html.Div(side_bar_bal, style={'textAlign': 'center'}), className='pretty_container', md=3,
                style={'textAlign': 'left', 'margin-left': '0.8%'}),
        dbc.Col(bal_container, className='pretty_container eight columns',
                style={"padding": "0% 1% 1% 1%", "margin-left": "1%"})
    ], justify='start'), modal_bal,
    html.Div(html.P('Dados disponibilizados pela EPAL e pela Águas do Tejo Atlântico (ADTA).',
                    style=INSTRUCTION_STYLE_left))
], style={'margin-top': '0.8%'})

collapse_ar = html.Div(
    [
        dbc.Button(
            "+ Info",
            id="collapse-btn-ar",
            size="lg",
            # className="mb-3",
            # outline=True,
            color="link",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(

                id='info-ar'),
                # style= {'font-style': 'italic'}
            ),
            id="collapse-ar",
        ),
    ], style={'font-family': family_generico, 'margin-bottom': '2%'},
)
info_button_ar = html.Div(
    [
        html.I(className="fas fa-question-circle fa-sm", id="target_ar"),
        dbc.Tooltip(
            "A água residual do Concelho de Lisboa é tratada pelos Subsistemas de Alcântara, Beirolas, Chelas e Frielas. "
            "Estas estações recebem também afluentes provenientes de outros concelhos vizinhos (Amadora, Loures, Odivelas, Oeiras, Sintra e Vila Franca de Xira). "
            "Não se apresenta aqui a ETAR de Frielas pois esta não faz parte do Concelho de Lisboa.",
            target="target_ar",
            style={'font-size': '1.4rem'}),
    ],
    className="p-2 text-muted"
)
download_button_ar = html.Div(
    [
        html.A(
            children=html.I(
                className="fas fa-file-download fa-lg",
                id="target-ar",
            ),
            href='javascript:void(0);',
            id='link-dummy'
        ),
        dbc.Tooltip(
            "Download das águas residuais tratadas e reutilizadas em Lisboa (.xlsx).",
            target="target-ar", style={'font-size': '1.4rem'}),
    ],

    className="p-2 text-muted")

ar_1_container = html.Div([
    dbc.Row([
        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb2'),
        dbc.Col(dbc.Row([html.H6(id="header-bar-ar", style=TITLE_STYLE), info_button_ar, download_button_ar],
                        align="center", justify="center", no_gutters=True), align='center', className='title-blurb'),
        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb2'),
    ], justify='center'),

    dbc.Row([
        dbc.Col(
            dcc.Loading(type="circle",
                        style={'margin': '40%'},
                        children=dcc.Graph(id='bar-ar', config={'displayModeBar': False})
                        ),
            lg=6),
        dbc.Col(
            dcc.Loading(type="circle",
                        style={'margin': '40%'},
                        children=dcc.Graph(id='map-ar', config={'displayModeBar': False})
                        ), lg=6)
    ], justify='center'),
    collapse_ar,

])

info_button_ar_2 = html.Div(
    [
        html.I(className="fas fa-question-circle fa-sm", id="target_ar2"),
        dbc.Tooltip("A Águas do Tejo Atlântico (AdTA) é a entidade que recolhe e trata as águas residuais de Lisboa, "
                    "promove a sua reutilização dentro das próprias ETAR e fornece parte dessa água às Juntas de Freguesia e à Câmara Municipal de Lisboa.",
                    target="target_ar2",
                    style={'font-size': '1.4rem'}),
    ],
    className="p-2 text-muted"
)
collapse_ar_2 = html.Div(
    [
        dbc.Button(
            "+ Info",
            id="collapse-btn-ar2",
            size="lg",
            # className="mb-3",
            # outline=True,
            color="link",
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody(
                dcc.Markdown('''
                _Atendendo à tipologia de ocupação urbana, os potenciais usos identificados para a reutilização na área de concessão da AdTA são os seguintes:_
                * _irrigação na agricultura, para rega de diferentes tipos de culturas em campo aberto ou em estufas;_
                * _irrigação paisagística, para jardins, parques, campos de golfe, áreas residenciais e comerciais e, de um modo geral, em áreas verdes;_
                * _reutilização na indústria, para circuitos de arrefecimento, caldeiras, água de processo e construção civil;_
                * _usos urbanos não potáveis, para a proteção contra incêndios, limpeza de ruas e sanitários e aparelhos de ar condicionado._
                '''),

                id='info-ar2'),
                # style= {'font-style': 'italic'}
            ),
            id="collapse-ar2",
        ),
    ], style={'font-family': family_generico, 'margin-bottom': '2%'},
)
ar_2_container = html.Div(
    [dbc.Row([
        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),
        dbc.Col(dbc.Row(
            [html.H6("Evolução anual de água tratada e reutilizada em Lisboa", style=TITLE_STYLE), info_button_ar_2],
            align="center", justify="center", no_gutters=True), md=8, align="center"),
        dbc.Col(html.Hr(), style={'width': 'inherit'}, width=2, align="center", className='blurb'),

    ], justify='center'),
        dbc.Row([
            dbc.Col(dcc.Markdown('''**Filtrar por tipo de fluxo:**'''), align="center", width=6,
                    style=INSTRUCTION_STYLE_center, className='blurb3'),
            dbc.Col(dcc.Markdown('''**Personalizar:**'''), align="center", width={"size": 6},
                    style=INSTRUCTION_STYLE_center, className='blurb3'),

        ], justify='center', align="start", no_gutters=True),
        dbc.Row([
            dbc.Col(
                dcc.RadioItems(
                    options=[
                        {"label": "Águas Tratadas", "value": "Águas Tratadas"},
                        {"label": "Total - Água Tratada", "value": "Total1"},
                        {"label": "Águas Reutilizadas", "value": "Águas Reutilizadas"},
                        {"label": "Total - Água Reutilizada", "value": "Total2"},
                        {"label": "Personalizado", "value": "Personalizado"},
                        {"label": "Seleccionar Tudo", "value": "Todas"},
                    ],
                    # labelStyle={"margin-right": "0.5%"},
                    # switch=True,
                    value="Personalizado",
                    id="radio-ar-anual",
                    # inline=True,
                    labelStyle={'display': 'inline-block', 'margin-left': '4%'},

                ),
                md=6, style={'font-family': family_generico}
            ),
            dbc.Col(
                dcc.Dropdown(

                    value=["Alcântara"],
                    id='drop-ar',
                    clearable=False,
                    multi=True,
                    style={'font-family': family_generico}
                ), md=6
            ),
        ], justify='center', align="start", no_gutters=True),
        dbc.Col(
            dcc.Graph(id='ar-timeseries', config={'displayModeBar': False}),

            width=12),
        collapse_ar_2
    ], style={"padding": "0% 1% 1% 1%", "margin-left": "1%", "margin-top": "1%"})

tab_residuais = html.Div([

    dbc.Row([
        dbc.Col(side_bar_ar, className="pretty_container", lg=3, style={'margin-top': '0.8%', 'margin-left': '0.8%'}),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    ar_1_container
                ], lg=12),
            ]),

            dbc.Row([
                dbc.Col([
                    ar_2_container
                ], lg=12)
            ])

        ], className="pretty_container eight columns", align="center",
            style={"padding": "0% 1% 1% 1%", "margin-left": "1%", "margin-top": "1%"}),

    ]), modal_ar,
    html.Div(html.P('Dados disponibilizados pela EPAL e pela Águas do Tejo Atlântico (ADTA).',
                    style=INSTRUCTION_STYLE_left)),
    html.Div('escondido', id='escondido', style={'display': 'none'})
]),

tabs = dbc.Tabs(
    [
        dbc.Tab(label="Consumo de Água", tab_id='tab-consumo', label_style={'font-family': family_generico},
                tab_style={"margin-left": "0%"}),
        dbc.Tab(label="Águas Residuais", tab_id='tab-residuais', label_style={'font-family': family_generico},
                tab_style={"margin-left": "0%"}),
        dbc.Tab(label="Balanço de Água", tab_id='tab-balanco', label_style={'font-family': family_generico},
                tab_style={"margin-left": "0%"}),

    ],
    id='multi-tabs',
    active_tab="tab-consumo",
    style={"margin-left": "0%"}
    # style={"position": "fixed", "z-index": "1"}
)


@app.callback(
    Output("collapse", "is_open"),
    [Input("toggle", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory("data", path, as_attachment=True)


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Matriz de Água</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([

    html.Button(
        # use the Bootstrap navbar-toggler classes to style the toggle
        html.Span(className="navbar-toggler-icon"),
        className="navbar-toggler",
        # the navbar-toggler classes don't set color, so we do it here
        style={
            "color": "rgba(0,0,0,.5)",
            "border-color": "rgba(0,0,0,.1)",
        },
        id="toggle",
    ),
    dbc.Collapse(tabs, id="collapse"),
    html.Div(id='tabs-content'),

])


#
# app.layout = html.Div([
#     dcc.Loading(children=
#     [
#         tabs,
#         html.Div(id='tabs-content'),
#
#     ],
#         fullscreen=True
#     )
# ])
def update_buttons(type_bar, ano_bar_graph_selected, trigger, anos, tab):
    if trigger != type_bar + '.clickData':

        anos_bool = [trigger != f'sel_{a}_{tab}.n_clicks' for a in anos]

        if sum(anos_bool) == len(anos):
            anos_bool = [True] * (len(anos) - 1) + [False]

        a_pos = anos_bool.index(False)
        ano = anos[a_pos]
        return anos_bool + [json.dumps(str(ano))]

    else:

        anos_bool = [a != int(ano_bar_graph_selected['points'][0]['x']) for a in anos]
        a_pos = anos_bool.index(False)
        ano = anos[a_pos]
        return anos_bool + [json.dumps(str(ano))]


@app.callback(
    [Output(f"sel_{a}_cons", "outline") for a in anos_cons]
    + [Output("mem-year-cons", "children")]
    ,
    [Input("ano-bar-graph", "clickData")] + [Input(f"sel_{a}_cons", "n_clicks") for a in anos_cons]
)
def update_button_outline_cons(ano_bar_graph_selected, sel_2013, sel_2014, sel_2015, sel_2016, sel_2017, sel_2018, sel_2019):
    if not ctx.triggered:
        raise PreventUpdate

    return update_buttons("ano-bar-graph", ano_bar_graph_selected, ctx.triggered[0]['prop_id'], anos_cons, 'cons')


@app.callback(
    [Output(f"sel_{a}_ar", "outline") for a in anos_ar]
    + [Output("mem-year-ar", "children")]
    ,
    [Input("ano-bar-graph-ar", "clickData")] + [Input(f"sel_{a}_ar", "n_clicks") for a in anos_ar]
)
def update_button_outline_ar(ano_bar_graph_selected, sel_03, sel_04, sel_05, sel_06, sel_07, sel_08, sel_09, sel_10,
                             sel_11, sel_12, sel_13, sel_14, sel_15, sel_16, sel_17, sel_18, sel_19):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    return update_buttons('ano-bar-graph-ar', ano_bar_graph_selected, ctx.triggered[0]['prop_id'], anos_ar, 'ar')


@app.callback(
    [Output(f"sel_{a}_bal", "outline") for a in anos_bal]
    + [Output("mem-year-bal", "children")]
    ,
    [Input("ano-bar-graph-bal", "clickData")] + [Input(f"sel_{a}_bal", "n_clicks") for a in anos_bal]
)
def update_button_outline_bal(ano_bar_graph_selected, sel_2008, sel_2009,
                              sel_2010, sel_2011, sel_2012, sel_2013, sel_2014, sel_2015, sel_2016, sel_2017, sel_2018, sel_2019):
    if not dash.callback_context.triggered:
        raise PreventUpdate

    return update_buttons("ano-bar-graph-bal", ano_bar_graph_selected, ctx.triggered[0]['prop_id'], anos_bal, 'bal')


@app.callback(Output('tabs-content', 'children'),
              [Input('multi-tabs', 'active_tab')])
def render_content(tab):
    if tab == 'tab-consumo':
        return tab_consumo
    elif tab == 'tab-balanco':
        return tab_balanco
    elif tab == 'tab-residuais':
        return tab_residuais


for tab in ids_modal:

    @app.callback(
        Output(ids_modal[tab]['id_m'], "is_open"),
        [
            Input(ids_modal[tab]['id_t'], "n_clicks"),
            Input(ids_modal[tab]['id_d'], "n_clicks"),
            Input(ids_modal[tab]['id_c'], "n_clicks")],
        [State(ids_modal[tab]['id_m'], "is_open")],
    )
    def toggle_modal_consumo(n1, n2, close, is_open):

        if n1 or n2 or close:
            return not is_open

        return is_open

for tab in ids_modal:

    @app.callback(
        Output(ids_modal[tab]['div'], 'children'),
        [

            Input(ids_modal[tab]['id_d'], "n_clicks"),

        ],
        [
            State(ids_modal[tab]['id_t'], "id"),
            State(ids_modal[tab]['id_r'], "value")
        ]
    )
    def regista_pessoas(n, nome, tipo):
        if not ctx.triggered:
            raise PreventUpdate
        if n:
            if nome == 'target-consumo':
                num = 0
            elif nome == 'target-freg':
                num = 1
            elif nome == 'target-ar':
                num = 2
            else:
                num = 3
            if tipo == 1:
                letra = 'pessoal'
            elif tipo == 2:
                letra = 'profissional'
            else:
                letra = 'academico'

            pessoa_lista = ["", "", "", ""]
            pessoa_lista[num] = letra
            registo = Pessoas(consumo=pessoa_lista[0], freguesias=pessoa_lista[1], aguasresiduais=pessoa_lista[2],
                              balanco=pessoa_lista[3])

            db.session.add(registo)
            db.session.commit()

            # position = letra + num
            # print(position)
            # registo = openpyxl.load_workbook('data/registo_pessoas.xlsx')
            # registo_sheet = registo['Sheet1']
            # registo_sheet[position] = registo_sheet[position].value + 1
            # registo.save('data/registo_pessoas.xlsx')

        return None
#
# @app.callback(
#     [Output('link-file-freg', 'href'),
#      Output("modal-freg", "is_open")],
#     [
#      Input("target-freg", "n_clicks"),
#      Input("close-freg", "n_clicks")],
#     [State("modal-freg", "is_open")],
# )
# def toggle_modal_freg(freg, close, is_open):
#
#     if freg or close:
#         print("aqui")
#         link = '/download/Consumo_Freguesias.xlsx'
#         return link, not is_open
#
#     return 'javascript:void(0);', is_open

for tab in ids_modal:
    @app.callback(
        Output(ids_modal[tab]['id_d'], 'disabled'),
        [Input(ids_modal[tab]['id_r'], "value"), Input(ids_modal[tab]['id_c'], "n_clicks")]
    )
    def enable_dwnld_button(value, n):
        if value:
            return False
        if n:
            return True
        else:
            return True

for tab in ids_modal:
    @app.callback(
        Output(ids_modal[tab]['id_r'], "value"),
        [Input(ids_modal[tab]['id_c'], "n_clicks")]
    )
    def enable_radio(n):
        if n:
            return None


def create_ano_bar_graph(df, ano_select, per_capita):
    """
    O formato de df deve mesmo ser uma pd.DataFrame, nao uma pd.series
    A coluna deve-se chamar 'Total' e os valores devem estar em 10^3 m3

    """

    if per_capita == None:
        per_capita = 1
    layout_ano_bar = copy.deepcopy(layout)
    # ano_select = 2017
    # df = bal_potavel_df
    ano_posi = list(df.index).index(ano_select)

    # color_fill = ['#9BD7F1', ] * len(df.index)

    color_fill = ['#85ceed', ] * len(df.index)
    color_fill[ano_posi] = '#029CDE'
    color_line = ['#029CDE', ] * len(df.index)
    if per_capita == 2:
        if isleap(ano_select):
            dias = 366
        else:
            dias = 365

        df['pop'] = populacao
        df['Total'] = (df['Total'] * 1000000) / df['pop'] / dias
        text_un = ' l/dia per capita'

        text_hover = ['Total: ' + '{:.0f}'.format(tr) + text_un + '<br>Ano: ' + '{}'.format(an)
                      for tr, an in zip(list(df['Total']), list(df.index))]

        text_write = ['{:.0f}'.format(tr)
                      for tr in list(df['Total'])]
    else:

        text_hover = ['Total: ' + '{:.2f}'.format(tr / 1000) + unidade_1 + '<br>Ano: ' + '{}'.format(an)
                      for tr, an in zip(list(df['Total']), list(df.index))]

        text_write = ['{:.0f}'.format(tr / 1000) + "M"
                      for tr in list(df['Total'])]

    fig = go.Figure(data=[go.Bar(
        x=df.index,
        y=df['Total'],
        marker_color=color_fill,
        marker_line_color=color_line,
        text=text_write,
        hovertext=text_hover,
        hoverinfo='text',
        textposition='outside',
        hoverlabel=dict(font=dict(family=layout['font']['family'])),

    )])

    layout_ano_bar['margin'] = dict(l=0, r=0, b=0, t=0)
    layout_ano_bar['height'] = 200

    layout_ano_bar['dragmode'] = 'select'

    fig.update_layout(layout_ano_bar)
    # fig.update_layout(height=350)
    fig.update_yaxes(automargin=True, range=[0, max(df['Total']) * 1.15],
                     autorange=False, fixedrange=True, showticklabels=False)
    fig.update_xaxes(fixedrange=True, type='category')

    return fig


#
# def update_slider_template(ano_bar_graph_selected):
#
#
#     if ano_bar_graph_selected is None:
#         return 2018
#     else:
#         return int(ano_bar_graph_selected['points'][0]['x'])

@app.callback(
    [
        Output('head-ano-bar-cons', 'children'),
        Output("ano-bar-graph", "figure"),
    ],
    [
        # Input("year-slider", "value"),
        Input('multi-tabs', 'active_tab'),
        Input("mem-year-cons", "children"),
        Input('radio-pop', 'value')

    ]
)
def update_ano_bar_cons(at, ano_mem, per_capita):
    if not ctx.triggered or at != 'tab-consumo':
        raise PreventUpdate
    try:
        ano = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano = anos_cons[-1]
    # print(ano)
    df = copy.deepcopy(sector_df)
    if per_capita == 2:
        title = 'Consumo Médio Diário de Água em Lisboa (l/dia per capita)'
    else:
        title = 'Consumo Total Anual de Água, em Lisboa ({})'.format(unidade)

    return title, create_ano_bar_graph(df, ano, per_capita)


#
#
# @app.callback(
#     Output("year-slider", "value"),
#     [Input("ano-bar-graph", "clickData")])
# def update_year_slider_cons(ano_bar_graph_selected):
#     if not dash.callback_context.triggered:
#         raise PreventUpdate
#     return update_slider_template (ano_bar_graph_selected)
#

@app.callback(
    Output("ano-bar-graph-bal", "figure"),
    [
        # Input("year-slider-bal", "value"),
        Input('multi-tabs', 'active_tab'),
        Input("mem-year-bal", "children"),
    ]
)
def update_ano_bar_bal(at, ano_mem):
    if not ctx.triggered or at != 'tab-balanco':
        raise PreventUpdate
    try:
        ano = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano = anos_bal[-1]
    df = bal_potavel_df
    df = df.loc[df['Ordem'] == 'Água consumida em Lisboa', 'value'].to_frame()
    df = df.rename({'value': 'Total'}, axis='columns')
    df = df * 1000

    return create_ano_bar_graph(df, ano, 1)


# @app.callback(
#     Output("year-slider-bal", "value"),
#     [Input("ano-bar-graph-bal", "clickData")])
# def update_year_slider_bal(ano_bar_graph_selected):
#     if not dash.callback_context.triggered:
#         raise PreventUpdate
#     return update_slider_template (ano_bar_graph_selected)


@app.callback(
    Output("ano-bar-graph-ar", "figure"),
    [
        # Input("year-slider-ar", "value"),
        Input('multi-tabs', 'active_tab'),
        Input("mem-year-ar", "children"),

    ]
)
def update_ano_bar_ar(at, ano_mem):
    if not ctx.triggered or at != 'tab-residuais':
        raise PreventUpdate
    try:
        ano = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano = anos_ar[-1]
    df = aguas_r_df
    bad_df = df.Subsistema.isin(['Total'])
    df = df[~bad_df]
    df = df.loc[df.Subsistema == 'Total - Água Tratada', 'Total'].to_frame()
    df = df * 1000
    fig = create_ano_bar_graph(df, ano, 1)
    fig.update_layout(xaxis_tickangle=-80)
    return fig


#
#
# @app.callback(
#     Output("year-slider-ar", "value"),
#     [Input("ano-bar-graph-ar", "clickData")])
# def update_year_slider_bal(ano_bar_graph_selected):
#     if not dash.callback_context.triggered:
#         raise PreventUpdate
#     return update_slider_template (ano_bar_graph_selected)


@app.callback(
    [
        Output('info-freg', 'children'),
        Output('drop-freg-container', 'style'),
        Output('header-freg', 'children'),
        Output('bar-freg-container', 'style'),
        Output('bar-freguesias', 'figure')
    ],
    [
        Input('mem-year-cons', 'children'),
        Input('drop-freg', 'value'),
        Input('multi-tabs', 'active_tab')
    ],
)
def update_bar_freguesias(ano_mem, drop_select, at):
    if not ctx.triggered or at != 'tab-consumo':
        raise PreventUpdate
    try:
        ano_select = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano_select = anos_cons[-1]
    if ano_select < 2017:
        # text_alert = "Ausência de dados para {}".format(str(ano_select))
        return None, {'visibility': 'hidden'}, None, {'visibility': 'hidden'}, {}

    df = df_fregs[df_fregs['Ano'] == ano_select]

    if drop_select == 'consumo_dom':
        df = df.sort_values('Consumo_dom')
        values = df['Consumo_dom']
        my_text_show = ['{:.2f}'.format(cons / 1000000) + unidade_1 for cons in list(values)]

        text_hover = ['<span style="font-weight:bold">Freguesia: ' + '{}'.format(freguesias) + '</span>' +
                      '<br>Consumo Doméstico: ' + '{:.2f}'.format(cons / 1000000) + unidade_1
                      for freguesias, cons in
                      zip(list(df['Freguesias']), values)]

        title_1 = "Consumo Doméstico de Água Potável, "

    elif drop_select == 'consumo_total':
        df = df.sort_values('Consumo_total')
        values = df['Consumo_total']
        my_text_show = ['{:.2f}'.format(cons / 1000000) + unidade_1 for cons in list(values)]

        text_hover = ['<span style="font-weight:bold">Freguesia: ' + '{}'.format(freguesias) + '</span>' +
                      '<br>Consumo Total: ' + '{:.2f}'.format(cons / 1000000) + unidade_1
                      for freguesias, cons in
                      zip(list(df['Freguesias']), values)]

        title_1 = "Consumo de Água Potável, "

    elif drop_select == "contadores":
        df = df.sort_values('N_contadores')
        values = df['N_contadores']
        my_text_show = list(values)

        text_hover = ['<span style="font-weight:bold">Freguesia: ' + '{}'.format(freguesias) + '</span>' +
                      '<br>Nº contadores: ' + '{}'.format(cont)
                      for freguesias, cont in
                      zip(list(df['Freguesias']), values)]
        title_1 = "Número de Contadores, "

    else:
        df = df.sort_values('N_smartmeters')
        values = df['N_smartmeters']
        my_text_show = list(values)

        text_hover = ['<span style="font-weight:bold">Freguesia: ' + '{}'.format(freguesias) + '</span>' +
                      '<br>Nº smartmeters: ' + '{}'.format(smart)
                      for freguesias, smart in
                      zip(list(df['Freguesias']), values)]

        title_1 = "Número de Smartmeters, "

    # values = values/sum(values)

    fig = go.Figure(data=[go.Bar(
        x=values,
        y=df['Freguesias'],
        marker={'color': values,
                'colorscale': cl_scale_blues},
        orientation='h',
        opacity=0.8,
        marker_line_width=1.5,
        text=my_text_show,
        hovertext=text_hover,
        hoverlabel=dict(font=layout['font']),
        hoverinfo='text',
        textposition='outside'

    )])

    layout_freg = copy.deepcopy(layout)
    # 'height': '80vh
    layout_freg['margin'] = dict(l=0, b=0, t=0, r=0)
    # layout_freg['autosize'] = True

    layout_freg['hovermode'] = "y"
    fig.update_xaxes(showticklabels=False, range=[0, values.max() * 1.2])
    # fig.update_xaxes(showticklabels=False)

    fig.update_layout(layout_freg)

    title_bar = title_1 + "por Freguesia, em {}".format(ano_select)

    text_freg = dcc.Markdown('''
        No ano {0} estavam instalados pela EPAL **{1}** smartmeters em comparação com o número total de contadores, **{2}**, o que equivale a cerca de **{3}%**.


    '''.format(ano_select, df.N_smartmeters.sum(), df.N_smartmeters.sum() + df.N_contadores.sum(),
               round(df.N_smartmeters.sum() / (df.N_smartmeters.sum() + df.N_contadores.sum()) * 100)))
    return text_freg, {'visibility': 'visible'}, title_bar, {'visibility': 'visible'}, fig


#

@app.callback(

    [
        Output('freg-title-geral', 'style'),
        Output('map-freg-container', 'style'),
        Output('alert-map', 'children'),
        Output('alert-map', 'is_open'),
        Output('mapa-freguesias', 'figure')],
    [Input('mem-year-cons', 'children'),
     Input('drop-freg', 'value'),
     Input('multi-tabs', 'active_tab')
     ]
)
def update_mapa_freguesias(ano_mem, drop_select, at):
    if not ctx.triggered or at != 'tab-consumo':
        raise PreventUpdate

    try:
        ano_select = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano_select = anos_cons[-1]
    if ano_select < 2017:
        text_alert = "Ausência de dados para {}".format(str(ano_select))
        return {'visibility': 'hidden'}, {'visibility': 'hidden'}, text_alert, True, {}

    df = df_fregs.loc[df_fregs['Ano'] == ano_select].copy()
    df['id'] = list(range(1, len(df) + 1))
    df['id'] = [str(i).zfill(2) for i in df['id']]

    consumo_simp_dom = list(df['Consumo_dom'])
    consumo_simp_dom = [(c / 1000000) for c in consumo_simp_dom]

    consumo_simp_total = list(df['Consumo_total'])
    consumo_simp_total = [(c / 1000000) for c in consumo_simp_total]

    if drop_select == 'consumo_dom':

        values = consumo_simp_dom
        text_scatter = [str(round(cons, 2)) + unidade_1 for cons in values]
        title_bar = unidade_1
        cl_scale = cl_scale_blues

    elif drop_select == 'consumo_total':

        values = consumo_simp_total
        text_scatter = [str(round(cons, 2)) + unidade_1 for cons in values]
        title_bar = unidade_1
        cl_scale = cl_scale_blues


    elif drop_select == "contadores":
        values = df['N_contadores']
        text_scatter = values
        title_bar = 'Contadores'
        cl_scale = cl_scale_blues


    else:
        values = df['N_smartmeters']
        text_scatter = values
        title_bar = 'Smartmeters'
        cl_scale = cl_scale_blues

    text_hover = ['<span style="font-weight:bold">Freguesia: ' + '{}'.format(freguesias) + '</span>' +
                  '<br>Ano: ' + '{}'.format(ano_select) +
                  "<br>Consumo Total: " + '{:.2f}'.format(consumo_tot) + unidade_1 +
                  "<br>Consumo Doméstico: " + '{:.2f}'.format(consumo_dom) + unidade_1 +
                  '<br>Nº contadores: ' + '{:.0f}'.format(contador) +
                  '<br>Nº smartmeters: ' + '{:.0f}'.format(smartmeter)
                  for freguesias, consumo_tot, consumo_dom, contador, smartmeter in
                  zip(list(df['Freguesias']), consumo_simp_total, consumo_simp_dom, list(df['N_contadores']),
                      list(df['N_smartmeters']))]

    data_trace_1 = go.Choroplethmapbox(
        geojson=freguesias_jsn,
        locations=df['id'],
        z=values,
        # text=df_fregs['Freguesias'],
        hovertext=text_hover,
        hoverinfo='text',
        colorscale=cl_scale,
        hoverlabel=dict(font=layout['font']),
        # zmin=min(values),
        # zmax=max(values)*1.20,
        # zmin=670, zmax=3800,
        marker_opacity=0.8,
        marker_line_width=0,
        below=True,
        selected=dict(marker=dict(opacity=1)),
        unselected=dict(marker=dict(opacity=0.5)),
        colorbar=dict(outlinecolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)', bgcolor='#F9F9F9', title=title_bar),

    )

    # Futuramente, pontos para colocar texto
    # data_trace_2 = dict(type='scattermapbox',
    #                     lon=freg_center['centroid_long'],
    #                     lat=freg_center['centroid_lat'],
    #                     text=text_scatter,
    #                     mode='text',
    #                     hoverinfo='none',
    #                     textfont=layout['font'],
    #                     # textposition="bottom left",
    #                     # hovertext="rrrrr",
    #
    #                     # marker_color = df['cnt'],
    #                     )

    layout_map = dict(mapbox_style="light", mapbox_zoom=11, mapbox_center={"lat": 38.738946, "lon": -9.155685},
                      mapbox_accesstoken=mapbox_access_token, )

    layout_map['font'] = layout['font']

    fig = go.Figure(data=[data_trace_1], layout=layout_map)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    # fig.show()
    return {'visibility': 'visible'}, {'visibility': 'visible'}, None, False, fig


def collapse_template(n, is_open):
    if n:
        b = not is_open
        if is_open:
            return '+ info', b
        else:
            return '- info', b
    return '+ info', is_open


@app.callback(
    [
        Output("collapse-btn-bal", "children"),
        Output("collapse-bal", "is_open"),
    ],
    [
        Input("collapse-btn-bal", "n_clicks"),
    ],
    [State("collapse-bal", "is_open")],
)
def toggle_collapse_bal(n, is_open):
    return collapse_template(n, is_open)


@app.callback(
    [
        Output("collapse-btn-ar2", "children"),
        Output("collapse-ar2", "is_open"),
    ],
    [
        Input("collapse-btn-ar2", "n_clicks"),
    ],
    [State("collapse-ar2", "is_open")],
)
def toggle_collapse_ar2(n, is_open):
    return collapse_template(n, is_open)


@app.callback(
    [
        Output("collapse-btn-ar", "children"),
        Output("collapse-ar", "is_open"),
    ],
    [
        Input("collapse-btn-ar", "n_clicks"),
    ],
    [State("collapse-ar", "is_open")],
)
def toggle_collapse_ar(n, is_open):
    return collapse_template(n, is_open)


@app.callback(
    [
        Output("collapse-btn-cons", "children"),
        Output("collapse-cons", "is_open"),
    ],
    [
        Input("collapse-btn-cons", "n_clicks"),
    ],
    [State("collapse-cons", "is_open")],
)
def toggle_collapse_cons(n, is_open):
    return collapse_template(n, is_open)


@app.callback(
    [
        Output("collapse-btn-freg", "children"),
        Output("collapse-freg", "is_open"),
    ],
    [
        Input("collapse-btn-freg", "n_clicks"),
    ],
    [State("collapse-freg", "is_open")],
)
def toggle_collapse_freg(n, is_open):
    return collapse_template(n, is_open)


@app.callback(
    [
        Output("collapse-btn-donut", "children"),
        Output("collapse-donut", "is_open"),
    ],
    [
        Input("collapse-btn-donut", "n_clicks"),
    ],
    [State("collapse-donut", "is_open")],
)
def toggle_collapse_donut(n, is_open):
    return collapse_template(n, is_open)


@app.callback(
    [Output('info-donut', 'children'),
     Output('donut-sector', 'figure'),
     Output('header-donut', 'children')],
    [Input('mem-year-cons', 'children'),
     Input('drop-cons', 'value'),
     ], )
def update_donut(ano_mem, drop_cons):
    layout_donut = copy.deepcopy(layout)

    try:
        ano_select = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano_select = anos_cons[-1]

    # ano_select = 2018
    if drop_cons == "consumo_sector":
        df = sector_df.loc[ano_select, sector_df.columns != 'Total'].to_frame()
        df = df[(df.T != 0).any()]

        df = round(df / 1000, 2)
        df['labels'] = df.index
        df['color_fill'] = df['labels'].apply(lambda x: color_sector_dead_d[x])
        df['color_line'] = df['labels'].apply(lambda x: color_sector_live_d[x])

        my_text_hover = [lab + ': ' + '{:.1f}'.format(val) + unidade_1 + '<br>Ano: ' + '{}'.format(ano_select)
                         for lab, val in zip(df.index.tolist(), list(df[ano_select]))]

        fig = go.Figure(data=[go.Pie(labels=df.index.tolist(),
                                     values=df[ano_select].tolist(),
                                     hole=0.6,
                                     marker=dict(colors=df['color_fill'], line=dict(color=df['color_line'], width=2)),
                                     textinfo='percent',
                                     hovertext=my_text_hover,
                                     hoverinfo='text',
                                     hoverlabel=dict(font=dict(family=layout['font']['family'])),
                                     opacity=0.8,
                                     sort=False)])
        title_donut = "Consumo por Sector de Consumo, em {}".format(ano_select)
        text_info = dcc.Markdown('''
        _No ano de 2014, na sequência da reorganização administrativa 
        da cidade de Lisboa, houve transferência da titularidade de contratos da CML (Câmara Municipal de Lisboa)
         para as Juntas de Freguesia, designados de Delegação CML, o que causou o aumento dos consumos das Juntas._
         ''')


    elif drop_cons == "ndom":
        df = ndom_df.loc[ano_select, ndom_df.columns != 'Total'].to_frame()
        df = df[(df.T != 0).any()]
        df = round(df / 1000000, 2)
        df = df.sort_values(ano_select)
        df['labels'] = df.index
        df['color_fill'] = df['labels'].apply(lambda x: color_ndom_dead_d[x])
        df['color_line'] = df['labels'].apply(lambda x: color_ndom_live_d[x])
        df['Percentagem'] = df[ano_select] / (df[ano_select].sum()) * 100

        my_text_hover = [lab + ': ' + '{:.1f}'.format(val) + unidade_1 + '<br>Ano: ' + '{}'.format(ano_select)
                         for lab, val in zip(df.index.tolist(), list(df[ano_select]))]

        my_text_show = [nom + " (" + '{:.0f}'.format(pr) + '%)' for nom, pr in
                        zip(list(df.index), list(df['Percentagem']))]

        fig = go.Figure(data=[go.Bar(
            x=df[ano_select],
            y=df.index,
            marker_color=df['color_fill'],
            orientation='h',
            opacity=0.8,
            marker_line_color=df['color_line'],
            marker_line_width=1.5,
            text=my_text_show,
            hovertext=my_text_hover,
            hoverinfo='text',
            hoverlabel=dict(font=dict(family=layout['font']['family'])),
            textposition='auto'

        )])
        fig.update_xaxes(title_text="Milhões de {}".format(unidade))
        title_donut = "Consumo Não Doméstico , em {}".format(ano_select)
        percentagem = round(perc_ndom[ano_select], 1)
        text_info = dcc.Markdown('''
        * _O consumo não doméstico na cidade de Lisboa em **{0}** representa **{1}%** do consumo total na cidade (excluindo as perdas económicas)._ 
        * _O **Consumo Habitacional** diz respeito a consumos de alojamento em habitações municipais, 
         consumos de água nas residências de estudantes e consumos nos domicílios de embaixadores. 
         Ou seja, apesar dos contratos serem feitos com empresas ou entidades públicas, a água 
         é utilizada para fins habitacionais._
         * _A categoria **Outros** refere-se aos consumos de água destinados a atividades desportivas, 
         Lares e Centros de dia/Recolhimento, Estabelecimentos prisionais, etc._
         '''.format(ano_select, percentagem))
        pos_annot = [[0.09, 0.076], [0.092, 0.076], [0.11, 0.076], [0.168, 0.076], [0.205, 0.076], [0.2222, 0.27]]

        # layout_donut['annotations'] = [
        #     go.layout.Annotation(
        #         x=pos_annot[anos.index(ano_select)][0],
        #         y=pos_annot[anos.index(ano_select)][1],
        #         xref="paper",
        #         yref="paper",
        #         text="Contratos de entidades públicas (ver <i>+INFO</i> )",
        #         showarrow=True,
        #         arrowhead=7,
        #         ax= 300,
        #         ay=-10,
        #         font=dict(color='#667073'),
        #
        #         arrowcolor='#667073'
        #     )
        # ]

    layout_donut['legend'] = go.layout.Legend(

        x=0.1,
        y=1.3,
        xanchor='center',
        traceorder="normal",
        font=dict(
            # size=13,
            color="black"
        ),
        bgcolor='rgba(0,0,0,0)',
        orientation='h'
    )

    layout_donut['margin'] = dict(l=0, r=0, b=20, t=10)
    fig.update_layout(layout_donut)
    fig.update_yaxes(showticklabels=False, showgrid=False)

    return text_info, fig, title_donut


@app.callback(
    [Output('drop-ano-line', 'options'),
     Output('drop-ano-line', 'value')],
    [
        Input('multi-tabs', 'active_tab'),
        Input('drop-cons', 'value'),
        Input('radio-ano-line', 'value'),
    ],
    [State('drop-ano-line', 'value')]
)
def update_ano_line_drop(at, drop_cons, selector, current_drop_cons):
    if not dash.callback_context.triggered or at != 'tab-consumo':
        raise PreventUpdate
    if drop_cons == "consumo_sector":
        items = sector_options
        if selector == 'Todos':
            value = sector_df.columns.to_list()
        elif selector == 'Personalizado':
            value = ['Doméstico']
        elif selector == 'Total':
            value = ['Total']
        else:
            value = []
        if 'Doméstico' in current_drop_cons:
            value = value + ['Doméstico Per Capita']
    else:

        items = ndom_options
        if selector == 'Todos':
            value = ndom_df.columns.to_list()
        elif selector == 'Personalizado':
            value = ["CML  + Delegações CML"]
        elif selector == 'Total':
            value = ['Total']
        else:
            value = []

    return items, value


@app.callback(
    [
        Output('sector-tipo-inst', 'children'),
        Output("header-ano-line", "children"),
        Output("ano-line-graph", "figure")
    ],
    [
        Input('drop-ano-line', 'value'),
        Input('multi-tabs', 'active_tab'),
        Input('drop-cons', 'value'),
    ]
)
def update_ano_line(drop_tipo, at, drop_cons):
    if not dash.callback_context.triggered or at != 'tab-consumo':
        raise PreventUpdate

    if drop_cons == "consumo_sector":
        df = copy.deepcopy(sector_df)
        df['Doméstico Per Capita'] = df['Doméstico'] * 1000 / populacao
        if not all(elem in df.columns.to_list() for elem in drop_tipo):
            raise PreventUpdate

        df = df[drop_tipo] / 1000
        lista_index = list(df.sum().sort_values().index)
        color_line = [color_sector_live_d[x] for x in lista_index]
        color_fill = [color_sector_dead_d[x] for x in lista_index]
        title = "Consumo Anual, por Sector de Consumo"
        sector_tipo_inst = dcc.Markdown('''**Filtrar por sector:**''')

    else:
        if not all(elem in ndom_df.columns.to_list() for elem in drop_tipo):
            raise PreventUpdate

        df = ndom_df[drop_tipo] / 1000000

        lista_index = list(df.sum().sort_values().index)
        color_line = [color_ndom_live_d[x] for x in lista_index]
        color_fill = [color_ndom_dead_d[x] for x in lista_index]
        title = "Consumo Não Doméstico Anual"
        sector_tipo_inst = "Filtrar por tipo de utilização:"

    layout_ano_line = copy.deepcopy(layout)
    if 'Doméstico Per Capita' in drop_tipo:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
    else:
        fig = go.Figure()
    i = 0
    anos = df.index.unique().tolist()

    minimos = []
    maximos = []
    for trace in lista_index:
        if trace == 'Doméstico Per Capita':

            df[trace] = df[trace] * 1000
            my_text = [trace + ': ' + '{:.1f}'.format(tr) + unidade + ' per capita' + "<br>Ano: " + str(ano) for
                       tr, ano in zip(list(df[trace]), anos)]
            df_trace = df[[trace]]
            # minimo = min(df_trace)
            #
            minimo_capita = min(df_trace[trace].tolist())
            maximo_capita = max(df_trace[trace].tolist())

            if False in (df_trace.T != 0).any().tolist():
                df_trace.replace(0, np.nan, inplace=True)
                # anos = df_trace.index.unique().tolist()
            fig.add_trace(
                go.Scatter(x=anos,
                           y=df_trace[trace],
                           name=trace,
                           mode='lines+markers',
                           # line_color=color_line[i],
                           hovertext=my_text,
                           hoverinfo="text",
                           hoverlabel=dict(
                               bgcolor=color_fill[i],
                               # font=dict(size=13)
                           ),
                           line=dict(
                               shape="spline",
                               smoothing=1,
                               width=2,
                               color=color_line[i]
                           ),
                           marker=dict(symbol='hexagon2-dot')
                           ),
                secondary_y=True,
            )
            i += 1

        else:
            my_text = [trace + ': ' + '{:.1f}'.format(tr) + unidade_1 + "<br>Ano: " + str(ano) for tr, ano in
                       zip(list(df[trace]), anos)]

            df_trace = df[[trace]]
            # minimo = min(df_trace)

            minimo = min(df_trace[trace].tolist())
            maximo = max(df_trace[trace].tolist())
            minimos.append(minimo)
            maximos.append(maximo)
            if False in (df_trace.T != 0).any().tolist():
                df_trace.replace(0, np.nan, inplace=True)
                # anos = df_trace.index.unique().tolist()
            fig.add_trace(
                go.Scatter(x=anos,
                           y=df_trace[trace],
                           name=trace,
                           mode='lines+markers',
                           # line_color=color_line[i],
                           hovertext=my_text,
                           hoverinfo="text",
                           hoverlabel=dict(
                               bgcolor=color_fill[i],
                               # font=dict(size=13)
                           ),
                           line=dict(
                               shape="spline",
                               smoothing=1,
                               width=2,
                               color=color_line[i]
                           ),
                           marker=dict(symbol='hexagon2-dot')
                           ),
            )
            i += 1
    try:

        smaller = min(minimos)
        bigger = max(maximos)
    except:
        smaller = 0
        bigger = 30
    espaco = min((bigger - smaller) * 2, 5)
    y_min = max(smaller - espaco, 0)
    y_max = bigger + espaco

    y_span = [y_min, y_max]

    layout_ano_line['legend'] = go.layout.Legend(
        y=1,
        x=0.5,
        yanchor='bottom',
        xanchor='right',
        font=dict(
            # size=13,
            color="black"
        ),
        orientation='h',
        bgcolor='rgba(0,0,0,0)',

    )
    # layout_ano_line['hovermode'] = "x"
    layout_ano_line['margin'] = dict(l=45, r=25, b=0, t=10)
    # layout_ano_line['height'] = 300
    # layout_ano_line['hoverlabel'] = dict(font=dict(family=layout['font']['family']))

    # layout_ano_line['title'] = dict(text=title, xref='paper', x=0.5)
    layout_ano_line['showlegend'] = True
    # , range = y_span
    fig.update_layout(layout_ano_line)

    if 'Doméstico Per Capita' in drop_tipo:
        fig.update_yaxes(title_text="Milhões de {}".format(unidade), showgrid=True, range=y_span, gridcolor="#E0E1DF",
                         secondary_y=False)
        fig.update_yaxes(title_text="{} per capita".format(unidade), showgrid=True,
                         secondary_y=True, overlaying='y1', range=[50.6, 55.39])
    else:
        fig.update_yaxes(title_text="Milhões de {}".format(unidade), showgrid=True, gridcolor="#E0E1DF")

    fig.update_xaxes(showgrid=False)
    # fig.show()
    # fig.update_yaxes(showgrid=False)
    return sector_tipo_inst, title, fig


@app.callback(
    [
        Output('drop-bal', 'options'),
        Output('drop-bal', 'value')
    ],
    [
        Input('multi-tabs', 'active_tab'),
        Input('radio-bal-anual', 'value'),
    ]
)
def update_bal_drop(at, selector):
    if not dash.callback_context.triggered or at != 'tab-balanco':
        raise PreventUpdate
    items = bal_pot_options
    if selector == 'Todos':
        value = list(bal_potavel_df.Ordem.unique())
    elif selector == 'Personalizado':
        value = ['Água consumida em Lisboa']

    # elif selector == 'Total':
    #     value = ['Total']
    else:
        value = []
    return items, value


@app.callback(
    Output('bal-timeseries', 'figure'),
    [
        # Input('bal-potavel', 'hoverData'),
        Input('drop-bal', 'value'),
    ]
)
def update_timeseries(drop_bal):
    if not ctx.triggered:
        raise PreventUpdate

    layout_timeseries = copy.deepcopy(layout)

    df = bal_pot_ts_df
    if isinstance(drop_bal, str):
        drop_bal = [drop_bal]

    df = df[drop_bal]
    lista_index = list(df.sum().sort_values().index)

    color_line = [color_balanco_live_d[x] for x in lista_index]
    color_fill = [color_balanco_dead_d[x] for x in lista_index]

    anos = df.index.unique().tolist()
    fig = go.Figure()

    i = 0
    for trace in lista_index:
        my_text = [trace + ': ' + '{:.0f}'.format(tr) + unidade_1 + "<br>Ano: " + str(ano) for tr, ano in
                   zip(list(df[trace]), anos)]
        fig.add_trace(
            go.Scatter(
                x=anos,
                y=df[trace],
                name=trace,
                # mode='lines+markers'
                mode='lines+markers',
                hovertext=my_text, hoverinfo="text",
                hoverlabel=dict(bgcolor=color_fill[i]),
                line=dict(
                    shape="spline",
                    smoothing=1,
                    width=2,
                    color=color_line[i]
                ),
                marker=dict(symbol='hexagon2-dot')

            ))
        i += 1

        layout_timeseries['legend'] = go.layout.Legend(
            y=1,
            x=0.5,
            yanchor='bottom',
            xanchor='right',
            font=dict(
                # size=13,
                color="black"
            ),
            orientation='h',
            bgcolor='rgba(0,0,0,0)',

        )

    layout_timeseries['autosize'] = True

    fig.update_layout(layout_timeseries, showlegend=True)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(title_text="Milhões de {}".format(unidade), showgrid=True, gridcolor="#E0E1DF")
    fig.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10})

    return fig


# fig.show()


#

@app.callback(
    [
        Output('bal-header', 'children'),
        Output('bal-potavel', 'figure')],
    [Input('mem-year-bal', 'children'),
     Input('multi-tabs', 'active_tab'),
     ]
)
def update_balanco(ano_mem, at):
    if not dash.callback_context.triggered or at != 'tab-balanco':
        raise PreventUpdate
    try:
        ano_select = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano_select = anos_cons[-1]

    # ano_select=2018
    df = bal_potavel_df.loc[ano_select, :]
    layout_balanco = copy.deepcopy(layout)
    layout_balanco['paper_bgcolor'] = '#F9F9F9'

    color_line = [color_balanco_live_d[x] for x in df['Ordem']]
    color_fill = [color_balanco_dead_d[x] for x in df['Ordem']]
    #
    my_text = [nome + ": " + str(valor) + unidade_1 for nome, valor in
               zip(list(df['Ordem']), list(df['value']))]

    fig = go.Figure(data=[dict(
        type='sankey',
        domain=dict(
            x=[0, 1],
            y=[0, 1],
        ),
        orientation="h",
        arrangement='fixed',
        valueformat=".1f",
        valuesuffix=unidade_1,
        # hoverinfo="x",
        node=dict(
            pad=30,
            thickness=30,
            line=dict(
                color=color_line,
                width=1
            ),
            label=my_text,
            color=color_fill,
            x=[0.4, 0.4, 0.7, 0.95, 0.7, 0],
            y=[0.18, 0.7, 0.74, 0.48, 0.4, 0],
        ),
        link=dict(
            source=df['Source'][:-1].tolist(),
            target=df['Target'][:-1].tolist(),
            value=df['value'][:-1].dropna(axis=0, how='any'),
            label=df['Ordem']
        ),
    )
    ])
    # layout_balanco['width']= 100
    layout_balanco['margin'] = dict(l=0, r=10, b=30, t=30)
    layout_balanco['autosize'] = True

    fig.update_layout(layout_balanco)

    title = "Balanço de Água em Lisboa, em {}".format(ano_select)

    # fig.show()
    return title, fig


@app.callback(
    [
        Output('drop-ar', 'options'),
        Output('drop-ar', 'value')
    ],
    [
        Input('multi-tabs', 'active_tab'),
        Input('radio-ar-anual', 'value'),
    ]
)
def update_ar_drop(at, selector):
    if not dash.callback_context.triggered or at != 'tab-residuais':
        raise PreventUpdate

    items = ar_options
    if selector == 'Todas':
        value = ar_values
    elif selector == 'Personalizado':
        value = ['Alcântara']
    elif selector == 'Águas Tratadas':
        value = list(aguas_r_df.Subsistema.unique())
    elif selector == 'Águas Reutilizadas':
        value = list(ar_reu_df.Subsistema.unique())
    elif selector == 'Total1':
        value = ['Total - Água Tratada']
    elif selector == 'Total2':
        value = ['Total - Água Reutilizada']
    else:
        value = []

    return items, value


@app.callback(
    Output('ar-timeseries', 'figure'),
    [
        Input('drop-ar', 'value'),
        Input('multi-tabs', 'active_tab')

    ]
)
def update_ar_timeseries(drop_ar, at):
    if not dash.callback_context.triggered or at != 'tab-residuais':
        raise PreventUpdate

    layout_ar = copy.deepcopy(layout)
    df = ar_totais
    # df_2 = ar_reu_df.T
    # df.loc[:, df.dtypes == float] = df.loc[:, df.dtypes == float]/1000
    if isinstance(drop_ar, str):
        drop_ar = [drop_ar]

    df = df.loc[df['Subsistema'].isin(drop_ar)]

    lista_subs = list(df.Subsistema.unique())

    color_line = [color_ar_live_d[x] for x in lista_subs]
    color_fill = [color_ar_dead_d[x] for x in lista_subs]

    anos = df.index.unique().tolist()

    if all(elem in ar_reu_df.Subsistema.unique() for elem in drop_ar):
        df.assign(quantity=df.Total.mul(1000))
        unidade_temp = unidade_1
        title = "Milhões de " + unidade
    else:
        unidade_temp = unidade_1
        title = "Milhões de " + unidade

    fig = go.Figure()
    i = 0
    minimos = []
    maximos = []
    for trace in lista_subs:
        df_sub = df[df['Subsistema'] == trace]
        my_text = [trace + ': ' + '{:.2f}'.format(tr) + unidade_temp + "<br>Ano: " + str(ano) for tr, ano in
                   zip(list(df_sub['Total']), anos)]

        minimo = min(df_sub['Total'].tolist())
        maximo = max(df_sub['Total'].tolist())
        minimos.append(minimo)
        maximos.append(maximo)

        if False in (df_sub['Total'].T != 0.0).tolist():
            df_sub = df_sub.replace(0, np.nan).copy()

        if trace in ar_reu_df.Subsistema.unique():
            line1 = dict(
                shape="spline",
                smoothing=1,
                width=2,
                color=color_line[i],
                dash='dash'
            )
        else:
            line1 = dict(
                shape="spline",
                smoothing=1,
                width=2,
                color=color_line[i],

            )

        fig.add_trace(
            go.Scatter(
                x=anos,
                y=df_sub['Total'],
                name=df_sub.Subsistema.unique()[0],
                mode='lines+markers',
                hovertext=my_text, hoverinfo="text",
                hoverlabel=dict(bgcolor=color_fill[i]),
                line=line1,
                marker=dict(symbol='hexagon2-dot')
            )
        )
        i += 1

    try:

        smaller = min(minimos)
        bigger = max(maximos)
    except:
        smaller = 0
        bigger = 30
    espaco = min((bigger - smaller) * 2, 20)
    y_min = max(smaller - espaco, 0)
    y_max = bigger + espaco

    y_span = [y_min, y_max]

    layout_ar['legend'] = go.layout.Legend(
        y=1,
        x=0.5,
        yanchor='bottom',
        xanchor='right',
        font=dict(
            # size=13,
            color="black"
        ),
        orientation='h',
        bgcolor='rgba(0,0,0,0)',

    )

    fig.update_layout(layout_ar)
    fig.update_layout(barmode='group', xaxis_tickangle=-45, showlegend=True)
    fig.update_xaxes(type='category', showgrid=True)
    fig.update_yaxes(title_text=title, showgrid=True, gridcolor="#E0E1DF", range=y_span)
    fig.update_layout(margin={"r": 10, "t": 10, "l": 10, "b": 10})
    return fig
    # fig.show()


@app.callback(
    [Output('bar-ar', 'figure'),
     Output('info-ar', 'children'),
     Output('header-bar-ar', 'children')],
    [Input('mem-year-ar', 'children'),
     Input('multi-tabs', 'active_tab')
     ]
)
def update_bar_ar(ano_mem, at):
    if not dash.callback_context.triggered or at != 'tab-residuais':
        raise PreventUpdate

    try:
        ano_select = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano_select = anos_cons[-1]

    layout_bar_ar = copy.deepcopy(layout)
    df = aguas_r_df[aguas_r_df.index == ano_select]
    bad_df = df.Subsistema.isin(['Total'])
    df = df[~bad_df]
    df = df[(df['Total'].T != 0)]
    df = df.loc[df.Subsistema != 'Total - Água Tratada', :]
    # df['lis_perc'] = df['Lisboa']/df['Total']*100
    # df['out_perc'] = df['Outros Concelhos']/df['Total']*100
    df = df.replace(0, np.nan)
    my_text_hover_lis = [
        '{:.2f}'.format(val) + unidade_1 + " (" + '{:.1f}'.format(perc) + "%)" + '<br>Ano: ' + str(ano_select) for
        val, perc in
        zip(list(df['Lisboa']), list(df['lis_perc']))]
    my_text_hover_out = [
        '{:.2f}'.format(val) + unidade_1 + " (" + '{:.1f}'.format(perc) + "%)" + '<br>Ano: ' + str(ano_select) for
        val, perc in
        zip(list(df['Outros Concelhos']), list(df['out_perc']))]

    my_text_show_lis = ['{:.0f}'.format(val) + 'M' for val in
                        list(df['Lisboa'])]
    my_text_show_out = ['{:.0f}'.format(val) + 'M' for val in
                        list(df['Outros Concelhos'])]

    fig = go.Figure(
        data=[
            go.Bar(
                x=df.Subsistema,
                y=df['Lisboa'],
                name="AR provenientes do Concelho de Lisboa",
                marker_color=color_dead[4],
                marker_line_color=color_live[4],
                marker_line_width=1.5,
                text=my_text_show_lis,
                hovertext=my_text_hover_lis,
                hoverinfo='text',
                textposition='outside',
                hoverlabel=dict(font=dict(family=layout['font']['family']))
            ),
            go.Bar(
                x=df.Subsistema,
                y=df['Outros Concelhos'],
                name="AR provenientes de Outros Concelhos",
                marker_color=color_dead[1],
                marker_line_color=color_live[1],
                marker_line_width=1.5,
                text=my_text_show_out,
                hovertext=my_text_hover_out,
                hoverinfo='text',
                textposition='outside',
                hoverlabel=dict(font=dict(family=layout['font']['family']))
            ),
        ]
    )

    altura_int = max(list(df.drop(['Total', 'Subsistema', 'lis_perc', 'out_perc'], axis=1).max(skipna=True)))

    fig.update_layout(layout_bar_ar)
    fig.update_layout(legend=dict(x=0.5, y=1.2))
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    fig.update_yaxes(automargin=True, range=[0, altura_int * 1.15],
                     autorange=False, fixedrange=True, showticklabels=False, title_text="Milhões de {}".format(unidade))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # fig.show()
    alcantara_perc = round(df.loc[df.Subsistema == 'Alcântara', 'Total'] / df['Total'].sum() * 100, 1).values[0]
    beirolas_perc = round(df.loc[df.Subsistema == 'Beirolas', 'Total'] / df['Total'].sum() * 100, 1).values[0]
    chelas_perc = round(df.loc[df.Subsistema == 'Chelas', 'Total'] / df['Total'].sum() * 100, 1).values[0]

    title = "Águas Residuais (AR) Tratadas, nas ETAR de Lisboa, em {0} ({1})".format(ano_select, unidade)

    text_chelas = "ETAR de Chelas ({}%, que apenas trata das águas residuais **produzidas** em Lisboa)".format(
        chelas_perc)
    texto_beirolas = "ETAR de Beirolas ({}%)".format(beirolas_perc)

    if beirolas_perc > chelas_perc:
        text_1 = texto_beirolas
        text_2 = text_chelas
    else:
        text_2 = texto_beirolas
        text_1 = text_chelas
    texto_col = dcc.Markdown('''
    _Em {0}, a ETAR de Alcântara foi responsável pelo tratamento e encaminhamento de {1}% das águas residuais **tratadas** em Lisboa, seguindo-se a {2} e a {3}._
                '''.format(ano_select, alcantara_perc, text_1, text_2))

    return fig, texto_col, title


def legend_on_off(concelho, visivel, memoria):
    if concelho == 0:
        if memoria['Outros'] == 'off':
            if visivel == 'legendonly':
                # print('Lisboa: Desligado   :::   Outros: Desilgado')
                memoria['Lisboa'] = 'off'
            else:
                # print('Lisboa: Ligado   :::   Outros: Desilgado')
                memoria['Lisboa'] = 'on'
        else:
            if visivel == 'legendonly':
                # print('Lisboa: Desligado   :::   Outros: Ligados')
                memoria['Lisboa'] = 'off'
            else:
                # print('Lisboa: Ligado   :::   Outros: Ligados')
                memoria['Lisboa'] = 'on'

    elif concelho == 1:
        if memoria['Lisboa'] == 'off':
            if visivel == 'legendonly':
                # print('Lisboa: Desligado   :::   Outros: Desilgado')
                memoria['Outros'] = 'off'
            else:
                # print('Lisboa: Desligado   :::   Outros: Ligados')
                memoria['Outros'] = 'on'
        else:
            if visivel == 'legendonly':
                # print('Lisboa: Ligado   :::   Outros: Desligado')
                memoria['Outros'] = 'off'
            else:
                # print('Lisboa: Ligado   :::   Outros: Ligados')
                memoria['Outros'] = 'on'
    else:
        memoria['Lisboa'] = 'on'
        memoria['Outros'] = 'on'

    return memoria


@app.callback(
    [
        Output('escondido', 'children'),
        Output('map-ar', 'figure'),
    ],
    [Input('mem-year-ar', 'children'),
     Input('multi-tabs', 'active_tab'),
     Input('bar-ar', 'restyleData')

     ],
    [State('escondido', 'children')]

)
def update_map_ar(ano_mem, at, restyleData, data):
    if not dash.callback_context.triggered or at != 'tab-residuais':
        raise PreventUpdate

    try:
        ano_select = int(json.loads(ano_mem))
    except (ValueError, TypeError) as e:
        ano_select = anos_cons[-1]

    df = ar_centro_df
    if ctx.triggered[0]['prop_id'] == 'bar-ar.restyleData':
        visivel = ctx.triggered[0]['value'][0]['visible'][0]
        concelho = ctx.triggered[0]['value'][1][0]

    else:
        visivel = None
        concelho = None

    try:
        memoria = json.loads(data)
    except ValueError:
        memoria = {'Lisboa': 'on', 'Outros': 'on'}

    memoria = legend_on_off(concelho, visivel, memoria)
    # print(memoria)
    bad_df = aguas_r_df.Subsistema.isin(['Total'])
    aguas_r_dff = aguas_r_df[~bad_df]
    df['Lisboa'] = aguas_r_dff.loc[aguas_r_dff.index == ano_select, 'Lisboa'].to_list()
    df['Outros Concelhos'] = aguas_r_dff.loc[aguas_r_dff.index == ano_select, 'Outros Concelhos'].to_list()
    df['Total'] = aguas_r_dff.loc[aguas_r_dff.index == ano_select, 'Total'].to_list()
    df = df.loc[df.et != 'Frielas', :]

    text_hover_base = ['<span style="font-weight:bold">ETAR</span>: ' + '{}'.format(etar) +
                       '   |   ' + '<span style="font-weight:bold">Ano</span>: ' + '{}'.format(ano_select) for etar in
                       list(df['et'])]
    text_hover_lisboa = ["<br>AR Proveniente de Lisboa: " + '{:.2f}'.format(lisboa) + unidade_1 for lisboa in
                         list(df['Lisboa'])]
    text_hover_outros = ["<br>AR Proveniente de Outros Concelhos: " + '{:.2f}'.format(outros) + unidade_1 for outros in
                         list(df['Outros Concelhos'])]
    text_hover_total = ["<br>Total: " + '{:.2f}'.format(total) + unidade_1 for total in list(df['Total'])]

    # text_hover = ['<span style="font-weight:bold">ETAR</span>: ' + '{}'.format(etar) +
    #               '   |   ' + '<span style="font-weight:bold">Ano</span>: ' + '{}'.format(ano_select) +
    #               "<br>AR Proveniente de Lisboa: " + '{:.2f}'.format(lisboa) + unidade_1 +
    #               '<br>AR Proveniente de Outros Concelhos: ' + '{:.0f}'.format(concelhos) + unidade_1 +
    #               '<br>Total: ' + '{:.0f}'.format(total) + unidade_1
    #               for etar, lisboa, concelhos, total in
    #               zip(list(df['et']), df['Lisboa'], list(df['Outros Concelhos']),
    #                   list(df['Total']))]

    if memoria['Lisboa'] == 'on':
        raio_outros = df['Lisboa'] + df['Outros Concelhos']
        info_out = 'none'
        txt_out = ''
        if memoria['Outros'] == 'on':
            text_hover = [b + l + o + t for b, l, o, t in
                          zip(text_hover_base, text_hover_lisboa, text_hover_outros, text_hover_total)]
            sel = [True, True]
        else:
            text_hover = [b + l for b, l in zip(text_hover_base, text_hover_lisboa)]
            sel = [True, False]
    else:
        raio_outros = df['Outros Concelhos']
        if memoria['Outros'] == 'on':
            text_hover = [b + o for b, o in
                          zip(text_hover_base, text_hover_outros)]
            sel = [False, True]

        else:
            text_hover = ['']
            sel = [False, False]

        info_out = 'text'
        txt_out = text_hover

    data_trace_1 = dict(
        type='scattermapbox',
        lat=df['centroid_lat'],
        lon=df['centroid_long'],
        mode='markers',
        hovertext=text_hover,
        hoverinfo='text',
        showlegend=False,
        hoverlabel=dict(font=layout['font']),
        marker=dict(size=df['Lisboa'],
                    opacity=0.8,
                    sizeref=0.5,
                    sizemin=3,
                    color=color_live[4],
                    ),

    )

    data_trace_2 = dict(
        type='scattermapbox',
        lat=df['centroid_lat'],
        lon=df['centroid_long'],
        mode='markers',
        hoverinfo=info_out,
        hovertext=txt_out,
        showlegend=False,
        # hoverlabel=dict(font=layout['font']),
        marker=dict(size=raio_outros,
                    opacity=0.8,
                    sizeref=0.5,
                    sizemin=3,
                    color=color_live[1],
                    )

    )

    layout_map = dict(mapbox_style="light", mapbox_zoom=10.8, mapbox_center={"lat": 38.760129, "lon": -9.159281},
                      mapbox_accesstoken=mapbox_access_token)
    # print(sel)
    if sel[0]:
        if sel[1]:
            traces = [data_trace_2, data_trace_1]
        else:
            traces = [data_trace_1]
    else:
        if sel[1]:
            traces = [data_trace_2]
        else:
            traces = [
                dict(
                    type='scattermapbox',
                    lat=[38.760129],
                    lon=[-9.159281],
                    mode='text',
                    hoverinfo=None,
                    showlegend=False,
                )

            ]
    # traces = [data_trace_1, data_trace_2]

    layout_map['font'] = layout['font']
    layout_map['hovermode'] = 'closest'
    fig = go.Figure(data=traces, layout=layout_map)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    title = "Águas Residuais Tratadas em {}".format(ano_select)
    return json.dumps(memoria), fig


if __name__ == '__main__':
    # app.run_server(debug=False, port = 5000, host ='0.0.0.0')
    # app.run_server(debug=True)
    app.run_server(debug=False)
