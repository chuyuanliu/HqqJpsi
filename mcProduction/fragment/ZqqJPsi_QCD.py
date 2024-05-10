import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8GeneratorFilter",
                        maxEventsToPrint = cms.untracked.int32(1),
                        pythiaPylistVerbosity = cms.untracked.int32(1),
                        filterEfficiency = cms.untracked.double(1.0),
                        pythiaHepMCVerbosity = cms.untracked.bool(False),
                        comEnergy = cms.double(13000.0),
                        PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            'HiggsSM:ffbar2H =true',
            '25:m0 = 91.187600000001', #don't know why, but the Higgs mass can't be the same of Z0
            '25:mWidth = 2.49520',
            '25:mMin = 10.00000',
            '25:mMax = 0.00000',
            '25:spinType = 3', #(2S+1)
            '25:onMode = off',
            '25:addChannel = 1 1.00 103 {quark} -{quark}',
            '443:onMode = off',
            '443:onIfMatch = 13 -13',
            ),
        parameterSets = cms.vstring('pythia8CommonSettings',
                                    'pythia8CP5Settings',
                                    'processParameters',
                                    )
        )
                        )

jpsi_from_quark_filter = cms.EDFilter('PythiaFilterMultiMother',
    ParticleID = cms.untracked.int32(443),
    MotherIDs = cms.untracked.vint32({quark}, -{quark}),
)

ProductionFilterSequence = cms.Sequence(generator*jpsi_from_quark_filter)