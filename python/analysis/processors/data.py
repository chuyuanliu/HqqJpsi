# TODO rename _p1 to obj1, _p2 to obj2
from __future__ import annotations

from operator import add

import awkward as ak
import heptools
from coffea.lumi_tools import LumiMask
from coffea.processor import ProcessorABC
from heptools.aktools import between, or_fields, set_field, where
from heptools.hist import Collection, Fill
from heptools.physics.object import Jet
from heptools.system.eos import EOS
from heptools.utils import sequence_call

from ..configs import *
from .common import (build_boson, hists_basic, log, pass_hlt, select_jet,
                     select_muon)


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

def select_antitag_jet(events: ak.Array):
    log('not b-tagged jets', 'select')
    events['NonBJet'] = events.SelectedJet[
        (events.SelectedJet.btagDeepFlavB < ZHqqJpsi.tag_DeepJetB)
    ]

    log('not c-tagged jets', 'select')
    events['NonCJet'] = events.SelectedJet[
        (events.SelectedJet.btagDeepFlavCvL < ZHqqJpsi.tag_DeepJetCvL)
        | (events.SelectedJet.btagDeepFlavCvB < ZHqqJpsi.tag_DeepJetCvB)
    ]

    return events

def build_twotag_dijet(events: ak.Array):
    log('ntags', 'check')
    set_field(events, ('ntags', 'b2_c2'), (ak.num(events.BJet) >= 2) & (ak.num(events.CJet) >= 2))
    set_field(events, ('ntags', 'b2_only'), (ak.num(events.BJet) >= 2) & (ak.num(events.CJet) <2))
    set_field(events, ('ntags', 'c2_only'), (ak.num(events.BJet) < 2) & (ak.num(events.CJet) >=2))

    log('2 b/c-tagged jets', 'cut')
    events = events[
        or_fields(events.ntags, 'b2_c2', 'b2_only', 'c2_only')
    ]

    log('b-tagged jet pairs', 'build')
    events['DiBJets'] = Jet.pair(events.BJet, mode = 'combination')
    events['DiBJets', 'tag_score'] = events.DiBJets.cumulate(add, 'btagDeepFlavB')

    log('c-tagged jet pairs', 'build')
    events['DiCJets'] = Jet.pair(events.CJet, mode = 'combination')
    events['DiCJets', 'tag_score'] = events.DiCJets.cumulate(add, 'btagDeepFlavCvB')

    log('b/c-tagged jet pairs (cc>bb)', 'select')
    events['DiJets'] = where(
        events.DiCJets,
        (events.ntags.b2_only, events.DiBJets),
    )

    return events

def build_onetag_dijet(events: ak.Array):
    log('ntags', 'check')
    set_field(events, ('ntags', 'b1_c1'), (ak.num(events.BJet) == 1) & (ak.num(events.CJet) == 1))
    set_field(events, ('ntags', 'b1_c0'), (ak.num(events.BJet) == 1) & (ak.num(events.CJet) == 0))
    set_field(events, ('ntags', 'c1_b0'), (ak.num(events.BJet) == 0) & (ak.num(events.CJet) == 1))

    log('1 b/c-tagged jet', 'cut')
    events = events[
        or_fields(events.ntags, 'b1_c1', 'b1_c0', 'c1_b0')
    ]

    log('b + not b pairs', 'build')
    events['DiBJets'] = Jet.pair(events.BJet[:, 0:1], events.NonBJet, mode = 'cartesian')
    events['DiBJets', 'tag_score'] = events.DiBJets._p2.btagDeepFlavB

    log('c + not c pairs', 'build')
    events['DiCJets'] = Jet.pair(events.CJet[:, 0:1], events.NonCJet, mode = 'cartesian')
    events['DiCJets', 'tag_score'] = events.DiCJets._p2.btagDeepFlavCvB

    log('b/c-tagged + untagged pairs (cj>bj)', 'select')
    events['DiJets'] = where(
        events.DiCJets,
        (events.ntags.b1_c0, events.DiBJets),
    )

    return events

def build_zerotag_dijet(events: ak.Array):
    log('ntags', 'check')
    set_field(events, ('ntags', 'b0_c0'), (ak.num(events.BJet) == 0) & (ak.num(events.CJet) == 0))

    log('0 b/c-tagged jet', 'cut')
    events = events[
        or_fields(events.ntags, 'b0_c0')
    ]

    log('not b/c pairs', 'build')
    events['DiJets'] = Jet.pair(events.SelectedJet, mode = 'combination')
    events['DiJets', 'tag_score'] = events.DiJets.cumulate(add, 'btagDeepFlavB')

    return events

def check_onetag(events: ak.Array):
    events['tagged_is_closest'] = events.JJ._p1.jetIdx == events.closest.jetIdx
    return events

def hists_onetag(hs: Collection):
    hs.cd()
    bins_p = {'pt': (100, 0, 200)}
    skip_p = ['mass', 'pz', 'energy']
    kwargs_p = {'bins': bins_p, 'skip': skip_p}

    f = Fill()
    f += Jet.plot(('DiJets._p2', 'untagged jet'), **kwargs_p)
    f += hs.add('tagged_is_closest',
                (('tagged_is_closest', R'tagged jet is the closest from $J/\psi$'),))
    return f

class TwoTag(ProcessorABC):
    has_SR = True
    ntags = ['b2_c2', 'b2_only', 'c2_only']
    dijet = (build_twotag_dijet,)
    hists = (hists_basic,)
    final = ()

    def process(self, events):
        ZHqqJpsi.update(Charmonium, DeepJet2018) # TODO

        events = sequence_call(
            init_data,
            pass_hlt,
            select_muon,
            select_jet,
            *self.dijet,
            build_boson,
            *self.final,
        )(events)

        if self.has_SR and ZHqqJpsi.blind:
            log('blind SR', 'cut')
            events = events[~(
                between(events.mMuMu, ZHqqJpsi.mass_mumu_SR) &
                between(events.mJJMuMu, ZHqqJpsi.mass_mumujj_SR)
            )]

        log('init', 'hist')
        f = Fill(weight = 1)
        hs = Collection(
            ntags = self.ntags,
            HLT = ZHqqJpsi.hlt + ['Failed'],
            mMuMu   = sorted([*ZHqqJpsi.mass_mumu_SB, *ZHqqJpsi.mass_mumu_SR]),
            mJJMuMu = sorted([*ZHqqJpsi.mass_mumujj_SB, *ZHqqJpsi.mass_mumujj_SR]),
        )
        f = sum((hists(hs) for hists in self.hists), f)

        log('cache', 'hist')
        f.cache(events)

        log('fill', 'hist')
        f(events)

        return hs.output

    def postprocess(self, accumulator):
        ...

class OneTag(TwoTag):
    has_SR = False
    ntags = ['b1_c1', 'b1_c0', 'c1_b0']
    dijet = (select_antitag_jet, build_onetag_dijet)
    hists = (hists_basic, hists_onetag)
    final = (check_onetag,)

class ZeroTag(TwoTag):
    has_SR = False
    ntags = ['b0_c0']
    dijet = (build_zerotag_dijet,)
    hists = (hists_basic,)
    final = ()

