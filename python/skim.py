import os
import warnings
from datetime import datetime

from dask.distributed import Client
from heptools.cms import LPC
from heptools.dataset import Dataset
from heptools.system.cluster import HTCondor
from heptools.task import create_picoaod_from_dataset, merge_chunks
from rich import print
from skim import AntiTag, TwoTag

warnings.filterwarnings('ignore', message='invalid value encountered in sqrt')

def in_fnal(file):
    return 'T1_US_FNAL_Disk' in file.site

def run_skim(base):
    dataset = Dataset.load('datasets/data_NanoAOD.json')
    create_picoaod_from_dataset(base, dataset, twotag = TwoTag()).save('datasets/skim_twotag.json')
    create_picoaod_from_dataset(base, dataset, antitag = AntiTag()).save('datasets/skim_antitag.json')

def run_merge(base):
    dataset = (Dataset.load('datasets/skim_antitag.json') +
               Dataset.load('datasets/skim_twotag.json'))
    merge_chunks(base, dataset, '1M', '0.1M').save('datasets/data_PicoAOD.json')
    os.remove('datasets/skim_antitag.json')
    os.remove('datasets/skim_twotag.json')

if __name__ == '__main__':
    start = datetime.now()
    LPC.setup_condor()
    base = LPC.eos / 'user/chuyuanl/HqqJpsi/'
    cluster = HTCondor(
        dashboard_port=10200,
        name = 'HqqJpsi_merge',
        cores = 1,
        memory = '4GB',
        inputs = [
            'config.py',
            'skim',
            'lumiMasks'
        ])
    print(cluster.check_inputs().rich)
    print(cluster.dashboard(8787))
    print(cluster.cluster.job_script())
    cluster.cluster.adapt(minimum_jobs = 0, maximum_jobs = 100)
    client = Client(cluster.cluster)
    client.forward_logging()
    run_skim(base)
    run_merge(base)
    cluster.clean()
    print((datetime.now() - start))