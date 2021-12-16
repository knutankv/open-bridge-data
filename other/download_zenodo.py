import requests
     
def temp_download(url, save_path):
    r = requests.get(url)
    open(save_path, 'wb').write(r.content)
    
#%% Initial settings
filename = 'NTNU142M-2018-03-19_02-59-44_2Hz.mat'
ACCESS_TOKEN = 'qF6yzPowAhzD6B5a7afz1hZYtG5Brupbnrp3ojbpALyz7zu6yP9ybGufuhy1'

#%% Request
r = requests.get('https://sandbox.zenodo.org/api/deposit/depositions/976642/files', 
                 params={'access_token': ACCESS_TOKEN})
r_list = r.json()

#%% Establish selected
filenames = [ri['filename'] for ri in r_list]
file_ix = filenames.index(filename)

chosen_file_dict = r_list[file_ix]

#%% Alt. 1 - download
temp_download(chosen_file_dict['links']['download'], 'temp.mat')

#%% Alt. 2 - download

