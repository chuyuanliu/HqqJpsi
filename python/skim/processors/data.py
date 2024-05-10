import awkward as ak
import heptools
from coffea.lumi_tools import LumiMask
from coffea.processor import ProcessorABC
from heptools.root import Selection
from heptools.utils import seqcall

from ..configs import LooseSkim
from .common import select_jet_loose, select_Jpsi_loose


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

class TwoTag(ProcessorABC):
    def process(self, events):
        selected = Selection()
        events = seqcall(
            init_data,
            select_Jpsi_loose,
            select_jet_loose,
        )(events)
        events['bjets'] = events.selected_jets[
                events.selected_jets.btagDeepFlavB > LooseSkim.tag_DeepJetB
            ]
        events['cjets'] = events.selected_jets[
                (events.selected_jets.btagDeepFlavCvL > LooseSkim.tag_DeepJetCvL)
            &   (events.selected_jets.btagDeepFlavCvB > LooseSkim.tag_DeepJetCvB)
            ]
        events = events[
                (ak.num(events.bjets) >= 2)
            |   (ak.num(events.cjets) >= 2)
        ]
        selected.add('twotag', True, events.run, events.luminosityBlock, events.event)
        return selected

    def postprocess(self, accumulator):
        return super().postprocess(accumulator)

class AntiTag(ProcessorABC):
    def process(self, events):
        selected = Selection()
        events = seqcall(
            init_data,
            select_Jpsi_loose,
            select_jet_loose,
        )(events)
        events['bjets'] = events.selected_jets[
                events.selected_jets.btagDeepFlavB > LooseSkim.tag_DeepJetB
            ]
        events['cjets'] = events.selected_jets[
                (events.selected_jets.btagDeepFlavCvL > LooseSkim.tag_DeepJetCvL)
            &   (events.selected_jets.btagDeepFlavCvB > LooseSkim.tag_DeepJetCvB)
            ]
        events = events[
                (ak.num(events.bjets) < 2)
            &   (ak.num(events.cjets) < 2)
        ]
        selected.add('antitag', True, events.run, events.luminosityBlock, events.event)
        return selected

    def postprocess(self, accumulator):
        return super().postprocess(accumulator)