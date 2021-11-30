import matplotlib.pyplot as plt
import numpy as np
from os import listdir
import pandas as pd
import json
import pybd

# path = './recordings/'
# path = 'C:/Users/knutankv/Downloads/Events_Low_Wind_2013_12_08_HighFreq/Low_Wind_2013_12_08_HighFreq/HB141M-2013-12-08_09-52-02_HighFreq.mat'
# path = 'C:/Users/knutankv/Downloads/MidFreq_2014_10/2014_10/HB141M-2014-10-03_04-23-12_MidFreq.mat'
path = r'\\iktnimbus03.ivt.ntnu.no\ProcessedData_Bergsoysund\DataSharing\10\NTNU142M-2018-02-15_14-56-50_low.mat'
# files = listdir(path)

recording = pybd.loadrec(path, output_format='dataframe')
recording_struct = pybd.loadrec(path, output_format='dict')
#sensor_components = list(recording.columns.values)
recording.plot(x='t', y=['H1 East_y'])

#statistics = pybd.load.loadrec('./statistics.mat', name='statistics', output_format='dict')