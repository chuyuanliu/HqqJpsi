#include "HqqJpsi/nTupleAnalysis/interface/dimuonjet.h"

using namespace HqqJpsi;

//dimuonjet object
//dimuonjet::dimuonjet(){}
dimuonjet::dimuonjet(std::shared_ptr<nTupleAnalysis::dimuon> &_dimuon, std::shared_ptr<nTupleAnalysis::jet> &_jet){


  dimuon = _dimuon;
  jet    = _jet;

  pmm = dimuon->p;
  pjet = jet->p;


  dR  = pmm.DeltaR(pjet);
  dPhi= pmm.DeltaPhi(pjet);
  st  = pmm.Pt() + pjet.Pt();
  p   = pmm + pjet;
  pt  = p.Pt();
  eta = p.Eta();
  phi = p.Phi();
  m   = p.M();
  e   = p.E();


}

dimuonjet::~dimuonjet(){}


