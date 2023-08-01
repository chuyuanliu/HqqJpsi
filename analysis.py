from pathlib import Path

import awkward as ak
import heptools
import heptools.hist as hs
import heptools.io as io
from coffea.nanoevents import NanoAODSchema
from coffea.processor import ProcessorABC, Runner, futures_executor
from heptools.aktools import where
from heptools.physics.object import jet as dijet
from heptools.physics.object import muon as dimuon
from heptools.physics.object import vector as multivector


def log(content):
    ...
    # print(datetime.now(), content)

class Gen():
    ...

class Data(ProcessorABC):
    def process(self, events: ak.Array):
        events = events
        log('initializing')
        fills = hs.Fill(dataset = events.metadata['dataset'], weight = 1)
        hists = hs.Hists(
            dataset = [],
            mMuMu   = (10, 2.0, 4.0),
            mMuMuBB = (27, 40.0, 175.0),
        )
        events.behavior |= heptools.behavior

        log('selecting objects')
        # select objects
        events['selected_muons'] = events.Muon[
            (abs(events.Muon.eta) < 2.4) &
            (events.Muon.pt > 4) &
            (events.Muon.softId)
        ]
        events['selected_bJets'] = events.Jet[
            (abs(events.Jet.eta) < 2.4) &
            (events.Jet.btagDeepFlavB > 0.3) & 
            (events.Jet.pt > 0)
        ]
        events['selected_bJets'] = events.selected_bJets[ak.argsort(events.selected_bJets.pt, ascending=False)]

        ##### cut #####
        events = events[
            (ak.num(events.selected_muons) >= 2)
        ]
        events = events[
            (ak.num(events.selected_bJets) >= 2)
        ]
        events = events[
            (events.selected_bJets.pt[:,0] > 20)
        ]
        ###############

        log('pairing')
        # pair
        events['diMuon'] = dimuon.pair(events.selected_muons, mode = 'combination')
        events['diMuon'] = events.diMuon[
            (events.diMuon.mass > 2) &
            (events.diMuon.mass < 4) &
            (events.diMuon.charge == 0)
        ]
        events['diBJet'] = dijet.pair(events.selected_bJets, mode = 'combination')
        events['diBJet'] = events.diBJet[
            (events.diBJet.lead_pt.pt > 40)
        ]

        ##### cut #####
        events = events[
            (ak.num(events.diMuon) > 0) &
            (ak.num(events.diBJet) > 0)
        ]
        ###############

        log('selecting J/psi and Z/H')
        # select J/psi and Z/H
        events['diMuon'] = events.diMuon[ak.argsort(events.diMuon.dr, ascending=False)]
        events['diBJet', 'score'] = events.diBJet.lead_pt.btagDeepFlavB + events.diBJet.subl_pt.btagDeepFlavB
        events['diBJet'] = events.diBJet[ak.argsort(events.diBJet.score, ascending=False)]

        events['Jpsi'] = events.diMuon[
            (events.diMuon.mass > 3.0) &
            (events.diMuon.mass < 3.2)
        ]
        events['Jpsi'] = events.Jpsi[ak.argsort(events.Jpsi.dr, ascending=True)]

        events['MuMu'] = where(events['Jpsi'][:, :1], (ak.num(events.Jpsi) == 0, events.diMuon[:, :1]))[:, 0]
        events['mMuMu'] = events.MuMu.mass
        events['BB'] =  events.diBJet[:, 0]
        events['MuMuBB'] = events.MuMu + events.BB
        events['mMuMuBB'] = events.MuMuBB.mass
        events['closest_jet'] = where(events.BB.lead_pt,
                                  (events.MuMu.delta_r(events.BB.lead_pt) > events.MuMu.delta_r(events.BB.subl_pt), events.BB.subl_pt))
        events['MuMu_closest'] = multivector.pair(events.MuMu, events.closest_jet)
        events['leadMu_closest'] = events.MuMu.lead_pt.delta_r(events.closest_jet)
        events['sublMu_closest'] = events.MuMu.subl_pt.delta_r(events.closest_jet)

        # blind signal region
        events = events[
            (events.mMuMu < 3.0) |
            (events.mMuMu > 3.2) |
            (events.mMuMuBB < 70) |
            (events.mMuMuBB > 145)
        ]

        log('filling histograms')
        # histogram
        dr_r = (60, 0,  6)
        fp_r = (50, 0,100)
        fm_r = (20, 0,  5)
        f_r = {'pt':fp_r, 'pz':fp_r, 'energy':fp_r, 'mass':fm_r}
        df_r = f_r | {'dr': dr_r}
        bp_r = (100, 0, 200)
        b_r = {'pt':bp_r, 'pz':bp_r, 'energy':bp_r, 'mass':bp_r}

        fills += hs.Fourvector(('selected_muons', R'Selected $\mu$'), **f_r, count = True)
        fills += hs.Fourvector(('selected_bJets', R'Selected $b$ Jets'), **f_r, count = True)

        fills += hs.DiFourvector(('diMuon', R'$\mu^-\mu^+'), **df_r, count = True)
        fills += hs.DiFourvector(('diBJet', R'$bb$'), **df_r, count = True)
        fills += hs.DiFourvector(('Jpsi', R'$J/\psi$'), **df_r, count = True)
        fills += hs.DiFourvector(('MuMu', R'$Selected \mu^-\mu^+$'), **df_r)
        fills += hs.DiFourvector(('BB', R'$Selected bb$'), **df_r)
        fills += hs.Fourvector(('MuMuBB', R'$Selected \mu^-\mu^+bb$'), **b_r)

        fills += hs.Fourvector(('BB.lead_pt', '$b$ leading $p_T$'), **f_r)
        fills += hs.Fourvector(('BB.subl_pt', '$b$ sub-leadling $p_T$'), **f_r)
        fills += hs.Fourvector(('MuMu.lead_pt', R'$\mu$ leading $p_T$'), **f_r)
        fills += hs.Fourvector(('MuMu.subl_pt', R'$\mu$ sub-leading $p_T$'), **f_r)

        fills += hists.add('MuMu_closest_dr', (*dr_r, ('MuMu_closest.dr', R'$closest $b$ Jet to $\mu^-\mu^+$ $\Delta R$')))
        fills += hists.add('leadMu_closest_dr', (*dr_r, ('leadMu_closest', R'closest $b$ Jet to leading $p_T$ $\mu$ $\Delta R$')))
        fills += hists.add('sublMu_closest_dr', (*dr_r, ('sublMu_closest', R'closest $b$ Jet to sub-leading $p_T$ $\mu$ Jet $\Delta R$')))

        fills(events)

        return hists.output
    
    def postprocess(self, accumulator):
        return super().postprocess(accumulator)


if __name__ == '__main__':
    run = Runner(
        executor = futures_executor(workers=4),
        schema = NanoAODSchema,
        chunksize = 50_000,
        xrootdtimeout = 1800,
    )
    base = '/nobackup/HqqQuarkonium/data/'
    base = Path(base)
    files = {dataset: {
        'files': [str(base.joinpath(dataset, f'2018{era}', 'picoAOD.root')) for era in 'ABCD']
    } for dataset in ['Charmonium', 'DoubleMuon']}
    output = run(files, "Events", processor_instance = Data())
    log(f'saving histograms')
    io.save(f'/nobackup/HqqQuarkonium/hists.pkl.gz', output)