# TODO generilize
import gzip
import os
import pickle
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import mplhep as mpl
import numpy as np
from analysis.configs import Charmonium
from hist import Hist
from hist.axis import Regular, Variable
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle

HLT_all = Charmonium.hlt + ['Failed']
ntags_all = {
    'TwoTag_2018': ['b2_c2', 'b2_only', 'c2_only'],
    'OneTag_2018': ['b1_c1', 'b1_c0', 'c1_b0'],
    'ZeroTag_2018': ['b0_c0'],
}


warnings.filterwarnings('ignore')
plt.style.use(mpl.style.CMS)
plt.rcParams.update({
    "text.usetex": True,
})
density = True
_float_error = 1e-10

text2tex = {
    'mMuMu': R'$m_{\mu^-\mu^+}$',
    'mJJMuMu': R'$m_{\mu^-\mu^+jj}$',
    'Mmumu': R'$m_{\mu^-\mu^+}$',
    'Mjjmumu': R'$m_{\mu^-\mu^+jj}$',
}
blinded = ['TwoTag_2018']
def latex(text: str):
    for k, v in text2tex.items():
        if text == k:
            return v
    if '$\mu\mu ' in text: # TODO Temp fix
        text = text.replace('$\mu\mu ', R'$\mu^-\mu^+$ ')
    return text

def find_bin(axis: Regular | Variable, start: float, end: float):
    edges = axis.edges
    start = (edges <= (start + _float_error))
    start = int(len(edges) - np.argmax((start)[::-1]) - 1) if np.any(start) else 0
    end = (edges >= (end - _float_error))
    end = int(np.argmax(end)) if np.any(end) else (len(edges) - 1)
    if start == end:
        return start, (edges[start], edges[end])
    else:
        return slice(start, end, (end - start) * 1j), (edges[start], edges[end])

def plot_1d(path: Path, name: str, rotate: bool = None, **hists: Hist):
    plt.figure(figsize=(16, 9), dpi=300)
    for label, hist in hists.items():
        for axis in hist.axes:
            axis.label = latex(axis.label)
        label = label.replace("__", ", ").replace("_", " ")
        mpl.histplot(hist, label = label, density = density)
    if rotate is not None:
        ax = plt.gca()
        ax.set_xticklabels(ax.get_xticklabels(), rotation = rotate, va='center', position=(0,-0.05))
    if len(hists) > 1:
        plt.legend(fontsize = 16)
    name = name.replace(".", "/")
    if os.path.basename(name).endswith('dr'):
        plt.axvline(x = 0.3, color = 'purple')
        plt.axvline(x = 0.4, color = 'red')
        plt.axvline(x = 0.8, color = 'orange')
    hist_path = path.joinpath(f'{name}.png')
    hist_path.parent.mkdir(exist_ok=True, parents=True)
    mpl.cms.text('internal')
    plt.savefig(hist_path)
    plt.close()

def plot_2d(path: Path, name: str, **hists: Hist):
    plt.figure(figsize=(16, 9), dpi=200)
    name = name.replace(".", "/")
    for label, hist in hists.items():
        for axis in hist.axes:
            axis.label = latex(axis.label)
        mpl.hist2dplot(hist, label = label)
        mpl.cms.text('internal')
        hist_path = path.joinpath(f'{name}__{label}.png')
        hist_path.parent.mkdir(exist_ok=True, parents=True)
        plt.savefig(hist_path)
        plt.close()

def plot_count(path: Path, name: str, hist: Hist, *rects: dict[str, tuple[float, float]]):
    plt.figure(figsize=(16, 9), dpi=300)
    ax = plt.gca()
    hist = hist.copy()
    for axis in hist.axes:
        axis.label = latex(axis.label)
    mpl.hist2dplot(hist, norm = LogNorm())
    ranges = {axis.name: (axis.edges[0], axis.edges[-1]) for axis in hist.axes}
    for rect in rects:
        rect = ranges | rect
        rect = Rectangle(tuple(rect[axis.name][0] for axis in hist.axes), *(rect[axis.name][1] - rect[axis.name][0] for axis in hist.axes), linewidth=3, edgecolor='r', facecolor='none', hatch='X', zorder=10)
        ax.add_patch(rect)
    name = name.replace(".", "/")
    path = path.joinpath(f'{name}.png')
    path.parent.mkdir(exist_ok=True, parents=True)
    mpl.cms.text('internal')
    plt.savefig(path)
    plt.close()

def plot_all(file):
    path_plot = Path(f'../TEMP/hists/fig/{file}{"_density" if density else ""}')
    h = pickle.load(gzip.open(f'../TEMP/hists/packed/hists_{file}.pkl.gz', 'rb'))
    categories = h['categories']
    h: dict[str, Hist] = h['hists']

    categories = {axis.name: axis for axis in h['count'].axes if axis.name in categories}

    def projection(hist: Hist, selection: dict[str, str], **mass: tuple[float, float]):
        for m in mass:
            bins = find_bin(categories[m], *mass[m])[0]
            selection[m] = bins
        choose = {}
        for category in categories:
            if category not in selection:
                bins = len(categories[category])
                selection[category] = slice(0, bins, bins * 1j)
                choose[category] = 0
        hist = hist[selection]
        for k in selection:
            if isinstance(selection[k], slice):
                choose[k] = 0
        if choose:
            hist = hist[choose]
        return hist

    regions = {
        'SB_boson_mass': {'mMuMu': (2.0, 4.0), 'mJJMuMu': (70, 145)},
        'SB_Jpsi_mass': {'mMuMu': (3.0, 3.2), 'mJJMuMu': (50, 200)},
        'inclusive': {},
        'SR': {'mMuMu': (3.0, 3.2), 'mJJMuMu': (70, 145)},
    }
    count_cat = h['count'][
        {'mMuMu': slice(0, 3, 3j), 'mJJMuMu': slice(0, 3, 3j)}][
        {'mMuMu': 0, 'mJJMuMu': 0}
    ]
    plot_1d(path_plot, 'HLT', rotate = 10, HLT = count_cat.project('HLT'))
    plot_1d(path_plot, 'HLT_ntags', rotate = 10, **{ntags: count_cat[{'ntags': ntags}].project('HLT') for ntags in ntags_all[file]})
    plot_1d(path_plot, 'ntags_HLT', **{hlt: count_cat[{'HLT': hlt}].project('ntags') for hlt in HLT_all})
    for hlt in HLT_all:
        count = h['count'][{'HLT': hlt}].project('mJJMuMu', 'mMuMu')
        for region in regions:
            plot_count(path_plot.joinpath(hlt, region), 'mJJMuMu_mMuMu', count, regions[region])
        for k in h:
            if k == 'count':
                continue
            if len(h[k].axes) == len(categories) + 1:
                plot = plot_1d
            elif len(h[k].axes) == len(categories) + 2:
                plot = plot_2d
            else:
                continue
            for region in regions:
                if region == 'SR' and file in blinded:
                    continue
                plot(path_plot.joinpath(hlt, region), k, **{ntags: projection(h[k], {'HLT': hlt, 'ntags': ntags}, **regions[region]) for ntags in ntags_all[file]})

for file in ['TwoTag_2018', 'OneTag_2018', 'ZeroTag_2018']:
    plot_all(file)