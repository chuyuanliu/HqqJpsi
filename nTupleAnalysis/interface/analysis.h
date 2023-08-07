
// -*- C++ -*-
#if !defined(analysis_H)
#define analysis_H

#include <ctime>
#include <chrono>
#include <sys/resource.h>

#include <TFile.h>
#include <TChain.h>
#include <TTree.h>
#include <TSpline.h>
#include "DataFormats/FWLite/interface/InputSource.h" //for edm::LuminosityBlockRange
#include "nTupleAnalysis/baseClasses/interface/brilCSV.h"
#include "nTupleAnalysis/baseClasses/interface/initBranch.h"
#include "nTupleAnalysis/baseClasses/interface/jetData.h"
#include "nTupleAnalysis/baseClasses/interface/muonData.h"
#include "nTupleAnalysis/baseClasses/interface/elecData.h"
#include "nTupleAnalysis/baseClasses/interface/truthParticle.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "HqqJpsi/nTupleAnalysis/interface/eventData.h"
//#include "ZZ4b/nTupleAnalysis/interface/cutflowHists.h"
//#include "ZZ4b/nTupleAnalysis/interface/tagCutflowHists.h"
#include "HqqJpsi/nTupleAnalysis/interface/eventHists.h"
//#include "ZZ4b/nTupleAnalysis/interface/tagHists.h"
//#include "ZZ4b/nTupleAnalysis/interface/hemisphereMixTool.h"
//#include "ZZ4b/nTupleAnalysis/interface/triggerStudy.h"
//#include "ZZ4b/nTupleAnalysis/interface/lumiHists.h"
#include <fstream>


namespace HqqJpsi {

  class analysis {
  public:

    typedef std::pair<ULong64_t, UInt_t> EventLBData;
    typedef std::map<UInt_t, std::vector<EventLBData>> RunToEventLBMap;
    RunToEventLBMap passedEvents;

    unsigned int nTotalEvents = 0;
    unsigned int nPassEvents = 0;
    unsigned int nDupEvents = 0;
    bool autoPassNext = false;

    TChain* events;
    TChain* runs;
    TChain* lumiBlocks;
    Long64_t genEventCount;
    double_t genEventSumw;
    double_t genEventSumw2;
    Long64_t mcEventCount = 0;
    double_t mcEventSumw  = 0;
    double_t mcEventSumw2 = 0;
    
    bool debug = false;
    std::string year;
    bool isMC  = false;
    bool isDataMCMix  = false;
    bool mcUnitWeight  = false;
    bool blind = true;

    int treeEvents;
    eventData* event;
    //tagCutflowHists* cutflow;
    //lumiHists* lumiCounts    = NULL;
    float  lumiLastWrite    = 0;

    eventHists* allEvents   = NULL;
    eventHists* Dimuon0_Jpsi   = NULL;
    eventHists* Dimuon25_Jpsi   = NULL;
    eventHists* preSel     = NULL;
    eventHists* bTags     = NULL;

    //tagHists* passPreSel    = NULL;
    //tagHists* pass4Jets    = NULL;
    //tagHists* pass4AllJets    = NULL;
    ////tagHists* passDijetMass = NULL;
    //// tagHists* passMDRs      = NULL;
    //tagHists* passSvB       = NULL;
    //tagHists* passMjjOth    = NULL;
    //tagHists* failrWbW2     = NULL;
    //tagHists* passMuon      = NULL;
    //tagHists* passDvT05     = NULL;
    //tagHists* passTTCR      = NULL;
    //tagHists* passTTCRe     = NULL;
    //tagHists* passTTCRm     = NULL;
    //tagHists* passTTCRem    = NULL;
    //
    //triggerStudy* trigStudy  = NULL;
    //triggerStudy* trigStudyMjjOth  = NULL;


    long int nEvents = 0;
    double lumi      = 1;
    std::vector<edm::LuminosityBlockRange> lumiMask;
    edm::LuminosityBlockID prevLumiID;
    //UInt_t prevLumiBlock = 0;
    Int_t firstRun      = 1e9;
    Int_t lastRun       = 0;
    edm::RunNumber_t prevRun;
    //UInt_t nruns = 0;
    UInt_t nls   = 0;
    float  lumiID_intLumi = 0;
    float  intLumi = 0;
    bool   lumiID_passL1  = false;
    bool   lumiID_passHLT = false;
    float  intLumi_passL1  = 0;
    float  intLumi_passHLT = 0;
    double kFactor = 1;
    double xs = 1;

    bool writePicoAOD = false;
    bool fastSkim = false;
    bool looseSkim = false;

    TFile* picoAODFile;
    TTree* picoAODEvents;
    TTree* picoAODRuns;
    TTree* picoAODLumiBlocks;

    // debugging
    long int currentEvent = 0;

    //Monitoring Variables
    long int percent;
    std::chrono::time_point<std::chrono::system_clock> start;
    double timeTotal;
    double previousMonitorTime = 0;
    double timeElapsed = 0;
    long int previousMonitorEvent = 0;
    long int eventsElapsed;
    double eventRate = 0;
    double timeRemaining;
    int hours;
    int minutes;
    int seconds;
    int who = RUSAGE_SELF;
    struct rusage usage;
    long int usageMB;

    //
    //  Output Data for the new PicoAOD when using Hemisphere Mixing
    //   (Move these to event data ?
    UInt_t    m_run       =  0;
    UInt_t    m_lumiBlock =  0;
    ULong64_t m_event     =  0;
    Float_t   m_genWeight =  0;
    Float_t   m_bTagSF    =  0;
    Float_t   m_ttbarWeight =  0;
    
    nTupleAnalysis::jetData*  m_mixed_jetData = NULL;
    nTupleAnalysis::muonData*  m_mixed_muonData = NULL;
    nTupleAnalysis::elecData*  m_mixed_elecData = NULL;
    nTupleAnalysis::truthParticle*  m_mixed_truthParticle = NULL;

    Int_t     m_nPVs;
    Int_t     m_nPVsGood;    

    analysis(TChain* _events, TChain* _runs, TChain* _lumiBlocks, fwlite::TFileService& fs, bool _isMC, bool _blind, std::string _year,
	     std::string histDetailLevel, bool _debug, bool _fastSkim = false, 
	     std::string bjetSF = "", std::string btagVariations = "central",
	     std::string JECSyst = "", std::string friendFile = "");

    void createPicoAOD(std::string fileName, bool copyInputPicoAOD = true);

    bool alreadyFilled=false;
    void picoAODFillEvents();

    //
    // only used when overwritting the input picoAOD info (eg: in hemisphere mixing)
    //
    void createPicoAODBranches();

    // Write out all event and run numbers to histogram file
    bool writeOutEventNumbers = false;
    std::vector<UInt_t> passed_runs;
    std::vector<ULong64_t> passed_events;
    std::vector<UInt_t> passed_LBs;
    TFile* histFile = NULL;

    void addDerivedQuantitiesToPicoAOD();
    void storePicoAOD();
    void monitor(long int);
    int eventLoop(int maxEvents, long int firstEvent = 0);
    int processEvent();
    bool passLumiMask();
    std::map<edm::LuminosityBlockID, float> lumiData;
    void getLumiData(std::string);
    void countLumi();

    ~analysis();

  };

}
#endif // analysis_H

