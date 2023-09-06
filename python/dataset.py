import numpy as np
from heptools.cms import DAS
from heptools.root.dataset import Dataset, FileList

np.finfo(np.dtype("float64"))

if __name__ == '__main__':
    data = Dataset()
    for dataset in ['Charmonium', 'DoubleMuon']:
        for period in ['A', 'B', 'C', 'D']:
            query = f'/{dataset}/Run2018{period}-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD'
            print(query)
            data.update('Data', dataset, '2018', period, 'NanoAODv9', FileList(DAS.query_dataset(query)))
    data.save('datasets/data_NanoAOD.json')
    print(data)