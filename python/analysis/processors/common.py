import awkward as ak
import numpy as np
from heptools.aktools import (between, get_field, or_fields, set_field, sort,
                              where)
from heptools.hist import Collection, Fill
from heptools.physics.object import Jet, LorentzVector, Muon, with_index

from ..configs import ZHqqJpsi


def log(msg: str, *tags: str):
    # print(''.join(f'[{tag}]' for tag in tags), msg)
    ...

def pass_hlt(events: ak.Array):
    log('HLT', 'check')
    set_field(events, ('HLT', 'Failed'), ~or_fields(events.HLT, *ZHqqJpsi.hlt))
    return events

def select_muon(events: ak.Array):
    log('muons', 'select')
    events['SelectedMuon'] = events.Muon[
        (abs(events.Muon.eta) < ZHqqJpsi.eta)
    ]
    if ZHqqJpsi.tag_muon_cutID is not None:
        events['SelectedMuon'] = events.SelectedMuon[
            (get_field(events.SelectedMuon, ZHqqJpsi.tag_muon_cutID))
        ]

    log('muon pairs', 'build')
    events['DiMuon'] = Muon.pair(events.SelectedMuon, mode = 'combination')

    log('neutral muon pairs', 'select')
    events['DiMuonN'] = events.DiMuon[
        between(events.DiMuon.mass, ZHqqJpsi.mass_mumu_SB) &
        (events.DiMuon.charge == 0)
    ]

    log('J/psi mass muon pairs', 'select')
    events['Jpsi'] = events.DiMuon[
        between(events.DiMuon.mass, ZHqqJpsi.mass_mumu_SR)
    ]

    ##### cut #####
    log('at least 1 neutral pair', 'cut')
    events = events[
        (ak.num(events.DiMuonN) >= 1)
    ]
    ###############

    return events

def select_jet(events: ak.Array):
    log('jets', 'select')
    events['Jet'] = with_index(events.Jet)
    events['SelectedJet'] = events.Jet[
        (abs(events.Jet.eta) < ZHqqJpsi.eta) &
        (events.Jet.pt > ZHqqJpsi.pt_jet)
    ]

    log('b-tagged jets', 'select')
    events['BJet'] = events.SelectedJet[
        (events.SelectedJet.btagDeepFlavB > ZHqqJpsi.tag_DeepJetB)
    ]

    log('c-tagged jets', 'select')
    events['CJet'] = events.SelectedJet[
        (events.SelectedJet.btagDeepFlavCvL > ZHqqJpsi.tag_DeepJetCvL) &
        (events.SelectedJet.btagDeepFlavCvB > ZHqqJpsi.tag_DeepJetCvB)
    ]

    return events

def build_boson(events: ak.Array):
    'require `events.DiJets`'

    log(f'jet pairs with 1 pt > {ZHqqJpsi.pt_jet_lead} GeV', 'select')
    events['DiJets'] = events.DiJets[
        (events.DiJets.lead_pt.pt > ZHqqJpsi.pt_jet_lead)
    ]
    log(f'at least 2 jets and 1 with pt > {ZHqqJpsi.pt_jet_lead} GeV', 'cut')
    events = events[
        (ak.num(events.DiJets) >= 1)
    ]

    log('J/psi -> mu+mu-', 'build')
    events['MuMu'] = sort(events.DiMuonN, lambda x: abs(x.mass - ZHqqJpsi.mass_Jpsi), ascending = True)[:, 0]
    events['mMuMu'] = events.MuMu.mass

    log('bb/cc', 'build')
    events['JJ'] = sort(events.DiJets, 'tag_score')[:, 0:1]
    events['dr_j1'] = events.JJ._p1.delta_r(events.MuMu)
    events['dr_j2'] = events.JJ._p2.delta_r(events.MuMu)
    dr_order = events.dr_j1 > events.dr_j2
    events[ 'closest'] = where(events.JJ._p1, (dr_order, events.JJ._p2))[:, 0]
    events['farthest'] = where(events.JJ._p2, (dr_order, events.JJ._p1))[:, 0]
    dr_order = None

    log('Z/H -> bb/cc + J/psi', 'build')
    events['JMuMu'] = Jet.extend(events.MuMu, events.closest)
    events['JJMuMu'] = Jet.extend(events.JMuMu, events.farthest)
    events['mJJMuMu'] = events.JJMuMu.mass
    return events

def hists_basic(hs: Collection):
    hs.cd()
    bins_p = {'pt': (100, 0, 200)}
    skip_p = ['mass', 'pz', 'energy']
    kwargs_p = {'bins': bins_p, 'skip': skip_p}
    skip_ZH = ['pz']
    bins_m_mumu = (int(np.ptp(ZHqqJpsi.mass_mumu_SB)/0.2), *ZHqqJpsi.mass_mumu_SB)
    bins_m_jjmumu = (int(np.ptp(ZHqqJpsi.mass_mumujj_SB)/5), *ZHqqJpsi.mass_mumujj_SB)
    kwargs_mumu = {'bins': bins_p | {'mass': bins_m_mumu}, 'skip': skip_ZH}
    kwargs_ZH = {'bins': bins_p | {'mass': bins_m_jjmumu},
        'skip': skip_ZH}

    f = Fill()
    f += Muon.plot(('SelectedMuon', R'$\mu$ (selected)'), **kwargs_p)
    f += Muon.plot_pair(('DiMuon', R'$\mu\mu$'), **kwargs_mumu)
    f += Muon.plot_pair(('DiMuonN', R'$\mu^-\mu^+$'), **kwargs_mumu)
    f += Muon.plot_pair(('Jpsi', R'$m_{\mu\mu}\in' + str(ZHqqJpsi.mass_mumu_SR) + '$'), **kwargs_mumu)

    f += Jet.plot(('SelectedJet', R'jet (selected)'), **kwargs_p)
    f += Jet.plot(('BJet', R'$b$ jet'), **kwargs_p)
    f += Jet.plot(('CJet', R'$c$ jet'), **kwargs_p)
    f += Jet.plot_pair(('DiJets', R'$bb/cc$'), **kwargs_ZH)

    kwargs_mumu['skip'] += ['n']
    kwargs_ZH['skip'] += ['n']
    kwargs_p['skip'] += ['n']
    f += Jet.plot(('closest', R'closest jet to $\mu^-\mu^+$'), **kwargs_p)
    f += Jet.plot(('farthest', R'farthest jet to $\mu^-\mu^+$'), **kwargs_p)
    f += Muon.plot_pair(('MuMu', R'$\mu^-\mu^+$ ($J/\psi$ candidate)'), **kwargs_mumu)
    f += LorentzVector.plot_pair(('JMuMu', R'closest $b/c$ + $\mu^-\mu^+$ ($Z/H$ candidate)'), **kwargs_ZH)
    f += LorentzVector.plot_pair(('JJMuMu', R'$bb/cc$ + $\mu^-\mu^+$ ($Z/H$ candidate)'), **kwargs_ZH)

    f += hs.add('jet_muon',
                (0, 3, ('closest', R'Number of $J/\psi$ $\mu$ in closest jet')),
                closest = lambda x: 3 - x.JMuMu.n_unique)
    f += hs.add('dr_Jpsi_j1_j2',
                (100, 0, 5, ('dr_j1', R'$\Delta R$ between $J/\psi$ and the first jet')),
                (100, 0, 5, ('dr_j2', R'$\Delta R$ between $J/\psi$ and the second jet')))
    f += hs.add('count')

    return f