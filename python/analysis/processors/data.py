from __future__ import annotations

import awkward as ak
import heptools
from coffea.lumi_tools import LumiMask
from heptools.system.eos import EOS

from ..configs import *
from .common import log
from .common_ntag import *


def init_data(events: ak.Array):
    events.behavior |= heptools.behavior
    year = events.metadata['year']

    log('apply lumi mask', 'cut')
    masks = {'2016': 'Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt',
             '2017': 'Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt',
             '2018': 'Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt'}
    lumimask = LumiMask(EOS(ZHqqJpsi.lumimask_base) / masks[year])
    events = events[lumimask(events.run, events.luminosityBlock)]

    return events

class DataTwoTag(TwoTag):
    init = (init_data,)

class DataOneTag(OneTag):
    init = (init_data,)

class DataZeroTag(ZeroTag):
    init = (init_data,)