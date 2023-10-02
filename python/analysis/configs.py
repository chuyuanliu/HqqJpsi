from typing import Optional

from heptools.config import *
from heptools.system.eos import PathLike


class ZHqqJpsi(Config):
    blind: bool = True

    mass_Jpsi: const[float] = 3.1
    mass_H: const[float] = 125.0
    mass_Z: const[float] = 91.2

    tag_DeepJetB  : float = Undefined
    tag_DeepJetCvL: float = Undefined
    tag_DeepJetCvL_Loose: float = Undefined
    tag_DeepJetCvB: float = Undefined
    tag_muon_cutID: Optional[str] = 'softId'

    pt_jet_lead: float = 20.0
    pt_jet: float = 10.0
    pt_muon: float = 0.0
    eta: float = 2.4

    mass_mumu_SR  : tuple[float, float] = (3.0, 3.2)
    mass_mumujj_SR: tuple[float, float] = (70.0, 145.0)
    mass_mumu_SB  : tuple[float, float] = (2.0, 4.0)
    mass_mumujj_SB: tuple[float, float] = (50.0, 200.0)

    hlt: list[str] = Undefined

    lumimask_base: PathLike = 'lumiMasks/'

class DeepJet2018(ZHqqJpsi):
    tag_DeepJetB   = 0.2783 # M
    tag_DeepJetCvL = 0.2820 # T
    tag_DeepJetCvB = 0.2670 # T

class Charmonium(ZHqqJpsi):
    hlt = [
        'Dimuon0_Jpsi3p5_Muon2',
        # 'Dimuon25_Jpsi_noCorrL1',
        'Dimuon25_Jpsi',
        # 'DoubleMu2_Jpsi_DoubleTkMu0_Phi',
        # 'DoubleMu2_Jpsi_DoubleTrk1_Phi1p05',
        'DoubleMu4_JpsiTrkTrk_Displaced',
        'DoubleMu4_JpsiTrk_Displaced',
    ]

class DoubleMuon(ZHqqJpsi):
    hlt = [
        'DoubleL2Mu23NoVtx_2Cha',
        # 'DoubleL2Mu25NoVtx_2Cha',
        'DoubleL2Mu50',
        'DoubleMu33NoFiltersNoVtxDisplaced',
        # 'DoubleMu40NoFiltersNoVtxDisplaced',
        'DoubleMu43NoFiltersNoVtx',
        # 'DoubleMu48NoFiltersNoVtx',
        'Mu37_TkMu27',
    ]