import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from opyndata import data_import
from os import listdir
import os
import plotly.graph_objs as go
import numpy as np
from flask import send_from_directory
from scipy import signal
import requests

def temp_download(url, save_path):
        r = requests.get(url)
        open(save_path, 'wb').write(r.content)

class AppSetup:
    def __init__(self, buffered_data=True, 
                temp_path="temp.mat",
                dash_path=None,
                download_path=None,
                stats_path="stats.mat",
                dash_suffix='_2Hz',
                download_suffix='_10Hz',
                stat_suffix='',
                logo_path=None,
                stylesheet_path="/static/style.css"):
        
        self.buffered_data = buffered_data
        self.temp_path = temp_path
        self.dash_path = dash_path
        self.download_path = download_path
        self.stats_path = stats_path
        self.logo_path = logo_path
        self.stylesheet_path = stylesheet_path 
        self.dash_suffix = dash_suffix
        self.download_suffix = download_suffix
        self.stat_suffix = stat_suffix


    def create_app(self):
        # ------------ INITIALIZE LAYOUT ------------
        app = dash.Dash(__name__)
        app.css.config.serve_locally = True
        app.scripts.config.serve_locally = True

        statistics = data_import.loadrec(self.stats_path, name='statistics', output_format='dict')
        sensors_stat = list(statistics['sensor'].keys())
        files = statistics['recording']
        files = [file.replace(self.stat_suffix, self.dash_suffix) for file in files]

        # ------------ LAYOUT ------------
        logo_html = html.Img(src=self.logo_path, style={'width': '250px', 'margin':'1em'}) if self.logo_path else []

        app.layout = html.Div(className='main', children=
            [   html.Div(id='buffered_file', style={'display': 'none'}, title=''),        
                html.Link(
                    href=self.stylesheet_path,
                    rel='stylesheet'
                ),

                html.Link(href='https://fonts.googleapis.com/css?family=Source+Sans+Pro',
                rel='stylesheet'),

                logo_html,

                # Statistics and time series selection
                html.H2('Select time series'),
                html.Div(children=[
                        html.Div(
                                dcc.Graph(
                                    id = 'stat-plot',
                                    figure = go.Figure(
                                        data=[
                                            go.Scatter(x=np.arange(len(statistics['recording'])), y=statistics['sensor'][sensors_stat[0]]['std'][:,0], hovertext=files)
                                            ],
                                        layout = go.Layout(xaxis={'title': 'Recording number'}, 
                                                        yaxis={'tickformat': '.1e'}, 
                                                        height=300,  
                                                        margin=dict(l=0,r=0,t=5,b=0))

                                    )
                                ),
                            className='plot'
                        ),

                        html.Div(children=[
                                dcc.Dropdown(
                                    id='file-dropdown',
                                    options = [{'label':name, 'value':name} for name in files],
                                    value = files[0]
                                ),
                                html.Div(style={'margin-top': '0.5em', 'margin-bottom': '1em'}),    
                                    
                                dcc.Dropdown(
                                    id='sensor-dropdown-stat',
                                    options = [{'label':name, 'value':name} for name in sensors_stat],
                                    value = sensors_stat[0],
                                ),
                                
        
                                dcc.Dropdown(
                                    id='component-dropdown-stat',
                                    options=[{'label':name, 'value':name} for name in statistics['sensor'][sensors_stat[0]]['component_names']],
                                    value=statistics['sensor'][sensors_stat[0]]['component_names'][0]
                                ),

                                html.H3('Plot type'),
                                dcc.RadioItems(
                                    id='stat-radio',
                                options=[
                                    {'label': 'Standard deviation', 'value': 'std'},
                                    {'label': 'Mean value', 'value': 'mean'}
                                ],
                                    value='std',
                                    labelStyle={'display': 'inline-block'}
                                )     
                            ], className='sac'
                        )
                ], className ='plot_wrapper'
                ),

                # Time series study
                html.H2(children=['Study time series'], className='h2'),
                html.Div(children=[
                        html.Div(
                                dcc.Graph(
                                    id = 'sensor-data-plot',
                                    figure = go.Figure(
                                        data=[
                                            go.Scatter(x=[], y=[])
                                            ],
                                        layout = go.Layout(xaxis={'title': 'Time [s]'}, height=300, margin=dict(l=0,r=0,t=20,b=0))
                                    )
                                ),
                            className='plot'
                        ),

                        html.Div(children=[
                                dcc.Dropdown(
                                    id='sensor-dropdown',
                                    options = [{'label':name, 'value':name} for name in sensors_stat],
                                    value = sensors_stat[0],
                                ),
                                

                                dcc.Dropdown(
                                    id='component-dropdown',
                                    options = [{'label':name, 'value':name} for name in statistics['sensor'][sensors_stat[0]]['component_names']],
                                    value = statistics['sensor'][sensors_stat[0]]['component_names'][0],
                                ),  

                                html.H3('Options and visualization'),

                                dcc.RadioItems(
                                    id='psd-radio',
                                    options=[
                                        {'label': 'Time history', 'value': 'time'},
                                        {'label': 'Power spectral density', 'value': 'freq'},
                                    ],
                                    value='time'
                                ),

                                html.Div(children=[
                                    dcc.Checklist(
                                        id='detrend-checkbox',
                                        options= [{'label': 'Detrend (time history)', 'value': 1}],
                                        value=[1]
                                    ) ]
                                ),  

                                html.H4('Welch estimation'),
                                html.Div(children=[

                                    html.Div(children=[
                                        dcc.Slider(
                                            id='nfft-slider',
                                            min=0,
                                            max=11-6,
                                            step=None,
                                            marks={(n-6):str(int(2**n)) for n in [6,7,8,9,10,11]},
                                            value=3
                                        )
                                        ], style={'width':'100%'}),
                                    html.Div(children=[
                                        dcc.Slider(
                                            id='zp-slider',
                                            min=1,
                                            max=8,
                                            step=1,
                                            marks={n:str(n) for n in range(1,8+1)},
                                            value=2
                                    )
                                    ], style={'width':'100%'})],         
                                ),                     
                                    
                                html.H3('Selection'),
                                html.Div(children=[
                                    dcc.Checklist(
                                        options= [{'label': 'Mark recording for download', 'value': ''}],
                                        value =['']
                                    ),
                                    html.Button('Download marked', id='download-button-all'),
                                    html.Button('Download this', id='download-button')])
                                
                            ], className='sac'
                        )
                ], className ='plot_wrapper'
                )    ])

        # ------------ CALLBACKS --------------
        # Stat plot
        @app.callback(
            dash.dependencies.Output('stat-plot', 'figure'),
            [dash.dependencies.Input('sensor-dropdown-stat', 'value'),
            dash.dependencies.Input('component-dropdown-stat', 'value'),
            dash.dependencies.Input('stat-radio', 'value')
            ]
        )
        def update_figure_stat(selected_sensor, selected_component, stat_quantity):
            componentix = statistics['sensor'][selected_sensor]['component_names'].index(selected_component)
            figout = go.Figure(
                                    data=[
                                        go.Scatter(x=np.arange(len(statistics['recording'])), y=statistics['sensor'][selected_sensor][stat_quantity][:,componentix], hovertext=files)
                                        ],
                                    layout = go.Layout(xaxis={'title': 'Recording number'},  yaxis={'tickformat': '.1e'})
                                )
            figout.update_layout(height=300, margin=dict(l=0,r=0,t=20,b=0))
            
            return figout

        # Sensor data plot
        @app.callback(
            [dash.dependencies.Output('sensor-data-plot', 'figure'),
            dash.dependencies.Output('buffered_file', 'title')],        # output from next function
            [dash.dependencies.Input('sensor-dropdown', 'value'),
            dash.dependencies.Input('component-dropdown', 'value'),
            dash.dependencies.Input('file-dropdown', 'value'), 
            dash.dependencies.Input('detrend-checkbox', 'value'),
            dash.dependencies.Input('psd-radio', 'value'),
            dash.dependencies.Input('nfft-slider', 'value'),
            dash.dependencies.Input('zp-slider', 'value'),
            dash.dependencies.Input('buffered_file', 'title')])      # specified input given to next function

        def update_figure(selected_sensor, selected_component, selected_file, detrend_state, domain, nfft, zp, buffered_file):
            if self.buffered_data:
                tot_path = self.temp_path + ''
                if selected_file != buffered_file:
                    temp_download(self.dash_path.format(filename=selected_file), self.temp_path)
                    buffered_file = selected_file + ''
            else:
                tot_path = self.dash_path.format(filename=selected_file)
                
            recording = data_import.loadrec(tot_path, output_format='struct')
            componentix = statistics['sensor'][selected_sensor]['component_names'].index(selected_component)

            try:
                y = recording.sensor[selected_sensor].data[:, componentix]
                x = recording.t.flatten()
                
                if detrend_state:
                    y = signal.detrend(y)

                if domain == 'freq':
                    fs = 1/(x[1]-x[0])
                    x, y = signal.welch(signal.detrend(y), fs, nperseg=2**(nfft+6), nfft=zp*2**(nfft+6))
                    layout = go.Layout(xaxis={'title': 'Frequency [Hz]'}, yaxis={'tickformat': '.1e'})
                else:
                    layout = go.Layout(xaxis={'title': 'Time [s]'}, yaxis={'tickformat': '.1e'})

                figout = go.Figure(
                            data=[
                                go.Scatter(x=x, y=y
                                )
                            ],
                            layout = layout
                            )
                figout.update_layout(height=300, margin=dict(l=0,r=0,t=20,b=0))
                
            except:
                figout = go.Figure(data=[go.Scatter(x=None, y=None)])

            return figout, buffered_file

        @app.callback(
            dash.dependencies.Output('file-dropdown', 'value'),
            [dash.dependencies.Input('stat-plot', 'clickData')])
        def select_file_by_click(clickData):
            if clickData:
                ix = clickData['points'][0]['pointIndex']
                load_file = files[ix]
            else:
                load_file = files[0]
            return load_file


        # Component dropdown list
        @app.callback(
            dash.dependencies.Output('component-dropdown', 'value'),       # output from next function
            [dash.dependencies.Input('sensor-dropdown', 'value')])      # specified input given to next function
        def update_component_dropdown_value(selected_sensor):
            updated_component_value = statistics['sensor'][selected_sensor]['component_names'][0]
            return updated_component_value

        @app.callback(
            dash.dependencies.Output('component-dropdown', 'options'),       # output from next function
            [dash.dependencies.Input('sensor-dropdown', 'value')])      # specified input given to next function
        def update_component_dropdown(selected_sensor):
            updated_component_options = [{'label':name, 'value':name} for name in statistics['sensor'][selected_sensor]['component_names']]
            return updated_component_options


        # Component dropdown list STAT
        @app.callback(
            dash.dependencies.Output('component-dropdown-stat', 'value'),       # output from next function
            [dash.dependencies.Input('sensor-dropdown-stat', 'value')])      # specified input given to next function
        def update_component_dropdown_value_stat(selected_sensor):
            updated_component_value = statistics['sensor'][selected_sensor]['component_names'][0]
            return updated_component_value

        @app.callback(
            dash.dependencies.Output('component-dropdown-stat', 'options'),       # output from next function
            [dash.dependencies.Input('sensor-dropdown-stat', 'value')])      # specified input given to next function
        def update_component_dropdown_stat(selected_sensor):
            updated_component_options = [{'label':name, 'value':name} for name in statistics['sensor'][selected_sensor]['component_names']]
            return updated_component_options

        @app.server.route('/static/<recpath>')
        def static_file(recpath):
            static_folder = os.path.join(os.getcwd(), 'static')
            return send_from_directory(static_folder, recpath)


        return app