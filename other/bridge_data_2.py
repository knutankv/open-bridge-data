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

from opyndata import interface

dash_path = 'https://sandbox.zenodo.org/record/976642/files/{filename}?download=1'
download_path = dash_path + ''

app_setup = interface.AppSetup(buffered_data=True,
                               dash_path=dash_path,
                               dash_suffix='_2Hz',
                               download_suffix='_10Hz',
                               stat_suffix='_2Hz',
                               download_path=download_path)

app = app_setup.create_app()
server = app.server
    
# ------------ RUN SERVER -------------
if __name__ == '__main__':
    app.run_server(debug=True)