import numpy as np
import scipy.io as sio
from collections import namedtuple
import pandas as pd

def avoid_ugly(arr):
    if arr.size is 1:
        arr = arr.flatten()[0]
#    elif arr.
    elif arr.dtype.name == 'object':
        value = []
        
        for val in arr[0]:
            if val.size !=0:
                value.append(val[0])
            else: 
                value.append('N/A')
        arr = value
                
    return arr


def loadrec(path, output_format='dataframe', name='recording'):
    tmp = sio.loadmat(path, squeeze_me=False, struct_as_record=True)
    tmp_rec = tmp[name][0][0] 
    
    # ------------ Sensor fields --------------- 
    sensor_names = [sname[0] for sname in tmp_rec['sensor'][0]['sensor_name']]
    sensors = dict()
    
    for sensor_ix, sensor_name in enumerate(sensor_names):
        sensor = tmp_rec['sensor'][0][sensor_ix]
        keys = [key for key in sensor.dtype.names]

        sensordict = dict()
        for key in keys:
            sensordict[key] = avoid_ugly(sensor[key])             # modify to avoid ugly nested numpy arrays
        
        if output_format.lower() == 'dict' or output_format.lower() == 'dictionary': 
            sensors[sensor_name] = sensordict
        else:
            sensors[sensor_name] = namedtuple('Struct', sensordict.keys())(*sensordict.values())           
        
    # ------------ General fields ---------------
    recording = dict()
    keys = [key for key in tmp_rec.dtype.names]
    keys.remove('sensor')

    for key in keys:
        recording[key] = avoid_ugly(tmp_rec[key])
        
    recording['sensor'] = sensors
    
    if output_format.lower() == 'dict' or output_format.lower() == 'dictionary':    
        1 #do nothing    
    elif output_format.lower() == 'dataframe' or output_format.lower() == 'df':
        recording = namedtuple('Struct', recording.keys())(*recording.values())
        data_array = np.hstack([recording.sensor[s].data for s in recording.sensor_names])

        labels = []
        for sensor in recording.sensor_names:
            labels.append([sensor+'_'+component for component in recording.sensor[sensor].component_names])
            
        labels = [item for sublist in labels for item in sublist]
        
        t = recording.t
        recording = pd.DataFrame(data=data_array, columns=labels)
        recording.insert(0, 't', t)    
    elif output_format.lower() == 'struct':  
        recording = namedtuple('Struct', recording.keys())(*recording.values())
    else:
        raise ValueError('No valid output_format is given. Valid options are "dict", "df", and "struct"')

    return recording
