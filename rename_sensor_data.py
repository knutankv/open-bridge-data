import h5py
import glob

g_rename = dict(
    accelerometers='acceleration',
    displacement_sensors='displacement',
    anemometers='wind',
    wave_radars='wave'
    )

root = 'C:/Users/knutankv/BergsoysundData'
files = glob.glob(f'{root}/*.h5')

for file in files:
    with h5py.File(file, 'w') as hf:
        rec_names = list(hf.keys())
        rec_names = [rec_name for rec_name in rec_names if rec_names[0]!='.']
        
        for r in rec_names:
            for g in g_rename:
                if g in hf[r]:
                    hf[r][g_rename[g]] = hf[r][g]
                    del hf[r][g]