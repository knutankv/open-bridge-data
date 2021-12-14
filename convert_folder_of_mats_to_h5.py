from opyndata.data_import import loadrec
from opyndata.misc import datenum_to_datetime
import h5py
import glob
import numpy as np
import json

# hf.close()

#%% Initial definitions   
suffix = '2Hz'
file_str = f'C:/Users/knutankv/BergsoysundData/*{suffix}.mat'
group_dict = {
    'Miros SM-140 wave radar': 'wave_radars',
    'Trimble GNSS RTK': 'displacement_sensors',
    "'D' resolution triaxial accelerometer": 'accelerometers',
    'Windmaster Pro + AD wind sensor': 'anemometers'}

with open('./metadata/bergsoysund.json', encoding='utf-8') as f:
    project_data = json.load(f)
    
project_data['samplerate'] = '10 Hz (downsampled from 200 Hz)'
component_wise_metadata = {'component_names': None, 
                           'component_data_quality': 'data_quality',
                           'component_units': 'unit'}

recording_fields = ['duration',  'title']

#%% Find files and define initial groups
files = glob.glob(file_str)
hf = h5py.File(f'C:/Users/knutankv/BergsoysundData/data_{suffix}.h5', 'w')
files = files[-50:]
#%% Add global metadata
for field in project_data:
    hf.attrs[field] = project_data[field]

#%% Add all recordings
for path in files:
    data = loadrec(path, output_format='dict')
    rec_group = hf.create_group(data['recording'])
        
    for field in recording_fields:
        if type(data[field]) is np.str_:
            data[field] = str(data[field])
            
        rec_group.attrs[field] = data[field]
        
    rec_group.attrs['starttime'] = '-'.join(data['recording'].split('_')[0].split('-')[1:]) + 'T' + data['recording'].split('_')[1].replace('-',':')
    rec_group.attrs['name'] = str(data['recording'])
    
    for sensor in data['sensor']:
        sensor_group_name = group_dict[data['sensor'][sensor]['type']]
        if sensor_group_name not in rec_group:         
            sensor_group = rec_group.create_group(sensor_group_name)
            
        this_sensor_group = sensor_group.create_group(sensor)
        sensor_components = data['sensor'][sensor]['component_names']
        
        # Add data: component level
        for component_ix, component in enumerate(sensor_components):
            this_sensor_group.create_dataset(component, data=data['sensor'][sensor]['data'][:,component_ix])
        
        # Add metadata: sensor / component level
        sensor_metadata = data['sensor'][sensor]
        sensor_metadata.pop('data')
        sensor_metadata.pop('sensor_name')
        sensor_metadata.pop('component_names')
            
        for key in sensor_metadata:
            if type(sensor_metadata[key]) is np.str_:
                    sensor_metadata[key] = str(sensor_metadata[key])
                    
            if key in component_wise_metadata:
                for component_ix, component in enumerate(sensor_components):
                    if type(sensor_metadata[key][component_ix]) is np.str_:
                        sensor_metadata[key][component_ix] = str(sensor_metadata[key][component_ix])
                        
                    this_sensor_group[component].attrs[component_wise_metadata[key]] = sensor_metadata[key][component_ix]
            else:
                this_sensor_group.attrs[key] = sensor_metadata[key]
                
hf.close()