#include "HqqJpsi/nTupleAnalysis/interface/dimuonjetHists.h"

using namespace HqqJpsi;

dimuonjetHists::dimuonjetHists(std::string name, fwlite::TFileService& fs, std::string title) {

    dir = fs.mkdir(name);
    v = new nTupleAnalysis::fourVectorHists(name, dir, title);

    dR = dir.make<TH1F>("dR", (name+"/dR; "+title+" #DeltaR(j,j); Entries").c_str(), 50,0,5);
    dPhi = dir.make<TH1F>("dPhi", (name+"/dPhi; "+title+" #DeltaPhi(j,j); Entries").c_str(), 50,-3.2,3.2);  
    ptRatio = dir.make<TH1F>("ptRatio", (name+"/ptRatio; "+title+" pt(mu,mu)/pt(jet); Entries").c_str(), 50,-0.1,1.1);  

    jet = new nTupleAnalysis::jetHists(name+"/jet", fs, "Jet");
} 

void dimuonjetHists::Fill(std::shared_ptr<dimuonjet> &dimuonjet, float weight){

  v->Fill(dimuonjet->p, weight);

  dR->Fill(dimuonjet->dR, weight);
  dPhi->Fill(dimuonjet->dPhi, weight);

  float ptRatioVal = (dimuonjet->pmm.Pt() / (dimuonjet->pmm.Pt() + dimuonjet->pjet.Pt()));
  ptRatio->Fill(ptRatioVal, weight);

  jet->Fill(dimuonjet->jet, weight);

  return;
}

dimuonjetHists::~dimuonjetHists(){} 
