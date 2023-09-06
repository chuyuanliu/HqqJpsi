import awkward as ak
from coffea.processor import ProcessorABC
from heptools.root import Selection

from .common import init_data, select_jet_loose, select_Jpsi_loose
from .config import ZHqqJpsi


class TwoTag(ProcessorABC):
    def process(self, events):
        selected = Selection()
        events = init_data(events)
        events = select_Jpsi_loose(events)
        events = select_jet_loose(events)
        events['bjets'] = events.selected_jets[
                events.selected_jets.btagDeepFlavB > ZHqqJpsi.DeepJet_B
            ]
        events['cjets'] = events.selected_jets[
                (events.selected_jets.btagDeepFlavCvL > ZHqqJpsi.DeepJet_CvL)
            # &   (events.selected_jets.btagDeepFlavCvB > ZHqqJpsi.deepCvB)
            ]
        b_events = events[ak.num(events.bjets) >= 2]
        c_events = events[ak.num(events.cjets) >= 2]
        selected.add('twotag', True, b_events.run, b_events.luminosityBlock, b_events.event)
        selected.add('twotag', True, c_events.run, c_events.luminosityBlock, c_events.event)
        return selected

    def postprocess(self, accumulator):
        return super().postprocess(accumulator)