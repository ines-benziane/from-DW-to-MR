import pathlib
import PIL
import pandas as pd
import numpy as np
from mutools import io
from mutools.tables import getresults

import logging
logging.basicConfig(level=logging.INFO)

# local
from mutools.utils import msquares

#
# user defined
WORK = pathlib.Path('work')
DEST = pathlib.Path('results')

# configuration file
CONFIG = pathlib.Path('config') / 'results_config.yml'

# examination 
# INDEX = 'aim.pat001.v1.20161104.legs'
# INDEX = 'aim.pat001.v2.20220426.legs'
INDEX = 'vol.3'

# METHOD
METHOD = 'dixon3pt_t2slice'
# METHOD = 't2map_3exp'


#
# other constants
INFO_SUFFIXES = ['.yml']
VOL_SUFFIXES = ['.mha', '.mhd', 'nii', '.nii.gz']

#
# load config and data
print('load config')
config = io.config.read(CONFIG)

# check method
if not METHOD in config:
    print(f'Unkown method: {METHOD}')
config = config[METHOD]

# load data
print('load data')
inputs = config['inputs']
info, volumes = {}, {}
for input in (inputs if isinstance(inputs, list) else [inputs]) if inputs is not None else []:
    datadir = WORK / INDEX / input
    for file in datadir.glob('*'):
        # load volumes
        for suffix in VOL_SUFFIXES:
            if file.name.endswith(suffix):
                name = file.name[:-len(suffix)]
                volumes[name] = io.read(file)
                continue
        # load info
        for suffix in INFO_SUFFIXES:
            if file.name.endswith(suffix):
                name = file.name[:-len(suffix)]
                info[name] = io.config.read(file)



print('load roi')
roidir = WORK / INDEX / config['roi']
print(f'roidir: {roidir.resolve()}')
print(f'exists: {roidir.exists()}')
for suffix in VOL_SUFFIXES:
    file = roidir / f'roi{suffix}'
    print(f'checking: {file} → {file.is_file()}')
    if file.is_file():
        ...



# load ROI
print('load roi')
roidir = WORK / INDEX / config['roi']
# load roi
for suffix in VOL_SUFFIXES:
    file = roidir / f'roi{suffix}'
    if file.is_file():
        roi = io.read(file)
        if roi.sum() == 0:
            print('warning: empty ROI')
        break
# load labels
labels = None
for file in roidir.glob('labels*.txt'):
    labels = io.read_labels(file)
    break



# extract results
print('compute stats')
tasks = config['variables']
suffix = config.get('suffix')
defaults = config.get('defaults', {})
reference = config.get('options', {}).get('reference')
table = getresults.extract(tasks, roi, volumes, labels=labels, defaults=defaults, reference=reference)
table.reset_index(inplace=True)

# tmp
# import matplotlib.pyplot as plt
# from mutools.utils import msquares, interpolate
# roi_ = interpolate.interpolate_roi(volumes['t2map'], roi)
# labelset = set(np.unique(roi_)) - {0}
# for i in range(roi_.shape[2]):
#     print(i)
#     plt.close('all')
#     fig = plt.figure(0)
#     plt.imshow(roi_[..., i].T, cmap='gray')
#     for label in labelset:
#         mask = roi_[..., i] == label
#         if not mask.sum():
#             continue
#         vertices = msquares.marching_squares(mask)
#         plt.plot(vertices[:, 0], vertices[:, 1])
#     fig.savefig(f'slice_{i}.png', dpi=300)

    

# store table
print('store table')
dest = DEST / f'{INDEX}_{METHOD}'
dest.mkdir(parents=True, exist_ok=True)
table.to_excel((dest / 'results').with_suffix('.xlsx'), index=False)
table.to_csv((dest / 'results').with_suffix('.csv'), index=False)

