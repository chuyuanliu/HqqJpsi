// -*- C++ -*-

#if !defined(dimuonjet_H)
#define dimuonjet_H
#include <iostream>
#include <TLorentzVector.h>
#include "nTupleAnalysis/baseClasses/interface/dimuon.h"
#include "nTupleAnalysis/baseClasses/interface/jetData.h"

namespace HqqJpsi {

  //dimuonjet object
  class dimuonjet {

  public:
    TLorentzVector pmm;
    TLorentzVector pjet;

    std::shared_ptr<nTupleAnalysis::dimuon> dimuon;
    std::shared_ptr<nTupleAnalysis::jet>    jet;

    TLorentzVector p;
    float dR;
    float dPhi;
    float st;
    float pt;
    float eta;
    float phi;
    float m;
    float e;

    //dimuonjet();
    dimuonjet(std::shared_ptr<nTupleAnalysis::dimuon>&, std::shared_ptr<nTupleAnalysis::jet>&); 
    ~dimuonjet(); 

    //void dump();
  };

  typedef std::shared_ptr<dimuonjet> dimuonjetPtr;

}
#endif // dimuonjet_H

