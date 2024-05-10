from optparse import OptionParser
from pathlib import Path

years = ['2018', '2017', '2016postVFP', '2016preVFP']

def write(text, *files):
    for file in files:
        file.write(text)

def cond(param, step, year):
    if (step, year) in param:
        return param[step, year]
    elif year in param:
        return param[year]
    elif step in param:
        return param[step]
    else:
        return param[None]

pack = ['fragment', 'gridpack', 'init.py']

# CMSSW
CMSSW = {
    None: ('CMSSW_10_6_30', 'slc7_amd64_gcc700'),
    ('HLT', '2018'): ('CMSSW_10_2_16_UL', 'slc7_amd64_gcc700'),
    ('HLT', '2017'): ('CMSSW_9_4_14_UL_patch1', 'slc7_amd64_gcc630'),
    ('HLT', '2016postVFP'): ('CMSSW_8_0_36_UL_patch1', 'slc7_amd64_gcc530'),
    ('HLT', '2016preVFP'): ('CMSSW_8_0_36_UL_patch1', 'slc7_amd64_gcc530'),
}

# era
eras = {
    '2018': 'Run2_2018',
    '2017': 'Run2_2017',
    '2016postVFP': 'Run2_2016',
    '2016preVFP': 'Run2_2016_HIPM',
    ('HLT', '2016preVFP'): 'Run2_2016',
}

for key in years:
    eras['NanoAODv9', key] = eras[key] + ',run2_nanoAOD_106Xv2'

# global tag
GT = {
    '2018': '106X_upgrade2018_realistic_v16_L1v1',
    '2017': '106X_mc2017_realistic_v10',
    '2016postVFP': '106X_mcRun2_asymptotic_v17',
    '2016preVFP': '106X_mcRun2_asymptotic_preVFP_v11',
    ('HLT', '2018'): '102X_upgrade2018_realistic_v15',
    ('HLT', '2017'): '94X_mc2017_realistic_v15',
    ('HLT', '2016postVFP'): '80X_mcRun2_asymptotic_2016_TrancheIV_v6',
    ('HLT', '2016preVFP'): '80X_mcRun2_asymptotic_2016_TrancheIV_v6',
}

# eventcontent, datatier, step, extra
steps = {
    'LHEGEN':       ['RAWSIM,LHE',      'GEN,LHE',      'LHE,GEN',                          []],
    'SIM':          ['RAWSIM',          'GEN-SIM',      'SIM',                              []],
    'GENSIM':       ['RAWSIM',          'GEN-SIM',      'GEN,SIM',                          []],
    'DIGI':         ['PREMIXRAW',       'GEN-SIM-DIGI', 'DIGI,DATAMIX,L1,DIGI2RAW',         [
        '--procModifiers premix_stage2',
        '--datamix PreMix',
    ]],
    'HLT':          ['RAWSIM',          'GEN-SIM-RAW',  'HLT:{HLT}',                        [
        "--customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)'",
    ]],
    'RECO':         ['AODSIM',          'AODSIM',       'RAW2DIGI,L1Reco,RECO,RECOSIM,EI',  []],
    'MiniAODv2':    ['MINIAODSIM',      'MINIAODSIM',   'PAT',                              [
        '--procModifiers run2_miniAOD_UL',
    ]],
    'NanoAODv9':    ['NANOAODSIM',      'NANOAODSIM',   'NANO',                             []],
}

def copy_step(step, year = None):
    if year is None:
        for year in years:
            copy_step(step, year)
    else:
        steps[step, year] = steps[step].copy()
        steps[step, year][-1] = steps[step][-1].copy()

for step in {'SIM', 'DIGI', 'RECO', 'MiniAODv2'}:
    steps[step][-1] += ['--runUnscheduled']

for step in {*steps.keys()} - {'NanoAODv9'}:
    steps[step][-1] += ['--geometry DB:Extended']

# HLT menu
HLT = {
    '2018': '2018v32',
    '2017': '2e34v40',
    '2016postVFP': '25ns15e33_v4',
    '2016preVFP': '25ns15e33_v4',
}
for step in {'HLT'}:
    copy_step(step)
    for year in years:
        steps[step, year][2] = steps[step, year][2].format(HLT = cond(HLT, step, year))
    for year in ['2016preVFP', '2016postVFP']:
        steps[step, year][-1] += [
            '--outputCommand "keep *_mix_*_*,keep *_genPUProtons_*_*"',
            '--inputCommands "keep *","drop *_*_BMTF_*","drop *PixelFEDChannel*_*_*_*"',
        ]

# pileup
PU = {
    '2018': 'dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL18_106X_upgrade2018_realistic_v11_L1v1-v2/PREMIX',
    '2017': 'dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL17_106X_mc2017_realistic_v6-v3/PREMIX',
    '2016postVFP': 'dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL16_106X_mcRun2_asymptotic_v13-v1/PREMIX',
    '2016preVFP': 'dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL16_106X_mcRun2_asymptotic_v13-v1/PREMIX',
}
for step in {'DIGI'}:
    copy_step(step)
    for year in years:
        steps[step, year][-1] += [f'--pileup_input "{cond(PU, step, year)}"']

# beamspot
BS = {
    '2018': 'Realistic25ns13TeVEarly2018Collision',
    '2017': 'Realistic25ns13TeVEarly2017Collision',
    '2016postVFP': 'Realistic25ns13TeV2016Collision',
    '2016preVFP': 'Realistic25ns13TeV2016Collision',
}
for step in {'LHEGEN', 'SIM', 'GENSIM'}:
    copy_step(step)
    for year in years:
        steps[step, year][-1] += [f'--beamspot {cond(BS, step, year)}']

sequence = {
    'powheg':   ['LHEGEN', 'SIM'],
    'pythia8':  ['GENSIM'],
    'detector': ['DIGI', 'HLT', 'RECO', 'MiniAODv2', 'NanoAODv9'],
}

parser = OptionParser()
parser.add_option('-y', '--year', default = '2018')
parser.add_option('-n', '--nevents', default = '1000')
parser.add_option('-i', '--input', default = None)
parser.add_option('-o', '--output', default = '.')
parser.add_option('-s', '--sequence', default = 'powheg', help = 'powheg,pythia8')
parser.add_option('-f', '--file', default = 'NanoAODv9')
o, a = parser.parse_args()

# input
if o.input is None:
    raise ValueError('Please specify the input process name')
else:
    generator = f'Configuration/GenProduction/python/{o.input}.py'
    process = o.input

# script
tmp = Path(f'tmp_{process}_{o.year}')
tmp.mkdir(parents = True, exist_ok = True)
tmp = tmp.resolve()

# output
output_path = Path(o.output).resolve()
output_file = {*o.file.split(',')}
# TODO copy output to output directory

# cfg
def cmsdriver(step, filein):
    eventcontent, datatier, driver_step, extra = cond(steps, step, o.year)
    cfg = f'{step}_cfg.py'
    fileout = f"{tmp/step}.root"
    return ' '.join([
        'cmsDriver.py',
        f'--filein file:{filein}' if filein else generator,
        f'-n {-1 if filein else o.nevents}',
        f'--fileout file:{fileout}',
         '--customise Configuration/DataProcessing/Utils.addMonitoring',
         '--no_exec',
         '--mc',
        f'--conditions {cond(GT, step, o.year)}',
        f'--python_filename {cfg}',
        f'--eventcontent {eventcontent}',
        f'--datatier {datatier}',
        f'--step {driver_step}',
        f'--era {cond(eras, step, o.year)}',
        *extra,
    ]), cfg, fileout, cond(CMSSW, step, o.year)

cfgs = []
for step in sequence[o.sequence] + sequence['detector']:
    if cfgs:
        filein = cfgs[-1][2]
    else:
        filein = None
    cfgs.append(cmsdriver(step, filein))
init_cmssw = {cfg[-1] for cfg in cfgs}

# script

def create_cmssw(ver, arch):
    return ''.join([
        f'export SCRAM_ARCH={arch}\n',
        f'if [ -r {ver}/src ] ; then\n',
        f'  echo release {ver} already exists\n',
        f'else\n',
        f'cmsrel {ver}\n',
        f'fi\n',
    ])

def switch_to_cmssw(ver, arch):
    return ''.join([
        f'export SCRAM_ARCH={arch}\n',
        f'cd {tmp/ver/"src"}\n',
         'cmsenv\n',
    ])

script_dir = Path(__file__).parent.resolve()
init_cfg = ' '.join(str(script_dir/file) for file in pack)

with open(tmp/'init.sh', 'w') as f:
    f.write('#!/bin/bash\n\n')
    for ver, arch in init_cmssw:
        f.write(f'export SCRAM_ARCH={arch}\n')
        f.write(f'cmsrel {ver}\n')
        f.write(f'cp -r -t {ver}/src/ {init_cfg}\n')
    for ver, arch in init_cmssw:
        f.write(switch_to_cmssw(ver, arch))
        f.write(f'python3 init.py\n')
        f.write(f'scram b -j 4\n')

with open(tmp/'cfg.sh', 'w') as f1:
    with open(tmp/'run.sh', 'w') as f2:
        write('#!/bin/bash\n\n', f1, f2)
        current = None
        for driver, cfg, fileout, (ver, arch) in cfgs:
            if current != (ver, arch):
                current = (ver, arch)
                write(switch_to_cmssw(ver, arch), f1, f2)
            f1.write(f'{driver}\n')
            f2.write(f'cmsRun -e {cfg}\n')
            if fileout in output_file:
                ... # TODO
                # TODO customize init command
                # TODO directly write to EOS if output directory is specified