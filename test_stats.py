from opyndata.data_import import loadrec, get_stats_multi_df
from opyndata.misc import datenum_to_datetime, create_sensor_dict
from opyndata.data_import import export_from_hdf, export_from_multirec_hdf, get_stats_multi, get_stats
import h5py
import numpy as np

fname = 'C:/Users/knutankv/BergsoysundData/data_2Hz.h5'
hf = h5py.File(fname, 'r')

statistics = loadrec('stats.mat', name='statistics', output_format='dict')

#%%
test_range = np.arange(5000,5500)
for ix in test_range:
    hf_mean = hf[statistics['recording'][ix]]['anemometers']['A1']['angle'].attrs['mean']
    stat_mean = statistics['sensor']['A1']['mean'][ix,0]
    
    print([hf_mean, stat_mean])