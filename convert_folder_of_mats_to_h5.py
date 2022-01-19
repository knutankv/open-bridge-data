from opyndata.data_import import loadrec, convert_stats
from opyndata.misc import datenum_to_datetime, create_sensor_dict_from_groups
import h5py
import glob
import numpy as np
import json

def stat_get(field, rec_name, comp_path):
    if comp_path in statistics_df[field]:
        return statistics_df[field].loc[rec_name][comp_path]
    else:
        return np.nan

#%% Initial definitions   
suffix = '10Hz'

sensor_dict = create_sensor_dict_from_groups({
    'wave_radars': ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 
                    'W1b', 'W2b', 'W3b', 'W4b', 'W5b', 'W6b'],
    'accelerometers': ['1S', '1N', '2S', '2N', '3S', '3N', '4S', '4N', '5S', 
                       '5N', '6S', '6N', '7S', '7N'],
    'anemometers': ['A0', 'A1', 'A2', 'A3', 'A4', 'A5'],
    'displacement_sensors': ['GNSS']})

group_dict = {
    'Miros SM-140 wave radar': 'wave_radars',
    'Trimble GNSS RTK': 'displacement_sensors',
    "'D' resolution triaxial accelerometer": 'accelerometers',
    'Windmaster Pro + AD wind sensor': 'anemometers'}

with open('./metadata/bergsoysund.json', encoding='utf-8') as f:
    project_data = json.load(f)
    
project_data['samplerate'] = f'{suffix} (downsampled from 200 Hz)'
component_wise_metadata = {'component_names': None, 
                           'component_data_quality': 'data_quality',
                           'component_units': 'unit'}

recording_fields = ['duration',  'title']

compression = dict()

rename_sensors = {'GNNS': 'GNSS', 
                  'P2 S': '2S', 'P2 N': '2N',
                  'P3 S': '3S', 'P3 N': '3N', 
                  'P4 S': '4S', 'P4 N': '4N',
                  'P5 S': '5S', 'P5 N': '5N'}

if len(compression)!=0:
    comp_str = '_compressed'
else:
    comp_str = ''
    
file_str = f'C:/Users/knutankv/BergsoysundData/*{suffix}.mat'

#%%
statistics = loadrec('stats.mat', name='statistics', output_format='dict')
statistics_df = convert_stats(statistics, sensor_dict=sensor_dict)
component_stat_fields = {'std': lambda rec_name, comp_path: stat_get('std', rec_name, comp_path),
                         'mean': lambda rec_name, comp_path: stat_get('mean', rec_name, comp_path)}

#%% Find files and define initial groups
files = glob.glob(file_str)

with h5py.File(f'C:/Users/knutankv/BergsoysundData/data_{suffix}{comp_str}.h5', 'w') as hf:
        
    #% Add global metadata
    for field in project_data:
        hf.attrs[field] = project_data[field]
    
    #% Add all recordings
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
            if sensor in rename_sensors:
                save_sensor_as = rename_sensors[sensor]
                data['sensor'][sensor]['sensor_name'] = sensor
            else:
                save_sensor_as = sensor+''
                           
            sensor_group_name = group_dict[data['sensor'][sensor]['type']]
            if sensor_group_name not in rec_group:         
                sensor_group = rec_group.create_group(sensor_group_name)
                
            this_sensor_group = sensor_group.create_group(save_sensor_as)
            sensor_components = data['sensor'][sensor]['component_names']
            
            # Add data: component level
            for component_ix, component in enumerate(sensor_components):
                this_sensor_group.create_dataset(component, data=data['sensor'][sensor]['data'][:,component_ix], **compression)
                # Component stats
                col_name = f'{sensor_group_name}/{save_sensor_as}/{component}'
                for field in component_stat_fields:
                    stat_f = component_stat_fields[field] # this stat function
                    this_sensor_group[component].attrs[field] = stat_f(rec_group.attrs['name'], col_name)
                
                
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
                    
            
            # Global samplerate?
            all_samplerates = [data['sensor'][sensor]['samplerate'] for sensor in data['sensor']]
    
            if all(all_samplerates == all_samplerates[0]):
                rec_group.attrs['samplerate'] = all_samplerates[0]
