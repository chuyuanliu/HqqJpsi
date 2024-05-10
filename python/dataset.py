import numpy as np
from heptools.cms import DAS
from heptools.dataset import Dataset, FileList

np.finfo(np.dtype("float64"))


def data():
    data = Dataset()
    for dataset in ['Charmonium', 'DoubleMuon']:
        for period in ['A', 'B', 'C', 'D']:
            query = f'/{dataset}/Run2018{period}-UL2018_MiniAODv2_NanoAODv9_GT36-v1/NANOAOD'
            print(query)
            data.update('Data', dataset, '2018', period,
                        'NanoAODv9', FileList(DAS.query(dataset=query)))
    data.save('datasets/data_NanoAOD.json')
    print(data)


def mc():
    data = Dataset()
    for dataset in ['GluGluHToBB', 'GluGluHToCC']:
        query = f'/{dataset}_M-125_TuneCP5_MINLO_NNLOPS_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v*/NANOAODSIM'
        print(query)
        data.update('MC', dataset, '2018', '', 'NanoAODv9',
                    FileList(DAS.query(dataset=query)))
    data.save('mc_NanoAOD.json')
    print(data)


if __name__ == '__main__':
    mc()
