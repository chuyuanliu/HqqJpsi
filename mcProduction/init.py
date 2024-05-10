import os
from pathlib import Path
from urllib.request import urlopen

cmssw = Path(os.environ['CMSSW_BASE'])/'src'

# fragment

fragment_base = cmssw/'Configuration/GenProduction/python/'
fragment_base.mkdir(parents = True, exist_ok = True)

cfgs = {
    'ggHqqJPsi': [
        (4, 'GluGluHToCCJPsi_JPsiToMuMu'),
        (5, 'GluGluHToBBJPsi_JPsiToMuMu'),
    ],
    'ZqqJPsi': [
        (4, 'ZToCCJPsi_JPsiToMuMu'),
        (5, 'ZToBBJPsi_JPsiToMuMu'),
    ],
}

private_gridpack = Path('gridpack').resolve()

for interaction in ['QCD', 'EW']:
    for template, cfg in cfgs.items():
        with open(f'fragment/{template}_{interaction}.py', 'r') as f:
            fragment = f.read()
        for quark, process in cfg:
            with open(fragment_base/f'{process}_{interaction}.py', 'w') as f:
                f.write(fragment.format(quark = quark, gridpack = private_gridpack))