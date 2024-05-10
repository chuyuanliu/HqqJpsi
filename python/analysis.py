
from datetime import datetime

from analysis.processors import DataOneTag, DataTwoTag, DataZeroTag
from coffea.nanoevents import NanoAODSchema
from coffea.processor import dask_executor, run_uproot_job
from dask.distributed import Client
from heptools.cms import AAA, LPC
from heptools.dataset import Dataset
from heptools.system.cluster import HTCondor
from heptools.system.eos import EOS, save
from rich import print

if __name__ == '__main__':
    ntags = [
        (DataTwoTag, 'twotag'),
        (DataOneTag, 'twotag'),
        (DataZeroTag, 'twotag'),
        (DataOneTag, 'antitag'),
        (DataZeroTag, 'antitag'),
    ]

    start = datetime.now()
    LPC.setup_condor()
    cluster = HTCondor(
        dashboard_port=10200,
        name = 'HqqJpsi_analysis',
        cores = 1,
        memory = '8GB',
        inputs = [
            'analysis',
            'lumiMasks'
        ])
    print(cluster.check_inputs().rich)
    print(cluster.dashboard(8787))
    print(cluster.cluster.job_script())
    cluster.cluster.adapt(minimum_jobs = 1, maximum_jobs = 50)
    client = Client(cluster.cluster)
    client.forward_logging()
    client.wait_for_workers(1)
    for era in 'ABCD':
        for processor, picoAOD in ntags:
            datasets = Dataset.load('datasets/data_PicoAOD.json').subset(dataset = 'Charmonium', tier = f'picoAOD_{picoAOD}', era = era)
            inputs = {}
            for (_, dataset, year, era, _), files in datasets:
                inputs[f'{dataset}_{year}{era}'] = {
                    'files': [str(EOS(f.path, AAA.EOS_LPC)) for f in files],
                    'metadata': {
                        'year': year,
                    }
                }
            hists = run_uproot_job(
                inputs,
                treename="Events",
                processor_instance = processor(),
                executor=dask_executor,
                executor_args={
                    "client": client,
                    "schema": NanoAODSchema,
                    "align_clusters": True,
                },
                chunksize = 100_000,
            )
            save(f'hists_{processor.__name__}_2018{era}_{picoAOD}.pkl.gz', hists)
            print(datetime.now() - start, f'2018{era}', processor.__name__, picoAOD)
    cluster.clean()
    print(datetime.now() - start)