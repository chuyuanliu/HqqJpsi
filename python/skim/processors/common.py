import awkward as ak
from heptools.aktools import sort
from heptools.physics.object import muon

from ..configs import LooseSkim


def select_Jpsi_loose(events: ak.Array):
    events['selected_muons'] = events.Muon[abs(events.Muon.eta) < LooseSkim.eta]
    events = events[ak.num(events.selected_muons) >= 2]
    events['dimu'] = muon.pair(events.selected_muons, mode = 'combination')
    events = events[ak.any(
          (events.dimu.mass > LooseSkim.mass_Jpsi[0])
        & (events.dimu.mass < LooseSkim.mass_Jpsi[1])
        , axis = -1)]
    return events

def select_jet_loose(events: ak.Array):
    events['selected_jets'] = sort(events.Jet[
            (abs(events.Jet.eta) < LooseSkim.eta)
        &   (events.Jet.pt > LooseSkim.pt_jet)
        ], 'pt')
    events = events[ak.num(events.selected_jets) >= 2]
    events = events[events.selected_jets.pt[:,0] > LooseSkim.pt_jet_lead]
    return events