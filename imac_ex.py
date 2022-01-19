import numpy as np

from opyndata.data_import import export_from_hdf
import h5py
import koma.oma, koma.clustering

import matplotlib.pyplot as plt
import seaborn as sns

import hdbscan

from scipy.signal import detrend

#%% ---------------- Define import -------------------------------------------
component_dict = {'accelerometers': ['x', 'y', 'z']}

fname = 'C:/Users/knutankv/BergsoysundData/data_2Hz.h5'
rec_name = 'NTNU142M-2015-12-30_03-20-21'

#%% ---------------- Import ---------------------------------------------------
with h5py.File(fname, 'r') as hf:
    df = export_from_hdf(hf[rec_name], component_dict=component_dict)
    df = df.set_index('t')
    fs = hf[rec_name].attrs['samplerate']    

#%% ---------------- OMA: SSI -------------------------------------------------
data = detrend(df.values, axis=0)

blockrows = 24
orders = np.arange(2, 200+2, 2)
weighting = 'br'
matrix_type = 'hankel'
algorithm = 'shift'

lambd, phi = koma.oma.covssi(data, fs, blockrows, orders, weighting=weighting, showinfo=False, matrix_type=matrix_type)

#%% ---------------- OMA: Clustering (automatic selection) --------------------
s = 1
stabcrit = dict(freq=0.04, damping=0.2, mac=0.1)

scaling = {'mac':1.0, 'lambda_real':2.0, 'lambda_imag':2.0}

lambd_stab, phi_stab, orders_stab, ix_stab = koma.oma.find_stable_poles(lambd, 	
     phi, orders, s, stabcrit=stabcrit, indicator='freq')

pole_clusterer = koma.clustering.PoleClusterer(lambd_stab, phi_stab, orders_stab, scaling=scaling)

#%%
prob_threshold = 0.5  
args = pole_clusterer.postprocess(prob_threshold=prob_threshold)
xi_auto, omega_n_auto, phi_auto, order_auto, probs_auto, __ = koma.clustering.group_clusters(*args)

