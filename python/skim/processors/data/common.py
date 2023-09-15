import awkward as ak
import heptools
from coffea.lumi_tools import LumiMask
from heptools.aktools import sort_field
from heptools.physics.object import muon

from ...configs import LooseSkim


def init_data(events: ak.Array):
    events.behavior |= heptools.behavior
    year = events.metadata['year']

    # apply lumi mask
    masks = {'2016': 'Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt',
             '2017': 'Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt',
             '2018': 'Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt'}
    lumimask = LumiMask(f'../lumiMasks/{masks[year]}')
    events = events[lumimask(events.run, events.luminosityBlock)]

    return events

def select_Jpsi_loose(events: ak.Array):
    events['selected_muons'] = events.Muon[abs(events.Muon.eta < LooseSkim.eta)]
    events = events[ak.num(events.selected_muons) >= 2]
    events['dimu'] = muon.pair(events.selected_muons, mode = 'combination')
    events = events[ak.any(
          (events.dimu.mass > LooseSkim.mass_Jpsi[0])
        & (events.dimu.mass < LooseSkim.mass_Jpsi[1])
        , axis = -1)]
    return events

def select_jet_loose(events: ak.Array):
    events['selected_jets'] = sort_field(events.Jet[
            (abs(events.Jet.eta < LooseSkim.eta))
        &   (events.Jet.pt > LooseSkim.pt_jet)
        ], 'pt')
    events = events[ak.num(events.selected_jets) >= 2]
    events = events[events.selected_jets.pt[:,0] > LooseSkim.pt_jet_lead]
    return events