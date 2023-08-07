// -*- C++ -*-
#if !defined(eventHists_H)
#define eventHists_H

#include <iostream>
#include <TH1F.h>
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "HqqJpsi/nTupleAnalysis/interface/eventData.h"
#include "nTupleAnalysis/baseClasses/interface/fourVectorHists.h"
#include "nTupleAnalysis/baseClasses/interface/jetHists.h"
#include "nTupleAnalysis/baseClasses/interface/muonHists.h"
#include "nTupleAnalysis/baseClasses/interface/dimuonHists.h"
#include "HqqJpsi/nTupleAnalysis/interface/dimuonjetHists.h"
#include "nTupleAnalysis/baseClasses/interface/dijetHists.h"
#include "nTupleAnalysis/baseClasses/interface/elecHists.h"


using namespace HqqJpsi;

namespace HqqJpsi {

  class eventHists {
  public:

    TFileDirectory dir;
    bool debug;

    // Object Level
    nTupleAnalysis::jetHists*  allJets;
    nTupleAnalysis::jetHists*  selJets;
    nTupleAnalysis::jetHists*  tagJets;
    nTupleAnalysis::dijetHists* diJets;

    nTupleAnalysis::muonHists* allMuons;
    nTupleAnalysis::muonHists* preSelMuons;
    nTupleAnalysis::dimuonHists* preSelDiMuons;
    nTupleAnalysis::dimuonHists* selDiMuons;
    nTupleAnalysis::dimuonHists* selDiMuons3p5;

    nTupleAnalysis::fourVectorHists* v4j;
    
    nTupleAnalysis::elecHists* allElecs;

    dimuonjetHists* dimuonJetClose;
    dimuonjetHists* dimuonJetOther;

    eventHists(std::string, fwlite::TFileService&, bool isMC = false, bool blind = true, std::string histDetailLevel = "", bool _debug = false, eventData* event=NULL);
    void Fill(eventData*);
    //void Fill(eventData* event, std::vector<std::shared_ptr<eventView>> &views);
    ~eventHists(); 

  };

}
#endif // eventHists_H
