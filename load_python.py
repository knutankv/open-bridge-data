import matplotlib.pyplot as plt
import numpy as np
from os import listdir
import pandas as pd
import json
import pybd

path = './recordings/'
path = r'\\iktnimbus03.ivt.ntnu.no\ProcessedData_Bergsoysund\DataSharing\10\NTNU142M-2018-02-15_14-56-50_low.mat'
#files = listdir(path)

recording = pybd.loadrec(path, output_format='dataframe')
recording_struct = pybd.loadrec(path, output_format='dict')
#sensor_components = list(recording.columns.values)
#recording.plot(x='t', y=['2S_x','2S_y', '4S_x'])

#statistics = pybd.load.loadrec('./statistics.mat', name='statistics', output_format='dict')