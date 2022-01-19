import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from opyndata import data_import
from opyndata.misc import create_sensor_dict, time_axis
from os import listdir
import os
import plotly.graph_objs as go
import numpy as np
from flask import send_from_directory
from scipy import signal
import requests
import h5py

def temp_download(url, save_path):
        r = requests.get(url)
        open(save_path, 'wb').write(r.content)
    

class AppSetup:
    def __init__(self, data_path,
                logo_path=None,
                stylesheet_path=None):
        
        self.data_path = data_path
        self.logo_path = logo_path
        self.stylesheet_path = stylesheet_path 
        self.hf = h5py.File(data_path, 'r')

    def create_app(self):
        # ------------ INITIALIZE LAYOUT ------------
        app = dash.Dash(__name__)
        
        if self.stylesheet_path:
            app.css.config.serve_locally = True
        else:
            app.css.config.serve_locally = False
            self.stylesheet_path = 'https://codepen.io/chriddyp/pen/bWLwgP.css'

        global_stats = self.hf['.global_stats']
        rec_names = [a.decode() for a in  global_stats['rec_names'][()]]
        
        field0 = list(global_stats.keys())[0]
        sensor_types = list(global_stats[field0].keys())
        sensor_gr0 = list(global_stats[field0].keys())[0]
        sensor0 = list(global_stats[field0][sensor_gr0].keys())[0]
        comp0 = list(global_stats[field0][sensor_gr0][sensor0].keys())[0]

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
                                            go.Scatter(x=np.arange(len(rec_names)), 
                                                       y=global_stats[field0][sensor_gr0][sensor0][comp0][()], 
                                                       hovertext=rec_names)
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
                                    options = [{'label':name, 'value':name} for name in rec_names],
                                    value = rec_names[0]
                                ),
                                
                                html.Div(style={'margin-top': '0.5em', 'margin-bottom': '1em'}),    
                                
                                dcc.Dropdown(
                                    id='sensor_group-dropdown-stat',
                                    options = [{'label':name, 'value':name} for name in sensor_types],
                                    value = sensor_types[0],
                                ),
                                
                                
                                dcc.Dropdown(
                                    id='sensor-dropdown-stat',
                                    options = [{'label':name, 'value':name} for name in global_stats[field0][sensor_gr0].keys()],
                                    value = list(global_stats[field0][sensor_gr0].keys())[0],
                                ),
                                
        
                                dcc.Dropdown(
                                    id='component-dropdown-stat',
                                    options=[{'label':name, 'value':name} for name in global_stats[field0][sensor_gr0][sensor0].keys()],
                                    value=list(global_stats[field0][sensor_gr0][sensor0].keys())[0]
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
                                    id='sensor_group-dropdown',
                                    options = [{'label':name, 'value':name} for name in global_stats[field0].keys()],
                                    value = list(global_stats[field0].keys())[0],
                                ),
                            
                                dcc.Dropdown(
                                    id='sensor-dropdown',
                                    options = [{'label':name, 'value':name} for name in global_stats[field0][sensor_gr0].keys()],
                                    value = list(global_stats[field0][sensor_gr0].keys())[0],
                                ),
                                

                                dcc.Dropdown(
                                    id='component-dropdown',
                                    options = [{'label':name, 'value':name} for name in global_stats[field0][sensor_gr0][sensor0].keys()],
                                    value = list(global_stats[field0][sensor_gr0][sensor0].keys())[0],
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
                                    
                                
                            ], className='sac'
                        )
                ], className ='plot_wrapper'
                )    ])

        # ------------ CALLBACKS --------------
        # Stat plot
        @app.callback(
            dash.dependencies.Output('stat-plot', 'figure'),
            [dash.dependencies.Input('sensor_group-dropdown-stat', 'value'),
             dash.dependencies.Input('sensor-dropdown-stat', 'value'),
            dash.dependencies.Input('component-dropdown-stat', 'value'),
            dash.dependencies.Input('stat-radio', 'value')
            ]
        )
        def update_figure_stat(selected_group, selected_sensor, selected_component, stat_quantity):
            gr = selected_group
            s = selected_sensor
            c = selected_component
            f = stat_quantity
            
            y = global_stats[f][gr][s][c][()]
            
            figout = go.Figure(
                                    data=[
                                        go.Scatter(x=np.arange(len(rec_names)), y=y, hovertext=rec_names)
                                        ],
                                    layout = go.Layout(xaxis={'title': 'Recording number'},  yaxis={'tickformat': '.1e'})
                                )
            figout.update_layout(height=300, margin=dict(l=0,r=0,t=20,b=0))
            
            return figout

        # Sensor data plot
        @app.callback(
            dash.dependencies.Output('sensor-data-plot', 'figure'),        # output from next function
            [dash.dependencies.Input('sensor_group-dropdown', 'value'),
             dash.dependencies.Input('sensor-dropdown', 'value'),
            dash.dependencies.Input('component-dropdown', 'value'),
            dash.dependencies.Input('file-dropdown', 'value'), 
            dash.dependencies.Input('detrend-checkbox', 'value'),
            dash.dependencies.Input('psd-radio', 'value'),
            dash.dependencies.Input('nfft-slider', 'value'),
            dash.dependencies.Input('zp-slider', 'value')])      # specified input given to next function

        def update_figure(selected_group, selected_sensor, selected_component, 
                          selected_file, detrend_state, domain, nfft, zp):
            gr = selected_group
            s = selected_sensor
            c = selected_component

            selected_hf = self.hf[selected_file]
            
            try:
                y = selected_hf[gr][s][c][()]
        
                t_max = selected_hf.attrs['duration']
                n = len(y)
                x = np.linspace(0, t_max, n)
    
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
                figout.add_annotation(x=0.5, y=0.5,
                    text="Requested data not available",
                    showarrow=False)

            return figout

        @app.callback(
            dash.dependencies.Output('file-dropdown', 'value'),
            [dash.dependencies.Input('stat-plot', 'clickData')])
        def select_file_by_click(clickData):
            if clickData:
                ix = clickData['points'][0]['pointIndex']
                load_file = rec_names[ix]
            else:
                load_file = rec_names[0]
            return load_file


        # Sensor dropdown list
        @app.callback(
            dash.dependencies.Output('sensor-dropdown', 'value'),       # output from next function
            [dash.dependencies.Input('sensor_group-dropdown', 'value')])      # specified input given to next function
        def update_sensor_dropdown_value(selected_group):
            updated_sensor_value = list(list(global_stats.values())[0][selected_group].keys())[0]
            return updated_sensor_value

        @app.callback(
            dash.dependencies.Output('sensor-dropdown', 'options'),       # output from next function
            [dash.dependencies.Input('sensor_group-dropdown', 'value')])      # specified input given to next function
        def update_sensor_dropdown(selected_group):
            valid_opts = list(list(global_stats.values())[0][selected_group].keys())
            updated_sensor_options = [{'label':name, 'value':name} for name in valid_opts]            
            return updated_sensor_options


        # Sensor dropdown list STAT
        @app.callback(
            dash.dependencies.Output('sensor-dropdown-stat', 'value'),       # output from next function
            [dash.dependencies.Input('sensor_group-dropdown-stat', 'value')])      # specified input given to next function
        def update_sensor_dropdown_value_stat(selected_group):
            updated_sensor_value = list(list(global_stats.values())[0][selected_group].keys())[0]
            return updated_sensor_value

        @app.callback(
            dash.dependencies.Output('sensor-dropdown-stat', 'options'),       # output from next function
            [dash.dependencies.Input('sensor_group-dropdown-stat', 'value')])      # specified input given to next function
        def update_sensor_dropdown_stat(selected_group):
            valid_opts = list(list(global_stats.values())[0][selected_group].keys())
            updated_sensor_options = [{'label':name, 'value':name} for name in valid_opts]            
            return updated_sensor_options

        # Component dropdown list
        @app.callback(
            dash.dependencies.Output('component-dropdown', 'value'),       # output from next function
            [dash.dependencies.Input('sensor_group-dropdown', 'value'),
             dash.dependencies.Input('sensor-dropdown', 'value')])      # specified input given to next function
        def update_component_dropdown_value(selected_group, selected_sensor):
            updated_component_value = list(list(global_stats.values())[0][selected_group][selected_sensor].keys())[0]
            return updated_component_value

        @app.callback(
            dash.dependencies.Output('component-dropdown', 'options'),       # output from next function
            [dash.dependencies.Input('sensor_group-dropdown', 'value'),
             dash.dependencies.Input('sensor-dropdown', 'value')])      # specified input given to next function
        def update_component_dropdown(selected_group, selected_sensor):
            valid_opts = list(list(global_stats.values())[0][selected_group][selected_sensor].keys())
            updated_component_options = [{'label':name, 'value':name} for name in valid_opts]            
            return updated_component_options


        # Component dropdown list STAT
        @app.callback(
            dash.dependencies.Output('component-dropdown-stat', 'value'),       # output from next function
            [dash.dependencies.Input('sensor_group-dropdown-stat', 'value'),
             dash.dependencies.Input('sensor-dropdown-stat', 'value')])      # specified input given to next function
        def update_component_dropdown_value_stat(selected_group, selected_sensor):
            updated_component_value = list(list(global_stats.values())[0][selected_group][selected_sensor].keys())[0]
            return updated_component_value

        @app.callback(
            dash.dependencies.Output('component-dropdown-stat', 'options'),       # output from next function
            [dash.dependencies.Input('sensor_group-dropdown-stat', 'value'),
             dash.dependencies.Input('sensor-dropdown-stat', 'value')])      # specified input given to next function
        def update_component_dropdown_stat(selected_group, selected_sensor):
            valid_opts = list(list(global_stats.values())[0][selected_group][selected_sensor].keys())
            updated_component_options = [{'label':name, 'value':name} for name in valid_opts]            
            return updated_component_options
        
        

        @app.server.route('/static/<recpath>')
        def static_file(recpath):
            static_folder = os.path.join(os.getcwd(), 'static')
            return send_from_directory(static_folder, recpath)


        return app