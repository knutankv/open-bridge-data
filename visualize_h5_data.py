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

data_path = 'C:/Users/knutankv/BergsoysundData/data_2Hz.h5'
app_setup = interface.AppSetup(data_path=data_path)

app = app_setup.create_app()
server = app.server
    
# ------------ RUN SERVER -------------
if __name__ == '__main__':
    app.run_server(debug=True)