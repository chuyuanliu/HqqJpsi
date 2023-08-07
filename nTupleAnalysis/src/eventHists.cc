#include "HqqJpsi/nTupleAnalysis/interface/eventHists.h"
#include "nTupleAnalysis/baseClasses/interface/helpers.h"

using namespace HqqJpsi;

using std::cout; using std::endl;

eventHists::eventHists(std::string name, fwlite::TFileService& fs, bool isMC, bool blind, std::string histDetailLevel, bool _debug, eventData* event) {
  std::cout << "Initialize >> eventHists: " << name << " with detail level: " << histDetailLevel << std::endl;
  dir = fs.mkdir(name);
  debug = _debug;

  allJets = new nTupleAnalysis::jetHists(name+"/allJets", fs, "All Jets");
  selJets = new nTupleAnalysis::jetHists(name+"/selJets", fs, "Selected Jets");
  tagJets = new nTupleAnalysis::jetHists(name+"/tagJets", fs, "Tagged Jets");
  diJets  = new nTupleAnalysis::dijetHists(name+"/diJets", fs, " Di Jets");

  allMuons        = new nTupleAnalysis::muonHists(name+"/allMuons", fs, "All Muons");
  preSelMuons     = new nTupleAnalysis::muonHists(name+"/preSelMuons", fs, "PreSel Muons");
  preSelDiMuons   = new nTupleAnalysis::dimuonHists(name+"/preSelDiMuons", fs, "PreDiSel Muons");
  selDiMuons      = new nTupleAnalysis::dimuonHists(name+"/selDiMuons", fs, "SelDiSel Muons");

  allElecs        = new nTupleAnalysis::elecHists(name+"/allElecs", fs, "All Elecs");


  //
  //  Jet vs JPsi 
  //
  dimuonJetClose      = new dimuonjetHists(name+"/dimuonJetClose", fs, "di-muon + jet (close)");
  dimuonJetOther      = new dimuonjetHists(name+"/dimuonJetOther", fs, "di-muon + jet (other)");

  
  //
  //  4j hists
  //
  v4j = new nTupleAnalysis::fourVectorHists(name+"/v4j", fs, "4j");

} 

void eventHists::Fill(eventData* event){
  if(debug) cout << "eventHists::Fill " << endl;
  //
  // Object Level
  //

  //
  // Jets 
  //
  if(debug) cout << "eventHists::fillJets " << endl;
  allJets->nJets->Fill(event->allJets.size(), event->weight);
  for(auto &jet: event->allJets) allJets->Fill(jet, event->weight);

  selJets->nJets->Fill(event->selJets.size(), event->weight);
  for(auto &jet: event->selJets) selJets->Fill(jet, event->weight);

  unsigned int nTagJets = event->tagJets.size()   ;
  tagJets->nJets->Fill(nTagJets, event->weight);
  for(auto &jet: event->tagJets) tagJets->Fill(jet, event->weight);

  //
  //  Muons
  //
  if(debug) cout << "eventHists::fillMuons " << endl;
  allMuons->nMuons->Fill(event->allMuons.size(), event->weight);
  for(auto &muon: event->allMuons) allMuons->Fill(muon, event->weight);

  preSelMuons->nMuons->Fill(event->preSelMuons.size(), event->weight);
  for(auto &muon: event->preSelMuons) preSelMuons->Fill(muon, event->weight);

  unsigned int nPreSelDiMuons = event->preSelDiMuons.size();
  preSelDiMuons->nDiMuons->Fill(nPreSelDiMuons, event->weight);
  for(auto &dimuon: event->preSelDiMuons) preSelDiMuons->Fill(dimuon, event->weight);

  if(nPreSelDiMuons)
    selDiMuons->Fill(event->preSelDiMuons[0], event->weight);



  //
  //  Electrons
  //
  if(debug) cout << "eventHists::fillElectrons " << endl;
  allElecs->nElecs->Fill(event->allElecs.size(), event->weight);
  for(auto &elec: event->allElecs)             allElecs->Fill(elec, event->weight);

  //
  ///
  // 
//  To add 
//    delta R phi plots

  if(nPreSelDiMuons && nTagJets > 1){
    if(debug) cout << "eventHists::fillEvents " << endl;

    diJets->Fill(event->diJets, event->weight);

    const nTupleAnalysis::dimuonPtr& jPsi = event->preSelDiMuons[0]; 

    dimuonJetClose->Fill(event->dimuonJetClose, event->weight);
    dimuonJetOther->Fill(event->dimuonJetOther, event->weight);
    //dRJPsiJet_close->Fill(event->dimuonJetClose->pjet.DeltaR(jPsi->p), event->weight);
    //dRJPsiJet_other->Fill(event->dimuonJetOther->pjet.DeltaR(jPsi->p), event->weight);

  }

  if(nTagJets >= 4){
    TLorentzVector p4j = event->tagJets[0]->p + event->tagJets[1]->p + event->tagJets[2]->p + event->tagJets[3]->p;
    v4j->Fill(p4j, event->weight);
  }

  if(debug) cout << "eventHists::Fill left " << endl;
  return;
}

eventHists::~eventHists(){} 

