#!/bin/bash

export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_6_30
cd CMSSW_10_6_30/src
cmsenv

git clone -b powhegUL https://github.com/cms-sw/genproductions
cp ../../make_rwl.py genproductions/bin/Powheg/ # reduce PDF variations
cd genproductions/bin/Powheg/

mkdir gg_H
cp production/2017/13TeV/Higgs/gg_H_quark-mass-effects_NNPDF31_13TeV/gg_H_quark-mass-effects_NNPDF31_13TeV_M125.input gg_H/

voms-proxy-init -voms cms -valid 192:00
python ./run_pwg_condor.py -p f -i gg_H/gg_H_quark-mass-effects_NNPDF31_13TeV_M125.input -m gg_H_quark-mass-effects -f fast -q longlunch -n 5000
condor_q