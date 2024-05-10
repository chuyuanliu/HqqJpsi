import FWCore.ParameterSet.Config as cms

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    # args = cms.vstring('/cvmfs/cms.cern.ch/phys_generator/gridpacks/UL/13TeV/powheg/V2/gg_H_quark-mass-effects_slc7_amd64_gcc820_CMSSW_10_6_20_ggH_M125/v1/gg_H_quark-mass-effects_slc7_amd64_gcc820_CMSSW_10_6_20_ggH_M125.tgz'),
    args = cms.vstring('{gridpack}/gg_H_quark-mass-effects_slc7_amd64_gcc700_CMSSW_10_6_30_fast.tgz'),
    nEvents = cms.untracked.uint32(5000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.Pythia8PowhegEmissionVetoSettings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

generator = cms.EDFilter("Pythia8HadronizerFilter",
                        maxEventsToPrint = cms.untracked.int32(1),
                        pythiaPylistVerbosity = cms.untracked.int32(1),
                        filterEfficiency = cms.untracked.double(1.0),
                        pythiaHepMCVerbosity = cms.untracked.bool(False),
                        comEnergy = cms.double(13000.0),
                        PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        pythia8PowhegEmissionVetoSettingsBlock,
        processParameters = cms.vstring(
            'POWHEG:nFinal = 1',    ## Number of final state particles
                                    ## (BEFORE THE DECAYS) in the LHE
                                    ## other than emitted extra parton
            '25:m0 = 125.0',
            '25:onMode = off',
            '25:addChannel = 1 1.00 103 {quark} -{quark} 443',
            '443:onMode = off',
            '443:onIfMatch = 13 -13',
        ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'pythia8PowhegEmissionVetoSettings',
                                    'pythia8PSweightsSettings',
                                    'processParameters'
                                    )
        )
                        )
ProductionFilterSequence = cms.Sequence(generator)