from heptools.config import *


class LooseSkim(Config):
    mass_Jpsi: tuple[float, float] = (2.0, 4.0)

    tag_DeepJetB  : float = 0.2783
    tag_DeepJetCvL: float = 0.099
    tag_DeepJetCvB: float = 0.325

    pt_jet_lead: float = 20.0
    pt_jet: float = 10.0

    eta: float = 2.4