// -*- C++ -*-

#if !defined(HqqJpsi_eventData_H)
#define HqqJpsi_eventData_H

#include <iostream>
#include <boost/range/numeric.hpp>
#include <boost/range/adaptor/map.hpp>
#include <boost/any.hpp>
#include <TChain.h>
#include <TFile.h>
#include <TLorentzVector.h>
#include "nTupleAnalysis/baseClasses/interface/initBranch.h"
#include "nTupleAnalysis/baseClasses/interface/truthData.h"
#include "nTupleAnalysis/baseClasses/interface/jetData.h"
#include "nTupleAnalysis/baseClasses/interface/muonData.h"
#include "nTupleAnalysis/baseClasses/interface/elecData.h"
#include "nTupleAnalysis/baseClasses/interface/eventData.h"
#include "nTupleAnalysis/baseClasses/interface/dimuon.h"
#include "HqqJpsi/nTupleAnalysis/interface/dimuonjet.h"
#include "nTupleAnalysis/baseClasses/interface/dijet.h"
#include "nTupleAnalysis/baseClasses/interface/trigData.h"


// for jet pseudoTag calculations
#include <TRandom3.h>
#include <numeric> 
#include <boost/math/special_functions/binomial.hpp> 

namespace HqqJpsi {

  class eventData {

  public:

    // Member variables
    TChain* tree;
    bool isMC;
    float year;
    bool debug;
    bool printCurrentFile = true;
    bool fastSkim = false;
    
    nTupleAnalysis::eventData* eventDataTree = NULL;

    Float_t   bTagSF = 1;
    int       nTrueBJets = 0;
    float weight = 1.0;

    nTupleAnalysis::truthData* truth = NULL;

    //Predefine btag sorting functions
    float       bTag    = 0.6;
    std::string bTagger = "deepFlavB";

    //triggers
    std::map<std::string, bool> L1_triggers;
    std::map<std::string, bool> HLT_triggers;
    std::map<std::string, std::map<std::string, bool*>> HLT_L1_seeds;
    bool passL1              = false;
    bool passHLT             = false;

    std::map<std::string, bool*> L1_triggers_mon;

  public:

    float jetPtMin = 20;
    const float jetEtaMax= 2.4;
    const int puIdMin = 0b110;//7=tight, 6=medium, 4=loose working point
    const bool doJetCleaning=false;
     
    nTupleAnalysis::jetData* treeJets;
    std::vector<nTupleAnalysis::jetPtr> allJets;//all jets in nTuple
    std::vector<nTupleAnalysis::jetPtr> selJetsLoosePt;//jets passing loose pt/eta requirements
    std::vector<nTupleAnalysis::jetPtr> tagJetsLoosePt;//tagged jets passing loose pt/eta requirements
    std::vector<nTupleAnalysis::jetPtr> selJets;//jets passing pt/eta requirements
    std::vector<nTupleAnalysis::jetPtr> looseTagJets;//jets passing pt/eta and loose bTagging requirements
    std::vector<nTupleAnalysis::jetPtr> tagJets;//jets passing pt/eta and bTagging requirements
    std::vector<nTupleAnalysis::jetPtr> antiTag;//jets passing pt/eta and failing bTagging requirements
    std::vector<nTupleAnalysis::jetPtr> othJets;//other selected jets
    std::vector<nTupleAnalysis::trigPtr> allTrigJets;//all jets in nTuple
    std::vector<nTupleAnalysis::trigPtr> selTrigJets;//sel jets in nTuple
 

    nTupleAnalysis::muonData* treeMuons;
    std::vector<nTupleAnalysis::muonPtr> allMuons;
    std::vector<nTupleAnalysis::muonPtr> preSelMuons;
    std::vector<nTupleAnalysis::muonPtr> preSelMuons3p5;

    std::vector<nTupleAnalysis::dimuonPtr> preSelDiMuons;
    std::vector<nTupleAnalysis::dimuonPtr> preSelDiMuons3p5;
    std::shared_ptr<nTupleAnalysis::dijet> diJets;

    //nTupleAnalysis::jetPtr closeJetJPsi;
    //nTupleAnalysis::jetPtr otherJetJPsi;
    std::shared_ptr<dimuonjet> dimuonJetClose;
    std::shared_ptr<dimuonjet> dimuonJetOther;


    nTupleAnalysis::elecData* treeElecs;
    std::vector<nTupleAnalysis::elecPtr> allElecs;


    nTupleAnalysis::trigData* treeTrig = NULL;

    // Constructors and member functions
    eventData(TChain* t, bool mc, std::string y, bool d, bool _fastSkim = false, std::string bjetSF = "", std::string btagVariations = "central",
	      std::string JECSyst = "");
        
    void update(long int);
    void buildEvent();
    void buildDiMuons(std::vector<nTupleAnalysis::muonPtr>& thisMuons, std::vector<nTupleAnalysis::dimuonPtr>& thisDiMuons);
    void resetEvent();


    void dump();
    ~eventData(); 

    float ttbarSF(float pt);

    std::string currentFile = "";


  };

}
#endif // HqqJpsi_eventData_H
