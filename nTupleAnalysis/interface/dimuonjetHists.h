// -*- C++ -*-
#if !defined(dimuonjetHists_H)
#define dimuonjetHists_H

#include <iostream>
#include <TH1F.h>
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "HqqJpsi/nTupleAnalysis/interface/dimuonjet.h"
#include "nTupleAnalysis/baseClasses/interface/jetHists.h"
#include "nTupleAnalysis/baseClasses/interface/fourVectorHists.h"

//using namespace nTupleAnalysis;

namespace HqqJpsi {

  class dimuonjetHists {
  public:
    TFileDirectory dir;
    
    nTupleAnalysis::fourVectorHists* v;
    TH1F* dR;
    TH1F* dPhi;
    TH1F* ptRatio;

    nTupleAnalysis::jetHists* jet;

    dimuonjetHists(std::string, fwlite::TFileService&, std::string title = "");
    void Fill(std::shared_ptr<dimuonjet>&, float);
    ~dimuonjetHists(); 

  };

}
#endif // dimuonjetHists_H
