import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import pybd
from os import listdir
import os
import plotly.graph_objs as go
import numpy as np
from flask import send_from_directory
from scipy import signal
# ------------- PRE --------------
recpath = '//iktnimbus03.ivt.ntnu.no/ProcessedData_Bergsoysund/Test/' 

files = listdir(recpath)
files.remove('dash-stat-bergsoysund.mat')
statistics = pybd.loadrec(recpath + 'dash-stat-bergsoysund.mat', name='statistics', output_format='dict')

sensors_stat = list(statistics['sensor'].keys())

# ------------ INITIALIZE LAYOUT ------------
app = dash.Dash()
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# ------------ LAYOUT ------------
app.layout = html.Div(className='main', children=
    [   html.Div(id='data-cache', style={'display': 'none'}),        
        html.Link(
            href='/static/style.css',
            rel='stylesheet'
        ),

        html.Link(href='https://fonts.googleapis.com/css?family=Source+Sans+Pro',
        rel='stylesheet'),

        html.Img(src='./static/logo.png', style={'width': '250px', 'margin':'1em'}),

# Statistics and time series selection
        html.H2('Select time series'),
        html.Div(children=[
                html.Div(
                        dcc.Graph(
                            id = 'stat-plot',
                            figure = go.Figure(
                                data=[
                                    go.Scatter(x=np.arange(len(statistics['recording'])), y=statistics['sensor'][sensors_stat[0]]['std'][:,0])
                                    ],
                                layout = go.Layout(xaxis={'title': 'Recording number'}, yaxis={'tickformat': '.1e'}, height=400)
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
                        
                        html.Div(id='starttime-label', style={'margin-top': '0.5em', 'margin-bottom': '1em'}), 

                        dcc.Dropdown(
                            id='sensor-dropdown-stat',
                            options = [{'label':name, 'value':name} for name in sensors_stat],
                            value = sensors_stat[0],
                        ),
                        
                        html.Div(id='sensor-type-stat', style={'margin-top': '0.5em', 'margin-bottom': '1em'}),    
                            
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

        # html.Button('Load time series', id='load-button'), 
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
                                layout = go.Layout(xaxis={'title': 'Time [s]'}, height=400)
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
                        
                        html.Div(id='sensor-type', style={'margin-top': '0.5em', 'margin-bottom': '1em'}),    
                            
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
                                values =[1]
                            )],
                        style={'margin-top':'1em', 'margin-bottom': '1em'}   
                        ),   

                        html.H3('Selection'),
                        html.Div(children=[
                            dcc.Checklist(
                                options= [{'label': 'Mark recording for download', 'value': 'mark'}],
                                values =[]
                            )],
                        style={'margin-bottom':'1em'}   
                        ),   

                    ], className='sac'
                )
        ], className ='plot_wrapper'
        ),


# Download stuff
html.Div(children=[
            html.Div(children=[
                    html.H2('Download'),
                    dcc.RadioItems(
                        options=[
                            {'label': '20 Hz (low samplerate)', 'value': 'low'},
                            {'label': '200 Hz (high samplerate)', 'value': 'high'}
                        ],
                        value='low',
                        labelStyle={'display': 'inline-block'}
                    )],
                style={'margin-bottom': '1em'}
            ),
            
            html.Button('Download', id='download-button'),  
            html.Button('Download all marked', id='download-all-button'),

        ],  className = 'downloadstuff'
    )
])

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
                                go.Scatter(x=np.arange(len(statistics['recording'])), y=statistics['sensor'][selected_sensor][stat_quantity][:,componentix])
                                ],
                            layout = go.Layout(xaxis={'title': 'Recording number'},  yaxis={'tickformat': '.1e'}, height=400)
                        )
    return figout

# Sensor data plot
@app.callback(
    dash.dependencies.Output('sensor-data-plot', 'figure'),        # output from next function
    [dash.dependencies.Input('sensor-dropdown', 'value'),
    dash.dependencies.Input('component-dropdown', 'value'),
    dash.dependencies.Input('file-dropdown', 'value'), 
    dash.dependencies.Input('detrend-checkbox', 'values'),
    dash.dependencies.Input('psd-radio', 'value')])      # specified input given to next function
def update_figure(selected_sensor, selected_component, selected_file, detrend_state, domain):
    recording = pybd.loadrec(recpath+selected_file, output_format='struct')
    componentix = statistics['sensor'][selected_sensor]['component_names'].index(selected_component)

    try:
        y = recording.sensor[selected_sensor].data[:, componentix]
        x = recording.t.flatten()
           
        if detrend_state:
            y = signal.detrend(y)

        if domain == 'freq':
            n_windows = 20
            fs = 1/(x[1]-x[0])
            x, y = signal.welch(signal.detrend(y), fs, nperseg=len(x)/n_windows)
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
    except:
        figout = go.Figure(data=[go.Scatter(x=None, y=None)])


    return figout

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

# Date label
@app.callback(
    dash.dependencies.Output('starttime-label', 'children'),        # output from next function
    [dash.dependencies.Input('file-dropdown', 'value')])      # specified input given to next function
def update_date_label(selected_file):
    return 'Recording start time: %s' % (selected_file.split('M')[1].split('.')[0][1:-3])
 

# ----------- SERVE CSS --------------
@app.server.route('/static/<recpath>')
def static_file(recpath):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, recpath)
    
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

# ------------ RUN SERVER -------------
if __name__ == '__main__':
    app.run_server(debug=True)