from datetime import datetime
from datetime import timedelta
import numpy as np

def datenum_to_datetime(datenum):
    dt = datetime.fromordinal(int(datenum)) + timedelta(days=datenum%1) - timedelta(days = 366)
    return dt


def create_sensor_dict(hf_recording):
    sensor_groups = list(hf_recording.keys())
    sensor_dict = {}
    
    for g in sensor_groups:
        sensors = list(hf_recording[g].keys())
        g_expanded = [g]*len(sensors)
        new_dict = dict(zip(sensors, g_expanded))

        sensor_dict.update(new_dict)
        
    return sensor_dict


def time_axis(hf_recording, sensor_name, component=None, sensor_dict=None, starttime=0):
    if sensor_dict is None:
        sensor_dict = create_sensor_dict(hf_recording)
    if component is None:
        component = list(hf_recording[sensor_dict[sensor_name]][sensor_name].keys())[0]
        
    return np.linspace(0, hf_recording.attrs['duration'], len(hf_recording[sensor_dict[sensor_name]][sensor_name][component]))