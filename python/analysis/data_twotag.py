from pathlib import Path

import awkward as ak
import heptools
import heptools.hist as hs
import heptools.system.eos as io
from coffea.nanoevents import NanoAODSchema
from coffea.processor import ProcessorABC, Runner, futures_executor
from heptools.aktools import sort_field, where
from heptools.physics.object import jet, muon, select


class Data(ProcessorABC):
    def process(self, events: ak.Array):
        events = events
        fills = hs.Fill(dataset = events.metadata['dataset'], weight = 1)
        mMuMu_range = (10, 2.0, 4.0)
        mMuMuBB_range = (27, 40.0, 175.0)
        hists = hs.Hists(
            dataset = [],
            mMuMuBB = mMuMuBB_range,
            mMuMu   = mMuMu_range,
        )
        events.behavior |= heptools.behavior

        # select objects
        events['selected_muons'] = select(events.Muon,
            (abs(events.Muon.eta) < 2.4) &
            (events.Muon.pt > 3) &
            (events.Muon.softId)
        )
        events['selected_bJets'] = select(events.Jet,
            (abs(events.Jet.eta) < 2.4) &
            (events.Jet.pt > 0) &
            (events.Jet.btagDeepFlavB > 0.3),
            add_index = True)
        events['selected_bJets'] = sort_field(events.selected_bJets, 'pt')

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

        # pair
        events['diMuon'] = muon.pair(events.selected_muons, mode = 'combination')
        events['diMuon'] = events.diMuon[
            (events.diMuon.mass > 2) &
            (events.diMuon.mass < 4) &
            (events.diMuon.charge == 0)
        ]
        events['diBJet'] = jet.pair(events.selected_bJets, mode = 'combination')
        events['diBJet'] = events.diBJet[
            (events.diBJet.lead_pt.pt > 20)
        ]

        ##### cut #####
        events = events[
            (ak.num(events.diMuon) > 0) &
            (ak.num(events.diBJet) > 0)
        ]
        ###############

        # select J/psi and Z/H
        events['diMuon'] = events.diMuon[ak.argsort(abs(events.diMuon.mass - 3.1))]
        events['diBJet'] = events.diBJet[ak.argsort(ak.sum(events.diBJet.constituents.Jet.btagDeepFlavB, axis=2), ascending = False)]
        events['MuMu'] = events.diMuon[:, 0]
        events['mMuMu'] = events.MuMu.mass
        events['BB'] =  events.diBJet[:, 0]
        events['MuMuBB'] = jet.extend(events.MuMu, events.BB)
        events['mMuMuBB'] = events.MuMuBB.mass
        events['closest_jet'] = where(events.BB.lead_pt,
                                  (events.MuMu.delta_r(events.BB.lead_pt) > events.MuMu.delta_r(events.BB.subl_pt), events.BB.subl_pt))
        events['MuMu_closest'] = jet.extend(events.MuMu, events.closest_jet)
        events['leadMu_closest'] = events.MuMu.lead_pt.delta_r(events.closest_jet)
        events['sublMu_closest'] = events.MuMu.subl_pt.delta_r(events.closest_jet)

        # blind signal region
        events = events[
            (events.mMuMu < 3.0) |
            (events.mMuMu > 3.2) |
            (events.mMuMuBB < 70) |
            (events.mMuMuBB > 145)
        ]

        # histogram
        dr_r = (100, 0,   5)
        fp_r = (150, 0, 150)
        fpz_r = (150, -150, 150)
        f_r = {'pt':fp_r, 'pz':fpz_r, 'energy':fp_r, 'mass':fp_r}
        df_r = f_r | {'dr': dr_r}
        bp_r = (100, 0, 200)
        b_r = {'pt':bp_r, 'pz':bp_r, 'energy':bp_r, 'mass':mMuMuBB_range}

        fills += hs.Fourvector(('selected_muons', R'Selected $\mu$'), **f_r, count = True)
        fills += hs.Fourvector(('selected_bJets', R'Selected $b$ Jets'), **f_r, count = True)

        fills += hs.DiFourvector(('diBJet', R'$bb$'), **df_r, ht = fp_r, count = True)
        fills += hs.DiFourvector(('BB', R'Selected $bb$'), **df_r, ht = fp_r)
        fills += hs.DiFourvector(('diMuon', R'$\mu^-\mu^+$'), **(df_r | {'mass':mMuMu_range}), ht = fp_r, count = True)
        fills += hs.DiFourvector(('MuMu', R'Selected $\mu^-\mu^+$'), **(df_r | {'mass':mMuMu_range}), ht = fp_r)
        fills += hs.Fourvector(('MuMuBB', R'Selected $\mu^-\mu^+bb$'), **b_r)

        fills += hs.Fourvector(('BB.lead_pt', '$b$ leading $p_T$'), **f_r)
        fills += hs.Fourvector(('BB.subl_pt', '$b$ sub-leadling $p_T$'), **f_r)
        fills += hs.Fourvector(('MuMu.lead_pt', R'$\mu$ leading $p_T$'), **f_r)
        fills += hs.Fourvector(('MuMu.subl_pt', R'$\mu$ sub-leading $p_T$'), **f_r)

        fills += hists.add('MuMu_closest_dr', (*dr_r, ('MuMu_closest.dr', R'$closest $b$ Jet to $\mu^-\mu^+$ $\Delta R$')))
        fills += hists.add('leadMu_closest_dr', (*dr_r, ('leadMu_closest', R'closest $b$ Jet to leading $p_T$ $\mu$ $\Delta R$')))
        fills += hists.add('sublMu_closest_dr', (*dr_r, ('sublMu_closest', R'closest $b$ Jet to sub-leading $p_T$ $\mu$ Jet $\Delta R$')))
        fills += hists.add('count')

        fills(events)

        return hists.output

    def postprocess(self, accumulator):
        return super().postprocess(accumulator)


if __name__ == '__main__':
    local = True
    if local:
        from coffea.nanoevents import NanoEventsFactory
        events = NanoEventsFactory.from_root(
            '../TEMP/NanoAOD/Charmonium2018A.root',
            schemaclass = NanoAODSchema,
            metadata  = {'dataset': 'Charmonium'},
            entry_start = 0,
            entry_stop = 100_000,
        ).events()
        processor = Data()
        output = processor.process(events)
    else:
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
        io.save(f'/nobackup/HqqQuarkonium/hists.pkl.gz', output)