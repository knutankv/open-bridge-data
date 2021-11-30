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
import requests


def temp_download(url, save_path):
    r = requests.get(url)
    open(save_path, 'wb').write(r.content)

# ------------ INITIALIZE LAYOUT ------------
app = dash.Dash(__name__)
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
server = app.server

# ------------- PRE --------------
buffered_data = True    #if url path is used (not local storage)
temp_path = 'temp.mat'

# dash_recpath = '//iktnimbus03.kt.ntnu.no/ProcessedData_Bergsoysund/DataSharing/2/' 
# dash_recpath = './recordings/'
dash_recpath = 'https://folk.ntnu.no/knutankv/recordings/bergsoysund/'
download_path = 'https://sandbox.zenodo.org/record/916289/files/{filename}.mat'

statistics = pybd.loadrec('stats.mat', name='statistics', output_format='dict')
sensors_stat = list(statistics['sensor'].keys())
files = statistics['recording']

# ------------ LAYOUT ------------
app.layout = html.Div(className='main', children=
    [   html.Div(id='buffered_file', style={'display': 'none'}, title=''),        
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
                                    go.Scatter(x=np.arange(len(statistics['recording'])), y=statistics['sensor'][sensors_stat[0]]['std'][:,0], hovertext=files)
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
                                value=[1]
                            ) ],
                        style={'margin-top':'1em', 'margin-bottom': '1em'}   
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
                                ], style={'width':'30em'}),
                            html.Div(children=[
                                dcc.Slider(
                                    id='zp-slider',
                                    min=1,
                                    max=8,
                                    step=1,
                                    marks={n:str(n) for n in range(1,8+1)},
                                    value=2
                            )
                            ], style={'width':'30em'})],        
                        style={'margin-top':'1em', 'margin-bottom': '1em'}   
                        ),                     
                            
                        html.H3('Selection')
                        # html.Div(children=[
                        #     dcc.Checklist(
                        #         options= [{'label': 'Mark recording for download', 'value': 'mark'}],
                        #         value =['mark']
                        #     )],
                        # style={'margin-bottom':'1em'})
                         
                    ], className='sac'
                )
        ], className ='plot_wrapper'
        ),


# Download stuff
html.Div(children=[
            html.Button('Download', id='download-button'),  
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
                                go.Scatter(x=np.arange(len(statistics['recording'])), y=statistics['sensor'][selected_sensor][stat_quantity][:,componentix], hovertext=files)
                                ],
                            layout = go.Layout(xaxis={'title': 'Recording number'},  yaxis={'tickformat': '.1e'}, height=400)
                        )
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
    if buffered_data:
        tot_path = temp_path + ''
        if selected_file != buffered_file:
            temp_download(dash_recpath + selected_file, temp_path)
            buffered_file = selected_file + ''
    else:
        tot_path = dash_recpath + selected_file
    
        
    recording = pybd.loadrec(tot_path, output_format='struct')
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

# @app.callback(
#     dash.dependencies.Output('download-button', 'children'),
#     [dash.dependencies.Input('file-dropdown', 'value')]
# def update_output(filename):
#     return 'The input value was "{}" and the button has been clicked {} times'.format(
#         value,
#         n_clicks
#     )
#  download_path.format(filename=download_path)

# ----------- SERVE CSS --------------
@app.server.route('/static/<recpath>')
def static_file(recpath):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, recpath)
    
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

# ------------ RUN SERVER -------------
if __name__ == '__main__':
    app.run_server(debug=True)