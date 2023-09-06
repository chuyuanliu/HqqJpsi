import awkward as ak
from coffea.processor import ProcessorABC
from heptools.root import Selection

from .common import init_data, select_jet_loose, select_Jpsi_loose
from .config import ZHqqJpsi


class AntiTag(ProcessorABC):
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
        events = events[
            (ak.num(events.bjets) < 2) &
            (ak.num(events.cjets) < 2)
        ]
        selected.add('antitag', True, events.run, events.luminosityBlock, events.event)
        return selected

    def postprocess(self, accumulator):
        return super().postprocess(accumulator)