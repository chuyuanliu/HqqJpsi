import datetime
from pathlib import Path

import heptools.io as io
import psutil
from heptools.io.dataset import Dataset
from heptools.io.selection import Selection
from heptools.io.skim import PicoAOD

if __name__ == '__main__':
    process = psutil.Process()
    tag = ''
    base = '/nobackup/HqqQuarkonium/data/'
    data = Dataset().load('./dataset/data.json')
    def in_fnal(file):
        return 'T1_US_FNAL_Disk' in file.site
    url = 'root://cmsxrootd.fnal.gov/'
    for dataset in ['Charmonium', 'DoubleMuon']:
        for era in 'ABCD':
            output = Path(base).joinpath(dataset, f'2018{era}')
            output.mkdir(parents = True, exist_ok = True)
            selection: Selection = io.load(output.joinpath(f'nano_skim{tag}.pkl.gz'))['[all]&[2mu_eta_2p4__1Jpsi_m_2GeV_4GeV]&[2jet_b_0p3_eta_2p4_1pT_20GeV]']
            filelist = []
            subset = data.subset(file = in_fnal, dataset = dataset, era = era)
            total = sum(sum(file.events for file in files.files) for _, files in subset)
            print(datetime.datetime.now())
            def select(x):
                global start, n_selected, n_finished
                n_finished += len(x)
                selected = x[selection(x['event'])]
                n_selected += len(selected)
                percentage = n_finished/total
                current = datetime.datetime.now()
                expected = start + (current - start)/percentage
                print('processed', f'{percentage*100:.3g}%', f'efficiency={n_selected/n_finished*100:.3g}%', 'will finish at', expected, 'RAM', f'{process.memory_info().rss/1024**3:.3g}', 'GB')
                return selected
            for _, file in subset.files:
                filelist.append(url + file)
                print(url + file)
            picoaod_path = output.joinpath(f'picoAOD{tag}.root')
            print('creating', picoaod_path)
            start = datetime.datetime.now()
            n_finished = 0
            n_selected = 0
            PicoAOD(filelist, str(picoaod_path), selection = select, iterate_step = 200_000)
            print('created', picoaod_path)