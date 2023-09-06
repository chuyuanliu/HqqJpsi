from heptools.config import *


class ZHqqJpsi(Config):
    mass_Jpsi: tuple[float, float] = (2.0, 4.0)

    DeepJet_CvL: float = 0.099
    DeepJet_CvB: float = 0.325
    DeepJet_B  : float = 0.2783

    pt_jet_lead: float = 20.0
    pt_jet: float = 10.0

    eta: float = 2.4