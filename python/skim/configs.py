from heptools.config import *


class LooseSkim(Config):
    mass_Jpsi: tuple[float, float] = (2.0, 4.0)

    tag_DeepJetB  : float = 0.2783 # M
    tag_DeepJetCvL: float = 0.2820 # T
    tag_DeepJetCvB: float = 0.2670 # T

    pt_jet_lead: float = 20.0
    pt_jet: float = 10.0

    eta: float = 2.4