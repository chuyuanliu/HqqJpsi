# TODO generilize
import gzip
import os
from pathlib import Path

import dill as pickle
import matplotlib.pyplot as plt
import mplhep as mpl
import numpy as np
from hist import Hist
from hist.axis import Regular
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle

plt.style.use(mpl.style.CMS)

density = True
_float_error = 1e-10

text2tex = {
    'mMuMu': R'$m_{\mu^-\mu^+}$',
    'mMuMuBB': R'$m_{\mu^-\mu^+b\bar{b}}$',
    'Mmumu': R'$m_{\mu^-\mu^+}$',
    'Mmumubb': R'$m_{\mu^-\mu^+b\bar{b}}$',
}
def latex(text: str):
    for k, v in text2tex.items():
        if text == k:
            return v
    return text

def find_bin(axis: Regular, start: float, end: float):
    edges = axis.edges
    start = (edges <= (start + _float_error))
    start = int(len(edges) - np.argmax((start)[::-1]) - 1) if np.any(start) else 0
    end = (edges >= (end - _float_error))
    end = int(np.argmax(end)) if np.any(end) else (len(edges) - 1)
    return slice(start, end, (end - start) * 1j), (edges[start], edges[end])

def plot_1d(path: Path, name: str, **hists: Hist):
    plt.figure(figsize=(16, 9), dpi=300)
    for label, hist in hists.items():
        label = label.replace("__", ", ").replace("_", " ")
        mpl.histplot(hist, label = label, density = density)
    if len(hists) > 1:
        plt.legend(fontsize = 16)
    name = name.replace(".", "/")
    if os.path.basename(name).endswith('dr'):
        plt.axvline(x = 0.3, color = 'purple')
        plt.axvline(x = 0.4, color = 'red')
        plt.axvline(x = 0.8, color = 'orange')
    path = path.joinpath(f'{name}.png')
    path.parent.mkdir(exist_ok=True, parents=True)
    mpl.cms.text('internal')
    plt.savefig(path)
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

def plot_all():
    file = 'data'
    path_plot = Path(f'./TEMP/hists/{file}{"_density" if density else ""}')
    h = pickle.load(gzip.open(f'./TEMP/hists/{file}.pkl.gz', 'rb'))
    categories = h['categories']
    h = h['hists']

    categories = {axis.name: axis for axis in next(iter(h.values())).axes if axis.name in categories}

    def projection(hist: Hist, dataset: str, **mass: tuple[float, float]):
        selection = {'dataset': dataset}
        label = []
        for m in mass:
            bins, edges = find_bin(categories[m], *mass[m])
            selection[m] = bins
            label.append(Rf'{latex(m)}$\in({edges[0]:.1f}, {edges[1]:.1f})$')
        for category in categories:
            if category not in selection:
                bins = len(categories[category])
                selection[category] = slice(0, bins, bins * 1j)
        if not label:
            label = ['all']
        return (', '.join(label),
                hist[selection][{m: 0 for m in mass}].project(*(axis.name for axis in hist.axes if axis.name not in categories)))

    regions = {
        'SB_dimu': [
            {'mMuMu': (i, i + 0.2)} for i in [*np.arange(2, 3, 0.2), *np.arange(3.2, 4, 0.2)]
        ],
        'SB_boson': [
            {'mMuMu': (2.0, 3.0), 'mMuMuBB': (70, 145)},
            {'mMuMu': (3.2, 4.0), 'mMuMuBB': (70, 145)},
        ],
        'SB_Jpsi': [
            {'mMuMu': (3.0, 3.2), 'mMuMuBB': (i, i + 5)} for i in [*np.arange(50, 70, 5), *np.arange(145, 175, 5)]
        ],
        'SB_mumubb': [
            {'mMuMuBB': (i, i + 5)} for i in [*np.arange(50, 70, 5), *np.arange(145, 175, 5)]
        ],
        'inclusive': [
            {}
        ]
        # 'SR': [{'mMuMu': (3.0, 3.2), 'mMuMuBB': (70, 145)}],
    }
    for dataset in ['Charmonium', 'DoubleMuon']:
        count = h['count'][{'dataset': dataset}]
        for region in regions:
            plot_count(path_plot.joinpath(dataset, region), 'mMuMuBB_mMuMu', count, *regions[region])
        for k in h:
            if k == 'count':
                continue
            print(dataset, k)
            for region in regions:
                plot_1d(path_plot.joinpath(dataset, region), k, **dict([projection(h[k], dataset, **r) for r in regions[region]]))
plot_all()