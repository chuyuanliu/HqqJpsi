import heptools.cms.das as das
import numpy as np
from heptools.io.dataset import Dataset, FileList

np.finfo(np.dtype("float64"))

if __name__ == '__main__':
    data = Dataset()
    for dataset in ['Charmonium', 'DoubleMuon']:
        for period in ['A', 'B', 'C', 'D']:
            query = f'/{dataset}/Run2018{period}-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD'
            print(query)
            data.update('Data', dataset, '2018', period, 'NanoAOD', FileList(das.query_dataset(query)))
    data.save('./dataset/data.json')
    print(data)