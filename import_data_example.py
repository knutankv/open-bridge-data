from opyndata.data_import import loadrec
from opyndata.misc import datenum_to_datetime, create_sensor_dict
from opyndata.data_import import export_from_hdf, export_from_multirec_hdf, get_stats_multi, get_stats
import h5py
import glob
import numpy as np
import json

component_dict = {'wave_radars': ['h'], 
                  'accelerometers': ['x', 'y', 'z'],
                  'anemometers': ['U']}
fname = 'C:/Users/knutankv/BergsoysundData/data_2Hz_.h5'

with h5py.File(fname, 'r') as hf:
    rec_names = list(hf.keys())
    stats = get_stats_multi(hf)
    
    # Single recording import
    # data_single = export_from_hdf(hf[rec_names[0]], component_dict=component_dict)
    # data_single = data_single.set_index('t')
    
    # Multiple recording import (example shows last 10 recs)
    # data_multiple = export_from_multirec_hdf(hf, rec_names[-10:], component_dict=component_dict, decimation_factor=100)
