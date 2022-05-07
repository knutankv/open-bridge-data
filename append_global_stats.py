from opyndata.data_import import load_matlab_rec as loadrec, get_stats_multi
from opyndata.misc import datenum_to_datetime, create_sensor_dict, create_sensor_dict_from_groups
from opyndata.data_import import export_from_hdf, export_from_multirec_hdf, get_stats_multi, get_stats

import h5py
import glob
import numpy as np
import json

# fname = 'C:/Users/knutankv/BergsoysundData/data_10Hz.h5'
# fname = 'C:/Users/knutankv/GjemnessundData/data_10Hz.h5'
fname = 'C:/Users/knutankv/HardangerData/data_10Hz.h5'

#%% Get all statistics
with h5py.File(fname, 'a') as hf:
    
    rec_names = list(hf.keys())
    
    if '.global_stats' in rec_names:
        rec_names.remove('.global_stats')
        del hf['.global_stats']
    
    all_stats = get_stats_multi(hf, avoid=[])
    
    global_stats = hf.create_group('.global_stats') 
    global_stats.create_dataset('rec_names', data=np.array(rec_names, dtype='S'))
    
    fields = list(all_stats.keys())    
    for field in fields:
        field_group = global_stats.create_group(field)
        for comp_path in all_stats[field]:
            field_group.create_dataset(comp_path, data=all_stats[field][comp_path].values)
        