import os
from collections import defaultdict
from pathlib import Path

import awkward as ak
import heptools
import heptools.io as io
from coffea.processor import (NanoAODSchema, ProcessorABC, Runner,
                              futures_executor)
from heptools.io.dataset import Dataset
from heptools.io.selection import Selection
from heptools.physics.object import muon as dimuon


class Skim(ProcessorABC):
    def process(self, events):
        dataset = events.metadata['dataset']
        selection = Selection()
        events.behavior |= heptools.behavior
        selection.add('all', events.event, True)
        events['selected_muons'] = events.Muon[abs(events.Muon.eta < 2.4)]
        events['selected_muons'] = events.selected_muons[ak.argsort(events.selected_muons.pt, ascending=False)]
        events['bJets'] = events.Jet[(events.Jet.btagDeepFlavB > 0.3) & (abs(events.Jet.eta) < 2.4)]
        events['bJets'] = events.bJets[ak.argsort(events.bJets.pt, ascending=False)]
        mu2_events = events[ak.num(events.selected_muons) >= 2]
        mu2_events['Dimu'] = dimuon.pair(mu2_events.selected_muons, mode = 'combination')
        selection.add('2mu_eta_2p4__1Jpsi_m_2GeV_4GeV', mu2_events.event, ak.any(
            (mu2_events.Dimu.mass > 2) &
            (mu2_events.Dimu.mass < 4) &
            (mu2_events.Dimu.charge == 0), axis=-1))
        b2_events = events[ak.num(events.bJets) >= 2]
        selection.add('2jet_b_0p3_eta_2p4_1pT_20GeV', b2_events.event, b2_events.bJets.pt[:,0] > 20)
        return {dataset: selection}

    def postprocess(self, accumulator):
        ...

if __name__ == '__main__':
    tag = ''
    base = '/nobackup/HqqQuarkonium/data/'
    data = Dataset().load('./dataset/data.json')
    def in_fnal(file):
        return 'T1_US_FNAL_Disk' in file.site
    base = Path(base)
    url = 'root://cmsxrootd.fnal.gov/'
    for dataset in ['Charmonium', 'DoubleMuon']:
        for era in 'ABCD':
            if not os.path.exists(base.joinpath(dataset, f'2018{era}', f'nano_skim{tag}.pkl.gz')):
                subset = data.subset(file = in_fnal, dataset = dataset, era = era)
                fileset = defaultdict(list)
                for metadata, file in subset.files:
                    _, _, year, _, _, = metadata
                    fileset[f'{dataset}/{year}/{era}/'].append(url + file)
                    base.joinpath(dataset, year, era).mkdir(parents=True, exist_ok=True)
                run = Runner(
                    executor = futures_executor(workers=4),
                    schema = NanoAODSchema,
                    chunksize = 1_000_000,
                    xrootdtimeout = 1800,
                )
                output = run(fileset, "Events", processor_instance = Skim())
                for k, v in output.items():
                    io.save(base.joinpath(k, f'nano_skim{tag}.pkl.gz'), v)
                    print(k)